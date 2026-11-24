from pathlib import Path
import json,re,hashlib
from playwright.sync_api import sync_playwright

OUT=Path(__file__).resolve().parent
BASE='https://bobazbob.github.io/cuojuan-scroll/'
LOCAL='http://127.0.0.1:4173/'
PROJECT=OUT.parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
result={'fileComparisons':[],'layoutDetails':[]}
with sync_playwright() as p:
 b=p.chromium.launch()
 c=b.new_context(viewport={'width':1600,'height':900})
 html=c.request.get(BASE+'daiyu-huaguoshan.html').text()
 paths=re.findall(r'(?:src|href)="\./([^\"]+\.(?:js|css))"',html)
 wanted=['huaguoshan_layer1_back','huaguoshan_layer2_mid','huaguoshan_layer3_ground','huaguoshan_layer4_front',
         'daiyu_neutral','daiyu_happy','daiyu_upset','scroll_frame','paper_texture','cuojuan-serif']
 for name in wanted:
  matches=list((PROJECT/'dist/assets').glob(name+'-*'))
  assert len(matches)==1,(name,matches)
  paths.append('assets/'+matches[0].name)
 for path in paths:
  pr=c.request.get(BASE+path);lr=c.request.get(LOCAL+path)
  result['fileComparisons'].append({'path':path,'publicHTTP':pr.status,'localHTTP':lr.status,
    'sha256':sha(pr.body()),'publicEqualsLocal':pr.body()==lr.body(),
    'publicEqualsDist':pr.body()==(PROJECT/'dist'/path).read_bytes()})
 page=c.new_page();page.goto(BASE,wait_until='networkidle');page.wait_for_timeout(600)
 page.screenshot(path=str(OUT/'public-root-H03.png'),full_page=True)
 result['root']={'url':page.url,'title':page.title(),'h03Entry':bool(page.locator('script[src*="h03-"]').count())}
 c.close()
 for w,h in [(1600,900),(390,844),(320,568)]:
  c=b.new_context(viewport={'width':w,'height':h},has_touch=w<500,is_mobile=w<500)
  page=c.new_page();page.goto(BASE+'daiyu-huaguoshan.html',wait_until='networkidle')
  page.wait_for_selector('#page[data-phase="cover"]')
  for label in ['展开画卷','花果山']:
   page.locator('#reader-actions button',has_text=label).click()
  page.wait_for_timeout(1300)
  page.locator('#reader-actions button',has_text='林黛玉').click();page.locator('#drop').click()
  page.wait_for_timeout(400)
  d=page.evaluate('''()=>{
    const el=id=>document.getElementById(id),box=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};};
    const a=box(el('art')),f=box(el('figure')),r=box(el('reader')),t=box(el('reader-text'));
    const font=getComputedStyle(el('reader-text'));
    return {innerWidth,innerHeight,clientWidth:document.documentElement.clientWidth,
      stageStyle:el('stage').getAttribute('style'),scrollStyle:el('scroll').getAttribute('style'),
      pagePadding:getComputedStyle(el('page')).padding,art:a,artRatio:a.w/a.h,figure:f,figureRatio:f.w/f.h,
      distortionPercent:(16/9/(a.w/a.h)-1)*100,reader:r,text:t,
      fontSize:font.fontSize,lineHeight:font.lineHeight,actualLines:t.h/parseFloat(font.lineHeight),
      mask:getComputedStyle(el('reader')).maskImage};}''')
  result['layoutDetails'].append(d)
  page.screenshot(path=str(OUT/f'diagnostic-actual-{w}.png'),full_page=True)
  if w==1600:
   # Local DOM diagnostic only. Not a code change or accepted screenshot of implementation.
   page.add_style_tag(content='#reader { mask-image:none!important; -webkit-mask-image:none!important; }')
   page.screenshot(path=str(OUT/'diagnostic-mask-off-1600.png'),full_page=True)
  c.close()
 b.close()
(OUT/'diagnostics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'root':result['root'],'comparisons':len(result['fileComparisons']),
 'allSame':all(x['publicEqualsLocal'] and x['publicEqualsDist'] for x in result['fileComparisons']),
 'layouts':result['layoutDetails']},ensure_ascii=False,indent=2))
