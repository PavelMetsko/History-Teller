import sys,os,json,glob; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); import compose as c, eyes, numpy as np
from PIL import Image
res={}
for f in sorted(glob.glob('char_*.webp')):
    A=np.array(Image.open(f).convert('RGBA')).astype(np.float32)
    if A.shape!=(768,512,4): continue
    al=A[...,3]>128; w=al.sum(1); headw=w[200:430].max()
    if headw==0: continue
    hsv=c.rgb2hsv(A[...,:3]/255)
    skin=(hsv[...,0]>0.02)&(hsv[...,0]<0.10)&(hsv[...,1]>0.12)&(hsv[...,1]<0.5)&(hsv[...,2]>0.78)&al
    best=None
    for y in range(400,560):
        xs=np.where(al[y])[0]
        if not len(xs): continue
        cx=int((xs.min()+xs.max())/2)
        if skin[y,cx-20:cx+20].mean()>0.85 and w[y]<0.75*headw: best=(y,cx)
    if best:
        y,cx=best
        # neck = contiguous skin run around cx on row y
        l=cx; r=cx
        while l>0 and skin[y,l-1]: l-=1
        while r<511 and skin[y,r+1]: r+=1
        fc=[(np.where(al[yy])[0].min()+np.where(al[yy])[0].max())/2 for yy in range(260,400) if al[yy].any()]
        res[f]=dict(eye=eyes.eye_row(A,float(np.median(fc))),face=float(np.median(fc)),neck=y,cx=(l+r)/2,neckw=r-l+1,headw=int(headw))
json.dump(res,open(HERE+'/scan.json','w'))
base=[k for k in res if '_' not in k[5:-5]]
print(len(res),'of 864; base sprites:',len(base))
