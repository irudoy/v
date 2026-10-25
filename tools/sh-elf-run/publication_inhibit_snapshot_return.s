! Explicit observing return after the bounded stock snapshot instructions.
    .text
    .balign 2
publication_snapshot_return:
    mov.l @(24,r15),r7
    lds r7,pr
    rts
    nop
