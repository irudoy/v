! Complete natural timing/remainder callers and exact real interpolation, division and remainder helpers.
    .text
    .balign 4
    .set ORIGIN,0x8290
    .org 0x8290-ORIGIN
P_00008290:
    .byte 0x00
    .org 0x83ea-ORIGIN
P_000083ea:
    .byte 0x1e
    .org 0x8710-ORIGIN
P_00008710:
    .byte 0x7c
    .org 0x8a3c-ORIGIN
P_00008a3c:
    .byte 0x64
    .org 0x8a3d-ORIGIN
P_00008a3d:
    .byte 0x64
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
    .org 0x21e14-ORIGIN
L_00021e14:
    mov.l r2,@-r15
    .org 0x21e16-ORIGIN
L_00021e16:
    tst r0,r0
    .org 0x21e18-ORIGIN
L_00021e18:
    bt L_00021ed0
    .org 0x21e1a-ORIGIN
L_00021e1a:
    mov.l r3,@-r15
    .org 0x21e1c-ORIGIN
L_00021e1c:
    mov r1,r3
    .org 0x21e1e-ORIGIN
L_00021e1e:
    rotcl r3
    .org 0x21e20-ORIGIN
L_00021e20:
    movt r3
    .org 0x21e22-ORIGIN
L_00021e22:
    cmp/pl r0
    .org 0x21e24-ORIGIN
L_00021e24:
    bt L_00021e2a
    .org 0x21e26-ORIGIN
L_00021e26:
    add #-0x1,r0
    .org 0x21e28-ORIGIN
L_00021e28:
    not r0,r0
    .org 0x21e2a-ORIGIN
L_00021e2a:
    cmp/pl r1
    .org 0x21e2c-ORIGIN
L_00021e2c:
    bt L_00021e32
    .org 0x21e2e-ORIGIN
L_00021e2e:
    add #-0x1,r1
    .org 0x21e30-ORIGIN
L_00021e30:
    not r1,r1
    .org 0x21e32-ORIGIN
L_00021e32:
    extu.w r0,r2
    .org 0x21e34-ORIGIN
L_00021e34:
    cmp/eq r2,r0
    .org 0x21e36-ORIGIN
L_00021e36:
    bf L_00021edc
    .org 0x21e38-ORIGIN
L_00021e38:
    div0u
    .org 0x21e3a-ORIGIN
L_00021e3a:
    shll8 r0
    .org 0x21e3c-ORIGIN
L_00021e3c:
    cmp/hi r1,r0
    .org 0x21e3e-ORIGIN
L_00021e3e:
    bf L_00021e68
    .org 0x21e40-ORIGIN
L_00021e40:
    div1 r0,r1
    .org 0x21e42-ORIGIN
L_00021e42:
    div1 r0,r1
    .org 0x21e44-ORIGIN
L_00021e44:
    div1 r0,r1
    .org 0x21e46-ORIGIN
L_00021e46:
    div1 r0,r1
    .org 0x21e48-ORIGIN
L_00021e48:
    div1 r0,r1
    .org 0x21e4a-ORIGIN
L_00021e4a:
    div1 r0,r1
    .org 0x21e4c-ORIGIN
L_00021e4c:
    div1 r0,r1
    .org 0x21e4e-ORIGIN
L_00021e4e:
    div1 r0,r1
    .org 0x21e50-ORIGIN
L_00021e50:
    mov r1,r2
    .org 0x21e52-ORIGIN
L_00021e52:
    bt L_00021e56
    .org 0x21e54-ORIGIN
L_00021e54:
    add r0,r2
    .org 0x21e56-ORIGIN
L_00021e56:
    shlr8 r2
    .org 0x21e58-ORIGIN
L_00021e58:
    mov r2,r0
    .org 0x21e5a-ORIGIN
L_00021e5a:
    rotcr r3
    .org 0x21e5c-ORIGIN
L_00021e5c:
    bf L_00021e62
    .org 0x21e5e-ORIGIN
L_00021e5e:
    not r0,r0
    .org 0x21e60-ORIGIN
L_00021e60:
    add #0x1,r0
    .org 0x21e62-ORIGIN
L_00021e62:
    mov.l @r15+,r3
    .org 0x21e64-ORIGIN
L_00021e64:
    rts
    .org 0x21e66-ORIGIN
L_00021e66:
    mov.l @r15+,r2
    .org 0x21e68-ORIGIN
L_00021e68:
    mov.l r4,@-r15
    .org 0x21e6a-ORIGIN
L_00021e6a:
    extu.w r1,r4
    .org 0x21e6c-ORIGIN
L_00021e6c:
    shll8 r0
    .org 0x21e6e-ORIGIN
L_00021e6e:
    shlr16 r1
    .org 0x21e70-ORIGIN
L_00021e70:
    div1 r0,r1
    .org 0x21e72-ORIGIN
L_00021e72:
    div1 r0,r1
    .org 0x21e74-ORIGIN
L_00021e74:
    div1 r0,r1
    .org 0x21e76-ORIGIN
L_00021e76:
    div1 r0,r1
    .org 0x21e78-ORIGIN
L_00021e78:
    div1 r0,r1
    .org 0x21e7a-ORIGIN
L_00021e7a:
    div1 r0,r1
    .org 0x21e7c-ORIGIN
L_00021e7c:
    div1 r0,r1
    .org 0x21e7e-ORIGIN
L_00021e7e:
    div1 r0,r1
    .org 0x21e80-ORIGIN
L_00021e80:
    div1 r0,r1
    .org 0x21e82-ORIGIN
L_00021e82:
    div1 r0,r1
    .org 0x21e84-ORIGIN
L_00021e84:
    div1 r0,r1
    .org 0x21e86-ORIGIN
L_00021e86:
    div1 r0,r1
    .org 0x21e88-ORIGIN
L_00021e88:
    div1 r0,r1
    .org 0x21e8a-ORIGIN
L_00021e8a:
    div1 r0,r1
    .org 0x21e8c-ORIGIN
L_00021e8c:
    div1 r0,r1
    .org 0x21e8e-ORIGIN
L_00021e8e:
    div1 r0,r1
    .org 0x21e90-ORIGIN
L_00021e90:
    extu.w r1,r2
    .org 0x21e92-ORIGIN
L_00021e92:
    xor r2,r1
    .org 0x21e94-ORIGIN
L_00021e94:
    add r4,r1
    .org 0x21e96-ORIGIN
L_00021e96:
    div1 r0,r1
    .org 0x21e98-ORIGIN
L_00021e98:
    div1 r0,r1
    .org 0x21e9a-ORIGIN
L_00021e9a:
    div1 r0,r1
    .org 0x21e9c-ORIGIN
L_00021e9c:
    div1 r0,r1
    .org 0x21e9e-ORIGIN
L_00021e9e:
    div1 r0,r1
    .org 0x21ea0-ORIGIN
L_00021ea0:
    div1 r0,r1
    .org 0x21ea2-ORIGIN
L_00021ea2:
    div1 r0,r1
    .org 0x21ea4-ORIGIN
L_00021ea4:
    div1 r0,r1
    .org 0x21ea6-ORIGIN
L_00021ea6:
    div1 r0,r1
    .org 0x21ea8-ORIGIN
L_00021ea8:
    div1 r0,r1
    .org 0x21eaa-ORIGIN
L_00021eaa:
    div1 r0,r1
    .org 0x21eac-ORIGIN
L_00021eac:
    div1 r0,r1
    .org 0x21eae-ORIGIN
L_00021eae:
    div1 r0,r1
    .org 0x21eb0-ORIGIN
L_00021eb0:
    div1 r0,r1
    .org 0x21eb2-ORIGIN
L_00021eb2:
    div1 r0,r1
    .org 0x21eb4-ORIGIN
L_00021eb4:
    div1 r0,r1
    .org 0x21eb6-ORIGIN
L_00021eb6:
    mov r1,r2
    .org 0x21eb8-ORIGIN
L_00021eb8:
    bt L_00021ebc
    .org 0x21eba-ORIGIN
L_00021eba:
    add r0,r2
    .org 0x21ebc-ORIGIN
L_00021ebc:
    mov r2,r0
    .org 0x21ebe-ORIGIN
L_00021ebe:
    shlr16 r0
    .org 0x21ec0-ORIGIN
L_00021ec0:
    rotcr r3
    .org 0x21ec2-ORIGIN
L_00021ec2:
    bf L_00021ec8
    .org 0x21ec4-ORIGIN
L_00021ec4:
    not r0,r0
    .org 0x21ec6-ORIGIN
L_00021ec6:
    add #0x1,r0
    .org 0x21ec8-ORIGIN
L_00021ec8:
    mov.l @r15+,r4
    .org 0x21eca-ORIGIN
L_00021eca:
    mov.l @r15+,r3
    .org 0x21ecc-ORIGIN
L_00021ecc:
    rts
    .org 0x21ece-ORIGIN
L_00021ece:
    mov.l @r15+,r2
    .org 0x21ed0-ORIGIN
L_00021ed0:
    mov.l P_00021f38,r1
    .org 0x21ed2-ORIGIN
L_00021ed2:
    mov.l P_00021f3c,r2
    .org 0x21ed4-ORIGIN
L_00021ed4:
    mov.l r2,@r1
    .org 0x21ed6-ORIGIN
L_00021ed6:
    mov #0x0,r0
    .org 0x21ed8-ORIGIN
L_00021ed8:
    rts
    .org 0x21eda-ORIGIN
L_00021eda:
    mov.l @r15+,r2
    .org 0x21edc-ORIGIN
L_00021edc:
    div0u
    .org 0x21ede-ORIGIN
L_00021ede:
    extu.w r1,r2
    .org 0x21ee0-ORIGIN
L_00021ee0:
    shll16 r2
    .org 0x21ee2-ORIGIN
L_00021ee2:
    shlr16 r1
    .org 0x21ee4-ORIGIN
L_00021ee4:
    rotcl r2
    .org 0x21ee6-ORIGIN
L_00021ee6:
    div1 r0,r1
    .org 0x21ee8-ORIGIN
L_00021ee8:
    rotcl r2
    .org 0x21eea-ORIGIN
L_00021eea:
    div1 r0,r1
    .org 0x21eec-ORIGIN
L_00021eec:
    rotcl r2
    .org 0x21eee-ORIGIN
L_00021eee:
    div1 r0,r1
    .org 0x21ef0-ORIGIN
L_00021ef0:
    rotcl r2
    .org 0x21ef2-ORIGIN
L_00021ef2:
    div1 r0,r1
    .org 0x21ef4-ORIGIN
L_00021ef4:
    rotcl r2
    .org 0x21ef6-ORIGIN
L_00021ef6:
    div1 r0,r1
    .org 0x21ef8-ORIGIN
L_00021ef8:
    rotcl r2
    .org 0x21efa-ORIGIN
L_00021efa:
    div1 r0,r1
    .org 0x21efc-ORIGIN
L_00021efc:
    rotcl r2
    .org 0x21efe-ORIGIN
L_00021efe:
    div1 r0,r1
    .org 0x21f00-ORIGIN
L_00021f00:
    rotcl r2
    .org 0x21f02-ORIGIN
L_00021f02:
    div1 r0,r1
    .org 0x21f04-ORIGIN
L_00021f04:
    rotcl r2
    .org 0x21f06-ORIGIN
L_00021f06:
    div1 r0,r1
    .org 0x21f08-ORIGIN
L_00021f08:
    rotcl r2
    .org 0x21f0a-ORIGIN
L_00021f0a:
    div1 r0,r1
    .org 0x21f0c-ORIGIN
L_00021f0c:
    rotcl r2
    .org 0x21f0e-ORIGIN
L_00021f0e:
    div1 r0,r1
    .org 0x21f10-ORIGIN
L_00021f10:
    rotcl r2
    .org 0x21f12-ORIGIN
L_00021f12:
    div1 r0,r1
    .org 0x21f14-ORIGIN
L_00021f14:
    rotcl r2
    .org 0x21f16-ORIGIN
L_00021f16:
    div1 r0,r1
    .org 0x21f18-ORIGIN
L_00021f18:
    rotcl r2
    .org 0x21f1a-ORIGIN
L_00021f1a:
    div1 r0,r1
    .org 0x21f1c-ORIGIN
L_00021f1c:
    rotcl r2
    .org 0x21f1e-ORIGIN
L_00021f1e:
    div1 r0,r1
    .org 0x21f20-ORIGIN
L_00021f20:
    rotcl r2
    .org 0x21f22-ORIGIN
L_00021f22:
    div1 r0,r1
    .org 0x21f24-ORIGIN
L_00021f24:
    bt L_00021f28
    .org 0x21f26-ORIGIN
L_00021f26:
    add r0,r1
    .org 0x21f28-ORIGIN
L_00021f28:
    mov r1,r0
    .org 0x21f2a-ORIGIN
L_00021f2a:
    rotcr r3
    .org 0x21f2c-ORIGIN
L_00021f2c:
    bf L_00021f32
    .org 0x21f2e-ORIGIN
L_00021f2e:
    not r0,r0
    .org 0x21f30-ORIGIN
L_00021f30:
    add #0x1,r0
    .org 0x21f32-ORIGIN
L_00021f32:
    mov.l @r15+,r3
    .org 0x21f34-ORIGIN
L_00021f34:
    rts
    .org 0x21f36-ORIGIN
L_00021f36:
    mov.l @r15+,r2
    .org 0x21f38-ORIGIN
P_00021f38:
    .byte 0xff
    .org 0x21f39-ORIGIN
P_00021f39:
    .byte 0xff
    .org 0x21f3a-ORIGIN
P_00021f3a:
    .byte 0x98
    .org 0x21f3b-ORIGIN
P_00021f3b:
    .byte 0x18
    .org 0x21f3c-ORIGIN
P_00021f3c:
    .byte 0x00
    .org 0x21f3d-ORIGIN
P_00021f3d:
    .byte 0x00
    .org 0x21f3e-ORIGIN
P_00021f3e:
    .byte 0x04
    .org 0x21f3f-ORIGIN
P_00021f3f:
    .byte 0x4e
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
    .org 0x4d99c-ORIGIN
L_0004d99c:
    mov.l r12,@-r15
    .org 0x4d99e-ORIGIN
L_0004d99e:
    mov.l r13,@-r15
    .org 0x4d9a0-ORIGIN
L_0004d9a0:
    mov.l r14,@-r15
    .org 0x4d9a2-ORIGIN
L_0004d9a2:
    sts.l pr,@-r15
    .org 0x4d9a4-ORIGIN
L_0004d9a4:
    sts.l macl,@-r15
    .org 0x4d9a6-ORIGIN
L_0004d9a6:
    stc.l gbr,@-r15
    .org 0x4d9a8-ORIGIN
L_0004d9a8:
    mov.l P_0004dba0,r0
    .org 0x4d9aa-ORIGIN
L_0004d9aa:
    ldc r0,gbr
    .org 0x4d9ac-ORIGIN
L_0004d9ac:
    mov.l P_0004dba4,r2
    .org 0x4d9ae-ORIGIN
L_0004d9ae:
    mov.l P_0004dba8,r7
    .org 0x4d9b0-ORIGIN
L_0004d9b0:
    mov.b @r2,r0
    .org 0x4d9b2-ORIGIN
L_0004d9b2:
    and #0x20,r0
    .org 0x4d9b4-ORIGIN
L_0004d9b4:
    mov r0,r6
    .org 0x4d9b6-ORIGIN
L_0004d9b6:
    mov.b @(0x5,r7),r0
    .org 0x4d9b8-ORIGIN
L_0004d9b8:
    tst #0x20,r0
    .org 0x4d9ba-ORIGIN
L_0004d9ba:
    bf L_0004d9d8
    .org 0x4d9bc-ORIGIN
L_0004d9bc:
    mov.b @(0xb,r7),r0
    .org 0x4d9be-ORIGIN
L_0004d9be:
    tst #0x4,r0
    .org 0x4d9c0-ORIGIN
L_0004d9c0:
    bf L_0004d9d8
    .org 0x4d9c2-ORIGIN
L_0004d9c2:
    mov.l P_0004dbac,r14
    .org 0x4d9c4-ORIGIN
L_0004d9c4:
    mov #0x25,r0
    .org 0x4d9c6-ORIGIN
L_0004d9c6:
    tst r6,r6
    .org 0x4d9c8-ORIGIN
L_0004d9c8:
    mov.b @(r0,r14),r5
    .org 0x4d9ca-ORIGIN
L_0004d9ca:
    neg r5,r0
    .org 0x4d9cc-ORIGIN
L_0004d9cc:
    bt/s L_0004da2a
    .org 0x4d9ce-ORIGIN
L_0004d9ce:
    mov.w r0,@(0x2,r14)
    .org 0x4d9d0-ORIGIN
L_0004d9d0:
    mov #0x26,r0
    .org 0x4d9d2-ORIGIN
L_0004d9d2:
    mov.b @(r0,r14),r6
    .org 0x4d9d4-ORIGIN
L_0004d9d4:
    bra L_0004da28
    .org 0x4d9d6-ORIGIN
L_0004d9d6:
    neg r6,r0
    .org 0x4d9d8-ORIGIN
L_0004d9d8:
    tst r6,r6
    .org 0x4d9da-ORIGIN
L_0004d9da:
    bf L_0004d9f6
    .org 0x4d9dc-ORIGIN
L_0004d9dc:
    mov.l P_0004dbac,r14
    .org 0x4d9de-ORIGIN
L_0004d9de:
    mov #0x25,r0
    .org 0x4d9e0-ORIGIN
L_0004d9e0:
    mov.l P_0004dbb0,r4
    .org 0x4d9e2-ORIGIN
L_0004d9e2:
    mov.b @(r0,r14),r2
    .org 0x4d9e4-ORIGIN
L_0004d9e4:
    mov.b @(0x2,r4),r0
    .org 0x4d9e6-ORIGIN
L_0004d9e6:
    neg r2,r6
    .org 0x4d9e8-ORIGIN
L_0004d9e8:
    cmp/gt r6,r0
    .org 0x4d9ea-ORIGIN
L_0004d9ea:
    bt/s L_0004d9f0
    .org 0x4d9ec-ORIGIN
L_0004d9ec:
    mov r0,r2
    .org 0x4d9ee-ORIGIN
L_0004d9ee:
    mov r2,r6
    .org 0x4d9f0-ORIGIN
L_0004d9f0:
    mov r6,r0
    .org 0x4d9f2-ORIGIN
L_0004d9f2:
    bra L_0004da2a
    .org 0x4d9f4-ORIGIN
L_0004d9f4:
    mov.w r0,@(0x2,r14)
    .org 0x4d9f6-ORIGIN
L_0004d9f6:
    mov.l P_0004dbb4,r6
    .org 0x4d9f8-ORIGIN
L_0004d9f8:
    mov.l P_0004dbb0,r4
    .org 0x4d9fa-ORIGIN
L_0004d9fa:
    mov.w @(0x6,r6),r0
    .org 0x4d9fc-ORIGIN
L_0004d9fc:
    mov.l P_0004dbac,r14
    .org 0x4d9fe-ORIGIN
L_0004d9fe:
    extu.w r0,r6
    .org 0x4da00-ORIGIN
L_0004da00:
    mov.b @(0x2,r4),r0
    .org 0x4da02-ORIGIN
L_0004da02:
    shlr8 r6
    .org 0x4da04-ORIGIN
L_0004da04:
    mov r0,r5
    .org 0x4da06-ORIGIN
L_0004da06:
    mov r0,r2
    .org 0x4da08-ORIGIN
L_0004da08:
    mov #0x26,r0
    .org 0x4da0a-ORIGIN
L_0004da0a:
    mov.b @(r0,r14),r4
    .org 0x4da0c-ORIGIN
L_0004da0c:
    sub r6,r2
    .org 0x4da0e-ORIGIN
L_0004da0e:
    exts.w r2,r2
    .org 0x4da10-ORIGIN
L_0004da10:
    neg r4,r6
    .org 0x4da12-ORIGIN
L_0004da12:
    cmp/gt r6,r2
    .org 0x4da14-ORIGIN
L_0004da14:
    bf L_0004da18
    .org 0x4da16-ORIGIN
L_0004da16:
    mov r6,r2
    .org 0x4da18-ORIGIN
L_0004da18:
    cmp/gt r6,r5
    .org 0x4da1a-ORIGIN
L_0004da1a:
    mov r2,r0
    .org 0x4da1c-ORIGIN
L_0004da1c:
    bf/s L_0004da24
    .org 0x4da1e-ORIGIN
L_0004da1e:
    mov.w r0,@(0x2,r14)
    .org 0x4da20-ORIGIN
L_0004da20:
    bra L_0004da26
    .org 0x4da22-ORIGIN
L_0004da22:
    mov r6,r2
    .org 0x4da24-ORIGIN
L_0004da24:
    exts.b r5,r2
    .org 0x4da26-ORIGIN
L_0004da26:
    mov r2,r0
    .org 0x4da28-ORIGIN
L_0004da28:
    mov.w r0,@(0x4,r14)
    .org 0x4da2a-ORIGIN
L_0004da2a:
    mov.l P_0004dbb8,r12
    .org 0x4da2c-ORIGIN
L_0004da2c:
    mov.b @r12,r5
    .org 0x4da2e-ORIGIN
L_0004da2e:
    tst r5,r5
    .org 0x4da30-ORIGIN
L_0004da30:
    bt L_0004da70
    .org 0x4da32-ORIGIN
L_0004da32:
    mov.b @(0x2,r7),r0
    .org 0x4da34-ORIGIN
L_0004da34:
    mov r0,r2
    .org 0x4da36-ORIGIN
L_0004da36:
    and #0x2,r0
    .org 0x4da38-ORIGIN
L_0004da38:
    mov r0,r6
    .org 0x4da3a-ORIGIN
L_0004da3a:
    mov r2,r0
    .org 0x4da3c-ORIGIN
L_0004da3c:
    tst #0x1,r0
    .org 0x4da3e-ORIGIN
L_0004da3e:
    bt L_0004da5e
    .org 0x4da40-ORIGIN
L_0004da40:
    tst r6,r6
    .org 0x4da42-ORIGIN
L_0004da42:
    bf L_0004da5e
    .org 0x4da44-ORIGIN
L_0004da44:
    mov.l P_0004dbbc,r13
    .org 0x4da46-ORIGIN
L_0004da46:
    mov #0x48,r0
    .org 0x4da48-ORIGIN
L_0004da48:
    mov.l P_0004dba0,r4
    .org 0x4da4a-ORIGIN
L_0004da4a:
    mov.b @(r0,r13),r2
    .org 0x4da4c-ORIGIN
L_0004da4c:
    mov.w P_0004daa4,r0
    .org 0x4da4e-ORIGIN
L_0004da4e:
    mov.l P_0004dbc0,r6
    .org 0x4da50-ORIGIN
L_0004da50:
    mov.b r2,@(r0,r4)
    .org 0x4da52-ORIGIN
L_0004da52:
    mov.b @r7,r0
    .org 0x4da54-ORIGIN
L_0004da54:
    or #0x40,r0
    .org 0x4da56-ORIGIN
L_0004da56:
    mov.b r0,@r7
    .org 0x4da58-ORIGIN
L_0004da58:
    mov r5,r0
    .org 0x4da5a-ORIGIN
L_0004da5a:
    bra L_0004da76
    .org 0x4da5c-ORIGIN
L_0004da5c:
    mov.b r0,@(0x1,r6)
    .org 0x4da5e-ORIGIN
L_0004da5e:
    tst r6,r6
    .org 0x4da60-ORIGIN
L_0004da60:
    bf L_0004da70
    .org 0x4da62-ORIGIN
L_0004da62:
    mov.l @(0x4,gbr),r0
    .org 0x4da64-ORIGIN
L_0004da64:
    mov.l P_0004dba0,r4
    .org 0x4da66-ORIGIN
L_0004da66:
    mov r0,r3
    .org 0x4da68-ORIGIN
L_0004da68:
    mov.w P_0004daa4,r0
    .org 0x4da6a-ORIGIN
L_0004da6a:
    mov.b @(r0,r4),r2
    .org 0x4da6c-ORIGIN
L_0004da6c:
    cmp/eq r3,r2
    .org 0x4da6e-ORIGIN
L_0004da6e:
    bf L_0004da76
    .org 0x4da70-ORIGIN
L_0004da70:
    mov.b @r7,r0
    .org 0x4da72-ORIGIN
L_0004da72:
    and #0xbf,r0
    .org 0x4da74-ORIGIN
L_0004da74:
    mov.b r0,@r7
    .org 0x4da76-ORIGIN
L_0004da76:
    mov.b @(0xc,r7),r0
    .org 0x4da78-ORIGIN
L_0004da78:
    tst #0x2,r0
    .org 0x4da7a-ORIGIN
L_0004da7a:
    bf L_0004db74
    .org 0x4da7c-ORIGIN
L_0004da7c:
    mov.l P_0004dbbc,r13
    .org 0x4da7e-ORIGIN
L_0004da7e:
    mov #0x4e,r0
    .org 0x4da80-ORIGIN
L_0004da80:
    mov.l P_0004dbc4,r4
    .org 0x4da82-ORIGIN
L_0004da82:
    mov.w @(r0,r13),r7
    .org 0x4da84-ORIGIN
L_0004da84:
    mov.l P_0004dbc8,r5
    .org 0x4da86-ORIGIN
L_0004da86:
    mov.l P_0004dbcc,r2
    .org 0x4da88-ORIGIN
L_0004da88:
    jsr @r2
    .org 0x4da8a-ORIGIN
L_0004da8a:
    extu.w r7,r6
    .org 0x4da8c-ORIGIN
L_0004da8c:
    mov.l P_0004dbd0,r5
    .org 0x4da8e-ORIGIN
L_0004da8e:
    mov r0,r6
    .org 0x4da90-ORIGIN
L_0004da90:
    mov.w r0,@(0xc,gbr)
    .org 0x4da92-ORIGIN
L_0004da92:
    mov.b @r5,r0
    .org 0x4da94-ORIGIN
L_0004da94:
    tst #0x20,r0
    .org 0x4da96-ORIGIN
L_0004da96:
    bt L_0004daa8
    .org 0x4da98-ORIGIN
L_0004da98:
    mov.l P_0004dbd4,r5
    .org 0x4da9a-ORIGIN
L_0004da9a:
    mov.l P_0004dba0,r4
    .org 0x4da9c-ORIGIN
L_0004da9c:
    mov.b @r5,r2
    .org 0x4da9e-ORIGIN
L_0004da9e:
    mov.w P_0004daa6,r0
    .org 0x4daa0-ORIGIN
L_0004daa0:
    bra L_0004dab4
    .org 0x4daa2-ORIGIN
L_0004daa2:
    mov.b r2,@(r0,r4)
    .org 0x4daa4-ORIGIN
P_0004daa4:
    .byte 0x02
    .org 0x4daa5-ORIGIN
P_0004daa5:
    .byte 0xa9
    .org 0x4daa6-ORIGIN
P_0004daa6:
    .byte 0x02
    .org 0x4daa7-ORIGIN
P_0004daa7:
    .byte 0x78
    .org 0x4daa8-ORIGIN
L_0004daa8:
    mov.l P_0004dbd8,r2
    .org 0x4daaa-ORIGIN
L_0004daaa:
    mov.l P_0004dba0,r4
    .org 0x4daac-ORIGIN
L_0004daac:
    mov.b @r2,r5
    .org 0x4daae-ORIGIN
L_0004daae:
    mov.w P_0004db9c,r0
    .org 0x4dab0-ORIGIN
L_0004dab0:
    mov r5,r2
    .org 0x4dab2-ORIGIN
L_0004dab2:
    mov.b r5,@(r0,r4)
    .org 0x4dab4-ORIGIN
L_0004dab4:
    extu.w r6,r6
    .org 0x4dab6-ORIGIN
L_0004dab6:
    extu.b r2,r2
    .org 0x4dab8-ORIGIN
L_0004dab8:
    mul.l r6,r2
    .org 0x4daba-ORIGIN
L_0004daba:
    mov.l P_0004dbdc,r6
    .org 0x4dabc-ORIGIN
L_0004dabc:
    mov #0x64,r0
    .org 0x4dabe-ORIGIN
L_0004dabe:
    jsr @r6
    .org 0x4dac0-ORIGIN
L_0004dac0:
    sts macl,r1
    .org 0x4dac2-ORIGIN
L_0004dac2:
    mov #-0x1,r6
    .org 0x4dac4-ORIGIN
L_0004dac4:
    extu.w r6,r6
    .org 0x4dac6-ORIGIN
L_0004dac6:
    cmp/hi r6,r0
    .org 0x4dac8-ORIGIN
L_0004dac8:
    bf/s L_0004dace
    .org 0x4daca-ORIGIN
L_0004daca:
    mov r0,r2
    .org 0x4dacc-ORIGIN
L_0004dacc:
    mov r6,r2
    .org 0x4dace-ORIGIN
L_0004dace:
    mov.l P_0004dba8,r7
    .org 0x4dad0-ORIGIN
L_0004dad0:
    extu.w r2,r6
    .org 0x4dad2-ORIGIN
L_0004dad2:
    mov r6,r0
    .org 0x4dad4-ORIGIN
L_0004dad4:
    mov.w r0,@(0x2,gbr)
    .org 0x4dad6-ORIGIN
L_0004dad6:
    mov.b @r7,r0
    .org 0x4dad8-ORIGIN
L_0004dad8:
    tst #0x40,r0
    .org 0x4dada-ORIGIN
L_0004dada:
    bt L_0004db14
    .org 0x4dadc-ORIGIN
L_0004dadc:
    mov.l P_0004dbc0,r5
    .org 0x4dade-ORIGIN
L_0004dade:
    mov.b @(0x1,r5),r0
    .org 0x4dae0-ORIGIN
L_0004dae0:
    tst r0,r0
    .org 0x4dae2-ORIGIN
L_0004dae2:
    bf L_0004db0e
    .org 0x4dae4-ORIGIN
L_0004dae4:
    mov.l P_0004dba0,r4
    .org 0x4dae6-ORIGIN
L_0004dae6:
    mov.w P_0004db9e,r0
    .org 0x4dae8-ORIGIN
L_0004dae8:
    mov.b @(r0,r4),r2
    .org 0x4daea-ORIGIN
L_0004daea:
    mov.l @(0x4,gbr),r0
    .org 0x4daec-ORIGIN
L_0004daec:
    cmp/gt r2,r0
    .org 0x4daee-ORIGIN
L_0004daee:
    bf/s L_0004dafe
    .org 0x4daf0-ORIGIN
L_0004daf0:
    mov r0,r5
    .org 0x4daf2-ORIGIN
L_0004daf2:
    mov.b @r12,r0
    .org 0x4daf4-ORIGIN
L_0004daf4:
    mov.l P_0004dbc0,r3
    .org 0x4daf6-ORIGIN
L_0004daf6:
    mov.b r0,@(0x1,r3)
    .org 0x4daf8-ORIGIN
L_0004daf8:
    exts.w r5,r0
    .org 0x4dafa-ORIGIN
L_0004dafa:
    bra L_0004db0c
    .org 0x4dafc-ORIGIN
L_0004dafc:
    add #-0x1,r0
    .org 0x4dafe-ORIGIN
L_0004dafe:
    cmp/ge r2,r5
    .org 0x4db00-ORIGIN
L_0004db00:
    bt L_0004db0e
    .org 0x4db02-ORIGIN
L_0004db02:
    mov.b @r12,r0
    .org 0x4db04-ORIGIN
L_0004db04:
    mov.l P_0004dbc0,r3
    .org 0x4db06-ORIGIN
L_0004db06:
    mov.b r0,@(0x1,r3)
    .org 0x4db08-ORIGIN
L_0004db08:
    exts.w r5,r0
    .org 0x4db0a-ORIGIN
L_0004db0a:
    add #0x1,r0
    .org 0x4db0c-ORIGIN
L_0004db0c:
    mov.l r0,@(0x4,gbr)
    .org 0x4db0e-ORIGIN
L_0004db0e:
    mov.l @(0x4,gbr),r0
    .org 0x4db10-ORIGIN
L_0004db10:
    bra L_0004db56
    .org 0x4db12-ORIGIN
L_0004db12:
    mov r0,r2
    .org 0x4db14-ORIGIN
L_0004db14:
    mov.l P_0004dbe0,r2
    .org 0x4db16-ORIGIN
L_0004db16:
    mov #0x1b,r0
    .org 0x4db18-ORIGIN
L_0004db18:
    mov.b @(r0,r2),r4
    .org 0x4db1a-ORIGIN
L_0004db1a:
    extu.b r4,r4
    .org 0x4db1c-ORIGIN
L_0004db1c:
    cmp/pl r4
    .org 0x4db1e-ORIGIN
L_0004db1e:
    bf L_0004db48
    .org 0x4db20-ORIGIN
L_0004db20:
    mov.b @(0x2,r7),r0
    .org 0x4db22-ORIGIN
L_0004db22:
    tst #0x2,r0
    .org 0x4db24-ORIGIN
L_0004db24:
    bf L_0004db48
    .org 0x4db26-ORIGIN
L_0004db26:
    mov.w @(0x2,r14),r0
    .org 0x4db28-ORIGIN
L_0004db28:
    exts.w r4,r5
    .org 0x4db2a-ORIGIN
L_0004db2a:
    mov r0,r7
    .org 0x4db2c-ORIGIN
L_0004db2c:
    mov #0x26,r0
    .org 0x4db2e-ORIGIN
L_0004db2e:
    mov.b @(r0,r13),r2
    .org 0x4db30-ORIGIN
L_0004db30:
    add r2,r7
    .org 0x4db32-ORIGIN
L_0004db32:
    neg r5,r2
    .org 0x4db34-ORIGIN
L_0004db34:
    cmp/gt r2,r7
    .org 0x4db36-ORIGIN
L_0004db36:
    bf L_0004db3c
    .org 0x4db38-ORIGIN
L_0004db38:
    exts.w r4,r4
    .org 0x4db3a-ORIGIN
L_0004db3a:
    neg r4,r7
    .org 0x4db3c-ORIGIN
L_0004db3c:
    mov #0x48,r0
    .org 0x4db3e-ORIGIN
L_0004db3e:
    mov r6,r2
    .org 0x4db40-ORIGIN
L_0004db40:
    mov.b @(r0,r13),r6
    .org 0x4db42-ORIGIN
L_0004db42:
    add r7,r6
    .org 0x4db44-ORIGIN
L_0004db44:
    bra L_0004db60
    .org 0x4db46-ORIGIN
L_0004db46:
    sub r2,r6
    .org 0x4db48-ORIGIN
L_0004db48:
    mov.w @(0x2,r14),r0
    .org 0x4db4a-ORIGIN
L_0004db4a:
    mov r0,r4
    .org 0x4db4c-ORIGIN
L_0004db4c:
    mov #0x48,r0
    .org 0x4db4e-ORIGIN
L_0004db4e:
    mov.b @(r0,r13),r2
    .org 0x4db50-ORIGIN
L_0004db50:
    add r4,r2
    .org 0x4db52-ORIGIN
L_0004db52:
    mov r2,r0
    .org 0x4db54-ORIGIN
L_0004db54:
    mov.l r0,@(0x4,gbr)
    .org 0x4db56-ORIGIN
L_0004db56:
    mov #0x26,r0
    .org 0x4db58-ORIGIN
L_0004db58:
    mov.b @(r0,r13),r5
    .org 0x4db5a-ORIGIN
L_0004db5a:
    add r5,r2
    .org 0x4db5c-ORIGIN
L_0004db5c:
    sub r6,r2
    .org 0x4db5e-ORIGIN
L_0004db5e:
    mov r2,r6
    .org 0x4db60-ORIGIN
L_0004db60:
    mov #-0x80,r2
    .org 0x4db62-ORIGIN
L_0004db62:
    cmp/ge r2,r6
    .org 0x4db64-ORIGIN
L_0004db64:
    bt/s L_0004db6a
    .org 0x4db66-ORIGIN
L_0004db66:
    mov r6,r2
    .org 0x4db68-ORIGIN
L_0004db68:
    mov #-0x80,r2
    .org 0x4db6a-ORIGIN
L_0004db6a:
    mov #0x7f,r6
    .org 0x4db6c-ORIGIN
L_0004db6c:
    cmp/gt r6,r2
    .org 0x4db6e-ORIGIN
L_0004db6e:
    bf L_0004db86
    .org 0x4db70-ORIGIN
L_0004db70:
    bra L_0004db86
    .org 0x4db72-ORIGIN
L_0004db72:
    mov #0x7f,r2
    .org 0x4db74-ORIGIN
L_0004db74:
    mov.l P_0004dbbc,r13
    .org 0x4db76-ORIGIN
L_0004db76:
    mov #0x48,r0
    .org 0x4db78-ORIGIN
L_0004db78:
    mov #0x7f,r6
    .org 0x4db7a-ORIGIN
L_0004db7a:
    mov.b @(r0,r13),r2
    .org 0x4db7c-ORIGIN
L_0004db7c:
    cmp/gt r6,r2
    .org 0x4db7e-ORIGIN
L_0004db7e:
    bf/s L_0004db84
    .org 0x4db80-ORIGIN
L_0004db80:
    mov r2,r6
    .org 0x4db82-ORIGIN
L_0004db82:
    mov #0x7f,r6
    .org 0x4db84-ORIGIN
L_0004db84:
    mov r6,r2
    .org 0x4db86-ORIGIN
L_0004db86:
    mov r2,r6
    .org 0x4db88-ORIGIN
L_0004db88:
    mov.l P_0004dbe4,r2
    .org 0x4db8a-ORIGIN
L_0004db8a:
    mov #0x4a,r0
    .org 0x4db8c-ORIGIN
L_0004db8c:
    mov.b r6,@(r0,r2)
    .org 0x4db8e-ORIGIN
L_0004db8e:
    ldc.l @r15+,gbr
    .org 0x4db90-ORIGIN
L_0004db90:
    lds.l @r15+,macl
    .org 0x4db92-ORIGIN
L_0004db92:
    lds.l @r15+,pr
    .org 0x4db94-ORIGIN
L_0004db94:
    mov.l @r15+,r14
    .org 0x4db96-ORIGIN
L_0004db96:
    mov.l @r15+,r13
    .org 0x4db98-ORIGIN
L_0004db98:
    rts
    .org 0x4db9a-ORIGIN
L_0004db9a:
    mov.l @r15+,r12
    .org 0x4db9c-ORIGIN
P_0004db9c:
    .byte 0x02
    .org 0x4db9d-ORIGIN
P_0004db9d:
    .byte 0x78
    .org 0x4db9e-ORIGIN
P_0004db9e:
    .byte 0x02
    .org 0x4db9f-ORIGIN
P_0004db9f:
    .byte 0xa9
    .org 0x4dba0-ORIGIN
P_0004dba0:
    .byte 0xff
    .org 0x4dba1-ORIGIN
P_0004dba1:
    .byte 0xff
    .org 0x4dba2-ORIGIN
P_0004dba2:
    .byte 0x1f
    .org 0x4dba3-ORIGIN
P_0004dba3:
    .byte 0xf4
    .org 0x4dba4-ORIGIN
P_0004dba4:
    .byte 0x00
    .org 0x4dba5-ORIGIN
P_0004dba5:
    .byte 0x00
    .org 0x4dba6-ORIGIN
P_0004dba6:
    .byte 0x87
    .org 0x4dba7-ORIGIN
P_0004dba7:
    .byte 0x10
    .org 0x4dba8-ORIGIN
P_0004dba8:
    .byte 0xff
    .org 0x4dba9-ORIGIN
P_0004dba9:
    .byte 0xff
    .org 0x4dbaa-ORIGIN
P_0004dbaa:
    .byte 0x24
    .org 0x4dbab-ORIGIN
P_0004dbab:
    .byte 0xc0
    .org 0x4dbac-ORIGIN
P_0004dbac:
    .byte 0xff
    .org 0x4dbad-ORIGIN
P_0004dbad:
    .byte 0xff
    .org 0x4dbae-ORIGIN
P_0004dbae:
    .byte 0x11
    .org 0x4dbaf-ORIGIN
P_0004dbaf:
    .byte 0xd4
    .org 0x4dbb0-ORIGIN
P_0004dbb0:
    .byte 0xff
    .org 0x4dbb1-ORIGIN
P_0004dbb1:
    .byte 0xff
    .org 0x4dbb2-ORIGIN
P_0004dbb2:
    .byte 0x22
    .org 0x4dbb3-ORIGIN
P_0004dbb3:
    .byte 0xf8
    .org 0x4dbb4-ORIGIN
P_0004dbb4:
    .byte 0xff
    .org 0x4dbb5-ORIGIN
P_0004dbb5:
    .byte 0xff
    .org 0x4dbb6-ORIGIN
P_0004dbb6:
    .byte 0x23
    .org 0x4dbb7-ORIGIN
P_0004dbb7:
    .byte 0xbc
    .org 0x4dbb8-ORIGIN
P_0004dbb8:
    .byte 0x00
    .org 0x4dbb9-ORIGIN
P_0004dbb9:
    .byte 0x00
    .org 0x4dbba-ORIGIN
P_0004dbba:
    .byte 0x82
    .org 0x4dbbb-ORIGIN
P_0004dbbb:
    .byte 0x90
    .org 0x4dbbc-ORIGIN
P_0004dbbc:
    .byte 0xff
    .org 0x4dbbd-ORIGIN
P_0004dbbd:
    .byte 0xff
    .org 0x4dbbe-ORIGIN
P_0004dbbe:
    .byte 0x23
    .org 0x4dbbf-ORIGIN
P_0004dbbf:
    .byte 0x30
    .org 0x4dbc0-ORIGIN
P_0004dbc0:
    .byte 0xff
    .org 0x4dbc1-ORIGIN
P_0004dbc1:
    .byte 0xff
    .org 0x4dbc2-ORIGIN
P_0004dbc2:
    .byte 0x25
    .org 0x4dbc3-ORIGIN
P_0004dbc3:
    .byte 0xfb
    .org 0x4dbc4-ORIGIN
P_0004dbc4:
    .byte 0x00
    .org 0x4dbc5-ORIGIN
P_0004dbc5:
    .byte 0x01
    .org 0x4dbc6-ORIGIN
P_0004dbc6:
    .byte 0x47
    .org 0x4dbc7-ORIGIN
P_0004dbc7:
    .byte 0xda
    .org 0x4dbc8-ORIGIN
P_0004dbc8:
    .byte 0x00
    .org 0x4dbc9-ORIGIN
P_0004dbc9:
    .byte 0x01
    .org 0x4dbca-ORIGIN
P_0004dbca:
    .byte 0x3c
    .org 0x4dbcb-ORIGIN
P_0004dbcb:
    .byte 0x48
    .org 0x4dbcc-ORIGIN
P_0004dbcc:
    .byte 0x00
    .org 0x4dbcd-ORIGIN
P_0004dbcd:
    .byte 0x02
    .org 0x4dbce-ORIGIN
P_0004dbce:
    .byte 0x64
    .org 0x4dbcf-ORIGIN
P_0004dbcf:
    .byte 0xcc
    .org 0x4dbd0-ORIGIN
P_0004dbd0:
    .byte 0xff
    .org 0x4dbd1-ORIGIN
P_0004dbd1:
    .byte 0xff
    .org 0x4dbd2-ORIGIN
P_0004dbd2:
    .byte 0x24
    .org 0x4dbd3-ORIGIN
P_0004dbd3:
    .byte 0x59
    .org 0x4dbd4-ORIGIN
P_0004dbd4:
    .byte 0x00
    .org 0x4dbd5-ORIGIN
P_0004dbd5:
    .byte 0x00
    .org 0x4dbd6-ORIGIN
P_0004dbd6:
    .byte 0x8a
    .org 0x4dbd7-ORIGIN
P_0004dbd7:
    .byte 0x3c
    .org 0x4dbd8-ORIGIN
P_0004dbd8:
    .byte 0x00
    .org 0x4dbd9-ORIGIN
P_0004dbd9:
    .byte 0x00
    .org 0x4dbda-ORIGIN
P_0004dbda:
    .byte 0x8a
    .org 0x4dbdb-ORIGIN
P_0004dbdb:
    .byte 0x3d
    .org 0x4dbdc-ORIGIN
P_0004dbdc:
    .byte 0x00
    .org 0x4dbdd-ORIGIN
P_0004dbdd:
    .byte 0x02
    .org 0x4dbde-ORIGIN
P_0004dbde:
    .byte 0x1c
    .org 0x4dbdf-ORIGIN
P_0004dbdf:
    .byte 0xe0
    .org 0x4dbe0-ORIGIN
P_0004dbe0:
    .byte 0xff
    .org 0x4dbe1-ORIGIN
P_0004dbe1:
    .byte 0xff
    .org 0x4dbe2-ORIGIN
P_0004dbe2:
    .byte 0x40
    .org 0x4dbe3-ORIGIN
P_0004dbe3:
    .byte 0xcc
    .org 0x4dbe4-ORIGIN
P_0004dbe4:
    .byte 0xff
    .org 0x4dbe5-ORIGIN
P_0004dbe5:
    .byte 0xff
    .org 0x4dbe6-ORIGIN
P_0004dbe6:
    .byte 0x12
    .org 0x4dbe7-ORIGIN
P_0004dbe7:
    .byte 0x8c
    .org 0x521a8-ORIGIN
L_000521a8:
    mov.l r14,@-r15
    .org 0x521aa-ORIGIN
L_000521aa:
    sts.l pr,@-r15
    .org 0x521ac-ORIGIN
L_000521ac:
    sts.l macl,@-r15
    .org 0x521ae-ORIGIN
L_000521ae:
    stc.l gbr,@-r15
    .org 0x521b0-ORIGIN
L_000521b0:
    mov.l P_00052298,r0
    .org 0x521b2-ORIGIN
L_000521b2:
    ldc r0,gbr
    .org 0x521b4-ORIGIN
L_000521b4:
    add #-0x8,r15
    .org 0x521b6-ORIGIN
L_000521b6:
    mov.l P_0005229c,r6
    .org 0x521b8-ORIGIN
L_000521b8:
    mov.b @r6,r0
    .org 0x521ba-ORIGIN
L_000521ba:
    tst #0x40,r0
    .org 0x521bc-ORIGIN
L_000521bc:
    bt L_000521c6
    .org 0x521be-ORIGIN
L_000521be:
    mov.l P_000522a0,r2
    .org 0x521c0-ORIGIN
L_000521c0:
    mov #0x36,r0
    .org 0x521c2-ORIGIN
L_000521c2:
    bra L_000521cc
    .org 0x521c4-ORIGIN
L_000521c4:
    mov.w @(r0,r2),r6
    .org 0x521c6-ORIGIN
L_000521c6:
    mov.l P_000522a4,r2
    .org 0x521c8-ORIGIN
L_000521c8:
    mov #0x20,r0
    .org 0x521ca-ORIGIN
L_000521ca:
    mov.w @(r0,r2),r6
    .org 0x521cc-ORIGIN
L_000521cc:
    extu.w r6,r6
    .org 0x521ce-ORIGIN
L_000521ce:
    mov.l P_000522a8,r2
    .org 0x521d0-ORIGIN
L_000521d0:
    shll2 r6
    .org 0x521d2-ORIGIN
L_000521d2:
    shll2 r6
    .org 0x521d4-ORIGIN
L_000521d4:
    mul.l r6,r2
    .org 0x521d6-ORIGIN
L_000521d6:
    stc gbr,r4
    .org 0x521d8-ORIGIN
L_000521d8:
    sts macl,r7
    .org 0x521da-ORIGIN
L_000521da:
    add #0x18,r4
    .org 0x521dc-ORIGIN
L_000521dc:
    mov #0x0,r14
    .org 0x521de-ORIGIN
L_000521de:
    shlr16 r7
    .org 0x521e0-ORIGIN
L_000521e0:
    mov #0x6,r5
    .org 0x521e2-ORIGIN
L_000521e2:
    mov.w @r4,r2
    .org 0x521e4-ORIGIN
L_000521e4:
    extu.w r2,r2
    .org 0x521e6-ORIGIN
L_000521e6:
    cmp/ge r2,r14
    .org 0x521e8-ORIGIN
L_000521e8:
    bt L_000521ec
    .org 0x521ea-ORIGIN
L_000521ea:
    mov r2,r14
    .org 0x521ec-ORIGIN
L_000521ec:
    dt r5
    .org 0x521ee-ORIGIN
L_000521ee:
    bf/s L_000521e2
    .org 0x521f0-ORIGIN
L_000521f0:
    add #0x2,r4
    .org 0x521f2-ORIGIN
L_000521f2:
    mov.w @(0x60,gbr),r0
    .org 0x521f4-ORIGIN
L_000521f4:
    extu.w r0,r6
    .org 0x521f6-ORIGIN
L_000521f6:
    cmp/ge r6,r14
    .org 0x521f8-ORIGIN
L_000521f8:
    bt L_000521fc
    .org 0x521fa-ORIGIN
L_000521fa:
    mov r6,r14
    .org 0x521fc-ORIGIN
L_000521fc:
    mul.l r7,r14
    .org 0x521fe-ORIGIN
L_000521fe:
    mov #-0x1,r4
    .org 0x52200-ORIGIN
L_00052200:
    extu.b r4,r4
    .org 0x52202-ORIGIN
L_00052202:
    sts macl,r2
    .org 0x52204-ORIGIN
L_00052204:
    shlr16 r2
    .org 0x52206-ORIGIN
L_00052206:
    cmp/hi r4,r2
    .org 0x52208-ORIGIN
L_00052208:
    bt L_0005220c
    .org 0x5220a-ORIGIN
L_0005220a:
    mov r2,r4
    .org 0x5220c-ORIGIN
L_0005220c:
    mov.l P_000522ac,r2
    .org 0x5220e-ORIGIN
L_0005220e:
    extu.b r4,r4
    .org 0x52210-ORIGIN
L_00052210:
    mov.w P_00052296,r0
    .org 0x52212-ORIGIN
L_00052212:
    mov.w @(r0,r2),r5
    .org 0x52214-ORIGIN
L_00052214:
    mov r4,r2
    .org 0x52216-ORIGIN
L_00052216:
    shll r2
    .org 0x52218-ORIGIN
L_00052218:
    extu.w r5,r5
    .org 0x5221a-ORIGIN
L_0005221a:
    cmp/ge r2,r5
    .org 0x5221c-ORIGIN
L_0005221c:
    bt L_00052222
    .org 0x5221e-ORIGIN
L_0005221e:
    bra L_00052228
    .org 0x52220-ORIGIN
L_00052220:
    mov #0x0,r5
    .org 0x52222-ORIGIN
L_00052222:
    shll r5
    .org 0x52224-ORIGIN
L_00052224:
    shll2 r4
    .org 0x52226-ORIGIN
L_00052226:
    sub r4,r5
    .org 0x52228-ORIGIN
L_00052228:
    mov.l P_000522b0,r6
    .org 0x5222a-ORIGIN
L_0005222a:
    mov.l r5,@r15
    .org 0x5222c-ORIGIN
L_0005222c:
    mov.b @(0x1,r6),r0
    .org 0x5222e-ORIGIN
L_0005222e:
    tst #0x20,r0
    .org 0x52230-ORIGIN
L_00052230:
    bt L_00052242
    .org 0x52232-ORIGIN
L_00052232:
    mov.l P_000522b4,r6
    .org 0x52234-ORIGIN
L_00052234:
    mov.b @r6,r2
    .org 0x52236-ORIGIN
L_00052236:
    extu.b r2,r2
    .org 0x52238-ORIGIN
L_00052238:
    sub r2,r5
    .org 0x5223a-ORIGIN
L_0005223a:
    cmp/pz r5
    .org 0x5223c-ORIGIN
L_0005223c:
    bt L_00052240
    .org 0x5223e-ORIGIN
L_0005223e:
    mov #0x0,r5
    .org 0x52240-ORIGIN
L_00052240:
    mov.l r5,@r15
    .org 0x52242-ORIGIN
L_00052242:
    mov.l P_000522b8,r2
    .org 0x52244-ORIGIN
L_00052244:
    mov #0x78,r0
    .org 0x52246-ORIGIN
L_00052246:
    jsr @r2
    .org 0x52248-ORIGIN
L_00052248:
    mov r5,r1
    .org 0x5224a-ORIGIN
L_0005224a:
    mov.l P_000522bc,r2
    .org 0x5224c-ORIGIN
L_0005224c:
    mov.l @r15,r1
    .org 0x5224e-ORIGIN
L_0005224e:
    mov.l r0,@(0x4,r15)
    .org 0x52250-ORIGIN
L_00052250:
    jsr @r2
    .org 0x52252-ORIGIN
L_00052252:
    mov #0x78,r0
    .org 0x52254-ORIGIN
L_00052254:
    mov #0x4,r2
    .org 0x52256-ORIGIN
L_00052256:
    cmp/ge r2,r0
    .org 0x52258-ORIGIN
L_00052258:
    bt/s L_0005225e
    .org 0x5225a-ORIGIN
L_0005225a:
    mov r0,r5
    .org 0x5225c-ORIGIN
L_0005225c:
    mov #0x4,r5
    .org 0x5225e-ORIGIN
L_0005225e:
    mov #0x74,r2
    .org 0x52260-ORIGIN
L_00052260:
    cmp/gt r2,r5
    .org 0x52262-ORIGIN
L_00052262:
    bf L_00052266
    .org 0x52264-ORIGIN
L_00052264:
    mov #0x74,r5
    .org 0x52266-ORIGIN
L_00052266:
    cmp/pz r5
    .org 0x52268-ORIGIN
L_00052268:
    bt/s L_0005226e
    .org 0x5226a-ORIGIN
L_0005226a:
    mov r5,r2
    .org 0x5226c-ORIGIN
L_0005226c:
    add #0x3,r2
    .org 0x5226e-ORIGIN
L_0005226e:
    shar r2
    .org 0x52270-ORIGIN
L_00052270:
    mov.l P_000522c0,r5
    .org 0x52272-ORIGIN
L_00052272:
    shar r2
    .org 0x52274-ORIGIN
L_00052274:
    mov r2,r0
    .org 0x52276-ORIGIN
L_00052276:
    mov.b r0,@(0x3,gbr)
    .org 0x52278-ORIGIN
L_00052278:
    mov.b @(0x5,r5),r0
    .org 0x5227a-ORIGIN
L_0005227a:
    tst #0x1,r0
    .org 0x5227c-ORIGIN
L_0005227c:
    bt L_00052282
    .org 0x5227e-ORIGIN
L_0005227e:
    mov #0x3,r6
    .org 0x52280-ORIGIN
L_00052280:
    mov.l r6,@(0x4,r15)
    .org 0x52282-ORIGIN
L_00052282:
    mov.l @(0x4,r15),r0
    .org 0x52284-ORIGIN
L_00052284:
    mov.b r0,@(0x34,gbr)
    .org 0x52286-ORIGIN
L_00052286:
    add #0x8,r15
    .org 0x52288-ORIGIN
L_00052288:
    ldc.l @r15+,gbr
    .org 0x5228a-ORIGIN
L_0005228a:
    lds.l @r15+,macl
    .org 0x5228c-ORIGIN
L_0005228c:
    lds.l @r15+,pr
    .org 0x5228e-ORIGIN
L_0005228e:
    rts
    .org 0x52290-ORIGIN
L_00052290:
    mov.l @r15+,r14
    .org 0x52296-ORIGIN
P_00052296:
    .byte 0x06
    .org 0x52297-ORIGIN
P_00052297:
    .byte 0xa2
    .org 0x52298-ORIGIN
P_00052298:
    .byte 0xff
    .org 0x52299-ORIGIN
P_00052299:
    .byte 0xff
    .org 0x5229a-ORIGIN
P_0005229a:
    .byte 0x23
    .org 0x5229b-ORIGIN
P_0005229b:
    .byte 0xbc
    .org 0x5229c-ORIGIN
P_0005229c:
    .byte 0xff
    .org 0x5229d-ORIGIN
P_0005229d:
    .byte 0xff
    .org 0x5229e-ORIGIN
P_0005229e:
    .byte 0x41
    .org 0x5229f-ORIGIN
P_0005229f:
    .byte 0x84
    .org 0x522a0-ORIGIN
P_000522a0:
    .byte 0xff
    .org 0x522a1-ORIGIN
P_000522a1:
    .byte 0xff
    .org 0x522a2-ORIGIN
P_000522a2:
    .byte 0x10
    .org 0x522a3-ORIGIN
P_000522a3:
    .byte 0x94
    .org 0x522a4-ORIGIN
P_000522a4:
    .byte 0xff
    .org 0x522a5-ORIGIN
P_000522a5:
    .byte 0xff
    .org 0x522a6-ORIGIN
P_000522a6:
    .byte 0x11
    .org 0x522a7-ORIGIN
P_000522a7:
    .byte 0x9c
    .org 0x522a8-ORIGIN
P_000522a8:
    .byte 0x00
    .org 0x522a9-ORIGIN
P_000522a9:
    .byte 0x00
    .org 0x522aa-ORIGIN
P_000522aa:
    .byte 0xc4
    .org 0x522ab-ORIGIN
P_000522ab:
    .byte 0x9b
    .org 0x522ac-ORIGIN
P_000522ac:
    .byte 0xff
    .org 0x522ad-ORIGIN
P_000522ad:
    .byte 0xff
    .org 0x522ae-ORIGIN
P_000522ae:
    .byte 0x12
    .org 0x522af-ORIGIN
P_000522af:
    .byte 0x8c
    .org 0x522b0-ORIGIN
P_000522b0:
    .byte 0xff
    .org 0x522b1-ORIGIN
P_000522b1:
    .byte 0xff
    .org 0x522b2-ORIGIN
P_000522b2:
    .byte 0x24
    .org 0x522b3-ORIGIN
P_000522b3:
    .byte 0xc8
    .org 0x522b4-ORIGIN
P_000522b4:
    .byte 0x00
    .org 0x522b5-ORIGIN
P_000522b5:
    .byte 0x00
    .org 0x522b6-ORIGIN
P_000522b6:
    .byte 0x83
    .org 0x522b7-ORIGIN
P_000522b7:
    .byte 0xea
    .org 0x522b8-ORIGIN
P_000522b8:
    .byte 0x00
    .org 0x522b9-ORIGIN
P_000522b9:
    .byte 0x02
    .org 0x522ba-ORIGIN
P_000522ba:
    .byte 0x1b
    .org 0x522bb-ORIGIN
P_000522bb:
    .byte 0xbc
    .org 0x522bc-ORIGIN
P_000522bc:
    .byte 0x00
    .org 0x522bd-ORIGIN
P_000522bd:
    .byte 0x02
    .org 0x522be-ORIGIN
P_000522be:
    .byte 0x1e
    .org 0x522bf-ORIGIN
P_000522bf:
    .byte 0x14
    .org 0x522c0-ORIGIN
P_000522c0:
    .byte 0xff
    .org 0x522c1-ORIGIN
P_000522c1:
    .byte 0xff
    .org 0x522c2-ORIGIN
P_000522c2:
    .byte 0x42
    .org 0x522c3-ORIGIN
P_000522c3:
    .byte 0x4c
