# Codex instructions — SF3 recompilation feasibility lab

These instructions apply to this repository. It is an isolated,
noncommercial PSXRecomp experiment targeting USA *Syphon Filter 3*. It is not
the MIT shipping port and must not modify its sibling workspaces except for
explicit, provenance-safe feedback to the private PSX-Ports knowledge corpus.

## Mission

Preserve and extend the proven complete-executable plus bounded dirty-RAM
interpreter architecture across authentic SCUS-94640 campaign qualification,
then qualify optional Redux presentation/input features independently against
the retail-compatible oracle.

The original TITLE and Mission 1 feasibility gates are complete. Current gates
are defined by `docs/sf3/CURRENT_OBJECTIVE.md` and the 19-row campaign ledger;
they retain two-process, dispatch-ownership and subsystem evidence rules.

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
- This lab is the authoritative SF3 working repository. The legacy
  `I:\Projects\SF3-Recomp-Published` and
  `I:\Projects\SF3-Recomp-Public-Staging` workspaces may be inspected and
  retired only after their clean tracked histories are preserved here and any
  ignored files are inventoried. No other sibling workspace is writable.
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
- Public GitHub publication is source-only and owned-input. Before every public
  push, audit the exact exported tree and package for retail executable/disc
  data, generated game or BIOS C, overlay captures/caches, cards/saves, RAM or
  state dumps, screenshots/media, private corpus material, credentials and
  absolute private paths. CI and release workflows must remain unable to
  acquire retail input or generate the private game executable.
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
- Optional modernization belongs only in isolated, independently switchable
  profiles after the compatibility gate. Compatibility remains the oracle;
  enhancement evidence cannot substitute for campaign or retail correctness.

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
- Keep the complete repository footprint below 60 GiB. Remove regenerable
  traces, temporary build trees and diagnostic caches after each completed
  investigation or milestone; the larger cap is working headroom, not a reason
  to retain obsolete artifacts.
- Do not ask for human testing until an automated gate passes.
- If blocked, perform three distinct bounded falsification attempts after
  corpus consultation, then document the exact first divergence without adding
  containment.

## Git discipline

- Expected branch: `experiment/sf3-recomp-feasibility`.
- The renamed public project remote is
  `https://github.com/Alexbeav/Syphon-Filter-3-Recompiled.git`. It may be
  configured in this lab after the existing curated public history is fetched
  and preserved.
- Never push the experiment branch or its full lab history directly to public
  `main`. Publish only an audited source-only curated/export branch that
  preserves the public repository's history. Never force-push or delete a
  public branch, tag or release without a separate explicit user instruction.
- Follow `I:\Projects\PSX-Ports\_shared\DISTRIBUTION_PLAYBOOK.md` and the
  community contribution policy for every public update. Record the exact
  source/export identities and payload audit before pushing.
- Preserve small milestone commits, update the objective/devlog/report, run
  `git diff --check`, relevant Release tests, artifact/provenance scans and a
  footprint check before committing.
