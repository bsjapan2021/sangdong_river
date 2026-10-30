#!/usr/bin/env python3
"""v2 패치: 보행 데크(다리) 밑은 반드시 기둥과 기둥 사이 '통과 게이트'로만 지나가게
 - 데크 띠(폭/2 + 1.4 m) 안은 운항 금지, 단 기둥 사이 중앙 ±1.1 m 통로만 허용(기둥 간격 4 m)
 - A* 경로계획에 게이트 링크(데크 앞 → 기둥 사이 중앙 → 데크 뒤, 데크에 수직) 추가 → 데크를 건널 땐 항상 게이트 경유
 - 실제 이동(자율·회피·탈출·리모콘)도 같은 규칙(기둥 0.75 m 이격, 데크 밑은 통로만) 적용
 - LiDAR는 데크 대신 수면 높이의 기둥을 감지, 게이트는 초록 표식으로 표시"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
GATE = r"""
/* ---- 데크 밑 통과 게이트(기둥 사이) ---- */
let DECK_PILES=[],DECK_WOOD=[],BANDS=[];
function buildBands(){BANDS=[];DECK_WOOD.forEach(d=>{const hw=d.w/2;for(let i=0;i<d.pts.length-1;i++){const a=d.pts[i],b=d.pts[i+1];const L=Math.hypot(b[0]-a[0],b[1]-a[1]);if(L<1)continue;
    const mid=[(a[0]+b[0])/2,(a[1]+b[1])/2];if(!(inPoly(a,LAKE)||inPoly(b,LAKE)||inPoly(mid,LAKE)||edgeDist(mid,LAKE)<hw+3))continue;
    const gaps=[];for(let s=0;s+4<=L+1e-6;s+=4)gaps.push(s+2);BANDS.push({a,b,L,ux:(b[0]-a[0])/L,uz:(b[1]-a[1])/L,hw,gaps})}})}
function bandInfo(p,extra){for(const B of BANDS){const dx=p[0]-B.a[0],dz=p[1]-B.a[1];const s=dx*B.ux+dz*B.uz;if(s<-1.5||s>B.L+1.5)continue;const d=-dx*B.uz+dz*B.ux;
    if(Math.abs(d)<B.hw+extra){let g=null,gd=1e9;for(const q of B.gaps){const e=Math.abs(q-s);if(e<gd){gd=e;g=q}}return {B,s,d,g,gd}}}return null}
function nearPile(p,r){for(const q of DECK_PILES){const dx=q[0]-p[0],dz=q[1]-p[1];if(dx*dx+dz*dz<r*r)return true}return false}
function deckOK(p,strict){const bi=bandInfo(p,strict?1.4:0.6);if(bi&&!(bi.g!==null&&bi.gd<(strict?1.1:1.5)))return false;return !nearPile(p,strict?1.1:0.75)}
"""
def patch(path, html):
    p = ROOT/path; t = p.read_text()
    def rep(a, b):
        nonlocal t
        assert t.count(a) == 1, (path, a[:70], t.count(a)); t = t.replace(a, b)
    rep("const deckSegs=[];let MODE='pur';", "const deckSegs=[];let MODE='pur';" + GATE)
    rep("for(const s of deckSegs)if(segDist(p,s[0],s[1])<5)return false;return true}", "return deckOK(p,true)}")
    rep("  for(const s of deckSegs)if(segDist(p,s[0],s[1])<2.2)return false;return true}", "  return deckOK(p,false)}")
    rep("  for(const s of deckSegs){const h=segHit(ox,oz,dx,dz,s[0],s[1]);if(h<t){t=h;ty=2}}",
        "  for(const q of DECK_PILES){if(Math.abs(q[0]-ox)>maxR+1||Math.abs(q[1]-oz)>maxR+1)continue;const h=cirHit(ox,oz,dx,dz,q,.2);if(h<t){t=h;ty=2}}   /* 수면 높이 = 데크 기둥 */")
    # grid + gates
    rep("  const v=new Uint8Array(nx*nz);for(let j=0;j<nz;j++)for(let i=0;i<nx;i++)v[j*nx+i]=boatValid([x0+i*cs,z0+j*cs])?1:0;MS.grid={cs,x0,z0,nx,nz,v};",
        "  buildBands();\n"
        "  const v=new Uint8Array(nx*nz);for(let j=0;j<nz;j++)for(let i=0;i<nx;i++)v[j*nx+i]=boatValid([x0+i*cs,z0+j*cs])?1:0;MS.grid={cs,x0,z0,nx,nz,v};\n"
        "  MS.gates=[];MS.gateMap=new Map();BANDS.forEach(B=>B.gaps.forEach(gp=>{const G=[B.a[0]+B.ux*gp,B.a[1]+B.uz*gp],nx2=-B.uz,nz2=B.ux,o=B.hw+2.2;\n"
        "    const A=[G[0]-nx2*o,G[1]-nz2*o],Bp=[G[0]+nx2*o,G[1]+nz2*o];if(!inPoly(G,LAKE)||edgeDist(G,LAKE)<3||!boatValid(A)||!boatValid(Bp))return;\n"
        "    const ca=nearValid(cellOf(A)),cb=nearValid(cellOf(Bp)),ia=ca[1]*nx+ca[0],ib=cb[1]*nx+cb[0];if(ia===ib)return;const cost=(2*o)/cs+1;\n"
        "    const gate={A,G,B:Bp};MS.gates.push(gate);[[ia,ib,A,Bp],[ib,ia,Bp,A]].forEach(([f,to,p0,p1])=>{if(!MS.gateMap.has(f))MS.gateMap.set(f,[]);MS.gateMap.get(f).push({to,cost,pts:[p0,G,p1]})})}));")
    rep("const gs=new Float32Array(N).fill(1e9),from=new Int32Array(N).fill(-1),cl=new Uint8Array(N);",
        "const gs=new Float32Array(N).fill(1e9),from=new Int32Array(N).fill(-1),cl=new Uint8Array(N),via=new Map();")
    rep("      const w=gs[c]+(di&&dj?1.4142:1);if(w<gs[n]){gs[n]=w;from[n]=c;push(n,w+Math.hypot(i-ex,j-ez))}}}",
        "      const w=gs[c]+(di&&dj?1.4142:1);if(w<gs[n]){gs[n]=w;from[n]=c;via.delete(n);push(n,w+Math.hypot(i-ex,j-ez))}}\n"
        "    const gl=MS.gateMap&&MS.gateMap.get(c);if(gl)for(const L of gl){const n=L.to;if(cl[n])continue;const w=gs[c]+L.cost;if(w<gs[n]){gs[n]=w;from[n]=c;via.set(n,L.pts);push(n,w+Math.hypot(n%nx-ex,((n/nx)|0)-ez))}}}   /* 데크 횡단 = 게이트 링크만 */")
    rep("const out=[];let c=ei;if(from[c]<0&&c!==si)return [pa,pb];while(c>=0){out.push(cellW(c%nx,(c/nx)|0));if(c===si)break;c=from[c]}out.reverse();out[0]=pa;out.push(pb);",
        "const out=[];let c=ei;if(from[c]<0&&c!==si)return [pa,pb];while(c>=0){out.push(cellW(c%nx,(c/nx)|0));if(via.has(c)){const vp=via.get(c);out.push(vp[2],vp[1],vp[0])}if(c===si)break;c=from[c]}out.reverse();out[0]=pa;out.push(pb);")
    # gate markers (green), revealed with the scan like other zones
    rep("  deckSegs.forEach(s=>{const g=new THREE.BufferGeometry();",
        "  (MS.gates||[]).forEach(gt=>{const m=new THREE.Mesh(new THREE.RingGeometry(.45,.65,24),msMat(0x7ff0b0,.85));m.rotation.x=-Math.PI/2;m.position.set(gt.G[0],-0.34,gt.G[1]);m.userData.z=gt.G[1];m.userData.gate=1;G.add(m);MS.nogo.push(m)});\n"
        "  deckSegs.forEach(s=>{const g=new THREE.BufferGeometry();")
    if html:
        rep("const dm=new THREE.Mesh(geo(deckP,deckUV),", "DECK_PILES=piles;DECK_WOOD=decks.filter(d=>!d.road).map(d=>({pts:d.pts,w:d.w}));\n  const dm=new THREE.Mesh(geo(deckP,deckUV),")
        rep('<i style="color:#ff5a5a">○</i><span data-i18n="lgNogo">금지구역</span>', '<i style="color:#ff5a5a">○</i><span data-i18n="lgNogo">금지구역</span> <i style="color:#7ff0b0">○</i><span data-i18n="lgGate">기둥 사이 게이트</span>')
        rep(" hudFold:{", " lgGate:{ko:'기둥 사이 게이트',en:'Pile gate',ja:'橋脚間ゲート'},\n hudFold:{")
    p.write_text(t)
patch('src/template_v2.html', True); patch('src/tools/boat.js', False); print('gate patched')
