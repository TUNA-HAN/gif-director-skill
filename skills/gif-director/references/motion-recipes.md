# Motion Recipes

Use this file when choosing motion for a user request.

For natural-language requests, run `scripts/plan_gif.py` first or apply the same routing. Do not jump straight from a vague prompt to rendering.

## Core Presets

| Preset | Use for | Avoid when |
| --- | --- | --- |
| `caption-pop` | Korean meme text, clear chat reactions | Image-only product showcases |
| `gentle-zoom` | Polished product/detail-page emphasis | Panic/surprise reactions |
| `shake` | Panic, surprise, "뭐야?" style reactions | Premium product visuals |
| `bounce` | Cute sticker-like motion | Formal B2B banners |
| `polaroid` | Photo-card/reference GIF styles | Tight product inspection |
| `pulse` | Offer highlight, ad badges, CTA emphasis | Long loops |
| `spin` | Playful sticker motion | Text-heavy marketing |
| `slide` | Detail-page reveal, before/after, sequence | Tiny square emoji |
| `wiggle` | Casual attention, tired/waiting reactions | Luxury branding |
| `explode` | Launch, sale, announcement | Subtle UX placements |
| `detail-page` | Product detail hero, campaign insert GIFs | Pure chat stickers |

## Prompt Routing

| User wording | Mode | Preset |
| --- | --- | --- |
| "카톡용", "스티커" | quick or pack | `bounce`, `caption-pop` |
| "상세페이지", "마케팅", "배너" | marketing | `detail-page`, `pulse`, `slide` |
| "이런 느낌" + GIF | reference | copy reference timing/canvas first |
| "캐릭터처럼 움직이게" | sprite | 4x4 sprite sheet or deterministic still animation |
| "런칭", "특가", "혜택" | marketing | `explode`, `pulse`, `detail-page` |
| "여러 감정" | pack | four reaction outputs |

## Pack Defaults

Create four outputs by default:

- `hello`: "확인했어요", `bounce`
- `laugh`: "좋아요", `pulse`
- `tired`: "잠깐만요", `wiggle`
- `love`: "완전 추천", `caption-pop`

Each output must validate independently. Report partial failures instead of hiding them.
