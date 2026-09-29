#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))

#define TEST_RAM_BASE 0x01000000U
#define SELECTOR_STATE 0xffff5d00U
#define FUEL_SHADOW 0xffff5d10U
#define THROTTLE_RUNTIME 0xffff1796U
#define RL_STATE_GUARD 0xffff5d3cU
#define RL_STATE 0xffff5d40U
#ifdef TARGET_VQ37_ROLLING
#define FUEL_SHADOW_SIZE 36U
#define THROTTLE_SHADOW 0xffff5d38U
#define THROTTLE_SHADOW_SIZE 2U
#define RL_STATE_SIZE 24U
#define FUEL_CUT_WRAPPER 0x000d5000U
#define FUEL_REQUEST_OFFSET 20U
#define FUEL_REQUEST_MASK 0x003fU
/* The request latch: set at or above cut, released below restore. */
#define FUEL_REQUEST_LATCH_OFFSET 22U
/* The final six-cylinder inhibit mask that the stock coordinator publishes
   and the wrapper extends. */
#define FUEL_FINAL_MASK 0xffff22e0U
/* The base mask that the coordinator stub publishes and returns, and the
   mask after the wrapper adds the six cylinder bits of a request. */
#define FUEL_STOCK_MASK 0x80U
#define FUEL_REQUESTED_MASK 0xbfU
#else
#define FUEL_SHADOW_SIZE 12U
#define THROTTLE_SHADOW 0xffff5d20U
#define THROTTLE_SHADOW_SIZE 28U
#define RL_STATE_SIZE 20U
#endif
#define RL_CONFIG 0x000d3f60U
#define BUTTON_CODE 0xffff2a85U
#define ASCD_STATUS 0xffff41aeU
/* The ASCD task keeps the MAIN switch state in one bit of this flag byte, at
   the position of the layout; the other bits hold flags of other ASCD
   functions, which neither abort the selector nor fail the launch gate. */
#ifdef TARGET_1ND
#define ASCD_MAIN 0x20U
#elif defined(TARGET_1ME3B)
#define ASCD_MAIN 0x02U
#elif defined(TARGET_JK78)
#define ASCD_MAIN 0x10U
#else
#define ASCD_MAIN 0x80U
#endif
#define ASCD_FOREIGN_FLAGS ((uint8_t)~ASCD_MAIN)
/* The stock RPM fuel-cut state keeps its active cut in one bit, at the
   position of the layout; the engine reports that bit in the fuel-cut flag,
   and the other bits of the byte leave the flag clear. */
#ifdef TARGET_1ND
#define FUEL_CUT_ACTIVE 0x20U
#elif defined(TARGET_1ME3B)
#define FUEL_CUT_ACTIVE 0x08U
#elif defined(TARGET_JK78)
#define FUEL_CUT_ACTIVE 0x10U
#elif defined(TARGET_8MFK)
#define FUEL_CUT_ACTIVE 0x40U
#else
#define FUEL_CUT_ACTIVE 0x04U
#endif
#define SPEED 0xffff110eU
#define RPM 0xffff11bcU
#define PEDAL 0xffff2672U
#define COOLANT 0xffff1077U
#define FORMER_BRAKE_STATUS 0xffff2451U
#define FUEL_CUT_STATUS 0xffff2497U
#define IGNITION_OUTPUT 0xffff2022U
#define APC_MODE_SNAPSHOT 0xffff24c9U
#define PAYLOAD 0xffff3ad5U

#define PERIODIC_WRAPPER 0x000d3860U
#define SELECTOR_ARBITER 0x000d3880U
#define STARTUP_WRAPPER 0x000d38a0U
#define RL_ENGINE 0x000d38e4U
#define IGNITION_ADAPTER 0x000d3ea0U
#define IGNITION_CONTROLLER 0x000d40c0U
#define THRESHOLD_HELPER 0x000d4140U
#define FEEDBACK_ARBITER 0x000d41e0U
#define FEEDBACK_COUNTS 0x000d3848U

#ifndef TARGET_VQ37_ROLLING
#define FUEL_STOCK 0x0000934eU
#endif

#define PHASE_IDLE 0U
#define PHASE_ACTIVE 1U
#define PHASE_COOLDOWN 2U

#define MODE_OBSERVE 0U
#define MODE_RPM_HOLD 1U
#define MODE_RPM_HOLD_RETARD 2U

#define BUTTON_ZERO 0x00U
#define BUTTON_CANCEL 0x02U
#define BUTTON_SET 0x08U
#define BUTTON_RELEASED 0x20U

#define REASON_NONE 0U
#define REASON_CONFIG_INVALID 1U
#define REASON_MAP_INDEX_INVALID 2U
#define REASON_MAP_DISABLED 3U
#define REASON_SELECTOR_BUSY 4U
#define REASON_FEEDBACK_BUSY 5U
#define REASON_ASCD_ACTIVE 6U
#define REASON_BUTTON_RELEASED 7U
#define REASON_BUTTON_INVALID 8U
#define REASON_SPEED_LOW 9U
#define REASON_RPM_LOW 10U
#define REASON_PEDAL_LOW 11U
#define REASON_COOLANT_OUTSIDE 12U
#define REASON_TIMEOUT 14U
#define REASON_MAP_REQUEST 15U
#define REASON_STATE_CORRUPT 16U
#define REASON_MAP_CHANGED 17U
#define REASON_MODE_CHANGED 18U

#define FLAG_TIMER_OK 0x0800U
#define FLAG_BUTTON_HELD 0x0020U
#define FLAGS_OBSERVE_ACTIVE 0x1bffU
#define FLAGS_RPM_ACTIVE 0x5bffU
#define FLAGS_RPM_FUEL_CUT_ACTIVE 0x7bffU
#define FLAGS_RETARD_ACTIVE 0xdbffU

extern uint32_t invoke_r4(uint32_t entry, uint32_t argument);
extern uint32_t invoke_r0(uint32_t entry);

static size_t case_count;

static const uint8_t valid_configuration[32] = {
    0x52, 0x4c, 0x03, 0x00, 0x01, 0x00, 0x00, 0xff,
    0x01, 0x10, 0x00, 0x64, 0x00, 0x01, 0x00, 0x10,
    0x04, 0x0c, 0x00, 0x04, 0x00, 0x03, 0x73, 0x73,
    0x73, 0x73, 0x73, 0x14, 0xad, 0xb3, 0xa5, 0x5a,
};

static const uint8_t payload_seed[8] = {
    0x11, 0x22, 0x33, 0x44, 0x55, 0xb5, 0x77, 0x88,
};

#ifdef TARGET_VQ37_ROLLING
static const uint32_t fuel_cap_slots[5] = {
    0x00009040U, 0x000d24f4U, 0x000d24f8U, 0x000d24fcU,
    0x000d353cU,
};

static const uint32_t fuel_curve_slots[5] = {
    0x00016bf4U, 0x000d36e0U, 0x000d3700U, 0x000d3720U,
    0x000d3740U,
};
#else
static const uint32_t fuel_slots[5] = {
    0x0000934eU, 0x000d3500U, 0x000d3508U, 0x000d3510U,
    0x000d3518U,
};
#endif

static volatile uint8_t *ram_pointer(uint32_t original)
{
    uintptr_t address = TEST_RAM_BASE + (original & 0xffffU);
    return (volatile uint8_t *)address;
}

static volatile uint8_t *rom_pointer(uint32_t address)
{
    return (volatile uint8_t *)(uintptr_t)address;
}

static void fill_bytes(volatile uint8_t *target, size_t size, uint8_t value)
{
    size_t index;

    for (index = 0; index < size; ++index)
        target[index] = value;
}

static void write_bytes(
    volatile uint8_t *target, const uint8_t *source, size_t size)
{
    size_t index;

    for (index = 0; index < size; ++index)
        target[index] = source[index];
}

static uint16_t read_u16(const volatile uint8_t *source)
{
    return (uint16_t)((uint16_t)source[0] << 8) | source[1];
}

static void write_u16(volatile uint8_t *target, uint16_t value)
{
    target[0] = (uint8_t)(value >> 8);
    target[1] = (uint8_t)value;
}

static void write_u32(volatile uint8_t *target, uint32_t value)
{
    target[0] = (uint8_t)(value >> 24);
    target[1] = (uint8_t)(value >> 16);
    target[2] = (uint8_t)(value >> 8);
    target[3] = (uint8_t)value;
}

static int fail_value(
    const char *name, const char *field, uint32_t actual, uint32_t expected)
{
    printf(
        "VQ_SH_ELF_ROLLING_LAUNCH status=FAIL case=%s field=%s "
        "actual=%08lx expected=%08lx\n",
        name, field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}

static int fail_bytes(
    const char *name,
    const char *field,
    const volatile uint8_t *actual,
    const uint8_t *expected,
    size_t size)
{
    size_t index;

    for (index = 0; index < size; ++index) {
        if (actual[index] != expected[index]) {
            printf(
                "VQ_SH_ELF_ROLLING_LAUNCH status=FAIL case=%s field=%s "
                "offset=%lu actual=%02x expected=%02x\n",
                name, field, (unsigned long)index,
                (unsigned int)actual[index], (unsigned int)expected[index]);
            return 0;
        }
    }
    return 1;
}

static void count_case(void)
{
    ++case_count;
}

static void set_configuration(uint8_t mode, uint8_t enable_mask)
{
    write_bytes(rom_pointer(RL_CONFIG), valid_configuration, 32);
    rom_pointer(RL_CONFIG)[3] = mode;
    rom_pointer(RL_CONFIG)[4] = enable_mask;
}

static void reset_case(uint8_t mode, uint8_t enable_mask)
{
    volatile uint8_t *selector = ram_pointer(SELECTOR_STATE);

    fill_bytes(selector, 8, 0);
    fill_bytes(ram_pointer(RL_STATE_GUARD), RL_STATE_SIZE + 8U, 0xa5);
    fill_bytes(ram_pointer(RL_STATE), RL_STATE_SIZE, 0);
    fill_bytes(ram_pointer(FUEL_SHADOW), FUEL_SHADOW_SIZE, 0xa5);
    fill_bytes(
        ram_pointer(THROTTLE_SHADOW), THROTTLE_SHADOW_SIZE, 0xa5);
    fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_CANCEL;
    ram_pointer(BUTTON_CODE)[1] = BUTTON_CANCEL;
    ram_pointer(ASCD_STATUS)[0] = 0;
    ram_pointer(SPEED)[0] = 20;
    write_u16(ram_pointer(RPM), 300);
    write_u16(ram_pointer(PEDAL), 2000);
    ram_pointer(COOLANT)[0] = 100;
    ram_pointer(FORMER_BRAKE_STATUS)[0] = 0;
    ram_pointer(FUEL_CUT_STATUS)[0] = 0;
#ifdef TARGET_VQ37_ROLLING
    ram_pointer(FUEL_FINAL_MASK)[0] = 0;
#endif
    ram_pointer(IGNITION_OUTPUT)[0] = 0;
    ram_pointer(APC_MODE_SNAPSHOT)[0] = 0;
    write_bytes(ram_pointer(PAYLOAD), payload_seed, sizeof(payload_seed));
    set_configuration(mode, enable_mask);
}

static void run_engine(void)
{
    (void)invoke_r4(RL_ENGINE, 0);
}

static int expect_phase_reason(
    const char *name, uint8_t phase, uint8_t reason)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);

    if (state[0] != phase)
        return fail_value(name, "phase", state[0], phase);
    if (state[1] != reason)
        return fail_value(name, "abort_reason", state[1], reason);
    return 1;
}

static int verify_state_guards(const char *name)
{
    volatile uint8_t *guard = ram_pointer(RL_STATE_GUARD);
    size_t index;

    for (index = 0; index < 4; ++index) {
        if (guard[index] != 0xa5)
            return fail_value(name, "guard_before", guard[index], 0xa5);
    }
    for (index = RL_STATE_SIZE + 4U;
         index < RL_STATE_SIZE + 8U; ++index) {
        if (guard[index] != 0xa5)
            return fail_value(name, "guard_after", guard[index], 0xa5);
    }
    return 1;
}

static int verify_corrupt_recovery(const char *name)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);
    size_t index;

    if (!expect_phase_reason(name, PHASE_COOLDOWN, REASON_STATE_CORRUPT))
        return 0;
    for (index = 2; index < RL_STATE_SIZE; ++index) {
        if (state[index] != 0)
            return fail_value(name, "cleared_state", state[index], 0);
    }
    if (!verify_state_guards(name))
        return 0;
    return 1;
}

static int verify_fuel_restored(const char *name, size_t slot)
{
#ifdef TARGET_VQ37_ROLLING
    uint8_t expected[FUEL_SHADOW_SIZE];
    size_t index;

    for (index = 0; index < 4; ++index)
        expected[index] = rom_pointer(fuel_cap_slots[slot])[index];
    for (index = 0; index < 32; ++index)
        expected[index + 4] = rom_pointer(fuel_curve_slots[slot])[index];
#else
    uint8_t expected[12];
    size_t index;

    for (index = 0; index < 8; ++index)
        expected[index] = rom_pointer(fuel_slots[slot])[index];
    for (index = 8; index < 12; ++index)
        expected[index] = rom_pointer(FUEL_STOCK)[index];
#endif
    return fail_bytes(
        name, "fuel_restore", ram_pointer(FUEL_SHADOW), expected,
        sizeof(expected));
}

static int verify_engine_fuel_release(const char *name, size_t slot)
{
    return verify_fuel_restored(name, slot);
}

static int verify_fuel_untouched(const char *name)
{
    uint8_t expected[FUEL_SHADOW_SIZE];
    size_t index;

    for (index = 0; index < sizeof(expected); ++index)
        expected[index] = 0xa5;
    return fail_bytes(
        name, "fuel_write", ram_pointer(FUEL_SHADOW), expected,
        sizeof(expected));
}

struct structural_case {
    const char *name;
    uint8_t phase;
    uint8_t map;
    uint8_t mode;
    uint16_t run_ticks;
    uint16_t rearm_ticks;
};

static const struct structural_case structural_cases[] = {
    {"invalid-phase", 3, 0, 0, 0, 0},
    {"idle-map-snapshot", 0, 5, 0, 0, 0},
    {"idle-mode-snapshot", 0, 0, 1, 0, 0},
    {"idle-run-ticks", 0, 0, 0, 1, 0},
    {"idle-rearm-ticks", 0, 0, 0, 0, 1},
    {"active-map-snapshot", 1, 5, 1, 0, 0},
    {"active-mode-snapshot", 1, 0, 3, 0, 0},
    {"active-rearm-ticks", 1, 0, 1, 0, 1},
    {"cooldown-map-snapshot", 2, 5, 1, 0, 0},
    {"cooldown-mode-snapshot", 2, 0, 3, 0, 0},
    {"cooldown-rearm-range", 2, 0, 1, 0, 0x8000},
};

static int run_structural_cases(void)
{
    size_t index;

    for (index = 0; index < ARRAY_SIZE(structural_cases); ++index) {
        const struct structural_case *test = &structural_cases[index];
        volatile uint8_t *state;

        count_case();
        reset_case(MODE_RPM_HOLD, 0x01);
        state = ram_pointer(RL_STATE);
        state[0] = test->phase;
        state[4] = test->map;
        state[5] = test->mode;
        write_u16(state + 6, test->run_ticks);
        write_u16(state + 8, test->rearm_ticks);
#ifdef TARGET_VQ37_ROLLING
        write_u16(state + FUEL_REQUEST_LATCH_OFFSET, 1);
#endif
        run_engine();
        if (!verify_corrupt_recovery(test->name))
            return 0;
        if (!verify_engine_fuel_release(test->name, 0))
            return 0;
    }
    return 1;
}

enum gate_mutation {
    GATE_MAP_INDEX,
    GATE_MAP_DISABLED,
    GATE_SELECTOR_PHASE,
    GATE_SELECTOR_COUNT,
    GATE_SELECTOR_ELAPSED,
    GATE_FEEDBACK_PULSES,
    GATE_FEEDBACK_PHASE,
    GATE_FEEDBACK_TICKS,
    GATE_FEEDBACK_RESERVED,
    GATE_ASCD,
    GATE_ASCD_FOREIGN_FLAGS,
    GATE_BUTTON_RELEASED,
    GATE_BUTTON_ZERO,
    GATE_BUTTON_SET,
    GATE_SPEED_LOW,
    GATE_SPEED_EXACT,
    GATE_SPEED_DISABLED,
    GATE_RPM_LOW,
    GATE_RPM_EXACT,
    GATE_PEDAL_LOW,
    GATE_PEDAL_EXACT,
    GATE_PEDAL_DISABLED,
    GATE_COOLANT_LOW,
    GATE_COOLANT_HIGH,
    GATE_COOLANT_MIN,
    GATE_COOLANT_MAX,
    GATE_FORMER_BRAKE_SIGNAL,
};

struct gate_case {
    const char *name;
    enum gate_mutation mutation;
    uint8_t expected_reason;
    uint8_t succeeds;
};

static const struct gate_case gate_cases[] = {
    {"gate-map-index", GATE_MAP_INDEX, REASON_MAP_INDEX_INVALID, 0},
    {"gate-map-disabled", GATE_MAP_DISABLED, REASON_MAP_DISABLED, 0},
    {"gate-selector-phase", GATE_SELECTOR_PHASE, REASON_SELECTOR_BUSY, 0},
    {"gate-selector-count", GATE_SELECTOR_COUNT, REASON_SELECTOR_BUSY, 0},
    {"gate-selector-elapsed", GATE_SELECTOR_ELAPSED, REASON_SELECTOR_BUSY, 0},
    {"gate-feedback-pulses", GATE_FEEDBACK_PULSES, REASON_FEEDBACK_BUSY, 0},
    {"gate-feedback-phase", GATE_FEEDBACK_PHASE, REASON_FEEDBACK_BUSY, 0},
    {"gate-feedback-ticks", GATE_FEEDBACK_TICKS, REASON_FEEDBACK_BUSY, 0},
    {"gate-feedback-reserved", GATE_FEEDBACK_RESERVED, REASON_FEEDBACK_BUSY, 0},
    {"gate-ascd", GATE_ASCD, REASON_ASCD_ACTIVE, 0},
    {"gate-ascd-foreign-flags", GATE_ASCD_FOREIGN_FLAGS, REASON_NONE, 1},
    {"gate-button-released", GATE_BUTTON_RELEASED, REASON_BUTTON_INVALID, 0},
    {"gate-button-zero", GATE_BUTTON_ZERO, REASON_BUTTON_INVALID, 0},
    {"gate-button-set", GATE_BUTTON_SET, REASON_BUTTON_INVALID, 0},
    {"gate-speed-low", GATE_SPEED_LOW, REASON_SPEED_LOW, 0},
    {"gate-speed-exact", GATE_SPEED_EXACT, REASON_NONE, 1},
    {"gate-speed-disabled", GATE_SPEED_DISABLED, REASON_NONE, 1},
    {"gate-rpm-low", GATE_RPM_LOW, REASON_RPM_LOW, 0},
    {"gate-rpm-exact", GATE_RPM_EXACT, REASON_NONE, 1},
    {"gate-pedal-low", GATE_PEDAL_LOW, REASON_PEDAL_LOW, 0},
    {"gate-pedal-exact", GATE_PEDAL_EXACT, REASON_NONE, 1},
    {"gate-pedal-disabled", GATE_PEDAL_DISABLED, REASON_NONE, 1},
    {"gate-coolant-low", GATE_COOLANT_LOW, REASON_COOLANT_OUTSIDE, 0},
    {"gate-coolant-high", GATE_COOLANT_HIGH, REASON_COOLANT_OUTSIDE, 0},
    {"gate-coolant-min", GATE_COOLANT_MIN, REASON_NONE, 1},
    {"gate-coolant-max", GATE_COOLANT_MAX, REASON_NONE, 1},
    {"gate-former-brake-signal", GATE_FORMER_BRAKE_SIGNAL, REASON_NONE, 1},
};

static void apply_gate_mutation(enum gate_mutation mutation)
{
    volatile uint8_t *selector = ram_pointer(SELECTOR_STATE);
    volatile uint8_t *config = rom_pointer(RL_CONFIG);

    switch (mutation) {
    case GATE_MAP_INDEX:
        selector[0] = 5;
        break;
    case GATE_MAP_DISABLED:
        config[4] = 0;
        break;
    case GATE_SELECTOR_PHASE:
        selector[1] = 1;
        break;
    case GATE_SELECTOR_COUNT:
        selector[2] = 1;
        break;
    case GATE_SELECTOR_ELAPSED:
        selector[3] = 1;
        break;
    case GATE_FEEDBACK_PULSES:
        selector[4] = 1;
        break;
    case GATE_FEEDBACK_PHASE:
        selector[5] = 1;
        break;
    case GATE_FEEDBACK_TICKS:
        selector[6] = 1;
        break;
    case GATE_FEEDBACK_RESERVED:
        selector[7] = 1;
        break;
    case GATE_ASCD:
        ram_pointer(ASCD_STATUS)[0] = ASCD_MAIN;
        break;
    case GATE_ASCD_FOREIGN_FLAGS:
        ram_pointer(ASCD_STATUS)[0] = ASCD_FOREIGN_FLAGS;
        break;
    case GATE_BUTTON_RELEASED:
        ram_pointer(BUTTON_CODE)[0] = BUTTON_RELEASED;
        break;
    case GATE_BUTTON_ZERO:
        ram_pointer(BUTTON_CODE)[0] = BUTTON_ZERO;
        break;
    case GATE_BUTTON_SET:
        ram_pointer(BUTTON_CODE)[0] = BUTTON_SET;
        break;
    case GATE_SPEED_LOW:
        config[8] = 10;
        ram_pointer(SPEED)[0] = 9;
        break;
    case GATE_SPEED_EXACT:
        config[8] = 10;
        ram_pointer(SPEED)[0] = 10;
        break;
    case GATE_SPEED_DISABLED:
        config[8] = 0;
        ram_pointer(SPEED)[0] = 0;
        break;
    case GATE_RPM_LOW:
        write_u16(config + 10, 200);
        write_u16(ram_pointer(RPM), 199);
        break;
    case GATE_RPM_EXACT:
        write_u16(config + 10, 200);
        write_u16(ram_pointer(RPM), 200);
        break;
    case GATE_PEDAL_LOW:
        write_u16(config + 12, 100);
        write_u16(ram_pointer(PEDAL), 99);
        break;
    case GATE_PEDAL_EXACT:
        write_u16(config + 12, 100);
        write_u16(ram_pointer(PEDAL), 100);
        break;
    case GATE_PEDAL_DISABLED:
        write_u16(config + 12, 0);
        write_u16(ram_pointer(PEDAL), 0);
        break;
    case GATE_COOLANT_LOW:
        config[6] = 10;
        config[7] = 200;
        ram_pointer(COOLANT)[0] = 9;
        break;
    case GATE_COOLANT_HIGH:
        config[6] = 10;
        config[7] = 200;
        ram_pointer(COOLANT)[0] = 201;
        break;
    case GATE_COOLANT_MIN:
        config[6] = 10;
        config[7] = 200;
        ram_pointer(COOLANT)[0] = 10;
        break;
    case GATE_COOLANT_MAX:
        config[6] = 10;
        config[7] = 200;
        ram_pointer(COOLANT)[0] = 200;
        break;
    case GATE_FORMER_BRAKE_SIGNAL:
        ram_pointer(FORMER_BRAKE_STATUS)[0] = 0x80;
        break;
    }
}

static int run_gate_cases(void)
{
    size_t index;

    for (index = 0; index < ARRAY_SIZE(gate_cases); ++index) {
        const struct gate_case *test = &gate_cases[index];

        count_case();
        reset_case(MODE_OBSERVE, 0x01);
        apply_gate_mutation(test->mutation);
        run_engine();
        if (test->succeeds) {
            if (!expect_phase_reason(test->name, PHASE_ACTIVE, REASON_NONE))
                return 0;
        }
        else if (!expect_phase_reason(
                     test->name, PHASE_IDLE, test->expected_reason))
            return 0;
        if (!verify_state_guards(test->name))
            return 0;
    }
    return 1;
}

struct config_case {
    const char *name;
    uint8_t offset;
    uint8_t width;
    uint32_t value;
};

static const struct config_case config_cases[] = {
    {"config-magic", 0, 2, 0},
    {"config-schema", 2, 1, 1},
    {"config-mode", 3, 1, 3},
    {"config-enable-mask", 4, 1, 0x20},
    {"config-options-low", 5, 1, 1},
    {"config-options-high", 5, 1, 0x80},
    {"config-coolant-order", 6, 2, 0xff00},
    {"config-retard-ramp-zero", 9, 1, 0},
    {"config-retard-ramp-offset", 9, 1, 17},
    {"config-rpm-zero", 10, 2, 0},
    {"config-offset-zero", 14, 2, 0},
    {"config-min-hysteresis-zero", 16, 1, 0},
    {"config-min-hysteresis-above-max", 16, 1, 13},
    {"config-max-hysteresis-below-min", 17, 1, 3},
    {"config-max-hysteresis-at-offset", 17, 1, 16},
    {"config-timeout-zero", 18, 2, 0},
    {"config-timeout-range", 18, 2, 0x8000},
    {"config-rearm-zero", 20, 2, 0},
    {"config-rearm-range", 20, 2, 0x8000},
    {"config-target-low", 22, 1, 109},
    {"config-target-high", 22, 1, 118},
    {"config-hysteresis-ratio-zero", 27, 1, 0},
    {"config-inverse", 28, 2, 0},
    {"config-end", 30, 2, 0},
};

static void apply_config_value(const struct config_case *test)
{
    volatile uint8_t *target = rom_pointer(RL_CONFIG) + test->offset;

    if (test->width == 1)
        target[0] = (uint8_t)test->value;
    else if (test->width == 2)
        write_u16(target, (uint16_t)test->value);
    else
        write_u32(target, test->value);
}

static int run_config_cases(void)
{
    size_t index;

    for (index = 0; index < ARRAY_SIZE(config_cases); ++index) {
        const struct config_case *test = &config_cases[index];

        count_case();
        reset_case(MODE_OBSERVE, 0x01);
        apply_config_value(test);
        run_engine();
        if (!expect_phase_reason(
                test->name, PHASE_IDLE, REASON_CONFIG_INVALID))
            return 0;
    }
    return 1;
}

static int verify_overlay(
    const char *name, uint16_t cut, uint16_t restore)
{
#ifdef TARGET_VQ37_ROLLING
    uint8_t expected[FUEL_SHADOW_SIZE];

    /* Activation leaves the selected map storage unchanged. Engine speed is
       the captured value, below cut, so no request is published yet. */
    (void)cut;
    (void)restore;
    for (size_t index = 0; index < sizeof(expected); ++index)
        expected[index] = 0xa5;
    if (!fail_bytes(
            name, "fuel_map_storage", ram_pointer(FUEL_SHADOW), expected,
            sizeof(expected)))
        return 0;
    if (read_u16(ram_pointer(RL_STATE) + FUEL_REQUEST_OFFSET) != 0)
        return fail_value(
            name, "fuel_request",
            read_u16(ram_pointer(RL_STATE) + FUEL_REQUEST_OFFSET), 0);
    if (read_u16(ram_pointer(RL_STATE) + FUEL_REQUEST_LATCH_OFFSET) != 0)
        return fail_value(
            name, "fuel_request_latch",
            read_u16(ram_pointer(RL_STATE) + FUEL_REQUEST_LATCH_OFFSET), 0);
    return 1;
#else
    uint8_t expected[8];

    expected[0] = (uint8_t)(cut >> 8);
    expected[1] = (uint8_t)cut;
    expected[2] = expected[0];
    expected[3] = expected[1];
    expected[4] = (uint8_t)(restore >> 8);
    expected[5] = (uint8_t)restore;
    expected[6] = expected[4];
    expected[7] = expected[5];
    if (!fail_bytes(
            name, "fuel_overlay", ram_pointer(FUEL_SHADOW), expected, 8))
        return 0;
    if (
        ram_pointer(FUEL_SHADOW)[8] != 0xa5
        || ram_pointer(FUEL_SHADOW)[9] != 0xa5
        || ram_pointer(FUEL_SHADOW)[10] != 0xa5
        || ram_pointer(FUEL_SHADOW)[11] != 0xa5
    )
        return fail_value(name, "fuel_tail", 0, 0xa5a5a5a5U);
    return 1;
#endif
}

static int verify_active_state(
    const char *name,
    uint8_t mode,
    uint16_t captured,
    uint16_t cut,
    uint16_t restore,
    uint16_t retard_band_start,
    uint16_t flags)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);

    if (!expect_phase_reason(name, PHASE_ACTIVE, REASON_NONE))
        return 0;
    if (state[4] != 0 || state[5] != mode)
        return fail_value(name, "map_mode", state[5], mode);
    if (read_u16(state + 2) != flags)
        return fail_value(name, "flags", read_u16(state + 2), flags);
    if (read_u16(state + 10) != captured)
        return fail_value(name, "captured", read_u16(state + 10), captured);
    if (read_u16(state + 12) != cut)
        return fail_value(name, "cut", read_u16(state + 12), cut);
    if (read_u16(state + 14) != restore)
        return fail_value(name, "restore", read_u16(state + 14), restore);
    if (read_u16(state + 18) != retard_band_start)
        return fail_value(
            name, "retard_band_start", read_u16(state + 18),
            retard_band_start);
#ifdef TARGET_VQ37_ROLLING
    /* The activation pass runs at the captured speed, below cut, in every
       mode. */
    if (read_u16(state + FUEL_REQUEST_OFFSET) != 0)
        return fail_value(
            name, "fuel_request", read_u16(state + FUEL_REQUEST_OFFSET), 0);
    if (read_u16(state + FUEL_REQUEST_LATCH_OFFSET) != 0)
        return fail_value(
            name, "fuel_request_latch",
            read_u16(state + FUEL_REQUEST_LATCH_OFFSET), 0);
#endif
    return verify_state_guards(name);
}

static int run_threshold_helper_case(
    const char *name,
    uint16_t captured,
    uint16_t cut,
    uint16_t expected_restore,
    uint16_t expected_band_start)
{
    volatile uint8_t *state;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    rom_pointer(RL_CONFIG)[9] = 8;
    state = ram_pointer(RL_STATE);
    write_u16(state + 10, captured);
    write_u16(state + 12, cut);
    (void)invoke_r4(THRESHOLD_HELPER, 0);
    if (read_u16(state + 14) != expected_restore)
        return fail_value(
            name, "restore", read_u16(state + 14), expected_restore);
    if (read_u16(state + 18) != expected_band_start)
        return fail_value(
            name, "retard_band_start", read_u16(state + 18),
            expected_band_start);
    return verify_state_guards(name);
}

static int run_threshold_helper_cases(void)
{
    if (!run_threshold_helper_case(
            "threshold-minimum", 160, 176, 172, 168))
        return 0;
    if (!run_threshold_helper_case(
            "threshold-proportional", 400, 416, 408, 400))
        return 0;
    if (!run_threshold_helper_case(
            "threshold-maximum", 600, 616, 604, 600))
        return 0;
    if (!run_threshold_helper_case(
            "threshold-saturated", 0xfff8, 0xffff, 0xfff3, 0xfff8))
        return 0;
    return 1;
}

static int run_activation_cases(void)
{
    volatile uint8_t *state;

    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    run_engine();
    if (!verify_active_state(
            "activate-observe", MODE_OBSERVE, 300, 316, 310, 300,
            FLAGS_OBSERVE_ACTIVE))
        return 0;
    if (!verify_fuel_untouched("activate-observe"))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    run_engine();
    if (!verify_active_state(
            "activate-rpm", MODE_RPM_HOLD, 300, 316, 310, 300,
            FLAGS_RPM_ACTIVE))
        return 0;
    if (!verify_overlay("activate-rpm", 316, 310))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    write_u16(ram_pointer(RPM), 0xfff8);
    run_engine();
    if (!verify_active_state(
            "activate-saturated", MODE_RPM_HOLD, 0xfff8, 0xffff,
            0xfff3, 0xfff8, FLAGS_RPM_ACTIVE))
        return 0;
    if (!verify_overlay("activate-saturated", 0xffff, 0xfff3))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    run_engine();
    if (!verify_active_state(
            "activate-retard", MODE_RPM_HOLD_RETARD, 300, 316, 310, 300,
            FLAGS_RETARD_ACTIVE))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    ram_pointer(FUEL_CUT_STATUS)[0] = FUEL_CUT_ACTIVE;
    run_engine();
    state = ram_pointer(RL_STATE);
    if (read_u16(state + 2) != FLAGS_RPM_FUEL_CUT_ACTIVE)
        return fail_value(
            "activate-fuel-cut", "flags", read_u16(state + 2),
            FLAGS_RPM_FUEL_CUT_ACTIVE);

    /* Every other bit of the state byte leaves the flag clear, and on the
       VQ37VHR layouts so does a final mask that inhibits all six cylinders,
       as the wrapper leaves it after a Rolling Launch request. */
    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    ram_pointer(FUEL_CUT_STATUS)[0] = (uint8_t)~FUEL_CUT_ACTIVE;
#ifdef TARGET_VQ37_ROLLING
    ram_pointer(FUEL_FINAL_MASK)[0] = 0x3fU;
#endif
    run_engine();
    if (read_u16(state + 2) != FLAGS_RPM_ACTIVE)
        return fail_value(
            "activate-fuel-cut-other-bits", "flags", read_u16(state + 2),
            FLAGS_RPM_ACTIVE);
    return 1;
}

static int activate(uint8_t mode, uint8_t mask)
{
    reset_case(mode, mask);
    run_engine();
    return ram_pointer(RL_STATE)[0] == PHASE_ACTIVE;
}

static int run_active_cases(void)
{
    volatile uint8_t *state;

    count_case();
    if (!activate(MODE_RPM_HOLD, 0x01))
        return fail_value("active-normal", "setup", 0, 1);
    run_engine();
    state = ram_pointer(RL_STATE);
    if (!expect_phase_reason("active-normal", PHASE_ACTIVE, REASON_NONE))
        return 0;
    if (read_u16(state + 6) != 1)
        return fail_value("active-normal", "run_ticks", read_u16(state + 6), 1);

    count_case();
    if (!activate(MODE_RPM_HOLD, 0x01))
        return fail_value("active-timeout", "setup", 0, 1);
    write_u16(rom_pointer(RL_CONFIG) + 18, 2);
    run_engine();
    run_engine();
    if (!expect_phase_reason(
            "active-timeout", PHASE_COOLDOWN, REASON_TIMEOUT))
        return 0;
    if (read_u16(ram_pointer(RL_STATE) + 2) & FLAG_TIMER_OK)
        return fail_value("active-timeout", "timer_flag", 1, 0);
    if (!verify_engine_fuel_release("active-timeout", 0))
        return 0;

    count_case();
    if (!activate(MODE_RPM_HOLD, 0x03))
        return fail_value("active-map-change", "setup", 0, 1);
    ram_pointer(SELECTOR_STATE)[0] = 1;
    run_engine();
    if (!expect_phase_reason(
            "active-map-change", PHASE_COOLDOWN, REASON_MAP_CHANGED))
        return 0;
    if (!verify_engine_fuel_release("active-map-change", 0))
        return 0;

    count_case();
    if (!activate(MODE_RPM_HOLD, 0x01))
        return fail_value("active-mode-change", "setup", 0, 1);
    rom_pointer(RL_CONFIG)[3] = MODE_RPM_HOLD_RETARD;
    run_engine();
    if (!expect_phase_reason(
            "active-mode-change", PHASE_COOLDOWN, REASON_MODE_CHANGED))
        return 0;

    count_case();
    if (!activate(MODE_RPM_HOLD, 0x01))
        return fail_value("active-map-request", "setup", 0, 1);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_SET;
    run_engine();
    if (!expect_phase_reason(
            "active-map-request", PHASE_COOLDOWN, REASON_MAP_REQUEST))
        return 0;

    count_case();
    if (!activate(MODE_RPM_HOLD, 0x01))
        return fail_value("active-release", "setup", 0, 1);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_RELEASED;
    run_engine();
    if (!expect_phase_reason(
            "active-release", PHASE_COOLDOWN, REASON_BUTTON_RELEASED))
        return 0;
    if (!verify_engine_fuel_release("active-release", 0))
        return 0;

    count_case();
    if (!activate(MODE_RPM_HOLD, 0x01))
        return fail_value("active-invalid-button", "setup", 0, 1);
    ram_pointer(BUTTON_CODE)[0] = 4;
    run_engine();
    if (!expect_phase_reason(
            "active-invalid-button", PHASE_COOLDOWN, REASON_BUTTON_INVALID))
        return 0;

    count_case();
    if (!activate(MODE_RPM_HOLD, 0x01))
        return fail_value("active-config-invalid", "setup", 0, 1);
    rom_pointer(RL_CONFIG)[0] = 0;
    run_engine();
    if (!expect_phase_reason(
            "active-config-invalid", PHASE_COOLDOWN,
            REASON_CONFIG_INVALID))
        return 0;

    count_case();
    if (!activate(MODE_OBSERVE, 0x01))
        return fail_value("active-observe-release", "setup", 0, 1);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_RELEASED;
    run_engine();
    if (!expect_phase_reason(
            "active-observe-release", PHASE_COOLDOWN,
            REASON_BUTTON_RELEASED))
        return 0;
    if (!verify_fuel_untouched("active-observe-release"))
        return 0;
    return 1;
}

static void set_cooldown(uint16_t rearm)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);

    state[0] = PHASE_COOLDOWN;
    state[1] = REASON_BUTTON_RELEASED;
    state[4] = 0;
    state[5] = MODE_RPM_HOLD;
    write_u16(state + 8, rearm);
}

static int run_cooldown_cases(void)
{
    volatile uint8_t *state;

    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    set_cooldown(2);
    rom_pointer(RL_CONFIG)[0] = 0;
    run_engine();
    state = ram_pointer(RL_STATE);
    if (!expect_phase_reason(
            "cooldown-config", PHASE_COOLDOWN, REASON_CONFIG_INVALID))
        return 0;
    if (read_u16(state + 8) != 0)
        return fail_value("cooldown-config", "rearm", read_u16(state + 8), 0);

    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    set_cooldown(2);
    run_engine();
    if (read_u16(ram_pointer(RL_STATE) + 8) != 0)
        return fail_value("cooldown-held", "rearm", read_u16(ram_pointer(RL_STATE) + 8), 0);

    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    set_cooldown(0);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_RELEASED;
    run_engine();
    if (read_u16(ram_pointer(RL_STATE) + 8) != 1)
        return fail_value("cooldown-increment", "rearm", read_u16(ram_pointer(RL_STATE) + 8), 1);

    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    set_cooldown(2);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_RELEASED;
    run_engine();
    state = ram_pointer(RL_STATE);
    if (!expect_phase_reason(
            "cooldown-complete", PHASE_IDLE, REASON_BUTTON_RELEASED))
        return 0;
    if (state[5] != MODE_OBSERVE || read_u16(state + 8) != 0)
        return fail_value("cooldown-complete", "reset", state[5], 0);

    ram_pointer(BUTTON_CODE)[0] = BUTTON_CANCEL;
    run_engine();
    if (!expect_phase_reason(
            "cooldown-complete", PHASE_ACTIVE, REASON_NONE))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    set_cooldown(2);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_ZERO;
    run_engine();
    state = ram_pointer(RL_STATE);
    if (!expect_phase_reason(
            "cooldown-zero", PHASE_COOLDOWN, REASON_BUTTON_RELEASED))
        return 0;
    if (read_u16(state + 8) != 0)
        return fail_value(
            "cooldown-zero", "rearm", read_u16(state + 8), 0);
    return 1;
}

static int invoke_ignition(
    const char *name, uint8_t stock, uint16_t rpm, uint8_t expected)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);
    uint32_t returned;

    write_u16(ram_pointer(RPM), rpm);
    ram_pointer(IGNITION_OUTPUT)[0] = stock;
    returned = invoke_r4(IGNITION_ADAPTER, stock);
    if (returned != expected)
        return fail_value(name, "returned", returned, expected);
    if (ram_pointer(IGNITION_OUTPUT)[0] != expected)
        return fail_value(
            name, "output", ram_pointer(IGNITION_OUTPUT)[0], expected);
    if (state[16] != stock || state[17] != expected)
        return fail_value(name, "diagnostic", state[17], expected);
    return 1;
}

static void set_ignition_state(uint8_t phase, uint8_t mode, uint8_t map)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);

    state[0] = phase;
    state[4] = map;
    state[5] = mode;
    write_u16(state + 10, 300);
    write_u16(state + 12, 316);
    write_u16(state + 14, 310);
    write_u16(state + 18, 300);
}

static int run_ignition_cases(void)
{
    static const struct config_case invalid[] = {
        {"ign-magic", 0, 2, 0},
        {"ign-schema", 2, 1, 1},
        {"ign-config-mode", 3, 1, MODE_RPM_HOLD},
        {"ign-disabled", 4, 1, 0},
        {"ign-markers", 28, 4, 0},
        {"ign-ramp-zero", 9, 1, 0},
        {"ign-target-low", 22, 1, 109},
        {"ign-target-high", 22, 1, 118},
    };
    size_t index;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_IDLE, MODE_OBSERVE, 0);
    if (!invoke_ignition("ign-inactive", 110, 316, 110))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD, 0);
    if (!invoke_ignition("ign-wrong-mode", 110, 316, 110))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    if (!invoke_ignition("ign-band-start", 110, 300, 110))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    if (!invoke_ignition("ign-band-quarter", 110, 304, 111))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    if (!invoke_ignition("ign-band-restore", 110, 308, 112))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    if (!invoke_ignition("ign-band-three-quarter", 110, 312, 113))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    if (!invoke_ignition("ign-band-near-cut", 110, 315, 114))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    if (!invoke_ignition("ign-band-cut", 110, 316, 115))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    if (!invoke_ignition("ign-band-above", 110, 320, 115))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    if (!invoke_ignition("ign-stock-max", 117, 316, 117))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    ram_pointer(APC_MODE_SNAPSHOT)[0] = 0x40;
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    if (!invoke_ignition("ign-apc-fallback", 110, 316, 110))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    ram_pointer(APC_MODE_SNAPSHOT)[0] = 0x20;
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    if (!invoke_ignition("ign-apc-bit-five", 110, 316, 115))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 5);
    if (!invoke_ignition("ign-index-invalid", 110, 316, 110))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x10);
    rom_pointer(RL_CONFIG)[22] = 110;
    rom_pointer(RL_CONFIG)[23] = 111;
    rom_pointer(RL_CONFIG)[24] = 112;
    rom_pointer(RL_CONFIG)[25] = 113;
    rom_pointer(RL_CONFIG)[26] = 114;
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 4);
    if (!invoke_ignition("ign-map-five-target", 110, 316, 114))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    write_u16(ram_pointer(RL_STATE) + 10, 316);
    write_u16(ram_pointer(RL_STATE) + 12, 316);
    write_u16(ram_pointer(RL_STATE) + 18, 316);
    if (!invoke_ignition("ign-zero-width", 110, 316, 110))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    write_u16(ram_pointer(RL_STATE) + 10, 0xfff8);
    write_u16(ram_pointer(RL_STATE) + 12, 0xffff);
    write_u16(ram_pointer(RL_STATE) + 18, 0xfff8);
    if (!invoke_ignition("ign-saturated-band", 110, 0xfffc, 112))
        return 0;

    for (index = 0; index < ARRAY_SIZE(invalid); ++index) {
        count_case();
        reset_case(MODE_RPM_HOLD_RETARD, 0x01);
        set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
        apply_config_value(&invalid[index]);
        if (!invoke_ignition(invalid[index].name, 110, 316, 110))
            return 0;
    }
    return 1;
}

struct feedback_case {
    const char *name;
    uint8_t phase;
    uint8_t reason;
    uint16_t flags;
    uint8_t initial_map_feedback[4];
    uint8_t expected_status;
    uint8_t expected_map_feedback[4];
};

static const struct feedback_case feedback_cases[] = {
    {
        "feedback-idle-released", PHASE_IDLE, REASON_RPM_LOW, 0,
        {0, 0, 0, 0}, 0xb5, {0, 0, 0, 0},
    },
    {
        "feedback-failed-held", PHASE_IDLE, REASON_RPM_LOW,
        FLAG_BUTTON_HELD, {0, 0, 0, 0}, 0xd5, {0, 0, 0, 0},
    },
    {
        "feedback-active", PHASE_ACTIVE, REASON_NONE,
        FLAGS_OBSERVE_ACTIVE, {0, 0, 0, 0}, 0xc5, {0, 0, 0, 0},
    },
    {
        "feedback-cooldown", PHASE_COOLDOWN, REASON_TIMEOUT, 0,
        {0, 0, 0, 0}, 0x85, {0, 0, 0, 0},
    },
    {
        "feedback-corrupt", 3, REASON_STATE_CORRUPT, 0,
        {0, 0, 0, 0}, 0xb5, {0, 0, 0, 0},
    },
    {
        /* Map ON is state 4 like ACTIVE, so the failed-attempt state 5 is the
         * Rolling Launch value that a lost priority would expose here. */
        "feedback-map-on-priority", PHASE_IDLE, REASON_RPM_LOW,
        FLAG_BUTTON_HELD, {1, 1, 0, 0}, 0xc5, {1, 2, 0, 0},
    },
    {
        "feedback-map-off-priority", PHASE_ACTIVE, REASON_NONE,
        FLAGS_OBSERVE_ACTIVE, {1, 2, 0, 0}, 0x85, {0, 0, 0, 0},
    },
};

static int run_feedback_cases(void)
{
    size_t case_index;

    for (case_index = 0; case_index < ARRAY_SIZE(feedback_cases);
         ++case_index) {
        const struct feedback_case *test = &feedback_cases[case_index];
        volatile uint8_t *selector;
        volatile uint8_t *state;
        size_t index;

        count_case();
        reset_case(MODE_OBSERVE, 0x01);
        selector = ram_pointer(SELECTOR_STATE);
        state = ram_pointer(RL_STATE);
        state[0] = test->phase;
        state[1] = test->reason;
        write_u16(state + 2, test->flags);
        write_bytes(
            selector + 4, test->initial_map_feedback,
            sizeof(test->initial_map_feedback));
        rom_pointer(FEEDBACK_COUNTS)[0] = 1;
        rom_pointer(FEEDBACK_COUNTS)[1] = 1;

        (void)invoke_r4(FEEDBACK_ARBITER, 0);

        for (index = 0; index < sizeof(payload_seed); ++index) {
            uint8_t expected = index == 5
                ? test->expected_status
                : payload_seed[index];
            if (ram_pointer(PAYLOAD)[index] != expected)
                return fail_value(
                    test->name, "payload",
                    ram_pointer(PAYLOAD)[index], expected);
        }
        if (!fail_bytes(
                test->name, "map_feedback", selector + 4,
                test->expected_map_feedback,
                sizeof(test->expected_map_feedback)))
            return 0;
        if (
            state[0] != test->phase
            || state[1] != test->reason
            || read_u16(state + 2) != test->flags
        )
            return fail_value(
                test->name, "rolling_state", read_u16(state + 2),
                test->flags);
        if (!verify_state_guards(test->name))
            return 0;
    }
    return 1;
}

static int run_wrapper_cases(void)
{
    volatile uint8_t *selector;
    uint8_t before[8];
    size_t index;

    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    fill_bytes(ram_pointer(RL_STATE), RL_STATE_SIZE, 0xa5);
    (void)invoke_r4(STARTUP_WRAPPER, 0xa5);
    for (index = 0; index < RL_STATE_SIZE; ++index) {
        if (ram_pointer(RL_STATE)[index] != 0)
            return fail_value("wrapper-startup", "state", ram_pointer(RL_STATE)[index], 0);
    }
    if (!verify_engine_fuel_release("wrapper-startup", 0))
        return 0;
    if (!verify_state_guards("wrapper-startup"))
        return 0;

    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    selector = ram_pointer(SELECTOR_STATE);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_SET;
    ram_pointer(BUTTON_CODE)[1] = BUTTON_RELEASED;
    (void)invoke_r4(SELECTOR_ARBITER, 0);
    if (selector[1] != 1 || selector[3] != 1)
        return fail_value("wrapper-selector-idle", "selector_phase", selector[1], 1);

    for (index = PHASE_ACTIVE; index <= 3; ++index) {
        const char *name = index == PHASE_ACTIVE
            ? "wrapper-selector-active"
            : (index == PHASE_COOLDOWN
                ? "wrapper-selector-cooldown"
                : "wrapper-selector-corrupt");

        count_case();
        reset_case(MODE_OBSERVE, 0x01);
        selector = ram_pointer(SELECTOR_STATE);
        selector[0] = 2;
        selector[1] = 1;
        selector[2] = 3;
        selector[3] = 7;
        for (size_t byte = 0; byte < sizeof(before); ++byte)
            before[byte] = selector[byte];
        ram_pointer(RL_STATE)[0] = (uint8_t)index;
        ram_pointer(BUTTON_CODE)[0] = BUTTON_SET;
        ram_pointer(BUTTON_CODE)[1] = BUTTON_RELEASED;
        (void)invoke_r4(SELECTOR_ARBITER, 0);
        if (!fail_bytes(name, "selector", selector, before, sizeof(before)))
            return 0;
    }

    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    (void)invoke_r4(PERIODIC_WRAPPER, 0);
    if (!expect_phase_reason(
            "wrapper-periodic", PHASE_ACTIVE, REASON_NONE))
        return 0;
    return 1;
}

#ifdef TARGET_VQ37_ROLLING
struct fuel_wrapper_case {
    const char *name;
    uint16_t request;
    uint8_t expected_mask;
};

static const struct fuel_wrapper_case fuel_wrapper_cases[] = {
    {"fuel-wrapper-inactive", 0x0000U, FUEL_STOCK_MASK},
    {"fuel-wrapper-corrupt-request", 0x003eU, FUEL_STOCK_MASK},
    {"fuel-wrapper-active", FUEL_REQUEST_MASK, FUEL_REQUESTED_MASK},
};

static int run_fuel_wrapper_cases(void)
{
    size_t index;

    for (index = 0; index < ARRAY_SIZE(fuel_wrapper_cases); ++index) {
        const struct fuel_wrapper_case *test = &fuel_wrapper_cases[index];
        volatile uint8_t *state;
        uint32_t returned;

        count_case();
        reset_case(MODE_RPM_HOLD, 0x01);
        state = ram_pointer(RL_STATE);
        write_u16(state + FUEL_REQUEST_OFFSET, test->request);
        ram_pointer(FUEL_FINAL_MASK)[0] = 0x12U;
        ram_pointer(FUEL_CUT_STATUS)[0] = FUEL_CUT_ACTIVE;
        returned = invoke_r0(FUEL_CUT_WRAPPER);
        if (returned != FUEL_STOCK_MASK)
            return fail_value(
                test->name, "stock_return", returned, FUEL_STOCK_MASK);
        if (ram_pointer(FUEL_FINAL_MASK)[0] != test->expected_mask)
            return fail_value(
                test->name, "fuel_mask",
                ram_pointer(FUEL_FINAL_MASK)[0], test->expected_mask);
        if (ram_pointer(FUEL_CUT_STATUS)[0] != FUEL_CUT_ACTIVE)
            return fail_value(
                test->name, "fuel_cut_state",
                ram_pointer(FUEL_CUT_STATUS)[0], FUEL_CUT_ACTIVE);
        if (read_u16(state + FUEL_REQUEST_OFFSET) != test->request)
            return fail_value(
                test->name, "fuel_request",
                read_u16(state + FUEL_REQUEST_OFFSET), test->request);
        if (!verify_state_guards(test->name))
            return 0;
    }
    return 1;
}

/* Check the phase, the request and its latch after an engine pass, then run
   the coordinator wrapper and check the final mask it leaves. */
static int expect_hold(
    const char *name, uint8_t phase, uint16_t request, uint16_t latch)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);
    uint8_t expected_mask = request == FUEL_REQUEST_MASK
        ? FUEL_REQUESTED_MASK
        : FUEL_STOCK_MASK;
    uint32_t returned;

    if (state[0] != phase)
        return fail_value(name, "phase", state[0], phase);
    if (read_u16(state + FUEL_REQUEST_OFFSET) != request)
        return fail_value(
            name, "fuel_request", read_u16(state + FUEL_REQUEST_OFFSET),
            request);
    if (read_u16(state + FUEL_REQUEST_LATCH_OFFSET) != latch)
        return fail_value(
            name, "fuel_request_latch",
            read_u16(state + FUEL_REQUEST_LATCH_OFFSET), latch);
    ram_pointer(FUEL_FINAL_MASK)[0] = 0x12U;
    returned = invoke_r0(FUEL_CUT_WRAPPER);
    if (returned != FUEL_STOCK_MASK)
        return fail_value(name, "stock_return", returned, FUEL_STOCK_MASK);
    if (ram_pointer(FUEL_FINAL_MASK)[0] != expected_mask)
        return fail_value(
            name, "fuel_mask", ram_pointer(FUEL_FINAL_MASK)[0],
            expected_mask);
    return verify_state_guards(name);
}

/* One ACTIVE pass at an engine speed. The selected map storage stays
   unchanged while the request holds or releases. */
static int hold_step(
    const char *name, uint16_t rpm, uint16_t request, uint16_t latch)
{
    write_u16(ram_pointer(RPM), rpm);
    run_engine();
    if (!expect_hold(name, PHASE_ACTIVE, request, latch))
        return 0;
    return verify_fuel_untouched(name);
}

/* Activation at the reset speed 300 captures cut 316 and restore 310. The
   longer run timeout leaves room for every pass of a case. */
static void reset_hold_case(uint8_t mode)
{
    reset_case(mode, 0x01);
    write_u16(rom_pointer(RL_CONFIG) + 18, 0x0100);
}

static int activate_hold(uint8_t mode)
{
    reset_hold_case(mode);
    run_engine();
    return ram_pointer(RL_STATE)[0] == PHASE_ACTIVE;
}

static int run_hold_cases(void)
{
    volatile uint8_t *state;

    count_case();
    if (!activate_hold(MODE_RPM_HOLD))
        return fail_value("hold-below-cut", "setup", 0, 1);
    if (!hold_step("hold-below-cut", 315, 0, 0))
        return 0;

    count_case();
    if (!activate_hold(MODE_RPM_HOLD))
        return fail_value("hold-at-cut", "setup", 0, 1);
    if (!hold_step("hold-at-cut", 316, FUEL_REQUEST_MASK, 1))
        return 0;

    count_case();
    if (!activate_hold(MODE_RPM_HOLD))
        return fail_value("hold-above-cut", "setup", 0, 1);
    if (!hold_step("hold-above-cut", 400, FUEL_REQUEST_MASK, 1))
        return 0;

    count_case();
    if (!activate_hold(MODE_RPM_HOLD))
        return fail_value("hold-latched-between", "setup", 0, 1);
    if (!hold_step("hold-latched-between", 316, FUEL_REQUEST_MASK, 1))
        return 0;
    if (!hold_step("hold-latched-between", 313, FUEL_REQUEST_MASK, 1))
        return 0;

    count_case();
    if (!activate_hold(MODE_RPM_HOLD))
        return fail_value("hold-latched-at-restore", "setup", 0, 1);
    if (!hold_step("hold-latched-at-restore", 316, FUEL_REQUEST_MASK, 1))
        return 0;
    if (!hold_step("hold-latched-at-restore", 310, FUEL_REQUEST_MASK, 1))
        return 0;

    /* Below restore the request releases, stays released between the
       thresholds, and latches again at cut. */
    count_case();
    if (!activate_hold(MODE_RPM_HOLD))
        return fail_value("hold-release", "setup", 0, 1);
    if (!hold_step("hold-release", 316, FUEL_REQUEST_MASK, 1))
        return 0;
    if (!hold_step("hold-release", 309, 0, 0))
        return 0;
    if (!hold_step("hold-release", 313, 0, 0))
        return 0;
    if (!hold_step("hold-release", 316, FUEL_REQUEST_MASK, 1))
        return 0;

    count_case();
    if (!activate_hold(MODE_RPM_HOLD_RETARD))
        return fail_value("hold-retard", "setup", 0, 1);
    if (!hold_step("hold-retard", 316, FUEL_REQUEST_MASK, 1))
        return 0;
    if (!hold_step("hold-retard", 309, 0, 0))
        return 0;

    count_case();
    if (!activate_hold(MODE_OBSERVE))
        return fail_value("hold-observe", "setup", 0, 1);
    if (!hold_step("hold-observe", 400, 0, 0))
        return 0;

    /* A latch other than 1 publishes no request until a threshold sets or
       releases it. */
    count_case();
    if (!activate_hold(MODE_RPM_HOLD))
        return fail_value("hold-foreign-latch", "setup", 0, 1);
    write_u16(ram_pointer(RL_STATE) + FUEL_REQUEST_LATCH_OFFSET, 2);
    if (!hold_step("hold-foreign-latch", 313, 0, 2))
        return 0;
    if (!hold_step("hold-foreign-latch", 316, FUEL_REQUEST_MASK, 1))
        return 0;

    /* An abort clears the latch with the request and republishes the
       captured map. */
    count_case();
    if (!activate_hold(MODE_RPM_HOLD))
        return fail_value("hold-abort", "setup", 0, 1);
    if (!hold_step("hold-abort", 316, FUEL_REQUEST_MASK, 1))
        return 0;
    ram_pointer(BUTTON_CODE)[0] = BUTTON_RELEASED;
    run_engine();
    if (!expect_phase_reason(
            "hold-abort", PHASE_COOLDOWN, REASON_BUTTON_RELEASED))
        return 0;
    if (!expect_hold("hold-abort", PHASE_COOLDOWN, 0, 0))
        return 0;
    if (!verify_engine_fuel_release("hold-abort", 0))
        return 0;

    /* Activation clears a latch left in IDLE. The saturated capture puts
       the captured speed between restore and cut, where a kept latch would
       publish the request. */
    count_case();
    reset_hold_case(MODE_RPM_HOLD);
    state = ram_pointer(RL_STATE);
    write_u16(state + FUEL_REQUEST_LATCH_OFFSET, 1);
    write_u16(ram_pointer(RPM), 0xfff8);
    run_engine();
    if (!expect_hold("hold-activation-latch", PHASE_ACTIVE, 0, 0))
        return 0;
    if (read_u16(state + 12) != 0xffff || read_u16(state + 14) != 0xfff3)
        return fail_value(
            "hold-activation-latch", "thresholds", read_u16(state + 14),
            0xfff3);
    if (!hold_step("hold-activation-latch", 0xffff, FUEL_REQUEST_MASK, 1))
        return 0;
    return 1;
}
#endif

int main(void)
{
    if (!run_structural_cases())
        return 1;
    if (!run_gate_cases())
        return 1;
    if (!run_config_cases())
        return 1;
    if (!run_threshold_helper_cases())
        return 1;
    if (!run_activation_cases())
        return 1;
    if (!run_active_cases())
        return 1;
    if (!run_cooldown_cases())
        return 1;
    if (!run_ignition_cases())
        return 1;
    if (!run_wrapper_cases())
        return 1;
    if (!run_feedback_cases())
        return 1;
#ifdef TARGET_VQ37_ROLLING
    if (!run_fuel_wrapper_cases())
        return 1;
    if (!run_hold_cases())
        return 1;
    if (case_count != 137U)
        return fail_value("summary", "case_count", case_count, 137);

    printf(
        "VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=%lu "
        "structural=11 gates=27 config=24 threshold=4 activation=6 "
        "active=9 cooldown=5 ignition=24 wrappers=6 feedback=7 "
        "fuel_coordinator=3 hold=11 entries=9\n",
        (unsigned long)case_count);
#else
    if (case_count != 123U)
        return fail_value("summary", "case_count", case_count, 123);

    printf(
        "VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=%lu "
        "structural=11 gates=27 config=24 threshold=4 activation=6 "
        "active=9 cooldown=5 ignition=24 wrappers=6 feedback=7 "
        "entries=8\n",
        (unsigned long)case_count);
#endif
    return 0;
}
