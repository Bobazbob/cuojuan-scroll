# H09 UI与完整视觉规范 v01

B→A；2026-11-23，北京时间。H01 v02，资源ID与原14列assets.csv不变。

ui下scroll_frame.png、paper_texture.png、ending_card_frame.png三张实际生成PNG，均1600×900 RGBA/sRGB ICC，有真实透明像素，无烘焙文字。纸纹是实际生成纸纹的低alpha叠加版，最大alpha28；只作程序底色上的纹理，不声称已验证无缝平铺。三图均小于2MB。

附完整visual-spec.md、ending-effects.csv八结局映射、实际validation.json、三材质preview.png、真实场景＋卷轴stage-art-reference.png、横向结果卡静态参考ending-card-reference.png，以及两场景完整／标注参考。sources为生成原件，不导入。

已查看材质检查板、卷轴叠合和卡面静态参考。卡面中的阶段说明只作交接，所有参考图均非实际网页录屏；正式图片没有这些文字。UI按完整16:9等比使用，不宣称九宫格切片支持。请A复验透明区、正文／控件留白、实际图像解码，并结合全部17正式PNG及H04内容准备Claude包。

H04/H06/H07/H08已在a-to-b中获A接收；H05透明残留已由H06修复并关闭。H09尚待A验收；B没有启动Claude、改网页、改底层或资产库。Claude正式页面之后的最终视觉验收与真机结果仍未完成。
