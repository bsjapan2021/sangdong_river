# 상동호수공원 디지털트윈 · NHI PhotoNano K-테스트베드 2026

부천 상동호수공원을 OpenStreetMap 실측 지형과 현장 사진을 바탕으로 재현한 3D 디지털트윈입니다.
NHI PhotoNano(UFB–TiO₂ 광촉매 융합 수질개선) 테스트베드의 측정 3지점과 Side-stream 모듈 배치안을 표시합니다.

## 실행
- 웹: 배포 주소의 `/` (실사판 v2), `/v1` (단순 모델)
- 로컬: `index.html` 더블클릭 (완전 오프라인). 저사양 PC는 주소 뒤에 `?q=low`

## 주요 기능
- 실시간 반사 수면, 갈대·억새, 파란 난간 목재 데크, 분수 2기, 첨탑 광장, 수종별 수목
- 사진 누끼 원경 스카이라인, 절차적 하늘·구름, 시간대(해 위치·가로등) 변화, 차량 흐름
- 현장 사진 8장과 3D 시점 겹쳐보기
- PhotoNano 2기(서측·동측 호안, 호기 간 약 170 m) · 측정 5지점(S-01~05) 수질 패널(시뮬레이션) · DO 분포 레이어

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

지도 데이터 © OpenStreetMap contributors (ODbL) · ㈜나노하이드로인
