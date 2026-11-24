export const characters = ['daiyu', 'wukong'] as const;
export const scenes = ['huaguoshan', 'daguanyuan'] as const;
export const sceneLayers = ['layer1_back', 'layer2_mid', 'layer3_ground', 'layer4_front'] as const;
export const uiAssetIds = ['ui_scroll_frame', 'ui_paper_texture', 'ui_ending_card_frame'] as const;

export type CharacterId = typeof characters[number];
export type SceneId = typeof scenes[number];
export type SceneLayer = typeof sceneLayers[number];
export type Expression = 'neutral' | 'happy' | 'upset' | 'angry';
export type StoryId = `${CharacterId}_${SceneId}`;
export type EndingId = `${StoryId}_end_${1 | 2}`;
export type CharacterAssetId = 'daiyu_neutral' | 'daiyu_happy' | 'daiyu_upset'
  | 'wukong_neutral' | 'wukong_happy' | 'wukong_angry';
export type SceneAssetId = `${SceneId}_${SceneLayer}`;
export type UiAssetId = typeof uiAssetIds[number];
export type AssetId = CharacterAssetId | SceneAssetId | UiAssetId;
export type EffectId = 'petal_fall' | 'petal_gather' | 'gold_spark' | 'clone_echo';
export type Point = Readonly<{ x: number; y: number }>;

export interface ChoiceOption {
  readonly optionId: string;
  readonly label: string;
  readonly endingId: EndingId;
}

export interface Story {
  readonly storyId: StoryId;
  readonly character: CharacterId;
  readonly scene: SceneId;
  readonly title: string;
  readonly intro: string;
  readonly choice: Readonly<{ prompt: string; options: readonly ChoiceOption[] }>;
}

export interface Ending {
  readonly endingId: EndingId;
  readonly storyId: StoryId;
  readonly title: string;
  readonly text: string;
  readonly expression: Expression;
  readonly effects: readonly EffectId[];
}

export interface Scene {
  readonly sceneId: SceneId;
  readonly frame: Readonly<{ width: 1600; height: 900 }>;
  readonly dropPoints: Readonly<Partial<Record<CharacterId, Point>>>;
}

export interface StoryDocument { readonly schemaVersion: 1; readonly stories: readonly Story[] }
export interface EndingDocument { readonly schemaVersion: 1; readonly endings: readonly Ending[] }
export interface SceneDocument { readonly schemaVersion: 1; readonly scenes: readonly Scene[] }

export interface GameData {
  readonly stories: StoryDocument;
  readonly endings: EndingDocument;
  readonly scenes: SceneDocument;
}

export type Phase = 'cover' | 'scene' | 'character' | 'placement' | 'intro' | 'choice' | 'ending';

export interface EffectDirective {
  readonly effectId: EffectId;
  readonly runId: number;
  readonly ordinal: number;
  readonly durationMs: number;
  readonly origin: 'scene-top' | 'foot' | 'character' | 'character-sides';
  readonly foot: Point;
}

export interface Composition {
  readonly back: SceneAssetId;
  readonly mid: SceneAssetId;
  readonly ground: SceneAssetId;
  readonly character?: CharacterAssetId;
  readonly front: SceneAssetId;
}

export interface Snapshot {
  readonly runId: number;
  readonly phase: Phase;
  readonly sceneId?: SceneId;
  readonly characterId?: CharacterId;
  readonly target?: Point;
  readonly foot?: Point;
  readonly story?: Story;
  readonly options: readonly ChoiceOption[];
  readonly ending?: Ending;
  readonly expression?: Expression;
  readonly composition?: Composition;
}

export interface ResultCardData {
  readonly storyId: StoryId;
  readonly sceneId: SceneId;
  readonly characterId: CharacterId;
  readonly ending: Ending;
  readonly composition: Composition;
  readonly frameAssetId: 'ui_ending_card_frame';
  readonly foot: Point;
}
