from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageSequence
except ImportError as exc:  # pragma: no cover - exercised by real users without deps
    raise SystemExit(
        "Missing dependency: install Pillow with `python -m pip install -r "
        "skills/gif-director/requirements.txt`."
    ) from exc


def load_image(path: Path) -> Image.Image:
    image = Image.open(path)
    image = ImageOps.exif_transpose(image)
    return image.convert("RGBA")


def cover(image: Image.Image, width: int, height: int) -> Image.Image:
    src_w, src_h = image.size
    scale = max(width / src_w, height / src_h)
    resized = image.resize(
        (max(1, round(src_w * scale)), max(1, round(src_h * scale))),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def fit_contain(image: Image.Image, width: int, height: int, fill=(246, 244, 239, 255)) -> Image.Image:
    src_w, src_h = image.size
    scale = min(width / src_w, height / src_h)
    resized = image.resize(
        (max(1, round(src_w * scale)), max(1, round(src_h * scale))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", (width, height), fill)
    canvas.alpha_composite(resized, ((width - resized.width) // 2, (height - resized.height) // 2))
    return canvas


def ease_out_back(t: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def ease_in_out(t: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * t)


def find_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    windir = os.environ.get("WINDIR", r"C:\Windows")
    if bold:
        candidates.append(Path(windir) / "Fonts" / "malgunbd.ttf")
    candidates.extend(
        [
            Path(windir) / "Fonts" / "malgun.ttf",
            Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"),
            Path("/Library/Fonts/Arial Unicode.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
        ]
    )
    for font_path in candidates:
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size=size)
            except OSError:
                continue
    return ImageFont.load_default(size=size)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=0)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    text = " ".join(text.strip().split())
    if not text:
        return []
    has_spaces = " " in text
    units = text.split(" ") if has_spaces else list(text)
    lines: list[str] = []
    current = ""
    for unit in units:
        candidate = f"{current} {unit}".strip() if has_spaces else f"{current}{unit}"
        if current and text_size(draw, candidate, font)[0] > max_width:
            lines.append(current)
            current = unit
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def fit_caption(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
    start_size: int,
) -> tuple[ImageFont.ImageFont, list[str], int]:
    for size in range(start_size, 11, -2):
        font = find_font(size, bold=True)
        lines = wrap_text(draw, text, font, max_width)
        if not lines:
            return font, [], 0
        line_heights = [text_size(draw, line, font)[1] for line in lines]
        line_gap = max(3, size // 7)
        total_height = sum(line_heights) + line_gap * (len(lines) - 1)
        if total_height <= max_height:
            return font, lines, line_gap
    font = find_font(11, bold=True)
    return font, wrap_text(draw, text, font, max_width), 2


def draw_caption(
    image: Image.Image,
    text: str,
    progress: float,
    zone: str = "bottom",
) -> None:
    if not text:
        return
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = image.size
    margin = max(8, round(width * 0.06))
    box_width = width - margin * 2
    max_text_height = max(28, round(height * 0.3))
    font, lines, line_gap = fit_caption(draw, text, box_width - 18, max_text_height, max(18, width // 8))
    if not lines:
        return
    line_sizes = [text_size(draw, line, font) for line in lines]
    text_height = sum(h for _, h in line_sizes) + line_gap * (len(lines) - 1)
    box_height = text_height + 18
    if zone == "top":
        y = margin
    else:
        y = height - margin - box_height
    pop = max(0.0, min(1.0, progress))
    alpha = round(220 * pop)
    radius = max(6, width // 35)
    draw.rounded_rectangle(
        (margin, y, margin + box_width, y + box_height),
        radius=radius,
        fill=(255, 255, 255, alpha),
        outline=(24, 24, 24, round(230 * pop)),
        width=max(1, width // 120),
    )
    cursor_y = y + 9
    for line, (line_width, line_height) in zip(lines, line_sizes):
        x = margin + (box_width - line_width) // 2
        draw.text(
            (x, cursor_y),
            line,
            font=font,
            fill=(20, 20, 20, round(255 * pop)),
            stroke_width=max(1, width // 180),
            stroke_fill=(255, 255, 255, round(230 * pop)),
        )
        cursor_y += line_height + line_gap
    image.alpha_composite(overlay)


def inspect_gif(path: Path) -> dict:
    with Image.open(path) as image:
        frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(image)]
        durations = [int(frame.info.get("duration", image.info.get("duration", 0)) or 0) for frame in ImageSequence.Iterator(image)]
        if not durations and frames:
            durations = [0] * len(frames)
        unique_changes = 0
        blank_frames = 0
        previous = None
        for frame in frames:
            if frame.getbbox() is None:
                blank_frames += 1
            current_rgb = frame.convert("RGB")
            if previous is not None and ImageChops.difference(previous, current_rgb).getbbox() is not None:
                unique_changes += 1
            previous = current_rgb
        file_size = path.stat().st_size
        return {
            "format": "GIF",
            "path": str(path),
            "width": image.width,
            "height": image.height,
            "frame_count": len(frames),
            "duration_ms": sum(durations),
            "durations_ms": durations,
            "file_size_bytes": file_size,
            "blank_frames": blank_frames,
            "changed_transitions": unique_changes,
            "loop": image.info.get("loop", 0),
        }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_gif(frames: Iterable[Image.Image], output: Path, duration_ms: int) -> dict:
    prepared = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=256) for frame in frames]
    if not prepared:
        raise ValueError("No frames to save")
    output.parent.mkdir(parents=True, exist_ok=True)
    prepared[0].save(
        output,
        save_all=True,
        append_images=prepared[1:],
        duration=duration_ms,
        loop=0,
        optimize=False,
        disposal=2,
    )
    return inspect_gif(output)
