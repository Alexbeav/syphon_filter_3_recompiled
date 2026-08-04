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

    puts("ws full-width effect regression: PASS");
    return 0;
}
