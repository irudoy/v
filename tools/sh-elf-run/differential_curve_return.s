! Observing return after the explicit stock difference-divisor window.
    .text
    .balign 2
differential_curve_return:
    mov.l @(24,r15),r7
    lds r7,pr
    rts
    nop
