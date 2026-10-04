/* Separate arithmetic entries with explicit R4 and independent RAM count. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "stock-jk08a-knock-integration-cases.h"

#define RAM_BASE 0x01000000U
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))

struct context { uint32_t r[15], gbr, mach, macl; };
struct observation {
    uint32_t exit[20], sp, continuation, abi_before[12], abi_after[12];
    uint8_t frame_before[52], frame_after[52];
};
extern void stock_invoke_knock_integration(uint32_t entry,
    const struct context *context, struct observation *observation);

static uint8_t ram_before[65536], calibration_before[36];
static unsigned long completed;
static const uint32_t abi_expected[10] = {
    0x18283848U, 0x19293949U, 0x1a2a3a4aU, 0x1b2b3b4bU,
    0x1c2c3c4cU, 0x1d2d3d4dU, 0x1e2e3e4eU, 0x12344321U,
    0x10203040U, 0x50607080U
};
static const struct { uint32_t address, size; } calibrations[] = {
    {0x8eaaU, 2}, {0x8eaeU, 2}, {0x49668U, 4}, {0x49678U, 4},
    {0x4968cU, 4}, {0x49690U, 4}, {0x49694U, 4}, {0x49698U, 4},
    {0x49938U, 4}, {0x4995cU, 4}
};

static volatile uint8_t *ram(uint32_t address)
{ return (volatile uint8_t *)(RAM_BASE + (address & 0xffffU)); }

static uint32_t reg(const struct observation *out, unsigned n)
{ return out->exit[19U - n]; }

static uint32_t frame_word(const uint8_t *frame, unsigned offset)
{
    return (uint32_t)frame[offset] << 24 | (uint32_t)frame[offset + 1] << 16 |
           (uint32_t)frame[offset + 2] << 8 | frame[offset + 3];
}

static int fail(const char *scope, unsigned long index, const char *field,
                uint32_t actual, uint32_t expected)
{
    fprintf(stderr, "%s[%lu] %s actual=%08lx expected=%08lx\n", scope, index,
            field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}

static void set_ram_word(uint32_t address, uint16_t value)
{
    volatile uint8_t *p = ram(address);
    p[0] = (uint8_t)(value >> 8); p[1] = (uint8_t)value;
}

static uint16_t ram_word(uint32_t address)
{
    volatile uint8_t *p = ram(address);
    return (uint16_t)((uint16_t)p[0] << 8 | p[1]);
}

static int verify_initial_calibrations(void)
{
    unsigned i;
    static const struct { uint32_t pool, stock; } aliases[] = {
        {0x49668U, 0xffff119cU}, {0x49678U, 0xffff128cU},
        {0x4968cU, 0xffff1ff4U}, {0x49690U, 0xffff124cU},
        {0x49938U, 0xffff124cU}
    };
    if (*(volatile uint16_t *)0x8eaaU != 13U || *(volatile uint16_t *)0x8eaeU != 307U)
        return fail("initial", 0, "stock arithmetic constants", 1, 0);
    if (*(volatile uint32_t *)0x49694U != 0x8eaaU ||
        *(volatile uint32_t *)0x49698U != 0x8292U ||
        *(volatile uint32_t *)0x4995cU != 0x8eaeU)
        return fail("initial", 0, "stock ROM pointers", 1, 0);
    for (i = 0; i < ARRAY_SIZE(aliases); ++i)
        if (*(volatile uint32_t *)aliases[i].pool != (uint32_t)ram(aliases[i].stock))
            return fail("initial", i, "declared RAM alias", *(volatile uint32_t *)aliases[i].pool, (uint32_t)ram(aliases[i].stock));
    return 1;
}

static void seed_and_snapshot(const struct integration_case *test)
{
    unsigned i, j, at = 0;
    for (i = 0; i < 65536U; ++i)
        ((volatile uint8_t *)RAM_BASE)[i] = (uint8_t)(0x5dU + i * 29U + (i >> 8));
    set_ram_word(STATE, (uint16_t)test->state);
    set_ram_word(OUTPUT, 0x6d01U);
    *ram(COUNT) = test->ram_count;
    for (i = 0; i < 65536U; ++i)
        ram_before[i] = ((volatile uint8_t *)RAM_BASE)[i];
    for (i = 0; i < ARRAY_SIZE(calibrations); ++i)
        for (j = 0; j < calibrations[i].size; ++j)
            calibration_before[at++] = ((volatile uint8_t *)calibrations[i].address)[j];
}

static int preserve_inputs(const char *scope, unsigned long index)
{
    unsigned i, j, at = 0;
    for (i = 0; i < 65536U; ++i) {
        if (i == (OUTPUT & 0xffffU) || i == ((OUTPUT + 1U) & 0xffffU) ||
            i == (COUNT & 0xffffU)) continue;
        if (((volatile uint8_t *)RAM_BASE)[i] != ram_before[i])
            return fail(scope, index, "RAM/input preservation", i, ram_before[i]);
    }
    for (i = 0; i < ARRAY_SIZE(calibrations); ++i)
        for (j = 0; j < calibrations[i].size; ++j, ++at)
            if (((volatile uint8_t *)calibrations[i].address)[j] != calibration_before[at])
                return fail(scope, index, "calibration/pool preservation",
                            calibrations[i].address + j, calibration_before[at]);
    return 1;
}

static struct context new_context(const struct integration_case *test)
{
    struct context context;
    unsigned i;
    for (i = 0; i < 15U; ++i)
        context.r[i] = 0x28765430U + i * 0x01030507U;
    if (test->event) context.r[4] = test->count;
    context.r[7] = test->event ? EVENT_ENTRY : QUIET_ENTRY;
    context.gbr = 0x01000080U;
    context.mach = 0x13579bdfU;
    context.macl = 0x2468ace0U;
    return context;
}

static int run_case(unsigned long index, const struct integration_case *test)
{
    const char *scope = test->event ? "explicit-event-entry" : "explicit-quiet-entry";
    struct context context = new_context(test), before = context;
    struct observation out;
    unsigned i;
    seed_and_snapshot(test);
    memset(&out, 0xa6, sizeof(out));
    stock_invoke_knock_integration(context.r[7], &context, &out);
    if (memcmp(&context, &before, sizeof(before)))
        return fail(scope, index, "entry context preservation", 1, 0);
    if (ram_word(OUTPUT) != (uint16_t)test->expected || *ram(COUNT) != 0U)
        return fail(scope, index, "state/count publication", ram_word(OUTPUT), (uint16_t)test->expected);
    for (i = 0; i < 15U; ++i) {
        uint32_t expected = context.r[i];
        if (i == 0U) expected = 0x14eU;
        if (i == 2U) expected = (uint32_t)test->expected;
        if (i == 3U) expected = (uint32_t)ram(0xffff119cU);
        if (i == 4U) expected = (uint32_t)test->r4;
        if (i == 5U) expected = 0x8292U;
        if (i == 6U) expected = (uint32_t)ram(0xffff1ff4U);
        if (i == 10U) expected = (uint32_t)ram(0xffff124cU);
        if (i == 13U) expected = 0U;
        if (reg(&out, i) != expected)
            return fail(scope, index, "stock fragment register", reg(&out, i), expected);
    }
    if ((out.exit[0] & 1U) != test->t)
        return fail(scope, index, "stock lower-clamp T", out.exit[0] & 1U, test->t);
    if (out.exit[2] != (test->event ? test->product : context.macl))
        return fail(scope, index, "entry-specific MACL", out.exit[2], test->event ? test->product : context.macl);
    if (out.exit[3] != context.mach || out.exit[4] != context.gbr)
        return fail(scope, index, "stock MACH/GBR", out.exit[3], context.mach);
    if (out.sp != out.abi_before[10] - 152U || out.exit[1] != out.continuation)
        return fail(scope, index, "stock SP/PR restoration", out.sp, out.abi_before[10] - 152U);
    if (memcmp(out.abi_before, out.abi_after, sizeof(out.abi_before)))
        return fail(scope, index, "C caller ABI restoration", 1, 0);
    for (i = 0; i < ARRAY_SIZE(abi_expected); ++i)
        if (out.abi_before[i] != abi_expected[i])
            return fail(scope, index, "C caller ABI sentinel", out.abi_before[i], abi_expected[i]);
    if (memcmp(out.frame_before, out.frame_after, sizeof(out.frame_before)))
        return fail(scope, index, "entire stack/local frame preservation", 1, 0);
    if (frame_word(out.frame_before, 48) != out.continuation ||
        frame_word(out.frame_after, 48) != out.continuation)
        return fail(scope, index, "local continuation preservation", frame_word(out.frame_after, 48), out.continuation);
    if (!preserve_inputs(scope, index)) return 0;
    ++completed;
    return 1;
}

int main(void)
{
    unsigned long i;
    if (!verify_initial_calibrations()) return 1;
    for (i = 0; i < ARRAY_SIZE(integration_cases); ++i)
        if (!run_case(i, &integration_cases[i])) return 1;
    if (completed != KNOCK_INTEGRATION_CASE_COUNT)
        return !fail("total", 0, "case count", completed, KNOCK_INTEGRATION_CASE_COUNT);
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY, completed);
    return 0;
}
