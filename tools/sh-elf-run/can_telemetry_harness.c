#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#define TEST_RAM_BASE 0x01000000U
#define TELEMETRY_STATE 0xffff5e00U
#define TELEMETRY_ACTIVE_SIZE 0x100U
#define BANK_A 0xffff5e20U
#define BANK_B 0xffff5e78U
#define CONFIG 0x000d4e00U
#define TABLE 0x000d4c00U
#define MAIN_WRAPPER 0x000d4280U
#define KNOCK_WRAPPER 0x000d42b0U
#define STARTUP_WRAPPER 0x000d42f0U
#define CAPTURE 0x000d4340U
#define BUILD_BANK 0x000d4500U
#define REQUEST_PAGE 0x000d4700U
#define SLE1_ISR 0x000d4800U
#define COMPLETION 0x000d4900U
#define HCAN1_INIT_WRAPPER 0x000d4e10U
#define CONTROL_POLL 0x000d4ea0U
#define KNOCK_COUNT 0xffff2142U
#define KNOCK_MASK 0xffff2150U
#define TXPR1 0xffffd820U
#define TXACK1 0xffffd830U
#define ABACK1 0xffffd838U
#define IRR1 0xffffd808U
#define RXPR1 0xffffd840U
#define RFPR1 0xffffd848U
#define MBIMR1 0xffffd850U
#define UMSR1 0xffffd858U
#define MAILBOX_DATA 0xffffdc48U
#define CONTROL_MAILBOX 0xffffdce0U
#define CONTROL_MAILBOX_DATA 0xffffdce8U
#define STOCK_ACTIVITY 0xffffa56fU
#define MAILBOX26_MASK 0x0400U
#define MAILBOX28_MASK 0x1000U
#define MAILBOX31_MASK 0x8000U

static const uint8_t start_command[8] = {
    0x54, 0x45, 0x4c, 0x32, 0x02, 0x01, 0xb6, 0x32,
};

static const uint8_t stop_command[8] = {
    0x54, 0x45, 0x4c, 0x32, 0x02, 0x00, 0xa6, 0x13,
};

extern uint32_t invoke_r4(uint32_t entry, uint32_t argument);
extern uint32_t invoke_r0(uint32_t entry);
extern void invoke_exception_probe(uint32_t *registers);

static size_t case_count;

static const uint8_t configuration[16] = {
    0x43, 0x54, 0x02, 0x01, 0x03, 0x0b, 0x01, 0x00,
    0x06, 0xf0, 0x6f, 0x62, 0x54, 0x45, 0x4c, 0x32,
};

static volatile uint8_t *ram_pointer(uint32_t original)
{
    return (volatile uint8_t *)(uintptr_t)(
        TEST_RAM_BASE + (original & 0xffffU));
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

static void copy_bytes(
    volatile uint8_t *target, const uint8_t *source, size_t size)
{
    size_t index;

    for (index = 0; index < size; ++index)
        target[index] = source[index];
}

static uint16_t read_u16(const volatile uint8_t *source)
{
    return (uint16_t)(((uint16_t)source[0] << 8) | source[1]);
}

static uint32_t read_u32(const volatile uint8_t *source)
{
    return ((uint32_t)source[0] << 24)
        | ((uint32_t)source[1] << 16)
        | ((uint32_t)source[2] << 8)
        | source[3];
}

static void write_u16(volatile uint8_t *target, uint16_t value)
{
    target[0] = (uint8_t)(value >> 8);
    target[1] = (uint8_t)value;
}

static int fail_value(
    const char *name, const char *field, uint32_t actual, uint32_t expected)
{
    printf(
        "VQ_SH_ELF_CAN_TELEMETRY status=FAIL case=%s field=%s "
        "actual=%08lx expected=%08lx\n",
        name, field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}

static int expect_bytes(
    const char *name,
    const char *field,
    const volatile uint8_t *actual,
    const volatile uint8_t *expected,
    size_t size)
{
    size_t index;

    for (index = 0; index < size; ++index) {
        if (actual[index] != expected[index]) {
            printf(
                "VQ_SH_ELF_CAN_TELEMETRY status=FAIL case=%s field=%s "
                "offset=%lu actual=%02x expected=%02x\n",
                name, field, (unsigned long)index,
                (unsigned int)actual[index],
                (unsigned int)expected[index]);
            return 0;
        }
    }
    return 1;
}

static void count_case(void)
{
    ++case_count;
}

static void seed_sources(void)
{
    size_t index;

    for (index = 0; index < 111; ++index) {
        uint32_t address = read_u32(rom_pointer(TABLE + index * 4));
        volatile uint8_t *target =
            (volatile uint8_t *)(uintptr_t)address;
        target[0] = (uint8_t)(0x31U + index * 37U);
    }
}

static void set_configuration(void)
{
    copy_bytes(
        rom_pointer(CONFIG),
        configuration,
        sizeof(configuration));
}

static void reset_case(void)
{
    seed_sources();
    fill_bytes(ram_pointer(TELEMETRY_STATE), TELEMETRY_ACTIVE_SIZE, 0);
    fill_bytes(ram_pointer(BANK_A), 88, 0xa5);
    fill_bytes(ram_pointer(BANK_B), 88, 0xa5);
    set_configuration();
    write_u16(ram_pointer(TXPR1), 0);
    write_u16(ram_pointer(TXACK1), 0);
    write_u16(ram_pointer(ABACK1), 0);
    write_u16(ram_pointer(IRR1), 0);
    write_u16(ram_pointer(RXPR1), 0);
    write_u16(ram_pointer(RFPR1), 0);
    write_u16(ram_pointer(MBIMR1), MAILBOX31_MASK);
    write_u16(ram_pointer(UMSR1), 0);
    fill_bytes(ram_pointer(MAILBOX_DATA), 8, 0);
    fill_bytes(ram_pointer(CONTROL_MAILBOX), 0x14, 0);
    write_u16(ram_pointer(CONTROL_MAILBOX) + 4, 0x0700);
    ram_pointer(STOCK_ACTIVITY)[0] = 0;
}

static void seed_control_command(const uint8_t *payload, uint8_t dlc)
{
    copy_bytes(ram_pointer(CONTROL_MAILBOX_DATA), payload, 8);
    ram_pointer(CONTROL_MAILBOX)[5] = dlc;
    write_u16(ram_pointer(RXPR1), MAILBOX31_MASK);
}

static int verify_bank(const char *name, uint32_t bank, uint8_t context)
{
    volatile uint8_t *state = ram_pointer(TELEMETRY_STATE);
    volatile uint8_t *actual = ram_pointer(bank);
    uint16_t tick = read_u16(state + 8);
    size_t page;
    size_t offset;

    for (page = 0; page < 9; ++page) {
        uint8_t header = (uint8_t)(((tick & 0x0fU) << 4) | page);
        if (actual[page * 8] != header)
            return fail_value(
                name, "page_header", actual[page * 8], header);
        for (offset = 0; offset < 7; ++offset) {
            uint32_t source = read_u32(
                rom_pointer(TABLE + (page * 7 + offset) * 4));
            uint8_t expected =
                ((volatile uint8_t *)(uintptr_t)source)[0];
            if (actual[page * 8 + offset + 1] != expected)
                return fail_value(
                    name, "page_source",
                    actual[page * 8 + offset + 1], expected);
        }
    }
    if (actual[72] != (uint8_t)(((tick & 0x0fU) << 4) | 9U))
        return fail_value(name, "context_9_header", actual[72], 9);
    if (actual[73] != context)
        return fail_value(name, "context_9_tag", actual[73], context);
    for (offset = 0; offset < 6; ++offset) {
        uint32_t source = read_u32(
            rom_pointer(TABLE + (63 + context * 6 + offset) * 4));
        uint8_t expected = ((volatile uint8_t *)(uintptr_t)source)[0];
        if (actual[74 + offset] != expected)
            return fail_value(
                name, "context_9_source", actual[74 + offset], expected);
    }
    if (actual[80] != (uint8_t)(((tick & 0x0fU) << 4) | 10U))
        return fail_value(name, "context_10_header", actual[80], 10);
    if (actual[81] != context)
        return fail_value(name, "context_10_tag", actual[81], context);
    for (offset = 0; offset < 6; ++offset) {
        uint32_t source = read_u32(
            rom_pointer(TABLE + (87 + context * 6 + offset) * 4));
        uint8_t expected = ((volatile uint8_t *)(uintptr_t)source)[0];
        if (actual[82 + offset] != expected)
            return fail_value(
                name, "context_10_source", actual[82 + offset], expected);
    }
    return 1;
}

static int verify_started(
    const char *name, uint8_t active, uint8_t pages, uint32_t bank)
{
    volatile uint8_t *state = ram_pointer(TELEMETRY_STATE);

    if (state[0] != active)
        return fail_value(name, "active_bank", state[0], active);
    if (state[1] != 0)
        return fail_value(name, "pending", state[1], 0);
    if (state[2] != 1)
        return fail_value(name, "busy", state[2], 1);
    if (state[3] != 0)
        return fail_value(name, "page", state[3], 0);
    if (state[4] != pages)
        return fail_value(name, "page_count", state[4], pages);
    if (read_u16(ram_pointer(TXPR1)) != MAILBOX26_MASK)
        return fail_value(
            name, "txpr", read_u16(ram_pointer(TXPR1)), MAILBOX26_MASK);
    return expect_bytes(
        name, "mailbox_page0", ram_pointer(MAILBOX_DATA),
        ram_pointer(bank), 8);
}

static int run_wrapper_cases(void)
{
    size_t index;

    count_case();
    reset_case();
    if (invoke_r0(HCAN1_INIT_WRAPPER) != 1)
        return fail_value("hcan1-init", "stock_result", 0, 1);
    if (read_u16(ram_pointer(CONTROL_MAILBOX)) != 0x6f10)
        return fail_value(
            "hcan1-init", "control_id",
            read_u16(ram_pointer(CONTROL_MAILBOX)), 0x6f10);
    if (read_u16(ram_pointer(CONTROL_MAILBOX) + 4) != 0x0208)
        return fail_value(
            "hcan1-init", "mailbox_control",
            read_u16(ram_pointer(CONTROL_MAILBOX) + 4), 0x0208);
    if ((read_u16(ram_pointer(MBIMR1)) & MAILBOX31_MASK) == 0)
        return fail_value("hcan1-init", "interrupt_mask", 0, 1);
    if (
        read_u16(ram_pointer(RXPR1)) != MAILBOX31_MASK
        || read_u16(ram_pointer(RFPR1)) != MAILBOX31_MASK
        || read_u16(ram_pointer(UMSR1)) != MAILBOX31_MASK)
        return fail_value("hcan1-init", "receive_flag_clear", 0, 1);

    count_case();
    reset_case();
    write_u16(rom_pointer(CONFIG) + 8, 0x07fe);
    if (invoke_r0(HCAN1_INIT_WRAPPER) != 1)
        return fail_value("hcan1-init-high-id", "stock_result", 0, 1);
    if (read_u16(ram_pointer(CONTROL_MAILBOX)) != 0x7ff0)
        return fail_value(
            "hcan1-init-high-id", "control_id",
            read_u16(ram_pointer(CONTROL_MAILBOX)), 0x7ff0);

    count_case();
    reset_case();
    rom_pointer(CONFIG)[10] ^= 1;
    if (invoke_r0(HCAN1_INIT_WRAPPER) != 1)
        return fail_value("hcan1-init-invalid", "stock_result", 0, 1);
    if (read_u16(ram_pointer(CONTROL_MAILBOX) + 4) != 0x0700)
        return fail_value(
            "hcan1-init-invalid", "mailbox_control",
            read_u16(ram_pointer(CONTROL_MAILBOX) + 4), 0x0700);

    count_case();
    reset_case();
    fill_bytes(ram_pointer(0xffff5df0U), 0x120, 0xa5);
    (void)invoke_r4(STARTUP_WRAPPER, 0);
    for (index = 0; index < TELEMETRY_ACTIVE_SIZE; ++index) {
        if (ram_pointer(TELEMETRY_STATE)[index] != 0)
            return fail_value(
                "startup", "active_clear",
                ram_pointer(TELEMETRY_STATE)[index], 0);
    }
    for (index = 0; index < 16; ++index) {
        if (ram_pointer(0xffff5df0U)[index] != 0xa5)
            return fail_value("startup", "lower_guard", index, 0);
        if (ram_pointer(0xffff5f00U)[index] != 0xa5)
            return fail_value("startup", "upper_guard", index, 0);
    }

    count_case();
    reset_case();
    ram_pointer(KNOCK_COUNT)[0] = 0xfe;
    ram_pointer(KNOCK_MASK)[0] = 0x2d;
    (void)invoke_r4(KNOCK_WRAPPER, 0);
    if (ram_pointer(TELEMETRY_STATE)[12] != 0xfe)
        return fail_value(
            "knock", "count", ram_pointer(TELEMETRY_STATE)[12], 0xfe);
    if (ram_pointer(TELEMETRY_STATE)[13] != 0x2d)
        return fail_value(
            "knock", "mask", ram_pointer(TELEMETRY_STATE)[13], 0x2d);

    count_case();
    reset_case();
    (void)invoke_r4(MAIN_WRAPPER, 0);
    if (!verify_started("main-wrapper", 1, 11, BANK_B))
        return 0;
    return 1;
}

enum config_mutation {
    CONFIG_MAGIC,
    CONFIG_VERSION,
    CONFIG_DISABLED,
    CONFIG_ENABLE_INVALID,
    CONFIG_PROFILE_ZERO,
    CONFIG_PROFILE_HIGH,
    CONFIG_PAGE_COUNT,
    CONFIG_DIVISOR,
    CONFIG_RESERVED,
    CONFIG_CAN_ID_ZERO,
    CONFIG_CAN_ID_HIGH,
    CONFIG_CRC,
    CONFIG_INTEGRITY,
};

static void mutate_configuration(enum config_mutation mutation)
{
    volatile uint8_t *config = rom_pointer(CONFIG);

    switch (mutation) {
    case CONFIG_MAGIC:
        config[0] = 0;
        break;
    case CONFIG_VERSION:
        config[2] = 1;
        break;
    case CONFIG_DISABLED:
        config[3] = 0;
        break;
    case CONFIG_ENABLE_INVALID:
        config[3] = 2;
        break;
    case CONFIG_PROFILE_ZERO:
        config[4] = 0;
        break;
    case CONFIG_PROFILE_HIGH:
        config[4] = 2;
        break;
    case CONFIG_PAGE_COUNT:
        config[5] = 10;
        break;
    case CONFIG_DIVISOR:
        config[6] = 0;
        break;
    case CONFIG_RESERVED:
        config[7] = 1;
        break;
    case CONFIG_CAN_ID_ZERO:
        write_u16(config + 8, 0);
        break;
    case CONFIG_CAN_ID_HIGH:
        write_u16(config + 8, 0x07ff);
        break;
    case CONFIG_CRC:
        config[10] ^= 1;
        break;
    case CONFIG_INTEGRITY:
        config[15] ^= 1;
        break;
    }
}

static int run_configuration_cases(void)
{
    enum config_mutation mutation;

    for (mutation = CONFIG_MAGIC; mutation <= CONFIG_INTEGRITY; ++mutation) {
        volatile uint8_t *state;

        count_case();
        reset_case();
        mutate_configuration(mutation);
        (void)invoke_r4(CAPTURE, 0);
        state = ram_pointer(TELEMETRY_STATE);
        if (read_u16(state + 8) != 0 || state[2] != 0)
            return fail_value(
                "config-guard", "state", read_u16(state + 8), 0);
        if (read_u16(ram_pointer(TXPR1)) != 0)
            return fail_value(
                "config-guard", "txpr", read_u16(ram_pointer(TXPR1)), 0);
    }
    return 1;
}

static int run_control_cases(void)
{
    volatile uint8_t *state;

    count_case();
    reset_case();
    rom_pointer(CONFIG)[3] = 0;
    seed_control_command(start_command, 8);
    (void)invoke_r4(CONTROL_POLL, 0);
    state = ram_pointer(TELEMETRY_STATE);
    if (state[11] != 1 || state[10] != 0)
        return fail_value("control-start-disabled", "override", state[11], 1);
    (void)invoke_r4(CAPTURE, 0);
    if (!verify_started("control-start-disabled", 1, 11, BANK_B))
        return 0;
    if (read_u16(state + 8) != 1)
        return fail_value(
            "control-start-disabled", "tick", read_u16(state + 8), 1);

    count_case();
    reset_case();
    state = ram_pointer(TELEMETRY_STATE);
    state[1] = 1;
    state[10] = 0x7f;
    seed_control_command(stop_command, 8);
    (void)invoke_r4(CONTROL_POLL, 0);
    if (state[11] != 2 || state[1] != 0 || state[10] != 0)
        return fail_value("control-stop-enabled", "override", state[11], 2);
    (void)invoke_r4(CAPTURE, 0);
    if (
        read_u16(state + 8) != 0
        || state[2] != 0
        || read_u16(ram_pointer(TXPR1)) != 0)
        return fail_value(
            "control-stop-enabled", "capture_state",
            read_u16(state + 8), 0);

    count_case();
    reset_case();
    rom_pointer(CONFIG)[3] = 0;
    rom_pointer(CONFIG)[6] = 4;
    seed_control_command(start_command, 8);
    (void)invoke_r4(CONTROL_POLL, 0);
    state = ram_pointer(TELEMETRY_STATE);
    if (state[10] != 3)
        return fail_value("control-start-divider", "divider", state[10], 3);
    (void)invoke_r4(CAPTURE, 0);
    if (!verify_started("control-start-divider", 1, 11, BANK_B))
        return 0;
    if (read_u16(state + 8) != 1 || state[10] != 0)
        return fail_value(
            "control-start-divider", "tick", read_u16(state + 8), 1);

    count_case();
    reset_case();
    seed_control_command(start_command, 8);
    ram_pointer(CONTROL_MAILBOX_DATA)[7] ^= 1;
    (void)invoke_r4(CONTROL_POLL, 0);
    if (ram_pointer(TELEMETRY_STATE)[11] != 0)
        return fail_value(
            "control-invalid-payload", "override",
            ram_pointer(TELEMETRY_STATE)[11], 0);

    count_case();
    reset_case();
    seed_control_command(start_command, 7);
    (void)invoke_r4(CONTROL_POLL, 0);
    if (ram_pointer(TELEMETRY_STATE)[11] != 0)
        return fail_value(
            "control-invalid-dlc", "override",
            ram_pointer(TELEMETRY_STATE)[11], 0);

    count_case();
    reset_case();
    write_u16(ram_pointer(RFPR1), MAILBOX31_MASK);
    (void)invoke_r4(CONTROL_POLL, 0);
    if (ram_pointer(TELEMETRY_STATE)[11] != 0)
        return fail_value(
            "control-remote-only", "override",
            ram_pointer(TELEMETRY_STATE)[11], 0);

    count_case();
    reset_case();
    seed_control_command(start_command, 8);
    write_u16(ram_pointer(RFPR1), MAILBOX31_MASK);
    write_u16(ram_pointer(CONTROL_MAILBOX), 0x6f18);
    (void)invoke_r4(CONTROL_POLL, 0);
    if (ram_pointer(TELEMETRY_STATE)[11] != 0)
        return fail_value(
            "control-retained-remote", "override",
            ram_pointer(TELEMETRY_STATE)[11], 0);

    count_case();
    reset_case();
    rom_pointer(CONFIG)[10] ^= 1;
    seed_control_command(start_command, 8);
    (void)invoke_r4(CONTROL_POLL, 0);
    if (ram_pointer(TELEMETRY_STATE)[11] != 0)
        return fail_value(
            "control-invalid-config", "override",
            ram_pointer(TELEMETRY_STATE)[11], 0);
    if (read_u16(ram_pointer(RXPR1)) != MAILBOX31_MASK)
        return fail_value(
            "control-invalid-config", "rxpr",
            read_u16(ram_pointer(RXPR1)), MAILBOX31_MASK);

    count_case();
    reset_case();
    (void)invoke_r4(CAPTURE, 0);
    (void)invoke_r4(CAPTURE, 0);
    state = ram_pointer(TELEMETRY_STATE);
    if (state[2] != 1 || state[1] != 1)
        return fail_value("control-stop-busy", "precondition", state[1], 1);
    seed_control_command(stop_command, 8);
    (void)invoke_r4(CONTROL_POLL, 0);
    if (state[11] != 2 || state[1] != 0 || state[2] != 1)
        return fail_value("control-stop-busy", "queue", state[1], 0);
    write_u16(ram_pointer(TXACK1), MAILBOX26_MASK);
    write_u16(ram_pointer(ABACK1), 0);
    (void)invoke_r4(COMPLETION, 0);
    if (state[2] != 1 || state[3] != 1)
        return fail_value("control-stop-busy", "completion", state[3], 1);

    return 1;
}

static int run_capture_cases(void)
{
    volatile uint8_t *state;

    count_case();
    reset_case();
    write_u16(rom_pointer(CONFIG) + 8, 1);
    write_u16(ram_pointer(TELEMETRY_STATE) + 8, 0x121f);
    (void)invoke_r4(CAPTURE, 0);
    if (!verify_started("low-id", 1, 11, BANK_B))
        return 0;
    if (!verify_bank("low-id", BANK_B, 0))
        return 0;

    count_case();
    reset_case();
    write_u16(rom_pointer(CONFIG) + 8, 0x07fe);
    (void)invoke_r4(CAPTURE, 0);
    if (!verify_started("high-id", 1, 11, BANK_B))
        return 0;
    if (!verify_bank("high-id", BANK_B, 0))
        return 0;

    count_case();
    reset_case();
    rom_pointer(CONFIG)[6] = 3;
    (void)invoke_r4(CAPTURE, 0);
    (void)invoke_r4(CAPTURE, 0);
    state = ram_pointer(TELEMETRY_STATE);
    if (read_u16(state + 8) != 2 || state[10] != 2 || state[2] != 0)
        return fail_value("divider-wait", "state", state[10], 2);

    count_case();
    (void)invoke_r4(CAPTURE, 0);
    if (!verify_started("divider-due", 1, 11, BANK_B))
        return 0;
    if (read_u16(state + 8) != 3 || state[10] != 0)
        return fail_value("divider-due", "tick", read_u16(state + 8), 3);

    count_case();
    reset_case();
    write_u16(ram_pointer(TELEMETRY_STATE) + 8, 0xffff);
    (void)invoke_r4(CAPTURE, 0);
    if (read_u16(ram_pointer(TELEMETRY_STATE) + 8) != 0)
        return fail_value("tick-wrap", "tick", 1, 0);

    count_case();
    reset_case();
    (void)invoke_r4(CAPTURE, 0);
    ram_pointer(0xffff11f4U)[0] = 0x12;
    ram_pointer(0xffff11f4U)[1] = 0x34;
    (void)invoke_r4(CAPTURE, 0);
    state = ram_pointer(TELEMETRY_STATE);
    if (state[1] != 1 || state[0] != 1)
        return fail_value("pending", "publication", state[1], 1);
    if (!verify_bank("pending", BANK_A, 1))
        return 0;

    count_case();
    ram_pointer(0xffff11f4U)[0] = 0xab;
    ram_pointer(0xffff11f4U)[1] = 0xcd;
    (void)invoke_r4(CAPTURE, 0);
    if (state[7] != 1 || state[14] != 1)
        return fail_value("latest-wins", "overrun", state[14], 1);
    if (ram_pointer(BANK_A)[3] != 0xab || ram_pointer(BANK_A)[4] != 0xcd)
        return fail_value("latest-wins", "newest", 0, 0xabcd);

    count_case();
    state[14] = 0xff;
    (void)invoke_r4(CAPTURE, 0);
    if (state[14] != 0xff)
        return fail_value("overrun-saturates", "counter", state[14], 0xff);

    count_case();
    reset_case();
    state = ram_pointer(TELEMETRY_STATE);
    state[0] = 1;
    (void)invoke_r4(CAPTURE, 0);
    if (!verify_started("idle-bank-a", 0, 11, BANK_A))
        return 0;

    count_case();
    reset_case();
    state = ram_pointer(TELEMETRY_STATE);
    state[0] = 0;
    state[2] = 1;
    (void)invoke_r4(CAPTURE, 0);
    if (state[1] != 1 || !verify_bank("busy-bank-b", BANK_B, 0))
        return fail_value("busy-bank-b", "pending", state[1], 1);
    return 1;
}

static int run_direct_entry_cases(void)
{
    volatile uint8_t *state;
    uint8_t context;

    for (context = 0; context < 4; ++context) {
        count_case();
        reset_case();
        state = ram_pointer(TELEMETRY_STATE);
        state[6] = context;
        write_u16(state + 8, (uint16_t)(0x1000U + context));
        (void)invoke_r4(BUILD_BANK, (uint32_t)(uintptr_t)ram_pointer(BANK_A));
        if (!verify_bank("direct-build", BANK_A, context))
            return 0;
        if (state[6] != (uint8_t)((context + 1) & 3))
            return fail_value(
                "direct-build", "context_next", state[6],
                (uint8_t)((context + 1) & 3));
    }

    count_case();
    reset_case();
    state = ram_pointer(TELEMETRY_STATE);
    state[6] = 0xff;
    (void)invoke_r4(BUILD_BANK, (uint32_t)(uintptr_t)ram_pointer(BANK_A));
    if (!verify_bank("direct-build-invalid-context", BANK_A, 0))
        return 0;
    if (state[6] != 1)
        return fail_value(
            "direct-build-invalid-context", "context_next", state[6], 1);

    count_case();
    reset_case();
    state = ram_pointer(TELEMETRY_STATE);
    state[0] = 0;
    state[3] = 10;
    fill_bytes(ram_pointer(BANK_A), 88, 0x77);
    (void)invoke_r4(REQUEST_PAGE, 0);
    if (!expect_bytes(
            "request-a", "mailbox", ram_pointer(MAILBOX_DATA),
            ram_pointer(BANK_A) + 80, 8))
        return 0;

    count_case();
    reset_case();
    state = ram_pointer(TELEMETRY_STATE);
    state[0] = 1;
    state[3] = 4;
    fill_bytes(ram_pointer(BANK_B), 88, 0x44);
    (void)invoke_r4(REQUEST_PAGE, 0);
    if (!expect_bytes(
            "request-b", "mailbox", ram_pointer(MAILBOX_DATA),
            ram_pointer(BANK_B) + 32, 8))
        return 0;
    return 1;
}

static void signal_ack(uint16_t mask)
{
    write_u16(ram_pointer(TXACK1), mask);
    write_u16(ram_pointer(ABACK1), 0);
}

static void signal_abort(uint16_t mask)
{
    write_u16(ram_pointer(TXACK1), 0);
    write_u16(ram_pointer(ABACK1), mask);
}

static int run_completion_cases(void)
{
    volatile uint8_t *state;
    size_t page;

    count_case();
    reset_case();
    state = ram_pointer(TELEMETRY_STATE);
    state[7] = 0x0f;
    (void)invoke_r4(CAPTURE, 0);
    for (page = 1; page < 11; ++page) {
        signal_ack(MAILBOX26_MASK);
        (void)invoke_r4(COMPLETION, 0);
        if (state[3] != page)
            return fail_value("ack-sequence", "page", state[3], page);
        if (!expect_bytes(
                "ack-sequence", "mailbox", ram_pointer(MAILBOX_DATA),
                ram_pointer(BANK_B) + page * 8, 8))
            return 0;
    }
    signal_ack(MAILBOX26_MASK);
    (void)invoke_r4(COMPLETION, 0);
    if (state[2] != 0 || state[3] != 0 || state[7] != 0)
        return fail_value("ack-sequence", "done", state[7], 0);

    count_case();
    reset_case();
    (void)invoke_r4(CAPTURE, 0);
    (void)invoke_r4(CAPTURE, 0);
    state = ram_pointer(TELEMETRY_STATE);
    signal_ack(MAILBOX26_MASK);
    (void)invoke_r4(COMPLETION, 0);
    if (state[0] != 0 || state[1] != 0 || state[3] != 0 || state[7] != 8)
        return fail_value("ack-preempt", "state", state[7], 8);
    if (!expect_bytes(
            "ack-preempt", "mailbox", ram_pointer(MAILBOX_DATA),
            ram_pointer(BANK_A), 8))
        return 0;

    count_case();
    reset_case();
    state = ram_pointer(TELEMETRY_STATE);
    state[0] = 0;
    state[1] = 1;
    state[2] = 1;
    state[3] = 10;
    state[4] = 11;
    signal_ack(MAILBOX26_MASK);
    (void)invoke_r4(COMPLETION, 0);
    if (state[0] != 1 || state[7] != 0)
        return fail_value("ack-last-pending", "status", state[7], 0);

    count_case();
    reset_case();
    state = ram_pointer(TELEMETRY_STATE);
    state[0] = 0;
    state[2] = 1;
    state[3] = 10;
    state[4] = 11;
    ram_pointer(BANK_A)[31] = 0x03;
    state[7] = 0x0f;
    signal_ack(MAILBOX26_MASK);
    (void)invoke_r4(COMPLETION, 0);
    if (state[7] != 0x0c)
        return fail_value("status-bank-a", "status", state[7], 0x0c);

    count_case();
    reset_case();
    state = ram_pointer(TELEMETRY_STATE);
    state[2] = 1;
    state[4] = 11;
    signal_ack(0);
    (void)invoke_r4(COMPLETION, 0);
    if (state[2] != 1)
        return fail_value("completion-no-flags", "busy", state[2], 1);

    for (page = 0; page < 4; ++page) {
        count_case();
        reset_case();
        state = ram_pointer(TELEMETRY_STATE);
        state[2] = 1;
        state[4] = 11;
        if (page == 0)
            state[0] = 2;
        else if (page == 1)
            state[1] = 2;
        else if (page == 2)
            state[4] = 10;
        else
            state[3] = 11;
        signal_ack(MAILBOX26_MASK);
        (void)invoke_r4(COMPLETION, 0);
        if (state[1] != 0 || state[2] != 0 || state[3] != 0)
            return fail_value("queue-corrupt", "busy", state[2], 0);
    }
    return 1;
}

static int run_abort_cases(void)
{
    volatile uint8_t *state;

    count_case();
    reset_case();
    (void)invoke_r4(CAPTURE, 0);
    state = ram_pointer(TELEMETRY_STATE);
    signal_abort(MAILBOX26_MASK);
    (void)invoke_r4(COMPLETION, 0);
    if (state[2] != 0 || state[7] != 2 || state[15] != 1)
        return fail_value("abort-idle", "state", state[15], 1);

    count_case();
    reset_case();
    (void)invoke_r4(CAPTURE, 0);
    (void)invoke_r4(CAPTURE, 0);
    state = ram_pointer(TELEMETRY_STATE);
    signal_abort(MAILBOX26_MASK);
    (void)invoke_r4(COMPLETION, 0);
    if (state[0] != 0 || state[1] != 0 || state[2] != 1 || state[3] != 0)
        return fail_value("abort-pending", "busy", state[2], 1);

    count_case();
    reset_case();
    (void)invoke_r4(CAPTURE, 0);
    state = ram_pointer(TELEMETRY_STATE);
    state[15] = 0xff;
    signal_abort(MAILBOX26_MASK);
    (void)invoke_r4(COMPLETION, 0);
    if (state[15] != 0xff)
        return fail_value("abort-saturates", "counter", state[15], 0xff);
    return 1;
}

static int verify_registers(const char *name, const uint32_t *registers)
{
    size_t index;

    for (index = 0; index < 8; ++index) {
        if (registers[index] != index + 1)
            return fail_value(
                name, "register", registers[index], (uint32_t)index + 1);
    }
    return 1;
}

static int run_isr_case(
    const char *name, uint16_t txack, uint16_t aback, int busy)
{
    uint32_t registers[8] = {0};
    volatile uint8_t *state;

    count_case();
    reset_case();
    state = ram_pointer(TELEMETRY_STATE);
    state[2] = (uint8_t)busy;
    state[4] = 11;
    write_u16(ram_pointer(TXACK1), txack);
    write_u16(ram_pointer(ABACK1), aback);
    invoke_exception_probe(registers);
    if (!verify_registers(name, registers))
        return 0;
#ifndef TELEMETRY_TAIL_CHAIN
    if ((txack | aback) & MAILBOX28_MASK) {
        if (ram_pointer(STOCK_ACTIVITY)[0] != 0xff)
            return fail_value(
                name, "stock_activity", ram_pointer(STOCK_ACTIVITY)[0], 0xff);
    }
#endif
    if (((txack | aback) & MAILBOX26_MASK) != 0
            && read_u16(ram_pointer(IRR1)) != 0x0100)
        return fail_value(
            name, "irr", read_u16(ram_pointer(IRR1)), 0x0100);
    return 1;
}

static int run_isr_cases(void)
{
    if (!run_isr_case("isr-none", 0, 0, 0))
        return 0;
    if (!run_isr_case("isr-stock-ack", MAILBOX28_MASK, 0, 0))
        return 0;
    if (!run_isr_case("isr-stock-abort", 0, MAILBOX28_MASK, 0))
        return 0;
    if (!run_isr_case(
            "isr-simultaneous-ack",
            MAILBOX26_MASK, MAILBOX28_MASK, 1))
        return 0;
    if (!run_isr_case(
            "isr-simultaneous-abort", MAILBOX28_MASK,
            MAILBOX26_MASK, 1))
        return 0;
    return 1;
}

int main(void)
{
    if (!run_wrapper_cases())
        return 1;
    if (!run_configuration_cases())
        return 1;
    if (!run_control_cases())
        return 1;
    if (!run_capture_cases())
        return 1;
    if (!run_direct_entry_cases())
        return 1;
    if (!run_completion_cases())
        return 1;
    if (!run_abort_cases())
        return 1;
    if (!run_isr_cases())
        return 1;
    printf(
        "VQ_SH_ELF_CAN_TELEMETRY status=PASS cases=%lu entries=10 "
        "profiles=1 contexts=8 isr_rte=5\n",
        (unsigned long)case_count);
    return 0;
}
