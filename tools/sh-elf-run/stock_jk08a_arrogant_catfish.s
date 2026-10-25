! Natural byte-control entry with independently reconstructed helper closure.
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
    .org 0x4bbee-ORIGIN
L_0004bbee:
    mov.l r9,@-r15
    .org 0x4bbf0-ORIGIN
L_0004bbf0:
    mov.l r10,@-r15
    .org 0x4bbf2-ORIGIN
L_0004bbf2:
    mov.l r11,@-r15
    .org 0x4bbf4-ORIGIN
L_0004bbf4:
    mov.l r12,@-r15
    .org 0x4bbf6-ORIGIN
L_0004bbf6:
    mov.l r13,@-r15
    .org 0x4bbf8-ORIGIN
L_0004bbf8:
    mov.l r14,@-r15
    .org 0x4bbfa-ORIGIN
L_0004bbfa:
    sts.l pr,@-r15
    .org 0x4bbfc-ORIGIN
L_0004bbfc:
    sts.l macl,@-r15
    .org 0x4bbfe-ORIGIN
L_0004bbfe:
    add #-0xc,r15
    .org 0x4bc00-ORIGIN
L_0004bc00:
    mov.l L_0004bc84,r6
    .org 0x4bc02-ORIGIN
L_0004bc02:
    mov.b @r6,r0
    .org 0x4bc04-ORIGIN
L_0004bc04:
    tst #0x40,r0
    .org 0x4bc06-ORIGIN
L_0004bc06:
    bf L_0004bc94
    .org 0x4bc08-ORIGIN
L_0004bc08:
    mov.l L_0004bc54,r7
    .org 0x4bc0a-ORIGIN
L_0004bc0a:
    mov #0x17,r0
    .org 0x4bc0c-ORIGIN
L_0004bc0c:
    mov.l L_0004bc88,r4
    .org 0x4bc0e-ORIGIN
L_0004bc0e:
    mov.b @(r0,r7),r2
    .org 0x4bc10-ORIGIN
L_0004bc10:
    mov.l L_0004bc5c,r14
    .org 0x4bc12-ORIGIN
L_0004bc12:
    mov.l L_0004bc44,r9
    .org 0x4bc14-ORIGIN
L_0004bc14:
    jsr @r14
    .org 0x4bc16-ORIGIN
L_0004bc16:
    extu.b r2,r5
    .org 0x4bc18-ORIGIN
L_0004bc18:
    mov r0,r2
    .org 0x4bc1a-ORIGIN
L_0004bc1a:
    mov.w L_0004bc3e,r0
    .org 0x4bc1c-ORIGIN
L_0004bc1c:
    mov.l L_0004bc54,r7
    .org 0x4bc1e-ORIGIN
L_0004bc1e:
    mov.b r2,@(r0,r9)
    .org 0x4bc20-ORIGIN
L_0004bc20:
    mov #0x17,r0
    .org 0x4bc22-ORIGIN
L_0004bc22:
    mov.b @(r0,r7),r2
    .org 0x4bc24-ORIGIN
L_0004bc24:
    mov.l L_0004bc8c,r4
    .org 0x4bc26-ORIGIN
L_0004bc26:
    jsr @r14
    .org 0x4bc28-ORIGIN
L_0004bc28:
    extu.b r2,r5
    .org 0x4bc2a-ORIGIN
L_0004bc2a:
    mov r0,r5
    .org 0x4bc2c-ORIGIN
L_0004bc2c:
    mov.w L_0004bc40,r0
    .org 0x4bc2e-ORIGIN
L_0004bc2e:
    mov.l L_0004bc90,r6
    .org 0x4bc30-ORIGIN
L_0004bc30:
    mov.b r5,@(r0,r9)
    .org 0x4bc32-ORIGIN
L_0004bc32:
    mov.b @(0x5,r6),r0
    .org 0x4bc34-ORIGIN
L_0004bc34:
    mov.b @r6,r12
    .org 0x4bc36-ORIGIN
L_0004bc36:
    mov r0,r11
    .org 0x4bc38-ORIGIN
L_0004bc38:
    mov.b @(0x7,r6),r0
    .org 0x4bc3a-ORIGIN
L_0004bc3a:
    bra L_0004bcca
    .org 0x4bc3c-ORIGIN
L_0004bc3c:
    mov r0,r10
    .org 0x4bc3e-ORIGIN
L_0004bc3e:
    .word 0x0361
    .org 0x4bc40-ORIGIN
L_0004bc40:
    .word 0x0362
    .org 0x4bc44-ORIGIN
L_0004bc44:
    .long 0xffff128c
    .org 0x4bc54-ORIGIN
L_0004bc54:
    .long 0xffff119c
    .org 0x4bc5c-ORIGIN
L_0004bc5c:
    .long 0x00026388
    .org 0x4bc84-ORIGIN
L_0004bc84:
    .long 0xffff2466
    .org 0x4bc88-ORIGIN
L_0004bc88:
    .long 0x0001243a
    .org 0x4bc8c-ORIGIN
L_0004bc8c:
    .long 0x00012462
    .org 0x4bc90-ORIGIN
L_0004bc90:
    .long 0x000087ca
    .org 0x4bc94-ORIGIN
L_0004bc94:
    mov.l L_0004befc,r7
    .org 0x4bc96-ORIGIN
L_0004bc96:
    mov #0x17,r0
    .org 0x4bc98-ORIGIN
L_0004bc98:
    mov.l L_0004bf00,r4
    .org 0x4bc9a-ORIGIN
L_0004bc9a:
    mov.b @(r0,r7),r2
    .org 0x4bc9c-ORIGIN
L_0004bc9c:
    mov.l L_0004bf04,r14
    .org 0x4bc9e-ORIGIN
L_0004bc9e:
    mov.l L_0004bf08,r9
    .org 0x4bca0-ORIGIN
L_0004bca0:
    jsr @r14
    .org 0x4bca2-ORIGIN
L_0004bca2:
    extu.b r2,r5
    .org 0x4bca4-ORIGIN
L_0004bca4:
    mov r0,r6
    .org 0x4bca6-ORIGIN
L_0004bca6:
    mov.w L_0004bdb8,r0
    .org 0x4bca8-ORIGIN
L_0004bca8:
    mov.l L_0004befc,r7
    .org 0x4bcaa-ORIGIN
L_0004bcaa:
    mov.b r6,@(r0,r9)
    .org 0x4bcac-ORIGIN
L_0004bcac:
    mov #0x17,r0
    .org 0x4bcae-ORIGIN
L_0004bcae:
    mov.b @(r0,r7),r2
    .org 0x4bcb0-ORIGIN
L_0004bcb0:
    mov.l L_0004bf0c,r4
    .org 0x4bcb2-ORIGIN
L_0004bcb2:
    jsr @r14
    .org 0x4bcb4-ORIGIN
L_0004bcb4:
    extu.b r2,r5
    .org 0x4bcb6-ORIGIN
L_0004bcb6:
    mov r0,r5
    .org 0x4bcb8-ORIGIN
L_0004bcb8:
    mov.w L_0004bdba,r0
    .org 0x4bcba-ORIGIN
L_0004bcba:
    mov.l L_0004bf10,r6
    .org 0x4bcbc-ORIGIN
L_0004bcbc:
    mov.b r5,@(r0,r9)
    .org 0x4bcbe-ORIGIN
L_0004bcbe:
    mov.b @(0x1,r6),r0
    .org 0x4bcc0-ORIGIN
L_0004bcc0:
    mov r0,r12
    .org 0x4bcc2-ORIGIN
L_0004bcc2:
    mov.b @(0x6,r6),r0
    .org 0x4bcc4-ORIGIN
L_0004bcc4:
    mov r0,r11
    .org 0x4bcc6-ORIGIN
L_0004bcc6:
    mov.b @(0x8,r6),r0
    .org 0x4bcc8-ORIGIN
L_0004bcc8:
    mov r0,r10
    .org 0x4bcca-ORIGIN
L_0004bcca:
    mov.w L_0004bdb8,r0
    .org 0x4bccc-ORIGIN
L_0004bccc:
    mov.l L_0004bf14,r6
    .org 0x4bcce-ORIGIN
L_0004bcce:
    mov.b @(r0,r9),r13
    .org 0x4bcd0-ORIGIN
L_0004bcd0:
    mov.b @(0xf,r6),r0
    .org 0x4bcd2-ORIGIN
L_0004bcd2:
    extu.b r13,r13
    .org 0x4bcd4-ORIGIN
L_0004bcd4:
    extu.b r0,r2
    .org 0x4bcd6-ORIGIN
L_0004bcd6:
    cmp/ge r2,r13
    .org 0x4bcd8-ORIGIN
L_0004bcd8:
    bt L_0004bd0c
    .org 0x4bcda-ORIGIN
L_0004bcda:
    mov.l L_0004bf18,r4
    .org 0x4bcdc-ORIGIN
L_0004bcdc:
    extu.b r5,r5
    .org 0x4bcde-ORIGIN
L_0004bcde:
    sub r13,r2
    .org 0x4bce0-ORIGIN
L_0004bce0:
    mov.b @r4,r6
    .org 0x4bce2-ORIGIN
L_0004bce2:
    mov r2,r0
    .org 0x4bce4-ORIGIN
L_0004bce4:
    mov.l L_0004bf1c,r4
    .org 0x4bce6-ORIGIN
L_0004bce6:
    extu.b r6,r6
    .org 0x4bce8-ORIGIN
L_0004bce8:
    sub r13,r6
    .org 0x4bcea-ORIGIN
L_0004bcea:
    mul.l r6,r5
    .org 0x4bcec-ORIGIN
L_0004bcec:
    jsr @r4
    .org 0x4bcee-ORIGIN
L_0004bcee:
    sts macl,r1
    .org 0x4bcf0-ORIGIN
L_0004bcf0:
    mov r0,r6
    .org 0x4bcf2-ORIGIN
L_0004bcf2:
    mov.w L_0004bdba,r0
    .org 0x4bcf4-ORIGIN
L_0004bcf4:
    mov.b @(r0,r9),r5
    .org 0x4bcf6-ORIGIN
L_0004bcf6:
    extu.b r5,r2
    .org 0x4bcf8-ORIGIN
L_0004bcf8:
    cmp/gt r2,r6
    .org 0x4bcfa-ORIGIN
L_0004bcfa:
    bt L_0004bcfe
    .org 0x4bcfc-ORIGIN
L_0004bcfc:
    mov r6,r2
    .org 0x4bcfe-ORIGIN
L_0004bcfe:
    cmp/pz r2
    .org 0x4bd00-ORIGIN
L_0004bd00:
    bt L_0004bd04
    .org 0x4bd02-ORIGIN
L_0004bd02:
    mov #0x0,r2
    .org 0x4bd04-ORIGIN
L_0004bd04:
    mov.w L_0004bdbc,r0
    .org 0x4bd06-ORIGIN
L_0004bd06:
    mov r2,r5
    .org 0x4bd08-ORIGIN
L_0004bd08:
    bra L_0004bd12
    .org 0x4bd0a-ORIGIN
L_0004bd0a:
    mov.b r2,@(r0,r9)
    .org 0x4bd0c-ORIGIN
L_0004bd0c:
    mov.w L_0004bdbc,r0
    .org 0x4bd0e-ORIGIN
L_0004bd0e:
    mov #0x0,r5
    .org 0x4bd10-ORIGIN
L_0004bd10:
    mov.b r5,@(r0,r9)
    .org 0x4bd12-ORIGIN
L_0004bd12:
    mov.w L_0004bdbe,r0
    .org 0x4bd14-ORIGIN
L_0004bd14:
    extu.b r12,r12
    .org 0x4bd16-ORIGIN
L_0004bd16:
    mov.l L_0004bf20,r14
    .org 0x4bd18-ORIGIN
L_0004bd18:
    mov.b @(r0,r9),r4
    .org 0x4bd1a-ORIGIN
L_0004bd1a:
    extu.b r4,r2
    .org 0x4bd1c-ORIGIN
L_0004bd1c:
    cmp/ge r12,r2
    .org 0x4bd1e-ORIGIN
L_0004bd1e:
    bt/s L_0004bd34
    .org 0x4bd20-ORIGIN
L_0004bd20:
    mov.w @(0xc,r14),r0
    .org 0x4bd22-ORIGIN
L_0004bd22:
    shll2 r2
    .org 0x4bd24-ORIGIN
L_0004bd24:
    shll2 r2
    .org 0x4bd26-ORIGIN
L_0004bd26:
    shll2 r2
    .org 0x4bd28-ORIGIN
L_0004bd28:
    extu.w r0,r14
    .org 0x4bd2a-ORIGIN
L_0004bd2a:
    shll r2
    .org 0x4bd2c-ORIGIN
L_0004bd2c:
    extu.b r11,r11
    .org 0x4bd2e-ORIGIN
L_0004bd2e:
    sub r14,r2
    .org 0x4bd30-ORIGIN
L_0004bd30:
    bra L_0004bd86
    .org 0x4bd32-ORIGIN
L_0004bd32:
    mul.l r2,r11
    .org 0x4bd34-ORIGIN
L_0004bd34:
    mov r12,r6
    .org 0x4bd36-ORIGIN
L_0004bd36:
    shll2 r6
    .org 0x4bd38-ORIGIN
L_0004bd38:
    shll2 r6
    .org 0x4bd3a-ORIGIN
L_0004bd3a:
    shll2 r6
    .org 0x4bd3c-ORIGIN
L_0004bd3c:
    extu.w r0,r7
    .org 0x4bd3e-ORIGIN
L_0004bd3e:
    shll r6
    .org 0x4bd40-ORIGIN
L_0004bd40:
    cmp/ge r6,r7
    .org 0x4bd42-ORIGIN
L_0004bd42:
    bt L_0004bd72
    .org 0x4bd44-ORIGIN
L_0004bd44:
    extu.b r10,r10
    .org 0x4bd46-ORIGIN
L_0004bd46:
    mov r2,r4
    .org 0x4bd48-ORIGIN
L_0004bd48:
    sub r12,r4
    .org 0x4bd4a-ORIGIN
L_0004bd4a:
    mov.w @(0xc,r14),r0
    .org 0x4bd4c-ORIGIN
L_0004bd4c:
    mul.l r4,r10
    .org 0x4bd4e-ORIGIN
L_0004bd4e:
    shll2 r12
    .org 0x4bd50-ORIGIN
L_0004bd50:
    shll2 r12
    .org 0x4bd52-ORIGIN
L_0004bd52:
    sts macl,r6
    .org 0x4bd54-ORIGIN
L_0004bd54:
    shll2 r12
    .org 0x4bd56-ORIGIN
L_0004bd56:
    extu.w r0,r3
    .org 0x4bd58-ORIGIN
L_0004bd58:
    shll2 r6
    .org 0x4bd5a-ORIGIN
L_0004bd5a:
    mov.l r3,@(0x4,r15)
    .org 0x4bd5c-ORIGIN
L_0004bd5c:
    shll2 r6
    .org 0x4bd5e-ORIGIN
L_0004bd5e:
    shll2 r6
    .org 0x4bd60-ORIGIN
L_0004bd60:
    shll r6
    .org 0x4bd62-ORIGIN
L_0004bd62:
    shll r12
    .org 0x4bd64-ORIGIN
L_0004bd64:
    extu.b r11,r11
    .org 0x4bd66-ORIGIN
L_0004bd66:
    sub r3,r12
    .org 0x4bd68-ORIGIN
L_0004bd68:
    mov.l r11,@r15
    .org 0x4bd6a-ORIGIN
L_0004bd6a:
    mul.l r12,r11
    .org 0x4bd6c-ORIGIN
L_0004bd6c:
    sts macl,r2
    .org 0x4bd6e-ORIGIN
L_0004bd6e:
    bra L_0004bd88
    .org 0x4bd70-ORIGIN
L_0004bd70:
    add r2,r6
    .org 0x4bd72-ORIGIN
L_0004bd72:
    shll2 r2
    .org 0x4bd74-ORIGIN
L_0004bd74:
    mov.w @(0xc,r14),r0
    .org 0x4bd76-ORIGIN
L_0004bd76:
    shll2 r2
    .org 0x4bd78-ORIGIN
L_0004bd78:
    shll2 r2
    .org 0x4bd7a-ORIGIN
L_0004bd7a:
    extu.w r0,r6
    .org 0x4bd7c-ORIGIN
L_0004bd7c:
    shll r2
    .org 0x4bd7e-ORIGIN
L_0004bd7e:
    mov.l r6,@(0x8,r15)
    .org 0x4bd80-ORIGIN
L_0004bd80:
    extu.b r10,r10
    .org 0x4bd82-ORIGIN
L_0004bd82:
    sub r6,r2
    .org 0x4bd84-ORIGIN
L_0004bd84:
    mul.l r2,r10
    .org 0x4bd86-ORIGIN
L_0004bd86:
    sts macl,r6
    .org 0x4bd88-ORIGIN
L_0004bd88:
    shll r6
    .org 0x4bd8a-ORIGIN
L_0004bd8a:
    subc r2,r2
    .org 0x4bd8c-ORIGIN
L_0004bd8c:
    shll r6
    .org 0x4bd8e-ORIGIN
L_0004bd8e:
    rotcl r2
    .org 0x4bd90-ORIGIN
L_0004bd90:
    xtrct r2,r6
    .org 0x4bd92-ORIGIN
L_0004bd92:
    extu.b r5,r2
    .org 0x4bd94-ORIGIN
L_0004bd94:
    cmp/gt r2,r6
    .org 0x4bd96-ORIGIN
L_0004bd96:
    bt L_0004bd9a
    .org 0x4bd98-ORIGIN
L_0004bd98:
    mov r6,r2
    .org 0x4bd9a-ORIGIN
L_0004bd9a:
    cmp/pz r2
    .org 0x4bd9c-ORIGIN
L_0004bd9c:
    bt L_0004bda0
    .org 0x4bd9e-ORIGIN
L_0004bd9e:
    mov #0x0,r2
    .org 0x4bda0-ORIGIN
L_0004bda0:
    mov.w L_0004bdc0,r0
    .org 0x4bda2-ORIGIN
L_0004bda2:
    mov.b r2,@(r0,r9)
    .org 0x4bda4-ORIGIN
L_0004bda4:
    add #0xc,r15
    .org 0x4bda6-ORIGIN
L_0004bda6:
    lds.l @r15+,macl
    .org 0x4bda8-ORIGIN
L_0004bda8:
    lds.l @r15+,pr
    .org 0x4bdaa-ORIGIN
L_0004bdaa:
    mov.l @r15+,r14
    .org 0x4bdac-ORIGIN
L_0004bdac:
    mov.l @r15+,r13
    .org 0x4bdae-ORIGIN
L_0004bdae:
    mov.l @r15+,r12
    .org 0x4bdb0-ORIGIN
L_0004bdb0:
    mov.l @r15+,r11
    .org 0x4bdb2-ORIGIN
L_0004bdb2:
    mov.l @r15+,r10
    .org 0x4bdb4-ORIGIN
L_0004bdb4:
    rts
    .org 0x4bdb6-ORIGIN
L_0004bdb6:
    mov.l @r15+,r9
    .org 0x4bdb8-ORIGIN
L_0004bdb8:
    .word 0x0361
    .org 0x4bdba-ORIGIN
L_0004bdba:
    .word 0x0362
    .org 0x4bdbc-ORIGIN
L_0004bdbc:
    .word 0x0360
    .org 0x4bdbe-ORIGIN
L_0004bdbe:
    .word 0x035f
    .org 0x4bdc0-ORIGIN
L_0004bdc0:
    .word 0x035e
    .org 0x4befc-ORIGIN
L_0004befc:
    .long 0xffff119c
    .org 0x4bf00-ORIGIN
L_0004bf00:
    .long 0x0001244a
    .org 0x4bf04-ORIGIN
L_0004bf04:
    .long 0x00026388
    .org 0x4bf08-ORIGIN
L_0004bf08:
    .long 0xffff128c
    .org 0x4bf0c-ORIGIN
L_0004bf0c:
    .long 0x00012472
    .org 0x4bf10-ORIGIN
L_0004bf10:
    .long 0x000087ca
    .org 0x4bf14-ORIGIN
L_0004bf14:
    .long 0x00011ebe
    .org 0x4bf18-ORIGIN
L_0004bf18:
    .long 0xffff1048
    .org 0x4bf1c-ORIGIN
L_0004bf1c:
    .long 0x00021bbc
    .org 0x4bf20-ORIGIN
L_0004bf20:
    .long 0xffff22dc
