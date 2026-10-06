/* Bounded scheduler copy, real helper tails, and independent full-state checks. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "injection-snapshot-cases.h"

#define RAM_BASE 0x01000000U
#define ALIAS(a) (RAM_BASE + ((a) & 65535U))
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
struct context { uint32_t r[15], gbr, mach, macl, entry_t; };
struct observation {
    uint32_t exit[20], sp, continuation, abi_before[12], abi_after[12];
    uint8_t frame_before[96], frame_after[96];
    uint32_t sr_before;
};
_Static_assert(sizeof(struct context) == 76U, "context byte contract");
_Static_assert(offsetof(struct context, entry_t) == 72U, "prepared SR input offset");
_Static_assert(sizeof(struct observation) == 380U, "complete observation contract");
_Static_assert(offsetof(struct observation, frame_before) == 184U, "frame input offset");
_Static_assert(offsetof(struct observation, frame_after) == 280U, "frame output offset");
_Static_assert(offsetof(struct observation, sr_before) == 376U, "prepared SR offset");
extern void stock_invoke_injection_start_delay(uint32_t, const struct context *, struct observation *);
static uint8_t ram_before[65536];
static uint8_t pools_before[8];
static unsigned long completed;
static const uint32_t abi_expected[10] = {
    0x18283848U, 0x19293949U, 0x1a2a3a4aU, 0x1b2b3b4bU,
    0x1c2c3c4cU, 0x1d2d3d4dU, 0x1e2e3e4eU, 0x12344321U, 0x10203040U, 0x50607080U
};
static volatile uint8_t *ram(uint32_t address) {
    return (volatile uint8_t *)(uintptr_t)ALIAS(address);
}
static uint32_t reg(const struct observation *out, unsigned index) {
    return out->exit[19U - index];
}
static void frame_set(uint8_t *frame, unsigned offset, uint32_t value) {
    frame[offset] = (uint8_t)(value >> 24);
    frame[offset + 1U] = (uint8_t)(value >> 16);
    frame[offset + 2U] = (uint8_t)(value >> 8);
    frame[offset + 3U] = (uint8_t)value;
}
static int fail(unsigned long index, const char *field, uint32_t actual, uint32_t expected) {
    fprintf(stderr, "injection_snapshot[%lu] %s actual=%08lx expected=%08lx\n",
            index, field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}
static int initial(void) {
    if (ALIAS(LEAD_SOURCE) - 52U != 0x010023bcU || ALIAS(ANGLE_SOURCE) - 3U != 0x010023bcU
        || ALIAS(LEAD_SNAPSHOT) - 52U != 0x01002330U || ALIAS(ANGLE_SNAPSHOT) - 3U != 0x01002330U)
        return fail(0, "four independent byte-owner offsets", 1, 0);
    if (*(volatile uint32_t *)0x213a0U != 0x01002330U
        || *(volatile uint32_t *)0x213a4U != 0x010023bcU)
        return fail(0, "two declared data-pointer aliases", 1, 0);
    return 1;
}
static void seed(unsigned long index, const struct snapshot_case *test) {
    unsigned i;
    if (!test->carry)
        for (i = 0; i < 65536U; ++i)
            ((volatile uint8_t *)RAM_BASE)[i] = (uint8_t)(0x5dU + i * 19U + (i >> 8) + index);
    for (i = 0; i < test->length; ++i) {
        uint8_t value = test->pattern == 1U ? (i == test->position ? 0x81U : 0U)
                       : (uint8_t)(test->seed + i * 29U);
        ram(test->source)[i] = value;
    }
    for (i = 0; i < 65536U; ++i)
        ram_before[i] = ((volatile uint8_t *)RAM_BASE)[i];
    for (i = 0; i < 8U; ++i)
        pools_before[i] = ((volatile uint8_t *)0x213a0U)[i];
}
static int run_case(unsigned long index, const struct snapshot_case *test) {
    struct context context, before;
    struct observation out;
    uint8_t expected_frame[96];
    unsigned i;
    memcpy(context.r, test->incoming, sizeof(context.r));
    context.gbr = test->variant ? 0xd8b6a491U : 0x456789abU;
    context.mach = test->variant ? 0xf1e2d3c4U : 0x13579bdfU;
    context.macl = test->variant ? 0x9274b6d8U : 0x2468ace0U;
    context.entry_t = test->entry_t;
    before = context;
    seed(index, test);
    memset(&out, 0xa6, sizeof(out));
    stock_invoke_injection_start_delay(test->entry, &context, &out);
    if (memcmp(&context, &before, sizeof(context)))
        return fail(index, "immutable complete entry context", 1, 0);
    for (i = 0; i < 15U; ++i) {
        uint32_t expected = test->expected[i];
        if (test->entry == REGION_ENTRY && i == 7U)
            expected = out.continuation;
        if (reg(&out, i) != expected)
            return fail(index, "literal full GPR", i, expected);
    }
    if ((out.sr_before & 0x301U) != test->entry_t)
        return fail(index, "actual prepared M/Q/T", out.sr_before & 0x301U, test->entry_t);
    if (out.exit[0] != ((out.sr_before & ~1U) | test->expected_t))
        return fail(index, "complete SR", out.exit[0], (out.sr_before & ~1U) | test->expected_t);
    if (out.exit[2] != context.macl || out.exit[3] != context.mach || out.exit[4] != context.gbr)
        return fail(index, "MACL/MACH/GBR preservation", 1, 0);
    if (out.sp != out.abi_before[10] - 164U || out.exit[1] != out.continuation)
        return fail(index, "natural helper and caller boundary PR/SP", 1, 0);
    if (memcmp(out.abi_before, out.abi_after, sizeof(out.abi_before)))
        return fail(index, "independent C caller ABI", 1, 0);
    for (i = 0; i < ARRAY_SIZE(abi_expected); ++i)
        if (out.abi_before[i] != abi_expected[i])
            return fail(index, "outer ABI sentinel", out.abi_before[i], abi_expected[i]);
    memcpy(expected_frame, out.frame_before, sizeof(expected_frame));
    frame_set(expected_frame, 60U, test->entry == REGION_ENTRY ? ALIAS(test->source) : context.r[2]);
    frame_set(expected_frame, 56U, context.r[3]);
    frame_set(expected_frame, 52U, context.r[4]);
    if (memcmp(out.frame_after, expected_frame, sizeof(expected_frame)))
        return fail(index, "complete helper frame and neighboring bytes", 1, 0);
    for (i = 0; i < 65536U; ++i) {
        unsigned destination = test->destination & 65535U;
        uint8_t expected = i >= destination && i < destination + test->length
            ? ram_before[(test->source & 65535U) + i - destination] : ram_before[i];
        if (((volatile uint8_t *)RAM_BASE)[i] != expected)
            return fail(index, "full RAM, immutable source and exact destination", i, expected);
    }
    for (i = 0; i < 8U; ++i)
        if (((volatile uint8_t *)0x213a0U)[i] != pools_before[i])
            return fail(index, "all bound data bytes", ((volatile uint8_t *)0x213a0U)[i], pools_before[i]);
    ++completed;
    return 1;
}
int main(void) {
    unsigned long i;
    if (ARRAY_SIZE(snapshot_early_indices) != 12U)
        return 1;
    if (!initial())
        return 1;
#if EARLY_ONLY
    for (i = 0; i < ARRAY_SIZE(snapshot_early_indices); ++i)
        if (!run_case(snapshot_early_indices[i], snapshot_cases + snapshot_early_indices[i]))
            return 1;
    if (completed != ARRAY_SIZE(snapshot_early_indices))
        return 1;
#else
    for (i = 0; i < ARRAY_SIZE(snapshot_cases); ++i)
        if (!run_case(i, snapshot_cases + i))
            return 1;
    if (completed != SNAPSHOT_CASE_COUNT)
        return 1;
#endif
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY, completed);
    return 0;
}
