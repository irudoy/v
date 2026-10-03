#include <stdint.h>
#include <stdio.h>

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(ADDR4) \
    || !defined(ADDR15) || !defined(MAF_SAMPLE_B1) || !defined(MAF_SAMPLE_B2) \
    || !defined(ADC_BASE)
#error "the verifier defines the MAF ADC entry, sources, and outputs"
#endif

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define TEST_RAM_BASE 0x01000000U

extern uint32_t stock_invoke_adc(uint32_t entry, uint32_t mmio_base);

struct stock_case {
    const char *name;
    uint16_t bank1, bank2, sample1, sample2;
};

static const struct stock_case stock_cases[] = {
    {"zero-banks", 0, 0, 0, 0},
    {"discard-low-six-bits", 63, 62, 0, 0},
    {"first-count", 64, 127, 1, 1},
    {"distinct-counts", 128, 255, 2, 3},
    {"aligned-distinct-banks", 0x0040, 0x8000, 1, 512},
    {"before-signed-boundary", 0x7fff, 0x8000, 511, 512},
    {"reverse-signed-boundary", 0x8000, 0x7fff, 512, 511},
    {"independent-bank-values", 0x1234, 0xabcd, 72, 687},
    {"maximum-counts", 0xffff, 0xffc0, 1023, 1023},
    {"before-maximum-count", 0xff80, 0xffc0, 1022, 1023},
    {"same-count-different-low-bits", 0xab00, 0xab3f, 684, 684},
    {"alternating-bits", 0xa5a5, 0x5a5a, 662, 361},
};

static volatile uint8_t *ram_pointer(uint32_t address)
{
    return (volatile uint8_t *)(uintptr_t)(TEST_RAM_BASE + (address & 0xffffU));
}

static int run_case(const struct stock_case *test)
{
    uint8_t input_before[0x40], output_before[0x40];
    size_t index;
    uint32_t result;
    for (index = 0; index < 0x40; ++index) {
        ram_pointer(ADC_BASE)[index] = (uint8_t)(19U * index + 7U);
        ram_pointer(0xffff1d50U)[index] = (uint8_t)(29U * index + 11U);
    }
    *(volatile uint16_t *)ram_pointer(ADDR4) = test->bank1;
    *(volatile uint16_t *)ram_pointer(ADDR15) = test->bank2;
    for (index = 0; index < 0x40; ++index) {
        input_before[index] = ram_pointer(ADC_BASE)[index];
        output_before[index] = ram_pointer(0xffff1d50U)[index];
    }
    result = stock_invoke_adc(REGION_ENTRY, (uint32_t)(uintptr_t)ram_pointer(ADC_BASE));
    if (*(volatile uint16_t *)ram_pointer(MAF_SAMPLE_B1) != test->sample1
        || *(volatile uint16_t *)ram_pointer(MAF_SAMPLE_B2) != test->sample2
        || result != 0x30) {
        printf("VQ_SH_ELF_STOCK_CODE status=FAIL case=%s field=sample-or-return\n", test->name);
        return 0;
    }
    for (index = 0; index < 0x40; ++index) {
        uint32_t address = 0xffff1d50U + (uint32_t)index;
        if (ram_pointer(ADC_BASE)[index] != input_before[index]) {
            printf("VQ_SH_ELF_STOCK_CODE status=FAIL case=%s field=read-only-mmio\n", test->name);
            return 0;
        }
        if ((address >= MAF_SAMPLE_B1 && address < MAF_SAMPLE_B1 + 2U)
            || (address >= MAF_SAMPLE_B2 && address < MAF_SAMPLE_B2 + 2U))
            continue;
        if (ram_pointer(address)[0] != output_before[index]) {
            printf("VQ_SH_ELF_STOCK_CODE status=FAIL case=%s field=output-neighbor\n", test->name);
            return 0;
        }
    }
    return 1;
}

int main(void)
{
    size_t index;
    for (index = 0; index < ARRAY_SIZE(stock_cases); ++index)
        if (!run_case(stock_cases + index))
            return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n", REGION_KEY,
           (unsigned long)ARRAY_SIZE(stock_cases));
    return 0;
}
