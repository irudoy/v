! Exact-address stock reconstruction of the JK08A BFS rate-stage fragment.
! The diagnostic predicate and signed shift helper retain their natural returns.
    .section .text
    .balign 4
    .org 0x00008319 - 0x00008318
P_00008319:
    .byte 202
P_0000831a:
    .byte 200
    .org 0x0000865a - 0x00008318
P_0000865a:
    .byte 160
    .org 0x00008d92 - 0x00008318
P_00008d92:
    .byte 0x7a
    .org 0x000224fa - 0x00008318
L_000224fa:
    shar r0
    shar r0
    shar r0
    shar r0
    shar r0
    rts
    shar r0
    .org 0x000259e4 - 0x00008318
L_000259e4:
    mov.l P_00025b98,r1
    exts.w r4,r0
    cmp/eq #-1,r0
    bt L_00025a0c
    mov r0,r7
    shll r7
    mov r1,r2
    add r0,r7
    add r7,r2
    mov.b @(2,r2),r0
    tst #0x40,r0
    bf/s L_00025a0e
    mov #1,r5
    mov r1,r2
    add r7,r2
    mov.b @(2,r2),r0
    tst #0x20,r0
    bf L_00025a0e
    bra L_00025a0e
    mov #0,r5
L_00025a0c:
    mov #0,r5
L_00025a0e:
    rts
    mov r5,r0
    .org 0x00025b98 - 0x00008318
P_00025b98:
    .long 0xffff5718
    .org 0x0003b908 - 0x00008318
L_0003b908:
    mov #0x48,r0
    mov.w @(r0,r8),r6
    extu.w r6,r2
    mul.l r2,r5
    mov #0x40,r6
    shll8 r6
    sts macl,r2
    shll16 r6
    cmp/hs r6,r2
    bt L_0003b922
    shll2 r2
    bra L_0003b924
    mov r2,r6
L_0003b922:
    mov #-1,r6
L_0003b924:
    mov.w @(0x144,gbr),r0
    extu.w r0,r9
    mov.w @(0x1a,gbr),r0
    extu.w r0,r7
    mov r14,r0
    mul.l r9,r7
    tst #0x10,r0
    bf/s L_0003b970
    sts macl,r4
    not r4,r2
    cmp/hs r2,r6
    bt L_0003b94a
    add r4,r6
    shlr8 r6
    shlr2 r6
    shlr2 r6
    shlr2 r6
    bra L_0003b94c
    shlr r6
L_0003b94a:
    mov #-1,r6
L_0003b94c:
    cmp/hi r13,r6
    bf/s L_0003b954
    mov r6,r2
    mov r13,r2
L_0003b954:
    mov r2,r6
    mov r5,r2
    shll2 r2
    cmp/hi r13,r2
    bf L_0003b960
    mov r13,r2
L_0003b960:
    cmp/hs r2,r6
    bt L_0003b9da
    mov.w @(2,gbr),r0
    extu.w r0,r2
    cmp/eq r2,r6
    bf L_0003b9da
    bra L_0003b9da
    add #1,r6
L_0003b970:
    cmp/hs r6,r4
    bf L_0003b9d8
    sub r6,r4
    shlr8 r4
    shlr2 r4
    shlr2 r4
    shlr2 r4
    shlr r4
    cmp/hi r13,r4
    bf/s L_0003b988
    mov r4,r2
    mov r13,r2
L_0003b988:
    bra L_0003b9da
    mov r2,r6
    .org 0x0003b9d0 - 0x00008318
P_0003b9d0:
    .long 0xffff24ac
P_0003b9d4:
    .long 0xffff1048
L_0003b9d8:
    mov #0,r6
L_0003b9da:
    mov.l P_0003bbc4,r3
    mov r6,r0
    mov.w r0,@(2,gbr)
    mov #0x5c,r0
    mov.b @(r0,r8),r4
    mov.b @r3,r2
    extu.b r4,r4
    extu.b r2,r2
    cmp/ge r2,r4
    bf L_0003b9fc
    shll2 r5
    cmp/hs r5,r7
    bf L_0003b9fc
    mov r14,r0
    mov.l P_0003bbc8,r2
    bra L_0003ba0c
    or #0x80,r0
L_0003b9fc:
    mov.l P_0003bbcc,r6
    mov.b @r6,r2
    extu.b r2,r2
    cmp/ge r2,r4
    bt L_0003ba10
    mov r14,r0
    and #0x7f,r0
    mov.l P_0003bbc8,r2
L_0003ba0c:
    mov r0,r14
    mov.b r0,@(5,r2)
L_0003ba10:
    mov.l P_0003bbd0,r6
    mov.b @(1,r6),r0
    tst #0x80,r0
    bt L_0003ba1e
    mov #4,r4
    bra L_0003ba36
    mov r4,r0
L_0003ba1e:
    mov.b @(0x34,gbr),r0
    extu.b r0,r6
    exts.w r6,r2
    add #-1,r2
    cmp/pz r2
    bt L_0003ba2e
    bra L_0003ba32
    mov #0,r6
L_0003ba2e:
    exts.w r6,r6
    add #-1,r6
L_0003ba32:
    mov r6,r4
    mov r6,r0
L_0003ba36:
    mov.l P_0003bbd4,r6
    mov.b r0,@(0x34,gbr)
    mov.b @(4,r6),r0
    tst #0x40,r0
    bt L_0003ba44
    bra L_0003ba5a
    mov #4,r0
L_0003ba44:
    mov.b @(0x5b,gbr),r0
    extu.b r0,r6
    exts.w r6,r2
    add #-1,r2
    cmp/pz r2
    bt L_0003ba54
    bra L_0003ba58
    mov #0,r2
L_0003ba54:
    exts.w r6,r2
    add #-1,r2
L_0003ba58:
    mov r2,r0
L_0003ba5a:
    mov.l P_0003bbd8,r13
    mov.b r0,@(0x5b,gbr)
    mov.b @r13,r0
    tst #8,r0
    bt L_0003bab8
    mov.l P_0003bbdc,r2
    jsr @r2
    mov #-1,r4
    tst r0,r0
    bt L_0003ba74
    mov #4,r7
    bra L_0003ba8c
    mov r7,r0
L_0003ba74:
    mov.b @(0x60,gbr),r0
    extu.b r0,r6
    exts.w r6,r2
    add #-1,r2
    cmp/pz r2
    bt L_0003ba84
    bra L_0003ba88
    mov #0,r2
L_0003ba84:
    exts.w r6,r2
    add #-1,r2
L_0003ba88:
    mov r2,r7
    mov r2,r0
L_0003ba8c:
    mov.b r0,@(0x60,gbr)
    mov.b @(0x34,gbr),r0
    mov.l P_0003bbd0,r5
    mov r0,r4
    tst r0,r0
    mov.b @(6,r5),r0
    bf/s L_0003bab0
    mov r0,r5
    mov.b @(0x5b,gbr),r0
    tst r0,r0
    bf L_0003bab0
    extu.b r7,r7
    tst r7,r7
    bf L_0003bab0
    mov r5,r0
    mov.l P_0003bbd0,r2
    bra L_0003bab6
    and #0x7f,r0
L_0003bab0:
    mov r5,r0
    or #0x80,r0
    mov.l P_0003bbd0,r2
L_0003bab6:
    mov.b r0,@(6,r2)
L_0003bab8:
    mov.b @(2,r12),r0
    and #1,r0
    mov r0,r2
    mov #0x10,r0
    tst r2,r2
    bt/s L_0003bb34
    mov.b r2,@(r0,r15)
    mov.l P_0003bbc8,r5
    mov #0x11,r0
    mov.b @(r0,r5),r0
    tst #4,r0
    bt L_0003bb34
    mov.b @(5,r5),r0
    tst #0x80,r0
    bf L_0003bb34
    extu.b r4,r4
    tst r4,r4
    bf L_0003bb34
    mov.b @(0x5b,gbr),r0
    tst r0,r0
    bf L_0003bb34
    mov.w @(2,gbr),r0
    mov.l P_0003bbe0,r2
    extu.w r0,r6
    mov.w @(0x1a,gbr),r0
    mov.b @r2,r7
    extu.w r0,r5
    mov.l P_0003bbe4,r4
    extu.b r7,r7
    sub r5,r6
    mul.l r6,r7
    jsr @r4
    sts macl,r0
    mov #-0x80,r5
    shll8 r5
    cmp/ge r5,r0
    bf L_0003bb1c
    mov.w @(2,gbr),r0
    mov.l P_0003bbe0,r3
    extu.w r0,r6
    mov.w @(0x1a,gbr),r0
    mov.b @r3,r7
    extu.w r0,r5
    mov.l P_0003bbe4,r4
    extu.b r7,r7
    sub r5,r6
    mul.l r6,r7
    jsr @r4
    sts macl,r0
    mov r0,r5
L_0003bb1c:
    mov.w P_0003bb22,r6
    bra L_0003bb24
    mov r5,r14
P_0003bb22:
    .word 0x7fff
L_0003bb24:
    cmp/gt r6,r5
    bt L_0003bb2a
    mov r14,r6
L_0003bb2a:
    mov.l P_0003bbe8,r3
    mov r6,r0
    mov.w r0,@(0x18,r3)
    bra L_0003bb3c
    mov r6,r7
L_0003bb34:
    mov.l P_0003bbe8,r3
    mov #0,r7
    mov r7,r0
    mov.w r0,@(0x18,r3)
L_0003bb3c:
    mov.b @r13,r0
    and #0x10,r0
    tst r0,r0
    bt/s L_0003bb86
    mov r0,r5
    mov #0x10,r0
    mov.b @(r0,r15),r2
    tst r2,r2
    bt L_0003bb80
    mov.l P_0003bbc8,r6
    mov #0x11,r0
    mov.b @(r0,r6),r0
    tst #4,r0
    bf L_0003bb80
    mov.l P_0003bbc8,r6
    mov.b @(5,r6),r0
    tst #0x80,r0
    bt L_0003bb80
    mov.b @(0xf5,gbr),r0
    mov #1,r6
    shll8 r6
    extu.b r0,r4
    mov.w @(2,gbr),r0
    sub r4,r6
    extu.w r0,r2
    mov.w @(0x18,gbr),r0
    mul.l r4,r2
    extu.w r0,r4
    sts macl,r0
    mul.l r6,r4
    sts macl,r6
    add r6,r0
    bra L_0003bb84
    shlr8 r0
L_0003bb80:
    mov.w @(2,gbr),r0
    mov.l r0,@(0x14,r15)
L_0003bb84:
    mov.w r0,@(0,gbr)
L_0003bb86:
    .org 0x0003bbc4 - 0x00008318
P_0003bbc4:
    .long 0x00008319
P_0003bbc8:
    .long 0xffff24ac
P_0003bbcc:
    .long 0x0000831a
P_0003bbd0:
    .long 0xffff2448
P_0003bbd4:
    .long 0xffff424c
P_0003bbd8:
    .long 0x00008d92
P_0003bbdc:
    .long 0x000259e4
P_0003bbe0:
    .long 0x0000865a
P_0003bbe4:
    .long 0x000224fa
P_0003bbe8:
    .long 0xffff1048
