"""验证公网修复版的V01-V05、D01效果"""
import sys, json, time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path('work/b-deliveries/Claude_scene_review_v02')
OUT.mkdir(parents=True, exist_ok=True)

results = {
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'base_url': 'https://bobazbob.github.io/cuojuan-scroll',
    'fixes': {},
    'checks': {}
}

with sync_playwright() as p:
    browser = p.chromium.launch()
    
    # D01：根入口重定向
    print("D01：检查根入口是否重定向到正式场景...")
    page = browser.new_page(viewport={'width': 1600, 'height': 900})
    page.goto('https://bobazbob.github.io/cuojuan-scroll/')
    time.sleep(1)
    final_url = page.url
    is_redirected = 'daiyu-huaguoshan.html' in final_url
    results['fixes']['D01_root_redirect'] = {
        'pass': is_redirected,
        'final_url': final_url
    }
    print(f"  最终URL: {final_url}")
    print(f"  {'✓通过' if is_redirected else '✗失败'}")
    
    # V01：文字清晰度（1600×900）
    print("\nV01：检查1600×900阅读区文字清晰度...")
    page.goto('https://bobazbob.github.io/cuojuan-scroll/daiyu-huaguoshan.html')
    page.wait_for_selector('#page[data-phase="cover"]')
    page.locator('#reader-actions button').first.click()
    page.wait_for_selector('#page[data-phase="scene"]')
    page.locator('#reader-actions button').first.click()
    page.wait_for_selector('#page[data-phase="character"]')
    page.locator('#reader-actions button').first.click()
    page.wait_for_selector('#page[data-phase="placement"]')
    art = page.locator('#art').bounding_box()
    page.mouse.click(art['x'] + art['width'] * 0.625, art['y'] + art['height'] * 0.75)
    page.wait_for_selector('#page[data-phase="intro"]')
    
    opacity_check = page.evaluate("""() => {
        const title = document.getElementById('reader-title');
        const text = document.getElementById('reader-text');
        const btn = document.querySelector('#reader-actions button');
        return {
            titleOpacity: window.getComputedStyle(title).opacity,
            textOpacity: window.getComputedStyle(text).opacity,
            btnOpacity: window.getComputedStyle(btn).opacity,
            titleFilter: window.getComputedStyle(title).filter,
            textFilter: window.getComputedStyle(text).filter,
            btnFilter: window.getComputedStyle(btn).filter
        };
    }""")
    
    is_clear = all(float(v) >= 0.95 for v in [
        opacity_check['titleOpacity'],
        opacity_check['textOpacity'],
        opacity_check['btnOpacity']
    ])
    results['fixes']['V01_text_clarity'] = {
        'pass': is_clear,
        'details': opacity_check
    }
    print(f"  标题opacity: {opacity_check['titleOpacity']}")
    print(f"  正文opacity: {opacity_check['textOpacity']}")
    print(f"  按钮opacity: {opacity_check['btnOpacity']}")
    print(f"  {'✓文字清晰' if is_clear else '✗仍有淡化'}")
    
    # V02：宽高比（390×844）
    print("\nV02：检查390×844窄屏宽高比...")
    page.close()
    page = browser.new_page(viewport={'width': 390, 'height': 844})
    page.goto('https://bobazbob.github.io/cuojuan-scroll/daiyu-huaguoshan.html')
    page.wait_for_selector('#page[data-phase="cover"]')
    page.locator('#reader-actions button').first.click()
    page.wait_for_selector('#page[data-phase="scene"]')
    page.locator('#reader-actions button').first.click()
    page.wait_for_selector('#page[data-phase="character"]')
    page.locator('#reader-actions button').first.click()
    page.wait_for_selector('#page[data-phase="placement"]')
    art = page.locator('#art').bounding_box()
    page.mouse.click(art['x'] + art['width'] * 0.625, art['y'] + art['height'] * 0.75)
    page.wait_for_selector('#page[data-phase="intro"]')
    
    aspect_check = page.evaluate("""() => {
        const scroll = document.getElementById('scroll');
        const fig = document.getElementById('figure');
        return {
            scrollWidth: scroll.offsetWidth,
            scrollHeight: scroll.offsetHeight,
            scrollAspectRatio: scroll.offsetWidth / scroll.offsetHeight,
            figureWidth: fig.offsetWidth,
            figureHeight: fig.offsetHeight,
            figureAspectRatio: fig.offsetWidth / (fig.offsetHeight || 1)
        };
    }""")
    
    scroll_ratio = aspect_check['scrollAspectRatio']
    fig_ratio = aspect_check['figureAspectRatio']
    is_correct = abs(scroll_ratio - 16/9) < 0.02
    results['fixes']['V02_aspect_ratio'] = {
        'pass': is_correct,
        'details': aspect_check
    }
    print(f"  画境宽高比: {scroll_ratio:.4f} (期望 {16/9:.4f})")
    print(f"  人物宽高比: {fig_ratio:.4f} (期望 0.75)")
    print(f"  {'✓正确' if is_correct else '✗非等比'}")
    
    # V03/V05：窄屏布局
    print("\nV03/V05：检查窄屏阅读区布局...")
    layout_check = page.evaluate("""() => {
        return {
            pageLayout: document.getElementById('page').dataset.layout,
            narrowLayout: document.getElementById('page').dataset.narrowLayout,
            readerDisplay: window.getComputedStyle(document.getElementById('reader')).display,
            readerFlexDirection: window.getComputedStyle(document.getElementById('reader')).flexDirection
        };
    }""")
    
    is_below_layout = layout_check['pageLayout'] == 'below'
    is_narrow_layout = layout_check['narrowLayout'] == 'yes'
    results['fixes']['V03_V05_narrow_layout'] = {
        'pass': is_below_layout and is_narrow_layout,
        'details': layout_check
    }
    print(f"  页面布局: {layout_check['pageLayout']} (期望 below)")
    print(f"  窄屏标记: {layout_check['narrowLayout']} (期望 yes)")
    print(f"  {'✓正确' if (is_below_layout and is_narrow_layout) else '✗布局错误'}")
    
    page.close()
    browser.close()

# 保存结果
with open(OUT / 'fix-verification-v02.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n结果已保存至 {OUT}/fix-verification-v02.json")
print("\n总结:")
print(f"  D01 根入口: {'✓' if results['fixes']['D01_root_redirect']['pass'] else '✗'}")
print(f"  V01 文字清晰: {'✓' if results['fixes']['V01_text_clarity']['pass'] else '✗'}")
print(f"  V02 宽高比: {'✓' if results['fixes']['V02_aspect_ratio']['pass'] else '✗'}")
print(f"  V03/V05 窄屏布局: {'✓' if results['fixes']['V03_V05_narrow_layout']['pass'] else '✗'}")
