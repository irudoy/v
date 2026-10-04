#include <stdint.h>
#include <stdio.h>

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(BFS_INPUT) \
    || !defined(LIVE_LOAD) || !defined(REFERENCE_ADDRESS) || !defined(DIVIDER_ENTRY) \
    || !defined(FAULT_ADDRESS)
#error "the verifier defines the BFS input, byte output, reference, and divider"
#endif

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U
#define MACL_SEED 0x89abcdefU
#define FAULT_SEED 0xdeadbeefU

extern uint32_t stock_invoke_normalized_load(uint32_t, uint32_t, uint32_t, uint32_t *);
extern uint32_t stock_invoke_r1(uint32_t, uint32_t, uint32_t);

struct load_case {
    const char *name;
    uint16_t cached, input, reference;
    uint8_t expected;
};
static const struct load_case load_cases[] = {
    {"zero", 0, 0, 27226, 0},
    {"one", 1, 1, 27226, 0},
    {"before-first-count", 212, 212, 27226, 0},
    {"first-count", 213, 213, 27226, 1},
    {"before-second-count", 425, 425, 27226, 1},
    {"second-count", 426, 426, 27226, 2},
    {"small-word", 1000, 1000, 27226, 4},
    {"second-small-word", 2000, 2000, 27226, 9},
    {"below-reference", 10000, 10000, 27226, 47},
    {"near-reference", 20000, 20000, 27226, 94},
    {"before-unity", 27225, 27225, 27226, 127},
    {"unity", 27226, 27226, 27226, 128},
    {"after-unity", 27227, 27227, 27226, 128},
    {"above-reference", 30000, 30000, 27226, 141},
    {"last-signed-word", 32767, 32767, 27226, 154},
    {"high-word-bit", 32768, 32768, 27226, 154},
    {"large-word", 40000, 40000, 27226, 188},
    {"before-cap-range", 50000, 50000, 27226, 235},
    {"last-254", 54239, 54239, 27226, 254},
    {"first-255", 54240, 54240, 27226, 255},
    {"last-unsaturated-quotient", 54451, 54451, 27226, 255},
    {"first-saturated-quotient", 54452, 54452, 27226, 255},
    {"before-maximum-word", 65534, 65534, 27226, 255},
    {"maximum-word", 65535, 65535, 27226, 255},
    {"unit-reference-zero", 0, 0, 1, 0},
    {"unit-reference-one", 1, 1, 1, 128},
    {"unit-reference-cap", 2, 2, 1, 255},
    {"unit-reference-wide-quotient", 65535, 65535, 1, 255},
    {"byte-reference-last", 255, 255, 128, 255},
    {"byte-reference-cap", 256, 256, 128, 255},
    {"high-bit-reference-unity", 32768, 32768, 32768, 128},
    {"high-bit-reference-last", 65535, 65535, 32768, 255},
    {"maximum-reference-below", 65534, 65534, 65535, 127},
    {"maximum-reference-unity", 65535, 65535, 65535, 128},
    {"zero-reference-zero", 0, 0, 0, 0},
    {"zero-reference-high", 65535, 65535, 0, 0},
    {"artificial-cache-caps-zero-ram", 54452, 0, 27226, 255},
    {"artificial-cache-allows-low-byte", 0, 65535, 27226, 52},
};

struct divider_case { const char *name; uint32_t numerator, denominator, expected; };
static const struct divider_case divider_cases[] = {
    {"direct-divider-zero-numerator", 0, 1, 0},
    {"direct-divider-large-quotient", 0x7fffffffU, 1, 0x7fffffffU},
    {"direct-divider-last-word", 0xffffffffU, 0xffffU, 65537},
    {"direct-divider-first-long", 0xffffffffU, 0x10000U, 65535},
    {"direct-divider-high-bit", 0xffffffffU, 0x80000000U, 1},
    {"direct-divider-zero-fault", 0x12345678U, 0, 0},
};

struct window { uint32_t start; size_t size; uint8_t before[0x40]; };
static struct window windows[] = {
    {0xffff1020U, 0x40, {0}}, {0xffff9810U, 0x10, {0}},
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

static void prepare(uint16_t input)
{
    size_t index, window_index;
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index)
            ram_pointer(window->start)[index] = (uint8_t)(index * 19U + 23U);
    }
    *(volatile uint16_t *)ram_pointer(BFS_INPUT) = input;
    *(volatile uint32_t *)ram_pointer(FAULT_ADDRESS) = FAULT_SEED;
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index)
            window->before[index] = ram_pointer(window->start)[index];
    }
}

static int check_memory(const char *name, int writes_output, int zero_divisor)
{
    size_t index, window_index;
    uint32_t expected_fault = zero_divisor ? 0x44eU : FAULT_SEED;
    if (*(volatile uint32_t *)ram_pointer(FAULT_ADDRESS) != expected_fault)
        return fail_value(name, "fault-record", *(volatile uint32_t *)ram_pointer(FAULT_ADDRESS), expected_fault);
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index) {
            uint32_t address = window->start + (uint32_t)index;
            if ((writes_output && address == LIVE_LOAD)
                || (zero_divisor && address >= FAULT_ADDRESS && address < FAULT_ADDRESS + 4U))
                continue;
            if (ram_pointer(address)[0] != window->before[index])
                return fail_value(name, "read-only-input-fault-or-neighbor", address, 0);
        }
    }
    return 1;
}

static int run_load(const struct load_case *test, uint32_t macl)
{
    uint32_t state[6];
    volatile uint16_t *reference = (volatile uint16_t *)(uintptr_t)REFERENCE_ADDRESS;
    uint8_t neighbor = *(volatile uint8_t *)(uintptr_t)(REFERENCE_ADDRESS + 2U);
    prepare(test->input);
    *reference = test->reference;
    stock_invoke_normalized_load(REGION_ENTRY, test->cached, macl, state);
    if (ram_pointer(LIVE_LOAD)[0] != test->expected)
        return fail_value(test->name, "stored-byte", ram_pointer(LIVE_LOAD)[0], test->expected);
    if (state[0] != macl || state[1] != 0x10203040U || state[2] != 0x13579bdfU
        || state[3] != 0x2468ace0U || state[4] != 0x13572468U || state[5] != DIVIDER_ENTRY)
        return fail_value(test->name, "preserved-registers-macl-gbr-divider", 1, 0);
    if (*reference != test->reference
        || *(volatile uint8_t *)(uintptr_t)(REFERENCE_ADDRESS + 2U) != neighbor)
        return fail_value(test->name, "read-only-reference-word-and-neighbor", 1, 0);
    return check_memory(test->name, 1, test->reference == 0);
}

static int run_divider(const struct divider_case *test)
{
    uint32_t result;
    prepare(0x8123);
    result = stock_invoke_r1(DIVIDER_ENTRY, test->numerator, test->denominator);
    if (result != test->expected)
        return fail_value(test->name, "direct-divider-result", result, test->expected);
    return check_memory(test->name, 0, test->denominator == 0);
}

int main(void)
{
    size_t index;
    for (index = 0; index < ARRAY_SIZE(load_cases); ++index)
        if (!run_load(load_cases + index, MACL_SEED ^ (uint32_t)index))
            return 1;
    for (index = 0; index < ARRAY_SIZE(divider_cases); ++index)
        if (!run_divider(divider_cases + index))
            return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY,
           (unsigned long)(ARRAY_SIZE(load_cases) + ARRAY_SIZE(divider_cases)));
    return 0;
}
