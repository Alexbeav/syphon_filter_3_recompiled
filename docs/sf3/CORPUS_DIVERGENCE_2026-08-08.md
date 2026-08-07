# SF3 Recomp versus the private corpus

Date: 2026-08-08

This report compares the authoritative `SF3-Recomp-Lab` working tree with the
private PSX reference/corpus contracts. It separates actual implementation or
qualification gaps from stale documentation. A difference is not automatically
a defect: some local decisions are evidence-backed title policy, and some
corpus statements simply predate the current SF3 checkpoint.

## Executive result

The compatibility architecture is substantially aligned with the corpus:
retail retains semantic ownership, generated game code is untouched, overlay
interpreter use is reported honestly, deterministic gates use clean processes,
PGXP fails closed on complete per-primitive provenance, and public material is
owned-input/source-owned only.

The important divergences are:

1. PGXP coverage is too sparse to remove motion-era wobble. Two clean 3,000-
   sample runs on 2026-08-07 agree exactly: 56,919 candidate triangles, 2,125
   complete corrections (3.733%), and 54,794 fully unmatched triangles. All
   164,382 unmatched vertex queries are `missing`; partial, stale, address-
   mismatch, packed-mismatch, speculative and invalid counts are zero. This
   confirms a provenance-transport/coverage gap, not corrupt metadata or an
   unsafe mixed primitive.
2. The v0.1.0 public bootstrap predates the current `PSX-PUB-001` distribution
   contract. It has a manifest/hash verifier and payload-name checks, but no
   public CI/release-kit workflow, no clean acquisition contract, no shared
   behavioral rejection matrix, no independent archive traversal/size/path
   auditor, and no re-download audit. It also assumes Python, CMake, Ninja and
   a compiler are already on `PATH`.
3. Optional features are profiles/settings rather than the corpus's newer
   `PSX-MOD-001` first-class launcher Mods. Widescreen, PGXP and mouse camera do
   have off states, but the public kit does not expose all three as independent,
   default-off toggles in one launcher lifecycle.
4. Campaign qualification is incomplete after Mission 4 entry. Mission 1 is
   deterministic and connected; Missions 2 and 3 have human completion; Mission
   4 has entry-only evidence; Missions 5-19 are open. This is a maturity gap,
   not a violation of the validation method.
5. The lab charter and the corpus SF3 snapshot are stale in opposite directions
   and should not be used as current status authorities.

## Contract comparison

| Area | Corpus contract | Current SF3 state | Disposition |
|---|---|---|---|
| Retail authority | Retail owns gameplay, scripts, AI, collision, camera, saves and timing | Preserved; no native gameplay substitute, forced state or generated-code edit | aligned |
| Determinism | Two clean processes at equivalent semantic boundaries; diagnostic evidence is not the ordinary oracle | Mission 1 and PGXP route gates use paired clean runs; ordinary and diagnostic lanes are kept distinct | aligned |
| GPU composition | Preserve persistent pages and all authored same-tick submissions | Local GPU work records complete same-tick submission behavior; the shared GPU contract still says this is pending | corpus snapshot stale; return at checkpoint |
| PGXP eligibility | Exact XY/depth metadata, exact RAM address/generation, all-corner atomic eligibility, renderer-neutral fallback, default off | Exact SWC2 address/generation/packed-value gate; all three corners required; unmatched primitives stay native | aligned |
| PGXP observability | Record matched and rejected primitives and inspect camera motion/dense geometry | Aggregate hits existed; this checkpoint adds complete/partial and reason counters | gap closed locally, pending commit/corpus return |
| PGXP visual result | Human high-resolution off/on comparison; plumbing is insufficient | User reports static improvement but model swimming during camera/motion; only 3.733% of route triangles qualify | open; current PGXP is not visually accepted |
| Presentation independence | Compatibility remains oracle; enhancements independently selectable and default off | Separate complete configs exist, but the public launcher does not expose independent Mods | partially aligned; product gap |
| Campaign | Connected deterministic content matrix, not direct-level or visible-frame inference | Explicit 19-row ledger; only Mission 1 fully deterministic | method aligned; coverage incomplete |
| Graduation language | Use standard states such as `representative_slice_verified`, `enhanced_playable`, `campaign_complete` | Project also uses custom phase labels (`compatibility_baseline_verified`, `phase1_widescreen_human_accepted`) | documentation divergence; map labels explicitly |
| Distribution | Audited owned-input kit, durable pins, clean-room setup, behavioral tests, CI/release workflow and downloaded-asset audit | Legal v0.1.0 kit exists and had one clean package-root build, but lacks the current full release contract | material release-hardening gap |
| Licensing | Explicit audience/license and no proprietary payload | PolyForm Noncommercial 1.0.0; OpenBIOS notice; retail/generated/private artifacts excluded | aligned |
| Workspace/public history | One authoritative working home with a curated public history | Lab is authoritative; legacy Published/Staging histories are archived as refs and their redundant directories recycled; renamed GitHub remote is canonical | corrected 2026-08-07 |

## PGXP: what SF2 contributes and what it does not

SF2's accepted pass implemented the same core rule now present in SF3: retain
guest-visible GTE/RAM values, bind precision metadata to exact stores, and use
correction only when every primitive corner validates. SF2's final report also
records selective coverage and remaining motion-era instability. Consequently,
there is no missing relaxed-match patch to copy from SF2.

The new SF3 classification rejects three tempting explanations:

- no `packed_mismatch` means the tracked packet word was not simply rewritten
  after projection;
- no `address_mismatch` or `stale` means a wrong generation/address is not the
  dominant failure;
- no `partial` means the route does not mostly lose one corner of otherwise
  tracked triangles.

Instead, every rejected corner lacks a precision record at the GPU packet
address. The next bounded experiment is therefore to identify how SF3 builds or
copies those packet words after GTE projection, then transport provenance only
through proven RAM-copy/packet-construction operations. Relaxing value-only
matching would contradict `PSX-GPU-005` and risks the stitched-geometry cracks
recorded by `FAIL-031`.

SF2-Modern's deeper source-semantic matrix/vector provenance is a useful oracle,
but it cannot be copied directly into a binary recompilation until SF3 proves an
equivalent semantic owner.

## Local documentation drift found and reconciled

- `SF3_LAB.md` declared widescreen, PGXP and mouse-camera work out of scope. It
  now distinguishes permanent faithfulness rules from independently gated,
  reversible enhancements.
- `AGENTS.md` said no modernization belonged in the experiment and
  foregrounded the already-complete TITLE/Mission 1 feasibility gate. It now
  names current campaign/Redux work while preserving compatibility authority.
- `docs/sf3/CURRENT_OBJECTIVE.md` and the devlog are the closest current status
  sources, but their PGXP section previously reported only aggregate hits and
  had not incorporated the user's motion-swimming result.
- `lab/sf3/README.md` named `dist/.../psxrecomp-game.exe`; it now uses the
  package's canonical `libexec/psxrecomp-game.exe` path.
- The standalone-publication section named the old underscore repository and
  said the lab had no writable project remote. It now names
  `Alexbeav/Syphon-Filter-3-Recompiled` and the guarded curated-export rule.

These corrections retain the historical feasibility evidence without allowing
stale phase rules to block user-authorized Redux/publication work.

## Stale or internally drifting corpus statements

- `_knowledge/projects/sf3.md` is dated 2026-08-03 and still classifies SF3 as
  `bootstrap_verified`, Mission-1-only, without mission completion, persistent
  save or modern presentation. Current local evidence proves the connected
  Mission 1 lifecycle/save/Mission 2 handoff, human play through Mission 4
  entry, and accepted widescreen/mouse work.
- The same snapshot's current-gap section contradicts later content already in
  that file. It should be replaced by a normalized current checkpoint, not
  incrementally extended again.
- `GPU_AND_PRESENTATION.md` says SF3 full same-tick composition is pending;
  local source/docs record that composition work as complete.
- `DISTRIBUTION_PLAYBOOK.md` describes the earlier SF2 11-test/WinGet contract,
  while the newer `PSX-PUB-001` candidate records a direct-archive, bounded
  acquisition contract with 15 focused tests. SF3 public hardening should target
  the accepted successor after that corpus discrepancy is resolved, not blindly
  reproduce the older WinGet path.

## Evidence-backed exceptions, not divergences

- `[runtime] overlay_native = false` is the accepted SF3 compatibility policy.
  Visible testing proved a native overlay changed retail flow; interpreter
  ownership is therefore an honest compatibility result, not failure to pursue
  native coverage.
- HUD elements remaining at authored 4:3 coordinates are disclosed optional
  presentation debt, not a compatibility defect.
- The public repository uses curated history rather than the complete lab
  branch. This is required provenance separation, not lost development history.

## Ordered closure plan

1. Keep PGXP geometry fail-closed and add bounded packet-construction/copy
   provenance tracing; do not ask for another visual test until coverage changes
   materially and two automated runs pass.
2. Map the now-reconciled local phase labels explicitly to corpus graduation
   states.
3. Upgrade the public kit to the resolved current `PSX-PUB-001` contract and
   expose Widescreen, PGXP and Mouse Look as independent default-off launcher
   features before publishing a new release.
4. Resume connected Mission 4 completion and the `4 -> 5` seam in two ordinary
   clean processes, then request the visible 16:9 confirmation.
5. At the next committed checkpoint, return a payload-free SF3 snapshot and the
   PGXP missing-provenance result to the corpus, naming SF2 Recomp/Tenchu as
   independent validators.

## Corpus sources consulted

- `PSX-References/START_HERE.md`, `PORTING_PLAYBOOK.md`, `BUILDING.md`,
  `PROJECT_TEMPLATE/PUBLIC_KIT.md`, and the community contribution policy;
- `PSX-Ports/_shared/PORT_QUALITY_STANDARD.md`,
  `DISTRIBUTION_PLAYBOOK.md`, and `FINDINGS_REGISTRY.md`;
- `PSX-Ports/_knowledge/contracts/GPU_AND_PRESENTATION.md` and `VALIDATION.md`;
- `PSX-Ports/_knowledge/FINDING_CANDIDATES.md`, including `PSX-GPU-005`,
  `PSX-PUB-001` and `PSX-MOD-001`;
- `PSX-Ports/_knowledge/failures/FAILURE_CATALOG.md`, especially `FAIL-031`;
- the SF3 and final SF2 Recomp project snapshots; and
- read-only SF2 Recomp/Modern PGXP documentation and source.
