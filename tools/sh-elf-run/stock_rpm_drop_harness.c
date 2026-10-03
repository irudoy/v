#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(DROP_WORD) \
    || !defined(CURRENT_SPEED) || !defined(HISTORY_SPEED) \
    || !defined(PREVIOUS_DROP) || !defined(DROP_COEFFICIENT)
#error "the verifier defines the stock region, meaning addresses, and coefficient"
#endif

extern uint32_t stock_invoke_gbr(
    uint32_t entry, uint32_t r12, uint32_t r0, uint32_t gbr);

struct stock_case {
    const char *name;
    uint16_t history;
    uint16_t current;
    uint16_t previous;
    uint16_t expected;
};

/* Expected values are reviewed literals, independent of the recurrence in
   the meaning and specification. Rising speed clears nonzero history. */
static const struct stock_case stock_cases[] = {
    {"rising-with-history", 100, 101, 256, 0},
    {"rising-high-word", 0x8000, 0xffff, 0xffff, 0},
    {"rising-from-zero", 0, 1, 0xffff, 0},
    {"equal-with-zero-history", 0, 0, 0, 0},
    {"equal-with-history", 100, 100, 256, 192},
    {"equal-truncates-history", 100, 100, 1, 0},
    {"equal-high-word", 0xffff, 0xffff, 0xffff, 49151},
    {"one-count-drop", 101, 100, 0, 64},
    {"one-count-drop-with-history", 101, 100, 256, 256},
    {"drop-truncates-history", 101, 100, 3, 66},
    {"below-saturation", 1023, 0, 0, 65472},
    {"at-saturation", 1024, 0, 0, 65535},
    {"history-reaches-saturation", 1000, 0, 2048, 65535},
    {"maximum-drop", 65535, 0, 65535, 65535},
};

static const uint32_t windows[] = {DROP_WORD - 4U, CURRENT_SPEED - 4U,
                                  HISTORY_SPEED - 4U};
static uint8_t before[ARRAY_SIZE(windows)][16];

static volatile uint8_t *ram_pointer(uint32_t original)
{
    return (volatile uint8_t *)(uintptr_t)(
        TEST_RAM_BASE + (original & 0xffffU));
}

static volatile uint16_t *ram_word(uint32_t original)
{
    return (volatile uint16_t *)ram_pointer(original);
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
    size_t window, offset;
    uint32_t result;

    for (window = 0; window < ARRAY_SIZE(windows); ++window)
        for (offset = 0; offset < 16; ++offset)
            ram_pointer(windows[window])[offset] = (uint8_t)(37U * offset + 11U);
    ram_word(DROP_WORD)[0] = 0xa55a;
    ram_word(CURRENT_SPEED)[0] = test->current;
    ram_word(HISTORY_SPEED)[0] = test->history;
    ram_word(PREVIOUS_DROP)[0] = test->previous;
    for (window = 0; window < ARRAY_SIZE(windows); ++window)
        for (offset = 0; offset < 16; ++offset)
            before[window][offset] = ram_pointer(windows[window])[offset];

    result = stock_invoke_gbr(
        REGION_ENTRY, 0, 0, (uint32_t)(uintptr_t)ram_pointer(DROP_WORD));
    if (ram_word(DROP_WORD)[0] != test->expected)
        return fail_value(test->name, "drop", ram_word(DROP_WORD)[0], test->expected);
    if (result != test->expected)
        return fail_value(test->name, "result", result, test->expected);
    for (window = 0; window < ARRAY_SIZE(windows); ++window) {
        for (offset = 0; offset < 16; ++offset) {
            uint32_t address = windows[window] + (uint32_t)offset;
            if (address == DROP_WORD || address == DROP_WORD + 1U)
                continue;
            if (ram_pointer(address)[0] != before[window][offset])
                return fail_value(test->name, "write-window", address,
                                  before[window][offset]);
        }
    }
    return 1;
}

int main(void)
{
    size_t index;
    uint8_t coefficient = *(const volatile uint8_t *)(uintptr_t)DROP_COEFFICIENT;
    if (coefficient != 64)
        return !fail_value("calibration", "coefficient", coefficient, 64);
    for (index = 0; index < ARRAY_SIZE(stock_cases); ++index)
        if (!run_case(&stock_cases[index]))
            return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",
           REGION_KEY, (unsigned long)ARRAY_SIZE(stock_cases));
    return 0;
}
