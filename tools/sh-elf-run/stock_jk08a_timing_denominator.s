! Natural denominator entries 0007B2C8 and 0007B3F4 with their lookup and division closure.
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
    .org 0x262a8-ORIGIN
L_000262a8:
    sts.l pr,@-r15
    .org 0x262aa-ORIGIN
L_000262aa:
    mov.l r4,@-r15
    .org 0x262ac-ORIGIN
L_000262ac:
    extu.w r7,r7
    .org 0x262ae-ORIGIN
L_000262ae:
    mov r5,r0
    .org 0x262b0-ORIGIN
L_000262b0:
    mov r7,r5
    .org 0x262b2-ORIGIN
L_000262b2:
    mov.l L_000262dc,r7
    .org 0x262b4-ORIGIN
L_000262b4:
    jsr @r7
    .org 0x262b6-ORIGIN
L_000262b6:
    mov #0x1e,r4
    .org 0x262b8-ORIGIN
L_000262b8:
    mov.l r5,@-r15
    .org 0x262ba-ORIGIN
L_000262ba:
    mov.l r4,@-r15
    .org 0x262bc-ORIGIN
L_000262bc:
    mov r6,r0
    .org 0x262be-ORIGIN
L_000262be:
    mov.l @(0x10,r15),r5
    .org 0x262c0-ORIGIN
L_000262c0:
    extu.w r5,r5
    .org 0x262c2-ORIGIN
L_000262c2:
    jsr @r7
    .org 0x262c4-ORIGIN
L_000262c4:
    mov #0x1e,r4
    .org 0x262c6-ORIGIN
L_000262c6:
    mov.l @r15+,r0
    .org 0x262c8-ORIGIN
L_000262c8:
    mov.l @r15+,r1
    .org 0x262ca-ORIGIN
L_000262ca:
    mov r4,r2
    .org 0x262cc-ORIGIN
L_000262cc:
    mov r5,r3
    .org 0x262ce-ORIGIN
L_000262ce:
    mov.l @r15+,r4
    .org 0x262d0-ORIGIN
L_000262d0:
    lds.l @r15+,pr
    .org 0x262d2-ORIGIN
L_000262d2:
    mov.l L_000262d8,r7
    .org 0x262d4-ORIGIN
L_000262d4:
    jmp @r7
    .org 0x262d6-ORIGIN
L_000262d6:
    mov #0x10,r5
    .org 0x262d8-ORIGIN
L_000262d8:
    .long 0x00026848
    .org 0x262dc-ORIGIN
L_000262dc:
    .long 0x00026984
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
    .org 0x26628-ORIGIN
L_00026628:
    sts.l pr,@-r15
    .org 0x2662a-ORIGIN
L_0002662a:
    mov.l r4,@-r15
    .org 0x2662c-ORIGIN
L_0002662c:
    extu.w r7,r7
    .org 0x2662e-ORIGIN
L_0002662e:
    mov r5,r0
    .org 0x26630-ORIGIN
L_00026630:
    mov r7,r5
    .org 0x26632-ORIGIN
L_00026632:
    mov.l L_0002665c,r7
    .org 0x26634-ORIGIN
L_00026634:
    jsr @r7
    .org 0x26636-ORIGIN
L_00026636:
    mov #0x1e,r4
    .org 0x26638-ORIGIN
L_00026638:
    mov.l r5,@-r15
    .org 0x2663a-ORIGIN
L_0002663a:
    mov.l r4,@-r15
    .org 0x2663c-ORIGIN
L_0002663c:
    mov r6,r0
    .org 0x2663e-ORIGIN
L_0002663e:
    mov.l @(0x10,r15),r5
    .org 0x26640-ORIGIN
L_00026640:
    extu.w r5,r5
    .org 0x26642-ORIGIN
L_00026642:
    jsr @r7
    .org 0x26644-ORIGIN
L_00026644:
    mov #0x1e,r4
    .org 0x26646-ORIGIN
L_00026646:
    mov.l @r15+,r0
    .org 0x26648-ORIGIN
L_00026648:
    mov.l @r15+,r1
    .org 0x2664a-ORIGIN
L_0002664a:
    mov r4,r2
    .org 0x2664c-ORIGIN
L_0002664c:
    mov r5,r3
    .org 0x2664e-ORIGIN
L_0002664e:
    mov.l @r15+,r4
    .org 0x26650-ORIGIN
L_00026650:
    lds.l @r15+,pr
    .org 0x26652-ORIGIN
L_00026652:
    mov.l L_00026658,r7
    .org 0x26654-ORIGIN
L_00026654:
    jmp @r7
    .org 0x26656-ORIGIN
L_00026656:
    mov #0x10,r5
    .org 0x26658-ORIGIN
L_00026658:
    .long 0x00026b28
    .org 0x2665c-ORIGIN
L_0002665c:
    .long 0x00026b84
    .org 0x266bc-ORIGIN
L_000266bc:
    sts.l pr,@-r15
    .org 0x266be-ORIGIN
L_000266be:
    mov.l r4,@-r15
    .org 0x266c0-ORIGIN
L_000266c0:
    mov r5,r0
    .org 0x266c2-ORIGIN
L_000266c2:
    extu.w r6,r5
    .org 0x266c4-ORIGIN
L_000266c4:
    mov.l L_000266e4,r7
    .org 0x266c6-ORIGIN
L_000266c6:
    jsr @r7
    .org 0x266c8-ORIGIN
L_000266c8:
    mov #0xe,r4
    .org 0x266ca-ORIGIN
L_000266ca:
    mov.l @r15+,r6
    .org 0x266cc-ORIGIN
L_000266cc:
    add r4,r6
    .org 0x266ce-ORIGIN
L_000266ce:
    mov.w @(0x2,r6),r0
    .org 0x266d0-ORIGIN
L_000266d0:
    extu.w r0,r2
    .org 0x266d2-ORIGIN
L_000266d2:
    mov r5,r3
    .org 0x266d4-ORIGIN
L_000266d4:
    mov.w @r6,r1
    .org 0x266d6-ORIGIN
L_000266d6:
    lds.l @r15+,pr
    .org 0x266d8-ORIGIN
L_000266d8:
    mov.l L_000266e0,r6
    .org 0x266da-ORIGIN
L_000266da:
    jmp @r6
    .org 0x266dc-ORIGIN
L_000266dc:
    extu.w r1,r0
    .org 0x266e0-ORIGIN
L_000266e0:
    .long 0x00026af8
    .org 0x266e4-ORIGIN
L_000266e4:
    .long 0x00026b84
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
    .org 0x26848-ORIGIN
L_00026848:
    mov.l r8,@-r15
    .org 0x2684a-ORIGIN
L_0002684a:
    sts.l pr,@-r15
    .org 0x2684c-ORIGIN
L_0002684c:
    sts macl,r7
    .org 0x2684e-ORIGIN
L_0002684e:
    mulu.w r5,r0
    .org 0x26850-ORIGIN
L_00026850:
    add r2,r4
    .org 0x26852-ORIGIN
L_00026852:
    sts macl,r0
    .org 0x26854-ORIGIN
L_00026854:
    lds r7,macl
    .org 0x26856-ORIGIN
L_00026856:
    shll r5
    .org 0x26858-ORIGIN
L_00026858:
    add r0,r4
    .org 0x2685a-ORIGIN
L_0002685a:
    add r4,r5
    .org 0x2685c-ORIGIN
L_0002685c:
    mov r1,r8
    .org 0x2685e-ORIGIN
L_0002685e:
    mov.l L_000268a0,r7
    .org 0x26860-ORIGIN
L_00026860:
    tst r3,r3
    .org 0x26862-ORIGIN
L_00026862:
    bt L_0002688a
    .org 0x26864-ORIGIN
L_00026864:
    mov.w @r4,r1
    .org 0x26866-ORIGIN
L_00026866:
    mov.w @(0x2,r4),r0
    .org 0x26868-ORIGIN
L_00026868:
    extu.w r0,r2
    .org 0x2686a-ORIGIN
L_0002686a:
    jsr @r7
    .org 0x2686c-ORIGIN
L_0002686c:
    extu.w r1,r0
    .org 0x2686e-ORIGIN
L_0002686e:
    tst r8,r8
    .org 0x26870-ORIGIN
L_00026870:
    bt L_0002689a
    .org 0x26872-ORIGIN
L_00026872:
    mov.l r0,@-r15
    .org 0x26874-ORIGIN
L_00026874:
    mov.w @r5,r1
    .org 0x26876-ORIGIN
L_00026876:
    mov.w @(0x2,r5),r0
    .org 0x26878-ORIGIN
L_00026878:
    extu.w r0,r2
    .org 0x2687a-ORIGIN
L_0002687a:
    jsr @r7
    .org 0x2687c-ORIGIN
L_0002687c:
    extu.w r1,r0
    .org 0x2687e-ORIGIN
L_0002687e:
    mov r0,r2
    .org 0x26880-ORIGIN
L_00026880:
    mov.l @r15+,r0
    .org 0x26882-ORIGIN
L_00026882:
    jsr @r7
    .org 0x26884-ORIGIN
L_00026884:
    mov r8,r3
    .org 0x26886-ORIGIN
L_00026886:
    bra L_0002689a
    .org 0x26888-ORIGIN
L_00026888:
    nop
    .org 0x2688a-ORIGIN
L_0002688a:
    tst r8,r8
    .org 0x2688c-ORIGIN
L_0002688c:
    bt/s L_0002689a
    .org 0x2688e-ORIGIN
L_0002688e:
    mov.w @r4,r0
    .org 0x26890-ORIGIN
L_00026890:
    mov.w @r5,r2
    .org 0x26892-ORIGIN
L_00026892:
    extu.w r0,r0
    .org 0x26894-ORIGIN
L_00026894:
    extu.w r2,r2
    .org 0x26896-ORIGIN
L_00026896:
    jsr @r7
    .org 0x26898-ORIGIN
L_00026898:
    mov r8,r3
    .org 0x2689a-ORIGIN
L_0002689a:
    lds.l @r15+,pr
    .org 0x2689c-ORIGIN
L_0002689c:
    rts
    .org 0x2689e-ORIGIN
L_0002689e:
    mov.l @r15+,r8
    .org 0x268a0-ORIGIN
L_000268a0:
    .long 0x00026740
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
    .org 0x26b28-ORIGIN
L_00026b28:
    mov.l r8,@-r15
    .org 0x26b2a-ORIGIN
L_00026b2a:
    sts.l pr,@-r15
    .org 0x26b2c-ORIGIN
L_00026b2c:
    sts macl,r7
    .org 0x26b2e-ORIGIN
L_00026b2e:
    mulu.w r5,r0
    .org 0x26b30-ORIGIN
L_00026b30:
    add r2,r4
    .org 0x26b32-ORIGIN
L_00026b32:
    sts macl,r0
    .org 0x26b34-ORIGIN
L_00026b34:
    lds r7,macl
    .org 0x26b36-ORIGIN
L_00026b36:
    shll r5
    .org 0x26b38-ORIGIN
L_00026b38:
    add r0,r4
    .org 0x26b3a-ORIGIN
L_00026b3a:
    add r4,r5
    .org 0x26b3c-ORIGIN
L_00026b3c:
    mov r1,r8
    .org 0x26b3e-ORIGIN
L_00026b3e:
    mov.l L_00026b80,r7
    .org 0x26b40-ORIGIN
L_00026b40:
    tst r3,r3
    .org 0x26b42-ORIGIN
L_00026b42:
    bt L_00026b6a
    .org 0x26b44-ORIGIN
L_00026b44:
    mov.w @r4,r1
    .org 0x26b46-ORIGIN
L_00026b46:
    mov.w @(0x2,r4),r0
    .org 0x26b48-ORIGIN
L_00026b48:
    extu.w r0,r2
    .org 0x26b4a-ORIGIN
L_00026b4a:
    jsr @r7
    .org 0x26b4c-ORIGIN
L_00026b4c:
    extu.w r1,r0
    .org 0x26b4e-ORIGIN
L_00026b4e:
    tst r8,r8
    .org 0x26b50-ORIGIN
L_00026b50:
    bt L_00026b7a
    .org 0x26b52-ORIGIN
L_00026b52:
    mov.l r0,@-r15
    .org 0x26b54-ORIGIN
L_00026b54:
    mov.w @r5,r1
    .org 0x26b56-ORIGIN
L_00026b56:
    mov.w @(0x2,r5),r0
    .org 0x26b58-ORIGIN
L_00026b58:
    extu.w r0,r2
    .org 0x26b5a-ORIGIN
L_00026b5a:
    jsr @r7
    .org 0x26b5c-ORIGIN
L_00026b5c:
    extu.w r1,r0
    .org 0x26b5e-ORIGIN
L_00026b5e:
    mov r0,r2
    .org 0x26b60-ORIGIN
L_00026b60:
    mov.l @r15+,r0
    .org 0x26b62-ORIGIN
L_00026b62:
    jsr @r7
    .org 0x26b64-ORIGIN
L_00026b64:
    mov r8,r3
    .org 0x26b66-ORIGIN
L_00026b66:
    bra L_00026b7a
    .org 0x26b68-ORIGIN
L_00026b68:
    nop
    .org 0x26b6a-ORIGIN
L_00026b6a:
    tst r8,r8
    .org 0x26b6c-ORIGIN
L_00026b6c:
    bt/s L_00026b7a
    .org 0x26b6e-ORIGIN
L_00026b6e:
    mov.w @r4,r0
    .org 0x26b70-ORIGIN
L_00026b70:
    mov.w @r5,r2
    .org 0x26b72-ORIGIN
L_00026b72:
    extu.w r0,r0
    .org 0x26b74-ORIGIN
L_00026b74:
    extu.w r2,r2
    .org 0x26b76-ORIGIN
L_00026b76:
    jsr @r7
    .org 0x26b78-ORIGIN
L_00026b78:
    mov r8,r3
    .org 0x26b7a-ORIGIN
L_00026b7a:
    lds.l @r15+,pr
    .org 0x26b7c-ORIGIN
L_00026b7c:
    rts
    .org 0x26b7e-ORIGIN
L_00026b7e:
    mov.l @r15+,r8
    .org 0x26b80-ORIGIN
L_00026b80:
    .long 0x00026af8
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
    .org 0x7b2c8-ORIGIN
L_0007b2c8:
    mov.l r12,@-r15
    .org 0x7b2ca-ORIGIN
L_0007b2ca:
    mov.l r14,@-r15
    .org 0x7b2cc-ORIGIN
L_0007b2cc:
    sts.l pr,@-r15
    .org 0x7b2ce-ORIGIN
L_0007b2ce:
    sts.l macl,@-r15
    .org 0x7b2d0-ORIGIN
L_0007b2d0:
    stc.l gbr,@-r15
    .org 0x7b2d2-ORIGIN
L_0007b2d2:
    mov.l L_0007b3b8,r0
    .org 0x7b2d4-ORIGIN
L_0007b2d4:
    ldc r0,gbr
    .org 0x7b2d6-ORIGIN
L_0007b2d6:
    add #-0x4,r15
    .org 0x7b2d8-ORIGIN
L_0007b2d8:
    mov.l L_0007b3bc,r6
    .org 0x7b2da-ORIGIN
L_0007b2da:
    mov.b @r6,r0
    .org 0x7b2dc-ORIGIN
L_0007b2dc:
    tst #0x2,r0
    .org 0x7b2de-ORIGIN
L_0007b2de:
    bt L_0007b392
    .org 0x7b2e0-ORIGIN
L_0007b2e0:
    mov.l L_0007b3c0,r7
    .org 0x7b2e2-ORIGIN
L_0007b2e2:
    mov.l L_0007b3c4,r4
    .org 0x7b2e4-ORIGIN
L_0007b2e4:
    mov.w @(0x1a,r7),r0
    .org 0x7b2e6-ORIGIN
L_0007b2e6:
    mov.l L_0007b3c8,r5
    .org 0x7b2e8-ORIGIN
L_0007b2e8:
    mov.w r0,@(0x2,r15)
    .org 0x7b2ea-ORIGIN
L_0007b2ea:
    mov.w @(0x6,gbr),r0
    .org 0x7b2ec-ORIGIN
L_0007b2ec:
    mov.l L_0007b3cc,r6
    .org 0x7b2ee-ORIGIN
L_0007b2ee:
    mov.l L_0007b3d0,r2
    .org 0x7b2f0-ORIGIN
L_0007b2f0:
    mov.l L_0007b3d4,r12
    .org 0x7b2f2-ORIGIN
L_0007b2f2:
    jsr @r2
    .org 0x7b2f4-ORIGIN
L_0007b2f4:
    extu.w r0,r7
    .org 0x7b2f6-ORIGIN
L_0007b2f6:
    extu.w r0,r2
    .org 0x7b2f8-ORIGIN
L_0007b2f8:
    mov.w L_0007b3ae,r0
    .org 0x7b2fa-ORIGIN
L_0007b2fa:
    mov #-0x80,r5
    .org 0x7b2fc-ORIGIN
L_0007b2fc:
    mov.l L_0007b3d8,r4
    .org 0x7b2fe-ORIGIN
L_0007b2fe:
    exts.w r2,r6
    .org 0x7b300-ORIGIN
L_0007b300:
    mov.l L_0007b3dc,r2
    .org 0x7b302-ORIGIN
L_0007b302:
    shll8 r5
    .org 0x7b304-ORIGIN
L_0007b304:
    add r5,r6
    .org 0x7b306-ORIGIN
L_0007b306:
    mov.l L_0007b3e0,r5
    .org 0x7b308-ORIGIN
L_0007b308:
    mov.w r6,@(r0,r12)
    .org 0x7b30a-ORIGIN
L_0007b30a:
    mov #0x28,r0
    .org 0x7b30c-ORIGIN
L_0007b30c:
    mov.l L_0007b3e4,r6
    .org 0x7b30e-ORIGIN
L_0007b30e:
    mov.w @(r0,r6),r7
    .org 0x7b310-ORIGIN
L_0007b310:
    jsr @r2
    .org 0x7b312-ORIGIN
L_0007b312:
    extu.w r7,r6
    .org 0x7b314-ORIGIN
L_0007b314:
    extu.w r0,r6
    .org 0x7b316-ORIGIN
L_0007b316:
    mov.w L_0007b3b0,r0
    .org 0x7b318-ORIGIN
L_0007b318:
    tst r6,r6
    .org 0x7b31a-ORIGIN
L_0007b31a:
    bf/s L_0007b322
    .org 0x7b31c-ORIGIN
L_0007b31c:
    mov.w r6,@(r0,r12)
    .org 0x7b31e-ORIGIN
L_0007b31e:
    bra L_0007b334
    .org 0x7b320-ORIGIN
L_0007b320:
    mov #-0x1,r2
    .org 0x7b322-ORIGIN
L_0007b322:
    mov.w @(0x6,gbr),r0
    .org 0x7b324-ORIGIN
L_0007b324:
    extu.w r0,r5
    .org 0x7b326-ORIGIN
L_0007b326:
    mov r5,r1
    .org 0x7b328-ORIGIN
L_0007b328:
    shll8 r1
    .org 0x7b32a-ORIGIN
L_0007b32a:
    sub r5,r1
    .org 0x7b32c-ORIGIN
L_0007b32c:
    mov.l L_0007b3e8,r5
    .org 0x7b32e-ORIGIN
L_0007b32e:
    jsr @r5
    .org 0x7b330-ORIGIN
L_0007b330:
    mov r6,r0
    .org 0x7b332-ORIGIN
L_0007b332:
    mov r0,r2
    .org 0x7b334-ORIGIN
L_0007b334:
    mov #-0x1,r6
    .org 0x7b336-ORIGIN
L_0007b336:
    extu.b r6,r6
    .org 0x7b338-ORIGIN
L_0007b338:
    cmp/hi r6,r2
    .org 0x7b33a-ORIGIN
L_0007b33a:
    bt L_0007b33e
    .org 0x7b33c-ORIGIN
L_0007b33c:
    mov r2,r6
    .org 0x7b33e-ORIGIN
L_0007b33e:
    mov.w L_0007b3b2,r0
    .org 0x7b340-ORIGIN
L_0007b340:
    mov #-0x1,r5
    .org 0x7b342-ORIGIN
L_0007b342:
    extu.b r5,r5
    .org 0x7b344-ORIGIN
L_0007b344:
    mov.b r6,@(r0,r12)
    .org 0x7b346-ORIGIN
L_0007b346:
    extu.b r6,r6
    .org 0x7b348-ORIGIN
L_0007b348:
    mov.w @(0x16,gbr),r0
    .org 0x7b34a-ORIGIN
L_0007b34a:
    mov r5,r2
    .org 0x7b34c-ORIGIN
L_0007b34c:
    sub r6,r2
    .org 0x7b34e-ORIGIN
L_0007b34e:
    mov.l L_0007b3ec,r6
    .org 0x7b350-ORIGIN
L_0007b350:
    mul.l r0,r2
    .org 0x7b352-ORIGIN
L_0007b352:
    mov r0,r4
    .org 0x7b354-ORIGIN
L_0007b354:
    mov r5,r0
    .org 0x7b356-ORIGIN
L_0007b356:
    jsr @r6
    .org 0x7b358-ORIGIN
L_0007b358:
    sts macl,r1
    .org 0x7b35a-ORIGIN
L_0007b35a:
    exts.w r0,r2
    .org 0x7b35c-ORIGIN
L_0007b35c:
    mov.w L_0007b3ae,r0
    .org 0x7b35e-ORIGIN
L_0007b35e:
    mov.w @(r0,r12),r14
    .org 0x7b360-ORIGIN
L_0007b360:
    mov.w @(0x14,gbr),r0
    .org 0x7b362-ORIGIN
L_0007b362:
    add r2,r14
    .org 0x7b364-ORIGIN
L_0007b364:
    cmp/gt r0,r14
    .org 0x7b366-ORIGIN
L_0007b366:
    bf/s L_0007b36c
    .org 0x7b368-ORIGIN
L_0007b368:
    mov r0,r6
    .org 0x7b36a-ORIGIN
L_0007b36a:
    mov r6,r14
    .org 0x7b36c-ORIGIN
L_0007b36c:
    mov.w @(0x16,gbr),r0
    .org 0x7b36e-ORIGIN
L_0007b36e:
    cmp/ge r0,r14
    .org 0x7b370-ORIGIN
L_0007b370:
    bt/s L_0007b376
    .org 0x7b372-ORIGIN
L_0007b372:
    mov r0,r4
    .org 0x7b374-ORIGIN
L_0007b374:
    mov r4,r14
    .org 0x7b376-ORIGIN
L_0007b376:
    mov.b @(0xd7,gbr),r0
    .org 0x7b378-ORIGIN
L_0007b378:
    tst #0x20,r0
    .org 0x7b37a-ORIGIN
L_0007b37a:
    bt/s L_0007b382
    .org 0x7b37c-ORIGIN
L_0007b37c:
    mov r0,r2
    .org 0x7b37e-ORIGIN
L_0007b37e:
    mov.w @(0x14,gbr),r0
    .org 0x7b380-ORIGIN
L_0007b380:
    mov r0,r14
    .org 0x7b382-ORIGIN
L_0007b382:
    mov r2,r0
    .org 0x7b384-ORIGIN
L_0007b384:
    tst #0x10,r0
    .org 0x7b386-ORIGIN
L_0007b386:
    bt L_0007b38c
    .org 0x7b388-ORIGIN
L_0007b388:
    mov.w @(0x16,gbr),r0
    .org 0x7b38a-ORIGIN
L_0007b38a:
    mov r0,r14
    .org 0x7b38c-ORIGIN
L_0007b38c:
    mov.w L_0007b3b4,r0
    .org 0x7b38e-ORIGIN
L_0007b38e:
    bra L_0007b3a0
    .org 0x7b390-ORIGIN
L_0007b390:
    mov.w r14,@(r0,r12)
    .org 0x7b392-ORIGIN
L_0007b392:
    mov.l L_0007b3f0,r6
    .org 0x7b394-ORIGIN
L_0007b394:
    mov #-0x80,r0
    .org 0x7b396-ORIGIN
L_0007b396:
    extu.b r0,r0
    .org 0x7b398-ORIGIN
L_0007b398:
    mov.l L_0007b3d4,r12
    .org 0x7b39a-ORIGIN
L_0007b39a:
    mov.w @(r0,r6),r2
    .org 0x7b39c-ORIGIN
L_0007b39c:
    mov.w L_0007b3b4,r0
    .org 0x7b39e-ORIGIN
L_0007b39e:
    mov.w r2,@(r0,r12)
    .org 0x7b3a0-ORIGIN
L_0007b3a0:
    add #0x4,r15
    .org 0x7b3a2-ORIGIN
L_0007b3a2:
    ldc.l @r15+,gbr
    .org 0x7b3a4-ORIGIN
L_0007b3a4:
    lds.l @r15+,macl
    .org 0x7b3a6-ORIGIN
L_0007b3a6:
    lds.l @r15+,pr
    .org 0x7b3a8-ORIGIN
L_0007b3a8:
    mov.l @r15+,r14
    .org 0x7b3aa-ORIGIN
L_0007b3aa:
    rts
    .org 0x7b3ac-ORIGIN
L_0007b3ac:
    mov.l @r15+,r12
    .org 0x7b3ae-ORIGIN
L_0007b3ae:
    .word 0x0376
    .org 0x7b3b0-ORIGIN
L_0007b3b0:
    .word 0x0406
    .org 0x7b3b2-ORIGIN
L_0007b3b2:
    .word 0x0405
    .org 0x7b3b4-ORIGIN
L_0007b3b4:
    .word 0x0374
    .org 0x7b3b8-ORIGIN
L_0007b3b8:
    .long 0xffff4124
    .org 0x7b3bc-ORIGIN
L_0007b3bc:
    .long 0x000083c1
    .org 0x7b3c0-ORIGIN
L_0007b3c0:
    .long 0xffff119c
    .org 0x7b3c4-ORIGIN
L_0007b3c4:
    .long 0x0000c98e
    .org 0x7b3c8-ORIGIN
L_0007b3c8:
    .long 0x00013478
    .org 0x7b3cc-ORIGIN
L_0007b3cc:
    .long 0x00013498
    .org 0x7b3d0-ORIGIN
L_0007b3d0:
    .long 0x000262a8
    .org 0x7b3d4-ORIGIN
L_0007b3d4:
    .long 0xffff28f8
    .org 0x7b3d8-ORIGIN
L_0007b3d8:
    .long 0x00014afa
    .org 0x7b3dc-ORIGIN
L_0007b3dc:
    .long 0x000264cc
    .org 0x7b3e0-ORIGIN
L_0007b3e0:
    .long 0x000134b8
    .org 0x7b3e4-ORIGIN
L_0007b3e4:
    .long 0xffff1094
    .org 0x7b3e8-ORIGIN
L_0007b3e8:
    .long 0x00021ce0
    .org 0x7b3ec-ORIGIN
L_0007b3ec:
    .long 0x00021bbc
    .org 0x7b3f0-ORIGIN
L_0007b3f0:
    .long 0xffff23bc
    .org 0x7b3f4-ORIGIN
L_0007b3f4:
    mov.l r14,@-r15
    .org 0x7b3f6-ORIGIN
L_0007b3f6:
    sts.l pr,@-r15
    .org 0x7b3f8-ORIGIN
L_0007b3f8:
    sts.l macl,@-r15
    .org 0x7b3fa-ORIGIN
L_0007b3fa:
    add #-0x4,r15
    .org 0x7b3fc-ORIGIN
L_0007b3fc:
    mov.l L_0007b4ec,r6
    .org 0x7b3fe-ORIGIN
L_0007b3fe:
    mov.b @r6,r0
    .org 0x7b400-ORIGIN
L_0007b400:
    tst #0x2,r0
    .org 0x7b402-ORIGIN
L_0007b402:
    bf L_0007b412
    .org 0x7b404-ORIGIN
L_0007b404:
    mov.l L_0007b4f0,r6
    .org 0x7b406-ORIGIN
L_0007b406:
    mov.w L_0007b4de,r0
    .org 0x7b408-ORIGIN
L_0007b408:
    mov.l L_0007b4f4,r14
    .org 0x7b40a-ORIGIN
L_0007b40a:
    mov.w @(r0,r6),r2
    .org 0x7b40c-ORIGIN
L_0007b40c:
    mov.w L_0007b4e0,r0
    .org 0x7b40e-ORIGIN
L_0007b40e:
    bra L_0007b4d4
    .org 0x7b410-ORIGIN
L_0007b410:
    mov.w r2,@(r0,r14)
    .org 0x7b412-ORIGIN
L_0007b412:
    mov.l L_0007b4f8,r6
    .org 0x7b414-ORIGIN
L_0007b414:
    mov #0x6b,r0
    .org 0x7b416-ORIGIN
L_0007b416:
    mov.b @(r0,r6),r0
    .org 0x7b418-ORIGIN
L_0007b418:
    tst #0x10,r0
    .org 0x7b41a-ORIGIN
L_0007b41a:
    bt L_0007b424
    .org 0x7b41c-ORIGIN
L_0007b41c:
    mov.l L_0007b4f4,r14
    .org 0x7b41e-ORIGIN
L_0007b41e:
    mov.w L_0007b4e2,r0
    .org 0x7b420-ORIGIN
L_0007b420:
    bra L_0007b4ce
    .org 0x7b422-ORIGIN
L_0007b422:
    mov.w @(r0,r14),r6
    .org 0x7b424-ORIGIN
L_0007b424:
    tst #0x20,r0
    .org 0x7b426-ORIGIN
L_0007b426:
    bt L_0007b430
    .org 0x7b428-ORIGIN
L_0007b428:
    mov.l L_0007b4fc,r5
    .org 0x7b42a-ORIGIN
L_0007b42a:
    mov.w @(0x14,r5),r0
    .org 0x7b42c-ORIGIN
L_0007b42c:
    bra L_0007b4ce
    .org 0x7b42e-ORIGIN
L_0007b42e:
    mov r0,r6
    .org 0x7b430-ORIGIN
L_0007b430:
    mov.l L_0007b500,r7
    .org 0x7b432-ORIGIN
L_0007b432:
    mov.l L_0007b4f4,r14
    .org 0x7b434-ORIGIN
L_0007b434:
    mov.w @(0x1a,r7),r0
    .org 0x7b436-ORIGIN
L_0007b436:
    mov.l L_0007b504,r4
    .org 0x7b438-ORIGIN
L_0007b438:
    mov.w r0,@(0x2,r15)
    .org 0x7b43a-ORIGIN
L_0007b43a:
    mov.w L_0007b4e4,r0
    .org 0x7b43c-ORIGIN
L_0007b43c:
    mov.l L_0007b508,r5
    .org 0x7b43e-ORIGIN
L_0007b43e:
    mov.w @(r0,r14),r3
    .org 0x7b440-ORIGIN
L_0007b440:
    mov.l L_0007b50c,r6
    .org 0x7b442-ORIGIN
L_0007b442:
    mov.l L_0007b510,r2
    .org 0x7b444-ORIGIN
L_0007b444:
    jsr @r2
    .org 0x7b446-ORIGIN
L_0007b446:
    extu.w r3,r7
    .org 0x7b448-ORIGIN
L_0007b448:
    extu.w r0,r2
    .org 0x7b44a-ORIGIN
L_0007b44a:
    mov.w L_0007b4e6,r0
    .org 0x7b44c-ORIGIN
L_0007b44c:
    mov #-0x80,r5
    .org 0x7b44e-ORIGIN
L_0007b44e:
    mov.l L_0007b514,r6
    .org 0x7b450-ORIGIN
L_0007b450:
    exts.w r2,r2
    .org 0x7b452-ORIGIN
L_0007b452:
    mov.l L_0007b518,r4
    .org 0x7b454-ORIGIN
L_0007b454:
    shll8 r5
    .org 0x7b456-ORIGIN
L_0007b456:
    add r5,r2
    .org 0x7b458-ORIGIN
L_0007b458:
    mov.l L_0007b51c,r5
    .org 0x7b45a-ORIGIN
L_0007b45a:
    mov.w r2,@(r0,r14)
    .org 0x7b45c-ORIGIN
L_0007b45c:
    mov #0x28,r0
    .org 0x7b45e-ORIGIN
L_0007b45e:
    mov.w @(r0,r6),r7
    .org 0x7b460-ORIGIN
L_0007b460:
    mov.l L_0007b520,r2
    .org 0x7b462-ORIGIN
L_0007b462:
    jsr @r2
    .org 0x7b464-ORIGIN
L_0007b464:
    extu.w r7,r6
    .org 0x7b466-ORIGIN
L_0007b466:
    extu.w r0,r6
    .org 0x7b468-ORIGIN
L_0007b468:
    mov.w L_0007b4e8,r0
    .org 0x7b46a-ORIGIN
L_0007b46a:
    tst r6,r6
    .org 0x7b46c-ORIGIN
L_0007b46c:
    bf/s L_0007b474
    .org 0x7b46e-ORIGIN
L_0007b46e:
    mov.w r6,@(r0,r14)
    .org 0x7b470-ORIGIN
L_0007b470:
    bra L_0007b488
    .org 0x7b472-ORIGIN
L_0007b472:
    mov #-0x1,r2
    .org 0x7b474-ORIGIN
L_0007b474:
    mov.w L_0007b4e4,r0
    .org 0x7b476-ORIGIN
L_0007b476:
    mov.l L_0007b524,r5
    .org 0x7b478-ORIGIN
L_0007b478:
    mov.w @(r0,r14),r2
    .org 0x7b47a-ORIGIN
L_0007b47a:
    mov r6,r0
    .org 0x7b47c-ORIGIN
L_0007b47c:
    extu.w r2,r4
    .org 0x7b47e-ORIGIN
L_0007b47e:
    mov r4,r1
    .org 0x7b480-ORIGIN
L_0007b480:
    shll8 r1
    .org 0x7b482-ORIGIN
L_0007b482:
    jsr @r5
    .org 0x7b484-ORIGIN
L_0007b484:
    sub r4,r1
    .org 0x7b486-ORIGIN
L_0007b486:
    mov r0,r2
    .org 0x7b488-ORIGIN
L_0007b488:
    mov #-0x1,r6
    .org 0x7b48a-ORIGIN
L_0007b48a:
    extu.b r6,r6
    .org 0x7b48c-ORIGIN
L_0007b48c:
    cmp/hi r6,r2
    .org 0x7b48e-ORIGIN
L_0007b48e:
    bt L_0007b492
    .org 0x7b490-ORIGIN
L_0007b490:
    mov r2,r6
    .org 0x7b492-ORIGIN
L_0007b492:
    mov.w L_0007b4ea,r0
    .org 0x7b494-ORIGIN
L_0007b494:
    mov #-0x1,r5
    .org 0x7b496-ORIGIN
L_0007b496:
    extu.b r5,r5
    .org 0x7b498-ORIGIN
L_0007b498:
    mov.b r6,@(r0,r14)
    .org 0x7b49a-ORIGIN
L_0007b49a:
    extu.b r6,r6
    .org 0x7b49c-ORIGIN
L_0007b49c:
    mov.w L_0007b4e2,r0
    .org 0x7b49e-ORIGIN
L_0007b49e:
    mov r5,r2
    .org 0x7b4a0-ORIGIN
L_0007b4a0:
    sub r6,r2
    .org 0x7b4a2-ORIGIN
L_0007b4a2:
    mov.l L_0007b528,r6
    .org 0x7b4a4-ORIGIN
L_0007b4a4:
    mov.w @(r0,r14),r4
    .org 0x7b4a6-ORIGIN
L_0007b4a6:
    mov r5,r0
    .org 0x7b4a8-ORIGIN
L_0007b4a8:
    mul.l r4,r2
    .org 0x7b4aa-ORIGIN
L_0007b4aa:
    jsr @r6
    .org 0x7b4ac-ORIGIN
L_0007b4ac:
    sts macl,r1
    .org 0x7b4ae-ORIGIN
L_0007b4ae:
    exts.w r0,r2
    .org 0x7b4b0-ORIGIN
L_0007b4b0:
    mov.w L_0007b4e6,r0
    .org 0x7b4b2-ORIGIN
L_0007b4b2:
    mov.l L_0007b4fc,r5
    .org 0x7b4b4-ORIGIN
L_0007b4b4:
    mov.w @(r0,r14),r6
    .org 0x7b4b6-ORIGIN
L_0007b4b6:
    mov.w @(0x14,r5),r0
    .org 0x7b4b8-ORIGIN
L_0007b4b8:
    add r2,r6
    .org 0x7b4ba-ORIGIN
L_0007b4ba:
    cmp/gt r0,r6
    .org 0x7b4bc-ORIGIN
L_0007b4bc:
    bf/s L_0007b4c4
    .org 0x7b4be-ORIGIN
L_0007b4be:
    mov r0,r2
    .org 0x7b4c0-ORIGIN
L_0007b4c0:
    bra L_0007b4ce
    .org 0x7b4c2-ORIGIN
L_0007b4c2:
    mov r2,r6
    .org 0x7b4c4-ORIGIN
L_0007b4c4:
    mov.w L_0007b4e2,r0
    .org 0x7b4c6-ORIGIN
L_0007b4c6:
    mov.w @(r0,r14),r4
    .org 0x7b4c8-ORIGIN
L_0007b4c8:
    cmp/ge r4,r6
    .org 0x7b4ca-ORIGIN
L_0007b4ca:
    bt L_0007b4ce
    .org 0x7b4cc-ORIGIN
L_0007b4cc:
    mov r4,r6
    .org 0x7b4ce-ORIGIN
L_0007b4ce:
    mov.l L_0007b4f4,r14
    .org 0x7b4d0-ORIGIN
L_0007b4d0:
    mov.w L_0007b4e0,r0
    .org 0x7b4d2-ORIGIN
L_0007b4d2:
    mov.w r6,@(r0,r14)
    .org 0x7b4d4-ORIGIN
L_0007b4d4:
    add #0x4,r15
    .org 0x7b4d6-ORIGIN
L_0007b4d6:
    lds.l @r15+,macl
    .org 0x7b4d8-ORIGIN
L_0007b4d8:
    lds.l @r15+,pr
    .org 0x7b4da-ORIGIN
L_0007b4da:
    rts
    .org 0x7b4dc-ORIGIN
L_0007b4dc:
    mov.l @r15+,r14
    .org 0x7b4de-ORIGIN
L_0007b4de:
    .word 0x0a9a
    .org 0x7b4e0-ORIGIN
L_0007b4e0:
    .word 0x0cda
    .org 0x7b4e2-ORIGIN
L_0007b4e2:
    .word 0x0cf8
    .org 0x7b4e4-ORIGIN
L_0007b4e4:
    .word 0x0cd6
    .org 0x7b4e6-ORIGIN
L_0007b4e6:
    .word 0x0cd8
    .org 0x7b4e8-ORIGIN
L_0007b4e8:
    .word 0x0ce0
    .org 0x7b4ea-ORIGIN
L_0007b4ea:
    .word 0x0cde
    .org 0x7b4ec-ORIGIN
L_0007b4ec:
    .long 0x000083c1
    .org 0x7b4f0-ORIGIN
L_0007b4f0:
    .long 0xffff128c
    .org 0x7b4f4-ORIGIN
L_0007b4f4:
    .long 0xffff28f8
    .org 0x7b4f8-ORIGIN
L_0007b4f8:
    .long 0xffff41a9
    .org 0x7b4fc-ORIGIN
L_0007b4fc:
    .long 0xffff4124
    .org 0x7b500-ORIGIN
L_0007b500:
    .long 0xffff119c
    .org 0x7b504-ORIGIN
L_0007b504:
    .long 0x00016948
    .org 0x7b508-ORIGIN
L_0007b508:
    .long 0x00018846
    .org 0x7b50c-ORIGIN
L_0007b50c:
    .long 0x00018866
    .org 0x7b510-ORIGIN
L_0007b510:
    .long 0x00026628
    .org 0x7b514-ORIGIN
L_0007b514:
    .long 0xffff1094
    .org 0x7b518-ORIGIN
L_0007b518:
    .long 0x00018dd6
    .org 0x7b51c-ORIGIN
L_0007b51c:
    .long 0x00018886
    .org 0x7b520-ORIGIN
L_0007b520:
    .long 0x000266bc
    .org 0x7b524-ORIGIN
L_0007b524:
    .long 0x00021ce0
    .org 0x7b528-ORIGIN
L_0007b528:
    .long 0x00021bbc
