# GIF Director Prompt Intelligence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `gif-director` from a working GIF skill into a service-grade prompt interpreter that turns attached images and Korean/business prompts into marketing/detail-page GIFs, sticker packs, and optimized GIF inserts without video generation.

**Architecture:** Keep the deterministic Pillow GIF renderer as the default engine. Add a structured planning layer, marketing intent recipes, plan-driven orchestration, and stricter visual/readback QA so Codex/Claude Code/Antigravity can infer the right mode without users learning flags. Preserve optional still-image sprite generation only behind explicit upload consent.

**Tech Stack:** Python stdlib, Pillow, `unittest`, existing Agent Skill manifests, `gh skill install` install verification.

---

## Reference Hub Inputs

- `ai_agent_rag_core`: prompt routing, prompt chaining, and evaluation flywheel patterns from `dair-ai__prompt-engineering-guide`, `openai__openai-cookbook`, and `microsoft__agent-framework`.
- `mcp_connectors_agent_skills_core`: progressive skill disclosure and task routing patterns from `muratcankoylan__agent-skills-for-context-engineering` and Microsoft Agent Skills examples.
- `business_pm_marketing_skills_optional_core`: product messaging, CTA, launch/GTM, CRO, landing-page, and hero visual/GIF positioning references from `marketingagentskills`, `marketingskills`, `pm-skills`, and SuperPM prompt index.
- `design_visual_automation_core`: visual context/readback habit from Figma MCP guide, especially "get design context, then get screenshot" as an analogue for reference analysis plus contact-sheet QA.

## Success Criteria

- Korean prompt routing passes at least 40 fixture cases across marketing, detail page, sticker pack, optimize, sprite, reference-style, premium/subtle, urgent/promo, review/trust, and product demo prompts.
- `gif_director.py --prompt ... --image ...` writes `plan.json`, GIF, contact sheet, validation/QA report, and final report under `outputs/`.
- Business-facing output reports include actual saved dimensions, frame count, duration, file size, selected business intent, motion intensity, caption placement, and unresolved risks.
- No video generation, image-to-video, MP4/MOV/WebM workflow, or external image upload is introduced.
- Local and remote skill install paths still work for Codex, Claude Code, and Antigravity.

## Files

- Modify: `skills/gif-director/scripts/plan_gif.py`
- Create: `skills/gif-director/scripts/planner_rules.py`
- Modify: `skills/gif-director/scripts/gif_director.py`
- Modify: `skills/gif-director/scripts/gif_utils.py`
- Modify: `skills/gif-director/scripts/render_gif.py`
- Modify: `skills/gif-director/scripts/validate_gif.py`
- Create: `skills/gif-director/scripts/qa_report.py`
- Create: `skills/gif-director/references/marketing-intent-recipes.md`
- Modify: `skills/gif-director/references/motion-recipes.md`
- Modify: `skills/gif-director/references/quality-rubric.md`
- Modify: `skills/gif-director/SKILL.md`
- Modify: `README.md`
- Modify: `tests/test_prompt_planner.py`
- Create: `tests/fixtures/prompt_cases.json`
- Create: `tests/test_qa_report.py`
- Modify: `tests/test_gif_director_scripts.py`
- Release-only modify: `.codex-plugin/plugin.json`
- Release-only modify: `.claude-plugin/plugin.json`
- Release-only modify: `.claude-plugin/marketplace.json`

---

### Task 1: Golden Prompt Evaluation Fixtures

**Files:**
- Create: `tests/fixtures/prompt_cases.json`
- Modify: `tests/test_prompt_planner.py`

- [ ] **Step 1: Add representative Korean/business prompt fixtures**

Create `tests/fixtures/prompt_cases.json` with cases like:

```json
[
  {
    "id": "detail_launch_offer_premium",
    "prompt": "상세페이지 중간에 넣을 런칭 특가 GIF. 고급스럽고 너무 정신없지 않게.",
    "has_reference": false,
    "expect": {
      "mode": "marketing",
      "target": "detail-page",
      "business_intent": "launch_offer",
      "motion_intensity": "subtle",
      "caption_role": "offer",
      "must_have_flags": ["business-facing", "contact-sheet", "readback-validation", "avoid-chaotic-motion"]
    }
  },
  {
    "id": "detail_feature_highlight",
    "prompt": "제품 사진으로 상세페이지용 기능 강조 움짤 만들어줘. 문구는 흡수력 업.",
    "has_reference": false,
    "expect": {
      "mode": "marketing",
      "target": "detail-page",
      "business_intent": "feature_highlight",
      "motion_intensity": "balanced",
      "caption": "흡수력 업"
    }
  },
  {
    "id": "kakao_reaction_pack",
    "prompt": "카톡에서 쓸 귀여운 리액션팩 4개 만들어줘. 확인했어요, 좋아요, 잠깐만요, 완전 추천.",
    "has_reference": false,
    "expect": {
      "mode": "pack",
      "target": "sticker-pack",
      "count": 4,
      "business_intent": "reaction_pack"
    }
  },
  {
    "id": "reference_mimic",
    "prompt": "첨부한 레퍼런스처럼 사진이 딸깍 튀면서 글자가 크게 나오는 느낌으로.",
    "has_reference": true,
    "expect": {
      "mode": "reference",
      "needs_reference_analysis": true,
      "motion_intensity": "reference"
    }
  }
]
```

- [ ] **Step 2: Replace narrow prompt assertions with fixture-driven checks**

In `tests/test_prompt_planner.py`, keep the existing subprocess helper and add:

```python
FIXTURES = ROOT / "tests" / "fixtures" / "prompt_cases.json"

def flatten_plan_value(plan: dict, key: str):
    if key == "motion_intensity":
        return plan.get("motion", {}).get("intensity")
    if key == "caption_role":
        return plan.get("caption", {}).get("role")
    if key == "caption":
        caption = plan.get("caption", "")
        return caption.get("text", "") if isinstance(caption, dict) else caption
    return plan.get(key)

def test_fixture_prompt_cases(self) -> None:
    cases = json.loads(FIXTURES.read_text(encoding="utf-8"))
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
```

- [ ] **Step 3: Run the planner test and confirm it fails before implementation**

Run:

```powershell
python -B -m unittest tests.test_prompt_planner
```

Expected: FAIL because `business_intent`, nested `motion`, and nested `caption` are not implemented yet.

---

### Task 2: Structured Planner Schema

**Files:**
- Create: `skills/gif-director/scripts/planner_rules.py`
- Modify: `skills/gif-director/scripts/plan_gif.py`

- [ ] **Step 1: Create focused planner rules**

Create `planner_rules.py` with phrase sets and defaults:

```python
from __future__ import annotations

BUSINESS_INTENTS = {
    "launch_offer": ["런칭", "특가", "오픈", "할인", "혜택", "쿠폰"],
    "feature_highlight": ["기능", "강조", "흡수력", "효과", "성능", "포인트"],
    "review_trust": ["후기", "리뷰", "만족", "검증", "믿고", "재구매"],
    "social_proof": ["인기", "베스트", "추천", "판매량", "1위"],
    "urgency": ["오늘만", "마감", "한정", "지금", "놓치지"],
    "product_demo": ["사용법", "전후", "비교", "보여줘", "시연"],
    "reaction_pack": ["리액션팩", "4개", "네 개", "감정", "카톡"],
}

TARGET_HINTS = {
    "detail-page": ["상세페이지", "상세", "제품페이지", "상품페이지"],
    "ad-banner": ["광고", "배너", "소셜", "인스타", "정사각"],
    "sticker-pack": ["팩", "리액션팩", "스티커"],
    "lightweight-web": ["용량", "최적화", "가볍게", "삽입"],
}

TONE_HINTS = {
    "subtle": ["고급", "깔끔", "프리미엄", "차분", "너무 정신없지", "과하지 않게"],
    "energetic": ["딸깍", "통통", "강조", "팡", "튀", "신나게"],
}

DEFAULT_CAPTIONS = {
    "launch_offer": "런칭 특가",
    "feature_highlight": "포인트 체크",
    "review_trust": "만족 후기",
    "social_proof": "완전 추천",
    "urgency": "오늘만",
    "product_demo": "한눈에 보기",
    "reaction_pack": "",
    "unknown": "",
}
```

- [ ] **Step 2: Change `plan_prompt()` to emit nested, service-grade fields**

In `plan_gif.py`, preserve existing top-level compatibility keys and add nested fields:

```python
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
        "priority": "high" if caption_text else "optional"
    },
    "motion": {
        "preset": preset,
        "intensity": motion_intensity,
        "duration": duration,
        "fps": fps,
        "frame_count": frame_count
    },
    "layout": {
        "width": width,
        "height": height,
        "caption_zone": caption_zone
    },
    "constraints": {
        "no_video": True,
        "external_upload": "forbidden_by_default",
        "max_width": max_width,
        "max_frames": max_frames
    },
    "quality_flags": quality_flags,
    "needs_reference_analysis": needs_reference_analysis,
    "count": count,
    "confidence": confidence,
    "rationale": rationale,
}
```

Keep these legacy aliases for current callers:

```python
plan["width"] = plan["layout"]["width"]
plan["height"] = plan["layout"]["height"]
plan["duration"] = plan["motion"]["duration"]
plan["fps"] = plan["motion"]["fps"]
plan["frame_count"] = plan["motion"]["frame_count"]
plan["max_width"] = plan["constraints"]["max_width"]
plan["max_frames"] = plan["constraints"]["max_frames"]
```

- [ ] **Step 3: Run planner fixture tests**

Run:

```powershell
python -B -m unittest tests.test_prompt_planner
```

Expected: PASS after all fixture expectations are supported.

---

### Task 3: Plan-Driven Orchestration

**Files:**
- Modify: `skills/gif-director/scripts/gif_director.py`
- Modify: `tests/test_gif_director_scripts.py`

- [ ] **Step 1: Add tests for prompt-to-output report shape**

In `tests/test_gif_director_scripts.py`, add a smoke test that creates a tiny image, runs `gif_director.py --prompt`, and asserts:

```python
self.assertEqual(report["plan"]["business_intent"], "launch_offer")
self.assertIn("gif", report)
self.assertIn("contact_sheet", report)
self.assertTrue(report["validation"]["ok"], report)
self.assertEqual(report["plan"]["constraints"]["no_video"], True)
```

- [ ] **Step 2: Make `render_one()` accept layout from the planner**

Change the function signature:

```python
def render_one(
    images: list[Path],
    text: str,
    output: Path,
    report: Path,
    preset_name: str,
    max_bytes: int,
    width: int | None = None,
    height: int | None = None,
    duration: float | None = None,
    fps: int | None = None,
    caption_zone: str = "bottom",
) -> dict:
```

Inside the function, use:

```python
default_width, default_height, render_preset, default_duration = preset_details(preset_name)
width = width or default_width
height = height or default_height
duration = duration or default_duration
fps = fps or 10
```

Append `--fps` and `--caption-zone` to the `render_gif.py` subprocess arguments.

- [ ] **Step 3: Persist plan data as a real output artifact**

When `args.prompt` exists, write:

```python
plan_path = args.output_dir / f"{args.base_name}-plan.json"
write_json(plan_path, plan)
```

Include `plan_path` in final, pack, and optimize reports.

- [ ] **Step 4: Route reference prompts through `analyze_reference_gif.py`**

If `plan["needs_reference_analysis"]` and `args.reference_gif` are present, run `analyze_reference_gif.py --input <reference> --json`, store the analysis in the final report, and use its style recipe to select closest existing preset, duration, and frame budget.

- [ ] **Step 5: Run orchestrator smoke tests**

Run:

```powershell
python -B -m unittest tests.test_gif_director_scripts
```

Expected: PASS and output reports include `plan_path`, nested `plan`, GIF metadata, and validation.

---

### Task 4: Caption and Visual QA Report

**Files:**
- Modify: `skills/gif-director/scripts/gif_utils.py`
- Modify: `skills/gif-director/scripts/render_gif.py`
- Modify: `skills/gif-director/scripts/validate_gif.py`
- Create: `skills/gif-director/scripts/qa_report.py`
- Create: `tests/test_qa_report.py`

- [ ] **Step 1: Make caption drawing return metrics**

Change `draw_caption()` to return:

```python
{
    "text": text,
    "zone": zone,
    "bbox": [margin, y, margin + box_width, y + box_height],
    "line_count": len(lines),
    "font_size": getattr(font, "size", 0),
    "text_height": text_height,
    "box_height": box_height,
    "clipped": text_height > max_text_height
}
```

When there is no text, return:

```python
{"text": "", "zone": zone, "bbox": None, "line_count": 0, "font_size": 0, "text_height": 0, "box_height": 0, "clipped": False}
```

- [ ] **Step 2: Store caption metrics in render reports**

In `render_gif.py`, collect the last non-empty caption metric and write it into the report:

```python
caption_metrics = []
...
metrics = draw_caption(frame, args.text, min(1, progress), zone=args.caption_zone)
caption_metrics.append(metrics)
...
report.update({
    "caption": args.text,
    "caption_zone": args.caption_zone,
    "caption_metrics": caption_metrics[-1] if caption_metrics else None,
})
```

- [ ] **Step 3: Add QA report composition**

Create `qa_report.py` that accepts `--gif`, `--render-report`, `--plan`, `--output`, and `--max-bytes`. It should read the saved GIF through `inspect_gif()`, merge planner/render metadata, and emit:

```python
{
    "ok": True,
    "issues": [],
    "target": plan.get("target"),
    "business_intent": plan.get("business_intent"),
    "motion_intensity": plan.get("motion", {}).get("intensity"),
    "caption": render_report.get("caption"),
    "caption_metrics": render_report.get("caption_metrics"),
    "gif": inspect_gif(gif_path)
}
```

Mark `ok` false when:

```python
if gif["frame_count"] < 2: issues.append("too few frames")
if gif["duration_ms"] <= 0: issues.append("missing frame durations")
if gif["file_size_bytes"] > max_bytes: issues.append("file too large")
if gif["blank_frames"] >= gif["frame_count"]: issues.append("all frames are blank")
if gif["changed_transitions"] == 0 and gif["frame_count"] > 1: issues.append("frames do not visibly change")
if caption_metrics and caption_metrics.get("clipped"): issues.append("caption clipped")
if plan.get("target") == "detail-page" and not render_report.get("caption"): issues.append("business caption missing")
if plan.get("constraints", {}).get("no_video") is not True: issues.append("no-video constraint missing")
```

- [ ] **Step 4: Add QA tests**

In `tests/test_qa_report.py`, create a generated GIF through `render_gif.py`, create a minimal plan JSON with `target: detail-page`, run `qa_report.py`, and assert:

```python
self.assertTrue(report["ok"], report)
self.assertEqual(report["target"], "detail-page")
self.assertEqual(report["business_intent"], "launch_offer")
self.assertGreater(report["gif"]["frame_count"], 1)
self.assertFalse(report["caption_metrics"]["clipped"], report)
```

- [ ] **Step 5: Run QA tests**

Run:

```powershell
python -B -m unittest tests.test_qa_report
```

Expected: PASS.

---

### Task 5: Marketing Intent Recipes

**Files:**
- Create: `skills/gif-director/references/marketing-intent-recipes.md`
- Modify: `skills/gif-director/references/motion-recipes.md`
- Modify: `skills/gif-director/references/quality-rubric.md`
- Modify: `skills/gif-director/SKILL.md`

- [ ] **Step 1: Add marketing recipes**

Create `marketing-intent-recipes.md` with this table:

```markdown
# Marketing Intent Recipes

| Intent | Best target | Caption role | Motion | Default caption | QA emphasis |
| --- | --- | --- | --- | --- | --- |
| launch_offer | detail-page/ad-banner | offer | subtle or balanced pulse | 런칭 특가 | offer visible on first loop |
| feature_highlight | detail-page | benefit | slide or detail-page | 포인트 체크 | product not covered |
| review_trust | detail-page | trust | gentle-zoom | 만족 후기 | readable, calm loop |
| social_proof | detail-page/ad-banner | proof | caption-pop | 완전 추천 | text prominence |
| urgency | ad-banner/detail-page | CTA | pulse | 오늘만 | short duration |
| product_demo | detail-page | explanation | slide or polaroid | 한눈에 보기 | sequence clarity |
| reaction_pack | sticker-pack | reaction | bounce/pulse/wiggle | mixed | four outputs distinct |
```

- [ ] **Step 2: Update skill instructions**

In `SKILL.md`, change the planning rule to require this order:

```markdown
1. Run or mentally follow `scripts/plan_gif.py`.
2. Read `references/marketing-intent-recipes.md` when the target is business-facing.
3. Read `references/motion-recipes.md` for preset selection.
4. Render locally.
5. Generate contact sheet and QA report.
6. Repair only the failed axis.
```

- [ ] **Step 3: Run skill validation**

Run:

```powershell
$env:PYTHONUTF8='1'; python "C:\Users\SANGYUN HAN\.codex\skills\.system\skill-creator\scripts\quick_validate.py" skills\gif-director
```

Expected: PASS.

---

### Task 6: Full Workflow Verification

**Files:**
- Modify: `tests/test_gif_director_scripts.py`
- Modify: `README.md`

- [ ] **Step 1: Add one end-to-end marketing prompt smoke test**

The test should create a small product image, run:

```powershell
python -B skills\gif-director\scripts\gif_director.py --prompt "상세페이지 중간에 넣을 런칭 특가 GIF. 고급스럽고 너무 정신없지 않게." --image <tmp>\product.png --output-dir <tmp>\outputs --base-name planned-detail
```

Assert the following files exist:

```python
planned-detail.gif
planned-detail-sheet.png
planned-detail-plan.json
planned-detail-report.json
```

- [ ] **Step 2: Update README usage examples**

Add examples for:

```bash
python skills/gif-director/scripts/gif_director.py --prompt "상세페이지용 런칭 특가 GIF. 고급스럽고 너무 정신없지 않게." --image product.png --output-dir outputs --base-name detail-launch
python skills/gif-director/scripts/gif_director.py --prompt "카톡에서 쓸 리액션팩 4개 만들어줘." --image mascot.png --output-dir outputs --base-name reaction
python skills/gif-director/scripts/gif_director.py --prompt "이 GIF 상세페이지에 넣게 용량 줄여줘." --input-gif source.gif --output-dir outputs --base-name source-small
```

- [ ] **Step 3: Run all unit tests**

Run:

```powershell
python -B -m unittest tests.test_prompt_planner tests.test_gif_director_scripts tests.test_qa_report
```

Expected: PASS.

---

### Task 7: Release and Install Proof

**Files:**
- Modify: `.codex-plugin/plugin.json`
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `docs/PROJECT_CONTEXT.md`

- [ ] **Step 1: Bump plugin versions to `1.1.0`**

Set each manifest version field to:

```json
"version": "1.1.0"
```

- [ ] **Step 2: Run validators**

Run:

```powershell
python "C:\Users\SANGYUN HAN\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py" .
$env:PYTHONUTF8='1'; python "C:\Users\SANGYUN HAN\.codex\skills\.system\skill-creator\scripts\quick_validate.py" skills\gif-director
```

Expected: both PASS.

- [ ] **Step 3: Verify local install paths**

Run with fresh temp directories:

```powershell
gh skill install . gif-director --from-local --agent codex --dir <temp-codex> --force
gh skill install . gif-director --from-local --agent claude-code --dir <temp-claude> --force
gh skill install . gif-director --from-local --agent antigravity --dir <temp-antigravity> --force
```

Expected: each install directory contains `skills/gif-director/SKILL.md`, `scripts/plan_gif.py`, and `scripts/qa_report.py`.

- [ ] **Step 4: Commit and push**

Run:

```powershell
git status --short
git add skills tests README.md .codex-plugin .claude-plugin docs/superpowers/plans/2026-06-05-gif-director-prompt-intelligence.md
git commit -m "Upgrade GIF Director prompt intelligence"
git push origin main
```

- [ ] **Step 5: Verify remote install**

Run:

```powershell
gh skill install TUNA-HAN/gif-director-skill gif-director --agent codex --dir <temp-remote> --force
```

Expected: remote install includes `scripts/qa_report.py`, `references/marketing-intent-recipes.md`, and the updated `SKILL.md`.

---

## Execution Choice

Recommended execution order:

1. Task 1 and Task 2 first. This proves the "알잘딱" prompt interpretation layer.
2. Task 3 and Task 4 next. This makes the planner actually drive rendering and QA.
3. Task 5 and Task 6 next. This makes the skill understandable and verifiable for real users.
4. Task 7 last. This publishes only after local behavior and install paths are proven.

Use subagent-driven execution if speed matters. Use inline execution if we want tighter manual control over the Korean planner rules.
