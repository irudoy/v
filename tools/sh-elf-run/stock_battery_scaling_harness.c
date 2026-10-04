#include <stdint.h>
#include <stdio.h>

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(BATTERY_SAMPLE) \
    || !defined(BATTERY_COPY) || !defined(BATTERY_BYTE) || !defined(BATTERY_OUTPUT) \
    || !defined(COEFFICIENT) || !defined(MODE_FLAGS)
#error "the verifier defines the battery entry, input, intermediate cells, and output"
#endif

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U
#define MACL_SEED 0x89abcdefU
#define SAVED_R13 0x13579bdfU
#define SAVED_R14 0x2468ace0U
#define GBR_SEED 0x13572468U

extern uint32_t stock_invoke_battery(uint32_t, uint32_t, uint32_t *);

struct battery_case {
    const char *name;
    uint8_t mode;
    uint16_t coefficient, raw;
    uint8_t input_byte;
    uint16_t coefficient_after;
    uint8_t output;
};

/* Word-entry boundary vectors do not assert a reachable ADC input. */
static const struct battery_case battery_cases[] = {
    {"zero", 0, 0x8000, 0, 0, 0x8000, 0},
    {"discard-low-bits", 0, 0x8000, 3, 0, 0x8000, 0},
    {"first-count", 0, 0x8000, 4, 1, 0x8000, 1},
    {"before-full-adc", 0, 0x8000, 1022, 255, 0x8000, 255},
    {"full-adc-without-increment", 0, 0x8000, 1023, 255, 0x8000, 255},
    {"lower-bound", 0, 0x7900, 1023, 255, 0x7900, 241},
    {"upper-bound", 0, 0x8700, 256, 64, 0x8700, 67},
    {"below-unity", 0, 0x7fff, 1023, 255, 0x7fff, 254},
    {"above-unity", 0, 0x8001, 1023, 255, 0x8001, 255},
    {"reset-zero", 0, 0, 1023, 255, 0x8000, 255},
    {"reset-below", 0, 0x78ff, 1023, 255, 0x8000, 255},
    {"reset-above", 0, 0x8701, 256, 64, 0x8000, 64},
    {"reset-maximum", 0, 0xffff, 256, 64, 0x8000, 64},
    {"bypass-zero", 8, 0, 1023, 255, 0, 0},
    {"bypass-one", 8, 1, 1023, 255, 1, 0},
    {"bypass-half", 8, 0x4000, 1023, 255, 0x4000, 127},
    {"bypass-maximum", 8, 0xffff, 1023, 255, 0xffff, 255},
    {"bypass-at-byte-cap", 8, 0xffff, 512, 128, 0xffff, 255},
    {"bypass-above-byte-cap", 8, 0xffff, 516, 129, 0xffff, 255},
    {"bypass-below-byte-cap", 8, 0xffff, 508, 127, 0xffff, 253},
    {"other-mode-bits-bypass", 0xff, 0, 1023, 255, 0, 0},
    {"other-mode-bits-guard", 0xf7, 0x8000, 512, 128, 0x8000, 128},
    {"input-byte-wrap", 0, 0x8000, 0x0400, 0, 0x8000, 0},
    {"first-after-byte-wrap", 0, 0x8000, 0x0404, 1, 0x8000, 1},
    {"word-before-signed-boundary", 0, 0x8000, 0x7fff, 255, 0x8000, 255},
    {"word-signed-boundary", 0, 0x8000, 0x8000, 0, 0x8000, 0},
    {"word-after-signed-boundary", 0, 0x8000, 0x8004, 1, 0x8000, 1},
    {"word-maximum-aligned", 0, 0x8000, 0xfffc, 255, 0x8000, 255},
    {"word-maximum", 0, 0x8000, 0xffff, 255, 0x8000, 255},
    {"word-pattern", 0, 0x8000, 0x2345, 209, 0x8000, 209},
    {"fraction-truncation", 8, 0x4000, 4, 1, 0x4000, 0},
    {"upper-bound-byte-cap", 0, 0x8700, 1023, 255, 0x8700, 255},
};

struct window {
    uint32_t address;
    uint8_t before[12];
};

static volatile uint8_t *ram_pointer(uint32_t address)
{
    return (volatile uint8_t *)(uintptr_t)(TEST_RAM_BASE + (address & 0xffffU));
}

static uint16_t word(uint32_t address)
{
    return *(volatile uint16_t *)ram_pointer(address);
}

static int fail(const char *name, const char *field)
{
    printf("VQ_SH_ELF_STOCK_CODE status=FAIL case=%s field=%s\n", name, field);
    return 0;
}

static int run_case(const struct battery_case *test, uint32_t macl)
{
    struct window windows[5];
    const uint32_t addresses[] = {BATTERY_SAMPLE - 4U, BATTERY_COPY - 4U,
                                 BATTERY_OUTPUT - 4U, COEFFICIENT - 4U, MODE_FLAGS - 4U};
    uint32_t state[4], result;
    size_t index, byte;
    for (index = 0; index < ARRAY_SIZE(addresses); ++index) {
        windows[index].address = addresses[index];
        for (byte = 0; byte < sizeof(windows[index].before); ++byte)
            ram_pointer(addresses[index])[byte] = (uint8_t)(37U * byte + 19U * index + 5U);
    }
    *(volatile uint16_t *)ram_pointer(BATTERY_SAMPLE) = test->raw;
    *(volatile uint16_t *)ram_pointer(COEFFICIENT) = test->coefficient;
    ram_pointer(MODE_FLAGS)[0] = test->mode;
    for (index = 0; index < ARRAY_SIZE(addresses); ++index)
        for (byte = 0; byte < sizeof(windows[index].before); ++byte)
            windows[index].before[byte] = ram_pointer(addresses[index])[byte];

    result = stock_invoke_battery(REGION_ENTRY, macl, state);
    if (word(BATTERY_COPY) != test->raw
        || ram_pointer(BATTERY_BYTE)[0] != test->input_byte
        || word(COEFFICIENT) != test->coefficient_after
        || ram_pointer(BATTERY_OUTPUT)[0] != test->output || result != 0x74)
        return fail(test->name, "copy-byte-coefficient-output-or-return");
    if (state[0] != macl || state[1] != SAVED_R13 || state[2] != SAVED_R14 || state[3] != GBR_SEED)
        return fail(test->name, "macl-saved-registers-or-gbr");
    for (index = 0; index < ARRAY_SIZE(addresses); ++index)
        for (byte = 0; byte < sizeof(windows[index].before); ++byte) {
            uint32_t address = windows[index].address + (uint32_t)byte;
            if ((address >= BATTERY_COPY && address < BATTERY_COPY + 2U)
                || address == BATTERY_BYTE || address == BATTERY_OUTPUT
                || (address >= COEFFICIENT && address < COEFFICIENT + 2U))
                continue;
            if (ram_pointer(address)[0] != windows[index].before[byte])
                return fail(test->name, "read-only-input-or-neighbor");
        }
    if (*(const volatile uint16_t *)(uintptr_t)0x87f8 != 0x8779
        || *(const volatile uint16_t *)(uintptr_t)0x92be != 0x8000)
        return fail(test->name, "read-only-rom");
    return 1;
}

int main(void)
{
    size_t index;
    for (index = 0; index < ARRAY_SIZE(battery_cases); ++index)
        if (!run_case(battery_cases + index, MACL_SEED ^ (uint32_t)index))
            return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY,
           (unsigned long)ARRAY_SIZE(battery_cases));
    return 0;
}
