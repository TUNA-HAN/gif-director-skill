from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from gif_utils import inspect_gif, write_json


SCRIPT_DIR = Path(__file__).resolve().parent


PACK_DEFAULTS = [
    ("hello", "확인했어요", "bounce"),
    ("laugh", "좋아요", "pulse"),
    ("tired", "잠깐만요", "wiggle"),
    ("love", "완전 추천", "caption-pop"),
]


PRESETS = {
    "chat": (512, 512, "caption-pop", 1.6),
    "sticker": (512, 512, "bounce", 1.5),
    "detail-page": (900, 506, "detail-page", 2.0),
    "ad-banner": (1080, 1080, "pulse", 1.8),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="High-level GIF Director runner with validation and repair.")
    parser.add_argument("--mode", choices=["quick", "pack", "marketing", "optimize"], default="quick")
    parser.add_argument("--image", type=Path, action="append", help="Input image. Repeat for multi-image GIFs.")
    parser.add_argument("--input-gif", type=Path, help="Existing GIF for optimize mode.")
    parser.add_argument("--text", default="")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--base-name", default="gif-director")
    parser.add_argument("--preset", default="chat", help="chat, sticker, detail-page, ad-banner, or a render_gif preset.")
    parser.add_argument("--max-bytes", type=int, default=8_000_000)
    parser.add_argument("--max-width", type=int, default=720)
    parser.add_argument("--max-frames", type=int, default=14)
    return parser.parse_args()


def run_python(args: list[str]) -> None:
    result = subprocess.run([sys.executable, "-B", *args], text=True, capture_output=True, check=False, encoding="utf-8")
    if result.returncode != 0:
        raise SystemExit(result.stderr + result.stdout)


def preset_details(name: str) -> tuple[int, int, str, float]:
    if name in PRESETS:
        return PRESETS[name]
    return 512, 512, name, 1.7


def render_one(
    images: list[Path],
    text: str,
    output: Path,
    report: Path,
    preset_name: str,
    max_bytes: int,
) -> dict:
    width, height, render_preset, duration = preset_details(preset_name)
    args = [str(SCRIPT_DIR / "render_gif.py")]
    for image in images:
        args.extend(["--image", str(image)])
    args.extend(
        [
            "--text",
            text,
            "--output",
            str(output),
            "--report",
            str(report),
            "--preset",
            render_preset,
            "--width",
            str(width),
            "--height",
            str(height),
            "--duration",
            str(duration),
        ]
    )
    run_python(args)
    validation = validate(output, max_bytes=max_bytes)
    if not validation["ok"]:
        repaired = output.with_name(output.stem + "-repair.gif")
        repair_report = report.with_name(report.stem + "-repair.json")
        repair_width = max(320, round(width * 0.82))
        repair_height = max(240, round(height * 0.82))
        args = [str(SCRIPT_DIR / "render_gif.py")]
        for image in images:
            args.extend(["--image", str(image)])
        args.extend(
            [
                "--text",
                text,
                "--output",
                str(repaired),
                "--report",
                str(repair_report),
                "--preset",
                "caption-pop",
                "--width",
                str(repair_width),
                "--height",
                str(repair_height),
                "--duration",
                "1.4",
                "--fps",
                "8",
            ]
        )
        run_python(args)
        output = repaired
        report = repair_report
        validation = validate(output, max_bytes=max_bytes)
    return {"gif": str(output), "report": str(report), "validation": validation}


def validate(path: Path, max_bytes: int) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPT_DIR / "validate_gif.py"),
            "--input",
            str(path),
            "--max-bytes",
            str(max_bytes),
            "--json",
        ],
        text=True,
        capture_output=True,
        check=False,
        encoding="utf-8",
    )
    if result.stdout.strip():
        import json

        return json.loads(result.stdout)
    return {"ok": False, "issues": [result.stderr.strip() or "validation failed"]}


def make_sheet(gif_path: Path, sheet_path: Path) -> None:
    run_python([str(SCRIPT_DIR / "make_contact_sheet.py"), "--input", str(gif_path), "--output", str(sheet_path), "--columns", "4"])


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    images = args.image or []
    if args.mode != "optimize" and not images:
        raise SystemExit("--image is required unless --mode optimize")

    if args.mode == "pack":
        outputs = []
        for suffix, caption, preset in PACK_DEFAULTS:
            gif_path = args.output_dir / f"{args.base_name}-{suffix}.gif"
            report_path = args.output_dir / f"{args.base_name}-{suffix}.json"
            outputs.append(render_one(images, caption, gif_path, report_path, preset, args.max_bytes))
        pack_report = {"mode": "pack", "outputs": outputs}
        write_json(args.output_dir / f"{args.base_name}-pack.json", pack_report)
        print(f"OK wrote pack report {args.output_dir / f'{args.base_name}-pack.json'}")
        return 0

    if args.mode == "optimize":
        if not args.input_gif:
            raise SystemExit("--input-gif is required for optimize mode")
        optimized = args.output_dir / f"{args.base_name}.gif"
        optimize_report = args.output_dir / f"{args.base_name}.json"
        run_python(
            [
                str(SCRIPT_DIR / "optimize_gif.py"),
                "--input",
                str(args.input_gif),
                "--output",
                str(optimized),
                "--report",
                str(optimize_report),
                "--max-width",
                str(args.max_width),
                "--max-frames",
                str(args.max_frames),
            ]
        )
        validation = validate(optimized, max_bytes=args.max_bytes)
        report = {"mode": "optimize", "gif": str(optimized), "report": str(optimize_report), "validation": validation, "source": str(args.input_gif), "metadata": inspect_gif(optimized)}
        write_json(args.output_dir / f"{args.base_name}-report.json", report)
        print(f"OK wrote optimize report {args.output_dir / f'{args.base_name}-report.json'}")
        return 0

    selected = args.preset if args.mode == "marketing" else args.preset
    gif_path = args.output_dir / f"{args.base_name}.gif"
    report_path = args.output_dir / f"{args.base_name}.json"
    result = render_one(images, args.text, gif_path, report_path, selected, args.max_bytes)
    sheet_path = args.output_dir / f"{args.base_name}-sheet.png"
    make_sheet(Path(result["gif"]), sheet_path)
    final_report = {"mode": args.mode, **result, "contact_sheet": str(sheet_path)}
    write_json(args.output_dir / f"{args.base_name}-report.json", final_report)
    print(f"OK wrote final report {args.output_dir / f'{args.base_name}-report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
