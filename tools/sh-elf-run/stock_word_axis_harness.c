#include "stock_axis_search.h"

#ifndef TORQUE_AXIS
#error "the verifier defines the engine-torque row axis"
#endif

static const struct axis_case stock_cases[] = {
    {"word-zero", TORQUE_AXIS, 0, 0, 0},
    {"word-below-first", TORQUE_AXIS, 127, 0, 0},
    {"word-first-point", TORQUE_AXIS, 128, 0, 0},
    {"word-first-count", TORQUE_AXIS, 129, 0, 512},
    {"word-first-midpoint", TORQUE_AXIS, 192, 0, 32768},
    {"word-before-second", TORQUE_AXIS, 255, 0, 65024},
    {"word-second-point", TORQUE_AXIS, 256, 2, 0},
    {"word-before-third", TORQUE_AXIS, 383, 2, 65024},
    {"word-point-twelve", TORQUE_AXIS, 1664, 24, 0},
    {"word-long-interval-first-count", TORQUE_AXIS, 1665, 24, 256},
    {"word-long-interval-midpoint", TORQUE_AXIS, 1792, 24, 32768},
    {"word-long-interval-before-end", TORQUE_AXIS, 1919, 24, 65280},
    {"word-point-thirteen", TORQUE_AXIS, 1920, 26, 0},
    {"word-before-point-fourteen", TORQUE_AXIS, 2175, 26, 65280},
    {"word-point-fourteen", TORQUE_AXIS, 2176, 28, 0},
    {"word-before-last", TORQUE_AXIS, 2431, 28, 65280},
    {"word-last-point", TORQUE_AXIS, 2432, 30, 0},
    {"word-unsigned-high-bit", TORQUE_AXIS, 0x8000, 30, 0},
    {"word-maximum", TORQUE_AXIS, 0xffff, 30, 0},
};

static const struct divider_case divider_cases[] = {
    {"fraction-three-quarters", 196608, 4, 49152},
    {"unsigned-divider-boundary", 0xffffffffU, 3, 0x55555555},
    {"zero-divisor", 0xffffffffU, 0, 0},
};

int main(void)
{
    size_t index;
    for (index = 0; index < ARRAY_SIZE(stock_cases); ++index)
        if (!run_axis_case(&stock_cases[index]))
            return 1;
    for (index = 0; index < ARRAY_SIZE(divider_cases); ++index)
        if (!run_divider_case(&divider_cases[index]))
            return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY,
           (unsigned long)(ARRAY_SIZE(stock_cases) + ARRAY_SIZE(divider_cases)));
    return 0;
}
