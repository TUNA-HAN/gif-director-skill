# GIF Director Skill

Portable `SKILL.md` package for creating polished non-video GIFs from images, Korean captions, text prompts, and reference GIFs.

## Install With One Prompt

Send this to Codex, Claude Code, Antigravity, or another agent that can install Agent Skills:

```text
Install this Agent Skill from GitHub:
https://github.com/TUNA-HAN/gif-director-skill/tree/main/skills/gif-director
```

The skill itself lives at:

```text
skills/gif-director/SKILL.md
```

## GitHub CLI Install

GitHub CLI 2.93+ supports `gh skill install` for Claude Code, Codex, Antigravity, and other agents.

```bash
gh skill install TUNA-HAN/gif-director-skill gif-director --agent codex --scope user
gh skill install TUNA-HAN/gif-director-skill gif-director --agent claude-code --scope user
gh skill install TUNA-HAN/gif-director-skill gif-director --agent antigravity --scope user
```

## Claude Code Marketplace Install

Claude Code can also install this repo as a plugin marketplace:

```text
/plugin marketplace add TUNA-HAN/gif-director-skill
/plugin install gif-director@gif-director-skills
```

## Runtime Dependency

The bundled scripts use Pillow only:

```bash
python -m pip install -r skills/gif-director/requirements.txt
```

## What It Does

- Image + caption to GIF.
- Reference GIF analysis before style matching.
- Korean/CJK caption wrapping and fit checks.
- Contact sheet generation.
- Saved GIF readback validation.
- No video generation, no MP4 workflow.
