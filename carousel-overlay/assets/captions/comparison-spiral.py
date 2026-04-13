import os
"""
GLY Carousel Overlay System — Captions Config
===============================================
POSITIONING PRINCIPLE:
  All non-stylized text uses "bottom" position by default.
  Fixed Y anchor = subtitle stability. Reader's eye parks at the bottom
  after frame 1 and never has to hunt again.

  Exceptions:
  - "middle" for stylized single-word moments (BREATHE.)
  - Frame 10 has two overlays: closer at top, CTA at bottom

OVERLAY SCHEMA:
  "text"      : string to display
  "position"  : "bottom" (default) | "top" | "middle" (stylized only)
  "style"     : "hook" | "body" | "closer" | "stylized" | "cta"
  "color"     : key from COLOR dict in stylesheet.py
  "font"      : optional path override — use for one-off font choices per overlay
  "scrim"     : True | False
  "scrim_side": "top" | "bottom"
  "stylized"  : True | False  — uses FONT_STYLIZED + stylized size
  "contrast"  : optional override — "stroke" | "dual_shadow" | "halo_shadow"
"""

_FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")

FRAMES = [

    # ── Frame 1: The hook ────────────────────────────────────────
    {
        "file": "COMPARISON_1.png",
        "overlays": [
            {
                "text":       "you before the scroll",
                "position":   "bottom",
                "style":      "hook",
                "color":      "white",
                "scrim":      True,
                "scrim_side": "bottom",
            }
        ]
    },

    # ── Frame 2: The drop ────────────────────────────────────────
    {
        "file": "COMPARISON_2.png",
        "overlays": [
            {
                "text":       "after 20 mins of their highlights",
                "position":   "bottom",
                "style":      "body",
                "color":      "white",
                "scrim":      True,
                "scrim_side": "bottom",
            }
        ]
    },

    # ── Frame 3: GLY arrives ─────────────────────────────────────
    {
        "file": "COMPARISON_3.png",
        "overlays": [
            {
                "text":       "GLY pulls up",
                "position":   "bottom",
                "style":      "hook",
                "color":      "white",
                "scrim":      True,
                "scrim_side": "bottom",
            }
        ]
    },

    # ── Frame 4: The offer ───────────────────────────────────────
    {
        "file": "COMPARISON_4.png",
        "overlays": [
            {
                "text":       "put the phone down for a sec",
                "position":   "bottom",
                "style":      "body",
                "color":      "white",
                "scrim":      True,
                "scrim_side": "bottom",
            }
        ]
    },

    # ── Frame 5: Breath 1 ────────────────────────────────────────
    {
        "file": "COMPARISON_5.png",
        "overlays": [
            {
                "text":       "breathe in",
                "position":   "bottom",
                "style":      "body",
                "color":      "white",
                "scrim":      True,
                "scrim_side": "bottom",
            }
        ]
    },

    # ── Frame 6: Breath 2 ────────────────────────────────────────
    {
        "file": "COMPARISON_6.png",
        "overlays": [
            {
                "text":       "breathe out",
                "position":   "bottom",
                "style":      "body",
                "color":      "white",
                "scrim":      True,
                "scrim_side": "bottom",
            }
        ]
    },

    # ── Frame 7: Save frame / emotional peak ─────────────────────
    {
        "file": "COMPARISON_7.png",
        "overlays": [
            {
                "text":       "one more time...",
                "position":   "bottom",
                "style":      "body",
                "color":      "gold",
                "scrim":      True,
                "scrim_side": "bottom",
            }
        ]
    },

    # ── Frame 8: Stylized moment — Danfo, editorial placement ────
    {
        "file": "COMPARISON_8.png",
        "overlays": [
            {
                "text":       "breathe.",
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

    # ── Frame 9: No text ─────────────────────────────────────────
    {
        "file": "COMPARISON_9.png",
        "overlays": []
    },

    # ── Frame 10: The closer ──────────────────────────────────────
    # "still here. still you." uses Oi — decorative, earned moment
    # CTA at bottom, closer at top (two anchors intentionally)
    {
        "file": "COMPARISON_10.png",
        "overlays": [
            {
                "text":       "still here. still you.",
                "position":   "top",
                "style":      "closer",
                "color":      "gold_bold",
                "scrim":      True,
                "scrim_side": "top",
                "font":       _FONTS + "/Oi-Regular.ttf",
            },
            {
                "text":       "save this for the next spiral",
                "position":   "bottom",
                "style":      "cta",
                "color":      "white",
                "scrim":      True,
                "scrim_side": "bottom",
            }
        ]
    },

]
