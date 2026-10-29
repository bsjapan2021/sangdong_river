#!/usr/bin/env python3
"""v2 패치: 녹조제거 쌍동선(STL) 자율운항 + 나노버블·ROS 분사 + 녹조 제거 마스크 + '보트 운행' 모드(3개 국어)"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
BOATJS = (ROOT/'src/tools/boat.js').read_text()

def patch(path, is_template):
    p = pathlib.Path(path); t = p.read_text()
    def rep(a, b, n=1):
        nonlocal t
        assert t.count(a) == n, (path, a[:80], t.count(a)); t = t.replace(a, b)
    # --- shared uniforms / GLSL helpers
    rep("uUnder:{value:0},uSun:skyU.uSun};",
        "uUnder:{value:0},uSun:skyU.uSun,uMask:{value:(()=>{const x=new THREE.DataTexture(new Uint8Array([0,0,0,255]),1,1);x.needsUpdate=true;return x})()},uMaskOn:{value:0},uBox:{value:new THREE.Vector4(0,0,1,1)},uBoat:{value:new THREE.Vector3(0,0,0)}};")
    rep("uniform sampler2D uAtlas;uniform vec3 uSun;`;", "uniform sampler2D uAtlas;uniform vec3 uSun;uniform sampler2D uMask;uniform float uMaskOn;uniform vec4 uBox;uniform vec3 uBoat;`;")
    rep("w*=.5;}return a;}`;", "w*=.5;}return a;}\n    float mk(vec2 p){vec2 uv=(p-uBox.xy)*uBox.zw;return uMaskOn*texture2D(uMask,uv).r;}float bN(vec2 p){return uMaskOn*exp(-distance(p,uBoat.xy)/6.);}`;")
    # --- surface film: cleaned wake from the mask, foam ring + ROS sparkle around the boat
    rep("float inner=(1.-dirty)*smoothstep(uR,uR-30.,d)*(1.-uRegrow);",
        "float inner=(1.-dirty)*smoothstep(uR,uR-30.,d)*(1.-uRegrow);float m_=mk(p);dirty=min(dirty,1.-m_);inner=max(inner,m_*.7);"
        "float bw=uMaskOn*exp(-pow((distance(p,uBoat.xy)-4.5)/1.6,2.))*(.5+.5*fb(p*.8+t*.6));foam=max(foam,bw*.7);")
    rep("float rs=pow(vn(p*5.+t*6.),14.)*rosb*2.2;", "float rs=pow(vn(p*5.+t*6.),14.)*max(rosb,bN(p)+m_*.15)*2.2;")
    # --- outlet jets are not shown in boat mode
    rep("const pts=new THREE.Points(g,m);pts.position.set(nz.p[0],-0.42,nz.p[1]);", "const pts=new THREE.Points(g,m);pts.userData.jet=1;pts.position.set(nz.p[0],-0.42,nz.p[1]);")
    rep("boil.rotation.x=-Math.PI/2;", "boil.userData.jet=1;boil.rotation.x=-Math.PI/2;")
    rep("const pts=new THREE.Points(g,m);pts.position.set(nz.p[0],-1.95,nz.p[1]);", "const pts=new THREE.Points(g,m);pts.userData.jet=1;pts.position.set(nz.p[0],-1.95,nz.p[1]);")
    # --- haze / microbes / ROS / ceiling / bed follow the mask
    rep("float in_=1.-smoothstep(uR-4.,uR+2.,d);", "float in_=1.-smoothstep(uR-4.,uR+2.,d);in_=max(in_,mk(p.xz)*.8);")
    rep("float alive=max(smoothstep(uR-5.,uR+1.,d),uRegrow);", "float alive=max(smoothstep(uR-5.,uR+1.,d),uRegrow);float mm=mk(p.xz);alive*=1.-mm;")
    rep("vF=exp(-pow((d-uR+2.)/2.5,2.))*(1.-uRegrow);", "vF=exp(-pow((d-uR+2.)/2.5,2.))*(1.-uRegrow)*step(.5,uR);vF=max(vF,uMaskOn*exp(-pow((distance(p.xz,uBoat.xy)-6.5)/2.,2.))*(1.-mm*.6));")
    rep("float w=max(band,near)*(1.-uRegrow*.8);", "float w=max(band,near*(1.-uMaskOn))*(1.-uRegrow*.8);w=max(w,max(min(1.,bN(p.xz)*1.6),mk(p.xz)*.12));")
    rep("float d=dRet(p);float dirty=max(smoothstep(uR-10.,uR+3.,d),uRegrow);", "float d=dRet(p);float dirty=max(smoothstep(uR-10.,uR+3.,d),uRegrow);dirty=min(dirty,1.-mk(p));", 2)
    # --- boat module
    rep("function updatePurify(dt){", BOATJS + "\nfunction updatePurify(dt){")
    if is_template:
        rep('const PHOTOS = __PHOTOS__;', 'const PHOTOS = __PHOTOS__;\nconst BOATMESH = __BOAT__;')
        rep("buildPurify();buildLabels()", "buildPurify();buildBoat();buildLabels()")
        rep("  updatePurify(dt);", "  updatePurify(dt);updateBoat(dt);")
        rep("window.__dt={scene,camera,controls,openCompare,setTime,flyTo,U,PUR};", "window.__dt={scene,camera,controls,openCompare,setTime,flyTo,U,PUR,BOAT,setMode};")
        rep("function sensorClean(s){if(!PUR.on)return 0;", "function sensorClean(s){if(MODE==='boat')return cleanAt(s.p[0],s.p[1]);if(!PUR.on)return 0;")
        # mode switch (3 modes)
        a = t.index("function setMode(on){"); b = t.index("$('#mPur').addEventListener")
        t = t[:a] + """function setMode(m){if(m===true)m='pur';if(m===false)m='normal';MODE=m;const on=m==='pur';PUR.on=on;PUR.t0=U.time.value;PUR.R=0;PUR.regrow=0;
  if(PUR.group)PUR.group.children.forEach(o=>{if(!o.userData.env)o.visible=on||(m==='boat'&&!o.userData.jet)});
  $('#purBody').hidden=!on;$('#normBody').hidden=m!=='normal';$('#boatBody').hidden=m!=='boat';
  [['mPur','pur'],['mNormal','normal'],['mBoat','boat']].forEach(([id,k])=>$('#'+id).setAttribute('aria-checked',String(m===k)));
  boatSetOn(m==='boat');SENS.forEach(s=>{const v=live[s.id];if(m!=='pur')Object.assign(v,POL,{c:0})});render()}
""" + t[b:]
        rep("$('#mPur').addEventListener('click',()=>setMode(true));$('#mNormal').addEventListener('click',()=>setMode(false));",
            "$('#mPur').addEventListener('click',()=>setMode('pur'));$('#mNormal').addEventListener('click',()=>setMode('normal'));$('#mBoat').addEventListener('click',()=>setMode('boat'));\n"
            "document.querySelectorAll('#boatBody [data-bs]').forEach(b=>b.addEventListener('click',()=>{BOAT.speed=+b.dataset.bs;document.querySelectorAll('#boatBody [data-bs]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)))}));\n"
            "$('#bFollow').addEventListener('click',()=>{BOAT.follow=!BOAT.follow;$('#bFollow').setAttribute('aria-pressed',String(BOAT.follow))});\n"
            "controls.addEventListener('start',()=>{if(BOAT.follow){BOAT.follow=false;$('#bFollow').setAttribute('aria-pressed','false')}});")
        rep("setMode(!PUR.on)});", "setMode(!PUR.on);if((e.key==='b'||e.key==='B'||e.key==='ㅠ')&&!e.metaKey&&!e.ctrlKey&&e.target.tagName!=='INPUT')setMode(MODE==='boat'?'pur':'boat')});")
        rep("setPressed(b.dataset.v);closeCompare();", "setPressed(b.dataset.v);closeCompare();if(BOAT.follow){BOAT.follow=false;$('#bFollow').setAttribute('aria-pressed','false')}")
        # HUD markup + css
        rep('data-i18n="mPur">정화 연출</button>', 'data-i18n="mPur">정화 연출</button><button id="mBoat" role="radio" aria-checked="false" data-i18n="mBoat">보트 운행</button>')
        rep('<kbd title="키보드 P로 전환" data-i18n-title="kbdP">P</kbd>', '<kbd title="키보드 P로 전환 · B 보트" data-i18n-title="kbdP">P·B</kbd>')
        rep('<div class="pnote" data-i18n="normNote">측정 5지점은 운전 전 기준값으로 표시됩니다</div></div>',
            '<div class="pnote" data-i18n="normNote">측정 5지점은 운전 전 기준값으로 표시됩니다</div></div>\n'
            '  <div id="boatBody" hidden><div class="sec" data-i18n="boatTitle">녹조제거 쌍동선 · 자율운항</div>\n'
            '  <div class="ph"><b id="boatPct">0%</b><span id="boatMsg" data-i18n="boatReady">출항 준비</span></div><div class="pbar"><i id="boatBar"></i></div>\n'
            '  <div class="brow"><span data-i18n="boatSpeed">배속</span><button data-bs="1" aria-pressed="false">×1</button><button data-bs="10" aria-pressed="true">×10</button><button data-bs="30" aria-pressed="false">×30</button><button id="bFollow" aria-pressed="true" data-i18n="boatFollow">보트 추적</button></div>\n'
            '  <div class="pnote" data-i18n="boatNote">수면 구역만 운항 · 녹조 밀집 구역 우선 탐색 · 전방 UFB 노즐 + 태양광 TiO₂/UVA ROS · 개념 시각화(실제 속도 1.5 m/s)</div></div>')
        rep("#purHud .pnote{", "#purHud .modes button#mBoat[aria-checked=\"true\"]{color:#082a14;background:#9ff0b8;border-color:#9ff0b8}\n"
            "#purHud .brow{display:flex;gap:4px;align-items:center;margin-top:7px;font-size:11px;color:var(--ink-3)}\n"
            "#purHud .brow button{font:500 11px var(--mono);color:var(--ink-2);background:rgba(255,255,255,.04);border:1px solid var(--glass-line);border-radius:5px;padding:3px 7px;cursor:pointer}\n"
            "#purHud .brow button[aria-pressed=\"true\"]{color:#06222a;background:#9ff0b8;border-color:#9ff0b8}\n#purHud .brow #bFollow{margin-left:auto;font-family:var(--ui)}\n"
            "#boatBar{background:linear-gradient(90deg,#9ff0b8,#e8fff0)!important}\n#purHud .pnote{")
        # i18n
        rep(" mPur:{ko:'정화 연출',en:'Purification',ja:'浄化演出'},", """ mPur:{ko:'정화 연출',en:'Purification',ja:'浄化演出'},
 mBoat:{ko:'보트 운행',en:'Boat',ja:'ボート運航'},
 boatTitle:{ko:'녹조제거 쌍동선 · 자율운항',en:'Algae-removal catamaran · autonomous',ja:'アオコ除去双胴船・自律運航'},
 boatReady:{ko:'출항 준비',en:'Ready to launch',ja:'出航準備'},
 boatRun:{ko:'운항 {v} m/s · 녹조 밀집 구역 탐색 → UFB·ROS 분사 중',en:'Cruising {v} m/s · seeking dense algae → spraying UFB + ROS',ja:'航行 {v} m/s・アオコ密集域を探索 → UFB・ROS噴射中'},
 boatDone:{ko:'호수 전역 녹조 제거 · 순회 유지 운항',en:'Lake-wide algae removed · patrol continues',ja:'湖全域のアオコ除去・巡回運航を継続'},
 boatSpeed:{ko:'배속',en:'Speed',ja:'倍速'},
 boatFollow:{ko:'보트 추적',en:'Follow',ja:'追跡'},
 boatNote:{ko:'수면 구역만 운항 · 녹조 밀집 구역 우선 탐색 · 전방 UFB 노즐 + 태양광 TiO₂/UVA ROS · 개념 시각화(실제 속도 1.5 m/s)',en:'Water area only · targets dense algae first · bow UFB nozzles + solar TiO₂/UVA ROS · concept visualization (real speed 1.5 m/s)',ja:'水域のみ航行・アオコ密集域を優先探索・船首UFBノズル＋太陽光TiO₂/UVA ROS・概念ビジュアル（実速度1.5 m/s）'},
 boatLbl:{ko:'녹조제거 쌍동선',en:'Algae-removal catamaran',ja:'アオコ除去双胴船'},""")
    p.write_text(t)

patch(ROOT/'src/template_v2.html', True)
print('patched')
