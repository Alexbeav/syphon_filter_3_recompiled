from pathlib import Path


root = Path(__file__).resolve().parents[2]
gpu = (root / "runtime/src/gpu.c").read_text(encoding="utf-8")
render = (root / "runtime/src/gpu_render.c").read_text(encoding="utf-8")
gl = (root / "runtime/src/gpu_gl_renderer.c").read_text(encoding="utf-8")
main = (root / "runtime/src/main.cpp").read_text(encoding="utf-8")
loader = (root / "recompiler/src/config_loader.cpp").read_text(encoding="utf-8")

# Packed screen coordinates are values, not identities. Both fractional XY
# and depth must use the exact packet address/generation store.
precision_body = gpu.split("static void prepare_precision_triangle", 1)[1]
precision_body = precision_body.split("/* Write a single pixel", 1)[0]
assert "gte_geometry_correction_lookup" not in precision_body
assert "gp0_cmd_source_addr" in precision_body
assert "indices[i] * 4u" in precision_body
assert "gte_precision_load_word" in precision_body
assert "s_precision_triangle_unmatched++" in precision_body
assert "gr_set_precise_triangle(0" in precision_body
assert "gr_set_perspective_triangle(0" in precision_body

# The renderer-neutral boundary must reach software and OpenGL.
for token in (".set_precise_triangle", ".set_perspective_triangle"):
    assert token in render
    assert token in gl
assert "layout(location=9) in float a_q" in gl
assert "s_precise_x16[i]" in gl
assert "s_perspective_q[i]" in gl

# Both features default off and require an explicit profile.
for token in ("geometry_precision", "perspective_textures"):
    assert f'video.contains("{token}")' in loader
assert "g_geometry_precision = 0" in main
assert "g_perspective_textures = 0" in main
assert "gpu_geometry_correction_set(g_geometry_precision)" in main
assert "gpu_texture_correction_set(g_perspective_textures)" in main

print("PGXP precision provenance contract: OK")
