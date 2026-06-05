from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageSequence

from gif_utils import inspect_gif, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a reference GIF and emit a compact style recipe.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, help="Write analysis JSON.")
    return parser.parse_args()


def average_color(frame: Image.Image) -> tuple[int, int, int]:
    thumb = frame.convert("RGB").resize((1, 1))
    return tuple(int(v) for v in thumb.getpixel((0, 0)))


def motion_score(path: Path) -> float:
    with Image.open(path) as image:
        previous = None
        scores = []
        for frame in ImageSequence.Iterator(image):
            current = frame.convert("RGBA")
            if previous is not None:
                diff = ImageChops.difference(previous.convert("RGB"), current.convert("RGB")).convert("L")
                scores.append(sum(diff.resize((16, 16)).getdata()) / (16 * 16 * 255))
            previous = current
    return round(sum(scores) / len(scores), 4) if scores else 0.0


def infer_recipe(meta: dict, motion: float) -> dict:
    if motion < 0.015:
        preset = "caption-pop"
    elif motion < 0.08:
        preset = "gentle-zoom"
    else:
        preset = "shake"
    aspect = round(meta["width"] / meta["height"], 3) if meta["height"] else 1
    return {
        "preset": preset,
        "canvas": {"width": meta["width"], "height": meta["height"], "aspect": aspect},
        "timing": {"duration_ms": meta["duration_ms"], "frame_count": meta["frame_count"]},
        "caption_zone": "bottom",
        "loop": "seamless" if meta["changed_transitions"] > 0 else "static-emphasis",
    }


def main() -> int:
    args = parse_args()
    meta = inspect_gif(args.input)
    with Image.open(args.input) as image:
        first = next(ImageSequence.Iterator(image)).convert("RGBA")
        color = average_color(first)
    motion = motion_score(args.input)
    result = {
        **meta,
        "average_first_frame_rgb": color,
        "motion_score": motion,
        "style_recipe": infer_recipe(meta, motion),
    }
    if args.json_output:
        write_json(args.json_output, result)
        print(f"OK wrote {args.json_output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
