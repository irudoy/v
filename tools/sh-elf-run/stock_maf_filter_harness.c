#include <stdint.h>
#include <stdio.h>

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(FILTER_ENTRY) \
    || !defined(COPY_CAP_ENTRY) || !defined(ANTI_STALL_ENTRY) \
    || !defined(MAF_SOURCE_B1) || !defined(MAF_SOURCE_B2) \
    || !defined(MAF_WORKING_B1) || !defined(MAF_WORKING_B2) \
    || !defined(MAF_FILTERED_B1) || !defined(MAF_FILTERED_B2) \
    || !defined(MODE_FLAGS) || !defined(COEFFICIENT_ADDRESS) || !defined(FILTER_BASE)
#error "the verifier defines the MAF copy, filter, mode, and bank symbols"
#endif

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U
#define MACL_SEED 0x89abcdefU
#define GBR_SEED 0x13572468U

extern uint32_t stock_invoke_compensation(uint32_t, uint32_t, uint32_t, uint32_t *);
extern uint32_t stock_invoke_working_cap(uint32_t, uint32_t, const void *, uint32_t *);
extern uint32_t stock_invoke_filter_tail(uint32_t, uint32_t, const void *, uint32_t *);

struct copy_case { const char *name; uint16_t input; };
static const struct copy_case copy_cases[] = {
    {"copy-zero", 0}, {"copy-one", 1}, {"copy-bank-one-first", 211},
    {"copy-bank-two-first", 222}, {"copy-last-positive", 32767},
    {"copy-high-unsigned", 32768}, {"copy-before-maximum", 65534},
    {"copy-maximum", 65535},
};

struct cap_case { const char *name; uint32_t input; uint16_t expected; };
static const struct cap_case cap_cases[] = {
    {"cap-zero", 0, 0}, {"cap-last-word", 0xffff, 65535},
    {"cap-above-word", 0x10000, 65535}, {"cap-largest-signed", 0x7fffffffU, 65535},
    {"cap-smallest-signed", 0x80000000U, 0}, {"cap-minus-one", 0xffffffffU, 0},
    {"cap-high-unsigned-word", 0x8000, 32768}, {"cap-negative-wide", 0xffff0000U, 0},
};

struct filter_case {
    const char *name;
    uint8_t flags;
    uint16_t input, previous, expected;
};
static const struct filter_case filter_cases[] = {
    {"copy-zero", 0x00, 0, 65535, 0},
    {"copy-high", 0x00, 65535, 0, 65535},
    {"copy-other-flags", 0xdf, 32768, 1, 32768},
    {"copy-independent", 0x1f, 211, 61744, 211},
    {"weighted-zero", 0x20, 0, 0, 0},
    {"weighted-equal", 0xff, 1000, 1000, 1000},
    {"weighted-rise", 0x20, 1000, 0, 101},
    {"weighted-fall", 0x20, 0, 1000, 898},
    {"rise-one", 0x20, 101, 100, 101},
    {"fall-one", 0x20, 100, 101, 100},
    {"rise-nine", 0x20, 109, 100, 101},
    {"rise-ten", 0x20, 110, 100, 101},
    {"fall-nine", 0x20, 91, 100, 99},
    {"unsigned-rise", 0x20, 65535, 0, 6655},
    {"unsigned-fall", 0x20, 0, 65535, 58879},
    {"high-equal", 0x20, 65535, 65535, 65535},
    {"last-word-rise", 0x20, 65535, 65534, 65535},
    {"last-word-fall", 0x20, 65534, 65535, 65534},
    {"signed-edge-rise", 0x20, 32768, 32767, 32768},
    {"signed-edge-fall", 0x20, 32767, 32768, 32767},
    {"high-word-rise", 0x20, 32768, 0, 3328},
    {"high-word-fall", 0x20, 0, 32768, 29440},
    {"small-first", 0x20, 1, 0, 1},
    {"small-fall", 0x20, 0, 1, 0},
};

struct tail_case {
    const char *name;
    uint16_t input, previous, weighted, expected;
};
static const struct tail_case tail_cases[] = {
    {"tail-rise-one", 1, 0, 0, 1},
    {"tail-rise-last-word", 65535, 65534, 65534, 65535},
    {"tail-fall-one", 0, 1, 1, 0},
    {"tail-fall-signed-edge", 32767, 32768, 32768, 32767},
    {"tail-fall-wide-difference", 0, 65535, 65535, 65534},
    {"tail-equal", 100, 100, 100, 100},
    {"tail-input-equals-weighted", 200, 100, 200, 200},
    {"tail-weighted-changes", 200, 100, 150, 150},
};

struct window { uint32_t start; size_t size; uint8_t before[0x30]; };
static struct window windows[] = {
    {0xffff1048U, 0x30, {0}}, {0xffff1de0U, 0x30, {0}}, {0xffff2460U, 0x10, {0}},
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

static uint32_t source_address(uint32_t bank)
{
    return bank ? MAF_SOURCE_B2 : MAF_SOURCE_B1;
}

static uint32_t working_address(uint32_t bank)
{
    return bank ? MAF_WORKING_B2 : MAF_WORKING_B1;
}

static uint32_t filtered_address(uint32_t bank)
{
    return bank ? MAF_FILTERED_B2 : MAF_FILTERED_B1;
}

static void prepare(uint32_t bank, uint16_t input, uint16_t previous, uint8_t flags, int copy)
{
    size_t index, window_index;
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index)
            ram_pointer(window->start)[index] = (uint8_t)(19U * index + 23U);
    }
    *(volatile uint16_t *)ram_pointer(source_address(bank)) = copy ? input : 0x7abc;
    *(volatile uint16_t *)ram_pointer(working_address(bank)) = copy ? 0xa55a : input;
    *(volatile uint16_t *)ram_pointer(filtered_address(bank)) = previous;
    ram_pointer(MODE_FLAGS)[0] = flags;
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index)
            window->before[index] = ram_pointer(window->start)[index];
    }
}

static int check_result(const char *name, uint32_t output, uint16_t expected,
                        uint32_t result, uint32_t bank, uint32_t macl, uint32_t *state)
{
    size_t index, window_index;
    if (*(volatile uint16_t *)ram_pointer(output) != expected)
        return fail_value(name, "output-word", *(volatile uint16_t *)ram_pointer(output), expected);
    if (result != bank * 2U)
        return fail_value(name, "return-bank-offset", result, bank * 2U);
    if (state[0] != macl || state[1] != 0x10203040U || state[2] != 0x13579bdfU
        || state[3] != 0x2468ace0U || state[4] != GBR_SEED)
        return fail_value(name, "preserved-registers-macl-gbr", 1, 0);
    if (*(const volatile uint8_t *)(uintptr_t)COEFFICIENT_ADDRESS != 26)
        return fail_value(name, "read-only-coefficient", 1, 0);
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index) {
            uint32_t address = window->start + (uint32_t)index;
            if (address >= output && address < output + 2U)
                continue;
            if (ram_pointer(address)[0] != window->before[index])
                return fail_value(name, "read-only-input-flags-sibling-neighbor", address, 0);
        }
    }
    return 1;
}

static int run_copy(const struct copy_case *test, uint32_t bank_argument, uint32_t macl)
{
    uint32_t bank = bank_argument & 1U, result, state[5];
    prepare(bank, test->input, 0x1234, 0xff, 1);
    result = stock_invoke_compensation(REGION_ENTRY, bank_argument, macl, state);
    return check_result(test->name, working_address(bank), test->input, result, bank, macl, state);
}

static int run_filter(const struct filter_case *test, uint32_t bank_argument, uint32_t macl)
{
    uint32_t bank = bank_argument & 1U, result, state[5];
    prepare(bank, test->input, test->previous, test->flags, 0);
    result = stock_invoke_compensation(FILTER_ENTRY, bank_argument, macl, state);
    return check_result(test->name, filtered_address(bank), test->expected, result, bank, macl, state);
}

static int run_cap(const struct cap_case *test, uint32_t bank)
{
    uint32_t result, state[5];
    uint32_t context[] = {(uint32_t)(uintptr_t)ram_pointer(MAF_SOURCE_B1 - 12U), test->input};
    prepare(bank, 0x4321, 0x1234, 0xff, 1);
    result = stock_invoke_working_cap(COPY_CAP_ENTRY, bank, context, state);
    return check_result(test->name, working_address(bank), test->expected,
                        result, bank, MACL_SEED, state);
}

static int run_tail(const struct tail_case *test, uint32_t bank)
{
    uint32_t result, state[5];
    uint32_t context[] = {test->input, test->previous, test->weighted,
                          (uint32_t)(uintptr_t)ram_pointer(FILTER_BASE), MACL_SEED};
    prepare(bank, test->input, test->previous, 0x20, 0);
    result = stock_invoke_filter_tail(ANTI_STALL_ENTRY, bank, context, state);
    return check_result(test->name, filtered_address(bank), test->expected,
                        result, bank, MACL_SEED, state);
}

static int run_sequence(uint32_t bank)
{
    static const uint16_t expected[] = {101, 192, 274, 347, 413};
    uint32_t result, state[5];
    size_t index;
    prepare(bank, 1000, 0, 0x20, 0);
    for (index = 0; index < ARRAY_SIZE(expected); ++index) {
        result = stock_invoke_compensation(FILTER_ENTRY, bank, MACL_SEED, state);
        if (!check_result("five-successive-filter-calls", filtered_address(bank), expected[index],
                          result, bank, MACL_SEED, state))
            return 0;
    }
    return 1;
}

int main(void)
{
    size_t index;
    uint32_t bank;
    for (bank = 0; bank < 2; ++bank) {
        for (index = 0; index < ARRAY_SIZE(copy_cases); ++index)
            if (!run_copy(copy_cases + index, bank, MACL_SEED ^ (uint32_t)index))
                return 1;
        for (index = 0; index < ARRAY_SIZE(cap_cases); ++index)
            if (!run_cap(cap_cases + index, bank))
                return 1;
        for (index = 0; index < ARRAY_SIZE(filter_cases); ++index)
            if (!run_filter(filter_cases + index, bank, MACL_SEED ^ (uint32_t)index))
                return 1;
        for (index = 0; index < ARRAY_SIZE(tail_cases); ++index)
            if (!run_tail(tail_cases + index, bank))
                return 1;
        if (!run_copy(copy_cases + 7, bank + 0x100U, MACL_SEED)
            || !run_filter(filter_cases + 6, bank + 0x100U, MACL_SEED)
            || !run_sequence(bank))
            return 1;
    }
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY,
           (unsigned long)(2U * (ARRAY_SIZE(copy_cases) + ARRAY_SIZE(cap_cases)
                                 + ARRAY_SIZE(filter_cases) + ARRAY_SIZE(tail_cases)) + 14U));
    return 0;
}
