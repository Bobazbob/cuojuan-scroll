import { useEffect, useReducer, useRef, useState, type CSSProperties } from 'react';
import { createRoot } from 'react-dom/client';
import { characterArt, figureFoot, figureFootX, figureHeight, sceneArt, stand } from './art';
import { cardFont, createResultCard } from './card';
import { characterName, effectPlaceholders, endingFor, expressionNames, sceneName, story, type Ending, type Option } from './content';
import './style.css';

type Step = 'cover' | 'scene' | 'character' | 'place' | 'intro' | 'choice';
type Game = { step: Step; missed?: boolean } | { step: 'ending'; ending: Ending };
type Action = { type: 'open' | 'scene' | 'character' | 'place' | 'miss' | 'read' | 'replay' }
  | { type: 'choose'; option: Option };

function advance(game: Game, action: Action): Game {
  switch (action.type) {
    case 'open': return game.step === 'cover' ? { step: 'scene' } : game;
    case 'scene': return game.step === 'scene' ? { step: 'character' } : game;
    case 'character': return game.step === 'character' ? { step: 'place' } : game;
    case 'miss': return game.step === 'place' ? { step: 'place', missed: true } : game;
    case 'place': return game.step === 'place' ? { step: 'intro' } : game;
    case 'read': return game.step === 'intro' ? { step: 'choice' } : game;
    case 'choose': {
      if (game.step !== 'choice') return game;
      const ending = endingFor(action.option);
      return ending ? { step: 'ending', ending } : game;
    }
    case 'replay': return { step: 'cover' };
  }
}

function CardPreview({ ending }: { ending: Ending }) {
  const [card, setCard] = useState<{ src: string } | { error: string }>();

  useEffect(() => {
    let closed = false;
    let url: string | undefined;
    createResultCard(ending).then((blob) => {
      if (closed) return;
      url = URL.createObjectURL(blob);
      setCard({ src: url });
    }).catch(() => {
      if (!closed) setCard({ error: '未能生成结果卡。请关闭预览后重试。' });
    });
    return () => {
      closed = true;
      if (url) URL.revokeObjectURL(url);
    };
  }, [ending]);

  if (!card) return <p role="status">正在生成中文结果卡…</p>;
  if ('error' in card) return <p role="alert">{card.error}</p>;
  return <div className="card-output">
    <img src={card.src} alt={ending.title + ' · 中文结果卡'} />
    <a className="action primary" href={card.src} download={'错卷-' + ending.title + '.png'}>下载 PNG</a>
  </div>;
}

const layers = ['back', 'middle', 'ground', 'front'];
const figureStyle = {
  '--foot-x': (stand.x * 100) + '%',
  '--foot-y': (stand.y * 100) + '%',
  '--figure-h': (figureHeight * 100) + '%',
  '--sprite-foot-x': (figureFootX * -100) + '%',
  '--sprite-foot-y': (figureFoot * -100) + '%',
} as CSSProperties;
const placedSteps = ['intro', 'choice', 'ending'];

function App() {
  const [game, dispatch] = useReducer(advance, { step: 'cover' });
  const [preview, setPreview] = useState(false);
  const reading = useRef<HTMLElement>(null);
  const result = useRef<HTMLElement>(null);
  const drop = useRef<HTMLButtonElement>(null);
  const cover = game.step === 'cover';
  const placed = placedSteps.includes(game.step);
  const ending = game.step === 'ending' ? game.ending : undefined;
  const feedback = ending?.effects.map((effect) => effectPlaceholders[effect]).filter(Boolean).join('、');

  useEffect(() => {
    if (game.step === 'cover') return;
    const panel = game.step === 'place' ? drop.current : reading.current;
    panel?.focus({ preventScroll: true });
    panel?.scrollIntoView({ block: 'nearest' });
  }, [game.step]);

  useEffect(() => {
    if (preview) {
      result.current?.focus({ preventScroll: true });
      result.current?.scrollIntoView({ block: 'start' });
    }
  }, [preview]);

  function replay() {
    setPreview(false);
    dispatch({ type: 'replay' });
    window.scrollTo(0, 0);
  }

  function closePreview() {
    setPreview(false);
    reading.current?.querySelector('button')?.focus();
  }

  return <main className="shell">
    <header className="masthead">
      <div className="wordmark"><span className="seal" aria-hidden="true">卷</span><span>错卷</span></div>
      <span className="build">H03 v01 <span aria-hidden="true">·</span> 花果山篇</span>
    </header>
    <div className={'scroll-frame' + (cover ? ' closed' : '')}>
      <div className="stage" data-step={game.step} style={figureStyle}>
        <div className="stage-visual" onClick={() => {
          if (game.step === 'place') dispatch({ type: 'miss' });
        }}>
          {sceneArt.map((url, index) => <img className={'layer layer-' + layers[index]}
            src={url} alt="" aria-hidden="true" key={url} draggable="false" />)}
          {placed && <>
            <span className="figure-shadow" aria-hidden="true" />
            <img className="figure" src={characterArt} alt="林黛玉占位立绘"
              data-expression={ending?.expression ?? 'neutral'} draggable="false" />
          </>}
          {game.step === 'place' && <button ref={drop} className="drop-target"
            aria-label="将林黛玉放在标记处" aria-describedby="placement-help"
            onClick={(event) => { event.stopPropagation(); dispatch({ type: 'place' }); }}>
            <span aria-hidden="true" />
          </button>}
          {ending && <p className="expression-note">
            {expressionNames[ending.expression]} {feedback && '· ' + feedback + '占位'}
          </p>}
        </div>
        {cover && <div className="cover-content">
          <p className="eyebrow">花果山篇</p>
          <h1>错卷</h1>
          <p className="cover-line">诗中人，入山来。</p>
          <button className="action primary" onClick={() => dispatch({ type: 'open' })}>展开画卷</button>
        </div>}
      </div>

      {!cover && <div className="fixed-tools">
        <button className="action quiet" onClick={replay}>重玩</button>
      </div>}
      {!cover && <section className="reader" ref={reading} tabIndex={-1} aria-label="画卷阅读区">
        {game.step === 'scene' && <>
          <div><h1>选一处入卷</h1><p>翻开花果山这一页。</p></div>
          <button className="action primary" onClick={() => dispatch({ type: 'scene' })}>{sceneName}</button>
        </>}
        {game.step === 'character' && <>
          <div><h1>谁来到花果山？</h1><p>选定人物，再把她放进画卷。</p></div>
          <button className="action primary" onClick={() => dispatch({ type: 'character' })}>{characterName}</button>
        </>}
        {game.step === 'place' && <>
          <h1>放置林黛玉</h1>
          <p id="placement-help" role="status">{game.missed ? '请点岩台上带圆环的落点。' : '点击岩台上的圆环，让黛玉入画。'}</p>
        </>}
        {game.step === 'intro' && <>
          <div><h1>{story.title}</h1><p className="story-text">{story.intro}</p></div>
          <button className="action primary" onClick={() => dispatch({ type: 'read' })}>继续</button>
        </>}
        {game.step === 'choice' && <>
          <h1>{story.choice.prompt}</h1>
          <div className="choices">{story.choice.options.map((option) => <button className="action primary"
            key={option.optionId} onClick={() => dispatch({ type: 'choose', option })}>{option.label}</button>)}</div>
        </>}
        {ending && <>
          <div data-ending-id={ending.endingId}><h1>{ending.title}</h1><p className="story-text">{ending.text}</p></div>
          <button className="action primary" aria-expanded={preview}
            onClick={() => setPreview((visible) => !visible)}>{preview ? '关闭预览' : '预览结果卡'}</button>
        </>}
      </section>}
    </div>
    <footer className="footnote">场景与人物为占位素材</footer>
    {ending && preview && <section className="result" ref={result} tabIndex={-1} aria-labelledby="result-title">
      <div className="result-header"><h2 id="result-title">结果卡</h2>
        <button className="action quiet" onClick={closePreview}>关闭</button>
        <button className="action quiet" onClick={replay}>重玩</button>
      </div>
      <CardPreview key={ending.endingId} ending={ending} />
    </section>}
  </main>;
}

document.fonts.load('500 22px ' + cardFont).catch(() => {});
createRoot(document.getElementById('root')!).render(<App />);
