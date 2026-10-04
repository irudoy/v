! JK08A primary quarter-BFS arithmetic, Q7 compensation, and unsigned helpers.
! Instruction addresses and all original pools retain their ROM positions.
    .section .text
    .balign 4
    .org 0x3
P_000088fb:
    .byte 0x03
    .org 0x12f
P_00008a27:
    .byte 0x6d
    .org 0x98c
P_00009284:
    .byte 0x68
P_00009285:
    .byte 0xb6
    .org 0x193e8
L_00021ce0:
    mov.l r2,@-r15
L_00021ce2:
    tst r0,r0
L_00021ce4:
    bt L_00021d6a
L_00021ce6:
    extu.w r0,r2
L_00021ce8:
    cmp/eq r2,r0
L_00021cea:
    bf L_00021d76
L_00021cec:
    div0u
L_00021cee:
    shll8 r0
L_00021cf0:
    cmp/hi r1,r0
L_00021cf2:
    bf L_00021d0c
L_00021cf4:
    div1 r0,r1
L_00021cf6:
    div1 r0,r1
L_00021cf8:
    div1 r0,r1
L_00021cfa:
    div1 r0,r1
L_00021cfc:
    div1 r0,r1
L_00021cfe:
    div1 r0,r1
L_00021d00:
    div1 r0,r1
L_00021d02:
    div1 r0,r1
L_00021d04:
    rotcl r1
L_00021d06:
    mov.l @r15+,r2
L_00021d08:
    rts
L_00021d0a:
    extu.b r1,r0
L_00021d0c:
    mov.l r3,@-r15
L_00021d0e:
    extu.w r1,r3
L_00021d10:
    shll8 r0
L_00021d12:
    shlr16 r1
L_00021d14:
    div1 r0,r1
L_00021d16:
    div1 r0,r1
L_00021d18:
    div1 r0,r1
L_00021d1a:
    div1 r0,r1
L_00021d1c:
    div1 r0,r1
L_00021d1e:
    div1 r0,r1
L_00021d20:
    div1 r0,r1
L_00021d22:
    div1 r0,r1
L_00021d24:
    div1 r0,r1
L_00021d26:
    div1 r0,r1
L_00021d28:
    div1 r0,r1
L_00021d2a:
    div1 r0,r1
L_00021d2c:
    div1 r0,r1
L_00021d2e:
    div1 r0,r1
L_00021d30:
    div1 r0,r1
L_00021d32:
    div1 r0,r1
L_00021d34:
    extu.w r1,r2
L_00021d36:
    xor r2,r1
L_00021d38:
    addc r2,r2
L_00021d3a:
    shll16 r2
L_00021d3c:
    add r3,r1
L_00021d3e:
    div1 r0,r1
L_00021d40:
    div1 r0,r1
L_00021d42:
    div1 r0,r1
L_00021d44:
    div1 r0,r1
L_00021d46:
    div1 r0,r1
L_00021d48:
    div1 r0,r1
L_00021d4a:
    div1 r0,r1
L_00021d4c:
    div1 r0,r1
L_00021d4e:
    div1 r0,r1
L_00021d50:
    div1 r0,r1
L_00021d52:
    div1 r0,r1
L_00021d54:
    div1 r0,r1
L_00021d56:
    div1 r0,r1
L_00021d58:
    div1 r0,r1
L_00021d5a:
    div1 r0,r1
L_00021d5c:
    div1 r0,r1
L_00021d5e:
    rotcl r1
L_00021d60:
    extu.w r1,r0
L_00021d62:
    add r2,r0
L_00021d64:
    mov.l @r15+,r3
L_00021d66:
    rts
L_00021d68:
    mov.l @r15+,r2
L_00021d6a:
    mov.l P_00021dc8,r1
L_00021d6c:
    mov.l P_00021dcc,r2
L_00021d6e:
    mov.l r2,@r1
L_00021d70:
    mov #0x0,r0
L_00021d72:
    rts
L_00021d74:
    mov.l @r15+,r2
L_00021d76:
    div0u
L_00021d78:
    extu.w r1,r2
L_00021d7a:
    shll16 r2
L_00021d7c:
    shlr16 r1
L_00021d7e:
    rotcl r2
L_00021d80:
    div1 r0,r1
L_00021d82:
    rotcl r2
L_00021d84:
    div1 r0,r1
L_00021d86:
    rotcl r2
L_00021d88:
    div1 r0,r1
L_00021d8a:
    rotcl r2
L_00021d8c:
    div1 r0,r1
L_00021d8e:
    rotcl r2
L_00021d90:
    div1 r0,r1
L_00021d92:
    rotcl r2
L_00021d94:
    div1 r0,r1
L_00021d96:
    rotcl r2
L_00021d98:
    div1 r0,r1
L_00021d9a:
    rotcl r2
L_00021d9c:
    div1 r0,r1
L_00021d9e:
    rotcl r2
L_00021da0:
    div1 r0,r1
L_00021da2:
    rotcl r2
L_00021da4:
    div1 r0,r1
L_00021da6:
    rotcl r2
L_00021da8:
    div1 r0,r1
L_00021daa:
    rotcl r2
L_00021dac:
    div1 r0,r1
L_00021dae:
    rotcl r2
L_00021db0:
    div1 r0,r1
L_00021db2:
    rotcl r2
L_00021db4:
    div1 r0,r1
L_00021db6:
    rotcl r2
L_00021db8:
    div1 r0,r1
L_00021dba:
    rotcl r2
L_00021dbc:
    div1 r0,r1
L_00021dbe:
    rotcl r2
L_00021dc0:
    mov r2,r0
L_00021dc2:
    rts
L_00021dc4:
    mov.l @r15+,r2
    .org 0x194d0
P_00021dc8:
    .byte 0xff
P_00021dc9:
    .byte 0xff
P_00021dca:
    .byte 0x98
P_00021dcb:
    .byte 0x18
P_00021dcc:
    .byte 0x00
P_00021dcd:
    .byte 0x00
P_00021dce:
    .byte 0x04
P_00021dcf:
    .byte 0x4e
    .org 0x19648
L_00021f40:
    mov.l r2,@-r15
L_00021f42:
    tst r0,r0
L_00021f44:
    bt L_00021fd0
L_00021f46:
    extu.w r0,r2
L_00021f48:
    cmp/eq r2,r0
L_00021f4a:
    bf L_00021fdc
L_00021f4c:
    div0u
L_00021f4e:
    shll8 r0
L_00021f50:
    cmp/hi r1,r0
L_00021f52:
    bf L_00021f72
L_00021f54:
    div1 r0,r1
L_00021f56:
    div1 r0,r1
L_00021f58:
    div1 r0,r1
L_00021f5a:
    div1 r0,r1
L_00021f5c:
    div1 r0,r1
L_00021f5e:
    div1 r0,r1
L_00021f60:
    div1 r0,r1
L_00021f62:
    div1 r0,r1
L_00021f64:
    mov r1,r2
L_00021f66:
    bt L_00021f6a
L_00021f68:
    add r0,r2
L_00021f6a:
    shlr8 r2
L_00021f6c:
    mov r2,r0
L_00021f6e:
    rts
L_00021f70:
    mov.l @r15+,r2
L_00021f72:
    mov.l r3,@-r15
L_00021f74:
    extu.w r1,r3
L_00021f76:
    shll8 r0
L_00021f78:
    shlr16 r1
L_00021f7a:
    div1 r0,r1
L_00021f7c:
    div1 r0,r1
L_00021f7e:
    div1 r0,r1
L_00021f80:
    div1 r0,r1
L_00021f82:
    div1 r0,r1
L_00021f84:
    div1 r0,r1
L_00021f86:
    div1 r0,r1
L_00021f88:
    div1 r0,r1
L_00021f8a:
    div1 r0,r1
L_00021f8c:
    div1 r0,r1
L_00021f8e:
    div1 r0,r1
L_00021f90:
    div1 r0,r1
L_00021f92:
    div1 r0,r1
L_00021f94:
    div1 r0,r1
L_00021f96:
    div1 r0,r1
L_00021f98:
    div1 r0,r1
L_00021f9a:
    extu.w r1,r2
L_00021f9c:
    xor r2,r1
L_00021f9e:
    add r3,r1
L_00021fa0:
    div1 r0,r1
L_00021fa2:
    div1 r0,r1
L_00021fa4:
    div1 r0,r1
L_00021fa6:
    div1 r0,r1
L_00021fa8:
    div1 r0,r1
L_00021faa:
    div1 r0,r1
L_00021fac:
    div1 r0,r1
L_00021fae:
    div1 r0,r1
L_00021fb0:
    div1 r0,r1
L_00021fb2:
    div1 r0,r1
L_00021fb4:
    div1 r0,r1
L_00021fb6:
    div1 r0,r1
L_00021fb8:
    div1 r0,r1
L_00021fba:
    div1 r0,r1
L_00021fbc:
    div1 r0,r1
L_00021fbe:
    div1 r0,r1
L_00021fc0:
    mov r1,r2
L_00021fc2:
    bt L_00021fc6
L_00021fc4:
    add r0,r2
L_00021fc6:
    mov r2,r0
L_00021fc8:
    shlr16 r0
L_00021fca:
    mov.l @r15+,r3
L_00021fcc:
    rts
L_00021fce:
    mov.l @r15+,r2
L_00021fd0:
    mov.l P_00022030,r1
L_00021fd2:
    mov.l P_00022034,r2
L_00021fd4:
    mov.l r2,@r1
L_00021fd6:
    mov #0x0,r0
L_00021fd8:
    rts
L_00021fda:
    mov.l @r15+,r2
L_00021fdc:
    div0u
L_00021fde:
    extu.w r1,r2
L_00021fe0:
    shll16 r2
L_00021fe2:
    shlr16 r1
L_00021fe4:
    rotcl r2
L_00021fe6:
    div1 r0,r1
L_00021fe8:
    rotcl r2
L_00021fea:
    div1 r0,r1
L_00021fec:
    rotcl r2
L_00021fee:
    div1 r0,r1
L_00021ff0:
    rotcl r2
L_00021ff2:
    div1 r0,r1
L_00021ff4:
    rotcl r2
L_00021ff6:
    div1 r0,r1
L_00021ff8:
    rotcl r2
L_00021ffa:
    div1 r0,r1
L_00021ffc:
    rotcl r2
L_00021ffe:
    div1 r0,r1
L_00022000:
    rotcl r2
L_00022002:
    div1 r0,r1
L_00022004:
    rotcl r2
L_00022006:
    div1 r0,r1
L_00022008:
    rotcl r2
L_0002200a:
    div1 r0,r1
L_0002200c:
    rotcl r2
L_0002200e:
    div1 r0,r1
L_00022010:
    rotcl r2
L_00022012:
    div1 r0,r1
L_00022014:
    rotcl r2
L_00022016:
    div1 r0,r1
L_00022018:
    rotcl r2
L_0002201a:
    div1 r0,r1
L_0002201c:
    rotcl r2
L_0002201e:
    div1 r0,r1
L_00022020:
    rotcl r2
L_00022022:
    div1 r0,r1
L_00022024:
    bt L_00022028
L_00022026:
    add r0,r1
L_00022028:
    mov r1,r0
L_0002202a:
    rts
L_0002202c:
    mov.l @r15+,r2
    .org 0x19738
P_00022030:
    .byte 0xff
P_00022031:
    .byte 0xff
P_00022032:
    .byte 0x98
P_00022033:
    .byte 0x18
P_00022034:
    .byte 0x00
P_00022035:
    .byte 0x00
P_00022036:
    .byte 0x04
P_00022037:
    .byte 0x4e
    .org 0x32ece
L_0003b7c6:
    tst r4,r4
L_0003b7c8:
    bf L_0003b7f2
L_0003b7ca:
    mov.l P_0003b9a0,r12
L_0003b7cc:
    mov.l P_0003b9a4,r7
L_0003b7ce:
    mov.b @(0x1,r12),r0
L_0003b7d0:
    tst #0x20,r0
L_0003b7d2:
    bt L_0003b7e2
L_0003b7d4:
    mov.w @(0x8,r7),r0
L_0003b7d6:
    mov #0x40,r5
L_0003b7d8:
    extu.w r0,r6
L_0003b7da:
    cmp/ge r5,r6
L_0003b7dc:
    bt L_0003b7ee
L_0003b7de:
    bra L_0003b7ee
L_0003b7e0:
    mov #0x40,r6
L_0003b7e2:
    mov.w @(0x14,r7),r0
L_0003b7e4:
    mov #0x40,r5
L_0003b7e6:
    extu.w r0,r6
L_0003b7e8:
    cmp/ge r5,r6
L_0003b7ea:
    bt L_0003b7ee
L_0003b7ec:
    mov #0x40,r6
L_0003b7ee:
    bra L_0003b802
L_0003b7f0:
    mov r6,r14
L_0003b7f2:
    shll2 r5
L_0003b7f4:
    mov.l P_0003b9a0,r12
L_0003b7f6:
    shll r5
L_0003b7f8:
    mov #0x40,r2
L_0003b7fa:
    cmp/hs r2,r5
L_0003b7fc:
    bt L_0003b800
L_0003b7fe:
    mov #0x40,r5
L_0003b800:
    mov r5,r14
L_0003b802:
    mov.l @(0x4c,gbr),r0
L_0003b804:
    cmp/pl r0
L_0003b806:
    bt/s L_0003b80e
L_0003b808:
    mov r0,r6
L_0003b80a:
    bra L_0003b86a
L_0003b80c:
    mov #0x0,r2
L_0003b80e:
    mov.l P_0003b9a8,r5
L_0003b810:
    mov r6,r2
L_0003b812:
    shlr16 r2
L_0003b814:
    mov.w @r5,r4
L_0003b816:
    extu.w r4,r4
L_0003b818:
    mul.l r2,r4
L_0003b81a:
    extu.w r6,r2
L_0003b81c:
    sts macl,r5
L_0003b81e:
    mul.l r2,r4
L_0003b820:
    mov.l P_0003b9ac,r4
L_0003b822:
    sts macl,r2
L_0003b824:
    mov.b @r4,r7
L_0003b826:
    mov r2,r6
L_0003b828:
    shlr8 r6
L_0003b82a:
    extu.b r7,r7
L_0003b82c:
    mul.l r6,r7
L_0003b82e:
    extu.b r2,r2
L_0003b830:
    sts macl,r4
L_0003b832:
    mul.l r2,r7
L_0003b834:
    sts macl,r2
L_0003b836:
    shlr8 r2
L_0003b838:
    add r2,r4
L_0003b83a:
    mov r5,r2
L_0003b83c:
    shlr8 r2
L_0003b83e:
    mul.l r2,r7
L_0003b840:
    extu.b r5,r5
L_0003b842:
    sts macl,r1
L_0003b844:
    mul.l r5,r7
L_0003b846:
    shll8 r1
L_0003b848:
    sts macl,r2
L_0003b84a:
    add r2,r1
L_0003b84c:
    mov r4,r2
L_0003b84e:
    shlr8 r2
L_0003b850:
    add r2,r1
L_0003b852:
    mov.l P_0003b9b0,r2
L_0003b854:
    extu.b r4,r4
L_0003b856:
    mov.l r1,@r15
L_0003b858:
    mov.b @r2,r6
L_0003b85a:
    mov.l r4,@(0x4,r15)
L_0003b85c:
    extu.b r6,r2
L_0003b85e:
    mul.l r14,r2
L_0003b860:
    sts macl,r0
L_0003b862:
    tst r0,r0
L_0003b864:
    bf/s L_0003b870
L_0003b866:
    mov.l r0,@(0x8,r15)
L_0003b868:
    mov.l P_0003b9b4,r2
L_0003b86a:
    mov.l P_0003b9b8,r11
L_0003b86c:
    bra L_0003b8aa
L_0003b86e:
    nop
L_0003b870:
    mov.l P_0003b9b8,r11
L_0003b872:
    jsr @r11
L_0003b874:
    nop
L_0003b876:
    mov.w P_0003b8b8,r2
L_0003b878:
    cmp/hs r2,r0
L_0003b87a:
    bt/s L_0003b8a8
L_0003b87c:
    mov r0,r6
L_0003b87e:
    mov r6,r5
L_0003b880:
    mov.l P_0003b9bc,r6
L_0003b882:
    mov.l @r15,r1
L_0003b884:
    shll8 r5
L_0003b886:
    mov.l @(0x8,r15),r0
L_0003b888:
    jsr @r6
L_0003b88a:
    mov.l r5,@(0xc,r15)
L_0003b88c:
    mov.l @(0x4,r15),r4
L_0003b88e:
    mov r0,r1
L_0003b890:
    shll8 r1
L_0003b892:
    mov.l @(0x8,r15),r0
L_0003b894:
    jsr @r11
L_0003b896:
    add r4,r1
L_0003b898:
    mov.l @(0xc,r15),r5
L_0003b89a:
    mov.l P_0003b9b4,r6
L_0003b89c:
    add r0,r5
L_0003b89e:
    cmp/hi r6,r5
L_0003b8a0:
    bt L_0003b8a4
L_0003b8a2:
    mov r5,r6
L_0003b8a4:
    bra L_0003b8aa
L_0003b8a6:
    mov r6,r2
L_0003b8a8:
    mov.l P_0003b9b4,r2
L_0003b8aa:
    mov.w P_0003b8ba,r6
L_0003b8ac:
    mul.l r2,r6
L_0003b8ae:
    sts macl,r0
L_0003b8b0:
    shlr16 r0
L_0003b8b2:
    mov r0,r6
L_0003b8b4:
    bra L_0003b8da
L_0003b8b6:
    mov.l r0,@(0x54,gbr)
P_0003b8b8:
    .byte 0x07
P_0003b8b9:
    .byte 0x27
P_0003b8ba:
    .byte 0x23
P_0003b8bb:
    .byte 0xcb
    .org 0x32fe2
L_0003b8da:
    mov.l P_0003b9cc,r8
L_0003b8dc:
    mov #0x4c,r0
L_0003b8de:
    mov #-0x1,r13
L_0003b8e0:
    mov.b @(r0,r8),r2
L_0003b8e2:
    extu.w r13,r13
L_0003b8e4:
    extu.b r2,r5
L_0003b8e6:
    mul.l r6,r5
L_0003b8e8:
    mov.l P_0003b9d0,r5
L_0003b8ea:
    sts macl,r6
L_0003b8ec:
    mov.b @(0x5,r5),r0
L_0003b8ee:
    shlr2 r6
L_0003b8f0:
    shlr2 r6
L_0003b8f2:
    shlr2 r6
L_0003b8f4:
    shlr r6
L_0003b8f6:
    cmp/hi r13,r6
L_0003b8f8:
    extu.b r0,r14
L_0003b8fa:
    bf/s L_0003b900
L_0003b8fc:
    mov r6,r5
L_0003b8fe:
    mov r13,r5
L_0003b900:
    mov.l P_0003b9d4,r10
L_0003b902:
    extu.w r5,r5
L_0003b904:
    mov r5,r0
L_0003b906:
    mov.w r0,@(0x1a,r10)
    .org 0x33094
P_0003b98c:
    .byte 0xff
P_0003b98d:
    .byte 0xff
P_0003b98e:
    .byte 0x1d
P_0003b98f:
    .byte 0xec
    .org 0x330a8
P_0003b9a0:
    .byte 0xff
P_0003b9a1:
    .byte 0xff
P_0003b9a2:
    .byte 0x24
P_0003b9a3:
    .byte 0x60
P_0003b9a4:
    .byte 0xff
P_0003b9a5:
    .byte 0xff
P_0003b9a6:
    .byte 0x11
P_0003b9a7:
    .byte 0xd4
P_0003b9a8:
    .byte 0x00
P_0003b9a9:
    .byte 0x00
P_0003b9aa:
    .byte 0x92
P_0003b9ab:
    .byte 0x84
P_0003b9ac:
    .byte 0x00
P_0003b9ad:
    .byte 0x00
P_0003b9ae:
    .byte 0x8a
P_0003b9af:
    .byte 0x27
P_0003b9b0:
    .byte 0x00
P_0003b9b1:
    .byte 0x00
P_0003b9b2:
    .byte 0x88
P_0003b9b3:
    .byte 0xfb
P_0003b9b4:
    .byte 0x00
P_0003b9b5:
    .byte 0x07
P_0003b9b6:
    .byte 0x26
P_0003b9b7:
    .byte 0xf9
P_0003b9b8:
    .byte 0x00
P_0003b9b9:
    .byte 0x02
P_0003b9ba:
    .byte 0x1c
P_0003b9bb:
    .byte 0xe0
P_0003b9bc:
    .byte 0x00
P_0003b9bd:
    .byte 0x02
P_0003b9be:
    .byte 0x1f
P_0003b9bf:
    .byte 0x40
    .org 0x330d4
P_0003b9cc:
    .byte 0xff
P_0003b9cd:
    .byte 0xff
P_0003b9ce:
    .byte 0x11
P_0003b9cf:
    .byte 0x14
P_0003b9d0:
    .byte 0xff
P_0003b9d1:
    .byte 0xff
P_0003b9d2:
    .byte 0x24
P_0003b9d3:
    .byte 0xac
P_0003b9d4:
    .byte 0xff
P_0003b9d5:
    .byte 0xff
P_0003b9d6:
    .byte 0x10
P_0003b9d7:
    .byte 0x48
