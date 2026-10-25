! Exact natural bounded-divisor callers and complete real signed/unsigned helper closure.
    .text
    .balign 4
    .set ORIGIN,0x8348
    .org 0x8349-ORIGIN
P_00008349:
    .byte 0x3b
    .org 0x8542-ORIGIN
P_00008542:
    .byte 0x00
    .org 0x8543-ORIGIN
P_00008543:
    .byte 0x00
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
    .org 0x3a254-ORIGIN
L_0003a254:
    sts.l pr,@-r15
    .org 0x3a256-ORIGIN
L_0003a256:
    mov.l P_0003a48c,r6
    .org 0x3a258-ORIGIN
L_0003a258:
    mov.b @r6,r0
    .org 0x3a25a-ORIGIN
L_0003a25a:
    tst #0x8,r0
    .org 0x3a25c-ORIGIN
L_0003a25c:
    bt L_0003a280
    .org 0x3a25e-ORIGIN
L_0003a25e:
    mov.l P_0003a490,r2
    .org 0x3a260-ORIGIN
L_0003a260:
    extu.w r4,r1
    .org 0x3a262-ORIGIN
L_0003a262:
    jsr @r2
    .org 0x3a264-ORIGIN
L_0003a264:
    mov #0x14,r0
    .org 0x3a266-ORIGIN
L_0003a266:
    mov #-0x1,r6
    .org 0x3a268-ORIGIN
L_0003a268:
    extu.b r6,r6
    .org 0x3a26a-ORIGIN
L_0003a26a:
    cmp/gt r6,r0
    .org 0x3a26c-ORIGIN
L_0003a26c:
    bf/s L_0003a272
    .org 0x3a26e-ORIGIN
L_0003a26e:
    mov r0,r2
    .org 0x3a270-ORIGIN
L_0003a270:
    mov r6,r2
    .org 0x3a272-ORIGIN
L_0003a272:
    mov.l P_0003a494,r5
    .org 0x3a274-ORIGIN
L_0003a274:
    mov r2,r0
    .org 0x3a276-ORIGIN
L_0003a276:
    mov r2,r6
    .org 0x3a278-ORIGIN
L_0003a278:
    mov.l P_0003a498,r2
    .org 0x3a27a-ORIGIN
L_0003a27a:
    mov.b r0,@(0x8,r5)
    .org 0x3a27c-ORIGIN
L_0003a27c:
    mov #0x7a,r0
    .org 0x3a27e-ORIGIN
L_0003a27e:
    mov.b r6,@(r0,r2)
    .org 0x3a280-ORIGIN
L_0003a280:
    lds.l @r15+,pr
    .org 0x3a282-ORIGIN
L_0003a282:
    rts
    .org 0x3a284-ORIGIN
L_0003a284:
    nop
    .org 0x3a48c-ORIGIN
P_0003a48c:
    .byte 0x00
    .org 0x3a48d-ORIGIN
P_0003a48d:
    .byte 0x00
    .org 0x3a48e-ORIGIN
P_0003a48e:
    .byte 0x83
    .org 0x3a48f-ORIGIN
P_0003a48f:
    .byte 0x49
    .org 0x3a490-ORIGIN
P_0003a490:
    .byte 0x00
    .org 0x3a491-ORIGIN
P_0003a491:
    .byte 0x02
    .org 0x3a492-ORIGIN
P_0003a492:
    .byte 0x1b
    .org 0x3a493-ORIGIN
P_0003a493:
    .byte 0xbc
    .org 0x3a494-ORIGIN
P_0003a494:
    .byte 0xff
    .org 0x3a495-ORIGIN
P_0003a495:
    .byte 0xff
    .org 0x3a496-ORIGIN
P_0003a496:
    .byte 0x10
    .org 0x3a497-ORIGIN
P_0003a497:
    .byte 0x18
    .org 0x3a498-ORIGIN
P_0003a498:
    .byte 0xff
    .org 0x3a499-ORIGIN
P_0003a499:
    .byte 0xff
    .org 0x3a49a-ORIGIN
P_0003a49a:
    .byte 0x11
    .org 0x3a49b-ORIGIN
P_0003a49b:
    .byte 0x14
    .org 0x6e442-ORIGIN
L_0006e442:
    sts.l pr,@-r15
    .org 0x6e444-ORIGIN
L_0006e444:
    sts.l macl,@-r15
    .org 0x6e446-ORIGIN
L_0006e446:
    mov.l P_0006e5e0,r2
    .org 0x6e448-ORIGIN
L_0006e448:
    mov #0x17,r0
    .org 0x6e44a-ORIGIN
L_0006e44a:
    mov.b @(r0,r2),r6
    .org 0x6e44c-ORIGIN
L_0006e44c:
    extu.b r6,r6
    .org 0x6e44e-ORIGIN
L_0006e44e:
    tst r6,r6
    .org 0x6e450-ORIGIN
L_0006e450:
    bt L_0006e482
    .org 0x6e452-ORIGIN
L_0006e452:
    mov r6,r2
    .org 0x6e454-ORIGIN
L_0006e454:
    shll2 r2
    .org 0x6e456-ORIGIN
L_0006e456:
    add r6,r2
    .org 0x6e458-ORIGIN
L_0006e458:
    mov.l P_0006e5c4,r5
    .org 0x6e45a-ORIGIN
L_0006e45a:
    mov.w P_0006e4e2,r0
    .org 0x6e45c-ORIGIN
L_0006e45c:
    shll2 r2
    .org 0x6e45e-ORIGIN
L_0006e45e:
    mov r2,r6
    .org 0x6e460-ORIGIN
L_0006e460:
    shll2 r6
    .org 0x6e462-ORIGIN
L_0006e462:
    mov.b @(r0,r5),r2
    .org 0x6e464-ORIGIN
L_0006e464:
    mov r6,r0
    .org 0x6e466-ORIGIN
L_0006e466:
    extu.b r2,r5
    .org 0x6e468-ORIGIN
L_0006e468:
    mov.w P_0006e4e4,r2
    .org 0x6e46a-ORIGIN
L_0006e46a:
    mul.l r5,r2
    .org 0x6e46c-ORIGIN
L_0006e46c:
    mov.l P_0006e5e4,r5
    .org 0x6e46e-ORIGIN
L_0006e46e:
    jsr @r5
    .org 0x6e470-ORIGIN
L_0006e470:
    sts macl,r1
    .org 0x6e472-ORIGIN
L_0006e472:
    mov #-0x1,r6
    .org 0x6e474-ORIGIN
L_0006e474:
    add #0x32,r0
    .org 0x6e476-ORIGIN
L_0006e476:
    extu.b r6,r6
    .org 0x6e478-ORIGIN
L_0006e478:
    cmp/hi r6,r0
    .org 0x6e47a-ORIGIN
L_0006e47a:
    bf/s L_0006e484
    .org 0x6e47c-ORIGIN
L_0006e47c:
    mov r0,r2
    .org 0x6e47e-ORIGIN
L_0006e47e:
    bra L_0006e484
    .org 0x6e480-ORIGIN
L_0006e480:
    mov r6,r2
    .org 0x6e482-ORIGIN
L_0006e482:
    mov #0x0,r2
    .org 0x6e484-ORIGIN
L_0006e484:
    mov.l P_0006e5e8,r5
    .org 0x6e486-ORIGIN
L_0006e486:
    mov.w P_0006e4e6,r0
    .org 0x6e488-ORIGIN
L_0006e488:
    lds.l @r15+,macl
    .org 0x6e48a-ORIGIN
L_0006e48a:
    lds.l @r15+,pr
    .org 0x6e48c-ORIGIN
L_0006e48c:
    rts
    .org 0x6e48e-ORIGIN
L_0006e48e:
    mov.b r2,@(r0,r5)
    .org 0x6e4e2-ORIGIN
P_0006e4e2:
    .byte 0x04
    .org 0x6e4e3-ORIGIN
P_0006e4e3:
    .byte 0xda
    .org 0x6e4e4-ORIGIN
P_0006e4e4:
    .byte 0x05
    .org 0x6e4e5-ORIGIN
P_0006e4e5:
    .byte 0xc3
    .org 0x6e4e6-ORIGIN
P_0006e4e6:
    .byte 0x01
    .org 0x6e4e7-ORIGIN
P_0006e4e7:
    .byte 0x26
    .org 0x6e5c4-ORIGIN
P_0006e5c4:
    .byte 0xff
    .org 0x6e5c5-ORIGIN
P_0006e5c5:
    .byte 0xff
    .org 0x6e5c6-ORIGIN
P_0006e5c6:
    .byte 0x12
    .org 0x6e5c7-ORIGIN
P_0006e5c7:
    .byte 0x8c
    .org 0x6e5e0-ORIGIN
P_0006e5e0:
    .byte 0xff
    .org 0x6e5e1-ORIGIN
P_0006e5e1:
    .byte 0xff
    .org 0x6e5e2-ORIGIN
P_0006e5e2:
    .byte 0x11
    .org 0x6e5e3-ORIGIN
P_0006e5e3:
    .byte 0x9c
    .org 0x6e5e4-ORIGIN
P_0006e5e4:
    .byte 0x00
    .org 0x6e5e5-ORIGIN
P_0006e5e5:
    .byte 0x02
    .org 0x6e5e6-ORIGIN
P_0006e5e6:
    .byte 0x1c
    .org 0x6e5e7-ORIGIN
P_0006e5e7:
    .byte 0xe0
    .org 0x6e5e8-ORIGIN
P_0006e5e8:
    .byte 0xff
    .org 0x6e5e9-ORIGIN
P_0006e5e9:
    .byte 0xff
    .org 0x6e5ea-ORIGIN
P_0006e5ea:
    .byte 0x1e
    .org 0x6e5eb-ORIGIN
P_0006e5eb:
    .byte 0x60
    .org 0xb7c84-ORIGIN
L_000b7c84:
    sts.l pr,@-r15
    .org 0xb7c86-ORIGIN
L_000b7c86:
    sts.l macl,@-r15
    .org 0xb7c88-ORIGIN
L_000b7c88:
    mov.l P_000b7e18,r2
    .org 0xb7c8a-ORIGIN
L_000b7c8a:
    cmp/gt r2,r4
    .org 0xb7c8c-ORIGIN
L_000b7c8c:
    bt L_000b7c96
    .org 0xb7c8e-ORIGIN
L_000b7c8e:
    mov.l P_000b7e1c,r2
    .org 0xb7c90-ORIGIN
L_000b7c90:
    cmp/ge r2,r4
    .org 0xb7c92-ORIGIN
L_000b7c92:
    bf L_000b7c96
    .org 0xb7c94-ORIGIN
L_000b7c94:
    mov r4,r2
    .org 0xb7c96-ORIGIN
L_000b7c96:
    mov.l P_000b7e20,r6
    .org 0xb7c98-ORIGIN
L_000b7c98:
    mov r2,r5
    .org 0xb7c9a-ORIGIN
L_000b7c9a:
    mov.b @(0x1,r6),r0
    .org 0xb7c9c-ORIGIN
L_000b7c9c:
    mov.b @r6,r2
    .org 0xb7c9e-ORIGIN
L_000b7c9e:
    extu.b r0,r4
    .org 0xb7ca0-ORIGIN
L_000b7ca0:
    extu.b r2,r6
    .org 0xb7ca2-ORIGIN
L_000b7ca2:
    mulu.w r4,r6
    .org 0xb7ca4-ORIGIN
L_000b7ca4:
    mov.w P_000b7cf2,r4
    .org 0xb7ca6-ORIGIN
L_000b7ca6:
    sts macl,r2
    .org 0xb7ca8-ORIGIN
L_000b7ca8:
    extu.w r2,r2
    .org 0xb7caa-ORIGIN
L_000b7caa:
    cmp/gt r4,r2
    .org 0xb7cac-ORIGIN
L_000b7cac:
    bf L_000b7cb0
    .org 0xb7cae-ORIGIN
L_000b7cae:
    mov r4,r2
    .org 0xb7cb0-ORIGIN
L_000b7cb0:
    extu.w r2,r6
    .org 0xb7cb2-ORIGIN
L_000b7cb2:
    tst r6,r6
    .org 0xb7cb4-ORIGIN
L_000b7cb4:
    bt L_000b7cc6
    .org 0xb7cb6-ORIGIN
L_000b7cb6:
    mov.w P_000b7cf4,r2
    .org 0xb7cb8-ORIGIN
L_000b7cb8:
    exts.w r6,r0
    .org 0xb7cba-ORIGIN
L_000b7cba:
    mul.l r5,r2
    .org 0xb7cbc-ORIGIN
L_000b7cbc:
    mov.l P_000b7e24,r5
    .org 0xb7cbe-ORIGIN
L_000b7cbe:
    jsr @r5
    .org 0xb7cc0-ORIGIN
L_000b7cc0:
    sts macl,r1
    .org 0xb7cc2-ORIGIN
L_000b7cc2:
    bra L_000b7cd4
    .org 0xb7cc4-ORIGIN
L_000b7cc4:
    mov r0,r2
    .org 0xb7cc6-ORIGIN
L_000b7cc6:
    cmp/pz r5
    .org 0xb7cc8-ORIGIN
L_000b7cc8:
    bt L_000b7cd2
    .org 0xb7cca-ORIGIN
L_000b7cca:
    mov #-0x80,r2
    .org 0xb7ccc-ORIGIN
L_000b7ccc:
    shll8 r2
    .org 0xb7cce-ORIGIN
L_000b7cce:
    bra L_000b7cd4
    .org 0xb7cd0-ORIGIN
L_000b7cd0:
    shll16 r2
    .org 0xb7cd2-ORIGIN
L_000b7cd2:
    mov.l P_000b7e28,r2
    .org 0xb7cd4-ORIGIN
L_000b7cd4:
    mov.l P_000b7e2c,r6
    .org 0xb7cd6-ORIGIN
L_000b7cd6:
    cmp/gt r6,r2
    .org 0xb7cd8-ORIGIN
L_000b7cd8:
    bt L_000b7ce2
    .org 0xb7cda-ORIGIN
L_000b7cda:
    mov.l P_000b7e30,r6
    .org 0xb7cdc-ORIGIN
L_000b7cdc:
    cmp/ge r6,r2
    .org 0xb7cde-ORIGIN
L_000b7cde:
    bf L_000b7ce2
    .org 0xb7ce0-ORIGIN
L_000b7ce0:
    mov r2,r6
    .org 0xb7ce2-ORIGIN
L_000b7ce2:
    mov r6,r2
    .org 0xb7ce4-ORIGIN
L_000b7ce4:
    mov.l P_000b7e34,r6
    .org 0xb7ce6-ORIGIN
L_000b7ce6:
    mov.w P_000b7cf6,r0
    .org 0xb7ce8-ORIGIN
L_000b7ce8:
    mov.l r2,@(r0,r6)
    .org 0xb7cea-ORIGIN
L_000b7cea:
    lds.l @r15+,macl
    .org 0xb7cec-ORIGIN
L_000b7cec:
    lds.l @r15+,pr
    .org 0xb7cee-ORIGIN
L_000b7cee:
    rts
    .org 0xb7cf0-ORIGIN
L_000b7cf0:
    nop
    .org 0xb7cf2-ORIGIN
P_000b7cf2:
    .byte 0x29
    .org 0xb7cf3-ORIGIN
P_000b7cf3:
    .byte 0xef
    .org 0xb7cf4-ORIGIN
P_000b7cf4:
    .byte 0x4e
    .org 0xb7cf5-ORIGIN
P_000b7cf5:
    .byte 0x20
    .org 0xb7cf6-ORIGIN
P_000b7cf6:
    .byte 0x0b
    .org 0xb7cf7-ORIGIN
P_000b7cf7:
    .byte 0x08
    .org 0xb7e18-ORIGIN
P_000b7e18:
    .byte 0x00
    .org 0xb7e19-ORIGIN
P_000b7e19:
    .byte 0x01
    .org 0xb7e1a-ORIGIN
P_000b7e1a:
    .byte 0xa3
    .org 0xb7e1b-ORIGIN
P_000b7e1b:
    .byte 0x56
    .org 0xb7e1c-ORIGIN
P_000b7e1c:
    .byte 0xff
    .org 0xb7e1d-ORIGIN
P_000b7e1d:
    .byte 0xfe
    .org 0xb7e1e-ORIGIN
P_000b7e1e:
    .byte 0x5c
    .org 0xb7e1f-ORIGIN
P_000b7e1f:
    .byte 0xaa
    .org 0xb7e20-ORIGIN
P_000b7e20:
    .byte 0x00
    .org 0xb7e21-ORIGIN
P_000b7e21:
    .byte 0x00
    .org 0xb7e22-ORIGIN
P_000b7e22:
    .byte 0x85
    .org 0xb7e23-ORIGIN
P_000b7e23:
    .byte 0x42
    .org 0xb7e24-ORIGIN
P_000b7e24:
    .byte 0x00
    .org 0xb7e25-ORIGIN
P_000b7e25:
    .byte 0x02
    .org 0xb7e26-ORIGIN
P_000b7e26:
    .byte 0x1b
    .org 0xb7e27-ORIGIN
P_000b7e27:
    .byte 0xbc
    .org 0xb7e28-ORIGIN
P_000b7e28:
    .byte 0x7f
    .org 0xb7e29-ORIGIN
P_000b7e29:
    .byte 0xff
    .org 0xb7e2a-ORIGIN
P_000b7e2a:
    .byte 0xff
    .org 0xb7e2b-ORIGIN
P_000b7e2b:
    .byte 0xff
    .org 0xb7e2c-ORIGIN
P_000b7e2c:
    .byte 0x00
    .org 0xb7e2d-ORIGIN
P_000b7e2d:
    .byte 0x03
    .org 0xb7e2e-ORIGIN
P_000b7e2e:
    .byte 0x0d
    .org 0xb7e2f-ORIGIN
P_000b7e2f:
    .byte 0x40
    .org 0xb7e30-ORIGIN
P_000b7e30:
    .byte 0xff
    .org 0xb7e31-ORIGIN
P_000b7e31:
    .byte 0xfc
    .org 0xb7e32-ORIGIN
P_000b7e32:
    .byte 0xf2
    .org 0xb7e33-ORIGIN
P_000b7e33:
    .byte 0xc0
    .org 0xb7e34-ORIGIN
P_000b7e34:
    .byte 0xff
    .org 0xb7e35-ORIGIN
P_000b7e35:
    .byte 0xff
    .org 0xb7e36-ORIGIN
P_000b7e36:
    .byte 0x28
    .org 0xb7e37-ORIGIN
P_000b7e37:
    .byte 0xf8
