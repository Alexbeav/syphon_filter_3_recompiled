# SF3 Redux profiles

`settings-4x.toml` enables the already-tested generic OpenGL 4x internal
supersampling path. `keybinds.ini` maps a conventional keyboard layout onto
retail PAD bits. `game-controller.toml` is the SCUS-94640-only fragment merged
into an isolated generated `game.toml` before regeneration; it enables the
exact-word-guarded direct camera bridge. The profile deliberately keeps 4:3
presentation and interpolation off until their SF3-specific gates pass.

`settings-compat.toml` is the runtime A/B profile: it selects 1x 4:3 and turns
the direct mouse camera off without changing generated code. `settings-4x.toml`
turns it on and persists all four sensitivity axes plus Y inversion. These
settings remain hand-editable until the launcher grows dedicated camera rows.

These are source templates, not retail data. Copy them into an isolated
generated build; do not place SCUS-94640, disc images, BIOS images, memory
cards, traces, captures or generated retail code in this directory or Git.
