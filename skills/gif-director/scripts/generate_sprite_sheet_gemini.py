from __future__ import annotations

import argparse
import os
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Optionally generate a still-image sprite sheet with Gemini image generation.")
    parser.add_argument("--image", type=Path, required=True, help="Source image to upload.")
    parser.add_argument("--output", type=Path, required=True, help="Output sprite sheet PNG.")
    parser.add_argument("--style", default="clean marketing sticker character")
    parser.add_argument("--model", default="gemini-3.1-flash-image")
    parser.add_argument("--allow-upload", action="store_true", help="Required. Confirms the source image may be uploaded.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.allow_upload:
        raise SystemExit("Refusing external upload. Re-run with --allow-upload only after user consent.")
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit("GEMINI_API_KEY is not set.")
    try:
        from google import genai
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Install optional AI dependencies with `python -m pip install -r skills/gif-director/requirements-ai.txt`.") from exc

    prompt = (
        "Create a 4x4 sprite sheet with 16 evenly spaced frames from the provided image. "
        "The subject should stay recognizable, no text, transparent or plain light background, "
        f"style: {args.style}. Each cell must show a small motion variation suitable for a looping GIF."
    )
    client = genai.Client()
    source = Image.open(args.image)
    response = client.models.generate_content(model=args.model, contents=[prompt, source])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for part in response.parts:
        if part.inline_data is not None:
            part.as_image().save(args.output)
            print(f"OK wrote {args.output}")
            return 0
    raise SystemExit("Gemini response did not include an image.")


if __name__ == "__main__":
    raise SystemExit(main())
