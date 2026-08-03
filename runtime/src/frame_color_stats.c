/* SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0 */
#include "frame_color_stats.h"

void psx_frame_color_stats_bgr555(const uint16_t *pixels, size_t count,
                                  PsxFrameColorStats *out)
{
    PsxFrameColorStats result = {0, 0, 0, 0};
    if (!out) return;
    if (!pixels) {
        *out = result;
        return;
    }
    result.total = (uint64_t)count;
    for (size_t i = 0; i < count; i++) {
        const unsigned p = pixels[i];
        const unsigned r = p & 31u;
        const unsigned g = (p >> 5) & 31u;
        const unsigned b = (p >> 10) & 31u;
        unsigned hi = r > g ? r : g;
        unsigned lo = r < g ? r : g;
        if (b > hi) hi = b;
        if (b < lo) lo = b;
        if (r >= 12u && 5u * r >= 8u * g && 20u * r >= 27u * b)
            result.red_dominant++;
        if (r >= 20u && g < 13u && b < 13u)
            result.hot_red++;
        if (hi - lo >= 12u)
            result.saturated++;
    }
    *out = result;
}
