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

A later timestamped ordinary route sharpened the transition symptom: intro XA
audio remained audible while video, visible input response and mission progress
all stopped. The neutral-bookended `PSXPAD2` artifact has 3,194 contiguous
samples, 333 active samples in 59 runs, and repeated Cross/Start activity as
late as sample 3045. This confirms host input publication at the retail SIO
boundary and contradicts a single lost-edge explanation; it does not prove
guest input consumption. The artifact remains ignored and is not part of the
source repository.

## Consumed leads

Generic load-delay and encoded-JALR corrections remain covered by framework
regressions, but TITLE has not independently isolated either prior failure
mode. The nested-call IRQ path is exercised (`irq_need_delivery` nonzero and
`irq_skip_nested=48` in both clean runs), but no counterfactual has yet made the
SF2 fix independently causal for SF3.

The SF2 CFG load-delay portability report was rechecked against this exact
failure. SF3 already includes the generic CFG correction at `663ac4a`, its
focused code-generation regression, and regenerated products, contradicting a
missing known-patch explanation. The conservative patch's documented boundary
cases remain candidates only if a first divergent instruction reaches one.
`PSX-MDEC-005` remains directly applicable: live XA audio does not prove MDEC
decode, display or completion. Repeated recorded inputs contradict `FAIL-018`
as the sole owner. The next bounded check must separate stalled MDEC/CD/IRQ
progress from completed decode with a failed execution-tier/lifecycle handoff.

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

The paired diagnostic observer now labels every retained display sample with
its VRAM display origin, records retail application transitions and bounded
subsystem snapshots, and immediately preserves the first retained frame that
matches the observed corruption signature. Source guards prohibit active TCP
input or guest writes. Two 1,132-file generations match (tree SHA-256
`dea76d13f43caa9a327e48427c4b3fc2510091bfb8c2b60ef486acf77d30dffe`),
and matching ordinary/diagnostic Release products link from the same source
identity. Neither was launched, so page coverage and replay behavior remain
unverified.

An even-cadence observer was contradicted as a valid two-page witness because
SF3 alternates pages each frame; the corrected observer samples adjacent ring
frames. The 47-test suite includes a bounded comparator for matching semantic
transitions, distinct display origins, live subsystem snapshots and absence of
the known corruption signature. It deliberately leaves human presentation,
audio quality, pause/death/checkpoint and mission-completion gates open.
Timestamped recorder output preserves intermittent failed routes instead of
blocking or overwriting the next attempt.

The first timestamped route structurally validates and captures the audio-only
stall. Its localization order was an exact hidden, silent diagnostic replay:
first compare retail state, XA and MDEC counters; inspect CD/IRQ and MDEC DMA if
decoding does not advance; and inspect dirty/static lifecycle ownership only if
decode completes without a retail transition. Instrumented output is not
promoted to ordinary-Release acceptance evidence.

Permissioned replay narrowed the audio-only failure away from deterministic
guest ownership. The exact route reaches state 8/state 0 with 215 decoded movie
frames, advancing CD delivery, zero dispatch misses and clean two-page output
under repeated diagnostic OpenGL, software, copied-card and corrected ordinary
Release runs. The ordinary replay helper itself required a generic Windows
process-wait correction: a GUI-subsystem executable must be waited through its
process object before logs or exit status are evidence.

The remaining visible-only symptom matches a pre-existing runtime diagnosis:
an NVIDIA swap queue can block `wglSwapBuffers` for about 1.5 seconds while the
audio callback continues, making video, emulation and input appear frozen. The
generic vsync self-heal covered only SDL renderer presents; direct OpenGL swaps
bypassed it. All guest-vblank OpenGL paths now share the same recovery threshold,
while the wall-clock pacer preserves guest rate. This is a strong owner inference,
not confirmed end-to-end causality, until the user's visible run passes or
records recovery activation.

The corrected framework passes 48/48. Two 1,132-file generations match at tree
SHA-256 `ebb7812bed9a129f1e0a2df21c6cdfcdcf3f6fc28d1b636c3f1ec660ee68983b`;
ordinary products normalize to
`d503db02073df5f35979b936f2a20604a6f1233499fb4fe64e3daec042187ea5`.
Two ordinary bounded replays complete and the matching diagnostic route reaches
state 8 at frame 2317 and state 0 at 2386 with clean subsystem evidence. The
desktop candidate is retargeted, but representative readiness remains open
pending visible and connected Mission 1 acceptance.

The next visible run contradicted that presentation inference for the observed
fatal: it recorded zero slow swaps and no vsync recovery, showed catastrophic
Mission 1 geometry/texture corruption and exited near frame 2751. The product
was missing its compiled SF3 cache and ran about 134.10 million dirty-interpreter
instructions. Restoring the exact four-region SF3 cache halves that instruction
load on the recorded route; a diagnostic run measures 8.83 million native
overlay dispatches against 16.8 thousand overlay fallbacks and completes with
clean two-page output. Two ordinary exact-route replays also complete. This is
a narrowed execution-tier amplifier, not yet the proven corruption owner.

New candidate `PSX-OVL-004`: a release overlay compiler must consume the
runtime's immutable additive capture history, not only its replace-on-latest
manifest. The generic loader now unions exact-byte variants and their evidence,
preserves reused-address variants and tolerates a torn sibling. The registered
49-test suite covers the contract. SF2 recomp should independently validate it.
The human recorder now waits on its GUI-subsystem process object before testing
for a finalized route.

## Quality debt

| Debt | Likely owner | Removal gate |
| --- | --- | --- |
| Briefing can appear to fail while audio continues | unresolved; latest fatal contradicts swap backpressure and exposes missing-cache/heavy-fallback amplification | cache-complete visible candidate plus two connected ordinary Release transitions |
| State-0 world textures can be corrupt | GPU/VRAM unresolved | authoritative software/OpenGL comparison and correct two-page multi-room output |
| Existing probe ends after initial movement | validation harness | connected death/restart, checkpoint and Mission 1 completion replay |

## Representative-slice closure — 2026-08-03

The cache-complete human route is accepted through live Mission 2 gameplay. It
contains 42,480 retail PAD samples and covers Mission 1 death/checkpoint reload,
completion, FMV, new-card save and the complete Mission 2 frontend handoff. Two
ordinary isolated-card replays complete at the exact bound and generate
byte-identical card images. A passive diagnostic replay records 14 retail state
transitions, 1,011 state-0 display samples and zero known-corruption matches.

This closes the SF3 representative-slice validation gap and narrows the earlier
fatal to a cache-empty release-closure failure. It does not promote the brief
Mission 1 start-frame graphical defect as fixed. It also exposes the next
execution-tier boundary: Mission 2 raises ordinary dirty execution to 125.35M
instructions; the diagnostic endpoint measures 9.72M native overlay dispatches
and 292K fallbacks with four regions loaded. SF2 recomp remains the independent
validator for additive-history compilation; SF3 now independently demonstrates
that deterministic card artifacts can strengthen a long retail lifecycle route.

## Provenance

No retail input, executable, generated C, overlay capture, RAM/state, card or
media payload is tracked. Oracle projects are read-only. Reusable findings were
returned to the private corpus in `87e6c7a`; input-witness status and the
independent-validator assignment were returned in `76393af`. The parentless
public source snapshot is published as `Alexbeav/syphon_filter_3_recompiled`.
