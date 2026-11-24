"""Build the Claude intake ZIP only after the formal inputs and review record exist."""
import argparse
import csv
from pathlib import Path
from subprocess import run
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "asset-library"
OUTPUT = ROOT / "output"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engineering-snapshot", action="store_true",
                        help="打包工程检查点，素材未齐时使用。不能作为 Claude 正式接入包")
    args = parser.parse_args()
    with (LIBRARY / "visual-requests.csv").open(encoding="utf-8-sig", newline="") as source:
        assets = list(csv.DictReader(source))
    complete = len(assets) == 17 and all(row["status"] == "已通过" and (LIBRARY / row["target_relpath"]).is_file()
                                         for row in assets)
    if not complete and not args.engineering_snapshot:
        raise SystemExit("17 张正式素材未齐或尚未通过验收。")
    required = [
        "asset-library/content/stories.json", "asset-library/content/endings.json",
        "asset-library/runtime-manifest.json",
        "asset-library/reference/h02_style_v01/sample.png",
        "docs/claude-readiness.md", "docs/claude-task.md", "dist/core-demo.html",
        "output/core-runtime/index.js", "output/core-runtime/index.d.ts",
    ]
    if not args.engineering_snapshot:
        required.extend(["asset-library/content/scenes.json", "asset-library/visual/visual-spec.md",
                         "asset-library/visual/huaguoshan/preview.png",
                         "asset-library/visual/daguanyuan/preview.png"])
    missing = [name for name in required if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit("缺少 Claude 接入项：" + "、".join(missing))

    run(["node", "docs/h01-v02/validate_stories.mjs", "--stories", required[0], "--endings", required[1]],
        cwd=ROOT, check=True)
    run(["node", "scripts/verify-core.mjs", "--formal", "asset-library/content"], cwd=ROOT, check=True)
    include = [ROOT / name for name in (
        "README.md", "CLAUDE-START.md", "package.json", "package-lock.json", "index.html", "core-demo.html",
        "tsconfig.json", "tsconfig.core.json", "vite.config.mjs",
        "scripts/serve-dist.mjs", "scripts/verify-core.mjs", "scripts/intake-story.mjs",
        "scripts/intake-assets.py", "scripts/make-placeholders.py", "scripts/verify-scene-art.py",
        "scripts/package-claude.py",
    )]
    for directory in ("src", "public", "docs", "dist", "asset-library", "output/core-runtime"):
        base = ROOT / directory
        include.extend(path for path in base.rglob("*") if path.is_file()
                       and not any(part in {"archive", "__pycache__", "node_modules", ".git"}
                                   or part.startswith(".env") for part in path.relative_to(base).parts))

    prefix = "Cuojuan_engineering_checkpoint_v01" if args.engineering_snapshot else "Cuojuan_Claude_intake_v01"
    package = OUTPUT / (prefix + ".zip")
    with ZipFile(package, "x", ZIP_DEFLATED) as file:
        for path in sorted(include):
            file.write(path, f"{prefix}/{path.relative_to(ROOT).as_posix()}")
    with ZipFile(package) as file:
        assert file.testzip() is None
        for path in include:
            assert file.read(f"{prefix}/{path.relative_to(ROOT).as_posix()}") == path.read_bytes()
    print(package)


if __name__ == "__main__":
    main()
