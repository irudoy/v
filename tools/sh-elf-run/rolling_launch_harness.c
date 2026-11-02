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
#define FUEL_SHADOW_SIZE 12U
#define THROTTLE_SHADOW 0xffff5d20U
#define THROTTLE_SHADOW_SIZE 28U
/* The engine owns the first 28 bytes of the state; the spark-cut actuator
   owns the rest. */
#define RL_ENGINE_STATE_SIZE 28U
#define RL_STATE_SIZE 44U
#define RL_CONFIG 0x000d6040U
#define RL_CONFIG_SIZE 40U
#define BUTTON_CODE 0xffff2a85U
#define ASCD_STATUS 0xffff41aeU
/* The ASCD task keeps the MAIN switch state in bit 7 of this flag byte; the
   other bits hold flags of other ASCD functions, which neither abort the
   selector nor fail the launch gate. */
#define ASCD_MAIN 0x80U
#define ASCD_FOREIGN_FLAGS ((uint8_t)~ASCD_MAIN)
/* The stock RPM fuel-cut state keeps its active cut in bit 2; the controller
   reports that bit in the fuel-cut flag, and the other bits of the byte leave
   the flag clear. */
#define FUEL_CUT_ACTIVE 0x04U
/* Vehicle speed in km/h*10 and the stock receive age of its CAN 0x284
   record, which advances once per 10.24 ms tick without a frame. */
#define SPEED 0xffff113cU
#define SPEED_AGE 0xffff3b38U
#define RPM 0xffff11bcU
#define PEDAL 0xffff2672U
#define COOLANT 0xffff1077U
#define FORMER_BRAKE_STATUS 0xffff2451U
#define FUEL_CUT_STATUS 0xffff2497U
#define IGNITION_OUTPUT 0xffff2022U
#define APC_MODE_SNAPSHOT 0xffff24c9U
#define PAYLOAD 0xffff3ad5U
#define FUEL_INHIBIT_MASK 0xffff22e0U
/* The simulator-only stock coordinator stub copies this cell into the final
   cylinder mask and returns COORDINATOR_RETURN. */
#define COORDINATOR_RESULT 0xffff6ff0U
#define COORDINATOR_RETURN 0xc0de22e0U
/* GR11A spark-cut actuator. TRAPA #0x40 enters the redirected vector, and
   the simulator-only stock-handler stub pushes SR at its entry into
   SPARK_ENTRY_SR and returns with RTE. The simulator sets SR bit 28 on
   exception entry, so a control handler measures the entry SR without the
   wrapper. */
#define SPARK_CUT 0x000d60c0U
#define SPARK_TABLE_ENTRY 0x000202e4U
#define SPARK_TRAP_VECTOR 0x00000100U
#define SPARK_ENTRY_SR 0xffff6fe8U
#define DWELL_VETO 0xffff8511U
#define SPARK_ARMED 0xffff8517U
#define CRANK_SYNC 0xffff8501U
#define DWELL_ANGLE 0xffff237aU
#define EVENT_CYLINDER 0xffff13c9U
#define MISFIRE_LATCH 0xffff436fU
#define MISFIRE_MARKER 0x01U
#define MISFIRE_RELEASE_EVENTS 14U
#define SPARK_CYLINDERS 6U
#define SPARK_CUT_ONE 6000U
#define SPARK_DWELL_LIMIT 110U
#define TORQUE_ONE 1000U

#define PERIODIC_WRAPPER 0x000d3860U
#define SELECTOR_ARBITER 0x000d3880U
#define STARTUP_WRAPPER 0x000d38a0U
#define RL_ENGINE 0x000d38e4U
#define IGNITION_ADAPTER 0x000d3ea0U
#define SPEED_CONTROLLER 0x000d40c0U
#define FEEDBACK_ARBITER 0x000d41e0U
#define FUEL_CUT_WRAPPER 0x000d6000U
#define SCHEDULER_TABLE 0x0002196cU
#define FEEDBACK_COUNTS 0x000d3848U

#define FUEL_STOCK 0x0000934eU

#define PHASE_IDLE 0U
#define PHASE_ACTIVE 1U
#define PHASE_COOLDOWN 2U

#define MODE_OBSERVE 0U
#define MODE_HOLD 1U

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
#define REASON_MAIN_PRESSED 6U
#define REASON_BUTTON_RELEASED 7U
#define REASON_BUTTON_INVALID 8U
#define REASON_SPEED_LOW 9U
#define REASON_RPM_LOW 10U
#define REASON_PEDAL_LOW 11U
#define REASON_COOLANT_OUTSIDE 12U
#define REASON_SPEED_FRAME_STALE 13U
#define REASON_TIMEOUT 14U
#define REASON_MAP_REQUEST 15U
#define REASON_STATE_CORRUPT 16U
#define REASON_MAP_CHANGED 17U
#define REASON_MODE_CHANGED 18U
#define REASON_SPEED_HIGH 19U
#define REASON_SPEED_ABOVE_WINDOW 20U
#define REASON_SPEED_BELOW_WINDOW 21U

#define FLAG_TIMER_OK 0x0800U
#define FLAG_BUTTON_HELD 0x0020U
#define FLAG_FUEL_CUT_BIT 0x2000U
#define FLAGS_GATES 0x0fffU
#define FLAGS_ACTIVE_OUTPUTS 0xf000U
#define FLAGS_OBSERVE_ACTIVE 0x1fffU
#define FLAGS_HOLD_ACTIVE 0x5fffU
#define FLAGS_HOLD_FUEL_CUT_ACTIVE 0x7fffU
#define FLAGS_HOLD_CEILING_ACTIVE 0xffffU
#define FUEL_CUT_REQUEST_ALL 0x003fU

/* Configuration record offsets. */
#define CFG_MODE 3U
#define CFG_ENABLE 4U
#define CFG_COOLANT_MIN 6U
#define CFG_COOLANT_MAX 7U
#define CFG_MIN_SPEED 8U
#define CFG_MAX_SPEED 10U
#define CFG_MIN_RPM 12U
#define CFG_MIN_PEDAL 14U
#define CFG_OFFSET 16U
#define CFG_RATE 20U
#define CFG_GAIN 22U
#define CFG_LIMIT 24U
#define CFG_TIMEOUT 30U
#define CFG_REARM 32U
#define CFG_AGE 34U
#define CFG_HYSTERESIS 35U

/* State record offsets. */
#define ST_FLAGS 2U
#define ST_RUN 6U
#define ST_REARM 8U
#define ST_CAPTURED 10U
#define ST_TARGET 12U
#define ST_FRACTION 14U
#define ST_ERROR 16U
#define ST_INTEGRATOR 18U
#define ST_REQUEST 20U
#define ST_COMMAND 22U
#define ST_LATCH 24U
#define ST_QUIET 28U
#define ST_CUTS 29U
#define ST_ACCUMULATORS 32U

extern uint32_t invoke_r4(uint32_t entry, uint32_t argument);
extern uint32_t invoke_r0(uint32_t entry);
extern void invoke_spark_probe(uint32_t *registers, uint32_t t_bit);
extern void spark_entry_sr_handler(void);

static size_t case_count;

/* Schema 4 with short run and rearm periods: speeds 20..120 km/h, 160 native
   RPM, window 4.0 km/h with top 2.0 km/h, rate 50, no integral gain,
   integrator limit 500, abort window +15.0/-10.0 km/h, ceiling offset 80,
   timeout 4, rearm 3, speed-frame age limit 10, and ceiling hysteresis 8. */
static const uint8_t valid_configuration[RL_CONFIG_SIZE] = {
    0x52, 0x4c, 0x04, 0x00, 0x01, 0x00, 0x00, 0xff,
    0x00, 0xc8, 0x04, 0xb0, 0x00, 0xa0, 0x00, 0x01,
    0x00, 0x00, 0x28, 0x14, 0x00, 0x32, 0x00, 0x00,
    0x01, 0xf4, 0x96, 0x64, 0x00, 0x50, 0x00, 0x04,
    0x00, 0x03, 0x0a, 0x08, 0xad, 0xb3, 0xa5, 0x5a,
};

static const uint8_t payload_seed[8] = {
    0x11, 0x22, 0x33, 0x44, 0x55, 0xb5, 0x77, 0x88,
};

/* Accumulator offsets of event cylinders 1..6, in firing order. */
static const uint16_t spark_offsets[SPARK_CYLINDERS] = {
    250, 2250, 4250, 1250, 3250, 5250,
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

static uint32_t read_u32(const volatile uint8_t *source)
{
    return ((uint32_t)read_u16(source) << 16) | read_u16(source + 2);
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
    write_bytes(rom_pointer(RL_CONFIG), valid_configuration, RL_CONFIG_SIZE);
    rom_pointer(RL_CONFIG)[CFG_MODE] = mode;
    rom_pointer(RL_CONFIG)[CFG_ENABLE] = enable_mask;
}

static void reset_case(uint8_t mode, uint8_t enable_mask)
{
    volatile uint8_t *selector = ram_pointer(SELECTOR_STATE);

    fill_bytes(selector, 8, 0);
    fill_bytes(ram_pointer(RL_STATE_GUARD), RL_STATE_SIZE + 8U, 0xa5);
    fill_bytes(ram_pointer(RL_STATE), RL_ENGINE_STATE_SIZE, 0);
    fill_bytes(ram_pointer(RL_STATE) + RL_ENGINE_STATE_SIZE,
               RL_STATE_SIZE - RL_ENGINE_STATE_SIZE, 0x3c);
    fill_bytes(ram_pointer(FUEL_SHADOW), FUEL_SHADOW_SIZE, 0xa5);
    fill_bytes(
        ram_pointer(THROTTLE_SHADOW), THROTTLE_SHADOW_SIZE, 0xa5);
    fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_CANCEL;
    ram_pointer(BUTTON_CODE)[1] = BUTTON_CANCEL;
    ram_pointer(ASCD_STATUS)[0] = 0;
    write_u16(ram_pointer(SPEED), 500);
    ram_pointer(SPEED_AGE)[0] = 0;
    write_u16(ram_pointer(RPM), 300);
    write_u16(ram_pointer(PEDAL), 2000);
    ram_pointer(COOLANT)[0] = 100;
    ram_pointer(FORMER_BRAKE_STATUS)[0] = 0;
    ram_pointer(FUEL_CUT_STATUS)[0] = 0;
    ram_pointer(IGNITION_OUTPUT)[0] = 0;
    ram_pointer(APC_MODE_SNAPSHOT)[0] = 0;
    write_bytes(ram_pointer(PAYLOAD), payload_seed, sizeof(payload_seed));
    ram_pointer(FUEL_INHIBIT_MASK)[0] = 0;
    ram_pointer(COORDINATOR_RESULT)[0] = 0;
    set_configuration(mode, enable_mask);
}

static void run_engine(void)
{
    (void)invoke_r4(RL_ENGINE, 0);
}

/* Scheduler entry 1: the displaced stock task, then the engine. */
static void run_periodic_entry(void)
{
    (void)invoke_r4(PERIODIC_WRAPPER, 0);
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
    for (index = 2; index < RL_ENGINE_STATE_SIZE; ++index) {
        if (state[index] != 0)
            return fail_value(name, "cleared_state", state[index], 0);
    }
    for (; index < RL_STATE_SIZE; ++index) {
        if (state[index] != 0x3c)
            return fail_value(name, "actuator_state", state[index], 0x3c);
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

static int verify_request(const char *name, uint16_t request)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);

    if (read_u16(state + ST_REQUEST) != request)
        return fail_value(
            name, "fuel_cut_request", read_u16(state + ST_REQUEST),
            request);
    return 1;
}

/* The buffers that no direct Rolling Launch entry may change. */
struct preserved_buffer {
    uint32_t address;
    size_t size;
    uint8_t bytes[28];
};

#define PRESERVED_BUFFERS                                               \
    {SELECTOR_STATE, 8, {0}}, {FUEL_SHADOW, FUEL_SHADOW_SIZE, {0}},     \
    {THROTTLE_SHADOW, THROTTLE_SHADOW_SIZE, {0}},                       \
    {THROTTLE_RUNTIME, 2, {0}}, {BUTTON_CODE, 2, {0}},                  \
    {ASCD_STATUS, 1, {0}}, {SPEED, 2, {0}}, {SPEED_AGE, 1, {0}},        \
    {RPM, 2, {0}}, {PEDAL, 2, {0}}, {COOLANT, 1, {0}},                  \
    {FORMER_BRAKE_STATUS, 1, {0}}, {FUEL_CUT_STATUS, 1, {0}},           \
    {IGNITION_OUTPUT, 1, {0}}, {APC_MODE_SNAPSHOT, 1, {0}},             \
    {PAYLOAD, 8, {0}}

static void capture_buffers(struct preserved_buffer *buffers, size_t count)
{
    size_t index, byte;

    for (index = 0; index < count; ++index)
        for (byte = 0; byte < buffers[index].size; ++byte)
            buffers[index].bytes[byte] =
                ram_pointer(buffers[index].address)[byte];
}

static int verify_buffers(
    const char *name, const struct preserved_buffer *buffers, size_t count)
{
    size_t index;

    for (index = 0; index < count; ++index)
        if (!fail_bytes(name, "preserved_buffer",
                        ram_pointer(buffers[index].address),
                        buffers[index].bytes, buffers[index].size))
            return 0;
    return 1;
}

struct structural_case {
    const char *name;
    uint8_t phase;
    uint8_t map;
    uint8_t mode;
    uint16_t run_ticks;
    uint16_t rearm_ticks;
    uint16_t fraction;
    uint16_t latch;
};

static const struct structural_case structural_cases[] = {
    {"invalid-phase", 3, 0, 0, 0, 0, 0, 0},
    {"idle-map-snapshot", 0, 5, 0, 0, 0, 0, 0},
    {"idle-mode-snapshot", 0, 0, 1, 0, 0, 0, 0},
    {"idle-run-ticks", 0, 0, 0, 1, 0, 0, 0},
    {"idle-rearm-ticks", 0, 0, 0, 0, 1, 0, 0},
    {"active-map-snapshot", 1, 5, 1, 0, 0, 1000, 0},
    {"active-mode-snapshot", 1, 0, 2, 0, 0, 1000, 0},
    {"active-rearm-ticks", 1, 0, 1, 0, 1, 1000, 0},
    {"active-fraction", 1, 0, 1, 0, 0, 1001, 0},
    {"cooldown-map-snapshot", 2, 5, 1, 0, 0, 0, 0},
    {"cooldown-mode-snapshot", 2, 0, 2, 0, 0, 0, 0},
    {"cooldown-rearm-range", 2, 0, 1, 0, 0x8000, 0, 0},
    {"active-ceiling-latch", 1, 0, 1, 0, 0, 1000, 2},
};

static int run_structural_cases(void)
{
    size_t index;

    for (index = 0; index < ARRAY_SIZE(structural_cases); ++index) {
        const struct structural_case *test = &structural_cases[index];
        volatile uint8_t *state;

        count_case();
        reset_case(MODE_HOLD, 0x01);
        state = ram_pointer(RL_STATE);
        state[0] = test->phase;
        state[4] = test->map;
        state[5] = test->mode;
        write_u16(state + ST_RUN, test->run_ticks);
        write_u16(state + ST_REARM, test->rearm_ticks);
        write_u16(state + ST_FRACTION, test->fraction);
        write_u16(state + ST_LATCH, test->latch);
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
    GATE_MAIN_PRESSED,
    GATE_MAIN_FOREIGN_FLAGS,
    GATE_BUTTON_RELEASED,
    GATE_BUTTON_ZERO,
    GATE_BUTTON_SET,
    GATE_FRAME_STALE,
    GATE_FRAME_EXACT,
    GATE_FRAME_SATURATED,
    GATE_FRAME_BEFORE_SPEED,
    GATE_SPEED_LOW,
    GATE_SPEED_MIN_EXACT,
    GATE_SPEED_HIGH,
    GATE_SPEED_MAX_EXACT,
    GATE_SPEED_MIN_DISABLED,
    GATE_SPEED_MAX_DISABLED,
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
    {"gate-main-pressed", GATE_MAIN_PRESSED, REASON_MAIN_PRESSED, 0},
    {"gate-main-foreign-flags", GATE_MAIN_FOREIGN_FLAGS, REASON_NONE, 1},
    {"gate-button-released", GATE_BUTTON_RELEASED, REASON_BUTTON_INVALID, 0},
    {"gate-button-zero", GATE_BUTTON_ZERO, REASON_BUTTON_INVALID, 0},
    {"gate-button-set", GATE_BUTTON_SET, REASON_BUTTON_INVALID, 0},
    {"gate-frame-stale", GATE_FRAME_STALE, REASON_SPEED_FRAME_STALE, 0},
    {"gate-frame-exact", GATE_FRAME_EXACT, REASON_NONE, 1},
    {"gate-frame-saturated", GATE_FRAME_SATURATED, REASON_SPEED_FRAME_STALE, 0},
    {"gate-frame-before-speed", GATE_FRAME_BEFORE_SPEED,
     REASON_SPEED_FRAME_STALE, 0},
    {"gate-speed-low", GATE_SPEED_LOW, REASON_SPEED_LOW, 0},
    {"gate-speed-min-exact", GATE_SPEED_MIN_EXACT, REASON_NONE, 1},
    {"gate-speed-high", GATE_SPEED_HIGH, REASON_SPEED_HIGH, 0},
    {"gate-speed-max-exact", GATE_SPEED_MAX_EXACT, REASON_NONE, 1},
    {"gate-speed-min-disabled", GATE_SPEED_MIN_DISABLED, REASON_NONE, 1},
    {"gate-speed-max-disabled", GATE_SPEED_MAX_DISABLED, REASON_NONE, 1},
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
        config[CFG_ENABLE] = 0;
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
    case GATE_MAIN_PRESSED:
        ram_pointer(ASCD_STATUS)[0] = ASCD_MAIN;
        break;
    case GATE_MAIN_FOREIGN_FLAGS:
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
    case GATE_FRAME_STALE:
        ram_pointer(SPEED_AGE)[0] = 11;
        break;
    case GATE_FRAME_EXACT:
        ram_pointer(SPEED_AGE)[0] = 10;
        break;
    case GATE_FRAME_SATURATED:
        /* The largest valid limit still rejects the saturated age. */
        config[CFG_AGE] = 254;
        ram_pointer(SPEED_AGE)[0] = 255;
        break;
    case GATE_FRAME_BEFORE_SPEED:
        ram_pointer(SPEED_AGE)[0] = 11;
        write_u16(ram_pointer(SPEED), 199);
        break;
    case GATE_SPEED_LOW:
        write_u16(ram_pointer(SPEED), 199);
        break;
    case GATE_SPEED_MIN_EXACT:
        write_u16(ram_pointer(SPEED), 200);
        break;
    case GATE_SPEED_HIGH:
        write_u16(ram_pointer(SPEED), 1201);
        break;
    case GATE_SPEED_MAX_EXACT:
        write_u16(ram_pointer(SPEED), 1200);
        break;
    case GATE_SPEED_MIN_DISABLED:
        write_u16(config + CFG_MIN_SPEED, 0);
        write_u16(ram_pointer(SPEED), 0);
        break;
    case GATE_SPEED_MAX_DISABLED:
        write_u16(config + CFG_MAX_SPEED, 0);
        write_u16(ram_pointer(SPEED), 0xffff);
        break;
    case GATE_RPM_LOW:
        write_u16(config + CFG_MIN_RPM, 200);
        write_u16(ram_pointer(RPM), 199);
        break;
    case GATE_RPM_EXACT:
        write_u16(config + CFG_MIN_RPM, 200);
        write_u16(ram_pointer(RPM), 200);
        break;
    case GATE_PEDAL_LOW:
        write_u16(config + CFG_MIN_PEDAL, 100);
        write_u16(ram_pointer(PEDAL), 99);
        break;
    case GATE_PEDAL_EXACT:
        write_u16(config + CFG_MIN_PEDAL, 100);
        write_u16(ram_pointer(PEDAL), 100);
        break;
    case GATE_PEDAL_DISABLED:
        write_u16(config + CFG_MIN_PEDAL, 0);
        write_u16(ram_pointer(PEDAL), 0);
        break;
    case GATE_COOLANT_LOW:
        config[CFG_COOLANT_MIN] = 10;
        config[CFG_COOLANT_MAX] = 200;
        ram_pointer(COOLANT)[0] = 9;
        break;
    case GATE_COOLANT_HIGH:
        config[CFG_COOLANT_MIN] = 10;
        config[CFG_COOLANT_MAX] = 200;
        ram_pointer(COOLANT)[0] = 201;
        break;
    case GATE_COOLANT_MIN:
        config[CFG_COOLANT_MIN] = 10;
        config[CFG_COOLANT_MAX] = 200;
        ram_pointer(COOLANT)[0] = 10;
        break;
    case GATE_COOLANT_MAX:
        config[CFG_COOLANT_MIN] = 10;
        config[CFG_COOLANT_MAX] = 200;
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

    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    write_u16(rom_pointer(RL_CONFIG), 0);
    ram_pointer(SELECTOR_STATE)[0] = 5;
    run_engine();
    if (!expect_phase_reason(
            "gate-config-and-map-index", PHASE_IDLE, REASON_CONFIG_INVALID))
        return 0;
    if (!verify_state_guards("gate-config-and-map-index"))
        return 0;

    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    write_u16(rom_pointer(RL_CONFIG), 0);
    ram_pointer(SELECTOR_STATE)[1] = 1;
    run_engine();
    if (!expect_phase_reason(
            "gate-config-and-selector", PHASE_IDLE, REASON_CONFIG_INVALID))
        return 0;
    if (!verify_state_guards("gate-config-and-selector"))
        return 0;

    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    write_u16(rom_pointer(RL_CONFIG), 0);
    ram_pointer(SELECTOR_STATE)[4] = 1;
    run_engine();
    if (!expect_phase_reason(
            "gate-config-and-feedback", PHASE_IDLE, REASON_CONFIG_INVALID))
        return 0;
    if (!verify_state_guards("gate-config-and-feedback"))
        return 0;

    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    write_u16(rom_pointer(RL_CONFIG), 0);
    ram_pointer(ASCD_STATUS)[0] = ASCD_MAIN;
    run_engine();
    if (!expect_phase_reason(
            "gate-config-and-ascd", PHASE_IDLE, REASON_CONFIG_INVALID))
        return 0;
    if (!verify_state_guards("gate-config-and-ascd"))
        return 0;

    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    write_u16(rom_pointer(RL_CONFIG), 0);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_RELEASED;
    run_engine();
    if (!expect_phase_reason(
            "gate-config-and-button", PHASE_IDLE, REASON_CONFIG_INVALID))
        return 0;
    if (!verify_state_guards("gate-config-and-button"))
        return 0;
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
    {"config-schema", 2, 1, 3},
    {"config-mode", 3, 1, 2},
    {"config-enable-mask", 4, 1, 0x20},
    {"config-options-low", 5, 1, 1},
    {"config-options-high", 5, 1, 0x80},
    {"config-coolant-order", 6, 2, 0x6463},
    {"config-speed-order", 8, 4, 0x00c800c7},
    {"config-rpm-zero", 12, 2, 0},
    {"config-above-zero", 26, 1, 0},
    {"config-below-zero", 27, 1, 0},
    {"config-offset-above", 16, 2, 0xff6a},
    {"config-offset-below", 16, 2, 100},
    {"config-width-zero", 18, 1, 0},
    {"config-rate-zero", 20, 2, 0},
    {"config-rate-range", 20, 2, 1001},
    {"config-gain-negative", 22, 2, 0x8000},
    {"config-limit-range", 24, 2, 1001},
    {"config-ceiling-zero", 28, 2, 0},
    {"config-timeout-zero", 30, 2, 0},
    {"config-timeout-range", 30, 2, 0x8000},
    {"config-rearm-zero", 32, 2, 0},
    {"config-rearm-range", 32, 2, 0x8000},
    {"config-age-zero", 34, 1, 0},
    {"config-age-saturated", 34, 1, 255},
    {"config-hysteresis-zero", 35, 1, 0},
    {"config-hysteresis-above-offset", 35, 1, 81},
    {"config-inverse", 36, 2, 0},
    {"config-end", 38, 2, 0},
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
    volatile uint8_t *config;
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

    /* Every upper bound and the largest positive target offset are valid. */
    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    config = rom_pointer(RL_CONFIG);
    config[CFG_COOLANT_MIN] = 100;
    config[CFG_COOLANT_MAX] = 100;
    write_u16(config + CFG_OFFSET, 99);
    config[18] = 0xff;
    config[19] = 0xff;
    write_u16(config + CFG_RATE, 1000);
    write_u16(config + CFG_GAIN, 0x7fff);
    write_u16(config + CFG_LIMIT, 1000);
    write_u16(config + 28, 0xffff);
    write_u16(config + CFG_TIMEOUT, 0x7fff);
    write_u16(config + CFG_REARM, 0x7fff);
    config[CFG_AGE] = 254;
    config[CFG_HYSTERESIS] = 255;
    run_engine();
    if (!expect_phase_reason("config-upper-bounds", PHASE_ACTIVE, REASON_NONE)
            || !verify_state_guards("config-upper-bounds"))
        return 0;

    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    write_u16(rom_pointer(RL_CONFIG) + CFG_OFFSET, 0xff6b);
    run_engine();
    if (!expect_phase_reason("config-offset-lowest", PHASE_ACTIVE, REASON_NONE)
            || !verify_state_guards("config-offset-lowest"))
        return 0;

    /* The hysteresis may equal the ceiling offset. */
    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    rom_pointer(RL_CONFIG)[CFG_HYSTERESIS] = 80;
    run_engine();
    if (!expect_phase_reason(
            "config-hysteresis-equal", PHASE_ACTIVE, REASON_NONE)
            || !verify_state_guards("config-hysteresis-equal"))
        return 0;
    return 1;
}

/* Direct controller calls on an ACTIVE state whose gate flags all passed.
   Expected values come from the reference model. */
struct controller_case {
    const char *name;
    uint8_t mode;
    uint16_t target;
    uint16_t fraction;
    int16_t integrator;
    uint16_t speed;
    uint16_t rpm;
    uint16_t captured;
    uint16_t gain;
    uint16_t limit;
    uint8_t fuel_cut_status;
    int16_t error;
    int16_t next_integrator;
    uint16_t command;
    uint16_t next_fraction;
    uint16_t request;
    uint16_t flags;
    uint16_t latch;
    uint16_t next_latch;
};

/* The ceiling of captured 300 is 380 and its restore point is 372. */
static const struct controller_case controller_cases[] = {
    {"ctrl-proportional-zero", 0, 500, 1000, 0, 525, 300, 300, 0, 500, 0x00, 25, 0, 0, 950, 0x0000, 0x1fff, 0, 0},
    {"ctrl-proportional-full", 1, 500, 500, 0, 470, 300, 300, 0, 500, 0x00, -30, 0, 1000, 550, 0x0000, 0x5fff, 0, 0},
    {"ctrl-proportional-divide", 0, 500, 520, 0, 500, 300, 300, 0, 500, 0x00, 0, 0, 500, 500, 0x0000, 0x1fff, 0, 0},
    {"ctrl-proportional-top", 0, 500, 30, 0, 520, 300, 300, 0, 500, 0x00, 20, 0, 0, 0, 0x0000, 0x1fff, 0, 0},
    {"ctrl-proportional-width", 0, 500, 990, 0, 480, 300, 300, 0, 500, 0x00, -20, 0, 1000, 1000, 0x0000, 0x1fff, 0, 0},
    {"ctrl-freeze-low", 0, 500, 1000, 0, 530, 300, 300, 2, 500, 0x00, 30, 0, 0, 950, 0x0000, 0x1fff, 0, 0},
    {"ctrl-accumulate-low", 0, 500, 0, -11200, 495, 300, 300, 2, 1000, 0x00, -5, -11190, 0, 0, 0x0000, 0x1fff, 0, 0},
    {"ctrl-freeze-high", 0, 500, 1000, 0, 470, 300, 300, 1, 500, 0x00, -30, 0, 1000, 1000, 0x0000, 0x1fff, 0, 0},
    {"ctrl-accumulate-high", 0, 500, 1000, 11200, 504, 300, 300, 3, 1000, 0x00, 4, 11188, 1000, 1000, 0x0000, 0x1fff, 0, 0},
    {"ctrl-integrator-upper", 0, 500, 600, 1590, 498, 300, 300, 10, 100, 0x00, -2, 1600, 650, 650, 0x0000, 0x1fff, 0, 0},
    {"ctrl-integrator-lower", 0, 500, 400, -1590, 502, 300, 300, 10, 100, 0x00, 2, -1600, 350, 350, 0x0000, 0x1fff, 0, 0},
    {"ctrl-integrator-restore", 0, 500, 1000, 16384, 500, 300, 300, 0, 500, 0x00, 0, 8000, 1000, 1000, 0x0000, 0x1fff, 0, 0},
    {"ctrl-ceiling-at", 1, 500, 500, 0, 500, 380, 300, 0, 500, 0x00, 0, 0, 500, 500, 0x0000, 0x5fff, 0, 0},
    {"ctrl-ceiling-above", 1, 500, 500, 0, 500, 381, 300, 0, 500, 0x00, 0, 0, 500, 500, 0x003f, 0xffff, 0, 1},
    {"ctrl-ceiling-wide", 1, 500, 500, 0, 500, 65535, 65520, 0, 500, 0x00, 0, 0, 500, 500, 0x0000, 0x5fff, 0, 0},
    {"ctrl-stock-cut", 0, 500, 500, 0, 500, 300, 300, 0, 500, 0x04, 0, 0, 500, 500, 0x0000, 0x3fff, 0, 0},
    {"ctrl-stock-cut-other-bits", 0, 500, 500, 0, 500, 300, 300, 0, 500, 0xfb, 0, 0, 500, 500, 0x0000, 0x1fff, 0, 0},
    {"ctrl-ceiling-stock-cut", 1, 500, 500, 0, 500, 381, 300, 0, 500, 0x04, 0, 0, 500, 500, 0x003f, 0xffff, 0, 1},
    {"ctrl-ceiling-latched-band", 1, 500, 500, 0, 500, 376, 300, 0, 500, 0x00, 0, 0, 500, 500, 0x003f, 0xffff, 1, 1},
    {"ctrl-ceiling-restore-above", 1, 500, 500, 0, 500, 373, 300, 0, 500, 0x00, 0, 0, 500, 500, 0x003f, 0xffff, 1, 1},
    {"ctrl-ceiling-restore-exact", 1, 500, 500, 0, 500, 372, 300, 0, 500, 0x00, 0, 0, 500, 500, 0x0000, 0x5fff, 1, 0},
    {"ctrl-ceiling-unlatched-band", 1, 500, 500, 0, 500, 376, 300, 0, 500, 0x00, 0, 0, 500, 500, 0x0000, 0x5fff, 0, 0},
    {"ctrl-ceiling-observe-latched", 0, 500, 500, 0, 500, 381, 300, 0, 500, 0x00, 0, 0, 500, 500, 0x0000, 0x1fff, 1, 0},
    {"ctrl-ceiling-wide-latched", 1, 500, 500, 0, 500, 65535, 65520, 0, 500, 0x00, 0, 0, 500, 500, 0x0000, 0x5fff, 1, 0},
};

static int run_controller_case(const struct controller_case *test)
{
    struct preserved_buffer buffers[] = {PRESERVED_BUFFERS};
    volatile uint8_t *state = ram_pointer(RL_STATE);
    volatile uint8_t *configuration = rom_pointer(RL_CONFIG);
    uint8_t expected_state[RL_STATE_SIZE];
    uint8_t expected_configuration[RL_CONFIG_SIZE];
    uint32_t sp_before, sp_after, gbr_before, gbr_after, observed_r4;
    size_t byte;

    count_case();
    reset_case(test->mode, 0x01);
    write_u16(configuration + CFG_GAIN, test->gain);
    write_u16(configuration + CFG_LIMIT, test->limit);
    write_u16(ram_pointer(SPEED), test->speed);
    write_u16(ram_pointer(RPM), test->rpm);
    ram_pointer(FUEL_CUT_STATUS)[0] = test->fuel_cut_status;
    state[0] = PHASE_ACTIVE;
    state[5] = test->mode;
    write_u16(state + ST_FLAGS, FLAGS_GATES);
    write_u16(state + ST_RUN, 2);
    write_u16(state + ST_CAPTURED, test->captured);
    write_u16(state + ST_TARGET, test->target);
    write_u16(state + ST_FRACTION, test->fraction);
    write_u16(state + ST_ERROR, 0x5a5a);
    write_u16(state + ST_INTEGRATOR, (uint16_t)test->integrator);
    write_u16(state + ST_COMMAND, 0x5a5a);
    write_u16(state + ST_LATCH, test->latch);
    for (byte = 0; byte < sizeof(expected_state); ++byte)
        expected_state[byte] = state[byte];
    write_u16(expected_state + ST_FLAGS, test->flags);
    write_u16(expected_state + ST_FRACTION, test->next_fraction);
    write_u16(expected_state + ST_ERROR, (uint16_t)test->error);
    write_u16(expected_state + ST_INTEGRATOR, (uint16_t)test->next_integrator);
    write_u16(expected_state + ST_REQUEST, test->request);
    write_u16(expected_state + ST_COMMAND, test->command);
    write_u16(expected_state + ST_LATCH, test->next_latch);
    for (byte = 0; byte < sizeof(expected_configuration); ++byte)
        expected_configuration[byte] = configuration[byte];
    capture_buffers(buffers, ARRAY_SIZE(buffers));

    __asm__ volatile ("mov r15,%0" : "=r" (sp_before) : : "memory");
    __asm__ volatile ("stc gbr,%0" : "=r" (gbr_before) : : "memory");
    observed_r4 = invoke_r4(SPEED_CONTROLLER, 0);
    __asm__ volatile ("mov r15,%0" : "=r" (sp_after) : : "memory");
    __asm__ volatile ("stc gbr,%0" : "=r" (gbr_after) : : "memory");
    if (sp_after != sp_before)
        return fail_value(test->name, "stack_pointer", sp_after, sp_before);
    if (gbr_after != gbr_before)
        return fail_value(test->name, "gbr", gbr_after, gbr_before);
    /* invoke_r4 observes the controller's configuration-register role and
       the divider's preservation of r4. */
    if (observed_r4 != RL_CONFIG)
        return fail_value(
            test->name, "configuration_r4", observed_r4, RL_CONFIG);
    if (!fail_bytes(test->name, "complete_state", state, expected_state,
                    sizeof(expected_state))
            || !fail_bytes(test->name, "configuration", configuration,
                           expected_configuration,
                           sizeof(expected_configuration))
            || !verify_buffers(test->name, buffers, ARRAY_SIZE(buffers)))
        return 0;
    return verify_state_guards(test->name);
}

static int run_controller_cases(void)
{
    size_t index;

    for (index = 0; index < ARRAY_SIZE(controller_cases); ++index)
        if (!run_controller_case(&controller_cases[index]))
            return 0;
    return 1;
}

static int verify_active_state(
    const char *name,
    uint8_t mode,
    uint16_t captured,
    uint16_t target,
    uint16_t fraction,
    int16_t error,
    uint16_t command,
    uint16_t flags)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);

    if (!expect_phase_reason(name, PHASE_ACTIVE, REASON_NONE))
        return 0;
    if (state[4] != 0 || state[5] != mode)
        return fail_value(name, "map_mode", state[5], mode);
    if (read_u16(state + ST_FLAGS) != flags)
        return fail_value(name, "flags", read_u16(state + ST_FLAGS), flags);
    if (read_u16(state + ST_RUN) != 0 || read_u16(state + ST_REARM) != 0)
        return fail_value(name, "timers", read_u32(state + ST_RUN), 0);
    if (read_u16(state + ST_CAPTURED) != captured)
        return fail_value(
            name, "captured", read_u16(state + ST_CAPTURED), captured);
    if (read_u16(state + ST_TARGET) != target)
        return fail_value(name, "target", read_u16(state + ST_TARGET), target);
    if (read_u16(state + ST_FRACTION) != fraction)
        return fail_value(
            name, "fraction", read_u16(state + ST_FRACTION), fraction);
    if (read_u16(state + ST_ERROR) != (uint16_t)error)
        return fail_value(
            name, "error", read_u16(state + ST_ERROR), (uint16_t)error);
    if (read_u16(state + ST_INTEGRATOR) != 0)
        return fail_value(
            name, "integrator", read_u16(state + ST_INTEGRATOR), 0);
    if (read_u16(state + ST_COMMAND) != command)
        return fail_value(
            name, "command", read_u16(state + ST_COMMAND), command);
    if (read_u16(state + ST_LATCH) != 0)
        return fail_value(name, "latch", read_u16(state + ST_LATCH), 0);
    if (!verify_request(name, 0) || !verify_fuel_untouched(name))
        return 0;
    return verify_state_guards(name);
}

static int run_activation_cases(void)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);
    volatile uint8_t *config;

    /* Activation captures a fresh controller state whatever IDLE retained. */
    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    write_u16(state + ST_CAPTURED, 0x5a5a);
    write_u16(state + ST_TARGET, 0x5a5a);
    write_u16(state + ST_FRACTION, 5);
    write_u16(state + ST_ERROR, 0x5a5a);
    write_u16(state + ST_INTEGRATOR, 0x4000);
    write_u16(state + ST_REQUEST, FUEL_CUT_REQUEST_ALL);
    write_u16(state + ST_COMMAND, 0x5a5a);
    write_u16(state + ST_LATCH, 1);
    run_engine();
    if (!verify_active_state(
            "activate-observe", MODE_OBSERVE, 300, 500, 950, 0, 500,
            FLAGS_OBSERVE_ACTIVE))
        return 0;

    count_case();
    reset_case(MODE_HOLD, 0x01);
    run_engine();
    if (!verify_active_state(
            "activate-hold", MODE_HOLD, 300, 500, 950, 0, 500,
            FLAGS_HOLD_ACTIVE))
        return 0;

    count_case();
    reset_case(MODE_HOLD, 0x01);
    ram_pointer(FUEL_CUT_STATUS)[0] = FUEL_CUT_ACTIVE;
    run_engine();
    if (!verify_active_state(
            "activate-fuel-cut", MODE_HOLD, 300, 500, 950, 0, 500,
            FLAGS_HOLD_FUEL_CUT_ACTIVE))
        return 0;

    /* Every other bit of the state byte leaves the flag clear. */
    count_case();
    reset_case(MODE_HOLD, 0x01);
    ram_pointer(FUEL_CUT_STATUS)[0] = (uint8_t)~FUEL_CUT_ACTIVE;
    run_engine();
    if (!verify_active_state(
            "activate-fuel-cut-other-bits", MODE_HOLD, 300, 500, 950, 0,
            500, FLAGS_HOLD_ACTIVE))
        return 0;

    /* A negative captured target saturates at zero. */
    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    config = rom_pointer(RL_CONFIG);
    write_u16(config + CFG_MIN_SPEED, 0);
    write_u16(config + CFG_OFFSET, 0xffce);
    write_u16(ram_pointer(SPEED), 30);
    run_engine();
    if (!verify_active_state(
            "activate-target-floor", MODE_OBSERVE, 300, 0, 950, 30, 0,
            FLAGS_OBSERVE_ACTIVE))
        return 0;

    /* A captured target above the u16 range saturates at 0xFFFF. */
    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    config = rom_pointer(RL_CONFIG);
    write_u16(config + CFG_MAX_SPEED, 0);
    write_u16(config + CFG_OFFSET, 60);
    write_u16(ram_pointer(SPEED), 0xfff0);
    run_engine();
    if (!verify_active_state(
            "activate-target-saturated", MODE_OBSERVE, 300, 0xffff, 950,
            -15, 875, FLAGS_OBSERVE_ACTIVE))
        return 0;
    return 1;
}

static int activate(uint8_t mode, uint8_t mask)
{
    reset_case(mode, mask);
    run_engine();
    return ram_pointer(RL_STATE)[0] == PHASE_ACTIVE;
}

/* One ACTIVE tick at the given RPM. The run timer restarts first so the
   short test timeout leaves the hold active. */
static int run_hold_step(
    const char *name, uint16_t rpm, uint16_t request, uint16_t flags)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);

    count_case();
    write_u16(ram_pointer(RPM), rpm);
    write_u16(state + ST_RUN, 0);
    run_engine();
    if (!expect_phase_reason(name, PHASE_ACTIVE, REASON_NONE))
        return 0;
    if (read_u16(state + ST_FLAGS) != flags)
        return fail_value(name, "flags", read_u16(state + ST_FLAGS), flags);
    if (read_u16(state + ST_LATCH) != (request ? 1U : 0U))
        return fail_value(
            name, "latch", read_u16(state + ST_LATCH), request ? 1U : 0U);
    if (!verify_request(name, request) || !verify_fuel_untouched(name))
        return 0;
    return verify_state_guards(name);
}

static int run_hold_cases(void)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);

    /* Activation at 300 places the ceiling at 380; hysteresis 8 places the
       restore point at 372. */
    if (!activate(MODE_HOLD, 0x01))
        return fail_value("hold", "setup", 0, 1);
    if (!run_hold_step("hold-below-ceiling", 379, 0, FLAGS_HOLD_ACTIVE)
            || !run_hold_step("hold-at-ceiling", 380, 0, FLAGS_HOLD_ACTIVE)
            || !run_hold_step("hold-above-ceiling", 381, FUEL_CUT_REQUEST_ALL,
                              FLAGS_HOLD_CEILING_ACTIVE)
            || !run_hold_step("hold-latched-band", 373, FUEL_CUT_REQUEST_ALL,
                              FLAGS_HOLD_CEILING_ACTIVE)
            || !run_hold_step("hold-restored", 372, 0, FLAGS_HOLD_ACTIVE)
            || !run_hold_step("hold-unlatched-band", 376, 0,
                              FLAGS_HOLD_ACTIVE)
            || !run_hold_step("hold-retrigger", 400, FUEL_CUT_REQUEST_ALL,
                              FLAGS_HOLD_CEILING_ACTIVE))
        return 0;

    /* An abort releases a held request in the same tick. */
    count_case();
    ram_pointer(BUTTON_CODE)[0] = BUTTON_RELEASED;
    run_engine();
    if (!expect_phase_reason(
            "hold-abort", PHASE_COOLDOWN, REASON_BUTTON_RELEASED))
        return 0;
    if (read_u16(state + ST_FLAGS) & FLAGS_ACTIVE_OUTPUTS)
        return fail_value(
            "hold-abort", "output_flags", read_u16(state + ST_FLAGS), 0);
    if (read_u16(state + ST_LATCH) != 0)
        return fail_value(
            "hold-abort", "latch", read_u16(state + ST_LATCH), 0);
    if (!verify_request("hold-abort", 0)
            || !verify_fuel_untouched("hold-abort"))
        return 0;

    if (!activate(MODE_OBSERVE, 0x01))
        return fail_value("hold-observe", "setup", 0, 1);
    if (!run_hold_step("hold-observe", 400, 0, FLAGS_OBSERVE_ACTIVE))
        return 0;
    return 1;
}

/* One ACTIVE tick after a HOLD activation at speed 500 with one input
   changed by the caller. */
static int expect_active_abort(const char *name, uint8_t reason)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);

    run_engine();
    if (!expect_phase_reason(name, PHASE_COOLDOWN, reason))
        return 0;
    if (read_u16(state + ST_FLAGS) & FLAGS_ACTIVE_OUTPUTS)
        return fail_value(
            name, "output_flags", read_u16(state + ST_FLAGS), 0);
    if (read_u16(state + ST_REARM) != 0)
        return fail_value(name, "rearm", read_u16(state + ST_REARM), 0);
    if (!verify_request(name, 0) || !verify_fuel_untouched(name))
        return 0;
    return verify_state_guards(name);
}

static int expect_active_continues(const char *name)
{
    run_engine();
    if (!expect_phase_reason(name, PHASE_ACTIVE, REASON_NONE))
        return 0;
    return verify_state_guards(name);
}

static int run_active_cases(void)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);

    count_case();
    if (!activate(MODE_HOLD, 0x01))
        return fail_value("active-normal", "setup", 0, 1);
    if (!expect_active_continues("active-normal"))
        return 0;
    if (read_u16(state + ST_RUN) != 1)
        return fail_value(
            "active-normal", "run_ticks", read_u16(state + ST_RUN), 1);

    count_case();
    if (!activate(MODE_HOLD, 0x01))
        return fail_value("active-timeout", "setup", 0, 1);
    write_u16(rom_pointer(RL_CONFIG) + CFG_TIMEOUT, 2);
    run_engine();
    if (!expect_active_abort("active-timeout", REASON_TIMEOUT))
        return 0;
    if (read_u16(state + ST_FLAGS) & FLAG_TIMER_OK)
        return fail_value("active-timeout", "timer_flag", 1, 0);

    count_case();
    if (!activate(MODE_HOLD, 0x03))
        return fail_value("active-map-change", "setup", 0, 1);
    ram_pointer(SELECTOR_STATE)[0] = 1;
    if (!expect_active_abort("active-map-change", REASON_MAP_CHANGED))
        return 0;

    count_case();
    if (!activate(MODE_HOLD, 0x01))
        return fail_value("active-mode-change", "setup", 0, 1);
    rom_pointer(RL_CONFIG)[CFG_MODE] = MODE_OBSERVE;
    if (!expect_active_abort("active-mode-change", REASON_MODE_CHANGED))
        return 0;

    count_case();
    if (!activate(MODE_HOLD, 0x01))
        return fail_value("active-map-request", "setup", 0, 1);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_SET;
    if (!expect_active_abort("active-map-request", REASON_MAP_REQUEST))
        return 0;

    count_case();
    if (!activate(MODE_HOLD, 0x01))
        return fail_value("active-release", "setup", 0, 1);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_RELEASED;
    if (!expect_active_abort("active-release", REASON_BUTTON_RELEASED))
        return 0;

    count_case();
    if (!activate(MODE_HOLD, 0x01))
        return fail_value("active-invalid-button", "setup", 0, 1);
    ram_pointer(BUTTON_CODE)[0] = 4;
    if (!expect_active_abort("active-invalid-button", REASON_BUTTON_INVALID))
        return 0;

    count_case();
    if (!activate(MODE_HOLD, 0x01))
        return fail_value("active-config-invalid", "setup", 0, 1);
    rom_pointer(RL_CONFIG)[0] = 0;
    if (!expect_active_abort("active-config-invalid", REASON_CONFIG_INVALID))
        return 0;

    /* The window is inclusive: +15.0 and -10.0 km/h against target 50.0. */
    count_case();
    if (!activate(MODE_HOLD, 0x01))
        return fail_value("active-above-exact", "setup", 0, 1);
    write_u16(ram_pointer(SPEED), 650);
    if (!expect_active_continues("active-above-exact"))
        return 0;

    count_case();
    if (!activate(MODE_HOLD, 0x01))
        return fail_value("active-above-window", "setup", 0, 1);
    write_u16(ram_pointer(SPEED), 651);
    if (!expect_active_abort("active-above-window", REASON_SPEED_ABOVE_WINDOW))
        return 0;

    count_case();
    if (!activate(MODE_HOLD, 0x01))
        return fail_value("active-below-exact", "setup", 0, 1);
    write_u16(ram_pointer(SPEED), 400);
    if (!expect_active_continues("active-below-exact"))
        return 0;

    count_case();
    if (!activate(MODE_HOLD, 0x01))
        return fail_value("active-below-window", "setup", 0, 1);
    write_u16(ram_pointer(SPEED), 399);
    if (!expect_active_abort("active-below-window", REASON_SPEED_BELOW_WINDOW))
        return 0;

    /* ACTIVE checks the error window, not the activation speed range. */
    count_case();
    if (!activate(MODE_HOLD, 0x01))
        return fail_value("active-range-ignored", "setup", 0, 1);
    write_u16(rom_pointer(RL_CONFIG) + CFG_MAX_SPEED, 600);
    write_u16(ram_pointer(SPEED), 650);
    if (!expect_active_continues("active-range-ignored"))
        return 0;

    count_case();
    if (!activate(MODE_HOLD, 0x01))
        return fail_value("active-frame-stale", "setup", 0, 1);
    ram_pointer(SPEED_AGE)[0] = 11;
    if (!expect_active_abort("active-frame-stale", REASON_SPEED_FRAME_STALE))
        return 0;

    count_case();
    if (!activate(MODE_OBSERVE, 0x01))
        return fail_value("active-observe-release", "setup", 0, 1);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_RELEASED;
    if (!expect_active_abort(
            "active-observe-release", REASON_BUTTON_RELEASED))
        return 0;
    return 1;
}

static void set_cooldown(uint16_t rearm)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);

    state[0] = PHASE_COOLDOWN;
    state[1] = REASON_BUTTON_RELEASED;
    state[4] = 0;
    state[5] = MODE_HOLD;
    write_u16(state + ST_REARM, rearm);
}

static int run_cooldown_cases(void)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);

    count_case();
    reset_case(MODE_HOLD, 0x01);
    set_cooldown(2);
    rom_pointer(RL_CONFIG)[0] = 0;
    run_engine();
    if (!expect_phase_reason(
            "cooldown-config", PHASE_COOLDOWN, REASON_CONFIG_INVALID))
        return 0;
    if (read_u16(state + ST_REARM) != 0)
        return fail_value(
            "cooldown-config", "rearm", read_u16(state + ST_REARM), 0);

    count_case();
    reset_case(MODE_HOLD, 0x01);
    set_cooldown(2);
    run_engine();
    if (read_u16(state + ST_REARM) != 0)
        return fail_value(
            "cooldown-held", "rearm", read_u16(state + ST_REARM), 0);

    count_case();
    reset_case(MODE_HOLD, 0x01);
    set_cooldown(0);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_RELEASED;
    run_engine();
    if (read_u16(state + ST_REARM) != 1)
        return fail_value(
            "cooldown-increment", "rearm", read_u16(state + ST_REARM), 1);

    count_case();
    reset_case(MODE_HOLD, 0x01);
    set_cooldown(2);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_RELEASED;
    run_engine();
    if (!expect_phase_reason(
            "cooldown-complete", PHASE_IDLE, REASON_BUTTON_RELEASED))
        return 0;
    if (state[5] != MODE_OBSERVE || read_u16(state + ST_REARM) != 0)
        return fail_value("cooldown-complete", "reset", state[5], 0);

    ram_pointer(BUTTON_CODE)[0] = BUTTON_CANCEL;
    run_engine();
    if (!expect_phase_reason(
            "cooldown-complete", PHASE_ACTIVE, REASON_NONE))
        return 0;

    count_case();
    reset_case(MODE_HOLD, 0x01);
    set_cooldown(2);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_ZERO;
    run_engine();
    if (!expect_phase_reason(
            "cooldown-zero", PHASE_COOLDOWN, REASON_BUTTON_RELEASED))
        return 0;
    if (read_u16(state + ST_REARM) != 0)
        return fail_value(
            "cooldown-zero", "rearm", read_u16(state + ST_REARM), 0);

    /* Every engine entry clears a stale request outside ACTIVE. */
    count_case();
    reset_case(MODE_HOLD, 0x01);
    set_cooldown(0);
    write_u16(state + ST_REQUEST, FUEL_CUT_REQUEST_ALL);
    run_engine();
    if (!expect_phase_reason(
            "cooldown-stale-request", PHASE_COOLDOWN, REASON_BUTTON_RELEASED))
        return 0;
    return verify_request("cooldown-stale-request", 0);
}

/* The adapter passes the stock command to the stock consumer stub in every
   phase and changes no Rolling Launch state. */
static int invoke_adapter(
    const char *name, uint8_t phase, uint8_t mode, uint8_t stock)
{
    struct preserved_buffer buffers[] = {PRESERVED_BUFFERS};
    volatile uint8_t *state = ram_pointer(RL_STATE);
    uint8_t expected_state[RL_STATE_SIZE];
    uint8_t expected_configuration[RL_CONFIG_SIZE];
    uint32_t sp_before, sp_after, gbr_before, gbr_after, returned;
    size_t byte;

    count_case();
    reset_case(MODE_HOLD, 0x01);
    fill_bytes(state, RL_STATE_SIZE, 0x5a);
    state[0] = phase;
    state[4] = 0;
    state[5] = mode;
    write_u16(state + ST_FRACTION, 500);
    write_u16(state + ST_REQUEST, phase == PHASE_ACTIVE
        ? FUEL_CUT_REQUEST_ALL : 0);
    ram_pointer(IGNITION_OUTPUT)[0] = 0x6e;
    for (byte = 0; byte < sizeof(expected_state); ++byte)
        expected_state[byte] = state[byte];
    for (byte = 0; byte < sizeof(expected_configuration); ++byte)
        expected_configuration[byte] = rom_pointer(RL_CONFIG)[byte];
    capture_buffers(buffers, ARRAY_SIZE(buffers));
    __asm__ volatile ("mov r15,%0" : "=r" (sp_before) : : "memory");
    __asm__ volatile ("stc gbr,%0" : "=r" (gbr_before) : : "memory");
    returned = invoke_r4(IGNITION_ADAPTER, stock);
    __asm__ volatile ("mov r15,%0" : "=r" (sp_after) : : "memory");
    __asm__ volatile ("stc gbr,%0" : "=r" (gbr_after) : : "memory");
    if (sp_after != sp_before)
        return fail_value(name, "stack_pointer", sp_after, sp_before);
    if (gbr_after != gbr_before)
        return fail_value(name, "gbr", gbr_after, gbr_before);
    if (returned != stock)
        return fail_value(name, "stock_r4", returned, stock);
    if (!fail_bytes(name, "complete_state", state, expected_state,
                    sizeof(expected_state))
            || !fail_bytes(name, "configuration", rom_pointer(RL_CONFIG),
                           expected_configuration,
                           sizeof(expected_configuration))
            || !verify_buffers(name, buffers, ARRAY_SIZE(buffers)))
        return 0;
    return verify_state_guards(name);
}

static int run_adapter_cases(void)
{
    return invoke_adapter("adapter-idle", PHASE_IDLE, MODE_OBSERVE, 110)
        && invoke_adapter("adapter-active-hold", PHASE_ACTIVE, MODE_HOLD, 0)
        && invoke_adapter("adapter-cooldown", PHASE_COOLDOWN, MODE_HOLD, 0xff);
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
        "feedback-idle-clear-held", PHASE_IDLE, REASON_NONE,
        FLAG_BUTTON_HELD, {0, 0, 0, 0}, 0xb5, {0, 0, 0, 0},
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

        struct preserved_feedback_buffer {
            uint32_t address;
            size_t size;
            uint8_t bytes[28];
        } buffers[] = {
            {FUEL_SHADOW, FUEL_SHADOW_SIZE, {0}},
            {THROTTLE_SHADOW, THROTTLE_SHADOW_SIZE, {0}},
            {THROTTLE_RUNTIME, 2, {0}}, {BUTTON_CODE, 2, {0}},
            {ASCD_STATUS, 1, {0}}, {SPEED, 2, {0}}, {SPEED_AGE, 1, {0}},
            {RPM, 2, {0}},
            {PEDAL, 2, {0}}, {COOLANT, 1, {0}}, {FORMER_BRAKE_STATUS, 1, {0}},
            {FUEL_CUT_STATUS, 1, {0}}, {IGNITION_OUTPUT, 1, {0}},
            {APC_MODE_SNAPSHOT, 1, {0}},
        };
        uint8_t expected_state[RL_STATE_SIZE], expected_selector[8];
        uint8_t expected_configuration[RL_CONFIG_SIZE];
        const uint8_t expected_counts[2] = {1, 1};
        uint32_t sp_before, sp_after, gbr_before, gbr_after;
        size_t byte;

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

        /* The arbiter consumes only phase, reason and flags. Preserve the
           remaining state bytes without relying on their reset zeros. */
        fill_bytes(state + 4, RL_STATE_SIZE - 4U, 0x5a);
        for (byte = 0; byte < sizeof(expected_state); ++byte)
            expected_state[byte] = state[byte];
        for (byte = 0; byte < sizeof(expected_selector); ++byte)
            expected_selector[byte] = byte < 4
                ? selector[byte] : test->expected_map_feedback[byte - 4];
        for (byte = 0; byte < sizeof(expected_configuration); ++byte)
            expected_configuration[byte] = rom_pointer(RL_CONFIG)[byte];
        for (index = 0; index < ARRAY_SIZE(buffers); ++index)
            for (byte = 0; byte < buffers[index].size; ++byte)
                buffers[index].bytes[byte] = ram_pointer(buffers[index].address)[byte];
        __asm__ volatile ("mov r15,%0" : "=r" (sp_before) : : "memory");
        __asm__ volatile ("stc gbr,%0" : "=r" (gbr_before) : : "memory");
        (void)invoke_r4(FEEDBACK_ARBITER, 0);
        __asm__ volatile ("mov r15,%0" : "=r" (sp_after) : : "memory");
        __asm__ volatile ("stc gbr,%0" : "=r" (gbr_after) : : "memory");
        if (sp_after != sp_before)
            return fail_value(test->name, "stack_pointer", sp_after, sp_before);
        if (gbr_after != gbr_before)
            return fail_value(test->name, "gbr", gbr_after, gbr_before);
        if (!fail_bytes(test->name, "complete_state", state,
                        expected_state, sizeof(expected_state))
                || !fail_bytes(test->name, "complete_selector", selector,
                               expected_selector, sizeof(expected_selector))
                || !fail_bytes(test->name, "configuration", rom_pointer(RL_CONFIG),
                               expected_configuration, sizeof(expected_configuration))
                || !fail_bytes(test->name, "feedback_counts", rom_pointer(FEEDBACK_COUNTS),
                               expected_counts, sizeof(expected_counts)))
            return 0;
        for (index = 0; index < ARRAY_SIZE(buffers); ++index)
            if (!fail_bytes(test->name, "preserved_buffer", ram_pointer(buffers[index].address),
                            buffers[index].bytes, buffers[index].size))
                return 0;


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
    reset_case(MODE_HOLD, 0x01);
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
    run_periodic_entry();
    if (!expect_phase_reason(
            "wrapper-periodic", PHASE_ACTIVE, REASON_NONE))
        return 0;
    return 1;
}


/* The wrapper runs the stock coordinator stub, then merges the request. The
   preset mask differs from every stub result, so a merge before the stock
   call would be overwritten. */
static int invoke_fuel_cut(
    const char *name, uint8_t stock, uint16_t request, uint8_t expected)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);
    uint8_t expected_state[RL_STATE_SIZE];
    uint32_t sp_before, sp_after, gbr_before, gbr_after, returned;
    size_t byte;

    count_case();
    reset_case(MODE_HOLD, 0x01);
    fill_bytes(state, RL_STATE_SIZE, 0x5a);
    write_u16(state + ST_REQUEST, request);
    for (byte = 0; byte < sizeof(expected_state); ++byte)
        expected_state[byte] = state[byte];
    ram_pointer(COORDINATOR_RESULT)[0] = stock;
    ram_pointer(FUEL_INHIBIT_MASK)[0] = 0xc0;
    __asm__ volatile ("mov r15,%0" : "=r" (sp_before) : : "memory");
    __asm__ volatile ("stc gbr,%0" : "=r" (gbr_before) : : "memory");
    returned = invoke_r0(FUEL_CUT_WRAPPER);
    __asm__ volatile ("mov r15,%0" : "=r" (sp_after) : : "memory");
    __asm__ volatile ("stc gbr,%0" : "=r" (gbr_after) : : "memory");
    if (sp_after != sp_before)
        return fail_value(name, "stack_pointer", sp_after, sp_before);
    if (gbr_after != gbr_before)
        return fail_value(name, "gbr", gbr_after, gbr_before);
    if (returned != COORDINATOR_RETURN)
        return fail_value(name, "returned", returned, COORDINATOR_RETURN);
    if (ram_pointer(FUEL_INHIBIT_MASK)[0] != expected)
        return fail_value(
            name, "final_mask", ram_pointer(FUEL_INHIBIT_MASK)[0], expected);
    if (!fail_bytes(name, "complete_state", state, expected_state,
                    sizeof(expected_state))
            || !verify_fuel_untouched(name))
        return 0;
    return verify_state_guards(name);
}

static int run_fuel_cut_cases(void)
{
    uint32_t periodic, coordinator;

    if (!invoke_fuel_cut("fuel-cut-zero-inactive", 0x00, 0x0000, 0x00)
            || !invoke_fuel_cut("fuel-cut-zero-active", 0x3f, 0x0000, 0x3f)
            || !invoke_fuel_cut("fuel-cut-zero-partial", 0x05, 0x0000, 0x05)
            || !invoke_fuel_cut("fuel-cut-full", 0x00, 0x003f, 0x3f)
            || !invoke_fuel_cut("fuel-cut-full-active", 0x3f, 0x003f, 0x3f)
            || !invoke_fuel_cut("fuel-cut-partial", 0x00, 0x0015, 0x15)
            || !invoke_fuel_cut("fuel-cut-partial-active", 0x0a, 0x0015, 0x1f)
            || !invoke_fuel_cut("fuel-cut-single", 0x00, 0x0001, 0x01)
            || !invoke_fuel_cut("fuel-cut-malformed-bit6", 0x05, 0x0040, 0x05)
            || !invoke_fuel_cut("fuel-cut-malformed-high", 0x05, 0x0100, 0x05)
            || !invoke_fuel_cut("fuel-cut-malformed-mixed", 0x00, 0x803f, 0x00)
            || !invoke_fuel_cut("fuel-cut-malformed-all", 0x0a, 0xffff, 0x0a))
        return 0;

    /* Index 1 runs the engine before index 28 merges its request, so the
       mask follows the request of the same scheduler pass. */
    count_case();
    reset_case(MODE_HOLD, 0x01);
    periodic = read_u32(rom_pointer(SCHEDULER_TABLE + 4U * 1U));
    coordinator = read_u32(rom_pointer(SCHEDULER_TABLE + 4U * 28U));
    if (periodic != PERIODIC_WRAPPER)
        return fail_value("fuel-cut-scheduler", "entry_1", periodic,
                          PERIODIC_WRAPPER);
    if (coordinator != FUEL_CUT_WRAPPER)
        return fail_value("fuel-cut-scheduler", "entry_28", coordinator,
                          FUEL_CUT_WRAPPER);
    run_periodic_entry();
    (void)invoke_r0(coordinator);
    if (ram_pointer(RL_STATE)[0] != PHASE_ACTIVE
            || ram_pointer(FUEL_INHIBIT_MASK)[0] != 0x00)
        return fail_value("fuel-cut-scheduler", "activation_mask",
                          ram_pointer(FUEL_INHIBIT_MASK)[0], 0x00);
    write_u16(ram_pointer(RPM), 381);
    run_periodic_entry();
    (void)invoke_r0(coordinator);
    if (ram_pointer(FUEL_INHIBIT_MASK)[0] != 0x3f)
        return fail_value("fuel-cut-scheduler", "held_mask",
                          ram_pointer(FUEL_INHIBIT_MASK)[0], 0x3f);
    ram_pointer(BUTTON_CODE)[0] = BUTTON_RELEASED;
    run_periodic_entry();
    (void)invoke_r0(coordinator);
    if (!expect_phase_reason(
            "fuel-cut-scheduler", PHASE_COOLDOWN, REASON_BUTTON_RELEASED))
        return 0;
    if (ram_pointer(FUEL_INHIBIT_MASK)[0] != 0x00)
        return fail_value("fuel-cut-scheduler", "released_mask",
                          ram_pointer(FUEL_INHIBIT_MASK)[0], 0x00);
    if (!verify_fuel_untouched("fuel-cut-scheduler"))
        return 0;

    /* Observe never requests a cut: above the ceiling, the final mask keeps
       the stock coordinator result. */
    count_case();
    reset_case(MODE_OBSERVE, 0x01);
    ram_pointer(COORDINATOR_RESULT)[0] = 0x05;
    run_periodic_entry();
    write_u16(ram_pointer(RPM), 400);
    run_periodic_entry();
    (void)invoke_r0(coordinator);
    if (!expect_phase_reason(
            "fuel-cut-scheduler-observe", PHASE_ACTIVE, REASON_NONE))
        return 0;
    if (ram_pointer(FUEL_INHIBIT_MASK)[0] != 0x05)
        return fail_value("fuel-cut-scheduler-observe", "stock_mask",
                          ram_pointer(FUEL_INHIBIT_MASK)[0], 0x05);
    if (read_u16(ram_pointer(RL_STATE) + ST_LATCH) != 0)
        return fail_value("fuel-cut-scheduler-observe", "latch",
                          read_u16(ram_pointer(RL_STATE) + ST_LATCH), 0);
    if (!verify_request("fuel-cut-scheduler-observe", 0))
        return 0;
    return verify_fuel_untouched("fuel-cut-scheduler-observe");
}


/* The C reference of the spark-cut actuator for one GR11A match, computed
   from the RAM inputs and the state before the match. */
struct spark_expect {
    uint8_t state[RL_STATE_SIZE];
    uint8_t veto;
    uint8_t latch;
};

static void spark_reset(uint8_t *state)
{
    size_t index;

    for (index = 0; index < SPARK_CYLINDERS; ++index)
        write_u16(state + ST_ACCUMULATORS + 2U * index, spark_offsets[index]);
}

static void spark_reference(struct spark_expect *out)
{
    const volatile uint8_t *state = ram_pointer(RL_STATE);
    uint8_t phase = state[0];
    uint8_t cylinder = ram_pointer(EVENT_CYLINDER)[0];
    int active = phase == PHASE_ACTIVE;
    int hold = active && state[5] == MODE_HOLD;
    uint16_t fraction = read_u16(state + ST_FRACTION);
    uint16_t accumulator;
    size_t index;

    for (index = 0; index < RL_STATE_SIZE; ++index)
        out->state[index] = state[index];
    out->veto = ram_pointer(DWELL_VETO)[0];
    out->latch = ram_pointer(MISFIRE_LATCH)[0];
    if ((ram_pointer(SPARK_ARMED)[0] & 0x80U) == 0)
        return;
    if (active)
        out->state[ST_QUIET] = 0;
    else if (out->state[ST_QUIET] != 0xff)
        ++out->state[ST_QUIET];
    if (hold) {
        if (out->latch == 0)
            out->latch = MISFIRE_MARKER;
    } else if (phase == PHASE_IDLE && out->latch == MISFIRE_MARKER
               && out->state[ST_QUIET] >= MISFIRE_RELEASE_EVENTS) {
        out->latch = 0;
    }
    if (!hold || fraction > TORQUE_ONE) {
        spark_reset(out->state);
        return;
    }
    if ((ram_pointer(CRANK_SYNC)[0] & 0x80U) == 0
            || (ram_pointer(APC_MODE_SNAPSHOT)[0] & 0x40U) != 0
            || ram_pointer(DWELL_ANGLE)[0] > SPARK_DWELL_LIMIT
            || (uint8_t)(cylinder - 1U) >= SPARK_CYLINDERS)
        return;
    index = ST_ACCUMULATORS + 2U * (size_t)(cylinder - 1U);
    accumulator = read_u16(out->state + index);
    if (accumulator >= SPARK_CUT_ONE) {
        spark_reset(out->state);
        return;
    }
    accumulator = (uint16_t)(accumulator + 6U * (TORQUE_ONE - fraction));
    if (accumulator >= SPARK_CUT_ONE) {
        accumulator = (uint16_t)(accumulator - SPARK_CUT_ONE);
        out->veto |= 0x80U;
        ++out->state[ST_CUTS];
    }
    write_u16(out->state + index, accumulator);
}

/* Inputs of an eligible match of event cylinder 1 in an ACTIVE hold, with
   the accumulators at their offsets and foreign bits in the veto byte. */
static void reset_spark_case(uint8_t phase, uint8_t mode, uint16_t fraction)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);
    uint8_t offsets[RL_STATE_SIZE];

    reset_case(mode, 0x01);
    state[0] = phase;
    state[5] = mode;
    write_u16(state + ST_FRACTION, fraction);
    state[ST_QUIET] = 0x40;
    state[ST_CUTS] = 0x10;
    spark_reset(offsets);
    write_bytes(state + ST_ACCUMULATORS, offsets + ST_ACCUMULATORS,
                2U * SPARK_CYLINDERS);
    ram_pointer(SPARK_ARMED)[0] = 0x80;
    ram_pointer(CRANK_SYNC)[0] = 0x80;
    ram_pointer(APC_MODE_SNAPSHOT)[0] = 0;
    ram_pointer(DWELL_ANGLE)[0] = 60;
    ram_pointer(EVENT_CYLINDER)[0] = 1;
    ram_pointer(DWELL_VETO)[0] = 0x15;
    ram_pointer(MISFIRE_LATCH)[0] = 0;
}

static uint32_t spark_matches;
static uint32_t spark_entry_sr[2];

/* One GR11A match through TRAPA and the redirected vector. The probe sets
   r0..r7 to 1..8 and alternates the T bit; the stock-handler stub records SR
   at its entry. */
static int spark_match(const char *name)
{
    static const uint32_t inputs[] = {
        SPARK_ARMED, CRANK_SYNC, APC_MODE_SNAPSHOT, DWELL_ANGLE,
        EVENT_CYLINDER,
    };
    struct spark_expect expected;
    uint32_t registers[10];
    uint8_t before[ARRAY_SIZE(inputs)];
    uint32_t t_bit = spark_matches++ & 1U;
    size_t index;

    spark_reference(&expected);
    for (index = 0; index < ARRAY_SIZE(inputs); ++index)
        before[index] = ram_pointer(inputs[index])[0];
    write_u32(ram_pointer(SPARK_ENTRY_SR), 0xffffffffU);
    invoke_spark_probe(registers, t_bit);
    for (index = 0; index < 8; ++index) {
        if (registers[index] != index + 1U)
            return fail_value(name, "register", registers[index], index + 1U);
    }
    if ((registers[8] & 1U) != t_bit)
        return fail_value(name, "t_bit", registers[8] & 1U, t_bit);
    if (registers[9] != registers[8])
        return fail_value(name, "returned_sr", registers[9], registers[8]);
    if (read_u32(ram_pointer(SPARK_ENTRY_SR)) != spark_entry_sr[t_bit])
        return fail_value(name, "stock_entry_sr",
                          read_u32(ram_pointer(SPARK_ENTRY_SR)),
                          spark_entry_sr[t_bit]);
    for (index = 0; index < ARRAY_SIZE(inputs); ++index) {
        if (ram_pointer(inputs[index])[0] != before[index])
            return fail_value(name, "stock_input",
                              ram_pointer(inputs[index])[0], before[index]);
    }
    if (ram_pointer(DWELL_VETO)[0] != expected.veto)
        return fail_value(name, "veto", ram_pointer(DWELL_VETO)[0], expected.veto);
    if (ram_pointer(MISFIRE_LATCH)[0] != expected.latch)
        return fail_value(name, "misfire_latch",
                          ram_pointer(MISFIRE_LATCH)[0], expected.latch);
    if (!fail_bytes(name, "complete_state", ram_pointer(RL_STATE),
                    expected.state, RL_STATE_SIZE))
        return 0;
    return verify_state_guards(name);
}

static int spark_expect(
    const char *name, uint8_t veto, uint8_t latch, uint8_t quiet)
{
    if (ram_pointer(DWELL_VETO)[0] != veto)
        return fail_value(name, "expected_veto", ram_pointer(DWELL_VETO)[0], veto);
    if (ram_pointer(MISFIRE_LATCH)[0] != latch)
        return fail_value(name, "expected_latch",
                          ram_pointer(MISFIRE_LATCH)[0], latch);
    if (ram_pointer(RL_STATE)[ST_QUIET] != quiet)
        return fail_value(name, "expected_quiet",
                          ram_pointer(RL_STATE)[ST_QUIET], quiet);
    return 1;
}

static int spark_offsets_hold(const char *name)
{
    size_t index;

    for (index = 0; index < SPARK_CYLINDERS; ++index) {
        uint16_t actual = read_u16(
            ram_pointer(RL_STATE) + ST_ACCUMULATORS + 2U * index);
        if (actual != spark_offsets[index])
            return fail_value(name, "offset", actual, spark_offsets[index]);
    }
    return 1;
}

struct spark_ineligible_case {
    const char *name;
    uint32_t address;
    uint8_t value;
};

static const struct spark_ineligible_case spark_ineligible_cases[] = {
    {"spark-ineligible-sync", CRANK_SYNC, 0x7f},
    {"spark-ineligible-cam", APC_MODE_SNAPSHOT, 0x40},
    {"spark-ineligible-dwell", DWELL_ANGLE, SPARK_DWELL_LIMIT + 1U},
    {"spark-ineligible-cylinder-low", EVENT_CYLINDER, 0},
    {"spark-ineligible-cylinder-high", EVENT_CYLINDER, SPARK_CYLINDERS + 1U},
};

struct spark_latch_case {
    const char *name;
    uint8_t phase;
    uint8_t quiet;
    uint8_t latch;
    uint8_t expected_quiet;
    uint8_t expected_latch;
};

static const struct spark_latch_case spark_latch_cases[] = {
    {"spark-idle-count", PHASE_IDLE, 12, MISFIRE_MARKER, 13, MISFIRE_MARKER},
    {"spark-idle-release", PHASE_IDLE, 13, MISFIRE_MARKER, 14, 0},
    {"spark-idle-foreign-latch", PHASE_IDLE, 20, 0x32, 21, 0x32},
    {"spark-idle-saturated", PHASE_IDLE, 0xff, MISFIRE_MARKER, 0xff, 0},
    {"spark-cooldown-latch", PHASE_COOLDOWN, 30, MISFIRE_MARKER, 31,
     MISFIRE_MARKER},
    {"spark-corrupt", 3, 0, 0, 1, 0},
};

static const uint16_t spark_sweep_fractions[] = {
    0, 1, 166, 167, 250, 333, 334, 500, 501, 666, 667, 750, 833, 834, 999,
    1000,
};

/* Two aligned 36-match periods per fraction: the cut count of each period
   is within one of 36 * (1 - u), and every event cylinder within one of the
   mean of its six matches. */
static int run_spark_sweep(void)
{
    size_t fraction_index, match, cylinder;

    count_case();
    for (fraction_index = 0;
         fraction_index < ARRAY_SIZE(spark_sweep_fractions); ++fraction_index) {
        uint16_t fraction = spark_sweep_fractions[fraction_index];
        uint32_t ideal = 36U * (TORQUE_ONE - fraction);
        uint32_t period = 0, cuts[SPARK_CYLINDERS] = {0};

        reset_spark_case(PHASE_ACTIVE, MODE_HOLD, fraction);
        for (match = 0; match < 72U; ++match) {
            ram_pointer(EVENT_CYLINDER)[0] = (uint8_t)(match % 6U + 1U);
            ram_pointer(DWELL_VETO)[0] = 0x15;
            if (!spark_match("spark-sweep"))
                return 0;
            if (ram_pointer(DWELL_VETO)[0] & 0x80U) {
                ++period;
                ++cuts[match % 6U];
            }
            if (match % 36U != 35U)
                continue;
            if (1000U * period + 1000U < ideal || 1000U * period > ideal + 1000U)
                return fail_value("spark-sweep", "period_cuts", period, fraction);
            for (cylinder = 0; cylinder < SPARK_CYLINDERS; ++cylinder) {
                uint32_t scaled = 6000U * cuts[cylinder];
                if (scaled + 1000U * 6U < ideal || scaled > ideal + 6000U)
                    return fail_value(
                        "spark-sweep", "cylinder_cuts", cuts[cylinder], fraction);
                cuts[cylinder] = 0;
            }
            period = 0;
        }
    }
    return 1;
}

/* A volatile address keeps the compiler from treating the low vector
   address as a null-pointer offset. */
static volatile uint32_t spark_trap_vector = SPARK_TRAP_VECTOR;

static int run_spark_cases(void)
{
    volatile uint8_t *state = ram_pointer(RL_STATE);
    uint32_t vector;
    size_t index;

    count_case();
    if (read_u32(rom_pointer(SPARK_TABLE_ENTRY)) != SPARK_CUT)
        return fail_value("spark-vector", "table_entry",
                          read_u32(rom_pointer(SPARK_TABLE_ENTRY)), SPARK_CUT);
    vector = read_u32(rom_pointer(spark_trap_vector));
    if (vector != SPARK_CUT)
        return fail_value("spark-vector", "trap_vector", vector, SPARK_CUT);
    write_u32(rom_pointer(spark_trap_vector),
              (uint32_t)(uintptr_t)spark_entry_sr_handler);
    for (index = 0; index < 2; ++index) {
        uint32_t registers[10];
        size_t item;

        write_u32(ram_pointer(SPARK_ENTRY_SR), 0xffffffffU);
        invoke_spark_probe(registers, (uint32_t)index);
        for (item = 0; item < 8; ++item) {
            if (registers[item] != item + 1U)
                return fail_value("spark-vector", "control_register",
                                  registers[item], item + 1U);
        }
        spark_entry_sr[index] = read_u32(ram_pointer(SPARK_ENTRY_SR));
        if ((spark_entry_sr[index] & 1U) != index || registers[9] != registers[8])
            return fail_value("spark-vector", "control_sr",
                              spark_entry_sr[index], registers[8]);
    }
    write_u32(rom_pointer(spark_trap_vector), SPARK_CUT);

    /* A forced timeout match without the armed spark bit changes nothing. */
    count_case();
    reset_spark_case(PHASE_ACTIVE, MODE_HOLD, 0);
    ram_pointer(SPARK_ARMED)[0] = 0x7f;
    if (!spark_match("spark-timeout-match")
            || !spark_expect("spark-timeout-match", 0x15, 0, 0x40))
        return 0;

    /* u = 0 cuts every eligible match; the cut counter wraps. */
    count_case();
    reset_spark_case(PHASE_ACTIVE, MODE_HOLD, 0);
    state[ST_CUTS] = 0xff;
    if (!spark_match("spark-hold-cut")
            || !spark_expect("spark-hold-cut", 0x95, MISFIRE_MARKER, 0))
        return 0;
    if (state[ST_CUTS] != 0)
        return fail_value("spark-hold-cut", "cut_counter", state[ST_CUTS], 0);

    count_case();
    reset_spark_case(PHASE_ACTIVE, MODE_HOLD, 0);
    ram_pointer(MISFIRE_LATCH)[0] = 0x32;
    if (!spark_match("spark-hold-foreign-latch")
            || !spark_expect("spark-hold-foreign-latch", 0x95, 0x32, 0))
        return 0;

    count_case();
    reset_spark_case(PHASE_ACTIVE, MODE_HOLD, TORQUE_ONE);
    if (!spark_match("spark-hold-full-torque")
            || !spark_expect("spark-hold-full-torque", 0x15, MISFIRE_MARKER, 0)
            || !spark_offsets_hold("spark-hold-full-torque"))
        return 0;

    /* An ineligible match leaves every accumulator unchanged, even one that
       an eligible match would cut. */
    for (index = 0; index < ARRAY_SIZE(spark_ineligible_cases); ++index) {
        const struct spark_ineligible_case *test = &spark_ineligible_cases[index];

        count_case();
        reset_spark_case(PHASE_ACTIVE, MODE_HOLD, 0);
        write_u16(state + ST_ACCUMULATORS, SPARK_CUT_ONE - 1U);
        ram_pointer(test->address)[0] = test->value;
        if (!spark_match(test->name)
                || !spark_expect(test->name, 0x15, MISFIRE_MARKER, 0))
            return 0;
        if (read_u16(state + ST_ACCUMULATORS) != SPARK_CUT_ONE - 1U)
            return fail_value(test->name, "accumulator",
                              read_u16(state + ST_ACCUMULATORS),
                              SPARK_CUT_ONE - 1U);
    }

    count_case();
    reset_spark_case(PHASE_ACTIVE, MODE_HOLD, 999);
    write_u16(state + ST_ACCUMULATORS, SPARK_CUT_ONE - 6U);
    ram_pointer(DWELL_ANGLE)[0] = SPARK_DWELL_LIMIT;
    if (!spark_match("spark-dwell-limit")
            || !spark_expect("spark-dwell-limit", 0x95, MISFIRE_MARKER, 0))
        return 0;
    if (read_u16(state + ST_ACCUMULATORS) != 0)
        return fail_value("spark-dwell-limit", "accumulator",
                          read_u16(state + ST_ACCUMULATORS), 0);

    /* An out-of-range accumulator or fraction returns every accumulator to
       its offset without a veto. */
    count_case();
    reset_spark_case(PHASE_ACTIVE, MODE_HOLD, 0);
    write_u16(state + ST_ACCUMULATORS, SPARK_CUT_ONE);
    write_u16(state + ST_ACCUMULATORS + 2U, 7);
    if (!spark_match("spark-accumulator-range")
            || !spark_expect("spark-accumulator-range", 0x15, MISFIRE_MARKER, 0)
            || !spark_offsets_hold("spark-accumulator-range"))
        return 0;

    count_case();
    reset_spark_case(PHASE_ACTIVE, MODE_HOLD, TORQUE_ONE + 1U);
    write_u16(state + ST_ACCUMULATORS + 2U, 7);
    if (!spark_match("spark-fraction-invalid")
            || !spark_expect("spark-fraction-invalid", 0x15, MISFIRE_MARKER, 0)
            || !spark_offsets_hold("spark-fraction-invalid"))
        return 0;

    count_case();
    reset_spark_case(PHASE_ACTIVE, MODE_OBSERVE, 0);
    write_u16(state + ST_ACCUMULATORS + 2U, 7);
    if (!spark_match("spark-observe-active")
            || !spark_expect("spark-observe-active", 0x15, 0, 0)
            || !spark_offsets_hold("spark-observe-active"))
        return 0;

    for (index = 0; index < ARRAY_SIZE(spark_latch_cases); ++index) {
        const struct spark_latch_case *test = &spark_latch_cases[index];

        count_case();
        reset_spark_case(test->phase, MODE_HOLD, 0);
        state[ST_QUIET] = test->quiet;
        ram_pointer(MISFIRE_LATCH)[0] = test->latch;
        write_u16(state + ST_ACCUMULATORS + 2U, 7);
        if (!spark_match(test->name)
                || !spark_expect(test->name, 0x15, test->expected_latch,
                                 test->expected_quiet)
                || !spark_offsets_hold(test->name))
            return 0;
    }

    /* The first match that sees the state leave ACTIVE sets no veto. */
    count_case();
    reset_spark_case(PHASE_ACTIVE, MODE_HOLD, 0);
    if (!spark_match("spark-leave-active")
            || !spark_expect("spark-leave-active", 0x95, MISFIRE_MARKER, 0))
        return 0;
    state[0] = PHASE_COOLDOWN;
    ram_pointer(DWELL_VETO)[0] = 0x15;
    ram_pointer(EVENT_CYLINDER)[0] = 2;
    if (!spark_match("spark-leave-active")
            || !spark_expect("spark-leave-active", 0x15, MISFIRE_MARKER, 1)
            || !spark_offsets_hold("spark-leave-active"))
        return 0;

    return run_spark_sweep();
}

int main(void)
{
    if (!run_structural_cases())
        return 1;
    if (!run_gate_cases())
        return 1;
    if (!run_config_cases())
        return 1;
    if (!run_controller_cases())
        return 1;
    if (!run_activation_cases())
        return 1;
    if (!run_hold_cases())
        return 1;
    if (!run_active_cases())
        return 1;
    if (!run_cooldown_cases())
        return 1;
    if (!run_adapter_cases())
        return 1;
    if (!run_wrapper_cases())
        return 1;
    if (!run_fuel_cut_cases())
        return 1;
    if (!run_feedback_cases())
        return 1;
    if (!run_spark_cases())
        return 1;
    if (case_count != 197U)
        return fail_value("summary", "case_count", case_count, 197);

    printf(
        "VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=%lu "
        "structural=13 gates=39 config=32 controller=24 activation=6 "
        "hold=9 active=15 cooldown=6 adapter=3 wrappers=6 fuel_cut=14 "
        "feedback=8 spark=22 entries=10\n",
        (unsigned long)case_count);
    return 0;
}
