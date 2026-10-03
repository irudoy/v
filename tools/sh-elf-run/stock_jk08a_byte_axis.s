! JK08A byte axis search with its unsigned fraction divider.
! Every instruction and loaded pool word stays at its original ROM address.
    .text
    .balign 4
byte_axis_search:
    mov r4,r3
byte_scan:
    mov.b @(r0,r4),r1
    extu.b r1,r1
    shll2 r1
    cmp/eq r5,r1
    bt byte_exact
    cmp/hi r5,r1
    bt byte_previous
    cmp/eq r4,r3
    bt byte_exact
    sub r1,r5
    shll16 r5
    mov r4,r3
    add r0,r3
    mov.b @r3,r1
    mov.b @(1,r3),r0
    extu.b r1,r1
    extu.b r0,r0
    sts.l pr,@-r15
    mov.l byte_divider,r2
    sub r1,r0
    shll2 r0
    jsr @r2
    mov r5,r1
    lds.l @r15+,pr
    rts
    mov r0,r5
byte_previous:
    add #-1,r4
    cmp/pz r4
    bt byte_scan
    mov #0,r4
byte_exact:
    rts
    mov #0,r5
    .balign 4
byte_divider:
    .long fraction_divider
    .org 0x2b4
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
