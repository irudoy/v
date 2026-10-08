! Post-feedback STFT publication and the complete caller-frame epilogue.
! The caller supplies the saved PR and seven saved register words.
    .section .text
    .org 0
    .global stock_stft_fragment
stock_stft_fragment:
    mov.w L_mode,r6
    mov.b @r6,r0
    tst #2,r0
    bt L_normal
    mov.w L_forced_base,r6
    mov #0x4b,r5
    shll8 r5
    mov.b @(1,r6),r0
    extu.b r0,r6
    shll8 r6
    extu.w r6,r2
    cmp/ge r5,r2
    bt L_lower_admitted
    bra L_shift_capped
    mov #0x4b,r6
L_lower_admitted:
    mov #0x7d,r5
    extu.w r6,r6
    shll8 r5
    cmp/gt r5,r6
    bf L_store_forced
    mov #0x7d,r6
L_shift_capped:
    shll8 r6
L_store_forced:
    mov.l L_output,r2
    mov r6,r0
    mov.w r6,@r2
    bra L_epilogue
    mov.w r0,@(2,r2)
L_normal:
    mov.l L_working,r6
    mov.l L_working,r5
    mov.w @r6,r2
    mov.l L_output,r6
    mov.w @(2,r5),r0
    mov.w r2,@r6
    mov.w r0,@(2,r6)
L_epilogue:
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    rts
    mov.l @r15+,r8
    .org 0x5ca5e-0x5ca08
L_mode: .word 0x99c4
    .org 0x5ca6c-0x5ca08
L_forced_base: .word 0x9924
    .org 0x5ca84-0x5ca08
L_working: .long 0xffff40ac
    .org 0x5ca88-0x5ca08
L_output: .long 0xffff22dc
