    ! Simulator-only interrupt handler of the Rolling Launch interrupt rows.
    !
    ! The simulator interrupt hook enters it with SR and the return PC on
    ! the stack of the interrupted engine pass. It saves r0..r7, PR, MACH,
    ! MACL and GBR, calls irq_rolling_publish, restores them, stores the
    ! return marker and returns with RTE.
    .text
    .balign 2
    .global _irq_rolling_handler
    .type _irq_rolling_handler,@function
_irq_rolling_handler:
    mov.l r0,@-r15
    mov.l r1,@-r15
    mov.l r2,@-r15
    mov.l r3,@-r15
    mov.l r4,@-r15
    mov.l r5,@-r15
    mov.l r6,@-r15
    mov.l r7,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    mov.l irq_rolling_publish_address,r0
    jsr @r0
    nop
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r7
    mov.l @r15+,r6
    mov.l @r15+,r5
    mov.l @r15+,r4
    mov.l @r15+,r3
    mov.l @r15+,r2
    mov.l irq_rolling_returned_address,r1
    mov.l irq_rolling_returned_value,r0
    mov.l r0,@r1
    mov.l @r15+,r1
    mov.l @r15+,r0
    rte
    nop
    .balign 4
irq_rolling_publish_address:
    .long _irq_rolling_publish
irq_rolling_returned_address:
    .long _irq_rolling_returned
irq_rolling_returned_value:
    .long 0x52455445
    .size _irq_rolling_handler,.-_irq_rolling_handler
