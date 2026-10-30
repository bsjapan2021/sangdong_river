#!/usr/bin/env python3
"""v2 패치: 경로 띠·금지구역·호안선을 은은하게 — 가산 블렌딩, 운항 중 자동 페이드, 지나간 구간은 사라짐"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
def patch(path):
    p = ROOT/path; t = p.read_text()
    def rep(a, b):
        nonlocal t
        assert t.count(a) == 1, (path, a[:70], t.count(a)); t = t.replace(a, b)
    rep("new THREE.MeshBasicMaterial({vertexColors:true,transparent:true,opacity:.85,depthWrite:false,side:THREE.DoubleSide})",
        "new THREE.MeshBasicMaterial({vertexColors:true,transparent:true,opacity:.7,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending})")
    rep("n=Math.min(pts.length-1,MS.plN),W=1.1;", "n=Math.min(pts.length-1,MS.plN),W=0.45;")
    rep("Cc[(k*6+v)*3]=.35*w;Cc[(k*6+v)*3+1]=.95*w;Cc[(k*6+v)*3+2]=1*w", "Cc[(k*6+v)*3]=.22*w;Cc[(k*6+v)*3+1]=.62*w;Cc[(k*6+v)*3+2]=.7*w")
    rep("Cc[k*3]=.22;Cc[k*3+1]=.3;Cc[k*3+2]=.32}", "Cc[k*3]=0;Cc[k*3+1]=0;Cc[k*3+2]=0}")   # 지나간 구간: 가산 블렌딩에서 검정 = 투명
    rep("  MS.su.uFade.value+=(0.1-MS.su.uFade.value)*Math.min(1,dt*.8);",
        "  {const k=Math.min(1,dt*.8);MS.su.uFade.value+=(0.06-MS.su.uFade.value)*k;MS.pl.material.opacity+=(0.32-MS.pl.material.opacity)*k;\n"
        "   MS.shore.material.opacity+=(0.3-MS.shore.material.opacity)*k;MS.nogo.forEach(o=>{o.material.opacity+=((o.userData.line?0.35:0.22)-o.material.opacity)*k})}   /* 운항 중엔 경로·호안선·금지구역을 은은하게 */")
    rep("function missionStart(){if(!MS.G)return;MS.G.visible=true;",
        "function missionStart(){if(!MS.G)return;MS.G.visible=true;MS.pl.material.opacity=.7;MS.shore.material.opacity=.95;MS.nogo.forEach(o=>o.material.opacity=o.userData.line?.9:.6);")
    p.write_text(t)
patch('src/template_v2.html'); patch('src/tools/boat.js'); print('path patched')
