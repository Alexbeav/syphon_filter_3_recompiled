/* SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0 */
#ifndef PSX_FRAME_COLOR_STATS_H
#define PSX_FRAME_COLOR_STATS_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct PsxFrameColorStats {
    uint64_t total;
    uint64_t red_dominant;
    uint64_t hot_red;
    uint64_t saturated;
} PsxFrameColorStats;

/* Summarize PS1 BGR555 pixels without interpreting scene or title state.
 * Thresholds mirror simple 8-bit diagnostic predicates at 5-bit precision:
 * red >= 96 and strongly exceeds green/blue; hot red additionally requires
 * red >= 160 with green/blue < 104; saturated spans at least 96 levels. */
void psx_frame_color_stats_bgr555(const uint16_t *pixels, size_t count,
                                  PsxFrameColorStats *out);

#ifdef __cplusplus
}
#endif

#endif
