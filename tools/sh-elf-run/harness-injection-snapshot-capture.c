/* Capture actual states around the unchanged checked snapshot invocation. */
#include <stdint.h>

struct context;
struct observation;
extern void stock_invoke_injection_start_delay(
    uint32_t, const struct context *, struct observation *);
static void capture_invoke(uint32_t, const struct context *, struct observation *);

/* The checked harness and its fixture bytes remain separate inputs. */
#define stock_invoke_injection_start_delay capture_invoke
#define main injection_snapshot_checked_main
#include "harness-stock-jk08a-injection-snapshot.c"
#undef main
#undef stock_invoke_injection_start_delay

static void words(const uint32_t *values, unsigned count) {
    unsigned i;
    putchar('[');
    for (i = 0; i < count; ++i)
        printf("%s%lu", i ? "," : "", (unsigned long)values[i]);
    putchar(']');
}

static void bytes(const uint8_t *values, unsigned count) {
    unsigned i;
    putchar('"');
    for (i = 0; i < count; ++i)
        printf("%02x", (unsigned)values[i]);
    putchar('"');
}

static void span(uint32_t address, unsigned count, int before) {
    unsigned i;
    putchar('"');
    for (i = 0; i < count; ++i) {
        uint8_t value = before ? ram_before[(address & 65535U) + i] : ram(address)[i];
        printf("%02x", (unsigned)value);
    }
    putchar('"');
}

static void capture_invoke(uint32_t entry, const struct context *context,
                           struct observation *out) {
    unsigned i, changed = 0U;
    unsigned long index;
    const struct snapshot_case *test;
    struct context incoming = *context;
#if EARLY_ONLY
    index = snapshot_early_indices[completed];
#else
    index = completed;
#endif
    test = snapshot_cases + index;
    stock_invoke_injection_start_delay(entry, context, out);
    printf("kb-injection-snapshot-observation {\"index\":%lu,\"entry\":%lu,"
           "\"source\":%lu,\"destination\":%lu,\"length\":%u,\"incoming\":",
           index, (unsigned long)entry, (unsigned long)test->source,
           (unsigned long)test->destination, (unsigned)test->length);
    words(incoming.r, 15U);
    printf(",\"incoming_after\":");
    words(context->r, 15U);
    printf(",\"gbr_after\":%lu,\"mach_after\":%lu,\"macl_after\":%lu,\"entry_t_after\":%lu",
           (unsigned long)context->gbr, (unsigned long)context->mach,
           (unsigned long)context->macl, (unsigned long)context->entry_t);
    printf(",\"gbr\":%lu,\"mach\":%lu,\"macl\":%lu,\"entry_t\":%lu,\"exit\":",
           (unsigned long)incoming.gbr, (unsigned long)incoming.mach,
           (unsigned long)incoming.macl, (unsigned long)incoming.entry_t);
    words(out->exit, 20U);
    printf(",\"sp\":%lu,\"continuation\":%lu,\"sr_before\":%lu,\"abi_before\":",
           (unsigned long)out->sp, (unsigned long)out->continuation,
           (unsigned long)out->sr_before);
    words(out->abi_before, 12U);
    printf(",\"abi_after\":");
    words(out->abi_after, 12U);
    printf(",\"frame_before\":");
    bytes(out->frame_before, 96U);
    printf(",\"frame_after\":");
    bytes(out->frame_after, 96U);
    printf(",\"source_before\":");
    span(test->source, test->length, 1);
    printf(",\"source_after\":");
    span(test->source, test->length, 0);
    printf(",\"destination_before\":");
    span(test->destination, test->length, 1);
    printf(",\"destination_after\":");
    span(test->destination, test->length, 0);
    printf(",\"pools_before\":");
    bytes(pools_before, 8U);
    printf(",\"pools_after\":\"");
    for (i = 0; i < 8U; ++i)
        printf("%02x", (unsigned)((volatile uint8_t *)0x213a0U)[i]);
    printf("\",\"outside_changes\":[");
    for (i = 0; i < 65536U; ++i) {
        unsigned destination = test->destination & 65535U;
        uint8_t actual = ((volatile uint8_t *)RAM_BASE)[i];
        if ((i < destination || i >= destination + test->length) && actual != ram_before[i]) {
            printf("%s[%u,%u,%u]", changed ? "," : "", i,
                   (unsigned)ram_before[i], (unsigned)actual);
            ++changed;
        }
    }
    printf("]}\n");
}

int main(void) {
    int result = injection_snapshot_checked_main();
    if (result)
        return result;
    printf("VQ_SH_ELF_INJECTION_SNAPSHOT_CAPTURE cases=%lu early=%s\n", completed,
           EARLY_ONLY ? "true" : "false");
    return 0;
}
