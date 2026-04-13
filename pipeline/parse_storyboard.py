"""
Storyboard Parser
==================
Parses a unified storyboard markdown file into:
  A) Shot list  — for the keyframes generation skill
  B) Captions config — for the overlay engine (carousel-overlay)

Usage:
  from pipeline.parse_storyboard import parse_storyboard

  result = parse_storyboard("episodes/comparison-spiral/storyboard.md")
  result.frontmatter   # dict: project, episode, aspect, model, frame_count
  result.shots         # list of shot dicts for keyframes skill
  result.captions_py   # string: valid Python source for captions.py

CLI:
  python -m pipeline.parse_storyboard episodes/comparison-spiral/storyboard.md
  python -m pipeline.parse_storyboard storyboard.md --write-captions episodes/ep/captions.py
"""

from __future__ import annotations

import re
import sys
import argparse
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional


# ─── Storyboard field patterns ──────────────────────────────────

_RE_FRAME_HEADER = re.compile(
    r"^##\s+FRAME_(\d+)\s*(?:—|--|-)\s*(.+)$", re.IGNORECASE
)
_RE_FIELD = re.compile(
    r"^\*\*(\w+):\*\*\s*(.*)$"
)

# Strip surrounding quotes from field values
def _unquote(val: str) -> str:
    val = val.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
        return val[1:-1]
    return val


# ─── Data structures ────────────────────────────────────────────

@dataclass
class FrameSpec:
    """Parsed representation of one frame from the storyboard."""
    number: int           # e.g. 1, 2, 10
    slug: str             # e.g. "hook", "breathe-stylized"
    prompt: str           # image generation prompt
    caption: str = ""     # overlay text (empty = no overlay)
    style: str = "body"
    position: str = ""    # "" means use default derivation
    color: str = "white"
    font: str = ""        # font filename override (e.g. "Oi-Regular.ttf")
    contrast: str = ""    # contrast method override
    scrim: str = ""       # explicit scrim override ("true"/"false"), "" = auto
    cta: str = ""         # CTA text for second overlay

    @property
    def frame_id(self) -> str:
        return f"FRAME_{self.number:02d}"

    @property
    def filename(self) -> str:
        return f"{self.frame_id}.png"


@dataclass
class StoryboardResult:
    """Complete parsed storyboard."""
    frontmatter: dict = field(default_factory=dict)
    frames: list[FrameSpec] = field(default_factory=list)

    @property
    def shots(self) -> list[dict]:
        """Shot list for keyframes skill."""
        return [
            {
                "frame_id": f.frame_id,
                "slug": f.slug,
                "prompt": f.prompt,
            }
            for f in self.frames
        ]

    @property
    def captions_py(self) -> str:
        """Generate a valid captions .py file for the overlay engine."""
        return _generate_captions_py(self)


# ─── Frontmatter parsing ────────────────────────────────────────

def _parse_frontmatter(lines: list[str]) -> tuple[dict, int]:
    """Parse YAML-like frontmatter between --- delimiters. Returns (dict, end_line_index)."""
    fm = {}
    if not lines or lines[0].strip() != "---":
        return fm, 0

    end = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break

    if end == -1:
        return fm, 0

    for line in lines[1:end]:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            fm[key.strip()] = _unquote(val.strip())

    return fm, end + 1


# ─── Frame parsing ──────────────────────────────────────────────

def _parse_frames(lines: list[str]) -> list[FrameSpec]:
    """Parse frame sections from storyboard body."""
    frames: list[FrameSpec] = []
    current = None  # type: FrameSpec or None

    for line in lines:
        line_stripped = line.strip()

        # Check for frame header
        m = _RE_FRAME_HEADER.match(line_stripped)
        if m:
            if current is not None:
                frames.append(current)
            current = FrameSpec(
                number=int(m.group(1)),
                slug=m.group(2).strip(),
                prompt="",
            )
            continue

        if current is None:
            continue

        # Check for field
        m = _RE_FIELD.match(line_stripped)
        if m:
            key = m.group(1).lower()
            val = _unquote(m.group(2))

            if key == "prompt":
                current.prompt = val
            elif key == "caption":
                current.caption = val
            elif key == "style":
                current.style = val
            elif key == "position":
                current.position = val
            elif key == "color":
                current.color = val
            elif key == "font":
                current.font = val
            elif key == "contrast":
                current.contrast = val
            elif key == "scrim":
                current.scrim = val.lower()
            elif key == "cta":
                current.cta = val

    if current is not None:
        frames.append(current)

    return frames


# ─── Captions .py generation ────────────────────────────────────

def _generate_captions_py(result: StoryboardResult) -> str:
    """Generate a valid Python captions file from parsed storyboard."""
    episode = result.frontmatter.get("episode", "untitled")
    lines = []
    lines.append('import os')
    lines.append(f'"""')
    lines.append(f'{episode} — Captions (auto-generated from storyboard.md)')
    lines.append(f'"""')
    lines.append('')
    lines.append('_FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),')
    lines.append('                      "..", "..", "carousel-overlay", "assets", "fonts")')
    lines.append('')
    lines.append('FRAMES = [')

    for f in result.frames:
        lines.append('')
        lines.append(f'    # ── Frame {f.number}: {f.slug} ' + '─' * max(1, 50 - len(f.slug)) + '')

        overlays = _frame_to_overlays(f)

        if not overlays:
            lines.append('    {')
            lines.append(f'        "file": "{f.filename}",')
            lines.append(f'        "overlays": []')
            lines.append('    },')
        else:
            lines.append('    {')
            lines.append(f'        "file": "{f.filename}",')
            lines.append(f'        "overlays": [')
            for ov in overlays:
                lines.append('            {')
                for k, v in ov.items():
                    if isinstance(v, str):
                        lines.append(f'                "{k}": {_py_repr(v)},')
                    elif isinstance(v, bool):
                        lines.append(f'                "{k}": {v},')
                lines.append('            },')
            lines.append('        ]')
            lines.append('    },')

    lines.append('')
    lines.append(']')
    lines.append('')
    return '\n'.join(lines)


def _frame_to_overlays(f: FrameSpec) -> list[dict]:
    """Convert a FrameSpec to a list of overlay dicts matching the captions schema."""
    if not f.caption:
        return []

    overlays = []

    # Main overlay
    ov = {}
    ov["text"] = f.caption

    # Position derivation
    if f.position:
        ov["position"] = f.position
    elif f.style == "stylized":
        ov["position"] = "middle"
    else:
        ov["position"] = "bottom"

    ov["style"] = f.style
    ov["color"] = f.color

    # Scrim derivation
    if f.scrim == "false":
        ov["scrim"] = False
    else:
        ov["scrim"] = True
        # scrim_side matches position for top/bottom, defaults to bottom for middle
        if ov["position"] == "top":
            ov["scrim_side"] = "top"
        else:
            ov["scrim_side"] = "bottom"

    # Stylized flag
    if f.style == "stylized":
        ov["stylized"] = True

    # Optional overrides
    if f.contrast:
        ov["contrast"] = f.contrast

    if f.font:
        ov["font"] = f'_FONTS + "/{f.font}"'

    overlays.append(ov)

    # CTA second overlay
    if f.cta:
        cta_ov = {
            "text": f.cta,
            "position": "bottom",
            "style": "cta",
            "color": "white",
            "scrim": True,
            "scrim_side": "bottom",
        }
        overlays.append(cta_ov)

    return overlays


def _py_repr(val: str) -> str:
    """Python string repr, but use _FONTS reference for font paths."""
    if val.startswith('_FONTS + '):
        return val  # already a code expression
    return f'"{val}"'


# ─── Main entry point ───────────────────────────────────────────

def parse_storyboard(path: str) -> StoryboardResult:
    """Parse a unified storyboard file and return structured result."""
    with open(path, "r") as f:
        raw_lines = f.read().splitlines()

    frontmatter, body_start = _parse_frontmatter(raw_lines)
    frames = _parse_frames(raw_lines[body_start:])

    return StoryboardResult(frontmatter=frontmatter, frames=frames)


def write_captions(result: StoryboardResult, output_path: str):
    """Write the generated captions.py to disk."""
    with open(output_path, "w") as f:
        f.write(result.captions_py)


# ─── CLI ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Parse a unified storyboard file")
    parser.add_argument("storyboard", help="Path to storyboard.md")
    parser.add_argument("--write-captions", metavar="PATH",
                        help="Write generated captions.py to this path")
    parser.add_argument("--print-shots", action="store_true",
                        help="Print shot list (for keyframes skill)")
    parser.add_argument("--print-captions", action="store_true",
                        help="Print generated captions.py to stdout")
    args = parser.parse_args()

    result = parse_storyboard(args.storyboard)

    print(f"Parsed: {len(result.frames)} frames")
    print(f"Project: {result.frontmatter.get('project', '?')}")
    print(f"Episode: {result.frontmatter.get('episode', '?')}")

    if args.print_shots:
        print("\n--- Shot List ---")
        for s in result.shots:
            print(f"  {s['frame_id']} ({s['slug']}): {s['prompt'][:80]}...")

    if args.print_captions or args.write_captions:
        captions = result.captions_py

        if args.print_captions:
            print("\n--- Captions .py ---")
            print(captions)

        if args.write_captions:
            write_captions(result, args.write_captions)
            print(f"\nWrote captions to: {args.write_captions}")


if __name__ == "__main__":
    main()
