# Current objective — SF3 Redux Phase 1

Updated: 2026-08-04

Baseline state: `compatibility_baseline_verified`. A connected human route now
covers cold boot, Story/Mission 1, death, checkpoint reload, full mission
completion, FMV, new-card save and the retail Mission 2 handoff through live
gameplay. Two ordinary hidden OpenGL replays and a passive diagnostic replay
consume the same complete route after safe Mission 2 overlay promotion. The
previous catastrophic red/checkered failure and deterministic opening-room
textured-shard defect are fixed. Visible 4x testing confirms a clean Mission 1
opening room and connected, comfortable play through arrival in Mission 4.

Redux state: `phase1_widescreen_human_accepted`. The isolated branch has a
clean 4x/4:3 control and a 4x/16:9 default candidate, keyboard mapping,
a reversible relative-mouse-to-retail-PAD fallback and a direct camera bridge
with strict focus, word, state, pointer and retail-owner guards. A generated
ordinary Release product and separate Release-diagnostic product both link.
Human mouse feel, aim/fire/wheel controls and scripted-camera handoff are
accepted through the connected Mission 1-to-Mission 4 session. Native-wide
world presentation, full-width cinematic mattes, mouse and keyboard are
human-accepted in Mission 1, and two clean 3,000-sample runs match frame and
card hashes. HUD/UI remains at its original 4:3 coordinates.

## Objective

Carry the verified retail-compatible build into optional PC enhancements in an
isolated project. First deliver 4x internal resolution, configurable keyboard
and mouse input, and title-owned direct camera/freelook while preserving retail
state and gameplay. Validate every enhancement independently against the
accepted route, keep an off switch, and record honest native/fallback ownership.

## Current blockers

- Widescreen has no gameplay compatibility blocker in the accepted Mission 1
  slice. SCUS-94640's generic
  screen-cull detector emits zero sites, contradicting that route. A passive
  Mission 1 DMA census independently identifies list 3 as the world owner
  (483..925 polygons versus 1..21 for auxiliary lists). Guest-visible 3:4 GTE
  projection plus inverse raster composition only for lists at or above the
  measured 64-polygon threshold records 174,900 vertex restores in the short
  route. Two ordinary 42,480-sample runs complete with accepted card hashes.
  Visible 16:9 inspection confirms continuous world rendering after disabling
  the unowned blanket HUD-corner shift and full-mirror compositor. Remaining
  Full-width cinematic mattes are accepted through the list-qualified flat-
  rectangle path. Remaining presentation debt is optional HUD relocation.

- No structural or visible direct-camera blocker remains. Live SCUS-94640
  evidence proves
  the player/state/controller/wrapper/base chain, owner `+0xDC`, pitch
  `+0x8E8/+0x918`, and exact site execution. A visible human check of chase/aim
  feel and scripted-camera handoff passed through connected play reaching
  Mission 4.

- No representative-slice P0 remains. The cache-complete visible countercheck
  and three complete replays supersede the earlier cache-empty fatal.
- The visible opening-room primitive defect is closed with a proven generic GPU
  owner and visible acceptance of the rebuilt candidate.
  The runtime incorrectly rejected decomposed quad triangles independently;
  five captured `GP0 3Ch` commands would render one oversized half even though
  PS1 hardware drops the complete original quad by perimeter-edge limits.
- Mission 2 safe overlay coverage is compiled and replay-validated. The passive
  endpoint loads seven regions, registers 164 candidates, executes 9.81M native
  overlay dispatches and 270,891 fallbacks with 70.95M dirty instructions.
  Four overlapping early partial shards were rejected after they changed TITLE
  timing/flow; correct flow is proven, not campaign-wide native closure.

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
| Oversized textured shards in Mission 1 opening room | **closed 2026-08-04**: generic complete-quad rejection mismatch | no remaining observed impact through arrival in Mission 4 | five captured `GP0 3Ch` partial-quad risks, hardware-backed perimeter contract, 63/63 tests, two clean 3,000-sample runs, two complete 42,480-sample runs with matching cards and a clean visible 4x pass | passed: opening room has no shards and connected visible play reached Mission 4 |
| Small OpenGL/software raster delta at Mission 1 start | GPU raster precision | subtle shading/facet differences at native resolution | 115 dense common startup frames plus 71 later sampled frames; worst sampled mean RGB delta 3.723/255 | independently validate PSX 5-bit versus host 8-bit Gouraud/edge precision before changing presentation |
| Campaign overlays beyond early Mission 2 | overlay coverage | performance risk and incomplete recompilation ownership | safe Mission 2 endpoint: seven regions, 9.81M native dispatches, 270,891 fallbacks | extend only from exact-byte additive history and replay each promotion |
| Diagnostic display readback can alter host timing | validation observer | a clean observed run may not represent ordinary Release timing | OpenGL ring capture flushes/reads back even without CPU-VRAM synchronization; route observer is source/build validated only | reproduce under a recorded route, localize with bounded capture, then confirm the fix twice in ordinary Release with the observer disabled |
| Campaign beyond arrival in Mission 4 unverified | retail/content lifecycle | no whole-campaign claim | connected visible play reached Mission 4; Missions 5–19 and later lifecycle seams remain unverified | campaign qualification matrix covering every mission, transition, checkpoint and save/load seam |
| Cutscene mattes stop at authored 4:3 edges | **closed 2026-08-04**: auxiliary-list mono-quad ownership | no remaining observed impact in Mission 1 cinematics | list 4 carries `GP0 28h` black bands at authored `-192..192`; list 3 is the dense world owner; focused regression plus visible acceptance | passed: bars cover both 16:9 margins without restoring world slabs |
| HUD/UI remains at 4:3 coordinates | HUD provenance | low-priority inset HUD at 16:9 | human 16:9 Mission 1 capture; `nw_hud_corners` cannot distinguish HUD from world polygons in SF3 | relocate only structurally proven HUD primitives |

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

## Visible compatibility correction (2026-08-04)

Visible/manual testing revoked the native-overlay compatibility claim. The
Mission 1 handoff succeeds with runtime overlay native execution disabled and
fails with a compiled overlay active. SF3 therefore uses
`[runtime] overlay_native = false`: resident executable code remains static
native code, while runtime-installed overlays remain interpreter-owned and are
still captured for audit. Hidden replay is secondary evidence only; a visible
manual run is the acceptance gate.

The first localized black-screen divergence is resident function `0x8001E278`
receiving loaded overlay code at `0x801D8680` as a geometry descriptor, reading
a negative signed count and entering a non-terminating loop. Native overlay CRC
`0x3F64E67F` is narrowed as the preceding state owner; entry-specific
equivalence and campaign-wide validation remain open.

The accepted test presentation now defaults to 4x internal supersampling and
ships the SF2 recompilation keyboard profile beside the executable. This does
not change the 4:3 aspect ratio or the interpreter ownership decision above.

## Standalone publication

- Project checkpoint `db98b05` contains both generic fixes and 42/42 tests.
- Private-corpus commit `87e6c7a` records the independently confirmed
  `PSX-CD-001` candidate and corrected SF3 project snapshot.
- Public `Alexbeav/syphon_filter_3_recompiled` main is a provenance-clean,
  source-only history. It excludes retail inputs, generated SF3
  code, overlays, traces, cards, saves, captures and media.
- The lab retains its fetch-only upstream remote and has no writable project
  remote. `SF3_Redux` enhancement work has not begun.

Each public checkpoint is rebuilt from audited source paths rather than pushing
the lab history. Publication must continue to exclude OpenBIOS binaries,
local/private workflow material and every user-owned or retail-derived payload.
