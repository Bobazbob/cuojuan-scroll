# 错卷

融合《红楼梦》和《西游记》的互动网页画卷。当前为 H03 v01（0.1.0），可玩「林黛玉 × 花果山」一组，两个结局。

## 启动

交接包已经包含生产构建。解压后，在有 Node.js 的终端进入包根运行：

```sh
node scripts/serve-dist.mjs
```

用浏览器访问 <http://127.0.0.1:4173/>。端口被占用时运行 `node scripts/serve-dist.mjs 4174`，打开终端打印的地址。页面、字体、图片和结果卡均可在本地使用。服务只监听本机。

源码开发和重新构建使用 Node.js 20.19+ 或 22.12+：

```sh
npm ci
npm run dev
npm run build
```

## 操作

展开画卷 → 花果山 → 林黛玉 → 点击岩台圆环 → 读开场 → 继续 → 两选一 → 预览结果卡 → 下载 PNG 或重玩。

- 「先安葬落花」进入《花有归处》，「立下护花约」进入《树上留春》。
- 点击空地会提示正确落点。重玩回到封卷，可以重新选择另一结局。
- 手机空间不足时，字幕和选项排到场景下方，可向下滚动。

## 内容与素材

H02 的 `story-sample.json` 原样接入，`src/content.ts` 负责按现有 ID 对照选项和结局。场景用 CSS 叠放四张几何临时图，人物用独立 PNG；图源为 `scripts/make-placeholders.py`，H02 平面样板仅作为配色和构图参考。结果卡用 Canvas 绘制为 1200×1100 PNG，载入同源本地图和本地 Noto Serif SC 字体子集。字体许可随部署文件提供。页面的表情文字与效果文字均为占位反馈。

H02 验收见 [docs/H02-acceptance.md](docs/H02-acceptance.md)。可运行交接包附独立运行记录、页面截图和导出的结果卡样件。

## 正式实现的底层接入

H03 继续保留在根路径作功能对照。新的视觉层使用 [底层接口](docs/core-api.md) 和 [资产库](asset-library/README.md)。本地服务启动后打开 `/core-demo.html`，可逐步调用场景选择、放置、分支、效果指令、结果卡数据和重玩。执行 `npm run verify:core -- --formal asset-library/content` 可复验 H04 四组八结局。
