! Independent reconstruction of both word-copy destinations.
    .text
    .balign 4
    .set ORIGIN,0x21314
    .org 0x21316-ORIGIN
    mov.l L_2145c,r7
    add #-94,r11
    mov.l L_21460,r14
    mov.w @r7,r2
    mov.w @(2,r7),r0
    mov.l L_21464,r7
    mov.w r2,@r14
    mov.w r2,@r7
    .org 0x2145c-ORIGIN
L_2145c: .long 0xffff227a
L_21460: .long 0xffff2276
L_21464: .long 0xffff227e
