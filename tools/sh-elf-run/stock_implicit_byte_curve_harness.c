#include <stdint.h>
#include <stdio.h>

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(BODY_ENTRY) \
    || !defined(INJECTION_TABLE) || !defined(COLD_TIMING_TABLE)
#error "the verifier defines the stock curve entries and table symbols"
#endif

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define ROM_TABLE(address) ((const void *)(uintptr_t)(address))

extern uint32_t stock_invoke_curve(uint32_t entry, uint32_t table, uint32_t coordinate);
extern uint32_t stock_invoke_format_curve(uint32_t entry, uint32_t format,
                                         uint32_t table, uint32_t coordinate);

static const uint8_t descending_bytes[] = {255, 0, 0, 0, 0, 0, 0, 0};
static const uint16_t ascending_words[] = {0, 1000, 2000, 3000, 4000, 5000, 6000, 7000};
static const uint16_t descending_words[] = {8000, 4000, 4000, 4000, 4000, 4000, 4000, 4000};

struct curve_case {
    const char *name;
    const void *table;
    uint32_t coordinate, expected;
};

static const struct curve_case stock_cases[] = {
    {"timing-first", ROM_TABLE(COLD_TIMING_TABLE), 0, 128},
    {"timing-truncate-low", ROM_TABLE(COLD_TIMING_TABLE), 1, 128},
    {"timing-first-increment", ROM_TABLE(COLD_TIMING_TABLE), 5, 129},
    {"timing-first-midpoint", ROM_TABLE(COLD_TIMING_TABLE), 16, 132},
    {"timing-before-second", ROM_TABLE(COLD_TIMING_TABLE), 31, 136},
    {"timing-second", ROM_TABLE(COLD_TIMING_TABLE), 32, 137},
    {"timing-flat-third", ROM_TABLE(COLD_TIMING_TABLE), 64, 137},
    {"timing-flat-upper", ROM_TABLE(COLD_TIMING_TABLE), 127, 137},
    {"timing-fifth", ROM_TABLE(COLD_TIMING_TABLE), 128, 138},
    {"timing-before-sixth", ROM_TABLE(COLD_TIMING_TABLE), 159, 139},
    {"timing-sixth", ROM_TABLE(COLD_TIMING_TABLE), 160, 140},
    {"timing-seventh", ROM_TABLE(COLD_TIMING_TABLE), 192, 143},
    {"timing-before-last", ROM_TABLE(COLD_TIMING_TABLE), 223, 144},
    {"timing-signed-last-return", ROM_TABLE(COLD_TIMING_TABLE), 224, 0xffffff91U},
    {"timing-maximum-byte", ROM_TABLE(COLD_TIMING_TABLE), 255, 0xffffff91U},
    {"timing-word-truncation", ROM_TABLE(COLD_TIMING_TABLE), 256, 128},
    {"timing-high-bits-truncation", ROM_TABLE(COLD_TIMING_TABLE), 0x80000001U, 128},
    {"injection-first", ROM_TABLE(INJECTION_TABLE), 0, 133},
    {"injection-first-count", ROM_TABLE(INJECTION_TABLE), 1, 133},
    {"injection-middle", ROM_TABLE(INJECTION_TABLE), 127, 133},
    {"injection-before-last", ROM_TABLE(INJECTION_TABLE), 223, 133},
    {"injection-signed-last-return", ROM_TABLE(INJECTION_TABLE), 224, 0xffffff85U},
    {"injection-maximum-byte", ROM_TABLE(INJECTION_TABLE), 255, 0xffffff85U},
    {"injection-word-truncation", ROM_TABLE(INJECTION_TABLE), 256, 133},
    {"descending-first", descending_bytes, 0, 255},
    {"descending-truncate-low", descending_bytes, 1, 248},
    {"descending-quarter", descending_bytes, 8, 192},
    {"descending-midpoint", descending_bytes, 16, 128},
    {"descending-before-second", descending_bytes, 31, 8},
    {"descending-second", descending_bytes, 32, 0},
};

struct format_case {
    const char *name;
    const void *table;
    uint32_t coordinate, format, expected;
};

static const struct format_case format_cases[] = {
    {"word-first", ascending_words, 0, 0x100, 0},
    {"word-first-midpoint", ascending_words, 16, 0x100, 500},
    {"word-before-second", ascending_words, 31, 0x100, 968},
    {"word-second", ascending_words, 32, 0x100, 1000},
    {"word-before-seventh", ascending_words, 191, 0x100, 5968},
    {"word-before-last", ascending_words, 223, 0x100, 6968},
    {"word-descending-first-count", descending_words, 1, 0x100, 7875},
    {"word-descending-midpoint", descending_words, 16, 0x100, 6000},
    {"word-descending-before-second", descending_words, 31, 0x100, 4125},
    {"direct-byte-format", descending_bytes, 16, 0, 128},
};

static int check_result(const char *name, uint32_t result, uint32_t expected)
{
    if (result == expected)
        return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=FAIL case=%s actual=%08lx expected=%08lx\n",
           name, (unsigned long)result, (unsigned long)expected);
    return 0;
}

int main(void)
{
    size_t index;
    for (index = 0; index < ARRAY_SIZE(stock_cases); ++index) {
        const struct curve_case *test = stock_cases + index;
        uint32_t result = stock_invoke_curve(REGION_ENTRY,
                                            (uint32_t)(uintptr_t)test->table, test->coordinate);
        if (!check_result(test->name, result, test->expected))
            return 1;
    }
    for (index = 0; index < ARRAY_SIZE(format_cases); ++index) {
        const struct format_case *test = format_cases + index;
        uint32_t result = stock_invoke_format_curve(BODY_ENTRY, test->format,
                                                    (uint32_t)(uintptr_t)test->table, test->coordinate);
        if (!check_result(test->name, result, test->expected))
            return 1;
    }
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY,
           (unsigned long)(ARRAY_SIZE(stock_cases) + ARRAY_SIZE(format_cases)));
    return 0;
}
