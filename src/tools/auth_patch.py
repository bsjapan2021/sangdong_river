#!/usr/bin/env python3
"""v2 패치: 스플래시 + 로그인/회원가입/이메일 인증/비밀번호 찾기·재설정 + 최고관리자 전용 접속자 관리(회원 승인·차단·해지, IP 차단·해제). 3개 국어."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
p = ROOT/'src/template_v2.html'; t = p.read_text()
def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (a[:80], t.count(a)); t = t.replace(a, b)

CSS = r"""
/* ---------- splash · auth · admin ---------- */
#splash{position:fixed;inset:0;z-index:60;display:grid;place-items:center;overflow:hidden;color:var(--ink);
  background:radial-gradient(120% 90% at 50% 110%,#0f4a52 0%,#07232a 45%,#030c10 100%);transition:opacity .9s ease}
#splash.out{opacity:0;pointer-events:none}
#splash .bub{position:absolute;bottom:-40px;border-radius:50%;border:1px solid rgba(160,240,255,.45);background:radial-gradient(circle at 32% 30%,rgba(255,255,255,.55),rgba(140,230,255,.08) 45%,rgba(140,230,255,0) 70%);animation:rise linear infinite}
@keyframes rise{from{transform:translateY(0) translateX(0)}50%{transform:translateY(-55vh) translateX(14px)}to{transform:translateY(-115vh) translateX(-10px)}}
#splash .ros{position:absolute;width:3px;height:3px;border-radius:50%;background:#c99bff;box-shadow:0 0 8px 2px rgba(201,155,255,.7);animation:twk 2.4s ease-in-out infinite}
@keyframes twk{0%,100%{opacity:0}50%{opacity:1}}
#splash .sp{position:relative;text-align:center;padding:0 20px;max-width:560px}
#splash .eb{font:600 11px var(--mono);letter-spacing:.32em;color:#7fe3ff}
#splash h1{font:700 clamp(26px,5vw,40px)/1.15 var(--ui);margin:14px 0 6px;letter-spacing:-.01em}
#splash .sub{font-size:13px;color:var(--ink-2)}
#splash .logo{width:74px;height:74px;margin:0 auto 4px;border-radius:50%;display:grid;place-items:center;
  background:radial-gradient(circle at 35% 30%,#bff6ff,#3fb7cf 55%,#0d5160);box-shadow:0 0 40px rgba(110,220,240,.45),inset 0 -6px 14px rgba(0,0,0,.3);font:800 20px var(--ui);color:#04222a}
#splash .pg{width:min(300px,70vw);height:3px;background:rgba(255,255,255,.1);margin:22px auto 8px;border-radius:2px;overflow:hidden}
#splash .pg i{display:block;height:100%;width:4%;background:linear-gradient(90deg,#7fe3ff,#e8fbff);transition:width .25s}
#splash .st{font:500 11px var(--mono);color:var(--ink-3);min-height:16px}
#splash .cp{position:absolute;bottom:calc(14px + env(safe-area-inset-bottom,0px));left:0;right:0;text-align:center;font-size:10.5px;color:rgba(255,255,255,.45)}
#auth{position:fixed;inset:0;z-index:61;display:grid;place-items:center;padding:16px;overflow:auto}
#auth[hidden]{display:none!important}
#auth .card{width:min(400px,100%);background:rgba(8,22,27,.86);border:1px solid var(--glass-line);border-radius:14px;padding:20px 22px 18px;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);box-shadow:0 20px 60px rgba(0,0,0,.45)}
#auth .top{display:flex;align-items:center;gap:8px;margin-bottom:12px}
#auth .top b{font:700 15px var(--ui);flex:1}
#auth .alangs{display:flex;gap:3px}#auth .alangs button{font:600 10px var(--ui);color:var(--ink-2);background:transparent;border:1px solid var(--glass-line);border-radius:4px;padding:2px 6px;cursor:pointer}
#auth .alangs button[aria-pressed="true"]{color:#06222a;background:#8fe6ff;border-color:#8fe6ff}
#auth .tabs{display:flex;gap:4px;margin-bottom:12px}
#auth .tabs button{flex:1;font:600 12.5px var(--ui);color:var(--ink-2);background:rgba(255,255,255,.04);border:1px solid var(--glass-line);border-radius:7px;padding:7px;cursor:pointer}
#auth .tabs button[aria-selected="true"]{color:#06222a;background:#8fe6ff;border-color:#8fe6ff}
#auth label{display:block;font-size:11px;color:var(--ink-3);margin:8px 0 3px}
#auth input,#auth textarea{width:100%;box-sizing:border-box;font:500 13.5px var(--ui);color:var(--ink);background:rgba(255,255,255,.05);border:1px solid var(--glass-line);border-radius:7px;padding:9px 10px;outline:none}
#auth input:focus,#auth textarea:focus{border-color:#8fe6ff;box-shadow:0 0 0 3px rgba(143,230,255,.15)}
#auth textarea{resize:vertical;min-height:52px}
#auth .row2{display:grid;grid-template-columns:1fr 1fr;gap:8px}
#auth .go{width:100%;margin-top:14px;font:700 14px var(--ui);color:#04222a;background:#8fe6ff;border:0;border-radius:8px;padding:10px;cursor:pointer}
#auth .go:disabled{opacity:.55;cursor:wait}
#auth .lnk{background:none;border:0;color:#9fd8ff;font:500 12px var(--ui);cursor:pointer;padding:0;text-decoration:underline;text-underline-offset:2px}
#auth .links{display:flex;justify-content:space-between;gap:8px;margin-top:10px;flex-wrap:wrap}
#auth .msg{font-size:12.5px;line-height:1.5;margin-top:10px;padding:8px 10px;border-radius:7px;display:none}
#auth .msg.err{display:block;color:#ffb4b4;background:rgba(255,80,80,.1);border:1px solid rgba(255,120,120,.25)}
#auth .msg.okm{display:block;color:#b9f5cf;background:rgba(80,220,140,.1);border:1px solid rgba(120,230,160,.25)}
#auth .chk{display:flex;gap:7px;align-items:flex-start;font-size:11.5px;color:var(--ink-2);margin-top:10px}#auth .chk input{width:auto;margin-top:2px}
#auth .cp{text-align:center;font-size:10px;color:var(--ink-3);margin-top:12px}
#who{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-top:8px;padding-top:7px;border-top:1px solid var(--glass-line);font-size:11.5px;color:var(--ink-2)}
#who[hidden]{display:none!important}#who b{color:var(--ink);font-weight:600}
#who button{font:500 11px var(--ui);color:var(--ink-2);background:rgba(255,255,255,.04);border:1px solid var(--glass-line);border-radius:5px;padding:2px 7px;cursor:pointer}
#who #wAdmin{color:#04222a;background:#ffd15a;border-color:#ffd15a;font-weight:700}
#who .pend{display:inline-block;min-width:15px;padding:0 4px;margin-left:3px;border-radius:8px;background:#ff5a6a;color:#fff;font-size:10px;text-align:center}
#adm{position:fixed;inset:0;z-index:55;display:grid;place-items:center;background:rgba(2,8,10,.55);padding:12px}
#adm[hidden]{display:none!important}
#adm .box{width:min(1100px,100%);height:min(86vh,900px);display:flex;flex-direction:column;background:rgba(8,20,24,.95);border:1px solid var(--glass-line);border-radius:12px;overflow:hidden}
#adm .hd{display:flex;align-items:center;gap:10px;padding:12px 16px;border-bottom:1px solid var(--glass-line)}
#adm .hd b{font:700 15px var(--ui)}#adm .hd .sm{font-size:11px;color:var(--ink-3);flex:1}
#adm .hd button{font:500 12px var(--ui);color:var(--ink-2);background:rgba(255,255,255,.05);border:1px solid var(--glass-line);border-radius:6px;padding:4px 10px;cursor:pointer}
#adm .tabs{display:flex;gap:4px;padding:10px 16px 0}
#adm .tabs button{font:600 12.5px var(--ui);color:var(--ink-2);background:transparent;border:1px solid var(--glass-line);border-bottom:0;border-radius:7px 7px 0 0;padding:7px 14px;cursor:pointer}
#adm .tabs button[aria-selected="true"]{color:#06222a;background:#8fe6ff;border-color:#8fe6ff}
#adm .bd{flex:1;overflow:auto;padding:0 16px 14px;border-top:1px solid var(--glass-line)}
#adm .kpis{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 10px}
#adm .kpi{background:rgba(255,255,255,.04);border:1px solid var(--glass-line);border-radius:8px;padding:6px 12px;font-size:11px;color:var(--ink-3)}#adm .kpi b{display:block;font:700 18px var(--mono);color:var(--ink)}
#adm table{width:100%;border-collapse:collapse;font-size:12px}
#adm th{position:sticky;top:0;background:#0b1d22;text-align:left;font-weight:600;color:var(--ink-3);font-size:11px;padding:7px 6px;border-bottom:1px solid var(--glass-line);white-space:nowrap}
#adm td{padding:7px 6px;border-bottom:1px solid rgba(170,215,220,.08);vertical-align:top}
#adm td .s{font-size:10.5px;color:var(--ink-3)}
#adm .tag{display:inline-block;font-size:10.5px;padding:1px 6px;border-radius:4px;white-space:nowrap}
#adm .t-pending{color:#ffd15a;background:rgba(255,209,90,.12)}#adm .t-active{color:#7ff0b0;background:rgba(80,220,140,.12)}#adm .t-blocked{color:#ff8a95;background:rgba(255,90,106,.14)}
#adm .t-adm{color:#04222a;background:#ffd15a}#adm .t-nv{color:#ffb86b;background:rgba(255,160,80,.12)}
#adm .acts{display:flex;gap:4px;flex-wrap:wrap}
#adm .acts button{font:600 11px var(--ui);border-radius:5px;padding:3px 8px;cursor:pointer;border:1px solid var(--glass-line);background:rgba(255,255,255,.05);color:var(--ink-2);white-space:nowrap}
#adm .acts .ok{color:#04222a;background:#7ff0b0;border-color:#7ff0b0}#adm .acts .no{color:#fff;background:#d9465a;border-color:#d9465a}#adm .acts .warn{color:#04222a;background:#ffd15a;border-color:#ffd15a}
#adm .dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#59656a;margin-right:5px}#adm .dot.on{background:#3fe08a;box-shadow:0 0 6px #3fe08a}
#adm .note{font-size:11px;color:var(--ink-3);margin:10px 0 0}
#adm .tp{font:600 13px var(--mono);color:#ffd15a;user-select:all}
#blockedScr{position:fixed;inset:0;z-index:70;display:grid;place-items:center;background:#05090b;color:var(--ink);text-align:center;padding:20px}
#blockedScr[hidden]{display:none!important}
@media (prefers-reduced-motion:reduce){#splash .bub,#splash .ros{animation:none;display:none}}
"""

HTML = r"""
<div id="splash" role="status" aria-live="polite">
  <div class="sp">
    <div class="logo">NHI</div>
    <div class="eb">NANOHYDROIN CO., LTD.</div>
    <h1 data-i18n="spTitle">상동호수공원 디지털트윈</h1>
    <div class="sub" data-i18n="spSub">NHI PhotoNano · UFB × TiO₂/UVA 광촉매 수질개선 · K-테스트베드 2026</div>
    <div class="pg"><i id="spBar"></i></div>
    <div class="st" id="spTxt"></div>
  </div>
  <div class="cp" data-i18n="credit">© 2026 주식회사 나노하이드로인 (NanoHydroIn Co., Ltd.) · All rights reserved</div>
</div>
<div id="auth" hidden>
  <div class="card">
    <div class="top"><b data-i18n="spTitle">상동호수공원 디지털트윈</b><div class="alangs"><button data-lang="ko">한국어</button><button data-lang="en">EN</button><button data-lang="ja">日本語</button></div></div>
    <div class="tabs" role="tablist" id="aTabs"><button role="tab" data-v="login" data-i18n="auLogin">로그인</button><button role="tab" data-v="register" data-i18n="auRegister">회원가입</button></div>
    <form id="fLogin" data-v="login">
      <label data-i18n="auEmail">이메일</label><input name="email" type="email" autocomplete="username" required>
      <label data-i18n="auPw">비밀번호</label><input name="password" type="password" autocomplete="current-password" required>
      <button class="go" type="submit" data-i18n="auLogin">로그인</button>
      <div class="links"><button type="button" class="lnk" data-go="forgot" data-i18n="auForgot">비밀번호를 잊으셨나요?</button><button type="button" class="lnk" id="aResend" hidden data-i18n="auResend">인증 메일 다시 보내기</button></div>
    </form>
    <form id="fRegister" data-v="register" hidden>
      <div class="row2"><div><label data-i18n="auName">이름</label><input name="name" required maxlength="60" autocomplete="name"></div>
        <div><label data-i18n="auPhone">연락처</label><input name="phone" required maxlength="40" autocomplete="tel"></div></div>
      <label data-i18n="auEmail">이메일</label><input name="email" type="email" required autocomplete="email">
      <div class="row2"><div><label data-i18n="auPw8">비밀번호(8자 이상)</label><input name="password" type="password" minlength="8" required autocomplete="new-password"></div>
        <div><label data-i18n="auPw2">비밀번호 확인</label><input name="password2" type="password" minlength="8" required autocomplete="new-password"></div></div>
      <label data-i18n="auOrg">소속(기관·회사)</label><input name="org" maxlength="80" autocomplete="organization">
      <label data-i18n="auMemo">이용 목적</label><textarea name="memo" maxlength="300"></textarea>
      <div class="chk"><input type="checkbox" name="agree" id="aAgree" required><label for="aAgree" style="margin:0" data-i18n="auAgree">개인정보(이름·이메일·연락처·소속·접속 IP) 수집·이용에 동의합니다. 가입 후 이메일 인증과 관리자 승인을 거쳐 이용할 수 있습니다.</label></div>
      <button class="go" type="submit" data-i18n="auRegister">회원가입</button>
    </form>
    <form id="fForgot" data-v="forgot" hidden>
      <p style="font-size:12.5px;color:var(--ink-2);margin:0 0 4px" data-i18n="auForgotP">가입한 이메일을 입력하면 비밀번호 재설정 링크를 보내드립니다.</p>
      <label data-i18n="auEmail">이메일</label><input name="email" type="email" required>
      <button class="go" type="submit" data-i18n="auSendLink">재설정 링크 보내기</button>
      <div class="links"><button type="button" class="lnk" data-go="login" data-i18n="auBack">로그인으로 돌아가기</button></div>
    </form>
    <form id="fReset" data-v="reset" hidden>
      <p style="font-size:12.5px;color:var(--ink-2);margin:0 0 4px" data-i18n="auResetP">새 비밀번호를 입력하세요.</p>
      <label data-i18n="auPw8">비밀번호(8자 이상)</label><input name="password" type="password" minlength="8" required autocomplete="new-password">
      <label data-i18n="auPw2">비밀번호 확인</label><input name="password2" type="password" minlength="8" required autocomplete="new-password">
      <button class="go" type="submit" data-i18n="auSetPw">비밀번호 변경</button>
    </form>
    <form id="fChange" data-v="change" hidden>
      <label data-i18n="auCurPw">현재 비밀번호</label><input name="current" type="password" required autocomplete="current-password">
      <label data-i18n="auPw8">비밀번호(8자 이상)</label><input name="password" type="password" minlength="8" required autocomplete="new-password">
      <label data-i18n="auPw2">비밀번호 확인</label><input name="password2" type="password" minlength="8" required autocomplete="new-password">
      <button class="go" type="submit" data-i18n="auSetPw">비밀번호 변경</button>
      <div class="links"><button type="button" class="lnk" id="aCancel" data-i18n="auClose">닫기</button></div>
    </form>
    <div class="msg" id="aMsg" role="alert"></div>
    <div class="cp" data-i18n="credit">© 2026 주식회사 나노하이드로인 (NanoHydroIn Co., Ltd.) · All rights reserved</div>
  </div>
</div>
<div id="adm" hidden role="dialog" aria-modal="true" aria-labelledby="admT">
  <div class="box">
    <div class="hd"><b id="admT" data-i18n="adTitle">접속자 관리</b><span class="sm" data-i18n="adOnly">최고관리자 전용 · 일반 회원에게는 보이지 않습니다</span><button id="admRef" data-i18n="adRefresh">새로고침</button><button id="admX" data-i18n="auClose">닫기</button></div>
    <div class="tabs" role="tablist"><button data-t="members" aria-selected="true"></button><button data-t="visitors" aria-selected="false"></button><button data-t="blocked" aria-selected="false"></button></div>
    <div class="bd" id="admBody"></div>
  </div>
</div>
<div id="blockedScr" hidden><div><div style="font-size:44px">⛔</div><h2 data-i18n="blkTitle">접속이 차단되었습니다</h2><p style="color:var(--ink-2);font-size:13px" data-i18n="blkP">이 IP 또는 계정의 접속이 관리자에 의해 차단되었습니다. 문의: 주식회사 나노하이드로인</p></div></div>
"""

JS = r"""
/* ================= 스플래시 · 회원 인증 · 최고관리자 접속자 관리 ================= */
(function(){
const API=location.protocol.startsWith('http');            /* file:// 오프라인 실행은 로컬 전용 → 인증 생략 */
const TK='sd_token';let token=null,me=null,splashMin=false,sceneReady=false,authDone=false,admTab='members',admData=null,admTimer=null,tempPw={};
try{token=localStorage.getItem(TK)}catch(e){}
const sp=$('#splash'),au=$('#auth'),msg=$('#aMsg');
/* splash decoration */
(function(){const n=matchMedia('(prefers-reduced-motion: reduce)').matches?0:26;for(let i=0;i<n;i++){const b=document.createElement('i');b.className='bub';const s=6+Math.random()*34;
  b.style.cssText=`left:${Math.random()*100}%;width:${s}px;height:${s}px;animation-duration:${7+Math.random()*9}s;animation-delay:${-Math.random()*12}s;opacity:${.35+Math.random()*.5}`;sp.appendChild(b)}
  for(let i=0;i<n;i++){const r=document.createElement('i');r.className='ros';r.style.cssText=`left:${Math.random()*100}%;top:${Math.random()*100}%;animation-delay:${-Math.random()*2.4}s;background:${Math.random()<.5?'#bdefff':'#c99bff'}`;sp.appendChild(r)}})();
setTimeout(()=>{splashMin=true;maybeOpen()},2200);
/* mirror loading progress */
const lb=$('#ldbar'),lt=$('#ldtxt');setInterval(()=>{if(lb)$('#spBar').style.width=Math.max(4,parseFloat(lb.style.width)||0)+'%';if(lt)$('#spTxt').textContent=lt.textContent;
  if(!sceneReady&&$('#loading').classList.contains('done')){sceneReady=true;$('#spBar').style.width='100%';maybeOpen()}},150);
function maybeOpen(){if(!splashMin||!authDone)return;if(me||!API){if(sceneReady){sp.classList.add('out');au.hidden=true}}else{au.hidden=false}}
async function api(path,opt={}){const h={'Content-Type':'application/json'};if(token)h.Authorization='Bearer '+token;
  try{const r=await fetch('/api/'+path,{method:opt.body?'POST':'GET',headers:h,body:opt.body?JSON.stringify(opt.body):undefined,cache:'no-store'});
    let j=null;try{j=await r.json()}catch(e){}return j||{success:false,error:{code:'HTTP_'+r.status,message:'HTTP '+r.status}}}
  catch(e){return {success:false,error:{code:'NETWORK',message:String(e)}}}}
const errMsg=e=>{const k='er_'+((e&&e.code)||'X');const v=T(k);return v===k?((e&&e.message)||T('er_X')):v};
function say(text,good){msg.textContent=text;msg.className='msg '+(good?'okm':'err')}
function clearMsg(){msg.className='msg';msg.textContent=''}
function view(v){document.querySelectorAll('#auth form').forEach(f=>f.hidden=f.dataset.v!==v);document.querySelectorAll('#aTabs button').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.v===v)));
  $('#aTabs').hidden=!(v==='login'||v==='register');clearMsg();const f=document.querySelector(`#auth form[data-v="${v}"] input`);if(f)setTimeout(()=>f.focus(),50)}
document.querySelectorAll('#aTabs button').forEach(b=>b.onclick=()=>view(b.dataset.v));
document.querySelectorAll('#auth [data-go]').forEach(b=>b.onclick=()=>view(b.dataset.go));
document.querySelectorAll('#auth .alangs button').forEach(b=>b.onclick=()=>{setLang(b.dataset.lang);syncLang()});
function syncLang(){document.querySelectorAll('#auth .alangs button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.lang===LANG)));if(!$('#adm').hidden)admRender();renderWho()}
document.querySelectorAll('#langs button').forEach(b=>b.addEventListener('click',syncLang));
const fd=f=>Object.fromEntries(new FormData(f).entries());
async function busy(f,fn){const b=f.querySelector('.go');b.disabled=true;try{await fn()}finally{b.disabled=false}}
let lastEmail='';
$('#fLogin').onsubmit=e=>{e.preventDefault();const f=e.target;busy(f,async()=>{const d=fd(f);lastEmail=d.email;const r=await api('auth?a=login',{body:d});
  if(r.success){token=r.data.token;try{localStorage.setItem(TK,token)}catch(e){}me=r.data.member;f.reset();onAuthed()}else{say(errMsg(r.error));$('#aResend').hidden=r.error.code!=='EMAIL_UNVERIFIED'}})};
$('#aResend').onclick=async()=>{const r=await api('auth?a=resend',{body:{email:lastEmail}});say(r.success?T('auResent'):errMsg(r.error),r.success)};
$('#fRegister').onsubmit=e=>{e.preventDefault();const f=e.target;const d=fd(f);if(d.password!==d.password2)return say(T('er_PWMATCH'));busy(f,async()=>{
  const r=await api('auth?a=register',{body:d});if(r.success){f.reset();view('login');say(r.data.verificationSent?T('auRegMail'):T('auRegPending'),true)}else say(errMsg(r.error))})};
$('#fForgot').onsubmit=e=>{e.preventDefault();const f=e.target;busy(f,async()=>{const r=await api('auth?a=forgot',{body:fd(f)});
  if(r.success)say(r.data.mail?T('auForgotSent'):T('auForgotNoMail'),!!r.data.mail);else say(errMsg(r.error))})};
const qs=new URLSearchParams(location.search);const resetTok=qs.get('reset'),verifyTok=qs.get('verify');
function cleanUrl(){try{const u=new URL(location.href);['reset','verify'].forEach(k=>u.searchParams.delete(k));history.replaceState(null,'',u.pathname+(u.search||'')+u.hash)}catch(e){}}
$('#fReset').onsubmit=e=>{e.preventDefault();const f=e.target;const d=fd(f);if(d.password!==d.password2)return say(T('er_PWMATCH'));busy(f,async()=>{
  const r=await api('auth?a=reset',{body:{token:resetTok,password:d.password}});if(r.success){cleanUrl();f.reset();view('login');say(r.data.status==='pending'?T('auResetDonePending'):T('auResetDone'),true)}else say(errMsg(r.error))})};
$('#fChange').onsubmit=e=>{e.preventDefault();const f=e.target;const d=fd(f);if(d.password!==d.password2)return say(T('er_PWMATCH'));busy(f,async()=>{
  const r=await api('auth?a=password',{body:{current:d.current,password:d.password}});if(r.success){f.reset();say(T('auPwChanged'),true);setTimeout(()=>{au.hidden=true;view('login')},1300)}else say(errMsg(r.error))})};
$('#aCancel').onclick=()=>{au.hidden=true;view('login')};
/* who chip in head panel */
const who=document.createElement('div');who.id='who';who.hidden=true;$('#head').appendChild(who);
function renderWho(){if(!me){who.hidden=true;return}who.hidden=false;const pend=(admData&&admData.members||[]).filter(m=>m.status==='pending').length;
  who.innerHTML=`<span>👤 <b></b>${me.role==='admin'?' · '+T('adSuper'):''}</span><button id="wPw">${T('auChangePw')}</button><button id="wOut">${T('auLogout')}</button>${me.superAdmin?`<button id="wAdmin">👥 ${T('adTitle')}${pend?`<span class="pend">${pend}</span>`:''}</button>`:''}`;
  who.querySelector('b').textContent=me.name;$('#wOut').onclick=logout;$('#wPw').onclick=()=>{au.hidden=false;view('change')};if(me.superAdmin)$('#wAdmin').onclick=openAdm;layoutPanels()}
function logout(){api('auth?a=logout',{body:{}});token=null;me=null;try{localStorage.removeItem(TK)}catch(e){}closeAdm();renderWho();sp.classList.remove('out');au.hidden=false;view('login')}
/* heartbeat / blocking */
async function beat(){if(!API)return;const r=await api('track',{body:{p:location.pathname}});if(r.success&&r.data.blocked){$('#blockedScr').hidden=false;au.hidden=true}}
setInterval(()=>{if(!document.hidden)beat()},45000);
function onAuthed(){authDone=true;clearMsg();au.hidden=me?true:au.hidden;renderWho();beat();maybeOpen();
  if(me&&me.superAdmin){admLoad(true);if(qs.get('admin')==='1')setTimeout(openAdm,400)}}
/* boot */
(async()=>{applyI18n();syncLang();
  if(!API){authDone=true;maybeOpen();return}
  beat();
  if(verifyTok){const r=await api('auth?a=verify',{body:{token:verifyTok}});cleanUrl();authDone=true;view('login');
    say(r.success?(r.data.status==='pending'?T('auVerifiedPending'):T('auVerified')):errMsg(r.error),r.success);maybeOpen();return}
  if(resetTok){authDone=true;view('reset');maybeOpen();return}
  if(token){const r=await api('auth?a=me');if(r.success){me=r.data.member;onAuthed();return}
    if(r.error&&r.error.code==='AUTH_DISABLED'){me={name:'guest',role:'user'};authDone=true;maybeOpen();return}
    if(r.error&&r.error.code==='IP_BLOCKED'){$('#blockedScr').hidden=false;return}
    token=null;try{localStorage.removeItem(TK)}catch(e){}}
  else{const r=await api('auth?a=me');if(r.error&&r.error.code==='AUTH_DISABLED'){me=null;authDone=true;au.hidden=true;sp.dataset.open=1;
      /* 서버 회원 기능 미설정: 열람 허용(롤아웃 유예) */ me={name:'guest',role:'user'};maybeOpen();return}}
  authDone=true;view('login');maybeOpen()})();
/* ---------- admin panel (최고관리자 전용 — 서버에서도 superAdmin 토큰만 허용) ---------- */
const fmt=ms=>{if(!ms)return '—';const d=new Date(ms);return d.toLocaleString(LANG==='ko'?'ko-KR':LANG==='ja'?'ja-JP':'en-US',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'})};
const ago=ms=>{const s=Math.max(0,(Date.now()-ms)/1000);return s<60?T('adSec',{n:Math.round(s)}):s<3600?T('adMin',{n:Math.round(s/60)}):s<86400?T('adHour',{n:Math.round(s/3600)}):T('adDay',{n:Math.round(s/86400)})};
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function uaShort(u){u=u||'';const os=/iPhone|iPad/.test(u)?'iOS':/Android/.test(u)?'Android':/Mac OS/.test(u)?'macOS':/Windows/.test(u)?'Windows':/Linux/.test(u)?'Linux':'?';
  const br=/Edg\//.test(u)?'Edge':/Whale/.test(u)?'Whale':/SamsungBrowser/.test(u)?'Samsung':/Chrome\//.test(u)?'Chrome':/Safari\//.test(u)?'Safari':/Firefox/.test(u)?'Firefox':/bot|crawl|spider/i.test(u)?'Bot':'?';return br+' · '+os}
async function admLoad(silent){const r=await api('admin?a=overview');if(r.success){admData=r.data;renderWho();if(!$('#adm').hidden)admRender()}else if(!silent){$('#admBody').innerHTML=`<p class="note">${esc(errMsg(r.error))}</p>`}}
function openAdm(){$('#adm').hidden=false;admRender();admLoad();clearInterval(admTimer);admTimer=setInterval(()=>admLoad(true),15000)}
function closeAdm(){$('#adm').hidden=true;clearInterval(admTimer)}
$('#admX').onclick=closeAdm;$('#admRef').onclick=()=>admLoad();addEventListener('keydown',e=>{if(e.key==='Escape'&&!$('#adm').hidden)closeAdm()});
document.querySelectorAll('#adm .tabs button').forEach(b=>b.onclick=()=>{admTab=b.dataset.t;admRender()});
async function act(a,payload,confirmKey){if(confirmKey&&!confirm(T(confirmKey,payload)))return;const r=await api('admin?a='+a,{body:payload});
  if(!r.success){alert(errMsg(r.error));return}if(r.data&&r.data.tempPassword)tempPw[payload.id]=r.data.tempPassword;await admLoad()}
function admRender(){const d=admData;const tb=document.querySelectorAll('#adm .tabs button');
  const pend=d?d.members.filter(m=>m.status==='pending').length:0,onl=d?d.visitors.filter(v=>v.online).length:0;
  tb[0].textContent=`${T('adMembers')}${d?` (${d.members.length})`:''}${pend?` · ${T('adPendingN',{n:pend})}`:''}`;tb[1].textContent=`${T('adVisitors')}${d?` · ${T('adOnlineN',{n:onl})}`:''}`;tb[2].textContent=`${T('adBlocked')}${d?` (${d.blocked.length})`:''}`;
  tb.forEach(b=>b.setAttribute('aria-selected',String(b.dataset.t===admTab)));const el=$('#admBody');if(!d){el.innerHTML=`<p class="note">${T('adLoading')}</p>`;return}
  if(admTab==='members'){const st={pending:T('stPending'),active:T('stActive'),blocked:T('stBlocked')};
    el.innerHTML=`<div class="kpis"><div class="kpi"><b>${d.members.length}</b>${T('adTotal')}</div><div class="kpi"><b style="color:#ffd15a">${pend}</b>${T('stPending')}</div><div class="kpi"><b style="color:#7ff0b0">${d.members.filter(m=>m.status==='active').length}</b>${T('stActive')}</div><div class="kpi"><b style="color:#ff8a95">${d.members.filter(m=>m.status==='blocked').length}</b>${T('stBlocked')}</div><div class="kpi"><b>${d.mail?'ON':'OFF'}</b>${T('adMail')}</div></div>
    <table><thead><tr><th>${T('auName')} / ${T('auEmail')}</th><th>${T('auOrg')} · ${T('auPhone')}</th><th>${T('auMemo')}</th><th>${T('adState')}</th><th>${T('adJoined')}</th><th>${T('adLastLogin')}</th><th>${T('adActions')}</th></tr></thead><tbody>
    ${d.members.map(m=>`<tr><td><b>${esc(m.name)}</b> ${m.superAdmin?`<span class="tag t-adm">${T('adSuper')}</span>`:''}<div class="s">${esc(m.email)}</div></td><td>${esc(m.org||'—')}<div class="s">${esc(m.phone||'')}</div></td><td class="s" style="max-width:220px">${esc(m.memo||'')}</td>
      <td><span class="tag t-${m.status}">${st[m.status]||m.status}</span>${m.emailVerified?'':` <span class="tag t-nv">${T('adUnverified')}</span>`}</td><td class="s">${fmt(m.createdAt)}</td><td class="s">${m.lastLogin?fmt(m.lastLogin):'—'}<div>${esc(m.lastIp||'')}</div></td>
      <td>${m.superAdmin?'<span class="s">—</span>':`<div class="acts">${m.status==='pending'?`<button class="ok" data-a="approve" data-id="${m.id}">${T('acApprove')}</button>`:''}${m.status==='active'?`<button class="no" data-a="block" data-id="${m.id}">${T('acBlock')}</button>`:''}${m.status==='blocked'?`<button class="ok" data-a="unblock" data-id="${m.id}">${T('acUnblock')}</button>`:''}${m.emailVerified?'':`<button class="warn" data-a="verify" data-id="${m.id}">${T('acVerify')}</button>`}<button data-a="temp-password" data-id="${m.id}">${T('acTemp')}</button><button data-a="delete" data-id="${m.id}">${T('acDelete')}</button></div>${tempPw[m.id]?`<div class="s" style="margin-top:4px">${T('adTempIs')} <span class="tp">${esc(tempPw[m.id])}</span></div>`:''}`}</td></tr>`).join('')}
    </tbody></table><p class="note">${T('adMemberNote')}</p>`;
    el.querySelectorAll('[data-a]').forEach(b=>b.onclick=()=>{const a=b.dataset.a,id=+b.dataset.id,m=d.members.find(x=>x.id===id);
      if(a==='delete'){const c=prompt(T('cfDelete',{e:m.email}));if(c===null)return;act('delete',{id,confirm:c.trim()});return}
      act(a,{id,e:m.email,n:m.name},a==='block'?'cfBlock':a==='temp-password'?'cfTemp':null)})}
  else if(admTab==='visitors'){
    el.innerHTML=`<div class="kpis"><div class="kpi"><b style="color:#3fe08a">${onl}</b>${T('adOnline')}</div><div class="kpi"><b>${d.visitors.length}</b>${T('adRecent14')}</div><div class="kpi"><b>${d.visitors.filter(v=>v.email).length}</b>${T('adMemberIps')}</div><div class="kpi"><b style="font-size:13px">${esc(d.me.ip)}</b>${T('adMyIp')}</div></div>
    <table><thead><tr><th>IP</th><th>${T('adWhere')}</th><th>${T('adMember')}</th><th>${T('adDevice')}</th><th>${T('adFirst')}</th><th>${T('adLast')}</th><th>${T('adHits')}</th><th>${T('adActions')}</th></tr></thead><tbody>
    ${d.visitors.map(v=>`<tr><td><span class="dot ${v.online?'on':''}"></span>${esc(v.ip)}${v.ip===d.me.ip?` <span class="tag t-adm">${T('adMe')}</span>`:''}${v.blocked?` <span class="tag t-blocked">${T('stBlocked')}</span>`:''}</td>
      <td class="s">${esc([v.city,v.country].filter(Boolean).join(', ')||'—')}</td><td>${v.email?`${esc(v.name||'')}<div class="s">${esc(v.email)}</div>`:`<span class="s">${T('adGuest')}</span>`}</td><td class="s">${esc(uaShort(v.ua))}</td>
      <td class="s">${fmt(v.firstSeen)}</td><td class="s">${v.online?`<b style="color:#3fe08a">${T('adNow')}</b>`:ago(v.lastSeen)}</td><td class="s">${v.hits}</td>
      <td>${v.ip===d.me.ip?'<span class="s">—</span>':`<div class="acts">${v.blocked?`<button class="ok" data-ip="${esc(v.ip)}" data-a="ip-unblock">${T('acIpUnblock')}</button>`:`<button class="no" data-ip="${esc(v.ip)}" data-a="ip-block">${T('acIpBlock')}</button>`}</div>`}</td></tr>`).join('')}
    </tbody></table><p class="note">${T('adVisitNote')}</p>`;
    el.querySelectorAll('[data-ip]').forEach(b=>b.onclick=()=>{const ip=b.dataset.ip;if(b.dataset.a==='ip-block'){const rs=prompt(T('cfIpBlock',{ip}),'');if(rs===null)return;act('ip-block',{ip,reason:rs})}else act('ip-unblock',{ip})})}
  else{el.innerHTML=`<div class="kpis"><div class="kpi"><b>${d.blocked.length}</b>${T('adBlocked')}</div></div>
    <div style="display:flex;gap:6px;margin:4px 0 10px"><input id="admIp" placeholder="IP" style="font:500 12.5px var(--mono);color:var(--ink);background:rgba(255,255,255,.05);border:1px solid var(--glass-line);border-radius:6px;padding:6px 8px;width:200px"><input id="admRs" data-ph="adReason" placeholder="${T('adReason')}" style="flex:1;font:500 12.5px var(--ui);color:var(--ink);background:rgba(255,255,255,.05);border:1px solid var(--glass-line);border-radius:6px;padding:6px 8px"><div class="acts"><button class="no" id="admAddIp">${T('acIpBlock')}</button></div></div>
    <table><thead><tr><th>IP</th><th>${T('adReason')}</th><th>${T('adBlockedAt')}</th><th>${T('adBy')}</th><th>${T('adActions')}</th></tr></thead><tbody>
    ${d.blocked.map(b=>`<tr><td>${esc(b.ip)}</td><td class="s">${esc(b.reason||'—')}</td><td class="s">${fmt(b.at)}</td><td class="s">${esc(b.by||'')}</td><td><div class="acts"><button class="ok" data-ip="${esc(b.ip)}">${T('acIpUnblock')}</button></div></td></tr>`).join('')||`<tr><td colspan="5" class="s">${T('adNone')}</td></tr>`}
    </tbody></table>`;
    $('#admAddIp').onclick=()=>{const ip=$('#admIp').value.trim();if(ip)act('ip-block',{ip,reason:$('#admRs').value.trim()})};
    el.querySelectorAll('[data-ip]').forEach(b=>b.onclick=()=>act('ip-unblock',{ip:b.dataset.ip}))}}
})();
"""

I18N = r""" spTitle:{ko:'상동호수공원 디지털트윈',en:'Sangdong Lake Park Digital Twin',ja:'上洞湖水公園デジタルツイン'},
 spSub:{ko:'NHI PhotoNano · UFB × TiO₂/UVA 광촉매 수질개선 · K-테스트베드 2026',en:'NHI PhotoNano · UFB × TiO₂/UVA photocatalytic water treatment · K-Testbed 2026',ja:'NHI PhotoNano・UFB×TiO₂/UVA光触媒水質改善・Kテストベッド2026'},
 auLogin:{ko:'로그인',en:'Sign in',ja:'ログイン'},auRegister:{ko:'회원가입',en:'Sign up',ja:'会員登録'},auEmail:{ko:'이메일',en:'Email',ja:'メール'},auPw:{ko:'비밀번호',en:'Password',ja:'パスワード'},
 auPw8:{ko:'비밀번호(8자 이상)',en:'Password (8+ chars)',ja:'パスワード（8文字以上）'},auPw2:{ko:'비밀번호 확인',en:'Confirm password',ja:'パスワード確認'},auCurPw:{ko:'현재 비밀번호',en:'Current password',ja:'現在のパスワード'},
 auName:{ko:'이름',en:'Name',ja:'氏名'},auPhone:{ko:'연락처',en:'Phone',ja:'連絡先'},auOrg:{ko:'소속(기관·회사)',en:'Organization',ja:'所属（機関・会社）'},auMemo:{ko:'이용 목적',en:'Purpose of use',ja:'利用目的'},
 auAgree:{ko:'개인정보(이름·이메일·연락처·소속·접속 IP) 수집·이용에 동의합니다. 가입 후 이메일 인증과 관리자 승인을 거쳐 이용할 수 있습니다.',en:'I agree to the collection and use of my personal data (name, email, phone, organization, access IP). After sign-up, email verification and administrator approval are required.',ja:'個人情報（氏名・メール・連絡先・所属・接続IP）の収集・利用に同意します。登録後、メール認証と管理者承認を経て利用できます。'},
 auForgot:{ko:'비밀번호를 잊으셨나요?',en:'Forgot password?',ja:'パスワードをお忘れですか？'},auResend:{ko:'인증 메일 다시 보내기',en:'Resend verification email',ja:'認証メールを再送'},
 auForgotP:{ko:'가입한 이메일을 입력하면 비밀번호 재설정 링크를 보내드립니다.',en:'Enter your email and we will send you a password reset link.',ja:'登録メールを入力すると、パスワード再設定リンクをお送りします。'},
 auSendLink:{ko:'재설정 링크 보내기',en:'Send reset link',ja:'再設定リンクを送信'},auBack:{ko:'로그인으로 돌아가기',en:'Back to sign in',ja:'ログインに戻る'},
 auResetP:{ko:'새 비밀번호를 입력하세요.',en:'Enter a new password.',ja:'新しいパスワードを入力してください。'},auSetPw:{ko:'비밀번호 변경',en:'Change password',ja:'パスワード変更'},auClose:{ko:'닫기',en:'Close',ja:'閉じる'},
 auChangePw:{ko:'비밀번호 변경',en:'Change password',ja:'パスワード変更'},auLogout:{ko:'로그아웃',en:'Sign out',ja:'ログアウト'},
 auRegMail:{ko:'가입 신청이 접수되었습니다. 메일함의 인증 링크를 눌러 이메일 인증을 완료해 주세요. 관리자 승인 후 로그인할 수 있습니다.',en:'Sign-up received. Please click the verification link in your inbox. You can sign in after administrator approval.',ja:'登録を受け付けました。メールの認証リンクをクリックしてください。管理者の承認後にログインできます。'},
 auRegPending:{ko:'가입 신청이 접수되었습니다. 관리자 승인 후 로그인할 수 있습니다.',en:'Sign-up received. You can sign in after administrator approval.',ja:'登録を受け付けました。管理者の承認後にログインできます。'},
 auResent:{ko:'인증 메일을 다시 보냈습니다. 메일함을 확인해 주세요.',en:'Verification email sent again. Please check your inbox.',ja:'認証メールを再送しました。メールをご確認ください。'},
 auForgotSent:{ko:'가입된 이메일이면 재설정 링크를 보냈습니다(1시간 유효). 메일함을 확인해 주세요.',en:'If the email is registered, a reset link has been sent (valid 1 h).',ja:'登録済みのメールであれば再設定リンクを送信しました（1時間有効）。'},
 auForgotNoMail:{ko:'현재 메일 발송이 설정되지 않았습니다. 관리자에게 임시 비밀번호 발급을 요청해 주세요.',en:'Email sending is not configured yet. Please ask the administrator for a temporary password.',ja:'現在メール送信が設定されていません。管理者に仮パスワードの発行を依頼してください。'},
 auResetDone:{ko:'비밀번호가 변경되었습니다. 새 비밀번호로 로그인하세요.',en:'Password changed. Please sign in with your new password.',ja:'パスワードを変更しました。新しいパスワードでログインしてください。'},
 auResetDonePending:{ko:'비밀번호가 변경되었습니다. 관리자 승인 후 로그인할 수 있습니다.',en:'Password changed. You can sign in after administrator approval.',ja:'パスワードを変更しました。管理者承認後にログインできます。'},
 auVerified:{ko:'이메일 인증이 완료되었습니다. 로그인하세요.',en:'Email verified. Please sign in.',ja:'メール認証が完了しました。ログインしてください。'},
 auVerifiedPending:{ko:'이메일 인증이 완료되었습니다. 관리자 승인 후 로그인할 수 있습니다.',en:'Email verified. You can sign in after administrator approval.',ja:'メール認証が完了しました。管理者承認後にログインできます。'},
 auPwChanged:{ko:'비밀번호가 변경되었습니다.',en:'Password changed.',ja:'パスワードを変更しました。'},
 er_X:{ko:'요청을 처리하지 못했습니다. 잠시 후 다시 시도하세요.',en:'Request failed. Please try again later.',ja:'処理できませんでした。しばらくしてから再度お試しください。'},
 er_NETWORK:{ko:'서버에 연결할 수 없습니다. 네트워크를 확인하세요.',en:'Cannot reach the server. Check your network.',ja:'サーバーに接続できません。ネットワークをご確認ください。'},
 er_PWMATCH:{ko:'비밀번호 확인이 일치하지 않습니다.',en:'Passwords do not match.',ja:'パスワードが一致しません。'},
 er_BAD_CREDENTIALS:{ko:'이메일 또는 비밀번호가 올바르지 않습니다.',en:'Incorrect email or password.',ja:'メールまたはパスワードが正しくありません。'},
 er_EMAIL_UNVERIFIED:{ko:'이메일 인증이 필요합니다. 메일함의 인증 링크를 확인하세요.',en:'Email verification required. Check your inbox for the link.',ja:'メール認証が必要です。認証リンクをご確認ください。'},
 er_PENDING_APPROVAL:{ko:'관리자 승인 대기 중입니다. 승인 후 로그인할 수 있습니다.',en:'Awaiting administrator approval.',ja:'管理者の承認待ちです。'},
 er_ACCOUNT_BLOCKED:{ko:'이용이 차단된 계정입니다. 관리자에게 문의하세요.',en:'This account is blocked. Contact the administrator.',ja:'このアカウントは利用停止中です。管理者にお問い合わせください。'},
 er_IP_BLOCKED:{ko:'접속이 차단된 IP입니다. 관리자에게 문의하세요.',en:'Access from this IP is blocked.',ja:'このIPからの接続は遮断されています。'},
 er_EMAIL_TAKEN:{ko:'이미 가입된 이메일입니다.',en:'This email is already registered.',ja:'既に登録されているメールです。'},
 er_RATE_LIMIT:{ko:'요청이 많습니다. 잠시 후 다시 시도하세요.',en:'Too many requests. Please wait a moment.',ja:'リクエストが多すぎます。しばらくお待ちください。'},
 er_LOGIN_LOCKED:{ko:'로그인 시도가 많아 10분간 잠겼습니다.',en:'Too many attempts — locked for 10 minutes.',ja:'試行回数が多いため10分間ロックされました。'},
 er_INVALID_TOKEN:{ko:'링크가 유효하지 않거나 만료되었습니다.',en:'The link is invalid or has expired.',ja:'リンクが無効または期限切れです。'},
 er_AUTH_DISABLED:{ko:'회원 기능이 아직 설정되지 않았습니다.',en:'Membership is not configured yet.',ja:'会員機能がまだ設定されていません。'},
 er_FORBIDDEN:{ko:'최고관리자만 접근할 수 있습니다.',en:'Super-administrator only.',ja:'最高管理者のみアクセスできます。'},
 er_SELF_BLOCK:{ko:'현재 사용 중인 내 IP는 차단할 수 없습니다.',en:'You cannot block your own current IP.',ja:'現在使用中の自分のIPは遮断できません。'},
 er_CONFIRM:{ko:'확인용 이메일이 일치하지 않습니다.',en:'Confirmation email does not match.',ja:'確認用メールが一致しません。'},
 adTitle:{ko:'접속자 관리',en:'Access management',ja:'アクセス管理'},adOnly:{ko:'최고관리자 전용 · 일반 회원에게는 보이지 않습니다',en:'Super-admin only · hidden from regular members',ja:'最高管理者専用・一般会員には表示されません'},
 adRefresh:{ko:'새로고침',en:'Refresh',ja:'更新'},adMembers:{ko:'회원',en:'Members',ja:'会員'},adVisitors:{ko:'접속자',en:'Visitors',ja:'接続者'},adBlocked:{ko:'차단 IP',en:'Blocked IPs',ja:'遮断IP'},
 adPendingN:{ko:'승인 대기 {n}',en:'{n} pending',ja:'承認待ち {n}'},adOnlineN:{ko:'접속 중 {n}',en:'{n} online',ja:'接続中 {n}'},adLoading:{ko:'불러오는 중…',en:'Loading…',ja:'読み込み中…'},
 adTotal:{ko:'전체',en:'Total',ja:'全体'},adMail:{ko:'메일 발송',en:'Email',ja:'メール送信'},stPending:{ko:'승인 대기',en:'Pending',ja:'承認待ち'},stActive:{ko:'승인됨',en:'Active',ja:'承認済み'},stBlocked:{ko:'차단',en:'Blocked',ja:'遮断'},
 adState:{ko:'상태',en:'Status',ja:'状態'},adJoined:{ko:'가입일',en:'Joined',ja:'登録日'},adLastLogin:{ko:'최근 로그인 · IP',en:'Last sign-in · IP',ja:'最終ログイン・IP'},adActions:{ko:'관리',en:'Actions',ja:'操作'},
 adSuper:{ko:'최고관리자',en:'Super admin',ja:'最高管理者'},adUnverified:{ko:'메일 미인증',en:'Unverified',ja:'メール未認証'},
 acApprove:{ko:'승인',en:'Approve',ja:'承認'},acBlock:{ko:'차단',en:'Block',ja:'遮断'},acUnblock:{ko:'차단 해지',en:'Unblock',ja:'遮断解除'},acVerify:{ko:'인증 처리',en:'Mark verified',ja:'認証済みにする'},
 acTemp:{ko:'임시 비밀번호',en:'Temp password',ja:'仮パスワード'},acDelete:{ko:'삭제',en:'Delete',ja:'削除'},acIpBlock:{ko:'IP 차단',en:'Block IP',ja:'IP遮断'},acIpUnblock:{ko:'차단 해제',en:'Unblock',ja:'遮断解除'},
 adTempIs:{ko:'임시 비밀번호(본인에게 전달 후 변경 안내):',en:'Temp password (share it and ask them to change it):',ja:'仮パスワード（本人に伝え変更を案内）:'},
 adMemberNote:{ko:'신규 가입은 ‘승인 대기’로 시작합니다. 승인하면 로그인할 수 있고, 차단하면 즉시 이용이 중지되며 ‘차단 해지’로 복구합니다.',en:'New sign-ups start as Pending. Approve to allow sign-in; Block stops access immediately; Unblock restores it.',ja:'新規登録は「承認待ち」から始まります。承認でログイン可能、遮断で即時停止、遮断解除で復旧します。'},
 adOnline:{ko:'현재 접속',en:'Online now',ja:'現在接続'},adRecent14:{ko:'최근 14일 IP',en:'IPs (14 days)',ja:'直近14日のIP'},adMemberIps:{ko:'회원 IP',en:'Member IPs',ja:'会員IP'},adMyIp:{ko:'내 IP',en:'My IP',ja:'自分のIP'},
 adWhere:{ko:'지역',en:'Location',ja:'地域'},adMember:{ko:'회원',en:'Member',ja:'会員'},adDevice:{ko:'브라우저 · OS',en:'Browser · OS',ja:'ブラウザ・OS'},adFirst:{ko:'최초 접속',en:'First seen',ja:'初回接続'},adLast:{ko:'최근 접속',en:'Last seen',ja:'最終接続'},
 adHits:{ko:'횟수',en:'Hits',ja:'回数'},adMe:{ko:'나',en:'me',ja:'自分'},adGuest:{ko:'비로그인',en:'guest',ja:'未ログイン'},adNow:{ko:'접속 중',en:'online',ja:'接続中'},
 adSec:{ko:'{n}초 전',en:'{n}s ago',ja:'{n}秒前'},adMin:{ko:'{n}분 전',en:'{n} min ago',ja:'{n}分前'},adHour:{ko:'{n}시간 전',en:'{n} h ago',ja:'{n}時間前'},adDay:{ko:'{n}일 전',en:'{n} d ago',ja:'{n}日前'},
 adVisitNote:{ko:'최근 2분 내 신호가 있으면 ‘접속 중’입니다. IP 차단은 공유 IP·VPN에 한계가 있으니 계정 차단과 함께 사용하세요.',en:'“Online” = heartbeat within 2 min. IP blocking is limited for shared IPs/VPNs — combine it with account blocking.',ja:'2分以内に信号があれば「接続中」です。IP遮断は共有IP・VPNに限界があるため、アカウント遮断と併用してください。'},
 adReason:{ko:'차단 사유',en:'Reason',ja:'遮断理由'},adBlockedAt:{ko:'차단 일시',en:'Blocked at',ja:'遮断日時'},adBy:{ko:'처리자',en:'By',ja:'処理者'},adNone:{ko:'차단된 IP가 없습니다.',en:'No blocked IPs.',ja:'遮断中のIPはありません。'},
 cfBlock:{ko:'{n}({e}) 회원을 차단할까요? 즉시 이용이 중지됩니다.',en:'Block {n} ({e})? Access stops immediately.',ja:'{n}（{e}）を遮断しますか？即時に利用停止されます。'},
 cfTemp:{ko:'{n}({e}) 회원의 비밀번호를 임시 비밀번호로 바꿀까요?',en:'Replace the password of {n} ({e}) with a temporary one?',ja:'{n}（{e}）のパスワードを仮パスワードに変更しますか？'},
 cfDelete:{ko:'삭제는 되돌릴 수 없습니다. 확인을 위해 이메일({e})을 입력하세요.',en:'Deletion cannot be undone. Type the email ({e}) to confirm.',ja:'削除は元に戻せません。確認のためメール（{e}）を入力してください。'},
 cfIpBlock:{ko:'{ip} 를 차단합니다. 차단 사유(선택):',en:'Block {ip}. Reason (optional):',ja:'{ip} を遮断します。理由（任意）:'},
 blkTitle:{ko:'접속이 차단되었습니다',en:'Access blocked',ja:'接続が遮断されました'},blkP:{ko:'이 IP 또는 계정의 접속이 관리자에 의해 차단되었습니다. 문의: 주식회사 나노하이드로인',en:'Access from this IP or account has been blocked by the administrator. Contact: NanoHydroIn Co., Ltd.',ja:'このIPまたはアカウントの接続は管理者により遮断されています。お問い合わせ：株式会社ナノハイドロイン'},
"""

rep("@media (prefers-reduced-motion:reduce){#loading{transition:none}}", "@media (prefers-reduced-motion:reduce){#loading{transition:none}}" + CSS)
rep('<div id="stage"></div>', '<div id="stage"></div>' + HTML)
rep(" mPur:{ko:'정화 연출'", I18N + " mPur:{ko:'정화 연출'")
rep("window.__dt={scene,", JS + "\nwindow.__dt={scene,")
p.write_text(t); print('auth patched')
