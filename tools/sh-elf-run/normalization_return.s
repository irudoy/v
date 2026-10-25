! Observing return outside each stock window; SP+24 belongs to stock output data.
    .text
    .balign 2
normalization_return:
    mov.l @(28,r15),r7
    lds r7,pr
    rts
    nop
