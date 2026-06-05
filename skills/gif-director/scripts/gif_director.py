from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from gif_utils import inspect_gif, write_json
from plan_gif import plan_prompt


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
    parser.add_argument("--mode", choices=["quick", "pack", "marketing", "optimize", "sprite"], default="quick")
    parser.add_argument("--prompt", help="Natural language request. Used to infer mode, preset, caption, and target.")
    parser.add_argument("--image", type=Path, action="append", help="Input image. Repeat for multi-image GIFs.")
    parser.add_argument("--input-gif", type=Path, help="Existing GIF for optimize mode.")
    parser.add_argument("--reference-gif", type=Path, help="Reference GIF for style planning.")
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


def caption_text(plan: dict | None) -> str:
    if not plan:
        return ""
    caption = plan.get("caption", "")
    if isinstance(caption, dict):
        return caption.get("text", "")
    return str(caption)


def render_options(plan: dict | None) -> dict:
    if not plan:
        return {}
    return {
        "width": plan.get("layout", {}).get("width", plan.get("width")),
        "height": plan.get("layout", {}).get("height", plan.get("height")),
        "duration": plan.get("motion", {}).get("duration", plan.get("duration")),
        "fps": plan.get("motion", {}).get("fps", plan.get("fps")),
        "caption_zone": plan.get("layout", {}).get("caption_zone", "bottom"),
    }


def analyze_reference(reference_gif: Path, output: Path) -> dict:
    run_python([str(SCRIPT_DIR / "analyze_reference_gif.py"), "--input", str(reference_gif), "--json-output", str(output)])
    return json.loads(output.read_text(encoding="utf-8"))


def apply_reference_recipe(plan: dict, reference_analysis: dict) -> None:
    recipe = reference_analysis.get("style_recipe", {})
    if not recipe:
        return
    plan["preset"] = recipe.get("preset", plan.get("preset", "caption-pop"))
    plan.setdefault("motion", {})["preset"] = plan["preset"]
    timing = recipe.get("timing", {})
    if timing.get("duration_ms"):
        plan["motion"]["duration"] = max(0.4, timing["duration_ms"] / 1000)
    if timing.get("frame_count"):
        plan["motion"]["frame_count"] = timing["frame_count"]
    canvas = recipe.get("canvas", {})
    if canvas.get("width") and canvas.get("height"):
        plan.setdefault("layout", {})["width"] = canvas["width"]
        plan["layout"]["height"] = canvas["height"]
    if recipe.get("caption_zone"):
        plan.setdefault("layout", {})["caption_zone"] = recipe["caption_zone"]


def render_one(
    images: list[Path],
    text: str,
    output: Path,
    report: Path,
    preset_name: str,
    max_bytes: int,
    width: int | None = None,
    height: int | None = None,
    duration: float | None = None,
    fps: int | None = None,
    caption_zone: str = "bottom",
) -> dict:
    default_width, default_height, render_preset, default_duration = preset_details(preset_name)
    width = width or default_width
    height = height or default_height
    duration = duration or default_duration
    fps = fps or 10
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
            "--fps",
            str(fps),
            "--caption-zone",
            caption_zone,
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
                "--caption-zone",
                caption_zone,
            ]
        )
        run_python(args)
        output = repaired
        report = repair_report
        validation = validate(output, max_bytes=max_bytes)
    return {"gif": str(output), "report": str(report), "validation": validation}


def render_sprite(images: list[Path], text: str, output: Path, report: Path, plan: dict | None, max_bytes: int) -> dict:
    options = render_options(plan)
    args = [
        str(SCRIPT_DIR / "render_sprite_gif.py"),
        "--image",
        str(images[0]),
        "--text",
        text,
        "--output",
        str(output),
        "--report",
        str(report),
        "--width",
        str(options.get("width") or 512),
        "--height",
        str(options.get("height") or 512),
        "--duration",
        str(options.get("duration") or 1.6),
    ]
    run_python(args)
    return {"gif": str(output), "report": str(report), "validation": validate(output, max_bytes=max_bytes)}


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
        return json.loads(result.stdout)
    return {"ok": False, "issues": [result.stderr.strip() or "validation failed"]}


def make_sheet(gif_path: Path, sheet_path: Path) -> None:
    run_python([str(SCRIPT_DIR / "make_contact_sheet.py"), "--input", str(gif_path), "--output", str(sheet_path), "--columns", "4"])


def make_qa(gif_path: Path, render_report: Path, plan_path: Path, qa_path: Path, max_bytes: int) -> dict:
    run_python(
        [
            str(SCRIPT_DIR / "qa_report.py"),
            "--gif",
            str(gif_path),
            "--render-report",
            str(render_report),
            "--plan",
            str(plan_path),
            "--output",
            str(qa_path),
            "--max-bytes",
            str(max_bytes),
        ]
    )
    return json.loads(qa_path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    plan = plan_prompt(args.prompt, has_reference=bool(args.reference_gif)) if args.prompt else None
    plan_path = None
    reference_analysis = None
    if plan and args.reference_gif:
        reference_path = args.output_dir / f"{args.base_name}-reference.json"
        reference_analysis = analyze_reference(args.reference_gif, reference_path)
        if plan.get("needs_reference_analysis"):
            apply_reference_recipe(plan, reference_analysis)
    if plan:
        plan_path = args.output_dir / f"{args.base_name}-plan.json"
        write_json(plan_path, plan)
        args.mode = "quick" if plan["mode"] == "reference" else plan["mode"]
        if not args.text:
            args.text = caption_text(plan)
        if args.preset == "chat":
            args.preset = plan.get("target", "chat") if plan["mode"] == "marketing" else plan.get("preset", args.preset)
        if plan["mode"] == "optimize":
            args.max_width = plan.get("max_width", args.max_width)
            args.max_frames = plan.get("max_frames", args.max_frames)
    images = args.image or []
    if args.mode != "optimize" and not images:
        raise SystemExit("--image is required unless --mode optimize")

    if args.mode == "pack":
        outputs = []
        for suffix, caption, preset in PACK_DEFAULTS:
            gif_path = args.output_dir / f"{args.base_name}-{suffix}.gif"
            report_path = args.output_dir / f"{args.base_name}-{suffix}.json"
            outputs.append(render_one(images, caption, gif_path, report_path, preset, args.max_bytes))
        pack_report = {"mode": "pack", "plan": plan, "plan_path": str(plan_path) if plan_path else None, "outputs": outputs}
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
        report = {
            "mode": "optimize",
            "plan": plan,
            "plan_path": str(plan_path) if plan_path else None,
            "gif": str(optimized),
            "report": str(optimize_report),
            "validation": validation,
            "source": str(args.input_gif),
            "metadata": inspect_gif(optimized),
        }
        write_json(args.output_dir / f"{args.base_name}-report.json", report)
        print(f"OK wrote optimize report {args.output_dir / f'{args.base_name}-report.json'}")
        return 0

    gif_path = args.output_dir / f"{args.base_name}.gif"
    report_path = args.output_dir / f"{args.base_name}.json"
    options = render_options(plan)
    if args.mode == "sprite":
        result = render_sprite(images, args.text, gif_path, report_path, plan, args.max_bytes)
    else:
        result = render_one(images, args.text, gif_path, report_path, args.preset, args.max_bytes, **options)
    sheet_path = args.output_dir / f"{args.base_name}-sheet.png"
    make_sheet(Path(result["gif"]), sheet_path)
    qa_path = None
    qa = None
    if plan_path:
        qa_path = args.output_dir / f"{args.base_name}-qa.json"
        qa = make_qa(Path(result["gif"]), Path(result["report"]), plan_path, qa_path, args.max_bytes)
    final_report = {
        "mode": plan.get("mode", args.mode) if plan else args.mode,
        "plan": plan,
        "plan_path": str(plan_path) if plan_path else None,
        **result,
        "contact_sheet": str(sheet_path),
        "qa_report": str(qa_path) if qa_path else None,
        "qa": qa,
        "reference_analysis": reference_analysis,
    }
    write_json(args.output_dir / f"{args.base_name}-report.json", final_report)
    print(f"OK wrote final report {args.output_dir / f'{args.base_name}-report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
