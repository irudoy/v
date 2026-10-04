#include <stdint.h>
#include <stdio.h>

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(MAF_INPUT_B1) \
    || !defined(MAF_INPUT_B2) || !defined(MAF_OUTPUT_B1) || !defined(MAF_OUTPUT_B2) \
    || !defined(CORRECTION_B1) || !defined(CORRECTION_B2) || !defined(INIT_FLAGS) \
    || !defined(DIVIDER_ENTRY) || !defined(ZERO_DEN_ENTRY) || !defined(FAULT_ADDRESS) \
    || !defined(MULTIPLIER_ADDRESS) || !defined(BIAS_ADDRESS)
#error "the verifier defines the MAF banks, state, calibration, and divider entries"
#endif

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U
#define MACL_SEED 0x89abcdefU
#define SAVED_R12 0x10203040U
#define SAVED_R13 0x13579bdfU
#define SAVED_R14 0x2468ace0U
#define GBR_SEED 0x13572468U

extern uint32_t stock_invoke_compensation(uint32_t, uint32_t, uint32_t, uint32_t *);
extern uint32_t stock_invoke_compensation_zero(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t *);
extern uint32_t stock_invoke_r1(uint32_t, uint32_t, uint32_t);

struct compensation_case {
    const char *name;
    uint8_t flags[2], flags_after[2];
    uint16_t previous, raw;
    uint32_t correction;
    uint16_t output;
    uint8_t result[2];
};

static const struct compensation_case compensation_cases[] = {
    {"first-zero", {0, 0}, {1, 2}, 0xbeef, 0, 0xffffffff, 0, {1, 2}},
    {"first-ordinary", {0, 0}, {1, 2}, 0xffff, 200, 0xffffffff, 200, {1, 2}},
    {"first-signed-word", {0, 0}, {1, 2}, 0, 0x8000, 0xffffffff, 0x8000, {1, 2}},
    {"first-maximum-word", {0, 0}, {1, 2}, 0, 0xffff, 0, 0xffff, {1, 2}},
    {"first-other-flag-bits", {0xa0, 0xa0}, {0xa1, 0xa2}, 1, 345, 0xffffffff, 345, {0xa1, 0xa2}},
    {"first-sibling-flag-only", {2, 1}, {3, 3}, 1, 1000, 0xffffffff, 1000, {3, 3}},
    {"zero-correction", {1, 2}, {1, 2}, 0, 0xffff, 0, 0xffff, {0, 2}},
    {"both-bank-flags", {3, 3}, {3, 3}, 168, 200, 0x00180000, 168, {0, 2}},
    {"previous-zero", {1, 2}, {1, 2}, 0, 200, 0x00180000, 100, {0, 2}},
    {"previous-one", {1, 2}, {1, 2}, 1, 1000, 0x00180000, 901, {0, 2}},
    {"previous-167", {1, 2}, {1, 2}, 167, 200, 0x00180000, 168, {0, 2}},
    {"previous-168", {1, 2}, {1, 2}, 168, 200, 0x00180000, 168, {0, 2}},
    {"previous-169", {1, 2}, {1, 2}, 169, 200, 0x00180000, 168, {0, 2}},
    {"previous-200", {1, 2}, {1, 2}, 200, 200, 0x00180000, 172, {0, 2}},
    {"previous-255", {1, 2}, {1, 2}, 255, 1023, 0x00180000, 999, {0, 2}},
    {"below-denominator-cap", {1, 2}, {1, 2}, 65454, 1000, 0xffffffff, 665, {0, 2}},
    {"at-denominator-cap", {1, 2}, {1, 2}, 65455, 1000, 0xffffffff, 665, {0, 2}},
    {"above-denominator-cap", {1, 2}, {1, 2}, 65456, 1000, 0xffffffff, 665, {0, 2}},
    {"maximum-previous", {1, 2}, {1, 2}, 65535, 1000, 0xffffffff, 665, {0, 2}},
    {"unsigned-previous", {1, 2}, {1, 2}, 0x8000, 0x8000, 0x00180000, 0x8000, {0, 2}},
    {"unsigned-correction", {1, 2}, {1, 2}, 0, 1000, 0x80000000, 60392, {0, 2}},
    {"maximum-correction", {1, 2}, {1, 2}, 0, 1000, 0xffffffff, 54249, {0, 2}},
    {"maximum-correction-zero-raw", {1, 2}, {1, 2}, 0, 0, 0xffffffff, 53249, {0, 2}},
    {"numerator-floor-before", {1, 2}, {1, 2}, 255, 64, 0x0000ffff, 64, {0, 2}},
    {"numerator-floor-at", {1, 2}, {1, 2}, 255, 64, 0x00010000, 63, {0, 2}},
    {"numerator-floor-after", {1, 2}, {1, 2}, 255, 64, 0x00010001, 63, {0, 2}},
    {"mixed-correction-halves", {1, 2}, {1, 2}, 256, 64, 0x000100ff, 63, {0, 2}},
    {"fractional-numerator", {1, 2}, {1, 2}, 168, 200, 0x00180001, 168, {0, 2}},
    {"word-underflow", {1, 2}, {1, 2}, 0, 0, 0x00180000, 65436, {0, 2}},
    {"raw-below-correction", {1, 2}, {1, 2}, 0, 99, 0x00180000, 65535, {0, 2}},
    {"raw-equals-correction", {1, 2}, {1, 2}, 0, 100, 0x00180000, 0, {0, 2}},
    {"raw-above-correction", {1, 2}, {1, 2}, 0, 101, 0x00180000, 1, {0, 2}},
    {"unsigned-raw-word", {1, 2}, {1, 2}, 0, 0x8000, 0, 0x8000, {0, 2}},
    {"initialized-other-flag-bits", {0xa1, 0xa2}, {0xa1, 0xa2}, 168, 200, 0x00180000, 168, {0, 2}},
};

struct zero_case {
    const char *name;
    uint16_t raw, output;
};

static const struct zero_case zero_cases[] = {
    {"direct-zero-denominator", 0, 1},
    {"direct-zero-denominator-signed-boundary", 0x7fff, 0x8000},
    {"direct-zero-denominator-word-wrap", 0xffff, 0},
};

struct divider_case {
    const char *name;
    uint32_t numerator, denominator, quotient;
    uint32_t fault;
};

static const struct divider_case divider_cases[] = {
    {"direct-short-quotient", 255, 1, 255, 0xdeadbeef},
    {"direct-long-divisor", 0xffffffff, 0x10000, 65535, 0xdeadbeef},
    {"direct-wide-divisor", 0xffffffff, 0xffffffff, 1, 0xdeadbeef},
    {"direct-zero-divisor", 123, 0, 0, 0x44e},
};

struct window {
    uint32_t address;
    uint8_t before[16];
};

static volatile uint8_t *ram_pointer(uint32_t address)
{
    return (volatile uint8_t *)(uintptr_t)(TEST_RAM_BASE + (address & 0xffffU));
}

static void set_word(uint32_t address, uint16_t value)
{
    *(volatile uint16_t *)ram_pointer(address) = value;
}

static uint16_t word(uint32_t address)
{
    return *(volatile uint16_t *)ram_pointer(address);
}

static void set_longword(uint32_t address, uint32_t value)
{
    *(volatile uint32_t *)ram_pointer(address) = value;
}

static int fail(const char *name, uint32_t bank, const char *field)
{
    printf("VQ_SH_ELF_STOCK_CODE status=FAIL case=%s bank=%lu field=%s\n",
           name, (unsigned long)bank, field);
    return 0;
}

static void prepare(struct window *windows, const struct compensation_case *test, uint32_t bank)
{
    const uint32_t addresses[] = {MAF_INPUT_B1 - 4U, MAF_OUTPUT_B1 - 4U,
                                 CORRECTION_B1 - 4U, INIT_FLAGS - 4U};
    size_t index, byte;
    for (index = 0; index < ARRAY_SIZE(addresses); ++index) {
        windows[index].address = addresses[index];
        for (byte = 0; byte < sizeof(windows[index].before); ++byte)
            ram_pointer(addresses[index])[byte] = (uint8_t)(41U * byte + 23U * index + 7U);
    }
    set_word(MAF_INPUT_B1, bank == 0 ? test->raw : 0x1234);
    set_word(MAF_INPUT_B2, bank == 1 ? test->raw : 0x1234);
    set_word(MAF_OUTPUT_B1, bank == 0 ? test->previous : 0x4567);
    set_word(MAF_OUTPUT_B2, bank == 1 ? test->previous : 0x4567);
    set_longword(CORRECTION_B1, bank == 0 ? test->correction : 0x87654321);
    set_longword(CORRECTION_B2, bank == 1 ? test->correction : 0x87654321);
    ram_pointer(INIT_FLAGS)[0] = test->flags[bank];
    for (index = 0; index < ARRAY_SIZE(addresses); ++index)
        for (byte = 0; byte < sizeof(windows[index].before); ++byte)
            windows[index].before[byte] = ram_pointer(addresses[index])[byte];
}

static int preserved(const struct window *windows, const char *name, uint32_t bank,
                     uint8_t flags_after, uint32_t output)
{
    size_t index, byte;
    if (ram_pointer(INIT_FLAGS)[0] != flags_after)
        return fail(name, bank, "initialization-flags");
    for (index = 0; index < 4; ++index)
        for (byte = 0; byte < sizeof(windows[index].before); ++byte) {
            uint32_t address = windows[index].address + (uint32_t)byte;
            if (address == INIT_FLAGS || (address >= output && address < output + 2U))
                continue;
            if (ram_pointer(address)[0] != windows[index].before[byte])
                return fail(name, bank, "read-only-input-or-neighbor");
        }
    if (*(const volatile uint16_t *)(uintptr_t)MULTIPLIER_ADDRESS != 335
        || *(const volatile uint16_t *)(uintptr_t)BIAS_ADDRESS != 80)
        return fail(name, bank, "read-only-calibration");
    return 1;
}

static int state_matches(const uint32_t *state, const char *name, uint32_t bank, uint32_t macl)
{
    if (state[0] != macl || state[1] != SAVED_R12 || state[2] != SAVED_R13
        || state[3] != SAVED_R14 || state[4] != GBR_SEED)
        return fail(name, bank, "macl-saved-registers-or-gbr");
    return 1;
}

static int run_case(const struct compensation_case *test, uint32_t bank_argument, uint32_t macl)
{
    struct window windows[4];
    uint32_t state[5], bank = bank_argument & 0xffU;
    uint32_t output = bank == 0 ? MAF_OUTPUT_B1 : MAF_OUTPUT_B2;
    uint32_t result;
    prepare(windows, test, bank);
    result = stock_invoke_compensation(REGION_ENTRY, bank_argument, macl, state);
    if (word(output) != test->output || result != test->result[bank])
        return fail(test->name, bank_argument, "word-or-return");
    return state_matches(state, test->name, bank_argument, macl)
        && preserved(windows, test->name, bank, test->flags_after[bank], output);
}

static int run_zero(const struct zero_case *test, uint32_t bank)
{
    struct compensation_case context = compensation_cases[1];
    struct window windows[4];
    uint32_t state[5], result;
    uint32_t output = bank == 0 ? MAF_OUTPUT_B1 : MAF_OUTPUT_B2;
    context.raw = test->raw;
    prepare(windows, &context, bank);
    result = stock_invoke_compensation_zero(ZERO_DEN_ENTRY, bank, test->raw,
                 (uint32_t)(uintptr_t)ram_pointer(MAF_OUTPUT_B1 - 0x2cU), state);
    if (word(output) != test->output || result != bank * 2U)
        return fail(test->name, bank, "direct-zero-word-or-return");
    return state_matches(state, test->name, bank, MACL_SEED)
        && preserved(windows, test->name, bank, context.flags[bank], output);
}

static int run_sequence(uint32_t bank)
{
    static const uint16_t expected[] = {200, 172, 169, 168, 168};
    static const uint8_t flags[] = {1, 2};
    struct compensation_case context = compensation_cases[1];
    struct window windows[4];
    uint32_t state[5], result;
    uint32_t output = bank == 0 ? MAF_OUTPUT_B1 : MAF_OUTPUT_B2;
    size_t index;
    context.correction = 0x00180000;
    prepare(windows, &context, bank);
    for (index = 0; index < ARRAY_SIZE(expected); ++index) {
        uint32_t macl = MACL_SEED ^ (uint32_t)index;
        result = stock_invoke_compensation(REGION_ENTRY, bank, macl, state);
        if (word(output) != expected[index] || result != (index == 0 ? flags[bank] : bank * 2U))
            return fail("ordered-recurrence", bank, "word-or-return");
        if (!state_matches(state, "ordered-recurrence", bank, macl)
            || !preserved(windows, "ordered-recurrence", bank, flags[bank], output))
            return 0;
    }
    return 1;
}

static int run_divider(const struct divider_case *test)
{
    uint8_t before[16];
    size_t byte;
    uint32_t result;
    for (byte = 0; byte < sizeof(before); ++byte)
        ram_pointer(FAULT_ADDRESS - 8U)[byte] = (uint8_t)(43U * byte + 9U);
    set_longword(FAULT_ADDRESS, 0xdeadbeef);
    for (byte = 0; byte < sizeof(before); ++byte)
        before[byte] = ram_pointer(FAULT_ADDRESS - 8U)[byte];
    result = stock_invoke_r1(DIVIDER_ENTRY, test->numerator, test->denominator);
    if (result != test->quotient || *(volatile uint32_t *)ram_pointer(FAULT_ADDRESS) != test->fault)
        return fail(test->name, 0, "quotient-or-fault");
    for (byte = 0; byte < sizeof(before); ++byte)
        if ((byte < 8 || byte >= 12) && ram_pointer(FAULT_ADDRESS - 8U)[byte] != before[byte])
            return fail(test->name, 0, "fault-neighbor");
    return 1;
}

int main(void)
{
    size_t index, cases = 0;
    uint32_t bank;
    for (index = 0; index < ARRAY_SIZE(compensation_cases); ++index)
        for (bank = 0; bank < 2; ++bank) {
            if (!run_case(compensation_cases + index, bank, MACL_SEED ^ (uint32_t)index))
                return 1;
            ++cases;
        }
    for (bank = 0; bank < 2; ++bank) {
        if (!run_case(compensation_cases + 1, bank + 0x100U, MACL_SEED))
            return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(zero_cases); ++index)
        for (bank = 0; bank < 2; ++bank) {
            if (!run_zero(zero_cases + index, bank))
                return 1;
            ++cases;
        }
    for (bank = 0; bank < 2; ++bank) {
        if (!run_sequence(bank))
            return 1;
        cases += 5;
    }
    for (index = 0; index < ARRAY_SIZE(divider_cases); ++index) {
        if (!run_divider(divider_cases + index))
            return 1;
        ++cases;
    }
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY,
           (unsigned long)cases);
    return 0;
}
