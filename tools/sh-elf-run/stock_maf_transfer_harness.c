#include <stdint.h>
#include <stdio.h>

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(CURVE_ENTRY) \
    || !defined(BODY_ENTRY) || !defined(MAF_TABLE_B1) || !defined(MAF_TABLE_B2) \
    || !defined(MAF_INPUT_B1) || !defined(MAF_INPUT_B2) \
    || !defined(MAF_OUTPUT_B1) || !defined(MAF_OUTPUT_B2) \
    || !defined(INPUT_BASE) || !defined(CORRECTION_OUTPUT)
#error "the verifier defines the MAF slice, curves, inputs, and output symbols"
#endif

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define ROM_TABLE(address) ((const void *)(uintptr_t)(address))
#define TEST_RAM_BASE 0x01000000U
#define MACL_SEED 0x2468acdfU
#define GBR_SEED 0x76543210U

extern uint32_t stock_invoke_word_curve(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t *);
extern uint32_t stock_invoke_format_curve(uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t stock_invoke_maf_transfer(uint32_t, uint32_t, uint32_t, uint32_t *);

static const uint16_t ascending_words[64] = {0, 65535, [63] = 0xfedc};
static const uint16_t descending_words[64] = {65535, 0, [63] = 0x8000};
static const uint16_t flat_words[64] = {32768, 32768, [63] = 32767};
static const uint8_t descending_bytes[64] = {255, 0, [63] = 129};

struct lookup_case {
    const char *name;
    const void *table;
    uint32_t coordinate, expected;
};

static const struct lookup_case stock_cases[] = {
    {"b1-first", ROM_TABLE(MAF_TABLE_B1), 0, 211},
    {"b1-first-count", ROM_TABLE(MAF_TABLE_B1), 1, 211},
    {"b1-flat-end", ROM_TABLE(MAF_TABLE_B1), 0x600, 211},
    {"b1-flat-midpoint", ROM_TABLE(MAF_TABLE_B1), 0x680, 217},
    {"b1-before-seventh", ROM_TABLE(MAF_TABLE_B1), 0x6f0, 223},
    {"b1-seventh", ROM_TABLE(MAF_TABLE_B1), 0x700, 224},
    {"b1-seventh-midpoint", ROM_TABLE(MAF_TABLE_B1), 0x780, 236},
    {"b1-before-ninth", ROM_TABLE(MAF_TABLE_B1), 0x8ff, 287},
    {"b1-ninth", ROM_TABLE(MAF_TABLE_B1), 0x900, 288},
    {"b1-middle", ROM_TABLE(MAF_TABLE_B1), 0x2000, 7363},
    {"b1-high-unsigned-cell", ROM_TABLE(MAF_TABLE_B1), 0x3400, 33102},
    {"b1-high-unsigned-midpoint", ROM_TABLE(MAF_TABLE_B1), 0x3480, 34145},
    {"b1-penultimate", ROM_TABLE(MAF_TABLE_B1), 0x3e00, 58576},
    {"b1-penultimate-count", ROM_TABLE(MAF_TABLE_B1), 0x3e01, 58588},
    {"b1-penultimate-midpoint", ROM_TABLE(MAF_TABLE_B1), 0x3e80, 60160},
    {"b1-before-last", ROM_TABLE(MAF_TABLE_B1), 0x3eff, 61731},
    {"b1-signed-last-return", ROM_TABLE(MAF_TABLE_B1), 0x3f00, 0xfffff130U},
    {"b1-maximum-word", ROM_TABLE(MAF_TABLE_B1), 0xffff, 0xfffff130U},
    {"b1-word-wrap", ROM_TABLE(MAF_TABLE_B1), 0x10000, 211},
    {"b1-high-bits-truncate", ROM_TABLE(MAF_TABLE_B1), 0x80000680U, 217},
    {"b2-first", ROM_TABLE(MAF_TABLE_B2), 0, 222},
    {"b2-first-count", ROM_TABLE(MAF_TABLE_B2), 1, 222},
    {"b2-flat-end", ROM_TABLE(MAF_TABLE_B2), 0x600, 222},
    {"b2-flat-midpoint", ROM_TABLE(MAF_TABLE_B2), 0x680, 226},
    {"b2-before-seventh", ROM_TABLE(MAF_TABLE_B2), 0x6f0, 230},
    {"b2-seventh", ROM_TABLE(MAF_TABLE_B2), 0x700, 231},
    {"b2-seventh-midpoint", ROM_TABLE(MAF_TABLE_B2), 0x780, 242},
    {"b2-before-ninth", ROM_TABLE(MAF_TABLE_B2), 0x8ff, 289},
    {"b2-ninth", ROM_TABLE(MAF_TABLE_B2), 0x900, 290},
    {"b2-middle", ROM_TABLE(MAF_TABLE_B2), 0x2000, 7332},
    {"b2-high-unsigned-cell", ROM_TABLE(MAF_TABLE_B2), 0x3400, 32854},
    {"b2-high-unsigned-midpoint", ROM_TABLE(MAF_TABLE_B2), 0x3480, 33889},
    {"b2-penultimate", ROM_TABLE(MAF_TABLE_B2), 0x3e00, 58203},
    {"b2-penultimate-count", ROM_TABLE(MAF_TABLE_B2), 0x3e01, 58215},
    {"b2-penultimate-midpoint", ROM_TABLE(MAF_TABLE_B2), 0x3e80, 59782},
    {"b2-before-last", ROM_TABLE(MAF_TABLE_B2), 0x3eff, 61349},
    {"b2-signed-last-return", ROM_TABLE(MAF_TABLE_B2), 0x3f00, 0xffffefb2U},
    {"b2-maximum-word", ROM_TABLE(MAF_TABLE_B2), 0xffff, 0xffffefb2U},
    {"b2-word-wrap", ROM_TABLE(MAF_TABLE_B2), 0x10000, 222},
    {"b2-high-bits-truncate", ROM_TABLE(MAF_TABLE_B2), 0x80000680U, 226},
};

static const struct lookup_case synthetic_cases[] = {
    {"ascending-first", ascending_words, 0, 0},
    {"ascending-count", ascending_words, 1, 255},
    {"ascending-midpoint", ascending_words, 0x80, 32767},
    {"ascending-before-second", ascending_words, 0xff, 65279},
    {"ascending-second-unsigned", ascending_words, 0x100, 65535},
    {"ascending-last-signed", ascending_words, 0x3f00, 0xfffffedcU},
    {"ascending-maximum-word", ascending_words, 0xffff, 0xfffffedcU},
    {"ascending-word-wrap", ascending_words, 0x10000, 0},
    {"descending-first-unsigned", descending_words, 0, 65535},
    {"descending-count", descending_words, 1, 65280},
    {"descending-midpoint", descending_words, 0x80, 32768},
    {"descending-before-second", descending_words, 0xff, 256},
    {"descending-second", descending_words, 0x100, 0},
    {"descending-last-signed", descending_words, 0x3f00, 0xffff8000U},
    {"flat-first-unsigned", flat_words, 0, 32768},
    {"flat-midpoint", flat_words, 0x80, 32768},
    {"flat-last-positive", flat_words, 0x3f00, 32767},
    {"flat-high-bits-truncate", flat_words, 0x80000080U, 32768},
};

struct format_case {
    const char *name;
    const void *table;
    uint32_t format, coordinate, expected;
};

static const struct format_case format_cases[] = {
    {"direct-word-ascending", ascending_words, 0x100, 0x80, 32767},
    {"direct-word-descending", descending_words, 0x100, 0x80, 32768},
    {"direct-byte-descending", descending_bytes, 0, 0x80, 128},
    {"direct-byte-before-last", descending_bytes, 0, 0x3eff, 128},
};

struct caller_case {
    const char *name;
    uint16_t input_one, input_two, expected_one, expected_two;
};

static const struct caller_case caller_cases[] = {
    {"both-first", 0, 0, 211, 222},
    {"both-first-count", 1, 1, 211, 222},
    {"both-before-seventh", 0x6f, 0x6f, 223, 230},
    {"both-seventh", 0x70, 0x70, 224, 231},
    {"independent-fractions", 0x78, 0x88, 236, 271},
    {"independent-cells", 0x200, 0x340, 7363, 32854},
    {"both-penultimate", 0x3e0, 0x3e0, 58576, 58203},
    {"both-penultimate-count", 0x3e1, 0x3e1, 58774, 58400},
    {"both-penultimate-midpoint", 0x3e8, 0x3e8, 60160, 59782},
    {"both-before-last", 0x3ef, 0x3ef, 61546, 61164},
    {"both-last-unsigned-store", 0x3f0, 0x3f0, 61744, 61362},
    {"both-after-last", 0x3ff, 0x3ff, 61744, 61362},
    {"both-original-full-scale", 0x400, 0x400, 61744, 61362},
    {"both-last-low-12-bits", 0xfff, 0xfff, 61744, 61362},
    {"both-low-12-bit-wrap", 0x1000, 0x1000, 211, 222},
    {"both-high-nibble-truncate", 0x1068, 0x1068, 217, 226},
    {"both-last-positive-word", 0x7fff, 0x7fff, 61744, 61362},
    {"both-high-unsigned-word", 0x8000, 0x8000, 211, 222},
    {"both-high-unsigned-fraction", 0x83e8, 0x83e8, 60160, 59782},
    {"both-maximum-word", 0xffff, 0xffff, 61744, 61362},
};

struct window {
    uint32_t start;
    size_t size;
    uint8_t before[0xa0];
};

static struct window windows[] = {
    {0xffff1048U, 0x30, {0}},
    {0xffff1e10U, 0xa0, {0}},
    {0xffff56b0U, 0x20, {0}},
};

static volatile uint8_t *ram_pointer(uint32_t original)
{
    return (volatile uint8_t *)(uintptr_t)(TEST_RAM_BASE + (original & 0xffffU));
}

static int fail_value(const char *name, const char *field, uint32_t actual, uint32_t expected)
{
    printf("VQ_SH_ELF_STOCK_CODE status=FAIL case=%s field=%s actual=%08lx expected=%08lx\n",
           name, field, (unsigned long)actual, (unsigned long)expected);
    return 0;
}

static int run_lookup(const struct lookup_case *test, uint32_t macl)
{
    uint32_t result, state[1];
    size_t index;
    const volatile uint16_t *table = test->table;
    uint16_t before[64];
    for (index = 0; index < ARRAY_SIZE(before); ++index)
        before[index] = table[index];
    result = stock_invoke_word_curve(CURVE_ENTRY, (uint32_t)(uintptr_t)test->table,
                                    test->coordinate, macl, state);
    if (result != test->expected)
        return fail_value(test->name, "return-register", result, test->expected);
    if (state[0] != macl)
        return fail_value(test->name, "preserved-macl", state[0], macl);
    for (index = 0; index < ARRAY_SIZE(before); ++index)
        if (table[index] != before[index])
            return fail_value(test->name, "read-only-table", (uint32_t)index, 0);
    return 1;
}

static int run_caller(const struct caller_case *test, uint32_t macl)
{
    uint32_t result, state[3];
    size_t index, window_index;
    uint16_t tables_before[2][64];
    const volatile uint16_t *tables[] = {ROM_TABLE(MAF_TABLE_B1), ROM_TABLE(MAF_TABLE_B2)};
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index)
            ram_pointer(window->start)[index] = (uint8_t)(17U * index + 29U);
    }
    *(volatile uint16_t *)ram_pointer(MAF_INPUT_B1) = test->input_one;
    *(volatile uint16_t *)ram_pointer(MAF_INPUT_B2) = test->input_two;
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index)
            window->before[index] = ram_pointer(window->start)[index];
    }
    for (window_index = 0; window_index < ARRAY_SIZE(tables); ++window_index)
        for (index = 0; index < 64; ++index)
            tables_before[window_index][index] = tables[window_index][index];
    result = stock_invoke_maf_transfer(REGION_ENTRY,
                                      (uint32_t)(uintptr_t)ram_pointer(INPUT_BASE), macl, state);
    if (*(volatile uint16_t *)ram_pointer(MAF_OUTPUT_B1) != test->expected_one)
        return fail_value(test->name, "bank-one-word",
                          *(volatile uint16_t *)ram_pointer(MAF_OUTPUT_B1), test->expected_one);
    if (*(volatile uint16_t *)ram_pointer(MAF_OUTPUT_B2) != test->expected_two)
        return fail_value(test->name, "bank-two-delay-slot-word",
                          *(volatile uint16_t *)ram_pointer(MAF_OUTPUT_B2), test->expected_two);
    if (result != 0 || *(volatile uint16_t *)ram_pointer(CORRECTION_OUTPUT) != 0)
        return fail_value(test->name, "stock-zero-correction-path", result, 0);
    if (state[0] != macl || state[1] != (uint32_t)(uintptr_t)ram_pointer(INPUT_BASE)
        || state[2] != GBR_SEED)
        return fail_value(test->name, "preserved-macl-base-gbr", 1, 0);
    for (window_index = 0; window_index < ARRAY_SIZE(windows); ++window_index) {
        struct window *window = &windows[window_index];
        for (index = 0; index < window->size; ++index) {
            uint32_t address = window->start + (uint32_t)index;
            if ((address >= MAF_OUTPUT_B1 && address < MAF_OUTPUT_B1 + 2U)
                || (address >= MAF_OUTPUT_B2 && address < MAF_OUTPUT_B2 + 2U)
                || (address >= CORRECTION_OUTPUT && address < CORRECTION_OUTPUT + 2U))
                continue;
            if (ram_pointer(address)[0] != window->before[index])
                return fail_value(test->name, "read-only-input-and-neighbor", address, 0);
        }
    }
    for (window_index = 0; window_index < ARRAY_SIZE(tables); ++window_index)
        for (index = 0; index < 64; ++index)
            if (tables[window_index][index] != tables_before[window_index][index])
                return fail_value(test->name, "read-only-stock-curve", (uint32_t)index, 0);
    return 1;
}

int main(void)
{
    size_t index;
    for (index = 0; index < ARRAY_SIZE(stock_cases); ++index)
        if (!run_lookup(stock_cases + index, MACL_SEED ^ (uint32_t)index))
            return 1;
    for (index = 0; index < ARRAY_SIZE(synthetic_cases); ++index)
        if (!run_lookup(synthetic_cases + index, ~MACL_SEED ^ (uint32_t)index))
            return 1;
    for (index = 0; index < ARRAY_SIZE(format_cases); ++index) {
        const struct format_case *test = format_cases + index;
        uint32_t result = stock_invoke_format_curve(BODY_ENTRY, test->format,
                                                    (uint32_t)(uintptr_t)test->table,
                                                    test->coordinate);
        if (result != test->expected)
            return fail_value(test->name, "direct-body-result", result, test->expected);
    }
    for (index = 0; index < ARRAY_SIZE(caller_cases); ++index)
        if (!run_caller(caller_cases + index, MACL_SEED ^ (uint32_t)index))
            return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY,
           (unsigned long)(ARRAY_SIZE(stock_cases) + ARRAY_SIZE(synthetic_cases)
                           + ARRAY_SIZE(format_cases) + ARRAY_SIZE(caller_cases)));
    return 0;
}
