! JK08A conditional tooth-period normalization at original stock addresses.
! The assembly starts at 0x0002911c. The gap between the conditional path
! and the ordinary copy contains original pool words, not instructions.
! The fixture places its return at 0x00029168, outside both tested spans.
    .text
    .balign 4
normalization_select:
    mov.b @(4,r15),r0
    tst r0,r0
    bt ordinary_copy
    mov.w tooth_offset,r0
    mov.b @(r0,r8),r0
    cmp/eq #8,r0
    bf ordinary_copy
    mov.w factor,r6
    extu.w r13,r13
    mov.w reference_offset,r0
    mul.l r13,r6
    sts macl,r2
    shlr16 r2
    mov.w r2,@(r0,r9)
    mov.w interval_offset,r0
    mov.w @(r0,r9),r7
    mov.w normalized_offset,r0
    extu.w r7,r7
    mul.l r7,r6
    sts macl,r2
    shlr16 r2
    bra normalization_end
    mov.w r2,@(r0,r9)
sync_base:
    .word 0x84fb
tooth_offset:
    .word 0x0126
    .word 0x0127
    .word 0x06e0
    .word 0x84e8
factor:
    .word 0x5555
reference_offset:
    .word 0x02a2
interval_offset:
    .word 0x02c6
normalized_offset:
    .word 0x02c8
ordinary_copy:
    mov.w ordinary_reference_offset,r0
    mov.w r13,@(r0,r9)
    mov.w ordinary_interval_offset,r0
    mov.w @(r0,r9),r7
    mov.w ordinary_normalized_offset,r0
    mov.w r7,@(r0,r9)
normalization_end:
    .org 0xf2
ordinary_reference_offset:
    .word 0x02a2
ordinary_interval_offset:
    .word 0x02c6
ordinary_normalized_offset:
    .word 0x02c8
