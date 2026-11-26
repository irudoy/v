#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#ifdef P3_BINDINGS_HEADER
#include P3_BINDINGS_HEADER
#endif

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
#else
#define FUEL_SHADOW_SIZE 12U
#define THROTTLE_SHADOW 0xffff5d20U
#define THROTTLE_SHADOW_SIZE 28U
#endif
#define THROTTLE_RUNTIME 0xffff1796U
#define CURRENT_CODE 0xffff2a85U
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
#define DIAGNOSTIC_STATUS 0xffff2a84U
#define PAYLOAD 0xffff3ad5U

#define SELECTOR_HOST 0x000d2108U
#ifndef STARTUP_WRAPPER
#define STARTUP_WRAPPER 0x000d22a0U
#endif
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
#if defined(TARGET_1ND) || defined(TARGET_1ME3B) || defined(TARGET_1EK7A)
/* The SH7059 ignition coordinators read four 8x8 state-code surfaces through
   a lookup of their own, so the layout carries a separate adapter behind the
   VQ37 fuel-cut coordinator wrapper. */
#define TARGET_IGNITION_STATE 1
#define IGNITION_STATE_ADAPTER 0x000d5080U
#endif
#if defined(TARGET_1ND) || defined(TARGET_JK78)
/* These coordinators carry a second, configuration-gated half. */
#define TARGET_GATED_IGNITION 1
#endif
#define FEEDBACK_WRAPPER 0x000d35e0U
#define LIMITER_COMMIT 0x000d3660U
#define FEEDBACK_COUNTS 0x000d3848U
#define IDLE_IGNITION_ADAPTER 0x000d4000U
#ifdef VERIFY_CRUISE_FREE
#ifndef P3_BINDINGS_HEADER
#define CF_CONFIG_ADDR 0x000d6800U
#define CF_STARTUP_INIT 0x000d6820U
#define CF_STATIONARY_WRAPPER 0x000d6840U
#define CF_STEP_ENTRY 0x000d6900U
#define CF_ASCD_ENABLED_ENTRY 0x000d6ba0U
#define CF_FEEDBACK_EXT_ENTRY 0x000d6be0U
#define CF_TACH_180_WRAPPER 0x000d6ca0U
#define CF_TACH_1F9_WRAPPER 0x000d6cc0U
#define CF_TACH_APPLY_ENTRY 0x000d6ce0U
#define CF_RAM_BASE 0xffff6000U
#define CF_RAM_SIZE 32U
#define CF_RPM_FINE 0xffff11eeU
#define CF_RPM_COARSE 0xffff11bcU
#define CF_BRAKE_BYTE 0xffff2451U
#define CF_APP1_ADDR 0xffff269eU
#define CF_APP2_ADDR 0xffff26a2U
#define CF_PORT_STATE 0xffff4185U
#define CF_HCAN1_STATE 0xffff4195U
#define CF_RX_STATE 0xffff3b37U
#define CF_RX_RAW_HI 0xffff3b3dU
#define CF_MIL_BYTE 0xffff3ad8U
#define CF_TACH_180_PAYLOAD 0xffff3afdU
#define CF_TACH_1F9_PAYLOAD 0xffff3ae1U
#endif
#ifndef CF_PORT_READY_MASK
#define CF_PORT_READY_MASK 0x80U
#endif
#ifndef CF_HCAN1_INIT_MASK
#define CF_HCAN1_INIT_MASK 0x01U
#endif
#ifndef CF_BRAKE_MASK
#define CF_BRAKE_MASK 0x80U
#endif
#endif
#ifdef VERIFY_EEPROM_PERSISTENCE
#ifndef P3_BINDINGS_HEADER
#define EE_CONFIG_ADDR 0x000d7200U
#define EE_BOOT_RESTORE 0x000d7210U
#define EE_TASK_WRAPPER 0x000d73a0U
#define EE_RAM_BASE 0xffff6020U
#define EE_RAM_SIZE 64U
#define EE_WARM_REINIT_ENTRY 0x00027c42U
#define EE_WARM_REINIT_RETURN 0x00027c4cU
#define EE_STOCK_BUSY 0xffff2cd4U
#define EE_PORT_STATE 0xffff4185U
#define EE_SHUTDOWN_REQ 0xffff4213U
#define EE_SHUTDOWN_STATE 0xffff39dcU
#define EE_REINIT_MODE 0xffff84a8U
#define EE_VBAT 0xffff1188U
#define EE_PCDR_ADDR 0xfffff73eU
#define EE_PLDR_ADDR 0xfffff75eU
#endif
#ifndef EE_IG_ON_MASK
#define EE_IG_ON_MASK 0x80U
#endif
#ifndef EE_START_MASK
#define EE_START_MASK 0x40U
#endif
#ifndef EE_SHUTDOWN_REQ_MASK
#define EE_SHUTDOWN_REQ_MASK 0x80U
#endif
#define M95320_BASE 0x01010000U
#define EE_PAGE_A_OFF 0x0680U
#define EE_PAGE_B_OFF 0x0700U
#define EE_VALID_MARKER 0xa65dc39eU
#endif

#define FUEL_STOCK 0x0000934eU
#define THROTTLE_STOCK 0x00009424U
#define THROTTLE_SELECTED_OFFSET 8U

extern uint32_t invoke_r4(uint32_t entry, uint32_t argument);
extern uint32_t invoke_r0(uint32_t entry);
#ifdef VERIFY_EEPROM_PERSISTENCE
extern uint32_t invoke_with_saved_pr(uint32_t entry, uint32_t saved_pr);
#endif

#ifdef VERIFY_7MFK_THROTTLE_SCALAR
extern uint32_t invoke_throttle_scalar(
    uint32_t entry, uint32_t incoming, uint32_t *observed_sr);
#endif

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
    uint8_t expected_limiter_write;
};

struct feedback_case {
    const char *name;
    uint16_t counts;
    uint8_t initial[8];
    const uint8_t *statuses;
    size_t status_count;
    uint8_t expected[8];
    uint8_t expected_status_pointer;
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
#ifdef TARGET_IGNITION_STATE
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
#ifdef TARGET_GATED_IGNITION
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
#ifdef TARGET_IGNITION_STATE
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
        {0, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "arm", {0, 0, 0, 0, 0, 0, 0, 0}, 0x20, 8, 0,
        {0, 1, 0, 1, 0, 0, 0, 0}, 0,
    },
    {
        "set-held", {1, 1, 2, 7, 0, 0, 0, 0}, 8, 8, 0,
        {1, 1, 2, 8, 0, 0, 0, 0}, 0,
    },
    {
        "set-to-cancel", {1, 1, 2, 7, 0, 0, 0, 0}, 8, 2, 0,
        {1, 2, 2, 8, 0, 0, 0, 0}, 0,
    },
    {
        "cancel-held", {2, 2, 3, 9, 0, 0, 0, 0}, 2, 2, 0,
        {2, 2, 3, 10, 0, 0, 0, 0}, 0,
    },
    {
        "cancel-to-set", {2, 2, 3, 9, 0, 0, 0, 0}, 2, 8, 0,
        {2, 1, 4, 10, 0, 0, 0, 0}, 0,
    },
    {
        "commit-map-1", {3, 1, 1, 9, 0, 0, 0, 0}, 8, 0x20, 0,
        {0, 0, 0, 0, 1, 1, 0, 0}, 1,
    },
    {
        "commit-map-5", {1, 1, 5, 9, 0, 0, 0, 0}, 8, 0x20, 0,
        {4, 0, 0, 0, 5, 1, 0, 0}, 1,
    },
    {
        "release-zero-abort", {3, 1, 0, 9, 0, 0, 0, 0}, 8, 0, 0,
        {3, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "sixth-pulse-abort", {2, 2, 5, 9, 0, 0, 0, 0}, 2, 8, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "timeout-abort", {2, 1, 2, 99, 0, 0, 0, 0}, 8, 8, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "ascd-abort", {2, 1, 2, 9, 0, 0, 0, 0}, 8, 8, ASCD_MAIN,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "ascd-foreign-flags", {1, 1, 2, 7, 0, 0, 0, 0}, 8, 8,
        ASCD_FOREIGN_FLAGS,
        {1, 1, 2, 8, 0, 0, 0, 0}, 0,
    },
    {
        "feedback-blocks", {2, 1, 2, 9, 3, 1, 4, 0}, 8, 0, 0,
        {2, 0, 0, 0, 3, 1, 4, 0}, 0,
    },
    {
        "feedback-corrupt", {2, 1, 2, 9, 6, 1, 4, 0}, 8, 0, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "idle-feedback-corrupt", {2, 1, 2, 9, 0, 0, 1, 0}, 8, 0, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "selector-corrupt", {2, 3, 2, 9, 0, 0, 0, 0}, 8, 0, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "invalid-index", {0xff, 1, 2, 9, 3, 1, 4, 0}, 8, 0, 0,
        {0, 0, 0, 0, 0, 0, 0, 0}, 1,
    },
#ifdef VERIFY_SELECTOR_FEEDBACK_GUARDS
    {
        "feedback-off-blocks", {2, 1, 2, 9, 3, 2, 4, 0}, 8, 0, 0,
        {2, 0, 0, 0, 3, 2, 4, 0}, 0,
    },
    {
        "feedback-phase-three", {2, 1, 2, 9, 3, 3, 4, 0}, 8, 0, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "feedback-on-zero-pulses", {2, 1, 2, 9, 0, 1, 4, 0}, 8, 0, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "feedback-off-zero-pulses", {2, 1, 2, 9, 0, 2, 4, 0}, 8, 0, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "count-six", {2, 1, 6, 9, 0, 0, 0, 0}, 8, 8, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "count-ff", {2, 1, 0xff, 9, 0, 0, 0, 0}, 8, 8, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "ticks-one-hundred", {2, 1, 2, 100, 0, 0, 0, 0}, 8, 8, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "ticks-ff", {2, 1, 2, 0xff, 0, 0, 0, 0}, 8, 8, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "armed-set-zero-ticks", {2, 1, 2, 0, 0, 0, 0, 0}, 8, 8, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "armed-cancel-zero-ticks", {2, 2, 2, 0, 0, 0, 0, 0}, 2, 2, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "idle-with-count", {2, 0, 1, 0, 0, 0, 0, 0}, 0x20, 8, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "idle-with-ticks", {2, 0, 0, 1, 0, 0, 0, 0}, 0x20, 8, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "idle-held-set", {2, 0, 0, 0, 0, 0, 0, 0}, 8, 8, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "set-wrong-previous", {2, 1, 2, 9, 0, 0, 0, 0}, 2, 0x20, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "cancel-wrong-previous", {2, 2, 2, 9, 0, 0, 0, 0}, 8, 8, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "cancel-invalid-current", {2, 2, 2, 9, 0, 0, 0, 0}, 2, 0x20, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "set-release-zero-count", {2, 1, 0, 9, 0, 0, 0, 0}, 8, 0x20, 0,
        {2, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
#endif
};

static const uint8_t disabled_statuses[] = {0xb5};
static const uint8_t two_pulse_statuses[] = {
    0xc5, 0xc5, 0x85, 0x85, 0xc5, 0xc5, 0x85, 0x85,
};
static const uint8_t one_pulse_statuses[] = {0xc5, 0x85};
static const uint8_t idle_statuses[] = {0xb5};

static const struct feedback_case feedback_cases[] = {
    {
        "disabled", 0x0000, {0, 0, 0, 0, 1, 1, 0, 0},
        disabled_statuses, ARRAY_SIZE(disabled_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "two-pulses-2x2", 0x0202, {0, 0, 0, 0, 2, 1, 0, 0},
        two_pulse_statuses, ARRAY_SIZE(two_pulse_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0}, 1,
    },
    {
        "one-pulse-1x1", 0x0101, {0, 0, 0, 0, 1, 1, 0, 0},
        one_pulse_statuses, ARRAY_SIZE(one_pulse_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0}, 1,
    },
    {
        "idle", 0x0202, {0, 0, 0, 0, 0, 0, 0, 0},
        idle_statuses, ARRAY_SIZE(idle_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "corrupt-pulses", 0x0202, {0, 0, 0, 0, 6, 1, 0, 0},
        idle_statuses, ARRAY_SIZE(idle_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "corrupt-phase", 0x0202, {0, 0, 0, 0, 1, 3, 0, 0},
        idle_statuses, ARRAY_SIZE(idle_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "corrupt-idle", 0x0202, {0, 0, 0, 0, 0, 0, 1, 0},
        idle_statuses, ARRAY_SIZE(idle_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "missing-off-count", 0x0200, {0, 0, 0, 0, 1, 1, 0, 0},
        idle_statuses, ARRAY_SIZE(idle_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
    {
        "missing-on-count", 0x0002, {0, 0, 0, 0, 1, 1, 0, 0},
        idle_statuses, ARRAY_SIZE(idle_statuses),
        {0, 0, 0, 0, 0, 0, 0, 0}, 0,
    },
#ifdef VERIFY_SELECTOR_FEEDBACK_GUARDS
    {
        "on-zero-pulses", 0x0202, {2, 1, 2, 9, 0, 1, 7, 0x7e},
        idle_statuses, ARRAY_SIZE(idle_statuses),
        {2, 1, 2, 9, 0, 0, 0, 0}, 0,
    },
    {
        "off-zero-pulses", 0x0202, {2, 1, 2, 9, 0, 2, 7, 0x7e},
        idle_statuses, ARRAY_SIZE(idle_statuses),
        {2, 1, 2, 9, 0, 0, 0, 0}, 0,
    },
#endif
};

static const uint8_t payload_seed[] = {
    0x11, 0x22, 0x33, 0x44, 0x55, 0xb5, 0x77, 0x88,
};

static volatile uint8_t *ram_pointer(uint32_t original)
{
#ifdef TARGET_DUAL_BANK_MMIO
    if (original >= 0xfffff000U)
        return (volatile uint8_t *)(uintptr_t)(0x01028000U + (original - 0xfffff000U));
    if (original >= 0xffff0000U)
        return (volatile uint8_t *)(uintptr_t)(TEST_RAM_BASE + (original & 0xffffU));
    if (original >= 0xfffe8000U)
        return (volatile uint8_t *)(uintptr_t)(0x01020000U + (original - 0xfffe8000U));
#endif
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

#if defined(TARGET_VQ37) || defined(VERIFY_7MFK_FUEL_CUT) || defined(VERIFY_7MFK_THROTTLE_SCALAR) || defined(VERIFY_CRUISE_FREE) || defined(VERIFY_EEPROM_PERSISTENCE)
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

#ifdef VERIFY_EEPROM_PERSISTENCE
static volatile uint8_t *m95320_ptr(uint32_t offset)
{
    return (volatile uint8_t *)(uintptr_t)(M95320_BASE + offset);
}

static volatile uint32_t *m95320_u32(uint32_t offset)
{
    return (volatile uint32_t *)(uintptr_t)(M95320_BASE + offset);
}

static uint32_t ee_read_be32(const volatile uint8_t *source)
{
    return ((uint32_t)source[0] << 24)
        | ((uint32_t)source[1] << 16)
        | ((uint32_t)source[2] << 8)
        | (uint32_t)source[3];
}

static void ee_write_be32(volatile uint8_t *target, uint32_t value)
{
    target[0] = (uint8_t)(value >> 24);
    target[1] = (uint8_t)(value >> 16);
    target[2] = (uint8_t)(value >> 8);
    target[3] = (uint8_t)value;
}

static uint32_t ee_crc32_8(const uint8_t data[8])
{
    uint32_t crc = 0xffffffffU;
    size_t i, bit;

    for (i = 0; i < 8U; ++i) {
        crc ^= (uint32_t)data[i];
        for (bit = 0; bit < 8U; ++bit) {
            if (crc & 1U)
                crc = (crc >> 1) ^ 0xedb88320U;
            else
                crc >>= 1;
        }
    }
    return ~crc;
}

static void ee_build_record(uint8_t out[16], uint8_t slot, uint32_t generation)
{
    uint32_t crc;

    out[0] = 'M';
    out[1] = 'S';
    out[2] = 1U;
    out[3] = slot;
    out[4] = (uint8_t)(generation >> 24);
    out[5] = (uint8_t)(generation >> 16);
    out[6] = (uint8_t)(generation >> 8);
    out[7] = (uint8_t)generation;
    crc = ee_crc32_8(out);
    out[8] = (uint8_t)(crc >> 24);
    out[9] = (uint8_t)(crc >> 16);
    out[10] = (uint8_t)(crc >> 8);
    out[11] = (uint8_t)crc;
    out[12] = (uint8_t)(EE_VALID_MARKER >> 24);
    out[13] = (uint8_t)(EE_VALID_MARKER >> 16);
    out[14] = (uint8_t)(EE_VALID_MARKER >> 8);
    out[15] = (uint8_t)EE_VALID_MARKER;
}

static void ee_reset_device(int erase_pages)
{
    volatile uint8_t *ctrl = m95320_ptr(0x1000U);

    if (erase_pages) {
        fill_bytes(m95320_ptr(EE_PAGE_A_OFF), 32U, 0xffU);
        fill_bytes(m95320_ptr(EE_PAGE_B_OFF), 32U, 0xffU);
    }
    fill_bytes(ctrl, 32U, 0U);
    ctrl[0x1c] = 3U; /* reset EEPROM FSM + SCI2 */
    write_be16(ram_pointer(EE_PCDR_ADDR), 0x0015U);
}

static void ee_seed_admitted(void)
{
    ram_pointer(EE_STOCK_BUSY)[0] = 0U;
    write_be16(ram_pointer(EE_PLDR_ADDR), 0x0010U);
    ram_pointer(EE_PORT_STATE)[0] = EE_IG_ON_MASK;
    ram_pointer(EE_SHUTDOWN_REQ)[0] = 0x00U;
    ee_write_be32(ram_pointer(EE_SHUTDOWN_STATE), 0U);
    ee_write_be32(ram_pointer(EE_REINIT_MODE), 0U);
    ram_pointer(EE_VBAT)[0] = 0x90U;
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

#ifdef VERIFY_EEPROM_PERSISTENCE
    ee_reset_device(1);
#endif
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
#ifdef EE_STARTUP_COLD_CALL_PC
        /* Relocated startup_wrapper is fail-closed: non-cold calls preserve
           the live valid selector (and clamp invalid slots >= 5 to 0). */
        returned = invoke_r4(STARTUP_WRAPPER, requested[index]);
        if (returned != normalized)
            return fail_value(
                "startup_wrapper", "normalized_index", returned, normalized);
        if (!verify_limiter_memory("startup_wrapper", (int)normalized))
            return 0;
#else
        returned = invoke_r4(STARTUP_WRAPPER, requested[index]);
        if (returned != 0)
            return fail_value(
                "startup_wrapper", "normalized_index", returned, 0);
        if (!verify_limiter_memory("startup_wrapper", 0))
            return 0;
#endif
    }
#ifdef VERIFY_EEPROM_PERSISTENCE
    {
        uint8_t rec[16];
        uint8_t state[8] = {0, 0, 0, 0, 0, 0, 0, 0};
#ifdef EE_STARTUP_COLD_CALL_PC
        uint32_t saved_hook;

        /* Cold boot with blank EEPROM via real stock callsite -> CAN -> startup_wrapper. */
        ee_reset_device(1);
        state[0] = 3U;
        seed_ram(state);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        ram_pointer(CF_RAM_BASE)[0] = 0x03U;
        invoke_r0(EE_STARTUP_COLD_CALL_PC);
        if (ram_pointer(SELECTOR_STATE)[0] != 0U || ram_pointer(CF_RAM_BASE)[0] != 0U)
            return fail_value("startup_cold_blank", "slot", ram_pointer(SELECTOR_STATE)[0], 0U);
        if (!verify_limiter_memory("startup_cold_blank", 0))
            return 0;

        /* CAN-wrapped cold boot restores valid non-default slot 3 (index 2) from Page A. */
        ee_reset_device(1);
        ee_build_record(rec, 3U, 7U);
        write_bytes(m95320_ptr(EE_PAGE_A_OFF), rec, 16U);
        state[0] = 0U;
        seed_ram(state);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        invoke_r0(EE_STARTUP_COLD_CALL_PC);
        if (ram_pointer(SELECTOR_STATE)[0] != 2U)
            return fail_value("startup_cold_can_restore", "slot", ram_pointer(SELECTOR_STATE)[0], 2U);
        if (!verify_limiter_memory("startup_cold_can_restore", 2))
            return 0;

        /* Direct standalone cold boot (hook points straight to STARTUP_WRAPPER, no CAN wrapper). */
        saved_hook = ee_read_be32(rom_pointer(EE_STARTUP_HOOK_SLOT));
        ee_write_be32(rom_pointer(EE_STARTUP_HOOK_SLOT), STARTUP_WRAPPER);
        ee_reset_device(1);
        ee_build_record(rec, 4U, 9U);
        write_bytes(m95320_ptr(EE_PAGE_B_OFF), rec, 16U);
        state[0] = 0U;
        seed_ram(state);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        invoke_r0(EE_STARTUP_COLD_CALL_PC);
        ee_write_be32(rom_pointer(EE_STARTUP_HOOK_SLOT), saved_hook);
        if (ram_pointer(SELECTOR_STATE)[0] != 3U)
            return fail_value("startup_cold_direct_restore", "slot", ram_pointer(SELECTOR_STATE)[0], 3U);
        if (!verify_limiter_memory("startup_cold_direct_restore", 3))
            return 0;

        /* Warm/non-cold direct call preserves live valid slot 3 and CF/EEPROM RAM. */
        ee_reset_device(1);
        state[0] = 3U;
        seed_ram(state);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        ram_pointer(CF_RAM_BASE)[0] = 0x03U;
        ram_pointer(EE_RAM_BASE)[0] = 0x02U;
        invoke_r0(STARTUP_WRAPPER);
        if (ram_pointer(SELECTOR_STATE)[0] != 3U
                || ram_pointer(CF_RAM_BASE)[0] != 0x03U
                || ram_pointer(EE_RAM_BASE)[0] != 0x02U)
            return fail_value(
                "startup_warm_direct", "slot", ram_pointer(SELECTOR_STATE)[0], 3U);
        if (!verify_limiter_memory("startup_warm_direct", 3))
            return 0;

        /* Warm/non-cold clamps invalid live selector (>4) to Map 1 (0). */
        state[0] = 5U;
        seed_ram(state);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        invoke_r0(STARTUP_WRAPPER);
        if (ram_pointer(SELECTOR_STATE)[0] != 0U)
            return fail_value(
                "startup_warm_clamp", "slot", ram_pointer(SELECTOR_STATE)[0], 0U);
        if (!verify_limiter_memory("startup_warm_clamp", 0))
            return 0;

        /* Foreign caller with spoofed @(4,r15)==cold_return_pc must NOT trigger cold boot. */
        state[0] = 4U;
        seed_ram(state);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        ram_pointer(EE_RAM_BASE)[0] = 0x03U;
        invoke_with_saved_pr(STARTUP_WRAPPER, EE_STARTUP_COLD_RETURN_PC);
        if (ram_pointer(SELECTOR_STATE)[0] != 4U
                || ram_pointer(EE_RAM_BASE)[0] != 0x03U)
            return fail_value(
                "startup_foreign_spoof", "slot", ram_pointer(SELECTOR_STATE)[0], 4U);
        if (!verify_limiter_memory("startup_foreign_spoof", 4))
            return 0;

        /* CAN-wrapped non-cold call (PR==can_return_pc, @(4,r15)!=cold_return_pc) preserves state. */
        state[0] = 4U;
        seed_ram(state);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        ram_pointer(EE_RAM_BASE)[0] = 0x03U;
        invoke_r0(EE_CAN_STARTUP_WRAPPER);
        if (ram_pointer(SELECTOR_STATE)[0] != 4U
                || ram_pointer(EE_RAM_BASE)[0] != 0x03U)
            return fail_value(
                "startup_warm_can", "slot", ram_pointer(SELECTOR_STATE)[0], 4U);
        if (!verify_limiter_memory("startup_warm_can", 4))
            return 0;
#else
        uint32_t returned;

        /* Cold boot restores valid non-default slot 3 (index 2) from Page A. */
        ee_reset_device(1);
        ee_build_record(rec, 3U, 7U);
        write_bytes(m95320_ptr(EE_PAGE_A_OFF), rec, 16U);
        seed_ram(state);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        returned = invoke_r4(STARTUP_WRAPPER, 0U);
        if (returned != 2U)
            return fail_value("startup_cold_restore", "slot", returned, 2U);
        if (!verify_limiter_memory("startup_cold_restore", 2))
            return 0;

        /* Direct stock warm reinit chain (0x27C42 -> 0x27CE4 -> 0xD22A0, PR=0x27C4C):
           preserves live valid slot 3 (index 3) and active CF/EEPROM RAM. */
        ee_reset_device(1);
        state[0] = 3U;
        seed_ram(state);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        ram_pointer(CF_RAM_BASE)[0] = 0x03U;
        ram_pointer(EE_RAM_BASE)[0] = 0x02U;
        invoke_r0(EE_WARM_REINIT_ENTRY);
        if (ram_pointer(SELECTOR_STATE)[0] != 3U
                || ram_pointer(CF_RAM_BASE)[0] != 0x03U
                || ram_pointer(EE_RAM_BASE)[0] != 0x02U)
            return fail_value(
                "startup_warm_direct", "slot", ram_pointer(SELECTOR_STATE)[0], 3U);
        if (!verify_limiter_memory("startup_warm_direct", 3))
            return 0;

        /* Direct warm reinit clamps invalid live selector (>4) to Map 1 (0). */
        state[0] = 5U;
        seed_ram(state);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        invoke_r0(EE_WARM_REINIT_ENTRY);
        if (ram_pointer(SELECTOR_STATE)[0] != 0U)
            return fail_value(
                "startup_warm_clamp", "slot", ram_pointer(SELECTOR_STATE)[0], 0U);
        if (!verify_limiter_memory("startup_warm_clamp", 0))
            return 0;

        /* Layered Rolling-Launch warm reinit (@(4,r15) == 0x27C4C): preserves slot 4. */
        state[0] = 4U;
        seed_ram(state);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        ram_pointer(EE_RAM_BASE)[0] = 0x03U;
        invoke_with_saved_pr(STARTUP_WRAPPER, EE_WARM_REINIT_RETURN);
        if (ram_pointer(SELECTOR_STATE)[0] != 4U
                || ram_pointer(EE_RAM_BASE)[0] != 0x03U)
            return fail_value(
                "startup_warm_layered", "slot", ram_pointer(SELECTOR_STATE)[0], 4U);
        if (!verify_limiter_memory("startup_warm_layered", 4))
            return 0;
#endif

        ee_reset_device(1);
    }
#endif
    return 1;
}

#ifdef VERIFY_7MFK_THROTTLE_SCALAR
/* The real clamp returns through an observation stub after its delay slot
   and both branch outcomes, outside [0x77ac0,0x77ace). */
static int run_throttle_scalar_consumer_case(
    uint8_t requested, uint16_t threshold, uint32_t incoming, size_t *cases)
{
    static const uint8_t empty_state[8] = {0};
    uint8_t saved_stock[2], saved_slot[2], shadows[RAM_SENTINEL_SIZE];
    uint8_t runtime[2];
    uint32_t saved_gbr, after_gbr, before_sp, after_sp, before_sr, observed_sr;
    uint32_t sentinel_gbr = 0x2468ace0U;
    uint32_t returned, expected = incoming > threshold ? threshold : incoming;
    unsigned normalized = requested < ARRAY_SIZE(throttle_slots) ? requested : 0;
    uint32_t source = throttle_slots[normalized];
    uint32_t stock_scalar = THROTTLE_STOCK + THROTTLE_SELECTED_OFFSET;

    read_bytes(saved_stock, rom_pointer(stock_scalar), sizeof(saved_stock));
    read_bytes(saved_slot, rom_pointer(source), sizeof(saved_slot));
    write_be16(rom_pointer(source), threshold);
    seed_ram(empty_state);
    if (invoke_r4(LIMITER_COMMIT, requested) != normalized)
        return fail_value("throttle_scalar_consumer", "selected_bank", requested, normalized);
    if (read_be16(ram_pointer(THROTTLE_SHADOW + THROTTLE_SELECTED_OFFSET)) != threshold)
        return fail_value("throttle_scalar_consumer", "selected_threshold",
            read_be16(ram_pointer(THROTTLE_SHADOW + THROTTLE_SELECTED_OFFSET)), threshold);
    read_bytes(shadows, ram_pointer(RAM_SENTINEL_BASE), sizeof(shadows));
    read_bytes(runtime, ram_pointer(THROTTLE_RUNTIME), sizeof(runtime));
    /* Read-through of the old calibration word must produce a different limit. */
    write_be16(rom_pointer(stock_scalar), (uint16_t)(threshold ^ 0xffffU));
    __asm__ volatile (
        "stc gbr,%0\n\tmov r15,%1\n\tstc sr,%2\n\tldc %3,gbr"
        : "=&r" (saved_gbr), "=&r" (before_sp), "=&r" (before_sr)
        : "r" (sentinel_gbr) : "memory");
    returned = invoke_throttle_scalar(0x00077ac0U, incoming, &observed_sr);
    __asm__ volatile (
        "stc gbr,%0\n\tmov r15,%1\n\tldc %2,gbr"
        : "=&r" (after_gbr), "=&r" (after_sp) : "r" (saved_gbr) : "memory");
    write_bytes(rom_pointer(stock_scalar), saved_stock, sizeof(saved_stock));
    write_bytes(rom_pointer(source), saved_slot, sizeof(saved_slot));
    ++*cases;
    if (returned != expected)
        return fail_value("throttle_scalar_consumer", "clamp_result", returned, expected);
    if ((observed_sr & 1U) != (incoming > threshold))
        return fail_value("throttle_scalar_consumer", "unsigned_comparison", observed_sr & 1U, incoming > threshold);
    if ((observed_sr & ~1U) != (before_sr & ~1U))
        return fail_value("throttle_scalar_consumer", "preserved_sr", observed_sr & ~1U, before_sr & ~1U);
    if (after_gbr != sentinel_gbr)
        return fail_value("throttle_scalar_consumer", "gbr", after_gbr, sentinel_gbr);
    if (after_sp != before_sp)
        return fail_value("throttle_scalar_consumer", "stack", after_sp, before_sp);
    return fail_bytes("throttle_scalar_consumer", "shadow_read_only",
            ram_pointer(RAM_SENTINEL_BASE), shadows, sizeof(shadows))
        && fail_bytes("throttle_scalar_consumer", "runtime_read_only",
            ram_pointer(THROTTLE_RUNTIME), runtime, sizeof(runtime));
}

static int run_throttle_scalar_consumer_cases(void)
{
    static const uint8_t requested[] = {0, 1, 2, 3, 4, 5, 0xff};
    static const uint16_t thresholds[] = {0, 1, 0x7fffU, 0x8000U, 0xfffeU, 0xffffU};
    static const uint32_t inputs[] = {
        0, 1, 0x7fffU, 0x8000U, 0xffffU, 0x10000U,
        0x7fffffffU, 0x80000000U, 0xffffffffU,
    };
    size_t bank, threshold, sample, cases = 0;

    for (bank = 0; bank < ARRAY_SIZE(requested); ++bank)
        for (threshold = 0; threshold < ARRAY_SIZE(thresholds); ++threshold) {
            uint16_t limit = thresholds[threshold];
            for (sample = 0; sample < ARRAY_SIZE(inputs); ++sample)
                if (!run_throttle_scalar_consumer_case(
                        requested[bank], limit, inputs[sample], &cases))
                    return 0;
            if (limit && !run_throttle_scalar_consumer_case(
                    requested[bank], limit, (uint32_t)limit - 1U, &cases))
                return 0;
            if (!run_throttle_scalar_consumer_case(
                    requested[bank], limit, limit, &cases)
                    || !run_throttle_scalar_consumer_case(
                        requested[bank], limit, (uint32_t)limit + 1U, &cases))
                return 0;
        }
    printf("VQ_SH_ELF_MAP_SWITCHING_THROTTLE_SCALAR status=PASS cases=%lu entries=1\n",
        (unsigned long)cases);
    return 1;
}
#endif

#ifdef VERIFY_7MFK_FUEL_CUT
/* The composed pointer is bound before the three declared RAM translations.
   Mutable calibration data supplies boundary inputs; instructions stay intact. */
#define FUEL_CUT_CONSUMER 0x0004f282U
#define FUEL_CUT_STATE 0xffff2497U
#define FUEL_CUT_TIMER 0xffff24f1U
#define FUEL_CUT_RPM 0xffff11bcU
#define FUEL_CUT_GUARD 0xffff2440U
#define FUEL_CUT_GUARD_SIZE 0xc0U

static int run_fuel_cut_consumer_case(
    uint8_t requested, unsigned pair, uint16_t activation, uint16_t release,
    uint16_t rpm, uint8_t initial, uint8_t timer, uint8_t delay,
    unsigned missing_gate, size_t *cases)
{
    static const uint8_t empty_state[8] = {0};
    static const unsigned activation_offsets[] = {0, 2, 8};
    static const unsigned release_offsets[] = {4, 6, 10};
    uint8_t expected[FUEL_CUT_GUARD_SIZE];
    uint8_t shadows[RAM_SENTINEL_SIZE];
    uint8_t saved_stock[12];
    uint8_t saved_slot[8];
    uint8_t saved_configuration = rom_pointer(0x8b38U)[0];
    uint8_t saved_delay = rom_pointer(0x8c69U)[0];
    uint8_t expected_state = initial;
    uint8_t expected_timer = timer;
    uint32_t saved_gbr, after_gbr, before_sp, after_sp, returned;
    uint32_t sentinel_gbr = 0x13579bdfU;
    unsigned normalized = requested < ARRAY_SIZE(fuel_slots) ? requested : 0;
    uint32_t source = fuel_slots[normalized];

    read_bytes(saved_stock, rom_pointer(FUEL_STOCK), sizeof(saved_stock));
    read_bytes(saved_slot, rom_pointer(source), sizeof(saved_slot));
    /* Each bank has distinct words, including the two fallback pairs. */
    write_be16(rom_pointer(source), (uint16_t)(0x6000U + normalized * 0x100U));
    write_be16(rom_pointer(source + 2U), (uint16_t)(0x7000U + normalized * 0x100U));
    write_be16(rom_pointer(source + 4U), (uint16_t)(0x5000U + normalized * 0x100U));
    write_be16(rom_pointer(source + 6U), (uint16_t)(0x5800U + normalized * 0x100U));
    write_be16(rom_pointer(FUEL_STOCK + 8U), 0x8001U);
    write_be16(rom_pointer(FUEL_STOCK + 10U), 0x7fffU);
    write_be16(
        rom_pointer(pair == 2 ? FUEL_STOCK + 8U : source + activation_offsets[pair]),
        activation);
    write_be16(
        rom_pointer(pair == 2 ? FUEL_STOCK + 10U : source + release_offsets[pair]),
        release);

    seed_ram(empty_state);
    if (invoke_r4(LIMITER_COMMIT, requested) != normalized)
        return fail_value("fuel_cut_consumer", "selected_bank", requested, normalized);
    read_bytes(shadows, ram_pointer(RAM_SENTINEL_BASE), sizeof(shadows));
    /* Contradictory old-table values make each redirected read observable. */
    write_be16(rom_pointer(FUEL_STOCK), 0xffffU);
    write_be16(rom_pointer(FUEL_STOCK + 2U), 0xffffU);
    write_be16(rom_pointer(FUEL_STOCK + 4U), 0);
    write_be16(rom_pointer(FUEL_STOCK + 6U), 0);
    write_be16(rom_pointer(FUEL_STOCK + 8U), 0xffffU);
    write_be16(rom_pointer(FUEL_STOCK + 10U), 0);

    fill_bytes(ram_pointer(FUEL_CUT_GUARD), FUEL_CUT_GUARD_SIZE, 0xa5);
    ram_pointer(0xffff2468U)[0] = pair == 1 ? 0x10U : 0;
    ram_pointer(0xffff2499U)[0] = missing_gate == 1 ? 0 : 0x02U;
    ram_pointer(0xffff2494U)[0] = missing_gate == 2 ? 0 : 0x20U;
    ram_pointer(0xffff244fU)[0] = missing_gate == 3 ? 0 : 0x04U;
    rom_pointer(0x8b38U)[0] = (uint8_t)(saved_configuration & 0x7fU)
        | ((pair == 2 || missing_gate) ? 0x80U : 0);
    rom_pointer(0x8c69U)[0] = delay;
    ram_pointer(FUEL_CUT_STATE)[0] = initial;
    ram_pointer(FUEL_CUT_TIMER)[0] = timer;
    write_be16(ram_pointer(FUEL_CUT_RPM), rpm);
    read_bytes(expected, ram_pointer(FUEL_CUT_GUARD), sizeof(expected));
    if (initial & 0x04U) {
        if (rpm < release)
            expected_state &= 0xf9U;
    } else if (rpm < activation) {
        expected_state &= 0xfdU;
    } else {
        if (!(initial & 0x02U)) {
            expected_timer = delay;
            expected_state |= 0x02U;
        }
        if (!expected_timer)
            expected_state |= 0x04U;
    }
    expected[FUEL_CUT_STATE - FUEL_CUT_GUARD] = expected_state;
    expected[FUEL_CUT_TIMER - FUEL_CUT_GUARD] = expected_timer;
    __asm__ volatile (
        "stc gbr,%0\n\tmov r15,%1\n\tldc %2,gbr"
        : "=&r" (saved_gbr), "=&r" (before_sp) : "r" (sentinel_gbr) : "memory");
    returned = invoke_r0(FUEL_CUT_CONSUMER);
    __asm__ volatile (
        "stc gbr,%0\n\tmov r15,%1\n\tldc %2,gbr"
        : "=&r" (after_gbr), "=&r" (after_sp) : "r" (saved_gbr) : "memory");
    write_bytes(rom_pointer(FUEL_STOCK), saved_stock, sizeof(saved_stock));
    write_bytes(rom_pointer(source), saved_slot, sizeof(saved_slot));
    rom_pointer(0x8b38U)[0] = saved_configuration;
    rom_pointer(0x8c69U)[0] = saved_delay;
    ++*cases;
    if (after_gbr != sentinel_gbr)
        return fail_value("fuel_cut_consumer", "gbr", after_gbr, sentinel_gbr);
    if (after_sp != before_sp)
        return fail_value("fuel_cut_consumer", "stack", after_sp, before_sp);
    if (returned != ((expected_state & 4U) != 0))
        return fail_value("fuel_cut_consumer", "return", returned, (expected_state & 4U) != 0);
    if (read_be16(ram_pointer(FUEL_CUT_RPM)) != rpm)
        return fail_value("fuel_cut_consumer", "rpm_guard", read_be16(ram_pointer(FUEL_CUT_RPM)), rpm);
    return fail_bytes("fuel_cut_consumer", "state_and_guards",
            ram_pointer(FUEL_CUT_GUARD), expected, sizeof(expected))
        && fail_bytes("fuel_cut_consumer", "shadow_read_only",
            ram_pointer(RAM_SENTINEL_BASE), shadows, sizeof(shadows));
}

static int run_fuel_cut_consumer_cases(void)
{
    static const uint8_t requested[] = {0, 1, 2, 3, 4, 5, 0xff};
    static const uint16_t wide[] = {0, 0x7fffU, 0x8000U, 0xffffU};
    size_t bank, cases = 0;
    unsigned pair, boundary, pending, timer, delay, gate, threshold, sample;

    for (bank = 0; bank < ARRAY_SIZE(requested); ++bank) {
        for (pair = 0; pair < 3; ++pair) {
            uint16_t activation = (uint16_t)(0x8001U + bank * 13U + pair * 7U);
            uint16_t release = (uint16_t)(0x7fffU - bank * 17U - pair * 5U);
            for (boundary = 0; boundary < 3; ++boundary) {
                for (pending = 0; pending < 2; ++pending)
                    for (timer = 0; timer < 2; ++timer)
                        for (delay = 0; delay < 2; ++delay)
                            if (!run_fuel_cut_consumer_case(
                                    requested[bank], pair, activation, release,
                                    (uint16_t)(activation - 1U + boundary),
                                    (uint8_t)(0xa1U | pending * 2U),
                                    (uint8_t)(timer * 0x80U), (uint8_t)(delay * 0x80U),
                                    0, &cases))
                                return 0;
                if (!run_fuel_cut_consumer_case(
                        requested[bank], pair, activation, release,
                        (uint16_t)(release - 1U + boundary), 0xe7U, 0x55U, 0x80U,
                        0, &cases))
                    return 0;
            }
        }
    }
    /* Each short-circuit gate must fall back to each normal pair. */
    for (gate = 1; gate <= 3; ++gate)
        for (pair = 0; pair < 2; ++pair)
            if (!run_fuel_cut_consumer_case(
                    4, pair, 0x8000U, 0x7fffU, 0x8000U,
                    0xa1U, 0, 0, gate, &cases))
                return 0;
    for (pair = 0; pair < 3; ++pair)
        for (threshold = 0; threshold < ARRAY_SIZE(wide); ++threshold)
            for (sample = 0; sample < ARRAY_SIZE(wide); ++sample)
                for (pending = 0; pending < 2; ++pending)
                    if (!run_fuel_cut_consumer_case(
                            3, pair, wide[threshold], wide[threshold], wide[sample],
                            pending ? 0xe7U : 0xa1U, 0, 0, 0, &cases))
                        return 0;
    printf("VQ_SH_ELF_MAP_SWITCHING_FUEL_CUT status=PASS cases=%lu entries=1\n",
        (unsigned long)cases);
    return 1;
}
#endif

#ifdef VERIFY_7MFK_THROTTLE_CLUSTER
/* R0 observes the stopped prefix, not a return value of the stock void function.
   The enabled body is outside the fixture's qualified instruction windows. */
static int run_throttle_cluster_cases(void)
{
    static const uint8_t empty_state[8] = {0};
    static const uint8_t requested[] = {0, 1, 2, 3, 4, 5, 0xff};
    static const uint16_t words[] = {0, 1, 0x074cU, 0x7fffU, 0x8000U, 0xfffeU, 0xffffU};
    uint8_t saved[5][2], shadows[RAM_SENTINEL_SIZE], expected[8];
    size_t bank, sample, index, cases = 0;
    for (index = 0; index < ARRAY_SIZE(throttle_slots); ++index)
        read_bytes(saved[index], rom_pointer(throttle_slots[index]), 2);
    for (bank = 0; bank < ARRAY_SIZE(requested); ++bank) {
        unsigned normalized = requested[bank] < 5 ? requested[bank] : 0;
        for (sample = 0; sample < ARRAY_SIZE(words); ++sample) {
            uint16_t selected = words[sample];
            uint32_t observed, before_sp, after_sp;
            uint32_t probe = selected == 0xffffU ? 0x074cU : (uint32_t)(int32_t)(int16_t)selected;
            for (index = 0; index < ARRAY_SIZE(throttle_slots); ++index)
                write_be16(rom_pointer(throttle_slots[index]), (uint16_t)(0x2100U + index * 0x101U));
            write_be16(rom_pointer(throttle_slots[normalized]), selected);
            seed_ram(empty_state);
            write_be16(ram_pointer(THROTTLE_SHADOW + 8U), selected == 0xffffU ? 0 : 0xffffU);
            if (invoke_r4(LIMITER_COMMIT, requested[bank]) != normalized)
                return fail_value("throttle_cluster", "selected_bank", requested[bank], normalized);
            read_bytes(shadows, ram_pointer(RAM_SENTINEL_BASE), sizeof(shadows));
            /* The old ROM source contradicts the committed shadow for every case. */
            write_be16(rom_pointer(THROTTLE_STOCK + 8U), selected == 0xffffU ? 0 : 0xffffU);
            fill_bytes(ram_pointer(0xffff19d4U), sizeof(expected), 0xa5);
            read_bytes(expected, ram_pointer(0xffff19d4U), sizeof(expected));
            if (selected == 0xffffU) {
                expected[4] = 0x7f;
                expected[5] = 0xff;
            }
            __asm__ volatile ("mov r15,%0" : "=r" (before_sp) : : "memory");
            observed = invoke_r0(0x0007584eU);
            __asm__ volatile ("mov r15,%0" : "=r" (after_sp) : : "memory");
            ++cases;
            if (after_sp != before_sp)
                return fail_value("throttle_cluster", "stack", after_sp, before_sp);
            if (observed != probe)
                return fail_value("throttle_cluster", "prefix_r0_probe", observed, probe);
            if (!fail_bytes("throttle_cluster", "request_and_guards", ram_pointer(0xffff19d4U), expected, sizeof(expected))
                || !fail_bytes("throttle_cluster", "shadow_read_only", ram_pointer(RAM_SENTINEL_BASE), shadows, sizeof(shadows)))
                return 0;
        }
    }
    for (index = 0; index < ARRAY_SIZE(throttle_slots); ++index)
        write_bytes(rom_pointer(throttle_slots[index]), saved[index], 2);
    printf("VQ_SH_ELF_MAP_SWITCHING_THROTTLE_CLUSTER status=PASS cases=%lu entries=1\n", (unsigned long)cases);
    return 1;
}
#endif

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

static int verify_optional_selector_shadows(
    const char *name, int active, int expected_write)
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

    if (expected_write == 0 && !untouched)
        return fail_value(name, "unexpected_limiter_write", 1, 0);
    if (expected_write == 1 && untouched)
        return fail_value(name, "missing_limiter_write", 0, 1);
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
        int expected_write = -1;
        uint32_t returned;

        seed_ram(test->initial);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        ram_pointer(CURRENT_CODE)[0] = test->current;
        ram_pointer(CURRENT_CODE)[1] = test->previous;
        ram_pointer(ASCD_STATUS)[0] = test->ascd;
        ram_pointer(DIAGNOSTIC_STATUS)[0] = 0x25;
        returned = invoke_r4(SELECTOR_HOST, 0);
        if (!fail_bytes(
                test->name, "selector_state", ram_pointer(SELECTOR_STATE),
                test->expected, sizeof(test->expected)))
            return 0;
        active = test->expected[0];
#ifdef VERIFY_SELECTOR_FEEDBACK_GUARDS
        expected_write = test->expected_limiter_write;
        if (returned != (uint32_t)active)
            return fail_value(test->name, "selector_return", returned, (uint32_t)active);
#else
        (void)returned;
#endif
        expected_diagnostic =
            (uint8_t)(0x25U & 0x7fU) | (active == 0 ? 0U : 0x80U);
        if (ram_pointer(DIAGNOSTIC_STATUS)[0] != expected_diagnostic)
            return fail_value(
                test->name, "diagnostic",
                ram_pointer(DIAGNOSTIC_STATUS)[0], expected_diagnostic);
        if (!verify_ram_guards(test->name))
            return 0;
        if (!verify_optional_selector_shadows(test->name, active, expected_write))
            return 0;
    }
#ifdef VERIFY_CRUISE_FREE
    {
        /* Also cover selector_host when MSCF disables ASCD (cruise-less ECU):
           ASCD_STATUS=0x80 is ignored, ASCD transient bytes are cleared, and
           selector_host hands off mode=0 to cruise_free_step. */
        uint8_t saved_cfg[32];
        uint8_t initial[8] = {1, 1, 2, 9, 0, 0, 0, 0};
        uint8_t expected[8] = {1, 0, 0, 0, 0, 0, 0, 0};
        uint32_t returned;

        read_bytes(saved_cfg, rom_pointer(CF_CONFIG_ADDR), sizeof(saved_cfg));
        rom_pointer(CF_CONFIG_ADDR)[5] = 0x02U; /* cruise_free only, ASCD off */
        seed_ram(initial);
        fill_bytes(ram_pointer(CF_RAM_BASE), CF_RAM_SIZE, 0);
        ram_pointer(ASCD_STATUS)[0] = ASCD_MAIN;
        ram_pointer(DIAGNOSTIC_STATUS)[0] = 0x25U;
        returned = invoke_r4(SELECTOR_HOST, 0);
        write_bytes(rom_pointer(CF_CONFIG_ADDR), saved_cfg, sizeof(saved_cfg));
        if (returned != 1U)
            return fail_value("selector_ascd_disabled", "return", returned, 1U);
        if (!fail_bytes(
                "selector_ascd_disabled", "selector_state",
                ram_pointer(SELECTOR_STATE), expected, sizeof(expected)))
            return 0;
        if (ram_pointer(DIAGNOSTIC_STATUS)[0] != (0x25U | 0x80U))
            return fail_value(
                "selector_ascd_disabled", "diagnostic",
                ram_pointer(DIAGNOSTIC_STATUS)[0], 0x25U | 0x80U);
    }
#endif
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

            uint32_t returned = invoke_r4(FEEDBACK_WRAPPER, 0);
#ifdef VERIFY_SELECTOR_FEEDBACK_GUARDS
#ifdef TARGET_DUAL_BANK_MMIO
            uint32_t expected_return = test->expected_status_pointer
                ? (PAYLOAD + 5U) : 0;
#else
            uint32_t expected_return = test->expected_status_pointer
                ? (uint32_t)(uintptr_t)ram_pointer(PAYLOAD + 5U) : 0;
#endif
            if (returned != expected_return)
                return fail_value(test->name, "feedback_return", returned, expected_return);
#else
            (void)returned;
#endif
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

#ifdef VERIFY_CRUISE_FREE
#ifndef FEEDBACK_ENGINE
#define FEEDBACK_ENGINE 0x000d3760U
#endif

static void cf_write_rpm_coarse(uint16_t value)
{
#ifdef CF_RPM_COARSE_U16
    write_be16(ram_pointer(CF_RPM_COARSE), value);
#else
    ram_pointer(CF_RPM_COARSE)[0] = (uint8_t)value;
#endif
}

static void cf_seed_valid_inputs(void)
{
    volatile uint8_t *cf = ram_pointer(CF_RAM_BASE);

    write_be16(ram_pointer(CF_RPM_FINE), 0U);
    cf_write_rpm_coarse(0U);
    ram_pointer(CF_PORT_STATE)[0] = CF_PORT_READY_MASK;
    ram_pointer(CF_HCAN1_STATE)[0] = CF_HCAN1_INIT_MASK;
    ram_pointer(CF_BRAKE_BYTE)[0] = CF_BRAKE_MASK;
    write_be16(ram_pointer(CF_APP1_ADDR), 151U);
    write_be16(ram_pointer(CF_APP2_ADDR), 151U);
    cf[0] = 0x03U; /* observed | stationary_valid */
    cf[1] = 0U;    /* age = 0 */
    write_be16(cf + 2U, 0U);
}

static int cf_run_stationary_cases(size_t *cases)
{
    volatile uint8_t *cf = ram_pointer(CF_RAM_BASE);

    /* Startup init zeros extension RAM and sets age=0xFF, last_raw=0xFFFF. */
    fill_bytes(cf, CF_RAM_SIZE, 0x55U);
    invoke_r0(CF_STARTUP_INIT);
    if (cf[0] != 0U || cf[1] != 0xffU || read_be16(cf + 2U) != 0xffffU
            || cf[4] != 0U || cf[8] != 0U || cf[9] != 0U)
        return fail_value("cf_init", "ram", cf[0], 0U);
    ++*cases;

    /* Unobserved with gates on, no new frame -> saturates age=0xFF, unobserved. */
    ram_pointer(CF_PORT_STATE)[0] = CF_PORT_READY_MASK;
    ram_pointer(CF_HCAN1_STATE)[0] = CF_HCAN1_INIT_MASK;
    ram_pointer(CF_RX_STATE)[0] = 0x00U;
    invoke_r0(CF_STATIONARY_WRAPPER);
    if (cf[0] != 0U || cf[1] != 0xffU)
        return fail_value("cf_stat_unobs", "flags", cf[0], 0U);
    ++*cases;

    /* Gate 1 off -> resets to unobserved. */
    cf[0] = 0x03U;
    cf[1] = 0U;
    write_be16(cf + 2U, 0U);
    ram_pointer(CF_PORT_STATE)[0] = 0x00U;
    invoke_r0(CF_STATIONARY_WRAPPER);
    if (cf[0] != 0U || cf[1] != 0xffU || read_be16(cf + 2U) != 0xffffU)
        return fail_value("cf_stat_port_off", "flags", cf[0], 0U);
    ++*cases;

    /* Gate 2 off -> resets to unobserved. */
    ram_pointer(CF_PORT_STATE)[0] = CF_PORT_READY_MASK;
    ram_pointer(CF_HCAN1_STATE)[0] = 0x00U;
    invoke_r0(CF_STATIONARY_WRAPPER);
    if (cf[0] != 0U || cf[1] != 0xffU || read_be16(cf + 2U) != 0xffffU)
        return fail_value("cf_stat_hcan1_off", "flags", cf[0], 0U);
    ++*cases;

    /* Fresh zero frame -> observed & stationary_valid, age=0, raw=0. */
    ram_pointer(CF_HCAN1_STATE)[0] = CF_HCAN1_INIT_MASK;
    ram_pointer(CF_RX_STATE)[0] = 0x08U;
    write_be16(ram_pointer(CF_RX_RAW_HI), 0x0000U);
    invoke_r0(CF_STATIONARY_WRAPPER);
    if (cf[0] != 0x03U || cf[1] != 0U || read_be16(cf + 2U) != 0U)
        return fail_value("cf_stat_zero", "flags", cf[0], 0x03U);
    ++*cases;

    /* No new frame for age 1..3 remains valid; age 4 expires (> limit 3). */
    ram_pointer(CF_RX_STATE)[0] = 0x00U;
    for (unsigned tick = 1U; tick <= 4U; ++tick) {
        invoke_r0(CF_STATIONARY_WRAPPER);
        uint8_t want = tick <= 3U ? 0x03U : 0x01U;
        if (cf[0] != want || cf[1] != tick)
            return fail_value("cf_stat_age", "flags", cf[0], want);
        ++*cases;
    }

    /* Sentinel 0xFFFF new frame -> observed but NOT stationary. */
    ram_pointer(CF_RX_STATE)[0] = 0x08U;
    write_be16(ram_pointer(CF_RX_RAW_HI), 0xffffU);
    invoke_r0(CF_STATIONARY_WRAPPER);
    if (cf[0] != 0x01U || cf[1] != 0U || read_be16(cf + 2U) != 0xffffU)
        return fail_value("cf_stat_sentinel", "flags", cf[0], 0x01U);
    ++*cases;

    /* No new frame while raw != 0 -> stays observed, not valid. */
    ram_pointer(CF_RX_STATE)[0] = 0x00U;
    invoke_r0(CF_STATIONARY_WRAPPER);
    if (cf[0] != 0x01U || cf[1] != 1U)
        return fail_value("cf_stat_nonzero_hold", "flags", cf[0], 0x01U);
    ++*cases;

    /* Recovery with fresh zero frame. */
    ram_pointer(CF_RX_STATE)[0] = 0x08U;
    write_be16(ram_pointer(CF_RX_RAW_HI), 0x0000U);
    invoke_r0(CF_STATIONARY_WRAPPER);
    if (cf[0] != 0x03U || cf[1] != 0U || read_be16(cf + 2U) != 0U)
        return fail_value("cf_stat_recover", "flags", cf[0], 0x03U);
    ++*cases;

    /* Invalid MSCF+7 (0x00 and 0xFF) clears cached observation and tach state
       even when a fresh zero-speed frame arrives with both gates high. */
    {
        volatile uint8_t *cfg = rom_pointer(CF_CONFIG_ADDR);
        uint8_t saved_age = cfg[7];
        static const uint8_t bad_ages[] = {0x00U, 0xffU};
        static const uint8_t good_ages[] = {0x01U, 0x80U, 0xfeU};

        for (size_t i = 0; i < ARRAY_SIZE(bad_ages); ++i) {
            cf[0] = 0x03U;
            cf[1] = 0U;
            write_be16(cf + 2U, 0U);
            cf[4] = 1U;
            cf[5] = 1U;
            cf[6] = 9U;
            cf[7] = 2U;
            cfg[7] = bad_ages[i];
            ram_pointer(CF_RX_STATE)[0] = 0x08U;
            write_be16(ram_pointer(CF_RX_RAW_HI), 0x0000U);
            invoke_r0(CF_STATIONARY_WRAPPER);
            if (cf[0] != 0U || cf[1] != 0xffU || read_be16(cf + 2U) != 0xffffU
                    || cf[4] != 0U || cf[5] != 0U || cf[6] != 0U || cf[7] != 0U) {
                cfg[7] = saved_age;
                return fail_value("cf_stat_bad_age", "flags", cf[0], 0U);
            }
            ++*cases;
        }
        /* Valid unsigned age limits (0x01, 0x80, 0xFE): valid at age==limit,
           expired at age==limit+1. */
        for (size_t i = 0; i < ARRAY_SIZE(good_ages); ++i) {
            uint8_t lim = good_ages[i];
            cfg[7] = lim;
            cf[0] = 0x03U;
            cf[1] = (uint8_t)(lim - 1U);
            write_be16(cf + 2U, 0U);
            ram_pointer(CF_RX_STATE)[0] = 0x00U;
            invoke_r0(CF_STATIONARY_WRAPPER);
            if (cf[0] != 0x03U || cf[1] != lim) {
                cfg[7] = saved_age;
                return fail_value("cf_stat_age_eq", "flags", cf[0], 0x03U);
            }
            invoke_r0(CF_STATIONARY_WRAPPER);
            if (cf[0] != 0x01U || cf[1] != (uint8_t)(lim + 1U)) {
                cfg[7] = saved_age;
                return fail_value("cf_stat_age_gt", "flags", cf[0], 0x01U);
            }
            ++*cases;
        }
        cfg[7] = saved_age;
    }
    return 1;
}

static int cf_run_config_and_step_cases(size_t *cases)
{
    static const uint8_t empty_state[8] = {0};
    volatile uint8_t *cf = ram_pointer(CF_RAM_BASE);
    volatile uint8_t *cfg = rom_pointer(CF_CONFIG_ADDR);
    uint8_t saved_cfg[32];
    uint32_t ret;

    read_bytes(saved_cfg, cfg, sizeof(saved_cfg));

    /* Cover cruise_free_ascd_enabled: enabled, disabled, and invalid config. */
    seed_ram(empty_state);
    ram_pointer(SELECTOR_STATE)[1] = 2U;
    ram_pointer(SELECTOR_STATE)[2] = 3U;
    ram_pointer(SELECTOR_STATE)[3] = 4U;
    ret = invoke_r0(CF_ASCD_ENABLED_ENTRY);
    if (ret != 1U || ram_pointer(SELECTOR_STATE)[1] != 2U)
        return fail_value("cf_ascd_en", "ret", ret, 1U);
    ++*cases;

    cfg[5] = 0x02U; /* ASCD disabled */
    ret = invoke_r0(CF_ASCD_ENABLED_ENTRY);
    if (ret != 0U || ram_pointer(SELECTOR_STATE)[1] != 0U
            || ram_pointer(SELECTOR_STATE)[2] != 0U
            || ram_pointer(SELECTOR_STATE)[3] != 0U)
        return fail_value("cf_ascd_dis", "ret", ret, 0U);
    ++*cases;
    write_bytes(cfg, saved_cfg, sizeof(saved_cfg));

    /* Cover every branch of cf_validate_cfg_local via cruise_free_ascd_enabled,
       verifying each rejection wipes CF[0..7] fail-closed. */
    for (unsigned kind = 0U; kind < 14U; ++kind) {
        write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
        cf_seed_valid_inputs();
        cf[4] = 1U;
        cf[5] = 1U;
        cf[6] = 8U;
        cf[7] = 3U;
        if (kind == 0U)
            cfg[0] = 0x00U; /* bad magic */
        else if (kind == 1U)
            cfg[4] = 0x02U; /* bad version */
        else if (kind == 2U)
            cfg[0x1f] = 0x00U; /* bad sentinel */
        else if (kind == 3U)
            cfg[0x1b] = 0x01U; /* nonzero reserved2 */
        else if (kind == 4U)
            cfg[0x17] = 0x01U; /* nonzero reserved */
        else if (kind == 5U)
            cfg[5] = 0x08U; /* unsupported flags bit */
        else if (kind == 6U)
            cfg[6] = 0x08U; /* unsupported feedback_mode bit */
        else if (kind == 7U)
            cfg[7] = 0x00U; /* age_limit == 0 */
        else if (kind == 8U)
            cfg[7] = 0xffU; /* age_limit == 0xFF */
        else if (kind == 9U)
            cfg[0x15] = 0x00U; /* debounce == 0 */
        else if (kind == 10U)
            write_be16(cfg + 0x10U, 59U); /* release_max < app_min */
        else if (kind == 11U)
            write_be16(cfg + 0x12U, 260U); /* press_min == release_max */
        else if (kind == 12U)
            write_be16(cfg + 0x0aU, 699U); /* app1_max < press_min */
        else
            write_be16(cfg + 0x0cU, 699U); /* app2_max < press_min */
        ret = invoke_r0(CF_ASCD_ENABLED_ENTRY);
        if (ret != 0U || cf[0] != 0U || cf[1] != 0xffU
                || read_be16(cf + 2U) != 0xffffU
                || cf[4] != 0U || cf[5] != 0U || cf[6] != 0U || cf[7] != 0U)
            return fail_value("cf_cfg_bad", "ret", ret, 0U);
        ++*cases;
    }
    write_bytes(cfg, saved_cfg, sizeof(saved_cfg));

    /* Mode 1 (arbitration blocked) -> reason 6, clears cf transient. */
    seed_ram(empty_state);
    cf_seed_valid_inputs();
    cf[4] = 1U;
    cf[5] = 1U;
    invoke_r4(CF_STEP_ENTRY, 1U);
    if (cf[8] != 6U || cf[4] != 0U || cf[5] != 0U)
        return fail_value("cf_mode1", "reason", cf[8], 6U);
    ++*cases;

    /* Mode 0 reason 1: corrupt config and cruise_free_enabled=0. */
    cfg[0] = 0x00U;
    invoke_r4(CF_STEP_ENTRY, 0U);
    if (cf[8] != 1U)
        return fail_value("cf_r1_badcfg", "reason", cf[8], 1U);
    write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
    cfg[5] = 0x01U; /* cruise_free disabled */
    invoke_r4(CF_STEP_ENTRY, 0U);
    if (cf[8] != 1U)
        return fail_value("cf_r1_dis", "reason", cf[8], 1U);
    write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
    ++*cases;

    /* Mode 0 reason 2: rpm_fine != 0, then rpm_coarse != 0. */
    cf_seed_valid_inputs();
    write_be16(ram_pointer(CF_RPM_FINE), 1U);
    invoke_r4(CF_STEP_ENTRY, 0U);
    if (cf[8] != 2U)
        return fail_value("cf_r2_fine", "reason", cf[8], 2U);
    write_be16(ram_pointer(CF_RPM_FINE), 0U);
    cf_write_rpm_coarse(0x0001U);
    invoke_r4(CF_STEP_ENTRY, 0U);
    if (cf[8] != 2U)
        return fail_value("cf_r2_coarse", "reason", cf[8], 2U);
#ifdef CF_RPM_COARSE_U16
    cf_write_rpm_coarse(0x0100U);
    invoke_r4(CF_STEP_ENTRY, 0U);
    if (cf[8] != 2U)
        return fail_value("cf_r2_coarse_hi", "reason", cf[8], 2U);
#endif
    ++*cases;

    /* Mode 0 reason 3: port off, hcan1 off, flags!=3, raw!=0, age>limit. */
    for (unsigned sub = 0U; sub < 5U; ++sub) {
        cf_seed_valid_inputs();
        if (sub == 0U)
            ram_pointer(CF_PORT_STATE)[0] = 0U;
        else if (sub == 1U)
            ram_pointer(CF_HCAN1_STATE)[0] = 0U;
        else if (sub == 2U)
            cf[0] = 0x01U;
        else if (sub == 3U)
            write_be16(cf + 2U, 1U);
        else
            cf[1] = 4U;
        invoke_r4(CF_STEP_ENTRY, 0U);
        if (cf[8] != 3U)
            return fail_value("cf_r3_stat", "reason", cf[8], 3U);
        ++*cases;
    }

    /* Mode 0 reason 4: brake released. */
    cf_seed_valid_inputs();
    ram_pointer(CF_BRAKE_BYTE)[0] = 0U;
    invoke_r4(CF_STEP_ENTRY, 0U);
    if (cf[8] != 4U)
        return fail_value("cf_r4_brake", "reason", cf[8], 4U);
    ++*cases;

    /* Mode 0 reason 5: all 6 dual-APP implausibility branches. */
    {
        static const uint16_t bad_apps[][2] = {
            {59U, 151U},   /* app1 < min */
            {151U, 59U},   /* app2 < min */
            {965U, 965U},  /* app1 > app1_max */
            {960U, 1001U}, /* app2 > app2_max */
            {400U, 300U},  /* app1 - app2 > diff_max */
            {300U, 400U},  /* app2 - app1 > diff_max */
        };
        for (size_t i = 0; i < ARRAY_SIZE(bad_apps); ++i) {
            cf_seed_valid_inputs();
            write_be16(ram_pointer(CF_APP1_ADDR), bad_apps[i][0]);
            write_be16(ram_pointer(CF_APP2_ADDR), bad_apps[i][1]);
            invoke_r4(CF_STEP_ENTRY, 0U);
            if (cf[8] != 5U)
                return fail_value("cf_r5_app", "reason", cf[8], 5U);
            ++*cases;
        }
    }

    /* Corrupt cf_phase resets to 0. */
    cf_seed_valid_inputs();
    cf[4] = 7U;
    cf[5] = 3U;
    invoke_r4(CF_STEP_ENTRY, 0U);
    if (cf[4] != 0U || cf[5] != 0U || cf[8] != 0U)
        return fail_value("cf_corrupt_phase", "phase", cf[4], 0U);
    ++*cases;

    /* Pedal deadband classification branches (app1>rel, app2>rel, app1>=press&app2<press). */
    cf_seed_valid_inputs();
    cf[4] = 0U;
    cf[5] = 1U;
    write_be16(ram_pointer(CF_APP1_ADDR), 300U);
    write_be16(ram_pointer(CF_APP2_ADDR), 300U);
    invoke_r4(CF_STEP_ENTRY, 0U);
    if (cf[4] != 0U || cf[5] != 0U)
        return fail_value("cf_deadband1", "debounce", cf[5], 0U);
    write_be16(ram_pointer(CF_APP1_ADDR), 250U);
    write_be16(ram_pointer(CF_APP2_ADDR), 280U); /* app1<=rel, app2>rel */
    invoke_r4(CF_STEP_ENTRY, 0U);
    if (cf[4] != 0U || cf[5] != 0U)
        return fail_value("cf_deadband2", "debounce", cf[5], 0U);
    write_be16(ram_pointer(CF_APP1_ADDR), 710U);
    write_be16(ram_pointer(CF_APP2_ADDR), 680U); /* app1>=press, app2<press */
    invoke_r4(CF_STEP_ENTRY, 0U);
    if (cf[4] != 0U || cf[5] != 0U)
        return fail_value("cf_deadband3", "debounce", cf[5], 0U);
    ++*cases;

    /* Pedal already pressed in IDLE_WAIT_RELEASE -> must NOT arm or switch. */
    cf_seed_valid_inputs();
    write_be16(ram_pointer(CF_APP1_ADDR), 900U);
    write_be16(ram_pointer(CF_APP2_ADDR), 900U);
    invoke_r4(CF_STEP_ENTRY, 0U);
    if (cf[4] != 0U || ram_pointer(SELECTOR_STATE)[0] != 0U)
        return fail_value("cf_wait_release", "phase", cf[4], 0U);
    ++*cases;

    /* Full 5-tap cyclic sequence: 0 -> 1 -> 2 -> 3 -> 4 -> 0 with tach armed on tap 1. */
    seed_ram(empty_state);
    cf_seed_valid_inputs();
    cf[4] = 0U;
    cf[5] = 0U;
    cfg[5] = 0x07U; /* ascd | cruise_free | tach_allowed */
    cfg[6] = 0x05U; /* cruise | tach */
    for (unsigned step = 0U; step < 5U; ++step) {
        unsigned want_slot = (step + 1U) % 5U;

        /* Release 2 ticks -> ARMED_RELEASED (1). */
        write_be16(ram_pointer(CF_APP1_ADDR), 151U);
        write_be16(ram_pointer(CF_APP2_ADDR), 151U);
        invoke_r4(CF_STEP_ENTRY, 0U);
        if (cf[4] != (step == 0U ? 0U : 2U) || cf[5] != 1U)
            return fail_value("cf_rel1", "debounce", cf[5], 1U);
        invoke_r4(CF_STEP_ENTRY, 0U);
        if (cf[4] != 1U || cf[5] != 0U)
            return fail_value("cf_rel2", "phase", cf[4], 1U);

        /* While armed, one released tick clears debounce. */
        invoke_r4(CF_STEP_ENTRY, 0U);
        if (cf[4] != 1U || cf[5] != 0U)
            return fail_value("cf_arm_rel", "phase", cf[4], 1U);

        /* Press 2 ticks -> commit cyclic next slot, PRESSED_LATCHED (2). */
        write_be16(ram_pointer(CF_APP1_ADDR), 850U);
        write_be16(ram_pointer(CF_APP2_ADDR), 850U);
        invoke_r4(CF_STEP_ENTRY, 0U);
        if (cf[4] != 1U || cf[5] != 1U)
            return fail_value("cf_prs1", "debounce", cf[5], 1U);
        invoke_r4(CF_STEP_ENTRY, 0U);
        if (ram_pointer(SELECTOR_STATE)[0] != want_slot
                || ram_pointer(SELECTOR_STATE)[4] != want_slot + 1U
                || ram_pointer(SELECTOR_STATE)[5] != 1U
                || cf[4] != 2U || cf[5] != 0U || cf[9] != 2U
                || cf[6] != 40U || cf[7] != want_slot + 1U)
            return fail_value("cf_commit", "active", ram_pointer(SELECTOR_STATE)[0], want_slot);
        ++*cases;
    }

    /* Mode 2 (ASCD commit handoff) branches: running fine, running coarse,
       not stationary, tach disabled flags/mode/hold=0, invalid config, and armed. */
    write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
    cfg[5] = 0x07U;
    cfg[6] = 0x05U;
    ram_pointer(SELECTOR_STATE)[0] = 2U; /* map 3 */

    cf_seed_valid_inputs();
    cf[6] = 0U;
    cf[7] = 0U;
    write_be16(ram_pointer(CF_RPM_FINE), 100U);
    invoke_r4(CF_STEP_ENTRY, 2U);
    if (cf[9] != 1U || cf[6] != 0U)
        return fail_value("cf_m2_rpm_fine", "tach", cf[6], 0U);

    cf_seed_valid_inputs();
    cf_write_rpm_coarse(10U);
    invoke_r4(CF_STEP_ENTRY, 2U);
    if (cf[6] != 0U)
        return fail_value("cf_m2_rpm_coarse", "tach", cf[6], 0U);

    cf_seed_valid_inputs();
    cf[0] = 0x01U; /* not stationary */
    invoke_r4(CF_STEP_ENTRY, 2U);
    if (cf[6] != 0U)
        return fail_value("cf_m2_not_stat", "tach", cf[6], 0U);

    /* Invalid config at cruise_free_step mode 2 -> reason 1 and full CF[0..7] wipe. */
    cf_seed_valid_inputs();
    cf[6] = 5U;
    cf[7] = 2U;
    cfg[7] = 0xffU;
    invoke_r4(CF_STEP_ENTRY, 2U);
    if (cf[6] != 0U || cf[7] != 0U || cf[0] != 0U || cf[8] != 1U)
        return fail_value("cf_m2_badcfg", "tach", cf[6], 0U);
    write_bytes(cfg, saved_cfg, sizeof(saved_cfg));

    /* Live gate drop on mode 2 prevents tach arming even with cf[0]==3. */
    cf_seed_valid_inputs();
    cfg[5] = 0x07U;
    cfg[6] = 0x05U;
    ram_pointer(CF_PORT_STATE)[0] = 0U;
    invoke_r4(CF_STEP_ENTRY, 2U);
    if (cf[6] != 0U)
        return fail_value("cf_m2_port_off", "tach", cf[6], 0U);
    cf_seed_valid_inputs();
    ram_pointer(CF_HCAN1_STATE)[0] = 0U;
    invoke_r4(CF_STEP_ENTRY, 2U);
    if (cf[6] != 0U)
        return fail_value("cf_m2_hcan_off", "tach", cf[6], 0U);
    cf_seed_valid_inputs();
    cf[1] = 4U; /* age > default limit 3 */
    invoke_r4(CF_STEP_ENTRY, 2U);
    if (cf[6] != 0U)
        return fail_value("cf_m2_stale_age", "tach", cf[6], 0U);

    /* flags.2 == 0, feedback_mode.2 == 0, tach_hold_frames == 0. */
    write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
    cf_seed_valid_inputs();
    cfg[5] = 0x03U; /* tach_allowed = 0 */
    cfg[6] = 0x05U;
    invoke_r4(CF_STEP_ENTRY, 2U);
    if (cf[6] != 0U)
        return fail_value("cf_m2_noflag", "tach", cf[6], 0U);

    cfg[5] = 0x07U;
    cfg[6] = 0x01U; /* feedback_mode tach bit = 0 */
    invoke_r4(CF_STEP_ENTRY, 2U);
    if (cf[6] != 0U)
        return fail_value("cf_m2_nomode", "tach", cf[6], 0U);

    cfg[6] = 0x05U;
    cfg[0x14] = 0U; /* tach_hold_frames = 0 */
    invoke_r4(CF_STEP_ENTRY, 2U);
    if (cf[6] != 0U)
        return fail_value("cf_m2_nohold", "tach", cf[6], 0U);

    /* Allowed + stationary + stopped -> arms tach_ticks=40, tach_slot=3. */
    cfg[0x14] = 40U;
    invoke_r4(CF_STEP_ENTRY, 2U);
    if (cf[6] != 40U || cf[7] != 3U)
        return fail_value("cf_m2_arm", "tach_slot", cf[7], 3U);
    ++*cases;

    write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
    return 1;
}

static int cf_run_feedback_and_tach_cases(size_t *cases)
{
    volatile uint8_t *cf = ram_pointer(CF_RAM_BASE);
    volatile uint8_t *cfg = rom_pointer(CF_CONFIG_ADDR);
    uint8_t saved_cfg[32];
    uint8_t saved_counts[2];
    uint32_t ret;

    read_bytes(saved_cfg, cfg, sizeof(saved_cfg));
    read_bytes(saved_counts, rom_pointer(FEEDBACK_COUNTS), sizeof(saved_counts));

    /* Invalid config checks in cruise_free_feedback_ext (shared validator). */
    for (unsigned kind = 0U; kind < 7U; ++kind) {
        write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
        cf_seed_valid_inputs();
        cf[6] = 5U;
        cf[7] = 2U;
        if (kind == 0U)
            cfg[0] = 0x00U;
        else if (kind == 1U)
            cfg[4] = 0x02U;
        else if (kind == 2U)
            cfg[0x1f] = 0x00U;
        else if (kind == 3U)
            cfg[0x1b] = 0x01U;
        else if (kind == 4U)
            cfg[0x17] = 0x01U;
        else if (kind == 5U)
            cfg[7] = 0x00U;
        else
            cfg[7] = 0xffU;
        ret = invoke_r0(CF_FEEDBACK_EXT_ENTRY);
        if (ret != 0U || cf[0] != 0U || cf[1] != 0xffU
                || read_be16(cf + 2U) != 0xffffU || cf[6] != 0U || cf[7] != 0U)
            return fail_value("cf_fbext_badcfg", "ret", ret, 0U);
        ++*cases;
    }
    write_bytes(cfg, saved_cfg, sizeof(saved_cfg));

    /* Orphan tach_slot cleared when tach_ticks == 0. */
    cf_seed_valid_inputs();
    cf[6] = 0U;
    cf[7] = 4U;
    ret = invoke_r0(CF_FEEDBACK_EXT_ENTRY);
    if (ret != 1U || cf[7] != 0U)
        return fail_value("cf_fbext_orphan", "slot", cf[7], 0U);
    ++*cases;

    /* Every tach abort condition inside cruise_free_feedback_ext. */
    for (unsigned sub = 0U; sub < 7U; ++sub) {
        write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
        cfg[5] = 0x07U;
        cfg[6] = 0x07U;
        cf_seed_valid_inputs();
        cf[6] = 5U;
        cf[7] = 3U;
        if (sub == 0U)
            cfg[5] = 0x03U; /* flags.2 == 0 */
        else if (sub == 1U)
            cfg[6] = 0x03U; /* feedback_mode.2 == 0 */
        else if (sub == 2U)
            cf[7] = 0U; /* slot == 0 */
        else if (sub == 3U)
            cf[7] = 6U; /* slot >= 6 */
        else if (sub == 4U)
            write_be16(ram_pointer(CF_RPM_FINE), 1U);
        else if (sub == 5U)
            cf_write_rpm_coarse(1U);
        else
            cf[0] = 0x01U; /* not stationary */
        invoke_r0(CF_FEEDBACK_EXT_ENTRY);
        if (cf[6] != 0U || cf[7] != 0U)
            return fail_value("cf_fbext_abort", "ticks", cf[6], 0U);
        ++*cases;
    }

    /* Normal tach countdown 2 -> 1 -> 0 (clears slot on 0). */
    write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
    cfg[5] = 0x07U;
    cfg[6] = 0x04U; /* tach only, lamp_mask == 0 */
    cf_seed_valid_inputs();
    cf[6] = 2U;
    cf[7] = 4U;
    ret = invoke_r0(CF_FEEDBACK_EXT_ENTRY);
    if (ret != 0U || cf[6] != 1U || cf[7] != 4U)
        return fail_value("cf_fbext_tick1", "ticks", cf[6], 1U);
    ret = invoke_r0(CF_FEEDBACK_EXT_ENTRY);
    if (ret != 0U || cf[6] != 0U || cf[7] != 0U)
        return fail_value("cf_fbext_tick2", "slot", cf[7], 0U);
    ++*cases;

    /* Multi-channel cruise_feedback_engine: MIL-only (0x02), BOTH (0x03), OFF (0x00). */
    rom_pointer(FEEDBACK_COUNTS)[0] = 1U;
    rom_pointer(FEEDBACK_COUNTS)[1] = 1U;
    {
        uint8_t state[8] = {0, 0, 0, 0, 1, 1, 0, 0};

        /* MIL-only: sets/clears 0x551 byte 3 bit 5 preserving 0x5A, leaves byte 5 untouched. */
        cfg[5] = 0x03U;
        cfg[6] = 0x02U;
        seed_ram(state);
        write_bytes(ram_pointer(PAYLOAD), payload_seed, sizeof(payload_seed));
        ram_pointer(CF_MIL_BYTE)[0] = 0x5aU;
        invoke_r4(FEEDBACK_ENGINE, 0U);
        if (ram_pointer(CF_MIL_BYTE)[0] != 0x7aU || ram_pointer(PAYLOAD + 5U)[0] != 0xb5U)
            return fail_value("cf_mil_on", "mil", ram_pointer(CF_MIL_BYTE)[0], 0x7aU);
        ram_pointer(CF_MIL_BYTE)[0] = 0x7aU;
        invoke_r4(FEEDBACK_ENGINE, 0U);
#ifdef FEEDBACK_MIL_PRESERVES_STOCK
        if (ram_pointer(CF_MIL_BYTE)[0] != 0x7aU || ram_pointer(PAYLOAD + 5U)[0] != 0xb5U)
            return fail_value("cf_mil_off", "mil", ram_pointer(CF_MIL_BYTE)[0], 0x7aU);
#else
        if (ram_pointer(CF_MIL_BYTE)[0] != 0x5aU || ram_pointer(PAYLOAD + 5U)[0] != 0xb5U)
            return fail_value("cf_mil_off", "mil", ram_pointer(CF_MIL_BYTE)[0], 0x5aU);
#endif
        ++*cases;

        /* BOTH (CRUISE + MIL): drives both byte 5 and byte 3. */
        cfg[6] = 0x03U;
        seed_ram(state);
        write_bytes(ram_pointer(PAYLOAD), payload_seed, sizeof(payload_seed));
        ram_pointer(CF_MIL_BYTE)[0] = 0x5aU;
        invoke_r4(FEEDBACK_ENGINE, 0U);
        if (ram_pointer(CF_MIL_BYTE)[0] != 0x7aU || ram_pointer(PAYLOAD + 5U)[0] != 0xc5U)
            return fail_value("cf_both_on", "status", ram_pointer(PAYLOAD + 5U)[0], 0xc5U);
        ++*cases;

        /* Lamp mask 0 (feedback_mode=0x00): clears feedback state and preserves payload. */
        cfg[6] = 0x00U;
        seed_ram(state);
        write_bytes(ram_pointer(PAYLOAD), payload_seed, sizeof(payload_seed));
        invoke_r4(FEEDBACK_ENGINE, 0U);
        if (ram_pointer(SELECTOR_STATE)[4] != 0U || ram_pointer(PAYLOAD + 5U)[0] != 0xb5U)
            return fail_value("cf_lamp_off", "pulses", ram_pointer(SELECTOR_STATE)[4], 0U);
        ++*cases;
    }

    /* Tachometer 0x180 & 0x1F9 wrappers across all 5 slots (1000..5000 RPM). */
    write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
    cfg[5] = 0x07U;
    cfg[6] = 0x04U;
    for (unsigned slot = 1U; slot <= 5U; ++slot) {
        uint16_t want = (uint16_t)(slot * 0x1f40U);

        cf_seed_valid_inputs();
        cf[6] = 10U;
        cf[7] = (uint8_t)slot;
        fill_bytes(ram_pointer(CF_TACH_180_PAYLOAD - 1U), 4U, 0xa5U);
        fill_bytes(ram_pointer(CF_TACH_1F9_PAYLOAD - 1U), 4U, 0x5aU);
        invoke_r0(CF_TACH_180_WRAPPER);
        invoke_r0(CF_TACH_1F9_WRAPPER);
        if (read_be16(ram_pointer(CF_TACH_180_PAYLOAD)) != want
                || ram_pointer(CF_TACH_180_PAYLOAD - 1U)[0] != 0xa5U
                || ram_pointer(CF_TACH_180_PAYLOAD + 2U)[0] != 0xa5U)
            return fail_value("cf_tach_180", "rpm", read_be16(ram_pointer(CF_TACH_180_PAYLOAD)), want);
        if (read_be16(ram_pointer(CF_TACH_1F9_PAYLOAD)) != want
                || ram_pointer(CF_TACH_1F9_PAYLOAD - 1U)[0] != 0x5aU
                || ram_pointer(CF_TACH_1F9_PAYLOAD + 2U)[0] != 0x5aU)
            return fail_value("cf_tach_1f9", "rpm", read_be16(ram_pointer(CF_TACH_1F9_PAYLOAD)), want);
        ++*cases;
    }

    /* Tachometer fail-closed no-op returns (8 conditions). */
    for (unsigned sub = 0U; sub < 8U; ++sub) {
        write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
        cfg[5] = 0x07U;
        cfg[6] = 0x04U;
        cf_seed_valid_inputs();
        cf[6] = 10U;
        cf[7] = 2U;
        if (sub == 0U)
            cfg[0] = 0x00U;
        else if (sub == 1U)
            cfg[4] = 0x02U;
        else if (sub == 2U)
            cfg[0x1f] = 0x00U;
        else if (sub == 3U)
            cfg[5] = 0x03U;
        else if (sub == 4U)
            cfg[6] = 0x03U;
        else if (sub == 5U)
            cf[6] = 0U;
        else if (sub == 6U)
            cf[7] = 0U;
        else
            cf[7] = 6U;
        write_be16(ram_pointer(CF_TACH_180_PAYLOAD), 0x1234U);
        invoke_r0(CF_TACH_180_WRAPPER);
        if (read_be16(ram_pointer(CF_TACH_180_PAYLOAD)) != 0x1234U)
            return fail_value("cf_tach_noop", "rpm", read_be16(ram_pointer(CF_TACH_180_PAYLOAD)), 0x1234U);
        ++*cases;
    }

    /* Tachometer hard-interlock aborts (rpm_fine!=0, rpm_coarse!=0, !stationary,
       live gate drops, nonzero raw speed, and expired age between RX and TX). */
    for (unsigned sub = 0U; sub < 7U; ++sub) {
        write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
        cfg[5] = 0x07U;
        cfg[6] = 0x04U;
        cf_seed_valid_inputs();
        cf[6] = 10U;
        cf[7] = 3U;
        if (sub == 0U)
            write_be16(ram_pointer(CF_RPM_FINE), 1U);
        else if (sub == 1U)
            cf_write_rpm_coarse(1U);
        else if (sub == 2U)
            cf[0] = 0x01U;
        else if (sub == 3U)
            ram_pointer(CF_PORT_STATE)[0] = 0U;
        else if (sub == 4U)
            ram_pointer(CF_HCAN1_STATE)[0] = 0U;
        else if (sub == 5U)
            write_be16(cf + 2U, 1U);
        else
            cf[1] = 4U;
        write_be16(ram_pointer(CF_TACH_1F9_PAYLOAD), 0x4321U);
        invoke_r0(CF_TACH_1F9_WRAPPER);
        if (read_be16(ram_pointer(CF_TACH_1F9_PAYLOAD)) != 0x4321U
                || cf[6] != 0U || cf[7] != 0U)
            return fail_value("cf_tach_abort", "ticks", cf[6], 0U);
        ++*cases;
    }

    /* Invalid MSCF+7 (0x00, 0xFF) in tach_override_apply clears CF[0..7] and leaves TX stock. */
    for (unsigned sub = 0U; sub < 2U; ++sub) {
        write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
        cfg[5] = 0x07U;
        cfg[6] = 0x04U;
        cfg[7] = sub == 0U ? 0x00U : 0xffU;
        cf_seed_valid_inputs();
        cf[6] = 10U;
        cf[7] = 3U;
        write_be16(ram_pointer(CF_TACH_180_PAYLOAD), 0x2468U);
        invoke_r0(CF_TACH_180_WRAPPER);
        if (read_be16(ram_pointer(CF_TACH_180_PAYLOAD)) != 0x2468U
                || cf[0] != 0U || cf[1] != 0xffU || read_be16(cf + 2U) != 0xffffU
                || cf[6] != 0U || cf[7] != 0U)
            return fail_value("cf_tach_bad_age", "flags", cf[0], 0U);
        ++*cases;
    }

    write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
    write_bytes(rom_pointer(FEEDBACK_COUNTS), saved_counts, sizeof(saved_counts));
    return 1;
}

static int run_cruise_free_cases(void)
{
    size_t cases = 0;

    if (!cf_run_stationary_cases(&cases))
        return 0;
    if (!cf_run_config_and_step_cases(&cases))
        return 0;
    if (!cf_run_feedback_and_tach_cases(&cases))
        return 0;
    printf("VQ_SH_ELF_MAP_SWITCHING_CRUISE_FREE status=PASS cases=%lu entries=8\n",
        (unsigned long)cases);
    return 1;
}
#endif

#ifdef VERIFY_EEPROM_PERSISTENCE
static void ee_clear_quarantine(void)
{
    volatile uint8_t *ee = ram_pointer(EE_RAM_BASE);
    volatile uint8_t *ctrl = m95320_ptr(0x1000U);

    ctrl[0x00] = 0U;
    ctrl[0x01] = 0U;
    ctrl[0x02] = 0U;
    ctrl[0x03] = 0U;
    ctrl[0x05] = 0U;
    ctrl[0x1d] = 0U;
    ctrl[0x1c] = 3U;
    write_be16(ram_pointer(EE_PCDR_ADDR), 0x0015U);
    if (ee[0] == 5U) {
        invoke_r0(EE_TASK_WRAPPER);
        if (ee[0] == 5U)
            invoke_r0(EE_TASK_WRAPPER);
    }
}

static int ee_advance_to_phase(uint8_t slot_index, uint8_t target_phase)
{
    volatile uint8_t *ee = ram_pointer(EE_RAM_BASE);
    unsigned guard;

    ram_pointer(SELECTOR_STATE)[0] = slot_index;
    ee_seed_admitted();
    for (guard = 0U; guard < 16U; ++guard) {
        if (ee[0] == target_phase)
            return 1;
        invoke_r0(EE_TASK_WRAPPER);
    }
    return ee[0] == target_phase;
}

static int ee_run_boot_cases(size_t *cases)
{
    volatile uint8_t *ee = ram_pointer(EE_RAM_BASE);
    volatile uint8_t *cfg = rom_pointer(EE_CONFIG_ADDR);
    volatile uint8_t *ctrl = m95320_ptr(0x1000U);
    uint8_t saved_cfg[16];
    uint8_t rec_a[16], rec_b[16];
    uint32_t ret;

    read_bytes(saved_cfg, cfg, sizeof(saved_cfg));

    /* 1. Blank EEPROM -> Map 1 (0), boot_flags=1, active_page=0xFF. */
    ee_reset_device(1);
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 0U || ee[1] != 0xffU || ee[2] != 0U || ee[3] != 1U)
        return fail_value("ee_boot_blank", "boot_flags", ee[3], 1U);
    ++*cases;

    /* 2. Page A only (slot 4, gen 10) -> index 3, active_page=0. */
    ee_reset_device(1);
    ee_build_record(rec_a, 4U, 10U);
    write_bytes(m95320_ptr(EE_PAGE_A_OFF), rec_a, 16U);
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 3U || ee[1] != 0U || ee[2] != 4U || ee_read_be32(ee + 4) != 10U)
        return fail_value("ee_boot_only_a", "ret", ret, 3U);
    ++*cases;

    /* 3. Page B only (slot 2, gen 5) -> index 1, active_page=1. */
    ee_reset_device(1);
    ee_build_record(rec_b, 2U, 5U);
    write_bytes(m95320_ptr(EE_PAGE_B_OFF), rec_b, 16U);
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 1U || ee[1] != 1U || ee[2] != 2U || ee_read_be32(ee + 4) != 5U)
        return fail_value("ee_boot_only_b", "ret", ret, 1U);
    ++*cases;

    /* 4. Both valid: A newer, B newer, 32-bit rollover both directions. */
    ee_reset_device(1);
    ee_build_record(rec_a, 5U, 12U);
    ee_build_record(rec_b, 2U, 11U);
    write_bytes(m95320_ptr(EE_PAGE_A_OFF), rec_a, 16U);
    write_bytes(m95320_ptr(EE_PAGE_B_OFF), rec_b, 16U);
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 4U || ee[1] != 0U)
        return fail_value("ee_boot_a_newer", "ret", ret, 4U);
    ++*cases;

    ee_build_record(rec_b, 3U, 13U);
    write_bytes(m95320_ptr(EE_PAGE_B_OFF), rec_b, 16U);
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 2U || ee[1] != 1U)
        return fail_value("ee_boot_b_newer", "ret", ret, 2U);
    ++*cases;

    ee_build_record(rec_a, 2U, 0xffffffffU);
    ee_build_record(rec_b, 4U, 0U);
    write_bytes(m95320_ptr(EE_PAGE_A_OFF), rec_a, 16U);
    write_bytes(m95320_ptr(EE_PAGE_B_OFF), rec_b, 16U);
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 3U || ee[1] != 1U || ee_read_be32(ee + 4) != 0U)
        return fail_value("ee_boot_wrap_b", "ret", ret, 3U);
    ++*cases;

    ee_build_record(rec_a, 5U, 0U);
    ee_build_record(rec_b, 1U, 0xffffffffU);
    write_bytes(m95320_ptr(EE_PAGE_A_OFF), rec_a, 16U);
    write_bytes(m95320_ptr(EE_PAGE_B_OFF), rec_b, 16U);
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 4U || ee[1] != 0U || ee_read_be32(ee + 4) != 0U)
        return fail_value("ee_boot_wrap_a", "ret", ret, 4U);
    ++*cases;

    /* 5. Ambiguity: equal generation and exact half-range diff -> Map 1 + lockout. */
    for (unsigned kind = 0U; kind < 2U; ++kind) {
        ee_reset_device(1);
        ee_build_record(rec_a, 2U, kind == 0U ? 10U : 0U);
        ee_build_record(rec_b, 4U, kind == 0U ? 10U : 0x80000000U);
        write_bytes(m95320_ptr(EE_PAGE_A_OFF), rec_a, 16U);
        write_bytes(m95320_ptr(EE_PAGE_B_OFF), rec_b, 16U);
        ret = invoke_r0(EE_BOOT_RESTORE);
        if (ret != 0U || ee[3] != 3U || ee[0x0f] != 7U)
            return fail_value("ee_boot_ambig", "boot_flags", ee[3], 3U);
        ++*cases;
    }

    /* 6. Record decoder rejects every malformed field (7 variants). */
    for (unsigned kind = 0U; kind < 7U; ++kind) {
        ee_reset_device(1);
        ee_build_record(rec_a, 3U, 9U);
        if (kind == 0U)
            rec_a[12] = 0x00U; /* bad commit marker */
        else if (kind == 1U)
            rec_a[0] = 'X'; /* bad 'M' */
        else if (kind == 2U)
            rec_a[1] = 'X'; /* bad 'S' */
        else if (kind == 3U)
            rec_a[2] = 2U; /* bad version */
        else if (kind == 4U)
            rec_a[3] = 0U; /* slot == 0 */
        else if (kind == 5U)
            rec_a[3] = 6U; /* slot > 5 */
        else
            rec_a[8] ^= 0x01U; /* bad CRC-32 */
        write_bytes(m95320_ptr(EE_PAGE_A_OFF), rec_a, 16U);
        ret = invoke_r0(EE_BOOT_RESTORE);
        if (ret != 0U || ee[1] != 0xffU || ee[3] != 1U)
            return fail_value("ee_boot_corrupt", "active_page", ee[1], 0xffU);
        ++*cases;
    }

    /* 7. Invalid/disabled MSPE config checks (all 8 branches of ee_validate_cfg). */
    for (unsigned kind = 0U; kind < 8U; ++kind) {
        write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
        ee_reset_device(1);
        if (kind == 0U)
            cfg[0] = 0x00U; /* magic */
        else if (kind == 1U)
            cfg[4] = 2U; /* version */
        else if (kind == 2U)
            cfg[5] = 0U; /* flags disabled */
        else if (kind == 3U) {
            cfg[6] = 0U;
            cfg[7] = 0U; /* write_delay_ticks == 0 */
        } else if (kind == 4U)
            cfg[8] = 0U; /* wip_timeout_ticks == 0 */
        else if (kind == 5U)
            cfg[9] = 0U; /* max_retries == 0 */
        else if (kind == 6U)
            cfg[10] = 1U; /* reserved != 0 */
        else
            cfg[15] = 0x00U; /* sentinel */
        ret = invoke_r0(EE_BOOT_RESTORE);
        if (ret != 0U || ee[3] != 0U || *m95320_u32(0x1010U) != 0U)
            return fail_value("ee_boot_badcfg", "rdsr", *m95320_u32(0x1010U), 0U);
        ++*cases;
    }
    write_bytes(cfg, saved_cfg, sizeof(saved_cfg));

    /* 8. Boot SPI/SCI2 fault handling & stale RDRF/ORER drain. */
    /* spi_tx_stall -> RDSR timeout -> ERR_BOOT_READ (8). */
    ee_reset_device(1);
    ctrl[0x00] = 0x04U;
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 0U || ee[3] != 0U || ee[0x0f] != 8U)
        return fail_value("ee_boot_stall", "last_error", ee[0x0f], 8U);
    ++*cases;

    /* tend_stall -> ee_cs_high TEND timeout sets sticky r7=-1 -> RDSR returns -1. */
    ee_reset_device(1);
    ctrl[0x00] = 0x10U;
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 0U || ee[3] != 0U || ee[0x0f] != 8U)
        return fail_value("ee_boot_tend", "last_error", ee[0x0f], 8U);
    ++*cases;

    /* bus_fault_read (0xFF -> WIP==1) -> ERR_BOOT_READ (8). */
    ee_reset_device(1);
    ctrl[0x00] = 0x01U;
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 0U || ee[0x0f] != 8U)
        return fail_value("ee_boot_busfault", "last_error", ee[0x0f], 8U);
    ++*cases;

    /* Page A read SPI fail (2 bytes RDSR + 1st byte Page A). */
    ee_reset_device(1);
    ctrl[0x1d] = 3U;
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 0U || ee[0x0f] != 8U)
        return fail_value("ee_boot_page_a_fail", "last_error", ee[0x0f], 8U);
    ++*cases;

    /* Page B read SPI fail (2 bytes RDSR + 19 bytes Page A + 1st byte Page B). */
    ee_reset_device(1);
    ctrl[0x1d] = 22U;
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 0U || ee[0x0f] != 8U)
        return fail_value("ee_boot_page_b_fail", "last_error", ee[0x0f], 8U);
    ++*cases;

    /* Stale RDRF (0xC4) and stale ORER (0xA4) drained cleanly by ee_cs_low. */
    for (unsigned kind = 0U; kind < 2U; ++kind) {
        ee_reset_device(1);
        ee_build_record(rec_a, 3U, 1U);
        write_bytes(m95320_ptr(EE_PAGE_A_OFF), rec_a, 16U);
        ctrl[0x1e] = kind == 0U ? 0xc4U : 0xa4U;
        ret = invoke_r0(EE_BOOT_RESTORE);
        if (ret != 2U || ee[3] != 1U || ee[0x0f] != 0U)
            return fail_value("ee_boot_drain", "ret", ret, 2U);
        ++*cases;
    }

    /* Mid-transfer ORER (ctrl_flags bit 6) caught in ee_wait_rdrf -> ERR_BOOT_READ. */
    ee_reset_device(1);
    ctrl[0x00] = 0x40U;
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 0U || ee[0x0f] != 8U)
        return fail_value("ee_boot_orer", "last_error", ee[0x0f], 8U);
    ++*cases;

    /* TDRE stuck 0 (inject_ssr=0x04) caught in ee_wait_tdre -> ERR_BOOT_READ. */
    ee_reset_device(1);
    ctrl[0x1e] = 0x04U;
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 0U || ee[0x0f] != 8U)
        return fail_value("ee_boot_tdre", "last_error", ee[0x0f], 8U);
    ++*cases;

    write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
    return 1;
}

static int ee_run_writer_cases(size_t *cases)
{
    volatile uint8_t *ee = ram_pointer(EE_RAM_BASE);
    volatile uint8_t *cfg = rom_pointer(EE_CONFIG_ADDR);
    volatile uint8_t *ctrl = m95320_ptr(0x1000U);
    uint8_t saved_cfg[16];
    uint8_t tail_a[16], tail_b[16];
    uint8_t rec_a[16], rec_b[16];
    uint32_t ret;
    size_t i;

    read_bytes(saved_cfg, cfg, sizeof(saved_cfg));
    /* Shorten timings in mutable fixture ROM for deterministic ticks. */
    write_be16(cfg + 6U, 2U); /* write_delay_ticks = 2 */
    cfg[8] = 2U;              /* wip_timeout_ticks = 2 */
    cfg[9] = 2U;              /* max_retries_per_slot = 2 */

    /* 1. IDLE gates: stock_busy, disabled MSPE, boot_flags!=1, selector>4. */
    ee_reset_device(1);
    invoke_r0(EE_BOOT_RESTORE);
    ee_seed_admitted();
    ram_pointer(SELECTOR_STATE)[0] = 2U;
    ram_pointer(EE_STOCK_BUSY)[0] = 1U;
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[0] != 0U || ee[8] != 0U)
        return fail_value("ee_idle_busy", "pending", ee[8], 0U);
    ram_pointer(EE_STOCK_BUSY)[0] = 0U;

    cfg[5] = 0U; /* MSPE disabled */
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[8] != 0U)
        return fail_value("ee_idle_disabled", "pending", ee[8], 0U);
    cfg[5] = 1U;

    ee[3] = 3U; /* ambiguous lockout */
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[8] != 0U)
        return fail_value("ee_idle_lockout", "pending", ee[8], 0U);
    ee[3] = 1U;

    ram_pointer(SELECTOR_STATE)[0] = 5U; /* invalid selector */
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[8] != 0U)
        return fail_value("ee_idle_badsel", "pending", ee[8], 0U);
    ++*cases;

    /* 2. All 7 write-admission gates block debounce; Vbat 0x8A admits. */
    ram_pointer(SELECTOR_STATE)[0] = 1U;
    for (unsigned gate = 0U; gate < 7U; ++gate) {
        ee_seed_admitted();
        write_be16(ee + 0x0aU, 1U);
        if (gate == 0U)
            write_be16(ram_pointer(EE_PLDR_ADDR), 0x0000U);
        else if (gate == 1U)
            ram_pointer(EE_PORT_STATE)[0] = 0x00U;
        else if (gate == 2U)
            ram_pointer(EE_PORT_STATE)[0] = (uint8_t)(EE_IG_ON_MASK | EE_START_MASK);
        else if (gate == 3U)
            ram_pointer(EE_SHUTDOWN_REQ)[0] = EE_SHUTDOWN_REQ_MASK;
        else if (gate == 4U)
            ee_write_be32(ram_pointer(EE_SHUTDOWN_STATE), 1U);
        else if (gate == 5U)
            ee_write_be32(ram_pointer(EE_REINIT_MODE), 1U);
        else
            ram_pointer(EE_VBAT)[0] = 0x89U;
        invoke_r0(EE_TASK_WRAPPER);
        if (read_be16(ee + 0x0aU) != 0U || ee[0] != 0U)
            return fail_value("ee_idle_inhibit", "debounce", read_be16(ee + 0x0aU), 0U);
        ++*cases;
    }
    ee_seed_admitted();
    ram_pointer(EE_VBAT)[0] = 0x8aU; /* exact threshold admitted */
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[8] != 2U || read_be16(ee + 0x0aU) != 1U)
        return fail_value("ee_idle_vbat_ok", "debounce", read_be16(ee + 0x0aU), 1U);
    /* Slot change mid-debounce resets debounce to 1 for new slot. */
    ram_pointer(SELECTOR_STATE)[0] = 2U;
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[8] != 3U || read_be16(ee + 0x0aU) != 1U)
        return fail_value("ee_idle_redebounce", "pending", ee[8], 3U);
    ++*cases;

    /* 3. Full ping-pong commits (blank -> A -> B -> A) preserving bytes 16..31. */
    ee_reset_device(1);
    for (i = 0; i < 16U; ++i) {
        tail_a[i] = (uint8_t)(0xa1U + i);
        tail_b[i] = (uint8_t)(0xb1U + i);
    }
    write_bytes(m95320_ptr(EE_PAGE_A_OFF + 16U), tail_a, 16U);
    write_bytes(m95320_ptr(EE_PAGE_B_OFF + 16U), tail_b, 16U);
    invoke_r0(EE_BOOT_RESTORE);
    ctrl[0x02] = 1U; /* wip_polls_per_write = 1 */
    {
        static const uint8_t slots[3] = {2U, 4U, 1U}; /* 0-based -> Map 3, 5, 2 */
        static const uint8_t pages[3] = {0U, 1U, 0U};
        for (i = 0; i < 3U; ++i) {
            ee_seed_admitted();
            ram_pointer(SELECTOR_STATE)[0] = slots[i];
            if (!ee_advance_to_phase(slots[i], 1U))
                return fail_value("ee_pp_stage", "phase", ee[0], 1U);
            /* Step through PRE_WIP -> WAIT_INVAL -> WAIT_BODY -> WAIT_COMMIT -> IDLE. */
            for (unsigned tick = 0U; tick < 12U && ee[0] != 0U; ++tick)
                invoke_r0(EE_TASK_WRAPPER);
            if (ee[0] != 0U || ee[1] != pages[i]
                    || ee[2] != (uint8_t)(slots[i] + 1U)
                    || ee_read_be32(ee + 4) != (uint32_t)i
                    || ee_read_be32(ee + 0x14) != (uint32_t)(i + 1U)
                    || *m95320_u32(0x1008U) != (uint32_t)((i + 1U) * 3U))
                return fail_value("ee_pp_commit", "write_cmds",
                    *m95320_u32(0x1008U), (uint32_t)((i + 1U) * 3U));
            ++*cases;
        }
    }
    /* Redundant slot triggers 0 additional writes. */
    ram_pointer(SELECTOR_STATE)[0] = 1U;
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[0] != 0U || ee[8] != 0U || *m95320_u32(0x1008U) != 9U)
        return fail_value("ee_pp_redundant", "write_cmds", *m95320_u32(0x1008U), 9U);
    /* Bytes 16..31 of both pages untouched. */
    if (!fail_bytes("ee_pp_tail_a", "tail", m95320_ptr(EE_PAGE_A_OFF + 16U), tail_a, 16U))
        return 0;
    if (!fail_bytes("ee_pp_tail_b", "tail", m95320_ptr(EE_PAGE_B_OFF + 16U), tail_b, 16U))
        return 0;
    /* Reboot restores newest committed slot 2 (index 1, gen 2, page A). */
    ctrl[0x02] = 0U;
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 1U || ee[1] != 0U || ee_read_be32(ee + 4) != 2U)
        return fail_value("ee_pp_reboot", "ret", ret, 1U);
    ++*cases;

    /* 4. Active RDSR SPI fail + quarantine recovery (SPI fail, WIP, WRDI reject,
          and double-RDSR confirmation before releasing back to IDLE). */
    if (!ee_advance_to_phase(3U, 1U))
        return fail_value("ee_q_stage", "phase", ee[0], 1U);
    ctrl[0x00] = 0x04U; /* spi_tx_stall in active phase */
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[0] != 5U || ee[0x0f] != 1U)
        return fail_value("ee_q_enter", "phase", ee[0], 5U);
    /* SPI fail inside QUARANTINE keeps phase=5. */
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[0] != 5U)
        return fail_value("ee_q_spifail", "phase", ee[0], 5U);
    /* WIP==1 inside QUARANTINE keeps phase=5. */
    ctrl[0x00] = 0x00U;
    ctrl[0x1c] = 2U; /* reset SCI2 */
    ctrl[0x05] = 1U; /* wip_remaining = 1 */
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[0] != 5U)
        return fail_value("ee_q_wip", "phase", ee[0], 5U);
    /* WIP==0 && WEL==1 with wrdi_reject=1: issues WRDI, stays quarantined. */
    ctrl[0x1f] = 1U;    /* force WEL=1 */
    ctrl[0x00] = 0x20U; /* wrdi_reject */
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[0] != 5U)
        return fail_value("ee_q_wrdi_rej", "phase", ee[0], 5U);
    /* Clear wrdi_reject: issues WRDI, STILL stays quarantined until fresh RDSR! */
    ctrl[0x00] = 0x00U;
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[0] != 5U)
        return fail_value("ee_q_double_rdsr", "phase", ee[0], 5U);
    /* Next tick fresh RDSR proves WIP==0 && WEL==0 -> exits to IDLE. */
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[0] != 0U)
        return fail_value("ee_q_exit", "phase", ee[0], 0U);
    ++*cases;

    /* 5. WIP timeout in active phase (ERR_WIP_TIMEOUT = 2). */
    ee_reset_device(1);
    invoke_r0(EE_BOOT_RESTORE);
    if (!ee_advance_to_phase(2U, 1U))
        return fail_value("ee_wipto_stage", "phase", ee[0], 1U);
    ctrl[0x05] = 0xffU; /* sticky WIP */
    invoke_r0(EE_TASK_WRAPPER); /* wip_ticks = 1 < 2 */
    if (ee[0] != 1U || ee[0x0c] != 1U)
        return fail_value("ee_wipto_1", "wip_ticks", ee[0x0c], 1U);
    invoke_r0(EE_TASK_WRAPPER); /* wip_ticks = 2 >= 2 -> abort(2) */
    if (ee[0] != 5U || ee[0x0f] != 2U)
        return fail_value("ee_wipto_2", "last_error", ee[0x0f], 2U);
    ee_clear_quarantine();
    ++*cases;

    /* 6. Inhibit during PRE_WIP, WAIT_INVAL, and WAIT_BODY (ERR_INHIBITED = 6). */
    for (unsigned target_phase = 1U; target_phase <= 3U; ++target_phase) {
        ee_reset_device(1);
        invoke_r0(EE_BOOT_RESTORE);
        if (!ee_advance_to_phase(2U, (uint8_t)target_phase))
            return fail_value("ee_inh_stage", "phase", ee[0], target_phase);
        write_be16(ram_pointer(EE_PLDR_ADDR), 0x0000U); /* drop IG ON */
        invoke_r0(EE_TASK_WRAPPER);
        if (ee[0] != 5U || ee[0x0f] != 6U)
            return fail_value("ee_inh_abort", "last_error", ee[0x0f], 6U);
        ee_clear_quarantine();
        ++*cases;
    }

    /* 7. BP=3 write-protect fail at WAIT_INVAL + retry budget + slot re-selection. */
    ee_reset_device(1);
    ee_build_record(rec_a, 2U, 5U);
    write_bytes(m95320_ptr(EE_PAGE_A_OFF), rec_a, 16U);
    invoke_r0(EE_BOOT_RESTORE); /* committed_slot = 2 on page A; dest will be B */
    ctrl[0x01] = 3U; /* BP=3 protects entire EEPROM */
    if (!ee_advance_to_phase(3U, 2U))
        return fail_value("ee_bp_stage1", "phase", ee[0], 2U);
    invoke_r0(EE_TASK_WRAPPER); /* WAIT_INVAL sees 0xFFFFFFFF != 0 -> ERR_VERIFY_INVAL (3) */
    if (ee[0] != 5U || ee[0x0f] != 3U || ee[0x0e] != 1U)
        return fail_value("ee_bp_fail1", "retry", ee[0x0e], 1U);
    ee_clear_quarantine();
    /* Switch back to committed slot 2 (clears pending_slot=0, keeps retry_slot=4, retry_count=1). */
    ram_pointer(SELECTOR_STATE)[0] = 1U;
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[8] != 0U || ee[0x0d] != 4U || ee[0x0e] != 1U)
        return fail_value("ee_bp_back", "retry_slot", ee[0x0d], 4U);
    /* Return to slot 4 (hits pending_slot!=desired && retry_slot==desired), fail 2nd time. */
    ctrl[0x01] = 3U;
    if (!ee_advance_to_phase(3U, 2U))
        return fail_value("ee_bp_stage2", "phase", ee[0], 2U);
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[0] != 5U || ee[0x0e] != 2U)
        return fail_value("ee_bp_fail2", "retry", ee[0x0e], 2U);
    ee_clear_quarantine();
    /* Retry budget (2) exhausted -> IDLE refuses to debounce slot 4. */
    ram_pointer(SELECTOR_STATE)[0] = 3U;
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[0] != 0U || read_be16(ee + 0x0aU) != 0U)
        return fail_value("ee_bp_exhausted", "debounce", read_be16(ee + 0x0aU), 0U);
    ++*cases;

    /* 8. Torn body write & corrupt marker at WAIT_BODY (ERR_VERIFY_BODY = 4) +
          torn commit at WAIT_COMMIT (ERR_VERIFY_COMMIT = 5) + safe reboot recovery. */
    ee_reset_device(1);
    ee_build_record(rec_a, 2U, 7U);
    write_bytes(m95320_ptr(EE_PAGE_A_OFF), rec_a, 16U);
    invoke_r0(EE_BOOT_RESTORE);
    if (!ee_advance_to_phase(4U, 2U))
        return fail_value("ee_tear_body_stage", "phase", ee[0], 2U);
    ctrl[0x00] = 0x08U; /* tear_on_write */
    ctrl[0x03] = 4U;    /* only 4 of 12 body bytes written */
    invoke_r0(EE_TASK_WRAPPER); /* WAIT_INVAL writes torn body -> phase 3 */
    ctrl[0x00] = 0x00U;
    invoke_r0(EE_TASK_WRAPPER); /* WAIT_BODY mismatch -> ERR_VERIFY_BODY (4) */
    if (ee[0] != 5U || ee[0x0f] != 4U)
        return fail_value("ee_tear_body", "last_error", ee[0x0f], 4U);
    ee_clear_quarantine();
    /* Reboot after torn body still recovers Page A (slot 2, gen 7). */
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 1U || ee[1] != 0U || ee_read_be32(ee + 4) != 7U)
        return fail_value("ee_tear_body_boot", "ret", ret, 1U);
    ++*cases;

    /* WAIT_BODY corrupt marker bytes 12..15 != 0 -> ERR_VERIFY_BODY (4). */
    if (!ee_advance_to_phase(4U, 3U))
        return fail_value("ee_corrupt_m_stage", "phase", ee[0], 3U);
    m95320_ptr(EE_PAGE_B_OFF + 12U)[0] = 0x55U;
    invoke_r0(EE_TASK_WRAPPER);
    if (ee[0] != 5U || ee[0x0f] != 4U)
        return fail_value("ee_corrupt_m", "last_error", ee[0x0f], 4U);
    ee_clear_quarantine();
    ++*cases;

    /* Torn commit marker -> WAIT_COMMIT mismatch (ERR_VERIFY_COMMIT = 5) + safe reboot. */
    ee_reset_device(1);
    ee_build_record(rec_a, 2U, 7U);
    write_bytes(m95320_ptr(EE_PAGE_A_OFF), rec_a, 16U);
    invoke_r0(EE_BOOT_RESTORE);
    if (!ee_advance_to_phase(4U, 3U))
        return fail_value("ee_tear_commit_stage", "phase", ee[0], 3U);
    ctrl[0x00] = 0x08U;
    ctrl[0x03] = 2U; /* only 2 of 4 commit bytes written */
    invoke_r0(EE_TASK_WRAPPER); /* WAIT_BODY writes torn commit -> phase 4 */
    ctrl[0x00] = 0x00U;
    invoke_r0(EE_TASK_WRAPPER); /* WAIT_COMMIT mismatch -> ERR_VERIFY_COMMIT (5) */
    if (ee[0] != 5U || ee[0x0f] != 5U)
        return fail_value("ee_tear_commit", "last_error", ee[0x0f], 5U);
    ee_clear_quarantine();
    ret = invoke_r0(EE_BOOT_RESTORE);
    if (ret != 1U || ee[1] != 0U || ee_read_be32(ee + 4) != 7U)
        return fail_value("ee_tear_commit_boot", "ret", ret, 1U);
    ++*cases;

    /* 9. Per-phase SPI fault paths (PRE_WIP write, WAIT_INVAL read/write,
          WAIT_BODY read/write, WAIT_COMMIT read). */
    {
        static const struct {
            uint8_t phase;
            uint8_t countdown;
        } spi_faults[] = {
            {1U, 3U},  /* PRE_WIP write fail */
            {2U, 3U},  /* WAIT_INVAL read fail */
            {2U, 10U}, /* WAIT_INVAL write fail (2 RDSR + 7 READ = 9) */
            {3U, 3U},  /* WAIT_BODY read fail */
            {3U, 22U}, /* WAIT_BODY write fail (2 RDSR + 19 READ = 21) */
            {4U, 3U},  /* WAIT_COMMIT read fail */
        };
        for (i = 0; i < ARRAY_SIZE(spi_faults); ++i) {
            ee_reset_device(1);
            ee_build_record(rec_b, 1U, 1U);
            write_bytes(m95320_ptr(EE_PAGE_B_OFF), rec_b, 16U);
            invoke_r0(EE_BOOT_RESTORE);
            if (!ee_advance_to_phase(2U, spi_faults[i].phase))
                return fail_value("ee_spifault_stage", "phase", ee[0], spi_faults[i].phase);
            ctrl[0x1d] = spi_faults[i].countdown;
            invoke_r0(EE_TASK_WRAPPER);
            if (ee[0] != 5U || ee[0x0f] != 1U)
                return fail_value("ee_spifault", "last_error", ee[0x0f], 1U);
            ee_clear_quarantine();
            ++*cases;
        }
    }

    write_bytes(cfg, saved_cfg, sizeof(saved_cfg));
    ee_reset_device(1);
    return 1;
}

static int run_eeprom_cases(void)
{
    size_t cases = 0;

    if (!ee_run_boot_cases(&cases))
        return 0;
    if (!ee_run_writer_cases(&cases))
        return 0;
    printf("VQ_SH_ELF_MAP_SWITCHING_EEPROM status=PASS cases=%lu entries=2\n",
        (unsigned long)cases);
    return 1;
}

#ifdef EE_STARTUP_WARM_ENTRY_PC
static int run_stock_warm_reinit_cases(void)
{
    uint8_t state[8] = {3U, 0x11U, 0x22U, 0x33U, 0x44U, 0x55U, 0x66U, 0x77U};
    uint8_t cf_seed[CF_RAM_SIZE];
    uint8_t ee_seed[EE_RAM_SIZE];
    uint8_t rec[16];
    size_t i;
    size_t cases = 0;

    for (i = 0; i < CF_RAM_SIZE; ++i)
        cf_seed[i] = (uint8_t)(0x41U + i);
    for (i = 0; i < EE_RAM_SIZE; ++i)
        ee_seed[i] = (uint8_t)(0x81U + i);
    ee_seed[0] = 2U; /* pending write phase in flight */

    /* Seed EEPROM with a DIFFERENT valid slot (Map 5 = index 4, gen 99) so any
       unintended boot restore would overwrite live Map 4 (index 3). */
    ee_reset_device(1);
    ee_build_record(rec, 5U, 99U);
    write_bytes(m95320_ptr(EE_PAGE_A_OFF), rec, 16U);

#if EE_STARTUP_SHARED_POINTER
    {
        uint32_t saved_hook;

        /* 1. SH7058 stock warm BSR through CAN-wrapped shared hook cell. */
        seed_ram(state);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        write_bytes(ram_pointer(CF_RAM_BASE), cf_seed, sizeof(cf_seed));
        write_bytes(ram_pointer(EE_RAM_BASE), ee_seed, sizeof(ee_seed));
        invoke_r0(EE_STARTUP_WARM_ENTRY_PC);
        if (!fail_bytes("stock_warm_can", "cf_ram",
                ram_pointer(CF_RAM_BASE), cf_seed, sizeof(cf_seed)))
            return 0;
        if (!fail_bytes("stock_warm_can", "ee_ram",
                ram_pointer(EE_RAM_BASE), ee_seed, sizeof(ee_seed)))
            return 0;
        if (*m95320_u32(0x1010U) != 0U || *m95320_u32(0x100cU) != 0U)
            return fail_value("stock_warm_can", "eeprom_io", *m95320_u32(0x1010U), 0U);
        if (!verify_limiter_memory("stock_warm_can", 3))
            return 0;
        ++cases;

        /* 2. SH7058 stock warm BSR through direct Map Switching hook cell. */
        saved_hook = ee_read_be32(rom_pointer(EE_STARTUP_HOOK_SLOT));
        ee_write_be32(rom_pointer(EE_STARTUP_HOOK_SLOT), STARTUP_WRAPPER);
        seed_ram(state);
        fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
        write_bytes(ram_pointer(CF_RAM_BASE), cf_seed, sizeof(cf_seed));
        write_bytes(ram_pointer(EE_RAM_BASE), ee_seed, sizeof(ee_seed));
        invoke_r0(EE_STARTUP_WARM_ENTRY_PC);
        ee_write_be32(rom_pointer(EE_STARTUP_HOOK_SLOT), saved_hook);
        if (!fail_bytes("stock_warm_direct", "cf_ram",
                ram_pointer(CF_RAM_BASE), cf_seed, sizeof(cf_seed)))
            return 0;
        if (!fail_bytes("stock_warm_direct", "ee_ram",
                ram_pointer(EE_RAM_BASE), ee_seed, sizeof(ee_seed)))
            return 0;
        if (*m95320_u32(0x1010U) != 0U || *m95320_u32(0x100cU) != 0U)
            return fail_value("stock_warm_direct", "eeprom_io", *m95320_u32(0x1010U), 0U);
        if (!verify_limiter_memory("stock_warm_direct", 3))
            return 0;
        ++cases;
    }
#else
    /* SH7059 separate warm pointer bypasses startup_wrapper, CAN, limiter_commit,
       and EEPROM boot completely; every sentinel stays untouched. */
    seed_ram(state);
    fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5);
    write_bytes(ram_pointer(CF_RAM_BASE), cf_seed, sizeof(cf_seed));
    write_bytes(ram_pointer(EE_RAM_BASE), ee_seed, sizeof(ee_seed));
    invoke_r0(EE_STARTUP_WARM_ENTRY_PC);
    if (!fail_bytes("stock_warm_bypass", "selector_state",
            ram_pointer(SELECTOR_STATE), state, sizeof(state)))
        return 0;
    if (!fail_bytes("stock_warm_bypass", "cf_ram",
            ram_pointer(CF_RAM_BASE), cf_seed, sizeof(cf_seed)))
        return 0;
    if (!fail_bytes("stock_warm_bypass", "ee_ram",
            ram_pointer(EE_RAM_BASE), ee_seed, sizeof(ee_seed)))
        return 0;
    if (!all_value(ram_pointer(FUEL_SHADOW), FUEL_SHADOW_SIZE, 0xa5)
            || !all_value(ram_pointer(THROTTLE_SHADOW), THROTTLE_SHADOW_SIZE, 0xa5)
            || !all_value(ram_pointer(THROTTLE_RUNTIME), 2, 0xa5))
        return fail_value("stock_warm_bypass", "unexpected_limiter_write", 1U, 0U);
    if (*m95320_u32(0x1010U) != 0U || *m95320_u32(0x100cU) != 0U)
        return fail_value("stock_warm_bypass", "eeprom_io", *m95320_u32(0x1010U), 0U);
    ++cases;
#endif

    ee_reset_device(1);
    printf("VQ_SH_ELF_MAP_SWITCHING_WARM status=PASS cases=%lu shared=%u\n",
        (unsigned long)cases, (unsigned)EE_STARTUP_SHARED_POINTER);
    return 1;
}
#endif
#endif

int main(void)
{
    size_t feedback_invocations = 0;
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
#ifdef VERIFY_7MFK_FUEL_CUT
    if (!run_fuel_cut_consumer_cases())
        return 1;
#endif
#ifdef VERIFY_7MFK_THROTTLE_SCALAR
    if (!run_throttle_scalar_consumer_cases())
        return 1;
#endif
#ifdef VERIFY_7MFK_THROTTLE_CLUSTER
    if (!run_throttle_cluster_cases())
        return 1;
#endif
#ifdef TARGET_VQ37
    if (!run_native_fuel_cut_cases())
        return 1;
#endif
    if (!run_selector_cases())
        return 1;
    if (!run_feedback_cases(&feedback_invocations))
        return 1;
#ifdef VERIFY_CRUISE_FREE
    if (!run_cruise_free_cases())
        return 1;
#endif
#ifdef VERIFY_EEPROM_PERSISTENCE
    if (!run_eeprom_cases())
        return 1;
#ifdef EE_STARTUP_WARM_ENTRY_PC
    if (!run_stock_warm_reinit_cases())
        return 1;
#endif
#endif
#ifndef VERIFY_SELECTOR_FEEDBACK_GUARDS
#ifdef TARGET_1ND
    if (total_cases != 197U)
        return fail_value("summary", "case_count", total_cases, 197);
#elif defined(TARGET_1ME3B) || defined(TARGET_1EK7A)
    if (total_cases != 195U)
        return fail_value("summary", "case_count", total_cases, 195);
#elif defined(TARGET_VQ37)
    if (total_cases != 168U)
        return fail_value("summary", "case_count", total_cases, 168);
#elif defined(TARGET_DUAL_CVTC)
    if (total_cases != 140U)
        return fail_value("summary", "case_count", total_cases, 140);
#else
    if (total_cases != 132U)
        return fail_value("summary", "case_count", total_cases, 132);
#endif
    if (feedback_invocations != 17U)
        return fail_value(
            "summary", "feedback_invocations", feedback_invocations, 17);
#endif

    printf(
        "VQ_SH_ELF_MAP_SWITCHING status=PASS cases=%lu "
        "selector=%lu "
#ifdef TARGET_1ND
        "adapters=136 limiter=14 native_fuel=20 feedback=%lu "
        "feedback_invocations=%lu entries=14\n",
#elif defined(TARGET_1ME3B) || defined(TARGET_1EK7A)
        "adapters=134 limiter=14 native_fuel=20 feedback=%lu "
        "feedback_invocations=%lu entries=14\n",
#elif defined(TARGET_VQ37)
        "adapters=107 limiter=14 native_fuel=20 feedback=%lu "
        "feedback_invocations=%lu entries=13\n",
#elif defined(TARGET_DUAL_CVTC)
        "adapters=99 limiter=14 feedback=%lu feedback_invocations=%lu "
        "entries=13\n",
#else
        "adapters=91 limiter=14 feedback=%lu feedback_invocations=%lu "
        "entries=12\n",
#endif
        (unsigned long)total_cases, (unsigned long)ARRAY_SIZE(selector_cases),
        (unsigned long)ARRAY_SIZE(feedback_cases),
        (unsigned long)feedback_invocations);
    return 0;
}
