# QC Rules

Rules learned from corrections during keyframe QC review.
Each rule is a specific, actionable check that the QC reviewer applies to generated images.

---

## Character: GLY

### Outfit & Design
- [2026-04-09] GLY has an ethereal, soft-glow, minimalist geometric design aesthetic — not cartoonish or overly detailed
- [2026-04-09] GLY's faceplate has a nebula eye effect — deep blue-purple swirls with high-contrast nebula field. Never a plain visor or simple colored lens
- [2026-04-09] GLY wears a sleek innerspace suit with armor paneling and asymmetric arm detail — not a generic spacesuit or simple robot body
- [2026-04-09] GLY has a chest emblem with the "GLY" sigil design. It must always be visible on the front of the suit
- [2026-04-09] GLY wears a bronze-orange scarf/cape
- [2026-04-09] GLY's suit has integrated blue light paths (Blokendavecont style)
- [2026-04-09] CRITICAL: GLY's suit must have distinct blue-cyan light path LINES integrated into armor panel seams — this is the #1 most commonly missed detail. Always include "distinct blue-cyan light path lines along armor panel seams" in every GLY prompt
- [2026-04-09] GLY's chest emblem must be rendered as the sigil design, NOT as plain "GLY" text — the model frequently renders it as a text label instead
- [2026-04-09] GLY has detail outlining on the suit — bold, clean ink outlines

### Props & Equipment
- [2026-04-09] GLY's innerspace board has sleek paneling with integrated light paths and VFX-ready light trails. It is NOT a generic skateboard or surfboard
- [2026-04-09] GLY should only be on the spaceboard when the shot description explicitly calls for it. Default is standing on the ground
- [2026-04-09] GLY also has a casual hoodie variant — dark gray fabric with abstract vibrant light and dust effusion effect. Only use when specified

### Body & Proportions
- [2026-04-09] GLY uses 2-focal chibi proportions: large head, small body. Head approximately 1.5x body height
- [2026-04-09] CRITICAL: GLY must look MORE chibi — rounder, cuter, with an oversized head relative to body. Current generations make GLY look too robotic/proportional. Exaggerate the chibi proportions — bigger head, stubbier limbs, rounder silhouette. GLY should read as cute first, robot second.
- [2026-04-09] GLY has bold, clean ink outlines throughout — the style is minimalist geometric, not painterly
- [2026-04-09] GLY has round headphones/ear pieces on the sides of the helmet

### VFX & Particles
- [2026-04-09] GLY-specific VFX: swirl-light particle effects (comet wake), hand-drawn particle fields, light trails that follow dynamic light forms
- [2026-04-09] Board wake trails show swirl-light particle effects behind the board when in motion

---

## Character: Dozer

### Outfit & Design
- [2026-04-09] Dozer wears a white t-shirt with "GLYTOONS" text in colorful/rainbow lettering across the chest
- [2026-04-09] The t-shirt also has colorful cartoon character face prints (sticker-style) scattered on it
- [2026-04-09] Dozer wears white shorts with the same colorful cartoon character prints as the shirt — prints must be dense and clearly defined, NOT sparse blobs
- [2026-04-09] CRITICAL: Dozer wears WHITE sneakers with yellow lightning bolt details on the sides — model frequently renders them as plain white, gold, or tan. Always specify "white sneakers with yellow lightning bolt accents on the sides"
- [2026-04-09] Dozer's outfit must be fully visible in every shot — aura/glow effects must NOT obscure the clothing

### Body & Proportions
- [2026-04-09] Dozer is a brown bull/bison character with dark brown fluffy fur/hair tuft on top
- [2026-04-09] Dozer has two small light-colored horns
- [2026-04-09] Dozer has a round face with big dark eyes and a pink snout/nose
- [2026-04-09] Dozer has a visible tail (brown with dark tuft) — should be visible from side/back views
- [2026-04-09] Dozer has dark brown hooves, not human hands — stubby arms end in hooves
- [2026-04-09] Dozer has chibi proportions — large head relative to body

---

## General Rules

### Composition
- [2026-04-09] When two characters interact, they must be at the same depth/scale in the frame — never one significantly behind the other unless the shot explicitly calls for it
- [2026-04-09] When describing one character waving/gesturing at another, include eye direction and body orientation toward the other character
- [2026-04-09] For close-up shots where a character is partially off-screen, show enough of their body to be recognizable — no disembodied hands or floating heads
- [2026-04-09] CRITICAL: Character positions must maintain spatial continuity across the storyboard. If Dozer is on the LEFT in SH01, he must stay on the LEFT in subsequent shots unless the camera explicitly changes. Characters should not swap sides between shots — this breaks carousel/reel continuity
- [2026-04-09] This is a carousel reel — each frame must feel like the next moment in a continuous scene. Same environment, same character positions, same spatial relationships

### Common Defects
- [2026-04-09] Watch for disembodied body parts — hands, heads, or limbs that appear without being attached to a complete body
- [2026-04-09] Watch for missing clothing when aura/glow effects are applied — the model sometimes strips outfit details to render the effect. In v02 of the aura shot, Dozer was rendered completely naked
- [2026-04-09] Watch for characters rendered at different scales when they should be the same size
- [2026-04-09] Watch for missing arms — both arms should be visible unless one is explicitly behind the body
- [2026-04-09] When a partially off-screen character places a hand on another character, the hand must be connected to a visible arm/body at the frame edge — never a floating hand or orb
- [2026-04-09] Aura/glow effects must use flat animation-style rendering (clean, soft-edged color fields) — NOT photorealistic fire, flame, or particle effects that clash with the cartoon style
- [2026-04-09] Dozer's clothing print density must match the reference — densely scattered colorful character faces, not sparse blobs or simplified shapes
- [2026-04-09] Generated images must NEVER contain text watermarks, labels, metadata overlays, or file codes. Always include "no text, no watermarks" in prompts
- [2026-04-09] Color palette must stay consistent across all shots in a storyboard — do NOT cool or desaturate the palette for "approach" or "transition" shots unless the storyboard explicitly calls for it. Default is warm, matching the hero image
