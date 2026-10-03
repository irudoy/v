! JK08A eight-point byte entry, shared interpolation body, and linear kernel.
! All branches, pools, and natural returns retain their stock addresses.
    .text
    .balign 4
implicit_byte_curve:
    mov.w last_coordinate,r0
    extu.b r5,r5
    cmp/hs r0,r5
    bt last_cell
    mov.l curve_body,r6
    jmp @r6
    mov #0,r3
last_cell:
    rts
    mov.b @(7,r4),r0
last_coordinate:
    .word 224
curve_body:
    .long interpolation_body
    .org 0x3d0
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
    .org 0x710
interpolation_body:
    .rept 5
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
