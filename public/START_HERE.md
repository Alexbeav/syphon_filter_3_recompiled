# Syphon Filter 3 Recompiled — local build bootstrap

This noncommercial package contains PSXRecomp, the redistributable PCSX-Redux
OpenBIOS, and source-owned SF3 configuration. It contains **no Syphon Filter 3
executable, disc data, generated game code, saves, or other retail assets**.

## Requirements

- Windows 10/11 x64;
- your legally obtained *Syphon Filter 3* USA `SCUS-94640` BIN/CUE dump;
- an internet connection and approximately 6 GiB free.

That is all for the normal path. Keep every BIN track beside its CUE file and
place the CUE beside this README, then double-click `SETUP.cmd`. Setup discovers
compatible existing tools or downloads isolated, pinned, SHA-256-verified
Python and WinLibs archives into this folder. Nothing is installed system-wide;
WinGet, Git, pip, and Visual Studio are not required. Accept the PolyForm
Noncommercial license when prompted. The first build can take several minutes.

Setup writes `setup.log` for support and creates `PLAY_SF3.cmd` after a
successful build. Review and redact personal paths before sharing the log.
Advanced users can run `SETUP.ps1 -CuePath <file.cue>`, select a private output
with `-OutputDirectory`, cap compilation with `-BuildJobs 1..64`, or use
`-NoInstallDependencies` for a manual/offline preflight. `BUILD_SF3.cmd` remains
available as the manual developer entry point when tools are already installed.

The bootstrap verifies the extracted retail executable against the supported
SHA-256 before applying the accepted 4×, widescreen, PGXP precise-geometry,
precise-culling, mouse and keyboard profile. It does not launch the game
automatically. The final executable path is printed when compilation completes.

The generated directory and executable contain retail-derived code. Keep them
private; do not upload or redistribute them. The bootstrap package itself is
the redistributable artifact.
