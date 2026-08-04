#ifndef PSXRECOMP_WS_FULLWIDTH_EFFECT_H
#define PSXRECOMP_WS_FULLWIDTH_EFFECT_H

#include <stdint.h>

/* Expand a screen-space rectangle that owns the complete authored horizontal
 * display into both native-wide reveal margins. Height is intentionally not an
 * ownership signal: cinematic mattes and many filters are partial-height. */
static inline int ws_fullwidth_effect_rect(int active, int display_w,
                                           int reveal, int32_t authored_left,
                                           int32_t *x, int *w) {
    if (!active || display_w <= 0 || reveal <= 0 || !x || !w || *w <= 0)
        return 0;
    if (*x > authored_left || *x + *w < authored_left + display_w)
        return 0;
    *x -= reveal;
    *w += 2 * reveal;
    return 1;
}

#endif
