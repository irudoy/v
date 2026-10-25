! Exact natural constant-root curve/scale caller with real unsigned interpolation and signed-division helpers.
    .text
    .balign 4
    .set ORIGIN,0x8540
    .org 0x8543-ORIGIN
P_00008543:
    .byte 0x00
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
    .org 0x26524-ORIGIN
L_00026524:
    sts.l pr,@-r15
    .org 0x26526-ORIGIN
L_00026526:
    mov.l r4,@-r15
    .org 0x26528-ORIGIN
L_00026528:
    mov r5,r0
    .org 0x2652a-ORIGIN
L_0002652a:
    extu.w r6,r5
    .org 0x2652c-ORIGIN
L_0002652c:
    mov.l P_0002654c,r7
    .org 0x2652e-ORIGIN
L_0002652e:
    jsr @r7
    .org 0x26530-ORIGIN
L_00026530:
    mov #0x3e,r4
    .org 0x26532-ORIGIN
L_00026532:
    mov.l @r15+,r6
    .org 0x26534-ORIGIN
L_00026534:
    add r4,r6
    .org 0x26536-ORIGIN
L_00026536:
    mov.w @(0x2,r6),r0
    .org 0x26538-ORIGIN
L_00026538:
    extu.w r0,r2
    .org 0x2653a-ORIGIN
L_0002653a:
    mov r5,r3
    .org 0x2653c-ORIGIN
L_0002653c:
    mov.w @r6,r1
    .org 0x2653e-ORIGIN
L_0002653e:
    lds.l @r15+,pr
    .org 0x26540-ORIGIN
L_00026540:
    mov.l P_00026548,r6
    .org 0x26542-ORIGIN
L_00026542:
    jmp @r6
    .org 0x26544-ORIGIN
L_00026544:
    extu.w r1,r0
    .org 0x26548-ORIGIN
P_00026548:
    .byte 0x00
    .org 0x26549-ORIGIN
P_00026549:
    .byte 0x02
    .org 0x2654a-ORIGIN
P_0002654a:
    .byte 0x67
    .org 0x2654b-ORIGIN
P_0002654b:
    .byte 0x40
    .org 0x2654c-ORIGIN
P_0002654c:
    .byte 0x00
    .org 0x2654d-ORIGIN
P_0002654d:
    .byte 0x02
    .org 0x2654e-ORIGIN
P_0002654e:
    .byte 0x69
    .org 0x2654f-ORIGIN
P_0002654f:
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
    .org 0xb7768-ORIGIN
L_000b7768:
    mov.l r14,@-r15
    .org 0xb776a-ORIGIN
L_000b776a:
    sts.l pr,@-r15
    .org 0xb776c-ORIGIN
L_000b776c:
    sts.l macl,@-r15
    .org 0xb776e-ORIGIN
L_000b776e:
    add #-0xc,r15
    .org 0xb7770-ORIGIN
L_000b7770:
    mov.l r5,@r15
    .org 0xb7772-ORIGIN
L_000b7772:
    mov r4,r14
    .org 0xb7774-ORIGIN
L_000b7774:
    mov.l P_000b7960,r4
    .org 0xb7776-ORIGIN
L_000b7776:
    mov r6,r0
    .org 0xb7778-ORIGIN
L_000b7778:
    mov.l P_000b7964,r5
    .org 0xb777a-ORIGIN
L_000b777a:
    extu.w r14,r6
    .org 0xb777c-ORIGIN
L_000b777c:
    mov.l P_000b7968,r2
    .org 0xb777e-ORIGIN
L_000b777e:
    jsr @r2
    .org 0xb7780-ORIGIN
L_000b7780:
    mov.b r0,@(0x7,r15)
    .org 0xb7782-ORIGIN
L_000b7782:
    mov.w r0,@(0x8,r15)
    .org 0xb7784-ORIGIN
L_000b7784:
    mov.l P_000b796c,r5
    .org 0xb7786-ORIGIN
L_000b7786:
    mov.w P_000b7840,r0
    .org 0xb7788-ORIGIN
L_000b7788:
    jsr @r5
    .org 0xb778a-ORIGIN
L_000b778a:
    mov.l @r15,r1
    .org 0xb778c-ORIGIN
L_000b778c:
    mov r0,r5
    .org 0xb778e-ORIGIN
L_000b778e:
    mov.b @(0x7,r15),r0
    .org 0xb7790-ORIGIN
L_000b7790:
    mov #0x64,r6
    .org 0xb7792-ORIGIN
L_000b7792:
    extu.b r0,r2
    .org 0xb7794-ORIGIN
L_000b7794:
    mul.l r2,r6
    .org 0xb7796-ORIGIN
L_000b7796:
    sts macl,r2
    .org 0xb7798-ORIGIN
L_000b7798:
    sub r2,r5
    .org 0xb779a-ORIGIN
L_000b779a:
    mov.w P_000b7842,r2
    .org 0xb779c-ORIGIN
L_000b779c:
    cmp/gt r2,r5
    .org 0xb779e-ORIGIN
L_000b779e:
    bf L_000b77a6
    .org 0xb77a0-ORIGIN
L_000b77a0:
    mov.w P_000b7844,r2
    .org 0xb77a2-ORIGIN
L_000b77a2:
    bra L_000b77b8
    .org 0xb77a4-ORIGIN
L_000b77a4:
    nop
    .org 0xb77a6-ORIGIN
L_000b77a6:
    mov.l P_000b7970,r2
    .org 0xb77a8-ORIGIN
L_000b77a8:
    cmp/ge r2,r5
    .org 0xb77aa-ORIGIN
L_000b77aa:
    bt L_000b77b2
    .org 0xb77ac-ORIGIN
L_000b77ac:
    mov #-0x80,r2
    .org 0xb77ae-ORIGIN
L_000b77ae:
    bra L_000b77b8
    .org 0xb77b0-ORIGIN
L_000b77b0:
    shll8 r2
    .org 0xb77b2-ORIGIN
L_000b77b2:
    mov.w P_000b7846,r6
    .org 0xb77b4-ORIGIN
L_000b77b4:
    add r6,r5
    .org 0xb77b6-ORIGIN
L_000b77b6:
    mov r5,r2
    .org 0xb77b8-ORIGIN
L_000b77b8:
    exts.w r2,r5
    .org 0xb77ba-ORIGIN
L_000b77ba:
    cmp/pz r5
    .org 0xb77bc-ORIGIN
L_000b77bc:
    bt L_000b77c0
    .org 0xb77be-ORIGIN
L_000b77be:
    mov #0x0,r5
    .org 0xb77c0-ORIGIN
L_000b77c0:
    mov.l P_000b7974,r4
    .org 0xb77c2-ORIGIN
L_000b77c2:
    extu.w r5,r5
    .org 0xb77c4-ORIGIN
L_000b77c4:
    mov.w @(0x8,r15),r0
    .org 0xb77c6-ORIGIN
L_000b77c6:
    mov.b @r4,r2
    .org 0xb77c8-ORIGIN
L_000b77c8:
    extu.w r0,r6
    .org 0xb77ca-ORIGIN
L_000b77ca:
    mov.w P_000b7848,r0
    .org 0xb77cc-ORIGIN
L_000b77cc:
    extu.b r2,r4
    .org 0xb77ce-ORIGIN
L_000b77ce:
    mul.l r4,r6
    .org 0xb77d0-ORIGIN
L_000b77d0:
    sts macl,r2
    .org 0xb77d2-ORIGIN
L_000b77d2:
    shlr8 r2
    .org 0xb77d4-ORIGIN
L_000b77d4:
    extu.w r2,r2
    .org 0xb77d6-ORIGIN
L_000b77d6:
    mul.l r2,r5
    .org 0xb77d8-ORIGIN
L_000b77d8:
    mov.l P_000b7978,r2
    .org 0xb77da-ORIGIN
L_000b77da:
    sts macl,r6
    .org 0xb77dc-ORIGIN
L_000b77dc:
    shlr8 r6
    .org 0xb77de-ORIGIN
L_000b77de:
    mov.l r6,@(r0,r2)
    .org 0xb77e0-ORIGIN
L_000b77e0:
    add #0xc,r15
    .org 0xb77e2-ORIGIN
L_000b77e2:
    lds.l @r15+,macl
    .org 0xb77e4-ORIGIN
L_000b77e4:
    lds.l @r15+,pr
    .org 0xb77e6-ORIGIN
L_000b77e6:
    rts
    .org 0xb77e8-ORIGIN
L_000b77e8:
    mov.l @r15+,r14
    .org 0xb7840-ORIGIN
P_000b7840:
    .byte 0x27
    .org 0xb7841-ORIGIN
P_000b7841:
    .byte 0x10
    .org 0xb7842-ORIGIN
P_000b7842:
    .byte 0x6c
    .org 0xb7843-ORIGIN
P_000b7843:
    .byte 0x77
    .org 0xb7844-ORIGIN
P_000b7844:
    .byte 0x7f
    .org 0xb7845-ORIGIN
P_000b7845:
    .byte 0xff
    .org 0xb7846-ORIGIN
P_000b7846:
    .byte 0x13
    .org 0xb7847-ORIGIN
P_000b7847:
    .byte 0x88
    .org 0xb7848-ORIGIN
P_000b7848:
    .byte 0x04
    .org 0xb7849-ORIGIN
P_000b7849:
    .byte 0x10
    .org 0xb7960-ORIGIN
P_000b7960:
    .byte 0x00
    .org 0xb7961-ORIGIN
P_000b7961:
    .byte 0x01
    .org 0xb7962-ORIGIN
P_000b7962:
    .byte 0x4b
    .org 0xb7963-ORIGIN
P_000b7963:
    .byte 0x0a
    .org 0xb7964-ORIGIN
P_000b7964:
    .byte 0x00
    .org 0xb7965-ORIGIN
P_000b7965:
    .byte 0x01
    .org 0xb7966-ORIGIN
P_000b7966:
    .byte 0x3f
    .org 0xb7967-ORIGIN
P_000b7967:
    .byte 0xf4
    .org 0xb7968-ORIGIN
P_000b7968:
    .byte 0x00
    .org 0xb7969-ORIGIN
P_000b7969:
    .byte 0x02
    .org 0xb796a-ORIGIN
P_000b796a:
    .byte 0x65
    .org 0xb796b-ORIGIN
P_000b796b:
    .byte 0x24
    .org 0xb796c-ORIGIN
P_000b796c:
    .byte 0x00
    .org 0xb796d-ORIGIN
P_000b796d:
    .byte 0x02
    .org 0xb796e-ORIGIN
P_000b796e:
    .byte 0x1b
    .org 0xb796f-ORIGIN
P_000b796f:
    .byte 0xbc
    .org 0xb7970-ORIGIN
P_000b7970:
    .byte 0xff
    .org 0xb7971-ORIGIN
P_000b7971:
    .byte 0xff
    .org 0xb7972-ORIGIN
P_000b7972:
    .byte 0x6c
    .org 0xb7973-ORIGIN
P_000b7973:
    .byte 0x78
    .org 0xb7974-ORIGIN
P_000b7974:
    .byte 0x00
    .org 0xb7975-ORIGIN
P_000b7975:
    .byte 0x00
    .org 0xb7976-ORIGIN
P_000b7976:
    .byte 0x85
    .org 0xb7977-ORIGIN
P_000b7977:
    .byte 0x43
    .org 0xb7978-ORIGIN
P_000b7978:
    .byte 0xff
    .org 0xb7979-ORIGIN
P_000b7979:
    .byte 0xff
    .org 0xb797a-ORIGIN
P_000b797a:
    .byte 0x28
    .org 0xb797b-ORIGIN
P_000b797b:
    .byte 0xf8
