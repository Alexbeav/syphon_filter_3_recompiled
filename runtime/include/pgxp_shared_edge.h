#ifndef PSXRECOMP_PGXP_SHARED_EDGE_H
#define PSXRECOMP_PGXP_SHARED_EDGE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct PgxpSharedEdgeSample {
    uint32_t edge_a;
    uint32_t edge_b;
    uint32_t source_addr;
    uint16_t ot_rank;
    uint16_t depth_a;
    uint16_t depth_b;
    int32_t precise_ax;
    int32_t precise_ay;
    int32_t precise_bx;
    int32_t precise_by;
    uint8_t complete;
} PgxpSharedEdgeSample;

/* Make the second of two proven representations of one retail-visible edge
 * use the first edge's exact fractional endpoints. Returns nonzero only when
 * both complete samples have matching integer XY, depth, OT ownership and a
 * bounded packet-local source relationship, but disagree fractionally. */
int pgxp_shared_edge_canonicalize(const PgxpSharedEdgeSample *first,
                                  PgxpSharedEdgeSample *second);

/* Edge-local corrections are accepted only when their combined triangle keeps
 * the original nonzero/zero classification and winding. */
int pgxp_triangle_topology_preserved(int64_t area_before,
                                     int64_t area_after);

#ifdef __cplusplus
}
#endif

#endif
