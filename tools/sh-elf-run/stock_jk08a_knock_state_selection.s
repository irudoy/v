! Post-lookup arithmetic with preceding call/operand anchors kept unexecuted.
    .section .text
    .balign 4
P_9078: .word 0x0500

    .org 0x493fc - 0x9078
L_selection_gbr_anchor:
    mov.l P_4965c,r0
    ldc r0,gbr
    .org 0x495da - 0x9078
L_selection_normal_r9_anchor:
    mov.l P_496ac,r9
    .org 0x495e8 - 0x9078
L_selection_first_table_anchor:
    mov.l P_496b4,r4
    .org 0x495f6 - 0x9078
L_selection_lookup_target_anchor:
    mov.l P_496c0,r13
    .org 0x495fa - 0x9078
L_selection_first_call_anchor:
    jsr @r13
    mov r14,r6
    and #0x7f,r0
    mov.l P_496c4,r4
    mov.b r0,@(12,r15)
    .org 0x49610 - 0x9078
L_selection_second_call_anchor:
    jsr @r13
    extu.w r2,r7

L_selection_post_lookup_entry:
    and #0x7f,r0
    mov r0,r6
    mov #0x10,r0
    mov.b r6,@(r0,r15)
    mov.b @(0x11,gbr),r0
    tst #0x80,r0
    bt L_selection_second_gate
    bra L_selection_alternative_entry
    nop
L_selection_second_gate:
    mov.b @(0x0f,gbr),r0
    tst #0x40,r0
    bf L_selection_direct
    bra L_selection_alternative_entry
    nop
L_selection_direct:
    mov.b @(12,r15),r0
    mov.l P_49678,r3
    extu.b r0,r2
    mov #0x10,r0
    mov.b @(r0,r15),r6
    mov #-12,r0
    exts.w r2,r5
    extu.b r6,r6
    extu.b r0,r0
    sub r6,r5
    mov.w @(r0,r3),r2
    shll8 r5
    add r5,r2
L_selection_boundary:

    .org 0x4965c - 0x9078
P_4965c: .long 0xffff2458
    .org 0x49678 - 0x9078
P_49678: .long 0xffff128c
    .org 0x496ac - 0x9078
P_496ac: .long 0xffff22f8
    .org 0x496b4 - 0x9078
P_496b4: .long 0x00009a1a
    .org 0x496c0 - 0x9078
P_496c0: .long 0x00026230
    .org 0x496c4 - 0x9078
P_496c4: .long 0x00009b1a

    .org 0x499ae - 0x9078
L_selection_alternative_r9_anchor:
    mov.l P_49b38,r9
    .org 0x499b8 - 0x9078
L_selection_alternative_entry:
    mov.l P_49b28,r10
    mov.l P_49b2c,r3
    mov.w @(12,r10),r0
    mov r0,r2
    mov #-12,r0
    extu.b r0,r0
    mov.w @(r0,r3),r7
    mov r7,r4
    sub r2,r4
    mov.l P_49b3c,r2
    mov.w @r2,r6
    extu.w r6,r6
    cmp/gt r6,r4
    bf L_selection_slew_lower
    mov.w @(12,r10),r0
    add r6,r0
    mov r0,r7
L_selection_dynamic_bound:
    mov #0x12,r0
    mov.b @(r0,r9),r6
    mov #-1,r5
    shll8 r5
    extu.b r6,r6
    mul.l r6,r5
    sts macl,r2
    cmp/ge r2,r7
    bt L_selection_bound_pass
    mul.l r6,r5
    sts macl,r6
L_selection_positive_cap:
    cmp/pl r6
    bf L_selection_nonpositive
    bra L_selection_boundary
    mov #0,r2
L_selection_slew_lower:
    neg r6,r5
    cmp/ge r5,r4
    bt L_selection_dynamic_bound
    mov.w @(12,r10),r0
    sub r6,r0
    bra L_selection_dynamic_bound
    mov r0,r7
L_selection_bound_pass:
    bra L_selection_positive_cap
    mov r7,r6
L_selection_nonpositive:
    bra L_selection_boundary
    mov r6,r2

    .org 0x49b28 - 0x9078
P_49b28: .long 0xffff124c
    .org 0x49b2c - 0x9078
P_49b2c: .long 0xffff128c
    .org 0x49b38 - 0x9078
P_49b38: .long 0xffff22f8
    .org 0x49b3c - 0x9078
P_49b3c: .long 0x00009078
