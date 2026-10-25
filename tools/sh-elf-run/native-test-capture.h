#ifndef VQ_NATIVE_TEST_CAPTURE_H
#define VQ_NATIVE_TEST_CAPTURE_H

#include <stdint.h>

_Static_assert(sizeof(uint32_t) == 4U && sizeof(void *) == 4U,
               "native TEST capture requires the 32-bit target ABI");
#if !defined(__BYTE_ORDER__) || __BYTE_ORDER__ != __ORDER_BIG_ENDIAN__
#error native TEST capture requires the big-endian target ABI
#endif

struct vq_native_capture_field {
    const char *side;
    const char *name;
    uint32_t offset;
    uint32_t size;
};

struct vq_native_capture_span {
    const char *name;
    uint32_t original;
    uint32_t alias;
    uint32_t size;
};

struct vq_native_capture_spec {
    const char *region;
    uint32_t context_size;
    uint32_t observation_size;
    uint32_t field_count;
    const struct vq_native_capture_field *fields;
    uint32_t span_count;
    const struct vq_native_capture_span *spans;
    uint32_t selected_count;
    const uint32_t *selected;
};

extern const struct vq_native_capture_spec vq_native_capture_spec;

#endif
