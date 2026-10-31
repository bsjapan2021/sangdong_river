/* ================= 스플래시 · 회원 인증 · 최고관리자 접속자 관리 ================= */
(function(){
const API=location.protocol.startsWith('http');            /* file:// 오프라인 실행은 로컬 전용 → 인증 생략 */
const TK='app_token';let token=null,me=null,splashMin=false,sceneReady=false,authDone=false,admTab='members',admData=null,admTimer=null,tempPw={};
try{token=localStorage.getItem(TK)}catch(e){}
const sp=$('#splash'),au=$('#auth'),msg=$('#aMsg');
/* splash decoration */
(function(){const n=matchMedia('(prefers-reduced-motion: reduce)').matches?0:26;for(let i=0;i<n;i++){const b=document.createElement('i');b.className='bub';const s=6+Math.random()*34;
  b.style.cssText=`left:${Math.random()*100}%;width:${s}px;height:${s}px;animation-duration:${7+Math.random()*9}s;animation-delay:${-Math.random()*12}s;opacity:${.35+Math.random()*.5}`;sp.appendChild(b)}
  for(let i=0;i<n;i++){const r=document.createElement('i');r.className='ros';r.style.cssText=`left:${Math.random()*100}%;top:${Math.random()*100}%;animation-delay:${-Math.random()*2.4}s;background:${Math.random()<.5?'#bdefff':'#c99bff'}`;sp.appendChild(r)}})();
setTimeout(()=>{splashMin=true;maybeOpen()},2200);
/* 앱 로딩 연동: 앱이 준비되면 window.authAppReady() 호출, 진행률은 window.authProgress(0~100, '문구') */
window.authProgress=(p,t)=>{$('#spBar').style.width=Math.max(4,Math.min(100,p))+'%';if(t!=null)$('#spTxt').textContent=t};
window.authAppReady=()=>{if(sceneReady)return;sceneReady=true;$('#spBar').style.width='100%';maybeOpen()};
if(window.__appReadyEarly)window.authAppReady();   /* 앱이 먼저 끝났다면 window.__appReadyEarly=true 로 표시해 둘 것 */
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
document.querySelectorAll('#langs button').forEach(b=>b.addEventListener('click',syncLang));   /* 앱 본문 언어 버튼(#langs)이 있으면 동기화 */
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
const who=document.createElement('div');who.id='who';who.hidden=true;(document.querySelector('[data-who-host]')||document.body).appendChild(who);   /* 헤더 패널에 data-who-host 속성 */
function renderWho(){if(!me){who.hidden=true;return}who.hidden=false;const pend=(admData&&admData.members||[]).filter(m=>m.status==='pending').length;
  who.innerHTML=`<span>👤 <b></b>${me.role==='admin'?' · '+T('adSuper'):''}</span><button id="wPw">${T('auChangePw')}</button><button id="wOut">${T('auLogout')}</button>${me.superAdmin?`<button id="wAdmin">👥 ${T('adTitle')}${pend?`<span class="pend">${pend}</span>`:''}</button>`:''}`;
  who.querySelector('b').textContent=me.name;$('#wOut').onclick=logout;$('#wPw').onclick=()=>{au.hidden=false;view('change')};if(me.superAdmin)$('#wAdmin').onclick=openAdm;if(window.onAuthLayout)window.onAuthLayout()}
function logout(){api('auth?a=logout',{body:{}});token=null;me=null;try{localStorage.removeItem(TK)}catch(e){}closeAdm();renderWho();sp.classList.remove('out');au.hidden=false;view('login')}
/* heartbeat / blocking */
async function beat(){if(!API)return;const r=await api('track',{body:{p:location.pathname,b:BUILD_ID}});if(r.success&&r.data.blocked){$('#blockedScr').hidden=false;au.hidden=true}
  if(r.success&&r.data.release&&r.data.release.version>BUILD_ID)updateNotice(r.data.release)}
let updTimer=null;function updateNotice(rel){if(updTimer)return;try{if(sessionStorage.getItem('app_upd')===rel.version)return}catch(e){}   /* 같은 버전으로 이미 새로고침했는데도 구버전이면(캐시) 반복 새로고침 방지 */
  let n=10;const el=document.createElement('div');el.id='updToast';document.body.appendChild(el);
  const go=()=>{try{sessionStorage.setItem('app_upd',rel.version)}catch(e){}const u=new URL(location.href);u.searchParams.set('_v',rel.version);location.replace(u.toString())};
  const draw=()=>{el.innerHTML=`<b>⟳ ${T('upTitle')}</b><span>${rel.note?esc(rel.note)+' · ':''}${T('upCount',{n})}</span><button>${T('upNow')}</button>`;el.querySelector('button').onclick=go};
  draw();updTimer=setInterval(()=>{n--;if(n<=0){clearInterval(updTimer);go()}else draw()},1000)}
document.addEventListener('visibilitychange',()=>{if(!document.hidden)beat()});
try{const u=new URL(location.href);if(u.searchParams.has('_v')){u.searchParams.delete('_v');history.replaceState(null,'',u.pathname+(u.search||'')+u.hash)}}catch(e){}
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
  tb[0].textContent=`${T('adMembers')}${d?` (${d.members.length})`:''}${pend?` · ${T('adPendingN',{n:pend})}`:''}`;tb[1].textContent=`${T('adVisitors')}${d?` · ${T('adOnlineN',{n:onl})}`:''}`;tb[2].textContent=`⟳ ${T('adUpdate')}`;tb[3].textContent=`${T('adBlocked')}${d?` (${d.blocked.length})`:''}`;
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
  else if(admTab==='update'){const rel=d.release;const bv=b=>b?b.replace(/^(\d{4})(\d\d)(\d\d)-(\d\d)(\d\d)(\d\d)$/,'$1-$2-$3 $4:$5:$6 UTC'):'—';
    el.innerHTML=`<div class="kpis"><div class="kpi"><b style="font-size:13px">${bv(BUILD_ID)}</b>${T('upMine')}</div><div class="kpi"><b style="font-size:13px" id="upLatest">…</b>${T('upServer')}</div><div class="kpi"><b style="font-size:13px">${rel?bv(rel.version):'—'}</b>${T('upPushed')}${rel?' · '+fmt(rel.at):''}</div><div class="kpi"><b>${d.visitors.filter(v=>v.online).length}</b>${T('adOnline')}</div></div>
    <p class="note" style="margin-top:0">${T('upHow')}</p><div id="upWarn" class="note" style="color:#ffd15a"></div>
    <textarea id="upNote" maxlength="120" placeholder="${T('upNotePh')}" style="width:100%;box-sizing:border-box;min-height:54px;margin-top:8px;font:500 12.5px var(--ui);color:var(--ink);background:rgba(255,255,255,.05);border:1px solid var(--glass-line);border-radius:7px;padding:8px"></textarea>
    <div class="acts" style="margin-top:8px"><button class="ok" id="upPush" style="padding:7px 14px;font-size:12.5px">⟳ ${T('upPush')}</button></div>`;
    fetch('/?v='+Date.now(),{cache:'no-store'}).then(r=>r.text()).then(h=>{const m=h.match(/BUILD_ID = "([0-9-]+)"/);const lv=m?m[1]:null;$('#upLatest').textContent=bv(lv);
      if(lv&&lv>BUILD_ID)$('#upWarn').textContent=T('upStale');}).catch(()=>{});
    $('#upPush').onclick=async()=>{if(!confirm(T('upConfirm')))return;const r=await api('admin?a=release',{body:{version:BUILD_ID,note:$('#upNote').value.trim()}});if(!r.success){alert(errMsg(r.error));return}alert(T('upDone'));admLoad()}}
  else{el.innerHTML=`<div class="kpis"><div class="kpi"><b>${d.blocked.length}</b>${T('adBlocked')}</div></div>
    <div style="display:flex;gap:6px;margin:4px 0 10px"><input id="admIp" placeholder="IP" style="font:500 12.5px var(--mono);color:var(--ink);background:rgba(255,255,255,.05);border:1px solid var(--glass-line);border-radius:6px;padding:6px 8px;width:200px"><input id="admRs" data-ph="adReason" placeholder="${T('adReason')}" style="flex:1;font:500 12.5px var(--ui);color:var(--ink);background:rgba(255,255,255,.05);border:1px solid var(--glass-line);border-radius:6px;padding:6px 8px"><div class="acts"><button class="no" id="admAddIp">${T('acIpBlock')}</button></div></div>
    <table><thead><tr><th>IP</th><th>${T('adReason')}</th><th>${T('adBlockedAt')}</th><th>${T('adBy')}</th><th>${T('adActions')}</th></tr></thead><tbody>
    ${d.blocked.map(b=>`<tr><td>${esc(b.ip)}</td><td class="s">${esc(b.reason||'—')}</td><td class="s">${fmt(b.at)}</td><td class="s">${esc(b.by||'')}</td><td><div class="acts"><button class="ok" data-ip="${esc(b.ip)}">${T('acIpUnblock')}</button></div></td></tr>`).join('')||`<tr><td colspan="5" class="s">${T('adNone')}</td></tr>`}
    </tbody></table>`;
    $('#admAddIp').onclick=()=>{const ip=$('#admIp').value.trim();if(ip)act('ip-block',{ip,reason:$('#admRs').value.trim()})};
    el.querySelectorAll('[data-ip]').forEach(b=>b.onclick=()=>act('ip-unblock',{ip:b.dataset.ip}))}}
})();
