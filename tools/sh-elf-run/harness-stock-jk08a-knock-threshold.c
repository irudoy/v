/* Bounded raw-count threshold execution with explicit artificial contexts. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "stock-jk08a-knock-threshold-cases.h"

#define RAM_BASE 0x01000000U
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))

struct context { uint32_t r[15], gbr, mach, macl; };
struct observation {
    uint32_t exit[20], sp, continuation, abi_before[12], abi_after[12];
    uint8_t frame_before[32], frame_after[32];
};
extern void stock_invoke_knock_threshold(uint32_t entry,
    const struct context *context, struct observation *observation);

static uint8_t ram_before[65536], calibration_before[267];
static unsigned long completed;
static const uint32_t abi_expected[10] = {
    0x18283848U, 0x19293949U, 0x1a2a3a4aU, 0x1b2b3b4bU,
    0x1c2c3c4cU, 0x1d2d3d4dU, 0x1e2e3e4eU, 0x12344321U,
    0x10203040U, 0x50607080U
};
static const struct { uint32_t address, size; } calibrations[] = {
    {MODE, 1}, {TABLE, 194}, {AXIS, 32}, {0x2651cU, 8},
    {0x269c0U, 4}, {0x4a1fcU, 28}
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

static void write_word(uint32_t address, uint16_t value)
{
    volatile uint8_t *p = (volatile uint8_t *)address;
    p[0] = (uint8_t)(value >> 8); p[1] = (uint8_t)value;
}

static void set_ram_word(uint32_t address, uint16_t value)
{ write_word((uint32_t)ram(address), value); }

static uint16_t ram_word(uint32_t address)
{
    volatile uint8_t *p = ram(address);
    return (uint16_t)((uint16_t)p[0] << 8 | p[1]);
}

static int verify_initial_calibrations(void)
{
    unsigned i;
    if (*(volatile uint8_t *)MODE != 0x82U)
        return fail("initial", 0, "stock selector", *(volatile uint8_t *)MODE, 0x82U);
    for (i = 0; i < sizeof(stock_table); ++i)
        if (((volatile uint8_t *)TABLE)[i] != stock_table[i])
            return fail("initial", i, "stock table identity", ((volatile uint8_t *)TABLE)[i], stock_table[i]);
    for (i = 0; i < sizeof(stock_axis); ++i)
        if (((volatile uint8_t *)AXIS)[i] != stock_axis[i])
            return fail("initial", i, "stock axis identity", ((volatile uint8_t *)AXIS)[i], stock_axis[i]);
    if (*(volatile uint32_t *)0x4a200U != (uint32_t)ram(0xffff1ff4U) ||
        *(volatile uint32_t *)0x4a208U != (uint32_t)ram(0xffff11d4U) ||
        *(volatile uint32_t *)0x4a214U != (uint32_t)ram(THRESHOLDS))
        return fail("initial", 0, "declared RAM aliases", 1, 0);
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
}

static void seed_ram(void)
{
    unsigned i;
    for (i = 0; i < 65536U; ++i)
        ((volatile uint8_t *)RAM_BASE)[i] = (uint8_t)(0x5dU + i * 29U + (i >> 8));
    for (i = 0; i < 6U; ++i)
        set_ram_word(THRESHOLDS + 2U * i, (uint16_t)(0x6d01U + i * 0x111U));
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
        if (output && (i == (output & 0xffffU) || i == ((output + 1U) & 0xffffU)))
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
                  unsigned footprint)
{
    struct context before = *context;
    unsigned i;
    memset(out, 0xa6, sizeof(*out));
    stock_invoke_knock_threshold(entry, context, out);
    if (memcmp(context, &before, sizeof(before)))
        return fail(scope, index, "entry context preservation", 1, 0);
    for (i = 8; i <= 14; ++i)
        if (reg(out, i) != context->r[i])
            return fail(scope, index, "stock preserved register", reg(out, i), context->r[i]);
    if (out->exit[2] != context->macl || out->exit[3] != context->mach || out->exit[4] != context->gbr)
        return fail(scope, index, "stock special registers", out->exit[2], context->macl);
    if (out->sp != out->abi_before[10] - 132U || out->exit[1] != out->continuation)
        return fail(scope, index, "stock SP/PR restoration", out->sp, out->abi_before[10] - 132U);
    if (memcmp(out->abi_before, out->abi_after, sizeof(out->abi_before)))
        return fail(scope, index, "C caller ABI restoration", 1, 0);
    for (i = 0; i < ARRAY_SIZE(abi_expected); ++i)
        if (out->abi_before[i] != abi_expected[i])
            return fail(scope, index, "C caller ABI sentinel", out->abi_before[i], abi_expected[i]);
    for (i = 0; i < 32U - footprint; ++i)
        if (out->frame_before[i] != out->frame_after[i])
            return fail(scope, index, "stack neighbor preservation", i, out->frame_before[i]);
    return 1;
}

static int run_accessors(void)
{
    unsigned long i;
    for (i = 0; i < ARRAY_SIZE(accessor_cases); ++i) {
        const struct accessor_case *test = &accessor_cases[i];
        struct context context = new_context();
        struct observation out;
        uint8_t channel = test->mode & 8U ? test->alternate : test->primary;
        uint32_t output = THRESHOLDS + 2U * (channel - 1U);
        unsigned fractional = test->speed > 32U && test->speed < 512U && test->speed % 32U;
        const char *scope = test->artificial ? "artificial-mode" : "stock-accessor";
        restore_calibrations(); seed_ram();
        *(volatile uint8_t *)MODE = test->mode;
        *ram(PRIMARY) = test->primary; *ram(ALTERNATE) = test->alternate;
        set_ram_word(SPEED, test->speed); snapshot_inputs();
        if (!invoke(scope, i, REGION_ENTRY, &context, &out, fractional ? 24U : 16U))
            return 0;
        if (reg(&out, 0) != 2U * channel || reg(&out, 2) != test->expected ||
            ram_word(output) != test->expected || reg(&out, 5) != (uint32_t)ram(0xffff2142U))
            return fail(scope, i, "index/threshold/publication", reg(&out, 2), test->expected);
        if (frame_word(out.frame_after, 28) != context.r[14] ||
            frame_word(out.frame_after, 24) != out.continuation ||
            frame_word(out.frame_after, 16) != TABLE + 32U * (channel - 1U))
            return fail(scope, i, "accessor saved frame", frame_word(out.frame_after, 24), out.continuation);
        if (fractional && (frame_word(out.frame_after, 12) != 0x26506U ||
                           frame_word(out.frame_after, 8) != DIVIDER_ENTRY))
            return fail(scope, i, "nested caller frame", frame_word(out.frame_after, 8), DIVIDER_ENTRY);
        if (!preserve_inputs(scope, i, output)) return 0;
        ++completed;
    }
    return 1;
}

static int run_wrappers(void)
{
    unsigned long i;
    for (i = 0; i < ARRAY_SIZE(wrapper_cases); ++i) {
        const struct wrapper_case *test = &wrapper_cases[i];
        struct context context = new_context(); struct observation out;
        uint16_t coordinate = (uint16_t)test->coordinate;
        unsigned j, fractional = coordinate > 32U && coordinate < 512U && coordinate % 32U;
        const char *scope = test->pattern ? "artificial-table" : "direct-wrapper";
        restore_calibrations(); seed_ram();
        if (test->pattern)
            for (j = 0; j < 16U; ++j)
                write_word(TABLE + 2U * j, table_patterns[test->pattern - 1U][j]);
        context.r[4] = TABLE + 32U * (test->row - 1U);
        context.r[5] = AXIS; context.r[6] = test->coordinate;
        snapshot_inputs();
        if (!invoke(scope, i, WRAPPER_ENTRY, &context, &out, fractional ? 16U : 8U)) return 0;
        if (reg(&out, 0) != test->expected)
            return fail(scope, i, "threshold return", reg(&out, 0), test->expected);
        if (frame_word(out.frame_after, 24) != context.r[4])
            return fail(scope, i, "wrapper saved row", frame_word(out.frame_after, 24), context.r[4]);
        if (fractional && (frame_word(out.frame_after, 20) != 0x26506U ||
                           frame_word(out.frame_after, 16) != DIVIDER_ENTRY))
            return fail(scope, i, "wrapper nested frame", frame_word(out.frame_after, 16), DIVIDER_ENTRY);
        if (!preserve_inputs(scope, i, 0)) return 0;
        ++completed;
    }
    return 1;
}

static int run_axes(void)
{
    unsigned long i;
    for (i = 0; i < ARRAY_SIZE(axis_cases); ++i) {
        const struct axis_case *test = &axis_cases[i];
        struct context context = new_context(); struct observation out; unsigned j;
        restore_calibrations(); seed_ram();
        if (test->pattern)
            for (j = 0; j < 16U; ++j) write_word(AXIS + 2U * j, wide_axis[j]);
        context.r[0] = AXIS; context.r[4] = 30U; context.r[5] = test->coordinate;
        snapshot_inputs();
        if (!invoke("direct-axis", i, AXIS_ENTRY, &context, &out, test->fraction ? 8U : 0U)) return 0;
        if (reg(&out, 4) != test->offset || reg(&out, 5) != test->fraction)
            return fail("direct-axis", i, "offset/fraction", reg(&out, 5), test->fraction);
        if (test->fraction && (frame_word(out.frame_after, 28) != out.continuation ||
                              frame_word(out.frame_after, 24) != DIVIDER_ENTRY))
            return fail("direct-axis", i, "axis saved frame", frame_word(out.frame_after, 24), DIVIDER_ENTRY);
        if (!preserve_inputs("direct-axis", i, 0)) return 0;
        ++completed;
    }
    return 1;
}

static int run_linear(void)
{
    unsigned long i;
    for (i = 0; i < ARRAY_SIZE(linear_cases); ++i) {
        const struct linear_case *test = &linear_cases[i];
        struct context context = new_context(); struct observation out;
        restore_calibrations(); seed_ram();
        context.r[0] = test->left; context.r[2] = test->right; context.r[3] = test->fraction;
        snapshot_inputs();
        if (!invoke("direct-linear", i, LINEAR_ENTRY, &context, &out,
                    test->left > test->right ? 4U : 0U)) return 0;
        if (reg(&out, 0) != test->expected)
            return fail("direct-linear", i, "directional rounding", reg(&out, 0), test->expected);
        if (test->left > test->right && frame_word(out.frame_after, 28) != test->left)
            return fail("direct-linear", i, "saved left endpoint", frame_word(out.frame_after, 28), test->left);
        if (!preserve_inputs("direct-linear", i, 0)) return 0;
        ++completed;
    }
    return 1;
}

static int run_dividers(void)
{
    unsigned long i;
    for (i = 0; i < ARRAY_SIZE(divider_cases); ++i) {
        const struct divider_case *test = &divider_cases[i];
        struct context context = new_context(); struct observation out;
        restore_calibrations(); seed_ram();
        context.r[0] = test->divisor; context.r[1] = test->numerator;
        snapshot_inputs();
        if (!invoke("direct-divider", i, DIVIDER_ENTRY, &context, &out, test->divisor ? 4U : 0U)) return 0;
        if (reg(&out, 0) != test->expected || reg(&out, 2) != context.r[2])
            return fail("direct-divider", i, "quotient/saved R2", reg(&out, 0), test->expected);
        if (test->divisor && frame_word(out.frame_after, 28) != context.r[2])
            return fail("direct-divider", i, "saved R2 frame", frame_word(out.frame_after, 28), context.r[2]);
        if (!preserve_inputs("direct-divider", i, 0)) return 0;
        ++completed;
    }
    return 1;
}

int main(void)
{
    if (!verify_initial_calibrations() || !run_accessors() || !run_wrappers() ||
        !run_axes() || !run_linear() || !run_dividers())
        return 1;
    restore_calibrations();
    if (completed != KNOCK_CASE_COUNT) return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY, completed);
    return 0;
}
