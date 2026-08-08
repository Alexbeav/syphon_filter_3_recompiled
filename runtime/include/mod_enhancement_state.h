#ifndef PSX_MOD_ENHANCEMENT_STATE_H
#define PSX_MOD_ENHANCEMENT_STATE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

enum PsxModPgxpMode {
    PSX_MOD_PGXP_OFF = 0,
    PSX_MOD_PGXP_GEOMETRY = 1,
    PSX_MOD_PGXP_FULL = 2
};

typedef struct PsxModEnhancementConfig {
    uint32_t aspect_num;
    uint32_t aspect_den;
    int adaptive_aspect;
    uint32_t adaptive_max_num;
    uint32_t adaptive_max_den;
    int geometry_precision;
    int perspective_textures;
    int mouse_camera;
} PsxModEnhancementConfig;

typedef struct PsxModEnhancementState {
    PsxModEnhancementConfig baseline;
    PsxModEnhancementConfig current;
} PsxModEnhancementState;

/* Capture the complete non-Mod state. A null/invalid baseline becomes the
 * compatibility identity: 4:3, fixed view, PGXP off, mouse camera off. */
void psx_mod_enhancement_initialize(
    PsxModEnhancementState *state,
    const PsxModEnhancementConfig *baseline);
void psx_mod_enhancement_reset(PsxModEnhancementState *state);

int psx_mod_enhancement_set_fixed_aspect(
    PsxModEnhancementState *state, uint32_t numerator, uint32_t denominator);
int psx_mod_enhancement_set_adaptive_aspect(
    PsxModEnhancementState *state,
    uint32_t max_numerator, uint32_t max_denominator);
int psx_mod_enhancement_set_pgxp_mode(
    PsxModEnhancementState *state, uint32_t mode);
void psx_mod_enhancement_set_mouse_camera(
    PsxModEnhancementState *state, int enabled);

#ifdef __cplusplus
}
#endif

#endif
