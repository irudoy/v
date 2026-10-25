/* Raw driver observations around the existing entry/context/observation ABI. */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "native-test-capture.h"

#ifndef VQ_NATIVE_CAPTURE_REAL_SYMBOL
#error VQ_NATIVE_CAPTURE_REAL_SYMBOL is required
#endif
#ifndef VQ_NATIVE_CAPTURE_WRAP_SYMBOL
#error VQ_NATIVE_CAPTURE_WRAP_SYMBOL is required
#endif

extern void vq_native_capture_real(uint32_t, const void *, void *)
    __asm__(VQ_NATIVE_CAPTURE_REAL_SYMBOL);
void vq_native_capture_wrap(uint32_t, const void *, void *)
    __asm__(VQ_NATIVE_CAPTURE_WRAP_SYMBOL);

static uint32_t invocation_count;
static uint32_t captured_count;
static int initialized;

static void bytes(const volatile void *source, uint32_t size)
{
    static const char digits[] = "0123456789abcdef";
    const volatile uint8_t *data = source;
    uint32_t index;
    putchar('"');
    for (index = 0; index < size; ++index) {
        uint8_t value = data[index];
        putchar(digits[value >> 4]);
        putchar(digits[value & 15U]);
    }
    putchar('"');
}

static void memory(void)
{
    uint32_t index;
    putchar('[');
    for (index = 0; index < vq_native_capture_spec.span_count; ++index) {
        const struct vq_native_capture_span *span = &vq_native_capture_spec.spans[index];
        if (index != 0U)
            putchar(',');
        bytes((const volatile void *)(uintptr_t)span->alias, span->size);
    }
    putchar(']');
}

static void terminal(void)
{
    printf("vq-native-test-terminal {\"schema\":1,\"region\":\"%s\","
           "\"invocations\":%" PRIu32 ",\"captured\":%" PRIu32 "}\n",
           vq_native_capture_spec.region, invocation_count, captured_count);
}

static void initialize(void)
{
    uint32_t index;
    if (atexit(terminal) != 0) {
        fputs("native TEST capture cannot register its terminal\n", stderr);
        exit(2);
    }
    printf("vq-native-test-abi {\"schema\":1,\"region\":\"%s\","
           "\"context_size\":%" PRIu32 ",\"observation_size\":%" PRIu32 ","
           "\"fields\":[", vq_native_capture_spec.region,
           vq_native_capture_spec.context_size, vq_native_capture_spec.observation_size);
    for (index = 0; index < vq_native_capture_spec.field_count; ++index) {
        const struct vq_native_capture_field *field = &vq_native_capture_spec.fields[index];
        if (index != 0U)
            putchar(',');
        printf("{\"side\":\"%s\",\"name\":\"%s\",\"offset\":%" PRIu32
               ",\"size\":%" PRIu32 "}", field->side, field->name, field->offset, field->size);
    }
    fputs("],\"spans\":[", stdout);
    for (index = 0; index < vq_native_capture_spec.span_count; ++index) {
        const struct vq_native_capture_span *span = &vq_native_capture_spec.spans[index];
        if (index != 0U)
            putchar(',');
        printf("{\"name\":\"%s\",\"original\":%" PRIu32 ",\"alias\":%" PRIu32
               ",\"size\":%" PRIu32 "}", span->name, span->original, span->alias, span->size);
    }
    fputs("]}\n", stdout);
    initialized = 1;
}

void vq_native_capture_wrap(uint32_t entry, const void *context, void *observation)
{
    uint32_t index;
    int selected;
    if (!initialized)
        initialize();
    if (invocation_count == UINT32_MAX) {
        fputs("native TEST capture invocation count overflow\n", stderr);
        exit(2);
    }
    index = invocation_count++;
    selected = captured_count < vq_native_capture_spec.selected_count &&
        vq_native_capture_spec.selected[captured_count] == index;
    if (selected) {
        printf("vq-native-test-before {\"schema\":1,\"region\":\"%s\","
               "\"index\":%" PRIu32 ",\"entry\":%" PRIu32 ",\"driver_context\":",
               vq_native_capture_spec.region, index, entry);
        bytes(context, vq_native_capture_spec.context_size);
        fputs(",\"driver_memory\":", stdout);
        memory();
        fputs("}\n", stdout);
    }
    vq_native_capture_real(entry, context, observation);
    if (selected) {
        printf("vq-native-test-after {\"schema\":1,\"region\":\"%s\","
               "\"index\":%" PRIu32 ",\"entry\":%" PRIu32 ",\"observation\":",
               vq_native_capture_spec.region, index, entry);
        bytes(observation, vq_native_capture_spec.observation_size);
        fputs(",\"driver_context_after\":", stdout);
        bytes(context, vq_native_capture_spec.context_size);
        fputs(",\"driver_memory\":", stdout);
        memory();
        fputs("}\n", stdout);
        ++captured_count;
    }
}
