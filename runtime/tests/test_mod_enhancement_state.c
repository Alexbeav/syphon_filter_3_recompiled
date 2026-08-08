#include "mod_enhancement_state.h"

#include <stdio.h>

static int check(int condition, const char *message) {
    if (condition) return 1;
    fprintf(stderr, "%s\n", message);
    return 0;
}

int main(void) {
    PsxModEnhancementState state;
    PsxModEnhancementConfig baseline = {
        4, 3, 0, 16, 9, PSX_MOD_PGXP_OFF, 0
    };
    int ok = 1;
    psx_mod_enhancement_initialize(&state, &baseline);
    ok &= check(psx_mod_enhancement_set_fixed_aspect(&state, 16, 9),
                "fixed aspect rejected");
    ok &= check(psx_mod_enhancement_set_adaptive_aspect(&state, 21, 9),
                "adaptive aspect rejected");
    ok &= check(psx_mod_enhancement_set_pgxp_mode(
                    &state, PSX_MOD_PGXP_FULL), "full PGXP rejected");
    psx_mod_enhancement_set_mouse_camera(&state, 1);
    ok &= check(state.current.adaptive_aspect &&
                state.current.pgxp_mode == PSX_MOD_PGXP_FULL &&
                state.current.mouse_camera, "contamination setup failed");

    psx_mod_enhancement_reset(&state);
    ok &= check(state.current.aspect_num == 4 &&
                state.current.aspect_den == 3 &&
                !state.current.adaptive_aspect &&
                state.current.pgxp_mode == PSX_MOD_PGXP_OFF &&
                !state.current.mouse_camera,
                "reset did not restore the complete compatibility baseline");
    ok &= check(!psx_mod_enhancement_set_pgxp_mode(&state, 3),
                "invalid PGXP mode accepted");
    ok &= check(!psx_mod_enhancement_set_fixed_aspect(&state, 1, 1),
                "invalid aspect accepted");

    if (!ok) return 1;
    puts("PASS: enhancement state resets from contamination");
    return 0;
}
