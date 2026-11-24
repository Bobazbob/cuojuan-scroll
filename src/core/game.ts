import type {
  CharacterAssetId, CharacterId, Composition, EffectDirective, EffectId, Ending, EndingId,
  GameData, Phase, Point, ResultCardData, Scene, SceneId, Snapshot, Story, StoryId,
} from './types.js';

const effectPlan: Record<EffectId, Pick<EffectDirective, 'durationMs' | 'origin'>> = {
  petal_fall: { durationMs: 2000, origin: 'scene-top' },
  petal_gather: { durationMs: 1500, origin: 'foot' },
  gold_spark: { durationMs: 1500, origin: 'character' },
  clone_echo: { durationMs: 1000, origin: 'character-sides' },
};

function uniqueBy<K, T>(items: readonly T[], key: (item: T) => K): Map<K, T> {
  const map = new Map<K, T>();
  for (const item of items) {
    const id = key(item);
    if (map.has(id)) throw new Error('重复 ID：' + id);
    map.set(id, item);
  }
  return map;
}

function normalized(point: Point) {
  return Number.isFinite(point.x) && Number.isFinite(point.y)
    && point.x >= 0 && point.x <= 1 && point.y >= 0 && point.y <= 1;
}

export function createGame(data: GameData, hitRadiusPx = 40) {
  if (![data.stories, data.endings, data.scenes].every((doc) => doc.schemaVersion === 1)) {
    throw new Error('错卷数据的 schemaVersion 必须为 1。');
  }
  if (!Number.isFinite(hitRadiusPx) || hitRadiusPx <= 0) throw new Error('落点半径必须是正数。');
  const storyById = uniqueBy<StoryId, Story>(data.stories.stories, (story) => story.storyId);
  const endingById = uniqueBy<EndingId, Ending>(data.endings.endings, (ending) => ending.endingId);
  const sceneById = uniqueBy<SceneId, Scene>(data.scenes.scenes, (scene) => scene.sceneId);
  for (const scene of sceneById.values()) {
    if (scene.frame.width !== 1600 || scene.frame.height !== 900
      || Object.values(scene.dropPoints).some((point) => !normalized(point))) {
      throw new Error('场景坐标或画布规格无效：' + scene.sceneId);
    }
  }
  for (const story of storyById.values()) {
    if (story.storyId !== story.character + '_' + story.scene
      || !sceneById.get(story.scene)?.dropPoints[story.character]
      || story.choice.options.length !== 2
      || new Set(story.choice.options.map((option) => option.optionId)).size !== 2
      || new Set(story.choice.options.map((option) => option.endingId)).size !== 2
      || story.choice.options.some((option) => endingById.get(option.endingId)?.storyId !== story.storyId)) {
      throw new Error('故事缺合法落点、有效选项或有效结局：' + story.storyId);
    }
  }

  let phase: Phase = 'cover';
  let runId = 1;
  let lifetime = new AbortController();
  let sceneId: SceneId | undefined;
  let characterId: CharacterId | undefined;
  let story: Story | undefined;
  let ending: Ending | undefined;
  let foot: Point | undefined;
  let effects: EffectDirective[] = [];
  const listeners = new Set<(state: Snapshot) => void>();

  function composition(): Composition | undefined {
    if (!sceneId) return;
    return {
      back: sceneId + '_layer1_back' as Composition['back'],
      mid: sceneId + '_layer2_mid' as Composition['mid'],
      ground: sceneId + '_layer3_ground' as Composition['ground'],
      character: foot && characterId
        ? (characterId + '_' + (ending?.expression ?? 'neutral')) as CharacterAssetId : undefined,
      front: sceneId + '_layer4_front' as Composition['front'],
    };
  }

  function getState(): Snapshot {
    return {
      runId, phase, sceneId, characterId, foot, ending,
      target: phase === 'placement' && sceneId && characterId
        ? sceneById.get(sceneId)?.dropPoints[characterId] : undefined,
      story: foot ? story : undefined,
      expression: foot ? ending?.expression ?? 'neutral' : undefined,
      options: phase === 'choice' ? story?.choice.options ?? [] : [],
      composition: composition(),
    };
  }

  function publish() {
    const snapshot = getState();
    for (const callback of listeners) callback(snapshot);
  }

  function transition(from: Phase, to: Phase) {
    if (phase !== from) return false;
    phase = to;
    publish();
    return true;
  }

  function availableScenes() {
    return [...new Set(data.stories.stories.map((entry) => entry.scene))];
  }

  function availableCharacters(id: SceneId) {
    return data.stories.stories.filter((entry) => entry.scene === id).map((entry) => entry.character);
  }

  return {
    getState,
    getRunSignal: () => lifetime.signal,
    availableScenes,
    availableCharacters,
    subscribe(callback: (state: Snapshot) => void) {
      listeners.add(callback);
      return () => { listeners.delete(callback); };
    },
    open: () => transition('cover', 'scene'),
    selectScene(id: SceneId) {
      if (phase !== 'scene' || !availableScenes().includes(id)) return false;
      sceneId = id;
      return transition('scene', 'character');
    },
    selectCharacter(id: CharacterId) {
      if (phase !== 'character' || !sceneId) return false;
      const selected = storyById.get(`${id}_${sceneId}`);
      if (!selected) return false;
      characterId = id;
      story = selected;
      return transition('character', 'placement');
    },
    placeAt(point: Point) {
      if (phase !== 'placement' || !sceneId || !characterId || !normalized(point)) return false;
      const scene = sceneById.get(sceneId);
      const target = scene?.dropPoints[characterId];
      if (!scene || !target) return false;
      if (Math.hypot((target.x - point.x) * scene.frame.width, (target.y - point.y) * scene.frame.height)
        > hitRadiusPx) return false;
      foot = target;
      return transition('placement', 'intro');
    },
    showChoices: () => transition('intro', 'choice'),
    choose(optionId: string) {
      if (phase !== 'choice' || !foot || !story) return false;
      const option = story.choice.options.find((entry) => entry.optionId === optionId);
      const target = option && endingById.get(option.endingId);
      if (!target) return false;
      ending = target;
      const origin = foot;
      effects = target.effects.map((effectId, ordinal) => ({
        effectId, runId, ordinal, ...effectPlan[effectId], foot: origin,
      }));
      return transition('choice', 'ending');
    },
    takeEffects(): readonly EffectDirective[] {
      const pending = effects;
      effects = [];
      return pending;
    },
    getResultCard(): ResultCardData | undefined {
      const art = composition();
      if (!sceneId || !characterId || !ending || !story || !foot || !art) return;
      return { storyId: story.storyId, sceneId, characterId, ending, composition: art,
        frameAssetId: 'ui_ending_card_frame', foot };
    },
    replay() {
      const previous = lifetime;
      lifetime = new AbortController();
      runId++;
      phase = 'cover';
      sceneId = undefined;
      characterId = undefined;
      story = undefined;
      ending = undefined;
      foot = undefined;
      effects = [];
      previous.abort();
      publish();
    },
  };
}

export type Game = ReturnType<typeof createGame>;
