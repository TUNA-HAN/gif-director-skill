from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw

from gif_utils import cover, draw_caption, ease_in_out, ease_out_back, fit_contain, inspect_gif, load_image, save_gif, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a local image and caption into an animated GIF.")
    parser.add_argument("--image", type=Path, action="append", required=True, help="Input image path. Repeat for multi-image sequences.")
    parser.add_argument("--text", default="", help="Caption text. Korean and CJK text are supported when system fonts exist.")
    parser.add_argument("--output", type=Path, required=True, help="Output GIF path.")
    parser.add_argument("--report", type=Path, help="Optional JSON report path.")
    parser.add_argument(
        "--preset",
        default="caption-pop",
        choices=[
            "caption-pop",
            "gentle-zoom",
            "shake",
            "bounce",
            "polaroid",
            "pulse",
            "spin",
            "slide",
            "wiggle",
            "explode",
            "detail-page",
        ],
    )
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--duration", type=float, default=1.8, help="Duration in seconds.")
    parser.add_argument("--fps", type=int, default=10)
    parser.add_argument("--caption-zone", default="bottom", choices=["top", "bottom"])
    return parser.parse_args()


def pick_source(sources: list[Image.Image], t: float) -> Image.Image:
    if len(sources) == 1:
        return sources[0]
    scaled = min(0.999, max(0.0, t)) * len(sources)
    return sources[min(len(sources) - 1, int(scaled))]


def draw_burst(frame: Image.Image, t: float) -> None:
    draw = ImageDraw.Draw(frame)
    width, height = frame.size
    cx, cy = width // 2, height // 2
    radius = int(max(width, height) * (0.25 + 0.55 * ease_in_out(t)))
    color = (255, 222, 75, 150)
    for index in range(18):
        angle = (index / 18) * math.tau + t * 0.8
        inner = int(radius * 0.42)
        x1 = cx + int(math.cos(angle) * inner)
        y1 = cy + int(math.sin(angle) * inner)
        x2 = cx + int(math.cos(angle) * radius)
        y2 = cy + int(math.sin(angle) * radius)
        draw.line((x1, y1, x2, y2), fill=color, width=max(2, width // 90))


def make_marketing_frame(source: Image.Image, width: int, height: int, t: float) -> Image.Image:
    frame = Image.new("RGBA", (width, height), (248, 249, 250, 255))
    hero_w = round(width * 0.58)
    hero = cover(source, hero_w, height)
    slide = round((1 - ease_out_back(min(1, t * 1.4))) * -hero_w * 0.18)
    frame.alpha_composite(hero, (slide, 0))
    panel_x = round(width * 0.55)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(
        (panel_x, round(height * 0.12), width - round(width * 0.04), round(height * 0.88)),
        radius=max(8, width // 45),
        fill=(255, 255, 255, 235),
        outline=(20, 20, 20, 180),
        width=max(1, width // 180),
    )
    progress = ease_in_out(t)
    bar_w = round((width - panel_x - round(width * 0.12)) * progress)
    draw.rounded_rectangle(
        (panel_x + round(width * 0.04), round(height * 0.73), panel_x + round(width * 0.04) + bar_w, round(height * 0.77)),
        radius=max(2, width // 180),
        fill=(249, 115, 22, 230),
    )
    frame.alpha_composite(overlay)
    return frame


def transform_frame(sources: list[Image.Image], preset: str, width: int, height: int, t: float):
    source = pick_source(sources, t)
    if preset == "detail-page":
        return make_marketing_frame(source, width, height, t)

    if preset == "polaroid":
        background = fit_contain(source, width, height)
        card_w = round(width * 0.76)
        card_h = round(height * 0.72)
        photo = cover(source, card_w, round(card_h * 0.76))
        frame = background.copy()
        frame = frame.point(lambda value: round(value * 0.65 + 245 * 0.35))
        card = fit_contain(photo, card_w, card_h, fill=(255, 255, 255, 255))
        angle = -3 + 6 * ease_in_out(t)
        card = card.rotate(angle, expand=True, resample=2, fillcolor=(0, 0, 0, 0))
        frame.alpha_composite(card, ((width - card.width) // 2, (height - card.height) // 2))
        return frame

    zoom = 1.0
    dx = dy = 0
    angle = 0.0
    if preset == "gentle-zoom":
        zoom = 1.0 + 0.055 * ease_in_out(t)
    elif preset == "shake":
        dx = round(math.sin(t * math.pi * 6) * width * 0.018)
        dy = round(math.cos(t * math.pi * 8) * height * 0.01)
        zoom = 1.035
    elif preset == "bounce":
        dy = round(-math.sin(t * math.pi) * height * 0.06)
        zoom = 1.0 + 0.035 * math.sin(t * math.pi)
    elif preset == "pulse":
        zoom = 1.0 + 0.06 * math.sin(t * math.pi)
    elif preset == "spin":
        angle = 360 * t
        zoom = 0.9
    elif preset == "slide":
        dx = round((1 - ease_out_back(t)) * width * 0.22)
        zoom = 1.03
    elif preset == "wiggle":
        angle = math.sin(t * math.pi * 8) * 5
        dx = round(math.sin(t * math.pi * 10) * width * 0.01)
        zoom = 1.03
    elif preset == "explode":
        zoom = 0.82 + 0.25 * ease_out_back(min(1, t * 1.2))
    else:
        zoom = 1.0 + 0.025 * ease_in_out(t)

    scaled_w = max(width, round(width * zoom))
    scaled_h = max(height, round(height * zoom))
    base = cover(source, scaled_w, scaled_h)
    if angle:
        base = base.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC, fillcolor=(255, 255, 255, 0))
        base = cover(base, scaled_w, scaled_h)
    left = (scaled_w - width) // 2 - dx
    top = (scaled_h - height) // 2 - dy
    left = max(0, min(left, scaled_w - width))
    top = max(0, min(top, scaled_h - height))
    frame = base.crop((left, top, left + width, top + height))
    if preset == "explode":
        draw_burst(frame, t)
    return frame


def main() -> int:
    args = parse_args()
    if args.width <= 0 or args.height <= 0:
        raise SystemExit("--width and --height must be positive")
    frame_count = max(8, round(args.duration * args.fps))
    per_frame_ms = max(20, round(args.duration * 1000 / frame_count))
    sources = [load_image(path) for path in args.image]
    frames = []
    for index in range(frame_count):
        t = index / max(1, frame_count - 1)
        frame = transform_frame(sources, args.preset, args.width, args.height, t).convert("RGBA")
        caption_start = 0.18 if args.preset != "caption-pop" else 0.35
        progress = 0 if t < caption_start else ease_out_back((t - caption_start) / max(0.01, 1 - caption_start))
        draw_caption(frame, args.text, min(1, progress), zone=args.caption_zone)
        frames.append(frame.convert("RGB"))
    report = save_gif(frames, args.output, per_frame_ms)
    report.update({"preset": args.preset, "sources": [str(path) for path in args.image], "ok": True})
    # Re-read after writing; do not trust encoder inputs.
    report.update(inspect_gif(args.output))
    if args.report:
        write_json(args.report, report)
    print(f"OK wrote {args.output} frames={report['frame_count']} duration_ms={report['duration_ms']} bytes={report['file_size_bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
