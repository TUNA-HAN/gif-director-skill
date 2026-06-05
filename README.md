# GIF Director Skill

Portable Agent Skill for production-quality non-video GIF creation from images, Korean captions, marketing copy, reference GIFs, and sprite sheets.

Repo:

```text
https://github.com/TUNA-HAN/gif-director-skill
```

## Install With One Prompt

Send this to Codex, Claude Code, Antigravity, or another agent that can install Agent Skills:

```text
Install this Agent Skill from GitHub:
https://github.com/TUNA-HAN/gif-director-skill/tree/main/skills/gif-director
```

## GitHub CLI Install

```bash
gh skill install TUNA-HAN/gif-director-skill gif-director --agent codex --scope user
gh skill install TUNA-HAN/gif-director-skill gif-director --agent claude-code --scope user
gh skill install TUNA-HAN/gif-director-skill gif-director --agent antigravity --scope user
```

## Claude Code Marketplace Install

```text
/plugin marketplace add TUNA-HAN/gif-director-skill
/plugin install gif-director@gif-director-skills
```

## What It Supports

- Image + Korean/text caption to GIF.
- Multiple images to sequence/detail-page GIF.
- Reference GIF analysis before style matching.
- Marketing/detail-page GIF generation.
- Four-output reaction/sticker packs.
- 4x4 sprite sheet to 16-frame GIF.
- Deterministic still-image sprite motion.
- Optional Gemini still-image sprite sheet generation with explicit upload consent.
- Contact sheet generation.
- Saved GIF readback validation.
- GIF optimization with Pillow fallback and optional `gifski`/`ffmpeg` encoders.
- No video generation and no MP4 workflow.

## Runtime

Required:

```bash
python -m pip install -r skills/gif-director/requirements.txt
```

Optional AI still-image sprite sheet generation:

```bash
python -m pip install -r skills/gif-director/requirements-ai.txt
```

## Main Commands

Quick GIF:

```bash
python skills/gif-director/scripts/gif_director.py --mode quick --image input.png --text "퇴근하고 싶다" --output-dir outputs --base-name reaction
```

Natural-language prompt:

```bash
python skills/gif-director/scripts/gif_director.py --prompt "상세페이지 중간에 넣을 런칭 특가 GIF. 고급스럽고 너무 정신없지 않게." --image product.png --output-dir outputs --base-name planned-detail
```

Marketing/detail-page GIF:

```bash
python skills/gif-director/scripts/gif_director.py --mode marketing --image product1.png --image product2.png --text "런칭 특가" --preset detail-page --output-dir outputs --base-name detail-hero
```

Sticker pack:

```bash
python skills/gif-director/scripts/gif_director.py --mode pack --image input.png --output-dir outputs --base-name campaign
```

Sprite GIF:

```bash
python skills/gif-director/scripts/render_sprite_gif.py --sprite-sheet sprite_4x4.png --output outputs/sprite.gif --report outputs/sprite.json
```

Optimize:

```bash
python skills/gif-director/scripts/optimize_gif.py --input outputs/detail-hero.gif --output outputs/detail-hero-small.gif --report outputs/detail-hero-small.json --max-width 720 --max-frames 14
```
