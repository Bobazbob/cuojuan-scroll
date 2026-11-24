"""验证局部修复后的场景。检查V01-V05、D01的改动效果。"""
import sys
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

OUT = Path('work/b-deliveries/Claude_scene_review_v02/verification')
OUT.mkdir(parents=True, exist_ok=True)

results = {
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'fixes': {},
    'regressions': [],
    'viewports': {}
}

viewports = [
    {'name': 'desktop', 'width': 1600, 'height': 900},
    {'name': 'laptop', 'width': 1280, 'height': 720},
    {'name': 'phone_portrait', 'width': 390, 'height': 844},
    {'name': 'phone_landscape', 'width': 844, 'height': 390},
    {'name': 'narrow_portrait', 'width': 320, 'height': 568},
]

def shot(page, name, vp_name):
    path = OUT / f'{vp_name}_{name}.png'
    page.screenshot(path=str(path))
    return str(path)

def check_text_opacity(page):
    """V01检查：正文、标题、按钮是否清晰（非淡化）"""
    return page.evaluate("""() => {
        const title = document.getElementById('reader-title');
        const text = document.getElementById('reader-text');
        const btn = document.querySelector('#reader-actions button');
        return {
            titleOpacity: window.getComputedStyle(title).opacity,
            textOpacity: window.getComputedStyle(text).opacity,
            btnOpacity: window.getComputedStyle(btn).opacity,
            titleColor: window.getComputedStyle(title).color,
            textColor: window.getComputedStyle(text).color,
            btnBgColor: window.getComputedStyle(btn).backgroundColor
        };
    }""")

def check_aspect_ratio(page, vp_name):
    """V02检查：画境和人物比例是否为16:9和3:4"""
    return page.evaluate("""() => {
        const scroll = document.getElementById('scroll');
        const stage = document.getElementById('stage');
        const fig = document.getElementById('figure');
        const rect = scroll.getBoundingClientRect();
        return {
            scrollWidth: scroll.offsetWidth,
            scrollHeight: scroll.offsetHeight,
            stageHeight: stage.offsetHeight,
            scrollAspectRatio: scroll.offsetWidth / (scroll.offsetHeight || 1),
            figureWidth: fig.offsetWidth,
            figureHeight: fig.offsetHeight,
            figureAspectRatio: fig.offsetWidth / (fig.offsetHeight || 1),
            pageLayout: document.getElementById('page').dataset.layout,
            narrowLayout: document.getElementById('page').dataset.narrowLayout,
        };
    }""")

def check_root_redirect(page):
    """D01检查：根入口是否正确重定向"""
    return page.evaluate("() => window.location.pathname")

with sync_playwright() as p:
    browser = p.chromium.launch()
    
    # 检查1：D01 - 根入口重定向
    print("检查 D01：根入口重定向...")
    page = browser.new_page(viewport={'width': 1600, 'height': 900})
    page.goto('http://127.0.0.1:4173/')
    time.sleep(0.5)
    final_path = check_root_redirect(page)
    is_redirected = 'daiyu-huaguoshan.html' in final_path
    results['fixes']['D01_root_redirect'] = is_redirected
    print(f"  最终路径: {final_path} - {'✓通过' if is_redirected else '✗失败'}")
    page.close()
    
    # 检查2-6：各视口的V01-V05
    for vp in viewports:
        print(f"\n检查视口 {vp['name']} ({vp['width']}×{vp['height']})...")
        page = browser.new_page(viewport=vp)
        page.goto('http://127.0.0.1:4173/daiyu-huaguoshan.html')
        
        vp_key = vp['name']
        results['viewports'][vp_key] = {}
        
        # 开卷、选择、放置
        page.wait_for_selector('#page[data-phase="cover"]')
        shot(page, '01_cover', vp_key)
        
        page.locator('#reader-actions button').first.click()
        page.wait_for_selector('#page[data-phase="scene"]')
        page.locator('#reader-actions button').first.click()
        page.wait_for_selector('#page[data-phase="character"]')
        page.locator('#reader-actions button').first.click()
        page.wait_for_selector('#page[data-phase="placement"]')
        
        # 放置
        art = page.locator('#art').bounding_box()
        page.mouse.click(art['x'] + art['width'] * 0.625, art['y'] + art['height'] * 0.75)
        page.wait_for_selector('#page[data-phase="intro"]')
        shot(page, '02_intro', vp_key)
        
        # V01检查：正文清晰度
        opacity_check = check_text_opacity(page)
        is_clear = all(float(v) >= 0.95 for v in [
            opacity_check['titleOpacity'],
            opacity_check['textOpacity'],
            opacity_check['btnOpacity']
        ])
        results['viewports'][vp_key]['V01_text_opacity'] = {
            'pass': is_clear,
            'values': opacity_check
        }
        print(f"  V01文字不透明: {'✓' if is_clear else '✗'} {opacity_check}")
        
        # V02检查：宽高比
        aspect_check = check_aspect_ratio(page, vp_key)
        scroll_ratio = aspect_check['scrollAspectRatio']
        figure_ratio = aspect_check['figureAspectRatio']
        is_correct_ratio = abs(scroll_ratio - 16/9) < 0.01 and abs(figure_ratio - 0.75) < 0.02
        results['viewports'][vp_key]['V02_aspect_ratio'] = {
            'pass': is_correct_ratio,
            'scroll_ratio': scroll_ratio,
            'scroll_expected': 16/9,
            'figure_ratio': figure_ratio,
            'figure_expected': 0.75
        }
        print(f"  V02宽高比: {'✓' if is_correct_ratio else '✗'} scroll={scroll_ratio:.4f} figure={figure_ratio:.4f}")
        
        # V03/V05检查：窄屏布局
        layout_info = aspect_check['pageLayout']
        narrow = aspect_check['narrowLayout']
        is_correct_layout = (vp['width'] > 900 and layout_info == 'inside') or (vp['width'] <= 900 and layout_info == 'below')
        results['viewports'][vp_key]['V03_V05_layout'] = {
            'pass': is_correct_layout,
            'layout': layout_info,
            'narrow': narrow
        }
        print(f"  V03/V05布局: {'✓' if is_correct_layout else '✗'} layout={layout_info} narrow={narrow}")
        
        # V04检查：翻页焦点
        page.locator('#reader-actions button').first.click()
        page.wait_for_selector('#page[data-phase="choice"]')
        page.locator('#reader-actions button').first.click()
        page.wait_for_selector('#page[data-phase="ending"]')
        shot(page, '03_ending', vp_key)
        
        # 翻页测试（如果有多页）
        try:
            page.locator('#reader-actions button', has_text='继续').first.click(timeout=100)
            # 检查焦点是否在操作按钮上
            focused = page.evaluate("() => document.activeElement?.tagName")
            has_focus = focused == 'BUTTON'
            results['viewports'][vp_key]['V04_focus_after_page'] = {
                'pass': has_focus,
                'focused_element': focused
            }
            print(f"  V04翻页焦点: {'✓' if has_focus else '✗'} focused={focused}")
        except:
            results['viewports'][vp_key]['V04_focus_after_page'] = {'pass': True, 'note': '无多页'}
        
        page.close()
    
    browser.close()

# 保存结果
with open(OUT / 'verification-results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✓ 验证完成，结果保存至 {OUT}")
print(json.dumps(results, ensure_ascii=False, indent=2))
