# SF3 campaign qualification matrix

Updated: 2026-08-05

This ledger bounds the current `SCUS-94640` campaign claim. A mission row is
qualified only through connected retail progression from the preceding mission.
Direct mission boot, archive construction, overlay capture, state forcing and a
rendered first frame do not qualify entry, completion or an adjacent transition.

Evidence levels are deliberately distinct:

- `pass-2x+human`: two clean bounded ordinary Release runs and a visible human
  run cover the named gate;
- `pass-human`: connected visible retail play covers the gate, but it has no
  two-run deterministic qualification;
- `entry-human`: connected visible play reached the mission, with no broader
  gameplay or completion claim;
- `open`: no qualifying evidence;
- `n/a`: the gate does not apply to that row.

Every future promotion must bind the executable/configuration identity, input
artifact, starting and ending card hashes, application transition sequence,
dispatch ownership, GPU/display pages, SPU/XA/CD activity and terminal reason.
Automated milestones require two clean processes. Visible presentation and
control remain human gates after automation passes.

<!-- campaign-matrix:start -->
| # | Retail mission | Resource | Entry | Gameplay | Death/checkpoint | Completion | Outbound retail seam | Save/load | Automation |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | Hotel Fukushima | `TOKYO` | pass-2x+human | pass-2x+human | pass-2x+human | pass-2x+human | pass-2x+human (`1 -> 2`) | pass-2x+human (new-card save) | complete 42,480-sample route twice |
| 2 | Costa Rican Plantation | `JUNGLE` | pass-2x+human | pass-human | open | pass-human | pass-human (`2 -> 3`) | open | entry only in the qualified route |
| 3 | C-5 Galaxy Transport | `JUNGLE3` | pass-human | pass-human | open | pass-human | pass-human (`3 -> 4`) | open | open |
| 4 | Pugari Gold Mine | `AFRICA1` | entry-human | open | open | open | open (`4 -> 5`) | open | open |
| 5 | Pugari Complex | `AFRICA2` | open | open | open | open | open (`5 -> 6`) | open | open |
| 6 | Kabul, Afghanistan | `AFGHAN2` | open | open | open | open | open (`6 -> 7`) | open | open |
| 7 | S.S. Lorelei | `LONDON1` | open | open | open | open | open (`7 -> 8`) | open | open |
| 8 | Aztec Ruins | `JUNGLE2` | open | open | open | open | open (`8 -> 9`) | open | open |
| 9 | Waterfront | `LONDON2` | open | open | open | open | open (`9 -> 10`) | open | open |
| 10 | Docks Final Assault | `LONDON3` | open | open | open | open | open (`10 -> 11`) | open | open |
| 11 | Convoy | `AFGHAN1` | open | open | open | open | open (`11 -> 12`) | open | open |
| 12 | The Beast | `AFGHAN3` | open | open | open | open | open (`12 -> 13`) | open | open |
| 13 | Australian Outback | `TRIAGE1` | open | open | open | open | open (`13 -> 14`) | open | open |
| 14 | St. George Australia | `TRIAGE2` | open | open | open | open | open (`14 -> 15`) | open | open |
| 15 | Paradise Ridge | `RIDGE` | open | open | open | open | open (`15 -> 16`) | open | open |
| 16 | Militia Compound | `SNOWCAMP` | open | open | open | open | open (`16 -> 17`) | open | open |
| 17 | Underground Bunker | `MCAVES` | open | open | open | open | open (`17 -> 18`) | open | open |
| 18 | Senate Building | `SENATE` | open | open | open | open | open (`18 -> 19`) | open | open |
| 19 | DC Subway | `SENATE2` | open | open | open | open | open (final result/credits/title) | open | open |
<!-- campaign-matrix:end -->

## Current evidence boundary

Mission 1 owns the only complete deterministic representative slice. Its two
ordinary replays cover cold boot, retail frontend selection, briefing, authored
gameplay, death, checkpoint reload, completion, result/FMVs, new-card flow and
the Mission 2 handoff. A passive diagnostic run agrees at the named semantic
gates while retaining separate observer ownership.

The connected visible 4x session then completed Missions 2 and 3 and reached
Mission 4. That is valid human breadth evidence, including the `2 -> 3` and
`3 -> 4` retail seams, but it is not deterministic qualification. Mission 4
completion is explicitly open. The retained long human input witness is not
promoted to deterministic campaign evidence because `PSXPAD2` records retail
PAD samples, while the accepted direct-camera bridge consumes separate host
relative-mouse motion.

## Next gate

The next campaign checkpoint is a connected Mission 4 continuation through the
retail `4 -> 5` seam. Before asking for a visible run:

1. preserve the accepted Mission 4 card as an immutable source and copy it into
   two isolated writable directories;
2. bind both runs to the exact ordinary executable and 4:3 compatibility
   profile first;
3. record bounded semantic/device/dispatch summaries without forcing input or
   application state;
4. require matching entry, checkpoint/restart (if exercised), completion and
   outbound transition evidence from two clean processes; and
5. only then repeat visibly with the 16:9 presentation profile.

SF2 Recomp is the independent validator for the adjacent-transition and
two-process evidence contract. No SF2 address, mission state or overlay identity
is transferable to this matrix.
