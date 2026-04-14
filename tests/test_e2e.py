"""
End-to-end tests for the carousel pipeline.

Tests the full flow: storyboard.md → parse → captions.py → validate.
Does NOT test keyframe generation (requires API) or overlay rendering
(requires Pillow + fonts), but validates everything the pipeline controls.
"""
from __future__ import annotations

import os
import sys
import json
import tempfile
import shutil
import unittest
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from pipeline.parse_storyboard import (
    parse_storyboard,
    write_captions,
    _frame_to_overlays,
)
from pipeline.run_pipeline import (
    load_preset,
    ensure_episode_dir,
    next_version_dir,
    latest_version_dir,
    generate_captions,
)


def _write_tmp(content: str, suffix=".md") -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


# ─── E2E: Storyboard → Captions .py → Loadable module ───────────

class TestE2EStoryboardToCaptions(unittest.TestCase):
    """Full pipeline: parse storyboard, generate captions.py, load it, validate structure."""

    STORYBOARD = """\
---
project: glytoons
episode: e2e-test
aspect: "9:16"
model: gemini-3.1-flash-image-preview
frame_count: 6
---

# E2E Test Episode

## FRAME_01 — hook
**prompt:** Opening scene with character standing
**caption:** "this is the hook"
**style:** hook
**color:** white

## FRAME_02 — body
**prompt:** Character walks forward
**caption:** "middle of story"
**style:** body
**color:** white

## FRAME_03 — emotional
**prompt:** Character reaches peak emotion
**caption:** "the golden moment"
**style:** body
**color:** gold

## FRAME_04 — stylized
**prompt:** Wide artistic shot
**caption:** "breathe."
**style:** stylized
**color:** gold
**contrast:** stroke

## FRAME_05 — silence
**prompt:** Quiet beat, no text needed

## FRAME_06 — closer
**prompt:** Final close-up
**caption:** "still here."
**style:** closer
**position:** top
**color:** gold_bold
**font:** Oi-Regular.ttf
**cta:** "save this for later"
"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.storyboard_path = os.path.join(self.tmpdir, "storyboard.md")
        with open(self.storyboard_path, "w") as f:
            f.write(self.STORYBOARD)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_parse_returns_correct_frame_count(self):
        result = parse_storyboard(self.storyboard_path)
        self.assertEqual(len(result.frames), 6)

    def test_parse_returns_correct_frontmatter(self):
        result = parse_storyboard(self.storyboard_path)
        self.assertEqual(result.frontmatter["project"], "glytoons")
        self.assertEqual(result.frontmatter["episode"], "e2e-test")
        self.assertEqual(result.frontmatter["aspect"], "9:16")

    def test_generated_captions_is_valid_python(self):
        result = parse_storyboard(self.storyboard_path)
        captions_path = os.path.join(self.tmpdir, "captions.py")
        write_captions(result, captions_path)

        spec = importlib.util.spec_from_file_location("captions", captions_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        self.assertTrue(hasattr(mod, "FRAMES"))
        self.assertIsInstance(mod.FRAMES, list)

    def test_captions_frame_count_matches(self):
        result = parse_storyboard(self.storyboard_path)
        captions_path = os.path.join(self.tmpdir, "captions.py")
        write_captions(result, captions_path)

        spec = importlib.util.spec_from_file_location("captions", captions_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        self.assertEqual(len(mod.FRAMES), 6)

    def test_captions_filenames_sequential(self):
        result = parse_storyboard(self.storyboard_path)
        captions_path = os.path.join(self.tmpdir, "captions.py")
        write_captions(result, captions_path)

        spec = importlib.util.spec_from_file_location("captions", captions_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        expected_files = [f"FRAME_{i:02d}.png" for i in range(1, 7)]
        actual_files = [f["file"] for f in mod.FRAMES]
        self.assertEqual(actual_files, expected_files)

    def test_captions_overlay_counts(self):
        result = parse_storyboard(self.storyboard_path)
        captions_path = os.path.join(self.tmpdir, "captions.py")
        write_captions(result, captions_path)

        spec = importlib.util.spec_from_file_location("captions", captions_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        expected_counts = [1, 1, 1, 1, 0, 2]  # frame 5 = no text, frame 6 = closer + cta
        actual_counts = [len(f["overlays"]) for f in mod.FRAMES]
        self.assertEqual(actual_counts, expected_counts)

    def test_hook_overlay_structure(self):
        result = parse_storyboard(self.storyboard_path)
        captions_path = os.path.join(self.tmpdir, "captions.py")
        write_captions(result, captions_path)

        spec = importlib.util.spec_from_file_location("captions", captions_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        hook = mod.FRAMES[0]["overlays"][0]
        self.assertEqual(hook["text"], "this is the hook")
        self.assertEqual(hook["position"], "bottom")
        self.assertEqual(hook["style"], "hook")
        self.assertEqual(hook["color"], "white")
        self.assertTrue(hook["scrim"])

    def test_stylized_overlay_structure(self):
        result = parse_storyboard(self.storyboard_path)
        captions_path = os.path.join(self.tmpdir, "captions.py")
        write_captions(result, captions_path)

        spec = importlib.util.spec_from_file_location("captions", captions_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        stylized = mod.FRAMES[3]["overlays"][0]
        self.assertEqual(stylized["text"], "breathe.")
        self.assertEqual(stylized["position"], "middle")
        self.assertTrue(stylized["stylized"])
        self.assertEqual(stylized["contrast"], "stroke")

    def test_closer_with_cta_structure(self):
        result = parse_storyboard(self.storyboard_path)
        captions_path = os.path.join(self.tmpdir, "captions.py")
        write_captions(result, captions_path)

        spec = importlib.util.spec_from_file_location("captions", captions_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        closer_frame = mod.FRAMES[5]
        self.assertEqual(len(closer_frame["overlays"]), 2)

        closer = closer_frame["overlays"][0]
        self.assertEqual(closer["text"], "still here.")
        self.assertEqual(closer["position"], "top")
        self.assertEqual(closer["style"], "closer")
        self.assertEqual(closer["color"], "gold_bold")

        cta = closer_frame["overlays"][1]
        self.assertEqual(cta["text"], "save this for later")
        self.assertEqual(cta["style"], "cta")
        self.assertEqual(cta["position"], "bottom")

    def test_shot_list_for_keyframes(self):
        result = parse_storyboard(self.storyboard_path)
        shots = result.shots
        self.assertEqual(len(shots), 6)
        for shot in shots:
            self.assertIn("frame_id", shot)
            self.assertIn("slug", shot)
            self.assertIn("prompt", shot)
            self.assertTrue(len(shot["prompt"]) > 0)

    def test_shots_json_export(self):
        result = parse_storyboard(self.storyboard_path)
        shots_path = os.path.join(self.tmpdir, "shots.json")
        with open(shots_path, "w") as f:
            json.dump(result.shots, f, indent=2)

        with open(shots_path) as f:
            loaded = json.load(f)

        self.assertEqual(len(loaded), 6)
        self.assertEqual(loaded[0]["frame_id"], "FRAME_01")


# ─── E2E: Episode directory lifecycle ────────────────────────────

class TestE2EEpisodeDirectory(unittest.TestCase):
    """Tests episode directory creation, versioning, and captions conflict detection."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.ep_base = os.path.join(self.tmpdir, "episodes")
        os.makedirs(self.ep_base)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_full_version_lifecycle(self):
        kf_dir = os.path.join(self.ep_base, "test", "keyframes")
        os.makedirs(kf_dir)

        # First version
        v1 = next_version_dir(kf_dir)
        os.makedirs(v1)
        self.assertTrue(v1.endswith("v01"))

        # Latest points to v01
        self.assertEqual(latest_version_dir(kf_dir), v1)

        # Second version
        v2 = next_version_dir(kf_dir)
        os.makedirs(v2)
        self.assertTrue(v2.endswith("v02"))

        # Latest now points to v02
        self.assertEqual(latest_version_dir(kf_dir), v2)

    def test_captions_conflict_detection_flow(self):
        storyboard = """\
---
episode: conflict-test
---

## FRAME_01 — hook
**prompt:** test
**caption:** "auto line"
**style:** hook
"""
        sb_path = os.path.join(self.tmpdir, "storyboard.md")
        with open(sb_path, "w") as f:
            f.write(storyboard)

        result = parse_storyboard(sb_path)
        captions_path = os.path.join(self.tmpdir, "captions.py")

        # First write — succeeds
        self.assertTrue(generate_captions(result, captions_path))

        # Second write — succeeds (auto-generated marker present)
        self.assertTrue(generate_captions(result, captions_path))

        # Simulate manual edit (remove auto-generated marker)
        with open(captions_path, "w") as f:
            f.write("# Hand-edited captions\nFRAMES = []\n")

        # Third write — skipped (manual edit detected)
        self.assertFalse(generate_captions(result, captions_path))

        # Force write — succeeds
        self.assertTrue(generate_captions(result, captions_path, force=True))


# ─── E2E: Preset + storyboard integration ───────────────────────

class TestE2EPresetIntegration(unittest.TestCase):
    """Tests that presets load correctly and match storyboard project field."""

    def test_glytoons_preset_has_required_sections(self):
        preset = load_preset("glytoons")
        content = preset["content"]
        self.assertIn("## Style Prefix", content)
        self.assertIn("## Characters", content)
        self.assertIn("### DOZER", content)
        self.assertIn("### GLY", content)
        self.assertIn("## Prompt Suffixes", content)

    def test_storyboard_project_matches_preset(self):
        storyboard_path = os.path.join(
            REPO_ROOT, "episodes", "comparison-spiral", "storyboard.md"
        )
        if not os.path.exists(storyboard_path):
            self.skipTest("comparison-spiral storyboard not found")

        result = parse_storyboard(storyboard_path)
        project = result.frontmatter.get("project")
        self.assertIsNotNone(project)

        preset = load_preset(project)
        self.assertNotIn("error", preset)
        self.assertEqual(preset["name"], project)


# ─── E2E: Comparison spiral full roundtrip ───────────────────────

class TestE2EComparisonSpiralRoundtrip(unittest.TestCase):
    """Parse the real storyboard, generate captions.py, load it, and verify
    every frame matches the hand-written version."""

    def setUp(self):
        self.storyboard = os.path.join(
            REPO_ROOT, "episodes", "comparison-spiral", "storyboard.md"
        )
        self.original_captions = os.path.join(
            REPO_ROOT, "carousel-overlay", "assets", "captions", "comparison-spiral.py"
        )
        if not os.path.exists(self.storyboard) or not os.path.exists(self.original_captions):
            self.skipTest("comparison-spiral files not found")

        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_roundtrip_produces_loadable_captions(self):
        result = parse_storyboard(self.storyboard)
        captions_path = os.path.join(self.tmpdir, "captions.py")
        write_captions(result, captions_path)

        spec = importlib.util.spec_from_file_location("captions_rt", captions_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        self.assertEqual(len(mod.FRAMES), 10)

    def test_roundtrip_overlay_fields_match_original(self):
        """Every overlay field (except file/font path format) matches the original."""
        result = parse_storyboard(self.storyboard)

        spec = importlib.util.spec_from_file_location("orig", self.original_captions)
        orig = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(orig)

        check_keys = {"text", "position", "style", "color", "scrim", "scrim_side",
                       "stylized", "contrast"}

        for i, frame in enumerate(result.frames):
            parsed_ovs = _frame_to_overlays(frame)
            orig_ovs = orig.FRAMES[i].get("overlays", [])

            self.assertEqual(len(parsed_ovs), len(orig_ovs),
                             f"Frame {i+1}: overlay count")

            for j in range(len(parsed_ovs)):
                for key in check_keys:
                    self.assertEqual(
                        parsed_ovs[j].get(key), orig_ovs[j].get(key),
                        f"Frame {i+1} overlay {j+1} key '{key}'"
                    )


if __name__ == "__main__":
    unittest.main()
