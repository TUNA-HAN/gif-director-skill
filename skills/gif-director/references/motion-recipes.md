# Motion Recipes

Use this file when choosing motion for a user request. For natural-language requests, run `scripts/plan_gif.py` first or apply the same routing. Do not jump straight from a vague prompt to rendering.

## Core Presets

| Preset | Use for | Avoid when |
| --- | --- | --- |
| `caption-pop` | Korean meme text, clear chat reactions, proof captions | Image-only product showcases |
| `gentle-zoom` | Polished product/detail-page emphasis, review/trust loops | Panic/surprise reactions |
| `shake` | Panic, surprise, deliberately chaotic reactions | Premium product visuals |
| `bounce` | Cute sticker-like motion and pack items | Formal B2B banners |
| `polaroid` | Photo-card/reference GIF styles and casual sequences | Tight product inspection |
| `pulse` | Offer highlight, ad badges, CTA emphasis | Long loops |
| `spin` | Playful sticker motion | Text-heavy marketing |
| `slide` | Detail-page reveal, before/after, multi-image sequence | Tiny square emoji |
| `wiggle` | Casual attention, tired/waiting reactions | Luxury branding |
| `explode` | Launch, sale, announcement when user asks for loud motion | Subtle UX placements |
| `detail-page` | Product detail hero, campaign insert GIFs, premium offer blocks | Pure chat stickers |

## Prompt Routing

| User wording | Mode | Preset |
| --- | --- | --- |
| "카톡", "스티커", "짤" | quick or pack | `bounce`, `caption-pop` |
| "상세페이지", "상품페이지", "제품페이지" | marketing | `detail-page`, `slide` |
| "광고", "배너", "인스타", "정사각" | marketing | `pulse`, `caption-pop` |
| "레퍼런스처럼", "참고 GIF처럼" | reference | copy reference timing/canvas first |
| "스프라이트", "캐릭터처럼", "16프레임" | sprite | 4x4 sprite sheet or deterministic still animation |
| "런칭", "특가", "혜택", "쿠폰" | marketing | `detail-page`, `pulse` |
| "오늘만", "마감", "임박", "CTA" | marketing | `pulse` |
| "후기", "만족", "재구매" | marketing | `gentle-zoom` |
| "여러 감정", "리액션팩", "4개" | pack | four reaction outputs |

## Pack Defaults

Create four outputs by default:

- `hello`: "확인했어요", `bounce`
- `laugh`: "좋아요", `pulse`
- `tired`: "잠깐만요", `wiggle`
- `love`: "완전 추천", `caption-pop`

Each output must validate independently. Report partial failures instead of hiding them.
