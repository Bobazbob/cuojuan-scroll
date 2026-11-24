"""B只读首场景复核。只写本验收目录，不改实现；需要现有4173服务。"""
from pathlib import Path
import json, hashlib, time, re
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent
LOCAL = 'http://127.0.0.1:4173/daiyu-huaguoshan.html'
PUBLIC = 'https://bobazbob.github.io/cuojuan-scroll/daiyu-huaguoshan.html'
ROOT = 'https://bobazbob.github.io/cuojuan-scroll/'
RESULT = {'scope':'daiyu_huaguoshan only', 'cases':[], 'errors':[], 'network':[], 'comparisons':[]}
hash_ = lambda b: hashlib.sha256(b).hexdigest()

def snap(page, case, tag):
    dest = OUT / case / (tag+'.png')
    dest.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(dest), full_page=True)
    d = page.evaluate('''() => {
      const box = e => {if (!e) return null; const r=e.getBoundingClientRect();
        return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom};};
      const art=document.querySelector('#art'), a=art.getBoundingClientRect();
      const f=document.querySelector('#figure'), r=f.getBoundingClientRect();
      const reader=document.querySelector('#reader'), text=document.querySelector('#reader-text');
      return {phase:document.querySelector('#page').dataset.phase,
        layout:document.querySelector('#page').dataset.layout,
        pagination:document.querySelector('#page').dataset.page,
        text:text.innerText, title:document.querySelector('#reader-title').innerText,
        art:box(art),reader:box(reader),textBox:box(text),figure:box(f),figureHidden:f.hidden,
        foot: f.hidden?null:{x:(r.x+r.width*.499-a.x)/a.width*1600,
          y:(r.y+r.height*.980-a.y)/a.height*900,h:r.height/a.height*900,ratio:r.width/r.height},
        mask:getComputedStyle(reader).maskImage,fontSize:getComputedStyle(text).fontSize,
        scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth,
        active:document.activeElement?.id||document.activeElement?.textContent?.slice(0,40),
        buttons:[...document.querySelectorAll('button')].filter(e=>e.getClientRects().length)
          .map(e=>({label:e.innerText||e.getAttribute('aria-label'),...box(e)})),
        images:[...document.images].filter(e=>!e.hidden).map(e=>({src:e.src,decoded:e.complete&&e.naturalWidth>0,
          natural:[e.naturalWidth,e.naturalHeight],box:box(e)}))};}''')
    d['screenshot'] = str(dest.relative_to(OUT))
    return d

def click(page,label,touch=False):
    button=page.locator('#reader-actions button',has_text=label).first
    (button.tap if touch else button.click)()

def phase(page): return page.get_attribute('#page','data-phase')

def open_to_intro(page,case,records,touch=False):
    page.wait_for_selector('#page[data-phase="cover"]')
    page.wait_for_timeout(1300)
    records.append(snap(page,case,'01_cover'))
    click(page,'展开画卷',touch)
    click(page,'花果山',touch)
    page.wait_for_timeout(1300)
    records.append(snap(page,case,'02_character'))
    click(page,'林黛玉',touch)
    records.append(snap(page,case,'03_placement'))
    a=page.locator('#art').bounding_box()
    if touch: page.touchscreen.tap(a['x']+a['width']*.30,a['y']+a['height']*.5)
    else: page.mouse.click(a['x']+a['width']*.30,a['y']+a['height']*.5)
    assert phase(page)=='placement'
    assert '圆环' in page.inner_text('#reader-text')
    (page.locator('#drop').tap if touch else page.locator('#drop').click)()
    page.wait_for_selector('#page[data-phase="intro"]')
    page.wait_for_timeout(300)

def read_pages(page,case,records,prefix,touch=False):
    seen=[]
    current=phase(page)
    for i in range(12):
        d=snap(page,case,f'{prefix}_{i+1}')
        records.append(d);seen.append(d['text'])
        label=page.locator('#reader-actions button').first.inner_text()
        if label!='继续': return ''.join(seen)
        click(page,'继续',touch)
        if phase(page)!=current: return ''.join(seen)
    raise RuntimeError('Unexpected >12 pages')

def alpha_regions(page):
    return page.evaluate('''() => { const c=document.querySelector('#effects');
      const d=c.getContext('2d').getImageData(0,0,1600,900).data;
      const count=(x0,y0,x1,y1)=>{let n=0,max=0;for(let y=y0;y<y1;y++)for(let x=x0;x<x1;x++){
        const a=d[(y*1600+x)*4+3];if(a)n++;max=Math.max(max,a);}return {nonzero:n,maxAlpha:max};};
      return {whole:count(0,0,1600,900), face:count(930,190,1070,300),
        reading:count(96,720,1504,873),controls:count(1152,36,1504,108)};}''')

def branch(page,case,index,records,touch=False):
    if index: open_to_intro(page,case,records,touch)
    s=page.evaluate('window.__cuojuan.game.getState()')
    text=read_pages(page,case,records,'04_intro',touch)
    assert text==s['story']['intro']
    assert phase(page)=='choice'
    records.append(snap(page,case,'05_choice'))
    b=page.locator('#reader-actions button').nth(index)
    (b.tap if touch else b.click)()
    page.wait_for_selector('#page[data-phase="ending"]')
    samples=[]
    for i in range(12):
        page.wait_for_timeout(170)
        samples.append(alpha_regions(page))
        if i in (2,5): records.append(snap(page,case,f'06_effect_{i}'))
    s=page.evaluate('window.__cuojuan.game.getState()')
    src=page.get_attribute('#figure','src')
    assert s['ending']['endingId'].endswith(f'end_{index+1}')
    assert ('upset' if index==0 else 'happy') in src
    text=read_pages(page,case,records,'07_ending',touch)
    assert text==s['ending']['text']
    click(page,'重玩',touch)
    assert phase(page)=='cover'
    assert page.evaluate('window.__cuojuan.game.getState().ending') is None
    cleared=alpha_regions(page)
    assert cleared['whole']['nonzero']==0
    records.append(snap(page,case,'08_replay'))
    return {'endingId':s['ending']['endingId'],'expression':s['expression'],'effectSamples':samples,
      'replayCanvas':cleared,'introExact':True,'endingExact':True}

def add_errors(page,case):
    page.on('pageerror',lambda e:RESULT['errors'].append({'case':case,'type':'pageerror','message':str(e)}))
    page.on('console',lambda m:RESULT['errors'].append({'case':case,'type':'console','message':m.text}) if m.type=='error' else None)
    page.on('response',lambda r:RESULT['network'].append({'case':case,'status':r.status,'url':r.url}) if r.status>=400 else None)
    page.on('requestfailed',lambda r:RESULT['network'].append({'case':case,'failed':r.failure,'url':r.url}))

with sync_playwright() as p:
    browser=p.chromium.launch()
    RESULT['browser']=browser.version
    api=browser.new_context()
    # Fetch real deployment entry and compare all nine preloaded runtime images, JS and CSS.
    for url in (LOCAL,PUBLIC,ROOT):
        try:
            r=api.request.get(url,timeout=30000)
            body=r.body()
            RESULT['comparisons'].append({'url':url,'status':r.status,'sha256':hash_(body),
                'scripts':re.findall(r'(?:src|href)="([^"]+\.(?:js|css))"',body.decode('utf8'))})
        except Exception as e: RESULT['comparisons'].append({'url':url,'error':str(e)})
    api.close()
    for name,w,h,touch,url in [
        ('public_desktop',1600,900,False,PUBLIC),
        ('touch_portrait',390,844,True,PUBLIC),
        ('touch_landscape',844,390,True,PUBLIC),
        ('narrow_320',320,568,True,LOCAL),
    ]:
        print('Running',name,flush=True)
        context=browser.new_context(viewport={'width':w,'height':h},has_touch=touch,is_mobile=touch,device_scale_factor=1)
        page=context.new_page();add_errors(page,name)
        result={'name':name,'viewport':[w,h],'simulatedTouch':touch,'url':url,'snapshots':[]}
        RESULT['cases'].append(result)
        try:
            r=page.goto(url,wait_until='networkidle',timeout=45000);result['http']=r.status
            open_to_intro(page,name+'_bury',result['snapshots'],touch)
            if name=='public_desktop':
                # B源文件和部署预载图保持逐字节相同。
                for image in page.locator('img').evaluate_all('(es)=>es.map(e=>e.src).filter(Boolean)'):
                    local='http://127.0.0.1:4173/assets/'+image.split('/')[-1]
                    pr=context.request.get(image);lr=context.request.get(local)
                    RESULT['comparisons'].append({'public':image,'local':local,'publicStatus':pr.status,
                      'localStatus':lr.status,'sha256':hash_(pr.body()),'sameBytes':pr.body()==lr.body()})
            result['branches']=[branch(page,name+'_bury',0,result['snapshots'],touch),
                                branch(page,name+'_protect',1,result['snapshots'],touch)]
            result['passed']=True
        except Exception as e:
            result['error']=str(e);result['passed']=False
            result['snapshots'].append(snap(page,name,'failure'))
        context.close()
    # Keyboard only: Enter + Tab/Shift+Tab, not focus()/synthetic clicks.
    context=browser.new_context(viewport={'width':1600,'height':900})
    page=context.new_page();add_errors(page,'keyboard')
    page.goto(LOCAL,wait_until='networkidle');page.wait_for_timeout(1300)
    keyboard={'name':'keyboard','steps':[]};RESULT['cases'].append(keyboard)
    def key_enter():
        keyboard['steps'].append({'phase':phase(page),'key':'Enter','active':page.evaluate('document.activeElement.textContent'),
                                  'page':page.get_attribute('#page','data-page')})
        page.keyboard.press('Enter');page.wait_for_timeout(150)
    def tab_to(label):
        for _ in range(12):
            if page.evaluate('document.activeElement.textContent')==label:return
            page.keyboard.press('Tab')
        raise RuntimeError('keyboard target not reached: '+label)
    key_enter();key_enter();page.wait_for_timeout(1300);key_enter();key_enter()
    assert phase(page)=='intro';key_enter();assert phase(page)=='choice'
    key_enter();page.wait_for_timeout(900);assert phase(page)=='ending'
    keyboard['firstEnding']=snap(page,'keyboard','01_ending_first_page')
    key_enter()
    keyboard['afterPaginationFocus']=page.evaluate('({tag:document.activeElement.tagName,id:document.activeElement.id,text:document.activeElement.textContent.slice(0,80)})')
    before=phase(page);key_enter();keyboard['immediateEnterReplay']=phase(page)!=before
    tab_to('重玩')
    keyboard['tabAfterPagination']=snap(page,'keyboard','02_after_tab')
    key_enter();assert phase(page)=='cover'
    keyboard['withTabCompleted']=True
    context.close()
    # Early replay aborts active effect; reduced-motion produces no animation pixels.
    for reduce in (False,True):
        context=browser.new_context(viewport={'width':1600,'height':900},reduced_motion='reduce' if reduce else 'no-preference')
        page=context.new_page();add_errors(page,'reduced' if reduce else 'abort')
        page.goto(LOCAL,wait_until='networkidle');page.wait_for_selector('#page[data-phase="cover"]')
        click(page,'展开画卷');click(page,'花果山');page.wait_for_timeout(1300);click(page,'林黛玉');page.locator('#drop').click()
        while phase(page)=='intro': click(page,'继续')
        page.locator('#reader-actions button').nth(1).click();page.wait_for_timeout(650)
        pixels=alpha_regions(page)
        page.locator('#replay').click();after=alpha_regions(page)
        assert phase(page)=='cover' and after['whole']['nonzero']==0
        if reduce: assert pixels['whole']['nonzero']==0
        RESULT['cases'].append({'name':'reduced_motion' if reduce else 'replay_during_effect',
                                'pixelsBefore':pixels,'pixelsAfter':after,'passed':True})
        context.close()
    browser.close()

(OUT/'browser-results.json').write_text(json.dumps(RESULT,ensure_ascii=False,indent=2),encoding='utf8')
print('Saved browser-results.json',flush=True)
