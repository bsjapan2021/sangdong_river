#!/usr/bin/env python3
"""v2 패치: (1) 보트 회피 교착 해소(근접 시 후퇴·접근만 차단·장애물 비켜감·타임아웃) (2) 중앙 HUD 접기/자율운항 시 자동 축소 (3) 추적 카메라가 보트를 화면 아래쪽에 두도록"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
def patch(path, html):
    p = ROOT/path; t = p.read_text()
    def rep(a, b):
        nonlocal t
        assert t.count(a) == 1, (path, a[:70], t.count(a)); t = t.replace(a, b)
    rep("    if(boatValid(c))tg=c;else slow=.15;\n",
        "    if(boatValid(c))tg=c;else slow=.35;\n"
        "    A.t=(A.t||0)+sdt;if(dd<o.r+2.4){const e=[pos[0]-ux*6+px*2,pos[1]-uz*6+pz*2];if(boatValid(e)){tg=e;slow=.7}}   /* 너무 가까우면 후진·비켜서 간격 확보 */\n"
        "    if(A.t>25){let q=null;for(let k=0;k<80&&!q;k++){const s=PUR.samples[(Math.random()*PUR.samples.length)|0];if(boatValid([s[0],s[2]])&&Math.hypot(s[0]-pos[0],s[2]-pos[1])>45)q=[s[0],s[2]]}if(q){o.p=q;o.fade=0}dd=99}   /* 장기 교착 시 장애물이 흘러감 */\n")
    rep("  let slow=1;if(MS.avoid){const A=MS.avoid,o=A.o,dx=o.p[0]-pos[0],dz=o.p[1]-pos[1],dd=Math.hypot(dx,dz);",
        "  let slow=1;if(MS.avoid){const A=MS.avoid,o=A.o,dx=o.p[0]-pos[0],dz=o.p[1]-pos[1];let dd=Math.hypot(dx,dz);")
    rep("let blocked=false;for(const o of MS.obs)if(Math.hypot(nx-o.p[0],nz-o.p[1])<o.r+1)blocked=true;",
        "let blocked=false;for(const o of MS.obs){const dn=Math.hypot(nx-o.p[0],nz-o.p[1]),dc=Math.hypot(pos[0]-o.p[0],pos[1]-o.p[1]);if(dn<o.r+1&&dn<dc)blocked=true}   /* 장애물에 더 다가가는 이동만 차단(멀어지는 이동 허용) */")
    rep("if(boatValid([nx,nz])&&Math.hypot(nx-bx,nz-bz)>o.r+1.6)o.p=[nx,nz];else{const an=Math.random()*6.283;o.v=[Math.cos(an)*.18,Math.sin(an)*.18]}",
        "const db=Math.hypot(o.p[0]-bx,o.p[1]-bz);if(db<o.r+3.5){const ax=(o.p[0]-bx)/(db||1),az=(o.p[1]-bz)/(db||1);o.v=[ax*.4,az*.4]}   /* 보트가 다가오면 물결에 밀려 비켜남 */\n"
        "    if(boatValid([nx,nz])&&Math.hypot(nx-bx,nz-bz)>o.r+1.2)o.p=[nx,nz];else{const an=Math.random()*6.283;o.v=[Math.cos(an)*.18,Math.sin(an)*.18]}")
    rep("_bt.set(BOAT.pos.x,-0.3,BOAT.pos.y);_bc.set(BOAT.pos.x-fx*11+rx*5,5,BOAT.pos.y-fz*11+rz*5);",
        "_bt.set(BOAT.pos.x+fx*7,-0.3,BOAT.pos.y+fz*7);_bc.set(BOAT.pos.x-fx*12+rx*5,7.5,BOAT.pos.y-fz*12+rz*5);   /* 보트를 화면 아래쪽에 → 상단 패널에 가리지 않음 */")
    rep("MS.ph=3;MS.t=0;BOAT.follow=true;const fb=$('#bFollow');if(fb)fb.setAttribute('aria-pressed','true');msSteps()}",
        "MS.ph=3;MS.t=0;BOAT.follow=true;const fb=$('#bFollow');if(fb)fb.setAttribute('aria-pressed','true');msSteps();if(typeof hudMin==='function'&&!MS.userHud)hudMin(true)}")
    if html:
        rep('<kbd title="키보드 P로 전환 · B 보트" data-i18n-title="kbdP">P·B</kbd>',
            '<kbd title="키보드 P로 전환 · B 보트" data-i18n-title="kbdP">P·B</kbd><button id="hudMinB" class="hmin" aria-expanded="true" data-i18n-title="hudFold" title="패널 접기/펼치기">▴</button>')
        rep("#boatBar{background:",
            "#purHud .modes .hmin{flex:0 0 auto;padding:4px 8px;font:600 12px var(--ui)}\n"
            "#purHud.min .sec,#purHud.min .pnote,#purHud.min .brow,#purHud.min .msteps,#purHud.min .tele{display:none!important}\n"
            "#purHud.min{padding:7px 12px}#purHud.min .modes{margin-bottom:5px}#purHud.min .ph{font-size:11.5px}#purHud.min .ph b{font-size:16px}\n"
            "#boatBar{background:")
        rep("$('#bRestart').addEventListener('click',()=>{boatReset();missionStart()});",
            "$('#bRestart').addEventListener('click',()=>{boatReset();missionStart()});\n"
            "function hudMin(on){const h=$('#purHud');h.classList.toggle('min',on);const b=$('#hudMinB');b.textContent=on?'▾':'▴';b.setAttribute('aria-expanded',String(!on))}\n"
            "$('#hudMinB').addEventListener('click',()=>{MS.userHud=true;hudMin(!$('#purHud').classList.contains('min'))});\n"
            "if(matchMedia('(max-width:900px)').matches)hudMin(true);")
        rep(" boatLbl:{", " hudFold:{ko:'패널 접기/펼치기',en:'Collapse / expand panel',ja:'パネルの折りたたみ/展開'},\n boatLbl:{")
    p.write_text(t)
patch('src/template_v2.html', True)
patch('src/tools/boat.js', False)
print('fix patched')
