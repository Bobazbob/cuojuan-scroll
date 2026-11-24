# 错卷 · 共享接口与图像规格 contract-v1

- 版本：v02（2026-11-23，H01 接收反馈修订）
- 维护：A
- 适用：B02/H02 样稿、H04–H09 正式故事与素材、A 的导入器与验证脚本
- 配套：`story-template.json`（合法示例）、`asset-template.csv`（资产登记）、`validate_stories.mjs`（自动检查）
- 变更：凡影响已定字段或 ID 的改动，A 先给变更表（旧值/新值/受影响文件/兼容方案），B 确认后生效；未通知不得新增必填字段。

## 1. 固定枚举（不得自行增删）

### 1.1 角色与表情

| character | 显示名 | 合法表情 |
|---|---|---|
| `daiyu` | 林黛玉 | `neutral` / `happy` / `upset` |
| `wukong` | 孙悟空 | `neutral` / `happy` / `angry` |

### 1.2 场景

| scene | 显示名 |
|---|---|
| `huaguoshan` | 花果山 |
| `daguanyuan` | 大观园 |

### 1.3 故事（storyId 固定）

| storyId | character | scene |
|---|---|---|
| `daiyu_huaguoshan` | `daiyu` | `huaguoshan` |
| `daiyu_daguanyuan` | `daiyu` | `daguanyuan` |
| `wukong_huaguoshan` | `wukong` | `huaguoshan` |
| `wukong_daguanyuan` | `wukong` | `daguanyuan` |

规则：`storyId` 必须等于 `character + "_" + scene`，不得另起名字。

### 1.4 结局（endingId 固定）

| endingId | 所属 storyId |
|---|---|
| `daiyu_huaguoshan_end_1` | `daiyu_huaguoshan` |
| `daiyu_huaguoshan_end_2` | `daiyu_huaguoshan` |
| `daiyu_daguanyuan_end_1` | `daiyu_daguanyuan` |
| `daiyu_daguanyuan_end_2` | `daiyu_daguanyuan` |
| `wukong_huaguoshan_end_1` | `wukong_huaguoshan` |
| `wukong_huaguoshan_end_2` | `wukong_huaguoshan` |
| `wukong_daguanyuan_end_1` | `wukong_daguanyuan` |
| `wukong_daguanyuan_end_2` | `wukong_daguanyuan` |

规则：`endingId` 必须等于 `storyId + "_end_1"` 或 `storyId + "_end_2"`。

### 1.5 效果（effectId 固定）

H01 交付的是规格与数据校验器。四个 ID 均可通过数据校验，当前交付中已实现且有可运行证据的效果为 0 项。下表四项均列为计划，接入后由 A 用实际版本逐项触发并记录结果。

| effectId | 计划表现 | 实现方式 | H01 状态 |
|---|---|---|---|
| `petal_fall` | 少量花瓣自上方飘落，约 2 秒，避开角色面部与 UI | 代码粒子 | 计划 |
| `petal_gather` | 约 1.5 秒向角色脚边收拢，目标由程序根据站位确定。无可用锚点时取角色安全区的下方中央 | 代码粒子 | 计划 |
| `gold_spark` | 角色附近的金色小点闪烁浮动，约 1.5 秒 | 代码粒子 | 计划 |
| `clone_echo` | 当前立绘的低透明度同姿残影，约 1 秒。空间足够时可在两侧，边缘按可用空间收拢或用单侧 | 代码残影 | 计划 |

规则：

- B 只填现有 `effects` ID，脚边、两侧与时长由程序决定。以上位置供制作构图参考，表中状态及参数不进入故事数据。
- 尚无运行支持时，B02 用结局文字区分分支。A 的可玩版按可用能力显示对应立绘表情，略过暂未接入的效果并继续进入结局。
- 同一结局允许重复使用同一效果（如 `["gold_spark", "gold_spark"]`）。
- 每个结局最多 3 项效果。
- 八个结局只能依赖两角色的三表情 + 本表效果表达；不得要求新增立绘、新角色或新效果。

## 2. 坐标与放置

- 坐标系：左上角 `(0,0)`，右下角 `(1,1)`；x 向右，y 向下；值为 0–1 的浮点数，保留 3 位小数。
- 脚底锚点：人物立绘"脚底中点"在该图片内的归一化位置（相对图片左上角）。必须实测后登记在 `assets.csv` 的 `foot_anchor_x` / `foot_anchor_y`；模板中的数值不是测量结果。
- 场景落点：脚底锚点落到场景画布上的位置。每个场景、每个角色各一个；由 B 在 H07/H08 的 `scene-notes.md` 中按 §6.4 建议，A 在真实页面校验后写入 `scenes.json`（A06/A07 实现）。未定稿前 A 使用占位落点。
- 点击放置：点中该角色落点即吸附站好；拖放为增强，松手同样吸附。
- 人物阴影由程序绘制，不烘焙进任何 PNG。

`scenes.json` 结构（A 维护；以下数值仅为格式示例，不是测量或验收结果）：

```json
{
  "schemaVersion": 1,
  "scenes": [
    {
      "sceneId": "huaguoshan",
      "frame": { "width": 1600, "height": 900 },
      "dropPoints": {
        "daiyu": { "x": 0.380, "y": 0.760 },
        "wukong": { "x": 0.620, "y": 0.760 }
      }
    },
    {
      "sceneId": "daguanyuan",
      "frame": { "width": 1600, "height": 900 },
      "dropPoints": {
        "daiyu": { "x": 0.420, "y": 0.750 },
        "wukong": { "x": 0.660, "y": 0.750 }
      }
    }
  ]
}
```

## 3. stories.json

- 位置：H04 包根目录，与 `endings.json` 分开提交。
- 顶层：`schemaVersion`（必须为 1）、`stories`（数组）。
- 每个故事恰好 1 个 `choice`、恰好 2 个 `option`，两个选项指向不同 `endingId`。

### 3.1 字段

| 字段 | 类型 | 必填 | 限制 | 说明 |
|---|---|---|---|---|
| `storyId` | string | 是 | 固定 4 值之一 | 必须等于 `character + "_" + scene` |
| `character` | string | 是 | `daiyu` / `wukong` | 出场角色 |
| `scene` | string | 是 | `huaguoshan` / `daguanyuan` | 所在场景 |
| `title` | string | 是 | 2–16 字 | 故事标题 |
| `intro` | string | 是 | 60–120 字 | 选择前的引入文字 |
| `choice.prompt` | string | 是 | 8–40 字 | 关键选择的提问 |
| `choice.options` | array | 是 | 恰好 2 项 | 顺序即按钮显示顺序 |
| `options[].optionId` | string | 是 | 匹配 `^[a-z][a-z0-9_]{0,23}$` | 同一故事内唯一 |
| `options[].label` | string | 是 | 2–12 字 | 选项按钮文字 |
| `options[].endingId` | string | 是 | `<storyId>_end_1` 或 `<storyId>_end_2` | 必须存在于 `endings.json` |

字数计法：去除所有空白与换行后的 Unicode 字符数，标点计入。

### 3.2 完整示例（与 story-template.json 中的示例一致）

```json
{
  "schemaVersion": 1,
  "stories": [
    {
      "storyId": "daiyu_huaguoshan",
      "character": "daiyu",
      "scene": "huaguoshan",
      "title": "灵石下的一瓣花",
      "intro": "卷轴翻错了页。黛玉睁眼时，脚下不是潇湘馆的青苔，而是花果山湿凉的石头。溪水里漂着一瓣不知名的花，崖边一块巨石微微发亮，像在等她开口。她认得这地方，却想不起自己为何认得。",
      "choice": {
        "prompt": "这一瓣花，她是要拾，还是要问？",
        "options": [
          {
            "optionId": "pick_petal",
            "label": "拾起那瓣花",
            "endingId": "daiyu_huaguoshan_end_1"
          },
          {
            "optionId": "ask_stone",
            "label": "问那块石头",
            "endingId": "daiyu_huaguoshan_end_2"
          }
        ]
      }
    }
  ]
}
```

## 4. endings.json

- 位置：H04 包根目录，与 `stories.json` 分开提交。
- 顶层：`schemaVersion`（必须为 1）、`endings`（数组）。
- 结局卡由 A 的统一卡面 + 本文件的 `title` / `text` / `expression` / `effects` 生成；B 不为单个结局交付专属图片。

### 4.1 字段

| 字段 | 类型 | 必填 | 限制 | 说明 |
|---|---|---|---|---|
| `endingId` | string | 是 | 固定 8 值之一 | 必须等于 `storyId + "_end_1/2"` |
| `storyId` | string | 是 | 必须存在于 `stories.json` | 所属故事 |
| `title` | string | 是 | 2–16 字 | 结局标题 |
| `text` | string | 是 | 80–160 字 | 结局正文 |
| `expression` | string | 是 | 所属角色的合法表情 | 结局卡立绘表情 |
| `effects` | array | 是（可为 `[]`） | 0–3 项，可重复 | 每项为固定 `effectId` |

### 4.2 完整示例（属于上面的示例故事）

```json
{
  "schemaVersion": 1,
  "endings": [
    {
      "endingId": "daiyu_huaguoshan_end_1",
      "storyId": "daiyu_huaguoshan",
      "title": "一瓣还山",
      "text": "她把花瓣放回溪水，看它打着旋儿流远。石头的光暗下去，像一声没说出口的叹息。风从崖上下来，替她理了理鬓边碎发。她忽然明白，这山不是她的归处，却肯替她收好这一瓣心事。起身时，裙角已干，石上多了一小片湿痕。",
      "expression": "upset",
      "effects": ["petal_fall", "petal_gather"]
    },
    {
      "endingId": "daiyu_huaguoshan_end_2",
      "storyId": "daiyu_huaguoshan",
      "title": "石上三问",
      "text": "她对着石头问了三句话：我从哪里来，要往哪里去，这里又是何处。石头不答，回声却一句句落下来，全是她自己的声音。她忽然笑了——原来这山里没有别人，只有被卷轴送错地方的自己。起身时，裙角沾了一小片金屑，像谁悄悄塞给她的路费。",
      "expression": "neutral",
      "effects": ["gold_spark", "gold_spark", "clone_echo"]
    }
  ]
}
```

## 5. 文本与内容约束

1. 全部原创中文；不整段引用原著、影视台词或网络文案。
2. 两个结局必须在"发生了什么、角色最终状态"上不同，不能只换结尾一句。
3. 两个选项必须有真实分歧，不能同义改写。
4. 剧情表现只允许两角色、两场景、三表情、四效果；不得要求新角色出场、新场景或新特效。
5. 不写与固定范围冲突的系统提示（如"获得道具""升级""解锁皮肤"）。

## 6. 图像规格

### 6.1 人物立绘

- 768×1024，PNG-32（RGBA），sRGB；单文件建议 ≤ 2MB。
- 透明底：人物以外 alpha=0；不得有底色、白边、投影、文字、边框。
- 全身完整（头顶到脚底），不裁切；同一角色的 3 个表情使用同一画布。
- 换表情不得改变身高、服装、发型与脚底位置；头脚位置偏差 ≤ 2px。
- 脚底中点距画布底边约 1%–3%，以实测为准，登记 `assets.csv`。
- 文件名：`characters/<character>/<character>_<expression>.png`

### 6.2 场景分层

- 每层 1600×900，PNG-32，sRGB，整幅画布；单文件建议 ≤ 2MB。
- 四层，自后向前：`layer1_back`（天空/远景）、`layer2_mid`（中景）、`layer3_ground`（地面/立足面）、`layer4_front`（前景遮挡）。
- `layer1_back` 为全幅不透明的底图，1600×900 画布每个像素的 alpha 均为 255，确保四层叠合无漏底。文件按 PNG-32 导出，RGBA 仍带 alpha 通道，资产表的 `has_alpha` 填 `true`。
- `layer2_mid`、`layer3_ground`、`layer4_front` 的无内容区 alpha=0，画面边缘可保留抗锯齿的半透明像素。中景、地面和前景各自只画本层内容。
- 四层叠合须与 `preview.png` 一致；不得把人物、按钮、文字烘焙进任何层。
- 前景可在两侧形成局部遮挡，须避开角色面部与 §6.4 定义的 UI 区域。按远景 → 中景 → 地面 → 人物试放 → 前景的顺序合成人工检查，UI 由程序在画面上层绘制。
- 文件名：`scenes/<scene>/<scene>_layer1_back.png` 等；`preview.png` 仅供检查，不导入游戏。

### 6.3 UI（H09）

- 卷轴框、纸纹、结局卡框：PNG-32，透明底，1600×900 或九宫格切片；不烘焙任何文字。
- 文件名：`ui/scroll_frame.png`、`ui/paper_texture.png`、`ui/ending_card_frame.png`；新增项先在 `assets.csv` 登记并通知 A。

### 6.4 场景 UI 与人物安全区（花果山、大观园共用）

所有范围以 1600×900 场景原图为基准，左上为原点，百分比按图像坐标换算。坐标是 v02 制作与接入基准。两场景实际落点由 B 随正式资产提议，A 在页面内定稿。

| 用途 | 归一化 x / y | 原图 x / y（px） | 构图与排版约定 |
|---|---|---|---|
| 底部阅读留白 | 0–1 / 0.80–1 | 0–1600 / 720–900 | 保留低对比地面或纸色，避开高反差纹样、前景枝叶和关键剧情细节 |
| 字幕、提问和两项选择 | 0.06–0.94 / 0.80–0.97 | 96–1504 / 720–873 | 底部居中。按剧情阶段切换字幕与选择，选项阶段呈现提问和两个完整按钮 |
| 画面内常驻控制（如静音、重玩） | 0.72–0.94 / 0.04–0.12 | 1152–1504 / 36–108 | 右上留空，供程序排布 |
| 人物安全区 | 0.18–0.82 / 0.12–0.80 | 288–1312 / 108–720 | 保护人物全身与关键动作。前景的实体与高对比边缘避开头脸，效果避开操作区 |
| 脚底落点建议范围 | 0.25–0.75 / 0.70–0.77 | 400–1200 / 630–693 | 两个角色落点都落在平缓地面上。可点区由程序向落点上方或两侧扩展并与字幕、按钮分离 |

- 桌面：16:9 场景按等比完整显示，宽或高有余量时居中留边，所有图层、人物与落点使用同一个场景变换。UI 有足够空间时用表中对应位置叠放。
- 手机横屏：同样等比完整显示，按系统安全区避开刘海、圆角和底部手势区。按钮与放置点击目标均至少 44×44 CSS px，字号和点击区由页面排版决定。字幕与按钮排不下时，把该阶段的 UI 整块移到场景下方，允许页面纵向滚动。竖屏沿用场景在上、操作区在下的排法。
- B 在 H02 样板中按表留白，在 H07/H08 提交双角色试放合成图和落点建议。A 接入后用桌面和实际横屏手机检查六个要点：四层边缘、人物全身、头脸遮挡、可点落点、最长文案/两个选项、横屏安全边距。无法容纳的控件走场景下方排版，场景内容按完整画面验收。

## 7. 文件命名、路径与资产登记

- 文件名一律小写字母、数字、下划线；扩展名小写；不得含空格、中文或版本号（版本由目录承担）。
- 每个交付包根目录必须带 `assets.csv` 与 `README-交接.md`；引用路径一律相对包根，不写本机绝对路径。
- 版本：v01 验收后冻结；返工交 v02，不覆盖 v01。
- H04 包含 `stories.json`、`endings.json`、`assets.csv`、`README-交接.md`；H05–H09 按本规格交付。
- 正式内容由 A 导入工程；B 不直接修改工程内文件。

### 7.1 assets.csv 列

| 列 | 说明 |
|---|---|
| `asset_id` | 稳定 ID：`<character>_<expression>` / `<scene>_layer<N>_<name>` / `ui_<name>` |
| `kind` | `character` / `scene_layer` / `ui` / `preview` |
| `character` | 人物资产填 `daiyu` / `wukong`，其余留空 |
| `scene` | 场景资产填场景 ID，其余留空 |
| `expression` | 人物资产填表情 ID，其余留空 |
| `layer` | 场景层填 `back` / `mid` / `ground` / `front`，其余留空 |
| `file_relpath` | 相对包根的文件路径 |
| `width` / `height` | 像素尺寸 |
| `has_alpha` | 是否含 alpha 通道，填 `true` / `false`。RGBA 全不透明底图填 `true` |
| `foot_anchor_x` / `foot_anchor_y` | 仅人物：图片内实测归一化坐标；未测量留空 |
| `status` | `example`（示例，正式登记前删除）/ `draft` / `measured` / `verified` |
| `notes` | 备注 |

## 8. 验证

### 8.1 可自动检查（`validate_stories.mjs`）

| 阶段 | 命令 | 输入与通过条件 |
|---|---|---|
| H01 随包示例自检 | `node validate_stories.mjs --template story-template.json` | 检查示例结构和引用 |
| B02/H02 单组样稿 | `node validate_stories.mjs --sample story-sample.json` | `schemaVersion: 1`，`stories` 恰好含 `daiyu_huaguoshan` 一条，`_exampleEndings` 恰好含对应 `_end_1` 和 `_end_2` 两条。原有字段、字数、枚举与引用检查均适用 |
| H04 正式内容 | `node validate_stories.mjs --stories stories.json --endings endings.json` | 正式文件分开提交，全部四个故事、八个结局及其引用齐全 |

B02 可复制 `story-template.json` 为 `story-sample.json`，在 `stories`、`_exampleEndings` 中分别替换真实样稿故事与结局。`_exampleEndings` 是现有模板的样稿容器。转入 H04 时将故事和结局分别写进正式文件的 `stories`、`endings` 数组，再补齐全集。正式文件仅保留各自的契约字段。

B02 通过时脚本显示 `PASS（B02 样稿模式）：故事 1 / 结局 2`。H04 正式验收以 `PASS（正式模式）：故事 4 / 结局 8` 为准。

覆盖：

1. JSON 可解析；`schemaVersion` = 1。
2. 必填字段、类型、字数限制。
3. ID 格式与唯一性；`storyId` = `character_scene`；`endingId` = `storyId_end_N`。
4. 每个故事恰好 2 个选项，`optionId` 唯一，两个 `endingId` 不同。
5. 引用存在：option→ending、ending→story；每个结局恰被 1 个选项引用；每个故事恰好 2 个结局。
6. 全集覆盖：4 个 storyId、8 个 endingId 无缺无多（正式模式）。
7. 表情属于所属角色；效果属于固定表且 ≤ 3 项。

本轮脚本不检查：`scenes.json` 的坐标范围与落点数值——该文件在 A06/A07 实现时另行加入检查。

退出码：0 通过；1 不通过（逐条输出问题）；2 输入无法解析。

### 8.2 必须人审

- 文本是否原创、通顺；两结局是否真正不同，选择是否有分歧。
- 气质是否贴合角色与场景；标题是否难读（字数合规不等于可读）。
- 透明底是否干净（放大看边缘）；三表情是否跳身高；脚底锚点与落点是否落地自然。
- 前景是否挡脸/挡按钮；效果在真机上的观感与时长。
- 图片尺寸、alpha 通道与像素透明度：在 H05–H08 另行检查，场景底层逐像素验证 alpha=255，上三层检查空白处 alpha=0。故事脚本覆盖 JSON，图像与设备效果另行验收。

## 9. 导入与变更

- A 原样导入 `stories.json` / `endings.json`，不改语义；数据不合法出报告，B 修。
- 为工程需要拆分文件时，ID 与文本保持不变。
- 变更流程：A 出变更表 → B 确认 → 更新模板并升版本 → 旧包保留。

## 10. 非目标（重申）

账号、实时 AI、3D、战斗、复杂走路、实时生图、逐结局专属美术、音频必需项、新增 ID。
