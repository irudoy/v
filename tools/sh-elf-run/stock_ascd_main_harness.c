#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))

#define TEST_RAM_BASE 0x01000000U

/* The verifier defines the key and the entry of the region, the symbols
   that the entity files state for the layout: the ASCD flag byte, the mask of
   its MAIN bit, and the button state byte, and the base register value that
   the stock pool gives the region. */
#if !defined(REGION_KEY) || !defined(REGION_ENTRY)
#error "the verifier defines the key and the entry of the region"
#endif
#if !defined(ASCD_FLAGS) || !defined(ASCD_MAIN_MASK) || !defined(BUTTON_STATE)
#error "the verifier defines the symbols of the entity files"
#endif
#ifndef REGION_R12
#error "the verifier defines the stock base register value"
#endif

/* JK78C 0x000fcbb0..0x000fcbed of the ASCD task 0x000fb9c0. Bit 7 of the
   calibration byte selects bit 7 of the alternative state byte instead of
   bit 0 of the button state byte as the source of the MAIN bit, and the
   coolant flag is set while the coolant byte reaches the threshold byte. */
#define MAIN_CONFIG 0x0000894fU
#define ALTERNATIVE_STATE 0xffff455fU
#define COOLANT 0xffff1079U
#define COOLANT_THRESHOLD 0x000087deU
#define COOLANT_FLAGS 0xffff450cU
#define COOLANT_MASK 0x20U
/* The region stores r0 of its entry state here. */
#define ENTRY_FLAGS 0xffff4513U
#define WINDOW_START 0xffff4500U
#define WINDOW_SIZE 0x80U

extern uint32_t stock_invoke(uint32_t entry, uint32_t r12, uint32_t r0);

struct stock_case {
    const char *name;
    uint8_t alternative_selected;
    uint8_t button;
    uint8_t alternative;
    int8_t coolant_offset;
    uint8_t flags_before;
    uint8_t coolant_flags_before;
    uint8_t entry_r0;
};

static const struct stock_case stock_cases[] = {
    {"button-set", 0, 0x01, 0x00, 0, 0x00, 0x00, 0x3c},
    {"button-set-keeps-flags", 0, 0xff, 0x00, 0, 0xff, 0xff, 0xc3},
    {"button-clear", 0, 0xfe, 0xff, 0, 0xff, 0x00, 0x5a},
    {"button-clear-keeps-flags", 0, 0x00, 0xff, 0, 0x00, 0xdf, 0xa5},
    {"alternative-set", 1, 0x00, 0x80, 0, 0x00, 0x00, 0x66},
    {"alternative-clear", 1, 0x01, 0x7f, 0, 0xff, 0xff, 0x99},
    {"coolant-below-threshold", 0, 0x01, 0x00, -1, 0x00, 0xff, 0x0f},
    {"coolant-above-threshold", 0, 0x00, 0x00, 1, 0xff, 0x00, 0xf0},
};

static uint8_t window_seed[WINDOW_SIZE];

static volatile uint8_t *ram_pointer(uint32_t original)
{
    uintptr_t address = TEST_RAM_BASE + (original & 0xffffU);
    return (volatile uint8_t *)address;
}

static volatile uint8_t *rom_pointer(uint32_t address)
{
    return (volatile uint8_t *)(uintptr_t)address;
}

static int fail_value(
    const char *name, const char *field, uint32_t actual, uint32_t expected)
{
    printf(
        "VQ_SH_ELF_STOCK_CODE status=FAIL case=%s field=%s "
        "actual=%08lx expected=%08lx\n",
        name, field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}

static int run_case(const struct stock_case *test)
{
    volatile uint8_t *config = rom_pointer(MAIN_CONFIG);
    uint8_t stock_config = config[0];
    uint8_t threshold = rom_pointer(COOLANT_THRESHOLD)[0];
    uint8_t coolant = (uint8_t)(threshold + test->coolant_offset);
    uint8_t source;
    uint8_t expected;
    uint8_t expected_coolant;
    size_t index;

    if (stock_config & 0x80U)
        return fail_value(test->name, "stock_config", stock_config, 0);
    for (index = 0; index < WINDOW_SIZE; ++index) {
        window_seed[index] = (uint8_t)(index * 37U + 11U);
        ram_pointer(WINDOW_START + index)[0] = window_seed[index];
    }
    ram_pointer(ASCD_FLAGS)[0] = test->flags_before;
    ram_pointer(COOLANT_FLAGS)[0] = test->coolant_flags_before;
    ram_pointer(ALTERNATIVE_STATE)[0] = test->alternative;
    ram_pointer(BUTTON_STATE)[0] = test->button;
    ram_pointer(COOLANT)[0] = coolant;
    for (index = 0; index < WINDOW_SIZE; ++index)
        window_seed[index] = ram_pointer(WINDOW_START + index)[0];
    if (test->alternative_selected)
        config[0] = (uint8_t)(stock_config | 0x80U);

    (void)stock_invoke(
        REGION_ENTRY, TEST_RAM_BASE + (REGION_R12 & 0xffffU), test->entry_r0);
    config[0] = stock_config;

    source = test->alternative_selected
        ? (uint8_t)(test->alternative & 0x80U)
        : (uint8_t)(test->button & 0x01U);
    expected = (uint8_t)(
        (test->flags_before & (uint8_t)~ASCD_MAIN_MASK)
        | (source != 0 ? ASCD_MAIN_MASK : 0U));
    expected_coolant = (uint8_t)(
        (test->coolant_flags_before & (uint8_t)~COOLANT_MASK)
        | (coolant >= threshold ? COOLANT_MASK : 0U));
    if (ram_pointer(ASCD_FLAGS)[0] != expected)
        return fail_value(
            test->name, "ascd_flags", ram_pointer(ASCD_FLAGS)[0], expected);
    if (ram_pointer(COOLANT_FLAGS)[0] != expected_coolant)
        return fail_value(
            test->name, "coolant_flags", ram_pointer(COOLANT_FLAGS)[0],
            expected_coolant);
    if (ram_pointer(ENTRY_FLAGS)[0] != test->entry_r0)
        return fail_value(
            test->name, "entry_flags", ram_pointer(ENTRY_FLAGS)[0],
            test->entry_r0);
    for (index = 0; index < WINDOW_SIZE; ++index) {
        uint32_t address = WINDOW_START + index;

        if (address == ASCD_FLAGS || address == COOLANT_FLAGS
                || address == ENTRY_FLAGS)
            continue;
        if (ram_pointer(address)[0] != window_seed[index])
            return fail_value(
                test->name, "window", address, window_seed[index]);
    }
    return 1;
}

int main(void)
{
    size_t index;

    for (index = 0; index < ARRAY_SIZE(stock_cases); ++index) {
        if (!run_case(&stock_cases[index]))
            return 1;
    }
    printf(
        "VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",
        REGION_KEY, (unsigned long)ARRAY_SIZE(stock_cases));
    return 0;
}
