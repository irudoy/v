#include <stdint.h>
#include <stdio.h>

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(MAF_BANK1) \
    || !defined(MAF_BANK2) || !defined(MAF_CORRECTION) \
    || !defined(MAF_AUXILIARY) || !defined(MAF_AGGREGATE)
#error "the verifier defines the stock combined MAF symbols"
#endif

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U
#define MACL_SEED 0x89abcdefU
#define GBR_SEED 0x13572468U

extern uint32_t stock_invoke_compensation(uint32_t, uint32_t, uint32_t, uint32_t *);

struct aggregate_case {
    const char *name;
    uint32_t bank1, bank2;
    uint16_t correction, auxiliary;
    uint32_t expected;
};

static const struct aggregate_case aggregate_cases[] = {
    {"zero", 0, 0, 0, 0, 0},
    {"bank-one", 1, 0, 0, 0, 1},
    {"bank-two", 0, 1, 0, 0, 1},
    {"both-banks", 100, 200, 0, 0, 300},
    {"negative-bank-one", 0xffffffffU, 0, 0, 0, 0},
    {"negative-bank-two", 0, 0xffffffffU, 0, 0, 0},
    {"mixed-bank-one", 0xffffffffU, 2, 0, 0, 1},
    {"mixed-bank-two", 2, 0xffffffffU, 0, 0, 1},
    {"largest-positive", 0x7fffffffU, 0, 0, 0, 0x7fffffffU},
    {"smallest-negative", 0x80000000U, 0, 0, 0, 0},
    {"positive-sum-wrap", 0x7fffffffU, 1, 0, 0, 0},
    {"negative-sum-wrap", 0x80000000U, 0xffffffffU, 0, 0, 0x7fffffffU},
    {"two-negative-minus-one", 0xffffffffU, 0xffffffffU, 0, 0, 0},
    {"unsigned-wrap-to-positive", 0xfffffffeU, 4, 0, 0, 2},
    {"two-negative-minima", 0x80000000U, 0x80000000U, 0, 0, 0},
    {"two-positive-maxima", 0x7fffffffU, 0x7fffffffU, 0, 0, 0},
    {"correction-minus-one", 0, 0, 0xffff, 0, 0},
    {"correction-plus-one", 0, 0, 1, 0, 1},
    {"correction-positive-word", 0, 0, 0x7fff, 0, 32767},
    {"correction-negative-word", 0, 0, 0x8000, 0, 0},
    {"correction-cancels-bank", 32768, 0, 0x8000, 0, 0},
    {"correction-below-bank", 32769, 0, 0x8000, 0, 1},
    {"auxiliary-full-word", 0, 0, 0, 0xffff, 65535},
    {"auxiliary-high-bit", 0, 0, 0, 0x8000, 32768},
    {"correction-auxiliary-cancel", 0, 0, 0x8000, 0x8000, 0},
    {"all-inputs", 100, 200, 0xffff, 2, 301},
    {"positive-correction-wrap", 0x7fffffffU, 0, 1, 0, 0},
    {"positive-auxiliary-wrap", 0x7fffffffU, 0, 0, 1, 0},
    {"negative-correction-wrap", 0x80000000U, 0, 0xffff, 0, 0x7fffffffU},
    {"wide-negative-correction-wrap", 0x80000000U, 0, 0x8000, 0, 0x7fff8000U},
    {"sign-after-final-addition", 0x7fff8000U, 0, 0x7fff, 1, 0},
    {"negative-after-unsigned-addition", 0xffff0000U, 0, 0, 0xffff, 0},
};

struct window { uint32_t start; size_t size; uint8_t before[0x58]; };
static struct window windows[] = {
    {0xffff1decU, 0x58, {0}}, {0xffff2360U, 0x10, {0}},
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

static int run_case(const struct aggregate_case *test, uint32_t macl)
{
    uint32_t result, state[5];
    size_t index, window_index;
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index)
            ram_pointer(window->start)[index] = (uint8_t)(index * 19U + 23U);
    }
    *(volatile uint32_t *)ram_pointer(MAF_BANK1) = test->bank1;
    *(volatile uint32_t *)ram_pointer(MAF_BANK2) = test->bank2;
    *(volatile uint16_t *)ram_pointer(MAF_CORRECTION) = test->correction;
    *(volatile uint16_t *)ram_pointer(MAF_AUXILIARY) = test->auxiliary;
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index)
            window->before[index] = ram_pointer(window->start)[index];
    }
    result = stock_invoke_compensation(REGION_ENTRY, 0xa55aU, macl, state);
    if (result != test->expected)
        return fail_value(test->name, "return-value", result, test->expected);
    if (*(volatile uint32_t *)ram_pointer(MAF_AGGREGATE) != test->expected)
        return fail_value(test->name, "stored-longword",
                          *(volatile uint32_t *)ram_pointer(MAF_AGGREGATE), test->expected);
    if (state[0] != macl || state[1] != 0x10203040U || state[2] != 0x13579bdfU
        || state[3] != 0x2468ace0U || state[4] != GBR_SEED)
        return fail_value(test->name, "preserved-registers-macl-gbr", 1, 0);
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index) {
            uint32_t address = window->start + (uint32_t)index;
            if (address >= MAF_AGGREGATE && address < MAF_AGGREGATE + 4U)
                continue;
            if (ram_pointer(address)[0] != window->before[index])
                return fail_value(test->name, "read-only-input-or-output-neighbor", address, 0);
        }
    }
    return 1;
}

int main(void)
{
    size_t index;
    for (index = 0; index < ARRAY_SIZE(aggregate_cases); ++index)
        if (!run_case(aggregate_cases + index, MACL_SEED ^ (uint32_t)index))
            return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",
           REGION_KEY, (unsigned long)ARRAY_SIZE(aggregate_cases));
    return 0;
}
