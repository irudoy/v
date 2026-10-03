#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U
#define HISTORY_WINDOW 0xffff3e20U
#define HISTORY_SIZE 0x30U
#define OUTPUT_WINDOW 0xffff27f8U
#define OUTPUT_SIZE 0x20U
#define FAULT_SEED 0xa55ac33cU

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(MODE_FLAGS) \
    || !defined(TOOTH_PERIOD) || !defined(MEDIAN_OUTPUT) || !defined(LIVE_SPEED) \
    || !defined(HISTORY_NEWEST) || !defined(HISTORY_PREVIOUS) \
    || !defined(HISTORY_OLDER) || !defined(DIVIDER_ENTRY) \
    || !defined(FAULT_POINTER) || !defined(FAULT_VALUE)
#error "the verifier defines the stock median meanings and pools"
#endif

extern uint32_t stock_invoke(uint32_t entry, uint32_t r12, uint32_t r0);
extern uint32_t stock_invoke_r1(uint32_t entry, uint32_t r1, uint32_t r0);

struct stock_case {
    const char *name;
    uint16_t period;
    uint8_t flags, live, newest, previous, older, sample, median, fault;
};

/* Expected values are reviewed literals, including all six strict orders
   of the inserted sample and the two preceding samples. */
static const struct stock_case stock_cases[] = {
    {"low-middle-high", 4166, 0, 77, 20, 30, 99, 10, 20, 0},
    {"low-high-middle", 4166, 0, 77, 30, 20, 99, 10, 20, 0},
    {"middle-low-high", 2083, 0, 77, 10, 30, 99, 20, 20, 0},
    {"middle-high-low", 2083, 0, 77, 30, 10, 99, 20, 20, 0},
    {"high-low-middle", 1388, 0, 77, 10, 20, 99, 30, 20, 0},
    {"high-middle-low", 1388, 0, 77, 20, 10, 99, 30, 20, 0},
    {"new-equals-previous-low", 4166, 0, 77, 10, 30, 99, 10, 10, 0},
    {"new-equals-older-low", 4166, 0, 77, 30, 10, 99, 10, 10, 0},
    {"previous-equals-older-high", 4166, 0, 77, 30, 30, 99, 10, 30, 0},
    {"all-equal", 1000, 0, 77, 41, 41, 99, 41, 41, 0},
    {"new-equals-older-high", 1388, 0, 77, 10, 30, 99, 30, 30, 0},
    {"previous-equals-older-low", 1388, 0, 77, 10, 10, 99, 30, 10, 0},
    {"unsigned-byte-comparisons", 208, 0, 77, 180, 220, 99, 200, 200, 0},
    {"large-period-zero-sample", 65535, 0, 77, 200, 128, 99, 0, 128, 0},
    {"zero-period-retains-nonzero-median", 0, 0, 77, 40, 80, 99, 0, 40, 1},
    {"zero-period-zero-median", 0, 0, 77, 0, 80, 99, 0, 0, 1},
    {"saturated-byte-boundary", 163, 0, 77, 254, 253, 99, 255, 254, 0},
    {"first-unsaturated-byte", 164, 0, 77, 255, 253, 99, 254, 254, 0},
    {"unit-period-saturation", 1, 0, 77, 0, 1, 99, 255, 1, 0},
    {"maximum-byte-tie", 128, 0, 77, 254, 255, 99, 255, 255, 0},
    {"diagnostic-copy-skips-zero-divider", 0, 0x20, 231, 11, 22, 33, 0, 231, 0},
    {"diagnostic-copy-zero", 1, 0xff, 0, 11, 22, 33, 0, 0, 0},
    {"diagnostic-copy-maximum-byte", 65535, 0x20, 255, 11, 22, 33, 0, 255, 0},
    {"unrelated-flags-allow-median", 1000, 0xdf, 77, 42, 43, 99, 41, 42, 0},
};

struct divider_case {
    const char *name;
    uint32_t numerator, denominator, quotient;
    uint8_t fault;
};

static const struct divider_case divider_cases[] = {
    {"short-positive-quotient", 255000, 1000, 255, 0},
    {"word-quotient-boundary", 256000, 1000, 256, 0},
    {"negative-numerator", (uint32_t)-123, 10, (uint32_t)-12, 0},
    {"negative-denominator", 123, (uint32_t)-10, (uint32_t)-12, 0},
    {"both-negative", (uint32_t)-123, (uint32_t)-10, 12, 0},
    {"minimum-signed-numerator", 0x80000000U, 1, 0x80000000U, 0},
    {"large-denominator", 123456789, 100000, 1234, 0},
    {"negative-large-denominator", 123456789, (uint32_t)-100000, (uint32_t)-1234, 0},
    {"negative-large-numerator", (uint32_t)-123456789, 100000, (uint32_t)-1234, 0},
    {"maximum-signed-numerator", 0x7fffffffU, 65536, 32767, 0},
    {"direct-zero-divisor", 123, 0, 0, 1},
};

static uint8_t history_before[HISTORY_SIZE], output_before[OUTPUT_SIZE];

static volatile uint8_t *ram_pointer(uint32_t original)
{
    return (volatile uint8_t *)(uintptr_t)(TEST_RAM_BASE + (original & 0xffffU));
}

static int fail_value(const char *name, const char *field, uint32_t actual, uint32_t expected)
{
    printf("VQ_SH_ELF_STOCK_CODE status=FAIL case=%s field=%s "
           "actual=%08lx expected=%08lx\n", name, field,
           (unsigned long)actual, (unsigned long)expected);
    return 0;
}

static int run_case(const struct stock_case *test)
{
    size_t index;
    volatile uint32_t *fault = (volatile uint32_t *)(uintptr_t)
        *(const volatile uint32_t *)(uintptr_t)FAULT_POINTER;
    uint32_t expected_fault = test->fault
        ? *(const volatile uint32_t *)(uintptr_t)FAULT_VALUE : FAULT_SEED;
    const uint8_t expected_newest = (test->flags & 0x20) ? test->newest : test->sample;
    const uint8_t expected_previous = (test->flags & 0x20) ? test->previous : test->newest;
    const uint8_t expected_older = (test->flags & 0x20) ? test->older : test->previous;

    for (index = 0; index < HISTORY_SIZE; ++index)
        ram_pointer(HISTORY_WINDOW)[index] = (uint8_t)(37U * index + 11U);
    for (index = 0; index < OUTPUT_SIZE; ++index)
        ram_pointer(OUTPUT_WINDOW)[index] = (uint8_t)(53U * index + 7U);
    ram_pointer(HISTORY_NEWEST)[0] = test->newest;
    ram_pointer(HISTORY_PREVIOUS)[0] = test->previous;
    ram_pointer(HISTORY_OLDER)[0] = test->older;
    ram_pointer(MEDIAN_OUTPUT)[0] = 0xa5;
    ram_pointer(MODE_FLAGS)[0] = test->flags;
    ram_pointer(LIVE_SPEED)[0] = test->live;
    *(volatile uint16_t *)ram_pointer(TOOTH_PERIOD) = test->period;
    fault[0] = FAULT_SEED;
    for (index = 0; index < HISTORY_SIZE; ++index)
        history_before[index] = ram_pointer(HISTORY_WINDOW)[index];
    for (index = 0; index < OUTPUT_SIZE; ++index)
        output_before[index] = ram_pointer(OUTPUT_WINDOW)[index];

    stock_invoke(REGION_ENTRY, 0, 0);
    if (ram_pointer(MEDIAN_OUTPUT)[0] != test->median)
        return fail_value(test->name, "median", ram_pointer(MEDIAN_OUTPUT)[0], test->median);
    if (ram_pointer(HISTORY_NEWEST)[0] != expected_newest)
        return fail_value(test->name, "newest", ram_pointer(HISTORY_NEWEST)[0], expected_newest);
    if (ram_pointer(HISTORY_PREVIOUS)[0] != expected_previous)
        return fail_value(test->name, "previous", ram_pointer(HISTORY_PREVIOUS)[0], expected_previous);
    if (ram_pointer(HISTORY_OLDER)[0] != expected_older)
        return fail_value(test->name, "older", ram_pointer(HISTORY_OLDER)[0], expected_older);
    if (ram_pointer(MODE_FLAGS)[0] != test->flags
        || ram_pointer(LIVE_SPEED)[0] != test->live
        || *(volatile uint16_t *)ram_pointer(TOOTH_PERIOD) != test->period)
        return fail_value(test->name, "read-only-inputs", 1, 0);
    if (fault[0] != expected_fault)
        return fail_value(test->name, "fault-record", fault[0], expected_fault);
    for (index = 0; index < HISTORY_SIZE; ++index) {
        uint32_t address = HISTORY_WINDOW + (uint32_t)index;
        if (address == HISTORY_NEWEST || address == HISTORY_PREVIOUS || address == HISTORY_OLDER)
            continue;
        if (ram_pointer(address)[0] != history_before[index])
            return fail_value(test->name, "history-window", address, history_before[index]);
    }
    for (index = 0; index < OUTPUT_SIZE; ++index) {
        uint32_t address = OUTPUT_WINDOW + (uint32_t)index;
        if (address == MEDIAN_OUTPUT)
            continue;
        if (ram_pointer(address)[0] != output_before[index])
            return fail_value(test->name, "output-window", address, output_before[index]);
    }
    return 1;
}

static int run_divider_case(const struct divider_case *test)
{
    volatile uint32_t *fault = (volatile uint32_t *)(uintptr_t)
        *(const volatile uint32_t *)(uintptr_t)FAULT_POINTER;
    uint32_t expected_fault = test->fault
        ? *(const volatile uint32_t *)(uintptr_t)FAULT_VALUE : FAULT_SEED;
    uint32_t result;
    fault[0] = FAULT_SEED;
    result = stock_invoke_r1(DIVIDER_ENTRY, test->numerator, test->denominator);
    if (result != test->quotient)
        return fail_value(test->name, "quotient", result, test->quotient);
    if (fault[0] != expected_fault)
        return fail_value(test->name, "fault-record", fault[0], expected_fault);
    return 1;
}

int main(void)
{
    size_t index, passed = 0;
    for (index = 0; index < ARRAY_SIZE(stock_cases); ++index) {
        if (!run_case(&stock_cases[index]))
            return 1;
        ++passed;
    }
    for (index = 0; index < ARRAY_SIZE(divider_cases); ++index) {
        if (!run_divider_case(&divider_cases[index]))
            return 1;
        ++passed;
    }
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",
           REGION_KEY, (unsigned long)passed);
    return 0;
}
