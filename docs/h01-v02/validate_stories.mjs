#!/usr/bin/env node
// 《错卷》故事/结局 JSON 最小校验器。零依赖，Node 18+。
// 用法：
//   node validate_stories.mjs --stories stories.json --endings endings.json
//   node validate_stories.mjs --sample story-sample.json
//   node validate_stories.mjs --template story-template.json

import { readFileSync } from 'node:fs';

const CHARACTER_EXPRESSIONS = {
  daiyu: ['neutral', 'happy', 'upset'],
  wukong: ['neutral', 'happy', 'angry'],
};
const SCENES = ['huaguoshan', 'daguanyuan'];
const EFFECTS = ['petal_fall', 'petal_gather', 'gold_spark', 'clone_echo'];
const STORY_IDS = [
  'daiyu_huaguoshan',
  'daiyu_daguanyuan',
  'wukong_huaguoshan',
  'wukong_daguanyuan',
];
const SAMPLE_STORY_ID = 'daiyu_huaguoshan';
const ENDING_IDS = STORY_IDS.flatMap((s) => [`${s}_end_1`, `${s}_end_2`]);
const LIMITS = {
  storyTitle: [2, 16],
  intro: [60, 120],
  prompt: [8, 40],
  optionLabel: [2, 12],
  endingTitle: [2, 16],
  endingText: [80, 160],
};

const args = process.argv.slice(2);
const opt = (flag) => {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : undefined;
};
const fatal = (msg) => {
  console.error(msg);
  process.exit(2);
};
const isStr = (v) => typeof v === 'string' && v.length > 0;
const isObj = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);
const charLen = (s) => [...String(s).replace(/\s+/g, '')].length;
const inRange = (n, [lo, hi]) => n >= lo && n <= hi;

const issues = [];
const check = (ok, code, msg) => {
  if (!ok) issues.push({ code, msg });
};

const readJson = (path, label) => {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (e) {
    fatal(`[FATAL] ${label} 无法读取或解析：${path}\n${e.message}`);
  }
};

const sampleMode = args.includes('--sample');
const templateMode = args.includes('--template');
if (sampleMode && (templateMode || args.includes('--stories') || args.includes('--endings'))) {
  fatal('--sample 必须单独使用，不能与 --template、--stories 或 --endings 混用。');
}
const mode = sampleMode ? 'B02 样稿' : templateMode ? '模板' : '正式';
let stories;
let endings;
let schemaVersionOk;

if (sampleMode || templateMode) {
  const flag = sampleMode ? '--sample' : '--template';
  const label = sampleMode ? 'story-sample.json' : 'story-template.json';
  const path = opt(flag);
  if (!path || path.startsWith('--')) fatal("用法：node validate_stories.mjs " + flag + " <" + label + ">");
  const doc = readJson(path, label);
  stories = doc?.stories;
  endings = doc?._exampleEndings;
  schemaVersionOk = doc?.schemaVersion === 1;
} else {
  const sp = opt('--stories');
  const ep = opt('--endings');
  if (!sp || !ep) fatal('用法：node validate_stories.mjs --stories <stories.json> --endings <endings.json>');
  const sdoc = readJson(sp, 'stories.json');
  const edoc = readJson(ep, 'endings.json');
  stories = sdoc?.stories;
  endings = edoc?.endings;
  schemaVersionOk = sdoc?.schemaVersion === 1 && edoc?.schemaVersion === 1;
}

check(schemaVersionOk, 'SCHEMA_VERSION', 'schemaVersion 必须为 1');
check(Array.isArray(stories), 'STORIES_ARRAY', 'stories 必须是数组');
check(Array.isArray(endings), 'ENDINGS_ARRAY', 'endings 必须是数组');

const report = () => {
  const stats = `故事 ${Array.isArray(stories) ? stories.length : '?'} / 结局 ${Array.isArray(endings) ? endings.length : '?'}`;
  if (issues.length === 0) {
    console.log(`PASS（${mode}模式）：${stats}，全部可自动检查项通过。`);
    process.exit(0);
  }
  console.log(`FAIL（${mode}模式）：${stats}，共 ${issues.length} 个问题。`);
  for (const it of issues) console.log(`- [${it.code}] ${it.msg}`);
  process.exit(1);
};

if (!Array.isArray(stories) || !Array.isArray(endings)) report();

const storyById = new Map();

stories.forEach((s, i) => {
  const at = `stories[${i}]`;
  if (!isObj(s)) {
    check(false, 'STORY_OBJECT', `${at} 必须是对象`);
    return;
  }
  check(isStr(s.storyId), 'STORY_ID', `${at}.storyId 必填`);
  if (isStr(s.storyId)) {
    check(STORY_IDS.includes(s.storyId), 'STORY_ID_SET', `${at}.storyId "${s.storyId}" 不在固定集合`);
    check(!storyById.has(s.storyId), 'STORY_ID_UNIQUE', `storyId 重复：${s.storyId}`);
    if (!storyById.has(s.storyId)) storyById.set(s.storyId, s);
  }
  check(
    isStr(s.character) && Object.prototype.hasOwnProperty.call(CHARACTER_EXPRESSIONS, s.character),
    'CHARACTER',
    `${at}.character 非法：${String(s.character)}`
  );
  check(isStr(s.scene) && SCENES.includes(s.scene), 'SCENE', `${at}.scene 非法：${String(s.scene)}`);
  if (isStr(s.storyId) && isStr(s.character) && isStr(s.scene)) {
    check(s.storyId === `${s.character}_${s.scene}`, 'STORY_ID_MATCH', `${at}.storyId 必须为 "${s.character}_${s.scene}"`);
  }
  check(
    isStr(s.title) && inRange(charLen(s.title), LIMITS.storyTitle),
    'LENGTH_STORY_TITLE',
    `${at}.title 需 ${LIMITS.storyTitle[0]}–${LIMITS.storyTitle[1]} 字（当前 ${isStr(s.title) ? charLen(s.title) : '无'}）`
  );
  check(
    isStr(s.intro) && inRange(charLen(s.intro), LIMITS.intro),
    'LENGTH_INTRO',
    `${at}.intro 需 ${LIMITS.intro[0]}–${LIMITS.intro[1]} 字（当前 ${isStr(s.intro) ? charLen(s.intro) : '无'}）`
  );
  check(isObj(s.choice), 'CHOICE', `${at}.choice 必填`);
  if (!isObj(s.choice)) return;

  const c = s.choice;
  check(
    isStr(c.prompt) && inRange(charLen(c.prompt), LIMITS.prompt),
    'LENGTH_PROMPT',
    `${at}.choice.prompt 需 ${LIMITS.prompt[0]}–${LIMITS.prompt[1]} 字（当前 ${isStr(c.prompt) ? charLen(c.prompt) : '无'}）`
  );
  check(Array.isArray(c.options), 'OPTIONS_ARRAY', `${at}.choice.options 必须是数组`);
  if (!Array.isArray(c.options)) return;
  check(c.options.length === 2, 'OPTIONS_COUNT', `${at}.choice.options 必须恰好 2 项（当前 ${c.options.length}）`);

  const seenOption = new Set();
  const seenEnding = new Set();
  c.options.forEach((o, j) => {
    const oat = `${at}.choice.options[${j}]`;
    if (!isObj(o)) {
      check(false, 'OPTION_OBJECT', `${oat} 必须是对象`);
      return;
    }
    check(
      isStr(o.optionId) && /^[a-z][a-z0-9_]{0,23}$/.test(o.optionId),
      'OPTION_ID',
      `${oat}.optionId 需匹配 ^[a-z][a-z0-9_]{0,23}$`
    );
    if (isStr(o.optionId)) {
      check(!seenOption.has(o.optionId), 'OPTION_ID_UNIQUE', `${oat}.optionId 在同一故事内重复：${o.optionId}`);
      seenOption.add(o.optionId);
    }
    check(
      isStr(o.label) && inRange(charLen(o.label), LIMITS.optionLabel),
      'LENGTH_LABEL',
      `${oat}.label 需 ${LIMITS.optionLabel[0]}–${LIMITS.optionLabel[1]} 字（当前 ${isStr(o.label) ? charLen(o.label) : '无'}）`
    );
    check(isStr(o.endingId), 'ENDING_REF', `${oat}.endingId 必填`);
    if (!isStr(o.endingId)) return;
    check(!seenEnding.has(o.endingId), 'ENDING_REF_UNIQUE', `${oat}.endingId 与同故事另一选项重复：${o.endingId}`);
    seenEnding.add(o.endingId);
    if (isStr(s.storyId)) {
      check(
        o.endingId === `${s.storyId}_end_1` || o.endingId === `${s.storyId}_end_2`,
        'ENDING_REF_MATCH',
        `${oat}.endingId 必须为 ${s.storyId}_end_1 或 ${s.storyId}_end_2`
      );
    }
  });
});

const endingById = new Map();
const endingRefCount = new Map();
const endingsPerStory = new Map();

stories.forEach((s) => {
  if (!isObj(s) || !isObj(s.choice) || !Array.isArray(s.choice.options)) return;
  s.choice.options.forEach((o) => {
    if (isObj(o) && isStr(o.endingId)) {
      endingRefCount.set(o.endingId, (endingRefCount.get(o.endingId) || 0) + 1);
    }
  });
});

endings.forEach((e, i) => {
  const at = `endings[${i}]`;
  if (!isObj(e)) {
    check(false, 'ENDING_OBJECT', `${at} 必须是对象`);
    return;
  }
  check(isStr(e.endingId), 'ENDING_ID', `${at}.endingId 必填`);
  if (isStr(e.endingId)) {
    check(ENDING_IDS.includes(e.endingId), 'ENDING_ID_SET', `${at}.endingId "${e.endingId}" 不在固定集合`);
    check(!endingById.has(e.endingId), 'ENDING_ID_UNIQUE', `endingId 重复：${e.endingId}`);
    if (!endingById.has(e.endingId)) endingById.set(e.endingId, e);
  }
  check(isStr(e.storyId), 'ENDING_STORY', `${at}.storyId 必填`);
  const story = isStr(e.storyId) ? storyById.get(e.storyId) : undefined;
  check(!!story, 'ENDING_STORY_REF', `${at}.storyId 引用了不存在的故事：${String(e.storyId)}`);

  if (story && isStr(e.storyId)) {
    check(
      isStr(e.endingId) && (e.endingId === `${e.storyId}_end_1` || e.endingId === `${e.storyId}_end_2`),
      'ENDING_ID_MATCH',
      `${at}.endingId 必须为 ${e.storyId}_end_1 或 ${e.storyId}_end_2`
    );
    endingsPerStory.set(e.storyId, (endingsPerStory.get(e.storyId) || 0) + 1);
    if (isStr(e.endingId)) {
      const refs = endingRefCount.get(e.endingId) || 0;
      check(refs === 1, 'ENDING_REF_COUNT', `${at}.endingId ${e.endingId} 应被恰好 1 个选项引用（当前 ${refs}）`);
    }
    const allowedExpr = Object.hasOwn(CHARACTER_EXPRESSIONS, story.character)
      ? CHARACTER_EXPRESSIONS[story.character]
      : [];
    check(
      isStr(e.expression) && allowedExpr.includes(e.expression),
      'EXPRESSION',
      `${at}.expression "${String(e.expression)}" 不是 ${story.character} 的合法表情（${allowedExpr.join('/')}）`
    );
  }

  check(
    isStr(e.title) && inRange(charLen(e.title), LIMITS.endingTitle),
    'LENGTH_ENDING_TITLE',
    `${at}.title 需 ${LIMITS.endingTitle[0]}–${LIMITS.endingTitle[1]} 字（当前 ${isStr(e.title) ? charLen(e.title) : '无'}）`
  );
  check(
    isStr(e.text) && inRange(charLen(e.text), LIMITS.endingText),
    'LENGTH_ENDING_TEXT',
    `${at}.text 需 ${LIMITS.endingText[0]}–${LIMITS.endingText[1]} 字（当前 ${isStr(e.text) ? charLen(e.text) : '无'}）`
  );
  check(Array.isArray(e.effects), 'EFFECTS_ARRAY', `${at}.effects 必须是数组（可为空）`);
  if (Array.isArray(e.effects)) {
    check(e.effects.length <= 3, 'EFFECTS_COUNT', `${at}.effects 最多 3 项（当前 ${e.effects.length}）`);
    e.effects.forEach((f, k) => {
      check(isStr(f) && EFFECTS.includes(f), 'EFFECT_ID', `${at}.effects[${k}] 非法效果：${JSON.stringify(f)}`);
    });
  }
});

stories.forEach((s) => {
  if (!isObj(s) || !isStr(s.storyId)) return;
  check(
    (endingsPerStory.get(s.storyId) || 0) === 2,
    'STORY_ENDINGS',
    `${s.storyId} 应恰好有 2 个结局（当前 ${endingsPerStory.get(s.storyId) || 0}）`
  );
  if (isObj(s.choice) && Array.isArray(s.choice.options)) {
    s.choice.options.forEach((o) => {
      if (isObj(o) && isStr(o.endingId)) {
        check(endingById.has(o.endingId), 'ENDING_MISSING', `${s.storyId} 的选项引用了不存在的结局：${o.endingId}`);
      }
    });
  }
});

if (sampleMode) {
  check(stories.length === 1, 'STORY_COUNT', 'B02 样稿须恰好包含 1 个故事，当前 ' + stories.length);
  check(endings.length === 2, 'ENDING_COUNT', 'B02 样稿须恰好包含 2 个结局，当前 ' + endings.length);
  check(storyById.has(SAMPLE_STORY_ID), 'B02_STORY_ID', 'B02 样稿须使用故事 ' + SAMPLE_STORY_ID);
} else if (!templateMode) {
  check(stories.length === 4, 'STORY_COUNT', `stories 必须恰好 4 个（当前 ${stories.length}）`);
  check(endings.length === 8, 'ENDING_COUNT', `endings 必须恰好 8 个（当前 ${endings.length}）`);
  STORY_IDS.forEach((id) => check(storyById.has(id), 'COMBO_COVERAGE', `缺少故事 ${id}`));
  ENDING_IDS.forEach((id) => check(endingById.has(id), 'ENDING_COVERAGE', `缺少结局 ${id}`));
}

report();
