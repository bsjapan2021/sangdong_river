/* ================= 녹조제거 쌍동선 (AQUA-NANO BOT) =================
   STL(1.6 m, 면 색상) → 호수 수면에서만 자율운항. 녹조 밀집 구역 우선 탐색, 전방 다공 UFB 박스에서
   마이크로·나노버블 분사 + 광촉매 ROS 생성, 지나간 자리의 녹조를 마스크로 제거(서서히 재성장). 개념 시각화. */
const BOAT={on:false,speed:10,base:1.5,pos:new THREE.Vector2(-20,10),hd:0,v:0,target:null,follow:false,grp:null,lbl:null,
  mask:null,ctx:null,tex:null,box:null,stat:null,lakePix:null,pct:0,t:0,tStat:0,tRegrow:0,frame:0,R:9};
function buildBoat(){
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
    fragmentShader:pFS+`uniform sampler2D uAtlas;varying float vA,vK;void main(){`+pFE+`vec4 c=texture2D(uAtlas,vec2(gl_PointCoord.x*.25,gl_PointCoord.y));
      float r=length(gl_PointCoord-.5);float soft=smoothstep(.5,0.,r);vec3 col=vec3(.85,.98,1.);float a=c.a;
      if(vK>1.5&&vK<2.5){a=soft*.8;col=vec3(1.);}if(vK>2.5){a=soft;col=mix(vec3(.72,.95,1.),vec3(.8,.5,1.),step(3.5,vK));col=mix(col,vec3(1.),smoothstep(.18,0.,r)*.7);}
      if(a*vA<.01)discard;gl_FragColor=vec4(col*a,a*vA);}`});
  const pts=new THREE.Points(g,m);pts.frustumCulled=false;pts.visible=false;scene.add(pts);
  BOAT.pp={P,A,SZ,K,V:new Float32Array(NP*3),L:new Float32Array(NP),AG:new Float32Array(NP),N:NP,head:0,geo:g,pts};
}
function bSpawn(x,y,z,vx,vy,vz,life,size,kind){const p=BOAT.pp;const i=p.head;p.head=(p.head+1)%p.N;p.P[i*3]=x;p.P[i*3+1]=y;p.P[i*3+2]=z;p.V[i*3]=vx;p.V[i*3+1]=vy;p.V[i*3+2]=vz;p.L[i]=life;p.AG[i]=0;p.SZ[i]=size;p.K[i]=kind}
function cleanAt(x,z){if(!BOAT.stat)return 0;const i=Math.floor((x-BOAT.box[0])*BOAT.box[2]),j=Math.floor((z-BOAT.box[1])*BOAT.box[3]);if(i<0||j<0||i>=BOAT.S||j>=BOAT.S)return 0;return BOAT.stat[(j*BOAT.S+i)*4]/255}
/* navigation: water only (lake polygon, shore margin), avoid fountains, buoys, outlets, lake decks/pier */
const deckSegs=[];let MODE='pur';
function boatValid(p){if(!inPoly(p,LAKE)||edgeDist(p,LAKE)<5.5)return false;for(const f of FOUNT)if(Math.hypot(p[0]-f[0],p[1]-f[1])<8)return false;
  for(const s of SENS)if(Math.hypot(p[0]-s.p[0],p[1]-s.p[1])<4.5)return false;for(const u of UNITS)if(Math.hypot(p[0]-u.ret[0],p[1]-u.ret[1])<6||Math.hypot(p[0]-u.int[0],p[1]-u.int[1])<6)return false;for(const s of deckSegs)if(segDist(p,s[0],s[1])<5)return false;return true}
function boatPath(a,b){const L=Math.hypot(b[0]-a[0],b[1]-a[1]);const n=Math.max(2,Math.ceil(L/2));for(let k=1;k<=n;k++){const t=k/n;if(!boatValid([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]))return false}return true}
function boatPick(){const a=[BOAT.pos.x,BOAT.pos.y];let best=null,bs=-1e9;
  for(let k=0;k<40;k++){const s=PUR.samples[(Math.random()*PUR.samples.length)|0];const p=[s[0],s[2]];if(!boatValid(p))continue;const d=Math.hypot(p[0]-a[0],p[1]-a[1]);if(d<12)continue;
    let dirt=0;for(let j=0;j<5;j++){const ang=j*1.2566;dirt+=1-cleanAt(p[0]+Math.cos(ang)*6,p[1]+Math.sin(ang)*6)}dirt=dirt/5+(1-cleanAt(p[0],p[1]));
    const sc=dirt*1.6-d/120+Math.random()*.15;if(sc>bs&&boatPath(a,p)){bs=sc;best=p}}
  if(!best){for(let k=0;k<60&&!best;k++){const s=PUR.samples[(Math.random()*PUR.samples.length)|0];const p=[s[0],s[2]];if(boatValid(p)&&boatPath(a,p))best=p}}
  BOAT.target=best}
function boatReset(){const c=BOAT.ctx;c.globalCompositeOperation='source-over';c.fillStyle='#000';c.fillRect(0,0,BOAT.S,BOAT.S);BOAT.tex.needsUpdate=true;BOAT.stat=c.getImageData(0,0,BOAT.S,BOAT.S).data;
  let st=[-20,10];if(!boatValid(st))for(const s of PUR.samples){if(boatValid([s[0],s[2]])){st=[s[0],s[2]];break}}BOAT.pos.set(st[0],st[1]);BOAT.hd=0;BOAT.v=0;BOAT.target=null;BOAT.pct=0;
  const p=BOAT.pp;p.L.fill(0);p.A.fill(0)}
function boatSetOn(on){BOAT.on=on;if(!BOAT.grp)return;BOAT.grp.visible=on;BOAT.pp.pts.visible=on;BOAT.lbl.hidden=!on;PUR.u.uMaskOn.value=on?1:0;BOAT.follow=on;const fb=$('#bFollow');if(fb)fb.setAttribute('aria-pressed',String(on));if(on)boatReset()}
const _bt=new THREE.Vector3(),_bc=new THREE.Vector3();
function updateBoat(dt){if(!BOAT.on||!BOAT.grp)return;const sp=BOAT.speed,sdt=dt*sp;BOAT.t+=dt;
  BOAT.cd=(BOAT.cd||0)-dt;if((!BOAT.target||Math.hypot(BOAT.target[0]-BOAT.pos.x,BOAT.target[1]-BOAT.pos.y)<3)&&BOAT.cd<=0){boatPick();if(!BOAT.target)BOAT.cd=.4}
  if(!BOAT.target){BOAT.hd+=.4*sdt;BOAT.v*=.9}
  if(BOAT.target){const des=Math.atan2(BOAT.target[1]-BOAT.pos.y,BOAT.target[0]-BOAT.pos.x);let dh=des-BOAT.hd;dh=Math.atan2(Math.sin(dh),Math.cos(dh));
    const turn=clamp(dh,-.55*sdt,.55*sdt);BOAT.hd+=turn;const vt=BOAT.base*(1-Math.min(Math.abs(dh)/1.3,.75));BOAT.v+=(vt-BOAT.v)*Math.min(1,sdt*.8);
    const nx=BOAT.pos.x+Math.cos(BOAT.hd)*BOAT.v*sdt,nz=BOAT.pos.y+Math.sin(BOAT.hd)*BOAT.v*sdt;
    if(boatValid([nx,nz])||!boatValid([BOAT.pos.x,BOAT.pos.y]))BOAT.pos.set(nx,nz);else{BOAT.target=null;BOAT.v*=.3}}
  const T0=BOAT.t,fx=Math.cos(BOAT.hd),fz=Math.sin(BOAT.hd),rx=-fz,rz=fx;
  const g=BOAT.grp;g.position.set(BOAT.pos.x,-0.5+.025*Math.sin(T0*2.1),BOAT.pos.y);g.rotation.set(0,-BOAT.hd,0);BOAT.body.rotation.set(.018*Math.sin(T0*1.7),0,.012*Math.sin(T0*1.3+1));
  BOAT.ring.material.opacity=.45+.3*Math.sin(T0*3);BOAT.lbl.v.set(BOAT.pos.x,3.4,BOAT.pos.y);PUR.u.uBoat.value.set(BOAT.pos.x+fx*.7,BOAT.pos.y+fz*.7,BOAT.hd);
  /* emission (scaled gently with playback speed) */
  const em=Math.sqrt(sp);const bx=BOAT.pos.x+fx*.7,bz=BOAT.pos.y+fz*.7;
  for(let k=0;k<Math.round(4*em);k++){const sd=Math.random()<.5?-1:1,lat=R(.6,2.2)*sd,fwd=R(-.6,.3);bSpawn(bx+rx*.22*sd,-0.45,bz+rz*.22*sd,rx*lat+fx*fwd,0,rz*lat+fz*fwd,R(4,8),R(.08,.22),1)}
  for(let k=0;k<Math.round(3*em);k++){const a=Math.random()*6.283,s=R(.2,1.2);bSpawn(bx+R(-.2,.2),-0.85,bz+R(-.2,.2),Math.cos(a)*s,R(.05,.25),Math.sin(a)*s,R(4,7),R(.05,.16),0)}
  for(let k=0;k<Math.round(2*em);k++){const sd=Math.random()<.5?-1:1;const sx=BOAT.pos.x-fx*.8+rx*.3*sd,sz=BOAT.pos.y-fz*.8+rz*.3*sd;bSpawn(sx,-0.44,sz,-fx*.4+rx*R(-.25,.25)*sd,0,-fz*.4+rz*R(-.25,.25)*sd,R(3,5),R(.25,.5),2)}
  for(let k=0;k<Math.round(3*em);k++){const a=Math.random()*6.283,r0=R(.5,7);bSpawn(bx+Math.cos(a)*r0,R(-2.4,-0.6),bz+Math.sin(a)*r0,R(-.2,.2),R(-.05,.1),R(-.2,.2),R(.6,1.6),R(.12,.26),Math.random()<.55?3:4)}
  /* integrate particles */
  const p=BOAT.pp;for(let i=0;i<p.N;i++){if(p.L[i]<=0){p.A[i]=0;continue}p.AG[i]+=dt;const t=p.AG[i];if(t>=p.L[i]){p.L[i]=0;p.A[i]=0;continue}
    const k=p.K[i],dk=Math.exp(-dt*(k===0?.5:k===1?.35:.9));p.V[i*3]*=dk;p.V[i*3+2]*=dk;if(k===0){p.V[i*3+1]+=dt*.12;}
    p.P[i*3]+=p.V[i*3]*dt;p.P[i*3+1]+=p.V[i*3+1]*dt;p.P[i*3+2]+=p.V[i*3+2]*dt;if(k===0&&p.P[i*3+1]>-0.56){p.P[i*3+1]=-0.56;p.V[i*3+1]=0}
    const lf=t/p.L[i];p.A[i]=(k>2.5?Math.pow(.5+.5*Math.sin(t*25+i),2):1)*Math.min(1,t*4)*(1-lf)*(k===2?.55:1)}
  ['position','al','sz','kd'].forEach(a=>p.geo.attributes[a].needsUpdate=true);
  /* paint the clean mask (accumulates where the plume passes), slow regrowth */
  const c=BOAT.ctx,S=BOAT.S,px=(bx-BOAT.box[0])*BOAT.box[2],pz=(bz-BOAT.box[1])*BOAT.box[3],rp=BOAT.R*BOAT.box[2];
  c.globalCompositeOperation='lighter';const gr=c.createRadialGradient(px,pz,0,px,pz,rp);const al=Math.min(1,sdt*.5);gr.addColorStop(0,`rgba(255,255,255,${al})`);gr.addColorStop(.6,`rgba(255,255,255,${al*.6})`);gr.addColorStop(1,'rgba(255,255,255,0)');
  c.fillStyle=gr;c.beginPath();c.arc(px,pz,rp,0,7);c.fill();
  BOAT.tRegrow+=sdt;if(BOAT.tRegrow>20){BOAT.tRegrow=0;c.globalCompositeOperation='source-over';c.fillStyle='rgba(0,0,0,0.02)';c.fillRect(0,0,S,S)}
  if((++BOAT.frame)%3===0)BOAT.tex.needsUpdate=true;
  BOAT.tStat+=dt;if(BOAT.tStat>.8||!BOAT.stat){BOAT.tStat=0;BOAT.stat=c.getImageData(0,0,S,S).data;let k2=0;for(const ix of BOAT.lakePix)if(BOAT.stat[ix*4]>150)k2++;BOAT.pct=Math.round(k2/BOAT.lakePix.length*100);
    const hb=$('#boatBar');if(hb){hb.style.width=BOAT.pct+'%';$('#boatPct').textContent=BOAT.pct+'%';$('#boatMsg').textContent=BOAT.pct>=90?T('boatDone'):T('boatRun',{v:(BOAT.v).toFixed(1)})}}
  /* follow camera */
  if(BOAT.follow&&!fly){const k=1-Math.exp(-dt*2.2);_bt.set(BOAT.pos.x,-0.3,BOAT.pos.y);_bc.set(BOAT.pos.x-fx*11+rx*5,5,BOAT.pos.y-fz*11+rz*5);controls.target.lerp(_bt,k);camera.position.lerp(_bc,k)}
}
