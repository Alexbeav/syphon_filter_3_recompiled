# SF3 framework convergence plan

Updated: 2026-08-08

## Outcome

Make `Alexbeav/psxrecomp` the canonical reusable framework and reduce this
repository to a thin SCUS-94640 product layer: title identity/configuration,
bounded title hooks, campaign evidence and owned-input packaging. Preserve the
currently playable SF3 checkpoint throughout the work.

This is functional convergence, not a history rewrite. The accepted SF3 branch
and its ignored evidence remain recoverable while generic changes move through
small integration batches.

## Starting state

- Accepted SF3 checkpoint: `0998336`, 67/67 Release tests, two matching PGXP
  reason-classification runs and a clean focused GTE unit.
- Canonical public framework remote: `Alexbeav/psxrecomp`.
- Framework remote head: `0cfa9fe` (`framework/master`).
- SF3 is 56 commits ahead of that framework head.
- SF2 and SF3 split at `4f811c2`; current heads contain 39 SF2-only and 41
  SF3-only commits.
- Stable integration branch: `integration/framework-convergence`.
- No experiment/lab branch is pushed to the public SF3 repository.

Exact patch-ID comparison finds no whole-commit duplicates between the SF2 and
SF3 post-split histories. Similar fixes were committed with different title
tooling/docs, so convergence must compare behavior and tests rather than
cherry-picking commits by subject.

## Non-negotiable boundaries

- Never rewrite or force-push the accepted SF3 history.
- Never import SF2/SF3 addresses, generated code, retail bytes, routes, cards,
  captures or private corpus text into the framework.
- Every framework change needs a source-owned regression and a named second
  consumer.
- Compatibility 4:3, PGXP off and mouse camera off remain the semantic oracle.
- A batch is not promoted because it compiles; it must pass the gates below.
- Keep `origin/main` curated and source-only. Framework convergence is not
  permission to publish the lab branch.

## Repository shape

The convergence target has three layers:

1. **Canonical framework** — CPU/GTE, devices, GPU/VRAM, interpreter, overlay
   lifecycle, deterministic input, diagnostics, renderer-neutral enhancement
   APIs, launcher Mods and generic public-kit helpers.
2. **SF3 product layer** — SCUS-94640 manifest/configuration, proven camera and
   widescreen ownership profiles, campaign ledger and source-only setup recipe.
3. **Ignored evidence layer** — generated game, captures, routes, cards, logs,
   screenshots and user-owned media. This never crosses either public boundary.

## Work batches

### Batch 0 — inventory and dependency graph

Status: in progress.

Produce a ledger for every post-split SF2/SF3 commit and every changed
framework subsystem. Classify each item as:

- `generic-qualified` — source-owned regression and at least one proven game;
- `generic-needs-second-consumer` — reusable candidate lacking independence;
- `title-layer` — configuration/address/evidence belonging only to a game;
- `diagnostic-only` — bounded investigation support, not product behavior;
- `rejected` — negative experiment retained only as evidence;
- `publication` — source/owned-input packaging and policy.

The ledger also records ordering dependencies, the target framework commit and
the validation pair. This batch changes no runtime behavior.

Exit gate:

- all 80 post-split commits classified;
- semantic duplicate groups identified despite different patch IDs;
- first import batch contains no title addresses or private payload;
- accepted SF3 route/config identities remain unchanged.

### Batch 1 — hardware and execution correctness core

Promote the smallest already-qualified generic fixes first:

- OpenGL 15/24-bit VRAM ownership/coherency;
- CD seek/read-generation ownership and split-DMA sector latching;
- MIPS load-delay/JALR/IRQ and interpreter cycle-deadline corrections;
- complete-primitive PS1 rejection behavior;
- source/generated manifest guards needed by those fixes.

Candidate lineage pairs:

| Concern | SF2 lineage | SF3 lineage | Initial disposition |
|---|---|---|---|
| 24-bit VRAM ownership | `09be64b` | `31be333` | semantic duplicate group; extract generic regression |
| CD seek ownership | `485b79b` | `db98b05` | semantic duplicate group; reconcile exact behavior |
| split CD DMA sector latch | inherited/current SF2 runtime | `24cb538` and current regression | generic-qualified candidate |
| interpreter cycle deadline | no isolated SF2 commit yet | `52ef738` | needs second-consumer audit |
| complete quad rejection | no isolated SF2 commit yet | `642949e` | hardware-backed; needs independent runtime consumer |

Exit gate:

- canonical framework builds from a clean tree;
- framework Release suite passes;
- SF2 and SF3 source-owned regressions pass against the same framework commit;
- two ordinary SF3 compatibility runs preserve semantic/card identities.

### Batch 2 — deterministic lifecycle and overlay framework

Converge input timelines, process completion, capture history, overlay
publication/invalidations, safe interpreted fallback, freeze/crash reporting
and diagnostic observer separation.

SF3's `overlay_native = false` remains title policy. The generic framework owns
the switch and honest metrics; it must not encode why SCUS-94640 selects it.

Progress: the additive compiler/history contract, recoverable legacy `.d`
migration, deterministic input core, bounded crash serializers and generic
unpromoted-shard lifecycle are canonically adopted. The evidence classifier
that selects an SF3 quarantine remains project policy. Framework tests and two
fresh ordinary plus two separately configured diagnostic SF3 processes pass
with matching per-lane logs and common card hashes. Implementation scope is
qualified; the complete-Mission-1 replay exit gate below remains open.

Exit gate:

- two complete Mission 1 replays from clean processes;
- ordinary and diagnostic lanes remain separately qualified;
- matching cards and normalized semantic receipts;
- no compiled overlay is promoted merely because it links.

### Batch 3 — renderer-neutral enhancements and launcher Mods

Implementation checkpoint (2026-08-08): canonical commits `fdf23abd`,
`c1b24451` and `1ce3b001` provide dual bindings plus a complete resettable
enhancement state. SF3 has wired pre-activation reset for aspect, independent
geometry/perspective precision and mouse-camera state; 72/72 tests and a full
generated-runtime Release compile/link pass. Package/plugin definitions and the
automated feature matrix remain in progress; no visible test is requested yet.

Adopt one generic lifecycle for Widescreen, PGXP and Mouse Look. Use SF2
`452cc0c` as the launcher-Mod reference, but independently express SF3 title
configuration. Each feature must be available and independently toggleable,
default off, with same-process activation/reset tests.

Widescreen title addresses/owners and mouse-camera guards remain SF3 data. The
framework owns bounded APIs, lifecycle ordering and contaminated-state reset.

Exit gate:

- all-off identity against compatibility;
- each Mod passes alone and in representative combinations;
- pre-window aspect selection occurs before renderer creation;
- PGXP/mouse runtime activation occurs through narrow trusted APIs;
- two automated SF3 routes pass before a visible request.

### Batch 4 — PGXP provenance transport

Keep the current exact address/generation/packed-value and all-corner atomic
fallback. Instrument and prove the path that moves projected SXY/depth from GTE
results into final GP0 packet RAM. The leading generic hypothesis is
MFC2-to-GPR-to-RAM or a bounded RAM-copy construction path; it is not yet a
finding.

Do not use value-only matching. Add a title-neutral provenance-transfer unit
covering load delay, GPR overwrite, partial stores, timeline invalidation and
packet-copy invalidation. Validate with SF3 and SF2 or Tenchu.

Exit gate:

- materially higher complete-triangle coverage than 2,125/56,919;
- zero mixed/partial correction;
- two off/full automated route comparisons preserve retail state;
- no stitched-geometry cracks in the bounded regression;
- only then ask for the human motion A/B.

### Batch 5 — canonical dependency and public kit

Pin the SF3 source recipe to a durable canonical framework tag/SHA. Apply the
resolved successor to `PSX-PUB-001`: bounded clean acquisition, behavioral
rejection tests, CI/release-kit workflows, clean-room extraction/setup,
responsive launcher smoke and downloaded-asset audit.

Exit gate:

- exact curated export audited for retail/private/generated material;
- public workflows cannot acquire retail input or build the private game;
- clean-room kit rebuild and launcher smoke pass;
- user reviews the final public diff before push/release.

### Batch 6 — campaign continuation

Resume Mission 4 completion and the retail `4 -> 5` transition only after the
canonical framework is pinned and compatibility replay is stable. Continue one
adjacent mission seam at a time through the 19-row ledger.

## Gate applied to every implementation batch

1. Record the candidate commits and exact framework base.
2. Audit the diff for title addresses, payloads and private paths.
3. Run `git diff --check` and the relevant focused units.
4. Run the complete framework Release suite.
5. Regenerate the private SF3 candidate normally; never edit generated code.
6. Run two clean, silent compatibility processes at the named semantic gate.
7. Compare guest/device/dispatch/card evidence at equivalent boundaries.
8. Update the plan, current objective, devlog and quality debt.
9. Commit the small checkpoint.
10. Return normalized knowledge to a clean corpus tree; otherwise record why
    the return is deferred.

## Rollback points

- `0998336` is the pre-convergence playable SF3 rollback point.
- Each batch lands as its own commit or short dependency-preserving series.
- A failed batch is reverted on the integration branch; the accepted
  feasibility branch is not reset or rewritten.
- Generated candidates and routes remain ignored and are never used to repair
  source history.

## Immediate implementation queue

1. Finish the 80-commit classification ledger and semantic duplicate groups.
2. Audit the paired VRAM and CD fixes down to source-owned runtime/test hunks.
3. Create the first canonical-framework patch series from those two independent
   consumer fixes.
4. Build/test the framework series before changing SF3 configuration.
5. Regenerate and run the two-process SF3 compatibility gate.

No human testing is needed during Batches 0-2.
