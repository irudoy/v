/* Narrow two-word publication with explicit stock and artificial gate contexts. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "stock-jk08a-knock-event-retard-cases.h"

#define RAM_BASE 0x01000000U
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))

struct context { uint32_t r[15], gbr, mach, macl; };
struct observation {
    uint32_t exit[20], sp, continuation, abi_before[12], abi_after[12];
    uint8_t frame_before[52], frame_after[52];
};
extern void stock_invoke_knock_event_retard(uint32_t entry,
    const struct context *context, struct observation *observation);

static uint8_t ram_before[65536], calibration_before[21];
static unsigned long completed;
static const uint32_t abi_expected[10] = {
    0x18283848U, 0x19293949U, 0x1a2a3a4aU, 0x1b2b3b4bU,
    0x1c2c3c4cU, 0x1d2d3d4dU, 0x1e2e3e4eU, 0x12344321U,
    0x10203040U, 0x50607080U
};
static const struct { uint32_t address, size; } calibrations[] = {
    {MODE, 1}, {0x4dba4U, 4}, {0x4dba8U, 4}, {0x4dbacU, 4},
    {0x4dbb0U, 4}, {0x4dbb4U, 4}
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
        {0x4dba8U, 0xffff24c0U}, {0x4dbacU, 0xffff11d4U},
        {0x4dbb0U, 0xffff22f8U}, {0x4dbb4U, 0xffff23bcU}
    };
    if (*(volatile uint8_t *)MODE != 0x7cU || *(volatile uint32_t *)0x4dba4U != MODE)
        return fail("initial", 0, "stock selector/pointer", 1, 0);
    for (i = 0; i < ARRAY_SIZE(aliases); ++i)
        if (*(volatile uint32_t *)aliases[i].pool != (uint32_t)ram(aliases[i].stock))
            return fail("initial", i, "declared RAM alias", *(volatile uint32_t *)aliases[i].pool, (uint32_t)ram(aliases[i].stock));
    return 1;
}

static void seed_and_snapshot(const struct retard_case *test)
{
    unsigned i, j, at = 0;
    for (i = 0; i < 65536U; ++i)
        ((volatile uint8_t *)RAM_BASE)[i] = (uint8_t)(0x5dU + i * 29U + (i >> 8));
    *(volatile uint8_t *)MODE = test->mode;
    set_ram_word(FIRST, 0x1234U);
    set_ram_word(SECOND, test->old_companion);
    *ram(KNOCK_BYTE) = (uint8_t)test->k;
    *ram(REQUEST_A) = (uint8_t)test->a;
    *ram(REQUEST_B) = (uint8_t)test->b;
    set_ram_word(SOURCE_WORD, test->high_word);
    *ram(FLAG5) = test->flag5; *ram(FLAGB) = test->flagb;
    for (i = 0; i < 65536U; ++i)
        ram_before[i] = ((volatile uint8_t *)RAM_BASE)[i];
    for (i = 0; i < ARRAY_SIZE(calibrations); ++i)
        for (j = 0; j < calibrations[i].size; ++j)
            calibration_before[at++] = ((volatile uint8_t *)calibrations[i].address)[j];
}

static int preserve_inputs(const char *scope, unsigned long index, unsigned gate)
{
    unsigned i, j, at = 0;
    for (i = 0; i < 65536U; ++i) {
        if (i == (FIRST & 0xffffU) || i == ((FIRST + 1U) & 0xffffU) ||
            (gate && (i == (SECOND & 0xffffU) || i == ((SECOND + 1U) & 0xffffU)))) continue;
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

static struct context new_context(const struct retard_case *test)
{
    struct context context;
    unsigned i;
    for (i = 0; i < 15U; ++i)
        context.r[i] = 0x28765430U + i * 0x01030507U;
    (void)test;
    context.r[7] = REGION_ENTRY;
    context.gbr = 0x01000080U;
    context.mach = 0x13579bdfU;
    context.macl = 0x2468ace0U;
    return context;
}

static int run_case(unsigned long index, const struct retard_case *test)
{
    const char *scope = test->mode == 0x7cU ? "stock-gate-context" : "artificial-gate-context";
    struct context context = new_context(test), before = context;
    struct observation out;
    unsigned i;
    seed_and_snapshot(test);
    memset(&out, 0xa6, sizeof(out));
    stock_invoke_knock_event_retard(context.r[7], &context, &out);
    if (memcmp(&context, &before, sizeof(before)))
        return fail(scope, index, "entry context preservation", 1, 0);
    if (ram_word(FIRST) != (uint16_t)test->first)
        return fail(scope, index, "first-word publication", ram_word(FIRST), (uint16_t)test->first);
    if (ram_word(SECOND) != (uint16_t)test->second)
        return fail(scope, index, "companion-word publication/retention", ram_word(SECOND), (uint16_t)test->second);
    for (i = 0; i < 15U; ++i) {
        uint32_t expected = context.r[i];
        if (i == 0U) expected = test->r0;
        if (i == 2U) expected = test->r2;
        if (i == 4U) expected = test->r4;
        if (i == 5U) expected = test->r5;
        if (i == 6U) expected = test->r6;
        if (i == 7U) expected = (uint32_t)ram(0xffff24c0U);
        if (i == 14U) expected = (uint32_t)ram(0xffff11d4U);
        if (reg(&out, i) != expected)
            return fail(scope, index, "stock fragment register", reg(&out, i), expected);
    }
    if ((out.exit[0] & 1U) != test->t)
        return fail(scope, index, "stock branch T", out.exit[0] & 1U, test->t);
    if (out.exit[2] != context.macl)
        return fail(scope, index, "stock MACL preservation", out.exit[2], context.macl);
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
    if (!preserve_inputs(scope, index, test->mode & 32U)) return 0;
    ++completed;
    return 1;
}

int main(void)
{
    unsigned long i;
    if (!verify_initial_calibrations()) return 1;
    for (i = 0; i < ARRAY_SIZE(retard_cases); ++i)
        if (!run_case(i, &retard_cases[i])) return 1;
    if (completed != KNOCK_EVENT_RETARD_CASE_COUNT)
        return !fail("total", 0, "case count", completed, KNOCK_EVENT_RETARD_CASE_COUNT);
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY, completed);
    return 0;
}
