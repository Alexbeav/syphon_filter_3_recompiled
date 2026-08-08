#include "mod_enhancement_state.h"

#include <string.h>

static int valid_aspect(uint32_t numerator, uint32_t denominator) {
    return numerator != 0 && denominator != 0 &&
           numerator <= 99 && denominator <= 99 &&
           3u * numerator >= 4u * denominator &&
           9u * numerator <= 32u * denominator;
}

static PsxModEnhancementConfig identity_config(void) {
    PsxModEnhancementConfig config;
    memset(&config, 0, sizeof(config));
    config.aspect_num = 4;
    config.aspect_den = 3;
    config.adaptive_max_num = 16;
    config.adaptive_max_den = 9;
    return config;
}

void psx_mod_enhancement_initialize(
    PsxModEnhancementState *state,
    const PsxModEnhancementConfig *baseline) {
    if (!state) return;
    state->baseline = identity_config();
    if (baseline && valid_aspect(baseline->aspect_num, baseline->aspect_den)) {
        state->baseline = *baseline;
        state->baseline.geometry_precision =
            baseline->geometry_precision ? 1 : 0;
        state->baseline.perspective_textures =
            baseline->perspective_textures ? 1 : 0;
        state->baseline.mouse_camera = baseline->mouse_camera ? 1 : 0;
        state->baseline.adaptive_aspect = baseline->adaptive_aspect ? 1 : 0;
        if (!valid_aspect(state->baseline.adaptive_max_num,
                          state->baseline.adaptive_max_den)) {
            state->baseline.adaptive_aspect = 0;
            state->baseline.adaptive_max_num = 16;
            state->baseline.adaptive_max_den = 9;
        }
    }
    state->current = state->baseline;
}

void psx_mod_enhancement_reset(PsxModEnhancementState *state) {
    if (state) state->current = state->baseline;
}

int psx_mod_enhancement_set_fixed_aspect(
    PsxModEnhancementState *state, uint32_t numerator, uint32_t denominator) {
    if (!state || !valid_aspect(numerator, denominator)) return 0;
    state->current.aspect_num = numerator;
    state->current.aspect_den = denominator;
    state->current.adaptive_aspect = 0;
    return 1;
}

int psx_mod_enhancement_set_adaptive_aspect(
    PsxModEnhancementState *state,
    uint32_t max_numerator, uint32_t max_denominator) {
    if (!state || !valid_aspect(max_numerator, max_denominator)) return 0;
    state->current.adaptive_aspect = 1;
    state->current.adaptive_max_num = max_numerator;
    state->current.adaptive_max_den = max_denominator;
    return 1;
}

int psx_mod_enhancement_set_pgxp_mode(
    PsxModEnhancementState *state, uint32_t mode) {
    if (!state || mode > PSX_MOD_PGXP_FULL) return 0;
    state->current.geometry_precision = mode >= PSX_MOD_PGXP_GEOMETRY;
    state->current.perspective_textures = mode >= PSX_MOD_PGXP_FULL;
    return 1;
}

void psx_mod_enhancement_set_mouse_camera(
    PsxModEnhancementState *state, int enabled) {
    if (state) state->current.mouse_camera = enabled ? 1 : 0;
}
