#!/usr/bin/env python3
"""v2 패치: (1) 시네마틱 3컷 — CUT1 게이트 진입(진입 측 후방 저각) → CUT2 데크 밑(기둥 열 사이 수면 높이) → CUT3 빠져나오기(출구 측 정면), 하드컷+느린 돌리, 레터박스·컷 자막
 (2) 데크 밑 그늘 UVA 보강 — 데크 밑에서 UVA 365 nm 출력 60%→100%: 보라 글로우·기둥 조명, ROS 입자 3배, 녹조 제거 속도 1.8배, 텔레메트리 표시"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
CINE = r"""function cineCam(dt){const ig=MS.inGate;const lb=$('#cineLB');
  if(!ig||MS.cine===false){if(lb&&lb.classList.contains('on')){lb.classList.remove('on');document.body.classList.remove('cine')}MS.cut=0;return false}
  const g=ig.g,nx=g.B[0]-g.A[0],nz=g.B[1]-g.A[1],nl=Math.hypot(nx,nz)||1,ux=nx/nl,uz=nz/nl;   /* u: 데크 수직(통과 방향 축) */
  const fx=Math.cos(BOAT.hd),fz=Math.sin(BOAT.hd);const dir=Math.sign(fx*ux+fz*uz)||1;const tx=ux*dir,tz=uz*dir;   /* 진행 방향 */
  const dn=(BOAT.pos.x-g.G[0])*tx+(BOAT.pos.y-g.G[1])*tz;const ax=g.u[0],az=g.u[1];   /* a: 데크 길이 방향 */
  const cut=dn<-g.hw-0.3?1:dn<=g.hw+0.3?2:3;
  if(cut===1){_cp.set(g.G[0]-tx*(g.hw+8)+ax*3.2,1.3,g.G[1]-tz*(g.hw+8)+az*3.2);_ct.set(g.G[0]+tx*1.5,0.1,g.G[1]+tz*1.5)}          /* CUT1 진입: 보트 뒤·옆 저각, 데크와 기둥을 정면에 */
  else if(cut===2){_cp.set(g.G[0]+ax*6.5,0.12,g.G[1]+az*6.5);_ct.set(g.G[0]-ax*1,-0.25,g.G[1]-az*1)}                              /* CUT2 데크 밑: 기둥 열 사이 수면 높이에서 데크 아래를 따라 */
  else{_cp.set(g.G[0]+tx*(g.hw+7.5)-ax*2.5,0.9,g.G[1]+tz*(g.hw+7.5)-az*2.5);_ct.set(g.G[0]+tx*(g.hw*.5),-0.1,g.G[1]+tz*(g.hw*.5))}  /* CUT3 빠져나오기: 출구 측 정면 */
  if(cut!==MS.cut){MS.cut=cut;camera.position.copy(_cp);controls.target.copy(_ct);   /* 하드 컷 */
    if(lb){lb.classList.add('on');document.body.classList.add('cine');const c=$('#cineCap');c.textContent=T('cut'+cut);c.classList.remove('flash');void c.offsetWidth;c.classList.add('flash')}}
  else{const k=1-Math.exp(-dt*.6);camera.position.lerp(_cp,k);controls.target.lerp(_ct,1-Math.exp(-dt*4));camera.position.x+=Math.cos(U.time.value*.4)*.004;camera.position.y+=Math.sin(U.time.value*.5)*.002}   /* 느린 돌리 */
  return true}
"""
def patch(path, html):
    p = ROOT/path; t = p.read_text()
    def rep(a, b):
        nonlocal t
        assert t.count(a) == 1, (path, a[:70], t.count(a)); t = t.replace(a, b)
    a = t.index("function cineCam(dt){"); b = t.index("/* ---- 리모콘 수동 조종 ---- */")
    t = t[:a] + CINE + t[b:]
    # UVA glow parts on the boat
    rep("  grp.position.set(BOAT.pos.x,-0.5,BOAT.pos.y);grp.visible=false;scene.add(grp);",
        "  {const tx=canvasTex(128,128,(x,w,h)=>{const g=x.createRadialGradient(w/2,h/2,0,w/2,h/2,w/2);g.addColorStop(0,'rgba(200,150,255,1)');g.addColorStop(.35,'rgba(150,90,255,.55)');g.addColorStop(1,'rgba(120,60,255,0)');x.fillStyle=g;x.fillRect(0,0,w,h)});\n"
        "   const gl=new THREE.Mesh(new THREE.CircleGeometry(3.4,40),new THREE.MeshBasicMaterial({map:tx,transparent:true,opacity:0,depthWrite:false,blending:THREE.AdditiveBlending}));gl.rotation.x=-Math.PI/2;gl.position.y=.04;grp.add(gl);BOAT.uvGlow=gl;\n"
        "   const lt=new THREE.PointLight(0x9a6bff,0,9,1.6);lt.position.set(.6,.15,0);grp.add(lt);BOAT.uvLight=lt}   /* UVA 365 nm 램프(그늘 보강 시 강해짐) */\n"
        "  grp.position.set(BOAT.pos.x,-0.5,BOAT.pos.y);grp.visible=false;scene.add(grp);")
    rep("  const em=run?Math.sqrt(sp):0;",
        "  const em=run?Math.sqrt(sp):0;\n"
        "  const shade=run&&!!bandInfo([BOAT.pos.x,BOAT.pos.y],0.6);MS.uva=(MS.uva||.6)+((run?(shade?1:.6):0)-(MS.uva||.6))*Math.min(1,dt*6);   /* 데크 밑 그늘 → UVA 100% */\n"
        "  const boost=clamp((MS.uva-.6)/.4,0,1);if(BOAT.uvGlow){BOAT.uvGlow.material.opacity=boost*(.8+.2*Math.sin(BOAT.t*9));BOAT.uvLight.intensity=boost*4*(.85+.15*Math.sin(BOAT.t*7))}")
    rep("  for(let k=0;k<Math.round(3*em);k++){const a=Math.random()*6.283,r0=R(.5,7);bSpawn(bx+Math.cos(a)*r0,R(-2.4,-0.6),bz+Math.sin(a)*r0,R(-.2,.2),R(-.05,.1),R(-.2,.2),R(.6,1.6),R(.12,.26),Math.random()<.55?3:4)}",
        "  for(let k=0;k<Math.round(3*em*(1+2*boost));k++){const a=Math.random()*6.283,r0=R(.5,7-2*boost);bSpawn(bx+Math.cos(a)*r0,R(-2.4,-0.6),bz+Math.sin(a)*r0,R(-.2,.2),R(-.05,.1),R(-.2,.2),R(.6,1.6),R(.12,.26)*(1+.3*boost),Math.random()<(.55-.25*boost)?3:4)}   /* 그늘 보강 시 ROS 3배·보라(O₂⁻) 비중↑ */")
    rep("const al=Math.min(1,sdt*.5);", "const al=Math.min(1,sdt*.5*(1+.8*boost));")
    rep("if(e2)e2.textContent=T('lidarLn',{n:nh,d:near<99?near.toFixed(1)+' m':'—'})",
        "if(e2)e2.textContent=T('lidarLn',{n:nh,d:near<99?near.toFixed(1)+' m':'—'});const e3=$('#bUva');if(e3){const pc=Math.round((MS.uva||0)*100);e3.textContent=T(pc>=90?'uvaBoost':'uvaLn',{p:pc});e3.parentNode.classList.toggle('boost',pc>=90)}")
    rep("MS.inGate?T('msGate',{c:MS.inGate.g.clr.toFixed(2),k:Math.min(3,MS.inGate.g.passes+1)}):",
        "MS.inGate?T('msGate',{c:MS.inGate.g.clr.toFixed(2),k:Math.min(3,MS.inGate.g.passes+1),p:Math.round((MS.uva||.6)*100)}):")
    if html:
        rep('<div><i style="color:#7dff9e">●</i> <span id="bLidar">LiDAR</span></div>',
            '<div><i style="color:#7dff9e">●</i> <span id="bLidar">LiDAR</span></div><div class="uvl"><i style="color:#b48cff">●</i> <span id="bUva">UVA</span></div>')
        rep('<div id="credit"', '<div id="cineLB" aria-hidden="true"><i class="t"></i><i class="b"></i><span id="cineCap"></span></div>\n<div id="credit"')
        rep("#boatBar{background:",
            "#cineLB{position:fixed;inset:0;pointer-events:none;z-index:4}#cineLB i{position:absolute;left:0;right:0;height:0;background:#000;transition:height .6s ease}#cineLB .t{top:0}#cineLB .b{bottom:0}\n"
            "#cineLB.on i{height:9vh}#cineCap{position:absolute;left:24px;bottom:calc(9vh + 12px);font:600 12px var(--mono);letter-spacing:.18em;color:#fff;opacity:0;text-shadow:0 1px 6px #000}\n"
            "#cineLB:not(.on) #cineCap{display:none}#cineCap.flash{animation:capIn 2.6s ease forwards}@keyframes capIn{0%{opacity:0;transform:translateY(6px)}15%,70%{opacity:.95;transform:none}100%{opacity:.35}}\n"
            "#purHud .tele .uvl.boost{color:#d9c2ff;font-weight:700}\n#boatBar{background:")
        rep(" msGate:{ko:'🌉 게이트 서행 통과(50%) · 마스트 여유고 {c} m · 기둥 주변 녹조 세정 {k}/3회',en:'🌉 Slow gate pass (50%) · mast clearance {c} m · pile-area cleaning pass {k}/3',ja:'🌉 ゲート徐行通過（50%）・マスト余裕高 {c} m・橋脚周辺のアオコ洗浄 {k}/3回'},",
            " msGate:{ko:'🌉 게이트 서행 통과(50%) · 마스트 여유고 {c} m · 기둥 주변 세정 {k}/3회 · UVA {p}%',en:'🌉 Slow gate pass (50%) · mast clearance {c} m · pile cleaning {k}/3 · UVA {p}%',ja:'🌉 ゲート徐行通過（50%）・マスト余裕高 {c} m・橋脚周辺洗浄 {k}/3回・UVA {p}%'},\n"
            " cut1:{ko:'CUT 1 · 게이트 진입',en:'CUT 1 · Gate approach',ja:'CUT 1・ゲート進入'},cut2:{ko:'CUT 2 · 데크 밑 통과 · UVA 보강',en:'CUT 2 · Under the deck · UVA boost',ja:'CUT 2・デッキ下通過・UVA増強'},cut3:{ko:'CUT 3 · 빠져나오기',en:'CUT 3 · Exit',ja:'CUT 3・抜け出し'},\n"
            " uvaLn:{ko:'UVA 365 nm 광촉매 · 출력 {p}%',en:'UVA 365 nm photocatalyst · output {p}%',ja:'UVA 365 nm 光触媒・出力 {p}%'},\n"
            " uvaBoost:{ko:'UVA 365 nm · 출력 {p}% ▲ 데크 밑 그늘 보강 (녹조 우세 구역)',en:'UVA 365 nm · output {p}% ▲ shade boost under the deck (algae-prone)',ja:'UVA 365 nm・出力 {p}% ▲ デッキ下の日陰で増強（アオコ多発域）'},")
    p.write_text(t)
patch('src/template_v2.html', True); patch('src/tools/boat.js', False); print('cine patched')
