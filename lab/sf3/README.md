# Local SF3 recompilation artifacts

Only `reference-manifest.toml` is tracked here. Put user-owned inputs,
generated projects, runtime overlay captures and traces beneath ignored local
subdirectories. Never commit their contents.

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
