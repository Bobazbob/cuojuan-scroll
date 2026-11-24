// 将原文按句读切成字幕页。只切分、不改字：各页依次拼接后与原文完全相同。

const sentence = /[^。！？；…]+[。！？；…]+[”’」』）]*|[^。！？；…]+$/gu;
const clause = /[^，、：]+[，、：]+|[^，、：]+$/gu;

function pieces(text: string, pattern: RegExp) {
  return text.match(pattern) ?? [text];
}

/**
 * 贪心装页：fits(candidate) 由调用者用真实排版测量。
 * 单句放不下时退到逗号分句；仍放不下则单独成页，由调用者改用场景下方排版。
 */
export function paginate(text: string, fits: (candidate: string) => boolean): string[] {
  const pages: string[] = [];
  let current = '';
  const push = (unit: string) => {
    if (!current || fits(current + unit)) {
      current += unit;
      return;
    }
    pages.push(current);
    current = unit;
  };
  for (const unit of pieces(text, sentence)) {
    if (fits(unit)) push(unit);
    else for (const part of pieces(unit, clause)) push(part);
  }
  if (current) pages.push(current);
  if (pages.join('') !== text) throw new Error('字幕分页改变了原文。');
  return pages;
}
