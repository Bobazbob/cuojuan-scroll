# 《错卷》底层接口

供 A 与后续 Claude 视觉层使用。入口为 [src/core/index.ts](../src/core/index.ts)，类型在 [types.ts](../src/core/types.ts)。原有 H03 页面用作功能对照。正式视觉从本接口读取状态和提交操作。引擎不持有 DOM、镜头、布局、字体、颜色、声音或定时器。

## 运行和示例

```sh
npm ci
npm run dev
npm run build
npm run play
```

从 Vite 的地址打开 `/core-demo.html`。构建版默认地址为 [本地接口示例](http://127.0.0.1:4173/core-demo.html)。示例按屏幕上的阶段按钮逐步调用，引擎提供剧情、选项、结局、效果指令和结果卡数据。示例读取已入库的 H04、H06、H07、H08。进入放置阶段后点“加载当前图层”，再点诊断画面上的圆环可验证真实点击；进入开场或结局后重新加载图层可核对立绘。此画布仅用于观察组合，不作为正式页面设计。

在 TypeScript 中可从 `src/core/index.ts` 导入。若需要已编译 JavaScript及类型声明，运行 `npm run build:core`，取 `output/core-runtime/index.js` 和同目录的声明文件。

## 输入

| 输入 | 结构 |
|---|---|
| `asset-library/content/stories.json` | H01 v02 正式 StoryDocument，`schemaVersion: 1` 与 `stories` |
| `asset-library/content/endings.json` | H01 v02 正式 EndingDocument，`schemaVersion: 1` 与 `endings` |
| `asset-library/content/scenes.json` | H01 v02 SceneDocument，`sceneId`、1600×900 `frame`、按角色索引的 `dropPoints` |
| `asset-library/runtime-manifest.json` | 从原 14 列资产登记表生成的运行视图，保留既定资源 ID 和相对路径。尺寸、透明通道、实测锚点用数值或布尔值。仅含已验收的运行图片 |
| `asset-library/visual/placements.json` | 接入参考。各场景内按角色记录 PNG 完整画布的已试放显示高度。此文件独立于 H01 v02 运行契约 |

每张人物图的 `foot_anchor_x/y` 是其图片内归一化脚底中点，场景 `dropPoints` 是场景画布内归一化脚底位置。视觉层应使用实际图像和画布尺寸把两者对齐。由展示层把指针坐标换算到完整画境，调用引擎；引擎用逻辑画布像素判定点击范围，默认半径 40px，可用 `createGame(data, hitRadiusPx)` 配置。触控目标仍应满足契约的至少 44 CSS px，键盘／直接命中可传 `state.target`。

## 调用顺序

```ts
const game = createGame({ stories, endings, scenes });
const unlisten = game.subscribe(render);
game.open();
game.selectScene('huaguoshan');
game.selectCharacter('daiyu');
const point = game.getState().target;
if (point && game.placeAt(point)) {
  game.showChoices();
  const option = game.getState().options[0];
  if (option && game.choose(option.optionId)) {
    const card = game.getResultCard();
    const effects = game.takeEffects();
    // 将卡片数据与效果指令交给展示层。
  }
}
game.replay();
unlisten();
```

| 接口 | 行为 |
|---|---|
| `getState()` | 当前阶段、场景与角色、落点或已放置的位置、表情、正文、可触发选项、结局和素材层级 ID |
| `availableScenes()` / `availableCharacters(sceneId)` | 根据已提供故事返回可用组合。H02 只显示一组，H04 全集显示四组 |
| `open()`、`selectScene(id)`、`selectCharacter(id)`、`placeAt(point)`、`showChoices()`、`choose(optionId)` | 成功返回 true；阶段、选项或坐标非法时返回 false 且状态不变。完成选择后连点被拒绝 |
| `takeEffects()` | 消费本次分支的指令队列，一次领取。含已定 effectId、序号、参考时长、作用位置和脚底坐标。后续视觉层据此渲染效果 |
| `getResultCard()` | 结局阶段给出原始结局、场景／角色／故事 ID、卡框 ID、分层与表情素材 ID 和脚底位置。卡面绘制和导出由展示层使用这些字段实现 |
| `getRunSignal()` / `replay()` | 每局有独立 AbortSignal。渲染层异步效果、监听或下载预览可绑定该信号。重玩中止旧局、清空剧情和未领效果，回到封卷。订阅者在视图卸载时主动取消订阅 |

资源加载 `createAssetLoader(records, decode)` 接受注入的文件解码方法。正式视觉可由浏览器解码 PNG，也可由测试器提供解码器。`get(id)` 读当前 `idle/loading/ready/error/missing`，`load(id)` 或 `loadAll(ids)` 实际加载。相同资源的并发请求合并，成功结果缓存，错误可以重试。重玩保留跨局资源缓存。调用者使用 `getRunSignal()` 防止旧局加载完成后渲染到新局。

## 验证

```sh
npm run verify:core
node docs/h01-v02/validate_stories.mjs --stories asset-library/content/stories.json --endings asset-library/content/endings.json
npm run verify:core -- --formal asset-library/content
```

第一条使用合成夹具跑四组合八结局及非法点击、连点、重玩和加载状态。后两条使用已收到的正式内容。没有正式落点时日志会明确标出临时候选坐标；正式人物试放、图层遮挡、视觉动画和真机结果卡另验。运行数据与原契约字段没有变更。
