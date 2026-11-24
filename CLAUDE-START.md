# 《错卷》Claude 接入入口 v01

此包交付已验收的 17 张 PNG、四故事八结局、底层接口、实际调用示例、B 的视觉资料和运行证据。当前接手任务只有「黛玉来到花果山」的正式视觉与交互。H03 根入口仅保留作功能对照。

1. 直接运行 `node scripts/serve-dist.mjs`，打开 <http://127.0.0.1:4173/core-demo.html>。已含构建，无需先安装 npm 依赖。用“加载当前图层”查看正式素材组合，在放置阶段点画布圆环、走两条分支及重玩。开发和重建看 [README](README.md)。
2. 阅读 [发给 Claude 的任务](docs/claude-task.md)、[底层 API](docs/core-api.md) 和 [H01 v02 契约](docs/h01-v02/contract-v1.md)。机制从 `src/core/index.ts` 使用，原始剧情和站位在 `asset-library/content/`。
3. 以 [H02 用户确认的样板](asset-library/reference/h02_style_v01/sample.png)、[B 的完整视觉说明](asset-library/visual/visual-spec.md)、[花果山正式层重组和标注](asset-library/visual/huaguoshan/annotated-preview.png)作为视觉依据。[资产表与接入说明](asset-library/README.md)记录了实际尺寸、层序、脚底、落点和显示比例。
4. 先交一个真实可运行的正式场景给 B。B 验收通过后再处理其他组合、结果卡和手机布局。四项效果的实际播放、正式卡面、完整手机体验目前都待接入和验证。

[接入检查](docs/claude-readiness.md) · [浏览器验证](docs/core-verification.md)
