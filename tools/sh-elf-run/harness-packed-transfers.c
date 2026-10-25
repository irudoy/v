/* Raw observations of bounded packed-field windows and their natural callees.
   Semantic and physical admission belong to the independent consumer. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define RAM_BASE 0x01000000U
#define RAM_SIZE 65536U
#define ARRAY_SIZE(value) (sizeof(value) / sizeof((value)[0]))

struct context { uint32_t r[15], gbr, mach, macl, entry_sr; };
struct observation {
    uint32_t exit[20], sp, continuation, abi_before[12], abi_after[12];
    uint8_t frame_before[192], frame_after[192];
    uint32_t sr_before;
};
struct packed_window { uint32_t entry, callee, source, destination; };
struct packed_source { unsigned window; uint32_t source, width; };
struct packed_case { unsigned window, local; uint32_t pattern, variant, sr; };

#include "packed-transfer-cases.h"

_Static_assert(sizeof(void *) == 4U, "SH-2E pointer ABI");
_Static_assert(sizeof(struct context) == 76U, "exact oneshot input ABI");
_Static_assert(sizeof(struct observation) == 572U, "exact complete observer ABI");
_Static_assert(offsetof(struct observation, frame_before) == 184U, "entry frame offset");
_Static_assert(offsetof(struct observation, frame_after) == 376U, "exit frame offset");
_Static_assert(offsetof(struct observation, sr_before) == 568U, "full prepared SR");

extern void stock_invoke_oneshot(uint32_t, const struct context *, struct observation *);
static uint8_t ram_before[RAM_SIZE];

static void hex(const void *address, size_t size)
{
    const uint8_t *bytes = address;
    size_t index;
    for (index = 0; index < size; ++index)
        printf("%02x", (unsigned)bytes[index]);
}

static int observe(size_t index)
{
    const struct packed_case *input = &packed_cases[index];
    const struct packed_window *window = &packed_windows[input->window];
    struct context context, initial;
    struct observation observation;
    volatile uint8_t *ram = (volatile uint8_t *)(uintptr_t)RAM_BASE;
    size_t offset, source;
    for (offset = 0; offset < RAM_SIZE; ++offset)
        ram[offset] = (uint8_t)(0x5dU + offset * 19U + (offset >> 8) + input->variant * 37U);
    for (source = 0; source < ARRAY_SIZE(packed_sources); ++source) {
        const struct packed_source *span = &packed_sources[source];
        unsigned lane;
        if (span->window != input->window)
            continue;
        for (lane = 0; lane < span->width; ++lane)
            ram[(span->source & 65535U) + lane] =
                (uint8_t)(input->pattern >> ((span->width - lane - 1U) * 8U));
    }
    for (offset = 0; offset < 15U; ++offset)
        context.r[offset] = 0x1728394aU + (uint32_t)offset * 0x110203U + input->variant * 0x1000101U;
    if (window->callee) {
        context.r[1] = window->destination;
        context.r[2] = window->source;
        context.r[7] = window->callee;
    }
    context.gbr = 0x01003579U;
    context.mach = 0x13579bdfU;
    context.macl = 0x2468ace0U;
    context.entry_sr = input->sr;
    initial = context;
    memcpy(ram_before, (const void *)(uintptr_t)RAM_BASE, sizeof(ram_before));
    memset(&observation, 0xa6, sizeof(observation));
    stock_invoke_oneshot(window->entry, &context, &observation);
    if (memcmp(&initial, &context, sizeof(context))) {
        fprintf(stderr, "packed-transfer[%lu]: const entry context changes\n", (unsigned long)index);
        return 0;
    }
    printf("kb-packed-field-observation {\"schema\":1,\"index\":%lu,\"window\":%u,\"case\":%u,\"context\":\"",
           (unsigned long)index, input->window, input->local);
    hex(&initial, sizeof(initial));
    printf("\",\"context_after\":\""); hex(&context, sizeof(context));
    printf("\",\"observation\":\""); hex(&observation, sizeof(observation));
    printf("\",\"ram_before\":\""); hex(ram_before, sizeof(ram_before));
    printf("\",\"ram_after\":\""); hex((const void *)(uintptr_t)RAM_BASE, RAM_SIZE);
    printf("\"}\n");
    return 1;
}

int main(void)
{
    size_t index, completed = 0;
    for (index = 0; index < ARRAY_SIZE(packed_cases); ++index) {
        if (!observe(index))
            return 1;
        ++completed;
    }
    printf("VQ_SH_ELF_PACKED_TRANSFERS status=PASS region=%s cases=%lu windows=%lu\n",
           PACKED_REGION, (unsigned long)completed, (unsigned long)ARRAY_SIZE(packed_windows));
    return 0;
}
