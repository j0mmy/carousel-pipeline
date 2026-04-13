"""
[EPISODE NAME] — Captions
==========================
Copy this file to assets/captions/[episode-name].py
Edit the FRAMES list for your episode.
See references/captions-schema.md for full overlay schema.
"""

import os

# Font path — resolves to assets/fonts/ relative to this file
_FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")

FRAMES = [

    # ── Frame 1: Hook ────────────────────────────────────────────
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

    # ── Frame 2: Body ────────────────────────────────────────────
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

    # ── Frame 3: No text ─────────────────────────────────────────
    {
        "file": "FRAME_03.png",
        "overlays": []
    },

    # ── Frame 4: Stylized single word ────────────────────────────
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

    # ── Frame 5: Emotional peak ───────────────────────────────────
    {
        "file": "FRAME_05.png",
        "overlays": [
            {
                "text":       "save-worthy line here",
                "position":   "bottom",
                "style":      "body",
                "color":      "gold",
                "scrim":      True,
                "scrim_side": "bottom",
            }
        ]
    },

    # ── Frame 6: Closer + CTA ────────────────────────────────────
    # Two overlays: closer at top (special font), CTA at bottom
    {
        "file": "FRAME_06.png",
        "overlays": [
            {
                "text":       "closing line here",
                "position":   "top",
                "style":      "closer",
                "color":      "gold_bold",
                "scrim":      True,
                "scrim_side": "top",
                "font":       _FONTS + "/Oi-Regular.ttf",  # remove to use default
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
