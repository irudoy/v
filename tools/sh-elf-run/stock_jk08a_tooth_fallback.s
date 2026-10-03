! JK08A fallback period quotient and its unsigned divider at stock addresses.
! The fixture returns at 0x0002b820, after the word publication and before
! the marker logic. Intervening assembler padding is not executable fixture code.
    .text
    .balign 4
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
unsigned_divide_end:

    .org 0xe8
fault_pointer:
    .long 0xffff9818
fault_value:
    .long 0x0000044e

    .org 0x9b20
fallback_period:
    mov.l interval_base,r12
    mov r6,r1
    mov.w capture_offset,r0
    mov.l @(0x28,r12),r2
    mov.l divider,r4
    mov.l r6,@(r0,r10)
    mov #12,r0
    mov.l r2,@r15
    jsr @r4
    mov.l r6,@(0x28,r12)
    mov r0,r2
    mov.w normalized_offset,r0
    mov.l marker_pointer,r5
    mov.w r2,@(r0,r10)
    mov.w raw_period_offset,r0
    mov.w r2,@(r0,r10)
fallback_period_end:
    .org 0x9b7e
capture_offset:
    .word 0x02e0
normalized_offset:
    .word 0x02c8
raw_period_offset:
    .word 0x02c6
    .org 0x9b98
interval_base:
    .long 0xffff11d4
divider:
    .long 0x00021ce0
marker_pointer:
    .long 0xffff2465
