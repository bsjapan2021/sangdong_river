#!/usr/bin/env python3
"""상동호수공원 디지털트윈 빌드 스크립트
src/template.html + data/sd_osm.json  ->  sangdong_dt.html (온라인), sangdong_dt_offline.html (오프라인)
사용법:  python3 build.py
"""
import json, re, pathlib
R = pathlib.Path(__file__).resolve().parent
tpl = (R/'src/template.html').read_text(encoding='utf-8')
data = json.loads((R/'data/sd_osm.json').read_text(encoding='utf-8'))
online = tpl.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
(R/'sangdong_dt.html').write_text(online, encoding='utf-8')

three = (R/'src/vendor/three.min.js').read_text(encoding='utf-8')
orb = (R/'src/vendor/OrbitControls.js').read_text(encoding='utf-8')
h = online
h = h.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>', '<script>\n'+three+'\n</script>')
h = h.replace('<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>', '<script>\n'+orb+'\n</script>')
h = re.sub(r'<link rel="preconnect"[^>]*>\n', '', h)
h = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n', '', h)
h = h.replace('<title>상동호수공원 디지털트윈</title>',
  '<!doctype html>\n<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<title>상동호수공원 디지털트윈 (오프라인)</title>', 1)
h = h.replace('<div id="stage"></div>', '</head><body>\n<div id="stage"></div>', 1) + '\n</body></html>\n'
(R/'sangdong_dt_offline.html').write_text(h, encoding='utf-8')
print('built: sangdong_dt.html (%d KB), sangdong_dt_offline.html (%d KB)' % (len(online.encode())//1024, len(h.encode())//1024))
