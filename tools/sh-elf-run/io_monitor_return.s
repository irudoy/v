! Bounded stride prefix restores its stock local allocation.
    .text
    .balign 2
io_monitor_return:
    add #8,r15
    mov.l @(24,r15),r7
    lds r7,pr
    rts
    nop
