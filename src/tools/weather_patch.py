#!/usr/bin/env python3
"""v2 패치: OpenWeather 실시간 날씨(현재·오늘·주간 8일) 패널 + 기상 연출(비=빗줄기·수면 파문·빗소리, 뇌우=번개, 눈=눈송이, 안개/흐림=대기 감쇠).
   키는 서버(/api/weather, 환경변수 OPENWEATHER_API_KEY)에만 둔다. 데모용 수동 날씨 선택 포함. 3개 국어."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
p = ROOT/'src/template_v2.html'; t = p.read_text()
def rep(a, b):
    global t
    assert t.count(a) == 1, (a[:70], t.count(a)); t = t.replace(a, b)

rep('  <aside id="info" class="panel" aria-live="polite"></aside>',
    '''  <section id="wx" class="panel" aria-label="날씨" data-i18n-aria="wxTitle">
    <div class="wxh"><span class="sec" data-i18n="wxTitle">날씨 · 부천 상동</span>
      <select id="wxMode" aria-label="날씨 연출" data-i18n-aria="wxModeT"><option value="auto" data-i18n="wxAuto">실시간</option><option value="clear" data-i18n="wxClear">맑음</option><option value="clouds" data-i18n="wxClouds">흐림</option><option value="rain" data-i18n="wxRain">비</option><option value="storm" data-i18n="wxStorm">뇌우</option><option value="snow" data-i18n="wxSnow">눈</option><option value="fog" data-i18n="wxFog">안개</option></select>
      <button id="wxSnd" aria-pressed="true" data-i18n-title="wxSndT" title="빗소리·천둥 켜기/끄기">🔊</button><button id="wxFold" aria-expanded="true" data-i18n-title="hudFold" title="패널 접기/펼치기">▾</button></div>
    <div id="wxNow"><span class="wxi">⏳</span><div><b>—</b><small data-i18n="wxLoading">날씨 불러오는 중…</small></div></div>
    <div id="wxBody"><div id="wxToday"></div><div id="wxDays"></div><div id="wxSrc"></div></div>
  </section>
  <aside id="info" class="panel" aria-live="polite"></aside>''')

rep('#tbar{padding:10px 14px;margin-top:auto}',
    '''#wx{padding:9px 12px 8px;pointer-events:auto}
#wx .wxh{display:flex;align-items:center;gap:5px}#wx .wxh .sec{margin:0;flex:1}
#wx select,#wx .wxh button{font:500 10.5px var(--ui);color:var(--ink-2);background:rgba(255,255,255,.05);border:1px solid var(--glass-line);border-radius:5px;padding:2px 5px;cursor:pointer}
#wx select option{color:#111}#wx #wxSnd[aria-pressed="false"]{opacity:.45}
#wxNow{display:flex;align-items:center;gap:10px;margin-top:6px}#wxNow .wxi{font-size:30px;line-height:1;filter:drop-shadow(0 2px 4px rgba(0,0,0,.4))}
#wxNow b{font:600 22px var(--mono);color:var(--ink);font-variant-numeric:tabular-nums}#wxNow small{display:block;font-size:11.5px;color:var(--ink-2);margin-top:1px}
#wxNow .man{display:inline-block;margin-left:6px;font:600 9.5px var(--mono);color:#ffd15a;border:1px solid rgba(255,209,90,.45);border-radius:3px;padding:0 4px}
#wxToday{display:grid;grid-template-columns:repeat(3,1fr);gap:3px 8px;margin-top:7px;padding-top:7px;border-top:1px solid var(--glass-line);font-size:10.5px;color:var(--ink-3)}
#wxToday b{display:block;font:600 11px var(--mono);color:var(--ink);font-variant-numeric:tabular-nums}
#wxDays{display:grid;grid-template-columns:repeat(8,1fr);gap:2px;margin-top:7px;padding-top:7px;border-top:1px solid var(--glass-line)}
#wxDays div{text-align:center;font-size:10px;color:var(--ink-3);padding:3px 0;border-radius:5px;line-height:1.35}#wxDays div:first-child{background:rgba(143,230,255,.08)}
#wxDays i{display:block;font-style:normal;font-size:15px;margin:1px 0}#wxDays b{display:block;font:600 10.5px var(--mono);color:var(--ink)}#wxDays em{font-style:normal;font-family:var(--mono);color:var(--ink-3)}
#wxDays .pp{display:block;font:500 9px var(--mono);color:#8fd0ff}
#wxSrc{font-size:9.5px;color:var(--ink-3);margin-top:5px}#wxToday:empty,#wxDays:empty,#wxSrc:empty{display:none}
#wx.fold #wxBody{display:none}
#tbar{padding:10px 14px;margin-top:auto}''')
rep('  #info,#tbar{display:none}', '  #info,#tbar{display:none}\n  #wxBody{display:none}#wx{padding:7px 10px}#wxNow .wxi{font-size:22px}#wxNow b{font-size:17px}#wxFold{display:none}')

# 대기·광량: setTime 끝에서 날씨 감쇠 적용
rep('skyU.uSun.value.copy(dir);SUN_EL=el;SUN_NIGHT=night;', 'skyU.uSun.value.copy(dir);SUN_EL=el;SUN_NIGHT=night;CUR_H=h;')
rep("  fountains.forEach(f=>f.m.uniforms.uLight", "  wxAtmos(night);\n  fountains.forEach(f=>f.m.uniforms.uLight")
rep('  updatePurify(dt);updateBoat(dt);', '  updatePurify(dt);updateBoat(dt);updateWeather(dt);')
rep("applyI18n();relabel();render();", "applyI18n();relabel();render();try{wxLang()}catch(e){}")
rep("setMode,nav:{deckOK,", "setMode,WX:()=>WX,wxSet:m=>{$('#wxMode').value=m;wxSetMode(m)},nav:{deckOK,")

JS = r'''
/* ================= 날씨 (OpenWeather · /api/weather 서버 프록시) + 기상 연출 ================= */
let CUR_H=14;
const WX={data:null,err:null,mode:'auto',kind:'clear',k:0,dim:0,fog:0,rainA:0,snowA:0,tgtR:0,tgtS:0,flash:0,nextBolt:4,atmT:0,snd:true,au:null,t:0};
const wxEmoji=(id,icon)=>{const n=icon&&icon.endsWith('n');return id<300?'⛈️':id<400?'🌦️':id===511?'🌨️':id<600?'🌧️':id<700?'❄️':id<800?'🌫️':id===800?(n?'🌙':'☀️'):id===801?(n?'☁️':'🌤️'):id===802?'⛅':'☁️'};
function wxKindOf(c){if(!c)return {kind:'clear',k:0};const id=c.id;
  if(id<300)return {kind:'storm',k:1};
  if(id<400)return {kind:'rain',k:.35};
  if(id<600)return {kind:'rain',k:Math.min(1,.45+(c.rain1h||0)/8+(id>=502&&id<505?.3:0))};
  if(id<700)return {kind:'snow',k:Math.min(1,.5+(c.snow1h||0)/3+(id===602?.3:0))};
  if(id<800)return {kind:'fog',k:id===741?1:.6};
  return {kind:id>=803?'overcast':id===802?'clouds':'clear',k:id>=803?1:id===802?.5:0}}
function wxResolve(){const m=WX.mode;const r=m==='auto'?wxKindOf(WX.data&&WX.data.cur):m==='rain'?{kind:'rain',k:.75}:m==='storm'?{kind:'storm',k:1}:m==='snow'?{kind:'snow',k:.8}:m==='fog'?{kind:'fog',k:1}:m==='clouds'?{kind:'overcast',k:1}:{kind:'clear',k:0};
  WX.kind=r.kind;WX.k=r.k;const K=r.kind;
  WX.tgtR=(K==='rain'||K==='storm')?.35+.65*r.k:0;WX.tgtS=K==='snow'?.4+.6*r.k:0;
  WX.dimT=K==='storm'?1:K==='rain'?.45+.35*r.k:K==='snow'?.5:K==='fog'?.45:K==='overcast'?.4:K==='clouds'?.15:0;
  WX.fogT=K==='fog'?1.6*r.k:K==='snow'?.9:K==='storm'?.9:K==='rain'?.35+.4*r.k:K==='overcast'?.15:0;
  if(WX.dim===undefined)WX.dim=0}
/* setTime() 끝에서 호출: 흐림·강수 시 일사·하늘·안개·노출 감쇠 */
function wxAtmos(night){const d=WX.dim||0,f=WX.fog||0;if(d<=0&&f<=0)return;
  sun.intensity*=1-d*.72;hemi.intensity*=1-d*.25;
  tmpC.setRGB(.42,.45,.5).convertSRGBToLinear();const g=tmpC.clone().multiplyScalar(1-night*.85);
  skyU.uTop.value.lerp(g,Math.min(1,d*1.05));skyU.uHor.value.lerp(g.clone().multiplyScalar(1.3),Math.min(1,d*.9));skyU.uSunCol.value.multiplyScalar(1-d*.9);skyU.uCloud.value.lerp(g.clone().multiplyScalar(1.5),d*.7);
  PUR.aboveFog=new THREE.FogExp2(skyU.uHor.value.clone(),0.00034*(1+f*4.5));if(!PUR.under)scene.fog=PUR.aboveFog;
  renderer.toneMappingExposure*=1-d*.22;
  if(water){water.material.uniforms.sunColor.value.multiplyScalar(1-d*.8);water.material.uniforms.waterColor.value.multiplyScalar(1-d*.25)}}
/* --- 파티클: 카메라를 감싸는 월드 고정 박스(래핑) — 카메라가 움직여도 비·눈이 자연스럽게 이어짐 --- */
const WXU={uCam:{value:new THREE.Vector3()},uTime:{value:0},uA:{value:0},uWind:{value:new THREE.Vector2(1.2,.4)}};
const LD_V='#include <common>\n#include <logdepthbuf_pars_vertex>\n',LD_F='#include <common>\n#include <logdepthbuf_pars_fragment>\n';
function wxField(N,B,isSnow){const P=new Float32Array(N*(isSnow?3:6)),E=new Float32Array(N*(isSnow?1:2)),R=new Float32Array(N*(isSnow?1:2));
  for(let i=0;i<N;i++){const x=Math.random()*B,y=Math.random()*B,z=Math.random()*B,r=Math.random();
    if(isSnow){P.set([x,y,z],i*3);R[i]=r}else{P.set([x,y,z,x,y,z],i*6);E[i*2+1]=1;R[i*2]=R[i*2+1]=r}}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(P,3));g.setAttribute('aR',new THREE.BufferAttribute(R,1));if(!isSnow)g.setAttribute('aE',new THREE.BufferAttribute(E,1));
  g.boundingSphere=new THREE.Sphere(new THREE.Vector3(),1e7);
  const u={...WXU,uB:{value:B},uA:isSnow?{value:0}:WXU.uA};
  const vs=isSnow?
   `${LD_V}uniform vec3 uCam;uniform float uTime,uB;uniform vec2 uWind;attribute float aR;varying float vA;
    void main(){vec3 o=uCam-uB*.5;vec3 b=position;b.y-=uTime*(.9+aR*.5);b.xz-=uWind*uTime*.35;vec3 w=o+mod(b-o,uB);
     w.x+=sin(uTime*.9+aR*40.)*.55;w.z+=cos(uTime*.7+aR*25.)*.45;
     vA=step(-.45,w.y)*(1.-smoothstep(uB*.32,uB*.5,distance(w,uCam)));vec4 mv=viewMatrix*vec4(w,1.);
     gl_PointSize=clamp((1.2+aR*1.6)*170./max(1.,-mv.z),1.5,8.);gl_Position=projectionMatrix*mv;\n#include <logdepthbuf_vertex>\n}`:
   `${LD_V}uniform vec3 uCam;uniform float uTime,uB;uniform vec2 uWind;attribute float aR,aE;varying float vA;
    void main(){float sp=11.+aR*4.;vec3 o=uCam-uB*.5;vec3 b=position;b.y-=uTime*sp;b.xz-=uWind*uTime;vec3 w=o+mod(b-o,uB);
     float L=.55+aR*.5;w.y+=aE*L;w.xz-=uWind/sp*L*aE;
     vA=step(-.45,w.y-aE*L)*(1.-smoothstep(uB*.3,uB*.5,distance(w,uCam)))*(.35+.65*aE);
     gl_Position=projectionMatrix*viewMatrix*vec4(w,1.);\n#include <logdepthbuf_vertex>\n}`;
  const fs=isSnow?`${LD_F}uniform float uA;varying float vA;void main(){\n#include <logdepthbuf_fragment>\nfloat d=length(gl_PointCoord-.5);float a=smoothstep(.5,.15,d)*uA*vA;if(a<.01)discard;gl_FragColor=vec4(.96,.97,1.,a);}`
                 :`${LD_F}uniform float uA;varying float vA;void main(){\n#include <logdepthbuf_fragment>\nfloat a=uA*vA*.5;if(a<.01)discard;gl_FragColor=vec4(.78,.83,.9,a);}`;
  const m=new THREE.ShaderMaterial({uniforms:u,vertexShader:vs,fragmentShader:fs,transparent:true,depthWrite:false,fog:false});
  const o=isSnow?new THREE.Points(g,m):new THREE.LineSegments(g,m);o.frustumCulled=false;o.renderOrder=5;o.visible=false;scene.add(o);return o}
const WX_RAIN=wxField(LOW?2600:7000,70,false),WX_SNOW=wxField(LOW?3200:9000,60,true);
/* 수면 빗방울 파문 — 호수 형상 오버레이(근거리에서 동심원, 원거리는 수면 왜곡으로 표현) */
const WX_RIP=(()=>{const g=new THREE.ShapeGeometry(shapeOf(LAKE),2);g.rotateX(-Math.PI/2);
  const m=new THREE.ShaderMaterial({uniforms:{uTime:WXU.uTime,uA:{value:0},uD:{value:.5}},transparent:true,depthWrite:false,
   vertexShader:`${LD_V}varying vec3 vW;void main(){vec4 w=modelMatrix*vec4(position,1.);vW=w.xyz;gl_Position=projectionMatrix*viewMatrix*w;\n#include <logdepthbuf_vertex>\n}`,
   fragmentShader:`${LD_F}uniform float uTime,uA,uD;varying vec3 vW;float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
    void main(){\n#include <logdepthbuf_fragment>\nfloat a=0.;for(int j=0;j<3;j++){vec2 g=vW.xz/1.3+float(j)*vec2(.37,.71);vec2 c=floor(g),f=fract(g);float r=h(c+float(j)*7.3);
      if(r<uD){vec2 ct=vec2(h(c+3.1),h(c+5.7))*.6+.2;float t=fract(uTime*(.65+r*.7)+r*9.);float d=length(f-ct);a+=smoothstep(.045,0.,abs(d-t*.42))*(1.-t)*(1.-t);}}
     float far=1.-smoothstep(25.,140.,distance(vW,cameraPosition));float al=a*uA*far*.6;if(al<.01)discard;gl_FragColor=vec4(.88,.94,1.,al);}`});
  const o=new THREE.Mesh(g,m);o.position.y=-0.46;o.visible=false;o.renderOrder=4;scene.add(o);return o})();
const WX_FLASH=new THREE.AmbientLight(0xdfe8ff,0);scene.add(WX_FLASH);
/* --- 빗소리·천둥 (WebAudio 절차 합성, 첫 사용자 입력 후 시작) --- */
function wxAudio(){if(WX.au||!WX.snd)return;try{const C=new (window.AudioContext||window.webkitAudioContext)();const len=C.sampleRate*2,buf=C.createBuffer(1,len,C.sampleRate),d=buf.getChannelData(0);
  let b0=0,b1=0,b2=0;for(let i=0;i<len;i++){const w=Math.random()*2-1;b0=.99765*b0+w*.099;b1=.963*b1+w*.2965;b2=.57*b2+w*1.0526;d[i]=(b0+b1+b2+w*.1848)*.11}   /* 핑크 노이즈 */
  const s=C.createBufferSource();s.buffer=buf;s.loop=true;const hp=C.createBiquadFilter();hp.type='highpass';hp.frequency.value=900;const lp=C.createBiquadFilter();lp.type='lowpass';lp.frequency.value=7000;
  const g=C.createGain();g.gain.value=0;s.connect(hp);hp.connect(lp);lp.connect(g);g.connect(C.destination);s.start();WX.au={C,rain:g,buf}}catch(e){WX.snd=false}}
['pointerdown','keydown'].forEach(ev=>addEventListener(ev,()=>{if(WX.snd&&(WX.tgtR>0)){wxAudio();if(WX.au&&WX.au.C.state==='suspended')WX.au.C.resume()}}));
function wxThunder(dist){const A=WX.au;if(!A||!WX.snd||document.hidden)return;const C=A.C,now=C.currentTime+dist*.9;const s=C.createBufferSource();s.buffer=A.buf;s.playbackRate.value=.35;
  const lp=C.createBiquadFilter();lp.type='lowpass';lp.frequency.value=180+260*(1-dist);const g=C.createGain();g.gain.setValueAtTime(0,now);g.gain.linearRampToValueAtTime(.9*(1-dist*.6),now+.08);g.gain.exponentialRampToValueAtTime(.001,now+2.8+dist*1.5);
  s.connect(lp);lp.connect(g);g.connect(C.destination);s.start(now);s.stop(now+5)}
function updateWeather(dt){WX.t+=dt;WXU.uTime.value+=reduce?0:dt;WXU.uCam.value.copy(camera.position);
  const e=1-Math.exp(-dt*1.2);WX.rainA+=(WX.tgtR-WX.rainA)*e;WX.snowA+=(WX.tgtS-WX.snowA)*e;
  const dd=(WX.dimT||0)-WX.dim,df=(WX.fogT||0)-WX.fog;if(Math.abs(dd)>.004||Math.abs(df)>.004){WX.dim+=dd*e;WX.fog+=df*e;WX.atmT+=dt;if(WX.atmT>.4){WX.atmT=0;setTime(CUR_H)}}
  const under=PUR.under;WXU.uA.value=WX.rainA*(under?0:1);WX_RAIN.visible=WX.rainA>.01&&!under;
  WX_SNOW.material.uniforms.uA.value=WX.snowA*(under?0:.95);WX_SNOW.visible=WX.snowA>.01&&!under;
  WX_RIP.material.uniforms.uA.value=WX.rainA;WX_RIP.material.uniforms.uD.value=.25+.6*WX.rainA;WX_RIP.visible=WX.rainA>.01;
  if(water)water.material.uniforms.distortionScale.value=1.8+WX.rainA*3.2+WX.dim*.6;
  const ws=WX.data&&WX.data.cur&&WX.mode==='auto'?Math.min(8,WX.data.cur.wind||2):2.5,wd=((WX.data&&WX.data.cur&&WX.data.cur.windDeg)||250)*Math.PI/180;
  WXU.uWind.value.set(-Math.sin(wd)*ws*.35,Math.cos(wd)*ws*.35);
  /* 번개 */
  if(WX.kind==='storm'&&!reduce){WX.nextBolt-=dt;if(WX.nextBolt<=0){WX.nextBolt=5+Math.random()*10;WX.flash=1;WX.flash2=.18+Math.random()*.15;wxThunder(Math.random())}}
  if(WX.flash2>0){WX.flash2-=dt;if(WX.flash2<=0)WX.flash=.85}
  WX_FLASH.intensity=WX.flash*2.4;WX.flash*=Math.exp(-dt*9);
  if(WX.au){const now=WX.au.C.currentTime;WX.au.rain.gain.setTargetAtTime(WX.snd&&!document.hidden?WX.rainA*.22:0,now,.4)}}
/* --- 패널 --- */
const wxLoc=()=>LANG==='ko'?'ko-KR':LANG==='ja'?'ja-JP':'en-US';
const wxDay=(ms,i)=>i===0?T('wxToday'):new Date(ms).toLocaleDateString(wxLoc(),{weekday:'short',timeZone:'Asia/Seoul'});
const wxHm=ms=>ms?new Date(ms).toLocaleTimeString(wxLoc(),{hour:'2-digit',minute:'2-digit',hour12:false,timeZone:'Asia/Seoul'}):'—';
function wxRender(){const D=WX.data,c=D&&D.cur;const man=WX.mode!=='auto'?`<span class="man">${T('wxManual')}</span>`:'';
  if(!c){$('#wxNow').innerHTML=`<span class="wxi">${WX.mode==='auto'?'🛰️':wxEmoji({clear:800,clouds:804,rain:501,storm:211,snow:601,fog:741}[WX.mode]||800,'d')}</span><div><b>—</b>${man}<small>${WX.err?T(WX.err):T('wxLoading')}</small></div>`;$('#wxToday').innerHTML='';$('#wxDays').innerHTML='';$('#wxSrc').textContent='';return}
  $('#wxNow').innerHTML=`<span class="wxi">${wxEmoji(c.id,c.icon)}</span><div><b>${Math.round(c.temp)}°C</b>${man}<small>${c.desc||c.main} · ${T('wxFeels')} ${Math.round(c.feels)}°</small></div>`;
  const d0=D.daily&&D.daily[0];const rr=c.rain1h?`${c.rain1h} mm/h`:c.snow1h?`${c.snow1h} mm/h`:(d0?Math.round(d0.pop*100)+'%':'—');
  $('#wxToday').innerHTML=[[T('wxHiLo'),d0?`${Math.round(d0.max)}° / ${Math.round(d0.min)}°`:'—'],[c.rain1h||c.snow1h?T('wxPrecip'):T('wxPop'),rr],[T('wxHum'),c.hum+'%'],
    [T('wxWind'),(c.wind!=null?c.wind.toFixed(1):'—')+' m/s'],[T('wxSun'),wxHm(c.sunrise)],[T('wxSet'),wxHm(c.sunset)]].map(([k,v])=>`<div>${k}<b>${v}</b></div>`).join('');
  const days=(D.daily||[]);$('#wxDays').style.gridTemplateColumns=`repeat(${Math.max(1,days.length)},1fr)`;
  $('#wxDays').innerHTML=days.map((d,i)=>`<div title="${d.desc||''}">${wxDay(d.dt,i)}<i>${wxEmoji(d.id,d.icon)}</i><b>${Math.round(d.max)}°</b><em>${Math.round(d.min)}°</em><span class="pp">${d.pop>=.1?Math.round(d.pop*100)+'%':'&nbsp;'}</span></div>`).join('');
  $('#wxSrc').textContent=T('wxSrc',{t:wxHm(D.fetchedAt),n:days.length})}
async function wxFetch(){try{const r=await fetch('/api/weather?lang='+LANG,{cache:'no-store'});const j=await r.json().catch(()=>null);
    if(j&&j.success){WX.data=j.data;WX.err=null}else WX.err=(j&&j.error&&j.error.code==='WEATHER_DISABLED')?'wxNoKey':'wxFail'}catch(e){WX.err='wxFail'}
  wxResolve();wxRender()}
function wxSetMode(m){WX.mode=m;try{localStorage.setItem('sd_wx',m)}catch(e){}wxResolve();wxRender()}
function wxLang(){wxRender();wxFetch()}
try{const m=localStorage.getItem('sd_wx');if(m&&$('#wxMode').querySelector(`option[value="${m}"]`)){WX.mode=m;$('#wxMode').value=m}}catch(e){}
try{if(localStorage.getItem('sd_wxfold')==='1'){$('#wx').classList.add('fold');$('#wxFold').setAttribute('aria-expanded','false');$('#wxFold').textContent='▸'}}catch(e){}
$('#wxMode').addEventListener('change',e=>wxSetMode(e.target.value));
$('#wxSnd').addEventListener('click',e=>{WX.snd=!WX.snd;e.currentTarget.setAttribute('aria-pressed',String(WX.snd));if(WX.snd){wxAudio();if(WX.au)WX.au.C.resume()}});
$('#wxFold').addEventListener('click',e=>{const f=$('#wx').classList.toggle('fold');e.currentTarget.setAttribute('aria-expanded',String(!f));e.currentTarget.textContent=f?'▸':'▾';try{localStorage.setItem('sd_wxfold',f?'1':'0')}catch(_){}});
wxResolve();wxRender();wxFetch();setInterval(wxFetch,10*60e3);
'''
rep("\nstep(.05,T('ld1'),buildTextures);", JS + "\nstep(.05,T('ld1'),buildTextures);")

rep(" hudFold:{", """ wxTitle:{ko:'날씨 · 부천 상동',en:'Weather · Sangdong, Bucheon',ja:'天気・富川 上洞'},
 wxModeT:{ko:'날씨 연출 선택(실시간/수동)',en:'Weather effect (live / manual)',ja:'天気演出（リアルタイム／手動）'},
 wxAuto:{ko:'실시간',en:'Live',ja:'リアルタイム'},wxClear:{ko:'맑음',en:'Clear',ja:'晴れ'},wxClouds:{ko:'흐림',en:'Overcast',ja:'曇り'},wxRain:{ko:'비',en:'Rain',ja:'雨'},wxStorm:{ko:'뇌우',en:'Thunderstorm',ja:'雷雨'},wxSnow:{ko:'눈',en:'Snow',ja:'雪'},wxFog:{ko:'안개',en:'Fog',ja:'霧'},
 wxSndT:{ko:'빗소리·천둥 켜기/끄기',en:'Rain & thunder sound on/off',ja:'雨音・雷鳴のオン／オフ'},
 wxLoading:{ko:'날씨 불러오는 중…',en:'Loading weather…',ja:'天気を取得中…'},
 wxNoKey:{ko:'서버에 날씨 키(OPENWEATHER_API_KEY) 미설정 — 수동 연출만 가능',en:'Weather key (OPENWEATHER_API_KEY) not set on server — manual effects only',ja:'サーバーに天気キー（OPENWEATHER_API_KEY）未設定 — 手動演出のみ'},
 wxFail:{ko:'날씨 서버 응답 없음 — 잠시 후 다시 시도',en:'Weather service unavailable — retrying later',ja:'天気サーバー応答なし — 後で再試行'},
 wxManual:{ko:'수동 연출',en:'MANUAL',ja:'手動演出'},wxFeels:{ko:'체감',en:'feels',ja:'体感'},wxToday:{ko:'오늘',en:'Today',ja:'今日'},
 wxHiLo:{ko:'최고/최저',en:'High / Low',ja:'最高／最低'},wxPop:{ko:'강수확률',en:'Precip. chance',ja:'降水確率'},wxPrecip:{ko:'강수량',en:'Precipitation',ja:'降水量'},wxHum:{ko:'습도',en:'Humidity',ja:'湿度'},wxWind:{ko:'풍속',en:'Wind',ja:'風速'},wxSun:{ko:'일출',en:'Sunrise',ja:'日の出'},wxSet:{ko:'일몰',en:'Sunset',ja:'日の入り'},
 wxSrc:{ko:'OpenWeather · {t} 갱신 · {n}일 예보 · 10분마다 자동 갱신',en:'OpenWeather · updated {t} · {n}-day forecast · refreshes every 10 min',ja:'OpenWeather・{t} 更新・{n}日予報・10分ごと自動更新'},
 hudFold:{""")
p.write_text(t); print('weather patched')
