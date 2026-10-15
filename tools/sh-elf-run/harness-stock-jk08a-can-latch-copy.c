/* Exact bounded caller/helper effects and an observation boundary above SP. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "can-latch-copy-cases.h"

#define RAM_BASE 0x01000000U
#define ALIAS(a) (RAM_BASE + ((a) & 65535U))
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
struct context { uint32_t r[15], gbr, mach, macl, sr, caller; };
struct observation {
    uint32_t r[15], sr_before, sr_after, pr, gbr, mach, macl;
    uint32_t sp_before, sp_after, return_pc;
    uint8_t frame_before[64], frame_after[64];
    uint32_t abi_before[12], abi_after[12];
};
_Static_assert(sizeof(struct context) == 80U, "entry context");
_Static_assert(sizeof(struct observation) == 320U, "complete observation");
_Static_assert(offsetof(struct observation, frame_before) == 96U, "before frame");
_Static_assert(offsetof(struct observation, frame_after) == 160U, "after frame");
_Static_assert(offsetof(struct observation, abi_before) == 224U, "before ABI");
_Static_assert(offsetof(struct observation, abi_after) == 272U, "after ABI");
extern void can_copy_invoke(const struct context *, struct observation *);
static uint8_t ram_before[65536];
static uint8_t source_before[16];
static unsigned completed;

static volatile uint8_t *ram(uint32_t address) {
    return (volatile uint8_t *)(uintptr_t)ALIAS(address);
}
static void frame_word(uint8_t *frame, unsigned offset, uint32_t value) {
    frame[offset] = (uint8_t)(value >> 24);
    frame[offset + 1U] = (uint8_t)(value >> 16);
    frame[offset + 2U] = (uint8_t)(value >> 8);
    frame[offset + 3U] = (uint8_t)value;
}
static int fail(unsigned index, const char *field) {
    fprintf(stderr, "can_latch_copy[%u] %s\n", index, field);
    return 0;
}
static void hex(const uint8_t *data, unsigned length) {
    unsigned i;
    putchar('"');
    for (i = 0; i < length; ++i)
        printf("%02x", (unsigned)data[i]);
    putchar('"');
}
static void emit(const struct can_copy_case *test, const struct observation *out) {
    uint8_t source_after[16], destination_after[16];
    unsigned i;
    for (i = 0; i < test->length; ++i) {
        source_after[i] = ram(test->source)[i];
        destination_after[i] = ram(test->destination)[i];
    }
    printf("CAN_COPY_CASE {\"index\":%u,\"gpr\":[", test->index);
    for (i = 0; i < 15U; ++i)
        printf("%s%lu", i ? "," : "", (unsigned long)out->r[i]);
    printf("],\"sr_before\":%lu,\"sr_after\":%lu,\"pr\":%lu,"
           "\"gbr\":%lu,\"mach\":%lu,\"macl\":%lu,\"sp_before\":%lu,"
           "\"sp_after\":%lu,\"return_pc\":%lu,\"source_before\":",
           (unsigned long)out->sr_before, (unsigned long)out->sr_after,
           (unsigned long)out->pr, (unsigned long)out->gbr,
           (unsigned long)out->mach, (unsigned long)out->macl,
           (unsigned long)out->sp_before, (unsigned long)out->sp_after,
           (unsigned long)out->return_pc);
    hex(source_before, test->length);
    printf(",\"source_after\":"); hex(source_after, test->length);
    printf(",\"destination_after\":"); hex(destination_after, test->length);
    printf(",\"frame_before\":"); hex(out->frame_before, 64U);
    printf(",\"frame_after\":"); hex(out->frame_after, 64U);
    printf(",\"ram_checked_bytes\":65536,\"unchanged_outside_destination\":true,"
           "\"abi_preserved\":true,\"input_preserved\":true}\n");
}
static int run_case(const struct can_copy_case *test) {
    struct context context, before;
    struct { uint32_t first; struct observation out; uint32_t last; } guarded;
    struct observation *out = &guarded.out;
    uint8_t frame[64];
    unsigned i;
    if (test->length > sizeof(source_before) || test->source == test->destination)
        return fail(test->index, "invalid non-overlap matrix input");
    if (*(volatile uint32_t *)0x2125cU != 0x01004194U)
        return fail(test->index, "actual source-pointer alias");
    if (!test->carry)
        for (i = 0; i < 65536U; ++i)
            ((volatile uint8_t *)RAM_BASE)[i] = (uint8_t)(0x5dU + i * 19U + (i >> 8) + test->index);
    for (i = 0; i < test->length; ++i)
        ram(test->source)[i] = test->bytes[i];
    for (i = 0; i < 65536U; ++i)
        ram_before[i] = ((volatile uint8_t *)RAM_BASE)[i];
    for (i = 0; i < test->length; ++i)
        source_before[i] = ram(test->source)[i];
    memcpy(context.r, test->incoming, sizeof(context.r));
    context.gbr = test->gbr; context.mach = test->mach; context.macl = test->macl;
    context.sr = test->sr; context.caller = test->caller;
    before = context;
    memset(&guarded, 0xa6, sizeof(guarded));
    can_copy_invoke(&context, out);
    if (guarded.first != 0xa6a6a6a6U || guarded.last != 0xa6a6a6a6U)
        return fail(test->index, "observation output guards");
    if (memcmp(&context, &before, sizeof(context)))
        return fail(test->index, "immutable full entry context");
    for (i = 0; i < 15U; ++i)
        if (out->r[i] != test->expected[i]) {
            fprintf(stderr, "r%u actual=%08lx expected=%08lx\n", i,
                    (unsigned long)out->r[i], (unsigned long)test->expected[i]);
            return fail(test->index, "all live GPRs before boundary scratch");
        }
    if ((out->sr_before & 0x301U) != test->sr
        || out->sr_after != ((out->sr_before & ~1U) | (test->length == 0U)))
        return fail(test->index, "prepared and complete SR/M/Q/T effects");
    if (out->gbr != context.gbr || out->mach != context.mach || out->macl != context.macl)
        return fail(test->index, "GBR/MACH/MACL preservation");
    if (out->sp_before != out->sp_after || (out->sp_before & 3U)
        || out->pr != (test->caller ? 0x2109aU : out->return_pc))
        return fail(test->index, "natural return, PR and unchanged SP");
    if (memcmp(out->abi_before + 1, out->abi_after + 1, 11U * sizeof(uint32_t)))
        return fail(test->index, "outer C caller ABI");
    for (i = 0; i < 16U; ++i)
        frame_word(frame, i * 4U, 0xa3b4c5d6U + i * 17U);
    if (memcmp(out->frame_before, frame, sizeof(frame)))
        return fail(test->index, "complete seeded lower frame");
    frame_word(frame, 52U, context.r[4]);
    frame_word(frame, 56U, context.r[3]);
    frame_word(frame, 60U, ALIAS(test->source));
    if (memcmp(out->frame_after, frame, sizeof(frame)))
        return fail(test->index, "exact helper stack writes and untouched neighbors");
    for (i = 0; i < 65536U; ++i) {
        unsigned destination = test->destination & 65535U;
        uint8_t expected = i >= destination && i < destination + test->length
            ? ram_before[(test->source & 65535U) + i - destination] : ram_before[i];
        if (((volatile uint8_t *)RAM_BASE)[i] != expected)
            return fail(test->index, "all RAM, exact copy and immutable source/neighbors");
    }
    emit(test, out);
    ++completed;
    return 1;
}
int main(void) {
    unsigned i;
    if (ARRAY_SIZE(can_copy_early_indices) >= ARRAY_SIZE(can_copy_cases)) return 1;
#if EARLY_ONLY
    for (i = 0; i < ARRAY_SIZE(can_copy_early_indices); ++i)
        if (!run_case(can_copy_cases + can_copy_early_indices[i])) return 1;
    if (completed != ARRAY_SIZE(can_copy_early_indices)) return 1;
    printf("VQ_SH_ELF_CAN_COPY_SUBSET status=PASS region=%s cases=%u production=false\n", REGION_KEY, completed);
#else
    for (i = 0; i < ARRAY_SIZE(can_copy_cases); ++i)
        if (!run_case(can_copy_cases + i)) return 1;
    if (completed != ARRAY_SIZE(can_copy_cases)) return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%u\n", REGION_KEY, completed);
#endif
    return 0;
}
