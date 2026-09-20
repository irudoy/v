#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))

#define TEST_RAM_BASE 0x01000000U
#define RAM_SENTINEL_BASE 0xffff5cf0U
#define RAM_SENTINEL_SIZE 0x60U
#define RAM_RESERVATION_START 0xffff5d00U
#define RAM_RESERVATION_END 0xffff5d3cU
#define SELECTOR_STATE 0xffff5d00U
#define FUEL_SHADOW 0xffff5d10U
#ifdef TARGET_VQ37
#define FUEL_SHADOW_SIZE 36U
#define THROTTLE_SHADOW 0xffff5d38U
#define THROTTLE_SHADOW_SIZE 2U
#define NATIVE_FUEL_CUT 0x0006aeb8U
#define NATIVE_SELECTOR 0xffff10e5U
#define NATIVE_RPM 0xffff11acU
#define NATIVE_STATE 0xffff23f5U
#define NATIVE_DELAY 0xffff2449U
#ifdef TARGET_1ND
#define NATIVE_ACTIVE_MASK 0x20U
#define NATIVE_ARMED_MASK 0x10U
#elif defined(TARGET_JK78)
#define NATIVE_ACTIVE_MASK 0x10U
#define NATIVE_ARMED_MASK 0x08U
#else
#error "VQ37 target family is required"
#endif
#else
#define FUEL_SHADOW_SIZE 12U
#define THROTTLE_SHADOW 0xffff5d20U
#define THROTTLE_SHADOW_SIZE 28U
#endif
#define THROTTLE_RUNTIME 0xffff1796U
#define CURRENT_CODE 0xffff2a85U
#define ASCD_STATUS 0xffff41aeU
#define DIAGNOSTIC_STATUS 0xffff2a84U
#define PAYLOAD 0xffff3ad5U

#define SELECTOR_HOST 0x000d2108U
#define STARTUP_WRAPPER 0x000d22a0U
#define OVER_RUN_ADAPTER 0x000d2300U
#define FULL_DFCO_ADAPTER 0x000d2480U
#define IGNITION_ADAPTER 0x000d2340U
#define FUEL_COMP_ADAPTER 0x000d2380U
#define CVTC_TARGET_ADAPTER 0x000d23c0U
#ifdef TARGET_VQ37
/* VQ37 removes exhaust camshaft timing control, so the second idle-ignition
   literal-pool copy reuses the canonical CVTC target adapter slot. */
#define IDLE_IGNITION_POOL_2_ADAPTER 0x000d23c0U
#endif
#ifdef TARGET_DUAL_CVTC
#define SECONDARY_CVTC_TARGET_ADAPTER 0x000d5000U
#endif
#ifdef TARGET_1ND
/* The 1ND ignition coordinator reads four 8x8 state-code surfaces through a
   lookup of their own, so the layout carries a separate adapter behind the
   VQ37 fuel-cut coordinator wrapper. */
#define IGNITION_STATE_ADAPTER 0x000d5080U
#endif
#define FEEDBACK_WRAPPER 0x000d35e0U
#define LIMITER_COMMIT 0x000d3660U
#define FEEDBACK_COUNTS 0x000d3848U
#define IDLE_IGNITION_ADAPTER 0x000d4000U

#define FUEL_STOCK 0x0000934eU
#define THROTTLE_STOCK 0x00009424U
#define THROTTLE_SELECTED_OFFSET 8U

extern uint32_t invoke_r4(uint32_t entry, uint32_t argument);
extern uint32_t invoke_r0(uint32_t entry);

struct family {
    const char *name;
    uint32_t entry;
    uint32_t canonical;
    uint32_t size;
    uint32_t slots[5];
};

struct pass_through {
    const char *name;
    uint32_t entry;
    uint32_t requested;
};

struct selector_case {
    const char *name;
    uint8_t initial[8];
    uint8_t previous;
    uint8_t current;
    uint8_t ascd;
    uint8_t expected[8];
};

struct feedback_case {
    const char *name;
    uint16_t counts;
    uint8_t initial[8];
    const uint8_t *statuses;
    size_t status_count;
    uint8_t expected[8];
};

static const struct family adapter_families[] = {
    {
        "legacy_over_run_fuel_cut", OVER_RUN_ADAPTER, 0x00012718U, 16U,
        {0x00012718U, 0x000d2400U, 0x000d2410U, 0x000d2420U,
         0x000d2430U},
    },
    {
        "legacy_over_run_fuel_restore", OVER_RUN_ADAPTER, 0x00012818U,
        16U,
        {0x00012818U, 0x000d2440U, 0x000d2450U, 0x000d2460U,
         0x000d2470U},
    },
    {
        "over_run_fuel_hold", FULL_DFCO_ADAPTER, 0x000126e4U, 16U,
        {0x000126e4U, 0x000d3f80U, 0x000d3f90U, 0x000d3fa0U,
         0x000d3fb0U},
    },
    {
        "over_run_fuel_cut", FULL_DFCO_ADAPTER, 0x00012718U, 16U,
        {0x00012718U, 0x000d2400U, 0x000d2410U, 0x000d2420U,
         0x000d2430U},
    },
    {
        "over_run_fuel_restore", FULL_DFCO_ADAPTER, 0x00012818U, 16U,
        {0x00012818U, 0x000d2440U, 0x000d2450U, 0x000d2460U,
         0x000d2470U},
    },
    {
        "over_run_fuel_intermediate_restore", FULL_DFCO_ADAPTER,
        0x0001298cU, 16U,
        {0x0001298cU, 0x000d3fc0U, 0x000d3fd0U, 0x000d3fe0U,
         0x000d3ff0U},
    },
#ifdef TARGET_VQ37
    /* VQ37 executes the mode-selected half of its ignition coordinator, so the
       target renderer rewrites the two canonical 16x16 ignition bases to the
       two executed surfaces of that half and reuses the canonical storage. */
    {
        "ignition_surface_hot", IGNITION_ADAPTER, 0x00009a1aU,
        256U,
        {0x00009a1aU, 0x000d2500U, 0x000d2600U, 0x000d2700U,
         0x000d2800U},
    },
    {
        "ignition_surface_cold", IGNITION_ADAPTER, 0x00009b1aU,
        256U,
        {0x00009b1aU, 0x000d2900U, 0x000d2a00U, 0x000d2b00U,
         0x000d2c00U},
    },
#else
    {
        "high_octane_timing_state", IGNITION_ADAPTER, 0x00009a1aU,
        256U,
        {0x00009a1aU, 0x000d2500U, 0x000d2600U, 0x000d2700U,
         0x000d2800U},
    },
    {
        "high_detonation_timing_state", IGNITION_ADAPTER, 0x00009b1aU,
        256U,
        {0x00009b1aU, 0x000d2900U, 0x000d2a00U, 0x000d2b00U,
         0x000d2c00U},
    },
#endif
    {
        "fuel_compensation_main", FUEL_COMP_ADAPTER, 0x0000a29aU, 256U,
        {0x0000a29aU, 0x000d3100U, 0x000d3200U, 0x000d3300U,
         0x000d3400U},
    },
#ifdef TARGET_VQ37
    /* VQ37 reads a second 16x16 compensation surface through the same index
       byte, axis pair, and interpolator as the default surface, so the target
       renderer reuses the canonical exhaust-target allocation for it. */
    {
        "fuel_compensation_main_alternate", FUEL_COMP_ADAPTER,
        0x0000b33aU, 256U,
        {0x0000b33aU, 0x000d2d00U, 0x000d2e00U, 0x000d2f00U,
         0x000d3000U},
    },
#elif defined(TARGET_DUAL_CVTC)
    /* The dual-CVTC layout reuses the canonical exhaust-target allocation
       for the target intake-cam family, so the target renderer rewrites
       0x0000b33a to the target intake-cam target base. */
    {
        "intake_cvtc_target", CVTC_TARGET_ADAPTER,
        0x0000b33aU, 256U,
        {0x0000b33aU, 0x000d2d00U, 0x000d2e00U, 0x000d2f00U,
         0x000d3000U},
    },
#else
    {
        "exhaust_cvtc_target", CVTC_TARGET_ADAPTER,
        0x0000b33aU, 256U,
        {0x0000b33aU, 0x000d2d00U, 0x000d2e00U, 0x000d2f00U,
         0x000d3000U},
    },
#endif
#ifdef TARGET_DUAL_CVTC
    /* The second CVTC family has no canonical counterpart; the runtime
       verifier rewrites 0x0000b43a to the target exhaust-cam target base. */
    {
        "exhaust_cvtc_target", SECONDARY_CVTC_TARGET_ADAPTER,
        0x0000b43aU, 256U,
        {0x0000b43aU, 0x000d5100U, 0x000d5200U, 0x000d5300U,
         0x000d5400U},
    },
#endif
#ifdef TARGET_1ND
    /* The state-code surfaces have no canonical counterpart; the runtime
       verifier rewrites 0x0000f610, 0x0000f710, 0x0000f690, and 0x0000f6d0
       to the four target bases. */
    {
        "ignition_surface_state_3", IGNITION_STATE_ADAPTER,
        0x0000f610U, 64U,
        {0x0000f610U, 0x000d5180U, 0x000d51c0U, 0x000d5200U,
         0x000d5240U},
    },
    {
        "ignition_surface_state_4", IGNITION_STATE_ADAPTER,
        0x0000f710U, 64U,
        {0x0000f710U, 0x000d5280U, 0x000d52c0U, 0x000d5300U,
         0x000d5340U},
    },
    {
        "ignition_surface_state_5", IGNITION_STATE_ADAPTER,
        0x0000f690U, 64U,
        {0x0000f690U, 0x000d5380U, 0x000d53c0U, 0x000d5400U,
         0x000d5440U},
    },
    {
        "ignition_surface_state_6_7", IGNITION_STATE_ADAPTER,
        0x0000f6d0U, 64U,
        {0x0000f6d0U, 0x000d5480U, 0x000d54c0U, 0x000d5500U,
         0x000d5540U},
    },
#endif
    {
        "cold_idle_ignition_timing", IDLE_IGNITION_ADAPTER,
        0x00012196U, 8U,
        {0x00012196U, 0x000d4080U, 0x000d4088U, 0x000d4090U,
         0x000d4098U},
    },
    {
        "idle_ignition_timing", IDLE_IGNITION_ADAPTER, 0x0001219eU,
        8U,
        {0x0001219eU, 0x000d40a0U, 0x000d40a8U, 0x000d40b0U,
         0x000d40b8U},
    },
#ifdef TARGET_VQ37
    /* The VQ37 idle-ignition function holds two literal-pool copies of the same
       stock lookup pointer, and which branches each copy serves is image-
       specific, so both copies are redirected and every reachable table is
       registered under the copy that serves it. */
    {
        "cold_idle_ignition_timing_pool_2",
        IDLE_IGNITION_POOL_2_ADAPTER, 0x00012196U, 8U,
        {0x00012196U, 0x000d4080U, 0x000d4088U, 0x000d4090U,
         0x000d4098U},
    },
    {
        "idle_ignition_timing_alternate",
        IDLE_IGNITION_POOL_2_ADAPTER, 0x0000934eU, 8U,
        {0x0000934eU, 0x000d3500U, 0x000d3508U, 0x000d3510U,
         0x000d3518U},
    },
#endif
};

static const struct pass_through pass_throughs[] = {
    {"overrun_bosch_cut", OVER_RUN_ADAPTER, 0x000126e4U},
    {"overrun_bosch_restore", OVER_RUN_ADAPTER, 0x0001298cU},
    {"full_dfco_unknown", FULL_DFCO_ADAPTER, 0x0001298dU},
    {"ignition_cold", IGNITION_ADAPTER, 0x0000991aU},
#ifdef TARGET_VQ37
    /* The gated coordinator half reads three byte-identical surfaces through
       hooked literals. The target renderer rewrites 0x0000991a, 0x0000e91a,
       and 0x0000ea1a to those three bases; each must reach the stock lookup
       unchanged while a non-default slot is selected. */
    {"ignition_gated_surface_2", IGNITION_ADAPTER, 0x0000e91aU},
    {"ignition_gated_surface_3", IGNITION_ADAPTER, 0x0000ea1aU},
#endif
    {"fuel_compensation_unknown", FUEL_COMP_ADAPTER, 0x0000a29bU},
#ifdef TARGET_VQ37
    {"idle_ignition_pool_2_hidden", IDLE_IGNITION_POOL_2_ADAPTER,
     0x000121a6U},
#else
    {"cvtc_target_unknown", CVTC_TARGET_ADAPTER, 0x0000b33bU},
#endif
#ifdef TARGET_DUAL_CVTC
    {"secondary_cvtc_target_unknown",
     SECONDARY_CVTC_TARGET_ADAPTER, 0x0000b43bU},
#endif
#ifdef TARGET_1ND
    {"ignition_state_unknown", IGNITION_STATE_ADAPTER, 0x0000f611U},
#endif
    {"idle_ignition_hidden", IDLE_IGNITION_ADAPTER, 0x000121a6U},
};

#ifdef TARGET_VQ37
static const uint32_t fuel_cap_slots[] = {
    0x00009040U, 0x000d24f4U, 0x000d24f8U, 0x000d24fcU,
    0x000d353cU,
};

static const uint32_t fuel_curve_slots[] = {
    0x00016bf4U, 0x000d36e0U, 0x000d3700U, 0x000d3720U,
    0x000d3740U,
};
#else
static const uint32_t fuel_slots[] = {
    0x0000934eU, 0x000d3500U, 0x000d3508U, 0x000d3510U,
    0x000d3518U,
};
#endif

static const uint32_t throttle_slots[] = {
    0x0000942cU, 0x000d3520U, 0x000d3522U, 0x000d3524U,
    0x000d3526U,
};

static const struct selector_case selector_cases[] = {
    {
        "idle", {0, 0, 0, 0, 0, 0, 0, 0}, 0x20, 0x20, 0,
        {0, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "arm", {0, 0, 0, 0, 0, 0, 0, 0}, 0x20, 8, 0,
        {0, 1, 0, 1, 0, 0, 0, 0},
    },
    {
        "set-held", {1, 1, 2, 7, 0, 0, 0, 0}, 8, 8, 0,
        {1, 1, 2, 8, 0, 0, 0, 0},
    },
    {
        "set-to-cancel", {1, 1, 2, 7, 0, 0, 0, 0}, 8, 2, 0,
        {1, 2, 2, 8, 0, 0, 0, 0},
    },
    {
        "cancel-held", {2, 2, 3, 9, 0, 0, 0, 0}, 2, 2, 0,
        {2, 2, 3, 10, 0, 0, 0, 0},
    },
    {
        "cancel-to-set", {2, 2, 3, 9, 0, 0, 0, 0}, 2, 8, 0,
        {2, 1, 4, 10, 0, 0, 0, 0},
    },
    {
        "commit-map-1", {3, 1, 1, 9, 0, 0, 0, 0}, 8, 0x20, 0,
        {0, 0, 0, 0, 1, 1, 0, 0},
    },
    {
        "commit-map-5", {1, 1, 5, 9, 0, 0, 0, 0}, 8, 0x20, 0,
        {4, 0, 0, 0, 5, 1, 0, 0},
    },
    {
        "release-zero-abort", {3, 1, 0, 9, 0, 0, 0, 0}, 8, 0, 0,
        {3, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "sixth-pulse-abort", {2, 2, 5, 9, 0, 0, 0, 0}, 2, 8, 0,
        {2, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "timeout-abort", {2, 1, 2, 99, 0, 0, 0, 0}, 8, 8, 0,
        {2, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "ascd-abort", {2, 1, 2, 9, 0, 0, 0, 0}, 8, 8, 0x80,
        {2, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "feedback-blocks", {2, 1, 2, 9, 3, 1, 4, 0}, 8, 0, 0,
        {2, 0, 0, 0, 3, 1, 4, 0},
    },
    {
        "feedback-corrupt", {2, 1, 2, 9, 6, 1, 4, 0}, 8, 0, 0,
        {2, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "idle-feedback-corrupt", {2, 1, 2, 9, 0, 0, 1, 0}, 8, 0, 0,
        {2, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "selector-corrupt", {2, 3, 2, 9, 0, 0, 0, 0}, 8, 0, 0,
        {2, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "invalid-index", {0xff, 1, 2, 9, 3, 1, 4, 0}, 8, 0, 0,
        {0, 0, 0, 0, 0, 0, 0, 0},
    },
};

static const uint8_t disabled_statuses[] = {0xb5};
static const uint8_t two_pulse_statuses[] = {
    0xe5, 0xe5, 0x85, 0x85, 0xe5, 0xe5, 0x85, 0x85,
};
static const uint8_t one_pulse_statuses[] = {0xe5, 0x85};
static const uint8_t idle_statuses[] = {0xb5};

static const struct feedback_case feedback_cases[] = {
    {
        "disabled", 0x0000, {0, 0, 0, 0, 1, 1, 0, 0},
        disabled_statuses, ARRAY_SIZE(disabled_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "two-pulses-2x2", 0x0202, {0, 0, 0, 0, 2, 1, 0, 0},
        two_pulse_statuses, ARRAY_SIZE(two_pulse_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "one-pulse-1x1", 0x0101, {0, 0, 0, 0, 1, 1, 0, 0},
        one_pulse_statuses, ARRAY_SIZE(one_pulse_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "idle", 0x0202, {0, 0, 0, 0, 0, 0, 0, 0},
        idle_statuses, ARRAY_SIZE(idle_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "corrupt-pulses", 0x0202, {0, 0, 0, 0, 6, 1, 0, 0},
        idle_statuses, ARRAY_SIZE(idle_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "corrupt-phase", 0x0202, {0, 0, 0, 0, 1, 3, 0, 0},
        idle_statuses, ARRAY_SIZE(idle_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "corrupt-idle", 0x0202, {0, 0, 0, 0, 0, 0, 1, 0},
        idle_statuses, ARRAY_SIZE(idle_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "missing-off-count", 0x0200, {0, 0, 0, 0, 1, 1, 0, 0},
        idle_statuses, ARRAY_SIZE(idle_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0},
    },
    {
        "missing-on-count", 0x0002, {0, 0, 0, 0, 1, 1, 0, 0},
        idle_statuses, ARRAY_SIZE(idle_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0},
    },
};

static const uint8_t payload_seed[] = {
    0x11, 0x22, 0x33, 0x44, 0x55, 0xb5, 0x77, 0x88,
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

static void read_bytes(
    uint8_t *target, const volatile uint8_t *source, size_t size)
{
    size_t index;

    for (index = 0; index < size; ++index)
        target[index] = source[index];
}

#ifdef TARGET_VQ37
static uint16_t read_be16(const volatile uint8_t *source)
{
    return (uint16_t)(((uint16_t)source[0] << 8) | source[1]);
}

static void write_be16(volatile uint8_t *target, uint16_t value)
{
    target[0] = (uint8_t)(value >> 8);
    target[1] = (uint8_t)value;
}
#endif

static int fail_value(
    const char *name, const char *field, uint32_t actual, uint32_t expected)
{
    printf(
        "VQ_SH_ELF_MAP_SWITCHING status=FAIL case=%s field=%s "
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
                "VQ_SH_ELF_MAP_SWITCHING status=FAIL case=%s field=%s "
                "offset=%lu actual=%02x expected=%02x\n",
                name, field, (unsigned long)index,
                (unsigned int)actual[index], (unsigned int)expected[index]);
            return 0;
        }
    }
    return 1;
}

static void seed_ram(const uint8_t state[8])
{
    fill_bytes(ram_pointer(RAM_SENTINEL_BASE), RAM_SENTINEL_SIZE, 0xa5);
    write_bytes(ram_pointer(SELECTOR_STATE), state, 8);
}

static int verify_ram_guards(const char *name)
{
    volatile uint8_t *ram = ram_pointer(RAM_SENTINEL_BASE);
    size_t reservation_start = RAM_RESERVATION_START - RAM_SENTINEL_BASE;
    size_t reservation_end = RAM_RESERVATION_END - RAM_SENTINEL_BASE;
    size_t selector_end = SELECTOR_STATE + 8U - RAM_SENTINEL_BASE;
    size_t fuel_start = FUEL_SHADOW - RAM_SENTINEL_BASE;
    size_t fuel_end = FUEL_SHADOW + FUEL_SHADOW_SIZE - RAM_SENTINEL_BASE;
    size_t throttle_start = THROTTLE_SHADOW - RAM_SENTINEL_BASE;
    size_t throttle_end =
        THROTTLE_SHADOW + THROTTLE_SHADOW_SIZE - RAM_SENTINEL_BASE;
    size_t offset;

    for (offset = 0; offset < RAM_SENTINEL_SIZE; ++offset) {
        int outside = offset < reservation_start || offset >= reservation_end;
        int internal_gap =
            (offset >= selector_end && offset < fuel_start)
            || (offset >= fuel_end && offset < throttle_start)
            || (offset >= throttle_end && offset < reservation_end);
        if ((outside || internal_gap) && ram[offset] != 0xa5)
            return fail_value(name, "ram_guard", ram[offset], 0xa5);
    }
    return 1;
}

static void expected_limiter_ram(uint8_t expected[RAM_SENTINEL_SIZE], int slot)
{
#ifndef TARGET_VQ37
    uint8_t throttle[28];
#endif
    size_t index;
    size_t selector_offset = SELECTOR_STATE - RAM_SENTINEL_BASE;
    size_t fuel_offset = FUEL_SHADOW - RAM_SENTINEL_BASE;
    size_t throttle_offset = THROTTLE_SHADOW - RAM_SENTINEL_BASE;

    for (index = 0; index < RAM_SENTINEL_SIZE; ++index)
        expected[index] = 0xa5;
    expected[selector_offset] = (uint8_t)slot;
    for (index = 1; index < 8; ++index)
        expected[selector_offset + index] = 0;
#ifdef TARGET_VQ37
    read_bytes(
        expected + fuel_offset, rom_pointer(fuel_cap_slots[slot]), 4);
    read_bytes(
        expected + fuel_offset + 4,
        rom_pointer(fuel_curve_slots[slot]), 32);
    read_bytes(
        expected + throttle_offset, rom_pointer(throttle_slots[slot]), 2);
#else
    read_bytes(expected + fuel_offset, rom_pointer(fuel_slots[slot]), 8);
    read_bytes(expected + fuel_offset + 8, rom_pointer(FUEL_STOCK + 8U), 4);
    read_bytes(throttle, rom_pointer(THROTTLE_STOCK), sizeof(throttle));
    read_bytes(
        throttle + THROTTLE_SELECTED_OFFSET,
        rom_pointer(throttle_slots[slot]), 2);
    for (index = 0; index < sizeof(throttle); ++index)
        expected[throttle_offset + index] = throttle[index];
#endif
}

static int verify_limiter_memory(const char *name, int slot)
{
    uint8_t expected[RAM_SENTINEL_SIZE];
    uint8_t runtime[2];

    expected_limiter_ram(expected, slot);
    if (!fail_bytes(
            name, "limiter_ram", ram_pointer(RAM_SENTINEL_BASE),
            expected, sizeof(expected)))
        return 0;
#ifdef TARGET_VQ37
    runtime[0] = 0xa5;
    runtime[1] = 0xa5;
#else
    read_bytes(runtime, rom_pointer(throttle_slots[slot]), sizeof(runtime));
#endif
    if (!fail_bytes(
            name, "throttle_runtime", ram_pointer(THROTTLE_RUNTIME),
            runtime, sizeof(runtime)))
        return 0;
    return 1;
}

static int run_adapter_cases(void)
{
    static const uint8_t empty_state[8] = {0};
    uint8_t before[RAM_SENTINEL_SIZE];
    size_t family_index;
    size_t slot;

    for (family_index = 0; family_index < ARRAY_SIZE(adapter_families);
         ++family_index) {
        const struct family *family = &adapter_families[family_index];
        for (slot = 0; slot < 5; ++slot) {
            uint8_t state[8] = {0};
            uint32_t selected;

            state[0] = (uint8_t)slot;
            seed_ram(state);
            read_bytes(
                before, ram_pointer(RAM_SENTINEL_BASE), sizeof(before));
            selected = invoke_r4(family->entry, family->canonical);
            if (selected != family->slots[slot])
                return fail_value(
                    family->name, "selected_base", selected,
                    family->slots[slot]);
            if (!fail_bytes(
                    family->name, "ram", ram_pointer(RAM_SENTINEL_BASE),
                    before, sizeof(before)))
                return 0;
        }
        for (slot = 0; slot < 2; ++slot) {
            uint8_t state[8] = {0};
            uint32_t selected;

            state[0] = slot == 0 ? 5U : 0xffU;
            seed_ram(state);
            selected = invoke_r4(family->entry, family->canonical);
            if (selected != family->canonical)
                return fail_value(
                    family->name, "invalid_selected_base", selected,
                    family->canonical);
        }
    }
    for (family_index = 0; family_index < ARRAY_SIZE(pass_throughs);
         ++family_index) {
        const struct pass_through *test = &pass_throughs[family_index];
        uint32_t selected;

        seed_ram(empty_state);
        ram_pointer(SELECTOR_STATE)[0] = 4;
        selected = invoke_r4(test->entry, test->requested);
        if (selected != test->requested)
            return fail_value(
                test->name, "pass_through_base", selected,
                test->requested);
    }
    return 1;
}

static int run_limiter_cases(void)
{
    static const uint8_t requested[] = {0, 1, 2, 3, 4, 5, 0xff};
    size_t index;

    for (index = 0; index < ARRAY_SIZE(requested); ++index) {
        uint8_t state[8] = {0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
                            0xa5};
        uint32_t normalized = requested[index] < 5 ? requested[index] : 0;
        uint32_t returned;

        seed_ram(state);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        returned = invoke_r4(LIMITER_COMMIT, requested[index]);
        if (returned != normalized)
            return fail_value(
                "limiter_commit", "normalized_index", returned,
                normalized);
        if (!verify_limiter_memory("limiter_commit", (int)normalized))
            return 0;

        state[0] = requested[index];
        seed_ram(state);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        returned = invoke_r4(STARTUP_WRAPPER, requested[index]);
        if (returned != 0)
            return fail_value(
                "startup_wrapper", "normalized_index", returned, 0);
        if (!verify_limiter_memory("startup_wrapper", 0))
            return 0;
    }
    return 1;
}

#ifdef TARGET_VQ37
static int verify_native_fuel_cut(
    const char *field, uint16_t rpm, uint32_t expected_return,
    uint8_t expected_state)
{
    uint32_t returned;
    uint8_t state;

    write_be16(ram_pointer(NATIVE_RPM), rpm);
    returned = invoke_r0(NATIVE_FUEL_CUT);
    if (returned != expected_return)
        return fail_value(
            "native_fuel_cut", field, returned, expected_return);
    state = ram_pointer(NATIVE_STATE)[0]
        & (NATIVE_ACTIVE_MASK | NATIVE_ARMED_MASK);
    if (state != expected_state)
        return fail_value(
            "native_fuel_cut", field, state, expected_state);
    return 1;
}

static int run_native_fuel_cut_cases(void)
{
    static const uint8_t empty_state[8] = {0};
    size_t slot;

    for (slot = 0; slot < 5; ++slot) {
        uint16_t activation_cap;
        uint16_t activation_curve;
        uint16_t activation;
        uint16_t release_cap;
        uint16_t release_curve;
        uint16_t release;
        uint32_t committed;
        uint8_t active_state = NATIVE_ACTIVE_MASK | NATIVE_ARMED_MASK;

        seed_ram(empty_state);
        committed = invoke_r4(LIMITER_COMMIT, (uint32_t)slot);
        if (committed != slot)
            return fail_value(
                "native_fuel_cut", "slot", committed, (uint32_t)slot);
        activation_cap = read_be16(ram_pointer(FUEL_SHADOW));
        release_cap = read_be16(ram_pointer(FUEL_SHADOW + 2U));
        activation_curve = read_be16(ram_pointer(FUEL_SHADOW + 4U));
        release_curve = read_be16(ram_pointer(FUEL_SHADOW + 20U));
        activation = activation_cap < activation_curve
            ? activation_cap : activation_curve;
        release = release_cap < release_curve
            ? release_cap : release_curve;
        if (activation == 0U || release == 0U)
            return fail_value(
                "native_fuel_cut", "threshold", 0, 1);

        ram_pointer(NATIVE_SELECTOR)[0] = 15U;
        ram_pointer(NATIVE_STATE)[0] = 0U;
        ram_pointer(NATIVE_DELAY)[0] = 0U;
        if (!verify_native_fuel_cut(
                "activation_below", (uint16_t)(activation - 1U),
                0, 0))
            return 0;
        if (!verify_native_fuel_cut(
                "activation_equal", activation, 1, active_state))
            return 0;
        if (!verify_native_fuel_cut(
                "release_equal", release, 1, active_state))
            return 0;
        if (!verify_native_fuel_cut(
                "release_below", (uint16_t)(release - 1U), 0, 0))
            return 0;
    }
    return 1;
}
#endif

static int all_value(
    const volatile uint8_t *values, size_t size, uint8_t expected)
{
    size_t index;

    for (index = 0; index < size; ++index) {
        if (values[index] != expected)
            return 0;
    }
    return 1;
}

static int verify_optional_selector_shadows(const char *name, int active)
{
    uint8_t expected[RAM_SENTINEL_SIZE];
    uint8_t runtime[2];
    size_t fuel_offset = FUEL_SHADOW - RAM_SENTINEL_BASE;
    size_t throttle_offset = THROTTLE_SHADOW - RAM_SENTINEL_BASE;
    int untouched =
        all_value(ram_pointer(FUEL_SHADOW), FUEL_SHADOW_SIZE, 0xa5)
        && all_value(
            ram_pointer(THROTTLE_SHADOW), THROTTLE_SHADOW_SIZE, 0xa5)
        && all_value(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);

    if (untouched)
        return 1;
    active = active < 5 ? active : 0;
    expected_limiter_ram(expected, active);
    if (!fail_bytes(
            name, "fuel_shadow", ram_pointer(FUEL_SHADOW),
            expected + fuel_offset, FUEL_SHADOW_SIZE))
        return 0;
    if (!fail_bytes(
            name, "throttle_shadow", ram_pointer(THROTTLE_SHADOW),
            expected + throttle_offset, THROTTLE_SHADOW_SIZE))
        return 0;
#ifdef TARGET_VQ37
    runtime[0] = 0xa5;
    runtime[1] = 0xa5;
#else
    read_bytes(runtime, rom_pointer(throttle_slots[active]), sizeof(runtime));
#endif
    return fail_bytes(
        name, "throttle_runtime", ram_pointer(THROTTLE_RUNTIME),
        runtime, sizeof(runtime));
}

static int run_selector_cases(void)
{
    size_t index;

    for (index = 0; index < ARRAY_SIZE(selector_cases); ++index) {
        const struct selector_case *test = &selector_cases[index];
        uint8_t expected_diagnostic;
        int active;

        seed_ram(test->initial);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        ram_pointer(CURRENT_CODE)[0] = test->current;
        ram_pointer(CURRENT_CODE)[1] = test->previous;
        ram_pointer(ASCD_STATUS)[0] = test->ascd;
        ram_pointer(DIAGNOSTIC_STATUS)[0] = 0x25;
        (void)invoke_r4(SELECTOR_HOST, 0);
        if (!fail_bytes(
                test->name, "selector_state", ram_pointer(SELECTOR_STATE),
                test->expected, sizeof(test->expected)))
            return 0;
        active = test->expected[0];
        expected_diagnostic =
            (uint8_t)(0x25U & 0x7fU) | (active == 0 ? 0U : 0x80U);
        if (ram_pointer(DIAGNOSTIC_STATUS)[0] != expected_diagnostic)
            return fail_value(
                test->name, "diagnostic",
                ram_pointer(DIAGNOSTIC_STATUS)[0], expected_diagnostic);
        if (!verify_ram_guards(test->name))
            return 0;
        if (!verify_optional_selector_shadows(test->name, active))
            return 0;
    }
    return 1;
}

static int run_feedback_cases(size_t *invocations)
{
    size_t case_index;

    *invocations = 0;
    for (case_index = 0; case_index < ARRAY_SIZE(feedback_cases);
         ++case_index) {
        const struct feedback_case *test = &feedback_cases[case_index];
        size_t invocation;

        rom_pointer(FEEDBACK_COUNTS)[0] = (uint8_t)(test->counts >> 8);
        rom_pointer(FEEDBACK_COUNTS)[1] = (uint8_t)test->counts;
        seed_ram(test->initial);
        write_bytes(ram_pointer(PAYLOAD), payload_seed, sizeof(payload_seed));
        for (invocation = 0; invocation < test->status_count; ++invocation) {
            size_t byte_index;

            (void)invoke_r4(FEEDBACK_WRAPPER, 0);
            for (byte_index = 0; byte_index < sizeof(payload_seed);
                 ++byte_index) {
                uint8_t expected = byte_index == 5
                    ? test->statuses[invocation]
                    : payload_seed[byte_index];
                if (ram_pointer(PAYLOAD)[byte_index] != expected)
                    return fail_value(
                        test->name, "payload",
                        ram_pointer(PAYLOAD)[byte_index], expected);
            }
            ++*invocations;
        }
        if (!fail_bytes(
                test->name, "feedback_state", ram_pointer(SELECTOR_STATE),
                test->expected, sizeof(test->expected)))
            return 0;
        if (!verify_ram_guards(test->name))
            return 0;
    }
    return 1;
}

int main(void)
{
    size_t feedback_invocations;
    size_t total_cases = ARRAY_SIZE(adapter_families) * 7U
        + ARRAY_SIZE(pass_throughs) + 14U + ARRAY_SIZE(selector_cases)
        + ARRAY_SIZE(feedback_cases);

#ifdef TARGET_VQ37
    total_cases += 20U;
#endif

    if (!run_adapter_cases())
        return 1;
    if (!run_limiter_cases())
        return 1;
#ifdef TARGET_VQ37
    if (!run_native_fuel_cut_cases())
        return 1;
#endif
    if (!run_selector_cases())
        return 1;
    if (!run_feedback_cases(&feedback_invocations))
        return 1;
#ifdef TARGET_1ND
    if (total_cases != 196U)
        return fail_value("summary", "case_count", total_cases, 196);
#elif defined(TARGET_VQ37)
    if (total_cases != 167U)
        return fail_value("summary", "case_count", total_cases, 167);
#elif defined(TARGET_DUAL_CVTC)
    if (total_cases != 139U)
        return fail_value("summary", "case_count", total_cases, 139);
#else
    if (total_cases != 131U)
        return fail_value("summary", "case_count", total_cases, 131);
#endif
    if (feedback_invocations != 17U)
        return fail_value(
            "summary", "feedback_invocations", feedback_invocations, 17);

    printf(
        "VQ_SH_ELF_MAP_SWITCHING status=PASS cases=%lu selector=17 "
#ifdef TARGET_1ND
        "adapters=136 limiter=14 native_fuel=20 feedback=9 "
        "feedback_invocations=%lu entries=14\n",
#elif defined(TARGET_VQ37)
        "adapters=107 limiter=14 native_fuel=20 feedback=9 "
        "feedback_invocations=%lu entries=13\n",
#elif defined(TARGET_DUAL_CVTC)
        "adapters=99 limiter=14 feedback=9 feedback_invocations=%lu "
        "entries=13\n",
#else
        "adapters=91 limiter=14 feedback=9 feedback_invocations=%lu "
        "entries=12\n",
#endif
        (unsigned long)total_cases, (unsigned long)feedback_invocations);
    return 0;
}
