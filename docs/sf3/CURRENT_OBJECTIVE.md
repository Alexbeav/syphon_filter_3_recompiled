# Current objective — deterministic SCUS-94640 TITLE

Updated: 2026-08-03

Status: feasibility, stretch and FMV correction gates achieved; user test and
provenance-clean publication checkpoint in progress.

## Objective

Establish a clean reproducible SF3 game-project generation and Release build,
then boot OpenBIOS and the authentic SCUS-94640 executable through CRT,
`Game_Main`, the application loop and stable retail TITLE. Capture/rebuild
runtime-installed overlays and measure static, native-overlay and interpreter
ownership. Stretch through retail Story/Mission 1 selection, state 8 and
state-0 player control.

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

- Release framework suite: 41/41 with `PYTHONUTF8=1`, including the generic
  OpenGL 15/24-bit coherency regression.
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
- A neutral cold boot naturally plays SCEA and then the animated TITLE stream.
  SCUS-94640 requests the Tokyo intro only after retail accepts New Game.
- The prior story probe could bleed an accepted Cross press into the following
  movie. It now gates on active TITLE decoding and releases immediately at the
  observed retail transition.
- Two hidden-OpenGL, dummy-audio runs captured clean Tokyo intro frames, reached
  state 8 at frame 3499, and returned to state-0 control with zero dispatch
  misses.
- Fresh generation A/B tree SHA-256 is
  `096032a2bd37ca13bc163b94693d21281eb17d60829eb68e6a753559f18b3918`;
  both Release products normalize to
  `3a43b1461cc82f07d86179ec56d8e2509df6d4235c108416299f2ea79e016dfe`.
