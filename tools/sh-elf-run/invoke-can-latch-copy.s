! The capture area is above the stock SP; the helper's lower frame is intact.
    .macro CAPTURE_COPY
    .irp reg,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14
    mov.l r\reg,@(4*\reg,r15)
    .endr
    stc sr,r0
    mov.l r0,@(60,r15)
    mov r15,r1
    add #64,r1
    sts pr,r0
    mov.l r0,@r1
    add #4,r1
    stc gbr,r0
    mov.l r0,@r1
    add #4,r1
    sts mach,r0
    mov.l r0,@r1
    add #4,r1
    sts macl,r0
    mov.l r0,@r1
    add #4,r1
    mov.l @r1,r0
    jmp @r0
    nop
    .endm

    .macro SAVE_ABI
    .irp reg,8,9,10,11,12,13,14
    mov.l r\reg,@-r15
    .endr
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    stc.l sr,@-r15
    .endm

    .macro RESTORE_ABI
    ldc.l @r15+,sr
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    .irp reg,14,13,12,11,10,9,8
    mov.l @r15+,r\reg
    .endr
    .endm

    .text
    .balign 4
    .global _can_copy_invoke
    .type _can_copy_invoke,@function
_can_copy_invoke:
    SAVE_ABI
    add #-72,r15
    add #-72,r15
    mov r15,r0
    add #84,r0
    mov.l r5,@r0
    add #4,r0
    mov.l r4,@r0
    mov r15,r1
    add #72,r1
    add #72,r1
    mov r5,r2
    add #112,r2
    add #112,r2
    mov #12,r3
L_copy_abi_before:
    mov.l @r1+,r0
    mov.l r0,@r2
    add #4,r2
    dt r3
    bf L_copy_abi_before
    mov r15,r1
    add #-64,r1
    mov.l L_frame_seed,r0
    mov #16,r2
L_copy_seed_frame:
    mov.l r0,@r1
    add #4,r1
    add #17,r0
    dt r2
    bf L_copy_seed_frame
    mov r15,r1
    add #-64,r1
    mov r5,r2
    add #96,r2
    mov #16,r3
L_copy_frame_before:
    mov.l @r1+,r0
    mov.l r0,@r2
    add #4,r2
    dt r3
    bf L_copy_frame_before
    mov r5,r2
    add #84,r2
    mov.l r15,@r2
    add #8,r2
    mov.l L_helper_return,r0
    mov.l r0,@r2
    mov r15,r2
    add #80,r2
    mov.l L_capture_return,r0
    mov.l r0,@r2
    mov r4,r3
    mov r3,r2
    add #76,r2
    mov.l @r2,r0
    tst r0,r0
    bt L_copy_direct
    mov.l L_caller_entry,r0
    bra L_copy_prepare
    nop
L_copy_direct:
    mov.l L_helper_call,r0
L_copy_prepare:
    lds r0,pr
    mov.l @(60,r3),r0
    ldc r0,gbr
    mov r3,r2
    add #64,r2
    mov.l @r2+,r0
    lds r0,mach
    mov.l @r2+,r0
    lds r0,macl
    mov.l @r2,r1
    stc sr,r0
    mov.l L_clear_mqt,r2
    and r2,r0
    or r1,r0
    ldc r0,sr
    mov.l r0,@(60,r5)
    .irp reg,4,5,6,7,8,9,10,11,12,13,14
    mov.l @(4*\reg,r3),r\reg
    .endr
    mov.l @r3,r0
    mov.l @(4,r3),r1
    mov.l @(8,r3),r2
    mov.l @(12,r3),r3
    rts
    nop
L_copy_helper_call:
    jsr @r11
    nop
L_copy_helper_return:
    CAPTURE_COPY
L_copy_capture_return:
    mov r15,r0
    add #84,r0
    mov.l @r0,r4
    mov r15,r1
    mov r4,r2
    mov #15,r3
L_copy_gprs:
    mov.l @r1+,r0
    mov.l r0,@r2
    add #4,r2
    dt r3
    bf L_copy_gprs
    add #4,r2
    mov #5,r3
L_copy_controls:
    mov.l @r1+,r0
    mov.l r0,@r2
    add #4,r2
    dt r3
    bf L_copy_controls
    mov r4,r2
    add #88,r2
    mov.l r15,@r2
    mov r15,r1
    add #-64,r1
    mov r4,r2
    add #80,r2
    add #80,r2
    mov #16,r3
L_copy_frame_after:
    mov.l @r1+,r0
    mov.l r0,@r2
    add #4,r2
    dt r3
    bf L_copy_frame_after
    add #72,r15
    add #72,r15
    RESTORE_ABI
    SAVE_ABI
    mov r15,r1
    mov r4,r2
    add #120,r2
    add #120,r2
    add #32,r2
    mov #12,r3
L_copy_abi_after:
    mov.l @r1+,r0
    mov.l r0,@r2
    add #4,r2
    dt r3
    bf L_copy_abi_after
    RESTORE_ABI
    rts
    nop
    .balign 4
L_frame_seed: .long 0xa3b4c5d6
L_clear_mqt: .long 0xfffffcfe
L_caller_entry: .long 0x00021094
L_helper_call: .long L_copy_helper_call
L_helper_return: .long L_copy_helper_return
L_capture_return: .long L_copy_capture_return
    .size _can_copy_invoke,.-_can_copy_invoke

! Position-independent capture copied to the declared ROM boundary.
    .section .copy_boundary,"ax"
    CAPTURE_COPY
