! Natural bank-indexed signed MAF contribution sum and publication.
    .text
    .balign 4
L_0003b224:
    mov.l L_0003b38c,r2
    extu.b r4,r4
    shll2 r4
    mov.w @(0xe,r2),r0
    mov.l L_0003b390,r2
    mov r0,r5
    mov r4,r0
    add #0xc,r2
    mov.l @(r0,r2),r6
    mov #0x38,r0
    add r5,r6
    mov.l L_0003b394,r5
    mov.w @(r0,r5),r2
    extu.w r2,r5
    add r5,r6
    cmp/pz r6
    bt L_0003b248
    mov #0,r6
L_0003b248:
    mov.l L_0003b398,r2
    mov r4,r0
    add #4,r2
    rts
    mov.l r6,@(r0,r2)
    .org 0x3b38c - 0x3b224
L_0003b38c:
    .long 0xffff1e1c
L_0003b390:
    .long 0xffff1dec
L_0003b394:
    .long 0xffff2330
L_0003b398:
    .long 0xffff1048
