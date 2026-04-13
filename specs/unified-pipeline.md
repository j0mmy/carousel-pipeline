# Unified Carousel Pipeline — Spec

## Problem

The pipeline has three working stages — keyframe generation, QC review, and text overlay — but they are disconnected. Each stage has its own input format, naming conventions, and directory expectations. Chaining them requires manual translation at every handoff.

This spec defines the changes needed to run all three stages from a single storyboard document.

---

## Pipeline overview

```
STORYBOARD.md ──┐
                 ├──► KEYFRAMES ──► QC ──► OVERLAY ──► FINAL PNGs
PROJECT PRESET ──┘
```

One command. One document in, finished carousel frames out.

---

## 1. Unified storyboard format

The storyboard is the single source of truth. It carries everything both `/keyframes` and `/carousel-overlay` need — image generation prompts AND overlay specs — in one markdown file.

### Format

````markdown
---
project: glytoons
episode: comparison-spiral
aspect: "9:16"
model: gemini-3.1-flash-image-preview
frame_count: 10
---

# Comparison Spiral

## FRAME_01 — hook
**prompt:** Dozer sitting on the ground scrolling his phone, dull expression, muted colors, flat background. GLY not in frame yet.
**caption:** "you before the scroll"
**style:** hook
**color:** white

## FRAME_02 — drop
**prompt:** Same angle. Dozer's expression shifts to self-doubt, phone screen glowing on his face. Slightly desaturated environment.
**caption:** "after 20 mins of their highlights"
**style:** body
**color:** white

## FRAME_03 — gly-arrives
**prompt:** GLY floating into frame from the right on spaceboard, warm light trails behind. Dozer looks up from phone.
**caption:** "GLY pulls up"
**style:** hook
**color:** white

## FRAME_04 — offer
**prompt:** GLY hovers beside Dozer, small hand extended. Dozer still holding phone but looking at GLY. Warm light beginning to fill the scene.
**caption:** "put the phone down for a sec"
**style:** body
**color:** white

## FRAME_05 — breathe-in
**prompt:** Both characters eyes closed, chest expanded, soft golden particles floating upward around them. Phone on the ground beside Dozer.
**caption:** "breathe in"
**style:** body
**color:** white

## FRAME_06 — breathe-out
**prompt:** Both characters exhaling, shoulders relaxed, particles settling. Warm ambient glow.
**caption:** "breathe out"
**style:** body
**color:** white

## FRAME_07 — one-more
**prompt:** Dozer and GLY side by side, eyes closed again, deeper inhale. Golden aura building around both.
**caption:** "one more time..."
**style:** body
**color:** gold

## FRAME_08 — breathe-stylized
**prompt:** Wide shot. Both characters small in frame, massive soft golden aura radiating outward. Peaceful.
**caption:** "breathe."
**style:** stylized
**position:** middle
**color:** gold

## FRAME_09 — silence
**prompt:** Quiet moment. Dozer sitting peacefully, phone forgotten on the ground. GLY beside him. Warm sunset light.
**caption:**
<!-- no text — visual beat -->

## FRAME_10 — closer
**prompt:** Close-up of both characters looking at camera. Warm, content expressions. Golden hour light.
**caption:** "still here. still you."
**style:** closer
**position:** top
**color:** gold_bold
**font:** Oi-Regular.ttf
**cta:** "save this for the next spiral"
````

### Field reference

#### Frontmatter (YAML)

| Field | Required | Description |
|---|---|---|
| `project` | yes | Project preset name. Determines character descriptions, style prefix, position lock, refs directory. |
| `episode` | yes | Episode slug. Used for directory naming and captions filename. |
| `aspect` | no | Aspect ratio. Default: `9:16` |
| `model` | no | Image generation model. Default: `gemini-3.1-flash-image-preview` |
| `frame_count` | no | Expected frame count. Used for validation only. |

#### Per-frame fields

| Field | Required | Description |
|---|---|---|
| `## FRAME_NN — slug` | yes | Frame header. `NN` is zero-padded frame number (01-99). `slug` is a human-readable name. |
| `**prompt:**` | yes | Image generation prompt. The keyframe skill combines this with the project preset's style prefix and character descriptions. |
| `**caption:**` | no | Overlay text. Empty or omitted = no text overlay on this frame. |
| `**style:**` | no | Overlay style key: `hook`, `body`, `closer`, `stylized`, `cta`. Default: `body`. |
| `**position:**` | no | Overlay position: `bottom`, `top`, `middle`. Default: `bottom`. |
| `**color:**` | no | Color key from stylesheet: `white`, `gold`, `gold_bold`, `muted`, `black`. Default: `white`. |
| `**font:**` | no | Font filename override (must exist in `carousel-overlay/assets/fonts/`). |
| `**cta:**` | no | Second overlay for CTA text. When present, renders as a bottom-positioned CTA below/alongside the main caption. |
| `**scrim:**` | no | `true`/`false`. Default: `true` when caption is present. |
| `**contrast:**` | no | Contrast method override: `stroke`, `dual_shadow`, `halo_shadow`, `stroke_shadow`. |

### Parsing rules

- Frame IDs are extracted from the `## FRAME_NN` header. The `NN` is the canonical frame number.
- Output filenames follow the pattern `FRAME_01.png`, `FRAME_02.png`, etc. Both skills use this convention.
- The `slug` after the dash is for human readability only — not used in filenames.
- `**caption:**` with no value or an empty string = no overlay (equivalent to `"overlays": []` in the current captions schema).
- `**style:** stylized` automatically implies `stylized: True` and `position: middle` in the overlay config unless `position` is explicitly overridden.
- `**cta:**` generates a second overlay object with `style: "cta"`, `position: "bottom"`, `color: "white"`, `scrim: true`.

---

## 2. Episode directory structure

Every episode gets a standardized directory:

```
episodes/
└── comparison-spiral/
    ├── storyboard.md              ← unified storyboard (source of truth)
    ├── refs/                      ← character reference images (symlink or copy)
    ├── keyframes/
    │   ├── v01/                   ← first generation pass
    │   │   ├── FRAME_01.png
    │   │   ├── FRAME_02.png
    │   │   └── ...
    │   └── v02/                   ← re-gen pass (if needed)
    ├── captions.py                ← auto-generated from storyboard.md
    └── final/                     ← overlay output (production-ready PNGs)
        ├── FRAME_01_captioned.png
        └── ...
```

### Directory conventions

- `episodes/` lives at the repo root.
- Episode directory name = the `episode` field from storyboard frontmatter.
- `refs/` can be a symlink to a shared character references directory (e.g., `../../refs/glytoons/`).
- `keyframes/` uses versioned subdirectories (`v01/`, `v02/`, ...). The pipeline always writes to the next available version.
- `captions.py` is auto-generated but user-editable. If the user modifies it, the pipeline respects those edits and does not overwrite without confirmation.
- `final/` is the overlay output directory. Cleared and re-rendered on each overlay run.

---

## 3. Storyboard parser

**New file:** `pipeline/parse_storyboard.py`

Reads a unified storyboard markdown file and produces two outputs:

### Output A — Shot list (for keyframes skill)

```python
[
    {
        "frame_id": "FRAME_01",
        "slug": "hook",
        "prompt": "Dozer sitting on the ground scrolling his phone..."
    },
    ...
]
```

This is what the keyframes skill currently expects from its "parse the storyboard into individual shots" step. The parser replaces the ad-hoc parsing in Step 2 of the keyframes workflow.

### Output B — Captions config (for overlay engine)

```python
FRAMES = [
    {
        "file": "FRAME_01.png",
        "overlays": [
            {
                "text": "you before the scroll",
                "position": "bottom",
                "style": "hook",
                "color": "white",
                "scrim": True,
                "scrim_side": "bottom",
            }
        ]
    },
    ...
]
```

This is the exact format `overlay_engine.py` already consumes. The parser generates a valid captions `.py` file that can be used directly or edited by the user before rendering.

### Derivation rules for overlay defaults

When generating the captions config from the storyboard, the parser applies these defaults (matching the design rules in `reading-ux-principles.md`):

| Storyboard field | Overlay field | Default |
|---|---|---|
| `caption` empty/missing | `overlays` | `[]` (no text) |
| `style` missing | `style` | `"body"` |
| `position` missing | `position` | `"bottom"` |
| `position` missing + `style: stylized` | `position` | `"middle"` |
| `color` missing | `color` | `"white"` |
| `scrim` missing + caption present | `scrim` | `True` |
| `scrim` missing + caption empty | `scrim` | omitted |
| `scrim_side` | derived | same as `position` (`"bottom"` or `"top"`) |
| `style: stylized` | `stylized` | `True` |
| `font` present | `font` | resolved to full path: `assets/fonts/{value}` |
| `contrast` missing | `contrast` | omitted (uses stylesheet default) |
| `cta` present | second overlay | `{ style: "cta", position: "bottom", color: "white", scrim: true, scrim_side: "bottom" }` |

---

## 4. Filename standardization

Both skills must agree on filenames.

**Convention:** `FRAME_NN.png` where `NN` is zero-padded from the storyboard header.

### Changes required

**Keyframes skill** currently names outputs based on shot IDs from the storyboard (e.g., `SH01_A_wave.png`). Change to:
- Output filename = `FRAME_NN.png` derived from the `## FRAME_NN` header.
- The slug is NOT part of the filename. It's metadata only.

**Overlay engine** already expects `FRAME_01.png` etc. in the captions config. No change needed — the parser generates the correct `"file"` values.

---

## 5. Pipeline runner

**New file:** `pipeline/run_pipeline.py`

Orchestrates all stages in sequence.

### Interface

```
python pipeline/run_pipeline.py \
  --storyboard episodes/comparison-spiral/storyboard.md \
  [--refs episodes/comparison-spiral/refs/] \
  [--skip-keyframes]   \
  [--skip-overlay]     \
  [--auto-regen]       \
  [--edit-captions]
```

### Stages

```
Stage 1: PARSE
  ├── Read storyboard.md
  ├── Parse frontmatter → project preset, episode name
  ├── Parse frames → shot list + captions config
  └── Create episode directory structure if it doesn't exist

Stage 2: KEYFRAMES
  ├── Load project preset (character descriptions, style prefix, refs)
  ├── Generate hero image (FRAME_01) → show to user for approval
  ├── Generate remaining frames in parallel
  ├── Run QC review on all frames
  ├── Auto-regen failures if --auto-regen (max 3 retries)
  └── Output: episodes/{episode}/keyframes/vNN/FRAME_*.png

Stage 3: CAPTIONS
  ├── Generate captions.py from storyboard
  ├── If captions.py already exists and has been modified:
  │   └── Ask user: overwrite, merge, or skip?
  ├── If --edit-captions: pause for user to review/edit captions.py
  └── Output: episodes/{episode}/captions.py

Stage 4: OVERLAY
  ├── Run overlay_engine.py with:
  │   --input  episodes/{episode}/keyframes/vNN/  (latest version)
  │   --output episodes/{episode}/final/
  │   --captions episodes/{episode}/captions.py
  └── Output: episodes/{episode}/final/FRAME_*_captioned.png

Stage 5: REPORT
  ├── Total frames generated
  ├── QC pass rate
  ├── Any remaining QC issues
  ├── Output paths
  └── "Run with --skip-keyframes to re-render overlays only"
```

### Skip flags

- `--skip-keyframes` — Skip stages 1-2. Use existing keyframes in the latest version folder. Useful for re-running overlays after editing captions.
- `--skip-overlay` — Skip stages 3-4. Generate keyframes only, no text overlays.
- `--edit-captions` — Pause after generating `captions.py` so the user can edit before rendering.

---

## 6. Project presets

Project presets move out of the keyframes SKILL.md and into their own directory:

```
presets/
├── glytoons.md
└── [future-project].md
```

### Preset file format

```markdown
---
name: glytoons
default_aspect: "9:16"
default_model: gemini-3.1-flash-image-preview
position_lock: "Dozer LEFT, GLY RIGHT"
---

## Style Prefix

2D flat animation style, clean vector line art, bold ink outlines,
no photographic textures. 4K, high saturation, sharp focus.
Cute chibi aesthetic — characters should look adorable with
exaggerated chibi proportions.

## Characters

### DOZER (brown bull)

Cute chibi brown bull/bison with fluffy dark brown fur, small horns,
round face, big dark eyes, pink snout. Wearing white t-shirt with
exactly ONE "GLYTOONS" rainbow logo and densely scattered colorful
cartoon character face sticker-prints, white shorts with same dense
colorful character prints, WHITE sneakers with yellow lightning bolt
accents on the sides. Stubby arms ending in dark brown hooves
(NOT human hands). Visible tail from side/back views.

### GLY (robot)

Extremely cute round chibi robot. Oversized spherical helmet head
1.5-2x the size of the tiny body. Iridescent blue-purple nebula
visor faceplate. Tiny stubby limbs. Sleek white-silver innerspace
suit with distinct blue-cyan light path LINES along armor panel
seams. "GLY" sigil emblem on chest (rendered as sigil design,
NOT plain text). Bronze-orange scarf/cape. Round headphone ear
pieces on helmet sides. NOT on spaceboard unless the shot
explicitly calls for it — default is standing on the ground.

## Prompt Suffixes

- "Do NOT include any text, watermarks, labels, or metadata overlays anywhere in the image."
- "Both characters at the SAME scale — side by side on the same ground plane."

## Default Refs Directory

Look for `Character References/` containing:
- `Chibi_GLY_Reference.png`
- `Dozer_Hero_Reference.png`
```

The pipeline runner loads the preset named in the storyboard's `project` frontmatter field.

---

## 7. Unified skill (Claude Code integration)

**New file:** `.claude/commands/carousel.md` (or `.claude/skills/carousel-pipeline/SKILL.md`)

This is the user-facing skill that wraps the pipeline runner. It replaces the need to invoke `/keyframes` and `/carousel-overlay` separately.

### Trigger phrases

- "make a carousel"
- "run the pipeline"
- "new episode"
- "generate carousel from storyboard"
- "/carousel [storyboard path]"

### Workflow

1. Accept storyboard path or inline content
2. If inline: create `episodes/{episode}/storyboard.md` from it
3. Run `pipeline/run_pipeline.py` with appropriate flags
4. Show hero image for approval (pause point)
5. Continue generation
6. Show QC report
7. Generate captions, offer edit pause
8. Render overlays
9. Show final frames for review

### Re-entry points

The skill supports partial runs:
- "regenerate frame 3" — re-runs keyframe generation for a single frame
- "update the captions" — re-parses storyboard, regenerates captions.py, re-renders overlays
- "re-render overlays" — runs overlay engine on existing keyframes with current captions.py
- "run QC on frame 5" — runs QC reviewer on a single frame

---

## 8. Changes to existing skills

### keyframes/SKILL.md

- Remove the GLYTOONS character descriptions (moved to `presets/glytoons.md`)
- Change storyboard parsing to use `pipeline/parse_storyboard.py` instead of ad-hoc parsing
- Change output filename convention from `SH01_A_description.png` to `FRAME_NN.png`
- Load preset from `presets/{project}.md` based on storyboard frontmatter
- Load QC rules from `qc/qc-rules.md` (repo-relative) instead of `~/.claude/qc-rules.md`

### carousel-overlay/SKILL.md

- No changes to `overlay_engine.py` — it already works with the captions format the parser generates
- Update SKILL.md workflow to reference the pipeline runner as the primary entry point
- Add note that `captions.py` can be auto-generated from `storyboard.md`

### qc/qc-reviewer.md

- Update refs directory lookup to check `episodes/{episode}/refs/` first
- Update QC rules path to `qc/qc-rules.md` (repo-relative)

---

## 9. New files summary

| File | Purpose |
|---|---|
| `pipeline/parse_storyboard.py` | Parses unified storyboard → shot list + captions config |
| `pipeline/run_pipeline.py` | Orchestrates all stages |
| `presets/glytoons.md` | GLYTOONS project preset (extracted from keyframes SKILL.md) |
| `specs/unified-pipeline.md` | This document |
| `episodes/.gitkeep` | Episode output directory |

---

## 10. Migration path

### Phase 1 — Parser + directory structure
Build `parse_storyboard.py`. Establish episode directory convention. Convert the `comparison-spiral` example to the unified storyboard format.

### Phase 2 — Pipeline runner
Build `run_pipeline.py`. Wire it to the existing keyframes and overlay skills. Extract presets.

### Phase 3 — Unified skill
Create the `/carousel` skill that wraps the pipeline runner for Claude Code integration.

### Phase 4 — Backfill
Update existing skills to reference repo-relative paths instead of `~/.claude/` paths. Move QC rules into the repo.
