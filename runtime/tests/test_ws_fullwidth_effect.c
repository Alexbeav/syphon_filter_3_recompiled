#include "ws_fullwidth_effect.h"

#include <stdint.h>
#include <stdio.h>

int main(void) {
    int32_t x = 0;
    int w = 368;
    if (ws_fullwidth_effect_rect(0, 368, 61, 0, &x, &w)) return 1;
    if (x != 0 || w != 368) return 2;
    if (!ws_fullwidth_effect_rect(1, 368, 61, 0, &x, &w)) return 3;
    if (x != -61 || w != 490) return 4;

    x = 1; w = 367;
    if (ws_fullwidth_effect_rect(1, 368, 61, 0, &x, &w)) return 5;

    x = -184; w = 368;
    if (!ws_fullwidth_effect_rect(1, 368, 61, -184, &x, &w)) return 6;
    if (x != -245 || w != 490) return 7;

    {
        const int32_t vx[4] = {0, 368, 0, 368};
        const int32_t vy[4] = {0, 0, 44, 44};
        int32_t qx = 0, qy = 0; int qw = 0, qh = 0;
        if (!ws_fullwidth_effect_quad_rect(
                1, 1, 368, 0, vx, vy, &qx, &qy, &qw, &qh)) return 8;
        if (qx != 0 || qy != 0 || qw != 368 || qh != 44) return 9;
        if (ws_fullwidth_effect_quad_rect(
                1, 0, 368, 0, vx, vy, &qx, &qy, &qw, &qh)) return 10;
    }
    {
        const int32_t vx[4] = {368, 0, 368, 0};
        const int32_t vy[4] = {196, 196, 240, 240};
        int32_t qx = 0, qy = 0; int qw = 0, qh = 0;
        if (!ws_fullwidth_effect_quad_rect(
                1, 1, 368, 0, vx, vy, &qx, &qy, &qw, &qh)) return 11;
        if (qx != 0 || qy != 196 || qw != 368 || qh != 44) return 12;
    }
    {
        const int32_t vx[4] = {0, 368, 0, 368};
        const int32_t projected[4] = {80, 82, 140, 138};
        int32_t qx = 0, qy = 0; int qw = 0, qh = 0;
        if (ws_fullwidth_effect_quad_rect(
                1, 1, 368, 0, vx, projected,
                &qx, &qy, &qw, &qh)) return 13;
    }
    {
        const int32_t vx[4] = {1, 367, 1, 367};
        const int32_t vy[4] = {0, 0, 44, 44};
        int32_t qx = 0, qy = 0; int qw = 0, qh = 0;
        if (ws_fullwidth_effect_quad_rect(
                1, 1, 368, 0, vx, vy, &qx, &qy, &qw, &qh)) return 14;
    }
    {
        const int32_t vx[4] = {-184, 184, -184, 184};
        const int32_t vy[4] = {-120, -120, -75, -75};
        int32_t qx = 0, qy = 0; int qw = 0, qh = 0;
        if (!ws_fullwidth_effect_quad_rect(
                1, 1, 368, -184, vx, vy,
                &qx, &qy, &qw, &qh)) return 15;
        if (qx != -184 || qy != -120 || qw != 368 || qh != 45) return 16;
    }

    puts("ws full-width effect regression: PASS");
    return 0;
}
