"""
Carousel Pipeline Runner
=========================
Orchestrates all stages of carousel reel production:

  Stage 1: PARSE     — Read storyboard, create episode directory, parse frames
  Stage 2: KEYFRAMES — Generate keyframe images (delegated to Claude Code skill)
  Stage 3: CAPTIONS  — Generate captions.py from storyboard
  Stage 4: OVERLAY   — Run overlay engine on keyframes
  Stage 5: REPORT    — Summary of results

Usage:
  python -m pipeline.run_pipeline \\
    --storyboard episodes/comparison-spiral/storyboard.md \\
    [--refs episodes/comparison-spiral/refs/] \\
    [--skip-keyframes] \\
    [--skip-overlay] \\
    [--auto-regen] \\
    [--edit-captions]

Stages 2 (keyframes) and QC are designed to be driven by Claude Code skills
that call image generation APIs. This runner handles the non-interactive
stages (parse, captions, overlay) and prints instructions for the
interactive stages.
"""

from __future__ import annotations

import os
import sys
import argparse
import shutil
import json

from pipeline.parse_storyboard import parse_storyboard, write_captions


# ─── Paths ──────────────────────────────────────────────────────

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OVERLAY_ENGINE = os.path.join(REPO_ROOT, "carousel-overlay", "scripts", "overlay_engine.py")
PRESETS_DIR = os.path.join(REPO_ROOT, "presets")
EPISODES_DIR = os.path.join(REPO_ROOT, "episodes")


# ─── Preset loading ─────────────────────────────────────────────

def load_preset(project_name: str) -> dict:
    """Load a project preset file and return its contents as a dict."""
    preset_path = os.path.join(PRESETS_DIR, f"{project_name}.md")
    if not os.path.exists(preset_path):
        return {"error": f"Preset not found: {preset_path}"}

    with open(preset_path, "r") as f:
        content = f.read()

    return {
        "name": project_name,
        "path": preset_path,
        "content": content,
    }


# ─── Episode directory ──────────────────────────────────────────

def ensure_episode_dir(episode_name: str) -> dict:
    """Create and return paths for the episode directory structure."""
    ep_dir = os.path.join(EPISODES_DIR, episode_name)
    paths = {
        "root": ep_dir,
        "refs": os.path.join(ep_dir, "refs"),
        "keyframes": os.path.join(ep_dir, "keyframes"),
        "final": os.path.join(ep_dir, "final"),
        "storyboard": os.path.join(ep_dir, "storyboard.md"),
        "captions": os.path.join(ep_dir, "captions.py"),
    }

    for d in [paths["root"], paths["refs"], paths["keyframes"], paths["final"]]:
        os.makedirs(d, exist_ok=True)

    return paths


def next_version_dir(keyframes_dir: str) -> str:
    """Find the next available version directory (v01, v02, ...)."""
    existing = []
    if os.path.exists(keyframes_dir):
        for name in os.listdir(keyframes_dir):
            if name.startswith("v") and name[1:].isdigit():
                existing.append(int(name[1:]))
    next_v = max(existing, default=0) + 1
    return os.path.join(keyframes_dir, f"v{next_v:02d}")


def latest_version_dir(keyframes_dir: str):
    """Find the latest version directory, or None if none exist."""
    existing = []
    if os.path.exists(keyframes_dir):
        for name in os.listdir(keyframes_dir):
            if name.startswith("v") and name[1:].isdigit():
                existing.append((int(name[1:]), name))
    if not existing:
        return None
    existing.sort()
    return os.path.join(keyframes_dir, existing[-1][1])


# ─── Captions generation with conflict detection ────────────────

def generate_captions(result, captions_path: str, force: bool = False) -> bool:
    """
    Generate captions.py from storyboard. Returns True if written.
    If file exists and has been modified, prints warning and returns False
    unless force=True.
    """
    if os.path.exists(captions_path) and not force:
        # Check if the file was manually edited (has no auto-generated marker)
        with open(captions_path, "r") as f:
            existing = f.read()

        if "auto-generated from storyboard.md" not in existing:
            print(f"\n  WARNING: {captions_path} exists and appears manually edited.")
            print(f"  Use --force-captions to overwrite, or edit manually.")
            return False

    write_captions(result, captions_path)
    return True


# ─── Overlay rendering ──────────────────────────────────────────

def run_overlay(input_dir: str, output_dir: str, captions_path: str) -> int:
    """Run the overlay engine. Returns exit code."""
    import subprocess
    cmd = [
        sys.executable, OVERLAY_ENGINE,
        "--input", input_dir,
        "--output", output_dir,
        "--captions", captions_path,
    ]
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


# ─── Main pipeline ──────────────────────────────────────────────

def run(args):
    print("\n" + "=" * 60)
    print("  CAROUSEL PIPELINE")
    print("=" * 60)

    # ── Stage 1: PARSE ──────────────────────────────────────────
    print("\n── Stage 1: PARSE ─────────────────────────────────────")

    result = parse_storyboard(args.storyboard)
    fm = result.frontmatter
    episode = fm.get("episode", "untitled")
    project = fm.get("project", "")

    print(f"  Project:  {project}")
    print(f"  Episode:  {episode}")
    print(f"  Frames:   {len(result.frames)}")

    # Load preset
    if project:
        preset = load_preset(project)
        if "error" in preset:
            print(f"  WARNING: {preset['error']}")
        else:
            print(f"  Preset:   {preset['path']}")

    # Ensure episode directory
    paths = ensure_episode_dir(episode)
    print(f"  Episode dir: {paths['root']}")

    # Copy storyboard into episode dir if not already there
    storyboard_abs = os.path.abspath(args.storyboard)
    episode_storyboard = os.path.abspath(paths["storyboard"])
    if storyboard_abs != episode_storyboard:
        shutil.copy2(args.storyboard, paths["storyboard"])
        print(f"  Copied storyboard to: {paths['storyboard']}")

    # ── Stage 2: KEYFRAMES ──────────────────────────────────────
    if args.skip_keyframes:
        print("\n── Stage 2: KEYFRAMES (skipped) ───────────────────────")
        kf_dir = latest_version_dir(paths["keyframes"])
        if kf_dir:
            print(f"  Using existing keyframes: {kf_dir}")
        else:
            print("  WARNING: No keyframes found. Run without --skip-keyframes first.")
            if not args.skip_overlay:
                print("  Cannot run overlay without keyframes. Exiting.")
                return 1
    else:
        print("\n── Stage 2: KEYFRAMES ─────────────────────────────────")
        kf_dir = next_version_dir(paths["keyframes"])
        os.makedirs(kf_dir, exist_ok=True)

        print(f"  Output dir: {kf_dir}")
        print(f"  Refs dir:   {args.refs or paths['refs']}")
        print()
        print("  This stage requires the /keyframes Claude Code skill.")
        print("  Run the following to generate keyframes:")
        print()
        print(f"  /keyframes {paths['storyboard']} \\")
        print(f"    --refs {args.refs or paths['refs']} \\")
        print(f"    --output {kf_dir} \\")
        print(f"    --aspect {fm.get('aspect', '9:16')} \\")
        print(f"    --model {fm.get('model', 'gemini-3.1-flash-image-preview')}")
        if args.auto_regen:
            print(f"    --auto-regen")
        print()

        # Export shot list for the keyframes skill
        shots_path = os.path.join(paths["root"], "shots.json")
        with open(shots_path, "w") as f:
            json.dump(result.shots, f, indent=2)
        print(f"  Shot list written to: {shots_path}")
        print("  Waiting for keyframes to be generated...")
        print("  (Re-run with --skip-keyframes once keyframes are ready)")
        return 0

    # ── Stage 3: CAPTIONS ───────────────────────────────────────
    print("\n── Stage 3: CAPTIONS ──────────────────────────────────")

    wrote = generate_captions(result, paths["captions"], force=args.force_captions)
    if wrote:
        print(f"  Generated: {paths['captions']}")
    else:
        print(f"  Kept existing: {paths['captions']}")

    if args.edit_captions:
        print()
        print(f"  Edit captions now: {paths['captions']}")
        print("  Re-run with --skip-keyframes when ready.")
        return 0

    # ── Stage 4: OVERLAY ────────────────────────────────────────
    if args.skip_overlay:
        print("\n── Stage 4: OVERLAY (skipped) ─────────────────────────")
    else:
        print("\n── Stage 4: OVERLAY ───────────────────────────────────")
        print(f"  Input:    {kf_dir}")
        print(f"  Output:   {paths['final']}")
        print(f"  Captions: {paths['captions']}")

        ret = run_overlay(kf_dir, paths["final"], paths["captions"])
        if ret != 0:
            print(f"\n  Overlay engine failed with exit code {ret}")
            return ret

    # ── Stage 5: REPORT ─────────────────────────────────────────
    print("\n── Stage 5: REPORT ────────────────────────────────────")

    # Count outputs
    final_count = 0
    if os.path.exists(paths["final"]):
        final_count = len([f for f in os.listdir(paths["final"]) if f.endswith(".png")])

    kf_count = 0
    if kf_dir and os.path.exists(kf_dir):
        kf_count = len([f for f in os.listdir(kf_dir) if f.endswith(".png")])

    print(f"  Keyframes:     {kf_count} frames in {kf_dir}")
    print(f"  Final output:  {final_count} frames in {paths['final']}")
    print(f"  Captions:      {paths['captions']}")
    print(f"  Storyboard:    {paths['storyboard']}")
    print()

    if final_count > 0:
        print("  Pipeline complete.")
    elif kf_count > 0 and args.skip_overlay:
        print("  Keyframes ready. Run without --skip-overlay to render text overlays.")
    else:
        print("  Re-run with --skip-keyframes to render overlays on existing keyframes.")

    print()
    return 0


# ─── CLI ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Carousel Pipeline — storyboard to finished carousel frames",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline (pauses for keyframe generation)
  python -m pipeline.run_pipeline --storyboard episodes/ep01/storyboard.md

  # Skip keyframes, just render overlays on existing frames
  python -m pipeline.run_pipeline --storyboard episodes/ep01/storyboard.md --skip-keyframes

  # Generate captions only, edit them, then render
  python -m pipeline.run_pipeline --storyboard episodes/ep01/storyboard.md --skip-keyframes --edit-captions
        """
    )
    parser.add_argument("--storyboard", required=True, help="Path to storyboard.md")
    parser.add_argument("--refs", default=None, help="Character references directory")
    parser.add_argument("--skip-keyframes", action="store_true",
                        help="Skip keyframe generation, use existing frames")
    parser.add_argument("--skip-overlay", action="store_true",
                        help="Skip overlay rendering")
    parser.add_argument("--auto-regen", action="store_true",
                        help="Auto-regenerate keyframes that fail QC")
    parser.add_argument("--edit-captions", action="store_true",
                        help="Pause after generating captions.py for manual editing")
    parser.add_argument("--force-captions", action="store_true",
                        help="Overwrite existing captions.py even if manually edited")
    args = parser.parse_args()

    sys.exit(run(args))


if __name__ == "__main__":
    main()
