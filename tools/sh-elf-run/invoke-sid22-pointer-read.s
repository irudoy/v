! Natural entry/return and independent C-caller ABI observations.
    .macro RECORD_ABI pointer
    .irp reg,8,9,10,11,12,13,14
    mov.l r\reg,@\pointer
    add #4,\pointer
    .endr
    sts pr,r0
    mov.l r0,@\pointer
    add #4,\pointer
    stc gbr,r0
    mov.l r0,@\pointer
    add #4,\pointer
    sts mach,r0
    mov.l r0,@\pointer
    add #4,\pointer
    sts macl,r0
    mov.l r0,@\pointer
    add #4,\pointer
    mov.l r15,@\pointer
    .endm
    .text
    .balign 4
    .global _sid22_invoke
    .type _sid22_invoke,@function
_sid22_invoke:
    mov r4,r2
    add #112,r2
    add #112,r2
    RECORD_ABI r2
    .irp reg,8,9,10,11,12,13,14
    mov.l r\reg,@-r15
    .endr
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    stc.l sr,@-r15
    add #-88,r15
    mov r15,r2
    add #80,r2
    mov.l r4,@r2
    mov r4,r2
    add #80,r2
    mov.l r15,@r2
    mov r15,r1
    add #-64,r1
    mov.l L_frame_seed,r0
    mov #16,r2
    mov r4,r3
    add #96,r3
L_seed_frame:
    mov.l r0,@r1
    mov.l r0,@r3
    add #4,r1
    add #4,r3
    add #17,r0
    dt r2
    bf L_seed_frame
    .irp reg,8,9,10,11,12,13,14
    mov.l L_seed\reg,r\reg
    .endr
    mov.l L_seed_gbr,r0
    ldc r0,gbr
    mov.l L_seed_mach,r0
    lds r0,mach
    mov.l L_seed_macl,r0
    lds r0,macl
    stc sr,r0
    mov r4,r2
    add #92,r2
    mov.l r0,@r2
    mov.l L_entry,r0
    jsr @r0
    nop
L_stock_return:
    .irp reg,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14
    mov.l r\reg,@(4*\reg,r15)
    .endr
    stc sr,r0
    mov.l r0,@(60,r15)
    mov r15,r1
    add #64,r1
    stc gbr,r0
    mov.l r0,@r1
    add #4,r1
    sts mach,r0
    mov.l r0,@r1
    add #4,r1
    sts macl,r0
    mov.l r0,@r1
    add #4,r1
    sts pr,r0
    mov.l r0,@r1
    add #4,r1
    mov.l @r1,r3
    mov r15,r1
    mov r3,r2
    mov #20,r4
L_copy_exit:
    mov.l @r1+,r0
    mov.l r0,@r2
    add #4,r2
    dt r4
    bf L_copy_exit
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    mov.l L_continuation,r0
    mov.l r0,@r2
    mov r3,r2
    add #80,r2
    add #80,r2
    mov r15,r1
    add #-64,r1
    mov #16,r4
L_copy_frame:
    mov.l @r1+,r0
    mov.l r0,@r2
    add #4,r2
    dt r4
    bf L_copy_frame
    add #88,r15
    ldc.l @r15+,sr
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    .irp reg,14,13,12,11,10,9,8
    mov.l @r15+,r\reg
    .endr
    mov r3,r2
    add #112,r2
    add #112,r2
    add #48,r2
    RECORD_ABI r2
    rts
    mov #0,r0
    .balign 4
L_entry: .long 0x0003235c
L_continuation: .long L_stock_return
L_frame_seed: .long 0xa3b4c5d6
L_seed8: .long 0x18283848
L_seed9: .long 0x19293949
L_seed10: .long 0x1a2a3a4a
L_seed11: .long 0x1b2b3b4b
L_seed12: .long 0x1c2c3c4c
L_seed13: .long 0x1d2d3d4d
L_seed14: .long 0x1e2e3e4e
L_seed_gbr: .long 0x12344321
L_seed_mach: .long 0x10203040
L_seed_macl: .long 0x50607080

! Extracted into the simulator fixture; these sections are removed from the
! observer object before linking the driver. No publisher instruction changes.
    .macro RECORD_HELPER kind,result
    mov.l 9f,r2
    mov.l r4,@r2
    mov.l r5,@(4,r2)
    mov.l @(8,r2),r0
    add #1,r0
    mov.l r0,@(8,r2)
    mov #\kind,r0
    mov.l r0,@(12,r2)
    mov #\result,r0
    rts
    nop
    .if \kind == 2
    nop
    .endif
9:  .long 0x0100f000
    .endm
    .section .sid_transport_stub,"ax"
    .org 2
    RECORD_HELPER 1,0x5a
    .section .sid_error_stub,"ax"
    RECORD_HELPER 2,0x6b
