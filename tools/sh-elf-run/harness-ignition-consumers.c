/* Bounded real lookup-call windows through the injected adapters.
   The stock interpolation body is a declared simulator-only observation stub. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define RAM_BASE 0x01000000U
#define RAM_SIZE 65536U
#define CALL_VIEW 0x01010000U
#define CALL_WORDS 24U
#define LOOKUP_RESULT 0xa1b2c3d4U
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))

struct context { uint32_t r[15], gbr, mach, macl, entry_sr, fifth_argument; };
struct observation {
    uint32_t exit[20], sp, continuation, abi_before[12], abi_after[12];
    uint8_t frame_before[192], frame_after[192];
    uint32_t sr_before;
};
struct c5_window {
    uint32_t entry, load, call, literal, table, axis6, axis5, stock, adapter;
    unsigned target_register, family, overwrites_fifth;
};
struct c5_family { uint32_t canonical, pointers, slots[5]; };
struct input { uint32_t r0, r7, fifth, sr; };

#include "ignition-consumer-cases.h"

_Static_assert(sizeof(void *) == 4U, "SH-2E pointer ABI");
_Static_assert(sizeof(uint32_t) == 4U, "32-bit observation words");
_Static_assert(sizeof(struct context) == 80U, "independent fifth argument");
_Static_assert(offsetof(struct context, fifth_argument) == 76U, "stack argument offset");
_Static_assert(sizeof(struct observation) == 572U, "complete observer ABI");
_Static_assert(offsetof(struct observation, frame_before) == 184U, "entry frame offset");
_Static_assert(offsetof(struct observation, frame_after) == 376U, "exit frame offset");
_Static_assert(offsetof(struct observation, sr_before) == 568U, "complete entry SR");

extern void stock_invoke_ignition_consumer(uint32_t, const struct context *, struct observation *);
static uint8_t ram_before[RAM_SIZE];
static const uint8_t selectors[] = {0, 1, 2, 3, 4, 5, 255};
static const struct input inputs[] = {
    {0x00000000U, 0x00000000U, 0x000000ffU, 0x000U},
    {0x000000ffU, 0x0000ffffU, 0x00000000U, 0x001U},
    {0x12345680U, 0xffff8000U, 0x0000007fU, 0x0f0U},
    {0xffffff7fU, 0xffff0001U, 0x00000080U, 0x0f1U},
    {0x89abcdefU, 0x80000000U, 0x12345678U, 0x300U},
    {0xffffffffU, 0xffffffffU, 0xffffffffU, 0x3f1U},
};
static const uint32_t abi[] = {
    0x18283848U, 0x19293949U, 0x1a2a3a4aU, 0x1b2b3b4bU,
    0x1c2c3c4cU, 0x1d2d3d4dU, 0x1e2e3e4eU,
    0x12344321U, 0x10203040U, 0x50607080U,
};

static volatile uint8_t *ram(uint32_t original)
{
    return (volatile uint8_t *)(uintptr_t)(RAM_BASE + (original & 65535U));
}

static int fail(size_t index, const char *field, uint32_t actual, uint32_t expected)
{
    fprintf(stderr, "ignition_consumer[%lu] %s actual=%08lx expected=%08lx\n",
            (unsigned long)index, field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}

static void hex(const void *data, size_t size)
{
    const uint8_t *bytes = data;
    size_t index;
    for (index = 0; index < size; ++index)
        printf("%02x", (unsigned)bytes[index]);
}

static void put32(uint8_t *target, uint32_t value)
{
    target[0] = (uint8_t)(value >> 24);
    target[1] = (uint8_t)(value >> 16);
    target[2] = (uint8_t)(value >> 8);
    target[3] = (uint8_t)value;
}

static int run_case(size_t index, size_t window_index, size_t selector_index, size_t variant)
{
    const struct c5_window *window = &c5_windows[window_index];
    const struct c5_family *family = &c5_families[window->family];
    const struct input *input = &inputs[variant];
    struct context context, before;
    struct observation out;
    uint32_t call[CALL_WORDS], expected[15], fifth, sr;
    uint8_t frame[192];
    size_t i;
    unsigned selector = selectors[selector_index], slot = selector < 5U ? selector : 0U;

    if (window->table != family->canonical
            || *(volatile uint32_t *)(uintptr_t)window->literal != window->adapter)
        return fail(index, "actual hooked literal and family", 1, 0);
    for (i = 0; i < RAM_SIZE; ++i)
        ((volatile uint8_t *)(uintptr_t)RAM_BASE)[i] = (uint8_t)(0x5dU + i * 19U + (i >> 8));
    *ram(C5_SELECTOR_ADDRESS) = (uint8_t)selector;
    ram(0xfffe819eU)[0] = (uint8_t)(input->r7 >> 8);
    ram(0xfffe819eU)[1] = (uint8_t)input->r7;
    memset((void *)(uintptr_t)(CALL_VIEW - 16U), 0xa6, 16U + CALL_WORDS * 4U + 16U);
    ((volatile uint32_t *)(uintptr_t)CALL_VIEW)[22] = 0;
    memcpy(ram_before, (const void *)(uintptr_t)RAM_BASE, sizeof(ram_before));
    for (i = 0; i < 15U; ++i)
        context.r[i] = 0x1728394aU + (uint32_t)i * 0x110203U + (uint32_t)variant * 0x1000101U;
    context.r[0] = input->r0;
    context.r[7] = input->r7;
    context.r[12] = 0x0100817cU;
    context.gbr = 0x01003579U;
    context.mach = 0x13579bdfU;
    context.macl = 0x2468ace0U;
    context.entry_sr = input->sr;
    context.fifth_argument = input->fifth;
    before = context;
    memset(&out, 0xa6, sizeof(out));
    stock_invoke_ignition_consumer(window->entry, &context, &out);
    memcpy(call, (const void *)(uintptr_t)CALL_VIEW, sizeof(call));
    if (memcmp(&before, &context, sizeof(context)))
        return fail(index, "immutable entry context", 1, 0);
    if ((out.sr_before & 0x3f1U) != context.entry_sr)
        return fail(index, "actual prepared SR", out.sr_before & 0x3f1U, context.entry_sr);
    if (call[22] != 1U || call[23] != window->stock || call[20] != out.sp
            || call[1] != window->call + 4U)
        return fail(index, "exact callee, call count, SP and return path", 1, 0);
    memcpy(expected, context.r, sizeof(expected));
    if (window->overwrites_fifth)
        expected[13] = context.r[0] & 255U;
    expected[window->target_register] = window->adapter;
    expected[0] = slot * 4U;
    expected[1] = 5U;
    expected[2] = family->pointers;
    expected[3] = window->stock;
    expected[4] = family->slots[slot];
    expected[5] = window->axis5;
    expected[6] = window->axis6;
    expected[7] = input->r7 & 65535U;
    for (i = 0; i < 15U; ++i)
        if (call[19U - i] != expected[i])
            return fail(index, "complete real callee GPR", call[19U - i], expected[i]);
    sr = (out.sr_before & ~1U) | (uint32_t)(selector >= 5U);
    fifth = window->overwrites_fifth ? context.r[0] & 255U : context.fifth_argument;
    if (call[0] != sr || call[2] != context.macl || call[3] != context.mach
            || call[4] != context.gbr || call[21] != fifth)
        return fail(index, "complete callee SR/special registers/stack argument", 1, 0);
    expected[0] = LOOKUP_RESULT;
    expected[7] = out.continuation; /* Declared post-window PR restoration scratch. */
    for (i = 0; i < 15U; ++i)
        if (out.exit[19U - i] != expected[i])
            return fail(index, "complete window return GPR", out.exit[19U - i], expected[i]);
    if (out.exit[0] != sr || out.exit[1] != out.continuation
            || out.exit[2] != context.macl || out.exit[3] != context.mach
            || out.exit[4] != context.gbr || out.sp != out.abi_before[10] - 164U)
        return fail(index, "complete window return SR/special registers/ABI SP", 1, 0);
    if (memcmp(out.abi_before, out.abi_after, sizeof(out.abi_before)))
        return fail(index, "independent outer caller ABI", 1, 0);
    for (i = 0; i < ARRAY_SIZE(abi); ++i)
        if (out.abi_before[i] != abi[i])
            return fail(index, "outer ABI sentinel", out.abi_before[i], abi[i]);
    memcpy(frame, out.frame_before, sizeof(frame));
    memcpy(frame + 80U, call, 80U);
    put32(frame + 160U, fifth);
    if (memcmp(frame, out.frame_after, sizeof(frame))
            || memcmp(ram_before, (const void *)(uintptr_t)RAM_BASE, sizeof(ram_before)))
        return fail(index, "complete frame and target RAM", 1, 0);
    for (i = 0; i < 16U; ++i)
        if (((volatile uint8_t *)(uintptr_t)(CALL_VIEW - 16U))[i] != 0xa6U
                || ((volatile uint8_t *)(uintptr_t)(CALL_VIEW + sizeof(call)))[i] != 0xa6U)
            return fail(index, "callee observation guards", 1, 0);
    printf("kb-ignition-literal-observation {\"schema\":1,\"index\":%lu,\"window\":%lu,\"selector\":%u,\"variant\":%lu,\"context\":\"",
           (unsigned long)index, (unsigned long)window_index, selector, (unsigned long)variant);
    hex(&context, sizeof(context));
    printf("\",\"observation\":\""); hex(&out, sizeof(out));
    printf("\",\"callee\":\""); hex(call, sizeof(call));
    printf("\",\"ram_before\":\""); hex(ram_before, sizeof(ram_before));
    printf("\",\"ram_after\":\""); hex((const void *)(uintptr_t)RAM_BASE, RAM_SIZE);
    printf("\",\"guards\":\"");
    hex((const void *)(uintptr_t)(CALL_VIEW - 16U), 16U);
    hex((const void *)(uintptr_t)(CALL_VIEW + sizeof(call)), 16U);
    printf("\"}\n");
    return 1;
}

int main(void)
{
    size_t window, selector, variant, completed = 0;
    for (window = 0; window < ARRAY_SIZE(c5_windows); ++window)
        for (selector = 0; selector < ARRAY_SIZE(selectors); ++selector)
            for (variant = 0; variant < ARRAY_SIZE(inputs); ++variant) {
                if (!run_case(completed, window, selector, variant))
                    return 1;
                ++completed;
            }
    printf("VQ_SH_ELF_IGNITION_LITERAL_CONSUMERS status=PASS cases=%lu windows=%lu\n",
           (unsigned long)completed, (unsigned long)ARRAY_SIZE(c5_windows));
    return 0;
}
