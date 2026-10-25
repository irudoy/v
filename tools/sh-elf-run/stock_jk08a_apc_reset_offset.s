! Explicit stock APC reset offset entry and natural byte-lookup/division closure.
! 0001208E is a factor of the signed dividend; R0 is the constant 00014000.
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
    .org 0x26370-ORIGIN
L_00026370:
    mov.w L_00026382,r0
    .org 0x26372-ORIGIN
L_00026372:
    extu.b r5,r5
    .org 0x26374-ORIGIN
L_00026374:
    cmp/hs r0,r5
    .org 0x26376-ORIGIN
L_00026376:
    bt L_0002637e
    .org 0x26378-ORIGIN
L_00026378:
    mov.l L_00026384,r6
    .org 0x2637a-ORIGIN
L_0002637a:
    jmp @r6
    .org 0x2637c-ORIGIN
L_0002637c:
    mov #0x0,r3
    .org 0x2637e-ORIGIN
L_0002637e:
    rts
    .org 0x26380-ORIGIN
L_00026380:
    mov.b @(0x7,r4),r0
    .org 0x26382-ORIGIN
L_00026382:
    .word 0x00e0
    .org 0x26384-ORIGIN
L_00026384:
    .long 0x00026a80
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
    .org 0x4c1e4-ORIGIN
L_0004c1e4:
    mov.l r10,@-r15
    .org 0x4c1e6-ORIGIN
L_0004c1e6:
    mov.l r11,@-r15
    .org 0x4c1e8-ORIGIN
L_0004c1e8:
    mov.l r12,@-r15
    .org 0x4c1ea-ORIGIN
L_0004c1ea:
    mov.l r13,@-r15
    .org 0x4c1ec-ORIGIN
L_0004c1ec:
    mov.l r14,@-r15
    .org 0x4c1ee-ORIGIN
L_0004c1ee:
    sts.l pr,@-r15
    .org 0x4c1f0-ORIGIN
L_0004c1f0:
    sts.l macl,@-r15
    .org 0x4c1f2-ORIGIN
L_0004c1f2:
    add #-0x4,r15
    .org 0x4c1f4-ORIGIN
L_0004c1f4:
    mov.l L_0004c3ec,r2
    .org 0x4c1f6-ORIGIN
L_0004c1f6:
    mov.b @r2,r0
    .org 0x4c1f8-ORIGIN
L_0004c1f8:
    and #0x40,r0
    .org 0x4c1fa-ORIGIN
L_0004c1fa:
    tst r0,r0
    .org 0x4c1fc-ORIGIN
L_0004c1fc:
    bt/s L_0004c23a
    .org 0x4c1fe-ORIGIN
L_0004c1fe:
    mov.b r0,@r15
    .org 0x4c200-ORIGIN
L_0004c200:
    mov.l L_0004c3f0,r10
    .org 0x4c202-ORIGIN
L_0004c202:
    mov.l L_0004c3f4,r2
    .org 0x4c204-ORIGIN
L_0004c204:
    mov.b @(0x1,r10),r0
    .org 0x4c206-ORIGIN
L_0004c206:
    mov.b @r2,r13
    .org 0x4c208-ORIGIN
L_0004c208:
    mov.l L_0004c3f8,r2
    .org 0x4c20a-ORIGIN
L_0004c20a:
    extu.b r0,r6
    .org 0x4c20c-ORIGIN
L_0004c20c:
    mov #0x36,r0
    .org 0x4c20e-ORIGIN
L_0004c20e:
    mov.w @(r0,r2),r5
    .org 0x4c210-ORIGIN
L_0004c210:
    shll2 r6
    .org 0x4c212-ORIGIN
L_0004c212:
    extu.w r6,r12
    .org 0x4c214-ORIGIN
L_0004c214:
    extu.w r5,r5
    .org 0x4c216-ORIGIN
L_0004c216:
    shll r12
    .org 0x4c218-ORIGIN
L_0004c218:
    cmp/pz r5
    .org 0x4c21a-ORIGIN
L_0004c21a:
    bt/s L_0004c220
    .org 0x4c21c-ORIGIN
L_0004c21c:
    mov r5,r2
    .org 0x4c21e-ORIGIN
L_0004c21e:
    add #0x3,r2
    .org 0x4c220-ORIGIN
L_0004c220:
    shar r2
    .org 0x4c222-ORIGIN
L_0004c222:
    mov #-0x1,r4
    .org 0x4c224-ORIGIN
L_0004c224:
    shar r2
    .org 0x4c226-ORIGIN
L_0004c226:
    extu.b r4,r4
    .org 0x4c228-ORIGIN
L_0004c228:
    cmp/gt r4,r2
    .org 0x4c22a-ORIGIN
L_0004c22a:
    bt L_0004c250
    .org 0x4c22c-ORIGIN
L_0004c22c:
    cmp/pz r5
    .org 0x4c22e-ORIGIN
L_0004c22e:
    bt/s L_0004c234
    .org 0x4c230-ORIGIN
L_0004c230:
    mov r5,r4
    .org 0x4c232-ORIGIN
L_0004c232:
    add #0x3,r4
    .org 0x4c234-ORIGIN
L_0004c234:
    shar r4
    .org 0x4c236-ORIGIN
L_0004c236:
    bra L_0004c250
    .org 0x4c238-ORIGIN
L_0004c238:
    shar r4
    .org 0x4c23a-ORIGIN
L_0004c23a:
    mov.l L_0004c3f0,r10
    .org 0x4c23c-ORIGIN
L_0004c23c:
    mov #0x12,r0
    .org 0x4c23e-ORIGIN
L_0004c23e:
    mov.l L_0004c3fc,r6
    .org 0x4c240-ORIGIN
L_0004c240:
    mov.b @r10,r5
    .org 0x4c242-ORIGIN
L_0004c242:
    mov.b @r6,r13
    .org 0x4c244-ORIGIN
L_0004c244:
    extu.b r5,r5
    .org 0x4c246-ORIGIN
L_0004c246:
    mov.l L_0004c400,r6
    .org 0x4c248-ORIGIN
L_0004c248:
    mov r5,r12
    .org 0x4c24a-ORIGIN
L_0004c24a:
    shll r12
    .org 0x4c24c-ORIGIN
L_0004c24c:
    add r5,r12
    .org 0x4c24e-ORIGIN
L_0004c24e:
    mov.b @(r0,r6),r4
    .org 0x4c250-ORIGIN
L_0004c250:
    mov.b @(0x3,r10),r0
    .org 0x4c252-ORIGIN
L_0004c252:
    extu.b r4,r4
    .org 0x4c254-ORIGIN
L_0004c254:
    extu.b r0,r7
    .org 0x4c256-ORIGIN
L_0004c256:
    cmp/gt r7,r4
    .org 0x4c258-ORIGIN
L_0004c258:
    bf L_0004c25c
    .org 0x4c25a-ORIGIN
L_0004c25a:
    mov r7,r4
    .org 0x4c25c-ORIGIN
L_0004c25c:
    mov.b @(0x4,r10),r0
    .org 0x4c25e-ORIGIN
L_0004c25e:
    extu.b r4,r7
    .org 0x4c260-ORIGIN
L_0004c260:
    extu.b r0,r5
    .org 0x4c262-ORIGIN
L_0004c262:
    cmp/ge r5,r7
    .org 0x4c264-ORIGIN
L_0004c264:
    bf L_0004c268
    .org 0x4c266-ORIGIN
L_0004c266:
    mov r7,r5
    .org 0x4c268-ORIGIN
L_0004c268:
    mov.l L_0004c404,r11
    .org 0x4c26a-ORIGIN
L_0004c26a:
    mov #0x70,r0
    .org 0x4c26c-ORIGIN
L_0004c26c:
    extu.b r5,r5
    .org 0x4c26e-ORIGIN
L_0004c26e:
    mov.l L_0004c3f8,r2
    .org 0x4c270-ORIGIN
L_0004c270:
    shll2 r0
    .org 0x4c272-ORIGIN
L_0004c272:
    mov.b r5,@(r0,r11)
    .org 0x4c274-ORIGIN
L_0004c274:
    mov #0x74,r0
    .org 0x4c276-ORIGIN
L_0004c276:
    mov.b @(r0,r2),r7
    .org 0x4c278-ORIGIN
L_0004c278:
    mov.b @(0x6,r10),r0
    .org 0x4c27a-ORIGIN
L_0004c27a:
    extu.b r7,r7
    .org 0x4c27c-ORIGIN
L_0004c27c:
    extu.b r0,r6
    .org 0x4c27e-ORIGIN
L_0004c27e:
    cmp/ge r6,r7
    .org 0x4c280-ORIGIN
L_0004c280:
    bt L_0004c286
    .org 0x4c282-ORIGIN
L_0004c282:
    mov.b @(0x6,r10),r0
    .org 0x4c284-ORIGIN
L_0004c284:
    mov r0,r7
    .org 0x4c286-ORIGIN
L_0004c286:
    mov #0x71,r0
    .org 0x4c288-ORIGIN
L_0004c288:
    extu.b r7,r2
    .org 0x4c28a-ORIGIN
L_0004c28a:
    extu.b r7,r4
    .org 0x4c28c-ORIGIN
L_0004c28c:
    tst r2,r2
    .org 0x4c28e-ORIGIN
L_0004c28e:
    shll2 r0
    .org 0x4c290-ORIGIN
L_0004c290:
    bt/s L_0004c2dc
    .org 0x4c292-ORIGIN
L_0004c292:
    mov.b r4,@(r0,r11)
    .org 0x4c294-ORIGIN
L_0004c294:
    mul.l r4,r4
    .org 0x4c296-ORIGIN
L_0004c296:
    mov.b @(0x5,r10),r0
    .org 0x4c298-ORIGIN
L_0004c298:
    extu.b r0,r2
    .org 0x4c29a-ORIGIN
L_0004c29a:
    sts macl,r0
    .org 0x4c29c-ORIGIN
L_0004c29c:
    mul.l r5,r2
    .org 0x4c29e-ORIGIN
L_0004c29e:
    sts macl,r2
    .org 0x4c2a0-ORIGIN
L_0004c2a0:
    mov r2,r14
    .org 0x4c2a2-ORIGIN
L_0004c2a2:
    shll r14
    .org 0x4c2a4-ORIGIN
L_0004c2a4:
    add r2,r14
    .org 0x4c2a6-ORIGIN
L_0004c2a6:
    mov.l L_0004c408,r2
    .org 0x4c2a8-ORIGIN
L_0004c2a8:
    shll r14
    .org 0x4c2aa-ORIGIN
L_0004c2aa:
    mov.w @r2,r6
    .org 0x4c2ac-ORIGIN
L_0004c2ac:
    extu.w r6,r2
    .org 0x4c2ae-ORIGIN
L_0004c2ae:
    mul.l r5,r2
    .org 0x4c2b0-ORIGIN
L_0004c2b0:
    sts macl,r7
    .org 0x4c2b2-ORIGIN
L_0004c2b2:
    mov r7,r1
    .org 0x4c2b4-ORIGIN
L_0004c2b4:
    shll r1
    .org 0x4c2b6-ORIGIN
L_0004c2b6:
    add r7,r1
    .org 0x4c2b8-ORIGIN
L_0004c2b8:
    mov.l L_0004c40c,r7
    .org 0x4c2ba-ORIGIN
L_0004c2ba:
    jsr @r7
    .org 0x4c2bc-ORIGIN
L_0004c2bc:
    shll r1
    .org 0x4c2be-ORIGIN
L_0004c2be:
    mov.b @r15,r6
    .org 0x4c2c0-ORIGIN
L_0004c2c0:
    add r14,r0
    .org 0x4c2c2-ORIGIN
L_0004c2c2:
    tst r6,r6
    .org 0x4c2c4-ORIGIN
L_0004c2c4:
    bt/s L_0004c2f4
    .org 0x4c2c6-ORIGIN
L_0004c2c6:
    mov r0,r4
    .org 0x4c2c8-ORIGIN
L_0004c2c8:
    mov.b @(0x2,r10),r0
    .org 0x4c2ca-ORIGIN
L_0004c2ca:
    extu.b r0,r2
    .org 0x4c2cc-ORIGIN
L_0004c2cc:
    mul.l r4,r2
    .org 0x4c2ce-ORIGIN
L_0004c2ce:
    sts macl,r6
    .org 0x4c2d0-ORIGIN
L_0004c2d0:
    mov r6,r4
    .org 0x4c2d2-ORIGIN
L_0004c2d2:
    shll2 r4
    .org 0x4c2d4-ORIGIN
L_0004c2d4:
    add r6,r4
    .org 0x4c2d6-ORIGIN
L_0004c2d6:
    shll r4
    .org 0x4c2d8-ORIGIN
L_0004c2d8:
    bra L_0004c2f4
    .org 0x4c2da-ORIGIN
L_0004c2da:
    shlr8 r4
    .org 0x4c2dc-ORIGIN
L_0004c2dc:
    mov.b @(0x5,r10),r0
    .org 0x4c2de-ORIGIN
L_0004c2de:
    mov r5,r6
    .org 0x4c2e0-ORIGIN
L_0004c2e0:
    mov #-0x1,r5
    .org 0x4c2e2-ORIGIN
L_0004c2e2:
    extu.b r0,r2
    .org 0x4c2e4-ORIGIN
L_0004c2e4:
    extu.w r5,r5
    .org 0x4c2e6-ORIGIN
L_0004c2e6:
    add r5,r2
    .org 0x4c2e8-ORIGIN
L_0004c2e8:
    mul.l r6,r2
    .org 0x4c2ea-ORIGIN
L_0004c2ea:
    sts macl,r6
    .org 0x4c2ec-ORIGIN
L_0004c2ec:
    mov r6,r4
    .org 0x4c2ee-ORIGIN
L_0004c2ee:
    shll r4
    .org 0x4c2f0-ORIGIN
L_0004c2f0:
    add r6,r4
    .org 0x4c2f2-ORIGIN
L_0004c2f2:
    shll r4
    .org 0x4c2f4-ORIGIN
L_0004c2f4:
    mov.l L_0004c410,r5
    .org 0x4c2f6-ORIGIN
L_0004c2f6:
    extu.b r13,r13
    .org 0x4c2f8-ORIGIN
L_0004c2f8:
    add r13,r4
    .org 0x4c2fa-ORIGIN
L_0004c2fa:
    mov.b @r5,r6
    .org 0x4c2fc-ORIGIN
L_0004c2fc:
    extu.b r6,r6
    .org 0x4c2fe-ORIGIN
L_0004c2fe:
    cmp/hi r6,r4
    .org 0x4c300-ORIGIN
L_0004c300:
    bf L_0004c304
    .org 0x4c302-ORIGIN
L_0004c302:
    mov r6,r4
    .org 0x4c304-ORIGIN
L_0004c304:
    mov.b @(0x1,r5),r0
    .org 0x4c306-ORIGIN
L_0004c306:
    extu.b r0,r6
    .org 0x4c308-ORIGIN
L_0004c308:
    cmp/hs r6,r4
    .org 0x4c30a-ORIGIN
L_0004c30a:
    bf L_0004c30e
    .org 0x4c30c-ORIGIN
L_0004c30c:
    mov r4,r6
    .org 0x4c30e-ORIGIN
L_0004c30e:
    mov.w L_0004c364,r0
    .org 0x4c310-ORIGIN
L_0004c310:
    extu.w r12,r12
    .org 0x4c312-ORIGIN
L_0004c312:
    mov.l L_0004c414,r4
    .org 0x4c314-ORIGIN
L_0004c314:
    mov.b r6,@(r0,r11)
    .org 0x4c316-ORIGIN
L_0004c316:
    mov #0x70,r0
    .org 0x4c318-ORIGIN
L_0004c318:
    shll2 r0
    .org 0x4c31a-ORIGIN
L_0004c31a:
    mov.l L_0004c418,r6
    .org 0x4c31c-ORIGIN
L_0004c31c:
    mov.b @(r0,r11),r5
    .org 0x4c31e-ORIGIN
L_0004c31e:
    jsr @r6
    .org 0x4c320-ORIGIN
L_0004c320:
    extu.b r5,r5
    .org 0x4c322-ORIGIN
L_0004c322:
    mov r0,r2
    .org 0x4c324-ORIGIN
L_0004c324:
    mov.w L_0004c366,r0
    .org 0x4c326-ORIGIN
L_0004c326:
    mov.l L_0004c41c,r4
    .org 0x4c328-ORIGIN
L_0004c328:
    mov.b r2,@(r0,r11)
    .org 0x4c32a-ORIGIN
L_0004c32a:
    mov #0x71,r0
    .org 0x4c32c-ORIGIN
L_0004c32c:
    shll2 r0
    .org 0x4c32e-ORIGIN
L_0004c32e:
    mov.l L_0004c418,r6
    .org 0x4c330-ORIGIN
L_0004c330:
    mov.b @(r0,r11),r2
    .org 0x4c332-ORIGIN
L_0004c332:
    jsr @r6
    .org 0x4c334-ORIGIN
L_0004c334:
    extu.b r2,r5
    .org 0x4c336-ORIGIN
L_0004c336:
    mov r0,r2
    .org 0x4c338-ORIGIN
L_0004c338:
    mov.w L_0004c368,r0
    .org 0x4c33a-ORIGIN
L_0004c33a:
    extu.b r2,r5
    .org 0x4c33c-ORIGIN
L_0004c33c:
    mov.b r2,@(r0,r11)
    .org 0x4c33e-ORIGIN
L_0004c33e:
    mov.w L_0004c366,r0
    .org 0x4c340-ORIGIN
L_0004c340:
    mov.b @(r0,r11),r6
    .org 0x4c342-ORIGIN
L_0004c342:
    mov.l L_0004c420,r0
    .org 0x4c344-ORIGIN
L_0004c344:
    extu.b r6,r6
    .org 0x4c346-ORIGIN
L_0004c346:
    mul.l r12,r6
    .org 0x4c348-ORIGIN
L_0004c348:
    mov.l L_0004c424,r6
    .org 0x4c34a-ORIGIN
L_0004c34a:
    sts macl,r2
    .org 0x4c34c-ORIGIN
L_0004c34c:
    mul.l r2,r5
    .org 0x4c34e-ORIGIN
L_0004c34e:
    jsr @r6
    .org 0x4c350-ORIGIN
L_0004c350:
    sts macl,r1
    .org 0x4c352-ORIGIN
L_0004c352:
    mov #-0x1,r6
    .org 0x4c354-ORIGIN
L_0004c354:
    extu.b r6,r6
    .org 0x4c356-ORIGIN
L_0004c356:
    cmp/hi r6,r0
    .org 0x4c358-ORIGIN
L_0004c358:
    bf/s L_0004c35e
    .org 0x4c35a-ORIGIN
L_0004c35a:
    mov r0,r2
    .org 0x4c35c-ORIGIN
L_0004c35c:
    mov r6,r2
    .org 0x4c35e-ORIGIN
L_0004c35e:
    mov.w L_0004c36a,r0
    .org 0x4c360-ORIGIN
L_0004c360:
    bra L_0004c36c
    .org 0x4c362-ORIGIN
L_0004c362:
    extu.b r2,r5
    .org 0x4c364-ORIGIN
L_0004c364:
    .word 0x05e8
    .org 0x4c366-ORIGIN
L_0004c366:
    .word 0x01c1
    .org 0x4c368-ORIGIN
L_0004c368:
    .word 0x01c5
    .org 0x4c36a-ORIGIN
L_0004c36a:
    .word 0x05e9
    .org 0x4c36c-ORIGIN
L_0004c36c:
    mov.b r5,@(r0,r11)
    .org 0x4c36e-ORIGIN
L_0004c36e:
    mov.w L_0004c3ea,r0
    .org 0x4c370-ORIGIN
L_0004c370:
    mov.b @(r0,r11),r4
    .org 0x4c372-ORIGIN
L_0004c372:
    extu.b r4,r4
    .org 0x4c374-ORIGIN
L_0004c374:
    cmp/gt r5,r4
    .org 0x4c376-ORIGIN
L_0004c376:
    bt L_0004c37a
    .org 0x4c378-ORIGIN
L_0004c378:
    mov r4,r5
    .org 0x4c37a-ORIGIN
L_0004c37a:
    mov r5,r6
    .org 0x4c37c-ORIGIN
L_0004c37c:
    mov.l L_0004c428,r5
    .org 0x4c37e-ORIGIN
L_0004c37e:
    mov #0x4a,r0
    .org 0x4c380-ORIGIN
L_0004c380:
    mov.b r6,@(r0,r5)
    .org 0x4c382-ORIGIN
L_0004c382:
    mov.l L_0004c42c,r6
    .org 0x4c384-ORIGIN
L_0004c384:
    mov.b @(0x5,r6),r0
    .org 0x4c386-ORIGIN
L_0004c386:
    tst #0x1,r0
    .org 0x4c388-ORIGIN
L_0004c388:
    bt L_0004c390
    .org 0x4c38a-ORIGIN
L_0004c38a:
    mov #0x18,r2
    .org 0x4c38c-ORIGIN
L_0004c38c:
    mov #0x4a,r0
    .org 0x4c38e-ORIGIN
L_0004c38e:
    mov.b r2,@(r0,r5)
    .org 0x4c390-ORIGIN
L_0004c390:
    add #0x4,r15
    .org 0x4c392-ORIGIN
L_0004c392:
    lds.l @r15+,macl
    .org 0x4c394-ORIGIN
L_0004c394:
    lds.l @r15+,pr
    .org 0x4c396-ORIGIN
L_0004c396:
    mov.l @r15+,r14
    .org 0x4c398-ORIGIN
L_0004c398:
    mov.l @r15+,r13
    .org 0x4c39a-ORIGIN
L_0004c39a:
    mov.l @r15+,r12
    .org 0x4c39c-ORIGIN
L_0004c39c:
    mov.l @r15+,r11
    .org 0x4c39e-ORIGIN
L_0004c39e:
    rts
    .org 0x4c3a0-ORIGIN
L_0004c3a0:
    mov.l @r15+,r10
    .org 0x4c3ea-ORIGIN
L_0004c3ea:
    .word 0x05e8
    .org 0x4c3ec-ORIGIN
L_0004c3ec:
    .long 0xffff4184
    .org 0x4c3f0-ORIGIN
L_0004c3f0:
    .long 0x0000851f
    .org 0x4c3f4-ORIGIN
L_0004c3f4:
    .long 0x00008291
    .org 0x4c3f8-ORIGIN
L_0004c3f8:
    .long 0xffff1094
    .org 0x4c3fc-ORIGIN
L_0004c3fc:
    .long 0x0000828a
    .org 0x4c400-ORIGIN
L_0004c400:
    .long 0xffff119c
    .org 0x4c404-ORIGIN
L_0004c404:
    .long 0xffff128c
    .org 0x4c408-ORIGIN
L_0004c408:
    .long 0x0000959a
    .org 0x4c40c-ORIGIN
L_0004c40c:
    .long 0x00021ce0
    .org 0x4c410-ORIGIN
L_0004c410:
    .long 0x00008b87
    .org 0x4c414-ORIGIN
L_0004c414:
    .long 0x0001208e
    .org 0x4c418-ORIGIN
L_0004c418:
    .long 0x00026370
    .org 0x4c41c-ORIGIN
L_0004c41c:
    .long 0x00012096
    .org 0x4c420-ORIGIN
L_0004c420:
    .long 0x00014000
    .org 0x4c424-ORIGIN
L_0004c424:
    .long 0x00021bbc
    .org 0x4c428-ORIGIN
L_0004c428:
    .long 0xffff23bc
    .org 0x4c42c-ORIGIN
L_0004c42c:
    .long 0xffff424c
