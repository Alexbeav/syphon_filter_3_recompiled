# Syphon Filter 3 recompilation feasibility lab

This isolated noncommercial experiment tests USA SCUS-94640 on the proven
PSXRecomp complete-executable and overlay lifecycle framework. It does not
replace `I:\Projects\SF3-PC-Port` and does not authorize code transfer into
that MIT project.

## Architecture under test

- Ahead-of-time translation owns the resident PS-X executable.
- Runtime-installed code is captured, compiled, cached and invalidated by
  identity/generation.
- Dirty-RAM interpretation remains a measured compatibility tier.
- OpenBIOS LLE and the runtime own PS1 hardware/device presentation.
- Retail SF3 owns all application and game behavior.

## Lineage

The repository was cloned from tracked commit `4f811c2` of the SF2 feasibility
lab with `--no-hardlinks`; ignored captures, builds, cards and private state did
not cross over. Framework history retains generic corrections for captured-CFG
MIPS-I load delays, encoded JALR links, IRQ delivery inside native call units,
runtime text invalidation and bounded GPU diagnostics. SF2-specific project
configuration and reports were removed from the SF3 branch.

## Start here

Read `AGENTS.md`, then the required SF3 documents it lists. All retail-derived
outputs belong under ignored `lab/sf3` storage. The fixed target and oracle
identities live in `lab/sf3/reference-manifest.toml`.

## Permanent non-goals

- No native gameplay or frontend replacement.
- No forced application-state writes or generated-code edits.
- No SF2 address reuse by analogy.
- No enhancement that changes retail simulation, authored timing or save state.
- No widescreen, PGXP, interpolation, remastered UI or mouse-camera claim
  without an independent compatibility control, off switch and bounded gate.
- No claim of static coverage when interpreter fallback remains.
