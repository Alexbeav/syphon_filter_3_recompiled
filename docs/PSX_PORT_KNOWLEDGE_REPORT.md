# PSX port knowledge report — SF3 recompilation feasibility lab

- Date: 2026-08-03
- Branch: `experiment/sf3-recomp-feasibility`
- Framework lineage: SF2 lab `4f811c2`; PSXRecomp
  `0cfa9fe0a8da944e9f694a24361b4973c57131ea`
- Target: USA `SCUS-94640`
- Lane: PolyForm Noncommercial static/captured-overlay feasibility experiment

## Current state

Repository scaffold and corpus consultation established. Deterministic
generation and retail execution are pending.

## Consumed leads

Generic load-delay, encoded-JALR and nested-call IRQ corrections are retained
with their source regressions, but SF3 has not yet independently exercised
those failure modes. Persistent display pages, caller-qualified capture and
complete same-tick composition are active presentation leads.

## Next decisive experiment

Generate the SCUS-94640 project twice, build both, then boot OpenBIOS to stable
retail TITLE twice while measuring overlay and fallback ownership. Any first
divergence enters the mandatory consult-test-return loop.

## Provenance

No retail input, executable, generated C, overlay capture, RAM/state, card or
media payload is tracked. Oracle projects are read-only. Reusable findings will
be normalized into the private corpus only after a committed project result.
