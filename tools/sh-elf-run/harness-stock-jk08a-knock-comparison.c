/* Bounded comparison/count execution from explicit selected-channel contexts. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "stock-jk08a-knock-comparison-cases.h"

#define RAM_BASE 0x01000000U
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))

struct context { uint32_t r[15], gbr, mach, macl; };
struct observation {
    uint32_t exit[20], sp, continuation, abi_before[12], abi_after[12];
    uint8_t frame_before[52], frame_after[52];
};
extern void stock_invoke_knock_comparison(uint32_t entry,
    const struct context *context, struct observation *observation);

static uint8_t ram_before[65536], calibration_before[335];
static unsigned long completed;
static const uint32_t abi_expected[10] = {
    0x18283848U, 0x19293949U, 0x1a2a3a4aU, 0x1b2b3b4bU,
    0x1c2c3c4cU, 0x1d2d3d4dU, 0x1e2e3e4eU, 0x12344321U,
    0x10203040U, 0x50607080U
};
static const struct { uint32_t address, size; } calibrations[] = {
    {MODE, 1}, {TABLE, 194}, {AXIS, 32}, {JUMP_TABLE, 32},
    {0x221d8U, 8}, {0x2651cU, 8}, {0x269c0U, 4},
    {0x4a1fcU, 28}, {0x4a4c8U, 12}, {0x4a4e4U, 16}
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

static void set_ram_long(uint32_t address, uint32_t value)
{
    volatile uint8_t *p = ram(address);
    p[0] = (uint8_t)(value >> 24); p[1] = (uint8_t)(value >> 16);
    p[2] = (uint8_t)(value >> 8); p[3] = (uint8_t)value;
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
        {0x4a200U, 0xffff1ff4U}, {0x4a208U, 0xffff11d4U},
        {0x4a214U, THRESHOLDS}, {0x4a4ccU, 0xffff11d4U},
        {0x4a4d0U, 0xffff1ff4U}, {0x4a4e4U, METRICS},
        {0x4a4e8U, THRESHOLDS}, {0x4a4ecU, 0xffff24c0U}
    };
    if (*(volatile uint8_t *)MODE != 0x82U)
        return fail("initial", 0, "stock selector", *(volatile uint8_t *)MODE, 0x82U);
    for (i = 0; i < sizeof(stock_table); ++i)
        if (((volatile uint8_t *)TABLE)[i] != stock_table[i])
            return fail("initial", i, "stock table identity", ((volatile uint8_t *)TABLE)[i], stock_table[i]);
    for (i = 0; i < sizeof(stock_axis); ++i)
        if (((volatile uint8_t *)AXIS)[i] != stock_axis[i])
            return fail("initial", i, "stock axis identity", ((volatile uint8_t *)AXIS)[i], stock_axis[i]);
    for (i = 0; i < sizeof(stock_jump_table); ++i)
        if (((volatile uint8_t *)JUMP_TABLE)[i] != stock_jump_table[i])
            return fail("initial", i, "stock jump-table identity", ((volatile uint8_t *)JUMP_TABLE)[i], stock_jump_table[i]);
    for (i = 0; i < ARRAY_SIZE(aliases); ++i)
        if (*(volatile uint32_t *)aliases[i].pool != (uint32_t)ram(aliases[i].stock))
            return fail("initial", i, "declared RAM alias", *(volatile uint32_t *)aliases[i].pool, (uint32_t)ram(aliases[i].stock));
    return 1;
}

static void restore_calibrations(void)
{
    unsigned i;
    *(volatile uint8_t *)MODE = 0x82U;
    for (i = 0; i < sizeof(stock_table); ++i)
        ((volatile uint8_t *)TABLE)[i] = stock_table[i];
    for (i = 0; i < sizeof(stock_axis); ++i)
        ((volatile uint8_t *)AXIS)[i] = stock_axis[i];
    for (i = 0; i < sizeof(stock_jump_table); ++i)
        ((volatile uint8_t *)JUMP_TABLE)[i] = stock_jump_table[i];
}

static void seed_ram(void)
{
    unsigned i;
    for (i = 0; i < 65536U; ++i)
        ((volatile uint8_t *)RAM_BASE)[i] = (uint8_t)(0x5dU + i * 29U + (i >> 8));
    for (i = 0; i < 6U; ++i) {
        set_ram_word(THRESHOLDS + 2U * i, (uint16_t)(0x6d01U + i * 0x111U));
        set_ram_long(METRICS + 4U * i, 0x80010000U + i * 0x1234U);
    }
}

static void snapshot_inputs(void)
{
    unsigned i, j, at = 0;
    for (i = 0; i < 65536U; ++i)
        ram_before[i] = ((volatile uint8_t *)RAM_BASE)[i];
    for (i = 0; i < ARRAY_SIZE(calibrations); ++i)
        for (j = 0; j < calibrations[i].size; ++j)
            calibration_before[at++] = ((volatile uint8_t *)calibrations[i].address)[j];
}

static int preserve_inputs(const char *scope, unsigned long index, uint32_t output)
{
    unsigned i, j, at = 0;
    for (i = 0; i < 65536U; ++i) {
        if (output && (i == (output & 0xffffU) || i == ((output + 1U) & 0xffffU) ||
                       i == (COUNT & 0xffffU) || i == (STATUS & 0xffffU) || i == (BITMAP & 0xffffU)))
            continue;
        if (((volatile uint8_t *)RAM_BASE)[i] != ram_before[i])
            return fail(scope, index, "RAM preservation", i, ram_before[i]);
    }
    for (i = 0; i < ARRAY_SIZE(calibrations); ++i)
        for (j = 0; j < calibrations[i].size; ++j, ++at)
            if (((volatile uint8_t *)calibrations[i].address)[j] != calibration_before[at])
                return fail(scope, index, "calibration preservation",
                            calibrations[i].address + j, calibration_before[at]);
    return 1;
}

static struct context new_context(void)
{
    struct context context;
    unsigned i;
    for (i = 0; i < 15U; ++i)
        context.r[i] = 0x28765430U + i * 0x01030507U;
    context.gbr = 0x01000080U;
    context.mach = 0x13579bdfU;
    context.macl = 0x2468ace0U;
    return context;
}

static int invoke(const char *scope, unsigned long index, uint32_t entry,
                  const struct context *context, struct observation *out,
                  unsigned footprint, unsigned comparison)
{
    struct context before = *context;
    unsigned i, last_preserved = comparison ? 13U : 14U;
    memset(out, 0xa6, sizeof(*out));
    stock_invoke_knock_comparison(entry, context, out);
    if (memcmp(context, &before, sizeof(before)))
        return fail(scope, index, "entry context preservation", 1, 0);
    for (i = 8; i <= last_preserved; ++i)
        if (reg(out, i) != context->r[i])
            return fail(scope, index, "stock preserved register", reg(out, i), context->r[i]);
    if (out->exit[2] != context->macl || out->exit[3] != context->mach || out->exit[4] != context->gbr)
        return fail(scope, index, "stock special registers", out->exit[2], context->macl);
    if (out->sp != out->abi_before[10] - 152U)
        return fail(scope, index, "entry/exit SP", out->sp, out->abi_before[10] - 152U);
    if (out->exit[1] != out->continuation || (comparison && reg(out, 1) != out->continuation))
        return fail(scope, index, "driver return continuation", out->exit[1], out->continuation);
    if (memcmp(out->abi_before, out->abi_after, sizeof(out->abi_before)))
        return fail(scope, index, "C caller ABI restoration", 1, 0);
    for (i = 0; i < ARRAY_SIZE(abi_expected); ++i)
        if (out->abi_before[i] != abi_expected[i])
            return fail(scope, index, "C caller ABI sentinel", out->abi_before[i], abi_expected[i]);
    for (i = 0; i < 32U - footprint; ++i)
        if (out->frame_before[i] != out->frame_after[i])
            return fail(scope, index, "stack neighbor preservation", i, out->frame_before[i]);
    for (i = 32U; i < sizeof(out->frame_after); ++i)
        if (!(comparison && i == 44U) && out->frame_before[i] != out->frame_after[i])
            return fail(scope, index, "local frame preservation", i, out->frame_before[i]);
    if (frame_word(out->frame_before, 48) != out->continuation ||
        frame_word(out->frame_after, 48) != out->continuation)
        return fail(scope, index, "local continuation preservation", frame_word(out->frame_after, 48), out->continuation);
    return 1;
}

static int run_comparisons(void)
{
    unsigned long i;
    for (i = 0; i < ARRAY_SIZE(comparison_cases); ++i) {
        const struct comparison_case *test = &comparison_cases[i];
        struct context context = new_context();
        struct observation out;
        uint8_t channel = test->mode & 8U ? test->alternate : test->primary;
        uint32_t output = THRESHOLDS + 2U * (channel - 1U);
        unsigned fractional = test->speed > 32U && test->speed < 512U && test->speed % 32U;
        const char *scope = test->mode == 0x82U ? "stock-comparison" : "artificial-mode-comparison";
        restore_calibrations(); seed_ram();
        *(volatile uint8_t *)MODE = test->mode;
        *ram(PRIMARY) = test->primary; *ram(ALTERNATE) = test->alternate;
        set_ram_word(SPEED, test->speed);
        set_ram_long(METRICS + 4U * (channel - 1U), test->metric);
        *ram(COUNT) = test->count; *ram(STATUS) = test->status; *ram(BITMAP) = test->bitmap;
        snapshot_inputs();
        if (!invoke(scope, i, REGION_ENTRY, &context, &out, fractional ? 24U : 16U, 1U)) return 0;
        if (ram_word(output) != test->threshold)
            return fail(scope, i, "threshold publication", ram_word(output), test->threshold);
        if (*ram(COUNT) != test->out_count)
            return fail(scope, i, "event count", *ram(COUNT), test->out_count);
        if (*ram(STATUS) != test->out_status)
            return fail(scope, i, "status and unrelated bits", *ram(STATUS), test->out_status);
        if (*ram(BITMAP) != test->out_bitmap)
            return fail(scope, i, "selected bitmap and unrelated bits", *ram(BITMAP), test->out_bitmap);
        if (out.frame_after[44] != test->local_flag)
            return fail(scope, i, "local exceedance flag", out.frame_after[44], test->local_flag);
        if (reg(&out, 4) != (uint32_t)(channel - 1U) || reg(&out, 7) != test->metric ||
            reg(&out, 14) != (uint32_t)ram(0xffff1ff4U))
            return fail(scope, i, "channel/metric/base context", reg(&out, 7), test->metric);
        if (frame_word(out.frame_after, 28) != 0x80000000U + test->threshold ||
            frame_word(out.frame_after, 24) != 0x4a2f2U ||
            frame_word(out.frame_after, 16) != TABLE + 32U * (channel - 1U))
            return fail(scope, i, "nested saved frame", frame_word(out.frame_after, 28), 0x80000000U + test->threshold);
        if (frame_word(out.frame_after, 20) != test->saved_tail_slot)
            return fail(scope, i, "wrapper/linear tail frame", frame_word(out.frame_after, 20), test->saved_tail_slot);
        if (fractional && (frame_word(out.frame_after, 12) != 0x26506U ||
                           frame_word(out.frame_after, 8) != 0x26c78U))
            return fail(scope, i, "fractional nested frame", frame_word(out.frame_after, 8), 0x26c78U);
        if (!preserve_inputs(scope, i, output)) return 0;
        ++completed;
    }
    return 1;
}

static int run_shifts(void)
{
    unsigned long i;
    for (i = 0; i < ARRAY_SIZE(shift_cases); ++i) {
        const struct shift_case *test = &shift_cases[i];
        struct context context = new_context();
        struct observation out;
        restore_calibrations(); seed_ram();
        context.r[0] = test->value; context.r[1] = (uint32_t)test->count;
        snapshot_inputs();
        if (!invoke("direct-shift", i, SHIFT_ENTRY, &context, &out, 4U, 0U)) return 0;
        if (reg(&out, 0) != test->expected || reg(&out, 2) != context.r[2])
            return fail("direct-shift", i, "result/R2 preservation", reg(&out, 0), test->expected);
        if (frame_word(out.frame_after, 28) != context.r[2])
            return fail("direct-shift", i, "saved R2 frame", frame_word(out.frame_after, 28), context.r[2]);
        if (!preserve_inputs("direct-shift", i, 0U)) return 0;
        ++completed;
    }
    return 1;
}

int main(void)
{
    if (!verify_initial_calibrations() || !run_comparisons() || !run_shifts()) return 1;
    if (completed != KNOCK_COMPARISON_CASE_COUNT)
        return !fail("total", 0, "case count", completed, KNOCK_COMPARISON_CASE_COUNT);
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY, completed);
    return 0;
}
