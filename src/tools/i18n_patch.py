#!/usr/bin/env python3
"""v2 3개국어(한국어/English/日本語) 패치 — src/template_v2.html"""
import pathlib, re, sys
p = pathlib.Path(sys.argv[1]); t = p.read_text()
def rep(a, b, n=1):
    global t
    c = t.count(a); assert c == n, (a[:80], c); t = t.replace(a, b)

I18N_JS = r"""
/* ================= i18n: 한국어 / English / 日本語 ================= */
const I18N={
 title:{ko:'상동호수공원 디지털트윈',en:'Sangdong Lake Park Digital Twin',ja:'上洞湖水公園 デジタルツイン'},
 headP:{ko:'OpenStreetMap 실측 지형 + 현장 사진 기반 실사 재현. 측정 5지점과 PhotoNano 2기(호안 설치) 배치안을 표시합니다.',en:'Photoreal reconstruction from surveyed OpenStreetMap terrain and site photos, showing 5 monitoring points and the layout of two shoreline PhotoNano units.',ja:'OpenStreetMapの実測地形と現地写真に基づくフォトリアル再現。測定5地点とPhotoNano 2基（護岸設置）の配置案を表示します。'},
 loading:{ko:'실사 텍스처와 지형을 생성하는 중…',en:'Generating photoreal textures and terrain…',ja:'フォトリアルなテクスチャと地形を生成中…'},
 ld1:{ko:'실사 텍스처 생성 중…',en:'Generating textures…',ja:'テクスチャ生成中…'},
 ld2:{ko:'하늘·구름 생성 중…',en:'Building sky and clouds…',ja:'空と雲を生成中…'},
 ld3:{ko:'지형·호수 생성 중…',en:'Building terrain and lake…',ja:'地形と湖を生成中…'},
 ld4:{ko:'도로·데크 생성 중…',en:'Building roads and decks…',ja:'道路とデッキを生成中…'},
 ld5:{ko:'건물·스카이라인 배치 중…',en:'Placing buildings and skyline…',ja:'建物とスカイラインを配置中…'},
 ld6:{ko:'수목·갈대 식재 중…',en:'Planting trees and reeds…',ja:'樹木とヨシを植栽中…'},
 ld7:{ko:'분수·차량·테스트베드 배치 중…',en:'Placing fountains, traffic and testbed…',ja:'噴水・車両・テストベッドを配置中…'},
 ld8:{ko:'마무리…',en:'Finishing…',ja:'仕上げ中…'},
 layers:{ko:'레이어',en:'Layers',ja:'レイヤー'},
 lyBuild:{ko:'건물·스카이라인',en:'Buildings & skyline',ja:'建物・スカイライン'},
 lyTree:{ko:'수목·갈대',en:'Trees & reeds',ja:'樹木・ヨシ'},
 lyLabel:{ko:'명칭',en:'Place names',ja:'名称'},
 lyTB:{ko:'테스트베드 시설',en:'Testbed facilities',ja:'テストベッド設備'},
 lyFount:{ko:'분수 가동',en:'Fountains on',ja:'噴水運転'},
 lyCar:{ko:'차량 흐름',en:'Traffic',ja:'車両の流れ'},
 lyHeat:{ko:'DO 분포 (시뮬레이션)',en:'DO distribution (simulated)',ja:'DO分布（シミュレーション）'},
 lyRot:{ko:'자동 회전',en:'Auto-rotate',ja:'自動回転'},
 photos:{ko:'현장 사진 비교',en:'Site photo comparison',ja:'現地写真の比較'},
 photosHint:{ko:'사진을 누르면 비슷한 시점으로 이동해 3D 위에 겹쳐 봅니다.',en:'Tap a photo to fly to a matching viewpoint and overlay it on the 3D view.',ja:'写真を押すと近い視点へ移動し、3Dに重ねて表示します。'},
 tod:{ko:'시간대',en:'Time of day',ja:'時間帯'},
 intakeLine:{ko:'취수 라인',en:'Intake line',ja:'取水ライン'},
 returnLine:{ko:'환수 라인',en:'Return line',ja:'還水ライン'},
 heatLbl:{ko:'DO mg/L (시뮬레이션)',en:'DO mg/L (simulated)',ja:'DO mg/L（シミュレーション）'},
 photo:{ko:'사진',en:'Photo',ja:'写真'},
 overlay:{ko:'겹침',en:'Overlay',ja:'重ね'},
 closeCmp:{ko:'비교 닫기',en:'Close comparison',ja:'比較を閉じる'},
 views:{ko:'시점',en:'Views',ja:'視点'},
 v_bird:{ko:'전경',en:'Overview',ja:'全景'},
 v_top:{ko:'평면',en:'Plan',ja:'平面'},
 v_tb:{ko:'1호기',en:'Unit 1',ja:'1号機'},
 v_tb2:{ko:'2호기',en:'Unit 2',ja:'2号機'},
 v_water:{ko:'수면 시점',en:'Water level',ja:'水面視点'},
 v_walk:{ko:'산책로',en:'Promenade',ja:'散策路'},
 v_pur:{ko:'정화 전경',en:'Purification view',ja:'浄化全景'},
 v_under:{ko:'수중 시점',en:'Underwater',ja:'水中視点'},
 modeGroup:{ko:'표시 모드',en:'Display mode',ja:'表示モード'},
 mNormal:{ko:'일반 상태',en:'Normal',ja:'通常状態'},
 mPur:{ko:'정화 연출',en:'Purification',ja:'浄化演出'},
 kbdP:{ko:'키보드 P로 전환',en:'Press P to switch',ja:'Pキーで切替'},
 purTitle:{ko:'UFB 마이크로·나노버블 정화 연출',en:'UFB micro/nano-bubble purification',ja:'UFBマイクロ・ナノバブル浄化演出'},
 purReady:{ko:'준비 중',en:'Preparing',ja:'準備中'},
 rosNote:{ko:'광촉매 활성산소 · 개념 시각화(반복)',en:'Photocatalytic ROS · conceptual visualization (loop)',ja:'光触媒活性酸素・概念ビジュアル（反復）'},
 stop:{ko:'정지',en:'Off',ja:'停止'},
 normMsg:{ko:'PhotoNano 미가동 · 현재 호수 상태(녹조·혐기성 오염 잔존 가정)',en:'PhotoNano off · current lake condition (algae and anaerobic pollution assumed)',ja:'PhotoNano停止・現在の湖の状態（アオコ・嫌気性汚染が残存と仮定）'},
 normNote:{ko:'측정 5지점은 운전 전 기준값으로 표시됩니다',en:'The 5 monitoring points show pre-operation baselines',ja:'測定5地点は運転前の基準値で表示します'},
 credit:{ko:'© 2026 주식회사 나노하이드로인 (NanoHydroIn Co., Ltd.) · All rights reserved · 지도 © OpenStreetMap contributors (ODbL) · three.js (MIT) · 사진: 각 원저작자',
   en:'© 2026 NanoHydroIn Co., Ltd. (주식회사 나노하이드로인) · All rights reserved · Map © OpenStreetMap contributors (ODbL) · three.js (MIT) · Photos: respective owners',
   ja:'© 2026 株式会社ナノハイドロイン (NanoHydroIn Co., Ltd.) · All rights reserved · 地図 © OpenStreetMap contributors (ODbL) · three.js (MIT) · 写真：各原著作者'},
 hudRegrow:{ko:'다음 정화 사이클 준비 (반복 연출)',en:'Preparing the next purification cycle (loop)',ja:'次の浄化サイクルを準備中（反復演出）'},
 hudRun:{ko:'UFB 확산 · TiO₂/UVA 광촉매 ROS(·OH, O₂⁻)가 녹조·세균·곰팡이 산화 분해 중',en:'UFB spreading · TiO₂/UVA photocatalytic ROS (·OH, O₂⁻) oxidizing algae, bacteria and fungi',ja:'UFB拡散中・TiO₂/UVA光触媒ROS（·OH, O₂⁻）がアオコ・細菌・カビを酸化分解中'},
 hudDone:{ko:'호수 전역 정화 완료 · 용존산소 회복',en:'Whole lake purified · dissolved oxygen restored',ja:'湖全域の浄化完了・溶存酸素が回復'},
 u1:{ko:'1호기(서측)',en:'Unit 1 (west)',ja:'1号機（西側）'},
 u2:{ko:'2호기(동측)',en:'Unit 2 (east)',ja:'2号機（東側）'},
 s_in1:{ko:'1호기 취수부',en:'Unit 1 intake',ja:'1号機 取水部'},
 s_out1:{ko:'1호기 환수부',en:'Unit 1 return',ja:'1号機 還水部'},
 s_ctr:{ko:'연못 중앙부',en:'Lake center',ja:'池の中央部'},
 s_in2:{ko:'2호기 취수부',en:'Unit 2 intake',ja:'2号機 取水部'},
 s_out2:{ko:'2호기 환수부',en:'Unit 2 return',ja:'2号機 還水部'},
 ss_in1:{ko:'1호기 취수',en:'U1 intake',ja:'1号機 取水'},
 ss_out1:{ko:'1호기 환수',en:'U1 return',ja:'1号機 還水'},
 ss_ctr:{ko:'중앙',en:'Center',ja:'中央'},
 ss_in2:{ko:'2호기 취수',en:'U2 intake',ja:'2号機 取水'},
 ss_out2:{ko:'2호기 환수',en:'U2 return',ja:'2号機 還水'},
 st0:{ko:'정화 전',en:'Untreated',ja:'浄化前'},st1:{ko:'정화 중',en:'Treating',ja:'浄化中'},st2:{ko:'정화 완료',en:'Purified',ja:'浄化完了'},
 sts0:{ko:'전',en:'Pre',ja:'前'},sts1:{ko:'중',en:'In',ja:'中'},sts2:{ko:'완료',en:'Done',ja:'完了'},
 monTitle:{ko:'수질 모니터링 · 5지점',en:'Water quality · 5 points',ja:'水質モニタリング・5地点'},
 monSub:{ko:'정화 전선 통과에 따라 실시간 변화 (DO mg/L · 탁도 NTU · 운전 전 대비)',en:'Updates live as the purification front passes (DO mg/L · turbidity NTU · vs. pre-operation)',ja:'浄化前線の通過に応じてリアルタイム変化（DO mg/L・濁度 NTU・運転前比）'},
 thPoint:{ko:'지점',en:'Point',ja:'地点'},turb:{ko:'탁도',en:'Turbidity',ja:'濁度'},
 monFlow:{ko:'표 5 판정 기준: DO <i>+30~50%</i> · 탁도 <i>−20% 이상</i> → 달성 시 초록 표시<br>PhotoNano 2기 · 호기 간 {d} m · 각 호기 취수–환수 {s} m<br>부표를 누르면 지점별 상세값을 봅니다.',
   en:'Table 5 criteria: DO <i>+30–50%</i> · turbidity <i>−20% or more</i> → green when met<br>2 PhotoNano units · {d} m apart · intake–return {s} m each<br>Tap a buoy for point details.',
   ja:'表5 判定基準：DO <i>+30〜50%</i>・濁度 <i>−20%以上</i> → 達成時は緑で表示<br>PhotoNano 2基・号機間 {d} m・各号機の取水–還水 {s} m<br>ブイを押すと地点別の詳細を表示します。'},
 simPill:{ko:'시뮬레이션 데이터 · 실측 연동 전',en:'Simulated data · not yet linked to field sensors',ja:'シミュレーションデータ・実測未連携'},
 detSub:{ko:'수심 0.5 m 다항목 수질계 · 0.5초 갱신',en:'Multi-parameter sonde at 0.5 m · 0.5 s refresh',ja:'水深0.5 m 多項目水質計・0.5秒更新'},
 wt:{ko:'수온',en:'Water temp.',ja:'水温'},coord:{ko:'좌표(공원 기준)',en:'Coordinates (park origin)',ja:'座標（公園基準）'},
 detFlow:{ko:'표 5 판정: DO 운전 전 대비 30~50% 증가 {a} · 탁도 20% 이상 저감 {b}<br>ORP 상승은 ·OH 등 산화성 활성종 증가와 함께 나타나는 참고 지표입니다.',
   en:'Table 5: DO +30–50% vs. pre-operation {a} · turbidity −20% or more {b}<br>Rising ORP is a reference indicator that accompanies more oxidizing species such as ·OH.',
   ja:'表5 判定：DO 運転前比30〜50%増加 {a}・濁度20%以上低減 {b}<br>ORPの上昇は·OHなど酸化性活性種の増加に伴う参考指標です。'},
 p1:{ko:'수변 전경 · 웅진 돔 방향',en:'Lakeside view toward the Woongjin dome',ja:'水辺の全景・ウンジンドーム方向'},
 p2:{ko:'항공 · 분수와 아파트',en:'Aerial · fountains and apartments',ja:'空撮・噴水とマンション'},
 p3:{ko:'호안 갈대 · 수면 반사',en:'Shoreline reeds · reflections',ja:'護岸のヨシ・水面の反射'},
 p4:{ko:'노을 항공',en:'Aerial at sunset',ja:'夕焼けの空撮'},
 p5:{ko:'보행 데크 위',en:'On the boardwalk',ja:'遊歩デッキの上'},
 p6:{ko:'파란 난간 데크',en:'Blue-railed deck',ja:'青い手すりのデッキ'},
 p7:{ko:'분수',en:'Fountain',ja:'噴水'},
 p8:{ko:'드론 · 남측 광장',en:'Drone · south plaza',ja:'ドローン・南側広場'},
 pl_lake:{ko:'상동호수',en:'Sangdong Lake',ja:'上洞湖'},
 pl_park:{ko:'상동호수공원',en:'Sangdong Lake Park',ja:'上洞湖水公園'},
 pl_supia:{ko:'부천호수식물원 수피아',en:'Supia Lake Botanic Garden',ja:'富川湖水植物園スピア'},
 pl_wj:{ko:'웅진플레이도시',en:'Woongjin Playdoci',ja:'ウンジン・プレイドシ'},
 pl_samsan:{ko:'삼산체육관역',en:'Samsan Gymnasium Stn.',ja:'三山体育館駅'},
 pl_kiosk:{ko:'상동호수공원 매점',en:'Park kiosk',ja:'公園売店'},
 pl_cheongun:{ko:'청운공원',en:'Cheongun Park',ja:'青雲公園'},
 pl_jomaru:{ko:'조마루로',en:'Jomaru-ro',ja:'チョマル路'},
 pl_gilju:{ko:'길주로',en:'Gilju-ro',ja:'キルジュ路'},
 pl_subyeon:{ko:'수변로',en:'Subyeon-ro',ja:'スビョン路'},
 pl_ring:{ko:'수도권제1순환고속도로',en:'Seoul Ring Expressway',ja:'首都圏第1循環高速道路'},
 pl_fount:{ko:'분수',en:'Fountain',ja:'噴水'},
 pl_deck:{ko:'보행 데크',en:'Boardwalk',ja:'遊歩デッキ'},
 pl_spire:{ko:'기념 첨탑 광장',en:'Spire plaza',ja:'記念尖塔広場'},
 photoPanel:{ko:'현장 사진 비교',en:'Site photo comparison',ja:'現地写真の比較'},
};
const LANGS=['ko','en','ja'];
let LANG=(()=>{try{const q=new URLSearchParams(location.search).get('lang');if(LANGS.includes(q))return q}catch(e){}
  try{const s=localStorage.getItem('sd_lang');if(LANGS.includes(s))return s}catch(e){}
  const n=(navigator.language||'ko').toLowerCase();return n.startsWith('ja')?'ja':n.startsWith('ko')?'ko':'en'})();
function T(k,vars){const e=I18N[k];let s=e?(e[LANG]||e.ko):k;if(vars)for(const v in vars)s=s.split('{'+v+'}').join(vars[v]);return s}
function applyI18n(){document.documentElement.lang=LANG;document.title=T('title');
  document.querySelectorAll('[data-i18n]').forEach(el=>el.textContent=T(el.dataset.i18n));
  document.querySelectorAll('[data-i18n-aria]').forEach(el=>el.setAttribute('aria-label',T(el.dataset.i18nAria)));
  document.querySelectorAll('[data-i18n-title]').forEach(el=>el.title=T(el.dataset.i18nTitle));
  document.querySelectorAll('#langs button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.lang===LANG)))}
applyI18n();
"""

# ---------- 1. static HTML → data-i18n ----------
rep('<div id="loading"><div><div id="ldtxt">실사 텍스처와 지형을 생성하는 중…</div>', '<div id="loading"><div><div id="ldtxt" data-i18n="loading">실사 텍스처와 지형을 생성하는 중…</div>')
rep('  <h1>상동호수공원 디지털트윈</h1>\n  <p>OpenStreetMap 실측 지형 + 현장 사진 기반 실사 재현. 측정 5지점과 PhotoNano 2기(호안 설치) 배치안을 표시합니다.</p>',
    '  <div id="langs" role="group" aria-label="Language"><button data-lang="ko" aria-pressed="true">한국어</button><button data-lang="en" aria-pressed="false">EN</button><button data-lang="ja" aria-pressed="false">日本語</button></div>\n  <h1 data-i18n="title">상동호수공원 디지털트윈</h1>\n  <p data-i18n="headP">OpenStreetMap 실측 지형 + 현장 사진 기반 실사 재현. 측정 5지점과 PhotoNano 2기(호안 설치) 배치안을 표시합니다.</p>')
rep('<div id="layers" class="panel" aria-label="레이어">\n  <div class="sec">레이어</div>', '<div id="layers" class="panel" aria-label="레이어" data-i18n-aria="layers">\n  <div class="sec" data-i18n="layers">레이어</div>')
for k, ko in [('lyBuild','건물·스카이라인'),('lyTree','수목·갈대'),('lyLabel','명칭'),('lyTB','테스트베드 시설'),('lyFount','분수 가동'),('lyCar','차량 흐름'),('lyHeat','DO 분포 (시뮬레이션)'),('lyRot','자동 회전')]:
    t2 = re.sub(r'(<input type="checkbox" id="%s"[^>]*>)%s</label>' % (k, re.escape(ko)), lambda m: m.group(1) + '<span data-i18n="%s">%s</span></label>' % (k, ko), t)
    assert t2 != t, k; t = t2
rep('<section id="photos" class="panel" aria-label="현장 사진 비교">\n    <div class="sec">현장 사진 비교</div>', '<section id="photos" class="panel" aria-label="현장 사진 비교" data-i18n-aria="photos">\n    <div class="sec" data-i18n="photos">현장 사진 비교</div>')
rep('<div class="hint">사진을 누르면 비슷한 시점으로 이동해 3D 위에 겹쳐 봅니다.</div>', '<div class="hint" data-i18n="photosHint">사진을 누르면 비슷한 시점으로 이동해 3D 위에 겹쳐 봅니다.</div>')
rep('<label for="tod">시간대 <b id="todv">', '<label for="tod"><span data-i18n="tod">시간대</span> <b id="todv">')
rep('<i style="background:var(--intake)"></i>취수 라인</span>', '<i style="background:var(--intake)"></i><span data-i18n="intakeLine">취수 라인</span></span>')
rep('<i style="background:var(--return)"></i>환수 라인</span>', '<i style="background:var(--return)"></i><span data-i18n="returnLine">환수 라인</span></span>')
rep('<span>DO mg/L (시뮬레이션)</span>', '<span data-i18n="heatLbl">DO mg/L (시뮬레이션)</span>')
rep('<label for="cmpo">겹침</label>', '<label for="cmpo" data-i18n="overlay">겹침</label>')
rep('<button id="cmpx">비교 닫기</button>', '<button id="cmpx" data-i18n="closeCmp">비교 닫기</button>')
rep('<nav id="views" class="panel" aria-label="시점">', '<nav id="views" class="panel" aria-label="시점" data-i18n-aria="views">')
for v, ko in [('bird','전경'),('top','평면'),('tb','1호기'),('tb2','2호기'),('water','수면 시점'),('walk','산책로'),('pur','정화 전경'),('under','수중 시점')]:
    t2 = re.sub(r'(<button data-v="%s" aria-pressed="(?:true|false)")>%s</button>' % (v, re.escape(ko)), lambda m: m.group(1) + ' data-i18n="v_%s">%s</button>' % (v, ko), t)
    assert t2 != t, v; t = t2
rep('<div class="modes" role="radiogroup" aria-label="표시 모드"><button id="mNormal" role="radio" aria-checked="false">일반 상태</button><button id="mPur" role="radio" aria-checked="true">정화 연출</button><kbd title="키보드 P로 전환">P</kbd>',
    '<div class="modes" role="radiogroup" aria-label="표시 모드" data-i18n-aria="modeGroup"><button id="mNormal" role="radio" aria-checked="false" data-i18n="mNormal">일반 상태</button><button id="mPur" role="radio" aria-checked="true" data-i18n="mPur">정화 연출</button><kbd title="키보드 P로 전환" data-i18n-title="kbdP">P</kbd>')
rep('<div id="purBody"><div class="sec">UFB 마이크로·나노버블 정화 연출</div>', '<div id="purBody"><div class="sec" data-i18n="purTitle">UFB 마이크로·나노버블 정화 연출</div>')
rep('<span id="purMsg">준비 중</span>', '<span id="purMsg" data-i18n="purReady">준비 중</span>')
rep('</span> 광촉매 활성산소 · 개념 시각화(반복)</div></div>', '</span> <span data-i18n="rosNote">광촉매 활성산소 · 개념 시각화(반복)</span></div></div>')
rep('<b style="color:#d8cf8a">정지</b><span>PhotoNano 미가동 · 현재 호수 상태(녹조·혐기성 오염 잔존 가정)</span></div><div class="pnote">측정 5지점은 운전 전 기준값으로 표시됩니다</div>',
    '<b style="color:#d8cf8a" data-i18n="stop">정지</b><span data-i18n="normMsg">PhotoNano 미가동 · 현재 호수 상태(녹조·혐기성 오염 잔존 가정)</span></div><div class="pnote" data-i18n="normNote">측정 5지점은 운전 전 기준값으로 표시됩니다</div>')
rep('<div id="credit">© 2026', '<div id="credit" data-i18n="credit">© 2026')
# CSS for language switch
rep('#head h1{', '#langs{position:absolute;top:10px;right:10px;display:flex;gap:2px}\n#langs button{font:600 10.5px var(--ui);color:var(--ink-2);background:rgba(255,255,255,.04);border:1px solid var(--glass-line);border-radius:4px;padding:2px 6px;cursor:pointer}\n#langs button[aria-pressed="true"]{color:#06222a;background:#8fe6ff;border-color:#8fe6ff}\n#head h1{')

# ---------- 2. JS ----------
rep("(function(){\n'use strict';\nconst $=s=>document.querySelector(s);", "(function(){\n'use strict';\nconst $=s=>document.querySelector(s);" + I18N_JS)
# loading steps
for i, ko in enumerate(['실사 텍스처 생성 중…','하늘·구름 생성 중…','지형·호수 생성 중…','도로·데크 생성 중…','건물·스카이라인 배치 중…','수목·갈대 식재 중…','분수·차량·테스트베드 배치 중…','마무리…'], 1):
    t2=re.sub(r"(step\(\.\d+,)'%s'," % re.escape(ko), lambda m: m.group(1)+"T('ld%d')," % i, t); assert t2!=t, ko; t=t2
# HUD messages
rep("PUR.hud.msg.textContent=rg>0.02?'다음 정화 사이클 준비 (반복 연출)':pct<99?'UFB 확산 · TiO₂/UVA 광촉매 ROS(·OH, O₂⁻)가 녹조·세균·곰팡이 산화 분해 중':'호수 전역 정화 완료 · 용존산소 회복'",
    "PUR.hud.msg.textContent=rg>0.02?T('hudRegrow'):pct<99?T('hudRun'):T('hudDone')")
# place labels -> keys
for k, ko in [('pl_lake','상동호수'),('pl_park','상동호수공원'),('pl_supia','부천호수식물원 수피아'),('pl_wj','웅진플레이도시'),('pl_samsan','삼산체육관역'),('pl_kiosk','상동호수공원 매점'),('pl_cheongun','청운공원'),('pl_jomaru','조마루로'),('pl_gilju','길주로'),('pl_subyeon','수변로'),('pl_ring','수도권제1순환고속도로'),('pl_fount','분수'),('pl_deck','보행 데크'),('pl_spire','기념 첨탑 광장')]:
    rep("addLabel('%s'," % ko, "addLabel('@%s'," % k)
rep("function addLabel(text,x,y,z,cls,group){const el=document.createElement('div');el.className='lbl '+(cls||'');el.textContent=text;labelsEl.appendChild(el);const o={el,v:new THREE.Vector3(x,y,z),group:group||'name'};LBL.push(o);return o}",
    "function addLabel(text,x,y,z,cls,group){const el=document.createElement('div');el.className='lbl '+(cls||'');labelsEl.appendChild(el);\n  const fn=typeof text==='function'?text:text.startsWith('@')?()=>T(text.slice(1)):()=>text;el.textContent=fn();const o={el,fn,v:new THREE.Vector3(x,y,z),group:group||'name'};LBL.push(o);return o}\nfunction relabel(){LBL.forEach(o=>o.el.textContent=o.fn())}")
rep("const l=addLabel(`${s.code} ${s.name}`,", "const l=addLabel(()=>`${s.code} ${T('s_'+s.id)}`,")
rep("UNITS.forEach(u=>addLabel(`PhotoNano ${u.name}`,", "UNITS.forEach(u=>addLabel(()=>`PhotoNano ${T('u'+u.no)}`,")
# state + panel
rep("function stateOf(c){return c<.05?['정화 전','#b8b36a','rgba(160,150,60,.18)']:c<.95?['정화 중','#9fe8ff','rgba(80,190,230,.16)']:['정화 완료','#7ff0b0','rgba(80,220,140,.16)']}",
    "function stateOf(c){const i=c<.05?0:c<.95?1:2;return [T('st'+i),['#b8b36a','#9fe8ff','#7ff0b0'][i],['rgba(160,150,60,.18)','rgba(80,190,230,.16)','rgba(80,220,140,.16)'][i],T('sts'+i)]}")
rep("${s.name.replace('부','').replace('연못 ','')}</td>", "${T('ss_'+s.id)}</td>")
rep("${st[0].replace('정화 ','')}</span></td></tr>", "${st[3]}</span></td></tr>")
rep("el.innerHTML=`<h2>수질 모니터링 · 5지점</h2><div class=\"sub\">정화 전선 통과에 따라 실시간 변화 (DO mg/L · 탁도 NTU · 운전 전 대비)</div>",
    "el.innerHTML=`<h2>${T('monTitle')}</h2><div class=\"sub\">${T('monSub')}</div>")
rep('<th style="text-align:left;font-weight:500">지점</th>', '<th style="text-align:left;font-weight:500">${T(\'thPoint\')}</th>')
rep('<th style="text-align:right;font-weight:500">탁도</th>', '<th style="text-align:right;font-weight:500">${T(\'turb\')}</th>')
t2 = re.sub(r"<div class=\"flow\">표 5 판정 기준: .*?부표를 누르면 지점별 상세값을 봅니다\.</div>",
    lambda m: "<div class=\"flow\">${T('monFlow',{d:Math.round(Math.hypot(UNITS[0].mod[0]-UNITS[1].mod[0],UNITS[0].mod[1]-UNITS[1].mod[1])),s:Math.round(Math.hypot(UNITS[0].int[0]-UNITS[0].ret[0],UNITS[0].int[1]-UNITS[0].ret[1]))})}</div>", t, flags=re.S)
assert t2 != t; t = t2
rep('<span class="pill">시뮬레이션 데이터 · 실측 연동 전</span>', "<span class=\"pill\">${T('simPill')}</span>", 2)
rep("el.innerHTML=`<h2>${selected.code} · ${selected.name}</h2><div class=\"sub\">수심 0.5 m 다항목 수질계 · 0.5초 갱신 · ",
    "el.innerHTML=`<h2>${selected.code} · ${T('s_'+selected.id)}</h2><div class=\"sub\">${T('detSub')} · ")
rep('<div class="kv" style="margin-top:6px"><span>탁도</span>', '<div class="kv" style="margin-top:6px"><span>${T(\'turb\')}</span>')
rep('<span>수온</span><b>${v.t.toFixed(1)} °C</b><span>좌표(공원 기준)</span>', '<span>${T(\'wt\')}</span><b>${v.t.toFixed(1)} °C</b><span>${T(\'coord\')}</span>')
rep("<div class=\"flow\">표 5 판정: DO 운전 전 대비 30~50% 증가 ${dd>=30?'✔':'…'} · 탁도 20% 이상 저감 ${dn<=-20?'✔':'…'}<br>ORP 상승은 ·OH 등 산화성 활성종 증가와 함께 나타나는 참고 지표입니다.</div>",
    "<div class=\"flow\">${T('detFlow',{a:dd>=30?'✔':'…',b:dn<=-20?'✔':'…'})}</div>")
# photos
for i, ko in enumerate(['수변 전경 · 웅진 돔 방향','항공 · 분수와 아파트','호안 갈대 · 수면 반사','노을 항공','보행 데크 위','파란 난간 데크','분수','드론 · 남측 광장'], 1):
    rep("{t:'%s'," % ko, "{t:'p%d'," % i)
rep("$('#cmpt').textContent=`사진 ${i+1} · ${m.t}`;", "$('#cmpt').textContent=`${T('photo')} ${i+1} · ${T(m.t)}`;")
rep("b.setAttribute('aria-label',`사진 ${i+1}: ${PHOTO_META[i].t}`);b.title=PHOTO_META[i].t;",
    "b.dataset.pi=i;b.setAttribute('aria-label',`${T('photo')} ${i+1}: ${T(PHOTO_META[i].t)}`);b.title=T(PHOTO_META[i].t);")
# language switch handler (after toggles)
rep("$('#tod').addEventListener('input',e=>setTime(+e.target.value));",
    "$('#tod').addEventListener('input',e=>setTime(+e.target.value));\n"
    "function setLang(l){if(!LANGS.includes(l))return;LANG=l;try{localStorage.setItem('sd_lang',l)}catch(e){}applyI18n();relabel();render();\n"
    "  document.querySelectorAll('#thumbs button').forEach(b=>{const i=+b.dataset.pi;b.title=T(PHOTO_META[i].t);b.setAttribute('aria-label',`${T('photo')} ${i+1}: ${T(PHOTO_META[i].t)}`)});\n"
    "  if(cmpIdx>=0)$('#cmpt').textContent=`${T('photo')} ${cmpIdx+1} · ${T(PHOTO_META[cmpIdx].t)}`}\n"
    "document.querySelectorAll('#langs button').forEach(b=>b.addEventListener('click',()=>setLang(b.dataset.lang)));")
p.write_text(t)
left = [l for l in t.split('\n') if re.search('[가-힣]', l) and 'I18N' not in l and not re.match(r"\s*(ko:|[a-z_0-9]+:\{ko:)", l)]
print('patched; remaining Korean lines (non-dict):', len(left))
for l in left: print('  ', l.strip()[:150])
