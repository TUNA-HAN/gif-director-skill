---
name: gif-director
description: Use when creating, adapting, validating, optimizing, or style-matching animated GIFs from images, multiple images, text, Korean captions, reaction prompts, sticker packs, marketing/detail-page assets, existing GIFs, or reference GIFs; includes "움짤", "짤", "gif", "스티커", "상세페이지", and "이런 느낌" requests.
---

# GIF Director

## Overview

Create polished non-video GIFs for chat, sticker packs, marketing banners, product detail pages, and reference-style matching. Work locally by default, analyze references before imitating them, and always validate the saved GIF by reading it back.

## Hard Rules

- Do not use video generation, image-to-video models, MP4, MOV, WebM, or video transcode workflows.
- Do not upload user images to external services unless the user explicitly requests cloud/AI still-image assistance and consents to upload.
- Do not trust intended frame data. Re-open the final GIF and report actual dimensions, frame count, duration, and file size.
- Use ASCII console output in scripts. Korean belongs in captions, prompts, docs, and reports, not status glyphs.
- Preserve Korean captions with CJK-capable font fallback, wrapping, text outline, and automatic fit.
- Prefer deterministic local rendering for business assets. Use AI sprite-sheet generation only as an optional still-image lane.

## Mode Routing

- **quick**: one polished GIF from image(s) and text. Default for vague "움짤 만들어줘" requests.
- **reference**: run `analyze_reference_gif.py`, then copy canvas, timing, caption zone, and motion intensity.
- **sprite**: use `render_sprite_gif.py` for 4x4 sprite sheets or deterministic still-image animation.
- **pack**: use `gif_director.py --mode pack` for four reaction/sticker variants.
- **marketing**: use `gif_director.py --mode marketing --preset detail-page` for detail-page or ad insert GIFs.
- **optimize**: use `optimize_gif.py` for web/detail-page size, frame, and encoder optimization.

Read `references/motion-recipes.md` for preset selection and `references/quality-rubric.md` before final delivery.

## Main Commands

Install local runtime dependency:

```bash
python -m pip install -r <skill-dir>/requirements.txt
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
python <skill-dir>/scripts/gif_director.py --mode pack --image input.png --output-dir outputs --base-name campaign
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
python <skill-dir>/scripts/optimize_gif.py --input outputs/detail-hero.gif --output outputs/detail-hero-small.gif --report outputs/detail-hero-small.json --max-width 720 --max-frames 14
```

## Required Delivery Loop

1. Resolve images, text, target use, and output path. Default to `outputs/`.
2. If a reference GIF exists, run `analyze_reference_gif.py` and use its `style_recipe`.
3. Route to quick, sprite, pack, marketing, or optimize mode.
4. Render locally with Pillow unless the user explicitly authorizes AI still-image upload.
5. Generate a contact sheet for anything subjective or business-facing.
6. Validate with `validate_gif.py --json`.
7. If validation fails, repair the smallest axis: text fit, canvas, frame count, duration, or file size.
8. Final response: output path, contact sheet path when present, dimensions, frame count, duration, file size, and any unresolved risk.

## Presets

Core render presets: `caption-pop`, `gentle-zoom`, `shake`, `bounce`, `polaroid`, `pulse`, `spin`, `slide`, `wiggle`, `explode`, `detail-page`.

Business target presets in `gif_director.py`: `chat`, `sticker`, `detail-page`, `ad-banner`.

## Quality Bar

- Text readable at final display size.
- Main subject not covered by captions.
- First frame identifies the subject or offer.
- Loop feels intentional.
- No blank frames.
- Actual saved frame count matches the intended motion class.
- File size is appropriate for the target surface.
- No external upload occurred unless explicitly authorized.
