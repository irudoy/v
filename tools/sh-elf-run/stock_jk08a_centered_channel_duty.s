! Complete stock centered-channel producer and indexed duty consumer with all real helpers.
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
    .org 0xbe5bc-ORIGIN
L_000be5bc:
    mov.l r10,@-r15
    .org 0xbe5be-ORIGIN
L_000be5be:
    mov.l r11,@-r15
    .org 0xbe5c0-ORIGIN
L_000be5c0:
    mov.l r12,@-r15
    .org 0xbe5c2-ORIGIN
L_000be5c2:
    mov.l r13,@-r15
    .org 0xbe5c4-ORIGIN
L_000be5c4:
    mov.l r14,@-r15
    .org 0xbe5c6-ORIGIN
L_000be5c6:
    sts.l pr,@-r15
    .org 0xbe5c8-ORIGIN
L_000be5c8:
    mov.l P_000be74c,r11
    .org 0xbe5ca-ORIGIN
L_000be5ca:
    mov.b @r11,r0
    .org 0xbe5cc-ORIGIN
L_000be5cc:
    tst #0x80,r0
    .org 0xbe5ce-ORIGIN
L_000be5ce:
    bt L_000be682
    .org 0xbe5d0-ORIGIN
L_000be5d0:
    mov.l P_000be750,r2
    .org 0xbe5d2-ORIGIN
L_000be5d2:
    mov.l P_000be754,r4
    .org 0xbe5d4-ORIGIN
L_000be5d4:
    mov.b @(0x2,r2),r0
    .org 0xbe5d6-ORIGIN
L_000be5d6:
    mov.b @r4,r2
    .org 0xbe5d8-ORIGIN
L_000be5d8:
    mov #-0x80,r4
    .org 0xbe5da-ORIGIN
L_000be5da:
    extu.b r4,r4
    .org 0xbe5dc-ORIGIN
L_000be5dc:
    extu.b r2,r7
    .org 0xbe5de-ORIGIN
L_000be5de:
    extu.b r0,r5
    .org 0xbe5e0-ORIGIN
L_000be5e0:
    add r4,r7
    .org 0xbe5e2-ORIGIN
L_000be5e2:
    cmp/hi r7,r5
    .org 0xbe5e4-ORIGIN
L_000be5e4:
    bt L_000be616
    .org 0xbe5e6-ORIGIN
L_000be5e6:
    mov.l P_000be758,r6
    .org 0xbe5e8-ORIGIN
L_000be5e8:
    mov.l P_000be75c,r13
    .org 0xbe5ea-ORIGIN
L_000be5ea:
    mov.b @r6,r2
    .org 0xbe5ec-ORIGIN
L_000be5ec:
    mov.w P_000be614,r0
    .org 0xbe5ee-ORIGIN
L_000be5ee:
    mov.l P_000be760,r6
    .org 0xbe5f0-ORIGIN
L_000be5f0:
    mov.b r2,@(r0,r13)
    .org 0xbe5f2-ORIGIN
L_000be5f2:
    mov #0x1e,r0
    .org 0xbe5f4-ORIGIN
L_000be5f4:
    mov.b @(r0,r6),r0
    .org 0xbe5f6-ORIGIN
L_000be5f6:
    and #0xbf,r0
    .org 0xbe5f8-ORIGIN
L_000be5f8:
    mov r0,r2
    .org 0xbe5fa-ORIGIN
L_000be5fa:
    mov #0x1e,r0
    .org 0xbe5fc-ORIGIN
L_000be5fc:
    mov.b r2,@(r0,r6)
    .org 0xbe5fe-ORIGIN
L_000be5fe:
    mov #0x37,r0
    .org 0xbe600-ORIGIN
L_000be600:
    mov.b @(r0,r6),r0
    .org 0xbe602-ORIGIN
L_000be602:
    or #0x1,r0
    .org 0xbe604-ORIGIN
L_000be604:
    mov r0,r2
    .org 0xbe606-ORIGIN
L_000be606:
    mov #0x37,r0
    .org 0xbe608-ORIGIN
L_000be608:
    bra L_000be806
    .org 0xbe60a-ORIGIN
L_000be60a:
    mov.b r2,@(r0,r6)
    .org 0xbe614-ORIGIN
P_000be614:
    .byte 0x07
    .org 0xbe615-ORIGIN
P_000be615:
    .byte 0xcd
    .org 0xbe616-ORIGIN
L_000be616:
    mov.l P_000be760,r7
    .org 0xbe618-ORIGIN
L_000be618:
    mov #0x1e,r0
    .org 0xbe61a-ORIGIN
L_000be61a:
    mov.l P_000be764,r6
    .org 0xbe61c-ORIGIN
L_000be61c:
    mov #-0x80,r14
    .org 0xbe61e-ORIGIN
L_000be61e:
    mov.b @(r0,r7),r2
    .org 0xbe620-ORIGIN
L_000be620:
    extu.b r14,r14
    .org 0xbe622-ORIGIN
L_000be622:
    mov.b @(0x2,r6),r0
    .org 0xbe624-ORIGIN
L_000be624:
    extu.b r2,r4
    .org 0xbe626-ORIGIN
L_000be626:
    extu.b r0,r2
    .org 0xbe628-ORIGIN
L_000be628:
    add r14,r2
    .org 0xbe62a-ORIGIN
L_000be62a:
    cmp/hs r2,r5
    .org 0xbe62c-ORIGIN
L_000be62c:
    bf L_000be682
    .org 0xbe62e-ORIGIN
L_000be62e:
    mov r4,r0
    .org 0xbe630-ORIGIN
L_000be630:
    and #0x40,r0
    .org 0xbe632-ORIGIN
L_000be632:
    tst r0,r0
    .org 0xbe634-ORIGIN
L_000be634:
    bf/s L_000be65a
    .org 0xbe636-ORIGIN
L_000be636:
    mov r0,r6
    .org 0xbe638-ORIGIN
L_000be638:
    mov.l P_000be764,r6
    .org 0xbe63a-ORIGIN
L_000be63a:
    mov.l P_000be75c,r13
    .org 0xbe63c-ORIGIN
L_000be63c:
    mov.b @r6,r2
    .org 0xbe63e-ORIGIN
L_000be63e:
    mov.w P_000be732,r0
    .org 0xbe640-ORIGIN
L_000be640:
    mov.l P_000be768,r5
    .org 0xbe642-ORIGIN
L_000be642:
    mov.b r2,@(r0,r13)
    .org 0xbe644-ORIGIN
L_000be644:
    mov.b @(0x6,r6),r0
    .org 0xbe646-ORIGIN
L_000be646:
    extu.b r0,r0
    .org 0xbe648-ORIGIN
L_000be648:
    shll r0
    .org 0xbe64a-ORIGIN
L_000be64a:
    mov.w r0,@(0x4,r5)
    .org 0xbe64c-ORIGIN
L_000be64c:
    mov #0x40,r0
    .org 0xbe64e-ORIGIN
L_000be64e:
    or r0,r4
    .org 0xbe650-ORIGIN
L_000be650:
    mov #0x1e,r0
    .org 0xbe652-ORIGIN
L_000be652:
    mov.b r4,@(r0,r7)
    .org 0xbe654-ORIGIN
L_000be654:
    exts.b r4,r0
    .org 0xbe656-ORIGIN
L_000be656:
    and #0x40,r0
    .org 0xbe658-ORIGIN
L_000be658:
    mov r0,r6
    .org 0xbe65a-ORIGIN
L_000be65a:
    extu.b r6,r6
    .org 0xbe65c-ORIGIN
L_000be65c:
    tst r6,r6
    .org 0xbe65e-ORIGIN
L_000be65e:
    bt L_000be674
    .org 0xbe660-ORIGIN
L_000be660:
    mov.l P_000be768,r5
    .org 0xbe662-ORIGIN
L_000be662:
    mov.w @(0x4,r5),r0
    .org 0xbe664-ORIGIN
L_000be664:
    tst r0,r0
    .org 0xbe666-ORIGIN
L_000be666:
    bf L_000be674
    .org 0xbe668-ORIGIN
L_000be668:
    mov.l P_000be764,r3
    .org 0xbe66a-ORIGIN
L_000be66a:
    mov.l P_000be75c,r13
    .org 0xbe66c-ORIGIN
L_000be66c:
    mov.b @(0x1,r3),r0
    .org 0xbe66e-ORIGIN
L_000be66e:
    mov r0,r2
    .org 0xbe670-ORIGIN
L_000be670:
    mov.w P_000be732,r0
    .org 0xbe672-ORIGIN
L_000be672:
    mov.b r2,@(r0,r13)
    .org 0xbe674-ORIGIN
L_000be674:
    mov #0x37,r0
    .org 0xbe676-ORIGIN
L_000be676:
    mov.b @(r0,r7),r0
    .org 0xbe678-ORIGIN
L_000be678:
    or #0x1,r0
    .org 0xbe67a-ORIGIN
L_000be67a:
    mov r0,r2
    .org 0xbe67c-ORIGIN
L_000be67c:
    mov #0x37,r0
    .org 0xbe67e-ORIGIN
L_000be67e:
    bra L_000be806
    .org 0xbe680-ORIGIN
L_000be680:
    mov.b r2,@(r0,r7)
    .org 0xbe682-ORIGIN
L_000be682:
    mov.l P_000be760,r6
    .org 0xbe684-ORIGIN
L_000be684:
    mov #0x1e,r0
    .org 0xbe686-ORIGIN
L_000be686:
    mov.l P_000be75c,r14
    .org 0xbe688-ORIGIN
L_000be688:
    mov #-0x80,r12
    .org 0xbe68a-ORIGIN
L_000be68a:
    mov.b @(r0,r6),r0
    .org 0xbe68c-ORIGIN
L_000be68c:
    extu.b r12,r12
    .org 0xbe68e-ORIGIN
L_000be68e:
    shll16 r12
    .org 0xbe690-ORIGIN
L_000be690:
    mov.l P_000be76c,r10
    .org 0xbe692-ORIGIN
L_000be692:
    and #0xbf,r0
    .org 0xbe694-ORIGIN
L_000be694:
    mov.l P_000be770,r13
    .org 0xbe696-ORIGIN
L_000be696:
    mov r0,r2
    .org 0xbe698-ORIGIN
L_000be698:
    mov #0x1e,r0
    .org 0xbe69a-ORIGIN
L_000be69a:
    mov.b r2,@(r0,r6)
    .org 0xbe69c-ORIGIN
L_000be69c:
    mov #0x37,r0
    .org 0xbe69e-ORIGIN
L_000be69e:
    mov.b @(r0,r6),r0
    .org 0xbe6a0-ORIGIN
L_000be6a0:
    mov.b @r10,r5
    .org 0xbe6a2-ORIGIN
L_000be6a2:
    and #0xfe,r0
    .org 0xbe6a4-ORIGIN
L_000be6a4:
    mov r0,r2
    .org 0xbe6a6-ORIGIN
L_000be6a6:
    mov #0x37,r0
    .org 0xbe6a8-ORIGIN
L_000be6a8:
    mov.b r2,@(r0,r6)
    .org 0xbe6aa-ORIGIN
L_000be6aa:
    extu.b r5,r5
    .org 0xbe6ac-ORIGIN
L_000be6ac:
    mov.w P_000be734,r0
    .org 0xbe6ae-ORIGIN
L_000be6ae:
    mov r5,r4
    .org 0xbe6b0-ORIGIN
L_000be6b0:
    mov.l @(r0,r14),r6
    .org 0xbe6b2-ORIGIN
L_000be6b2:
    mov r5,r0
    .org 0xbe6b4-ORIGIN
L_000be6b4:
    sub r12,r6
    .org 0xbe6b6-ORIGIN
L_000be6b6:
    shll2 r6
    .org 0xbe6b8-ORIGIN
L_000be6b8:
    shll2 r6
    .org 0xbe6ba-ORIGIN
L_000be6ba:
    shll2 r6
    .org 0xbe6bc-ORIGIN
L_000be6bc:
    shll r6
    .org 0xbe6be-ORIGIN
L_000be6be:
    jsr @r13
    .org 0xbe6c0-ORIGIN
L_000be6c0:
    mov r6,r1
    .org 0xbe6c2-ORIGIN
L_000be6c2:
    mov #-0x80,r6
    .org 0xbe6c4-ORIGIN
L_000be6c4:
    extu.b r6,r6
    .org 0xbe6c6-ORIGIN
L_000be6c6:
    shll16 r6
    .org 0xbe6c8-ORIGIN
L_000be6c8:
    add r6,r0
    .org 0xbe6ca-ORIGIN
L_000be6ca:
    cmp/pz r0
    .org 0xbe6cc-ORIGIN
L_000be6cc:
    bt/s L_000be6d2
    .org 0xbe6ce-ORIGIN
L_000be6ce:
    mov r0,r6
    .org 0xbe6d0-ORIGIN
L_000be6d0:
    mov #0x0,r6
    .org 0xbe6d2-ORIGIN
L_000be6d2:
    mov.l P_000be744,r7
    .org 0xbe6d4-ORIGIN
L_000be6d4:
    cmp/gt r7,r6
    .org 0xbe6d6-ORIGIN
L_000be6d6:
    bf/s L_000be6dc
    .org 0xbe6d8-ORIGIN
L_000be6d8:
    mov r6,r2
    .org 0xbe6da-ORIGIN
L_000be6da:
    mov r7,r2
    .org 0xbe6dc-ORIGIN
L_000be6dc:
    mov.w P_000be736,r0
    .org 0xbe6de-ORIGIN
L_000be6de:
    mov.b @r10,r5
    .org 0xbe6e0-ORIGIN
L_000be6e0:
    mov.l r2,@(r0,r14)
    .org 0xbe6e2-ORIGIN
L_000be6e2:
    mov.w P_000be738,r0
    .org 0xbe6e4-ORIGIN
L_000be6e4:
    extu.b r5,r5
    .org 0xbe6e6-ORIGIN
L_000be6e6:
    mov.l @(r0,r14),r6
    .org 0xbe6e8-ORIGIN
L_000be6e8:
    mov r5,r0
    .org 0xbe6ea-ORIGIN
L_000be6ea:
    sub r12,r6
    .org 0xbe6ec-ORIGIN
L_000be6ec:
    shll2 r6
    .org 0xbe6ee-ORIGIN
L_000be6ee:
    mov r6,r1
    .org 0xbe6f0-ORIGIN
L_000be6f0:
    shll2 r1
    .org 0xbe6f2-ORIGIN
L_000be6f2:
    shll2 r1
    .org 0xbe6f4-ORIGIN
L_000be6f4:
    jsr @r13
    .org 0xbe6f6-ORIGIN
L_000be6f6:
    shll r1
    .org 0xbe6f8-ORIGIN
L_000be6f8:
    mov #-0x80,r6
    .org 0xbe6fa-ORIGIN
L_000be6fa:
    extu.b r6,r6
    .org 0xbe6fc-ORIGIN
L_000be6fc:
    shll16 r6
    .org 0xbe6fe-ORIGIN
L_000be6fe:
    add r6,r0
    .org 0xbe700-ORIGIN
L_000be700:
    cmp/pz r0
    .org 0xbe702-ORIGIN
L_000be702:
    bt/s L_000be708
    .org 0xbe704-ORIGIN
L_000be704:
    mov r0,r6
    .org 0xbe706-ORIGIN
L_000be706:
    mov #0x0,r6
    .org 0xbe708-ORIGIN
L_000be708:
    mov.l P_000be744,r7
    .org 0xbe70a-ORIGIN
L_000be70a:
    cmp/gt r7,r6
    .org 0xbe70c-ORIGIN
L_000be70c:
    bf/s L_000be712
    .org 0xbe70e-ORIGIN
L_000be70e:
    mov r6,r2
    .org 0xbe710-ORIGIN
L_000be710:
    mov r7,r2
    .org 0xbe712-ORIGIN
L_000be712:
    mov.w P_000be73a,r0
    .org 0xbe714-ORIGIN
L_000be714:
    mov.l r2,@(r0,r14)
    .org 0xbe716-ORIGIN
L_000be716:
    mov.b @(0x1,r11),r0
    .org 0xbe718-ORIGIN
L_000be718:
    tst #0x1,r0
    .org 0xbe71a-ORIGIN
L_000be71a:
    bt L_000be784
    .org 0xbe71c-ORIGIN
L_000be71c:
    mov.l P_000be774,r6
    .org 0xbe71e-ORIGIN
L_000be71e:
    mov #-0x8,r0
    .org 0xbe720-ORIGIN
L_000be720:
    extu.b r0,r0
    .org 0xbe722-ORIGIN
L_000be722:
    mov.l P_000be778,r4
    .org 0xbe724-ORIGIN
L_000be724:
    mov.b @(r0,r6),r7
    .org 0xbe726-ORIGIN
L_000be726:
    mov.l P_000be77c,r5
    .org 0xbe728-ORIGIN
L_000be728:
    mov.l P_000be780,r2
    .org 0xbe72a-ORIGIN
L_000be72a:
    jsr @r2
    .org 0xbe72c-ORIGIN
L_000be72c:
    extu.b r7,r6
    .org 0xbe72e-ORIGIN
L_000be72e:
    bra L_000be792
    .org 0xbe730-ORIGIN
L_000be730:
    nop
    .org 0xbe732-ORIGIN
P_000be732:
    .byte 0x07
    .org 0xbe733-ORIGIN
P_000be733:
    .byte 0xcd
    .org 0xbe734-ORIGIN
P_000be734:
    .byte 0x08
    .org 0xbe735-ORIGIN
P_000be735:
    .byte 0x70
    .org 0xbe736-ORIGIN
P_000be736:
    .byte 0x04
    .org 0xbe737-ORIGIN
P_000be737:
    .byte 0x5c
    .org 0xbe738-ORIGIN
P_000be738:
    .byte 0x08
    .org 0xbe739-ORIGIN
P_000be739:
    .byte 0x74
    .org 0xbe73a-ORIGIN
P_000be73a:
    .byte 0x04
    .org 0xbe73b-ORIGIN
P_000be73b:
    .byte 0x60
    .org 0xbe744-ORIGIN
P_000be744:
    .byte 0x00
    .org 0xbe745-ORIGIN
P_000be745:
    .byte 0xff
    .org 0xbe746-ORIGIN
P_000be746:
    .byte 0xff
    .org 0xbe747-ORIGIN
P_000be747:
    .byte 0xff
    .org 0xbe74c-ORIGIN
P_000be74c:
    .byte 0x00
    .org 0xbe74d-ORIGIN
P_000be74d:
    .byte 0x00
    .org 0xbe74e-ORIGIN
P_000be74e:
    .byte 0x86
    .org 0xbe74f-ORIGIN
P_000be74f:
    .byte 0x15
    .org 0xbe750-ORIGIN
P_000be750:
    .byte 0xff
    .org 0xbe751-ORIGIN
P_000be751:
    .byte 0xff
    .org 0xbe752-ORIGIN
P_000be752:
    .byte 0x23
    .org 0xbe753-ORIGIN
P_000be753:
    .byte 0x24
    .org 0xbe754-ORIGIN
P_000be754:
    .byte 0x00
    .org 0xbe755-ORIGIN
P_000be755:
    .byte 0x00
    .org 0xbe756-ORIGIN
P_000be756:
    .byte 0x88
    .org 0xbe757-ORIGIN
P_000be757:
    .byte 0x30
    .org 0xbe758-ORIGIN
P_000be758:
    .byte 0x00
    .org 0xbe759-ORIGIN
P_000be759:
    .byte 0x00
    .org 0xbe75a-ORIGIN
P_000be75a:
    .byte 0x88
    .org 0xbe75b-ORIGIN
P_000be75b:
    .byte 0x2f
    .org 0xbe75c-ORIGIN
P_000be75c:
    .byte 0xff
    .org 0xbe75d-ORIGIN
P_000be75d:
    .byte 0xff
    .org 0xbe75e-ORIGIN
P_000be75e:
    .byte 0x12
    .org 0xbe75f-ORIGIN
P_000be75f:
    .byte 0x8c
    .org 0xbe760-ORIGIN
P_000be760:
    .byte 0xff
    .org 0xbe761-ORIGIN
P_000be761:
    .byte 0xff
    .org 0xbe762-ORIGIN
P_000be762:
    .byte 0x24
    .org 0xbe763-ORIGIN
P_000be763:
    .byte 0x70
    .org 0xbe764-ORIGIN
P_000be764:
    .byte 0x00
    .org 0xbe765-ORIGIN
P_000be765:
    .byte 0x00
    .org 0xbe766-ORIGIN
P_000be766:
    .byte 0x86
    .org 0xbe767-ORIGIN
P_000be767:
    .byte 0xb7
    .org 0xbe768-ORIGIN
P_000be768:
    .byte 0xff
    .org 0xbe769-ORIGIN
P_000be769:
    .byte 0xff
    .org 0xbe76a-ORIGIN
P_000be76a:
    .byte 0x26
    .org 0xbe76b-ORIGIN
P_000be76b:
    .byte 0x04
    .org 0xbe76c-ORIGIN
P_000be76c:
    .byte 0x00
    .org 0xbe76d-ORIGIN
P_000be76d:
    .byte 0x00
    .org 0xbe76e-ORIGIN
P_000be76e:
    .byte 0x8d
    .org 0xbe76f-ORIGIN
P_000be76f:
    .byte 0xd8
    .org 0xbe770-ORIGIN
P_000be770:
    .byte 0x00
    .org 0xbe771-ORIGIN
P_000be771:
    .byte 0x02
    .org 0xbe772-ORIGIN
P_000be772:
    .byte 0x1b
    .org 0xbe773-ORIGIN
P_000be773:
    .byte 0xbc
    .org 0xbe774-ORIGIN
P_000be774:
    .byte 0xff
    .org 0xbe775-ORIGIN
P_000be775:
    .byte 0xff
    .org 0xbe776-ORIGIN
P_000be776:
    .byte 0x26
    .org 0xbe777-ORIGIN
P_000be777:
    .byte 0x7a
    .org 0xbe778-ORIGIN
P_000be778:
    .byte 0x00
    .org 0xbe779-ORIGIN
P_000be779:
    .byte 0x01
    .org 0xbe77a-ORIGIN
P_000be77a:
    .byte 0x2e
    .org 0xbe77b-ORIGIN
P_000be77b:
    .byte 0x82
    .org 0xbe77c-ORIGIN
P_000be77c:
    .byte 0x00
    .org 0xbe77d-ORIGIN
P_000be77d:
    .byte 0x01
    .org 0xbe77e-ORIGIN
P_000be77e:
    .byte 0x1b
    .org 0xbe77f-ORIGIN
P_000be77f:
    .byte 0xdb
    .org 0xbe780-ORIGIN
P_000be780:
    .byte 0x00
    .org 0xbe781-ORIGIN
P_000be781:
    .byte 0x02
    .org 0xbe782-ORIGIN
P_000be782:
    .byte 0x64
    .org 0xbe783-ORIGIN
P_000be783:
    .byte 0x74
    .org 0xbe784-ORIGIN
L_000be784:
    mov.l P_000be9ac,r5
    .org 0xbe786-ORIGIN
L_000be786:
    mov.l P_000be9b0,r4
    .org 0xbe788-ORIGIN
L_000be788:
    mov.b @(0x5,r5),r0
    .org 0xbe78a-ORIGIN
L_000be78a:
    mov.l P_000be9b4,r2
    .org 0xbe78c-ORIGIN
L_000be78c:
    extu.b r0,r5
    .org 0xbe78e-ORIGIN
L_000be78e:
    jsr @r2
    .org 0xbe790-ORIGIN
L_000be790:
    mov r0,r6
    .org 0xbe792-ORIGIN
L_000be792:
    mov r0,r2
    .org 0xbe794-ORIGIN
L_000be794:
    mov.l P_000be9b8,r13
    .org 0xbe796-ORIGIN
L_000be796:
    mov.w P_000be8ea,r0
    .org 0xbe798-ORIGIN
L_000be798:
    mov.b r2,@(r0,r13)
    .org 0xbe79a-ORIGIN
L_000be79a:
    extu.b r2,r2
    .org 0xbe79c-ORIGIN
L_000be79c:
    mov.w P_000be8ec,r0
    .org 0xbe79e-ORIGIN
L_000be79e:
    shll16 r2
    .org 0xbe7a0-ORIGIN
L_000be7a0:
    mov.l @(r0,r14),r6
    .org 0xbe7a2-ORIGIN
L_000be7a2:
    sub r12,r6
    .org 0xbe7a4-ORIGIN
L_000be7a4:
    add r6,r2
    .org 0xbe7a6-ORIGIN
L_000be7a6:
    cmp/pz r2
    .org 0xbe7a8-ORIGIN
L_000be7a8:
    bt L_000be7ac
    .org 0xbe7aa-ORIGIN
L_000be7aa:
    mov #0x0,r2
    .org 0xbe7ac-ORIGIN
L_000be7ac:
    mov.l P_000be9bc,r7
    .org 0xbe7ae-ORIGIN
L_000be7ae:
    cmp/gt r7,r2
    .org 0xbe7b0-ORIGIN
L_000be7b0:
    bf L_000be7b4
    .org 0xbe7b2-ORIGIN
L_000be7b2:
    mov r7,r2
    .org 0xbe7b4-ORIGIN
L_000be7b4:
    mov.w P_000be8ee,r0
    .org 0xbe7b6-ORIGIN
L_000be7b6:
    mov.l r2,@(r0,r14)
    .org 0xbe7b8-ORIGIN
L_000be7b8:
    mov.b @(0x1,r11),r0
    .org 0xbe7ba-ORIGIN
L_000be7ba:
    tst #0x1,r0
    .org 0xbe7bc-ORIGIN
L_000be7bc:
    bt L_000be7d4
    .org 0xbe7be-ORIGIN
L_000be7be:
    mov.l P_000be9c0,r6
    .org 0xbe7c0-ORIGIN
L_000be7c0:
    mov #-0x8,r0
    .org 0xbe7c2-ORIGIN
L_000be7c2:
    extu.b r0,r0
    .org 0xbe7c4-ORIGIN
L_000be7c4:
    mov.l P_000be9c4,r4
    .org 0xbe7c6-ORIGIN
L_000be7c6:
    mov.b @(r0,r6),r7
    .org 0xbe7c8-ORIGIN
L_000be7c8:
    mov.l P_000be9c8,r5
    .org 0xbe7ca-ORIGIN
L_000be7ca:
    mov.l P_000be9cc,r2
    .org 0xbe7cc-ORIGIN
L_000be7cc:
    jsr @r2
    .org 0xbe7ce-ORIGIN
L_000be7ce:
    extu.b r7,r6
    .org 0xbe7d0-ORIGIN
L_000be7d0:
    bra L_000be7e2
    .org 0xbe7d2-ORIGIN
L_000be7d2:
    nop
    .org 0xbe7d4-ORIGIN
L_000be7d4:
    mov.l P_000be9ac,r5
    .org 0xbe7d6-ORIGIN
L_000be7d6:
    mov.l P_000be9d0,r4
    .org 0xbe7d8-ORIGIN
L_000be7d8:
    mov.b @(0x5,r5),r0
    .org 0xbe7da-ORIGIN
L_000be7da:
    mov.l P_000be9b4,r2
    .org 0xbe7dc-ORIGIN
L_000be7dc:
    extu.b r0,r5
    .org 0xbe7de-ORIGIN
L_000be7de:
    jsr @r2
    .org 0xbe7e0-ORIGIN
L_000be7e0:
    mov r0,r6
    .org 0xbe7e2-ORIGIN
L_000be7e2:
    mov r0,r2
    .org 0xbe7e4-ORIGIN
L_000be7e4:
    mov.w P_000be8f0,r0
    .org 0xbe7e6-ORIGIN
L_000be7e6:
    extu.b r2,r5
    .org 0xbe7e8-ORIGIN
L_000be7e8:
    mov.b r2,@(r0,r13)
    .org 0xbe7ea-ORIGIN
L_000be7ea:
    shll16 r5
    .org 0xbe7ec-ORIGIN
L_000be7ec:
    mov.w P_000be8f2,r0
    .org 0xbe7ee-ORIGIN
L_000be7ee:
    mov.l @(r0,r14),r6
    .org 0xbe7f0-ORIGIN
L_000be7f0:
    sub r12,r6
    .org 0xbe7f2-ORIGIN
L_000be7f2:
    add r6,r5
    .org 0xbe7f4-ORIGIN
L_000be7f4:
    cmp/pz r5
    .org 0xbe7f6-ORIGIN
L_000be7f6:
    bt L_000be7fa
    .org 0xbe7f8-ORIGIN
L_000be7f8:
    mov #0x0,r5
    .org 0xbe7fa-ORIGIN
L_000be7fa:
    mov.l P_000be9bc,r7
    .org 0xbe7fc-ORIGIN
L_000be7fc:
    cmp/gt r7,r5
    .org 0xbe7fe-ORIGIN
L_000be7fe:
    bt L_000be802
    .org 0xbe800-ORIGIN
L_000be800:
    mov r5,r7
    .org 0xbe802-ORIGIN
L_000be802:
    mov.w P_000be8f4,r0
    .org 0xbe804-ORIGIN
L_000be804:
    mov.l r7,@(r0,r14)
    .org 0xbe806-ORIGIN
L_000be806:
    lds.l @r15+,pr
    .org 0xbe808-ORIGIN
L_000be808:
    mov.l @r15+,r14
    .org 0xbe80a-ORIGIN
L_000be80a:
    mov.l @r15+,r13
    .org 0xbe80c-ORIGIN
L_000be80c:
    mov.l @r15+,r12
    .org 0xbe80e-ORIGIN
L_000be80e:
    mov.l @r15+,r11
    .org 0xbe810-ORIGIN
L_000be810:
    rts
    .org 0xbe812-ORIGIN
L_000be812:
    mov.l @r15+,r10
    .org 0xbe814-ORIGIN
L_000be814:
    mov.l r13,@-r15
    .org 0xbe816-ORIGIN
L_000be816:
    sts.l pr,@-r15
    .org 0xbe818-ORIGIN
L_000be818:
    sts.l macl,@-r15
    .org 0xbe81a-ORIGIN
L_000be81a:
    stc.l gbr,@-r15
    .org 0xbe81c-ORIGIN
L_000be81c:
    mov.l P_000be9d4,r0
    .org 0xbe81e-ORIGIN
L_000be81e:
    ldc r0,gbr
    .org 0xbe820-ORIGIN
L_000be820:
    add #-0xc,r15
    .org 0xbe822-ORIGIN
L_000be822:
    mov.l P_000be9d8,r2
    .org 0xbe824-ORIGIN
L_000be824:
    mov #0x2a,r0
    .org 0xbe826-ORIGIN
L_000be826:
    extu.b r4,r13
    .org 0xbe828-ORIGIN
L_000be828:
    mov.b @(r0,r2),r6
    .org 0xbe82a-ORIGIN
L_000be82a:
    mov r13,r2
    .org 0xbe82c-ORIGIN
L_000be82c:
    add #0x1,r2
    .org 0xbe82e-ORIGIN
L_000be82e:
    extu.b r6,r6
    .org 0xbe830-ORIGIN
L_000be830:
    tst r2,r6
    .org 0xbe832-ORIGIN
L_000be832:
    bt L_000be842
    .org 0xbe834-ORIGIN
L_000be834:
    mov #-0x7c,r6
    .org 0xbe836-ORIGIN
L_000be836:
    mov r13,r0
    .org 0xbe838-ORIGIN
L_000be838:
    stc gbr,r2
    .org 0xbe83a-ORIGIN
L_000be83a:
    extu.b r6,r6
    .org 0xbe83c-ORIGIN
L_000be83c:
    add r6,r2
    .org 0xbe83e-ORIGIN
L_000be83e:
    bra L_000be8dc
    .org 0xbe840-ORIGIN
L_000be840:
    mov #-0x1,r6
    .org 0xbe842-ORIGIN
L_000be842:
    mov.b @(0xaf,gbr),r0
    .org 0xbe844-ORIGIN
L_000be844:
    tst #0x40,r0
    .org 0xbe846-ORIGIN
L_000be846:
    bf L_000be866
    .org 0xbe848-ORIGIN
L_000be848:
    mov.b @(0xcf,gbr),r0
    .org 0xbe84a-ORIGIN
L_000be84a:
    tst #0x2,r0
    .org 0xbe84c-ORIGIN
L_000be84c:
    bt L_000be858
    .org 0xbe84e-ORIGIN
L_000be84e:
    mov.l P_000be9dc,r6
    .org 0xbe850-ORIGIN
L_000be850:
    mov #0x51,r0
    .org 0xbe852-ORIGIN
L_000be852:
    mov.b @(r0,r6),r0
    .org 0xbe854-ORIGIN
L_000be854:
    tst #0x1,r0
    .org 0xbe856-ORIGIN
L_000be856:
    bf L_000be866
    .org 0xbe858-ORIGIN
L_000be858:
    mov #-0x7c,r6
    .org 0xbe85a-ORIGIN
L_000be85a:
    mov r13,r0
    .org 0xbe85c-ORIGIN
L_000be85c:
    stc gbr,r2
    .org 0xbe85e-ORIGIN
L_000be85e:
    extu.b r6,r6
    .org 0xbe860-ORIGIN
L_000be860:
    add r6,r2
    .org 0xbe862-ORIGIN
L_000be862:
    bra L_000be8dc
    .org 0xbe864-ORIGIN
L_000be864:
    mov #0x0,r6
    .org 0xbe866-ORIGIN
L_000be866:
    mov.b @(0xeb,gbr),r0
    .org 0xbe868-ORIGIN
L_000be868:
    tst #0x1,r0
    .org 0xbe86a-ORIGIN
L_000be86a:
    bt L_000be876
    .org 0xbe86c-ORIGIN
L_000be86c:
    mov.l P_000be9b8,r2
    .org 0xbe86e-ORIGIN
L_000be86e:
    mov.w P_000be8f6,r0
    .org 0xbe870-ORIGIN
L_000be870:
    mov.b @(r0,r2),r6
    .org 0xbe872-ORIGIN
L_000be872:
    bra L_000be8c8
    .org 0xbe874-ORIGIN
L_000be874:
    extu.b r6,r6
    .org 0xbe876-ORIGIN
L_000be876:
    mov.l P_000be9b8,r6
    .org 0xbe878-ORIGIN
L_000be878:
    mov r13,r0
    .org 0xbe87a-ORIGIN
L_000be87a:
    mov.w P_000be8ee,r2
    .org 0xbe87c-ORIGIN
L_000be87c:
    shll2 r0
    .org 0xbe87e-ORIGIN
L_000be87e:
    mov #-0x6a,r7
    .org 0xbe880-ORIGIN
L_000be880:
    mov.l P_000be9e0,r3
    .org 0xbe882-ORIGIN
L_000be882:
    add r2,r6
    .org 0xbe884-ORIGIN
L_000be884:
    mov.l P_000be9e4,r5
    .org 0xbe886-ORIGIN
L_000be886:
    mov.l @(r0,r6),r4
    .org 0xbe888-ORIGIN
L_000be888:
    extu.b r7,r7
    .org 0xbe88a-ORIGIN
L_000be88a:
    mov #0x74,r0
    .org 0xbe88c-ORIGIN
L_000be88c:
    mov.l r7,@(0x4,r15)
    .org 0xbe88e-ORIGIN
L_000be88e:
    mov r4,r2
    .org 0xbe890-ORIGIN
L_000be890:
    shlr16 r2
    .org 0xbe892-ORIGIN
L_000be892:
    mul.l r2,r7
    .org 0xbe894-ORIGIN
L_000be894:
    mov.b @(r0,r3),r2
    .org 0xbe896-ORIGIN
L_000be896:
    mov.l r4,@r15
    .org 0xbe898-ORIGIN
L_000be898:
    sts macl,r1
    .org 0xbe89a-ORIGIN
L_000be89a:
    extu.b r2,r6
    .org 0xbe89c-ORIGIN
L_000be89c:
    jsr @r5
    .org 0xbe89e-ORIGIN
L_000be89e:
    mov r6,r0
    .org 0xbe8a0-ORIGIN
L_000be8a0:
    mov.l @r15,r2
    .org 0xbe8a2-ORIGIN
L_000be8a2:
    mov.l @(0x4,r15),r7
    .org 0xbe8a4-ORIGIN
L_000be8a4:
    shlr8 r2
    .org 0xbe8a6-ORIGIN
L_000be8a6:
    mov.l P_000be9e0,r3
    .org 0xbe8a8-ORIGIN
L_000be8a8:
    extu.b r2,r2
    .org 0xbe8aa-ORIGIN
L_000be8aa:
    mov.l r0,@(0x8,r15)
    .org 0xbe8ac-ORIGIN
L_000be8ac:
    mul.l r2,r7
    .org 0xbe8ae-ORIGIN
L_000be8ae:
    mov #0x74,r0
    .org 0xbe8b0-ORIGIN
L_000be8b0:
    mov.l P_000be9e4,r5
    .org 0xbe8b2-ORIGIN
L_000be8b2:
    mov.b @(r0,r3),r6
    .org 0xbe8b4-ORIGIN
L_000be8b4:
    sts macl,r1
    .org 0xbe8b6-ORIGIN
L_000be8b6:
    extu.b r6,r4
    .org 0xbe8b8-ORIGIN
L_000be8b8:
    jsr @r5
    .org 0xbe8ba-ORIGIN
L_000be8ba:
    mov r4,r0
    .org 0xbe8bc-ORIGIN
L_000be8bc:
    mov #-0x80,r6
    .org 0xbe8be-ORIGIN
L_000be8be:
    extu.b r6,r6
    .org 0xbe8c0-ORIGIN
L_000be8c0:
    add r6,r0
    .org 0xbe8c2-ORIGIN
L_000be8c2:
    mov.l @(0x8,r15),r6
    .org 0xbe8c4-ORIGIN
L_000be8c4:
    shlr8 r0
    .org 0xbe8c6-ORIGIN
L_000be8c6:
    add r0,r6
    .org 0xbe8c8-ORIGIN
L_000be8c8:
    mov #-0x1,r2
    .org 0xbe8ca-ORIGIN
L_000be8ca:
    extu.b r2,r2
    .org 0xbe8cc-ORIGIN
L_000be8cc:
    cmp/gt r2,r6
    .org 0xbe8ce-ORIGIN
L_000be8ce:
    bf L_000be8d2
    .org 0xbe8d0-ORIGIN
L_000be8d0:
    mov r2,r6
    .org 0xbe8d2-ORIGIN
L_000be8d2:
    mov #-0x7c,r5
    .org 0xbe8d4-ORIGIN
L_000be8d4:
    mov r13,r0
    .org 0xbe8d6-ORIGIN
L_000be8d6:
    stc gbr,r2
    .org 0xbe8d8-ORIGIN
L_000be8d8:
    extu.b r5,r5
    .org 0xbe8da-ORIGIN
L_000be8da:
    add r5,r2
    .org 0xbe8dc-ORIGIN
L_000be8dc:
    mov.b r6,@(r0,r2)
    .org 0xbe8de-ORIGIN
L_000be8de:
    add #0xc,r15
    .org 0xbe8e0-ORIGIN
L_000be8e0:
    ldc.l @r15+,gbr
    .org 0xbe8e2-ORIGIN
L_000be8e2:
    lds.l @r15+,macl
    .org 0xbe8e4-ORIGIN
L_000be8e4:
    lds.l @r15+,pr
    .org 0xbe8e6-ORIGIN
L_000be8e6:
    rts
    .org 0xbe8e8-ORIGIN
L_000be8e8:
    mov.l @r15+,r13
    .org 0xbe8ea-ORIGIN
P_000be8ea:
    .byte 0x07
    .org 0xbe8eb-ORIGIN
P_000be8eb:
    .byte 0xef
    .org 0xbe8ec-ORIGIN
P_000be8ec:
    .byte 0x04
    .org 0xbe8ed-ORIGIN
P_000be8ed:
    .byte 0x5c
    .org 0xbe8ee-ORIGIN
P_000be8ee:
    .byte 0x08
    .org 0xbe8ef-ORIGIN
P_000be8ef:
    .byte 0x10
    .org 0xbe8f0-ORIGIN
P_000be8f0:
    .byte 0x07
    .org 0xbe8f1-ORIGIN
P_000be8f1:
    .byte 0xf0
    .org 0xbe8f2-ORIGIN
P_000be8f2:
    .byte 0x04
    .org 0xbe8f3-ORIGIN
P_000be8f3:
    .byte 0x60
    .org 0xbe8f4-ORIGIN
P_000be8f4:
    .byte 0x08
    .org 0xbe8f5-ORIGIN
P_000be8f5:
    .byte 0x14
    .org 0xbe8f6-ORIGIN
P_000be8f6:
    .byte 0x07
    .org 0xbe8f7-ORIGIN
P_000be8f7:
    .byte 0xcd
    .org 0xbe9ac-ORIGIN
P_000be9ac:
    .byte 0xff
    .org 0xbe9ad-ORIGIN
P_000be9ad:
    .byte 0xff
    .org 0xbe9ae-ORIGIN
P_000be9ae:
    .byte 0x10
    .org 0xbe9af-ORIGIN
P_000be9af:
    .byte 0x6a
    .org 0xbe9b0-ORIGIN
P_000be9b0:
    .byte 0x00
    .org 0xbe9b1-ORIGIN
P_000be9b1:
    .byte 0x01
    .org 0xbe9b2-ORIGIN
P_000be9b2:
    .byte 0x2e
    .org 0xbe9b3-ORIGIN
P_000be9b3:
    .byte 0x72
    .org 0xbe9b4-ORIGIN
P_000be9b4:
    .byte 0x00
    .org 0xbe9b5-ORIGIN
P_000be9b5:
    .byte 0x02
    .org 0xbe9b6-ORIGIN
P_000be9b6:
    .byte 0x63
    .org 0xbe9b7-ORIGIN
P_000be9b7:
    .byte 0x70
    .org 0xbe9b8-ORIGIN
P_000be9b8:
    .byte 0xff
    .org 0xbe9b9-ORIGIN
P_000be9b9:
    .byte 0xff
    .org 0xbe9ba-ORIGIN
P_000be9ba:
    .byte 0x12
    .org 0xbe9bb-ORIGIN
P_000be9bb:
    .byte 0x8c
    .org 0xbe9bc-ORIGIN
P_000be9bc:
    .byte 0x00
    .org 0xbe9bd-ORIGIN
P_000be9bd:
    .byte 0xff
    .org 0xbe9be-ORIGIN
P_000be9be:
    .byte 0xff
    .org 0xbe9bf-ORIGIN
P_000be9bf:
    .byte 0xff
    .org 0xbe9c0-ORIGIN
P_000be9c0:
    .byte 0xff
    .org 0xbe9c1-ORIGIN
P_000be9c1:
    .byte 0xff
    .org 0xbe9c2-ORIGIN
P_000be9c2:
    .byte 0x26
    .org 0xbe9c3-ORIGIN
P_000be9c3:
    .byte 0x7a
    .org 0xbe9c4-ORIGIN
P_000be9c4:
    .byte 0x00
    .org 0xbe9c5-ORIGIN
P_000be9c5:
    .byte 0x01
    .org 0xbe9c6-ORIGIN
P_000be9c6:
    .byte 0x2e
    .org 0xbe9c7-ORIGIN
P_000be9c7:
    .byte 0x8a
    .org 0xbe9c8-ORIGIN
P_000be9c8:
    .byte 0x00
    .org 0xbe9c9-ORIGIN
P_000be9c9:
    .byte 0x01
    .org 0xbe9ca-ORIGIN
P_000be9ca:
    .byte 0x1b
    .org 0xbe9cb-ORIGIN
P_000be9cb:
    .byte 0xdb
    .org 0xbe9cc-ORIGIN
P_000be9cc:
    .byte 0x00
    .org 0xbe9cd-ORIGIN
P_000be9cd:
    .byte 0x02
    .org 0xbe9ce-ORIGIN
P_000be9ce:
    .byte 0x64
    .org 0xbe9cf-ORIGIN
P_000be9cf:
    .byte 0x74
    .org 0xbe9d0-ORIGIN
P_000be9d0:
    .byte 0x00
    .org 0xbe9d1-ORIGIN
P_000be9d1:
    .byte 0x01
    .org 0xbe9d2-ORIGIN
P_000be9d2:
    .byte 0x2e
    .org 0xbe9d3-ORIGIN
P_000be9d3:
    .byte 0x7a
    .org 0xbe9d4-ORIGIN
P_000be9d4:
    .byte 0xff
    .org 0xbe9d5-ORIGIN
P_000be9d5:
    .byte 0xff
    .org 0xbe9d6-ORIGIN
P_000be9d6:
    .byte 0x23
    .org 0xbe9d7-ORIGIN
P_000be9d7:
    .byte 0xbc
    .org 0xbe9d8-ORIGIN
P_000be9d8:
    .byte 0xff
    .org 0xbe9d9-ORIGIN
P_000be9d9:
    .byte 0xff
    .org 0xbe9da-ORIGIN
P_000be9da:
    .byte 0x28
    .org 0xbe9db-ORIGIN
P_000be9db:
    .byte 0x98
    .org 0xbe9dc-ORIGIN
P_000be9dc:
    .byte 0xff
    .org 0xbe9dd-ORIGIN
P_000be9dd:
    .byte 0xff
    .org 0xbe9de-ORIGIN
P_000be9de:
    .byte 0x41
    .org 0xbe9df-ORIGIN
P_000be9df:
    .byte 0xa9
    .org 0xbe9e0-ORIGIN
P_000be9e0:
    .byte 0xff
    .org 0xbe9e1-ORIGIN
P_000be9e1:
    .byte 0xff
    .org 0xbe9e2-ORIGIN
P_000be9e2:
    .byte 0x10
    .org 0xbe9e3-ORIGIN
P_000be9e3:
    .byte 0x94
    .org 0xbe9e4-ORIGIN
P_000be9e4:
    .byte 0x00
    .org 0xbe9e5-ORIGIN
P_000be9e5:
    .byte 0x02
    .org 0xbe9e6-ORIGIN
P_000be9e6:
    .byte 0x1c
    .org 0xbe9e7-ORIGIN
P_000be9e7:
    .byte 0xe0
