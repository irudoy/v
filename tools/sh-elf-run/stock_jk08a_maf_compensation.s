! JK08A MAF word compensation and unsigned divider at their stock addresses.
! Link at 0x00009584; the two initial padding bytes are outside tested spans.
! The image fixture aliases four declared RAM pools after byte identity.
    .text
    .balign 4
    .org 2
correction_multiplier:
    .word 335
    .org 0x0000958c - 0x00009584
denominator_bias:
    .word 80

    .org 0x00021ce0 - 0x00009584
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
    .org 0x00021dc8 - 0x00009584
fault_pointer:
    .long 0xffff9818
fault_value:
    .long 0x0000044e

    .org 0x0003ae8a - 0x00009584
maf_compensate:
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    mov.l correction_context,r0
    ldc r0,gbr
    add #-4,r15
    mov.l input_base,r2
    extu.b r4,r5
    mov.b @(0xe,gbr),r0
    mov r5,r13
    shll r13
    add #4,r2
    extu.b r0,r7
    mov r13,r0
    mov.w @(r0,r2),r6
    mov r5,r2
    add #1,r2
    tst r2,r7
    bf/s initialized
    mov.w r6,@r15
    mov.l output_base,r2
    add #1,r5
    or r5,r7
    add #0x2c,r2
    mov.w r6,@(r0,r2)
    mov r7,r0
    bra compensate_return
    mov.b r0,@(0xe,gbr)
initialized:
    mov.l output_base,r14
    mov r13,r0
    mov.l calibration_pointer,r4
    mov r14,r2
    add #0x2c,r2
    mov.w @(r0,r2),r7
    mov.w @(6,r4),r0
    mov #-1,r4
    extu.w r7,r7
    extu.w r0,r12
    mov r7,r2
    add r12,r2
    extu.w r4,r4
    cmp/gt r4,r2
    bf sum_fits
    bra denominator_ready
    mov r4,r7
sum_fits:
    mov.l calibration_pointer,r3
    mov.w @(6,r3),r0
    extu.w r0,r6
    add r6,r7
denominator_ready:
    tst r7,r7
    bf nonzero_denominator
    bra compensate_store
    mov #-1,r5
nonzero_denominator:
    stc gbr,r4
    mov.l calibration_pointer,r3
    add #0x30,r4
    mov r5,r0
    shll2 r0
    mov.l @(r0,r4),r5
    mov r7,r0
    mov.w @r3,r7
    mov r5,r2
    shlr16 r2
    extu.w r7,r7
    mul.l r2,r7
    extu.w r5,r5
    sts macl,r4
    mul.l r5,r7
    sts macl,r2
    shlr16 r2
    add r2,r4
    mov.l divider_pointer,r2
    jsr @r2
    mov r4,r1
    mov r0,r5
compensate_store:
    mov.w @r15,r6
    add #0x2c,r14
    mov r13,r0
    extu.w r6,r6
    sub r5,r6
    mov.w r6,@(r0,r14)
compensate_return:
    add #4,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    rts
    mov.l @r15+,r12

    .org 0x0003b0f8 - 0x00009584
correction_context:
    .long 0xffff3968
input_base:
    .long 0xffff1018
output_base:
    .long 0xffff1e1c
calibration_pointer:
    .long correction_multiplier
divider_pointer:
    .long unsigned_divide
