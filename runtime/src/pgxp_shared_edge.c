#include "pgxp_shared_edge.h"

int pgxp_shared_edge_canonicalize(const PgxpSharedEdgeSample *first,
                                  PgxpSharedEdgeSample *second) {
    if (!first || !second || !first->complete || !second->complete ||
        first->edge_a != second->edge_a ||
        first->edge_b != second->edge_b ||
        first->ot_rank != second->ot_rank ||
        first->depth_a != second->depth_a ||
        first->depth_b != second->depth_b)
        return 0;

    const uint32_t source_distance = first->source_addr > second->source_addr
        ? first->source_addr - second->source_addr
        : second->source_addr - first->source_addr;
    if (source_distance > 0x10000u ||
        (first->precise_ax == second->precise_ax &&
         first->precise_ay == second->precise_ay &&
         first->precise_bx == second->precise_bx &&
         first->precise_by == second->precise_by))
        return 0;

    second->precise_ax = first->precise_ax;
    second->precise_ay = first->precise_ay;
    second->precise_bx = first->precise_bx;
    second->precise_by = first->precise_by;
    return 1;
}

int pgxp_triangle_topology_preserved(int64_t area_before,
                                     int64_t area_after) {
    if (area_before == 0 || area_after == 0)
        return area_before == area_after;
    return (area_before < 0) == (area_after < 0);
}
