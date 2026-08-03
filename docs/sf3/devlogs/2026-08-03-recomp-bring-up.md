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
