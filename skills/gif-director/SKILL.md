---
name: gif-director
description: Use when creating, adapting, validating, optimizing, or style-matching animated GIFs from images, multiple images, text, Korean captions, reaction prompts, sticker packs, marketing/detail-page assets, existing GIFs, or reference GIFs; includes "움짤", "짤", "gif", "스티커", "상세페이지", and "레퍼런스" requests.
---

# GIF Director

## Overview

Create polished non-video GIFs for chat, sticker packs, marketing banners, product detail pages, and reference-style matching. Work locally by default, analyze references before imitating them, and always validate the saved GIF by reading it back.

## Hard Rules

- Do not use video generation, image-to-video models, MP4, MOV, WebM, or video transcode workflows.
- Do not upload user images to external services unless the user explicitly requests cloud/AI still-image assistance and consents to upload.
- Do not trust intended frame data. Re-open the final GIF and report actual dimensions, frame count, duration, and file size.
- Use ASCII console status output in scripts. Korean belongs in captions, prompts, docs, and reports, not status glyphs.
- Preserve Korean captions with CJK-capable font fallback, wrapping, text outline, and automatic fit.
- Prefer deterministic local rendering for business assets. Use AI sprite-sheet generation only as an optional still-image lane.

## Mode Routing

For natural-language requests, run or mentally follow `scripts/plan_gif.py` first. The plan must choose mode, target, business intent, preset, caption, dimensions, quality flags, constraints, and whether reference analysis is required before rendering.

- **quick**: one polished GIF from image(s) and text. Default for vague "움짤 만들어줘" requests.
- **reference**: run `analyze_reference_gif.py`, then copy canvas, timing, caption zone, and motion intensity.
- **sprite**: use `render_sprite_gif.py` for 4x4 sprite sheets or deterministic still-image animation.
- **photoreal**: use AI still-image editing keyframes when the user asks for a realistic action, expression, or pose that is not present in the source image.
- **pack**: use `gif_director.py --mode pack` for four reaction/sticker variants.
- **marketing**: use `gif_director.py --mode marketing --preset detail-page` for detail-page or ad insert GIFs.
- **optimize**: use `optimize_gif.py` for web/detail-page size, frame, and encoder optimization.

Read `references/photoreal-action-recipes.md` for realistic action/expression edits, `references/marketing-intent-recipes.md` for business-facing GIFs, `references/motion-recipes.md` for preset selection, and `references/quality-rubric.md` before final delivery.

## Main Commands

Install local runtime dependency:

```bash
python -m pip install -r <skill-dir>/requirements.txt
```

Natural-language prompt, preferred for most users:

```bash
python <skill-dir>/scripts/gif_director.py --prompt "상세페이지용 런칭 특가 GIF. 고급스럽고 너무 정신없지 않게." --image product.png --output-dir outputs --base-name detail-launch
```

One GIF from image(s):

```bash
python <skill-dir>/scripts/gif_director.py --mode quick --image input.png --text "퇴근하고 싶다" --output-dir outputs --base-name reaction
```

Marketing/detail-page GIF:

```bash
python <skill-dir>/scripts/gif_director.py --mode marketing --image product1.png --image product2.png --text "런칭 특가" --preset detail-page --output-dir outputs --base-name detail-hero
```

Four reaction pack:

```bash
python <skill-dir>/scripts/gif_director.py --prompt "카톡에서 쓸 리액션팩 4개 만들어줘." --image mascot.png --output-dir outputs --base-name reaction
```

Photoreal action GIF from a still image, only after explicit upload consent:

```bash
python <skill-dir>/scripts/gif_director.py --prompt "이 사진을 아빠가 딸에게 뽀뽀를 하려는데 딸이 싫어하는 영상으로 만들어줘." --image family.png --output-dir outputs --base-name family-reject --allow-upload
```

Sprite sheet or still-image character motion:

```bash
python <skill-dir>/scripts/render_sprite_gif.py --sprite-sheet sprite_4x4.png --output outputs/sprite.gif --report outputs/sprite.json
python <skill-dir>/scripts/render_sprite_gif.py --image portrait.png --text "좋아요" --output outputs/portrait-sprite.gif
```

Optional Gemini still-image sprite sheet generation, only after upload consent:

```bash
python -m pip install -r <skill-dir>/requirements-ai.txt
python <skill-dir>/scripts/generate_sprite_sheet_gemini.py --image portrait.png --output outputs/sprite-sheet.png --allow-upload
```

Optimize an existing GIF:

```bash
python <skill-dir>/scripts/gif_director.py --prompt "이 GIF 상세페이지에 넣게 용량 줄여줘." --input-gif source.gif --output-dir outputs --base-name source-small
```

## Required Delivery Loop

1. Resolve images, text, target use, and output path. Default to `outputs/`.
2. Run or mentally follow `scripts/plan_gif.py`.
3. Read `references/marketing-intent-recipes.md` when the target is business-facing.
4. Read `references/photoreal-action-recipes.md` when the prompt asks for realistic new action, pose, or expression.
5. Read `references/motion-recipes.md` for preset selection.
6. If a reference GIF exists, run `analyze_reference_gif.py` and use its `style_recipe`.
7. Render locally with Pillow unless the user explicitly authorizes AI still-image upload.
8. For photoreal mode, refuse generation without `--allow-upload`; do not fall back to overlays or duplicated subjects.
9. Generate contact sheet and QA report for subjective, prompt-driven, or business-facing work.
10. Validate with `validate_gif.py --json` or inspect the final report's `validation`.
11. If validation or QA fails, repair only the failed axis: text fit, canvas, frame count, duration, motion intensity, file size, or failed keyframe.
12. Final response: output path, contact sheet path when present, dimensions, frame count, duration, file size, upload status, and any unresolved risk.

## Output Contract

Prompt-driven `gif_director.py` runs should preserve:

- `<base>.gif`
- `<base>-plan.json`
- `<base>-sheet.png`
- `<base>-qa.json`
- `<base>-report.json`

Photoreal runs should also preserve:

- `<base>-frame-01.png` through generated keyframes
- `<base>-photoreal-report.json`

## Presets

Core render presets: `caption-pop`, `gentle-zoom`, `shake`, `bounce`, `polaroid`, `pulse`, `spin`, `slide`, `wiggle`, `explode`, `detail-page`.

Business target presets in `gif_director.py`: `chat`, `sticker`, `detail-page`, `ad-banner`.

## Quality Bar

- Text readable at final display size.
- Main subject not covered by captions.
- First frame identifies the subject or offer.
- Business intent matches the user's prompt.
- Loop feels intentional.
- No blank frames.
- Actual saved frame count matches the intended motion class.
- File size is appropriate for the target surface.
- No external upload occurred unless explicitly authorized.
- For photoreal action GIFs, no duplicated people, no extra child/parent, no clone, and no cartoon/text overlay substitute.
