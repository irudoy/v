! Complete natural state-ratio callers with exact real signed/unsigned division and fixed byte-path helpers.
    .text
    .balign 4
    .set ORIGIN,0x851c
    .org 0x851d-ORIGIN
P_0000851d:
    .byte 0x80
    .org 0x8616-ORIGIN
P_00008616:
    .byte 0x01
    .org 0x86f9-ORIGIN
P_000086f9:
    .byte 0xdc
    .org 0x870c-ORIGIN
P_0000870c:
    .byte 0x44
    .org 0x8710-ORIGIN
P_00008710:
    .byte 0x7c
    .org 0x8b34-ORIGIN
P_00008b34:
    .byte 0x81
    .org 0x8b38-ORIGIN
P_00008b38:
    .byte 0x63
    .org 0x8b3f-ORIGIN
P_00008b3f:
    .byte 0x18
    .org 0x8b42-ORIGIN
P_00008b42:
    .byte 0xe0
    .org 0x8d2d-ORIGIN
P_00008d2d:
    .byte 0x83
    .org 0x8d2e-ORIGIN
P_00008d2e:
    .byte 0x6a
    .org 0x8ea6-ORIGIN
P_00008ea6:
    .byte 0x00
    .org 0x8ea7-ORIGIN
P_00008ea7:
    .byte 0x00
    .org 0x906c-ORIGIN
P_0000906c:
    .byte 0x00
    .org 0x906d-ORIGIN
P_0000906d:
    .byte 0x00
    .org 0x9456-ORIGIN
P_00009456:
    .byte 0x00
    .org 0x9457-ORIGIN
P_00009457:
    .byte 0x9a
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
    .org 0x64cb2-ORIGIN
L_00064cb2:
    mov.l r14,@-r15
    .org 0x64cb4-ORIGIN
L_00064cb4:
    sts.l pr,@-r15
    .org 0x64cb6-ORIGIN
L_00064cb6:
    sts.l macl,@-r15
    .org 0x64cb8-ORIGIN
L_00064cb8:
    stc.l gbr,@-r15
    .org 0x64cba-ORIGIN
L_00064cba:
    mov.l P_00064dd0,r0
    .org 0x64cbc-ORIGIN
L_00064cbc:
    ldc r0,gbr
    .org 0x64cbe-ORIGIN
L_00064cbe:
    add #-0x8,r15
    .org 0x64cc0-ORIGIN
L_00064cc0:
    mov.l P_00064ddc,r6
    .org 0x64cc2-ORIGIN
L_00064cc2:
    mov.b @r6,r0
    .org 0x64cc4-ORIGIN
L_00064cc4:
    tst #0x80,r0
    .org 0x64cc6-ORIGIN
L_00064cc6:
    bt L_00064d9c
    .org 0x64cc8-ORIGIN
L_00064cc8:
    mov.l P_00064de0,r5
    .org 0x64cca-ORIGIN
L_00064cca:
    mov #0x12,r0
    .org 0x64ccc-ORIGIN
L_00064ccc:
    mov.b @(r0,r5),r0
    .org 0x64cce-ORIGIN
L_00064cce:
    tst #0x1,r0
    .org 0x64cd0-ORIGIN
L_00064cd0:
    bt L_00064d08
    .org 0x64cd2-ORIGIN
L_00064cd2:
    mov.b @(0xc,r5),r0
    .org 0x64cd4-ORIGIN
L_00064cd4:
    tst #0x1,r0
    .org 0x64cd6-ORIGIN
L_00064cd6:
    bt L_00064d08
    .org 0x64cd8-ORIGIN
L_00064cd8:
    mov.l P_00064de4,r6
    .org 0x64cda-ORIGIN
L_00064cda:
    mov.b @(0x4,r6),r0
    .org 0x64cdc-ORIGIN
L_00064cdc:
    tst #0x80,r0
    .org 0x64cde-ORIGIN
L_00064cde:
    bf L_00064d08
    .org 0x64ce0-ORIGIN
L_00064ce0:
    mov.l P_00064de8,r4
    .org 0x64ce2-ORIGIN
L_00064ce2:
    mov.l P_00064dec,r6
    .org 0x64ce4-ORIGIN
L_00064ce4:
    mov.b @(0x6,r4),r0
    .org 0x64ce6-ORIGIN
L_00064ce6:
    mov.b @r6,r2
    .org 0x64ce8-ORIGIN
L_00064ce8:
    tst #0x20,r0
    .org 0x64cea-ORIGIN
L_00064cea:
    bf/s L_00064d00
    .org 0x64cec-ORIGIN
L_00064cec:
    extu.b r2,r7
    .org 0x64cee-ORIGIN
L_00064cee:
    mov #0x33,r0
    .org 0x64cf0-ORIGIN
L_00064cf0:
    mov.b @(r0,r5),r0
    .org 0x64cf2-ORIGIN
L_00064cf2:
    and #0xbf,r0
    .org 0x64cf4-ORIGIN
L_00064cf4:
    mov r0,r2
    .org 0x64cf6-ORIGIN
L_00064cf6:
    mov #0x33,r0
    .org 0x64cf8-ORIGIN
L_00064cf8:
    mov.b r2,@(r0,r5)
    .org 0x64cfa-ORIGIN
L_00064cfa:
    mov r7,r0
    .org 0x64cfc-ORIGIN
L_00064cfc:
    bra L_00064d04
    .org 0x64cfe-ORIGIN
L_00064cfe:
    and #0xfe,r0
    .org 0x64d00-ORIGIN
L_00064d00:
    mov r7,r0
    .org 0x64d02-ORIGIN
L_00064d02:
    or #0x1,r0
    .org 0x64d04-ORIGIN
L_00064d04:
    bra L_00064d1a
    .org 0x64d06-ORIGIN
L_00064d06:
    mov r0,r7
    .org 0x64d08-ORIGIN
L_00064d08:
    mov #0x33,r0
    .org 0x64d0a-ORIGIN
L_00064d0a:
    mov.l P_00064dec,r6
    .org 0x64d0c-ORIGIN
L_00064d0c:
    mov.b @(r0,r5),r0
    .org 0x64d0e-ORIGIN
L_00064d0e:
    or #0x40,r0
    .org 0x64d10-ORIGIN
L_00064d10:
    mov r0,r2
    .org 0x64d12-ORIGIN
L_00064d12:
    mov #0x33,r0
    .org 0x64d14-ORIGIN
L_00064d14:
    mov.b r2,@(r0,r5)
    .org 0x64d16-ORIGIN
L_00064d16:
    mov.b @r6,r0
    .org 0x64d18-ORIGIN
L_00064d18:
    and #0xfe,r0
    .org 0x64d1a-ORIGIN
L_00064d1a:
    mov.b r0,@r6
    .org 0x64d1c-ORIGIN
L_00064d1c:
    exts.b r0,r0
    .org 0x64d1e-ORIGIN
L_00064d1e:
    tst #0x1,r0
    .org 0x64d20-ORIGIN
L_00064d20:
    bt L_00064d70
    .org 0x64d22-ORIGIN
L_00064d22:
    mov.l P_00064df0,r2
    .org 0x64d24-ORIGIN
L_00064d24:
    mov #0x52,r0
    .org 0x64d26-ORIGIN
L_00064d26:
    mov.w @(r0,r2),r5
    .org 0x64d28-ORIGIN
L_00064d28:
    tst r5,r5
    .org 0x64d2a-ORIGIN
L_00064d2a:
    bf L_00064d30
    .org 0x64d2c-ORIGIN
L_00064d2c:
    bra L_00064fce
    .org 0x64d2e-ORIGIN
L_00064d2e:
    nop
    .org 0x64d30-ORIGIN
L_00064d30:
    mov.l P_00064df4,r6
    .org 0x64d32-ORIGIN
L_00064d32:
    exts.w r5,r5
    .org 0x64d34-ORIGIN
L_00064d34:
    mov.w @r6,r2
    .org 0x64d36-ORIGIN
L_00064d36:
    mov r5,r6
    .org 0x64d38-ORIGIN
L_00064d38:
    sub r2,r6
    .org 0x64d3a-ORIGIN
L_00064d3a:
    mov #-0x80,r2
    .org 0x64d3c-ORIGIN
L_00064d3c:
    shll8 r2
    .org 0x64d3e-ORIGIN
L_00064d3e:
    cmp/ge r2,r6
    .org 0x64d40-ORIGIN
L_00064d40:
    bt L_00064d44
    .org 0x64d42-ORIGIN
L_00064d42:
    mov r2,r6
    .org 0x64d44-ORIGIN
L_00064d44:
    mov.w P_00064dc4,r2
    .org 0x64d46-ORIGIN
L_00064d46:
    cmp/gt r2,r6
    .org 0x64d48-ORIGIN
L_00064d48:
    bf L_00064d4c
    .org 0x64d4a-ORIGIN
L_00064d4a:
    mov r2,r6
    .org 0x64d4c-ORIGIN
L_00064d4c:
    mov r6,r1
    .org 0x64d4e-ORIGIN
L_00064d4e:
    mov.l P_00064dd8,r6
    .org 0x64d50-ORIGIN
L_00064d50:
    shll16 r1
    .org 0x64d52-ORIGIN
L_00064d52:
    exts.w r5,r5
    .org 0x64d54-ORIGIN
L_00064d54:
    jsr @r6
    .org 0x64d56-ORIGIN
L_00064d56:
    mov r5,r0
    .org 0x64d58-ORIGIN
L_00064d58:
    cmp/pz r0
    .org 0x64d5a-ORIGIN
L_00064d5a:
    bt/s L_00064d60
    .org 0x64d5c-ORIGIN
L_00064d5c:
    mov r0,r6
    .org 0x64d5e-ORIGIN
L_00064d5e:
    mov #0x0,r6
    .org 0x64d60-ORIGIN
L_00064d60:
    mov #-0x1,r2
    .org 0x64d62-ORIGIN
L_00064d62:
    extu.w r2,r2
    .org 0x64d64-ORIGIN
L_00064d64:
    cmp/gt r2,r6
    .org 0x64d66-ORIGIN
L_00064d66:
    bf L_00064d6a
    .org 0x64d68-ORIGIN
L_00064d68:
    mov r2,r6
    .org 0x64d6a-ORIGIN
L_00064d6a:
    mov.l P_00064dd0,r14
    .org 0x64d6c-ORIGIN
L_00064d6c:
    bra L_00064e52
    .org 0x64d6e-ORIGIN
L_00064d6e:
    nop
    .org 0x64d70-ORIGIN
L_00064d70:
    mov #0x33,r0
    .org 0x64d72-ORIGIN
L_00064d72:
    mov.b @(r0,r5),r0
    .org 0x64d74-ORIGIN
L_00064d74:
    tst #0x40,r0
    .org 0x64d76-ORIGIN
L_00064d76:
    bt L_00064d7c
    .org 0x64d78-ORIGIN
L_00064d78:
    bra L_00064fce
    .org 0x64d7a-ORIGIN
L_00064d7a:
    nop
    .org 0x64d7c-ORIGIN
L_00064d7c:
    mov.l P_00064dd0,r14
    .org 0x64d7e-ORIGIN
L_00064d7e:
    mov.w P_00064dc6,r0
    .org 0x64d80-ORIGIN
L_00064d80:
    mov.w @(r0,r14),r6
    .org 0x64d82-ORIGIN
L_00064d82:
    extu.w r6,r6
    .org 0x64d84-ORIGIN
L_00064d84:
    tst r6,r6
    .org 0x64d86-ORIGIN
L_00064d86:
    bf L_00064d8c
    .org 0x64d88-ORIGIN
L_00064d88:
    bra L_00064fd6
    .org 0x64d8a-ORIGIN
L_00064d8a:
    nop
    .org 0x64d8c-ORIGIN
L_00064d8c:
    mov.l P_00064df8,r5
    .org 0x64d8e-ORIGIN
L_00064d8e:
    mov.w @r5,r2
    .org 0x64d90-ORIGIN
L_00064d90:
    extu.w r2,r2
    .org 0x64d92-ORIGIN
L_00064d92:
    sub r2,r6
    .org 0x64d94-ORIGIN
L_00064d94:
    cmp/pz r6
    .org 0x64d96-ORIGIN
L_00064d96:
    bt L_00064e52
    .org 0x64d98-ORIGIN
L_00064d98:
    bra L_00064e52
    .org 0x64d9a-ORIGIN
L_00064d9a:
    mov #0x0,r6
    .org 0x64d9c-ORIGIN
L_00064d9c:
    mov.l P_00064dcc,r2
    .org 0x64d9e-ORIGIN
L_00064d9e:
    mov.b @r2,r0
    .org 0x64da0-ORIGIN
L_00064da0:
    tst #0x8,r0
    .org 0x64da2-ORIGIN
L_00064da2:
    bt L_00064da8
    .org 0x64da4-ORIGIN
L_00064da4:
    bra L_00064fce
    .org 0x64da6-ORIGIN
L_00064da6:
    nop
    .org 0x64da8-ORIGIN
L_00064da8:
    mov.l P_00064dfc,r4
    .org 0x64daa-ORIGIN
L_00064daa:
    mov.b @r4,r5
    .org 0x64dac-ORIGIN
L_00064dac:
    mov.b @(0x8,r4),r0
    .org 0x64dae-ORIGIN
L_00064dae:
    extu.b r5,r5
    .org 0x64db0-ORIGIN
L_00064db0:
    extu.b r0,r2
    .org 0x64db2-ORIGIN
L_00064db2:
    cmp/gt r2,r5
    .org 0x64db4-ORIGIN
L_00064db4:
    bf L_00064e00
    .org 0x64db6-ORIGIN
L_00064db6:
    mov.l P_00064dd0,r14
    .org 0x64db8-ORIGIN
L_00064db8:
    mov #0x0,r2
    .org 0x64dba-ORIGIN
L_00064dba:
    mov.w P_00064dc6,r0
    .org 0x64dbc-ORIGIN
L_00064dbc:
    mov.w r2,@(r0,r14)
    .org 0x64dbe-ORIGIN
L_00064dbe:
    mov.w P_00064dc8,r0
    .org 0x64dc0-ORIGIN
L_00064dc0:
    bra L_00064fd6
    .org 0x64dc2-ORIGIN
L_00064dc2:
    mov.w r2,@(r0,r14)
    .org 0x64dc4-ORIGIN
P_00064dc4:
    .byte 0x7f
    .org 0x64dc5-ORIGIN
P_00064dc5:
    .byte 0xff
    .org 0x64dc6-ORIGIN
P_00064dc6:
    .byte 0x05
    .org 0x64dc7-ORIGIN
P_00064dc7:
    .byte 0xda
    .org 0x64dc8-ORIGIN
P_00064dc8:
    .byte 0x05
    .org 0x64dc9-ORIGIN
P_00064dc9:
    .byte 0xdc
    .org 0x64dcc-ORIGIN
P_00064dcc:
    .byte 0x00
    .org 0x64dcd-ORIGIN
P_00064dcd:
    .byte 0x00
    .org 0x64dce-ORIGIN
P_00064dce:
    .byte 0x8b
    .org 0x64dcf-ORIGIN
P_00064dcf:
    .byte 0x38
    .org 0x64dd0-ORIGIN
P_00064dd0:
    .byte 0xff
    .org 0x64dd1-ORIGIN
P_00064dd1:
    .byte 0xff
    .org 0x64dd2-ORIGIN
P_00064dd2:
    .byte 0x12
    .org 0x64dd3-ORIGIN
P_00064dd3:
    .byte 0x8c
    .org 0x64dd8-ORIGIN
P_00064dd8:
    .byte 0x00
    .org 0x64dd9-ORIGIN
P_00064dd9:
    .byte 0x02
    .org 0x64dda-ORIGIN
P_00064dda:
    .byte 0x1b
    .org 0x64ddb-ORIGIN
P_00064ddb:
    .byte 0xbc
    .org 0x64ddc-ORIGIN
P_00064ddc:
    .byte 0x00
    .org 0x64ddd-ORIGIN
P_00064ddd:
    .byte 0x00
    .org 0x64dde-ORIGIN
P_00064dde:
    .byte 0x87
    .org 0x64ddf-ORIGIN
P_00064ddf:
    .byte 0x0c
    .org 0x64de0-ORIGIN
P_00064de0:
    .byte 0xff
    .org 0x64de1-ORIGIN
P_00064de1:
    .byte 0xff
    .org 0x64de2-ORIGIN
P_00064de2:
    .byte 0x24
    .org 0x64de3-ORIGIN
P_00064de3:
    .byte 0x70
    .org 0x64de4-ORIGIN
P_00064de4:
    .byte 0xff
    .org 0x64de5-ORIGIN
P_00064de5:
    .byte 0xff
    .org 0x64de6-ORIGIN
P_00064de6:
    .byte 0x42
    .org 0x64de7-ORIGIN
P_00064de7:
    .byte 0x4c
    .org 0x64de8-ORIGIN
P_00064de8:
    .byte 0xff
    .org 0x64de9-ORIGIN
P_00064de9:
    .byte 0xff
    .org 0x64dea-ORIGIN
P_00064dea:
    .byte 0x41
    .org 0x64deb-ORIGIN
P_00064deb:
    .byte 0x88
    .org 0x64dec-ORIGIN
P_00064dec:
    .byte 0xff
    .org 0x64ded-ORIGIN
P_00064ded:
    .byte 0xff
    .org 0x64dee-ORIGIN
P_00064dee:
    .byte 0x24
    .org 0x64def-ORIGIN
P_00064def:
    .byte 0x6a
    .org 0x64df0-ORIGIN
P_00064df0:
    .byte 0xff
    .org 0x64df1-ORIGIN
P_00064df1:
    .byte 0xff
    .org 0x64df2-ORIGIN
P_00064df2:
    .byte 0x23
    .org 0x64df3-ORIGIN
P_00064df3:
    .byte 0xbc
    .org 0x64df4-ORIGIN
P_00064df4:
    .byte 0x00
    .org 0x64df5-ORIGIN
P_00064df5:
    .byte 0x00
    .org 0x64df6-ORIGIN
P_00064df6:
    .byte 0x8e
    .org 0x64df7-ORIGIN
P_00064df7:
    .byte 0xa6
    .org 0x64df8-ORIGIN
P_00064df8:
    .byte 0x00
    .org 0x64df9-ORIGIN
P_00064df9:
    .byte 0x00
    .org 0x64dfa-ORIGIN
P_00064dfa:
    .byte 0x90
    .org 0x64dfb-ORIGIN
P_00064dfb:
    .byte 0x6c
    .org 0x64dfc-ORIGIN
P_00064dfc:
    .byte 0xff
    .org 0x64dfd-ORIGIN
P_00064dfd:
    .byte 0xff
    .org 0x64dfe-ORIGIN
P_00064dfe:
    .byte 0x10
    .org 0x64dff-ORIGIN
P_00064dff:
    .byte 0x82
    .org 0x64e00-ORIGIN
L_00064e00:
    mov.l P_00064ff0,r6
    .org 0x64e02-ORIGIN
L_00064e02:
    mov.b @r6,r0
    .org 0x64e04-ORIGIN
L_00064e04:
    tst #0x1,r0
    .org 0x64e06-ORIGIN
L_00064e06:
    bf L_00064e10
    .org 0x64e08-ORIGIN
L_00064e08:
    mov.l P_00064ff4,r6
    .org 0x64e0a-ORIGIN
L_00064e0a:
    mov.b @r6,r0
    .org 0x64e0c-ORIGIN
L_00064e0c:
    tst #0x1,r0
    .org 0x64e0e-ORIGIN
L_00064e0e:
    bf L_00064e2c
    .org 0x64e10-ORIGIN
L_00064e10:
    mov.l P_00064ff8,r6
    .org 0x64e12-ORIGIN
L_00064e12:
    mov.b @(0x8,r6),r0
    .org 0x64e14-ORIGIN
L_00064e14:
    tst #0x20,r0
    .org 0x64e16-ORIGIN
L_00064e16:
    bf L_00064e1e
    .org 0x64e18-ORIGIN
L_00064e18:
    mov.b @(0x4,r6),r0
    .org 0x64e1a-ORIGIN
L_00064e1a:
    tst #0x20,r0
    .org 0x64e1c-ORIGIN
L_00064e1c:
    bf L_00064e2c
    .org 0x64e1e-ORIGIN
L_00064e1e:
    mov.l P_00064ff8,r6
    .org 0x64e20-ORIGIN
L_00064e20:
    mov.b @(0x7,r6),r0
    .org 0x64e22-ORIGIN
L_00064e22:
    tst #0x40,r0
    .org 0x64e24-ORIGIN
L_00064e24:
    bf L_00064e58
    .org 0x64e26-ORIGIN
L_00064e26:
    mov.b @(0x3,r6),r0
    .org 0x64e28-ORIGIN
L_00064e28:
    tst #0x40,r0
    .org 0x64e2a-ORIGIN
L_00064e2a:
    bt L_00064e58
    .org 0x64e2c-ORIGIN
L_00064e2c:
    mov.l P_00064ffc,r3
    .org 0x64e2e-ORIGIN
L_00064e2e:
    mov.b @(0x7,r3),r0
    .org 0x64e30-ORIGIN
L_00064e30:
    tst #0x10,r0
    .org 0x64e32-ORIGIN
L_00064e32:
    bt L_00064e48
    .org 0x64e34-ORIGIN
L_00064e34:
    mov.l P_00065000,r7
    .org 0x64e36-ORIGIN
L_00064e36:
    mov.b @r7,r0
    .org 0x64e38-ORIGIN
L_00064e38:
    tst #0x40,r0
    .org 0x64e3a-ORIGIN
L_00064e3a:
    bt L_00064e48
    .org 0x64e3c-ORIGIN
L_00064e3c:
    mov.l P_00065004,r6
    .org 0x64e3e-ORIGIN
L_00064e3e:
    mov.w P_00064ed4,r0
    .org 0x64e40-ORIGIN
L_00064e40:
    mov.b @(r0,r6),r2
    .org 0x64e42-ORIGIN
L_00064e42:
    extu.b r2,r2
    .org 0x64e44-ORIGIN
L_00064e44:
    bra L_00064fd0
    .org 0x64e46-ORIGIN
L_00064e46:
    shll8 r2
    .org 0x64e48-ORIGIN
L_00064e48:
    mov.l P_00065008,r14
    .org 0x64e4a-ORIGIN
L_00064e4a:
    mov.w P_00064ed6,r0
    .org 0x64e4c-ORIGIN
L_00064e4c:
    mov.b @(r0,r14),r2
    .org 0x64e4e-ORIGIN
L_00064e4e:
    extu.b r2,r6
    .org 0x64e50-ORIGIN
L_00064e50:
    shll8 r6
    .org 0x64e52-ORIGIN
L_00064e52:
    mov.w P_00064ed8,r0
    .org 0x64e54-ORIGIN
L_00064e54:
    bra L_00064fd6
    .org 0x64e56-ORIGIN
L_00064e56:
    mov.w r6,@(r0,r14)
    .org 0x64e58-ORIGIN
L_00064e58:
    mov.l P_00064ff4,r6
    .org 0x64e5a-ORIGIN
L_00064e5a:
    mov.b @r6,r0
    .org 0x64e5c-ORIGIN
L_00064e5c:
    tst #0x1,r0
    .org 0x64e5e-ORIGIN
L_00064e5e:
    bt L_00064ee2
    .org 0x64e60-ORIGIN
L_00064e60:
    mov.l P_00065004,r6
    .org 0x64e62-ORIGIN
L_00064e62:
    mov.w P_00064ed4,r0
    .org 0x64e64-ORIGIN
L_00064e64:
    mov.l P_00064ffc,r3
    .org 0x64e66-ORIGIN
L_00064e66:
    mov.b @(r0,r6),r2
    .org 0x64e68-ORIGIN
L_00064e68:
    mov.b @(0x7,r3),r0
    .org 0x64e6a-ORIGIN
L_00064e6a:
    extu.b r2,r6
    .org 0x64e6c-ORIGIN
L_00064e6c:
    shll8 r6
    .org 0x64e6e-ORIGIN
L_00064e6e:
    tst #0x10,r0
    .org 0x64e70-ORIGIN
L_00064e70:
    bt/s L_00064e82
    .org 0x64e72-ORIGIN
L_00064e72:
    extu.w r6,r4
    .org 0x64e74-ORIGIN
L_00064e74:
    mov.l P_00065000,r7
    .org 0x64e76-ORIGIN
L_00064e76:
    mov.b @r7,r0
    .org 0x64e78-ORIGIN
L_00064e78:
    tst #0x40,r0
    .org 0x64e7a-ORIGIN
L_00064e7a:
    bt L_00064e82
    .org 0x64e7c-ORIGIN
L_00064e7c:
    mov.l P_00065008,r14
    .org 0x64e7e-ORIGIN
L_00064e7e:
    bra L_00064ea4
    .org 0x64e80-ORIGIN
L_00064e80:
    nop
    .org 0x64e82-ORIGIN
L_00064e82:
    mov.l P_00065008,r14
    .org 0x64e84-ORIGIN
L_00064e84:
    mov.w P_00064ed8,r0
    .org 0x64e86-ORIGIN
L_00064e86:
    mov.w @(r0,r14),r7
    .org 0x64e88-ORIGIN
L_00064e88:
    extu.w r7,r6
    .org 0x64e8a-ORIGIN
L_00064e8a:
    cmp/ge r4,r6
    .org 0x64e8c-ORIGIN
L_00064e8c:
    bt L_00064e9e
    .org 0x64e8e-ORIGIN
L_00064e8e:
    mov.w @(0x152,gbr),r0
    .org 0x64e90-ORIGIN
L_00064e90:
    extu.w r0,r2
    .org 0x64e92-ORIGIN
L_00064e92:
    add r2,r6
    .org 0x64e94-ORIGIN
L_00064e94:
    mov #-0x1,r2
    .org 0x64e96-ORIGIN
L_00064e96:
    extu.w r2,r2
    .org 0x64e98-ORIGIN
L_00064e98:
    cmp/hi r2,r6
    .org 0x64e9a-ORIGIN
L_00064e9a:
    bf L_00064e9e
    .org 0x64e9c-ORIGIN
L_00064e9c:
    mov r2,r6
    .org 0x64e9e-ORIGIN
L_00064e9e:
    cmp/hi r4,r6
    .org 0x64ea0-ORIGIN
L_00064ea0:
    bt L_00064ea4
    .org 0x64ea2-ORIGIN
L_00064ea2:
    mov r6,r4
    .org 0x64ea4-ORIGIN
L_00064ea4:
    mov.w P_00064ed8,r0
    .org 0x64ea6-ORIGIN
L_00064ea6:
    mov.l P_0006500c,r3
    .org 0x64ea8-ORIGIN
L_00064ea8:
    mov.w r4,@(r0,r14)
    .org 0x64eaa-ORIGIN
L_00064eaa:
    mov.b @(0x1,r3),r0
    .org 0x64eac-ORIGIN
L_00064eac:
    extu.b r0,r2
    .org 0x64eae-ORIGIN
L_00064eae:
    cmp/gt r5,r2
    .org 0x64eb0-ORIGIN
L_00064eb0:
    bt L_00064eb6
    .org 0x64eb2-ORIGIN
L_00064eb2:
    bra L_00064fd6
    .org 0x64eb4-ORIGIN
L_00064eb4:
    nop
    .org 0x64eb6-ORIGIN
L_00064eb6:
    mov.l P_00064ff8,r6
    .org 0x64eb8-ORIGIN
L_00064eb8:
    mov.b @(0x3,r6),r0
    .org 0x64eba-ORIGIN
L_00064eba:
    tst #0x1,r0
    .org 0x64ebc-ORIGIN
L_00064ebc:
    bt L_00064ec2
    .org 0x64ebe-ORIGIN
L_00064ebe:
    bra L_00064fd6
    .org 0x64ec0-ORIGIN
L_00064ec0:
    nop
    .org 0x64ec2-ORIGIN
L_00064ec2:
    mov.w P_00064eda,r0
    .org 0x64ec4-ORIGIN
L_00064ec4:
    mov.w @(r0,r14),r2
    .org 0x64ec6-ORIGIN
L_00064ec6:
    mov.w P_00064edc,r0
    .org 0x64ec8-ORIGIN
L_00064ec8:
    mov.w r2,@(r0,r14)
    .org 0x64eca-ORIGIN
L_00064eca:
    mov.w P_00064ede,r0
    .org 0x64ecc-ORIGIN
L_00064ecc:
    mov.w r2,@(r0,r14)
    .org 0x64ece-ORIGIN
L_00064ece:
    mov.w P_00064ee0,r0
    .org 0x64ed0-ORIGIN
L_00064ed0:
    bra L_00064fd6
    .org 0x64ed2-ORIGIN
L_00064ed2:
    mov.w r4,@(r0,r14)
    .org 0x64ed4-ORIGIN
P_00064ed4:
    .byte 0x0a
    .org 0x64ed5-ORIGIN
P_00064ed5:
    .byte 0x7b
    .org 0x64ed6-ORIGIN
P_00064ed6:
    .byte 0x05
    .org 0x64ed7-ORIGIN
P_00064ed7:
    .byte 0xe7
    .org 0x64ed8-ORIGIN
P_00064ed8:
    .byte 0x05
    .org 0x64ed9-ORIGIN
P_00064ed9:
    .byte 0xda
    .org 0x64eda-ORIGIN
P_00064eda:
    .byte 0x04
    .org 0x64edb-ORIGIN
P_00064edb:
    .byte 0xe4
    .org 0x64edc-ORIGIN
P_00064edc:
    .byte 0x04
    .org 0x64edd-ORIGIN
P_00064edd:
    .byte 0xde
    .org 0x64ede-ORIGIN
P_00064ede:
    .byte 0x04
    .org 0x64edf-ORIGIN
P_00064edf:
    .byte 0xe8
    .org 0x64ee0-ORIGIN
P_00064ee0:
    .byte 0x05
    .org 0x64ee1-ORIGIN
P_00064ee1:
    .byte 0xdc
    .org 0x64ee2-ORIGIN
L_00064ee2:
    mov.l P_00065010,r7
    .org 0x64ee4-ORIGIN
L_00064ee4:
    mov #0x33,r0
    .org 0x64ee6-ORIGIN
L_00064ee6:
    mov.b @(r0,r7),r4
    .org 0x64ee8-ORIGIN
L_00064ee8:
    mov #0x12,r0
    .org 0x64eea-ORIGIN
L_00064eea:
    mov.b @(r0,r7),r0
    .org 0x64eec-ORIGIN
L_00064eec:
    mov.l r7,@(0x4,r15)
    .org 0x64eee-ORIGIN
L_00064eee:
    tst #0x1,r0
    .org 0x64ef0-ORIGIN
L_00064ef0:
    bt/s L_00064fbc
    .org 0x64ef2-ORIGIN
L_00064ef2:
    mov.b r4,@r15
    .org 0x64ef4-ORIGIN
L_00064ef4:
    mov.b @(0xc,r7),r0
    .org 0x64ef6-ORIGIN
L_00064ef6:
    tst #0x1,r0
    .org 0x64ef8-ORIGIN
L_00064ef8:
    bt L_00064fbc
    .org 0x64efa-ORIGIN
L_00064efa:
    mov.l P_00065014,r6
    .org 0x64efc-ORIGIN
L_00064efc:
    mov.b @(0x4,r6),r0
    .org 0x64efe-ORIGIN
L_00064efe:
    tst #0x80,r0
    .org 0x64f00-ORIGIN
L_00064f00:
    bf L_00064fbc
    .org 0x64f02-ORIGIN
L_00064f02:
    mov.l P_00064ffc,r3
    .org 0x64f04-ORIGIN
L_00064f04:
    mov.b @(0x7,r3),r0
    .org 0x64f06-ORIGIN
L_00064f06:
    tst #0x14,r0
    .org 0x64f08-ORIGIN
L_00064f08:
    bt L_00064f96
    .org 0x64f0a-ORIGIN
L_00064f0a:
    mov.l P_0006500c,r3
    .org 0x64f0c-ORIGIN
L_00064f0c:
    mov.b @(0x1,r3),r0
    .org 0x64f0e-ORIGIN
L_00064f0e:
    extu.b r0,r6
    .org 0x64f10-ORIGIN
L_00064f10:
    cmp/gt r5,r6
    .org 0x64f12-ORIGIN
L_00064f12:
    bf L_00064f96
    .org 0x64f14-ORIGIN
L_00064f14:
    mov.l P_00065008,r14
    .org 0x64f16-ORIGIN
L_00064f16:
    mov.w P_00064fe2,r0
    .org 0x64f18-ORIGIN
L_00064f18:
    mov.w @(r0,r14),r2
    .org 0x64f1a-ORIGIN
L_00064f1a:
    extu.w r2,r6
    .org 0x64f1c-ORIGIN
L_00064f1c:
    cmp/pl r6
    .org 0x64f1e-ORIGIN
L_00064f1e:
    bf L_00064f96
    .org 0x64f20-ORIGIN
L_00064f20:
    mov.w P_00064fe4,r0
    .org 0x64f22-ORIGIN
L_00064f22:
    mov.w @(r0,r14),r2
    .org 0x64f24-ORIGIN
L_00064f24:
    extu.w r2,r6
    .org 0x64f26-ORIGIN
L_00064f26:
    cmp/pl r6
    .org 0x64f28-ORIGIN
L_00064f28:
    bf L_00064f96
    .org 0x64f2a-ORIGIN
L_00064f2a:
    mov.w P_00064fe6,r0
    .org 0x64f2c-ORIGIN
L_00064f2c:
    mov.w @(r0,r14),r2
    .org 0x64f2e-ORIGIN
L_00064f2e:
    mov.w P_00064fe8,r0
    .org 0x64f30-ORIGIN
L_00064f30:
    extu.w r2,r6
    .org 0x64f32-ORIGIN
L_00064f32:
    mov.w @(r0,r14),r5
    .org 0x64f34-ORIGIN
L_00064f34:
    extu.w r5,r5
    .org 0x64f36-ORIGIN
L_00064f36:
    cmp/gt r5,r6
    .org 0x64f38-ORIGIN
L_00064f38:
    bf L_00064f3e
    .org 0x64f3a-ORIGIN
L_00064f3a:
    bra L_00064f42
    .org 0x64f3c-ORIGIN
L_00064f3c:
    mov r5,r6
    .org 0x64f3e-ORIGIN
L_00064f3e:
    mov.w P_00064fe6,r0
    .org 0x64f40-ORIGIN
L_00064f40:
    mov.w @(r0,r14),r6
    .org 0x64f42-ORIGIN
L_00064f42:
    mov.w P_00064fe6,r0
    .org 0x64f44-ORIGIN
L_00064f44:
    extu.w r6,r5
    .org 0x64f46-ORIGIN
L_00064f46:
    mov.w r5,@(r0,r14)
    .org 0x64f48-ORIGIN
L_00064f48:
    mov.w P_00064fea,r0
    .org 0x64f4a-ORIGIN
L_00064f4a:
    mov.w @(r0,r14),r2
    .org 0x64f4c-ORIGIN
L_00064f4c:
    mov.w P_00064fec,r0
    .org 0x64f4e-ORIGIN
L_00064f4e:
    extu.w r2,r4
    .org 0x64f50-ORIGIN
L_00064f50:
    mov.l P_00065018,r2
    .org 0x64f52-ORIGIN
L_00064f52:
    mov.w @r2,r6
    .org 0x64f54-ORIGIN
L_00064f54:
    extu.w r6,r2
    .org 0x64f56-ORIGIN
L_00064f56:
    mov r4,r6
    .org 0x64f58-ORIGIN
L_00064f58:
    add r2,r6
    .org 0x64f5a-ORIGIN
L_00064f5a:
    mov.w @(r0,r14),r2
    .org 0x64f5c-ORIGIN
L_00064f5c:
    extu.w r2,r4
    .org 0x64f5e-ORIGIN
L_00064f5e:
    cmp/hi r6,r4
    .org 0x64f60-ORIGIN
L_00064f60:
    bf L_00064f92
    .org 0x64f62-ORIGIN
L_00064f62:
    cmp/hi r6,r5
    .org 0x64f64-ORIGIN
L_00064f64:
    bf L_00064f92
    .org 0x64f66-ORIGIN
L_00064f66:
    mov.w P_00064fe4,r0
    .org 0x64f68-ORIGIN
L_00064f68:
    mov r5,r2
    .org 0x64f6a-ORIGIN
L_00064f6a:
    sub r6,r2
    .org 0x64f6c-ORIGIN
L_00064f6c:
    mov.w @(r0,r14),r4
    .org 0x64f6e-ORIGIN
L_00064f6e:
    mov.w P_00064fec,r0
    .org 0x64f70-ORIGIN
L_00064f70:
    extu.w r4,r5
    .org 0x64f72-ORIGIN
L_00064f72:
    mul.l r5,r2
    .org 0x64f74-ORIGIN
L_00064f74:
    mov.w @(r0,r14),r5
    .org 0x64f76-ORIGIN
L_00064f76:
    sts macl,r1
    .org 0x64f78-ORIGIN
L_00064f78:
    extu.w r5,r4
    .org 0x64f7a-ORIGIN
L_00064f7a:
    mov r4,r5
    .org 0x64f7c-ORIGIN
L_00064f7c:
    sub r6,r5
    .org 0x64f7e-ORIGIN
L_00064f7e:
    mov.l P_0006501c,r6
    .org 0x64f80-ORIGIN
L_00064f80:
    jsr @r6
    .org 0x64f82-ORIGIN
L_00064f82:
    mov r5,r0
    .org 0x64f84-ORIGIN
L_00064f84:
    mov #-0x1,r2
    .org 0x64f86-ORIGIN
L_00064f86:
    extu.w r2,r2
    .org 0x64f88-ORIGIN
L_00064f88:
    cmp/hi r2,r0
    .org 0x64f8a-ORIGIN
L_00064f8a:
    bt/s L_00064fae
    .org 0x64f8c-ORIGIN
L_00064f8c:
    mov r0,r6
    .org 0x64f8e-ORIGIN
L_00064f8e:
    bra L_00064fae
    .org 0x64f90-ORIGIN
L_00064f90:
    mov r6,r2
    .org 0x64f92-ORIGIN
L_00064f92:
    bra L_00064fae
    .org 0x64f94-ORIGIN
L_00064f94:
    mov #0x0,r2
    .org 0x64f96-ORIGIN
L_00064f96:
    mov.l P_00065008,r14
    .org 0x64f98-ORIGIN
L_00064f98:
    mov.w P_00064fe2,r0
    .org 0x64f9a-ORIGIN
L_00064f9a:
    mov.w @(r0,r14),r6
    .org 0x64f9c-ORIGIN
L_00064f9c:
    extu.w r6,r2
    .org 0x64f9e-ORIGIN
L_00064f9e:
    tst r2,r2
    .org 0x64fa0-ORIGIN
L_00064fa0:
    bt L_00064fb2
    .org 0x64fa2-ORIGIN
L_00064fa2:
    mov.w @(0x150,gbr),r0
    .org 0x64fa4-ORIGIN
L_00064fa4:
    extu.w r0,r6
    .org 0x64fa6-ORIGIN
L_00064fa6:
    sub r6,r2
    .org 0x64fa8-ORIGIN
L_00064fa8:
    cmp/pz r2
    .org 0x64faa-ORIGIN
L_00064faa:
    bt L_00064fae
    .org 0x64fac-ORIGIN
L_00064fac:
    mov #0x0,r2
    .org 0x64fae-ORIGIN
L_00064fae:
    mov.w P_00064fe2,r0
    .org 0x64fb0-ORIGIN
L_00064fb0:
    mov.w r2,@(r0,r14)
    .org 0x64fb2-ORIGIN
L_00064fb2:
    mov.b @r15,r0
    .org 0x64fb4-ORIGIN
L_00064fb4:
    mov.l @(0x4,r15),r7
    .org 0x64fb6-ORIGIN
L_00064fb6:
    and #0xbf,r0
    .org 0x64fb8-ORIGIN
L_00064fb8:
    bra L_00064fc8
    .org 0x64fba-ORIGIN
L_00064fba:
    mov r0,r4
    .org 0x64fbc-ORIGIN
L_00064fbc:
    mov.l P_00065008,r14
    .org 0x64fbe-ORIGIN
L_00064fbe:
    mov #0x0,r2
    .org 0x64fc0-ORIGIN
L_00064fc0:
    mov.w P_00064fe2,r0
    .org 0x64fc2-ORIGIN
L_00064fc2:
    mov.w r2,@(r0,r14)
    .org 0x64fc4-ORIGIN
L_00064fc4:
    mov #0x40,r0
    .org 0x64fc6-ORIGIN
L_00064fc6:
    or r0,r4
    .org 0x64fc8-ORIGIN
L_00064fc8:
    mov #0x33,r0
    .org 0x64fca-ORIGIN
L_00064fca:
    bra L_00064fd6
    .org 0x64fcc-ORIGIN
L_00064fcc:
    mov.b r4,@(r0,r7)
    .org 0x64fce-ORIGIN
L_00064fce:
    mov #0x0,r2
    .org 0x64fd0-ORIGIN
L_00064fd0:
    mov.l P_00065008,r14
    .org 0x64fd2-ORIGIN
L_00064fd2:
    mov.w P_00064fe2,r0
    .org 0x64fd4-ORIGIN
L_00064fd4:
    mov.w r2,@(r0,r14)
    .org 0x64fd6-ORIGIN
L_00064fd6:
    add #0x8,r15
    .org 0x64fd8-ORIGIN
L_00064fd8:
    ldc.l @r15+,gbr
    .org 0x64fda-ORIGIN
L_00064fda:
    lds.l @r15+,macl
    .org 0x64fdc-ORIGIN
L_00064fdc:
    lds.l @r15+,pr
    .org 0x64fde-ORIGIN
L_00064fde:
    rts
    .org 0x64fe0-ORIGIN
L_00064fe0:
    mov.l @r15+,r14
    .org 0x64fe2-ORIGIN
P_00064fe2:
    .byte 0x05
    .org 0x64fe3-ORIGIN
P_00064fe3:
    .byte 0xda
    .org 0x64fe4-ORIGIN
P_00064fe4:
    .byte 0x05
    .org 0x64fe5-ORIGIN
P_00064fe5:
    .byte 0xdc
    .org 0x64fe6-ORIGIN
P_00064fe6:
    .byte 0x04
    .org 0x64fe7-ORIGIN
P_00064fe7:
    .byte 0xe8
    .org 0x64fe8-ORIGIN
P_00064fe8:
    .byte 0x04
    .org 0x64fe9-ORIGIN
P_00064fe9:
    .byte 0xe4
    .org 0x64fea-ORIGIN
P_00064fea:
    .byte 0x04
    .org 0x64feb-ORIGIN
P_00064feb:
    .byte 0xe6
    .org 0x64fec-ORIGIN
P_00064fec:
    .byte 0x04
    .org 0x64fed-ORIGIN
P_00064fed:
    .byte 0xde
    .org 0x64ff0-ORIGIN
P_00064ff0:
    .byte 0xff
    .org 0x64ff1-ORIGIN
P_00064ff1:
    .byte 0xff
    .org 0x64ff2-ORIGIN
P_00064ff2:
    .byte 0x24
    .org 0x64ff3-ORIGIN
P_00064ff3:
    .byte 0x6d
    .org 0x64ff4-ORIGIN
P_00064ff4:
    .byte 0xff
    .org 0x64ff5-ORIGIN
P_00064ff5:
    .byte 0xff
    .org 0x64ff6-ORIGIN
P_00064ff6:
    .byte 0x24
    .org 0x64ff7-ORIGIN
P_00064ff7:
    .byte 0x6a
    .org 0x64ff8-ORIGIN
P_00064ff8:
    .byte 0xff
    .org 0x64ff9-ORIGIN
P_00064ff9:
    .byte 0xff
    .org 0x64ffa-ORIGIN
P_00064ffa:
    .byte 0x24
    .org 0x64ffb-ORIGIN
P_00064ffb:
    .byte 0x4c
    .org 0x64ffc-ORIGIN
P_00064ffc:
    .byte 0x00
    .org 0x64ffd-ORIGIN
P_00064ffd:
    .byte 0x00
    .org 0x64ffe-ORIGIN
P_00064ffe:
    .byte 0x8b
    .org 0x64fff-ORIGIN
P_00064fff:
    .byte 0x38
    .org 0x65000-ORIGIN
P_00065000:
    .byte 0x00
    .org 0x65001-ORIGIN
P_00065001:
    .byte 0x00
    .org 0x65002-ORIGIN
P_00065002:
    .byte 0x87
    .org 0x65003-ORIGIN
P_00065003:
    .byte 0x10
    .org 0x65004-ORIGIN
P_00065004:
    .byte 0xff
    .org 0x65005-ORIGIN
P_00065005:
    .byte 0xff
    .org 0x65006-ORIGIN
P_00065006:
    .byte 0x28
    .org 0x65007-ORIGIN
P_00065007:
    .byte 0xf8
    .org 0x65008-ORIGIN
P_00065008:
    .byte 0xff
    .org 0x65009-ORIGIN
P_00065009:
    .byte 0xff
    .org 0x6500a-ORIGIN
P_0006500a:
    .byte 0x12
    .org 0x6500b-ORIGIN
P_0006500b:
    .byte 0x8c
    .org 0x6500c-ORIGIN
P_0006500c:
    .byte 0xff
    .org 0x6500d-ORIGIN
P_0006500d:
    .byte 0xff
    .org 0x6500e-ORIGIN
P_0006500e:
    .byte 0x10
    .org 0x6500f-ORIGIN
P_0006500f:
    .byte 0x82
    .org 0x65010-ORIGIN
P_00065010:
    .byte 0xff
    .org 0x65011-ORIGIN
P_00065011:
    .byte 0xff
    .org 0x65012-ORIGIN
P_00065012:
    .byte 0x24
    .org 0x65013-ORIGIN
P_00065013:
    .byte 0x70
    .org 0x65014-ORIGIN
P_00065014:
    .byte 0xff
    .org 0x65015-ORIGIN
P_00065015:
    .byte 0xff
    .org 0x65016-ORIGIN
P_00065016:
    .byte 0x42
    .org 0x65017-ORIGIN
P_00065017:
    .byte 0x4c
    .org 0x65018-ORIGIN
P_00065018:
    .byte 0x00
    .org 0x65019-ORIGIN
P_00065019:
    .byte 0x00
    .org 0x6501a-ORIGIN
P_0006501a:
    .byte 0x94
    .org 0x6501b-ORIGIN
P_0006501b:
    .byte 0x56
    .org 0x6501c-ORIGIN
P_0006501c:
    .byte 0x00
    .org 0x6501d-ORIGIN
P_0006501d:
    .byte 0x02
    .org 0x6501e-ORIGIN
P_0006501e:
    .byte 0x1c
    .org 0x6501f-ORIGIN
P_0006501f:
    .byte 0xe0
    .org 0xbdc66-ORIGIN
L_000bdc66:
    mov.l r13,@-r15
    .org 0xbdc68-ORIGIN
L_000bdc68:
    mov.l r14,@-r15
    .org 0xbdc6a-ORIGIN
L_000bdc6a:
    sts.l pr,@-r15
    .org 0xbdc6c-ORIGIN
L_000bdc6c:
    sts.l macl,@-r15
    .org 0xbdc6e-ORIGIN
L_000bdc6e:
    add #-0xc,r15
    .org 0xbdc70-ORIGIN
L_000bdc70:
    mov.l P_000bdd5c,r6
    .org 0xbdc72-ORIGIN
L_000bdc72:
    mov.b @r6,r0
    .org 0xbdc74-ORIGIN
L_000bdc74:
    tst #0x10,r0
    .org 0xbdc76-ORIGIN
L_000bdc76:
    bt L_000bdcda
    .org 0xbdc78-ORIGIN
L_000bdc78:
    mov.l P_000bdd60,r6
    .org 0xbdc7a-ORIGIN
L_000bdc7a:
    mov.b @r6,r0
    .org 0xbdc7c-ORIGIN
L_000bdc7c:
    tst #0x2,r0
    .org 0xbdc7e-ORIGIN
L_000bdc7e:
    bt L_000bdcda
    .org 0xbdc80-ORIGIN
L_000bdc80:
    tst #0x1,r0
    .org 0xbdc82-ORIGIN
L_000bdc82:
    bf L_000bdcc4
    .org 0xbdc84-ORIGIN
L_000bdc84:
    mov.l P_000bdd64,r6
    .org 0xbdc86-ORIGIN
L_000bdc86:
    mov #0x50,r0
    .org 0xbdc88-ORIGIN
L_000bdc88:
    mov.b @(r0,r6),r0
    .org 0xbdc8a-ORIGIN
L_000bdc8a:
    tst #0x8,r0
    .org 0xbdc8c-ORIGIN
L_000bdc8c:
    bf L_000bdc92
    .org 0xbdc8e-ORIGIN
L_000bdc8e:
    bra L_000bdecc
    .org 0xbdc90-ORIGIN
L_000bdc90:
    nop
    .org 0xbdc92-ORIGIN
L_000bdc92:
    mov.l P_000bdd68,r2
    .org 0xbdc94-ORIGIN
L_000bdc94:
    mov.w @r2,r6
    .org 0xbdc96-ORIGIN
L_000bdc96:
    extu.w r6,r6
    .org 0xbdc98-ORIGIN
L_000bdc98:
    cmp/pz r6
    .org 0xbdc9a-ORIGIN
L_000bdc9a:
    bt/s L_000bdca0
    .org 0xbdc9c-ORIGIN
L_000bdc9c:
    mov r6,r2
    .org 0xbdc9e-ORIGIN
L_000bdc9e:
    add #0x3,r2
    .org 0xbdca0-ORIGIN
L_000bdca0:
    shar r2
    .org 0xbdca2-ORIGIN
L_000bdca2:
    mov #-0x1,r5
    .org 0xbdca4-ORIGIN
L_000bdca4:
    shar r2
    .org 0xbdca6-ORIGIN
L_000bdca6:
    extu.b r5,r5
    .org 0xbdca8-ORIGIN
L_000bdca8:
    cmp/gt r5,r2
    .org 0xbdcaa-ORIGIN
L_000bdcaa:
    bf L_000bdcb0
    .org 0xbdcac-ORIGIN
L_000bdcac:
    bra L_000bdcbc
    .org 0xbdcae-ORIGIN
L_000bdcae:
    mov r5,r2
    .org 0xbdcb0-ORIGIN
L_000bdcb0:
    cmp/pz r6
    .org 0xbdcb2-ORIGIN
L_000bdcb2:
    bt/s L_000bdcb8
    .org 0xbdcb4-ORIGIN
L_000bdcb4:
    mov r6,r2
    .org 0xbdcb6-ORIGIN
L_000bdcb6:
    add #0x3,r2
    .org 0xbdcb8-ORIGIN
L_000bdcb8:
    shar r2
    .org 0xbdcba-ORIGIN
L_000bdcba:
    shar r2
    .org 0xbdcbc-ORIGIN
L_000bdcbc:
    mov.l P_000bdd58,r5
    .org 0xbdcbe-ORIGIN
L_000bdcbe:
    mov r2,r0
    .org 0xbdcc0-ORIGIN
L_000bdcc0:
    bra L_000bdecc
    .org 0xbdcc2-ORIGIN
L_000bdcc2:
    mov.b r0,@(0x2,r5)
    .org 0xbdcc4-ORIGIN
L_000bdcc4:
    mov.l P_000bdd6c,r2
    .org 0xbdcc6-ORIGIN
L_000bdcc6:
    mov.b @r2,r0
    .org 0xbdcc8-ORIGIN
L_000bdcc8:
    tst #0x2,r0
    .org 0xbdcca-ORIGIN
L_000bdcca:
    bt L_000bdcd2
    .org 0xbdccc-ORIGIN
L_000bdccc:
    mov.l P_000bdd70,r6
    .org 0xbdcce-ORIGIN
L_000bdcce:
    bra L_000bdec8
    .org 0xbdcd0-ORIGIN
L_000bdcd0:
    mov.b @r6,r0
    .org 0xbdcd2-ORIGIN
L_000bdcd2:
    mov.l P_000bdd74,r6
    .org 0xbdcd4-ORIGIN
L_000bdcd4:
    mov.w P_000bdcfa,r0
    .org 0xbdcd6-ORIGIN
L_000bdcd6:
    bra L_000bdec8
    .org 0xbdcd8-ORIGIN
L_000bdcd8:
    mov.b @(r0,r6),r0
    .org 0xbdcda-ORIGIN
L_000bdcda:
    mov.l P_000bdd78,r6
    .org 0xbdcdc-ORIGIN
L_000bdcdc:
    mov.b @(0x3,r6),r0
    .org 0xbdcde-ORIGIN
L_000bdcde:
    tst #0x40,r0
    .org 0xbdce0-ORIGIN
L_000bdce0:
    bf L_000bdd80
    .org 0xbdce2-ORIGIN
L_000bdce2:
    mov.l P_000bdd78,r6
    .org 0xbdce4-ORIGIN
L_000bdce4:
    mov #0x23,r0
    .org 0xbdce6-ORIGIN
L_000bdce6:
    mov.b @(r0,r6),r0
    .org 0xbdce8-ORIGIN
L_000bdce8:
    tst #0x2,r0
    .org 0xbdcea-ORIGIN
L_000bdcea:
    bt L_000bdcf6
    .org 0xbdcec-ORIGIN
L_000bdcec:
    mov.l P_000bdd7c,r6
    .org 0xbdcee-ORIGIN
L_000bdcee:
    mov #0x51,r0
    .org 0xbdcf0-ORIGIN
L_000bdcf0:
    mov.b @(r0,r6),r0
    .org 0xbdcf2-ORIGIN
L_000bdcf2:
    tst #0x1,r0
    .org 0xbdcf4-ORIGIN
L_000bdcf4:
    bf L_000bdd80
    .org 0xbdcf6-ORIGIN
L_000bdcf6:
    bra L_000bdec8
    .org 0xbdcf8-ORIGIN
L_000bdcf8:
    mov #-0x80,r0
    .org 0xbdcfa-ORIGIN
P_000bdcfa:
    .byte 0x10
    .org 0xbdcfb-ORIGIN
P_000bdcfb:
    .byte 0x32
    .org 0xbdd58-ORIGIN
P_000bdd58:
    .byte 0xff
    .org 0xbdd59-ORIGIN
P_000bdd59:
    .byte 0xff
    .org 0xbdd5a-ORIGIN
P_000bdd5a:
    .byte 0x23
    .org 0xbdd5b-ORIGIN
P_000bdd5b:
    .byte 0x24
    .org 0xbdd5c-ORIGIN
P_000bdd5c:
    .byte 0x00
    .org 0xbdd5d-ORIGIN
P_000bdd5d:
    .byte 0x00
    .org 0xbdd5e-ORIGIN
P_000bdd5e:
    .byte 0x8b
    .org 0xbdd5f-ORIGIN
P_000bdd5f:
    .byte 0x34
    .org 0xbdd60-ORIGIN
P_000bdd60:
    .byte 0x00
    .org 0xbdd61-ORIGIN
P_000bdd61:
    .byte 0x00
    .org 0xbdd62-ORIGIN
P_000bdd62:
    .byte 0x8b
    .org 0xbdd63-ORIGIN
P_000bdd63:
    .byte 0x42
    .org 0xbdd64-ORIGIN
P_000bdd64:
    .byte 0xff
    .org 0xbdd65-ORIGIN
P_000bdd65:
    .byte 0xff
    .org 0xbdd66-ORIGIN
P_000bdd66:
    .byte 0x10
    .org 0xbdd67-ORIGIN
P_000bdd67:
    .byte 0x94
    .org 0xbdd68-ORIGIN
P_000bdd68:
    .byte 0xff
    .org 0xbdd69-ORIGIN
P_000bdd69:
    .byte 0xff
    .org 0xbdd6a-ORIGIN
P_000bdd6a:
    .byte 0x10
    .org 0xbdd6b-ORIGIN
P_000bdd6b:
    .byte 0x00
    .org 0xbdd6c-ORIGIN
P_000bdd6c:
    .byte 0x00
    .org 0xbdd6d-ORIGIN
P_000bdd6d:
    .byte 0x00
    .org 0xbdd6e-ORIGIN
P_000bdd6e:
    .byte 0x86
    .org 0xbdd6f-ORIGIN
P_000bdd6f:
    .byte 0xf9
    .org 0xbdd70-ORIGIN
P_000bdd70:
    .byte 0x00
    .org 0xbdd71-ORIGIN
P_000bdd71:
    .byte 0x00
    .org 0xbdd72-ORIGIN
P_000bdd72:
    .byte 0x85
    .org 0xbdd73-ORIGIN
P_000bdd73:
    .byte 0x1d
    .org 0xbdd74-ORIGIN
P_000bdd74:
    .byte 0xff
    .org 0xbdd75-ORIGIN
P_000bdd75:
    .byte 0xff
    .org 0xbdd76-ORIGIN
P_000bdd76:
    .byte 0x45
    .org 0xbdd77-ORIGIN
P_000bdd77:
    .byte 0x58
    .org 0xbdd78-ORIGIN
P_000bdd78:
    .byte 0xff
    .org 0xbdd79-ORIGIN
P_000bdd79:
    .byte 0xff
    .org 0xbdd7a-ORIGIN
P_000bdd7a:
    .byte 0x24
    .org 0xbdd7b-ORIGIN
P_000bdd7b:
    .byte 0x68
    .org 0xbdd7c-ORIGIN
P_000bdd7c:
    .byte 0xff
    .org 0xbdd7d-ORIGIN
P_000bdd7d:
    .byte 0xff
    .org 0xbdd7e-ORIGIN
P_000bdd7e:
    .byte 0x41
    .org 0xbdd7f-ORIGIN
P_000bdd7f:
    .byte 0xa9
    .org 0xbdd80-ORIGIN
L_000bdd80:
    mov.l P_000bdfa0,r14
    .org 0xbdd82-ORIGIN
L_000bdd82:
    mov.b @(0x1,r14),r0
    .org 0xbdd84-ORIGIN
L_000bdd84:
    mov.b @r14,r2
    .org 0xbdd86-ORIGIN
L_000bdd86:
    extu.b r0,r5
    .org 0xbdd88-ORIGIN
L_000bdd88:
    extu.b r2,r4
    .org 0xbdd8a-ORIGIN
L_000bdd8a:
    cmp/ge r4,r5
    .org 0xbdd8c-ORIGIN
L_000bdd8c:
    bt L_000bdde4
    .org 0xbdd8e-ORIGIN
L_000bdd8e:
    mov.l P_000bdfa4,r2
    .org 0xbdd90-ORIGIN
L_000bdd90:
    mov.b @(0x9,r2),r0
    .org 0xbdd92-ORIGIN
L_000bdd92:
    mov.b @r14,r2
    .org 0xbdd94-ORIGIN
L_000bdd94:
    extu.b r0,r4
    .org 0xbdd96-ORIGIN
L_000bdd96:
    extu.b r2,r7
    .org 0xbdd98-ORIGIN
L_000bdd98:
    cmp/gt r7,r4
    .org 0xbdd9a-ORIGIN
L_000bdd9a:
    bt L_000bddee
    .org 0xbdd9c-ORIGIN
L_000bdd9c:
    cmp/gt r5,r4
    .org 0xbdd9e-ORIGIN
L_000bdd9e:
    bf L_000bddf6
    .org 0xbdda0-ORIGIN
L_000bdda0:
    mov.l P_000bdfa8,r13
    .org 0xbdda2-ORIGIN
L_000bdda2:
    mov.w P_000bded8,r0
    .org 0xbdda4-ORIGIN
L_000bdda4:
    mov.b @(r0,r13),r6
    .org 0xbdda6-ORIGIN
L_000bdda6:
    mov.w P_000bdeda,r0
    .org 0xbdda8-ORIGIN
L_000bdda8:
    extu.b r6,r6
    .org 0xbddaa-ORIGIN
L_000bddaa:
    mov.b @(r0,r13),r7
    .org 0xbddac-ORIGIN
L_000bddac:
    exts.b r7,r1
    .org 0xbddae-ORIGIN
L_000bddae:
    extu.b r7,r2
    .org 0xbddb0-ORIGIN
L_000bddb0:
    mov r5,r7
    .org 0xbddb2-ORIGIN
L_000bddb2:
    mov.l r2,@(0x4,r15)
    .org 0xbddb4-ORIGIN
L_000bddb4:
    extu.b r1,r3
    .org 0xbddb6-ORIGIN
L_000bddb6:
    mov.l r3,@(0x8,r15)
    .org 0xbddb8-ORIGIN
L_000bddb8:
    sub r5,r4
    .org 0xbddba-ORIGIN
L_000bddba:
    mov r2,r3
    .org 0xbddbc-ORIGIN
L_000bddbc:
    mov.b @r14,r2
    .org 0xbddbe-ORIGIN
L_000bddbe:
    sub r3,r6
    .org 0xbddc0-ORIGIN
L_000bddc0:
    mul.l r6,r4
    .org 0xbddc2-ORIGIN
L_000bddc2:
    extu.b r2,r0
    .org 0xbddc4-ORIGIN
L_000bddc4:
    sub r5,r0
    .org 0xbddc6-ORIGIN
L_000bddc6:
    mov.l P_000bdfac,r5
    .org 0xbddc8-ORIGIN
L_000bddc8:
    sts macl,r6
    .org 0xbddca-ORIGIN
L_000bddca:
    jsr @r5
    .org 0xbddcc-ORIGIN
L_000bddcc:
    mov r6,r1
    .org 0xbddce-ORIGIN
L_000bddce:
    mov.l @(0x8,r15),r6
    .org 0xbddd0-ORIGIN
L_000bddd0:
    add r6,r0
    .org 0xbddd2-ORIGIN
L_000bddd2:
    mov r0,r2
    .org 0xbddd4-ORIGIN
L_000bddd4:
    mov #-0x1,r5
    .org 0xbddd6-ORIGIN
L_000bddd6:
    extu.b r5,r5
    .org 0xbddd8-ORIGIN
L_000bddd8:
    cmp/gt r5,r2
    .org 0xbddda-ORIGIN
L_000bddda:
    bt L_000bddde
    .org 0xbdddc-ORIGIN
L_000bdddc:
    mov r2,r5
    .org 0xbddde-ORIGIN
L_000bddde:
    mov r5,r2
    .org 0xbdde0-ORIGIN
L_000bdde0:
    bra L_000bde00
    .org 0xbdde2-ORIGIN
L_000bdde2:
    mov.l r5,@r15
    .org 0xbdde4-ORIGIN
L_000bdde4:
    mov.l P_000bdfa4,r6
    .org 0xbdde6-ORIGIN
L_000bdde6:
    mov.b @(0x9,r6),r0
    .org 0xbdde8-ORIGIN
L_000bdde8:
    extu.b r0,r2
    .org 0xbddea-ORIGIN
L_000bddea:
    cmp/gt r5,r2
    .org 0xbddec-ORIGIN
L_000bddec:
    bf L_000bddf6
    .org 0xbddee-ORIGIN
L_000bddee:
    mov.l P_000bdfa8,r13
    .org 0xbddf0-ORIGIN
L_000bddf0:
    mov.w P_000bded8,r0
    .org 0xbddf2-ORIGIN
L_000bddf2:
    bra L_000bddfc
    .org 0xbddf4-ORIGIN
L_000bddf4:
    mov.b @(r0,r13),r2
    .org 0xbddf6-ORIGIN
L_000bddf6:
    mov.l P_000bdfa8,r13
    .org 0xbddf8-ORIGIN
L_000bddf8:
    mov.w P_000bdeda,r0
    .org 0xbddfa-ORIGIN
L_000bddfa:
    mov.b @(r0,r13),r2
    .org 0xbddfc-ORIGIN
L_000bddfc:
    extu.b r2,r2
    .org 0xbddfe-ORIGIN
L_000bddfe:
    mov.l r2,@r15
    .org 0xbde00-ORIGIN
L_000bde00:
    mov.w P_000bdedc,r0
    .org 0xbde02-ORIGIN
L_000bde02:
    mov.l P_000bdfb0,r5
    .org 0xbde04-ORIGIN
L_000bde04:
    mov.b r2,@(r0,r13)
    .org 0xbde06-ORIGIN
L_000bde06:
    mov #0x3f,r0
    .org 0xbde08-ORIGIN
L_000bde08:
    mov.b @(r0,r5),r0
    .org 0xbde0a-ORIGIN
L_000bde0a:
    tst #0x2,r0
    .org 0xbde0c-ORIGIN
L_000bde0c:
    bt L_000bde9c
    .org 0xbde0e-ORIGIN
L_000bde0e:
    mov.l P_000bdfb4,r5
    .org 0xbde10-ORIGIN
L_000bde10:
    mov.b @(0x2,r5),r0
    .org 0xbde12-ORIGIN
L_000bde12:
    extu.b r0,r4
    .org 0xbde14-ORIGIN
L_000bde14:
    mov.w P_000bdede,r0
    .org 0xbde16-ORIGIN
L_000bde16:
    mov.b @(r0,r13),r5
    .org 0xbde18-ORIGIN
L_000bde18:
    extu.b r5,r5
    .org 0xbde1a-ORIGIN
L_000bde1a:
    cmp/ge r5,r4
    .org 0xbde1c-ORIGIN
L_000bde1c:
    bt L_000bde9a
    .org 0xbde1e-ORIGIN
L_000bde1e:
    mov.l P_000bdfb0,r6
    .org 0xbde20-ORIGIN
L_000bde20:
    mov #0x13,r0
    .org 0xbde22-ORIGIN
L_000bde22:
    mov.b @(r0,r6),r0
    .org 0xbde24-ORIGIN
L_000bde24:
    tst #0x2,r0
    .org 0xbde26-ORIGIN
L_000bde26:
    bt L_000bde9a
    .org 0xbde28-ORIGIN
L_000bde28:
    mov.w P_000bdee0,r0
    .org 0xbde2a-ORIGIN
L_000bde2a:
    mov.b @(r0,r13),r2
    .org 0xbde2c-ORIGIN
L_000bde2c:
    tst r2,r2
    .org 0xbde2e-ORIGIN
L_000bde2e:
    bt L_000bde9a
    .org 0xbde30-ORIGIN
L_000bde30:
    mov.l P_000bdfb8,r7
    .org 0xbde32-ORIGIN
L_000bde32:
    mov #-0x7c,r0
    .org 0xbde34-ORIGIN
L_000bde34:
    extu.b r0,r0
    .org 0xbde36-ORIGIN
L_000bde36:
    mov.b @(r0,r7),r2
    .org 0xbde38-ORIGIN
L_000bde38:
    tst r2,r2
    .org 0xbde3a-ORIGIN
L_000bde3a:
    bf L_000bde96
    .org 0xbde3c-ORIGIN
L_000bde3c:
    mov r4,r2
    .org 0xbde3e-ORIGIN
L_000bde3e:
    add #0x1,r2
    .org 0xbde40-ORIGIN
L_000bde40:
    mov.l r2,@r15
    .org 0xbde42-ORIGIN
L_000bde42:
    mov.l P_000bdfbc,r2
    .org 0xbde44-ORIGIN
L_000bde44:
    mov.b @r2,r0
    .org 0xbde46-ORIGIN
L_000bde46:
    tst #0x1,r0
    .org 0xbde48-ORIGIN
L_000bde48:
    bt L_000bde78
    .org 0xbde4a-ORIGIN
L_000bde4a:
    mov.l P_000bdfc0,r2
    .org 0xbde4c-ORIGIN
L_000bde4c:
    mov #-0x8,r0
    .org 0xbde4e-ORIGIN
L_000bde4e:
    extu.b r0,r0
    .org 0xbde50-ORIGIN
L_000bde50:
    mov.b @(r0,r2),r6
    .org 0xbde52-ORIGIN
L_000bde52:
    mov #0x14,r0
    .org 0xbde54-ORIGIN
L_000bde54:
    extu.b r6,r5
    .org 0xbde56-ORIGIN
L_000bde56:
    mov.l P_000bdfac,r6
    .org 0xbde58-ORIGIN
L_000bde58:
    shll2 r5
    .org 0xbde5a-ORIGIN
L_000bde5a:
    shll2 r5
    .org 0xbde5c-ORIGIN
L_000bde5c:
    shll r5
    .org 0xbde5e-ORIGIN
L_000bde5e:
    jsr @r6
    .org 0xbde60-ORIGIN
L_000bde60:
    mov r5,r1
    .org 0xbde62-ORIGIN
L_000bde62:
    mov #-0x1,r5
    .org 0xbde64-ORIGIN
L_000bde64:
    extu.w r0,r4
    .org 0xbde66-ORIGIN
L_000bde66:
    extu.b r5,r5
    .org 0xbde68-ORIGIN
L_000bde68:
    cmp/gt r5,r4
    .org 0xbde6a-ORIGIN
L_000bde6a:
    bf L_000bde6e
    .org 0xbde6c-ORIGIN
L_000bde6c:
    mov r5,r4
    .org 0xbde6e-ORIGIN
L_000bde6e:
    mov r4,r5
    .org 0xbde70-ORIGIN
L_000bde70:
    mov.l P_000bdfc4,r4
    .org 0xbde72-ORIGIN
L_000bde72:
    mov.l P_000bdfc8,r6
    .org 0xbde74-ORIGIN
L_000bde74:
    bra L_000bde82
    .org 0xbde76-ORIGIN
L_000bde76:
    extu.b r5,r5
    .org 0xbde78-ORIGIN
L_000bde78:
    mov.l P_000bdfa4,r3
    .org 0xbde7a-ORIGIN
L_000bde7a:
    mov.l P_000bdfcc,r4
    .org 0xbde7c-ORIGIN
L_000bde7c:
    mov.b @(0x7,r3),r0
    .org 0xbde7e-ORIGIN
L_000bde7e:
    mov.l P_000bdfc8,r6
    .org 0xbde80-ORIGIN
L_000bde80:
    extu.b r0,r5
    .org 0xbde82-ORIGIN
L_000bde82:
    jsr @r6
    .org 0xbde84-ORIGIN
L_000bde84:
    nop
    .org 0xbde86-ORIGIN
L_000bde86:
    mov r0,r5
    .org 0xbde88-ORIGIN
L_000bde88:
    mov.w P_000bdee0,r0
    .org 0xbde8a-ORIGIN
L_000bde8a:
    mov.l P_000bdfb8,r7
    .org 0xbde8c-ORIGIN
L_000bde8c:
    mov.b r5,@(r0,r13)
    .org 0xbde8e-ORIGIN
L_000bde8e:
    mov #-0x7c,r0
    .org 0xbde90-ORIGIN
L_000bde90:
    extu.b r0,r0
    .org 0xbde92-ORIGIN
L_000bde92:
    bra L_000bde9c
    .org 0xbde94-ORIGIN
L_000bde94:
    mov.b r5,@(r0,r7)
    .org 0xbde96-ORIGIN
L_000bde96:
    bra L_000bde9c
    .org 0xbde98-ORIGIN
L_000bde98:
    mov.l r4,@r15
    .org 0xbde9a-ORIGIN
L_000bde9a:
    mov.l r5,@r15
    .org 0xbde9c-ORIGIN
L_000bde9c:
    mov.l P_000bdfd0,r5
    .org 0xbde9e-ORIGIN
L_000bde9e:
    mov #0x51,r0
    .org 0xbdea0-ORIGIN
L_000bdea0:
    mov.b @(r0,r5),r0
    .org 0xbdea2-ORIGIN
L_000bdea2:
    tst #0x1,r0
    .org 0xbdea4-ORIGIN
L_000bdea4:
    bt L_000bdec6
    .org 0xbdea6-ORIGIN
L_000bdea6:
    mov.w P_000bdee2,r0
    .org 0xbdea8-ORIGIN
L_000bdea8:
    mov #-0x1,r5
    .org 0xbdeaa-ORIGIN
L_000bdeaa:
    mov.l @r15,r2
    .org 0xbdeac-ORIGIN
L_000bdeac:
    extu.b r5,r5
    .org 0xbdeae-ORIGIN
L_000bdeae:
    mov.b @(r0,r13),r4
    .org 0xbdeb0-ORIGIN
L_000bdeb0:
    mov r2,r6
    .org 0xbdeb2-ORIGIN
L_000bdeb2:
    add r4,r6
    .org 0xbdeb4-ORIGIN
L_000bdeb4:
    cmp/gt r5,r6
    .org 0xbdeb6-ORIGIN
L_000bdeb6:
    bt L_000bdebc
    .org 0xbdeb8-ORIGIN
L_000bdeb8:
    add r4,r2
    .org 0xbdeba-ORIGIN
L_000bdeba:
    mov r2,r5
    .org 0xbdebc-ORIGIN
L_000bdebc:
    cmp/pz r5
    .org 0xbdebe-ORIGIN
L_000bdebe:
    bt/s L_000bdec4
    .org 0xbdec0-ORIGIN
L_000bdec0:
    mov r5,r2
    .org 0xbdec2-ORIGIN
L_000bdec2:
    mov #0x0,r2
    .org 0xbdec4-ORIGIN
L_000bdec4:
    mov.l r2,@r15
    .org 0xbdec6-ORIGIN
L_000bdec6:
    mov.l @r15,r0
    .org 0xbdec8-ORIGIN
L_000bdec8:
    mov.l P_000bdfb4,r5
    .org 0xbdeca-ORIGIN
L_000bdeca:
    mov.b r0,@(0x2,r5)
    .org 0xbdecc-ORIGIN
L_000bdecc:
    add #0xc,r15
    .org 0xbdece-ORIGIN
L_000bdece:
    lds.l @r15+,macl
    .org 0xbded0-ORIGIN
L_000bded0:
    lds.l @r15+,pr
    .org 0xbded2-ORIGIN
L_000bded2:
    mov.l @r15+,r14
    .org 0xbded4-ORIGIN
L_000bded4:
    rts
    .org 0xbded6-ORIGIN
L_000bded6:
    mov.l @r15+,r13
    .org 0xbded8-ORIGIN
P_000bded8:
    .byte 0x09
    .org 0xbded9-ORIGIN
P_000bded9:
    .byte 0xd0
    .org 0xbdeda-ORIGIN
P_000bdeda:
    .byte 0x09
    .org 0xbdedb-ORIGIN
P_000bdedb:
    .byte 0xd2
    .org 0xbdedc-ORIGIN
P_000bdedc:
    .byte 0x09
    .org 0xbdedd-ORIGIN
P_000bdedd:
    .byte 0x62
    .org 0xbdede-ORIGIN
P_000bdede:
    .byte 0x02
    .org 0xbdedf-ORIGIN
P_000bdedf:
    .byte 0xc7
    .org 0xbdee0-ORIGIN
P_000bdee0:
    .byte 0x07
    .org 0xbdee1-ORIGIN
P_000bdee1:
    .byte 0x92
    .org 0xbdee2-ORIGIN
P_000bdee2:
    .byte 0x04
    .org 0xbdee3-ORIGIN
P_000bdee3:
    .byte 0x78
    .org 0xbdfa0-ORIGIN
P_000bdfa0:
    .byte 0x00
    .org 0xbdfa1-ORIGIN
P_000bdfa1:
    .byte 0x00
    .org 0xbdfa2-ORIGIN
P_000bdfa2:
    .byte 0x8d
    .org 0xbdfa3-ORIGIN
P_000bdfa3:
    .byte 0x2d
    .org 0xbdfa4-ORIGIN
P_000bdfa4:
    .byte 0xff
    .org 0xbdfa5-ORIGIN
P_000bdfa5:
    .byte 0xff
    .org 0xbdfa6-ORIGIN
P_000bdfa6:
    .byte 0x10
    .org 0xbdfa7-ORIGIN
P_000bdfa7:
    .byte 0x68
    .org 0xbdfa8-ORIGIN
P_000bdfa8:
    .byte 0xff
    .org 0xbdfa9-ORIGIN
P_000bdfa9:
    .byte 0xff
    .org 0xbdfaa-ORIGIN
P_000bdfaa:
    .byte 0x12
    .org 0xbdfab-ORIGIN
P_000bdfab:
    .byte 0x8c
    .org 0xbdfac-ORIGIN
P_000bdfac:
    .byte 0x00
    .org 0xbdfad-ORIGIN
P_000bdfad:
    .byte 0x02
    .org 0xbdfae-ORIGIN
P_000bdfae:
    .byte 0x1b
    .org 0xbdfaf-ORIGIN
P_000bdfaf:
    .byte 0xbc
    .org 0xbdfb0-ORIGIN
P_000bdfb0:
    .byte 0xff
    .org 0xbdfb1-ORIGIN
P_000bdfb1:
    .byte 0xff
    .org 0xbdfb2-ORIGIN
P_000bdfb2:
    .byte 0x24
    .org 0xbdfb3-ORIGIN
P_000bdfb3:
    .byte 0x68
    .org 0xbdfb4-ORIGIN
P_000bdfb4:
    .byte 0xff
    .org 0xbdfb5-ORIGIN
P_000bdfb5:
    .byte 0xff
    .org 0xbdfb6-ORIGIN
P_000bdfb6:
    .byte 0x23
    .org 0xbdfb7-ORIGIN
P_000bdfb7:
    .byte 0x24
    .org 0xbdfb8-ORIGIN
P_000bdfb8:
    .byte 0xff
    .org 0xbdfb9-ORIGIN
P_000bdfb9:
    .byte 0xff
    .org 0xbdfba-ORIGIN
P_000bdfba:
    .byte 0x25
    .org 0xbdfbb-ORIGIN
P_000bdfbb:
    .byte 0x6a
    .org 0xbdfbc-ORIGIN
P_000bdfbc:
    .byte 0x00
    .org 0xbdfbd-ORIGIN
P_000bdfbd:
    .byte 0x00
    .org 0xbdfbe-ORIGIN
P_000bdfbe:
    .byte 0x86
    .org 0xbdfbf-ORIGIN
P_000bdfbf:
    .byte 0x16
    .org 0xbdfc0-ORIGIN
P_000bdfc0:
    .byte 0xff
    .org 0xbdfc1-ORIGIN
P_000bdfc1:
    .byte 0xff
    .org 0xbdfc2-ORIGIN
P_000bdfc2:
    .byte 0x26
    .org 0xbdfc3-ORIGIN
P_000bdfc3:
    .byte 0x7a
    .org 0xbdfc4-ORIGIN
P_000bdfc4:
    .byte 0x00
    .org 0xbdfc5-ORIGIN
P_000bdfc5:
    .byte 0x01
    .org 0xbdfc6-ORIGIN
P_000bdfc6:
    .byte 0x2e
    .org 0xbdfc7-ORIGIN
P_000bdfc7:
    .byte 0xfe
    .org 0xbdfc8-ORIGIN
P_000bdfc8:
    .byte 0x00
    .org 0xbdfc9-ORIGIN
P_000bdfc9:
    .byte 0x02
    .org 0xbdfca-ORIGIN
P_000bdfca:
    .byte 0x63
    .org 0xbdfcb-ORIGIN
P_000bdfcb:
    .byte 0x70
    .org 0xbdfcc-ORIGIN
P_000bdfcc:
    .byte 0x00
    .org 0xbdfcd-ORIGIN
P_000bdfcd:
    .byte 0x01
    .org 0xbdfce-ORIGIN
P_000bdfce:
    .byte 0x2f
    .org 0xbdfcf-ORIGIN
P_000bdfcf:
    .byte 0x06
    .org 0xbdfd0-ORIGIN
P_000bdfd0:
    .byte 0xff
    .org 0xbdfd1-ORIGIN
P_000bdfd1:
    .byte 0xff
    .org 0xbdfd2-ORIGIN
P_000bdfd2:
    .byte 0x41
    .org 0xbdfd3-ORIGIN
P_000bdfd3:
    .byte 0xa9
