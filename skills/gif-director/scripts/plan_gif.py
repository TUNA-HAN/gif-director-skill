from __future__ import annotations

import argparse
import json
import re
import sys


def has_any(text: str, words: list[str]) -> bool:
    return any(word in text for word in words)


def extract_caption(text: str) -> str:
    quoted = re.findall(r"[\"'“”‘’](.+?)[\"'“”‘’]", text)
    if quoted:
        return quoted[0].strip()
    priority_phrases = [
        "런칭 특가",
        "혜택 강조",
        "완전 추천",
        "좋아요",
        "확인했어요",
        "잠깐만요",
        "퇴근하고 싶다",
    ]
    for phrase in priority_phrases:
        if phrase in text:
            return phrase
    if has_any(text, ["런칭", "특가"]):
        return "런칭 특가"
    if has_any(text, ["혜택", "할인"]):
        return "혜택 강조"
    if has_any(text, ["추천", "좋아"]):
        return "완전 추천"
    return ""


def plan_prompt(prompt: str, has_reference: bool = False) -> dict:
    text = " ".join(prompt.lower().split())
    raw = prompt.strip()

    plan = {
        "mode": "quick",
        "target": "chat",
        "preset": "caption-pop",
        "caption": extract_caption(raw),
        "width": 512,
        "height": 512,
        "duration": 1.6,
        "fps": 10,
        "frame_count": 12,
        "count": 1,
        "max_width": 720,
        "max_frames": 14,
        "needs_reference_analysis": False,
        "quality_flags": ["readback-validation", "contact-sheet"],
        "rationale": [],
    }

    subtle = has_any(text, ["고급", "깔끔", "프리미엄", "차분", "담백", "정신없지 않", "너무 과하지"])
    energetic = has_any(text, ["런칭", "특가", "혜택", "할인", "이벤트", "강조", "임팩트"])

    if has_reference and has_any(text, ["이런 느낌", "따라", "참고", "비슷하게", "레퍼런스"]):
        plan.update({"mode": "reference", "needs_reference_analysis": True})
        plan["rationale"].append("reference-style request")

    if has_any(text, ["상세페이지", "상세", "마케팅", "배너", "광고", "상품페이지", "제품"]):
        plan.update({"mode": "marketing", "target": "detail-page", "preset": "detail-page", "width": 900, "height": 506, "duration": 2.0, "frame_count": 16})
        plan["quality_flags"].append("business-facing")
        plan["rationale"].append("marketing/detail-page target")

    if has_any(text, ["팩", "세트", "여러", "네 개", "4개", "감정", "리액션팩"]):
        plan.update({"mode": "pack", "target": "sticker-pack", "preset": "bounce", "width": 512, "height": 512, "count": 4})
        plan["rationale"].append("multi-output pack request")

    if has_any(text, ["캐릭터처럼", "스프라이트", "16프레임", "16 프레임", "움직이는 캐릭터", "캐릭터화"]):
        plan.update({"mode": "sprite", "target": "sprite-gif", "preset": "sprite", "width": 512, "height": 512, "frame_count": 16, "duration": 1.6})
        plan["rationale"].append("sprite motion request")

    if has_any(text, ["용량", "줄여", "최적화", "가볍게", "삽입할 수 있게", "압축"]):
        plan.update({"mode": "optimize", "target": "lightweight-web", "preset": "optimize", "max_width": 720, "max_frames": 14})
        plan["quality_flags"].append("size-budget")
        plan["rationale"].append("optimization request")

    if has_any(text, ["카톡", "채팅", "친구", "짤", "움짤", "스티커"]):
        if plan["mode"] == "quick":
            plan.update({"target": "sticker" if "스티커" in text else "chat"})
        plan["quality_flags"].append("caption-readability")

    if subtle:
        plan["quality_flags"].append("avoid-chaotic-motion")
        if plan["mode"] == "quick":
            plan["preset"] = "gentle-zoom"
        elif plan["mode"] == "marketing":
            plan["preset"] = "detail-page"
        plan["rationale"].append("subtle/premium tone")
    elif energetic and plan["mode"] == "quick":
        plan["preset"] = "pulse"
        plan["rationale"].append("energetic emphasis")

    if not plan["caption"] and plan["mode"] in {"marketing", "quick"}:
        if energetic:
            plan["caption"] = "혜택 강조"
        elif plan["target"] == "chat":
            plan["caption"] = "좋아요"

    return plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan GIF mode, preset, canvas, caption, and QA from a natural language prompt.")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--has-reference", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(plan_prompt(args.prompt, has_reference=args.has_reference), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
