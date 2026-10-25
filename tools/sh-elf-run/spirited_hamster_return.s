! Observing return after the explicit stock byte-denominator window.
    .text
    .balign 2
spirited_hamster_return:
    mov.l @(24,r15),r7
    lds r7,pr
    rts
    nop
