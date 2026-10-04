! JK08A Q7 BFS normalization and unsigned divider at their stock addresses.
! Origin 0x9534 retains the stock reference, pools, and exact instructions.
    .text
    .balign 4
load_reference:
    .word 27226
    .org 0x21ce0 - 0x9534
unsigned_divide:
    mov.l r2,@-r15
    tst r0,r0
    bt divide_by_zero
    extu.w r0,r2
    cmp/eq r2,r0
    bf long_divisor
    div0u
    shll8 r0
    cmp/hi r1,r0
    bf large_quotient
    .rept 8
    div1 r0,r1
    .endr
    rotcl r1
    mov.l @r15+,r2
    rts
    extu.b r1,r0
large_quotient:
    mov.l r3,@-r15
    extu.w r1,r3
    shll8 r0
    shlr16 r1
    .rept 16
    div1 r0,r1
    .endr
    extu.w r1,r2
    xor r2,r1
    addc r2,r2
    shll16 r2
    add r3,r1
    .rept 16
    div1 r0,r1
    .endr
    rotcl r1
    extu.w r1,r0
    add r2,r0
    mov.l @r15+,r3
    rts
    mov.l @r15+,r2
divide_by_zero:
    mov.l fault_pointer,r1
    mov.l fault_value,r2
    mov.l r2,@r1
    mov #0,r0
    rts
    mov.l @r15+,r2
long_divisor:
    div0u
    extu.w r1,r2
    shll16 r2
    shlr16 r1
    rotcl r2
    .rept 16
    div1 r0,r1
    rotcl r2
    .endr
    mov r2,r0
    rts
    mov.l @r15+,r2
    .org 0x21dc8 - 0x9534
fault_pointer:
    .long 0xffff9818
fault_value:
    .long 0x0000044e

    .org 0x3bd1c - 0x9534
normalize_load:
    mov.l reference_pointer,r6
    mov r5,r1
    shll2 r1
    shll2 r1
    mov.w @r6,r2
    shll2 r1
    shll r1
    jsr @r11
    extu.w r2,r0
    mov #-1,r6
    extu.b r6,r6
    cmp/hi r6,r0
    bt saturated
    mov.l bfs_pointer,r6
    mov.l reference_pointer,r5
    mov.w @(2,r6),r0
    mov.w @r5,r6
    extu.w r0,r1
    mov.l divider_pointer,r2
    shll2 r1
    shll2 r1
    shll2 r1
    shll r1
    extu.w r6,r5
    jsr @r2
    mov r5,r0
    bra publish
    mov r0,r2
saturated:
    mov #-1,r2
publish:
    mov r2,r6
    mov.l output_pointer,r2
    mov.b r6,@r2
    .org 0x3bdf0 - 0x9534
bfs_pointer:
    .long 0xffff1024
    .org 0x3be10 - 0x9534
output_pointer:
    .long 0xffff1048
reference_pointer:
    .long load_reference
divider_pointer:
    .long unsigned_divide
