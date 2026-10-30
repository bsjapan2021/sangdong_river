#!/usr/bin/env python3
"""상동호수공원 디지털트윈 v2 (실사판) 빌드
src/template_v2.html + data/sd_osm.json + src/assets(누끼 스카이라인, 현장 사진)
 -> sangdong_dt_v2.html (CDN 사용) / sangdong_dt_v2_offline.html (완전 오프라인)
사용법: python3 build_v2.py   (에셋 재생성: python3 src/tools/make_assets.py)
"""
import json, re, base64, pathlib
R = pathlib.Path(__file__).resolve().parent
A = R/'src/assets'
def uri(p, mime): return f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()
tpl = (R/'src/template_v2.html').read_text(encoding='utf-8')
data = json.loads((R/'data/sd_osm.json').read_text(encoding='utf-8'))
photos = [uri(A/f'photo_{i}.jpg','image/jpeg') for i in range(1,9)]
h = (tpl.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',',':')))
        .replace('__SKYLINE__', uri(A/'skyline_cut.png','image/png'))
        .replace('__PHOTOS__', json.dumps(photos))
        .replace('__BOAT__', (A/'boat_mesh.json').read_text())
        .replace('__LOGO__', uri(A/'logo_nanohydroin_light.svg','image/svg+xml'))
        .replace('__BUILD__', __import__('datetime').datetime.utcnow().strftime('%Y%m%d-%H%M%S')))
(R/'sangdong_dt_v2.html').write_text(h, encoding='utf-8')
V = R/'src/vendor'
off = h
for url, f in [('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js','three.min.js'),
               ('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js','OrbitControls.js'),
               ('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/objects/Water.js','Water.js')]:
    tag = f'<script src="{url}"></script>'; assert tag in off, f
    off = off.replace(tag, '<script>\n'+(V/f).read_text(encoding='utf-8')+'\n</script>')
off = re.sub(r'<link rel="preconnect"[^>]*>\n','',off)
off = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n','',off)
off = off.replace('<title>상동호수공원 디지털트윈</title>','<!doctype html>\n<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<title>상동호수공원 디지털트윈 v2 (오프라인)</title>',1)
off = off.replace('<div id="stage"></div>','</head><body>\n<div id="stage"></div>',1) + '\n</body></html>\n'
(R/'sangdong_dt_v2_offline.html').write_text(off, encoding='utf-8')
print('built v2: online %d KB, offline %d KB' % (len(h.encode())//1024, len(off.encode())//1024))
