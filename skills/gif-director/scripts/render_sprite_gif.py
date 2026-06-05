from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image

from gif_utils import cover, draw_caption, ease_in_out, inspect_gif, load_image, save_gif, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render an image or a 4x4 sprite sheet into a GIF.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--sprite-sheet", type=Path, help="Existing sprite sheet image.")
    source.add_argument("--image", type=Path, help="Still image to animate deterministically.")
    parser.add_argument("--text", default="", help="Optional caption.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--cell-columns", type=int, default=4)
    parser.add_argument("--cell-rows", type=int, default=4)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--duration", type=float, default=1.6)
    return parser.parse_args()


def extract_sprite_frames(sheet_path: Path, columns: int, rows: int, width: int, height: int) -> list[Image.Image]:
    sheet = load_image(sheet_path)
    cell_w = sheet.width // columns
    cell_h = sheet.height // rows
    frames = []
    for row in range(rows):
        for col in range(columns):
            cell = sheet.crop((col * cell_w, row * cell_h, (col + 1) * cell_w, (row + 1) * cell_h))
            frames.append(cover(cell, width, height).convert("RGBA"))
    return frames


def animate_still(image_path: Path, width: int, height: int) -> list[Image.Image]:
    source = load_image(image_path)
    frames = []
    for index in range(16):
        t = index / 15
        zoom = 0.96 + 0.08 * math.sin(math.pi * t)
        dx = round(math.sin(math.tau * t) * width * 0.018)
        dy = round(math.sin(math.tau * t + math.pi / 2) * height * 0.012)
        angle = math.sin(math.tau * t) * 3.5
        base = cover(source, round(width * zoom), round(height * zoom))
        base = base.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC, fillcolor=(255, 255, 255, 0))
        frame = cover(base, width, height)
        canvas = Image.new("RGBA", (width, height), (255, 255, 255, 255))
        canvas.alpha_composite(frame, (dx, dy))
        frames.append(canvas)
    return frames


def main() -> int:
    args = parse_args()
    if args.cell_columns <= 0 or args.cell_rows <= 0:
        raise SystemExit("cell columns/rows must be positive")
    if args.sprite_sheet:
        frames = extract_sprite_frames(args.sprite_sheet, args.cell_columns, args.cell_rows, args.width, args.height)
        source = str(args.sprite_sheet)
        mode = "sprite-sheet"
    else:
        frames = animate_still(args.image, args.width, args.height)
        source = str(args.image)
        mode = "still-image"
    if args.text:
        for index, frame in enumerate(frames):
            progress = ease_in_out(index / max(1, len(frames) - 1))
            draw_caption(frame, args.text, progress, zone="bottom")
    per_frame_ms = max(20, round(args.duration * 1000 / len(frames)))
    report = save_gif([frame.convert("RGB") for frame in frames], args.output, per_frame_ms)
    report.update({"ok": True, "mode": mode, "source": source})
    report.update(inspect_gif(args.output))
    if args.report:
        write_json(args.report, report)
    print(f"OK wrote {args.output} frames={report['frame_count']} duration_ms={report['duration_ms']} bytes={report['file_size_bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
