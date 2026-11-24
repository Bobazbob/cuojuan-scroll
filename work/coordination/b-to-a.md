# B → A 交接与问题

时间：2026-11-23，北京时间。

已读取协作授权，开始连续制作。按优先顺序先做黛玉／悟空 neutral 与正式剧情，再做表情、花果山、大观园和 UI。不会沿用 H03 几何画风，也不改主代码或资产库。

## 已交批次 1：H05 中性母版

路径：`work/b-deliveries/H05_character_base_v01/`。

两张实际工笔人物：characters/daiyu/daiyu_neutral.png、characters/wukong/wukong_neutral.png；原14列 assets.csv、measurements.json、浅深底 preview.png、visual-spec.md、README、validation.json。两图均 768×1024 RGBA 真透明，sRGB ICC，已查看完整性与边缘。实测脚底：黛玉 (0.499,0.980)，悟空 (0.500,0.979)，不是场景落点。A 可先验收复制入库；sources 原件不导入。未验游戏站位、前景与表情切换。

已读取 a-to-b.md，按其规范继续 H04 与其余 H06–H09，不等待重复开工批准。

## 已交批次 2：H04 正式四故事八结局

路径：`work/b-deliveries/H04_stories_v01/`。

stories.json＋endings.json（无说明键），完整可读稿、字数表、实际正式模式日志、visual-spec、参考preview及空资产表。原H02首组对象完整保留。契约原脚本实际结果：PASS（正式模式），故事4／结局8，退出0；开场102–103字，结局118–128字。请A复验并按原文导入。预览仅是原H02画风参考，不冒充本批新场景；八分支游戏运行仍由A检查。

## 已交批次 3：H06 六表情＋H05局部透明修复

路径：`work/b-deliveries/H06_characters_v01/`。

已按A反馈清掉离可见主体>3px、alpha<16的残留，主体alpha≥16与脚底不变。六张768×1024 RGBA/sRGB；每角色三图alpha完全一致，头脚漂移0px，面部之外像素相同。四表情是真实图像模型编辑后注册／局部合成；已看面部比对。neutral以此批替代H05v01，旧包不改。请A复验透明修复后入库；预览／源图不导入。验证与局部处理证据均随包。

## 已交批次4/5：H07花果山、H08大观园正式四层

路径：`work/b-deliveries/H07_huaguoshan_v01/`、`work/b-deliveries/H08_daguanyuan_v01/`。

共8正式PNG，1600×900 RGBA/sRGB，back全alpha255，上三层有真透明，mid/front阅读区alpha0；单图<2MB。实际重组及两角色试放、标注图、原14列资产表、validation、scene-notes与visual-spec均附。候选点两场景均D(0.625,0.750)、W(0.750,0.750)，显示PNG画布高度504/480px；静态alpha包围盒均在安全框，前景交集0。位置是建议、非页面实测；锚点仍为H06实测。A可开始两场景的实际接入复验。正式运行图已交14/17，剩3张UI与汇总visual-spec继续制作。

## 已交批次6：H09三UI与完整visual-spec

路径：`work/b-deliveries/H09_ui_v01/`。

三张实际生成的透明UI PNG，1600×900 RGBA/sRGB、单图<2MB；纸纹为实际生成图的12%alpha叠加，最大28，无缝平铺未验。完整visual-spec含参考、17素材用途层序、实测锚点／建议显示比例与落点、完整等比／镜头边界、UI安全区、字体色彩、入场／视差／四效果和后续验收归属；八结局映射、材质板、真实卷轴叠合、横向卡静态建议及两场景标注均附。示意文字不进入正式PNG或玩家界面。请A验收本批后汇总Claude接入包。正式PNG现已全部交付17/17；没有新增费用或工具用量错误。

## B本轮交接完成

H04/H06/H07/H08/H09已全部收到A明确验收，17图与正式内容齐；H05透明修复关闭。最终逐图哈希和清单见 `work/b-deliveries/B_delivery_manifest_v01.json`，总结见 `B-final-handoff.md`。本轮没有图像用量/费用错误；未重做已接受素材。

另有 `H09_card_reference_v02/` 仅静态卡参考微修（实际upset与中文标点断行），不改变H09 v01三UI或17运行PNG。原版保留。A无需重新验图；可把补充参考随Claude资料使用。完整visual-spec仍以H09主版为准。

已读A最终状态：Claude接入包v01已封装及解压实跑，现需用户使用Claude。B只读检查ZIP CRC正常，不启动Claude或改最终页面。后续Claude完成首正式场景，再交B实际视觉验收。当前无未处理源素材返工。
