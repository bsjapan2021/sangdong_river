#!/usr/bin/env python3
"""v2 패치: 빗줄기 가시성 강화(밀도↑·길이↑·불투명도↑) — weather_patch 적용 후 템플릿에 직접 반영"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
p = ROOT/'src/template_v2.html'; t = p.read_text()
def rep(a, b):
    global t
    assert t.count(a) == 1, (a[:70], t.count(a)); t = t.replace(a, b)
rep("const WX_RAIN=wxField(LOW?2600:7000,70,false)","const WX_RAIN=wxField(LOW?5000:9000,60,false)")
rep("float L=.55+aR*.5;","float L=1.+aR*.9;")
rep("float a=uA*vA*.5;if(a<.01)discard;gl_FragColor=vec4(.78,.83,.9,a);","float a=uA*vA*.7;if(a<.01)discard;gl_FragColor=vec4(.82,.87,.94,a);")
p.write_text(t); print('rain2 patched')
