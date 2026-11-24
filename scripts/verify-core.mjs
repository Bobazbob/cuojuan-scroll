import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { characters, createAssetLoader, createGame, scenes } from '../output/core-runtime/index.js';

const json = async (file) => JSON.parse(await readFile(file, 'utf8'));
const sample = await json(new URL('../src/data/story-sample.json', import.meta.url));
const candidateScenes = {
  schemaVersion: 1,
  scenes: scenes.map((sceneId) => ({ sceneId, frame: { width: 1600, height: 900 },
    dropPoints: { daiyu: { x: .38, y: .756 }, wukong: { x: .62, y: .753 } } })),
};
const formalDir = process.argv[2] === '--formal' && process.argv[3]
  ? resolve(process.argv[3]) : null;
const scenesFile = formalDir && resolve(formalDir, 'scenes.json');
const sceneConfig = scenesFile ? await json(scenesFile).catch((error) => {
  if (error.code !== 'ENOENT') throw error;
  return candidateScenes;
}) : candidateScenes;

function makeFixture() {
  const stories = [];
  const endings = [];
  for (const scene of scenes) {
    for (const character of characters) {
      const storyId = character + '_' + scene;
      const original = structuredClone(sample.stories[0]);
      original.choice.options.forEach((option, index) => {
        option.endingId = storyId + '_end_' + (index + 1);
      });
      stories.push({ ...original, storyId, character, scene });
      for (const [index, ending] of sample._exampleEndings.entries()) {
        endings.push({ ...ending, endingId: storyId + '_end_' + (index + 1), storyId,
          expression: character === 'wukong' && index === 0 ? 'angry' : ending.expression });
      }
    }
  }
  return { stories: { schemaVersion: 1, stories }, endings: { schemaVersion: 1, endings } };
}

const content = formalDir ? {
  stories: await json(resolve(formalDir, 'stories.json')),
  endings: await json(resolve(formalDir, 'endings.json')),
} : makeFixture();
assert.equal(content.stories.stories.length, 4);
assert.equal(content.endings.endings.length, 8);
const game = createGame({ ...content, scenes: sceneConfig });
let published = 0;
const disconnect = game.subscribe(() => published++);

for (const scene of scenes) {
  for (const character of characters) {
    for (const index of [0, 1]) {
      const signal = game.getRunSignal();
      assert.equal(game.getState().phase, 'cover');
      assert.equal(game.getResultCard(), undefined);
      assert.equal(game.selectScene(scene), false);
      assert(game.open() && game.selectScene(scene) && game.selectCharacter(character));
      const point = game.getState().target;
      assert(point);
      assert.equal(game.placeAt({ x: .05, y: .06 }), false);
      assert.equal(game.placeAt({ x: NaN, y: point.y }), false);
      assert(game.placeAt({ x: point.x + .01, y: point.y }));
      assert.equal(game.placeAt(point), false);
      assert.deepEqual(game.getState().foot, point);
      assert.equal(game.getState().composition.character, character + '_neutral');
      assert.equal(game.getState().story.storyId, character + '_' + scene);
      assert(game.showChoices());
      assert.equal(game.choose('not_existing'), false);
      const choices = game.getState().options;
      assert(game.choose(choices[index].optionId));
      assert.equal(game.choose(choices[1-index].optionId), false);
      const card = game.getResultCard();
      assert.equal(card.ending.endingId, choices[index].endingId);
      assert.equal(card.frameAssetId, 'ui_ending_card_frame');
      assert.equal(card.composition.character, character + '_' + card.ending.expression);
      assert(card.ending.title && card.ending.text);
      const effects = game.takeEffects();
      assert.deepEqual(effects.map((event) => event.effectId), card.ending.effects);
      assert.equal(game.takeEffects().length, 0);
      assert(effects.every((event) => event.runId === game.getState().runId && event.durationMs > 0));
      let cleanup = 0;
      signal.addEventListener('abort', () => cleanup++, { once: true });
      game.replay();
      assert.equal(cleanup, 1);
      assert(game.getRunSignal() !== signal && !game.getRunSignal().aborted);
      for (const field of ['story', 'ending', 'foot', 'expression', 'composition', 'characterId', 'sceneId']) {
        assert.equal(game.getState()[field], undefined);
      }
      assert.equal(game.takeEffects().length, 0);
      console.log('PASS', card.ending.endingId, 'click / id / card / replay');
    }
  }
}
disconnect();
const total = published;
game.replay();
assert.equal(total, published);

const incomplete = createGame({
  stories: { schemaVersion: 1, stories: sample.stories },
  endings: { schemaVersion: 1, endings: sample._exampleEndings },
  scenes: candidateScenes,
});
assert.deepEqual(incomplete.availableScenes(), ['huaguoshan']);
assert.deepEqual(incomplete.availableCharacters('huaguoshan'), ['daiyu']);
assert.throws(() => createGame({ ...content,
  endings: { schemaVersion: 1, endings: content.endings.endings.slice(1) }, scenes: candidateScenes }),
/缺合法落点、有效选项或有效结局/);

const record = { asset_id: 'daiyu_neutral', kind: 'character', file_relpath: 'characters/daiyu/daiyu_neutral.png',
  width: 768, height: 1024, has_alpha: true, status: 'verified' };
let called = 0;
const loader = createAssetLoader([record], async () => {
  if (++called === 1) throw 'mock decode failure';
  return 'decoded';
});
assert.equal(loader.get('daiyu_neutral').status, 'idle');
const first = loader.load('daiyu_neutral');
assert.equal(loader.get('daiyu_neutral').status, 'loading');
assert.equal(first, loader.load('daiyu_neutral'));
assert.equal((await first).status, 'error');
assert.equal((await loader.load('wukong_neutral')).status, 'missing');
assert.equal((await loader.load('daiyu_neutral')).value, 'decoded');
await loader.loadAll(['daiyu_neutral', 'wukong_neutral']);
assert.equal(called, 2);
console.log('PASS asset states missing / idle / loading / error / ready, cache / concurrent requests / retry');
console.log('DATA:', formalDir ? 'H04 正式内容' : '合成验证夹具（四组合八结局），H02 单组另验可用范围');
console.log('POINTS:', sceneConfig === candidateScenes ? '测试候选坐标，未做正式画面试放' : '库内登记坐标');
