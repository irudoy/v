/* SH-2E CPU entry probes; no peripheral or interrupt-controller model. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

extern void irq_probe(void);
extern void irq_handler(void);
extern void irq_handler_alt(void);
extern void irq_trap_handler(void);

#ifndef PROBE_EXIT
#define PROBE_EXIT 0
#endif

volatile uint32_t irq_vectors[256] __attribute__((aligned(1024)));
volatile uint32_t irq_vectors_alt[256] __attribute__((aligned(1024)));
volatile uint32_t irq_hits, irq_saved_pc, irq_saved_sr, irq_handler_sr;
volatile uint32_t irq_entry_sp, irq_expected_sp, irq_after_sr;
volatile uint32_t irq_after_r0, irq_after_r1, irq_value, irq_second;
volatile uint32_t irq_seen_value, irq_seen_second;
volatile uint32_t irq_iterations, irq_seen_iterations;
volatile uint32_t irq_rte_sp;
volatile uint32_t irq_trap_hits, irq_outer_resumed;
volatile uint32_t irq_caller_resumed, irq_outer_sr;
volatile uint32_t irq_caller_sr_before, irq_caller_sr_after;

void irq_exit_handler(void)
{
    exit(PROBE_EXIT);
}

int main(void)
{
    for (unsigned index = 0; index < 256; ++index) {
        irq_vectors[index] = (uint32_t)(uintptr_t)irq_handler;
        irq_vectors_alt[index] = (uint32_t)(uintptr_t)irq_handler_alt;
    }
    irq_vectors[0x40] = (uint32_t)(uintptr_t)irq_trap_handler;
    __asm__ volatile ("ldc %0,vbr\n\tnop" : : "r" (irq_vectors) : "memory");
    irq_probe();
    if (irq_hits > 1)
        return 10;
    if (irq_hits && (irq_saved_sr != irq_after_sr ||
                     irq_entry_sp + 8 != irq_expected_sp))
        return 11;
    printf("VQ_SH_IRQ_PROBE status=PASS hits=%u saved_pc=%08x saved_sr=%08x "
           "handler_sr=%08x entry_sp=%08x expected_sp=%08x after_sr=%08x "
           "after_r0=%08x after_r1=%08x seen_value=%08x seen_second=%08x "
           "seen_iterations=%08x rte_sp=%08x trap_hits=%08x outer_resumed=%08x "
           "caller_resumed=%08x outer_sr=%08x caller_sr_before=%08x caller_sr_after=%08x\n",
           (unsigned)irq_hits, (unsigned)irq_saved_pc, (unsigned)irq_saved_sr,
           (unsigned)irq_handler_sr, (unsigned)irq_entry_sp, (unsigned)irq_expected_sp,
           (unsigned)irq_after_sr, (unsigned)irq_after_r0, (unsigned)irq_after_r1,
           (unsigned)irq_seen_value, (unsigned)irq_seen_second,
           (unsigned)irq_seen_iterations, (unsigned)irq_rte_sp,
           (unsigned)irq_trap_hits, (unsigned)irq_outer_resumed,
           (unsigned)irq_caller_resumed, (unsigned)irq_outer_sr,
           (unsigned)irq_caller_sr_before, (unsigned)irq_caller_sr_after);
    return PROBE_EXIT;
}
