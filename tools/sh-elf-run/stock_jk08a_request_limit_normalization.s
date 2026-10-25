! Complete stock endpoint normalization, real live limits and alternate publication.
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
    .org 0x264f8-ORIGIN
L_000264f8:
    sts.l pr,@-r15
    .org 0x264fa-ORIGIN
L_000264fa:
    mov.l r4,@-r15
    .org 0x264fc-ORIGIN
L_000264fc:
    mov r5,r0
    .org 0x264fe-ORIGIN
L_000264fe:
    extu.w r6,r5
    .org 0x26500-ORIGIN
L_00026500:
    mov.l P_00026520,r7
    .org 0x26502-ORIGIN
L_00026502:
    jsr @r7
    .org 0x26504-ORIGIN
L_00026504:
    mov #0x1e,r4
    .org 0x26506-ORIGIN
L_00026506:
    mov.l @r15+,r6
    .org 0x26508-ORIGIN
L_00026508:
    add r4,r6
    .org 0x2650a-ORIGIN
L_0002650a:
    mov.w @(0x2,r6),r0
    .org 0x2650c-ORIGIN
L_0002650c:
    extu.w r0,r2
    .org 0x2650e-ORIGIN
L_0002650e:
    mov r5,r3
    .org 0x26510-ORIGIN
L_00026510:
    mov.w @r6,r1
    .org 0x26512-ORIGIN
L_00026512:
    lds.l @r15+,pr
    .org 0x26514-ORIGIN
L_00026514:
    mov.l P_0002651c,r6
    .org 0x26516-ORIGIN
L_00026516:
    jmp @r6
    .org 0x26518-ORIGIN
L_00026518:
    extu.w r1,r0
    .org 0x2651c-ORIGIN
P_0002651c:
    .byte 0x00
    .org 0x2651d-ORIGIN
P_0002651d:
    .byte 0x02
    .org 0x2651e-ORIGIN
P_0002651e:
    .byte 0x67
    .org 0x2651f-ORIGIN
P_0002651f:
    .byte 0x40
    .org 0x26520-ORIGIN
P_00026520:
    .byte 0x00
    .org 0x26521-ORIGIN
P_00026521:
    .byte 0x02
    .org 0x26522-ORIGIN
P_00026522:
    .byte 0x69
    .org 0x26523-ORIGIN
P_00026523:
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
    .org 0x7ae80-ORIGIN
L_0007ae80:
    mov.l r9,@-r15
    .org 0x7ae82-ORIGIN
L_0007ae82:
    mov.l r10,@-r15
    .org 0x7ae84-ORIGIN
L_0007ae84:
    mov.l r11,@-r15
    .org 0x7ae86-ORIGIN
L_0007ae86:
    mov.l r12,@-r15
    .org 0x7ae88-ORIGIN
L_0007ae88:
    mov.l r13,@-r15
    .org 0x7ae8a-ORIGIN
L_0007ae8a:
    mov.l r14,@-r15
    .org 0x7ae8c-ORIGIN
L_0007ae8c:
    sts.l pr,@-r15
    .org 0x7ae8e-ORIGIN
L_0007ae8e:
    stc.l gbr,@-r15
    .org 0x7ae90-ORIGIN
L_0007ae90:
    mov.l P_0007b064,r0
    .org 0x7ae92-ORIGIN
L_0007ae92:
    ldc r0,gbr
    .org 0x7ae94-ORIGIN
L_0007ae94:
    bsr L_0007af78
    .org 0x7ae96-ORIGIN
L_0007ae96:
    nop
    .org 0x7ae98-ORIGIN
L_0007ae98:
    mov.w @(0x182,gbr),r0
    .org 0x7ae9a-ORIGIN
L_0007ae9a:
    mov.l P_0007b064,r9
    .org 0x7ae9c-ORIGIN
L_0007ae9c:
    extu.w r0,r7
    .org 0x7ae9e-ORIGIN
L_0007ae9e:
    mov.w P_0007af6e,r0
    .org 0x7aea0-ORIGIN
L_0007aea0:
    mov.l P_0007b068,r11
    .org 0x7aea2-ORIGIN
L_0007aea2:
    mov.w @(r0,r9),r6
    .org 0x7aea4-ORIGIN
L_0007aea4:
    mov #0x52,r0
    .org 0x7aea6-ORIGIN
L_0007aea6:
    mov.l P_0007b06c,r10
    .org 0x7aea8-ORIGIN
L_0007aea8:
    extu.w r6,r4
    .org 0x7aeaa-ORIGIN
L_0007aeaa:
    mov.b @(r0,r11),r14
    .org 0x7aeac-ORIGIN
L_0007aeac:
    mov.b @(0x3,r10),r0
    .org 0x7aeae-ORIGIN
L_0007aeae:
    cmp/ge r4,r7
    .org 0x7aeb0-ORIGIN
L_0007aeb0:
    bf/s L_0007aeb6
    .org 0x7aeb2-ORIGIN
L_0007aeb2:
    mov r0,r13
    .org 0x7aeb4-ORIGIN
L_0007aeb4:
    mov r7,r4
    .org 0x7aeb6-ORIGIN
L_0007aeb6:
    mov.w P_0007af70,r0
    .org 0x7aeb8-ORIGIN
L_0007aeb8:
    extu.w r4,r4
    .org 0x7aeba-ORIGIN
L_0007aeba:
    mov.w @(r0,r9),r5
    .org 0x7aebc-ORIGIN
L_0007aebc:
    extu.w r5,r5
    .org 0x7aebe-ORIGIN
L_0007aebe:
    cmp/ge r5,r4
    .org 0x7aec0-ORIGIN
L_0007aec0:
    bt L_0007aec4
    .org 0x7aec2-ORIGIN
L_0007aec2:
    mov r5,r4
    .org 0x7aec4-ORIGIN
L_0007aec4:
    mov.w P_0007af72,r0
    .org 0x7aec6-ORIGIN
L_0007aec6:
    extu.w r4,r4
    .org 0x7aec8-ORIGIN
L_0007aec8:
    mov.w @(r0,r9),r5
    .org 0x7aeca-ORIGIN
L_0007aeca:
    extu.w r5,r2
    .org 0x7aecc-ORIGIN
L_0007aecc:
    cmp/gt r2,r4
    .org 0x7aece-ORIGIN
L_0007aece:
    bt L_0007aed2
    .org 0x7aed0-ORIGIN
L_0007aed0:
    mov r4,r2
    .org 0x7aed2-ORIGIN
L_0007aed2:
    mov #0x4a,r0
    .org 0x7aed4-ORIGIN
L_0007aed4:
    mov r2,r12
    .org 0x7aed6-ORIGIN
L_0007aed6:
    mov.b @(r0,r11),r0
    .org 0x7aed8-ORIGIN
L_0007aed8:
    and #0x1,r0
    .org 0x7aeda-ORIGIN
L_0007aeda:
    tst r0,r0
    .org 0x7aedc-ORIGIN
L_0007aedc:
    bt/s L_0007aee6
    .org 0x7aede-ORIGIN
L_0007aede:
    mov r0,r6
    .org 0x7aee0-ORIGIN
L_0007aee0:
    mov.w P_0007af74,r0
    .org 0x7aee2-ORIGIN
L_0007aee2:
    bra L_0007aee8
    .org 0x7aee4-ORIGIN
L_0007aee4:
    mov.w @(r0,r9),r4
    .org 0x7aee6-ORIGIN
L_0007aee6:
    mov r12,r4
    .org 0x7aee8-ORIGIN
L_0007aee8:
    extu.w r4,r4
    .org 0x7aeea-ORIGIN
L_0007aeea:
    mov r14,r0
    .org 0x7aeec-ORIGIN
L_0007aeec:
    cmp/pl r4
    .org 0x7aeee-ORIGIN
L_0007aeee:
    bt/s L_0007aef4
    .org 0x7aef0-ORIGIN
L_0007aef0:
    and #0xef,r0
    .org 0x7aef2-ORIGIN
L_0007aef2:
    or #0x10,r0
    .org 0x7aef4-ORIGIN
L_0007aef4:
    mov r0,r14
    .org 0x7aef6-ORIGIN
L_0007aef6:
    mov #0x52,r0
    .org 0x7aef8-ORIGIN
L_0007aef8:
    mov.b r14,@(r0,r11)
    .org 0x7aefa-ORIGIN
L_0007aefa:
    mov.w P_0007af76,r14
    .org 0x7aefc-ORIGIN
L_0007aefc:
    mov.b @(r0,r11),r0
    .org 0x7aefe-ORIGIN
L_0007aefe:
    cmp/ge r14,r4
    .org 0x7af00-ORIGIN
L_0007af00:
    bf/s L_0007af06
    .org 0x7af02-ORIGIN
L_0007af02:
    and #0xdf,r0
    .org 0x7af04-ORIGIN
L_0007af04:
    or #0x20,r0
    .org 0x7af06-ORIGIN
L_0007af06:
    mov.l P_0007b070,r5
    .org 0x7af08-ORIGIN
L_0007af08:
    mov r0,r2
    .org 0x7af0a-ORIGIN
L_0007af0a:
    mov #0x52,r0
    .org 0x7af0c-ORIGIN
L_0007af0c:
    mov.b r2,@(r0,r11)
    .org 0x7af0e-ORIGIN
L_0007af0e:
    mov.b @r5,r0
    .org 0x7af10-ORIGIN
L_0007af10:
    tst #0x2,r0
    .org 0x7af12-ORIGIN
L_0007af12:
    bt L_0007af2c
    .org 0x7af14-ORIGIN
L_0007af14:
    extu.w r12,r12
    .org 0x7af16-ORIGIN
L_0007af16:
    cmp/eq r12,r7
    .org 0x7af18-ORIGIN
L_0007af18:
    bf L_0007af24
    .org 0x7af1a-ORIGIN
L_0007af1a:
    tst r6,r6
    .org 0x7af1c-ORIGIN
L_0007af1c:
    bf L_0007af24
    .org 0x7af1e-ORIGIN
L_0007af1e:
    mov r13,r0
    .org 0x7af20-ORIGIN
L_0007af20:
    bra L_0007af28
    .org 0x7af22-ORIGIN
L_0007af22:
    and #0xfe,r0
    .org 0x7af24-ORIGIN
L_0007af24:
    mov r13,r0
    .org 0x7af26-ORIGIN
L_0007af26:
    or #0x1,r0
    .org 0x7af28-ORIGIN
L_0007af28:
    bra L_0007af56
    .org 0x7af2a-ORIGIN
L_0007af2a:
    mov.b r0,@(0x3,r10)
    .org 0x7af2c-ORIGIN
L_0007af2c:
    mov.l P_0007b074,r6
    .org 0x7af2e-ORIGIN
L_0007af2e:
    mov #0x2b,r0
    .org 0x7af30-ORIGIN
L_0007af30:
    mov.b @(r0,r6),r0
    .org 0x7af32-ORIGIN
L_0007af32:
    tst #0x2,r0
    .org 0x7af34-ORIGIN
L_0007af34:
    mov r13,r0
    .org 0x7af36-ORIGIN
L_0007af36:
    bt/s L_0007af3c
    .org 0x7af38-ORIGIN
L_0007af38:
    and #0xfe,r0
    .org 0x7af3a-ORIGIN
L_0007af3a:
    or #0x1,r0
    .org 0x7af3c-ORIGIN
L_0007af3c:
    mov.l P_0007b078,r2
    .org 0x7af3e-ORIGIN
L_0007af3e:
    mov.b r0,@(0x3,r10)
    .org 0x7af40-ORIGIN
L_0007af40:
    mov.w @(0x1a,r2),r0
    .org 0x7af42-ORIGIN
L_0007af42:
    mov.l P_0007b07c,r2
    .org 0x7af44-ORIGIN
L_0007af44:
    extu.w r0,r4
    .org 0x7af46-ORIGIN
L_0007af46:
    mov #-0x68,r0
    .org 0x7af48-ORIGIN
L_0007af48:
    extu.b r0,r0
    .org 0x7af4a-ORIGIN
L_0007af4a:
    mov.w @(r0,r2),r5
    .org 0x7af4c-ORIGIN
L_0007af4c:
    extu.w r5,r2
    .org 0x7af4e-ORIGIN
L_0007af4e:
    cmp/ge r2,r4
    .org 0x7af50-ORIGIN
L_0007af50:
    bf L_0007af54
    .org 0x7af52-ORIGIN
L_0007af52:
    mov r4,r2
    .org 0x7af54-ORIGIN
L_0007af54:
    mov r2,r4
    .org 0x7af56-ORIGIN
L_0007af56:
    mov.l P_0007b080,r6
    .org 0x7af58-ORIGIN
L_0007af58:
    mov r4,r0
    .org 0x7af5a-ORIGIN
L_0007af5a:
    mov.w r0,@(0x6,r6)
    .org 0x7af5c-ORIGIN
L_0007af5c:
    ldc.l @r15+,gbr
    .org 0x7af5e-ORIGIN
L_0007af5e:
    lds.l @r15+,pr
    .org 0x7af60-ORIGIN
L_0007af60:
    mov.l @r15+,r14
    .org 0x7af62-ORIGIN
L_0007af62:
    mov.l @r15+,r13
    .org 0x7af64-ORIGIN
L_0007af64:
    mov.l @r15+,r12
    .org 0x7af66-ORIGIN
L_0007af66:
    mov.l @r15+,r11
    .org 0x7af68-ORIGIN
L_0007af68:
    mov.l @r15+,r10
    .org 0x7af6a-ORIGIN
L_0007af6a:
    rts
    .org 0x7af6c-ORIGIN
L_0007af6c:
    mov.l @r15+,r9
    .org 0x7af6e-ORIGIN
P_0007af6e:
    .byte 0x0b
    .org 0x7af6f-ORIGIN
P_0007af6f:
    .byte 0x80
    .org 0x7af70-ORIGIN
P_0007af70:
    .byte 0x0b
    .org 0x7af71-ORIGIN
P_0007af71:
    .byte 0x82
    .org 0x7af72-ORIGIN
P_0007af72:
    .byte 0x0b
    .org 0x7af73-ORIGIN
P_0007af73:
    .byte 0x84
    .org 0x7af74-ORIGIN
P_0007af74:
    .byte 0x07
    .org 0x7af75-ORIGIN
P_0007af75:
    .byte 0x2e
    .org 0x7af76-ORIGIN
P_0007af76:
    .byte 0x03
    .org 0x7af77-ORIGIN
P_0007af77:
    .byte 0x20
    .org 0x7af78-ORIGIN
L_0007af78:
    mov.l r10,@-r15
    .org 0x7af7a-ORIGIN
L_0007af7a:
    mov.l r11,@-r15
    .org 0x7af7c-ORIGIN
L_0007af7c:
    mov.l r12,@-r15
    .org 0x7af7e-ORIGIN
L_0007af7e:
    mov.l r13,@-r15
    .org 0x7af80-ORIGIN
L_0007af80:
    mov.l r14,@-r15
    .org 0x7af82-ORIGIN
L_0007af82:
    sts.l pr,@-r15
    .org 0x7af84-ORIGIN
L_0007af84:
    sts.l macl,@-r15
    .org 0x7af86-ORIGIN
L_0007af86:
    add #-0x4,r15
    .org 0x7af88-ORIGIN
L_0007af88:
    mov.l P_0007b084,r13
    .org 0x7af8a-ORIGIN
L_0007af8a:
    mov #0x28,r0
    .org 0x7af8c-ORIGIN
L_0007af8c:
    mov.l P_0007b088,r4
    .org 0x7af8e-ORIGIN
L_0007af8e:
    mov.w @(r0,r13),r7
    .org 0x7af90-ORIGIN
L_0007af90:
    mov.l P_0007b08c,r14
    .org 0x7af92-ORIGIN
L_0007af92:
    mov.l P_0007b090,r2
    .org 0x7af94-ORIGIN
L_0007af94:
    extu.w r7,r6
    .org 0x7af96-ORIGIN
L_0007af96:
    mov.l P_0007b064,r10
    .org 0x7af98-ORIGIN
L_0007af98:
    jsr @r2
    .org 0x7af9a-ORIGIN
L_0007af9a:
    mov r14,r5
    .org 0x7af9c-ORIGIN
L_0007af9c:
    mov.w r0,@r15
    .org 0x7af9e-ORIGIN
L_0007af9e:
    mov #0x28,r0
    .org 0x7afa0-ORIGIN
L_0007afa0:
    mov.w @(r0,r13),r7
    .org 0x7afa2-ORIGIN
L_0007afa2:
    mov r14,r5
    .org 0x7afa4-ORIGIN
L_0007afa4:
    mov.l P_0007b094,r4
    .org 0x7afa6-ORIGIN
L_0007afa6:
    mov.l P_0007b090,r2
    .org 0x7afa8-ORIGIN
L_0007afa8:
    mov.l P_0007b098,r14
    .org 0x7afaa-ORIGIN
L_0007afaa:
    jsr @r2
    .org 0x7afac-ORIGIN
L_0007afac:
    extu.w r7,r6
    .org 0x7afae-ORIGIN
L_0007afae:
    mov r0,r2
    .org 0x7afb0-ORIGIN
L_0007afb0:
    mov.w P_0007b054,r0
    .org 0x7afb2-ORIGIN
L_0007afb2:
    mov.w @r15,r7
    .org 0x7afb4-ORIGIN
L_0007afb4:
    mov.w @(r0,r10),r5
    .org 0x7afb6-ORIGIN
L_0007afb6:
    extu.w r7,r7
    .org 0x7afb8-ORIGIN
L_0007afb8:
    sub r7,r5
    .org 0x7afba-ORIGIN
L_0007afba:
    add r14,r5
    .org 0x7afbc-ORIGIN
L_0007afbc:
    cmp/pz r5
    .org 0x7afbe-ORIGIN
L_0007afbe:
    bt L_0007afc2
    .org 0x7afc0-ORIGIN
L_0007afc0:
    mov #0x0,r5
    .org 0x7afc2-ORIGIN
L_0007afc2:
    mov.w P_0007b056,r0
    .org 0x7afc4-ORIGIN
L_0007afc4:
    mov r5,r4
    .org 0x7afc6-ORIGIN
L_0007afc6:
    mov.w @(r0,r10),r5
    .org 0x7afc8-ORIGIN
L_0007afc8:
    sub r7,r5
    .org 0x7afca-ORIGIN
L_0007afca:
    add r14,r5
    .org 0x7afcc-ORIGIN
L_0007afcc:
    cmp/pz r5
    .org 0x7afce-ORIGIN
L_0007afce:
    bt L_0007afd2
    .org 0x7afd0-ORIGIN
L_0007afd0:
    mov #0x0,r5
    .org 0x7afd2-ORIGIN
L_0007afd2:
    mov.w P_0007b058,r0
    .org 0x7afd4-ORIGIN
L_0007afd4:
    mov r5,r12
    .org 0x7afd6-ORIGIN
L_0007afd6:
    mov.w @(r0,r10),r5
    .org 0x7afd8-ORIGIN
L_0007afd8:
    sub r7,r5
    .org 0x7afda-ORIGIN
L_0007afda:
    add r14,r5
    .org 0x7afdc-ORIGIN
L_0007afdc:
    cmp/pz r5
    .org 0x7afde-ORIGIN
L_0007afde:
    bt L_0007afe2
    .org 0x7afe0-ORIGIN
L_0007afe0:
    mov #0x0,r5
    .org 0x7afe2-ORIGIN
L_0007afe2:
    extu.w r2,r14
    .org 0x7afe4-ORIGIN
L_0007afe4:
    sub r7,r14
    .org 0x7afe6-ORIGIN
L_0007afe6:
    cmp/pz r14
    .org 0x7afe8-ORIGIN
L_0007afe8:
    bt/s L_0007afee
    .org 0x7afea-ORIGIN
L_0007afea:
    mov r5,r11
    .org 0x7afec-ORIGIN
L_0007afec:
    mov #0x0,r14
    .org 0x7afee-ORIGIN
L_0007afee:
    tst r14,r14
    .org 0x7aff0-ORIGIN
L_0007aff0:
    bt L_0007b034
    .org 0x7aff2-ORIGIN
L_0007aff2:
    mov.w P_0007b05a,r13
    .org 0x7aff4-ORIGIN
L_0007aff4:
    mov r14,r0
    .org 0x7aff6-ORIGIN
L_0007aff6:
    mov.l P_0007b09c,r6
    .org 0x7aff8-ORIGIN
L_0007aff8:
    mul.l r4,r13
    .org 0x7affa-ORIGIN
L_0007affa:
    jsr @r6
    .org 0x7affc-ORIGIN
L_0007affc:
    sts macl,r1
    .org 0x7affe-ORIGIN
L_0007affe:
    cmp/gt r13,r0
    .org 0x7b000-ORIGIN
L_0007b000:
    bf/s L_0007b006
    .org 0x7b002-ORIGIN
L_0007b002:
    mov r0,r2
    .org 0x7b004-ORIGIN
L_0007b004:
    mov r13,r2
    .org 0x7b006-ORIGIN
L_0007b006:
    mul.l r12,r13
    .org 0x7b008-ORIGIN
L_0007b008:
    mov.w P_0007b05c,r0
    .org 0x7b00a-ORIGIN
L_0007b00a:
    mov.l P_0007b09c,r6
    .org 0x7b00c-ORIGIN
L_0007b00c:
    sts macl,r1
    .org 0x7b00e-ORIGIN
L_0007b00e:
    mov.w r2,@(r0,r10)
    .org 0x7b010-ORIGIN
L_0007b010:
    jsr @r6
    .org 0x7b012-ORIGIN
L_0007b012:
    mov r14,r0
    .org 0x7b014-ORIGIN
L_0007b014:
    cmp/gt r13,r0
    .org 0x7b016-ORIGIN
L_0007b016:
    bf/s L_0007b01c
    .org 0x7b018-ORIGIN
L_0007b018:
    mov r0,r2
    .org 0x7b01a-ORIGIN
L_0007b01a:
    mov r13,r2
    .org 0x7b01c-ORIGIN
L_0007b01c:
    mul.l r11,r13
    .org 0x7b01e-ORIGIN
L_0007b01e:
    mov.w P_0007b05e,r0
    .org 0x7b020-ORIGIN
L_0007b020:
    mov.l P_0007b09c,r6
    .org 0x7b022-ORIGIN
L_0007b022:
    sts macl,r1
    .org 0x7b024-ORIGIN
L_0007b024:
    mov.w r2,@(r0,r10)
    .org 0x7b026-ORIGIN
L_0007b026:
    jsr @r6
    .org 0x7b028-ORIGIN
L_0007b028:
    mov r14,r0
    .org 0x7b02a-ORIGIN
L_0007b02a:
    cmp/gt r13,r0
    .org 0x7b02c-ORIGIN
L_0007b02c:
    bf/s L_0007b03e
    .org 0x7b02e-ORIGIN
L_0007b02e:
    mov r0,r2
    .org 0x7b030-ORIGIN
L_0007b030:
    bra L_0007b03e
    .org 0x7b032-ORIGIN
L_0007b032:
    mov r13,r2
    .org 0x7b034-ORIGIN
L_0007b034:
    mov.w P_0007b05a,r2
    .org 0x7b036-ORIGIN
L_0007b036:
    mov.w P_0007b05c,r0
    .org 0x7b038-ORIGIN
L_0007b038:
    mov.w r2,@(r0,r10)
    .org 0x7b03a-ORIGIN
L_0007b03a:
    mov.w P_0007b05e,r0
    .org 0x7b03c-ORIGIN
L_0007b03c:
    mov.w r2,@(r0,r10)
    .org 0x7b03e-ORIGIN
L_0007b03e:
    mov.w P_0007b060,r0
    .org 0x7b040-ORIGIN
L_0007b040:
    mov.w r2,@(r0,r10)
    .org 0x7b042-ORIGIN
L_0007b042:
    add #0x4,r15
    .org 0x7b044-ORIGIN
L_0007b044:
    lds.l @r15+,macl
    .org 0x7b046-ORIGIN
L_0007b046:
    lds.l @r15+,pr
    .org 0x7b048-ORIGIN
L_0007b048:
    mov.l @r15+,r14
    .org 0x7b04a-ORIGIN
L_0007b04a:
    mov.l @r15+,r13
    .org 0x7b04c-ORIGIN
L_0007b04c:
    mov.l @r15+,r12
    .org 0x7b04e-ORIGIN
L_0007b04e:
    mov.l @r15+,r11
    .org 0x7b050-ORIGIN
L_0007b050:
    rts
    .org 0x7b052-ORIGIN
L_0007b052:
    mov.l @r15+,r10
    .org 0x7b054-ORIGIN
P_0007b054:
    .byte 0x0a
    .org 0x7b055-ORIGIN
P_0007b055:
    .byte 0x94
    .org 0x7b056-ORIGIN
P_0007b056:
    .byte 0x0a
    .org 0x7b057-ORIGIN
P_0007b057:
    .byte 0x96
    .org 0x7b058-ORIGIN
P_0007b058:
    .byte 0x0a
    .org 0x7b059-ORIGIN
P_0007b059:
    .byte 0x9e
    .org 0x7b05a-ORIGIN
P_0007b05a:
    .byte 0x03
    .org 0x7b05b-ORIGIN
P_0007b05b:
    .byte 0x20
    .org 0x7b05c-ORIGIN
P_0007b05c:
    .byte 0x0b
    .org 0x7b05d-ORIGIN
P_0007b05d:
    .byte 0x80
    .org 0x7b05e-ORIGIN
P_0007b05e:
    .byte 0x0b
    .org 0x7b05f-ORIGIN
P_0007b05f:
    .byte 0x82
    .org 0x7b060-ORIGIN
P_0007b060:
    .byte 0x0b
    .org 0x7b061-ORIGIN
P_0007b061:
    .byte 0x84
    .org 0x7b064-ORIGIN
P_0007b064:
    .byte 0xff
    .org 0x7b065-ORIGIN
P_0007b065:
    .byte 0xff
    .org 0x7b066-ORIGIN
P_0007b066:
    .byte 0x28
    .org 0x7b067-ORIGIN
P_0007b067:
    .byte 0xf8
    .org 0x7b068-ORIGIN
P_0007b068:
    .byte 0xff
    .org 0x7b069-ORIGIN
P_0007b069:
    .byte 0xff
    .org 0x7b06a-ORIGIN
P_0007b06a:
    .byte 0x41
    .org 0x7b06b-ORIGIN
P_0007b06b:
    .byte 0xa9
    .org 0x7b06c-ORIGIN
P_0007b06c:
    .byte 0xff
    .org 0x7b06d-ORIGIN
P_0007b06d:
    .byte 0xff
    .org 0x7b06e-ORIGIN
P_0007b06e:
    .byte 0x42
    .org 0x7b06f-ORIGIN
P_0007b06f:
    .byte 0x4c
    .org 0x7b070-ORIGIN
P_0007b070:
    .byte 0x00
    .org 0x7b071-ORIGIN
P_0007b071:
    .byte 0x00
    .org 0x7b072-ORIGIN
P_0007b072:
    .byte 0x83
    .org 0x7b073-ORIGIN
P_0007b073:
    .byte 0xc1
    .org 0x7b074-ORIGIN
P_0007b074:
    .byte 0xff
    .org 0x7b075-ORIGIN
P_0007b075:
    .byte 0xff
    .org 0x7b076-ORIGIN
P_0007b076:
    .byte 0x24
    .org 0x7b077-ORIGIN
P_0007b077:
    .byte 0x70
    .org 0x7b078-ORIGIN
P_0007b078:
    .byte 0xff
    .org 0x7b079-ORIGIN
P_0007b079:
    .byte 0xff
    .org 0x7b07a-ORIGIN
P_0007b07a:
    .byte 0x10
    .org 0x7b07b-ORIGIN
P_0007b07b:
    .byte 0x94
    .org 0x7b07c-ORIGIN
P_0007b07c:
    .byte 0xff
    .org 0x7b07d-ORIGIN
P_0007b07d:
    .byte 0xff
    .org 0x7b07e-ORIGIN
P_0007b07e:
    .byte 0x26
    .org 0x7b07f-ORIGIN
P_0007b07f:
    .byte 0x7a
    .org 0x7b080-ORIGIN
P_0007b080:
    .byte 0xff
    .org 0x7b081-ORIGIN
P_0007b081:
    .byte 0xff
    .org 0x7b082-ORIGIN
P_0007b082:
    .byte 0x41
    .org 0x7b083-ORIGIN
P_0007b083:
    .byte 0x24
    .org 0x7b084-ORIGIN
P_0007b084:
    .byte 0xff
    .org 0x7b085-ORIGIN
P_0007b085:
    .byte 0xff
    .org 0x7b086-ORIGIN
P_0007b086:
    .byte 0x11
    .org 0x7b087-ORIGIN
P_0007b087:
    .byte 0x14
    .org 0x7b088-ORIGIN
P_0007b088:
    .byte 0x00
    .org 0x7b089-ORIGIN
P_0007b089:
    .byte 0x01
    .org 0x7b08a-ORIGIN
P_0007b08a:
    .byte 0x54
    .org 0x7b08b-ORIGIN
P_0007b08b:
    .byte 0xe0
    .org 0x7b08c-ORIGIN
P_0007b08c:
    .byte 0x00
    .org 0x7b08d-ORIGIN
P_0007b08d:
    .byte 0x01
    .org 0x7b08e-ORIGIN
P_0007b08e:
    .byte 0x4b
    .org 0x7b08f-ORIGIN
P_0007b08f:
    .byte 0xaa
    .org 0x7b090-ORIGIN
P_0007b090:
    .byte 0x00
    .org 0x7b091-ORIGIN
P_0007b091:
    .byte 0x02
    .org 0x7b092-ORIGIN
P_0007b092:
    .byte 0x64
    .org 0x7b093-ORIGIN
P_0007b093:
    .byte 0xf8
    .org 0x7b094-ORIGIN
P_0007b094:
    .byte 0x00
    .org 0x7b095-ORIGIN
P_0007b095:
    .byte 0x01
    .org 0x7b096-ORIGIN
P_0007b096:
    .byte 0x54
    .org 0x7b097-ORIGIN
P_0007b097:
    .byte 0xc0
    .org 0x7b098-ORIGIN
P_0007b098:
    .byte 0x00
    .org 0x7b099-ORIGIN
P_0007b099:
    .byte 0x00
    .org 0x7b09a-ORIGIN
P_0007b09a:
    .byte 0x80
    .org 0x7b09b-ORIGIN
P_0007b09b:
    .byte 0x00
    .org 0x7b09c-ORIGIN
P_0007b09c:
    .byte 0x00
    .org 0x7b09d-ORIGIN
P_0007b09d:
    .byte 0x02
    .org 0x7b09e-ORIGIN
P_0007b09e:
    .byte 0x1b
    .org 0x7b09f-ORIGIN
P_0007b09f:
    .byte 0xbc
