! Observing return after the explicit stock timing tail.
    .text
    .balign 2
timing_tail_return:
    mov.l @(24,r15),r7
    lds r7,pr
    rts
    nop
