#ifndef PSX_GPU_PRIMITIVE_REJECT_H
#define PSX_GPU_PRIMITIVE_REJECT_H

#include <stdint.h>

/* PS1 hardware primitive-size rejection. Parsed coordinates are checked before
 * widescreen transforms and draw offsets; offsets do not change distances.
 * Hardware tests the original polygon edges and drops the complete primitive.
 * A quad's perimeter is v0-v1, v1-v3, v3-v2, v2-v0; its internal raster split
 * must neither create a rejection edge nor permit one triangle to survive. */
static inline int psx_gpu_edge_oversize(int32_t x0, int32_t y0,
                                        int32_t x1, int32_t y1) {
    int32_t dx = x0 > x1 ? x0 - x1 : x1 - x0;
    int32_t dy = y0 > y1 ? y0 - y1 : y1 - y0;
    return dx > 1023 || dy > 511;
}

static inline int psx_gpu_triangle_oversize(const int32_t* vx,
                                            const int32_t* vy,
                                            int a, int b, int c) {
    return psx_gpu_edge_oversize(vx[a], vy[a], vx[b], vy[b]) ||
           psx_gpu_edge_oversize(vx[b], vy[b], vx[c], vy[c]) ||
           psx_gpu_edge_oversize(vx[c], vy[c], vx[a], vy[a]);
}

static inline int psx_gpu_quad_oversize(const int32_t* vx,
                                        const int32_t* vy) {
    return psx_gpu_edge_oversize(vx[0], vy[0], vx[1], vy[1]) ||
           psx_gpu_edge_oversize(vx[1], vy[1], vx[3], vy[3]) ||
           psx_gpu_edge_oversize(vx[3], vy[3], vx[2], vy[2]) ||
           psx_gpu_edge_oversize(vx[2], vy[2], vx[0], vy[0]);
}

static inline int psx_gpu_line_oversize(int32_t x0, int32_t y0,
                                        int32_t x1, int32_t y1) {
    return psx_gpu_edge_oversize(x0, y0, x1, y1);
}

#endif
