! Complete natural AN1 source dispatch closure and all exact real callees.
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
    add -0x1,r0
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
    add -0x1,r1
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
    add 0x1,r0
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
    add 0x1,r0
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
    add 0x1,r0
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
    .long 0xffff9818
    .org 0x21cdc-ORIGIN
P_00021cdc:
    .long 0x0000044e
    .org 0x263a0-ORIGIN
L_000263a0:
    mov.w P_000263b4,r0
    .org 0x263a2-ORIGIN
L_000263a2:
    extu.b r5,r5
    .org 0x263a4-ORIGIN
L_000263a4:
    cmp/hs r0,r5
    .org 0x263a6-ORIGIN
L_000263a6:
    bt L_000263ae
    .org 0x263a8-ORIGIN
L_000263a8:
    mov.l P_000263b8,r6
    .org 0x263aa-ORIGIN
L_000263aa:
    jmp @r6
    .org 0x263ac-ORIGIN
L_000263ac:
    mov #0x0,r3
    .org 0x263ae-ORIGIN
L_000263ae:
    add 0x1f,r4
    .org 0x263b0-ORIGIN
L_000263b0:
    rts
    .org 0x263b2-ORIGIN
L_000263b2:
    mov.b @r4,r0
    .org 0x263b4-ORIGIN
P_000263b4:
    .word 0x00f8
    .org 0x263b8-ORIGIN
P_000263b8:
    .long 0x00026a88
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
    mov.l P_00026abc,r6
    .org 0x26ab6-ORIGIN
L_00026ab6:
    jmp @r6
    .org 0x26ab8-ORIGIN
L_00026ab8:
    nop
    .org 0x26abc-ORIGIN
P_00026abc:
    .long 0x00026740
    .org 0x3d258-ORIGIN
L_0003d258:
    mov.l r12,@-r15
    .org 0x3d25a-ORIGIN
L_0003d25a:
    mov.l r13,@-r15
    .org 0x3d25c-ORIGIN
L_0003d25c:
    mov.l r14,@-r15
    .org 0x3d25e-ORIGIN
L_0003d25e:
    mov.l P_0003d4f8,r1
    .org 0x3d260-ORIGIN
L_0003d260:
    extu.b r4,r2
    .org 0x3d262-ORIGIN
L_0003d262:
    mov.w P_0003d3ce,r0
    .org 0x3d264-ORIGIN
L_0003d264:
    mov r2,r5
    .org 0x3d266-ORIGIN
L_0003d266:
    add 0x1,r5
    .org 0x3d268-ORIGIN
L_0003d268:
    mov r2,r7
    .org 0x3d26a-ORIGIN
L_0003d26a:
    mov.b @(r0,r1),r12
    .org 0x3d26c-ORIGIN
L_0003d26c:
    extu.b r12,r12
    .org 0x3d26e-ORIGIN
L_0003d26e:
    tst r5,r12
    .org 0x3d270-ORIGIN
L_0003d270:
    bf/s L_0003d2cc
    .org 0x3d272-ORIGIN
L_0003d272:
    add 0x1,r7
    .org 0x3d274-ORIGIN
L_0003d274:
    mov.w P_0003d3d0,r0
    .org 0x3d276-ORIGIN
L_0003d276:
    shll r2
    .org 0x3d278-ORIGIN
L_0003d278:
    mov r2,r13
    .org 0x3d27a-ORIGIN
L_0003d27a:
    mov.l P_0003d4fc,r2
    .org 0x3d27c-ORIGIN
L_0003d27c:
    mov.b @(r0,r1),r6
    .org 0x3d27e-ORIGIN
L_0003d27e:
    mov r13,r0
    .org 0x3d280-ORIGIN
L_0003d280:
    add 0x24,r2
    .org 0x3d282-ORIGIN
L_0003d282:
    extu.b r6,r14
    .org 0x3d284-ORIGIN
L_0003d284:
    mov.w @(r0,r2),r6
    .org 0x3d286-ORIGIN
L_0003d286:
    tst r5,r14
    .org 0x3d288-ORIGIN
L_0003d288:
    bf/s L_0003d29a
    .org 0x3d28a-ORIGIN
L_0003d28a:
    extu.w r6,r6
    .org 0x3d28c-ORIGIN
L_0003d28c:
    mov.w P_0003d3d0,r0
    .org 0x3d28e-ORIGIN
L_0003d28e:
    mov r6,r4
    .org 0x3d290-ORIGIN
L_0003d290:
    mov.l P_0003d500,r14
    .org 0x3d292-ORIGIN
L_0003d292:
    mov.b @(r0,r1),r2
    .org 0x3d294-ORIGIN
L_0003d294:
    or r7,r2
    .org 0x3d296-ORIGIN
L_0003d296:
    bra L_0003d2be
    .org 0x3d298-ORIGIN
L_0003d298:
    mov.b r2,@(r0,r1)
    .org 0x3d29a-ORIGIN
L_0003d29a:
    mov.l P_0003d500,r14
    .org 0x3d29c-ORIGIN
L_0003d29c:
    mov #-0x4c,r5
    .org 0x3d29e-ORIGIN
L_0003d29e:
    extu.b r5,r5
    .org 0x3d2a0-ORIGIN
L_0003d2a0:
    mov r14,r2
    .org 0x3d2a2-ORIGIN
L_0003d2a2:
    add r5,r2
    .org 0x3d2a4-ORIGIN
L_0003d2a4:
    mov.w @(r0,r2),r5
    .org 0x3d2a6-ORIGIN
L_0003d2a6:
    extu.w r5,r5
    .org 0x3d2a8-ORIGIN
L_0003d2a8:
    mov r5,r2
    .org 0x3d2aa-ORIGIN
L_0003d2aa:
    shll r2
    .org 0x3d2ac-ORIGIN
L_0003d2ac:
    add r5,r2
    .org 0x3d2ae-ORIGIN
L_0003d2ae:
    add r6,r2
    .org 0x3d2b0-ORIGIN
L_0003d2b0:
    shlr2 r2
    .org 0x3d2b2-ORIGIN
L_0003d2b2:
    extu.w r2,r4
    .org 0x3d2b4-ORIGIN
L_0003d2b4:
    cmp/eq r5,r4
    .org 0x3d2b6-ORIGIN
L_0003d2b6:
    bf L_0003d2be
    .org 0x3d2b8-ORIGIN
L_0003d2b8:
    cmp/ge r6,r4
    .org 0x3d2ba-ORIGIN
L_0003d2ba:
    bt L_0003d2be
    .org 0x3d2bc-ORIGIN
L_0003d2bc:
    add 0x1,r4
    .org 0x3d2be-ORIGIN
L_0003d2be:
    mov #-0x4c,r2
    .org 0x3d2c0-ORIGIN
L_0003d2c0:
    mov r13,r0
    .org 0x3d2c2-ORIGIN
L_0003d2c2:
    extu.b r2,r2
    .org 0x3d2c4-ORIGIN
L_0003d2c4:
    add r2,r14
    .org 0x3d2c6-ORIGIN
L_0003d2c6:
    mov.w r4,@(r0,r14)
    .org 0x3d2c8-ORIGIN
L_0003d2c8:
    bra L_0003d2d0
    .org 0x3d2ca-ORIGIN
L_0003d2ca:
    or r7,r12
    .org 0x3d2cc-ORIGIN
L_0003d2cc:
    not r7,r2
    .org 0x3d2ce-ORIGIN
L_0003d2ce:
    and r2,r12
    .org 0x3d2d0-ORIGIN
L_0003d2d0:
    mov.w P_0003d3ce,r0
    .org 0x3d2d2-ORIGIN
L_0003d2d2:
    mov.b r12,@(r0,r1)
    .org 0x3d2d4-ORIGIN
L_0003d2d4:
    mov.l @r15+,r14
    .org 0x3d2d6-ORIGIN
L_0003d2d6:
    mov.l @r15+,r13
    .org 0x3d2d8-ORIGIN
L_0003d2d8:
    rts
    .org 0x3d2da-ORIGIN
L_0003d2da:
    mov.l @r15+,r12
    .org 0x3d2dc-ORIGIN
L_0003d2dc:
    mov.l r12,@-r15
    .org 0x3d2de-ORIGIN
L_0003d2de:
    mov.l r13,@-r15
    .org 0x3d2e0-ORIGIN
L_0003d2e0:
    mov.l r14,@-r15
    .org 0x3d2e2-ORIGIN
L_0003d2e2:
    sts.l pr,@-r15
    .org 0x3d2e4-ORIGIN
L_0003d2e4:
    stc.l gbr,@-r15
    .org 0x3d2e6-ORIGIN
L_0003d2e6:
    mov.l P_0003d504,r0
    .org 0x3d2e8-ORIGIN
L_0003d2e8:
    ldc r0,gbr
    .org 0x3d2ea-ORIGIN
L_0003d2ea:
    mov #0xe,r0
    .org 0x3d2ec-ORIGIN
L_0003d2ec:
    tst.b 0x1,@(r0,gbr)
    .org 0x3d2ee-ORIGIN
L_0003d2ee:
    bf L_0003d310
    .org 0x3d2f0-ORIGIN
L_0003d2f0:
    mov #0x0,r0
    .org 0x3d2f2-ORIGIN
L_0003d2f2:
    tst.b 0x10,@(r0,gbr)
    .org 0x3d2f4-ORIGIN
L_0003d2f4:
    bt L_0003d310
    .org 0x3d2f6-ORIGIN
L_0003d2f6:
    tst.b 0x2,@(r0,gbr)
    .org 0x3d2f8-ORIGIN
L_0003d2f8:
    bf L_0003d310
    .org 0x3d2fa-ORIGIN
L_0003d2fa:
    mov #0xe,r0
    .org 0x3d2fc-ORIGIN
L_0003d2fc:
    tst.b 0x20,@(r0,gbr)
    .org 0x3d2fe-ORIGIN
L_0003d2fe:
    bf L_0003d310
    .org 0x3d300-ORIGIN
L_0003d300:
    mov.l P_0003d500,r2
    .org 0x3d302-ORIGIN
L_0003d302:
    mov #-0x46,r3
    .org 0x3d304-ORIGIN
L_0003d304:
    extu.b r3,r3
    .org 0x3d306-ORIGIN
L_0003d306:
    add r3,r2
    .org 0x3d308-ORIGIN
L_0003d308:
    extu.b r4,r0
    .org 0x3d30a-ORIGIN
L_0003d30a:
    mov #0x4b,r1
    .org 0x3d30c-ORIGIN
L_0003d30c:
    bra L_0003d338
    .org 0x3d30e-ORIGIN
L_0003d30e:
    mov.b r1,@(r0,r2)
    .org 0x3d310-ORIGIN
L_0003d310:
    mov.l P_0003d500,r14
    .org 0x3d312-ORIGIN
L_0003d312:
    mov #-0x4c,r13
    .org 0x3d314-ORIGIN
L_0003d314:
    extu.b r13,r13
    .org 0x3d316-ORIGIN
L_0003d316:
    extu.b r4,r12
    .org 0x3d318-ORIGIN
L_0003d318:
    mov r14,r5
    .org 0x3d31a-ORIGIN
L_0003d31a:
    add r13,r5
    .org 0x3d31c-ORIGIN
L_0003d31c:
    mov r12,r0
    .org 0x3d31e-ORIGIN
L_0003d31e:
    shll r0
    .org 0x3d320-ORIGIN
L_0003d320:
    mov.l P_0003d508,r4
    .org 0x3d322-ORIGIN
L_0003d322:
    mov.w @(r0,r5),r2
    .org 0x3d324-ORIGIN
L_0003d324:
    add 0x6,r13
    .org 0x3d326-ORIGIN
L_0003d326:
    add r13,r14
    .org 0x3d328-ORIGIN
L_0003d328:
    extu.w r2,r5
    .org 0x3d32a-ORIGIN
L_0003d32a:
    mov.l P_0003d50c,r2
    .org 0x3d32c-ORIGIN
L_0003d32c:
    shlr2 r5
    .org 0x3d32e-ORIGIN
L_0003d32e:
    jsr @r2
    .org 0x3d330-ORIGIN
L_0003d330:
    extu.b r5,r5
    .org 0x3d332-ORIGIN
L_0003d332:
    mov r0,r2
    .org 0x3d334-ORIGIN
L_0003d334:
    mov r12,r0
    .org 0x3d336-ORIGIN
L_0003d336:
    mov.b r2,@(r0,r14)
    .org 0x3d338-ORIGIN
L_0003d338:
    ldc.l @r15+,gbr
    .org 0x3d33a-ORIGIN
L_0003d33a:
    lds.l @r15+,pr
    .org 0x3d33c-ORIGIN
L_0003d33c:
    mov.l @r15+,r14
    .org 0x3d33e-ORIGIN
L_0003d33e:
    mov.l @r15+,r13
    .org 0x3d340-ORIGIN
L_0003d340:
    rts
    .org 0x3d342-ORIGIN
L_0003d342:
    mov.l @r15+,r12
    .org 0x3d344-ORIGIN
L_0003d344:
    mov.l r14,@-r15
    .org 0x3d346-ORIGIN
L_0003d346:
    sts.l pr,@-r15
    .org 0x3d348-ORIGIN
L_0003d348:
    stc.l gbr,@-r15
    .org 0x3d34a-ORIGIN
L_0003d34a:
    mov.l P_0003d510,r0
    .org 0x3d34c-ORIGIN
L_0003d34c:
    ldc r0,gbr
    .org 0x3d34e-ORIGIN
L_0003d34e:
    mov.l P_0003d500,r2
    .org 0x3d350-ORIGIN
L_0003d350:
    mov #-0x46,r3
    .org 0x3d352-ORIGIN
L_0003d352:
    extu.b r3,r3
    .org 0x3d354-ORIGIN
L_0003d354:
    extu.b r4,r14
    .org 0x3d356-ORIGIN
L_0003d356:
    add r3,r2
    .org 0x3d358-ORIGIN
L_0003d358:
    mov r14,r0
    .org 0x3d35a-ORIGIN
L_0003d35a:
    mov.b @(r0,r2),r6
    .org 0x3d35c-ORIGIN
L_0003d35c:
    mov #0xa,r1
    .org 0x3d35e-ORIGIN
L_0003d35e:
    extu.b r6,r6
    .org 0x3d360-ORIGIN
L_0003d360:
    cmp/ge r1,r6
    .org 0x3d362-ORIGIN
L_0003d362:
    bt L_0003d372
    .org 0x3d364-ORIGIN
L_0003d364:
    stc gbr,r2
    .org 0x3d366-ORIGIN
L_0003d366:
    add 0x61,r2
    .org 0x3d368-ORIGIN
L_0003d368:
    mov r14,r0
    .org 0x3d36a-ORIGIN
L_0003d36a:
    mov #0x0,r3
    .org 0x3d36c-ORIGIN
L_0003d36c:
    mov.b r3,@(r0,r2)
    .org 0x3d36e-ORIGIN
L_0003d36e:
    bra L_0003d3a6
    .org 0x3d370-ORIGIN
L_0003d370:
    nop
    .org 0x3d372-ORIGIN
L_0003d372:
    mov #-0x56,r3
    .org 0x3d374-ORIGIN
L_0003d374:
    extu.b r3,r3
    .org 0x3d376-ORIGIN
L_0003d376:
    cmp/ge r3,r6
    .org 0x3d378-ORIGIN
L_0003d378:
    bt L_0003d39e
    .org 0x3d37a-ORIGIN
L_0003d37a:
    add -0xa,r6
    .org 0x3d37c-ORIGIN
L_0003d37c:
    mov.l P_0003d514,r2
    .org 0x3d37e-ORIGIN
L_0003d37e:
    extu.w r6,r6
    .org 0x3d380-ORIGIN
L_0003d380:
    mov r6,r1
    .org 0x3d382-ORIGIN
L_0003d382:
    shll2 r1
    .org 0x3d384-ORIGIN
L_0003d384:
    shll2 r1
    .org 0x3d386-ORIGIN
L_0003d386:
    sub r6,r1
    .org 0x3d388-ORIGIN
L_0003d388:
    shll2 r1
    .org 0x3d38a-ORIGIN
L_0003d38a:
    mov #-0x6a,r3
    .org 0x3d38c-ORIGIN
L_0003d38c:
    shll2 r1
    .org 0x3d38e-ORIGIN
L_0003d38e:
    jsr @r2
    .org 0x3d390-ORIGIN
L_0003d390:
    extu.b r3,r0
    .org 0x3d392-ORIGIN
L_0003d392:
    mov r0,r6
    .org 0x3d394-ORIGIN
L_0003d394:
    mov r14,r0
    .org 0x3d396-ORIGIN
L_0003d396:
    stc gbr,r2
    .org 0x3d398-ORIGIN
L_0003d398:
    add 0x61,r2
    .org 0x3d39a-ORIGIN
L_0003d39a:
    bra L_0003d3a6
    .org 0x3d39c-ORIGIN
L_0003d39c:
    mov.b r6,@(r0,r2)
    .org 0x3d39e-ORIGIN
L_0003d39e:
    stc gbr,r2
    .org 0x3d3a0-ORIGIN
L_0003d3a0:
    add 0x61,r2
    .org 0x3d3a2-ORIGIN
L_0003d3a2:
    mov #-0x1,r3
    .org 0x3d3a4-ORIGIN
L_0003d3a4:
    mov.b r3,@(r0,r2)
    .org 0x3d3a6-ORIGIN
L_0003d3a6:
    ldc.l @r15+,gbr
    .org 0x3d3a8-ORIGIN
L_0003d3a8:
    lds.l @r15+,pr
    .org 0x3d3aa-ORIGIN
L_0003d3aa:
    rts
    .org 0x3d3ac-ORIGIN
L_0003d3ac:
    mov.l @r15+,r14
    .org 0x3d3ae-ORIGIN
L_0003d3ae:
    mov.l P_0003d500,r5
    .org 0x3d3b0-ORIGIN
L_0003d3b0:
    mov #-0x4c,r3
    .org 0x3d3b2-ORIGIN
L_0003d3b2:
    extu.b r4,r4
    .org 0x3d3b4-ORIGIN
L_0003d3b4:
    mov.l P_0003d4f8,r2
    .org 0x3d3b6-ORIGIN
L_0003d3b6:
    extu.b r3,r3
    .org 0x3d3b8-ORIGIN
L_0003d3b8:
    mov r4,r0
    .org 0x3d3ba-ORIGIN
L_0003d3ba:
    add r3,r5
    .org 0x3d3bc-ORIGIN
L_0003d3bc:
    mov.w P_0003d3d2,r1
    .org 0x3d3be-ORIGIN
L_0003d3be:
    shll r0
    .org 0x3d3c0-ORIGIN
L_0003d3c0:
    mov.w @(r0,r5),r6
    .org 0x3d3c2-ORIGIN
L_0003d3c2:
    add r1,r2
    .org 0x3d3c4-ORIGIN
L_0003d3c4:
    mov r4,r0
    .org 0x3d3c6-ORIGIN
L_0003d3c6:
    extu.w r6,r6
    .org 0x3d3c8-ORIGIN
L_0003d3c8:
    shlr2 r6
    .org 0x3d3ca-ORIGIN
L_0003d3ca:
    rts
    .org 0x3d3cc-ORIGIN
L_0003d3cc:
    mov.b r6,@(r0,r2)
    .org 0x3d3ce-ORIGIN
P_0003d3ce:
    .word 0x057a
    .org 0x3d3d0-ORIGIN
P_0003d3d0:
    .word 0x0580
    .org 0x3d3d2-ORIGIN
P_0003d3d2:
    .word 0x057b
    .org 0x3d3d4-ORIGIN
L_0003d3d4:
    mov.l P_0003d518,r5
    .org 0x3d3d6-ORIGIN
L_0003d3d6:
    mov.b @r5,r0
    .org 0x3d3d8-ORIGIN
L_0003d3d8:
    tst 0x40,r0
    .org 0x3d3da-ORIGIN
L_0003d3da:
    bt/s L_0003d3fa
    .org 0x3d3dc-ORIGIN
L_0003d3dc:
    mov r4,r6
    .org 0x3d3de-ORIGIN
L_0003d3de:
    mov.l P_0003d510,r5
    .org 0x3d3e0-ORIGIN
L_0003d3e0:
    mov #0x74,r0
    .org 0x3d3e2-ORIGIN
L_0003d3e2:
    mov.b @(r0,r5),r2
    .org 0x3d3e4-ORIGIN
L_0003d3e4:
    mov #0x64,r5
    .org 0x3d3e6-ORIGIN
L_0003d3e6:
    cmp/hs r5,r2
    .org 0x3d3e8-ORIGIN
L_0003d3e8:
    bt L_0003d3fa
    .org 0x3d3ea-ORIGIN
L_0003d3ea:
    mov.l P_0003d51c,r7
    .org 0x3d3ec-ORIGIN
L_0003d3ec:
    add 0x1,r6
    .org 0x3d3ee-ORIGIN
L_0003d3ee:
    mov.w P_0003d4ee,r0
    .org 0x3d3f0-ORIGIN
L_0003d3f0:
    not r6,r6
    .org 0x3d3f2-ORIGIN
L_0003d3f2:
    mov.b @(r0,r7),r2
    .org 0x3d3f4-ORIGIN
L_0003d3f4:
    and r6,r2
    .org 0x3d3f6-ORIGIN
L_0003d3f6:
    bra L_0003d414
    .org 0x3d3f8-ORIGIN
L_0003d3f8:
    mov.b r2,@(r0,r7)
    .org 0x3d3fa-ORIGIN
L_0003d3fa:
    mov.l P_0003d51c,r7
    .org 0x3d3fc-ORIGIN
L_0003d3fc:
    extu.b r6,r6
    .org 0x3d3fe-ORIGIN
L_0003d3fe:
    mov.w P_0003d4ee,r0
    .org 0x3d400-ORIGIN
L_0003d400:
    mov r6,r2
    .org 0x3d402-ORIGIN
L_0003d402:
    add 0x1,r2
    .org 0x3d404-ORIGIN
L_0003d404:
    mov.b @(r0,r7),r4
    .org 0x3d406-ORIGIN
L_0003d406:
    extu.b r4,r4
    .org 0x3d408-ORIGIN
L_0003d408:
    tst r2,r4
    .org 0x3d40a-ORIGIN
L_0003d40a:
    bf L_0003d418
    .org 0x3d40c-ORIGIN
L_0003d40c:
    add 0x1,r6
    .org 0x3d40e-ORIGIN
L_0003d40e:
    mov.w P_0003d4ee,r0
    .org 0x3d410-ORIGIN
L_0003d410:
    or r6,r4
    .org 0x3d412-ORIGIN
L_0003d412:
    mov.b r4,@(r0,r7)
    .org 0x3d414-ORIGIN
L_0003d414:
    rts
    .org 0x3d416-ORIGIN
L_0003d416:
    mov #0x1,r0
    .org 0x3d418-ORIGIN
L_0003d418:
    rts
    .org 0x3d41a-ORIGIN
L_0003d41a:
    mov #0x0,r0
    .org 0x3d41c-ORIGIN
L_0003d41c:
    mov.l r14,@-r15
    .org 0x3d41e-ORIGIN
L_0003d41e:
    sts.l pr,@-r15
    .org 0x3d420-ORIGIN
L_0003d420:
    mov.l P_0003d51c,r5
    .org 0x3d422-ORIGIN
L_0003d422:
    extu.b r4,r14
    .org 0x3d424-ORIGIN
L_0003d424:
    mov r14,r0
    .org 0x3d426-ORIGIN
L_0003d426:
    mov #0x1,r3
    .org 0x3d428-ORIGIN
L_0003d428:
    mov r5,r2
    .org 0x3d42a-ORIGIN
L_0003d42a:
    add 0x7a,r2
    .org 0x3d42c-ORIGIN
L_0003d42c:
    mov.b @(r0,r2),r6
    .org 0x3d42e-ORIGIN
L_0003d42e:
    extu.b r6,r6
    .org 0x3d430-ORIGIN
L_0003d430:
    cmp/ge r3,r6
    .org 0x3d432-ORIGIN
L_0003d432:
    bf L_0003d450
    .org 0x3d434-ORIGIN
L_0003d434:
    bsr L_0003d3d4
    .org 0x3d436-ORIGIN
L_0003d436:
    mov r14,r4
    .org 0x3d438-ORIGIN
L_0003d438:
    tst r0,r0
    .org 0x3d43a-ORIGIN
L_0003d43a:
    bt L_0003d456
    .org 0x3d43c-ORIGIN
L_0003d43c:
    mov.l P_0003d500,r2
    .org 0x3d43e-ORIGIN
L_0003d43e:
    mov #-0x46,r3
    .org 0x3d440-ORIGIN
L_0003d440:
    extu.b r3,r3
    .org 0x3d442-ORIGIN
L_0003d442:
    mov r14,r0
    .org 0x3d444-ORIGIN
L_0003d444:
    add r3,r2
    .org 0x3d446-ORIGIN
L_0003d446:
    mov.b @(r0,r2),r6
    .org 0x3d448-ORIGIN
L_0003d448:
    mov.l P_0003d520,r2
    .org 0x3d44a-ORIGIN
L_0003d44a:
    add 0x54,r2
    .org 0x3d44c-ORIGIN
L_0003d44c:
    bra L_0003d456
    .org 0x3d44e-ORIGIN
L_0003d44e:
    mov.b r6,@(r0,r2)
    .org 0x3d450-ORIGIN
L_0003d450:
    add 0x1,r6
    .org 0x3d452-ORIGIN
L_0003d452:
    add 0x7a,r5
    .org 0x3d454-ORIGIN
L_0003d454:
    mov.b r6,@(r0,r5)
    .org 0x3d456-ORIGIN
L_0003d456:
    lds.l @r15+,pr
    .org 0x3d458-ORIGIN
L_0003d458:
    rts
    .org 0x3d45a-ORIGIN
L_0003d45a:
    mov.l @r15+,r14
    .org 0x3d45c-ORIGIN
L_0003d45c:
    add -0x4,r15
    .org 0x3d45e-ORIGIN
L_0003d45e:
    mov.l P_0003d524,r6
    .org 0x3d460-ORIGIN
L_0003d460:
    mov.b @(0x6,r6),r0
    .org 0x3d462-ORIGIN
L_0003d462:
    tst 0x40,r0
    .org 0x3d464-ORIGIN
L_0003d464:
    bf/s L_0003d4a4
    .org 0x3d466-ORIGIN
L_0003d466:
    extu.b r4,r4
    .org 0x3d468-ORIGIN
L_0003d468:
    mov.b @r6,r0
    .org 0x3d46a-ORIGIN
L_0003d46a:
    tst 0x20,r0
    .org 0x3d46c-ORIGIN
L_0003d46c:
    bf L_0003d4a4
    .org 0x3d46e-ORIGIN
L_0003d46e:
    mov.l P_0003d4f8,r2
    .org 0x3d470-ORIGIN
L_0003d470:
    mov.w P_0003d4f0,r0
    .org 0x3d472-ORIGIN
L_0003d472:
    mov.b @(r0,r2),r6
    .org 0x3d474-ORIGIN
L_0003d474:
    mov r4,r2
    .org 0x3d476-ORIGIN
L_0003d476:
    add 0x1,r2
    .org 0x3d478-ORIGIN
L_0003d478:
    extu.b r6,r6
    .org 0x3d47a-ORIGIN
L_0003d47a:
    tst r2,r6
    .org 0x3d47c-ORIGIN
L_0003d47c:
    bt L_0003d4a4
    .org 0x3d47e-ORIGIN
L_0003d47e:
    mov.l P_0003d500,r2
    .org 0x3d480-ORIGIN
L_0003d480:
    mov #-0x46,r6
    .org 0x3d482-ORIGIN
L_0003d482:
    extu.b r6,r6
    .org 0x3d484-ORIGIN
L_0003d484:
    mov.l P_0003d4f8,r7
    .org 0x3d486-ORIGIN
L_0003d486:
    add r6,r2
    .org 0x3d488-ORIGIN
L_0003d488:
    mov.w P_0003d4f2,r6
    .org 0x3d48a-ORIGIN
L_0003d48a:
    mov r4,r0
    .org 0x3d48c-ORIGIN
L_0003d48c:
    mov.b @(r0,r2),r5
    .org 0x3d48e-ORIGIN
L_0003d48e:
    mov r7,r2
    .org 0x3d490-ORIGIN
L_0003d490:
    add r6,r2
    .org 0x3d492-ORIGIN
L_0003d492:
    mov.b @(r0,r2),r6
    .org 0x3d494-ORIGIN
L_0003d494:
    extu.b r5,r5
    .org 0x3d496-ORIGIN
L_0003d496:
    extu.b r6,r6
    .org 0x3d498-ORIGIN
L_0003d498:
    cmp/ge r6,r5
    .org 0x3d49a-ORIGIN
L_0003d49a:
    bt/s L_0003d4a4
    .org 0x3d49c-ORIGIN
L_0003d49c:
    mov.l r5,@r15
    .org 0x3d49e-ORIGIN
L_0003d49e:
    mov.w P_0003d4f2,r2
    .org 0x3d4a0-ORIGIN
L_0003d4a0:
    add r2,r7
    .org 0x3d4a2-ORIGIN
L_0003d4a2:
    mov.b r5,@(r0,r7)
    .org 0x3d4a4-ORIGIN
L_0003d4a4:
    rts
    .org 0x3d4a6-ORIGIN
L_0003d4a6:
    add 0x4,r15
    .org 0x3d4a8-ORIGIN
L_0003d4a8:
    mov.l r14,@-r15
    .org 0x3d4aa-ORIGIN
L_0003d4aa:
    sts.l pr,@-r15
    .org 0x3d4ac-ORIGIN
L_0003d4ac:
    mov.l P_0003d4fc,r5
    .org 0x3d4ae-ORIGIN
L_0003d4ae:
    extu.b r4,r14
    .org 0x3d4b0-ORIGIN
L_0003d4b0:
    mov r14,r0
    .org 0x3d4b2-ORIGIN
L_0003d4b2:
    shll r0
    .org 0x3d4b4-ORIGIN
L_0003d4b4:
    add 0x24,r5
    .org 0x3d4b6-ORIGIN
L_0003d4b6:
    mov.l P_0003d508,r4
    .org 0x3d4b8-ORIGIN
L_0003d4b8:
    mov.w @(r0,r5),r6
    .org 0x3d4ba-ORIGIN
L_0003d4ba:
    mov.l P_0003d50c,r2
    .org 0x3d4bc-ORIGIN
L_0003d4bc:
    extu.w r6,r5
    .org 0x3d4be-ORIGIN
L_0003d4be:
    shlr2 r5
    .org 0x3d4c0-ORIGIN
L_0003d4c0:
    jsr @r2
    .org 0x3d4c2-ORIGIN
L_0003d4c2:
    extu.b r5,r5
    .org 0x3d4c4-ORIGIN
L_0003d4c4:
    extu.b r0,r6
    .org 0x3d4c6-ORIGIN
L_0003d4c6:
    mov #0xa,r3
    .org 0x3d4c8-ORIGIN
L_0003d4c8:
    cmp/gt r3,r6
    .org 0x3d4ca-ORIGIN
L_0003d4ca:
    bf L_0003d4dc
    .org 0x3d4cc-ORIGIN
L_0003d4cc:
    mov.l P_0003d4f8,r2
    .org 0x3d4ce-ORIGIN
L_0003d4ce:
    add -0xa,r6
    .org 0x3d4d0-ORIGIN
L_0003d4d0:
    extu.b r6,r6
    .org 0x3d4d2-ORIGIN
L_0003d4d2:
    mov.w P_0003d4f4,r3
    .org 0x3d4d4-ORIGIN
L_0003d4d4:
    mov r14,r0
    .org 0x3d4d6-ORIGIN
L_0003d4d6:
    add r3,r2
    .org 0x3d4d8-ORIGIN
L_0003d4d8:
    bra L_0003d4e8
    .org 0x3d4da-ORIGIN
L_0003d4da:
    mov.b r6,@(r0,r2)
    .org 0x3d4dc-ORIGIN
L_0003d4dc:
    mov.l P_0003d4f8,r2
    .org 0x3d4de-ORIGIN
L_0003d4de:
    mov #0x0,r1
    .org 0x3d4e0-ORIGIN
L_0003d4e0:
    mov.w P_0003d4f4,r3
    .org 0x3d4e2-ORIGIN
L_0003d4e2:
    mov r14,r0
    .org 0x3d4e4-ORIGIN
L_0003d4e4:
    add r3,r2
    .org 0x3d4e6-ORIGIN
L_0003d4e6:
    mov.b r1,@(r0,r2)
    .org 0x3d4e8-ORIGIN
L_0003d4e8:
    lds.l @r15+,pr
    .org 0x3d4ea-ORIGIN
L_0003d4ea:
    rts
    .org 0x3d4ec-ORIGIN
L_0003d4ec:
    mov.l @r15+,r14
    .org 0x3d4ee-ORIGIN
P_0003d4ee:
    .word 0x0125
    .org 0x3d4f0-ORIGIN
P_0003d4f0:
    .word 0x057a
    .org 0x3d4f2-ORIGIN
P_0003d4f2:
    .word 0x0588
    .org 0x3d4f4-ORIGIN
P_0003d4f4:
    .word 0x057e
    .org 0x3d4f8-ORIGIN
P_0003d4f8:
    .long 0xffff39c4
    .org 0x3d4fc-ORIGIN
P_0003d4fc:
    .long 0xffff1d34
    .org 0x3d500-ORIGIN
P_0003d500:
    .long 0xffff277e
    .org 0x3d504-ORIGIN
P_0003d504:
    .long 0x00008b34
    .org 0x3d508-ORIGIN
P_0003d508:
    .long 0x00012dea
    .org 0x3d50c-ORIGIN
P_0003d50c:
    .long 0x000263a0
    .org 0x3d510-ORIGIN
P_0003d510:
    .long 0xffff1114
    .org 0x3d514-ORIGIN
P_0003d514:
    .long 0x00021bbc
    .org 0x3d518-ORIGIN
P_0003d518:
    .long 0xffff4185
    .org 0x3d51c-ORIGIN
P_0003d51c:
    .long 0xffff1e60
    .org 0x3d520-ORIGIN
P_0003d520:
    .long 0xffff55bc
    .org 0x3d524-ORIGIN
P_0003d524:
    .long 0xffff417f
    .org 0x3d528-ORIGIN
L_0003d528:
    mov.l P_0003d770,r5
    .org 0x3d52a-ORIGIN
L_0003d52a:
    mov.b @(0x9,r5),r0
    .org 0x3d52c-ORIGIN
L_0003d52c:
    tst 0x80,r0
    .org 0x3d52e-ORIGIN
L_0003d52e:
    bf/s L_0003d560
    .org 0x3d530-ORIGIN
L_0003d530:
    mov r0,r6
    .org 0x3d532-ORIGIN
L_0003d532:
    mov.l P_0003d774,r4
    .org 0x3d534-ORIGIN
L_0003d534:
    mov #-0x47,r0
    .org 0x3d536-ORIGIN
L_0003d536:
    extu.b r0,r0
    .org 0x3d538-ORIGIN
L_0003d538:
    mov.l P_0003d778,r1
    .org 0x3d53a-ORIGIN
L_0003d53a:
    mov.b @(r0,r4),r2
    .org 0x3d53c-ORIGIN
L_0003d53c:
    mov.w P_0003d652,r0
    .org 0x3d53e-ORIGIN
L_0003d53e:
    mov.b r2,@(r0,r1)
    .org 0x3d540-ORIGIN
L_0003d540:
    mov.w P_0003d654,r0
    .org 0x3d542-ORIGIN
L_0003d542:
    mov.b r2,@(r0,r1)
    .org 0x3d544-ORIGIN
L_0003d544:
    mov.w P_0003d656,r0
    .org 0x3d546-ORIGIN
L_0003d546:
    mov.b r2,@(r0,r1)
    .org 0x3d548-ORIGIN
L_0003d548:
    mov.w P_0003d658,r0
    .org 0x3d54a-ORIGIN
L_0003d54a:
    mov.b r2,@(r0,r1)
    .org 0x3d54c-ORIGIN
L_0003d54c:
    mov.w P_0003d65a,r0
    .org 0x3d54e-ORIGIN
L_0003d54e:
    mov.b r2,@(r0,r1)
    .org 0x3d550-ORIGIN
L_0003d550:
    mov.w P_0003d65c,r0
    .org 0x3d552-ORIGIN
L_0003d552:
    mov.b r2,@(r0,r1)
    .org 0x3d554-ORIGIN
L_0003d554:
    mov.w P_0003d65e,r0
    .org 0x3d556-ORIGIN
L_0003d556:
    mov.b r2,@(r0,r1)
    .org 0x3d558-ORIGIN
L_0003d558:
    mov r6,r0
    .org 0x3d55a-ORIGIN
L_0003d55a:
    or 0x80,r0
    .org 0x3d55c-ORIGIN
L_0003d55c:
    rts
    .org 0x3d55e-ORIGIN
L_0003d55e:
    mov.b r0,@(0x9,r5)
    .org 0x3d560-ORIGIN
L_0003d560:
    mov.w P_0003d660,r6
    .org 0x3d562-ORIGIN
L_0003d562:
    mov.b @r6,r0
    .org 0x3d564-ORIGIN
L_0003d564:
    tst 0x20,r0
    .org 0x3d566-ORIGIN
L_0003d566:
    bt L_0003d5c0
    .org 0x3d568-ORIGIN
L_0003d568:
    mov.l P_0003d778,r1
    .org 0x3d56a-ORIGIN
L_0003d56a:
    mov.w P_0003d65c,r0
    .org 0x3d56c-ORIGIN
L_0003d56c:
    mov.l P_0003d774,r4
    .org 0x3d56e-ORIGIN
L_0003d56e:
    mov.b @(r0,r1),r7
    .org 0x3d570-ORIGIN
L_0003d570:
    mov.w P_0003d65e,r0
    .org 0x3d572-ORIGIN
L_0003d572:
    mov.b r7,@(r0,r1)
    .org 0x3d574-ORIGIN
L_0003d574:
    extu.b r7,r7
    .org 0x3d576-ORIGIN
L_0003d576:
    mov.w P_0003d65a,r0
    .org 0x3d578-ORIGIN
L_0003d578:
    mov.b @(r0,r1),r2
    .org 0x3d57a-ORIGIN
L_0003d57a:
    mov.w P_0003d65c,r0
    .org 0x3d57c-ORIGIN
L_0003d57c:
    mov.b r2,@(r0,r1)
    .org 0x3d57e-ORIGIN
L_0003d57e:
    mov.w P_0003d658,r0
    .org 0x3d580-ORIGIN
L_0003d580:
    mov.b @(r0,r1),r2
    .org 0x3d582-ORIGIN
L_0003d582:
    mov.w P_0003d65a,r0
    .org 0x3d584-ORIGIN
L_0003d584:
    mov.b r2,@(r0,r1)
    .org 0x3d586-ORIGIN
L_0003d586:
    mov.w P_0003d656,r0
    .org 0x3d588-ORIGIN
L_0003d588:
    mov.b @(r0,r1),r2
    .org 0x3d58a-ORIGIN
L_0003d58a:
    mov.w P_0003d658,r0
    .org 0x3d58c-ORIGIN
L_0003d58c:
    mov.b r2,@(r0,r1)
    .org 0x3d58e-ORIGIN
L_0003d58e:
    mov.w P_0003d654,r0
    .org 0x3d590-ORIGIN
L_0003d590:
    mov.b @(r0,r1),r2
    .org 0x3d592-ORIGIN
L_0003d592:
    mov.w P_0003d656,r0
    .org 0x3d594-ORIGIN
L_0003d594:
    mov.b r2,@(r0,r1)
    .org 0x3d596-ORIGIN
L_0003d596:
    mov.w P_0003d652,r0
    .org 0x3d598-ORIGIN
L_0003d598:
    mov.b @(r0,r1),r2
    .org 0x3d59a-ORIGIN
L_0003d59a:
    mov.w P_0003d654,r0
    .org 0x3d59c-ORIGIN
L_0003d59c:
    mov.b r2,@(r0,r1)
    .org 0x3d59e-ORIGIN
L_0003d59e:
    mov #-0x47,r0
    .org 0x3d5a0-ORIGIN
L_0003d5a0:
    extu.b r0,r0
    .org 0x3d5a2-ORIGIN
L_0003d5a2:
    mov.b @(r0,r4),r2
    .org 0x3d5a4-ORIGIN
L_0003d5a4:
    mov.w P_0003d652,r0
    .org 0x3d5a6-ORIGIN
L_0003d5a6:
    mov.b r2,@(r0,r1)
    .org 0x3d5a8-ORIGIN
L_0003d5a8:
    extu.b r2,r2
    .org 0x3d5aa-ORIGIN
L_0003d5aa:
    cmp/gt r2,r7
    .org 0x3d5ac-ORIGIN
L_0003d5ac:
    bf/s L_0003d5ba
    .org 0x3d5ae-ORIGIN
L_0003d5ae:
    sub r7,r2
    .org 0x3d5b0-ORIGIN
L_0003d5b0:
    extu.b r2,r5
    .org 0x3d5b2-ORIGIN
L_0003d5b2:
    mov.w P_0003d662,r0
    .org 0x3d5b4-ORIGIN
L_0003d5b4:
    neg r5,r2
    .org 0x3d5b6-ORIGIN
L_0003d5b6:
    rts
    .org 0x3d5b8-ORIGIN
L_0003d5b8:
    mov.b r2,@(r0,r1)
    .org 0x3d5ba-ORIGIN
L_0003d5ba:
    mov.w P_0003d662,r0
    .org 0x3d5bc-ORIGIN
L_0003d5bc:
    rts
    .org 0x3d5be-ORIGIN
L_0003d5be:
    mov.b r2,@(r0,r1)
    .org 0x3d5c0-ORIGIN
L_0003d5c0:
    rts
    .org 0x3d5c2-ORIGIN
L_0003d5c2:
    nop
    .org 0x3d5c4-ORIGIN
L_0003d5c4:
    stc.l gbr,@-r15
    .org 0x3d5c6-ORIGIN
L_0003d5c6:
    mov.l P_0003d770,r0
    .org 0x3d5c8-ORIGIN
L_0003d5c8:
    ldc r0,gbr
    .org 0x3d5ca-ORIGIN
L_0003d5ca:
    mov.l P_0003d77c,r2
    .org 0x3d5cc-ORIGIN
L_0003d5cc:
    mov #0x7a,r0
    .org 0x3d5ce-ORIGIN
L_0003d5ce:
    mov.b @(r0,r2),r1
    .org 0x3d5d0-ORIGIN
L_0003d5d0:
    mov.l P_0003d780,r2
    .org 0x3d5d2-ORIGIN
L_0003d5d2:
    mov.b @(0x1d,gbr),r0
    .org 0x3d5d4-ORIGIN
L_0003d5d4:
    mov.b @r2,r4
    .org 0x3d5d6-ORIGIN
L_0003d5d6:
    cmp/hs r4,r1
    .org 0x3d5d8-ORIGIN
L_0003d5d8:
    bf/s L_0003d5ec
    .org 0x3d5da-ORIGIN
L_0003d5da:
    mov r0,r6
    .org 0x3d5dc-ORIGIN
L_0003d5dc:
    mov.b @(0xa9,gbr),r0
    .org 0x3d5de-ORIGIN
L_0003d5de:
    tst r0,r0
    .org 0x3d5e0-ORIGIN
L_0003d5e0:
    mov r6,r0
    .org 0x3d5e2-ORIGIN
L_0003d5e2:
    bf/s L_0003d5e8
    .org 0x3d5e4-ORIGIN
L_0003d5e4:
    and 0xfe,r0
    .org 0x3d5e6-ORIGIN
L_0003d5e6:
    or 0x1,r0
    .org 0x3d5e8-ORIGIN
L_0003d5e8:
    bra L_0003d5f8
    .org 0x3d5ea-ORIGIN
L_0003d5ea:
    mov.b r0,@(0x1d,gbr)
    .org 0x3d5ec-ORIGIN
L_0003d5ec:
    mov r6,r0
    .org 0x3d5ee-ORIGIN
L_0003d5ee:
    mov.l P_0003d784,r6
    .org 0x3d5f0-ORIGIN
L_0003d5f0:
    and 0xfe,r0
    .org 0x3d5f2-ORIGIN
L_0003d5f2:
    mov.b r0,@(0x1d,gbr)
    .org 0x3d5f4-ORIGIN
L_0003d5f4:
    mov.b @r6,r0
    .org 0x3d5f6-ORIGIN
L_0003d5f6:
    mov.b r0,@(0xa9,gbr)
    .org 0x3d5f8-ORIGIN
L_0003d5f8:
    rts
    .org 0x3d5fa-ORIGIN
L_0003d5fa:
    ldc.l @r15+,gbr
    .org 0x3d5fc-ORIGIN
L_0003d5fc:
    stc.l gbr,@-r15
    .org 0x3d5fe-ORIGIN
L_0003d5fe:
    mov.l P_0003d788,r0
    .org 0x3d600-ORIGIN
L_0003d600:
    ldc r0,gbr
    .org 0x3d602-ORIGIN
L_0003d602:
    mov.b @(0xb2,gbr),r0
    .org 0x3d604-ORIGIN
L_0003d604:
    mov r0,r1
    .org 0x3d606-ORIGIN
L_0003d606:
    mov.b @(0x0,gbr),r0
    .org 0x3d608-ORIGIN
L_0003d608:
    and 0x40,r0
    .org 0x3d60a-ORIGIN
L_0003d60a:
    mov r0,r4
    .org 0x3d60c-ORIGIN
L_0003d60c:
    mov.b @(0x2,gbr),r0
    .org 0x3d60e-ORIGIN
L_0003d60e:
    tst 0x40,r0
    .org 0x3d610-ORIGIN
L_0003d610:
    bt L_0003d61c
    .org 0x3d612-ORIGIN
L_0003d612:
    tst r4,r4
    .org 0x3d614-ORIGIN
L_0003d614:
    bf L_0003d61c
    .org 0x3d616-ORIGIN
L_0003d616:
    mov r1,r0
    .org 0x3d618-ORIGIN
L_0003d618:
    bra L_0003d624
    .org 0x3d61a-ORIGIN
L_0003d61a:
    or 0x20,r0
    .org 0x3d61c-ORIGIN
L_0003d61c:
    tst r4,r4
    .org 0x3d61e-ORIGIN
L_0003d61e:
    bt L_0003d626
    .org 0x3d620-ORIGIN
L_0003d620:
    mov r1,r0
    .org 0x3d622-ORIGIN
L_0003d622:
    and 0xdf,r0
    .org 0x3d624-ORIGIN
L_0003d624:
    mov.b r0,@(0xb2,gbr)
    .org 0x3d626-ORIGIN
L_0003d626:
    mov.b @(0xb2,gbr),r0
    .org 0x3d628-ORIGIN
L_0003d628:
    tst 0x20,r0
    .org 0x3d62a-ORIGIN
L_0003d62a:
    bt L_0003d63e
    .org 0x3d62c-ORIGIN
L_0003d62c:
    mov.l P_0003d78c,r6
    .org 0x3d62e-ORIGIN
L_0003d62e:
    mov #0x6f,r0
    .org 0x3d630-ORIGIN
L_0003d630:
    mov.b @(r0,r6),r2
    .org 0x3d632-ORIGIN
L_0003d632:
    tst r2,r2
    .org 0x3d634-ORIGIN
L_0003d634:
    bf L_0003d64e
    .org 0x3d636-ORIGIN
L_0003d636:
    mov #-0x4d,r2
    .org 0x3d638-ORIGIN
L_0003d638:
    extu.b r2,r0
    .org 0x3d63a-ORIGIN
L_0003d63a:
    bra L_0003d64e
    .org 0x3d63c-ORIGIN
L_0003d63c:
    or.b 0x20,@(r0,gbr)
    .org 0x3d63e-ORIGIN
L_0003d63e:
    mov.l P_0003d790,r6
    .org 0x3d640-ORIGIN
L_0003d640:
    mov #-0x4d,r2
    .org 0x3d642-ORIGIN
L_0003d642:
    extu.b r2,r0
    .org 0x3d644-ORIGIN
L_0003d644:
    mov.b @r6,r2
    .org 0x3d646-ORIGIN
L_0003d646:
    mov.l P_0003d78c,r6
    .org 0x3d648-ORIGIN
L_0003d648:
    and.b 0xdf,@(r0,gbr)
    .org 0x3d64a-ORIGIN
L_0003d64a:
    mov #0x6f,r0
    .org 0x3d64c-ORIGIN
L_0003d64c:
    mov.b r2,@(r0,r6)
    .org 0x3d64e-ORIGIN
L_0003d64e:
    rts
    .org 0x3d650-ORIGIN
L_0003d650:
    ldc.l @r15+,gbr
    .org 0x3d652-ORIGIN
P_0003d652:
    .word 0x0581
    .org 0x3d654-ORIGIN
P_0003d654:
    .word 0x0582
    .org 0x3d656-ORIGIN
P_0003d656:
    .word 0x0583
    .org 0x3d658-ORIGIN
P_0003d658:
    .word 0x0584
    .org 0x3d65a-ORIGIN
P_0003d65a:
    .word 0x0585
    .org 0x3d65c-ORIGIN
P_0003d65c:
    .word 0x0586
    .org 0x3d65e-ORIGIN
P_0003d65e:
    .word 0x0587
    .org 0x3d660-ORIGIN
P_0003d660:
    .word 0x84c3
    .org 0x3d662-ORIGIN
P_0003d662:
    .word 0x039e
    .org 0x3d664-ORIGIN
L_0003d664:
    mov.l P_0003d794,r4
    .org 0x3d666-ORIGIN
L_0003d666:
    mov.l P_0003d798,r2
    .org 0x3d668-ORIGIN
L_0003d668:
    mov.b @(0x1,r4),r0
    .org 0x3d66a-ORIGIN
L_0003d66a:
    extu.b r0,r6
    .org 0x3d66c-ORIGIN
L_0003d66c:
    mov.b @(0x7,r2),r0
    .org 0x3d66e-ORIGIN
L_0003d66e:
    extu.b r0,r5
    .org 0x3d670-ORIGIN
L_0003d670:
    cmp/gt r5,r6
    .org 0x3d672-ORIGIN
L_0003d672:
    bt L_0003d6be
    .org 0x3d674-ORIGIN
L_0003d674:
    mov.b @r4,r2
    .org 0x3d676-ORIGIN
L_0003d676:
    extu.b r2,r2
    .org 0x3d678-ORIGIN
L_0003d678:
    cmp/gt r2,r5
    .org 0x3d67a-ORIGIN
L_0003d67a:
    bt L_0003d6be
    .org 0x3d67c-ORIGIN
L_0003d67c:
    mov.l P_0003d770,r5
    .org 0x3d67e-ORIGIN
L_0003d67e:
    mov #0x1d,r0
    .org 0x3d680-ORIGIN
L_0003d680:
    mov.b @(r0,r5),r0
    .org 0x3d682-ORIGIN
L_0003d682:
    tst 0x1,r0
    .org 0x3d684-ORIGIN
L_0003d684:
    bt L_0003d6be
    .org 0x3d686-ORIGIN
L_0003d686:
    mov.l P_0003d778,r7
    .org 0x3d688-ORIGIN
L_0003d688:
    mov.w P_0003d768,r0
    .org 0x3d68a-ORIGIN
L_0003d68a:
    mov.l P_0003d79c,r4
    .org 0x3d68c-ORIGIN
L_0003d68c:
    mov.b @(r0,r7),r6
    .org 0x3d68e-ORIGIN
L_0003d68e:
    mov.b @r4,r2
    .org 0x3d690-ORIGIN
L_0003d690:
    cmp/hs r2,r6
    .org 0x3d692-ORIGIN
L_0003d692:
    bt L_0003d6be
    .org 0x3d694-ORIGIN
L_0003d694:
    mov #0x1b,r0
    .org 0x3d696-ORIGIN
L_0003d696:
    mov.b @(r0,r5),r0
    .org 0x3d698-ORIGIN
L_0003d698:
    tst 0x20,r0
    .org 0x3d69a-ORIGIN
L_0003d69a:
    bt L_0003d6be
    .org 0x3d69c-ORIGIN
L_0003d69c:
    mov.w P_0003d76a,r6
    .org 0x3d69e-ORIGIN
L_0003d69e:
    mov.b @r6,r0
    .org 0x3d6a0-ORIGIN
L_0003d6a0:
    tst 0x20,r0
    .org 0x3d6a2-ORIGIN
L_0003d6a2:
    bt L_0003d6be
    .org 0x3d6a4-ORIGIN
L_0003d6a4:
    mov.w P_0003d76c,r0
    .org 0x3d6a6-ORIGIN
L_0003d6a6:
    mov #-0x1,r5
    .org 0x3d6a8-ORIGIN
L_0003d6a8:
    extu.b r5,r2
    .org 0x3d6aa-ORIGIN
L_0003d6aa:
    mov.b @(r0,r7),r6
    .org 0x3d6ac-ORIGIN
L_0003d6ac:
    extu.b r6,r6
    .org 0x3d6ae-ORIGIN
L_0003d6ae:
    add 0x1,r6
    .org 0x3d6b0-ORIGIN
L_0003d6b0:
    extu.w r6,r6
    .org 0x3d6b2-ORIGIN
L_0003d6b2:
    cmp/gt r2,r6
    .org 0x3d6b4-ORIGIN
L_0003d6b4:
    bt L_0003d6b8
    .org 0x3d6b6-ORIGIN
L_0003d6b6:
    mov r6,r2
    .org 0x3d6b8-ORIGIN
L_0003d6b8:
    mov.w P_0003d76c,r0
    .org 0x3d6ba-ORIGIN
L_0003d6ba:
    rts
    .org 0x3d6bc-ORIGIN
L_0003d6bc:
    mov.b r2,@(r0,r7)
    .org 0x3d6be-ORIGIN
L_0003d6be:
    rts
    .org 0x3d6c0-ORIGIN
L_0003d6c0:
    nop
    .org 0x3d6c2-ORIGIN
L_0003d6c2:
    stc.l gbr,@-r15
    .org 0x3d6c4-ORIGIN
L_0003d6c4:
    mov.l P_0003d770,r0
    .org 0x3d6c6-ORIGIN
L_0003d6c6:
    ldc r0,gbr
    .org 0x3d6c8-ORIGIN
L_0003d6c8:
    mov.b @(0x11,gbr),r0
    .org 0x3d6ca-ORIGIN
L_0003d6ca:
    tst 0x8,r0
    .org 0x3d6cc-ORIGIN
L_0003d6cc:
    bf/s L_0003d6ea
    .org 0x3d6ce-ORIGIN
L_0003d6ce:
    mov r0,r5
    .org 0x3d6d0-ORIGIN
L_0003d6d0:
    mov.l P_0003d77c,r2
    .org 0x3d6d2-ORIGIN
L_0003d6d2:
    mov #0x7a,r0
    .org 0x3d6d4-ORIGIN
L_0003d6d4:
    mov.l P_0003d780,r4
    .org 0x3d6d6-ORIGIN
L_0003d6d6:
    mov.b @(r0,r2),r6
    .org 0x3d6d8-ORIGIN
L_0003d6d8:
    mov.b @r4,r2
    .org 0x3d6da-ORIGIN
L_0003d6da:
    cmp/hs r2,r6
    .org 0x3d6dc-ORIGIN
L_0003d6dc:
    bf L_0003d6fe
    .org 0x3d6de-ORIGIN
L_0003d6de:
    mov r5,r0
    .org 0x3d6e0-ORIGIN
L_0003d6e0:
    and 0xef,r0
    .org 0x3d6e2-ORIGIN
L_0003d6e2:
    mov.b r0,@(0x11,gbr)
    .org 0x3d6e4-ORIGIN
L_0003d6e4:
    mov #0x11,r0
    .org 0x3d6e6-ORIGIN
L_0003d6e6:
    bra L_0003d6fe
    .org 0x3d6e8-ORIGIN
L_0003d6e8:
    or.b 0x8,@(r0,gbr)
    .org 0x3d6ea-ORIGIN
L_0003d6ea:
    mov.l P_0003d778,r2
    .org 0x3d6ec-ORIGIN
L_0003d6ec:
    mov.w P_0003d76c,r0
    .org 0x3d6ee-ORIGIN
L_0003d6ee:
    mov.l P_0003d7a0,r4
    .org 0x3d6f0-ORIGIN
L_0003d6f0:
    mov.b @(r0,r2),r6
    .org 0x3d6f2-ORIGIN
L_0003d6f2:
    mov.b @r4,r2
    .org 0x3d6f4-ORIGIN
L_0003d6f4:
    cmp/hs r2,r6
    .org 0x3d6f6-ORIGIN
L_0003d6f6:
    bf L_0003d6fe
    .org 0x3d6f8-ORIGIN
L_0003d6f8:
    mov r5,r0
    .org 0x3d6fa-ORIGIN
L_0003d6fa:
    or 0x10,r0
    .org 0x3d6fc-ORIGIN
L_0003d6fc:
    mov.b r0,@(0x11,gbr)
    .org 0x3d6fe-ORIGIN
L_0003d6fe:
    rts
    .org 0x3d700-ORIGIN
L_0003d700:
    ldc.l @r15+,gbr
    .org 0x3d702-ORIGIN
L_0003d702:
    stc.l gbr,@-r15
    .org 0x3d704-ORIGIN
L_0003d704:
    mov.l P_0003d774,r0
    .org 0x3d706-ORIGIN
L_0003d706:
    ldc r0,gbr
    .org 0x3d708-ORIGIN
L_0003d708:
    mov.l P_0003d7a4,r2
    .org 0x3d70a-ORIGIN
L_0003d70a:
    mov #0x18,r0
    .org 0x3d70c-ORIGIN
L_0003d70c:
    mov.b @(r0,r2),r4
    .org 0x3d70e-ORIGIN
L_0003d70e:
    mov.l P_0003d798,r2
    .org 0x3d710-ORIGIN
L_0003d710:
    extu.b r4,r4
    .org 0x3d712-ORIGIN
L_0003d712:
    mov.b @(0x4,r2),r0
    .org 0x3d714-ORIGIN
L_0003d714:
    extu.b r0,r6
    .org 0x3d716-ORIGIN
L_0003d716:
    cmp/gt r6,r4
    .org 0x3d718-ORIGIN
L_0003d718:
    bf/s L_0003d720
    .org 0x3d71a-ORIGIN
L_0003d71a:
    sub r6,r4
    .org 0x3d71c-ORIGIN
L_0003d71c:
    bra L_0003d724
    .org 0x3d71e-ORIGIN
L_0003d71e:
    mov r4,r5
    .org 0x3d720-ORIGIN
L_0003d720:
    extu.b r4,r4
    .org 0x3d722-ORIGIN
L_0003d722:
    neg r4,r5
    .org 0x3d724-ORIGIN
L_0003d724:
    mov.l P_0003d7a8,r4
    .org 0x3d726-ORIGIN
L_0003d726:
    mov.b @r4,r2
    .org 0x3d728-ORIGIN
L_0003d728:
    extu.b r2,r2
    .org 0x3d72a-ORIGIN
L_0003d72a:
    cmp/ge r2,r6
    .org 0x3d72c-ORIGIN
L_0003d72c:
    bt L_0003d74c
    .org 0x3d72e-ORIGIN
L_0003d72e:
    mov.l P_0003d7ac,r6
    .org 0x3d730-ORIGIN
L_0003d730:
    extu.b r5,r5
    .org 0x3d732-ORIGIN
L_0003d732:
    mov.b @r6,r2
    .org 0x3d734-ORIGIN
L_0003d734:
    extu.b r2,r2
    .org 0x3d736-ORIGIN
L_0003d736:
    cmp/ge r2,r5
    .org 0x3d738-ORIGIN
L_0003d738:
    bt L_0003d74c
    .org 0x3d73a-ORIGIN
L_0003d73a:
    mov.l P_0003d7b0,r2
    .org 0x3d73c-ORIGIN
L_0003d73c:
    mov.b @(0xbe,gbr),r0
    .org 0x3d73e-ORIGIN
L_0003d73e:
    mov.b @r2,r4
    .org 0x3d740-ORIGIN
L_0003d740:
    extu.b r0,r5
    .org 0x3d742-ORIGIN
L_0003d742:
    extu.b r4,r4
    .org 0x3d744-ORIGIN
L_0003d744:
    cmp/gt r4,r5
    .org 0x3d746-ORIGIN
L_0003d746:
    bt L_0003d75a
    .org 0x3d748-ORIGIN
L_0003d748:
    bra L_0003d760
    .org 0x3d74a-ORIGIN
L_0003d74a:
    nop
    .org 0x3d74c-ORIGIN
L_0003d74c:
    mov.b @(0xbe,gbr),r0
    .org 0x3d74e-ORIGIN
L_0003d74e:
    mov.l P_0003d7b0,r2
    .org 0x3d750-ORIGIN
L_0003d750:
    extu.b r0,r5
    .org 0x3d752-ORIGIN
L_0003d752:
    mov.b @(0x1,r2),r0
    .org 0x3d754-ORIGIN
L_0003d754:
    extu.b r0,r4
    .org 0x3d756-ORIGIN
L_0003d756:
    cmp/gt r4,r5
    .org 0x3d758-ORIGIN
L_0003d758:
    bf L_0003d760
    .org 0x3d75a-ORIGIN
L_0003d75a:
    sub r4,r5
    .org 0x3d75c-ORIGIN
L_0003d75c:
    bra L_0003d762
    .org 0x3d75e-ORIGIN
L_0003d75e:
    mov r5,r0
    .org 0x3d760-ORIGIN
L_0003d760:
    mov #0x0,r0
    .org 0x3d762-ORIGIN
L_0003d762:
    mov.b r0,@(0xbc,gbr)
    .org 0x3d764-ORIGIN
L_0003d764:
    rts
    .org 0x3d766-ORIGIN
L_0003d766:
    ldc.l @r15+,gbr
    .org 0x3d768-ORIGIN
P_0003d768:
    .word 0x039e
    .org 0x3d76a-ORIGIN
P_0003d76a:
    .word 0x84c3
    .org 0x3d76c-ORIGIN
P_0003d76c:
    .word 0x038e
    .org 0x3d770-ORIGIN
P_0003d770:
    .long 0xffff421d
    .org 0x3d774-ORIGIN
P_0003d774:
    .long 0xffff277e
    .org 0x3d778-ORIGIN
P_0003d778:
    .long 0xffff39c4
    .org 0x3d77c-ORIGIN
P_0003d77c:
    .long 0xffff1114
    .org 0x3d780-ORIGIN
P_0003d780:
    .long 0x00008dc8
    .org 0x3d784-ORIGIN
P_0003d784:
    .long 0x00008c5d
    .org 0x3d788-ORIGIN
P_0003d788:
    .long 0xffff4185
    .org 0x3d78c-ORIGIN
P_0003d78c:
    .long 0xffff4258
    .org 0x3d790-ORIGIN
P_0003d790:
    .long 0x00008c5e
    .org 0x3d794-ORIGIN
P_0003d794:
    .long 0x00008d26
    .org 0x3d798-ORIGIN
P_0003d798:
    .long 0xffff1072
    .org 0x3d79c-ORIGIN
P_0003d79c:
    .long 0x00008424
    .org 0x3d7a0-ORIGIN
P_0003d7a0:
    .long 0x000083ee
    .org 0x3d7a4-ORIGIN
P_0003d7a4:
    .long 0xffff4534
    .org 0x3d7a8-ORIGIN
P_0003d7a8:
    .long 0x00008cef
    .org 0x3d7ac-ORIGIN
P_0003d7ac:
    .long 0x00008cce
    .org 0x3d7b0-ORIGIN
P_0003d7b0:
    .long 0x00008b5b
    .org 0x3d7b4-ORIGIN
L_0003d7b4:
    mov.l P_0003d8e0,r5
    .org 0x3d7b6-ORIGIN
L_0003d7b6:
    mov #0x1a,r0
    .org 0x3d7b8-ORIGIN
L_0003d7b8:
    mov.b @(r0,r5),r6
    .org 0x3d7ba-ORIGIN
L_0003d7ba:
    mov r6,r0
    .org 0x3d7bc-ORIGIN
L_0003d7bc:
    tst 0x2,r0
    .org 0x3d7be-ORIGIN
L_0003d7be:
    bf L_0003d7d6
    .org 0x3d7c0-ORIGIN
L_0003d7c0:
    mov.l P_0003d8e4,r4
    .org 0x3d7c2-ORIGIN
L_0003d7c2:
    mov #-0x47,r0
    .org 0x3d7c4-ORIGIN
L_0003d7c4:
    extu.b r0,r0
    .org 0x3d7c6-ORIGIN
L_0003d7c6:
    mov.b @(r0,r4),r2
    .org 0x3d7c8-ORIGIN
L_0003d7c8:
    mov #-0x44,r0
    .org 0x3d7ca-ORIGIN
L_0003d7ca:
    extu.b r0,r0
    .org 0x3d7cc-ORIGIN
L_0003d7cc:
    mov.b r2,@(r0,r4)
    .org 0x3d7ce-ORIGIN
L_0003d7ce:
    mov #0x2,r0
    .org 0x3d7d0-ORIGIN
L_0003d7d0:
    or r0,r6
    .org 0x3d7d2-ORIGIN
L_0003d7d2:
    mov #0x1a,r0
    .org 0x3d7d4-ORIGIN
L_0003d7d4:
    mov.b r6,@(r0,r5)
    .org 0x3d7d6-ORIGIN
L_0003d7d6:
    bra L_0003d702
    .org 0x3d7d8-ORIGIN
L_0003d7d8:
    nop
    .org 0x3d7da-ORIGIN
L_0003d7da:
    mov.l P_0003d8e0,r1
    .org 0x3d7dc-ORIGIN
L_0003d7dc:
    mov #0x1a,r0
    .org 0x3d7de-ORIGIN
L_0003d7de:
    mov.b @(r0,r1),r5
    .org 0x3d7e0-ORIGIN
L_0003d7e0:
    mov r5,r0
    .org 0x3d7e2-ORIGIN
L_0003d7e2:
    tst 0x4,r0
    .org 0x3d7e4-ORIGIN
L_0003d7e4:
    bf L_0003d810
    .org 0x3d7e6-ORIGIN
L_0003d7e6:
    mov.l P_0003d8e8,r2
    .org 0x3d7e8-ORIGIN
L_0003d7e8:
    mov #0x18,r0
    .org 0x3d7ea-ORIGIN
L_0003d7ea:
    mov.l P_0003d8e4,r6
    .org 0x3d7ec-ORIGIN
L_0003d7ec:
    mov.b @(r0,r2),r7
    .org 0x3d7ee-ORIGIN
L_0003d7ee:
    mov #0x56,r0
    .org 0x3d7f0-ORIGIN
L_0003d7f0:
    mov.l P_0003d8ec,r2
    .org 0x3d7f2-ORIGIN
L_0003d7f2:
    extu.b r7,r7
    .org 0x3d7f4-ORIGIN
L_0003d7f4:
    mov.b @(r0,r2),r4
    .org 0x3d7f6-ORIGIN
L_0003d7f6:
    mov #-0x41,r0
    .org 0x3d7f8-ORIGIN
L_0003d7f8:
    extu.b r4,r4
    .org 0x3d7fa-ORIGIN
L_0003d7fa:
    cmp/ge r4,r7
    .org 0x3d7fc-ORIGIN
L_0003d7fc:
    bf/s L_0003d804
    .org 0x3d7fe-ORIGIN
L_0003d7fe:
    extu.b r0,r0
    .org 0x3d800-ORIGIN
L_0003d800:
    bra L_0003d806
    .org 0x3d802-ORIGIN
L_0003d802:
    mov.b r4,@(r0,r6)
    .org 0x3d804-ORIGIN
L_0003d804:
    mov.b r7,@(r0,r6)
    .org 0x3d806-ORIGIN
L_0003d806:
    mov #0x4,r0
    .org 0x3d808-ORIGIN
L_0003d808:
    or r0,r5
    .org 0x3d80a-ORIGIN
L_0003d80a:
    mov #0x1a,r0
    .org 0x3d80c-ORIGIN
L_0003d80c:
    rts
    .org 0x3d80e-ORIGIN
L_0003d80e:
    mov.b r5,@(r0,r1)
    .org 0x3d810-ORIGIN
L_0003d810:
    rts
    .org 0x3d812-ORIGIN
L_0003d812:
    nop
    .org 0x3d814-ORIGIN
L_0003d814:
    mov.l P_0003d8e0,r6
    .org 0x3d816-ORIGIN
L_0003d816:
    mov #0x11,r0
    .org 0x3d818-ORIGIN
L_0003d818:
    mov.b @(r0,r6),r0
    .org 0x3d81a-ORIGIN
L_0003d81a:
    tst 0x10,r0
    .org 0x3d81c-ORIGIN
L_0003d81c:
    bt L_0003d82e
    .org 0x3d81e-ORIGIN
L_0003d81e:
    mov.l P_0003d8e4,r6
    .org 0x3d820-ORIGIN
L_0003d820:
    mov #-0x44,r0
    .org 0x3d822-ORIGIN
L_0003d822:
    extu.b r0,r0
    .org 0x3d824-ORIGIN
L_0003d824:
    mov.b @(r0,r6),r2
    .org 0x3d826-ORIGIN
L_0003d826:
    mov #0x56,r0
    .org 0x3d828-ORIGIN
L_0003d828:
    mov.l P_0003d8ec,r6
    .org 0x3d82a-ORIGIN
L_0003d82a:
    rts
    .org 0x3d82c-ORIGIN
L_0003d82c:
    mov.b r2,@(r0,r6)
    .org 0x3d82e-ORIGIN
L_0003d82e:
    rts
    .org 0x3d830-ORIGIN
L_0003d830:
    nop
    .org 0x3d832-ORIGIN
L_0003d832:
    mov.l r12,@-r15
    .org 0x3d834-ORIGIN
L_0003d834:
    mov.l r13,@-r15
    .org 0x3d836-ORIGIN
L_0003d836:
    mov.l r14,@-r15
    .org 0x3d838-ORIGIN
L_0003d838:
    sts.l pr,@-r15
    .org 0x3d83a-ORIGIN
L_0003d83a:
    stc.l gbr,@-r15
    .org 0x3d83c-ORIGIN
L_0003d83c:
    mov.l P_0003d8e4,r0
    .org 0x3d83e-ORIGIN
L_0003d83e:
    ldc r0,gbr
    .org 0x3d840-ORIGIN
L_0003d840:
    mov #0x0,r13
    .org 0x3d842-ORIGIN
L_0003d842:
    mov.l P_0003d8f0,r14
    .org 0x3d844-ORIGIN
L_0003d844:
    mov r13,r4
    .org 0x3d846-ORIGIN
L_0003d846:
    bsr L_0003d258
    .org 0x3d848-ORIGIN
L_0003d848:
    mov #0x1,r12
    .org 0x3d84a-ORIGIN
L_0003d84a:
    bsr L_0003d258
    .org 0x3d84c-ORIGIN
L_0003d84c:
    mov r12,r4
    .org 0x3d84e-ORIGIN
L_0003d84e:
    mov.w @(0xb4,gbr),r0
    .org 0x3d850-ORIGIN
L_0003d850:
    mov r13,r4
    .org 0x3d852-ORIGIN
L_0003d852:
    bsr L_0003d2dc
    .org 0x3d854-ORIGIN
L_0003d854:
    mov.w r0,@(0xb2,gbr)
    .org 0x3d856-ORIGIN
L_0003d856:
    bsr L_0003d2dc
    .org 0x3d858-ORIGIN
L_0003d858:
    mov r12,r4
    .org 0x3d85a-ORIGIN
L_0003d85a:
    mov.b @(0xba,gbr),r0
    .org 0x3d85c-ORIGIN
L_0003d85c:
    mov r13,r4
    .org 0x3d85e-ORIGIN
L_0003d85e:
    bsr L_0003d344
    .org 0x3d860-ORIGIN
L_0003d860:
    mov.b r0,@(0xb9,gbr)
    .org 0x3d862-ORIGIN
L_0003d862:
    bsr L_0003d344
    .org 0x3d864-ORIGIN
L_0003d864:
    mov r12,r4
    .org 0x3d866-ORIGIN
L_0003d866:
    mov.l P_0003d8f4,r6
    .org 0x3d868-ORIGIN
L_0003d868:
    mov #0x61,r0
    .org 0x3d86a-ORIGIN
L_0003d86a:
    mov r13,r4
    .org 0x3d86c-ORIGIN
L_0003d86c:
    mov.b @(r0,r6),r2
    .org 0x3d86e-ORIGIN
L_0003d86e:
    mov #0x60,r0
    .org 0x3d870-ORIGIN
L_0003d870:
    bsr L_0003d3ae
    .org 0x3d872-ORIGIN
L_0003d872:
    mov.b r2,@(r0,r6)
    .org 0x3d874-ORIGIN
L_0003d874:
    bsr L_0003d3ae
    .org 0x3d876-ORIGIN
L_0003d876:
    mov r12,r4
    .org 0x3d878-ORIGIN
L_0003d878:
    mov.w P_0003d8d8,r0
    .org 0x3d87a-ORIGIN
L_0003d87a:
    mov r13,r4
    .org 0x3d87c-ORIGIN
L_0003d87c:
    mov.b @(r0,r14),r0
    .org 0x3d87e-ORIGIN
L_0003d87e:
    bsr L_0003d41c
    .org 0x3d880-ORIGIN
L_0003d880:
    mov.b r0,@(0xb8,gbr)
    .org 0x3d882-ORIGIN
L_0003d882:
    bsr L_0003d41c
    .org 0x3d884-ORIGIN
L_0003d884:
    mov r12,r4
    .org 0x3d886-ORIGIN
L_0003d886:
    mov.l P_0003d8ec,r6
    .org 0x3d888-ORIGIN
L_0003d888:
    mov #0x54,r0
    .org 0x3d88a-ORIGIN
L_0003d88a:
    mov r13,r4
    .org 0x3d88c-ORIGIN
L_0003d88c:
    mov.b @(r0,r6),r2
    .org 0x3d88e-ORIGIN
L_0003d88e:
    mov #0x18,r0
    .org 0x3d890-ORIGIN
L_0003d890:
    mov.l P_0003d8e8,r6
    .org 0x3d892-ORIGIN
L_0003d892:
    bsr L_0003d45c
    .org 0x3d894-ORIGIN
L_0003d894:
    mov.b r2,@(r0,r6)
    .org 0x3d896-ORIGIN
L_0003d896:
    bsr L_0003d45c
    .org 0x3d898-ORIGIN
L_0003d898:
    mov r12,r4
    .org 0x3d89a-ORIGIN
L_0003d89a:
    mov.w P_0003d8da,r0
    .org 0x3d89c-ORIGIN
L_0003d89c:
    mov.b @(r0,r14),r0
    .org 0x3d89e-ORIGIN
L_0003d89e:
    bsr L_0003d528
    .org 0x3d8a0-ORIGIN
L_0003d8a0:
    mov.b r0,@(0xbe,gbr)
    .org 0x3d8a2-ORIGIN
L_0003d8a2:
    bsr L_0003d5c4
    .org 0x3d8a4-ORIGIN
L_0003d8a4:
    nop
    .org 0x3d8a6-ORIGIN
L_0003d8a6:
    bsr L_0003d5fc
    .org 0x3d8a8-ORIGIN
L_0003d8a8:
    nop
    .org 0x3d8aa-ORIGIN
L_0003d8aa:
    bsr L_0003d664
    .org 0x3d8ac-ORIGIN
L_0003d8ac:
    nop
    .org 0x3d8ae-ORIGIN
L_0003d8ae:
    bsr L_0003d6c2
    .org 0x3d8b0-ORIGIN
L_0003d8b0:
    nop
    .org 0x3d8b2-ORIGIN
L_0003d8b2:
    bsr L_0003d7b4
    .org 0x3d8b4-ORIGIN
L_0003d8b4:
    nop
    .org 0x3d8b6-ORIGIN
L_0003d8b6:
    bsr L_0003d4a8
    .org 0x3d8b8-ORIGIN
L_0003d8b8:
    mov r13,r4
    .org 0x3d8ba-ORIGIN
L_0003d8ba:
    bsr L_0003d4a8
    .org 0x3d8bc-ORIGIN
L_0003d8bc:
    mov r12,r4
    .org 0x3d8be-ORIGIN
L_0003d8be:
    mov.w P_0003d8dc,r0
    .org 0x3d8c0-ORIGIN
L_0003d8c0:
    mov.b @(r0,r14),r2
    .org 0x3d8c2-ORIGIN
L_0003d8c2:
    mov.w P_0003d8de,r0
    .org 0x3d8c4-ORIGIN
L_0003d8c4:
    bsr L_0003d7da
    .org 0x3d8c6-ORIGIN
L_0003d8c6:
    mov.b r2,@(r0,r14)
    .org 0x3d8c8-ORIGIN
L_0003d8c8:
    bsr L_0003d814
    .org 0x3d8ca-ORIGIN
L_0003d8ca:
    nop
    .org 0x3d8cc-ORIGIN
L_0003d8cc:
    ldc.l @r15+,gbr
    .org 0x3d8ce-ORIGIN
L_0003d8ce:
    lds.l @r15+,pr
    .org 0x3d8d0-ORIGIN
L_0003d8d0:
    mov.l @r15+,r14
    .org 0x3d8d2-ORIGIN
L_0003d8d2:
    mov.l @r15+,r13
    .org 0x3d8d4-ORIGIN
L_0003d8d4:
    rts
    .org 0x3d8d6-ORIGIN
L_0003d8d6:
    mov.l @r15+,r12
    .org 0x3d8d8-ORIGIN
P_0003d8d8:
    .word 0x057b
    .org 0x3d8da-ORIGIN
P_0003d8da:
    .word 0x0588
    .org 0x3d8dc-ORIGIN
P_0003d8dc:
    .word 0x057e
    .org 0x3d8de-ORIGIN
P_0003d8de:
    .word 0x057d
    .org 0x3d8e0-ORIGIN
P_0003d8e0:
    .long 0xffff421d
    .org 0x3d8e4-ORIGIN
P_0003d8e4:
    .long 0xffff277e
    .org 0x3d8e8-ORIGIN
P_0003d8e8:
    .long 0xffff4534
    .org 0x3d8ec-ORIGIN
P_0003d8ec:
    .long 0xffff55bc
    .org 0x3d8f0-ORIGIN
P_0003d8f0:
    .long 0xffff39c4
    .org 0x3d8f4-ORIGIN
P_0003d8f4:
    .long 0xffff1114
