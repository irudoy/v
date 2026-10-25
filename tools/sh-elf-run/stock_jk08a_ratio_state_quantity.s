! Complete stock ratio producer, scaled state consumer and real helpers.
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
    mov.l P_00021dc8,r1
    .org 0x21d6c-ORIGIN
L_00021d6c:
    mov.l P_00021dcc,r2
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
P_00021dc8:
    .byte 0xff
    .org 0x21dc9-ORIGIN
P_00021dc9:
    .byte 0xff
    .org 0x21dca-ORIGIN
P_00021dca:
    .byte 0x98
    .org 0x21dcb-ORIGIN
P_00021dcb:
    .byte 0x18
    .org 0x21dcc-ORIGIN
P_00021dcc:
    .byte 0x00
    .org 0x21dcd-ORIGIN
P_00021dcd:
    .byte 0x00
    .org 0x21dce-ORIGIN
P_00021dce:
    .byte 0x04
    .org 0x21dcf-ORIGIN
P_00021dcf:
    .byte 0x4e
    .org 0x224fa-ORIGIN
L_000224fa:
    shar r0
    .org 0x224fc-ORIGIN
L_000224fc:
    shar r0
    .org 0x224fe-ORIGIN
L_000224fe:
    shar r0
    .org 0x22500-ORIGIN
L_00022500:
    shar r0
    .org 0x22502-ORIGIN
L_00022502:
    shar r0
    .org 0x22504-ORIGIN
L_00022504:
    rts
    .org 0x22506-ORIGIN
L_00022506:
    shar r0
    .org 0x263f4-ORIGIN
L_000263f4:
    mov.l P_0002640c,r0
    .org 0x263f6-ORIGIN
L_000263f6:
    extu.w r5,r5
    .org 0x263f8-ORIGIN
L_000263f8:
    cmp/hs r0,r5
    .org 0x263fa-ORIGIN
L_000263fa:
    bt L_00026402
    .org 0x263fc-ORIGIN
L_000263fc:
    mov.l P_00026408,r6
    .org 0x263fe-ORIGIN
L_000263fe:
    jmp @r6
    .org 0x26400-ORIGIN
L_00026400:
    mov #0x0,r3
    .org 0x26402-ORIGIN
L_00026402:
    rts
    .org 0x26404-ORIGIN
L_00026404:
    mov.w @(0x1e,r4),r0
    .org 0x26408-ORIGIN
P_00026408:
    .byte 0x00
    .org 0x26409-ORIGIN
P_00026409:
    .byte 0x02
    .org 0x2640a-ORIGIN
P_0002640a:
    .byte 0x6a
    .org 0x2640b-ORIGIN
P_0002640b:
    .byte 0x64
    .org 0x2640c-ORIGIN
P_0002640c:
    .byte 0x00
    .org 0x2640d-ORIGIN
P_0002640d:
    .byte 0x00
    .org 0x2640e-ORIGIN
P_0002640e:
    .byte 0xf0
    .org 0x2640f-ORIGIN
P_0002640f:
    .byte 0x00
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
    mov.l P_000264f4,r7
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
    mov.l P_000264f0,r6
    .org 0x264ea-ORIGIN
L_000264ea:
    jmp @r6
    .org 0x264ec-ORIGIN
L_000264ec:
    extu.w r1,r0
    .org 0x264f0-ORIGIN
P_000264f0:
    .byte 0x00
    .org 0x264f1-ORIGIN
P_000264f1:
    .byte 0x02
    .org 0x264f2-ORIGIN
P_000264f2:
    .byte 0x67
    .org 0x264f3-ORIGIN
P_000264f3:
    .byte 0x40
    .org 0x264f4-ORIGIN
P_000264f4:
    .byte 0x00
    .org 0x264f5-ORIGIN
P_000264f5:
    .byte 0x02
    .org 0x264f6-ORIGIN
P_000264f6:
    .byte 0x69
    .org 0x264f7-ORIGIN
P_000264f7:
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
    .byte 0x00
    .org 0x26abd-ORIGIN
P_00026abd:
    .byte 0x02
    .org 0x26abe-ORIGIN
P_00026abe:
    .byte 0x67
    .org 0x26abf-ORIGIN
P_00026abf:
    .byte 0x40
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
    .org 0x75174-ORIGIN
L_00075174:
    mov.l r14,@-r15
    .org 0x75176-ORIGIN
L_00075176:
    sts.l pr,@-r15
    .org 0x75178-ORIGIN
L_00075178:
    sts.l macl,@-r15
    .org 0x7517a-ORIGIN
L_0007517a:
    mov.l P_00075218,r14
    .org 0x7517c-ORIGIN
L_0007517c:
    mov.w P_0007520e,r0
    .org 0x7517e-ORIGIN
L_0007517e:
    mov.w @(r0,r14),r5
    .org 0x75180-ORIGIN
L_00075180:
    extu.w r5,r5
    .org 0x75182-ORIGIN
L_00075182:
    cmp/pl r5
    .org 0x75184-ORIGIN
L_00075184:
    bf L_000751d2
    .org 0x75186-ORIGIN
L_00075186:
    mov.l P_0007521c,r2
    .org 0x75188-ORIGIN
L_00075188:
    mov #0x42,r0
    .org 0x7518a-ORIGIN
L_0007518a:
    mov.w @(r0,r2),r4
    .org 0x7518c-ORIGIN
L_0007518c:
    mov.w P_00075210,r0
    .org 0x7518e-ORIGIN
L_0007518e:
    extu.w r4,r4
    .org 0x75190-ORIGIN
L_00075190:
    mov.w @(r0,r14),r7
    .org 0x75192-ORIGIN
L_00075192:
    extu.w r7,r2
    .org 0x75194-ORIGIN
L_00075194:
    cmp/gt r2,r4
    .org 0x75196-ORIGIN
L_00075196:
    bt L_0007519a
    .org 0x75198-ORIGIN
L_00075198:
    mov r4,r2
    .org 0x7519a-ORIGIN
L_0007519a:
    extu.w r2,r6
    .org 0x7519c-ORIGIN
L_0007519c:
    mov #0x19,r2
    .org 0x7519e-ORIGIN
L_0007519e:
    mov r6,r4
    .org 0x751a0-ORIGIN
L_000751a0:
    mul.l r5,r2
    .org 0x751a2-ORIGIN
L_000751a2:
    shll2 r4
    .org 0x751a4-ORIGIN
L_000751a4:
    shll2 r4
    .org 0x751a6-ORIGIN
L_000751a6:
    sts macl,r2
    .org 0x751a8-ORIGIN
L_000751a8:
    sub r6,r4
    .org 0x751aa-ORIGIN
L_000751aa:
    shll8 r4
    .org 0x751ac-ORIGIN
L_000751ac:
    shll2 r4
    .org 0x751ae-ORIGIN
L_000751ae:
    cmp/pz r2
    .org 0x751b0-ORIGIN
L_000751b0:
    bt/s L_000751b6
    .org 0x751b2-ORIGIN
L_000751b2:
    shll2 r4
    .org 0x751b4-ORIGIN
L_000751b4:
    add #0x7,r2
    .org 0x751b6-ORIGIN
L_000751b6:
    shar r2
    .org 0x751b8-ORIGIN
L_000751b8:
    mov.l P_00075220,r6
    .org 0x751ba-ORIGIN
L_000751ba:
    shar r2
    .org 0x751bc-ORIGIN
L_000751bc:
    mov r4,r1
    .org 0x751be-ORIGIN
L_000751be:
    shar r2
    .org 0x751c0-ORIGIN
L_000751c0:
    jsr @r6
    .org 0x751c2-ORIGIN
L_000751c2:
    mov r2,r0
    .org 0x751c4-ORIGIN
L_000751c4:
    mov #-0x1,r5
    .org 0x751c6-ORIGIN
L_000751c6:
    extu.w r5,r5
    .org 0x751c8-ORIGIN
L_000751c8:
    cmp/hi r5,r0
    .org 0x751ca-ORIGIN
L_000751ca:
    bf/s L_000751d4
    .org 0x751cc-ORIGIN
L_000751cc:
    mov r0,r2
    .org 0x751ce-ORIGIN
L_000751ce:
    bra L_000751d4
    .org 0x751d0-ORIGIN
L_000751d0:
    mov r5,r2
    .org 0x751d2-ORIGIN
L_000751d2:
    mov #-0x1,r2
    .org 0x751d4-ORIGIN
L_000751d4:
    mov.w P_00075212,r0
    .org 0x751d6-ORIGIN
L_000751d6:
    extu.w r2,r6
    .org 0x751d8-ORIGIN
L_000751d8:
    mov.l P_00075224,r5
    .org 0x751da-ORIGIN
L_000751da:
    mov.w r2,@(r0,r14)
    .org 0x751dc-ORIGIN
L_000751dc:
    mov.w @r5,r2
    .org 0x751de-ORIGIN
L_000751de:
    mov #-0x1,r5
    .org 0x751e0-ORIGIN
L_000751e0:
    extu.w r5,r5
    .org 0x751e2-ORIGIN
L_000751e2:
    extu.w r2,r2
    .org 0x751e4-ORIGIN
L_000751e4:
    mul.l r6,r2
    .org 0x751e6-ORIGIN
L_000751e6:
    sts macl,r6
    .org 0x751e8-ORIGIN
L_000751e8:
    shll r6
    .org 0x751ea-ORIGIN
L_000751ea:
    subc r2,r2
    .org 0x751ec-ORIGIN
L_000751ec:
    xtrct r2,r6
    .org 0x751ee-ORIGIN
L_000751ee:
    cmp/hi r5,r6
    .org 0x751f0-ORIGIN
L_000751f0:
    bt L_000751f4
    .org 0x751f2-ORIGIN
L_000751f2:
    mov r6,r5
    .org 0x751f4-ORIGIN
L_000751f4:
    mov.w P_00075214,r0
    .org 0x751f6-ORIGIN
L_000751f6:
    mov.l P_00075228,r4
    .org 0x751f8-ORIGIN
L_000751f8:
    mov.l P_0007522c,r2
    .org 0x751fa-ORIGIN
L_000751fa:
    mov.w r5,@(r0,r14)
    .org 0x751fc-ORIGIN
L_000751fc:
    jsr @r2
    .org 0x751fe-ORIGIN
L_000751fe:
    extu.w r5,r5
    .org 0x75200-ORIGIN
L_00075200:
    mov r0,r2
    .org 0x75202-ORIGIN
L_00075202:
    mov.w P_00075216,r0
    .org 0x75204-ORIGIN
L_00075204:
    mov.w r2,@(r0,r14)
    .org 0x75206-ORIGIN
L_00075206:
    lds.l @r15+,macl
    .org 0x75208-ORIGIN
L_00075208:
    lds.l @r15+,pr
    .org 0x7520a-ORIGIN
L_0007520a:
    rts
    .org 0x7520c-ORIGIN
L_0007520c:
    mov.l @r15+,r14
    .org 0x7520e-ORIGIN
P_0007520e:
    .byte 0x04
    .org 0x7520f-ORIGIN
P_0007520f:
    .byte 0x76
    .org 0x75210-ORIGIN
P_00075210:
    .byte 0x02
    .org 0x75211-ORIGIN
P_00075211:
    .byte 0xf6
    .org 0x75212-ORIGIN
P_00075212:
    .byte 0x05
    .org 0x75213-ORIGIN
P_00075213:
    .byte 0x56
    .org 0x75214-ORIGIN
P_00075214:
    .byte 0x04
    .org 0x75215-ORIGIN
P_00075215:
    .byte 0x26
    .org 0x75216-ORIGIN
P_00075216:
    .byte 0x07
    .org 0x75217-ORIGIN
P_00075217:
    .byte 0x16
    .org 0x75218-ORIGIN
P_00075218:
    .byte 0xff
    .org 0x75219-ORIGIN
P_00075219:
    .byte 0xff
    .org 0x7521a-ORIGIN
P_0007521a:
    .byte 0x12
    .org 0x7521b-ORIGIN
P_0007521b:
    .byte 0x8c
    .org 0x7521c-ORIGIN
P_0007521c:
    .byte 0xff
    .org 0x7521d-ORIGIN
P_0007521d:
    .byte 0xff
    .org 0x7521e-ORIGIN
P_0007521e:
    .byte 0x10
    .org 0x7521f-ORIGIN
P_0007521f:
    .byte 0x94
    .org 0x75220-ORIGIN
P_00075220:
    .byte 0x00
    .org 0x75221-ORIGIN
P_00075221:
    .byte 0x02
    .org 0x75222-ORIGIN
P_00075222:
    .byte 0x1c
    .org 0x75223-ORIGIN
P_00075223:
    .byte 0xe0
    .org 0x75224-ORIGIN
P_00075224:
    .byte 0x00
    .org 0x75225-ORIGIN
P_00075225:
    .byte 0x00
    .org 0x75226-ORIGIN
P_00075226:
    .byte 0x92
    .org 0x75227-ORIGIN
P_00075227:
    .byte 0x0e
    .org 0x75228-ORIGIN
P_00075228:
    .byte 0x00
    .org 0x75229-ORIGIN
P_00075229:
    .byte 0x01
    .org 0x7522a-ORIGIN
P_0007522a:
    .byte 0x57
    .org 0x7522b-ORIGIN
P_0007522b:
    .byte 0x70
    .org 0x7522c-ORIGIN
P_0007522c:
    .byte 0x00
    .org 0x7522d-ORIGIN
P_0007522d:
    .byte 0x02
    .org 0x7522e-ORIGIN
P_0007522e:
    .byte 0x63
    .org 0x7522f-ORIGIN
P_0007522f:
    .byte 0xf4
    .org 0x7654c-ORIGIN
L_0007654c:
    mov.l r8,@-r15
    .org 0x7654e-ORIGIN
L_0007654e:
    mov.l r9,@-r15
    .org 0x76550-ORIGIN
L_00076550:
    mov.l r10,@-r15
    .org 0x76552-ORIGIN
L_00076552:
    mov.l r11,@-r15
    .org 0x76554-ORIGIN
L_00076554:
    mov.l r12,@-r15
    .org 0x76556-ORIGIN
L_00076556:
    mov.l r13,@-r15
    .org 0x76558-ORIGIN
L_00076558:
    mov.l r14,@-r15
    .org 0x7655a-ORIGIN
L_0007655a:
    sts.l pr,@-r15
    .org 0x7655c-ORIGIN
L_0007655c:
    sts.l macl,@-r15
    .org 0x7655e-ORIGIN
L_0007655e:
    stc.l gbr,@-r15
    .org 0x76560-ORIGIN
L_00076560:
    mov.l P_00076748,r0
    .org 0x76562-ORIGIN
L_00076562:
    ldc r0,gbr
    .org 0x76564-ORIGIN
L_00076564:
    mov.l P_00076748,r8
    .org 0x76566-ORIGIN
L_00076566:
    mov.w P_000766b4,r0
    .org 0x76568-ORIGIN
L_00076568:
    mov.w @(r0,r8),r6
    .org 0x7656a-ORIGIN
L_0007656a:
    mov.w P_000766b6,r0
    .org 0x7656c-ORIGIN
L_0007656c:
    extu.w r6,r6
    .org 0x7656e-ORIGIN
L_0007656e:
    mov.w @(r0,r8),r2
    .org 0x76570-ORIGIN
L_00076570:
    extu.w r2,r2
    .org 0x76572-ORIGIN
L_00076572:
    mul.l r6,r2
    .org 0x76574-ORIGIN
L_00076574:
    mov.l P_0007674c,r6
    .org 0x76576-ORIGIN
L_00076576:
    jsr @r6
    .org 0x76578-ORIGIN
L_00076578:
    sts macl,r0
    .org 0x7657a-ORIGIN
L_0007657a:
    mov #-0x1,r2
    .org 0x7657c-ORIGIN
L_0007657c:
    extu.w r2,r2
    .org 0x7657e-ORIGIN
L_0007657e:
    cmp/hi r2,r0
    .org 0x76580-ORIGIN
L_00076580:
    bf/s L_00076586
    .org 0x76582-ORIGIN
L_00076582:
    mov r0,r6
    .org 0x76584-ORIGIN
L_00076584:
    mov r2,r6
    .org 0x76586-ORIGIN
L_00076586:
    mov.w P_000766b8,r0
    .org 0x76588-ORIGIN
L_00076588:
    mov #-0x80,r13
    .org 0x7658a-ORIGIN
L_0007658a:
    mov.l P_00076750,r5
    .org 0x7658c-ORIGIN
L_0007658c:
    shll8 r13
    .org 0x7658e-ORIGIN
L_0007658e:
    mov.w @(r0,r8),r2
    .org 0x76590-ORIGIN
L_00076590:
    mov.l P_00076754,r10
    .org 0x76592-ORIGIN
L_00076592:
    mul.l r6,r2
    .org 0x76594-ORIGIN
L_00076594:
    mov.w @r5,r2
    .org 0x76596-ORIGIN
L_00076596:
    sts macl,r6
    .org 0x76598-ORIGIN
L_00076598:
    extu.w r2,r0
    .org 0x7659a-ORIGIN
L_0007659a:
    jsr @r10
    .org 0x7659c-ORIGIN
L_0007659c:
    mov r6,r1
    .org 0x7659e-ORIGIN
L_0007659e:
    cmp/ge r13,r0
    .org 0x765a0-ORIGIN
L_000765a0:
    bt/s L_000765a6
    .org 0x765a2-ORIGIN
L_000765a2:
    mov r0,r6
    .org 0x765a4-ORIGIN
L_000765a4:
    mov r13,r6
    .org 0x765a6-ORIGIN
L_000765a6:
    mov.w P_000766ba,r12
    .org 0x765a8-ORIGIN
L_000765a8:
    cmp/gt r12,r6
    .org 0x765aa-ORIGIN
L_000765aa:
    bf/s L_000765b0
    .org 0x765ac-ORIGIN
L_000765ac:
    mov r6,r2
    .org 0x765ae-ORIGIN
L_000765ae:
    mov r12,r2
    .org 0x765b0-ORIGIN
L_000765b0:
    mov.l P_00076758,r9
    .org 0x765b2-ORIGIN
L_000765b2:
    mov r2,r0
    .org 0x765b4-ORIGIN
L_000765b4:
    mov.w r0,@(0x1ce,gbr)
    .org 0x765b6-ORIGIN
L_000765b6:
    mov #0x3e,r0
    .org 0x765b8-ORIGIN
L_000765b8:
    mov.l P_0007675c,r4
    .org 0x765ba-ORIGIN
L_000765ba:
    mov.w @(r0,r9),r7
    .org 0x765bc-ORIGIN
L_000765bc:
    mov.l P_00076760,r2
    .org 0x765be-ORIGIN
L_000765be:
    mov r4,r5
    .org 0x765c0-ORIGIN
L_000765c0:
    add #0x10,r5
    .org 0x765c2-ORIGIN
L_000765c2:
    jsr @r2
    .org 0x765c4-ORIGIN
L_000765c4:
    extu.w r7,r6
    .org 0x765c6-ORIGIN
L_000765c6:
    extu.w r0,r2
    .org 0x765c8-ORIGIN
L_000765c8:
    mov.w P_000766bc,r0
    .org 0x765ca-ORIGIN
L_000765ca:
    exts.w r2,r11
    .org 0x765cc-ORIGIN
L_000765cc:
    mov.l P_00076764,r2
    .org 0x765ce-ORIGIN
L_000765ce:
    add r13,r11
    .org 0x765d0-ORIGIN
L_000765d0:
    mov.w r11,@(r0,r8)
    .org 0x765d2-ORIGIN
L_000765d2:
    mov #0x3e,r0
    .org 0x765d4-ORIGIN
L_000765d4:
    mov.w @(r0,r9),r14
    .org 0x765d6-ORIGIN
L_000765d6:
    mov.w @r2,r7
    .org 0x765d8-ORIGIN
L_000765d8:
    extu.w r14,r14
    .org 0x765da-ORIGIN
L_000765da:
    mov.l @(0x2b4,gbr),r0
    .org 0x765dc-ORIGIN
L_000765dc:
    extu.w r7,r7
    .org 0x765de-ORIGIN
L_000765de:
    mul.l r14,r7
    .org 0x765e0-ORIGIN
L_000765e0:
    mov r0,r2
    .org 0x765e2-ORIGIN
L_000765e2:
    shlr16 r2
    .org 0x765e4-ORIGIN
L_000765e4:
    mov r0,r6
    .org 0x765e6-ORIGIN
L_000765e6:
    shll16 r14
    .org 0x765e8-ORIGIN
L_000765e8:
    sts macl,r5
    .org 0x765ea-ORIGIN
L_000765ea:
    mul.l r2,r7
    .org 0x765ec-ORIGIN
L_000765ec:
    cmp/hs r14,r0
    .org 0x765ee-ORIGIN
L_000765ee:
    mov r0,r4
    .org 0x765f0-ORIGIN
L_000765f0:
    sts macl,r2
    .org 0x765f2-ORIGIN
L_000765f2:
    sub r2,r6
    .org 0x765f4-ORIGIN
L_000765f4:
    add r5,r6
    .org 0x765f6-ORIGIN
L_000765f6:
    bt/s L_00076600
    .org 0x765f8-ORIGIN
L_000765f8:
    mov r6,r7
    .org 0x765fa-ORIGIN
L_000765fa:
    cmp/eq r7,r4
    .org 0x765fc-ORIGIN
L_000765fc:
    bf L_00076600
    .org 0x765fe-ORIGIN
L_000765fe:
    add #0x1,r7
    .org 0x76600-ORIGIN
L_00076600:
    mov r7,r2
    .org 0x76602-ORIGIN
L_00076602:
    sub r4,r2
    .org 0x76604-ORIGIN
L_00076604:
    shlr8 r2
    .org 0x76606-ORIGIN
L_00076606:
    swap.w r2,r6
    .org 0x76608-ORIGIN
L_00076608:
    exts.b r6,r2
    .org 0x7660a-ORIGIN
L_0007660a:
    xtrct r2,r6
    .org 0x7660c-ORIGIN
L_0007660c:
    cmp/gt r12,r6
    .org 0x7660e-ORIGIN
L_0007660e:
    bf/s L_00076614
    .org 0x76610-ORIGIN
L_00076610:
    mov r6,r2
    .org 0x76612-ORIGIN
L_00076612:
    mov r12,r2
    .org 0x76614-ORIGIN
L_00076614:
    cmp/ge r13,r2
    .org 0x76616-ORIGIN
L_00076616:
    bt L_0007661a
    .org 0x76618-ORIGIN
L_00076618:
    mov r13,r2
    .org 0x7661a-ORIGIN
L_0007661a:
    mov.w P_000766be,r6
    .org 0x7661c-ORIGIN
L_0007661c:
    exts.w r2,r2
    .org 0x7661e-ORIGIN
L_0007661e:
    mul.l r2,r6
    .org 0x76620-ORIGIN
L_00076620:
    sts macl,r6
    .org 0x76622-ORIGIN
L_00076622:
    cmp/pz r6
    .org 0x76624-ORIGIN
L_00076624:
    bt L_0007662c
    .org 0x76626-ORIGIN
L_00076626:
    mov #-0x1,r2
    .org 0x76628-ORIGIN
L_00076628:
    extu.b r2,r2
    .org 0x7662a-ORIGIN
L_0007662a:
    add r2,r6
    .org 0x7662c-ORIGIN
L_0007662c:
    mov r6,r2
    .org 0x7662e-ORIGIN
L_0007662e:
    shlr8 r2
    .org 0x76630-ORIGIN
L_00076630:
    swap.w r2,r6
    .org 0x76632-ORIGIN
L_00076632:
    exts.b r6,r2
    .org 0x76634-ORIGIN
L_00076634:
    xtrct r2,r6
    .org 0x76636-ORIGIN
L_00076636:
    cmp/gt r12,r6
    .org 0x76638-ORIGIN
L_00076638:
    bf/s L_0007663e
    .org 0x7663a-ORIGIN
L_0007663a:
    mov r6,r2
    .org 0x7663c-ORIGIN
L_0007663c:
    mov r12,r2
    .org 0x7663e-ORIGIN
L_0007663e:
    cmp/ge r13,r2
    .org 0x76640-ORIGIN
L_00076640:
    bt L_00076644
    .org 0x76642-ORIGIN
L_00076642:
    mov r13,r2
    .org 0x76644-ORIGIN
L_00076644:
    mov r2,r5
    .org 0x76646-ORIGIN
L_00076646:
    mov.w P_000766c0,r2
    .org 0x76648-ORIGIN
L_00076648:
    mov.w P_000766c2,r0
    .org 0x7664a-ORIGIN
L_0007664a:
    add r2,r5
    .org 0x7664c-ORIGIN
L_0007664c:
    mov.l P_00076768,r2
    .org 0x7664e-ORIGIN
L_0007664e:
    extu.w r5,r5
    .org 0x76650-ORIGIN
L_00076650:
    mov.w @r2,r14
    .org 0x76652-ORIGIN
L_00076652:
    mov.w r5,@(r0,r8)
    .org 0x76654-ORIGIN
L_00076654:
    mov r7,r0
    .org 0x76656-ORIGIN
L_00076656:
    extu.w r14,r14
    .org 0x76658-ORIGIN
L_00076658:
    mov.l r0,@(0x2b4,gbr)
    .org 0x7665a-ORIGIN
L_0007665a:
    mul.l r5,r14
    .org 0x7665c-ORIGIN
L_0007665c:
    mov.l @(0x26c,gbr),r0
    .org 0x7665e-ORIGIN
L_0007665e:
    mov r0,r2
    .org 0x76660-ORIGIN
L_00076660:
    shlr16 r2
    .org 0x76662-ORIGIN
L_00076662:
    sts macl,r4
    .org 0x76664-ORIGIN
L_00076664:
    mul.l r2,r14
    .org 0x76666-ORIGIN
L_00076666:
    mov r0,r6
    .org 0x76668-ORIGIN
L_00076668:
    mov r0,r7
    .org 0x7666a-ORIGIN
L_0007666a:
    sts macl,r2
    .org 0x7666c-ORIGIN
L_0007666c:
    sub r2,r6
    .org 0x7666e-ORIGIN
L_0007666e:
    mov r5,r2
    .org 0x76670-ORIGIN
L_00076670:
    shll16 r2
    .org 0x76672-ORIGIN
L_00076672:
    cmp/hs r2,r0
    .org 0x76674-ORIGIN
L_00076674:
    bt/s L_0007667e
    .org 0x76676-ORIGIN
L_00076676:
    add r4,r6
    .org 0x76678-ORIGIN
L_00076678:
    cmp/eq r6,r7
    .org 0x7667a-ORIGIN
L_0007667a:
    bf L_0007667e
    .org 0x7667c-ORIGIN
L_0007667c:
    add #0x1,r6
    .org 0x7667e-ORIGIN
L_0007667e:
    mov r6,r0
    .org 0x76680-ORIGIN
L_00076680:
    mov r6,r2
    .org 0x76682-ORIGIN
L_00076682:
    mov #-0x80,r6
    .org 0x76684-ORIGIN
L_00076684:
    mov.l r0,@(0x26c,gbr)
    .org 0x76686-ORIGIN
L_00076686:
    shlr16 r2
    .org 0x76688-ORIGIN
L_00076688:
    mov.w P_000766c4,r0
    .org 0x7668a-ORIGIN
L_0007668a:
    shll8 r6
    .org 0x7668c-ORIGIN
L_0007668c:
    mov.l P_0007676c,r4
    .org 0x7668e-ORIGIN
L_0007668e:
    sub r6,r2
    .org 0x76690-ORIGIN
L_00076690:
    mov.w r2,@(r0,r8)
    .org 0x76692-ORIGIN
L_00076692:
    exts.w r2,r2
    .org 0x76694-ORIGIN
L_00076694:
    mov.w @(0x2,r4),r0
    .org 0x76696-ORIGIN
L_00076696:
    extu.w r0,r6
    .org 0x76698-ORIGIN
L_00076698:
    mov.w P_000766c6,r0
    .org 0x7669a-ORIGIN
L_0007669a:
    mul.l r2,r6
    .org 0x7669c-ORIGIN
L_0007669c:
    jsr @r10
    .org 0x7669e-ORIGIN
L_0007669e:
    sts macl,r1
    .org 0x766a0-ORIGIN
L_000766a0:
    cmp/ge r13,r0
    .org 0x766a2-ORIGIN
L_000766a2:
    bt/s L_000766a8
    .org 0x766a4-ORIGIN
L_000766a4:
    mov r0,r6
    .org 0x766a6-ORIGIN
L_000766a6:
    mov r13,r6
    .org 0x766a8-ORIGIN
L_000766a8:
    cmp/gt r12,r6
    .org 0x766aa-ORIGIN
L_000766aa:
    bf L_000766ae
    .org 0x766ac-ORIGIN
L_000766ac:
    mov r12,r6
    .org 0x766ae-ORIGIN
L_000766ae:
    mov.w P_000766c8,r0
    .org 0x766b0-ORIGIN
L_000766b0:
    bra L_000766ca
    .org 0x766b2-ORIGIN
L_000766b2:
    exts.w r11,r11
    .org 0x766b4-ORIGIN
P_000766b4:
    .byte 0x07
    .org 0x766b5-ORIGIN
P_000766b5:
    .byte 0x16
    .org 0x766b6-ORIGIN
P_000766b6:
    .byte 0x04
    .org 0x766b7-ORIGIN
P_000766b7:
    .byte 0xe4
    .org 0x766b8-ORIGIN
P_000766b8:
    .byte 0x06
    .org 0x766b9-ORIGIN
P_000766b9:
    .byte 0x46
    .org 0x766ba-ORIGIN
P_000766ba:
    .byte 0x7f
    .org 0x766bb-ORIGIN
P_000766bb:
    .byte 0xff
    .org 0x766bc-ORIGIN
P_000766bc:
    .byte 0x05
    .org 0x766bd-ORIGIN
P_000766bd:
    .byte 0x06
    .org 0x766be-ORIGIN
P_000766be:
    .byte 0x01
    .org 0x766bf-ORIGIN
P_000766bf:
    .byte 0x1b
    .org 0x766c0-ORIGIN
P_000766c0:
    .byte 0x80
    .org 0x766c1-ORIGIN
P_000766c1:
    .byte 0x00
    .org 0x766c2-ORIGIN
P_000766c2:
    .byte 0x02
    .org 0x766c3-ORIGIN
P_000766c3:
    .byte 0x68
    .org 0x766c4-ORIGIN
P_000766c4:
    .byte 0x02
    .org 0x766c5-ORIGIN
P_000766c5:
    .byte 0x6a
    .org 0x766c6-ORIGIN
P_000766c6:
    .byte 0x03
    .org 0x766c7-ORIGIN
P_000766c7:
    .byte 0xe8
    .org 0x766c8-ORIGIN
P_000766c8:
    .byte 0x02
    .org 0x766c9-ORIGIN
P_000766c9:
    .byte 0x7c
    .org 0x766ca-ORIGIN
L_000766ca:
    mov.w r6,@(r0,r8)
    .org 0x766cc-ORIGIN
L_000766cc:
    exts.w r6,r6
    .org 0x766ce-ORIGIN
L_000766ce:
    mov.w @(0x1ce,gbr),r0
    .org 0x766d0-ORIGIN
L_000766d0:
    sub r11,r0
    .org 0x766d2-ORIGIN
L_000766d2:
    sub r6,r0
    .org 0x766d4-ORIGIN
L_000766d4:
    cmp/ge r13,r0
    .org 0x766d6-ORIGIN
L_000766d6:
    bt/s L_000766dc
    .org 0x766d8-ORIGIN
L_000766d8:
    mov r0,r2
    .org 0x766da-ORIGIN
L_000766da:
    mov r13,r2
    .org 0x766dc-ORIGIN
L_000766dc:
    cmp/gt r12,r2
    .org 0x766de-ORIGIN
L_000766de:
    bf/s L_000766e4
    .org 0x766e0-ORIGIN
L_000766e0:
    mov r2,r14
    .org 0x766e2-ORIGIN
L_000766e2:
    mov r12,r14
    .org 0x766e4-ORIGIN
L_000766e4:
    mov.l P_0007676c,r4
    .org 0x766e6-ORIGIN
L_000766e6:
    mov r14,r6
    .org 0x766e8-ORIGIN
L_000766e8:
    mov.w P_00076742,r2
    .org 0x766ea-ORIGIN
L_000766ea:
    mov.w P_00076744,r0
    .org 0x766ec-ORIGIN
L_000766ec:
    mov.w @r4,r5
    .org 0x766ee-ORIGIN
L_000766ee:
    add r2,r6
    .org 0x766f0-ORIGIN
L_000766f0:
    mov.w r6,@(r0,r8)
    .org 0x766f2-ORIGIN
L_000766f2:
    mov #0x1,r2
    .org 0x766f4-ORIGIN
L_000766f4:
    extu.w r5,r5
    .org 0x766f6-ORIGIN
L_000766f6:
    mov.w P_00076746,r0
    .org 0x766f8-ORIGIN
L_000766f8:
    mul.l r14,r5
    .org 0x766fa-ORIGIN
L_000766fa:
    mov.w @(r0,r8),r7
    .org 0x766fc-ORIGIN
L_000766fc:
    shll16 r2
    .org 0x766fe-ORIGIN
L_000766fe:
    sub r5,r2
    .org 0x76700-ORIGIN
L_00076700:
    extu.w r7,r7
    .org 0x76702-ORIGIN
L_00076702:
    sts macl,r6
    .org 0x76704-ORIGIN
L_00076704:
    mul.l r7,r2
    .org 0x76706-ORIGIN
L_00076706:
    sts macl,r2
    .org 0x76708-ORIGIN
L_00076708:
    add r2,r6
    .org 0x7670a-ORIGIN
L_0007670a:
    swap.w r6,r2
    .org 0x7670c-ORIGIN
L_0007670c:
    exts.w r2,r2
    .org 0x7670e-ORIGIN
L_0007670e:
    cmp/eq r2,r14
    .org 0x76710-ORIGIN
L_00076710:
    bt L_00076720
    .org 0x76712-ORIGIN
L_00076712:
    cmp/eq r2,r7
    .org 0x76714-ORIGIN
L_00076714:
    bf L_00076720
    .org 0x76716-ORIGIN
L_00076716:
    cmp/gt r7,r14
    .org 0x76718-ORIGIN
L_00076718:
    bf L_0007671e
    .org 0x7671a-ORIGIN
L_0007671a:
    bra L_00076720
    .org 0x7671c-ORIGIN
L_0007671c:
    add #0x1,r2
    .org 0x7671e-ORIGIN
L_0007671e:
    add #-0x1,r2
    .org 0x76720-ORIGIN
L_00076720:
    cmp/pz r2
    .org 0x76722-ORIGIN
L_00076722:
    bt/s L_00076728
    .org 0x76724-ORIGIN
L_00076724:
    mov r2,r6
    .org 0x76726-ORIGIN
L_00076726:
    mov #0x0,r6
    .org 0x76728-ORIGIN
L_00076728:
    mov.w P_00076746,r0
    .org 0x7672a-ORIGIN
L_0007672a:
    mov.w r6,@(r0,r8)
    .org 0x7672c-ORIGIN
L_0007672c:
    ldc.l @r15+,gbr
    .org 0x7672e-ORIGIN
L_0007672e:
    lds.l @r15+,macl
    .org 0x76730-ORIGIN
L_00076730:
    lds.l @r15+,pr
    .org 0x76732-ORIGIN
L_00076732:
    mov.l @r15+,r14
    .org 0x76734-ORIGIN
L_00076734:
    mov.l @r15+,r13
    .org 0x76736-ORIGIN
L_00076736:
    mov.l @r15+,r12
    .org 0x76738-ORIGIN
L_00076738:
    mov.l @r15+,r11
    .org 0x7673a-ORIGIN
L_0007673a:
    mov.l @r15+,r10
    .org 0x7673c-ORIGIN
L_0007673c:
    mov.l @r15+,r9
    .org 0x7673e-ORIGIN
L_0007673e:
    rts
    .org 0x76740-ORIGIN
L_00076740:
    mov.l @r15+,r8
    .org 0x76742-ORIGIN
P_00076742:
    .byte 0x80
    .org 0x76743-ORIGIN
P_00076743:
    .byte 0x00
    .org 0x76744-ORIGIN
P_00076744:
    .byte 0x04
    .org 0x76745-ORIGIN
P_00076745:
    .byte 0xf2
    .org 0x76746-ORIGIN
P_00076746:
    .byte 0x04
    .org 0x76747-ORIGIN
P_00076747:
    .byte 0xf0
    .org 0x76748-ORIGIN
P_00076748:
    .byte 0xff
    .org 0x76749-ORIGIN
P_00076749:
    .byte 0xff
    .org 0x7674a-ORIGIN
P_0007674a:
    .byte 0x12
    .org 0x7674b-ORIGIN
P_0007674b:
    .byte 0x8c
    .org 0x7674c-ORIGIN
P_0007674c:
    .byte 0x00
    .org 0x7674d-ORIGIN
P_0007674d:
    .byte 0x02
    .org 0x7674e-ORIGIN
P_0007674e:
    .byte 0x24
    .org 0x7674f-ORIGIN
P_0007674f:
    .byte 0xfa
    .org 0x76750-ORIGIN
P_00076750:
    .byte 0x00
    .org 0x76751-ORIGIN
P_00076751:
    .byte 0x00
    .org 0x76752-ORIGIN
P_00076752:
    .byte 0x94
    .org 0x76753-ORIGIN
P_00076753:
    .byte 0x4e
    .org 0x76754-ORIGIN
P_00076754:
    .byte 0x00
    .org 0x76755-ORIGIN
P_00076755:
    .byte 0x02
    .org 0x76756-ORIGIN
P_00076756:
    .byte 0x1b
    .org 0x76757-ORIGIN
P_00076757:
    .byte 0xbc
    .org 0x76758-ORIGIN
P_00076758:
    .byte 0xff
    .org 0x76759-ORIGIN
P_00076759:
    .byte 0xff
    .org 0x7675a-ORIGIN
P_0007675a:
    .byte 0x11
    .org 0x7675b-ORIGIN
P_0007675b:
    .byte 0x14
    .org 0x7675c-ORIGIN
P_0007675c:
    .byte 0x00
    .org 0x7675d-ORIGIN
P_0007675d:
    .byte 0x01
    .org 0x7675e-ORIGIN
P_0007675e:
    .byte 0x52
    .org 0x7675f-ORIGIN
P_0007675f:
    .byte 0x76
    .org 0x76760-ORIGIN
P_00076760:
    .byte 0x00
    .org 0x76761-ORIGIN
P_00076761:
    .byte 0x02
    .org 0x76762-ORIGIN
P_00076762:
    .byte 0x64
    .org 0x76763-ORIGIN
P_00076763:
    .byte 0xcc
    .org 0x76764-ORIGIN
P_00076764:
    .byte 0x00
    .org 0x76765-ORIGIN
P_00076765:
    .byte 0x00
    .org 0x76766-ORIGIN
P_00076766:
    .byte 0x95
    .org 0x76767-ORIGIN
P_00076767:
    .byte 0xa0
    .org 0x76768-ORIGIN
P_00076768:
    .byte 0x00
    .org 0x76769-ORIGIN
P_00076769:
    .byte 0x00
    .org 0x7676a-ORIGIN
P_0007676a:
    .byte 0x91
    .org 0x7676b-ORIGIN
P_0007676b:
    .byte 0x8e
    .org 0x7676c-ORIGIN
P_0007676c:
    .byte 0x00
    .org 0x7676d-ORIGIN
P_0007676d:
    .byte 0x00
    .org 0x7676e-ORIGIN
P_0007676e:
    .byte 0x92
    .org 0x7676f-ORIGIN
P_0007676f:
    .byte 0x8c
