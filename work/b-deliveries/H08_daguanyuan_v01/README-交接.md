# H08 大观园正式四层 v01

B→A；2026-11-23，北京时间；H01 v02，固定ID和字段不变。

交付：scenes/daguanyuan下四PNG；原14列assets.csv；validation.json；scene-notes.md／visual-spec.md；无人物重组、黛玉与悟空各自试放、标注预览；reference.png及sources原件（仅溯源）。

四层实际生成，精确1600×900 RGBA/sRGB ICC。back逐像素alpha255，上三层有真实透明空白；mid与front的阅读带alpha全0。已经实际查看黛玉重组，树石／廊桥与地面没有明显接缝或重复整图；两角色静态包围盒均在安全框，front交集0。详见validation.json。全部正式层单文件均低于2MB。

建议落点（均非运行定稿）：黛玉x=0.625,y=0.750；悟空x=0.750,y=0.750。建议PNG画布高度504／480px。人物锚点来自H06实测。请A按scene-notes接入并用真实PNG复验脚底、遮挡、字幕、手机与全幅显示，再反馈素材或页面归属。不要沿用H03占位图参数或审美。

本批未修改工程或资产库，不声称游戏内站位、手机、运行视差或效果已测。后续A局部问题单只修定位项，不重画已经合格的部分。
