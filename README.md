# 상동호수공원 디지털트윈 · NHI PhotoNano K-테스트베드 2026

**한국어** · [English](#english) · [日本語](#日本語)

부천 상동호수공원을 OpenStreetMap 실측 지형과 현장 사진을 바탕으로 재현한 3D 디지털트윈입니다.
NHI PhotoNano(UFB–TiO₂ 광촉매 융합 수질개선) 테스트베드의 측정 3지점과 Side-stream 모듈 배치안을 표시합니다.

## 실행
- 화면 언어: 왼쪽 위 `한국어 | EN | 日本語` 버튼, 또는 주소에 `?lang=ko|en|ja` (선택은 브라우저에 기억)
- 웹: https://park.nanohydroin.com (실사판 v2) · https://park.nanohydroin.com/v1 (단순 모델) · 보조 주소 https://sangdong.vercel.app
- 로컬: `index.html` 더블클릭 (완전 오프라인). 저사양 PC는 주소 뒤에 `?q=low`

## 주요 기능
- 실시간 반사 수면, 갈대·억새, 파란 난간 목재 데크, 분수 2기, 첨탑 광장, 수종별 수목
- 사진 누끼 원경 스카이라인, 절차적 하늘·구름, 시간대(해 위치·가로등) 변화, 차량 흐름
- 현장 사진 8장과 3D 시점 겹쳐보기
- PhotoNano 2기(서측·동측 호안, 호기 간 약 170 m) · 측정 5지점(S-01~05) 수질 패널(시뮬레이션) · DO 분포 레이어

- **UFB 정화 연출**: 두 환수부에서 마이크로·나노버블이 분사되어 정화 전선이 호수 전역으로 서서히 확산(48초 반복). 수면 녹조·혐기성 슬러지 막이 걷히고, 수중의 세균·바이러스·곰팡이·조류 입자가 소멸, 나노버블 헤이즈가 채워짐. `정화 전경`·`수중 시점` 버튼, 정화 진행률 표시. 개념 시각화이며 실측 결과가 아님

- **수질 패널 연동**: 정화 전선이 측정 지점을 지나면 S-01~S-05의 DO 상승·탁도 저감·ORP 상승이 실시간 반영(운전 전 대비 %, 표 5 기준 달성 시 초록 표시)
- **광촉매 ROS 연출**: 수중에 ·OH(청백)·O₂⁻(보라) 빛 입자가 환수부와 정화 전선 뒤에 집중, 미생물이 ROS를 받아 흔들리며 분해·소멸

- **표시 모드 토글**: 상단 `일반 상태 | 정화 연출` 버튼(또는 키보드 P). 일반 상태는 PhotoNano 미가동·운전 전 기준값, 정화 연출은 처음부터 다시 재생

- **보트 운행(녹조제거 쌍동선)**: 상단 `보트 운행` 버튼(또는 키보드 B). STL 실측 모델(1.6 m)이 ① **수계 인식**(위성영상+LiDAR 경계 스캔, 수면적·운항 금지구역 등록) → ② **경로 최적화**(동서/남북 교차 왕복 커버리지 경로, 예상 커버리지 표시) → ③ **자율 운항**(GNSS RTK 위성 좌표 수신·LiDAR 360° 스캔, 부유 장애물 감지 시 회피 기동 후 경로 복귀) 순서로 미션을 수행하며 나노버블·광촉매 ROS로 녹조를 제거. 배속 ×1/×10/×30, 보트 추적 카메라, 미션 재시작, 고착 시 후진·탈출 경로 재계산, **리모콘 수동 조종**(원형 조이스틱 드래그·방향키/WASD, 5초 무입력 시 자율운항 복귀)

- **데크 기둥 사이 통과**: 데크 밑은 기둥 사이 게이트로만 수직 통과, 게이트 서행(50%)·마스트 여유고 검사·게이트별 3회 왕복 세정, 3컷 시네마틱 카메라(진입→데크 밑→빠져나오기)
- **시간대·그림자·UVA**: 시간대는 한국 표준시와 실시간 동기화(● LIVE, 슬라이더로 수동 조절 가능). 태양 위치로 데크 그림자를 투영하고 실제 그늘 또는 야간에서만 UVA 365 nm 출력 100%(평시 60%), 야간 UVA 빛 강화
- **효과음**: 물소리·모터음·버블(WebAudio 합성, 🔊 토글) — 브라우저 정책상 첫 클릭 후 재생
- **게이트 운항 보고서**(📊): 게이트별 통과 횟수·UVA 가동시간·ROS 발생 지수(시뮬레이션 입자 수)·마지막 통과, 서버 저장(회원)·PDF 출력

## 회원 · 접속자 관리
- 첫 화면은 **스플래시 → 로그인**. 회원가입(이름·이메일·연락처·소속·이용 목적, 개인정보 동의) → **이메일 인증**(메일 설정 시) → **최고관리자 승인** 후 이용
- 비밀번호 찾기(메일 재설정 링크, 1시간·1회용), 로그인 후 비밀번호 변경, 연속 실패 시 10분 잠금
- **접속자 관리(최고관리자 전용)**: 회원 승인·차단·차단 해지·메일 인증 처리·임시 비밀번호·삭제, 접속자(IP·지역·브라우저·회원·접속 중 여부) 조회, IP 차단·해제. 일반 회원에게는 버튼이 보이지 않고 서버 API도 최고관리자 토큰만 허용
- **회원 화면 일괄 업데이트**: 새 버전 배포 후 관리자창 ‘업데이트’ 탭에서 버튼을 누르면 접속 중인 모든 화면이 안내 후 10초 뒤 자동 새로고침(최대 45초 내 반영)
- 로컬 `index.html`(file://) 실행은 오프라인 열람용이라 로그인 없이 열립니다

### 서버 설정 (Vercel 환경변수 — 값은 저장소에 커밋하지 않음)
| 변수 | 내용 |
|---|---|
| `DATABASE_URL` / `DATABASE_POSTGRES_URL` | Neon Postgres (Vercel Storage 연결 시 자동 주입) |
| `ADMIN_PASSWORD` | 최고관리자(`ADMIN_EMAIL`, 기본 kr.seunghunyeo@gmail.com) 최초 비밀번호 — 첫 요청 시 해시로만 저장 |
| `MAIL_USER`, `MAIL_APP_PASSWORD` | Gmail 주소 + 앱 비밀번호 → 가입 인증·비밀번호 재설정·승인 알림 메일. 미설정 시 메일 없이 ‘관리자 승인’만으로 운영 |
| `AUTH_SECRET` (선택) | 토큰 서명 키. 미설정 시 DB에 자동 생성·보관 |

## 빌드
```
python3 src/tools/make_assets.py   # photos/ → 누끼 스카이라인·비교용 사진
python3 build_v2.py                # sangdong_dt_v2(.html/_offline.html)
python3 build.py                   # v1
cp sangdong_dt_v2_offline.html index.html
```

## 구조
| 경로 | 내용 |
|---|---|
| `index.html` | 배포용 (v2 오프라인판과 동일) |
| `src/template_v2.html`, `src/template.html` | 화면·3D 소스 |
| `src/assets/` | 스카이라인 누끼, 비교용 사진 |
| `src/vendor/` | three.js r128, OrbitControls, Water |
| `data/sd_osm.json` | OSM 지형 (원점 37.5038N 126.7450E, m, x=동 z=남) |
| `photos/` | 현장 참고 사진 원본 |
| `api/`, `lib/` | Vercel 서버리스 API (회원 인증·관리자·접속 기록) |
| `data/ssangdong_ship.stl`, `src/assets/boat_mesh.json` | 녹조제거 쌍동선 STL 원본·변환 메시 |

## 저작권 · 라이선스
© 2026 주식회사 나노하이드로인 (NanoHydroIn Co., Ltd.). All rights reserved.
본 저장소의 소스코드·3D 장면·연출·문서는 주식회사 나노하이드로인의 저작물이며, 사전 서면 동의 없는 복제·수정·배포·상업적 이용을 금지합니다(열람 및 K-테스트베드 심사 목적 시연은 허용). 자세한 내용은 [LICENSE](LICENSE)를 참조하십시오.
제3자 구성요소(three.js — MIT, OpenStreetMap — ODbL, 웹 폰트 — OFL, 현장 참고 사진 — 각 원저작자)는 각 원 라이선스를 따릅니다: [NOTICE.md](NOTICE.md)


---

## English
Photoreal 3D digital twin of Sangdong Lake Park (Bucheon, Korea), built from surveyed OpenStreetMap terrain and site photos, for the NHI PhotoNano (UFB–TiO₂ photocatalytic water-treatment) K-water K-Testbed 2026.

- **Open**: https://park.nanohydroin.com (v2, photoreal) · `/v1` (simple model). Offline: double-click `index.html`. Low-spec PCs: add `?q=low`.
- **Language**: `한국어 | EN | 日本語` buttons at top-left, or `?lang=en` / `?lang=ja`.
- **Features**: reflective water, reeds, blue-railed boardwalks, fountains, spire plaza, species-specific trees, cut-out photo skyline, time-of-day lighting, traffic, site-photo overlay comparison, 2 shoreline PhotoNano units with 5 monitoring points (S-01–S-05).
- **Purification mode** (`Normal | Purification`, key `P`): micro/nano-bubble plumes spread from both returns across the lake; algae and anaerobic sludge clear on the surface; underwater, photocatalytic ROS (·OH cyan, O₂⁻ violet) break down bacteria, viruses and fungi; the S-01–S-05 panel tracks DO rise and turbidity drop against Table 5 criteria.
- **Boat mission** (`Boat`, key `B`): the algae-removal catamaran (STL, 1.6 m) runs ① water-area mapping (satellite imagery + LiDAR boundary scan, no-go zones) → ② coverage-path optimization (lawnmower / cross-pass) → ③ autonomous run with GNSS RTK fixes and 360° LiDAR, avoiding floating obstacles and rejoining the route, spraying nano-bubbles + photocatalytic ROS.
- **Members & access**: splash → sign-in; sign-up with email verification and super-admin approval; password reset; super-admin-only access management (approve / block / unblock members, visitor IPs, IP blocking). Server env vars: `DATABASE_URL` (Neon), `ADMIN_PASSWORD`, `MAIL_USER` + `MAIL_APP_PASSWORD` (Gmail app password), optional `AUTH_SECRET`.
- All water-quality values and purification effects are **conceptual simulations**, not field measurements.

© 2026 NanoHydroIn Co., Ltd. All rights reserved — see [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).

## 日本語
OpenStreetMapの実測地形と現地写真に基づき、上洞湖水公園（韓国・富川市）をフォトリアルに再現した3Dデジタルツインです。NHI PhotoNano（UFB–TiO₂光触媒水質改善）K-water K-テストベッド2026向けに制作しました。

- **閲覧**：https://park.nanohydroin.com （v2 フォトリアル版）・`/v1`（シンプル版）。オフライン：`index.html` をダブルクリック。低スペックPCは `?q=low` を付加。
- **言語**：左上の `한국어 | EN | 日本語` ボタン、または `?lang=ja`。
- **主な機能**：反射する水面、ヨシ、青い手すりの遊歩デッキ、噴水、尖塔広場、樹種別の樹木、写真切り抜きのスカイライン、時間帯の光、車両の流れ、現地写真との重ね比較、護岸設置のPhotoNano 2基と測定5地点（S-01〜S-05）。
- **浄化演出**（`通常状態 | 浄化演出`、Pキー）：2か所の還水部からマイクロ・ナノバブルが湖全域へ広がり、水面のアオコ・嫌気性スラッジが消え、水中では光触媒ROS（·OH 青白、O₂⁻ 紫）が細菌・ウイルス・カビを分解。S-01〜S-05パネルはDO上昇・濁度低下を表5基準と比較して表示します。
- **ボート運航**（`ボート運航`、Bキー）：アオコ除去双胴船（STL、1.6 m）が ①水域認識（衛星画像＋LiDAR境界スキャン、禁止区域登録）→ ②カバレッジ経路最適化 → ③GNSS RTK・LiDAR 360°による自律運航（浮遊障害物を回避し経路へ復帰）を行い、ナノバブルと光触媒ROSでアオコを除去。
- **会員・アクセス管理**：スプラッシュ→ログイン。会員登録はメール認証と最高管理者の承認が必要。パスワード再設定、最高管理者専用のアクセス管理（会員の承認・遮断・解除、接続IP一覧、IP遮断）。
- 水質数値と浄化演出はすべて**概念シミュレーション**であり、実測値ではありません。

© 2026 株式会社ナノハイドロイン（NanoHydroIn Co., Ltd.）All rights reserved — [LICENSE](LICENSE)・[NOTICE.md](NOTICE.md) を参照。
