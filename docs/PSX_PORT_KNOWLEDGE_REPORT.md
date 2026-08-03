# PSX port knowledge report — SF3 recompilation feasibility lab

- Date: 2026-08-03
- Branch: `experiment/sf3-recomp-feasibility`
- Framework lineage: SF2 lab `4f811c2`; PSXRecomp
  `0cfa9fe0a8da944e9f694a24361b4973c57131ea`
- Target: USA `SCUS-94640`
- Lane: PolyForm Noncommercial static/captured-overlay feasibility experiment

## Current state

Graduation state is `bootstrap_verified`; the representative slice is not
verified. Two clean generated trees
and their normalized Release products match. Two clean headless/silent native
runtime processes boot OpenBIOS, enter the authentic executable at frame 714,
call `Game_Main` and its retail application loop, and reach stable TITLE
depth/state `2/4` with exact matching frame fingerprints. Two further clean,
packaged-probe processes select retail New Game, reach Mission 1 state `8/2`,
pop to state `0/1`, poll the retail Mission 1 PAD path and visibly move the
player in the rendered Tokyo scene. The first user FMV report is also resolved:
hidden-OpenGL runs render both the restored pre-menu cemetery intro and the
retail New Game Tokyo intro without stale colored VRAM bands, then continue
through the same Mission 1 gates.

Subsequent ordinary human testing contradicted the implied readiness of those
bounded probe results. One cold launch accepted the briefing but did not start
Mission 1. A second launch entered gameplay with large world surfaces sampling
red/checkered corrupt texture data while geometry, actors and HUD remained
visible. State `0/1`, PAD polling, movement and zero dispatch misses therefore
proved bootstrap ownership only, not sustained retail correctness.

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

A separate CD ownership finding is confirmed. On the broken SF3 route, a
completed SeekL targeted `[51,54,39]` while the drive remained actively reading
`[50,31,14]` with READ status set. SeekL/SeekP must cancel the prior read
generation and pending INT1, clear READ/PLAY, and only then seek to the SetLoc
target. The generic correction restores the full retail cemetery intro before
TITLE and independently validates the SF2 recomp finding from `485b79b`.

An input-boundary finding remains narrowed but is secondary, not the cause of
the missing cemetery intro. State `4/2` alone is not a movie-completion gate,
and a multi-frame Cross pulse can outlive the transition that accepted it. The
probe now waits through SCEA and the cemetery movie to the actual TITLE stream,
then immediately releases accepted input. SCUS-94640 separately plays the
Tokyo car-arrival movie after New Game. MDEC underflow and neutral/auto-skip
causes were contradicted.

## Next decisive experiment

Independently validate the below-floor dirty-text capture finding in Tenchu.
SF2 recomp and SF3 independently validate the OpenGL 15/24-bit ownership
handoff and CD seek-retarget contract; SF2 hybrid should validate
release-on-transition input automation. The next decisive experiments are an
ordinary-Release lifecycle trace across accepted state-8 input and an
identical-route software/OpenGL comparison at the first corrupt gameplay frame.
Enhancement work remains prohibited until the representative Mission 1 gate
passes.

The user later observed a correct ordinary run, confirming intermittency rather
than resolution. One clean OpenGL, one clean software and one clean OpenGL
no-intermediate-screenshot route have not reproduced the corrupt surface. The
no-screenshot run contradicts a required screenshot-sync healing theory, while
the screenshot implementation itself remains a perturbing observer because it
synchronizes FBO-owned 15-bit state into CPU VRAM. A corrupt same-frame display
ring/software comparison is still required. The display ring must not be called
non-perturbing either: it avoids the CPU-VRAM write, but OpenGL pack/readback
can still affect host timing. Full-VRAM ring capture is now explicit opt-in;
the default stores only the displayed surface and applies a tested,
symptom-specific BGR555 color-ratio alarm for the observed red/checkered case.

Candidate reuse from `_shared/runtime` was converted into an SF3-bounded check:
the title-neutral `PSXPAD2` input timeline is integrated exactly at SF3's
normalized pad-to-SIO sample boundary, with a content-derived runtime/generated
image compatibility token and a source-owned regression. A fresh ordinary
SCUS-94640 Release links from one of two 1,130-file matching clean generations
(tree SHA-256
`b7ba1712d1c69be424842bc49a220b8d7bb9c2c8fea59546f8132495fe88625b`).
Runtime capture/replay is deliberately unclaimed
until the user records a neutral-bookended Mission 1 route and two clean
replays match. Tenchu remains the independent validator for the generic input
timeline; SF3 will independently validate the complete connected route.

The bounded-observer revision is reproducible across two fresh 1,132-file
generations (tree SHA-256
`0c4de43aa0af9f1dbc1df4379d91876582e0f760c4bb458dc0d250adea6df05e`).
Both ordinary Release and Release-optimized diagnostic configurations link,
and the source suite passes 45/45. Neither product was launched after the
user's no-run instruction, so the new TCP color handlers remain compile-tested
but runtime-unclaimed.

Bounded timeline replay can now use `--hidden-window`, keeping OpenGL/software
presentation active while stopping at the exact recorded retail-SIO sample
count; visible processes still reject the stop limit. A source-owned two-run
helper uses isolated cards/logs and dummy audio. Two clean 1,132-file
generations match (tree SHA-256
`aecb26b66492b0ca0074c9d58895483ca7686227313188f321ad9c96ce7febe5`),
the ordinary Release links, and 46/46 tests pass. The user prohibited launching
the product during this interval, so this remains a source/build-validated
route contract rather than replay evidence.

## Quality debt

| Debt | Likely owner | Removal gate |
| --- | --- | --- |
| Briefing can fail to hand off to gameplay | lifecycle/device/control unresolved | two clean ordinary Release transitions with matching semantic state |
| State-0 world textures can be corrupt | GPU/VRAM unresolved | authoritative software/OpenGL comparison and correct two-page multi-room output |
| Existing probe ends after initial movement | validation harness | connected death/restart, checkpoint and Mission 1 completion replay |

## Provenance

No retail input, executable, generated C, overlay capture, RAM/state, card or
media payload is tracked. Oracle projects are read-only. Reusable findings were
returned to the private corpus in `87e6c7a`; input-witness status and the
independent-validator assignment were returned in `76393af`. The parentless
public source snapshot is published as `Alexbeav/syphon_filter_3_recompiled`.
