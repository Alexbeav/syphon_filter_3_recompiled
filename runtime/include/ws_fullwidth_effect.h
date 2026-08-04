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

/* Classify an authored-width axis-aligned quad after the caller proves it came
 * from a screen-space/effect submission. The renderer's flat-rect backend then
 * owns native-wide margin coverage. Keeping ownership explicit is essential:
 * SF3 world lists contain width-spanning quads too. */
static inline int ws_fullwidth_effect_quad_rect(
    int active, int screen_space_owned, int display_w,
    int32_t authored_left, const int32_t vx[4], const int32_t vy[4],
    int32_t *x, int32_t *y, int *w, int *h) {
    if (!active || !screen_space_owned || display_w <= 0 || !vx || !vy ||
        !x || !y || !w || !h)
        return 0;
    if (vx[0] != vx[2] || vx[1] != vx[3] ||
        vy[0] != vy[1] || vy[2] != vy[3])
        return 0;

    const int left_pair = vx[0] <= vx[1] ? 0 : 1;
    const int right_pair = left_pair ^ 1;
    const int32_t left = vx[left_pair];
    const int32_t right = vx[right_pair];
    const int32_t top = vy[0] < vy[2] ? vy[0] : vy[2];
    const int32_t bottom = vy[0] < vy[2] ? vy[2] : vy[0];
    if (left > authored_left || right < authored_left + display_w ||
        right <= left || bottom <= top)
        return 0;
    *x = left;
    *y = top;
    *w = (int)(right - left);
    *h = (int)(bottom - top);
    return 1;
}

#endif
