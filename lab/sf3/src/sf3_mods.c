#include "mod_plugins.h"

#include <string.h>

static void enable_mouse_look(void) {
    (void)psx_mod_set_mouse_camera(1);
}

static void enable_widescreen(void) {
    (void)psx_mod_set_fixed_display_aspect(16, 9);
}

static void enable_pgxp(void) {
    char mode[16];
    uint32_t pgxp_mode = PSX_MOD_PGXP_GEOMETRY;
    if (psx_mod_option_value("sf3.enhancements", "pgxp", "mode",
                             mode, sizeof(mode)) &&
        strcmp(mode, "full") == 0) {
        pgxp_mode = PSX_MOD_PGXP_FULL;
    }
    (void)psx_mod_set_pgxp_mode(pgxp_mode);
}

PSX_MOD_CONSTRUCTOR(register_sf3_mods) {
    (void)psx_mod_register_activation_plugin(
        "sf3.mouse-look", enable_mouse_look);
    (void)psx_mod_register_activation_plugin(
        "sf3.widescreen", enable_widescreen);
    (void)psx_mod_register_activation_plugin(
        "sf3.pgxp", enable_pgxp);
}
