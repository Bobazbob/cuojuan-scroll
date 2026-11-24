"""Draw the original temporary paper scenery and token for H03. Requires Pillow."""
from math import cos, sin, tau
from pathlib import Path
from random import Random

from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parents[1] / "src" / "art"
OUT.mkdir(parents=True, exist_ok=True)
SIZE = (1600, 900)
RNG = Random(16)


def blank(size=SIZE):
    return Image.new("RGBA", size)


def save(image, layer):
    image.save(OUT / f"placeholder-{layer}.png", optimize=True)


def petal(draw, x, y, radius, color, turn=0):
    points = [
        (x + cos(turn + t * tau / 5) * radius, y + sin(turn + t * tau / 5) * radius)
        for t in range(5)
    ]
    draw.polygon(points, fill=color)


def rock(draw, x, y, width, height, colors):
    points = [(x, y), (x + width * .11, y - height * .68), (x + width * .48, y - height),
              (x + width * .79, y - height * .78), (x + width, y - height * .09)]
    draw.polygon(points, fill=colors[0])
    draw.polygon([points[0], points[2], points[3], (x + width * .59, y)], fill=colors[1])
    draw.line([points[1], points[2], points[3], points[4]], fill=colors[2], width=2)


def ridge(draw, points, color, floor):
    draw.polygon([*points, (1600, floor), (0, floor)], fill=color)


def sky():
    picture = blank()
    draw = ImageDraw.Draw(picture)
    for y in range(900):
        draw.line((0, y, 1600, y), fill=(246 - y // 85, 237 - y // 100, 218 - y // 170))
    draw.ellipse((1115, 146, 1229, 260), fill="#ecd1b6", outline="#e6c3a8", width=2)
    ranges = [
        ([(0, 350), (116, 278), (195, 315), (308, 211), (415, 298), (530, 263),
          (658, 166), (770, 268), (846, 233), (1011, 103), (1065, 132), (1167, 277),
          (1293, 235), (1424, 141), (1503, 167), (1600, 296)], "#cbd1ba"),
        ([(0, 499), (120, 434), (244, 468), (331, 361), (418, 431), (527, 392),
          (688, 268), (725, 263), (793, 330), (866, 420), (967, 351), (1035, 316),
          (1095, 326), (1174, 427), (1278, 348), (1350, 305), (1415, 361), (1505, 282),
          (1551, 303), (1600, 338)], "#a5bca8"),
        ([(0, 539), (149, 525), (299, 463), (411, 501), (533, 568), (677, 518), (813, 564),
          (960, 495), (1057, 520), (1210, 418), (1305, 392), (1429, 452), (1510, 423),
          (1600, 466)], "#85a798"),
    ]
    for points, color in ranges:
        ridge(draw, points, color, 695)
    mist = Image.new("L", SIZE)
    brush = ImageDraw.Draw(mist)
    for x, y, w, h in [(309, 440, 705, 63), (856, 286, 1090, 45), (1014, 507, 702, 80),
                       (1374, 390, 478, 35), (596, 569, 887, 57)]:
        brush.ellipse((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=150)
    wash = Image.new("RGBA", SIZE, (247, 238, 217))
    wash.putalpha(mist.filter(ImageFilter.GaussianBlur(16)))
    picture = Image.alpha_composite(picture, wash)
    draw = ImageDraw.Draw(picture)
    draw.polygon([(1321, 420), (1357, 425), (1349, 479), (1331, 524), (1325, 554), (1279, 572),
                  (1311, 544), (1316, 490)], fill="#e7e1d1")
    draw.line([(1343, 434), (1336, 489), (1320, 545)], fill="#f3ecdc", width=4)
    return picture


def middle():
    picture = blank()
    draw = ImageDraw.Draw(picture)
    ridge(draw, [(0, 488), (148, 456), (272, 497), (359, 477), (428, 522), (596, 559),
                 (753, 621), (980, 632), (1133, 599), (1262, 517), (1398, 531), (1517, 473),
                 (1600, 489)], "#91a891", 697)
    colors = ("#8a9b83", "#a4ac91", "#6f8979")
    for x, y, width, height in [(25, 639, 330, 154), (207, 652, 247, 113),
                                 (1380, 648, 238, 136), (1246, 642, 141, 74),
                                 (353, 635, 263, 63), (1300, 660, 205, 64)]:
        rock(draw, x, y, width, height, colors)
    return picture


def terrace():
    picture = blank()
    draw = ImageDraw.Draw(picture)
    for y in range(616, 900):
        draw.line((0, y, 1600, y), fill=(225 + (y - 616) // 16, 205 + (y - 616) // 14,
                                       174 + (y - 616) // 11))
    draw.polygon([(0, 596), (103, 587), (213, 610), (425, 605), (593, 625), (764, 618),
                  (961, 612), (1084, 626), (1262, 612), (1414, 594), (1600, 603),
                  (1600, 646), (0, 640)], fill="#dec9a9")
    for line in [[(0, 666), (166, 659), (327, 636), (394, 640)], [(449, 668), (551, 656), (734, 650)],
                 [(1000, 696), (1131, 693), (1263, 671), (1527, 675), (1600, 668)],
                 [(0, 709), (159, 706), (249, 693), (430, 695)], [(1380, 631), (1494, 628), (1600, 622)]]:
        draw.line(line, fill="#beaa8b", width=2, joint="curve")
    return picture


def foreground():
    picture = blank()
    draw = ImageDraw.Draw(picture)
    trunk = [(0, 642), (43, 600), (64, 483), (109, 386), (139, 282), (113, 210), (23, 169),
             (0, 137), (0, 95), (65, 132), (155, 161), (187, 227), (195, 181), (256, 107),
             (331, 80), (437, 77), (538, 31), (560, 39), (457, 98), (362, 115), (293, 139),
             (239, 193), (216, 272), (227, 326), (190, 387), (131, 461), (111, 592), (157, 641)]
    draw.polygon(trunk, fill="#6f6656")
    draw.line([(37, 625), (95, 568), (113, 474), (159, 392), (192, 320), (190, 267), (225, 189),
               (296, 132), (374, 105), (479, 90)], fill="#a18b6f", width=8, joint="curve")
    draw.line([(193, 255), (282, 219), (353, 216), (435, 180), (562, 172), (637, 138)],
              fill="#706553", width=12, joint="curve")
    draw.line([(335, 219), (400, 258), (489, 262), (576, 287)], fill="#81715b", width=7, joint="curve")
    draw.line([(176, 297), (119, 270), (41, 262)], fill="#81715b", width=8, joint="curve")
    draw.line([(303, 117), (287, 66), (304, 25)], fill="#706553", width=9, joint="curve")
    for cx, cy, spread, amount in [(61, 144, 123, 47), (240, 95, 107, 39), (384, 75, 120, 48),
                                   (550, 70, 106, 32), (518, 166, 119, 39), (394, 232, 98, 37),
                                   (595, 255, 76, 19), (63, 274, 85, 31)]:
        for _ in range(amount):
            x, y = cx + RNG.gauss(0, spread / 2.1), cy + RNG.gauss(0, spread / 3.6)
            r = RNG.uniform(5, 19)
            angle = RNG.uniform(0, tau)
            color = RNG.choice(("#c78991", "#d79fa1", "#ebbcb7", "#e7cec0", "#b57982", "#97a289"))
            petal(draw, x, y, r, color, angle)
            if r > 12 and color != "#97a289":
                draw.ellipse((x - 1.7, y - 1.7, x + 1.7, y + 1.7), fill="#9a666d")
    colors = ("#637f70", "#7c917d", "#566f64")
    for x, y, w, h in [(-45, 684, 217, 102), (80, 684, 174, 70), (1417, 686, 226, 128),
                        (1510, 698, 130, 82)]:
        rock(draw, x, y, w, h, colors)
    return picture


def figure():
    picture = blank((768, 1024))
    draw = ImageDraw.Draw(picture)
    # The token's feet sit near (374, 976), independently from the scene.
    draw.ellipse((300, 943, 376, 975), fill="#6d6253", outline="#514a41", width=5)
    draw.ellipse((392, 943, 460, 975), fill="#6d6253", outline="#514a41", width=5)
    draw.polygon([(301, 414), (467, 421), (479, 596), (546, 944), (433, 965), (290, 960),
                  (223, 944), (266, 694)], fill="#e7d7be", outline="#716657", width=6)
    draw.polygon([(349, 463), (385, 475), (428, 949), (351, 960), (302, 957)], fill="#d7a7a6")
    draw.polygon([(327, 285), (416, 274), (472, 321), (485, 479), (442, 537), (394, 471),
                  (351, 497), (298, 550), (260, 471), (267, 362)], fill="#97ac98", outline="#635f50", width=6)
    draw.polygon([(311, 294), (351, 285), (408, 402), (390, 435), (348, 379)], fill="#f3e5cd")
    draw.polygon([(403, 296), (435, 307), (416, 387), (390, 410), (370, 383)], fill="#c27f89")
    draw.line([(314, 451), (378, 466), (441, 449)], fill="#7e6256", width=12)
    draw.ellipse((281, 87, 464, 273), fill="#514c42")
    draw.ellipse((345, 44, 440, 134), fill="#514c42")
    draw.ellipse((315, 119, 453, 281), fill="#f1ddc6", outline="#7a6d5b", width=4)
    draw.pieslice((299, 90, 462, 260), 175, 334, fill="#514c42")
    draw.line([(354, 187), (370, 181), (383, 183)], fill="#725949", width=4)
    draw.line([(411, 182), (426, 180), (436, 184)], fill="#725949", width=4)
    draw.arc((385, 221, 424, 244), 15, 150, fill="#a16c67", width=4)
    for x, y, r in [(341, 116, 14), (317, 110, 11), (330, 90, 10), (355, 102, 8)]:
        petal(draw, x, y, r, "#cf959b", .5)
    draw.line([(453, 490), (598, 914)], fill="#796957", width=13)
    draw.polygon([(557, 919), (599, 902), (649, 919), (585, 947)], fill="#887761", outline="#625844", width=4)
    draw.ellipse((438, 476, 470, 513), fill="#eed9be", outline="#80745f", width=3)
    draw.ellipse((314, 484, 347, 521), fill="#eed9be", outline="#80745f", width=3)
    draw.line([(319, 545), (295, 702), (272, 860), (262, 935)], fill="#ab9f8b", width=5)
    draw.line([(465, 557), (467, 685), (506, 910), (511, 940)], fill="#ab9f8b", width=5)
    return picture


if __name__ == "__main__":
    for name, image in [("back", sky()), ("mid", middle()), ("ground", terrace()),
                        ("front", foreground()), ("daiyu", figure())]:
        save(image, name)
