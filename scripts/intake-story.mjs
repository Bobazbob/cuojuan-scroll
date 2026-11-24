import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { copyFile, mkdir, readFile, stat } from 'node:fs/promises';
import { resolve } from 'node:path';

const [folder, action] = process.argv.slice(2);
if (!folder || (action && action !== '--accept')) {
  throw new Error('用法：node scripts/intake-story.mjs <H04 包路径> [--accept]');
}
const path = resolve(folder);
for (const file of ['stories.json', 'endings.json', 'assets.csv', 'README-交接.md']) {
  assert((await stat(resolve(path, file))).isFile(), '缺必要文件：' + file);
}
const storiesPath = resolve(path, 'stories.json');
const endingsPath = resolve(path, 'endings.json');
const validated = spawnSync(process.execPath, [
  'docs/h01-v02/validate_stories.mjs', '--stories', storiesPath, '--endings', endingsPath,
], { stdio: 'inherit' });
if (validated.error) throw validated.error;
if (validated.status !== 0) process.exit(validated.status ?? 1);

const load = async (file) => JSON.parse(await readFile(file, 'utf8'));
const receivedStories = await load(storiesPath);
const receivedEndings = await load(endingsPath);
const baseline = await load('src/data/story-sample.json');
assert.deepEqual(Object.keys(receivedStories).sort(), ['schemaVersion', 'stories']);
assert.deepEqual(Object.keys(receivedEndings).sort(), ['endings', 'schemaVersion']);
for (const story of baseline.stories) {
  assert.deepEqual(receivedStories.stories.find((entry) => entry.storyId === story.storyId), story,
    'H02 已验收故事有改动，需人工复核：' + story.storyId);
}
for (const ending of baseline._exampleEndings) {
  assert.deepEqual(receivedEndings.endings.find((entry) => entry.endingId === ending.endingId), ending,
    'H02 已验收结局有改动，需人工复核：' + ending.endingId);
}
console.log('H02 故事、两个结局和引用均在 H04 中原样保留。');
if (action === '--accept') {
  const library = 'asset-library/content';
  await mkdir(library, { recursive: true });
  await copyFile(storiesPath, library + '/stories.json');
  await copyFile(endingsPath, library + '/endings.json');
  console.log('正式剧情已复制入库。');
}
