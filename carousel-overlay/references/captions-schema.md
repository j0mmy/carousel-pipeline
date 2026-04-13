# Captions Schema Reference

Every episode gets its own captions file in `assets/captions/`.
The renderer reads the `FRAMES` list and applies overlays in order.

---

## Frame object

```python
{
    "file":     "FRAME_01.png",    # source image filename (no path)
    "overlays": [ ... ]            # list of overlay objects (empty = no text)
}
```

---

## Overlay object — full schema

```python
{
    # REQUIRED
    "text":       "your copy here",

    # REQUIRED — positioning
    # "bottom" is the default for all non-stylized text (subtitle stability)
    # "top"    for intentional top placement (e.g. frame 10 closer)
    # "middle" for stylized single-word editorial frames only
    "position":   "bottom",

    # REQUIRED — maps to FONT_SIZE in stylesheet.py
    # "hook"      large punchy opener text
    # "body"      mid-story lines
    # "closer"    final emotional payoff
    # "stylized"  single-word oversized Danfo moments
    # "cta"       small handle / save prompt
    "style":      "body",

    # REQUIRED — key from COLOR dict in stylesheet.py
    # built-in: "white", "gold", "gold_bold", "muted", "black"
    "color":      "white",

    # OPTIONAL — gradient darkening behind text region
    "scrim":      True,
    "scrim_side": "bottom",   # "top" or "bottom"

    # OPTIONAL — use Danfo font + stylized size, bypass fixed Y anchor
    "stylized":   False,

    # OPTIONAL — per-overlay contrast method override
    # "stroke" | "dual_shadow" | "halo_shadow" | "stroke_shadow"
    # omit to use TEXT_CONTRAST["method"] from stylesheet.py
    "contrast":   "stroke",

    # OPTIONAL — per-overlay font path override
    # use for one-off font choices (e.g. Oi for a closer)
    # omit to use FONT_PRIMARY (or FONT_STYLIZED if stylized=True)
    "font":       "assets/fonts/Oi-Regular.ttf",
}
```

---

## Positioning rules

| Position | Y anchor | Use for |
|---|---|---|
| `"bottom"` | Fixed at `anchor_bottom_pct` (76%) | All regular text — default |
| `"top"` | Fixed at `anchor_top_pct` (12%) | Intentional top placement only |
| `"middle"` | Editorial 58% of safe zone height | Stylized single-word frames only |

**Subtitle stability:** every `"bottom"` overlay across every frame lands
at the exact same Y position. Reader's eye parks there after frame 2.
Never use `"top"` for regular copy — use it only when a frame intentionally
needs two overlays (top closer + bottom CTA).

---

## Copy rules

- **Max 4 words per line** at standard font sizes and 60% width budget
- **Max 2 lines** total — if copy wraps to 3 lines, shorten the copy
- Wrap happens automatically at pixel budget — no manual line breaks needed
- If wrapping still produces 3+ lines, font shrinks until it fits 2 lines
- **Stylized frames:** 1–2 words max (single word ideal). These are
  compositional, not informational.

---

## Template — copy-paste starter

```python
"""
[EPISODE NAME] — Captions
"""

_FONTS = "assets/fonts"   # update if your font path differs

FRAMES = [

    {
        "file": "FRAME_01.png",
        "overlays": [
            {
                "text":       "your hook line here",
                "position":   "bottom",
                "style":      "hook",
                "color":      "white",
                "scrim":      True,
                "scrim_side": "bottom",
            }
        ]
    },

    {
        "file": "FRAME_02.png",
        "overlays": [
            {
                "text":       "mid story line",
                "position":   "bottom",
                "style":      "body",
                "color":      "white",
                "scrim":      True,
                "scrim_side": "bottom",
            }
        ]
    },

    # No text frame:
    {
        "file": "FRAME_03.png",
        "overlays": []
    },

    # Stylized single-word frame:
    {
        "file": "FRAME_04.png",
        "overlays": [
            {
                "text":       "word.",
                "position":   "middle",
                "style":      "stylized",
                "color":      "gold",
                "scrim":      True,
                "scrim_side": "bottom",
                "stylized":   True,
                "contrast":   "stroke",
            }
        ]
    },

    # Two-overlay closer frame:
    {
        "file": "FRAME_05.png",
        "overlays": [
            {
                "text":       "closing line",
                "position":   "top",
                "style":      "closer",
                "color":      "gold_bold",
                "scrim":      True,
                "scrim_side": "top",
                "font":       _FONTS + "/Oi-Regular.ttf",  # optional override
            },
            {
                "text":       "save this for the next time",
                "position":   "bottom",
                "style":      "cta",
                "color":      "white",
                "scrim":      True,
                "scrim_side": "bottom",
            }
        ]
    },

]
```
