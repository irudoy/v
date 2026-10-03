#include "stock_axis_search.h"

#if !defined(CVTC_RPM_AXIS) || !defined(CVTC_LOAD_AXIS)
#error "the verifier defines the main CVTC axes"
#endif

static const struct axis_case stock_cases[] = {
    {"rpm-zero", CVTC_RPM_AXIS, 0, 0, 0},
    {"rpm-below-first", CVTC_RPM_AXIS, 15, 0, 0},
    {"rpm-first-point", CVTC_RPM_AXIS, 16, 0, 0},
    {"rpm-first-midpoint", CVTC_RPM_AXIS, 17, 0, 32768},
    {"rpm-second-point", CVTC_RPM_AXIS, 18, 1, 0},
    {"rpm-second-midpoint", CVTC_RPM_AXIS, 19, 1, 32768},
    {"rpm-wider-interval", CVTC_RPM_AXIS, 21, 2, 16384},
    {"rpm-wide-interval", CVTC_RPM_AXIS, 35, 5, 24576},
    {"rpm-before-penultimate", CVTC_RPM_AXIS, 111, 13, 61440},
    {"rpm-penultimate", CVTC_RPM_AXIS, 112, 14, 0},
    {"rpm-final-first-count", CVTC_RPM_AXIS, 113, 14, 4096},
    {"rpm-before-last", CVTC_RPM_AXIS, 127, 14, 61440},
    {"rpm-last", CVTC_RPM_AXIS, 128, 15, 0},
    {"rpm-maximum-byte", CVTC_RPM_AXIS, 255, 15, 0},
    {"load-zero", CVTC_LOAD_AXIS, 0, 0, 0},
    {"load-below-first", CVTC_LOAD_AXIS, 7, 0, 0},
    {"load-first", CVTC_LOAD_AXIS, 8, 0, 0},
    {"load-first-count", CVTC_LOAD_AXIS, 9, 0, 8192},
    {"load-before-second", CVTC_LOAD_AXIS, 15, 0, 57344},
    {"load-second", CVTC_LOAD_AXIS, 16, 1, 0},
    {"load-middle-count", CVTC_LOAD_AXIS, 27, 2, 24576},
    {"load-middle-midpoint", CVTC_LOAD_AXIS, 28, 2, 32768},
    {"load-upper-count", CVTC_LOAD_AXIS, 65, 7, 8192},
    {"load-before-last", CVTC_LOAD_AXIS, 127, 14, 57344},
    {"load-last", CVTC_LOAD_AXIS, 128, 15, 0},
    {"load-forced-maximum", CVTC_LOAD_AXIS, 255, 15, 0},
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
