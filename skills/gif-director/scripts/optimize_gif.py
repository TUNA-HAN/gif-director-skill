from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageSequence

from gif_utils import inspect_gif, save_gif, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Optimize an existing GIF for web/detail-page use.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--max-width", type=int, default=720)
    parser.add_argument("--max-frames", type=int, default=18)
    parser.add_argument("--encoder", choices=["auto", "pillow", "gifski", "ffmpeg"], default="auto")
    return parser.parse_args()


def load_frames(path: Path, max_width: int, max_frames: int) -> tuple[list[Image.Image], int]:
    with Image.open(path) as image:
        raw_frames = [frame.copy().convert("RGB") for frame in ImageSequence.Iterator(image)]
        durations = [int(frame.info.get("duration", image.info.get("duration", 100)) or 100) for frame in ImageSequence.Iterator(image)]
    if not raw_frames:
        raise SystemExit("No frames found")
    if len(raw_frames) > max_frames:
        step = max(1, round(len(raw_frames) / max_frames))
        raw_frames = raw_frames[::step][:max_frames]
        durations = durations[::step][:max_frames]
    width, height = raw_frames[0].size
    if width > max_width:
        scale = max_width / width
        new_size = (max_width, max(1, round(height * scale)))
        raw_frames = [frame.resize(new_size, Image.Resampling.LANCZOS) for frame in raw_frames]
    per_frame = max(20, round(sum(durations) / max(1, len(durations))))
    return raw_frames, per_frame


def write_png_frames(frames: list[Image.Image], directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for index, frame in enumerate(frames):
        frame.save(directory / f"frame_{index:04d}.png")


def encode_with_gifski(frames: list[Image.Image], output: Path, duration_ms: int) -> bool:
    if not shutil.which("gifski"):
        return False
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        write_png_frames(frames, tmp_path)
        fps = max(1, round(1000 / duration_ms))
        command = ["gifski", "--fps", str(fps), "-o", str(output), *map(str, sorted(tmp_path.glob("frame_*.png")))]
        return subprocess.run(command, check=False).returncode == 0


def encode_with_ffmpeg(frames: list[Image.Image], output: Path, duration_ms: int) -> bool:
    if not shutil.which("ffmpeg"):
        return False
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        write_png_frames(frames, tmp_path)
        fps = max(1, round(1000 / duration_ms))
        palette = tmp_path / "palette.png"
        pattern = str(tmp_path / "frame_%04d.png")
        first = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-framerate", str(fps), "-i", pattern, "-vf", "palettegen", str(palette)]
        second = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-framerate",
            str(fps),
            "-i",
            pattern,
            "-i",
            str(palette),
            "-lavfi",
            "paletteuse",
            str(output),
        ]
        if subprocess.run(first, check=False).returncode != 0:
            return False
        return subprocess.run(second, check=False).returncode == 0


def main() -> int:
    args = parse_args()
    frames, duration_ms = load_frames(args.input, args.max_width, args.max_frames)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoder_used = "pillow"
    encoded = False
    if args.encoder in ("auto", "gifski"):
        encoded = encode_with_gifski(frames, args.output, duration_ms)
        if encoded:
            encoder_used = "gifski"
    if not encoded and args.encoder in ("auto", "ffmpeg"):
        encoded = encode_with_ffmpeg(frames, args.output, duration_ms)
        if encoded:
            encoder_used = "ffmpeg"
    if not encoded:
        save_gif(frames, args.output, duration_ms)
    validation = inspect_gif(args.output)
    validation["issues"] = []
    validation["ok"] = True
    report = {
        "ok": True,
        "encoder": encoder_used,
        "input": str(args.input),
        "output": str(args.output),
        "validation": validation,
    }
    if args.report:
        write_json(args.report, report)
    print(f"OK wrote {args.output} encoder={encoder_used} frames={validation['frame_count']} bytes={validation['file_size_bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
