from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gif_utils import inspect_gif, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a visual/readback QA report for a generated GIF.")
    parser.add_argument("--gif", type=Path, required=True)
    parser.add_argument("--render-report", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-bytes", type=int, default=8_000_000)
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report(gif_path: Path, render_report: dict, plan: dict, max_bytes: int) -> dict:
    gif = inspect_gif(gif_path)
    caption_metrics = render_report.get("caption_metrics")
    issues = []
    if gif["frame_count"] < 2:
        issues.append("too few frames")
    if gif["duration_ms"] <= 0:
        issues.append("missing frame durations")
    if gif["file_size_bytes"] > max_bytes:
        issues.append("file too large")
    if gif["blank_frames"] >= gif["frame_count"]:
        issues.append("all frames are blank")
    if gif["changed_transitions"] == 0 and gif["frame_count"] > 1:
        issues.append("frames do not visibly change")
    if caption_metrics and caption_metrics.get("clipped"):
        issues.append("caption clipped")
    if plan.get("target") == "detail-page" and not render_report.get("caption"):
        issues.append("business caption missing")
    if plan.get("constraints", {}).get("no_video") is not True:
        issues.append("no-video constraint missing")

    return {
        "ok": not issues,
        "issues": issues,
        "target": plan.get("target"),
        "business_intent": plan.get("business_intent"),
        "motion_intensity": plan.get("motion", {}).get("intensity"),
        "caption": render_report.get("caption"),
        "caption_metrics": caption_metrics,
        "gif": gif,
    }


def main() -> int:
    args = parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    report = build_report(args.gif, read_json(args.render_report), read_json(args.plan), args.max_bytes)
    write_json(args.output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
