#!/usr/bin/env python3
"""v2 패치: 쌍동선 자율운항 미션 — ① 수계 인식 ② 경로 최적화 ③ GNSS·LiDAR 자율운항/장애물 회피 (3개 국어)"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
BOATJS = (ROOT/'src/tools/boat.js').read_text()
p = ROOT/'src/template_v2.html'; t = p.read_text()
def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (a[:80], t.count(a)); t = t.replace(a, b)
a = t.index("/* ================= 녹조제거 쌍동선"); b = t.index("\nfunction updatePurify(dt){")
t = t[:a] + BOATJS + t[b:]
rep('<div class="pnote" data-i18n="boatNote">',
    '<div class="msteps"><span data-ms="1" data-i18n="msSt1">① 수계 인식</span><span data-ms="2" data-i18n="msSt2">② 경로 최적화</span><span data-ms="3" data-i18n="msSt3">③ 자율 운항</span></div>\n'
    '  <div class="tele"><div><i style="color:#9fd8ff">●</i> <span id="bGnss">GNSS</span></div><div><i style="color:#7dff9e">●</i> <span id="bLidar">LiDAR</span></div>'
    '<div class="lleg"><i style="color:#5ae6ff">●</i><span data-i18n="lgShore">호안</span> <i style="color:#ffd15a">●</i><span data-i18n="lgStruct">구조물</span> <i style="color:#ff4d5e">●</i><span data-i18n="lgObs">부유 장애물</span> <i style="color:#ff5a5a">○</i><span data-i18n="lgNogo">금지구역</span><button id="bRestart" data-i18n="bRestart">미션 재시작</button></div></div>\n'
    '  <div class="pnote" data-i18n="boatNote">')
rep("#boatBar{", "#purHud .msteps{display:flex;gap:4px;margin-top:8px}#purHud .msteps span{flex:1;text-align:center;font-size:10.5px;padding:3px 2px;border-radius:4px;color:var(--ink-3);border:1px solid var(--glass-line)}\n"
    "#purHud .msteps span[data-st=\"on\"]{color:#06222a;background:#8fe6ff;border-color:#8fe6ff;font-weight:600}#purHud .msteps span[data-st=\"done\"]{color:#9ff0b8;border-color:rgba(159,240,184,.5)}\n"
    "#purHud .tele{margin-top:6px;font:500 10.5px var(--mono);color:var(--ink-2);line-height:1.55}#purHud .tele i{font-style:normal}\n"
    "#purHud .lleg{font-family:var(--ui);color:var(--ink-3);display:flex;gap:3px;align-items:center;flex-wrap:wrap}#purHud .lleg span{margin-right:4px}\n"
    "#purHud #bRestart{margin-left:auto;font:500 10.5px var(--ui);color:var(--ink-2);background:rgba(255,255,255,.04);border:1px solid var(--glass-line);border-radius:5px;padding:2px 7px;cursor:pointer}\n#boatBar{")
rep("controls.addEventListener('start',", "$('#bRestart').addEventListener('click',()=>{boatReset();missionStart()});\ncontrols.addEventListener('start',")
rep(" boatLbl:{", """ msSt1:{ko:'① 수계 인식',en:'① Water mapping',ja:'① 水域認識'},
 msSt2:{ko:'② 경로 최적화',en:'② Path planning',ja:'② 経路最適化'},
 msSt3:{ko:'③ 자율 운항',en:'③ Autonomous run',ja:'③ 自律運航'},
 ms1:{ko:'수계 인식 중 · 위성영상 + LiDAR 경계 스캔 {p}%',en:'Mapping water area · satellite imagery + LiDAR boundary scan {p}%',ja:'水域認識中・衛星画像＋LiDAR境界スキャン {p}%'},
 ms1done:{ko:'수계 인식 완료 · 수면적 {a} m² · 운항 금지구역 {n}곳 등록',en:'Water area mapped · {a} m² · {n} no-go zones registered',ja:'水域認識完了・水面積 {a} m²・航行禁止区域 {n}か所登録'},
 ms2:{ko:'경로 최적화 · {pat} 커버리지 경로 {L} m · 예상 커버리지 {C}%',en:'Path optimized · {pat} coverage route {L} m · expected coverage {C}%',ja:'経路最適化・{pat}カバレッジ経路 {L} m・予想カバー率 {C}%'},
 patH:{ko:'동서 왕복',en:'east–west lawnmower',ja:'東西往復'},
 patV:{ko:'남북 왕복(교차)',en:'north–south cross-pass',ja:'南北往復（交差）'},
 msAvoid:{ko:'⚠ LiDAR 부유 장애물 감지 {d} m → 회피 기동 후 경로 복귀',en:'⚠ LiDAR: floating obstacle {d} m → avoiding, then rejoining route',ja:'⚠ LiDAR浮遊障害物検知 {d} m → 回避後に経路復帰'},
 gnssLn:{ko:'GNSS RTK-FIX · 위성 {n} · {lat}°N {lon}°E · HDOP {h}',en:'GNSS RTK-FIX · {n} sats · {lat}°N {lon}°E · HDOP {h}',ja:'GNSS RTK-FIX・衛星 {n}・{lat}°N {lon}°E・HDOP {h}'},
 lidarLn:{ko:'LiDAR 360° · 15 m · 장애물 반사 {n} · 최근접 {d}',en:'LiDAR 360° · 15 m · obstacle returns {n} · nearest {d}',ja:'LiDAR 360°・15 m・障害物反射 {n}・最近接 {d}'},
 lgShore:{ko:'호안',en:'Shore',ja:'護岸'},lgStruct:{ko:'구조물',en:'Structure',ja:'構造物'},lgObs:{ko:'부유 장애물',en:'Floating obstacle',ja:'浮遊障害物'},lgNogo:{ko:'금지구역',en:'No-go',ja:'禁止区域'},
 bRestart:{ko:'미션 재시작',en:'Restart mission',ja:'ミッション再開'},
 obsLbl:{ko:'⚠ LiDAR 장애물 · 회피',en:'⚠ LiDAR obstacle · avoiding',ja:'⚠ LiDAR障害物・回避'},
 boatLbl:{""")
rep("boatNote:{ko:'수면 구역만 운항 · 녹조 밀집 구역 우선 탐색 · 전방 UFB 노즐 + 태양광 TiO₂/UVA ROS · 개념 시각화(실제 속도 1.5 m/s)',en:'Water area only · targets dense algae first · bow UFB nozzles + solar TiO₂/UVA ROS · concept visualization (real speed 1.5 m/s)',ja:'水域のみ航行・アオコ密集域を優先探索・船首UFBノズル＋太陽光TiO₂/UVA ROS・概念ビジュアル（実速度1.5 m/s）'}",
    "boatNote:{ko:'수면 구역만 운항 · 왕복 커버리지 경로 · 전방 UFB 노즐 + 태양광 TiO₂/UVA ROS · 좌표는 근사값 · 개념 시각화(실제 속도 1.5 m/s)',en:'Water area only · lawnmower coverage route · bow UFB nozzles + solar TiO₂/UVA ROS · coordinates approximate · concept visualization (real speed 1.5 m/s)',ja:'水域のみ航行・往復カバレッジ経路・船首UFBノズル＋太陽光TiO₂/UVA ROS・座標は概算・概念ビジュアル（実速度1.5 m/s）'}")
rep('data-i18n="boatNote">수면 구역만 운항 · 녹조 밀집 구역 우선 탐색 · 전방 UFB 노즐 + 태양광 TiO₂/UVA ROS · 개념 시각화(실제 속도 1.5 m/s)',
    'data-i18n="boatNote">수면 구역만 운항 · 왕복 커버리지 경로 · 전방 UFB 노즐 + 태양광 TiO₂/UVA ROS · 좌표는 근사값 · 개념 시각화(실제 속도 1.5 m/s)')
rep("window.__dt={scene,camera,controls,openCompare,setTime,flyTo,U,PUR,BOAT,setMode};", "window.__dt={scene,camera,controls,openCompare,setTime,flyTo,U,PUR,BOAT,MS,setMode};")
p.write_text(t); print('mission patched')
