---
name: gif-director
description: Use when creating, adapting, validating, optimizing, or style-matching animated GIFs from images, text, Korean captions, reaction prompts, sticker requests, existing GIFs, or reference GIFs; includes "움짤", "짤", "gif", "스티커", and "이런 느낌" requests.
---

# GIF Director

## Overview

Create polished non-video GIFs from user images, text, and reference GIFs. Prefer a fast local image-to-GIF path, analyze references before imitating a style, and always validate the saved GIF by reading it back.

## Hard Rules

- Do not use video generation, image-to-video models, MP4, MOV, or video transcode workflows.
- Do not upload user images to external services unless the user explicitly asks for an AI-generated or cloud-assisted visual and understands the upload.
- Do not stop after rendering. Re-open the final GIF and report actual dimensions, frame count, duration, and file size.
- Ask only when a missing source image, missing output target, or external upload permission blocks progress.
- Preserve Korean captions. Use CJK-capable fonts and automatic wrapping/fit checks.

## Mode Selection

- **quick**: one good GIF from an image and optional text. Default for vague requests.
- **reference**: analyze an existing GIF first, then match its size, timing, caption zone, and motion intensity.
- **pack**: create 3-4 reaction variants when the user asks for a set, stickers, or multiple moods.
- **optimize**: validate, resize, caption, or reduce an existing GIF without changing the concept.

Read `references/recipes.md` for preset choices and `references/quality-checks.md` before final delivery or repair.

## Quick Workflow

1. Resolve inputs: source image(s), optional text, optional reference GIF, target use such as chat/sticker/web.
2. If there is a reference GIF, run `scripts/analyze_reference_gif.py` and use the emitted `style_recipe`.
3. Pick a conservative canvas and preset. Default to `caption-pop` for text-heavy chat GIFs.
4. Render with `scripts/render_gif.py`.
5. Create a contact sheet with `scripts/make_contact_sheet.py` when the user will review timing or style.
6. Validate with `scripts/validate_gif.py --json`.
7. If validation fails, repair the smallest axis: frame count, duration, caption fit, canvas, or file size.
8. Return output path(s), dimensions, frame count, duration, and file size. Keep commentary short.

## Script Usage

Install the single runtime dependency if Pillow is missing:

```bash
python -m pip install -r <skill-dir>/requirements.txt
```

Create a GIF from one image:

```bash
python <skill-dir>/scripts/render_gif.py --image input.png --text "퇴근하고 싶다" --output outputs/reaction.gif --preset caption-pop --width 512 --height 512 --duration 1.8 --report outputs/reaction.json
```

Analyze a reference GIF:

```bash
python <skill-dir>/scripts/analyze_reference_gif.py --input reference.gif --json-output outputs/reference-analysis.json
```

Validate the final GIF:

```bash
python <skill-dir>/scripts/validate_gif.py --input outputs/reaction.gif --json
```

Make a contact sheet:

```bash
python <skill-dir>/scripts/make_contact_sheet.py --input outputs/reaction.gif --output outputs/reaction-sheet.png --columns 4
```

## Defaults

- Chat/sticker GIF: 512x512, 1.4-2.0 seconds, 8-14 frames.
- Wide meme GIF: keep reference aspect ratio or use 800x450.
- Caption: bottom zone, white rounded panel, dark text, fitted to 1-3 lines.
- Presets: `caption-pop`, `gentle-zoom`, `shake`, `bounce`, `polaroid`.
- Output folder: `outputs/` under the current project unless the user gives another path.

## Repair Loop

When quality is weak:

- Text clipped: reduce font size, shorten line width, or move caption zone.
- Motion too static: switch to `gentle-zoom`, `bounce`, or `shake`.
- Too chaotic: lower duration, use `caption-pop`, or reduce canvas motion.
- File too large: reduce canvas, frames, or duration; then validate again.
- Loop pops: make first and last frames visually closer or use a hold on the final frame.
- Reference mismatch: re-run analysis and copy its canvas/timing before changing the art direction.
