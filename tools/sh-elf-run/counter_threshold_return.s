! Observing return after the explicit stock counter-threshold window.
    .text
    .balign 2
counter_threshold_return:
    mov.l @(24,r15),r7
    lds r7,pr
    rts
    nop
