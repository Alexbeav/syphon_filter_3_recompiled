# SF3 recompilation reference map

## Mandatory SF3 oracle

- `I:\Projects\SF3-PC-Port\docs\SF3_PC_PORT.md`
- `I:\Projects\SF3-PC-Port\docs\PSX_PORT_KNOWLEDGE_REPORT.md`
- `I:\Projects\SF3-PC-Port\docs\devlogs\2026-08-02-sf3-bring-up.md`
- `I:\Projects\SF3-PC-Port\docs\SF2_EXECUTABLE_MAP.md`
- `I:\Projects\SF3-PC-Port\docs\SF2_SHARED_SYSTEM_MAP.md`
- `I:\Projects\SF3-PC-Port\docs\SF2_SF3_PORT_NOTES.md`
- `I:\Projects\SF3-PC-Port\docs\SF2_MISSION_SCRIPT_VM.md`
- `I:\Projects\SF3-PC-Port\docs\handoffs\sf3-retail-guest-alpha-2026-08-03`

These provide expected semantic boundaries. Independently reproduce every
address and behavior before it becomes recomp-lab configuration.

## Framework lineage

- `I:\Projects\SF2-Recomp-Lab\docs\sf2\SESSION_REPORT_2026-08-03.md`
- `I:\Projects\SF2-Recomp-Lab\docs\sf2\CFG_LOAD_DELAY_REPORT.md`
- generic commits `663ac4a`, `61d3667`, `dc873fc`, and `4b5edc7`

SF2 findings are leads. No SF2 game address, trigger or overlay identity is
valid for SF3 without SCUS-94640 evidence.

## Read-only reference library

- `I:\Projects\PSX-References\CATALOG.md`
- `PORTING_PLAYBOOK.md`, `NEW_GAME_CHECKLIST.md`, `PROJECT_TEMPLATE`
- pinned PSXRecomp, PsyDoom, SOTN, PCSX-Redux, DuckStation, PSX-SPX,
  `ghidra_psx_ldr`, splat, mips_to_c, asm-differ, decomp-permuter and maspsx

Observe each source's license. This PolyForm experiment may study the
references; no code transfers to the MIT product without separate provenance
and compatible independent implementation.

## Mandatory private corpus consultation

Read/search:

- `_shared/FINDINGS_REGISTRY.md`
- `_shared/BASELINE_CAPABILITIES.md`
- `_knowledge/FINDING_CANDIDATES.md`
- `_knowledge/failures/FAILURE_CATALOG.md`
- `_knowledge/regressions/REGRESSION_LEDGER.md`
- `_knowledge/contracts/CPU_AND_CONTROL.md`
- `_knowledge/contracts/DEVICE_AND_HLE.md`
- `_knowledge/contracts/GPU_AND_PRESENTATION.md`
- `_knowledge/contracts/VALIDATION.md`
- `_knowledge/projects/sf2-recomp.md`
- `_knowledge/projects/sf3.md`
- `_knowledge/projects/tenchu.md`

Repository root: `I:\Projects\PSX-Ports`.
