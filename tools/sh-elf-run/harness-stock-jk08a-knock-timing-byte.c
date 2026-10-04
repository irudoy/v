/* Raw low-word publication and signed division from explicit incoming R2. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "stock-jk08a-knock-timing-byte-cases.h"

#define RAM_BASE 0x01000000U
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))

struct context { uint32_t r[15], gbr, mach, macl; };
struct observation {
    uint32_t exit[20], sp, continuation, abi_before[12], abi_after[12];
    uint8_t frame_before[52], frame_after[52];
};
extern void stock_invoke_knock_timing_byte(uint32_t entry,
    const struct context *context, struct observation *observation);

static uint8_t ram_before[65536], calibration_before[16];
static unsigned long completed;
static const uint32_t abi_expected[10] = {
    0x18283848U, 0x19293949U, 0x1a2a3a4aU, 0x1b2b3b4bU,
    0x1c2c3c4cU, 0x1d2d3d4dU, 0x1e2e3e4eU, 0x12344321U,
    0x10203040U, 0x50607080U
};
static const struct { uint32_t address, size; } calibrations[] = {
    {0x495daU, 2}, {0x496acU, 4}, {0x496c8U, 4},
    {0x499aeU, 2}, {0x49b38U, 4}
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

static uint16_t ram_word(uint32_t address)
{
    volatile uint8_t *p = ram(address);
    return (uint16_t)((uint16_t)p[0] << 8 | p[1]);
}

static int verify_initial_context_anchors(void)
{
    if (*(volatile uint16_t *)0x495daU != 0xd934U ||
        *(volatile uint16_t *)0x499aeU != 0xd962U ||
        *(volatile uint32_t *)0x496acU != 0xffff22f8U ||
        *(volatile uint32_t *)0x49b38U != 0xffff22f8U)
        return fail("initial", 0, "R9 stock context anchors", 1, 0);
    if (*(volatile uint32_t *)0x496c8U != (uint32_t)ram(0xffff120eU))
        return fail("initial", 0, "declared word-state RAM alias", *(volatile uint32_t *)0x496c8U, (uint32_t)ram(0xffff120eU));
    return 1;
}

static void seed_and_snapshot(void)
{
    unsigned i, j, at = 0;
    for (i = 0; i < 65536U; ++i) {
        uint8_t value = (uint8_t)(0x5dU + i * 29U + (i >> 8));
        ((volatile uint8_t *)RAM_BASE)[i] = value;
        ram_before[i] = value;
    }
    for (i = 0; i < ARRAY_SIZE(calibrations); ++i)
        for (j = 0; j < calibrations[i].size; ++j)
            calibration_before[at++] = ((volatile uint8_t *)calibrations[i].address)[j];
}

static int preserve_calibrations(const char *scope, unsigned long index)
{
    unsigned i, j, at = 0;
    for (i = 0; i < ARRAY_SIZE(calibrations); ++i)
        for (j = 0; j < calibrations[i].size; ++j, ++at)
            if (((volatile uint8_t *)calibrations[i].address)[j] != calibration_before[at])
                return fail(scope, index, "calibration/context-anchor preservation",
                            calibrations[i].address + j, calibration_before[at]);
    return 1;
}

static int preserve_ram(const char *scope, unsigned long index)
{
    unsigned i;
    for (i = 0; i < 65536U; ++i) {
        if (i == (WORD_STATE & 0xffffU) || i == ((WORD_STATE + 1U) & 0xffffU) ||
            i == (BYTE_STATE & 0xffffU)) continue;
        if (((volatile uint8_t *)RAM_BASE)[i] != ram_before[i])
            return fail(scope, index, "RAM preservation", i, ram_before[i]);
    }
    return preserve_calibrations(scope, index);
}

static int preserve_neighbors(const char *scope, unsigned long index)
{
    unsigned i;
    for (i = (WORD_STATE & 0xffffU) - 2U; i < (WORD_STATE & 0xffffU) + 4U; ++i)
        if (i != (WORD_STATE & 0xffffU) && i != ((WORD_STATE + 1U) & 0xffffU) &&
            ((volatile uint8_t *)RAM_BASE)[i] != ram_before[i])
            return fail(scope, index, "word-state neighbors", i, ram_before[i]);
    for (i = (BYTE_STATE & 0xffffU) - 2U; i < (BYTE_STATE & 0xffffU) + 3U; ++i)
        if (i != (BYTE_STATE & 0xffffU) && ((volatile uint8_t *)RAM_BASE)[i] != ram_before[i])
            return fail(scope, index, "byte-state neighbors", i, ram_before[i]);
    return preserve_calibrations(scope, index);
}

static struct context new_context(uint32_t input)
{
    struct context context;
    unsigned i;
    for (i = 0; i < 15U; ++i)
        context.r[i] = 0x28765430U + i * 0x01030507U;
    context.r[2] = input;
    context.r[7] = CONVERSION_ENTRY;
    context.r[9] = (uint32_t)ram(0xffff22f8U);
    context.gbr = 0x01000080U;
    context.mach = 0x13579bdfU;
    context.macl = 0x2468ace0U;
    return context;
}

static int run_case(const char *scope, unsigned long index, uint32_t input,
                    int32_t signed_word, int32_t quotient)
{
    struct context context = new_context(input), before = context;
    struct observation out;
    unsigned i;
    memset(&out, 0xa6, sizeof(out));
    stock_invoke_knock_timing_byte(CONVERSION_ENTRY, &context, &out);
    if (memcmp(&context, &before, sizeof(before)))
        return fail(scope, index, "entry context preservation", 1, 0);
    if (ram_word(WORD_STATE) != (uint16_t)input || *ram(BYTE_STATE) != (uint8_t)quotient)
        return fail(scope, index, "raw word/signed byte publication", *ram(BYTE_STATE), (uint8_t)quotient);
    for (i = 0; i < 15U; ++i) {
        uint32_t expected = context.r[i];
        if (i == 0U) expected = (uint32_t)quotient;
        if (i == 2U) expected = (uint32_t)quotient & 0x00ffffffU;
        if (i == 6U) expected = quotient < 0 ? 0xffffffffU : 0U;
        if (i == 8U) expected = (uint32_t)ram(0xffff120eU);
        if (i == 12U) expected = (uint32_t)signed_word;
        if (reg(&out, i) != expected)
            return fail(scope, index, "stock fragment register", reg(&out, i), expected);
    }
    if ((out.exit[0] & 1U) != (signed_word >= 0))
        return fail(scope, index, "stock sign-branch T", out.exit[0] & 1U, signed_word >= 0);
    if (out.exit[2] != context.macl || out.exit[3] != context.mach || out.exit[4] != context.gbr)
        return fail(scope, index, "stock special registers", out.exit[2], context.macl);
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
    if (!preserve_neighbors(scope, index)) return 0;
    ++completed;
    return 1;
}

static int run_literals(void)
{
    unsigned long i;
    for (i = 0; i < ARRAY_SIZE(literal_cases); ++i) {
        const struct literal_case *test = &literal_cases[i];
        seed_and_snapshot();
        if (!run_case("literal-boundary", i, test->input, test->signed_word, test->quotient) ||
            !preserve_ram("literal-boundary", i)) return 0;
    }
    return 1;
}

static int run_sweep(void)
{
    uint32_t raw;
    for (raw = 0; raw < KNOCK_TIMING_BYTE_SWEEP_CASES; ++raw) {
        int32_t value = raw < 32768U ? (int32_t)raw : (int32_t)raw - 65536;
        /* Sweep arithmetic uses C signed division, separate from literal anchors. */
        int32_t quotient = value / 256;
        if (!(raw & 255U)) seed_and_snapshot();
        if (!run_case("exhaustive-low-word", raw, raw, value, quotient)) return 0;
        /* Full RAM preservation is observed at each 256-case block boundary. */
        if ((raw & 255U) == 255U && !preserve_ram("sweep-block", raw)) return 0;
    }
    return 1;
}

int main(void)
{
    if (!verify_initial_context_anchors() || !run_literals() || !run_sweep()) return 1;
    if (completed != KNOCK_TIMING_BYTE_CASE_COUNT)
        return !fail("total", 0, "case count", completed, KNOCK_TIMING_BYTE_CASE_COUNT);
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=jk08a-knock-timing-byte cases=%lu\n", completed);
    return 0;
}
