# Photoreal Action GIF Recipes

Use this when a still image prompt asks for a realistic action, expression, or pose that is not already present in the source image.

## Route

- Plan mode: `photoreal`
- Visual strategy: `photoreal_still_edit_keyframes`
- Required consent: `--allow-upload`
- Output type: GIF only
- Forbidden workflow: video generation, MP4/MOV/WebM, image-to-video

## When To Use

Use this lane for prompts like:

- "아빠가 딸에게 뽀뽀하려는데 딸이 싫어하는 영상"
- "사진 속 사람이 놀라서 뒤로 피하는 장면"
- "원본 사진의 아이가 웃다가 싫어하는 표정으로 바뀌는 움짤"
- "실제처럼 자연스럽게 표정과 몸동작이 바뀌는 GIF"

These prompts require new pose/expression/action edits. Do not fake them with local overlays.

## Required Prompt Constraints

Every keyframe edit prompt must include:

- Same people and identities.
- Same clothing, lighting, camera angle, and background.
- No duplicate people.
- No extra child or parent.
- No clone, ghost, double exposure, or second version of a person.
- No cartoon overlay, speech bubble, or text as a substitute for the real action.
- No video workflow.

## Affection Rejection Sequence

For "father tries to kiss daughter, daughter dislikes it":

1. Setup: same father and daughter, father close, daughter notices.
2. Approach: father gently leans in, daughter starts turning away.
3. Rejection readable: daughter pulls face/body away.
4. Comic peak: daughter's dislike is clear through natural expression/body language.
5. Settle: father pauses awkwardly, daughter still avoids the kiss.

## QA Bar

Reject the result if any of these are visible:

- A duplicated daughter or father.
- A new person not present in the source.
- The daughter looks like she accepts the kiss.
- The action is only represented by a caption or sticker.
- The background or identities drift between frames.
- It looks like a collage rather than a real sequence.
