---
name: carousel-overlay
description: >
  Composites text overlays onto carousel reel frames for Instagram.
  Use this skill whenever the user provides new animation frames and wants
  captions added, or asks to run the carousel overlay pipeline, or says
  things like "add text to these frames", "caption these slides", "run
  the overlay system", "new episode captions", or "process these frames
  for posting". Also trigger when the user wants to change copy, fonts,
  colors, or contrast settings for an existing carousel. This skill
  manages the full pipeline: reading frames, compositing styled text with
  IG safe zone enforcement, wrapping copy to 60% width, fixed subtitle
  anchors, and outputting production-ready PNGs. Always use this skill
  rather than writing one-off Pillow code.
---

# Carousel Overlay Skill

Composites styled text onto 9:16 carousel reel frames. Handles IG safe
zones, subtitle stability (fixed Y anchors), 60% line width cap,
wrap-first-then-shrink logic, modular fonts/colors/contrast, and
per-overlay font overrides.

## File map

```
carousel-overlay/
├── SKILL.md                        ← you are here
├── scripts/
│   ├── overlay_engine.py           ← core renderer — never edit directly
│   └── run.sh                      ← one-command runner
├── references/
│   ├── stylesheet-guide.md         ← all tunable design tokens explained
│   ├── captions-schema.md          ← full overlay schema + examples
│   └── reading-ux-principles.md    ← why the system is designed this way
└── assets/
    ├── fonts/                      ← drop .ttf files here
    │   ├── BlackHanSans-Regular.ttf
    │   ├── Danfo-Regular-VariableFont_ELSH.ttf
    │   └── Oi-Regular.ttf
    ├── stylesheet.py               ← global design tokens (edit this)
    └── captions/
        └── [episode-name].py       ← per-episode copy config (create one per episode)
```

## Workflow — every new episode

**Step 1 — Create a captions file**

Copy `assets/captions/template.py` to `assets/captions/[episode-name].py`.
Edit the copy, positions, colors, and styles for each frame.
Read `references/captions-schema.md` for the full overlay schema.

**Step 2 — Run the renderer**

```bash
bash scripts/run.sh \
  --input  /path/to/frame/images \
  --output /path/to/output \
  --captions assets/captions/[episode-name].py
```

Or call the engine directly:

```bash
python scripts/overlay_engine.py \
  --input  /path/to/frames \
  --output /path/to/output \
  --captions assets/captions/[episode-name].py
```

**Step 3 — QA**

Enable safe zone guide for a quick visual check:
```python
# In stylesheet.py, temporarily set:
SHOW_SAFE_ZONE_GUIDE = True
```
Re-run, check the output, then set back to `False`.

---

## When the user wants to change visual style

Edit `assets/stylesheet.py`. The three swap points are:

| What to change | Where |
|---|---|
| Fonts | `FONT_PRIMARY`, `FONT_STYLIZED`, `FONT_CTA` paths |
| Colors | `COLOR` dict — add/edit named entries |
| Contrast method | `TEXT_CONTRAST["method"]` — stroke / dual_shadow / halo_shadow / stroke_shadow |
| Text size | `FONT_SIZE` dict per style key |
| Line width cap | `LAYOUT["line_width_pct"]` (default 0.60) |
| Subtitle Y anchor | `LAYOUT["anchor_bottom_pct"]` and `"anchor_top_pct"]` |
| IG safe zones | `IG_SAFE` dict |

Read `references/stylesheet-guide.md` for full explanation of every token.

---

## When the user wants to change copy only

Edit the relevant `assets/captions/[episode-name].py`. Never touch
`overlay_engine.py`. Re-run Step 2.

---

## Design rules encoded in this system

Read `references/reading-ux-principles.md` for the full rationale.
Short version:

- **Bottom anchor by default.** All non-stylized text sits at a fixed Y
  (76% from top). Reader's eye parks there after frame 2 and stops hunting.
- **60% line width.** Keeps lines to 1–2 eye fixations on mobile. Longer
  copy wraps to a second line at the same font size.
- **Wrap first, shrink last.** Font size never changes unless wrapping still
  produces 3+ lines. Shrinking is a last resort.
- **Max 2 lines.** Hard cap. If copy needs 3 lines, the copy is too long.
- **Stylized frames are exceptions.** `position: "middle"` + `stylized: True`
  bypasses the fixed anchor and uses editorial 58% placement. These frames
  are compositional, not informational.

---

## Per-overlay font override

To use a different font on a single overlay (e.g. Oi for a closer):

```python
{
    "text":     "still here. still you.",
    "position": "top",
    "style":    "closer",
    "color":    "gold_bold",
    "scrim":    True,
    "scrim_side": "top",
    "font":     "assets/fonts/Oi-Regular.ttf",   # ← override
}
```

---

## Adding a new episode — Claude Code checklist

1. Read the storyboard or frame descriptions the user provides
2. Create `assets/captions/[episode-name].py` using the schema in
   `references/captions-schema.md`
3. Confirm copy with user before rendering
4. Run `scripts/run.sh` with correct `--input`, `--output`, `--captions`
5. Check output frames — verify no bleed, correct anchor positions
6. If user requests style changes, edit `stylesheet.py` and re-run
7. Deliver output frames to user

---

## Dependencies

```
Pillow>=10.0
emoji>=2.0
Python>=3.10
```

Install: `pip install Pillow emoji`
