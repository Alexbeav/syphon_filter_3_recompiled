from pathlib import Path


root = Path(__file__).resolve().parents[2]
gpu = (root / "runtime/src/gpu.c").read_text(encoding="utf-8")
gte = (root / "runtime/src/gte.cpp").read_text(encoding="utf-8")
render = (root / "runtime/src/gpu_render.c").read_text(encoding="utf-8")
gl = (root / "runtime/src/gpu_gl_renderer.c").read_text(encoding="utf-8")
main = (root / "runtime/src/main.cpp").read_text(encoding="utf-8")
loader = (root / "recompiler/src/config_loader.cpp").read_text(encoding="utf-8")
codegen = (root / "recompiler/src/code_generator.cpp").read_text(encoding="utf-8")
strict = (root / "recompiler/src/strict_translator.cpp").read_text(encoding="utf-8")
dirty = (root / "runtime/src/dirty_ram_interp.c").read_text(encoding="utf-8")
interp = (root / "runtime/src/psx_interpreter.c").read_text(encoding="utf-8")

# Packed screen coordinates are values, not identities. Both fractional XY
# and depth must use the exact packet address/generation store.
precision_body = gpu.split("static void prepare_precision_triangle", 1)[1]
precision_body = precision_body.split("/* Write a single pixel", 1)[0]
assert "gte_geometry_correction_lookup" not in precision_body
assert "gp0_cmd_source_addr" in precision_body
assert "indices[i] * 4u" in precision_body
assert "s_precision_triangle_unmatched++" in precision_body
assert "gte_precision_query_word" in precision_body
for reason in (
    "missing_vertices",
    "stale_vertices",
    "address_mismatch_vertices",
    "packed_mismatch_vertices",
    "invalid_vertices",
):
    assert f"s_precision_stats.{reason}++" in precision_body
assert "gr_set_precise_triangle(0" in precision_body
assert "gr_set_perspective_triangle(0" in precision_body

# A failed lookup must retain its exact owner instead of collapsing every
# moving-model miss into one aggregate counter.
for status in (
    "GTE_PRECISION_MISSING",
    "GTE_PRECISION_STALE",
    "GTE_PRECISION_ADDRESS_MISMATCH",
    "GTE_PRECISION_PACKED_MISMATCH",
    "GTE_PRECISION_INVALID",
):
    assert f"return {status}" in gte

# Projected vertices commonly cross MFC2->GPR->SW and packet-copy LW->GPR->SW
# paths. Every tier must transport exact source identity and invalidate ordinary
# GPR writes; rounded packed values alone are never sufficient provenance.
for token in (
    "gte_precision_gpr_invalidate",
    "gte_precision_gpr_from_gte",
    "gte_precision_gpr_load_word",
    "gte_precision_store_gpr",
):
    assert token in gte
    assert token in codegen
for text in (strict, dirty, interp):
    assert "gte_precision_gpr_invalidate" in text
    assert "gte_precision_gpr_from_gte" in text
    assert "gte_precision_store_gpr" in text
assert "projection.packed != packed" in gte
assert "gte_precision_query_word(addr, packed" in gte
assert "latest_missing_addr = addr" in gpu
assert "latest_missing_addr" in (root / "runtime/src/debug_server.c").read_text(encoding="utf-8")

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
