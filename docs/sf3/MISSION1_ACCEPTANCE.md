# SCUS-94640 Mission 1 representative-slice capture

This is the human gate for moving SF3 recomp beyond `bootstrap_verified`.
Rendering the first room or accepting movement is not sufficient. Use the
desktop shortcut **Syphon Filter 3 Recomp - Record Mission 1** only when a full
connected attempt is practical.

The shortcut creates a timestamped ignored route such as
`lab/sf3/traces/human-mission1-20260803-120000.psxpad`. It never overwrites an
earlier success or failure. The route contains normalized controller packets,
not video, audio, retail code or host key names.

## Connected route

1. Begin from the cold OpenBIOS boot and use the retail frontend to select
   Story and Mission 1. Do not load a developer state or bypass the briefing.
2. Confirm the cemetery/title and Tokyo FMVs present correctly. Note any skipped
   movie, colored band, broken frame or audio failure.
3. Accept the Mission 1 briefing normally. If gameplay does not begin, release
   every control for several seconds, close the window normally and retain the
   timestamped failed route.
4. In gameplay, inspect both camera directions and several rooms for the known
   red/checkered surfaces, wrong palettes, missing textures or stale page data.
5. Exercise keyboard/controller movement, aiming/camera, weapons and interaction.
   Pause and resume once while dialogue, music and effects are active.
6. Take damage and deliberately die once. Use the retail restart flow and
   confirm control, rendering and audio recover.
7. After reaching a checkpoint, deliberately fail or restart and confirm the
   retail checkpoint restore returns to the authored location with live input,
   audio and correct presentation.
8. Complete Mission 1 and continue through its retail result/save flow until the
   following authored application transition is visibly established.
9. Release all controls for several seconds before closing the window normally.
   The shortcut keeps its console open after the game closes. It must report
   `Input route finalized`; otherwise preserve the `.partial` file and report
   how the process ended. Close the console after noting the route filename.

## Evidence to report

- Route filename and whether the attempt completed or failed.
- Whether briefing-to-gameplay succeeded.
- Whether both alternating framebuffer pages remained visually correct across
  multiple rooms.
- Input/camera, pause/resume, dialogue/music/effects status.
- Damage/death/restart and checkpoint-restore status.
- Mission completion and the following retail transition.
- The first visible symptom and approximate location if anything fails.

This human report is necessary but not sufficient. The same compatible route
must subsequently pass the passive diagnostic comparison and two clean ordinary
Release replays. Diagnostic color thresholds cover only the supplied
red/checkered symptom and cannot prove arbitrary texture correctness.
