! JK08A bank-selected MAF publisher, coefficient guard, and unsigned scaler.
! Link at 0x000087f8 and require exact code, literal, bound, and reset bytes.
! Padding between reconstructed spans is not part of the simulator fixture.
! The stock-image fixture aliases five RAM literals after byte identity.
    .text
    .balign 4
coefficient_bounds:
    .byte 0x87,0x79

    .org 0x000092be - 0x000087f8
coefficient_default:
    .word 0x8000

    .org 0x0003c408 - 0x000087f8
maf_publish:
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    add #-4,r15
    mov.l guard_pointer,r2
    mov.l sample_base,r14
    jsr @r2
    extu.b r4,r13
    shll r13
    mov r14,r2
    add #0x2e,r2
    mov r13,r0
    mov.w @(r0,r2),r4
    mov r15,r5
    mov.l scaler_pointer,r2
    jsr @r2
    add #0x2e,r14
    mov r13,r0
    mov.w @(r0,r14),r2
    mov.w sample_maximum,r3
    extu.w r2,r2
    cmp/eq r3,r2
    bf publish_cap
    mov.w @r15,r3
    add #1,r3
    mov.w r3,@r15
publish_cap:
    mov.w @r15,r5
    mov #-1,r6
    extu.w r6,r6
    extu.w r5,r5
    cmp/gt r6,r5
    bt publish_store
    mov r5,r6
publish_store:
    mov.l output_base,r2
    mov r13,r0
    add #4,r2
    mov.w r6,@(r0,r2)
    add #4,r15
    lds.l @r15+,pr
    mov.l @r15+,r14
    rts
    mov.l @r15+,r13

    .org 0x0003c474 - 0x000087f8
sample_maximum:
    .word 0x03ff
    .org 0x0003c48c - 0x000087f8
guard_pointer:
    .long coefficient_guard
sample_base:
    .long 0xffff1d34
scaler_pointer:
    .long unsigned_scale
output_base:
    .long 0xffff1018

    .org 0x00067188 - 0x000087f8
coefficient_guard:
    mov.l mode_base,r6
    mov.b @(6,r6),r0
    extu.b r0,r2
    mov r2,r0
    tst #8,r0
    bf guard_return
    mov.l guard_coefficient_base,r7
    mov.w guard_coefficient_offset,r0
    mov.l bounds_pointer,r4
    mov.w @(r0,r7),r5
    mov.b @(1,r4),r0
    extu.w r5,r5
    extu.b r0,r2
    shll8 r2
    cmp/ge r2,r5
    bf guard_reset
    mov.b @r4,r2
    extu.b r2,r6
    shll8 r6
    cmp/gt r6,r5
    bt guard_reset
    bra guard_return
    mov #0x55,r2
guard_reset:
    mov.l default_pointer,r6
    mov.w guard_coefficient_offset,r0
    mov.w @r6,r2
    mov.w r2,@(r0,r7)
    mov #-86,r2
    extu.b r2,r2
guard_return:
    rts
    mov r2,r0
guard_coefficient_offset:
    .word 0x0418
mode_base:
    .long 0xffff424c
guard_coefficient_base:
    .long 0xffff4558
bounds_pointer:
    .long coefficient_bounds
default_pointer:
    .long coefficient_default

    .org 0x000671d8 - 0x000087f8
unsigned_scale:
    sts.l macl,@-r15
    mov.l scale_coefficient_base,r6
    extu.w r4,r4
    mov.w scale_coefficient_offset,r0
    mov.w @(r0,r6),r2
    extu.w r2,r6
    mul.l r4,r6
    mov #-1,r6
    extu.w r6,r6
    sts macl,r2
    shlr8 r2
    shlr2 r2
    shlr2 r2
    shlr2 r2
    shlr r2
    cmp/hi r6,r2
    bf scale_store
    mov r6,r2
scale_store:
    mov.w r2,@r5
    rts
    lds.l @r15+,macl

    .org 0x0006726a - 0x000087f8
scale_coefficient_offset:
    .word 0x0418
scale_coefficient_base:
    .long 0xffff4558
