import numpy as np, sys, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import compose as c
def eye_row(A,fc):
    """pupil row: both eye windows (left/right of face center) contain dark saturated pixels"""
    hsv=c.rgb2hsv(A[...,:3]/255); pup=(A[...,3]>128)&(hsv[...,2]<0.5)&(hsv[...,1]>0.45)
    fc=int(fc); L=pup[:,fc-105:fc-30].sum(1); R=pup[:,fc+30:fc+105].sum(1)
    sc=np.minimum(L,R).astype(float); sc[:260]=0; sc[470:]=0
    k=np.convolve(sc,np.ones(15),'same')
    th=0.5*k.max(); y=int(np.argmax(k>=th))
    while y+1<len(k) and k[y+1]>=k[y]: y+=1
    return y
