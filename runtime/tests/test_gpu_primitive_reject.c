#include "gpu_primitive_reject.h"

#include <stdio.h>

static int failures;

static void check(int condition, const char* name) {
    if (!condition) {
        fprintf(stderr, "FAIL: %s\n", name);
        failures++;
    }
}

int main(void) {
    int32_t x_ok[3] = { -512, 511, 0 };
    int32_t y_ok[3] = { -255, 256, 0 };
    int32_t x_wide[3] = { -512, 512, 0 };
    int32_t y_tall[3] = { -256, 256, 0 };
    int32_t quad_partial_x[4] = { 568, -561, 110, -112 };
    int32_t quad_partial_y[4] = { 549, 630, 181, 185 };
    int32_t quad_split_x[4] = { 0, -512, 512, 0 };
    int32_t quad_split_y[4] = { 0, 0, 20, 20 };

    check(!psx_gpu_triangle_oversize(x_ok, y_ok, 0, 1, 2),
          "inclusive 1023x511 boundary is accepted");
    check(psx_gpu_triangle_oversize(x_wide, y_ok, 0, 1, 2),
          "triangle wider than 1023 is rejected");
    check(psx_gpu_triangle_oversize(x_ok, y_tall, 0, 1, 2),
          "triangle taller than 511 is rejected");
    check(psx_gpu_quad_oversize(quad_partial_x, quad_partial_y),
          "one oversized quad perimeter edge rejects the complete primitive");
    check(!psx_gpu_triangle_oversize(quad_partial_x, quad_partial_y, 2, 1, 3),
          "the second raster triangle alone would incorrectly survive");
    check(!psx_gpu_quad_oversize(quad_split_x, quad_split_y),
          "internal quad split is not a hardware rejection edge");
    check(psx_gpu_triangle_oversize(quad_split_x, quad_split_y, 2, 1, 3),
          "triangle-local testing would incorrectly reject the split edge");
    check(!psx_gpu_line_oversize(-512, -255, 511, 256),
          "line boundary is accepted");
    check(psx_gpu_line_oversize(-512, 0, 512, 0),
          "oversize horizontal line is rejected");
    check(psx_gpu_line_oversize(0, -256, 0, 256),
          "oversize vertical line is rejected");

    if (failures) return 1;
    puts("PASS: PS1 primitive size rejection boundaries");
    return 0;
}
