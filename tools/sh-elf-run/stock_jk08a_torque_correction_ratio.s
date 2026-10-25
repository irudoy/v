! Complete stock torque correction, delayed ratio state and real helpers.
    .text
    .balign 4
    .set ORIGIN,0x21bbc
    .org 0x21bbc-ORIGIN
L_00021bbc:
    mov.l r2,@-r15
    .org 0x21bbe-ORIGIN
L_00021bbe:
    tst r0,r0
    .org 0x21bc0-ORIGIN
L_00021bc0:
    bt L_00021c70
    .org 0x21bc2-ORIGIN
L_00021bc2:
    mov.l r3,@-r15
    .org 0x21bc4-ORIGIN
L_00021bc4:
    div0s r0,r1
    .org 0x21bc6-ORIGIN
L_00021bc6:
    movt r3
    .org 0x21bc8-ORIGIN
L_00021bc8:
    cmp/pl r0
    .org 0x21bca-ORIGIN
L_00021bca:
    bt L_00021bd0
    .org 0x21bcc-ORIGIN
L_00021bcc:
    add #-0x1,r0
    .org 0x21bce-ORIGIN
L_00021bce:
    not r0,r0
    .org 0x21bd0-ORIGIN
L_00021bd0:
    cmp/pl r1
    .org 0x21bd2-ORIGIN
L_00021bd2:
    bt L_00021bd8
    .org 0x21bd4-ORIGIN
L_00021bd4:
    add #-0x1,r1
    .org 0x21bd6-ORIGIN
L_00021bd6:
    not r1,r1
    .org 0x21bd8-ORIGIN
L_00021bd8:
    extu.w r0,r2
    .org 0x21bda-ORIGIN
L_00021bda:
    cmp/eq r2,r0
    .org 0x21bdc-ORIGIN
L_00021bdc:
    bf L_00021c7c
    .org 0x21bde-ORIGIN
L_00021bde:
    div0u
    .org 0x21be0-ORIGIN
L_00021be0:
    shll8 r0
    .org 0x21be2-ORIGIN
L_00021be2:
    cmp/hi r1,r0
    .org 0x21be4-ORIGIN
L_00021be4:
    bf L_00021c08
    .org 0x21be6-ORIGIN
L_00021be6:
    div1 r0,r1
    .org 0x21be8-ORIGIN
L_00021be8:
    div1 r0,r1
    .org 0x21bea-ORIGIN
L_00021bea:
    div1 r0,r1
    .org 0x21bec-ORIGIN
L_00021bec:
    div1 r0,r1
    .org 0x21bee-ORIGIN
L_00021bee:
    div1 r0,r1
    .org 0x21bf0-ORIGIN
L_00021bf0:
    div1 r0,r1
    .org 0x21bf2-ORIGIN
L_00021bf2:
    div1 r0,r1
    .org 0x21bf4-ORIGIN
L_00021bf4:
    div1 r0,r1
    .org 0x21bf6-ORIGIN
L_00021bf6:
    rotcl r1
    .org 0x21bf8-ORIGIN
L_00021bf8:
    extu.b r1,r0
    .org 0x21bfa-ORIGIN
L_00021bfa:
    rotcr r3
    .org 0x21bfc-ORIGIN
L_00021bfc:
    bf L_00021c02
    .org 0x21bfe-ORIGIN
L_00021bfe:
    not r0,r0
    .org 0x21c00-ORIGIN
L_00021c00:
    add #0x1,r0
    .org 0x21c02-ORIGIN
L_00021c02:
    mov.l @r15+,r3
    .org 0x21c04-ORIGIN
L_00021c04:
    rts
    .org 0x21c06-ORIGIN
L_00021c06:
    mov.l @r15+,r2
    .org 0x21c08-ORIGIN
L_00021c08:
    mov.l r4,@-r15
    .org 0x21c0a-ORIGIN
L_00021c0a:
    extu.w r1,r4
    .org 0x21c0c-ORIGIN
L_00021c0c:
    shll8 r0
    .org 0x21c0e-ORIGIN
L_00021c0e:
    shlr16 r1
    .org 0x21c10-ORIGIN
L_00021c10:
    div1 r0,r1
    .org 0x21c12-ORIGIN
L_00021c12:
    div1 r0,r1
    .org 0x21c14-ORIGIN
L_00021c14:
    div1 r0,r1
    .org 0x21c16-ORIGIN
L_00021c16:
    div1 r0,r1
    .org 0x21c18-ORIGIN
L_00021c18:
    div1 r0,r1
    .org 0x21c1a-ORIGIN
L_00021c1a:
    div1 r0,r1
    .org 0x21c1c-ORIGIN
L_00021c1c:
    div1 r0,r1
    .org 0x21c1e-ORIGIN
L_00021c1e:
    div1 r0,r1
    .org 0x21c20-ORIGIN
L_00021c20:
    div1 r0,r1
    .org 0x21c22-ORIGIN
L_00021c22:
    div1 r0,r1
    .org 0x21c24-ORIGIN
L_00021c24:
    div1 r0,r1
    .org 0x21c26-ORIGIN
L_00021c26:
    div1 r0,r1
    .org 0x21c28-ORIGIN
L_00021c28:
    div1 r0,r1
    .org 0x21c2a-ORIGIN
L_00021c2a:
    div1 r0,r1
    .org 0x21c2c-ORIGIN
L_00021c2c:
    div1 r0,r1
    .org 0x21c2e-ORIGIN
L_00021c2e:
    div1 r0,r1
    .org 0x21c30-ORIGIN
L_00021c30:
    extu.w r1,r2
    .org 0x21c32-ORIGIN
L_00021c32:
    xor r2,r1
    .org 0x21c34-ORIGIN
L_00021c34:
    addc r2,r2
    .org 0x21c36-ORIGIN
L_00021c36:
    shll16 r2
    .org 0x21c38-ORIGIN
L_00021c38:
    add r4,r1
    .org 0x21c3a-ORIGIN
L_00021c3a:
    div1 r0,r1
    .org 0x21c3c-ORIGIN
L_00021c3c:
    div1 r0,r1
    .org 0x21c3e-ORIGIN
L_00021c3e:
    div1 r0,r1
    .org 0x21c40-ORIGIN
L_00021c40:
    div1 r0,r1
    .org 0x21c42-ORIGIN
L_00021c42:
    div1 r0,r1
    .org 0x21c44-ORIGIN
L_00021c44:
    div1 r0,r1
    .org 0x21c46-ORIGIN
L_00021c46:
    div1 r0,r1
    .org 0x21c48-ORIGIN
L_00021c48:
    div1 r0,r1
    .org 0x21c4a-ORIGIN
L_00021c4a:
    div1 r0,r1
    .org 0x21c4c-ORIGIN
L_00021c4c:
    div1 r0,r1
    .org 0x21c4e-ORIGIN
L_00021c4e:
    div1 r0,r1
    .org 0x21c50-ORIGIN
L_00021c50:
    div1 r0,r1
    .org 0x21c52-ORIGIN
L_00021c52:
    div1 r0,r1
    .org 0x21c54-ORIGIN
L_00021c54:
    div1 r0,r1
    .org 0x21c56-ORIGIN
L_00021c56:
    div1 r0,r1
    .org 0x21c58-ORIGIN
L_00021c58:
    div1 r0,r1
    .org 0x21c5a-ORIGIN
L_00021c5a:
    rotcl r1
    .org 0x21c5c-ORIGIN
L_00021c5c:
    extu.w r1,r0
    .org 0x21c5e-ORIGIN
L_00021c5e:
    add r2,r0
    .org 0x21c60-ORIGIN
L_00021c60:
    rotcr r3
    .org 0x21c62-ORIGIN
L_00021c62:
    bf L_00021c68
    .org 0x21c64-ORIGIN
L_00021c64:
    not r0,r0
    .org 0x21c66-ORIGIN
L_00021c66:
    add #0x1,r0
    .org 0x21c68-ORIGIN
L_00021c68:
    mov.l @r15+,r4
    .org 0x21c6a-ORIGIN
L_00021c6a:
    mov.l @r15+,r3
    .org 0x21c6c-ORIGIN
L_00021c6c:
    rts
    .org 0x21c6e-ORIGIN
L_00021c6e:
    mov.l @r15+,r2
    .org 0x21c70-ORIGIN
L_00021c70:
    mov.l P_00021cd8,r1
    .org 0x21c72-ORIGIN
L_00021c72:
    mov.l P_00021cdc,r2
    .org 0x21c74-ORIGIN
L_00021c74:
    mov.l r2,@r1
    .org 0x21c76-ORIGIN
L_00021c76:
    mov #0x0,r0
    .org 0x21c78-ORIGIN
L_00021c78:
    rts
    .org 0x21c7a-ORIGIN
L_00021c7a:
    mov.l @r15+,r2
    .org 0x21c7c-ORIGIN
L_00021c7c:
    div0u
    .org 0x21c7e-ORIGIN
L_00021c7e:
    extu.w r1,r2
    .org 0x21c80-ORIGIN
L_00021c80:
    shll16 r2
    .org 0x21c82-ORIGIN
L_00021c82:
    shlr16 r1
    .org 0x21c84-ORIGIN
L_00021c84:
    rotcl r2
    .org 0x21c86-ORIGIN
L_00021c86:
    div1 r0,r1
    .org 0x21c88-ORIGIN
L_00021c88:
    rotcl r2
    .org 0x21c8a-ORIGIN
L_00021c8a:
    div1 r0,r1
    .org 0x21c8c-ORIGIN
L_00021c8c:
    rotcl r2
    .org 0x21c8e-ORIGIN
L_00021c8e:
    div1 r0,r1
    .org 0x21c90-ORIGIN
L_00021c90:
    rotcl r2
    .org 0x21c92-ORIGIN
L_00021c92:
    div1 r0,r1
    .org 0x21c94-ORIGIN
L_00021c94:
    rotcl r2
    .org 0x21c96-ORIGIN
L_00021c96:
    div1 r0,r1
    .org 0x21c98-ORIGIN
L_00021c98:
    rotcl r2
    .org 0x21c9a-ORIGIN
L_00021c9a:
    div1 r0,r1
    .org 0x21c9c-ORIGIN
L_00021c9c:
    rotcl r2
    .org 0x21c9e-ORIGIN
L_00021c9e:
    div1 r0,r1
    .org 0x21ca0-ORIGIN
L_00021ca0:
    rotcl r2
    .org 0x21ca2-ORIGIN
L_00021ca2:
    div1 r0,r1
    .org 0x21ca4-ORIGIN
L_00021ca4:
    rotcl r2
    .org 0x21ca6-ORIGIN
L_00021ca6:
    div1 r0,r1
    .org 0x21ca8-ORIGIN
L_00021ca8:
    rotcl r2
    .org 0x21caa-ORIGIN
L_00021caa:
    div1 r0,r1
    .org 0x21cac-ORIGIN
L_00021cac:
    rotcl r2
    .org 0x21cae-ORIGIN
L_00021cae:
    div1 r0,r1
    .org 0x21cb0-ORIGIN
L_00021cb0:
    rotcl r2
    .org 0x21cb2-ORIGIN
L_00021cb2:
    div1 r0,r1
    .org 0x21cb4-ORIGIN
L_00021cb4:
    rotcl r2
    .org 0x21cb6-ORIGIN
L_00021cb6:
    div1 r0,r1
    .org 0x21cb8-ORIGIN
L_00021cb8:
    rotcl r2
    .org 0x21cba-ORIGIN
L_00021cba:
    div1 r0,r1
    .org 0x21cbc-ORIGIN
L_00021cbc:
    rotcl r2
    .org 0x21cbe-ORIGIN
L_00021cbe:
    div1 r0,r1
    .org 0x21cc0-ORIGIN
L_00021cc0:
    rotcl r2
    .org 0x21cc2-ORIGIN
L_00021cc2:
    div1 r0,r1
    .org 0x21cc4-ORIGIN
L_00021cc4:
    rotcl r2
    .org 0x21cc6-ORIGIN
L_00021cc6:
    mov r2,r0
    .org 0x21cc8-ORIGIN
L_00021cc8:
    rotcr r3
    .org 0x21cca-ORIGIN
L_00021cca:
    bf L_00021cd0
    .org 0x21ccc-ORIGIN
L_00021ccc:
    not r0,r0
    .org 0x21cce-ORIGIN
L_00021cce:
    add #0x1,r0
    .org 0x21cd0-ORIGIN
L_00021cd0:
    mov.l @r15+,r3
    .org 0x21cd2-ORIGIN
L_00021cd2:
    rts
    .org 0x21cd4-ORIGIN
L_00021cd4:
    mov.l @r15+,r2
    .org 0x21cd8-ORIGIN
P_00021cd8:
    .byte 0xff
    .org 0x21cd9-ORIGIN
P_00021cd9:
    .byte 0xff
    .org 0x21cda-ORIGIN
P_00021cda:
    .byte 0x98
    .org 0x21cdb-ORIGIN
P_00021cdb:
    .byte 0x18
    .org 0x21cdc-ORIGIN
P_00021cdc:
    .byte 0x00
    .org 0x21cdd-ORIGIN
P_00021cdd:
    .byte 0x00
    .org 0x21cde-ORIGIN
P_00021cde:
    .byte 0x04
    .org 0x21cdf-ORIGIN
P_00021cdf:
    .byte 0x4e
    .org 0x263f4-ORIGIN
L_000263f4:
    mov.l P_0002640c,r0
    .org 0x263f6-ORIGIN
L_000263f6:
    extu.w r5,r5
    .org 0x263f8-ORIGIN
L_000263f8:
    cmp/hs r0,r5
    .org 0x263fa-ORIGIN
L_000263fa:
    bt L_00026402
    .org 0x263fc-ORIGIN
L_000263fc:
    mov.l P_00026408,r6
    .org 0x263fe-ORIGIN
L_000263fe:
    jmp @r6
    .org 0x26400-ORIGIN
L_00026400:
    mov #0x0,r3
    .org 0x26402-ORIGIN
L_00026402:
    rts
    .org 0x26404-ORIGIN
L_00026404:
    mov.w @(0x1e,r4),r0
    .org 0x26408-ORIGIN
P_00026408:
    .byte 0x00
    .org 0x26409-ORIGIN
P_00026409:
    .byte 0x02
    .org 0x2640a-ORIGIN
P_0002640a:
    .byte 0x6a
    .org 0x2640b-ORIGIN
P_0002640b:
    .byte 0x64
    .org 0x2640c-ORIGIN
P_0002640c:
    .byte 0x00
    .org 0x2640d-ORIGIN
P_0002640d:
    .byte 0x00
    .org 0x2640e-ORIGIN
P_0002640e:
    .byte 0xf0
    .org 0x2640f-ORIGIN
P_0002640f:
    .byte 0x00
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
    mov.l P_000264f4,r7
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
    mov.l P_000264f0,r6
    .org 0x264ea-ORIGIN
L_000264ea:
    jmp @r6
    .org 0x264ec-ORIGIN
L_000264ec:
    extu.w r1,r0
    .org 0x264f0-ORIGIN
P_000264f0:
    .byte 0x00
    .org 0x264f1-ORIGIN
P_000264f1:
    .byte 0x02
    .org 0x264f2-ORIGIN
P_000264f2:
    .byte 0x67
    .org 0x264f3-ORIGIN
P_000264f3:
    .byte 0x40
    .org 0x264f4-ORIGIN
P_000264f4:
    .byte 0x00
    .org 0x264f5-ORIGIN
P_000264f5:
    .byte 0x02
    .org 0x264f6-ORIGIN
P_000264f6:
    .byte 0x69
    .org 0x264f7-ORIGIN
P_000264f7:
    .byte 0x84
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
    mov.l P_000269c0,r2
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
P_000269c0:
    .byte 0x00
    .org 0x269c1-ORIGIN
P_000269c1:
    .byte 0x02
    .org 0x269c2-ORIGIN
P_000269c2:
    .byte 0x6c
    .org 0x269c3-ORIGIN
P_000269c3:
    .byte 0x78
    .org 0x26a64-ORIGIN
L_00026a64:
    shlr r5
    .org 0x26a66-ORIGIN
L_00026a66:
    rotcr r3
    .org 0x26a68-ORIGIN
L_00026a68:
    shlr r5
    .org 0x26a6a-ORIGIN
L_00026a6a:
    rotcr r3
    .org 0x26a6c-ORIGIN
L_00026a6c:
    shlr r5
    .org 0x26a6e-ORIGIN
L_00026a6e:
    rotcr r3
    .org 0x26a70-ORIGIN
L_00026a70:
    shlr r5
    .org 0x26a72-ORIGIN
L_00026a72:
    rotcr r3
    .org 0x26a74-ORIGIN
L_00026a74:
    shlr r5
    .org 0x26a76-ORIGIN
L_00026a76:
    rotcr r3
    .org 0x26a78-ORIGIN
L_00026a78:
    shlr r5
    .org 0x26a7a-ORIGIN
L_00026a7a:
    rotcr r3
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
    mov.l P_00026abc,r6
    .org 0x26ab6-ORIGIN
L_00026ab6:
    jmp @r6
    .org 0x26ab8-ORIGIN
L_00026ab8:
    nop
    .org 0x26abc-ORIGIN
P_00026abc:
    .byte 0x00
    .org 0x26abd-ORIGIN
P_00026abd:
    .byte 0x02
    .org 0x26abe-ORIGIN
P_00026abe:
    .byte 0x67
    .org 0x26abf-ORIGIN
P_00026abf:
    .byte 0x40
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
    .org 0x64a1c-ORIGIN
L_00064a1c:
    mov.l r8,@-r15
    .org 0x64a1e-ORIGIN
L_00064a1e:
    mov.l r9,@-r15
    .org 0x64a20-ORIGIN
L_00064a20:
    mov.l r10,@-r15
    .org 0x64a22-ORIGIN
L_00064a22:
    mov.l r11,@-r15
    .org 0x64a24-ORIGIN
L_00064a24:
    mov.l r12,@-r15
    .org 0x64a26-ORIGIN
L_00064a26:
    mov.l r13,@-r15
    .org 0x64a28-ORIGIN
L_00064a28:
    mov.l r14,@-r15
    .org 0x64a2a-ORIGIN
L_00064a2a:
    sts.l pr,@-r15
    .org 0x64a2c-ORIGIN
L_00064a2c:
    sts.l macl,@-r15
    .org 0x64a2e-ORIGIN
L_00064a2e:
    mov.l P_00064b64,r6
    .org 0x64a30-ORIGIN
L_00064a30:
    mov #0x17,r0
    .org 0x64a32-ORIGIN
L_00064a32:
    mov.l P_00064b68,r4
    .org 0x64a34-ORIGIN
L_00064a34:
    mov.b @(r0,r6),r2
    .org 0x64a36-ORIGIN
L_00064a36:
    mov.l P_00064b50,r12
    .org 0x64a38-ORIGIN
L_00064a38:
    extu.b r2,r5
    .org 0x64a3a-ORIGIN
L_00064a3a:
    mov.l P_00064b6c,r2
    .org 0x64a3c-ORIGIN
L_00064a3c:
    shll8 r5
    .org 0x64a3e-ORIGIN
L_00064a3e:
    mov.w P_00064b34,r10
    .org 0x64a40-ORIGIN
L_00064a40:
    jsr @r2
    .org 0x64a42-ORIGIN
L_00064a42:
    extu.w r5,r5
    .org 0x64a44-ORIGIN
L_00064a44:
    extu.w r0,r2
    .org 0x64a46-ORIGIN
L_00064a46:
    mov.w P_00064b36,r0
    .org 0x64a48-ORIGIN
L_00064a48:
    mov.l P_00064b70,r6
    .org 0x64a4a-ORIGIN
L_00064a4a:
    mov.w r2,@(r0,r12)
    .org 0x64a4c-ORIGIN
L_00064a4c:
    mov #0x4c,r0
    .org 0x64a4e-ORIGIN
L_00064a4e:
    mov.w @(r0,r6),r9
    .org 0x64a50-ORIGIN
L_00064a50:
    mov #0x54,r0
    .org 0x64a52-ORIGIN
L_00064a52:
    mov.w @(r0,r6),r8
    .org 0x64a54-ORIGIN
L_00064a54:
    mov.w P_00064b38,r0
    .org 0x64a56-ORIGIN
L_00064a56:
    extu.w r9,r9
    .org 0x64a58-ORIGIN
L_00064a58:
    extu.w r8,r8
    .org 0x64a5a-ORIGIN
L_00064a5a:
    mov.w @(r0,r12),r4
    .org 0x64a5c-ORIGIN
L_00064a5c:
    add r9,r4
    .org 0x64a5e-ORIGIN
L_00064a5e:
    add r8,r4
    .org 0x64a60-ORIGIN
L_00064a60:
    cmp/gt r10,r4
    .org 0x64a62-ORIGIN
L_00064a62:
    bf L_00064a66
    .org 0x64a64-ORIGIN
L_00064a64:
    mov r10,r4
    .org 0x64a66-ORIGIN
L_00064a66:
    exts.w r4,r4
    .org 0x64a68-ORIGIN
L_00064a68:
    mov.l P_00064b50,r11
    .org 0x64a6a-ORIGIN
L_00064a6a:
    mov.w P_00064b3a,r0
    .org 0x64a6c-ORIGIN
L_00064a6c:
    mov r2,r5
    .org 0x64a6e-ORIGIN
L_00064a6e:
    mul.l r2,r4
    .org 0x64a70-ORIGIN
L_00064a70:
    mov #0x1,r2
    .org 0x64a72-ORIGIN
L_00064a72:
    mov.w @(r0,r11),r7
    .org 0x64a74-ORIGIN
L_00064a74:
    shll16 r2
    .org 0x64a76-ORIGIN
L_00064a76:
    sub r5,r2
    .org 0x64a78-ORIGIN
L_00064a78:
    sts macl,r6
    .org 0x64a7a-ORIGIN
L_00064a7a:
    mul.l r2,r7
    .org 0x64a7c-ORIGIN
L_00064a7c:
    sts macl,r2
    .org 0x64a7e-ORIGIN
L_00064a7e:
    add r2,r6
    .org 0x64a80-ORIGIN
L_00064a80:
    swap.w r6,r2
    .org 0x64a82-ORIGIN
L_00064a82:
    exts.w r2,r2
    .org 0x64a84-ORIGIN
L_00064a84:
    exts.w r2,r13
    .org 0x64a86-ORIGIN
L_00064a86:
    cmp/ge r4,r13
    .org 0x64a88-ORIGIN
L_00064a88:
    bt/s L_00064a96
    .org 0x64a8a-ORIGIN
L_00064a8a:
    mov.w r13,@(r0,r11)
    .org 0x64a8c-ORIGIN
L_00064a8c:
    cmp/eq r7,r13
    .org 0x64a8e-ORIGIN
L_00064a8e:
    bf L_00064a96
    .org 0x64a90-ORIGIN
L_00064a90:
    mov.l P_00064b50,r3
    .org 0x64a92-ORIGIN
L_00064a92:
    add #0x1,r13
    .org 0x64a94-ORIGIN
L_00064a94:
    mov.w r13,@(r0,r3)
    .org 0x64a96-ORIGIN
L_00064a96:
    mov.l P_00064b74,r11
    .org 0x64a98-ORIGIN
L_00064a98:
    mov #0x33,r0
    .org 0x64a9a-ORIGIN
L_00064a9a:
    mov.b @(r0,r11),r7
    .org 0x64a9c-ORIGIN
L_00064a9c:
    mov r7,r0
    .org 0x64a9e-ORIGIN
L_00064a9e:
    tst #0x8,r0
    .org 0x64aa0-ORIGIN
L_00064aa0:
    bf L_00064ac4
    .org 0x64aa2-ORIGIN
L_00064aa2:
    mov #0x0,r5
    .org 0x64aa4-ORIGIN
L_00064aa4:
    mov.w P_00064b3c,r14
    .org 0x64aa6-ORIGIN
L_00064aa6:
    mov #0xa,r4
    .org 0x64aa8-ORIGIN
L_00064aa8:
    extu.b r5,r5
    .org 0x64aaa-ORIGIN
L_00064aaa:
    mov r12,r6
    .org 0x64aac-ORIGIN
L_00064aac:
    mov r5,r0
    .org 0x64aae-ORIGIN
L_00064aae:
    add #0x1,r5
    .org 0x64ab0-ORIGIN
L_00064ab0:
    extu.b r5,r5
    .org 0x64ab2-ORIGIN
L_00064ab2:
    add r14,r6
    .org 0x64ab4-ORIGIN
L_00064ab4:
    shll r0
    .org 0x64ab6-ORIGIN
L_00064ab6:
    cmp/ge r4,r5
    .org 0x64ab8-ORIGIN
L_00064ab8:
    bf/s L_00064aa8
    .org 0x64aba-ORIGIN
L_00064aba:
    mov.w r13,@(r0,r6)
    .org 0x64abc-ORIGIN
L_00064abc:
    mov #0x8,r0
    .org 0x64abe-ORIGIN
L_00064abe:
    or r0,r7
    .org 0x64ac0-ORIGIN
L_00064ac0:
    mov #0x33,r0
    .org 0x64ac2-ORIGIN
L_00064ac2:
    mov.b r7,@(r0,r11)
    .org 0x64ac4-ORIGIN
L_00064ac4:
    mov.l P_00064b78,r2
    .org 0x64ac6-ORIGIN
L_00064ac6:
    mov.b @r2,r6
    .org 0x64ac8-ORIGIN
L_00064ac8:
    extu.b r6,r6
    .org 0x64aca-ORIGIN
L_00064aca:
    tst r6,r6
    .org 0x64acc-ORIGIN
L_00064acc:
    bf L_00064ad2
    .org 0x64ace-ORIGIN
L_00064ace:
    bra L_00064af0
    .org 0x64ad0-ORIGIN
L_00064ad0:
    mov r13,r6
    .org 0x64ad2-ORIGIN
L_00064ad2:
    mov r6,r2
    .org 0x64ad4-ORIGIN
L_00064ad4:
    add #-0x1,r2
    .org 0x64ad6-ORIGIN
L_00064ad6:
    mov #0x9,r5
    .org 0x64ad8-ORIGIN
L_00064ad8:
    cmp/gt r5,r2
    .org 0x64ada-ORIGIN
L_00064ada:
    bf L_00064ae0
    .org 0x64adc-ORIGIN
L_00064adc:
    bra L_00064ae4
    .org 0x64ade-ORIGIN
L_00064ade:
    mov #0x9,r2
    .org 0x64ae0-ORIGIN
L_00064ae0:
    add #-0x1,r6
    .org 0x64ae2-ORIGIN
L_00064ae2:
    mov r6,r2
    .org 0x64ae4-ORIGIN
L_00064ae4:
    mov.w P_00064b3c,r14
    .org 0x64ae6-ORIGIN
L_00064ae6:
    extu.b r2,r0
    .org 0x64ae8-ORIGIN
L_00064ae8:
    mov r12,r5
    .org 0x64aea-ORIGIN
L_00064aea:
    shll r0
    .org 0x64aec-ORIGIN
L_00064aec:
    add r14,r5
    .org 0x64aee-ORIGIN
L_00064aee:
    mov.w @(r0,r5),r6
    .org 0x64af0-ORIGIN
L_00064af0:
    mov.l P_00064b50,r3
    .org 0x64af2-ORIGIN
L_00064af2:
    exts.w r6,r11
    .org 0x64af4-ORIGIN
L_00064af4:
    mov.w P_00064b3e,r0
    .org 0x64af6-ORIGIN
L_00064af6:
    mov r12,r7
    .org 0x64af8-ORIGIN
L_00064af8:
    mov.w P_00064b3c,r14
    .org 0x64afa-ORIGIN
L_00064afa:
    mov #0x9,r4
    .org 0x64afc-ORIGIN
L_00064afc:
    mov.w r11,@(r0,r3)
    .org 0x64afe-ORIGIN
L_00064afe:
    add r14,r7
    .org 0x64b00-ORIGIN
L_00064b00:
    add #-0x2,r7
    .org 0x64b02-ORIGIN
L_00064b02:
    extu.b r4,r4
    .org 0x64b04-ORIGIN
L_00064b04:
    mov r12,r6
    .org 0x64b06-ORIGIN
L_00064b06:
    mov r4,r0
    .org 0x64b08-ORIGIN
L_00064b08:
    shll r0
    .org 0x64b0a-ORIGIN
L_00064b0a:
    mov.w @(r0,r7),r5
    .org 0x64b0c-ORIGIN
L_00064b0c:
    mov r4,r0
    .org 0x64b0e-ORIGIN
L_00064b0e:
    add #-0x1,r4
    .org 0x64b10-ORIGIN
L_00064b10:
    extu.b r4,r4
    .org 0x64b12-ORIGIN
L_00064b12:
    extu.b r4,r4
    .org 0x64b14-ORIGIN
L_00064b14:
    add r14,r6
    .org 0x64b16-ORIGIN
L_00064b16:
    shll r0
    .org 0x64b18-ORIGIN
L_00064b18:
    cmp/pl r4
    .org 0x64b1a-ORIGIN
L_00064b1a:
    bt/s L_00064b02
    .org 0x64b1c-ORIGIN
L_00064b1c:
    mov.w r5,@(r0,r6)
    .org 0x64b1e-ORIGIN
L_00064b1e:
    mov.w P_00064b3c,r0
    .org 0x64b20-ORIGIN
L_00064b20:
    mov.l P_00064b7c,r6
    .org 0x64b22-ORIGIN
L_00064b22:
    mov.w r13,@(r0,r12)
    .org 0x64b24-ORIGIN
L_00064b24:
    mov.b @r6,r0
    .org 0x64b26-ORIGIN
L_00064b26:
    tst #0x20,r0
    .org 0x64b28-ORIGIN
L_00064b28:
    bt L_00064b80
    .org 0x64b2a-ORIGIN
L_00064b2a:
    mov.l P_00064b50,r3
    .org 0x64b2c-ORIGIN
L_00064b2c:
    mov.w P_00064b40,r0
    .org 0x64b2e-ORIGIN
L_00064b2e:
    mov.w @(r0,r3),r5
    .org 0x64b30-ORIGIN
L_00064b30:
    bra L_00064b82
    .org 0x64b32-ORIGIN
L_00064b32:
    nop
    .org 0x64b34-ORIGIN
P_00064b34:
    .byte 0x7f
    .org 0x64b35-ORIGIN
P_00064b35:
    .byte 0xff
    .org 0x64b36-ORIGIN
P_00064b36:
    .byte 0x03
    .org 0x64b37-ORIGIN
P_00064b37:
    .byte 0x7c
    .org 0x64b38-ORIGIN
P_00064b38:
    .byte 0x07
    .org 0x64b39-ORIGIN
P_00064b39:
    .byte 0x3a
    .org 0x64b3a-ORIGIN
P_00064b3a:
    .byte 0x07
    .org 0x64b3b-ORIGIN
P_00064b3b:
    .byte 0x12
    .org 0x64b3c-ORIGIN
P_00064b3c:
    .byte 0x07
    .org 0x64b3d-ORIGIN
P_00064b3d:
    .byte 0x6a
    .org 0x64b3e-ORIGIN
P_00064b3e:
    .byte 0x07
    .org 0x64b3f-ORIGIN
P_00064b3f:
    .byte 0x14
    .org 0x64b40-ORIGIN
P_00064b40:
    .byte 0x06
    .org 0x64b41-ORIGIN
P_00064b41:
    .byte 0x48
    .org 0x64b50-ORIGIN
P_00064b50:
    .byte 0xff
    .org 0x64b51-ORIGIN
P_00064b51:
    .byte 0xff
    .org 0x64b52-ORIGIN
P_00064b52:
    .byte 0x12
    .org 0x64b53-ORIGIN
P_00064b53:
    .byte 0x8c
    .org 0x64b64-ORIGIN
P_00064b64:
    .byte 0xff
    .org 0x64b65-ORIGIN
P_00064b65:
    .byte 0xff
    .org 0x64b66-ORIGIN
P_00064b66:
    .byte 0x11
    .org 0x64b67-ORIGIN
P_00064b67:
    .byte 0x9c
    .org 0x64b68-ORIGIN
P_00064b68:
    .byte 0x00
    .org 0x64b69-ORIGIN
P_00064b69:
    .byte 0x01
    .org 0x64b6a-ORIGIN
P_00064b6a:
    .byte 0x4e
    .org 0x64b6b-ORIGIN
P_00064b6b:
    .byte 0x52
    .org 0x64b6c-ORIGIN
P_00064b6c:
    .byte 0x00
    .org 0x64b6d-ORIGIN
P_00064b6d:
    .byte 0x02
    .org 0x64b6e-ORIGIN
P_00064b6e:
    .byte 0x63
    .org 0x64b6f-ORIGIN
P_00064b6f:
    .byte 0xf4
    .org 0x64b70-ORIGIN
P_00064b70:
    .byte 0xff
    .org 0x64b71-ORIGIN
P_00064b71:
    .byte 0xff
    .org 0x64b72-ORIGIN
P_00064b72:
    .byte 0x23
    .org 0x64b73-ORIGIN
P_00064b73:
    .byte 0xbc
    .org 0x64b74-ORIGIN
P_00064b74:
    .byte 0xff
    .org 0x64b75-ORIGIN
P_00064b75:
    .byte 0xff
    .org 0x64b76-ORIGIN
P_00064b76:
    .byte 0x24
    .org 0x64b77-ORIGIN
P_00064b77:
    .byte 0x70
    .org 0x64b78-ORIGIN
P_00064b78:
    .byte 0x00
    .org 0x64b79-ORIGIN
P_00064b79:
    .byte 0x00
    .org 0x64b7a-ORIGIN
P_00064b7a:
    .byte 0x8c
    .org 0x64b7b-ORIGIN
P_00064b7b:
    .byte 0x61
    .org 0x64b7c-ORIGIN
P_00064b7c:
    .byte 0x00
    .org 0x64b7d-ORIGIN
P_00064b7d:
    .byte 0x00
    .org 0x64b7e-ORIGIN
P_00064b7e:
    .byte 0x83
    .org 0x64b7f-ORIGIN
P_00064b7f:
    .byte 0xc1
    .org 0x64b80-ORIGIN
L_00064b80:
    mov r11,r5
    .org 0x64b82-ORIGIN
L_00064b82:
    mov.l P_00064dcc,r2
    .org 0x64b84-ORIGIN
L_00064b84:
    mov.b @r2,r0
    .org 0x64b86-ORIGIN
L_00064b86:
    tst #0x2,r0
    .org 0x64b88-ORIGIN
L_00064b88:
    bt L_00064bac
    .org 0x64b8a-ORIGIN
L_00064b8a:
    mov.l P_00064dd0,r3
    .org 0x64b8c-ORIGIN
L_00064b8c:
    mov #0x6,r2
    .org 0x64b8e-ORIGIN
L_00064b8e:
    mov.w P_00064ca4,r0
    .org 0x64b90-ORIGIN
L_00064b90:
    exts.w r5,r5
    .org 0x64b92-ORIGIN
L_00064b92:
    mov.l P_00064dd4,r13
    .org 0x64b94-ORIGIN
L_00064b94:
    mov.b @(r0,r3),r6
    .org 0x64b96-ORIGIN
L_00064b96:
    mov #0x6,r0
    .org 0x64b98-ORIGIN
L_00064b98:
    extu.b r6,r6
    .org 0x64b9a-ORIGIN
L_00064b9a:
    sub r6,r2
    .org 0x64b9c-ORIGIN
L_00064b9c:
    mov.l P_00064dd8,r6
    .org 0x64b9e-ORIGIN
L_00064b9e:
    mul.l r5,r2
    .org 0x64ba0-ORIGIN
L_00064ba0:
    jsr @r6
    .org 0x64ba2-ORIGIN
L_00064ba2:
    sts macl,r1
    .org 0x64ba4-ORIGIN
L_00064ba4:
    mov r0,r2
    .org 0x64ba6-ORIGIN
L_00064ba6:
    mov.w P_00064ca6,r0
    .org 0x64ba8-ORIGIN
L_00064ba8:
    bra L_00064bb4
    .org 0x64baa-ORIGIN
L_00064baa:
    mov.w r2,@(r0,r13)
    .org 0x64bac-ORIGIN
L_00064bac:
    mov.l P_00064dd4,r13
    .org 0x64bae-ORIGIN
L_00064bae:
    mov r5,r2
    .org 0x64bb0-ORIGIN
L_00064bb0:
    mov.w P_00064ca6,r0
    .org 0x64bb2-ORIGIN
L_00064bb2:
    mov.w r5,@(r0,r13)
    .org 0x64bb4-ORIGIN
L_00064bb4:
    mov.l P_00064dd0,r3
    .org 0x64bb6-ORIGIN
L_00064bb6:
    mov.w P_00064ca8,r0
    .org 0x64bb8-ORIGIN
L_00064bb8:
    mov.w @(r0,r3),r6
    .org 0x64bba-ORIGIN
L_00064bba:
    cmp/eq r10,r6
    .org 0x64bbc-ORIGIN
L_00064bbc:
    bf L_00064bca
    .org 0x64bbe-ORIGIN
L_00064bbe:
    mov.l P_00064dd0,r3
    .org 0x64bc0-ORIGIN
L_00064bc0:
    mov #-0x1,r2
    .org 0x64bc2-ORIGIN
L_00064bc2:
    mov.w P_00064caa,r0
    .org 0x64bc4-ORIGIN
L_00064bc4:
    mov.b r2,@(r0,r3)
    .org 0x64bc6-ORIGIN
L_00064bc6:
    bra L_00064c24
    .org 0x64bc8-ORIGIN
L_00064bc8:
    nop
    .org 0x64bca-ORIGIN
L_00064bca:
    mov.l P_00064dd0,r12
    .org 0x64bcc-ORIGIN
L_00064bcc:
    exts.w r2,r2
    .org 0x64bce-ORIGIN
L_00064bce:
    mov.w P_00064cac,r0
    .org 0x64bd0-ORIGIN
L_00064bd0:
    tst r2,r2
    .org 0x64bd2-ORIGIN
L_00064bd2:
    mov r9,r7
    .org 0x64bd4-ORIGIN
L_00064bd4:
    mov.w @(r0,r12),r4
    .org 0x64bd6-ORIGIN
L_00064bd6:
    mov.w P_00064ca8,r0
    .org 0x64bd8-ORIGIN
L_00064bd8:
    extu.w r4,r4
    .org 0x64bda-ORIGIN
L_00064bda:
    mov.w @(r0,r12),r14
    .org 0x64bdc-ORIGIN
L_00064bdc:
    add r9,r14
    .org 0x64bde-ORIGIN
L_00064bde:
    add r4,r14
    .org 0x64be0-ORIGIN
L_00064be0:
    bt/s L_00064c0c
    .org 0x64be2-ORIGIN
L_00064be2:
    add r8,r14
    .org 0x64be4-ORIGIN
L_00064be4:
    mov.l P_00064dd8,r6
    .org 0x64be6-ORIGIN
L_00064be6:
    shll8 r14
    .org 0x64be8-ORIGIN
L_00064be8:
    exts.w r2,r0
    .org 0x64bea-ORIGIN
L_00064bea:
    mov r14,r5
    .org 0x64bec-ORIGIN
L_00064bec:
    jsr @r6
    .org 0x64bee-ORIGIN
L_00064bee:
    mov r14,r1
    .org 0x64bf0-ORIGIN
L_00064bf0:
    cmp/pz r0
    .org 0x64bf2-ORIGIN
L_00064bf2:
    bt/s L_00064bf8
    .org 0x64bf4-ORIGIN
L_00064bf4:
    mov r0,r6
    .org 0x64bf6-ORIGIN
L_00064bf6:
    mov #0x0,r6
    .org 0x64bf8-ORIGIN
L_00064bf8:
    mov #-0x1,r5
    .org 0x64bfa-ORIGIN
L_00064bfa:
    extu.b r5,r2
    .org 0x64bfc-ORIGIN
L_00064bfc:
    cmp/gt r2,r6
    .org 0x64bfe-ORIGIN
L_00064bfe:
    bt L_00064c02
    .org 0x64c00-ORIGIN
L_00064c00:
    mov r6,r2
    .org 0x64c02-ORIGIN
L_00064c02:
    mov.l P_00064dd0,r3
    .org 0x64c04-ORIGIN
L_00064c04:
    mov.w P_00064caa,r0
    .org 0x64c06-ORIGIN
L_00064c06:
    mov.b r2,@(r0,r3)
    .org 0x64c08-ORIGIN
L_00064c08:
    bra L_00064c24
    .org 0x64c0a-ORIGIN
L_00064c0a:
    nop
    .org 0x64c0c-ORIGIN
L_00064c0c:
    cmp/pl r14
    .org 0x64c0e-ORIGIN
L_00064c0e:
    bf L_00064c1c
    .org 0x64c10-ORIGIN
L_00064c10:
    mov.l P_00064dd0,r3
    .org 0x64c12-ORIGIN
L_00064c12:
    mov #-0x1,r2
    .org 0x64c14-ORIGIN
L_00064c14:
    mov.w P_00064caa,r0
    .org 0x64c16-ORIGIN
L_00064c16:
    mov.b r2,@(r0,r3)
    .org 0x64c18-ORIGIN
L_00064c18:
    bra L_00064c24
    .org 0x64c1a-ORIGIN
L_00064c1a:
    nop
    .org 0x64c1c-ORIGIN
L_00064c1c:
    mov.l P_00064dd0,r3
    .org 0x64c1e-ORIGIN
L_00064c1e:
    mov #0x0,r2
    .org 0x64c20-ORIGIN
L_00064c20:
    mov.w P_00064caa,r0
    .org 0x64c22-ORIGIN
L_00064c22:
    mov.b r2,@(r0,r3)
    .org 0x64c24-ORIGIN
L_00064c24:
    mov.w P_00064cae,r0
    .org 0x64c26-ORIGIN
L_00064c26:
    mov.w @(r0,r13),r7
    .org 0x64c28-ORIGIN
L_00064c28:
    cmp/eq r10,r7
    .org 0x64c2a-ORIGIN
L_00064c2a:
    bf L_00064c38
    .org 0x64c2c-ORIGIN
L_00064c2c:
    mov.l P_00064dd0,r3
    .org 0x64c2e-ORIGIN
L_00064c2e:
    mov #-0x1,r2
    .org 0x64c30-ORIGIN
L_00064c30:
    mov.w P_00064cb0,r0
    .org 0x64c32-ORIGIN
L_00064c32:
    mov.b r2,@(r0,r3)
    .org 0x64c34-ORIGIN
L_00064c34:
    bra L_00064c90
    .org 0x64c36-ORIGIN
L_00064c36:
    nop
    .org 0x64c38-ORIGIN
L_00064c38:
    mov.l P_00064dd0,r3
    .org 0x64c3a-ORIGIN
L_00064c3a:
    mov r7,r2
    .org 0x64c3c-ORIGIN
L_00064c3c:
    mov.w P_00064cac,r0
    .org 0x64c3e-ORIGIN
L_00064c3e:
    add r9,r2
    .org 0x64c40-ORIGIN
L_00064c40:
    mov r9,r5
    .org 0x64c42-ORIGIN
L_00064c42:
    mov r8,r4
    .org 0x64c44-ORIGIN
L_00064c44:
    mov.w @(r0,r3),r6
    .org 0x64c46-ORIGIN
L_00064c46:
    exts.w r11,r0
    .org 0x64c48-ORIGIN
L_00064c48:
    tst r0,r0
    .org 0x64c4a-ORIGIN
L_00064c4a:
    extu.w r6,r6
    .org 0x64c4c-ORIGIN
L_00064c4c:
    add r6,r2
    .org 0x64c4e-ORIGIN
L_00064c4e:
    bt/s L_00064c78
    .org 0x64c50-ORIGIN
L_00064c50:
    add r8,r2
    .org 0x64c52-ORIGIN
L_00064c52:
    mov r2,r6
    .org 0x64c54-ORIGIN
L_00064c54:
    mov.l P_00064dd8,r2
    .org 0x64c56-ORIGIN
L_00064c56:
    shll8 r6
    .org 0x64c58-ORIGIN
L_00064c58:
    jsr @r2
    .org 0x64c5a-ORIGIN
L_00064c5a:
    mov r6,r1
    .org 0x64c5c-ORIGIN
L_00064c5c:
    cmp/pz r0
    .org 0x64c5e-ORIGIN
L_00064c5e:
    bt/s L_00064c64
    .org 0x64c60-ORIGIN
L_00064c60:
    mov r0,r6
    .org 0x64c62-ORIGIN
L_00064c62:
    mov #0x0,r6
    .org 0x64c64-ORIGIN
L_00064c64:
    mov #-0x1,r5
    .org 0x64c66-ORIGIN
L_00064c66:
    extu.b r5,r2
    .org 0x64c68-ORIGIN
L_00064c68:
    cmp/gt r2,r6
    .org 0x64c6a-ORIGIN
L_00064c6a:
    bt L_00064c6e
    .org 0x64c6c-ORIGIN
L_00064c6c:
    mov r6,r2
    .org 0x64c6e-ORIGIN
L_00064c6e:
    mov.l P_00064dd0,r3
    .org 0x64c70-ORIGIN
L_00064c70:
    mov.w P_00064cb0,r0
    .org 0x64c72-ORIGIN
L_00064c72:
    mov.b r2,@(r0,r3)
    .org 0x64c74-ORIGIN
L_00064c74:
    bra L_00064c90
    .org 0x64c76-ORIGIN
L_00064c76:
    nop
    .org 0x64c78-ORIGIN
L_00064c78:
    cmp/pl r2
    .org 0x64c7a-ORIGIN
L_00064c7a:
    bf L_00064c88
    .org 0x64c7c-ORIGIN
L_00064c7c:
    mov.l P_00064dd0,r3
    .org 0x64c7e-ORIGIN
L_00064c7e:
    mov #-0x1,r2
    .org 0x64c80-ORIGIN
L_00064c80:
    mov.w P_00064cb0,r0
    .org 0x64c82-ORIGIN
L_00064c82:
    mov.b r2,@(r0,r3)
    .org 0x64c84-ORIGIN
L_00064c84:
    bra L_00064c90
    .org 0x64c86-ORIGIN
L_00064c86:
    nop
    .org 0x64c88-ORIGIN
L_00064c88:
    mov.l P_00064dd0,r3
    .org 0x64c8a-ORIGIN
L_00064c8a:
    mov #0x0,r2
    .org 0x64c8c-ORIGIN
L_00064c8c:
    mov.w P_00064cb0,r0
    .org 0x64c8e-ORIGIN
L_00064c8e:
    mov.b r2,@(r0,r3)
    .org 0x64c90-ORIGIN
L_00064c90:
    lds.l @r15+,macl
    .org 0x64c92-ORIGIN
L_00064c92:
    lds.l @r15+,pr
    .org 0x64c94-ORIGIN
L_00064c94:
    mov.l @r15+,r14
    .org 0x64c96-ORIGIN
L_00064c96:
    mov.l @r15+,r13
    .org 0x64c98-ORIGIN
L_00064c98:
    mov.l @r15+,r12
    .org 0x64c9a-ORIGIN
L_00064c9a:
    mov.l @r15+,r11
    .org 0x64c9c-ORIGIN
L_00064c9c:
    mov.l @r15+,r10
    .org 0x64c9e-ORIGIN
L_00064c9e:
    mov.l @r15+,r9
    .org 0x64ca0-ORIGIN
L_00064ca0:
    rts
    .org 0x64ca2-ORIGIN
L_00064ca2:
    mov.l @r15+,r8
    .org 0x64ca4-ORIGIN
P_00064ca4:
    .byte 0x04
    .org 0x64ca5-ORIGIN
P_00064ca5:
    .byte 0x17
    .org 0x64ca6-ORIGIN
P_00064ca6:
    .byte 0x0b
    .org 0x64ca7-ORIGIN
P_00064ca7:
    .byte 0xde
    .org 0x64ca8-ORIGIN
P_00064ca8:
    .byte 0x07
    .org 0x64ca9-ORIGIN
P_00064ca9:
    .byte 0x40
    .org 0x64caa-ORIGIN
P_00064caa:
    .byte 0x05
    .org 0x64cab-ORIGIN
P_00064cab:
    .byte 0xe0
    .org 0x64cac-ORIGIN
P_00064cac:
    .byte 0x02
    .org 0x64cad-ORIGIN
P_00064cad:
    .byte 0x56
    .org 0x64cae-ORIGIN
P_00064cae:
    .byte 0x0b
    .org 0x64caf-ORIGIN
P_00064caf:
    .byte 0xc0
    .org 0x64cb0-ORIGIN
P_00064cb0:
    .byte 0x05
    .org 0x64cb1-ORIGIN
P_00064cb1:
    .byte 0xd8
    .org 0x64dcc-ORIGIN
P_00064dcc:
    .byte 0x00
    .org 0x64dcd-ORIGIN
P_00064dcd:
    .byte 0x00
    .org 0x64dce-ORIGIN
P_00064dce:
    .byte 0x8b
    .org 0x64dcf-ORIGIN
P_00064dcf:
    .byte 0x38
    .org 0x64dd0-ORIGIN
P_00064dd0:
    .byte 0xff
    .org 0x64dd1-ORIGIN
P_00064dd1:
    .byte 0xff
    .org 0x64dd2-ORIGIN
P_00064dd2:
    .byte 0x12
    .org 0x64dd3-ORIGIN
P_00064dd3:
    .byte 0x8c
    .org 0x64dd4-ORIGIN
P_00064dd4:
    .byte 0xff
    .org 0x64dd5-ORIGIN
P_00064dd5:
    .byte 0xff
    .org 0x64dd6-ORIGIN
P_00064dd6:
    .byte 0x28
    .org 0x64dd7-ORIGIN
P_00064dd7:
    .byte 0xf8
    .org 0x64dd8-ORIGIN
P_00064dd8:
    .byte 0x00
    .org 0x64dd9-ORIGIN
P_00064dd9:
    .byte 0x02
    .org 0x64dda-ORIGIN
P_00064dda:
    .byte 0x1b
    .org 0x64ddb-ORIGIN
P_00064ddb:
    .byte 0xbc
    .org 0x658a4-ORIGIN
L_000658a4:
    mov.l r14,@-r15
    .org 0x658a6-ORIGIN
L_000658a6:
    sts.l pr,@-r15
    .org 0x658a8-ORIGIN
L_000658a8:
    sts.l macl,@-r15
    .org 0x658aa-ORIGIN
L_000658aa:
    mov.l P_00065aa0,r6
    .org 0x658ac-ORIGIN
L_000658ac:
    mov #0x20,r0
    .org 0x658ae-ORIGIN
L_000658ae:
    mov.l P_00065aa4,r4
    .org 0x658b0-ORIGIN
L_000658b0:
    mov.w @(r0,r6),r7
    .org 0x658b2-ORIGIN
L_000658b2:
    mov.l P_00065aa8,r5
    .org 0x658b4-ORIGIN
L_000658b4:
    mov.l P_00065aac,r2
    .org 0x658b6-ORIGIN
L_000658b6:
    mov.l P_00065ab0,r14
    .org 0x658b8-ORIGIN
L_000658b8:
    jsr @r2
    .org 0x658ba-ORIGIN
L_000658ba:
    extu.w r7,r6
    .org 0x658bc-ORIGIN
L_000658bc:
    mov r0,r6
    .org 0x658be-ORIGIN
L_000658be:
    mov.w P_000659a6,r0
    .org 0x658c0-ORIGIN
L_000658c0:
    mov.l P_00065ab4,r5
    .org 0x658c2-ORIGIN
L_000658c2:
    mov.w r6,@(r0,r14)
    .org 0x658c4-ORIGIN
L_000658c4:
    mov.b @r5,r0
    .org 0x658c6-ORIGIN
L_000658c6:
    tst #0x80,r0
    .org 0x658c8-ORIGIN
L_000658c8:
    bt L_000658d2
    .org 0x658ca-ORIGIN
L_000658ca:
    mov.l P_00065ab8,r5
    .org 0x658cc-ORIGIN
L_000658cc:
    mov.b @(0x7,r5),r0
    .org 0x658ce-ORIGIN
L_000658ce:
    bra L_000658fc
    .org 0x658d0-ORIGIN
L_000658d0:
    mov r0,r5
    .org 0x658d2-ORIGIN
L_000658d2:
    mov.l P_00065abc,r5
    .org 0x658d4-ORIGIN
L_000658d4:
    mov #0x1,r2
    .org 0x658d6-ORIGIN
L_000658d6:
    shll8 r2
    .org 0x658d8-ORIGIN
L_000658d8:
    mov.l P_00065ac0,r7
    .org 0x658da-ORIGIN
L_000658da:
    mov.b @r5,r4
    .org 0x658dc-ORIGIN
L_000658dc:
    mov.l P_00065ab8,r5
    .org 0x658de-ORIGIN
L_000658de:
    extu.b r4,r4
    .org 0x658e0-ORIGIN
L_000658e0:
    mov.b @(0x7,r5),r0
    .org 0x658e2-ORIGIN
L_000658e2:
    sub r4,r2
    .org 0x658e4-ORIGIN
L_000658e4:
    extu.b r0,r5
    .org 0x658e6-ORIGIN
L_000658e6:
    mov #-0x8,r0
    .org 0x658e8-ORIGIN
L_000658e8:
    mulu.w r2,r5
    .org 0x658ea-ORIGIN
L_000658ea:
    extu.b r0,r0
    .org 0x658ec-ORIGIN
L_000658ec:
    mov.b @(r0,r7),r2
    .org 0x658ee-ORIGIN
L_000658ee:
    sts macl,r5
    .org 0x658f0-ORIGIN
L_000658f0:
    extu.b r2,r7
    .org 0x658f2-ORIGIN
L_000658f2:
    mulu.w r4,r7
    .org 0x658f4-ORIGIN
L_000658f4:
    sts macl,r2
    .org 0x658f6-ORIGIN
L_000658f6:
    add r2,r5
    .org 0x658f8-ORIGIN
L_000658f8:
    extu.w r5,r5
    .org 0x658fa-ORIGIN
L_000658fa:
    shlr8 r5
    .org 0x658fc-ORIGIN
L_000658fc:
    mov.l P_00065ac4,r4
    .org 0x658fe-ORIGIN
L_000658fe:
    extu.b r5,r5
    .org 0x65900-ORIGIN
L_00065900:
    extu.w r6,r6
    .org 0x65902-ORIGIN
L_00065902:
    mov.b @r4,r2
    .org 0x65904-ORIGIN
L_00065904:
    extu.b r2,r4
    .org 0x65906-ORIGIN
L_00065906:
    sub r5,r4
    .org 0x65908-ORIGIN
L_00065908:
    mul.l r4,r6
    .org 0x6590a-ORIGIN
L_0006590a:
    sts macl,r2
    .org 0x6590c-ORIGIN
L_0006590c:
    cmp/pz r2
    .org 0x6590e-ORIGIN
L_0006590e:
    bt L_00065912
    .org 0x65910-ORIGIN
L_00065910:
    mov #0x0,r2
    .org 0x65912-ORIGIN
L_00065912:
    mov r2,r6
    .org 0x65914-ORIGIN
L_00065914:
    shlr8 r6
    .org 0x65916-ORIGIN
L_00065916:
    swap.w r6,r2
    .org 0x65918-ORIGIN
L_00065918:
    mov.w P_000659a8,r0
    .org 0x6591a-ORIGIN
L_0006591a:
    exts.b r2,r6
    .org 0x6591c-ORIGIN
L_0006591c:
    xtrct r6,r2
    .org 0x6591e-ORIGIN
L_0006591e:
    mov.w r2,@(r0,r14)
    .org 0x65920-ORIGIN
L_00065920:
    lds.l @r15+,macl
    .org 0x65922-ORIGIN
L_00065922:
    lds.l @r15+,pr
    .org 0x65924-ORIGIN
L_00065924:
    rts
    .org 0x65926-ORIGIN
L_00065926:
    mov.l @r15+,r14
    .org 0x659a6-ORIGIN
P_000659a6:
    .byte 0x02
    .org 0x659a7-ORIGIN
P_000659a7:
    .byte 0x58
    .org 0x659a8-ORIGIN
P_000659a8:
    .byte 0x02
    .org 0x659a9-ORIGIN
P_000659a9:
    .byte 0x56
    .org 0x65aa0-ORIGIN
P_00065aa0:
    .byte 0xff
    .org 0x65aa1-ORIGIN
P_00065aa1:
    .byte 0xff
    .org 0x65aa2-ORIGIN
P_00065aa2:
    .byte 0x11
    .org 0x65aa3-ORIGIN
P_00065aa3:
    .byte 0x9c
    .org 0x65aa4-ORIGIN
P_00065aa4:
    .byte 0x00
    .org 0x65aa5-ORIGIN
P_00065aa5:
    .byte 0x01
    .org 0x65aa6-ORIGIN
P_00065aa6:
    .byte 0x4c
    .org 0x65aa7-ORIGIN
P_00065aa7:
    .byte 0x1a
    .org 0x65aa8-ORIGIN
P_00065aa8:
    .byte 0x00
    .org 0x65aa9-ORIGIN
P_00065aa9:
    .byte 0x01
    .org 0x65aaa-ORIGIN
P_00065aaa:
    .byte 0x4a
    .org 0x65aab-ORIGIN
P_00065aab:
    .byte 0xba
    .org 0x65aac-ORIGIN
P_00065aac:
    .byte 0x00
    .org 0x65aad-ORIGIN
P_00065aad:
    .byte 0x02
    .org 0x65aae-ORIGIN
P_00065aae:
    .byte 0x64
    .org 0x65aaf-ORIGIN
P_00065aaf:
    .byte 0xcc
    .org 0x65ab0-ORIGIN
P_00065ab0:
    .byte 0xff
    .org 0x65ab1-ORIGIN
P_00065ab1:
    .byte 0xff
    .org 0x65ab2-ORIGIN
P_00065ab2:
    .byte 0x12
    .org 0x65ab3-ORIGIN
P_00065ab3:
    .byte 0x8c
    .org 0x65ab4-ORIGIN
P_00065ab4:
    .byte 0xff
    .org 0x65ab5-ORIGIN
P_00065ab5:
    .byte 0xff
    .org 0x65ab6-ORIGIN
P_00065ab6:
    .byte 0x41
    .org 0x65ab7-ORIGIN
P_00065ab7:
    .byte 0x81
    .org 0x65ab8-ORIGIN
P_00065ab8:
    .byte 0xff
    .org 0x65ab9-ORIGIN
P_00065ab9:
    .byte 0xff
    .org 0x65aba-ORIGIN
P_00065aba:
    .byte 0x10
    .org 0x65abb-ORIGIN
P_00065abb:
    .byte 0x6a
    .org 0x65abc-ORIGIN
P_00065abc:
    .byte 0x00
    .org 0x65abd-ORIGIN
P_00065abd:
    .byte 0x00
    .org 0x65abe-ORIGIN
P_00065abe:
    .byte 0x86
    .org 0x65abf-ORIGIN
P_00065abf:
    .byte 0x39
    .org 0x65ac0-ORIGIN
P_00065ac0:
    .byte 0xff
    .org 0x65ac1-ORIGIN
P_00065ac1:
    .byte 0xff
    .org 0x65ac2-ORIGIN
P_00065ac2:
    .byte 0x26
    .org 0x65ac3-ORIGIN
P_00065ac3:
    .byte 0x7a
    .org 0x65ac4-ORIGIN
P_00065ac4:
    .byte 0x00
    .org 0x65ac5-ORIGIN
P_00065ac5:
    .byte 0x00
    .org 0x65ac6-ORIGIN
P_00065ac6:
    .byte 0x8e
    .org 0x65ac7-ORIGIN
P_00065ac7:
    .byte 0x51
