! Natural bank-indexed diagnostic word copy and RTS delay-slot store.
    .text
    .balign 4
L_0003c45c:
    mov.l L_0003c490,r2
    extu.b r4,r0
    shll r0
    mov.w L_0003c476,r3
    add #0x2e,r2
    mov.w @(r0,r2),r6
    mov.l L_0003c49c,r2
    add r3,r2
    rts
    mov.w r6,@(r0,r2)
    .org 0x3c476 - 0x3c45c
L_0003c476:
    .word 0x07b2
    .org 0x3c490 - 0x3c45c
L_0003c490:
    .long 0xffff1d34
    .org 0x3c49c - 0x3c45c
L_0003c49c:
    .long 0xffff128c
