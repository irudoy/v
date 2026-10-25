! Exact MAF-summary and shared-status contributor instructions and pointer pools.
    .text
    .balign 4
    .set ORIGIN,0x4f734
    .org 0x4f736-ORIGIN
L_0004f736:
    mov.l L_0004f910,r6
    mov.b @r6,r0
    tst #0x80,r0
    bt L_0004f752
    mov.l L_0004f914,r6
    mov #0x16,r0
    mov.b @(r0,r6),r2
    mov #-0x40,r6
    extu.b r6,r6
    extu.b r2,r2
    cmp/ge r6,r2
    bf L_0004f752
    bra L_0004f754
    mov #0x1,r2
L_0004f752:
    mov #0x0,r2
L_0004f754:
    rts
    mov r2,r0
    .org 0x4f910-ORIGIN
L_0004f910:
    .long 0xffff2448
L_0004f914:
    .long 0xffff119c
    .org 0x4faa0-ORIGIN
L_0004faa0:
    mov.l L_0004fb9c,r6
    mov.b @(0x4,r6),r0
    tst #0x2,r0
    movt r0
    rts
    xor #0x1,r0
    .org 0x4fb9c-ORIGIN
L_0004fb9c:
    .long 0xffff4188
