# Framework convergence ledger

Updated: 2026-08-08

This is the evidence ledger for
[`FRAMEWORK_CONVERGENCE_PLAN.md`](FRAMEWORK_CONVERGENCE_PLAN.md). `candidate`
means the source/test delta is under audit; it does not authorize publication
or framework promotion.

## Identity

| Item | Identity |
|---|---|
| Common SF2/SF3 split | `4f811c252e63886c59da0a28ff22b7182dc38398` |
| Canonical framework head at intake | `0cfa9fe0a8da944e9f694a24361b4973c57131ea` |
| SF2 intake head | `1e6b27a8df162c36fc033efc7b50977169001927` |
| SF3 rollback/intake head | `09983367dbdd61794168f13bf7f063c0f6d28b10` |
| Unique histories | 39 SF2-only / 41 SF3-only commits |
| Whole-commit stable patch-ID matches | 0 |

No whole-commit match is expected: both labs combined reusable code with
different title evidence and tooling. Semantic/source-hunk equivalence is the
promotion unit.

## Semantic duplicate groups audited

| Group | SF2 commit | SF3 commit | Source comparison | Classification | Next action |
|---|---|---|---|---|---|
| OpenGL 15/24-bit VRAM handoff | `09be64b` | `31be333` | Same renderer facade, GP1 transition, CPU/FBO authority transfer, depth-24 dual-owned fill and 76-line title-neutral contract; comment-only/model wording differs | `generic-qualified` | use the cleaner generic source/test delta; exclude SF2/SF3 probes and reports |
| Active ReadN/ReadS to SeekL/SeekP retarget | `485b79b` | `db98b05` | Same `stop_read_stream()`, READ/PLAY clear, SEEK ownership ordering and title-neutral model; SF2 version has four additional explanatory/test lines | `generic-qualified` | use the stronger SF2 test text after verifying current SF3 behavior is identical |

These groups have independent SF2 and SF3 runtime evidence. They form the
provisional first canonical-framework batch because neither implementation
contains a title address or retail payload.

## Initial subsystem classification

| Subsystem | SF2 lineage leads | SF3 lineage leads | Initial class | Independent validation/gap |
|---|---|---|---|---|
| GPU 15/24-bit coherency | `09be64b` | `31be333` | `generic-qualified` | SF2 + SF3 |
| CD seek ownership | `485b79b` | `db98b05` | `generic-qualified` | SF2 + SF3 |
| deterministic input timeline | `89804a7`, `2009297` | `cbae3a9`, `e332f5e`, `2b1a7fb`, `6a3c9e5` | `generic-needs-reconciliation` | two independently evolved formats/helpers |
| additive overlay history/promotion | `17e9bba` | `70c167a`, `3dd2f7b`, `4250697` | `generic-needs-reconciliation` | generic cache rules mixed with title policy |
| OpenGL present recovery | inherited observation | `4f9aab6` | `generic-needs-second-consumer` | SF3 visible owner was later contradicted for one symptom |
| interpreter cycle deadlines | no isolated SF2 lead | `52ef738` | `generic-needs-second-consumer` | source-owned regression exists; independence pending |
| complete-quad rejection | no isolated SF2 lead | `642949e` | `generic-needs-second-consumer` | hardware-backed contract; second game pending |
| widescreen composition APIs | `65e3c49` through `a2b951c` | `04540b1`, `24cb538`, `f187fc3` | `generic-needs-reconciliation` | projection APIs generic; owner rules title-specific |
| PGXP base contract | `2eebc41` | current SF3 renderer/GTE implementation plus `0998336` diagnostics | `generic-needs-reconciliation` | exact eligibility aligns; provenance transport remains open |
| launcher enhancement Mods | `452cc0c` | profiles plus runtime settings | `generic-qualified-reference` | SF2 accepted; SF3 must become second lifecycle consumer |
| public setup/bootstrap | `91c94e6` through `1e6b27a` | `7ef45a9` | `publication-needs-reconciliation` | SF2 contract is newer and broader |

## Commit classification progress

The full exit gate is 80/80 post-split commits assigned to one class. The first
pass works by commit subject and changed paths; mixed commits are then split by
source hunk.

| History | Total | Classified | Remaining | Notes |
|---|---:|---:|---:|---|
| SF2 | 39 | 9 | 30 | VRAM, CD, input, PGXP, overlay, Mods and publication leads routed |
| SF3 | 41 | 16 | 25 | corresponding runtime leads plus title-policy commits routed |
| Combined | 80 | 25 | 55 | no runtime import yet |

## First-batch import manifest (provisional)

Only these paths are eligible for the first canonical patch series:

- `runtime/include/gpu_render.h`
- `runtime/src/gpu.c`
- `runtime/src/gpu_render.c`
- `runtime/src/gpu_gl_renderer.c`
- `runtime/src/gpu_vk_renderer.c`
- `runtime/src/main.cpp`
- `runtime/src/cdrom.c`
- `runtime/tests/test_gl_depth24_coherency.py`
- `runtime/tests/test_cdrom_seek_retarget.py`
- the minimal test registration hunks in `recompiler/CMakeLists.txt`

Explicitly excluded:

- every `docs/sf2`, `docs/sf3`, `lab/sf3` and title route/probe file;
- generated code, captures, cards and local build output;
- SF3 overlay configuration and all game addresses;
- unrelated later renderer, widescreen, PGXP or diagnostic changes sharing the
  same current files.

## Next audit

Compare the final canonical hunks against the current SF3 implementations and
the SF2 tests. If behavior already matches, the first framework commit should
be reconstructed from the generic hunks and tests rather than cherry-picked.
Then run both focused contracts and the full framework suite before creating a
framework tag or changing SF3 dependencies.
