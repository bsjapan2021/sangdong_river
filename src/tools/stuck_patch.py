#!/usr/bin/env python3
"""v2 패치: 보트 고착(구석·협소 수역) 감지·탈출 루틴
 - 이동 판정은 완화 기준(boatSoft: 호안 2.2 m·데크 2.2 m·분수 4 m), 경로 계획은 기존 엄격 기준 유지
 - 6초(시뮬) 동안 1.5 m 미만 이동 → 고착 판정 → ① 후진 ② 주변 '넓은 수역' 셀로 A* 탈출 경로 ③ 경로 복귀(같은 곳 반복 고착 시 해당 구간 건너뜀)
 - 탈출 경로도 막히면 최후 수단으로 탈출 지점까지 천천히 미끄러져 이동(시뮬레이션 보정)"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
REC = r"""
/* ---- 고착 감지·탈출 루틴 ---- */
function boatSoft(p){if(!inPoly(p,LAKE)||edgeDist(p,LAKE)<2.2)return false;for(const f of FOUNT)if(Math.hypot(p[0]-f[0],p[1]-f[1])<4)return false;
  for(const s of deckSegs)if(segDist(p,s[0],s[1])<2.2)return false;return true}
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
  if(boatSoft([nx,nz])||!boatSoft(pos))BOAT.pos.set(nx,nz);
  else if(R.tt>14){const d=Math.hypot(tg[0]-pos[0],tg[1]-pos[1])||1,s=Math.min(d,.6*sdt);BOAT.pos.set(pos[0]+(tg[0]-pos[0])/d*s,pos[1]+(tg[1]-pos[1])/d*s)}   /* 최후 수단: 탈출 지점으로 서서히 이동 */
  return true}
"""
def patch(path):
    p = ROOT/path; t = p.read_text()
    def rep(a, b):
        nonlocal t
        assert t.count(a) == 1, (path, a[:70], t.count(a)); t = t.replace(a, b)
    rep("/* 2D ray cast against shoreline", REC + "/* 2D ray cast against shoreline")
    rep("  let tg=PW[Math.min(MS.pi+1,tot-1)];const fx=Math.cos(BOAT.hd),fz=Math.sin(BOAT.hd);",
        "  if(!MS.prog)MS.prog={t:0,x:pos[0],z:pos[1]};MS.prog.t+=sdt;\n"
        "  if(MS.prog.t>6){if(!MS.rec&&Math.hypot(pos[0]-MS.prog.x,pos[1]-MS.prog.z)<1.5)startRecover(pos);MS.prog={t:0,x:pos[0],z:pos[1]}}   /* 6초간 1.5 m 미만 이동 = 고착 */\n"
        "  if(MS.rec)return recoverStep(dt,sdt,pos);\n"
        "  let tg=PW[Math.min(MS.pi+1,tot-1)];const fx=Math.cos(BOAT.hd),fz=Math.sin(BOAT.hd);")
    rep("if(!blocked&&(boatValid([nx,nz])||!boatValid(pos))){", "if(!blocked&&(boatSoft([nx,nz])||!boatSoft(pos))){")
    rep("if(MS.ph===3)$('#boatMsg').textContent=MS.avoid?", "if(MS.ph===3)$('#boatMsg').textContent=MS.rec?T('msRecover'):MS.avoid?")
    rep("function missionStart(){if(!MS.G)return;", "function missionStart(){if(!MS.G)return;MS.rec=null;MS.prog=null;MS.stuckN=0;")
    if path.endswith('.html'):
        rep(" hudFold:{", " msRecover:{ko:'⚠ 협소 구역 고착 감지 → 후진 · 넓은 수역으로 탈출 경로 재계산 중',en:'⚠ Stuck in a tight spot → reversing and re-planning an escape to open water',ja:'⚠ 狭い水域で停滞を検知 → 後退し広い水域への脱出経路を再計算中'},\n hudFold:{")
    p.write_text(t)
patch('src/template_v2.html'); patch('src/tools/boat.js'); print('stuck patched')
