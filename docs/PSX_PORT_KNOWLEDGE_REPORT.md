# PSX port knowledge report — SF3 recompilation feasibility lab

- Date: 2026-08-03
- Branch: `experiment/sf3-recomp-feasibility`
- Framework lineage: SF2 lab `4f811c2`; PSXRecomp
  `0cfa9fe0a8da944e9f694a24361b4973c57131ea`
- Target: USA `SCUS-94640`
- Lane: PolyForm Noncommercial static/captured-overlay feasibility experiment

## Current state

Minimum feasibility gate achieved at local milestone `bba60ce` plus the
subsequent ignored runtime evidence described below. Two clean generated trees
and their normalized Release products match. Two clean headless/silent native
runtime processes boot OpenBIOS, enter the authentic executable at frame 714,
call `Game_Main` and its retail application loop, and reach stable TITLE
depth/state `2/4` with exact matching frame fingerprints.

## Consumed leads

Generic load-delay and encoded-JALR corrections remain covered by framework
regressions, but TITLE has not independently isolated either prior failure
mode. The nested-call IRQ path is exercised (`irq_need_delivery` nonzero and
`irq_skip_nested=48` in both clean runs), but no counterfactual has yet made the
SF2 fix independently causal for SF3.

`PSX-HLE-001` is irrelevant to this boundary because the active image is
verified OpenBIOS and the backend is LLE. `PSX-GPU-001` remains relevant: SF3
uses alternating 320x240x15 draw/display pages, and both clean runs retain live
GP0 draw/copy/environment traffic. No 24-bit coherence symptom appeared, so
`PSX-GPU-002` is currently irrelevant.

New candidate finding: a PS-X EXE header text extent is not an immutable-code
boundary. SCUS-94640 declares text through physical `0x1DC000`, then installs
frontend code into nominal text pages around `0x141000..0x17C000`. The generic
dirty-text guard and three-window overlay capture lifecycle correctly preserve
live bytes below the overlay floor. Five coherent current regions were
compiled (four code-bearing, one data-only), producing 122 validated native
candidates with zero invalidations or CRC misses. Interpreter ownership fell
from millions of dispatches to about 11–15 thousand while native-overlay
dispatch exceeded 13 million at the sampled TITLE boundary.

## Next decisive experiment

Drive only retail-sampled PAD through Story/Mission 1, then measure state 8 and
state-0 player control. Independently validate the below-floor dirty-text
capture finding in Tenchu; use SF2 hybrid to validate persistent-page GPU
composition.

## Provenance

No retail input, executable, generated C, overlay capture, RAM/state, card or
media payload is tracked. Oracle projects are read-only. Reusable findings will
be normalized into the private corpus only after a committed project result.
