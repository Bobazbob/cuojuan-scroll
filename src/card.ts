import { characterArt, sceneArt, stand, figureHeight, figureFoot, figureFootX } from './art';
import { characterName, expressionNames, sceneName, type Ending } from './content';

function loadImage(url: string): Promise<HTMLImageElement> {
  const image = new Image();
  image.src = url;
  return image.decode().then(() => image);
}

// 以实际字体宽度换行，并把常见中文行首禁排标点留在上一行。
function wrapText(context: CanvasRenderingContext2D, text: string, width: number) {
  const lines: string[] = [];
  let line = '';
  for (const char of text) {
    if (line && context.measureText(line + char).width > width) {
      if ('，。！？；：、）】》”’'.includes(char)) {
        lines.push(line + char);
        line = '';
        continue;
      }
      const last = line.at(-1) ?? '';
      if (line.length > 1 && '（【《“‘'.includes(last)) {
        lines.push(line.slice(0, -1));
        line = last + char;
        continue;
      }
      lines.push(line);
      line = '';
    }
    line += char;
  }
  if (line) lines.push(line);
  return lines;
}

export const cardFont = '"Cuoplan Serif", "Noto Serif SC", "Songti SC", SimSun, serif';

export async function createResultCard(ending: Ending): Promise<Blob> {
  const [back, middle, ground, front, character] = await Promise.all(
    [...sceneArt, characterArt].map(loadImage),
  );
  await document.fonts.load('500 36px ' + cardFont);
  const canvas = document.createElement('canvas');
  canvas.width = 1200;
  canvas.height = 1100;
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('浏览器无法建立画布。');

  ctx.fillStyle = '#f4ebdd';
  ctx.fillRect(0, 0, 1200, 1100);
  ctx.strokeStyle = '#b3a38c';
  ctx.lineWidth = 2;
  ctx.strokeRect(32, 32, 1136, 1036);
  ctx.fillStyle = '#315950';
  ctx.font = '500 27px ' + cardFont;
  ctx.fillText('错卷  ·  ' + sceneName + '篇', 72, 91);
  ctx.save();
  ctx.translate(72, 120);
  const width = 1056;
  const height = width * 9 / 16;
  for (const layer of [back, middle, ground]) ctx.drawImage(layer, 0, 0, width, height);
  const figureH = height * figureHeight;
  const figureW = figureH * 0.75;
  ctx.drawImage(character, width * stand.x - figureW * figureFootX, height * stand.y - figureH * figureFoot, figureW, figureH);
  ctx.drawImage(front, 0, 0, width, height);
  ctx.fillStyle = '#315950';
  ctx.fillRect(22, 26, 324, 49);
  ctx.fillStyle = '#fff8ec';
  ctx.font = '500 23px ' + cardFont;
  ctx.fillText('场景与人物为占位示意', 41, 59);
  ctx.restore();
  ctx.fillStyle = '#382f29';
  ctx.font = '500 56px ' + cardFont;
  ctx.fillText(ending.title, 72, 789, 1050);
  ctx.fillStyle = '#315950';
  ctx.font = '500 22px ' + cardFont;
  ctx.fillText(characterName + ' · ' + (expressionNames[ending.expression] ?? '') + '  /  H03 v01', 74, 828);
  ctx.fillStyle = '#382f29';
  ctx.font = '500 30px ' + cardFont;
  wrapText(ctx, ending.text, 1000).forEach((line, index) => ctx.fillText(line, 74, 878 + index * 42));

  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => blob ? resolve(blob) : reject(new Error('无法生成 PNG。')), 'image/png');
  });
}
