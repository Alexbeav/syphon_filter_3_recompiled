# Public local-build bootstrap

The public deliverable is a source/tooling bootstrap, not a pre-generated game
binary. `SF3-Recompiled-Bootstrap-<version>-win64.zip` contains the exact
PSXRecomp CLI/runtime, PCSX-Redux OpenBIOS with its MIT notice, and source-owned
SCUS-94640 configuration. It contains no retail executable, disc sector,
generated game C, overlay capture, save, card, screenshot, movie, or audio.

`BUILD_SF3.cmd` invokes `Build-SF3.ps1`. Before reading owned input, the script
verifies the complete bootstrap manifest. It then generates into a new private
directory, verifies the extracted `SCUS_946.40` SHA-256, applies the accepted
compatibility and presentation profile, regenerates retail code locally, and
builds an ordinary Release executable. Generated sources and binaries remain
private and are never copied back into the public package.

Maintainers build the audited package with:

```powershell
$env:PYTHONUTF8 = '1'
python tools\build_cli.py release
powershell -ExecutionPolicy Bypass -File tools\package_sf3_bootstrap.ps1 `
  -Version v0.2.2-alpha
```

The package test checks every declared path, size and SHA-256 and rejects extra
files. The packager additionally rejects retail-media extensions, SCUS payloads,
overlay/capture/report/card names, and generated/private directory boundaries.

The supported enhanced profile is 4× OpenGL at 16:9 with PGXP precise geometry,
perspective textures, exact-FIFO precise culling, the human-accepted SF3
mouse/keyboard mapping and full-width cinematic mattes. A 4× 4:3 compatibility
profile is also available from the PowerShell entry point. Minor residual
texture wobble and model seams remain, HUD relocation is still low-priority
presentation debt, and campaign validation beyond arrival in Mission 4 remains
incomplete.
