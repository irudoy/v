#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "can-telemetry-identity.h"

#define TEST_RAM_BASE 0x01000000U
#define TELEMETRY_STATE 0xffff5e00U
#define TELEMETRY_ACTIVE_SIZE 0x190U
#define DYNAMIC_STATE 0xffff5f00U
#define DYNAMIC_WINDOW_START 0x00ff0000U
#define DYNAMIC_WINDOW_END 0x00ffc000U
#define BANK_A 0xffff5e20U
#define BANK_B 0xffff5e78U
#define CONFIG 0x000d4e00U
#define TABLE 0x000d4c00U
#define MAIN_WRAPPER 0x000d4280U
#define KNOCK_WRAPPER 0x000d42b0U
#define STARTUP_WRAPPER 0x000d42f0U
/* The Map Switching selector state, which the Map Switching startup wrapper
   at the base of the startup chain clears. */
#define MAP_SELECTOR_STATE 0xffff5d00U
#define CAPTURE 0x000d4340U
#define BUILD_BANK 0x000d4500U
#define KNOCK_MARGIN_WRAPPER 0x000d4600U
#define REQUEST_PAGE 0x000d4700U
#define SLE1_ISR 0x000d4800U
#define COMPLETION 0x000d4900U
#define HCAN1_INIT_WRAPPER 0x000d4e10U
#define CONTROL_POLL 0x000d4ea0U
#define KNOCK_COUNT 0xffff2142U
#define KNOCK_MASK 0xffff2150U
#define KNOCK_SELECTOR 0x00008b3dU
#define KNOCK_CHANNEL_PRIMARY 0xffff11deU
#define KNOCK_CHANNEL_ALTERNATE 0xffff2143U
#define KNOCK_METRIC 0xffff21d8U
#define KNOCK_THRESHOLD 0xffff2144U
#define KNOCK_MARGIN_STATE 16U
#define KNOCK_MARGIN_IDLE 32767U
#define EVALUATOR_STAGE 0x0100ff00U
#define TXPR1 0xffffd820U
#define TXACK1 0xffffd830U
#define ABACK1 0xffffd838U
#define IRR1 0xffffd808U
#define RXPR1 0xffffd840U
#define RFPR1 0xffffd848U
#define MBIMR1 0xffffd850U
#define UMSR1 0xffffd858U
#define MAILBOX_DATA 0xffffdc48U
#ifdef TARGET_1ME3B
#define CONTROL_MAILBOX 0xffffdbc0U
#define CONTROL_MAILBOX_DATA 0xffffdbc8U
#define CONTROL_MAILBOX_MASK 0x0040U
#else
#define CONTROL_MAILBOX 0xffffdce0U
#define CONTROL_MAILBOX_DATA 0xffffdce8U
#define CONTROL_MAILBOX_MASK 0x8000U
#endif
#define STOCK_ACTIVITY 0xffffa56fU
#define MAILBOX26_MASK 0x0400U
#define MAILBOX28_MASK 0x1000U
/* The one-bit fields: their table slot, bank byte, and wire bit, which the
   hosts decode, and the source bit of the layout. The capture of a layout
   that keeps the bit elsewhere moves it into the wire bit and clears the
   other bits of the wire byte. The LTFT neutral control field lies on the
   dynamic page and moves only while the page carries its default row. */
#define LTFT_NEUTRAL_SLOT 23U
#define LTFT_NEUTRAL_BYTE 27U
#define LTFT_NEUTRAL_WIRE 0x01U
#define KNOCK_BRANCH_SLOT 29U
#define KNOCK_BRANCH_BYTE 34U
#define KNOCK_BRANCH_WIRE 0x80U
#define KNOCK_SURFACE_SLOT 32U
#define KNOCK_SURFACE_BYTE 37U
#define KNOCK_SURFACE_WIRE 0x40U
#if defined(TARGET_1EK7A)
#define LTFT_NEUTRAL_SOURCE 0x20U
#define KNOCK_BRANCH_SOURCE 0x80U
#define KNOCK_SURFACE_SOURCE 0x80U
#elif defined(TARGET_1ME3B)
#define LTFT_NEUTRAL_SOURCE 0x04U
#define KNOCK_BRANCH_SOURCE 0x80U
#define KNOCK_SURFACE_SOURCE 0x80U
#elif defined(TARGET_1ND)
#define LTFT_NEUTRAL_SOURCE 0x80U
#define KNOCK_BRANCH_SOURCE 0x40U
#define KNOCK_SURFACE_SOURCE 0x40U
#elif defined(TARGET_JK78)
#define LTFT_NEUTRAL_SOURCE 0x40U
#define KNOCK_BRANCH_SOURCE 0x40U
#define KNOCK_SURFACE_SOURCE 0x40U
#else
#define LTFT_NEUTRAL_SOURCE 0x01U
#define KNOCK_BRANCH_SOURCE 0x80U
#define KNOCK_SURFACE_SOURCE 0x40U
#endif

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
static uint8_t margin_snapshot[12];
/* Expected bytes 1..7 of the dynamic page under a dynamic configuration. */
static const uint8_t *dynamic_page;

static const uint8_t configuration[16] = TELEMETRY_CONFIGURATION;

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

    for (index = 0; index < 123; ++index) {
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
    write_u16(ram_pointer(MBIMR1), CONTROL_MAILBOX_MASK);
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
    write_u16(ram_pointer(RXPR1), CONTROL_MAILBOX_MASK);
}

#ifdef TARGET_1ME3B
static int run_stock_receive_preservation_cases(void)
{
    static const uint8_t stock_mailbox31[0x14] = {
        0x29, 0x20, 0x00, 0x00, 0x02, 0x08, 0x00, 0x00,
        0x91, 0x82, 0x73, 0x64, 0x55, 0x46, 0x37, 0x28,
        0x00, 0x00, 0x00, 0x00,
    };
    /* This stock address is independent of the control mailbox allocation. */
    volatile uint8_t *stock = ram_pointer(0xffffdce0U);

    count_case();
    reset_case();
    copy_bytes(stock, stock_mailbox31, sizeof(stock_mailbox31));
    write_u16(ram_pointer(MBIMR1), 0x8000U);
    (void)invoke_r0(HCAN1_INIT_WRAPPER);
    if (!expect_bytes("stock-rx-init", "mailbox31", stock,
            stock_mailbox31, sizeof(stock_mailbox31)))
        return 0;
    if (read_u16(ram_pointer(MBIMR1)) != 0x8040U)
        return fail_value("stock-rx-init", "interrupt_mask",
            read_u16(ram_pointer(MBIMR1)), 0x8040U);

    count_case();
    seed_control_command(start_command, 8);
    (void)invoke_r4(CONTROL_POLL, 0);
    if (ram_pointer(TELEMETRY_STATE)[11] != 1)
        return fail_value("stock-rx-start", "override",
            ram_pointer(TELEMETRY_STATE)[11], 1);
    if (!expect_bytes("stock-rx-start", "mailbox31", stock,
            stock_mailbox31, sizeof(stock_mailbox31)))
        return 0;

    count_case();
    seed_control_command(stop_command, 8);
    (void)invoke_r4(CONTROL_POLL, 0);
    if (ram_pointer(TELEMETRY_STATE)[11] != 2)
        return fail_value("stock-rx-stop", "override",
            ram_pointer(TELEMETRY_STATE)[11], 2);
    if (!expect_bytes("stock-rx-stop", "mailbox31", stock,
            stock_mailbox31, sizeof(stock_mailbox31)))
        return 0;

    count_case();
    seed_control_command(start_command, 7);
    (void)invoke_r4(CONTROL_POLL, 0);
    if (ram_pointer(TELEMETRY_STATE)[11] != 2)
        return fail_value("stock-rx-invalid", "override",
            ram_pointer(TELEMETRY_STATE)[11], 2);
    if (!expect_bytes("stock-rx-invalid", "mailbox31", stock,
            stock_mailbox31, sizeof(stock_mailbox31)))
        return 0;
    if (read_u16(ram_pointer(RXPR1)) != 0x0040U
            || read_u16(ram_pointer(RFPR1)) != 0x0040U
            || read_u16(ram_pointer(UMSR1)) != 0x0040U)
        return fail_value("stock-rx-invalid", "control_ack", 0, 1);

    count_case();
    seed_control_command(start_command, 8);
    write_u16(ram_pointer(RXPR1), 0x8000U);
    /* Model the previous write-one-to-clear acknowledgment in plain memory. */
    write_u16(ram_pointer(RFPR1), 0);
    (void)invoke_r4(CONTROL_POLL, 0);
    if (ram_pointer(TELEMETRY_STATE)[11] != 2)
        return fail_value("stock-rx-pending", "override",
            ram_pointer(TELEMETRY_STATE)[11], 2);
    if (read_u16(ram_pointer(RXPR1)) != 0x8000U)
        return fail_value("stock-rx-pending", "receive_pending",
            read_u16(ram_pointer(RXPR1)), 0x8000U);
    if (read_u16(ram_pointer(RFPR1)) != 0)
        return fail_value("stock-rx-pending", "remote_pending",
            read_u16(ram_pointer(RFPR1)), 0);
    if (!expect_bytes("stock-rx-pending", "mailbox31", stock,
            stock_mailbox31, sizeof(stock_mailbox31)))
        return 0;

    count_case();
    write_u16(ram_pointer(CONTROL_MAILBOX) + 4, 0x0700);
    (void)invoke_r0(HCAN1_INIT_WRAPPER);
    if (read_u16(ram_pointer(CONTROL_MAILBOX)) != 0x6f10
            || read_u16(ram_pointer(CONTROL_MAILBOX) + 4) != 0x0208)
        return fail_value("stock-rx-recovery", "control_restore", 0, 1);
    return expect_bytes("stock-rx-recovery", "mailbox31", stock,
        stock_mailbox31, sizeof(stock_mailbox31));
}
#endif

static const struct {
    const char *bit_case;
    const char *other_case;
    size_t slot;
    size_t byte;
    uint8_t source;
    uint8_t wire;
} bit_fields[] = {
    {
        "ltft-neutral-bit", "ltft-neutral-other-bits",
        LTFT_NEUTRAL_SLOT, LTFT_NEUTRAL_BYTE,
        LTFT_NEUTRAL_SOURCE, LTFT_NEUTRAL_WIRE,
    },
    {
        "knock-branch-inhibit", "knock-branch-other-bits",
        KNOCK_BRANCH_SLOT, KNOCK_BRANCH_BYTE,
        KNOCK_BRANCH_SOURCE, KNOCK_BRANCH_WIRE,
    },
    {
        "knock-surface-high-detonation", "knock-surface-other-bits",
        KNOCK_SURFACE_SLOT, KNOCK_SURFACE_BYTE,
        KNOCK_SURFACE_SOURCE, KNOCK_SURFACE_WIRE,
    },
};

/* The wire byte of a fixed page slot whose source byte the capture read. */
static uint8_t wire_byte(size_t slot, uint8_t source)
{
    size_t index;

    for (index = 0; index < sizeof(bit_fields) / sizeof(bit_fields[0]);
            ++index) {
        if (bit_fields[index].slot != slot
                || bit_fields[index].source == bit_fields[index].wire)
            continue;
        return (source & bit_fields[index].source) != 0
            ? bit_fields[index].wire
            : 0U;
    }
    return source;
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
            uint8_t expected = wire_byte(
                page * 7 + offset,
                ((volatile uint8_t *)(uintptr_t)source)[0]);
            if (page == TELEMETRY_DYNAMIC_PAGE && dynamic_page != NULL)
                expected = dynamic_page[offset];
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
        uint8_t expected = context == 4
            ? margin_snapshot[offset]
            : ((volatile uint8_t *)(uintptr_t)source)[0];
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
            rom_pointer(TABLE + (93 + context * 6 + offset) * 4));
        uint8_t expected = context == 4
            ? margin_snapshot[6 + offset]
            : ((volatile uint8_t *)(uintptr_t)source)[0];
        if (actual[82 + offset] != expected)
            return fail_value(
                name, "context_10_source", actual[82 + offset], expected);
    }
    /* The default configuration carries configuration byte 0, independent
       of the source-pointer table used by the generic capture comparison. */
    if (dynamic_page == NULL
            && actual[TELEMETRY_DYNAMIC_PAGE * 8
                + TELEMETRY_DYNAMIC_CONFIGURATION_OFFSET] != 0)
        return fail_value(name, "default_configuration",
            actual[TELEMETRY_DYNAMIC_PAGE * 8
                + TELEMETRY_DYNAMIC_CONFIGURATION_OFFSET], 0);
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
    if ((read_u16(ram_pointer(MBIMR1)) & CONTROL_MAILBOX_MASK) == 0)
        return fail_value("hcan1-init", "interrupt_mask", 0, 1);
    if (
        read_u16(ram_pointer(RXPR1)) != CONTROL_MAILBOX_MASK
        || read_u16(ram_pointer(RFPR1)) != CONTROL_MAILBOX_MASK
        || read_u16(ram_pointer(UMSR1)) != CONTROL_MAILBOX_MASK)
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
    fill_bytes(ram_pointer(0xffff5df0U), 0x1b0, 0xa5);
    ram_pointer(MAP_SELECTOR_STATE)[0] = 0xa5;
    (void)invoke_r4(STARTUP_WRAPPER, 0);
    if (ram_pointer(MAP_SELECTOR_STATE)[0] != 0)
        return fail_value(
            "startup", "map_selector_clear",
            ram_pointer(MAP_SELECTOR_STATE)[0], 0);
    for (index = 0; index < TELEMETRY_ACTIVE_SIZE; ++index) {
        uint8_t expected = 0;

        if (index >= KNOCK_MARGIN_STATE && index < KNOCK_MARGIN_STATE + 12)
            expected = (index & 1U) ? 0xff : 0x7f;
        if (ram_pointer(TELEMETRY_STATE)[index] != expected)
            return fail_value(
                "startup", "active_clear",
                ram_pointer(TELEMETRY_STATE)[index], expected);
    }
    for (index = 0; index < 16; ++index) {
        if (ram_pointer(0xffff5df0U)[index] != 0xa5)
            return fail_value("startup", "lower_guard", index, 0);
        if (ram_pointer(0xffff5f90U)[index] != 0xa5)
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
    if (!verify_started("main-wrapper", 1, TELEMETRY_PAGE_COUNT, BANK_B))
        return 0;
    return 1;
}

enum config_mutation {
    CONFIG_MAGIC,
    CONFIG_VERSION,
    CONFIG_DISABLED,
    CONFIG_ENABLE_INVALID,
    CONFIG_PROFILE_ZERO,
    CONFIG_PROFILE_PREVIOUS,
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
    case CONFIG_PROFILE_PREVIOUS:
        config[4] = TELEMETRY_PROFILE_ID - 1;
        break;
    case CONFIG_PROFILE_HIGH:
        config[4] = TELEMETRY_PROFILE_ID + 1;
        break;
    case CONFIG_PAGE_COUNT:
        config[5] = TELEMETRY_PAGE_COUNT - 1;
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
    if (!verify_started(
            "control-start-disabled", 1, TELEMETRY_PAGE_COUNT, BANK_B))
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
    if (!verify_started(
            "control-start-divider", 1, TELEMETRY_PAGE_COUNT, BANK_B))
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
    seed_control_command(start_command, 8);
    ram_pointer(CONTROL_MAILBOX_DATA)[0] ^= 1;
    (void)invoke_r4(CONTROL_POLL, 0);
    if (ram_pointer(TELEMETRY_STATE)[11] != 0)
        return fail_value(
            "control-invalid-magic", "override",
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
    write_u16(ram_pointer(RFPR1), CONTROL_MAILBOX_MASK);
    (void)invoke_r4(CONTROL_POLL, 0);
    if (ram_pointer(TELEMETRY_STATE)[11] != 0)
        return fail_value(
            "control-remote-only", "override",
            ram_pointer(TELEMETRY_STATE)[11], 0);

    count_case();
    reset_case();
    seed_control_command(start_command, 8);
    write_u16(ram_pointer(RFPR1), CONTROL_MAILBOX_MASK);
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
    if (read_u16(ram_pointer(RXPR1)) != CONTROL_MAILBOX_MASK)
        return fail_value(
            "control-invalid-config", "rxpr",
            read_u16(ram_pointer(RXPR1)), CONTROL_MAILBOX_MASK);

    count_case();
    reset_case();
    rom_pointer(CONFIG)[4] = TELEMETRY_PROFILE_ID - 1;
    seed_control_command(start_command, 8);
    (void)invoke_r4(CONTROL_POLL, 0);
    if (ram_pointer(TELEMETRY_STATE)[11] != 0)
        return fail_value(
            "control-previous-profile", "override",
            ram_pointer(TELEMETRY_STATE)[11], 0);
    if (read_u16(ram_pointer(RXPR1)) != CONTROL_MAILBOX_MASK)
        return fail_value(
            "control-previous-profile", "rxpr",
            read_u16(ram_pointer(RXPR1)), CONTROL_MAILBOX_MASK);

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

#if defined(VERIFY_7MFK_CAN_CONTROL) || defined(MEASURE_CAN_TELEMETRY)
#define CONTROL_STATE_GUARD (TELEMETRY_STATE - 4U)
#define CONTROL_STATE_BYTES (TELEMETRY_ACTIVE_SIZE + 8U)
#define CONTROL_BOX_GUARD (CONTROL_MAILBOX - 4U)
#define CONTROL_BOX_BYTES 28U

static void snapshot_control(uint8_t *target, const volatile uint8_t *source, size_t size)
{
    size_t index;
    for (index = 0; index < size; ++index)
        target[index] = source[index];
}

static void seed_control_probe(void)
{
    reset_case();
    fill_bytes(ram_pointer(CONTROL_STATE_GUARD), CONTROL_STATE_BYTES, 0x6d);
    fill_bytes(ram_pointer(CONTROL_BOX_GUARD), CONTROL_BOX_BYTES, 0xa7);
    write_u16(ram_pointer(RXPR1), 0x8001U);
    write_u16(ram_pointer(RFPR1), 0x8002U);
    write_u16(ram_pointer(UMSR1), 0x4003U);
    write_u16(ram_pointer(MBIMR1), 0x25a5U);
}

static int check_control_probe(const char *name, const uint8_t *state,
    const uint8_t *mailbox, const uint16_t *flags, uint32_t before, uint32_t after)
{
    static const uint32_t addresses[] = {RXPR1, RFPR1, UMSR1, MBIMR1};
    size_t index;
    if (before != after)
        return fail_value(name, "stack", after, before);
    for (index = 0; index < 4; ++index)
        if (read_u16(ram_pointer(addresses[index])) != flags[index])
            return fail_value(name, "flag_write", read_u16(ram_pointer(addresses[index])), flags[index]);
    return expect_bytes(name, "state_and_guards", ram_pointer(CONTROL_STATE_GUARD), state, CONTROL_STATE_BYTES)
        && expect_bytes(name, "mailbox_and_guards", ram_pointer(CONTROL_BOX_GUARD), mailbox, CONTROL_BOX_BYTES);
}

static int run_control_config_probe(enum config_mutation mutation)
{
    uint8_t state[CONTROL_STATE_BYTES], mailbox[CONTROL_BOX_BYTES];
    const uint16_t flags[] = {0x8001U, 0x8002U, 0x4003U, 0x25a5U};
    uint32_t before, after;
    count_case();
    seed_control_probe();
    seed_control_command(start_command, 8);
    write_u16(ram_pointer(CONTROL_MAILBOX), 0x6f10U);
    write_u16(ram_pointer(RXPR1), flags[0]);
    snapshot_control(state, ram_pointer(CONTROL_STATE_GUARD), sizeof(state));
    snapshot_control(mailbox, ram_pointer(CONTROL_BOX_GUARD), sizeof(mailbox));
    __asm__ volatile ("mov r15,%0" : "=r" (before) : : "memory");
    mutate_configuration(mutation);
    (void)invoke_r4(CONTROL_POLL, 0);
    __asm__ volatile ("mov r15,%0" : "=r" (after) : : "memory");
    return check_control_probe("control-config-reject", state, mailbox, flags, before, after);
}

#ifndef TARGET_1ME3B
static int run_control_init_probe(uint16_t identifier, uint16_t expected_mailbox_id,
    uint8_t enabled, int invalid)
{
    uint8_t state[CONTROL_STATE_BYTES], mailbox[CONTROL_BOX_BYTES];
    uint16_t flags[] = {0x8001U, 0x8002U, 0x4003U, 0x25a5U};
    uint32_t before, after, returned;
    count_case();
    seed_control_probe();
    write_u16(rom_pointer(CONFIG) + 8, identifier);
    rom_pointer(CONFIG)[3] = enabled;
    if (invalid)
        mutate_configuration(CONFIG_CRC);
    snapshot_control(state, ram_pointer(CONTROL_STATE_GUARD), sizeof(state));
    snapshot_control(mailbox, ram_pointer(CONTROL_BOX_GUARD), sizeof(mailbox));
    if (!invalid) {
        write_u16(mailbox + 4, expected_mailbox_id);
        write_u16(mailbox + 6, 0);
        write_u16(mailbox + 8, 0x0208U);
        write_u16(mailbox + 10, 0);
        write_u16(mailbox + 20, 0);
        write_u16(mailbox + 22, 0);
        flags[0] = flags[1] = flags[2] = CONTROL_MAILBOX_MASK;
        flags[3] = 0xa5a5U;
    }
    __asm__ volatile ("mov r15,%0" : "=r" (before) : : "memory");
    returned = invoke_r0(HCAN1_INIT_WRAPPER);
    __asm__ volatile ("mov r15,%0" : "=r" (after) : : "memory");
    if (returned != 1)
        return fail_value("control-init-probe", "stock_result", returned, 1);
    return check_control_probe("control-init-probe", state, mailbox, flags, before, after);
}
#endif

#ifndef TARGET_1ME3B
static int run_control_command_probe(unsigned mode, uint8_t divisor,
    uint8_t expected_divider)
{
    uint8_t state[CONTROL_STATE_BYTES], mailbox[CONTROL_BOX_BYTES];
    uint16_t flags[] = {0x8001U, 0x0002U, 0x4003U, 0x25a5U};
    uint32_t before, after;
    count_case();
    seed_control_probe();
    seed_control_command(mode == 8 ? stop_command : start_command, 8);
    write_u16(ram_pointer(CONTROL_MAILBOX), mode == 2 ? 0x6f18U : 0x6f10U);
    rom_pointer(CONFIG)[6] = divisor;
    ram_pointer(TELEMETRY_STATE)[1] = 1;
    ram_pointer(TELEMETRY_STATE)[2] = 1;
    ram_pointer(TELEMETRY_STATE)[10] = 0x7f;
    ram_pointer(TELEMETRY_STATE)[11] = 0;
    if (mode == 0 || mode == 1)
        flags[0] = 1;
    if (mode == 1 || mode == 2 || mode == 9)
        flags[1] = 0x8002U;
    write_u16(ram_pointer(RXPR1), flags[0]);
    write_u16(ram_pointer(RFPR1), flags[1]);
    if (mode == 3 || mode == 4)
        ram_pointer(CONTROL_MAILBOX)[5] = mode == 3 ? 7 : 9;
    if (mode == 5)
        ram_pointer(CONTROL_MAILBOX_DATA)[0] ^= 1;
    if (mode == 6)
        ram_pointer(CONTROL_MAILBOX_DATA)[7] ^= 1;
    if (mode == 7 || mode == 9)
        rom_pointer(CONFIG)[3] = 0;
    snapshot_control(state, ram_pointer(CONTROL_STATE_GUARD), sizeof(state));
    snapshot_control(mailbox, ram_pointer(CONTROL_BOX_GUARD), sizeof(mailbox));
    if (mode != 0)
        flags[0] = flags[1] = flags[2] = CONTROL_MAILBOX_MASK;
    if (mode == 7 || mode == 9) {
        state[4 + 11] = 1;
        state[4 + 10] = expected_divider;
    } else if (mode == 8) {
        state[4 + 11] = 2;
        state[4 + 10] = 0;
        state[4 + 1] = 0;
    } else if (mode == 5) {
        /* Without the TEL2 magic the frame is a dynamic page command, and
           its CRC fails: the reject counter advances and the staging clears. */
        state[4 + 0x103] = 0x6e;
        state[4 + 0x106] = 0;
        state[4 + 0x107] = 0;
        state[4 + 0x108] = 0;
    }
    __asm__ volatile ("mov r15,%0" : "=r" (before) : : "memory");
    (void)invoke_r4(CONTROL_POLL, 0);
    __asm__ volatile ("mov r15,%0" : "=r" (after) : : "memory");
    return check_control_probe("control-command-probe", state, mailbox, flags, before, after);
}
#endif

static int run_canonical_control_cases(void)
{
    enum config_mutation mutation;
    for (mutation = CONFIG_MAGIC; mutation <= CONFIG_INTEGRITY; ++mutation)
        if (mutation != CONFIG_DISABLED && !run_control_config_probe(mutation))
            return 0;
#ifndef TARGET_1ME3B
    unsigned mode;
    if (!run_control_init_probe(0x06f0U, 0x6f10U, 1, 0)
        || !run_control_init_probe(1, 0x0020U, 1, 0)
        || !run_control_init_probe(0x07feU, 0x7ff0U, 1, 0)
        || !run_control_init_probe(0x06f0U, 0x6f10U, 0, 0)
        || !run_control_init_probe(0x06f0U, 0x6f10U, 1, 1))
        return 0;
    for (mode = 0; mode < 10; ++mode)
        if (!run_control_command_probe(mode, 1, 0))
            return 0;
    return run_control_command_probe(7, 0xffU, 0xfeU);
#else
    return 1;
#endif
}
#endif

static int run_capture_cases(void)
{
    volatile uint8_t *state;

    count_case();
    reset_case();
    write_u16(rom_pointer(CONFIG) + 8, 1);
    write_u16(ram_pointer(TELEMETRY_STATE) + 8, 0x121f);
    (void)invoke_r4(CAPTURE, 0);
    if (!verify_started("low-id", 1, TELEMETRY_PAGE_COUNT, BANK_B))
        return 0;
    if (!verify_bank("low-id", BANK_B, 0))
        return 0;

    count_case();
    reset_case();
    write_u16(rom_pointer(CONFIG) + 8, 0x07fe);
    (void)invoke_r4(CAPTURE, 0);
    if (!verify_started("high-id", 1, TELEMETRY_PAGE_COUNT, BANK_B))
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
    if (!verify_started("divider-due", 1, TELEMETRY_PAGE_COUNT, BANK_B))
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
    ram_pointer(0xffff1980U)[0] = 0x12;
    ram_pointer(0xffff1980U)[1] = 0x34;
    (void)invoke_r4(CAPTURE, 0);
    state = ram_pointer(TELEMETRY_STATE);
    if (state[1] != 1 || state[0] != 1)
        return fail_value("pending", "publication", state[1], 1);
    if (!verify_bank("pending", BANK_A, 1))
        return 0;

    count_case();
    ram_pointer(0xffff1980U)[0] = 0xab;
    ram_pointer(0xffff1980U)[1] = 0xcd;
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
    if (!verify_started("idle-bank-a", 0, TELEMETRY_PAGE_COUNT, BANK_A))
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

/* Each one-bit field with only its source bit set, then with every other bit
   set, under the default row of the dynamic page. A moved field carries the
   wire bit alone; a field that the layout keeps in the wire bit passes its
   byte unchanged. */
static int run_bit_field_cases(void)
{
    size_t index;
    unsigned other;

    for (index = 0; index < sizeof(bit_fields) / sizeof(bit_fields[0]);
            ++index) {
        uint32_t source =
            read_u32(rom_pointer(TABLE + bit_fields[index].slot * 4));
        uint8_t moved =
            bit_fields[index].source != bit_fields[index].wire;

        for (other = 0; other < 2; ++other) {
            const char *name = other
                ? bit_fields[index].other_case
                : bit_fields[index].bit_case;
            uint8_t value = other
                ? (uint8_t)~bit_fields[index].source
                : bit_fields[index].source;
            uint8_t wire = !other
                ? bit_fields[index].wire
                : moved ? 0U : (uint8_t)~bit_fields[index].wire;

            count_case();
            reset_case();
            ((volatile uint8_t *)(uintptr_t)source)[0] = value;
            (void)invoke_r4(CAPTURE, 0);
            if (!verify_started(name, 1, TELEMETRY_PAGE_COUNT, BANK_B))
                return 0;
            if (ram_pointer(BANK_B)[bit_fields[index].byte] != wire)
                return fail_value(name, "wire_byte",
                    ram_pointer(BANK_B)[bit_fields[index].byte], wire);
            if (!verify_bank(name, BANK_B, 0))
                return 0;
        }
    }
    return 1;
}

static int run_direct_entry_cases(void)
{
    volatile uint8_t *state;
    uint8_t context;

    for (context = 0; context < 5; ++context) {
        size_t index;

        count_case();
        reset_case();
        state = ram_pointer(TELEMETRY_STATE);
        state[6] = context;
        write_u16(state + 8, (uint16_t)(0x1000U + context));
        for (index = 0; index < 12; ++index) {
            state[KNOCK_MARGIN_STATE + index] =
                (uint8_t)(0x91U + index * 13U);
            margin_snapshot[index] = state[KNOCK_MARGIN_STATE + index];
        }
        (void)invoke_r4(BUILD_BANK, (uint32_t)(uintptr_t)ram_pointer(BANK_A));
        if (!verify_bank("direct-build", BANK_A, context))
            return 0;
        if (state[6] != (uint8_t)((context + 1) % 5))
            return fail_value(
                "direct-build", "context_next", state[6],
                (uint8_t)((context + 1) % 5));
        for (index = 0; index < 12; ++index) {
            uint8_t expected = margin_snapshot[index];

            if (context == 4)
                expected = (index & 1U) ? 0xff : 0x7f;
            if (state[KNOCK_MARGIN_STATE + index] != expected)
                return fail_value(
                    "direct-build", "margin_rearm",
                    state[KNOCK_MARGIN_STATE + index], expected);
        }
        if (state[KNOCK_MARGIN_STATE - 1] != 0
                || state[KNOCK_MARGIN_STATE + 12] != 0)
            return fail_value("direct-build", "margin_guard", 1, 0);
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

static int run_margin_case(
    const char *name,
    int selector,
    uint8_t primary,
    uint8_t alternate,
    uint8_t channel,
    uint16_t threshold,
    uint32_t metric,
    uint16_t before,
    uint16_t expected)
{
    volatile uint8_t *state;
    volatile uint8_t *stage = (volatile uint8_t *)(uintptr_t)EVALUATOR_STAGE;
    uint8_t stock_selector = rom_pointer(KNOCK_SELECTOR)[0];
    size_t index;
#ifdef VERIFY_7MFK_CAN_MARGIN
    uint8_t expected_state[TELEMETRY_ACTIVE_SIZE];
    uint32_t before_sp, after_sp;
#endif

    count_case();
    reset_case();
    state = ram_pointer(TELEMETRY_STATE);
    for (index = 0; index < 6; ++index) {
        write_u16(state + KNOCK_MARGIN_STATE + index * 2, before);
        write_u16(ram_pointer(KNOCK_THRESHOLD) + index * 2, 0);
        write_u32(ram_pointer(KNOCK_METRIC) + index * 4, 0xffffffffU);
    }
    if (selector >= 0)
        rom_pointer(KNOCK_SELECTOR)[0] = (uint8_t)selector;
    ram_pointer(KNOCK_CHANNEL_PRIMARY)[0] = primary;
    ram_pointer(KNOCK_CHANNEL_ALTERNATE)[0] = alternate;
    if (channel >= 1 && channel <= 6) {
        write_u16(
            ram_pointer(KNOCK_THRESHOLD) + (channel - 1U) * 2, threshold);
        write_u32(
            stage,
            (uint32_t)(uintptr_t)(
                ram_pointer(KNOCK_METRIC) + (channel - 1U) * 4));
    } else {
        write_u32(stage, EVALUATOR_STAGE + 12U);
    }
    write_u32(stage + 4, metric);
    write_u32(stage + 8, 0);
#ifdef VERIFY_7MFK_CAN_MARGIN
    for (index = 0; index < sizeof(expected_state); ++index)
        expected_state[index] = state[index];
    if (channel >= 1 && channel <= 6)
        write_u16(expected_state + KNOCK_MARGIN_STATE + (channel - 1U) * 2U, expected);
    __asm__ volatile ("mov r15,%0" : "=r" (before_sp) : : "memory");
#endif
    (void)invoke_r4(KNOCK_MARGIN_WRAPPER, 0);
#ifdef VERIFY_7MFK_CAN_MARGIN
    __asm__ volatile ("mov r15,%0" : "=r" (after_sp) : : "memory");
    if (before_sp != after_sp)
        return fail_value(name, "stack", after_sp, before_sp);
    if (!expect_bytes(name, "allocated_state", state, expected_state, sizeof(expected_state)))
        return 0;
#endif
    rom_pointer(KNOCK_SELECTOR)[0] = stock_selector;
    if (read_u32(stage + 8) != 1)
        return fail_value(name, "stock_calls", read_u32(stage + 8), 1);
    for (index = 0; index < 6; ++index) {
        uint16_t actual = read_u16(state + KNOCK_MARGIN_STATE + index * 2);
        uint16_t wanted = index + 1U == channel ? expected : before;

        if (actual != wanted)
            return fail_value(name, "latch", actual, wanted);
    }
    if (state[KNOCK_MARGIN_STATE - 1] != 0
            || state[KNOCK_MARGIN_STATE + 12] != 0)
        return fail_value(name, "guard", 1, 0);
    return 1;
}

/*
 * The simulator-only evaluator stub stores the staged offset-binary metric
 * before it returns, so every expected latch proves that the wrapper reads
 * the channel state after the stock call. The stale metric seeded by the case
 * would otherwise saturate the latch at -32768.
 */
static int run_knock_margin_cases(void)
{
    uint8_t stock_selector = rom_pointer(KNOCK_SELECTOR)[0];
    uint8_t stock_primary = (stock_selector & 8U) ? 2 : 5;
    uint8_t stock_alternate = (stock_selector & 8U) ? 5 : 2;

    if (!run_margin_case(
            "margin-channel-zero", 0, 0, 3, 0, 0, 0x80000000U,
            KNOCK_MARGIN_IDLE, KNOCK_MARGIN_IDLE))
        return 0;
    if (!run_margin_case(
            "margin-channel-high", 0, 7, 3, 0, 0, 0x80000000U,
            KNOCK_MARGIN_IDLE, KNOCK_MARGIN_IDLE))
        return 0;
    if (!run_margin_case(
            "margin-primary-positive", 0, 1, 4, 1, 1000,
            0x80000000U + 400U, KNOCK_MARGIN_IDLE, 600))
        return 0;
    if (!run_margin_case(
            "margin-alternate-boundary", 8, 2, 6, 6, 5000,
            0x80000000U + 5000U, KNOCK_MARGIN_IDLE, 0))
        return 0;
    if (!run_margin_case(
            "margin-stock-selector", -1, stock_primary, stock_alternate, 5,
            900, 0x80000000U - 100U, KNOCK_MARGIN_IDLE, 1000))
        return 0;
    if (!run_margin_case(
            "margin-exceeded", 0, 3, 1, 3, 1000,
            0x80000000U + 1500U, 600, (uint16_t)-500))
        return 0;
    if (!run_margin_case(
            "margin-exceeded-saturated", 0, 4, 1, 4, 0,
            0xffffffffU, (uint16_t)-500, (uint16_t)-32768))
        return 0;
    if (!run_margin_case(
            "margin-exceeded-edge", 8, 1, 4, 4, 0,
            0x80000000U + 32767U, (uint16_t)-500, (uint16_t)-32767))
        return 0;
    if (!run_margin_case(
            "margin-keeps-lower", 0, 2, 1, 2, 1000,
            0x80000000U + 400U, 100, 100))
        return 0;
    if (!run_margin_case(
            "margin-takes-lower", 8, 1, 5, 5, 1000,
            0x80000000U + 900U, 600, 100))
        return 0;
    if (!run_margin_case(
            "margin-signed-keep", 0, 6, 1, 6, 1000,
            0x80000000U + 400U, (uint16_t)-500, (uint16_t)-500))
        return 0;
    if (!run_margin_case(
            "margin-signed-take", 0, 6, 1, 6, 1000,
            0x80000000U + 2000U, (uint16_t)-500, (uint16_t)-1000))
        return 0;
    if (!run_margin_case(
            "margin-wide-positive", 0, 1, 2, 1, 65535,
            0U, 600, 600))
        return 0;
#if defined(VERIFY_7MFK_CAN_MARGIN) || defined(MEASURE_CAN_TELEMETRY)
    if (!run_margin_case(
            "margin-exceeded-limit", 0, 4, 1, 4, 0,
            0x80008000U, (uint16_t)-500, 0x8000U))
        return 0;
    if (!run_margin_case(
            "margin-equal-keeps", 0, 2, 1, 2, 1000,
            0x80000190U, 600, 600))
        return 0;
#endif
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
    ram_pointer(BANK_A)[63] = 0x03;
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

    count_case();
    reset_case();
    state = ram_pointer(TELEMETRY_STATE);
    state[2] = 0;
    state[3] = 4;
    signal_ack(MAILBOX26_MASK);
    (void)invoke_r4(COMPLETION, 0);
    if (state[2] != 0 || state[3] != 4)
        return fail_value("ack-idle", "page", state[3], 4);

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

    count_case();
    reset_case();
    state = ram_pointer(TELEMETRY_STATE);
    state[2] = 0;
    state[3] = 3;
    signal_abort(MAILBOX26_MASK);
    (void)invoke_r4(COMPLETION, 0);
    if (state[2] != 0 || state[3] != 3 || state[7] != 2 || state[15] != 1)
        return fail_value("abort-not-busy", "counter", state[15], 1);

    count_case();
    reset_case();
    state = ram_pointer(TELEMETRY_STATE);
    state[0] = 2;
    state[2] = 1;
    state[4] = 11;
    signal_abort(MAILBOX26_MASK);
    (void)invoke_r4(COMPLETION, 0);
    if (state[0] != 2 || state[2] != 0 || state[7] != 2 || state[15] != 1)
        return fail_value("abort-corrupt", "busy", state[2], 0);
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

/* Dynamic page: commands on the control frame and page 3 of the capture. */
static volatile uint8_t *dynamic_state(void)
{
    return ram_pointer(DYNAMIC_STATE);
}

static uint32_t window_start(uint32_t offset)
{
    return 0xff000000U | (DYNAMIC_WINDOW_START + offset);
}

static uint32_t window_end(uint32_t offset)
{
    return 0xff000000U | (DYNAMIC_WINDOW_END - offset);
}

static uint16_t dynamic_crc(const uint8_t *bytes)
{
    uint16_t crc = 0xffffU;
    size_t index;
    unsigned bit;

    for (index = 0; index < 6; ++index) {
        crc ^= (uint16_t)(bytes[index] << 8);
        for (bit = 0; bit < 8; ++bit)
            crc = (crc & 0x8000U)
                ? (uint16_t)((crc << 1) ^ 0x1021U)
                : (uint16_t)(crc << 1);
    }
    return crc;
}

static void send_dynamic(
    uint8_t opcode, uint8_t b1, uint8_t b2, uint8_t b3, uint8_t b4,
    uint8_t b5, int corrupt)
{
    uint8_t frame[8] = {opcode, b1, b2, b3, b4, b5, 0, 0};
    uint16_t crc = dynamic_crc(frame);

    if (corrupt)
        crc ^= 1U;
    frame[6] = (uint8_t)(crc >> 8);
    frame[7] = (uint8_t)crc;
    seed_control_command(frame, 8);
    (void)invoke_r4(CONTROL_POLL, 0);
}

static void send_set(
    uint8_t id, unsigned group, unsigned slot, unsigned width,
    uint32_t address)
{
    send_dynamic(0xc1, id, (uint8_t)((group << 7) | (slot << 4) | width),
        (uint8_t)(address >> 16), (uint8_t)(address >> 8), (uint8_t)address,
        0);
}

static void send_commit(uint8_t id, uint8_t groups, uint8_t n0, uint8_t n1)
{
    send_dynamic(0xc2, id, groups, n0, n1, 0, 0);
}

static int expect_dynamic(
    const char *name, uint8_t active, uint8_t staging, uint16_t mask,
    uint8_t rejects)
{
    volatile uint8_t *state = dynamic_state();

    if (state[0] != active)
        return fail_value(name, "active_id", state[0], active);
    if (state[8] != staging)
        return fail_value(name, "staging_id", state[8], staging);
    if (read_u16(state + 6) != mask)
        return fail_value(name, "staged_mask", read_u16(state + 6), mask);
    if (state[3] != rejects)
        return fail_value(name, "rejects", state[3], rejects);
    return 1;
}

static void seed_slot(uint32_t address, unsigned width, uint8_t first)
{
    unsigned index;

    for (index = 0; index < width; ++index)
        ram_pointer(address + index)[0] = (uint8_t)(first + index * 13U);
}

/* Bytes 1..7 of the dynamic page: the slot bytes, zero padding, and the
   configuration byte. */
static void expect_page(
    uint8_t *page, const uint32_t *addresses, const uint8_t *widths,
    size_t count, uint8_t id_byte)
{
    size_t slot;
    size_t out = 0;
    unsigned index;

    for (slot = 0; slot < count; ++slot)
        for (index = 0; index < widths[slot]; ++index)
            page[out++] = ram_pointer(addresses[slot] + index)[0];
    while (out < TELEMETRY_DYNAMIC_DATA_BYTES)
        page[out++] = 0;
    page[TELEMETRY_DYNAMIC_DATA_BYTES] = id_byte;
}

/* Build one idle snapshot of context 0 and verify every page of it. */
static int capture_dynamic(const char *name, const uint8_t *page)
{
    volatile uint8_t *state = ram_pointer(TELEMETRY_STATE);
    uint32_t bank = state[0] ? BANK_A : BANK_B;
    int result;

    state[1] = 0;
    state[2] = 0;
    state[6] = 0;
    dynamic_page = page;
    (void)invoke_r4(CAPTURE, 0);
    result = verify_bank(name, bank, 0);
    dynamic_page = NULL;
    return result;
}

static int run_dynamic_command_cases(void)
{
    uint32_t a = window_start(0x100);
    volatile uint8_t *state;

    count_case();
    reset_case();
    if (dynamic_crc(start_command) != 0xb632U
            || dynamic_crc(stop_command) != 0xa613U)
        return fail_value("dyn-crc-model", "crc", dynamic_crc(start_command),
            0xb632U);
    send_set(1, 0, 0, 1, a);
    if (!expect_dynamic("dyn-set", 0, 1, 0x0001U, 0))
        return 0;
    send_dynamic(0xc1, 1, 0x11, (uint8_t)(a >> 16), (uint8_t)(a >> 8),
        (uint8_t)a, 1);
    if (!expect_dynamic("dyn-crc", 0, 0, 0, 1))
        return 0;

    count_case();
    send_set(1, 0, 0, 1, a);
    send_dynamic(0xc3, 1, 0x01, 0, 0, 0, 0);
    if (!expect_dynamic("dyn-opcode", 0, 0, 0, 2))
        return 0;

    count_case();
    send_dynamic(0xc0, 1, 0, 0, 0, 0, 0);
    if (!expect_dynamic("dyn-default-head", 0, 0, 0, 3))
        return 0;

    count_case();
    send_dynamic(0xc0, 0, 0, 0, 0, 1, 0);
    if (!expect_dynamic("dyn-default-tail", 0, 0, 0, 4))
        return 0;

    count_case();
    send_set(0, 0, 0, 1, a);
    if (!expect_dynamic("dyn-set-id-zero", 0, 0, 0, 5))
        return 0;

    count_case();
    send_set(0x80, 0, 0, 1, a);
    if (!expect_dynamic("dyn-set-id-high", 0, 0, 0, 6))
        return 0;

    count_case();
    send_set(1, 0, TELEMETRY_DYNAMIC_DATA_BYTES, 1, a);
    if (!expect_dynamic("dyn-set-slot", 0, 0, 0, 7))
        return 0;

    count_case();
    send_set(1, 0, 0, 3, a);
    if (!expect_dynamic("dyn-set-width", 0, 0, 0, 8))
        return 0;

    count_case();
    send_set(1, 0, 0, 2, a + 1);
    if (!expect_dynamic("dyn-set-word-align", 0, 0, 0, 9))
        return 0;

    count_case();
    send_set(1, 0, 0, 4, a + 2);
    if (!expect_dynamic("dyn-set-long-align", 0, 0, 0, 10))
        return 0;

    count_case();
    send_set(1, 0, 0, 1, window_start(0) - 1);
    if (!expect_dynamic("dyn-set-below-byte", 0, 0, 0, 11))
        return 0;

    count_case();
    send_set(1, 0, 0, 2, window_start(0) - 2);
    if (!expect_dynamic("dyn-set-below-word", 0, 0, 0, 12))
        return 0;

    count_case();
    send_set(1, 0, 0, 1, window_end(0));
    if (!expect_dynamic("dyn-set-above-byte", 0, 0, 0, 13))
        return 0;

    count_case();
    send_set(1, 0, 0, 2, window_end(0));
    if (!expect_dynamic("dyn-set-above-word", 0, 0, 0, 14))
        return 0;

    count_case();
    send_set(1, 0, 0, 4, window_end(0));
    if (!expect_dynamic("dyn-set-above-long", 0, 0, 0, 15))
        return 0;

    count_case();
    send_set(2, 0, 0, 1, window_start(0));
    send_set(2, 0, 1, 2, window_start(0));
    send_set(2, 0, 2, 4, window_start(0));
    send_set(2, 1, 0, 1, window_end(1));
    send_set(2, 1, 1, 2, window_end(2));
    send_set(2, 1, 5, 4, window_end(4));
    if (!expect_dynamic("dyn-set-edges", 0, 2, 0x2307U, 15))
        return 0;

    count_case();
    send_set(3, 0, 1, 1, a);
    if (!expect_dynamic("dyn-set-restart", 0, 3, 0x0002U, 15))
        return 0;

    count_case();
    state = dynamic_state();
    state[3] = 0xff;
    send_dynamic(0xc3, 0, 0, 0, 0, 0, 0);
    if (!expect_dynamic("dyn-reject-saturates", 0, 0, 0, 0xff))
        return 0;
    state[3] = 0;

    count_case();
    send_set(4, 0, 0, 1, a);
    send_commit(0, 1, 1, 0);
    if (!expect_dynamic("dyn-commit-id-zero", 0, 0, 0, 1))
        return 0;

    count_case();
    send_set(4, 0, 0, 1, a);
    send_commit(5, 1, 1, 0);
    if (!expect_dynamic("dyn-commit-id-staging", 0, 0, 0, 2))
        return 0;

    count_case();
    send_set(4, 0, 0, 1, a);
    send_dynamic(0xc2, 4, 1, 1, 0, 1, 0);
    if (!expect_dynamic("dyn-commit-reserved", 0, 0, 0, 3))
        return 0;

    count_case();
    send_set(4, 0, 0, 1, a);
    send_commit(4, 1, 0, 0);
    if (!expect_dynamic("dyn-commit-count-zero", 0, 0, 0, 4))
        return 0;

    count_case();
    send_set(4, 0, 0, 1, a);
    send_commit(4, 1, TELEMETRY_DYNAMIC_DATA_BYTES + 1, 0);
    if (!expect_dynamic("dyn-commit-count-high", 0, 0, 0, 5))
        return 0;

    count_case();
    send_set(4, 0, 0, 4, a);
    send_set(4, 0, 1, 2, a + 4);
    send_set(4, 0, 2, 1, a + 6);
    send_commit(4, 1, 3, 0);
    if (!expect_dynamic("dyn-commit-wide", 0, 0, 0, 6))
        return 0;

    count_case();
    send_set(4, 0, 0, 1, a);
    send_commit(4, 2, 1, 0);
    if (!expect_dynamic("dyn-commit-groups", 0, 0, 0, 7))
        return 0;

    count_case();
    send_set(4, 0, 0, 1, a);
    send_set(4, 1, 0, 1, a);
    send_commit(4, 2, 1, TELEMETRY_DYNAMIC_DATA_BYTES + 1);
    if (!expect_dynamic("dyn-commit-group-1", 0, 0, 0, 8))
        return 0;

    count_case();
    send_set(4, 0, 0, 1, a);
    send_set(4, 0, 1, 1, a);
    send_set(4, 0, 2, 1, a);
    send_commit(4, 1, 2, 0);
    if (!expect_dynamic("dyn-commit-mask", 0, 0, 0, 9))
        return 0;

    count_case();
    send_set(4, 0, 0, 1, a);
    send_set(4, 1, 0, 1, a);
    send_commit(4, 1, 1, 0);
    if (!expect_dynamic("dyn-commit-extra-group", 0, 0, 0, 10))
        return 0;
    return 1;
}

static int run_dynamic_capture_cases(void)
{
    uint32_t a = window_start(0x101);
    uint32_t b = window_start(0x106);
    uint32_t c = window_start(0x108);
    uint32_t d = window_start(0x10e);
    uint32_t e = window_start(0x113);
    uint8_t page[TELEMETRY_DYNAMIC_DATA_BYTES + 1];
    volatile uint8_t *state;

    count_case();
    reset_case();
    seed_slot(a, 1, 0x3c);
    seed_slot(b, 2, 0x51);
    send_set(7, 0, 0, 1, a);
    send_set(7, 0, 1, 2, b);
    send_commit(7, 1, 2, 0);
    state = dynamic_state();
    if (!expect_dynamic("dyn-one-group", 7, 0, 0, 0)
            || state[1] != 1 || state[2] != 0 || state[4] != 2
            || state[5] != 0)
        return fail_value("dyn-one-group", "configuration", state[4], 2);
    {
        const uint32_t addresses[] = {a, b};
        const uint8_t widths[] = {1, 2};

        expect_page(page, addresses, widths, 2, 7);
        if (!capture_dynamic("dyn-one-group-first", page))
            return 0;
        count_case();
        if (!capture_dynamic("dyn-one-group-second", page))
            return 0;
    }

    count_case();
    seed_slot(c, 4, 0x92);
    seed_slot(d, 2, 0x17);
    seed_slot(e, 1, 0xe4);
    send_set(9, 0, 0, 4, c);
    send_set(9, 0, 1, 1, a);
    send_set(9, 0, 2, 1, e);
    send_set(9, 1, 0, 2, b);
    send_set(9, 1, 1, 2, d);
    send_set(9, 1, 2, 1, e);
    send_commit(9, 2, 3, 3);
    if (!expect_dynamic("dyn-two-groups", 9, 0, 0, 0)
            || state[1] != 2 || state[4] != 3 || state[5] != 3)
        return fail_value("dyn-two-groups", "configuration", state[5], 3);
    {
        const uint32_t first[] = {c, a, e};
        const uint8_t first_widths[] = {4, 1, 1};
        const uint32_t second[] = {b, d, e};
        const uint8_t second_widths[] = {2, 2, 1};

        expect_page(page, first, first_widths, 3, 9);
        if (!capture_dynamic("dyn-two-groups-0", page))
            return 0;
        count_case();
        expect_page(page, second, second_widths, 3, 0x89);
        if (!capture_dynamic("dyn-two-groups-1", page))
            return 0;
        count_case();
        expect_page(page, first, first_widths, 3, 9);
        if (!capture_dynamic("dyn-two-groups-again", page))
            return 0;
    }

    count_case();
    seed_slot(window_start(0), 4, 0x21);
    seed_slot(window_end(1), 1, 0xc7);
    send_set(10, 0, 0, 4, window_start(0));
    send_set(10, 0, 1, 1, window_end(1));
    send_commit(10, 1, 2, 0);
    {
        const uint32_t addresses[] = {window_start(0), window_end(1)};
        const uint8_t widths[] = {4, 1};

        expect_page(page, addresses, widths, 2, 10);
        if (!capture_dynamic("dyn-window-edges", page))
            return 0;
    }

    count_case();
    seed_slot(window_end(4), 4, 0x6b);
    seed_slot(window_end(2), 2, 0x1d);
    send_set(11, 0, 0, 4, window_end(4));
    send_set(11, 1, 0, 2, window_end(2));
    send_set(11, 1, 1, 2, window_start(0));
    send_commit(11, 2, 1, 2);
    {
        const uint32_t first[] = {window_end(4)};
        const uint8_t first_widths[] = {4};

        expect_page(page, first, first_widths, 1, 11);
        if (!capture_dynamic("dyn-window-end", page))
            return 0;
    }

    count_case();
    {
        uint32_t addresses[TELEMETRY_DYNAMIC_DATA_BYTES];
        uint8_t widths[TELEMETRY_DYNAMIC_DATA_BYTES];
        unsigned slot;

        for (slot = 0; slot < TELEMETRY_DYNAMIC_DATA_BYTES; ++slot) {
            addresses[slot] = window_start(0x120 + slot);
            widths[slot] = 1;
            seed_slot(addresses[slot], 1, (uint8_t)(0x40 + slot * 7U));
            send_set(15, 0, slot, 1, addresses[slot]);
        }
        send_commit(15, 1, TELEMETRY_DYNAMIC_DATA_BYTES, 0);
        expect_page(page, addresses, widths, TELEMETRY_DYNAMIC_DATA_BYTES, 15);
        if (!capture_dynamic("dyn-six-slots", page))
            return 0;
    }

    count_case();
    send_dynamic(0xc0, 0, 0, 0, 0, 0, 0);
    if (!expect_dynamic("dyn-default", 0, 0, 0, 0))
        return 0;
    if (!capture_dynamic("dyn-default-page", NULL))
        return 0;

    count_case();
    send_set(12, 0, 0, 1, a);
    send_set(12, 0, 1, 1, b);
    send_commit(12, 1, 2, 0);
    write_u32(dynamic_state() + 0x14, 0x03000000U | (b & 0x00ffffffU));
    if (!capture_dynamic("dyn-corrupt-slot", NULL))
        return 0;
    if (dynamic_state()[0] != 0)
        return fail_value("dyn-corrupt-slot", "active_id",
            dynamic_state()[0], 0);

    count_case();
    send_set(13, 0, 0, 4, c);
    send_commit(13, 1, 1, 0);
    write_u32(dynamic_state() + 0x14, 0x04000000U | (c & 0x00ffffffU));
    dynamic_state()[4] = 2;
    if (!capture_dynamic("dyn-corrupt-budget", NULL))
        return 0;
    if (dynamic_state()[0] != 0)
        return fail_value("dyn-corrupt-budget", "active_id",
            dynamic_state()[0], 0);

    count_case();
    send_set(14, 0, 0, 1, a);
    send_commit(14, 1, 1, 0);
    seed_control_command(start_command, 8);
    (void)invoke_r4(CONTROL_POLL, 0);
    if (ram_pointer(TELEMETRY_STATE)[11] != 1
            || !expect_dynamic("dyn-start", 14, 0, 0, 0))
        return fail_value("dyn-start", "override",
            ram_pointer(TELEMETRY_STATE)[11], 1);
    seed_control_command(stop_command, 8);
    (void)invoke_r4(CONTROL_POLL, 0);
    if (ram_pointer(TELEMETRY_STATE)[11] != 2
            || !expect_dynamic("dyn-stop", 14, 0, 0, 0))
        return fail_value("dyn-stop", "override",
            ram_pointer(TELEMETRY_STATE)[11], 2);
    return 1;
}

/* An installed configuration fills the bank byte of the LTFT neutral control
   field with slot data, which the capture keeps as the slot reads it while
   the default source holds its source bit. */
static int run_bit_field_configuration_case(void)
{
    uint32_t addresses[TELEMETRY_DYNAMIC_DATA_BYTES];
    uint8_t widths[TELEMETRY_DYNAMIC_DATA_BYTES];
    uint8_t page[TELEMETRY_DYNAMIC_DATA_BYTES + 1];
    uint32_t source = read_u32(rom_pointer(TABLE + LTFT_NEUTRAL_SLOT * 4));
    size_t data = LTFT_NEUTRAL_BYTE - TELEMETRY_DYNAMIC_PAGE * 8U - 1U;
    unsigned slot;

    count_case();
    reset_case();
    ((volatile uint8_t *)(uintptr_t)source)[0] = LTFT_NEUTRAL_SOURCE;
    for (slot = 0; slot < TELEMETRY_DYNAMIC_DATA_BYTES; ++slot) {
        addresses[slot] = window_start(0x140 + slot);
        widths[slot] = 1;
        ram_pointer(addresses[slot])[0] = 0xffU;
        send_set(16, 0, slot, 1, addresses[slot]);
    }
    send_commit(16, 1, TELEMETRY_DYNAMIC_DATA_BYTES, 0);
    if (!expect_dynamic("ltft-neutral-configured", 16, 0, 0, 0))
        return 0;
    expect_page(page, addresses, widths, TELEMETRY_DYNAMIC_DATA_BYTES, 16);
    if (page[data] != 0xffU)
        return fail_value("ltft-neutral-configured", "slot_byte",
            page[data], 0xff);
    return capture_dynamic("ltft-neutral-configured", page);
}

int main(void)
{
#ifdef TARGET_1ME3B
    if (!run_stock_receive_preservation_cases())
        return 1;
#endif
    if (!run_wrapper_cases())
        return 1;
    if (!run_configuration_cases())
        return 1;
    if (!run_control_cases())
        return 1;
    if (!run_dynamic_command_cases())
        return 1;
    if (!run_dynamic_capture_cases())
        return 1;
    if (!run_capture_cases())
        return 1;
    if (!run_bit_field_cases())
        return 1;
    if (!run_bit_field_configuration_case())
        return 1;
    if (!run_direct_entry_cases())
        return 1;
    if (!run_knock_margin_cases())
        return 1;
    if (!run_completion_cases())
        return 1;
    if (!run_abort_cases())
        return 1;
#if defined(VERIFY_7MFK_CAN_CONTROL) || defined(MEASURE_CAN_TELEMETRY)
    if (!run_canonical_control_cases())
        return 1;
#endif
    if (!run_isr_cases())
        return 1;
    printf(
        "VQ_SH_ELF_CAN_TELEMETRY status=PASS cases=%lu entries=13 "
        "profiles=1 contexts=10 isr_rte=5\n",
        (unsigned long)case_count);
    return 0;
}
