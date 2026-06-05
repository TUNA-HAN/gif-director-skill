from __future__ import annotations

import argparse
import json
from pathlib import Path

from gif_utils import inspect_gif


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a rendered GIF by reading back the saved file.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--min-frames", type=int, default=2)
    parser.add_argument("--max-bytes", type=int, default=8_000_000)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    issues = []
    if not args.input.exists():
        result = {"ok": False, "issues": [f"missing file: {args.input}"]}
        print(json.dumps(result, ensure_ascii=False))
        return 1
    result = inspect_gif(args.input)
    if result["frame_count"] < args.min_frames:
        issues.append("too few frames")
    if result["duration_ms"] <= 0:
        issues.append("missing frame durations")
    if result["file_size_bytes"] > args.max_bytes:
        issues.append("file too large")
    if result["blank_frames"] >= result["frame_count"]:
        issues.append("all frames are blank")
    if result["changed_transitions"] == 0 and result["frame_count"] > 1:
        issues.append("frames do not visibly change")
    result["issues"] = issues
    result["ok"] = not issues
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        status = "OK" if result["ok"] else "FAIL"
        print(f"{status} frames={result['frame_count']} duration_ms={result['duration_ms']} bytes={result['file_size_bytes']}")
        for issue in issues:
            print(f"- {issue}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
