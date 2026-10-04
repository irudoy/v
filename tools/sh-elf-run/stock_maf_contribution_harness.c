#include <stdint.h>
#include <stdio.h>

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(TAIL_ENTRY) \
    || !defined(MAF_INPUT_B1) || !defined(MAF_INPUT_B2) \
    || !defined(MAF_OUTPUT_B1) || !defined(MAF_OUTPUT_B2) \
    || !defined(BASE_B1) || !defined(BASE_B2) \
    || !defined(REFERENCE_B1) || !defined(REFERENCE_B2) \
    || !defined(FALLBACK_B1) || !defined(FALLBACK_B2) \
    || !defined(DELTA_B1) || !defined(DELTA_B2) \
    || !defined(CORRECTION_B1) || !defined(CORRECTION_B2) \
    || !defined(MAGNITUDE_B1) || !defined(MAGNITUDE_B2) \
    || !defined(SIGN_FLAGS) || !defined(LATCH_B1) || !defined(LATCH_B2) \
    || !defined(ENABLE_FLAGS) || !defined(DIAGNOSTIC_FLAGS) || !defined(INHIBIT_FLAGS) \
    || !defined(COEFFICIENT_ADDRESS) || !defined(FALLBACK_WEIGHT_ADDRESS) \
    || !defined(CONTRIBUTION_BASE)
#error "the verifier defines both MAF banks, states, flags, and coefficients"
#endif

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U
#define MACL_SEED 0x89abcdefU

extern uint32_t stock_invoke_compensation(uint32_t, uint32_t, uint32_t, uint32_t *);
extern uint32_t stock_invoke_contribution_tail(uint32_t, uint32_t, const void *, uint32_t *);

struct contribution_case {
    const char *name;
    uint16_t input, reference, delta;
    int16_t correction;
    uint16_t magnitude;
    uint8_t positive, enable, diagnostic, inhibit, latch;
    uint32_t fallback;
    uint8_t weight;
    uint32_t output;
    uint16_t base;
    int16_t correction_after;
    uint16_t magnitude_after;
    uint8_t positive_after, latch_after;
};

struct tail_case {
    const char *name;
    int32_t residual;
    uint16_t base, delta;
    int16_t correction;
    uint32_t output;
    int16_t correction_after;
    uint16_t magnitude_after;
    uint8_t positive_after;
};

static const struct contribution_case contribution_cases[] = {
    {"active-ordinary", 1000, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 5782, 5625, 131, 0, 1, 0},
    {"base-0-0", 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, 0, 0, 1, 0},
    {"base-1-0", 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 5, 5, 0, 0, 1, 0},
    {"base-0-1", 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, 0, 4, 0, 0},
    {"base-7-0", 7, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 39, 39, 0, 0, 1, 0},
    {"base-0-7", 0, 7, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, 0, 32, 0, 0},
    {"base-8-0", 8, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 46, 45, 1, 0, 1, 0},
    {"base-0-8", 0, 8, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, 0, 37, 0, 0},
    {"base-9-0", 9, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 51, 50, 1, 0, 1, 0},
    {"base-0-9", 0, 9, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, 0, 41, 0, 0},
    {"base-1000-1000", 1000, 1000, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 1027, 1000, 23, 0, 1, 0},
    {"base-1001-1000", 1001, 1000, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 1032, 1005, 23, 0, 1, 0},
    {"base-999-1000", 999, 1000, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 1022, 995, 23, 0, 1, 0},
    {"base-65535-0", 65535, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 370480, 65535, 1535, 0, 1, 0},
    {"base-0-65535", 0, 65535, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, 0, 65535, 0, 0},
    {"base-65535-65535", 65535, 65535, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 67381, 65535, 1535, 0, 1, 0},
    {"base-65534-65535", 65534, 65535, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 67376, 65530, 1535, 0, 1, 0},
    {"base-65535-65534", 65535, 65534, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 67385, 65535, 1535, 0, 1, 0},
    {"base-32768-32767", 32768, 32767, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 33696, 32772, 768, 0, 1, 0},
    {"base-32767-32768", 32767, 32768, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 33685, 32763, 767, 0, 1, 0},
    {"delta-negative-1", 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, 0, 0, 1, 0},
    {"delta-positive-1", 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 1, 1, 0, 0, 1, 0},
    {"delta-negative-127", 0, 0, 127, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, -2, 2, 0, 0},
    {"delta-positive-127", 127, 127, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 129, 127, 2, 0, 1, 0},
    {"delta-negative-128", 0, 0, 128, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, -3, 3, 0, 0},
    {"delta-positive-128", 128, 128, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 131, 128, 3, 0, 1, 0},
    {"delta-negative-129", 0, 0, 129, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, -3, 3, 0, 0},
    {"delta-positive-129", 129, 129, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 132, 129, 3, 0, 1, 0},
    {"delta-negative-511", 0, 0, 511, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, -11, 11, 0, 0},
    {"delta-positive-511", 511, 511, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 524, 511, 11, 0, 1, 0},
    {"delta-negative-512", 0, 0, 512, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, -12, 12, 0, 0},
    {"delta-positive-512", 512, 512, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 526, 512, 12, 0, 1, 0},
    {"delta-negative-513", 0, 0, 513, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, -12, 12, 0, 0},
    {"delta-positive-513", 513, 513, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 527, 513, 12, 0, 1, 0},
    {"delta-negative-32767", 0, 0, 32767, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, -767, 767, 0, 0},
    {"delta-positive-32767", 32767, 32767, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 33689, 32767, 767, 0, 1, 0},
    {"delta-negative-32768", 0, 0, 32768, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, -768, 768, 0, 0},
    {"delta-positive-32768", 32768, 32768, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 33692, 32768, 768, 0, 1, 0},
    {"delta-negative-65535", 0, 0, 65535, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, -1535, 1535, 0, 0},
    {"delta-positive-65535", 65535, 65535, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 67381, 65535, 1535, 0, 1, 0},
    {"correction--32768", 100, 100, 100, -32768, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 100, -32640, 32540, 0, 0},
    {"correction--32767", 100, 100, 100, -32767, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 100, -32639, 32539, 0, 0},
    {"correction--257", 100, 100, 100, -257, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 100, -255, 155, 0, 0},
    {"correction--256", 100, 100, 100, -256, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 100, -255, 155, 0, 0},
    {"correction--255", 100, 100, 100, -255, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 100, -254, 154, 0, 0},
    {"correction--129", 100, 100, 100, -129, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 100, -128, 28, 0, 0},
    {"correction--128", 100, 100, 100, -128, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 100, -127, 27, 0, 0},
    {"correction--64", 100, 100, 100, -64, 0, 1, 1, 0, 0, 0, 1193046, 128, 37, 100, -63, 0, 1, 0},
    {"correction--1", 100, 100, 100, -1, 0, 1, 1, 0, 0, 0, 1193046, 128, 100, 100, 0, 0, 1, 0},
    {"correction-0", 100, 100, 100, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 100, 100, 0, 0, 1, 0},
    {"correction-1", 100, 100, 100, 1, 0, 1, 1, 0, 0, 0, 1193046, 128, 100, 100, 0, 0, 1, 0},
    {"correction-64", 100, 100, 100, 64, 0, 1, 1, 0, 0, 0, 1193046, 128, 175, 100, 63, 0, 1, 0},
    {"correction-128", 100, 100, 100, 128, 0, 1, 1, 0, 0, 0, 1193046, 128, 252, 100, 127, 0, 1, 0},
    {"correction-255", 100, 100, 100, 255, 0, 1, 1, 0, 0, 0, 1193046, 128, 405, 100, 254, 0, 1, 0},
    {"correction-256", 100, 100, 100, 256, 0, 1, 1, 0, 0, 0, 1193046, 128, 406, 100, 255, 0, 1, 0},
    {"correction-257", 100, 100, 100, 257, 0, 1, 1, 0, 0, 0, 1193046, 128, 406, 100, 255, 0, 1, 0},
    {"correction-32767", 100, 100, 100, 32767, 0, 1, 1, 0, 0, 0, 1193046, 128, 39368, 100, 32639, 0, 1, 0},
    {"correction-positive-cap", 65535, 65535, 0, 32767, 0, 1, 1, 0, 0, 0, 1193046, 128, 104957, 65535, 32767, 0, 1, 0},
    {"correction-negative-cap", 0, 0, 65535, -32768, 0, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, -32768, 32768, 0, 0},
    {"residual-0-0", 1000, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1193046, 128, 5782, 5625, 131, 0, 1, 0},
    {"residual-1-0", 1000, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1193046, 128, 5781, 5625, 131, 0, 1, 0},
    {"residual-1-1", 1000, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1193046, 128, 5783, 5625, 131, 0, 1, 0},
    {"residual-65535-0", 1000, 0, 0, 0, 65535, 0, 1, 0, 0, 0, 1193046, 128, 0, 5625, 131, 59753, 0, 0},
    {"residual-65535-1", 1000, 0, 0, 0, 65535, 1, 1, 0, 0, 0, 1193046, 128, 71317, 5625, 131, 0, 1, 0},
    {"negative-base-magnitude-cap", 0, 65535, 0, 0, 65535, 0, 1, 0, 0, 0, 1193046, 128, 0, 0, 0, 65535, 0, 0},
    {"negative-value-positive-residual", 0, 0, 0, -100, 200, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, -99, 101, 1, 0},
    {"negative-value-negative-residual", 0, 0, 0, -100, 50, 1, 1, 0, 0, 0, 1193046, 128, 0, 0, -99, 49, 0, 0},
    {"residual-cancels-positive-value", 100, 100, 100, 0, 100, 0, 1, 0, 0, 0, 1193046, 128, 0, 100, 0, 0, 1, 0},
    {"mode-0", 1000, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1193046, 128, 597023, 65535, 0, 0, 1, 0},
    {"mode-1", 1000, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1193046, 128, 5782, 5625, 131, 0, 1, 0},
    {"mode-2", 1000, 0, 0, 0, 0, 1, 0, 128, 0, 0, 1193046, 128, 597023, 65535, 0, 0, 1, 3},
    {"mode-3", 1000, 0, 0, 0, 0, 1, 1, 128, 0, 0, 1193046, 128, 597023, 65535, 0, 0, 1, 3},
    {"mode-4", 1000, 0, 0, 0, 0, 1, 0, 0, 8, 0, 1193046, 128, 597023, 65535, 0, 0, 1, 3},
    {"mode-5", 1000, 0, 0, 0, 0, 1, 1, 0, 8, 0, 1193046, 128, 597023, 65535, 0, 0, 1, 3},
    {"mode-6", 1000, 0, 0, 0, 0, 1, 0, 128, 8, 0, 1193046, 128, 597023, 65535, 0, 0, 1, 3},
    {"mode-7", 1000, 0, 0, 0, 0, 1, 1, 128, 8, 0, 1193046, 128, 597023, 65535, 0, 0, 1, 3},
    {"latch-1", 1000, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1193046, 128, 597023, 65535, 0, 0, 1, 1},
    {"latch-3", 1000, 0, 0, 0, 0, 1, 1, 0, 0, 3, 1193046, 128, 597023, 65535, 0, 0, 1, 3},
    {"latch-255", 1000, 0, 0, 0, 0, 1, 1, 0, 0, 255, 1193046, 128, 597023, 65535, 0, 0, 1, 255},
    {"unrelated-mode-bits", 1000, 0, 0, 0, 0, 1, 255, 127, 247, 0, 1193046, 128, 5782, 5625, 131, 0, 1, 0},
    {"fallback-00000000", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 128, 32767, 32767, 0, 0, 1, 0},
    {"fallback-00000001", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 128, 32768, 32768, 0, 0, 1, 0},
    {"fallback-00000002", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 128, 32768, 32768, 0, 0, 1, 0},
    {"fallback-0000ffff", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 65535, 128, 65535, 65535, 0, 0, 1, 0},
    {"fallback-00010000", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 65536, 128, 65535, 65535, 0, 0, 1, 0},
    {"fallback-0001ffff", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 131071, 128, 98303, 65535, 0, 0, 1, 0},
    {"fallback-007fffff", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 8388607, 128, 4227071, 65535, 0, 0, 1, 0},
    {"fallback-00ffffff", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 16777215, 128, 8421375, 65535, 0, 0, 1, 0},
    {"fallback-01000000", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 16777216, 128, 8421375, 65535, 0, 0, 1, 0},
    {"fallback-01ffffff", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 33554431, 128, 16777215, 65535, 0, 0, 1, 0},
    {"fallback-02000000", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 33554432, 128, 32767, 32767, 0, 0, 1, 0},
    {"fallback-7fffffff", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2147483647, 128, 16777215, 65535, 0, 0, 1, 0},
    {"fallback-80000000", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2147483648, 128, 32767, 32767, 0, 0, 1, 0},
    {"fallback-ffffffff", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 4294967295, 128, 16777215, 65535, 0, 0, 1, 0},
    {"fallback-weight-0", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 16843009, 0, 65793, 65535, 0, 0, 1, 0},
    {"fallback-weight-1", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 16843009, 1, 16777215, 65535, 0, 0, 1, 0},
    {"fallback-weight-127", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 16843009, 127, 8519809, 65535, 0, 0, 1, 0},
    {"fallback-weight-129", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 16843009, 129, 8388734, 65535, 0, 0, 1, 0},
    {"fallback-weight-255", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 16843009, 255, 131072, 65535, 0, 0, 1, 0},
    {"fallback-zero-result", 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 128, 0, 0, 0, 0, 1, 0},
    {"fallback-word-cap-before", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 65535, 128, 65535, 65535, 0, 0, 1, 0},
    {"fallback-word-cap-after", 65535, 0, 0, 0, 0, 1, 0, 0, 0, 0, 65537, 128, 65536, 65535, 0, 0, 1, 0},
};

static const struct tail_case tail_cases[] = {
    {"tail-0-0", 0, 0, 0, 0, 0, 0, 0, 1},
    {"tail-0-65535", 0, 65535, 65535, 0, 65535, 0, 0, 1},
    {"tail-1-0", 1, 0, 0, 0, 1, 0, 0, 1},
    {"tail-1-65535", 1, 65535, 65535, 0, 65536, 0, 0, 1},
    {"tail--1-0", -1, 0, 0, 0, 0, 0, 1, 0},
    {"tail--1-65535", -1, 65535, 65535, 0, 65534, 0, 0, 1},
    {"tail-16777214-0", 16777214, 0, 0, 0, 16777214, 0, 0, 1},
    {"tail-16777214-65535", 16777214, 65535, 65535, 0, 16777215, 0, 0, 1},
    {"tail-16777215-0", 16777215, 0, 0, 0, 16777215, 0, 0, 1},
    {"tail-16777215-65535", 16777215, 65535, 65535, 0, 16777215, 0, 0, 1},
    {"tail-16777216-0", 16777216, 0, 0, 0, 16777215, 0, 0, 1},
    {"tail-16777216-65535", 16777216, 65535, 65535, 0, 16777215, 0, 0, 1},
    {"tail--16777214-0", -16777214, 0, 0, 0, 0, 0, 65535, 0},
    {"tail--16777214-65535", -16777214, 65535, 65535, 0, 0, 0, 65535, 0},
    {"tail--16777215-0", -16777215, 0, 0, 0, 0, 0, 65535, 0},
    {"tail--16777215-65535", -16777215, 65535, 65535, 0, 0, 0, 65535, 0},
    {"tail--16777216-0", -16777216, 0, 0, 0, 0, 0, 65535, 0},
    {"tail--16777216-65535", -16777216, 65535, 65535, 0, 0, 0, 65535, 0},
    {"tail-2147483647-0", 2147483647, 0, 0, 0, 16777215, 0, 0, 1},
    {"tail-2147483647-65535", 2147483647, 65535, 65535, 0, 16777215, 0, 0, 1},
    {"tail--2147483648-0", -2147483648, 0, 0, 0, 0, 0, 65535, 0},
    {"tail--2147483648-65535", -2147483648, 65535, 65535, 0, 0, 0, 65535, 0},
};

struct window { uint32_t start; size_t size; uint8_t before[0x60]; };
static struct window windows[] = {
    {0xffff1de0U, 0x60, {0}}, {0xffff2440U, 0x20, {0}},
    {0xffff24b0U, 0x10, {0}}, {0xffff2460U, 0x10, {0}},
    {0xffff43c0U, 0x20, {0}},
};

static volatile uint8_t *ram(uint32_t address)
{
    return (volatile uint8_t *)(uintptr_t)(TEST_RAM_BASE + (address & 0xffffU));
}

static uint32_t bank_address(uint32_t bank, uint32_t first, uint32_t second)
{
    return bank ? second : first;
}

static void set_word(uint32_t address, uint16_t value)
{
    *(volatile uint16_t *)ram(address) = value;
}

static void set_longword(uint32_t address, uint32_t value)
{
    *(volatile uint32_t *)ram(address) = value;
}

static void prepare(const struct contribution_case *test, uint32_t bank)
{
    size_t w, byte;
    for (w = 0; w < ARRAY_SIZE(windows); ++w)
        for (byte = 0; byte < windows[w].size; ++byte)
            ram(windows[w].start)[byte] = (uint8_t)(37U * byte + 17U * w + 11U);
    set_word(bank_address(bank, MAF_INPUT_B1, MAF_INPUT_B2), test->input);
    set_word(bank_address(bank, BASE_B1, BASE_B2), 0xa55a);
    set_word(bank_address(bank, REFERENCE_B1, REFERENCE_B2), test->reference);
    set_word(bank_address(bank, DELTA_B1, DELTA_B2), test->delta);
    set_word(bank_address(bank, CORRECTION_B1, CORRECTION_B2), (uint16_t)test->correction);
    set_word(bank_address(bank, MAGNITUDE_B1, MAGNITUDE_B2), test->magnitude);
    set_longword(bank_address(bank, FALLBACK_B1, FALLBACK_B2), test->fallback);
    set_longword(bank_address(bank, MAF_OUTPUT_B1, MAF_OUTPUT_B2), 0xdeadbeefU);
    ram(SIGN_FLAGS)[0] = (uint8_t)(0xacU | (bank ? 1U : 2U)
                                | (test->positive ? bank + 1U : 0U));
    ram(ENABLE_FLAGS)[0] = test->enable;
    ram(DIAGNOSTIC_FLAGS)[0] = test->diagnostic;
    ram(INHIBIT_FLAGS)[0] = test->inhibit;
    ram(bank_address(bank, LATCH_B1, LATCH_B2))[0] = test->latch;
    *(volatile uint8_t *)(uintptr_t)FALLBACK_WEIGHT_ADDRESS = test->weight;
    for (w = 0; w < ARRAY_SIZE(windows); ++w)
        for (byte = 0; byte < windows[w].size; ++byte)
            windows[w].before[byte] = ram(windows[w].start)[byte];
}

static int fail(const char *name, uint32_t bank, const char *field,
                uint32_t actual, uint32_t expected)
{
    printf("VQ_SH_ELF_STOCK_CODE status=FAIL case=%s bank=%lu field=%s actual=%08lx expected=%08lx\n",
           name, (unsigned long)bank, field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}

static int check(const struct contribution_case *test, uint32_t bank, uint32_t result,
                 const uint32_t *state, uint32_t macl, int intermediate)
{
    const uint32_t changed[] = {
        bank_address(bank, MAF_OUTPUT_B1, MAF_OUTPUT_B2),
        bank_address(bank, BASE_B1, BASE_B2),
        bank_address(bank, CORRECTION_B1, CORRECTION_B2),
        bank_address(bank, MAGNITUDE_B1, MAGNITUDE_B2), SIGN_FLAGS,
        bank_address(bank, LATCH_B1, LATCH_B2),
    };
    const uint32_t sizes[] = {4, intermediate ? 0U : 2U, 2, 2, 1, 1};
    const uint32_t expected[] = {
        test->output, test->base, (uint16_t)test->correction_after, test->magnitude_after,
        0xacU | (bank ? 1U : 2U) | (test->positive_after ? bank + 1U : 0U), test->latch_after,
    };
    size_t index, w, byte;
    for (index = 0; index < ARRAY_SIZE(changed); ++index) {
        uint32_t actual;
        if (sizes[index] == 0)
            continue;
        actual = sizes[index] == 4 ? *(volatile uint32_t *)ram(changed[index])
               : sizes[index] == 2 ? *(volatile uint16_t *)ram(changed[index])
               : ram(changed[index])[0];
        if (actual != expected[index])
            return fail(test->name, bank, "output-base-correction-residual-sign-latch", actual, expected[index]);
    }
    if (result != bank * 2U)
        return fail(test->name, bank, "return-offset", result, bank * 2U);
    if (state[0] != macl || state[1] != 0x10203040U || state[2] != 0x13579bdfU
        || state[3] != 0x2468ace0U || state[4] != 0x13572468U)
        return fail(test->name, bank, "saved-registers-macl-gbr", 1, 0);
    for (index = 0; index < 3; ++index) {
        const uint8_t coefficients[] = {77, 12, 255};
        if (*(const volatile uint8_t *)(uintptr_t)(COEFFICIENT_ADDRESS + index) != coefficients[index])
            return fail(test->name, bank, "read-only-coefficient", 1, 0);
    }
    if (*(const volatile uint8_t *)(uintptr_t)(COEFFICIENT_ADDRESS + 7U) != 45
        || *(const volatile uint8_t *)(uintptr_t)FALLBACK_WEIGHT_ADDRESS != test->weight)
        return fail(test->name, bank, "read-only-base-or-fallback-coefficient", 1, 0);
    for (w = 0; w < ARRAY_SIZE(windows); ++w)
        for (byte = 0; byte < windows[w].size; ++byte) {
            uint32_t address = windows[w].start + (uint32_t)byte;
            int allowed = 0;
            for (index = 0; index < ARRAY_SIZE(changed); ++index)
                if (address >= changed[index] && address - changed[index] < sizes[index])
                    allowed = 1;
            if (!allowed && ram(address)[0] != windows[w].before[byte])
                return fail(test->name, bank, "read-only-input-sibling-mode-neighbor", address, 0);
        }
    return 1;
}

static int run_case(const struct contribution_case *test, uint32_t argument, uint32_t macl)
{
    uint32_t bank = argument & 0xffU, state[5], result;
    prepare(test, bank);
    result = stock_invoke_compensation(REGION_ENTRY, argument, macl, state);
    return check(test, bank, result, state, macl, 0);
}

static int run_tail(const struct tail_case *test, uint32_t bank)
{
    struct contribution_case context = contribution_cases[0];
    uint32_t state[5], result;
    const uint32_t registers[] = {
        (uint32_t)(uintptr_t)ram(CONTRIBUTION_BASE), (uint32_t)test->residual, test->base, MACL_SEED,
    };
    context.name = test->name;
    context.delta = test->delta;
    context.correction = test->correction;
    context.output = test->output;
    context.correction_after = test->correction_after;
    context.magnitude_after = test->magnitude_after;
    context.positive_after = test->positive_after;
    prepare(&context, bank);
    result = stock_invoke_contribution_tail(TAIL_ENTRY, bank, registers, state);
    return check(&context, bank, result, state, MACL_SEED, 1);
}

static int run_sequence(uint32_t bank)
{
    static const uint32_t outputs[] = {5782, 5939, 6094, 6249, 6403};
    static const int16_t corrections[] = {131, 261, 390, 519, 647};
    struct contribution_case context = contribution_cases[0];
    uint32_t state[5], result;
    size_t index;
    prepare(&context, bank);
    for (index = 0; index < ARRAY_SIZE(outputs); ++index) {
        uint32_t macl = MACL_SEED ^ (uint32_t)index;
        result = stock_invoke_compensation(REGION_ENTRY, bank, macl, state);
        context.output = outputs[index];
        context.correction_after = corrections[index];
        if (!check(&context, bank, result, state, macl, 0))
            return 0;
    }
    return 1;
}

int main(void)
{
    size_t index, cases = 0;
    uint32_t bank;
    for (index = 0; index < ARRAY_SIZE(contribution_cases); ++index)
        for (bank = 0; bank < 2; ++bank) {
            if (!run_case(contribution_cases + index, bank, MACL_SEED ^ (uint32_t)index))
                return 1;
            ++cases;
        }
    for (index = 0; index < ARRAY_SIZE(tail_cases); ++index)
        for (bank = 0; bank < 2; ++bank) {
            if (!run_tail(tail_cases + index, bank))
                return 1;
            ++cases;
        }
    for (bank = 0; bank < 2; ++bank) {
        if (!run_case(contribution_cases, bank + 0x100U, MACL_SEED) || !run_sequence(bank))
            return 1;
        cases += 6;
    }
    *(volatile uint8_t *)(uintptr_t)FALLBACK_WEIGHT_ADDRESS = 128;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY,
           (unsigned long)cases);
    return 0;
}
