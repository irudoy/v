! Complete stock dispatch and actual selector, one-shot and programmer calls.
    .text
    .balign 4
    .org 0x85f7 - 0x85f4
L_000085f7:
    .byte 0x80
    .org 0x8d92 - 0x85f4
L_00008d92:
    .byte 0x7a
    .org 0x94e8 - 0x85f4
L_000094e8:
    .word 0x00aa
    .org 0x2219c - 0x85f4
L_0002219c:
    .byte 0x0e,0x0c,0x0a,0x08,0x06,0x04,0x02,0x00,0x20,0x1e,0x1c,0x1a,0x18,0x16,0x14,0x12,0x34,0x32,0x30,0x2e,0x2c,0x2a,0x28,0x26,0x40,0x3e,0x3c,0x3a,0x48,0x56,0x62,0x6c
    .org 0x221bc - 0x85f4
L_000221bc:
    mov.l r2,@-r15
    .org 0x221be - 0x85f4
L_000221be:
    cmp/pz r1
    .org 0x221c0 - 0x85f4
L_000221c0:
    bf/s L_000221f4
    .org 0x221c2 - 0x85f4
L_000221c2:
    mov #0x20,r2
    .org 0x221c4 - 0x85f4
L_000221c4:
    cmp/ge r2,r1
    .org 0x221c6 - 0x85f4
L_000221c6:
    bt L_000221e0
    .org 0x221c8 - 0x85f4
L_000221c8:
    mov.l L_000221dc,r2
    .org 0x221ca - 0x85f4
L_000221ca:
    add r1,r2
    .org 0x221cc - 0x85f4
L_000221cc:
    mov.b @r2,r2
    .org 0x221ce - 0x85f4
L_000221ce:
    mov.l L_000221d8,r1
    .org 0x221d0 - 0x85f4
L_000221d0:
    add r2,r1
    .org 0x221d2 - 0x85f4
L_000221d2:
    jmp @r1
    .org 0x221d4 - 0x85f4
L_000221d4:
    nop
    .org 0x221d8 - 0x85f4
L_000221d8:
    .long 0x000221e6
    .org 0x221dc - 0x85f4
L_000221dc:
    .long 0x0002219c
    .org 0x221e0 - 0x85f4
L_000221e0:
    mov #0x0,r0
    .org 0x221e2 - 0x85f4
L_000221e2:
    rts
    .org 0x221e4 - 0x85f4
L_000221e4:
    mov.l @r15+,r2
    .org 0x221e6 - 0x85f4
L_000221e6:
    shll r0
    .org 0x221e8 - 0x85f4
L_000221e8:
    shll r0
    .org 0x221ea - 0x85f4
L_000221ea:
    shll r0
    .org 0x221ec - 0x85f4
L_000221ec:
    shll r0
    .org 0x221ee - 0x85f4
L_000221ee:
    shll r0
    .org 0x221f0 - 0x85f4
L_000221f0:
    shll r0
    .org 0x221f2 - 0x85f4
L_000221f2:
    shll r0
    .org 0x221f4 - 0x85f4
L_000221f4:
    rts
    .org 0x221f6 - 0x85f4
L_000221f6:
    mov.l @r15+,r2
    .org 0x2268e - 0x85f4
L_0002268e:
    .byte 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x02,0x04,0x08,0x10,0x20,0x01,0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x00,0x18,0x30,0x21,0x03,0x06,0x0c,0x00,0x00,0x00,0x00,0x01,0x1d,0x89,0xff,0xff,0x10,0x79,0xff,0xff,0x11,0x8e,0xff,0xff,0x11,0x88,0xff,0xff,0x10,0x74,0xff,0xff,0x3f,0xc5,0xff,0xff,0x28,0x37,0xff,0xff,0x20,0x22,0xff,0xff,0x20,0x22,0xff,0xff,0x20,0x22,0xff,0xff,0x20,0x22,0xff,0xff,0xff,0xff,0xff,0xff,0x56,0x47,0xff,0xff,0x22,0xe4,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0x23,0x5a,0xff,0xff,0x10,0x74,0xff,0xff,0x56,0x45,0xff,0xff,0x11,0x3a,0xff,0xff,0x98,0x1c,0xff,0xff,0x11,0x44,0xff,0xff,0x11,0x8a,0xff,0xff,0x41,0x3e,0xff,0xff,0x22,0xc4,0xff,0xff,0x22,0xc5,0xff,0xff,0x11,0x8c,0xff,0xff,0x11,0x8d,0xff,0xff,0x1f,0xb6,0xff,0xff,0xff,0xff,0xff,0xff,0x10,0x75,0xff,0xff,0x28,0x76,0x00,0x01,0x1d,0x95,0xff,0xff,0x1e,0xd4,0xff,0xff,0xff,0xff,0xff,0xff,0x22,0xdc,0xff,0xff,0x22,0xde,0xff,0xff,0x23,0x02,0xff,0xff,0x23,0x04,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0x45,0x44,0xff,0xff,0x16,0xd2,0xff,0xff,0x2e,0x96,0xff,0xff,0xff,0xff,0xff,0xff,0x56,0x4c,0xff,0xff,0x56,0x90,0xff,0xff,0xff,0xff,0xff,0xff,0x16,0xe0,0xff,0xff,0x16,0x2e,0xff,0xff,0x16,0x2e,0xff,0xff,0x16,0x2e,0xff,0xff,0x22,0xe8,0xff,0xff,0x24,0x42,0xff,0xff,0x1a,0xe8,0xff,0xff,0x1a,0xe9,0xff,0xff,0x24,0x40,0xff,0xff,0x24,0x41,0xff,0xff,0x23,0x26,0xff,0xff,0x1b
    .org 0x28dc8 - 0x85f4
L_00028dc8:
    mov.l L_00029020,r2
    .org 0x28dca - 0x85f4
L_00028dca:
    mov r5,r7
    .org 0x28dcc - 0x85f4
L_00028dcc:
    mov.w L_00028e9e,r0
    .org 0x28dce - 0x85f4
L_00028dce:
    mov.b @(r0,r2),r5
    .org 0x28dd0 - 0x85f4
L_00028dd0:
    mov.w @r4,r2
    .org 0x28dd2 - 0x85f4
L_00028dd2:
    extu.b r5,r0
    .org 0x28dd4 - 0x85f4
L_00028dd4:
    cmp/eq #0x4,r0
    .org 0x28dd6 - 0x85f4
L_00028dd6:
    bf/s L_00028df4
    .org 0x28dd8 - 0x85f4
L_00028dd8:
    extu.w r2,r2
    .org 0x28dda - 0x85f4
L_00028dda:
    mov #0x6,r5
    .org 0x28ddc - 0x85f4
L_00028ddc:
    cmp/ge r5,r2
    .org 0x28dde - 0x85f4
L_00028dde:
    bf L_00028de6
    .org 0x28de0 - 0x85f4
L_00028de0:
    mov #0xf,r5
    .org 0x28de2 - 0x85f4
L_00028de2:
    cmp/gt r5,r2
    .org 0x28de4 - 0x85f4
L_00028de4:
    bf L_00028e4c
    .org 0x28de6 - 0x85f4
L_00028de6:
    mov r2,r0
    .org 0x28de8 - 0x85f4
L_00028de8:
    cmp/eq #0x5,r0
    .org 0x28dea - 0x85f4
L_00028dea:
    bt L_00028e6a
    .org 0x28dec - 0x85f4
L_00028dec:
    cmp/eq #0x4,r0
    .org 0x28dee - 0x85f4
L_00028dee:
    bt L_00028e5e
    .org 0x28df0 - 0x85f4
L_00028df0:
    bra L_00028e78
    .org 0x28df2 - 0x85f4
L_00028df2:
    nop
    .org 0x28df4 - 0x85f4
L_00028df4:
    cmp/eq #0x9,r0
    .org 0x28df6 - 0x85f4
L_00028df6:
    bf L_00028e18
    .org 0x28df8 - 0x85f4
L_00028df8:
    mov r2,r0
    .org 0x28dfa - 0x85f4
L_00028dfa:
    cmp/eq #0x9,r0
    .org 0x28dfc - 0x85f4
L_00028dfc:
    bf L_00028e0c
    .org 0x28dfe - 0x85f4
L_00028dfe:
    add #-0x1,r2
    .org 0x28e00 - 0x85f4
L_00028e00:
    extu.w r2,r2
    .org 0x28e02 - 0x85f4
L_00028e02:
    mov.w r2,@r4
    .org 0x28e04 - 0x85f4
L_00028e04:
    mov.b @r7,r2
    .org 0x28e06 - 0x85f4
L_00028e06:
    add #0xa,r2
    .org 0x28e08 - 0x85f4
L_00028e08:
    mov.b r2,@r7
    .org 0x28e0a - 0x85f4
L_00028e0a:
    mov.w @r4,r2
    .org 0x28e0c - 0x85f4
L_00028e0c:
    extu.w r2,r2
    .org 0x28e0e - 0x85f4
L_00028e0e:
    mov #0xa,r5
    .org 0x28e10 - 0x85f4
L_00028e10:
    cmp/ge r5,r2
    .org 0x28e12 - 0x85f4
L_00028e12:
    bt L_00028e6a
    .org 0x28e14 - 0x85f4
L_00028e14:
    bra L_00028e78
    .org 0x28e16 - 0x85f4
L_00028e16:
    nop
    .org 0x28e18 - 0x85f4
L_00028e18:
    mov #0xf,r5
    .org 0x28e1a - 0x85f4
L_00028e1a:
    cmp/ge r5,r2
    .org 0x28e1c - 0x85f4
L_00028e1c:
    bf L_00028e2a
    .org 0x28e1e - 0x85f4
L_00028e1e:
    mov #0x18,r5
    .org 0x28e20 - 0x85f4
L_00028e20:
    cmp/gt r5,r2
    .org 0x28e22 - 0x85f4
L_00028e22:
    bt L_00028e2a
    .org 0x28e24 - 0x85f4
L_00028e24:
    add #-0x4,r2
    .org 0x28e26 - 0x85f4
L_00028e26:
    bra L_00028e50
    .org 0x28e28 - 0x85f4
L_00028e28:
    extu.w r2,r2
    .org 0x28e2a - 0x85f4
L_00028e2a:
    mov r2,r0
    .org 0x28e2c - 0x85f4
L_00028e2c:
    cmp/eq #0xe,r0
    .org 0x28e2e - 0x85f4
L_00028e2e:
    bf L_00028e36
    .org 0x28e30 - 0x85f4
L_00028e30:
    add #-0x4,r2
    .org 0x28e32 - 0x85f4
L_00028e32:
    bra L_00028e6e
    .org 0x28e34 - 0x85f4
L_00028e34:
    extu.w r2,r2
    .org 0x28e36 - 0x85f4
L_00028e36:
    cmp/eq #0xd,r0
    .org 0x28e38 - 0x85f4
L_00028e38:
    bf L_00028e40
    .org 0x28e3a - 0x85f4
L_00028e3a:
    add #-0x3,r2
    .org 0x28e3c - 0x85f4
L_00028e3c:
    bra L_00028e62
    .org 0x28e3e - 0x85f4
L_00028e3e:
    extu.w r2,r2
    .org 0x28e40 - 0x85f4
L_00028e40:
    mov #0x3,r5
    .org 0x28e42 - 0x85f4
L_00028e42:
    cmp/ge r5,r2
    .org 0x28e44 - 0x85f4
L_00028e44:
    bf L_00028e54
    .org 0x28e46 - 0x85f4
L_00028e46:
    mov #0xc,r5
    .org 0x28e48 - 0x85f4
L_00028e48:
    cmp/gt r5,r2
    .org 0x28e4a - 0x85f4
L_00028e4a:
    bt L_00028e54
    .org 0x28e4c - 0x85f4
L_00028e4c:
    add #-0x2,r2
    .org 0x28e4e - 0x85f4
L_00028e4e:
    extu.w r2,r2
    .org 0x28e50 - 0x85f4
L_00028e50:
    rts
    .org 0x28e52 - 0x85f4
L_00028e52:
    mov.w r2,@r4
    .org 0x28e54 - 0x85f4
L_00028e54:
    mov r2,r0
    .org 0x28e56 - 0x85f4
L_00028e56:
    cmp/eq #0x2,r0
    .org 0x28e58 - 0x85f4
L_00028e58:
    bt L_00028e6a
    .org 0x28e5a - 0x85f4
L_00028e5a:
    cmp/eq #0x1,r0
    .org 0x28e5c - 0x85f4
L_00028e5c:
    bf L_00028e78
    .org 0x28e5e - 0x85f4
L_00028e5e:
    add #-0x1,r2
    .org 0x28e60 - 0x85f4
L_00028e60:
    extu.w r2,r2
    .org 0x28e62 - 0x85f4
L_00028e62:
    mov.w r2,@r4
    .org 0x28e64 - 0x85f4
L_00028e64:
    mov.b @r7,r2
    .org 0x28e66 - 0x85f4
L_00028e66:
    bra L_00028e74
    .org 0x28e68 - 0x85f4
L_00028e68:
    add #0xa,r2
    .org 0x28e6a - 0x85f4
L_00028e6a:
    add #-0x2,r2
    .org 0x28e6c - 0x85f4
L_00028e6c:
    extu.w r2,r2
    .org 0x28e6e - 0x85f4
L_00028e6e:
    mov.w r2,@r4
    .org 0x28e70 - 0x85f4
L_00028e70:
    mov.b @r7,r2
    .org 0x28e72 - 0x85f4
L_00028e72:
    add #0x14,r2
    .org 0x28e74 - 0x85f4
L_00028e74:
    rts
    .org 0x28e76 - 0x85f4
L_00028e76:
    mov.b r2,@r7
    .org 0x28e78 - 0x85f4
L_00028e78:
    rts
    .org 0x28e7a - 0x85f4
L_00028e7a:
    nop
    .org 0x28e7c - 0x85f4
L_00028e7c:
    sts.l macl,@-r15
    .org 0x28e7e - 0x85f4
L_00028e7e:
    mov.w L_00028ea0,r3
    .org 0x28e80 - 0x85f4
L_00028e80:
    mov r6,r7
    .org 0x28e82 - 0x85f4
L_00028e82:
    mul.l r4,r3
    .org 0x28e84 - 0x85f4
L_00028e84:
    sts macl,r2
    .org 0x28e86 - 0x85f4
L_00028e86:
    shlr16 r2
    .org 0x28e88 - 0x85f4
L_00028e88:
    mov r2,r6
    .org 0x28e8a - 0x85f4
L_00028e8a:
    shll2 r6
    .org 0x28e8c - 0x85f4
L_00028e8c:
    add r2,r6
    .org 0x28e8e - 0x85f4
L_00028e8e:
    shll r6
    .org 0x28e90 - 0x85f4
L_00028e90:
    tst r6,r6
    .org 0x28e92 - 0x85f4
L_00028e92:
    bt/s L_00028e98
    .org 0x28e94 - 0x85f4
L_00028e94:
    mov.w r2,@r5
    .org 0x28e96 - 0x85f4
L_00028e96:
    sub r6,r4
    .org 0x28e98 - 0x85f4
L_00028e98:
    mov.b r4,@r7
    .org 0x28e9a - 0x85f4
L_00028e9a:
    rts
    .org 0x28e9c - 0x85f4
L_00028e9c:
    lds.l @r15+,macl
    .org 0x28e9e - 0x85f4
L_00028e9e:
    .word 0x0126
    .org 0x28ea0 - 0x85f4
L_00028ea0:
    .word 0x199a
    .org 0x29020 - 0x85f4
L_00029020:
    .long 0xffff128c
    .org 0x2b64a - 0x85f4
L_0002b64a:
    mov.l r13,@-r15
    .org 0x2b64c - 0x85f4
L_0002b64c:
    mov.l r14,@-r15
    .org 0x2b64e - 0x85f4
L_0002b64e:
    sts.l pr,@-r15
    .org 0x2b650 - 0x85f4
L_0002b650:
    sts.l macl,@-r15
    .org 0x2b652 - 0x85f4
L_0002b652:
    stc.l gbr,@-r15
    .org 0x2b654 - 0x85f4
L_0002b654:
    mov.l L_0002b864,r0
    .org 0x2b656 - 0x85f4
L_0002b656:
    ldc r0,gbr
    .org 0x2b658 - 0x85f4
L_0002b658:
    mov.w L_0002b75c,r6
    .org 0x2b65a - 0x85f4
L_0002b65a:
    mov.b @r6,r0
    .org 0x2b65c - 0x85f4
L_0002b65c:
    or #0x80,r0
    .org 0x2b65e - 0x85f4
L_0002b65e:
    mov.b r0,@r6
    .org 0x2b660 - 0x85f4
L_0002b660:
    mov.l L_0002b868,r6
    .org 0x2b662 - 0x85f4
L_0002b662:
    mov.b @(0x1,r6),r0
    .org 0x2b664 - 0x85f4
L_0002b664:
    tst #0x40,r0
    .org 0x2b666 - 0x85f4
L_0002b666:
    bt/s L_0002b68e
    .org 0x2b668 - 0x85f4
L_0002b668:
    extu.b r4,r4
    .org 0x2b66a - 0x85f4
L_0002b66a:
    mov #0x78,r6
    .org 0x2b66c - 0x85f4
L_0002b66c:
    mov r4,r2
    .org 0x2b66e - 0x85f4
L_0002b66e:
    mov #0x0,r0
    .org 0x2b670 - 0x85f4
L_0002b670:
    cmp/ge r6,r4
    .org 0x2b672 - 0x85f4
L_0002b672:
    bf/s L_0002b686
    .org 0x2b674 - 0x85f4
L_0002b674:
    mov.w r0,@(0x12c,gbr)
    .org 0x2b676 - 0x85f4
L_0002b676:
    add #-0x78,r2
    .org 0x2b678 - 0x85f4
L_0002b678:
    cmp/pz r2
    .org 0x2b67a - 0x85f4
L_0002b67a:
    bt/s L_0002b680
    .org 0x2b67c - 0x85f4
L_0002b67c:
    mov r2,r6
    .org 0x2b67e - 0x85f4
L_0002b67e:
    mov #0x0,r6
    .org 0x2b680 - 0x85f4
L_0002b680:
    mov #0x1,r0
    .org 0x2b682 - 0x85f4
L_0002b682:
    mov r6,r2
    .org 0x2b684 - 0x85f4
L_0002b684:
    mov.w r0,@(0x12c,gbr)
    .org 0x2b686 - 0x85f4
L_0002b686:
    mov.l L_0002b864,r13
    .org 0x2b688 - 0x85f4
L_0002b688:
    mov.w L_0002b75e,r0
    .org 0x2b68a - 0x85f4
L_0002b68a:
    bra L_0002b6ce
    .org 0x2b68c - 0x85f4
L_0002b68c:
    mov.b r2,@(r0,r13)
    .org 0x2b68e - 0x85f4
L_0002b68e:
    mov #0x4b,r2
    .org 0x2b690 - 0x85f4
L_0002b690:
    mov.l L_0002b864,r14
    .org 0x2b692 - 0x85f4
L_0002b692:
    stc gbr,r5
    .org 0x2b694 - 0x85f4
L_0002b694:
    shll2 r2
    .org 0x2b696 - 0x85f4
L_0002b696:
    mov r14,r6
    .org 0x2b698 - 0x85f4
L_0002b698:
    add r2,r5
    .org 0x2b69a - 0x85f4
L_0002b69a:
    mov.w L_0002b75e,r2
    .org 0x2b69c - 0x85f4
L_0002b69c:
    mov.l L_0002b86c,r3
    .org 0x2b69e - 0x85f4
L_0002b69e:
    jsr @r3
    .org 0x2b6a0 - 0x85f4
L_0002b6a0:
    add r2,r6
    .org 0x2b6a2 - 0x85f4
L_0002b6a2:
    mov.w @(0x12c,gbr),r0
    .org 0x2b6a4 - 0x85f4
L_0002b6a4:
    tst r0,r0
    .org 0x2b6a6 - 0x85f4
L_0002b6a6:
    bt/s L_0002b6bc
    .org 0x2b6a8 - 0x85f4
L_0002b6a8:
    mov r0,r6
    .org 0x2b6aa - 0x85f4
L_0002b6aa:
    add #-0x1,r6
    .org 0x2b6ac - 0x85f4
L_0002b6ac:
    extu.w r6,r6
    .org 0x2b6ae - 0x85f4
L_0002b6ae:
    mov.l L_0002b864,r13
    .org 0x2b6b0 - 0x85f4
L_0002b6b0:
    mov r6,r0
    .org 0x2b6b2 - 0x85f4
L_0002b6b2:
    mov.w r0,@(0x12c,gbr)
    .org 0x2b6b4 - 0x85f4
L_0002b6b4:
    mov.w L_0002b75e,r0
    .org 0x2b6b6 - 0x85f4
L_0002b6b6:
    mov.b @(r0,r13),r2
    .org 0x2b6b8 - 0x85f4
L_0002b6b8:
    add #0xa,r2
    .org 0x2b6ba - 0x85f4
L_0002b6ba:
    mov.b r2,@(r0,r13)
    .org 0x2b6bc - 0x85f4
L_0002b6bc:
    mov #0x4b,r2
    .org 0x2b6be - 0x85f4
L_0002b6be:
    stc gbr,r4
    .org 0x2b6c0 - 0x85f4
L_0002b6c0:
    shll2 r2
    .org 0x2b6c2 - 0x85f4
L_0002b6c2:
    add r2,r4
    .org 0x2b6c4 - 0x85f4
L_0002b6c4:
    mov.w L_0002b75e,r2
    .org 0x2b6c6 - 0x85f4
L_0002b6c6:
    add r2,r14
    .org 0x2b6c8 - 0x85f4
L_0002b6c8:
    mov.l L_0002b870,r3
    .org 0x2b6ca - 0x85f4
L_0002b6ca:
    jsr @r3
    .org 0x2b6cc - 0x85f4
L_0002b6cc:
    mov r14,r5
    .org 0x2b6ce - 0x85f4
L_0002b6ce:
    mov.w @(0x12c,gbr),r0
    .org 0x2b6d0 - 0x85f4
L_0002b6d0:
    tst r0,r0
    .org 0x2b6d2 - 0x85f4
L_0002b6d2:
    bf L_0002b74a
    .org 0x2b6d4 - 0x85f4
L_0002b6d4:
    mov.l L_0002b874,r2
    .org 0x2b6d6 - 0x85f4
L_0002b6d6:
    mov.w L_0002b760,r0
    .org 0x2b6d8 - 0x85f4
L_0002b6d8:
    mov.l L_0002b864,r13
    .org 0x2b6da - 0x85f4
L_0002b6da:
    mov.w @(r0,r2),r6
    .org 0x2b6dc - 0x85f4
L_0002b6dc:
    mov.w L_0002b75e,r0
    .org 0x2b6de - 0x85f4
L_0002b6de:
    extu.w r6,r6
    .org 0x2b6e0 - 0x85f4
L_0002b6e0:
    mov.b @(r0,r13),r2
    .org 0x2b6e2 - 0x85f4
L_0002b6e2:
    extu.b r2,r5
    .org 0x2b6e4 - 0x85f4
L_0002b6e4:
    mov.w L_0002b762,r2
    .org 0x2b6e6 - 0x85f4
L_0002b6e6:
    mul.l r6,r5
    .org 0x2b6e8 - 0x85f4
L_0002b6e8:
    mov r13,r5
    .org 0x2b6ea - 0x85f4
L_0002b6ea:
    add r2,r5
    .org 0x2b6ec - 0x85f4
L_0002b6ec:
    add #-0x56,r2
    .org 0x2b6ee - 0x85f4
L_0002b6ee:
    mov r13,r6
    .org 0x2b6f0 - 0x85f4
L_0002b6f0:
    sts macl,r4
    .org 0x2b6f2 - 0x85f4
L_0002b6f2:
    mov.l L_0002b86c,r3
    .org 0x2b6f4 - 0x85f4
L_0002b6f4:
    jsr @r3
    .org 0x2b6f6 - 0x85f4
L_0002b6f6:
    add r2,r6
    .org 0x2b6f8 - 0x85f4
L_0002b6f8:
    stc sr,r0
    .org 0x2b6fa - 0x85f4
L_0002b6fa:
    mov.w L_0002b75a,r6
    .org 0x2b6fc - 0x85f4
L_0002b6fc:
    and r6,r0
    .org 0x2b6fe - 0x85f4
L_0002b6fe:
    or #0xf0,r0
    .org 0x2b700 - 0x85f4
L_0002b700:
    ldc r0,sr
    .org 0x2b702 - 0x85f4
L_0002b702:
    mov.w L_0002b764,r4
    .org 0x2b704 - 0x85f4
L_0002b704:
    mov.w L_0002b766,r0
    .org 0x2b706 - 0x85f4
L_0002b706:
    mov.w @r4,r2
    .org 0x2b708 - 0x85f4
L_0002b708:
    mov.w @(r0,r13),r5
    .org 0x2b70a - 0x85f4
L_0002b70a:
    mov.w L_0002b762,r0
    .org 0x2b70c - 0x85f4
L_0002b70c:
    extu.w r2,r6
    .org 0x2b70e - 0x85f4
L_0002b70e:
    extu.w r5,r5
    .org 0x2b710 - 0x85f4
L_0002b710:
    sub r5,r6
    .org 0x2b712 - 0x85f4
L_0002b712:
    mov.w @(r0,r13),r7
    .org 0x2b714 - 0x85f4
L_0002b714:
    extu.w r6,r2
    .org 0x2b716 - 0x85f4
L_0002b716:
    extu.w r7,r7
    .org 0x2b718 - 0x85f4
L_0002b718:
    add #0x2,r2
    .org 0x2b71a - 0x85f4
L_0002b71a:
    cmp/gt r7,r2
    .org 0x2b71c - 0x85f4
L_0002b71c:
    bf L_0002b724
    .org 0x2b71e - 0x85f4
L_0002b71e:
    mov.w @r4,r0
    .org 0x2b720 - 0x85f4
L_0002b720:
    bra L_0002b728
    .org 0x2b722 - 0x85f4
L_0002b722:
    add #0x2,r0
    .org 0x2b724 - 0x85f4
L_0002b724:
    add r7,r5
    .org 0x2b726 - 0x85f4
L_0002b726:
    mov r5,r0
    .org 0x2b728 - 0x85f4
L_0002b728:
    mov.w r0,@(0x4,r4)
    .org 0x2b72a - 0x85f4
L_0002b72a:
    mov #-0x2,r5
    .org 0x2b72c - 0x85f4
L_0002b72c:
    mov.w @(0x1e,r4),r0
    .org 0x2b72e - 0x85f4
L_0002b72e:
    extu.w r0,r0
    .org 0x2b730 - 0x85f4
L_0002b730:
    and r5,r0
    .org 0x2b732 - 0x85f4
L_0002b732:
    mov.w r0,@(0x1e,r4)
    .org 0x2b734 - 0x85f4
L_0002b734:
    mov #0x22,r0
    .org 0x2b736 - 0x85f4
L_0002b736:
    mov.w @(r0,r4),r0
    .org 0x2b738 - 0x85f4
L_0002b738:
    or #0x1,r0
    .org 0x2b73a - 0x85f4
L_0002b73a:
    mov r0,r2
    .org 0x2b73c - 0x85f4
L_0002b73c:
    mov #0x22,r0
    .org 0x2b73e - 0x85f4
L_0002b73e:
    mov.w r2,@(r0,r4)
    .org 0x2b740 - 0x85f4
L_0002b740:
    stc sr,r0
    .org 0x2b742 - 0x85f4
L_0002b742:
    mov.w L_0002b75a,r6
    .org 0x2b744 - 0x85f4
L_0002b744:
    and r6,r0
    .org 0x2b746 - 0x85f4
L_0002b746:
    or #0x80,r0
    .org 0x2b748 - 0x85f4
L_0002b748:
    ldc r0,sr
    .org 0x2b74a - 0x85f4
L_0002b74a:
    ldc.l @r15+,gbr
    .org 0x2b74c - 0x85f4
L_0002b74c:
    lds.l @r15+,macl
    .org 0x2b74e - 0x85f4
L_0002b74e:
    lds.l @r15+,pr
    .org 0x2b750 - 0x85f4
L_0002b750:
    mov.l @r15+,r14
    .org 0x2b752 - 0x85f4
L_0002b752:
    rts
    .org 0x2b754 - 0x85f4
L_0002b754:
    mov.l @r15+,r13
    .org 0x2b75a - 0x85f4
L_0002b75a:
    .word 0xff0f
    .org 0x2b75c - 0x85f4
L_0002b75c:
    .word 0x84ec
    .org 0x2b75e - 0x85f4
L_0002b75e:
    .word 0x06af
    .org 0x2b760 - 0x85f4
L_0002b760:
    .word 0x02c8
    .org 0x2b762 - 0x85f4
L_0002b762:
    .word 0x0436
    .org 0x2b764 - 0x85f4
L_0002b764:
    .word 0xf440
    .org 0x2b766 - 0x85f4
L_0002b766:
    .word 0x02fe
    .org 0x2b864 - 0x85f4
L_0002b864:
    .long 0xffff128c
    .org 0x2b868 - 0x85f4
L_0002b868:
    .long 0xffff24c8
    .org 0x2b86c - 0x85f4
L_0002b86c:
    .long 0x00028e7c
    .org 0x2b870 - 0x85f4
L_0002b870:
    .long 0x00028dc8
    .org 0x2b874 - 0x85f4
L_0002b874:
    .long 0xffff1ff4
    .org 0x2c13c - 0x85f4
L_0002c13c:
    mov.l r8,@-r15
    .org 0x2c13e - 0x85f4
L_0002c13e:
    mov.l r9,@-r15
    .org 0x2c140 - 0x85f4
L_0002c140:
    mov.l r10,@-r15
    .org 0x2c142 - 0x85f4
L_0002c142:
    mov.l r11,@-r15
    .org 0x2c144 - 0x85f4
L_0002c144:
    mov.l r12,@-r15
    .org 0x2c146 - 0x85f4
L_0002c146:
    mov.l r13,@-r15
    .org 0x2c148 - 0x85f4
L_0002c148:
    mov.l r14,@-r15
    .org 0x2c14a - 0x85f4
L_0002c14a:
    sts.l macl,@-r15
    .org 0x2c14c - 0x85f4
L_0002c14c:
    stc.l gbr,@-r15
    .org 0x2c14e - 0x85f4
L_0002c14e:
    mov.l L_0002c240,r0
    .org 0x2c150 - 0x85f4
L_0002c150:
    ldc r0,gbr
    .org 0x2c152 - 0x85f4
L_0002c152:
    add #-0xc,r15
    .org 0x2c154 - 0x85f4
L_0002c154:
    mov.l L_0002c244,r6
    .org 0x2c156 - 0x85f4
L_0002c156:
    mov r5,r14
    .org 0x2c158 - 0x85f4
L_0002c158:
    mov.b @r6,r0
    .org 0x2c15a - 0x85f4
L_0002c15a:
    tst #0x80,r0
    .org 0x2c15c - 0x85f4
L_0002c15c:
    bt/s L_0002c21e
    .org 0x2c15e - 0x85f4
L_0002c15e:
    mov r4,r11
    .org 0x2c160 - 0x85f4
L_0002c160:
    mov.w L_0002c234,r12
    .org 0x2c162 - 0x85f4
L_0002c162:
    mov #-0x1,r8
    .org 0x2c164 - 0x85f4
L_0002c164:
    extu.w r8,r8
    .org 0x2c166 - 0x85f4
L_0002c166:
    mov.w L_0002c238,r9
    .org 0x2c168 - 0x85f4
L_0002c168:
    mov r12,r10
    .org 0x2c16a - 0x85f4
L_0002c16a:
    mov #0x1,r2
    .org 0x2c16c - 0x85f4
L_0002c16c:
    mov #0x6,r13
    .org 0x2c16e - 0x85f4
L_0002c16e:
    extu.b r2,r2
    .org 0x2c170 - 0x85f4
L_0002c170:
    extu.b r11,r11
    .org 0x2c172 - 0x85f4
L_0002c172:
    tst r2,r11
    .org 0x2c174 - 0x85f4
L_0002c174:
    bt L_0002c20e
    .org 0x2c176 - 0x85f4
L_0002c176:
    mov.l L_0002c248,r3
    .org 0x2c178 - 0x85f4
L_0002c178:
    mov.b @(0x4,r3),r0
    .org 0x2c17a - 0x85f4
L_0002c17a:
    tst r11,r0
    .org 0x2c17c - 0x85f4
L_0002c17c:
    bf/s L_0002c18a
    .org 0x2c17e - 0x85f4
L_0002c17e:
    mov.w @r14,r4
    .org 0x2c180 - 0x85f4
L_0002c180:
    mov.l L_0002c24c,r3
    .org 0x2c182 - 0x85f4
L_0002c182:
    mov.w L_0002c23a,r0
    .org 0x2c184 - 0x85f4
L_0002c184:
    mov.b @(r0,r3),r6
    .org 0x2c186 - 0x85f4
L_0002c186:
    tst r11,r6
    .org 0x2c188 - 0x85f4
L_0002c188:
    bt L_0002c198
    .org 0x2c18a - 0x85f4
L_0002c18a:
    mov.w @(0x7a,gbr),r0
    .org 0x2c18c - 0x85f4
L_0002c18c:
    mov.l L_0002c24c,r1
    .org 0x2c18e - 0x85f4
L_0002c18e:
    mov r0,r4
    .org 0x2c190 - 0x85f4
L_0002c190:
    mov.w L_0002c23a,r0
    .org 0x2c192 - 0x85f4
L_0002c192:
    mov.b @(r0,r1),r6
    .org 0x2c194 - 0x85f4
L_0002c194:
    or r11,r6
    .org 0x2c196 - 0x85f4
L_0002c196:
    mov.b r6,@(r0,r1)
    .org 0x2c198 - 0x85f4
L_0002c198:
    mov #0x26,r0
    .org 0x2c19a - 0x85f4
L_0002c19a:
    mov.w @(r0,r10),r5
    .org 0x2c19c - 0x85f4
L_0002c19c:
    tst r2,r5
    .org 0x2c19e - 0x85f4
L_0002c19e:
    bt L_0002c1b2
    .org 0x2c1a0 - 0x85f4
L_0002c1a0:
    mov.w @(0x7a,gbr),r0
    .org 0x2c1a2 - 0x85f4
L_0002c1a2:
    extu.w r4,r5
    .org 0x2c1a4 - 0x85f4
L_0002c1a4:
    extu.w r0,r7
    .org 0x2c1a6 - 0x85f4
L_0002c1a6:
    cmp/ge r7,r5
    .org 0x2c1a8 - 0x85f4
L_0002c1a8:
    bt L_0002c1ae
    .org 0x2c1aa - 0x85f4
L_0002c1aa:
    bra L_0002c1b0
    .org 0x2c1ac - 0x85f4
L_0002c1ac:
    mov #0x0,r5
    .org 0x2c1ae - 0x85f4
L_0002c1ae:
    sub r7,r5
    .org 0x2c1b0 - 0x85f4
L_0002c1b0:
    mov r5,r4
    .org 0x2c1b2 - 0x85f4
L_0002c1b2:
    mov.w L_0002c23c,r5
    .org 0x2c1b4 - 0x85f4
L_0002c1b4:
    extu.w r4,r4
    .org 0x2c1b6 - 0x85f4
L_0002c1b6:
    mul.l r4,r5
    .org 0x2c1b8 - 0x85f4
L_0002c1b8:
    sts macl,r6
    .org 0x2c1ba - 0x85f4
L_0002c1ba:
    shlr8 r6
    .org 0x2c1bc - 0x85f4
L_0002c1bc:
    swap.w r6,r5
    .org 0x2c1be - 0x85f4
L_0002c1be:
    exts.b r5,r6
    .org 0x2c1c0 - 0x85f4
L_0002c1c0:
    xtrct r6,r5
    .org 0x2c1c2 - 0x85f4
L_0002c1c2:
    cmp/hi r8,r5
    .org 0x2c1c4 - 0x85f4
L_0002c1c4:
    bf L_0002c1c8
    .org 0x2c1c6 - 0x85f4
L_0002c1c6:
    mov r8,r5
    .org 0x2c1c8 - 0x85f4
L_0002c1c8:
    mov r5,r4
    .org 0x2c1ca - 0x85f4
L_0002c1ca:
    mov r5,r0
    .org 0x2c1cc - 0x85f4
L_0002c1cc:
    mov.l L_0002c250,r5
    .org 0x2c1ce - 0x85f4
L_0002c1ce:
    mov.w r0,@(0x8,r15)
    .org 0x2c1d0 - 0x85f4
L_0002c1d0:
    mov.b @(0x5,r5),r0
    .org 0x2c1d2 - 0x85f4
L_0002c1d2:
    tst #0x1,r0
    .org 0x2c1d4 - 0x85f4
L_0002c1d4:
    bt L_0002c1dc
    .org 0x2c1d6 - 0x85f4
L_0002c1d6:
    mov.w L_0002c23e,r4
    .org 0x2c1d8 - 0x85f4
L_0002c1d8:
    mov r4,r0
    .org 0x2c1da - 0x85f4
L_0002c1da:
    mov.w r0,@(0x8,r15)
    .org 0x2c1dc - 0x85f4
L_0002c1dc:
    stc sr,r0
    .org 0x2c1de - 0x85f4
L_0002c1de:
    shlr2 r0
    .org 0x2c1e0 - 0x85f4
L_0002c1e0:
    shlr2 r0
    .org 0x2c1e2 - 0x85f4
L_0002c1e2:
    and #0xf,r0
    .org 0x2c1e4 - 0x85f4
L_0002c1e4:
    mov r0,r6
    .org 0x2c1e6 - 0x85f4
L_0002c1e6:
    stc sr,r0
    .org 0x2c1e8 - 0x85f4
L_0002c1e8:
    and r9,r0
    .org 0x2c1ea - 0x85f4
L_0002c1ea:
    or #0xf0,r0
    .org 0x2c1ec - 0x85f4
L_0002c1ec:
    ldc r0,sr
    .org 0x2c1ee - 0x85f4
L_0002c1ee:
    mov.w @r12,r5
    .org 0x2c1f0 - 0x85f4
L_0002c1f0:
    mov r6,r0
    .org 0x2c1f2 - 0x85f4
L_0002c1f2:
    and #0xf,r0
    .org 0x2c1f4 - 0x85f4
L_0002c1f4:
    add r4,r5
    .org 0x2c1f6 - 0x85f4
L_0002c1f6:
    mov.w r5,@r12
    .org 0x2c1f8 - 0x85f4
L_0002c1f8:
    mov r0,r5
    .org 0x2c1fa - 0x85f4
L_0002c1fa:
    shll2 r5
    .org 0x2c1fc - 0x85f4
L_0002c1fc:
    shll2 r5
    .org 0x2c1fe - 0x85f4
L_0002c1fe:
    stc sr,r6
    .org 0x2c200 - 0x85f4
L_0002c200:
    and r9,r6
    .org 0x2c202 - 0x85f4
L_0002c202:
    or r5,r6
    .org 0x2c204 - 0x85f4
L_0002c204:
    ldc r6,sr
    .org 0x2c206 - 0x85f4
L_0002c206:
    mov #0x26,r0
    .org 0x2c208 - 0x85f4
L_0002c208:
    mov.w @(r0,r10),r6
    .org 0x2c20a - 0x85f4
L_0002c20a:
    or r2,r6
    .org 0x2c20c - 0x85f4
L_0002c20c:
    mov.w r6,@(r0,r10)
    .org 0x2c20e - 0x85f4
L_0002c20e:
    add #0x2,r12
    .org 0x2c210 - 0x85f4
L_0002c210:
    shll r2
    .org 0x2c212 - 0x85f4
L_0002c212:
    mov.l r12,@r15
    .org 0x2c214 - 0x85f4
L_0002c214:
    dt r13
    .org 0x2c216 - 0x85f4
L_0002c216:
    mov r2,r0
    .org 0x2c218 - 0x85f4
L_0002c218:
    add #0x2,r14
    .org 0x2c21a - 0x85f4
L_0002c21a:
    bf/s L_0002c16e
    .org 0x2c21c - 0x85f4
L_0002c21c:
    mov.b r0,@(0x4,r15)
    .org 0x2c21e - 0x85f4
L_0002c21e:
    add #0xc,r15
    .org 0x2c220 - 0x85f4
L_0002c220:
    ldc.l @r15+,gbr
    .org 0x2c222 - 0x85f4
L_0002c222:
    lds.l @r15+,macl
    .org 0x2c224 - 0x85f4
L_0002c224:
    mov.l @r15+,r14
    .org 0x2c226 - 0x85f4
L_0002c226:
    mov.l @r15+,r13
    .org 0x2c228 - 0x85f4
L_0002c228:
    mov.l @r15+,r12
    .org 0x2c22a - 0x85f4
L_0002c22a:
    mov.l @r15+,r11
    .org 0x2c22c - 0x85f4
L_0002c22c:
    mov.l @r15+,r10
    .org 0x2c22e - 0x85f4
L_0002c22e:
    mov.l @r15+,r9
    .org 0x2c230 - 0x85f4
L_0002c230:
    rts
    .org 0x2c232 - 0x85f4
L_0002c232:
    mov.l @r15+,r8
    .org 0x2c234 - 0x85f4
L_0002c234:
    .word 0xf640
    .org 0x2c238 - 0x85f4
L_0002c238:
    .word 0xff0f
    .org 0x2c23a - 0x85f4
L_0002c23a:
    .word 0x06a9
    .org 0x2c23c - 0x85f4
L_0002c23c:
    .word 0x0320
    .org 0x2c23e - 0x85f4
L_0002c23e:
    .word 0x03e8
    .org 0x2c240 - 0x85f4
L_0002c240:
    .long 0xffff2330
    .org 0x2c244 - 0x85f4
L_0002c244:
    .long 0xffff4184
    .org 0x2c248 - 0x85f4
L_0002c248:
    .long 0xffff22dc
    .org 0x2c24c - 0x85f4
L_0002c24c:
    .long 0xffff128c
    .org 0x2c250 - 0x85f4
L_0002c250:
    .long 0xffff424c
    .org 0x54a44 - 0x85f4
L_00054a44:
    mov.l r8,@-r15
    .org 0x54a46 - 0x85f4
L_00054a46:
    mov.l r9,@-r15
    .org 0x54a48 - 0x85f4
L_00054a48:
    mov.l r10,@-r15
    .org 0x54a4a - 0x85f4
L_00054a4a:
    mov.l r11,@-r15
    .org 0x54a4c - 0x85f4
L_00054a4c:
    mov.l r12,@-r15
    .org 0x54a4e - 0x85f4
L_00054a4e:
    mov.l r13,@-r15
    .org 0x54a50 - 0x85f4
L_00054a50:
    mov.l r14,@-r15
    .org 0x54a52 - 0x85f4
L_00054a52:
    sts.l pr,@-r15
    .org 0x54a54 - 0x85f4
L_00054a54:
    stc.l gbr,@-r15
    .org 0x54a56 - 0x85f4
L_00054a56:
    mov.l L_00054c30,r0
    .org 0x54a58 - 0x85f4
L_00054a58:
    ldc r0,gbr
    .org 0x54a5a - 0x85f4
L_00054a5a:
    add #-0x18,r15
    .org 0x54a5c - 0x85f4
L_00054a5c:
    mov.l L_00054c34,r14
    .org 0x54a5e - 0x85f4
L_00054a5e:
    mov #-0x1,r2
    .org 0x54a60 - 0x85f4
L_00054a60:
    mov.w L_00054b52,r5
    .org 0x54a62 - 0x85f4
L_00054a62:
    extu.b r2,r2
    .org 0x54a64 - 0x85f4
L_00054a64:
    mov.b @r14,r4
    .org 0x54a66 - 0x85f4
L_00054a66:
    mov.b @(0x3,r5),r0
    .org 0x54a68 - 0x85f4
L_00054a68:
    extu.b r4,r4
    .org 0x54a6a - 0x85f4
L_00054a6a:
    cmp/ge r2,r4
    .org 0x54a6c - 0x85f4
L_00054a6c:
    bt/s L_00054a74
    .org 0x54a6e - 0x85f4
L_00054a6e:
    mov r0,r7
    .org 0x54a70 - 0x85f4
L_00054a70:
    add #0x1,r4
    .org 0x54a72 - 0x85f4
L_00054a72:
    mov.b r4,@r14
    .org 0x54a74 - 0x85f4
L_00054a74:
    mov.l L_00054c38,r2
    .org 0x54a76 - 0x85f4
L_00054a76:
    mov.l L_00054c3c,r8
    .org 0x54a78 - 0x85f4
L_00054a78:
    mov.b @(0xa,r2),r0
    .org 0x54a7a - 0x85f4
L_00054a7a:
    extu.b r0,r0
    .org 0x54a7c - 0x85f4
L_00054a7c:
    mov.b @(r0,r8),r2
    .org 0x54a7e - 0x85f4
L_00054a7e:
    extu.b r2,r4
    .org 0x54a80 - 0x85f4
L_00054a80:
    mov r8,r2
    .org 0x54a82 - 0x85f4
L_00054a82:
    add #0xd,r2
    .org 0x54a84 - 0x85f4
L_00054a84:
    mov.b @(r0,r2),r5
    .org 0x54a86 - 0x85f4
L_00054a86:
    mov #0x1,r2
    .org 0x54a88 - 0x85f4
L_00054a88:
    cmp/hi r2,r4
    .org 0x54a8a - 0x85f4
L_00054a8a:
    bf/s L_00054a98
    .org 0x54a8c - 0x85f4
L_00054a8c:
    add #-0x1,r5
    .org 0x54a8e - 0x85f4
L_00054a8e:
    mov #0x1,r6
    .org 0x54a90 - 0x85f4
L_00054a90:
    add #0x1,r6
    .org 0x54a92 - 0x85f4
L_00054a92:
    shll r2
    .org 0x54a94 - 0x85f4
L_00054a94:
    cmp/hs r4,r6
    .org 0x54a96 - 0x85f4
L_00054a96:
    bf L_00054a90
    .org 0x54a98 - 0x85f4
L_00054a98:
    mov.l L_00054c40,r3
    .org 0x54a9a - 0x85f4
L_00054a9a:
    mov.w L_00054b54,r0
    .org 0x54a9c - 0x85f4
L_00054a9c:
    mov.b @(r0,r3),r6
    .org 0x54a9e - 0x85f4
L_00054a9e:
    or r2,r6
    .org 0x54aa0 - 0x85f4
L_00054aa0:
    mov.b r6,@(r0,r3)
    .org 0x54aa2 - 0x85f4
L_00054aa2:
    mov r7,r0
    .org 0x54aa4 - 0x85f4
L_00054aa4:
    tst #0x20,r0
    .org 0x54aa6 - 0x85f4
L_00054aa6:
    bf L_00054aac
    .org 0x54aa8 - 0x85f4
L_00054aa8:
    bra L_00054ab4
    .org 0x54aaa - 0x85f4
L_00054aaa:
    mov #0x3,r9
    .org 0x54aac - 0x85f4
L_00054aac:
    mov.l L_00054c44,r4
    .org 0x54aae - 0x85f4
L_00054aae:
    mov #0x34,r0
    .org 0x54ab0 - 0x85f4
L_00054ab0:
    mov.b @(r0,r4),r9
    .org 0x54ab2 - 0x85f4
L_00054ab2:
    extu.b r9,r9
    .org 0x54ab4 - 0x85f4
L_00054ab4:
    mov r5,r0
    .org 0x54ab6 - 0x85f4
L_00054ab6:
    and #0xf,r0
    .org 0x54ab8 - 0x85f4
L_00054ab8:
    sub r9,r0
    .org 0x54aba - 0x85f4
L_00054aba:
    cmp/pz r0
    .org 0x54abc - 0x85f4
L_00054abc:
    bt/s L_00054ac2
    .org 0x54abe - 0x85f4
L_00054abe:
    mov r0,r2
    .org 0x54ac0 - 0x85f4
L_00054ac0:
    add #0x6,r2
    .org 0x54ac2 - 0x85f4
L_00054ac2:
    mov.l L_00054c48,r6
    .org 0x54ac4 - 0x85f4
L_00054ac4:
    mov r2,r0
    .org 0x54ac6 - 0x85f4
L_00054ac6:
    mov.b r0,@(0xc0,gbr)
    .org 0x54ac8 - 0x85f4
L_00054ac8:
    mov r2,r5
    .org 0x54aca - 0x85f4
L_00054aca:
    mov.b @(0x1,r6),r0
    .org 0x54acc - 0x85f4
L_00054acc:
    and #0x20,r0
    .org 0x54ace - 0x85f4
L_00054ace:
    tst r0,r0
    .org 0x54ad0 - 0x85f4
L_00054ad0:
    bt/s L_00054b10
    .org 0x54ad2 - 0x85f4
L_00054ad2:
    mov r0,r2
    .org 0x54ad4 - 0x85f4
L_00054ad4:
    mov r7,r0
    .org 0x54ad6 - 0x85f4
L_00054ad6:
    tst #0x10,r0
    .org 0x54ad8 - 0x85f4
L_00054ad8:
    bf L_00054b10
    .org 0x54ada - 0x85f4
L_00054ada:
    mov.w L_00054b52,r6
    .org 0x54adc - 0x85f4
L_00054adc:
    or #0xe0,r0
    .org 0x54ade - 0x85f4
L_00054ade:
    mov.w L_00054b52,r4
    .org 0x54ae0 - 0x85f4
L_00054ae0:
    mov.b r0,@(0x3,r6)
    .org 0x54ae2 - 0x85f4
L_00054ae2:
    extu.b r5,r6
    .org 0x54ae4 - 0x85f4
L_00054ae4:
    mov.b @(0x4,r4),r0
    .org 0x54ae6 - 0x85f4
L_00054ae6:
    add #-0x1,r6
    .org 0x54ae8 - 0x85f4
L_00054ae8:
    mov.w L_00054b52,r7
    .org 0x54aea - 0x85f4
L_00054aea:
    cmp/pz r6
    .org 0x54aec - 0x85f4
L_00054aec:
    or #0x80,r0
    .org 0x54aee - 0x85f4
L_00054aee:
    mov.l r6,@(0x4,r15)
    .org 0x54af0 - 0x85f4
L_00054af0:
    bt/s L_00054af8
    .org 0x54af2 - 0x85f4
L_00054af2:
    mov.b r0,@(0x4,r7)
    .org 0x54af4 - 0x85f4
L_00054af4:
    mov #0x5,r6
    .org 0x54af6 - 0x85f4
L_00054af6:
    mov.l r6,@(0x4,r15)
    .org 0x54af8 - 0x85f4
L_00054af8:
    mov.l L_00054c30,r14
    .org 0x54afa - 0x85f4
L_00054afa:
    mov.w L_00054b56,r0
    .org 0x54afc - 0x85f4
L_00054afc:
    mov.w L_00054b52,r5
    .org 0x54afe - 0x85f4
L_00054afe:
    mov.b r6,@(r0,r14)
    .org 0x54b00 - 0x85f4
L_00054b00:
    mov.w L_00054b58,r0
    .org 0x54b02 - 0x85f4
L_00054b02:
    mov.w L_00054b52,r4
    .org 0x54b04 - 0x85f4
L_00054b04:
    mov.b r9,@(r0,r14)
    .org 0x54b06 - 0x85f4
L_00054b06:
    mov.b @(0x3,r5),r0
    .org 0x54b08 - 0x85f4
L_00054b08:
    or #0x10,r0
    .org 0x54b0a - 0x85f4
L_00054b0a:
    mov.b r0,@(0x3,r4)
    .org 0x54b0c - 0x85f4
L_00054b0c:
    mov.b @(0x3,r5),r0
    .org 0x54b0e - 0x85f4
L_00054b0e:
    mov r0,r7
    .org 0x54b10 - 0x85f4
L_00054b10:
    mov #-0x20,r6
    .org 0x54b12 - 0x85f4
L_00054b12:
    mov r7,r0
    .org 0x54b14 - 0x85f4
L_00054b14:
    and #0xe0,r0
    .org 0x54b16 - 0x85f4
L_00054b16:
    extu.b r6,r5
    .org 0x54b18 - 0x85f4
L_00054b18:
    cmp/eq r5,r0
    .org 0x54b1a - 0x85f4
L_00054b1a:
    bt L_00054b20
    .org 0x54b1c - 0x85f4
L_00054b1c:
    bra L_00054d28
    .org 0x54b1e - 0x85f4
L_00054b1e:
    nop
    .org 0x54b20 - 0x85f4
L_00054b20:
    mov.w L_00054b5a,r5
    .org 0x54b22 - 0x85f4
L_00054b22:
    mov.b @r5,r0
    .org 0x54b24 - 0x85f4
L_00054b24:
    tst #0x80,r0
    .org 0x54b26 - 0x85f4
L_00054b26:
    bt L_00054bc4
    .org 0x54b28 - 0x85f4
L_00054b28:
    tst r2,r2
    .org 0x54b2a - 0x85f4
L_00054b2a:
    bf L_00054b5e
    .org 0x54b2c - 0x85f4
L_00054b2c:
    mov.l L_00054c30,r14
    .org 0x54b2e - 0x85f4
L_00054b2e:
    mov #0x4,r6
    .org 0x54b30 - 0x85f4
L_00054b30:
    mov.w L_00054b5c,r0
    .org 0x54b32 - 0x85f4
L_00054b32:
    mov.b @(r0,r14),r2
    .org 0x54b34 - 0x85f4
L_00054b34:
    cmp/hi r6,r2
    .org 0x54b36 - 0x85f4
L_00054b36:
    bt L_00054b5e
    .org 0x54b38 - 0x85f4
L_00054b38:
    bsr L_00054d3e
    .org 0x54b3a - 0x85f4
L_00054b3a:
    mov #0x4,r4
    .org 0x54b3c - 0x85f4
L_00054b3c:
    mov.l L_00054c30,r3
    .org 0x54b3e - 0x85f4
L_00054b3e:
    mov.w L_00054b5c,r0
    .org 0x54b40 - 0x85f4
L_00054b40:
    mov.b @(r0,r3),r0
    .org 0x54b42 - 0x85f4
L_00054b42:
    cmp/eq #0x4,r0
    .org 0x54b44 - 0x85f4
L_00054b44:
    bf L_00054b62
    .org 0x54b46 - 0x85f4
L_00054b46:
    mov.w L_00054b52,r6
    .org 0x54b48 - 0x85f4
L_00054b48:
    mov.w L_00054b52,r5
    .org 0x54b4a - 0x85f4
L_00054b4a:
    mov.b @(0x4,r6),r0
    .org 0x54b4c - 0x85f4
L_00054b4c:
    or #0x80,r0
    .org 0x54b4e - 0x85f4
L_00054b4e:
    bra L_00054b62
    .org 0x54b50 - 0x85f4
L_00054b50:
    mov.b r0,@(0x4,r5)
    .org 0x54b52 - 0x85f4
L_00054b52:
    .word 0x8510
    .org 0x54b54 - 0x85f4
L_00054b54:
    .word 0x029a
    .org 0x54b56 - 0x85f4
L_00054b56:
    .word 0x022a
    .org 0x54b58 - 0x85f4
L_00054b58:
    .word 0x0229
    .org 0x54b5a - 0x85f4
L_00054b5a:
    .word 0x84ec
    .org 0x54b5c - 0x85f4
L_00054b5c:
    .word 0x02a4
    .org 0x54b5e - 0x85f4
L_00054b5e:
    bsr L_00054d3e
    .org 0x54b60 - 0x85f4
L_00054b60:
    mov #0x3,r4
    .org 0x54b62 - 0x85f4
L_00054b62:
    mov.b @(0xc1,gbr),r0
    .org 0x54b64 - 0x85f4
L_00054b64:
    mov.l L_00054c30,r14
    .org 0x54b66 - 0x85f4
L_00054b66:
    mov r0,r2
    .org 0x54b68 - 0x85f4
L_00054b68:
    mov.l r0,@(0x14,r15)
    .org 0x54b6a - 0x85f4
L_00054b6a:
    mov.w L_00054c1a,r0
    .org 0x54b6c - 0x85f4
L_00054b6c:
    mov.l L_00054c40,r5
    .org 0x54b6e - 0x85f4
L_00054b6e:
    mov.b @(r0,r14),r4
    .org 0x54b70 - 0x85f4
L_00054b70:
    or r4,r2
    .org 0x54b72 - 0x85f4
L_00054b72:
    mov r2,r0
    .org 0x54b74 - 0x85f4
L_00054b74:
    mov.b r0,@(0xc1,gbr)
    .org 0x54b76 - 0x85f4
L_00054b76:
    mov.w L_00054c1c,r0
    .org 0x54b78 - 0x85f4
L_00054b78:
    mov.b @(r0,r5),r2
    .org 0x54b7a - 0x85f4
L_00054b7a:
    or r4,r2
    .org 0x54b7c - 0x85f4
L_00054b7c:
    mov.b r2,@(r0,r5)
    .org 0x54b7e - 0x85f4
L_00054b7e:
    mov.w L_00054c1e,r0
    .org 0x54b80 - 0x85f4
L_00054b80:
    mov.b @(r0,r5),r2
    .org 0x54b82 - 0x85f4
L_00054b82:
    or r4,r2
    .org 0x54b84 - 0x85f4
L_00054b84:
    mov.b r2,@(r0,r5)
    .org 0x54b86 - 0x85f4
L_00054b86:
    not r4,r2
    .org 0x54b88 - 0x85f4
L_00054b88:
    mov.w L_00054c20,r0
    .org 0x54b8a - 0x85f4
L_00054b8a:
    mov.b @(r0,r5),r6
    .org 0x54b8c - 0x85f4
L_00054b8c:
    and r2,r6
    .org 0x54b8e - 0x85f4
L_00054b8e:
    mov.b r6,@(r0,r5)
    .org 0x54b90 - 0x85f4
L_00054b90:
    mov.l L_00054c4c,r5
    .org 0x54b92 - 0x85f4
L_00054b92:
    mov.b @r5,r0
    .org 0x54b94 - 0x85f4
L_00054b94:
    tst #0x8,r0
    .org 0x54b96 - 0x85f4
L_00054b96:
    bt L_00054baa
    .org 0x54b98 - 0x85f4
L_00054b98:
    mov.l L_00054c40,r6
    .org 0x54b9a - 0x85f4
L_00054b9a:
    mov.w L_00054c22,r0
    .org 0x54b9c - 0x85f4
L_00054b9c:
    mov.b @(r0,r6),r2
    .org 0x54b9e - 0x85f4
L_00054b9e:
    or r4,r2
    .org 0x54ba0 - 0x85f4
L_00054ba0:
    mov.b r2,@(r0,r6)
    .org 0x54ba2 - 0x85f4
L_00054ba2:
    mov.w L_00054c24,r0
    .org 0x54ba4 - 0x85f4
L_00054ba4:
    mov.b @(r0,r6),r2
    .org 0x54ba6 - 0x85f4
L_00054ba6:
    or r4,r2
    .org 0x54ba8 - 0x85f4
L_00054ba8:
    mov.b r2,@(r0,r6)
    .org 0x54baa - 0x85f4
L_00054baa:
    mov.l L_00054c30,r5
    .org 0x54bac - 0x85f4
L_00054bac:
    mov.w L_00054c26,r2
    .org 0x54bae - 0x85f4
L_00054bae:
    add r2,r5
    .org 0x54bb0 - 0x85f4
L_00054bb0:
    mov.l L_00054c50,r2
    .org 0x54bb2 - 0x85f4
L_00054bb2:
    jsr @r2
    .org 0x54bb4 - 0x85f4
L_00054bb4:
    nop
    .org 0x54bb6 - 0x85f4
L_00054bb6:
    mov.w L_00054c28,r5
    .org 0x54bb8 - 0x85f4
L_00054bb8:
    mov #0x22,r0
    .org 0x54bba - 0x85f4
L_00054bba:
    mov #-0x2,r4
    .org 0x54bbc - 0x85f4
L_00054bbc:
    mov.w @(r0,r5),r6
    .org 0x54bbe - 0x85f4
L_00054bbe:
    extu.w r6,r6
    .org 0x54bc0 - 0x85f4
L_00054bc0:
    and r4,r6
    .org 0x54bc2 - 0x85f4
L_00054bc2:
    mov.w r6,@(r0,r5)
    .org 0x54bc4 - 0x85f4
L_00054bc4:
    mov.l L_00054c30,r14
    .org 0x54bc6 - 0x85f4
L_00054bc6:
    mov.w L_00054c2a,r0
    .org 0x54bc8 - 0x85f4
L_00054bc8:
    mov.l L_00054c44,r4
    .org 0x54bca - 0x85f4
L_00054bca:
    mov.b @(r0,r14),r6
    .org 0x54bcc - 0x85f4
L_00054bcc:
    mov.b @(0x3,r4),r0
    .org 0x54bce - 0x85f4
L_00054bce:
    extu.b r6,r6
    .org 0x54bd0 - 0x85f4
L_00054bd0:
    sub r9,r6
    .org 0x54bd2 - 0x85f4
L_00054bd2:
    extu.b r0,r5
    .org 0x54bd4 - 0x85f4
L_00054bd4:
    tst r6,r6
    .org 0x54bd6 - 0x85f4
L_00054bd6:
    shll2 r5
    .org 0x54bd8 - 0x85f4
L_00054bd8:
    bf/s L_00054c0a
    .org 0x54bda - 0x85f4
L_00054bda:
    mov.l r5,@(0x8,r15)
    .org 0x54bdc - 0x85f4
L_00054bdc:
    mov.w L_00054c1a,r0
    .org 0x54bde - 0x85f4
L_00054bde:
    mov #0x0,r2
    .org 0x54be0 - 0x85f4
L_00054be0:
    mov #0x6,r5
    .org 0x54be2 - 0x85f4
L_00054be2:
    mov.b r2,@(r0,r14)
    .org 0x54be4 - 0x85f4
L_00054be4:
    mov.w L_00054c2c,r0
    .org 0x54be6 - 0x85f4
L_00054be6:
    mov.b @(r0,r14),r2
    .org 0x54be8 - 0x85f4
L_00054be8:
    extu.b r2,r6
    .org 0x54bea - 0x85f4
L_00054bea:
    add #0x1,r6
    .org 0x54bec - 0x85f4
L_00054bec:
    cmp/ge r5,r6
    .org 0x54bee - 0x85f4
L_00054bee:
    bf L_00054bf2
    .org 0x54bf0 - 0x85f4
L_00054bf0:
    mov #0x0,r6
    .org 0x54bf2 - 0x85f4
L_00054bf2:
    mov.b @(0xc0,gbr),r0
    .org 0x54bf4 - 0x85f4
L_00054bf4:
    extu.b r0,r5
    .org 0x54bf6 - 0x85f4
L_00054bf6:
    cmp/eq r5,r6
    .org 0x54bf8 - 0x85f4
L_00054bf8:
    bt L_00054bfe
    .org 0x54bfa - 0x85f4
L_00054bfa:
    bra L_00054d0c
    .org 0x54bfc - 0x85f4
L_00054bfc:
    nop
    .org 0x54bfe - 0x85f4
L_00054bfe:
    mov.l L_00054c30,r14
    .org 0x54c00 - 0x85f4
L_00054c00:
    add #0x7,r8
    .org 0x54c02 - 0x85f4
L_00054c02:
    mov.w L_00054c2c,r0
    .org 0x54c04 - 0x85f4
L_00054c04:
    mov.b r5,@(r0,r14)
    .org 0x54c06 - 0x85f4
L_00054c06:
    bra L_00054d06
    .org 0x54c08 - 0x85f4
L_00054c08:
    mov r5,r0
    .org 0x54c0a - 0x85f4
L_00054c0a:
    cmp/pz r6
    .org 0x54c0c - 0x85f4
L_00054c0c:
    bt L_00054c54
    .org 0x54c0e - 0x85f4
L_00054c0e:
    mov.l L_00054c30,r3
    .org 0x54c10 - 0x85f4
L_00054c10:
    mov #0x0,r2
    .org 0x54c12 - 0x85f4
L_00054c12:
    mov.w L_00054c1a,r0
    .org 0x54c14 - 0x85f4
L_00054c14:
    mov.b r2,@(r0,r3)
    .org 0x54c16 - 0x85f4
L_00054c16:
    bra L_00054d0c
    .org 0x54c18 - 0x85f4
L_00054c18:
    nop
    .org 0x54c1a - 0x85f4
L_00054c1a:
    .word 0x0234
    .org 0x54c1c - 0x85f4
L_00054c1c:
    .word 0x02f2
    .org 0x54c1e - 0x85f4
L_00054c1e:
    .word 0x0472
    .org 0x54c20 - 0x85f4
L_00054c20:
    .word 0x06a9
    .org 0x54c22 - 0x85f4
L_00054c22:
    .word 0x0237
    .org 0x54c24 - 0x85f4
L_00054c24:
    .word 0x0236
    .org 0x54c26 - 0x85f4
L_00054c26:
    .word 0x025a
    .org 0x54c28 - 0x85f4
L_00054c28:
    .word 0xf440
    .org 0x54c2a - 0x85f4
L_00054c2a:
    .word 0x0229
    .org 0x54c2c - 0x85f4
L_00054c2c:
    .word 0x022a
    .org 0x54c30 - 0x85f4
L_00054c30:
    .long 0xffff1ff4
    .org 0x54c34 - 0x85f4
L_00054c34:
    .long 0xffff4555
    .org 0x54c38 - 0x85f4
L_00054c38:
    .long 0xffff11d4
    .org 0x54c3c - 0x85f4
L_00054c3c:
    .long 0x0002268e
    .org 0x54c40 - 0x85f4
L_00054c40:
    .long 0xffff128c
    .org 0x54c44 - 0x85f4
L_00054c44:
    .long 0xffff2330
    .org 0x54c48 - 0x85f4
L_00054c48:
    .long 0xffff24c8
    .org 0x54c4c - 0x85f4
L_00054c4c:
    .long 0x00008d92
    .org 0x54c50 - 0x85f4
L_00054c50:
    .long 0x0002c13c
    .org 0x54c54 - 0x85f4
L_00054c54:
    extu.b r6,r10
    .org 0x54c56 - 0x85f4
L_00054c56:
    mov #0x0,r11
    .org 0x54c58 - 0x85f4
L_00054c58:
    cmp/pl r10
    .org 0x54c5a - 0x85f4
L_00054c5a:
    mov.l r11,@(0xc,r15)
    .org 0x54c5c - 0x85f4
L_00054c5c:
    mov r11,r6
    .org 0x54c5e - 0x85f4
L_00054c5e:
    bf/s L_00054cc8
    .org 0x54c60 - 0x85f4
L_00054c60:
    mov.l r11,@(0x10,r15)
    .org 0x54c62 - 0x85f4
L_00054c62:
    mov.l L_00054e8c,r3
    .org 0x54c64 - 0x85f4
L_00054c64:
    mov.w L_00054dbe,r0
    .org 0x54c66 - 0x85f4
L_00054c66:
    mov.l L_00054e90,r2
    .org 0x54c68 - 0x85f4
L_00054c68:
    mov.b @(r0,r3),r12
    .org 0x54c6a - 0x85f4
L_00054c6a:
    mov.b @(0xc1,gbr),r0
    .org 0x54c6c - 0x85f4
L_00054c6c:
    mov.l r9,@r15
    .org 0x54c6e - 0x85f4
L_00054c6e:
    mov #0x6,r9
    .org 0x54c70 - 0x85f4
L_00054c70:
    mov r0,r7
    .org 0x54c72 - 0x85f4
L_00054c72:
    mov.w L_00054dc0,r0
    .org 0x54c74 - 0x85f4
L_00054c74:
    mov.b @(r0,r2),r13
    .org 0x54c76 - 0x85f4
L_00054c76:
    mov.w L_00054dc2,r0
    .org 0x54c78 - 0x85f4
L_00054c78:
    mov.b @(r0,r2),r14
    .org 0x54c7a - 0x85f4
L_00054c7a:
    mov.w L_00054dc4,r0
    .org 0x54c7c - 0x85f4
L_00054c7c:
    mov.b @(r0,r2),r4
    .org 0x54c7e - 0x85f4
L_00054c7e:
    mov.l L_00054e8c,r3
    .org 0x54c80 - 0x85f4
L_00054c80:
    add #0x1,r12
    .org 0x54c82 - 0x85f4
L_00054c82:
    mov.w L_00054dbe,r0
    .org 0x54c84 - 0x85f4
L_00054c84:
    mov.b r12,@(r0,r3)
    .org 0x54c86 - 0x85f4
L_00054c86:
    extu.b r12,r12
    .org 0x54c88 - 0x85f4
L_00054c88:
    cmp/ge r9,r12
    .org 0x54c8a - 0x85f4
L_00054c8a:
    bf L_00054c92
    .org 0x54c8c - 0x85f4
L_00054c8c:
    mov.l L_00054e8c,r3
    .org 0x54c8e - 0x85f4
L_00054c8e:
    mov #0x0,r12
    .org 0x54c90 - 0x85f4
L_00054c90:
    mov.b r12,@(r0,r3)
    .org 0x54c92 - 0x85f4
L_00054c92:
    mov r8,r2
    .org 0x54c94 - 0x85f4
L_00054c94:
    add #0x7,r2
    .org 0x54c96 - 0x85f4
L_00054c96:
    extu.b r12,r12
    .org 0x54c98 - 0x85f4
L_00054c98:
    mov r12,r0
    .org 0x54c9a - 0x85f4
L_00054c9a:
    mov.b @(r0,r2),r5
    .org 0x54c9c - 0x85f4
L_00054c9c:
    add #0x1,r11
    .org 0x54c9e - 0x85f4
L_00054c9e:
    extu.b r5,r2
    .org 0x54ca0 - 0x85f4
L_00054ca0:
    cmp/ge r10,r11
    .org 0x54ca2 - 0x85f4
L_00054ca2:
    or r2,r6
    .org 0x54ca4 - 0x85f4
L_00054ca4:
    not r6,r2
    .org 0x54ca6 - 0x85f4
L_00054ca6:
    mov.l r6,@(0x10,r15)
    .org 0x54ca8 - 0x85f4
L_00054ca8:
    or r6,r7
    .org 0x54caa - 0x85f4
L_00054caa:
    or r6,r13
    .org 0x54cac - 0x85f4
L_00054cac:
    and r2,r4
    .org 0x54cae - 0x85f4
L_00054cae:
    bf/s L_00054c7e
    .org 0x54cb0 - 0x85f4
L_00054cb0:
    or r6,r14
    .org 0x54cb2 - 0x85f4
L_00054cb2:
    mov.l L_00054e90,r2
    .org 0x54cb4 - 0x85f4
L_00054cb4:
    mov.w L_00054dc4,r0
    .org 0x54cb6 - 0x85f4
L_00054cb6:
    mov.l r11,@(0xc,r15)
    .org 0x54cb8 - 0x85f4
L_00054cb8:
    mov.b r4,@(r0,r2)
    .org 0x54cba - 0x85f4
L_00054cba:
    mov.w L_00054dc2,r0
    .org 0x54cbc - 0x85f4
L_00054cbc:
    mov.l @r15,r9
    .org 0x54cbe - 0x85f4
L_00054cbe:
    mov.b r14,@(r0,r2)
    .org 0x54cc0 - 0x85f4
L_00054cc0:
    mov.w L_00054dc0,r0
    .org 0x54cc2 - 0x85f4
L_00054cc2:
    mov.b r13,@(r0,r2)
    .org 0x54cc4 - 0x85f4
L_00054cc4:
    mov r7,r0
    .org 0x54cc6 - 0x85f4
L_00054cc6:
    mov.b r0,@(0xc1,gbr)
    .org 0x54cc8 - 0x85f4
L_00054cc8:
    mov.l L_00054e94,r5
    .org 0x54cca - 0x85f4
L_00054cca:
    mov.b @r5,r0
    .org 0x54ccc - 0x85f4
L_00054ccc:
    tst #0x8,r0
    .org 0x54cce - 0x85f4
L_00054cce:
    bt L_00054ce2
    .org 0x54cd0 - 0x85f4
L_00054cd0:
    mov.l L_00054e90,r3
    .org 0x54cd2 - 0x85f4
L_00054cd2:
    mov.w L_00054dc6,r0
    .org 0x54cd4 - 0x85f4
L_00054cd4:
    mov.b @(r0,r3),r2
    .org 0x54cd6 - 0x85f4
L_00054cd6:
    or r6,r2
    .org 0x54cd8 - 0x85f4
L_00054cd8:
    mov.b r2,@(r0,r3)
    .org 0x54cda - 0x85f4
L_00054cda:
    mov.w L_00054dc8,r0
    .org 0x54cdc - 0x85f4
L_00054cdc:
    mov.b @(r0,r3),r2
    .org 0x54cde - 0x85f4
L_00054cde:
    or r6,r2
    .org 0x54ce0 - 0x85f4
L_00054ce0:
    mov.b r2,@(r0,r3)
    .org 0x54ce2 - 0x85f4
L_00054ce2:
    mov.l L_00054e8c,r14
    .org 0x54ce4 - 0x85f4
L_00054ce4:
    mov #0x3,r4
    .org 0x54ce6 - 0x85f4
L_00054ce6:
    mov.w L_00054dca,r0
    .org 0x54ce8 - 0x85f4
L_00054ce8:
    add #0x7,r8
    .org 0x54cea - 0x85f4
L_00054cea:
    bsr L_00054d3e
    .org 0x54cec - 0x85f4
L_00054cec:
    mov.b r6,@(r0,r14)
    .org 0x54cee - 0x85f4
L_00054cee:
    mov.w L_00054dcc,r2
    .org 0x54cf0 - 0x85f4
L_00054cf0:
    mov r14,r5
    .org 0x54cf2 - 0x85f4
L_00054cf2:
    add r2,r5
    .org 0x54cf4 - 0x85f4
L_00054cf4:
    mov.l L_00054e98,r2
    .org 0x54cf6 - 0x85f4
L_00054cf6:
    jsr @r2
    .org 0x54cf8 - 0x85f4
L_00054cf8:
    mov.l @(0x10,r15),r4
    .org 0x54cfa - 0x85f4
L_00054cfa:
    mov.b @(0xc0,gbr),r0
    .org 0x54cfc - 0x85f4
L_00054cfc:
    mov r0,r6
    .org 0x54cfe - 0x85f4
L_00054cfe:
    mov r0,r2
    .org 0x54d00 - 0x85f4
L_00054d00:
    mov.w L_00054dbe,r0
    .org 0x54d02 - 0x85f4
L_00054d02:
    mov.b r2,@(r0,r14)
    .org 0x54d04 - 0x85f4
L_00054d04:
    extu.b r6,r0
    .org 0x54d06 - 0x85f4
L_00054d06:
    mov.b @(r0,r8),r2
    .org 0x54d08 - 0x85f4
L_00054d08:
    mov.w L_00054dca,r0
    .org 0x54d0a - 0x85f4
L_00054d0a:
    mov.b r2,@(r0,r14)
    .org 0x54d0c - 0x85f4
L_00054d0c:
    mov.l L_00054e8c,r3
    .org 0x54d0e - 0x85f4
L_00054d0e:
    mov.w L_00054dce,r0
    .org 0x54d10 - 0x85f4
L_00054d10:
    mov.l L_00054e9c,r6
    .org 0x54d12 - 0x85f4
L_00054d12:
    mov.b r9,@(r0,r3)
    .org 0x54d14 - 0x85f4
L_00054d14:
    mov.b @(0x5,r6),r0
    .org 0x54d16 - 0x85f4
L_00054d16:
    tst #0x1,r0
    .org 0x54d18 - 0x85f4
L_00054d18:
    bt L_00054d20
    .org 0x54d1a - 0x85f4
L_00054d1a:
    mov.l L_00054ea0,r2
    .org 0x54d1c - 0x85f4
L_00054d1c:
    bra L_00054d24
    .org 0x54d1e - 0x85f4
L_00054d1e:
    mov #0x34,r4
    .org 0x54d20 - 0x85f4
L_00054d20:
    mov.l @(0x8,r15),r4
    .org 0x54d22 - 0x85f4
L_00054d22:
    mov.l L_00054ea0,r2
    .org 0x54d24 - 0x85f4
L_00054d24:
    jsr @r2
    .org 0x54d26 - 0x85f4
L_00054d26:
    nop
    .org 0x54d28 - 0x85f4
L_00054d28:
    add #0x18,r15
    .org 0x54d2a - 0x85f4
L_00054d2a:
    ldc.l @r15+,gbr
    .org 0x54d2c - 0x85f4
L_00054d2c:
    lds.l @r15+,pr
    .org 0x54d2e - 0x85f4
L_00054d2e:
    mov.l @r15+,r14
    .org 0x54d30 - 0x85f4
L_00054d30:
    mov.l @r15+,r13
    .org 0x54d32 - 0x85f4
L_00054d32:
    mov.l @r15+,r12
    .org 0x54d34 - 0x85f4
L_00054d34:
    mov.l @r15+,r11
    .org 0x54d36 - 0x85f4
L_00054d36:
    mov.l @r15+,r10
    .org 0x54d38 - 0x85f4
L_00054d38:
    mov.l @r15+,r9
    .org 0x54d3a - 0x85f4
L_00054d3a:
    rts
    .org 0x54d3c - 0x85f4
L_00054d3c:
    mov.l @r15+,r8
    .org 0x54d3e - 0x85f4
L_00054d3e:
    mov.l r14,@-r15
    .org 0x54d40 - 0x85f4
L_00054d40:
    sts.l pr,@-r15
    .org 0x54d42 - 0x85f4
L_00054d42:
    sts.l macl,@-r15
    .org 0x54d44 - 0x85f4
L_00054d44:
    stc.l gbr,@-r15
    .org 0x54d46 - 0x85f4
L_00054d46:
    mov.l L_00054ea4,r0
    .org 0x54d48 - 0x85f4
L_00054d48:
    ldc r0,gbr
    .org 0x54d4a - 0x85f4
L_00054d4a:
    add #-0x4,r15
    .org 0x54d4c - 0x85f4
L_00054d4c:
    mov.l L_00054ea8,r6
    .org 0x54d4e - 0x85f4
L_00054d4e:
    mov.b @(0x4,r6),r0
    .org 0x54d50 - 0x85f4
L_00054d50:
    tst #0x2,r0
    .org 0x54d52 - 0x85f4
L_00054d52:
    bt/s L_00054d5a
    .org 0x54d54 - 0x85f4
L_00054d54:
    extu.b r4,r4
    .org 0x54d56 - 0x85f4
L_00054d56:
    bra L_00054e5a
    .org 0x54d58 - 0x85f4
L_00054d58:
    nop
    .org 0x54d5a - 0x85f4
L_00054d5a:
    mov.l L_00054eac,r6
    .org 0x54d5c - 0x85f4
L_00054d5c:
    mov #0x30,r0
    .org 0x54d5e - 0x85f4
L_00054d5e:
    mov.b @(r0,r6),r0
    .org 0x54d60 - 0x85f4
L_00054d60:
    tst #0x40,r0
    .org 0x54d62 - 0x85f4
L_00054d62:
    bf L_00054e5a
    .org 0x54d64 - 0x85f4
L_00054d64:
    tst r4,r4
    .org 0x54d66 - 0x85f4
L_00054d66:
    bf L_00054d80
    .org 0x54d68 - 0x85f4
L_00054d68:
    mov.l L_00054e8c,r2
    .org 0x54d6a - 0x85f4
L_00054d6a:
    mov #0x6,r6
    .org 0x54d6c - 0x85f4
L_00054d6c:
    mov.w L_00054dcc,r5
    .org 0x54d6e - 0x85f4
L_00054d6e:
    mov.w @(0x5a,gbr),r0
    .org 0x54d70 - 0x85f4
L_00054d70:
    add r5,r2
    .org 0x54d72 - 0x85f4
L_00054d72:
    mov r0,r5
    .org 0x54d74 - 0x85f4
L_00054d74:
    dt r6
    .org 0x54d76 - 0x85f4
L_00054d76:
    mov.w r5,@r2
    .org 0x54d78 - 0x85f4
L_00054d78:
    bf/s L_00054d74
    .org 0x54d7a - 0x85f4
L_00054d7a:
    add #0x2,r2
    .org 0x54d7c - 0x85f4
L_00054d7c:
    bra L_00054e6e
    .org 0x54d7e - 0x85f4
L_00054d7e:
    nop
    .org 0x54d80 - 0x85f4
L_00054d80:
    mov r4,r0
    .org 0x54d82 - 0x85f4
L_00054d82:
    cmp/eq #0x1,r0
    .org 0x54d84 - 0x85f4
L_00054d84:
    bt L_00054dd0
    .org 0x54d86 - 0x85f4
L_00054d86:
    cmp/eq #0x2,r0
    .org 0x54d88 - 0x85f4
L_00054d88:
    bt L_00054dd0
    .org 0x54d8a - 0x85f4
L_00054d8a:
    mov r4,r0
    .org 0x54d8c - 0x85f4
L_00054d8c:
    cmp/eq #0x4,r0
    .org 0x54d8e - 0x85f4
L_00054d8e:
    bt L_00054dd0
    .org 0x54d90 - 0x85f4
L_00054d90:
    mov.w @(0x60,gbr),r0
    .org 0x54d92 - 0x85f4
L_00054d92:
    mov #0x6,r7
    .org 0x54d94 - 0x85f4
L_00054d94:
    mov.l L_00054e8c,r5
    .org 0x54d96 - 0x85f4
L_00054d96:
    extu.w r0,r2
    .org 0x54d98 - 0x85f4
L_00054d98:
    mov.l r2,@r15
    .org 0x54d9a - 0x85f4
L_00054d9a:
    mov.w L_00054dcc,r2
    .org 0x54d9c - 0x85f4
L_00054d9c:
    stc gbr,r4
    .org 0x54d9e - 0x85f4
L_00054d9e:
    add r2,r5
    .org 0x54da0 - 0x85f4
L_00054da0:
    mov.l @r15,r14
    .org 0x54da2 - 0x85f4
L_00054da2:
    add #0x18,r4
    .org 0x54da4 - 0x85f4
L_00054da4:
    mov.w @r4,r2
    .org 0x54da6 - 0x85f4
L_00054da6:
    extu.w r2,r2
    .org 0x54da8 - 0x85f4
L_00054da8:
    cmp/ge r14,r2
    .org 0x54daa - 0x85f4
L_00054daa:
    bt L_00054db0
    .org 0x54dac - 0x85f4
L_00054dac:
    mov.w @(0x60,gbr),r0
    .org 0x54dae - 0x85f4
L_00054dae:
    mov r0,r2
    .org 0x54db0 - 0x85f4
L_00054db0:
    dt r7
    .org 0x54db2 - 0x85f4
L_00054db2:
    mov.w r2,@r5
    .org 0x54db4 - 0x85f4
L_00054db4:
    add #0x2,r4
    .org 0x54db6 - 0x85f4
L_00054db6:
    bf/s L_00054da4
    .org 0x54db8 - 0x85f4
L_00054db8:
    add #0x2,r5
    .org 0x54dba - 0x85f4
L_00054dba:
    bra L_00054e6e
    .org 0x54dbc - 0x85f4
L_00054dbc:
    nop
    .org 0x54dbe - 0x85f4
L_00054dbe:
    .word 0x022a
    .org 0x54dc0 - 0x85f4
L_00054dc0:
    .word 0x02f2
    .org 0x54dc2 - 0x85f4
L_00054dc2:
    .word 0x0472
    .org 0x54dc4 - 0x85f4
L_00054dc4:
    .word 0x06a9
    .org 0x54dc6 - 0x85f4
L_00054dc6:
    .word 0x0237
    .org 0x54dc8 - 0x85f4
L_00054dc8:
    .word 0x0236
    .org 0x54dca - 0x85f4
L_00054dca:
    .word 0x0234
    .org 0x54dcc - 0x85f4
L_00054dcc:
    .word 0x025a
    .org 0x54dce - 0x85f4
L_00054dce:
    .word 0x0229
    .org 0x54dd0 - 0x85f4
L_00054dd0:
    mov.l L_00054eb0,r5
    .org 0x54dd2 - 0x85f4
L_00054dd2:
    mov.w @(0x7a,gbr),r0
    .org 0x54dd4 - 0x85f4
L_00054dd4:
    mov.w @r5,r2
    .org 0x54dd6 - 0x85f4
L_00054dd6:
    extu.w r2,r2
    .org 0x54dd8 - 0x85f4
L_00054dd8:
    mov #0x64,r6
    .org 0x54dda - 0x85f4
L_00054dda:
    mul.l r2,r6
    .org 0x54ddc - 0x85f4
L_00054ddc:
    sts macl,r2
    .org 0x54dde - 0x85f4
L_00054dde:
    cmp/pz r2
    .org 0x54de0 - 0x85f4
L_00054de0:
    bt/s L_00054dea
    .org 0x54de2 - 0x85f4
L_00054de2:
    extu.w r0,r5
    .org 0x54de4 - 0x85f4
L_00054de4:
    mov #-0x1,r6
    .org 0x54de6 - 0x85f4
L_00054de6:
    extu.b r6,r6
    .org 0x54de8 - 0x85f4
L_00054de8:
    add r6,r2
    .org 0x54dea - 0x85f4
L_00054dea:
    mov r2,r6
    .org 0x54dec - 0x85f4
L_00054dec:
    shlr8 r6
    .org 0x54dee - 0x85f4
L_00054dee:
    swap.w r6,r2
    .org 0x54df0 - 0x85f4
L_00054df0:
    exts.b r2,r6
    .org 0x54df2 - 0x85f4
L_00054df2:
    xtrct r6,r2
    .org 0x54df4 - 0x85f4
L_00054df4:
    add r2,r5
    .org 0x54df6 - 0x85f4
L_00054df6:
    mov #-0x1,r2
    .org 0x54df8 - 0x85f4
L_00054df8:
    extu.w r2,r2
    .org 0x54dfa - 0x85f4
L_00054dfa:
    cmp/hi r2,r5
    .org 0x54dfc - 0x85f4
L_00054dfc:
    bf L_00054e00
    .org 0x54dfe - 0x85f4
L_00054dfe:
    mov r2,r5
    .org 0x54e00 - 0x85f4
L_00054e00:
    mov.w @(0x58,gbr),r0
    .org 0x54e02 - 0x85f4
L_00054e02:
    extu.w r0,r6
    .org 0x54e04 - 0x85f4
L_00054e04:
    mov.w @(0x56,gbr),r0
    .org 0x54e06 - 0x85f4
L_00054e06:
    cmp/hi r5,r6
    .org 0x54e08 - 0x85f4
L_00054e08:
    bf/s L_00054e18
    .org 0x54e0a - 0x85f4
L_00054e0a:
    extu.w r0,r5
    .org 0x54e0c - 0x85f4
L_00054e0c:
    mov.w @(0x5a,gbr),r0
    .org 0x54e0e - 0x85f4
L_00054e0e:
    extu.w r0,r2
    .org 0x54e10 - 0x85f4
L_00054e10:
    sub r2,r5
    .org 0x54e12 - 0x85f4
L_00054e12:
    cmp/pz r5
    .org 0x54e14 - 0x85f4
L_00054e14:
    bt L_00054e18
    .org 0x54e16 - 0x85f4
L_00054e16:
    mov #0x0,r5
    .org 0x54e18 - 0x85f4
L_00054e18:
    mov r4,r0
    .org 0x54e1a - 0x85f4
L_00054e1a:
    cmp/eq #0x1,r0
    .org 0x54e1c - 0x85f4
L_00054e1c:
    bf L_00054e2a
    .org 0x54e1e - 0x85f4
L_00054e1e:
    mov.w @(0x5c,gbr),r0
    .org 0x54e20 - 0x85f4
L_00054e20:
    extu.w r0,r6
    .org 0x54e22 - 0x85f4
L_00054e22:
    cmp/ge r6,r5
    .org 0x54e24 - 0x85f4
L_00054e24:
    bf L_00054e44
    .org 0x54e26 - 0x85f4
L_00054e26:
    bra L_00054e46
    .org 0x54e28 - 0x85f4
L_00054e28:
    nop
    .org 0x54e2a - 0x85f4
L_00054e2a:
    mov r4,r0
    .org 0x54e2c - 0x85f4
L_00054e2c:
    cmp/eq #0x2,r0
    .org 0x54e2e - 0x85f4
L_00054e2e:
    bf L_00054e3c
    .org 0x54e30 - 0x85f4
L_00054e30:
    mov.w @(0x5e,gbr),r0
    .org 0x54e32 - 0x85f4
L_00054e32:
    extu.w r0,r6
    .org 0x54e34 - 0x85f4
L_00054e34:
    cmp/ge r6,r5
    .org 0x54e36 - 0x85f4
L_00054e36:
    bf L_00054e44
    .org 0x54e38 - 0x85f4
L_00054e38:
    bra L_00054e46
    .org 0x54e3a - 0x85f4
L_00054e3a:
    nop
    .org 0x54e3c - 0x85f4
L_00054e3c:
    mov.w @(0x62,gbr),r0
    .org 0x54e3e - 0x85f4
L_00054e3e:
    extu.w r0,r6
    .org 0x54e40 - 0x85f4
L_00054e40:
    cmp/ge r6,r5
    .org 0x54e42 - 0x85f4
L_00054e42:
    bt L_00054e46
    .org 0x54e44 - 0x85f4
L_00054e44:
    mov r6,r5
    .org 0x54e46 - 0x85f4
L_00054e46:
    mov.l L_00054e8c,r2
    .org 0x54e48 - 0x85f4
L_00054e48:
    mov #0x6,r6
    .org 0x54e4a - 0x85f4
L_00054e4a:
    mov.w L_00054e88,r4
    .org 0x54e4c - 0x85f4
L_00054e4c:
    add r4,r2
    .org 0x54e4e - 0x85f4
L_00054e4e:
    dt r6
    .org 0x54e50 - 0x85f4
L_00054e50:
    mov.w r5,@r2
    .org 0x54e52 - 0x85f4
L_00054e52:
    bf/s L_00054e4e
    .org 0x54e54 - 0x85f4
L_00054e54:
    add #0x2,r2
    .org 0x54e56 - 0x85f4
L_00054e56:
    bra L_00054e6e
    .org 0x54e58 - 0x85f4
L_00054e58:
    nop
    .org 0x54e5a - 0x85f4
L_00054e5a:
    mov.l L_00054e8c,r2
    .org 0x54e5c - 0x85f4
L_00054e5c:
    mov #0x6,r6
    .org 0x54e5e - 0x85f4
L_00054e5e:
    mov.w L_00054e88,r5
    .org 0x54e60 - 0x85f4
L_00054e60:
    mov.w @(0x7a,gbr),r0
    .org 0x54e62 - 0x85f4
L_00054e62:
    add r5,r2
    .org 0x54e64 - 0x85f4
L_00054e64:
    mov r0,r5
    .org 0x54e66 - 0x85f4
L_00054e66:
    dt r6
    .org 0x54e68 - 0x85f4
L_00054e68:
    mov.w r5,@r2
    .org 0x54e6a - 0x85f4
L_00054e6a:
    bf/s L_00054e66
    .org 0x54e6c - 0x85f4
L_00054e6c:
    add #0x2,r2
    .org 0x54e6e - 0x85f4
L_00054e6e:
    mov.l L_00054e94,r6
    .org 0x54e70 - 0x85f4
L_00054e70:
    mov.b @r6,r0
    .org 0x54e72 - 0x85f4
L_00054e72:
    tst #0x8,r0
    .org 0x54e74 - 0x85f4
L_00054e74:
    bt L_00054e7c
    .org 0x54e76 - 0x85f4
L_00054e76:
    mov.l L_00054eb4,r2
    .org 0x54e78 - 0x85f4
L_00054e78:
    jsr @r2
    .org 0x54e7a - 0x85f4
L_00054e7a:
    nop
    .org 0x54e7c - 0x85f4
L_00054e7c:
    add #0x4,r15
    .org 0x54e7e - 0x85f4
L_00054e7e:
    ldc.l @r15+,gbr
    .org 0x54e80 - 0x85f4
L_00054e80:
    lds.l @r15+,macl
    .org 0x54e82 - 0x85f4
L_00054e82:
    lds.l @r15+,pr
    .org 0x54e84 - 0x85f4
L_00054e84:
    rts
    .org 0x54e86 - 0x85f4
L_00054e86:
    mov.l @r15+,r14
    .org 0x54e88 - 0x85f4
L_00054e88:
    .word 0x025a
    .org 0x54e8c - 0x85f4
L_00054e8c:
    .long 0xffff1ff4
    .org 0x54e90 - 0x85f4
L_00054e90:
    .long 0xffff128c
    .org 0x54e94 - 0x85f4
L_00054e94:
    .long 0x00008d92
    .org 0x54e98 - 0x85f4
L_00054e98:
    .long 0x0002c13c
    .org 0x54e9c - 0x85f4
L_00054e9c:
    .long 0xffff424c
    .org 0x54ea0 - 0x85f4
L_00054ea0:
    .long 0x0002b64a
    .org 0x54ea4 - 0x85f4
L_00054ea4:
    .long 0xffff2330
    .org 0x54ea8 - 0x85f4
L_00054ea8:
    .long 0xffff4188
    .org 0x54eac - 0x85f4
L_00054eac:
    .long 0xffff2470
    .org 0x54eb0 - 0x85f4
L_00054eb0:
    .long 0x000094e8
    .org 0x54eb4 - 0x85f4
L_00054eb4:
    .long 0x000571c0
    .org 0x571c0 - 0x85f4
L_000571c0:
    mov.l r8,@-r15
    .org 0x571c2 - 0x85f4
L_000571c2:
    mov.l r9,@-r15
    .org 0x571c4 - 0x85f4
L_000571c4:
    mov.l r10,@-r15
    .org 0x571c6 - 0x85f4
L_000571c6:
    mov.l r11,@-r15
    .org 0x571c8 - 0x85f4
L_000571c8:
    mov.l r12,@-r15
    .org 0x571ca - 0x85f4
L_000571ca:
    mov.l r13,@-r15
    .org 0x571cc - 0x85f4
L_000571cc:
    mov.l r14,@-r15
    .org 0x571ce - 0x85f4
L_000571ce:
    sts.l pr,@-r15
    .org 0x571d0 - 0x85f4
L_000571d0:
    sts.l macl,@-r15
    .org 0x571d2 - 0x85f4
L_000571d2:
    stc.l gbr,@-r15
    .org 0x571d4 - 0x85f4
L_000571d4:
    mov.l L_00057354,r0
    .org 0x571d6 - 0x85f4
L_000571d6:
    ldc r0,gbr
    .org 0x571d8 - 0x85f4
L_000571d8:
    mov.l L_00057358,r2
    .org 0x571da - 0x85f4
L_000571da:
    mov #0x0,r14
    .org 0x571dc - 0x85f4
L_000571dc:
    mov.w L_0005729c,r0
    .org 0x571de - 0x85f4
L_000571de:
    mov #0x1,r10
    .org 0x571e0 - 0x85f4
L_000571e0:
    mov.l L_0005735c,r11
    .org 0x571e2 - 0x85f4
L_000571e2:
    mov #0x6,r9
    .org 0x571e4 - 0x85f4
L_000571e4:
    mov.b @(r0,r2),r13
    .org 0x571e6 - 0x85f4
L_000571e6:
    mov #0x12,r0
    .org 0x571e8 - 0x85f4
L_000571e8:
    mov.l L_00057360,r2
    .org 0x571ea - 0x85f4
L_000571ea:
    mov.w L_0005729e,r8
    .org 0x571ec - 0x85f4
L_000571ec:
    mov.b @(r0,r2),r12
    .org 0x571ee - 0x85f4
L_000571ee:
    extu.b r14,r14
    .org 0x571f0 - 0x85f4
L_000571f0:
    mov r10,r0
    .org 0x571f2 - 0x85f4
L_000571f2:
    mov r14,r1
    .org 0x571f4 - 0x85f4
L_000571f4:
    jsr @r11
    .org 0x571f6 - 0x85f4
L_000571f6:
    extu.b r13,r13
    .org 0x571f8 - 0x85f4
L_000571f8:
    extu.b r0,r2
    .org 0x571fa - 0x85f4
L_000571fa:
    tst r2,r13
    .org 0x571fc - 0x85f4
L_000571fc:
    bt L_0005725c
    .org 0x571fe - 0x85f4
L_000571fe:
    stc gbr,r6
    .org 0x57200 - 0x85f4
L_00057200:
    extu.b r12,r12
    .org 0x57202 - 0x85f4
L_00057202:
    mov r14,r4
    .org 0x57204 - 0x85f4
L_00057204:
    shll r4
    .org 0x57206 - 0x85f4
L_00057206:
    tst r2,r12
    .org 0x57208 - 0x85f4
L_00057208:
    add r8,r6
    .org 0x5720a - 0x85f4
L_0005720a:
    mov r4,r0
    .org 0x5720c - 0x85f4
L_0005720c:
    mov #0x0,r5
    .org 0x5720e - 0x85f4
L_0005720e:
    bf/s L_0005725c
    .org 0x57210 - 0x85f4
L_00057210:
    mov.w r5,@(r0,r6)
    .org 0x57212 - 0x85f4
L_00057212:
    mov.l L_00057364,r3
    .org 0x57214 - 0x85f4
L_00057214:
    mov.l L_00057354,r5
    .org 0x57216 - 0x85f4
L_00057216:
    mov.b @(0x4,r3),r0
    .org 0x57218 - 0x85f4
L_00057218:
    tst r2,r0
    .org 0x5721a - 0x85f4
L_0005721a:
    bt L_0005724e
    .org 0x5721c - 0x85f4
L_0005721c:
    mov.w L_000572a0,r7
    .org 0x5721e - 0x85f4
L_0005721e:
    mov r5,r2
    .org 0x57220 - 0x85f4
L_00057220:
    mov.l L_00057368,r3
    .org 0x57222 - 0x85f4
L_00057222:
    mov r4,r0
    .org 0x57224 - 0x85f4
L_00057224:
    add r7,r2
    .org 0x57226 - 0x85f4
L_00057226:
    mov.w @(r0,r2),r6
    .org 0x57228 - 0x85f4
L_00057228:
    mov.b @r3,r2
    .org 0x5722a - 0x85f4
L_0005722a:
    extu.w r6,r6
    .org 0x5722c - 0x85f4
L_0005722c:
    extu.b r2,r1
    .org 0x5722e - 0x85f4
L_0005722e:
    mul.l r6,r1
    .org 0x57230 - 0x85f4
L_00057230:
    sts macl,r2
    .org 0x57232 - 0x85f4
L_00057232:
    cmp/pz r2
    .org 0x57234 - 0x85f4
L_00057234:
    bt L_0005723c
    .org 0x57236 - 0x85f4
L_00057236:
    mov #-0x1,r6
    .org 0x57238 - 0x85f4
L_00057238:
    extu.b r6,r6
    .org 0x5723a - 0x85f4
L_0005723a:
    add r6,r2
    .org 0x5723c - 0x85f4
L_0005723c:
    mov r2,r6
    .org 0x5723e - 0x85f4
L_0005723e:
    shlr8 r6
    .org 0x57240 - 0x85f4
L_00057240:
    swap.w r6,r2
    .org 0x57242 - 0x85f4
L_00057242:
    mov r4,r0
    .org 0x57244 - 0x85f4
L_00057244:
    exts.b r2,r6
    .org 0x57246 - 0x85f4
L_00057246:
    xtrct r6,r2
    .org 0x57248 - 0x85f4
L_00057248:
    add r7,r5
    .org 0x5724a - 0x85f4
L_0005724a:
    bra L_0005725c
    .org 0x5724c - 0x85f4
L_0005724c:
    mov.w r2,@(r0,r5)
    .org 0x5724e - 0x85f4
L_0005724e:
    mov.l L_0005736c,r2
    .org 0x57250 - 0x85f4
L_00057250:
    mov r4,r0
    .org 0x57252 - 0x85f4
L_00057252:
    mov.w L_000572a0,r7
    .org 0x57254 - 0x85f4
L_00057254:
    add #0x68,r2
    .org 0x57256 - 0x85f4
L_00057256:
    mov.w @(r0,r2),r6
    .org 0x57258 - 0x85f4
L_00057258:
    add r7,r5
    .org 0x5725a - 0x85f4
L_0005725a:
    mov.w r6,@(r0,r5)
    .org 0x5725c - 0x85f4
L_0005725c:
    add #0x1,r14
    .org 0x5725e - 0x85f4
L_0005725e:
    extu.b r14,r14
    .org 0x57260 - 0x85f4
L_00057260:
    cmp/ge r9,r14
    .org 0x57262 - 0x85f4
L_00057262:
    bf L_000571ee
    .org 0x57264 - 0x85f4
L_00057264:
    ldc.l @r15+,gbr
    .org 0x57266 - 0x85f4
L_00057266:
    lds.l @r15+,macl
    .org 0x57268 - 0x85f4
L_00057268:
    lds.l @r15+,pr
    .org 0x5726a - 0x85f4
L_0005726a:
    mov.l @r15+,r14
    .org 0x5726c - 0x85f4
L_0005726c:
    mov.l @r15+,r13
    .org 0x5726e - 0x85f4
L_0005726e:
    mov.l @r15+,r12
    .org 0x57270 - 0x85f4
L_00057270:
    mov.l @r15+,r11
    .org 0x57272 - 0x85f4
L_00057272:
    mov.l @r15+,r10
    .org 0x57274 - 0x85f4
L_00057274:
    mov.l @r15+,r9
    .org 0x57276 - 0x85f4
L_00057276:
    rts
    .org 0x57278 - 0x85f4
L_00057278:
    mov.l @r15+,r8
    .org 0x5729c - 0x85f4
L_0005729c:
    .word 0x0234
    .org 0x5729e - 0x85f4
L_0005729e:
    .word 0x01da
    .org 0x572a0 - 0x85f4
L_000572a0:
    .word 0x06d2
    .org 0x57354 - 0x85f4
L_00057354:
    .long 0xffff128c
    .org 0x57358 - 0x85f4
L_00057358:
    .long 0xffff1ff4
    .org 0x5735c - 0x85f4
L_0005735c:
    .long 0x000221bc
    .org 0x57360 - 0x85f4
L_00057360:
    .long 0xffff120e
    .org 0x57364 - 0x85f4
L_00057364:
    .long 0xffff22dc
    .org 0x57368 - 0x85f4
L_00057368:
    .long 0x000085f7
    .org 0x5736c - 0x85f4
L_0005736c:
    .long 0xffff2330
