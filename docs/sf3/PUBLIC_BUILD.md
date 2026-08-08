# Public local-build bootstrap

The public deliverable is a source/tooling bootstrap, not a pre-generated game
binary. `SF3-Recompiled-Bootstrap-<version>-win64.zip` contains the exact
PSXRecomp CLI/runtime, PCSX-Redux OpenBIOS with its MIT notice, and source-owned
SCUS-94640 configuration. It contains no retail executable, disc sector,
generated game C, overlay capture, save, card, screenshot, movie, or audio.

`SETUP.cmd` is the supported player entry point. It verifies the complete
bootstrap manifest, discovers compatible tools or downloads hash-pinned
portable Python and WinLibs GCC/CMake/Ninja archives into the extracted kit,
then invokes `Build-SF3.ps1` with explicit tool paths. WinGet, Git, pip, Visual
Studio and system-wide installation are not required. The build generates into
a new private directory, verifies the extracted `SCUS_946.40` SHA-256, applies
the accepted compatibility and presentation profile, regenerates retail code
locally, builds an ordinary Release executable, and writes `PLAY_SF3.cmd`.
Generated sources and binaries remain private and are never copied back into
the public package. `BUILD_SF3.cmd` remains the advanced manual path.

Maintainers build the audited package with:

```powershell
$env:PYTHONUTF8 = '1'
python tools\build_cli.py release
powershell -ExecutionPolicy Bypass -File tools\package_sf3_bootstrap.ps1 `
  -Version v0.2.3-alpha
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

## v0.2.3 qualification receipt

The exact `SF3-Recompiled-Bootstrap-v0.2.3-alpha-win64.zip` was extracted into
a fresh directory. With normal tool discovery disabled, setup downloaded and
verified the pinned portable WinLibs 16.1.0 and Python 3.13.14 archives, reused
that verified closure on the build invocation, hash-gated the owned USA retail
executable, regenerated the accepted profile and completed the private Release
build with four jobs. The first complete setup took about 15 minutes on the
qualification machine.

- public ZIP SHA-256:
  `CA42EF902BB118980FCBA66F3092E32B254989661C5FDDDD6CACB4B0F90BEDA2`;
- private qualification executable SHA-256:
  `CA136374F56CE15F81FD26DA192CA97410105739BF1968B6E499500317A63B72`;
- archive audit: 909 entries, zero traversal paths and zero retail/save
  payload matches;
- setup contract: six behavioral/policy tests pass;
- generated config: SCUS-94640, 16:9, PGXP geometry and perspective enabled,
  precise culling enabled, native overlay promotion disabled; and
- the generated `PLAY_SF3.cmd` is ASCII+CRLF and the resulting executable
  remained responsive during a 12-second hidden, dummy-audio OpenGL smoke.
