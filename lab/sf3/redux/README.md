# SF3 Redux profiles

`settings-4x.toml` enables the already-tested generic OpenGL 4x internal
supersampling path. `keybinds.ini` maps a conventional keyboard layout onto
retail PAD bits. `game-controller.toml` is the SCUS-94640-only fragment merged
into an isolated generated `game.toml` before regeneration; it enables the
exact-word-guarded direct camera bridge. The accepted 4x profile remains the
4:3 control; widescreen is a separate profile and interpolation remains off.

`settings-compat.toml` is the runtime A/B profile: it selects 1x 4:3 and turns
the direct mouse camera off without changing generated code. `settings-4x.toml`
turns it on and persists all four sensitivity axes plus Y inversion. These
settings remain hand-editable until the launcher grows dedicated camera rows.

`settings-wide.toml` is the isolated 4x/16:9 acceptance profile. Generate its
candidate with `configure_compatibility.py <project> --widescreen
--output-config game-wide.toml`; this enables
the separate native-wide surface, GTE activity classification, one full-mirror
raster path, HUD corner anchoring and the generic screen-cull detector. The
detector emits zero SCUS-94640 sites. A passive Mission 1 census instead proves
one dense world DMA list (483..925 polygon commands) separated from auxiliary
lists (1..21); the profile enables guest-wide projection and restores retail
proportions only for lists containing at least 64 polygons. It does not install
an SF2 address or force a cull result. Use `settings-4x.toml` beside
the same executable as the 4:3 control so code-generation drift cannot masquerade
as an aspect difference.

These are source templates, not retail data. Copy them into an isolated
generated build; do not place SCUS-94640, disc images, BIOS images, memory
cards, traces, captures or generated retail code in this directory or Git.
