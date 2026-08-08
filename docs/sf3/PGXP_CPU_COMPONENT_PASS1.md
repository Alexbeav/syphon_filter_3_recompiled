# PGXP CPU component-provenance pass 1

Updated: 2026-08-08

Status: `human_accepted_precise_culling_minor_texture_wobble_remaining`

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

## Shared-edge and precise-culling checkpoint

Bounded frame-local adjacency and temporal tables found zero mixed
complete/fallback shared edges and zero recent eligibility flips, but 194
same-integer/depth/OT shared edges with different precise fractions. A
renderer-neutral edge reconciler now acts only on two complete, depth-matched,
packet-local representations. In two clean routes it safely reconciled 135
triangles; a whole-triangle guard rolled back three corrections that would
reverse winding. Human testing reports another material improvement, but
character seams, couch snapping and a distant bellhop face dropout remain.

Disabling perspective-depth correction did not change the face dropout, so the
DuckStation SF3 cached-Z warning is narrowed rather than confirmed as owner.
Read-only SF1 PC-port inspection supplied a closer invariant: its model
renderer culls using the same full-precision projection that it renders because
packed PS1 XY made thin triangles randomly change winding. Observation-only
SF3 instrumentation then compared retail NCLIP with the exact current PGXP FIFO
without changing MAC0. A bounded Mission 1 route measured 393,174 complete
comparisons and 34,122 sign disagreements, including 20,721 native-nonpositive
versus precise-positive cases; the latest sample was native area -2 versus
precise sign +1.

This confirms a precision split before GP0 submission. SF1 can fix it in its
native model renderer; SF3 retail has already discarded the material packet
when quantized NCLIP rejects the face. Any precise-NCLIP experiment must
therefore be isolated, optional, exact-three-vertex-only and explicitly report
that it changes guest-visible MAC0/branch behavior. Compatibility remains the
unchanged native oracle. SF2 Recomp remains a selective pass-1 comparison, not
a claim of solved PGXP; GT2 `FAIL-031` remains the negative validator.

## Optional precise-NCLIP experiment

The authorized behavior candidate is now implemented behind
`[video].precise_culling`, default off. It changes MAC0 only when precision
tracking has three valid projections whose packed values exactly equal the
current GTE SXY FIFO, and only when native and precise winding signs disagree.
Agreement retains the native NCLIP magnitude; disagreement substitutes only
`-1`, `0` or `+1`. A source-owned GTE regression proves both default-off
identity and the exact-match opt-in result.

Three diagnostic 3,000-sample processes reached briefing state 8 and live
Mission 1 state 0 with no known corruption signature. Their observer sampled
different transient application-state intermediates, so the strict diagnostic
transition-list comparator did not qualify a pair. The independent
observer-free gate did: two clean processes consumed all 3,000 samples with
identical normalized logs, stderr and cards. Card SHA-256 remains
`a717d08d...70cc3f` and `7706c7d4...8f58e8`. The diagnostic routes applied
32,081-32,682 exact-FIFO NCLIP overrides. This proves execution and activation,
not visual acceptance.

The human candidate deliberately isolates geometry plus precise culling with
perspective textures off. Its generated profile explicitly enables 16:9,
`widescreen.offer` and direct mouse camera. The next gate is an A/B at the
distant bellhop face, character seams and starting-room couch; native culling
remains the compatibility control.

Human validation accepts this candidate as good enough to ship. The distant
face loss and material character seams are resolved to the user's satisfaction.
Very minor texture wobble remains and is recorded as presentation debt rather
than represented as fully solved PGXP. Precise culling therefore graduates as
an accepted opt-in enhancement; default-off native culling remains the strict
compatibility path.
