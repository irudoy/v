#ifndef VQ_STOCK_AXIS_SEARCH_H
#define VQ_STOCK_AXIS_SEARCH_H

#include <stdint.h>
#include <stdio.h>

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(LAST_OFFSET) \
    || !defined(AXIS_BYTES) || !defined(DIVIDER_ENTRY)
#error "the verifier defines the axis-search entry, element contract, and divider"
#endif

struct axis_case {
    const char *name;
    uint32_t axis, coordinate, offset, fraction;
};

struct divider_case {
    const char *name;
    uint32_t numerator, divisor, quotient;
};

extern void stock_invoke_axis(uint32_t entry, uint32_t last_offset,
                              uint32_t coordinate, uint32_t axis, uint32_t *result);
extern uint32_t stock_invoke_r1(uint32_t entry, uint32_t numerator, uint32_t divisor);

static int fail_value(const char *name, const char *field, uint32_t actual, uint32_t expected)
{
    printf("VQ_SH_ELF_STOCK_CODE status=FAIL case=%s field=%s actual=%08lx expected=%08lx\n",
           name, field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}

static int run_axis_case(const struct axis_case *test)
{
    uint32_t result[] = {0x12345678, 0x55aa55aa, 0xaa55aa55, 0x87654321};
    volatile const uint8_t *axis = (volatile const uint8_t *)(uintptr_t)test->axis;
    uint8_t before[AXIS_BYTES];
    size_t index;
    for (index = 0; index < AXIS_BYTES; ++index)
        before[index] = axis[index];
    stock_invoke_axis(REGION_ENTRY, LAST_OFFSET, test->coordinate, test->axis, result + 1);
    if (result[1] != test->offset)
        return fail_value(test->name, "axis-offset", result[1], test->offset);
    if (result[2] != test->fraction)
        return fail_value(test->name, "fraction", result[2], test->fraction);
    if (result[0] != 0x12345678 || result[3] != 0x87654321)
        return fail_value(test->name, "output-neighbor", 1, 0);
    for (index = 0; index < AXIS_BYTES; ++index)
        if (axis[index] != before[index])
            return fail_value(test->name, "read-only-axis", (uint32_t)index, 0);
    return 1;
}

static int run_divider_case(const struct divider_case *test)
{
    uint32_t result = stock_invoke_r1(DIVIDER_ENTRY, test->numerator, test->divisor);
    return result == test->quotient ? 1 : fail_value(test->name, "quotient", result, test->quotient);
}

#endif
