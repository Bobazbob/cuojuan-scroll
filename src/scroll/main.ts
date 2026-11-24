import storiesJson from '../../asset-library/content/stories.json';
import endingsJson from '../../asset-library/content/endings.json';
import scenesJson from '../../asset-library/content/scenes.json';
import manifestJson from '../../asset-library/runtime-manifest.json';
import placementsJson from '../../asset-library/visual/placements.json';
import {
  createAssetLoader, createGame,
  type AssetId, type AssetRecord, type EndingDocument, type SceneDocument, type Snapshot, type StoryDocument,
} from '../core';
import { playEffects } from './effects';
import { paginate } from './text';
import './scroll.css';

// 本轮只开放这一组；其余组合等 B 验收后再接。
const SCENE = 'huaguoshan' as const;
const CHARACTER = 'daiyu' as const;
const FRAME = { width: 1600, height: 900 };
// 阅读区：v02 字幕带 x=96–1504、y=720–873，扣除卷轴下缘横杆 y=841–864。
const READER = { left: 96, right: 1504, top: 722, bottom: 838 };

const urls = import.meta.glob('../../asset-library/{characters,scenes,ui}/**/*.png', {
  eager: true, import: 'default', query: '?url',
}) as Record<string, string>;
const manifest = manifestJson as unknown as readonly AssetRecord[];
const heights = placementsJson as Record<string, Record<string, number>>;
const game = createGame({
  stories: storiesJson as StoryDocument,
  endings: endingsJson as EndingDocument,
  scenes: scenesJson as SceneDocument,
});
const assets = createAssetLoader<HTMLImageElement>(manifest, async (path) => {
  const url = urls['../../asset-library/' + path];
  if (!url) throw new Error('缺资源文件：' + path);
  const image = new Image();
  image.src = url;
  await image.decode();
  return image;
});

const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
const page = $('page');
const scroll = $('scroll');
const stage = $('stage');
const art = $('art');
const figure = $<HTMLImageElement>('figure');
const figureOld = $<HTMLImageElement>('figure-old');
const shadow = $('shadow');
const drop = $<HTMLButtonElement>('drop');
const readerTitle = $('reader-title');
const readerText = $('reader-text');
const actions = $('reader-actions');
const measure = $('measure');
const effectsCanvas = $<HTMLCanvasElement>('effects');
const layerImg = (name: string) => art.querySelector<HTMLImageElement>(`[data-layer="${name}"]`)!;

const preload: AssetId[] = [
  `${SCENE}_layer1_back`, `${SCENE}_layer2_mid`, `${SCENE}_layer3_ground`, `${SCENE}_layer4_front`,
  `${CHARACTER}_neutral`, `${CHARACTER}_happy`, `${CHARACTER}_upset`, 'ui_scroll_frame', 'ui_paper_texture',
];
const src = (id: AssetId) => {
  const state = assets.get(id);
  return state.status === 'ready' ? state.value.src : '';
};

// 页面本地状态只管字幕翻页与提示，不重复引擎的阶段逻辑。
let ready = false;
let loadError = '';
let pages: string[] = [];
let pageIndex = 0;
let pageKey = '';
let textKey = '';
let missed = false;

function pct(value: number, total: number) {
  return (value / total * 100) + '%';
}

function button(label: string, onClick: () => void, className = 'ink') {
  const node = document.createElement('button');
  node.type = 'button';
  node.className = className;
  node.textContent = label;
  node.addEventListener('click', onClick);
  actions.append(node);
  return node;
}

/** 人物按实测脚底锚点对齐场景落点；立绘保持原始 3:4，不拉伸。 */
function placeFigure(state: Snapshot) {
  const id = state.composition?.character;
  const record = id && assets.get(id);
  if (!id || !state.foot || !record || record.status !== 'ready') {
    figure.hidden = true;
    shadow.hidden = true;
    return;
  }
  const { width, height, foot_anchor_x: ax = 0.5, foot_anchor_y: ay = 1 } = record.record;
  const h = heights[SCENE]?.[CHARACTER] ?? 504;
  const w = h * width / height;
  const footX = state.foot.x * FRAME.width;
  const footY = state.foot.y * FRAME.height;
  const box = {
    left: pct(footX - ax * w, FRAME.width), top: pct(footY - ay * h, FRAME.height),
    width: pct(w, FRAME.width), height: pct(h, FRAME.height),
    transformOrigin: `${ax * 100}% ${ay * 100}%`,
  };
  const next = record.value.src;
  if (!figure.hidden && figure.src && figure.src !== next) {
    // 换表情：同画布交叉淡化，位置不变。
    Object.assign(figureOld.style, box);
    figureOld.src = figure.src;
    figureOld.hidden = false;
    figureOld.classList.remove('fade-out');
    void figureOld.offsetWidth;
    figureOld.classList.add('fade-out');
  }
  const entering = figure.hidden;
  Object.assign(figure.style, box);
  figure.src = next;
  figure.hidden = false;
  if (entering) {
    figure.classList.remove('enter');
    void figure.offsetWidth;
    figure.classList.add('enter');
  }
  Object.assign(shadow.style, { left: pct(footX, FRAME.width), top: pct(footY, FRAME.height) });
  shadow.hidden = false;
}

function setCopy(title: string, text: string) {
  readerTitle.textContent = title;
  readerTitle.hidden = !title;
  readerText.textContent = text;
}

/** 用实际阅读区宽度与行高测量，按句切页；原文逐字保留。 */
function paginateFor(key: string, text: string) {
  if (key === pageKey) return;
  pageKey = key;
  const style = getComputedStyle(readerText);
  const line = parseFloat(style.lineHeight);
  const maxLines = page.dataset.layout === 'inside' ? 2 : 4;
  measure.style.width = readerText.getBoundingClientRect().width + 'px';
  const sameText = key === textKey;
  textKey = key;
  const offset = sameText ? pages.slice(0, pageIndex).join('').length : 0;
  pages = paginate(text, (candidate) => {
    measure.textContent = candidate;
    return measure.getBoundingClientRect().height <= line * maxLines + 1;
  });
  // 重排时停在包含已读位置的那一页。
  let seen = 0;
  pageIndex = 0;
  while (pageIndex < pages.length - 1 && seen + pages[pageIndex].length <= offset) {
    seen += pages[pageIndex].length;
    pageIndex++;
  }
}

function renderReader(state: Snapshot) {
  actions.replaceChildren();
  const story = state.story;
  if (!ready) {
    setCopy('', loadError || '正在展开…');
    if (loadError) button('重试', start);
    return;
  }
  switch (state.phase) {
    case 'cover':
      setCopy('', '诗中人，入山来。');
      button('展开画卷', () => game.open(), 'ink primary').dataset.focus = 'true';
      break;
    case 'scene':
      setCopy('选一处入卷', '翻开花果山这一页。');
      if (game.availableScenes().includes(SCENE)) button('花果山', () => game.selectScene(SCENE)).dataset.focus = 'true';
      break;
    case 'character':
      setCopy('谁来到花果山？', '选定人物，再把她放进画卷。');
      if (state.sceneId && game.availableCharacters(state.sceneId).includes(CHARACTER)) {
        button('林黛玉', () => game.selectCharacter(CHARACTER)).dataset.focus = 'true';
      }
      break;
    case 'placement':
      setCopy('放置林黛玉', missed ? '请点岩台上带圆环的落点。' : '点击岩台上的圆环，让黛玉入画。');
      break;
    case 'intro':
    case 'ending': {
      const title = state.phase === 'intro' ? story!.title : state.ending!.title;
      const text = state.phase === 'intro' ? story!.intro : state.ending!.text;
      setCopy(title, '');
      paginateFor(state.runId + state.phase, text);
      readerText.textContent = pages[pageIndex];
      const last = pageIndex >= pages.length - 1;
      if (!last) {
        button('继续', () => { 
          pageIndex++; 
          renderReader(game.getState());
          // V04修复：翻页后焦点回到新按钮
          actions.querySelector<HTMLElement>('button')?.focus({ preventScroll: true });
        }).dataset.focus = 'true';
      } else if (state.phase === 'intro') {
        button('继续', () => game.showChoices()).dataset.focus = 'true';
      } else {
        button('重玩', replay, 'ink primary').dataset.focus = 'true';
      }
      break;
    }
    case 'choice':
      setCopy('', story!.choice.prompt);
      for (const option of state.options) {
        button(option.label, () => game.choose(option.optionId), 'ink choice').dataset.optionId = option.optionId;
      }
      actions.firstElementChild?.setAttribute('data-focus', 'true');
      break;
  }
  page.dataset.page = pages.length > 1 && (state.phase === 'intro' || state.phase === 'ending')
    ? `${pageIndex + 1}/${pages.length}` : '';
  
  // 聚焦第一个标记为focus的按钮（延迟确保DOM已更新）
  setTimeout(() => {
    const toFocus = actions.querySelector<HTMLElement>('[data-focus="true"]');
    if (toFocus && page.dataset.phase !== 'placement') {
      toFocus.focus({ preventScroll: true });
    }
  }, 0);
}

function render(state: Snapshot) {
  const previous = page.dataset.phase;
  page.dataset.phase = ready ? state.phase : 'loading';
  const art_ = state.composition;
  if (art_) {
    layerImg('back').src = src(art_.back);
    layerImg('mid').src = src(art_.mid);
    layerImg('ground').src = src(art_.ground);
    layerImg('front').src = src(art_.front);
  }
  if (state.phase === 'cover' || state.phase === 'scene') {
    figure.hidden = true;
    figureOld.hidden = true;
    shadow.hidden = true;
  } else {
    placeFigure(state);
  }
  drop.hidden = state.phase !== 'placement' || !state.target;
  if (state.target) {
    drop.style.left = pct(state.target.x * FRAME.width, FRAME.width);
    drop.style.top = pct(state.target.y * FRAME.height, FRAME.height);
  }
  if (state.phase !== 'placement') missed = false;
  if (state.phase !== 'intro' && state.phase !== 'ending') { pages = []; pageIndex = 0; pageKey = ''; }
  renderReader(state);
  if (state.phase === 'ending' && previous !== 'ending') {
    const directives = game.takeEffects();
    const media = matchMedia('(prefers-reduced-motion: reduce)');
    page.dataset.effects = directives.map((d) => d.effectId).join(' ');
    if (!media.matches) playEffects(effectsCanvas, directives, game.getRunSignal());
  }
  if (state.phase !== 'ending') page.dataset.effects = '';
  if (previous !== page.dataset.phase) {
    const target = (state.phase === 'placement' ? drop : actions.querySelector<HTMLElement>('[data-focus], button'));
    target?.focus({ preventScroll: true });
    if (page.dataset.layout === 'below' && state.phase !== 'cover') {
      $('reader').scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }
}

function replay() {
  game.replay();
  window.scrollTo({ top: 0 });
}

function toPoint(event: PointerEvent | MouseEvent) {
  const rect = art.getBoundingClientRect();
  return { x: (event.clientX - rect.left) / rect.width, y: (event.clientY - rect.top) / rect.height };
}

art.addEventListener('click', (event) => {
  const state = game.getState();
  if (state.phase !== 'placement') return;
  if (!game.placeAt(toPoint(event))) {
    missed = true;
    renderReader(state);
  }
});
drop.addEventListener('click', (event) => {
  event.stopPropagation();
  const target = game.getState().target;
  if (target) game.placeAt(target);
});
$('replay').addEventListener('click', replay);

/** 16:9 整景等比完整显示；阅读区放不下时整块移到场景下方。 V02修复：实际容器宽度计算，统一等比。 */
function layout() {
  const gutter = Math.min(24, innerWidth * 0.02);
  const vw = document.documentElement.clientWidth - gutter * 2;
  const vh = innerHeight - gutter * 2;
  
  // 第一步：计算内布局（画境 + 阅读区叠在内）的理想宽度
  let width = Math.min(vw, vh * 16 / 9);
  const readerPx = (READER.bottom - READER.top) / FRAME.height * (width * 9 / 16);
  const inside = readerPx >= 92 && width >= 900;
  
  // 第二步：若下方阅读，重新计算宽度，但要应用到实际页面padding后的容器
  if (!inside) {
    // 横屏：画境让出阅读区高度
    // 竖屏：画境填满宽度
    const isLandscape = innerWidth > innerHeight;
    const availW = document.documentElement.clientWidth - gutter * 2;
    if (isLandscape) {
      width = Math.min(availW, (vh - 150) * 16 / 9);
    } else {
      width = availW;
    }
  }
  
  const height = width * 9 / 16;
  scroll.style.width = width + 'px';
  scroll.style.aspectRatio = '16/9';
  const layoutName = inside ? 'inside' : 'below';
  const changed = page.dataset.layout !== layoutName;
  page.dataset.layout = layoutName;
  const reader = $('reader');
  if (inside) {
    Object.assign(reader.style, {
      left: pct(READER.left, FRAME.width), width: pct(READER.right - READER.left, FRAME.width),
      top: (READER.top / FRAME.height * height) + 'px', height: readerPx + 'px',
    });
  } else {
    reader.removeAttribute('style');
  }
  // V03/V05修复：窄屏下方阅读上下排列，重玩移到画下
  page.dataset.narrowLayout = inside ? 'no' : (innerWidth <= 480 ? 'yes' : 'no');
  if (changed || inside) pageKey = '';
  renderReader(game.getState());
}

async function start() {
  loadError = '';
  renderReader(game.getState());
  const results = await assets.loadAll(preload);
  const failed = results.filter((r) => r.status !== 'ready');
  if (failed.length) {
    loadError = '画卷未能载入。';
    console.error(failed);
    render(game.getState());
    return;
  }
  const frame = src('ui_scroll_frame');
  document.querySelectorAll<HTMLImageElement>('.roller').forEach((img) => { img.src = frame; });
  page.style.setProperty('--paper', `url("${src('ui_paper_texture')}")`);
  // 封卷阶段也先放好场景，以便开卷时从中缝展开。
  layerImg('back').src = src(`${SCENE}_layer1_back`);
  layerImg('mid').src = src(`${SCENE}_layer2_mid`);
  layerImg('ground').src = src(`${SCENE}_layer3_ground`);
  layerImg('front').src = src(`${SCENE}_layer4_front`);
  ready = true;
  render(game.getState());
}

game.subscribe(render);
addEventListener('resize', layout);
layout();
render(game.getState());
void start();
Object.assign(window, { __cuojuan: { game, assets } });
