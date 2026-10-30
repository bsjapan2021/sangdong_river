#!/usr/bin/env python3
"""v2 패치: 좌측 '레이어' 카드와 '리모콘' 카드 겹침 해소 + 두 카드 가로폭 통일(222px).
   리모콘이 보이면 레이어 카드 바로 아래에 배치하고, 화면 높이가 모자라면 레이어 목록을 자동 접기(제목 클릭으로 펼침)."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
p = ROOT/'src/template_v2.html'; t = p.read_text()
def rep(a, b):
    global t
    assert t.count(a) == 1, (a[:70], t.count(a)); t = t.replace(a, b)
rep("#layers{top:calc(116px + env(safe-area-inset-top,0px));left:max(12px,env(safe-area-inset-left,0px));padding:10px 12px;width:196px}",
    "#layers{top:calc(116px + env(safe-area-inset-top,0px));left:max(12px,env(safe-area-inset-left,0px));padding:10px 12px;width:222px;box-sizing:border-box}\n"
    "#layers .sec{cursor:pointer;display:flex;justify-content:space-between;align-items:center}#layers .sec::after{content:'▾';font-size:10px;letter-spacing:0}\n"
    "#layers.fold .sec{margin-bottom:0}#layers.fold .sec::after{content:'▸'}#layers.fold .tg{display:none}")
rep("#rc{left:16px;bottom:calc(76px + env(safe-area-inset-bottom,0px));width:178px;padding:9px 10px;",
    "#rc{left:max(12px,env(safe-area-inset-left,0px));bottom:calc(76px + env(safe-area-inset-bottom,0px));width:222px;box-sizing:border-box;padding:10px 12px;")
rep("#rc{left:10px;bottom:calc(150px + env(safe-area-inset-bottom,0px));width:156px}#rc .rn{display:none}",
    "#rc{bottom:calc(150px + env(safe-area-inset-bottom,0px))}#rc .rn{display:none}}\n@media (max-width:760px){#rc{left:10px;width:180px}")
JS = r'''
/* 좌측 카드 배치: 리모콘은 레이어 카드 바로 아래(10px 간격), 공간 부족 시 레이어 목록 자동 접기 */
let lyUserOpen=false;
function layoutLeft(){const L=$('#layers'),R=$('#rc');if(!L||!R)return;L.style.maxHeight='';L.style.overflowY='';
  const lv=getComputedStyle(L).display!=='none',rv=!R.hidden;
  if(!rv||!lv){R.style.top='';R.style.bottom='';if(L.dataset.auto)L.classList.remove('fold');L.dataset.auto='';return}
  const bottomLimit=innerHeight-(innerWidth<=900?150:76);
  const place=()=>{const top=L.getBoundingClientRect().bottom+10;return top+R.offsetHeight<=bottomLimit?top:null};
  if(L.dataset.auto&&!lyUserOpen){L.classList.remove('fold');L.dataset.auto=''}
  let top=place();
  if(top===null&&!lyUserOpen&&!L.classList.contains('fold')){L.classList.add('fold');L.dataset.auto='1';top=place()}
  if(top!==null){R.style.top=top+'px';R.style.bottom='auto';return}
  R.style.top='';R.style.bottom='';const lim=R.getBoundingClientRect().top-10-L.getBoundingClientRect().top;L.style.maxHeight=Math.max(40,lim)+'px';L.style.overflowY='auto'}   /* 그래도 부족하면 레이어 카드만 스크롤 */
$('#layers .sec').addEventListener('click',()=>{const L=$('#layers');const f=L.classList.toggle('fold');L.dataset.auto='';lyUserOpen=!f;layoutLeft()});
new MutationObserver(layoutLeft).observe($('#rc'),{attributes:true,attributeFilter:['hidden']});
addEventListener('resize',layoutLeft);setTimeout(layoutLeft,0);
'''
rep("\nstep(.05,T('ld1'),buildTextures);", JS + "\nstep(.05,T('ld1'),buildTextures);")
p.write_text(t); print('leftcol patched')
