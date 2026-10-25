! JK08A event correction, final coordinate and diagnostic command instructions.
! Exact retained instruction spans, natural helpers and literal pools.
! APC scheduler effects require a separately declared observation boundary.
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
    .org 0x264cc-ORIGIN
L_000264cc:
    sts.l pr,@-r15
    .org 0x264ce-ORIGIN
L_000264ce:
    mov.l r4,@-r15
    .org 0x264d0-ORIGIN
L_000264d0:
    mov r5,r0
    .org 0x264d2-ORIGIN
L_000264d2:
    extu.w r6,r5
    .org 0x264d4-ORIGIN
L_000264d4:
    mov.l L_000264f4,r7
    .org 0x264d6-ORIGIN
L_000264d6:
    jsr @r7
    .org 0x264d8-ORIGIN
L_000264d8:
    mov #0xe,r4
    .org 0x264da-ORIGIN
L_000264da:
    mov.l @r15+,r6
    .org 0x264dc-ORIGIN
L_000264dc:
    add r4,r6
    .org 0x264de-ORIGIN
L_000264de:
    mov.w @(0x2,r6),r0
    .org 0x264e0-ORIGIN
L_000264e0:
    extu.w r0,r2
    .org 0x264e2-ORIGIN
L_000264e2:
    mov r5,r3
    .org 0x264e4-ORIGIN
L_000264e4:
    mov.w @r6,r1
    .org 0x264e6-ORIGIN
L_000264e6:
    lds.l @r15+,pr
    .org 0x264e8-ORIGIN
L_000264e8:
    mov.l L_000264f0,r6
    .org 0x264ea-ORIGIN
L_000264ea:
    jmp @r6
    .org 0x264ec-ORIGIN
L_000264ec:
    extu.w r1,r0
    .org 0x264f0-ORIGIN
L_000264f0:
    .long 0x00026740
    .org 0x264f4-ORIGIN
L_000264f4:
    .long 0x00026984
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
    .org 0x26984-ORIGIN
L_00026984:
    mov r4,r3
    .org 0x26986-ORIGIN
L_00026986:
    mov.w @(r0,r4),r1
    .org 0x26988-ORIGIN
L_00026988:
    extu.w r1,r1
    .org 0x2698a-ORIGIN
L_0002698a:
    cmp/eq r1,r5
    .org 0x2698c-ORIGIN
L_0002698c:
    bt L_000269bc
    .org 0x2698e-ORIGIN
L_0002698e:
    cmp/hi r1,r5
    .org 0x26990-ORIGIN
L_00026990:
    bf L_000269b4
    .org 0x26992-ORIGIN
L_00026992:
    cmp/eq r4,r3
    .org 0x26994-ORIGIN
L_00026994:
    bt L_000269bc
    .org 0x26996-ORIGIN
L_00026996:
    sub r1,r5
    .org 0x26998-ORIGIN
L_00026998:
    shll16 r5
    .org 0x2699a-ORIGIN
L_0002699a:
    add r4,r0
    .org 0x2699c-ORIGIN
L_0002699c:
    mov.w @r0,r1
    .org 0x2699e-ORIGIN
L_0002699e:
    mov.w @(0x2,r0),r0
    .org 0x269a0-ORIGIN
L_000269a0:
    extu.w r1,r1
    .org 0x269a2-ORIGIN
L_000269a2:
    extu.w r0,r0
    .org 0x269a4-ORIGIN
L_000269a4:
    sts.l pr,@-r15
    .org 0x269a6-ORIGIN
L_000269a6:
    mov.l L_000269c0,r2
    .org 0x269a8-ORIGIN
L_000269a8:
    sub r1,r0
    .org 0x269aa-ORIGIN
L_000269aa:
    jsr @r2
    .org 0x269ac-ORIGIN
L_000269ac:
    mov r5,r1
    .org 0x269ae-ORIGIN
L_000269ae:
    lds.l @r15+,pr
    .org 0x269b0-ORIGIN
L_000269b0:
    rts
    .org 0x269b2-ORIGIN
L_000269b2:
    mov r0,r5
    .org 0x269b4-ORIGIN
L_000269b4:
    add #-0x2,r4
    .org 0x269b6-ORIGIN
L_000269b6:
    cmp/pz r4
    .org 0x269b8-ORIGIN
L_000269b8:
    bt L_00026986
    .org 0x269ba-ORIGIN
L_000269ba:
    mov #0x0,r4
    .org 0x269bc-ORIGIN
L_000269bc:
    rts
    .org 0x269be-ORIGIN
L_000269be:
    mov #0x0,r5
    .org 0x269c0-ORIGIN
L_000269c0:
    .long 0x00026c78
    .org 0x26c78-ORIGIN
L_00026c78:
    tst r0,r0
    .org 0x26c7a-ORIGIN
L_00026c7a:
    bt L_00026d0a
    .org 0x26c7c-ORIGIN
L_00026c7c:
    mov.l r2,@-r15
    .org 0x26c7e-ORIGIN
L_00026c7e:
    mov #0x0,r2
    .org 0x26c80-ORIGIN
L_00026c80:
    div0u
    .org 0x26c82-ORIGIN
L_00026c82:
    rotcl r1
    .org 0x26c84-ORIGIN
L_00026c84:
    div1 r0,r2
    .org 0x26c86-ORIGIN
L_00026c86:
    rotcl r1
    .org 0x26c88-ORIGIN
L_00026c88:
    div1 r0,r2
    .org 0x26c8a-ORIGIN
L_00026c8a:
    rotcl r1
    .org 0x26c8c-ORIGIN
L_00026c8c:
    div1 r0,r2
    .org 0x26c8e-ORIGIN
L_00026c8e:
    rotcl r1
    .org 0x26c90-ORIGIN
L_00026c90:
    div1 r0,r2
    .org 0x26c92-ORIGIN
L_00026c92:
    rotcl r1
    .org 0x26c94-ORIGIN
L_00026c94:
    div1 r0,r2
    .org 0x26c96-ORIGIN
L_00026c96:
    rotcl r1
    .org 0x26c98-ORIGIN
L_00026c98:
    div1 r0,r2
    .org 0x26c9a-ORIGIN
L_00026c9a:
    rotcl r1
    .org 0x26c9c-ORIGIN
L_00026c9c:
    div1 r0,r2
    .org 0x26c9e-ORIGIN
L_00026c9e:
    rotcl r1
    .org 0x26ca0-ORIGIN
L_00026ca0:
    div1 r0,r2
    .org 0x26ca2-ORIGIN
L_00026ca2:
    rotcl r1
    .org 0x26ca4-ORIGIN
L_00026ca4:
    div1 r0,r2
    .org 0x26ca6-ORIGIN
L_00026ca6:
    rotcl r1
    .org 0x26ca8-ORIGIN
L_00026ca8:
    div1 r0,r2
    .org 0x26caa-ORIGIN
L_00026caa:
    rotcl r1
    .org 0x26cac-ORIGIN
L_00026cac:
    div1 r0,r2
    .org 0x26cae-ORIGIN
L_00026cae:
    rotcl r1
    .org 0x26cb0-ORIGIN
L_00026cb0:
    div1 r0,r2
    .org 0x26cb2-ORIGIN
L_00026cb2:
    rotcl r1
    .org 0x26cb4-ORIGIN
L_00026cb4:
    div1 r0,r2
    .org 0x26cb6-ORIGIN
L_00026cb6:
    rotcl r1
    .org 0x26cb8-ORIGIN
L_00026cb8:
    div1 r0,r2
    .org 0x26cba-ORIGIN
L_00026cba:
    rotcl r1
    .org 0x26cbc-ORIGIN
L_00026cbc:
    div1 r0,r2
    .org 0x26cbe-ORIGIN
L_00026cbe:
    rotcl r1
    .org 0x26cc0-ORIGIN
L_00026cc0:
    div1 r0,r2
    .org 0x26cc2-ORIGIN
L_00026cc2:
    rotcl r1
    .org 0x26cc4-ORIGIN
L_00026cc4:
    div1 r0,r2
    .org 0x26cc6-ORIGIN
L_00026cc6:
    rotcl r1
    .org 0x26cc8-ORIGIN
L_00026cc8:
    div1 r0,r2
    .org 0x26cca-ORIGIN
L_00026cca:
    rotcl r1
    .org 0x26ccc-ORIGIN
L_00026ccc:
    div1 r0,r2
    .org 0x26cce-ORIGIN
L_00026cce:
    rotcl r1
    .org 0x26cd0-ORIGIN
L_00026cd0:
    div1 r0,r2
    .org 0x26cd2-ORIGIN
L_00026cd2:
    rotcl r1
    .org 0x26cd4-ORIGIN
L_00026cd4:
    div1 r0,r2
    .org 0x26cd6-ORIGIN
L_00026cd6:
    rotcl r1
    .org 0x26cd8-ORIGIN
L_00026cd8:
    div1 r0,r2
    .org 0x26cda-ORIGIN
L_00026cda:
    rotcl r1
    .org 0x26cdc-ORIGIN
L_00026cdc:
    div1 r0,r2
    .org 0x26cde-ORIGIN
L_00026cde:
    rotcl r1
    .org 0x26ce0-ORIGIN
L_00026ce0:
    div1 r0,r2
    .org 0x26ce2-ORIGIN
L_00026ce2:
    rotcl r1
    .org 0x26ce4-ORIGIN
L_00026ce4:
    div1 r0,r2
    .org 0x26ce6-ORIGIN
L_00026ce6:
    rotcl r1
    .org 0x26ce8-ORIGIN
L_00026ce8:
    div1 r0,r2
    .org 0x26cea-ORIGIN
L_00026cea:
    rotcl r1
    .org 0x26cec-ORIGIN
L_00026cec:
    div1 r0,r2
    .org 0x26cee-ORIGIN
L_00026cee:
    rotcl r1
    .org 0x26cf0-ORIGIN
L_00026cf0:
    div1 r0,r2
    .org 0x26cf2-ORIGIN
L_00026cf2:
    rotcl r1
    .org 0x26cf4-ORIGIN
L_00026cf4:
    div1 r0,r2
    .org 0x26cf6-ORIGIN
L_00026cf6:
    rotcl r1
    .org 0x26cf8-ORIGIN
L_00026cf8:
    div1 r0,r2
    .org 0x26cfa-ORIGIN
L_00026cfa:
    rotcl r1
    .org 0x26cfc-ORIGIN
L_00026cfc:
    div1 r0,r2
    .org 0x26cfe-ORIGIN
L_00026cfe:
    rotcl r1
    .org 0x26d00-ORIGIN
L_00026d00:
    div1 r0,r2
    .org 0x26d02-ORIGIN
L_00026d02:
    rotcl r1
    .org 0x26d04-ORIGIN
L_00026d04:
    mov.l @r15+,r2
    .org 0x26d06-ORIGIN
L_00026d06:
    rts
    .org 0x26d08-ORIGIN
L_00026d08:
    mov r1,r0
    .org 0x26d0a-ORIGIN
L_00026d0a:
    rts
    .org 0x26d0c-ORIGIN
L_00026d0c:
    mov #0x0,r0
    .org 0x4d99c-ORIGIN
L_0004d99c:
    mov.l r12,@-r15
    .org 0x4d99e-ORIGIN
L_0004d99e:
    mov.l r13,@-r15
    .org 0x4d9a0-ORIGIN
L_0004d9a0:
    mov.l r14,@-r15
    .org 0x4d9a2-ORIGIN
L_0004d9a2:
    sts.l pr,@-r15
    .org 0x4d9a4-ORIGIN
L_0004d9a4:
    sts.l macl,@-r15
    .org 0x4d9a6-ORIGIN
L_0004d9a6:
    stc.l gbr,@-r15
    .org 0x4d9a8-ORIGIN
L_0004d9a8:
    mov.l L_0004dba0,r0
    .org 0x4d9aa-ORIGIN
L_0004d9aa:
    ldc r0,gbr
    .org 0x4d9ac-ORIGIN
L_0004d9ac:
    mov.l L_0004dba4,r2
    .org 0x4d9ae-ORIGIN
L_0004d9ae:
    mov.l L_0004dba8,r7
    .org 0x4d9b0-ORIGIN
L_0004d9b0:
    mov.b @r2,r0
    .org 0x4d9b2-ORIGIN
L_0004d9b2:
    and #0x20,r0
    .org 0x4d9b4-ORIGIN
L_0004d9b4:
    mov r0,r6
    .org 0x4d9b6-ORIGIN
L_0004d9b6:
    mov.b @(0x5,r7),r0
    .org 0x4d9b8-ORIGIN
L_0004d9b8:
    tst #0x20,r0
    .org 0x4d9ba-ORIGIN
L_0004d9ba:
    bf L_0004d9d8
    .org 0x4d9bc-ORIGIN
L_0004d9bc:
    mov.b @(0xb,r7),r0
    .org 0x4d9be-ORIGIN
L_0004d9be:
    tst #0x4,r0
    .org 0x4d9c0-ORIGIN
L_0004d9c0:
    bf L_0004d9d8
    .org 0x4d9c2-ORIGIN
L_0004d9c2:
    mov.l L_0004dbac,r14
    .org 0x4d9c4-ORIGIN
L_0004d9c4:
    mov #0x25,r0
    .org 0x4d9c6-ORIGIN
L_0004d9c6:
    tst r6,r6
    .org 0x4d9c8-ORIGIN
L_0004d9c8:
    mov.b @(r0,r14),r5
    .org 0x4d9ca-ORIGIN
L_0004d9ca:
    neg r5,r0
    .org 0x4d9cc-ORIGIN
L_0004d9cc:
    bt/s L_0004da2a
    .org 0x4d9ce-ORIGIN
L_0004d9ce:
    mov.w r0,@(0x2,r14)
    .org 0x4d9d0-ORIGIN
L_0004d9d0:
    mov #0x26,r0
    .org 0x4d9d2-ORIGIN
L_0004d9d2:
    mov.b @(r0,r14),r6
    .org 0x4d9d4-ORIGIN
L_0004d9d4:
    bra L_0004da28
    .org 0x4d9d6-ORIGIN
L_0004d9d6:
    neg r6,r0
    .org 0x4d9d8-ORIGIN
L_0004d9d8:
    tst r6,r6
    .org 0x4d9da-ORIGIN
L_0004d9da:
    bf L_0004d9f6
    .org 0x4d9dc-ORIGIN
L_0004d9dc:
    mov.l L_0004dbac,r14
    .org 0x4d9de-ORIGIN
L_0004d9de:
    mov #0x25,r0
    .org 0x4d9e0-ORIGIN
L_0004d9e0:
    mov.l L_0004dbb0,r4
    .org 0x4d9e2-ORIGIN
L_0004d9e2:
    mov.b @(r0,r14),r2
    .org 0x4d9e4-ORIGIN
L_0004d9e4:
    mov.b @(0x2,r4),r0
    .org 0x4d9e6-ORIGIN
L_0004d9e6:
    neg r2,r6
    .org 0x4d9e8-ORIGIN
L_0004d9e8:
    cmp/gt r6,r0
    .org 0x4d9ea-ORIGIN
L_0004d9ea:
    bt/s L_0004d9f0
    .org 0x4d9ec-ORIGIN
L_0004d9ec:
    mov r0,r2
    .org 0x4d9ee-ORIGIN
L_0004d9ee:
    mov r2,r6
    .org 0x4d9f0-ORIGIN
L_0004d9f0:
    mov r6,r0
    .org 0x4d9f2-ORIGIN
L_0004d9f2:
    bra L_0004da2a
    .org 0x4d9f4-ORIGIN
L_0004d9f4:
    mov.w r0,@(0x2,r14)
    .org 0x4d9f6-ORIGIN
L_0004d9f6:
    mov.l L_0004dbb4,r6
    .org 0x4d9f8-ORIGIN
L_0004d9f8:
    mov.l L_0004dbb0,r4
    .org 0x4d9fa-ORIGIN
L_0004d9fa:
    mov.w @(0x6,r6),r0
    .org 0x4d9fc-ORIGIN
L_0004d9fc:
    mov.l L_0004dbac,r14
    .org 0x4d9fe-ORIGIN
L_0004d9fe:
    extu.w r0,r6
    .org 0x4da00-ORIGIN
L_0004da00:
    mov.b @(0x2,r4),r0
    .org 0x4da02-ORIGIN
L_0004da02:
    shlr8 r6
    .org 0x4da04-ORIGIN
L_0004da04:
    mov r0,r5
    .org 0x4da06-ORIGIN
L_0004da06:
    mov r0,r2
    .org 0x4da08-ORIGIN
L_0004da08:
    mov #0x26,r0
    .org 0x4da0a-ORIGIN
L_0004da0a:
    mov.b @(r0,r14),r4
    .org 0x4da0c-ORIGIN
L_0004da0c:
    sub r6,r2
    .org 0x4da0e-ORIGIN
L_0004da0e:
    exts.w r2,r2
    .org 0x4da10-ORIGIN
L_0004da10:
    neg r4,r6
    .org 0x4da12-ORIGIN
L_0004da12:
    cmp/gt r6,r2
    .org 0x4da14-ORIGIN
L_0004da14:
    bf L_0004da18
    .org 0x4da16-ORIGIN
L_0004da16:
    mov r6,r2
    .org 0x4da18-ORIGIN
L_0004da18:
    cmp/gt r6,r5
    .org 0x4da1a-ORIGIN
L_0004da1a:
    mov r2,r0
    .org 0x4da1c-ORIGIN
L_0004da1c:
    bf/s L_0004da24
    .org 0x4da1e-ORIGIN
L_0004da1e:
    mov.w r0,@(0x2,r14)
    .org 0x4da20-ORIGIN
L_0004da20:
    bra L_0004da26
    .org 0x4da22-ORIGIN
L_0004da22:
    mov r6,r2
    .org 0x4da24-ORIGIN
L_0004da24:
    exts.b r5,r2
    .org 0x4da26-ORIGIN
L_0004da26:
    mov r2,r0
    .org 0x4da28-ORIGIN
L_0004da28:
    mov.w r0,@(0x4,r14)
    .org 0x4da2a-ORIGIN
L_0004da2a:
    mov.l L_0004dbb8,r12
    .org 0x4da2c-ORIGIN
L_0004da2c:
    mov.b @r12,r5
    .org 0x4da2e-ORIGIN
L_0004da2e:
    tst r5,r5
    .org 0x4da30-ORIGIN
L_0004da30:
    bt L_0004da70
    .org 0x4da32-ORIGIN
L_0004da32:
    mov.b @(0x2,r7),r0
    .org 0x4da34-ORIGIN
L_0004da34:
    mov r0,r2
    .org 0x4da36-ORIGIN
L_0004da36:
    and #0x2,r0
    .org 0x4da38-ORIGIN
L_0004da38:
    mov r0,r6
    .org 0x4da3a-ORIGIN
L_0004da3a:
    mov r2,r0
    .org 0x4da3c-ORIGIN
L_0004da3c:
    tst #0x1,r0
    .org 0x4da3e-ORIGIN
L_0004da3e:
    bt L_0004da5e
    .org 0x4da40-ORIGIN
L_0004da40:
    tst r6,r6
    .org 0x4da42-ORIGIN
L_0004da42:
    bf L_0004da5e
    .org 0x4da44-ORIGIN
L_0004da44:
    mov.l L_0004dbbc,r13
    .org 0x4da46-ORIGIN
L_0004da46:
    mov #0x48,r0
    .org 0x4da48-ORIGIN
L_0004da48:
    mov.l L_0004dba0,r4
    .org 0x4da4a-ORIGIN
L_0004da4a:
    mov.b @(r0,r13),r2
    .org 0x4da4c-ORIGIN
L_0004da4c:
    mov.w L_0004daa4,r0
    .org 0x4da4e-ORIGIN
L_0004da4e:
    mov.l L_0004dbc0,r6
    .org 0x4da50-ORIGIN
L_0004da50:
    mov.b r2,@(r0,r4)
    .org 0x4da52-ORIGIN
L_0004da52:
    mov.b @r7,r0
    .org 0x4da54-ORIGIN
L_0004da54:
    or #0x40,r0
    .org 0x4da56-ORIGIN
L_0004da56:
    mov.b r0,@r7
    .org 0x4da58-ORIGIN
L_0004da58:
    mov r5,r0
    .org 0x4da5a-ORIGIN
L_0004da5a:
    bra L_0004da76
    .org 0x4da5c-ORIGIN
L_0004da5c:
    mov.b r0,@(0x1,r6)
    .org 0x4da5e-ORIGIN
L_0004da5e:
    tst r6,r6
    .org 0x4da60-ORIGIN
L_0004da60:
    bf L_0004da70
    .org 0x4da62-ORIGIN
L_0004da62:
    mov.l @(0x4,gbr),r0
    .org 0x4da64-ORIGIN
L_0004da64:
    mov.l L_0004dba0,r4
    .org 0x4da66-ORIGIN
L_0004da66:
    mov r0,r3
    .org 0x4da68-ORIGIN
L_0004da68:
    mov.w L_0004daa4,r0
    .org 0x4da6a-ORIGIN
L_0004da6a:
    mov.b @(r0,r4),r2
    .org 0x4da6c-ORIGIN
L_0004da6c:
    cmp/eq r3,r2
    .org 0x4da6e-ORIGIN
L_0004da6e:
    bf L_0004da76
    .org 0x4da70-ORIGIN
L_0004da70:
    mov.b @r7,r0
    .org 0x4da72-ORIGIN
L_0004da72:
    and #0xbf,r0
    .org 0x4da74-ORIGIN
L_0004da74:
    mov.b r0,@r7
    .org 0x4da76-ORIGIN
L_0004da76:
    mov.b @(0xc,r7),r0
    .org 0x4da78-ORIGIN
L_0004da78:
    tst #0x2,r0
    .org 0x4da7a-ORIGIN
L_0004da7a:
    bf L_0004db74
    .org 0x4da7c-ORIGIN
L_0004da7c:
    mov.l L_0004dbbc,r13
    .org 0x4da7e-ORIGIN
L_0004da7e:
    mov #0x4e,r0
    .org 0x4da80-ORIGIN
L_0004da80:
    mov.l L_0004dbc4,r4
    .org 0x4da82-ORIGIN
L_0004da82:
    mov.w @(r0,r13),r7
    .org 0x4da84-ORIGIN
L_0004da84:
    mov.l L_0004dbc8,r5
    .org 0x4da86-ORIGIN
L_0004da86:
    mov.l L_0004dbcc,r2
    .org 0x4da88-ORIGIN
L_0004da88:
    jsr @r2
    .org 0x4da8a-ORIGIN
L_0004da8a:
    extu.w r7,r6
    .org 0x4da8c-ORIGIN
L_0004da8c:
    mov.l L_0004dbd0,r5
    .org 0x4da8e-ORIGIN
L_0004da8e:
    mov r0,r6
    .org 0x4da90-ORIGIN
L_0004da90:
    mov.w r0,@(0xc,gbr)
    .org 0x4da92-ORIGIN
L_0004da92:
    mov.b @r5,r0
    .org 0x4da94-ORIGIN
L_0004da94:
    tst #0x20,r0
    .org 0x4da96-ORIGIN
L_0004da96:
    bt L_0004daa8
    .org 0x4da98-ORIGIN
L_0004da98:
    mov.l L_0004dbd4,r5
    .org 0x4da9a-ORIGIN
L_0004da9a:
    mov.l L_0004dba0,r4
    .org 0x4da9c-ORIGIN
L_0004da9c:
    mov.b @r5,r2
    .org 0x4da9e-ORIGIN
L_0004da9e:
    mov.w L_0004daa6,r0
    .org 0x4daa0-ORIGIN
L_0004daa0:
    bra L_0004dab4
    .org 0x4daa2-ORIGIN
L_0004daa2:
    mov.b r2,@(r0,r4)
    .org 0x4daa4-ORIGIN
L_0004daa4:
    .word 0x02a9
    .org 0x4daa6-ORIGIN
L_0004daa6:
    .word 0x0278
    .org 0x4daa8-ORIGIN
L_0004daa8:
    mov.l L_0004dbd8,r2
    .org 0x4daaa-ORIGIN
L_0004daaa:
    mov.l L_0004dba0,r4
    .org 0x4daac-ORIGIN
L_0004daac:
    mov.b @r2,r5
    .org 0x4daae-ORIGIN
L_0004daae:
    mov.w L_0004db9c,r0
    .org 0x4dab0-ORIGIN
L_0004dab0:
    mov r5,r2
    .org 0x4dab2-ORIGIN
L_0004dab2:
    mov.b r5,@(r0,r4)
    .org 0x4dab4-ORIGIN
L_0004dab4:
    extu.w r6,r6
    .org 0x4dab6-ORIGIN
L_0004dab6:
    extu.b r2,r2
    .org 0x4dab8-ORIGIN
L_0004dab8:
    mul.l r6,r2
    .org 0x4daba-ORIGIN
L_0004daba:
    mov.l L_0004dbdc,r6
    .org 0x4dabc-ORIGIN
L_0004dabc:
    mov #0x64,r0
    .org 0x4dabe-ORIGIN
L_0004dabe:
    jsr @r6
    .org 0x4dac0-ORIGIN
L_0004dac0:
    sts macl,r1
    .org 0x4dac2-ORIGIN
L_0004dac2:
    mov #-0x1,r6
    .org 0x4dac4-ORIGIN
L_0004dac4:
    extu.w r6,r6
    .org 0x4dac6-ORIGIN
L_0004dac6:
    cmp/hi r6,r0
    .org 0x4dac8-ORIGIN
L_0004dac8:
    bf/s L_0004dace
    .org 0x4daca-ORIGIN
L_0004daca:
    mov r0,r2
    .org 0x4dacc-ORIGIN
L_0004dacc:
    mov r6,r2
    .org 0x4dace-ORIGIN
L_0004dace:
    mov.l L_0004dba8,r7
    .org 0x4dad0-ORIGIN
L_0004dad0:
    extu.w r2,r6
    .org 0x4dad2-ORIGIN
L_0004dad2:
    mov r6,r0
    .org 0x4dad4-ORIGIN
L_0004dad4:
    mov.w r0,@(0x2,gbr)
    .org 0x4dad6-ORIGIN
L_0004dad6:
    mov.b @r7,r0
    .org 0x4dad8-ORIGIN
L_0004dad8:
    tst #0x40,r0
    .org 0x4dada-ORIGIN
L_0004dada:
    bt L_0004db14
    .org 0x4dadc-ORIGIN
L_0004dadc:
    mov.l L_0004dbc0,r5
    .org 0x4dade-ORIGIN
L_0004dade:
    mov.b @(0x1,r5),r0
    .org 0x4dae0-ORIGIN
L_0004dae0:
    tst r0,r0
    .org 0x4dae2-ORIGIN
L_0004dae2:
    bf L_0004db0e
    .org 0x4dae4-ORIGIN
L_0004dae4:
    mov.l L_0004dba0,r4
    .org 0x4dae6-ORIGIN
L_0004dae6:
    mov.w L_0004db9e,r0
    .org 0x4dae8-ORIGIN
L_0004dae8:
    mov.b @(r0,r4),r2
    .org 0x4daea-ORIGIN
L_0004daea:
    mov.l @(0x4,gbr),r0
    .org 0x4daec-ORIGIN
L_0004daec:
    cmp/gt r2,r0
    .org 0x4daee-ORIGIN
L_0004daee:
    bf/s L_0004dafe
    .org 0x4daf0-ORIGIN
L_0004daf0:
    mov r0,r5
    .org 0x4daf2-ORIGIN
L_0004daf2:
    mov.b @r12,r0
    .org 0x4daf4-ORIGIN
L_0004daf4:
    mov.l L_0004dbc0,r3
    .org 0x4daf6-ORIGIN
L_0004daf6:
    mov.b r0,@(0x1,r3)
    .org 0x4daf8-ORIGIN
L_0004daf8:
    exts.w r5,r0
    .org 0x4dafa-ORIGIN
L_0004dafa:
    bra L_0004db0c
    .org 0x4dafc-ORIGIN
L_0004dafc:
    add #-0x1,r0
    .org 0x4dafe-ORIGIN
L_0004dafe:
    cmp/ge r2,r5
    .org 0x4db00-ORIGIN
L_0004db00:
    bt L_0004db0e
    .org 0x4db02-ORIGIN
L_0004db02:
    mov.b @r12,r0
    .org 0x4db04-ORIGIN
L_0004db04:
    mov.l L_0004dbc0,r3
    .org 0x4db06-ORIGIN
L_0004db06:
    mov.b r0,@(0x1,r3)
    .org 0x4db08-ORIGIN
L_0004db08:
    exts.w r5,r0
    .org 0x4db0a-ORIGIN
L_0004db0a:
    add #0x1,r0
    .org 0x4db0c-ORIGIN
L_0004db0c:
    mov.l r0,@(0x4,gbr)
    .org 0x4db0e-ORIGIN
L_0004db0e:
    mov.l @(0x4,gbr),r0
    .org 0x4db10-ORIGIN
L_0004db10:
    bra L_0004db56
    .org 0x4db12-ORIGIN
L_0004db12:
    mov r0,r2
    .org 0x4db14-ORIGIN
L_0004db14:
    mov.l L_0004dbe0,r2
    .org 0x4db16-ORIGIN
L_0004db16:
    mov #0x1b,r0
    .org 0x4db18-ORIGIN
L_0004db18:
    mov.b @(r0,r2),r4
    .org 0x4db1a-ORIGIN
L_0004db1a:
    extu.b r4,r4
    .org 0x4db1c-ORIGIN
L_0004db1c:
    cmp/pl r4
    .org 0x4db1e-ORIGIN
L_0004db1e:
    bf L_0004db48
    .org 0x4db20-ORIGIN
L_0004db20:
    mov.b @(0x2,r7),r0
    .org 0x4db22-ORIGIN
L_0004db22:
    tst #0x2,r0
    .org 0x4db24-ORIGIN
L_0004db24:
    bf L_0004db48
    .org 0x4db26-ORIGIN
L_0004db26:
    mov.w @(0x2,r14),r0
    .org 0x4db28-ORIGIN
L_0004db28:
    exts.w r4,r5
    .org 0x4db2a-ORIGIN
L_0004db2a:
    mov r0,r7
    .org 0x4db2c-ORIGIN
L_0004db2c:
    mov #0x26,r0
    .org 0x4db2e-ORIGIN
L_0004db2e:
    mov.b @(r0,r13),r2
    .org 0x4db30-ORIGIN
L_0004db30:
    add r2,r7
    .org 0x4db32-ORIGIN
L_0004db32:
    neg r5,r2
    .org 0x4db34-ORIGIN
L_0004db34:
    cmp/gt r2,r7
    .org 0x4db36-ORIGIN
L_0004db36:
    bf L_0004db3c
    .org 0x4db38-ORIGIN
L_0004db38:
    exts.w r4,r4
    .org 0x4db3a-ORIGIN
L_0004db3a:
    neg r4,r7
    .org 0x4db3c-ORIGIN
L_0004db3c:
    mov #0x48,r0
    .org 0x4db3e-ORIGIN
L_0004db3e:
    mov r6,r2
    .org 0x4db40-ORIGIN
L_0004db40:
    mov.b @(r0,r13),r6
    .org 0x4db42-ORIGIN
L_0004db42:
    add r7,r6
    .org 0x4db44-ORIGIN
L_0004db44:
    bra L_0004db60
    .org 0x4db46-ORIGIN
L_0004db46:
    sub r2,r6
    .org 0x4db48-ORIGIN
L_0004db48:
    mov.w @(0x2,r14),r0
    .org 0x4db4a-ORIGIN
L_0004db4a:
    mov r0,r4
    .org 0x4db4c-ORIGIN
L_0004db4c:
    mov #0x48,r0
    .org 0x4db4e-ORIGIN
L_0004db4e:
    mov.b @(r0,r13),r2
    .org 0x4db50-ORIGIN
L_0004db50:
    add r4,r2
    .org 0x4db52-ORIGIN
L_0004db52:
    mov r2,r0
    .org 0x4db54-ORIGIN
L_0004db54:
    mov.l r0,@(0x4,gbr)
    .org 0x4db56-ORIGIN
L_0004db56:
    mov #0x26,r0
    .org 0x4db58-ORIGIN
L_0004db58:
    mov.b @(r0,r13),r5
    .org 0x4db5a-ORIGIN
L_0004db5a:
    add r5,r2
    .org 0x4db5c-ORIGIN
L_0004db5c:
    sub r6,r2
    .org 0x4db5e-ORIGIN
L_0004db5e:
    mov r2,r6
    .org 0x4db60-ORIGIN
L_0004db60:
    mov #-0x80,r2
    .org 0x4db62-ORIGIN
L_0004db62:
    cmp/ge r2,r6
    .org 0x4db64-ORIGIN
L_0004db64:
    bt/s L_0004db6a
    .org 0x4db66-ORIGIN
L_0004db66:
    mov r6,r2
    .org 0x4db68-ORIGIN
L_0004db68:
    mov #-0x80,r2
    .org 0x4db6a-ORIGIN
L_0004db6a:
    mov #0x7f,r6
    .org 0x4db6c-ORIGIN
L_0004db6c:
    cmp/gt r6,r2
    .org 0x4db6e-ORIGIN
L_0004db6e:
    bf L_0004db86
    .org 0x4db70-ORIGIN
L_0004db70:
    bra L_0004db86
    .org 0x4db72-ORIGIN
L_0004db72:
    mov #0x7f,r2
    .org 0x4db74-ORIGIN
L_0004db74:
    mov.l L_0004dbbc,r13
    .org 0x4db76-ORIGIN
L_0004db76:
    mov #0x48,r0
    .org 0x4db78-ORIGIN
L_0004db78:
    mov #0x7f,r6
    .org 0x4db7a-ORIGIN
L_0004db7a:
    mov.b @(r0,r13),r2
    .org 0x4db7c-ORIGIN
L_0004db7c:
    cmp/gt r6,r2
    .org 0x4db7e-ORIGIN
L_0004db7e:
    bf/s L_0004db84
    .org 0x4db80-ORIGIN
L_0004db80:
    mov r2,r6
    .org 0x4db82-ORIGIN
L_0004db82:
    mov #0x7f,r6
    .org 0x4db84-ORIGIN
L_0004db84:
    mov r6,r2
    .org 0x4db86-ORIGIN
L_0004db86:
    mov r2,r6
    .org 0x4db88-ORIGIN
L_0004db88:
    mov.l L_0004dbe4,r2
    .org 0x4db8a-ORIGIN
L_0004db8a:
    mov #0x4a,r0
    .org 0x4db8c-ORIGIN
L_0004db8c:
    mov.b r6,@(r0,r2)
    .org 0x4db8e-ORIGIN
L_0004db8e:
    ldc.l @r15+,gbr
    .org 0x4db90-ORIGIN
L_0004db90:
    lds.l @r15+,macl
    .org 0x4db92-ORIGIN
L_0004db92:
    lds.l @r15+,pr
    .org 0x4db94-ORIGIN
L_0004db94:
    mov.l @r15+,r14
    .org 0x4db96-ORIGIN
L_0004db96:
    mov.l @r15+,r13
    .org 0x4db98-ORIGIN
L_0004db98:
    rts
    .org 0x4db9a-ORIGIN
L_0004db9a:
    mov.l @r15+,r12
    .org 0x4db9c-ORIGIN
L_0004db9c:
    .word 0x0278
    .org 0x4db9e-ORIGIN
L_0004db9e:
    .word 0x02a9
    .org 0x4dba0-ORIGIN
L_0004dba0:
    .long 0xffff1ff4
    .org 0x4dba4-ORIGIN
L_0004dba4:
    .long 0x00008710
    .org 0x4dba8-ORIGIN
L_0004dba8:
    .long 0xffff24c0
    .org 0x4dbac-ORIGIN
L_0004dbac:
    .long 0xffff11d4
    .org 0x4dbb0-ORIGIN
L_0004dbb0:
    .long 0xffff22f8
    .org 0x4dbb4-ORIGIN
L_0004dbb4:
    .long 0xffff23bc
    .org 0x4dbb8-ORIGIN
L_0004dbb8:
    .long 0x00008290
    .org 0x4dbbc-ORIGIN
L_0004dbbc:
    .long 0xffff2330
    .org 0x4dbc0-ORIGIN
L_0004dbc0:
    .long 0xffff25fb
    .org 0x4dbc4-ORIGIN
L_0004dbc4:
    .long 0x000147da
    .org 0x4dbc8-ORIGIN
L_0004dbc8:
    .long 0x00013c48
    .org 0x4dbcc-ORIGIN
L_0004dbcc:
    .long 0x000264cc
    .org 0x4dbd0-ORIGIN
L_0004dbd0:
    .long 0xffff2459
    .org 0x4dbd4-ORIGIN
L_0004dbd4:
    .long 0x00008a3c
    .org 0x4dbd8-ORIGIN
L_0004dbd8:
    .long 0x00008a3d
    .org 0x4dbdc-ORIGIN
L_0004dbdc:
    .long 0x00021ce0
    .org 0x4dbe0-ORIGIN
L_0004dbe0:
    .long 0xffff40cc
    .org 0x4dbe4-ORIGIN
L_0004dbe4:
    .long 0xffff128c
    .org 0x4dbe8-ORIGIN
L_0004dbe8:
    mov.l r8,@-r15
    .org 0x4dbea-ORIGIN
L_0004dbea:
    mov.l r9,@-r15
    .org 0x4dbec-ORIGIN
L_0004dbec:
    mov.l r10,@-r15
    .org 0x4dbee-ORIGIN
L_0004dbee:
    mov.l r11,@-r15
    .org 0x4dbf0-ORIGIN
L_0004dbf0:
    mov.l r12,@-r15
    .org 0x4dbf2-ORIGIN
L_0004dbf2:
    mov.l r13,@-r15
    .org 0x4dbf4-ORIGIN
L_0004dbf4:
    mov.l r14,@-r15
    .org 0x4dbf6-ORIGIN
L_0004dbf6:
    sts.l pr,@-r15
    .org 0x4dbf8-ORIGIN
L_0004dbf8:
    stc.l gbr,@-r15
    .org 0x4dbfa-ORIGIN
L_0004dbfa:
    mov.l L_0004ddcc,r0
    .org 0x4dbfc-ORIGIN
L_0004dbfc:
    ldc r0,gbr
    .org 0x4dbfe-ORIGIN
L_0004dbfe:
    add #-0xc,r15
    .org 0x4dc00-ORIGIN
L_0004dc00:
    mov.l L_0004ddd0,r2
    .org 0x4dc02-ORIGIN
L_0004dc02:
    mov #0x17,r0
    .org 0x4dc04-ORIGIN
L_0004dc04:
    mov.l L_0004ddd4,r7
    .org 0x4dc06-ORIGIN
L_0004dc06:
    mov.b @(r0,r2),r6
    .org 0x4dc08-ORIGIN
L_0004dc08:
    mov.b @r7,r4
    .org 0x4dc0a-ORIGIN
L_0004dc0a:
    extu.b r6,r6
    .org 0x4dc0c-ORIGIN
L_0004dc0c:
    mov r4,r0
    .org 0x4dc0e-ORIGIN
L_0004dc0e:
    tst #0x4,r0
    .org 0x4dc10-ORIGIN
L_0004dc10:
    bf/s L_0004dc16
    .org 0x4dc12-ORIGIN
L_0004dc12:
    mov r6,r5
    .org 0x4dc14-ORIGIN
L_0004dc14:
    add #0x8,r5
    .org 0x4dc16-ORIGIN
L_0004dc16:
    mov.l L_0004ddd8,r3
    .org 0x4dc18-ORIGIN
L_0004dc18:
    mov r4,r0
    .org 0x4dc1a-ORIGIN
L_0004dc1a:
    mov.b @r3,r2
    .org 0x4dc1c-ORIGIN
L_0004dc1c:
    extu.b r2,r2
    .org 0x4dc1e-ORIGIN
L_0004dc1e:
    cmp/hs r2,r5
    .org 0x4dc20-ORIGIN
L_0004dc20:
    bt/s L_0004dc26
    .org 0x4dc22-ORIGIN
L_0004dc22:
    and #0xfb,r0
    .org 0x4dc24-ORIGIN
L_0004dc24:
    or #0x4,r0
    .org 0x4dc26-ORIGIN
L_0004dc26:
    exts.b r0,r5
    .org 0x4dc28-ORIGIN
L_0004dc28:
    mov.b r0,@r7
    .org 0x4dc2a-ORIGIN
L_0004dc2a:
    mov r5,r0
    .org 0x4dc2c-ORIGIN
L_0004dc2c:
    tst #0x8,r0
    .org 0x4dc2e-ORIGIN
L_0004dc2e:
    bt L_0004dc32
    .org 0x4dc30-ORIGIN
L_0004dc30:
    add #0x8,r6
    .org 0x4dc32-ORIGIN
L_0004dc32:
    mov.l L_0004dddc,r4
    .org 0x4dc34-ORIGIN
L_0004dc34:
    mov r5,r0
    .org 0x4dc36-ORIGIN
L_0004dc36:
    mov.b @r4,r2
    .org 0x4dc38-ORIGIN
L_0004dc38:
    extu.b r2,r2
    .org 0x4dc3a-ORIGIN
L_0004dc3a:
    cmp/hi r2,r6
    .org 0x4dc3c-ORIGIN
L_0004dc3c:
    bt/s L_0004dc42
    .org 0x4dc3e-ORIGIN
L_0004dc3e:
    or #0x8,r0
    .org 0x4dc40-ORIGIN
L_0004dc40:
    and #0xf7,r0
    .org 0x4dc42-ORIGIN
L_0004dc42:
    mov.l L_0004dde0,r2
    .org 0x4dc44-ORIGIN
L_0004dc44:
    exts.b r0,r5
    .org 0x4dc46-ORIGIN
L_0004dc46:
    mov.b r0,@r7
    .org 0x4dc48-ORIGIN
L_0004dc48:
    mov r5,r0
    .org 0x4dc4a-ORIGIN
L_0004dc4a:
    mov.b @r2,r8
    .org 0x4dc4c-ORIGIN
L_0004dc4c:
    tst #0x10,r0
    .org 0x4dc4e-ORIGIN
L_0004dc4e:
    extu.b r8,r8
    .org 0x4dc50-ORIGIN
L_0004dc50:
    bf/s L_0004dc56
    .org 0x4dc52-ORIGIN
L_0004dc52:
    mov r8,r6
    .org 0x4dc54-ORIGIN
L_0004dc54:
    add #0x4,r6
    .org 0x4dc56-ORIGIN
L_0004dc56:
    mov.l L_0004dde4,r4
    .org 0x4dc58-ORIGIN
L_0004dc58:
    mov r5,r0
    .org 0x4dc5a-ORIGIN
L_0004dc5a:
    mov.b @r4,r2
    .org 0x4dc5c-ORIGIN
L_0004dc5c:
    extu.b r2,r2
    .org 0x4dc5e-ORIGIN
L_0004dc5e:
    cmp/hs r2,r6
    .org 0x4dc60-ORIGIN
L_0004dc60:
    bt/s L_0004dc66
    .org 0x4dc62-ORIGIN
L_0004dc62:
    and #0xef,r0
    .org 0x4dc64-ORIGIN
L_0004dc64:
    or #0x10,r0
    .org 0x4dc66-ORIGIN
L_0004dc66:
    exts.b r0,r5
    .org 0x4dc68-ORIGIN
L_0004dc68:
    mov.b r0,@r7
    .org 0x4dc6a-ORIGIN
L_0004dc6a:
    mov r5,r0
    .org 0x4dc6c-ORIGIN
L_0004dc6c:
    tst #0x20,r0
    .org 0x4dc6e-ORIGIN
L_0004dc6e:
    bt/s L_0004dc74
    .org 0x4dc70-ORIGIN
L_0004dc70:
    mov r8,r6
    .org 0x4dc72-ORIGIN
L_0004dc72:
    add #0x4,r6
    .org 0x4dc74-ORIGIN
L_0004dc74:
    mov.l L_0004dde8,r4
    .org 0x4dc76-ORIGIN
L_0004dc76:
    mov r5,r0
    .org 0x4dc78-ORIGIN
L_0004dc78:
    mov.b @r4,r2
    .org 0x4dc7a-ORIGIN
L_0004dc7a:
    extu.b r2,r2
    .org 0x4dc7c-ORIGIN
L_0004dc7c:
    cmp/hi r2,r6
    .org 0x4dc7e-ORIGIN
L_0004dc7e:
    bt/s L_0004dc84
    .org 0x4dc80-ORIGIN
L_0004dc80:
    or #0x20,r0
    .org 0x4dc82-ORIGIN
L_0004dc82:
    and #0xdf,r0
    .org 0x4dc84-ORIGIN
L_0004dc84:
    mov.l L_0004ddec,r2
    .org 0x4dc86-ORIGIN
L_0004dc86:
    mov.b r0,@r7
    .org 0x4dc88-ORIGIN
L_0004dc88:
    mov.b @(0x7,r2),r0
    .org 0x4dc8a-ORIGIN
L_0004dc8a:
    mov.b @r7,r5
    .org 0x4dc8c-ORIGIN
L_0004dc8c:
    extu.b r0,r6
    .org 0x4dc8e-ORIGIN
L_0004dc8e:
    mov r5,r0
    .org 0x4dc90-ORIGIN
L_0004dc90:
    tst #0x2,r0
    .org 0x4dc92-ORIGIN
L_0004dc92:
    bf L_0004dc96
    .org 0x4dc94-ORIGIN
L_0004dc94:
    add #0x3,r6
    .org 0x4dc96-ORIGIN
L_0004dc96:
    mov #0x6e,r2
    .org 0x4dc98-ORIGIN
L_0004dc98:
    mov r5,r0
    .org 0x4dc9a-ORIGIN
L_0004dc9a:
    cmp/hs r2,r6
    .org 0x4dc9c-ORIGIN
L_0004dc9c:
    bt/s L_0004dca2
    .org 0x4dc9e-ORIGIN
L_0004dc9e:
    and #0xfd,r0
    .org 0x4dca0-ORIGIN
L_0004dca0:
    or #0x2,r0
    .org 0x4dca2-ORIGIN
L_0004dca2:
    mov.l L_0004ddf0,r2
    .org 0x4dca4-ORIGIN
L_0004dca4:
    mov #-0x7f,r6
    .org 0x4dca6-ORIGIN
L_0004dca6:
    extu.b r6,r6
    .org 0x4dca8-ORIGIN
L_0004dca8:
    mov.b r0,@r7
    .org 0x4dcaa-ORIGIN
L_0004dcaa:
    mov.b @r2,r10
    .org 0x4dcac-ORIGIN
L_0004dcac:
    extu.b r10,r10
    .org 0x4dcae-ORIGIN
L_0004dcae:
    cmp/gt r6,r10
    .org 0x4dcb0-ORIGIN
L_0004dcb0:
    bf L_0004dcb6
    .org 0x4dcb2-ORIGIN
L_0004dcb2:
    bra L_0004dcb8
    .org 0x4dcb4-ORIGIN
L_0004dcb4:
    mov #0x0,r6
    .org 0x4dcb6-ORIGIN
L_0004dcb6:
    sub r10,r6
    .org 0x4dcb8-ORIGIN
L_0004dcb8:
    mov.b @r7,r0
    .org 0x4dcba-ORIGIN
L_0004dcba:
    mov r6,r11
    .org 0x4dcbc-ORIGIN
L_0004dcbc:
    mov.l L_0004ddf4,r14
    .org 0x4dcbe-ORIGIN
L_0004dcbe:
    tst #0x3e,r0
    .org 0x4dcc0-ORIGIN
L_0004dcc0:
    bt/s L_0004dcc8
    .org 0x4dcc2-ORIGIN
L_0004dcc2:
    mov.b @r14,r12
    .org 0x4dcc4-ORIGIN
L_0004dcc4:
    bra L_0004dccc
    .org 0x4dcc6-ORIGIN
L_0004dcc6:
    mov #0x0,r2
    .org 0x4dcc8-ORIGIN
L_0004dcc8:
    mov.l L_0004ddf8,r6
    .org 0x4dcca-ORIGIN
L_0004dcca:
    mov.b @r6,r2
    .org 0x4dccc-ORIGIN
L_0004dccc:
    mov.l L_0004ddfc,r5
    .org 0x4dcce-ORIGIN
L_0004dcce:
    mov #0x4a,r0
    .org 0x4dcd0-ORIGIN
L_0004dcd0:
    mov.b @(r0,r5),r14
    .org 0x4dcd2-ORIGIN
L_0004dcd2:
    mov.b @(0x0,gbr),r0
    .org 0x4dcd4-ORIGIN
L_0004dcd4:
    add r2,r14
    .org 0x4dcd6-ORIGIN
L_0004dcd6:
    cmp/gt r0,r14
    .org 0x4dcd8-ORIGIN
L_0004dcd8:
    mov r0,r7
    .org 0x4dcda-ORIGIN
L_0004dcda:
    bf/s L_0004dce0
    .org 0x4dcdc-ORIGIN
L_0004dcdc:
    mov r14,r6
    .org 0x4dcde-ORIGIN
L_0004dcde:
    mov r7,r6
    .org 0x4dce0-ORIGIN
L_0004dce0:
    mov.b @(0x3,gbr),r0
    .org 0x4dce2-ORIGIN
L_0004dce2:
    exts.b r6,r2
    .org 0x4dce4-ORIGIN
L_0004dce4:
    cmp/ge r0,r2
    .org 0x4dce6-ORIGIN
L_0004dce6:
    bt/s L_0004dcee
    .org 0x4dce8-ORIGIN
L_0004dce8:
    mov r0,r4
    .org 0x4dcea-ORIGIN
L_0004dcea:
    bra L_0004dcf0
    .org 0x4dcec-ORIGIN
L_0004dcec:
    mov r4,r6
    .org 0x4dcee-ORIGIN
L_0004dcee:
    exts.b r6,r6
    .org 0x4dcf0-ORIGIN
L_0004dcf0:
    mov.l L_0004ddf4,r3
    .org 0x4dcf2-ORIGIN
L_0004dcf2:
    mov r6,r0
    .org 0x4dcf4-ORIGIN
L_0004dcf4:
    mov.w L_0004dd32,r6
    .org 0x4dcf6-ORIGIN
L_0004dcf6:
    mov.b r0,@(0x6,r3)
    .org 0x4dcf8-ORIGIN
L_0004dcf8:
    mov.b @r6,r0
    .org 0x4dcfa-ORIGIN
L_0004dcfa:
    tst #0x4,r0
    .org 0x4dcfc-ORIGIN
L_0004dcfc:
    bt L_0004dd1a
    .org 0x4dcfe-ORIGIN
L_0004dcfe:
    mov.w L_0004dd34,r6
    .org 0x4dd00-ORIGIN
L_0004dd00:
    mov.b @(0x2,r6),r0
    .org 0x4dd02-ORIGIN
L_0004dd02:
    extu.b r0,r2
    .org 0x4dd04-ORIGIN
L_0004dd04:
    exts.b r2,r2
    .org 0x4dd06-ORIGIN
L_0004dd06:
    cmp/pl r2
    .org 0x4dd08-ORIGIN
L_0004dd08:
    bf L_0004dd0c
    .org 0x4dd0a-ORIGIN
L_0004dd0a:
    mov #0x0,r2
    .org 0x4dd0c-ORIGIN
L_0004dd0c:
    exts.b r2,r2
    .org 0x4dd0e-ORIGIN
L_0004dd0e:
    mov #-0xa,r6
    .org 0x4dd10-ORIGIN
L_0004dd10:
    cmp/ge r6,r2
    .org 0x4dd12-ORIGIN
L_0004dd12:
    bt L_0004dd16
    .org 0x4dd14-ORIGIN
L_0004dd14:
    mov #-0xa,r2
    .org 0x4dd16-ORIGIN
L_0004dd16:
    exts.b r2,r2
    .org 0x4dd18-ORIGIN
L_0004dd18:
    add r2,r14
    .org 0x4dd1a-ORIGIN
L_0004dd1a:
    mov.l L_0004de00,r9
    .org 0x4dd1c-ORIGIN
L_0004dd1c:
    mov.b @r9,r13
    .org 0x4dd1e-ORIGIN
L_0004dd1e:
    mov r13,r0
    .org 0x4dd20-ORIGIN
L_0004dd20:
    tst #0x10,r0
    .org 0x4dd22-ORIGIN
L_0004dd22:
    bf L_0004dd26
    .org 0x4dd24-ORIGIN
L_0004dd24:
    mov r14,r12
    .org 0x4dd26-ORIGIN
L_0004dd26:
    mov.l L_0004de04,r6
    .org 0x4dd28-ORIGIN
L_0004dd28:
    mov.b @r6,r0
    .org 0x4dd2a-ORIGIN
L_0004dd2a:
    tst #0x40,r0
    .org 0x4dd2c-ORIGIN
L_0004dd2c:
    bt L_0004dd36
    .org 0x4dd2e-ORIGIN
L_0004dd2e:
    bra L_0004dd82
    .org 0x4dd30-ORIGIN
L_0004dd30:
    mov.b @(0x73,gbr),r0
    .org 0x4dd32-ORIGIN
L_0004dd32:
    .word 0x99c4
    .org 0x4dd34-ORIGIN
L_0004dd34:
    .word 0x9924
    .org 0x4dd36-ORIGIN
L_0004dd36:
    mov.l L_0004de08,r6
    .org 0x4dd38-ORIGIN
L_0004dd38:
    mov.b @(0x2,r6),r0
    .org 0x4dd3a-ORIGIN
L_0004dd3a:
    tst #0x1,r0
    .org 0x4dd3c-ORIGIN
L_0004dd3c:
    bt L_0004dd42
    .org 0x4dd3e-ORIGIN
L_0004dd3e:
    bra L_0004dd82
    .org 0x4dd40-ORIGIN
L_0004dd40:
    mov.b @(0x71,gbr),r0
    .org 0x4dd42-ORIGIN
L_0004dd42:
    mov.b @(0x1,r6),r0
    .org 0x4dd44-ORIGIN
L_0004dd44:
    tst #0x1,r0
    .org 0x4dd46-ORIGIN
L_0004dd46:
    bf L_0004dd56
    .org 0x4dd48-ORIGIN
L_0004dd48:
    mov.l L_0004de0c,r6
    .org 0x4dd4a-ORIGIN
L_0004dd4a:
    mov #0x2a,r0
    .org 0x4dd4c-ORIGIN
L_0004dd4c:
    mov.b @(r0,r6),r2
    .org 0x4dd4e-ORIGIN
L_0004dd4e:
    tst r2,r2
    .org 0x4dd50-ORIGIN
L_0004dd50:
    bf L_0004dd56
    .org 0x4dd52-ORIGIN
L_0004dd52:
    bra L_0004dd82
    .org 0x4dd54-ORIGIN
L_0004dd54:
    mov.b @(0x6c,gbr),r0
    .org 0x4dd56-ORIGIN
L_0004dd56:
    mov.l L_0004de10,r5
    .org 0x4dd58-ORIGIN
L_0004dd58:
    mov.b @r5,r2
    .org 0x4dd5a-ORIGIN
L_0004dd5a:
    extu.b r2,r2
    .org 0x4dd5c-ORIGIN
L_0004dd5c:
    cmp/ge r2,r8
    .org 0x4dd5e-ORIGIN
L_0004dd5e:
    bt L_0004dd72
    .org 0x4dd60-ORIGIN
L_0004dd60:
    mov.l L_0004de14,r5
    .org 0x4dd62-ORIGIN
L_0004dd62:
    mov.b @r5,r2
    .org 0x4dd64-ORIGIN
L_0004dd64:
    extu.b r2,r2
    .org 0x4dd66-ORIGIN
L_0004dd66:
    cmp/ge r2,r8
    .org 0x4dd68-ORIGIN
L_0004dd68:
    bt L_0004dd6e
    .org 0x4dd6a-ORIGIN
L_0004dd6a:
    bra L_0004dd82
    .org 0x4dd6c-ORIGIN
L_0004dd6c:
    mov.b @(0x6d,gbr),r0
    .org 0x4dd6e-ORIGIN
L_0004dd6e:
    bra L_0004dd82
    .org 0x4dd70-ORIGIN
L_0004dd70:
    mov.b @(0x6e,gbr),r0
    .org 0x4dd72-ORIGIN
L_0004dd72:
    mov.l L_0004de18,r5
    .org 0x4dd74-ORIGIN
L_0004dd74:
    mov.b @r5,r2
    .org 0x4dd76-ORIGIN
L_0004dd76:
    extu.b r2,r2
    .org 0x4dd78-ORIGIN
L_0004dd78:
    cmp/ge r2,r8
    .org 0x4dd7a-ORIGIN
L_0004dd7a:
    bt L_0004dd80
    .org 0x4dd7c-ORIGIN
L_0004dd7c:
    bra L_0004dd82
    .org 0x4dd7e-ORIGIN
L_0004dd7e:
    mov.b @(0x6f,gbr),r0
    .org 0x4dd80-ORIGIN
L_0004dd80:
    mov.b @(0x70,gbr),r0
    .org 0x4dd82-ORIGIN
L_0004dd82:
    extu.b r0,r5
    .org 0x4dd84-ORIGIN
L_0004dd84:
    exts.w r12,r12
    .org 0x4dd86-ORIGIN
L_0004dd86:
    exts.w r5,r2
    .org 0x4dd88-ORIGIN
L_0004dd88:
    mov r12,r6
    .org 0x4dd8a-ORIGIN
L_0004dd8a:
    add r2,r6
    .org 0x4dd8c-ORIGIN
L_0004dd8c:
    cmp/gt r6,r14
    .org 0x4dd8e-ORIGIN
L_0004dd8e:
    bf L_0004dd98
    .org 0x4dd90-ORIGIN
L_0004dd90:
    exts.w r12,r12
    .org 0x4dd92-ORIGIN
L_0004dd92:
    exts.w r5,r5
    .org 0x4dd94-ORIGIN
L_0004dd94:
    mov r12,r14
    .org 0x4dd96-ORIGIN
L_0004dd96:
    add r5,r14
    .org 0x4dd98-ORIGIN
L_0004dd98:
    mov.l L_0004de1c,r2
    .org 0x4dd9a-ORIGIN
L_0004dd9a:
    exts.w r12,r12
    .org 0x4dd9c-ORIGIN
L_0004dd9c:
    mov.b @r2,r5
    .org 0x4dd9e-ORIGIN
L_0004dd9e:
    mov r12,r2
    .org 0x4dda0-ORIGIN
L_0004dda0:
    extu.b r5,r5
    .org 0x4dda2-ORIGIN
L_0004dda2:
    exts.w r5,r6
    .org 0x4dda4-ORIGIN
L_0004dda4:
    sub r6,r2
    .org 0x4dda6-ORIGIN
L_0004dda6:
    cmp/ge r2,r14
    .org 0x4dda8-ORIGIN
L_0004dda8:
    bt L_0004ddb2
    .org 0x4ddaa-ORIGIN
L_0004ddaa:
    exts.w r12,r2
    .org 0x4ddac-ORIGIN
L_0004ddac:
    exts.w r5,r5
    .org 0x4ddae-ORIGIN
L_0004ddae:
    bra L_0004ddb4
    .org 0x4ddb0-ORIGIN
L_0004ddb0:
    sub r5,r2
    .org 0x4ddb2-ORIGIN
L_0004ddb2:
    mov r14,r2
    .org 0x4ddb4-ORIGIN
L_0004ddb4:
    exts.b r7,r7
    .org 0x4ddb6-ORIGIN
L_0004ddb6:
    cmp/gt r7,r2
    .org 0x4ddb8-ORIGIN
L_0004ddb8:
    bf L_0004ddbe
    .org 0x4ddba-ORIGIN
L_0004ddba:
    bra L_0004ddc0
    .org 0x4ddbc-ORIGIN
L_0004ddbc:
    exts.b r7,r7
    .org 0x4ddbe-ORIGIN
L_0004ddbe:
    mov r2,r7
    .org 0x4ddc0-ORIGIN
L_0004ddc0:
    exts.b r4,r4
    .org 0x4ddc2-ORIGIN
L_0004ddc2:
    exts.b r7,r2
    .org 0x4ddc4-ORIGIN
L_0004ddc4:
    cmp/ge r4,r2
    .org 0x4ddc6-ORIGIN
L_0004ddc6:
    bt L_0004de20
    .org 0x4ddc8-ORIGIN
L_0004ddc8:
    bra L_0004de22
    .org 0x4ddca-ORIGIN
L_0004ddca:
    exts.b r4,r6
    .org 0x4ddcc-ORIGIN
L_0004ddcc:
    .long 0x0000821e
    .org 0x4ddd0-ORIGIN
L_0004ddd0:
    .long 0xffff119c
    .org 0x4ddd4-ORIGIN
L_0004ddd4:
    .long 0xffff5b31
    .org 0x4ddd8-ORIGIN
L_0004ddd8:
    .long 0x00008897
    .org 0x4dddc-ORIGIN
L_0004dddc:
    .long 0x00008896
    .org 0x4dde0-ORIGIN
L_0004dde0:
    .long 0xffff1048
    .org 0x4dde4-ORIGIN
L_0004dde4:
    .long 0x00008768
    .org 0x4dde8-ORIGIN
L_0004dde8:
    .long 0x00008767
    .org 0x4ddec-ORIGIN
L_0004ddec:
    .long 0xffff1072
    .org 0x4ddf0-ORIGIN
L_0004ddf0:
    .long 0x000083d5
    .org 0x4ddf4-ORIGIN
L_0004ddf4:
    .long 0xffff11d4
    .org 0x4ddf8-ORIGIN
L_0004ddf8:
    .long 0xffff564c
    .org 0x4ddfc-ORIGIN
L_0004ddfc:
    .long 0xffff128c
    .org 0x4de00-ORIGIN
L_0004de00:
    .long 0xffff24c0
    .org 0x4de04-ORIGIN
L_0004de04:
    .long 0xffff4184
    .org 0x4de08-ORIGIN
L_0004de08:
    .long 0xffff24c8
    .org 0x4de0c-ORIGIN
L_0004de0c:
    .long 0xffff256a
    .org 0x4de10-ORIGIN
L_0004de10:
    .long 0x0000876c
    .org 0x4de14-ORIGIN
L_0004de14:
    .long 0x0000876b
    .org 0x4de18-ORIGIN
L_0004de18:
    .long 0x0000876d
    .org 0x4de1c-ORIGIN
L_0004de1c:
    .long 0x00008a4f
    .org 0x4de20-ORIGIN
L_0004de20:
    exts.b r7,r6
    .org 0x4de22-ORIGIN
L_0004de22:
    neg r11,r4
    .org 0x4de24-ORIGIN
L_0004de24:
    mov r13,r0
    .org 0x4de26-ORIGIN
L_0004de26:
    or #0x10,r0
    .org 0x4de28-ORIGIN
L_0004de28:
    cmp/ge r4,r6
    .org 0x4de2a-ORIGIN
L_0004de2a:
    mov.b r0,@r9
    .org 0x4de2c-ORIGIN
L_0004de2c:
    bt/s L_0004de32
    .org 0x4de2e-ORIGIN
L_0004de2e:
    mov.l r4,@r15
    .org 0x4de30-ORIGIN
L_0004de30:
    mov r4,r6
    .org 0x4de32-ORIGIN
L_0004de32:
    mov r10,r2
    .org 0x4de34-ORIGIN
L_0004de34:
    add #-0x28,r2
    .org 0x4de36-ORIGIN
L_0004de36:
    cmp/gt r2,r6
    .org 0x4de38-ORIGIN
L_0004de38:
    bf L_0004de40
    .org 0x4de3a-ORIGIN
L_0004de3a:
    mov r10,r2
    .org 0x4de3c-ORIGIN
L_0004de3c:
    bra L_0004de42
    .org 0x4de3e-ORIGIN
L_0004de3e:
    add #-0x28,r2
    .org 0x4de40-ORIGIN
L_0004de40:
    mov r6,r2
    .org 0x4de42-ORIGIN
L_0004de42:
    mov r2,r13
    .org 0x4de44-ORIGIN
L_0004de44:
    mov.l L_0004dfe8,r2
    .org 0x4de46-ORIGIN
L_0004de46:
    mov.b @r2,r0
    .org 0x4de48-ORIGIN
L_0004de48:
    and #0x10,r0
    .org 0x4de4a-ORIGIN
L_0004de4a:
    tst r0,r0
    .org 0x4de4c-ORIGIN
L_0004de4c:
    bt/s L_0004deba
    .org 0x4de4e-ORIGIN
L_0004de4e:
    mov r0,r14
    .org 0x4de50-ORIGIN
L_0004de50:
    mov.w L_0004de56,r0
    .org 0x4de52-ORIGIN
L_0004de52:
    bra L_0004de58
    .org 0x4de54-ORIGIN
L_0004de54:
    tst.b #0x80,@(r0,gbr)
    .org 0x4de56-ORIGIN
L_0004de56:
    .word 0x0924
    .org 0x4de58-ORIGIN
L_0004de58:
    bf L_0004deba
    .org 0x4de5a-ORIGIN
L_0004de5a:
    mov.w L_0004df7c,r0
    .org 0x4de5c-ORIGIN
L_0004de5c:
    tst.b #0x1,@(r0,gbr)
    .org 0x4de5e-ORIGIN
L_0004de5e:
    bt L_0004de8c
    .org 0x4de60-ORIGIN
L_0004de60:
    mov.w L_0004df7e,r0
    .org 0x4de62-ORIGIN
L_0004de62:
    tst.b #0x2,@(r0,gbr)
    .org 0x4de64-ORIGIN
L_0004de64:
    bt L_0004de6c
    .org 0x4de66-ORIGIN
L_0004de66:
    mov.b @(0x8,gbr),r0
    .org 0x4de68-ORIGIN
L_0004de68:
    bra L_0004de72
    .org 0x4de6a-ORIGIN
L_0004de6a:
    mov r0,r2
    .org 0x4de6c-ORIGIN
L_0004de6c:
    mov.l L_0004dfec,r4
    .org 0x4de6e-ORIGIN
L_0004de6e:
    mov #0x1a,r0
    .org 0x4de70-ORIGIN
L_0004de70:
    mov.b @(r0,r4),r2
    .org 0x4de72-ORIGIN
L_0004de72:
    mov.l @r15,r4
    .org 0x4de74-ORIGIN
L_0004de74:
    cmp/ge r4,r2
    .org 0x4de76-ORIGIN
L_0004de76:
    bf L_0004de7a
    .org 0x4de78-ORIGIN
L_0004de78:
    mov r2,r4
    .org 0x4de7a-ORIGIN
L_0004de7a:
    mov r10,r2
    .org 0x4de7c-ORIGIN
L_0004de7c:
    add #-0x2,r2
    .org 0x4de7e-ORIGIN
L_0004de7e:
    cmp/gt r2,r4
    .org 0x4de80-ORIGIN
L_0004de80:
    bf L_0004de88
    .org 0x4de82-ORIGIN
L_0004de82:
    add #-0x2,r10
    .org 0x4de84-ORIGIN
L_0004de84:
    bra L_0004df4e
    .org 0x4de86-ORIGIN
L_0004de86:
    mov r10,r2
    .org 0x4de88-ORIGIN
L_0004de88:
    bra L_0004df4e
    .org 0x4de8a-ORIGIN
L_0004de8a:
    mov r4,r2
    .org 0x4de8c-ORIGIN
L_0004de8c:
    mov.l L_0004dff0,r6
    .org 0x4de8e-ORIGIN
L_0004de8e:
    mov #0x72,r0
    .org 0x4de90-ORIGIN
L_0004de90:
    mov.l @r15,r4
    .org 0x4de92-ORIGIN
L_0004de92:
    mov.b @(r0,r6),r2
    .org 0x4de94-ORIGIN
L_0004de94:
    extu.b r2,r2
    .org 0x4de96-ORIGIN
L_0004de96:
    exts.w r2,r6
    .org 0x4de98-ORIGIN
L_0004de98:
    mov #0x0,r2
    .org 0x4de9a-ORIGIN
L_0004de9a:
    cmp/gt r6,r2
    .org 0x4de9c-ORIGIN
L_0004de9c:
    addc r2,r6
    .org 0x4de9e-ORIGIN
L_0004de9e:
    shar r6
    .org 0x4dea0-ORIGIN
L_0004dea0:
    add #-0xa,r6
    .org 0x4dea2-ORIGIN
L_0004dea2:
    cmp/ge r4,r6
    .org 0x4dea4-ORIGIN
L_0004dea4:
    bt L_0004dea8
    .org 0x4dea6-ORIGIN
L_0004dea6:
    mov r4,r6
    .org 0x4dea8-ORIGIN
L_0004dea8:
    mov r10,r2
    .org 0x4deaa-ORIGIN
L_0004deaa:
    add #-0x2,r2
    .org 0x4deac-ORIGIN
L_0004deac:
    cmp/gt r2,r6
    .org 0x4deae-ORIGIN
L_0004deae:
    bf L_0004deb6
    .org 0x4deb0-ORIGIN
L_0004deb0:
    add #-0x2,r10
    .org 0x4deb2-ORIGIN
L_0004deb2:
    bra L_0004df4e
    .org 0x4deb4-ORIGIN
L_0004deb4:
    mov r10,r2
    .org 0x4deb6-ORIGIN
L_0004deb6:
    bra L_0004df4e
    .org 0x4deb8-ORIGIN
L_0004deb8:
    mov r6,r2
    .org 0x4deba-ORIGIN
L_0004deba:
    mov.w L_0004df7c,r0
    .org 0x4debc-ORIGIN
L_0004debc:
    tst.b #0x41,@(r0,gbr)
    .org 0x4debe-ORIGIN
L_0004debe:
    bf L_0004deca
    .org 0x4dec0-ORIGIN
L_0004dec0:
    tst r14,r14
    .org 0x4dec2-ORIGIN
L_0004dec2:
    bt L_0004deca
    .org 0x4dec4-ORIGIN
L_0004dec4:
    mov.w L_0004df80,r0
    .org 0x4dec6-ORIGIN
L_0004dec6:
    tst.b #0x1,@(r0,gbr)
    .org 0x4dec8-ORIGIN
L_0004dec8:
    bf L_0004ded8
    .org 0x4deca-ORIGIN
L_0004deca:
    mov.w L_0004df7c,r0
    .org 0x4decc-ORIGIN
L_0004decc:
    tst.b #0x1,@(r0,gbr)
    .org 0x4dece-ORIGIN
L_0004dece:
    bt L_0004df50
    .org 0x4ded0-ORIGIN
L_0004ded0:
    tst.b #0x40,@(r0,gbr)
    .org 0x4ded2-ORIGIN
L_0004ded2:
    bf L_0004df50
    .org 0x4ded4-ORIGIN
L_0004ded4:
    tst r14,r14
    .org 0x4ded6-ORIGIN
L_0004ded6:
    bt L_0004df50
    .org 0x4ded8-ORIGIN
L_0004ded8:
    mov.l L_0004dff4,r6
    .org 0x4deda-ORIGIN
L_0004deda:
    mov.l L_0004dff8,r3
    .org 0x4dedc-ORIGIN
L_0004dedc:
    mov.b @r6,r2
    .org 0x4dede-ORIGIN
L_0004dede:
    mov.b @(0xa,r3),r0
    .org 0x4dee0-ORIGIN
L_0004dee0:
    extu.b r2,r6
    .org 0x4dee2-ORIGIN
L_0004dee2:
    mov.l L_0004dffc,r5
    .org 0x4dee4-ORIGIN
L_0004dee4:
    mov.l r6,@(0x8,r15)
    .org 0x4dee6-ORIGIN
L_0004dee6:
    extu.b r0,r6
    .org 0x4dee8-ORIGIN
L_0004dee8:
    add #-0x1,r6
    .org 0x4deea-ORIGIN
L_0004deea:
    mov #0x1,r0
    .org 0x4deec-ORIGIN
L_0004deec:
    jsr @r5
    .org 0x4deee-ORIGIN
L_0004deee:
    mov r6,r1
    .org 0x4def0-ORIGIN
L_0004def0:
    mov.l @(0x8,r15),r6
    .org 0x4def2-ORIGIN
L_0004def2:
    tst r0,r6
    .org 0x4def4-ORIGIN
L_0004def4:
    bt L_0004df50
    .org 0x4def6-ORIGIN
L_0004def6:
    mov.l L_0004e000,r2
    .org 0x4def8-ORIGIN
L_0004def8:
    mov #0x48,r0
    .org 0x4defa-ORIGIN
L_0004defa:
    mov.l L_0004dff8,r3
    .org 0x4defc-ORIGIN
L_0004defc:
    mov.b @(r0,r2),r5
    .org 0x4defe-ORIGIN
L_0004defe:
    mov #0x25,r0
    .org 0x4df00-ORIGIN
L_0004df00:
    mov.b @(r0,r3),r2
    .org 0x4df02-ORIGIN
L_0004df02:
    mov.w L_0004df7c,r0
    .org 0x4df04-ORIGIN
L_0004df04:
    sub r2,r5
    .org 0x4df06-ORIGIN
L_0004df06:
    tst.b #0x1,@(r0,gbr)
    .org 0x4df08-ORIGIN
L_0004df08:
    bt/s L_0004df24
    .org 0x4df0a-ORIGIN
L_0004df0a:
    mov.l r5,@(0x4,r15)
    .org 0x4df0c-ORIGIN
L_0004df0c:
    mov.w L_0004df7e,r0
    .org 0x4df0e-ORIGIN
L_0004df0e:
    tst.b #0x2,@(r0,gbr)
    .org 0x4df10-ORIGIN
L_0004df10:
    bt/s L_0004df1a
    .org 0x4df12-ORIGIN
L_0004df12:
    mov.l @(0x4,r15),r5
    .org 0x4df14-ORIGIN
L_0004df14:
    mov.b @(0x9,gbr),r0
    .org 0x4df16-ORIGIN
L_0004df16:
    bra L_0004df36
    .org 0x4df18-ORIGIN
L_0004df18:
    add r0,r5
    .org 0x4df1a-ORIGIN
L_0004df1a:
    mov.l L_0004dfec,r4
    .org 0x4df1c-ORIGIN
L_0004df1c:
    mov #0x1b,r0
    .org 0x4df1e-ORIGIN
L_0004df1e:
    mov.b @(r0,r4),r2
    .org 0x4df20-ORIGIN
L_0004df20:
    bra L_0004df36
    .org 0x4df22-ORIGIN
L_0004df22:
    add r2,r5
    .org 0x4df24-ORIGIN
L_0004df24:
    mov.l L_0004e004,r6
    .org 0x4df26-ORIGIN
L_0004df26:
    mov.w @(0x2,r6),r0
    .org 0x4df28-ORIGIN
L_0004df28:
    mov.l L_0004e008,r6
    .org 0x4df2a-ORIGIN
L_0004df2a:
    extu.w r0,r1
    .org 0x4df2c-ORIGIN
L_0004df2c:
    jsr @r6
    .org 0x4df2e-ORIGIN
L_0004df2e:
    mov #0x50,r0
    .org 0x4df30-ORIGIN
L_0004df30:
    mov.l @(0x4,r15),r5
    .org 0x4df32-ORIGIN
L_0004df32:
    add r0,r5
    .org 0x4df34-ORIGIN
L_0004df34:
    add #-0x20,r5
    .org 0x4df36-ORIGIN
L_0004df36:
    mov.l @r15,r4
    .org 0x4df38-ORIGIN
L_0004df38:
    cmp/ge r4,r5
    .org 0x4df3a-ORIGIN
L_0004df3a:
    bf L_0004df3e
    .org 0x4df3c-ORIGIN
L_0004df3c:
    mov r5,r4
    .org 0x4df3e-ORIGIN
L_0004df3e:
    mov r10,r2
    .org 0x4df40-ORIGIN
L_0004df40:
    add #-0x2,r2
    .org 0x4df42-ORIGIN
L_0004df42:
    cmp/gt r2,r4
    .org 0x4df44-ORIGIN
L_0004df44:
    bf L_0004df4c
    .org 0x4df46-ORIGIN
L_0004df46:
    add #-0x2,r10
    .org 0x4df48-ORIGIN
L_0004df48:
    bra L_0004df4e
    .org 0x4df4a-ORIGIN
L_0004df4a:
    mov r10,r2
    .org 0x4df4c-ORIGIN
L_0004df4c:
    mov r4,r2
    .org 0x4df4e-ORIGIN
L_0004df4e:
    mov r2,r13
    .org 0x4df50-ORIGIN
L_0004df50:
    mov.b @r9,r2
    .org 0x4df52-ORIGIN
L_0004df52:
    mov r2,r0
    .org 0x4df54-ORIGIN
L_0004df54:
    tst #0x80,r0
    .org 0x4df56-ORIGIN
L_0004df56:
    bf L_0004df62
    .org 0x4df58-ORIGIN
L_0004df58:
    mov.b @(0x6b,gbr),r0
    .org 0x4df5a-ORIGIN
L_0004df5a:
    mov r0,r13
    .org 0x4df5c-ORIGIN
L_0004df5c:
    mov r2,r0
    .org 0x4df5e-ORIGIN
L_0004df5e:
    or #0x80,r0
    .org 0x4df60-ORIGIN
L_0004df60:
    mov.b r0,@r9
    .org 0x4df62-ORIGIN
L_0004df62:
    mov.l L_0004dff8,r3
    .org 0x4df64-ORIGIN
L_0004df64:
    mov.b r13,@r3
    .org 0x4df66-ORIGIN
L_0004df66:
    add #0xc,r15
    .org 0x4df68-ORIGIN
L_0004df68:
    ldc.l @r15+,gbr
    .org 0x4df6a-ORIGIN
L_0004df6a:
    lds.l @r15+,pr
    .org 0x4df6c-ORIGIN
L_0004df6c:
    mov.l @r15+,r14
    .org 0x4df6e-ORIGIN
L_0004df6e:
    mov.l @r15+,r13
    .org 0x4df70-ORIGIN
L_0004df70:
    mov.l @r15+,r12
    .org 0x4df72-ORIGIN
L_0004df72:
    mov.l @r15+,r11
    .org 0x4df74-ORIGIN
L_0004df74:
    mov.l @r15+,r10
    .org 0x4df76-ORIGIN
L_0004df76:
    mov.l @r15+,r9
    .org 0x4df78-ORIGIN
L_0004df78:
    rts
    .org 0x4df7a-ORIGIN
L_0004df7a:
    mov.l @r15+,r8
    .org 0x4df7c-ORIGIN
L_0004df7c:
    .word 0x0924
    .org 0x4df7e-ORIGIN
L_0004df7e:
    .word 0x04db
    .org 0x4df80-ORIGIN
L_0004df80:
    .word 0x0916
    .org 0x4df82-ORIGIN
L_0004df82:
    sts.l pr,@-r15
    .org 0x4df84-ORIGIN
L_0004df84:
    stc.l gbr,@-r15
    .org 0x4df86-ORIGIN
L_0004df86:
    mov.l L_0004e00c,r0
    .org 0x4df88-ORIGIN
L_0004df88:
    ldc r0,gbr
    .org 0x4df8a-ORIGIN
L_0004df8a:
    mov.l L_0004e010,r2
    .org 0x4df8c-ORIGIN
L_0004df8c:
    jsr @r2
    .org 0x4df8e-ORIGIN
L_0004df8e:
    nop
    .org 0x4df90-ORIGIN
L_0004df90:
    tst r0,r0
    .org 0x4df92-ORIGIN
L_0004df92:
    bt L_0004e024
    .org 0x4df94-ORIGIN
L_0004df94:
    mov.l L_0004e014,r6
    .org 0x4df96-ORIGIN
L_0004df96:
    mov.b @(0x8,r6),r0
    .org 0x4df98-ORIGIN
L_0004df98:
    tst #0x20,r0
    .org 0x4df9a-ORIGIN
L_0004df9a:
    bf L_0004dfba
    .org 0x4df9c-ORIGIN
L_0004df9c:
    mov.b @r6,r0
    .org 0x4df9e-ORIGIN
L_0004df9e:
    tst #0x80,r0
    .org 0x4dfa0-ORIGIN
L_0004dfa0:
    bf L_0004dfba
    .org 0x4dfa2-ORIGIN
L_0004dfa2:
    mov.l L_0004e018,r6
    .org 0x4dfa4-ORIGIN
L_0004dfa4:
    mov.b @(0xb,r6),r0
    .org 0x4dfa6-ORIGIN
L_0004dfa6:
    tst #0x80,r0
    .org 0x4dfa8-ORIGIN
L_0004dfa8:
    bf L_0004dfba
    .org 0x4dfaa-ORIGIN
L_0004dfaa:
    mov.l L_0004dff8,r7
    .org 0x4dfac-ORIGIN
L_0004dfac:
    mov.l L_0004e01c,r2
    .org 0x4dfae-ORIGIN
L_0004dfae:
    mov.b @r7,r5
    .org 0x4dfb0-ORIGIN
L_0004dfb0:
    mov.b @r2,r6
    .org 0x4dfb2-ORIGIN
L_0004dfb2:
    mov r6,r0
    .org 0x4dfb4-ORIGIN
L_0004dfb4:
    sub r5,r0
    .org 0x4dfb6-ORIGIN
L_0004dfb6:
    bra L_0004e05e
    .org 0x4dfb8-ORIGIN
L_0004dfb8:
    mov r0,r4
    .org 0x4dfba-ORIGIN
L_0004dfba:
    mov.l L_0004e01c,r2
    .org 0x4dfbc-ORIGIN
L_0004dfbc:
    mov.l L_0004e020,r4
    .org 0x4dfbe-ORIGIN
L_0004dfbe:
    mov.l L_0004dff8,r7
    .org 0x4dfc0-ORIGIN
L_0004dfc0:
    mov.b @r2,r6
    .org 0x4dfc2-ORIGIN
L_0004dfc2:
    mov.b @r4,r5
    .org 0x4dfc4-ORIGIN
L_0004dfc4:
    mov.b @r7,r4
    .org 0x4dfc6-ORIGIN
L_0004dfc6:
    extu.b r6,r6
    .org 0x4dfc8-ORIGIN
L_0004dfc8:
    mov r6,r2
    .org 0x4dfca-ORIGIN
L_0004dfca:
    extu.b r5,r5
    .org 0x4dfcc-ORIGIN
L_0004dfcc:
    sub r4,r2
    .org 0x4dfce-ORIGIN
L_0004dfce:
    add r5,r2
    .org 0x4dfd0-ORIGIN
L_0004dfd0:
    exts.w r2,r5
    .org 0x4dfd2-ORIGIN
L_0004dfd2:
    cmp/pz r5
    .org 0x4dfd4-ORIGIN
L_0004dfd4:
    bt L_0004dfd8
    .org 0x4dfd6-ORIGIN
L_0004dfd6:
    mov #0x0,r5
    .org 0x4dfd8-ORIGIN
L_0004dfd8:
    exts.w r5,r2
    .org 0x4dfda-ORIGIN
L_0004dfda:
    mov #-0x1,r5
    .org 0x4dfdc-ORIGIN
L_0004dfdc:
    extu.b r5,r5
    .org 0x4dfde-ORIGIN
L_0004dfde:
    cmp/gt r5,r2
    .org 0x4dfe0-ORIGIN
L_0004dfe0:
    bf L_0004e05a
    .org 0x4dfe2-ORIGIN
L_0004dfe2:
    bra L_0004e05a
    .org 0x4dfe4-ORIGIN
L_0004dfe4:
    mov r5,r2
    .org 0x4dfe8-ORIGIN
L_0004dfe8:
    .long 0x00008b34
    .org 0x4dfec-ORIGIN
L_0004dfec:
    .long 0xffff5628
    .org 0x4dff0-ORIGIN
L_0004dff0:
    .long 0xffff1114
    .org 0x4dff4-ORIGIN
L_0004dff4:
    .long 0x00008657
    .org 0x4dff8-ORIGIN
L_0004dff8:
    .long 0xffff11d4
    .org 0x4dffc-ORIGIN
L_0004dffc:
    .long 0x000221bc
    .org 0x4e000-ORIGIN
L_0004e000:
    .long 0xffff2330
    .org 0x4e004-ORIGIN
L_0004e004:
    .long 0xffff1006
    .org 0x4e008-ORIGIN
L_0004e008:
    .long 0x00021bbc
    .org 0x4e00c-ORIGIN
L_0004e00c:
    .long 0xffff1ff4
    .org 0x4e010-ORIGIN
L_0004e010:
    .long 0x0008c3fa
    .org 0x4e014-ORIGIN
L_0004e014:
    .long 0xffff2451
    .org 0x4e018-ORIGIN
L_0004e018:
    .long 0xffff24c8
    .org 0x4e01c-ORIGIN
L_0004e01c:
    .long 0x000083d5
    .org 0x4e020-ORIGIN
L_0004e020:
    .long 0x00008c95
    .org 0x4e024-ORIGIN
L_0004e024:
    mov.l L_0004e180,r2
    .org 0x4e026-ORIGIN
L_0004e026:
    mov.l L_0004e184,r7
    .org 0x4e028-ORIGIN
L_0004e028:
    mov.l L_0004e188,r4
    .org 0x4e02a-ORIGIN
L_0004e02a:
    mov.b @r2,r6
    .org 0x4e02c-ORIGIN
L_0004e02c:
    mov.b @r7,r5
    .org 0x4e02e-ORIGIN
L_0004e02e:
    mov.b @(0x1,r4),r0
    .org 0x4e030-ORIGIN
L_0004e030:
    extu.b r6,r6
    .org 0x4e032-ORIGIN
L_0004e032:
    mov r6,r2
    .org 0x4e034-ORIGIN
L_0004e034:
    sub r5,r2
    .org 0x4e036-ORIGIN
L_0004e036:
    tst #0x20,r0
    .org 0x4e038-ORIGIN
L_0004e038:
    bt/s L_0004e05a
    .org 0x4e03a-ORIGIN
L_0004e03a:
    mov r2,r5
    .org 0x4e03c-ORIGIN
L_0004e03c:
    mov.l L_0004e18c,r4
    .org 0x4e03e-ORIGIN
L_0004e03e:
    mov.b @r4,r2
    .org 0x4e040-ORIGIN
L_0004e040:
    extu.b r2,r2
    .org 0x4e042-ORIGIN
L_0004e042:
    sub r2,r5
    .org 0x4e044-ORIGIN
L_0004e044:
    exts.w r5,r4
    .org 0x4e046-ORIGIN
L_0004e046:
    cmp/pz r4
    .org 0x4e048-ORIGIN
L_0004e048:
    bt L_0004e04c
    .org 0x4e04a-ORIGIN
L_0004e04a:
    mov #0x0,r4
    .org 0x4e04c-ORIGIN
L_0004e04c:
    mov.l L_0004e190,r2
    .org 0x4e04e-ORIGIN
L_0004e04e:
    exts.w r4,r4
    .org 0x4e050-ORIGIN
L_0004e050:
    mov.b @r2,r5
    .org 0x4e052-ORIGIN
L_0004e052:
    extu.b r5,r2
    .org 0x4e054-ORIGIN
L_0004e054:
    cmp/gt r2,r4
    .org 0x4e056-ORIGIN
L_0004e056:
    bt L_0004e05a
    .org 0x4e058-ORIGIN
L_0004e058:
    mov r4,r2
    .org 0x4e05a-ORIGIN
L_0004e05a:
    mov r2,r4
    .org 0x4e05c-ORIGIN
L_0004e05c:
    mov r2,r0
    .org 0x4e05e-ORIGIN
L_0004e05e:
    mov.l L_0004e194,r5
    .org 0x4e060-ORIGIN
L_0004e060:
    mov.b r0,@(0x2e,gbr)
    .org 0x4e062-ORIGIN
L_0004e062:
    mov.b @(0x5,r5),r0
    .org 0x4e064-ORIGIN
L_0004e064:
    tst #0x1,r0
    .org 0x4e066-ORIGIN
L_0004e066:
    bt L_0004e072
    .org 0x4e068-ORIGIN
L_0004e068:
    add #-0x14,r6
    .org 0x4e06a-ORIGIN
L_0004e06a:
    extu.b r6,r6
    .org 0x4e06c-ORIGIN
L_0004e06c:
    mov r6,r0
    .org 0x4e06e-ORIGIN
L_0004e06e:
    mov r6,r4
    .org 0x4e070-ORIGIN
L_0004e070:
    mov.b r0,@(0x2e,gbr)
    .org 0x4e072-ORIGIN
L_0004e072:
    mov.l L_0004e198,r2
    .org 0x4e074-ORIGIN
L_0004e074:
    jsr @r2
    .org 0x4e076-ORIGIN
L_0004e076:
    extu.b r4,r4
    .org 0x4e078-ORIGIN
L_0004e078:
    ldc.l @r15+,gbr
    .org 0x4e07a-ORIGIN
L_0004e07a:
    lds.l @r15+,pr
    .org 0x4e07c-ORIGIN
L_0004e07c:
    rts
    .org 0x4e07e-ORIGIN
L_0004e07e:
    nop
    .org 0x4e180-ORIGIN
L_0004e180:
    .long 0x000083d5
    .org 0x4e184-ORIGIN
L_0004e184:
    .long 0xffff11d4
    .org 0x4e188-ORIGIN
L_0004e188:
    .long 0xffff24c8
    .org 0x4e18c-ORIGIN
L_0004e18c:
    .long 0x000083ea
    .org 0x4e190-ORIGIN
L_0004e190:
    .long 0x0000864a
    .org 0x4e194-ORIGIN
L_0004e194:
    .long 0xffff424c
    .org 0x4e198-ORIGIN
L_0004e198:
    .long 0x0002a892
    .org 0x8c3fa-ORIGIN
L_0008c3fa:
    stc.l gbr,@-r15
    .org 0x8c3fc-ORIGIN
L_0008c3fc:
    mov.l L_0008c468,r0
    .org 0x8c3fe-ORIGIN
L_0008c3fe:
    ldc r0,gbr
    .org 0x8c400-ORIGIN
L_0008c400:
    add #-0x4,r15
    .org 0x8c402-ORIGIN
L_0008c402:
    mov.b @(0x0,gbr),r0
    .org 0x8c404-ORIGIN
L_0008c404:
    tst #0x40,r0
    .org 0x8c406-ORIGIN
L_0008c406:
    bf/s L_0008c43e
    .org 0x8c408-ORIGIN
L_0008c408:
    mov #0x0,r1
    .org 0x8c40a-ORIGIN
L_0008c40a:
    mov.l L_0008c46c,r6
    .org 0x8c40c-ORIGIN
L_0008c40c:
    mov.b @r6,r0
    .org 0x8c40e-ORIGIN
L_0008c40e:
    tst #0x20,r0
    .org 0x8c410-ORIGIN
L_0008c410:
    bt L_0008c43e
    .org 0x8c412-ORIGIN
L_0008c412:
    mov.b @(0x21,gbr),r0
    .org 0x8c414-ORIGIN
L_0008c414:
    mov #0x1,r6
    .org 0x8c416-ORIGIN
L_0008c416:
    tst #0x4,r0
    .org 0x8c418-ORIGIN
L_0008c418:
    bt/s L_0008c43c
    .org 0x8c41a-ORIGIN
L_0008c41a:
    mov.l r6,@r15
    .org 0x8c41c-ORIGIN
L_0008c41c:
    mov.b @(0x39,gbr),r0
    .org 0x8c41e-ORIGIN
L_0008c41e:
    tst #0x1,r0
    .org 0x8c420-ORIGIN
L_0008c420:
    bf L_0008c43c
    .org 0x8c422-ORIGIN
L_0008c422:
    mov.l L_0008c464,r5
    .org 0x8c424-ORIGIN
L_0008c424:
    mov #0x14,r4
    .org 0x8c426-ORIGIN
L_0008c426:
    mov.w L_0008c44a,r0
    .org 0x8c428-ORIGIN
L_0008c428:
    mov.w @(r0,r5),r2
    .org 0x8c42a-ORIGIN
L_0008c42a:
    cmp/hs r4,r2
    .org 0x8c42c-ORIGIN
L_0008c42c:
    bt L_0008c43c
    .org 0x8c42e-ORIGIN
L_0008c42e:
    mov.w L_0008c44c,r0
    .org 0x8c430-ORIGIN
L_0008c430:
    mov.w @(r0,r5),r2
    .org 0x8c432-ORIGIN
L_0008c432:
    extu.w r2,r2
    .org 0x8c434-ORIGIN
L_0008c434:
    cmp/ge r4,r2
    .org 0x8c436-ORIGIN
L_0008c436:
    bt L_0008c43c
    .org 0x8c438-ORIGIN
L_0008c438:
    mov #0x0,r6
    .org 0x8c43a-ORIGIN
L_0008c43a:
    mov.l r6,@r15
    .org 0x8c43c-ORIGIN
L_0008c43c:
    mov.l @r15,r1
    .org 0x8c43e-ORIGIN
L_0008c43e:
    extu.b r1,r0
    .org 0x8c440-ORIGIN
L_0008c440:
    add #0x4,r15
    .org 0x8c442-ORIGIN
L_0008c442:
    rts
    .org 0x8c444-ORIGIN
L_0008c444:
    ldc.l @r15+,gbr
    .org 0x8c44a-ORIGIN
L_0008c44a:
    .word 0x0bec
    .org 0x8c44c-ORIGIN
L_0008c44c:
    .word 0x0bee
    .org 0x8c464-ORIGIN
L_0008c464:
    .long 0xffff28f8
    .org 0x8c468-ORIGIN
L_0008c468:
    .long 0xffff4184
    .org 0x8c46c-ORIGIN
L_0008c46c:
    .long 0xffff244f
