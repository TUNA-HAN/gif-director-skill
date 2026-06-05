from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path

from gif_utils import inspect_gif, load_image, save_gif, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate photoreal still-edit keyframes with OpenAI image editing, then encode them as a GIF.")
    parser.add_argument("--image", type=Path, required=True, help="Source image to upload as the visual reference.")
    parser.add_argument("--plan", type=Path, required=True, help="Planner JSON containing photoreal keyframes.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--base-name", default="photoreal-action")
    parser.add_argument("--model", default="gpt-image-1.5")
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--quality", default="high")
    parser.add_argument("--duration", type=float, default=1.8)
    parser.add_argument("--allow-upload", action="store_true", help="Required. Confirms the source image may be uploaded for AI still-image editing.")
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def response_image_bytes(response) -> bytes:
    for item in getattr(response, "data", []) or []:
        b64_json = getattr(item, "b64_json", None)
        if b64_json:
            return base64.b64decode(b64_json)
    raise RuntimeError("OpenAI image edit response did not include base64 image data.")


def make_upload_png(source: Path, output_dir: Path) -> Path:
    upload = output_dir / "_source-upload.png"
    load_image(source).convert("RGB").save(upload)
    return upload


def frame_prompt(plan: dict, frame: dict) -> str:
    must_not = ", ".join(plan.get("constraints", {}).get("must_not", []))
    return (
        "Edit the provided photo into one photorealistic still frame for a GIF keyframe sequence. "
        "Preserve the same father and daughter, the same identities, clothing, street background, lighting, camera angle, and realistic photo style. "
        "Do not add or duplicate people. Do not create an extra child, clone, ghost, second version of a person, cartoon overlay, speech bubble, or text. "
        "Use only natural facial expression and body-language changes to make the action readable. "
        f"Forbidden failure modes: {must_not}. "
        f"Frame {frame.get('index')}: {frame.get('prompt')}"
    )


def generate_frame(client, model: str, upload_image: Path, prompt: str, output: Path, size: str, quality: str) -> None:
    with upload_image.open("rb") as image_file:
        response = client.images.edit(
            model=model,
            image=[image_file],
            prompt=prompt,
            size=size,
            quality=quality,
            n=1,
        )
    output.write_bytes(response_image_bytes(response))


def main() -> int:
    args = parse_args()
    if not args.allow_upload:
        raise SystemExit("Refusing external upload. Re-run with --allow-upload only after explicit user consent.")
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set.")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("Install optional AI dependencies with `python -m pip install -r skills/gif-director/requirements-ai.txt`.") from exc

    plan = read_json(args.plan)
    if plan.get("visual_strategy") != "photoreal_still_edit_keyframes":
        raise SystemExit("Plan is not a photoreal still-edit keyframe plan.")
    keyframes = plan.get("keyframes") or []
    if not keyframes:
        raise SystemExit("Plan does not contain keyframes.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    upload_image = make_upload_png(args.image, args.output_dir)
    client = OpenAI()
    frame_paths = []
    prompts = []
    for frame in keyframes:
        output = args.output_dir / f"{args.base_name}-frame-{int(frame.get('index', len(frame_paths) + 1)):02d}.png"
        prompt = frame_prompt(plan, frame)
        generate_frame(client, args.model, upload_image, prompt, output, args.size, args.quality)
        frame_paths.append(output)
        prompts.append({"frame": frame.get("index"), "prompt": prompt, "output": str(output)})

    frames = [load_image(path).convert("RGB") for path in frame_paths]
    per_frame_ms = max(80, round(args.duration * 1000 / len(frames)))
    gif_path = args.output_dir / f"{args.base_name}.gif"
    gif_report = save_gif(frames, gif_path, per_frame_ms)
    gif_report.update(inspect_gif(gif_path))
    report = {
        "ok": True,
        "mode": "photoreal",
        "provider": "openai",
        "model": args.model,
        "source": str(args.image),
        "upload_image": str(upload_image),
        "plan": str(args.plan),
        "frames": [str(path) for path in frame_paths],
        "prompts": prompts,
        "gif": str(gif_path),
        "gif_metadata": gif_report,
        "qa_checklist": [
            "same two people only",
            "no duplicate subjects",
            "daughter rejection is readable",
            "father remains recognizable",
            "same background and lighting",
            "no cartoon/text overlay substitute",
            "no video/mp4 workflow",
        ],
    }
    write_json(args.output_dir / f"{args.base_name}-photoreal-report.json", report)
    print(f"OK wrote {gif_path} frames={gif_report['frame_count']} duration_ms={gif_report['duration_ms']} bytes={gif_report['file_size_bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
