! Exact post-acquisition subtraction, top-three and metric instructions.
    .section .text
    .balign 4
    .org 0x8618 - 0x8618
P_8618:
    .byte 0x00
    .org 0x8694 - 0x8618
P_8694:
    .byte 0x80
    .org 0x86a7 - 0x8618
P_86a7:
    .byte 0x80
    .org 0x86ac - 0x8618
P_86ac:
    .byte 0x80
    .org 0x8870 - 0x8618
P_8870:
    .byte 0x03
    .org 0x8b3d - 0x8618
P_8b3d:
    .byte 0x82
    .org 0x2219c - 0x8618
P_2219c:
    .long 0x0e0c0a08
    .long 0x06040200
    .long 0x201e1c1a
    .long 0x18161412
    .long 0x3432302e
    .long 0x2c2a2826
    .long 0x403e3c3a
    .long 0x4856626c
    .org 0x221bc - 0x8618
L_221bc:
    mov.l r2,@-r15
    .org 0x221be - 0x8618
L_221be:
    cmp/pz r1
    .org 0x221c0 - 0x8618
L_221c0:
    bf/s L_221f4
    .org 0x221c2 - 0x8618
L_221c2:
    mov #0x20,r2
    .org 0x221c4 - 0x8618
L_221c4:
    cmp/ge r2,r1
    .org 0x221c6 - 0x8618
L_221c6:
    bt L_221e0
    .org 0x221c8 - 0x8618
L_221c8:
    mov.l P_221dc,r2
    .org 0x221ca - 0x8618
L_221ca:
    add r1,r2
    .org 0x221cc - 0x8618
L_221cc:
    mov.b @r2,r2
    .org 0x221ce - 0x8618
L_221ce:
    mov.l P_221d8,r1
    .org 0x221d0 - 0x8618
L_221d0:
    add r2,r1
    .org 0x221d2 - 0x8618
L_221d2:
    jmp @r1
    .org 0x221d4 - 0x8618
L_221d4:
    nop
    .org 0x221d8 - 0x8618
P_221d8: .long 0x000221e6
P_221dc: .long 0x0002219c
    .org 0x221e0 - 0x8618
L_221e0:
    mov #0x0,r0
    .org 0x221e2 - 0x8618
L_221e2:
    rts
    .org 0x221e4 - 0x8618
L_221e4:
    mov.l @r15+,r2
    .org 0x221e6 - 0x8618
L_221e6:
    shll r0
    .org 0x221e8 - 0x8618
L_221e8:
    shll r0
    .org 0x221ea - 0x8618
L_221ea:
    shll r0
    .org 0x221ec - 0x8618
L_221ec:
    shll r0
    .org 0x221ee - 0x8618
L_221ee:
    shll r0
    .org 0x221f0 - 0x8618
L_221f0:
    shll r0
    .org 0x221f2 - 0x8618
L_221f2:
    shll r0
    .org 0x221f4 - 0x8618
L_221f4:
    rts
    .org 0x221f6 - 0x8618
L_221f6:
    mov.l @r15+,r2
    .org 0x49d88 - 0x8618
L_49d88:
    mov.l r8,@-r15
    .org 0x49d8a - 0x8618
L_49d8a:
    mov.l r9,@-r15
    .org 0x49d8c - 0x8618
L_49d8c:
    mov.l r10,@-r15
    .org 0x49d8e - 0x8618
L_49d8e:
    mov.l r11,@-r15
    .org 0x49d90 - 0x8618
L_49d90:
    mov.l r12,@-r15
    .org 0x49d92 - 0x8618
L_49d92:
    mov.l r13,@-r15
    .org 0x49d94 - 0x8618
L_49d94:
    mov.l r14,@-r15
    .org 0x49d96 - 0x8618
L_49d96:
    sts.l pr,@-r15
    .org 0x49d98 - 0x8618
L_49d98:
    add #-0x20,r15
    .org 0x49d9a - 0x8618
L_49d9a:
    mov.l P_49fc0,r2
    .org 0x49d9c - 0x8618
L_49d9c:
    mov #0x0,r14
    .org 0x49d9e - 0x8618
L_49d9e:
    mov r14,r11
    .org 0x49da0 - 0x8618
L_49da0:
    mov #0x8,r12
    .org 0x49da2 - 0x8618
L_49da2:
    mov.b @r2,r8
    .org 0x49da4 - 0x8618
L_49da4:
    mov r15,r13
    .org 0x49da6 - 0x8618
L_49da6:
    mov #0x1,r10
    .org 0x49da8 - 0x8618
L_49da8:
    mov.l P_49fc4,r9
    .org 0x49daa - 0x8618
L_49daa:
    extu.b r8,r8
    .org 0x49dac - 0x8618
L_49dac:
    extu.b r10,r10
    .org 0x49dae - 0x8618
L_49dae:
    mov r14,r1
    .org 0x49db0 - 0x8618
L_49db0:
    jsr @r9
    .org 0x49db2 - 0x8618
L_49db2:
    mov r10,r0
    .org 0x49db4 - 0x8618
L_49db4:
    tst r0,r8
    .org 0x49db6 - 0x8618
L_49db6:
    bt L_49e7c
    .org 0x49db8 - 0x8618
L_49db8:
    mov #-0x80,r2
    .org 0x49dba - 0x8618
L_49dba:
    shll8 r2
    .org 0x49dbc - 0x8618
L_49dbc:
    shll16 r2
    .org 0x49dbe - 0x8618
L_49dbe:
    mov.l r2,@r13
    .org 0x49dc0 - 0x8618
L_49dc0:
    dt r12
    .org 0x49dc2 - 0x8618
L_49dc2:
    add #0x1,r14
    .org 0x49dc4 - 0x8618
L_49dc4:
    add #0x4,r11
    .org 0x49dc6 - 0x8618
L_49dc6:
    bf/s L_49dac
    .org 0x49dc8 - 0x8618
L_49dc8:
    add #0x4,r13
    .org 0x49dca - 0x8618
L_49dca:
    mov #0x8,r12
    .org 0x49dcc - 0x8618
L_49dcc:
    mov r15,r14
    .org 0x49dce - 0x8618
L_49dce:
    mov r12,r9
    .org 0x49dd0 - 0x8618
L_49dd0:
    mov #0x0,r13
    .org 0x49dd2 - 0x8618
L_49dd2:
    mov r15,r7
    .org 0x49dd4 - 0x8618
L_49dd4:
    mov #0x7,r10
    .org 0x49dd6 - 0x8618
L_49dd6:
    mov #0x1c,r11
    .org 0x49dd8 - 0x8618
L_49dd8:
    cmp/ge r10,r13
    .org 0x49dda - 0x8618
L_49dda:
    bt/s L_49e08
    .org 0x49ddc - 0x8618
L_49ddc:
    mov r13,r4
    .org 0x49dde - 0x8618
L_49dde:
    shll2 r4
    .org 0x49de0 - 0x8618
L_49de0:
    mov r4,r5
    .org 0x49de2 - 0x8618
L_49de2:
    add r15,r5
    .org 0x49de4 - 0x8618
L_49de4:
    mov.l @r14,r6
    .org 0x49de6 - 0x8618
L_49de6:
    mov.l @r5,r2
    .org 0x49de8 - 0x8618
L_49de8:
    cmp/ge r2,r6
    .org 0x49dea - 0x8618
L_49dea:
    bt L_49df2
    .org 0x49dec - 0x8618
L_49dec:
    mov.l r6,@r5
    .org 0x49dee - 0x8618
L_49dee:
    mov r2,r6
    .org 0x49df0 - 0x8618
L_49df0:
    mov.l r2,@r14
    .org 0x49df2 - 0x8618
L_49df2:
    mov.l @(0x4,r5),r2
    .org 0x49df4 - 0x8618
L_49df4:
    cmp/ge r2,r6
    .org 0x49df6 - 0x8618
L_49df6:
    bt L_49dfc
    .org 0x49df8 - 0x8618
L_49df8:
    mov.l r6,@(0x4,r5)
    .org 0x49dfa - 0x8618
L_49dfa:
    mov.l r2,@r14
    .org 0x49dfc - 0x8618
L_49dfc:
    add #0x8,r4
    .org 0x49dfe - 0x8618
L_49dfe:
    cmp/ge r11,r4
    .org 0x49e00 - 0x8618
L_49e00:
    bf/s L_49de4
    .org 0x49e02 - 0x8618
L_49e02:
    add #0x8,r5
    .org 0x49e04 - 0x8618
L_49e04:
    shar r4
    .org 0x49e06 - 0x8618
L_49e06:
    shar r4
    .org 0x49e08 - 0x8618
L_49e08:
    cmp/ge r9,r4
    .org 0x49e0a - 0x8618
L_49e0a:
    bt L_49e1c
    .org 0x49e0c - 0x8618
L_49e0c:
    mov r4,r0
    .org 0x49e0e - 0x8618
L_49e0e:
    shll2 r0
    .org 0x49e10 - 0x8618
L_49e10:
    mov.l @r7,r4
    .org 0x49e12 - 0x8618
L_49e12:
    mov.l @(r0,r15),r5
    .org 0x49e14 - 0x8618
L_49e14:
    cmp/ge r5,r4
    .org 0x49e16 - 0x8618
L_49e16:
    bt L_49e1c
    .org 0x49e18 - 0x8618
L_49e18:
    mov.l r4,@(r0,r15)
    .org 0x49e1a - 0x8618
L_49e1a:
    mov.l r5,@r7
    .org 0x49e1c - 0x8618
L_49e1c:
    dt r12
    .org 0x49e1e - 0x8618
L_49e1e:
    add #0x1,r13
    .org 0x49e20 - 0x8618
L_49e20:
    add #0x4,r14
    .org 0x49e22 - 0x8618
L_49e22:
    bf/s L_49dd8
    .org 0x49e24 - 0x8618
L_49e24:
    add #0x4,r7
    .org 0x49e26 - 0x8618
L_49e26:
    mov.l P_49fc8,r2
    .org 0x49e28 - 0x8618
L_49e28:
    mov #0x0,r4
    .org 0x49e2a - 0x8618
L_49e2a:
    mov.b @r2,r7
    .org 0x49e2c - 0x8618
L_49e2c:
    extu.b r7,r7
    .org 0x49e2e - 0x8618
L_49e2e:
    cmp/pl r7
    .org 0x49e30 - 0x8618
L_49e30:
    bf/s L_49e4c
    .org 0x49e32 - 0x8618
L_49e32:
    mov r4,r5
    .org 0x49e34 - 0x8618
L_49e34:
    mov #-0x80,r14
    .org 0x49e36 - 0x8618
L_49e36:
    mov r15,r6
    .org 0x49e38 - 0x8618
L_49e38:
    shll8 r14
    .org 0x49e3a - 0x8618
L_49e3a:
    shll16 r14
    .org 0x49e3c - 0x8618
L_49e3c:
    mov.l @r6,r2
    .org 0x49e3e - 0x8618
L_49e3e:
    cmp/eq r14,r2
    .org 0x49e40 - 0x8618
L_49e40:
    bt L_49e44
    .org 0x49e42 - 0x8618
L_49e42:
    add r2,r4
    .org 0x49e44 - 0x8618
L_49e44:
    add #0x1,r5
    .org 0x49e46 - 0x8618
L_49e46:
    cmp/ge r7,r5
    .org 0x49e48 - 0x8618
L_49e48:
    bf/s L_49e3c
    .org 0x49e4a - 0x8618
L_49e4a:
    add #0x4,r6
    .org 0x49e4c - 0x8618
L_49e4c:
    mov.l P_49fcc,r6
    .org 0x49e4e - 0x8618
L_49e4e:
    mov.b @r6,r0
    .org 0x49e50 - 0x8618
L_49e50:
    tst #0x8,r0
    .org 0x49e52 - 0x8618
L_49e52:
    bt L_49e86
    .org 0x49e54 - 0x8618
L_49e54:
    mov #0x1,r0
    .org 0x49e56 - 0x8618
L_49e56:
    mov.l P_49fd0,r2
    .org 0x49e58 - 0x8618
L_49e58:
    shll8 r0
    .org 0x49e5a - 0x8618
L_49e5a:
    add #0x4f,r0
    .org 0x49e5c - 0x8618
L_49e5c:
    mov.b @(r0,r2),r5
    .org 0x49e5e - 0x8618
L_49e5e:
    mov.l P_49fd4,r2
    .org 0x49e60 - 0x8618
L_49e60:
    extu.b r5,r0
    .org 0x49e62 - 0x8618
L_49e62:
    add #-0x4,r2
    .org 0x49e64 - 0x8618
L_49e64:
    shll2 r0
    .org 0x49e66 - 0x8618
L_49e66:
    mov.l r4,@(r0,r2)
    .org 0x49e68 - 0x8618
L_49e68:
    add #0x20,r15
    .org 0x49e6a - 0x8618
L_49e6a:
    lds.l @r15+,pr
    .org 0x49e6c - 0x8618
L_49e6c:
    mov.l @r15+,r14
    .org 0x49e6e - 0x8618
L_49e6e:
    mov.l @r15+,r13
    .org 0x49e70 - 0x8618
L_49e70:
    mov.l @r15+,r12
    .org 0x49e72 - 0x8618
L_49e72:
    mov.l @r15+,r11
    .org 0x49e74 - 0x8618
L_49e74:
    mov.l @r15+,r10
    .org 0x49e76 - 0x8618
L_49e76:
    mov.l @r15+,r9
    .org 0x49e78 - 0x8618
L_49e78:
    rts
    .org 0x49e7a - 0x8618
L_49e7a:
    mov.l @r15+,r8
    .org 0x49e7c - 0x8618
L_49e7c:
    mov.l P_49fd8,r6
    .org 0x49e7e - 0x8618
L_49e7e:
    mov r11,r0
    .org 0x49e80 - 0x8618
L_49e80:
    mov.l @(r0,r6),r2
    .org 0x49e82 - 0x8618
L_49e82:
    bra L_49dc0
    .org 0x49e84 - 0x8618
L_49e84:
    mov.l r2,@r13
    .org 0x49e86 - 0x8618
L_49e86:
    mov.l P_49fdc,r6
    .org 0x49e88 - 0x8618
L_49e88:
    mov.b @(0xa,r6),r0
    .org 0x49e8a - 0x8618
L_49e8a:
    mov.l P_49fd4,r6
    .org 0x49e8c - 0x8618
L_49e8c:
    extu.b r0,r0
    .org 0x49e8e - 0x8618
L_49e8e:
    add #-0x4,r6
    .org 0x49e90 - 0x8618
L_49e90:
    shll2 r0
    .org 0x49e92 - 0x8618
L_49e92:
    bra L_49e68
    .org 0x49e94 - 0x8618
L_49e94:
    mov.l r4,@(r0,r6)
    .org 0x49e96 - 0x8618
L_49e96:
    mov.l r14,@-r15
    .org 0x49e98 - 0x8618
L_49e98:
    sts.l macl,@-r15
    .org 0x49e9a - 0x8618
L_49e9a:
    mov.l P_49fe0,r6
    .org 0x49e9c - 0x8618
L_49e9c:
    mov #-0x1,r4
    .org 0x49e9e - 0x8618
L_49e9e:
    extu.w r4,r4
    .org 0x49ea0 - 0x8618
L_49ea0:
    mov.b @r6,r2
    .org 0x49ea2 - 0x8618
L_49ea2:
    extu.b r2,r5
    .org 0x49ea4 - 0x8618
L_49ea4:
    mov.l P_49fe4,r2
    .org 0x49ea6 - 0x8618
L_49ea6:
    mov.b @r2,r6
    .org 0x49ea8 - 0x8618
L_49ea8:
    extu.b r6,r2
    .org 0x49eaa - 0x8618
L_49eaa:
    mulu.w r5,r2
    .org 0x49eac - 0x8618
L_49eac:
    mov.l P_49fe8,r5
    .org 0x49eae - 0x8618
L_49eae:
    sts macl,r2
    .org 0x49eb0 - 0x8618
L_49eb0:
    extu.w r2,r6
    .org 0x49eb2 - 0x8618
L_49eb2:
    mov.b @r5,r2
    .org 0x49eb4 - 0x8618
L_49eb4:
    extu.b r2,r2
    .org 0x49eb6 - 0x8618
L_49eb6:
    mul.l r6,r2
    .org 0x49eb8 - 0x8618
L_49eb8:
    sts macl,r2
    .org 0x49eba - 0x8618
L_49eba:
    shlr2 r2
    .org 0x49ebc - 0x8618
L_49ebc:
    shlr2 r2
    .org 0x49ebe - 0x8618
L_49ebe:
    shlr2 r2
    .org 0x49ec0 - 0x8618
L_49ec0:
    shlr r2
    .org 0x49ec2 - 0x8618
L_49ec2:
    cmp/hi r4,r2
    .org 0x49ec4 - 0x8618
L_49ec4:
    bt L_49ec8
    .org 0x49ec6 - 0x8618
L_49ec6:
    mov r2,r4
    .org 0x49ec8 - 0x8618
L_49ec8:
    mov.l P_49fcc,r6
    .org 0x49eca - 0x8618
L_49eca:
    mov.b @r6,r0
    .org 0x49ecc - 0x8618
L_49ecc:
    tst #0x8,r0
    .org 0x49ece - 0x8618
L_49ece:
    bf/s L_49f54
    .org 0x49ed0 - 0x8618
L_49ed0:
    extu.w r4,r4
    .org 0x49ed2 - 0x8618
L_49ed2:
    mov.l P_49fdc,r6
    .org 0x49ed4 - 0x8618
L_49ed4:
    mov.b @(0xa,r6),r0
    .org 0x49ed6 - 0x8618
L_49ed6:
    mov r0,r1
    .org 0x49ed8 - 0x8618
L_49ed8:
    mov.l P_49fd4,r14
    .org 0x49eda - 0x8618
L_49eda:
    extu.b r1,r1
    .org 0x49edc - 0x8618
L_49edc:
    mov r1,r0
    .org 0x49ede - 0x8618
L_49ede:
    shll2 r0
    .org 0x49ee0 - 0x8618
L_49ee0:
    mov r14,r2
    .org 0x49ee2 - 0x8618
L_49ee2:
    add #-0x4,r2
    .org 0x49ee4 - 0x8618
L_49ee4:
    mov.l @(r0,r2),r5
    .org 0x49ee6 - 0x8618
L_49ee6:
    cmp/pz r5
    .org 0x49ee8 - 0x8618
L_49ee8:
    bf L_49f60
    .org 0x49eea - 0x8618
L_49eea:
    mov r14,r5
    .org 0x49eec - 0x8618
L_49eec:
    add #-0x4,r5
    .org 0x49eee - 0x8618
L_49eee:
    mov r1,r0
    .org 0x49ef0 - 0x8618
L_49ef0:
    shll2 r0
    .org 0x49ef2 - 0x8618
L_49ef2:
    mov.l @(r0,r5),r7
    .org 0x49ef4 - 0x8618
L_49ef4:
    mov #0x0,r6
    .org 0x49ef6 - 0x8618
L_49ef6:
    mov r7,r2
    .org 0x49ef8 - 0x8618
L_49ef8:
    shll8 r6
    .org 0x49efa - 0x8618
L_49efa:
    add #-0x1,r6
    .org 0x49efc - 0x8618
L_49efc:
    shll16 r6
    .org 0x49efe - 0x8618
L_49efe:
    and r6,r2
    .org 0x49f00 - 0x8618
L_49f00:
    extu.w r7,r6
    .org 0x49f02 - 0x8618
L_49f02:
    mul.l r6,r4
    .org 0x49f04 - 0x8618
L_49f04:
    shlr16 r2
    .org 0x49f06 - 0x8618
L_49f06:
    sts macl,r6
    .org 0x49f08 - 0x8618
L_49f08:
    mul.l r2,r4
    .org 0x49f0a - 0x8618
L_49f0a:
    mov #-0x80,r4
    .org 0x49f0c - 0x8618
L_49f0c:
    shll8 r4
    .org 0x49f0e - 0x8618
L_49f0e:
    sts macl,r5
    .org 0x49f10 - 0x8618
L_49f10:
    shll16 r4
    .org 0x49f12 - 0x8618
L_49f12:
    cmp/hs r4,r5
    .org 0x49f14 - 0x8618
L_49f14:
    bf L_49f6e
    .org 0x49f16 - 0x8618
L_49f16:
    mov r4,r5
    .org 0x49f18 - 0x8618
L_49f18:
    add #-0x4,r14
    .org 0x49f1a - 0x8618
L_49f1a:
    mov r1,r0
    .org 0x49f1c - 0x8618
L_49f1c:
    shll2 r0
    .org 0x49f1e - 0x8618
L_49f1e:
    mov.l @(r0,r14),r6
    .org 0x49f20 - 0x8618
L_49f20:
    cmp/pz r6
    .org 0x49f22 - 0x8618
L_49f22:
    bf L_49fbc
    .org 0x49f24 - 0x8618
L_49f24:
    mov.l P_49fec,r5
    .org 0x49f26 - 0x8618
L_49f26:
    mov.l P_49ff0,r4
    .org 0x49f28 - 0x8618
L_49f28:
    extu.b r1,r1
    .org 0x49f2a - 0x8618
L_49f2a:
    mov r1,r0
    .org 0x49f2c - 0x8618
L_49f2c:
    shll2 r0
    .org 0x49f2e - 0x8618
L_49f2e:
    mov r4,r6
    .org 0x49f30 - 0x8618
L_49f30:
    add #-0x4,r6
    .org 0x49f32 - 0x8618
L_49f32:
    mov.l r5,@(r0,r6)
    .org 0x49f34 - 0x8618
L_49f34:
    add #-0x4,r4
    .org 0x49f36 - 0x8618
L_49f36:
    mov r1,r0
    .org 0x49f38 - 0x8618
L_49f38:
    shll2 r0
    .org 0x49f3a - 0x8618
L_49f3a:
    mov #-0x80,r2
    .org 0x49f3c - 0x8618
L_49f3c:
    mov.l @(r0,r4),r5
    .org 0x49f3e - 0x8618
L_49f3e:
    shll8 r2
    .org 0x49f40 - 0x8618
L_49f40:
    shll16 r2
    .org 0x49f42 - 0x8618
L_49f42:
    add r2,r5
    .org 0x49f44 - 0x8618
L_49f44:
    mov.l P_49ff4,r2
    .org 0x49f46 - 0x8618
L_49f46:
    shll2 r1
    .org 0x49f48 - 0x8618
L_49f48:
    add #-0x4,r2
    .org 0x49f4a - 0x8618
L_49f4a:
    mov r1,r0
    .org 0x49f4c - 0x8618
L_49f4c:
    mov.l r5,@(r0,r2)
    .org 0x49f4e - 0x8618
L_49f4e:
    lds.l @r15+,macl
    .org 0x49f50 - 0x8618
L_49f50:
    rts
    .org 0x49f52 - 0x8618
L_49f52:
    mov.l @r15+,r14
    .org 0x49f54 - 0x8618
L_49f54:
    mov #0x1,r0
    .org 0x49f56 - 0x8618
L_49f56:
    mov.l P_49fd0,r6
    .org 0x49f58 - 0x8618
L_49f58:
    shll8 r0
    .org 0x49f5a - 0x8618
L_49f5a:
    add #0x4f,r0
    .org 0x49f5c - 0x8618
L_49f5c:
    bra L_49ed8
    .org 0x49f5e - 0x8618
L_49f5e:
    mov.b @(r0,r6),r1
    .org 0x49f60 - 0x8618
L_49f60:
    mov r14,r2
    .org 0x49f62 - 0x8618
L_49f62:
    add #-0x4,r2
    .org 0x49f64 - 0x8618
L_49f64:
    mov r1,r0
    .org 0x49f66 - 0x8618
L_49f66:
    shll2 r0
    .org 0x49f68 - 0x8618
L_49f68:
    mov.l @(r0,r2),r5
    .org 0x49f6a - 0x8618
L_49f6a:
    bra L_49ef4
    .org 0x49f6c - 0x8618
L_49f6c:
    neg r5,r7
    .org 0x49f6e - 0x8618
L_49f6e:
    mov r6,r2
    .org 0x49f70 - 0x8618
L_49f70:
    shlr16 r2
    .org 0x49f72 - 0x8618
L_49f72:
    add r2,r5
    .org 0x49f74 - 0x8618
L_49f74:
    cmp/hs r4,r5
    .org 0x49f76 - 0x8618
L_49f76:
    bt L_49fb0
    .org 0x49f78 - 0x8618
L_49f78:
    shll r5
    .org 0x49f7a - 0x8618
L_49f7a:
    mov r5,r2
    .org 0x49f7c - 0x8618
L_49f7c:
    mov.l P_49ff8,r5
    .org 0x49f7e - 0x8618
L_49f7e:
    tst r5,r6
    .org 0x49f80 - 0x8618
L_49f80:
    bt L_49f84
    .org 0x49f82 - 0x8618
L_49f82:
    add #0x1,r2
    .org 0x49f84 - 0x8618
L_49f84:
    cmp/hs r4,r2
    .org 0x49f86 - 0x8618
L_49f86:
    bt L_49fb4
    .org 0x49f88 - 0x8618
L_49f88:
    mov r2,r5
    .org 0x49f8a - 0x8618
L_49f8a:
    mov #0x40,r2
    .org 0x49f8c - 0x8618
L_49f8c:
    shll8 r2
    .org 0x49f8e - 0x8618
L_49f8e:
    shll r5
    .org 0x49f90 - 0x8618
L_49f90:
    tst r2,r6
    .org 0x49f92 - 0x8618
L_49f92:
    bt L_49f96
    .org 0x49f94 - 0x8618
L_49f94:
    add #0x1,r5
    .org 0x49f96 - 0x8618
L_49f96:
    cmp/hs r4,r5
    .org 0x49f98 - 0x8618
L_49f98:
    bt L_49fb8
    .org 0x49f9a - 0x8618
L_49f9a:
    add #-0x4,r14
    .org 0x49f9c - 0x8618
L_49f9c:
    mov r1,r0
    .org 0x49f9e - 0x8618
L_49f9e:
    shll2 r0
    .org 0x49fa0 - 0x8618
L_49fa0:
    mov.l @(r0,r14),r6
    .org 0x49fa2 - 0x8618
L_49fa2:
    cmp/pz r6
    .org 0x49fa4 - 0x8618
L_49fa4:
    bf L_49fbc
    .org 0x49fa6 - 0x8618
L_49fa6:
    mov.l P_49fec,r2
    .org 0x49fa8 - 0x8618
L_49fa8:
    cmp/hi r2,r5
    .org 0x49faa - 0x8618
L_49faa:
    bt L_49f24
    .org 0x49fac - 0x8618
L_49fac:
    bra L_49f26
    .org 0x49fae - 0x8618
L_49fae:
    nop
    .org 0x49fb0 - 0x8618
L_49fb0:
    bra L_49f18
    .org 0x49fb2 - 0x8618
L_49fb2:
    mov r4,r5
    .org 0x49fb4 - 0x8618
L_49fb4:
    bra L_49f18
    .org 0x49fb6 - 0x8618
L_49fb6:
    mov r4,r5
    .org 0x49fb8 - 0x8618
L_49fb8:
    bra L_49f18
    .org 0x49fba - 0x8618
L_49fba:
    mov r4,r5
    .org 0x49fbc - 0x8618
L_49fbc:
    bra L_49f26
    .org 0x49fbe - 0x8618
L_49fbe:
    neg r5,r5
    .org 0x49fc0 - 0x8618
P_49fc0: .long 0x00008618
P_49fc4: .long 0x000221bc
P_49fc8: .long 0x00008870
P_49fcc: .long 0x00008b3d
P_49fd0: .long 0xffff1ff4
P_49fd4: .long 0xffff2274
P_49fd8: .long 0xffff2158
P_49fdc: .long 0xffff11d4
P_49fe0: .long 0x000086a7
P_49fe4: .long 0x00008694
P_49fe8: .long 0x000086ac
P_49fec: .long 0x7fffffff
P_49ff0: .long 0xffff21f8
P_49ff4: .long 0xffff21d8
P_49ff8: .long 0x00008000
    .org 0x4a24c - 0x8618
P_4a24c:
    .byte 0xd2,0x9e,0x60,0x20,0xc9,0x08,0x20,0x08,0x8d,0x02,0x6b,0x03
    .org 0x4a296 - 0x8618
P_4a296:
    .byte 0xd6,0x90
    .org 0x4a29c - 0x8618
P_4a29c:
    .byte 0x2f,0x62
    .org 0x4a2b6 - 0x8618
L_4a2b6:
    tst r11,r11
    .org 0x4a2b8 - 0x8618
L_4a2b8:
    bt L_4a2be
    .org 0x4a2ba - 0x8618
L_4a2ba:
    bra L_4a496
    .org 0x4a2bc - 0x8618
L_4a2bc:
    nop
    .org 0x4a2be - 0x8618
L_4a2be:
    mov.l P_4a4cc,r14
    .org 0x4a2c0 - 0x8618
L_4a2c0:
    mov #0x8,r7
    .org 0x4a2c2 - 0x8618
L_4a2c2:
    mov.l P_4a4dc,r5
    .org 0x4a2c4 - 0x8618
L_4a2c4:
    mov.b @(0xa,r14),r0
    .org 0x4a2c6 - 0x8618
L_4a2c6:
    mov.l P_4a4e0,r14
    .org 0x4a2c8 - 0x8618
L_4a2c8:
    extu.b r0,r2
    .org 0x4a2ca - 0x8618
L_4a2ca:
    mov.l @r15,r4
    .org 0x4a2cc - 0x8618
L_4a2cc:
    shll2 r2
    .org 0x4a2ce - 0x8618
L_4a2ce:
    shll2 r2
    .org 0x4a2d0 - 0x8618
L_4a2d0:
    add r2,r5
    .org 0x4a2d2 - 0x8618
L_4a2d2:
    add #-0x10,r5
    .org 0x4a2d4 - 0x8618
L_4a2d4:
    mov.w @r4+,r2
    .org 0x4a2d6 - 0x8618
L_4a2d6:
    dt r7
    .org 0x4a2d8 - 0x8618
L_4a2d8:
    extu.w r2,r6
    .org 0x4a2da - 0x8618
L_4a2da:
    mov.w @r5+,r2
    .org 0x4a2dc - 0x8618
L_4a2dc:
    extu.w r2,r2
    .org 0x4a2de - 0x8618
L_4a2de:
    sub r2,r6
    .org 0x4a2e0 - 0x8618
L_4a2e0:
    mov.l r6,@r14
    .org 0x4a2e2 - 0x8618
L_4a2e2:
    bf/s L_4a2d4
    .org 0x4a2e4 - 0x8618
L_4a2e4:
    add #0x4,r14
    .org 0x4a2e6 - 0x8618
L_4a2e6:
    bsr L_49d88
    .org 0x4a2e8 - 0x8618
L_4a2e8:
    nop
    .org 0x4a2ea - 0x8618
L_4a2ea:
    bsr L_49e96
    .org 0x4a2ec - 0x8618
L_4a2ec:
    nop
    .org 0x4a3da - 0x8618
P_4a3da:
    .byte 0xd6,0x3f
    .org 0x4a3e0 - 0x8618
P_4a3e0:
    .byte 0x2f,0x62
    .org 0x4a496 - 0x8618
L_4a496:
    mov #0x1,r0
    .org 0x4a498 - 0x8618
L_4a498:
    mov.l P_4a4d0,r3
    .org 0x4a49a - 0x8618
L_4a49a:
    shll8 r0
    .org 0x4a49c - 0x8618
L_4a49c:
    mov.l P_4a4dc,r5
    .org 0x4a49e - 0x8618
L_4a49e:
    add #0x4f,r0
    .org 0x4a4a0 - 0x8618
L_4a4a0:
    mov.l P_4a4e0,r14
    .org 0x4a4a2 - 0x8618
L_4a4a2:
    mov.b @(r0,r3),r6
    .org 0x4a4a4 - 0x8618
L_4a4a4:
    mov #0x8,r7
    .org 0x4a4a6 - 0x8618
L_4a4a6:
    mov.l @r15,r4
    .org 0x4a4a8 - 0x8618
L_4a4a8:
    extu.b r6,r6
    .org 0x4a4aa - 0x8618
L_4a4aa:
    shll2 r6
    .org 0x4a4ac - 0x8618
L_4a4ac:
    shll2 r6
    .org 0x4a4ae - 0x8618
L_4a4ae:
    add r6,r5
    .org 0x4a4b0 - 0x8618
L_4a4b0:
    add #-0x10,r5
    .org 0x4a4b2 - 0x8618
L_4a4b2:
    mov.w @r4+,r2
    .org 0x4a4b4 - 0x8618
L_4a4b4:
    dt r7
    .org 0x4a4b6 - 0x8618
L_4a4b6:
    extu.w r2,r6
    .org 0x4a4b8 - 0x8618
L_4a4b8:
    mov.w @r5+,r2
    .org 0x4a4ba - 0x8618
L_4a4ba:
    extu.w r2,r2
    .org 0x4a4bc - 0x8618
L_4a4bc:
    sub r2,r6
    .org 0x4a4be - 0x8618
L_4a4be:
    mov.l r6,@r14
    .org 0x4a4c0 - 0x8618
L_4a4c0:
    bf/s L_4a4b2
    .org 0x4a4c2 - 0x8618
L_4a4c2:
    add #0x4,r14
    .org 0x4a4c4 - 0x8618
L_4a4c4:
    bra L_4a2e6
    .org 0x4a4c6 - 0x8618
L_4a4c6:
    nop
    .org 0x4a4c8 - 0x8618
P_4a4c8:
    .long 0x00008b3d
    .org 0x4a4cc - 0x8618
P_4a4cc:
    .long 0xffff11d4
    .org 0x4a4d0 - 0x8618
P_4a4d0:
    .long 0xffff1ff4
    .org 0x4a4d8 - 0x8618
P_4a4d8:
    .long 0xffff20c2
    .org 0x4a4dc - 0x8618
P_4a4dc:
    .long 0xffff2178
    .org 0x4a4e0 - 0x8618
P_4a4e0:
    .long 0xffff2158
