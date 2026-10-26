/* ================= purification animation (UFB 정화 연출) =================
   환수부 2곳에서 마이크로·나노버블이 분사되어 호수 전역으로 정화 전선(R)이 서서히 확산.
   수면: 녹조·혐기성 슬러지 막이 걷히고, 수중: 세균·곰팡이·조류 입자가 소멸하고 나노버블 헤이즈가 채워짐.
   개념 시각화(연출)이며 실측·수치해석 결과가 아님. */
const PUR={on:true,cycle:48,grow:34,hold:6,maxR:170,R:0,regrow:0,u:{},samples:[],skyMesh:null,aboveFog:null,under:false};
function lakeSample(n,y0,y1){const xs=LAKE.map(p=>p[0]),zs=LAKE.map(p=>p[1]);const x0=Math.min(...xs),x1=Math.max(...xs),z0=Math.min(...zs),z1=Math.max(...zs);
  const out=[];let g=0;while(out.length<n&&g<n*20){g++;const p=[R(x0,x1),R(z0,z1)];if(!inPoly(p,LAKE)||edgeDist(p,LAKE)<1.2)continue;out.push([p[0],R(y0,y1),p[1]])}return out}
function microbeAtlas(){return canvasTex(256,64,(x,w,h)=>{x.clearRect(0,0,w,h);
  /* 0: bubble */ {const g=x.createRadialGradient(32,32,8,32,32,30);g.addColorStop(0,'rgba(255,255,255,0.05)');g.addColorStop(.72,'rgba(220,250,255,0.35)');g.addColorStop(.9,'rgba(255,255,255,0.95)');g.addColorStop(1,'rgba(255,255,255,0)');
    x.fillStyle=g;x.beginPath();x.arc(32,32,30,0,7);x.fill();x.fillStyle='rgba(255,255,255,.9)';x.beginPath();x.ellipse(23,22,6,4,-.6,0,7);x.fill()}
  /* 1: bacillus (rod) */ x.save();x.translate(96,32);x.rotate(.5);x.fillStyle='rgba(120,170,60,.95)';x.strokeStyle='rgba(60,90,30,1)';x.lineWidth=2;
    x.beginPath();x.moveTo(-18,-8);x.lineTo(18,-8);x.arc(18,0,8,-Math.PI/2,Math.PI/2);x.lineTo(-18,8);x.arc(-18,0,8,Math.PI/2,Math.PI*1.5);x.fill();x.stroke();
    x.strokeStyle='rgba(90,130,40,.9)';x.lineWidth=1.2;for(let i=0;i<8;i++){x.beginPath();x.moveTo(-26+i*7,(i%2?8:-8));x.quadraticCurveTo(-28+i*7,(i%2?20:-20),-22+i*7,(i%2?26:-26));x.stroke()}x.restore();
  /* 2: virus / coccus (spiky) */ x.save();x.translate(160,32);x.fillStyle='rgba(150,90,170,.95)';x.beginPath();x.arc(0,0,13,0,7);x.fill();x.strokeStyle='rgba(110,60,130,1)';x.lineWidth=2.4;
    for(let i=0;i<14;i++){const a=i/14*6.283;x.beginPath();x.moveTo(Math.cos(a)*12,Math.sin(a)*12);x.lineTo(Math.cos(a)*22,Math.sin(a)*22);x.stroke();x.beginPath();x.arc(Math.cos(a)*23,Math.sin(a)*23,2.6,0,7);x.fillStyle='rgba(190,120,200,1)';x.fill()}x.restore();
  /* 3: fungus / algae filament */ x.save();x.translate(224,32);x.strokeStyle='rgba(140,120,50,.95)';x.lineWidth=3;for(let k=0;k<5;k++){x.beginPath();x.moveTo(0,0);let px=0,py=0;for(let s=0;s<6;s++){px+=Math.cos(k*1.3+s*.5)*5;py+=Math.sin(k*1.3+s*.7)*5;x.lineTo(px,py)}x.stroke()}
    x.fillStyle='rgba(90,110,40,.95)';x.beginPath();x.arc(0,0,6,0,7);x.fill();x.restore()},{linear:false})}
const pVS=`#include <common>\n#include <logdepthbuf_pars_vertex>\n`;const pVE=`\n#include <logdepthbuf_vertex>\n`;
const pFS=`#include <common>\n#include <logdepthbuf_pars_fragment>\n`;const pFE=`\n#include <logdepthbuf_fragment>\n`;
function buildPurify(){
  const r1=UNITS[0].ret,r2=UNITS[1].ret;
  /* nozzle (underwater diffuser) at each return, aimed at the lake interior */
  const lc=(()=>{let x=0,z=0;LAKE.forEach(p=>{x+=p[0];z+=p[1]});return [x/LAKE.length,z/LAKE.length]})();
  PUR.nozzles=UNITS.map(u=>{const d=[lc[0]-u.ret[0],lc[1]-u.ret[1]];const l=Math.hypot(...d);return {p:u.ret,dir:[d[0]/l,d[1]/l]}});
  const U2={uTime:U.time,uR:{value:0},uRegrow:{value:0},uPoll:{value:1},uRet1:{value:new THREE.Vector2(r1[0],r1[1])},uRet2:{value:new THREE.Vector2(r2[0],r2[1])},
    uScale:{value:innerHeight/(2*Math.tan(camera.fov*Math.PI/360))},uAtlas:{value:microbeAtlas()},uUnder:{value:0},uSun:skyU.uSun};
  PUR.u=U2;const G=new THREE.Group();scene.add(G);PUR.group=G;
  const dfun=`float dRet(vec2 p){return min(distance(p,uRet1),distance(p,uRet2));}
    float h21(vec2 p){p=fract(p*vec2(123.34,456.21));p+=dot(p,p+45.32);return fract(p.x*p.y);}
    float vn(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h21(i),h21(i+vec2(1,0)),f.x),mix(h21(i+vec2(0,1)),h21(i+vec2(1,1)),f.x),f.y);}
    float fb(vec2 p){float a=0.,w=.5;for(int i=0;i<5;i++){a+=w*vn(p);p*=2.07;w*=.5;}return a;}`;
  const U2decl=`uniform float uTime,uR,uRegrow,uPoll,uScale,uUnder;uniform vec2 uRet1,uRet2;uniform sampler2D uAtlas;uniform vec3 uSun;`;

  /* ---- 1. surface: algae scum / anaerobic sludge film + advancing purification front ---- */
  {const g=new THREE.ShapeGeometry(shapeOf(LAKE),2);g.rotateX(-Math.PI/2);
   const m=new THREE.ShaderMaterial({uniforms:U2,transparent:true,depthWrite:false,side:THREE.DoubleSide,
    vertexShader:pVS+`varying vec3 vW;void main(){vec4 w=modelMatrix*vec4(position,1.);vW=w.xyz;gl_Position=projectionMatrix*viewMatrix*w;`+pVE+`}`,
    fragmentShader:pFS+U2decl+dfun+`varying vec3 vW;void main(){`+pFE+`
      vec2 p=vW.xz;float t=uTime;
      float n=fb(p*.045+vec2(t*.01,-t*.006)),n2=fb(p*.16+vec2(-t*.02,t*.015)),n3=fb(p*.6);
      float wob=(fb(p*.03+t*.03)-.5)*18.;float d=dRet(p)+wob;
      vec3 algae=mix(vec3(.16,.30,.08),vec3(.42,.50,.12),n);
      algae=mix(algae,vec3(.10,.09,.05),smoothstep(.55,.72,n2));           /* anaerobic dark sludge */
      algae=mix(algae,vec3(.55,.58,.20),smoothstep(.62,.8,n3)*.6);          /* floating scum flecks */
      float cover=clamp(.55+.55*smoothstep(.3,.7,n*.8+n2*.4),0.,1.)*uPoll;
      float dirty=max(smoothstep(uR-10.,uR+3.,d),uRegrow);
      float ring=exp(-pow((d-uR)/3.2,2.))*step(.5,uR)*(1.-uRegrow);
      float foam=ring*(.55+.45*smoothstep(.35,.75,fb(p*.5+t*.4)));
      float inner=(1.-dirty)*smoothstep(uR,uR-30.,d)*(1.-uRegrow);
      float glint=pow(vn(p*3.+t*2.),18.)*inner*1.6;
      vec3 col=mix(algae,vec3(.85,.98,1.),clamp(foam*1.3,0.,1.));
      col+=vec3(.75,.95,1.)*glint;
      float a=cover*dirty*.92+foam*.85+glint*.8+inner*.06;
      col=mix(col,vec3(.55,.9,.95),inner*.25*(1.-dirty));
      if(uUnder>.5)a*=.55;
      gl_FragColor=vec4(col,clamp(a,0.,.95));}`});
   const mesh=new THREE.Mesh(g,m);mesh.position.y=-0.47;mesh.renderOrder=3;G.add(mesh)}

  /* ---- 2. surface jets: micro-bubble plumes fanning out from each return ---- */
  function surfaceJet(nz,N){const g=new THREE.BufferGeometry();const P=new Float32Array(N*3),A=new Float32Array(N*4);
    const base=Math.atan2(nz.dir[1],nz.dir[0]);
    for(let i=0;i<N;i++){A[i*4]=base+(rnd()-.5)*(rnd()<.75?1.6:3.2);A[i*4+1]=R(9,22);A[i*4+2]=rnd();A[i*4+3]=R(6,11)}
    g.setAttribute('position',new THREE.BufferAttribute(P,3));g.setAttribute('a',new THREE.BufferAttribute(A,4));
    const m=new THREE.ShaderMaterial({uniforms:U2,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
      vertexShader:pVS+U2decl+`attribute vec4 a;varying float vA;void main(){float L=a.w;float t=mod(uTime*1.0+a.z*L,L);float k=.45;
        float s=a.y*(1.-exp(-k*t))/k;float ang=a.x+.25*sin(t*.8+a.z*30.);vec3 p=vec3(cos(ang)*s,.06*sin(t*3.+a.z*40.),sin(ang)*s);
        p.y+=.25*exp(-t*2.);vA=(1.-t/L)*smoothstep(0.,.25,t);vec4 mv=modelViewMatrix*vec4(p,1.);
        gl_PointSize=(.22+.55*(1.-t/L))*uScale/-mv.z;gl_Position=projectionMatrix*mv;`+pVE+`}`,
      fragmentShader:pFS+`uniform sampler2D uAtlas;varying float vA;void main(){`+pFE+`vec2 uv=vec2(gl_PointCoord.x*.25,gl_PointCoord.y);vec4 c=texture2D(uAtlas,uv);
        gl_FragColor=vec4(vec3(.82,.97,1.)*c.a,c.a*vA*.9);}`});
    const pts=new THREE.Points(g,m);pts.position.set(nz.p[0],-0.42,nz.p[1]);pts.frustumCulled=false;G.add(pts);
    /* boil dome at the outlet */
    const boil=new THREE.Mesh(new THREE.CircleGeometry(3.2,32),new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.55,depthWrite:false}));
    boil.rotation.x=-Math.PI/2;boil.position.set(nz.p[0],-0.43,nz.p[1]);G.add(boil);PUR.boils=(PUR.boils||[]).concat(boil)}
  PUR.nozzles.forEach(nz=>surfaceJet(nz,2600));

  /* ---- 3. underwater: diffuser jets of rising micro-bubbles ---- */
  function underJet(nz,N){const g=new THREE.BufferGeometry();const P=new Float32Array(N*3),A=new Float32Array(N*4);const base=Math.atan2(nz.dir[1],nz.dir[0]);
    for(let i=0;i<N;i++){A[i*4]=base+(rnd()-.5)*.9;A[i*4+1]=R(5,13);A[i*4+2]=rnd();A[i*4+3]=R(5,9)}
    g.setAttribute('position',new THREE.BufferAttribute(P,3));g.setAttribute('a',new THREE.BufferAttribute(A,4));
    const m=new THREE.ShaderMaterial({uniforms:U2,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
      vertexShader:pVS+U2decl+`attribute vec4 a;varying float vA;void main(){float L=a.w;float t=mod(uTime+a.z*L,L);float k=.6;float s=a.y*(1.-exp(-k*t))/k;
        float rise=(.18+.5*fract(a.z*7.))*t+.03*t*t;vec3 p=vec3(cos(a.x)*s,min(rise,1.45),sin(a.x)*s);
        p.x+=.35*sin(t*2.+a.z*50.);p.z+=.35*cos(t*1.7+a.z*40.);
        vA=smoothstep(0.,.2,t)*(1.-smoothstep(L*.7,L,t))*(1.-smoothstep(1.3,1.45,rise));
        vec4 mv=modelViewMatrix*vec4(p,1.);gl_PointSize=min((.06+.22*fract(a.z*13.))*uScale/-mv.z,26.);vA*=mix(1.,exp(-length(mv.xyz)*.045),uUnder);gl_Position=projectionMatrix*mv;`+pVE+`}`,
      fragmentShader:pFS+`uniform sampler2D uAtlas;varying float vA;void main(){`+pFE+`vec4 c=texture2D(uAtlas,vec2(gl_PointCoord.x*.25,gl_PointCoord.y));gl_FragColor=vec4(vec3(.85,.98,1.)*c.a,c.a*vA);}`});
    const pts=new THREE.Points(g,m);pts.position.set(nz.p[0],-1.95,nz.p[1]);pts.frustumCulled=false;G.add(pts);
    /* diffuser nozzle head */
    const head=new THREE.Mesh(new THREE.CylinderGeometry(.35,.45,1.2,16),new THREE.MeshLambertMaterial({color:C(0x8a9399)}));head.rotation.z=Math.PI/2;head.rotation.y=-base;head.position.set(nz.p[0],-1.95,nz.p[1]);G.add(head)}
  PUR.nozzles.forEach(nz=>underJet(nz,2400));

  /* ---- 4. nano-bubble haze filling the purified volume ---- */
  {const S=lakeSample(7000,-3.0,-0.6);PUR.samples=S;const g=new THREE.BufferGeometry();const P=new Float32Array(S.length*3),A=new Float32Array(S.length);
   S.forEach((s,i)=>{P.set(s,i*3);A[i]=rnd()});g.setAttribute('position',new THREE.BufferAttribute(P,3));g.setAttribute('r',new THREE.BufferAttribute(A,1));
   const m=new THREE.ShaderMaterial({uniforms:U2,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
     vertexShader:pVS+U2decl+dfun+`attribute float r;varying float vA;void main(){vec3 p=position;p.y+=mod(uTime*.05+r*3.,2.)*.25;p.x+=.4*sin(uTime*.3+r*20.);
       float d=dRet(p.xz);float in_=1.-smoothstep(uR-4.,uR+2.,d);float tw=.55+.45*sin(uTime*3.+r*60.);vA=in_*tw*(1.-uRegrow)*(.35+.65*uUnder);
       vec4 mv=modelViewMatrix*vec4(p,1.);gl_PointSize=min((.05+.07*r)*uScale/-mv.z,9.);vA*=mix(1.,exp(-length(mv.xyz)*.04),uUnder);gl_Position=projectionMatrix*mv;`+pVE+`}`,
     fragmentShader:pFS+`uniform sampler2D uAtlas;varying float vA;void main(){`+pFE+`vec2 c=gl_PointCoord-.5;float a=smoothstep(.5,.0,length(c));gl_FragColor=vec4(vec3(.8,.97,1.)*a,a*vA);}`});
   const pts=new THREE.Points(g,m);pts.frustumCulled=false;G.add(pts);PUR.haze=pts}

  /* ---- 5. pathogens: bacteria, viruses, fungi/algae — dissolve as the front passes ---- */
  {const S=lakeSample(5200,-3.0,-0.65);const g=new THREE.BufferGeometry();const P=new Float32Array(S.length*3),A=new Float32Array(S.length*2);
   S.forEach((s,i)=>{P.set(s,i*3);A[i*2]=1+((rnd()*3)|0);A[i*2+1]=rnd()});g.setAttribute('position',new THREE.BufferAttribute(P,3));g.setAttribute('k',new THREE.BufferAttribute(A,2));
   const m=new THREE.ShaderMaterial({uniforms:U2,transparent:true,depthWrite:false,
     vertexShader:pVS+U2decl+dfun+`attribute vec2 k;varying float vA,vI,vF;void main(){vec3 p=position;p.x+=.6*sin(uTime*.4+k.y*30.);p.y+=.25*sin(uTime*.6+k.y*17.);p.z+=.6*cos(uTime*.35+k.y*23.);
       float d=dRet(p.xz)+(k.y-.5)*8.;float alive=max(smoothstep(uR-5.,uR+1.,d),uRegrow);vF=exp(-pow((d-uR+2.)/2.5,2.))*(1.-uRegrow);
       vA=alive*uPoll;vI=k.x;float sz=(.5+.5*k.y)*(.2+.8*alive)*(1.+vF*1.2);
       vec4 mv=modelViewMatrix*vec4(p,1.);gl_PointSize=min(sz*uScale/-mv.z,64.);vA*=mix(1.,exp(-length(mv.xyz)*.022),uUnder);vF*=mix(1.,exp(-length(mv.xyz)*.022),uUnder);gl_Position=projectionMatrix*mv;`+pVE+`}`,
     fragmentShader:pFS+`uniform sampler2D uAtlas;uniform float uUnder;varying float vA,vI,vF;void main(){`+pFE+`vec4 c=texture2D(uAtlas,vec2((gl_PointCoord.x+vI)*.25,gl_PointCoord.y));
       vec3 col=mix(c.rgb,vec3(1.),vF);float a=c.a*max(vA,vF)*(.25+.75*uUnder);if(a<.03)discard;gl_FragColor=vec4(col,a);}`});
   const pts=new THREE.Points(g,m);pts.frustumCulled=false;G.add(pts);PUR.microbes=pts}

  /* ---- 6. underwater environment: surface ceiling, caustic bed, basin wall ---- */
  {const g=new THREE.ShapeGeometry(shapeOf(LAKE),2);g.rotateX(-Math.PI/2);
   const m=new THREE.ShaderMaterial({uniforms:U2,side:THREE.BackSide,transparent:true,depthWrite:false,
     vertexShader:pVS+`varying vec3 vW;void main(){vec4 w=modelMatrix*vec4(position,1.);vW=w.xyz;gl_Position=projectionMatrix*viewMatrix*w;`+pVE+`}`,
     fragmentShader:pFS+U2decl+dfun+`varying vec3 vW;void main(){`+pFE+`vec2 p=vW.xz;float r=fb(p*.25+uTime*.15)*.6+fb(p*.9-uTime*.25)*.4;
       vec3 V=normalize(cameraPosition-vW);float win=smoothstep(.55,.9,abs(V.y));
       float d=dRet(p);float dirty=max(smoothstep(uR-10.,uR+3.,d),uRegrow);
       vec3 clean=mix(vec3(.18,.42,.46),vec3(.75,.92,.95),win*.8+r*.25);vec3 murky=mix(vec3(.12,.2,.1),vec3(.35,.42,.18),r);
       vec3 col=mix(clean,murky,dirty*.75);float fd=1.-exp(-distance(cameraPosition,vW)*.05);col=mix(col,vec3(.08,.22,.21),fd*.85);gl_FragColor=vec4(col,.96);}`});
   const ceil=new THREE.Mesh(g,m);ceil.position.y=-0.51;ceil.visible=false;G.add(ceil);PUR.ceil=ceil}
  {const g=new THREE.ShapeGeometry(shapeOf(LAKE),2);g.rotateX(-Math.PI/2);
   const m=new THREE.ShaderMaterial({uniforms:U2,
     vertexShader:pVS+`varying vec3 vW;void main(){vec4 w=modelMatrix*vec4(position,1.);vW=w.xyz;gl_Position=projectionMatrix*viewMatrix*w;`+pVE+`}`,
     fragmentShader:pFS+U2decl+dfun+`varying vec3 vW;void main(){`+pFE+`vec2 p=vW.xz;float n=fb(p*.15);
       vec2 q=p*.35;float c=0.;for(int i=0;i<3;i++){q+=vec2(sin(q.y*1.7+uTime*.9),cos(q.x*1.3-uTime*.7))*.6;c+=pow(abs(sin(q.x+q.y)),12.);}
       float d=dRet(p);float dirty=max(smoothstep(uR-10.,uR+3.,d),uRegrow);
       vec3 sand=mix(vec3(.15,.16,.11),vec3(.21,.21,.15),n);vec3 sludge=mix(vec3(.05,.06,.03),vec3(.10,.12,.05),n);
       vec3 col=mix(sand,sludge,dirty*.85)*(.55+.45*uUnder)+vec3(.35,.55,.5)*c*.22*(1.-dirty*.7)*uUnder;
       float fd=1.-exp(-distance(cameraPosition,vW)*.05);col=mix(col,mix(vec3(.07,.2,.19),vec3(.09,.16,.07),dirty*.6),fd*uUnder);
       gl_FragColor=vec4(col,1.);}`});
   const bed=new THREE.Mesh(g,m);bed.position.y=-3.15;G.add(bed)}
  {const Pw=[];for(let i=0;i<LAKE.length-1;i++){const a=LAKE[i],b=LAKE[i+1];Pw.push(a[0],-0.9,a[1],b[0],-0.9,b[1],a[0],-3.3,a[1],b[0],-0.9,b[1],b[0],-3.3,b[1],a[0],-3.3,a[1])}
   const w=new THREE.Mesh(geo(Pw),new THREE.MeshLambertMaterial({color:C(0x3c4a3c),side:THREE.DoubleSide}));G.add(w)}
  PUR.hud={bar:document.getElementById('purBar'),pct:document.getElementById('purPct'),msg:document.getElementById('purMsg')};
  PUR.maxR=Math.max(...lakeSample(800,0,0).map(s=>Math.min(Math.hypot(s[0]-r1[0],s[2]-r1[1]),Math.hypot(s[0]-r2[0],s[2]-r2[1]))))+12;
}
function updatePurify(dt){if(!PUR.u.uR)return;const u=PUR.u;const T=U.time.value;u.uScale.value=innerHeight/(2*Math.tan(camera.fov*Math.PI/360));
  controls.maxPolarAngle=controls.target.y<-0.5?Math.PI*0.78:Math.PI*0.497;
  const c=T%PUR.cycle;let R,rg=0;
  if(c<PUR.grow){const x=c/PUR.grow;R=PUR.maxR*(1-Math.pow(1-x,1.55))}else{R=PUR.maxR+8;const r0=PUR.grow+PUR.hold;rg=c<r0?0:clamp((c-r0)/(PUR.cycle-r0),0,1)}
  rg=rg*rg*(3-2*rg);PUR.R=R;PUR.regrow=rg;u.uR.value=PUR.on?R:0;u.uRegrow.value=PUR.on?rg:0;u.uPoll.value=1;
  (PUR.boils||[]).forEach((b,i)=>{const s=1+.18*Math.sin(T*6+i*2);b.scale.set(s,s,s);b.material.opacity=.45+.15*Math.sin(T*9+i)});
  /* underwater switch */
  const under=camera.position.y<-0.5;if(under!==PUR.under){PUR.under=under;u.uUnder.value=under?1:0;PUR.ceil.visible=under;if(PUR.skyMesh)PUR.skyMesh.visible=!under;if(water)water.visible=!under;
    if(under){scene.fog=new THREE.FogExp2(C(0x1d4e4a),0.055);scene.background=C(0x1d4e4a)}else{scene.fog=PUR.aboveFog;scene.background=null}}
  if(under&&camera.position.y<-2.9)camera.position.y=-2.9;
  /* HUD */
  if(PUR.hud&&PUR.on){let k=0;const S=PUR.samples;for(let i=0;i<S.length;i+=7){const d=Math.min(Math.hypot(S[i][0]-UNITS[0].ret[0],S[i][2]-UNITS[0].ret[1]),Math.hypot(S[i][0]-UNITS[1].ret[0],S[i][2]-UNITS[1].ret[1]));if(d<R)k++}
    const pct=Math.round(k/Math.ceil(S.length/7)*100*(1-rg));PUR.hud.bar.style.width=pct+'%';PUR.hud.pct.textContent=pct+'%';
    PUR.hud.msg.textContent=rg>0.02?'다음 정화 사이클 준비 (반복 연출)':pct<99?'마이크로·나노버블 확산 중 · 녹조·혐기성 세균·곰팡이 분해':'호수 전역 정화 완료 · 용존산소 회복'}}
