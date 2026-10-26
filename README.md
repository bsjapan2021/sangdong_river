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
- All water-quality values and purification effects are **conceptual simulations**, not field measurements.

© 2026 NanoHydroIn Co., Ltd. All rights reserved — see [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).

## 日本語
OpenStreetMapの実測地形と現地写真に基づき、上洞湖水公園（韓国・富川市）をフォトリアルに再現した3Dデジタルツインです。NHI PhotoNano（UFB–TiO₂光触媒水質改善）K-water K-テストベッド2026向けに制作しました。

- **閲覧**：https://park.nanohydroin.com （v2 フォトリアル版）・`/v1`（シンプル版）。オフライン：`index.html` をダブルクリック。低スペックPCは `?q=low` を付加。
- **言語**：左上の `한국어 | EN | 日本語` ボタン、または `?lang=ja`。
- **主な機能**：反射する水面、ヨシ、青い手すりの遊歩デッキ、噴水、尖塔広場、樹種別の樹木、写真切り抜きのスカイライン、時間帯の光、車両の流れ、現地写真との重ね比較、護岸設置のPhotoNano 2基と測定5地点（S-01〜S-05）。
- **浄化演出**（`通常状態 | 浄化演出`、Pキー）：2か所の還水部からマイクロ・ナノバブルが湖全域へ広がり、水面のアオコ・嫌気性スラッジが消え、水中では光触媒ROS（·OH 青白、O₂⁻ 紫）が細菌・ウイルス・カビを分解。S-01〜S-05パネルはDO上昇・濁度低下を表5基準と比較して表示します。
- 水質数値と浄化演出はすべて**概念シミュレーション**であり、実測値ではありません。

© 2026 株式会社ナノハイドロイン（NanoHydroIn Co., Ltd.）All rights reserved — [LICENSE](LICENSE)・[NOTICE.md](NOTICE.md) を参照。
