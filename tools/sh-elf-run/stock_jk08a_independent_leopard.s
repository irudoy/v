! Explicit stock independent-leopard loop and natural byte-lookup/divider closure.
! The separately assembled observing return lies outside these stock spans.
    .text
    .balign 4
    .set ORIGIN,0x21ce0
    .org 0x21ce0-ORIGIN
L_00021ce0:
    mov.l r2,@-r15
    .org 0x21ce2-ORIGIN
L_00021ce2:
    tst r0,r0
    .org 0x21ce4-ORIGIN
L_00021ce4:
    bt L_00021d6a
    .org 0x21ce6-ORIGIN
L_00021ce6:
    extu.w r0,r2
    .org 0x21ce8-ORIGIN
L_00021ce8:
    cmp/eq r2,r0
    .org 0x21cea-ORIGIN
L_00021cea:
    bf L_00021d76
    .org 0x21cec-ORIGIN
L_00021cec:
    div0u
    .org 0x21cee-ORIGIN
L_00021cee:
    shll8 r0
    .org 0x21cf0-ORIGIN
L_00021cf0:
    cmp/hi r1,r0
    .org 0x21cf2-ORIGIN
L_00021cf2:
    bf L_00021d0c
    .org 0x21cf4-ORIGIN
L_00021cf4:
    div1 r0,r1
    .org 0x21cf6-ORIGIN
L_00021cf6:
    div1 r0,r1
    .org 0x21cf8-ORIGIN
L_00021cf8:
    div1 r0,r1
    .org 0x21cfa-ORIGIN
L_00021cfa:
    div1 r0,r1
    .org 0x21cfc-ORIGIN
L_00021cfc:
    div1 r0,r1
    .org 0x21cfe-ORIGIN
L_00021cfe:
    div1 r0,r1
    .org 0x21d00-ORIGIN
L_00021d00:
    div1 r0,r1
    .org 0x21d02-ORIGIN
L_00021d02:
    div1 r0,r1
    .org 0x21d04-ORIGIN
L_00021d04:
    rotcl r1
    .org 0x21d06-ORIGIN
L_00021d06:
    mov.l @r15+,r2
    .org 0x21d08-ORIGIN
L_00021d08:
    rts
    .org 0x21d0a-ORIGIN
L_00021d0a:
    extu.b r1,r0
    .org 0x21d0c-ORIGIN
L_00021d0c:
    mov.l r3,@-r15
    .org 0x21d0e-ORIGIN
L_00021d0e:
    extu.w r1,r3
    .org 0x21d10-ORIGIN
L_00021d10:
    shll8 r0
    .org 0x21d12-ORIGIN
L_00021d12:
    shlr16 r1
    .org 0x21d14-ORIGIN
L_00021d14:
    div1 r0,r1
    .org 0x21d16-ORIGIN
L_00021d16:
    div1 r0,r1
    .org 0x21d18-ORIGIN
L_00021d18:
    div1 r0,r1
    .org 0x21d1a-ORIGIN
L_00021d1a:
    div1 r0,r1
    .org 0x21d1c-ORIGIN
L_00021d1c:
    div1 r0,r1
    .org 0x21d1e-ORIGIN
L_00021d1e:
    div1 r0,r1
    .org 0x21d20-ORIGIN
L_00021d20:
    div1 r0,r1
    .org 0x21d22-ORIGIN
L_00021d22:
    div1 r0,r1
    .org 0x21d24-ORIGIN
L_00021d24:
    div1 r0,r1
    .org 0x21d26-ORIGIN
L_00021d26:
    div1 r0,r1
    .org 0x21d28-ORIGIN
L_00021d28:
    div1 r0,r1
    .org 0x21d2a-ORIGIN
L_00021d2a:
    div1 r0,r1
    .org 0x21d2c-ORIGIN
L_00021d2c:
    div1 r0,r1
    .org 0x21d2e-ORIGIN
L_00021d2e:
    div1 r0,r1
    .org 0x21d30-ORIGIN
L_00021d30:
    div1 r0,r1
    .org 0x21d32-ORIGIN
L_00021d32:
    div1 r0,r1
    .org 0x21d34-ORIGIN
L_00021d34:
    extu.w r1,r2
    .org 0x21d36-ORIGIN
L_00021d36:
    xor r2,r1
    .org 0x21d38-ORIGIN
L_00021d38:
    addc r2,r2
    .org 0x21d3a-ORIGIN
L_00021d3a:
    shll16 r2
    .org 0x21d3c-ORIGIN
L_00021d3c:
    add r3,r1
    .org 0x21d3e-ORIGIN
L_00021d3e:
    div1 r0,r1
    .org 0x21d40-ORIGIN
L_00021d40:
    div1 r0,r1
    .org 0x21d42-ORIGIN
L_00021d42:
    div1 r0,r1
    .org 0x21d44-ORIGIN
L_00021d44:
    div1 r0,r1
    .org 0x21d46-ORIGIN
L_00021d46:
    div1 r0,r1
    .org 0x21d48-ORIGIN
L_00021d48:
    div1 r0,r1
    .org 0x21d4a-ORIGIN
L_00021d4a:
    div1 r0,r1
    .org 0x21d4c-ORIGIN
L_00021d4c:
    div1 r0,r1
    .org 0x21d4e-ORIGIN
L_00021d4e:
    div1 r0,r1
    .org 0x21d50-ORIGIN
L_00021d50:
    div1 r0,r1
    .org 0x21d52-ORIGIN
L_00021d52:
    div1 r0,r1
    .org 0x21d54-ORIGIN
L_00021d54:
    div1 r0,r1
    .org 0x21d56-ORIGIN
L_00021d56:
    div1 r0,r1
    .org 0x21d58-ORIGIN
L_00021d58:
    div1 r0,r1
    .org 0x21d5a-ORIGIN
L_00021d5a:
    div1 r0,r1
    .org 0x21d5c-ORIGIN
L_00021d5c:
    div1 r0,r1
    .org 0x21d5e-ORIGIN
L_00021d5e:
    rotcl r1
    .org 0x21d60-ORIGIN
L_00021d60:
    extu.w r1,r0
    .org 0x21d62-ORIGIN
L_00021d62:
    add r2,r0
    .org 0x21d64-ORIGIN
L_00021d64:
    mov.l @r15+,r3
    .org 0x21d66-ORIGIN
L_00021d66:
    rts
    .org 0x21d68-ORIGIN
L_00021d68:
    mov.l @r15+,r2
    .org 0x21d6a-ORIGIN
L_00021d6a:
    mov.l L_00021dc8,r1
    .org 0x21d6c-ORIGIN
L_00021d6c:
    mov.l L_00021dcc,r2
    .org 0x21d6e-ORIGIN
L_00021d6e:
    mov.l r2,@r1
    .org 0x21d70-ORIGIN
L_00021d70:
    mov #0x0,r0
    .org 0x21d72-ORIGIN
L_00021d72:
    rts
    .org 0x21d74-ORIGIN
L_00021d74:
    mov.l @r15+,r2
    .org 0x21d76-ORIGIN
L_00021d76:
    div0u
    .org 0x21d78-ORIGIN
L_00021d78:
    extu.w r1,r2
    .org 0x21d7a-ORIGIN
L_00021d7a:
    shll16 r2
    .org 0x21d7c-ORIGIN
L_00021d7c:
    shlr16 r1
    .org 0x21d7e-ORIGIN
L_00021d7e:
    rotcl r2
    .org 0x21d80-ORIGIN
L_00021d80:
    div1 r0,r1
    .org 0x21d82-ORIGIN
L_00021d82:
    rotcl r2
    .org 0x21d84-ORIGIN
L_00021d84:
    div1 r0,r1
    .org 0x21d86-ORIGIN
L_00021d86:
    rotcl r2
    .org 0x21d88-ORIGIN
L_00021d88:
    div1 r0,r1
    .org 0x21d8a-ORIGIN
L_00021d8a:
    rotcl r2
    .org 0x21d8c-ORIGIN
L_00021d8c:
    div1 r0,r1
    .org 0x21d8e-ORIGIN
L_00021d8e:
    rotcl r2
    .org 0x21d90-ORIGIN
L_00021d90:
    div1 r0,r1
    .org 0x21d92-ORIGIN
L_00021d92:
    rotcl r2
    .org 0x21d94-ORIGIN
L_00021d94:
    div1 r0,r1
    .org 0x21d96-ORIGIN
L_00021d96:
    rotcl r2
    .org 0x21d98-ORIGIN
L_00021d98:
    div1 r0,r1
    .org 0x21d9a-ORIGIN
L_00021d9a:
    rotcl r2
    .org 0x21d9c-ORIGIN
L_00021d9c:
    div1 r0,r1
    .org 0x21d9e-ORIGIN
L_00021d9e:
    rotcl r2
    .org 0x21da0-ORIGIN
L_00021da0:
    div1 r0,r1
    .org 0x21da2-ORIGIN
L_00021da2:
    rotcl r2
    .org 0x21da4-ORIGIN
L_00021da4:
    div1 r0,r1
    .org 0x21da6-ORIGIN
L_00021da6:
    rotcl r2
    .org 0x21da8-ORIGIN
L_00021da8:
    div1 r0,r1
    .org 0x21daa-ORIGIN
L_00021daa:
    rotcl r2
    .org 0x21dac-ORIGIN
L_00021dac:
    div1 r0,r1
    .org 0x21dae-ORIGIN
L_00021dae:
    rotcl r2
    .org 0x21db0-ORIGIN
L_00021db0:
    div1 r0,r1
    .org 0x21db2-ORIGIN
L_00021db2:
    rotcl r2
    .org 0x21db4-ORIGIN
L_00021db4:
    div1 r0,r1
    .org 0x21db6-ORIGIN
L_00021db6:
    rotcl r2
    .org 0x21db8-ORIGIN
L_00021db8:
    div1 r0,r1
    .org 0x21dba-ORIGIN
L_00021dba:
    rotcl r2
    .org 0x21dbc-ORIGIN
L_00021dbc:
    div1 r0,r1
    .org 0x21dbe-ORIGIN
L_00021dbe:
    rotcl r2
    .org 0x21dc0-ORIGIN
L_00021dc0:
    mov r2,r0
    .org 0x21dc2-ORIGIN
L_00021dc2:
    rts
    .org 0x21dc4-ORIGIN
L_00021dc4:
    mov.l @r15+,r2
    .org 0x21dc8-ORIGIN
L_00021dc8:
    .long 0xffff9818
    .org 0x21dcc-ORIGIN
L_00021dcc:
    .long 0x0000044e
    .org 0x26358-ORIGIN
L_00026358:
    mov.w L_0002636a,r0
    .org 0x2635a-ORIGIN
L_0002635a:
    extu.b r5,r5
    .org 0x2635c-ORIGIN
L_0002635c:
    cmp/hs r0,r5
    .org 0x2635e-ORIGIN
L_0002635e:
    bt L_00026366
    .org 0x26360-ORIGIN
L_00026360:
    mov.l L_0002636c,r6
    .org 0x26362-ORIGIN
L_00026362:
    jmp @r6
    .org 0x26364-ORIGIN
L_00026364:
    mov #0x0,r3
    .org 0x26366-ORIGIN
L_00026366:
    rts
    .org 0x26368-ORIGIN
L_00026368:
    mov.b @(0x3,r4),r0
    .org 0x2636a-ORIGIN
L_0002636a:
    .word 0x00c0
    .org 0x2636c-ORIGIN
L_0002636c:
    .long 0x00026a7c
    .org 0x26740-ORIGIN
L_00026740:
    cmp/hs r0,r2
    .org 0x26742-ORIGIN
L_00026742:
    bt L_0002675c
    .org 0x26744-ORIGIN
L_00026744:
    mov.l r0,@-r15
    .org 0x26746-ORIGIN
L_00026746:
    sub r2,r0
    .org 0x26748-ORIGIN
L_00026748:
    sts macl,r1
    .org 0x2674a-ORIGIN
L_0002674a:
    mul.l r3,r0
    .org 0x2674c-ORIGIN
L_0002674c:
    sts macl,r0
    .org 0x2674e-ORIGIN
L_0002674e:
    lds r1,macl
    .org 0x26750-ORIGIN
L_00026750:
    swap.w r0,r0
    .org 0x26752-ORIGIN
L_00026752:
    mov.l @r15+,r2
    .org 0x26754-ORIGIN
L_00026754:
    extu.w r0,r0
    .org 0x26756-ORIGIN
L_00026756:
    sub r0,r2
    .org 0x26758-ORIGIN
L_00026758:
    rts
    .org 0x2675a-ORIGIN
L_0002675a:
    mov r2,r0
    .org 0x2675c-ORIGIN
L_0002675c:
    sub r0,r2
    .org 0x2675e-ORIGIN
L_0002675e:
    sts macl,r1
    .org 0x26760-ORIGIN
L_00026760:
    mul.l r3,r2
    .org 0x26762-ORIGIN
L_00026762:
    sts macl,r2
    .org 0x26764-ORIGIN
L_00026764:
    lds r1,macl
    .org 0x26766-ORIGIN
L_00026766:
    swap.w r2,r2
    .org 0x26768-ORIGIN
L_00026768:
    extu.w r2,r2
    .org 0x2676a-ORIGIN
L_0002676a:
    rts
    .org 0x2676c-ORIGIN
L_0002676c:
    add r2,r0
    .org 0x26a7c-ORIGIN
L_00026a7c:
    shlr r5
    .org 0x26a7e-ORIGIN
L_00026a7e:
    rotcr r3
    .org 0x26a80-ORIGIN
L_00026a80:
    shlr r5
    .org 0x26a82-ORIGIN
L_00026a82:
    rotcr r3
    .org 0x26a84-ORIGIN
L_00026a84:
    shlr r5
    .org 0x26a86-ORIGIN
L_00026a86:
    rotcr r3
    .org 0x26a88-ORIGIN
L_00026a88:
    shlr r5
    .org 0x26a8a-ORIGIN
L_00026a8a:
    rotcr r3
    .org 0x26a8c-ORIGIN
L_00026a8c:
    shlr r5
    .org 0x26a8e-ORIGIN
L_00026a8e:
    rotcr r3
    .org 0x26a90-ORIGIN
L_00026a90:
    shlr r5
    .org 0x26a92-ORIGIN
L_00026a92:
    rotcr r3
    .org 0x26a94-ORIGIN
L_00026a94:
    swap.w r3,r3
    .org 0x26a96-ORIGIN
L_00026a96:
    shlr8 r0
    .org 0x26a98-ORIGIN
L_00026a98:
    tst r0,r0
    .org 0x26a9a-ORIGIN
L_00026a9a:
    bt L_00026aaa
    .org 0x26a9c-ORIGIN
L_00026a9c:
    shll r5
    .org 0x26a9e-ORIGIN
L_00026a9e:
    add r5,r4
    .org 0x26aa0-ORIGIN
L_00026aa0:
    mov.w @r4,r1
    .org 0x26aa2-ORIGIN
L_00026aa2:
    mov.w @(0x2,r4),r0
    .org 0x26aa4-ORIGIN
L_00026aa4:
    extu.w r0,r2
    .org 0x26aa6-ORIGIN
L_00026aa6:
    bra L_00026ab4
    .org 0x26aa8-ORIGIN
L_00026aa8:
    extu.w r1,r0
    .org 0x26aaa-ORIGIN
L_00026aaa:
    add r5,r4
    .org 0x26aac-ORIGIN
L_00026aac:
    mov.b @r4,r1
    .org 0x26aae-ORIGIN
L_00026aae:
    mov.b @(0x1,r4),r0
    .org 0x26ab0-ORIGIN
L_00026ab0:
    extu.b r0,r2
    .org 0x26ab2-ORIGIN
L_00026ab2:
    extu.b r1,r0
    .org 0x26ab4-ORIGIN
L_00026ab4:
    mov.l L_00026abc,r6
    .org 0x26ab6-ORIGIN
L_00026ab6:
    jmp @r6
    .org 0x26ab8-ORIGIN
L_00026ab8:
    nop
    .org 0x26abc-ORIGIN
L_00026abc:
    .long 0x00026740
    .org 0x5ac54-ORIGIN
L_0005ac54:
    mov.l r8,@-r15
    .org 0x5ac56-ORIGIN
L_0005ac56:
    mov.l r9,@-r15
    .org 0x5ac58-ORIGIN
L_0005ac58:
    mov.l r10,@-r15
    .org 0x5ac5a-ORIGIN
L_0005ac5a:
    mov.l r11,@-r15
    .org 0x5ac5c-ORIGIN
L_0005ac5c:
    mov.l r12,@-r15
    .org 0x5ac5e-ORIGIN
L_0005ac5e:
    mov.l r13,@-r15
    .org 0x5ac60-ORIGIN
L_0005ac60:
    mov.l r14,@-r15
    .org 0x5ac62-ORIGIN
L_0005ac62:
    sts.l pr,@-r15
    .org 0x5ac64-ORIGIN
L_0005ac64:
    sts.l macl,@-r15
    .org 0x5ac66-ORIGIN
L_0005ac66:
    mov #-0x1,r10
    .org 0x5ac68-ORIGIN
L_0005ac68:
    mov.l L_0005ad30,r11
    .org 0x5ac6a-ORIGIN
L_0005ac6a:
    mov #0x7d,r9
    .org 0x5ac6c-ORIGIN
L_0005ac6c:
    mov.l L_0005ad34,r8
    .org 0x5ac6e-ORIGIN
L_0005ac6e:
    extu.b r10,r10
    .org 0x5ac70-ORIGIN
L_0005ac70:
    shll2 r9
    .org 0x5ac72-ORIGIN
L_0005ac72:
    mov #0x0,r13
    .org 0x5ac74-ORIGIN
L_0005ac74:
    extu.w r13,r13
    .org 0x5ac76-ORIGIN
L_0005ac76:
    mov.l L_0005ad2c,r3
    .org 0x5ac78-ORIGIN
L_0005ac78:
    mov r13,r0
    .org 0x5ac7a-ORIGIN
L_0005ac7a:
    shll r0
    .org 0x5ac7c-ORIGIN
L_0005ac7c:
    mov.w @(r0,r3),r2
    .org 0x5ac7e-ORIGIN
L_0005ac7e:
    mov r0,r12
    .org 0x5ac80-ORIGIN
L_0005ac80:
    mov.l L_0005ad38,r1
    .org 0x5ac82-ORIGIN
L_0005ac82:
    extu.w r2,r4
    .org 0x5ac84-ORIGIN
L_0005ac84:
    mov.l L_0005ad3c,r3
    .org 0x5ac86-ORIGIN
L_0005ac86:
    mov.w @(r0,r1),r2
    .org 0x5ac88-ORIGIN
L_0005ac88:
    mov r4,r7
    .org 0x5ac8a-ORIGIN
L_0005ac8a:
    extu.w r2,r5
    .org 0x5ac8c-ORIGIN
L_0005ac8c:
    sub r5,r7
    .org 0x5ac8e-ORIGIN
L_0005ac8e:
    mov.w r7,@(r0,r11)
    .org 0x5ac90-ORIGIN
L_0005ac90:
    mov r13,r0
    .org 0x5ac92-ORIGIN
L_0005ac92:
    mov.b @(r0,r3),r2
    .org 0x5ac94-ORIGIN
L_0005ac94:
    extu.b r2,r2
    .org 0x5ac96-ORIGIN
L_0005ac96:
    mov r2,r6
    .org 0x5ac98-ORIGIN
L_0005ac98:
    add #-0x68,r6
    .org 0x5ac9a-ORIGIN
L_0005ac9a:
    cmp/pz r6
    .org 0x5ac9c-ORIGIN
L_0005ac9c:
    bt/s L_0005aca4
    .org 0x5ac9e-ORIGIN
L_0005ac9e:
    sub r5,r4
    .org 0x5aca0-ORIGIN
L_0005aca0:
    bra L_0005aca6
    .org 0x5aca2-ORIGIN
L_0005aca2:
    mov #0x0,r2
    .org 0x5aca4-ORIGIN
L_0005aca4:
    add #-0x68,r2
    .org 0x5aca6-ORIGIN
L_0005aca6:
    shll r2
    .org 0x5aca8-ORIGIN
L_0005aca8:
    cmp/hi r10,r2
    .org 0x5acaa-ORIGIN
L_0005acaa:
    bf L_0005acae
    .org 0x5acac-ORIGIN
L_0005acac:
    mov r10,r2
    .org 0x5acae-ORIGIN
L_0005acae:
    exts.w r7,r7
    .org 0x5acb0-ORIGIN
L_0005acb0:
    cmp/pz r7
    .org 0x5acb2-ORIGIN
L_0005acb2:
    bt L_0005ad48
    .org 0x5acb4-ORIGIN
L_0005acb4:
    neg r4,r14
    .org 0x5acb6-ORIGIN
L_0005acb6:
    mov.l L_0005ad40,r4
    .org 0x5acb8-ORIGIN
L_0005acb8:
    mov.l L_0005ad44,r3
    .org 0x5acba-ORIGIN
L_0005acba:
    jsr @r3
    .org 0x5acbc-ORIGIN
L_0005acbc:
    extu.b r2,r5
    .org 0x5acbe-ORIGIN
L_0005acbe:
    bra L_0005ad54
    .org 0x5acc0-ORIGIN
L_0005acc0:
    mov r0,r2
    .org 0x5ad2c-ORIGIN
L_0005ad2c:
    .long 0xffff288c
    .org 0x5ad30-ORIGIN
L_0005ad30:
    .long 0xffff40a8
    .org 0x5ad34-ORIGIN
L_0005ad34:
    .long 0xffff40a4
    .org 0x5ad38-ORIGIN
L_0005ad38:
    .long 0xffff4020
    .org 0x5ad3c-ORIGIN
L_0005ad3c:
    .long 0xffff3529
    .org 0x5ad40-ORIGIN
L_0005ad40:
    .long 0x00012526
    .org 0x5ad44-ORIGIN
L_0005ad44:
    .long 0x00026358
    .org 0x5ad48-ORIGIN
L_0005ad48:
    mov r4,r14
    .org 0x5ad4a-ORIGIN
L_0005ad4a:
    mov.l L_0005af48,r4
    .org 0x5ad4c-ORIGIN
L_0005ad4c:
    mov.l L_0005af4c,r3
    .org 0x5ad4e-ORIGIN
L_0005ad4e:
    jsr @r3
    .org 0x5ad50-ORIGIN
L_0005ad50:
    extu.b r2,r5
    .org 0x5ad52-ORIGIN
L_0005ad52:
    mov r0,r2
    .org 0x5ad54-ORIGIN
L_0005ad54:
    mov.l L_0005af50,r3
    .org 0x5ad56-ORIGIN
L_0005ad56:
    mov r13,r0
    .org 0x5ad58-ORIGIN
L_0005ad58:
    mov.b r2,@(r0,r3)
    .org 0x5ad5a-ORIGIN
L_0005ad5a:
    extu.b r2,r2
    .org 0x5ad5c-ORIGIN
L_0005ad5c:
    mul.l r2,r14
    .org 0x5ad5e-ORIGIN
L_0005ad5e:
    mov.l L_0005af54,r3
    .org 0x5ad60-ORIGIN
L_0005ad60:
    mov #0x64,r0
    .org 0x5ad62-ORIGIN
L_0005ad62:
    jsr @r3
    .org 0x5ad64-ORIGIN
L_0005ad64:
    sts macl,r1
    .org 0x5ad66-ORIGIN
L_0005ad66:
    mov r0,r6
    .org 0x5ad68-ORIGIN
L_0005ad68:
    mov r12,r0
    .org 0x5ad6a-ORIGIN
L_0005ad6a:
    mov.w @(r0,r11),r2
    .org 0x5ad6c-ORIGIN
L_0005ad6c:
    cmp/pz r2
    .org 0x5ad6e-ORIGIN
L_0005ad6e:
    bt L_0005ad76
    .org 0x5ad70-ORIGIN
L_0005ad70:
    mov r9,r2
    .org 0x5ad72-ORIGIN
L_0005ad72:
    bra L_0005ad84
    .org 0x5ad74-ORIGIN
L_0005ad74:
    sub r6,r2
    .org 0x5ad76-ORIGIN
L_0005ad76:
    mov #-0x1,r3
    .org 0x5ad78-ORIGIN
L_0005ad78:
    add r9,r6
    .org 0x5ad7a-ORIGIN
L_0005ad7a:
    extu.w r3,r3
    .org 0x5ad7c-ORIGIN
L_0005ad7c:
    cmp/hi r3,r6
    .org 0x5ad7e-ORIGIN
L_0005ad7e:
    bf L_0005ad82
    .org 0x5ad80-ORIGIN
L_0005ad80:
    mov #-0x1,r6
    .org 0x5ad82-ORIGIN
L_0005ad82:
    mov r6,r2
    .org 0x5ad84-ORIGIN
L_0005ad84:
    add #0x1,r13
    .org 0x5ad86-ORIGIN
L_0005ad86:
    mov r12,r0
    .org 0x5ad88-ORIGIN
L_0005ad88:
    extu.w r13,r13
    .org 0x5ad8a-ORIGIN
L_0005ad8a:
    mov #0x2,r3
    .org 0x5ad8c-ORIGIN
L_0005ad8c:
    cmp/ge r3,r13
    .org 0x5ad8e-ORIGIN
L_0005ad8e:
    bt/s L_0005ad96
    .org 0x5ad90-ORIGIN
L_0005ad90:
    mov.w r2,@(r0,r8)
    .org 0x5ad92-ORIGIN
L_0005ad92:
    bra L_0005ac74
    .org 0x5ad94-ORIGIN
L_0005ad94:
    nop
    .org 0x5ad96-ORIGIN
L_0005ad96:
    lds.l @r15+,macl
    .org 0x5ad98-ORIGIN
L_0005ad98:
    lds.l @r15+,pr
    .org 0x5ad9a-ORIGIN
L_0005ad9a:
    mov.l @r15+,r14
    .org 0x5ad9c-ORIGIN
L_0005ad9c:
    mov.l @r15+,r13
    .org 0x5ad9e-ORIGIN
L_0005ad9e:
    mov.l @r15+,r12
    .org 0x5ada0-ORIGIN
L_0005ada0:
    mov.l @r15+,r11
    .org 0x5ada2-ORIGIN
L_0005ada2:
    mov.l @r15+,r10
    .org 0x5ada4-ORIGIN
L_0005ada4:
    mov.l @r15+,r9
    .org 0x5ada6-ORIGIN
L_0005ada6:
    rts
    .org 0x5ada8-ORIGIN
L_0005ada8:
    mov.l @r15+,r8
    .org 0x5af48-ORIGIN
L_0005af48:
    .long 0x00012522
    .org 0x5af4c-ORIGIN
L_0005af4c:
    .long 0x00026358
    .org 0x5af50-ORIGIN
L_0005af50:
    .long 0xffff409c
    .org 0x5af54-ORIGIN
L_0005af54:
    .long 0x00021ce0
