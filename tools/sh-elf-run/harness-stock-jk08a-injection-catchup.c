/* Bounded catchup-mask selection with literal state, register and frame checks. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "injection-catchup-cases.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define CATCHUP_ACTIVE_CASE_COUNT (EARLY_ONLY ? 12U : CATCHUP_CASE_COUNT)

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
static uint8_t pools_before[22];
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
static int fail(unsigned long index, const char *field, uint32_t actual, uint32_t expected) {
    fprintf(stderr, "injection_catchup[%lu] %s actual=%08lx expected=%08lx\n",
            index, field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}
static const uint32_t pool_addresses[22] = {0x22695,0x22696,0x22697,0x22698,0x22699,0x2269a,0x54dbe,0x54dbf,0x54dc0,0x54dc1,0x54dc2,0x54dc3,0x54dc4,0x54dc5,0x54e8c,0x54e8d,0x54e8e,0x54e8f,0x54e90,0x54e91,0x54e92,0x54e93};
static int initial(void) {
    return REGION_ENTRY == 0x54c54U && CURSOR == 0xffff221eU && QUEUE == 0xffff20b5U
        && MASK_A == 0xffff157eU && MASK_B == 0xffff16feU && CLEAR == 0xffff1935U;
}
static void seed(unsigned long index, const struct catchup_case *test) {
    unsigned i;
    for (i = 0; i < 65536U; ++i)
        ((volatile uint8_t *)RAM_BASE)[i] = (uint8_t)(0x5dU + i * 19U + (i >> 8) + index);
    *ram(CURSOR) = test->cursor;
    *ram(QUEUE) = test->old[0];
    *ram(MASK_A) = test->old[1];
    *ram(MASK_B) = test->old[2];
    *ram(CLEAR) = test->old[3];
    for (i = 0; i < 65536U; ++i)
        ram_before[i] = ((volatile uint8_t *)RAM_BASE)[i];
    for (i = 0; i < ARRAY_SIZE(pool_addresses); ++i)
        pools_before[i] = *(volatile uint8_t *)(uintptr_t)pool_addresses[i];
}
static int run_case(unsigned long index, const struct catchup_case *test) {
    struct context context, before;
    struct observation out;
    uint8_t expected_frame[96];
    unsigned i;
    memcpy(context.r, test->incoming, sizeof(context.r));
    context.gbr = 0x01001ff4U;
    context.mach = test->variant ? 0xf1e2d3c4U : 0x13579bdfU;
    context.macl = test->variant ? 0x9274b6d8U : 0x2468ace0U;
    context.entry_t = test->entry_t;
    before = context;
    seed(index, test);
    memset(&out, 0xa6, sizeof(out));
    stock_invoke_injection_start_delay(REGION_ENTRY, &context, &out);
    if (memcmp(&context, &before, sizeof(context)))
        return fail(index, "immutable complete entry context", 1, 0);
    for (i = 0; i < 15U; ++i) {
        uint32_t expected = test->expected[i];
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
        return fail(index, "bounded loop boundary PR/SP", 1, 0);
    if (memcmp(out.abi_before, out.abi_after, sizeof(out.abi_before)))
        return fail(index, "independent C caller ABI", 1, 0);
    for (i = 0; i < ARRAY_SIZE(abi_expected); ++i)
        if (out.abi_before[i] != abi_expected[i])
            return fail(index, "outer ABI sentinel", out.abi_before[i], abi_expected[i]);
    memcpy(expected_frame, out.frame_before, sizeof(expected_frame));
    for (i = 0; i < 4U; ++i) {
        unsigned shift = 24U-i*8U;
        expected_frame[76U+i] = (uint8_t)((test->delta & 255U) >> shift);
        expected_frame[80U+i] = (uint8_t)(test->mask >> shift);
        if (test->delta & 255U)
            expected_frame[64U+i] = (uint8_t)(context.r[9] >> shift);
    }
    if (memcmp(out.frame_after, expected_frame, sizeof(expected_frame)))
        return fail(index, "complete helper frame and neighboring bytes", 1, 0);
    for (i = 0; i < 65536U; ++i) {
        uint8_t expected = i == (CURSOR & 65535U) ? test->next_cursor
            : i == (QUEUE & 65535U) ? test->state[0]
            : i == (MASK_A & 65535U) ? test->state[1]
            : i == (MASK_B & 65535U) ? test->state[2]
            : i == (CLEAR & 65535U) ? test->state[3] : ram_before[i];
        if (((volatile uint8_t *)RAM_BASE)[i] != expected)
            return fail(index, "full RAM, immutable source and exact destination", i, expected);
    }
    for (i = 0; i < ARRAY_SIZE(pool_addresses); ++i)
        if (*(volatile uint8_t *)(uintptr_t)pool_addresses[i] != pools_before[i])
            return fail(index, "all bound ROM bytes", pool_addresses[i], pools_before[i]);
    ++completed;
    return 1;
}
int main(void) {
    unsigned long i;
    if (ARRAY_SIZE(catchup_cases) != CATCHUP_CASE_COUNT || !initial()) return 1;
    for (i = 0; i < CATCHUP_ACTIVE_CASE_COUNT; ++i)
        if (!run_case(i, catchup_cases + i)) return 1;
    if (completed != CATCHUP_ACTIVE_CASE_COUNT) return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY, completed);
    return 0;
}
