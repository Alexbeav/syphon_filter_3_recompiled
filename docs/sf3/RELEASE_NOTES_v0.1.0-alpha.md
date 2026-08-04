# Syphon Filter 3 Recompiled v0.1.0-alpha

This is the first public, noncommercial local-build bootstrap for the USA
`SCUS-94640` release.

Included:

- authentic retail execution through PSXRecomp and bundled MIT OpenBIOS;
- 4x OpenGL rendering;
- native 16:9 world presentation and full-width cinematic mattes;
- keyboard controls, direct mouse camera/aim, mouse buttons and weapon wheel;
- a hash-pinned generator that compiles the private game executable locally.

The download contains no Syphon Filter 3 executable, disc data, generated game
code, saves, cards, screenshots, movies, audio, or other retail assets. Supply a
legally obtained USA BIN/CUE dump. The bootstrap verifies `SCUS_946.40` before
compilation. Generated sources and binaries must remain private.

Known limitations:

- HUD elements remain inset at their original 4:3 coordinates;
- human campaign validation currently reaches Mission 4, not the full campaign;
- local compilation requires Python 3, CMake, Ninja and a C/C++ compiler and can
  take several minutes.
