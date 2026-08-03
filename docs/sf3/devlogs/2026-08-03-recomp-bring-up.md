# SF3 recompilation bring-up

## 2026-08-03 — isolated feasibility baseline

The lab was cloned with `--no-hardlinks` from clean tracked SF2 feasibility
commit `4f811c2` and switched to branch
`experiment/sf3-recomp-feasibility`. The local clone remote was removed;
upstream is fetch-only with push URL `DISABLED`. Initial tracked working-tree
footprint is 0.073 GiB versus 5.4 GiB in the source workspace including its
ignored build/capture state, proving those local artifacts did not transfer.

SF2-specific instructions, manifests and reports were removed. Generic
framework corrections and their source-owned regressions remain in history.
SCUS-94640 is the only game target on this branch.

### Initial corpus consultation

The private corpus, SF2 recomp report and SF3 hybrid report were consulted
before implementation.

| Lead | Initial disposition | First SF3 check |
| --- | --- | --- |
| `PSX-CPU-002` load delay | framework correction retained; SF3 applicability unproven | complete framework regression, then observe any SF3 first divergence |
| `PSX-CPU-003` encoded JALR | framework correction retained; SF3 consumer unproven | measure dirty-RAM JALR forms before attribution |
| `PSX-IRQ-001` nested-call IRQ | framework correction retained; SF3 consumer unproven | require an actual in-call event wait before calling it confirmed |
| `PSX-GPU-001` persistent pages | strong SF3 presentation lead | compare draw/display pages and complete same-tick submissions |
| `PSX-GPU-002` CPU/FBO coherence | not yet applicable | test only if an SF3 24-bit presentation symptom appears |
| `PSX-HLE-001` wrapper mirrors | hybrid-proven, but recomp path uses LLE OpenBIOS | verify whether authentic wrappers eliminate the HLE-specific failure |
| `PSX-MEM-001` alias safety | relevant lifecycle contract | inspect actual runtime stack/range allocation; do not import hybrid stack |
| `PSX-VAL-002` pre-fetch stop | diagnostic contract adopted | report stop reason/fetch status and read RAM before invalid-code diagnosis |

Independent validator named for generic CPU/IRQ results: Tenchu. Independent
validator for GPU page/composition results: SF2 hybrid.

### Framework baseline and retail identity

- Initialized `lib/recomp-net` at pinned commit
  `01b648e4acc26c8e229b5b0451618aeac24b7444`.
- Built the redistributable CLI in Release mode with GCC 16.1.0 and packaged
  `dist/psxrecomp-cli-windows-x86_64.zip`.
- The first direct `ctest` invocation inherited the host's Greek CP1253 Python
  locale. Three Python-driven tests failed while decoding child-process/source
  bytes, before their intended assertions could complete. Repeating the same
  suite with `PYTHONUTF8=1` passed all 40/40 tests in 2.86 seconds. This is
  classified as a narrowed host test-environment invariant, not a CPU/runtime
  regression; subsequent scripted test gates must pin UTF-8 mode.
- Read-only `sf_tool inspect` independently identified the user-owned disc as
  volume `SCUS94640`, executable `SCUS_946.40`, executable SHA-256
  `b4b32cc92e6b8634762893b637bc9a471442edbeb7569afcfb18eafbe82b9460`,
  entry `0x800FB368`, text address `0x80010000`, and text size `0x001CC000`.
- The disc image SHA-256 is
  `2c36429649e50036fd5c9187bdc3ff23e04039499e7cdf1aba5cfd5a3badcb38`;
  tracked OpenBIOS SHA-256 is
  `fabe498fbf224e4721f12f31b6f5fe0659205e341dc4e5c5f91b9bd1a1011c57`.

### Deterministic generation and clean Release builds

- Two independent CLI invocations generated 1,128 files each from the same
  gated retail disc and OpenBIOS inputs.
- Narrow root-path normalization found 1,128/1,128 files identical, no
  one-sided or differing paths, and tree SHA-256
  `09043b8c29b5c34a0364d0fd36778fa7002ef14d29128938a60b272bf915433e`.
- Generation discovered 3,450 static retail functions, 54,265 basic blocks,
  and 199 alias entries. These are generation facts, not proof that every
  emitted address is executable code; the generator also reported reserved
  opcode candidates in executable-range data and those warnings remain open
  until runtime reachability distinguishes relevant code from false seeds.
- Both clean generated trees built in Release mode. Each product is
  97,722,767 bytes. Raw binaries differ by exactly eight bytes: PE timestamp,
  PE checksum, and one embedded build timestamp. After normalizing only those
  fields, both products have SHA-256
  `a23b0071a7e8ae94746e1e0080a0e4cf4c43c62648724ddc8367842911ac683d`.
- Current repository footprint including both ignored generated trees and
  their clean builds is 1.662 GiB, below the 20 GiB cap.

### R1 — OpenBIOS, retail entry and stable TITLE

The untouched Release product first ran for a bounded 30 seconds with
`--headless --no-launcher`, a fresh memory-card directory and no SDL audio
initialization. It loaded the bundled OpenBIOS image, selected `LLE (recompiled
BIOS)`, mounted SCUS-94640, and began at `0xBFC00000`. The first launch attempt
was contradicted before guest execution because PowerShell split the cue path;
explicit argument quoting fixed the host launcher invariant.

A separate Release-optimized `build-r1` enabled the framework TCP diagnostics.
The first uncached run reached frame 714 with an identical retail chain:

| Target | Caller RA | SP | Frame |
| --- | --- | --- | ---: |
| `0x800FB368` executable entry | `0xBFC06694` | `0x801FFFF0` | 714 |
| `0x80029ED8` `Game_Main` | `0x800FB40C` | `0x807FFFF8` | 714 |
| `0x80029FB8` application loop | `0x80029FA0` | `0x807FFFE0` | 714 |

Live RAM `0x80121B84..0x80121B93` was
`02000000040000000000000000000000`: depth 2, current state 4, transition 0.
GPU state was 320x240x15 with alternating page-zero/page-240 draw/display
ownership and live GP0 draw, copy and environment traffic. CD remained active
with `int1_lost=0`. Headless mode intentionally had no host/SPU render pump,
while decoded CD/XA input was nonzero; this proves silent device activity, not
audible output.

### R1 — runtime-installed code ownership

The uncached TITLE run recorded 39 chronological installs, represented by five
coherent current capture regions. SF3 writes executable frontend code into
nominal main-EXE text pages below physical `0x1DC000`. Initial interpretation
that the overlay floor blocked these regions was contradicted by corpus/code
consultation: the framework deliberately divides kernel, overwritten boot-text
and above-floor overlay windows, and the runtime had checked below-floor bases
`0x141000`, `0x146000`, `0x150000` and `0x15E000`.

The first shard preflight correctly rejected an unstamped source include tree
(`00000000` versus recompiler emitter hash `9713afe3`). Pointing it at the exact
packaged runtime include tree used by the built game satisfied the staleness
guard. Throwaway preflight and real cache publication both built four
code-bearing regions, skipped one data-only region, and reported zero failures.

Two subsequent clean headless/silent processes each loaded four regions and
registered 122 candidates. Both reported zero static dispatch misses, overlay
invalidations, revalidation CRC misses, stale blocks, candidate overflow and
range-index overflow. At the sampled TITLE checkpoints:

| Run | Frame | Native overlay | Interpreter fallback | Static hits |
| --- | ---: | ---: | ---: | ---: |
| A | 3006 | 16,313,494 | 14,741 | 9,285,427 |
| B | 2463 | 13,225,927 | 11,183 | 9,131,008 |

Counts differ with observation time; ownership ratios are honest cumulative
counters. Semantic determinism is stronger: both runs produced exactly the
same fingerprints at frames 714 and 1000:

| Frame | write hash | PC hash | MMIO hash | SPU hash/count | cycles |
| ---: | --- | --- | --- | --- | ---: |
| 714 | `ca4cf1d7f0e72c45` | `ec595161d237329d` | `35c81a96dd3a652a` | `14650fb0739d0383` / 0 | 403038720 |
| 1000 | `ab542f8206d1859e` | `b36c2304ed0c7251` | `2fc2b4305ce0eff4` | `d5e100f87114fb31` / 218 | 564480000 |

The corpus disposition is therefore: below-floor capture lifecycle confirmed;
text-end-as-immutable-code contradicted; `PSX-HLE-001` irrelevant under LLE;
`PSX-GPU-001` narrowed/active; `PSX-GPU-002` irrelevant without a 24-bit
symptom; CPU load-delay/JALR causal relevance not yet established; nested IRQ
path exercised but causality not yet isolated. Tenchu is the independent
validator for the generic overwritten-text lifecycle; SF2 hybrid remains the
GPU page/composition validator.

### R2 — retail Story, state 8 and state-0 player control

The first live TITLE gate appeared contradictory: state/depth was stable
`4/2`, mode/substate RAM was `0/0`, retail PAD polling was live, but the hybrid
oracle's transient mode-0 widget word was zero rather than four. A bounded
screenshot resolved ownership without guessing: the runtime was rendering the
authentic user-operable `New Game` menu. The widget word is therefore useful
while constructing the menu, not a durable readiness invariant.

Only active-low physical SIO words were then supplied: Cross `0xBFFF`, neutral
release, and later Up `0xFFEF`. No application-state write, processed-PAD
record, callback handoff or native substitute was used. Retail rendered the
New Game/Two Player/Mini Game choice, selected New Game, displayed the Tokyo
briefing, entered state/depth `8/2`, and popped to `0/1`. The exact observed
state-8 PAD return, pop return and Mission 1 PAD return register/SP shapes were
identical in two clean packaged runs:

| Gate | Stable call evidence |
| --- | --- |
| state-8 PAD | `a0=0x807FFF84`, `a1=0`, `a2=0x10`, `a3=2`, `s3=0x8012D79C`, `sp=0x807FFF70` |
| state-8 pop | `a0=0`, `a1=2`, `a2=0x177C8`, `a3=0x780000`, `s3=0x8012D79C`, `sp=0x807FFF70` |
| Mission 1 PAD | `a0=0x1F8003A4`, `a1=0`, `a2=0x80122258`, `a3=0x807FFF28`, `s3=0x8012D79C`, `sp=0x1F800384` |

The rendered state-0 frame contains the player, HUD and Tokyo world geometry.
A bounded Up press visibly moves the player while the application remains
`0/1` and the Mission 1 PAD return continues polling. The runtime's low-level
CD path owns disc transfer and retail owns archive parsing and installed code;
no hybrid host archive/member bridge is present. Read-only `sf_tool`
independently identifies the loaded resource as the 40-room Tokyo archive with
270 objects and player index 199.

Two clean executions of tracked `lab/sf3/probe_story.py` passed. Because TCP
commands are delivered at the next host-serviced boundary, their gates landed
at frames `1517/1522` (TITLE), `3217/3223` (state 8), `3231/3239` (pop), and
`3240/3250` (first post-pop Mission 1 PAD sample). Absolute frame equality is
not claimed. The call shapes, state path, overlay identities and device
invariants match exactly.

At the final bounded samples, the dispatch census was:

| Run | Static | Native overlay | Fallback | Ownership percentages |
| --- | ---: | ---: | ---: | --- |
| D | 9,486,303 | 14,998,871 | 28,075 | `38.699 / 61.187 / 0.115` |
| E | 9,489,763 | 15,090,082 | 28,162 | `38.564 / 61.322 / 0.114` |

Both runs had 123 registered candidates, four loaded native regions, zero
static misses, invalidations and CRC misses. GPU world-3D/draw counters, SPU
key-on counts, decoded XA input and CD state were live. Host audio output was
inactive with zero SPU/host render frames, preserving the silent-run promise.

The packaged probe exposed one host-side nuance. On a fresh headless pad, the
first injected D-pad edge can be consumed while the generic runtime requests a
coherent analog-to-digital type transition. Retail state remains unchanged;
after a neutral interval the next physical edge is accepted. The probe retries
only while the retail gate is unchanged, stops immediately on transition,
permits at most three attempts and records the actual count. Both clean runs
used two edges at initial TITLE and one thereafter. This is narrowed input
boundary behavior, not an SF3 application or CPU defect.

Current footprint including ignored generations, builds, captures and all
probe evidence is 2.187 GiB, below the 20 GiB ceiling.

### R3 — retail FMV coherency and New Game intro

The first user playtest exposed two superficially similar symptoms: colorful
stale bands around a correctly decoded Mission 1 movie, and an apparently
missing intro. The mandatory corpus pass matched the presentation symptom to
`FAIL-009` / `PSX-GPU-002`: a hardware-renderer FBO and the CPU VRAM mirror can
disagree when packed 24-bit movie uploads take ownership. The SF2 recomp lab's
`09be64b` correction was treated only as a candidate. Its generic invariant
was checked against SCUS-94640 with a fresh OpenGL diagnostic build.

The OpenGL backend now receives GP1(08h) depth transitions. On 15-to-24-bit
entry it first flushes/readbacks authoritative 15-bit FBO state, then permits
packed RGB uploads to own the CPU mirror. GP0 fills issued in 24-bit mode update
both representations, and upload policy runs before the first CPU write. No
SCUS address, movie geometry, generated retail code or native movie presenter
is involved. A title-neutral structural/model regression covers ordering,
fills and upload ownership; the complete Release suite is 41/41 passing.

The intro hypothesis required separate falsification. A persistent neutral
PAD (`0xFFFF`) and disabled auto-skip showed the natural retail sequence:

| Gate | Observed evidence |
| --- | --- |
| SCEA stream | decode 1 at frame 919/920; decode 45 at frame 1096 |
| post-logo transition | title substate 3; XA inactive around frame 1414/1415 |
| TITLE stream/menu | decode resumes at frame 1501/1506; title substate 0 |
| New Game intro | retail-selected transition captures the Tokyo car arrival |
| briefing/state 8 | decode total 414/415; state-8 PAD gate at frame 3499 |
| state-0 control | state-8 pop at frame 3509/3511; zero dispatch misses |

Thus SCUS-94640 does not request ZINTRO before its main menu. The Tokyo intro
is retail-owned by the New Game transition. The earlier automation was able to
misreport a skip because it considered state 4 sufficient while SCEA was still
playing, then left an eight-frame Cross injection armed after retail accepted
the menu edge. The remaining input could legitimately cross the next state
boundary. The corrected probe waits until the TITLE stream itself is decoding
and immediately replaces an accepted press with neutral input. This changes no
guest state and fabricates no callback.

Two fresh hidden-window/dummy-audio runs followed the complete retail path.
Both captured clean SCEA, TITLE and Tokyo intro frames with black letterbox
regions and no stale colored bands. They reached the same state-8 call shape,
state-0 Mission 1 control, and `miss_total=0`. Their semantic checkpoints were:

| Run | TITLE frame/decode | accepted decode | state-8 frame/decode | pop frame |
| --- | --- | ---: | --- | ---: |
| C | `1556 / 60` | 217 | `3499 / 415` | 3511 |
| D | `1556 / 60` | 216 | `3499 / 414` | 3509 |

The one-frame/decode arrival variation is host TCP sampling, not divergent
retail behavior. SDL used a hidden OpenGL window and the dummy audio driver, so
the hardware presentation path was exercised without a visible window or
sound device.

Two new clean projects generated from the gated disc are identical across
1,128/1,128 files with tree SHA-256
`096032a2bd37ca13bc163b94693d21281eb17d60829eb68e6a753559f18b3918`.
Both 97,723,953-byte Release products built successfully. They differ only in
the same eight PE/build timestamp bytes and normalize to SHA-256
`3a43b1461cc82f07d86179ec56d8e2509df6d4235c108416299f2ea79e016dfe`.
The repository plus ignored generations/builds/traces occupies 4.182 GiB.

Corpus disposition: `FAIL-009` / `PSX-GPU-002` is confirmed for the SF3 user
symptom and fixed at the generic ownership invariant; early-input startup skip
is narrowed to probe press lifetime rather than a retail playlist or MDEC
failure; neutral input, MDEC underflow and auto-skip causes are contradicted.
SF2 recomp is the independent validator for the GPU handoff. SF2 hybrid can
independently validate the corrected release-on-transition probe contract.
