! Observing return after an exact bounded I/O software window.
    .text
    .balign 2
io_access_return:
    mov.l @(24,r15),r7
    lds r7,pr
    rts
    nop
