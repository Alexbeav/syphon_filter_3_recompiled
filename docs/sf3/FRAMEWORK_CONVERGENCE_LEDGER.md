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
| SF2 | 39 | 39 | 0 | every commit routed; mixed commits still require hunk extraction |
| SF3 | 41 | 41 | 0 | every commit routed; mixed commits still require hunk extraction |
| Combined | 80 | 80 | 0 | subject/path routing complete; no broad history merge permitted |

Class abbreviations below are `GQ` generic-qualified, `G2` generic candidate
needing reconciliation or a second consumer, `T` title layer, `D` diagnostic,
`R` rejected/negative evidence, and `P` publication/corpus documentation.
`mixed` means only audited source/test hunks may cross into the framework.

### SF3 post-split commit routing

| Commit | Class | Routing |
|---|---|---|
| `bba60ce` scaffold isolated lab | T | repository/title scaffold only |
| `a06f16a` deterministic TITLE/native overlays | G2 mixed | reusable execution evidence mixed with SF3 bring-up |
| `dd3049e` Mission 1 player control | G2 mixed | generic devices/diagnostics mixed with title route |
| `31be333` FMV presentation/input | GQ mixed | VRAM hunk independently matched; probes/docs stay SF3 |
| `024267e` standalone publication prep | P | superseded SF3 kit documentation |
| `db98b05` CD seek retarget | GQ mixed | CD hunk independently matched; docs stay SF3 |
| `abdc4b8` publication record | P | historical publication receipt |
| `29ee4c3` classification correction | P | status documentation |
| `cbae3a9` retail input timelines | G2 mixed | input contract candidate plus SF3 witness |
| `7d455ba` input witness handoff | T | SF3 evidence documentation |
| `fb912db` display corruption observer | D | bounded diagnostic candidate |
| `e332f5e` hidden route replay | D/G2 mixed | reusable stop contract requires reconciliation |
| `bf39137` route shortcut | T | local operator documentation |
| `2b1a7fb` complete route observer | D | passive SF3 diagnostic consumer |
| `6a3c9e5` route comparator | D/G2 mixed | reusable comparison rules plus SF3 schema |
| `48962bf` test shortcut | T | local operator documentation |
| `e42ce82` movie-stall classification | T | symptom evidence only |
| `4f9aab6` stalled present recovery | G2 | source regression; independent consumer pending |
| `70c167a` additive overlay closure | G2 mixed | generic history rules plus SF3 evidence |
| `acbd713` Mission 1 acceptance | T | connected-route evidence |
| `6aa349e` compatibility closure | D/T | source validation plus title closure |
| `3dd2f7b` unsafe overlays interpreted | T | evidence-backed SF3 policy |
| `4250697` overlay ownership control | G2 | generic switch/metrics; second title audit required |
| `6e654d5` 4x/SF2 bindings | T | SF3 test profile |
| `d4af170` Redux input profile | T | title product configuration |
| `509904c` direct mouse camera | G2 mixed | generic bridge plus SF3 guards/addresses |
| `8da2a4e` SCUS-94640 Redux profile | T | title configuration |
| `821246b` selectable mouse camera | G2 mixed | lifecycle candidate plus SF3 configuration |
| `52ef738` interpreter deadlines | G2 | generic regression; second consumer pending |
| `38f4de8` mouse combat/wheel | G2 mixed | generic input surface plus title mapping |
| `642949e` complete-quad rejection | G2 | hardware-backed regression; second game pending |
| `9ebae24` primitive localization | T | SF3 evidence report |
| `5e8f24b` route after quad fix | T | SF3 validation record |
| `40754c7` human Mission 4 breadth | T | campaign evidence |
| `04540b1` native-wide candidate | G2 mixed | generic composition plus SF3 ownership |
| `24cb538` handoff/widescreen qualification | G2 mixed | CD/GPU fixes plus title acceptance |
| `f187fc3` cinematic mattes | G2 mixed | generic effect API plus SF3 classifier |
| `7ef45a9` owned-input bootstrap | P | legal SF3 kit; predates current public contract |
| `ef099d4` campaign matrix | T | SF3 content ledger |
| `76dbda7` PGXP route qualification | T | SF3 evidence documentation |
| `0998336` PGXP reason diagnostics | D/G2 mixed | generic counters/tests plus SF3 result/report |

### SF2 post-split commit routing

| Commit | Class | Routing |
|---|---|---|
| `09be64b` OpenGL 24-bit ownership | GQ | clean generic commit; imported in Batch 1 |
| `485b79b` active reads on seek | GQ | clean generic commit; imported in Batch 1 |
| `89804a7` deterministic route validation | G2 mixed | generic timeline plus SF2 route tooling |
| `7613d6f` Mission 1 closure | T | SF2 evidence documentation |
| `2009297` final SIO timelines | D/G2 mixed | reusable boundary plus private route evidence |
| `6fb6a41` modernization profile | T | SF2 product configuration |
| `53208be` pass-one validation | T | SF2 evidence documentation |
| `5b64d86` aim tuning/remove turbo | T | title input choice |
| `2686df2` modernization pass two | T | SF2 phase scaffold |
| `65e3c49` native-wide/direct camera | G2 mixed | generic APIs plus SF2 ownership/addresses |
| `43325ff` Disc 1 capture | D | bounded SF2 validation tooling |
| `fd3126e` backdrop ownership | G2 mixed | renderer policy plus SF2 classifier |
| `f8d5270` Disc 1 hardening | D/T | SF2 route/validation only |
| `0752501` effect/backdrop classification | G2 mixed | generic effect helper plus title rules |
| `2a8a239` pass-2 identity | T | SF2 artifact/config gate |
| `a2b951c` projection at DMA submissions | G2 mixed | generic submission API plus SF2 owner |
| `cf8d65a` modernization checkpoint | T | SF2 acceptance record |
| `e9a0f69` corpus return | P | normalized knowledge receipt |
| `a0766d3` lab graduation | P | project status documentation |
| `9d1455f` tier candidate testing | P | validation-process documentation |
| `d064822` confidence workflow | P | validation-process documentation |
| `2eebc41` renderer-neutral PGXP | G2 | generic base; SF3 is second eligibility consumer |
| `17e9bba` overlay/capture/crash hardening | G2 mixed | reusable bundle requiring hunk separation |
| `11e949f` high-refresh R1-R3 rejection | R | negative evidence only |
| `b3b63a7` state/outbound backlog | P | documentation and contribution queue |
| `10a328f` R3 rejection/root cause | R | negative evidence only |
| `34dcc23` close high-refresh experiment | R mixed | retain rollback fixes only after separate audit |
| `b33eb14` public alpha preparation | P | release documentation |
| `0a9038d` alpha closure | P | project milestone documentation |
| `e37dbeb` alpha publication | P | publication receipt |
| `452cc0c` launcher enhancement Mods | GQ reference | accepted generic lifecycle; SF3 second consumer pending |
| `4d79e17` accepted launcher release | P | validation record |
| `9b0271d` v0.1.1 publication | P | publication receipt |
| `12c06bb` two-disc support | T | SF2 campaign evidence |
| `e7d83c2` final knowledge return | P | normalized corpus receipt |
| `91c94e6` setup bootstrap | P/G2 mixed | reusable installer plus SF2 recipe |
| `ded57a2` installer qualification | P | clean-room validation receipt |
| `c526a94` shared template rollout | P | template/corpus handoff |
| `1e6b27a` v0.1.2 qualification | P | publication receipt |

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

## Batch 1 framework branch checkpoint

An ignored in-repository worktree now checks out
`framework/convergence-batch1` from `framework/master` at `0cfa9fe`. Three
generic commits applied without conflicts:

| New framework commit | Source lineage | Content |
|---|---|---|
| `13aee712` | `4b5edc7` | bounded depth-24 upload telemetry |
| `e289210c` | `09be64b` | OpenGL 15/24-bit VRAM ownership handoff and regression |
| `49e428c6` | `485b79b` | active-read seek retarget and regression |

The branch contains no title docs, probes, addresses or payload. The stronger
SF2 generic commits were used directly because their diffs were already clean;
the independent SF3 mixed commits remain evidence, not import sources.

Validation:

- CLI targets built successfully.
- The complete 40-test framework suite passes with `PYTHONUTF8=1`.
- Both newly imported contracts pass.
- GCC 16.1.0 ICEs in unchanged `function_analysis.cpp` at `-O3`; rebuilding the
  same Release/`NDEBUG` suite at `-O2` succeeds. This is recorded as a toolchain
  qualification issue, not attributed to the imported changes.
- Omitting `PYTHONUTF8=1` reproduces three Windows code-page decoding failures;
  the required UTF-8 environment resolves them without source changes.

The branch is local only. It is not tagged, pushed or consumed by SF3 yet. The
next gate is exact diff/payload audit followed by an SF3 generation/build using
this framework branch and two ordinary compatibility runs.

## Batch 1 SF3 adoption and consumer gate

Commit `a1dac337` completed the 80/80 subject/path routing. The exact framework
batch diff then passed path/content scans: only runtime, recompiler registration
and the two title-neutral tests were present; no game address, title name,
private path, route marker or payload extension was found.

A merge simulation correctly reported conflicts only where SF3 already has the
same behavior in newer files/tests. Integration commit `fefa576d` therefore
records `framework/convergence-batch1` as a second parent with the `ours`
strategy. This is not a claim that untested framework content was preferred:
`git diff HEAD^1 HEAD -- runtime recompiler tools` is empty, so the accepted SF3
tree is byte-identical while canonical ancestry is explicit.

Post-adoption evidence:

- SF3 Release suite: 67/67 pass with `PYTHONUTF8=1`.
- Fresh ordinary diagnostics-off 4:3 executable SHA-256:
  `777D950589549516581770ECEAF40996E600EE6900676BDF80DFEB75E16CF5DD`.
- Two isolated OpenGL processes consumed all 3,000 unchanged input samples.
- Normalized logs match. Normalization replaces only the isolated output
  directory suffix and removes the optional asynchronous `[Keybinds] Loaded`
  notice; all semantic/runtime lines remain compared.
- Card 1 matches in both runs:
  `A717D08D25E78DB0ED71DCEB6CFC0A5A6249B71727820C0C69B5E89AE570CC3F`.
- Card 2 matches in both runs:
  `7706C7D43EDAF8CB7618E574F03457105153E3BDC196DB803A600AD96A8F58E8`.

Batch 1 is locally adopted and compatibility-qualified. It remains unpushed;
canonical framework publication needs its own final audit and user review.

## Batch 2 overlay/input checkpoint

Local branch `framework/convergence-batch2` extends Batch 1 with three
title-neutral commits:

| Framework commit | Source lineage | Content |
|---|---|---|
| `f8bd4ff8` | SF3 `70c167a` | compile latest plus immutable `.d` capture history by byte identity |
| `d62fe45c` | SF2 `17e9bba` | recoverably migrate a legacy `.d` file before publishing new evidence |
| `a1d2d77d` | SF3 `cbae3a9` | bounded deterministic input serialization/replay core and Release-active test |

SF3 title policy (`overlay_native = false`), route helpers, addresses and the
SF2 SIO-coupled timeline implementation did not cross into the framework.
Crash serializers and unpromoted-shard policy remain separately routed work;
they were not smuggled in with the mixed SF2/SF3 source commits.

Validation:

- Framework recompiler suite: 42/42 with `PYTHONUTF8=1`; dedicated runtime
  `input_timeline_test` passes as an actual Release CMake target.
- SF3 MinGW/Ninja Release suite: 68/68. A separately rebuilt MSVC tree passes
  66/68 but retains two diagnostic-string differences in pre-existing codegen
  tests; the same sources pass under the qualified MinGW/Ninja lane.
- Integration commit `b806480e` records the canonical branch as ancestry. The
  only new SF3 runtime behavior is the recoverable legacy-history migration;
  the input core and additive loader already existed in the SF3 tree.
- Ordinary diagnostics-off executable SHA-256:
  `95E7AD12E5DFA422B4A1B22DF96E5D51504A3B1BFCFCB985E706FA871DA74E37`.
- The accepted 3,000-sample payload was rebound from
  `psxrecomp-e9d9d51622b7b96d` to `psxrecomp-d18f3b1313f83741`; body SHA-256
  remained `dc57139288ebc5f17de801264619ff855aedb6973da5e54c4ad6cb1917662f5b`.
- Two isolated OpenGL processes reached the bounded 3,000 marker. Normalized
  stdout hash is `c53cb6472722ab22f45b757b6817e85fb096c3ddee8798a78e2fdd9d6ca8a7a1`;
  normalized stderr hash is
  `89bb21f6adf81a7cff80e718cee89dc0756ac70f8e868058a3a9e58330398499`.
- Both runs reproduce Batch 1 card hashes: card 1
  `A717D08D25E78DB0ED71DCEB6CFC0A5A6249B71727820C0C69B5E89AE570CC3F`,
  card 2
  `7706C7D43EDAF8CB7618E574F03457105153E3BDC196DB803A600AD96A8F58E8`.

Two early consumer attempts failed at the retail entry because the prior CMake
clean had removed ignored generated game C; CMake then relinked a BIOS-only
runtime. Regenerating from the owned local executable restored 269 retail
translation/dispatch units. Those failed outputs are retained and are not
counted as Batch 2 behavior.

The separate debug-tools/PGXP diagnostic executable was then reconfigured so
its configure-time compatibility hash included the adopted runtime source.
Executable SHA-256 is
`78239E2D85A34AF9B4189738FBC94BA9DB7C468F66701D4313DAD73EEA3CB8E5`;
its route ID is `psxrecomp-0a29eb4681c71b42`, again with the unchanged payload
hash above. Two isolated diagnostic OpenGL processes reached all 3,000 samples.
Their normalized stdout matches at
`09666334d3bd27c08a3a3f5af40829f2677a1e7f7e6df306ca6a8cf4fa30e33d`,
stderr matches the ordinary lane at
`89bb21f6adf81a7cff80e718cee89dc0756ac70f8e868058a3a9e58330398499`,
and both cards reproduce the ordinary/Baseline hashes. The ordinary and
diagnostic execution lanes are therefore qualified independently. Crash dump
serializer bounds and unpromoted-shard lifecycle remain separate Batch 2 work.
