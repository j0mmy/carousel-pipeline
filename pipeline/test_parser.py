"""
Validates parser output against the hand-written comparison-spiral.py captions.

Checks that every overlay field matches (text, position, style, color, scrim,
scrim_side, stylized, contrast). Font paths and filenames differ by design
(old uses COMPARISON_N.png, new uses FRAME_NN.png) — those are noted but not
treated as failures.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.parse_storyboard import parse_storyboard

# Load hand-written captions
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "carousel-overlay", "assets", "captions"))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "comparison_spiral",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "carousel-overlay", "assets", "captions", "comparison-spiral.py")
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
EXPECTED = mod.FRAMES

# Parse storyboard
result = parse_storyboard(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "episodes", "comparison-spiral", "storyboard.md")
)

# Build overlay list from parser
from pipeline.parse_storyboard import _frame_to_overlays
parsed_frames = []
for f in result.frames:
    parsed_frames.append({
        "file": f.filename,
        "overlays": _frame_to_overlays(f),
    })

# Compare
SKIP_KEYS = {"file", "font"}  # filenames differ by design, font paths differ in structure
CHECK_KEYS = {"text", "position", "style", "color", "scrim", "scrim_side", "stylized", "contrast"}

errors = 0
notes = 0

for i in range(min(len(EXPECTED), len(parsed_frames))):
    exp = EXPECTED[i]
    got = parsed_frames[i]

    # Note filename difference
    if exp["file"] != got["file"]:
        print(f"  [note] Frame {i+1}: filename {exp['file']} -> {got['file']} (expected, new convention)")
        notes += 1

    exp_overlays = exp.get("overlays", [])
    got_overlays = got.get("overlays", [])

    if len(exp_overlays) != len(got_overlays):
        print(f"  [FAIL] Frame {i+1}: overlay count mismatch: expected {len(exp_overlays)}, got {len(got_overlays)}")
        errors += 1
        continue

    for j in range(len(exp_overlays)):
        eo = exp_overlays[j]
        go = got_overlays[j]

        for key in CHECK_KEYS:
            exp_val = eo.get(key)
            got_val = go.get(key)
            if exp_val != got_val:
                # Allow None vs missing — both mean "not set"
                if exp_val is None and got_val is None:
                    continue
                print(f"  [FAIL] Frame {i+1} overlay {j+1}: {key}: expected {exp_val!r}, got {got_val!r}")
                errors += 1

        # Note font differences (structural, not semantic)
        if "font" in eo or "font" in go:
            exp_font = eo.get("font", "(none)")
            got_font = go.get("font", "(none)")
            if "Oi-Regular" in str(exp_font) and "Oi-Regular" in str(got_font):
                print(f"  [note] Frame {i+1} overlay {j+1}: font both reference Oi-Regular (path format differs)")
                notes += 1
            elif exp_font != got_font:
                print(f"  [FAIL] Frame {i+1} overlay {j+1}: font mismatch: {exp_font!r} vs {got_font!r}")
                errors += 1

if len(EXPECTED) != len(parsed_frames):
    print(f"  [FAIL] Frame count mismatch: expected {len(EXPECTED)}, got {len(parsed_frames)}")
    errors += 1

print(f"\n{'PASS' if errors == 0 else 'FAIL'} — {errors} errors, {notes} notes")
sys.exit(0 if errors == 0 else 1)
