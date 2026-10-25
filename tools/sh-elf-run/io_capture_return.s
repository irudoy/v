! Bounded native read restores only the stock prologue before observation.
    .text
    .balign 2
io_capture_return:
    add #12,r15
    lds.l @r15+,pr
    mov.l @r15+,r14
    rts
    nop
