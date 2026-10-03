#include <stdio.h>

#include "stock_crank_period.h"

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(OSBR1) \
    || !defined(CRANK_CAPTURE) || !defined(RAW_PERIOD) || !defined(CAPTURE_FLAGS) \
    || !defined(INIT_MASK) || !defined(CRANK_BASE) || !defined(CORE_BASE) \
    || !defined(MMIO_BASE) || !defined(REFERENCE_PERIOD)
#error "the verifier defines the capture entry, symbols, and initialization bit"
#endif

struct stock_case {
    const char *name;
    uint16_t current, previous, interval;
    uint8_t flags, flags_after;
};

static const struct stock_case stock_cases[] = {
    {"first-zero-capture", 0, 120, 0xffff, 0, 0x40},
    {"first-maximum-capture", 0xffff, 0, 0xffff, 0, 0x40},
    {"first-capture-preserves-flags", 0x8000, 0x7fff, 0xffff, 0xbf, 0xff},
    {"first-capture-with-unrelated-bit", 1234, 1230, 0xffff, 0x01, 0x41},
    {"ordinary-capture", 1200, 200, 1000, 0x40, 0x40},
    {"equal-captures", 1234, 1234, 0, 0x40, 0x40},
    {"zero-captures", 0, 0, 0, 0xff, 0xff},
    {"maximum-captures", 0xffff, 0xffff, 0, 0x40, 0x40},
    {"word-wrap-one-count", 0, 0xffff, 1, 0x40, 0x40},
    {"word-wrap-ordinary", 200, 0xff00, 456, 0x40, 0x40},
    {"signed-boundary-forward", 0x8000, 0x7fff, 1, 0x40, 0x40},
    {"signed-boundary-backward", 0x7fff, 0x8000, 0xffff, 0x40, 0x40},
    {"maximum-forward-difference", 0xffff, 0, 0xffff, 0x40, 0x40},
    {"high-half-interval", 0x8000, 0, 0x8000, 0x40, 0x40},
    {"high-half-previous", 0, 0x8000, 0x8000, 0x40, 0x40},
    {"initialized-preserves-flags", 601, 600, 1, 0xff, 0xff},
};

struct window {
    uint32_t start;
    size_t size;
    uint8_t before[0x60];
};

static struct window windows[] = {
    {0xffff1560U, 0x60, {0}},
    {0xffff2280U, 0x60, {0}},
    {0xffff24a0U, 0x60, {0}},
    {0xfffff430U, 0x60, {0}},
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
        (uint32_t)(uintptr_t)ram_pointer(CRANK_BASE),
        (uint32_t)(uintptr_t)ram_pointer(CORE_BASE), 0, 0, 0, 0,
        (uint32_t)(uintptr_t)ram_pointer(MMIO_BASE),
    };
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index)
            ram_pointer(window->start)[index] = (uint8_t)(29U * index + 11U);
    }
    *(volatile uint16_t *)ram_pointer(OSBR1) = test->current;
    *(volatile uint16_t *)ram_pointer(CRANK_CAPTURE) = test->previous;
    *(volatile uint16_t *)ram_pointer(RAW_PERIOD) = 0xa55a;
    *(volatile uint16_t *)ram_pointer(REFERENCE_PERIOD) = 0x5aa5;
    ram_pointer(CAPTURE_FLAGS)[0] = test->flags;
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index)
            window->before[index] = ram_pointer(window->start)[index];
    }
    result = stock_invoke_crank_period(REGION_ENTRY, &context);
    if (*(volatile uint16_t *)ram_pointer(CRANK_CAPTURE) != test->current)
        return fail_value(test->name, "capture-store", 1, 0);
    if (*(volatile uint16_t *)ram_pointer(RAW_PERIOD) != test->interval
        || *(volatile uint16_t *)ram_pointer(REFERENCE_PERIOD) != test->interval)
        return fail_value(test->name, "interval-word-stores", 1, 0);
    if (ram_pointer(CAPTURE_FLAGS)[0] != test->flags_after)
        return fail_value(test->name, "initialization-flags", ram_pointer(CAPTURE_FLAGS)[0], test->flags_after);
    if ((test->flags_after & INIT_MASK) == 0)
        return fail_value(test->name, "initialized-bit", test->flags_after, INIT_MASK);
    if (result != 0x2c6)
        return fail_value(test->name, "return-register", result, 0x2c6);
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index) {
            uint32_t address = window->start + (uint32_t)index;
            if ((address >= CRANK_CAPTURE && address < CRANK_CAPTURE + 2U)
                || (address >= RAW_PERIOD && address < RAW_PERIOD + 2U)
                || (address >= REFERENCE_PERIOD && address < REFERENCE_PERIOD + 2U)
                || address == CAPTURE_FLAGS)
                continue;
            if (ram_pointer(address)[0] != window->before[index])
                return fail_value(test->name, "neighbor-or-mmio", address, 0);
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
