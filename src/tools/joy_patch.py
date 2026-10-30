#!/usr/bin/env python3
"""v2 패치: (1) 리모콘 D-패드 → 드래그형 원형 조이스틱(아날로그, 스마트폰 터치) (2) 관리자 '회원 화면 일괄 업데이트' — 배포 후 관리자창에서 누르면 모든 접속 화면이 새 버전으로 자동 새로고침"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
def patch(path, html):
    p = ROOT/path; t = p.read_text()
    def rep(a, b):
        nonlocal t
        assert t.count(a) == 1, (path, a[:70], t.count(a)); t = t.replace(a, b)
    rep("const RC={up:false,down:false,left:false,right:false,stop:false};", "const RC={up:false,down:false,left:false,right:false,stop:false,jx:0,jy:0};")
    rep("function rcActive(){return RC.up||RC.down||RC.left||RC.right||RC.stop}", "function rcActive(){return RC.up||RC.down||RC.left||RC.right||RC.stop||Math.hypot(RC.jx,RC.jy)>.08}")
    rep("  const turn=(RC.left?-1:0)+(RC.right?1:0);BOAT.hd+=turn*.85*s;\n  const vt=RC.stop?0:RC.up?BOAT.base:RC.down?-.6:BOAT.v*.97;",
        "  const jOn=Math.hypot(RC.jx,RC.jy)>.08;const turn=clamp((RC.left?-1:0)+(RC.right?1:0)+(jOn?RC.jx:0),-1,1);BOAT.hd+=turn*.85*s;   /* 조이스틱: 좌우=선회(아날로그) */\n"
        "  const vt=RC.stop?0:RC.up?BOAT.base:RC.down?-.6:(jOn&&Math.abs(RC.jy)>.12)?(RC.jy<0?BOAT.base*-RC.jy:-.6*RC.jy):BOAT.v*.97;   /* 위=전진·아래=후진(밀어낸 만큼 속도) */")
    if html:
        rep('<div class="pad"><span></span><button data-k="up" aria-label="전진">▲</button><span></span><button data-k="left" aria-label="좌회전">◀</button><button data-k="stop" class="st" aria-label="정지">■</button><button data-k="right" aria-label="우회전">▶</button><span></span><button data-k="down" aria-label="후진">▼</button><span></span></div>\n  <button id="rcAuto" data-i18n="rcBackBtn">자율운항 복귀</button>',
            '<div class="joy" id="joy" role="slider" aria-label="조이스틱" data-i18n-aria="rcJoy"><i class="ring"></i><span class="ar u">▲</span><span class="ar d">▼</span><span class="ar l">◀</span><span class="ar r">▶</span><div class="knob" id="joyK"></div></div>\n'
            '  <div class="jrow"><button data-k="stop" class="st" data-i18n="rcStop">■ 정지</button><button id="rcAuto" data-i18n="rcBackBtn">자율운항 복귀</button></div>')
        rep('data-i18n="rcHint">방향키·WASD 또는 버튼을 누르고 있으면 수동 조종 · 5초간 입력이 없으면 자율운항으로 복귀</div>',
            'data-i18n="rcHint">조이스틱을 끌어서(또는 방향키·WASD) 수동 조종 · 5초간 입력이 없으면 자율운항으로 복귀</div>')
        rep("#rc .pad{display:grid;", "#rc .joy{position:relative;width:132px;height:132px;margin:2px auto 0;border-radius:50%;touch-action:none;cursor:grab;\n"
            "  background:radial-gradient(circle at 50% 50%,rgba(143,230,255,.10),rgba(143,230,255,.03) 60%,rgba(0,0,0,.18));border:1px solid var(--glass-line);box-shadow:inset 0 0 18px rgba(0,0,0,.35)}\n"
            "#rc .joy .ring{position:absolute;inset:30%;border-radius:50%;border:1px dashed rgba(170,215,220,.22)}\n"
            "#rc .joy .ar{position:absolute;font-size:10px;color:var(--ink-3);pointer-events:none}#rc .joy .u{top:5px;left:50%;transform:translateX(-50%)}#rc .joy .d{bottom:5px;left:50%;transform:translateX(-50%)}#rc .joy .l{left:7px;top:50%;transform:translateY(-50%)}#rc .joy .r{right:7px;top:50%;transform:translateY(-50%)}\n"
            "#rc .joy .knob{position:absolute;left:50%;top:50%;width:50px;height:50px;margin:-25px 0 0 -25px;border-radius:50%;pointer-events:none;\n"
            "  background:radial-gradient(circle at 38% 32%,#e9fbff,#8fe6ff 45%,#3aa9c4);box-shadow:0 4px 14px rgba(0,0,0,.45),0 0 0 4px rgba(143,230,255,.15);transition:transform .18s ease-out}\n"
            "#rc .joy.drag{cursor:grabbing}#rc .joy.drag .knob{transition:none}\n"
            "#rc .jrow{display:flex;gap:5px;margin-top:8px}#rc .jrow button{flex:1;font:600 11.5px var(--ui);color:var(--ink-2);background:rgba(255,255,255,.04);border:1px solid var(--glass-line);border-radius:6px;padding:6px 4px;cursor:pointer;touch-action:none}\n"
            "#rc .jrow .st{color:#ff8a95}#rc .jrow .st.on{background:#ff5a6a;color:#fff}\n"
            "#rc .pad{display:grid;")
        rep("#rc #rcAuto{width:100%;margin-top:7px;", "#rc #rcAuto{")
        rep("document.querySelectorAll('#rc .pad button').forEach(b=>{",
            "{const J=$('#joy'),K=$('#joyK');let pid=null;const R=48;\n"
            "  const upd=e=>{const r=J.getBoundingClientRect();let x=e.clientX-(r.left+r.width/2),y=e.clientY-(r.top+r.height/2);const d=Math.hypot(x,y);if(d>R){x*=R/d;y*=R/d}\n"
            "    K.style.transform=`translate(${x}px,${y}px)`;RC.jx=x/R;RC.jy=y/R;rcInput()};\n"
            "  J.addEventListener('pointerdown',e=>{e.preventDefault();pid=e.pointerId;try{J.setPointerCapture(pid)}catch(_){}J.classList.add('drag');upd(e)});\n"
            "  J.addEventListener('pointermove',e=>{if(e.pointerId===pid)upd(e)});\n"
            "  const end=e=>{if(e.pointerId!==pid)return;pid=null;J.classList.remove('drag');K.style.transform='';RC.jx=0;RC.jy=0};\n"
            "  ['pointerup','pointercancel','lostpointercapture'].forEach(ev=>J.addEventListener(ev,end))}\n"
            "document.querySelectorAll('#rc [data-k]').forEach(b=>{")
        # ---- build id + update push ----
        rep("const BOATMESH = __BOAT__;", "const BOATMESH = __BOAT__;\nconst BUILD_ID = \"__BUILD__\";")
        rep("async function beat(){if(!API)return;const r=await api('track',{body:{p:location.pathname}});if(r.success&&r.data.blocked){$('#blockedScr').hidden=false;au.hidden=true}}",
            "async function beat(){if(!API)return;const r=await api('track',{body:{p:location.pathname,b:BUILD_ID}});if(r.success&&r.data.blocked){$('#blockedScr').hidden=false;au.hidden=true}\n"
            "  if(r.success&&r.data.release&&r.data.release.version>BUILD_ID)updateNotice(r.data.release)}\n"
            "let updTimer=null;function updateNotice(rel){if(updTimer)return;try{if(sessionStorage.getItem('sd_upd')===rel.version)return}catch(e){}   /* 같은 버전으로 이미 새로고침했는데도 구버전이면(캐시) 반복 새로고침 방지 */
  let n=10;const el=document.createElement('div');el.id='updToast';document.body.appendChild(el);\n"
            "  const go=()=>{try{sessionStorage.setItem('sd_upd',rel.version)}catch(e){}const u=new URL(location.href);u.searchParams.set('_v',rel.version);location.replace(u.toString())};\n"
            "  const draw=()=>{el.innerHTML=`<b>⟳ ${T('upTitle')}</b><span>${rel.note?esc(rel.note)+' · ':''}${T('upCount',{n})}</span><button>${T('upNow')}</button>`;el.querySelector('button').onclick=go};\n"
            "  draw();updTimer=setInterval(()=>{n--;if(n<=0){clearInterval(updTimer);go()}else draw()},1000)}\n"
            "document.addEventListener('visibilitychange',()=>{if(!document.hidden)beat()});\n"
            "try{const u=new URL(location.href);if(u.searchParams.has('_v')){u.searchParams.delete('_v');history.replaceState(null,'',u.pathname+(u.search||'')+u.hash)}}catch(e){}")
        rep('<button data-t="blocked" aria-selected="false">', '<button data-t="update" aria-selected="false"></button><button data-t="blocked" aria-selected="false">')
        rep("tb[2].textContent=`${T('adBlocked')}${d?` (${d.blocked.length})`:''}`;",
            "tb[2].textContent=`⟳ ${T('adUpdate')}`;tb[3].textContent=`${T('adBlocked')}${d?` (${d.blocked.length})`:''}`;")
        rep("  else{el.innerHTML=`<div class=\"kpis\"><div class=\"kpi\"><b>${d.blocked.length}</b>${T('adBlocked')}</div></div>",
            "  else if(admTab==='update'){const rel=d.release;const bv=b=>b?b.replace(/^(\\d{4})(\\d\\d)(\\d\\d)-(\\d\\d)(\\d\\d)(\\d\\d)$/,'$1-$2-$3 $4:$5:$6 UTC'):'—';\n"
            "    el.innerHTML=`<div class=\"kpis\"><div class=\"kpi\"><b style=\"font-size:13px\">${bv(BUILD_ID)}</b>${T('upMine')}</div><div class=\"kpi\"><b style=\"font-size:13px\" id=\"upLatest\">…</b>${T('upServer')}</div><div class=\"kpi\"><b style=\"font-size:13px\">${rel?bv(rel.version):'—'}</b>${T('upPushed')}${rel?' · '+fmt(rel.at):''}</div><div class=\"kpi\"><b>${d.visitors.filter(v=>v.online).length}</b>${T('adOnline')}</div></div>\n"
            "    <p class=\"note\" style=\"margin-top:0\">${T('upHow')}</p><div id=\"upWarn\" class=\"note\" style=\"color:#ffd15a\"></div>\n"
            "    <textarea id=\"upNote\" maxlength=\"120\" placeholder=\"${T('upNotePh')}\" style=\"width:100%;box-sizing:border-box;min-height:54px;margin-top:8px;font:500 12.5px var(--ui);color:var(--ink);background:rgba(255,255,255,.05);border:1px solid var(--glass-line);border-radius:7px;padding:8px\"></textarea>\n"
            "    <div class=\"acts\" style=\"margin-top:8px\"><button class=\"ok\" id=\"upPush\" style=\"padding:7px 14px;font-size:12.5px\">⟳ ${T('upPush')}</button></div>`;\n"
            "    fetch('/?v='+Date.now(),{cache:'no-store'}).then(r=>r.text()).then(h=>{const m=h.match(/BUILD_ID = \"([0-9-]+)\"/);const lv=m?m[1]:null;$('#upLatest').textContent=bv(lv);\n"
            "      if(lv&&lv>BUILD_ID)$('#upWarn').textContent=T('upStale');}).catch(()=>{});\n"
            "    $('#upPush').onclick=async()=>{if(!confirm(T('upConfirm')))return;const r=await api('admin?a=release',{body:{version:BUILD_ID,note:$('#upNote').value.trim()}});if(!r.success){alert(errMsg(r.error));return}alert(T('upDone'));admLoad()}}\n"
            "  else{el.innerHTML=`<div class=\"kpis\"><div class=\"kpi\"><b>${d.blocked.length}</b>${T('adBlocked')}</div></div>")
        rep("#blockedScr{", "#updToast{position:fixed;left:50%;top:calc(14px + env(safe-area-inset-top,0px));transform:translateX(-50%);z-index:80;display:flex;align-items:center;gap:10px;flex-wrap:wrap;justify-content:center;max-width:calc(100vw - 24px);\n"
            "  background:rgba(8,26,32,.95);border:1px solid #8fe6ff;border-radius:10px;padding:10px 14px;font-size:12.5px;color:var(--ink);box-shadow:0 10px 30px rgba(0,0,0,.45)}\n"
            "#updToast b{color:#8fe6ff}#updToast button{font:700 12px var(--ui);color:#04222a;background:#8fe6ff;border:0;border-radius:6px;padding:5px 10px;cursor:pointer}\n#blockedScr{")
        rep(" hudFold:{", " rcJoy:{ko:'조이스틱',en:'Joystick',ja:'ジョイスティック'},rcStop:{ko:'■ 정지',en:'■ Stop',ja:'■ 停止'},\n"
            " adUpdate:{ko:'업데이트',en:'Update',ja:'アップデート'},upMine:{ko:'내 화면 버전',en:'My page build',ja:'自分の画面のバージョン'},upServer:{ko:'서버 최신 배포',en:'Latest deployed build',ja:'サーバー最新配信'},upPushed:{ko:'회원 적용 버전',en:'Pushed to members',ja:'会員適用バージョン'},\n"
            " upHow:{ko:'새 버전을 배포한 뒤 이 화면을 새로고침해 ‘내 화면 버전’이 최신인지 확인하고 아래 버튼을 누르세요. 접속 중인 모든 화면(회원·방문자)에 안내가 뜨고 10초 후 자동으로 새 버전으로 새로고침됩니다(최대 45초 내 반영).',en:'After deploying, reload this page so “My page build” is the latest, then press the button. Every open page (members and visitors) shows a notice and reloads to the new build after 10 s (within ~45 s).',ja:'新バージョン配信後にこの画面を再読み込みし「自分の画面のバージョン」が最新か確認してからボタンを押してください。接続中の全画面に通知が表示され、10秒後に自動で新バージョンへ再読み込みされます（最大45秒以内）。'},\n"
            " upStale:{ko:'⚠ 내 화면이 서버 최신 배포보다 오래되었습니다. 먼저 새로고침(⌘+Shift+R)하세요.',en:'⚠ Your page is older than the latest deployment. Reload first (⌘+Shift+R).',ja:'⚠ 自分の画面がサーバー最新配信より古いです。先に再読み込み（⌘+Shift+R）してください。'},\n"
            " upNotePh:{ko:'업데이트 안내 문구(선택) — 예: 보트 리모콘 조이스틱 추가',en:'Update note (optional) — e.g. joystick remote added',ja:'更新案内（任意）— 例：ボートのジョイスティック追加'},\n"
            " upPush:{ko:'회원 화면 일괄 업데이트',en:'Update all member pages',ja:'会員画面を一括更新'},upConfirm:{ko:'접속 중인 모든 화면을 지금 이 버전으로 새로고침할까요?',en:'Reload every open page to this build now?',ja:'接続中のすべての画面をこのバージョンに更新しますか？'},\n"
            " upDone:{ko:'배포 알림을 보냈습니다. 접속 중인 화면이 45초 안에 새 버전으로 바뀝니다.',en:'Update pushed. Open pages will switch within 45 s.',ja:'更新を通知しました。接続中の画面は45秒以内に切り替わります。'},\n"
            " upTitle:{ko:'새 버전이 배포되었습니다',en:'A new version is available',ja:'新しいバージョンが配信されました'},upCount:{ko:'{n}초 후 자동 새로고침',en:'reloading in {n} s',ja:'{n}秒後に自動更新'},upNow:{ko:'지금 새로고침',en:'Reload now',ja:'今すぐ更新'},\n hudFold:{")
    p.write_text(t)
patch('src/template_v2.html', True); patch('src/tools/boat.js', False); print('joy+update patched')
