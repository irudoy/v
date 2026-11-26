/* Execute 24 stock SH7059 Service 0xA0/01 iterations over Package 3 RAM. */
#include <stdint.h>
#include <stdio.h>

#include A001_BINDINGS_HEADER

#define BYTE(addr) (*(volatile uint8_t *)(uintptr_t)(addr))
#define WORD(addr) (*(volatile uint16_t *)(uintptr_t)(addr))
#define LONG(addr) (*(volatile uint32_t *)(uintptr_t)(addr))

#define CHCR0_SHADOW 0x01029CCCU
#define CHCR1_SHADOW 0x01029CDCU
#define CHCR2_SHADOW 0x01029CECU
#define ADC_SHADOW_BASE 0x01028800U
#define EXT_WORDS 24U

extern uint32_t invoke_r4(uint32_t target, uint32_t r4_arg);
extern void a001_irq_handler(void);

volatile uint32_t a001_irq_hits = 0U;
volatile uint32_t a001_last_word_addr = 0U;
volatile uint32_t a001_irq_observed_word = 0U;
volatile uint32_t a001_chcr0_shadow_addr = CHCR0_SHADOW;

static uint32_t irq_vectors[128] __attribute__((aligned(4)));

static int fail(const char *stage, const char *field, uint32_t actual, uint32_t expected)
{
    printf(
        "VQ_SH_ELF_SH7059_RAM_TEST status=FAIL stage=%s field=%s actual=%08lx expected=%08lx\n",
        stage, field, (unsigned long)actual, (unsigned long)expected
    );
    return 1;
}

static void seed_epilogue_flags(void)
{
    BYTE(A001_COMPLETION_ADDR) &= (uint8_t)~A001_COMPLETION_MASK;
#if A001_EPILOGUE_CLR0_ADDR != 0U
    BYTE(A001_EPILOGUE_CLR0_ADDR) &= (uint8_t)~A001_EPILOGUE_CLR0_MASK;
#endif
#if A001_EPILOGUE_CLR1_ADDR != 0U
    BYTE(A001_EPILOGUE_CLR1_ADDR) &= (uint8_t)~A001_EPILOGUE_CLR1_MASK;
#endif
#if A001_EPILOGUE_CLR2_ADDR != 0U
    BYTE(A001_EPILOGUE_CLR2_ADDR) &= (uint8_t)~A001_EPILOGUE_CLR2_MASK;
#endif
#if A001_EPILOGUE_CLR3_ADDR != 0U
    BYTE(A001_EPILOGUE_CLR3_ADDR) &= (uint8_t)~A001_EPILOGUE_CLR3_MASK;
#endif
}

static void seed_adc_shadows(void)
{
    uint32_t off;
    for (off = 0U; off <= 0x16U; off += 2U)
        WORD(ADC_SHADOW_BASE + off) = (uint16_t)(0x0100U + off);
    for (off = 0x20U; off <= 0x36U; off += 2U)
        WORD(ADC_SHADOW_BASE + off) = (uint16_t)(0x0200U + off);
    for (off = 0x40U; off <= 0x4EU; off += 2U)
        WORD(ADC_SHADOW_BASE + off) = (uint16_t)(0x0300U + off);
}

static int check_words(const char *stage, const uint32_t expected[EXT_WORDS],
                       uint32_t guard_before, uint32_t guard_after)
{
    uint32_t i;
    if (LONG(A001_EXT_START - 4U) != guard_before)
        return fail(stage, "guard_before", LONG(A001_EXT_START - 4U), guard_before);
    for (i = 0U; i < EXT_WORDS; ++i) {
        uint32_t actual = LONG(A001_EXT_START + i * 4U);
        if (actual != expected[i])
            return fail(stage, "ext_word", actual, expected[i]);
    }
    if (LONG(A001_EXT_END) != guard_after)
        return fail(stage, "guard_after", LONG(A001_EXT_END), guard_after);
    return 0;
}

int main(void)
{
    static const uint32_t chcr_shadows[3] = {CHCR0_SHADOW, CHCR1_SHADOW, CHCR2_SHADOW};
    uint32_t expected[EXT_WORDS];
    uint32_t guard_before = 0xCAFEBABEU;
    uint32_t guard_after = 0xDEADBEEFU;
    uint32_t saved_sr;
    uint32_t i;

    for (i = 0U; i < EXT_WORDS; ++i)
        expected[i] = 0x13572460U + i * 0x01010101U;

    seed_adc_shadows();
    seed_epilogue_flags();
    LONG(A001_EXT_START - 4U) = guard_before;
    for (i = 0U; i < EXT_WORDS; ++i)
        LONG(A001_EXT_START + i * 4U) = expected[i];
    LONG(A001_EXT_END) = guard_after;
    LONG(A001_CURSOR_ADDR) = A001_EXT_START;

    a001_irq_hits = 0U;
    a001_last_word_addr = A001_EXT_END - 4U;
    a001_irq_observed_word = 0U;
    irq_vectors[80] = (uint32_t)(uintptr_t)&a001_irq_handler;

    __asm__ volatile ("ldc %0,vbr" : : "r" ((uint32_t)(uintptr_t)irq_vectors) : "memory");
    __asm__ volatile ("stc sr,%0" : "=r" (saved_sr));
    __asm__ volatile ("ldc %0,sr" : : "r" (saved_sr & ~0x000000F0U) : "memory");

    /* Cases 1..3: CHCR0.DE, CHCR1.DE, and CHCR2.DE each defer the sweep with zero stores. */
    for (i = 0U; i < 3U; ++i) {
        LONG(CHCR0_SHADOW) = 0U;
        LONG(CHCR1_SHADOW) = 0U;
        LONG(CHCR2_SHADOW) = 0U;
        LONG(chcr_shadows[i]) = 1U;
        (void)invoke_r4(A001_ENTRY, 1U);
        if (LONG(A001_CURSOR_ADDR) != A001_EXT_START)
            return fail("dma_defer", "cursor", LONG(A001_CURSOR_ADDR), A001_EXT_START);
        if (a001_irq_hits != 0U)
            return fail("dma_defer", "irq_hits", a001_irq_hits, 0U);
        if (check_words("dma_defer", expected, guard_before, guard_after))
            return 1;
    }

    /* Case 4: Clear CHCR0..2 and sweep all 24 Package 3 extension words.
       The one-shot IRQ fires on word 24's first pattern store, defers through
       restore + unmask, verifies restored word 24, and sets CHCR0.DE=1 to yield. */
    LONG(CHCR0_SHADOW) = 0U;
    LONG(CHCR1_SHADOW) = 0U;
    LONG(CHCR2_SHADOW) = 0U;
    (void)invoke_r4(A001_ENTRY, 1U);

    if (a001_irq_hits != 1U)
        return fail("sweep_24", "irq_hits", a001_irq_hits, 1U);
    if (a001_irq_observed_word != expected[EXT_WORDS - 1U])
        return fail("sweep_24", "irq_word", a001_irq_observed_word, expected[EXT_WORDS - 1U]);
    if (LONG(A001_CURSOR_ADDR) != A001_EXT_END)
        return fail("sweep_24", "cursor", LONG(A001_CURSOR_ADDR), A001_EXT_END);
    if ((BYTE(A001_COMPLETION_ADDR) & A001_COMPLETION_MASK) != 0U)
        return fail("sweep_24", "completion", BYTE(A001_COMPLETION_ADDR), 0U);
    if (check_words("sweep_24", expected, guard_before, guard_after))
        return 1;

    printf("VQ_SH_ELF_SH7059_RAM_TEST status=PASS cases=4 words=%u irq_hits=%lu\n",
        (unsigned)EXT_WORDS, (unsigned long)a001_irq_hits);
    return 0;
}
