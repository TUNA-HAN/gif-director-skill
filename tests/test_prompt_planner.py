import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLANNER = ROOT / "skills" / "gif-director" / "scripts" / "plan_gif.py"
FIXTURES = ROOT / "tests" / "fixtures" / "prompt_cases.json"


def flatten_plan_value(plan: dict, key: str):
    if key == "motion_intensity":
        return plan.get("motion", {}).get("intensity")
    if key == "caption_role":
        return plan.get("caption", {}).get("role")
    if key == "caption":
        caption = plan.get("caption", "")
        return caption.get("text", "") if isinstance(caption, dict) else caption
    if key == "frame_count":
        return plan.get("motion", {}).get("frame_count", plan.get("frame_count"))
    if key == "no_video":
        return plan.get("constraints", {}).get("no_video")
    return plan.get(key)


class PromptPlannerTests(unittest.TestCase):
    def plan(self, prompt: str, *extra: str) -> dict:
        result = subprocess.run(
            [sys.executable, "-B", str(PLANNER), "--prompt", prompt, *extra],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return json.loads(result.stdout)

    def test_fixture_prompt_cases(self) -> None:
        cases = json.loads(FIXTURES.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases), 40)
        for case in cases:
            with self.subTest(case=case["id"]):
                extra = ["--has-reference"] if case.get("has_reference") else []
                plan = self.plan(case["prompt"], *extra)
                for key, expected in case["expect"].items():
                    if key == "must_have_flags":
                        flags = set(plan.get("quality_flags", []))
                        self.assertTrue(set(expected).issubset(flags), plan)
                    else:
                        self.assertEqual(flatten_plan_value(plan, key), expected, plan)

    def test_detail_page_marketing_prompt_prefers_subtle_business_motion(self) -> None:
        plan = self.plan("상세페이지 중간에 넣을 런칭 특가 GIF. 고급스럽고 너무 정신없지 않게.")
        self.assertEqual(plan["mode"], "marketing")
        self.assertEqual(plan["target"], "detail-page")
        self.assertEqual(plan["preset"], "detail-page")
        self.assertEqual(plan["width"], 900)
        self.assertEqual(plan["height"], 506)
        self.assertEqual(flatten_plan_value(plan, "caption"), "런칭 특가")
        self.assertIn("avoid-chaotic-motion", plan["quality_flags"])

    def test_pack_prompt_routes_to_four_reaction_outputs(self) -> None:
        plan = self.plan("카톡에서 친구한테 보낼 귀여운 리액션팩 네 개 만들어줘")
        self.assertEqual(plan["mode"], "pack")
        self.assertEqual(plan["target"], "sticker-pack")
        self.assertEqual(plan["count"], 4)
        self.assertEqual(plan["preset"], "bounce")

    def test_sprite_prompt_routes_to_sprite_mode(self) -> None:
        plan = self.plan("첨부 이미지를 캐릭터처럼 움직이는 16프레임 GIF로 만들어줘")
        self.assertEqual(plan["mode"], "sprite")
        self.assertEqual(plan["preset"], "sprite")
        self.assertEqual(plan["frame_count"], 16)

    def test_optimize_prompt_routes_to_optimize_mode(self) -> None:
        plan = self.plan("이미 만든 GIF 용량 줄여서 상세페이지에 삽입하기 좋게 최적화해줘")
        self.assertEqual(plan["mode"], "optimize")
        self.assertEqual(plan["target"], "lightweight-web")
        self.assertLessEqual(plan["max_width"], 720)
        self.assertLessEqual(plan["max_frames"], 14)

    def test_reference_prompt_requires_reference_analysis(self) -> None:
        plan = self.plan("이런 참고로 따라해서 카톡용 짤 만들어줘", "--has-reference")
        self.assertEqual(plan["mode"], "reference")
        self.assertEqual(plan["target"], "chat")
        self.assertTrue(plan["needs_reference_analysis"])


if __name__ == "__main__":
    unittest.main()
