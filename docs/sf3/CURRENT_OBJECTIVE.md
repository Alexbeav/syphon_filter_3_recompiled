# Current objective — deterministic SCUS-94640 TITLE

Updated: 2026-08-03

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
