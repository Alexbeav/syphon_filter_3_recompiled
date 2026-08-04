#include "mouse_pad_adapter.h"

#include <assert.h>

int main(void) {
    mouse_pad_configure(1, 10, 4);
    mouse_pad_set_focus(1);
    mouse_pad_add_motion(5, -5);
    unsigned short p = mouse_pad_merge(
        0xFFFFu, PSX_MOUSE_RIGHT | PSX_MOUSE_LEFT);
    assert((p & (1u << 15)) == 0); /* left mouse -> Square/fire */
    assert((p & (1u << 10)) == 0); /* right mouse -> L1/aim */
    assert((p & (1u << 5)) == 0);  /* positive X -> D-pad right */
    assert((p & (1u << 6)) == 0);  /* mouse up -> authored view up */
    mouse_pad_commit_frame();

    mouse_pad_reset();
    mouse_pad_add_motion(5, 0);
    p = mouse_pad_merge(0xFFFFu, 0);
    assert((p & (1u << 5)) != 0);  /* below chase threshold */
    p = mouse_pad_merge(0xFFFFu, PSX_MOUSE_RIGHT);
    assert((p & (1u << 5)) == 0);  /* same delta triggers in aim */
    mouse_pad_commit_frame();

    mouse_pad_set_focus(0);
    p = mouse_pad_merge(0xFFFFu, PSX_MOUSE_LEFT);
    assert(p == 0xFFFFu);          /* focus loss is neutral */

    /* Direct-camera mode disables fallback D-pad motion, not retail mouse
     * buttons: right-click must still hold L1 and left-click must fire. */
    mouse_pad_configure(0, 10, 4);
    mouse_pad_set_focus(1);
    mouse_pad_add_motion(100, 100);
    p = mouse_pad_merge_buttons(0xFFFFu,
        PSX_MOUSE_RIGHT | PSX_MOUSE_LEFT);
    assert((p & (1u << 15)) == 0);
    assert((p & (1u << 10)) == 0);
    assert((p & ((1u << 4) | (1u << 5) | (1u << 6) | (1u << 7))) ==
           ((1u << 4) | (1u << 5) | (1u << 6) | (1u << 7)));
    mouse_pad_set_focus(0);
    assert(mouse_pad_merge_buttons(0xFFFFu, PSX_MOUSE_LEFT) == 0xFFFFu);

    /* Each wheel notch becomes one retail Select edge with a sampled release
     * between queued notches. Direction is intentionally title-neutral: the
     * retail weapon ring owns ordering. */
    mouse_pad_configure(1, 10, 4);
    mouse_pad_set_focus(1);
    mouse_pad_add_wheel(-2);
    p = mouse_pad_merge_buttons(0xFFFFu, 0);
    assert((p & (1u << 0)) == 0);
    mouse_pad_commit_frame();
    p = mouse_pad_merge_buttons(0xFFFFu, 0);
    assert((p & (1u << 0)) != 0);
    mouse_pad_commit_frame();
    p = mouse_pad_merge_buttons(0xFFFFu, 0);
    assert((p & (1u << 0)) == 0);
    mouse_pad_commit_frame();
    p = mouse_pad_merge_buttons(0xFFFFu, 0);
    assert((p & (1u << 0)) != 0);
    mouse_pad_set_focus(0);
    mouse_pad_add_wheel(1);
    assert(mouse_pad_merge_buttons(0xFFFFu, 0) == 0xFFFFu);
    return 0;
}
