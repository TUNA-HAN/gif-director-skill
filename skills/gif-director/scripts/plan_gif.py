from __future__ import annotations

import argparse
import json
import re
import sys

from planner_rules import (
    BUSINESS_INTENTS,
    CAPTION_ROLES,
    DEFAULT_CAPTIONS,
    MARKETING_HINTS,
    OPTIMIZE_HINTS,
    PACK_HINTS,
    REFERENCE_HINTS,
    SPRITE_HINTS,
    TARGET_HINTS,
    TONE_HINTS,
)


def has_any(text: str, words: list[str]) -> bool:
    return any(word.lower() in text for word in words)


def count_hits(text: str, words: list[str]) -> int:
    return sum(1 for word in words if word.lower() in text)


def extract_caption(prompt: str, business_intent: str = "unknown") -> str:
    raw = prompt.strip()
    quoted = re.findall(r'"([^"]+)"|\'([^\']+)\'|"([^"]+)"|"([^"]+)"', raw)
    for groups in quoted:
        value = next((group for group in groups if group), "")
        if value.strip():
            return value.strip()

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
        if phrase in raw:
            return phrase

    label_match = re.search(r"(?:문구|텍스트|자막|카피|글자|멘트)\s*(?:는|은|로|:|=)?\s*([^.,\n]+)", raw)
    if label_match:
        caption = label_match.group(1).strip()
        caption = re.sub(r"\s*(?:문구|텍스트|자막|카피|글자|멘트)\s*(?:넣.*|보이.*)?$", "", caption).strip()
        if caption:
            return caption

    return DEFAULT_CAPTIONS.get(business_intent, "")


def infer_business_intent(text: str) -> str:
    if has_any(text, ["리액션팩", "감정 스티커", "네 개", "4개"]) and has_any(text, ["카톡", "친구", "스티커", "팩"]):
        return "reaction_pack"
    if has_any(text, ["마감", "임박", "한정", "cta"]) and not has_any(text, ["할인", "혜택", "특가", "런칭", "쿠폰"]):
        return "urgency"
    if has_any(text, BUSINESS_INTENTS["launch_offer"]):
        return "launch_offer"
    if has_any(text, BUSINESS_INTENTS["review_trust"]):
        return "review_trust"
    if has_any(text, BUSINESS_INTENTS["social_proof"]):
        return "social_proof"
    if has_any(text, BUSINESS_INTENTS["urgency"]):
        return "urgency"
    if has_any(text, BUSINESS_INTENTS["product_demo"]):
        return "product_demo"
    if has_any(text, BUSINESS_INTENTS["feature_highlight"]):
        return "feature_highlight"
    return "unknown"


def infer_target(text: str, mode: str, business_intent: str) -> str:
    if mode == "optimize":
        return "lightweight-web"
    if mode == "sprite":
        return "sprite-gif"
    if mode == "pack":
        return "sticker-pack"
    if has_any(text, TARGET_HINTS["ad-banner"]):
        return "ad-banner"
    if has_any(text, TARGET_HINTS["detail-page"]):
        return "detail-page"
    if has_any(text, TARGET_HINTS["sticker"]):
        return "sticker"
    if business_intent not in {"unknown", "reaction_pack"} and has_any(text, MARKETING_HINTS):
        return "detail-page"
    return "chat"


def infer_mode(text: str, has_reference: bool, business_intent: str) -> str:
    if has_reference and has_any(text, REFERENCE_HINTS):
        return "reference"
    if has_any(text, OPTIMIZE_HINTS) and has_any(text, ["gif", "움짤", "기존", "이미 만든"]):
        return "optimize"
    if has_any(text, SPRITE_HINTS):
        return "sprite"
    if business_intent == "reaction_pack" and has_any(text, PACK_HINTS):
        return "pack"
    if has_any(text, TARGET_HINTS["ad-banner"]) or has_any(text, TARGET_HINTS["detail-page"]):
        return "marketing"
    if business_intent not in {"unknown", "reaction_pack", "feature_highlight"} and has_any(text, MARKETING_HINTS):
        return "marketing"
    if business_intent == "feature_highlight" and has_any(text, ["제품", "상품", "상세", "제품페이지", "상품페이지", "상세페이지"]):
        return "marketing"
    return "quick"


def infer_motion_intensity(text: str, mode: str, business_intent: str) -> str:
    if mode == "reference":
        return "reference"
    if has_any(text, TONE_HINTS["subtle"]):
        return "subtle"
    if has_any(text, TONE_HINTS["energetic"]) or business_intent == "urgency":
        return "energetic"
    if mode in {"marketing", "optimize"}:
        return "balanced"
    if mode in {"pack", "sprite"}:
        return "playful"
    return "balanced"


def layout_for(target: str) -> tuple[int, int]:
    if target == "detail-page":
        return 900, 506
    if target == "ad-banner":
        return 1080, 1080
    return 512, 512


def preset_for(mode: str, target: str, intensity: str, business_intent: str) -> str:
    if mode == "optimize":
        return "optimize"
    if mode == "sprite":
        return "sprite"
    if mode == "pack":
        return "bounce"
    if target == "detail-page":
        return "detail-page"
    if target == "ad-banner":
        return "pulse" if intensity == "energetic" else "caption-pop"
    if intensity == "subtle":
        return "gentle-zoom"
    if intensity == "energetic":
        return "pulse"
    if business_intent == "product_demo":
        return "slide"
    return "caption-pop"


def timing_for(mode: str, target: str) -> tuple[float, int, int]:
    fps = 10
    if mode == "sprite":
        return 1.6, fps, 16
    if target == "detail-page":
        return 2.0, fps, 16
    if target == "ad-banner":
        return 1.8, fps, 14
    return 1.6, fps, 12


def quality_flags_for(mode: str, target: str, intensity: str) -> list[str]:
    flags = ["readback-validation", "contact-sheet"]
    if target in {"detail-page", "ad-banner"} or mode == "marketing":
        flags.append("business-facing")
    if target in {"chat", "sticker", "sticker-pack"}:
        flags.append("caption-readability")
    if intensity == "subtle":
        flags.append("avoid-chaotic-motion")
    if mode == "optimize" or target == "lightweight-web":
        flags.append("size-budget")
    return list(dict.fromkeys(flags))


def plan_prompt(prompt: str, has_reference: bool = False) -> dict:
    text = " ".join(prompt.lower().split())
    business_intent = infer_business_intent(text)
    mode = infer_mode(text, has_reference=has_reference, business_intent=business_intent)
    if mode == "optimize":
        business_intent = "unknown"
    target = infer_target(text, mode=mode, business_intent=business_intent)
    intensity = infer_motion_intensity(text, mode=mode, business_intent=business_intent)
    preset = preset_for(mode, target, intensity, business_intent)
    duration, fps, frame_count = timing_for(mode, target)
    width, height = layout_for(target)
    caption_text = "" if mode == "pack" else extract_caption(prompt, business_intent)
    caption_role = CAPTION_ROLES.get(business_intent, "message")
    caption_zone = "top" if "상단" in text else "bottom"
    count = 4 if mode == "pack" else 1
    needs_reference_analysis = mode == "reference"
    max_width = 720
    max_frames = 14
    flags = quality_flags_for(mode, target, intensity)
    rationale = []

    if needs_reference_analysis:
        rationale.append("reference-style request")
    if mode == "marketing":
        rationale.append("business-facing target")
    if business_intent != "unknown":
        rationale.append(f"business intent: {business_intent}")
    if intensity == "subtle":
        rationale.append("subtle/premium tone")
    if intensity == "energetic":
        rationale.append("energetic emphasis")
    if mode == "optimize":
        rationale.append("optimization request")

    signal_count = (
        count_hits(text, sum(BUSINESS_INTENTS.values(), []))
        + count_hits(text, sum(TARGET_HINTS.values(), []))
        + count_hits(text, TONE_HINTS["subtle"])
        + count_hits(text, TONE_HINTS["energetic"])
    )
    confidence = min(0.95, 0.55 + signal_count * 0.06 + (0.12 if mode != "quick" else 0))

    plan = {
        "version": "1.1",
        "mode": mode,
        "target": target,
        "business_intent": business_intent,
        "preset": preset,
        "caption": {
            "text": caption_text,
            "role": caption_role,
            "placement": caption_zone,
            "priority": "high" if caption_text else "optional",
        },
        "motion": {
            "preset": preset,
            "intensity": intensity,
            "duration": duration,
            "fps": fps,
            "frame_count": frame_count,
        },
        "layout": {
            "width": width,
            "height": height,
            "caption_zone": caption_zone,
        },
        "constraints": {
            "no_video": True,
            "external_upload": "forbidden_by_default",
            "max_width": max_width,
            "max_frames": max_frames,
        },
        "quality_flags": flags,
        "needs_reference_analysis": needs_reference_analysis,
        "count": count,
        "confidence": round(confidence, 2),
        "rationale": rationale,
    }

    # Legacy aliases for existing scripts and older tests.
    plan["width"] = plan["layout"]["width"]
    plan["height"] = plan["layout"]["height"]
    plan["duration"] = plan["motion"]["duration"]
    plan["fps"] = plan["motion"]["fps"]
    plan["frame_count"] = plan["motion"]["frame_count"]
    plan["max_width"] = plan["constraints"]["max_width"]
    plan["max_frames"] = plan["constraints"]["max_frames"]
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
