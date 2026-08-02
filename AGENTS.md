# Codex instructions — SF3 recompilation feasibility lab

These instructions apply to this repository. It is an isolated,
noncommercial PSXRecomp experiment targeting USA *Syphon Filter 3*. It is not
the MIT shipping port and must not modify its sibling workspaces except for
explicit, provenance-safe feedback to the private PSX-Ports knowledge corpus.

## Mission

Determine whether the proven complete-executable, native-overlay-cache and
bounded dirty-RAM interpreter architecture reaches authentic SCUS-94640 TITLE
and Mission 1 faster and with less game-specific machinery than the current
hybrid runtime.

Minimum gate: two deterministic clean runs to stable retail TITLE with measured
static/native-overlay/interpreter ownership. Stretch gate: retail-selected
Mission 1 state-0 player control with GPU, SPU/XA and processed PAD evidence.

## Required reading before acting

Read these files completely at the start of each session:

1. `SF3_LAB.md`
2. `docs/sf3/CURRENT_OBJECTIVE.md`
3. `docs/sf3/FEASIBILITY_PLAN.md`
4. `docs/sf3/COMPARISON_PROTOCOL.md`
5. `docs/sf3/REFERENCE_MAP.md`
6. `lab/sf3/reference-manifest.toml`
7. `CLAUDE.md`
8. `I:\Projects\PSX-References\COMMUNITY_CONTRIBUTION_POLICY.md`
9. the mandatory corpus files named in `docs/sf3/REFERENCE_MAP.md`

`CLAUDE.md` is inherited framework context. Preserve its faithfulness,
no-stubs, no-generated-code-edits, bounded-diagnostics and evidence rules.
Its historical phase checklist and unrelated paths do not override this lab's
current objective.

## Workspace boundaries

- Work in `I:\Projects\SF3-Recomp-Lab`.
- Treat `I:\Projects\SF3-PC-Port` as a read-only SF3 semantic oracle.
- Treat `I:\Projects\SF2-Recomp-Lab` as read-only lineage/evidence.
- Treat `I:\Projects\PSX-References` as read-only research material.
- Consult `I:\Projects\PSX-Ports` before each new symptom. Update it only at a
  meaningful committed checkpoint and only with normalized, payload-free
  knowledge authorized by the user's goal.
- Never modify or launch another project's binaries.

## Licensing and provenance

- This fork remains PolyForm Noncommercial 1.0.0. Do not merge its code into
  the MIT SF3 product or describe it as commercially reusable.
- OpenBIOS is the tracked, redistributable LLE BIOS used by this experiment.
- Never commit a disc, retail executable, generated game C, captured overlay,
  sector, RAM/state dump, card, movie, audio, texture, screenshot or private
  third-party artifact.
- Keep all derived game material below ignored `lab/sf3/*` or
  `.local-context/` paths.
- External addresses and sibling fixes are leads until SCUS-94640 independently
  proves them.

## Architecture rules

- Retail owns frontend, gameplay, scripts, AI, collision, camera, objectives,
  saves and authored timing.
- Fix proven CPU/device/lifecycle defects in the generic framework layer and add
  a source-owned regression.
- Never force retail state, fabricate callback success, patch generated code,
  substitute native gameplay or encode a title-address containment.
- Interpreter fallback is compatibility evidence, not native coverage. Measure
  every dispatch tier honestly.
- No modernization work belongs in this experiment.

## Mandatory consult-test-return loop

For each new symptom:

1. Record expected/actual behavior and first semantic divergence.
2. Classify likely owner.
3. Search stable findings, candidates, contracts, failures, regressions and
   comparable project reports in the private corpus.
4. Convert each match into a bounded falsifiable SCUS-94640 check.
5. Record the lead as confirmed, narrowed, contradicted or irrelevant.
6. Fix the owning invariant and add a regression.
7. Update this project's report/devlog and return normalized knowledge to the
   corpus at the next checkpoint.
8. Name an independent validating project.

## Execution and evidence

- Run headlessly and silently unless the user explicitly approves a visible
  validation. Do not open a physical audio device.
- Use bounded TCP diagnostics, rings and structured summaries; never unbounded
  instruction logs.
- Require two clean processes and semantic comparisons at each milestone.
- Keep the complete repository footprint below 20 GiB.
- Do not ask for human testing until an automated gate passes.
- If blocked, perform three distinct bounded falsification attempts after
  corpus consultation, then document the exact first divergence without adding
  containment.

## Git discipline

- Expected branch: `experiment/sf3-recomp-feasibility`.
- There is no writable project remote. Do not add or push one.
- Preserve small milestone commits, update the objective/devlog/report, run
  `git diff --check`, relevant Release tests, artifact/provenance scans and a
  footprint check before committing.
