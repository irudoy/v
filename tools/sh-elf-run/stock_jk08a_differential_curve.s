! Explicit difference-divisor window and complete natural byte-lookup/signed-divider closure.
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
    .org 0x26388-ORIGIN
L_00026388:
    mov.w L_0002639a,r0
    .org 0x2638a-ORIGIN
L_0002638a:
    extu.b r5,r5
    .org 0x2638c-ORIGIN
L_0002638c:
    cmp/hs r0,r5
    .org 0x2638e-ORIGIN
L_0002638e:
    bt L_00026396
    .org 0x26390-ORIGIN
L_00026390:
    mov.l L_0002639c,r6
    .org 0x26392-ORIGIN
L_00026392:
    jmp @r6
    .org 0x26394-ORIGIN
L_00026394:
    mov #0x0,r3
    .org 0x26396-ORIGIN
L_00026396:
    rts
    .org 0x26398-ORIGIN
L_00026398:
    mov.b @(0xf,r4),r0
    .org 0x2639a-ORIGIN
L_0002639a:
    .word 0x00f0
    .org 0x2639c-ORIGIN
L_0002639c:
    .long 0x00026a84
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
    .org 0x26a60-ORIGIN
L_00026a60:
    shlr r5
    .org 0x26a62-ORIGIN
L_00026a62:
    rotcr r3
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
    .org 0x44a58-ORIGIN
L_00044a58:
    mov.l L_00044b7c,r4
    .org 0x44a5a-ORIGIN
L_00044a5a:
    mov.b r2,@(r0,r10)
    .org 0x44a5c-ORIGIN
L_00044a5c:
    mov.b @(0x5,r11),r0
    .org 0x44a5e-ORIGIN
L_00044a5e:
    jsr @r14
    .org 0x44a60-ORIGIN
L_00044a60:
    extu.b r0,r5
    .org 0x44a62-ORIGIN
L_00044a62:
    mov.b r0,@r15
    .org 0x44a64-ORIGIN
L_00044a64:
    mov.b @(0x5,r11),r0
    .org 0x44a66-ORIGIN
L_00044a66:
    mov.l L_00044b80,r4
    .org 0x44a68-ORIGIN
L_00044a68:
    jsr @r14
    .org 0x44a6a-ORIGIN
L_00044a6a:
    extu.b r0,r5
    .org 0x44a6c-ORIGIN
L_00044a6c:
    mov.b r0,@(0x4,r15)
    .org 0x44a6e-ORIGIN
L_00044a6e:
    mov.b @(0x5,r11),r0
    .org 0x44a70-ORIGIN
L_00044a70:
    mov.l L_00044b84,r4
    .org 0x44a72-ORIGIN
L_00044a72:
    jsr @r14
    .org 0x44a74-ORIGIN
L_00044a74:
    extu.b r0,r5
    .org 0x44a76-ORIGIN
L_00044a76:
    mov r0,r5
    .org 0x44a78-ORIGIN
L_00044a78:
    mov.b @r15,r7
    .org 0x44a7a-ORIGIN
L_00044a7a:
    mov.b @(0x4,r15),r0
    .org 0x44a7c-ORIGIN
L_00044a7c:
    extu.b r7,r4
    .org 0x44a7e-ORIGIN
L_00044a7e:
    extu.b r0,r2
    .org 0x44a80-ORIGIN
L_00044a80:
    cmp/gt r2,r4
    .org 0x44a82-ORIGIN
L_00044a82:
    bf L_00044ab4
    .org 0x44a84-ORIGIN
L_00044a84:
    mov.w L_00044b20,r0
    .org 0x44a86-ORIGIN
L_00044a86:
    mov r4,r6
    .org 0x44a88-ORIGIN
L_00044a88:
    sub r2,r6
    .org 0x44a8a-ORIGIN
L_00044a8a:
    mov r4,r7
    .org 0x44a8c-ORIGIN
L_00044a8c:
    mov.b @(r0,r10),r2
    .org 0x44a8e-ORIGIN
L_00044a8e:
    extu.b r5,r5
    .org 0x44a90-ORIGIN
L_00044a90:
    exts.w r6,r0
    .org 0x44a92-ORIGIN
L_00044a92:
    extu.b r2,r2
    .org 0x44a94-ORIGIN
L_00044a94:
    sub r2,r7
    .org 0x44a96-ORIGIN
L_00044a96:
    exts.w r7,r7
    .org 0x44a98-ORIGIN
L_00044a98:
    mul.l r5,r7
    .org 0x44a9a-ORIGIN
L_00044a9a:
    mov.l L_00044b88,r5
    .org 0x44a9c-ORIGIN
L_00044a9c:
    jsr @r5
    .org 0x44a9e-ORIGIN
L_00044a9e:
    sts macl,r1
    .org 0x44aa0-ORIGIN
L_00044aa0:
    cmp/pz r0
    .org 0x44aa2-ORIGIN
L_00044aa2:
    bt/s L_00044aa8
    .org 0x44aa4-ORIGIN
L_00044aa4:
    mov r0,r6
    .org 0x44aa6-ORIGIN
L_00044aa6:
    mov #0x0,r6
    .org 0x44aa8-ORIGIN
L_00044aa8:
    mov #-0x1,r12
    .org 0x44aaa-ORIGIN
L_00044aaa:
    extu.b r12,r2
    .org 0x44aac-ORIGIN
L_00044aac:
    cmp/gt r2,r6
    .org 0x44aae-ORIGIN
L_00044aae:
    bt L_00044ab6
    .org 0x44ab0-ORIGIN
L_00044ab0:
    bra L_00044ab6
    .org 0x44ab2-ORIGIN
L_00044ab2:
    mov r6,r2
    .org 0x44ab4-ORIGIN
L_00044ab4:
    mov #0x0,r2
    .org 0x44ab6-ORIGIN
L_00044ab6:
    mov.w L_00044b22,r0
    .org 0x44ab8-ORIGIN
L_00044ab8:
    mov.l L_00044b8c,r9
    .org 0x44aba-ORIGIN
L_00044aba:
    mov.b r2,@(r0,r10)
    .org 0x44b20-ORIGIN
L_00044b20:
    .word 0x041f
    .org 0x44b22-ORIGIN
L_00044b22:
    .word 0x0491
    .org 0x44b7c-ORIGIN
L_00044b7c:
    .long 0x00012738
    .org 0x44b80-ORIGIN
L_00044b80:
    .long 0x00012748
    .org 0x44b84-ORIGIN
L_00044b84:
    .long 0x00012930
    .org 0x44b88-ORIGIN
L_00044b88:
    .long 0x00021bbc
    .org 0x44b8c-ORIGIN
L_00044b8c:
    .long 0xffff124c
