! Exact natural common-gain builder and real diagnostic, shift, lookup and divide helpers.
    .text
    .balign 4
    .org 0x83c4 - 0x83c4
L_000083c4:
    .byte 0x80,0x33,0xd7
    .org 0x89fe - 0x83c4
L_000089fe:
    .byte 0x00
    .org 0x8ae7 - 0x83c4
L_00008ae7:
    .byte 0xaf
    .org 0x8b51 - 0x83c4
L_00008b51:
    .byte 0x4b
    .org 0x9332 - 0x83c4
L_00009332:
    .byte 0x36,0x94
    .org 0x93c6 - 0x83c4
L_000093c6:
    .byte 0xca,0x99
    .org 0x129e2 - 0x83c4
L_000129e2:
    .byte 0x22,0x36,0x4a,0x5e,0x72,0x86,0x9a,0xae,0xc2,0xd6,0xea,0xff,0xff,0xff,0xff,0xff
    .org 0x129f2 - 0x83c4
L_000129f2:
    .byte 0x21,0x1a,0x12,0x0e,0x0b,0x0b,0x05,0x04,0x08,0x03,0x00,0x00,0x00,0x00,0x00,0x00
    .org 0x21ce0 - 0x83c4
L_00021ce0:
    mov.l r2,@-r15
    .org 0x21ce2 - 0x83c4
L_00021ce2:
    tst r0,r0
    .org 0x21ce4 - 0x83c4
L_00021ce4:
    bt L_00021d6a
    .org 0x21ce6 - 0x83c4
L_00021ce6:
    extu.w r0,r2
    .org 0x21ce8 - 0x83c4
L_00021ce8:
    cmp/eq r2,r0
    .org 0x21cea - 0x83c4
L_00021cea:
    bf L_00021d76
    .org 0x21cec - 0x83c4
L_00021cec:
    div0u
    .org 0x21cee - 0x83c4
L_00021cee:
    shll8 r0
    .org 0x21cf0 - 0x83c4
L_00021cf0:
    cmp/hi r1,r0
    .org 0x21cf2 - 0x83c4
L_00021cf2:
    bf L_00021d0c
    .org 0x21cf4 - 0x83c4
L_00021cf4:
    div1 r0,r1
    .org 0x21cf6 - 0x83c4
L_00021cf6:
    div1 r0,r1
    .org 0x21cf8 - 0x83c4
L_00021cf8:
    div1 r0,r1
    .org 0x21cfa - 0x83c4
L_00021cfa:
    div1 r0,r1
    .org 0x21cfc - 0x83c4
L_00021cfc:
    div1 r0,r1
    .org 0x21cfe - 0x83c4
L_00021cfe:
    div1 r0,r1
    .org 0x21d00 - 0x83c4
L_00021d00:
    div1 r0,r1
    .org 0x21d02 - 0x83c4
L_00021d02:
    div1 r0,r1
    .org 0x21d04 - 0x83c4
L_00021d04:
    rotcl r1
    .org 0x21d06 - 0x83c4
L_00021d06:
    mov.l @r15+,r2
    .org 0x21d08 - 0x83c4
L_00021d08:
    rts
    .org 0x21d0a - 0x83c4
L_00021d0a:
    extu.b r1,r0
    .org 0x21d0c - 0x83c4
L_00021d0c:
    mov.l r3,@-r15
    .org 0x21d0e - 0x83c4
L_00021d0e:
    extu.w r1,r3
    .org 0x21d10 - 0x83c4
L_00021d10:
    shll8 r0
    .org 0x21d12 - 0x83c4
L_00021d12:
    shlr16 r1
    .org 0x21d14 - 0x83c4
L_00021d14:
    div1 r0,r1
    .org 0x21d16 - 0x83c4
L_00021d16:
    div1 r0,r1
    .org 0x21d18 - 0x83c4
L_00021d18:
    div1 r0,r1
    .org 0x21d1a - 0x83c4
L_00021d1a:
    div1 r0,r1
    .org 0x21d1c - 0x83c4
L_00021d1c:
    div1 r0,r1
    .org 0x21d1e - 0x83c4
L_00021d1e:
    div1 r0,r1
    .org 0x21d20 - 0x83c4
L_00021d20:
    div1 r0,r1
    .org 0x21d22 - 0x83c4
L_00021d22:
    div1 r0,r1
    .org 0x21d24 - 0x83c4
L_00021d24:
    div1 r0,r1
    .org 0x21d26 - 0x83c4
L_00021d26:
    div1 r0,r1
    .org 0x21d28 - 0x83c4
L_00021d28:
    div1 r0,r1
    .org 0x21d2a - 0x83c4
L_00021d2a:
    div1 r0,r1
    .org 0x21d2c - 0x83c4
L_00021d2c:
    div1 r0,r1
    .org 0x21d2e - 0x83c4
L_00021d2e:
    div1 r0,r1
    .org 0x21d30 - 0x83c4
L_00021d30:
    div1 r0,r1
    .org 0x21d32 - 0x83c4
L_00021d32:
    div1 r0,r1
    .org 0x21d34 - 0x83c4
L_00021d34:
    extu.w r1,r2
    .org 0x21d36 - 0x83c4
L_00021d36:
    xor r2,r1
    .org 0x21d38 - 0x83c4
L_00021d38:
    addc r2,r2
    .org 0x21d3a - 0x83c4
L_00021d3a:
    shll16 r2
    .org 0x21d3c - 0x83c4
L_00021d3c:
    add r3,r1
    .org 0x21d3e - 0x83c4
L_00021d3e:
    div1 r0,r1
    .org 0x21d40 - 0x83c4
L_00021d40:
    div1 r0,r1
    .org 0x21d42 - 0x83c4
L_00021d42:
    div1 r0,r1
    .org 0x21d44 - 0x83c4
L_00021d44:
    div1 r0,r1
    .org 0x21d46 - 0x83c4
L_00021d46:
    div1 r0,r1
    .org 0x21d48 - 0x83c4
L_00021d48:
    div1 r0,r1
    .org 0x21d4a - 0x83c4
L_00021d4a:
    div1 r0,r1
    .org 0x21d4c - 0x83c4
L_00021d4c:
    div1 r0,r1
    .org 0x21d4e - 0x83c4
L_00021d4e:
    div1 r0,r1
    .org 0x21d50 - 0x83c4
L_00021d50:
    div1 r0,r1
    .org 0x21d52 - 0x83c4
L_00021d52:
    div1 r0,r1
    .org 0x21d54 - 0x83c4
L_00021d54:
    div1 r0,r1
    .org 0x21d56 - 0x83c4
L_00021d56:
    div1 r0,r1
    .org 0x21d58 - 0x83c4
L_00021d58:
    div1 r0,r1
    .org 0x21d5a - 0x83c4
L_00021d5a:
    div1 r0,r1
    .org 0x21d5c - 0x83c4
L_00021d5c:
    div1 r0,r1
    .org 0x21d5e - 0x83c4
L_00021d5e:
    rotcl r1
    .org 0x21d60 - 0x83c4
L_00021d60:
    extu.w r1,r0
    .org 0x21d62 - 0x83c4
L_00021d62:
    add r2,r0
    .org 0x21d64 - 0x83c4
L_00021d64:
    mov.l @r15+,r3
    .org 0x21d66 - 0x83c4
L_00021d66:
    rts
    .org 0x21d68 - 0x83c4
L_00021d68:
    mov.l @r15+,r2
    .org 0x21d6a - 0x83c4
L_00021d6a:
    mov.l L_00021dc8,r1
    .org 0x21d6c - 0x83c4
L_00021d6c:
    mov.l L_00021dcc,r2
    .org 0x21d6e - 0x83c4
L_00021d6e:
    mov.l r2,@r1
    .org 0x21d70 - 0x83c4
L_00021d70:
    mov #0x0,r0
    .org 0x21d72 - 0x83c4
L_00021d72:
    rts
    .org 0x21d74 - 0x83c4
L_00021d74:
    mov.l @r15+,r2
    .org 0x21d76 - 0x83c4
L_00021d76:
    div0u
    .org 0x21d78 - 0x83c4
L_00021d78:
    extu.w r1,r2
    .org 0x21d7a - 0x83c4
L_00021d7a:
    shll16 r2
    .org 0x21d7c - 0x83c4
L_00021d7c:
    shlr16 r1
    .org 0x21d7e - 0x83c4
L_00021d7e:
    rotcl r2
    .org 0x21d80 - 0x83c4
L_00021d80:
    div1 r0,r1
    .org 0x21d82 - 0x83c4
L_00021d82:
    rotcl r2
    .org 0x21d84 - 0x83c4
L_00021d84:
    div1 r0,r1
    .org 0x21d86 - 0x83c4
L_00021d86:
    rotcl r2
    .org 0x21d88 - 0x83c4
L_00021d88:
    div1 r0,r1
    .org 0x21d8a - 0x83c4
L_00021d8a:
    rotcl r2
    .org 0x21d8c - 0x83c4
L_00021d8c:
    div1 r0,r1
    .org 0x21d8e - 0x83c4
L_00021d8e:
    rotcl r2
    .org 0x21d90 - 0x83c4
L_00021d90:
    div1 r0,r1
    .org 0x21d92 - 0x83c4
L_00021d92:
    rotcl r2
    .org 0x21d94 - 0x83c4
L_00021d94:
    div1 r0,r1
    .org 0x21d96 - 0x83c4
L_00021d96:
    rotcl r2
    .org 0x21d98 - 0x83c4
L_00021d98:
    div1 r0,r1
    .org 0x21d9a - 0x83c4
L_00021d9a:
    rotcl r2
    .org 0x21d9c - 0x83c4
L_00021d9c:
    div1 r0,r1
    .org 0x21d9e - 0x83c4
L_00021d9e:
    rotcl r2
    .org 0x21da0 - 0x83c4
L_00021da0:
    div1 r0,r1
    .org 0x21da2 - 0x83c4
L_00021da2:
    rotcl r2
    .org 0x21da4 - 0x83c4
L_00021da4:
    div1 r0,r1
    .org 0x21da6 - 0x83c4
L_00021da6:
    rotcl r2
    .org 0x21da8 - 0x83c4
L_00021da8:
    div1 r0,r1
    .org 0x21daa - 0x83c4
L_00021daa:
    rotcl r2
    .org 0x21dac - 0x83c4
L_00021dac:
    div1 r0,r1
    .org 0x21dae - 0x83c4
L_00021dae:
    rotcl r2
    .org 0x21db0 - 0x83c4
L_00021db0:
    div1 r0,r1
    .org 0x21db2 - 0x83c4
L_00021db2:
    rotcl r2
    .org 0x21db4 - 0x83c4
L_00021db4:
    div1 r0,r1
    .org 0x21db6 - 0x83c4
L_00021db6:
    rotcl r2
    .org 0x21db8 - 0x83c4
L_00021db8:
    div1 r0,r1
    .org 0x21dba - 0x83c4
L_00021dba:
    rotcl r2
    .org 0x21dbc - 0x83c4
L_00021dbc:
    div1 r0,r1
    .org 0x21dbe - 0x83c4
L_00021dbe:
    rotcl r2
    .org 0x21dc0 - 0x83c4
L_00021dc0:
    mov r2,r0
    .org 0x21dc2 - 0x83c4
L_00021dc2:
    rts
    .org 0x21dc4 - 0x83c4
L_00021dc4:
    mov.l @r15+,r2
    .org 0x21dc8 - 0x83c4
L_00021dc8:
    .long 0xffff9818
    .org 0x21dcc - 0x83c4
L_00021dcc:
    .long 0x0000044e
    .org 0x224f8 - 0x83c4
L_000224f8:
    shar r0
    .org 0x224fa - 0x83c4
L_000224fa:
    shar r0
    .org 0x224fc - 0x83c4
L_000224fc:
    shar r0
    .org 0x224fe - 0x83c4
L_000224fe:
    shar r0
    .org 0x22500 - 0x83c4
L_00022500:
    shar r0
    .org 0x22502 - 0x83c4
L_00022502:
    shar r0
    .org 0x22504 - 0x83c4
L_00022504:
    rts
    .org 0x22506 - 0x83c4
L_00022506:
    shar r0
    .org 0x25e20 - 0x83c4
L_00025e20:
    mov.l L_00025f10,r1
    .org 0x25e22 - 0x83c4
L_00025e22:
    exts.w r4,r0
    .org 0x25e24 - 0x83c4
L_00025e24:
    cmp/eq #-0x1,r0
    .org 0x25e26 - 0x83c4
L_00025e26:
    bt L_00025e3e
    .org 0x25e28 - 0x83c4
L_00025e28:
    mov r1,r6
    .org 0x25e2a - 0x83c4
L_00025e2a:
    mov r0,r2
    .org 0x25e2c - 0x83c4
L_00025e2c:
    shll r2
    .org 0x25e2e - 0x83c4
L_00025e2e:
    add r0,r2
    .org 0x25e30 - 0x83c4
L_00025e30:
    add r2,r6
    .org 0x25e32 - 0x83c4
L_00025e32:
    mov.b @(0x1,r6),r0
    .org 0x25e34 - 0x83c4
L_00025e34:
    tst #0x80,r0
    .org 0x25e36 - 0x83c4
L_00025e36:
    movt r0
    .org 0x25e38 - 0x83c4
L_00025e38:
    xor #0x1,r0
    .org 0x25e3a - 0x83c4
L_00025e3a:
    bra L_00025e40
    .org 0x25e3c - 0x83c4
L_00025e3c:
    extu.b r0,r2
    .org 0x25e3e - 0x83c4
L_00025e3e:
    mov #0x0,r2
    .org 0x25e40 - 0x83c4
L_00025e40:
    rts
    .org 0x25e42 - 0x83c4
L_00025e42:
    mov r2,r0
    .org 0x25f10 - 0x83c4
L_00025f10:
    .long 0xffff5718
    .org 0x26388 - 0x83c4
L_00026388:
    mov.w L_0002639a,r0
    .org 0x2638a - 0x83c4
L_0002638a:
    extu.b r5,r5
    .org 0x2638c - 0x83c4
L_0002638c:
    cmp/hs r0,r5
    .org 0x2638e - 0x83c4
L_0002638e:
    bt L_00026396
    .org 0x26390 - 0x83c4
L_00026390:
    mov.l L_0002639c,r6
    .org 0x26392 - 0x83c4
L_00026392:
    jmp @r6
    .org 0x26394 - 0x83c4
L_00026394:
    mov #0x0,r3
    .org 0x26396 - 0x83c4
L_00026396:
    rts
    .org 0x26398 - 0x83c4
L_00026398:
    mov.b @(0xf,r4),r0
    .org 0x2639a - 0x83c4
L_0002639a:
    .word 0x00f0
    .org 0x2639c - 0x83c4
L_0002639c:
    .long 0x00026a84
    .org 0x26740 - 0x83c4
L_00026740:
    cmp/hs r0,r2
    .org 0x26742 - 0x83c4
L_00026742:
    bt L_0002675c
    .org 0x26744 - 0x83c4
L_00026744:
    mov.l r0,@-r15
    .org 0x26746 - 0x83c4
L_00026746:
    sub r2,r0
    .org 0x26748 - 0x83c4
L_00026748:
    sts macl,r1
    .org 0x2674a - 0x83c4
L_0002674a:
    mul.l r3,r0
    .org 0x2674c - 0x83c4
L_0002674c:
    sts macl,r0
    .org 0x2674e - 0x83c4
L_0002674e:
    lds r1,macl
    .org 0x26750 - 0x83c4
L_00026750:
    swap.w r0,r0
    .org 0x26752 - 0x83c4
L_00026752:
    mov.l @r15+,r2
    .org 0x26754 - 0x83c4
L_00026754:
    extu.w r0,r0
    .org 0x26756 - 0x83c4
L_00026756:
    sub r0,r2
    .org 0x26758 - 0x83c4
L_00026758:
    rts
    .org 0x2675a - 0x83c4
L_0002675a:
    mov r2,r0
    .org 0x2675c - 0x83c4
L_0002675c:
    sub r0,r2
    .org 0x2675e - 0x83c4
L_0002675e:
    sts macl,r1
    .org 0x26760 - 0x83c4
L_00026760:
    mul.l r3,r2
    .org 0x26762 - 0x83c4
L_00026762:
    sts macl,r2
    .org 0x26764 - 0x83c4
L_00026764:
    lds r1,macl
    .org 0x26766 - 0x83c4
L_00026766:
    swap.w r2,r2
    .org 0x26768 - 0x83c4
L_00026768:
    extu.w r2,r2
    .org 0x2676a - 0x83c4
L_0002676a:
    rts
    .org 0x2676c - 0x83c4
L_0002676c:
    add r2,r0
    .org 0x26a84 - 0x83c4
L_00026a84:
    shlr r5
    .org 0x26a86 - 0x83c4
L_00026a86:
    rotcr r3
    .org 0x26a88 - 0x83c4
L_00026a88:
    shlr r5
    .org 0x26a8a - 0x83c4
L_00026a8a:
    rotcr r3
    .org 0x26a8c - 0x83c4
L_00026a8c:
    shlr r5
    .org 0x26a8e - 0x83c4
L_00026a8e:
    rotcr r3
    .org 0x26a90 - 0x83c4
L_00026a90:
    shlr r5
    .org 0x26a92 - 0x83c4
L_00026a92:
    rotcr r3
    .org 0x26a94 - 0x83c4
L_00026a94:
    swap.w r3,r3
    .org 0x26a96 - 0x83c4
L_00026a96:
    shlr8 r0
    .org 0x26a98 - 0x83c4
L_00026a98:
    tst r0,r0
    .org 0x26a9a - 0x83c4
L_00026a9a:
    bt L_00026aaa
    .org 0x26a9c - 0x83c4
L_00026a9c:
    shll r5
    .org 0x26a9e - 0x83c4
L_00026a9e:
    add r5,r4
    .org 0x26aa0 - 0x83c4
L_00026aa0:
    mov.w @r4,r1
    .org 0x26aa2 - 0x83c4
L_00026aa2:
    mov.w @(0x2,r4),r0
    .org 0x26aa4 - 0x83c4
L_00026aa4:
    extu.w r0,r2
    .org 0x26aa6 - 0x83c4
L_00026aa6:
    bra L_00026ab4
    .org 0x26aa8 - 0x83c4
L_00026aa8:
    extu.w r1,r0
    .org 0x26aaa - 0x83c4
L_00026aaa:
    add r5,r4
    .org 0x26aac - 0x83c4
L_00026aac:
    mov.b @r4,r1
    .org 0x26aae - 0x83c4
L_00026aae:
    mov.b @(0x1,r4),r0
    .org 0x26ab0 - 0x83c4
L_00026ab0:
    extu.b r0,r2
    .org 0x26ab2 - 0x83c4
L_00026ab2:
    extu.b r1,r0
    .org 0x26ab4 - 0x83c4
L_00026ab4:
    mov.l L_00026abc,r6
    .org 0x26ab6 - 0x83c4
L_00026ab6:
    jmp @r6
    .org 0x26ab8 - 0x83c4
L_00026ab8:
    nop
    .org 0x26abc - 0x83c4
L_00026abc:
    .long 0x00026740
    .org 0x53698 - 0x83c4
L_00053698:
    mov.l r12,@-r15
    .org 0x5369a - 0x83c4
L_0005369a:
    mov.l r13,@-r15
    .org 0x5369c - 0x83c4
L_0005369c:
    mov.l r14,@-r15
    .org 0x5369e - 0x83c4
L_0005369e:
    sts.l pr,@-r15
    .org 0x536a0 - 0x83c4
L_000536a0:
    sts.l macl,@-r15
    .org 0x536a2 - 0x83c4
L_000536a2:
    add #-0x10,r15
    .org 0x536a4 - 0x83c4
L_000536a4:
    mov.l L_000538a0,r5
    .org 0x536a6 - 0x83c4
L_000536a6:
    mov #0x15,r0
    .org 0x536a8 - 0x83c4
L_000536a8:
    mov.b @(r0,r5),r0
    .org 0x536aa - 0x83c4
L_000536aa:
    tst #0x8,r0
    .org 0x536ac - 0x83c4
L_000536ac:
    bf L_000536b2
    .org 0x536ae - 0x83c4
L_000536ae:
    bra L_0005387a
    .org 0x536b0 - 0x83c4
L_000536b0:
    nop
    .org 0x536b2 - 0x83c4
L_000536b2:
    and #0xf7,r0
    .org 0x536b4 - 0x83c4
L_000536b4:
    mov r0,r6
    .org 0x536b6 - 0x83c4
L_000536b6:
    mov #0x15,r0
    .org 0x536b8 - 0x83c4
L_000536b8:
    mov.b r6,@(r0,r5)
    .org 0x536ba - 0x83c4
L_000536ba:
    mov.l L_000538a4,r5
    .org 0x536bc - 0x83c4
L_000536bc:
    jsr @r5
    .org 0x536be - 0x83c4
L_000536be:
    mov #-0x1,r4
    .org 0x536c0 - 0x83c4
L_000536c0:
    tst r0,r0
    .org 0x536c2 - 0x83c4
L_000536c2:
    bt L_000536ca
    .org 0x536c4 - 0x83c4
L_000536c4:
    mov.l L_000538a8,r7
    .org 0x536c6 - 0x83c4
L_000536c6:
    bra L_000536ee
    .org 0x536c8 - 0x83c4
L_000536c8:
    mov.l r7,@r15
    .org 0x536ca - 0x83c4
L_000536ca:
    mov.l L_000538ac,r2
    .org 0x536cc - 0x83c4
L_000536cc:
    mov.l L_000538b0,r5
    .org 0x536ce - 0x83c4
L_000536ce:
    mov.w @(0x10,r2),r0
    .org 0x536d0 - 0x83c4
L_000536d0:
    mov.b @r5,r2
    .org 0x536d2 - 0x83c4
L_000536d2:
    extu.w r0,r6
    .org 0x536d4 - 0x83c4
L_000536d4:
    mov.l L_000538b4,r5
    .org 0x536d6 - 0x83c4
L_000536d6:
    extu.b r2,r2
    .org 0x536d8 - 0x83c4
L_000536d8:
    mul.l r6,r2
    .org 0x536da - 0x83c4
L_000536da:
    mov.w @r5,r4
    .org 0x536dc - 0x83c4
L_000536dc:
    mov.l L_000538b8,r6
    .org 0x536de - 0x83c4
L_000536de:
    sts macl,r0
    .org 0x536e0 - 0x83c4
L_000536e0:
    extu.w r4,r5
    .org 0x536e2 - 0x83c4
L_000536e2:
    jsr @r6
    .org 0x536e4 - 0x83c4
L_000536e4:
    mov.l r5,@(0x4,r15)
    .org 0x536e6 - 0x83c4
L_000536e6:
    mov.l @(0x4,r15),r2
    .org 0x536e8 - 0x83c4
L_000536e8:
    add r2,r0
    .org 0x536ea - 0x83c4
L_000536ea:
    mov r0,r7
    .org 0x536ec - 0x83c4
L_000536ec:
    mov.l r0,@r15
    .org 0x536ee - 0x83c4
L_000536ee:
    mov #-0x1,r2
    .org 0x536f0 - 0x83c4
L_000536f0:
    extu.w r2,r2
    .org 0x536f2 - 0x83c4
L_000536f2:
    cmp/hi r2,r7
    .org 0x536f4 - 0x83c4
L_000536f4:
    bf/s L_000536fa
    .org 0x536f6 - 0x83c4
L_000536f6:
    mov r7,r2
    .org 0x536f8 - 0x83c4
L_000536f8:
    mov #-0x1,r2
    .org 0x536fa - 0x83c4
L_000536fa:
    mov r2,r6
    .org 0x536fc - 0x83c4
L_000536fc:
    mov.l L_000538bc,r2
    .org 0x536fe - 0x83c4
L_000536fe:
    mov.w L_000537e4,r0
    .org 0x53700 - 0x83c4
L_00053700:
    mov.l L_000538a4,r5
    .org 0x53702 - 0x83c4
L_00053702:
    mov.w L_000537e6,r4
    .org 0x53704 - 0x83c4
L_00053704:
    jsr @r5
    .org 0x53706 - 0x83c4
L_00053706:
    mov.w r6,@(r0,r2)
    .org 0x53708 - 0x83c4
L_00053708:
    tst r0,r0
    .org 0x5370a - 0x83c4
L_0005370a:
    bt L_00053712
    .org 0x5370c - 0x83c4
L_0005370c:
    mov.l L_000538c0,r6
    .org 0x5370e - 0x83c4
L_0005370e:
    bra L_0005371a
    .org 0x53710 - 0x83c4
L_00053710:
    mov.b @r6,r2
    .org 0x53712 - 0x83c4
L_00053712:
    mov.l L_000538c4,r6
    .org 0x53714 - 0x83c4
L_00053714:
    mov #-0x47,r0
    .org 0x53716 - 0x83c4
L_00053716:
    extu.b r0,r0
    .org 0x53718 - 0x83c4
L_00053718:
    mov.b @(r0,r6),r2
    .org 0x5371a - 0x83c4
L_0005371a:
    mov.l @r15,r1
    .org 0x5371c - 0x83c4
L_0005371c:
    extu.b r2,r6
    .org 0x5371e - 0x83c4
L_0005371e:
    mov.l L_000538c8,r13
    .org 0x53720 - 0x83c4
L_00053720:
    mov.l L_000538a8,r0
    .org 0x53722 - 0x83c4
L_00053722:
    shll8 r1
    .org 0x53724 - 0x83c4
L_00053724:
    jsr @r13
    .org 0x53726 - 0x83c4
L_00053726:
    mov.l r6,@(0x8,r15)
    .org 0x53728 - 0x83c4
L_00053728:
    mov.l L_000538cc,r7
    .org 0x5372a - 0x83c4
L_0005372a:
    mov.l r0,@(0xc,r15)
    .org 0x5372c - 0x83c4
L_0005372c:
    mov.b @r7,r5
    .org 0x5372e - 0x83c4
L_0005372e:
    extu.b r5,r5
    .org 0x53730 - 0x83c4
L_00053730:
    cmp/hs r5,r0
    .org 0x53732 - 0x83c4
L_00053732:
    bt/s L_0005373c
    .org 0x53734 - 0x83c4
L_00053734:
    mov r0,r4
    .org 0x53736 - 0x83c4
L_00053736:
    mov r5,r4
    .org 0x53738 - 0x83c4
L_00053738:
    bra L_00053748
    .org 0x5373a - 0x83c4
L_0005373a:
    mov.l r5,@(0xc,r15)
    .org 0x5373c - 0x83c4
L_0005373c:
    mov #0x1,r6
    .org 0x5373e - 0x83c4
L_0005373e:
    shll8 r6
    .org 0x53740 - 0x83c4
L_00053740:
    cmp/hi r6,r4
    .org 0x53742 - 0x83c4
L_00053742:
    bf L_00053748
    .org 0x53744 - 0x83c4
L_00053744:
    mov r6,r4
    .org 0x53746 - 0x83c4
L_00053746:
    mov.l r6,@(0xc,r15)
    .org 0x53748 - 0x83c4
L_00053748:
    mov.l @(0x8,r15),r0
    .org 0x5374a - 0x83c4
L_0005374a:
    mov #-0x21,r6
    .org 0x5374c - 0x83c4
L_0005374c:
    extu.b r6,r6
    .org 0x5374e - 0x83c4
L_0005374e:
    mov.l L_000538d0,r1
    .org 0x53750 - 0x83c4
L_00053750:
    jsr @r13
    .org 0x53752 - 0x83c4
L_00053752:
    add r6,r0
    .org 0x53754 - 0x83c4
L_00053754:
    mov.l L_000538cc,r7
    .org 0x53756 - 0x83c4
L_00053756:
    mov r0,r5
    .org 0x53758 - 0x83c4
L_00053758:
    mov #-0x80,r4
    .org 0x5375a - 0x83c4
L_0005375a:
    mov.b @(0x1,r7),r0
    .org 0x5375c - 0x83c4
L_0005375c:
    extu.b r4,r4
    .org 0x5375e - 0x83c4
L_0005375e:
    extu.b r0,r6
    .org 0x53760 - 0x83c4
L_00053760:
    mov r6,r2
    .org 0x53762 - 0x83c4
L_00053762:
    add r4,r2
    .org 0x53764 - 0x83c4
L_00053764:
    cmp/hs r2,r5
    .org 0x53766 - 0x83c4
L_00053766:
    bf L_00053778
    .org 0x53768 - 0x83c4
L_00053768:
    mov.b @(0x2,r7),r0
    .org 0x5376a - 0x83c4
L_0005376a:
    mov #-0x80,r4
    .org 0x5376c - 0x83c4
L_0005376c:
    extu.b r4,r4
    .org 0x5376e - 0x83c4
L_0005376e:
    extu.b r0,r6
    .org 0x53770 - 0x83c4
L_00053770:
    mov r6,r2
    .org 0x53772 - 0x83c4
L_00053772:
    add r4,r2
    .org 0x53774 - 0x83c4
L_00053774:
    cmp/hi r2,r5
    .org 0x53776 - 0x83c4
L_00053776:
    bf L_00053780
    .org 0x53778 - 0x83c4
L_00053778:
    mov #-0x80,r2
    .org 0x5377a - 0x83c4
L_0005377a:
    extu.b r2,r2
    .org 0x5377c - 0x83c4
L_0005377c:
    add r2,r6
    .org 0x5377e - 0x83c4
L_0005377e:
    mov r6,r5
    .org 0x53780 - 0x83c4
L_00053780:
    mov.l L_000538d4,r2
    .org 0x53782 - 0x83c4
L_00053782:
    mov #-0x1,r14
    .org 0x53784 - 0x83c4
L_00053784:
    mov.l @(0xc,r15),r4
    .org 0x53786 - 0x83c4
L_00053786:
    extu.b r14,r14
    .org 0x53788 - 0x83c4
L_00053788:
    mov.w @r2,r6
    .org 0x5378a - 0x83c4
L_0005378a:
    extu.w r6,r2
    .org 0x5378c - 0x83c4
L_0005378c:
    mul.l r2,r4
    .org 0x5378e - 0x83c4
L_0005378e:
    sts macl,r2
    .org 0x53790 - 0x83c4
L_00053790:
    shlr8 r2
    .org 0x53792 - 0x83c4
L_00053792:
    mul.l r2,r5
    .org 0x53794 - 0x83c4
L_00053794:
    sts macl,r5
    .org 0x53796 - 0x83c4
L_00053796:
    shlr8 r5
    .org 0x53798 - 0x83c4
L_00053798:
    shlr2 r5
    .org 0x5379a - 0x83c4
L_0005379a:
    shlr2 r5
    .org 0x5379c - 0x83c4
L_0005379c:
    shlr2 r5
    .org 0x5379e - 0x83c4
L_0005379e:
    shlr r5
    .org 0x537a0 - 0x83c4
L_000537a0:
    cmp/hi r14,r5
    .org 0x537a2 - 0x83c4
L_000537a2:
    bf L_000537a6
    .org 0x537a4 - 0x83c4
L_000537a4:
    mov r14,r5
    .org 0x537a6 - 0x83c4
L_000537a6:
    mov.l L_000538d8,r12
    .org 0x537a8 - 0x83c4
L_000537a8:
    mov.w L_000537e8,r0
    .org 0x537aa - 0x83c4
L_000537aa:
    mov.l L_000538dc,r4
    .org 0x537ac - 0x83c4
L_000537ac:
    mov.l L_000538e0,r6
    .org 0x537ae - 0x83c4
L_000537ae:
    mov.b r5,@(r0,r12)
    .org 0x537b0 - 0x83c4
L_000537b0:
    jsr @r6
    .org 0x537b2 - 0x83c4
L_000537b2:
    extu.b r5,r5
    .org 0x537b4 - 0x83c4
L_000537b4:
    mov r0,r2
    .org 0x537b6 - 0x83c4
L_000537b6:
    mov.w L_000537ea,r0
    .org 0x537b8 - 0x83c4
L_000537b8:
    mov.l L_000538e4,r5
    .org 0x537ba - 0x83c4
L_000537ba:
    mov.b r2,@(r0,r12)
    .org 0x537bc - 0x83c4
L_000537bc:
    mov #0x17,r0
    .org 0x537be - 0x83c4
L_000537be:
    mov.b @(r0,r5),r2
    .org 0x537c0 - 0x83c4
L_000537c0:
    mov.l L_000538e8,r4
    .org 0x537c2 - 0x83c4
L_000537c2:
    mov.l L_000538e0,r6
    .org 0x537c4 - 0x83c4
L_000537c4:
    jsr @r6
    .org 0x537c6 - 0x83c4
L_000537c6:
    extu.b r2,r5
    .org 0x537c8 - 0x83c4
L_000537c8:
    extu.b r0,r2
    .org 0x537ca - 0x83c4
L_000537ca:
    mov.w L_000537ec,r0
    .org 0x537cc - 0x83c4
L_000537cc:
    mov #-0x1,r5
    .org 0x537ce - 0x83c4
L_000537ce:
    mov.b r2,@(r0,r12)
    .org 0x537d0 - 0x83c4
L_000537d0:
    extu.b r5,r5
    .org 0x537d2 - 0x83c4
L_000537d2:
    mov.w L_000537ea,r0
    .org 0x537d4 - 0x83c4
L_000537d4:
    mov.b @(r0,r12),r4
    .org 0x537d6 - 0x83c4
L_000537d6:
    extu.b r4,r4
    .org 0x537d8 - 0x83c4
L_000537d8:
    mov r4,r6
    .org 0x537da - 0x83c4
L_000537da:
    add r2,r6
    .org 0x537dc - 0x83c4
L_000537dc:
    cmp/gt r5,r6
    .org 0x537de - 0x83c4
L_000537de:
    bf L_000537ee
    .org 0x537e0 - 0x83c4
L_000537e0:
    bra L_000537f2
    .org 0x537e2 - 0x83c4
L_000537e2:
    mov r5,r2
    .org 0x537e4 - 0x83c4
L_000537e4:
    .word 0x0c24
    .org 0x537e6 - 0x83c4
L_000537e6:
    .word 0x012e
    .org 0x537e8 - 0x83c4
L_000537e8:
    .word 0x0125
    .org 0x537ea - 0x83c4
L_000537ea:
    .word 0x052e
    .org 0x537ec - 0x83c4
L_000537ec:
    .word 0x052f
    .org 0x537ee - 0x83c4
L_000537ee:
    add r2,r4
    .org 0x537f0 - 0x83c4
L_000537f0:
    mov r4,r2
    .org 0x537f2 - 0x83c4
L_000537f2:
    mov.w L_00053890,r0
    .org 0x537f4 - 0x83c4
L_000537f4:
    extu.b r2,r6
    .org 0x537f6 - 0x83c4
L_000537f6:
    mov.l @r15,r7
    .org 0x537f8 - 0x83c4
L_000537f8:
    mov.b r2,@(r0,r12)
    .org 0x537fa - 0x83c4
L_000537fa:
    mov #0x1,r2
    .org 0x537fc - 0x83c4
L_000537fc:
    shll8 r2
    .org 0x537fe - 0x83c4
L_000537fe:
    sub r6,r2
    .org 0x53800 - 0x83c4
L_00053800:
    mul.l r2,r7
    .org 0x53802 - 0x83c4
L_00053802:
    mov #-0x1,r6
    .org 0x53804 - 0x83c4
L_00053804:
    extu.w r6,r6
    .org 0x53806 - 0x83c4
L_00053806:
    sts macl,r4
    .org 0x53808 - 0x83c4
L_00053808:
    shlr8 r4
    .org 0x5380a - 0x83c4
L_0005380a:
    cmp/hi r6,r4
    .org 0x5380c - 0x83c4
L_0005380c:
    bf L_00053810
    .org 0x5380e - 0x83c4
L_0005380e:
    mov #-0x1,r4
    .org 0x53810 - 0x83c4
L_00053810:
    mov.l L_000538ec,r2
    .org 0x53812 - 0x83c4
L_00053812:
    mov.w L_00053892,r0
    .org 0x53814 - 0x83c4
L_00053814:
    mov.w r4,@(r0,r2)
    .org 0x53816 - 0x83c4
L_00053816:
    extu.w r4,r4
    .org 0x53818 - 0x83c4
L_00053818:
    mov.l L_000538f0,r2
    .org 0x5381a - 0x83c4
L_0005381a:
    mov.b @r2,r5
    .org 0x5381c - 0x83c4
L_0005381c:
    extu.b r5,r1
    .org 0x5381e - 0x83c4
L_0005381e:
    mov r1,r2
    .org 0x53820 - 0x83c4
L_00053820:
    shll8 r2
    .org 0x53822 - 0x83c4
L_00053822:
    shll2 r2
    .org 0x53824 - 0x83c4
L_00053824:
    add r4,r2
    .org 0x53826 - 0x83c4
L_00053826:
    tst r2,r2
    .org 0x53828 - 0x83c4
L_00053828:
    bt L_00053836
    .org 0x5382a - 0x83c4
L_0005382a:
    shll16 r1
    .org 0x5382c - 0x83c4
L_0005382c:
    mov r2,r0
    .org 0x5382e - 0x83c4
L_0005382e:
    jsr @r13
    .org 0x53830 - 0x83c4
L_00053830:
    shll2 r1
    .org 0x53832 - 0x83c4
L_00053832:
    bra L_00053838
    .org 0x53834 - 0x83c4
L_00053834:
    mov r0,r2
    .org 0x53836 - 0x83c4
L_00053836:
    mov #0x0,r2
    .org 0x53838 - 0x83c4
L_00053838:
    cmp/hi r14,r2
    .org 0x5383a - 0x83c4
L_0005383a:
    bf/s L_00053840
    .org 0x5383c - 0x83c4
L_0005383c:
    mov r2,r6
    .org 0x5383e - 0x83c4
L_0005383e:
    mov r14,r6
    .org 0x53840 - 0x83c4
L_00053840:
    mov.w L_00053894,r0
    .org 0x53842 - 0x83c4
L_00053842:
    extu.b r6,r2
    .org 0x53844 - 0x83c4
L_00053844:
    mov.b r6,@(r0,r12)
    .org 0x53846 - 0x83c4
L_00053846:
    mov.w L_00053896,r6
    .org 0x53848 - 0x83c4
L_00053848:
    mov.w L_00053898,r0
    .org 0x5384a - 0x83c4
L_0005384a:
    mul.l r2,r6
    .org 0x5384c - 0x83c4
L_0005384c:
    mov.l L_000538f4,r6
    .org 0x5384e - 0x83c4
L_0005384e:
    sts macl,r1
    .org 0x53850 - 0x83c4
L_00053850:
    jsr @r13
    .org 0x53852 - 0x83c4
L_00053852:
    add r6,r1
    .org 0x53854 - 0x83c4
L_00053854:
    cmp/hi r14,r0
    .org 0x53856 - 0x83c4
L_00053856:
    bf/s L_0005385c
    .org 0x53858 - 0x83c4
L_00053858:
    mov r0,r6
    .org 0x5385a - 0x83c4
L_0005385a:
    mov r14,r6
    .org 0x5385c - 0x83c4
L_0005385c:
    mov.w L_0005389a,r0
    .org 0x5385e - 0x83c4
L_0005385e:
    mov.l L_000538f8,r5
    .org 0x53860 - 0x83c4
L_00053860:
    extu.b r6,r2
    .org 0x53862 - 0x83c4
L_00053862:
    mov.b r6,@(r0,r12)
    .org 0x53864 - 0x83c4
L_00053864:
    mov.w @r5,r6
    .org 0x53866 - 0x83c4
L_00053866:
    mov.w L_0005389c,r0
    .org 0x53868 - 0x83c4
L_00053868:
    extu.w r6,r6
    .org 0x5386a - 0x83c4
L_0005386a:
    mul.l r6,r2
    .org 0x5386c - 0x83c4
L_0005386c:
    sts macl,r6
    .org 0x5386e - 0x83c4
L_0005386e:
    shlr8 r6
    .org 0x53870 - 0x83c4
L_00053870:
    swap.w r6,r2
    .org 0x53872 - 0x83c4
L_00053872:
    exts.b r2,r6
    .org 0x53874 - 0x83c4
L_00053874:
    xtrct r6,r2
    .org 0x53876 - 0x83c4
L_00053876:
    bra L_00053882
    .org 0x53878 - 0x83c4
L_00053878:
    mov.w r2,@(r0,r12)
    .org 0x5387a - 0x83c4
L_0005387a:
    or #0x8,r0
    .org 0x5387c - 0x83c4
L_0005387c:
    mov r0,r6
    .org 0x5387e - 0x83c4
L_0005387e:
    mov #0x15,r0
    .org 0x53880 - 0x83c4
L_00053880:
    mov.b r6,@(r0,r5)
    .org 0x53882 - 0x83c4
L_00053882:
    add #0x10,r15
    .org 0x53884 - 0x83c4
L_00053884:
    lds.l @r15+,macl
    .org 0x53886 - 0x83c4
L_00053886:
    lds.l @r15+,pr
    .org 0x53888 - 0x83c4
L_00053888:
    mov.l @r15+,r14
    .org 0x5388a - 0x83c4
L_0005388a:
    mov.l @r15+,r13
    .org 0x5388c - 0x83c4
L_0005388c:
    rts
    .org 0x5388e - 0x83c4
L_0005388e:
    mov.l @r15+,r12
    .org 0x53890 - 0x83c4
L_00053890:
    .word 0x052d
    .org 0x53892 - 0x83c4
L_00053892:
    .word 0x08e0
    .org 0x53894 - 0x83c4
L_00053894:
    .word 0x0562
    .org 0x53896 - 0x83c4
L_00053896:
    .word 0x148b
    .org 0x53898 - 0x83c4
L_00053898:
    .word 0x2710
    .org 0x5389a - 0x83c4
L_0005389a:
    .word 0x0381
    .org 0x5389c - 0x83c4
L_0005389c:
    .word 0x03d2
    .org 0x538a0 - 0x83c4
L_000538a0:
    .long 0xffff2470
    .org 0x538a4 - 0x83c4
L_000538a4:
    .long 0x00025e20
    .org 0x538a8 - 0x83c4
L_000538a8:
    .long 0x0000ca99
    .org 0x538ac - 0x83c4
L_000538ac:
    .long 0xffff4514
    .org 0x538b0 - 0x83c4
L_000538b0:
    .long 0x000089fe
    .org 0x538b4 - 0x83c4
L_000538b4:
    .long 0x000093c6
    .org 0x538b8 - 0x83c4
L_000538b8:
    .long 0x000224f8
    .org 0x538bc - 0x83c4
L_000538bc:
    .long 0xffff4558
    .org 0x538c0 - 0x83c4
L_000538c0:
    .long 0x00008b51
    .org 0x538c4 - 0x83c4
L_000538c4:
    .long 0xffff267a
    .org 0x538c8 - 0x83c4
L_000538c8:
    .long 0x00021ce0
    .org 0x538cc - 0x83c4
L_000538cc:
    .long 0x000083c4
    .org 0x538d0 - 0x83c4
L_000538d0:
    .long 0x00012a00
    .org 0x538d4 - 0x83c4
L_000538d4:
    .long 0xffff1024
    .org 0x538d8 - 0x83c4
L_000538d8:
    .long 0xffff128c
    .org 0x538dc - 0x83c4
L_000538dc:
    .long 0x000129e2
    .org 0x538e0 - 0x83c4
L_000538e0:
    .long 0x00026388
    .org 0x538e4 - 0x83c4
L_000538e4:
    .long 0xffff119c
    .org 0x538e8 - 0x83c4
L_000538e8:
    .long 0x000129f2
    .org 0x538ec - 0x83c4
L_000538ec:
    .long 0xffff28f8
    .org 0x538f0 - 0x83c4
L_000538f0:
    .long 0x00008ae7
    .org 0x538f4 - 0x83c4
L_000538f4:
    .long 0x00128500
    .org 0x538f8 - 0x83c4
L_000538f8:
    .long 0x00009332
