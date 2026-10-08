! Simulator helper records the complete stock exit separately from the C caller ABI.
! The JSR delay slot restores the independent incoming R7 from the local frame.
! The stock save footprint is observed at SP-160..SP+31.
! The 80-byte exit capture stays above the 32-byte local frame.
! Natural stock returns preserve their actual driver PR.
    .section .text
    .balign 4
    .global _stock_invoke_closed_loop_adjustment
    .type _stock_invoke_closed_loop_adjustment,@function
_stock_invoke_closed_loop_adjustment:
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-8,r15
    mov.l r6,@r15
    mov.l L_closed_loop_adjustment_abi8,r8
    mov.l L_closed_loop_adjustment_abi9,r9
    mov.l L_closed_loop_adjustment_abi10,r10
    mov.l L_closed_loop_adjustment_abi11,r11
    mov.l L_closed_loop_adjustment_abi12,r12
    mov.l L_closed_loop_adjustment_abi13,r13
    mov.l L_closed_loop_adjustment_abi14,r14
    mov.l L_closed_loop_adjustment_abigbr,r0
    ldc r0,gbr
    mov.l L_closed_loop_adjustment_abimach,r0
    lds r0,mach
    mov.l L_closed_loop_adjustment_abimacl,r0
    lds r0,macl
    bsr L_closed_loop_adjustment_inner
    nop
L_closed_loop_adjustment_outer_return:
    mov.l @r15,r6
    mov r6,r2
    add #100,r2
    add #36,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    add #8,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    mov #0,r0
    .balign 4
L_closed_loop_adjustment_abi8: .long 0x18283848
L_closed_loop_adjustment_abi9: .long 0x19293949
L_closed_loop_adjustment_abi10: .long 0x1a2a3a4a
L_closed_loop_adjustment_abi11: .long 0x1b2b3b4b
L_closed_loop_adjustment_abi12: .long 0x1c2c3c4c
L_closed_loop_adjustment_abi13: .long 0x1d2d3d4d
L_closed_loop_adjustment_abi14: .long 0x1e2e3e4e
L_closed_loop_adjustment_abigbr: .long 0x12344321
L_closed_loop_adjustment_abimach: .long 0x10203040
L_closed_loop_adjustment_abimacl: .long 0x50607080
L_closed_loop_adjustment_inner:
    mov r6,r2
    add #88,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-120,r15
    mov #112,r0
    mov.l r6,@(r0,r15)
    add #4,r0
    mov.l r4,@(r0,r15)
    mov r5,r3
    mov r15,r1
    add #-80,r1
    add #-80,r1
    mov.l L_closed_loop_adjustment_frame_seed,r0
    mov #40,r2
L_closed_loop_adjustment_seed_frame:
    mov.l r0,@r1
    add #4,r1
    add #17,r0
    dt r2
    bf L_closed_loop_adjustment_seed_frame
    mov r15,r1
    mov #8,r2
L_closed_loop_adjustment_seed_local:
    mov.l r0,@r1
    add #4,r1
    add #17,r0
    dt r2
    bf L_closed_loop_adjustment_seed_local
    mov r6,r2
    add #100,r2
    add #84,r2
    mov r15,r1
    add #-80,r1
    add #-80,r1
    mov #48,r0
L_closed_loop_adjustment_frame_before:
    mov.l @r1+,r4
    mov.l r4,@r2
    add #4,r2
    dt r0
    bf L_closed_loop_adjustment_frame_before
    mov.l @(60,r3),r0
    ldc r0,gbr
    mov r3,r2
    add #64,r2
    mov.l @r2+,r0
    lds r0,mach
    mov.l @r2,r0
    lds r0,macl
    mov r3,r2
    add #72,r2
    mov.l @r2,r0
    stc sr,r1
    mov.l L_closed_loop_adjustment_sr_mask,r2
    and r2,r1
    or r0,r1
    ldc r1,sr
    stc sr,r1
    mov r6,r2
    add #124,r2
    add #124,r2
    add #124,r2
    add #124,r2
    add #72,r2
    mov.l r1,@r2
    mov.l @(28,r3),r0
    mov.l r0,@(32,r15)
    mov.l @(16,r3),r4
    mov.l @(20,r3),r5
    mov.l @(24,r3),r6
    mov.l @(28,r3),r7
    mov.l @(32,r3),r8
    mov.l @(36,r3),r9
    mov.l @(40,r3),r10
    mov.l @(44,r3),r11
    mov.l @(48,r3),r12
    mov.l @(52,r3),r13
    mov.l @(56,r3),r14
    mov.l @(0,r3),r0
    mov.l @(4,r3),r1
    mov.l @(8,r3),r2
    mov.l @(12,r3),r3
    mov r15,r7
    add #116,r7
    mov.l @r7,r7
    jsr @r7
    mov.l @(32,r15),r7
L_closed_loop_adjustment_stock_return:
    add #112,r15
    mov.l r0,@-r15
    mov.l r1,@-r15
    mov.l r2,@-r15
    mov.l r3,@-r15
    mov.l r4,@-r15
    mov.l r5,@-r15
    mov.l r6,@-r15
    mov.l r7,@-r15
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    stc.l gbr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    sts.l pr,@-r15
    stc.l sr,@-r15
    mov r15,r1
    mov r15,r0
    add #80,r0
    mov.l @r0,r3
    mov r3,r2
    mov #20,r4
L_closed_loop_adjustment_copy_exit:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_closed_loop_adjustment_copy_exit
    mov r15,r0
    add #-32,r0
    mov.l r0,@r2
    add #4,r2
    mov.l L_closed_loop_adjustment_return_pointer,r0
    mov.l r0,@r2
    mov r3,r2
    add #124,r2
    add #124,r2
    add #124,r2
    add #4,r2
    mov r15,r1
    add #-96,r1
    add #-96,r1
    mov #48,r4
L_closed_loop_adjustment_frame_after:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_closed_loop_adjustment_frame_after
    add #88,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    nop
    .balign 4
L_closed_loop_adjustment_sr_mask: .long 0xfffffcfe
L_closed_loop_adjustment_frame_seed: .long 0xa3b4c5d6
L_closed_loop_adjustment_return_pointer: .long L_closed_loop_adjustment_stock_return

    .size _stock_invoke_closed_loop_adjustment,.-_stock_invoke_closed_loop_adjustment
