#include "stock_axis_search.h"

#if !defined(FUEL_AXIS) || !defined(IGNITION_AXIS)
#error "the verifier defines the fuel and ignition row-axis symbols"
#endif

static const struct axis_case stock_cases[] = {
    {"fuel-zero", FUEL_AXIS, 0, 0, 0},
    {"fuel-below-first", FUEL_AXIS, 31, 0, 0},
    {"fuel-first-point", FUEL_AXIS, 32, 0, 0},
    {"fuel-first-quarter-count", FUEL_AXIS, 33, 0, 2048},
    {"fuel-first-midpoint", FUEL_AXIS, 48, 0, 32768},
    {"fuel-before-second", FUEL_AXIS, 63, 0, 63488},
    {"fuel-second-point", FUEL_AXIS, 64, 1, 0},
    {"fuel-before-third", FUEL_AXIS, 95, 1, 63488},
    {"fuel-fourth-interval-start", FUEL_AXIS, 160, 4, 0},
    {"fuel-long-interval-first-count", FUEL_AXIS, 161, 4, 1024},
    {"fuel-long-interval-midpoint", FUEL_AXIS, 192, 4, 32768},
    {"fuel-point-twelve", FUEL_AXIS, 512, 12, 0},
    {"fuel-short-interval-first-count", FUEL_AXIS, 513, 12, 4096},
    {"fuel-point-thirteen", FUEL_AXIS, 528, 13, 0},
    {"fuel-before-last", FUEL_AXIS, 591, 14, 63488},
    {"fuel-last-point", FUEL_AXIS, 592, 15, 0},
    {"fuel-maximum-word", FUEL_AXIS, 0xffff, 15, 0},
    {"ignition-zero", IGNITION_AXIS, 0, 0, 0},
    {"ignition-below-first", IGNITION_AXIS, 31, 0, 0},
    {"ignition-first-point", IGNITION_AXIS, 32, 0, 0},
    {"ignition-first-quarter-count", IGNITION_AXIS, 33, 0, 4096},
    {"ignition-first-midpoint", IGNITION_AXIS, 40, 0, 32768},
    {"ignition-before-second", IGNITION_AXIS, 47, 0, 61440},
    {"ignition-second-point", IGNITION_AXIS, 48, 1, 0},
    {"ignition-before-third", IGNITION_AXIS, 63, 1, 61440},
    {"ignition-third-point", IGNITION_AXIS, 64, 2, 0},
    {"ignition-third-midpoint", IGNITION_AXIS, 80, 2, 32768},
    {"ignition-point-twelve", IGNITION_AXIS, 480, 12, 0},
    {"ignition-point-twelve-first-count", IGNITION_AXIS, 481, 12, 2048},
    {"ignition-point-fourteen", IGNITION_AXIS, 544, 14, 0},
    {"ignition-final-first-count", IGNITION_AXIS, 545, 14, 1365},
    {"ignition-final-midpoint", IGNITION_AXIS, 568, 14, 32768},
    {"ignition-before-last", IGNITION_AXIS, 591, 14, 64170},
    {"ignition-last-point", IGNITION_AXIS, 592, 15, 0},
    {"ignition-maximum-word", IGNITION_AXIS, 0xffff, 15, 0},
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
