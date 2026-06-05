# GIF Director Quality Checks

This legacy reference is kept for compatibility. Prefer `quality-rubric.md` for current service-quality checks.

Before final delivery, validate the final file rather than the intended frame list.

## Required Readback

Run:

```bash
python <skill-dir>/scripts/validate_gif.py --input <output.gif> --json
```

Check:

- `ok` is true.
- `frame_count` is at least 2 and normally 8-14 for short chat GIFs.
- `duration_ms` is nonzero and matches the intended feeling.
- `changed_transitions` is greater than 0 unless the user asked for a static hold.
- `file_size_bytes` is reasonable for the target.
- `blank_frames` is 0.

## Visual QA

Create a contact sheet when subjective timing matters:

```bash
python <skill-dir>/scripts/make_contact_sheet.py --input <output.gif> --output <output-sheet.png>
```

Inspect whether:

- The first frame explains the subject.
- The caption is readable and not clipped.
- Korean text uses a real CJK font where available.
- The main subject is not hidden by the caption.
- The loop does not jump harshly unless the joke needs it.

## No-Video Boundary

Allowed:

- GIF input analysis.
- Image-to-GIF rendering.
- PNG/JPG/WebP still images as inputs.
- Optional external still-image generation only with user consent.

Forbidden:

- Image-to-video generation.
- MP4/MOV/WebM generation.
- MP4-to-GIF conversion as the main workflow.
