# Marketing Intent Recipes

Use this after `scripts/plan_gif.py` when the plan target is `detail-page`, `ad-banner`, or another business-facing surface.

| Intent | Best target | Caption role | Motion | Default caption | QA emphasis |
| --- | --- | --- | --- | --- | --- |
| `launch_offer` | detail-page/ad-banner | offer | subtle `detail-page` or balanced `pulse` | 런칭 특가 | offer visible in first loop |
| `feature_highlight` | detail-page | benefit | `slide` or `detail-page` | 포인트 체크 | product not covered by caption |
| `review_trust` | detail-page | trust | `gentle-zoom` | 만족 후기 | readable, calm loop |
| `social_proof` | detail-page/ad-banner | proof | `caption-pop` | 완전 추천 | text prominence |
| `urgency` | ad-banner/detail-page | cta | `pulse` | 오늘만 | short duration and strong CTA |
| `product_demo` | detail-page | explanation | `slide` or `polaroid` | 한눈에 보기 | sequence clarity |
| `reaction_pack` | sticker-pack | reaction | `bounce`, `pulse`, `wiggle` | mixed | four outputs distinct |

## Practical Defaults

- Detail-page inserts should feel useful inside commerce content, not like a full ad takeover.
- Premium/subtle prompts should reduce motion first, not shrink text first.
- Urgency prompts should stay short; do not add extra captions unless requested.
- Review/trust prompts should avoid explosive effects.
- Product demo prompts should favor sequence clarity over bounce.
- If the user provides a reference GIF, analyze it first and adapt timing/canvas before choosing a recipe.
