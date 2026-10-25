! Complete natural23F1 ratio producer and exact real unsigned/signed dividers and signed shift helper.
    .text
    .balign 4
    .set ORIGIN,0x884c
    .org 0x884d-ORIGIN
P_0000884d:
    .byte 0x80
    .org 0x8b6c-ORIGIN
P_00008b6c:
    .byte 0x0e
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
    .org 0x22508-ORIGIN
L_00022508:
    mov.l r1,@-r15
    .org 0x2250a-ORIGIN
L_0002250a:
    shlr8 r0
    .org 0x2250c-ORIGIN
L_0002250c:
    swap.w r0,r0
    .org 0x2250e-ORIGIN
L_0002250e:
    exts.b r0,r1
    .org 0x22510-ORIGIN
L_00022510:
    xtrct r1,r0
    .org 0x22512-ORIGIN
L_00022512:
    shar r0
    .org 0x22514-ORIGIN
L_00022514:
    shar r0
    .org 0x22516-ORIGIN
L_00022516:
    rts
    .org 0x22518-ORIGIN
L_00022518:
    mov.l @r15+,r1
    .org 0x4ae6c-ORIGIN
L_0004ae6c:
    sts.l pr,@-r15
    .org 0x4ae6e-ORIGIN
L_0004ae6e:
    sts.l macl,@-r15
    .org 0x4ae70-ORIGIN
L_0004ae70:
    mov.l P_0004afc4,r7
    .org 0x4ae72-ORIGIN
L_0004ae72:
    mov.w P_0004aec0,r0
    .org 0x4ae74-ORIGIN
L_0004ae74:
    mov.b @(r0,r7),r2
    .org 0x4ae76-ORIGIN
L_0004ae76:
    mov.w P_0004aebe,r0
    .org 0x4ae78-ORIGIN
L_0004ae78:
    extu.b r2,r5
    .org 0x4ae7a-ORIGIN
L_0004ae7a:
    mov.w @(r0,r7),r2
    .org 0x4ae7c-ORIGIN
L_0004ae7c:
    extu.w r2,r6
    .org 0x4ae7e-ORIGIN
L_0004ae7e:
    mul.l r5,r6
    .org 0x4ae80-ORIGIN
L_0004ae80:
    sts macl,r2
    .org 0x4ae82-ORIGIN
L_0004ae82:
    tst r2,r2
    .org 0x4ae84-ORIGIN
L_0004ae84:
    bt L_0004aec4
    .org 0x4ae86-ORIGIN
L_0004ae86:
    mov.l P_0004afc8,r6
    .org 0x4ae88-ORIGIN
L_0004ae88:
    mov.w P_0004aec2,r0
    .org 0x4ae8a-ORIGIN
L_0004ae8a:
    mov.b @r6,r4
    .org 0x4ae8c-ORIGIN
L_0004ae8c:
    extu.b r4,r4
    .org 0x4ae8e-ORIGIN
L_0004ae8e:
    mov r4,r6
    .org 0x4ae90-ORIGIN
L_0004ae90:
    shll2 r6
    .org 0x4ae92-ORIGIN
L_0004ae92:
    shll2 r6
    .org 0x4ae94-ORIGIN
L_0004ae94:
    sub r4,r6
    .org 0x4ae96-ORIGIN
L_0004ae96:
    mov.w @(r0,r7),r4
    .org 0x4ae98-ORIGIN
L_0004ae98:
    shll2 r6
    .org 0x4ae9a-ORIGIN
L_0004ae9a:
    mov r2,r0
    .org 0x4ae9c-ORIGIN
L_0004ae9c:
    shll r6
    .org 0x4ae9e-ORIGIN
L_0004ae9e:
    extu.w r4,r5
    .org 0x4aea0-ORIGIN
L_0004aea0:
    mul.l r6,r5
    .org 0x4aea2-ORIGIN
L_0004aea2:
    mov.l P_0004afac,r5
    .org 0x4aea4-ORIGIN
L_0004aea4:
    jsr @r5
    .org 0x4aea6-ORIGIN
L_0004aea6:
    sts macl,r1
    .org 0x4aea8-ORIGIN
L_0004aea8:
    bra L_0004aec8
    .org 0x4aeaa-ORIGIN
L_0004aeaa:
    mov r0,r5
    .org 0x4aebe-ORIGIN
P_0004aebe:
    .byte 0x02
    .org 0x4aebf-ORIGIN
P_0004aebf:
    .byte 0x50
    .org 0x4aec0-ORIGIN
P_0004aec0:
    .byte 0x05
    .org 0x4aec1-ORIGIN
P_0004aec1:
    .byte 0x2c
    .org 0x4aec2-ORIGIN
P_0004aec2:
    .byte 0x03
    .org 0x4aec3-ORIGIN
P_0004aec3:
    .byte 0xa4
    .org 0x4aec4-ORIGIN
L_0004aec4:
    mov #-0x1,r2
    .org 0x4aec6-ORIGIN
L_0004aec6:
    extu.w r2,r5
    .org 0x4aec8-ORIGIN
L_0004aec8:
    mov.l P_0004afcc,r2
    .org 0x4aeca-ORIGIN
L_0004aeca:
    mov.b @r2,r6
    .org 0x4aecc-ORIGIN
L_0004aecc:
    extu.b r6,r6
    .org 0x4aece-ORIGIN
L_0004aece:
    mov r6,r2
    .org 0x4aed0-ORIGIN
L_0004aed0:
    shll2 r2
    .org 0x4aed2-ORIGIN
L_0004aed2:
    add r6,r2
    .org 0x4aed4-ORIGIN
L_0004aed4:
    shlr r2
    .org 0x4aed6-ORIGIN
L_0004aed6:
    mov #0x1,r6
    .org 0x4aed8-ORIGIN
L_0004aed8:
    add r5,r2
    .org 0x4aeda-ORIGIN
L_0004aeda:
    shll16 r6
    .org 0x4aedc-ORIGIN
L_0004aedc:
    cmp/hs r6,r2
    .org 0x4aede-ORIGIN
L_0004aede:
    mov.l P_0004af94,r6
    .org 0x4aee0-ORIGIN
L_0004aee0:
    bt/s L_0004af00
    .org 0x4aee2-ORIGIN
L_0004aee2:
    mov #0x20,r0
    .org 0x4aee4-ORIGIN
L_0004aee4:
    mov.w @(r0,r6),r5
    .org 0x4aee6-ORIGIN
L_0004aee6:
    extu.w r5,r6
    .org 0x4aee8-ORIGIN
L_0004aee8:
    mul.l r2,r6
    .org 0x4aeea-ORIGIN
L_0004aeea:
    sts macl,r1
    .org 0x4aeec-ORIGIN
L_0004aeec:
    shlr8 r1
    .org 0x4aeee-ORIGIN
L_0004aeee:
    shlr2 r1
    .org 0x4aef0-ORIGIN
L_0004aef0:
    mov r1,r6
    .org 0x4aef2-ORIGIN
L_0004aef2:
    shll r1
    .org 0x4aef4-ORIGIN
L_0004aef4:
    add r6,r1
    .org 0x4aef6-ORIGIN
L_0004aef6:
    mov.l P_0004afac,r6
    .org 0x4aef8-ORIGIN
L_0004aef8:
    jsr @r6
    .org 0x4aefa-ORIGIN
L_0004aefa:
    mov #0x5,r0
    .org 0x4aefc-ORIGIN
L_0004aefc:
    bra L_0004af1a
    .org 0x4aefe-ORIGIN
L_0004aefe:
    nop
    .org 0x4af00-ORIGIN
L_0004af00:
    mov.w @(r0,r6),r2
    .org 0x4af02-ORIGIN
L_0004af02:
    mov.l P_0004afd0,r6
    .org 0x4af04-ORIGIN
L_0004af04:
    extu.w r2,r5
    .org 0x4af06-ORIGIN
L_0004af06:
    mov r5,r0
    .org 0x4af08-ORIGIN
L_0004af08:
    shll16 r0
    .org 0x4af0a-ORIGIN
L_0004af0a:
    jsr @r6
    .org 0x4af0c-ORIGIN
L_0004af0c:
    sub r5,r0
    .org 0x4af0e-ORIGIN
L_0004af0e:
    mov r0,r1
    .org 0x4af10-ORIGIN
L_0004af10:
    shll r1
    .org 0x4af12-ORIGIN
L_0004af12:
    mov.l P_0004afb8,r6
    .org 0x4af14-ORIGIN
L_0004af14:
    add r0,r1
    .org 0x4af16-ORIGIN
L_0004af16:
    jsr @r6
    .org 0x4af18-ORIGIN
L_0004af18:
    mov #0x5,r0
    .org 0x4af1a-ORIGIN
L_0004af1a:
    mov #-0x73,r6
    .org 0x4af1c-ORIGIN
L_0004af1c:
    extu.b r6,r6
    .org 0x4af1e-ORIGIN
L_0004af1e:
    cmp/hi r6,r0
    .org 0x4af20-ORIGIN
L_0004af20:
    bt/s L_0004af2a
    .org 0x4af22-ORIGIN
L_0004af22:
    mov r0,r2
    .org 0x4af24-ORIGIN
L_0004af24:
    add #-0xe,r2
    .org 0x4af26-ORIGIN
L_0004af26:
    bra L_0004af2c
    .org 0x4af28-ORIGIN
L_0004af28:
    mov r2,r6
    .org 0x4af2a-ORIGIN
L_0004af2a:
    mov #0x7f,r6
    .org 0x4af2c-ORIGIN
L_0004af2c:
    mov.l P_0004afd4,r2
    .org 0x4af2e-ORIGIN
L_0004af2e:
    mov #0x35,r0
    .org 0x4af30-ORIGIN
L_0004af30:
    lds.l @r15+,macl
    .org 0x4af32-ORIGIN
L_0004af32:
    lds.l @r15+,pr
    .org 0x4af34-ORIGIN
L_0004af34:
    rts
    .org 0x4af36-ORIGIN
L_0004af36:
    mov.b r6,@(r0,r2)
    .org 0x4af94-ORIGIN
P_0004af94:
    .byte 0xff
    .org 0x4af95-ORIGIN
P_0004af95:
    .byte 0xff
    .org 0x4af96-ORIGIN
P_0004af96:
    .byte 0x11
    .org 0x4af97-ORIGIN
P_0004af97:
    .byte 0x9c
    .org 0x4afac-ORIGIN
P_0004afac:
    .byte 0x00
    .org 0x4afad-ORIGIN
P_0004afad:
    .byte 0x02
    .org 0x4afae-ORIGIN
P_0004afae:
    .byte 0x1c
    .org 0x4afaf-ORIGIN
P_0004afaf:
    .byte 0xe0
    .org 0x4afb8-ORIGIN
P_0004afb8:
    .byte 0x00
    .org 0x4afb9-ORIGIN
P_0004afb9:
    .byte 0x02
    .org 0x4afba-ORIGIN
P_0004afba:
    .byte 0x1b
    .org 0x4afbb-ORIGIN
P_0004afbb:
    .byte 0xbc
    .org 0x4afc4-ORIGIN
P_0004afc4:
    .byte 0xff
    .org 0x4afc5-ORIGIN
P_0004afc5:
    .byte 0xff
    .org 0x4afc6-ORIGIN
P_0004afc6:
    .byte 0x12
    .org 0x4afc7-ORIGIN
P_0004afc7:
    .byte 0x8c
    .org 0x4afc8-ORIGIN
P_0004afc8:
    .byte 0x00
    .org 0x4afc9-ORIGIN
P_0004afc9:
    .byte 0x00
    .org 0x4afca-ORIGIN
P_0004afca:
    .byte 0x88
    .org 0x4afcb-ORIGIN
P_0004afcb:
    .byte 0x4d
    .org 0x4afcc-ORIGIN
P_0004afcc:
    .byte 0x00
    .org 0x4afcd-ORIGIN
P_0004afcd:
    .byte 0x00
    .org 0x4afce-ORIGIN
P_0004afce:
    .byte 0x8b
    .org 0x4afcf-ORIGIN
P_0004afcf:
    .byte 0x6c
    .org 0x4afd0-ORIGIN
P_0004afd0:
    .byte 0x00
    .org 0x4afd1-ORIGIN
P_0004afd1:
    .byte 0x02
    .org 0x4afd2-ORIGIN
P_0004afd2:
    .byte 0x25
    .org 0x4afd3-ORIGIN
P_0004afd3:
    .byte 0x08
    .org 0x4afd4-ORIGIN
P_0004afd4:
    .byte 0xff
    .org 0x4afd5-ORIGIN
P_0004afd5:
    .byte 0xff
    .org 0x4afd6-ORIGIN
P_0004afd6:
    .byte 0x23
    .org 0x4afd7-ORIGIN
P_0004afd7:
    .byte 0xbc
