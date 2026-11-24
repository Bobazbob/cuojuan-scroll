import sample from './data/story-sample.json';

export const story = sample.stories[0];
export type Ending = typeof sample._exampleEndings[number];
export type Option = typeof story.choice.options[number];
const endings = new Map(sample._exampleEndings.map((ending) => [ending.endingId, ending]));

export function endingFor(option: Option) {
  const ending = endings.get(option.endingId);
  return ending?.storyId === story.storyId ? ending : undefined;
}

export const sceneName = '花果山';
export const characterName = '林黛玉';
export const expressionNames: Record<string, string> = { upset: '怜惜', happy: '含笑' };

// H03 仅用静态反馈标记占位，四项正式效果仍按 H01 v02 列为计划。
export const effectPlaceholders: Record<string, string> = {
  petal_gather: '聚花',
  petal_fall: '落花',
};
