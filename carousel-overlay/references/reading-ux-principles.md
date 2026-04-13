# Reading UX Principles

The design decisions in this system are grounded in eye tracking research,
broadcast subtitle standards, and editorial typography. This file explains
why each rule exists so you can apply them intelligently rather than
mechanically.

---

## 1. Subtitle stability — fixed Y anchors

**Rule:** All non-stylized text lands at the same Y position every frame.

**Why:** The fovea — the high-resolution center of vision — covers about
2° of arc. At phone-viewing distance, that's roughly 5–6 characters wide.
Everything outside is peripheral. When text jumps position between frames,
the reader has to spend attention *finding* the text before they can read
it. This cognitive overhead compounds across a 10-frame carousel.

Broadcast subtitle standards (BBC, Netflix, EBU) mandate fixed bottom
positioning for exactly this reason. The reader's eye learns the location
after frame 2 and parks there passively for the rest of the sequence.

**Implementation:** `LAYOUT["anchor_bottom_pct"]` and `"anchor_top_pct"`.
One number controls all frames simultaneously.

---

## 2. 60% line width cap

**Rule:** Text lines are capped at 60% of frame width.

**Why:** A single eye fixation covers roughly 7–9 characters of normal
text at reading distance. On mobile at 375px wide, a full-width line at
large font size (120–130px) forces 3–4 saccades (rapid eye jumps) per
line. Each saccade takes ~200ms and breaks the emotional processing of
the image. At 60% width, most lines read in 1–2 fixations.

Additionally, narrower text creates breathing room on both sides of the
frame — which is compositionally important when the illustration is the
primary content. Text should annotate the image, not compete with it.

---

## 3. Wrap first, shrink last

**Rule:** Lines wrap to fit the width budget before font size ever reduces.
Font only shrinks if wrapping still produces 3+ lines.

**Why:** Consistent font size across frames is a form of subtitle stability
too. If size varies frame-to-frame based on copy length, the visual rhythm
of the carousel breaks. The reader registers "something is different" and
allocates attention to figuring out why, rather than processing content.

Shrinking is reserved for copy that is genuinely too long — which means
the copy itself needs editing. The 2-line max is a content discipline
constraint as much as a layout one.

---

## 4. Max 2 lines

**Rule:** Hard cap at 2 lines per overlay.

**Why:** Carousel frames are viewed for 1–2 seconds each at swipe speed.
3-line overlays require ~800ms to read at comfortable pace. They slow the
carousel's emotional rhythm and push the viewer into "reading mode" rather
than "feeling mode." 

The right response to 3-line copy is to shorten the copy, not to shrink
the font. Good carousel copy is 3–5 words per overlay, structured like
dialogue, not like sentences.

---

## 5. Color arc as emotional signal

**Rule:** White on dark/desaturated frames → gold on emotional peaks.

**Why:** Color carries pre-attentive information — it registers before the
reader consciously processes the text. The transition from white to gold
signals the emotional register of the frame before the copy is even read.
Gold = warmth, earned emotion, resolution. The reader feels the shift
before understanding it.

Gold on the "save frame" (the emotional peak screenshot-bait moment) is
not decorative — it's a compositional trigger that makes the frame feel
worth saving even before the text is processed.

---

## 6. Stylized frames are a different genre

**Rule:** Stylized frames (`position: "middle"`, `stylized: True`) bypass
all subtitle stability rules. Different font, different size, different
placement, different contrast method.

**Why:** These frames are not captions — they're typographic moments.
The text *is* the image. The rules that govern informational caption design
(stability, consistency, efficiency) actively work against the goal of
these frames, which is to create a visual beat that lands like a panel in
a graphic novel.

For stylized frames: think poster design and editorial typography, not
subtitle design. The text should have compositional weight, breathing room,
and intentional placement relative to the illustration.
