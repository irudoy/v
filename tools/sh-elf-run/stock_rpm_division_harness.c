#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U
#define WINDOW_START 0xffff1180U
#define WINDOW_SIZE 0x90U
#define FAULT_SEED 0xa55ac33cU

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(MODE_FLAGS) \
    || !defined(EVENT_INTERVAL) || !defined(ENGINE_SPEED) \
    || !defined(DIVIDER_ENTRY) \
    || !defined(FAULT_POINTER) || !defined(FAULT_VALUE)
#error "the verifier defines the stock region, meanings, and divider pools"
#endif

extern uint32_t stock_invoke(uint32_t entry, uint32_t r12, uint32_t r0);
extern uint32_t stock_invoke_r1(uint32_t entry, uint32_t r1, uint32_t r0);

struct stock_case {
    const char *name;
    uint32_t interval;
    uint8_t flags;
    uint16_t speed;
    uint8_t fault;
};

static const struct stock_case stock_cases[] = {
    {"zero-interval-records-fault", 0, 0, 0, 1},
    {"inhibited-zero-skips-divider", 0, 0x20, 0, 0},
    {"inhibited-nonzero", 6250, 0x20, 0, 0},
    {"inhibited-all-flags", 6250, 0xff, 0, 0},
    {"other-bits-allow-division", 6250, 0xdf, 5120, 0},
    {"unit-divisor-saturates", 1, 0, 65535, 0},
    {"two-count-divisor-saturates", 2, 0, 65535, 0},
    {"below-unsaturated-boundary", 488, 0, 65535, 0},
    {"first-unsaturated-interval", 489, 0, 65439, 0},
    {"fractional-quotient", 833, 0, 38415, 0},
    {"exact-quotient", 2500, 0, 12800, 0},
    {"normal-event-interval", 6250, 0, 5120, 0},
    {"maximum-word-divisor", 65535, 0, 488, 0},
    {"first-long-divisor", 65536, 0, 488, 0},
    {"high-bit-divisor", 0x80000000U, 0, 0, 0},
    {"maximum-long-divisor", 0xffffffffU, 0, 0, 0},
};

struct divider_case {
    const char *name;
    uint32_t numerator;
    uint32_t denominator;
    uint32_t quotient;
    uint8_t fault;
};

/* The producer's fixed dividend cannot enter the short-quotient branch.
   Direct entries cover that branch and the full unsigned return range. */
static const struct divider_case divider_cases[] = {
    {"short-quotient", 255000, 1000, 255, 0},
    {"word-quotient-boundary", 256000, 1000, 256, 0},
    {"maximum-unsigned-quotient", 0xffffffffU, 1, 0xffffffffU, 0},
    {"direct-zero-divisor", 123, 0, 0, 1},
};

static uint8_t before[WINDOW_SIZE];

static volatile uint8_t *ram_pointer(uint32_t original)
{
    return (volatile uint8_t *)(uintptr_t)(TEST_RAM_BASE + (original & 0xffffU));
}

static int fail_value(
    const char *name, const char *field, uint32_t actual, uint32_t expected)
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

    for (index = 0; index < WINDOW_SIZE; ++index)
        ram_pointer(WINDOW_START)[index] = (uint8_t)(37U * index + 11U);
    *(volatile uint32_t *)ram_pointer(EVENT_INTERVAL) = test->interval;
    *(volatile uint16_t *)ram_pointer(ENGINE_SPEED) = 0xa55a;
    ram_pointer(MODE_FLAGS)[0] = test->flags;
    fault[0] = FAULT_SEED;
    for (index = 0; index < WINDOW_SIZE; ++index)
        before[index] = ram_pointer(WINDOW_START)[index];
    stock_invoke(REGION_ENTRY, 0, 0);
    if (*(volatile uint16_t *)ram_pointer(ENGINE_SPEED) != test->speed)
        return fail_value(test->name, "speed",
                          *(volatile uint16_t *)ram_pointer(ENGINE_SPEED), test->speed);
    if (ram_pointer(MODE_FLAGS)[0] != test->flags)
        return fail_value(test->name, "mode-flags", ram_pointer(MODE_FLAGS)[0], test->flags);
    if (fault[0] != expected_fault)
        return fail_value(test->name, "fault-record", fault[0], expected_fault);
    for (index = 0; index < WINDOW_SIZE; ++index) {
        uint32_t address = WINDOW_START + (uint32_t)index;
        if (address == ENGINE_SPEED || address == ENGINE_SPEED + 1U)
            continue;
        if (ram_pointer(address)[0] != before[index])
            return fail_value(test->name, "write-window", address, before[index]);
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
