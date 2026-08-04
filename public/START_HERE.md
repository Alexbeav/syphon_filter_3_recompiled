# Syphon Filter 3 Recompiled — local build bootstrap

This noncommercial package contains PSXRecomp, the redistributable PCSX-Redux
OpenBIOS, and source-owned SF3 configuration. It contains **no Syphon Filter 3
executable, disc data, generated game code, saves, or other retail assets**.

## Requirements

- Windows 10/11 x64;
- your legally obtained *Syphon Filter 3* USA `SCUS-94640` BIN/CUE dump;
- Python 3, CMake, Ninja, and a C/C++ compiler available on `PATH`;
- enough free space for a private generated project and Release build.

Keep every BIN track beside its CUE file. Double-click `BUILD_SF3.cmd`, accept
the PolyForm Noncommercial license when prompted, select/type the CUE path, and
choose a new private output directory. Generation and compilation can take
several minutes.

The bootstrap verifies the extracted retail executable against the supported
SHA-256 before applying the accepted 4×, widescreen, mouse and keyboard profile.
It does not launch the game automatically. The final executable path is printed
when compilation completes.

The generated directory and executable contain retail-derived code. Keep them
private; do not upload or redistribute them. The bootstrap package itself is
the redistributable artifact.
