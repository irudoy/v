! JK08A bank-indexed working copy and first-order MAF filter.
! Origin 0x8708 retains the coefficient byte, pools, and natural returns.
    .text
    .balign 4
    .org 2
filter_coefficient:
    .byte 26
    .org 0x3a982 - 0x8708
working_copy:
    mov.l working_window,r5
    extu.b r4,r4
    shll r4
    mov r5,r2
    add #12,r2
    mov r4,r0
    mov.w @(r0,r2),r6
    extu.w r6,r2
    mov #-1,r6
    extu.w r6,r6
    cmp/gt r6,r2
    bf copy_nonnegative
    mov r6,r2
copy_nonnegative:
    cmp/pz r2
    bt copy_publish
    mov #0,r2
copy_publish:
    add #16,r5
    mov r4,r0
    rts
    mov.w r2,@(r0,r5)
maf_filter:
    sts.l macl,@-r15
    stc.l gbr,@-r15
    mov.l filter_window,r0
    ldc r0,gbr
    mov.l working_window,r2
    extu.b r4,r1
    mov.l flags_window,r5
    shll r1
    add #16,r2
    mov r1,r0
    mov.w @(r0,r2),r6
    mov.b @(1,r5),r0
    stc gbr,r2
    tst #0x20,r0
    extu.w r6,r6
    add #4,r2
    bt/s copy_input
    mov r1,r0
    mov.w @(r0,r2),r4
    mov.l coefficient_pointer,r2
    extu.w r4,r4
    mov.b @r2,r7
    mov #1,r2
    shll8 r2
    extu.b r7,r7
    mul.l r6,r7
    sub r7,r2
    sts macl,r5
    mul.l r4,r2
    sts macl,r2
    add r2,r5
    shlr8 r5
    extu.w r5,r7
    cmp/eq r7,r6
    bt filtered_publish
    cmp/eq r7,r4
    bf filtered_publish
    cmp/gt r4,r6
    bf decrement
    bra filtered_publish
    add #1,r7
decrement:
    add #-1,r7
    extu.w r7,r7
filtered_publish:
    stc gbr,r2
    add #4,r2
    mov r1,r0
    bra filter_return
    mov.w r7,@(r0,r2)
copy_input:
    mov.w r6,@(r0,r2)
filter_return:
    ldc.l @r15+,gbr
    rts
    lds.l @r15+,macl
    .org 0x3ab68 - 0x8708
working_window:
    .long 0xffff1048
    .org 0x3ab70 - 0x8708
filter_window:
    .long 0xffff1dec
flags_window:
    .long 0xffff2460
coefficient_pointer:
    .long filter_coefficient
