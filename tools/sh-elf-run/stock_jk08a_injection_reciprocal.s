! Real reciprocal splitter at its original address.
    .text
    .balign 4
splitter:
    sts.l macl,@-r15
    mov.w reciprocal,r3
    mov r6,r7
    mul.l r4,r3
    sts macl,r2
    shlr16 r2
    mov r2,r6
    shll2 r6
    add r2,r6
    shll r6
    tst r6,r6
    bt/s remainder_store
    mov.w r2,@r5
    sub r6,r4
remainder_store:
    mov.b r4,@r7
    rts
    lds.l @r15+,macl
    .org 0x28ea0 - 0x28e7c
reciprocal:
    .word 0x199a
