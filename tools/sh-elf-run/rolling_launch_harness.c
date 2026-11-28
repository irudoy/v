/* GNU SH-2E gate of exact JK08A Rolling Launch schema 6.
 *
 * The rows come from rolling_launch_rows.py, which runs the schema 6 model
 * in patches/rolling_launch.py. Every row writes its configuration and
 * efficiency table into the simulator ROM image, its base record and
 * extension and its inputs into test RAM, runs one composed entry through
 * invoke_regs, and compares the complete 64 KiB of test RAM with the
 * expected image: the row records, the map 1 limiter commit of a
 * corrupt-state recovery, and no other byte. Every call also checks r8..r14,
 * the stack pointer, GBR and the SR bits of its contract. */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "rolling_launch_rows.h"

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))

#define TEST_RAM_BASE 0x01000000U
#define TEST_RAM_SIZE 0x10000U

#define SELECTOR_STATE 0xffff5d00U
#define FUEL_SHADOW 0xffff5d10U
#define FUEL_SHADOW_SIZE 12U
#define THROTTLE_SHADOW 0xffff5d20U
#define THROTTLE_SHADOW_SIZE 28U
#define THROTTLE_SELECTED 0xffff5d28U
#define THROTTLE_RUNTIME 0xffff1796U
#define RL_STATE 0xffff5d40U
#define RL_STATE_SIZE 44U
#define CF_STATE 0xffff6000U
#define CF_STATE_SIZE 32U
#define EE_STATE 0xffff6020U
#define EE_STATE_SIZE 64U
#define M95320_BASE 0x01010000U
#define PCDR_ADDR 0xfffff73eU
#define RL_EXTENSION 0xffff6100U
#define RL_EXTENSION_SIZE 32U
/* RL_CONFIG, RL_TABLE and FEEDBACK_COUNTS come from the layouts through the
   compiler definitions of verify_rolling_launch.harness_definitions. */
#define RL_CONFIG_SIZE 102U
#define RL_TABLE_SIZE 82U

#define SPEED 0xffff113cU
#define RPM 0xffff11bcU
#define SPEED_RAW 0xffff3b3dU
#define SPEED_AGE 0xffff3b38U
#define HCAN1_STATE 0xffff4195U
#define PORT_STATE 0xffff4185U
#define BUTTON_CODE 0xffff2a85U
#define ASCD_STATUS 0xffff41aeU
#define PEDAL 0xffff2672U
#define COOLANT 0xffff1077U
#define APC_MODE_SNAPSHOT 0xffff24c9U
#define DIAGNOSTIC_STATUS 0xffff2a84U
#define PAYLOAD 0xffff3ad5U

/* Map 1 limiter commit sources of the map-switching runtime. */
#define FUEL_POINTER_TABLE 0x000d35b8U
#define FUEL_STOCK_TAIL 0x00009356U
#define THROTTLE_STOCK_CLUSTER 0x00009424U
#define THROTTLE_POINTER_TABLE 0x000d35ccU

#define PERIODIC_WRAPPER 0x000d3860U
#define SELECTOR_ARBITER 0x000d3880U
#define STARTUP_WRAPPER 0x000d38a0U
#define RL_ENGINE 0x000d38e4U
#define FEEDBACK_ARBITER 0x000d41e0U
#define RPM_FRACTION 0x000d6480U
#define CONTROL_PUBLISHER 0x000d6500U
#define IGNITION_PUBLISHER 0x000d6540U

#define BUTTON_SET 0x08U
#define BUTTON_RELEASED 0x20U

/* invoke_regs loads the T, S, I, Q and M bits of SR; the simulator keeps
   the others. */
#define SR_BITS 0x000003f3U
#define SR_I_S 0x000000f2U
#define SR_ENGINE 0x00000000U

extern uint32_t invoke_regs(uint32_t entry, uint32_t *regs);

static size_t case_count;
static uint32_t regs[16];
static uint8_t expected_ram[TEST_RAM_SIZE];

static volatile uint8_t *ram_pointer(uint32_t original)
{
    return (volatile uint8_t *)(uintptr_t)(TEST_RAM_BASE + (original & 0xffffU));
}

static volatile uint8_t *rom_pointer(uint32_t address)
{
    return (volatile uint8_t *)(uintptr_t)address;
}

static void write_bytes(volatile uint8_t *target, const uint8_t *source, size_t size)
{
    size_t index;

    for (index = 0; index < size; ++index)
        target[index] = source[index];
}

static void fill_bytes(volatile uint8_t *target, size_t size, uint8_t value)
{
    size_t index;

    for (index = 0; index < size; ++index)
        target[index] = value;
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

static int fail_value(const char *name, const char *field, uint32_t actual, uint32_t expected)
{
    printf("VQ_SH_ELF_ROLLING_LAUNCH status=FAIL case=%s field=%s actual=%08lx expected=%08lx\n",
           name, field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}

static int fail_bytes(const char *name, const char *field, const volatile uint8_t *actual,
                      const uint8_t *expected, size_t size)
{
    size_t index;

    for (index = 0; index < size; ++index) {
        if (actual[index] != expected[index]) {
            printf("VQ_SH_ELF_ROLLING_LAUNCH status=FAIL case=%s field=%s offset=%lu "
                   "actual=%02x expected=%02x\n", name, field, (unsigned long)index,
                   (unsigned int)actual[index], (unsigned int)expected[index]);
            return 0;
        }
    }
    return 1;
}

/* Every test RAM byte starts with a position-dependent value, so a stray
   store of any constant differs from it somewhere. */
static void seed_test_ram(void)
{
    uint32_t index;

    for (index = 0; index < TEST_RAM_SIZE; ++index)
        ram_pointer(index)[0] = (uint8_t)(0x5aU ^ (index * 7U) ^ (index >> 8));
}

static void snapshot_ram(void)
{
    const volatile uint32_t *source = (const volatile uint32_t *)(uintptr_t)TEST_RAM_BASE;
    uint32_t *target = (uint32_t *)expected_ram;
    uint32_t index;

    for (index = 0; index < TEST_RAM_SIZE / 4U; ++index)
        target[index] = source[index];
}

static void expect_bytes(uint32_t address, const uint8_t *bytes, size_t size)
{
    size_t index;

    for (index = 0; index < size; ++index)
        expected_ram[(address + index) & 0xffffU] = bytes[index];
}

static void expect_u16(uint32_t address, uint16_t value)
{
    expected_ram[address & 0xffffU] = (uint8_t)(value >> 8);
    expected_ram[(address + 1U) & 0xffffU] = (uint8_t)value;
}

static int compare_ram(const char *name)
{
    const volatile uint32_t *actual = (const volatile uint32_t *)(uintptr_t)TEST_RAM_BASE;
    const uint32_t *expected = (const uint32_t *)expected_ram;
    uint32_t index, byte;

    for (index = 0; index < TEST_RAM_SIZE / 4U; ++index) {
        if (actual[index] == expected[index])
            continue;
        for (byte = index * 4U; byte < index * 4U + 4U; ++byte) {
            if (ram_pointer(byte)[0] != expected_ram[byte]) {
                printf("VQ_SH_ELF_ROLLING_LAUNCH status=FAIL case=%s field=ram "
                       "address=ffff%04lx actual=%02x expected=%02x\n", name,
                       (unsigned long)byte, (unsigned int)ram_pointer(byte)[0],
                       (unsigned int)expected_ram[byte]);
                return 0;
            }
        }
    }
    return 1;
}

/* The map 1 limiter commit of the map-switching runtime: the fuel shadow
   from map 1 and the stock tail, the throttle shadow from the stock cluster
   with the selected map 1 word, and a clear selector. */
static void expect_map1_commit(void)
{
    const volatile uint8_t *fuel = rom_pointer(read_u32(rom_pointer(FUEL_POINTER_TABLE)));
    const volatile uint8_t *throttle = rom_pointer(read_u32(rom_pointer(THROTTLE_POINTER_TABLE)));
    uint8_t bytes[THROTTLE_SHADOW_SIZE];
    size_t index;

    for (index = 0; index < 8U; ++index)
        bytes[index] = fuel[index];
    for (index = 0; index < 4U; ++index)
        bytes[8U + index] = rom_pointer(FUEL_STOCK_TAIL)[index];
    expect_bytes(FUEL_SHADOW, bytes, FUEL_SHADOW_SIZE);
    for (index = 0; index < THROTTLE_SHADOW_SIZE; ++index)
        bytes[index] = rom_pointer(THROTTLE_STOCK_CLUSTER)[index];
    expect_bytes(THROTTLE_SHADOW, bytes, THROTTLE_SHADOW_SIZE);
    expect_u16(THROTTLE_SELECTED, read_u16(throttle));
    expect_u16(THROTTLE_RUNTIME, read_u16(throttle));
    for (index = 0; index < 8U; ++index)
        bytes[index] = 0;
    expect_bytes(SELECTOR_STATE, bytes, 8U);
}

static void load_configuration(uint8_t config)
{
    write_bytes(rom_pointer(RL_CONFIG), rl_configs[config], RL_CONFIG_SIZE);
    write_bytes(rom_pointer(RL_TABLE), rl_tables[config], RL_TABLE_SIZE);
}

static int verify_configuration(const char *name, uint8_t config)
{
    return fail_bytes(name, "configuration", rom_pointer(RL_CONFIG), rl_configs[config],
                      RL_CONFIG_SIZE)
        && fail_bytes(name, "efficiency_table", rom_pointer(RL_TABLE), rl_tables[config],
                      RL_TABLE_SIZE);
}

static void load_records(const uint8_t *base, const uint8_t *extension)
{
    write_bytes(ram_pointer(RL_STATE), base, RL_STATE_SIZE);
    write_bytes(ram_pointer(RL_EXTENSION), extension, RL_EXTENSION_SIZE);
}

/* The limiter shadows hold a value that no map 1 commit stores. */
static void load_shadows(void)
{
    fill_bytes(ram_pointer(FUEL_SHADOW), FUEL_SHADOW_SIZE, 0xa5);
    fill_bytes(ram_pointer(THROTTLE_SHADOW), THROTTLE_SHADOW_SIZE, 0xa5);
    fill_bytes(ram_pointer(THROTTLE_RUNTIME), 2U, 0xa5);
}

static void load_inputs(const struct rl_inputs *in)
{
    write_bytes(ram_pointer(SELECTOR_STATE), in->selector, sizeof(in->selector));
    ram_pointer(ASCD_STATUS)[0] = in->ascd;
    ram_pointer(BUTTON_CODE)[0] = in->button;
    ram_pointer(SPEED_AGE)[0] = in->age;
    ram_pointer(HCAN1_STATE)[0] = in->hcan;
    ram_pointer(PORT_STATE)[0] = in->port;
    ram_pointer(COOLANT)[0] = in->coolant;
    write_u16(ram_pointer(SPEED), in->speed);
    ram_pointer(SPEED_RAW)[0] = (uint8_t)(in->wire >> 8);
    ram_pointer(SPEED_RAW + 1U)[0] = (uint8_t)in->wire;
    write_u16(ram_pointer(RPM), in->rpm);
    write_u16(ram_pointer(PEDAL), in->pedal);
}

/* Call one entry with distinct r1..r14 and the given SR, and require the
   preserved r8..r14, stack pointer and GBR. */
static int call_entry(const char *name, uint32_t entry, uint32_t sr)
{
    uint32_t sp_before, sp_after, gbr_before, gbr_after;
    size_t index;

    for (index = 1; index < 15U; ++index)
        if (index < 3U || index > 5U)
            regs[index] = 0xc0de0000U | (uint32_t)(index << 8) | (uint32_t)index;
    regs[15] = sr;
    __asm__ volatile ("mov r15,%0" : "=r" (sp_before) : : "memory");
    __asm__ volatile ("stc gbr,%0" : "=r" (gbr_before) : : "memory");
    (void)invoke_regs(entry, regs);
    __asm__ volatile ("mov r15,%0" : "=r" (sp_after) : : "memory");
    __asm__ volatile ("stc gbr,%0" : "=r" (gbr_after) : : "memory");
    if (sp_after != sp_before)
        return fail_value(name, "stack_pointer", sp_after, sp_before);
    if (gbr_after != gbr_before)
        return fail_value(name, "gbr", gbr_after, gbr_before);
    for (index = 8; index < 15U; ++index) {
        uint32_t expected = 0xc0de0000U | (uint32_t)(index << 8) | (uint32_t)index;
        if (regs[index] != expected)
            return fail_value(name, "callee_saved", regs[index], expected);
    }
    ++case_count;
    return 1;
}

static int run_engine_rows(void)
{
    size_t index;

    for (index = 0; index < ARRAY_SIZE(engine_rows); ++index) {
        const struct engine_row *row = &engine_rows[index];

        load_configuration(row->config);
        load_records(row->base, row->ext);
        load_shadows();
        load_inputs(&row->in);
        snapshot_ram();
        expect_bytes(RL_STATE, row->base_out, RL_STATE_SIZE);
        expect_bytes(RL_EXTENSION, row->ext_out, RL_EXTENSION_SIZE);
        if (row->restore)
            expect_map1_commit();
        regs[3] = regs[4] = regs[5] = 0;
        if (!call_entry(row->name, row->periodic ? PERIODIC_WRAPPER : RL_ENGINE, SR_ENGINE))
            return 0;
        if ((regs[15] & SR_I_S) != (SR_ENGINE & SR_I_S))
            return fail_value(row->name, "sr", regs[15], SR_ENGINE);
        if (!compare_ram(row->name) || !verify_configuration(row->name, row->config))
            return 0;
    }
    return 1;
}

/* The publishers restore the complete SR of their caller; the rows alternate
   the scheduler level with every SR bit set. */
static uint32_t publisher_sr(size_t index)
{
    return (index & 1U) ? 0x000003f3U : 0x00000000U;
}

static int run_publisher_rows(const struct publisher_row *rows, size_t count, uint32_t entry,
                              int control)
{
    size_t index;

    for (index = 0; index < count; ++index) {
        const struct publisher_row *row = &rows[index];
        uint32_t sr = publisher_sr(index);
        uint32_t base = TEST_RAM_BASE + (RL_STATE & 0xffffU);

        load_configuration(row->config);
        load_records(row->base, row->ext);
        ram_pointer(APC_MODE_SNAPSHOT)[0] = row->apc;
        snapshot_ram();
        expect_bytes(RL_STATE, row->base_out, RL_STATE_SIZE);
        expect_bytes(RL_EXTENSION, row->ext_out, RL_EXTENSION_SIZE);
        regs[3] = row->r3;
        regs[4] = row->r4;
        regs[5] = control ? base : row->r5;
        if (!call_entry(row->name, entry, sr))
            return 0;
        if ((regs[15] & SR_BITS) != sr)
            return fail_value(row->name, "sr", regs[15], sr);
        if (regs[4] != row->r4)
            return fail_value(row->name, "r4", regs[4], row->r4);
        if (regs[5] != (control ? base : row->r5_out))
            return fail_value(row->name, "r5", regs[5], control ? base : row->r5_out);
        if (!compare_ram(row->name) || !verify_configuration(row->name, row->config))
            return 0;
    }
    return 1;
}

static int run_fraction_rows(void)
{
    size_t index;

    for (index = 0; index < ARRAY_SIZE(fraction_rows); ++index) {
        const struct fraction_row *row = &fraction_rows[index];
        uint32_t r3 = 0xc0de0303U, r6 = 0xc0de0606U, r7 = 0xc0de0707U;

        snapshot_ram();
        regs[3] = r3;
        regs[4] = (uint32_t)row->error;
        regs[5] = row->width;
        if (!call_entry(row->name, RPM_FRACTION, SR_ENGINE))
            return 0;
        if (regs[0] != row->fraction)
            return fail_value(row->name, "fraction", regs[0], row->fraction);
        if (regs[3] != r3 || regs[6] != r6 || regs[7] != r7)
            return fail_value(row->name, "preserved", regs[3] ^ regs[6] ^ regs[7], r3 ^ r6 ^ r7);
        if (regs[4] != (uint32_t)row->error || regs[5] != row->width)
            return fail_value(row->name, "arguments", regs[4], (uint32_t)row->error);
        if ((regs[15] & SR_I_S) != (SR_ENGINE & SR_I_S))
            return fail_value(row->name, "sr", regs[15], SR_ENGINE);
        if (!compare_ram(row->name))
            return 0;
    }
    return 1;
}

/* Startup clears both records, stores the default efficiency and runs the
   map-switching startup wrapper, whose stock initializer is a stub. */
static int run_startup_row(void)
{
    static const char name[] = "wrapper-startup";
    uint8_t cf_startup[CF_STATE_SIZE] = {0};
    uint8_t ee_startup[EE_STATE_SIZE] = {0};
    uint8_t telem_status_startup;
    volatile uint8_t *ee_mem = (volatile uint8_t *)(uintptr_t)M95320_BASE;

    cf_startup[1] = 0xffU;
    cf_startup[2] = 0xffU;
    cf_startup[3] = 0xffU;
    ee_startup[1] = 0xffU;
    ee_startup[3] = 0x01U;
    fill_bytes(ee_startup + 0x28U, 16U, 0xffU);
    fill_bytes(ee_mem + 0x0680U, 32U, 0xffU);
    fill_bytes(ee_mem + 0x0700U, 32U, 0xffU);
    ee_mem[0x1000U] = 0U;
    ee_mem[0x1001U] = 0U;
    ee_mem[0x1002U] = 0U;
    ee_mem[0x1005U] = 0U;
    ee_mem[0x101cU] = 3U;
    write_u16(ram_pointer(PCDR_ADDR), 0x0015U);
    load_configuration(0);
    fill_bytes(ram_pointer(RL_STATE), RL_STATE_SIZE, 0xa5);
    fill_bytes(ram_pointer(RL_EXTENSION), RL_EXTENSION_SIZE, 0xa5);
    load_shadows();
    ram_pointer(SELECTOR_STATE)[0] = 3;
    snapshot_ram();
    telem_status_startup = (uint8_t)(ram_pointer(0xffff5e07U)[0] & 0xcfU);
    expect_bytes(RL_STATE, rl_startup_base, RL_STATE_SIZE);
    expect_bytes(RL_EXTENSION, rl_startup_ext, RL_EXTENSION_SIZE);
    expect_bytes(CF_STATE, cf_startup, CF_STATE_SIZE);
    expect_bytes(EE_STATE, ee_startup, EE_STATE_SIZE);
    expect_bytes(0xffff5e07U, &telem_status_startup, 1U);
    expect_map1_commit();
    regs[3] = regs[5] = 0;
    regs[4] = 0xa5a5a5a5U;
    return call_entry(name, STARTUP_WRAPPER, SR_ENGINE) && compare_ram(name);
}

/* Map selection runs only from IDLE; ACTIVE, COOLDOWN and a corrupt phase
   reach the stock ASCD host stub and change nothing. */
static int run_selector_rows(void)
{
    static const char *const names[] = {
        "wrapper-selector-idle", "wrapper-selector-active",
        "wrapper-selector-cooldown", "wrapper-selector-corrupt",
    };
    size_t phase;

    for (phase = 0; phase < ARRAY_SIZE(names); ++phase) {
        volatile uint8_t *selector = ram_pointer(SELECTOR_STATE);

        load_configuration(0);
        load_records(rl_startup_base, rl_startup_ext);
        ram_pointer(RL_STATE)[0] = (uint8_t)phase;
        fill_bytes(selector, 8U, 0);
        if (phase) {
            selector[0] = 2;
            selector[1] = 1;
            selector[2] = 3;
            selector[3] = 7;
        }
        ram_pointer(BUTTON_CODE)[0] = BUTTON_SET;
        ram_pointer(BUTTON_CODE + 1U)[0] = BUTTON_RELEASED;
        ram_pointer(DIAGNOSTIC_STATUS)[0] = 0xa5;
        ram_pointer(ASCD_STATUS)[0] = 0;
        snapshot_ram();
        if (!phase) {
            /* The map selector host starts the SET gesture, records cruise-free
               arbitration block (reason 6), and mirrors map 1 as a clear bit 7
               of its diagnostic status byte. */
            expected_ram[(SELECTOR_STATE + 1U) & 0xffffU] = 1;
            expected_ram[(SELECTOR_STATE + 3U) & 0xffffU] = 1;
            expected_ram[(CF_STATE + 4U) & 0xffffU] = 0;
            expected_ram[(CF_STATE + 5U) & 0xffffU] = 0;
            expected_ram[(CF_STATE + 8U) & 0xffffU] = 6;
            expected_ram[DIAGNOSTIC_STATUS & 0xffffU] = 0x25;
        }
        regs[3] = regs[4] = regs[5] = 0;
        if (!call_entry(names[phase], SELECTOR_ARBITER, SR_ENGINE) || !compare_ram(names[phase]))
            return 0;
    }
    return 1;
}

struct feedback_case {
    const char *name;
    uint8_t phase;
    uint8_t reason;
    uint16_t flags;
    uint8_t map_feedback[4];
    uint8_t status;
    uint8_t mil_on;
    uint8_t map_feedback_out[4];
};

/* The serializer stub stores 0xb5; Rolling Launch replaces its ASCD field
   0x70. Map feedback drives MIL (0x551 byte 3, bit 5) and preserves byte 5. */
static const struct feedback_case feedback_cases[] = {
    {"feedback-idle-released", 0, 10, 0x0000, {0, 0, 0, 0}, 0xb5, 0, {0, 0, 0, 0}},
    {"feedback-idle-clear-held", 0, 0, 0x0020, {0, 0, 0, 0}, 0xb5, 0, {0, 0, 0, 0}},
    {"feedback-failed-held", 0, 10, 0x0020, {0, 0, 0, 0}, 0xd5, 0, {0, 0, 0, 0}},
    {"feedback-active", 1, 0, 0x1fff, {0, 0, 0, 0}, 0xc5, 0, {0, 0, 0, 0}},
    {"feedback-cooldown", 2, 14, 0x0000, {0, 0, 0, 0}, 0x85, 0, {0, 0, 0, 0}},
    {"feedback-corrupt", 3, 16, 0x0000, {0, 0, 0, 0}, 0xb5, 0, {0, 0, 0, 0}},
    {"feedback-map-on-priority", 0, 10, 0x0020, {1, 1, 0, 0}, 0xb5, 1, {1, 2, 0, 0}},
    {"feedback-map-off-priority", 1, 0, 0x1fff, {1, 2, 0, 0}, 0xb5, 0, {0, 0, 0, 0}},
};

static int run_feedback_rows(void)
{
    static const uint8_t counts[2] = {1, 1};
    size_t index;

    for (index = 0; index < ARRAY_SIZE(feedback_cases); ++index) {
        const struct feedback_case *test = &feedback_cases[index];
        volatile uint8_t *state = ram_pointer(RL_STATE);
        uint8_t status = test->status;

        load_configuration(0);
        fill_bytes(state, RL_STATE_SIZE, 0x5a);
        state[0] = test->phase;
        state[1] = test->reason;
        write_u16(state + 2, test->flags);
        write_bytes(ram_pointer(SELECTOR_STATE + 4U), test->map_feedback, 4U);
        write_bytes(rom_pointer(FEEDBACK_COUNTS), counts, sizeof(counts));
        ram_pointer(PAYLOAD + 3U)[0] = 0x88U;
        snapshot_ram();
        expect_bytes(SELECTOR_STATE + 4U, test->map_feedback_out, 4U);
        expect_bytes(PAYLOAD + 5U, &status, 1U);
        if (test->mil_on) {
            uint8_t mil = (uint8_t)(ram_pointer(PAYLOAD + 3U)[0] | 0x20U);
            expect_bytes(PAYLOAD + 3U, &mil, 1U);
        }
        regs[3] = regs[4] = regs[5] = 0;
        if (!call_entry(test->name, FEEDBACK_ARBITER, SR_ENGINE) || !compare_ram(test->name)
                || !fail_bytes(test->name, "feedback_counts", rom_pointer(FEEDBACK_COUNTS),
                               counts, sizeof(counts)))
            return 0;
    }
    return 1;
}

int main(void)
{
    seed_test_ram();
    if (!run_startup_row() || !run_selector_rows() || !run_engine_rows()
            || !run_publisher_rows(ignition_rows, ARRAY_SIZE(ignition_rows),
                                   IGNITION_PUBLISHER, 0)
            || !run_publisher_rows(control_rows, ARRAY_SIZE(control_rows),
                                   CONTROL_PUBLISHER, 1)
            || !run_fraction_rows() || !run_feedback_rows())
        return 1;
    printf("VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=%lu engine=%lu ignition=%lu "
           "control=%lu fraction=%lu wrappers=5 feedback=%lu\n",
           (unsigned long)case_count, (unsigned long)ARRAY_SIZE(engine_rows),
           (unsigned long)ARRAY_SIZE(ignition_rows), (unsigned long)ARRAY_SIZE(control_rows),
           (unsigned long)ARRAY_SIZE(fraction_rows), (unsigned long)ARRAY_SIZE(feedback_cases));
    return 0;
}
