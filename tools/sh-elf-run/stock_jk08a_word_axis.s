! JK08A word axis search with its unsigned fraction divider.
! Every instruction and loaded pool word stays at its original ROM address.
    .text
    .balign 4
word_axis_search:
    mov r4,r3
word_scan:
    mov.w @(r0,r4),r1
    extu.w r1,r1
    cmp/eq r1,r5
    bt word_exact
    cmp/hi r1,r5
    bf word_previous
    cmp/eq r4,r3
    bt word_exact
    sub r1,r5
    shll16 r5
    add r4,r0
    mov.w @r0,r1
    mov.w @(2,r0),r0
    extu.w r1,r1
    extu.w r0,r0
    sts.l pr,@-r15
    mov.l word_divider,r2
    sub r1,r0
    jsr @r2
    mov r5,r1
    lds.l @r15+,pr
    rts
    mov r0,r5
word_previous:
    add #-2,r4
    cmp/pz r4
    bt word_scan
    mov #0,r4
word_exact:
    rts
    mov #0,r5
word_divider:
    .long fraction_divider
    .org 0x2f4
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
