# SF3 recompilation bring-up

## 2026-08-03 — isolated feasibility baseline

The lab was cloned with `--no-hardlinks` from clean tracked SF2 feasibility
commit `4f811c2` and switched to branch
`experiment/sf3-recomp-feasibility`. The local clone remote was removed;
upstream is fetch-only with push URL `DISABLED`. Initial tracked working-tree
footprint is 0.073 GiB versus 5.4 GiB in the source workspace including its
ignored build/capture state, proving those local artifacts did not transfer.

SF2-specific instructions, manifests and reports were removed. Generic
framework corrections and their source-owned regressions remain in history.
SCUS-94640 is the only game target on this branch.

### Initial corpus consultation

The private corpus, SF2 recomp report and SF3 hybrid report were consulted
before implementation.

| Lead | Initial disposition | First SF3 check |
| --- | --- | --- |
| `PSX-CPU-002` load delay | framework correction retained; SF3 applicability unproven | complete framework regression, then observe any SF3 first divergence |
| `PSX-CPU-003` encoded JALR | framework correction retained; SF3 consumer unproven | measure dirty-RAM JALR forms before attribution |
| `PSX-IRQ-001` nested-call IRQ | framework correction retained; SF3 consumer unproven | require an actual in-call event wait before calling it confirmed |
| `PSX-GPU-001` persistent pages | strong SF3 presentation lead | compare draw/display pages and complete same-tick submissions |
| `PSX-GPU-002` CPU/FBO coherence | not yet applicable | test only if an SF3 24-bit presentation symptom appears |
| `PSX-HLE-001` wrapper mirrors | hybrid-proven, but recomp path uses LLE OpenBIOS | verify whether authentic wrappers eliminate the HLE-specific failure |
| `PSX-MEM-001` alias safety | relevant lifecycle contract | inspect actual runtime stack/range allocation; do not import hybrid stack |
| `PSX-VAL-002` pre-fetch stop | diagnostic contract adopted | report stop reason/fetch status and read RAM before invalid-code diagnosis |

Independent validator named for generic CPU/IRQ results: Tenchu. Independent
validator for GPU page/composition results: SF2 hybrid.

### Framework baseline and retail identity

- Initialized `lib/recomp-net` at pinned commit
  `01b648e4acc26c8e229b5b0451618aeac24b7444`.
- Built the redistributable CLI in Release mode with GCC 16.1.0 and packaged
  `dist/psxrecomp-cli-windows-x86_64.zip`.
- The first direct `ctest` invocation inherited the host's Greek CP1253 Python
  locale. Three Python-driven tests failed while decoding child-process/source
  bytes, before their intended assertions could complete. Repeating the same
  suite with `PYTHONUTF8=1` passed all 40/40 tests in 2.86 seconds. This is
  classified as a narrowed host test-environment invariant, not a CPU/runtime
  regression; subsequent scripted test gates must pin UTF-8 mode.
- Read-only `sf_tool inspect` independently identified the user-owned disc as
  volume `SCUS94640`, executable `SCUS_946.40`, executable SHA-256
  `b4b32cc92e6b8634762893b637bc9a471442edbeb7569afcfb18eafbe82b9460`,
  entry `0x800FB368`, text address `0x80010000`, and text size `0x001CC000`.
- The disc image SHA-256 is
  `2c36429649e50036fd5c9187bdc3ff23e04039499e7cdf1aba5cfd5a3badcb38`;
  tracked OpenBIOS SHA-256 is
  `fabe498fbf224e4721f12f31b6f5fe0659205e341dc4e5c5f91b9bd1a1011c57`.

### Deterministic generation and clean Release builds

- Two independent CLI invocations generated 1,128 files each from the same
  gated retail disc and OpenBIOS inputs.
- Narrow root-path normalization found 1,128/1,128 files identical, no
  one-sided or differing paths, and tree SHA-256
  `09043b8c29b5c34a0364d0fd36778fa7002ef14d29128938a60b272bf915433e`.
- Generation discovered 3,450 static retail functions, 54,265 basic blocks,
  and 199 alias entries. These are generation facts, not proof that every
  emitted address is executable code; the generator also reported reserved
  opcode candidates in executable-range data and those warnings remain open
  until runtime reachability distinguishes relevant code from false seeds.
- Both clean generated trees built in Release mode. Each product is
  97,722,767 bytes. Raw binaries differ by exactly eight bytes: PE timestamp,
  PE checksum, and one embedded build timestamp. After normalizing only those
  fields, both products have SHA-256
  `a23b0071a7e8ae94746e1e0080a0e4cf4c43c62648724ddc8367842911ac683d`.
- Current repository footprint including both ignored generated trees and
  their clean builds is 1.662 GiB, below the 20 GiB cap.
