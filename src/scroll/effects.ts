import type { EffectDirective, EffectId } from '../core';

// 代码粒子效果（H01 §1.5）。本轮实装 petal_fall、petal_gather；
// gold_spark、clone_echo 不在本场景的结局中，暂未实装，遇到时跳过。
export const implementedEffects: readonly EffectId[] = ['petal_fall', 'petal_gather'];

const W = 1600;
const H = 900;
// 避让区（场景像素）：黛玉头脸、底部阅读区。
const FACE = { x0: 930, x1: 1070, y0: 190, y1: 300 };
const READ_TOP = 712;

type Petal = {
  x0: number; y0: number; x1: number; y1: number; sway: number; spin: number;
  size: number; delay: number; life: number; tone: number;
};

let sprites: HTMLCanvasElement[] | undefined;

/** 单瓣桃花：桃粉渐变 + 细墨褐描边，取样板色板。 */
function petalSprites() {
  if (sprites) return sprites;
  sprites = [['#F7D6D6', '#E7A9B3'], ['#F4C9CC', '#D995A6'], ['#FAE2DE', '#EDB7BD']].map(([a, b]) => {
    const c = document.createElement('canvas');
    c.width = 40; c.height = 40;
    const g = c.getContext('2d')!;
    g.translate(20, 20);
    const fill = g.createLinearGradient(0, -14, 0, 14);
    fill.addColorStop(0, a); fill.addColorStop(1, b);
    g.beginPath();
    g.moveTo(0, 14);
    g.bezierCurveTo(-13, 6, -12, -9, -4, -14);
    g.quadraticCurveTo(0, -10, 0, -12);
    g.quadraticCurveTo(0, -10, 4, -14);
    g.bezierCurveTo(12, -9, 13, 6, 0, 14);
    g.closePath();
    g.fillStyle = fill;
    g.fill();
    g.lineWidth = 1.1;
    g.strokeStyle = 'rgba(150, 92, 90, 0.55)';
    g.stroke();
    g.beginPath();
    g.moveTo(0, 11); g.lineTo(0, -6);
    g.strokeStyle = 'rgba(200, 110, 125, 0.35)';
    g.stroke();
    return c;
  });
  return sprites;
}

const rand = (a: number, b: number) => a + Math.random() * (b - a);
const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);

function fall(d: EffectDirective, offset: number): Petal[] {
  return Array.from({ length: 22 }, () => {
    let x = rand(260, 1380);
    // 起落路线避开脸部所在的竖带。
    if (x > FACE.x0 - 30 && x < FACE.x1 + 30) x += x < 1000 ? -140 : 140;
    return {
      x0: x, y0: rand(-40, 120), x1: x + rand(-90, 60), y1: rand(520, 660), sway: rand(14, 34),
      spin: rand(-2.4, 2.4), size: rand(0.42, 0.66), delay: offset + rand(0, d.durationMs * 0.35),
      life: d.durationMs * rand(0.6, 0.75), tone: Math.floor(rand(0, 3)),
    };
  });
}

function gather(d: EffectDirective, offset: number): Petal[] {
  const fx = d.foot.x * W;
  const fy = d.foot.y * H;
  return Array.from({ length: 16 }, (_, i) => {
    const side = i % 2 ? 1 : -1;
    const x0 = fx + side * rand(170, 380);
    return {
      x0, y0: rand(588, 690), x1: fx + side * rand(18, 70), y1: fy + rand(-6, 10), sway: rand(4, 10),
      spin: rand(-1.2, 1.2), size: rand(0.38, 0.55), delay: offset + rand(0, d.durationMs * 0.2),
      life: d.durationMs * rand(0.7, 0.8), tone: Math.floor(rand(0, 3)),
    };
  });
}

/** 播放本局效果指令；signal 中止（重玩）时立即清空画布。 */
export function playEffects(canvas: HTMLCanvasElement, directives: readonly EffectDirective[], signal: AbortSignal) {
  const ctx = canvas.getContext('2d');
  if (!ctx || signal.aborted) return;
  const petals: Petal[] = [];
  let offset = 250; // 等表情交叉淡化后再起
  for (const d of directives) {
    if (d.effectId === 'petal_fall') petals.push(...fall(d, offset));
    else if (d.effectId === 'petal_gather') petals.push(...gather(d, offset));
    else continue;
    offset += d.durationMs * 0.5;
  }
  if (!petals.length) return;
  const images = petalSprites();
  const end = Math.max(...petals.map((p) => p.delay + p.life)) + 400;
  const start = performance.now();
  let frame = 0;
  const clear = () => { cancelAnimationFrame(frame); ctx.clearRect(0, 0, W, H); };
  signal.addEventListener('abort', clear, { once: true });
  const tick = (now: number) => {
    if (signal.aborted) return;
    const t = now - start;
    ctx.clearRect(0, 0, W, H);
    for (const p of petals) {
      const k = (t - p.delay) / p.life;
      if (k <= 0) continue;
      const e = easeOut(Math.min(k, 1));
      const x = p.x0 + (p.x1 - p.x0) * e + Math.sin(k * 5 + p.x0) * p.sway * (1 - e);
      const y = p.y0 + (p.y1 - p.y0) * e;
      if (y > READ_TOP) continue;
      const fadeIn = Math.min(1, k * 5);
      const fadeOut = k < 1 ? 1 : Math.max(0, 1 - (t - p.delay - p.life) / 400);
      const alpha = fadeIn * fadeOut * (y > FACE.y0 - 20 && y < FACE.y1 && x > FACE.x0 && x < FACE.x1 ? 0.15 : 0.92);
      if (alpha <= 0) continue;
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.translate(x, y);
      ctx.rotate(p.spin * e + p.x0);
      ctx.scale(p.size, p.size * 0.82);
      ctx.drawImage(images[p.tone], -20, -20);
      ctx.restore();
    }
    if (t < end) frame = requestAnimationFrame(tick);
    else clear();
  };
  frame = requestAnimationFrame(tick);
}
