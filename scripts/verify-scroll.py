"""实际操作《黛玉来到花果山》正式页：开卷、放置、两条分支与重玩，并截图。

用法：先运行 node scripts/serve-dist.mjs 4173，再运行
    python scripts/verify-scroll.py [base_url] [out_dir]
"""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:4173'
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else 'output/scroll_v01/screens')
OUT.mkdir(parents=True, exist_ok=True)
URL = BASE + '/daiyu-huaguoshan.html'
log = []
errors = []


def phase(page):
    return page.get_attribute('#page', 'data-phase')


def shot(page, name):
    page.screenshot(path=str(OUT / f'{name}.png'))
    log.append(f'shot {name} phase={phase(page)}')


def click_text(page, label):
    page.locator('#reader-actions button', has_text=label).first.click()


def read_through(page, prefix):
    """逐页点“继续”，记录每页文字，返回拼接结果。"""
    seen = []
    i = 1
    while True:
        seen.append(page.inner_text('#reader-text'))
        buttons = page.locator('#reader-actions button')
        label = buttons.first.inner_text()
        shot(page, f'{prefix}_{i}')
        if label != '继续':
            return ''.join(seen), label
        before = phase(page)
        buttons.first.click()
        page.wait_for_timeout(150)
        if phase(page) != before:
            return ''.join(seen), label
        i += 1


def run_branch(page, option_index, tag, first):
    page.wait_for_selector('#page[data-phase="cover"]')
    page.wait_for_timeout(1400)  # 等收卷过渡结束
    shot(page, f'01_cover_{tag}')
    click_text(page, '展开画卷')
    page.wait_for_selector('#page[data-phase="scene"]')
    click_text(page, '花果山')
    page.wait_for_selector('#page[data-phase="character"]')
    page.wait_for_timeout(1400)  # 展卷动画
    if first:
        shot(page, '02_unrolled')
    click_text(page, '林黛玉')
    page.wait_for_selector('#page[data-phase="placement"]')
    # 先点一处非法空地，应停留在放置阶段并给提示。
    art = page.locator('#art').bounding_box()
    page.mouse.click(art['x'] + art['width'] * 0.3, art['y'] + art['height'] * 0.5)
    page.wait_for_timeout(100)
    assert phase(page) == 'placement', '非法点击不应放置'
    hint = page.inner_text('#reader-text')
    log.append(f'miss hint: {hint}')
    if first:
        shot(page, '03_placement')
    # 再点画面上的落点（真实指针，按场景坐标换算）。
    page.mouse.click(art['x'] + art['width'] * 0.625, art['y'] + art['height'] * 0.75)
    page.wait_for_selector('#page[data-phase="intro"]')
    page.wait_for_timeout(400)
    state = page.evaluate('window.__cuojuan.game.getState()')
    intro_text, _ = read_through(page, f'04_intro_{tag}' if first else f'x_intro_{tag}')
    assert intro_text == state['story']['intro'], '开场分页拼接后应与原文一致'
    page.wait_for_selector('#page[data-phase="choice"]')
    shot(page, f'05_choice_{tag}')
    labels = page.locator('#reader-actions button').all_inner_texts()
    log.append(f'options: {labels}')
    page.locator('#reader-actions button').nth(option_index).click()
    page.wait_for_selector('#page[data-phase="ending"]')
    page.wait_for_timeout(900)
    shot(page, f'06_ending_{tag}_effect')
    page.wait_for_timeout(1800)
    state = page.evaluate('window.__cuojuan.game.getState()')
    fig = page.get_attribute('#figure', 'src')
    log.append(f"ending {state['ending']['endingId']} expr={state['expression']} "
               f"char={state['composition']['character']} figure={fig.split('/')[-1]} "
               f"effects={page.get_attribute('#page', 'data-effects')}")
    text, last = read_through(page, f'07_ending_{tag}')
    assert text == state['ending']['text'], '结局分页拼接后应与原文一致'
    assert last == '重玩'
    rect = page.evaluate("""() => { const f = document.getElementById('figure').getBoundingClientRect();
        const a = document.getElementById('art').getBoundingClientRect();
        return { footX: (f.left + f.width * 0.499 - a.left) / a.width * 1600,
                 footY: (f.top + f.height * 0.980 - a.top) / a.height * 900,
                 h: f.height / a.height * 900 }; }""")
    log.append(f'figure foot in scene px: {json.dumps(rect)}')
    click_text(page, '重玩')
    page.wait_for_selector('#page[data-phase="cover"]')
    state = page.evaluate('window.__cuojuan.game.getState()')
    assert state['phase'] == 'cover' and state.get('ending') is None
    log.append(f'replay -> cover runId={state["runId"]}')


with sync_playwright() as p:
    browser = p.chromium.launch()
    for (w, h, name) in [(1600, 900, 'desktop'), (1280, 720, 'laptop')]:
        page = browser.new_page(viewport={'width': w, 'height': h})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        page.goto(URL)
        prev = OUT
        OUT = prev / name
        OUT.mkdir(parents=True, exist_ok=True)
        log.append(f'== {name} {w}x{h} layout={page.get_attribute("#page", "data-layout")}')
        run_branch(page, 0, 'bury', True)
        run_branch(page, 1, 'protect', name == 'desktop')
        OUT = prev
        page.close()
    browser.close()

print('\n'.join(log))
print('page errors:', errors or 0)
