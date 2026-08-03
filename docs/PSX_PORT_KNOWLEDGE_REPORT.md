# PSX port knowledge report — SF3 recompilation feasibility lab

- Date: 2026-08-03
- Branch: `experiment/sf3-recomp-feasibility`
- Framework lineage: SF2 lab `4f811c2`; PSXRecomp
  `0cfa9fe0a8da944e9f694a24361b4973c57131ea`
- Target: USA `SCUS-94640`
- Lane: PolyForm Noncommercial static/captured-overlay feasibility experiment

## Current state

Minimum and stretch feasibility gates are achieved. Two clean generated trees
and their normalized Release products match. Two clean headless/silent native
runtime processes boot OpenBIOS, enter the authentic executable at frame 714,
call `Game_Main` and its retail application loop, and reach stable TITLE
depth/state `2/4` with exact matching frame fingerprints. Two further clean,
packaged-probe processes select retail New Game, reach Mission 1 state `8/2`,
pop to state `0/1`, poll the retail Mission 1 PAD path and visibly move the
player in the rendered Tokyo scene. The first user FMV report is also resolved:
two hidden-OpenGL runs render the retail New Game Tokyo intro without stale
colored VRAM bands and continue through the same Mission 1 gates.

## Consumed leads

Generic load-delay and encoded-JALR corrections remain covered by framework
regressions, but TITLE has not independently isolated either prior failure
mode. The nested-call IRQ path is exercised (`irq_need_delivery` nonzero and
`irq_skip_nested=48` in both clean runs), but no counterfactual has yet made the
SF2 fix independently causal for SF3.

`PSX-HLE-001` is irrelevant to this boundary because the active image is
verified OpenBIOS and the backend is LLE. `PSX-GPU-001` remains relevant: SF3
uses alternating draw/display pages and both clean runs retain live GP0
draw/copy/environment traffic. `FAIL-009` / `PSX-GPU-002` is now confirmed by
the user symptom and clean counterfactual: entering packed 24-bit ownership
must first synchronize authoritative OpenGL FBO state into CPU VRAM. Depth-24
fills are dual-owned and packed movie uploads become CPU-owned. The generic
fix and regression contain no SF3 addresses or presentation substitutes.

Confirmed project finding and corpus candidate: a PS-X EXE header text extent is not an immutable-code
boundary. SCUS-94640 declares text through physical `0x1DC000`, then installs
frontend code into nominal text pages around `0x141000..0x17C000`. The generic
dirty-text guard and three-window overlay capture lifecycle correctly preserve
live bytes below the overlay floor. Five coherent current regions were
compiled (four code-bearing, one data-only), producing 122 validated native
candidates with zero invalidations or CRC misses. Interpreter ownership fell
from millions of dispatches to about 11–15 thousand while native-overlay
dispatch exceeded 13 million at the sampled TITLE boundary.

At state-0 control, one additional candidate is registered (123 total) while
the same four native cache regions remain valid. Two clean packaged runs
reported total static/native-overlay/fallback ownership of
`38.699%/61.187%/0.115%` and `38.564%/61.322%/0.114%`. Both retained zero
static misses, invalidations, stale blocks and revalidation CRC misses. The
state-8, pop and Mission 1 PAD register/SP call shapes match exactly; their
absolute frames differ slightly because TCP input is intentionally gated by
observed retail state instead of pretending host command arrival is
frame-deterministic.

The initial diagnostic Cross can be consumed while a fresh headless pad moves
coherently from analog to digital presentation. This was narrowed to the host
input/type boundary: retail state remains unchanged, and a released second
physical edge is accepted. The probe permits at most three state-checked edges
and records the count; both clean runs required two at TITLE and one at each
later gate. No guest state, processed-PAD record or callback is fabricated.

A second input-boundary finding is narrowed. Retail installs TITLE behind the
SCEA stream, so state `4/2` alone is not a movie-completion gate. The earlier
probe also left part of an eight-frame Cross pulse active after New Game was
accepted, allowing that physical input to skip the following intro. With a
persistent neutral pad, active TITLE-decode readiness and immediate release on
the observed transition, SCUS-94640 naturally plays the Tokyo car-arrival
movie before state 8. Neutral/auto-skip and MDEC-underflow hypotheses were
contradicted.

## Next decisive experiment

Independently validate the below-floor dirty-text capture finding in Tenchu.
SF2 recomp independently validates the OpenGL 15/24-bit ownership handoff; SF2
hybrid should validate release-on-transition input automation. Remaining work
is a user-visible build check, the final reproducibility/provenance audit and
normalized corpus return before a clean public source publication.

## Provenance

No retail input, executable, generated C, overlay capture, RAM/state, card or
media payload is tracked. Oracle projects are read-only. Reusable findings will
be normalized into the private corpus only after a committed project result.
