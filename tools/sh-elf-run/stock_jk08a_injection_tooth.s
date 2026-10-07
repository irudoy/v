! Bounded angle-byte splitting and real phase normalization.
    .text
    .balign 4
    .org 0x28dc8 - 0x28dc8
L_00028dc8:
    mov.l L_00029020,r2
    .org 0x28dca - 0x28dc8
L_00028dca:
    mov r5,r7
    .org 0x28dcc - 0x28dc8
L_00028dcc:
    mov.w L_00028e9e,r0
    .org 0x28dce - 0x28dc8
L_00028dce:
    mov.b @(r0,r2),r5
    .org 0x28dd0 - 0x28dc8
L_00028dd0:
    mov.w @r4,r2
    .org 0x28dd2 - 0x28dc8
L_00028dd2:
    extu.b r5,r0
    .org 0x28dd4 - 0x28dc8
L_00028dd4:
    cmp/eq #0x4,r0
    .org 0x28dd6 - 0x28dc8
L_00028dd6:
    bf/s L_00028df4
    .org 0x28dd8 - 0x28dc8
L_00028dd8:
    extu.w r2,r2
    .org 0x28dda - 0x28dc8
L_00028dda:
    mov #0x6,r5
    .org 0x28ddc - 0x28dc8
L_00028ddc:
    cmp/ge r5,r2
    .org 0x28dde - 0x28dc8
L_00028dde:
    bf L_00028de6
    .org 0x28de0 - 0x28dc8
L_00028de0:
    mov #0xf,r5
    .org 0x28de2 - 0x28dc8
L_00028de2:
    cmp/gt r5,r2
    .org 0x28de4 - 0x28dc8
L_00028de4:
    bf L_00028e4c
    .org 0x28de6 - 0x28dc8
L_00028de6:
    mov r2,r0
    .org 0x28de8 - 0x28dc8
L_00028de8:
    cmp/eq #0x5,r0
    .org 0x28dea - 0x28dc8
L_00028dea:
    bt L_00028e6a
    .org 0x28dec - 0x28dc8
L_00028dec:
    cmp/eq #0x4,r0
    .org 0x28dee - 0x28dc8
L_00028dee:
    bt L_00028e5e
    .org 0x28df0 - 0x28dc8
L_00028df0:
    bra L_00028e78
    .org 0x28df2 - 0x28dc8
L_00028df2:
    nop
    .org 0x28df4 - 0x28dc8
L_00028df4:
    cmp/eq #0x9,r0
    .org 0x28df6 - 0x28dc8
L_00028df6:
    bf L_00028e18
    .org 0x28df8 - 0x28dc8
L_00028df8:
    mov r2,r0
    .org 0x28dfa - 0x28dc8
L_00028dfa:
    cmp/eq #0x9,r0
    .org 0x28dfc - 0x28dc8
L_00028dfc:
    bf L_00028e0c
    .org 0x28dfe - 0x28dc8
L_00028dfe:
    add #-0x1,r2
    .org 0x28e00 - 0x28dc8
L_00028e00:
    extu.w r2,r2
    .org 0x28e02 - 0x28dc8
L_00028e02:
    mov.w r2,@r4
    .org 0x28e04 - 0x28dc8
L_00028e04:
    mov.b @r7,r2
    .org 0x28e06 - 0x28dc8
L_00028e06:
    add #0xa,r2
    .org 0x28e08 - 0x28dc8
L_00028e08:
    mov.b r2,@r7
    .org 0x28e0a - 0x28dc8
L_00028e0a:
    mov.w @r4,r2
    .org 0x28e0c - 0x28dc8
L_00028e0c:
    extu.w r2,r2
    .org 0x28e0e - 0x28dc8
L_00028e0e:
    mov #0xa,r5
    .org 0x28e10 - 0x28dc8
L_00028e10:
    cmp/ge r5,r2
    .org 0x28e12 - 0x28dc8
L_00028e12:
    bt L_00028e6a
    .org 0x28e14 - 0x28dc8
L_00028e14:
    bra L_00028e78
    .org 0x28e16 - 0x28dc8
L_00028e16:
    nop
    .org 0x28e18 - 0x28dc8
L_00028e18:
    mov #0xf,r5
    .org 0x28e1a - 0x28dc8
L_00028e1a:
    cmp/ge r5,r2
    .org 0x28e1c - 0x28dc8
L_00028e1c:
    bf L_00028e2a
    .org 0x28e1e - 0x28dc8
L_00028e1e:
    mov #0x18,r5
    .org 0x28e20 - 0x28dc8
L_00028e20:
    cmp/gt r5,r2
    .org 0x28e22 - 0x28dc8
L_00028e22:
    bt L_00028e2a
    .org 0x28e24 - 0x28dc8
L_00028e24:
    add #-0x4,r2
    .org 0x28e26 - 0x28dc8
L_00028e26:
    bra L_00028e50
    .org 0x28e28 - 0x28dc8
L_00028e28:
    extu.w r2,r2
    .org 0x28e2a - 0x28dc8
L_00028e2a:
    mov r2,r0
    .org 0x28e2c - 0x28dc8
L_00028e2c:
    cmp/eq #0xe,r0
    .org 0x28e2e - 0x28dc8
L_00028e2e:
    bf L_00028e36
    .org 0x28e30 - 0x28dc8
L_00028e30:
    add #-0x4,r2
    .org 0x28e32 - 0x28dc8
L_00028e32:
    bra L_00028e6e
    .org 0x28e34 - 0x28dc8
L_00028e34:
    extu.w r2,r2
    .org 0x28e36 - 0x28dc8
L_00028e36:
    cmp/eq #0xd,r0
    .org 0x28e38 - 0x28dc8
L_00028e38:
    bf L_00028e40
    .org 0x28e3a - 0x28dc8
L_00028e3a:
    add #-0x3,r2
    .org 0x28e3c - 0x28dc8
L_00028e3c:
    bra L_00028e62
    .org 0x28e3e - 0x28dc8
L_00028e3e:
    extu.w r2,r2
    .org 0x28e40 - 0x28dc8
L_00028e40:
    mov #0x3,r5
    .org 0x28e42 - 0x28dc8
L_00028e42:
    cmp/ge r5,r2
    .org 0x28e44 - 0x28dc8
L_00028e44:
    bf L_00028e54
    .org 0x28e46 - 0x28dc8
L_00028e46:
    mov #0xc,r5
    .org 0x28e48 - 0x28dc8
L_00028e48:
    cmp/gt r5,r2
    .org 0x28e4a - 0x28dc8
L_00028e4a:
    bt L_00028e54
    .org 0x28e4c - 0x28dc8
L_00028e4c:
    add #-0x2,r2
    .org 0x28e4e - 0x28dc8
L_00028e4e:
    extu.w r2,r2
    .org 0x28e50 - 0x28dc8
L_00028e50:
    rts
    .org 0x28e52 - 0x28dc8
L_00028e52:
    mov.w r2,@r4
    .org 0x28e54 - 0x28dc8
L_00028e54:
    mov r2,r0
    .org 0x28e56 - 0x28dc8
L_00028e56:
    cmp/eq #0x2,r0
    .org 0x28e58 - 0x28dc8
L_00028e58:
    bt L_00028e6a
    .org 0x28e5a - 0x28dc8
L_00028e5a:
    cmp/eq #0x1,r0
    .org 0x28e5c - 0x28dc8
L_00028e5c:
    bf L_00028e78
    .org 0x28e5e - 0x28dc8
L_00028e5e:
    add #-0x1,r2
    .org 0x28e60 - 0x28dc8
L_00028e60:
    extu.w r2,r2
    .org 0x28e62 - 0x28dc8
L_00028e62:
    mov.w r2,@r4
    .org 0x28e64 - 0x28dc8
L_00028e64:
    mov.b @r7,r2
    .org 0x28e66 - 0x28dc8
L_00028e66:
    bra L_00028e74
    .org 0x28e68 - 0x28dc8
L_00028e68:
    add #0xa,r2
    .org 0x28e6a - 0x28dc8
L_00028e6a:
    add #-0x2,r2
    .org 0x28e6c - 0x28dc8
L_00028e6c:
    extu.w r2,r2
    .org 0x28e6e - 0x28dc8
L_00028e6e:
    mov.w r2,@r4
    .org 0x28e70 - 0x28dc8
L_00028e70:
    mov.b @r7,r2
    .org 0x28e72 - 0x28dc8
L_00028e72:
    add #0x14,r2
    .org 0x28e74 - 0x28dc8
L_00028e74:
    rts
    .org 0x28e76 - 0x28dc8
L_00028e76:
    mov.b r2,@r7
    .org 0x28e78 - 0x28dc8
L_00028e78:
    rts
    .org 0x28e7a - 0x28dc8
L_00028e7a:
    nop
    .org 0x28e7c - 0x28dc8
L_00028e7c:
    sts.l macl,@-r15
    .org 0x28e7e - 0x28dc8
L_00028e7e:
    mov.w L_00028ea0,r3
    .org 0x28e80 - 0x28dc8
L_00028e80:
    mov r6,r7
    .org 0x28e82 - 0x28dc8
L_00028e82:
    mul.l r4,r3
    .org 0x28e84 - 0x28dc8
L_00028e84:
    sts macl,r2
    .org 0x28e86 - 0x28dc8
L_00028e86:
    shlr16 r2
    .org 0x28e88 - 0x28dc8
L_00028e88:
    mov r2,r6
    .org 0x28e8a - 0x28dc8
L_00028e8a:
    shll2 r6
    .org 0x28e8c - 0x28dc8
L_00028e8c:
    add r2,r6
    .org 0x28e8e - 0x28dc8
L_00028e8e:
    shll r6
    .org 0x28e90 - 0x28dc8
L_00028e90:
    tst r6,r6
    .org 0x28e92 - 0x28dc8
L_00028e92:
    bt/s L_00028e98
    .org 0x28e94 - 0x28dc8
L_00028e94:
    mov.w r2,@r5
    .org 0x28e96 - 0x28dc8
L_00028e96:
    sub r6,r4
    .org 0x28e98 - 0x28dc8
L_00028e98:
    mov.b r4,@r7
    .org 0x28e9a - 0x28dc8
L_00028e9a:
    rts
    .org 0x28e9c - 0x28dc8
L_00028e9c:
    lds.l @r15+,macl
    .org 0x28e9e - 0x28dc8
L_00028e9e:
    .word 0x0126
    .org 0x28ea0 - 0x28dc8
L_00028ea0:
    .word 0x199a
    .org 0x29020 - 0x28dc8
L_00029020:
    .long 0xffff128c
    .org 0x2b660 - 0x28dc8
L_0002b660:
    mov.l L_0002b868,r6
    .org 0x2b662 - 0x28dc8
L_0002b662:
    mov.b @(0x1,r6),r0
    .org 0x2b664 - 0x28dc8
L_0002b664:
    tst #0x40,r0
    .org 0x2b666 - 0x28dc8
L_0002b666:
    bt/s L_0002b68e
    .org 0x2b668 - 0x28dc8
L_0002b668:
    extu.b r4,r4
    .org 0x2b66a - 0x28dc8
L_0002b66a:
    mov #0x78,r6
    .org 0x2b66c - 0x28dc8
L_0002b66c:
    mov r4,r2
    .org 0x2b66e - 0x28dc8
L_0002b66e:
    mov #0x0,r0
    .org 0x2b670 - 0x28dc8
L_0002b670:
    cmp/ge r6,r4
    .org 0x2b672 - 0x28dc8
L_0002b672:
    bf/s L_0002b686
    .org 0x2b674 - 0x28dc8
L_0002b674:
    mov.w r0,@(0x12c,gbr)
    .org 0x2b676 - 0x28dc8
L_0002b676:
    add #-0x78,r2
    .org 0x2b678 - 0x28dc8
L_0002b678:
    cmp/pz r2
    .org 0x2b67a - 0x28dc8
L_0002b67a:
    bt/s L_0002b680
    .org 0x2b67c - 0x28dc8
L_0002b67c:
    mov r2,r6
    .org 0x2b67e - 0x28dc8
L_0002b67e:
    mov #0x0,r6
    .org 0x2b680 - 0x28dc8
L_0002b680:
    mov #0x1,r0
    .org 0x2b682 - 0x28dc8
L_0002b682:
    mov r6,r2
    .org 0x2b684 - 0x28dc8
L_0002b684:
    mov.w r0,@(0x12c,gbr)
    .org 0x2b686 - 0x28dc8
L_0002b686:
    mov.l L_0002b864,r13
    .org 0x2b688 - 0x28dc8
L_0002b688:
    mov.w L_0002b75e,r0
    .org 0x2b68a - 0x28dc8
L_0002b68a:
    bra L_0002b6ce
    .org 0x2b68c - 0x28dc8
L_0002b68c:
    mov.b r2,@(r0,r13)
    .org 0x2b68e - 0x28dc8
L_0002b68e:
    mov #0x4b,r2
    .org 0x2b690 - 0x28dc8
L_0002b690:
    mov.l L_0002b864,r14
    .org 0x2b692 - 0x28dc8
L_0002b692:
    stc gbr,r5
    .org 0x2b694 - 0x28dc8
L_0002b694:
    shll2 r2
    .org 0x2b696 - 0x28dc8
L_0002b696:
    mov r14,r6
    .org 0x2b698 - 0x28dc8
L_0002b698:
    add r2,r5
    .org 0x2b69a - 0x28dc8
L_0002b69a:
    mov.w L_0002b75e,r2
    .org 0x2b69c - 0x28dc8
L_0002b69c:
    mov.l L_0002b86c,r3
    .org 0x2b69e - 0x28dc8
L_0002b69e:
    jsr @r3
    .org 0x2b6a0 - 0x28dc8
L_0002b6a0:
    add r2,r6
    .org 0x2b6a2 - 0x28dc8
L_0002b6a2:
    mov.w @(0x12c,gbr),r0
    .org 0x2b6a4 - 0x28dc8
L_0002b6a4:
    tst r0,r0
    .org 0x2b6a6 - 0x28dc8
L_0002b6a6:
    bt/s L_0002b6bc
    .org 0x2b6a8 - 0x28dc8
L_0002b6a8:
    mov r0,r6
    .org 0x2b6aa - 0x28dc8
L_0002b6aa:
    add #-0x1,r6
    .org 0x2b6ac - 0x28dc8
L_0002b6ac:
    extu.w r6,r6
    .org 0x2b6ae - 0x28dc8
L_0002b6ae:
    mov.l L_0002b864,r13
    .org 0x2b6b0 - 0x28dc8
L_0002b6b0:
    mov r6,r0
    .org 0x2b6b2 - 0x28dc8
L_0002b6b2:
    mov.w r0,@(0x12c,gbr)
    .org 0x2b6b4 - 0x28dc8
L_0002b6b4:
    mov.w L_0002b75e,r0
    .org 0x2b6b6 - 0x28dc8
L_0002b6b6:
    mov.b @(r0,r13),r2
    .org 0x2b6b8 - 0x28dc8
L_0002b6b8:
    add #0xa,r2
    .org 0x2b6ba - 0x28dc8
L_0002b6ba:
    mov.b r2,@(r0,r13)
    .org 0x2b6bc - 0x28dc8
L_0002b6bc:
    mov #0x4b,r2
    .org 0x2b6be - 0x28dc8
L_0002b6be:
    stc gbr,r4
    .org 0x2b6c0 - 0x28dc8
L_0002b6c0:
    shll2 r2
    .org 0x2b6c2 - 0x28dc8
L_0002b6c2:
    add r2,r4
    .org 0x2b6c4 - 0x28dc8
L_0002b6c4:
    mov.w L_0002b75e,r2
    .org 0x2b6c6 - 0x28dc8
L_0002b6c6:
    add r2,r14
    .org 0x2b6c8 - 0x28dc8
L_0002b6c8:
    mov.l L_0002b870,r3
    .org 0x2b6ca - 0x28dc8
L_0002b6ca:
    jsr @r3
    .org 0x2b6cc - 0x28dc8
L_0002b6cc:
    mov r14,r5
    .org 0x2b6ce - 0x28dc8
L_0002b6ce:
    .org 0x2b75e - 0x28dc8
L_0002b75e:
    .word 0x06af
    .org 0x2b864 - 0x28dc8
L_0002b864:
    .long 0xffff128c
    .org 0x2b868 - 0x28dc8
L_0002b868:
    .long 0xffff24c8
    .org 0x2b86c - 0x28dc8
L_0002b86c:
    .long 0x00028e7c
    .org 0x2b870 - 0x28dc8
L_0002b870:
    .long 0x00028dc8
