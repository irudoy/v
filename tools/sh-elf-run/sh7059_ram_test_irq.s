/* Maskable IRQ handler for the SH7059 Service 0xA0/01 24-word sweep gate.
   Verifies that the 24th extension word is already restored when the deferred
   IRQ is accepted after LDC SR unmask, then sets CHCR0.DE=1 in the simulator
   DMAC shadow so the stock CHCR0 poll yields immediately after word 24. */
    .text
    .balign 4
    .global _a001_irq_handler
    .type _a001_irq_handler,@function
_a001_irq_handler:
    mov.l r0,@-r15
    mov.l r1,@-r15
    mov.l r2,@-r15
    mov.l r3,@-r15

    mov.l .L_hits,r1
    mov.l @r1,r0
    add #1,r0
    mov.l r0,@r1

    mov.l .L_last_addr_ptr,r1
    mov.l @r1,r2
    mov.l @r2,r0
    mov.l .L_obs_word,r1
    mov.l r0,@r1

    mov.l .L_chcr0_shadow_ptr,r1
    mov.l @r1,r2
    mov #1,r0
    mov.l r0,@r2

    mov.l @r15+,r3
    mov.l @r15+,r2
    mov.l @r15+,r1
    mov.l @r15+,r0
    rte
    nop

    .balign 4
.L_hits:
    .long _a001_irq_hits
.L_last_addr_ptr:
    .long _a001_last_word_addr
.L_obs_word:
    .long _a001_irq_observed_word
.L_chcr0_shadow_ptr:
    .long _a001_chcr0_shadow_addr
    .size _a001_irq_handler,.-_a001_irq_handler
