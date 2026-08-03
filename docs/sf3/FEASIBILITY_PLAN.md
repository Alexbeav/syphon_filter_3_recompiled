# SF3 recompilation feasibility plan

## Decision

Can the mature PSXRecomp lifecycle reach SF3's retail frontend and Mission 1
with materially less title-specific machinery than the hybrid bring-up while
retaining deterministic evidence and honest fallback reporting?

## Gates

### R0 — reproducible generation

Generate twice from the same user-owned SCUS-94640 disc and tracked OpenBIOS.
Normalize only documented host/output-root fields. Both manifests and builds
must agree.

### R1 — resident executable and TITLE

Reach executable entry, CRT, `Game_Main`, application loop and stable TITLE.
Record CPU/application state, device/display state and dispatch tiers twice.

### R2 — overlay lifecycle and operable frontend

Capture TITLE/MENU/MOVIE/INIT variants, compile/cache them, prove clean reuse
and real invalidation, quantify fallback, and operate Story/Mission 1 only at
retail readiness/sample boundaries.

### R3 — Mission 1 vertical slice

Reach state 8, authored opening and state-0 player control. Validate input,
GPU/display pages, SPU/XA, dialogue, combat, death/restart and one checkpoint.

### R4 — architecture report

Compare setup time, title-specific code/configuration, native/fallback share,
correctness, determinism, performance, campaign cost and licensing against the
hybrid oracle.

## Stop conditions

Stop for review if progress requires proprietary tracked data, generated-code
edits, forced state/progression, native substitute behavior, weakened
determinism, title-address containment or incompatible code transfer. An
unresolved invariant needs corpus consultation and three bounded falsification
attempts before it can be declared the first divergence.
