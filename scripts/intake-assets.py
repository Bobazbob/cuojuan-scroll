"""Check a received B asset package. Accept specific images after visual review."""
import argparse
import csv
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
from shutil import copy2

from PIL import Image, ImageCms

LIBRARY = Path(__file__).resolve().parents[1] / "asset-library"
ASSET_COLUMNS = (
    "asset_id", "kind", "character", "scene", "expression", "layer", "file_relpath",
    "width", "height", "has_alpha", "foot_anchor_x", "foot_anchor_y", "status", "notes",
)


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        if not reader.fieldnames or any(None in row or None in row.values() for row in rows):
            raise ValueError(f"CSV 行列无效：{path.name}")
        return tuple(reader.fieldnames), rows


def write_csv(path, fields, rows):
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def actual_file(folder, name):
    path = (folder / name).resolve()
    if not path.is_relative_to(folder) or not path.is_file():
        raise ValueError(f"相对路径未指向包内文件：{name}")
    return path


def color_is_srgb(image):
    if "srgb" in image.info:
        return True
    profile = image.info.get("icc_profile")
    if not profile:
        return False
    label = ImageCms.getProfileDescription(ImageCms.getOpenProfile(BytesIO(profile)))
    return "srgb" in label.lower()


def checked_anchor(value):
    if not re.fullmatch(r"[01]\.\d{3}", value):
        raise ValueError("脚底坐标用实际测量的三个小数位")
    try:
        result = Decimal(value)
    except InvalidOperation as error:
        raise ValueError("脚底坐标无法解析") from error
    if not 0 <= result <= 1:
        raise ValueError("脚底坐标超出归一化范围")
    return result


def check_asset(row, requested, pack):
    kind = requested["kind"]
    if row["kind"] != kind or row["file_relpath"] != requested["target_relpath"]:
        raise ValueError("资源种类或路径与固定 ID 的登记不符")
    path = actual_file(pack, row["file_relpath"])
    if row["status"] not in {"draft", "measured", "verified"}:
        raise ValueError("无效交付状态")
    with path.open("rb") as file:
        header = file.read(26)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[24:26] != b"\x08\x06":
        raise ValueError("需要原生 8 位 RGBA PNG-32")
    with Image.open(path) as png:
        png.load()
        width, height = png.size
        if row["width"] != str(width) or row["height"] != str(height) or row["has_alpha"] != "true":
            raise ValueError(f"表中尺寸/通道与文件不符，实际 {width}×{height} RGBA")
        size = (768, 1024) if kind == "character" else (1600, 900)
        if kind == "ui" and png.size != size:
            notes_files = [p for p in pack.iterdir() if p.is_file() and p.suffix == ".md"]
            if not any("九宫格" in p.read_text(encoding="utf-8") for p in notes_files):
                raise ValueError("非 1600×900 的 UI 需随包给出九宫格说明")
        if kind != "ui" and png.size != size:
            raise ValueError(f"{kind} 的目标画幅为 {size}")
        if kind != "ui" and not color_is_srgb(png):
            raise ValueError("缺少可识别的 sRGB 声明")
        alpha = png.getchannel("A")
        lo, hi = alpha.getextrema()
        raw_bounds = alpha.getbbox()
        if not raw_bounds:
            raise ValueError("PNG 全部透明")
        bounds = raw_bounds
        if kind == "character":
            expected = f"{row['character']}_{row['expression']}"
            if expected != row["asset_id"] or row["scene"] or row["layer"]:
                raise ValueError("人物和表情列与固定 ID 不一致")
            bounds = alpha.point(lambda value: 255 if value >= 16 else 0).getbbox()
            if not bounds or bounds[0] == 0 or bounds[1] == 0 or bounds[2] == width or bounds[3] == height:
                raise ValueError("人物透明边界碰到画布边缘，需检查裁切")
            x = checked_anchor(row["foot_anchor_x"]) * width
            y = checked_anchor(row["foot_anchor_y"]) * height
            if not bounds[0] <= x <= bounds[2] or abs(y - bounds[3]) > 8:
                raise ValueError(f"登记的脚底不在人物接地带，实测 alpha 包围盒为 {bounds}")
            if any(abs(actual - visible) > 8 for actual, visible in zip(raw_bounds, bounds)):
                raise ValueError(f"人物可见轮廓之外有远处 alpha 残留（原始 {raw_bounds}，可见 {bounds}）")
        elif row["foot_anchor_x"] or row["foot_anchor_y"]:
            raise ValueError("非人物资源不登记人物脚底")
        if kind == "scene_layer":
            if row["scene"] != path.parent.name or not path.stem.endswith("_" + row["layer"]):
                raise ValueError("场景层级列与固定路径不一致")
        if row["layer"] == "back":
            if (lo, hi) != (255, 255):
                raise ValueError("远景底层需全幅 alpha=255")
        elif lo != 0:
            raise ValueError("无内容的透明区域需包含 alpha=0")
        return path, f"{width}×{height} RGBA，alpha={lo}..{hi}，边界 {bounds}", bounds


def update_registry(approved, requests, fields, pack):
    _, registered = read_csv(LIBRARY / "assets.csv")
    by_id = {row["asset_id"]: row for row in registered if row["asset_id"]}
    for row, path, _, _ in approved:
        asset_id = row["asset_id"]
        dest = LIBRARY / row["file_relpath"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.read_bytes() != path.read_bytes():
            previous = sha256(dest.read_bytes()).hexdigest()[:12]
            backup = LIBRARY / "archive" / previous / row["file_relpath"]
            backup.parent.mkdir(parents=True, exist_ok=True)
            copy2(dest, backup)
        copy2(path, dest)
        by_id[asset_id] = {**row, "status": "verified", "notes": pack.name + "；" + row["notes"]}
        requests[asset_id]["status"] = "已通过"
        requests[asset_id]["delivered_version"] = pack.name
    full = [row for row in registered if not row["asset_id"]] + [by_id[key] for key in sorted(by_id)]
    write_csv(LIBRARY / "assets.csv", ASSET_COLUMNS, full)
    write_csv(LIBRARY / "visual-requests.csv", fields, requests.values())
    manifest = []
    for row in by_id.values():
        record = {**row, "width": int(row["width"]), "height": int(row["height"]),
                  "has_alpha": row["has_alpha"] == "true"}
        for column in ("foot_anchor_x", "foot_anchor_y"):
            if row[column]:
                record[column] = float(row[column])
            else:
                del record[column]
        manifest.append(record)
    (LIBRARY / "runtime-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                                  encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path)
    parser.add_argument("--accept", nargs="+", metavar="ID", help="写入已目视确认的指定资源；默认仅检查")
    args = parser.parse_args()
    pack = args.pack.resolve()
    fields, request_rows = read_csv(LIBRARY / "visual-requests.csv")
    requests = {entry["asset_id"]: entry for entry in request_rows}
    columns, rows = read_csv(pack / "assets.csv")
    if columns != ASSET_COLUMNS:
        raise SystemExit("交付包的资产表与 H01 v02 的 14 列不一致")
    passed = {}
    used = set()
    seen_paths = set()
    failures = []
    for row in rows:
        key = row["asset_id"]
        try:
            path = row["file_relpath"]
            if not path or path in seen_paths:
                raise ValueError(f"文件路径缺失或重复：{path}")
            seen_paths.add(path)
            if row["kind"] == "preview":
                actual_file(pack, path)
                continue
            if not key or key in used:
                passed.pop(key, None)
                raise ValueError("资源 ID 缺失或重复")
            used.add(key)
            checked = check_asset(row, requests[key], pack)
            passed[key] = (row, *checked)
        except (ValueError, KeyError, OSError, ImageCms.PyCMSError) as error:
            passed.pop(key, None)
            failures.append((key or row["file_relpath"], str(error)))
    for key, (row, path, details, bounds) in list(passed.items()):
        if row["kind"] == "character" and row["expression"] != "neutral":
            base_id = f"{row['character']}_neutral"
            base = passed.get(base_id)
            base_row = base[0] if base else None
            base_bounds = base[3] if base else None
            if not base:
                _, registered = read_csv(LIBRARY/"assets.csv")
                base_row = next((entry for entry in registered if entry["asset_id"] == base_id), None)
                if base_row:
                    with Image.open(LIBRARY / base_row["file_relpath"]) as reference:
                        base_bounds = reference.getchannel("A").point(lambda value: 255 if value >= 16 else 0).getbbox()
            if not base_row or not base_bounds:
                failures.append((key, "缺少可对照的中性母版"))
                del passed[key]
            elif (abs(bounds[1] - base_bounds[1]) > 2 or abs(bounds[3] - base_bounds[3]) > 2
                  or abs(Decimal(row["foot_anchor_x"]) - Decimal(base_row["foot_anchor_x"])) * 768 > 2
                  or abs(Decimal(row["foot_anchor_y"]) - Decimal(base_row["foot_anchor_y"])) * 1024 > 2):
                failures.append((key, f"和中性母版头顶、脚底或脚底中点偏差超过 2px。当前 {bounds}，母版 {base_bounds}"))
                del passed[key]
    for key, (_, _, details, _) in passed.items():
        print("格式通过", key, details)
    for key, reason in failures:
        print("退回", key, reason)
    if args.accept:
        if set(args.accept) - passed.keys():
            raise SystemExit("有拟收条目未通过格式校验或不存在。")
        update_registry([passed[key] for key in sorted(set(args.accept))], requests, fields, pack)
        print("已入库（素材验收，游戏内试放另验）", *args.accept)
    elif failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
