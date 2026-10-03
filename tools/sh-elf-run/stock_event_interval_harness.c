#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U
#define INTERVAL_SEED 0xa55ac33cU

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(MODE_FLAGS) \
    || !defined(CURRENT_CAPTURE) || !defined(PREVIOUS_CAPTURE) \
    || !defined(EVENT_INTERVAL) || !defined(HOLDOFF) || !defined(PUBLISHED_FLAGS)
#error "the verifier defines the event-interval symbols and selector"
#endif

extern uint32_t stock_invoke_r1(uint32_t entry, uint32_t r1, uint32_t r0);

struct stock_case {
    const char *name;
    uint32_t current, previous;
    uint8_t flags, holdoff, marker;
    uint32_t interval, previous_after;
    uint8_t marker_after;
    uint32_t result;
};

static const struct stock_case stock_cases[] = {
    {"normal-event", 201000, 1000, 0, 0, 0, 6250, 201000, 0x20, 201000},
    {"fractional-count", 1033, 1000, 0, 0, 0, 1, 1033, 0x20, 1033},
    {"below-one-count", 1031, 1000, 0, 0, 0, 0, 1031, 0x20, 1031},
    {"exact-one-count", 1032, 1000, 0, 0, 0, 1, 1032, 0x20, 1032},
    {"equal-captures", 1000, 1000, 0, 0, 0, 0, 1000, 0x20, 1000},
    {"maximum-nonwrapping-difference", 0xffffffffU, 0, 0, 0, 0,
        0x07ffffff, 0xffffffffU, 0x20, 0xffffffffU},
    {"unsigned-high-captures", 0x80000120U, 0x80000000U, 0, 0, 0xdf,
        9, 0x80000120U, 0xff, 0x80000120U},
    {"wrap-at-maximum", 0, 0xffffffffU, 0, 0, 1, 0, 0, 0x21, 0},
    {"wrap-below-one-count", 0, 0xffffffe0U, 0, 0, 0, 0, 0, 0x20, 0},
    {"wrap-exact-one-count", 0, 0xffffffdfU, 0, 0, 0, 1, 0, 0x20, 0},
    {"wide-wrap", 0x100, 0xf0000000U, 0, 0, 0, 0x00800007, 0x100, 0x20, 0x100},
    {"maximum-wrapping-difference", 0, 1, 0, 0, 0, 0x07ffffff, 0, 0x20, 0},
    {"holdoff-selects-invalid-interval", 500, 400, 0, 1, 0x21,
        0xffffffffU, 500, 0x21, 500},
    {"maximum-holdoff", 0, 100, 0xdf, 0xff, 0x80, 0xffffffffU, 0, 0x80, 0},
    {"diagnostic-mode-preserves-state", 500, 400, 0x20, 0, 0x80,
        INTERVAL_SEED, 400, 0x80, 0x20},
    {"diagnostic-mode-skips-holdoff", 500, 400, 0xff, 1, 1,
        INTERVAL_SEED, 400, 1, 0xffffffffU},
    {"unrelated-mode-bits", 201000, 1000, 0xdf, 0, 0xa5,
        6250, 201000, 0xa5, 201000},
    {"diagnostic-zero-captures", 0, 0, 0x20, 0, 0,
        INTERVAL_SEED, 0, 0, 0x20},
};

struct window {
    uint32_t start, changed;
    size_t size;
    uint8_t before[0x90];
};

static struct window windows[] = {
    {0xffff1180U, EVENT_INTERVAL, 0x90, {0}},
    {0xffff1840U, 0, 0x30, {0}},
    {0xffff84c0U, PREVIOUS_CAPTURE, 0x20, {0}},
};

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
    size_t index, window_index;
    uint32_t result;
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index)
            ram_pointer(window->start)[index] = (uint8_t)(37U * index + 11U);
    }
    *(volatile uint32_t *)ram_pointer(CURRENT_CAPTURE) = test->current;
    *(volatile uint32_t *)ram_pointer(PREVIOUS_CAPTURE) = test->previous;
    *(volatile uint32_t *)ram_pointer(EVENT_INTERVAL) = INTERVAL_SEED;
    ram_pointer(MODE_FLAGS)[0] = test->flags;
    ram_pointer(HOLDOFF)[0] = test->holdoff;
    ram_pointer(PUBLISHED_FLAGS)[0] = test->marker;
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index)
            window->before[index] = ram_pointer(window->start)[index];
    }
    result = stock_invoke_r1(REGION_ENTRY,
                            (uint32_t)(uintptr_t)ram_pointer(PREVIOUS_CAPTURE), 0);
    if (*(volatile uint32_t *)ram_pointer(EVENT_INTERVAL) != test->interval)
        return fail_value(test->name, "interval",
                          *(volatile uint32_t *)ram_pointer(EVENT_INTERVAL), test->interval);
    if (*(volatile uint32_t *)ram_pointer(PREVIOUS_CAPTURE) != test->previous_after)
        return fail_value(test->name, "previous",
                          *(volatile uint32_t *)ram_pointer(PREVIOUS_CAPTURE), test->previous_after);
    if (ram_pointer(PUBLISHED_FLAGS)[0] != test->marker_after)
        return fail_value(test->name, "marker", ram_pointer(PUBLISHED_FLAGS)[0], test->marker_after);
    if (result != test->result)
        return fail_value(test->name, "return", result, test->result);
    if (ram_pointer(MODE_FLAGS)[0] != test->flags || ram_pointer(HOLDOFF)[0] != test->holdoff)
        return fail_value(test->name, "read-only-selectors", 1, 0);
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index) {
            uint32_t address = window->start + (uint32_t)index;
            if (window->changed && address >= window->changed && address < window->changed + 4U)
                continue;
            if (ram_pointer(address)[0] != window->before[index])
                return fail_value(test->name, "write-window", address, window->before[index]);
        }
    }
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
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",
           REGION_KEY, (unsigned long)passed);
    return 0;
}
