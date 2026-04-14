"""
Unit tests for pipeline/run_pipeline.py
"""
from __future__ import annotations

import os
import sys
import tempfile
import shutil
import unittest
from unittest.mock import patch
from argparse import Namespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.run_pipeline import (
    load_preset,
    ensure_episode_dir,
    next_version_dir,
    latest_version_dir,
    generate_captions,
)
from pipeline.parse_storyboard import parse_storyboard


# ─── Temp directory helper ──────────────────────────────────────

class TmpDirTestCase(unittest.TestCase):
    """Base class that provides a clean temp directory per test."""
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)


# ─── load_preset ────────────────────────────────────────────────

class TestLoadPreset(unittest.TestCase):
    def test_loads_glytoons(self):
        preset = load_preset("glytoons")
        self.assertEqual(preset["name"], "glytoons")
        self.assertIn("content", preset)
        self.assertIn("DOZER", preset["content"])
        self.assertIn("GLY", preset["content"])

    def test_missing_preset_returns_error(self):
        preset = load_preset("nonexistent-project-xyz")
        self.assertIn("error", preset)

    def test_preset_has_path(self):
        preset = load_preset("glytoons")
        self.assertTrue(preset["path"].endswith("glytoons.md"))
        self.assertTrue(os.path.exists(preset["path"]))


# ─── next_version_dir ───────────────────────────────────────────

class TestNextVersionDir(TmpDirTestCase):
    def test_empty_directory(self):
        result = next_version_dir(self.tmpdir)
        self.assertTrue(result.endswith("v01"))

    def test_existing_versions(self):
        os.makedirs(os.path.join(self.tmpdir, "v01"))
        os.makedirs(os.path.join(self.tmpdir, "v02"))
        result = next_version_dir(self.tmpdir)
        self.assertTrue(result.endswith("v03"))

    def test_nonexistent_directory(self):
        result = next_version_dir(os.path.join(self.tmpdir, "nope"))
        self.assertTrue(result.endswith("v01"))

    def test_non_version_dirs_ignored(self):
        os.makedirs(os.path.join(self.tmpdir, "v01"))
        os.makedirs(os.path.join(self.tmpdir, "other"))
        os.makedirs(os.path.join(self.tmpdir, "readme.md"))  # not a dir pattern match
        result = next_version_dir(self.tmpdir)
        self.assertTrue(result.endswith("v02"))

    def test_gap_in_versions(self):
        os.makedirs(os.path.join(self.tmpdir, "v01"))
        os.makedirs(os.path.join(self.tmpdir, "v05"))
        result = next_version_dir(self.tmpdir)
        self.assertTrue(result.endswith("v06"))


# ─── latest_version_dir ─────────────────────────────────────────

class TestLatestVersionDir(TmpDirTestCase):
    def test_empty_returns_none(self):
        self.assertIsNone(latest_version_dir(self.tmpdir))

    def test_nonexistent_returns_none(self):
        self.assertIsNone(latest_version_dir(os.path.join(self.tmpdir, "nope")))

    def test_returns_latest(self):
        os.makedirs(os.path.join(self.tmpdir, "v01"))
        os.makedirs(os.path.join(self.tmpdir, "v03"))
        os.makedirs(os.path.join(self.tmpdir, "v02"))
        result = latest_version_dir(self.tmpdir)
        self.assertTrue(result.endswith("v03"))

    def test_single_version(self):
        os.makedirs(os.path.join(self.tmpdir, "v01"))
        result = latest_version_dir(self.tmpdir)
        self.assertTrue(result.endswith("v01"))


# ─── ensure_episode_dir ─────────────────────────────────────────

class TestEnsureEpisodeDir(TmpDirTestCase):
    @patch("pipeline.run_pipeline.EPISODES_DIR")
    def test_creates_structure(self, mock_dir):
        mock_dir.__class__ = str  # needed for os.path.join
        ep_base = os.path.join(self.tmpdir, "episodes")

        with patch("pipeline.run_pipeline.EPISODES_DIR", ep_base):
            paths = ensure_episode_dir("test-ep")

        self.assertTrue(os.path.isdir(paths["root"]))
        self.assertTrue(os.path.isdir(paths["refs"]))
        self.assertTrue(os.path.isdir(paths["keyframes"]))
        self.assertTrue(os.path.isdir(paths["final"]))
        self.assertTrue(paths["storyboard"].endswith("storyboard.md"))
        self.assertTrue(paths["captions"].endswith("captions.py"))

    @patch("pipeline.run_pipeline.EPISODES_DIR")
    def test_idempotent(self, mock_dir):
        ep_base = os.path.join(self.tmpdir, "episodes")
        with patch("pipeline.run_pipeline.EPISODES_DIR", ep_base):
            paths1 = ensure_episode_dir("test-ep")
            paths2 = ensure_episode_dir("test-ep")
        self.assertEqual(paths1, paths2)


# ─── generate_captions ──────────────────────────────────────────

class TestGenerateCaptions(TmpDirTestCase):
    def _make_storyboard(self):
        content = """\
---
episode: gen-test
---

## FRAME_01 — hook
**prompt:** test
**caption:** "hello"
**style:** hook
"""
        path = os.path.join(self.tmpdir, "storyboard.md")
        with open(path, "w") as f:
            f.write(content)
        return parse_storyboard(path)

    def test_writes_new_file(self):
        result = self._make_storyboard()
        captions_path = os.path.join(self.tmpdir, "captions.py")
        wrote = generate_captions(result, captions_path)
        self.assertTrue(wrote)
        self.assertTrue(os.path.exists(captions_path))
        with open(captions_path) as f:
            content = f.read()
        self.assertIn("auto-generated from storyboard.md", content)

    def test_overwrites_auto_generated(self):
        result = self._make_storyboard()
        captions_path = os.path.join(self.tmpdir, "captions.py")
        generate_captions(result, captions_path)
        # Call again — should overwrite since it has the auto-generated marker
        wrote = generate_captions(result, captions_path)
        self.assertTrue(wrote)

    def test_skips_manually_edited(self):
        result = self._make_storyboard()
        captions_path = os.path.join(self.tmpdir, "captions.py")
        with open(captions_path, "w") as f:
            f.write("# Manually edited file\nFRAMES = []\n")
        wrote = generate_captions(result, captions_path)
        self.assertFalse(wrote)
        # Verify original content preserved
        with open(captions_path) as f:
            self.assertIn("Manually edited", f.read())

    def test_force_overwrites_manual(self):
        result = self._make_storyboard()
        captions_path = os.path.join(self.tmpdir, "captions.py")
        with open(captions_path, "w") as f:
            f.write("# Manually edited file\nFRAMES = []\n")
        wrote = generate_captions(result, captions_path, force=True)
        self.assertTrue(wrote)
        with open(captions_path) as f:
            self.assertIn("auto-generated", f.read())


if __name__ == "__main__":
    unittest.main()
