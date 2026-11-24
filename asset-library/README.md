# 《错卷》首版资产盘点

第一阶段记录，以 H01 v02 契约和 H02 v01 交付为依据。当前覆盖林黛玉、孙悟空、花果山、大观园。

**首版 17 张正式运行 PNG、4 个故事与 8 个结局已验收入库。** B 确认的 H02 样板和原件另存参考区。H03 保留为功能测试页，其图形、布局和卡片只适用于功能对照。

| 范围 | 已通过 | 待验收 | 缺失 | 负责人 |
|---|---|---|---|---|
| H02 视觉参考 | [规范样板](reference/h02_style_v01/sample.png)，1600×900 RGBA、sRGB、全幅 alpha=255。原图归档，见 [B 的画风说明](reference/h02_style_v01/style-guide.md) | 无 | 无 | B 提供，A 入库 |
| 两角色 × 三表情 | H06 全部 6 张通过，H05 透明残留已修复 | 实景试放与表情切换 | 无 | B 制作并实测脚底，A 验收一致性 |
| 两场景 × 四层 | H07、H08 共 8 张通过，附重组预览和标注。A 已用浏览器确认四个落点 | 最终视觉层的视差、遮挡和缩放检查 | 无 | B 制作及提议落点，A 试放并定稿 |
| 卷轴框、纸纹、结局卡框 | H09 全部 3 张通过，1600×900 RGBA/sRGB。按 16:9 整图使用，纸纹为低 alpha 叠加层 | 正式页面控件及结果卡的组合检查 | 无 | B 交素材和说明，A 验收 |
| 效果 | 四个合法 ID 已固定 | 无已接入效果 | 四项代码效果均为计划，所需独立 PNG 为 0 | A 负责对接现有 ID，B 提供表现映射 |
| 故事与结局 | H04 的四故事八结局全部通过，首组样稿原样保留 | 无 | 无 | B 提供，A 独立复跑正式校验 |
| 结果卡 | 八结局的标题、正文、表情和效果字段、共用卡框与对应正式图层已齐。H09 提供静态卡面参考 | 正式卡面渲染、排版和导出 | 无素材缺项 | A／Claude 实现，B 验收视觉 |

“待验收”用于已经收到且有实际文件、尚未通过完整验收的条目。首轮盘点与入库依据见 [实检记录](verification.md)，浏览器结果见 [底层验证](../docs/core-verification.md)。

## 路径、版本和验收登记

- [assets.csv](assets.csv) 沿用 H01 v02 原有 14 列，只记录当前真实可读、已核对的文件。两条 preview 记录中的空 ID 与空脚底沿用 H02 规则。其“已通过”仅指视觉参考的使用范围或源图归档核对。
- [visual-requests.csv](visual-requests.csv) 按正式 ID 记录 17 项素材的路径、规格、版本、状态和负责人。目标路径以本目录为根。实际文件的尺寸、alpha 通道和脚底数据以资产表为准。
- 正式文件命名为 `characters/<character>/<character>_<expression>.png`、`scenes/<scene>/<scene>_layer<N>_<name>.png` 和 `ui/<name>.png`。沿用契约的 ID、枚举和相对路径。正式交付包按 H 号及 v01/v02 留档，登记表备注记录来源包版本。通过的旧版本留存。
- B 交实际 PNG、`assets.csv` 及 `README-交接.md`。脚底适用于立绘图片内的实测坐标，场景落点适用于场景画布。收到图时登记实际尺寸、alpha 通道和脚底，图像与数值核对前用 `draft` 或 `measured`，接收通过后用 `verified`。没有图或测量就留空。

## 交接标准

| 交接 | B 提交内容 | A 检查点 |
|---|---|---|
| H05 → H06 | 黛玉与悟空各一张中性立绘；用同一母版补黛玉 happy/upset、悟空 happy/angry。六张均为 768×1024 RGBA/sRGB，人物外透明，脚底中点实测，附表情对齐图 | 完整全身、无白边/投影、脚底和头顶变化 ≤2 px，三表情身份、姿态和道具保持一致 |
| H07 → H08 | 先交花果山，再交大观园。每场景四张 1600×900 RGBA/sRGB，同一坐标叠合，附 `preview.png`、`scene-notes.md`、两种角色的候选脚底落点和显示比例建议 | 底层 alpha 全 255；上三层空白处 alpha=0。检查接缝、层序、平缓站位、视野边界与遮挡 |
| H09 | 卷轴框、纸纹和一套可复用结局卡框，PNG-32，透明底，无烘焙文字。1600×900 或九宫格方式，采用九宫格时附切片边距。给出八结局对应的现有效果 ID 和表情 | 核对透明区、对比度、素材能否容纳 v02 安全区及最长文案。效果映射从数据核对，独立效果图无需提交 |
| H04 | `stories.json`、`endings.json`、`assets.csv`、`README-交接.md`。将已通过的首组样稿拆入正式文件，补齐下表缺项，保留 `schemaVersion: 1` | 运行正式模式，检查四故事、八结局、引用与字数，检查结果卡文本 |

## 剧情和结局卡数据

正式输入是 [stories.json](content/stories.json) 和 [endings.json](content/endings.json)。[H02 样稿](../src/data/story-sample.json)保留在 H03，和 H04 的首组对象逐字段一致。

| 故事 ID | 结局 ID | 状态 |
|---|---|---|
| `daiyu_huaguoshan` | `daiyu_huaguoshan_end_1`、`daiyu_huaguoshan_end_2` | 已通过（H02 样稿）。《花有归处》upset / petal_gather，《树上留春》happy / petal_fall |
| `daiyu_daguanyuan` | `daiyu_daguanyuan_end_1`、`daiyu_daguanyuan_end_2` | 已通过（H04） |
| `wukong_huaguoshan` | `wukong_huaguoshan_end_1`、`wukong_huaguoshan_end_2` | 已通过（H04） |
| `wukong_daguanyuan` | `wukong_daguanyuan_end_1`、`wukong_daguanyuan_end_2` | 已通过（H04） |

结局卡使用统一卡面与场景、角色名称，数据取结局 `title`、`text`、`expression`、`effects`，图像复用对应场景层和该表情立绘。标题 2–16 字、正文 80–160 字，去空白、计标点。B 无需另画八张卡或加字段。正式效果使用 `petal_fall`、`petal_gather`、`gold_spark`、`clone_echo`，前 3 项使用代码粒子，最后一项复用当前立绘做残影。

[B 的完整视觉规范](visual/visual-spec.md) · [卷轴叠合参考](visual/stage-art-reference.png) · [结局卡静态参考](visual/ending-card-reference.png) · [八结局映射](visual/ending-effects.csv)

## 坐标、层序与建议比例

人物图片内脚底中点已实测。黛玉三表情均为 (0.499, 0.980)，悟空三表情均为 (0.500, 0.979)。所有 PNG 以左上原点为准。A 在浏览器诊断样例中试放后，将两场景的黛玉 (0.625, 0.750) 与悟空 (0.750, 0.750) 写入 [scenes.json](content/scenes.json)。两场景的 [花果山](visual/huaguoshan/scene-notes.md) 与 [大观园](visual/daguanyuan/scene-notes.md) 交付说明保留候选到实测的由来。

画境按 1600×900 等比完整显示。绘制顺序为 `layer1_back` → `layer2_mid` → `layer3_ground` → 人物 → `layer4_front`，字幕和控制固定在独立 UI 层。已试放的完整人物 PNG 画布高度为黛玉 504px、悟空 480px，作为 [显示比例基线](visual/placements.json)。这包含透明空白，显示时保持 3:4，从实测锚点对齐脚底。当前图层未加出血，镜头平移基线为 0。

| 区域 | v02 归一化 x / y | 1600×900 原图 x / y |
|---|---|---|
| 底部阅读留白 | 0–1 / 0.80–1 | 0–1600 / 720–900 |
| 字幕、提问和选项 | 0.06–0.94 / 0.80–0.97 | 96–1504 / 720–873 |
| 右上常驻控件 | 0.72–0.94 / 0.04–0.12 | 1152–1504 / 36–108 |
| 人物安全区 | 0.18–0.82 / 0.12–0.80 | 288–1312 / 108–720 |
| 脚底落点建议范围 | 0.25–0.75 / 0.70–0.77 | 400–1200 / 630–693 |

人物和效果避让脸部与操作区。手机给按钮和放置目标留至少 44×44 CSS px。空间不足时把阅读与选择区移到场景下方，保持完整画面。正式素材已在诊断页试放，最终 UI 与真机另验。
