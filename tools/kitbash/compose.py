from PIL import Image; import numpy as np, json, os, sys
# run from Content/art (sprites are read as char_<name>.webp from cwd); scan.json lives next to this file
S=os.environ.get('S', os.path.dirname(os.path.abspath(__file__)))
scan=json.load(open(S+'/scan.json')) if os.path.exists(S+'/scan.json') else {}
def load(n): return np.array(Image.open(f'char_{n}.webp').convert('RGBA')).astype(np.float32)
def dil(r,k):
    for _ in range(k):
        g=r.copy(); g[1:]|=r[:-1]; g[:-1]|=r[1:]; g[:,1:]|=r[:,:-1]; g[:,:-1]|=r[:,1:]; r=g
    return r
def flood(m,seed):
    r=np.zeros_like(m); r[seed]=True; r&=m
    if not r.any(): return r
    while True:
        g=dil(r,1)&m
        if (g==r).all(): return r
        r=g
def compose(headn, bodyn, hue=None, keep=6):
    H,B=load(headn),load(bodyn); sh,sb=scan[f'char_{headn}.webp'],scan[f'char_{bodyn}.webp']
    out=B.copy(); yb=sb['neck']
    neckcols=np.zeros(B.shape[1],bool); l=int(sb['cx']-sb['neckw']/2); neckcols[l:l+sb['neckw']]=True
    strip=out[yb-keep:yb].copy(); strip[:,~neckcols]=0
    out[:yb]=0; out[yb-keep:yb]=strip
    if hue is not None: out=recolor(out,hue)
    ya=max(sh['neck'],yb); cx=int(sh['cx'])
    lim=H[...,3]>20; lim[ya+1:]=False
    hm=flood(lim,(300,cx)) if lim[300,cx] else flood(lim,(ya,cx))
    # drop donor clothing (saturated non-skin colours) near the bottom of the head, plus the outline hugging it
    hsv=rgb2hsv(H[...,:3]/255); hu=hsv[...,0]
    cloth=(hsv[...,1]>0.55)&(hsv[...,2]>0.45)&((hu<0.02)|(hu>0.12))
    band=np.zeros_like(cloth); band[sh['neck']-60:]=True; cloth&=band&hm
    if cloth.any():
        hm&=~(dil(cloth,2)&~(hsv[...,2]<0.38))
        hm=flood(hm,(300,cx)) if hm[300,cx] else hm
    head=H.copy(); head[~hm]=0
    dx=int(round(sb['face']-sh['face']))
    head=np.roll(head,dx,axis=1)
    a=head[...,3:4]/255; out[...,:3]=head[...,:3]*a+out[...,:3]*(1-a); out[...,3:4]=np.maximum(out[...,3:4],head[...,3:4])
    return Image.fromarray(out.clip(0,255).astype(np.uint8))
def rgb2hsv(rgb):
    r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]; mx=rgb.max(-1); mn=rgb.min(-1); d=mx-mn+1e-9
    h=np.where(mx==r,((g-b)/d)%6,np.where(mx==g,(b-r)/d+2,(r-g)/d+4))/6
    h=np.where(mx-mn<1e-6,0,h); s=np.where(mx>0,(mx-mn)/(mx+1e-9),0)
    return np.stack([h,s,mx],-1)
def hsv2rgb(hsv):
    h,s,v=hsv[...,0]*6,hsv[...,1],hsv[...,2]; i=np.floor(h)%6; f=h-np.floor(h)
    p=v*(1-s); q=v*(1-s*f); t=v*(1-s*(1-f))
    r=np.choose(i.astype(int),[v,q,p,p,t,v]); g=np.choose(i.astype(int),[t,v,v,q,p,p]); b=np.choose(i.astype(int),[p,p,t,v,v,q])
    return np.stack([r,g,b],-1)
def recolor(img,shift):
    rgb=img[...,:3]/255; mx=rgb.max(-1); mn=rgb.min(-1); sat=(mx-mn)/(mx+1e-6)
    hsv=rgb2hsv(rgb)
    # skip skin: hue 0.02-0.12 low-mid sat high value; skip dark outline
    skin=(hsv[...,0]>0.02)&(hsv[...,0]<0.12)&(hsv[...,1]<0.55)&(hsv[...,2]>0.6)
    mask=(hsv[...,1]>0.35)&(hsv[...,2]>0.45)&~skin
    if not isinstance(shift,(list,tuple)):
        hh=hsv[...,0][mask&(img[...,3]>128)]
        if len(hh): shift=(float(np.argmax(np.histogram(hh,bins=36,range=(0,1))[0]))/36+1/72, shift)
    if isinstance(shift,(list,tuple)):
        src,shift=shift; dh=np.abs(((hsv[...,0]-src+0.5)%1)-0.5); mask&=dh<0.05
    hsv[...,0]=np.where(mask,(hsv[...,0]+shift)%1,hsv[...,0])
    img=img.copy(); img[...,:3]=hsv2rgb(hsv)*255; return img
if __name__=='__main__':
    pairs=json.loads(sys.argv[1]); tiles=[]
    for p in pairs:
        im=compose(p[0],p[1],p[2] if len(p)>2 else None)
        tiles+= [Image.open(f'char_{p[0]}.webp').convert('RGBA'),Image.open(f'char_{p[1]}.webp').convert('RGBA'),im]
    W=256;Ht=384; cols=3; rows=len(pairs)
    sheet=Image.new('RGBA',(W*cols,Ht*rows),(225,220,210,255))
    for i,t in enumerate(tiles): sheet.alpha_composite(t.resize((W,Ht)),((i%cols)*W,(i//cols)*Ht))
    sheet.save(sys.argv[2])
