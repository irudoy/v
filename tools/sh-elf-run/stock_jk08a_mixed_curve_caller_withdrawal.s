! Exact full mixed curve and scalar callers, physical inputs and complete real helpers.
    .text
    .balign 4
    .set ORIGIN,0x87ec
    .org 0x87ee-ORIGIN
P_000087ee:
    .byte 0x00
    .org 0x9012-ORIGIN
P_00009012:
    .byte 0x1c
    .org 0x9013-ORIGIN
P_00009013:
    .byte 0xb6
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
    .org 0x224f8-ORIGIN
L_000224f8:
    shar r0
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
    .org 0x26270-ORIGIN
L_00026270:
    sts.l pr,@-r15
    .org 0x26272-ORIGIN
L_00026272:
    mov.l r4,@-r15
    .org 0x26274-ORIGIN
L_00026274:
    extu.w r7,r7
    .org 0x26276-ORIGIN
L_00026276:
    mov r5,r0
    .org 0x26278-ORIGIN
L_00026278:
    mov r7,r5
    .org 0x2627a-ORIGIN
L_0002627a:
    mov.l P_000262a4,r7
    .org 0x2627c-ORIGIN
L_0002627c:
    jsr @r7
    .org 0x2627e-ORIGIN
L_0002627e:
    mov #0xe,r4
    .org 0x26280-ORIGIN
L_00026280:
    mov.l r4,@-r15
    .org 0x26282-ORIGIN
L_00026282:
    mov.l r5,@-r15
    .org 0x26284-ORIGIN
L_00026284:
    mov r6,r0
    .org 0x26286-ORIGIN
L_00026286:
    mov.l @(0x10,r15),r5
    .org 0x26288-ORIGIN
L_00026288:
    extu.w r5,r5
    .org 0x2628a-ORIGIN
L_0002628a:
    jsr @r7
    .org 0x2628c-ORIGIN
L_0002628c:
    mov #0xe,r4
    .org 0x2628e-ORIGIN
L_0002628e:
    mov.l @r15+,r1
    .org 0x26290-ORIGIN
L_00026290:
    mov.l @r15+,r0
    .org 0x26292-ORIGIN
L_00026292:
    mov r4,r2
    .org 0x26294-ORIGIN
L_00026294:
    mov r5,r3
    .org 0x26296-ORIGIN
L_00026296:
    mov.l @r15+,r4
    .org 0x26298-ORIGIN
L_00026298:
    lds.l @r15+,pr
    .org 0x2629a-ORIGIN
L_0002629a:
    mov.l P_000262a0,r7
    .org 0x2629c-ORIGIN
L_0002629c:
    jmp @r7
    .org 0x2629e-ORIGIN
L_0002629e:
    mov #0x8,r5
    .org 0x262a0-ORIGIN
P_000262a0:
    .byte 0x00
    .org 0x262a1-ORIGIN
P_000262a1:
    .byte 0x02
    .org 0x262a2-ORIGIN
P_000262a2:
    .byte 0x68
    .org 0x262a3-ORIGIN
P_000262a3:
    .byte 0x48
    .org 0x262a4-ORIGIN
P_000262a4:
    .byte 0x00
    .org 0x262a5-ORIGIN
P_000262a5:
    .byte 0x02
    .org 0x262a6-ORIGIN
P_000262a6:
    .byte 0x69
    .org 0x262a7-ORIGIN
P_000262a7:
    .byte 0x84
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
    mov.l P_000268a0,r7
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
P_000268a0:
    .byte 0x00
    .org 0x268a1-ORIGIN
P_000268a1:
    .byte 0x02
    .org 0x268a2-ORIGIN
P_000268a2:
    .byte 0x67
    .org 0x268a3-ORIGIN
P_000268a3:
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
    .org 0x3b498-ORIGIN
L_0003b498:
    mov.l r14,@-r15
    .org 0x3b49a-ORIGIN
L_0003b49a:
    sts.l pr,@-r15
    .org 0x3b49c-ORIGIN
L_0003b49c:
    sts.l macl,@-r15
    .org 0x3b49e-ORIGIN
L_0003b49e:
    stc.l gbr,@-r15
    .org 0x3b4a0-ORIGIN
L_0003b4a0:
    mov.l P_0003b670,r0
    .org 0x3b4a2-ORIGIN
L_0003b4a2:
    ldc r0,gbr
    .org 0x3b4a4-ORIGIN
L_0003b4a4:
    add #-0x4,r15
    .org 0x3b4a6-ORIGIN
L_0003b4a6:
    mov.b @(0x5c,gbr),r0
    .org 0x3b4a8-ORIGIN
L_0003b4a8:
    mov #-0x1,r7
    .org 0x3b4aa-ORIGIN
L_0003b4aa:
    mov.l P_0003b664,r6
    .org 0x3b4ac-ORIGIN
L_0003b4ac:
    extu.w r7,r7
    .org 0x3b4ae-ORIGIN
L_0003b4ae:
    mov.b r0,@r15
    .org 0x3b4b0-ORIGIN
L_0003b4b0:
    mov.w @r6,r2
    .org 0x3b4b2-ORIGIN
L_0003b4b2:
    mov.w @(0x3a,gbr),r0
    .org 0x3b4b4-ORIGIN
L_0003b4b4:
    extu.w r2,r14
    .org 0x3b4b6-ORIGIN
L_0003b4b6:
    extu.w r0,r5
    .org 0x3b4b8-ORIGIN
L_0003b4b8:
    mul.l r14,r5
    .org 0x3b4ba-ORIGIN
L_0003b4ba:
    sts macl,r4
    .org 0x3b4bc-ORIGIN
L_0003b4bc:
    shlr8 r4
    .org 0x3b4be-ORIGIN
L_0003b4be:
    shlr r4
    .org 0x3b4c0-ORIGIN
L_0003b4c0:
    cmp/hs r7,r4
    .org 0x3b4c2-ORIGIN
L_0003b4c2:
    bf L_0003b4c8
    .org 0x3b4c4-ORIGIN
L_0003b4c4:
    bra L_0003b4d8
    .org 0x3b4c6-ORIGIN
L_0003b4c6:
    mov r7,r4
    .org 0x3b4c8-ORIGIN
L_0003b4c8:
    mov.w @(0xfa,gbr),r0
    .org 0x3b4ca-ORIGIN
L_0003b4ca:
    extu.w r0,r2
    .org 0x3b4cc-ORIGIN
L_0003b4cc:
    mul.l r2,r5
    .org 0x3b4ce-ORIGIN
L_0003b4ce:
    sts macl,r5
    .org 0x3b4d0-ORIGIN
L_0003b4d0:
    shlr8 r5
    .org 0x3b4d2-ORIGIN
L_0003b4d2:
    shlr2 r5
    .org 0x3b4d4-ORIGIN
L_0003b4d4:
    shlr r5
    .org 0x3b4d6-ORIGIN
L_0003b4d6:
    add r5,r4
    .org 0x3b4d8-ORIGIN
L_0003b4d8:
    cmp/hi r7,r4
    .org 0x3b4da-ORIGIN
L_0003b4da:
    bf L_0003b4de
    .org 0x3b4dc-ORIGIN
L_0003b4dc:
    mov r7,r4
    .org 0x3b4de-ORIGIN
L_0003b4de:
    mov.l P_0003b664,r6
    .org 0x3b4e0-ORIGIN
L_0003b4e0:
    extu.w r4,r0
    .org 0x3b4e2-ORIGIN
L_0003b4e2:
    mov.w r0,@(0x2,r6)
    .org 0x3b4e4-ORIGIN
L_0003b4e4:
    mov #0x3c,r6
    .org 0x3b4e6-ORIGIN
L_0003b4e6:
    shll8 r6
    .org 0x3b4e8-ORIGIN
L_0003b4e8:
    cmp/ge r6,r0
    .org 0x3b4ea-ORIGIN
L_0003b4ea:
    bt L_0003b4f4
    .org 0x3b4ec-ORIGIN
L_0003b4ec:
    mov r0,r5
    .org 0x3b4ee-ORIGIN
L_0003b4ee:
    mov.l P_0003b684,r4
    .org 0x3b4f0-ORIGIN
L_0003b4f0:
    bra L_0003b4fe
    .org 0x3b4f2-ORIGIN
L_0003b4f2:
    shll2 r5
    .org 0x3b4f4-ORIGIN
L_0003b4f4:
    mov #0x3c,r2
    .org 0x3b4f6-ORIGIN
L_0003b4f6:
    mov r0,r5
    .org 0x3b4f8-ORIGIN
L_0003b4f8:
    shll8 r2
    .org 0x3b4fa-ORIGIN
L_0003b4fa:
    mov.l P_0003b688,r4
    .org 0x3b4fc-ORIGIN
L_0003b4fc:
    sub r2,r5
    .org 0x3b4fe-ORIGIN
L_0003b4fe:
    mov.l P_0003b68c,r2
    .org 0x3b500-ORIGIN
L_0003b500:
    jsr @r2
    .org 0x3b502-ORIGIN
L_0003b502:
    extu.w r5,r5
    .org 0x3b504-ORIGIN
L_0003b504:
    extu.w r0,r0
    .org 0x3b506-ORIGIN
L_0003b506:
    mov.b @r15,r6
    .org 0x3b508-ORIGIN
L_0003b508:
    shlr8 r0
    .org 0x3b50a-ORIGIN
L_0003b50a:
    mov.b r0,@(0x5c,gbr)
    .org 0x3b50c-ORIGIN
L_0003b50c:
    extu.b r0,r0
    .org 0x3b50e-ORIGIN
L_0003b50e:
    extu.b r6,r6
    .org 0x3b510-ORIGIN
L_0003b510:
    sub r6,r0
    .org 0x3b512-ORIGIN
L_0003b512:
    mov.w r0,@(0x24,gbr)
    .org 0x3b514-ORIGIN
L_0003b514:
    add #0x4,r15
    .org 0x3b516-ORIGIN
L_0003b516:
    ldc.l @r15+,gbr
    .org 0x3b518-ORIGIN
L_0003b518:
    lds.l @r15+,macl
    .org 0x3b51a-ORIGIN
L_0003b51a:
    lds.l @r15+,pr
    .org 0x3b51c-ORIGIN
L_0003b51c:
    rts
    .org 0x3b51e-ORIGIN
L_0003b51e:
    mov.l @r15+,r14
    .org 0x3b664-ORIGIN
P_0003b664:
    .byte 0xff
    .org 0x3b665-ORIGIN
P_0003b665:
    .byte 0xff
    .org 0x3b666-ORIGIN
P_0003b666:
    .byte 0x1e
    .org 0x3b667-ORIGIN
P_0003b667:
    .byte 0x60
    .org 0x3b670-ORIGIN
P_0003b670:
    .byte 0xff
    .org 0x3b671-ORIGIN
P_0003b671:
    .byte 0xff
    .org 0x3b672-ORIGIN
P_0003b672:
    .byte 0x11
    .org 0x3b673-ORIGIN
P_0003b673:
    .byte 0x14
    .org 0x3b684-ORIGIN
P_0003b684:
    .byte 0x00
    .org 0x3b685-ORIGIN
P_0003b685:
    .byte 0x01
    .org 0x3b686-ORIGIN
P_0003b686:
    .byte 0x50
    .org 0x3b687-ORIGIN
P_0003b687:
    .byte 0x42
    .org 0x3b688-ORIGIN
P_0003b688:
    .byte 0x00
    .org 0x3b689-ORIGIN
P_0003b689:
    .byte 0x01
    .org 0x3b68a-ORIGIN
P_0003b68a:
    .byte 0x50
    .org 0x3b68b-ORIGIN
P_0003b68b:
    .byte 0x22
    .org 0x3b68c-ORIGIN
P_0003b68c:
    .byte 0x00
    .org 0x3b68d-ORIGIN
P_0003b68d:
    .byte 0x02
    .org 0x3b68e-ORIGIN
P_0003b68e:
    .byte 0x63
    .org 0x3b68f-ORIGIN
P_0003b68f:
    .byte 0xf4
    .org 0x41db6-ORIGIN
L_00041db6:
    sts.l pr,@-r15
    .org 0x41db8-ORIGIN
L_00041db8:
    stc.l gbr,@-r15
    .org 0x41dba-ORIGIN
L_00041dba:
    mov.l P_00041e74,r0
    .org 0x41dbc-ORIGIN
L_00041dbc:
    ldc r0,gbr
    .org 0x41dbe-ORIGIN
L_00041dbe:
    mov.l P_00041e78,r6
    .org 0x41dc0-ORIGIN
L_00041dc0:
    mov.b @(0x1,r6),r0
    .org 0x41dc2-ORIGIN
L_00041dc2:
    tst #0x40,r0
    .org 0x41dc4-ORIGIN
L_00041dc4:
    bf L_00041dd0
    .org 0x41dc6-ORIGIN
L_00041dc6:
    mov.b @(0x4,r6),r0
    .org 0x41dc8-ORIGIN
L_00041dc8:
    tst #0x4,r0
    .org 0x41dca-ORIGIN
L_00041dca:
    bf L_00041dd0
    .org 0x41dcc-ORIGIN
L_00041dcc:
    bra L_00041e36
    .org 0x41dce-ORIGIN
L_00041dce:
    mov #-0x80,r0
    .org 0x41dd0-ORIGIN
L_00041dd0:
    mov.l P_00041e70,r2
    .org 0x41dd2-ORIGIN
L_00041dd2:
    mov.w P_00041e62,r0
    .org 0x41dd4-ORIGIN
L_00041dd4:
    mov.w @(r0,r2),r6
    .org 0x41dd6-ORIGIN
L_00041dd6:
    mov.w P_00041e64,r0
    .org 0x41dd8-ORIGIN
L_00041dd8:
    extu.w r6,r6
    .org 0x41dda-ORIGIN
L_00041dda:
    mov.b @(r0,r2),r5
    .org 0x41ddc-ORIGIN
L_00041ddc:
    mov.w P_00041e66,r0
    .org 0x41dde-ORIGIN
L_00041dde:
    extu.b r5,r5
    .org 0x41de0-ORIGIN
L_00041de0:
    mov.b @(r0,r2),r7
    .org 0x41de2-ORIGIN
L_00041de2:
    shll2 r5
    .org 0x41de4-ORIGIN
L_00041de4:
    mov.l P_00041e7c,r2
    .org 0x41de6-ORIGIN
L_00041de6:
    add r5,r6
    .org 0x41de8-ORIGIN
L_00041de8:
    mov.w P_00041e68,r0
    .org 0x41dea-ORIGIN
L_00041dea:
    extu.b r7,r7
    .org 0x41dec-ORIGIN
L_00041dec:
    add r7,r6
    .org 0x41dee-ORIGIN
L_00041dee:
    mov.b @(r0,r2),r4
    .org 0x41df0-ORIGIN
L_00041df0:
    mov.w P_00041e60,r0
    .org 0x41df2-ORIGIN
L_00041df2:
    extu.b r4,r4
    .org 0x41df4-ORIGIN
L_00041df4:
    add r4,r6
    .org 0x41df6-ORIGIN
L_00041df6:
    mov.l P_00041e6c,r4
    .org 0x41df8-ORIGIN
L_00041df8:
    tst r6,r6
    .org 0x41dfa-ORIGIN
L_00041dfa:
    bt/s L_00041e2c
    .org 0x41dfc-ORIGIN
L_00041dfc:
    mov r6,r5
    .org 0x41dfe-ORIGIN
L_00041dfe:
    mov.w @(r0,r4),r6
    .org 0x41e00-ORIGIN
L_00041e00:
    mov r5,r0
    .org 0x41e02-ORIGIN
L_00041e02:
    mov.l P_00041e80,r2
    .org 0x41e04-ORIGIN
L_00041e04:
    shll2 r6
    .org 0x41e06-ORIGIN
L_00041e06:
    shll2 r6
    .org 0x41e08-ORIGIN
L_00041e08:
    shll2 r6
    .org 0x41e0a-ORIGIN
L_00041e0a:
    shll r6
    .org 0x41e0c-ORIGIN
L_00041e0c:
    jsr @r2
    .org 0x41e0e-ORIGIN
L_00041e0e:
    mov r6,r1
    .org 0x41e10-ORIGIN
L_00041e10:
    mov #-0x80,r5
    .org 0x41e12-ORIGIN
L_00041e12:
    extu.b r5,r5
    .org 0x41e14-ORIGIN
L_00041e14:
    add r5,r0
    .org 0x41e16-ORIGIN
L_00041e16:
    add #0x7f,r5
    .org 0x41e18-ORIGIN
L_00041e18:
    cmp/gt r5,r0
    .org 0x41e1a-ORIGIN
L_00041e1a:
    bf/s L_00041e22
    .org 0x41e1c-ORIGIN
L_00041e1c:
    mov r0,r2
    .org 0x41e1e-ORIGIN
L_00041e1e:
    mov #-0x1,r6
    .org 0x41e20-ORIGIN
L_00041e20:
    extu.b r6,r2
    .org 0x41e22-ORIGIN
L_00041e22:
    cmp/pz r2
    .org 0x41e24-ORIGIN
L_00041e24:
    bt L_00041e28
    .org 0x41e26-ORIGIN
L_00041e26:
    mov #0x0,r2
    .org 0x41e28-ORIGIN
L_00041e28:
    bra L_00041e36
    .org 0x41e2a-ORIGIN
L_00041e2a:
    mov r2,r0
    .org 0x41e2c-ORIGIN
L_00041e2c:
    mov.w @(r0,r4),r2
    .org 0x41e2e-ORIGIN
L_00041e2e:
    cmp/pz r2
    .org 0x41e30-ORIGIN
L_00041e30:
    bt/s L_00041e36
    .org 0x41e32-ORIGIN
L_00041e32:
    mov #-0x1,r0
    .org 0x41e34-ORIGIN
L_00041e34:
    mov #0x0,r0
    .org 0x41e36-ORIGIN
L_00041e36:
    mov.b r0,@(0x1d,gbr)
    .org 0x41e38-ORIGIN
L_00041e38:
    ldc.l @r15+,gbr
    .org 0x41e3a-ORIGIN
L_00041e3a:
    lds.l @r15+,pr
    .org 0x41e3c-ORIGIN
L_00041e3c:
    rts
    .org 0x41e3e-ORIGIN
L_00041e3e:
    nop
    .org 0x41e60-ORIGIN
P_00041e60:
    .byte 0x02
    .org 0x41e61-ORIGIN
P_00041e61:
    .byte 0x72
    .org 0x41e62-ORIGIN
P_00041e62:
    .byte 0x04
    .org 0x41e63-ORIGIN
P_00041e63:
    .byte 0xc6
    .org 0x41e64-ORIGIN
P_00041e64:
    .byte 0x04
    .org 0x41e65-ORIGIN
P_00041e65:
    .byte 0xd9
    .org 0x41e66-ORIGIN
P_00041e66:
    .byte 0x04
    .org 0x41e67-ORIGIN
P_00041e67:
    .byte 0xd7
    .org 0x41e68-ORIGIN
P_00041e68:
    .byte 0x01
    .org 0x41e69-ORIGIN
P_00041e69:
    .byte 0x02
    .org 0x41e6c-ORIGIN
P_00041e6c:
    .byte 0xff
    .org 0x41e6d-ORIGIN
P_00041e6d:
    .byte 0xff
    .org 0x41e6e-ORIGIN
P_00041e6e:
    .byte 0x1f
    .org 0x41e6f-ORIGIN
P_00041e6f:
    .byte 0xf4
    .org 0x41e70-ORIGIN
P_00041e70:
    .byte 0xff
    .org 0x41e71-ORIGIN
P_00041e71:
    .byte 0xff
    .org 0x41e72-ORIGIN
P_00041e72:
    .byte 0x12
    .org 0x41e73-ORIGIN
P_00041e73:
    .byte 0x8c
    .org 0x41e74-ORIGIN
P_00041e74:
    .byte 0xff
    .org 0x41e75-ORIGIN
P_00041e75:
    .byte 0xff
    .org 0x41e76-ORIGIN
P_00041e76:
    .byte 0x22
    .org 0x41e77-ORIGIN
P_00041e77:
    .byte 0xf8
    .org 0x41e78-ORIGIN
P_00041e78:
    .byte 0xff
    .org 0x41e79-ORIGIN
P_00041e79:
    .byte 0xff
    .org 0x41e7a-ORIGIN
P_00041e7a:
    .byte 0x24
    .org 0x41e7b-ORIGIN
P_00041e7b:
    .byte 0x64
    .org 0x41e7c-ORIGIN
P_00041e7c:
    .byte 0xff
    .org 0x41e7d-ORIGIN
P_00041e7d:
    .byte 0xff
    .org 0x41e7e-ORIGIN
P_00041e7e:
    .byte 0x1e
    .org 0x41e7f-ORIGIN
P_00041e7f:
    .byte 0x60
    .org 0x41e80-ORIGIN
P_00041e80:
    .byte 0x00
    .org 0x41e81-ORIGIN
P_00041e81:
    .byte 0x02
    .org 0x41e82-ORIGIN
P_00041e82:
    .byte 0x1b
    .org 0x41e83-ORIGIN
P_00041e83:
    .byte 0xbc
    .org 0x4bdc2-ORIGIN
L_0004bdc2:
    mov.l r13,@-r15
    .org 0x4bdc4-ORIGIN
L_0004bdc4:
    mov.l r14,@-r15
    .org 0x4bdc6-ORIGIN
L_0004bdc6:
    sts.l pr,@-r15
    .org 0x4bdc8-ORIGIN
L_0004bdc8:
    sts.l macl,@-r15
    .org 0x4bdca-ORIGIN
L_0004bdca:
    stc.l gbr,@-r15
    .org 0x4bdcc-ORIGIN
L_0004bdcc:
    mov.l P_0004bf08,r0
    .org 0x4bdce-ORIGIN
L_0004bdce:
    ldc r0,gbr
    .org 0x4bdd0-ORIGIN
L_0004bdd0:
    add #-0x4,r15
    .org 0x4bdd2-ORIGIN
L_0004bdd2:
    mov.l P_0004bf24,r6
    .org 0x4bdd4-ORIGIN
L_0004bdd4:
    mov.l P_0004bf28,r7
    .org 0x4bdd6-ORIGIN
L_0004bdd6:
    mov.b @r6,r0
    .org 0x4bdd8-ORIGIN
L_0004bdd8:
    tst #0x20,r0
    .org 0x4bdda-ORIGIN
L_0004bdda:
    bf L_0004beaa
    .org 0x4bddc-ORIGIN
L_0004bddc:
    mov.b @(0x1,r7),r0
    .org 0x4bdde-ORIGIN
L_0004bdde:
    mov.l P_0004bf08,r13
    .org 0x4bde0-ORIGIN
L_0004bde0:
    extu.b r0,r6
    .org 0x4bde2-ORIGIN
L_0004bde2:
    mov.b @(0x9,r7),r0
    .org 0x4bde4-ORIGIN
L_0004bde4:
    extu.b r0,r5
    .org 0x4bde6-ORIGIN
L_0004bde6:
    mov #0x35,r0
    .org 0x4bde8-ORIGIN
L_0004bde8:
    mov.b @(r0,r7),r2
    .org 0x4bdea-ORIGIN
L_0004bdea:
    mov.b @(0x50,gbr),r0
    .org 0x4bdec-ORIGIN
L_0004bdec:
    add r6,r2
    .org 0x4bdee-ORIGIN
L_0004bdee:
    extu.b r0,r4
    .org 0x4bdf0-ORIGIN
L_0004bdf0:
    mov.w P_0004bef2,r0
    .org 0x4bdf2-ORIGIN
L_0004bdf2:
    sub r5,r2
    .org 0x4bdf4-ORIGIN
L_0004bdf4:
    mov.b @(r0,r13),r5
    .org 0x4bdf6-ORIGIN
L_0004bdf6:
    add #-0x40,r2
    .org 0x4bdf8-ORIGIN
L_0004bdf8:
    mov.w P_0004bef4,r0
    .org 0x4bdfa-ORIGIN
L_0004bdfa:
    sub r4,r2
    .org 0x4bdfc-ORIGIN
L_0004bdfc:
    extu.b r5,r5
    .org 0x4bdfe-ORIGIN
L_0004bdfe:
    mov.b @(r0,r13),r6
    .org 0x4be00-ORIGIN
L_0004be00:
    sub r5,r2
    .org 0x4be02-ORIGIN
L_0004be02:
    mov.l P_0004bf2c,r5
    .org 0x4be04-ORIGIN
L_0004be04:
    mov #0x20,r0
    .org 0x4be06-ORIGIN
L_0004be06:
    extu.b r6,r14
    .org 0x4be08-ORIGIN
L_0004be08:
    mov.w @(r0,r5),r6
    .org 0x4be0a-ORIGIN
L_0004be0a:
    mov #0x22,r0
    .org 0x4be0c-ORIGIN
L_0004be0c:
    add r2,r14
    .org 0x4be0e-ORIGIN
L_0004be0e:
    mov.w @(r0,r5),r2
    .org 0x4be10-ORIGIN
L_0004be10:
    extu.w r6,r6
    .org 0x4be12-ORIGIN
L_0004be12:
    extu.w r2,r2
    .org 0x4be14-ORIGIN
L_0004be14:
    cmp/gt r2,r6
    .org 0x4be16-ORIGIN
L_0004be16:
    bf/s L_0004be1c
    .org 0x4be18-ORIGIN
L_0004be18:
    add #-0x40,r14
    .org 0x4be1a-ORIGIN
L_0004be1a:
    mov r2,r6
    .org 0x4be1c-ORIGIN
L_0004be1c:
    mov r6,r5
    .org 0x4be1e-ORIGIN
L_0004be1e:
    mov.l P_0004bf30,r6
    .org 0x4be20-ORIGIN
L_0004be20:
    mov.b @(0x2,r6),r0
    .org 0x4be22-ORIGIN
L_0004be22:
    tst #0x40,r0
    .org 0x4be24-ORIGIN
L_0004be24:
    bt L_0004be98
    .org 0x4be26-ORIGIN
L_0004be26:
    mov.l P_0004bf34,r6
    .org 0x4be28-ORIGIN
L_0004be28:
    extu.w r5,r5
    .org 0x4be2a-ORIGIN
L_0004be2a:
    mov.w @r6,r2
    .org 0x4be2c-ORIGIN
L_0004be2c:
    extu.w r2,r2
    .org 0x4be2e-ORIGIN
L_0004be2e:
    cmp/ge r2,r5
    .org 0x4be30-ORIGIN
L_0004be30:
    bf L_0004be98
    .org 0x4be32-ORIGIN
L_0004be32:
    mov.l P_0004bf38,r6
    .org 0x4be34-ORIGIN
L_0004be34:
    mov.l P_0004bf3c,r4
    .org 0x4be36-ORIGIN
L_0004be36:
    mov.b @(0x7,r6),r0
    .org 0x4be38-ORIGIN
L_0004be38:
    mov.l P_0004bf40,r5
    .org 0x4be3a-ORIGIN
L_0004be3a:
    mov.l P_0004bf44,r2
    .org 0x4be3c-ORIGIN
L_0004be3c:
    jsr @r2
    .org 0x4be3e-ORIGIN
L_0004be3e:
    extu.b r0,r6
    .org 0x4be40-ORIGIN
L_0004be40:
    mov.l P_0004bf48,r7
    .org 0x4be42-ORIGIN
L_0004be42:
    mov.b r0,@(0xc0,gbr)
    .org 0x4be44-ORIGIN
L_0004be44:
    mov.w @r7,r0
    .org 0x4be46-ORIGIN
L_0004be46:
    mov.l P_0004bf4c,r7
    .org 0x4be48-ORIGIN
L_0004be48:
    mov.w r0,@(0x2,r15)
    .org 0x4be4a-ORIGIN
L_0004be4a:
    mov #0x36,r0
    .org 0x4be4c-ORIGIN
L_0004be4c:
    mov.w @(r0,r7),r3
    .org 0x4be4e-ORIGIN
L_0004be4e:
    mov.l P_0004bf50,r4
    .org 0x4be50-ORIGIN
L_0004be50:
    mov.l P_0004bf54,r5
    .org 0x4be52-ORIGIN
L_0004be52:
    mov.l P_0004bf58,r6
    .org 0x4be54-ORIGIN
L_0004be54:
    mov.l P_0004bf5c,r2
    .org 0x4be56-ORIGIN
L_0004be56:
    jsr @r2
    .org 0x4be58-ORIGIN
L_0004be58:
    extu.w r3,r7
    .org 0x4be5a-ORIGIN
L_0004be5a:
    mov #-0x1,r5
    .org 0x4be5c-ORIGIN
L_0004be5c:
    extu.w r0,r6
    .org 0x4be5e-ORIGIN
L_0004be5e:
    extu.b r5,r5
    .org 0x4be60-ORIGIN
L_0004be60:
    cmp/gt r5,r6
    .org 0x4be62-ORIGIN
L_0004be62:
    bt L_0004be66
    .org 0x4be64-ORIGIN
L_0004be64:
    mov r6,r5
    .org 0x4be66-ORIGIN
L_0004be66:
    mov r5,r0
    .org 0x4be68-ORIGIN
L_0004be68:
    mov.b r0,@(0xbc,gbr)
    .org 0x4be6a-ORIGIN
L_0004be6a:
    mov.w P_0004bef6,r0
    .org 0x4be6c-ORIGIN
L_0004be6c:
    extu.b r5,r6
    .org 0x4be6e-ORIGIN
L_0004be6e:
    mov.w @(r0,r13),r2
    .org 0x4be70-ORIGIN
L_0004be70:
    mov.b @(0xc0,gbr),r0
    .org 0x4be72-ORIGIN
L_0004be72:
    extu.w r2,r3
    .org 0x4be74-ORIGIN
L_0004be74:
    extu.b r0,r2
    .org 0x4be76-ORIGIN
L_0004be76:
    mov.l P_0004bf60,r0
    .org 0x4be78-ORIGIN
L_0004be78:
    mul.l r3,r2
    .org 0x4be7a-ORIGIN
L_0004be7a:
    sts macl,r2
    .org 0x4be7c-ORIGIN
L_0004be7c:
    mul.l r2,r6
    .org 0x4be7e-ORIGIN
L_0004be7e:
    mov.l P_0004bf64,r6
    .org 0x4be80-ORIGIN
L_0004be80:
    jsr @r6
    .org 0x4be82-ORIGIN
L_0004be82:
    sts macl,r1
    .org 0x4be84-ORIGIN
L_0004be84:
    mov #-0x1,r2
    .org 0x4be86-ORIGIN
L_0004be86:
    extu.b r2,r2
    .org 0x4be88-ORIGIN
L_0004be88:
    cmp/hi r2,r0
    .org 0x4be8a-ORIGIN
L_0004be8a:
    bf/s L_0004be90
    .org 0x4be8c-ORIGIN
L_0004be8c:
    mov r0,r6
    .org 0x4be8e-ORIGIN
L_0004be8e:
    mov r2,r6
    .org 0x4be90-ORIGIN
L_0004be90:
    mov r6,r0
    .org 0x4be92-ORIGIN
L_0004be92:
    mov.b r0,@(0xbe,gbr)
    .org 0x4be94-ORIGIN
L_0004be94:
    bra L_0004be9c
    .org 0x4be96-ORIGIN
L_0004be96:
    mov r6,r2
    .org 0x4be98-ORIGIN
L_0004be98:
    mov #0x0,r2
    .org 0x4be9a-ORIGIN
L_0004be9a:
    mov r2,r0
    .org 0x4be9c-ORIGIN
L_0004be9c:
    mov.l P_0004bf68,r6
    .org 0x4be9e-ORIGIN
L_0004be9e:
    extu.b r2,r2
    .org 0x4bea0-ORIGIN
L_0004bea0:
    mov.b r0,@(0x48,gbr)
    .org 0x4bea2-ORIGIN
L_0004bea2:
    add r2,r14
    .org 0x4bea4-ORIGIN
L_0004bea4:
    mov.b @(0x3,r6),r0
    .org 0x4bea6-ORIGIN
L_0004bea6:
    bra L_0004bec6
    .org 0x4bea8-ORIGIN
L_0004bea8:
    and #0xdf,r0
    .org 0x4beaa-ORIGIN
L_0004beaa:
    mov.b @(0x9,r7),r0
    .org 0x4beac-ORIGIN
L_0004beac:
    mov.l P_0004bf08,r13
    .org 0x4beae-ORIGIN
L_0004beae:
    extu.b r0,r5
    .org 0x4beb0-ORIGIN
L_0004beb0:
    mov.w P_0004bef4,r0
    .org 0x4beb2-ORIGIN
L_0004beb2:
    mov.l P_0004bf68,r6
    .org 0x4beb4-ORIGIN
L_0004beb4:
    mov.b @(r0,r13),r2
    .org 0x4beb6-ORIGIN
L_0004beb6:
    mov #0x32,r0
    .org 0x4beb8-ORIGIN
L_0004beb8:
    mov.b @(r0,r7),r4
    .org 0x4beba-ORIGIN
L_0004beba:
    extu.b r2,r14
    .org 0x4bebc-ORIGIN
L_0004bebc:
    mov.b @(0x3,r6),r0
    .org 0x4bebe-ORIGIN
L_0004bebe:
    sub r5,r4
    .org 0x4bec0-ORIGIN
L_0004bec0:
    add r4,r14
    .org 0x4bec2-ORIGIN
L_0004bec2:
    add #-0x40,r14
    .org 0x4bec4-ORIGIN
L_0004bec4:
    or #0x20,r0
    .org 0x4bec6-ORIGIN
L_0004bec6:
    exts.w r14,r14
    .org 0x4bec8-ORIGIN
L_0004bec8:
    mov #-0x80,r2
    .org 0x4beca-ORIGIN
L_0004beca:
    cmp/ge r2,r14
    .org 0x4becc-ORIGIN
L_0004becc:
    bt/s L_0004bed4
    .org 0x4bece-ORIGIN
L_0004bece:
    mov.b r0,@(0x3,r6)
    .org 0x4bed0-ORIGIN
L_0004bed0:
    bra L_0004bed6
    .org 0x4bed2-ORIGIN
L_0004bed2:
    mov #-0x80,r6
    .org 0x4bed4-ORIGIN
L_0004bed4:
    exts.w r14,r6
    .org 0x4bed6-ORIGIN
L_0004bed6:
    exts.w r6,r2
    .org 0x4bed8-ORIGIN
L_0004bed8:
    mov #0x7f,r6
    .org 0x4beda-ORIGIN
L_0004beda:
    cmp/gt r6,r2
    .org 0x4bedc-ORIGIN
L_0004bedc:
    bf L_0004bee0
    .org 0x4bede-ORIGIN
L_0004bede:
    mov #0x7f,r2
    .org 0x4bee0-ORIGIN
L_0004bee0:
    mov.w P_0004bef8,r0
    .org 0x4bee2-ORIGIN
L_0004bee2:
    mov.b r2,@(r0,r13)
    .org 0x4bee4-ORIGIN
L_0004bee4:
    add #0x4,r15
    .org 0x4bee6-ORIGIN
L_0004bee6:
    ldc.l @r15+,gbr
    .org 0x4bee8-ORIGIN
L_0004bee8:
    lds.l @r15+,macl
    .org 0x4beea-ORIGIN
L_0004beea:
    lds.l @r15+,pr
    .org 0x4beec-ORIGIN
L_0004beec:
    mov.l @r15+,r14
    .org 0x4beee-ORIGIN
L_0004beee:
    rts
    .org 0x4bef0-ORIGIN
L_0004bef0:
    mov.l @r15+,r13
    .org 0x4bef2-ORIGIN
P_0004bef2:
    .byte 0x03
    .org 0x4bef3-ORIGIN
P_0004bef3:
    .byte 0x5e
    .org 0x4bef4-ORIGIN
P_0004bef4:
    .byte 0x07
    .org 0x4bef5-ORIGIN
P_0004bef5:
    .byte 0xf1
    .org 0x4bef6-ORIGIN
P_0004bef6:
    .byte 0x06
    .org 0x4bef7-ORIGIN
P_0004bef7:
    .byte 0x74
    .org 0x4bef8-ORIGIN
P_0004bef8:
    .byte 0x05
    .org 0x4bef9-ORIGIN
P_0004bef9:
    .byte 0xa4
    .org 0x4bf08-ORIGIN
P_0004bf08:
    .byte 0xff
    .org 0x4bf09-ORIGIN
P_0004bf09:
    .byte 0xff
    .org 0x4bf0a-ORIGIN
P_0004bf0a:
    .byte 0x12
    .org 0x4bf0b-ORIGIN
P_0004bf0b:
    .byte 0x8c
    .org 0x4bf24-ORIGIN
P_0004bf24:
    .byte 0xff
    .org 0x4bf25-ORIGIN
P_0004bf25:
    .byte 0xff
    .org 0x4bf26-ORIGIN
P_0004bf26:
    .byte 0x24
    .org 0x4bf27-ORIGIN
P_0004bf27:
    .byte 0x58
    .org 0x4bf28-ORIGIN
P_0004bf28:
    .byte 0xff
    .org 0x4bf29-ORIGIN
P_0004bf29:
    .byte 0xff
    .org 0x4bf2a-ORIGIN
P_0004bf2a:
    .byte 0x23
    .org 0x4bf2b-ORIGIN
P_0004bf2b:
    .byte 0xbc
    .org 0x4bf2c-ORIGIN
P_0004bf2c:
    .byte 0xff
    .org 0x4bf2d-ORIGIN
P_0004bf2d:
    .byte 0xff
    .org 0x4bf2e-ORIGIN
P_0004bf2e:
    .byte 0x28
    .org 0x4bf2f-ORIGIN
P_0004bf2f:
    .byte 0x98
    .org 0x4bf30-ORIGIN
P_0004bf30:
    .byte 0xff
    .org 0x4bf31-ORIGIN
P_0004bf31:
    .byte 0xff
    .org 0x4bf32-ORIGIN
P_0004bf32:
    .byte 0x41
    .org 0x4bf33-ORIGIN
P_0004bf33:
    .byte 0xa9
    .org 0x4bf34-ORIGIN
P_0004bf34:
    .byte 0x00
    .org 0x4bf35-ORIGIN
P_0004bf35:
    .byte 0x00
    .org 0x4bf36-ORIGIN
P_0004bf36:
    .byte 0x90
    .org 0x4bf37-ORIGIN
P_0004bf37:
    .byte 0x12
    .org 0x4bf38-ORIGIN
P_0004bf38:
    .byte 0xff
    .org 0x4bf39-ORIGIN
P_0004bf39:
    .byte 0xff
    .org 0x4bf3a-ORIGIN
P_0004bf3a:
    .byte 0x10
    .org 0x4bf3b-ORIGIN
P_0004bf3b:
    .byte 0x68
    .org 0x4bf3c-ORIGIN
P_0004bf3c:
    .byte 0x00
    .org 0x4bf3d-ORIGIN
P_0004bf3d:
    .byte 0x01
    .org 0x4bf3e-ORIGIN
P_0004bf3e:
    .byte 0x1f
    .org 0x4bf3f-ORIGIN
P_0004bf3f:
    .byte 0x02
    .org 0x4bf40-ORIGIN
P_0004bf40:
    .byte 0x00
    .org 0x4bf41-ORIGIN
P_0004bf41:
    .byte 0x01
    .org 0x4bf42-ORIGIN
P_0004bf42:
    .byte 0x1e
    .org 0x4bf43-ORIGIN
P_0004bf43:
    .byte 0xea
    .org 0x4bf44-ORIGIN
P_0004bf44:
    .byte 0x00
    .org 0x4bf45-ORIGIN
P_0004bf45:
    .byte 0x02
    .org 0x4bf46-ORIGIN
P_0004bf46:
    .byte 0x64
    .org 0x4bf47-ORIGIN
P_0004bf47:
    .byte 0x74
    .org 0x4bf48-ORIGIN
P_0004bf48:
    .byte 0xff
    .org 0x4bf49-ORIGIN
P_0004bf49:
    .byte 0xff
    .org 0x4bf4a-ORIGIN
P_0004bf4a:
    .byte 0x10
    .org 0x4bf4b-ORIGIN
P_0004bf4b:
    .byte 0x24
    .org 0x4bf4c-ORIGIN
P_0004bf4c:
    .byte 0xff
    .org 0x4bf4d-ORIGIN
P_0004bf4d:
    .byte 0xff
    .org 0x4bf4e-ORIGIN
P_0004bf4e:
    .byte 0x10
    .org 0x4bf4f-ORIGIN
P_0004bf4f:
    .byte 0x94
    .org 0x4bf50-ORIGIN
P_0004bf50:
    .byte 0x00
    .org 0x4bf51-ORIGIN
P_0004bf51:
    .byte 0x00
    .org 0x4bf52-ORIGIN
P_0004bf52:
    .byte 0xc5
    .org 0x4bf53-ORIGIN
P_0004bf53:
    .byte 0x0e
    .org 0x4bf54-ORIGIN
P_0004bf54:
    .byte 0x00
    .org 0x4bf55-ORIGIN
P_0004bf55:
    .byte 0x01
    .org 0x4bf56-ORIGIN
P_0004bf56:
    .byte 0x46
    .org 0x4bf57-ORIGIN
P_0004bf57:
    .byte 0x1a
    .org 0x4bf58-ORIGIN
P_0004bf58:
    .byte 0x00
    .org 0x4bf59-ORIGIN
P_0004bf59:
    .byte 0x01
    .org 0x4bf5a-ORIGIN
P_0004bf5a:
    .byte 0x46
    .org 0x4bf5b-ORIGIN
P_0004bf5b:
    .byte 0x4a
    .org 0x4bf5c-ORIGIN
P_0004bf5c:
    .byte 0x00
    .org 0x4bf5d-ORIGIN
P_0004bf5d:
    .byte 0x02
    .org 0x4bf5e-ORIGIN
P_0004bf5e:
    .byte 0x62
    .org 0x4bf5f-ORIGIN
P_0004bf5f:
    .byte 0x70
    .org 0x4bf60-ORIGIN
P_0004bf60:
    .byte 0x00
    .org 0x4bf61-ORIGIN
P_0004bf61:
    .byte 0x07
    .org 0x4bf62-ORIGIN
P_0004bf62:
    .byte 0xa1
    .org 0x4bf63-ORIGIN
P_0004bf63:
    .byte 0x20
    .org 0x4bf64-ORIGIN
P_0004bf64:
    .byte 0x00
    .org 0x4bf65-ORIGIN
P_0004bf65:
    .byte 0x02
    .org 0x4bf66-ORIGIN
P_0004bf66:
    .byte 0x1c
    .org 0x4bf67-ORIGIN
P_0004bf67:
    .byte 0xe0
    .org 0x4bf68-ORIGIN
P_0004bf68:
    .byte 0xff
    .org 0x4bf69-ORIGIN
P_0004bf69:
    .byte 0xff
    .org 0x4bf6a-ORIGIN
P_0004bf6a:
    .byte 0x24
    .org 0x4bf6b-ORIGIN
P_0004bf6b:
    .byte 0xce
    .org 0x659ae-ORIGIN
L_000659ae:
    mov.l r14,@-r15
    .org 0x659b0-ORIGIN
L_000659b0:
    sts.l pr,@-r15
    .org 0x659b2-ORIGIN
L_000659b2:
    sts.l macl,@-r15
    .org 0x659b4-ORIGIN
L_000659b4:
    add #-0x4,r15
    .org 0x659b6-ORIGIN
L_000659b6:
    mov.l P_00065ab0,r14
    .org 0x659b8-ORIGIN
L_000659b8:
    mov.w P_00065a92,r0
    .org 0x659ba-ORIGIN
L_000659ba:
    mov.l P_00065ae8,r5
    .org 0x659bc-ORIGIN
L_000659bc:
    mov.w @(r0,r14),r2
    .org 0x659be-ORIGIN
L_000659be:
    mov.b @r5,r6
    .org 0x659c0-ORIGIN
L_000659c0:
    mov #-0x40,r5
    .org 0x659c2-ORIGIN
L_000659c2:
    extu.w r2,r2
    .org 0x659c4-ORIGIN
L_000659c4:
    shll8 r5
    .org 0x659c6-ORIGIN
L_000659c6:
    extu.b r6,r6
    .org 0x659c8-ORIGIN
L_000659c8:
    add r5,r2
    .org 0x659ca-ORIGIN
L_000659ca:
    mul.l r2,r6
    .org 0x659cc-ORIGIN
L_000659cc:
    sts macl,r2
    .org 0x659ce-ORIGIN
L_000659ce:
    cmp/pz r2
    .org 0x659d0-ORIGIN
L_000659d0:
    bt L_000659d4
    .org 0x659d2-ORIGIN
L_000659d2:
    add #0x7f,r2
    .org 0x659d4-ORIGIN
L_000659d4:
    mov.l P_00065aec,r6
    .org 0x659d6-ORIGIN
L_000659d6:
    jsr @r6
    .org 0x659d8-ORIGIN
L_000659d8:
    mov r2,r0
    .org 0x659da-ORIGIN
L_000659da:
    mov #0x40,r2
    .org 0x659dc-ORIGIN
L_000659dc:
    shll8 r2
    .org 0x659de-ORIGIN
L_000659de:
    add r2,r0
    .org 0x659e0-ORIGIN
L_000659e0:
    cmp/gt r2,r0
    .org 0x659e2-ORIGIN
L_000659e2:
    bf/s L_000659e8
    .org 0x659e4-ORIGIN
L_000659e4:
    mov r0,r5
    .org 0x659e6-ORIGIN
L_000659e6:
    mov r2,r5
    .org 0x659e8-ORIGIN
L_000659e8:
    mov.l P_00065af0,r6
    .org 0x659ea-ORIGIN
L_000659ea:
    mov #0x4c,r0
    .org 0x659ec-ORIGIN
L_000659ec:
    mov.w @(r0,r6),r2
    .org 0x659ee-ORIGIN
L_000659ee:
    mov.w P_00065a94,r0
    .org 0x659f0-ORIGIN
L_000659f0:
    extu.w r2,r2
    .org 0x659f2-ORIGIN
L_000659f2:
    mov.w @(r0,r14),r6
    .org 0x659f4-ORIGIN
L_000659f4:
    add r2,r6
    .org 0x659f6-ORIGIN
L_000659f6:
    mul.l r6,r5
    .org 0x659f8-ORIGIN
L_000659f8:
    sts macl,r7
    .org 0x659fa-ORIGIN
L_000659fa:
    cmp/pz r7
    .org 0x659fc-ORIGIN
L_000659fc:
    bt L_00065a02
    .org 0x659fe-ORIGIN
L_000659fe:
    mov.w P_00065a96,r2
    .org 0x65a00-ORIGIN
L_00065a00:
    add r2,r7
    .org 0x65a02-ORIGIN
L_00065a02:
    mov.w P_00065a98,r0
    .org 0x65a04-ORIGIN
L_00065a04:
    shll r7
    .org 0x65a06-ORIGIN
L_00065a06:
    subc r2,r2
    .org 0x65a08-ORIGIN
L_00065a08:
    mov.b @(r0,r14),r5
    .org 0x65a0a-ORIGIN
L_00065a0a:
    shll r7
    .org 0x65a0c-ORIGIN
L_00065a0c:
    mov #-0x80,r6
    .org 0x65a0e-ORIGIN
L_00065a0e:
    rotcl r2
    .org 0x65a10-ORIGIN
L_00065a10:
    extu.b r5,r5
    .org 0x65a12-ORIGIN
L_00065a12:
    extu.b r6,r6
    .org 0x65a14-ORIGIN
L_00065a14:
    xtrct r2,r7
    .org 0x65a16-ORIGIN
L_00065a16:
    cmp/gt r6,r5
    .org 0x65a18-ORIGIN
L_00065a18:
    bf/s L_00065a54
    .org 0x65a1a-ORIGIN
L_00065a1a:
    mov.l r7,@r15
    .org 0x65a1c-ORIGIN
L_00065a1c:
    mov.l P_00065af4,r6
    .org 0x65a1e-ORIGIN
L_00065a1e:
    mov #0x15,r0
    .org 0x65a20-ORIGIN
L_00065a20:
    mov.b @(r0,r6),r0
    .org 0x65a22-ORIGIN
L_00065a22:
    tst #0x20,r0
    .org 0x65a24-ORIGIN
L_00065a24:
    bf L_00065a54
    .org 0x65a26-ORIGIN
L_00065a26:
    mov.l P_00065af8,r6
    .org 0x65a28-ORIGIN
L_00065a28:
    exts.w r5,r5
    .org 0x65a2a-ORIGIN
L_00065a2a:
    mov.w @(0xc,r6),r0
    .org 0x65a2c-ORIGIN
L_00065a2c:
    extu.w r0,r6
    .org 0x65a2e-ORIGIN
L_00065a2e:
    shlr2 r6
    .org 0x65a30-ORIGIN
L_00065a30:
    shlr2 r6
    .org 0x65a32-ORIGIN
L_00065a32:
    shlr2 r6
    .org 0x65a34-ORIGIN
L_00065a34:
    shlr r6
    .org 0x65a36-ORIGIN
L_00065a36:
    sub r6,r5
    .org 0x65a38-ORIGIN
L_00065a38:
    exts.w r5,r6
    .org 0x65a3a-ORIGIN
L_00065a3a:
    cmp/pz r6
    .org 0x65a3c-ORIGIN
L_00065a3c:
    bt L_00065a40
    .org 0x65a3e-ORIGIN
L_00065a3e:
    mov #0x0,r6
    .org 0x65a40-ORIGIN
L_00065a40:
    mov.l P_00065afc,r4
    .org 0x65a42-ORIGIN
L_00065a42:
    mov.l P_00065b00,r5
    .org 0x65a44-ORIGIN
L_00065a44:
    mov.l P_00065b04,r2
    .org 0x65a46-ORIGIN
L_00065a46:
    jsr @r2
    .org 0x65a48-ORIGIN
L_00065a48:
    extu.b r6,r6
    .org 0x65a4a-ORIGIN
L_00065a4a:
    mov #0x1,r2
    .org 0x65a4c-ORIGIN
L_00065a4c:
    extu.b r0,r6
    .org 0x65a4e-ORIGIN
L_00065a4e:
    shll8 r2
    .org 0x65a50-ORIGIN
L_00065a50:
    bra L_00065a58
    .org 0x65a52-ORIGIN
L_00065a52:
    sub r6,r2
    .org 0x65a54-ORIGIN
L_00065a54:
    mov #0x1,r2
    .org 0x65a56-ORIGIN
L_00065a56:
    shll8 r2
    .org 0x65a58-ORIGIN
L_00065a58:
    mov.l @r15,r7
    .org 0x65a5a-ORIGIN
L_00065a5a:
    mul.l r7,r2
    .org 0x65a5c-ORIGIN
L_00065a5c:
    sts macl,r6
    .org 0x65a5e-ORIGIN
L_00065a5e:
    cmp/pz r6
    .org 0x65a60-ORIGIN
L_00065a60:
    bt L_00065a68
    .org 0x65a62-ORIGIN
L_00065a62:
    mov #-0x1,r2
    .org 0x65a64-ORIGIN
L_00065a64:
    extu.b r2,r2
    .org 0x65a66-ORIGIN
L_00065a66:
    add r2,r6
    .org 0x65a68-ORIGIN
L_00065a68:
    mov r6,r2
    .org 0x65a6a-ORIGIN
L_00065a6a:
    shlr8 r2
    .org 0x65a6c-ORIGIN
L_00065a6c:
    swap.w r2,r6
    .org 0x65a6e-ORIGIN
L_00065a6e:
    exts.b r6,r2
    .org 0x65a70-ORIGIN
L_00065a70:
    xtrct r2,r6
    .org 0x65a72-ORIGIN
L_00065a72:
    mov #-0x80,r2
    .org 0x65a74-ORIGIN
L_00065a74:
    shll8 r2
    .org 0x65a76-ORIGIN
L_00065a76:
    cmp/ge r2,r6
    .org 0x65a78-ORIGIN
L_00065a78:
    bt L_00065a7c
    .org 0x65a7a-ORIGIN
L_00065a7a:
    mov r2,r6
    .org 0x65a7c-ORIGIN
L_00065a7c:
    mov.w P_00065a9a,r2
    .org 0x65a7e-ORIGIN
L_00065a7e:
    cmp/gt r2,r6
    .org 0x65a80-ORIGIN
L_00065a80:
    bt L_00065a84
    .org 0x65a82-ORIGIN
L_00065a82:
    mov r6,r2
    .org 0x65a84-ORIGIN
L_00065a84:
    mov.w P_00065a9c,r0
    .org 0x65a86-ORIGIN
L_00065a86:
    mov.w r2,@(r0,r14)
    .org 0x65a88-ORIGIN
L_00065a88:
    add #0x4,r15
    .org 0x65a8a-ORIGIN
L_00065a8a:
    lds.l @r15+,macl
    .org 0x65a8c-ORIGIN
L_00065a8c:
    lds.l @r15+,pr
    .org 0x65a8e-ORIGIN
L_00065a8e:
    rts
    .org 0x65a90-ORIGIN
L_00065a90:
    mov.l @r15+,r14
    .org 0x65a92-ORIGIN
P_00065a92:
    .byte 0x06
    .org 0x65a93-ORIGIN
P_00065a93:
    .byte 0x58
    .org 0x65a94-ORIGIN
P_00065a94:
    .byte 0x06
    .org 0x65a95-ORIGIN
P_00065a95:
    .byte 0x3e
    .org 0x65a96-ORIGIN
P_00065a96:
    .byte 0x3f
    .org 0x65a97-ORIGIN
P_00065a97:
    .byte 0xff
    .org 0x65a98-ORIGIN
P_00065a98:
    .byte 0x03
    .org 0x65a99-ORIGIN
P_00065a99:
    .byte 0x5f
    .org 0x65a9a-ORIGIN
P_00065a9a:
    .byte 0x7f
    .org 0x65a9b-ORIGIN
P_00065a9b:
    .byte 0xff
    .org 0x65a9c-ORIGIN
P_00065a9c:
    .byte 0x06
    .org 0x65a9d-ORIGIN
P_00065a9d:
    .byte 0x40
    .org 0x65ab0-ORIGIN
P_00065ab0:
    .byte 0xff
    .org 0x65ab1-ORIGIN
P_00065ab1:
    .byte 0xff
    .org 0x65ab2-ORIGIN
P_00065ab2:
    .byte 0x12
    .org 0x65ab3-ORIGIN
P_00065ab3:
    .byte 0x8c
    .org 0x65ae8-ORIGIN
P_00065ae8:
    .byte 0x00
    .org 0x65ae9-ORIGIN
P_00065ae9:
    .byte 0x00
    .org 0x65aea-ORIGIN
P_00065aea:
    .byte 0x87
    .org 0x65aeb-ORIGIN
P_00065aeb:
    .byte 0xee
    .org 0x65aec-ORIGIN
P_00065aec:
    .byte 0x00
    .org 0x65aed-ORIGIN
P_00065aed:
    .byte 0x02
    .org 0x65aee-ORIGIN
P_00065aee:
    .byte 0x24
    .org 0x65aef-ORIGIN
P_00065aef:
    .byte 0xf8
    .org 0x65af0-ORIGIN
P_00065af0:
    .byte 0xff
    .org 0x65af1-ORIGIN
P_00065af1:
    .byte 0xff
    .org 0x65af2-ORIGIN
P_00065af2:
    .byte 0x23
    .org 0x65af3-ORIGIN
P_00065af3:
    .byte 0xbc
    .org 0x65af4-ORIGIN
P_00065af4:
    .byte 0xff
    .org 0x65af5-ORIGIN
P_00065af5:
    .byte 0xff
    .org 0x65af6-ORIGIN
P_00065af6:
    .byte 0x24
    .org 0x65af7-ORIGIN
P_00065af7:
    .byte 0x70
    .org 0x65af8-ORIGIN
P_00065af8:
    .byte 0xff
    .org 0x65af9-ORIGIN
P_00065af9:
    .byte 0xff
    .org 0x65afa-ORIGIN
P_00065afa:
    .byte 0x22
    .org 0x65afb-ORIGIN
P_00065afb:
    .byte 0xdc
    .org 0x65afc-ORIGIN
P_00065afc:
    .byte 0x00
    .org 0x65afd-ORIGIN
P_00065afd:
    .byte 0x01
    .org 0x65afe-ORIGIN
P_00065afe:
    .byte 0x24
    .org 0x65aff-ORIGIN
P_00065aff:
    .byte 0x5a
    .org 0x65b00-ORIGIN
P_00065b00:
    .byte 0x00
    .org 0x65b01-ORIGIN
P_00065b01:
    .byte 0x01
    .org 0x65b02-ORIGIN
P_00065b02:
    .byte 0x1a
    .org 0x65b03-ORIGIN
P_00065b03:
    .byte 0x55
    .org 0x65b04-ORIGIN
P_00065b04:
    .byte 0x00
    .org 0x65b05-ORIGIN
P_00065b05:
    .byte 0x02
    .org 0x65b06-ORIGIN
P_00065b06:
    .byte 0x64
    .org 0x65b07-ORIGIN
P_00065b07:
    .byte 0x74
