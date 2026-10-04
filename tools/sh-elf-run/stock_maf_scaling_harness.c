#include <stdint.h>
#include <stdio.h>

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(GUARD_ENTRY) \
    || !defined(SCALE_ENTRY) || !defined(CAP_ENTRY) || !defined(MAF_SAMPLE_B1) \
    || !defined(MAF_SAMPLE_B2) || !defined(MAF_OUTPUT_B1) || !defined(MAF_OUTPUT_B2) \
    || !defined(COEFFICIENT) || !defined(MODE_FLAGS) || !defined(BOUNDS_ADDRESS) \
    || !defined(DEFAULT_ADDRESS)
#error "the verifier defines the MAF entries, coefficient, mode, banks, and ROM data"
#endif

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U
#define SCALE_DESTINATION 0xffff4f04U
#define MACL_SEED 0x89abcdefU
#define SAVED_R13 0x13579bdfU
#define SAVED_R14 0x2468ace0U

extern uint32_t stock_invoke_maf(uint32_t, uint32_t, uint32_t, uint32_t *);
extern uint32_t stock_invoke_maf_scale(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t *);
extern uint32_t stock_invoke_maf_cap(uint32_t, uint32_t, uint32_t, uint32_t *);

struct publisher_case {
    const char *name;
    uint8_t mode;
    uint16_t coefficient, raw, coefficient_after, output;
    uint8_t guard_return;
};

/* Literal results cover the ADC domain and direct word-entry boundaries. */
static const struct publisher_case publisher_cases[] = {
    {"reset-zero", 0, 0, 1023, 0x8000, 1024, 0xaa},
    {"reset-below", 0, 0x78ff, 1023, 0x8000, 1024, 0xaa},
    {"lower-edge", 0, 0x7900, 1023, 0x7900, 968, 0x55},
    {"below-unity", 0, 0x7fff, 1023, 0x7fff, 1023, 0x55},
    {"unity-full-scale", 0, 0x8000, 1023, 0x8000, 1024, 0x55},
    {"unity-not-full-scale", 0, 0x8000, 1022, 0x8000, 1022, 0x55},
    {"above-unity", 0, 0x8001, 1023, 0x8001, 1024, 0x55},
    {"upper-edge", 0, 0x8700, 1023, 0x8700, 1079, 0x55},
    {"reset-above", 0, 0x8701, 1023, 0x8000, 1024, 0xaa},
    {"reset-maximum", 0, 0xffff, 1023, 0x8000, 1024, 0xaa},
    {"bypass-zero-full-scale", 8, 0, 1023, 0, 1, 8},
    {"bypass-one-full-scale", 8, 1, 1023, 1, 1, 8},
    {"bypass-half-full-scale", 8, 0x4000, 1023, 0x4000, 512, 8},
    {"bypass-maximum-full-scale", 8, 0xffff, 1023, 0xffff, 2046, 8},
    {"other-mode-bits-bypass", 0xff, 0, 1023, 0, 1, 0xff},
    {"other-mode-bits-guard", 0xf7, 0x8000, 1023, 0x8000, 1024, 0x55},
    {"bypass-zero-non-full-scale", 8, 0, 1022, 0, 0, 8},
    {"word-below-saturation", 8, 0xffff, 0x7fff, 0xffff, 65533, 8},
    {"word-at-saturation", 8, 0xffff, 0x8000, 0xffff, 65535, 8},
    {"word-above-saturation", 8, 0xffff, 0x8001, 0xffff, 65535, 8},
    {"word-maximum", 8, 0xffff, 0xffff, 0xffff, 65535, 8},
    {"zero-sample", 0, 0x8000, 0, 0x8000, 0, 0x55},
    {"first-sample", 0, 0x8000, 1, 0x8000, 1, 0x55},
    {"fraction-truncation", 8, 0x4000, 1, 0x4000, 0, 8},
    {"word-before-signed-boundary", 0, 0x8000, 0x7fff, 0x8000, 32767, 0x55},
    {"word-maximum-unity", 0, 0x8000, 0xffff, 0x8000, 65535, 0x55},
};

struct scale_case {
    const char *name;
    uint32_t raw;
    uint16_t coefficient, output;
};

static const struct scale_case scale_cases[] = {
    {"scale-zero", 0, 0, 0},
    {"scale-zero-coefficient", 0xffff, 0, 0},
    {"scale-small-coefficient", 0xffff, 1, 1},
    {"scale-full-adc-zero", 0x03ff, 0, 0},
    {"scale-full-adc-one", 0x03ff, 1, 0},
    {"scale-full-adc-half", 0x03ff, 0x4000, 511},
    {"scale-full-adc-unity", 0x03ff, 0x8000, 1023},
    {"scale-full-adc-maximum", 0x03ff, 0xffff, 2045},
    {"scale-below-saturation", 0x7fff, 0xffff, 65533},
    {"scale-at-saturation", 0x8000, 0xffff, 65535},
    {"scale-above-saturation", 0x8001, 0xffff, 65535},
    {"scale-unsigned-product", 0xffff, 0xffff, 65535},
    {"scale-signed-input-boundary", 0x8000, 0x8000, 32768},
    {"scale-word-unity", 0xffff, 0x8000, 65535},
    {"scale-discard-upper-ones", 0xffffffff, 0x8000, 65535},
    {"scale-discard-upper-pattern", 0x12340040, 0x8000, 64},
    {"scale-discard-sign-bit", 0x80000000, 0xffff, 0},
};

struct cap_case {
    const char *name;
    uint32_t input;
    uint16_t output;
};

/* Only direct branch entry supplies values above the preceding EXTU.W. */
static const struct cap_case cap_cases[] = {
    {"cap-zero", 0, 0},
    {"cap-word-maximum", 0xffff, 0xffff},
    {"cap-first-wide", 0x10000, 0xffff},
    {"cap-signed-maximum", 0x7fffffff, 0xffff},
    {"cap-signed-negative", 0x80000000, 0},
};

struct window {
    uint32_t address;
    uint8_t before[12];
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

static int fail(const char *name, uint32_t bank, const char *field)
{
    printf("VQ_SH_ELF_STOCK_CODE status=FAIL case=%s bank=%lu field=%s\n",
           name, (unsigned long)bank, field);
    return 0;
}

static void prepare(struct window *windows, uint8_t mode, uint16_t coefficient,
                    uint16_t raw, uint32_t bank)
{
    size_t index, byte;
    const uint32_t addresses[] = {
        MAF_SAMPLE_B1 - 4U, COEFFICIENT - 4U, MODE_FLAGS - 4U, MAF_OUTPUT_B1 - 4U,
    };
    for (index = 0; index < ARRAY_SIZE(addresses); ++index) {
        windows[index].address = addresses[index];
        for (byte = 0; byte < sizeof(windows[index].before); ++byte)
            ram_pointer(addresses[index])[byte] = (uint8_t)(31U * byte + 17U * index + 3U);
    }
    set_word(MAF_SAMPLE_B1, bank == 0 ? raw : 0x0155);
    set_word(MAF_SAMPLE_B2, bank == 1 ? raw : 0x0155);
    set_word(COEFFICIENT, coefficient);
    ram_pointer(MODE_FLAGS)[0] = mode;
    set_word(MAF_OUTPUT_B1, 0xa55a);
    set_word(MAF_OUTPUT_B2, 0x5aa5);
    for (index = 0; index < ARRAY_SIZE(addresses); ++index)
        for (byte = 0; byte < sizeof(windows[index].before); ++byte)
            windows[index].before[byte] = ram_pointer(addresses[index])[byte];
}

static int preserved(const struct window *windows, const char *name, uint32_t bank,
                     uint32_t output_address, uint16_t coefficient_after)
{
    size_t index, byte;
    if (word(COEFFICIENT) != coefficient_after)
        return fail(name, bank, "coefficient");
    for (index = 0; index < 4; ++index)
        for (byte = 0; byte < sizeof(windows[index].before); ++byte) {
            uint32_t address = windows[index].address + (uint32_t)byte;
            if ((address >= COEFFICIENT && address < COEFFICIENT + 2U)
                || (output_address != 0 && address >= output_address && address < output_address + 2U))
                continue;
            if (ram_pointer(address)[0] != windows[index].before[byte])
                return fail(name, bank, "read-only-input-or-neighbor");
        }
    if (*(const volatile uint16_t *)(uintptr_t)BOUNDS_ADDRESS != 0x8779
        || *(const volatile uint16_t *)(uintptr_t)DEFAULT_ADDRESS != 0x8000)
        return fail(name, bank, "read-only-rom");
    return 1;
}

static int state_matches(const uint32_t *state, const char *name, uint32_t bank, uint32_t macl)
{
    if (state[0] != macl || state[1] != SAVED_R13 || state[2] != SAVED_R14)
        return fail(name, bank, "macl-or-saved-registers");
    return 1;
}

static int run_guard(const struct publisher_case *test, uint32_t macl)
{
    struct window windows[4];
    uint32_t state[3], result;
    prepare(windows, test->mode, test->coefficient, test->raw, 0);
    result = stock_invoke_maf(GUARD_ENTRY, 0, macl, state);
    if (result != test->guard_return)
        return fail(test->name, 0, "guard-return");
    return state_matches(state, test->name, 0, macl)
        && preserved(windows, test->name, 0, 0, test->coefficient_after);
}

static int run_publisher(const struct publisher_case *test, uint32_t bank_argument, uint32_t macl)
{
    struct window windows[4];
    uint32_t state[3], result, bank = bank_argument & 0xffU;
    uint32_t output = bank == 0 ? MAF_OUTPUT_B1 : MAF_OUTPUT_B2;
    prepare(windows, test->mode, test->coefficient, test->raw, bank);
    result = stock_invoke_maf(REGION_ENTRY, bank_argument, macl, state);
    if (word(output) != test->output || result != bank * 2U)
        return fail(test->name, bank_argument, "published-word-or-return");
    return state_matches(state, test->name, bank_argument, macl)
        && preserved(windows, test->name, bank_argument, output, test->coefficient_after);
}

static int run_scale(const struct scale_case *test, uint32_t macl)
{
    struct window windows[4];
    uint8_t before[12];
    uint32_t state[3];
    size_t byte;
    prepare(windows, 0, test->coefficient, 0x0312, 0);
    for (byte = 0; byte < sizeof(before); ++byte) {
        before[byte] = (uint8_t)(byte * 23U + 5U);
        ram_pointer(SCALE_DESTINATION - 4U)[byte] = before[byte];
    }
    stock_invoke_maf_scale(SCALE_ENTRY, test->raw,
                          (uint32_t)(uintptr_t)ram_pointer(SCALE_DESTINATION), macl, state);
    if (word(SCALE_DESTINATION) != test->output)
        return fail(test->name, 0, "scaled-word");
    for (byte = 0; byte < sizeof(before); ++byte)
        if ((byte < 4 || byte >= 6) && ram_pointer(SCALE_DESTINATION - 4U)[byte] != before[byte])
            return fail(test->name, 0, "scale-destination-neighbor");
    return state_matches(state, test->name, 0, macl)
        && preserved(windows, test->name, 0, 0, test->coefficient);
}

static int run_cap(const struct cap_case *test, uint32_t bank)
{
    struct window windows[4];
    uint32_t state[3], result;
    uint32_t output = bank == 0 ? MAF_OUTPUT_B1 : MAF_OUTPUT_B2;
    prepare(windows, 0, 0x8000, 0x0201, bank);
    result = stock_invoke_maf_cap(CAP_ENTRY, test->input, bank, state);
    if (word(output) != test->output || result != bank * 2U)
        return fail(test->name, bank, "direct-cap-word-or-return");
    return state_matches(state, test->name, bank, MACL_SEED)
        && preserved(windows, test->name, bank, output, 0x8000);
}

int main(void)
{
    size_t index, cases = 0;
    uint32_t bank;
    for (index = 0; index < ARRAY_SIZE(publisher_cases); ++index) {
        uint32_t macl = MACL_SEED ^ (uint32_t)index;
        if (!run_guard(publisher_cases + index, macl))
            return 1;
        ++cases;
        for (bank = 0; bank < 2; ++bank) {
            if (!run_publisher(publisher_cases + index, bank, macl))
                return 1;
            ++cases;
        }
    }
    for (bank = 0; bank < 2; ++bank) {
        if (!run_publisher(publisher_cases + 4, bank + 0x100U, MACL_SEED))
            return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(scale_cases); ++index) {
        if (!run_scale(scale_cases + index, MACL_SEED ^ (uint32_t)index))
            return 1;
        ++cases;
    }
    for (index = 0; index < ARRAY_SIZE(cap_cases); ++index)
        for (bank = 0; bank < 2; ++bank) {
            if (!run_cap(cap_cases + index, bank))
                return 1;
            ++cases;
        }
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY,
           (unsigned long)cases);
    return 0;
}
