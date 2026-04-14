"""
Unit tests for pipeline/parse_storyboard.py
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.parse_storyboard import (
    parse_storyboard,
    write_captions,
    _unquote,
    _parse_frontmatter,
    _parse_frames,
    _frame_to_overlays,
    _py_repr,
    FrameSpec,
    StoryboardResult,
)


# ─── Helper ─────────────────────────────────────────────────────

def _write_tmp(content: str) -> str:
    """Write content to a temp file, return path."""
    fd, path = tempfile.mkstemp(suffix=".md")
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


# ─── _unquote ───────────────────────────────────────────────────

class TestUnquote(unittest.TestCase):
    def test_double_quotes(self):
        self.assertEqual(_unquote('"hello world"'), "hello world")

    def test_single_quotes(self):
        self.assertEqual(_unquote("'hello world'"), "hello world")

    def test_no_quotes(self):
        self.assertEqual(_unquote("hello world"), "hello world")

    def test_mismatched_quotes(self):
        self.assertEqual(_unquote('"hello\''), '"hello\'')

    def test_empty_string(self):
        self.assertEqual(_unquote(""), "")

    def test_whitespace_stripped(self):
        self.assertEqual(_unquote('  "value"  '), "value")

    def test_single_char(self):
        self.assertEqual(_unquote("x"), "x")

    def test_empty_quoted(self):
        self.assertEqual(_unquote('""'), "")


# ─── _parse_frontmatter ─────────────────────────────────────────

class TestParseFrontmatter(unittest.TestCase):
    def test_basic_frontmatter(self):
        lines = [
            "---",
            "project: glytoons",
            "episode: test-ep",
            "aspect: 9:16",
            "---",
            "# Body",
        ]
        fm, end = _parse_frontmatter(lines)
        self.assertEqual(fm["project"], "glytoons")
        self.assertEqual(fm["episode"], "test-ep")
        self.assertEqual(fm["aspect"], "9:16")
        self.assertEqual(end, 5)

    def test_quoted_values(self):
        lines = ["---", 'aspect: "9:16"', "---"]
        fm, end = _parse_frontmatter(lines)
        self.assertEqual(fm["aspect"], "9:16")

    def test_no_frontmatter(self):
        lines = ["# Just a heading", "Some text"]
        fm, end = _parse_frontmatter(lines)
        self.assertEqual(fm, {})
        self.assertEqual(end, 0)

    def test_unclosed_frontmatter(self):
        lines = ["---", "project: test", "no closing"]
        fm, end = _parse_frontmatter(lines)
        self.assertEqual(fm, {})
        self.assertEqual(end, 0)

    def test_empty_lines_in_frontmatter(self):
        lines = ["---", "project: test", "", "episode: ep1", "---"]
        fm, end = _parse_frontmatter(lines)
        self.assertEqual(fm["project"], "test")
        self.assertEqual(fm["episode"], "ep1")

    def test_comments_in_frontmatter(self):
        lines = ["---", "# comment", "project: test", "---"]
        fm, end = _parse_frontmatter(lines)
        self.assertEqual(fm["project"], "test")
        self.assertNotIn("#", fm)

    def test_empty_input(self):
        fm, end = _parse_frontmatter([])
        self.assertEqual(fm, {})
        self.assertEqual(end, 0)

    def test_colon_in_value(self):
        lines = ["---", "model: gemini-3.1-flash-image-preview", "---"]
        fm, end = _parse_frontmatter(lines)
        self.assertEqual(fm["model"], "gemini-3.1-flash-image-preview")


# ─── _parse_frames ──────────────────────────────────────────────

class TestParseFrames(unittest.TestCase):
    def test_single_frame(self):
        lines = [
            "## FRAME_01 — hook",
            '**prompt:** A test prompt here',
            '**caption:** "test caption"',
            '**style:** hook',
            '**color:** white',
        ]
        frames = _parse_frames(lines)
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0].number, 1)
        self.assertEqual(frames[0].slug, "hook")
        self.assertEqual(frames[0].prompt, "A test prompt here")
        self.assertEqual(frames[0].caption, "test caption")
        self.assertEqual(frames[0].style, "hook")
        self.assertEqual(frames[0].color, "white")

    def test_multiple_frames(self):
        lines = [
            "## FRAME_01 — first",
            '**prompt:** prompt one',
            '**caption:** "cap one"',
            "",
            "## FRAME_02 — second",
            '**prompt:** prompt two',
            '**caption:** "cap two"',
        ]
        frames = _parse_frames(lines)
        self.assertEqual(len(frames), 2)
        self.assertEqual(frames[0].number, 1)
        self.assertEqual(frames[1].number, 2)
        self.assertEqual(frames[0].caption, "cap one")
        self.assertEqual(frames[1].caption, "cap two")

    def test_frame_no_caption(self):
        lines = [
            "## FRAME_03 — silence",
            '**prompt:** quiet moment',
        ]
        frames = _parse_frames(lines)
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0].caption, "")

    def test_frame_empty_caption(self):
        lines = [
            "## FRAME_03 — silence",
            '**prompt:** quiet moment',
            '**caption:**',
        ]
        frames = _parse_frames(lines)
        self.assertEqual(frames[0].caption, "")

    def test_all_optional_fields(self):
        lines = [
            "## FRAME_10 — closer",
            '**prompt:** close up',
            '**caption:** "ending"',
            '**style:** closer',
            '**position:** top',
            '**color:** gold_bold',
            '**font:** Oi-Regular.ttf',
            '**contrast:** halo_shadow',
            '**scrim:** false',
            '**cta:** "save this"',
        ]
        frames = _parse_frames(lines)
        f = frames[0]
        self.assertEqual(f.style, "closer")
        self.assertEqual(f.position, "top")
        self.assertEqual(f.color, "gold_bold")
        self.assertEqual(f.font, "Oi-Regular.ttf")
        self.assertEqual(f.contrast, "halo_shadow")
        self.assertEqual(f.scrim, "false")
        self.assertEqual(f.cta, "save this")

    def test_dash_separator_variants(self):
        # em dash
        frames1 = _parse_frames(["## FRAME_01 — hook", "**prompt:** p"])
        self.assertEqual(len(frames1), 1)
        # double dash
        frames2 = _parse_frames(["## FRAME_01 -- hook", "**prompt:** p"])
        self.assertEqual(len(frames2), 1)
        # single dash
        frames3 = _parse_frames(["## FRAME_01 - hook", "**prompt:** p"])
        self.assertEqual(len(frames3), 1)

    def test_high_frame_numbers(self):
        frames = _parse_frames(["## FRAME_99 — last", "**prompt:** p"])
        self.assertEqual(frames[0].number, 99)
        self.assertEqual(frames[0].frame_id, "FRAME_99")

    def test_lines_before_first_frame_ignored(self):
        lines = [
            "# Episode Title",
            "Some preamble text",
            "",
            "## FRAME_01 — hook",
            "**prompt:** p",
        ]
        frames = _parse_frames(lines)
        self.assertEqual(len(frames), 1)

    def test_html_comments_ignored(self):
        lines = [
            "## FRAME_01 — test",
            "**prompt:** p",
            "<!-- this is a comment -->",
            "**caption:** cap",
        ]
        frames = _parse_frames(lines)
        self.assertEqual(frames[0].caption, "cap")

    def test_defaults(self):
        lines = ["## FRAME_01 — test", "**prompt:** p", '**caption:** "hi"']
        frames = _parse_frames(lines)
        f = frames[0]
        self.assertEqual(f.style, "body")  # default
        self.assertEqual(f.position, "")   # empty = derive later
        self.assertEqual(f.color, "white") # default
        self.assertEqual(f.font, "")
        self.assertEqual(f.contrast, "")
        self.assertEqual(f.scrim, "")
        self.assertEqual(f.cta, "")


# ─── FrameSpec properties ───────────────────────────────────────

class TestFrameSpec(unittest.TestCase):
    def test_frame_id_padding(self):
        self.assertEqual(FrameSpec(1, "s", "p").frame_id, "FRAME_01")
        self.assertEqual(FrameSpec(10, "s", "p").frame_id, "FRAME_10")

    def test_filename(self):
        self.assertEqual(FrameSpec(3, "s", "p").filename, "FRAME_03.png")


# ─── _frame_to_overlays ─────────────────────────────────────────

class TestFrameToOverlays(unittest.TestCase):
    def test_no_caption_returns_empty(self):
        f = FrameSpec(1, "s", "p", caption="")
        self.assertEqual(_frame_to_overlays(f), [])

    def test_basic_body_overlay(self):
        f = FrameSpec(1, "s", "p", caption="hello", style="body", color="white")
        ovs = _frame_to_overlays(f)
        self.assertEqual(len(ovs), 1)
        ov = ovs[0]
        self.assertEqual(ov["text"], "hello")
        self.assertEqual(ov["position"], "bottom")
        self.assertEqual(ov["style"], "body")
        self.assertEqual(ov["color"], "white")
        self.assertTrue(ov["scrim"])
        self.assertEqual(ov["scrim_side"], "bottom")
        self.assertNotIn("stylized", ov)
        self.assertNotIn("contrast", ov)
        self.assertNotIn("font", ov)

    def test_stylized_defaults(self):
        f = FrameSpec(1, "s", "p", caption="word.", style="stylized", color="gold")
        ovs = _frame_to_overlays(f)
        ov = ovs[0]
        self.assertEqual(ov["position"], "middle")  # auto-derived
        self.assertTrue(ov["stylized"])
        self.assertEqual(ov["scrim_side"], "bottom")  # middle -> bottom

    def test_explicit_position_overrides_stylized(self):
        f = FrameSpec(1, "s", "p", caption="word.", style="stylized",
                      position="top", color="gold")
        ovs = _frame_to_overlays(f)
        self.assertEqual(ovs[0]["position"], "top")

    def test_top_position_scrim_side(self):
        f = FrameSpec(1, "s", "p", caption="hi", position="top")
        ovs = _frame_to_overlays(f)
        self.assertEqual(ovs[0]["scrim_side"], "top")

    def test_scrim_false(self):
        f = FrameSpec(1, "s", "p", caption="hi", scrim="false")
        ovs = _frame_to_overlays(f)
        self.assertFalse(ovs[0]["scrim"])
        self.assertNotIn("scrim_side", ovs[0])

    def test_contrast_override(self):
        f = FrameSpec(1, "s", "p", caption="hi", contrast="halo_shadow")
        ovs = _frame_to_overlays(f)
        self.assertEqual(ovs[0]["contrast"], "halo_shadow")

    def test_font_override(self):
        f = FrameSpec(1, "s", "p", caption="hi", font="Oi-Regular.ttf")
        ovs = _frame_to_overlays(f)
        self.assertIn("Oi-Regular.ttf", ovs[0]["font"])

    def test_cta_generates_second_overlay(self):
        f = FrameSpec(1, "s", "p", caption="closer line", style="closer",
                      position="top", color="gold_bold", cta="save this")
        ovs = _frame_to_overlays(f)
        self.assertEqual(len(ovs), 2)
        # Main overlay
        self.assertEqual(ovs[0]["text"], "closer line")
        self.assertEqual(ovs[0]["position"], "top")
        # CTA overlay
        self.assertEqual(ovs[1]["text"], "save this")
        self.assertEqual(ovs[1]["position"], "bottom")
        self.assertEqual(ovs[1]["style"], "cta")
        self.assertEqual(ovs[1]["color"], "white")
        self.assertTrue(ovs[1]["scrim"])
        self.assertEqual(ovs[1]["scrim_side"], "bottom")

    def test_no_cta_means_single_overlay(self):
        f = FrameSpec(1, "s", "p", caption="hi")
        ovs = _frame_to_overlays(f)
        self.assertEqual(len(ovs), 1)


# ─── _py_repr ───────────────────────────────────────────────────

class TestPyRepr(unittest.TestCase):
    def test_regular_string(self):
        self.assertEqual(_py_repr("hello"), '"hello"')

    def test_font_path_passthrough(self):
        self.assertEqual(_py_repr('_FONTS + "/Oi.ttf"'), '_FONTS + "/Oi.ttf"')


# ─── StoryboardResult ───────────────────────────────────────────

class TestStoryboardResult(unittest.TestCase):
    def test_shots_property(self):
        frames = [
            FrameSpec(1, "hook", "prompt 1"),
            FrameSpec(2, "drop", "prompt 2"),
        ]
        result = StoryboardResult(frontmatter={}, frames=frames)
        shots = result.shots
        self.assertEqual(len(shots), 2)
        self.assertEqual(shots[0]["frame_id"], "FRAME_01")
        self.assertEqual(shots[0]["slug"], "hook")
        self.assertEqual(shots[0]["prompt"], "prompt 1")

    def test_captions_py_property(self):
        frames = [FrameSpec(1, "hook", "p", caption="hi", style="hook")]
        result = StoryboardResult(
            frontmatter={"episode": "test-ep"},
            frames=frames,
        )
        py = result.captions_py
        self.assertIn("test-ep", py)
        self.assertIn("FRAMES = [", py)
        self.assertIn('"hi"', py)
        self.assertIn("auto-generated from storyboard.md", py)


# ─── parse_storyboard (integration) ─────────────────────────────

class TestParseStoryboard(unittest.TestCase):
    def test_full_parse(self):
        content = """\
---
project: testproject
episode: test-ep
aspect: "16:9"
frame_count: 3
---

# Test Episode

## FRAME_01 — hook
**prompt:** A hook scene
**caption:** "hook line"
**style:** hook
**color:** white

## FRAME_02 — stylized
**prompt:** Stylized moment
**caption:** "word."
**style:** stylized
**color:** gold
**contrast:** stroke

## FRAME_03 — silence
**prompt:** Quiet moment
"""
        path = _write_tmp(content)
        try:
            result = parse_storyboard(path)
            self.assertEqual(result.frontmatter["project"], "testproject")
            self.assertEqual(result.frontmatter["episode"], "test-ep")
            self.assertEqual(result.frontmatter["aspect"], "16:9")
            self.assertEqual(len(result.frames), 3)

            # Frame 1
            self.assertEqual(result.frames[0].caption, "hook line")
            self.assertEqual(result.frames[0].style, "hook")

            # Frame 2 - stylized
            self.assertEqual(result.frames[1].style, "stylized")
            self.assertEqual(result.frames[1].contrast, "stroke")

            # Frame 3 - no caption
            self.assertEqual(result.frames[2].caption, "")

            # Shots
            self.assertEqual(len(result.shots), 3)
            self.assertEqual(result.shots[0]["frame_id"], "FRAME_01")

            # Captions py
            py = result.captions_py
            self.assertIn("FRAME_01.png", py)
            self.assertIn("FRAME_03.png", py)
        finally:
            os.unlink(path)

    def test_no_frontmatter(self):
        content = """\
# No Frontmatter

## FRAME_01 — test
**prompt:** A test
**caption:** "hi"
"""
        path = _write_tmp(content)
        try:
            result = parse_storyboard(path)
            self.assertEqual(result.frontmatter, {})
            self.assertEqual(len(result.frames), 1)
        finally:
            os.unlink(path)

    def test_closer_with_cta(self):
        content = """\
---
episode: cta-test
---

## FRAME_01 — closer
**prompt:** Close up
**caption:** "closing line"
**style:** closer
**position:** top
**color:** gold_bold
**font:** Oi-Regular.ttf
**cta:** "save this"
"""
        path = _write_tmp(content)
        try:
            result = parse_storyboard(path)
            f = result.frames[0]
            ovs = _frame_to_overlays(f)
            self.assertEqual(len(ovs), 2)
            self.assertEqual(ovs[0]["position"], "top")
            self.assertEqual(ovs[1]["style"], "cta")
        finally:
            os.unlink(path)


# ─── write_captions ─────────────────────────────────────────────

class TestWriteCaptions(unittest.TestCase):
    def test_write_and_reload(self):
        content = """\
---
episode: write-test
---

## FRAME_01 — hook
**prompt:** Test
**caption:** "hello world"
**style:** hook

## FRAME_02 — empty
**prompt:** No caption here
"""
        path = _write_tmp(content)
        try:
            result = parse_storyboard(path)
            fd, out_path = tempfile.mkstemp(suffix=".py")
            os.close(fd)
            write_captions(result, out_path)

            # Reload and validate
            import importlib.util
            spec = importlib.util.spec_from_file_location("captions", out_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            self.assertEqual(len(mod.FRAMES), 2)
            self.assertEqual(mod.FRAMES[0]["file"], "FRAME_01.png")
            self.assertEqual(len(mod.FRAMES[0]["overlays"]), 1)
            self.assertEqual(mod.FRAMES[0]["overlays"][0]["text"], "hello world")
            self.assertEqual(mod.FRAMES[1]["file"], "FRAME_02.png")
            self.assertEqual(len(mod.FRAMES[1]["overlays"]), 0)
            os.unlink(out_path)
        finally:
            os.unlink(path)


# ─── Comparison spiral validation ────────────────────────────────

class TestComparisonSpiralValidation(unittest.TestCase):
    """Validates parser output against the hand-written comparison-spiral.py."""

    REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STORYBOARD = os.path.join(REPO_ROOT, "episodes", "comparison-spiral", "storyboard.md")
    CAPTIONS = os.path.join(REPO_ROOT, "carousel-overlay", "assets", "captions",
                            "comparison-spiral.py")

    def setUp(self):
        if not os.path.exists(self.STORYBOARD) or not os.path.exists(self.CAPTIONS):
            self.skipTest("comparison-spiral files not found")

        import importlib.util
        spec = importlib.util.spec_from_file_location("comparison_spiral", self.CAPTIONS)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.expected = mod.FRAMES

        self.result = parse_storyboard(self.STORYBOARD)

    def test_frame_count_matches(self):
        self.assertEqual(len(self.result.frames), len(self.expected))

    def test_overlay_counts_match(self):
        for i, f in enumerate(self.result.frames):
            ovs = _frame_to_overlays(f)
            exp_ovs = self.expected[i].get("overlays", [])
            self.assertEqual(len(ovs), len(exp_ovs),
                             f"Frame {i+1}: overlay count mismatch")

    def test_overlay_text_matches(self):
        for i, f in enumerate(self.result.frames):
            ovs = _frame_to_overlays(f)
            exp_ovs = self.expected[i].get("overlays", [])
            for j in range(len(ovs)):
                self.assertEqual(ovs[j]["text"], exp_ovs[j]["text"],
                                 f"Frame {i+1} overlay {j+1}: text mismatch")

    def test_overlay_position_matches(self):
        for i, f in enumerate(self.result.frames):
            ovs = _frame_to_overlays(f)
            exp_ovs = self.expected[i].get("overlays", [])
            for j in range(len(ovs)):
                self.assertEqual(ovs[j]["position"], exp_ovs[j]["position"],
                                 f"Frame {i+1} overlay {j+1}: position mismatch")

    def test_overlay_style_matches(self):
        for i, f in enumerate(self.result.frames):
            ovs = _frame_to_overlays(f)
            exp_ovs = self.expected[i].get("overlays", [])
            for j in range(len(ovs)):
                self.assertEqual(ovs[j]["style"], exp_ovs[j]["style"],
                                 f"Frame {i+1} overlay {j+1}: style mismatch")

    def test_overlay_color_matches(self):
        for i, f in enumerate(self.result.frames):
            ovs = _frame_to_overlays(f)
            exp_ovs = self.expected[i].get("overlays", [])
            for j in range(len(ovs)):
                self.assertEqual(ovs[j]["color"], exp_ovs[j]["color"],
                                 f"Frame {i+1} overlay {j+1}: color mismatch")

    def test_overlay_scrim_matches(self):
        for i, f in enumerate(self.result.frames):
            ovs = _frame_to_overlays(f)
            exp_ovs = self.expected[i].get("overlays", [])
            for j in range(len(ovs)):
                self.assertEqual(ovs[j].get("scrim"), exp_ovs[j].get("scrim"),
                                 f"Frame {i+1} overlay {j+1}: scrim mismatch")
                self.assertEqual(ovs[j].get("scrim_side"), exp_ovs[j].get("scrim_side"),
                                 f"Frame {i+1} overlay {j+1}: scrim_side mismatch")

    def test_overlay_stylized_matches(self):
        for i, f in enumerate(self.result.frames):
            ovs = _frame_to_overlays(f)
            exp_ovs = self.expected[i].get("overlays", [])
            for j in range(len(ovs)):
                self.assertEqual(ovs[j].get("stylized"), exp_ovs[j].get("stylized"),
                                 f"Frame {i+1} overlay {j+1}: stylized mismatch")

    def test_overlay_contrast_matches(self):
        for i, f in enumerate(self.result.frames):
            ovs = _frame_to_overlays(f)
            exp_ovs = self.expected[i].get("overlays", [])
            for j in range(len(ovs)):
                self.assertEqual(ovs[j].get("contrast"), exp_ovs[j].get("contrast"),
                                 f"Frame {i+1} overlay {j+1}: contrast mismatch")


if __name__ == "__main__":
    unittest.main()
