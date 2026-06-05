# GIF Director Recipes

Use these as starting points. Adjust after reading the actual image and any reference GIF.

## Presets

| Preset | Use for | Notes |
| --- | --- | --- |
| `caption-pop` | Korean captions, chat reactions, quick stickers | Conservative default. Caption appears after the image is established. |
| `gentle-zoom` | Product/photo emphasis, polished profile-style GIFs | Smooth and readable. Good when the image already carries the joke. |
| `shake` | Surprise, panic, "what?" reactions | Keep duration short to avoid visual fatigue. |
| `bounce` | Cute/light reactions | Works well for centered subjects and sticker-like crops. |
| `polaroid` | Reference GIFs with photo cards or collage feeling | Use when a reference has frames/cards or printed-photo styling. |

## Prompt Mapping

| User wording | Likely mode | Suggested default |
| --- | --- | --- |
| "움짤 만들어줘", "gif로" | quick | `caption-pop`, 512x512 |
| "이런 느낌으로" + GIF | reference | analyze first, then copy timing/canvas |
| "카톡용", "스티커" | quick or pack | square canvas, readable caption |
| "웃긴 짤", "리액션" | quick | `shake` or `caption-pop` |
| "귀엽게" | quick | `bounce`, softer caption |
| "여러 개" | pack | 3-4 variants with distinct captions or presets |

## Pack Defaults

For a reaction pack, create up to four GIFs unless the user asks for a different count:

- greeting or attention
- laugh or approval
- tired or sad
- love or celebration

Keep each output independently valid. Do not let one failed variant block the others; report failed variants separately.
