! Explicit stock uptight-duck entry. The 00015C80 lookup is published after the signed call.
! The call delay slot passes incoming R4 as the dividend; R0 is the constant 000F4240.
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
    mov.l L_00021cd8,r1
    .org 0x21c72-ORIGIN
L_00021c72:
    mov.l L_00021cdc,r2
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
L_00021cd8:
    .long 0xffff9818
    .org 0x21cdc-ORIGIN
L_00021cdc:
    .long 0x0000044e
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
    mov.l L_0002654c,r7
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
    mov.l L_00026548,r6
    .org 0x26542-ORIGIN
L_00026542:
    jmp @r6
    .org 0x26544-ORIGIN
L_00026544:
    extu.w r1,r0
    .org 0x26548-ORIGIN
L_00026548:
    .long 0x00026740
    .org 0x2654c-ORIGIN
L_0002654c:
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
    .org 0xb784e-ORIGIN
L_000b784e:
    mov.l r9,@-r15
    .org 0xb7850-ORIGIN
L_000b7850:
    mov.l r10,@-r15
    .org 0xb7852-ORIGIN
L_000b7852:
    mov.l r11,@-r15
    .org 0xb7854-ORIGIN
L_000b7854:
    mov.l r12,@-r15
    .org 0xb7856-ORIGIN
L_000b7856:
    mov.l r13,@-r15
    .org 0xb7858-ORIGIN
L_000b7858:
    mov.l r14,@-r15
    .org 0xb785a-ORIGIN
L_000b785a:
    sts.l pr,@-r15
    .org 0xb785c-ORIGIN
L_000b785c:
    add #-0x8,r15
    .org 0xb785e-ORIGIN
L_000b785e:
    mov r4,r10
    .org 0xb7860-ORIGIN
L_000b7860:
    mov.l L_000b7988,r4
    .org 0xb7862-ORIGIN
L_000b7862:
    mov.l L_000b798c,r11
    .org 0xb7864-ORIGIN
L_000b7864:
    mov r6,r13
    .org 0xb7866-ORIGIN
L_000b7866:
    mov.l L_000b7968,r12
    .org 0xb7868-ORIGIN
L_000b7868:
    mov r5,r14
    .org 0xb786a-ORIGIN
L_000b786a:
    extu.w r5,r6
    .org 0xb786c-ORIGIN
L_000b786c:
    jsr @r12
    .org 0xb786e-ORIGIN
L_000b786e:
    mov r11,r5
    .org 0xb7870-ORIGIN
L_000b7870:
    mov.l L_000b7990,r4
    .org 0xb7872-ORIGIN
L_000b7872:
    extu.w r14,r6
    .org 0xb7874-ORIGIN
L_000b7874:
    mov.w r0,@r15
    .org 0xb7876-ORIGIN
L_000b7876:
    jsr @r12
    .org 0xb7878-ORIGIN
L_000b7878:
    mov r11,r5
    .org 0xb787a-ORIGIN
L_000b787a:
    mov r0,r2
    .org 0xb787c-ORIGIN
L_000b787c:
    mov.l L_000b7978,r9
    .org 0xb787e-ORIGIN
L_000b787e:
    mov.w L_000b794c,r0
    .org 0xb7880-ORIGIN
L_000b7880:
    extu.w r14,r6
    .org 0xb7882-ORIGIN
L_000b7882:
    mov.l L_000b7994,r4
    .org 0xb7884-ORIGIN
L_000b7884:
    mov r11,r5
    .org 0xb7886-ORIGIN
L_000b7886:
    mov.w r2,@(r0,r9)
    .org 0xb7888-ORIGIN
L_000b7888:
    jsr @r12
    .org 0xb788a-ORIGIN
L_000b788a:
    mov.w r2,@r13
    .org 0xb788c-ORIGIN
L_000b788c:
    mov.w r0,@(0x4,r15)
    .org 0xb788e-ORIGIN
L_000b788e:
    mov.l L_000b796c,r5
    .org 0xb7890-ORIGIN
L_000b7890:
    mov.l L_000b7998,r0
    .org 0xb7892-ORIGIN
L_000b7892:
    jsr @r5
    .org 0xb7894-ORIGIN
L_000b7894:
    mov r10,r1
    .org 0xb7896-ORIGIN
L_000b7896:
    mov.l L_000b799c,r6
    .org 0xb7898-ORIGIN
L_000b7898:
    exts.w r0,r5
    .org 0xb789a-ORIGIN
L_000b789a:
    mov.b @r6,r2
    .org 0xb789c-ORIGIN
L_000b789c:
    extu.b r2,r2
    .org 0xb789e-ORIGIN
L_000b789e:
    add #-0x32,r2
    .org 0xb78a0-ORIGIN
L_000b78a0:
    exts.w r2,r2
    .org 0xb78a2-ORIGIN
L_000b78a2:
    cmp/ge r2,r5
    .org 0xb78a4-ORIGIN
L_000b78a4:
    bt L_000b78aa
    .org 0xb78a6-ORIGIN
L_000b78a6:
    bra L_000b78ae
    .org 0xb78a8-ORIGIN
L_000b78a8:
    mov #0x1,r2
    .org 0xb78aa-ORIGIN
L_000b78aa:
    mov.w @(0x4,r15),r0
    .org 0xb78ac-ORIGIN
L_000b78ac:
    mov r0,r2
    .org 0xb78ae-ORIGIN
L_000b78ae:
    mov.w @r15,r7
    .org 0xb78b0-ORIGIN
L_000b78b0:
    mov #0x1,r6
    .org 0xb78b2-ORIGIN
L_000b78b2:
    mov.w L_000b794e,r0
    .org 0xb78b4-ORIGIN
L_000b78b4:
    extu.w r7,r7
    .org 0xb78b6-ORIGIN
L_000b78b6:
    cmp/ge r6,r7
    .org 0xb78b8-ORIGIN
L_000b78b8:
    bf/s L_000b78c2
    .org 0xb78ba-ORIGIN
L_000b78ba:
    mov.w r2,@(r0,r9)
    .org 0xb78bc-ORIGIN
L_000b78bc:
    mov.w L_000b7950,r0
    .org 0xb78be-ORIGIN
L_000b78be:
    bra L_000b78c8
    .org 0xb78c0-ORIGIN
L_000b78c0:
    mov.w r7,@(r0,r9)
    .org 0xb78c2-ORIGIN
L_000b78c2:
    mov.w L_000b7950,r0
    .org 0xb78c4-ORIGIN
L_000b78c4:
    mov #0x1,r2
    .org 0xb78c6-ORIGIN
L_000b78c6:
    mov.w r2,@(r0,r9)
    .org 0xb78c8-ORIGIN
L_000b78c8:
    add #0x8,r15
    .org 0xb78ca-ORIGIN
L_000b78ca:
    lds.l @r15+,pr
    .org 0xb78cc-ORIGIN
L_000b78cc:
    mov.l @r15+,r14
    .org 0xb78ce-ORIGIN
L_000b78ce:
    mov.l @r15+,r13
    .org 0xb78d0-ORIGIN
L_000b78d0:
    mov.l @r15+,r12
    .org 0xb78d2-ORIGIN
L_000b78d2:
    mov.l @r15+,r11
    .org 0xb78d4-ORIGIN
L_000b78d4:
    mov.l @r15+,r10
    .org 0xb78d6-ORIGIN
L_000b78d6:
    rts
    .org 0xb78d8-ORIGIN
L_000b78d8:
    mov.l @r15+,r9
    .org 0xb794c-ORIGIN
L_000b794c:
    .word 0x0cbc
    .org 0xb794e-ORIGIN
L_000b794e:
    .word 0x0cbe
    .org 0xb7950-ORIGIN
L_000b7950:
    .word 0x0ca8
    .org 0xb7968-ORIGIN
L_000b7968:
    .long 0x00026524
    .org 0xb796c-ORIGIN
L_000b796c:
    .long 0x00021bbc
    .org 0xb7978-ORIGIN
L_000b7978:
    .long 0xffff28f8
    .org 0xb7988-ORIGIN
L_000b7988:
    .long 0x00015bf0
    .org 0xb798c-ORIGIN
L_000b798c:
    .long 0x00013ca8
    .org 0xb7990-ORIGIN
L_000b7990:
    .long 0x00015c40
    .org 0xb7994-ORIGIN
L_000b7994:
    .long 0x00015c80
    .org 0xb7998-ORIGIN
L_000b7998:
    .long 0x000f4240
    .org 0xb799c-ORIGIN
L_000b799c:
    .long 0x00008c8c
