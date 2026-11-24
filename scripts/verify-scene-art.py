"""Check the library's formal scene/character PNGs and render A-side placement previews."""
import argparse
import csv
import json
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "asset-library"
SCENES = ("huaguoshan", "daguanyuan")
CHARACTERS = ("daiyu", "wukong")
LAYERS = ("layer1_back", "layer2_mid", "layer3_ground", "layer4_front")
FRAME = (1600, 900)


def visible(alpha):
    return alpha.point(lambda n: 255 if n >= 16 else 0)


def check_scene(scene_id, configuration, records, directory, sizes, ratio):
    def image(asset_id):
        row = records[asset_id]
        assert row["status"] == "verified", asset_id
        with Image.open(LIBRARY / row["file_relpath"]) as png:
            return png.convert("RGBA")

    back, mid, ground, front = (image(f"{scene_id}_{layer}") for layer in LAYERS)
    for layer in (back, mid, ground, front):
        assert layer.size == FRAME
    assert back.getchannel("A").getextrema() == (255, 255)
    for layer in (mid, ground, front):
        assert layer.getchannel("A").getextrema()[0] == 0
    art = Image.alpha_composite(Image.alpha_composite(back, mid), ground)
    front_alpha = visible(front.getchannel("A"))
    for ui in ((96, 720, 1504, 873), (1152, 36, 1504, 108)):
        assert front_alpha.crop(ui).getbbox() is None, (scene_id, "front enters UI", ui)

    for character in CHARACTERS:
        point = configuration["dropPoints"][character]
        assert .25 <= point["x"] <= .75 and .70 <= point["y"] <= .77, (scene_id, character, point)
        asset_id = f"{character}_neutral"
        profile = records[asset_id]
        sprite = image(asset_id)
        _, top, _, bottom = visible(sprite.getchannel("A")).getbbox()
        scale = sizes.get(scene_id, {}).get(character, 0) / sprite.height
        if not scale:
            scale = ratio * FRAME[1] / (bottom - top)
        w, h = (round(n * scale) for n in sprite.size)
        sprite = sprite.resize((w, h), Image.Resampling.LANCZOS)
        offset = (round(point["x"] * FRAME[0] - float(profile["foot_anchor_x"]) * w),
                  round(point["y"] * FRAME[1] - float(profile["foot_anchor_y"]) * h))
        on_stage = Image.new("RGBA", FRAME)
        on_stage.alpha_composite(sprite, dest=offset)
        body = visible(on_stage.getchannel("A"))
        x1, y1, x2, y2 = body.getbbox()
        assert (288 <= x1 < x2 <= 1312 and 108 <= y1 < y2 <= 720), (scene_id, character, body.getbbox())
        head_box = (x1, y1, x2, y1 + round((y2 - y1) * .25))
        assert ImageChops.multiply(front_alpha.crop(head_box), body.crop(head_box)).getbbox() is None, (
            scene_id, character, "front intersects upper quarter of figure")
        blended = Image.alpha_composite(Image.alpha_composite(art, on_stage), front)
        file = directory / f"{scene_id}_{character}_placement.png"
        blended.save(file)
        print(scene_id, character, "foot", point, "visible frame", body.getbbox(), file.relative_to(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", choices=SCENES)
    parser.add_argument("--figure-ratio", type=float, default=.45,
                        help="diagnostic ratio of the visible sprite height to scene height")
    args = parser.parse_args()
    assert .4 <= args.figure_ratio <= .5
    config = json.loads((LIBRARY / "content/scenes.json").read_text(encoding="utf-8"))
    assert config["schemaVersion"] == 1
    by_scene = {scene["sceneId"]: scene for scene in config["scenes"]}
    placement = LIBRARY / "visual/placements.json"
    sizes = json.loads(placement.read_text(encoding="utf-8")) if placement.exists() else {}
    with (LIBRARY / "assets.csv").open(encoding="utf-8-sig", newline="") as file:
        records = {row["asset_id"]: row for row in csv.DictReader(file) if row["asset_id"]}
    destination = ROOT / "output/scene-art-review"
    destination.mkdir(parents=True, exist_ok=True)
    for scene_id in (args.scene,) if args.scene else SCENES:
        check_scene(scene_id, by_scene[scene_id], records, destination, sizes, args.figure_ratio)
    print("通过：尺寸、alpha、坐标、人物安全框、UI 区和头部遮挡代理检查。接地与画面仍需看图确认。")


if __name__ == "__main__":
    main()
