#include "pgxp_shared_edge.h"

#include <stdio.h>

static int failures;

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "FAIL:%d: %s\n", __LINE__, #expr); \
        failures++; \
    } \
} while (0)

static PgxpSharedEdgeSample sample(void) {
    PgxpSharedEdgeSample value = {
        0x00100020u, 0x00110021u, 0x00150000u, 42u, 300u, 301u,
        0x00208000, 0x00104000, 0x00218000, 0x00114000, 1u
    };
    return value;
}

int main(void) {
    PgxpSharedEdgeSample first = sample();
    PgxpSharedEdgeSample second = sample();
    second.source_addr += 0x300u;
    second.precise_ax += 0x9000;
    second.precise_by -= 0x7000;
    CHECK(pgxp_shared_edge_canonicalize(&first, &second) == 1);
    CHECK(second.precise_ax == first.precise_ax);
    CHECK(second.precise_by == first.precise_by);

    second = sample();
    second.complete = 0;
    second.precise_ax++;
    CHECK(pgxp_shared_edge_canonicalize(&first, &second) == 0);

    CHECK(pgxp_triangle_topology_preserved(100, 25) == 1);
    CHECK(pgxp_triangle_topology_preserved(-100, -25) == 1);
    CHECK(pgxp_triangle_topology_preserved(0, 0) == 1);
    CHECK(pgxp_triangle_topology_preserved(100, -1) == 0);
    CHECK(pgxp_triangle_topology_preserved(-100, 1) == 0);
    CHECK(pgxp_triangle_topology_preserved(100, 0) == 0);
    CHECK(pgxp_triangle_topology_preserved(0, 100) == 0);
    CHECK(second.precise_ax != first.precise_ax);

    second = sample();
    second.depth_b++;
    second.precise_ax++;
    CHECK(pgxp_shared_edge_canonicalize(&first, &second) == 0);

    second = sample();
    second.ot_rank++;
    second.precise_ax++;
    CHECK(pgxp_shared_edge_canonicalize(&first, &second) == 0);

    second = sample();
    second.source_addr += 0x10004u;
    second.precise_ax++;
    CHECK(pgxp_shared_edge_canonicalize(&first, &second) == 0);

    if (failures) return 1;
    puts("PASS: PGXP shared-edge correction is bounded and topology-safe");
    return 0;
}
