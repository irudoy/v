/* Post-lookup widened difference and stock slew/cap from explicit contexts. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "stock-jk08a-knock-state-selection-cases.h"

#define RAM_BASE 0x01000000U
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))

struct context { uint32_t r[15], gbr, mach, macl, first_low7; };
struct observation {
    uint32_t exit[20], sp, continuation, abi_before[12], abi_after[12];
    uint8_t frame_before[64], frame_after[64];
};
extern void stock_invoke_knock_state_selection(uint32_t entry,
    const struct context *context, struct observation *observation);

static uint8_t ram_before[65536], calibration_before[68];
static unsigned long completed;
static const uint32_t abi_expected[10] = {
    0x18283848U, 0x19293949U, 0x1a2a3a4aU, 0x1b2b3b4bU,
    0x1c2c3c4cU, 0x1d2d3d4dU, 0x1e2e3e4eU, 0x12344321U,
    0x10203040U, 0x50607080U
};
static const struct { uint32_t address, size; } calibrations[] = {
    {0x9078U, 2}, {0x493fcU, 4}, {0x495daU, 2}, {0x495e8U, 2},
    {0x495f6U, 2}, {0x495faU, 10}, {0x49610U, 4},
    {0x4965cU, 4}, {0x49678U, 4}, {0x496acU, 4}, {0x496b4U, 4},
    {0x496c0U, 4}, {0x496c4U, 4}, {0x499aeU, 2},
    {0x49b28U, 4}, {0x49b2cU, 4}, {0x49b38U, 4}, {0x49b3cU, 4}
};

static volatile uint8_t *ram(uint32_t address)
{ return (volatile uint8_t *)(RAM_BASE + (address & 0xffffU)); }

static uint32_t reg(const struct observation *out, unsigned n)
{ return out->exit[19U - n]; }

static uint32_t frame_word(const uint8_t *frame, unsigned offset)
{
    return (uint32_t)frame[offset] << 24 | (uint32_t)frame[offset+1] << 16 |
           (uint32_t)frame[offset+2] << 8 | frame[offset+3];
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

static int verify_initial_calibrations(void)
{
    unsigned i, j;
    static const struct { uint32_t address, size; uint8_t bytes[10]; } anchors[] = {
        {0x493fcU, 4, {0xd0,0x97,0x40,0x1e}},
        {0x495daU, 2, {0xd9,0x34}},
        {0x495e8U, 2, {0xd4,0x32}},
        {0x495f6U, 2, {0xdd,0x32}},
        {0x495faU, 10, {0x4d,0x0b,0x66,0xe3,0xc9,0x7f,0xd4,0x30,0x80,0xfc}},
        {0x49610U, 4, {0x4d,0x0b,0x67,0x2d}},
        {0x499aeU, 2, {0xd9,0x62}}
    };
    static const struct { uint32_t pool, stock; } aliases[] = {
        {0x4965cU, 0xffff2458U}, {0x49678U, 0xffff128cU},
        {0x496acU, 0xffff22f8U}, {0x49b28U, 0xffff124cU},
        {0x49b2cU, 0xffff128cU}, {0x49b38U, 0xffff22f8U}
    };
    static const struct { uint32_t pool, value; } pointers[] = {
        {0x496b4U, 0x9a1aU}, {0x496c0U, 0x26230U},
        {0x496c4U, 0x9b1aU}, {0x49b3cU, 0x9078U}
    };
    if (*(volatile uint16_t *)0x9078U != 1280U)
        return fail("initial", 0, "stock slew calibration", *(volatile uint16_t *)0x9078U, 1280U);
    for (i = 0; i < ARRAY_SIZE(anchors); ++i)
        for (j = 0; j < anchors[i].size; ++j)
            if (((volatile uint8_t *)anchors[i].address)[j] != anchors[i].bytes[j])
                return fail("initial", i, "static call/input/base anchor",
                            ((volatile uint8_t *)anchors[i].address)[j], anchors[i].bytes[j]);
    for (i = 0; i < ARRAY_SIZE(aliases); ++i)
        if (*(volatile uint32_t *)aliases[i].pool != (uint32_t)ram(aliases[i].stock))
            return fail("initial", i, "declared RAM alias",
                        *(volatile uint32_t *)aliases[i].pool, (uint32_t)ram(aliases[i].stock));
    for (i = 0; i < ARRAY_SIZE(pointers); ++i)
        if (*(volatile uint32_t *)pointers[i].pool != pointers[i].value)
            return fail("initial", i, "stock lookup/calibration pointer",
                        *(volatile uint32_t *)pointers[i].pool, pointers[i].value);
    return 1;
}

static void seed_and_snapshot(const struct selection_case *test)
{
    unsigned i, j, at=0;
    for (i=0; i<65536U; ++i)
        ((volatile uint8_t *)RAM_BASE)[i]=(uint8_t)(0x5dU+i*29U+(i>>8));
    set_ram_word(SOURCE_STATE, (uint16_t)test->source);
    set_ram_word(TARGET_STATE, (uint16_t)test->target);
    *ram(NEGATIVE_BOUND)=test->negative_bound;
    *ram(GATE69)=test->gate69;
    *ram(GATE67)=test->gate67;
    set_ram_word(WORD_OUTPUT, 0x6d01U);
    *ram(BYTE_OUTPUT)=0x9bU;
    for (i=0; i<65536U; ++i)
        ram_before[i]=((volatile uint8_t *)RAM_BASE)[i];
    for (i=0; i<ARRAY_SIZE(calibrations); ++i)
        for (j=0; j<calibrations[i].size; ++j)
            calibration_before[at++]=((volatile uint8_t *)calibrations[i].address)[j];
}

static int preserve_inputs(const char *scope, unsigned long index)
{
    unsigned i, j, at=0;
    for (i=0; i<65536U; ++i)
        if (((volatile uint8_t *)RAM_BASE)[i] != ram_before[i])
            return fail(scope, index, "whole RAM/input preservation",
                        ((volatile uint8_t *)RAM_BASE)[i], ram_before[i]);
    for (i=0; i<ARRAY_SIZE(calibrations); ++i)
        for (j=0; j<calibrations[i].size; ++j, ++at)
            if (((volatile uint8_t *)calibrations[i].address)[j] != calibration_before[at])
                return fail(scope, index, "calibration/pool/anchor preservation",
                            ((volatile uint8_t *)calibrations[i].address)[j], calibration_before[at]);
    return 1;
}

static struct context new_context(const struct selection_case *test)
{
    struct context context;
    unsigned i;
    for (i=0; i<15U; ++i)
        context.r[i]=0x28765430U+i*0x01030507U;
    context.r[0]=test->raw_second;
    context.r[7]=test->alternative_entry ? ALTERNATIVE_ENTRY : POST_LOOKUP_ENTRY;
    context.r[9]=(uint32_t)ram(0xffff22f8U);
    context.gbr=test->alternative_entry ? 0x01000080U : (uint32_t)ram(0xffff2458U);
    context.mach=0x13579bdfU;
    context.macl=0x2468ace0U;
    context.first_low7=test->first;
    return context;
}

static int run_case(unsigned long index, const struct selection_case *test)
{
    const char *scope=test->alternative_entry ? "standalone-alternative" : "explicit-post-lookup";
    struct context context=new_context(test), before=context;
    struct observation out;
    unsigned i;
    seed_and_snapshot(test);
    memset(&out, 0xa6, sizeof(out));
    stock_invoke_knock_state_selection(context.r[7], &context, &out);
    if (memcmp(&context, &before, sizeof(before)))
        return fail(scope, index, "entry context preservation", 1, 0);
    for (i=0; i<15U; ++i)
        if (reg(&out,i) != test->expected[i])
            return fail(scope, index, "literal fragment register", reg(&out,i), test->expected[i]);
    if ((out.exit[0]&1U) != test->expected_t)
        return fail(scope, index, "literal final T", out.exit[0]&1U, test->expected_t);
    if (out.exit[2] != test->expected_macl)
        return fail(scope, index, "literal stock MACL", out.exit[2], test->expected_macl);
    if (out.exit[3] != context.mach)
        return fail(scope, index, "stock MACH preservation", out.exit[3], context.mach);
    if (out.exit[4] != context.gbr)
        return fail(scope, index, "stock GBR preservation", out.exit[4], context.gbr);
    if (out.sp != out.abi_before[10]-164U)
        return fail(scope, index, "stock SP preservation", out.sp, out.abi_before[10]-164U);
    if (out.exit[1] != out.continuation)
        return fail(scope, index, "driver PR preservation", out.exit[1], out.continuation);
    if (memcmp(out.abi_before, out.abi_after, sizeof(out.abi_before)))
        return fail(scope, index, "C caller ABI restoration", 1, 0);
    for (i=0; i<ARRAY_SIZE(abi_expected); ++i)
        if (out.abi_before[i] != abi_expected[i])
            return fail(scope, index, "C caller ABI sentinel", out.abi_before[i], abi_expected[i]);
    if (out.frame_before[44] != test->first || out.frame_after[44] != test->first)
        return fail(scope, index, "first low7 input preservation", out.frame_after[44], test->first);
    if (out.frame_before[48] != 0xa3U)
        return fail(scope, index, "distinct second-slot seed", out.frame_before[48], 0xa3U);
    if (!test->alternative_entry && out.frame_after[48] != test->stored_second)
        return fail(scope, index, "natural second low7 byte store", out.frame_after[48], test->stored_second);
    for (i=0; i<sizeof(out.frame_before); ++i)
        if ((test->alternative_entry || i != 48U) && out.frame_before[i] != out.frame_after[i])
            return fail(scope, index, "stack/local neighbor preservation", out.frame_after[i], out.frame_before[i]);
    if (frame_word(out.frame_before,56) != out.continuation ||
        frame_word(out.frame_after,56) != out.continuation)
        return fail(scope, index, "separate local continuation preservation", frame_word(out.frame_after,56), out.continuation);
    if (!preserve_inputs(scope,index)) return 0;
    ++completed;
    return 1;
}

int main(void)
{
    unsigned long i;
    if (!verify_initial_calibrations()) return 1;
    for (i=0; i<ARRAY_SIZE(selection_cases); ++i)
        if (!run_case(i,&selection_cases[i])) return 1;
    if (completed != KNOCK_STATE_SELECTION_CASE_COUNT)
        return !fail("total", 0, "case count", completed, KNOCK_STATE_SELECTION_CASE_COUNT);
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);
    return 0;
}
