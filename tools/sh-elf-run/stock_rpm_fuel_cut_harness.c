#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))

#define TEST_RAM_BASE 0x01000000U

/* The verifier defines the key and the entry of the region, the symbols that
   the entity files state for the layout: the fuel-inhibit state byte, the
   masks of its named bits armed and active, the engine speed word, and the
   threshold table, and the region constants: the cut delay counter, the byte
   whose bit 4 selects the threshold pair, and the configuration and delay
   bytes of the calibration. */
#if !defined(REGION_KEY) || !defined(REGION_ENTRY)
#error "the verifier defines the key and the entry of the region"
#endif
#if !defined(FUEL_INHIBIT) || !defined(ARMED_MASK) || !defined(ACTIVE_MASK) \
    || !defined(ENGINE_SPEED) || !defined(FUEL_CUT_TABLE)
#error "the verifier defines the symbols of the entity files"
#endif
#if !defined(DELAY_COUNTER) || !defined(PAIR_SELECTOR) || !defined(CUT_CONFIG) \
    || !defined(CUT_DELAY)
#error "the verifier defines the region constants"
#endif

/* The main RPM fuel-cut state machine of a relocated 8MFK layout. Bit 7 of
   the configuration byte, clear in the stock calibration, would choose the
   pair by three state bits instead. Pair p compares the engine speed word
   with the cut-on word p and the release word 2 + p of the table. */
#define PAIR_SELECT_MASK 0x10U
#define CONDITIONED_PAIRS 0x80U
#define CUT_ON(pair) (pair)
#define RELEASE(pair) (2U + (pair))
#define STATE_MASK (ARMED_MASK | ACTIVE_MASK)
/* The window around GBR of the function whose bytes stay unchanged, apart
   from the state byte and the delay counter. */
#define WINDOW_START 0xffff2480U
#define WINDOW_SIZE 0x180U

#if FUEL_INHIBIT < WINDOW_START || FUEL_INHIBIT >= WINDOW_START + WINDOW_SIZE \
    || DELAY_COUNTER < WINDOW_START \
    || DELAY_COUNTER >= WINDOW_START + WINDOW_SIZE \
    || PAIR_SELECTOR < WINDOW_START \
    || PAIR_SELECTOR >= WINDOW_START + WINDOW_SIZE
#error "the state byte, the delay counter, and the selector lie in the window"
#endif

extern uint32_t stock_invoke(uint32_t entry, uint32_t r12, uint32_t r0);

struct stock_case {
    const char *name;
    uint8_t pair;
    uint8_t armed_before;
    uint8_t active_before;
    /* The other bits of the state byte. */
    uint8_t others;
    /* The engine speed is the table word `word` plus `offset`. */
    uint8_t word;
    int8_t offset;
    /* The delay byte of the calibration during the case. */
    uint8_t delay;
    uint8_t counter_before;
    uint8_t armed_after;
    uint8_t active_after;
    uint8_t counter_after;
};

static const struct stock_case stock_cases[] = {
    {"below-cut-on", 0, 0, 0, 0x00, CUT_ON(0), -1, 0, 0x5a, 0, 0, 0x5a},
    {"below-cut-on-clears-arm", 0, 1, 0, 0xff, CUT_ON(0), -1, 0, 0x03,
     0, 0, 0x03},
    {"cut-on-arms-and-cuts", 0, 0, 0, 0x00, CUT_ON(0), 0, 0, 0x77, 1, 1, 0x00},
    {"above-cut-on-keeps-other-bits", 0, 0, 0, 0xff, CUT_ON(0), 1, 0, 0x77,
     1, 1, 0x00},
    {"armed-waits-for-counter", 0, 1, 0, 0x00, CUT_ON(0), 3, 0, 0x02,
     1, 0, 0x02},
    {"armed-counter-zero-cuts", 0, 1, 0, 0xff, CUT_ON(0), 0, 0, 0x00,
     1, 1, 0x00},
    {"delay-loads-counter", 0, 0, 0, 0x00, CUT_ON(0), 0, 5, 0x00, 1, 0, 0x05},
    {"active-at-release-keeps", 0, 1, 1, 0x00, RELEASE(0), 0, 0, 0x11,
     1, 1, 0x11},
    {"active-between-words-keeps", 0, 1, 1, 0xff, RELEASE(0), 1, 0, 0x11,
     1, 1, 0x11},
    {"active-below-release-releases", 0, 1, 1, 0xff, RELEASE(0), -1, 0, 0x11,
     0, 0, 0x11},
    {"second-pair-cut-on", 1, 0, 0, 0x00, CUT_ON(1), 0, 0, 0x33, 1, 1, 0x00},
    {"first-pair-below-its-cut-on", 0, 0, 0, 0xff, CUT_ON(1), 0, 0, 0x33,
     0, 0, 0x33},
    {"second-pair-keeps-above-its-release", 1, 1, 1, 0x00, RELEASE(1), 1, 0,
     0x44, 1, 1, 0x44},
    {"second-pair-below-release-releases", 1, 1, 1, 0xff, RELEASE(1), -1, 0,
     0x44, 0, 0, 0x44},
};

static uint8_t window_seed[WINDOW_SIZE];

static volatile uint8_t *ram_pointer(uint32_t original)
{
    uintptr_t address = TEST_RAM_BASE + (original & 0xffffU);
    return (volatile uint8_t *)address;
}

static volatile uint16_t *ram_word(uint32_t original)
{
    uintptr_t address = TEST_RAM_BASE + (original & 0xffffU);
    return (volatile uint16_t *)address;
}

static volatile uint8_t *rom_pointer(uint32_t address)
{
    return (volatile uint8_t *)(uintptr_t)address;
}

static uint16_t table_word(unsigned index)
{
    return ((const volatile uint16_t *)(uintptr_t)FUEL_CUT_TABLE)[index];
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

static uint8_t state_byte(uint8_t others, uint8_t armed, uint8_t active)
{
    return (uint8_t)(
        (others & (uint8_t)~STATE_MASK)
        | (armed ? ARMED_MASK : 0U) | (active ? ACTIVE_MASK : 0U));
}

static int run_case(const struct stock_case *test)
{
    volatile uint8_t *delay = rom_pointer(CUT_DELAY);
    uint8_t stock_delay = delay[0];
    uint16_t speed = (uint16_t)(table_word(test->word) + test->offset);
    uint8_t selector;
    uint8_t expected;
    uint32_t result;
    size_t index;

    for (index = 0; index < WINDOW_SIZE; ++index)
        ram_pointer(WINDOW_START + index)[0] = (uint8_t)(index * 37U + 11U);
    selector = ram_pointer(PAIR_SELECTOR)[0];
    ram_pointer(PAIR_SELECTOR)[0] = test->pair
        ? (uint8_t)(selector | PAIR_SELECT_MASK)
        : (uint8_t)(selector & (uint8_t)~PAIR_SELECT_MASK);
    ram_pointer(FUEL_INHIBIT)[0] = state_byte(
        test->others, test->armed_before, test->active_before);
    ram_pointer(DELAY_COUNTER)[0] = test->counter_before;
    ram_word(ENGINE_SPEED)[0] = speed;
    for (index = 0; index < WINDOW_SIZE; ++index)
        window_seed[index] = ram_pointer(WINDOW_START + index)[0];
    delay[0] = test->delay;

    result = stock_invoke(REGION_ENTRY, 0, 0);
    delay[0] = stock_delay;

    expected = state_byte(test->others, test->armed_after, test->active_after);
    if (ram_pointer(FUEL_INHIBIT)[0] != expected)
        return fail_value(
            test->name, "fuel_inhibit", ram_pointer(FUEL_INHIBIT)[0], expected);
    if (ram_pointer(DELAY_COUNTER)[0] != test->counter_after)
        return fail_value(
            test->name, "delay_counter", ram_pointer(DELAY_COUNTER)[0],
            test->counter_after);
    if (result != test->active_after)
        return fail_value(test->name, "result", result, test->active_after);
    if (ram_word(ENGINE_SPEED)[0] != speed)
        return fail_value(
            test->name, "engine_speed", ram_word(ENGINE_SPEED)[0], speed);
    for (index = 0; index < WINDOW_SIZE; ++index) {
        uint32_t address = WINDOW_START + index;

        if (address == FUEL_INHIBIT || address == DELAY_COUNTER)
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

    /* The stock calibration selects the pair by the selector bit, and each
       case that tells the pairs apart needs the second pair below the first
       one. */
    if (rom_pointer(CUT_CONFIG)[0] & CONDITIONED_PAIRS)
        return fail_value(
            "calibration", "cut_config", rom_pointer(CUT_CONFIG)[0], 0);
    if (table_word(CUT_ON(1)) >= table_word(CUT_ON(0)))
        return fail_value(
            "calibration", "cut_on", table_word(CUT_ON(1)),
            table_word(CUT_ON(0)));
    if (table_word(RELEASE(1)) + 1U >= table_word(RELEASE(0)))
        return fail_value(
            "calibration", "release", table_word(RELEASE(1)),
            table_word(RELEASE(0)));
    for (index = 0; index < ARRAY_SIZE(stock_cases); ++index) {
        if (!run_case(&stock_cases[index]))
            return 1;
    }
    printf(
        "VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",
        REGION_KEY, (unsigned long)ARRAY_SIZE(stock_cases));
    return 0;
}
