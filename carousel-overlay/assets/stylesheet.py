"""
GLY Carousel Overlay System — Stylesheet
=========================================
Global design tokens. Edit here to change the visual style
across all frames. Per-frame overrides live in captions.py.

MODULAR SYSTEM — three swap points:
  1. FONTS        → swap FONT_PRIMARY / FONT_STYLIZED paths
  2. CONTRAST     → change TEXT_CONTRAST["method"] and params
  3. COLORS       → add/edit entries in COLOR dict, reference by name in captions.py

To create a new theme: duplicate this file, rename it (e.g. stylesheet_dark.py),
and update the import line at the top of overlay_engine.py.
"""

import os

# Font paths are relative to this file's directory (assets/)
_HERE = os.path.dirname(os.path.abspath(__file__))
_FONTS = os.path.join(_HERE, "fonts")

FONT_PRIMARY  = os.path.join(_FONTS, "BlackHanSans-Regular.ttf")
FONT_STYLIZED = os.path.join(_FONTS, "Danfo-Regular-VariableFont_ELSH.ttf")
FONT_CTA      = os.path.join(_FONTS, "BlackHanSans-Regular.ttf")

# ─────────────────────────────────────────────────────────────────
# FONT SIZES  (px, calibrated for 1536x2752 / 9:16)
# Scale all values proportionally if your source images differ.
# ─────────────────────────────────────────────────────────────────

FONT_SIZE = {
    "hook":     130,
    "body":     110,
    "closer":   130,
    "stylized": 260,   # Danfo single-word moments — poster weight, intentionally large
    "cta":       72,
}

# ─────────────────────────────────────────────────────────────────
# COLORS  (R, G, B, A)
# Add any named color here, reference by name in captions.py.
# ─────────────────────────────────────────────────────────────────

COLOR = {
    "white":      (255, 255, 255, 255),
    "gold":       (255, 208, 106, 255),
    "gold_bold":  (255, 185,  60, 255),
    "muted":      (255, 255, 255, 200),
    "black":      (0,   0,   0,   255),
}

# ─────────────────────────────────────────────────────────────────
# TEXT CONTRAST
# Controls how text separates from the background.
#
# method options:
#   "stroke"        Clean outline. Default for Black Han Sans.
#   "dual_shadow"   Two shadow layers (wide soft + tight hard). Editorial depth.
#   "halo_shadow"   Blurred glow halo + tight shadow. Best for Danfo stylized.
#   "stroke_shadow" Thin stroke + soft shadow. Hybrid.
#
# Override per-overlay via "contrast" key in captions.py.
# ─────────────────────────────────────────────────────────────────

TEXT_CONTRAST = {
    "method":              "stroke",
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

TEXT_BACKING = TEXT_CONTRAST   # backward-compat alias

# ─────────────────────────────────────────────────────────────────
# SCRIM
# ─────────────────────────────────────────────────────────────────

SCRIM = {
    "opacity_max": 220,
    "height_pct":  0.38,
}

# ─────────────────────────────────────────────────────────────────
# TEXT LAYOUT
# ─────────────────────────────────────────────────────────────────
#
# READING UX PRINCIPLES ENCODED HERE:
#
# line_width_pct   — max line width as % of frame width.
#                    60% keeps lines to ~1-2 eye fixations on mobile.
#                    Anything wider forces saccades that break emotional flow.
#                    Stylized frames (BREATHE.) bypass this — they use full safe width.
#
# anchor_top_pct   — fixed Y position for ALL "top" overlays, every frame.
# anchor_bottom_pct— fixed Y position for ALL "bottom" overlays, every frame.
#                    Subtitle stability: reader's eye learns the location after
#                    frame 2 and stops hunting. Never deviate from these anchors
#                    for non-stylized text. Consistency > variety.
#
# max_lines        — hard cap at 2 lines. If copy needs 3, the copy is too long.
#
# ─────────────────────────────────────────────────────────────────

LAYOUT = {
    "line_width_pct":    0.60,   # max text line width as % of frame width
    "padding_x_pct":     0.06,   # horizontal inset from safe zone edge
    "padding_y_pct":     0.02,   # vertical inset — used only for stylized/middle
    "line_spacing":      22,     # px between wrapped lines
    "max_chars":         28,     # soft wrap — tightened to match 60% width budget
    "max_lines":          2,     # hard cap: never render more than 2 lines
    # Fixed Y anchors — % from top of frame. Applied to ALL non-stylized overlays.
    # Keeps text in the same place every frame. Reader's eye parks here.
    "anchor_top_pct":    0.12,   # top overlays always start here
    "anchor_bottom_pct": 0.76,   # bottom overlays always start here (text bottom edge)
}

# ─────────────────────────────────────────────────────────────────
# INSTAGRAM SAFE ZONES
# ─────────────────────────────────────────────────────────────────

IG_SAFE = {
    "top_clear_pct":    0.10,
    "bottom_clear_pct": 0.18,
    "right_clear_pct":  0.18,
    "left_clear_pct":   0.04,
}

SHOW_SAFE_ZONE_GUIDE = False

# ─────────────────────────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────────────────────────

OUTPUT = {
    "suffix":  "_captioned",
    "format":  "PNG",
    "quality": 95,
}
