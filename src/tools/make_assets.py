#!/usr/bin/env python3
"""현장 사진 -> DT 에셋
1) skyline_cut.png : 1.jpeg 상단 스카이라인(아파트·돔·산) 하늘 누끼 + 하단 페이드
2) photo_*.jpg     : 사진 비교 뷰용 리사이즈본
"""
import pathlib, numpy as np, cv2
from PIL import Image
R = pathlib.Path(__file__).resolve().parents[2]
A = R/'src/assets'; A.mkdir(parents=True, exist_ok=True)

def cut_sky(img, y0, y1):
    a = np.asarray(img.convert('RGB')).astype(np.float32)[y0:y1]
    H,W,_ = a.shape
    r,g,b = a[...,0],a[...,1],a[...,2]
    mx=a.max(-1); mn=a.min(-1); sat=(mx-mn)/np.maximum(mx,1)
    seed = ((b-r)>28)&(b>120)&(sat>0.18)
    # 확실한 하늘 픽셀로 2차 하늘색 모델 적합 (x,y 다항)
    yy,xx = np.nonzero(seed[:int(H*0.6)])
    X = np.stack([np.ones_like(xx),xx/W,yy/H,(xx/W)**2,(yy/H)**2,(xx/W)*(yy/H)],1).astype(np.float32)
    coef = np.linalg.lstsq(X, a[yy,xx], rcond=None)[0]
    gy,gx = np.mgrid[0:H,0:W]
    G = np.stack([np.ones_like(gx),gx/W,gy/H,(gx/W)**2,(gy/H)**2,(gx/W)*(gy/H)],-1).astype(np.float32)
    model = G@coef
    # 아래로 갈수록 하늘이 옅어지는 것을 외삽 오차 허용치로 보정
    d = np.sqrt(((a-model)**2).sum(-1))
    tol = 18 + 10*(gy/H)
    gray = a.mean(-1)
    mu = cv2.blur(gray,(5,5)); sd = np.sqrt(np.maximum(cv2.blur(gray*gray,(5,5))-mu*mu,0))
    pale = ((b-r)>7) & (gray>165) & (sd<5.5)
    skylike = (d<tol) | seed | pale
    # 열 단위 위→아래 스캔: 비하늘 3픽셀 연속 시 스카이라인
    m = np.zeros((H,W),np.uint8)
    for x in range(W):
        col = skylike[:,x]; run=0; edge=H
        for y in range(H):
            if col[y]: run=0
            else:
                run+=1
                if run>=3: edge=y-2; break
        m[:edge,x]=1
    alpha = (1-m).astype(np.float32)
    alpha = cv2.GaussianBlur(alpha,(3,3),0.8)
    h = H; fade = np.ones(h,np.float32)
    f0 = int(h*0.80); fade[f0:] = np.linspace(1,0,h-f0)
    alpha *= fade[:,None]
    haze = np.array([196,214,226],np.float32)
    rgb = a*0.82 + haze*0.18
    out = np.dstack([np.clip(rgb,0,255), alpha*255]).astype(np.uint8)
    return Image.fromarray(out,'RGBA')

src1 = Image.open(R/'photos'/'1.jpeg')
print('1.jpeg', src1.size)
sk = cut_sky(src1, 60, 330)
sk.save(A/'skyline_cut.png', optimize=True)
# 미리보기(체커 배경)
w,h = sk.size; chk = Image.new('RGB',(w,h),(255,0,255)); chk.paste(sk,(0,0),sk); chk.save(A/'_preview_skyline.jpg',quality=85)

for i,name in enumerate(['1.jpeg','2.jpeg','3.jpg','4.jpeg','5.jpg','6.jpg','7.jpg','8top.jpg'],1):
    im = Image.open(R/'photos'/name).convert('RGB'); W=960
    if im.width>W: im = im.resize((W, round(im.height*W/im.width)), Image.LANCZOS)
    im.save(A/f'photo_{i}.jpg', quality=76, optimize=True, progressive=True)
    print(name,'->',im.size, (A/f'photo_{i}.jpg').stat().st_size//1024,'KB')
print('skyline', sk.size, (A/'skyline_cut.png').stat().st_size//1024,'KB')
