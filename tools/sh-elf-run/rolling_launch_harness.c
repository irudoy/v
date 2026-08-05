#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))

#define TEST_RAM_BASE 0x01000000U
#define SELECTOR_STATE 0xffff5d00U
#define FUEL_SHADOW 0xffff5d10U
#define THROTTLE_SHADOW 0xffff5d20U
#define THROTTLE_RUNTIME 0xffff1796U
#define RL_STATE_GUARD 0xffff5d3cU
#define RL_STATE 0xffff5d40U
#define RL_STATE_SIZE 20U
#define RL_CONFIG 0x000d3f60U
#define BUTTON_CODE 0xffff2a85U
#define ASCD_STATUS 0xffff41aeU
#define SPEED 0xffff110eU
#define RPM 0xffff11bcU
#define PEDAL 0xffff2672U
#define COOLANT 0xffff1077U
#define BRAKE_STATUS 0xffff2451U
#define FUEL_CUT_STATUS 0xffff2497U
#define IGNITION_OUTPUT 0xffff2022U
#define APC_MODE_SNAPSHOT 0xffff24c9U

#define PERIODIC_WRAPPER 0x000d3860U
#define SELECTOR_ARBITER 0x000d3880U
#define STARTUP_WRAPPER 0x000d38a0U
#define RL_ENGINE 0x000d38e4U
#define IGNITION_ADAPTER 0x000d3ea0U

#define FUEL_STOCK 0x0000934eU

#define PHASE_IDLE 0U
#define PHASE_ACTIVE 1U
#define PHASE_COOLDOWN 2U

#define MODE_OBSERVE 0U
#define MODE_RPM_HOLD 1U
#define MODE_RPM_HOLD_RETARD 2U

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
#define REASON_BRAKE_ACTIVE 13U
#define REASON_TIMEOUT 14U
#define REASON_MAP_REQUEST 15U
#define REASON_STATE_CORRUPT 16U
#define REASON_MAP_CHANGED 17U
#define REASON_MODE_CHANGED 18U

#define FLAG_TIMER_OK 0x0800U
#define FLAGS_OBSERVE_ACTIVE 0x1fffU
#define FLAGS_RPM_ACTIVE 0x5fffU
#define FLAGS_RPM_FUEL_CUT_ACTIVE 0x7fffU
#define FLAGS_RETARD_ACTIVE 0xdfffU

extern uint32_t invoke_r4(uint32_t entry, uint32_t argument);

static size_t case_count;

static const uint8_t valid_configuration[32] = {
    0x52, 0x4c, 0x01, 0x00, 0x01, 0x00, 0x00, 0xff,
    0x01, 0x00, 0x00, 0x64, 0x00, 0x01, 0x00, 0x10,
    0x00, 0x08, 0x00, 0x04, 0x00, 0x03, 0x73, 0x73,
    0x73, 0x73, 0x73, 0x00, 0xad, 0xb3, 0xa5, 0x5a,
};

static const uint32_t fuel_slots[5] = {
    0x0000934eU, 0x000d3500U, 0x000d3508U, 0x000d3510U,
    0x000d3518U,
};

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
    fill_bytes(ram_pointer(RL_STATE_GUARD), 28, 0xa5);
    fill_bytes(ram_pointer(RL_STATE), RL_STATE_SIZE, 0);
    fill_bytes(ram_pointer(FUEL_SHADOW), 12, 0xa5);
    fill_bytes(ram_pointer(THROTTLE_SHADOW), 28, 0xa5);
    fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
    ram_pointer(BUTTON_CODE)[0] = 0x02;
    ram_pointer(BUTTON_CODE)[1] = 0x02;
    ram_pointer(ASCD_STATUS)[0] = 0;
    ram_pointer(SPEED)[0] = 20;
    write_u16(ram_pointer(RPM), 300);
    write_u16(ram_pointer(PEDAL), 2000);
    ram_pointer(COOLANT)[0] = 100;
    ram_pointer(BRAKE_STATUS)[0] = 0;
    ram_pointer(FUEL_CUT_STATUS)[0] = 0;
    ram_pointer(IGNITION_OUTPUT)[0] = 0;
    ram_pointer(APC_MODE_SNAPSHOT)[0] = 0;
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
    for (index = 24; index < 28; ++index) {
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
    uint8_t expected[12];
    size_t index;

    for (index = 0; index < 8; ++index)
        expected[index] = rom_pointer(fuel_slots[slot])[index];
    for (index = 8; index < 12; ++index)
        expected[index] = rom_pointer(FUEL_STOCK)[index];
    return fail_bytes(
        name, "fuel_restore", ram_pointer(FUEL_SHADOW), expected,
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
        run_engine();
        if (!verify_corrupt_recovery(test->name))
            return 0;
        if (!verify_fuel_restored(test->name, 0))
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
    GATE_BUTTON_RELEASED,
    GATE_BUTTON_SET,
    GATE_SPEED_LOW,
    GATE_SPEED_EXACT,
    GATE_RPM_LOW,
    GATE_RPM_EXACT,
    GATE_PEDAL_LOW,
    GATE_PEDAL_EXACT,
    GATE_COOLANT_LOW,
    GATE_COOLANT_HIGH,
    GATE_COOLANT_MIN,
    GATE_COOLANT_MAX,
    GATE_BRAKE_BLOCKED,
    GATE_BRAKE_IGNORED,
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
    {"gate-button-released", GATE_BUTTON_RELEASED, REASON_BUTTON_INVALID, 0},
    {"gate-button-set", GATE_BUTTON_SET, REASON_BUTTON_INVALID, 0},
    {"gate-speed-low", GATE_SPEED_LOW, REASON_SPEED_LOW, 0},
    {"gate-speed-exact", GATE_SPEED_EXACT, REASON_NONE, 1},
    {"gate-rpm-low", GATE_RPM_LOW, REASON_RPM_LOW, 0},
    {"gate-rpm-exact", GATE_RPM_EXACT, REASON_NONE, 1},
    {"gate-pedal-low", GATE_PEDAL_LOW, REASON_PEDAL_LOW, 0},
    {"gate-pedal-exact", GATE_PEDAL_EXACT, REASON_NONE, 1},
    {"gate-coolant-low", GATE_COOLANT_LOW, REASON_COOLANT_OUTSIDE, 0},
    {"gate-coolant-high", GATE_COOLANT_HIGH, REASON_COOLANT_OUTSIDE, 0},
    {"gate-coolant-min", GATE_COOLANT_MIN, REASON_NONE, 1},
    {"gate-coolant-max", GATE_COOLANT_MAX, REASON_NONE, 1},
    {"gate-brake-blocked", GATE_BRAKE_BLOCKED, REASON_BRAKE_ACTIVE, 0},
    {"gate-brake-ignored", GATE_BRAKE_IGNORED, REASON_NONE, 1},
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
        ram_pointer(ASCD_STATUS)[0] = 0x80;
        break;
    case GATE_BUTTON_RELEASED:
        ram_pointer(BUTTON_CODE)[0] = 0;
        break;
    case GATE_BUTTON_SET:
        ram_pointer(BUTTON_CODE)[0] = 8;
        break;
    case GATE_SPEED_LOW:
        config[8] = 10;
        ram_pointer(SPEED)[0] = 9;
        break;
    case GATE_SPEED_EXACT:
        config[8] = 10;
        ram_pointer(SPEED)[0] = 10;
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
    case GATE_BRAKE_BLOCKED:
        config[5] = 1;
        ram_pointer(BRAKE_STATUS)[0] = 0x80;
        break;
    case GATE_BRAKE_IGNORED:
        config[5] = 0;
        ram_pointer(BRAKE_STATUS)[0] = 0x80;
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
    {"config-schema", 2, 1, 2},
    {"config-mode", 3, 1, 3},
    {"config-enable-mask", 4, 1, 0x20},
    {"config-options", 5, 1, 2},
    {"config-coolant-order", 6, 2, 0xff00},
    {"config-speed-zero", 8, 1, 0},
    {"config-speed-padding", 9, 1, 1},
    {"config-rpm-zero", 10, 2, 0},
    {"config-pedal-zero", 12, 2, 0},
    {"config-offset-zero", 14, 2, 0},
    {"config-hysteresis-zero", 16, 2, 0},
    {"config-hysteresis-range", 16, 2, 100},
    {"config-timeout-zero", 18, 2, 0},
    {"config-timeout-range", 18, 2, 0x8000},
    {"config-rearm-zero", 20, 2, 0},
    {"config-rearm-range", 20, 2, 0x8000},
    {"config-target-low", 22, 1, 109},
    {"config-target-high", 22, 1, 118},
    {"config-reserved", 27, 1, 1},
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
}

static int verify_active_state(
    const char *name,
    uint8_t mode,
    uint16_t captured,
    uint16_t cut,
    uint16_t restore,
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
    return verify_state_guards(name);
}

static int run_activation_cases(void)
{
    volatile uint8_t *state;

    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    run_engine();
    if (!verify_active_state(
            "activate-observe", MODE_OBSERVE, 300, 316, 308,
            FLAGS_OBSERVE_ACTIVE))
        return 0;
    if (
        ram_pointer(FUEL_SHADOW)[0] != 0xa5
        || ram_pointer(FUEL_SHADOW)[11] != 0xa5
    )
        return fail_value("activate-observe", "fuel_write", 1, 0);

    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    run_engine();
    if (!verify_active_state(
            "activate-rpm", MODE_RPM_HOLD, 300, 316, 308,
            FLAGS_RPM_ACTIVE))
        return 0;
    if (!verify_overlay("activate-rpm", 316, 308))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    write_u16(ram_pointer(RPM), 0xfff8);
    run_engine();
    if (!verify_active_state(
            "activate-saturated", MODE_RPM_HOLD, 0xfff8, 0xffff,
            0xfff7, FLAGS_RPM_ACTIVE))
        return 0;
    if (!verify_overlay("activate-saturated", 0xffff, 0xfff7))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    run_engine();
    if (!verify_active_state(
            "activate-retard", MODE_RPM_HOLD_RETARD, 300, 316, 308,
            FLAGS_RETARD_ACTIVE))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    ram_pointer(FUEL_CUT_STATUS)[0] = 0x04;
    run_engine();
    state = ram_pointer(RL_STATE);
    if (read_u16(state + 2) != FLAGS_RPM_FUEL_CUT_ACTIVE)
        return fail_value(
            "activate-fuel-cut", "flags", read_u16(state + 2),
            FLAGS_RPM_FUEL_CUT_ACTIVE);
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
    if (!verify_fuel_restored("active-timeout", 0))
        return 0;

    count_case();
    if (!activate(MODE_RPM_HOLD, 0x03))
        return fail_value("active-map-change", "setup", 0, 1);
    ram_pointer(SELECTOR_STATE)[0] = 1;
    run_engine();
    if (!expect_phase_reason(
            "active-map-change", PHASE_COOLDOWN, REASON_MAP_CHANGED))
        return 0;
    if (!verify_fuel_restored("active-map-change", 0))
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
    ram_pointer(BUTTON_CODE)[0] = 8;
    run_engine();
    if (!expect_phase_reason(
            "active-map-request", PHASE_COOLDOWN, REASON_MAP_REQUEST))
        return 0;

    count_case();
    if (!activate(MODE_RPM_HOLD, 0x01))
        return fail_value("active-release", "setup", 0, 1);
    ram_pointer(BUTTON_CODE)[0] = 0;
    run_engine();
    if (!expect_phase_reason(
            "active-release", PHASE_COOLDOWN, REASON_BUTTON_RELEASED))
        return 0;
    if (!verify_fuel_restored("active-release", 0))
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
    ram_pointer(BUTTON_CODE)[0] = 0;
    run_engine();
    if (!expect_phase_reason(
            "active-observe-release", PHASE_COOLDOWN,
            REASON_BUTTON_RELEASED))
        return 0;
    if (
        ram_pointer(FUEL_SHADOW)[0] != 0xa5
        || ram_pointer(FUEL_SHADOW)[11] != 0xa5
    )
        return fail_value("active-observe-release", "fuel_write", 1, 0);
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
    ram_pointer(BUTTON_CODE)[0] = 0;
    run_engine();
    if (read_u16(ram_pointer(RL_STATE) + 8) != 1)
        return fail_value("cooldown-increment", "rearm", read_u16(ram_pointer(RL_STATE) + 8), 1);

    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    set_cooldown(2);
    ram_pointer(BUTTON_CODE)[0] = 0;
    run_engine();
    state = ram_pointer(RL_STATE);
    if (!expect_phase_reason(
            "cooldown-complete", PHASE_IDLE, REASON_BUTTON_RELEASED))
        return 0;
    if (state[5] != MODE_OBSERVE || read_u16(state + 8) != 0)
        return fail_value("cooldown-complete", "reset", state[5], 0);
    return 1;
}

static int invoke_ignition(
    const char *name, uint8_t stock, uint8_t expected)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);
    uint32_t returned;

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
}

static int run_ignition_cases(void)
{
    static const struct config_case invalid[] = {
        {"ign-magic", 0, 2, 0},
        {"ign-schema", 2, 1, 2},
        {"ign-config-mode", 3, 1, MODE_RPM_HOLD},
        {"ign-disabled", 4, 1, 0},
        {"ign-markers", 28, 4, 0},
        {"ign-target-low", 22, 1, 109},
        {"ign-target-high", 22, 1, 118},
    };
    size_t index;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_IDLE, MODE_OBSERVE, 0);
    if (!invoke_ignition("ign-inactive", 110, 110))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD, 0);
    if (!invoke_ignition("ign-wrong-mode", 110, 110))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    if (!invoke_ignition("ign-target-max", 110, 115))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    if (!invoke_ignition("ign-stock-max", 117, 117))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    ram_pointer(APC_MODE_SNAPSHOT)[0] = 0x40;
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    if (!invoke_ignition("ign-apc-fallback", 110, 110))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    ram_pointer(APC_MODE_SNAPSHOT)[0] = 0x20;
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
    if (!invoke_ignition("ign-apc-bit-five", 110, 115))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x01);
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 5);
    if (!invoke_ignition("ign-index-invalid", 110, 110))
        return 0;

    count_case();
    reset_case(MODE_RPM_HOLD_RETARD, 0x10);
    rom_pointer(RL_CONFIG)[22] = 110;
    rom_pointer(RL_CONFIG)[23] = 111;
    rom_pointer(RL_CONFIG)[24] = 112;
    rom_pointer(RL_CONFIG)[25] = 113;
    rom_pointer(RL_CONFIG)[26] = 114;
    set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 4);
    if (!invoke_ignition("ign-map-five-target", 110, 114))
        return 0;

    for (index = 0; index < ARRAY_SIZE(invalid); ++index) {
        count_case();
        reset_case(MODE_RPM_HOLD_RETARD, 0x01);
        set_ignition_state(PHASE_ACTIVE, MODE_RPM_HOLD_RETARD, 0);
        apply_config_value(&invalid[index]);
        if (!invoke_ignition(invalid[index].name, 110, 110))
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
    if (!verify_fuel_restored("wrapper-startup", 0))
        return 0;
    if (!verify_state_guards("wrapper-startup"))
        return 0;

    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    selector = ram_pointer(SELECTOR_STATE);
    ram_pointer(BUTTON_CODE)[0] = 8;
    ram_pointer(BUTTON_CODE)[1] = 0;
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
        ram_pointer(BUTTON_CODE)[0] = 8;
        ram_pointer(BUTTON_CODE)[1] = 0;
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

int main(void)
{
    if (!run_structural_cases())
        return 1;
    if (!run_gate_cases())
        return 1;
    if (!run_config_cases())
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
    if (case_count != 96U)
        return fail_value("summary", "case_count", case_count, 96);

    printf(
        "VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=%lu "
        "structural=11 gates=24 config=22 activation=5 active=9 "
        "cooldown=4 ignition=15 wrappers=6 entries=5\n",
        (unsigned long)case_count);
    return 0;
}
