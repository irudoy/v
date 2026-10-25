! Natural signed-curve entry 0007B0A0 and its lookup and signed-division closure.
! RAM pointer literals relocate in the fixture. Instruction words stay stock.
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
    .org 0x266e8-ORIGIN
L_000266e8:
    sts.l pr,@-r15
    .org 0x266ea-ORIGIN
L_000266ea:
    mov.l r4,@-r15
    .org 0x266ec-ORIGIN
L_000266ec:
    mov r5,r0
    .org 0x266ee-ORIGIN
L_000266ee:
    extu.w r6,r5
    .org 0x266f0-ORIGIN
L_000266f0:
    mov.l L_00026710,r7
    .org 0x266f2-ORIGIN
L_000266f2:
    jsr @r7
    .org 0x266f4-ORIGIN
L_000266f4:
    mov #0x1e,r4
    .org 0x266f6-ORIGIN
L_000266f6:
    mov.l @r15+,r6
    .org 0x266f8-ORIGIN
L_000266f8:
    add r4,r6
    .org 0x266fa-ORIGIN
L_000266fa:
    mov.w @(0x2,r6),r0
    .org 0x266fc-ORIGIN
L_000266fc:
    extu.w r0,r2
    .org 0x266fe-ORIGIN
L_000266fe:
    mov r5,r3
    .org 0x26700-ORIGIN
L_00026700:
    mov.w @r6,r1
    .org 0x26702-ORIGIN
L_00026702:
    lds.l @r15+,pr
    .org 0x26704-ORIGIN
L_00026704:
    mov.l L_0002670c,r6
    .org 0x26706-ORIGIN
L_00026706:
    jmp @r6
    .org 0x26708-ORIGIN
L_00026708:
    extu.w r1,r0
    .org 0x2670c-ORIGIN
L_0002670c:
    .long 0x00026af8
    .org 0x26710-ORIGIN
L_00026710:
    .long 0x00026b84
    .org 0x26af8-ORIGIN
L_00026af8:
    cmp/hs r0,r2
    .org 0x26afa-ORIGIN
L_00026afa:
    bt L_00026b14
    .org 0x26afc-ORIGIN
L_00026afc:
    mov.l r0,@-r15
    .org 0x26afe-ORIGIN
L_00026afe:
    sub r2,r0
    .org 0x26b00-ORIGIN
L_00026b00:
    sts macl,r1
    .org 0x26b02-ORIGIN
L_00026b02:
    mul.l r3,r0
    .org 0x26b04-ORIGIN
L_00026b04:
    sts macl,r0
    .org 0x26b06-ORIGIN
L_00026b06:
    lds r1,macl
    .org 0x26b08-ORIGIN
L_00026b08:
    swap.w r0,r0
    .org 0x26b0a-ORIGIN
L_00026b0a:
    mov.l @r15+,r2
    .org 0x26b0c-ORIGIN
L_00026b0c:
    extu.w r0,r0
    .org 0x26b0e-ORIGIN
L_00026b0e:
    sub r0,r2
    .org 0x26b10-ORIGIN
L_00026b10:
    rts
    .org 0x26b12-ORIGIN
L_00026b12:
    mov r2,r0
    .org 0x26b14-ORIGIN
L_00026b14:
    sub r0,r2
    .org 0x26b16-ORIGIN
L_00026b16:
    sts macl,r1
    .org 0x26b18-ORIGIN
L_00026b18:
    mul.l r3,r2
    .org 0x26b1a-ORIGIN
L_00026b1a:
    sts macl,r2
    .org 0x26b1c-ORIGIN
L_00026b1c:
    lds r1,macl
    .org 0x26b1e-ORIGIN
L_00026b1e:
    swap.w r2,r2
    .org 0x26b20-ORIGIN
L_00026b20:
    extu.w r2,r2
    .org 0x26b22-ORIGIN
L_00026b22:
    rts
    .org 0x26b24-ORIGIN
L_00026b24:
    add r2,r0
    .org 0x26b84-ORIGIN
L_00026b84:
    mov r4,r3
    .org 0x26b86-ORIGIN
L_00026b86:
    mov.w @(r0,r4),r1
    .org 0x26b88-ORIGIN
L_00026b88:
    extu.w r1,r1
    .org 0x26b8a-ORIGIN
L_00026b8a:
    cmp/eq r1,r5
    .org 0x26b8c-ORIGIN
L_00026b8c:
    bt L_00026bbc
    .org 0x26b8e-ORIGIN
L_00026b8e:
    cmp/hi r1,r5
    .org 0x26b90-ORIGIN
L_00026b90:
    bf L_00026bb4
    .org 0x26b92-ORIGIN
L_00026b92:
    cmp/eq r4,r3
    .org 0x26b94-ORIGIN
L_00026b94:
    bt L_00026bbc
    .org 0x26b96-ORIGIN
L_00026b96:
    sub r1,r5
    .org 0x26b98-ORIGIN
L_00026b98:
    shll16 r5
    .org 0x26b9a-ORIGIN
L_00026b9a:
    add r4,r0
    .org 0x26b9c-ORIGIN
L_00026b9c:
    mov.w @r0,r1
    .org 0x26b9e-ORIGIN
L_00026b9e:
    mov.w @(0x2,r0),r0
    .org 0x26ba0-ORIGIN
L_00026ba0:
    extu.w r1,r1
    .org 0x26ba2-ORIGIN
L_00026ba2:
    extu.w r0,r0
    .org 0x26ba4-ORIGIN
L_00026ba4:
    sts.l pr,@-r15
    .org 0x26ba6-ORIGIN
L_00026ba6:
    mov.l L_00026bc0,r2
    .org 0x26ba8-ORIGIN
L_00026ba8:
    sub r1,r0
    .org 0x26baa-ORIGIN
L_00026baa:
    jsr @r2
    .org 0x26bac-ORIGIN
L_00026bac:
    mov r5,r1
    .org 0x26bae-ORIGIN
L_00026bae:
    lds.l @r15+,pr
    .org 0x26bb0-ORIGIN
L_00026bb0:
    rts
    .org 0x26bb2-ORIGIN
L_00026bb2:
    mov r0,r5
    .org 0x26bb4-ORIGIN
L_00026bb4:
    add #-0x2,r4
    .org 0x26bb6-ORIGIN
L_00026bb6:
    cmp/pz r4
    .org 0x26bb8-ORIGIN
L_00026bb8:
    bt L_00026b86
    .org 0x26bba-ORIGIN
L_00026bba:
    mov #0x0,r4
    .org 0x26bbc-ORIGIN
L_00026bbc:
    rts
    .org 0x26bbe-ORIGIN
L_00026bbe:
    mov #0x0,r5
    .org 0x26bc0-ORIGIN
L_00026bc0:
    .long 0x00026d10
    .org 0x26d10-ORIGIN
L_00026d10:
    tst r0,r0
    .org 0x26d12-ORIGIN
L_00026d12:
    bt L_00026da2
    .org 0x26d14-ORIGIN
L_00026d14:
    mov.l r2,@-r15
    .org 0x26d16-ORIGIN
L_00026d16:
    mov #0x0,r2
    .org 0x26d18-ORIGIN
L_00026d18:
    div0u
    .org 0x26d1a-ORIGIN
L_00026d1a:
    rotcl r1
    .org 0x26d1c-ORIGIN
L_00026d1c:
    div1 r0,r2
    .org 0x26d1e-ORIGIN
L_00026d1e:
    rotcl r1
    .org 0x26d20-ORIGIN
L_00026d20:
    div1 r0,r2
    .org 0x26d22-ORIGIN
L_00026d22:
    rotcl r1
    .org 0x26d24-ORIGIN
L_00026d24:
    div1 r0,r2
    .org 0x26d26-ORIGIN
L_00026d26:
    rotcl r1
    .org 0x26d28-ORIGIN
L_00026d28:
    div1 r0,r2
    .org 0x26d2a-ORIGIN
L_00026d2a:
    rotcl r1
    .org 0x26d2c-ORIGIN
L_00026d2c:
    div1 r0,r2
    .org 0x26d2e-ORIGIN
L_00026d2e:
    rotcl r1
    .org 0x26d30-ORIGIN
L_00026d30:
    div1 r0,r2
    .org 0x26d32-ORIGIN
L_00026d32:
    rotcl r1
    .org 0x26d34-ORIGIN
L_00026d34:
    div1 r0,r2
    .org 0x26d36-ORIGIN
L_00026d36:
    rotcl r1
    .org 0x26d38-ORIGIN
L_00026d38:
    div1 r0,r2
    .org 0x26d3a-ORIGIN
L_00026d3a:
    rotcl r1
    .org 0x26d3c-ORIGIN
L_00026d3c:
    div1 r0,r2
    .org 0x26d3e-ORIGIN
L_00026d3e:
    rotcl r1
    .org 0x26d40-ORIGIN
L_00026d40:
    div1 r0,r2
    .org 0x26d42-ORIGIN
L_00026d42:
    rotcl r1
    .org 0x26d44-ORIGIN
L_00026d44:
    div1 r0,r2
    .org 0x26d46-ORIGIN
L_00026d46:
    rotcl r1
    .org 0x26d48-ORIGIN
L_00026d48:
    div1 r0,r2
    .org 0x26d4a-ORIGIN
L_00026d4a:
    rotcl r1
    .org 0x26d4c-ORIGIN
L_00026d4c:
    div1 r0,r2
    .org 0x26d4e-ORIGIN
L_00026d4e:
    rotcl r1
    .org 0x26d50-ORIGIN
L_00026d50:
    div1 r0,r2
    .org 0x26d52-ORIGIN
L_00026d52:
    rotcl r1
    .org 0x26d54-ORIGIN
L_00026d54:
    div1 r0,r2
    .org 0x26d56-ORIGIN
L_00026d56:
    rotcl r1
    .org 0x26d58-ORIGIN
L_00026d58:
    div1 r0,r2
    .org 0x26d5a-ORIGIN
L_00026d5a:
    rotcl r1
    .org 0x26d5c-ORIGIN
L_00026d5c:
    div1 r0,r2
    .org 0x26d5e-ORIGIN
L_00026d5e:
    rotcl r1
    .org 0x26d60-ORIGIN
L_00026d60:
    div1 r0,r2
    .org 0x26d62-ORIGIN
L_00026d62:
    rotcl r1
    .org 0x26d64-ORIGIN
L_00026d64:
    div1 r0,r2
    .org 0x26d66-ORIGIN
L_00026d66:
    rotcl r1
    .org 0x26d68-ORIGIN
L_00026d68:
    div1 r0,r2
    .org 0x26d6a-ORIGIN
L_00026d6a:
    rotcl r1
    .org 0x26d6c-ORIGIN
L_00026d6c:
    div1 r0,r2
    .org 0x26d6e-ORIGIN
L_00026d6e:
    rotcl r1
    .org 0x26d70-ORIGIN
L_00026d70:
    div1 r0,r2
    .org 0x26d72-ORIGIN
L_00026d72:
    rotcl r1
    .org 0x26d74-ORIGIN
L_00026d74:
    div1 r0,r2
    .org 0x26d76-ORIGIN
L_00026d76:
    rotcl r1
    .org 0x26d78-ORIGIN
L_00026d78:
    div1 r0,r2
    .org 0x26d7a-ORIGIN
L_00026d7a:
    rotcl r1
    .org 0x26d7c-ORIGIN
L_00026d7c:
    div1 r0,r2
    .org 0x26d7e-ORIGIN
L_00026d7e:
    rotcl r1
    .org 0x26d80-ORIGIN
L_00026d80:
    div1 r0,r2
    .org 0x26d82-ORIGIN
L_00026d82:
    rotcl r1
    .org 0x26d84-ORIGIN
L_00026d84:
    div1 r0,r2
    .org 0x26d86-ORIGIN
L_00026d86:
    rotcl r1
    .org 0x26d88-ORIGIN
L_00026d88:
    div1 r0,r2
    .org 0x26d8a-ORIGIN
L_00026d8a:
    rotcl r1
    .org 0x26d8c-ORIGIN
L_00026d8c:
    div1 r0,r2
    .org 0x26d8e-ORIGIN
L_00026d8e:
    rotcl r1
    .org 0x26d90-ORIGIN
L_00026d90:
    div1 r0,r2
    .org 0x26d92-ORIGIN
L_00026d92:
    rotcl r1
    .org 0x26d94-ORIGIN
L_00026d94:
    div1 r0,r2
    .org 0x26d96-ORIGIN
L_00026d96:
    rotcl r1
    .org 0x26d98-ORIGIN
L_00026d98:
    div1 r0,r2
    .org 0x26d9a-ORIGIN
L_00026d9a:
    rotcl r1
    .org 0x26d9c-ORIGIN
L_00026d9c:
    mov.l @r15+,r2
    .org 0x26d9e-ORIGIN
L_00026d9e:
    rts
    .org 0x26da0-ORIGIN
L_00026da0:
    mov r1,r0
    .org 0x26da2-ORIGIN
L_00026da2:
    rts
    .org 0x26da4-ORIGIN
L_00026da4:
    mov #0x0,r0
    .org 0x7b0a0-ORIGIN
L_0007b0a0:
    mov.l r8,@-r15
    .org 0x7b0a2-ORIGIN
L_0007b0a2:
    mov.l r9,@-r15
    .org 0x7b0a4-ORIGIN
L_0007b0a4:
    mov.l r10,@-r15
    .org 0x7b0a6-ORIGIN
L_0007b0a6:
    mov.l r11,@-r15
    .org 0x7b0a8-ORIGIN
L_0007b0a8:
    mov.l r12,@-r15
    .org 0x7b0aa-ORIGIN
L_0007b0aa:
    mov.l r13,@-r15
    .org 0x7b0ac-ORIGIN
L_0007b0ac:
    mov.l r14,@-r15
    .org 0x7b0ae-ORIGIN
L_0007b0ae:
    sts.l pr,@-r15
    .org 0x7b0b0-ORIGIN
L_0007b0b0:
    sts.l macl,@-r15
    .org 0x7b0b2-ORIGIN
L_0007b0b2:
    stc.l gbr,@-r15
    .org 0x7b0b4-ORIGIN
L_0007b0b4:
    mov.l L_0007b298,r0
    .org 0x7b0b6-ORIGIN
L_0007b0b6:
    ldc r0,gbr
    .org 0x7b0b8-ORIGIN
L_0007b0b8:
    add #-0xc,r15
    .org 0x7b0ba-ORIGIN
L_0007b0ba:
    mov.l L_0007b29c,r9
    .org 0x7b0bc-ORIGIN
L_0007b0bc:
    mov #0x6b,r0
    .org 0x7b0be-ORIGIN
L_0007b0be:
    mov.b @(r0,r9),r0
    .org 0x7b0c0-ORIGIN
L_0007b0c0:
    tst #0x40,r0
    .org 0x7b0c2-ORIGIN
L_0007b0c2:
    bt L_0007b0ce
    .org 0x7b0c4-ORIGIN
L_0007b0c4:
    mov.l L_0007b298,r14
    .org 0x7b0c6-ORIGIN
L_0007b0c6:
    mov.w L_0007b196,r0
    .org 0x7b0c8-ORIGIN
L_0007b0c8:
    mov.w @(r0,r14),r2
    .org 0x7b0ca-ORIGIN
L_0007b0ca:
    bra L_0007b0d4
    .org 0x7b0cc-ORIGIN
L_0007b0cc:
    mov.w r2,@r15
    .org 0x7b0ce-ORIGIN
L_0007b0ce:
    mov.w @(0x182,gbr),r0
    .org 0x7b0d0-ORIGIN
L_0007b0d0:
    mov.l r0,@(0x8,r15)
    .org 0x7b0d2-ORIGIN
L_0007b0d2:
    mov.w r0,@r15
    .org 0x7b0d4-ORIGIN
L_0007b0d4:
    mov.l L_0007b2a0,r11
    .org 0x7b0d6-ORIGIN
L_0007b0d6:
    mov #0x28,r0
    .org 0x7b0d8-ORIGIN
L_0007b0d8:
    mov.l L_0007b2a4,r4
    .org 0x7b0da-ORIGIN
L_0007b0da:
    mov #-0x80,r14
    .org 0x7b0dc-ORIGIN
L_0007b0dc:
    mov.w @(r0,r11),r2
    .org 0x7b0de-ORIGIN
L_0007b0de:
    shll8 r14
    .org 0x7b0e0-ORIGIN
L_0007b0e0:
    mov.l L_0007b2a8,r5
    .org 0x7b0e2-ORIGIN
L_0007b0e2:
    mov.l L_0007b2ac,r12
    .org 0x7b0e4-ORIGIN
L_0007b0e4:
    jsr @r12
    .org 0x7b0e6-ORIGIN
L_0007b0e6:
    extu.w r2,r6
    .org 0x7b0e8-ORIGIN
L_0007b0e8:
    extu.w r0,r13
    .org 0x7b0ea-ORIGIN
L_0007b0ea:
    mov.l L_0007b2b0,r4
    .org 0x7b0ec-ORIGIN
L_0007b0ec:
    mov #0x28,r0
    .org 0x7b0ee-ORIGIN
L_0007b0ee:
    mov.l L_0007b2a8,r5
    .org 0x7b0f0-ORIGIN
L_0007b0f0:
    mov.w @(r0,r11),r2
    .org 0x7b0f2-ORIGIN
L_0007b0f2:
    add r14,r13
    .org 0x7b0f4-ORIGIN
L_0007b0f4:
    jsr @r12
    .org 0x7b0f6-ORIGIN
L_0007b0f6:
    extu.w r2,r6
    .org 0x7b0f8-ORIGIN
L_0007b0f8:
    extu.w r0,r6
    .org 0x7b0fa-ORIGIN
L_0007b0fa:
    mov.w L_0007b198,r0
    .org 0x7b0fc-ORIGIN
L_0007b0fc:
    add r14,r6
    .org 0x7b0fe-ORIGIN
L_0007b0fe:
    mov.l L_0007b298,r14
    .org 0x7b100-ORIGIN
L_0007b100:
    mov.l L_0007b2b4,r4
    .org 0x7b102-ORIGIN
L_0007b102:
    mov.w @(r0,r14),r5
    .org 0x7b104-ORIGIN
L_0007b104:
    mov #0x6b,r0
    .org 0x7b106-ORIGIN
L_0007b106:
    mov.b @(r0,r9),r8
    .org 0x7b108-ORIGIN
L_0007b108:
    mov #0x6a,r0
    .org 0x7b10a-ORIGIN
L_0007b10a:
    sub r13,r5
    .org 0x7b10c-ORIGIN
L_0007b10c:
    mov.b @(r0,r9),r10
    .org 0x7b10e-ORIGIN
L_0007b10e:
    mov.b @(0x9,r4),r0
    .org 0x7b110-ORIGIN
L_0007b110:
    cmp/pz r5
    .org 0x7b112-ORIGIN
L_0007b112:
    bt/s L_0007b118
    .org 0x7b114-ORIGIN
L_0007b114:
    mov.b r0,@(0x4,r15)
    .org 0x7b116-ORIGIN
L_0007b116:
    mov #0x0,r5
    .org 0x7b118-ORIGIN
L_0007b118:
    mov.l L_0007b298,r3
    .org 0x7b11a-ORIGIN
L_0007b11a:
    mov.w L_0007b19a,r0
    .org 0x7b11c-ORIGIN
L_0007b11c:
    mov.w @(r0,r3),r2
    .org 0x7b11e-ORIGIN
L_0007b11e:
    sub r13,r2
    .org 0x7b120-ORIGIN
L_0007b120:
    cmp/pz r2
    .org 0x7b122-ORIGIN
L_0007b122:
    bt L_0007b126
    .org 0x7b124-ORIGIN
L_0007b124:
    mov #0x0,r2
    .org 0x7b126-ORIGIN
L_0007b126:
    mov.l L_0007b298,r3
    .org 0x7b128-ORIGIN
L_0007b128:
    mov r2,r12
    .org 0x7b12a-ORIGIN
L_0007b12a:
    mov.w L_0007b19c,r0
    .org 0x7b12c-ORIGIN
L_0007b12c:
    mov.w @(r0,r3),r4
    .org 0x7b12e-ORIGIN
L_0007b12e:
    mov r4,r2
    .org 0x7b130-ORIGIN
L_0007b130:
    sub r13,r2
    .org 0x7b132-ORIGIN
L_0007b132:
    cmp/pz r2
    .org 0x7b134-ORIGIN
L_0007b134:
    bt L_0007b138
    .org 0x7b136-ORIGIN
L_0007b136:
    mov #0x0,r2
    .org 0x7b138-ORIGIN
L_0007b138:
    sub r13,r6
    .org 0x7b13a-ORIGIN
L_0007b13a:
    cmp/pz r6
    .org 0x7b13c-ORIGIN
L_0007b13c:
    bt/s L_0007b142
    .org 0x7b13e-ORIGIN
L_0007b13e:
    mov r2,r11
    .org 0x7b140-ORIGIN
L_0007b140:
    mov #0x0,r6
    .org 0x7b142-ORIGIN
L_0007b142:
    tst r6,r6
    .org 0x7b144-ORIGIN
L_0007b144:
    bt/s L_0007b1a6
    .org 0x7b146-ORIGIN
L_0007b146:
    mov r6,r13
    .org 0x7b148-ORIGIN
L_0007b148:
    mov.w L_0007b19e,r14
    .org 0x7b14a-ORIGIN
L_0007b14a:
    mov r13,r0
    .org 0x7b14c-ORIGIN
L_0007b14c:
    mov.l L_0007b2b8,r6
    .org 0x7b14e-ORIGIN
L_0007b14e:
    mul.l r5,r14
    .org 0x7b150-ORIGIN
L_0007b150:
    jsr @r6
    .org 0x7b152-ORIGIN
L_0007b152:
    sts macl,r1
    .org 0x7b154-ORIGIN
L_0007b154:
    cmp/gt r14,r0
    .org 0x7b156-ORIGIN
L_0007b156:
    bf/s L_0007b15c
    .org 0x7b158-ORIGIN
L_0007b158:
    mov r0,r7
    .org 0x7b15a-ORIGIN
L_0007b15a:
    mov r14,r7
    .org 0x7b15c-ORIGIN
L_0007b15c:
    mul.l r12,r14
    .org 0x7b15e-ORIGIN
L_0007b15e:
    mov.l L_0007b298,r3
    .org 0x7b160-ORIGIN
L_0007b160:
    mov.w L_0007b1a0,r0
    .org 0x7b162-ORIGIN
L_0007b162:
    sts macl,r1
    .org 0x7b164-ORIGIN
L_0007b164:
    mov.l L_0007b2b8,r6
    .org 0x7b166-ORIGIN
L_0007b166:
    mov.w r7,@(r0,r3)
    .org 0x7b168-ORIGIN
L_0007b168:
    jsr @r6
    .org 0x7b16a-ORIGIN
L_0007b16a:
    mov r13,r0
    .org 0x7b16c-ORIGIN
L_0007b16c:
    cmp/gt r14,r0
    .org 0x7b16e-ORIGIN
L_0007b16e:
    bf/s L_0007b174
    .org 0x7b170-ORIGIN
L_0007b170:
    mov r0,r4
    .org 0x7b172-ORIGIN
L_0007b172:
    mov r14,r4
    .org 0x7b174-ORIGIN
L_0007b174:
    mul.l r11,r14
    .org 0x7b176-ORIGIN
L_0007b176:
    mov.l L_0007b298,r3
    .org 0x7b178-ORIGIN
L_0007b178:
    mov.w L_0007b1a2,r0
    .org 0x7b17a-ORIGIN
L_0007b17a:
    sts macl,r1
    .org 0x7b17c-ORIGIN
L_0007b17c:
    mov.l L_0007b2b8,r6
    .org 0x7b17e-ORIGIN
L_0007b17e:
    mov.w r4,@(r0,r3)
    .org 0x7b180-ORIGIN
L_0007b180:
    jsr @r6
    .org 0x7b182-ORIGIN
L_0007b182:
    mov r13,r0
    .org 0x7b184-ORIGIN
L_0007b184:
    cmp/gt r14,r0
    .org 0x7b186-ORIGIN
L_0007b186:
    bf/s L_0007b18c
    .org 0x7b188-ORIGIN
L_0007b188:
    mov r0,r6
    .org 0x7b18a-ORIGIN
L_0007b18a:
    mov r14,r6
    .org 0x7b18c-ORIGIN
L_0007b18c:
    mov.l L_0007b298,r3
    .org 0x7b18e-ORIGIN
L_0007b18e:
    mov.w L_0007b1a4,r0
    .org 0x7b190-ORIGIN
L_0007b190:
    mov.w r6,@(r0,r3)
    .org 0x7b192-ORIGIN
L_0007b192:
    bra L_0007b1b6
    .org 0x7b194-ORIGIN
L_0007b194:
    nop
    .org 0x7b196-ORIGIN
L_0007b196:
    .word 0x0cf2
    .org 0x7b198-ORIGIN
L_0007b198:
    .word 0x0a94
    .org 0x7b19a-ORIGIN
L_0007b19a:
    .word 0x0a96
    .org 0x7b19c-ORIGIN
L_0007b19c:
    .word 0x0a9e
    .org 0x7b19e-ORIGIN
L_0007b19e:
    .word 0x0320
    .org 0x7b1a0-ORIGIN
L_0007b1a0:
    .word 0x0d0e
    .org 0x7b1a2-ORIGIN
L_0007b1a2:
    .word 0x0d10
    .org 0x7b1a4-ORIGIN
L_0007b1a4:
    .word 0x0d12
    .org 0x7b1a6-ORIGIN
L_0007b1a6:
    mov.w L_0007b28c,r6
    .org 0x7b1a8-ORIGIN
L_0007b1a8:
    mov.l L_0007b298,r14
    .org 0x7b1aa-ORIGIN
L_0007b1aa:
    mov.w L_0007b28e,r0
    .org 0x7b1ac-ORIGIN
L_0007b1ac:
    mov.w r6,@(r0,r14)
    .org 0x7b1ae-ORIGIN
L_0007b1ae:
    mov.w L_0007b290,r0
    .org 0x7b1b0-ORIGIN
L_0007b1b0:
    mov.w r6,@(r0,r14)
    .org 0x7b1b2-ORIGIN
L_0007b1b2:
    mov.w L_0007b292,r0
    .org 0x7b1b4-ORIGIN
L_0007b1b4:
    mov.w r6,@(r0,r14)
    .org 0x7b1b6-ORIGIN
L_0007b1b6:
    mov.l L_0007b298,r3
    .org 0x7b1b8-ORIGIN
L_0007b1b8:
    mov.w L_0007b28e,r0
    .org 0x7b1ba-ORIGIN
L_0007b1ba:
    mov.w @r15,r2
    .org 0x7b1bc-ORIGIN
L_0007b1bc:
    mov.w @(r0,r3),r7
    .org 0x7b1be-ORIGIN
L_0007b1be:
    extu.w r2,r4
    .org 0x7b1c0-ORIGIN
L_0007b1c0:
    extu.w r7,r2
    .org 0x7b1c2-ORIGIN
L_0007b1c2:
    cmp/ge r2,r4
    .org 0x7b1c4-ORIGIN
L_0007b1c4:
    bf L_0007b1c8
    .org 0x7b1c6-ORIGIN
L_0007b1c6:
    mov.w @r15,r2
    .org 0x7b1c8-ORIGIN
L_0007b1c8:
    mov.l L_0007b298,r3
    .org 0x7b1ca-ORIGIN
L_0007b1ca:
    extu.w r2,r5
    .org 0x7b1cc-ORIGIN
L_0007b1cc:
    mov.w L_0007b290,r0
    .org 0x7b1ce-ORIGIN
L_0007b1ce:
    mov.w @(r0,r3),r4
    .org 0x7b1d0-ORIGIN
L_0007b1d0:
    extu.w r4,r4
    .org 0x7b1d2-ORIGIN
L_0007b1d2:
    cmp/ge r4,r5
    .org 0x7b1d4-ORIGIN
L_0007b1d4:
    bt L_0007b1d8
    .org 0x7b1d6-ORIGIN
L_0007b1d6:
    mov r4,r5
    .org 0x7b1d8-ORIGIN
L_0007b1d8:
    extu.w r5,r5
    .org 0x7b1da-ORIGIN
L_0007b1da:
    extu.w r6,r6
    .org 0x7b1dc-ORIGIN
L_0007b1dc:
    cmp/gt r6,r5
    .org 0x7b1de-ORIGIN
L_0007b1de:
    bf L_0007b1e2
    .org 0x7b1e0-ORIGIN
L_0007b1e0:
    mov r6,r5
    .org 0x7b1e2-ORIGIN
L_0007b1e2:
    extu.w r5,r5
    .org 0x7b1e4-ORIGIN
L_0007b1e4:
    mov r10,r0
    .org 0x7b1e6-ORIGIN
L_0007b1e6:
    cmp/eq r5,r4
    .org 0x7b1e8-ORIGIN
L_0007b1e8:
    bf/s L_0007b1ee
    .org 0x7b1ea-ORIGIN
L_0007b1ea:
    and #0xfd,r0
    .org 0x7b1ec-ORIGIN
L_0007b1ec:
    or #0x2,r0
    .org 0x7b1ee-ORIGIN
L_0007b1ee:
    mov r0,r10
    .org 0x7b1f0-ORIGIN
L_0007b1f0:
    mov #0x6a,r0
    .org 0x7b1f2-ORIGIN
L_0007b1f2:
    cmp/eq r5,r6
    .org 0x7b1f4-ORIGIN
L_0007b1f4:
    mov.b r10,@(r0,r9)
    .org 0x7b1f6-ORIGIN
L_0007b1f6:
    mov r8,r0
    .org 0x7b1f8-ORIGIN
L_0007b1f8:
    bf/s L_0007b1fe
    .org 0x7b1fa-ORIGIN
L_0007b1fa:
    and #0xf7,r0
    .org 0x7b1fc-ORIGIN
L_0007b1fc:
    or #0x8,r0
    .org 0x7b1fe-ORIGIN
L_0007b1fe:
    mov r0,r8
    .org 0x7b200-ORIGIN
L_0007b200:
    mov #0x6b,r0
    .org 0x7b202-ORIGIN
L_0007b202:
    mov.b r8,@(r0,r9)
    .org 0x7b204-ORIGIN
L_0007b204:
    cmp/pl r5
    .org 0x7b206-ORIGIN
L_0007b206:
    mov.b @(r0,r9),r0
    .org 0x7b208-ORIGIN
L_0007b208:
    bt/s L_0007b20e
    .org 0x7b20a-ORIGIN
L_0007b20a:
    and #0xef,r0
    .org 0x7b20c-ORIGIN
L_0007b20c:
    or #0x10,r0
    .org 0x7b20e-ORIGIN
L_0007b20e:
    mov r0,r2
    .org 0x7b210-ORIGIN
L_0007b210:
    mov #0x6b,r0
    .org 0x7b212-ORIGIN
L_0007b212:
    mov.b r2,@(r0,r9)
    .org 0x7b214-ORIGIN
L_0007b214:
    mov.w L_0007b28c,r14
    .org 0x7b216-ORIGIN
L_0007b216:
    mov.b @(r0,r9),r0
    .org 0x7b218-ORIGIN
L_0007b218:
    cmp/ge r14,r5
    .org 0x7b21a-ORIGIN
L_0007b21a:
    bf/s L_0007b220
    .org 0x7b21c-ORIGIN
L_0007b21c:
    and #0xdf,r0
    .org 0x7b21e-ORIGIN
L_0007b21e:
    or #0x20,r0
    .org 0x7b220-ORIGIN
L_0007b220:
    mov r0,r2
    .org 0x7b222-ORIGIN
L_0007b222:
    mov #0x6b,r0
    .org 0x7b224-ORIGIN
L_0007b224:
    mov.b r2,@(r0,r9)
    .org 0x7b226-ORIGIN
L_0007b226:
    mov.l L_0007b2bc,r2
    .org 0x7b228-ORIGIN
L_0007b228:
    mov.b @r2,r0
    .org 0x7b22a-ORIGIN
L_0007b22a:
    tst #0x2,r0
    .org 0x7b22c-ORIGIN
L_0007b22c:
    bt L_0007b24e
    .org 0x7b22e-ORIGIN
L_0007b22e:
    mov.w @r15,r6
    .org 0x7b230-ORIGIN
L_0007b230:
    mov.b @(0x4,r15),r0
    .org 0x7b232-ORIGIN
L_0007b232:
    extu.w r6,r6
    .org 0x7b234-ORIGIN
L_0007b234:
    cmp/eq r5,r6
    .org 0x7b236-ORIGIN
L_0007b236:
    bt/s L_0007b23c
    .org 0x7b238-ORIGIN
L_0007b238:
    and #0xef,r0
    .org 0x7b23a-ORIGIN
L_0007b23a:
    or #0x10,r0
    .org 0x7b23c-ORIGIN
L_0007b23c:
    mov.l L_0007b2b4,r6
    .org 0x7b23e-ORIGIN
L_0007b23e:
    mov.b r0,@(0x4,r15)
    .org 0x7b240-ORIGIN
L_0007b240:
    exts.b r0,r0
    .org 0x7b242-ORIGIN
L_0007b242:
    mov.b r0,@(0x9,r6)
    .org 0x7b244-ORIGIN
L_0007b244:
    mov.l L_0007b298,r3
    .org 0x7b246-ORIGIN
L_0007b246:
    mov.w L_0007b294,r0
    .org 0x7b248-ORIGIN
L_0007b248:
    mov.w r5,@(r0,r3)
    .org 0x7b24a-ORIGIN
L_0007b24a:
    bra L_0007b274
    .org 0x7b24c-ORIGIN
L_0007b24c:
    nop
    .org 0x7b24e-ORIGIN
L_0007b24e:
    mov.l L_0007b2c0,r6
    .org 0x7b250-ORIGIN
L_0007b250:
    mov #0x2b,r0
    .org 0x7b252-ORIGIN
L_0007b252:
    mov.b @(r0,r6),r0
    .org 0x7b254-ORIGIN
L_0007b254:
    tst #0x2,r0
    .org 0x7b256-ORIGIN
L_0007b256:
    mov.b @(0x4,r15),r0
    .org 0x7b258-ORIGIN
L_0007b258:
    bt/s L_0007b25e
    .org 0x7b25a-ORIGIN
L_0007b25a:
    and #0xef,r0
    .org 0x7b25c-ORIGIN
L_0007b25c:
    or #0x10,r0
    .org 0x7b25e-ORIGIN
L_0007b25e:
    mov.l L_0007b2b4,r6
    .org 0x7b260-ORIGIN
L_0007b260:
    mov.b r0,@(0x4,r15)
    .org 0x7b262-ORIGIN
L_0007b262:
    exts.b r0,r0
    .org 0x7b264-ORIGIN
L_0007b264:
    mov.b r0,@(0x9,r6)
    .org 0x7b266-ORIGIN
L_0007b266:
    mov #-0x68,r0
    .org 0x7b268-ORIGIN
L_0007b268:
    mov.l L_0007b2c4,r6
    .org 0x7b26a-ORIGIN
L_0007b26a:
    extu.b r0,r0
    .org 0x7b26c-ORIGIN
L_0007b26c:
    mov.l L_0007b298,r3
    .org 0x7b26e-ORIGIN
L_0007b26e:
    mov.w @(r0,r6),r2
    .org 0x7b270-ORIGIN
L_0007b270:
    mov.w L_0007b294,r0
    .org 0x7b272-ORIGIN
L_0007b272:
    mov.w r2,@(r0,r3)
    .org 0x7b274-ORIGIN
L_0007b274:
    add #0xc,r15
    .org 0x7b276-ORIGIN
L_0007b276:
    ldc.l @r15+,gbr
    .org 0x7b278-ORIGIN
L_0007b278:
    lds.l @r15+,macl
    .org 0x7b27a-ORIGIN
L_0007b27a:
    lds.l @r15+,pr
    .org 0x7b27c-ORIGIN
L_0007b27c:
    mov.l @r15+,r14
    .org 0x7b27e-ORIGIN
L_0007b27e:
    mov.l @r15+,r13
    .org 0x7b280-ORIGIN
L_0007b280:
    mov.l @r15+,r12
    .org 0x7b282-ORIGIN
L_0007b282:
    mov.l @r15+,r11
    .org 0x7b284-ORIGIN
L_0007b284:
    mov.l @r15+,r10
    .org 0x7b286-ORIGIN
L_0007b286:
    mov.l @r15+,r9
    .org 0x7b288-ORIGIN
L_0007b288:
    rts
    .org 0x7b28a-ORIGIN
L_0007b28a:
    mov.l @r15+,r8
    .org 0x7b28c-ORIGIN
L_0007b28c:
    .word 0x0320
    .org 0x7b28e-ORIGIN
L_0007b28e:
    .word 0x0d0e
    .org 0x7b290-ORIGIN
L_0007b290:
    .word 0x0d10
    .org 0x7b292-ORIGIN
L_0007b292:
    .word 0x0d12
    .org 0x7b294-ORIGIN
L_0007b294:
    .word 0x0cd6
    .org 0x7b298-ORIGIN
L_0007b298:
    .long 0xffff28f8
    .org 0x7b29c-ORIGIN
L_0007b29c:
    .long 0xffff41a9
    .org 0x7b2a0-ORIGIN
L_0007b2a0:
    .long 0xffff1094
    .org 0x7b2a4-ORIGIN
L_0007b2a4:
    .long 0x00018e06
    .org 0x7b2a8-ORIGIN
L_0007b2a8:
    .long 0x00018e26
    .org 0x7b2ac-ORIGIN
L_0007b2ac:
    .long 0x000266e8
    .org 0x7b2b0-ORIGIN
L_0007b2b0:
    .long 0x00018de6
    .org 0x7b2b4-ORIGIN
L_0007b2b4:
    .long 0xffff424c
    .org 0x7b2b8-ORIGIN
L_0007b2b8:
    .long 0x00021bbc
    .org 0x7b2bc-ORIGIN
L_0007b2bc:
    .long 0x000083c1
    .org 0x7b2c0-ORIGIN
L_0007b2c0:
    .long 0xffff2470
    .org 0x7b2c4-ORIGIN
L_0007b2c4:
    .long 0xffff267a
