! Complete stock timing-state caller and real engine-speed curve input closure.
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
    .org 0x26140-ORIGIN
L_00026140:
    sts.l pr,@-r15
    .org 0x26142-ORIGIN
L_00026142:
    mov.l r4,@-r15
    .org 0x26144-ORIGIN
L_00026144:
    extu.b r7,r7
    .org 0x26146-ORIGIN
L_00026146:
    mov r5,r0
    .org 0x26148-ORIGIN
L_00026148:
    mov r7,r5
    .org 0x2614a-ORIGIN
L_0002614a:
    mov.l P_00026174,r7
    .org 0x2614c-ORIGIN
L_0002614c:
    jsr @r7
    .org 0x2614e-ORIGIN
L_0002614e:
    mov #0x7,r4
    .org 0x26150-ORIGIN
L_00026150:
    mov.l r4,@-r15
    .org 0x26152-ORIGIN
L_00026152:
    mov.l r5,@-r15
    .org 0x26154-ORIGIN
L_00026154:
    mov r6,r0
    .org 0x26156-ORIGIN
L_00026156:
    mov.l @(0x10,r15),r5
    .org 0x26158-ORIGIN
L_00026158:
    extu.b r5,r5
    .org 0x2615a-ORIGIN
L_0002615a:
    jsr @r7
    .org 0x2615c-ORIGIN
L_0002615c:
    mov #0x7,r4
    .org 0x2615e-ORIGIN
L_0002615e:
    mov.l @r15+,r1
    .org 0x26160-ORIGIN
L_00026160:
    mov.l @r15+,r0
    .org 0x26162-ORIGIN
L_00026162:
    mov r4,r2
    .org 0x26164-ORIGIN
L_00026164:
    mov r5,r3
    .org 0x26166-ORIGIN
L_00026166:
    mov.l @r15+,r4
    .org 0x26168-ORIGIN
L_00026168:
    lds.l @r15+,pr
    .org 0x2616a-ORIGIN
L_0002616a:
    mov.l P_00026170,r7
    .org 0x2616c-ORIGIN
L_0002616c:
    jmp @r7
    .org 0x2616e-ORIGIN
L_0002616e:
    mov #0x8,r5
    .org 0x26170-ORIGIN
P_00026170:
    .byte 0x00
    .org 0x26171-ORIGIN
P_00026171:
    .byte 0x02
    .org 0x26172-ORIGIN
P_00026172:
    .byte 0x67
    .org 0x26173-ORIGIN
P_00026173:
    .byte 0x70
    .org 0x26174-ORIGIN
P_00026174:
    .byte 0x00
    .org 0x26175-ORIGIN
P_00026175:
    .byte 0x02
    .org 0x26176-ORIGIN
P_00026176:
    .byte 0x69
    .org 0x26177-ORIGIN
P_00026177:
    .byte 0x44
    .org 0x26370-ORIGIN
L_00026370:
    mov.w P_00026382,r0
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
    mov.l P_00026384,r6
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
P_00026382:
    .byte 0x00
    .org 0x26383-ORIGIN
P_00026383:
    .byte 0xe0
    .org 0x26384-ORIGIN
P_00026384:
    .byte 0x00
    .org 0x26385-ORIGIN
P_00026385:
    .byte 0x02
    .org 0x26386-ORIGIN
P_00026386:
    .byte 0x6a
    .org 0x26387-ORIGIN
P_00026387:
    .byte 0x80
    .org 0x26474-ORIGIN
L_00026474:
    sts.l pr,@-r15
    .org 0x26476-ORIGIN
L_00026476:
    mov.l r4,@-r15
    .org 0x26478-ORIGIN
L_00026478:
    mov r5,r0
    .org 0x2647a-ORIGIN
L_0002647a:
    extu.b r6,r5
    .org 0x2647c-ORIGIN
L_0002647c:
    mov.l P_0002649c,r7
    .org 0x2647e-ORIGIN
L_0002647e:
    jsr @r7
    .org 0x26480-ORIGIN
L_00026480:
    mov #0x7,r4
    .org 0x26482-ORIGIN
L_00026482:
    mov.l @r15+,r6
    .org 0x26484-ORIGIN
L_00026484:
    add r4,r6
    .org 0x26486-ORIGIN
L_00026486:
    mov.b @(0x1,r6),r0
    .org 0x26488-ORIGIN
L_00026488:
    extu.b r0,r2
    .org 0x2648a-ORIGIN
L_0002648a:
    mov r5,r3
    .org 0x2648c-ORIGIN
L_0002648c:
    mov.b @r6,r1
    .org 0x2648e-ORIGIN
L_0002648e:
    lds.l @r15+,pr
    .org 0x26490-ORIGIN
L_00026490:
    mov.l P_00026498,r6
    .org 0x26492-ORIGIN
L_00026492:
    jmp @r6
    .org 0x26494-ORIGIN
L_00026494:
    extu.b r1,r0
    .org 0x26498-ORIGIN
P_00026498:
    .byte 0x00
    .org 0x26499-ORIGIN
P_00026499:
    .byte 0x02
    .org 0x2649a-ORIGIN
P_0002649a:
    .byte 0x67
    .org 0x2649b-ORIGIN
P_0002649b:
    .byte 0x40
    .org 0x2649c-ORIGIN
P_0002649c:
    .byte 0x00
    .org 0x2649d-ORIGIN
P_0002649d:
    .byte 0x02
    .org 0x2649e-ORIGIN
P_0002649e:
    .byte 0x69
    .org 0x2649f-ORIGIN
P_0002649f:
    .byte 0x44
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
    .org 0x26770-ORIGIN
L_00026770:
    mov.l r8,@-r15
    .org 0x26772-ORIGIN
L_00026772:
    sts.l pr,@-r15
    .org 0x26774-ORIGIN
L_00026774:
    sts macl,r7
    .org 0x26776-ORIGIN
L_00026776:
    mulu.w r5,r0
    .org 0x26778-ORIGIN
L_00026778:
    add r2,r4
    .org 0x2677a-ORIGIN
L_0002677a:
    sts macl,r0
    .org 0x2677c-ORIGIN
L_0002677c:
    lds r7,macl
    .org 0x2677e-ORIGIN
L_0002677e:
    add r0,r4
    .org 0x26780-ORIGIN
L_00026780:
    add r4,r5
    .org 0x26782-ORIGIN
L_00026782:
    mov r1,r8
    .org 0x26784-ORIGIN
L_00026784:
    mov.l P_000267c8,r7
    .org 0x26786-ORIGIN
L_00026786:
    tst r3,r3
    .org 0x26788-ORIGIN
L_00026788:
    bt L_000267b0
    .org 0x2678a-ORIGIN
L_0002678a:
    mov.b @r4,r1
    .org 0x2678c-ORIGIN
L_0002678c:
    mov.b @(0x1,r4),r0
    .org 0x2678e-ORIGIN
L_0002678e:
    extu.b r0,r2
    .org 0x26790-ORIGIN
L_00026790:
    jsr @r7
    .org 0x26792-ORIGIN
L_00026792:
    extu.b r1,r0
    .org 0x26794-ORIGIN
L_00026794:
    tst r8,r8
    .org 0x26796-ORIGIN
L_00026796:
    bt L_000267c0
    .org 0x26798-ORIGIN
L_00026798:
    mov.l r0,@-r15
    .org 0x2679a-ORIGIN
L_0002679a:
    mov.b @r5,r1
    .org 0x2679c-ORIGIN
L_0002679c:
    mov.b @(0x1,r5),r0
    .org 0x2679e-ORIGIN
L_0002679e:
    extu.b r0,r2
    .org 0x267a0-ORIGIN
L_000267a0:
    jsr @r7
    .org 0x267a2-ORIGIN
L_000267a2:
    extu.b r1,r0
    .org 0x267a4-ORIGIN
L_000267a4:
    mov r0,r2
    .org 0x267a6-ORIGIN
L_000267a6:
    mov.l @r15+,r0
    .org 0x267a8-ORIGIN
L_000267a8:
    jsr @r7
    .org 0x267aa-ORIGIN
L_000267aa:
    mov r8,r3
    .org 0x267ac-ORIGIN
L_000267ac:
    bra L_000267c0
    .org 0x267ae-ORIGIN
L_000267ae:
    nop
    .org 0x267b0-ORIGIN
L_000267b0:
    tst r8,r8
    .org 0x267b2-ORIGIN
L_000267b2:
    bt/s L_000267c0
    .org 0x267b4-ORIGIN
L_000267b4:
    mov.b @r4,r0
    .org 0x267b6-ORIGIN
L_000267b6:
    mov.b @r5,r2
    .org 0x267b8-ORIGIN
L_000267b8:
    extu.b r0,r0
    .org 0x267ba-ORIGIN
L_000267ba:
    extu.b r2,r2
    .org 0x267bc-ORIGIN
L_000267bc:
    jsr @r7
    .org 0x267be-ORIGIN
L_000267be:
    mov r8,r3
    .org 0x267c0-ORIGIN
L_000267c0:
    lds.l @r15+,pr
    .org 0x267c2-ORIGIN
L_000267c2:
    rts
    .org 0x267c4-ORIGIN
L_000267c4:
    mov.l @r15+,r8
    .org 0x267c8-ORIGIN
P_000267c8:
    .byte 0x00
    .org 0x267c9-ORIGIN
P_000267c9:
    .byte 0x02
    .org 0x267ca-ORIGIN
P_000267ca:
    .byte 0x67
    .org 0x267cb-ORIGIN
P_000267cb:
    .byte 0x40
    .org 0x26944-ORIGIN
L_00026944:
    mov r4,r3
    .org 0x26946-ORIGIN
L_00026946:
    mov.b @(r0,r4),r1
    .org 0x26948-ORIGIN
L_00026948:
    extu.b r1,r1
    .org 0x2694a-ORIGIN
L_0002694a:
    cmp/eq r1,r5
    .org 0x2694c-ORIGIN
L_0002694c:
    bt L_0002697c
    .org 0x2694e-ORIGIN
L_0002694e:
    cmp/hi r1,r5
    .org 0x26950-ORIGIN
L_00026950:
    bf L_00026974
    .org 0x26952-ORIGIN
L_00026952:
    cmp/eq r4,r3
    .org 0x26954-ORIGIN
L_00026954:
    bt L_0002697c
    .org 0x26956-ORIGIN
L_00026956:
    sub r1,r5
    .org 0x26958-ORIGIN
L_00026958:
    shll16 r5
    .org 0x2695a-ORIGIN
L_0002695a:
    add r4,r0
    .org 0x2695c-ORIGIN
L_0002695c:
    mov.b @r0,r1
    .org 0x2695e-ORIGIN
L_0002695e:
    mov.b @(0x1,r0),r0
    .org 0x26960-ORIGIN
L_00026960:
    extu.b r1,r1
    .org 0x26962-ORIGIN
L_00026962:
    extu.b r0,r0
    .org 0x26964-ORIGIN
L_00026964:
    sts.l pr,@-r15
    .org 0x26966-ORIGIN
L_00026966:
    mov.l P_00026980,r2
    .org 0x26968-ORIGIN
L_00026968:
    sub r1,r0
    .org 0x2696a-ORIGIN
L_0002696a:
    jsr @r2
    .org 0x2696c-ORIGIN
L_0002696c:
    mov r5,r1
    .org 0x2696e-ORIGIN
L_0002696e:
    lds.l @r15+,pr
    .org 0x26970-ORIGIN
L_00026970:
    rts
    .org 0x26972-ORIGIN
L_00026972:
    mov r0,r5
    .org 0x26974-ORIGIN
L_00026974:
    add #-0x1,r4
    .org 0x26976-ORIGIN
L_00026976:
    cmp/pz r4
    .org 0x26978-ORIGIN
L_00026978:
    bt L_00026946
    .org 0x2697a-ORIGIN
L_0002697a:
    mov #0x0,r4
    .org 0x2697c-ORIGIN
L_0002697c:
    rts
    .org 0x2697e-ORIGIN
L_0002697e:
    mov #0x0,r5
    .org 0x26980-ORIGIN
P_00026980:
    .byte 0x00
    .org 0x26981-ORIGIN
P_00026981:
    .byte 0x02
    .org 0x26982-ORIGIN
P_00026982:
    .byte 0x6c
    .org 0x26983-ORIGIN
P_00026983:
    .byte 0x78
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
    .org 0x4afdc-ORIGIN
L_0004afdc:
    mov.l r9,@-r15
    .org 0x4afde-ORIGIN
L_0004afde:
    mov.l r10,@-r15
    .org 0x4afe0-ORIGIN
L_0004afe0:
    mov.l r11,@-r15
    .org 0x4afe2-ORIGIN
L_0004afe2:
    mov.l r12,@-r15
    .org 0x4afe4-ORIGIN
L_0004afe4:
    mov.l r13,@-r15
    .org 0x4afe6-ORIGIN
L_0004afe6:
    mov.l r14,@-r15
    .org 0x4afe8-ORIGIN
L_0004afe8:
    sts.l pr,@-r15
    .org 0x4afea-ORIGIN
L_0004afea:
    sts.l macl,@-r15
    .org 0x4afec-ORIGIN
L_0004afec:
    stc.l gbr,@-r15
    .org 0x4afee-ORIGIN
L_0004afee:
    mov.l P_0004b1f8,r0
    .org 0x4aff0-ORIGIN
L_0004aff0:
    ldc r0,gbr
    .org 0x4aff2-ORIGIN
L_0004aff2:
    add #-0x8,r15
    .org 0x4aff4-ORIGIN
L_0004aff4:
    mov.l P_0004b1fc,r9
    .org 0x4aff6-ORIGIN
L_0004aff6:
    mov.l P_0004b200,r13
    .org 0x4aff8-ORIGIN
L_0004aff8:
    mov.b @(0x9,r9),r0
    .org 0x4affa-ORIGIN
L_0004affa:
    extu.b r0,r6
    .org 0x4affc-ORIGIN
L_0004affc:
    mov #0x35,r0
    .org 0x4affe-ORIGIN
L_0004affe:
    mov.b @(r0,r13),r5
    .org 0x4b000-ORIGIN
L_0004b000:
    mov r5,r0
    .org 0x4b002-ORIGIN
L_0004b002:
    tst #0x20,r0
    .org 0x4b004-ORIGIN
L_0004b004:
    bt L_0004b008
    .org 0x4b006-ORIGIN
L_0004b006:
    add #0x4,r6
    .org 0x4b008-ORIGIN
L_0004b008:
    mov.l P_0004b204,r4
    .org 0x4b00a-ORIGIN
L_0004b00a:
    mov r5,r0
    .org 0x4b00c-ORIGIN
L_0004b00c:
    mov.b @r4,r2
    .org 0x4b00e-ORIGIN
L_0004b00e:
    extu.b r2,r2
    .org 0x4b010-ORIGIN
L_0004b010:
    cmp/hs r2,r6
    .org 0x4b012-ORIGIN
L_0004b012:
    bt/s L_0004b018
    .org 0x4b014-ORIGIN
L_0004b014:
    or #0x20,r0
    .org 0x4b016-ORIGIN
L_0004b016:
    and #0xdf,r0
    .org 0x4b018-ORIGIN
L_0004b018:
    mov.l P_0004b208,r6
    .org 0x4b01a-ORIGIN
L_0004b01a:
    mov r0,r2
    .org 0x4b01c-ORIGIN
L_0004b01c:
    mov #0x35,r0
    .org 0x4b01e-ORIGIN
L_0004b01e:
    mov.b r2,@(r0,r13)
    .org 0x4b020-ORIGIN
L_0004b020:
    mov.b @(0xc,r6),r0
    .org 0x4b022-ORIGIN
L_0004b022:
    mov r0,r4
    .org 0x4b024-ORIGIN
L_0004b024:
    and #0x20,r0
    .org 0x4b026-ORIGIN
L_0004b026:
    tst r0,r0
    .org 0x4b028-ORIGIN
L_0004b028:
    bf/s L_0004b036
    .org 0x4b02a-ORIGIN
L_0004b02a:
    mov r0,r2
    .org 0x4b02c-ORIGIN
L_0004b02c:
    mov.l P_0004b20c,r5
    .org 0x4b02e-ORIGIN
L_0004b02e:
    mov #0x26,r0
    .org 0x4b030-ORIGIN
L_0004b030:
    mov.l P_0004b210,r7
    .org 0x4b032-ORIGIN
L_0004b032:
    mov.b @r5,r6
    .org 0x4b034-ORIGIN
L_0004b034:
    mov.b r6,@(r0,r7)
    .org 0x4b036-ORIGIN
L_0004b036:
    mov.l P_0004b214,r5
    .org 0x4b038-ORIGIN
L_0004b038:
    mov.b @r5,r0
    .org 0x4b03a-ORIGIN
L_0004b03a:
    tst #0x1,r0
    .org 0x4b03c-ORIGIN
L_0004b03c:
    bt L_0004b062
    .org 0x4b03e-ORIGIN
L_0004b03e:
    mov.l P_0004b218,r7
    .org 0x4b040-ORIGIN
L_0004b040:
    mov #0x3c,r0
    .org 0x4b042-ORIGIN
L_0004b042:
    mov #0x40,r5
    .org 0x4b044-ORIGIN
L_0004b044:
    mov.w @(r0,r7),r6
    .org 0x4b046-ORIGIN
L_0004b046:
    shll8 r5
    .org 0x4b048-ORIGIN
L_0004b048:
    extu.w r6,r6
    .org 0x4b04a-ORIGIN
L_0004b04a:
    cmp/ge r5,r6
    .org 0x4b04c-ORIGIN
L_0004b04c:
    bt L_0004b062
    .org 0x4b04e-ORIGIN
L_0004b04e:
    mov.l P_0004b21c,r12
    .org 0x4b050-ORIGIN
L_0004b050:
    mov #0x16,r0
    .org 0x4b052-ORIGIN
L_0004b052:
    mov.l P_0004b220,r4
    .org 0x4b054-ORIGIN
L_0004b054:
    mov.b @(r0,r12),r2
    .org 0x4b056-ORIGIN
L_0004b056:
    mov.l P_0004b224,r14
    .org 0x4b058-ORIGIN
L_0004b058:
    jsr @r14
    .org 0x4b05a-ORIGIN
L_0004b05a:
    extu.b r2,r5
    .org 0x4b05c-ORIGIN
L_0004b05c:
    mov.l P_0004b208,r5
    .org 0x4b05e-ORIGIN
L_0004b05e:
    bra L_0004b0c0
    .org 0x4b060-ORIGIN
L_0004b060:
    extu.b r0,r6
    .org 0x4b062-ORIGIN
L_0004b062:
    mov.l P_0004b208,r5
    .org 0x4b064-ORIGIN
L_0004b064:
    mov.b @(0x3,r5),r0
    .org 0x4b066-ORIGIN
L_0004b066:
    and #0x4,r0
    .org 0x4b068-ORIGIN
L_0004b068:
    tst r0,r0
    .org 0x4b06a-ORIGIN
L_0004b06a:
    bf/s L_0004b098
    .org 0x4b06c-ORIGIN
L_0004b06c:
    mov r0,r5
    .org 0x4b06e-ORIGIN
L_0004b06e:
    mov #0x35,r0
    .org 0x4b070-ORIGIN
L_0004b070:
    mov.b @(r0,r13),r0
    .org 0x4b072-ORIGIN
L_0004b072:
    tst #0x20,r0
    .org 0x4b074-ORIGIN
L_0004b074:
    bt L_0004b098
    .org 0x4b076-ORIGIN
L_0004b076:
    tst r2,r2
    .org 0x4b078-ORIGIN
L_0004b078:
    bt L_0004b098
    .org 0x4b07a-ORIGIN
L_0004b07a:
    mov.l P_0004b210,r7
    .org 0x4b07c-ORIGIN
L_0004b07c:
    mov #0x26,r0
    .org 0x4b07e-ORIGIN
L_0004b07e:
    mov.b @(r0,r7),r2
    .org 0x4b080-ORIGIN
L_0004b080:
    tst r2,r2
    .org 0x4b082-ORIGIN
L_0004b082:
    bt L_0004b098
    .org 0x4b084-ORIGIN
L_0004b084:
    mov.l P_0004b21c,r12
    .org 0x4b086-ORIGIN
L_0004b086:
    mov #0x16,r0
    .org 0x4b088-ORIGIN
L_0004b088:
    mov.l P_0004b228,r4
    .org 0x4b08a-ORIGIN
L_0004b08a:
    mov.b @(r0,r12),r2
    .org 0x4b08c-ORIGIN
L_0004b08c:
    mov.l P_0004b224,r14
    .org 0x4b08e-ORIGIN
L_0004b08e:
    jsr @r14
    .org 0x4b090-ORIGIN
L_0004b090:
    extu.b r2,r5
    .org 0x4b092-ORIGIN
L_0004b092:
    mov.l P_0004b208,r5
    .org 0x4b094-ORIGIN
L_0004b094:
    bra L_0004b0c0
    .org 0x4b096-ORIGIN
L_0004b096:
    extu.b r0,r6
    .org 0x4b098-ORIGIN
L_0004b098:
    mov.l P_0004b22c,r6
    .org 0x4b09a-ORIGIN
L_0004b09a:
    mov.b @(0x7,r6),r0
    .org 0x4b09c-ORIGIN
L_0004b09c:
    cmp/eq #0x3,r0
    .org 0x4b09e-ORIGIN
L_0004b09e:
    bf L_0004b0ae
    .org 0x4b0a0-ORIGIN
L_0004b0a0:
    mov r4,r0
    .org 0x4b0a2-ORIGIN
L_0004b0a2:
    tst #0x80,r0
    .org 0x4b0a4-ORIGIN
L_0004b0a4:
    bt L_0004b0ae
    .org 0x4b0a6-ORIGIN
L_0004b0a6:
    mov.l P_0004b230,r6
    .org 0x4b0a8-ORIGIN
L_0004b0a8:
    mov.l P_0004b224,r14
    .org 0x4b0aa-ORIGIN
L_0004b0aa:
    bra L_0004b0c6
    .org 0x4b0ac-ORIGIN
L_0004b0ac:
    mov.b @r6,r6
    .org 0x4b0ae-ORIGIN
L_0004b0ae:
    mov.l P_0004b21c,r12
    .org 0x4b0b0-ORIGIN
L_0004b0b0:
    mov #0x16,r0
    .org 0x4b0b2-ORIGIN
L_0004b0b2:
    mov.l P_0004b234,r4
    .org 0x4b0b4-ORIGIN
L_0004b0b4:
    mov.b @(r0,r12),r2
    .org 0x4b0b6-ORIGIN
L_0004b0b6:
    mov.l P_0004b224,r14
    .org 0x4b0b8-ORIGIN
L_0004b0b8:
    jsr @r14
    .org 0x4b0ba-ORIGIN
L_0004b0ba:
    extu.b r2,r5
    .org 0x4b0bc-ORIGIN
L_0004b0bc:
    mov.l P_0004b208,r5
    .org 0x4b0be-ORIGIN
L_0004b0be:
    extu.b r0,r6
    .org 0x4b0c0-ORIGIN
L_0004b0c0:
    mov.b @(0x3,r5),r0
    .org 0x4b0c2-ORIGIN
L_0004b0c2:
    and #0x4,r0
    .org 0x4b0c4-ORIGIN
L_0004b0c4:
    mov r0,r5
    .org 0x4b0c6-ORIGIN
L_0004b0c6:
    exts.b r6,r2
    .org 0x4b0c8-ORIGIN
L_0004b0c8:
    mov.l P_0004b1f8,r10
    .org 0x4b0ca-ORIGIN
L_0004b0ca:
    mov.w P_0004b0e4,r0
    .org 0x4b0cc-ORIGIN
L_0004b0cc:
    add #-0x80,r2
    .org 0x4b0ce-ORIGIN
L_0004b0ce:
    mov.l P_0004b238,r12
    .org 0x4b0d0-ORIGIN
L_0004b0d0:
    mov.b r2,@(r0,r10)
    .org 0x4b0d2-ORIGIN
L_0004b0d2:
    mov.b @r12,r0
    .org 0x4b0d4-ORIGIN
L_0004b0d4:
    tst #0x40,r0
    .org 0x4b0d6-ORIGIN
L_0004b0d6:
    bt L_0004b0e6
    .org 0x4b0d8-ORIGIN
L_0004b0d8:
    mov.l P_0004b23c,r6
    .org 0x4b0da-ORIGIN
L_0004b0da:
    mov #0x64,r0
    .org 0x4b0dc-ORIGIN
L_0004b0dc:
    mov.l P_0004b240,r4
    .org 0x4b0de-ORIGIN
L_0004b0de:
    mov.b @r6,r2
    .org 0x4b0e0-ORIGIN
L_0004b0e0:
    bra L_0004b0fe
    .org 0x4b0e2-ORIGIN
L_0004b0e2:
    mov.b r2,@(r0,r4)
    .org 0x4b0e4-ORIGIN
P_0004b0e4:
    .byte 0x02
    .org 0x4b0e5-ORIGIN
P_0004b0e5:
    .byte 0x85
    .org 0x4b0e6-ORIGIN
L_0004b0e6:
    mov.l P_0004b218,r7
    .org 0x4b0e8-ORIGIN
L_0004b0e8:
    mov.b @(0x5,r7),r0
    .org 0x4b0ea-ORIGIN
L_0004b0ea:
    tst #0x1,r0
    .org 0x4b0ec-ORIGIN
L_0004b0ec:
    bt/s L_0004b0fe
    .org 0x4b0ee-ORIGIN
L_0004b0ee:
    mov r0,r6
    .org 0x4b0f0-ORIGIN
L_0004b0f0:
    mov r6,r0
    .org 0x4b0f2-ORIGIN
L_0004b0f2:
    tst #0x2,r0
    .org 0x4b0f4-ORIGIN
L_0004b0f4:
    bt L_0004b0fe
    .org 0x4b0f6-ORIGIN
L_0004b0f6:
    mov.l P_0004b244,r6
    .org 0x4b0f8-ORIGIN
L_0004b0f8:
    mov.b @(0x5,r6),r0
    .org 0x4b0fa-ORIGIN
L_0004b0fa:
    or #0x4,r0
    .org 0x4b0fc-ORIGIN
L_0004b0fc:
    mov.b r0,@(0x5,r6)
    .org 0x4b0fe-ORIGIN
L_0004b0fe:
    extu.b r5,r5
    .org 0x4b100-ORIGIN
L_0004b100:
    mov.b @(0x6,r9),r0
    .org 0x4b102-ORIGIN
L_0004b102:
    tst r5,r5
    .org 0x4b104-ORIGIN
L_0004b104:
    mov.l P_0004b248,r5
    .org 0x4b106-ORIGIN
L_0004b106:
    extu.b r0,r6
    .org 0x4b108-ORIGIN
L_0004b108:
    mov.b @r5,r2
    .org 0x4b10a-ORIGIN
L_0004b10a:
    bf/s L_0004b112
    .org 0x4b10c-ORIGIN
L_0004b10c:
    extu.b r2,r2
    .org 0x4b10e-ORIGIN
L_0004b10e:
    bra L_0004b264
    .org 0x4b110-ORIGIN
L_0004b110:
    nop
    .org 0x4b112-ORIGIN
L_0004b112:
    cmp/ge r2,r6
    .org 0x4b114-ORIGIN
L_0004b114:
    bf L_0004b152
    .org 0x4b116-ORIGIN
L_0004b116:
    mov.l P_0004b24c,r2
    .org 0x4b118-ORIGIN
L_0004b118:
    mov.w @(0x6,r2),r0
    .org 0x4b11a-ORIGIN
L_0004b11a:
    extu.w r0,r5
    .org 0x4b11c-ORIGIN
L_0004b11c:
    mov.w @(0x4,r2),r0
    .org 0x4b11e-ORIGIN
L_0004b11e:
    extu.w r0,r7
    .org 0x4b120-ORIGIN
L_0004b120:
    cmp/gt r7,r5
    .org 0x4b122-ORIGIN
L_0004b122:
    bf L_0004b152
    .org 0x4b124-ORIGIN
L_0004b124:
    mov.l @(0x36c,gbr),r0
    .org 0x4b126-ORIGIN
L_0004b126:
    cmp/gt r7,r0
    .org 0x4b128-ORIGIN
L_0004b128:
    bf/s L_0004b152
    .org 0x4b12a-ORIGIN
L_0004b12a:
    mov r0,r6
    .org 0x4b12c-ORIGIN
L_0004b12c:
    cmp/ge r5,r6
    .org 0x4b12e-ORIGIN
L_0004b12e:
    bf L_0004b136
    .org 0x4b130-ORIGIN
L_0004b130:
    mov.l P_0004b250,r6
    .org 0x4b132-ORIGIN
L_0004b132:
    bra L_0004b154
    .org 0x4b134-ORIGIN
L_0004b134:
    mov.b @r6,r2
    .org 0x4b136-ORIGIN
L_0004b136:
    mov.l P_0004b250,r3
    .org 0x4b138-ORIGIN
L_0004b138:
    sub r7,r6
    .org 0x4b13a-ORIGIN
L_0004b13a:
    sub r7,r5
    .org 0x4b13c-ORIGIN
L_0004b13c:
    mov.b @r3,r4
    .org 0x4b13e-ORIGIN
L_0004b13e:
    mov r5,r0
    .org 0x4b140-ORIGIN
L_0004b140:
    extu.b r4,r1
    .org 0x4b142-ORIGIN
L_0004b142:
    mul.l r6,r1
    .org 0x4b144-ORIGIN
L_0004b144:
    mov.l P_0004b254,r6
    .org 0x4b146-ORIGIN
L_0004b146:
    jsr @r6
    .org 0x4b148-ORIGIN
L_0004b148:
    sts macl,r1
    .org 0x4b14a-ORIGIN
L_0004b14a:
    mov r0,r6
    .org 0x4b14c-ORIGIN
L_0004b14c:
    mov.w P_0004b1f6,r0
    .org 0x4b14e-ORIGIN
L_0004b14e:
    bra L_0004b158
    .org 0x4b150-ORIGIN
L_0004b150:
    mov.b r6,@(r0,r10)
    .org 0x4b152-ORIGIN
L_0004b152:
    mov #0x0,r2
    .org 0x4b154-ORIGIN
L_0004b154:
    mov.w P_0004b1f6,r0
    .org 0x4b156-ORIGIN
L_0004b156:
    mov.b r2,@(r0,r10)
    .org 0x4b158-ORIGIN
L_0004b158:
    mov.b @(0x7,r9),r0
    .org 0x4b15a-ORIGIN
L_0004b15a:
    mov.l P_0004b258,r4
    .org 0x4b15c-ORIGIN
L_0004b15c:
    jsr @r14
    .org 0x4b15e-ORIGIN
L_0004b15e:
    extu.b r0,r5
    .org 0x4b160-ORIGIN
L_0004b160:
    mov.l P_0004b218,r7
    .org 0x4b162-ORIGIN
L_0004b162:
    mov r0,r6
    .org 0x4b164-ORIGIN
L_0004b164:
    mov.b r0,@(0x4,r15)
    .org 0x4b166-ORIGIN
L_0004b166:
    mov.b @(0x5,r7),r0
    .org 0x4b168-ORIGIN
L_0004b168:
    tst #0x1,r0
    .org 0x4b16a-ORIGIN
L_0004b16a:
    bt/s L_0004b1a0
    .org 0x4b16c-ORIGIN
L_0004b16c:
    mov r0,r5
    .org 0x4b16e-ORIGIN
L_0004b16e:
    mov r5,r0
    .org 0x4b170-ORIGIN
L_0004b170:
    tst #0x2,r0
    .org 0x4b172-ORIGIN
L_0004b172:
    bt L_0004b1a0
    .org 0x4b174-ORIGIN
L_0004b174:
    mov.b @(0x7,r9),r0
    .org 0x4b176-ORIGIN
L_0004b176:
    mov.l P_0004b25c,r4
    .org 0x4b178-ORIGIN
L_0004b178:
    jsr @r14
    .org 0x4b17a-ORIGIN
L_0004b17a:
    extu.b r0,r5
    .org 0x4b17c-ORIGIN
L_0004b17c:
    mov r0,r2
    .org 0x4b17e-ORIGIN
L_0004b17e:
    mov.b @(0x4,r15),r0
    .org 0x4b180-ORIGIN
L_0004b180:
    extu.b r2,r2
    .org 0x4b182-ORIGIN
L_0004b182:
    extu.b r0,r6
    .org 0x4b184-ORIGIN
L_0004b184:
    mov.w P_0004b1f6,r0
    .org 0x4b186-ORIGIN
L_0004b186:
    sub r2,r6
    .org 0x4b188-ORIGIN
L_0004b188:
    mov.b @(r0,r10),r5
    .org 0x4b18a-ORIGIN
L_0004b18a:
    extu.b r5,r4
    .org 0x4b18c-ORIGIN
L_0004b18c:
    sub r4,r6
    .org 0x4b18e-ORIGIN
L_0004b18e:
    mov r6,r2
    .org 0x4b190-ORIGIN
L_0004b190:
    exts.w r6,r6
    .org 0x4b192-ORIGIN
L_0004b192:
    cmp/pz r6
    .org 0x4b194-ORIGIN
L_0004b194:
    bt L_0004b19a
    .org 0x4b196-ORIGIN
L_0004b196:
    bra L_0004b19c
    .org 0x4b198-ORIGIN
L_0004b198:
    mov #0x0,r5
    .org 0x4b19a-ORIGIN
L_0004b19a:
    exts.w r2,r5
    .org 0x4b19c-ORIGIN
L_0004b19c:
    bra L_0004b2d2
    .org 0x4b19e-ORIGIN
L_0004b19e:
    mov r5,r0
    .org 0x4b1a0-ORIGIN
L_0004b1a0:
    mov.l P_0004b244,r5
    .org 0x4b1a2-ORIGIN
L_0004b1a2:
    mov.b @(0x5,r5),r0
    .org 0x4b1a4-ORIGIN
L_0004b1a4:
    tst #0x4,r0
    .org 0x4b1a6-ORIGIN
L_0004b1a6:
    bf L_0004b1dc
    .org 0x4b1a8-ORIGIN
L_0004b1a8:
    mov.l P_0004b240,r4
    .org 0x4b1aa-ORIGIN
L_0004b1aa:
    mov #0x64,r0
    .org 0x4b1ac-ORIGIN
L_0004b1ac:
    mov.b @(r0,r4),r2
    .org 0x4b1ae-ORIGIN
L_0004b1ae:
    tst r2,r2
    .org 0x4b1b0-ORIGIN
L_0004b1b0:
    bt L_0004b1dc
    .org 0x4b1b2-ORIGIN
L_0004b1b2:
    mov.b @r12,r0
    .org 0x4b1b4-ORIGIN
L_0004b1b4:
    tst #0x40,r0
    .org 0x4b1b6-ORIGIN
L_0004b1b6:
    bf L_0004b1dc
    .org 0x4b1b8-ORIGIN
L_0004b1b8:
    mov.b @(0x7,r9),r0
    .org 0x4b1ba-ORIGIN
L_0004b1ba:
    mov.l P_0004b260,r4
    .org 0x4b1bc-ORIGIN
L_0004b1bc:
    jsr @r14
    .org 0x4b1be-ORIGIN
L_0004b1be:
    extu.b r0,r5
    .org 0x4b1c0-ORIGIN
L_0004b1c0:
    mov r0,r2
    .org 0x4b1c2-ORIGIN
L_0004b1c2:
    mov.b @(0x4,r15),r0
    .org 0x4b1c4-ORIGIN
L_0004b1c4:
    extu.b r2,r2
    .org 0x4b1c6-ORIGIN
L_0004b1c6:
    extu.b r0,r6
    .org 0x4b1c8-ORIGIN
L_0004b1c8:
    add r2,r6
    .org 0x4b1ca-ORIGIN
L_0004b1ca:
    mov #-0x1,r4
    .org 0x4b1cc-ORIGIN
L_0004b1cc:
    extu.w r6,r5
    .org 0x4b1ce-ORIGIN
L_0004b1ce:
    extu.b r4,r4
    .org 0x4b1d0-ORIGIN
L_0004b1d0:
    cmp/gt r4,r5
    .org 0x4b1d2-ORIGIN
L_0004b1d2:
    bt L_0004b1d6
    .org 0x4b1d4-ORIGIN
L_0004b1d4:
    mov r5,r4
    .org 0x4b1d6-ORIGIN
L_0004b1d6:
    mov r4,r5
    .org 0x4b1d8-ORIGIN
L_0004b1d8:
    bra L_0004b2d2
    .org 0x4b1da-ORIGIN
L_0004b1da:
    mov r4,r0
    .org 0x4b1dc-ORIGIN
L_0004b1dc:
    mov.w P_0004b1f6,r0
    .org 0x4b1de-ORIGIN
L_0004b1de:
    extu.b r6,r6
    .org 0x4b1e0-ORIGIN
L_0004b1e0:
    mov.b @(r0,r10),r2
    .org 0x4b1e2-ORIGIN
L_0004b1e2:
    extu.b r2,r2
    .org 0x4b1e4-ORIGIN
L_0004b1e4:
    sub r2,r6
    .org 0x4b1e6-ORIGIN
L_0004b1e6:
    mov r6,r2
    .org 0x4b1e8-ORIGIN
L_0004b1e8:
    exts.w r6,r6
    .org 0x4b1ea-ORIGIN
L_0004b1ea:
    cmp/pz r6
    .org 0x4b1ec-ORIGIN
L_0004b1ec:
    bt L_0004b1f2
    .org 0x4b1ee-ORIGIN
L_0004b1ee:
    bra L_0004b2ce
    .org 0x4b1f0-ORIGIN
L_0004b1f0:
    mov #0x0,r2
    .org 0x4b1f2-ORIGIN
L_0004b1f2:
    bra L_0004b2ce
    .org 0x4b1f4-ORIGIN
L_0004b1f4:
    exts.w r2,r2
    .org 0x4b1f6-ORIGIN
P_0004b1f6:
    .byte 0x05
    .org 0x4b1f7-ORIGIN
P_0004b1f7:
    .byte 0xb6
    .org 0x4b1f8-ORIGIN
P_0004b1f8:
    .byte 0xff
    .org 0x4b1f9-ORIGIN
P_0004b1f9:
    .byte 0xff
    .org 0x4b1fa-ORIGIN
P_0004b1fa:
    .byte 0x12
    .org 0x4b1fb-ORIGIN
P_0004b1fb:
    .byte 0x8c
    .org 0x4b1fc-ORIGIN
P_0004b1fc:
    .byte 0xff
    .org 0x4b1fd-ORIGIN
P_0004b1fd:
    .byte 0xff
    .org 0x4b1fe-ORIGIN
P_0004b1fe:
    .byte 0x10
    .org 0x4b1ff-ORIGIN
P_0004b1ff:
    .byte 0x68
    .org 0x4b200-ORIGIN
P_0004b200:
    .byte 0xff
    .org 0x4b201-ORIGIN
P_0004b201:
    .byte 0xff
    .org 0x4b202-ORIGIN
P_0004b202:
    .byte 0x41
    .org 0x4b203-ORIGIN
P_0004b203:
    .byte 0xa9
    .org 0x4b204-ORIGIN
P_0004b204:
    .byte 0x00
    .org 0x4b205-ORIGIN
P_0004b205:
    .byte 0x00
    .org 0x4b206-ORIGIN
P_0004b206:
    .byte 0x86
    .org 0x4b207-ORIGIN
P_0004b207:
    .byte 0xa4
    .org 0x4b208-ORIGIN
P_0004b208:
    .byte 0xff
    .org 0x4b209-ORIGIN
P_0004b209:
    .byte 0xff
    .org 0x4b20a-ORIGIN
P_0004b20a:
    .byte 0x24
    .org 0x4b20b-ORIGIN
P_0004b20b:
    .byte 0x4c
    .org 0x4b20c-ORIGIN
P_0004b20c:
    .byte 0x00
    .org 0x4b20d-ORIGIN
P_0004b20d:
    .byte 0x00
    .org 0x4b20e-ORIGIN
P_0004b20e:
    .byte 0x86
    .org 0x4b20f-ORIGIN
P_0004b20f:
    .byte 0xa3
    .org 0x4b210-ORIGIN
P_0004b210:
    .byte 0xff
    .org 0x4b211-ORIGIN
P_0004b211:
    .byte 0xff
    .org 0x4b212-ORIGIN
P_0004b212:
    .byte 0x25
    .org 0x4b213-ORIGIN
P_0004b213:
    .byte 0x6a
    .org 0x4b214-ORIGIN
P_0004b214:
    .byte 0x00
    .org 0x4b215-ORIGIN
P_0004b215:
    .byte 0x00
    .org 0x4b216-ORIGIN
P_0004b216:
    .byte 0x87
    .org 0x4b217-ORIGIN
P_0004b217:
    .byte 0x0b
    .org 0x4b218-ORIGIN
P_0004b218:
    .byte 0xff
    .org 0x4b219-ORIGIN
P_0004b219:
    .byte 0xff
    .org 0x4b21a-ORIGIN
P_0004b21a:
    .byte 0x22
    .org 0x4b21b-ORIGIN
P_0004b21b:
    .byte 0xdc
    .org 0x4b21c-ORIGIN
P_0004b21c:
    .byte 0xff
    .org 0x4b21d-ORIGIN
P_0004b21d:
    .byte 0xff
    .org 0x4b21e-ORIGIN
P_0004b21e:
    .byte 0x11
    .org 0x4b21f-ORIGIN
P_0004b21f:
    .byte 0x9c
    .org 0x4b220-ORIGIN
P_0004b220:
    .byte 0x00
    .org 0x4b221-ORIGIN
P_0004b221:
    .byte 0x01
    .org 0x4b222-ORIGIN
P_0004b222:
    .byte 0x21
    .org 0x4b223-ORIGIN
P_0004b223:
    .byte 0xa6
    .org 0x4b224-ORIGIN
P_0004b224:
    .byte 0x00
    .org 0x4b225-ORIGIN
P_0004b225:
    .byte 0x02
    .org 0x4b226-ORIGIN
P_0004b226:
    .byte 0x63
    .org 0x4b227-ORIGIN
P_0004b227:
    .byte 0x70
    .org 0x4b228-ORIGIN
P_0004b228:
    .byte 0x00
    .org 0x4b229-ORIGIN
P_0004b229:
    .byte 0x01
    .org 0x4b22a-ORIGIN
P_0004b22a:
    .byte 0x21
    .org 0x4b22b-ORIGIN
P_0004b22b:
    .byte 0x9e
    .org 0x4b22c-ORIGIN
P_0004b22c:
    .byte 0xff
    .org 0x4b22d-ORIGIN
P_0004b22d:
    .byte 0xff
    .org 0x4b22e-ORIGIN
P_0004b22e:
    .byte 0x22
    .org 0x4b22f-ORIGIN
P_0004b22f:
    .byte 0xf8
    .org 0x4b230-ORIGIN
P_0004b230:
    .byte 0x00
    .org 0x4b231-ORIGIN
P_0004b231:
    .byte 0x00
    .org 0x4b232-ORIGIN
P_0004b232:
    .byte 0x86
    .org 0x4b233-ORIGIN
P_0004b233:
    .byte 0xa2
    .org 0x4b234-ORIGIN
P_0004b234:
    .byte 0x00
    .org 0x4b235-ORIGIN
P_0004b235:
    .byte 0x01
    .org 0x4b236-ORIGIN
P_0004b236:
    .byte 0x21
    .org 0x4b237-ORIGIN
P_0004b237:
    .byte 0x96
    .org 0x4b238-ORIGIN
P_0004b238:
    .byte 0xff
    .org 0x4b239-ORIGIN
P_0004b239:
    .byte 0xff
    .org 0x4b23a-ORIGIN
P_0004b23a:
    .byte 0x41
    .org 0x4b23b-ORIGIN
P_0004b23b:
    .byte 0x84
    .org 0x4b23c-ORIGIN
P_0004b23c:
    .byte 0x00
    .org 0x4b23d-ORIGIN
P_0004b23d:
    .byte 0x00
    .org 0x4b23e-ORIGIN
P_0004b23e:
    .byte 0x8c
    .org 0x4b23f-ORIGIN
P_0004b23f:
    .byte 0x3b
    .org 0x4b240-ORIGIN
P_0004b240:
    .byte 0xff
    .org 0x4b241-ORIGIN
P_0004b241:
    .byte 0xff
    .org 0x4b242-ORIGIN
P_0004b242:
    .byte 0x42
    .org 0x4b243-ORIGIN
P_0004b243:
    .byte 0x58
    .org 0x4b244-ORIGIN
P_0004b244:
    .byte 0xff
    .org 0x4b245-ORIGIN
P_0004b245:
    .byte 0xff
    .org 0x4b246-ORIGIN
P_0004b246:
    .byte 0x42
    .org 0x4b247-ORIGIN
P_0004b247:
    .byte 0x4c
    .org 0x4b248-ORIGIN
P_0004b248:
    .byte 0x00
    .org 0x4b249-ORIGIN
P_0004b249:
    .byte 0x00
    .org 0x4b24a-ORIGIN
P_0004b24a:
    .byte 0x8c
    .org 0x4b24b-ORIGIN
P_0004b24b:
    .byte 0xd1
    .org 0x4b24c-ORIGIN
P_0004b24c:
    .byte 0x00
    .org 0x4b24d-ORIGIN
P_0004b24d:
    .byte 0x00
    .org 0x4b24e-ORIGIN
P_0004b24e:
    .byte 0x92
    .org 0x4b24f-ORIGIN
P_0004b24f:
    .byte 0x76
    .org 0x4b250-ORIGIN
P_0004b250:
    .byte 0x00
    .org 0x4b251-ORIGIN
P_0004b251:
    .byte 0x00
    .org 0x4b252-ORIGIN
P_0004b252:
    .byte 0x87
    .org 0x4b253-ORIGIN
P_0004b253:
    .byte 0x8a
    .org 0x4b254-ORIGIN
P_0004b254:
    .byte 0x00
    .org 0x4b255-ORIGIN
P_0004b255:
    .byte 0x02
    .org 0x4b256-ORIGIN
P_0004b256:
    .byte 0x1b
    .org 0x4b257-ORIGIN
P_0004b257:
    .byte 0xbc
    .org 0x4b258-ORIGIN
P_0004b258:
    .byte 0x00
    .org 0x4b259-ORIGIN
P_0004b259:
    .byte 0x01
    .org 0x4b25a-ORIGIN
P_0004b25a:
    .byte 0x1f
    .org 0x4b25b-ORIGIN
P_0004b25b:
    .byte 0x12
    .org 0x4b25c-ORIGIN
P_0004b25c:
    .byte 0x00
    .org 0x4b25d-ORIGIN
P_0004b25d:
    .byte 0x01
    .org 0x4b25e-ORIGIN
P_0004b25e:
    .byte 0x1f
    .org 0x4b25f-ORIGIN
P_0004b25f:
    .byte 0x1a
    .org 0x4b260-ORIGIN
P_0004b260:
    .byte 0x00
    .org 0x4b261-ORIGIN
P_0004b261:
    .byte 0x01
    .org 0x4b262-ORIGIN
P_0004b262:
    .byte 0x1f
    .org 0x4b263-ORIGIN
P_0004b263:
    .byte 0x22
    .org 0x4b264-ORIGIN
L_0004b264:
    cmp/ge r2,r6
    .org 0x4b266-ORIGIN
L_0004b266:
    bf L_0004b2a8
    .org 0x4b268-ORIGIN
L_0004b268:
    mov.l P_0004b4e0,r2
    .org 0x4b26a-ORIGIN
L_0004b26a:
    mov.w @(0x2,r2),r0
    .org 0x4b26c-ORIGIN
L_0004b26c:
    mov.w @r2,r7
    .org 0x4b26e-ORIGIN
L_0004b26e:
    extu.w r0,r5
    .org 0x4b270-ORIGIN
L_0004b270:
    extu.w r7,r7
    .org 0x4b272-ORIGIN
L_0004b272:
    cmp/gt r7,r5
    .org 0x4b274-ORIGIN
L_0004b274:
    bf L_0004b2a8
    .org 0x4b276-ORIGIN
L_0004b276:
    mov.l @(0x36c,gbr),r0
    .org 0x4b278-ORIGIN
L_0004b278:
    cmp/gt r7,r0
    .org 0x4b27a-ORIGIN
L_0004b27a:
    bf L_0004b2a8
    .org 0x4b27c-ORIGIN
L_0004b27c:
    mov.l @(0x36c,gbr),r0
    .org 0x4b27e-ORIGIN
L_0004b27e:
    cmp/ge r5,r0
    .org 0x4b280-ORIGIN
L_0004b280:
    bf L_0004b288
    .org 0x4b282-ORIGIN
L_0004b282:
    mov.l P_0004b4e4,r6
    .org 0x4b284-ORIGIN
L_0004b284:
    bra L_0004b2aa
    .org 0x4b286-ORIGIN
L_0004b286:
    mov.b @r6,r2
    .org 0x4b288-ORIGIN
L_0004b288:
    mov.l P_0004b4e4,r3
    .org 0x4b28a-ORIGIN
L_0004b28a:
    sub r7,r5
    .org 0x4b28c-ORIGIN
L_0004b28c:
    mov.l @(0x36c,gbr),r0
    .org 0x4b28e-ORIGIN
L_0004b28e:
    mov.b @r3,r4
    .org 0x4b290-ORIGIN
L_0004b290:
    mov r0,r2
    .org 0x4b292-ORIGIN
L_0004b292:
    sub r7,r2
    .org 0x4b294-ORIGIN
L_0004b294:
    extu.b r4,r4
    .org 0x4b296-ORIGIN
L_0004b296:
    mov.l P_0004b4e8,r6
    .org 0x4b298-ORIGIN
L_0004b298:
    mul.l r2,r4
    .org 0x4b29a-ORIGIN
L_0004b29a:
    mov r5,r0
    .org 0x4b29c-ORIGIN
L_0004b29c:
    jsr @r6
    .org 0x4b29e-ORIGIN
L_0004b29e:
    sts macl,r1
    .org 0x4b2a0-ORIGIN
L_0004b2a0:
    mov r0,r6
    .org 0x4b2a2-ORIGIN
L_0004b2a2:
    mov.w P_0004b328,r0
    .org 0x4b2a4-ORIGIN
L_0004b2a4:
    bra L_0004b2ae
    .org 0x4b2a6-ORIGIN
L_0004b2a6:
    mov.b r6,@(r0,r10)
    .org 0x4b2a8-ORIGIN
L_0004b2a8:
    mov #0x0,r2
    .org 0x4b2aa-ORIGIN
L_0004b2aa:
    mov.w P_0004b328,r0
    .org 0x4b2ac-ORIGIN
L_0004b2ac:
    mov.b r2,@(r0,r10)
    .org 0x4b2ae-ORIGIN
L_0004b2ae:
    mov.b @(0x7,r9),r0
    .org 0x4b2b0-ORIGIN
L_0004b2b0:
    mov.l P_0004b4ec,r4
    .org 0x4b2b2-ORIGIN
L_0004b2b2:
    jsr @r14
    .org 0x4b2b4-ORIGIN
L_0004b2b4:
    extu.b r0,r5
    .org 0x4b2b6-ORIGIN
L_0004b2b6:
    extu.b r0,r6
    .org 0x4b2b8-ORIGIN
L_0004b2b8:
    mov.w P_0004b328,r0
    .org 0x4b2ba-ORIGIN
L_0004b2ba:
    mov.b @(r0,r10),r2
    .org 0x4b2bc-ORIGIN
L_0004b2bc:
    extu.b r2,r5
    .org 0x4b2be-ORIGIN
L_0004b2be:
    sub r5,r6
    .org 0x4b2c0-ORIGIN
L_0004b2c0:
    mov r6,r2
    .org 0x4b2c2-ORIGIN
L_0004b2c2:
    exts.w r6,r6
    .org 0x4b2c4-ORIGIN
L_0004b2c4:
    cmp/pz r6
    .org 0x4b2c6-ORIGIN
L_0004b2c6:
    bt L_0004b2cc
    .org 0x4b2c8-ORIGIN
L_0004b2c8:
    bra L_0004b2ce
    .org 0x4b2ca-ORIGIN
L_0004b2ca:
    mov #0x0,r2
    .org 0x4b2cc-ORIGIN
L_0004b2cc:
    exts.w r2,r2
    .org 0x4b2ce-ORIGIN
L_0004b2ce:
    mov r2,r5
    .org 0x4b2d0-ORIGIN
L_0004b2d0:
    mov r2,r0
    .org 0x4b2d2-ORIGIN
L_0004b2d2:
    mov.b r0,@(0x4f,gbr)
    .org 0x4b2d4-ORIGIN
L_0004b2d4:
    stc sr,r0
    .org 0x4b2d6-ORIGIN
L_0004b2d6:
    shlr2 r0
    .org 0x4b2d8-ORIGIN
L_0004b2d8:
    shlr2 r0
    .org 0x4b2da-ORIGIN
L_0004b2da:
    and #0xf,r0
    .org 0x4b2dc-ORIGIN
L_0004b2dc:
    mov r0,r2
    .org 0x4b2de-ORIGIN
L_0004b2de:
    stc sr,r0
    .org 0x4b2e0-ORIGIN
L_0004b2e0:
    mov.w P_0004b32a,r4
    .org 0x4b2e2-ORIGIN
L_0004b2e2:
    and r4,r0
    .org 0x4b2e4-ORIGIN
L_0004b2e4:
    or #0xf0,r0
    .org 0x4b2e6-ORIGIN
L_0004b2e6:
    ldc r0,sr
    .org 0x4b2e8-ORIGIN
L_0004b2e8:
    mov.l P_0004b4f0,r14
    .org 0x4b2ea-ORIGIN
L_0004b2ea:
    mov #0x1d,r0
    .org 0x4b2ec-ORIGIN
L_0004b2ec:
    mov.l P_0004b4f4,r7
    .org 0x4b2ee-ORIGIN
L_0004b2ee:
    mov.b @(r0,r14),r4
    .org 0x4b2f0-ORIGIN
L_0004b2f0:
    mov r4,r0
    .org 0x4b2f2-ORIGIN
L_0004b2f2:
    tst #0x10,r0
    .org 0x4b2f4-ORIGIN
L_0004b2f4:
    mov #0x2b,r0
    .org 0x4b2f6-ORIGIN
L_0004b2f6:
    bt/s L_0004b30a
    .org 0x4b2f8-ORIGIN
L_0004b2f8:
    mov.b @(r0,r7),r6
    .org 0x4b2fa-ORIGIN
L_0004b2fa:
    tst r6,r6
    .org 0x4b2fc-ORIGIN
L_0004b2fc:
    bf L_0004b322
    .org 0x4b2fe-ORIGIN
L_0004b2fe:
    mov r4,r0
    .org 0x4b300-ORIGIN
L_0004b300:
    and #0xef,r0
    .org 0x4b302-ORIGIN
L_0004b302:
    mov r0,r4
    .org 0x4b304-ORIGIN
L_0004b304:
    mov #0x1d,r0
    .org 0x4b306-ORIGIN
L_0004b306:
    bra L_0004b368
    .org 0x4b308-ORIGIN
L_0004b308:
    mov.b r4,@(r0,r14)
    .org 0x4b30a-ORIGIN
L_0004b30a:
    extu.b r6,r0
    .org 0x4b30c-ORIGIN
L_0004b30c:
    cmp/eq #0x1,r0
    .org 0x4b30e-ORIGIN
L_0004b30e:
    bf L_0004b32e
    .org 0x4b310-ORIGIN
L_0004b310:
    mov.l P_0004b4f8,r7
    .org 0x4b312-ORIGIN
L_0004b312:
    mov #0x2b,r0
    .org 0x4b314-ORIGIN
L_0004b314:
    mov.b @(r0,r7),r6
    .org 0x4b316-ORIGIN
L_0004b316:
    tst r6,r6
    .org 0x4b318-ORIGIN
L_0004b318:
    bf L_0004b32e
    .org 0x4b31a-ORIGIN
L_0004b31a:
    mov #0x10,r0
    .org 0x4b31c-ORIGIN
L_0004b31c:
    or r0,r4
    .org 0x4b31e-ORIGIN
L_0004b31e:
    mov #0x1d,r0
    .org 0x4b320-ORIGIN
L_0004b320:
    mov.b r4,@(r0,r14)
    .org 0x4b322-ORIGIN
L_0004b322:
    mov.w P_0004b32c,r0
    .org 0x4b324-ORIGIN
L_0004b324:
    bra L_0004b36a
    .org 0x4b326-ORIGIN
L_0004b326:
    mov.b @(r0,r10),r6
    .org 0x4b328-ORIGIN
P_0004b328:
    .byte 0x05
    .org 0x4b329-ORIGIN
P_0004b329:
    .byte 0xb5
    .org 0x4b32a-ORIGIN
P_0004b32a:
    .byte 0xff
    .org 0x4b32b-ORIGIN
P_0004b32b:
    .byte 0x0f
    .org 0x4b32c-ORIGIN
P_0004b32c:
    .byte 0x02
    .org 0x4b32d-ORIGIN
P_0004b32d:
    .byte 0x87
    .org 0x4b32e-ORIGIN
L_0004b32e:
    mov.l P_0004b4fc,r11
    .org 0x4b330-ORIGIN
L_0004b330:
    extu.b r5,r5
    .org 0x4b332-ORIGIN
L_0004b332:
    mov #0x7f,r6
    .org 0x4b334-ORIGIN
L_0004b334:
    mov.b @(0x9,r11),r0
    .org 0x4b336-ORIGIN
L_0004b336:
    extu.b r0,r4
    .org 0x4b338-ORIGIN
L_0004b338:
    mov.w P_0004b488,r0
    .org 0x4b33a-ORIGIN
L_0004b33a:
    mov.b @(r0,r10),r7
    .org 0x4b33c-ORIGIN
L_0004b33c:
    mov.w P_0004b48a,r0
    .org 0x4b33e-ORIGIN
L_0004b33e:
    extu.b r7,r7
    .org 0x4b340-ORIGIN
L_0004b340:
    mov.b @(r0,r10),r12
    .org 0x4b342-ORIGIN
L_0004b342:
    mov #0x48,r0
    .org 0x4b344-ORIGIN
L_0004b344:
    add r5,r12
    .org 0x4b346-ORIGIN
L_0004b346:
    sub r4,r12
    .org 0x4b348-ORIGIN
L_0004b348:
    mov.b @(r0,r11),r4
    .org 0x4b34a-ORIGIN
L_0004b34a:
    sub r12,r4
    .org 0x4b34c-ORIGIN
L_0004b34c:
    sub r7,r4
    .org 0x4b34e-ORIGIN
L_0004b34e:
    add #0x40,r4
    .org 0x4b350-ORIGIN
L_0004b350:
    exts.w r4,r5
    .org 0x4b352-ORIGIN
L_0004b352:
    cmp/gt r6,r5
    .org 0x4b354-ORIGIN
L_0004b354:
    bf/s L_0004b35a
    .org 0x4b356-ORIGIN
L_0004b356:
    mov r5,r6
    .org 0x4b358-ORIGIN
L_0004b358:
    mov #0x7f,r6
    .org 0x4b35a-ORIGIN
L_0004b35a:
    exts.w r6,r6
    .org 0x4b35c-ORIGIN
L_0004b35c:
    mov #-0x80,r5
    .org 0x4b35e-ORIGIN
L_0004b35e:
    cmp/ge r5,r6
    .org 0x4b360-ORIGIN
L_0004b360:
    bt L_0004b364
    .org 0x4b362-ORIGIN
L_0004b362:
    mov #-0x80,r6
    .org 0x4b364-ORIGIN
L_0004b364:
    mov.w P_0004b48c,r0
    .org 0x4b366-ORIGIN
L_0004b366:
    mov.b r6,@(r0,r10)
    .org 0x4b368-ORIGIN
L_0004b368:
    mov #0x0,r6
    .org 0x4b36a-ORIGIN
L_0004b36a:
    mov.w P_0004b48e,r0
    .org 0x4b36c-ORIGIN
L_0004b36c:
    mov.b r6,@(r0,r10)
    .org 0x4b36e-ORIGIN
L_0004b36e:
    mov r2,r0
    .org 0x4b370-ORIGIN
L_0004b370:
    and #0xf,r0
    .org 0x4b372-ORIGIN
L_0004b372:
    mov r0,r6
    .org 0x4b374-ORIGIN
L_0004b374:
    shll2 r6
    .org 0x4b376-ORIGIN
L_0004b376:
    shll2 r6
    .org 0x4b378-ORIGIN
L_0004b378:
    stc sr,r2
    .org 0x4b37a-ORIGIN
L_0004b37a:
    mov.w P_0004b490,r5
    .org 0x4b37c-ORIGIN
L_0004b37c:
    and r5,r2
    .org 0x4b37e-ORIGIN
L_0004b37e:
    or r6,r2
    .org 0x4b380-ORIGIN
L_0004b380:
    ldc r2,sr
    .org 0x4b382-ORIGIN
L_0004b382:
    mov #0x37,r0
    .org 0x4b384-ORIGIN
L_0004b384:
    mov.b @(r0,r14),r0
    .org 0x4b386-ORIGIN
L_0004b386:
    tst #0x2,r0
    .org 0x4b388-ORIGIN
L_0004b388:
    bt L_0004b3ec
    .org 0x4b38a-ORIGIN
L_0004b38a:
    mov.l P_0004b4fc,r7
    .org 0x4b38c-ORIGIN
L_0004b38c:
    mov #-0x7a,r0
    .org 0x4b38e-ORIGIN
L_0004b38e:
    extu.b r0,r0
    .org 0x4b390-ORIGIN
L_0004b390:
    mov.l P_0004b500,r12
    .org 0x4b392-ORIGIN
L_0004b392:
    mov.b @(r0,r7),r0
    .org 0x4b394-ORIGIN
L_0004b394:
    mov.l P_0004b504,r4
    .org 0x4b396-ORIGIN
L_0004b396:
    mov.b r0,@(0x3,r15)
    .org 0x4b398-ORIGIN
L_0004b398:
    mov #0x12,r0
    .org 0x4b39a-ORIGIN
L_0004b39a:
    mov.b @(r0,r12),r2
    .org 0x4b39c-ORIGIN
L_0004b39c:
    mov.l P_0004b508,r5
    .org 0x4b39e-ORIGIN
L_0004b39e:
    mov.l P_0004b50c,r6
    .org 0x4b3a0-ORIGIN
L_0004b3a0:
    mov.l P_0004b510,r3
    .org 0x4b3a2-ORIGIN
L_0004b3a2:
    jsr @r3
    .org 0x4b3a4-ORIGIN
L_0004b3a4:
    extu.b r2,r7
    .org 0x4b3a6-ORIGIN
L_0004b3a6:
    mov r0,r2
    .org 0x4b3a8-ORIGIN
L_0004b3a8:
    mov.w P_0004b492,r0
    .org 0x4b3aa-ORIGIN
L_0004b3aa:
    mov.l P_0004b4fc,r7
    .org 0x4b3ac-ORIGIN
L_0004b3ac:
    mov.b r2,@(r0,r10)
    .org 0x4b3ae-ORIGIN
L_0004b3ae:
    mov #-0x79,r0
    .org 0x4b3b0-ORIGIN
L_0004b3b0:
    extu.b r0,r0
    .org 0x4b3b2-ORIGIN
L_0004b3b2:
    mov.l P_0004b504,r4
    .org 0x4b3b4-ORIGIN
L_0004b3b4:
    mov.b @(r0,r7),r0
    .org 0x4b3b6-ORIGIN
L_0004b3b6:
    mov.l P_0004b508,r5
    .org 0x4b3b8-ORIGIN
L_0004b3b8:
    mov.b r0,@(0x3,r15)
    .org 0x4b3ba-ORIGIN
L_0004b3ba:
    mov #0x12,r0
    .org 0x4b3bc-ORIGIN
L_0004b3bc:
    mov.b @(r0,r12),r2
    .org 0x4b3be-ORIGIN
L_0004b3be:
    mov.l P_0004b50c,r6
    .org 0x4b3c0-ORIGIN
L_0004b3c0:
    mov.l P_0004b510,r1
    .org 0x4b3c2-ORIGIN
L_0004b3c2:
    jsr @r1
    .org 0x4b3c4-ORIGIN
L_0004b3c4:
    extu.b r2,r7
    .org 0x4b3c6-ORIGIN
L_0004b3c6:
    mov r0,r6
    .org 0x4b3c8-ORIGIN
L_0004b3c8:
    mov.w P_0004b494,r0
    .org 0x4b3ca-ORIGIN
L_0004b3ca:
    mov.b r6,@(r0,r10)
    .org 0x4b3cc-ORIGIN
L_0004b3cc:
    extu.b r6,r6
    .org 0x4b3ce-ORIGIN
L_0004b3ce:
    mov.w P_0004b492,r0
    .org 0x4b3d0-ORIGIN
L_0004b3d0:
    mov.b @(r0,r10),r2
    .org 0x4b3d2-ORIGIN
L_0004b3d2:
    extu.b r2,r5
    .org 0x4b3d4-ORIGIN
L_0004b3d4:
    exts.w r5,r2
    .org 0x4b3d6-ORIGIN
L_0004b3d6:
    add r6,r2
    .org 0x4b3d8-ORIGIN
L_0004b3d8:
    mov #-0x1,r6
    .org 0x4b3da-ORIGIN
L_0004b3da:
    shll8 r6
    .org 0x4b3dc-ORIGIN
L_0004b3dc:
    add r6,r2
    .org 0x4b3de-ORIGIN
L_0004b3de:
    mov #0x0,r6
    .org 0x4b3e0-ORIGIN
L_0004b3e0:
    cmp/gt r2,r6
    .org 0x4b3e2-ORIGIN
L_0004b3e2:
    addc r6,r2
    .org 0x4b3e4-ORIGIN
L_0004b3e4:
    shar r2
    .org 0x4b3e6-ORIGIN
L_0004b3e6:
    mov #-0x80,r6
    .org 0x4b3e8-ORIGIN
L_0004b3e8:
    bra L_0004b3ee
    .org 0x4b3ea-ORIGIN
L_0004b3ea:
    add r6,r2
    .org 0x4b3ec-ORIGIN
L_0004b3ec:
    mov #-0x80,r2
    .org 0x4b3ee-ORIGIN
L_0004b3ee:
    mov.w P_0004b496,r0
    .org 0x4b3f0-ORIGIN
L_0004b3f0:
    mov.b r2,@(r0,r10)
    .org 0x4b3f2-ORIGIN
L_0004b3f2:
    mov #0x20,r0
    .org 0x4b3f4-ORIGIN
L_0004b3f4:
    mov.l P_0004b514,r2
    .org 0x4b3f6-ORIGIN
L_0004b3f6:
    mov.w @(r0,r2),r5
    .org 0x4b3f8-ORIGIN
L_0004b3f8:
    mov #0x22,r0
    .org 0x4b3fa-ORIGIN
L_0004b3fa:
    mov.w @(r0,r2),r6
    .org 0x4b3fc-ORIGIN
L_0004b3fc:
    extu.w r5,r5
    .org 0x4b3fe-ORIGIN
L_0004b3fe:
    extu.w r6,r2
    .org 0x4b400-ORIGIN
L_0004b400:
    cmp/gt r2,r5
    .org 0x4b402-ORIGIN
L_0004b402:
    bt L_0004b406
    .org 0x4b404-ORIGIN
L_0004b404:
    mov r5,r2
    .org 0x4b406-ORIGIN
L_0004b406:
    mov r2,r5
    .org 0x4b408-ORIGIN
L_0004b408:
    extu.w r2,r6
    .org 0x4b40a-ORIGIN
L_0004b40a:
    mov.w P_0004b498,r2
    .org 0x4b40c-ORIGIN
L_0004b40c:
    add r2,r6
    .org 0x4b40e-ORIGIN
L_0004b40e:
    cmp/pz r6
    .org 0x4b410-ORIGIN
L_0004b410:
    bt/s L_0004b416
    .org 0x4b412-ORIGIN
L_0004b412:
    mov r6,r2
    .org 0x4b414-ORIGIN
L_0004b414:
    mov #0x0,r2
    .org 0x4b416-ORIGIN
L_0004b416:
    mov.w P_0004b49a,r0
    .org 0x4b418-ORIGIN
L_0004b418:
    mov.w r2,@(r0,r10)
    .org 0x4b41a-ORIGIN
L_0004b41a:
    mov.b @(0x2,r13),r0
    .org 0x4b41c-ORIGIN
L_0004b41c:
    tst #0x40,r0
    .org 0x4b41e-ORIGIN
L_0004b41e:
    bt L_0004b49c
    .org 0x4b420-ORIGIN
L_0004b420:
    mov.l P_0004b518,r6
    .org 0x4b422-ORIGIN
L_0004b422:
    extu.w r5,r5
    .org 0x4b424-ORIGIN
L_0004b424:
    mov.w @r6,r2
    .org 0x4b426-ORIGIN
L_0004b426:
    extu.w r2,r2
    .org 0x4b428-ORIGIN
L_0004b428:
    cmp/ge r2,r5
    .org 0x4b42a-ORIGIN
L_0004b42a:
    bf L_0004b49c
    .org 0x4b42c-ORIGIN
L_0004b42c:
    mov.b @(0x7,r9),r0
    .org 0x4b42e-ORIGIN
L_0004b42e:
    mov.l P_0004b51c,r4
    .org 0x4b430-ORIGIN
L_0004b430:
    mov.l P_0004b520,r5
    .org 0x4b432-ORIGIN
L_0004b432:
    mov.l P_0004b524,r2
    .org 0x4b434-ORIGIN
L_0004b434:
    jsr @r2
    .org 0x4b436-ORIGIN
L_0004b436:
    extu.b r0,r6
    .org 0x4b438-ORIGIN
L_0004b438:
    mov.l P_0004b528,r6
    .org 0x4b43a-ORIGIN
L_0004b43a:
    mov.b r0,@(0xbf,gbr)
    .org 0x4b43c-ORIGIN
L_0004b43c:
    mov #0x36,r0
    .org 0x4b43e-ORIGIN
L_0004b43e:
    mov.w @(r0,r6),r7
    .org 0x4b440-ORIGIN
L_0004b440:
    mov.l P_0004b52c,r4
    .org 0x4b442-ORIGIN
L_0004b442:
    mov.l P_0004b530,r5
    .org 0x4b444-ORIGIN
L_0004b444:
    mov.l P_0004b534,r2
    .org 0x4b446-ORIGIN
L_0004b446:
    jsr @r2
    .org 0x4b448-ORIGIN
L_0004b448:
    extu.w r7,r6
    .org 0x4b44a-ORIGIN
L_0004b44a:
    mov #-0x1,r4
    .org 0x4b44c-ORIGIN
L_0004b44c:
    extu.w r0,r2
    .org 0x4b44e-ORIGIN
L_0004b44e:
    extu.b r4,r6
    .org 0x4b450-ORIGIN
L_0004b450:
    cmp/gt r6,r2
    .org 0x4b452-ORIGIN
L_0004b452:
    bt L_0004b456
    .org 0x4b454-ORIGIN
L_0004b454:
    mov r2,r6
    .org 0x4b456-ORIGIN
L_0004b456:
    mov r6,r0
    .org 0x4b458-ORIGIN
L_0004b458:
    mov.b r0,@(0xbb,gbr)
    .org 0x4b45a-ORIGIN
L_0004b45a:
    mov.w P_0004b49a,r0
    .org 0x4b45c-ORIGIN
L_0004b45c:
    extu.b r6,r6
    .org 0x4b45e-ORIGIN
L_0004b45e:
    mov.w @(r0,r10),r2
    .org 0x4b460-ORIGIN
L_0004b460:
    mov.b @(0xbf,gbr),r0
    .org 0x4b462-ORIGIN
L_0004b462:
    extu.w r2,r3
    .org 0x4b464-ORIGIN
L_0004b464:
    extu.b r0,r2
    .org 0x4b466-ORIGIN
L_0004b466:
    mov.l P_0004b538,r0
    .org 0x4b468-ORIGIN
L_0004b468:
    mul.l r3,r2
    .org 0x4b46a-ORIGIN
L_0004b46a:
    sts macl,r2
    .org 0x4b46c-ORIGIN
L_0004b46c:
    mul.l r2,r6
    .org 0x4b46e-ORIGIN
L_0004b46e:
    mov.l P_0004b53c,r6
    .org 0x4b470-ORIGIN
L_0004b470:
    jsr @r6
    .org 0x4b472-ORIGIN
L_0004b472:
    sts macl,r1
    .org 0x4b474-ORIGIN
L_0004b474:
    mov #-0x1,r6
    .org 0x4b476-ORIGIN
L_0004b476:
    extu.b r6,r6
    .org 0x4b478-ORIGIN
L_0004b478:
    cmp/hi r6,r0
    .org 0x4b47a-ORIGIN
L_0004b47a:
    bf/s L_0004b480
    .org 0x4b47c-ORIGIN
L_0004b47c:
    mov r0,r2
    .org 0x4b47e-ORIGIN
L_0004b47e:
    mov r6,r2
    .org 0x4b480-ORIGIN
L_0004b480:
    mov r2,r0
    .org 0x4b482-ORIGIN
L_0004b482:
    mov.b r0,@(0xbd,gbr)
    .org 0x4b484-ORIGIN
L_0004b484:
    bra L_0004b4a0
    .org 0x4b486-ORIGIN
L_0004b486:
    mov r2,r4
    .org 0x4b488-ORIGIN
P_0004b488:
    .byte 0x07
    .org 0x4b489-ORIGIN
P_0004b489:
    .byte 0xf1
    .org 0x4b48a-ORIGIN
P_0004b48a:
    .byte 0x02
    .org 0x4b48b-ORIGIN
P_0004b48b:
    .byte 0x85
    .org 0x4b48c-ORIGIN
P_0004b48c:
    .byte 0x02
    .org 0x4b48d-ORIGIN
P_0004b48d:
    .byte 0x87
    .org 0x4b48e-ORIGIN
P_0004b48e:
    .byte 0x02
    .org 0x4b48f-ORIGIN
P_0004b48f:
    .byte 0x86
    .org 0x4b490-ORIGIN
P_0004b490:
    .byte 0xff
    .org 0x4b491-ORIGIN
P_0004b491:
    .byte 0x0f
    .org 0x4b492-ORIGIN
P_0004b492:
    .byte 0x02
    .org 0x4b493-ORIGIN
P_0004b493:
    .byte 0x89
    .org 0x4b494-ORIGIN
P_0004b494:
    .byte 0x02
    .org 0x4b495-ORIGIN
P_0004b495:
    .byte 0x8a
    .org 0x4b496-ORIGIN
P_0004b496:
    .byte 0x02
    .org 0x4b497-ORIGIN
P_0004b497:
    .byte 0x88
    .org 0x4b498-ORIGIN
P_0004b498:
    .byte 0xe3
    .org 0x4b499-ORIGIN
P_0004b499:
    .byte 0x4a
    .org 0x4b49a-ORIGIN
P_0004b49a:
    .byte 0x06
    .org 0x4b49b-ORIGIN
P_0004b49b:
    .byte 0x74
    .org 0x4b49c-ORIGIN
L_0004b49c:
    mov #0x0,r4
    .org 0x4b49e-ORIGIN
L_0004b49e:
    mov r4,r0
    .org 0x4b4a0-ORIGIN
L_0004b4a0:
    mov.b r0,@(0x49,gbr)
    .org 0x4b4a2-ORIGIN
L_0004b4a2:
    extu.b r4,r4
    .org 0x4b4a4-ORIGIN
L_0004b4a4:
    mov.b @(0x4f,gbr),r0
    .org 0x4b4a6-ORIGIN
L_0004b4a6:
    extu.b r0,r6
    .org 0x4b4a8-ORIGIN
L_0004b4a8:
    mov.w P_0004b4d8,r0
    .org 0x4b4aa-ORIGIN
L_0004b4aa:
    mov.b @(r0,r10),r2
    .org 0x4b4ac-ORIGIN
L_0004b4ac:
    mov.w P_0004b4da,r0
    .org 0x4b4ae-ORIGIN
L_0004b4ae:
    extu.b r2,r5
    .org 0x4b4b0-ORIGIN
L_0004b4b0:
    mov.b @(r0,r10),r7
    .org 0x4b4b2-ORIGIN
L_0004b4b2:
    mov.w P_0004b4dc,r0
    .org 0x4b4b4-ORIGIN
L_0004b4b4:
    add r6,r7
    .org 0x4b4b6-ORIGIN
L_0004b4b6:
    mov.b @(r0,r10),r6
    .org 0x4b4b8-ORIGIN
L_0004b4b8:
    add r6,r7
    .org 0x4b4ba-ORIGIN
L_0004b4ba:
    add r5,r7
    .org 0x4b4bc-ORIGIN
L_0004b4bc:
    add r4,r7
    .org 0x4b4be-ORIGIN
L_0004b4be:
    add #-0x80,r7
    .org 0x4b4c0-ORIGIN
L_0004b4c0:
    exts.w r7,r2
    .org 0x4b4c2-ORIGIN
L_0004b4c2:
    mov #0x7f,r6
    .org 0x4b4c4-ORIGIN
L_0004b4c4:
    cmp/gt r6,r2
    .org 0x4b4c6-ORIGIN
L_0004b4c6:
    bf/s L_0004b4cc
    .org 0x4b4c8-ORIGIN
L_0004b4c8:
    mov r2,r6
    .org 0x4b4ca-ORIGIN
L_0004b4ca:
    mov #0x7f,r6
    .org 0x4b4cc-ORIGIN
L_0004b4cc:
    exts.w r6,r2
    .org 0x4b4ce-ORIGIN
L_0004b4ce:
    mov #-0x80,r6
    .org 0x4b4d0-ORIGIN
L_0004b4d0:
    cmp/ge r6,r2
    .org 0x4b4d2-ORIGIN
L_0004b4d2:
    bt L_0004b542
    .org 0x4b4d4-ORIGIN
L_0004b4d4:
    bra L_0004b540
    .org 0x4b4d6-ORIGIN
L_0004b4d6:
    nop
    .org 0x4b4d8-ORIGIN
P_0004b4d8:
    .byte 0x02
    .org 0x4b4d9-ORIGIN
P_0004b4d9:
    .byte 0x88
    .org 0x4b4da-ORIGIN
P_0004b4da:
    .byte 0x02
    .org 0x4b4db-ORIGIN
P_0004b4db:
    .byte 0x85
    .org 0x4b4dc-ORIGIN
P_0004b4dc:
    .byte 0x02
    .org 0x4b4dd-ORIGIN
P_0004b4dd:
    .byte 0x86
    .org 0x4b4e0-ORIGIN
P_0004b4e0:
    .byte 0x00
    .org 0x4b4e1-ORIGIN
P_0004b4e1:
    .byte 0x00
    .org 0x4b4e2-ORIGIN
P_0004b4e2:
    .byte 0x92
    .org 0x4b4e3-ORIGIN
P_0004b4e3:
    .byte 0x76
    .org 0x4b4e4-ORIGIN
P_0004b4e4:
    .byte 0x00
    .org 0x4b4e5-ORIGIN
P_0004b4e5:
    .byte 0x00
    .org 0x4b4e6-ORIGIN
P_0004b4e6:
    .byte 0x87
    .org 0x4b4e7-ORIGIN
P_0004b4e7:
    .byte 0x89
    .org 0x4b4e8-ORIGIN
P_0004b4e8:
    .byte 0x00
    .org 0x4b4e9-ORIGIN
P_0004b4e9:
    .byte 0x02
    .org 0x4b4ea-ORIGIN
P_0004b4ea:
    .byte 0x1b
    .org 0x4b4eb-ORIGIN
P_0004b4eb:
    .byte 0xbc
    .org 0x4b4ec-ORIGIN
P_0004b4ec:
    .byte 0x00
    .org 0x4b4ed-ORIGIN
P_0004b4ed:
    .byte 0x01
    .org 0x4b4ee-ORIGIN
P_0004b4ee:
    .byte 0x1f
    .org 0x4b4ef-ORIGIN
P_0004b4ef:
    .byte 0x0a
    .org 0x4b4f0-ORIGIN
P_0004b4f0:
    .byte 0xff
    .org 0x4b4f1-ORIGIN
P_0004b4f1:
    .byte 0xff
    .org 0x4b4f2-ORIGIN
P_0004b4f2:
    .byte 0x24
    .org 0x4b4f3-ORIGIN
P_0004b4f3:
    .byte 0x70
    .org 0x4b4f4-ORIGIN
P_0004b4f4:
    .byte 0xff
    .org 0x4b4f5-ORIGIN
P_0004b4f5:
    .byte 0xff
    .org 0x4b4f6-ORIGIN
P_0004b4f6:
    .byte 0x12
    .org 0x4b4f7-ORIGIN
P_0004b4f7:
    .byte 0x0e
    .org 0x4b4f8-ORIGIN
P_0004b4f8:
    .byte 0xff
    .org 0x4b4f9-ORIGIN
P_0004b4f9:
    .byte 0xff
    .org 0x4b4fa-ORIGIN
P_0004b4fa:
    .byte 0x12
    .org 0x4b4fb-ORIGIN
P_0004b4fb:
    .byte 0x4c
    .org 0x4b4fc-ORIGIN
P_0004b4fc:
    .byte 0xff
    .org 0x4b4fd-ORIGIN
P_0004b4fd:
    .byte 0xff
    .org 0x4b4fe-ORIGIN
P_0004b4fe:
    .byte 0x23
    .org 0x4b4ff-ORIGIN
P_0004b4ff:
    .byte 0xbc
    .org 0x4b500-ORIGIN
P_0004b500:
    .byte 0xff
    .org 0x4b501-ORIGIN
P_0004b501:
    .byte 0xff
    .org 0x4b502-ORIGIN
P_0004b502:
    .byte 0x11
    .org 0x4b503-ORIGIN
P_0004b503:
    .byte 0x9c
    .org 0x4b504-ORIGIN
P_0004b504:
    .byte 0x00
    .org 0x4b505-ORIGIN
P_0004b505:
    .byte 0x00
    .org 0x4b506-ORIGIN
P_0004b506:
    .byte 0x9d
    .org 0x4b507-ORIGIN
P_0004b507:
    .byte 0xba
    .org 0x4b508-ORIGIN
P_0004b508:
    .byte 0x00
    .org 0x4b509-ORIGIN
P_0004b509:
    .byte 0x01
    .org 0x4b50a-ORIGIN
P_0004b50a:
    .byte 0x2e
    .org 0x4b50b-ORIGIN
P_0004b50b:
    .byte 0xba
    .org 0x4b50c-ORIGIN
P_0004b50c:
    .byte 0x00
    .org 0x4b50d-ORIGIN
P_0004b50d:
    .byte 0x01
    .org 0x4b50e-ORIGIN
P_0004b50e:
    .byte 0x2e
    .org 0x4b50f-ORIGIN
P_0004b50f:
    .byte 0x92
    .org 0x4b510-ORIGIN
P_0004b510:
    .byte 0x00
    .org 0x4b511-ORIGIN
P_0004b511:
    .byte 0x02
    .org 0x4b512-ORIGIN
P_0004b512:
    .byte 0x61
    .org 0x4b513-ORIGIN
P_0004b513:
    .byte 0x40
    .org 0x4b514-ORIGIN
P_0004b514:
    .byte 0xff
    .org 0x4b515-ORIGIN
P_0004b515:
    .byte 0xff
    .org 0x4b516-ORIGIN
P_0004b516:
    .byte 0x28
    .org 0x4b517-ORIGIN
P_0004b517:
    .byte 0x98
    .org 0x4b518-ORIGIN
P_0004b518:
    .byte 0x00
    .org 0x4b519-ORIGIN
P_0004b519:
    .byte 0x00
    .org 0x4b51a-ORIGIN
P_0004b51a:
    .byte 0x90
    .org 0x4b51b-ORIGIN
P_0004b51b:
    .byte 0x10
    .org 0x4b51c-ORIGIN
P_0004b51c:
    .byte 0x00
    .org 0x4b51d-ORIGIN
P_0004b51d:
    .byte 0x01
    .org 0x4b51e-ORIGIN
P_0004b51e:
    .byte 0x1e
    .org 0x4b51f-ORIGIN
P_0004b51f:
    .byte 0xfa
    .org 0x4b520-ORIGIN
P_0004b520:
    .byte 0x00
    .org 0x4b521-ORIGIN
P_0004b521:
    .byte 0x01
    .org 0x4b522-ORIGIN
P_0004b522:
    .byte 0x1e
    .org 0x4b523-ORIGIN
P_0004b523:
    .byte 0xea
    .org 0x4b524-ORIGIN
P_0004b524:
    .byte 0x00
    .org 0x4b525-ORIGIN
P_0004b525:
    .byte 0x02
    .org 0x4b526-ORIGIN
P_0004b526:
    .byte 0x64
    .org 0x4b527-ORIGIN
P_0004b527:
    .byte 0x74
    .org 0x4b528-ORIGIN
P_0004b528:
    .byte 0xff
    .org 0x4b529-ORIGIN
P_0004b529:
    .byte 0xff
    .org 0x4b52a-ORIGIN
P_0004b52a:
    .byte 0x10
    .org 0x4b52b-ORIGIN
P_0004b52b:
    .byte 0x94
    .org 0x4b52c-ORIGIN
P_0004b52c:
    .byte 0x00
    .org 0x4b52d-ORIGIN
P_0004b52d:
    .byte 0x01
    .org 0x4b52e-ORIGIN
P_0004b52e:
    .byte 0x47
    .org 0x4b52f-ORIGIN
P_0004b52f:
    .byte 0xca
    .org 0x4b530-ORIGIN
P_0004b530:
    .byte 0x00
    .org 0x4b531-ORIGIN
P_0004b531:
    .byte 0x01
    .org 0x4b532-ORIGIN
P_0004b532:
    .byte 0x46
    .org 0x4b533-ORIGIN
P_0004b533:
    .byte 0x0a
    .org 0x4b534-ORIGIN
P_0004b534:
    .byte 0x00
    .org 0x4b535-ORIGIN
P_0004b535:
    .byte 0x02
    .org 0x4b536-ORIGIN
P_0004b536:
    .byte 0x64
    .org 0x4b537-ORIGIN
P_0004b537:
    .byte 0xcc
    .org 0x4b538-ORIGIN
P_0004b538:
    .byte 0x00
    .org 0x4b539-ORIGIN
P_0004b539:
    .byte 0x07
    .org 0x4b53a-ORIGIN
P_0004b53a:
    .byte 0xa1
    .org 0x4b53b-ORIGIN
P_0004b53b:
    .byte 0x20
    .org 0x4b53c-ORIGIN
P_0004b53c:
    .byte 0x00
    .org 0x4b53d-ORIGIN
P_0004b53d:
    .byte 0x02
    .org 0x4b53e-ORIGIN
P_0004b53e:
    .byte 0x1c
    .org 0x4b53f-ORIGIN
P_0004b53f:
    .byte 0xe0
    .org 0x4b540-ORIGIN
L_0004b540:
    mov #-0x80,r2
    .org 0x4b542-ORIGIN
L_0004b542:
    mov.l P_0004b754,r11
    .org 0x4b544-ORIGIN
L_0004b544:
    mov #0x32,r0
    .org 0x4b546-ORIGIN
L_0004b546:
    mov.b r2,@(r0,r11)
    .org 0x4b548-ORIGIN
L_0004b548:
    add #0x8,r15
    .org 0x4b54a-ORIGIN
L_0004b54a:
    ldc.l @r15+,gbr
    .org 0x4b54c-ORIGIN
L_0004b54c:
    lds.l @r15+,macl
    .org 0x4b54e-ORIGIN
L_0004b54e:
    lds.l @r15+,pr
    .org 0x4b550-ORIGIN
L_0004b550:
    mov.l @r15+,r14
    .org 0x4b552-ORIGIN
L_0004b552:
    mov.l @r15+,r13
    .org 0x4b554-ORIGIN
L_0004b554:
    mov.l @r15+,r12
    .org 0x4b556-ORIGIN
L_0004b556:
    mov.l @r15+,r11
    .org 0x4b558-ORIGIN
L_0004b558:
    mov.l @r15+,r10
    .org 0x4b55a-ORIGIN
L_0004b55a:
    rts
    .org 0x4b55c-ORIGIN
L_0004b55c:
    mov.l @r15+,r9
    .org 0x4b754-ORIGIN
P_0004b754:
    .byte 0xff
    .org 0x4b755-ORIGIN
P_0004b755:
    .byte 0xff
    .org 0x4b756-ORIGIN
P_0004b756:
    .byte 0x23
    .org 0x4b757-ORIGIN
P_0004b757:
    .byte 0xbc
