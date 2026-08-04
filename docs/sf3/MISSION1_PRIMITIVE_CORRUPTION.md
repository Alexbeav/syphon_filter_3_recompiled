# Mission 1 opening-room textured primitive corruption

Updated: 2026-08-04

## Normalized symptom

Visible OpenGL playtesting consistently shows oversized textured triangles or
quads in the first room of Mission 1. Long multicolored shards span and obscure
the room. The player model, HUD and portions of the underlying environment
remain coherent, and later Mission 1 rooms appear normal.

This is classified as malformed textured primitives, not generic missing or
corrupt textures. Expected behavior is the retail room with every world
primitive bounded to its authored geometry.

## Corpus consultation and bounded checks

The shared GPU contract requires authored ordering, persistent per-page VRAM
and inherited draw state to remain authoritative. Its capture contract also
warns that one ordering table is not necessarily the whole tick. The existing
SF3 hidden software/OpenGL captures did not reproduce the visible defect;
therefore they narrow but do not close visible ownership.

Checks were ordered to stop at the first divergence:

1. Capture the first malformed visible frame and its bounded GP0 ring.
2. Decode every textured triangle/quad packet and identify outlier screen
   coordinates, invalid packet lengths and mixed primitive strides.
3. Compare the same retail-input boundary under software and OpenGL. Matching
   packets with backend-only pixels assign ownership to rasterization;
   different packets assign it earlier to guest memory/DMA/OT traversal.
4. Verify E3/E4 drawing area and E5 draw offset plus TPAGE, CLUT and texture
   window state immediately before the first outlier.
5. Trace the packet's DMA/ordering-table provenance without replaying or
   deleting other same-tick submissions.

Candidate dispositions at intake:

- Incorrect packet length/primitive stride: **contradicted in the bounded
  hidden capture**. All 59 broad outliers have the expected GP0 family length.
- Incorrect primitive rejection: **confirmed at the generic GPU boundary**.
  The runtime tested a quad's two raster triangles independently. Verified PS1
  behavior tests the original four perimeter edges and drops the complete quad
  if any edge exceeds 1023 pixels horizontally or 511 vertically.
- Ordering-table overrun: **narrowed against** by valid packet lengths and
  coherent source/OT provenance; it remains open only if visible evidence
  differs from the captured route.
- E3/E4/E5 or texture-state leakage: **narrowed, not contradicted**. It is no
  longer the first divergence because malformed output follows directly from
  the proven quad rejection mismatch.
- Global texture corruption: **narrowed against** by coherent HUD/player and
  intact room regions.
- Generic 4x scaling failure: **narrowed against** because a related opening
  defect was observed before the 4x default, but a controlled 1x/4x visible
  comparison remains required.

## First proven divergence and correction

The 3,000-sample diagnostic route contains 41 hardware-oversized polygons.
Five shaded textured quads (`GP0 3Ch`) hit the exact bad case: one decomposed
triangle exceeded the limit while the other did not. The old runtime rendered
the surviving half. All five share the bounded world submission path at guest
PC `0x800F5B3C`; no packet rewrite or title address is used by the fix.

The generic correction adds an original-quad perimeter check and rejects the
whole command before draw offset or enhancement transforms, while retaining
the textured command's TPAGE latch. It also stops treating the internal
triangle split as a hardware rejection edge. A source-owned regression covers
both directions using synthetic coordinates, and the analyzer now labels
`hardware_oversize` and `partial_quad_risk` explicitly.

The framework suite passes 63/63. Two clean ordinary hidden OpenGL/dummy-audio
runs consume 3,000 samples and produce matching card hashes, also matching the
pre-fix smoke route. This proves lifecycle stability only. Visible Mission 1
acceptance remains required to confirm that the shards are gone.

No room-specific filter, guest patch or title-state containment was added. The
independent validating project is SF2 Recomp; it should replay a geometry-heavy
route and exercise the synthetic complete-quad/perimeter contract without
adopting any SCUS-94640 address or packet.
