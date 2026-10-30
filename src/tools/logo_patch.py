#!/usr/bin/env python3
"""v2 패치: 스플래시·로그인 카드·상단 패널에 주식회사 나노하이드로인 공식 로고(SVG) 적용"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
p = ROOT/'src/template_v2.html'; t = p.read_text()
def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (a[:80], t.count(a)); t = t.replace(a, b)
rep("#splash .logo{width:74px;height:74px;margin:0 auto 4px;border-radius:50%;display:grid;place-items:center;\n  background:radial-gradient(circle at 35% 30%,#bff6ff,#3fb7cf 55%,#0d5160);box-shadow:0 0 40px rgba(110,220,240,.45),inset 0 -6px 14px rgba(0,0,0,.3);font:800 20px var(--ui);color:#04222a}",
    ".nhlogo{background:url(\"__LOGO__\") center/contain no-repeat}\n#splash .logo{width:min(260px,62vw);aspect-ratio:298/230;margin:0 auto 10px;filter:drop-shadow(0 0 24px rgba(120,225,245,.35));animation:lgIn 1.2s ease-out both}\n@keyframes lgIn{from{opacity:0;transform:scale(.94)}to{opacity:1;transform:none}}\n#auth .alogo{width:118px;aspect-ratio:298/230;margin:0 auto 10px}\n#head .hlogo{width:62px;aspect-ratio:298/230;float:right;margin:-2px 0 0 8px;opacity:.92}")
rep('<div class="logo">NHI</div>\n    <div class="eb">NANOHYDROIN CO., LTD.</div>', '<div class="logo nhlogo" role="img" aria-label="NANOHYDROIN — 79nm : The Next Dimension"></div>')
rep('<div class="card">\n    <div class="top">', '<div class="card">\n    <div class="alogo nhlogo" role="img" aria-label="NANOHYDROIN"></div>\n    <div class="top">')
rep('<div id="head" class="panel">\n', '<div id="head" class="panel">\n  <div class="hlogo nhlogo" role="img" aria-label="NANOHYDROIN"></div>\n')
p.write_text(t); print('logo patched')
