#!/usr/bin/env python3
"""v2 패치: (1) 정화 전선 ↔ S-01~S-05 수질 패널 연동  (2) 광촉매 ROS(·OH, O₂⁻) 빛 입자 + 미생물 분해 연출"""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[2]

ROS_BLOCK = r"""
  /* ---- 5b. photocatalytic ROS (·OH / O₂⁻): light specks concentrated behind the front and around the outlets ---- */
  {const S=lakeSample(6500,-3.0,-0.6);const g=new THREE.BufferGeometry();const P=new Float32Array(S.length*3),A=new Float32Array(S.length*2);
   S.forEach((s,i)=>{P.set(s,i*3);A[i*2]=rnd()<.55?0:1;A[i*2+1]=rnd()});g.setAttribute('position',new THREE.BufferAttribute(P,3));g.setAttribute('k',new THREE.BufferAttribute(A,2));
   const m=new THREE.ShaderMaterial({uniforms:U2,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
     vertexShader:pVS+U2decl+dfun+`attribute vec2 k;varying float vA,vT;void main(){vec3 p=position;float ph=k.y*6.283;
       p+=vec3(sin(uTime*2.3+ph*3.),.5*cos(uTime*1.9+ph*5.),cos(uTime*2.1+ph*7.))*.7;
       float d=dRet(p.xz);float band=exp(-pow((uR-d-9.)/8.,2.))*step(1.,uR);float near=exp(-d/16.)*.85;
       float w=max(band,near)*(1.-uRegrow*.8);float fl=pow(.5+.5*sin(uTime*(9.+k.y*14.)+ph*11.),3.);
       vec4 mv=modelViewMatrix*vec4(p,1.);vA=w*(.25+.75*fl)*mix(.3,exp(-length(mv.xyz)*.028),uUnder);vT=k.x;
       gl_PointSize=min((.10+.12*k.y)*(1.+fl)*uScale/-mv.z,16.);gl_Position=projectionMatrix*mv;`+pVE+`}`,
     fragmentShader:pFS+`varying float vA,vT;void main(){`+pFE+`float r=length(gl_PointCoord-.5);float a=smoothstep(.5,.0,r);float core=smoothstep(.18,.0,r);
       vec3 col=mix(vec3(.72,.95,1.),vec3(.78,.5,1.),vT);col=mix(col,vec3(1.),core*.7);if(a*vA<.01)discard;gl_FragColor=vec4(col*a,a*vA);}`});
   const pts=new THREE.Points(g,m);pts.frustumCulled=false;G.add(pts);PUR.ros=pts}
"""

SENSOR_BLOCK = r"""let selected=null;const live={};
/* 정화 전선 연동 수질 모델 (시뮬레이션): 오염 상태 POL → 정화 상태 CLN, 환수부는 처리수 유입분 가산 */
const POL={do:5.6,orp:95,ph:7.45,t:16.9,ntu:14.6},CLN={do:8.2,orp:232,ph:7.75,t:17.0,ntu:9.6},OUTB={do:.6,orp:15,ph:.02,t:.1,ntu:-.6};
SENS.forEach(s=>live[s.id]={...POL,c:0});
function sensorClean(s){if(!PUR.on)return s.cls==='out'?1:0;const d=Math.min(...UNITS.map(u=>Math.hypot(s.p[0]-u.ret[0],s.p[1]-u.ret[1])));
  let c=clamp((PUR.R-d)/18,0,1);c=c*c*(3-2*c);return c*(1-PUR.regrow)}
const _dirty=new THREE.Color(),_cl=new THREE.Color();
function drift(){SENS.forEach(s=>{const v=live[s.id];const c=sensorClean(s);v.c=c;
  for(const k in POL){const tgt=POL[k]+(CLN[k]-POL[k])*c+(s.cls==='out'?OUTB[k]*c:0);v[k]+=(tgt-v[k])*.3+(Math.random()-.5)*(k==='orp'?1.5:k==='ntu'?.08:k==='do'?.03:.008)}
  if(s.obj){_dirty.set(0x7a7f2a).convertSRGBToLinear();_cl.set(s.col).convertSRGBToLinear();s.obj.userData.ring.material.color.copy(_dirty).lerp(_cl,v.c)}});render()}
const pctD=(v,b)=>((v-b)/b*100);
function stateOf(c){return c<.05?['정화 전','#b8b36a','rgba(160,150,60,.18)']:c<.95?['정화 중','#9fe8ff','rgba(80,190,230,.16)']:['정화 완료','#7ff0b0','rgba(80,220,140,.16)']}
function bar(frac,col){return `<span style="display:block;height:5px;border-radius:3px;background:rgba(255,255,255,.08);margin-top:3px;overflow:hidden"><i style="display:block;height:100%;width:${Math.round(clamp(frac,0,1)*100)}%;background:${col}"></i></span>`}
function render(){const el=$('#info');
  if(!selected){const rows=SENS.map(s=>{const v=live[s.id];const st=stateOf(v.c);const dd=pctD(v.do,POL.do),dn=pctD(v.ntu,POL.ntu);
      return `<tr><td style="padding:3px 0;font-family:var(--mono);font-size:11px;color:var(--ink-2)">${s.code}</td><td style="font-size:11.5px">${s.name.replace('부','')}</td>
        <td style="text-align:right;font-family:var(--mono)">${v.do.toFixed(1)}<span style="color:${dd>=30?'#7ff0b0':'var(--ink-3)'};font-size:10px"> ${dd>=0?'+':''}${dd.toFixed(0)}%</span></td>
        <td style="text-align:right;font-family:var(--mono)">${v.ntu.toFixed(1)}<span style="color:${dn<=-20?'#7ff0b0':'var(--ink-3)'};font-size:10px"> ${dn.toFixed(0)}%</span></td>
        <td style="text-align:right"><span style="font-size:10px;padding:1px 5px;border-radius:3px;color:${st[1]};background:${st[2]}">${st[0]}</span></td></tr>`}).join('');
    el.innerHTML=`<h2>수질 모니터링 · 5지점</h2><div class="sub">정화 전선 통과에 따라 실시간 변화 (DO mg/L · 탁도 NTU · 운전 전 대비)</div>
     <table style="width:100%;border-collapse:collapse;font-size:12px;font-variant-numeric:tabular-nums"><thead><tr style="color:var(--ink-3);font-size:10.5px"><th style="text-align:left;font-weight:500">지점</th><th></th><th style="text-align:right;font-weight:500">DO</th><th style="text-align:right;font-weight:500">탁도</th><th></th></tr></thead><tbody>${rows}</tbody></table>
     <div class="flow">표 5 판정 기준: DO <i>+30~50%</i> · 탁도 <i>−20% 이상</i> → 달성 시 초록 표시<br>PhotoNano 2기 · 호기 간 ${Math.round(Math.hypot(UNITS[0].mod[0]-UNITS[1].mod[0],UNITS[0].mod[1]-UNITS[1].mod[1]))} m · 각 호기 취수–환수 ${Math.round(Math.hypot(UNITS[0].int[0]-UNITS[0].ret[0],UNITS[0].int[1]-UNITS[0].ret[1]))} m<br>부표를 누르면 지점별 상세값을 봅니다.</div>
     <div style="margin-top:8px"><span class="pill">시뮬레이션 데이터 · 실측 연동 전</span></div>`;return}
  const v=live[selected.id];const st=stateOf(v.c);const dd=pctD(v.do,POL.do),dn=pctD(v.ntu,POL.ntu),dorp=v.orp-POL.orp;
  el.innerHTML=`<h2>${selected.code} · ${selected.name}</h2><div class="sub">수심 0.5 m 다항목 수질계 · 0.5초 갱신 · <span style="color:${st[1]}">${st[0]}</span></div>
   <div class="kv"><span>DO</span><b>${v.do.toFixed(2)} mg/L <span style="color:${dd>=30?'#7ff0b0':'var(--ink-2)'};font-weight:500">${dd>=0?'+':''}${dd.toFixed(0)}%</span></b></div>${bar((v.do-4)/6,'linear-gradient(90deg,#3b8fd8,#7fe3ff)')}
   <div class="kv" style="margin-top:6px"><span>탁도</span><b>${v.ntu.toFixed(1)} NTU <span style="color:${dn<=-20?'#7ff0b0':'var(--ink-2)'};font-weight:500">${dn.toFixed(0)}%</span></b></div>${bar(v.ntu/18,'linear-gradient(90deg,#c9b45a,#8a7a2a)')}
   <div class="kv" style="margin-top:6px"><span>ORP</span><b>${v.orp.toFixed(0)} mV <span style="color:var(--ink-2);font-weight:500">${dorp>=0?'+':''}${dorp.toFixed(0)}</span></b>
   <span>pH</span><b>${v.ph.toFixed(2)}</b><span>수온</span><b>${v.t.toFixed(1)} °C</b><span>좌표(공원 기준)</span><b>${selected.p[0]}, ${selected.p[1]} m</b></div>
   <div style="margin-top:10px"><span class="pill">시뮬레이션 데이터 · 실측 연동 전</span></div>
   <div class="flow">표 5 판정: DO 운전 전 대비 30~50% 증가 ${dd>=30?'✔':'…'} · 탁도 20% 이상 저감 ${dn<=-20?'✔':'…'}<br>ORP 상승은 ·OH 등 산화성 활성종 증가와 함께 나타나는 참고 지표입니다.</div>`}
"""

def patch(path, is_template):
    p = pathlib.Path(path); t = p.read_text()
    def rep(a, b):
        nonlocal t
        assert t.count(a) == 1, (path, a[:70], t.count(a)); t = t.replace(a, b)
    rep("  /* ---- 6. underwater environment", ROS_BLOCK + "\n  /* ---- 6. underwater environment")
    rep("vF=exp(-pow((d-uR+2.)/2.5,2.))*(1.-uRegrow);", "vF=exp(-pow((d-uR+2.)/2.5,2.))*(1.-uRegrow);p+=vec3(sin(uTime*25.+k.y*90.),.3*sin(uTime*31.+k.y*40.),cos(uTime*23.+k.y*70.))*vF*.3;")
    rep("vec3 col=mix(c.rgb,vec3(1.),vF);", "vec3 col=mix(c.rgb,mix(vec3(.82,.55,1.),vec3(.8,1.,1.),fract(vI*.37+uUnder*.0)),vF);")
    rep("float glint=pow(vn(p*3.+t*2.),18.)*inner*1.6;",
        "float glint=pow(vn(p*3.+t*2.),18.)*inner*1.6;float rosb=exp(-pow((uR-d-8.)/7.,2.))*step(1.,uR)*(1.-uRegrow);float rs=pow(vn(p*5.+t*6.),14.)*rosb*2.2;")
    rep("col+=vec3(.75,.95,1.)*glint;", "col+=vec3(.75,.95,1.)*glint+vec3(.72,.5,1.)*rs;")
    rep("float a=cover*dirty*.92+foam*.85+glint*.8+inner*.06;", "float a=cover*dirty*.92+foam*.85+glint*.8+rs*.7+inner*.06;")
    rep("'마이크로·나노버블 확산 중 · 녹조·혐기성 세균·곰팡이 분해'", "'UFB 확산 · TiO₂/UVA 광촉매 ROS(·OH, O₂⁻)가 녹조·세균·곰팡이 산화 분해 중'")
    if is_template:
        t2 = re.sub(r"let selected=null;const live=\{\};SENS\.forEach.*?\n(?=function select\(s\)\{)", lambda m: SENSOR_BLOCK, t, flags=re.S)
        assert t2 != t; t = t2
        rep("setInterval(drift,2000);", "setInterval(drift,500);")
        rep('<div class="pnote">개념 시각화(반복 연출) · 실측·수치해석 결과가 아닙니다</div>',
            '<div class="pnote"><span style="color:#bdefff">● ·OH</span> <span style="color:#c99bff">● O₂⁻</span> 광촉매 활성산소 · 개념 시각화(반복 연출) · 실측 결과 아님</div>')
    p.write_text(t)

patch(ROOT/'src/template_v2.html', True)
patch(ROOT/'src/purify.js', False)
print('patched')
