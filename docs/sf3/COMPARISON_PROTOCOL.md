# SF3 hybrid-versus-recompilation comparison protocol

## Fixed semantic boundaries

1. Executable entry and CRT completion.
2. First `Game_Main`/application-loop iteration.
3. Stable TITLE state `4/2`.
4. Retail Story/Mission 1 acceptance and TOKYO request.
5. State-8 loading/briefing.
6. First state-0 authored gameplay frame.
7. Player-control handoff with authoritative state movement.
8. Pause, death/restart and checkpoint.

## Record at every point

- commits and exact input identities;
- PC, SP, GP, RA, COP0 and application state/depth;
- stable selected-RAM hashes;
- active image identities/load ranges/hashes/generations;
- static, native-overlay and interpreter dispatch counts;
- GPU submissions, draw/display page and presentation hash;
- SPU/XA/CD/device clocks and rejection counters;
- exact deterministic input artifact;
- warnings, unsupported paths, wall/CPU time and peak memory.

Run twice from clean processes. Normalize only explicitly host-variant fields.
Rendering or accepted input is not player ownership; prove retail player state
changes under the recorded input.

The hybrid is a read-only oracle. Count every title-specific rule and report
fallback honestly. Compare only the retail-compatible profile.
