! JK08A direct byte-axis search and its stock unsigned fraction divider.
! Point bytes are compared without the multiplier of the word-input wrapper.
    .text
    .balign 4
direct_byte_axis:
    mov r4,r3
direct_scan:
    mov.b @(r0,r4),r1
    extu.b r1,r1
    cmp/eq r1,r5
    bt direct_exact
    cmp/hi r1,r5
    bf direct_previous
    cmp/eq r4,r3
    bt direct_exact
    sub r1,r5
    shll16 r5
    add r4,r0
    mov.b @r0,r1
    mov.b @(1,r0),r0
    extu.b r1,r1
    extu.b r0,r0
    sts.l pr,@-r15
    mov.l direct_divider,r2
    sub r1,r0
    jsr @r2
    mov r5,r1
    lds.l @r15+,pr
    rts
    mov r0,r5
direct_previous:
    add #-1,r4
    cmp/pz r4
    bt direct_scan
    mov #0,r4
direct_exact:
    rts
    mov #0,r5
    .balign 4
direct_divider:
    .long fraction_divider
    .org 0x334
fraction_divider:
    tst r0,r0
    bt zero_divisor
    mov.l r2,@-r15
    mov #0,r2
    div0u
    rotcl r1
    .rept 32
    div1 r0,r2
    rotcl r1
    .endr
    mov.l @r15+,r2
    rts
    mov r1,r0
zero_divisor:
    rts
    mov #0,r0
