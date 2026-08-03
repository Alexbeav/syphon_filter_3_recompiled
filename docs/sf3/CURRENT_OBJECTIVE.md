# Current objective — representative SCUS-94640 Mission 1 slice

Updated: 2026-08-03

Graduation state: `bootstrap_verified`. The earlier state-0 bootstrap evidence
does not satisfy the representative-slice gate. Human validation contradicted
the readiness claim with a briefing-to-gameplay failure on one cold launch and
severe Mission 1 texture corruption on the next.

## Objective

Bring the authentic retail route from cold boot through user-selected Story,
Mission 1, sustained correct gameplay and the following retail transition.
Reproduce and fix the failed state-8 briefing handoff and corrupt gameplay
textures at their owning generic runtime invariants. Preserve the existing
generation, overlay and execution-tier evidence without treating it as proof
of playability.

## Current P0 blockers

- Ordinary Release can accept the Mission 1 briefing without beginning the
  mission.
- A recorded ordinary run plays the intro's XA audio but displays no video,
  consumes no visible retail input and never progresses into the mission. Its
  neutral-bookended 3,194-sample route contains 333 active retail-SIO samples,
  so missing host input delivery is contradicted while guest consumption is
  not yet established.
- A separate clean launch can reach state-0 gameplay with large world surfaces
  sampling visibly wrong red/checkered texture data while geometry, actors and
  HUD continue to render.
- The diagnostic probe stops after a movement sample. It does not cover
  sustained rendering, audio, pause, combat, death/restart, checkpoint restore,
  objective completion or the next retail transition.
- A retail-boundary input recorder now builds and has a passing source-owned
  contract test. A bounded two-run helper can replay through a hidden renderer,
  but no human Mission 1 route has been recorded or replayed. These are witness
  mechanisms, not resolution of either intermittent P0.

## Representative-slice exit gate

- Two clean ordinary Release processes follow cold boot → retail frontend →
  user-selected Story/Mission 1 → briefing → authored gameplay.
- Both framebuffer pages show correct world, actors, HUD, palette and textures
  across multiple rooms for at least five-to-ten minutes.
- Input, camera handoff, pause/resume, dialogue, music and effects remain live.
- Damage/death, retail restart and one checkpoint restore work.
- Mission 1 completes through its retail result/save/next-state flow.
- The connected deterministic route passes twice and a human completes the
  same representative route without developer-only state manipulation.
- Human evidence follows `docs/sf3/MISSION1_ACCEPTANCE.md` and identifies the
  exact first failed gate rather than treating initial movement as completion.

## Quality debt

| Debt | Owner | User impact | Evidence | Removal gate |
| --- | --- | --- | --- | --- |
| Briefing/movie handoff intermittently fails | MDEC/CD/IRQ or lifecycle/control owner unresolved | audio continues without video, input response or mission progress | captured 3,194-sample ordinary route with repeated Cross/Start runs | first divergence fixed; two ordinary Release routes pass |
| Mission textures can sample corrupt data | unresolved GPU/VRAM owner | gameplay is visually invalid | user cold-launch screenshot | software/OpenGL oracle comparison plus correct multi-room two-page presentation |
| Probe covers only initial state-0 movement | validation harness | false confidence in playability | prior `probe_story.py` exit boundary | extend through sustained play, failure/restart, checkpoint and completion |
| Human route recorder/replayer not runtime-validated | validation harness | offered playthrough cannot yet serve as deterministic witness | serializer, hidden-renderer helper guards and fresh Release link only | record one neutral-bookended Mission 1 route and replay it twice with matching semantic/GPU evidence |
| Diagnostic display readback can alter host timing | validation observer | a clean observed run may not represent ordinary Release timing | OpenGL ring capture flushes/reads back even without CPU-VRAM synchronization; route observer is source/build validated only | reproduce under a recorded route, localize with bounded capture, then confirm the fix twice in ordinary Release with the observer disabled |
| Campaign beyond Mission 1 unverified | retail/content lifecycle | no campaign claim | no connected mission matrix | later campaign-complete gate; not part of this representative slice |

## Starting evidence

- Framework lineage: SF2 lab `4f811c2`, PSXRecomp baseline
  `0cfa9fe0a8da944e9f694a24361b4973c57131ea`.
- Target executable: `SCUS_946.40`, SHA-256 gated in the manifest.
- Hybrid oracle independently proves entry `0x800FB368`, `Game_Main`
  `0x80029ED8`, application loop `0x80029FB8`, TITLE state `4/2`, and Mission 1
  stable gameplay state `0/1`.
- These addresses are comparison checkpoints, not permission to patch or force
  state.
- Repository clone footprint began at 0.073 GiB and contained no ignored
  source-lab artifacts.

## Initial sequence

1. Finish the SF3-only scaffold and provenance scan.
2. Initialize framework submodules and run the inherited Release suite.
3. Build/package the CLI.
4. Generate twice from the user-owned USA cue with tracked OpenBIOS.
5. Compare normalized manifests and build both generated projects.
6. Run headlessly/silently and locate authentic executable entry, `Game_Main`
   and stable TITLE from runtime state.
7. Capture/rebuild overlays, rerun twice from clean processes and record tier
   ownership plus GPU/SPU/CD state.
8. Only after TITLE passes, develop retail-sample-gated PAD automation for the
   Story/Mission 1 route.

## Minimum exit gate

- two normalized-identical clean generations;
- Release build and complete framework suite passing;
- two clean headless/silent runs reaching retail TITLE state `4`, depth `2`;
- active overlay identities plus native-overlay/interpreter dispatch metrics;
- deterministic semantic checkpoint comparison;
- no forced state, fabricated callback, generated-code edit or native
  substitute;
- updated devlog and knowledge report with corpus lead dispositions.

## Stretch gate

Retail frontend input selects Story/Mission 1, reaches state 8 and then state
`0/1`; player-owned state changes under recorded PAD input while GPU, SPU/XA
and CD remain live. Repeat from two clean processes.

## Achieved minimum evidence

- Release framework suite: 47/47 with `PYTHONUTF8=1`, including the generic
  OpenGL 15/24-bit coherency and CD seek-retarget regressions.
- Generated trees: 1,128/1,128 normalized-identical files, tree SHA-256
  `09043b8c29b5c34a0364d0fd36778fa7002ef14d29128938a60b272bf915433e`.
- Clean Release products: normalized SHA-256
  `a23b0071a7e8ae94746e1e0080a0e4cf4c43c62648724ddc8367842911ac683d`.
- Two clean native runs: executable entry, `Game_Main`, and application loop
  all occur at frame 714 with identical call records.
- Frame 714 and 1000 write/PC/MMIO/SPU/cycle fingerprints match exactly.
- Both runs reach retail TITLE depth/state `2/4`, with 122 valid native-overlay
  candidates, four loaded cache regions, zero dispatch misses/invalidations/CRC
  misses, and bounded residual fallback.

## Achieved stretch evidence

- A tracked state-gated probe now launches the diagnostic Release product with
  `--headless --no-launcher`, a fresh writable-state directory and no host
  audio output.
- Two fresh probe processes selected the visible retail `New Game` route,
  reached Mission 1 state/depth `8/2`, observed the retail state-8 pop, and
  reached state/depth `0/1` with the Mission 1 PAD return polling.
- Both runs produced identical state-8, pop and Mission 1 PAD call shapes. TCP
  polling landed within 5–10 guest frames between runs, so these are semantic
  matches rather than falsely claimed same-frame input schedules.
- At comparable final samples, static/native-overlay/fallback ownership was
  `38.699% / 61.187% / 0.115%` and
  `38.564% / 61.322% / 0.114%`. Each run had 123 registered candidates, four
  native regions and zero static misses, invalidations or CRC misses.
- Both runs retained live world-3D GPU traffic, SPU key-on activity, nonzero
  decoded XA input, retail CD service and silent host output. A movement-only
  Up press changed the rendered player position while state remained `0/1`.

## Achieved FMV correction evidence

- The corpus-matched FBO/CPU-mirror ownership fault is corrected generically
  at GP1 display-depth transitions; generated retail code is untouched.
- A neutral cold boot naturally plays SCEA, the full cemetery intro, and then
  the animated TITLE/menu. Retail New Game separately plays the Tokyo intro.
- The missing cemetery intro was caused by an active ReadN/ReadS stream
  surviving SeekL and retaining the old location. SeekL/SeekP now cancel that
  read generation and clear READ/PLAY before the requested seek takes ownership.
- The prior story probe could bleed an accepted Cross press into the following
  movie. It now gates on active TITLE decoding and releases immediately at the
  observed retail transition.
- Two cached hidden-OpenGL, dummy-audio runs captured clean cemetery and Tokyo
  intro frames, reached state 8 at frames 9523/9531, and returned to state-0
  control with zero dispatch misses. Native overlay ownership was 82.301% and
  82.304%; fallback was 0.086% in both runs.
- Fresh generation A/B tree SHA-256 is
  `b2994894e7b921b6e56adffa7c824ba65815c8dff9ea1974cb2c79f3e3757475`;
  both Release products normalize to
  `6d1cbdd2c1aa5e325ed0e86f3b405b6cd6ee6b15135ef355cc34b7e2c5852032`.

## Standalone publication

- Project checkpoint `db98b05` contains both generic fixes and 42/42 tests.
- Private-corpus commit `87e6c7a` records the independently confirmed
  `PSX-CD-001` candidate and corrected SF3 project snapshot.
- Public `Alexbeav/syphon_filter_3_recompiled` main is a parentless,
  provenance-clean source snapshot. It excludes retail inputs, generated SF3
  code, overlays, traces, cards, saves, captures and media.
- The lab retains its fetch-only upstream remote and has no writable project
  remote. `SF3_Redux` enhancement work has not begun.
