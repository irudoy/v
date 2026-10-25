! Explicit stock fine-gopher entry and natural lookup/divider closure.
! GBR and the later block use separate absolute windows, not the relocated 64 KiB image.
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
    .org 0x6062c-ORIGIN
L_0006062c:
    bra L_00060630
    .org 0x6062e-ORIGIN
L_0006062e:
    nop
    .org 0x60630-ORIGIN
L_00060630:
    mov.l r8,@-r15
    .org 0x60632-ORIGIN
L_00060632:
    mov.l r9,@-r15
    .org 0x60634-ORIGIN
L_00060634:
    mov.l r10,@-r15
    .org 0x60636-ORIGIN
L_00060636:
    mov.l r11,@-r15
    .org 0x60638-ORIGIN
L_00060638:
    mov.l r12,@-r15
    .org 0x6063a-ORIGIN
L_0006063a:
    mov.l r13,@-r15
    .org 0x6063c-ORIGIN
L_0006063c:
    mov.l r14,@-r15
    .org 0x6063e-ORIGIN
L_0006063e:
    sts.l pr,@-r15
    .org 0x60640-ORIGIN
L_00060640:
    sts.l macl,@-r15
    .org 0x60642-ORIGIN
L_00060642:
    stc.l gbr,@-r15
    .org 0x60644-ORIGIN
L_00060644:
    mov.w L_00060758,r0
    .org 0x60646-ORIGIN
L_00060646:
    ldc r0,gbr
    .org 0x60648-ORIGIN
L_00060648:
    mov.l L_00060850,r6
    .org 0x6064a-ORIGIN
L_0006064a:
    mov.b @r6,r0
    .org 0x6064c-ORIGIN
L_0006064c:
    tst #0x40,r0
    .org 0x6064e-ORIGIN
L_0006064e:
    bt/s L_00060654
    .org 0x60650-ORIGIN
L_00060650:
    mov #0x0,r0
    .org 0x60652-ORIGIN
L_00060652:
    mov #0x1,r0
    .org 0x60654-ORIGIN
L_00060654:
    mov.l L_00060854,r11
    .org 0x60656-ORIGIN
L_00060656:
    mov.b r0,@(0x24,gbr)
    .org 0x60658-ORIGIN
L_00060658:
    mov #0x20,r0
    .org 0x6065a-ORIGIN
L_0006065a:
    mov.w @(r0,r11),r2
    .org 0x6065c-ORIGIN
L_0006065c:
    mov.l L_00060858,r4
    .org 0x6065e-ORIGIN
L_0006065e:
    mov.l L_0006085c,r5
    .org 0x60660-ORIGIN
L_00060660:
    mov.l L_00060860,r14
    .org 0x60662-ORIGIN
L_00060662:
    mov.l L_00060864,r9
    .org 0x60664-ORIGIN
L_00060664:
    jsr @r14
    .org 0x60666-ORIGIN
L_00060666:
    extu.w r2,r6
    .org 0x60668-ORIGIN
L_00060668:
    mov.w r0,@(0x18,r9)
    .org 0x6066a-ORIGIN
L_0006066a:
    mov #0x20,r0
    .org 0x6066c-ORIGIN
L_0006066c:
    mov.w @(r0,r11),r2
    .org 0x6066e-ORIGIN
L_0006066e:
    mov.l L_00060868,r4
    .org 0x60670-ORIGIN
L_00060670:
    mov.l L_0006085c,r5
    .org 0x60672-ORIGIN
L_00060672:
    jsr @r14
    .org 0x60674-ORIGIN
L_00060674:
    extu.w r2,r6
    .org 0x60676-ORIGIN
L_00060676:
    mov.l L_0006086c,r2
    .org 0x60678-ORIGIN
L_00060678:
    mov.w r0,@(0x1a,r9)
    .org 0x6067a-ORIGIN
L_0006067a:
    mov #0x35,r0
    .org 0x6067c-ORIGIN
L_0006067c:
    mov.b @r11,r5
    .org 0x6067e-ORIGIN
L_0006067e:
    mov.b @(r0,r2),r6
    .org 0x60680-ORIGIN
L_00060680:
    mov r5,r2
    .org 0x60682-ORIGIN
L_00060682:
    sub r6,r2
    .org 0x60684-ORIGIN
L_00060684:
    exts.w r2,r0
    .org 0x60686-ORIGIN
L_00060686:
    mov #0x7f,r6
    .org 0x60688-ORIGIN
L_00060688:
    cmp/gt r6,r0
    .org 0x6068a-ORIGIN
L_0006068a:
    bt/s L_0006069a
    .org 0x6068c-ORIGIN
L_0006068c:
    mov.w r0,@(0x22,gbr)
    .org 0x6068e-ORIGIN
L_0006068e:
    mov #-0x80,r6
    .org 0x60690-ORIGIN
L_00060690:
    cmp/ge r6,r0
    .org 0x60692-ORIGIN
L_00060692:
    bt L_00060698
    .org 0x60694-ORIGIN
L_00060694:
    bra L_0006069a
    .org 0x60696-ORIGIN
L_00060696:
    mov #-0x80,r6
    .org 0x60698-ORIGIN
L_00060698:
    exts.b r0,r6
    .org 0x6069a-ORIGIN
L_0006069a:
    exts.b r6,r2
    .org 0x6069c-ORIGIN
L_0006069c:
    cmp/pz r2
    .org 0x6069e-ORIGIN
L_0006069e:
    mov r2,r0
    .org 0x606a0-ORIGIN
L_000606a0:
    bf/s L_000606ac
    .org 0x606a2-ORIGIN
L_000606a2:
    mov.b r0,@(0x38,gbr)
    .org 0x606a4-ORIGIN
L_000606a4:
    cmp/pz r2
    .org 0x606a6-ORIGIN
L_000606a6:
    bt L_000606b8
    .org 0x606a8-ORIGIN
L_000606a8:
    bra L_000606b8
    .org 0x606aa-ORIGIN
L_000606aa:
    mov #0x0,r2
    .org 0x606ac-ORIGIN
L_000606ac:
    neg r2,r0
    .org 0x606ae-ORIGIN
L_000606ae:
    exts.w r0,r2
    .org 0x606b0-ORIGIN
L_000606b0:
    cmp/pz r2
    .org 0x606b2-ORIGIN
L_000606b2:
    bt/s L_000606b8
    .org 0x606b4-ORIGIN
L_000606b4:
    mov.w r0,@(0x22,gbr)
    .org 0x606b6-ORIGIN
L_000606b6:
    mov #0x0,r2
    .org 0x606b8-ORIGIN
L_000606b8:
    mov.l L_00060870,r4
    .org 0x606ba-ORIGIN
L_000606ba:
    mov r2,r0
    .org 0x606bc-ORIGIN
L_000606bc:
    mov.l L_00060874,r5
    .org 0x606be-ORIGIN
L_000606be:
    extu.b r2,r6
    .org 0x606c0-ORIGIN
L_000606c0:
    mov.l L_00060878,r8
    .org 0x606c2-ORIGIN
L_000606c2:
    mov.l L_0006087c,r10
    .org 0x606c4-ORIGIN
L_000606c4:
    jsr @r14
    .org 0x606c6-ORIGIN
L_000606c6:
    mov.b r0,@(0x39,gbr)
    .org 0x606c8-ORIGIN
L_000606c8:
    mov.w r0,@(0xe,r9)
    .org 0x606ca-ORIGIN
L_000606ca:
    mov.w @r8,r2
    .org 0x606cc-ORIGIN
L_000606cc:
    mov.w @(0xa,r10),r0
    .org 0x606ce-ORIGIN
L_000606ce:
    extu.w r2,r5
    .org 0x606d0-ORIGIN
L_000606d0:
    mov.l L_00060880,r13
    .org 0x606d2-ORIGIN
L_000606d2:
    extu.w r0,r2
    .org 0x606d4-ORIGIN
L_000606d4:
    mov r0,r6
    .org 0x606d6-ORIGIN
L_000606d6:
    mul.l r5,r2
    .org 0x606d8-ORIGIN
L_000606d8:
    mov.l L_00060884,r0
    .org 0x606da-ORIGIN
L_000606da:
    jsr @r13
    .org 0x606dc-ORIGIN
L_000606dc:
    sts macl,r1
    .org 0x606de-ORIGIN
L_000606de:
    mov r0,r2
    .org 0x606e0-ORIGIN
L_000606e0:
    mov.w @(0xe,r9),r0
    .org 0x606e2-ORIGIN
L_000606e2:
    extu.w r2,r2
    .org 0x606e4-ORIGIN
L_000606e4:
    extu.w r0,r6
    .org 0x606e6-ORIGIN
L_000606e6:
    mul.l r2,r6
    .org 0x606e8-ORIGIN
L_000606e8:
    mov.l L_00060888,r6
    .org 0x606ea-ORIGIN
L_000606ea:
    sts macl,r2
    .org 0x606ec-ORIGIN
L_000606ec:
    cmp/hi r6,r2
    .org 0x606ee-ORIGIN
L_000606ee:
    bf L_000606f4
    .org 0x606f0-ORIGIN
L_000606f0:
    bra L_000606fc
    .org 0x606f2-ORIGIN
L_000606f2:
    mov #-0x1,r6
    .org 0x606f4-ORIGIN
L_000606f4:
    shlr2 r2
    .org 0x606f6-ORIGIN
L_000606f6:
    shlr2 r2
    .org 0x606f8-ORIGIN
L_000606f8:
    shlr2 r2
    .org 0x606fa-ORIGIN
L_000606fa:
    mov r2,r6
    .org 0x606fc-ORIGIN
L_000606fc:
    mov r6,r0
    .org 0x606fe-ORIGIN
L_000606fe:
    mov.w r0,@(0x20,gbr)
    .org 0x60700-ORIGIN
L_00060700:
    mov.w @(0x18,r9),r0
    .org 0x60702-ORIGIN
L_00060702:
    extu.w r6,r6
    .org 0x60704-ORIGIN
L_00060704:
    mov #-0x1,r12
    .org 0x60706-ORIGIN
L_00060706:
    extu.w r0,r2
    .org 0x60708-ORIGIN
L_00060708:
    mov r0,r5
    .org 0x6070a-ORIGIN
L_0006070a:
    mul.l r6,r2
    .org 0x6070c-ORIGIN
L_0006070c:
    mov.w L_0006075a,r0
    .org 0x6070e-ORIGIN
L_0006070e:
    extu.w r12,r12
    .org 0x60710-ORIGIN
L_00060710:
    jsr @r13
    .org 0x60712-ORIGIN
L_00060712:
    sts macl,r1
    .org 0x60714-ORIGIN
L_00060714:
    cmp/hi r12,r0
    .org 0x60716-ORIGIN
L_00060716:
    mov r0,r2
    .org 0x60718-ORIGIN
L_00060718:
    bf/s L_0006071e
    .org 0x6071a-ORIGIN
L_0006071a:
    mov.l r0,@(0x14,gbr)
    .org 0x6071c-ORIGIN
L_0006071c:
    mov #-0x1,r2
    .org 0x6071e-ORIGIN
L_0006071e:
    mov #0x34,r0
    .org 0x60720-ORIGIN
L_00060720:
    mov.l L_0006086c,r3
    .org 0x60722-ORIGIN
L_00060722:
    mov.w r2,@(r0,r9)
    .org 0x60724-ORIGIN
L_00060724:
    mov #0x35,r0
    .org 0x60726-ORIGIN
L_00060726:
    mov.b @r11,r2
    .org 0x60728-ORIGIN
L_00060728:
    mov.b @(r0,r3),r6
    .org 0x6072a-ORIGIN
L_0006072a:
    sub r6,r2
    .org 0x6072c-ORIGIN
L_0006072c:
    exts.w r2,r0
    .org 0x6072e-ORIGIN
L_0006072e:
    mov #0x7f,r6
    .org 0x60730-ORIGIN
L_00060730:
    cmp/gt r6,r0
    .org 0x60732-ORIGIN
L_00060732:
    bf/s L_0006073a
    .org 0x60734-ORIGIN
L_00060734:
    mov.w r0,@(0x22,gbr)
    .org 0x60736-ORIGIN
L_00060736:
    bra L_00060746
    .org 0x60738-ORIGIN
L_00060738:
    mov #0x7f,r2
    .org 0x6073a-ORIGIN
L_0006073a:
    mov #-0x80,r6
    .org 0x6073c-ORIGIN
L_0006073c:
    cmp/ge r6,r0
    .org 0x6073e-ORIGIN
L_0006073e:
    bt L_00060744
    .org 0x60740-ORIGIN
L_00060740:
    bra L_00060746
    .org 0x60742-ORIGIN
L_00060742:
    mov #-0x80,r2
    .org 0x60744-ORIGIN
L_00060744:
    exts.b r0,r2
    .org 0x60746-ORIGIN
L_00060746:
    exts.b r2,r2
    .org 0x60748-ORIGIN
L_00060748:
    cmp/pz r2
    .org 0x6074a-ORIGIN
L_0006074a:
    mov r2,r0
    .org 0x6074c-ORIGIN
L_0006074c:
    bf/s L_0006075c
    .org 0x6074e-ORIGIN
L_0006074e:
    mov.b r0,@(0x34,gbr)
    .org 0x60750-ORIGIN
L_00060750:
    cmp/pz r2
    .org 0x60752-ORIGIN
L_00060752:
    bt L_00060768
    .org 0x60754-ORIGIN
L_00060754:
    bra L_00060768
    .org 0x60756-ORIGIN
L_00060756:
    mov #0x0,r2
    .org 0x60758-ORIGIN
L_00060758:
    .word 0x8c54
    .org 0x6075a-ORIGIN
L_0006075a:
    .word 0x03fc
    .org 0x6075c-ORIGIN
L_0006075c:
    neg r2,r0
    .org 0x6075e-ORIGIN
L_0006075e:
    exts.w r0,r2
    .org 0x60760-ORIGIN
L_00060760:
    cmp/pz r2
    .org 0x60762-ORIGIN
L_00060762:
    bt/s L_00060768
    .org 0x60764-ORIGIN
L_00060764:
    mov.w r0,@(0x22,gbr)
    .org 0x60766-ORIGIN
L_00060766:
    mov #0x0,r2
    .org 0x60768-ORIGIN
L_00060768:
    mov.l L_0006088c,r4
    .org 0x6076a-ORIGIN
L_0006076a:
    mov r2,r0
    .org 0x6076c-ORIGIN
L_0006076c:
    mov.l L_00060874,r5
    .org 0x6076e-ORIGIN
L_0006076e:
    extu.b r2,r6
    .org 0x60770-ORIGIN
L_00060770:
    jsr @r14
    .org 0x60772-ORIGIN
L_00060772:
    mov.b r0,@(0x35,gbr)
    .org 0x60774-ORIGIN
L_00060774:
    mov.w r0,@(0x10,r9)
    .org 0x60776-ORIGIN
L_00060776:
    mov.w @r8,r2
    .org 0x60778-ORIGIN
L_00060778:
    mov.w @(0xa,r10),r0
    .org 0x6077a-ORIGIN
L_0006077a:
    extu.w r2,r5
    .org 0x6077c-ORIGIN
L_0006077c:
    mov.l L_00060884,r6
    .org 0x6077e-ORIGIN
L_0006077e:
    extu.w r0,r2
    .org 0x60780-ORIGIN
L_00060780:
    mul.l r5,r2
    .org 0x60782-ORIGIN
L_00060782:
    mov r6,r0
    .org 0x60784-ORIGIN
L_00060784:
    jsr @r13
    .org 0x60786-ORIGIN
L_00060786:
    sts macl,r1
    .org 0x60788-ORIGIN
L_00060788:
    mov r0,r2
    .org 0x6078a-ORIGIN
L_0006078a:
    mov.w @(0x10,r9),r0
    .org 0x6078c-ORIGIN
L_0006078c:
    extu.w r2,r2
    .org 0x6078e-ORIGIN
L_0006078e:
    extu.w r0,r6
    .org 0x60790-ORIGIN
L_00060790:
    mul.l r2,r6
    .org 0x60792-ORIGIN
L_00060792:
    mov.l L_00060888,r6
    .org 0x60794-ORIGIN
L_00060794:
    sts macl,r2
    .org 0x60796-ORIGIN
L_00060796:
    cmp/hi r6,r2
    .org 0x60798-ORIGIN
L_00060798:
    bf L_0006079e
    .org 0x6079a-ORIGIN
L_0006079a:
    bra L_000607a6
    .org 0x6079c-ORIGIN
L_0006079c:
    mov r12,r6
    .org 0x6079e-ORIGIN
L_0006079e:
    shlr2 r2
    .org 0x607a0-ORIGIN
L_000607a0:
    shlr2 r2
    .org 0x607a2-ORIGIN
L_000607a2:
    shlr2 r2
    .org 0x607a4-ORIGIN
L_000607a4:
    mov r2,r6
    .org 0x607a6-ORIGIN
L_000607a6:
    mov r6,r0
    .org 0x607a8-ORIGIN
L_000607a8:
    mov.w r0,@(0x1e,gbr)
    .org 0x607aa-ORIGIN
L_000607aa:
    mov.w @(0x1a,r9),r0
    .org 0x607ac-ORIGIN
L_000607ac:
    extu.w r6,r2
    .org 0x607ae-ORIGIN
L_000607ae:
    mov.w L_0006084a,r6
    .org 0x607b0-ORIGIN
L_000607b0:
    extu.w r0,r5
    .org 0x607b2-ORIGIN
L_000607b2:
    mul.l r2,r5
    .org 0x607b4-ORIGIN
L_000607b4:
    mov r6,r0
    .org 0x607b6-ORIGIN
L_000607b6:
    jsr @r13
    .org 0x607b8-ORIGIN
L_000607b8:
    sts macl,r1
    .org 0x607ba-ORIGIN
L_000607ba:
    cmp/hi r12,r0
    .org 0x607bc-ORIGIN
L_000607bc:
    mov.l r0,@(0x14,gbr)
    .org 0x607be-ORIGIN
L_000607be:
    bf/s L_000607c4
    .org 0x607c0-ORIGIN
L_000607c0:
    mov r0,r2
    .org 0x607c2-ORIGIN
L_000607c2:
    mov #-0x1,r2
    .org 0x607c4-ORIGIN
L_000607c4:
    mov.w L_0006084c,r5
    .org 0x607c6-ORIGIN
L_000607c6:
    mov r2,r0
    .org 0x607c8-ORIGIN
L_000607c8:
    extu.w r2,r2
    .org 0x607ca-ORIGIN
L_000607ca:
    mov.w r0,@(0x1c,gbr)
    .org 0x607cc-ORIGIN
L_000607cc:
    mul.l r2,r5
    .org 0x607ce-ORIGIN
L_000607ce:
    mov r5,r6
    .org 0x607d0-ORIGIN
L_000607d0:
    add #-0x13,r6
    .org 0x607d2-ORIGIN
L_000607d2:
    mov r6,r0
    .org 0x607d4-ORIGIN
L_000607d4:
    jsr @r13
    .org 0x607d6-ORIGIN
L_000607d6:
    sts macl,r1
    .org 0x607d8-ORIGIN
L_000607d8:
    mov r0,r2
    .org 0x607da-ORIGIN
L_000607da:
    mov #0x4a,r0
    .org 0x607dc-ORIGIN
L_000607dc:
    mov.w r2,@(r0,r9)
    .org 0x607de-ORIGIN
L_000607de:
    mov.b @(0x24,gbr),r0
    .org 0x607e0-ORIGIN
L_000607e0:
    tst r0,r0
    .org 0x607e2-ORIGIN
L_000607e2:
    movt r0
    .org 0x607e4-ORIGIN
L_000607e4:
    mov.w L_0006084e,r10
    .org 0x607e6-ORIGIN
L_000607e6:
    xor #0x1,r0
    .org 0x607e8-ORIGIN
L_000607e8:
    mov.l @(0x20,r10),r6
    .org 0x607ea-ORIGIN
L_000607ea:
    mov r0,r2
    .org 0x607ec-ORIGIN
L_000607ec:
    tst r6,r6
    .org 0x607ee-ORIGIN
L_000607ee:
    bt/s L_00060814
    .org 0x607f0-ORIGIN
L_000607f0:
    mov.l r0,@(0x4,r10)
    .org 0x607f2-ORIGIN
L_000607f2:
    mov.l @r10,r6
    .org 0x607f4-ORIGIN
L_000607f4:
    tst r6,r6
    .org 0x607f6-ORIGIN
L_000607f6:
    bf L_00060822
    .org 0x607f8-ORIGIN
L_000607f8:
    mov.l L_00060890,r7
    .org 0x607fa-ORIGIN
L_000607fa:
    mov.w @(0x1c,r10),r0
    .org 0x607fc-ORIGIN
L_000607fc:
    mov.w @r7,r6
    .org 0x607fe-ORIGIN
L_000607fe:
    extu.w r0,r4
    .org 0x60800-ORIGIN
L_00060800:
    extu.w r6,r6
    .org 0x60802-ORIGIN
L_00060802:
    cmp/ge r6,r4
    .org 0x60804-ORIGIN
L_00060804:
    bt L_0006080e
    .org 0x60806-ORIGIN
L_00060806:
    add #0x1,r4
    .org 0x60808-ORIGIN
L_00060808:
    mov r4,r0
    .org 0x6080a-ORIGIN
L_0006080a:
    bra L_00060822
    .org 0x6080c-ORIGIN
L_0006080c:
    mov.w r0,@(0x1c,r10)
    .org 0x6080e-ORIGIN
L_0006080e:
    mov #0x1,r6
    .org 0x60810-ORIGIN
L_00060810:
    bra L_00060822
    .org 0x60812-ORIGIN
L_00060812:
    mov.l r6,@r10
    .org 0x60814-ORIGIN
L_00060814:
    tst r2,r2
    .org 0x60816-ORIGIN
L_00060816:
    bf L_00060822
    .org 0x60818-ORIGIN
L_00060818:
    mov.l @(0x24,r10),r6
    .org 0x6081a-ORIGIN
L_0006081a:
    tst r6,r6
    .org 0x6081c-ORIGIN
L_0006081c:
    bt L_00060822
    .org 0x6081e-ORIGIN
L_0006081e:
    mov #0x1,r6
    .org 0x60820-ORIGIN
L_00060820:
    mov.l r6,@(0x20,r10)
    .org 0x60822-ORIGIN
L_00060822:
    mov.l @r10,r0
    .org 0x60824-ORIGIN
L_00060824:
    mov.l r2,@(0x24,r10)
    .org 0x60826-ORIGIN
L_00060826:
    tst r0,r0
    .org 0x60828-ORIGIN
L_00060828:
    bt/s L_00060894
    .org 0x6082a-ORIGIN
L_0006082a:
    mov.l r0,@(0x28,gbr)
    .org 0x6082c-ORIGIN
L_0006082c:
    mov.w @(0x1a,r10),r0
    .org 0x6082e-ORIGIN
L_0006082e:
    mov.l @(0x10,r10),r6
    .org 0x60830-ORIGIN
L_00060830:
    extu.w r0,r4
    .org 0x60832-ORIGIN
L_00060832:
    mov r6,r2
    .org 0x60834-ORIGIN
L_00060834:
    add r4,r2
    .org 0x60836-ORIGIN
L_00060836:
    cmp/hs r6,r2
    .org 0x60838-ORIGIN
L_00060838:
    mov r2,r0
    .org 0x6083a-ORIGIN
L_0006083a:
    bt/s L_00060844
    .org 0x6083c-ORIGIN
L_0006083c:
    mov.l r0,@(0x10,gbr)
    .org 0x6083e-ORIGIN
L_0006083e:
    mov #-0x1,r2
    .org 0x60840-ORIGIN
L_00060840:
    mov r2,r0
    .org 0x60842-ORIGIN
L_00060842:
    mov.l r0,@(0x10,gbr)
    .org 0x60844-ORIGIN
L_00060844:
    mov r2,r6
    .org 0x60846-ORIGIN
L_00060846:
    bra L_00060898
    .org 0x60848-ORIGIN
L_00060848:
    mov r2,r0
    .org 0x6084a-ORIGIN
L_0006084a:
    .word 0x03fc
    .org 0x6084c-ORIGIN
L_0006084c:
    .word 0x139b
    .org 0x6084e-ORIGIN
L_0006084e:
    .word 0x99fc
    .org 0x60850-ORIGIN
L_00060850:
    .long 0xffff4185
    .org 0x60854-ORIGIN
L_00060854:
    .long 0xffff11d4
    .org 0x60858-ORIGIN
L_00060858:
    .long 0x00014f42
    .org 0x6085c-ORIGIN
L_0006085c:
    .long 0x00013c58
    .org 0x60860-ORIGIN
L_00060860:
    .long 0x000264cc
    .org 0x60864-ORIGIN
L_00060864:
    .long 0xffff401c
    .org 0x60868-ORIGIN
L_00060868:
    .long 0x00014f52
    .org 0x6086c-ORIGIN
L_0006086c:
    .long 0xffff2330
    .org 0x60870-ORIGIN
L_00060870:
    .long 0x0001453a
    .org 0x60874-ORIGIN
L_00060874:
    .long 0x00013c38
    .org 0x60878-ORIGIN
L_00060878:
    .long 0xffff1026
    .org 0x6087c-ORIGIN
L_0006087c:
    .long 0xffff22dc
    .org 0x60880-ORIGIN
L_00060880:
    .long 0x00021ce0
    .org 0x60884-ORIGIN
L_00060884:
    .long 0x00020202
    .org 0x60888-ORIGIN
L_00060888:
    .long 0x003fffc0
    .org 0x6088c-ORIGIN
L_0006088c:
    .long 0x0001454a
    .org 0x60890-ORIGIN
L_00060890:
    .long 0x00009066
    .org 0x60894-ORIGIN
L_00060894:
    mov.l @(0x14,r10),r6
    .org 0x60896-ORIGIN
L_00060896:
    mov r6,r0
    .org 0x60898-ORIGIN
L_00060898:
    tst r6,r6
    .org 0x6089a-ORIGIN
L_0006089a:
    bf/s L_000608b2
    .org 0x6089c-ORIGIN
L_0006089c:
    mov.l r0,@(0xc,gbr)
    .org 0x6089e-ORIGIN
L_0006089e:
    mov.l L_00060a34,r5
    .org 0x608a0-ORIGIN
L_000608a0:
    mov.l L_00060a38,r4
    .org 0x608a2-ORIGIN
L_000608a2:
    mov.b @(0x4,r5),r0
    .org 0x608a4-ORIGIN
L_000608a4:
    mov.l L_00060a3c,r5
    .org 0x608a6-ORIGIN
L_000608a6:
    jsr @r14
    .org 0x608a8-ORIGIN
L_000608a8:
    extu.b r0,r6
    .org 0x608aa-ORIGIN
L_000608aa:
    extu.w r0,r2
    .org 0x608ac-ORIGIN
L_000608ac:
    mov r2,r6
    .org 0x608ae-ORIGIN
L_000608ae:
    shll8 r6
    .org 0x608b0-ORIGIN
L_000608b0:
    sub r2,r6
    .org 0x608b2-ORIGIN
L_000608b2:
    mov.l L_00060a40,r2
    .org 0x608b4-ORIGIN
L_000608b4:
    mov #0x40,r0
    .org 0x608b6-ORIGIN
L_000608b6:
    mov.l r6,@(r0,r9)
    .org 0x608b8-ORIGIN
L_000608b8:
    mov.w @r2,r5
    .org 0x608ba-ORIGIN
L_000608ba:
    extu.w r5,r5
    .org 0x608bc-ORIGIN
L_000608bc:
    tst r5,r5
    .org 0x608be-ORIGIN
L_000608be:
    bt L_000608d8
    .org 0x608c0-ORIGIN
L_000608c0:
    mov r6,r1
    .org 0x608c2-ORIGIN
L_000608c2:
    jsr @r13
    .org 0x608c4-ORIGIN
L_000608c4:
    mov r5,r0
    .org 0x608c6-ORIGIN
L_000608c6:
    mov #-0x1,r5
    .org 0x608c8-ORIGIN
L_000608c8:
    mov r0,r6
    .org 0x608ca-ORIGIN
L_000608ca:
    extu.b r5,r5
    .org 0x608cc-ORIGIN
L_000608cc:
    cmp/hi r5,r0
    .org 0x608ce-ORIGIN
L_000608ce:
    bf/s L_000608d4
    .org 0x608d0-ORIGIN
L_000608d0:
    mov.l r0,@(0x14,gbr)
    .org 0x608d2-ORIGIN
L_000608d2:
    mov #-0x1,r6
    .org 0x608d4-ORIGIN
L_000608d4:
    bra L_000608dc
    .org 0x608d6-ORIGIN
L_000608d6:
    mov r6,r0
    .org 0x608d8-ORIGIN
L_000608d8:
    mov #-0x1,r6
    .org 0x608da-ORIGIN
L_000608da:
    mov r6,r0
    .org 0x608dc-ORIGIN
L_000608dc:
    extu.b r6,r6
    .org 0x608de-ORIGIN
L_000608de:
    mov.b r0,@(0x3b,gbr)
    .org 0x608e0-ORIGIN
L_000608e0:
    neg r6,r2
    .org 0x608e2-ORIGIN
L_000608e2:
    mov #-0x1,r12
    .org 0x608e4-ORIGIN
L_000608e4:
    add r12,r2
    .org 0x608e6-ORIGIN
L_000608e6:
    extu.b r2,r2
    .org 0x608e8-ORIGIN
L_000608e8:
    tst r2,r2
    .org 0x608ea-ORIGIN
L_000608ea:
    mov r2,r0
    .org 0x608ec-ORIGIN
L_000608ec:
    bf/s L_000608f2
    .org 0x608ee-ORIGIN
L_000608ee:
    mov.b r0,@(0x3a,gbr)
    .org 0x608f0-ORIGIN
L_000608f0:
    mov #0x0,r2
    .org 0x608f2-ORIGIN
L_000608f2:
    mov.l L_00060a44,r7
    .org 0x608f4-ORIGIN
L_000608f4:
    mov r2,r0
    .org 0x608f6-ORIGIN
L_000608f6:
    extu.b r2,r2
    .org 0x608f8-ORIGIN
L_000608f8:
    tst r2,r2
    .org 0x608fa-ORIGIN
L_000608fa:
    mov.b r0,@(0x5,r7)
    .org 0x608fc-ORIGIN
L_000608fc:
    movt r0
    .org 0x608fe-ORIGIN
L_000608fe:
    mov.l @r10,r2
    .org 0x60900-ORIGIN
L_00060900:
    tst r2,r2
    .org 0x60902-ORIGIN
L_00060902:
    bt/s L_00060922
    .org 0x60904-ORIGIN
L_00060904:
    mov.l r0,@(0x30,gbr)
    .org 0x60906-ORIGIN
L_00060906:
    mov.w @(0x18,r10),r0
    .org 0x60908-ORIGIN
L_00060908:
    mov.l @(0x8,r10),r6
    .org 0x6090a-ORIGIN
L_0006090a:
    extu.w r0,r4
    .org 0x6090c-ORIGIN
L_0006090c:
    mov r6,r5
    .org 0x6090e-ORIGIN
L_0006090e:
    add r4,r5
    .org 0x60910-ORIGIN
L_00060910:
    cmp/hs r6,r5
    .org 0x60912-ORIGIN
L_00060912:
    mov r5,r0
    .org 0x60914-ORIGIN
L_00060914:
    bt/s L_0006091e
    .org 0x60916-ORIGIN
L_00060916:
    mov.l r0,@(0x8,gbr)
    .org 0x60918-ORIGIN
L_00060918:
    mov #-0x1,r5
    .org 0x6091a-ORIGIN
L_0006091a:
    mov r5,r0
    .org 0x6091c-ORIGIN
L_0006091c:
    mov.l r0,@(0x8,gbr)
    .org 0x6091e-ORIGIN
L_0006091e:
    bra L_00060926
    .org 0x60920-ORIGIN
L_00060920:
    mov r5,r0
    .org 0x60922-ORIGIN
L_00060922:
    mov.l @(0xc,r10),r5
    .org 0x60924-ORIGIN
L_00060924:
    mov r5,r0
    .org 0x60926-ORIGIN
L_00060926:
    tst r5,r5
    .org 0x60928-ORIGIN
L_00060928:
    bf/s L_00060940
    .org 0x6092a-ORIGIN
L_0006092a:
    mov.l r0,@(0x4,gbr)
    .org 0x6092c-ORIGIN
L_0006092c:
    mov.l L_00060a34,r5
    .org 0x6092e-ORIGIN
L_0006092e:
    mov.l L_00060a48,r4
    .org 0x60930-ORIGIN
L_00060930:
    mov.b @(0x4,r5),r0
    .org 0x60932-ORIGIN
L_00060932:
    mov.l L_00060a4c,r5
    .org 0x60934-ORIGIN
L_00060934:
    jsr @r14
    .org 0x60936-ORIGIN
L_00060936:
    extu.b r0,r6
    .org 0x60938-ORIGIN
L_00060938:
    mov.w L_0006098a,r6
    .org 0x6093a-ORIGIN
L_0006093a:
    extu.w r0,r2
    .org 0x6093c-ORIGIN
L_0006093c:
    mul.l r2,r6
    .org 0x6093e-ORIGIN
L_0006093e:
    sts macl,r5
    .org 0x60940-ORIGIN
L_00060940:
    mov.l L_00060a50,r6
    .org 0x60942-ORIGIN
L_00060942:
    mov r5,r0
    .org 0x60944-ORIGIN
L_00060944:
    mov.l r0,@(0x0,gbr)
    .org 0x60946-ORIGIN
L_00060946:
    mov.w @r6,r2
    .org 0x60948-ORIGIN
L_00060948:
    mov.l L_00060a54,r4
    .org 0x6094a-ORIGIN
L_0006094a:
    extu.w r2,r0
    .org 0x6094c-ORIGIN
L_0006094c:
    shll8 r0
    .org 0x6094e-ORIGIN
L_0006094e:
    mov.b @r4,r14
    .org 0x60950-ORIGIN
L_00060950:
    tst r0,r0
    .org 0x60952-ORIGIN
L_00060952:
    bt/s L_0006098c
    .org 0x60954-ORIGIN
L_00060954:
    mov.l r0,@(0x14,gbr)
    .org 0x60956-ORIGIN
L_00060956:
    mov.w L_0006098a,r6
    .org 0x60958-ORIGIN
L_00060958:
    mov r5,r1
    .org 0x6095a-ORIGIN
L_0006095a:
    jsr @r13
    .org 0x6095c-ORIGIN
L_0006095c:
    mov r6,r0
    .org 0x6095e-ORIGIN
L_0006095e:
    mov r0,r2
    .org 0x60960-ORIGIN
L_00060960:
    mov #0x48,r0
    .org 0x60962-ORIGIN
L_00060962:
    extu.w r2,r6
    .org 0x60964-ORIGIN
L_00060964:
    mov.w r2,@(r0,r9)
    .org 0x60966-ORIGIN
L_00060966:
    mov r6,r1
    .org 0x60968-ORIGIN
L_00060968:
    shll8 r1
    .org 0x6096a-ORIGIN
L_0006096a:
    sub r6,r1
    .org 0x6096c-ORIGIN
L_0006096c:
    mov.l @(0x14,gbr),r0
    .org 0x6096e-ORIGIN
L_0006096e:
    shll2 r1
    .org 0x60970-ORIGIN
L_00060970:
    shll2 r1
    .org 0x60972-ORIGIN
L_00060972:
    jsr @r13
    .org 0x60974-ORIGIN
L_00060974:
    mov r1,r6
    .org 0x60976-ORIGIN
L_00060976:
    mov #-0x1,r6
    .org 0x60978-ORIGIN
L_00060978:
    mov r0,r2
    .org 0x6097a-ORIGIN
L_0006097a:
    extu.b r6,r6
    .org 0x6097c-ORIGIN
L_0006097c:
    cmp/hi r6,r0
    .org 0x6097e-ORIGIN
L_0006097e:
    bf/s L_00060984
    .org 0x60980-ORIGIN
L_00060980:
    mov.l r0,@(0x18,gbr)
    .org 0x60982-ORIGIN
L_00060982:
    mov #-0x1,r2
    .org 0x60984-ORIGIN
L_00060984:
    mov r2,r6
    .org 0x60986-ORIGIN
L_00060986:
    bra L_00060990
    .org 0x60988-ORIGIN
L_00060988:
    mov r2,r0
    .org 0x6098a-ORIGIN
L_0006098a:
    .word 0x042f
    .org 0x6098c-ORIGIN
L_0006098c:
    mov r12,r6
    .org 0x6098e-ORIGIN
L_0006098e:
    mov r12,r0
    .org 0x60990-ORIGIN
L_00060990:
    extu.b r6,r6
    .org 0x60992-ORIGIN
L_00060992:
    mov.b r0,@(0x37,gbr)
    .org 0x60994-ORIGIN
L_00060994:
    neg r6,r2
    .org 0x60996-ORIGIN
L_00060996:
    add r12,r2
    .org 0x60998-ORIGIN
L_00060998:
    extu.b r2,r2
    .org 0x6099a-ORIGIN
L_0006099a:
    tst r2,r2
    .org 0x6099c-ORIGIN
L_0006099c:
    mov r2,r0
    .org 0x6099e-ORIGIN
L_0006099e:
    bf/s L_000609a4
    .org 0x609a0-ORIGIN
L_000609a0:
    mov.b r0,@(0x36,gbr)
    .org 0x609a2-ORIGIN
L_000609a2:
    mov #0x0,r2
    .org 0x609a4-ORIGIN
L_000609a4:
    mov.l L_00060a44,r7
    .org 0x609a6-ORIGIN
L_000609a6:
    mov r2,r0
    .org 0x609a8-ORIGIN
L_000609a8:
    extu.b r2,r2
    .org 0x609aa-ORIGIN
L_000609aa:
    tst r2,r2
    .org 0x609ac-ORIGIN
L_000609ac:
    mov.b r0,@(0x6,r7)
    .org 0x609ae-ORIGIN
L_000609ae:
    movt r6
    .org 0x609b0-ORIGIN
L_000609b0:
    mov r6,r0
    .org 0x609b2-ORIGIN
L_000609b2:
    mov.l r0,@(0x2c,gbr)
    .org 0x609b4-ORIGIN
L_000609b4:
    mov #0x40,r0
    .org 0x609b6-ORIGIN
L_000609b6:
    mov.l @(r0,r9),r2
    .org 0x609b8-ORIGIN
L_000609b8:
    mov #0x34,r0
    .org 0x609ba-ORIGIN
L_000609ba:
    mov.w @(r0,r9),r0
    .org 0x609bc-ORIGIN
L_000609bc:
    mov.l r2,@(0x14,r10)
    .org 0x609be-ORIGIN
L_000609be:
    mov.w r0,@(0x1a,r10)
    .org 0x609c0-ORIGIN
L_000609c0:
    mov.l @(0x0,gbr),r0
    .org 0x609c2-ORIGIN
L_000609c2:
    mov.l r2,@(0x10,r10)
    .org 0x609c4-ORIGIN
L_000609c4:
    mov.l r0,@(0xc,r10)
    .org 0x609c6-ORIGIN
L_000609c6:
    mov.l r0,@(0x8,r10)
    .org 0x609c8-ORIGIN
L_000609c8:
    mov #0x4a,r0
    .org 0x609ca-ORIGIN
L_000609ca:
    mov.w @(r0,r9),r0
    .org 0x609cc-ORIGIN
L_000609cc:
    mov.w r0,@(0x18,r10)
    .org 0x609ce-ORIGIN
L_000609ce:
    mov.l @(0x28,gbr),r0
    .org 0x609d0-ORIGIN
L_000609d0:
    tst r0,r0
    .org 0x609d2-ORIGIN
L_000609d2:
    mov r14,r0
    .org 0x609d4-ORIGIN
L_000609d4:
    bt/s L_000609da
    .org 0x609d6-ORIGIN
L_000609d6:
    and #0xfd,r0
    .org 0x609d8-ORIGIN
L_000609d8:
    or #0x2,r0
    .org 0x609da-ORIGIN
L_000609da:
    mov.l L_00060a54,r4
    .org 0x609dc-ORIGIN
L_000609dc:
    tst r6,r6
    .org 0x609de-ORIGIN
L_000609de:
    mov.b r0,@r4
    .org 0x609e0-ORIGIN
L_000609e0:
    exts.b r0,r0
    .org 0x609e2-ORIGIN
L_000609e2:
    bt/s L_000609e8
    .org 0x609e4-ORIGIN
L_000609e4:
    and #0xdf,r0
    .org 0x609e6-ORIGIN
L_000609e6:
    or #0x20,r0
    .org 0x609e8-ORIGIN
L_000609e8:
    mov.b r0,@r4
    .org 0x609ea-ORIGIN
L_000609ea:
    exts.b r0,r2
    .org 0x609ec-ORIGIN
L_000609ec:
    mov.l @(0x30,gbr),r0
    .org 0x609ee-ORIGIN
L_000609ee:
    tst r0,r0
    .org 0x609f0-ORIGIN
L_000609f0:
    mov r2,r0
    .org 0x609f2-ORIGIN
L_000609f2:
    bt/s L_000609f8
    .org 0x609f4-ORIGIN
L_000609f4:
    and #0xbf,r0
    .org 0x609f6-ORIGIN
L_000609f6:
    or #0x40,r0
    .org 0x609f8-ORIGIN
L_000609f8:
    mov.b r0,@r4
    .org 0x609fa-ORIGIN
L_000609fa:
    ldc.l @r15+,gbr
    .org 0x609fc-ORIGIN
L_000609fc:
    lds.l @r15+,macl
    .org 0x609fe-ORIGIN
L_000609fe:
    lds.l @r15+,pr
    .org 0x60a00-ORIGIN
L_00060a00:
    mov.l @r15+,r14
    .org 0x60a02-ORIGIN
L_00060a02:
    mov.l @r15+,r13
    .org 0x60a04-ORIGIN
L_00060a04:
    mov.l @r15+,r12
    .org 0x60a06-ORIGIN
L_00060a06:
    mov.l @r15+,r11
    .org 0x60a08-ORIGIN
L_00060a08:
    mov.l @r15+,r10
    .org 0x60a0a-ORIGIN
L_00060a0a:
    mov.l @r15+,r9
    .org 0x60a0c-ORIGIN
L_00060a0c:
    rts
    .org 0x60a0e-ORIGIN
L_00060a0e:
    mov.l @r15+,r8
    .org 0x60a34-ORIGIN
L_00060a34:
    .long 0xffff1072
    .org 0x60a38-ORIGIN
L_00060a38:
    .long 0x00015002
    .org 0x60a3c-ORIGIN
L_00060a3c:
    .long 0x00013bd8
    .org 0x60a40-ORIGIN
L_00060a40:
    .long 0x000093e8
    .org 0x60a44-ORIGIN
L_00060a44:
    .long 0xffff288c
    .org 0x60a48-ORIGIN
L_00060a48:
    .long 0x00015012
    .org 0x60a4c-ORIGIN
L_00060a4c:
    .long 0x00013be8
    .org 0x60a50-ORIGIN
L_00060a50:
    .long 0x000093ec
    .org 0x60a54-ORIGIN
L_00060a54:
    .long 0xffff423e
