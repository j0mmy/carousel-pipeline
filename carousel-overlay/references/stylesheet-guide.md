# Stylesheet Guide

`assets/stylesheet.py` is the single source of truth for visual style.
Edit it to change anything globally. Per-overlay overrides in captions.py
always win over stylesheet defaults.

---

## FONTS

```python
FONT_PRIMARY  = "assets/fonts/BlackHanSans-Regular.ttf"  # hook / body / closer
FONT_STYLIZED = "assets/fonts/Danfo-Regular-VariableFont_ELSH.ttf"  # stylized frames
FONT_CTA      = "assets/fonts/BlackHanSans-Regular.ttf"  # small CTA lines
```

Swap any of these to change fonts globally. Drop the .ttf into `assets/fonts/`
and update the path. Any .ttf or .otf works.

**Current font choices:**
- **Black Han Sans** — heavy rounded grotesque. Feels like a kids cartoon
  caption. High legibility at large sizes. Used for all regular text.
- **Danfo** — soft rounded slab serif. Warm, slightly retro. Used for
  single-word emotional beats (BREATHE.).
- **Oi** — ornate display serif. Used for the final closer only.

---

## FONT_SIZE

```python
FONT_SIZE = {
    "hook":     130,   # scroll-stop opener
    "body":     110,   # mid-story lines
    "closer":   130,   # final payoff
    "stylized": 260,   # poster-weight single word — intentionally large
    "cta":       72,   # small handle / save prompt
}
```

Calibrated for **1536×2752** source images (9:16). If your source images
are a different resolution, scale all values by: `new_height / 2752`.

---

## COLOR

```python
COLOR = {
    "white":      (255, 255, 255, 255),
    "gold":       (255, 208, 106, 255),   # #FFD06A — emotional peak
    "gold_bold":  (255, 185,  60, 255),   # #FFB93C — closer / max contrast
    "muted":      (255, 255, 255, 200),   # subdued white for CTA
    "black":      (0,   0,   0,   255),
}
```

Add any named color here. Reference it by name in captions.py.
Example: `"color": "teal"` after adding `"teal": (80, 200, 180, 255)`.

**Color arc principle:** white on dark/desaturated frames, transitioning
to gold on emotional peaks. Gold text on light backgrounds = screenshot bait.

---

## TEXT_CONTRAST

```python
TEXT_CONTRAST = {
    "method":              "stroke",   # default contrast method
    "stroke_width":        7,
    "stroke_color":        (0, 0, 0, 255),
    "shadow_tight_offset": 4,
    "shadow_tight_alpha":  220,
    "shadow_wide_offset":  12,
    "shadow_wide_blur":    22,
    "shadow_wide_alpha":   190,
    "halo_blur":           16,
    "halo_alpha":          255,
}
```

**Method options:**

| Method | Best for | Notes |
|---|---|---|
| `"stroke"` | All Black Han Sans text | Clean outline, works on any background |
| `"dual_shadow"` | Editorial body text | Two shadow layers, professional depth |
| `"halo_shadow"` | Danfo stylized frames | Blurred glow wraps rounded letterforms |
| `"stroke_shadow"` | Hybrid | Thin stroke + soft shadow |

Override per overlay via `"contrast": "halo_shadow"` in captions.py.
Change `TEXT_CONTRAST["method"]` to change the global default.

---

## SCRIM

```python
SCRIM = {
    "opacity_max": 220,   # 0–255. Darkest edge of gradient.
    "height_pct":  0.38,  # fraction of frame height the scrim covers
}
```

The scrim is a gradient that darkens the edge of the frame behind text.
Top scrims darken top-down. Bottom scrims darken bottom-up. Increase
`opacity_max` for lighter source images.

---

## LAYOUT

```python
LAYOUT = {
    "line_width_pct":    0.60,   # max line width as % of frame width
    "padding_x_pct":     0.06,
    "padding_y_pct":     0.02,
    "line_spacing":      22,
    "max_chars":         28,     # soft pre-wrap before pixel measurement
    "max_lines":          2,     # hard cap — never more than 2 lines
    "anchor_top_pct":    0.12,   # fixed Y for all "top" overlays
    "anchor_bottom_pct": 0.76,   # fixed Y for all "bottom" overlays (bottom edge)
}
```

**anchor_bottom_pct** is the most important value in the system. It
determines where every bottom-positioned subtitle lands. If text feels
too high or too low on your frames, adjust this one number and all frames
update simultaneously.

---

## IG_SAFE

```python
IG_SAFE = {
    "top_clear_pct":    0.10,   # profile bar + back arrow
    "bottom_clear_pct": 0.18,   # caption, likes, nav bar
    "right_clear_pct":  0.18,   # like/comment/share/follow buttons
    "left_clear_pct":   0.04,
}
```

These are the Instagram Reels UI elements that overlay your content.
Text is constrained to stay inside these bounds automatically.
Set `SHOW_SAFE_ZONE_GUIDE = True` to render a visual debug overlay.
