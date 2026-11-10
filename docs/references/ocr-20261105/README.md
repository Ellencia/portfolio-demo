# OMR motion reference

Reference commit: `0b219fd` (2026-11-05), before the subsequent portfolio redesign.

`manifest.json` records the source path and SHA-256 for every copied file. These HTML, CSS, JS, image and MP4 files are copied byte-for-byte from the same commit. `player.html` only adds a document encoding/viewport wrapper to the original artifact HTML. `index.html` compares the original MP4 with the current published MP4.

## Preserve the complete sequence

- Original first processing block: CSS start 2.2s, visible 4.1s, 2.93 iterations at 1.4s per turn. Labels change at 2.2, 3.0, 3.8, 4.6 and 5.4s; completion at 6.3s; result at 6.4s.
- Subsequent processing blocks: visible 1.8s, 1.29 iterations; completion is followed by the result 0.1s later.
- Rotation: -135deg to 225deg, `cubic-bezier(.6,.08,.4,.92)`. Preserve the SVG, parent entrance and label sequence together when comparing motion.
- Original common playback rate: 1.15. This page uses a 3000ms scene hold. Do not substitute a new total-duration target for these reference timings.
- The historical MP4 is a separate artifact: keep it intact rather than claiming a fresh browser render is the original video.

## Library decisions

See `../../FX_DESIGN.md`. GSAP is for new effects; existing CSS motion is not to be migrated wholesale. Rough Notation was applied to Harness A highlights. Perfect Arrows was retained for later use after its Harness A proposal was rejected. Lottie was a later planned stage, not the source of this OMR spinner.

Copying a rotation rule alone is not reproducing the original sequence. Compare normal playback and the encoded output with the original reference before describing a change as restored. This reference preserves historical motion, not a requirement to restore outdated explanatory claims in the main demo.
