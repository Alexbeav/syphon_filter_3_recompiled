# Local SF3 recompilation artifacts

Only the reference manifest and source-only probes are tracked here. Put
user-owned inputs, generated projects, runtime overlay captures and traces
beneath ignored local subdirectories. Never commit their contents.

## Reproduction gate

Run PowerShell from the repository root. Replace `$Sf3Cue` only with a
user-owned USA SCUS-94640 cue. Both output directories must be absent before
the run.

```powershell
$env:PYTHONUTF8 = '1'
$Sf3Cue = 'C:\path\to\your\Syphon Filter 3 (USA).cue'
python tools\build_cli.py release
ctest --test-dir recompiler\build-cli --output-on-failure
& .\dist\psxrecomp-cli-windows-x86_64\psxrecomp.exe build --disc $Sf3Cue --bios .\bios\openbios.bin --output .\lab\sf3\generated\run-a --name 'Syphon Filter 3'
& .\dist\psxrecomp-cli-windows-x86_64\psxrecomp.exe build --disc $Sf3Cue --bios .\bios\openbios.bin --output .\lab\sf3\generated\run-b --name 'Syphon Filter 3'
python .\lab\sf3\configure_compatibility.py .\lab\sf3\generated\run-a
python .\lab\sf3\configure_compatibility.py .\lab\sf3\generated\run-b
$GameRecompiler = (Resolve-Path .\dist\psxrecomp-cli-windows-x86_64\libexec\psxrecomp-game.exe).Path
Push-Location .\lab\sf3\generated\run-a; & $GameRecompiler --config game.toml; Pop-Location
Push-Location .\lab\sf3\generated\run-b; & $GameRecompiler --config game.toml; Pop-Location
python tools\compare_generated_projects.py .\lab\sf3\generated\run-a .\lab\sf3\generated\run-b
& .\lab\sf3\generated\run-a\build.ps1
& .\lab\sf3\generated\run-b\build.ps1
python tools\compare_generated_projects.py .\lab\sf3\generated\run-a .\lab\sf3\generated\run-b --pe-product build/Syphon_Filter_3_Recompiled.exe
```

The retail executable, generated sources, builds, traces and captures are
ignored and must remain local.

For a launcher-owned enhancement build, apply `--launcher-mods` instead of a
fixed widescreen/PGXP profile. This installs the payload-free built-in catalog,
links the trusted SF3 plugin and enables recomp-ui; configure CMake with the
game project's pinned `recomp-ui` checkout (or `RECOMP_UI_ROOT`). Widescreen,
Mouse Look and PGXP all default off. PGXP exposes geometry-only and full
geometry-plus-perspective choices inside one feature so mutually conflicting
modes cannot be enabled together.

The compatibility configurator disables native execution of runtime-installed
overlays for SF3. Visible testing proved the current compiled Mission 1 overlay
can return invalid geometry ownership while the same retail route succeeds
with interpreter ownership. Capture remains enabled for audit and future
promotion after native/interpreter equivalence is proved.

The same deterministic post-generation step selects 4x internal
supersampling and installs `lab/sf3/keybinds.ini` beside every Release product.
That tracked keyboard profile matches the SF2 recompilation project. These are
presentation/input defaults only and do not enable widescreen or native
runtime-overlay execution. The explicit second `psxrecomp-game` pass emits the
exact-word-guarded SCUS-94640 direct-camera hook from the configured title
profile; generated retail C remains ignored and is never hand-edited.

## Hidden-renderer Story/Mission 1 probe

After creating the Release-optimized diagnostic build (`build-r1`) and
publishing the captured overlay cache as described in the devlog, run:

```powershell
$env:PYTHONUTF8 = '1'
python .\lab\sf3\probe_story.py $Sf3Cue --out .\lab\sf3\traces\clean-story-a --port 4388
python .\lab\sf3\probe_story.py $Sf3Cue --out .\lab\sf3\traces\clean-story-b --port 4388
```

Each output directory must not already exist. The probe creates an SDL/OpenGL
window in hidden state and selects SDL's dummy audio driver, exercising the
hardware presentation path without a visible window or sound device. It waits
for SCEA and the full pre-menu cemetery intro to complete and the retail TITLE
stream/menu to begin before supplying only
active-low physical PAD words through SIO. Accepted edges are released
immediately so input cannot bleed into the next movie state. It records bounded
JSON/screenshots beneath the ignored output directory and exits only after
state `0/1`, Mission 1 PAD polling and a movement sample. It never writes guest
RAM, invokes a retail callback or patches generated code.

The diagnostic display ring is CPU-VRAM-nonmutating, not timing-transparent:
OpenGL capture still flushes and reads back the visible display. Full 1024×512
VRAM capture is disabled by default; add `--display-ring-aux` only when a
same-frame texture/CLUT dump is required. During the initial Mission 1 control
window the probe scans retained BGR555 displays for the user's observed
red/checkered failure signature (at least 15% red-dominant and 5% hot-red
pixels by default). Those thresholds distinguish the supplied corrupt capture
from the clean captures by a wide margin, but are a symptom-specific alarm,
not proof that arbitrary presentation is correct.

## Human route capture

The source-owned `record_input_route.ps1` helper records the two normalized PSX
pad packets at the retail SIO sampling boundary. It does not record retail data,
frames, audio or host key names. The route carries a content-derived runtime and
generated-image compatibility ID, so a changed build rejects it rather than
silently consuming stale input.

```powershell
.\lab\sf3\record_input_route.ps1 `
  -Project .\lab\sf3\generated\input-route-m `
  -Route .\lab\sf3\traces\human-mission1.psxpad `
  -Renderer opengl
```

Use `-Silent` to select SDL's dummy audio driver. Release all controls before
closing the window so the finalized route has a neutral trailing sample. A
`.partial` recovery file is refreshed every 3,600 guest samples; the final file
is written during orderly shutdown. This is a diagnostic input witness, not by
itself proof of deterministic state, correct rendering or campaign completion.
Use `-Unique` for repeated human attempts; it appends a timestamp before the
extension and still refuses to overwrite any existing final or partial route.
The connected human checklist is [MISSION1_ACCEPTANCE.md](../../docs/sf3/MISSION1_ACCEPTANCE.md).

The desktop has two distinct entry points targeting the same compatible
`input-route-m` ordinary Release: **Syphon Filter 3 Recomp Lab** for an ordinary
visible run, and **Syphon Filter 3 Recomp - Record Mission 1** for a timestamped
input witness. Neither shortcut enables diagnostic TCP tooling or modifies
retail state.

After the route is finalized, two ordinary Release replays can exercise the
same hidden renderer and stop at the exact recorded retail-SIO sample count:

```powershell
.\lab\sf3\replay_input_route.ps1 `
  -Project .\lab\sf3\generated\input-route-m `
  -Route .\lab\sf3\traces\human-mission1.psxpad `
  -Out .\lab\sf3\traces\human-mission1-replay-a `
  -Renderer opengl
.\lab\sf3\replay_input_route.ps1 `
  -Project .\lab\sf3\generated\input-route-m `
  -Route .\lab\sf3\traces\human-mission1.psxpad `
  -Out .\lab\sf3\traces\human-mission1-replay-b `
  -Renderer opengl
```

The helper always selects SDL dummy audio, uses an isolated memory-card
directory and refuses to reuse an output directory. `--hidden-window` keeps the
selected renderer active; it is not renderer-less `--headless`. Successful
process exit proves only that every recorded sample was consumed. State,
presentation and campaign gates still require the diagnostic observer and the
ordinary visible confirmation described in the objective.

For a diagnostic replay, `observe_input_route.py` consumes the same route
without injecting TCP input. It records retail application transitions,
periodic GPU/SPU/audio/CD/PAD/dispatch state, and BGR555 display statistics with
the framebuffer display origin. If the observed red/checkered signature occurs,
the first retained display frame is dumped immediately. Add
`--display-ring-aux` only when the extra same-frame 1024×512 VRAM evidence is
needed.

Focused presentation work can stop at an exact retail-PAD sample with
`--stop-after N` and request authoritative display captures with repeatable
`--capture-frame N` or `--capture-frame-range START:END`. Use
`--capture-frame-step N` to bound dense ranges. OpenGL captures are read from
the authoritative FBO; software captures use its CPU-owned VRAM. Missing
requested frames are reported in `evidence.json` rather than silently ignored.
Each requested frame also retains a bounded GP0 command ring. Run
`analyze_gp0_primitives.py` on the resulting evidence to flag polygon packet
length mismatches, extreme decoded vertex spans, PS1 edge-limit rejection and
the partial-quad risk where triangle-local rejection would draw half of a
hardware-rejected command.

```powershell
python .\lab\sf3\observe_input_route.py `
  'Z:\Emulators\PS1 Games\Syphon Filter 3 (USA).cue' `
  .\lab\sf3\traces\human-mission1.psxpad `
  --project .\lab\sf3\generated\input-route-m `
  --out .\lab\sf3\traces\human-mission1-observed-a `
  --renderer opengl `
  --stop-after 3000 `
  --capture-frame-range 2169:2300 `
  --capture-frame-step 10

python .\lab\sf3\analyze_gp0_primitives.py `
  .\lab\sf3\traces\human-mission1-observed-a\evidence.json `
  --output .\lab\sf3\traces\human-mission1-observed-a\gp0-analysis.json
```

This diagnostic route is intentionally timing-perturbing. Acceptance still
requires the ordinary Release replays with the observer absent.

Compare two completed diagnostic observations with the bounded semantic
classifier:

```powershell
python .\lab\sf3\compare_route_evidence.py `
  .\lab\sf3\traces\human-mission1-observed-a\evidence.json `
  .\lab\sf3\traces\human-mission1-observed-b\evidence.json `
  --out .\lab\sf3\traces\human-mission1-observed-compare.json
```

The comparator requires matching retail application-transition sequences, a
following retail transition, two display origins in each state-0 run, live
subsystem snapshots, exact bounded-route consumption and no match for the known
corruption signature. It deliberately does not claim general texture
correctness, audio quality, pause/death/checkpoint behavior or Mission 1
completion; those remain explicit human and ordinary-Release gates.
