! Explicit stock viridian-armadillo entry and natural word-lookup/division closure.
! 00014E42 is negated and multiplied into the signed dividend when incoming R4 is nonzero.
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
    mov.l L_00026520,r7
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
    mov.l L_0002651c,r6
    .org 0x26516-ORIGIN
L_00026516:
    jmp @r6
    .org 0x26518-ORIGIN
L_00026518:
    extu.w r1,r0
    .org 0x2651c-ORIGIN
L_0002651c:
    .long 0x00026740
    .org 0x26520-ORIGIN
L_00026520:
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
    .org 0xb7a3c-ORIGIN
L_000b7a3c:
    mov.l r11,@-r15
    .org 0xb7a3e-ORIGIN
L_000b7a3e:
    mov.l r12,@-r15
    .org 0xb7a40-ORIGIN
L_000b7a40:
    mov.l r13,@-r15
    .org 0xb7a42-ORIGIN
L_000b7a42:
    mov.l r14,@-r15
    .org 0xb7a44-ORIGIN
L_000b7a44:
    sts.l pr,@-r15
    .org 0xb7a46-ORIGIN
L_000b7a46:
    sts.l macl,@-r15
    .org 0xb7a48-ORIGIN
L_000b7a48:
    stc.l gbr,@-r15
    .org 0xb7a4a-ORIGIN
L_000b7a4a:
    mov.l L_000b7c1c,r0
    .org 0xb7a4c-ORIGIN
L_000b7a4c:
    ldc r0,gbr
    .org 0xb7a4e-ORIGIN
L_000b7a4e:
    add #-0x4,r15
    .org 0xb7a50-ORIGIN
L_000b7a50:
    mov r6,r1
    .org 0xb7a52-ORIGIN
L_000b7a52:
    mov r7,r0
    .org 0xb7a54-ORIGIN
L_000b7a54:
    mov.b r0,@(0x3,r15)
    .org 0xb7a56-ORIGIN
L_000b7a56:
    mov r4,r13
    .org 0xb7a58-ORIGIN
L_000b7a58:
    mov.l @(0x20,r15),r6
    .org 0xb7a5a-ORIGIN
L_000b7a5a:
    mov.l L_000b7c00,r7
    .org 0xb7a5c-ORIGIN
L_000b7a5c:
    mov #0x23,r0
    .org 0xb7a5e-ORIGIN
L_000b7a5e:
    mov.b r6,@(r0,r15)
    .org 0xb7a60-ORIGIN
L_000b7a60:
    mov.w L_000b7afe,r0
    .org 0xb7a62-ORIGIN
L_000b7a62:
    jsr @r7
    .org 0xb7a64-ORIGIN
L_000b7a64:
    mov r5,r11
    .org 0xb7a66-ORIGIN
L_000b7a66:
    mov r0,r5
    .org 0xb7a68-ORIGIN
L_000b7a68:
    mov.b @(0x3,r15),r0
    .org 0xb7a6a-ORIGIN
L_000b7a6a:
    mov #0x32,r6
    .org 0xb7a6c-ORIGIN
L_000b7a6c:
    mov r0,r2
    .org 0xb7a6e-ORIGIN
L_000b7a6e:
    extu.b r2,r2
    .org 0xb7a70-ORIGIN
L_000b7a70:
    mul.l r2,r6
    .org 0xb7a72-ORIGIN
L_000b7a72:
    sts macl,r2
    .org 0xb7a74-ORIGIN
L_000b7a74:
    sub r2,r5
    .org 0xb7a76-ORIGIN
L_000b7a76:
    mov.w L_000b7b00,r2
    .org 0xb7a78-ORIGIN
L_000b7a78:
    cmp/gt r2,r5
    .org 0xb7a7a-ORIGIN
L_000b7a7a:
    bf L_000b7a82
    .org 0xb7a7c-ORIGIN
L_000b7a7c:
    mov.w L_000b7b02,r2
    .org 0xb7a7e-ORIGIN
L_000b7a7e:
    bra L_000b7a94
    .org 0xb7a80-ORIGIN
L_000b7a80:
    nop
    .org 0xb7a82-ORIGIN
L_000b7a82:
    mov.l L_000b7c20,r2
    .org 0xb7a84-ORIGIN
L_000b7a84:
    cmp/ge r2,r5
    .org 0xb7a86-ORIGIN
L_000b7a86:
    bt L_000b7a8e
    .org 0xb7a88-ORIGIN
L_000b7a88:
    mov #-0x80,r2
    .org 0xb7a8a-ORIGIN
L_000b7a8a:
    bra L_000b7a94
    .org 0xb7a8c-ORIGIN
L_000b7a8c:
    shll8 r2
    .org 0xb7a8e-ORIGIN
L_000b7a8e:
    mov.w L_000b7b04,r6
    .org 0xb7a90-ORIGIN
L_000b7a90:
    add r6,r5
    .org 0xb7a92-ORIGIN
L_000b7a92:
    mov r5,r2
    .org 0xb7a94-ORIGIN
L_000b7a94:
    exts.w r2,r5
    .org 0xb7a96-ORIGIN
L_000b7a96:
    cmp/pz r5
    .org 0xb7a98-ORIGIN
L_000b7a98:
    bt L_000b7a9c
    .org 0xb7a9a-ORIGIN
L_000b7a9a:
    mov #0x0,r5
    .org 0xb7a9c-ORIGIN
L_000b7a9c:
    mov #0x23,r0
    .org 0xb7a9e-ORIGIN
L_000b7a9e:
    mov.b @(r0,r15),r6
    .org 0xb7aa0-ORIGIN
L_000b7aa0:
    mov.l L_000b7c24,r4
    .org 0xb7aa2-ORIGIN
L_000b7aa2:
    extu.w r5,r14
    .org 0xb7aa4-ORIGIN
L_000b7aa4:
    extu.b r6,r6
    .org 0xb7aa6-ORIGIN
L_000b7aa6:
    mov.l L_000b7c28,r5
    .org 0xb7aa8-ORIGIN
L_000b7aa8:
    shll8 r6
    .org 0xb7aaa-ORIGIN
L_000b7aaa:
    mov.l L_000b7c2c,r2
    .org 0xb7aac-ORIGIN
L_000b7aac:
    jsr @r2
    .org 0xb7aae-ORIGIN
L_000b7aae:
    extu.w r6,r6
    .org 0xb7ab0-ORIGIN
L_000b7ab0:
    mov r0,r2
    .org 0xb7ab2-ORIGIN
L_000b7ab2:
    mov.b @(0x0,gbr),r0
    .org 0xb7ab4-ORIGIN
L_000b7ab4:
    mov.l L_000b7c30,r5
    .org 0xb7ab6-ORIGIN
L_000b7ab6:
    mov r0,r12
    .org 0xb7ab8-ORIGIN
L_000b7ab8:
    extu.b r12,r6
    .org 0xb7aba-ORIGIN
L_000b7aba:
    mul.l r14,r6
    .org 0xb7abc-ORIGIN
L_000b7abc:
    sts macl,r6
    .org 0xb7abe-ORIGIN
L_000b7abe:
    cmp/hi r5,r6
    .org 0xb7ac0-ORIGIN
L_000b7ac0:
    bf L_000b7ac6
    .org 0xb7ac2-ORIGIN
L_000b7ac2:
    bra L_000b7ac8
    .org 0xb7ac4-ORIGIN
L_000b7ac4:
    mov #-0x1,r6
    .org 0xb7ac6-ORIGIN
L_000b7ac6:
    shlr r6
    .org 0xb7ac8-ORIGIN
L_000b7ac8:
    mov r6,r12
    .org 0xb7aca-ORIGIN
L_000b7aca:
    extu.w r2,r6
    .org 0xb7acc-ORIGIN
L_000b7acc:
    mov.l L_000b7c34,r2
    .org 0xb7ace-ORIGIN
L_000b7ace:
    extu.w r13,r13
    .org 0xb7ad0-ORIGIN
L_000b7ad0:
    tst r13,r13
    .org 0xb7ad2-ORIGIN
L_000b7ad2:
    mov.b @r2,r5
    .org 0xb7ad4-ORIGIN
L_000b7ad4:
    neg r6,r2
    .org 0xb7ad6-ORIGIN
L_000b7ad6:
    extu.b r5,r5
    .org 0xb7ad8-ORIGIN
L_000b7ad8:
    mul.l r2,r5
    .org 0xb7ada-ORIGIN
L_000b7ada:
    bt/s L_000b7b06
    .org 0xb7adc-ORIGIN
L_000b7adc:
    sts macl,r6
    .org 0xb7ade-ORIGIN
L_000b7ade:
    mov r6,r1
    .org 0xb7ae0-ORIGIN
L_000b7ae0:
    shll2 r1
    .org 0xb7ae2-ORIGIN
L_000b7ae2:
    add r6,r1
    .org 0xb7ae4-ORIGIN
L_000b7ae4:
    mov.l L_000b7c00,r7
    .org 0xb7ae6-ORIGIN
L_000b7ae6:
    shll2 r1
    .org 0xb7ae8-ORIGIN
L_000b7ae8:
    jsr @r7
    .org 0xb7aea-ORIGIN
L_000b7aea:
    mov r13,r0
    .org 0xb7aec-ORIGIN
L_000b7aec:
    mov.l L_000b7c04,r2
    .org 0xb7aee-ORIGIN
L_000b7aee:
    cmp/ge r2,r0
    .org 0xb7af0-ORIGIN
L_000b7af0:
    bf/s L_000b7b0c
    .org 0xb7af2-ORIGIN
L_000b7af2:
    mov r0,r6
    .org 0xb7af4-ORIGIN
L_000b7af4:
    mov #-0x1,r2
    .org 0xb7af6-ORIGIN
L_000b7af6:
    bra L_000b7b0e
    .org 0xb7af8-ORIGIN
L_000b7af8:
    add r2,r6
    .org 0xb7afe-ORIGIN
L_000b7afe:
    .word 0x4e20
    .org 0xb7b00-ORIGIN
L_000b7b00:
    .word 0x763b
    .org 0xb7b02-ORIGIN
L_000b7b02:
    .word 0x7fff
    .org 0xb7b04-ORIGIN
L_000b7b04:
    .word 0x09c4
    .org 0xb7b06-ORIGIN
L_000b7b06:
    cmp/pz r6
    .org 0xb7b08-ORIGIN
L_000b7b08:
    bt/s L_000b7b0e
    .org 0xb7b0a-ORIGIN
L_000b7b0a:
    mov #-0x1,r6
    .org 0xb7b0c-ORIGIN
L_000b7b0c:
    mov #0x0,r6
    .org 0xb7b0e-ORIGIN
L_000b7b0e:
    mov.l L_000b7c38,r4
    .org 0xb7b10-ORIGIN
L_000b7b10:
    mov.l L_000b7c3c,r5
    .org 0xb7b12-ORIGIN
L_000b7b12:
    mov.l L_000b7c10,r2
    .org 0xb7b14-ORIGIN
L_000b7b14:
    jsr @r2
    .org 0xb7b16-ORIGIN
L_000b7b16:
    extu.w r6,r6
    .org 0xb7b18-ORIGIN
L_000b7b18:
    extu.w r0,r2
    .org 0xb7b1a-ORIGIN
L_000b7b1a:
    neg r2,r6
    .org 0xb7b1c-ORIGIN
L_000b7b1c:
    mov.w L_000b7bf0,r2
    .org 0xb7b1e-ORIGIN
L_000b7b1e:
    cmp/ge r2,r6
    .org 0xb7b20-ORIGIN
L_000b7b20:
    bt L_000b7b26
    .org 0xb7b22-ORIGIN
L_000b7b22:
    bra L_000b7b2c
    .org 0xb7b24-ORIGIN
L_000b7b24:
    mov #0x0,r5
    .org 0xb7b26-ORIGIN
L_000b7b26:
    mov #-0x1,r2
    .org 0xb7b28-ORIGIN
L_000b7b28:
    add r2,r6
    .org 0xb7b2a-ORIGIN
L_000b7b2a:
    mov r6,r5
    .org 0xb7b2c-ORIGIN
L_000b7b2c:
    extu.b r11,r11
    .org 0xb7b2e-ORIGIN
L_000b7b2e:
    add #0x1,r11
    .org 0xb7b30-ORIGIN
L_000b7b30:
    extu.w r11,r2
    .org 0xb7b32-ORIGIN
L_000b7b32:
    mov #0x4,r4
    .org 0xb7b34-ORIGIN
L_000b7b34:
    cmp/gt r4,r2
    .org 0xb7b36-ORIGIN
L_000b7b36:
    bf L_000b7b3a
    .org 0xb7b38-ORIGIN
L_000b7b38:
    mov #0x4,r2
    .org 0xb7b3a-ORIGIN
L_000b7b3a:
    extu.b r2,r0
    .org 0xb7b3c-ORIGIN
L_000b7b3c:
    cmp/eq #0x1,r0
    .org 0xb7b3e-ORIGIN
L_000b7b3e:
    bt L_000b7b5c
    .org 0xb7b40-ORIGIN
L_000b7b40:
    cmp/eq #0x2,r0
    .org 0xb7b42-ORIGIN
L_000b7b42:
    bt L_000b7b56
    .org 0xb7b44-ORIGIN
L_000b7b44:
    cmp/eq #0x3,r0
    .org 0xb7b46-ORIGIN
L_000b7b46:
    bt L_000b7b52
    .org 0xb7b48-ORIGIN
L_000b7b48:
    cmp/eq #0x4,r0
    .org 0xb7b4a-ORIGIN
L_000b7b4a:
    bf L_000b7b5e
    .org 0xb7b4c-ORIGIN
L_000b7b4c:
    mov.b @(0x4,gbr),r0
    .org 0xb7b4e-ORIGIN
L_000b7b4e:
    bra L_000b7b5e
    .org 0xb7b50-ORIGIN
L_000b7b50:
    mov r0,r14
    .org 0xb7b52-ORIGIN
L_000b7b52:
    bra L_000b7b58
    .org 0xb7b54-ORIGIN
L_000b7b54:
    mov.b @(0x6,gbr),r0
    .org 0xb7b56-ORIGIN
L_000b7b56:
    mov.b @(0x5,gbr),r0
    .org 0xb7b58-ORIGIN
L_000b7b58:
    bra L_000b7b5e
    .org 0xb7b5a-ORIGIN
L_000b7b5a:
    mov r0,r14
    .org 0xb7b5c-ORIGIN
L_000b7b5c:
    mov #0xa,r14
    .org 0xb7b5e-ORIGIN
L_000b7b5e:
    extu.w r12,r12
    .org 0xb7b60-ORIGIN
L_000b7b60:
    mov.l L_000b7c14,r6
    .org 0xb7b62-ORIGIN
L_000b7b62:
    extu.b r5,r5
    .org 0xb7b64-ORIGIN
L_000b7b64:
    mul.l r5,r12
    .org 0xb7b66-ORIGIN
L_000b7b66:
    mov #-0x1,r2
    .org 0xb7b68-ORIGIN
L_000b7b68:
    extu.b r2,r0
    .org 0xb7b6a-ORIGIN
L_000b7b6a:
    sts macl,r1
    .org 0xb7b6c-ORIGIN
L_000b7b6c:
    jsr @r6
    .org 0xb7b6e-ORIGIN
L_000b7b6e:
    extu.b r14,r14
    .org 0xb7b70-ORIGIN
L_000b7b70:
    extu.w r0,r2
    .org 0xb7b72-ORIGIN
L_000b7b72:
    mov.l L_000b7c14,r6
    .org 0xb7b74-ORIGIN
L_000b7b74:
    mul.l r13,r2
    .org 0xb7b76-ORIGIN
L_000b7b76:
    mov.w L_000b7bf2,r0
    .org 0xb7b78-ORIGIN
L_000b7b78:
    jsr @r6
    .org 0xb7b7a-ORIGIN
L_000b7b7a:
    sts macl,r1
    .org 0xb7b7c-ORIGIN
L_000b7b7c:
    mul.l r0,r14
    .org 0xb7b7e-ORIGIN
L_000b7b7e:
    mov.l L_000b7c18,r6
    .org 0xb7b80-ORIGIN
L_000b7b80:
    mov.w L_000b7bf4,r0
    .org 0xb7b82-ORIGIN
L_000b7b82:
    sts macl,r2
    .org 0xb7b84-ORIGIN
L_000b7b84:
    mov.l r2,@(r0,r6)
    .org 0xb7b86-ORIGIN
L_000b7b86:
    add #0x4,r15
    .org 0xb7b88-ORIGIN
L_000b7b88:
    ldc.l @r15+,gbr
    .org 0xb7b8a-ORIGIN
L_000b7b8a:
    lds.l @r15+,macl
    .org 0xb7b8c-ORIGIN
L_000b7b8c:
    lds.l @r15+,pr
    .org 0xb7b8e-ORIGIN
L_000b7b8e:
    mov.l @r15+,r14
    .org 0xb7b90-ORIGIN
L_000b7b90:
    mov.l @r15+,r13
    .org 0xb7b92-ORIGIN
L_000b7b92:
    mov.l @r15+,r12
    .org 0xb7b94-ORIGIN
L_000b7b94:
    rts
    .org 0xb7b96-ORIGIN
L_000b7b96:
    mov.l @r15+,r11
    .org 0xb7bf0-ORIGIN
L_000b7bf0:
    .word 0xff01
    .org 0xb7bf2-ORIGIN
L_000b7bf2:
    .word 0x09c4
    .org 0xb7bf4-ORIGIN
L_000b7bf4:
    .word 0x0930
    .org 0xb7c00-ORIGIN
L_000b7c00:
    .long 0x00021bbc
    .org 0xb7c04-ORIGIN
L_000b7c04:
    .long 0xffff0001
    .org 0xb7c10-ORIGIN
L_000b7c10:
    .long 0x000264f8
    .org 0xb7c14-ORIGIN
L_000b7c14:
    .long 0x00021ce0
    .org 0xb7c18-ORIGIN
L_000b7c18:
    .long 0xffff28f8
    .org 0xb7c1c-ORIGIN
L_000b7c1c:
    .long 0x00008a30
    .org 0xb7c20-ORIGIN
L_000b7c20:
    .long 0xffff763c
    .org 0xb7c24-ORIGIN
L_000b7c24:
    .long 0x00014e42
    .org 0xb7c28-ORIGIN
L_000b7c28:
    .long 0x00013bb8
    .org 0xb7c2c-ORIGIN
L_000b7c2c:
    .long 0x000264cc
    .org 0xb7c30-ORIGIN
L_000b7c30:
    .long 0x0001fffe
    .org 0xb7c34-ORIGIN
L_000b7c34:
    .long 0x00008832
    .org 0xb7c38-ORIGIN
L_000b7c38:
    .long 0x000151f2
    .org 0xb7c3c-ORIGIN
L_000b7c3c:
    .long 0x00013bf8
