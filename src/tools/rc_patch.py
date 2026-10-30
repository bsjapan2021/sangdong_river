#!/usr/bin/env python3
"""v2 패치: 리모콘 수동 조종 — 방향키/WASD·화면 D-패드(길게 누르기)로 전진·후진·좌우 선회, 수면 밖·구조물·부유물 앞 자동 정지,
   리모콘 입력이 5초 끊기면 '신호 끊김'으로 판단해 가장 가까운 경로 지점부터 자율운항으로 자동 복귀. 3개 국어."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
RC = r"""
/* ---- 리모콘 수동 조종 ---- */
const RC={up:false,down:false,left:false,right:false,stop:false};const RC_TIMEOUT=5000;
function rcActive(){return RC.up||RC.down||RC.left||RC.right||RC.stop}
function rcInput(){if(!BOAT.on||MS.ph!==3)return;const now=performance.now();if(!MS.man){MS.man={last:now,v:BOAT.v,warn:0,tm:0};MS.rec=null;MS.avoid=null;BOAT.follow=true;const fb=$('#bFollow');if(fb)fb.setAttribute('aria-pressed','true');rcUi()}else MS.man.last=now}
function rcRelease(){MS.man=null;MS.prog=null;const tot=MS.path.length,pos=[BOAT.pos.x,BOAT.pos.y];let k=MS.pi,bd=1e9;
  for(let i=Math.max(0,MS.pi-20);i<tot;i++){const d=Math.hypot(MS.path[i][0]-pos[0],MS.path[i][1]-pos[1]);if(d<bd-1e-6){bd=d;k=i}}   /* 가장 가까운 경로 지점부터 재개 */
  MS.pi=Math.min(tot-1,k);MS.rcBackT=performance.now();rcUi()}
function rcMsg(){const M=MS.man;if(!M)return '';const idle=performance.now()-M.last;if(M.warn>performance.now())return T('msRcWall');
  return rcActive()||idle<800?T('msManual'):T('msRcIdle',{s:Math.max(0,Math.ceil((RC_TIMEOUT-idle)/1000))})}
function rcUi(){const el=$('#rc');if(!el)return;el.classList.toggle('man',!!MS.man);$('#rcSt').textContent=MS.man?T('rcManual'):T('rcAuto')}
function manualStep(dt,pos){const M=MS.man,now=performance.now();if(rcActive())M.last=now;
  if(now-M.last>RC_TIMEOUT){rcRelease();return true}   /* 리모콘 신호 끊김 → 자율 복귀 */
  const s=dt*Math.min(BOAT.speed,3);   /* 수동 조종은 최대 ×3 배속 */
  const turn=(RC.left?-1:0)+(RC.right?1:0);BOAT.hd+=turn*.85*s;
  const vt=RC.stop?0:RC.up?BOAT.base:RC.down?-.6:BOAT.v*.97;BOAT.v+=(vt-BOAT.v)*Math.min(1,s*1.2);
  const fx=Math.cos(BOAT.hd),fz=Math.sin(BOAT.hd);
  if(BOAT.v>0)for(const o of MS.obs){const dx=o.p[0]-pos[0],dz=o.p[1]-pos[1],d=Math.hypot(dx,dz);if(d<o.r+2.2&&(dx*fx+dz*fz)>0){BOAT.v=0;M.warn=now+1200}}   /* LiDAR 자동 정지 */
  const nx=pos[0]+fx*BOAT.v*s,nz=pos[1]+fz*BOAT.v*s;
  if(boatSoft([nx,nz])||!boatSoft(pos))BOAT.pos.set(nx,nz);else{BOAT.v=0;M.warn=now+1200}   /* 수면 밖·구조물 앞 정지 */
  M.tm+=dt;if(M.tm>.25){M.tm=0;const m=$('#boatMsg');if(m)m.textContent=rcMsg()}
  return true}
"""
def patch(path, html):
    p = ROOT/path; t = p.read_text()
    def rep(a, b):
        nonlocal t
        assert t.count(a) == 1, (path, a[:70], t.count(a)); t = t.replace(a, b)
    rep("/* ---- 고착 감지·탈출 루틴 ---- */", RC + "/* ---- 고착 감지·탈출 루틴 ---- */")
    rep("  if(!MS.prog)MS.prog={t:0,x:pos[0],z:pos[1]};MS.prog.t+=sdt;\n", "  if(MS.man)return manualStep(dt,pos);\n  if(!MS.prog)MS.prog={t:0,x:pos[0],z:pos[1]};MS.prog.t+=sdt;\n")
    rep("textContent=MS.rec?T('msRecover'):", "textContent=MS.man?rcMsg():(MS.rcBackT&&performance.now()-MS.rcBackT<4000)?T('msRcBack'):MS.rec?T('msRecover'):")
    rep("function missionStart(){if(!MS.G)return;MS.rec=null;", "function missionStart(){if(!MS.G)return;MS.man=null;MS.rec=null;")
    rep("function missionHide(){if(MS.G)MS.G.visible=false;", "function missionHide(){MS.man=null;const r=$('#rc');if(r)r.hidden=true;if(MS.G)MS.G.visible=false;")
    rep("  /* LiDAR */\n  MS.ang+=dt*12.566;", "  {const r=$('#rc');if(r){const sh=BOAT.on&&MS.ph===3;if(r.hidden===sh)r.hidden=!sh}}\n  /* LiDAR */\n  MS.ang+=dt*12.566;")
    if html:
        rep('<div id="credit"', '<div id="rc" class="panel" hidden aria-label="리모콘" data-i18n-aria="rcTitle">\n'
            '  <div class="rh"><b data-i18n="rcTitle">📡 리모콘</b><span id="rcSt">자율운항</span></div>\n'
            '  <div class="pad"><span></span><button data-k="up" aria-label="전진">▲</button><span></span><button data-k="left" aria-label="좌회전">◀</button><button data-k="stop" class="st" aria-label="정지">■</button><button data-k="right" aria-label="우회전">▶</button><span></span><button data-k="down" aria-label="후진">▼</button><span></span></div>\n'
            '  <button id="rcAuto" data-i18n="rcBackBtn">자율운항 복귀</button>\n'
            '  <div class="rn" data-i18n="rcHint">방향키·WASD 또는 버튼을 누르고 있으면 수동 조종 · 5초간 입력이 없으면 자율운항으로 복귀</div>\n</div>\n<div id="credit"')
        rep("#boatBar{background:",
            "#rc{left:16px;bottom:calc(76px + env(safe-area-inset-bottom,0px));width:178px;padding:9px 10px;user-select:none;-webkit-user-select:none;touch-action:none}\n"
            "#rc[hidden]{display:none!important}#rc .rh{display:flex;align-items:center;justify-content:space-between;font-size:12px;margin-bottom:7px}\n"
            "#rc #rcSt{font:600 10px var(--mono);padding:2px 6px;border-radius:4px;color:#7ff0b0;background:rgba(80,220,140,.12)}#rc.man #rcSt{color:#04222a;background:#ffd15a}\n"
            "#rc .pad{display:grid;grid-template-columns:repeat(3,1fr);gap:5px}#rc .pad button{height:40px;font:700 15px var(--ui);color:var(--ink);background:rgba(255,255,255,.07);border:1px solid var(--glass-line);border-radius:8px;cursor:pointer;touch-action:none}\n"
            "#rc .pad button.on{background:#8fe6ff;color:#04222a;border-color:#8fe6ff}#rc .pad .st{color:#ff8a95}\n"
            "#rc #rcAuto{width:100%;margin-top:7px;font:600 11.5px var(--ui);color:var(--ink-2);background:rgba(255,255,255,.04);border:1px solid var(--glass-line);border-radius:6px;padding:5px;cursor:pointer}#rc:not(.man) #rcAuto{opacity:.45}\n"
            "#rc .rn{font-size:10px;color:var(--ink-3);margin-top:6px;line-height:1.4}\n#boatBar{background:")
        rep("$('#bRestart').addEventListener('click',()=>{boatReset();missionStart()});",
            "$('#bRestart').addEventListener('click',()=>{boatReset();missionStart()});\n"
            "document.querySelectorAll('#rc .pad button').forEach(b=>{const k=b.dataset.k;const on=e=>{e.preventDefault();RC[k]=true;b.classList.add('on');rcInput()};const off=()=>{RC[k]=false;b.classList.remove('on')};\n"
            "  b.addEventListener('pointerdown',on);['pointerup','pointerleave','pointercancel'].forEach(ev=>b.addEventListener(ev,off))});\n"
            "$('#rcAuto').addEventListener('click',()=>{if(MS.man)rcRelease()});\n"
            "const RCK={ArrowUp:'up',ArrowDown:'down',ArrowLeft:'left',ArrowRight:'right',w:'up',s:'down',a:'left',d:'right',W:'up',S:'down',A:'left',D:'right','ㅈ':'up','ㄴ':'down','ㅁ':'left','ㅇ':'right',' ':'stop'};\n"
            "addEventListener('keydown',e=>{const k=RCK[e.key];if(!k||!BOAT.on||MS.ph!==3||/INPUT|TEXTAREA/.test(e.target.tagName)||e.metaKey||e.ctrlKey)return;e.preventDefault();RC[k]=true;rcInput();const b=document.querySelector(`#rc [data-k=\"${k}\"]`);if(b)b.classList.add('on')});\n"
            "addEventListener('keyup',e=>{const k=RCK[e.key];if(!k)return;RC[k]=false;const b=document.querySelector(`#rc [data-k=\"${k}\"]`);if(b)b.classList.remove('on')});\n"
            "addEventListener('blur',()=>{for(const k in RC)RC[k]=false;document.querySelectorAll('#rc .pad button.on').forEach(b=>b.classList.remove('on'))});")
        rep(" hudFold:{", " rcTitle:{ko:'📡 리모콘',en:'📡 Remote',ja:'📡 リモコン'},rcAuto:{ko:'자율운항',en:'AUTO',ja:'自律運航'},rcManual:{ko:'수동 조종',en:'MANUAL',ja:'手動操縦'},\n"
            " rcBackBtn:{ko:'자율운항 복귀',en:'Return to autonomous',ja:'自律運航に復帰'},\n"
            " rcHint:{ko:'방향키·WASD 또는 버튼을 누르고 있으면 수동 조종 · 5초간 입력이 없으면 자율운항으로 복귀',en:'Hold arrow keys / WASD or the buttons to steer · returns to autonomous after 5 s without input',ja:'方向キー・WASDまたはボタン長押しで手動操縦・5秒間入力がなければ自律運航に復帰'},\n"
            " msManual:{ko:'🎮 리모콘 수동 조종 중 · 방향키/버튼으로 운전',en:'🎮 Manual remote control · steer with arrows/buttons',ja:'🎮 リモコン手動操縦中・方向キー/ボタンで操作'},\n"
            " msRcIdle:{ko:'📡 리모콘 신호 없음 · {s}초 후 자율운항 복귀',en:'📡 No remote signal · back to autonomous in {s} s',ja:'📡 リモコン信号なし・{s}秒後に自律運航へ復帰'},\n"
            " msRcBack:{ko:'📡 리모콘 신호 끊김 → 자율운항 복귀 · 가장 가까운 경로부터 재개',en:'📡 Remote signal lost → autonomous mode resumed from the nearest route point',ja:'📡 リモコン信号途絶 → 自律運航に復帰・最寄りの経路から再開'},\n"
            " msRcWall:{ko:'⚠ 호안·구조물·부유물 근접 → 자동 정지 (방향을 바꾸세요)',en:'⚠ Shore / structure / obstacle ahead → auto-stop (turn away)',ja:'⚠ 護岸・構造物・浮遊物に接近 → 自動停止（向きを変えてください）'},\n hudFold:{")
    p.write_text(t)
patch('src/template_v2.html', True); patch('src/tools/boat.js', False); print('rc patched')
