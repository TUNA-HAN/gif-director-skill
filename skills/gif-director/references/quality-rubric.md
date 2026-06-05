# Quality Rubric

Use this before final delivery for business-facing GIFs.

## Required Checks

- Run readback validation on the saved GIF.
- Create a contact sheet for marketing/detail-page, pack, reference-match, or subjective style work.
- Verify Korean captions are readable and not clipped.
- Verify the primary subject or offer is visible in the first frame.
- Verify no blank frames and at least one changed transition.
- Verify actual frame count, duration, dimensions, and file size.
- Preserve `*-plan.json` for prompt-driven work.
- Preserve `*-qa.json` when visual/readback QA is available.
- For photoreal action GIFs, inspect the contact sheet for duplicated people, identity drift, missing action readability, and fake overlay substitutes.

## Business Use Targets

| Target | Typical size | Timing | Notes |
| --- | --- | --- | --- |
| Chat/sticker | 512x512 | 1.4-2.0s | Caption readability first |
| Product detail page | 900x506 or 720x405 | 1.6-2.4s | Product and offer must be visible |
| Ad/social square | 1080x1080 or optimized smaller | 1.5-2.2s | Strong CTA or benefit |
| Lightweight web insert | <=720px wide | 1.2-1.8s | Optimize frame count and size |

## Repair Policy

Repair one failed axis at a time:

- Text clipped: reduce font, caption width, or move caption zone.
- Subject hidden: move caption or switch to detail-page layout.
- Too large: run `optimize_gif.py`, reduce width, reduce frames, or shorten duration.
- Too static: switch to `pulse`, `slide`, `bounce`, or `wiggle`.
- Too chaotic: switch to `gentle-zoom` or `caption-pop`.
- Loop pops: make first/last frames closer or hold final frame intentionally.
- Business intent wrong: rerun `plan_gif.py`, inspect `business_intent`, and adjust prompt routing before rendering again.
- Photoreal action request handled by local overlays: reroute to `photoreal_still_edit_keyframes`.
- Duplicate person visible: discard the result and regenerate keyframes with stronger `no duplicate subjects` constraints.
- Requested emotion/action not readable: discard the result and regenerate the failed keyframe, not the whole workflow.

## No-Video Boundary

Allowed:

- GIF input analysis.
- Still image to GIF.
- Multiple still images to GIF.
- 4x4 sprite-sheet to GIF.
- AI-edited still-image keyframes to GIF after explicit upload consent.
- Optional still-image sprite sheet generation after explicit upload consent.
- PNG-frame encoding via Pillow, gifski, or ffmpeg palette tools.

Forbidden:

- Image-to-video generation.
- MP4, MOV, or WebM generation.
- MP4-to-GIF conversion as the primary workflow.
- Pretending an AI still-image edit is local-only when a user image was uploaded.
