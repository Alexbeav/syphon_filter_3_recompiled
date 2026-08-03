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
python tools\compare_generated_projects.py .\lab\sf3\generated\run-a .\lab\sf3\generated\run-b
& .\lab\sf3\generated\run-a\build.ps1
& .\lab\sf3\generated\run-b\build.ps1
python tools\compare_generated_projects.py .\lab\sf3\generated\run-a .\lab\sf3\generated\run-b --pe-product build/Syphon_Filter_3_Recompiled.exe
```

The retail executable, generated sources, builds, traces and captures are
ignored and must remain local.

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
  -Project .\lab\sf3\generated\input-route-e `
  -Route .\lab\sf3\traces\human-mission1.psxpad
```

Use `-Silent` to select SDL's dummy audio driver. Release all controls before
closing the window so the finalized route has a neutral trailing sample. A
`.partial` recovery file is refreshed every 3,600 guest samples; the final file
is written during orderly shutdown. This is a diagnostic input witness, not by
itself proof of deterministic state, correct rendering or campaign completion.
