#!/usr/bin/env python3
"""v2 패치: 시간대를 현재 시각(한국 표준시)과 항상 동기화(30초마다) + 슬라이더로 임의 조절(0~24시), '실시간' 버튼으로 복귀. PDF 색상 인쇄 보정."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
p = ROOT/'src/template_v2.html'; t = p.read_text()
def rep(a, b):
    global t
    assert t.count(a) == 1, (a[:70], t.count(a)); t = t.replace(a, b)
rep('<label for="tod"><span data-i18n="tod">시간대</span> <b id="todv">14:00</b></label>\n    <input type="range" id="tod" min="5.5" max="20.5" step="0.25" value="14">',
    '<label for="tod"><span data-i18n="tod">시간대</span> <span class="tr"><button id="todLive" aria-pressed="true" data-i18n-title="todLiveT" title="현재 시각과 동기화">● LIVE</button><b id="todv">14:00</b></span></label>\n    <input type="range" id="tod" min="0" max="23.75" step="0.25" value="14">')
rep("#tbar label b{", "#tbar .tr{display:flex;align-items:center;gap:7px}#todLive{font:700 9.5px var(--mono);letter-spacing:.06em;color:var(--ink-3);background:rgba(255,255,255,.04);border:1px solid var(--glass-line);border-radius:4px;padding:2px 6px;cursor:pointer}\n"
    "#todLive[aria-pressed=\"true\"]{color:#ff6b6b;border-color:rgba(255,107,107,.5);background:rgba(255,80,80,.1)}#todLive[aria-pressed=\"true\"]::first-letter{animation:liveDot 1.4s infinite}@keyframes liveDot{50%{opacity:.2}}\n#tbar label b{")
rep("$('#tod').addEventListener('input',e=>setTime(+e.target.value));",
    "const kstHour=()=>{try{const f=new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Seoul',hour:'2-digit',minute:'2-digit',hour12:false}).formatToParts(new Date());const g=k=>+f.find(x=>x.type===k).value;return (g('hour')%24)+g('minute')/60}catch(e){const d=new Date();return d.getHours()+d.getMinutes()/60}};\n"
    "let todLive=true;function liveTick(){if(!todLive)return;const h=kstHour();$('#tod').value=String(Math.min(23.75,Math.round(h*4)/4));setTime(h)}   /* 현재 시각(KST) 동기화 */\n"
    "function setLive(on){todLive=on;const b=$('#todLive');b.setAttribute('aria-pressed',String(on));b.textContent=on?'● LIVE':T('todBack');if(on)liveTick()}\n"
    "$('#tod').addEventListener('input',e=>{if(todLive)setLive(false);setTime(+e.target.value)});$('#todLive').addEventListener('click',()=>setLive(!todLive));setInterval(liveTick,30000);")
rep("step(.97,T('ld8'),()=>{setTime(14);", "step(.97,T('ld8'),()=>{liveTick();")
rep("  @page{size:A4;margin:14mm}body{", "  @page{size:A4;margin:14mm}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}body{")
rep(" hudFold:{", " todLiveT:{ko:'현재 시각(한국 표준시)과 동기화 — 슬라이더를 움직이면 수동 모드',en:'Sync with current time (KST) — moving the slider switches to manual',ja:'現在時刻（韓国標準時）と同期 — スライダー操作で手動モード'},todBack:{ko:'↺ 실시간',en:'↺ LIVE',ja:'↺ リアルタイム'},\n hudFold:{")
p.write_text(t); print('clock patched')
