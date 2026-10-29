#!/usr/bin/env python3
"""녹조제거 쌍동선 STL(mm, Z-up, 면별 색상) → 웹용 경량 메시(src/assets/boat_mesh.json)
- 면 색상(VisCAM 15bit, 상위=B·중간=G·하위=R)별로 그룹화, 재질 역할 지정
- 좌표 0.1 mm 정수(int16)로 양자화 → base64
"""
import struct, json, base64, pathlib, numpy as np
R = pathlib.Path(__file__).resolve().parents[2]
b = (R/'data/ssangdong_ship.stl').read_bytes()
n = struct.unpack('<I', b[80:84])[0]
a = np.frombuffer(b[84:84+n*50], dtype=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]))
ROLE = {0x1084:'pontoon',0x294a:'hull',0x6318:'ufbbox',0x48e5:'logo',0x0c63:'black',0x77bd:'white',0x6aed:'solar',0x4210:'frame',0x56b5:'ctrl'}
groups=[]; buf=[]
for k in sorted(set(a['a'].tolist()), key=lambda k:-(a['a']==k).sum()):
    V = a['v'][a['a']==k].reshape(-1,3).astype(np.float64)
    q = np.round(V*10).astype(np.int16)          # 0.1 mm
    r,g,bb = (k&31),(k>>5)&31,(k>>10)&31
    groups.append({'role':ROLE.get(k,'misc'),'rgb':[round(r/31,3),round(g/31,3),round(bb/31,3)],'count':int(len(q))})
    buf.append(q.reshape(-1))
allq = np.concatenate(buf)
out = {'unit':'0.1mm','upAxis':'Z','forward':'+X','waterlineZ_mm':90,'bbox_mm':[a['v'].reshape(-1,3).min(0).round(1).tolist(),a['v'].reshape(-1,3).max(0).round(1).tolist()],
       'groups':groups,'data':base64.b64encode(allq.tobytes()).decode()}
(R/'src/assets/boat_mesh.json').write_text(json.dumps(out,separators=(',',':')))
print('tris',n,'groups',[(g['role'],g['count']//3) for g in groups],'json KB',(R/'src/assets/boat_mesh.json').stat().st_size//1024)
