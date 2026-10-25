/* Raw bounded width-view observations; independent consumers own admission. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define RAM_BASE 0x01000000U
#define RAM_SIZE 65536U
#define ARRAY_SIZE(value) (sizeof(value) / sizeof((value)[0]))
struct context { uint32_t r[15], gbr, mach, macl, entry_sr, stack8; };
struct observation {
    uint32_t exit[20], sp, continuation, abi_before[12], abi_after[12];
    uint8_t frame_before[192], frame_after[192];
    uint32_t sr_before;
};
struct width_case {
    unsigned window, local;
    uint32_t entry, pattern, selector, variant, sr, gbr;
    unsigned stage_r13, stage_r14, terminal;
};
#include "width-view-cases.h"
_Static_assert(sizeof(void *) == 4U, "SH-2E pointer ABI");
_Static_assert(sizeof(struct context) == 80U, "width-view input ABI");
_Static_assert(offsetof(struct context, stack8) == 76U, "independent stack input");
_Static_assert(sizeof(struct observation) == 572U, "complete raw observer ABI");
_Static_assert(offsetof(struct observation, frame_before) == 184U, "entry frame offset");
_Static_assert(offsetof(struct observation, frame_after) == 376U, "exit frame offset");
_Static_assert(offsetof(struct observation, sr_before) == 568U, "full prepared SR");
extern void stock_invoke_width_view(uint32_t, const struct context *, struct observation *);
static uint8_t ram_before[RAM_SIZE];

static void hex(const void *address, size_t size)
{
    const uint8_t *bytes = address;
    size_t index;
    for (index = 0; index < size; ++index)
        printf("%02x", (unsigned)bytes[index]);
}

static void rle(const uint8_t *bytes, size_t size)
{
    size_t start = 0;
    while (start < size) {
        size_t end = start + 1U;
        while (end < size && bytes[end] == bytes[start])
            ++end;
        printf("%s%lu:%02x", start ? "," : "", (unsigned long)(end - start), (unsigned)bytes[start]);
        start = end;
    }
}

static void word(volatile uint8_t *ram, uint32_t address, uint32_t value)
{
    ram[address] = (uint8_t)(value >> 8);
    ram[address + 1U] = (uint8_t)value;
}

static int observe(size_t index)
{
    const struct width_case *input = &width_cases[index];
    struct context context, initial;
    struct observation observation;
    volatile uint8_t *ram = (volatile uint8_t *)(uintptr_t)RAM_BASE;
    size_t offset;
    uint32_t metric = 0x21d4U + 4U * input->selector;
    uint32_t value = (input->pattern << 16) | (input->pattern ^ 65535U);
    memset((void *)(uintptr_t)RAM_BASE, (int)((0x5dU + input->variant * 37U) & 255U), RAM_SIZE);
    word(ram, 0x118aU, input->pattern);
    word(ram, 0x16d2U, input->pattern);
    word(ram, 0x4544U, input->pattern);
    word(ram, 0x5606U, input->pattern);
    word(ram, 0x2142U + input->selector * 2U, input->pattern);
    ram[metric] = (uint8_t)(value >> 24);
    ram[metric + 1U] = (uint8_t)(value >> 16);
    ram[metric + 2U] = (uint8_t)(value >> 8);
    ram[metric + 3U] = (uint8_t)value;
    ram[0x11deU] = ram[0x2142U] = ram[0x2143U] = (uint8_t)input->selector;
    for (offset = 0; offset < 15U; ++offset)
        context.r[offset] = 0x1728394aU + (uint32_t)offset * 0x110203U + input->variant * 0x1000101U;
    if (input->stage_r13)
        context.r[13] = RAM_BASE + 0x55bcU;
    if (input->stage_r14) {
        context.r[14] = input->selector;
        context.r[0] = 0xb6c70000U | input->pattern;
    }
    if (input->terminal == 1U)
        context.r[0] = input->variant & 1U ? 2U : 0U;
    if (input->terminal == 2U)
        context.r[0] = input->variant & 1U ? 0x40U : 0U;
    context.gbr = input->gbr;
    context.mach = 0x13579bdfU;
    context.macl = 0x2468ace0U;
    context.entry_sr = input->sr;
    context.stack8 = value;
    initial = context;
    memcpy(ram_before, (const void *)(uintptr_t)RAM_BASE, sizeof(ram_before));
    memset(&observation, 0xa6, sizeof(observation));
    stock_invoke_width_view(input->entry, &context, &observation);
    if (memcmp(&initial, &context, sizeof(context))) {
        fprintf(stderr, "width-view[%lu]: const context changes\n", (unsigned long)index);
        return 0;
    }
    printf("kb-width-view-observation {\"schema\":1,\"index\":%lu,\"window\":%u,\"case\":%u,\"context\":\"",
           (unsigned long)index, input->window, input->local);
    hex(&initial, sizeof(initial));
    printf("\",\"context_after\":\""); hex(&context, sizeof(context));
    printf("\",\"observation\":\""); hex(&observation, sizeof(observation));
    printf("\",\"ram_before\":\""); rle(ram_before, RAM_SIZE);
    printf("\",\"ram_after\":\""); rle((const uint8_t *)(uintptr_t)RAM_BASE, RAM_SIZE);
    printf("\"}\n");
    return 1;
}

int main(void)
{
    size_t index;
    for (index = 0; index < ARRAY_SIZE(width_cases); ++index)
        if (!observe(index))
            return 1;
    printf("VQ_SH_ELF_WIDTH_VIEWS status=PASS region=%s cases=%lu windows=%u\n",
           WIDTH_VIEW_REGION, (unsigned long)ARRAY_SIZE(width_cases), WIDTH_VIEW_WINDOWS);
    return 0;
}
