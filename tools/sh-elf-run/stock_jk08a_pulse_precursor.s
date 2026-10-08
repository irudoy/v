! Exact natural precursor, unsigned division and signed fixed-point multiplication.
    .text
    .balign 4
    .org 0x94e8 - 0x94e8
L_000094e8:
    .byte 0x00,0xaa
    .org 0x96e0 - 0x94e8
L_000096e0:
    .byte 0x00,0x12,0xc0,0x00
    .org 0x21ce0 - 0x94e8
L_00021ce0:
    mov.l r2,@-r15
    .org 0x21ce2 - 0x94e8
L_00021ce2:
    tst r0,r0
    .org 0x21ce4 - 0x94e8
L_00021ce4:
    bt L_00021d6a
    .org 0x21ce6 - 0x94e8
L_00021ce6:
    extu.w r0,r2
    .org 0x21ce8 - 0x94e8
L_00021ce8:
    cmp/eq r2,r0
    .org 0x21cea - 0x94e8
L_00021cea:
    bf L_00021d76
    .org 0x21cec - 0x94e8
L_00021cec:
    div0u
    .org 0x21cee - 0x94e8
L_00021cee:
    shll8 r0
    .org 0x21cf0 - 0x94e8
L_00021cf0:
    cmp/hi r1,r0
    .org 0x21cf2 - 0x94e8
L_00021cf2:
    bf L_00021d0c
    .org 0x21cf4 - 0x94e8
L_00021cf4:
    div1 r0,r1
    .org 0x21cf6 - 0x94e8
L_00021cf6:
    div1 r0,r1
    .org 0x21cf8 - 0x94e8
L_00021cf8:
    div1 r0,r1
    .org 0x21cfa - 0x94e8
L_00021cfa:
    div1 r0,r1
    .org 0x21cfc - 0x94e8
L_00021cfc:
    div1 r0,r1
    .org 0x21cfe - 0x94e8
L_00021cfe:
    div1 r0,r1
    .org 0x21d00 - 0x94e8
L_00021d00:
    div1 r0,r1
    .org 0x21d02 - 0x94e8
L_00021d02:
    div1 r0,r1
    .org 0x21d04 - 0x94e8
L_00021d04:
    rotcl r1
    .org 0x21d06 - 0x94e8
L_00021d06:
    mov.l @r15+,r2
    .org 0x21d08 - 0x94e8
L_00021d08:
    rts
    .org 0x21d0a - 0x94e8
L_00021d0a:
    extu.b r1,r0
    .org 0x21d0c - 0x94e8
L_00021d0c:
    mov.l r3,@-r15
    .org 0x21d0e - 0x94e8
L_00021d0e:
    extu.w r1,r3
    .org 0x21d10 - 0x94e8
L_00021d10:
    shll8 r0
    .org 0x21d12 - 0x94e8
L_00021d12:
    shlr16 r1
    .org 0x21d14 - 0x94e8
L_00021d14:
    div1 r0,r1
    .org 0x21d16 - 0x94e8
L_00021d16:
    div1 r0,r1
    .org 0x21d18 - 0x94e8
L_00021d18:
    div1 r0,r1
    .org 0x21d1a - 0x94e8
L_00021d1a:
    div1 r0,r1
    .org 0x21d1c - 0x94e8
L_00021d1c:
    div1 r0,r1
    .org 0x21d1e - 0x94e8
L_00021d1e:
    div1 r0,r1
    .org 0x21d20 - 0x94e8
L_00021d20:
    div1 r0,r1
    .org 0x21d22 - 0x94e8
L_00021d22:
    div1 r0,r1
    .org 0x21d24 - 0x94e8
L_00021d24:
    div1 r0,r1
    .org 0x21d26 - 0x94e8
L_00021d26:
    div1 r0,r1
    .org 0x21d28 - 0x94e8
L_00021d28:
    div1 r0,r1
    .org 0x21d2a - 0x94e8
L_00021d2a:
    div1 r0,r1
    .org 0x21d2c - 0x94e8
L_00021d2c:
    div1 r0,r1
    .org 0x21d2e - 0x94e8
L_00021d2e:
    div1 r0,r1
    .org 0x21d30 - 0x94e8
L_00021d30:
    div1 r0,r1
    .org 0x21d32 - 0x94e8
L_00021d32:
    div1 r0,r1
    .org 0x21d34 - 0x94e8
L_00021d34:
    extu.w r1,r2
    .org 0x21d36 - 0x94e8
L_00021d36:
    xor r2,r1
    .org 0x21d38 - 0x94e8
L_00021d38:
    addc r2,r2
    .org 0x21d3a - 0x94e8
L_00021d3a:
    shll16 r2
    .org 0x21d3c - 0x94e8
L_00021d3c:
    add r3,r1
    .org 0x21d3e - 0x94e8
L_00021d3e:
    div1 r0,r1
    .org 0x21d40 - 0x94e8
L_00021d40:
    div1 r0,r1
    .org 0x21d42 - 0x94e8
L_00021d42:
    div1 r0,r1
    .org 0x21d44 - 0x94e8
L_00021d44:
    div1 r0,r1
    .org 0x21d46 - 0x94e8
L_00021d46:
    div1 r0,r1
    .org 0x21d48 - 0x94e8
L_00021d48:
    div1 r0,r1
    .org 0x21d4a - 0x94e8
L_00021d4a:
    div1 r0,r1
    .org 0x21d4c - 0x94e8
L_00021d4c:
    div1 r0,r1
    .org 0x21d4e - 0x94e8
L_00021d4e:
    div1 r0,r1
    .org 0x21d50 - 0x94e8
L_00021d50:
    div1 r0,r1
    .org 0x21d52 - 0x94e8
L_00021d52:
    div1 r0,r1
    .org 0x21d54 - 0x94e8
L_00021d54:
    div1 r0,r1
    .org 0x21d56 - 0x94e8
L_00021d56:
    div1 r0,r1
    .org 0x21d58 - 0x94e8
L_00021d58:
    div1 r0,r1
    .org 0x21d5a - 0x94e8
L_00021d5a:
    div1 r0,r1
    .org 0x21d5c - 0x94e8
L_00021d5c:
    div1 r0,r1
    .org 0x21d5e - 0x94e8
L_00021d5e:
    rotcl r1
    .org 0x21d60 - 0x94e8
L_00021d60:
    extu.w r1,r0
    .org 0x21d62 - 0x94e8
L_00021d62:
    add r2,r0
    .org 0x21d64 - 0x94e8
L_00021d64:
    mov.l @r15+,r3
    .org 0x21d66 - 0x94e8
L_00021d66:
    rts
    .org 0x21d68 - 0x94e8
L_00021d68:
    mov.l @r15+,r2
    .org 0x21d6a - 0x94e8
L_00021d6a:
    mov.l L_00021dc8,r1
    .org 0x21d6c - 0x94e8
L_00021d6c:
    mov.l L_00021dcc,r2
    .org 0x21d6e - 0x94e8
L_00021d6e:
    mov.l r2,@r1
    .org 0x21d70 - 0x94e8
L_00021d70:
    mov #0x0,r0
    .org 0x21d72 - 0x94e8
L_00021d72:
    rts
    .org 0x21d74 - 0x94e8
L_00021d74:
    mov.l @r15+,r2
    .org 0x21d76 - 0x94e8
L_00021d76:
    div0u
    .org 0x21d78 - 0x94e8
L_00021d78:
    extu.w r1,r2
    .org 0x21d7a - 0x94e8
L_00021d7a:
    shll16 r2
    .org 0x21d7c - 0x94e8
L_00021d7c:
    shlr16 r1
    .org 0x21d7e - 0x94e8
L_00021d7e:
    rotcl r2
    .org 0x21d80 - 0x94e8
L_00021d80:
    div1 r0,r1
    .org 0x21d82 - 0x94e8
L_00021d82:
    rotcl r2
    .org 0x21d84 - 0x94e8
L_00021d84:
    div1 r0,r1
    .org 0x21d86 - 0x94e8
L_00021d86:
    rotcl r2
    .org 0x21d88 - 0x94e8
L_00021d88:
    div1 r0,r1
    .org 0x21d8a - 0x94e8
L_00021d8a:
    rotcl r2
    .org 0x21d8c - 0x94e8
L_00021d8c:
    div1 r0,r1
    .org 0x21d8e - 0x94e8
L_00021d8e:
    rotcl r2
    .org 0x21d90 - 0x94e8
L_00021d90:
    div1 r0,r1
    .org 0x21d92 - 0x94e8
L_00021d92:
    rotcl r2
    .org 0x21d94 - 0x94e8
L_00021d94:
    div1 r0,r1
    .org 0x21d96 - 0x94e8
L_00021d96:
    rotcl r2
    .org 0x21d98 - 0x94e8
L_00021d98:
    div1 r0,r1
    .org 0x21d9a - 0x94e8
L_00021d9a:
    rotcl r2
    .org 0x21d9c - 0x94e8
L_00021d9c:
    div1 r0,r1
    .org 0x21d9e - 0x94e8
L_00021d9e:
    rotcl r2
    .org 0x21da0 - 0x94e8
L_00021da0:
    div1 r0,r1
    .org 0x21da2 - 0x94e8
L_00021da2:
    rotcl r2
    .org 0x21da4 - 0x94e8
L_00021da4:
    div1 r0,r1
    .org 0x21da6 - 0x94e8
L_00021da6:
    rotcl r2
    .org 0x21da8 - 0x94e8
L_00021da8:
    div1 r0,r1
    .org 0x21daa - 0x94e8
L_00021daa:
    rotcl r2
    .org 0x21dac - 0x94e8
L_00021dac:
    div1 r0,r1
    .org 0x21dae - 0x94e8
L_00021dae:
    rotcl r2
    .org 0x21db0 - 0x94e8
L_00021db0:
    div1 r0,r1
    .org 0x21db2 - 0x94e8
L_00021db2:
    rotcl r2
    .org 0x21db4 - 0x94e8
L_00021db4:
    div1 r0,r1
    .org 0x21db6 - 0x94e8
L_00021db6:
    rotcl r2
    .org 0x21db8 - 0x94e8
L_00021db8:
    div1 r0,r1
    .org 0x21dba - 0x94e8
L_00021dba:
    rotcl r2
    .org 0x21dbc - 0x94e8
L_00021dbc:
    div1 r0,r1
    .org 0x21dbe - 0x94e8
L_00021dbe:
    rotcl r2
    .org 0x21dc0 - 0x94e8
L_00021dc0:
    mov r2,r0
    .org 0x21dc2 - 0x94e8
L_00021dc2:
    rts
    .org 0x21dc4 - 0x94e8
L_00021dc4:
    mov.l @r15+,r2
    .org 0x21dc8 - 0x94e8
L_00021dc8:
    .long 0xffff9818
    .org 0x21dcc - 0x94e8
L_00021dcc:
    .long 0x0000044e
    .org 0x2657c - 0x94e8
L_0002657c:
    sts.l macl,@-r15
    .org 0x2657e - 0x94e8
L_0002657e:
    mov r4,r3
    .org 0x26580 - 0x94e8
L_00026580:
    cmp/pz r4
    .org 0x26582 - 0x94e8
L_00026582:
    bt L_00026586
    .org 0x26584 - 0x94e8
L_00026584:
    neg r4,r4
    .org 0x26586 - 0x94e8
L_00026586:
    mulu.w r4,r5
    .org 0x26588 - 0x94e8
L_00026588:
    sts macl,r1
    .org 0x2658a - 0x94e8
L_0002658a:
    swap.w r4,r4
    .org 0x2658c - 0x94e8
L_0002658c:
    mulu.w r4,r5
    .org 0x2658e - 0x94e8
L_0002658e:
    sts macl,r0
    .org 0x26590 - 0x94e8
L_00026590:
    mov r1,r2
    .org 0x26592 - 0x94e8
L_00026592:
    shlr16 r2
    .org 0x26594 - 0x94e8
L_00026594:
    add r2,r0
    .org 0x26596 - 0x94e8
L_00026596:
    swap.w r1,r1
    .org 0x26598 - 0x94e8
L_00026598:
    sub r4,r4
    .org 0x2659a - 0x94e8
L_0002659a:
    exts.b r6,r6
    .org 0x2659c - 0x94e8
L_0002659c:
    cmp/pz r6
    .org 0x2659e - 0x94e8
L_0002659e:
    bt L_000265a4
    .org 0x265a0 - 0x94e8
L_000265a0:
    bra L_000265ae
    .org 0x265a2 - 0x94e8
L_000265a2:
    neg r6,r6
    .org 0x265a4 - 0x94e8
L_000265a4:
    cmp/eq r4,r6
    .org 0x265a6 - 0x94e8
L_000265a6:
    bt L_000265ba
    .org 0x265a8 - 0x94e8
L_000265a8:
    shlr r0
    .org 0x265aa - 0x94e8
L_000265aa:
    bra L_000265a4
    .org 0x265ac - 0x94e8
L_000265ac:
    add #-0x1,r6
    .org 0x265ae - 0x94e8
L_000265ae:
    cmp/eq r4,r6
    .org 0x265b0 - 0x94e8
L_000265b0:
    bt L_000265ba
    .org 0x265b2 - 0x94e8
L_000265b2:
    shll r1
    .org 0x265b4 - 0x94e8
L_000265b4:
    rotcl r0
    .org 0x265b6 - 0x94e8
L_000265b6:
    bra L_000265ae
    .org 0x265b8 - 0x94e8
L_000265b8:
    add #-0x1,r6
    .org 0x265ba - 0x94e8
L_000265ba:
    cmp/pz r3
    .org 0x265bc - 0x94e8
L_000265bc:
    bt L_000265c0
    .org 0x265be - 0x94e8
L_000265be:
    neg r0,r0
    .org 0x265c0 - 0x94e8
L_000265c0:
    rts
    .org 0x265c2 - 0x94e8
L_000265c2:
    lds.l @r15+,macl
    .org 0x4e974 - 0x94e8
L_0004e974:
    mov.l r8,@-r15
    .org 0x4e976 - 0x94e8
L_0004e976:
    mov.l r9,@-r15
    .org 0x4e978 - 0x94e8
L_0004e978:
    mov.l r10,@-r15
    .org 0x4e97a - 0x94e8
L_0004e97a:
    mov.l r11,@-r15
    .org 0x4e97c - 0x94e8
L_0004e97c:
    mov.l r12,@-r15
    .org 0x4e97e - 0x94e8
L_0004e97e:
    mov.l r13,@-r15
    .org 0x4e980 - 0x94e8
L_0004e980:
    mov.l r14,@-r15
    .org 0x4e982 - 0x94e8
L_0004e982:
    sts.l pr,@-r15
    .org 0x4e984 - 0x94e8
L_0004e984:
    sts.l macl,@-r15
    .org 0x4e986 - 0x94e8
L_0004e986:
    stc.l gbr,@-r15
    .org 0x4e988 - 0x94e8
L_0004e988:
    mov.l L_0004ebe8,r0
    .org 0x4e98a - 0x94e8
L_0004e98a:
    ldc r0,gbr
    .org 0x4e98c - 0x94e8
L_0004e98c:
    add #-0x4,r15
    .org 0x4e98e - 0x94e8
L_0004e98e:
    mov.b @(0x1,gbr),r0
    .org 0x4e990 - 0x94e8
L_0004e990:
    tst #0x20,r0
    .org 0x4e992 - 0x94e8
L_0004e992:
    bt L_0004e9a0
    .org 0x4e994 - 0x94e8
L_0004e994:
    mov.l L_0004ebec,r2
    .org 0x4e996 - 0x94e8
L_0004e996:
    mov #0x30,r0
    .org 0x4e998 - 0x94e8
L_0004e998:
    mov.w @(r0,r2),r13
    .org 0x4e99a - 0x94e8
L_0004e99a:
    extu.w r13,r13
    .org 0x4e99c - 0x94e8
L_0004e99c:
    bra L_0004e9a8
    .org 0x4e99e - 0x94e8
L_0004e99e:
    mov r13,r12
    .org 0x4e9a0 - 0x94e8
L_0004e9a0:
    mov.l L_0004ebf0,r6
    .org 0x4e9a2 - 0x94e8
L_0004e9a2:
    mov.w @r6,r2
    .org 0x4e9a4 - 0x94e8
L_0004e9a4:
    extu.w r2,r12
    .org 0x4e9a6 - 0x94e8
L_0004e9a6:
    mov r12,r13
    .org 0x4e9a8 - 0x94e8
L_0004e9a8:
    mov.b @(0x76,gbr),r0
    .org 0x4e9aa - 0x94e8
L_0004e9aa:
    tst #0x1,r0
    .org 0x4e9ac - 0x94e8
L_0004e9ac:
    bt L_0004e9ea
    .org 0x4e9ae - 0x94e8
L_0004e9ae:
    mov.l L_0004ebf4,r2
    .org 0x4e9b0 - 0x94e8
L_0004e9b0:
    mov #0x20,r0
    .org 0x4e9b2 - 0x94e8
L_0004e9b2:
    mov.w @(r0,r2),r6
    .org 0x4e9b4 - 0x94e8
L_0004e9b4:
    extu.w r6,r6
    .org 0x4e9b6 - 0x94e8
L_0004e9b6:
    tst r6,r6
    .org 0x4e9b8 - 0x94e8
L_0004e9b8:
    bt L_0004e9ca
    .org 0x4e9ba - 0x94e8
L_0004e9ba:
    mov.l L_0004ebf8,r4
    .org 0x4e9bc - 0x94e8
L_0004e9bc:
    mov r6,r0
    .org 0x4e9be - 0x94e8
L_0004e9be:
    mov.l L_0004ebfc,r2
    .org 0x4e9c0 - 0x94e8
L_0004e9c0:
    mov.l @r4,r5
    .org 0x4e9c2 - 0x94e8
L_0004e9c2:
    jsr @r2
    .org 0x4e9c4 - 0x94e8
L_0004e9c4:
    mov r5,r1
    .org 0x4e9c6 - 0x94e8
L_0004e9c6:
    bra L_0004e9cc
    .org 0x4e9c8 - 0x94e8
L_0004e9c8:
    mov r0,r6
    .org 0x4e9ca - 0x94e8
L_0004e9ca:
    mov #-0x1,r6
    .org 0x4e9cc - 0x94e8
L_0004e9cc:
    mov.l L_0004ec00,r2
    .org 0x4e9ce - 0x94e8
L_0004e9ce:
    mov.w L_0004eaca,r0
    .org 0x4e9d0 - 0x94e8
L_0004e9d0:
    mov.w @(r0,r2),r5
    .org 0x4e9d2 - 0x94e8
L_0004e9d2:
    extu.w r5,r5
    .org 0x4e9d4 - 0x94e8
L_0004e9d4:
    cmp/hs r6,r5
    .org 0x4e9d6 - 0x94e8
L_0004e9d6:
    bt/s L_0004e9dc
    .org 0x4e9d8 - 0x94e8
L_0004e9d8:
    mov r5,r2
    .org 0x4e9da - 0x94e8
L_0004e9da:
    mov r6,r2
    .org 0x4e9dc - 0x94e8
L_0004e9dc:
    cmp/hi r12,r2
    .org 0x4e9de - 0x94e8
L_0004e9de:
    bf L_0004e9e2
    .org 0x4e9e0 - 0x94e8
L_0004e9e0:
    mov r12,r2
    .org 0x4e9e2 - 0x94e8
L_0004e9e2:
    mov.l L_0004ec04,r14
    .org 0x4e9e4 - 0x94e8
L_0004e9e4:
    mov r2,r13
    .org 0x4e9e6 - 0x94e8
L_0004e9e6:
    mov.w L_0004eacc,r0
    .org 0x4e9e8 - 0x94e8
L_0004e9e8:
    mov.w r2,@(r0,r14)
    .org 0x4e9ea - 0x94e8
L_0004e9ea:
    mov.l L_0004ec08,r14
    .org 0x4e9ec - 0x94e8
L_0004e9ec:
    mov #0x64,r9
    .org 0x4e9ee - 0x94e8
L_0004e9ee:
    mov #-0x1,r10
    .org 0x4e9f0 - 0x94e8
L_0004e9f0:
    mov.w L_0004eace,r8
    .org 0x4e9f2 - 0x94e8
L_0004e9f2:
    mov.w @(0xa,r14),r0
    .org 0x4e9f4 - 0x94e8
L_0004e9f4:
    shll8 r9
    .org 0x4e9f6 - 0x94e8
L_0004e9f6:
    extu.w r10,r10
    .org 0x4e9f8 - 0x94e8
L_0004e9f8:
    extu.w r0,r2
    .org 0x4e9fa - 0x94e8
L_0004e9fa:
    mul.l r13,r2
    .org 0x4e9fc - 0x94e8
L_0004e9fc:
    mov #0x0,r12
    .org 0x4e9fe - 0x94e8
L_0004e9fe:
    sts macl,r13
    .org 0x4ea00 - 0x94e8
L_0004ea00:
    shlr16 r13
    .org 0x4ea02 - 0x94e8
L_0004ea02:
    shlr r13
    .org 0x4ea04 - 0x94e8
L_0004ea04:
    mov.l L_0004ec0c,r2
    .org 0x4ea06 - 0x94e8
L_0004ea06:
    extu.b r12,r12
    .org 0x4ea08 - 0x94e8
L_0004ea08:
    mov r12,r11
    .org 0x4ea0a - 0x94e8
L_0004ea0a:
    shll r11
    .org 0x4ea0c - 0x94e8
L_0004ea0c:
    add #0x2,r2
    .org 0x4ea0e - 0x94e8
L_0004ea0e:
    mov r11,r0
    .org 0x4ea10 - 0x94e8
L_0004ea10:
    mov.w @(r0,r2),r6
    .org 0x4ea12 - 0x94e8
L_0004ea12:
    mov #0x24,r0
    .org 0x4ea14 - 0x94e8
L_0004ea14:
    mov.l L_0004ec08,r3
    .org 0x4ea16 - 0x94e8
L_0004ea16:
    extu.w r6,r6
    .org 0x4ea18 - 0x94e8
L_0004ea18:
    mul.l r6,r13
    .org 0x4ea1a - 0x94e8
L_0004ea1a:
    mov.l L_0004ebfc,r6
    .org 0x4ea1c - 0x94e8
L_0004ea1c:
    mov.w @(r0,r3),r14
    .org 0x4ea1e - 0x94e8
L_0004ea1e:
    mov r9,r0
    .org 0x4ea20 - 0x94e8
L_0004ea20:
    jsr @r6
    .org 0x4ea22 - 0x94e8
L_0004ea22:
    sts macl,r1
    .org 0x4ea24 - 0x94e8
L_0004ea24:
    mov r0,r4
    .org 0x4ea26 - 0x94e8
L_0004ea26:
    mov.l L_0004ec04,r3
    .org 0x4ea28 - 0x94e8
L_0004ea28:
    mov.w L_0004ead0,r0
    .org 0x4ea2a - 0x94e8
L_0004ea2a:
    add r14,r4
    .org 0x4ea2c - 0x94e8
L_0004ea2c:
    mov.l L_0004ec10,r7
    .org 0x4ea2e - 0x94e8
L_0004ea2e:
    mov #-0x2,r6
    .org 0x4ea30 - 0x94e8
L_0004ea30:
    mov.w @(r0,r3),r2
    .org 0x4ea32 - 0x94e8
L_0004ea32:
    jsr @r7
    .org 0x4ea34 - 0x94e8
L_0004ea34:
    extu.w r2,r5
    .org 0x4ea36 - 0x94e8
L_0004ea36:
    cmp/gt r10,r0
    .org 0x4ea38 - 0x94e8
L_0004ea38:
    bf/s L_0004ea3e
    .org 0x4ea3a - 0x94e8
L_0004ea3a:
    mov r0,r2
    .org 0x4ea3c - 0x94e8
L_0004ea3c:
    mov r10,r2
    .org 0x4ea3e - 0x94e8
L_0004ea3e:
    cmp/pz r2
    .org 0x4ea40 - 0x94e8
L_0004ea40:
    bt/s L_0004ea46
    .org 0x4ea42 - 0x94e8
L_0004ea42:
    mov r2,r14
    .org 0x4ea44 - 0x94e8
L_0004ea44:
    mov #0x0,r14
    .org 0x4ea46 - 0x94e8
L_0004ea46:
    mov.l L_0004ec14,r3
    .org 0x4ea48 - 0x94e8
L_0004ea48:
    mov.w @r3,r6
    .org 0x4ea4a - 0x94e8
L_0004ea4a:
    extu.w r6,r6
    .org 0x4ea4c - 0x94e8
L_0004ea4c:
    cmp/gt r6,r14
    .org 0x4ea4e - 0x94e8
L_0004ea4e:
    bt L_0004ea52
    .org 0x4ea50 - 0x94e8
L_0004ea50:
    mov r6,r14
    .org 0x4ea52 - 0x94e8
L_0004ea52:
    mov.l L_0004ec04,r2
    .org 0x4ea54 - 0x94e8
L_0004ea54:
    add #0x1,r12
    .org 0x4ea56 - 0x94e8
L_0004ea56:
    extu.b r12,r12
    .org 0x4ea58 - 0x94e8
L_0004ea58:
    mov r11,r0
    .org 0x4ea5a - 0x94e8
L_0004ea5a:
    mov #0x2,r6
    .org 0x4ea5c - 0x94e8
L_0004ea5c:
    add r8,r2
    .org 0x4ea5e - 0x94e8
L_0004ea5e:
    cmp/ge r6,r12
    .org 0x4ea60 - 0x94e8
L_0004ea60:
    bf/s L_0004ea04
    .org 0x4ea62 - 0x94e8
L_0004ea62:
    mov.w r14,@(r0,r2)
    .org 0x4ea64 - 0x94e8
L_0004ea64:
    mov.l L_0004ec08,r3
    .org 0x4ea66 - 0x94e8
L_0004ea66:
    mov #0x24,r0
    .org 0x4ea68 - 0x94e8
L_0004ea68:
    mov.l L_0004ec04,r1
    .org 0x4ea6a - 0x94e8
L_0004ea6a:
    mov #-0x2,r6
    .org 0x4ea6c - 0x94e8
L_0004ea6c:
    mov.w @(r0,r3),r2
    .org 0x4ea6e - 0x94e8
L_0004ea6e:
    mov.w L_0004ead0,r0
    .org 0x4ea70 - 0x94e8
L_0004ea70:
    add r2,r13
    .org 0x4ea72 - 0x94e8
L_0004ea72:
    mov.l L_0004ec10,r7
    .org 0x4ea74 - 0x94e8
L_0004ea74:
    mov.w @(r0,r1),r2
    .org 0x4ea76 - 0x94e8
L_0004ea76:
    mov r13,r4
    .org 0x4ea78 - 0x94e8
L_0004ea78:
    jsr @r7
    .org 0x4ea7a - 0x94e8
L_0004ea7a:
    extu.w r2,r5
    .org 0x4ea7c - 0x94e8
L_0004ea7c:
    mov r0,r6
    .org 0x4ea7e - 0x94e8
L_0004ea7e:
    mov.b @(0x45,gbr),r0
    .org 0x4ea80 - 0x94e8
L_0004ea80:
    cmp/gt r10,r6
    .org 0x4ea82 - 0x94e8
L_0004ea82:
    bf/s L_0004ea88
    .org 0x4ea84 - 0x94e8
L_0004ea84:
    mov r0,r5
    .org 0x4ea86 - 0x94e8
L_0004ea86:
    mov r10,r6
    .org 0x4ea88 - 0x94e8
L_0004ea88:
    cmp/pz r6
    .org 0x4ea8a - 0x94e8
L_0004ea8a:
    bt/s L_0004ea92
    .org 0x4ea8c - 0x94e8
L_0004ea8c:
    mov.l r6,@r15
    .org 0x4ea8e - 0x94e8
L_0004ea8e:
    mov #0x0,r6
    .org 0x4ea90 - 0x94e8
L_0004ea90:
    mov.l r6,@r15
    .org 0x4ea92 - 0x94e8
L_0004ea92:
    mov.l L_0004ec14,r3
    .org 0x4ea94 - 0x94e8
L_0004ea94:
    mov.w @r3,r4
    .org 0x4ea96 - 0x94e8
L_0004ea96:
    extu.w r4,r4
    .org 0x4ea98 - 0x94e8
L_0004ea98:
    cmp/gt r4,r6
    .org 0x4ea9a - 0x94e8
L_0004ea9a:
    bt L_0004eaa4
    .org 0x4ea9c - 0x94e8
L_0004ea9c:
    mov r5,r0
    .org 0x4ea9e - 0x94e8
L_0004ea9e:
    or #0x1,r0
    .org 0x4eaa0 - 0x94e8
L_0004eaa0:
    bra L_0004eaa8
    .org 0x4eaa2 - 0x94e8
L_0004eaa2:
    mov.l r4,@r15
    .org 0x4eaa4 - 0x94e8
L_0004eaa4:
    mov r5,r0
    .org 0x4eaa6 - 0x94e8
L_0004eaa6:
    and #0xfe,r0
    .org 0x4eaa8 - 0x94e8
L_0004eaa8:
    mov.b r0,@(0x45,gbr)
    .org 0x4eaaa - 0x94e8
L_0004eaaa:
    mov.l @r15,r6
    .org 0x4eaac - 0x94e8
L_0004eaac:
    mov.l L_0004ec04,r3
    .org 0x4eaae - 0x94e8
L_0004eaae:
    mov.w L_0004ead2,r0
    .org 0x4eab0 - 0x94e8
L_0004eab0:
    mov.w r6,@(r0,r3)
    .org 0x4eab2 - 0x94e8
L_0004eab2:
    add #0x4,r15
    .org 0x4eab4 - 0x94e8
L_0004eab4:
    ldc.l @r15+,gbr
    .org 0x4eab6 - 0x94e8
L_0004eab6:
    lds.l @r15+,macl
    .org 0x4eab8 - 0x94e8
L_0004eab8:
    lds.l @r15+,pr
    .org 0x4eaba - 0x94e8
L_0004eaba:
    mov.l @r15+,r14
    .org 0x4eabc - 0x94e8
L_0004eabc:
    mov.l @r15+,r13
    .org 0x4eabe - 0x94e8
L_0004eabe:
    mov.l @r15+,r12
    .org 0x4eac0 - 0x94e8
L_0004eac0:
    mov.l @r15+,r11
    .org 0x4eac2 - 0x94e8
L_0004eac2:
    mov.l @r15+,r10
    .org 0x4eac4 - 0x94e8
L_0004eac4:
    mov.l @r15+,r9
    .org 0x4eac6 - 0x94e8
L_0004eac6:
    rts
    .org 0x4eac8 - 0x94e8
L_0004eac8:
    mov.l @r15+,r8
    .org 0x4eaca - 0x94e8
L_0004eaca:
    .word 0x0bfe
    .org 0x4eacc - 0x94e8
L_0004eacc:
    .word 0x06de
    .org 0x4eace - 0x94e8
L_0004eace:
    .word 0x0634
    .org 0x4ead0 - 0x94e8
L_0004ead0:
    .word 0x03d2
    .org 0x4ead2 - 0x94e8
L_0004ead2:
    .word 0x05ea
    .org 0x4ebe8 - 0x94e8
L_0004ebe8:
    .long 0xffff245c
    .org 0x4ebec - 0x94e8
L_0004ebec:
    .long 0xffff120e
    .org 0x4ebf0 - 0x94e8
L_0004ebf0:
    .long 0xffff1024
    .org 0x4ebf4 - 0x94e8
L_0004ebf4:
    .long 0xffff119c
    .org 0x4ebf8 - 0x94e8
L_0004ebf8:
    .long 0x000096e0
    .org 0x4ebfc - 0x94e8
L_0004ebfc:
    .long 0x00021ce0
    .org 0x4ec00 - 0x94e8
L_0004ec00:
    .long 0xffff28f8
    .org 0x4ec04 - 0x94e8
L_0004ec04:
    .long 0xffff128c
    .org 0x4ec08 - 0x94e8
L_0004ec08:
    .long 0xffff22dc
    .org 0x4ec0c - 0x94e8
L_0004ec0c:
    .long 0xffff40b4
    .org 0x4ec10 - 0x94e8
L_0004ec10:
    .long 0x0002657c
    .org 0x4ec14 - 0x94e8
L_0004ec14:
    .long 0x000094e8
