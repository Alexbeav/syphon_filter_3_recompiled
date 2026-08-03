/* SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0 */
#include "frame_color_stats.h"

#include <assert.h>

#define BGR555(r, g, b) ((uint16_t)((r) | ((g) << 5) | ((b) << 10)))

int main(void)
{
    const uint16_t pixels[] = {
        BGR555(0, 0, 0),
        BGR555(31, 0, 0),
        BGR555(20, 12, 12),
        BGR555(12, 7, 8),
        BGR555(11, 0, 0),
        BGR555(31, 31, 31),
        BGR555(0, 31, 0),
        BGR555(0, 0, 31),
    };
    PsxFrameColorStats stats;
    psx_frame_color_stats_bgr555(pixels,
        sizeof(pixels) / sizeof(pixels[0]), &stats);
    assert(stats.total == 8);
    assert(stats.red_dominant == 3);
    assert(stats.hot_red == 2);
    assert(stats.saturated == 3);

    psx_frame_color_stats_bgr555(NULL, 10, &stats);
    assert(stats.total == 0 && stats.red_dominant == 0 &&
           stats.hot_red == 0 && stats.saturated == 0);
    psx_frame_color_stats_bgr555(pixels, 8, NULL);
    return 0;
}
