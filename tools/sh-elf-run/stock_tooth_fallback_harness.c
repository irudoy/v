#include <stdio.h>

#include "stock_crank_period.h"

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(EVENT_INTERVAL) \
    || !defined(RAW_PERIOD) || !defined(NORMALIZED_PERIOD) || !defined(CAM_INTERVAL) \
    || !defined(CORE_BASE)
#error "the verifier defines the fallback entry and period symbols"
#endif

struct stock_case {
    const char *name;
    uint32_t interval, previous_interval;
    uint16_t quotient;
};

static const struct stock_case stock_cases[] = {
    {"zero-interval", 0, 120, 0},
    {"below-one-count", 11, 120, 0},
    {"exact-one-count", 12, 0xffffffffU, 1},
    {"truncated-remainder", 13, 1, 1},
    {"short-divider-boundary", 3060, 1, 255},
    {"long-divider-boundary", 3072, 0xffffffffU, 256},
    {"ordinary-interval", 12000, 1, 1000},
    {"last-word-quotient", 786420, 1, 0xffff},
    {"last-word-with-remainder", 786431, 1, 0xffff},
    {"word-quotient-wrap", 786432, 1, 0},
    {"after-word-wrap", 786444, 1, 1},
    {"high-unsigned-interval", 0x80000000U, 0, 0xaaaa},
    {"maximum-unsigned-interval", 0xffffffffU, 0, 0x5555},
};

struct window {
    uint32_t start;
    size_t size;
    uint8_t before[0x60];
};

static struct window windows[] = {
    {0xffff11d0U, 0x60, {0}},
    {0xffff2280U, 0x60, {0}},
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
    size_t index, window_index;
    uint32_t result;
    struct crank_period_context context = {
        0, 0, (uint32_t)(uintptr_t)ram_pointer(CORE_BASE), 0, test->interval, 0,
    };
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index)
            ram_pointer(window->start)[index] = (uint8_t)(23U * index + 17U);
    }
    *(volatile uint32_t *)ram_pointer(EVENT_INTERVAL) = test->previous_interval;
    *(volatile uint32_t *)ram_pointer(0xffff9818U) = 0x55aa33cc;
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index)
            window->before[index] = ram_pointer(window->start)[index];
    }
    result = stock_invoke_crank_period(REGION_ENTRY, &context);
    if (*(volatile uint16_t *)ram_pointer(NORMALIZED_PERIOD) != test->quotient)
        return fail_value(test->name, "normalized-word",
                          *(volatile uint16_t *)ram_pointer(NORMALIZED_PERIOD), test->quotient);
    if (*(volatile uint16_t *)ram_pointer(RAW_PERIOD) != test->quotient)
        return fail_value(test->name, "raw-word",
                          *(volatile uint16_t *)ram_pointer(RAW_PERIOD), test->quotient);
    if (*(volatile uint32_t *)ram_pointer(EVENT_INTERVAL) != test->interval
        || *(volatile uint32_t *)ram_pointer(CAM_INTERVAL) != test->interval)
        return fail_value(test->name, "published-new-interval", 1, 0);
    if (*(volatile uint32_t *)ram_pointer(0xffff9818U) != 0x55aa33cc)
        return fail_value(test->name, "read-only-fault-record", 1, 0);
    if (result != 0x2c6)
        return fail_value(test->name, "return-register", result, 0x2c6);
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index) {
            uint32_t address = window->start + (uint32_t)index;
            if ((address >= EVENT_INTERVAL && address < EVENT_INTERVAL + 4U)
                || (address >= CAM_INTERVAL && address < CAM_INTERVAL + 4U)
                || (address >= RAW_PERIOD && address < RAW_PERIOD + 2U)
                || (address >= NORMALIZED_PERIOD && address < NORMALIZED_PERIOD + 2U))
                continue;
            if (ram_pointer(address)[0] != window->before[index])
                return fail_value(test->name, "neighbor-period", address, 0);
        }
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
