#include <stdio.h>

#include "stock_crank_period.h"

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U

#if !defined(REGION_KEY) || !defined(NORMALIZATION_ENTRY) || !defined(TOOTH_COUNTER) \
    || !defined(RAW_PERIOD) || !defined(NORMALIZED_PERIOD) || !defined(REFERENCE_PERIOD) \
    || !defined(CRANK_BASE) || !defined(CORE_BASE) || !defined(SYNC_MASK)
#error "the verifier defines the normalization entry and period symbols"
#endif

struct stock_case {
    const char *name;
    uint8_t sync, tooth;
    uint16_t period;
    uint32_t reference;
    uint16_t normalized, reference_after;
};

static const struct stock_case stock_cases[] = {
    {"unsynchronized-tooth-eight", 0, 8, 3, 6, 3, 6},
    {"synchronized-tooth-seven", 0x80, 7, 3, 6, 3, 6},
    {"synchronized-tooth-nine", 0x80, 9, 3, 6, 3, 6},
    {"first-positive-multiple", 0x80, 8, 3, 6, 0, 1},
    {"zero-period", 0x80, 8, 0, 0, 0, 0},
    {"below-first-multiple", 0x80, 8, 2, 3, 0, 0},
    {"above-first-multiple", 0x80, 8, 4, 5, 1, 1},
    {"second-multiple", 0x80, 8, 6, 9, 1, 2},
    {"third-multiple", 0x80, 8, 9, 12, 2, 3},
    {"operating-range-multiple", 0x80, 8, 15000, 6000, 4999, 1999},
    {"maximum-word-period", 0x80, 8, 0xffff, 0xffffffffU, 21844, 21844},
    {"unsigned-high-period", 0x80, 8, 0x8000, 0xffff8000U, 10922, 10922},
    {"high-positive-multiple", 0x80, 8, 0x8001, 0xffff8001U, 10922, 10922},
    {"independent-reference", 0x80, 8, 3, 3000, 0, 999},
    {"unsynchronized-reference-truncation", 0, 8, 0xffff, 0xffff0003U, 0xffff, 3},
    {"maximum-counter-byte", 0x80, 0xff, 0xffff, 0xffffffffU, 0xffff, 0xffff},
    {"high-counter-byte", 0x80, 0x88, 3, 0xffff0007U, 3, 7},
    {"zero-counter", 0x80, 0, 120, 240, 120, 240},
    {"unrelated-sync-bits", 0x7f, 8, 6, 9, 6, 9},
    {"synchronized-with-other-bits", 0xff, 8, 6, 9, 1, 2},
};

static volatile uint8_t *ram_pointer(uint32_t original)
{
    return (volatile uint8_t *)(uintptr_t)(TEST_RAM_BASE + (original & 0xffffU));
}

static int fail_value(const char *name, const char *field, uint32_t actual, uint32_t expected)
{
    printf("VQ_SH_ELF_STOCK_CODE status=FAIL case=%s field=%s actual=%08lx expected=%08lx\n",
           name, field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}

static int run_case(const struct stock_case *test)
{
    uint8_t before[0x60], counter_before[0x60];
    size_t index;
    uint32_t result;
    struct crank_period_context context = {
        (uint32_t)(uintptr_t)ram_pointer(CRANK_BASE),
        (uint32_t)(uintptr_t)ram_pointer(CORE_BASE),
        0, test->reference, 0, test->sync & SYNC_MASK, 0,
    };
    for (index = 0; index < sizeof(before); ++index) {
        ram_pointer(0xffff2280U)[index] = (uint8_t)(19U * index + 7U);
        ram_pointer(0xffff1380U)[index] = (uint8_t)(31U * index + 13U);
    }
    *(volatile uint16_t *)ram_pointer(RAW_PERIOD) = test->period;
    *(volatile uint16_t *)ram_pointer(NORMALIZED_PERIOD) = 0xa55a;
    *(volatile uint16_t *)ram_pointer(REFERENCE_PERIOD) = 0x5aa5;
    ram_pointer(TOOTH_COUNTER)[0] = test->tooth;
    for (index = 0; index < sizeof(before); ++index) {
        before[index] = ram_pointer(0xffff2280U)[index];
        counter_before[index] = ram_pointer(0xffff1380U)[index];
    }
    result = stock_invoke_crank_period(NORMALIZATION_ENTRY, &context);
    if (*(volatile uint16_t *)ram_pointer(NORMALIZED_PERIOD) != test->normalized)
        return fail_value(test->name, "normalized",
                          *(volatile uint16_t *)ram_pointer(NORMALIZED_PERIOD), test->normalized);
    if (*(volatile uint16_t *)ram_pointer(REFERENCE_PERIOD) != test->reference_after)
        return fail_value(test->name, "reference",
                          *(volatile uint16_t *)ram_pointer(REFERENCE_PERIOD), test->reference_after);
    if (result != 0x2c8)
        return fail_value(test->name, "return-register", result, 0x2c8);
    for (index = 0; index < sizeof(before); ++index) {
        uint32_t address = 0xffff2280U + (uint32_t)index;
        if (!((address >= NORMALIZED_PERIOD && address < NORMALIZED_PERIOD + 2U)
              || (address >= REFERENCE_PERIOD && address < REFERENCE_PERIOD + 2U))
            && ram_pointer(address)[0] != before[index])
            return fail_value(test->name, "neighbor-period", address, 0);
        if (ram_pointer(0xffff1380U)[index] != counter_before[index])
            return fail_value(test->name, "read-only-counter-window", (uint32_t)index, 0);
    }
    return 1;
}

int main(void)
{
    size_t index;
    for (index = 0; index < ARRAY_SIZE(stock_cases); ++index)
        if (!run_case(&stock_cases[index]))
            return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",
           REGION_KEY, (unsigned long)ARRAY_SIZE(stock_cases));
    return 0;
}
