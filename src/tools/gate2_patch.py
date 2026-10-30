#!/usr/bin/env python3
"""v2 패치: 게이트(기둥 사이) 고도화
 (1) 서행 통과 — 게이트 반경(데크폭/2+3.5 m) 안에서는 속도 50% (자율·리모콘 공통)
 (2) 시네마틱 카메라 — 게이트 통과 순간 데크 옆 수면 높이에서 기둥 열을 따라 비춤(🎬 토글)
 (3) 높이 검사 — 데크 하면(상판 0.85 m − 두께 0.12 m)과 보트 최고점(STL 마스트, 수면+0.94 m) 여유고 계산, 0.15 m 미만 게이트는 사용 금지(빨간 표식)
 (4) 기둥 주변 세정 — 모든 게이트를 커버리지 경로에 포함, 게이트마다 3회 왕복 통과(A→B→A→B)"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
def patch(path, html):
    p = ROOT/path; t = p.read_text()
    def rep(a, b):
        nonlocal t
        assert t.count(a) == 1, (path, a[:70], t.count(a)); t = t.replace(a, b)
    # height check at gate creation
    rep("    const gate={A,G,B:Bp};MS.gates.push(gate);",
        "    const boatTop=-0.5+((BOATMESH.bbox_mm[1][2]-(BOATMESH.waterlineZ_mm||90))/1000),deckBot=(B.y||0.85)-0.12,clr=deckBot-boatTop;   /* 마스트 높이 검사 */\n"
        "    if(clr<0.15){MS.lowGates.push({G,clr});return}\n"
        "    const gate={A,G,B:Bp,hw:B.hw,clr,u:[B.ux,B.uz],passes:0,side:0};MS.gates.push(gate);")
    rep("MS.gates=[];MS.gateMap=new Map();", "MS.gates=[];MS.lowGates=[];MS.gateMap=new Map();")
    rep("const gaps=[];for(let s=0;s+4<=L+1e-6;s+=4)gaps.push(s+2);BANDS.push({a,b,L,ux:(b[0]-a[0])/L,uz:(b[1]-a[1])/L,hw,gaps})",
        "const gaps=[];for(let s=0;s+4<=L+1e-6;s+=4)gaps.push(s+2);BANDS.push({a,b,L,ux:(b[0]-a[0])/L,uz:(b[1]-a[1])/L,hw,gaps,y:d.y||0.85})")
    rep("  (MS.gates||[]).forEach(gt=>{const m=new THREE.Mesh(new THREE.RingGeometry(.45,.65,24),msMat(0x7ff0b0,.85));",
        "  (MS.lowGates||[]).forEach(gt=>{const m=new THREE.Mesh(new THREE.RingGeometry(.45,.65,24),msMat(0xff4d5e,.9));m.rotation.x=-Math.PI/2;m.position.set(gt.G[0],-0.34,gt.G[1]);m.userData.z=gt.G[1];G.add(m);MS.nogo.push(m)});\n"
        "  (MS.gates||[]).forEach(gt=>{const m=new THREE.Mesh(new THREE.RingGeometry(.45,.65,24),msMat(0x7ff0b0,.85));")
    # coverage: include every gate as a 3-pass segment
    rep("  let cur=[BOAT.pos.x,BOAT.pos.y];const pts=[];const used=new Uint8Array(segs.length);",
        "  (MS.gates||[]).forEach(gt=>{const s=[gt.A,gt.B];s.gate=gt;segs.push(s)});   /* 기둥 주변 세정: 모든 게이트 포함 */\n"
        "  let cur=[BOAT.pos.x,BOAT.pos.y];const pts=[];const used=new Uint8Array(segs.length);")
    rep("used[bi]=1;const s=segs[bi],a=s[be],b=s[1-be];const con=boatPath(cur,a)?[cur,a]:astar(cur,a);if(!routeOK(con))continue;densify(con,pts);densify([a,b],pts);cur=b}",
        "used[bi]=1;const s=segs[bi],a=s[be],b=s[1-be];const con=boatPath(cur,a)?[cur,a]:astar(cur,a);if(!routeOK(con))continue;densify(con,pts);\n"
        "    if(s.gate){const Gp=s.gate.G;densify([a,Gp,b,Gp,a,Gp,b],pts)}else densify([a,b],pts);cur=b}   /* 게이트는 3회 왕복 통과 */")
    # slow pass + pass counting (autonomous)
    rep("  const des=Math.atan2(tg[1]-pos[1],tg[0]-pos[0]);let dh=des-BOAT.hd;dh=Math.atan2(Math.sin(dh),Math.cos(dh));BOAT.hd+=clamp(dh,-.6*sdt,.6*sdt);",
        "  if(gateWatch(pos))slow*=.5;   /* 게이트 서행 통과 */\n"
        "  const des=Math.atan2(tg[1]-pos[1],tg[0]-pos[0]);let dh=des-BOAT.hd;dh=Math.atan2(Math.sin(dh),Math.cos(dh));BOAT.hd+=clamp(dh,-.6*sdt,.6*sdt);")
    rep("  M.tm+=dt;if(M.tm>.25)", "  if(gateWatch(pos))BOAT.v=clamp(BOAT.v,-.3,BOAT.base*.5);   /* 리모콘도 게이트 서행 */\n  M.tm+=dt;if(M.tm>.25)")
    rep("/* ---- 리모콘 수동 조종 ---- */",
        "/* ---- 게이트 서행·통과 횟수·시네마틱 ---- */\n"
        "function gateWatch(pos){let best=null,bd=1e9;for(const g of MS.gates||[]){const d=Math.hypot(g.G[0]-pos[0],g.G[1]-pos[1]);if(d<bd){bd=d;best=g}}\n"
        "  if(!best||bd>best.hw+3.5){if(MS.inGate)MS.inGate.g.side=0;MS.inGate=null;return false}\n"
        "  const nx=best.B[0]-best.A[0],nz=best.B[1]-best.A[1],sd=Math.sign((pos[0]-best.G[0])*nx+(pos[1]-best.G[1])*nz)||1;\n"
        "  if(best.side&&sd!==best.side)best.passes++;best.side=sd;MS.inGate={g:best,d:bd};return true}\n"
        "const _cp=new THREE.Vector3(),_ct=new THREE.Vector3();\n"
        "function cineCam(dt){const ig=MS.inGate;if(!ig||MS.cine===false)return false;const g=ig.g;const n=[g.B[0]-g.A[0],g.B[1]-g.A[1]],nl=Math.hypot(n[0],n[1])||1;\n"
        "  const side=g.side||1;/* 데크 옆 수면 높이: 기둥 열을 따라 7 m 떨어진 곳, 보트가 나오는 쪽으로 살짝 */\n"
        "  _cp.set(g.G[0]+g.u[0]*7.5+n[0]/nl*(g.hw+1.2)*side,0.25,g.G[1]+g.u[1]*7.5+n[1]/nl*(g.hw+1.2)*side);_ct.set(g.G[0],-0.25,g.G[1]);\n"
        "  const k=1-Math.exp(-dt*3);camera.position.lerp(_cp,k);controls.target.lerp(_ct,k);return true}\n"
        "/* ---- 리모콘 수동 조종 ---- */")
    rep("  if(BOAT.follow&&!fly&&MS.ph===3){const k=1-Math.exp(-dt*2.2);",
        "  if(BOAT.follow&&!fly&&MS.ph===3&&cineCam(dt)){}else if(BOAT.follow&&!fly&&MS.ph===3){const k=1-Math.exp(-dt*2.2);")
    rep("textContent=MS.man?rcMsg():(MS.rcBackT&&performance.now()-MS.rcBackT<4000)?T('msRcBack'):MS.rec?T('msRecover'):",
        "textContent=MS.man?rcMsg():(MS.rcBackT&&performance.now()-MS.rcBackT<4000)?T('msRcBack'):MS.rec?T('msRecover'):MS.inGate?T('msGate',{c:MS.inGate.g.clr.toFixed(2),k:Math.min(3,MS.inGate.g.passes+1)}):")
    rep("function missionStart(){if(!MS.G)return;MS.man=null;", "function missionStart(){if(!MS.G)return;MS.man=null;MS.inGate=null;(MS.gates||[]).forEach(g=>{g.passes=0;g.side=0});")
    if html:
        rep("DECK_WOOD=decks.filter(d=>!d.road).map(d=>({pts:d.pts,w:d.w}));", "DECK_WOOD=decks.filter(d=>!d.road).map(d=>({pts:d.pts,w:d.w,y:0.85}));")
        rep('<button id="bFollow" aria-pressed="true" data-i18n="boatFollow">보트 추적</button>',
            '<button id="bCine" aria-pressed="true" data-i18n-title="boatCineT" title="게이트 통과 시네마틱 카메라">🎬</button><button id="bFollow" aria-pressed="true" data-i18n="boatFollow">보트 추적</button>')
        rep("$('#bRestart').addEventListener('click',()=>{boatReset();missionStart()});",
            "$('#bRestart').addEventListener('click',()=>{boatReset();missionStart()});\n$('#bCine').addEventListener('click',()=>{MS.cine=MS.cine===false;$('#bCine').setAttribute('aria-pressed',String(MS.cine!==false))});")
        rep("#purHud .brow #bFollow{margin-left:auto;", "#purHud .brow #bCine{margin-left:auto;font-family:var(--ui)}#purHud .brow #bFollow{")
        rep(" hudFold:{", " msGate:{ko:'🌉 게이트 서행 통과(50%) · 마스트 여유고 {c} m · 기둥 주변 녹조 세정 {k}/3회',en:'🌉 Slow gate pass (50%) · mast clearance {c} m · pile-area cleaning pass {k}/3',ja:'🌉 ゲート徐行通過（50%）・マスト余裕高 {c} m・橋脚周辺のアオコ洗浄 {k}/3回'},\n"
            " boatCineT:{ko:'게이트 통과 시네마틱 카메라 켜기/끄기',en:'Toggle cinematic gate camera',ja:'ゲート通過シネマカメラ切替'},\n hudFold:{")
    p.write_text(t)
patch('src/template_v2.html', True); patch('src/tools/boat.js', False); print('gate2 patched')
