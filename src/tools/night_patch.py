#!/usr/bin/env python3
"""v2 패치: (1) 효과음(WebAudio 합성: 물소리·모터음·버블, 시네마틱 시 근접음) (2) 야간 모드 UVA 강화
 (3) 시간대별 데크 그림자(태양 방향 투영) + 실제 그늘(또는 야간)에서만 UVA 100% (4) 게이트별 UVA 가동시간·ROS 발생 지수 집계 보고서 + 서버 저장 + PDF 출력"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
FN = r"""
/* ---- 태양·그림자 ---- */
let SUN_EL=.8,SUN_NIGHT=0;
function deckShadow(p){if(SUN_EL<=0.04)return 0;const d=skyU.uSun.value;const k=Math.min(1.25/Math.max(d.y,.08),14);const q=[p[0]+d.x*k,p[1]+d.z*k];   /* 수면점→태양 방향으로 데크 높이만큼 올려 데크 하면과 교차? */
  for(const B of BANDS){const dx=q[0]-B.a[0],dz=q[1]-B.a[1];const s=dx*B.ux+dz*B.uz;if(s<0||s>B.L)continue;if(Math.abs(-dx*B.uz+dz*B.ux)<B.hw)return 1}return 0}
/* ---- 효과음(WebAudio 합성, 저작권 음원 미사용) ---- */
const SFX={ctx:null,on:true,ready:false,t:0};
function sfxInit(){if(SFX.ctx||!SFX.on)return;try{const C=new (window.AudioContext||window.webkitAudioContext)();SFX.ctx=C;const M=C.createGain();M.gain.value=0;M.connect(C.destination);SFX.master=M;
  const len=C.sampleRate*3,buf=C.createBuffer(1,len,C.sampleRate),d=buf.getChannelData(0);let last=0;for(let i=0;i<len;i++){const w=Math.random()*2-1;last=(last+.02*w)/1.02;d[i]=last*3.2}   /* 브라운 노이즈 = 물결 */
  const src=C.createBufferSource();src.buffer=buf;src.loop=true;const lp=C.createBiquadFilter();lp.type='lowpass';lp.frequency.value=520;const wg=C.createGain();wg.gain.value=.0;src.connect(lp);lp.connect(wg);wg.connect(M);src.start();SFX.water=wg;
  const lfo=C.createOscillator();lfo.frequency.value=.18;const lg=C.createGain();lg.gain.value=180;lfo.connect(lg);lg.connect(lp.frequency);lfo.start();   /* 물결 출렁임 */
  const src2=C.createBufferSource();src2.buffer=buf;src2.loop=true;src2.playbackRate.value=2.7;const hp=C.createBiquadFilter();hp.type='bandpass';hp.frequency.value=2600;hp.Q.value=.8;const bg=C.createGain();bg.gain.value=0;src2.connect(hp);hp.connect(bg);bg.connect(M);src2.start();SFX.fizz=bg;   /* 버블 */
  const o1=C.createOscillator();o1.type='sawtooth';o1.frequency.value=58;const o2=C.createOscillator();o2.type='triangle';o2.frequency.value=116.5;const mlp=C.createBiquadFilter();mlp.type='lowpass';mlp.frequency.value=260;
  const mg=C.createGain();mg.gain.value=0;const trem=C.createOscillator();trem.frequency.value=7;const tg=C.createGain();tg.gain.value=.25;const tb=C.createGain();tb.gain.value=.75;trem.connect(tg);tg.connect(tb.gain);
  o1.connect(mlp);o2.connect(mlp);mlp.connect(tb);tb.connect(mg);mg.connect(M);o1.start();o2.start();trem.start();SFX.motor=mg;SFX.mo=[o1,o2];SFX.ready=true}catch(e){SFX.on=false}}
['pointerdown','keydown'].forEach(ev=>addEventListener(ev,()=>{if(BOAT.on&&SFX.on){sfxInit();if(SFX.ctx&&SFX.ctx.state==='suspended')SFX.ctx.resume()}}));
function sfxUpdate(dt){if(!SFX.ready)return;SFX.t+=dt;if(SFX.t<.1)return;SFX.t=0;const C=SFX.ctx,now=C.currentTime,on=BOAT.on&&SFX.on&&!document.hidden,cine=!!MS.cut;
  const sp=Math.abs(BOAT.v)/BOAT.base,run=MS.ph===3;const set=(g,v)=>g.gain.setTargetAtTime(v,now,.25);
  set(SFX.master,on?1:0);set(SFX.water,cine?.16:.06);set(SFX.fizz,run?(cine?.05:.018)*(.4+.6*sp):0);set(SFX.motor,run?(cine?.075:.03)*(.35+.65*sp):0);
  SFX.mo[0].frequency.setTargetAtTime(52+16*sp,now,.3);SFX.mo[1].frequency.setTargetAtTime(104+32*sp,now,.3)}
/* ---- 운항 집계 · 보고서 ---- */
function stReset(){MS.st={t:0,uvaT:0,ros:0,start:Date.now()};(MS.gates||[]).forEach((g,i)=>{g.no=i+1;g.ros=0;g.uvaT=0;g.passes=0;g.last=null})}
function llOf(p){return [GEO.lat-p[1]/111320,GEO.lon+p[0]/(111320*Math.cos(GEO.lat*Math.PI/180))]}
function buildReport(){const st=MS.st||{t:0,uvaT:0,ros:0,start:Date.now()};return {v:1,build:typeof BUILD_ID!=='undefined'?BUILD_ID:'',at:Date.now(),start:st.start,simSec:Math.round(st.t),uvaSec:Math.round(st.uvaT),ros:st.ros,
  clean:BOAT.pct,pass:MS.pass,hour:+($('#tod')?$('#tod').value:14),night:+SUN_NIGHT.toFixed(2),
  gates:(MS.gates||[]).map(g=>({no:g.no,ll:llOf(g.G).map(v=>+v.toFixed(6)),clr:+g.clr.toFixed(2),passes:g.passes,uvaSec:+(g.uvaT||0).toFixed(1),ros:g.ros||0,last:g.last})),low:(MS.lowGates||[]).length}}
"""
def patch(path, html):
    p = ROOT/path; t = p.read_text()
    def rep(a, b):
        nonlocal t
        assert t.count(a) == 1, (path, a[:70], t.count(a)); t = t.replace(a, b)
    rep("let DECK_PILES=[],DECK_WOOD=[],BANDS=[];", "let DECK_PILES=[],DECK_WOOD=[],BANDS=[];" + FN)
    rep("function buildBoat(){", "function buildBoat(){PUR.u.uNight={value:0};")
    rep("const shade=run&&!!bandInfo([BOAT.pos.x,BOAT.pos.y],0.6);MS.uva=(MS.uva||.6)+((run?(shade?1:.6):0)-(MS.uva||.6))*Math.min(1,dt*6);",
        "const shadeF=run?Math.max(deckShadow([BOAT.pos.x,BOAT.pos.y]),SUN_NIGHT):0;MS.shadeF=shadeF;MS.uva=(MS.uva||.6)+((run?.6+.4*shadeF:0)-(MS.uva||.6))*Math.min(1,dt*6);   /* 실제 데크 그림자(태양 방향) 또는 야간에만 UVA 100% */")
    rep("const boost=clamp((MS.uva-.6)/.4,0,1);if(BOAT.uvGlow){BOAT.uvGlow.material.opacity=boost*(.8+.2*Math.sin(BOAT.t*9));BOAT.uvLight.intensity=boost*4*(.85+.15*Math.sin(BOAT.t*7))}",
        "const boost=clamp((MS.uva-.6)/.4,0,1),glv=Math.min(1.3,boost+(run?SUN_NIGHT*.6:0));if(BOAT.uvGlow){BOAT.uvGlow.material.opacity=Math.min(1,glv*(.8+.2*Math.sin(BOAT.t*9)));BOAT.uvGlow.scale.setScalar(1+.4*SUN_NIGHT);BOAT.uvLight.intensity=glv*4*(1+2*SUN_NIGHT)*(.85+.15*Math.sin(BOAT.t*7))}PUR.u.uNight.value=SUN_NIGHT;   /* 야간: UVA 빛 강화 */\n"
        "  if(run){if(!MS.st)stReset();MS.st.t+=sdt;if(MS.uva>=.9){MS.st.uvaT+=sdt;if(MS.inGate)MS.inGate.g.uvaT=(MS.inGate.g.uvaT||0)+sdt}if(MS.inGate)MS.inGate.g.last=Date.now()}")
    rep("  for(let k=0;k<Math.round(3*em*(1+2*boost));k++){",
        "  const nRos=Math.round(3*em*(1+2*boost));if(run&&MS.st){MS.st.ros+=nRos;if(MS.inGate)MS.inGate.g.ros=(MS.inGate.g.ros||0)+nRos}   /* ROS 발생 지수 집계 */\n  for(let k=0;k<nRos;k++){")
    rep("if(vK>2.5){a=soft;col=mix(vec3(.72,.95,1.),vec3(.8,.5,1.),step(3.5,vK));col=mix(col,vec3(1.),smoothstep(.18,0.,r)*.7);}",
        "if(vK>2.5){a=soft;col=mix(vec3(.72,.95,1.),vec3(.8,.5,1.),step(3.5,vK));col=mix(col,vec3(1.),smoothstep(.18,0.,r)*.7);a*=1.+uNight*1.3;}")
    rep("fragmentShader:pFS+`uniform sampler2D uAtlas;varying float vA,vK;void main(){", "fragmentShader:pFS+`uniform sampler2D uAtlas;uniform float uNight;varying float vA,vK;void main(){")
    rep("  {const r=$('#rc');if(r){const sh=BOAT.on&&MS.ph===3;if(r.hidden===sh)r.hidden=!sh}}",
        "  {const r=$('#rc');if(r){const sh=BOAT.on&&MS.ph===3;if(r.hidden===sh)r.hidden=!sh}}\n  sfxUpdate(dt);\n"
        "  if(MS.shadowM){const d=skyU.uSun.value,k=Math.min(1.25/Math.max(d.y,.08),14),op=SUN_EL>.04?.3*(1-SUN_NIGHT):0;MS.shadowM.forEach(m=>{m.position.set(-d.x*k,0,-d.z*k);m.material.opacity=op;m.visible=op>.01})}   /* 시간대별 데크 그림자 */")
    rep("function missionHide(){MS.man=null;", "function missionHide(){MS.man=null;if(SFX.ready)SFX.master.gain.setTargetAtTime(0,SFX.ctx.currentTime,.2);")
    rep("function missionStart(){if(!MS.G)return;MS.man=null;MS.inGate=null;(MS.gates||[]).forEach(g=>{g.passes=0;g.side=0});",
        "function missionStart(){if(!MS.G)return;MS.man=null;MS.inGate=null;(MS.gates||[]).forEach(g=>{g.passes=0;g.side=0});stReset();")
    rep("  deckSegs.forEach(s=>{const g=new THREE.BufferGeometry();",
        "  MS.shadowM=BANDS.map(B=>{const nx=-B.uz*B.hw,nz=B.ux*B.hw,a=B.a,b=B.b,y=-0.455;const g=new THREE.BufferGeometry();\n"
        "    g.setAttribute('position',new THREE.Float32BufferAttribute([a[0]+nx,y,a[1]+nz,a[0]-nx,y,a[1]-nz,b[0]+nx,y,b[1]+nz,a[0]-nx,y,a[1]-nz,b[0]-nx,y,b[1]-nz,b[0]+nx,y,b[1]+nz],3));\n"
        "    const m=new THREE.Mesh(g,new THREE.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.3,depthWrite:false,side:THREE.DoubleSide}));m.renderOrder=4;G.add(m);return m});\n"
        "  deckSegs.forEach(s=>{const g=new THREE.BufferGeometry();")
    if html:
        rep("  skyU.uSun.value.copy(dir);", "  skyU.uSun.value.copy(dir);SUN_EL=el;SUN_NIGHT=night;")
        rep('<button id="bCine"', '<button id="bSnd" aria-pressed="true" data-i18n-title="sndT" title="효과음 켜기/끄기">🔊</button><button id="bRep" data-i18n-title="repT" title="게이트 운항 보고서">📊</button><button id="bCine"')
        rep("$('#bCine').addEventListener('click'",
            "$('#bSnd').addEventListener('click',()=>{SFX.on=!SFX.on;$('#bSnd').textContent=SFX.on?'🔊':'🔇';$('#bSnd').setAttribute('aria-pressed',String(SFX.on));if(SFX.on){sfxInit();if(SFX.ctx)SFX.ctx.resume()}else if(SFX.ready)SFX.master.gain.setTargetAtTime(0,SFX.ctx.currentTime,.1)});\n"
            "$('#bRep').addEventListener('click',()=>openReport());\n"
            "$('#bCine').addEventListener('click'")
        rep("#purHud .brow #bCine{margin-left:auto;", "#purHud .brow #bSnd{margin-left:auto;font-family:var(--ui)}#purHud .brow #bRep,#purHud .brow #bCine{")
        rep('<div id="credit"', REP_HTML + '<div id="credit"')
        rep("#boatBar{background:", REP_CSS + "#boatBar{background:")
        rep("window.__dt={scene,", REP_JS + "\nwindow.__dt={scene,")
        rep(" hudFold:{", REP_I18N + " hudFold:{")
        rep(" uvaBoost:{ko:'UVA 365 nm · 출력 {p}% ▲ 데크 밑 그늘 보강 (녹조 우세 구역)',en:'UVA 365 nm · output {p}% ▲ shade boost under the deck (algae-prone)',ja:'UVA 365 nm・出力 {p}% ▲ デッキ下の日陰で増強（アオコ多発域）'},",
            " uvaBoost:{ko:'UVA 365 nm · 출력 {p}% ▲ 그늘·야간 보강 (데크 그림자 = 태양 위치 기준)',en:'UVA 365 nm · output {p}% ▲ shade/night boost (deck shadow from sun position)',ja:'UVA 365 nm・出力 {p}% ▲ 日陰・夜間増強（デッキの影＝太陽位置基準）'},")
    p.write_text(t)

REP_HTML = r"""<div id="rep" hidden role="dialog" aria-modal="true"><div class="box">
  <div class="hd"><b data-i18n="repTitle">게이트 운항 보고서</b><span class="sm" data-i18n="repSub">UVA 가동시간 · ROS 발생 지수 · 기둥 주변 세정 (시뮬레이션 집계)</span>
  <button id="repSave" data-i18n="repSave">서버에 저장</button><button id="repPdf" data-i18n="repPdf">PDF 출력</button><button id="repX" data-i18n="auClose">닫기</button></div>
  <div class="bd" id="repBody"></div></div></div>
"""
REP_CSS = r"""#rep{position:fixed;inset:0;z-index:56;display:grid;place-items:center;background:rgba(2,8,10,.55);padding:12px}#rep[hidden]{display:none!important}
#rep .box{width:min(980px,100%);max-height:88vh;display:flex;flex-direction:column;background:rgba(8,20,24,.96);border:1px solid var(--glass-line);border-radius:12px;overflow:hidden}
#rep .hd{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:12px 16px;border-bottom:1px solid var(--glass-line)}#rep .hd b{font:700 15px var(--ui)}#rep .hd .sm{font-size:11px;color:var(--ink-3);flex:1}
#rep .hd button{font:600 12px var(--ui);color:var(--ink-2);background:rgba(255,255,255,.05);border:1px solid var(--glass-line);border-radius:6px;padding:5px 10px;cursor:pointer}#rep #repPdf{color:#04222a;background:#8fe6ff;border-color:#8fe6ff}
#rep .bd{overflow:auto;padding:12px 16px 16px}#rep .kp{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin-bottom:12px}
#rep .kp div{background:rgba(255,255,255,.04);border:1px solid var(--glass-line);border-radius:8px;padding:8px 10px;font-size:11px;color:var(--ink-3)}#rep .kp b{display:block;font:700 18px var(--mono);color:var(--ink)}
#rep table{width:100%;border-collapse:collapse;font-size:12px}#rep th{text-align:left;color:var(--ink-3);font-weight:600;font-size:11px;padding:6px;border-bottom:1px solid var(--glass-line)}#rep td{padding:6px;border-bottom:1px solid rgba(170,215,220,.08);font-variant-numeric:tabular-nums}
#rep .bar{height:7px;border-radius:4px;background:linear-gradient(90deg,#8fe6ff,#b48cff)}#rep .note{font-size:11px;color:var(--ink-3);margin-top:10px;line-height:1.5}#rep h4{font:600 12.5px var(--ui);margin:14px 0 6px}
"""
REP_JS = r"""
/* ================= 게이트 운항 보고서 (화면 · 서버 저장 · PDF) ================= */
function repHTML(R,forPrint){const esc2=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));const mx=Math.max(1,...R.gates.map(g=>g.ros));
  const dt=ms=>ms?new Date(ms).toLocaleString(LANG==='ko'?'ko-KR':LANG==='ja'?'ja-JP':'en-US'):'—';const hm=s=>s>=60?`${Math.floor(s/60)}${T('rpMin')} ${s%60}${T('rpSec')}`:`${s}${T('rpSec')}`;
  const kp=[[hm(R.simSec),T('rpRun')],[hm(R.uvaSec),T('rpUva')],[R.ros.toLocaleString(),T('rpRos')],[R.gates.reduce((a,g)=>a+g.passes,0),T('rpPass')],[R.clean+'%',T('rpClean')],[`${R.gates.length}${R.low?` (+${R.low} ${T('rpLow')})`:''}`,T('rpGates')]];
  return `${forPrint?`<h1>${T('repTitle')}</h1><div class="meta">${T('spTitle')} · NHI PhotoNano · ${dt(R.at)} · build ${esc2(R.build)}</div>`:''}
  <div class="kp">${kp.map(k=>`<div><b>${esc2(k[0])}</b>${esc2(k[1])}</div>`).join('')}</div>
  <h4>${T('rpTbl')}</h4><table><thead><tr><th>#</th><th>${T('rpLL')}</th><th>${T('rpClr')}</th><th>${T('rpPasses')}</th><th>${T('rpUvaT')}</th><th>${T('rpRosI')}</th><th style="width:22%"></th><th>${T('rpLast')}</th></tr></thead><tbody>
  ${R.gates.map(g=>`<tr><td>G${g.no}</td><td>${g.ll[0].toFixed(5)}, ${g.ll[1].toFixed(5)}</td><td>${g.clr.toFixed(2)} m</td><td>${g.passes}</td><td>${g.uvaSec.toFixed(1)} s</td><td>${g.ros.toLocaleString()}</td><td><div class="bar" style="width:${Math.round(g.ros/mx*100)}%"></div></td><td>${g.last?dt(g.last):'—'}</td></tr>`).join('')}</tbody></table>
  <p class="note">${T('rpNote',{h:R.hour,n:Math.round(R.night*100)})}</p>`}
function openReport(R,id){const r=R||buildReport();$('#repBody').innerHTML=repHTML(r,false)+`<h4>${T('rpSaved')}</h4><div id="repList" class="note">…</div>`;$('#rep').hidden=false;$('#rep').dataset.cur=JSON.stringify(r);loadReports()}
async function loadReports(){const el=$('#repList');if(!el)return;if(!location.protocol.startsWith('http')){el.textContent=T('rpOffline');return}let tok=null;try{tok=localStorage.getItem('sd_token')}catch(e){}
  try{const r=await (await fetch('/api/report?a=list',{headers:tok?{Authorization:'Bearer '+tok}:{},cache:'no-store'})).json();if(!r.success){el.textContent=T('rpLogin');return}
    el.innerHTML=r.data.length?r.data.map(x=>`<a href="#" data-id="${x.id}" style="color:#9fd8ff">${new Date(x.at).toLocaleString()} · ${String(x.by||'').replace(/[<>&"]/g,'')} · ROS ${(+x.ros||0).toLocaleString()}</a>`).join('<br>'):T('rpNone');
    el.querySelectorAll('a').forEach(a=>a.onclick=async e=>{e.preventDefault();const g=await (await fetch('/api/report?a=get&id='+a.dataset.id,{headers:tok?{Authorization:'Bearer '+tok}:{}})).json();if(g.success)openReport(g.data)})}catch(e){el.textContent=T('er_NETWORK')}}
$('#repX').onclick=()=>{$('#rep').hidden=true};
$('#repSave').onclick=async()=>{let tok=null;try{tok=localStorage.getItem('sd_token')}catch(e){}const R=JSON.parse($('#rep').dataset.cur||'null');if(!R)return;
  const r=await (await fetch('/api/report?a=save',{method:'POST',headers:{'Content-Type':'application/json',...(tok?{Authorization:'Bearer '+tok}:{})},body:JSON.stringify({report:R})}).catch(()=>({json:()=>({success:false})}))).json();
  alert(r.success?T('rpSavedOk'):T('rpLogin'));loadReports()};
$('#repPdf').onclick=()=>{const R=JSON.parse($('#rep').dataset.cur||'null');if(!R)return;const w=window.open('','_blank');if(!w){alert(T('rpPopup'));return}
  w.document.write(`<!doctype html><html lang="${LANG}"><head><meta charset="utf-8"><title>${T('repTitle')} ${new Date(R.at).toISOString().slice(0,10)}</title><style>
  @page{size:A4;margin:14mm}body{font-family:-apple-system,'Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR',sans-serif;color:#111;font-size:11.5px}
  h1{font-size:19px;margin:0 0 4px}.meta{color:#555;font-size:11px;margin-bottom:12px}.kp{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:10px}
  .kp div{border:1px solid #cfd8dc;border-radius:6px;padding:6px 8px;color:#555;font-size:10.5px}.kp b{display:block;font-size:16px;color:#0b3d4a}h4{font-size:12.5px;margin:12px 0 6px}
  table{width:100%;border-collapse:collapse}th,td{border-bottom:1px solid #e0e6e8;padding:5px;text-align:left}th{background:#f1f6f7;font-size:10.5px}
  .bar{height:7px;border-radius:4px;background:linear-gradient(90deg,#3ab7d6,#8b5cf6)}.note{color:#555;font-size:10.5px;margin-top:10px}
  .foot{margin-top:18px;color:#777;font-size:9.5px;border-top:1px solid #ddd;padding-top:6px}</style></head><body>${repHTML(R,true)}
  <div class="foot">© 2026 주식회사 나노하이드로인 (NanoHydroIn Co., Ltd.) · park.nanohydroin.com</div><script>onload=()=>setTimeout(()=>print(),300)<\/script></body></html>`);w.document.close()};
"""
REP_I18N = r""" sndT:{ko:'효과음 켜기/끄기',en:'Sound on/off',ja:'効果音オン/オフ'},repT:{ko:'게이트 운항 보고서',en:'Gate operation report',ja:'ゲート運航レポート'},
 repTitle:{ko:'게이트 운항 보고서',en:'Gate Operation Report',ja:'ゲート運航レポート'},repSub:{ko:'UVA 가동시간 · ROS 발생 지수 · 기둥 주변 세정 (시뮬레이션 집계)',en:'UVA run time · ROS index · pile-area cleaning (simulated)',ja:'UVA稼働時間・ROS発生指数・橋脚周辺洗浄（シミュレーション集計）'},
 repSave:{ko:'서버에 저장',en:'Save to server',ja:'サーバーに保存'},repPdf:{ko:'PDF 출력',en:'Export PDF',ja:'PDF出力'},
 rpRun:{ko:'운항 시간(시뮬)',en:'Run time (sim)',ja:'運航時間（シミュ）'},rpUva:{ko:'UVA 100% 가동',en:'UVA 100% time',ja:'UVA 100%稼働'},rpRos:{ko:'ROS 발생 지수',en:'ROS index',ja:'ROS発生指数'},rpPass:{ko:'게이트 통과',en:'Gate passes',ja:'ゲート通過'},
 rpClean:{ko:'녹조 제거율',en:'Algae removed',ja:'アオコ除去率'},rpGates:{ko:'사용 게이트',en:'Gates in use',ja:'使用ゲート'},rpLow:{ko:'높이 제한',en:'low clearance',ja:'高さ制限'},
 rpTbl:{ko:'게이트별 집계',en:'Per-gate summary',ja:'ゲート別集計'},rpLL:{ko:'위치(위도, 경도)',en:'Location (lat, lon)',ja:'位置（緯度・経度）'},rpClr:{ko:'마스트 여유고',en:'Mast clearance',ja:'マスト余裕高'},rpPasses:{ko:'통과',en:'Passes',ja:'通過'},
 rpUvaT:{ko:'UVA 가동',en:'UVA time',ja:'UVA稼働'},rpRosI:{ko:'ROS 지수',en:'ROS index',ja:'ROS指数'},rpLast:{ko:'마지막 통과',en:'Last pass',ja:'最終通過'},rpMin:{ko:'분',en:'m',ja:'分'},rpSec:{ko:'초',en:'s',ja:'秒'},
 rpNote:{ko:'ROS 발생 지수는 화면에 생성된 광촉매 활성산소(·OH, O₂⁻) 입자 수를 합산한 상대 지표이며 실측 농도가 아닙니다. UVA는 평시 60%, 데크 그림자(태양 위치 {h}시 기준) 또는 야간(야간도 {n}%)에 100%로 가동합니다. 시뮬레이션 데이터 · 실측 연동 전.',en:'The ROS index sums simulated photocatalytic ROS (·OH, O₂⁻) particles — a relative indicator, not a measured concentration. UVA runs at 60% normally and 100% in deck shadow (sun at {h}:00) or at night (night level {n}%). Simulated data, not yet linked to field sensors.',ja:'ROS発生指数は画面上で生成した光触媒活性酸素（·OH, O₂⁻）粒子数を合算した相対指標であり、実測濃度ではありません。UVAは平常60%、デッキの影（太陽位置 {h}時基準）または夜間（夜間度 {n}%）に100%で稼働します。シミュレーションデータ・実測連動前。'},
 rpSaved:{ko:'저장된 보고서',en:'Saved reports',ja:'保存済みレポート'},rpNone:{ko:'아직 저장된 보고서가 없습니다.',en:'No saved reports yet.',ja:'保存されたレポートはまだありません。'},rpLogin:{ko:'로그인한 회원만 서버에 저장·조회할 수 있습니다.',en:'Sign in to save or view server reports.',ja:'ログインした会員のみサーバー保存・閲覧できます。'},
 rpOffline:{ko:'오프라인 실행에서는 서버 저장을 쓸 수 없습니다(PDF 출력은 가능).',en:'Server save is unavailable offline (PDF export works).',ja:'オフライン実行ではサーバー保存は使えません（PDF出力は可能）。'},
 rpSavedOk:{ko:'보고서를 서버에 저장했습니다.',en:'Report saved to the server.',ja:'レポートをサーバーに保存しました。'},rpPopup:{ko:'팝업이 차단되었습니다. 이 사이트의 팝업을 허용해 주세요.',en:'Pop-up blocked — please allow pop-ups for this site.',ja:'ポップアップがブロックされました。このサイトのポップアップを許可してください。'},
"""
patch('src/template_v2.html', True); patch('src/tools/boat.js', False); print('night patched')
