! JK08A MAF lookup slice, implicit word wrapper, and unchanged stock callees.
! Origin 0x86f8 preserves every PC-relative pool and the second-bank delay slot.
    .text
    .balign 4
    .org 0x86f9 - 0x86f8
correction_mode:
    .byte 0xdc
    .org 0x8782 - 0x86f8
correction_factor:
    .byte 0
    .org 0x8b3f - 0x86f8
correction_selection:
    .byte 0x18
    .org 0x141f4 - 0x86f8
bank_two_curve:
    .word 222,222,222,222,222,222,222,231
    .word 253,290,341,408,491,592,711,850
    .word 1009,1189,1391,1618,1869,2146,2451,2784
    .word 3148,3544,3972,4436,4936,5473,6051,6670
    .word 7332,8039,8793,9597,10451,11358,12320,13339
    .word 14418,15558,16762,18032,19371,20781,22265,23824
    .word 25462,27182,28985,30875,32854,34925,37091,39356
    .word 41721,44190,46766,49452,52252,55168,58203,61362
bank_one_curve:
    .word 211,211,211,211,211,211,211,224
    .word 249,288,341,410,494,595,715,853
    .word 1011,1191,1394,1620,1871,2148,2454,2788
    .word 3153,3550,3981,4446,4949,5490,6072,6696
    .word 7363,8076,8837,9647,10509,11424,12396,13424
    .word 14513,15664,16879,18161,19512,20935,22431,24004
    .word 25655,27388,29206,31109,33102,35188,37368,39646
    .word 42025,44507,47095,49794,52604,55531,58576,61744
    .org 0x26410 - 0x86f8
implicit_word_curve:
    mov.w last_coordinate,r0
    extu.w r5,r5
    cmp/hs r0,r5
    bt last_cell
    mov.l curve_body,r6
    jmp @r6
    mov #0,r3
last_cell:
    add #0x7e,r4
    rts
    mov.w @r4,r0
last_coordinate:
    .word 0x3f00
    .word 0x0009
curve_body:
    .long interpolation_body
    .org 0x26740 - 0x86f8
linear_interpolation:
    cmp/hs r0,r2
    bt increasing
    mov.l r0,@-r15
    sub r2,r0
    sts macl,r1
    mul.l r3,r0
    sts macl,r0
    lds r1,macl
    swap.w r0,r0
    mov.l @r15+,r2
    extu.w r0,r0
    sub r0,r2
    rts
    mov r2,r0
increasing:
    sub r0,r2
    sts macl,r1
    mul.l r3,r2
    sts macl,r2
    lds r1,macl
    swap.w r2,r2
    extu.w r2,r2
    rts
    add r2,r0
    .org 0x26a74 - 0x86f8
interpolation_body:
    .rept 8
    shlr r5
    rotcr r3
    .endr
    swap.w r3,r3
    shlr8 r0
    tst r0,r0
    bt byte_cells
    shll r5
    add r5,r4
    mov.w @r4,r1
    mov.w @(2,r4),r0
    extu.w r0,r2
    bra interpolate
    extu.w r1,r0
byte_cells:
    add r5,r4
    mov.b @r4,r1
    mov.b @(1,r4),r0
    extu.b r0,r2
    extu.b r1,r0
interpolate:
    mov.l linear_entry,r6
    jmp @r6
    nop
    .balign 4
linear_entry:
    .long linear_interpolation
    .org 0x3a922 - 0x86f8
maf_lookup_slice:
    mov #0x2c,r0
    mov.l bank_one_pointer,r4
    mov.w @(r0,r14),r2
    mov.l wrapper_pointer,r7
    extu.w r2,r2
    shll2 r2
    shll2 r2
    jsr @r7
    extu.w r2,r5
    mov.l output_window,r6
    mov.l bank_two_pointer,r4
    mov.w r0,@(0xc,r6)
    mov #0x2e,r0
    mov.w @(r0,r14),r2
    mov.l wrapper_pointer,r7
    extu.w r2,r5
    shll2 r5
    shll2 r5
    jsr @r7
    extu.w r5,r5
    mov.l output_window,r6
    bsr correction_publisher
    mov.w r0,@(0xe,r6)
    .org 0x3ab60 - 0x86f8
bank_one_pointer:
    .long bank_one_curve
wrapper_pointer:
    .long implicit_word_curve
output_window:
    .long 0xffff1048
bank_two_pointer:
    .long bank_two_curve
    .org 0x3b320 - 0x86f8
correction_publisher:
    sts.l macl,@-r15
    stc.l gbr,@-r15
    mov.l correction_window,r0
    ldc r0,gbr
    mov.l selection_pointer,r6
    mov.l mode_pointer,r5
    mov.b @r6,r0
    and #1,r0
    mov r0,r2
    mov.b @r5,r0
    tst #0x20,r0
    bt ordinary_selection
    tst r2,r2
    bf correction_return
    mov.b @(0x13,gbr),r0
    mov #5,r5
    extu.b r0,r6
    cmp/ge r5,r6
    bf upper_interval
    mov #0x7b,r5
    cmp/ge r5,r6
    bt upper_interval
    mov.l factor_pointer,r5
    exts.w r6,r2
    mov.b @r5,r6
    add #-0x7b,r2
    extu.b r6,r6
    bra divide_product
    mul.l r2,r6
upper_interval:
    mov #-0x7b,r5
    extu.b r5,r5
    cmp/ge r5,r6
    bf zero_correction
    mov #-5,r5
    extu.b r5,r5
    cmp/ge r5,r6
    bt zero_correction
    mov.l factor_pointer,r5
    mov.b @r5,r2
    mov.w upper_bias,r5
    bra upper_product
    extu.b r2,r2
upper_bias:
    .word 0xff7b
upper_product:
    add r5,r6
    bra divide_product
    mul.l r6,r2
    .org 0x3b3ac - 0x86f8
correction_window:
    .long 0xffff1e60
selection_pointer:
    .long correction_selection
mode_pointer:
    .long correction_mode
factor_pointer:
    .long correction_factor
ordinary_selection:
    tst r2,r2
    bt zero_correction
    mov.l alternate_factor,r5
    mov.b @r5,r2
    mov.l alternate_window,r5
    extu.b r2,r2
    mov.b @(8,r5),r0
    mul.l r0,r2
divide_product:
    sts macl,r0
    .rept 4
    shar r0
    .endr
    bra publish_correction
    shar r0
zero_correction:
    mov #0,r0
publish_correction:
    mov.l correction_output,r5
    mov.w r0,@(0xe,r5)
correction_return:
    ldc.l @r15+,gbr
    rts
    lds.l @r15+,macl
    .org 0x3b3e8 - 0x86f8
alternate_factor:
    .long correction_factor
alternate_window:
    .long 0xffff56b2
correction_output:
    .long 0xffff1e1c
