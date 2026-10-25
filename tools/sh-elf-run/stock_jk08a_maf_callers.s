! Bounded dual-bank caller instructions; callee bodies use their own stock units.
    .text
    .balign 4
    .org 0x3a91a - 0x3a918
L_0003a91a:
    bsr L_0003ae8a
    mov r12,r4
    bsr L_0003ae8a
    mov r13,r4
    .org 0x3ae8a - 0x3a918
L_0003ae8a:
    .org 0x3c3b6 - 0x3a918
L_0003c3b6:
    bsr L_0003c408
    mov #0,r4
    bsr L_0003c408
    mov #1,r4
    .org 0x3c408 - 0x3a918
L_0003c408:
