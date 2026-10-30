/* ================= 녹조제거 쌍동선 (AQUA-NANO BOT) =================
   STL(1.6 m, 면 색상) → 호수 수면에서만 자율운항. 녹조 밀집 구역 우선 탐색, 전방 다공 UFB 박스에서
   마이크로·나노버블 분사 + 광촉매 ROS 생성, 지나간 자리의 녹조를 마스크로 제거(서서히 재성장). 개념 시각화. */
const BOAT={on:false,speed:10,base:1.5,pos:new THREE.Vector2(-20,10),hd:0,v:0,target:null,follow:false,grp:null,lbl:null,
  mask:null,ctx:null,tex:null,box:null,stat:null,lakePix:null,pct:0,t:0,tStat:0,tRegrow:0,frame:0,R:9};
function buildBoat(){PUR.u.uNight={value:0};
  /* --- mesh from STL groups (0.1 mm ints, Z-up, +X bow) --- */
  const raw=atob(BOATMESH.data);const u8=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)u8[i]=raw.charCodeAt(i);const q=new Int16Array(u8.buffer);
  const MAT={pontoon:new THREE.MeshPhongMaterial({color:C(0x1b1c1e),shininess:55,specular:C(0x555555)}),
    hull:new THREE.MeshPhongMaterial({color:C(0x8c9298),shininess:90,specular:C(0x888888)}),
    ufbbox:new THREE.MeshPhongMaterial({color:C(0xc6c8ca),shininess:40,specular:C(0x555555),side:THREE.DoubleSide}),
    logo:new THREE.MeshLambertMaterial({color:C(0x1f2a6b)}),black:new THREE.MeshPhongMaterial({color:C(0x1e1e20),shininess:30}),
    white:new THREE.MeshLambertMaterial({color:C(0xefefec)}),frame:new THREE.MeshLambertMaterial({color:C(0x8e9196)}),ctrl:new THREE.MeshLambertMaterial({color:C(0xdcdcd8)})};
  const solarTex=canvasTex(256,256,(x,w,h)=>{x.fillStyle='#24526c';x.fillRect(0,0,w,h);x.strokeStyle='#9fb3c2';x.lineWidth=3;x.strokeRect(1,1,w-2,h-2);
    x.strokeStyle='rgba(170,195,215,.55)';x.lineWidth=1;for(let i=1;i<6;i++){x.beginPath();x.moveTo(i*w/6,0);x.lineTo(i*w/6,h);x.stroke();x.beginPath();x.moveTo(0,i*h/6);x.lineTo(w,i*h/6);x.stroke()}
    const g=x.createLinearGradient(0,0,w,h);g.addColorStop(0,'rgba(255,255,255,.10)');g.addColorStop(.5,'rgba(255,255,255,0)');g.addColorStop(1,'rgba(255,255,255,.06)');x.fillStyle=g;x.fillRect(0,0,w,h)});
  MAT.solar=new THREE.MeshPhongMaterial({map:solarTex,shininess:140,specular:C(0xaabbcc)});
  const grp=new THREE.Group(),body=new THREE.Group();let off=0;const WL=(BOATMESH.waterlineZ_mm||90)/1000;
  BOATMESH.groups.forEach(g=>{const n=g.count;const P=new Float32Array(n*3);
    for(let i=0;i<n;i++){const x=q[(off+i)*3]*1e-4,y=q[(off+i)*3+1]*1e-4,z=q[(off+i)*3+2]*1e-4;P[i*3]=x;P[i*3+1]=z-WL;P[i*3+2]=-y}
    off+=n;const geo2=new THREE.BufferGeometry();geo2.setAttribute('position',new THREE.BufferAttribute(P,3));geo2.computeVertexNormals();
    if(g.role==='solar'){const UV=new Float32Array(n*2);for(let i=0;i<n;i++){UV[i*2]=(P[i*3]+.68)/1.16*4;UV[i*2+1]=(P[i*3+2]+.38)/.76*2}geo2.setAttribute('uv',new THREE.BufferAttribute(UV,2))}
    const m=new THREE.Mesh(geo2,MAT[g.role]||MAT.white);m.castShadow=true;m.receiveShadow=true;body.add(m)});
  grp.add(body);
  F.forEach(f=>{if(f.fl&1)for(let i=0;i<f.pts.length-1;i++){const a=f.pts[i],b=f.pts[i+1],m=[(a[0]+b[0])/2,(a[1]+b[1])/2];if(inPoly(a,LAKE)||inPoly(b,LAKE)||inPoly(m,LAKE))deckSegs.push([a,b])}});for(let i=0;i<PIER.length-1;i++)deckSegs.push([PIER[i],PIER[i+1]]);
  /* locator ring (boat is real-scale 1.6 m) */
  const ring=new THREE.Mesh(new THREE.RingGeometry(2.6,3.0,48),new THREE.MeshBasicMaterial({color:0x9ff0b8,transparent:true,opacity:.7,depthWrite:false,side:THREE.DoubleSide}));
  ring.rotation.x=-Math.PI/2;ring.position.y=.06;grp.add(ring);BOAT.ring=ring;
  {const tx=canvasTex(128,128,(x,w,h)=>{const g=x.createRadialGradient(w/2,h/2,0,w/2,h/2,w/2);g.addColorStop(0,'rgba(200,150,255,1)');g.addColorStop(.35,'rgba(150,90,255,.55)');g.addColorStop(1,'rgba(120,60,255,0)');x.fillStyle=g;x.fillRect(0,0,w,h)});
   const gl=new THREE.Mesh(new THREE.CircleGeometry(3.4,40),new THREE.MeshBasicMaterial({map:tx,transparent:true,opacity:0,depthWrite:false,blending:THREE.AdditiveBlending}));gl.rotation.x=-Math.PI/2;gl.position.y=.04;grp.add(gl);BOAT.uvGlow=gl;
   const lt=new THREE.PointLight(0x9a6bff,0,9,1.6);lt.position.set(.6,.15,0);grp.add(lt);BOAT.uvLight=lt}   /* UVA 365 nm 램프(그늘 보강 시 강해짐) */
  grp.position.set(BOAT.pos.x,-0.5,BOAT.pos.y);grp.visible=false;scene.add(grp);BOAT.grp=grp;BOAT.body=body;
  BOAT.lbl=addLabel(()=>T('boatLbl'),BOAT.pos.x,3.4,BOAT.pos.y,'module','boat');BOAT.lbl.hidden=true;
  /* --- clean mask over the lake (canvas → texture used by purify shaders) --- */
  const xs=LAKE.map(p=>p[0]),zs=LAKE.map(p=>p[1]);const x0=Math.min(...xs)-6,x1=Math.max(...xs)+6,z0=Math.min(...zs)-6,z1=Math.max(...zs)+6;
  const S=256;const cv=document.createElement('canvas');cv.width=cv.height=S;const ctx=cv.getContext('2d',{willReadFrequently:true});ctx.fillStyle='#000';ctx.fillRect(0,0,S,S);
  const tex=new THREE.CanvasTexture(cv);tex.minFilter=tex.magFilter=THREE.LinearFilter;tex.generateMipmaps=false;
  BOAT.mask=cv;BOAT.ctx=ctx;BOAT.tex=tex;BOAT.box=[x0,z0,S/(x1-x0),S/(z1-z0)];BOAT.S=S;
  const lp=[];for(let j=0;j<S;j+=2)for(let i=0;i<S;i+=2){const wx=x0+(i+.5)/BOAT.box[2],wz=z0+(j+.5)/BOAT.box[3];if(inPoly([wx,wz],LAKE))lp.push(j*S+i)}BOAT.lakePix=lp;
  tex.flipY=false;const u=PUR.u;u.uMask.value=tex;u.uBox.value.set(x0,z0,1/(x1-x0),1/(z1-z0));
  /* --- particle pool: surface UFB bubbles / underwater bubbles / wake foam / ROS sparks --- */
  const NP=3200;const P=new Float32Array(NP*3),A=new Float32Array(NP),SZ=new Float32Array(NP),K=new Float32Array(NP);
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(P,3));g.setAttribute('al',new THREE.BufferAttribute(A,1));g.setAttribute('sz',new THREE.BufferAttribute(SZ,1));g.setAttribute('kd',new THREE.BufferAttribute(K,1));
  const m=new THREE.ShaderMaterial({uniforms:PUR.u,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
    vertexShader:pVS+`uniform float uScale,uUnder;attribute float al,sz,kd;varying float vA,vK;void main(){vec4 mv=modelViewMatrix*vec4(position,1.);vK=kd;
      vA=al*mix(1.,exp(-length(mv.xyz)*.03),uUnder);if(kd>1.5&&kd<2.5)vA*=1.-.6*uUnder;gl_PointSize=clamp(sz*uScale/-mv.z,1.5,40.);gl_Position=projectionMatrix*mv;`+pVE+`}`,
    fragmentShader:pFS+`uniform sampler2D uAtlas;uniform float uNight;varying float vA,vK;void main(){`+pFE+`vec4 c=texture2D(uAtlas,vec2(gl_PointCoord.x*.25,gl_PointCoord.y));
      float r=length(gl_PointCoord-.5);float soft=smoothstep(.5,0.,r);vec3 col=vec3(.85,.98,1.);float a=c.a;
      if(vK>1.5&&vK<2.5){a=soft*.8;col=vec3(1.);}if(vK>2.5){a=soft;col=mix(vec3(.72,.95,1.),vec3(.8,.5,1.),step(3.5,vK));col=mix(col,vec3(1.),smoothstep(.18,0.,r)*.7);a*=1.+uNight*1.3;}
      if(a*vA<.01)discard;gl_FragColor=vec4(col*a,a*vA);}`});
  const pts=new THREE.Points(g,m);pts.frustumCulled=false;pts.visible=false;scene.add(pts);
  BOAT.pp={P,A,SZ,K,V:new Float32Array(NP*3),L:new Float32Array(NP),AG:new Float32Array(NP),N:NP,head:0,geo:g,pts};
  buildMission();
}
function bSpawn(x,y,z,vx,vy,vz,life,size,kind){const p=BOAT.pp;const i=p.head;p.head=(p.head+1)%p.N;p.P[i*3]=x;p.P[i*3+1]=y;p.P[i*3+2]=z;p.V[i*3]=vx;p.V[i*3+1]=vy;p.V[i*3+2]=vz;p.L[i]=life;p.AG[i]=0;p.SZ[i]=size;p.K[i]=kind}
function cleanAt(x,z){if(!BOAT.stat)return 0;const i=Math.floor((x-BOAT.box[0])*BOAT.box[2]),j=Math.floor((z-BOAT.box[1])*BOAT.box[3]);if(i<0||j<0||i>=BOAT.S||j>=BOAT.S)return 0;return BOAT.stat[(j*BOAT.S+i)*4]/255}
/* navigation: water only (lake polygon, shore margin), avoid fountains, buoys, outlets, lake decks/pier */
const deckSegs=[];let MODE='pur';
/* ---- 데크 밑 통과 게이트(기둥 사이) ---- */
let DECK_PILES=[],DECK_WOOD=[],BANDS=[];
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

function buildBands(){BANDS=[];DECK_WOOD.forEach(d=>{const hw=d.w/2;for(let i=0;i<d.pts.length-1;i++){const a=d.pts[i],b=d.pts[i+1];const L=Math.hypot(b[0]-a[0],b[1]-a[1]);if(L<1)continue;
    const mid=[(a[0]+b[0])/2,(a[1]+b[1])/2];if(!(inPoly(a,LAKE)||inPoly(b,LAKE)||inPoly(mid,LAKE)||edgeDist(mid,LAKE)<hw+3))continue;
    const gaps=[];for(let s=0;s+4<=L+1e-6;s+=4)gaps.push(s+2);BANDS.push({a,b,L,ux:(b[0]-a[0])/L,uz:(b[1]-a[1])/L,hw,gaps,y:d.y||0.85})}})}
function bandInfo(p,extra){for(const B of BANDS){const dx=p[0]-B.a[0],dz=p[1]-B.a[1];const s=dx*B.ux+dz*B.uz;if(s<-1.5||s>B.L+1.5)continue;const d=-dx*B.uz+dz*B.ux;
    if(Math.abs(d)<B.hw+extra){let g=null,gd=1e9;for(const q of B.gaps){const e=Math.abs(q-s);if(e<gd){gd=e;g=q}}return {B,s,d,g,gd}}}return null}
function nearPile(p,r){for(const q of DECK_PILES){const dx=q[0]-p[0],dz=q[1]-p[1];if(dx*dx+dz*dz<r*r)return true}return false}
function deckOK(p,strict){const ex=strict?1.4:0.6,cw=strict?1.1:1.5;for(const B of BANDS){const dx=p[0]-B.a[0],dz=p[1]-B.a[1];const s=dx*B.ux+dz*B.uz;if(s<-1.5||s>B.L+1.5)continue;
    if(Math.abs(-dx*B.uz+dz*B.ux)>=B.hw+ex)continue;let gd=1e9;for(const q of B.gaps)gd=Math.min(gd,Math.abs(q-s));if(gd>=cw)return false}   /* 겹치는 모든 데크 구간에서 통로 안이어야 함 */
  return !nearPile(p,strict?1.1:0.75)}

function boatValid(p){if(!inPoly(p,LAKE)||edgeDist(p,LAKE)<5.5)return false;for(const f of FOUNT)if(Math.hypot(p[0]-f[0],p[1]-f[1])<8)return false;
  for(const s of SENS)if(Math.hypot(p[0]-s.p[0],p[1]-s.p[1])<4.5)return false;for(const u of UNITS)if(Math.hypot(p[0]-u.ret[0],p[1]-u.ret[1])<6||Math.hypot(p[0]-u.int[0],p[1]-u.int[1])<6)return false;return deckOK(p,true)}
function boatPath(a,b){const L=Math.hypot(b[0]-a[0],b[1]-a[1]);const n=Math.max(2,Math.ceil(L/0.7));for(let k=1;k<=n;k++){const t=k/n;if(!boatValid([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]))return false}return true}
function boatPick(){const a=[BOAT.pos.x,BOAT.pos.y];let best=null,bs=-1e9;
  for(let k=0;k<40;k++){const s=PUR.samples[(Math.random()*PUR.samples.length)|0];const p=[s[0],s[2]];if(!boatValid(p))continue;const d=Math.hypot(p[0]-a[0],p[1]-a[1]);if(d<12)continue;
    let dirt=0;for(let j=0;j<5;j++){const ang=j*1.2566;dirt+=1-cleanAt(p[0]+Math.cos(ang)*6,p[1]+Math.sin(ang)*6)}dirt=dirt/5+(1-cleanAt(p[0],p[1]));
    const sc=dirt*1.6-d/120+Math.random()*.15;if(sc>bs&&boatPath(a,p)){bs=sc;best=p}}
  if(!best){for(let k=0;k<60&&!best;k++){const s=PUR.samples[(Math.random()*PUR.samples.length)|0];const p=[s[0],s[2]];if(boatValid(p)&&boatPath(a,p))best=p}}
  BOAT.target=best}
function boatReset(){const c=BOAT.ctx;c.globalCompositeOperation='source-over';c.fillStyle='#000';c.fillRect(0,0,BOAT.S,BOAT.S);BOAT.tex.needsUpdate=true;BOAT.stat=c.getImageData(0,0,BOAT.S,BOAT.S).data;
  let st=[-20,10];if(!boatValid(st))for(const s of PUR.samples){if(boatValid([s[0],s[2]])){st=[s[0],s[2]];break}}BOAT.pos.set(st[0],st[1]);BOAT.hd=0;BOAT.v=0;BOAT.target=null;BOAT.pct=0;
  const p=BOAT.pp;p.L.fill(0);p.A.fill(0)}
function boatSetOn(on){BOAT.on=on;if(!BOAT.grp)return;BOAT.grp.visible=on;BOAT.pp.pts.visible=on;BOAT.lbl.hidden=!on;PUR.u.uMaskOn.value=on?1:0;BOAT.follow=false;const fb=$('#bFollow');if(fb)fb.setAttribute('aria-pressed','false');if(on){boatReset();missionStart()}else missionHide()}
const _bt=new THREE.Vector3(),_bc=new THREE.Vector3();
function updateBoat(dt){if(!BOAT.on||!BOAT.grp)return;const sp=BOAT.speed,sdt=dt*sp;BOAT.t+=dt;
  const run=missionStep(dt,sdt);
  const T0=BOAT.t,fx=Math.cos(BOAT.hd),fz=Math.sin(BOAT.hd),rx=-fz,rz=fx;
  const g=BOAT.grp;g.position.set(BOAT.pos.x,-0.5+.025*Math.sin(T0*2.1),BOAT.pos.y);g.rotation.set(0,-BOAT.hd,0);BOAT.body.rotation.set(.018*Math.sin(T0*1.7),0,.012*Math.sin(T0*1.3+1));
  BOAT.ring.material.opacity=.45+.3*Math.sin(T0*3);BOAT.lbl.v.set(BOAT.pos.x,3.4,BOAT.pos.y);PUR.u.uBoat.value.set(BOAT.pos.x+fx*.7,BOAT.pos.y+fz*.7,BOAT.hd);
  /* emission (scaled gently with playback speed) */
  const em=run?Math.sqrt(sp):0;
  const shadeF=run?Math.max(deckShadow([BOAT.pos.x,BOAT.pos.y]),SUN_NIGHT):0;MS.shadeF=shadeF;MS.uva=(MS.uva||.6)+((run?.6+.4*shadeF:0)-(MS.uva||.6))*Math.min(1,dt*6);   /* 실제 데크 그림자(태양 방향) 또는 야간에만 UVA 100% */   /* 데크 밑 그늘 → UVA 100% */
  const boost=clamp((MS.uva-.6)/.4,0,1),glv=Math.min(1.3,boost+(run?SUN_NIGHT*.6:0));if(BOAT.uvGlow){BOAT.uvGlow.material.opacity=Math.min(1,glv*(.8+.2*Math.sin(BOAT.t*9)));BOAT.uvGlow.scale.setScalar(1+.4*SUN_NIGHT);BOAT.uvLight.intensity=glv*4*(1+2*SUN_NIGHT)*(.85+.15*Math.sin(BOAT.t*7))}PUR.u.uNight.value=SUN_NIGHT;   /* 야간: UVA 빛 강화 */
  if(run){if(!MS.st)stReset();MS.st.t+=sdt;if(MS.uva>=.9){MS.st.uvaT+=sdt;if(MS.inGate)MS.inGate.g.uvaT=(MS.inGate.g.uvaT||0)+sdt}if(MS.inGate)MS.inGate.g.last=Date.now()}const bx=BOAT.pos.x+fx*.7,bz=BOAT.pos.y+fz*.7;
  for(let k=0;k<Math.round(4*em);k++){const sd=Math.random()<.5?-1:1,lat=R(.6,2.2)*sd,fwd=R(-.6,.3);bSpawn(bx+rx*.22*sd,-0.45,bz+rz*.22*sd,rx*lat+fx*fwd,0,rz*lat+fz*fwd,R(4,8),R(.08,.22),1)}
  for(let k=0;k<Math.round(3*em);k++){const a=Math.random()*6.283,s=R(.2,1.2);bSpawn(bx+R(-.2,.2),-0.85,bz+R(-.2,.2),Math.cos(a)*s,R(.05,.25),Math.sin(a)*s,R(4,7),R(.05,.16),0)}
  for(let k=0;k<Math.round(2*em);k++){const sd=Math.random()<.5?-1:1;const sx=BOAT.pos.x-fx*.8+rx*.3*sd,sz=BOAT.pos.y-fz*.8+rz*.3*sd;bSpawn(sx,-0.44,sz,-fx*.4+rx*R(-.25,.25)*sd,0,-fz*.4+rz*R(-.25,.25)*sd,R(3,5),R(.25,.5),2)}
  const nRos=Math.round(3*em*(1+2*boost));if(run&&MS.st){MS.st.ros+=nRos;if(MS.inGate)MS.inGate.g.ros=(MS.inGate.g.ros||0)+nRos}   /* ROS 발생 지수 집계 */
  for(let k=0;k<nRos;k++){const a=Math.random()*6.283,r0=R(.5,7-2*boost);bSpawn(bx+Math.cos(a)*r0,R(-2.4,-0.6),bz+Math.sin(a)*r0,R(-.2,.2),R(-.05,.1),R(-.2,.2),R(.6,1.6),R(.12,.26)*(1+.3*boost),Math.random()<(.55-.25*boost)?3:4)}   /* 그늘 보강 시 ROS 3배·보라(O₂⁻) 비중↑ */
  /* integrate particles */
  const p=BOAT.pp;for(let i=0;i<p.N;i++){if(p.L[i]<=0){p.A[i]=0;continue}p.AG[i]+=dt;const t=p.AG[i];if(t>=p.L[i]){p.L[i]=0;p.A[i]=0;continue}
    const k=p.K[i],dk=Math.exp(-dt*(k===0?.5:k===1?.35:.9));p.V[i*3]*=dk;p.V[i*3+2]*=dk;if(k===0){p.V[i*3+1]+=dt*.12;}
    p.P[i*3]+=p.V[i*3]*dt;p.P[i*3+1]+=p.V[i*3+1]*dt;p.P[i*3+2]+=p.V[i*3+2]*dt;if(k===0&&p.P[i*3+1]>-0.56){p.P[i*3+1]=-0.56;p.V[i*3+1]=0}
    const lf=t/p.L[i];p.A[i]=(k>2.5?Math.pow(.5+.5*Math.sin(t*25+i),2):1)*Math.min(1,t*4)*(1-lf)*(k===2?.55:1)}
  ['position','al','sz','kd'].forEach(a=>p.geo.attributes[a].needsUpdate=true);
  /* paint the clean mask (accumulates where the plume passes), slow regrowth */
  const c=BOAT.ctx,S=BOAT.S,px=(bx-BOAT.box[0])*BOAT.box[2],pz=(bz-BOAT.box[1])*BOAT.box[3],rp=BOAT.R*BOAT.box[2];
  if(run){c.globalCompositeOperation='lighter';const gr=c.createRadialGradient(px,pz,0,px,pz,rp);const al=Math.min(1,sdt*.5*(1+.8*boost));gr.addColorStop(0,`rgba(255,255,255,${al})`);gr.addColorStop(.6,`rgba(255,255,255,${al*.6})`);gr.addColorStop(1,'rgba(255,255,255,0)');
  c.fillStyle=gr;c.beginPath();c.arc(px,pz,rp,0,7);c.fill()}
  BOAT.tRegrow+=sdt;if(BOAT.tRegrow>20){BOAT.tRegrow=0;c.globalCompositeOperation='source-over';c.fillStyle='rgba(0,0,0,0.02)';c.fillRect(0,0,S,S)}
  if((++BOAT.frame)%3===0)BOAT.tex.needsUpdate=true;
  BOAT.tStat+=dt;if(BOAT.tStat>.8||!BOAT.stat){BOAT.tStat=0;BOAT.stat=c.getImageData(0,0,S,S).data;let k2=0;for(const ix of BOAT.lakePix)if(BOAT.stat[ix*4]>150)k2++;BOAT.pct=Math.round(k2/BOAT.lakePix.length*100);
    const hb=$('#boatBar');if(hb){hb.style.width=BOAT.pct+'%';$('#boatPct').textContent=BOAT.pct+'%';if(MS.ph===3)$('#boatMsg').textContent=MS.man?rcMsg():(MS.rcBackT&&performance.now()-MS.rcBackT<4000)?T('msRcBack'):MS.rec?T('msRecover'):MS.inGate?T('msGate',{c:MS.inGate.g.clr.toFixed(2),k:Math.min(3,MS.inGate.g.passes+1),p:Math.round((MS.uva||.6)*100)}):MS.avoid?T('msAvoid',{d:MS.avoid.d.toFixed(1)}):BOAT.pct>=90?T('boatDone'):T('boatRun',{v:(BOAT.v).toFixed(1)})}}
  /* follow camera */
  updateSensorsViz(dt);
  if(BOAT.follow&&!fly&&MS.ph===3&&cineCam(dt)){}else if(BOAT.follow&&!fly&&MS.ph===3){const k=1-Math.exp(-dt*2.2);_bt.set(BOAT.pos.x+fx*7,-0.3,BOAT.pos.y+fz*7);_bc.set(BOAT.pos.x-fx*12+rx*5,7.5,BOAT.pos.y-fz*12+rz*5);   /* 보트를 화면 아래쪽에 → 상단 패널에 가리지 않음 */controls.target.lerp(_bt,k);camera.position.lerp(_bc,k)}
}
/* ===== 자율운항 미션: ① 수계 인식(위성영상+LiDAR) → ② 커버리지 경로 최적화 → ③ GNSS·LiDAR 자율운항/장애물 회피 ===== */
const MS={ph:0,t:0,grid:null,path:[],pi:0,pass:0,avoid:null,obs:[],len:0,cov:0,area:0,nogo:[],near:99,nHit:0,encT:0,stuck:0,tCol:0,tTel:0,ang:0};
const GEO={lat:37.5038,lon:126.7450};/* OSM 로컬좌표 원점(WGS84) — x=동, z=남 [m] */
let LAKEC=[0,0];
function msMat(c,o){return new THREE.MeshBasicMaterial({color:c,transparent:true,opacity:o,depthWrite:false,side:THREE.DoubleSide})}
function buildMission(){
  let cx=0,cz=0;LAKE.forEach(p=>{cx+=p[0];cz+=p[1]});LAKEC=[cx/LAKE.length,cz/LAKE.length];
  let ar=0;for(let i=0,j=LAKE.length-1;i<LAKE.length;j=i++)ar+=(LAKE[j][0]+LAKE[i][0])*(LAKE[j][1]-LAKE[i][1]);MS.area=Math.abs(ar/2);
  const xs=LAKE.map(p=>p[0]),zs=LAKE.map(p=>p[1]);const cs=3.5,x0=Math.min(...xs),z0=Math.min(...zs),nx=Math.ceil((Math.max(...xs)-x0)/cs)+1,nz=Math.ceil((Math.max(...zs)-z0)/cs)+1;
  buildBands();
  const v=new Uint8Array(nx*nz);for(let j=0;j<nz;j++)for(let i=0;i<nx;i++)v[j*nx+i]=boatValid([x0+i*cs,z0+j*cs])?1:0;MS.grid={cs,x0,z0,nx,nz,v};
  MS.gates=[];MS.lowGates=[];MS.gateMap=new Map();BANDS.forEach(B=>B.gaps.forEach(gp=>{const G=[B.a[0]+B.ux*gp,B.a[1]+B.uz*gp],nx2=-B.uz,nz2=B.ux,o=B.hw+2.2;
    const A=[G[0]-nx2*o,G[1]-nz2*o],Bp=[G[0]+nx2*o,G[1]+nz2*o];if(!inPoly(G,LAKE)||edgeDist(G,LAKE)<3||!boatValid(A)||!boatValid(Bp))return;
    for(let k=0;k<=40;k++){const q=[A[0]+(Bp[0]-A[0])*k/40,A[1]+(Bp[1]-A[1])*k/40];if(!deckOK(q,true)||!inPoly(q,LAKE))return}   /* 꺾인 데크 모서리 등 다른 구간을 스치는 게이트 제외 */
    const ca=nearValid(cellOf(A)),cb=nearValid(cellOf(Bp)),ia=ca[1]*nx+ca[0],ib=cb[1]*nx+cb[0];if(ia===ib)return;const cost=(2*o)/cs+1;
    const boatTop=-0.5+((BOATMESH.bbox_mm[1][2]-(BOATMESH.waterlineZ_mm||90))/1000),deckBot=(B.y||0.85)-0.12,clr=deckBot-boatTop;   /* 마스트 높이 검사 */
    if(clr<0.15){MS.lowGates.push({G,clr});return}
    const gate={A,G,B:Bp,hw:B.hw,clr,u:[B.ux,B.uz],passes:0,side:0};MS.gates.push(gate);[[ia,ib,A,Bp],[ib,ia,Bp,A]].forEach(([f,to,p0,p1])=>{if(!MS.gateMap.has(f))MS.gateMap.set(f,[]);MS.gateMap.get(f).push({to,cost,pts:[p0,G,p1]})})}));
  const G=new THREE.Group();G.visible=false;scene.add(G);MS.G=G;
  /* scan overlay */
  {const g=new THREE.ShapeGeometry(shapeOf(LAKE),2);g.rotateX(-Math.PI/2);
   const u={uScan:{value:0},uFade:{value:1},uZ0:{value:Math.min(...zs)-4},uZ1:{value:Math.max(...zs)+4}};MS.su=u;
   const m=new THREE.ShaderMaterial({uniforms:u,transparent:true,depthWrite:false,side:THREE.DoubleSide,
     vertexShader:pVS+`varying vec3 vW;void main(){vec4 w=modelMatrix*vec4(position,1.);vW=w.xyz;gl_Position=projectionMatrix*viewMatrix*w;`+pVE+`}`,
     fragmentShader:pFS+`uniform float uScan,uFade,uZ0,uZ1;varying vec3 vW;void main(){`+pFE+`float sz=mix(uZ0,uZ1,uScan);float done=step(vW.z,sz);
       vec2 g=abs(fract(vW.xz/4.)-.5);float ln=smoothstep(.43,.5,max(g.x,g.y));float band=exp(-pow((vW.z-sz)/2.4,2.))*step(uScan,.999);
       vec3 col=mix(vec3(.25,.85,1.),vec3(.92,1.,1.),band);float a=done*(.07+ln*.42)*uFade+band*.85;if(a<.004)discard;gl_FragColor=vec4(col,a);}`});
   const mesh=new THREE.Mesh(g,m);mesh.position.y=-0.40;mesh.renderOrder=4;G.add(mesh)}
  /* recognised shoreline */
  {const P=[];LAKE.forEach(p=>P.push(p[0],-0.33,p[1]));const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(P,3));
   const l=new THREE.Line(g,new THREE.LineBasicMaterial({color:0x7fe9ff,transparent:true,opacity:.95,depthWrite:false}));l.renderOrder=5;G.add(l);MS.shore=l;MS.shoreN=LAKE.length}
  /* no-go zones (fountains, buoys, outlets, decks) */
  const ring=(p,r)=>{const m=new THREE.Mesh(new THREE.RingGeometry(r-.3,r,48),msMat(0xff5a5a,.6));m.rotation.x=-Math.PI/2;m.position.set(p[0],-0.36,p[1]);m.userData.z=p[1];G.add(m);MS.nogo.push(m)};
  FOUNT.forEach(f=>ring(f,8));SENS.forEach(s=>ring(s.p,4.5));UNITS.forEach(u=>{ring(u.ret,6);ring(u.int,6)});
  (MS.lowGates||[]).forEach(gt=>{const m=new THREE.Mesh(new THREE.RingGeometry(.45,.65,24),msMat(0xff4d5e,.9));m.rotation.x=-Math.PI/2;m.position.set(gt.G[0],-0.34,gt.G[1]);m.userData.z=gt.G[1];G.add(m);MS.nogo.push(m)});
  (MS.gates||[]).forEach(gt=>{const m=new THREE.Mesh(new THREE.RingGeometry(.45,.65,24),msMat(0x7ff0b0,.85));m.rotation.x=-Math.PI/2;m.position.set(gt.G[0],-0.34,gt.G[1]);m.userData.z=gt.G[1];m.userData.gate=1;G.add(m);MS.nogo.push(m)});
  MS.shadowM=BANDS.map(B=>{const nx=-B.uz*B.hw,nz=B.ux*B.hw,a=B.a,b=B.b,y=-0.455;const g=new THREE.BufferGeometry();
    g.setAttribute('position',new THREE.Float32BufferAttribute([a[0]+nx,y,a[1]+nz,a[0]-nx,y,a[1]-nz,b[0]+nx,y,b[1]+nz,a[0]-nx,y,a[1]-nz,b[0]-nx,y,b[1]-nz,b[0]+nx,y,b[1]+nz],3));
    const m=new THREE.Mesh(g,new THREE.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.3,depthWrite:false,side:THREE.DoubleSide}));m.renderOrder=4;G.add(m);return m});
  deckSegs.forEach(s=>{const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute([s[0][0],-0.3,s[0][1],s[1][0],-0.3,s[1][1]],3));
    const l=new THREE.Line(g,new THREE.LineBasicMaterial({color:0xff6a5a,transparent:true,opacity:.9,depthWrite:false}));l.userData.z=Math.min(s[0][1],s[1][1]);l.userData.line=1;G.add(l);MS.nogo.push(l)});
  /* planned path: ribbon 2.2 m wide (6 verts / segment) */
  {const N=9000;const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(N*18),3));g.setAttribute('color',new THREE.BufferAttribute(new Float32Array(N*18),3));g.setDrawRange(0,0);
   const l=new THREE.Mesh(g,new THREE.MeshBasicMaterial({vertexColors:true,transparent:true,opacity:.7,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending}));l.renderOrder=6;l.frustumCulled=false;G.add(l);MS.pl=l;MS.plN=N}
  /* LiDAR: rotating fan + range ring + hit cloud */
  {const fan=new THREE.Mesh(new THREE.CircleGeometry(15,24,0,.42),new THREE.MeshBasicMaterial({color:0x7dff9e,transparent:true,opacity:.16,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending}));
   fan.geometry.rotateX(-Math.PI/2);G.add(fan);MS.fan=fan;
   const rr=new THREE.Mesh(new THREE.RingGeometry(14.85,15,96),msMat(0x7dff9e,.35));rr.rotation.x=-Math.PI/2;G.add(rr);MS.rr=rr;
   const N=1400;const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(N*3),3));g.setAttribute('col',new THREE.BufferAttribute(new Float32Array(N*3),3));g.setAttribute('al',new THREE.BufferAttribute(new Float32Array(N),1));
   const m=new THREE.ShaderMaterial({uniforms:PUR.u,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
     vertexShader:pVS+`uniform float uScale;attribute vec3 col;attribute float al;varying vec3 vC;varying float vA;void main(){vC=col;vA=al;vec4 mv=modelViewMatrix*vec4(position,1.);gl_PointSize=clamp(.42*uScale/-mv.z,2.,16.);gl_Position=projectionMatrix*mv;`+pVE+`}`,
     fragmentShader:pFS+`varying vec3 vC;varying float vA;void main(){`+pFE+`float r=length(gl_PointCoord-.5);float a=smoothstep(.5,.1,r)*vA;if(a<.01)discard;gl_FragColor=vec4(vC*a,a);}`});
   const pts=new THREE.Points(g,m);pts.frustumCulled=false;G.add(pts);MS.hp={g,N,head:0,L:new Float32Array(N)};MS.hpMat=m}
  /* GNSS constellation + downlink */
  {MS.sats=[];const bm=new THREE.MeshLambertMaterial({color:C(0xd9b44a)}),pm=new THREE.MeshLambertMaterial({color:C(0x2d5a8a)});
   for(let k=0;k<6;k++){const a=k*1.047+.4,r=230+30*(k%2);const s=new THREE.Group();s.add(new THREE.Mesh(new THREE.BoxGeometry(5,5,7),bm));
     const pn=new THREE.Mesh(new THREE.BoxGeometry(24,.4,6),pm);s.add(pn);s.position.set(LAKEC[0]+Math.cos(a)*r,150+(k*37)%70,LAKEC[1]+Math.sin(a)*r);G.add(s);MS.sats.push(s)}
   const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(36),3));
   const l=new THREE.LineSegments(g,new THREE.LineBasicMaterial({color:0x9fd8ff,transparent:true,opacity:.28,depthWrite:false}));l.frustumCulled=false;G.add(l);MS.gl=l;
   const N=6*6;const g2=new THREE.BufferGeometry();g2.setAttribute('position',new THREE.BufferAttribute(new Float32Array(N*3),3));const C2=new Float32Array(N*3),A2=new Float32Array(N).fill(1);for(let i=0;i<N;i++)C2.set([.75,.92,1.],i*3);
   g2.setAttribute('col',new THREE.BufferAttribute(C2,3));g2.setAttribute('al',new THREE.BufferAttribute(A2,1));const pk=new THREE.Points(g2,MS.hpMat);pk.frustumCulled=false;G.add(pk);MS.pk=pk}
  /* floating obstacles (drift log, duck family, debris cluster) */
  {const mk2=(r,build)=>{const o={grp:new THREE.Group(),p:[0,0],v:[0,0],r,fade:1};build(o.grp);G.add(o.grp);MS.obs.push(o);return o};
   mk2(1.4,g=>{const m=new THREE.Mesh(new THREE.CylinderGeometry(.22,.26,2.4,10),new THREE.MeshLambertMaterial({color:C(0x5a4632)}));m.rotation.z=Math.PI/2;m.position.y=.05;g.add(m)});
   mk2(1.6,g=>{const bm=new THREE.MeshLambertMaterial({color:C(0x8a6b4a)}),hm=new THREE.MeshLambertMaterial({color:C(0x2f5a2a)});[[0,0,1],[-.7,.35,.6],[-.8,-.4,.6],[-1.4,0,.6]].forEach(d=>{
     const b=new THREE.Mesh(new THREE.SphereGeometry(.2*d[2]+.05,10,8),bm);b.scale.set(1.5,.8,1);b.position.set(d[0],.08,d[1]);g.add(b);const h=new THREE.Mesh(new THREE.SphereGeometry(.09*d[2]+.03,8,6),hm);h.position.set(d[0]+.28*d[2],.25*d[2]+.05,d[1]);g.add(h)})});
   mk2(1.5,g=>{const cols=[0xe8eef2,0x3f8fd8,0xd94a3a,0xf2d24a,0x7a8a3a];for(let i=0;i<9;i++){const m=new THREE.Mesh(new THREE.BoxGeometry(R(.15,.4),R(.08,.2),R(.15,.5)),new THREE.MeshLambertMaterial({color:C(cols[i%5])}));m.position.set(R(-.9,.9),.03,R(-.7,.7));m.rotation.y=R(0,3);g.add(m)}});
   const or=new THREE.Mesh(new THREE.RingGeometry(1,1.12,40),msMat(0xff4d5e,.9));or.rotation.x=-Math.PI/2;or.visible=false;G.add(or);MS.oring=or;
   MS.alertLbl=addLabel(()=>T('obsLbl'),0,2.6,0,'module','boat');MS.alertLbl.hidden=true}
}
function cellOf(p){const g=MS.grid;return [clamp(Math.round((p[0]-g.x0)/g.cs),0,g.nx-1),clamp(Math.round((p[1]-g.z0)/g.cs),0,g.nz-1)]}
function cellW(i,j){const g=MS.grid;return [g.x0+i*g.cs,g.z0+j*g.cs]}
function nearValid(c){const g=MS.grid;if(g.v[c[1]*g.nx+c[0]])return c;for(let r=1;r<20;r++)for(let dj=-r;dj<=r;dj++)for(let di=-r;di<=r;di++){const i=c[0]+di,j=c[1]+dj;if(i>=0&&j>=0&&i<g.nx&&j<g.nz&&g.v[j*g.nx+i])return [i,j]}return c}
function nearValidLOS(p){/* 시야가 트인(직선 이동 가능한) 가장 가까운 유효 셀 — 데크 너머 셀을 잡지 않게 */const g=MS.grid,c=cellOf(p);if(g.v[c[1]*g.nx+c[0]]&&boatPath(p,cellW(c[0],c[1])))return c;
  for(let r=1;r<12;r++){let best=null,bd=1e9;for(let dj=-r;dj<=r;dj++)for(let di=-r;di<=r;di++){if(Math.max(Math.abs(di),Math.abs(dj))!==r)continue;const i=c[0]+di,j=c[1]+dj;if(i<0||j<0||i>=g.nx||j>=g.nz||!g.v[j*g.nx+i])continue;
    const w=cellW(i,j),d=Math.hypot(w[0]-p[0],w[1]-p[1]);if(d<bd&&boatPath(p,w)){bd=d;best=[i,j]}}if(best)return best}return nearValid(c)}
function astar(pa,pb){const g=MS.grid,nx=g.nx,N=nx*g.nz;const s=nearValidLOS(pa),e=nearValidLOS(pb);const si=s[1]*nx+s[0],ei=e[1]*nx+e[0];
  const gs=new Float32Array(N).fill(1e9),from=new Int32Array(N).fill(-1),cl=new Uint8Array(N),via=new Map();const h=[];const push=(i,f)=>{h.push([f,i]);let k=h.length-1;while(k>0){const p=(k-1)>>1;if(h[p][0]<=h[k][0])break;[h[p],h[k]]=[h[k],h[p]];k=p}};
  const pop=()=>{const t=h[0],l=h.pop();if(h.length){h[0]=l;let k=0;for(;;){const a=2*k+1,b=a+1;let m=k;if(a<h.length&&h[a][0]<h[m][0])m=a;if(b<h.length&&h[b][0]<h[m][0])m=b;if(m===k)break;[h[m],h[k]]=[h[k],h[m]];k=m}}return t};
  const ex=e[0],ez=e[1];gs[si]=0;push(si,0);
  while(h.length){const [,c]=pop();if(c===ei)break;if(cl[c])continue;cl[c]=1;const ci=c%nx,cj=(c/nx)|0;
    for(let dj=-1;dj<=1;dj++)for(let di=-1;di<=1;di++){if(!di&&!dj)continue;const i=ci+di,j=cj+dj;if(i<0||j<0||i>=nx||j>=g.nz)continue;const n=j*nx+i;if(!g.v[n]||cl[n])continue;
      const w=gs[c]+(di&&dj?1.4142:1);if(w<gs[n]){gs[n]=w;from[n]=c;via.delete(n);push(n,w+Math.hypot(i-ex,j-ez))}}
    const gl=MS.gateMap&&MS.gateMap.get(c);if(gl)for(const L of gl){const n=L.to;if(cl[n])continue;const w=gs[c]+L.cost;if(w<gs[n]){gs[n]=w;from[n]=c;via.set(n,L.pts);push(n,w+Math.hypot(n%nx-ex,((n/nx)|0)-ez))}}}   /* 데크 횡단 = 게이트 링크만 */
  const out=[];let c=ei;if(from[c]<0&&c!==si)return [pa,pb];while(c>=0){out.push(cellW(c%nx,(c/nx)|0));if(via.has(c)){const vp=via.get(c);out.push(vp[2],vp[1],vp[0])}if(c===si)break;c=from[c]}out.reverse();out[0]=pa;out.push(pb);
  /* string pulling */
  const sp=[out[0]];let i=0;while(i<out.length-1){let j=Math.min(out.length-1,i+40);while(j>i+1&&!boatPath(out[i],out[j]))j--;sp.push(out[j]);i=j}return sp}
function densify(pts,out){for(let k=0;k<pts.length-1;k++){const a=pts[k],b=pts[k+1],L=Math.hypot(b[0]-a[0],b[1]-a[1]),n=Math.max(1,Math.ceil(L/2));for(let t=0;t<n;t++)out.push([a[0]+(b[0]-a[0])*t/n,a[1]+(b[1]-a[1])*t/n])}}
function splitSeg(a,b){/* 레인을 0.5 m 간격으로 검사해 데크 밑·기둥 구간에서 끊음 */const L=Math.hypot(b[0]-a[0],b[1]-a[1]),n=Math.max(1,Math.ceil(L/0.5)),out=[];let st=null,last=null;
  for(let k=0;k<=n;k++){const q=[a[0]+(b[0]-a[0])*k/n,a[1]+(b[1]-a[1])*k/n];if(boatValid(q)){if(!st)st=q;last=q}else{if(st&&Math.hypot(last[0]-st[0],last[1]-st[1])>=4)out.push([st,last]);st=null}}
  if(st&&Math.hypot(last[0]-st[0],last[1]-st[1])>=4)out.push([st,last]);return out}
function routeOK(r){/* 연결 경로 전 구간이 수면·기둥 이격·데크 통로 규칙을 지키는지 0.5 m 단위 확인(못 지키면 그 레인은 건너뜀) */for(let i=0;i<r.length-1;i++){const a=r[i],b=r[i+1],n=Math.max(1,Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/0.5));
  for(let k=0;k<=n;k++){const q=[a[0]+(b[0]-a[0])*k/n,a[1]+(b[1]-a[1])*k/n];if(!inPoly(q,LAKE)||!deckOK(q,false))return false}}return true}
function computePath(pass){const g=MS.grid,vert=pass%2===1,segs=[];const NA=vert?g.nx:g.nz,NB=vert?g.nz:g.nx;
  for(let L=2;L<NA;L+=4){let run=null;for(let k=0;k<=NB;k++){const i=vert?L:k,j=vert?k:L;const ok=k<NB&&g.v[j*g.nx+i];if(ok&&!run)run=[k,k];else if(ok)run[1]=k;
      if(!ok&&run){if(run[1]-run[0]>=2)splitSeg(vert?cellW(L,run[0]):cellW(run[0],L),vert?cellW(L,run[1]):cellW(run[1],L)).forEach(sg=>segs.push(sg));run=null}}}
  (MS.gates||[]).forEach(gt=>{const s=[gt.A,gt.B];s.gate=gt;segs.push(s)});   /* 기둥 주변 세정: 모든 게이트 포함 */
  let cur=[BOAT.pos.x,BOAT.pos.y];const pts=[];const used=new Uint8Array(segs.length);const hard=new Set();
  for(let n=0;n<segs.length;n++){let bi=-1,be=0,bd=1e9;segs.forEach((s,i)=>{if(used[i])return;for(let e=0;e<2;e++){const d=Math.hypot(s[e][0]-cur[0],s[e][1]-cur[1]);if(d<bd){bd=d;bi=i;be=e}}});
    used[bi]=1;const s=segs[bi],a=s[be],b=s[1-be];const con=boatPath(cur,a)?[cur,a]:astar(cur,a);if(!routeOK(con))continue;densify(con,pts);
    if(s.gate){const Gp=s.gate.G,seq=[a,Gp,b,Gp,a,Gp,b];for(let q=0;q<seq.length-1;q++){hard.add(pts.length);densify([seq[q],seq[q+1]],pts)}hard.add(pts.length);pts.push([b[0],b[1]])}else densify([a,b],pts);cur=b}   /* 게이트는 3회 왕복 통과 */
  pts.push(cur);MS.path=pts;MS.hard=hard;MS.pi=0;let len=0;for(let k=1;k<pts.length;k++)len+=Math.hypot(pts[k][0]-pts[k-1][0],pts[k][1]-pts[k-1][1]);MS.len=len;
  const cov=new Uint8Array(g.nx*g.nz),rc=Math.floor(BOAT.R*.9/g.cs);pts.forEach((p,k)=>{if(k%2)return;const c=cellOf(p);for(let dj=-rc;dj<=rc;dj++)for(let di=-rc;di<=rc;di++){if(di*di+dj*dj>rc*rc)continue;const i=c[0]+di,j=c[1]+dj;if(i>=0&&j>=0&&i<g.nx&&j<g.nz)cov[j*g.nx+i]=1}});
  let nv=0,nc=0;for(let i=0;i<cov.length;i++)if(g.v[i]){nv++;if(cov[i])nc++}MS.cov=Math.round(nc/Math.max(1,nv)*100);
  const P=MS.pl.geometry.attributes.position.array,Cc=MS.pl.geometry.attributes.color.array,n=Math.min(pts.length-1,MS.plN),W=0.45;
  for(let k=0;k<n;k++){const a=pts[k],b=pts[k+1];let dx=b[0]-a[0],dz=b[1]-a[1];const L=Math.hypot(dx,dz)||1;const ox=-dz/L*W,oz=dx/L*W;
    const V=[a[0]+ox,a[1]+oz,a[0]-ox,a[1]-oz,b[0]+ox,b[1]+oz,a[0]-ox,a[1]-oz,b[0]-ox,b[1]-oz,b[0]+ox,b[1]+oz];
    const w=k%6<3?1:.7;for(let v=0;v<6;v++){P[(k*6+v)*3]=V[v*2];P[(k*6+v)*3+1]=-0.36;P[(k*6+v)*3+2]=V[v*2+1];Cc[(k*6+v)*3]=.22*w;Cc[(k*6+v)*3+1]=.62*w;Cc[(k*6+v)*3+2]=.7*w}}
  MS.plSeg=n;MS.pl.geometry.attributes.position.needsUpdate=true;MS.pl.geometry.attributes.color.needsUpdate=true;MS.pl.geometry.setDrawRange(0,0);MS.pl.visible=true}
function msSteps(){document.querySelectorAll('#boatBody [data-ms]').forEach(e=>{const k=+e.dataset.ms;e.dataset.st=k<MS.ph?'done':k===MS.ph?'on':''})}
function missionStart(){if(!MS.G)return;MS.man=null;MS.inGate=null;(MS.gates||[]).forEach(g=>{g.passes=0;g.side=0});stReset();MS.rec=null;MS.prog=null;MS.stuckN=0;MS.G.visible=true;MS.pl.material.opacity=.7;MS.shore.material.opacity=.95;MS.nogo.forEach(o=>o.material.opacity=o.userData.line?.9:.6);MS.ph=1;MS.t=0;MS.pass=0;MS.avoid=null;MS.encT=0;MS.su.uScan.value=0;MS.su.uFade.value=1;MS.shore.geometry.setDrawRange(0,0);
  MS.nogo.forEach(o=>{o.visible=false;o.scale.set(1,1,1)});MS.pl.visible=false;MS.oring.visible=false;MS.alertLbl.hidden=true;
  const a=[BOAT.pos.x,BOAT.pos.y];MS.obs.forEach((o,k)=>{for(let t=0;t<200;t++){const s=PUR.samples[(Math.random()*PUR.samples.length)|0];if(boatValid([s[0],s[2]])&&Math.hypot(s[0]-a[0],s[2]-a[1])>40){o.p=[s[0],s[2]];break}}const an=Math.random()*6.283;o.v=[Math.cos(an)*.18,Math.sin(an)*.18]});
  flyTo([LAKEC[0]+30,250,LAKEC[1]+220],[LAKEC[0],0,LAKEC[1]],1800,48);msSteps()}
function missionHide(){MS.man=null;if(SFX.ready)SFX.master.gain.setTargetAtTime(0,SFX.ctx.currentTime,.2);const r=$('#rc');if(r)r.hidden=true;if(MS.G)MS.G.visible=false;if(MS.alertLbl)MS.alertLbl.hidden=true;MS.ph=0}
function missionStep(dt,sdt){if(!MS.G)return false;MS.t+=dt;const tot=MS.path.length;
  if(MS.ph===1){const s=Math.min(1,MS.t/7);MS.su.uScan.value=s;const sz=MS.su.uZ0.value+(MS.su.uZ1.value-MS.su.uZ0.value)*s;
    MS.shore.geometry.setDrawRange(0,Math.floor(MS.shoreN*s));MS.nogo.forEach(o=>{if(!o.visible&&o.userData.z<sz){o.visible=true;o.userData.t0=MS.t}if(o.visible&&!o.userData.line){const k=Math.min(1,(MS.t-o.userData.t0)/.5);const sc=1+.6*Math.sin(k*Math.PI)*(1-k);o.scale.set(sc,sc,sc)}});
    $('#boatMsg').textContent=s<1?T('ms1',{p:Math.round(s*100)}):T('ms1done',{a:Math.round(MS.area).toLocaleString(),n:MS.nogo.length});
    BOAT.v*=.95;if(MS.t>8.5){MS.ph=2;MS.t=0;computePath(MS.pass);msSteps()}return false}
  if(MS.ph===2){const k=Math.min(1,MS.t/4);MS.pl.geometry.setDrawRange(0,Math.floor(MS.plSeg*k)*6);MS.su.uFade.value=1-.7*k;
    $('#boatMsg').textContent=T('ms2',{pat:T(MS.pass%2?'patV':'patH'),L:Math.round(MS.len).toLocaleString(),C:MS.cov});
    BOAT.v*=.95;if(MS.t>5.5){MS.ph=3;MS.t=0;BOAT.follow=true;const fb=$('#bFollow');if(fb)fb.setAttribute('aria-pressed','true');msSteps();if(typeof hudMin==='function'&&!MS.userHud)hudMin(true)}return false}
  if(MS.ph!==3)return false;
  {const k=Math.min(1,dt*.8);MS.su.uFade.value+=(0.06-MS.su.uFade.value)*k;MS.pl.material.opacity+=(0.32-MS.pl.material.opacity)*k;
   MS.shore.material.opacity+=(0.3-MS.shore.material.opacity)*k;MS.nogo.forEach(o=>{o.material.opacity+=((o.userData.line?0.35:0.22)-o.material.opacity)*k})}   /* 운항 중엔 경로·호안선·금지구역을 은은하게 */   /* 운항 중엔 인식 격자를 옅게 → 수면이 잘 보이게 */
  const PW=MS.path,pos=[BOAT.pos.x,BOAT.pos.y];while(MS.pi<tot-1){const hd=MS.hard&&MS.hard.has(MS.pi);if(Math.hypot(pos[0]-PW[MS.pi][0],pos[1]-PW[MS.pi][1])<(hd?1.3:4))MS.pi++;else break}   /* 게이트 왕복 꼭짓점은 반드시 도달 */
  if(MS.pi>=tot-1&&Math.hypot(pos[0]-PW[tot-1][0],pos[1]-PW[tot-1][1])<4){MS.pass++;MS.ph=2;MS.t=0;computePath(MS.pass);msSteps();return false}
  if(MS.man)return manualStep(dt,pos);
  if(!MS.prog)MS.prog={t:0,x:pos[0],z:pos[1]};MS.prog.t+=sdt;
  if(MS.prog.t>6){if(!MS.rec&&Math.hypot(pos[0]-MS.prog.x,pos[1]-MS.prog.z)<1.5)startRecover(pos);MS.prog={t:0,x:pos[0],z:pos[1]}}   /* 6초간 1.5 m 미만 이동 = 고착 */
  if(MS.rec)return recoverStep(dt,sdt,pos);
  let tg=(MS.hard&&MS.hard.has(MS.pi))?PW[MS.pi]:PW[Math.min(MS.pi+1,tot-1)];const fx=Math.cos(BOAT.hd),fz=Math.sin(BOAT.hd);
  /* LiDAR-based avoidance of floating obstacles */
  if(!MS.avoid){for(const o of MS.obs){const dx=o.p[0]-pos[0],dz=o.p[1]-pos[1],d=Math.hypot(dx,dz)-o.r;if(d>10||o.fade<1)continue;const ang=Math.atan2(dx*fz-dz*fx,dx*fx+dz*fz);
      if(Math.abs(ang)<.75){MS.avoid={o,side:ang>0?1:-1,d,flip:0};break}}}
  let slow=1;if(MS.avoid){const A=MS.avoid,o=A.o,dx=o.p[0]-pos[0],dz=o.p[1]-pos[1];let dd=Math.hypot(dx,dz);A.d=Math.max(0,dd-o.r);const ux=dx/dd,uz=dz/dd;
    let px=-uz*A.side,pz=ux*A.side;/* side: steer to the opposite side of the obstacle bearing */
    let c=[o.p[0]-px*(o.r+4.5)+ux*2,o.p[1]-pz*(o.r+4.5)+uz*2];if(!boatValid(c)&&A.flip<1){A.side*=-1;A.flip++;c=[o.p[0]+px*(o.r+4.5)+ux*2,o.p[1]+pz*(o.r+4.5)+uz*2]}
    if(boatValid(c))tg=c;else slow=.35;
    A.t=(A.t||0)+sdt;if(dd<o.r+2.4){const e=[pos[0]-ux*6+px*2,pos[1]-uz*6+pz*2];if(boatValid(e)){tg=e;slow=.7}}   /* 너무 가까우면 후진·비켜서 간격 확보 */
    if(A.t>25){let q=null;for(let k=0;k<80&&!q;k++){const s=PUR.samples[(Math.random()*PUR.samples.length)|0];if(boatValid([s[0],s[2]])&&Math.hypot(s[0]-pos[0],s[2]-pos[1])>45)q=[s[0],s[2]]}if(q){o.p=q;o.fade=0}dd=99}   /* 장기 교착 시 장애물이 흘러감 */
    if((dx*fx+dz*fz)<-1&&dd>o.r+3||dd>17){MS.avoid=null;let bi=MS.pi,bd=1e9;for(let k=MS.pi;k<Math.min(tot,MS.pi+40);k++){const d=Math.hypot(PW[k][0]-pos[0],PW[k][1]-pos[1]);if(d<bd){bd=d;bi=k}}MS.pi=bi}
    else slow*=.7}
  if(gateWatch(pos))slow*=.5;   /* 게이트 서행 통과 */
  const des=Math.atan2(tg[1]-pos[1],tg[0]-pos[0]);let dh=des-BOAT.hd;dh=Math.atan2(Math.sin(dh),Math.cos(dh));BOAT.hd+=clamp(dh,-.6*sdt,.6*sdt);
  const vt=BOAT.base*slow*(1-Math.min(Math.abs(dh)/1.3,.8));BOAT.v+=(vt-BOAT.v)*Math.min(1,sdt*.8);if(MS.inGate)BOAT.v=Math.min(BOAT.v,BOAT.base*.5);
  const nx=pos[0]+Math.cos(BOAT.hd)*BOAT.v*sdt,nz=pos[1]+Math.sin(BOAT.hd)*BOAT.v*sdt;let blocked=false;for(const o of MS.obs){const dn=Math.hypot(nx-o.p[0],nz-o.p[1]),dc=Math.hypot(pos[0]-o.p[0],pos[1]-o.p[1]);if(dn<o.r+1&&dn<dc)blocked=true}   /* 장애물에 더 다가가는 이동만 차단(멀어지는 이동 허용) */
  if(!blocked&&subOK(pos,[nx,nz])){BOAT.pos.set(nx,nz);MS.stuck=0}else{BOAT.v*=.3;MS.stuck+=sdt;if(MS.stuck>4){MS.pi=Math.min(tot-1,MS.pi+3);MS.stuck=0}}
  /* bring a drifting obstacle onto the route now and then (to exercise avoidance) */
  MS.encT+=sdt;if(MS.encT>50&&!MS.avoid&&MS.pi+16<tot){let far=null,fd=60;MS.obs.forEach(o=>{const d=Math.hypot(o.p[0]-pos[0],o.p[1]-pos[1]);if(d>fd){fd=d;far=o}});
    const q=PW[MS.pi+15];if(far&&boatValid(q)){far.p=[q[0],q[1]];far.fade=0;MS.encT=0}}
  MS.tCol+=dt;if(MS.tCol>.4){MS.tCol=0;const Cc=MS.pl.geometry.attributes.color.array;for(let k=0;k<Math.min(MS.pi,MS.plN)*6;k++){Cc[k*3]=0;Cc[k*3+1]=0;Cc[k*3+2]=0}MS.pl.geometry.attributes.color.needsUpdate=true}
  return true}


/* ---- 게이트 서행·통과 횟수·시네마틱 ---- */
function gateWatch(pos){let best=null,bd=1e9;for(const g of MS.gates||[]){const d=Math.hypot(g.G[0]-pos[0],g.G[1]-pos[1]);if(d<bd){bd=d;best=g}}
  if(!best||bd>best.hw+3.5){if(MS.inGate)MS.inGate.g.side=0;MS.inGate=null;return false}
  const nx=best.B[0]-best.A[0],nz=best.B[1]-best.A[1],sd=Math.sign((pos[0]-best.G[0])*nx+(pos[1]-best.G[1])*nz)||1;
  if(best.side&&sd!==best.side)best.passes++;best.side=sd;MS.inGate={g:best,d:bd};return true}
const _cp=new THREE.Vector3(),_ct=new THREE.Vector3();
function cineCam(dt){const ig=MS.inGate;const lb=$('#cineLB');
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
/* ---- 리모콘 수동 조종 ---- */
const RC={up:false,down:false,left:false,right:false,stop:false,jx:0,jy:0};const RC_TIMEOUT=5000;
function rcActive(){return RC.up||RC.down||RC.left||RC.right||RC.stop||Math.hypot(RC.jx,RC.jy)>.08}
function rcInput(){if(!BOAT.on||MS.ph!==3)return;const now=performance.now();if(!MS.man){MS.man={last:now,v:BOAT.v,warn:0,tm:0};MS.rec=null;MS.avoid=null;BOAT.follow=true;const fb=$('#bFollow');if(fb)fb.setAttribute('aria-pressed','true');rcUi()}else MS.man.last=now}
function rcRelease(){MS.man=null;MS.prog=null;const tot=MS.path.length,pos=[BOAT.pos.x,BOAT.pos.y];let k=MS.pi,bd=1e9;
  for(let i=Math.max(0,MS.pi-10);i<Math.min(tot,MS.pi+60);i++){const d=Math.hypot(MS.path[i][0]-pos[0],MS.path[i][1]-pos[1]);if(d<bd-1e-6){bd=d;k=i}}   /* 우선 현재 구간 근처에서 재개 */
  if(bd>25){for(let i=MS.pi;i<tot;i++){const d=Math.hypot(MS.path[i][0]-pos[0],MS.path[i][1]-pos[1]);if(d<bd-1e-6){bd=d;k=i}}}   /* 멀리 벗어났으면 남은 경로 중 가장 가까운 지점 */
  MS.pi=Math.min(tot-1,k);MS.rcBackT=performance.now();rcUi()}
function rcMsg(){const M=MS.man;if(!M)return '';const idle=performance.now()-M.last;if(M.warn>performance.now())return T('msRcWall');
  return rcActive()||idle<800?T('msManual'):T('msRcIdle',{s:Math.max(0,Math.ceil((RC_TIMEOUT-idle)/1000))})}
function rcUi(){const el=$('#rc');if(!el)return;el.classList.toggle('man',!!MS.man);$('#rcSt').textContent=MS.man?T('rcManual'):T('rcAuto')}
function manualStep(dt,pos){const M=MS.man,now=performance.now();if(rcActive())M.last=now;
  if(now-M.last>RC_TIMEOUT){rcRelease();return true}   /* 리모콘 신호 끊김 → 자율 복귀 */
  const s=dt*Math.min(BOAT.speed,3);   /* 수동 조종은 최대 ×3 배속 */
  const jOn=Math.hypot(RC.jx,RC.jy)>.08;const turn=clamp((RC.left?-1:0)+(RC.right?1:0)+(jOn?RC.jx:0),-1,1);BOAT.hd+=turn*.85*s;   /* 조이스틱: 좌우=선회(아날로그) */
  const vt=RC.stop?0:RC.up?BOAT.base:RC.down?-.6:(jOn&&Math.abs(RC.jy)>.12)?(RC.jy<0?BOAT.base*-RC.jy:-.6*RC.jy):BOAT.v*.97;   /* 위=전진·아래=후진(밀어낸 만큼 속도) */BOAT.v+=(vt-BOAT.v)*Math.min(1,s*1.2);
  const fx=Math.cos(BOAT.hd),fz=Math.sin(BOAT.hd);
  if(BOAT.v>0)for(const o of MS.obs){const dx=o.p[0]-pos[0],dz=o.p[1]-pos[1],d=Math.hypot(dx,dz);if(d<o.r+2.2&&(dx*fx+dz*fz)>0){BOAT.v=0;M.warn=now+1200}}   /* LiDAR 자동 정지 */
  const nx=pos[0]+fx*BOAT.v*s,nz=pos[1]+fz*BOAT.v*s;
  if(subOK(pos,[nx,nz]))BOAT.pos.set(nx,nz);else{BOAT.v=0;M.warn=now+1200}   /* 수면 밖·구조물 앞 정지 */
  if(gateWatch(pos))BOAT.v=clamp(BOAT.v,-.3,BOAT.base*.5);   /* 리모콘도 게이트 서행 */
  M.tm+=dt;if(M.tm>.25){M.tm=0;const m=$('#boatMsg');if(m)m.textContent=rcMsg()}
  return true}
/* ---- 고착 감지·탈출 루틴 ---- */
function subOK(a,b){/* 고배속에서도 기둥·데크·호안을 뛰어넘지 않게 0.4 m 단위로 검사 */if(!boatSoft(a))return true;const L=Math.hypot(b[0]-a[0],b[1]-a[1]),n=Math.max(1,Math.ceil(L/0.4));for(let k=1;k<=n;k++){if(!boatSoft([a[0]+(b[0]-a[0])*k/n,a[1]+(b[1]-a[1])*k/n]))return false}return true}
function boatSoft(p){if(!inPoly(p,LAKE)||edgeDist(p,LAKE)<2.2)return false;for(const f of FOUNT)if(Math.hypot(p[0]-f[0],p[1]-f[1])<4)return false;
  return deckOK(p,false)}
function clearCell(i,j){const g=MS.grid;for(let dj=-1;dj<=1;dj++)for(let di=-1;di<=1;di++){const a=i+di,b=j+dj;if(a<0||b<0||a>=g.nx||b>=g.nz||!g.v[b*g.nx+a])return false}return true}
function startRecover(pos){const g=MS.grid,c=cellOf(pos);let best=null,bd=1e9;
  for(let j=Math.max(0,c[1]-10);j<=Math.min(g.nz-1,c[1]+10);j++)for(let i=Math.max(0,c[0]-10);i<=Math.min(g.nx-1,c[0]+10);i++){if(!clearCell(i,j))continue;const w=cellW(i,j),d=Math.hypot(w[0]-pos[0],w[1]-pos[1]);if(d>4&&d<bd){bd=d;best=w}}
  if(!best){const s=PUR.samples.find(s=>boatValid([s[0],s[2]]));best=s?[s[0],s[2]]:[LAKEC[0],LAKEC[1]]}
  const same=MS.stuckAt&&Math.hypot(MS.stuckAt[0]-pos[0],MS.stuckAt[1]-pos[1])<8;MS.stuckN=same?(MS.stuckN||0)+1:1;MS.stuckAt=[pos[0],pos[1]];
  MS.rec={ph:'back',t:0,goal:best,route:astar(pos,best),ri:1,tt:0};MS.avoid=null}
function recoverStep(dt,sdt,pos){const R=MS.rec,tot=MS.path.length;R.t+=sdt;R.tt+=sdt;
  if(R.ph==='back'){const bx=pos[0]-Math.cos(BOAT.hd)*.5*sdt,bz=pos[1]-Math.sin(BOAT.hd)*.5*sdt;if(boatSoft([bx,bz]))BOAT.pos.set(bx,bz);BOAT.v=-.5;if(R.t>3){R.ph='go';R.t=0;BOAT.v=0}return false}
  const tg=R.route[Math.min(R.ri,R.route.length-1)];if(Math.hypot(tg[0]-pos[0],tg[1]-pos[1])<2.5)R.ri++;
  if(R.ri>=R.route.length){/* 탈출 완료 → 경로 복귀(같은 곳 반복 고착이면 그 구간 건너뜀) */
    let k=MS.pi,bd=1e9;for(let i=MS.pi;i<Math.min(tot,MS.pi+80);i++){const d=Math.hypot(MS.path[i][0]-pos[0],MS.path[i][1]-pos[1]);if(d<bd){bd=d;k=i}}
    if(MS.stuckN>=2){while(k<tot-1&&Math.hypot(MS.path[k][0]-MS.stuckAt[0],MS.path[k][1]-MS.stuckAt[1])<16)k++}
    MS.pi=k;MS.rec=null;MS.prog=null;return true}
  const des=Math.atan2(tg[1]-pos[1],tg[0]-pos[0]);let dh=des-BOAT.hd;dh=Math.atan2(Math.sin(dh),Math.cos(dh));BOAT.hd+=clamp(dh,-.9*sdt,.9*sdt);
  const vt=BOAT.base*.8*(1-Math.min(Math.abs(dh)/1.4,.85));BOAT.v+=(vt-BOAT.v)*Math.min(1,sdt*.8);
  const nx=pos[0]+Math.cos(BOAT.hd)*BOAT.v*sdt,nz=pos[1]+Math.sin(BOAT.hd)*BOAT.v*sdt;
  if(subOK(pos,[nx,nz]))BOAT.pos.set(nx,nz);
  else if(R.tt>14){const d=Math.hypot(tg[0]-pos[0],tg[1]-pos[1])||1,s=Math.min(d,.6*sdt);BOAT.pos.set(pos[0]+(tg[0]-pos[0])/d*s,pos[1]+(tg[1]-pos[1])/d*s)}   /* 최후 수단: 탈출 지점으로 서서히 이동 */
  return true}
/* 2D ray cast against shoreline, decks, fixed structures and floating obstacles */
function segHit(ox,oz,dx,dz,a,b){const ex=b[0]-a[0],ez=b[1]-a[1],den=dx*ez-dz*ex;if(Math.abs(den)<1e-9)return 1e9;const t=((a[0]-ox)*ez-(a[1]-oz)*ex)/den,u=((a[0]-ox)*dz-(a[1]-oz)*dx)/den;return t>0&&u>=0&&u<=1?t:1e9}
function cirHit(ox,oz,dx,dz,c,r){const fx=ox-c[0],fz=oz-c[1],b=fx*dx+fz*dz,cc=fx*fx+fz*fz-r*r,h=b*b-cc;if(h<0)return 1e9;const t=-b-Math.sqrt(h);return t>0?t:1e9}
function lidarRay(ox,oz,a,maxR){const dx=Math.cos(a),dz=Math.sin(a);let t=maxR,ty=0;
  for(let i=0;i<LAKE.length-1;i++){const h=segHit(ox,oz,dx,dz,LAKE[i],LAKE[i+1]);if(h<t){t=h;ty=1}}
  for(const q of DECK_PILES){if(Math.abs(q[0]-ox)>maxR+1||Math.abs(q[1]-oz)>maxR+1)continue;const h=cirHit(ox,oz,dx,dz,q,.2);if(h<t){t=h;ty=2}}   /* 수면 높이 = 데크 기둥 */
  for(const f of FOUNT){const h=cirHit(ox,oz,dx,dz,f,2.5);if(h<t){t=h;ty=2}}for(const s of SENS){const h=cirHit(ox,oz,dx,dz,s.p,.7);if(h<t){t=h;ty=2}}
  for(const o of MS.obs){const h=cirHit(ox,oz,dx,dz,o.p,o.r*.8);if(h<t){t=h;ty=3}}return ty?[ox+dx*t,oz+dz*t,ty,t]:null}
const LCOL=[null,[.35,.9,1.],[1.,.82,.35],[1.,.3,.36]];
function updateSensorsViz(dt){if(!MS.G||!MS.G.visible)return;const bx=BOAT.pos.x,bz=BOAT.pos.y,Tm=U.time.value,sdt=dt*BOAT.speed;
  /* floating obstacles drift */
  MS.obs.forEach((o,k)=>{const nx=o.p[0]+o.v[0]*sdt,nz=o.p[1]+o.v[1]*sdt;const db=Math.hypot(o.p[0]-bx,o.p[1]-bz);if(db<o.r+3.5){const ax=(o.p[0]-bx)/(db||1),az=(o.p[1]-bz)/(db||1);o.v=[ax*.4,az*.4]}   /* 보트가 다가오면 물결에 밀려 비켜남 */
    if(boatValid([nx,nz])&&Math.hypot(nx-bx,nz-bz)>o.r+1.2)o.p=[nx,nz];else{const an=Math.random()*6.283;o.v=[Math.cos(an)*.18,Math.sin(an)*.18]}
    o.fade=Math.min(1,o.fade+dt*.8);const s=o.fade;o.grp.scale.set(s,s,s);o.grp.position.set(o.p[0],-0.5+.03*Math.sin(Tm*1.6+k*2),o.p[1]);o.grp.rotation.y=-Math.atan2(o.v[1],o.v[0])});
  {const r=$('#rc');if(r){const sh=BOAT.on&&MS.ph===3;if(r.hidden===sh)r.hidden=!sh}}
  sfxUpdate(dt);
  if(MS.shadowM){const d=skyU.uSun.value,k=Math.min(1.25/Math.max(d.y,.08),14),op=SUN_EL>.04?.3*(1-SUN_NIGHT):0;MS.shadowM.forEach(m=>{m.position.set(-d.x*k,0,-d.z*k);m.material.opacity=op;m.visible=op>.01})}   /* 시간대별 데크 그림자 */
  /* LiDAR */
  MS.ang+=dt*12.566;MS.fan.position.set(bx,-0.28,bz);MS.fan.rotation.y=-MS.ang;MS.rr.position.set(bx,-0.32,bz);
  const hp=MS.hp,P=hp.g.attributes.position.array,Cc=hp.g.attributes.col.array,A=hp.g.attributes.al.array;let near=99,nh=0;
  for(let k=0;k<28;k++){const a=MS.ang+k*(6.2832/28)+Math.random()*.2;const h=lidarRay(bx,bz,a,15);if(!h)continue;const i=hp.head;hp.head=(hp.head+1)%hp.N;
    P[i*3]=h[0]+R(-.1,.1);P[i*3+1]=h[2]===3?-0.25+Math.random()*.35:-0.3+Math.random()*.5;P[i*3+2]=h[1]+R(-.1,.1);Cc.set(LCOL[h[2]],i*3);hp.L[i]=1.3;if(h[2]===3){near=Math.min(near,h[3]);nh++}}
  for(let i=0;i<hp.N;i++){if(hp.L[i]>0){hp.L[i]-=dt;A[i]=Math.max(0,hp.L[i]/1.3)}else A[i]=0}
  ['position','col','al'].forEach(k=>hp.g.attributes[k].needsUpdate=true);MS.near=near;
  /* avoidance marker */
  const av=MS.avoid;MS.oring.visible=!!av;MS.alertLbl.hidden=!av;if(av){const r=av.o.r+.6;MS.oring.scale.set(r,r,r);MS.oring.position.set(av.o.p[0],-0.3,av.o.p[1]);MS.oring.material.opacity=.55+.4*Math.sin(Tm*10);MS.alertLbl.v.set(av.o.p[0],2.6,av.o.p[1])}
  /* GNSS downlink */
  const mast=[bx,0.9,bz],GP=MS.gl.geometry.attributes.position.array,PP=MS.pk.geometry.attributes.position.array;
  MS.sats.forEach((s,k)=>{s.rotation.y=Tm*.05+k;GP.set([s.position.x,s.position.y,s.position.z,mast[0],mast[1],mast[2]],k*6);
    for(let j=0;j<6;j++){const t=(Tm*.45+j/6+k*.13)%1;PP.set([s.position.x+(mast[0]-s.position.x)*t,s.position.y+(mast[1]-s.position.y)*t,s.position.z+(mast[2]-s.position.z)*t],(k*6+j)*3)}});
  MS.gl.geometry.attributes.position.needsUpdate=true;MS.pk.geometry.attributes.position.needsUpdate=true;MS.gl.material.opacity=.2+.12*Math.sin(Tm*4);
  /* telemetry */
  MS.tTel+=dt;if(MS.tTel>.25){MS.tTel=0;const lat=GEO.lat-bz/111320,lon=GEO.lon+bx/(111320*Math.cos(GEO.lat*Math.PI/180));
    const e1=$('#bGnss'),e2=$('#bLidar');if(e1)e1.textContent=T('gnssLn',{n:9+((Tm/7|0)%3),lat:(lat+R(-1,1)*1e-7).toFixed(6),lon:(lon+R(-1,1)*1e-7).toFixed(6),h:(0.7+0.1*Math.sin(Tm*.3)).toFixed(1)});
    if(e2)e2.textContent=T('lidarLn',{n:nh,d:near<99?near.toFixed(1)+' m':'—'});const e3=$('#bUva');if(e3){const pc=Math.round((MS.uva||0)*100);e3.textContent=T(pc>=90?'uvaBoost':'uvaLn',{p:pc});e3.parentNode.classList.toggle('boost',pc>=90)}}}
