# PGXP Gate-B black-screen rejection

## Current disposition — 2026-08-05

The historical rejection below correctly cleared PGXP as the owner. R20 later
fixed the generic CD DMA sector-ownership defect at the same handoff. A rebuilt
candidate now passes the formerly failing boundary twice with PGXP off, twice
with geometry precision only and twice with geometry plus perspective-correct
textures. All six diagnostic runs consume the bounded 3,000-sample route,
observe retail state 8 and live state 0, retain 45 state-0 page samples, and
produce no non-startup freeze dump or semantic stall.

The counters prove feature engagement rather than config-only success: off has
zero geometry/perspective hits; geometry-only has roughly 2.1k geometry hits
and zero perspective hits; full PGXP has roughly 2.1k of each at the final
periodic sample. Two ordinary uninstrumented Release processes also consume the
complete 42,480-sample route. Their normalized stdout and both 128 KiB card
images are byte-identical, and neither run emits a freeze dump.

This qualifies the automated route only. The existing polling comparator
reports transient depth/state-sequence differences because separate diagnostic
processes can observe or miss one-frame intermediates; the required
TITLE -> state 8 -> state 0 milestones, following retail transition, framebuffer
origins and subsystem liveness agree. No exact diagnostic-frame determinism is
claimed. Visible 4x/4:3 off/full A/B acceptance remains required before PGXP is
enabled in the accepted presentation.

Date: 2026-08-04

## User-visible symptom

The combined PGXP candidate and the later geometry-only candidate both reach a
black screen after the Mission 1 briefing. Mission dialogue continues, followed
by later conversations, while music/dialogue becomes choppy. The window stays
responsive but the mission never becomes visible or controllable.

This rejects the candidates at Gate B. No PGXP qualification or milestone claim
is valid yet.

## Captured route and first divergence

The geometry-only evidence launcher captured 8,619 normalized input samples in
`evidence/human-transition-20260804-154600/manual-input.psxpad` (untracked).
Replaying that exact payload under the diagnostic observer gives this stable
sequence:

- retail state 8 at frame 2571/2572;
- retail state 0 at frame 2637/2638;
- dispatch depth falls from 1 to 0 at frame 2683;
- dirty-interpreter instructions and static dispatch then stop changing;
- the runtime reports a `spin_freeze` near frame 2760;
- terminal owner is BIOS function `0x000029CC`, with `I_STAT=0x1` and
  `I_MASK=0`, return address `0x8001F49C`, and last observed guest store at
  `0x8001E6A0`.

The last-store PC is an ordinary RAM write inside retail code, not proof that
the same instruction wrote `I_MASK`. Complete I_MASK write history remains
missing because the current `imask_trace` debug response is malformed JSON.

## Bounded falsification attempts

The private validation/GPU contracts and SF2/Tenchu PGXP notes were consulted.
Three bounded checks used the same captured payload and required state 8,
state 0, state-0 display samples, and absence of a semantic stall:

1. New runtime, geometry precision on, perspective textures off: freezes.
   Geometry hits remain zero before the divergence, so a corrected primitive
   cannot be the trigger.
2. Same new runtime, all PGXP switches off: reaches the same state sequence and
   stops advancing the same work counters.
3. Pre-PGXP diagnostic runtime from the accepted 4x/widescreen checkpoint,
   forced to the source-owned 4:3 settings profile: freezes at frame 2760 with
   the same `146,028,664` dirty-instruction count, BIOS function, store PC,
   interrupt state, return address and transition boundary as attempt 1.

This clears PGXP geometry and perspective rendering as the owner. The exact
input timing exposes a pre-existing CPU/scheduler/interrupt lifecycle defect.

## Invalidated evidence

The two earlier 42,480-sample PGXP runs are not campaign evidence. Both emitted
an early freeze dump but later reached the host-side input-sample limit. Sample
exhaustion proved host-frame progress only; it did not prove guest semantic
progress. Their qualification claim is withdrawn.

`observe_input_route.py` now:

- can require named retail states and a minimum count of state-0 display-page
  samples;
- isolates freeze reports in the evidence directory;
- rejects non-startup freeze dumps;
- rejects a depth-0 terminal interval where dirty and static work counters are
  unchanged for at least 1,200 observed frames.

Frame-zero detector dumps are recorded separately as startup noise rather than
accepted as a gameplay freeze.

## Current stop boundary

The unresolved invariant is the state-0-to-BIOS scheduler/interrupt handoff
that leaves pending VBlank/CD work masked and no guest execution advancing.
No state forcing, I_MASK repair, synthetic wakeup or other containment is
permitted. The next investigation must first obtain the exact final I_MASK
write and the retail/BIOS call chain into `0x000029CC`, then correct the generic
runtime invariant and add a focused regression.
