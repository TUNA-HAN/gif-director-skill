from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageSequence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a PNG contact sheet from GIF frames.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--columns", type=int, default=5)
    parser.add_argument("--max-frames", type=int, default=24)
    parser.add_argument("--thumb-width", type=int, default=160)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.columns <= 0:
        raise SystemExit("--columns must be positive")
    with Image.open(args.input) as image:
        frames = [frame.copy().convert("RGB") for frame in ImageSequence.Iterator(image)]
    if not frames:
        raise SystemExit("No frames found")
    if len(frames) > args.max_frames:
        step = max(1, math.floor(len(frames) / args.max_frames))
        frames = frames[::step][: args.max_frames]
    thumb_w = args.thumb_width
    thumb_h = round(thumb_w * frames[0].height / frames[0].width)
    label_h = 18
    rows = math.ceil(len(frames) / args.columns)
    sheet = Image.new("RGB", (args.columns * thumb_w, rows * (thumb_h + label_h)), (245, 245, 245))
    draw = ImageDraw.Draw(sheet)
    for index, frame in enumerate(frames):
        thumb = frame.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % args.columns) * thumb_w
        y = (index // args.columns) * (thumb_h + label_h)
        sheet.paste(thumb, (x, y))
        draw.text((x + 4, y + thumb_h + 2), f"frame {index}", fill=(30, 30, 30))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)
    print(f"OK wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
