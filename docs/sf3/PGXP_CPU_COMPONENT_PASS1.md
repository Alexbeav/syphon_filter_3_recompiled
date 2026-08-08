# PGXP CPU component-provenance pass 1

Updated: 2026-08-08

Status: `in_progress_major_improvement_residual_seams`

## Result

SF3 now preserves PGXP position provenance through the proven CPU packet path:
GTE result reads, shifts/masks/OR packing, scratchpad transport, inverse
expansion and MTC2 restoration. The implementation is generic and
component-aware. It retains guest-visible packed values and accepts a restored
component only when its signed GTE payload bits still originate from the exact
projected halfword. Diagnostic addresses proved the route; none are encoded as
title containment.

The previous first semantic divergence was an invalid restored SXY value at a
later SWC2 store after the original RTPT result had passed through
MFC2-to-GPR packing and scratchpad transport. Exact RAM address/generation and
packed-value matching therefore saw no final precision record. GPR and
scratchpad provenance now carry the current packed value plus independent X/Y
bit-origin masks. Unsupported or destructive operations invalidate metadata.

## Evidence

The source-owned GTE regression covers the complete
compress -> scratchpad -> expand -> MTC2 -> SWC2 path and a changed-bit
negative case. Static generated code, strict translation and both interpreter
lanes use the same propagation contract. The PGXP source contract and GTE
register-access tests pass.

Two clean hidden OpenGL 3,000-sample routes reached live Mission 1 state 0 and
exited normally:

| Run | Candidate triangles | Complete | Complete rate | Partial | Missing vertices |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 202,170 | 187,190 | 92.59% | 5 | 44,935 |
| 2 | 194,910 | 180,298 | 92.50% | 5 | 43,831 |

The prior paired result was 2,125/56,919 complete (3.733%) with 164,382
missing vertices. This proves a material coverage change, not merely enabled
switches or renderer activity.

## Human verdict and remaining divergence

The user reports that all previously observed wobbliness is gone, a major
visual upgrade. PGXP is nevertheless still in progress:

- seams remain visible in character models;
- at least one starting-room texture, the couch, snaps between two positions.

The corpus-matched next hypothesis is an eligibility boundary between adjacent
primitives: an all-corner-corrected primitive can be individually valid while
its unmatched neighbor remains at native coordinates. The couch may instead
be a temporal eligibility or perspective/depth transition. Neither hypothesis
is accepted without a bounded trace. Value-only matching, mixed-corner
correction and retained stale tags remain prohibited.

Next, classify complete/unmatched adjacency and frame-to-frame eligibility in
the starting room, add a renderer-neutral shared-edge regression, and correct
only the proven generic invariant. SF2 Recomp is the independent positive
validator; the GT2 stitched-terrain failure recorded as `FAIL-031` is the
negative validator.
