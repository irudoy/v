! Bounded raw-word publication and signed timing-byte conversion.
! The two R9 base loads are byte-bound entry-context anchors, not called paths.
    .section .text
    .balign 4
    .org 0x495da - 0x495d8
L_timing_primary_r9_anchor:
    mov.l P_496ac,r9

    .org 0x4964a - 0x495d8
L_timing_conversion_entry:
    exts.w r2,r12
    mov.l P_496c8,r8
    mov r2,r0
    exts.w r12,r2
    cmp/pz r2
    bt/s L_timing_shift
    mov.w r0,@(12,r8)
    bra L_timing_negative
    mov #-1,r6

    .org 0x496ac - 0x495d8
P_496ac: .long 0xffff22f8
    .org 0x496c8 - 0x495d8
P_496c8: .long 0xffff120e
L_timing_negative:
    extu.b r6,r6
    add r6,r2
L_timing_shift:
    shlr8 r2
    swap.w r2,r0
    exts.b r0,r6
    xtrct r6,r0
    mov.b r0,@(2,r9)
L_timing_boundary:

    .org 0x499ae - 0x495d8
L_timing_alternate_r9_anchor:
    mov.l P_49b38,r9
    .org 0x49b38 - 0x495d8
P_49b38: .long 0xffff22f8
