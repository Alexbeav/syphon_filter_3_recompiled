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

### R3 — retail FMV coherency and complete intro sequence

The first user playtest exposed two superficially similar symptoms: colorful
stale bands around a correctly decoded movie, and the missing pre-menu intro.
The mandatory corpus pass matched the presentation symptom to `FAIL-009` /
`PSX-GPU-002`: a hardware-renderer FBO and the CPU VRAM mirror can disagree
when packed 24-bit movie uploads take ownership. The SF2 recomp lab's
`09be64b` correction was treated only as a candidate and checked against
SCUS-94640 with a fresh OpenGL diagnostic build.

The OpenGL backend now receives GP1(08h) depth transitions. On 15-to-24-bit
entry it first flushes/readbacks authoritative 15-bit FBO state, then permits
packed RGB uploads to own the CPU mirror. GP0 fills issued in 24-bit mode update
both representations, and upload policy runs before the first CPU write. No
SCUS address, movie geometry, generated retail code or native movie presenter
is involved. A title-neutral regression covers ordering, fills and ownership.

The missing intro required separate falsification. After SCEA, a completed seek
targeted `[51,54,39]`, but the drive still reported an active read at
`[50,31,14]` with READ status set. The preceding ReadN/ReadS stream had survived
SeekL, so later SetLoc data could not become authoritative. This matched the
generic invariant independently isolated by SF2 recomp commit `485b79b`, but
was adopted only after this bounded SCUS-94640 check.

SeekL and SeekP now stop the active read generation (including pending INT1),
clear READ/PLAY status, and only then enter SEEK at the requested location. No
disc address, game state, generated retail code or movie callback is patched.
A title-neutral regression covers the CD retargeting contract. Together with
the GPU regression, the complete Release suite is 42/42 passing.

The fixed natural retail sequence is:

| Gate | Observed evidence |
| --- | --- |
| SCEA stream | decode begins around frame 920 and reaches 45 around frame 1096 |
| cemetery intro | full 512x240 pre-menu movie plays while title substate remains 3 |
| TITLE stream/menu | retail menu gate at frame 7582, decode total 1653 |
| New Game intro | retail-selected transition plays the Tokyo car arrival |
| briefing/state 8 | frame 9523/9531, decode total 2007/2008 |
| state-0 control | state-8 pop at frame 9535/9545; zero dispatch misses |

SCUS-94640 therefore owns two distinct sequences: the cemetery intro before
the menu and the Tokyo movie after New Game. The CD seek bug owned the missing
pre-menu intro. Separately, the earlier automation considered state 4
sufficient while SCEA was still playing and could leave a multi-frame Cross
pulse armed after a retail transition. The corrected probe waits for the
actual TITLE stream/menu after the cemetery movie and immediately replaces an
accepted press with neutral input. It changes no guest state and fabricates no
callback.

Two fresh uncached hidden-window/dummy-audio runs followed the complete retail
path and captured clean SCEA, cemetery, TITLE and Tokyo frames. Two further
clean runs used the previously compiled retail-derived overlay cache:

| Run | TITLE frame/decode | state-8 frame/decode | pop frame | Static / native / fallback |
| --- | --- | --- | ---: | --- |
| A | `7582 / 1653` | `9531 / 2008` | 9545 | `11,406,832 / 53,312,659 / 55,544` |
| B | `7582 / 1653` | `9523 / 2007` | 9535 | `11,404,559 / 53,288,291 / 55,470` |

Cached ownership was respectively `17.610% / 82.304% / 0.086%` and
`17.614% / 82.301% / 0.086%`. Each run registered 123 candidates across four
native regions with zero static misses, invalidations or CRC misses. SDL used
a hidden OpenGL window and dummy audio, exercising hardware presentation
without a visible window or sound device.

Two new clean projects generated from the gated disc are identical across
1,128/1,128 files with tree SHA-256
`b2994894e7b921b6e56adffa7c824ba65815c8dff9ea1974cb2c79f3e3757475`.
Both 97,723,953-byte Release products built successfully. They differ only in
two PE timestamp/checksum bytes and normalize to SHA-256
`6d1cbdd2c1aa5e325ed0e86f3b405b6cd6ee6b15135ef355cc34b7e2c5852032`.
The repository plus ignored generations, builds, caches and traces occupies
6.153 GiB, below the 20 GiB ceiling.

Corpus disposition: `FAIL-009` / `PSX-GPU-002` is confirmed for the colorful
bands and fixed at the generic ownership invariant. The missing-intro symptom
confirms the CD seek-retarget contract in SF3 after SF2's first proof. Probe
press lifetime remains a narrowed secondary input hazard; MDEC underflow and
neutral/auto-skip hypotheses are contradicted. SF2 recomp and SF3 now
independently validate the GPU and CD invariants. SF2 hybrid can independently
validate the release-on-transition probe contract.

### R4 — standalone checkpoint and source publication

The completed generic CD correction, regression and corrected evidence package
were checkpointed as `db98b05`. Private-corpus commit `87e6c7a` adds candidate
`PSX-CD-001`, records SF2 recomp `485b79b` as the first proof and SF3 as the
independent validator, and corrects the earlier provisional intro attribution.
Pre-existing unrelated Tenchu/shared-runtime work in the corpus checkout was
not staged or altered by that commit.

The ordinary lab history inherited local development cards, so publishing that
history would not satisfy the proprietary-data boundary. A fresh parentless
tree was instead built from the final tracked source and explicitly excluded
all root/test cards, `.mcp.json`, retail inputs, generated SF3 code, caches,
traces, captures and media. The snapshot contains 1,478 source/documentation
paths and no prohibited retail artifact. It was published to the public
`Alexbeav/syphon_filter_3_recompiled` repository without adding a writable
remote to this lab; the existing upstream remains fetch-only with push disabled.

The local desktop shortcut targets the fixed normal Release build and isolated
play memory-card directory. `SF3_Redux` enhancement work remains deliberately
outside this standalone checkpoint pending the user's visible FMV/intro and
campaign-flow test.

### R5 — human validation contradicts representative readiness

The first post-publication human test invalidated the assumption that initial
state-0 movement was an adequate product gate. On one ordinary cold launch,
the retail briefing was accepted but Mission 1 did not begin. On the next,
Mission 1 ran with large surfaces sampling red/checkered corrupt texture data;
geometry, the player, another actor and the HUD remained visible. The private
retail-derived screenshot remains outside version control.

These are two separate normalized symptoms until a shared first divergence is
proved. The transition failure is initially classified as lifecycle/device or
control ownership. The presentation failure is initially classified as
GPU/VRAM texture-source ownership (TPAGE/CLUT, upload/copy coherency or cache
invalidation), not as an MDEC continuation of the earlier movie symptom.

Corpus consultation found no existing failure with the same proven owner. It
did identify the applicable contracts: `PSX-VAL-001` forbids equating state-0,
input or a visible frame with playability; `PSX-GPU-001` requires persistent
authored pages; `PSX-GPU-002` requires explicit split-representation coherency;
and the SF3 hybrid report already leaves full same-tick composition and
guest-authoritative texture residency open. Each is a falsifiable lead, not a
fix to import. The next checks are an ordinary-Release state-8 lifecycle trace
and same-route software/OpenGL capture at the first corrupt frame.

The project remains `bootstrap_verified`. Representative-slice claims are
withdrawn pending sustained correct presentation, input/audio/pause,
death/restart, checkpoint restore, Mission 1 completion and its following
retail transition in two clean deterministic routes plus a human completion.

### R6 — bounded observer repro and retail-boundary input witness

The user subsequently reported that another ordinary launch looked and played
correctly. This narrows both P0 symptoms to intermittent behavior; it does not
contradict the failed briefing handoff or corrupt-texture observations and does
not promote the project beyond `bootstrap_verified`.

The first bounded renderer checks reached clean Mission 1 state-0 output in one
OpenGL run and one software run. A second OpenGL run omitted all intermediate
screenshots and captured the display ring instead. It was also clean. This
contradicts only the hypothesis that `screenshot_file`'s OpenGL-to-CPU VRAM
writeback was required to heal the route. It does not establish that the ring
is non-perturbing: OpenGL display capture still flushes and reads back the FBO,
and the original ring also read the entire 1024×512 VRAM every frame. The ring
does avoid changing CPU VRAM, which makes it a safer ownership witness than
`screenshot_file`, but its possible host-timing effect remains explicit. No
same-frame corrupt software/OpenGL pair has yet been captured.

The ring's full-VRAM auxiliary capture is now separately opt-in through
`PSX_DISPLAY_RING_AUX=1`; the default retains only the visible display and
reduces allocation from roughly 84 MiB to 20 MiB. A source-owned guard prevents
accidental restoration of unconditional full-VRAM capture. Generic BGR555
color statistics also let the SF3 probe alarm on the exact observed failure:
the supplied corrupt screenshot is 55.82% red-dominant and 34.08% hot-red,
where clean OpenGL/software samples are about 0.15%/0.01%. The default
15%/5% limits are deliberately described as a symptom-specific oracle, not a
general visual-correctness test. These changes pass the 45-test framework suite
without launching the game, as requested; runtime handler behavior remains
unclaimed until a later permitted diagnostic run.

To turn the user's connected Mission 1 playthrough into a repeatable witness,
the runtime now records and replays normalized two-port pad packets at the
existing retail SIO sample boundary. The `PSXPAD2` format contains input only,
uses contiguous guest-sample indices, preserves connection/type/analog state,
holds neutral after replay completion, rejects malformed or incompatible
routes, and disables the optional second low-latency host resample. Its
compatibility token hashes the complete runtime and generated retail source
content plus Release/Debug flavor. Periodic `.partial` publication limits loss
without introducing another guest sample. A source-owned parser/replay test and
PowerShell launcher syntax test pass.

A fresh SCUS-94640 project generated with the integration retained executable
entry `0x800FB368`, load address `0x80010000` and text size `0x1CC000`. An
initial two-tree comparison was reproducible but exposed a stale CLI packaging
snapshot that predated one required declaration; this was rejected before it
became a release artifact. After rebuilding the CLI package, two new clean
trees match across 1,130/1,130 files with tree SHA-256
`b7ba1712d1c69be424842bc49a220b8d7bb9c2c8fea59546f8132495fe88625b`,
and packaged `runtime/src/main.cpp` is byte-identical to the owning source.
One untouched generated tree builds an ordinary 97,744,583-byte Release
product (SHA-256
`7f18886f6118a6e32edb705806519ae5198fd6951c83ecb8588607e39b988631`).
The framework suite passes 42/42 with `PYTHONUTF8=1`. Per the user's request,
the game was not launched after that build, so runtime record/replay
equivalence remains an explicit open gate. The recorder is diagnostic
infrastructure, not a fix for either P0 and not evidence of campaign
completion. The repository plus ignored generations and builds occupies
9.040 GiB, within the 20 GiB ceiling.

Read-only sibling review separates the enhancement deltas. The recomp runtime
already owns generic internal supersampling and keyboard-to-pad mapping. Its
generic widescreen path can be used only after SCUS-94640-specific projection,
sprite/HUD and culling checks; no SF2 address is transferable. Native relative
mouse freelook in `sf-pc-port` is installed at identified SF1/SF2 retail camera
consumers and gates scripted-camera ownership, so SF3 requires its own bounded
consumer/ownership discovery. PsyCross PGXP is coupled to the hybrid scene
adapter and ordering-table renderer and is not a drop-in recomp-runtime patch.
High-resolution, native mouse/freelook, widescreen and PGXP therefore remain
Redux work after the representative compatibility gate.

Source checkpoint `cbae3a9` contains the recorder and earlier probe form;
the subsequent bounded-observer checkpoint corrects its transparency claim and
adds the opt-in auxiliary capture and color-signature regression.
Private-corpus checkpoint `76393af` records the earlier bounded status and
names Tenchu as the independent generic-format validator; it explicitly leaves
SF3 runtime capture/replay unverified. Neither checkpoint contains a retail
input, generated image, route, overlay cache or save.

After the observer correction, two further clean SCUS-94640 generations match
across 1,132/1,132 files with tree SHA-256
`0c4de43aa0af9f1dbc1df4379d91876582e0f760c4bb458dc0d250adea6df05e`.
The packaged runtime copies of `debug_server.c` and `frame_color_stats.c` are
byte-identical to their owning sources. The untouched ordinary Release links
to a 97,748,156-byte product (SHA-256
`690b8f91a96ba7dc2faf8323af4b8b99fcb77cdb79cc9c59fc0aa875e65c2211`),
and the Release-optimized diagnostic configuration that contains the new TCP
handlers links to a 100,921,552-byte product (SHA-256
`2109e69864fa909b71e1057e9c87b7cfa41dbb89ad06957beb3374762de212fa`).
The framework suite is 45/45 passing. Per the user's explicit instruction,
neither executable was launched; the process census remained zero and runtime
observer behavior is not claimed. The complete local footprint is 10.569 GiB,
below the 20 GiB limit.

The no-launch interval also closed the human-route replay packaging gap.
`PSX_INPUT_STOP_AFTER` previously accepted only renderer-less `--headless`, so
an unattended replay could not both exercise the authentic OpenGL presentation
path and stop at the recorded retail-SIO sample boundary. The generic runtime
now accepts the limit in `--hidden-window` mode while continuing to reject it
for an ordinary visible process. A source-owned helper validates a `PSXPAD2`
header, isolates memory cards and logs, enables dummy audio, consumes the route
through the selected hidden renderer and requires the exact bounded-completion
marker. It neither injects TCP input nor writes guest state. The recording
helper now makes the OpenGL/software renderer choice explicit.

The helper/source guards and PowerShell AST checks bring the framework suite to
46/46. Two clean post-change generations match across 1,132/1,132 files with
tree SHA-256
`aecb26b66492b0ca0074c9d58895483ca7686227313188f321ad9c96ce7febe5`.
The untouched ordinary Release links to a 97,748,156-byte product (SHA-256
`49b6e61e3a58730d7774fb7ac6e5e105b36b1ba35ca8c04d9fd19f9da751153b`).
Per the user's continuing instruction, the helper and product were not run;
the process census remained zero. The 11.723 GiB footprint remains below the
20 GiB limit. Runtime replay equivalence, presentation and semantic route
evidence therefore remain unclaimed.

A separate desktop shortcut, `Syphon Filter 3 Recomp - Record Mission 1`, was
initially created for the source-owned recorder and replay-compatible `input-route-i`
ordinary Release. It fixes the output to the ignored
`lab/sf3/traces/human-mission1.psxpad` path and selects OpenGL. The older normal
play shortcut was preserved. Creating and inspecting the new shortcut did not
launch the executable.

The diagnostic route observer now records every retail application-pair
transition, periodic GPU/SPU/audio/CD/PAD/dispatch state and the display origin
with each state-0 BGR555 sample. A matching red/checkered frame is dumped while
it remains in the 64-frame ring; optional full VRAM remains explicitly
expensive. The observer consumes only `PSX_INPUT_REPLAY`: source guards reject
TCP `set_input`, `press` and `write_ram` use. It is a perturbing localization
run, not acceptance evidence.

Two observer-ready generations match across 1,132/1,132 files with tree
SHA-256
`dea76d13f43caa9a327e48427c4b3fc2510091bfb8c2b60ef486acf77d30dffe`.
Both products were built from the same tree so their timeline compatibility ID
matches: ordinary Release is 97,748,156 bytes (SHA-256
`322adfabf59cf4e9e3bb8d6b6a2f77ba25c925e5dd4830f5722319f3174f7629`)
and diagnostic Release is 100,921,552 bytes (SHA-256
`97b310b6ad5400514bac0850f2fda662ee7b10174093ecdd147ca2013598ef32`).
The recording shortcut was retargeted from `input-route-i` to this matching
`input-route-k` ordinary product. No executable was launched, the process
census remained zero, and runtime observer behavior remains unclaimed. The
workspace occupies 13.255 GiB, still below the 20 GiB ceiling.

The first observer draft sampled every 60 frames. Because SF3 alternates its
display pages every frame, that even cadence could repeatedly land on one page
and falsely satisfy a long-duration presentation check. The observer now reads
adjacent retained frames at each state-0 checkpoint. A source-owned two-run
classifier requires matching application-transition sequences, a subsequent
retail transition, two display origins per run, live subsystem snapshots,
complete bounded input consumption and no known-corruption match. Its output
explicitly excludes arbitrary texture correctness, audio quality,
pause/death/checkpoint behavior and mission completion. Regression coverage
brings the suite to 47/47.

The human capture shortcut now passes `-Unique`, producing timestamped routes
without overwriting a prior success, P0 failure or partial recovery. A tracked
Mission 1 checklist names every representative-slice human gate through the
following retail transition. `-NoExit` keeps the capture receipt visible after
the game closes. The shortcut was edited but not opened; the game process
census remained zero.

The ordinary desktop shortcut `Syphon Filter 3 Recomp Lab` was then retargeted
from the stale `fmv-c` product to the same `input-route-k` ordinary Release used
by the capture/replay contract. It retains the isolated play memory-card path,
and the SCUS-94640 game configuration selects OpenGL. The shortcut was inspected
after editing but not opened.

### R7 — captured audio-only Mission 1 stall

The next ordinary human recording reproduced the Mission 1 blocker more
precisely: the intro cutscene's XA audio played, but no video was displayed,
retail input produced no visible response, and the mission did not progress.
The finalized ignored route is
`lab/sf3/traces/human-mission1-20260803-120259.psxpad`. Its `PSXPAD2` header
declares 3,194 contiguous samples and compatibility identity
`psxrecomp-f966f1dd14bf443e`; both endpoints are neutral. There are 333 active
samples in 59 runs from sample 205 through 3045, including 28 Cross runs (184
samples) and six Start runs (52 samples). The artifact therefore confirms that
host controls reached the normalized retail SIO boundary throughout the stall.
It does not establish that the guest reached a state which consumed them.

Mandatory corpus consultation classified `PSX-MDEC-005` and the device/lifecycle
handoff contract as live leads: XA playback alone does not prove MDEC decode,
display ownership or movie completion. `PSX-CPU-002` was checked directly
against the SF2 portability report. This tree already contains the generic CFG
ordinary-load delay correction at `663ac4a`, its focused generated-code
regression, and post-correction generated products, so a missing import of that
known fix is contradicted. Its incomplete edge coverage remains a framework
risk until the first divergent instruction is identified. `FAIL-018` (one lost
analog-to-digital input edge) is contradicted as the sole owner by repeated
button runs spanning almost the entire failed route. A purely visual OpenGL
coherency failure is also insufficient because retail progression and input
consumption stopped with the missing picture.

The bounded falsification order is now: (1) replay this exact route and compare
retail application state with XA and MDEC decode counters; (2) if decode stalls,
compare CD delivery/IRQ and MDEC DMA progress; (3) if decode completes without
the retail transition, inspect execution-tier/lifecycle ownership at the first
dirty-overlay handoff. The observer remains a localization instrument, not an
ordinary-Release oracle. No replay was launched because the user's prior
no-run instruction remains in force pending explicit permission.

### R8 — ordinary visible-path presentation recovery candidate

After explicit permission, the failed 3,194-sample route was replayed in two
clean diagnostic OpenGL processes and one software process against the original
`input-route-k` product. Every run reached retail state 8 near frame 2317 and
state-0 gameplay near frame 2387, completed 215 MDEC frames, advanced CD
data-ready/delivered-IRQ counts, reported zero dispatch misses, covered both
display origins and avoided the known red/checkered signature. A fourth OpenGL
run used copies of the failed session's memory cards and also succeeded without
changing either card. This contradicts a deterministic guest MDEC, CD/IRQ,
overlay, input-route, renderer-content or memory-card owner.

The ordinary replay helper initially returned while its GUI-subsystem process
was still running. Windows PowerShell's call operator had not provided a valid
wait boundary, so the empty logs were rejected rather than misclassified as a
runtime freeze. The helper now uses a hidden `Start-Process -Wait -PassThru`
process object and checks that object's exit code before reading the bounded
completion marker. Its source guard covers the wait contract. With the corrected
helper, the original ordinary Release completed the same route normally.

The remaining environment delta was visible direct-OpenGL presentation. The
runtime already documented a Windows/NVIDIA swap-queue failure in which
`wglSwapBuffers` blocks for roughly 1.5 seconds, audio continues on its callback
thread, and emulation/input appears frozen. Its generic self-heal existed only
around the SDL renderer's `SDL_RenderPresent`; SF3's configured OpenGL backend
calls `SDL_GL_SwapWindow` directly and bypassed it. This matches all observed
parts of the human symptom, but remains a strong owner inference until a visible
run either records the slow-swap counter or passes the previously failing gate.

All guest-vblank direct-OpenGL paths now time the swap, preserve latency-ring
markers and disable driver vsync for the remainder of the session after three
swaps exceed 250 ms. The existing wall-clock pacer continues to own 59.94 Hz,
so the recovery changes host presentation backpressure rather than guest time.
The interval setter cannot accidentally re-enable vsync after recovery. The
interpolation worker retains its intentional raw interval-zero swap. A focused
source regression covers all four guest-vblank paths, raising the framework
suite to 48/48.

Two fresh generations match across 1,132/1,132 files with tree SHA-256
`ebb7812bed9a129f1e0a2df21c6cdfcdcf3f6fc28d1b636c3f1ec660ee68983b`.
Their 97,748,212-byte ordinary Release products normalize to SHA-256
`d503db02073df5f35979b936f2a20604a6f1233499fb4fe64e3daec042187ea5`.
The selected tree's raw ordinary SHA-256 is
`d82a4c530267f7e6692ed359345f510f83e8436be568bff1e5f11b7e58726fff`;
its 100,921,608-byte diagnostic SHA-256 is
`8312169b201214e12f0444592ed791def5e173496c55c624197597633aabefe6`.

Because the timeline compatibility contract currently hashes all runtime
sources, this presentation-only change intentionally rejected the old route.
Comparison found all 1,130 guest/generated/input-boundary files identical; only
the GL presenter and source-only CMake/ignore files differ. An ignored receipt
therefore records a one-run header migration while proving the 3,194 sample rows
byte-identical. The new ordinary product completed that route twice. A matching
diagnostic run reached state 8 at frame 2317 and state 0 at 2386, decoded 215
movie frames, advanced CD delivery, reported zero dispatch misses, sampled
display origins `0,0`, `0,2` and `0,240`, and found no corruption match.

Both desktop shortcuts now target `input-route-m`; neither was opened. The
workspace is 15.160 GiB, below the 20 GiB ceiling. The candidate is ready for a
visible human falsification, but the P0 remains open until that check passes and
the longer representative Mission 1 gates are completed.

### R9 — visible corruption/fatal contradicts swap ownership; cache closure repaired

The human falsification failed decisively. Mission 1 presented a large blue
plane, malformed characters and texture/page corruption, then exited shortly
after gameplay began. The retained fatal dump reached frame 2751 with
`present_slow_count=0` and `present_vsync_disabled=0`; the direct-OpenGL
backpressure candidate is therefore irrelevant to this failure. The dump
records roughly 3.55 million dirty blocks and 134.10 million interpreted
instructions. Its final `instruction guard` record points at a valid `sltu` and
is a normal interpreter-slice yield, not an unsupported MIPS opcode.

The ordinary `input-route-m` product had been handed to the user without the
validated SF3 overlay cache. This was a release-closure error. The compiler
also contradicted its own additive-history documentation: manual compilation
read only the replace-on-latest `overlay_captures.json` and ignored immutable
`overlay_captures.json.d` contributions. A focused generic loader now unions
the latest file and every valid history snapshot by normalized address plus
exact bytes, unions evidence for the same variant, preserves different variants
at reused addresses and skips torn/malformed siblings. The 49-test framework
suite includes this contract. SF2 recomp is the independent validator.

Compiling the fatal route's large mixed code/data region directly correctly
rejected unsafe whole-region output and numerous data-as-code fragments. Those
partial products were not promoted. Instead, the four full SF3 shards from the
earlier two 82.3%-native clean runs were copied into `input-route-m` only after
their cache namespace matched exactly: SCUS-94640, gcc/win-x64, codegen 9,
emitter `9713afe3`, config `cd77ebe4`, ABI 21. This is same-title retail-derived
coverage under ignored storage, not an SF2 address or artifact.

The corrected diagnostic replay completes all 3,194 samples, reaches state 8
at frame 2317 and state 0 at 2386, samples display origins `(0,0)`, `(0,2)` and
`(0,240)`, and finds no red/checkered match. It reports four loaded regions,
122 registered candidates, 8,826,567 native overlay dispatches and 16,798
overlay fallbacks near frame 3004, with zero candidate overflow or ordinary
dispatch misses. Dirty execution remains material at 67.73 million
instructions, so cache restoration is an execution-tier correction rather than
proof of the crash's root invariant.

Two further non-diagnostic ordinary OpenGL replays completed the exact route
through sample 3194 with orderly `atexit` reports. The recorder itself also had
the Windows GUI-process wait defect already fixed in the replay helper; it now
uses `Start-Process -Wait -PassThru`, so a crash or normal close cannot return
before final route publication. The workspace is 15.668 GiB. The desktop
candidate is cache-complete and ready for one visible human countercheck, but
representative readiness and the corrupt-texture owner remain open.

### R10 — representative Mission 1 slice accepted through Mission 2 gameplay

The cache-complete visible countercheck passed. The user reported only brief
graphical defects at the start of Mission 1; the rest of the run matched the
original game to observation. The finalized 42,480-sample `PSXPAD2` route covers
death, checkpoint reload, full Mission 1 completion, following FMV, new-card
creation/save, Mission 2 FMV, briefing, cutscene and live state-0 gameplay before
a normal window close. Its SHA-256 is
`4b534e2b0e1b7e675fb55f8967f539333ba3b5b37902eb0caa503faa419d1277`.

Two clean ordinary hidden OpenGL processes consumed the exact route to the
bounded sample marker in 717.4 seconds each. Standard error is byte-identical;
standard output differs only by the intentionally isolated writable-state path.
Both runs created byte-identical 128-KiB slot-1 images with SHA-256
`ab79103084f591b122eff13803b64dec166102454ac10144b5a55399e1e2cf1f`;
the untouched slot-2 images also match. Terminal reports are orderly `atexit`
at frame 42,480 with 8–9 KiB maximum guest stack use and only the normal
interpreter instruction-guard yield.

One passive diagnostic OpenGL replay completed with zero exit at observed frame
42,476. It records 14 authentic application transitions, 1,011 state-0 samples
across display origins `(0,0)`, `(0,2)` and `(0,240)`, live GPU/SPU/CD/PAD
traffic, exact bounded completion and no match for the known red/checkered
signature. Near frame 42,074 it reports four loaded cache regions, 115 current
candidates, 9,715,051 native overlay dispatches, 292,119 interpreter fallbacks,
zero candidate overflow, zero static dispatch misses, eight invalidations and
nine revalidation CRC misses. Dirty execution is 71,182,859 instructions in the
diagnostic run; the ordinary terminal heartbeat reaches 125,345,648 after the
Mission 2 overlay arrives. The representative route is correct and repeatable,
but Mission 2 native closure remains explicit debt.

The acceptance status advances from `bootstrap_verified` to
`representative_slice_verified`. This does not erase the brief start-of-level
graphical defect or establish Missions 2–19. Those become the next compatibility
and campaign-coverage work, ahead of or alongside optional enhancements.

### R11 — compatibility baseline closed; unsafe Mission 2 shards rejected

The accepted 42,480-sample route was reused as the compatibility oracle. The
diagnostic observer gained bounded `--stop-after`, exact-frame and stepped-range
capture requests. OpenGL reads the authoritative FBO while software reads its
CPU-owned VRAM; requested but absent frames are explicit evidence failures.
Dense captures across frames 2169–2300 and stepped captures through frame 3000
show correct geometry, pages and textures in both renderers. Three bounded
cache-complete attempts contradict recurrence of the earlier catastrophic
blue-plane/red-checkered failure. Across the later 71-frame comparison, the
largest mean RGB delta is 3.723/255 and is visually limited to shading/raster
edges, consistent with the already documented host 8-bit versus PSX 5-bit
Gouraud precision debt. No generated retail code was changed.

The immutable overlay history contained eight new exact-byte compilable
variants. Promoting the complete set into a diagnostic cache was falsified: the
route stopped progressing in TITLE near frame 11,377 with starvation exit 2.
The three newly loaded early overlapping partial regions and their metadata
were moved into an ignored quarantine. The four later regions at `0x0014D000`,
`0x0014E000`, `0x00162000` and `0x00163000` passed a bounded diagnostic and the
entire route, so only those four were promoted to the ordinary cache.

The safe diagnostic endpoint loads seven regions, registers 164 candidates and
reports 9,810,330 native overlay dispatches, 270,891 fallbacks, 70,947,707 dirty
instructions, zero candidate overflow/static misses, ten invalidations and 27
CRC revalidations. Its stable retail-state sequence and slot-1 card match the
earlier diagnostic; 19 rather than 14 sampled transitions expose transient
observer-visible stack-depth steps without changing following-state/page
origins.

Two fresh ordinary hidden-OpenGL processes consumed all 42,480 samples in about
717 seconds each. Their logs match apart from isolated writable-state paths.
Both end orderly at frame 42,480 with exactly 124,850,811 dirty instructions.
Slot 1 is byte-identical at SHA-256
`ab79103084f591b122eff13803b64dec166102454ac10144b5a55399e1e2cf1f`;
slot 2 is byte-identical at
`7706c7d43edaf8cb7618e574f03457105153e3bdc196db803a600ad96a8f58e8`.
The compatibility baseline is therefore closed. Campaign-wide correctness and
the subtle native-resolution raster-precision delta remain explicit debt.

### R12 — visible validation revokes native-overlay compatibility baseline

Repeated visible/manual launches contradicted the hidden-replay acceptance.
After briefing, the ordinary build intermittently entered either a fatal GTE
loop or a black-screen spin while SPU output continued. Quarantining the
resident `0x8001E000` control-flow-only capture was necessary but did not fix
the visible transition.

The ordinary-Release focused write trace in
`human-transition-20260804-020449` localized the black-screen run without
recompiling retail translation units with diagnostic instrumentation. Runtime
code was installed at `0x801D8680` through normal retail/BIOS ownership. At
frame 2386 resident function `0x8001E278` received that code address as a
geometry descriptor. Its signed count at `a0+6` was negative, so the loop at
`0x8001E664..0x8001E6AC` could never decrement to zero and began overwriting
the loaded code region. The freeze report ends at frame 2458 with guest PC
zero, VBlank pending, interrupts masked, MDEC/CD work complete and SPU still
active. This explains the black display and repeating audio without assigning
ownership to FMV, CD-ROM or presentation.

Native overlay CRC `0x3F64E67F` executed 407,248 calls immediately before the
first proven invalid geometry ownership. The previously rejected resident CRC
`0x714A5E16` did not dispatch. A subsequent ordinary visible/manual run with
`PSX_OVERLAY_NATIVE_OFF=1` passed the same briefing-to-Mission-1 gate. This
confirms compiled runtime-overlay ownership as the bounded compatibility
owner; it does not yet prove which native entry first diverges. Hidden replay
is retained only as a secondary deterministic regression and can no longer
close the visible compatibility gate.

SF3 now defaults runtime-installed overlays to interpreter ownership through
the source-owned `overlay_native = false` game setting. Capture remains active
for audit and future native promotion. Static resident executable code remains
recompiled. The prior 82% native-overlay measurements are historical evidence,
not the ownership of the accepted build; current runtime-overlay native
ownership is intentionally 0% until entry-level equivalence is proved. The
campaign remains unverified beyond the user's earlier Mission 1/Mission 2
slice.
### R12a — isolated enhancement input work begins from the corrected baseline

Enhancement work moved to the independent `SF3_Redux` worktree at compatibility
commit `6aa349e`; the standalone recomp worktree remains unchanged. Review of
the compatible SF1/SF2 projects shows that 4x internal supersampling and
configurable keyboard PAD mapping are already generic framework facilities.
The first Redux source profile enables those facilities at 4:3 and leaves
widescreen/interpolation off pending SF3-specific capture gates.

A disabled-by-default relative-mouse adapter now emits bounded ordinary retail
PAD state and maps mouse buttons to retail controls. It resets on lost focus,
is inert for hidden/headless runs and commits once per vblank. Keyboard paths
received the same focus isolation. Unit and source-contract regressions cover
the new boundary. This layer enables immediate keyboard/mouse playtesting but
is explicitly not the direct camera/freelook milestone.

An independent raw-executable check narrows the true-camera candidate to the
unique SF3 instruction at `0x800549C4` inside the structurally mapped routine
at `0x80053954`. The local register semantics match SF2 while SF3's controller
layout differs. Owner and pitch offsets remain unproven and are the next live,
bounded invariant; none will be copied by address analogy.

### R13 — SCUS-94640 direct camera reaches structural acceptance

The focused read-only route probe was corrected through three bounded harness
issues: mapped-drive spelling must be preserved for the child process,
function tracing must be explicitly armed, and `cyc_watch_dump` is streamed
multi-line JSON. The final baseline proof reaches state 0 near frame 2177,
records the exact semantic block and establishes the live player, controller,
wrapper, base, owner and paired pitch fields. No guest RAM was written.

The direct bridge uses live `$s3` for the player and `$s2` for the controller,
so it improves on the SF2 global-pointer dependency. Generation is guarded by
the exact `0x8EA30034` word at `0x800549C4`; runtime additionally gates state 0,
RAM pointer validity and retail camera ownership. A 4x Redux diagnostic replay
exposed the opening scripted owner `0x801AEE48`, distinct from player
`0x801B0608`; the guard rejects that interval. Unit tests cover chase, aim and
owner rejection. The 53-test framework suite passes.

An independent generated tree links ordinary and diagnostic Release products.
Its generated source contains one hook immediately before the unmodified retail
instruction. The accepted route's header was retagged for the changed input
contract only after checking whole-file SHA-256; its 42,480-sample payload is
byte-identical. The 4x diagnostic product reaches state 0, records exact hook
hits and terminates cleanly at sample 3000. Visible mouse feel and scripted
handoff remain human acceptance items; widescreen is still disabled.

### R14 — compatibility and enhanced input become runtime-selectable

Human acceptance subsequently covered the complete first mission: death,
checkpoint reload, Mission 1 completion, FMV, new memory-card creation, save,
Mission 2 FMV/briefing/cutscene and entry into gameplay. The tester reported
no further Mission 1 discrepancy after the bounded startup-render fix. This is
strong compatibility-oracle evidence, but it does not replace the replay gate.

Audit then found that direct camera enablement still lived only in the bundled
game profile. The verified hook remains identical, while per-install
`settings.toml [controller]` can now enable/disable the host bridge and tune
chase/aim X/Y sensitivity plus Y inversion. A `PSX_MOUSE_CAMERA` override makes
headless A/B explicit. Launcher saves preserve the fields.

Release tests pass 54/54 with forced UTF-8 (the unforced Greek Windows code
page produced three Python decode errors, all absent under the deterministic
test environment). One rebuilt Release executable then completed paired
hidden, dummy-audio 3,000-sample runs with camera enabled and disabled. Both
produced identical card hashes; the route payload remained SHA-256
`6d26b87efb8b9cf935d73a156581edb899d2891896bd761d7d0ab7ec1499840f`
and was retagged only after its whole-file source hash was verified. This
closes runtime switch ownership; the full accepted-route matrix remains next.

### R15 — visible 4x acceptance exposes localized primitive debt; mouse playtest prepared

The source-only compatibility baseline was frozen at `3dd2f7b` plus the public
declaration correction `4250697`; the public repository carries the equivalent
history through `4d6b679`. Human testing then accepted the same visible Mission
1 entry with runtime overlays interpreter-owned. The deterministic 4x and SF2
keyboard defaults were checkpointed at `6e654d5` and published as `c64ebef`.

The 4x run confirms correct title, briefing, Mission 1 entry and continued
gameplay, but contradicts the claim that opening-room presentation debt is only
a subtle raster delta. The user supplied a repeatable visible capture containing
oversized textured triangles/quads that form long multicolored shards. The HUD,
player and parts of the room remain coherent, and later rooms appear normal.
`MISSION1_PRIMITIVE_CORRUPTION.md` normalizes this as malformed world primitives
and orders packet/vertex/OT checks ahead of E-state and texture-state leakage.
The shared GPU/presentation contract was consulted: ordering and persistent
per-page state remain authoritative, and hidden captures are negative controls,
not visible acceptance. SF2 Recomp is the independent validator for any generic
GPU invariant.

The already bounded SCUS-94640 direct-camera work was integrated without
copying SF2 addresses. Generation emits one exact-word-guarded hook at
`0x800549C4`; runtime additionally requires state zero, valid live pointers and
retail camera owner equality. Direct-camera mode keeps mouse motion off the PAD
path while left/right buttons retain retail Square/fire and L1/aim. A new
title-neutral wheel queue converts each notch to one retail Select edge and
inserts a sampled release between queued edges; retail still owns weapon order
and selection. Focus loss clears all pending input.

The ordinary Release product logs OpenGL 4x, interpreter-owned runtime overlays,
the enabled guarded camera and the installed tracked keybindings. A hidden,
dummy-audio replay retagged only after source-hash verification consumed 3,000
samples and exited at the bounded marker. This is a build/lifecycle smoke test,
not mouse-feel or visible-graphics acceptance. The desktop shortcut was not
launched; the next human gate is chase freelook, held-right-button aim,
left-button fire, wheel weapon changes, scripted-camera handoff and Mission 1
through Mission 2 entry.

### R16 — original-quad rejection owns the opening-room shard candidate

The bounded GP0 analyzer found no packet-length mismatch in 59 broadly flagged
world polygons. It did find 41 commands beyond the PS1 primitive edge limit.
Five shaded textured quads (`GP0 3Ch`) match a sharper invariant: one of the
runtime's two decomposed triangles was rejected and the other survived. This
is sufficient to produce the long textured half-quad shards seen by the user.
All five have coherent packet lengths and world submission provenance at guest
PC `0x800F5B3C`.

PSX-SPX documents the 1023-horizontal/511-vertical polygon limit. More precise
SCPH-5501 tests in the pinned PCSX-Redux reference establish that quad rejection
is performed on the original perimeter (`0-1, 1-3, 3-2, 2-0`) and drops the
complete command, not each raster triangle independently. The framework's
2026-07-14 correction had encoded the latter behavior and therefore contained
both a false-survivor and an internal-split false-reject case.

The generic helper now checks the original polygon edges before draw offsets or
enhancement transforms. Textured commands retain their TPAGE side effect before
the rejection boundary. A synthetic regression covers complete-quad rejection
when one triangle would survive and acceptance when only the internal split is
oversized. The analyzer labels both `hardware_oversize` and
`partial_quad_risk`; the captured route contains five such risks.

Release tests pass 63/63. The ordinary and diagnostic candidates rebuild. Two
clean ordinary hidden OpenGL/dummy-audio runs consume 3,000 samples, exit at the
bounded marker and produce identical card hashes that also match the pre-fix
smoke. This is a deterministic compatibility gate, not visual acceptance. The
desktop shortcut points to the rebuilt ordinary candidate; the next visible
gate is no shards in the opening room followed by mouse chase/aim/fire/wheel
and the connected Mission 1-to-Mission 2 route. SF2 Recomp is the independent
validator for the generic quad-perimeter contract.

The unchanged accepted-route payload was then rebound to the current
source-derived input contract only after whole-file verification; its 42,480
samples retain payload SHA-256
`6d26b87efb8b9cf935d73a156581edb899d2891896bd761d7d0ab7ec1499840f`.
Two additional ordinary hidden OpenGL/dummy-audio processes consumed the full
route and exited at the exact bound. Their isolated card images match
byte-for-byte (`A717D08D...CC3F`, `7706C7D4...8E8`). This extends the quad fix
through the recorded death/checkpoint, Mission 1 completion, result/FMVs, card
flow and Mission 2 handoff without claiming visible pixel acceptance.

### R17 — visible quad and modern-input acceptance reaches Mission 4

The rebuilt ordinary 4x candidate passed its remaining human gates. The tester
reported no graphical corruption in the Mission 1 opening room and comfortably
continued through connected retail play to Mission 4. Mouse freelook, aim,
fire, wheel weapon selection, scripted-camera ownership handoff and the SF2-
style keyboard profile all remained usable across that session. Overall visual
and control feel was reported as excellent.

This closes visible causality for the original-quad perimeter correction and
human acceptance of the current 4x mouse/keyboard profile. It does not claim
Mission 4 completion or whole-campaign compatibility. Missions 5–19, later
FMV/briefing/state transitions, checkpoint variants and save/load seams remain
campaign qualification work. The next compatibility priority is a per-mission
matrix that records the exact first divergence, while widescreen and PGXP stay
isolated behind independent enhancement gates.

### R18 — SF3-owned native-wide projection and culling composition

The SF2 recomp notes and private corpus were consulted before changing SF3.
Rejected SF2 leads stayed rejected: no packed-SXY provenance cache, textured-
edge expansion or broad ordering-table compensation was adopted. The generic
automatic 320x240 screen-cull detector emitted zero calls for SCUS-94640, so it
does not own this title's culling.

The reusable correction from SF2 checkpoint `a2b951c` was ported as an opt-in
runtime contract: a title may expose aspect-scaled GTE X to retail visibility,
then inverse that projection exactly once for a structurally classified dense
polygon linked-list DMA submission. The classifier defaults off, is identity
at 4:3, preserves PS1 primitive rejection on raw packet coordinates, and has a
focused composition/parser regression.

SCUS-94640 was measured independently. A passive 3,000-sample diagnostic route
recorded 227,206 primitive rows across 688 frames. Mission 1 list 3 contained
483..925 polygon commands per sampled frame; list 4 contained 5..21 and list 5
contained 1. The profile threshold is therefore 64: above every observed
auxiliary submission and below the smallest observed world submission. No SF2
address, threshold claim, packet payload or application state was copied.

The corrected 16:9 diagnostic run reported guest scale 3:4, zero inverse work
through boot/menu/movie states and 174,900 restored vertices after Mission 1
gameplay engaged. It exited at all 3,000 samples with baseline-identical blank
cards. Two ordinary hidden OpenGL/dummy-audio short runs and two complete
42,480-sample runs also exited at their exact bounds. Both complete runs match
the accepted card hashes `A717D08D...CC3F` and `7706C7D4...8E8`.

The required Ninja/MinGW suite passes 65/65. The exact 4x/4:3 build remains the
control; the 4x/16:9 build is an isolated visible candidate. The remaining gate
is human inspection of camera pans at the former 4:3 edges, HUD corners, FMV
pillarboxing, fades/scopes and mission transitions. SF2 Recomp independently
validates the generic DMA-submission ownership model; Tenchu independently
validates the one-projection-owner constraint through a different title-owned
mechanism.

### R19 — PGXP Gate B exposes a false replay gate and the baseline scheduler race

The first isolated PGXP candidate compiled, initialized the real NVIDIA OpenGL
3.3 path and completed a short diagnostic route with exact address/generation
provenance. The user nevertheless rejected it immediately: Mission 1 stayed
black after the briefing while dialogue and later conversations continued with
choppy audio. A geometry-only replacement reproduced the same symptom.

The evidence launcher retained the exact 8,619-sample user route. Three bounded
replays required retail state 8, state 0 and state-0 display-page activity. The
geometry-only build, the same build with all PGXP switches disabled, and the
pre-PGXP accepted diagnostic build all reach state 0 and then lose guest work
at the same boundary. Geometry correction has zero hits before the divergence.
The geometry and pre-PGXP cases agree at frame 2760, dirty-instruction count
146,028,664, BIOS function `0x000029CC`, last store `0x8001E6A0`, return address
`0x8001F49C`, `I_STAT=1` and `I_MASK=0`.

This contradicts PGXP ownership and reopens the generic scheduler/interrupt
lifecycle. It also invalidates two apparent 42,480-sample PGXP successes: both
had emitted early freeze dumps before eventually exhausting the host input
timeline. The observer now rejects semantic depth-0 work stagnation and
non-startup freeze dumps in addition to requiring explicit retail milestones.
Full detail and the exact stop boundary are in
`docs/sf3/PGXP_GATE_B_BLACK_SCREEN.md`. Per the objective, investigation stops
after corpus consultation and three bounded falsification attempts; no wakeup,
state force or interrupt-mask containment was added.

### R20 — stable CD DMA ownership restores the visible Mission 1 handoff

The reopened black-screen boundary was localized below PGXP and presentation.
The CD DMA consumer could observe a different sector buffer after a command or
device edge changed the live CD state during a split transfer. The runtime now
latches the completed sector that owns the transfer and keeps that immutable
payload until the DMA consumer finishes. Bounded diagnostics retain the sector
identity and transfer progress without changing retail state or fabricating a
wakeup. A focused split-DMA regression covers the invariant.

The rebuilt visible candidate passed the previously failing briefing-to-
Mission-1 transition and the user accepted Mission 1 gameplay. This supersedes
the headless-only compatibility claim: the owning fix was accepted in the same
visible/manual path that had repeatedly failed. The PGXP experiment remains
disabled and is not part of this checkpoint. Tab remains the retail R1 binding;
host turbo moved to keypad plus and has a source-contract regression.

### R21 — native-wide visible acceptance and bounded presentation debt

The first visible candidate was not actually exercising native-wide output:
its generated game-wide settings lacked `[video] aspect_ratio = "16:9"`.
After correcting the profile, true 16:9 exposed disconnected right-side world
slabs. Four bounded A/B checks assigned ownership:

- disabling guest projection did not remove the slabs, contradicting projection
  ownership;
- disabling the full-mirror compositor alone did not remove them;
- disabling `nw_hud_corners` removed the displaced slabs but exposed the
  mirror compositor's empty center dependency;
- disabling both produced one continuous authoritative native-wide world.

SF3 has no proven HUD sprite address boundary for the generic corner heuristic.
It was therefore shifting normal world polygon families as though they were
screen-space UI. The accepted profile keeps the measured dense-world GTE/DMA
composition but sets `nw_hud_corners = false` and `nw_full_mirror = false`.
The user then accepted Mission 1 widescreen world rendering and reported no
remaining culling defect.

A broad SF2-inspired full-width polygon/quad rule was also falsified: the human
countercheck produced a large vertical world slab. That rule was removed. A
narrow helper remains only for partial-height, authored-width PS1 monochrome
TILE rectangles. It is structurally screen-space, passes its focused C99 test,
and does not rewrite world polygons. It does not yet classify every SF3
cutscene matte.

Accepted limitations are explicit: cutscene black bars stop at the original
4:3 edges, and HUD/UI stays inset at original 4:3 coordinates (low priority).
No broad heuristic was added to conceal either issue. PGXP remains disabled.

Qualification after human approval:

- Release framework suite: 66/66;
- CD split-DMA sector-latch, turbo-hotkey, SF3 widescreen-profile and
  full-width TILE regressions: pass;
- two clean 3,000-sample OpenGL runs end at the exact bound and match the
  captured frame SHA-256 `542E3553...FC68` plus both card hashes
  `A717D08D...CC3F` and `7706C7D4...8E8`.

The complete 42,480-sample route was not repeated for this presentation-only
acceptance delta; its prior two-run compatibility qualification remains the
control. SF2 Recomp is the independent validator for provenance-scoped HUD and
matte expansion.

### R22 — list-qualified cinematic mattes complete the accepted widescreen slice

Human acceptance reopened the known 4:3 matte debt. SF2's full-width-effect
implementation was consulted, but its broad quad predicate could not be copied:
the earlier SF3 countercheck extended the bars while also turning width-
spanning world geometry into vertical slabs.

The existing SF3 census supplied a bounded owner. During the Mission 1
conversation, linked-list 4 repeatedly submits sixteen mono quads (`GP0 28h`)
spanning authored X `-192..192`; the black top and bottom bands occupy
`-120..-70` and `70..120`. The dense world owner remains list 3. A temporary
vertex trace confirmed the complete four-vertex topology, black color, list
identity and ordering rank, then was removed.

The accepted correction does not widen arbitrary polygon vertices. It
classifies an authored-width axis-aligned quad only after the caller proves
screen-space/effect-list ownership, then routes it through the existing flat-
rectangle backend. That backend already owns native-wide margin coverage and
avoids the shared-diagonal blend seam. Dense world submissions cannot enter
the path.

The focused helper regression covers zero/centered origins, reverse winding,
projected rejection, narrow rejection and explicit world-owner rejection. A
3,000-sample Mission 1 route completes with the central 384-pixel guest capture
byte-identical to the accepted control (`542E3553...FC68`), which is expected:
only the host-wide side margins change. Human testing then confirms full-width
cinematic bars, HQ rendering, widescreen world presentation and mouse/keyboard
operation together, with no return of the world-slab defect. HUD relocation
remains separate low-priority debt.

Post-acceptance qualification passes the UTF-8 Release framework suite 66/66.
The ordinary `build-wide` Release target rebuilds cleanly from the accepted
sources; the generated executable remains a local, retail-derived artifact and
is not eligible for source-repository publication.

### R23 — public owned-input bootstrap package

The redistributable deliverable is now an owned-input generator rather than a
pre-generated SF3 executable. The Windows bootstrap carries the exact
PSXRecomp CLI/runtime, PCSX-Redux OpenBIOS and notice, plus source-owned SF3
configuration. Before owned-input generation it verifies a complete package
path/size/SHA-256 manifest. It rejects retail media, SCUS payloads, generated
game code, captures, cards and reports. After generation it admits only the
supported `SCUS_946.40` executable SHA-256, applies the accepted 4x/16:9/input
profile, regenerates locally and compiles an ordinary private Release.

The first clean-room compile exposed a generic Windows boundary: 249 split game
C paths were forwarded in one `cmake -D` argument to the generated-source
guard, exceeding `cmd.exe`'s command-line limit before the guard could execute.
The runtime now writes the source list to a build-tree manifest and passes one
bounded filename. A source-owned regression covers 300 existing shards and the
actionable missing-shard failure. The same long-path clean project then linked
`Syphon_Filter_3_Recompiled.exe` and completed a 60-sample headless/silent
smoke. The framework suite remains 66/66; the new focused Python regression is
3/3. Generated output and the smoke timeline remain private.

### R24 — campaign qualification ledger bounds the Mission 4 claim

The next compatibility boundary is now represented by a source-owned 19-row
campaign ledger rather than prose that could blur arrival, gameplay and
completion. `docs/sf3/CAMPAIGN_QUALIFICATION.md` records each retail resource,
entry, gameplay, death/checkpoint, completion, outbound transition, save/load
and automation gate. A focused regression checks the exact SCUS-94640 campaign
order and current evidence ceiling.

The matrix preserves the strongest supported claims: Mission 1 has two-run and
human representative-slice evidence through the Mission 2 handoff; connected
human play completed Missions 2 and 3; Mission 4 has entry-only human evidence;
Missions 5–19 remain open. Direct mission boot and a rendered first frame are
explicitly excluded from campaign qualification.

The private validation contract and SF2/SF3 project records were consulted.
They reinforce adjacent retail transitions, isolated card state, exact profile
identity and two clean processes. The retained Mission 4 human route remains an
input witness rather than a deterministic campaign route: `PSXPAD2` records
retail PAD samples, while the accepted direct-camera bridge separately consumes
host relative-mouse motion. No route was retagged and no gameplay claim was
promoted.

The next automated gate is therefore Mission 4 completion through retail
Mission 5 entry, starting from copies of the preserved Mission 4 card in two
isolated writable directories under the ordinary 4:3 compatibility profile.
Only after matching semantic/device/dispatch evidence passes should the same
seam be checked visibly at 16:9. SF2 Recomp is the independent validator for
the adjacent-transition evidence contract. The reconfigured UTF-8 Release
framework suite passes 67/67, including the new matrix guard.

### R25 — PGXP returns to the visible gate after CD DMA correction

The user selected PGXP as the next enhancement after accepting HQ widescreen
and cinematic mattes. The retained `compat-candidate-2` routes and generated
profiles were audited before reuse. Both PGXP build trees share compatibility
identity `psxrecomp-a4877d515eb730e4`, exactly matching the 3,000- and
42,480-sample routes; copied core runtime sources match the current tree. The
ordinary and diagnostic Release products were rebuilt without editing generated
game code.

The historical Gate-B failure was retested as a true config A/B. PGXP off,
geometry-only and geometry-plus-perspective each passed twice in isolated
diagnostic processes through TITLE, briefing state 8 and live Mission 1 state
0. Every run retained 45 state-0 display-page samples, live subsystem evidence,
zero known-corruption matches, zero non-startup freeze dumps and no semantic
stall. Final periodic samples recorded zero correction hits for off; about
2.1k geometry hits and zero perspective hits for geometry-only; and about 2.1k
geometry plus 2.1k perspective hits for full PGXP.

The exact polled transition lists are not byte-identical: short-lived depth and
application-state intermediates are sometimes observed in one diagnostic run
and missed in another. The comparator therefore rejects strict list equality,
even though both runs preserve the required ordered retail milestones,
following Mission 1 transition, three framebuffer origins and complete live
state-0 snapshots. That observer-timing limitation is retained rather than
weakened or hidden.

Promotion then used the observer-free ordinary Release product. Two fresh
processes consumed all 42,480 recorded samples with the exact bounded marker,
no freeze artifacts, byte-identical normalized logs and matching card hashes:
`A717D08D...CC3F` and `7706C7D4...8E8`. The automated PGXP route gate is
therefore restored after the generic CD DMA fix. Visual quality is still open;
the next evidence is a human 4x/4:3 off/full comparison through the Mission 1
handoff and gameplay. SF2 Recomp remains the independent PGXP contract
validator; no SF2 address or title containment was adopted.
