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
  buildMission();
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
function boatSetOn(on){BOAT.on=on;if(!BOAT.grp)return;BOAT.grp.visible=on;BOAT.pp.pts.visible=on;BOAT.lbl.hidden=!on;PUR.u.uMaskOn.value=on?1:0;BOAT.follow=false;const fb=$('#bFollow');if(fb)fb.setAttribute('aria-pressed','false');if(on){boatReset();missionStart()}else missionHide()}
const _bt=new THREE.Vector3(),_bc=new THREE.Vector3();
function updateBoat(dt){if(!BOAT.on||!BOAT.grp)return;const sp=BOAT.speed,sdt=dt*sp;BOAT.t+=dt;
  const run=missionStep(dt,sdt);
  const T0=BOAT.t,fx=Math.cos(BOAT.hd),fz=Math.sin(BOAT.hd),rx=-fz,rz=fx;
  const g=BOAT.grp;g.position.set(BOAT.pos.x,-0.5+.025*Math.sin(T0*2.1),BOAT.pos.y);g.rotation.set(0,-BOAT.hd,0);BOAT.body.rotation.set(.018*Math.sin(T0*1.7),0,.012*Math.sin(T0*1.3+1));
  BOAT.ring.material.opacity=.45+.3*Math.sin(T0*3);BOAT.lbl.v.set(BOAT.pos.x,3.4,BOAT.pos.y);PUR.u.uBoat.value.set(BOAT.pos.x+fx*.7,BOAT.pos.y+fz*.7,BOAT.hd);
  /* emission (scaled gently with playback speed) */
  const em=run?Math.sqrt(sp):0;const bx=BOAT.pos.x+fx*.7,bz=BOAT.pos.y+fz*.7;
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
  if(run){c.globalCompositeOperation='lighter';const gr=c.createRadialGradient(px,pz,0,px,pz,rp);const al=Math.min(1,sdt*.5);gr.addColorStop(0,`rgba(255,255,255,${al})`);gr.addColorStop(.6,`rgba(255,255,255,${al*.6})`);gr.addColorStop(1,'rgba(255,255,255,0)');
  c.fillStyle=gr;c.beginPath();c.arc(px,pz,rp,0,7);c.fill()}
  BOAT.tRegrow+=sdt;if(BOAT.tRegrow>20){BOAT.tRegrow=0;c.globalCompositeOperation='source-over';c.fillStyle='rgba(0,0,0,0.02)';c.fillRect(0,0,S,S)}
  if((++BOAT.frame)%3===0)BOAT.tex.needsUpdate=true;
  BOAT.tStat+=dt;if(BOAT.tStat>.8||!BOAT.stat){BOAT.tStat=0;BOAT.stat=c.getImageData(0,0,S,S).data;let k2=0;for(const ix of BOAT.lakePix)if(BOAT.stat[ix*4]>150)k2++;BOAT.pct=Math.round(k2/BOAT.lakePix.length*100);
    const hb=$('#boatBar');if(hb){hb.style.width=BOAT.pct+'%';$('#boatPct').textContent=BOAT.pct+'%';if(MS.ph===3)$('#boatMsg').textContent=MS.avoid?T('msAvoid',{d:MS.avoid.d.toFixed(1)}):BOAT.pct>=90?T('boatDone'):T('boatRun',{v:(BOAT.v).toFixed(1)})}}
  /* follow camera */
  updateSensorsViz(dt);
  if(BOAT.follow&&!fly&&MS.ph===3){const k=1-Math.exp(-dt*2.2);_bt.set(BOAT.pos.x+fx*7,-0.3,BOAT.pos.y+fz*7);_bc.set(BOAT.pos.x-fx*12+rx*5,7.5,BOAT.pos.y-fz*12+rz*5);   /* 보트를 화면 아래쪽에 → 상단 패널에 가리지 않음 */controls.target.lerp(_bt,k);camera.position.lerp(_bc,k)}
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
  const v=new Uint8Array(nx*nz);for(let j=0;j<nz;j++)for(let i=0;i<nx;i++)v[j*nx+i]=boatValid([x0+i*cs,z0+j*cs])?1:0;MS.grid={cs,x0,z0,nx,nz,v};
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
function astar(pa,pb){const g=MS.grid,nx=g.nx,N=nx*g.nz;const s=nearValid(cellOf(pa)),e=nearValid(cellOf(pb));const si=s[1]*nx+s[0],ei=e[1]*nx+e[0];
  const gs=new Float32Array(N).fill(1e9),from=new Int32Array(N).fill(-1),cl=new Uint8Array(N);const h=[];const push=(i,f)=>{h.push([f,i]);let k=h.length-1;while(k>0){const p=(k-1)>>1;if(h[p][0]<=h[k][0])break;[h[p],h[k]]=[h[k],h[p]];k=p}};
  const pop=()=>{const t=h[0],l=h.pop();if(h.length){h[0]=l;let k=0;for(;;){const a=2*k+1,b=a+1;let m=k;if(a<h.length&&h[a][0]<h[m][0])m=a;if(b<h.length&&h[b][0]<h[m][0])m=b;if(m===k)break;[h[m],h[k]]=[h[k],h[m]];k=m}}return t};
  const ex=e[0],ez=e[1];gs[si]=0;push(si,0);
  while(h.length){const [,c]=pop();if(c===ei)break;if(cl[c])continue;cl[c]=1;const ci=c%nx,cj=(c/nx)|0;
    for(let dj=-1;dj<=1;dj++)for(let di=-1;di<=1;di++){if(!di&&!dj)continue;const i=ci+di,j=cj+dj;if(i<0||j<0||i>=nx||j>=g.nz)continue;const n=j*nx+i;if(!g.v[n]||cl[n])continue;
      const w=gs[c]+(di&&dj?1.4142:1);if(w<gs[n]){gs[n]=w;from[n]=c;push(n,w+Math.hypot(i-ex,j-ez))}}}
  const out=[];let c=ei;if(from[c]<0&&c!==si)return [pa,pb];while(c>=0){out.push(cellW(c%nx,(c/nx)|0));if(c===si)break;c=from[c]}out.reverse();out[0]=pa;out.push(pb);
  /* string pulling */
  const sp=[out[0]];let i=0;while(i<out.length-1){let j=Math.min(out.length-1,i+40);while(j>i+1&&!boatPath(out[i],out[j]))j--;sp.push(out[j]);i=j}return sp}
function densify(pts,out){for(let k=0;k<pts.length-1;k++){const a=pts[k],b=pts[k+1],L=Math.hypot(b[0]-a[0],b[1]-a[1]),n=Math.max(1,Math.ceil(L/2));for(let t=0;t<n;t++)out.push([a[0]+(b[0]-a[0])*t/n,a[1]+(b[1]-a[1])*t/n])}}
function computePath(pass){const g=MS.grid,vert=pass%2===1,segs=[];const NA=vert?g.nx:g.nz,NB=vert?g.nz:g.nx;
  for(let L=2;L<NA;L+=4){let run=null;for(let k=0;k<=NB;k++){const i=vert?L:k,j=vert?k:L;const ok=k<NB&&g.v[j*g.nx+i];if(ok&&!run)run=[k,k];else if(ok)run[1]=k;
      if(!ok&&run){if(run[1]-run[0]>=2)segs.push(vert?[cellW(L,run[0]),cellW(L,run[1])]:[cellW(run[0],L),cellW(run[1],L)]);run=null}}}
  let cur=[BOAT.pos.x,BOAT.pos.y];const pts=[];const used=new Uint8Array(segs.length);
  for(let n=0;n<segs.length;n++){let bi=-1,be=0,bd=1e9;segs.forEach((s,i)=>{if(used[i])return;for(let e=0;e<2;e++){const d=Math.hypot(s[e][0]-cur[0],s[e][1]-cur[1]);if(d<bd){bd=d;bi=i;be=e}}});
    used[bi]=1;const s=segs[bi],a=s[be],b=s[1-be];const con=boatPath(cur,a)?[cur,a]:astar(cur,a);densify(con,pts);densify([a,b],pts);cur=b}
  pts.push(cur);MS.path=pts;MS.pi=0;let len=0;for(let k=1;k<pts.length;k++)len+=Math.hypot(pts[k][0]-pts[k-1][0],pts[k][1]-pts[k-1][1]);MS.len=len;
  const cov=new Uint8Array(g.nx*g.nz),rc=Math.floor(BOAT.R*.9/g.cs);pts.forEach((p,k)=>{if(k%2)return;const c=cellOf(p);for(let dj=-rc;dj<=rc;dj++)for(let di=-rc;di<=rc;di++){if(di*di+dj*dj>rc*rc)continue;const i=c[0]+di,j=c[1]+dj;if(i>=0&&j>=0&&i<g.nx&&j<g.nz)cov[j*g.nx+i]=1}});
  let nv=0,nc=0;for(let i=0;i<cov.length;i++)if(g.v[i]){nv++;if(cov[i])nc++}MS.cov=Math.round(nc/Math.max(1,nv)*100);
  const P=MS.pl.geometry.attributes.position.array,Cc=MS.pl.geometry.attributes.color.array,n=Math.min(pts.length-1,MS.plN),W=0.45;
  for(let k=0;k<n;k++){const a=pts[k],b=pts[k+1];let dx=b[0]-a[0],dz=b[1]-a[1];const L=Math.hypot(dx,dz)||1;const ox=-dz/L*W,oz=dx/L*W;
    const V=[a[0]+ox,a[1]+oz,a[0]-ox,a[1]-oz,b[0]+ox,b[1]+oz,a[0]-ox,a[1]-oz,b[0]-ox,b[1]-oz,b[0]+ox,b[1]+oz];
    const w=k%6<3?1:.7;for(let v=0;v<6;v++){P[(k*6+v)*3]=V[v*2];P[(k*6+v)*3+1]=-0.36;P[(k*6+v)*3+2]=V[v*2+1];Cc[(k*6+v)*3]=.22*w;Cc[(k*6+v)*3+1]=.62*w;Cc[(k*6+v)*3+2]=.7*w}}
  MS.plSeg=n;MS.pl.geometry.attributes.position.needsUpdate=true;MS.pl.geometry.attributes.color.needsUpdate=true;MS.pl.geometry.setDrawRange(0,0);MS.pl.visible=true}
function msSteps(){document.querySelectorAll('#boatBody [data-ms]').forEach(e=>{const k=+e.dataset.ms;e.dataset.st=k<MS.ph?'done':k===MS.ph?'on':''})}
function missionStart(){if(!MS.G)return;MS.G.visible=true;MS.pl.material.opacity=.7;MS.shore.material.opacity=.95;MS.nogo.forEach(o=>o.material.opacity=o.userData.line?.9:.6);MS.ph=1;MS.t=0;MS.pass=0;MS.avoid=null;MS.encT=0;MS.su.uScan.value=0;MS.su.uFade.value=1;MS.shore.geometry.setDrawRange(0,0);
  MS.nogo.forEach(o=>{o.visible=false;o.scale.set(1,1,1)});MS.pl.visible=false;MS.oring.visible=false;MS.alertLbl.hidden=true;
  const a=[BOAT.pos.x,BOAT.pos.y];MS.obs.forEach((o,k)=>{for(let t=0;t<200;t++){const s=PUR.samples[(Math.random()*PUR.samples.length)|0];if(boatValid([s[0],s[2]])&&Math.hypot(s[0]-a[0],s[2]-a[1])>40){o.p=[s[0],s[2]];break}}const an=Math.random()*6.283;o.v=[Math.cos(an)*.18,Math.sin(an)*.18]});
  flyTo([LAKEC[0]+30,250,LAKEC[1]+220],[LAKEC[0],0,LAKEC[1]],1800,48);msSteps()}
function missionHide(){if(MS.G)MS.G.visible=false;if(MS.alertLbl)MS.alertLbl.hidden=true;MS.ph=0}
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
  const PW=MS.path,pos=[BOAT.pos.x,BOAT.pos.y];while(MS.pi<tot-1&&Math.hypot(pos[0]-PW[MS.pi][0],pos[1]-PW[MS.pi][1])<4)MS.pi++;
  if(MS.pi>=tot-1&&Math.hypot(pos[0]-PW[tot-1][0],pos[1]-PW[tot-1][1])<4){MS.pass++;MS.ph=2;MS.t=0;computePath(MS.pass);msSteps();return false}
  let tg=PW[Math.min(MS.pi+1,tot-1)];const fx=Math.cos(BOAT.hd),fz=Math.sin(BOAT.hd);
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
  const des=Math.atan2(tg[1]-pos[1],tg[0]-pos[0]);let dh=des-BOAT.hd;dh=Math.atan2(Math.sin(dh),Math.cos(dh));BOAT.hd+=clamp(dh,-.6*sdt,.6*sdt);
  const vt=BOAT.base*slow*(1-Math.min(Math.abs(dh)/1.3,.8));BOAT.v+=(vt-BOAT.v)*Math.min(1,sdt*.8);
  const nx=pos[0]+Math.cos(BOAT.hd)*BOAT.v*sdt,nz=pos[1]+Math.sin(BOAT.hd)*BOAT.v*sdt;let blocked=false;for(const o of MS.obs){const dn=Math.hypot(nx-o.p[0],nz-o.p[1]),dc=Math.hypot(pos[0]-o.p[0],pos[1]-o.p[1]);if(dn<o.r+1&&dn<dc)blocked=true}   /* 장애물에 더 다가가는 이동만 차단(멀어지는 이동 허용) */
  if(!blocked&&(boatValid([nx,nz])||!boatValid(pos))){BOAT.pos.set(nx,nz);MS.stuck=0}else{BOAT.v*=.3;MS.stuck+=sdt;if(MS.stuck>4){MS.pi=Math.min(tot-1,MS.pi+3);MS.stuck=0}}
  /* bring a drifting obstacle onto the route now and then (to exercise avoidance) */
  MS.encT+=sdt;if(MS.encT>50&&!MS.avoid&&MS.pi+16<tot){let far=null,fd=60;MS.obs.forEach(o=>{const d=Math.hypot(o.p[0]-pos[0],o.p[1]-pos[1]);if(d>fd){fd=d;far=o}});
    const q=PW[MS.pi+15];if(far&&boatValid(q)){far.p=[q[0],q[1]];far.fade=0;MS.encT=0}}
  MS.tCol+=dt;if(MS.tCol>.4){MS.tCol=0;const Cc=MS.pl.geometry.attributes.color.array;for(let k=0;k<Math.min(MS.pi,MS.plN)*6;k++){Cc[k*3]=0;Cc[k*3+1]=0;Cc[k*3+2]=0}MS.pl.geometry.attributes.color.needsUpdate=true}
  return true}
/* 2D ray cast against shoreline, decks, fixed structures and floating obstacles */
function segHit(ox,oz,dx,dz,a,b){const ex=b[0]-a[0],ez=b[1]-a[1],den=dx*ez-dz*ex;if(Math.abs(den)<1e-9)return 1e9;const t=((a[0]-ox)*ez-(a[1]-oz)*ex)/den,u=((a[0]-ox)*dz-(a[1]-oz)*dx)/den;return t>0&&u>=0&&u<=1?t:1e9}
function cirHit(ox,oz,dx,dz,c,r){const fx=ox-c[0],fz=oz-c[1],b=fx*dx+fz*dz,cc=fx*fx+fz*fz-r*r,h=b*b-cc;if(h<0)return 1e9;const t=-b-Math.sqrt(h);return t>0?t:1e9}
function lidarRay(ox,oz,a,maxR){const dx=Math.cos(a),dz=Math.sin(a);let t=maxR,ty=0;
  for(let i=0;i<LAKE.length-1;i++){const h=segHit(ox,oz,dx,dz,LAKE[i],LAKE[i+1]);if(h<t){t=h;ty=1}}
  for(const s of deckSegs){const h=segHit(ox,oz,dx,dz,s[0],s[1]);if(h<t){t=h;ty=2}}
  for(const f of FOUNT){const h=cirHit(ox,oz,dx,dz,f,2.5);if(h<t){t=h;ty=2}}for(const s of SENS){const h=cirHit(ox,oz,dx,dz,s.p,.7);if(h<t){t=h;ty=2}}
  for(const o of MS.obs){const h=cirHit(ox,oz,dx,dz,o.p,o.r*.8);if(h<t){t=h;ty=3}}return ty?[ox+dx*t,oz+dz*t,ty,t]:null}
const LCOL=[null,[.35,.9,1.],[1.,.82,.35],[1.,.3,.36]];
function updateSensorsViz(dt){if(!MS.G||!MS.G.visible)return;const bx=BOAT.pos.x,bz=BOAT.pos.y,Tm=U.time.value,sdt=dt*BOAT.speed;
  /* floating obstacles drift */
  MS.obs.forEach((o,k)=>{const nx=o.p[0]+o.v[0]*sdt,nz=o.p[1]+o.v[1]*sdt;const db=Math.hypot(o.p[0]-bx,o.p[1]-bz);if(db<o.r+3.5){const ax=(o.p[0]-bx)/(db||1),az=(o.p[1]-bz)/(db||1);o.v=[ax*.4,az*.4]}   /* 보트가 다가오면 물결에 밀려 비켜남 */
    if(boatValid([nx,nz])&&Math.hypot(nx-bx,nz-bz)>o.r+1.2)o.p=[nx,nz];else{const an=Math.random()*6.283;o.v=[Math.cos(an)*.18,Math.sin(an)*.18]}
    o.fade=Math.min(1,o.fade+dt*.8);const s=o.fade;o.grp.scale.set(s,s,s);o.grp.position.set(o.p[0],-0.5+.03*Math.sin(Tm*1.6+k*2),o.p[1]);o.grp.rotation.y=-Math.atan2(o.v[1],o.v[0])});
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
    if(e2)e2.textContent=T('lidarLn',{n:nh,d:near<99?near.toFixed(1)+' m':'—'})}}
