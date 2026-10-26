# 상동호수공원 디지털트윈 · NHI PhotoNano K-테스트베드 2026

부천 상동호수공원을 OpenStreetMap 실측 지형과 현장 사진을 바탕으로 재현한 3D 디지털트윈입니다.
NHI PhotoNano(UFB–TiO₂ 광촉매 융합 수질개선) 테스트베드의 측정 3지점과 Side-stream 모듈 배치안을 표시합니다.

## 실행
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
