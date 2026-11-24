import sample from './data/story-sample.json';
import { createAssetLoader, createGame, scenes, type AssetId, type AssetRecord, type CharacterId, type EndingDocument,
  type SceneId,
  type GameData, type SceneDocument, type Snapshot, type StoryDocument } from './core';

const files = import.meta.glob('../asset-library/content/*.json', { eager: true, import: 'default' });
const imageUrls = import.meta.glob('../asset-library/{characters,scenes,ui}/**/*.png', {
  eager: true, import: 'default', query: '?url',
});
const manifests = import.meta.glob('../asset-library/runtime-manifest.json', { eager: true, import: 'default' });
const visual = import.meta.glob('../asset-library/visual/placements.json', { eager: true, import: 'default' });
const heights = visual['../asset-library/visual/placements.json'] as
  Partial<Record<SceneId, Partial<Record<CharacterId, number>>>> | undefined;
const manifest = manifests['../asset-library/runtime-manifest.json'] as readonly AssetRecord[] | undefined;
const storyDoc = files['../asset-library/content/stories.json'] as StoryDocument | undefined;
const endingDoc = files['../asset-library/content/endings.json'] as EndingDocument | undefined;
const sceneDoc = files['../asset-library/content/scenes.json'] as SceneDocument | undefined;
const provisional: SceneDocument = {
  schemaVersion: 1,
  scenes: scenes.map((sceneId) => ({
    sceneId, frame: { width: 1600, height: 900 }, dropPoints: {
      daiyu: { x: .38, y: .756 }, wukong: { x: .62, y: .753 },
    },
  })),
};
const data: GameData = {
  stories: storyDoc ?? { schemaVersion: 1, stories: sample.stories } as StoryDocument,
  endings: endingDoc ?? { schemaVersion: 1, endings: sample._exampleEndings } as EndingDocument,
  scenes: sceneDoc ?? provisional,
};

document.getElementById('data-source')!.textContent =
  (storyDoc && endingDoc ? 'H04 正式剧情' : 'H02 首组样稿') +
  (sceneDoc ? '，使用库内站位。' : '，使用验证候选站位。') + '此页用于验证接口。';
const assets = createAssetLoader(manifest ?? [], async (path) => {
  const url = imageUrls['../asset-library/' + path];
  if (typeof url !== 'string') throw new Error('缺资源文件：' + path);
  const image = new Image();
  image.src = url;
  await image.decode();
  return image;
});
const game = createGame(data);
const steps = document.getElementById('steps')!;
const output = document.getElementById('state')!;
const diagnostic = document.getElementById('diagnostic') as HTMLCanvasElement;
diagnostic.addEventListener('click', (event) => {
  const frame = diagnostic.getBoundingClientRect();
  game.placeAt({ x: (event.clientX - frame.left) / frame.width, y: (event.clientY - frame.top) / frame.height });
});
let lastEffects: ReturnType<typeof game.takeEffects> = [];

function button(label: string, action: () => unknown) {
  const node = document.createElement('button');
  node.type = 'button';
  node.textContent = label;
  node.addEventListener('click', action);
  steps.append(node, ' ');
}

function describe(state = game.getState()) {
  const art = state.composition;
  const ids = art ? [art.back, art.mid, art.ground, ...(art.character ? [art.character] : []), art.front] : [];
  output.textContent = JSON.stringify({
    ...state, effects: lastEffects, card: game.getResultCard(),
    assets: Object.fromEntries(ids.map((id) => [id, assets.get(id).status])),
  }, null, 2);
}

function drawDiagnostic(state: Snapshot) {
  const art = state.composition;
  const ctx = diagnostic.getContext('2d');
  if (!art || !ctx) return;
  const ready = (id: AssetId) => {
    const resource = assets.get(id);
    return resource.status === 'ready' ? resource : undefined;
  };
  const layers = [art.back, art.mid, art.ground, art.front].map(ready);
  if (!layers.every((layer) => layer !== undefined)) return;
  const [back, mid, ground, front] = layers;
  const { width, height } = diagnostic;
  ctx.clearRect(0, 0, width, height);
  for (const layer of [back, mid, ground]) ctx.drawImage(layer!.value, 0, 0, width, height);
  if (art.character && state.sceneId && state.characterId && state.foot) {
    const sprite = ready(art.character);
    const spriteHeight = heights?.[state.sceneId]?.[state.characterId];
    const x = sprite?.record.foot_anchor_x;
    const y = sprite?.record.foot_anchor_y;
    if (sprite && spriteHeight && x !== undefined && y !== undefined) {
      const spriteWidth = spriteHeight * sprite.record.width / sprite.record.height;
      ctx.drawImage(sprite.value, state.foot.x * width - x * spriteWidth,
        state.foot.y * height - y * spriteHeight, spriteWidth, spriteHeight);
    }
  }
  ctx.drawImage(front!.value, 0, 0, width, height);
  if (state.target) {
    ctx.beginPath();
    ctx.arc(state.target.x * width, state.target.y * height, 40, 0, 2 * Math.PI);
    ctx.strokeStyle = '#111';
    ctx.lineWidth = 3;
    ctx.stroke();
  }
  diagnostic.hidden = false;
}

function render(state: Snapshot) {
  steps.replaceChildren();
  diagnostic.hidden = true;
  if (state.phase === 'cover') {
    lastEffects = [];
    button('展开', game.open);
  }
  if (state.phase === 'scene') {
    for (const id of game.availableScenes()) button(id, () => game.selectScene(id));
  }
  if (state.phase === 'character' && state.sceneId) {
    for (const id of game.availableCharacters(state.sceneId)) button(id, () => game.selectCharacter(id));
  }
  if (state.phase === 'placement' && state.target) {
    const point = state.target;
    button('在合法落点放置', () => game.placeAt(point));
  }
  if (state.phase === 'intro') button('显示选项', game.showChoices);
  if (state.phase === 'choice') {
    for (const option of state.options) button(option.label, () => game.choose(option.optionId));
  }
  if (state.phase === 'ending') lastEffects = game.takeEffects();
  if (state.phase !== 'cover') button('重玩', game.replay);
  if (state.composition) {
    const art = state.composition;
    button('加载当前图层', async () => {
      const pending = assets.loadAll([art.back, art.mid, art.ground, ...(art.character ? [art.character] : []), art.front]);
      const signal = game.getRunSignal();
      describe();
      await pending;
      const current = game.getState();
      if (!signal.aborted && current.phase === state.phase) {
        drawDiagnostic(current);
        describe(current);
      }
    });
  }
  describe(state);
}

game.subscribe(render);
render(game.getState());
