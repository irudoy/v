! Exact natural injection start-delay publication and genuine helpers.
    .section .text
    .balign 4
    .org 0x83ea - 0x83e8
P_83ea: .byte 0x1e
    .org 0x21bbc - 0x83e8
L_21bbc:
    mov.l r2,@-r15
    .org 0x21bbe - 0x83e8
L_21bbe:
    tst r0,r0
    .org 0x21bc0 - 0x83e8
L_21bc0:
    bt L_21c70
    .org 0x21bc2 - 0x83e8
L_21bc2:
    mov.l r3,@-r15
    .org 0x21bc4 - 0x83e8
L_21bc4:
    div0s r0,r1
    .org 0x21bc6 - 0x83e8
L_21bc6:
    movt r3
    .org 0x21bc8 - 0x83e8
L_21bc8:
    cmp/pl r0
    .org 0x21bca - 0x83e8
L_21bca:
    bt L_21bd0
    .org 0x21bcc - 0x83e8
L_21bcc:
    add #-0x1,r0
    .org 0x21bce - 0x83e8
L_21bce:
    not r0,r0
    .org 0x21bd0 - 0x83e8
L_21bd0:
    cmp/pl r1
    .org 0x21bd2 - 0x83e8
L_21bd2:
    bt L_21bd8
    .org 0x21bd4 - 0x83e8
L_21bd4:
    add #-0x1,r1
    .org 0x21bd6 - 0x83e8
L_21bd6:
    not r1,r1
    .org 0x21bd8 - 0x83e8
L_21bd8:
    extu.w r0,r2
    .org 0x21bda - 0x83e8
L_21bda:
    cmp/eq r2,r0
    .org 0x21bdc - 0x83e8
L_21bdc:
    bf L_21c7c
    .org 0x21bde - 0x83e8
L_21bde:
    div0u
    .org 0x21be0 - 0x83e8
L_21be0:
    shll8 r0
    .org 0x21be2 - 0x83e8
L_21be2:
    cmp/hi r1,r0
    .org 0x21be4 - 0x83e8
L_21be4:
    bf L_21c08
    .org 0x21be6 - 0x83e8
L_21be6:
    div1 r0,r1
    .org 0x21be8 - 0x83e8
L_21be8:
    div1 r0,r1
    .org 0x21bea - 0x83e8
L_21bea:
    div1 r0,r1
    .org 0x21bec - 0x83e8
L_21bec:
    div1 r0,r1
    .org 0x21bee - 0x83e8
L_21bee:
    div1 r0,r1
    .org 0x21bf0 - 0x83e8
L_21bf0:
    div1 r0,r1
    .org 0x21bf2 - 0x83e8
L_21bf2:
    div1 r0,r1
    .org 0x21bf4 - 0x83e8
L_21bf4:
    div1 r0,r1
    .org 0x21bf6 - 0x83e8
L_21bf6:
    rotcl r1
    .org 0x21bf8 - 0x83e8
L_21bf8:
    extu.b r1,r0
    .org 0x21bfa - 0x83e8
L_21bfa:
    rotcr r3
    .org 0x21bfc - 0x83e8
L_21bfc:
    bf L_21c02
    .org 0x21bfe - 0x83e8
L_21bfe:
    not r0,r0
    .org 0x21c00 - 0x83e8
L_21c00:
    add #0x1,r0
    .org 0x21c02 - 0x83e8
L_21c02:
    mov.l @r15+,r3
    .org 0x21c04 - 0x83e8
L_21c04:
    rts
    .org 0x21c06 - 0x83e8
L_21c06:
    mov.l @r15+,r2
    .org 0x21c08 - 0x83e8
L_21c08:
    mov.l r4,@-r15
    .org 0x21c0a - 0x83e8
L_21c0a:
    extu.w r1,r4
    .org 0x21c0c - 0x83e8
L_21c0c:
    shll8 r0
    .org 0x21c0e - 0x83e8
L_21c0e:
    shlr16 r1
    .org 0x21c10 - 0x83e8
L_21c10:
    div1 r0,r1
    .org 0x21c12 - 0x83e8
L_21c12:
    div1 r0,r1
    .org 0x21c14 - 0x83e8
L_21c14:
    div1 r0,r1
    .org 0x21c16 - 0x83e8
L_21c16:
    div1 r0,r1
    .org 0x21c18 - 0x83e8
L_21c18:
    div1 r0,r1
    .org 0x21c1a - 0x83e8
L_21c1a:
    div1 r0,r1
    .org 0x21c1c - 0x83e8
L_21c1c:
    div1 r0,r1
    .org 0x21c1e - 0x83e8
L_21c1e:
    div1 r0,r1
    .org 0x21c20 - 0x83e8
L_21c20:
    div1 r0,r1
    .org 0x21c22 - 0x83e8
L_21c22:
    div1 r0,r1
    .org 0x21c24 - 0x83e8
L_21c24:
    div1 r0,r1
    .org 0x21c26 - 0x83e8
L_21c26:
    div1 r0,r1
    .org 0x21c28 - 0x83e8
L_21c28:
    div1 r0,r1
    .org 0x21c2a - 0x83e8
L_21c2a:
    div1 r0,r1
    .org 0x21c2c - 0x83e8
L_21c2c:
    div1 r0,r1
    .org 0x21c2e - 0x83e8
L_21c2e:
    div1 r0,r1
    .org 0x21c30 - 0x83e8
L_21c30:
    extu.w r1,r2
    .org 0x21c32 - 0x83e8
L_21c32:
    xor r2,r1
    .org 0x21c34 - 0x83e8
L_21c34:
    addc r2,r2
    .org 0x21c36 - 0x83e8
L_21c36:
    shll16 r2
    .org 0x21c38 - 0x83e8
L_21c38:
    add r4,r1
    .org 0x21c3a - 0x83e8
L_21c3a:
    div1 r0,r1
    .org 0x21c3c - 0x83e8
L_21c3c:
    div1 r0,r1
    .org 0x21c3e - 0x83e8
L_21c3e:
    div1 r0,r1
    .org 0x21c40 - 0x83e8
L_21c40:
    div1 r0,r1
    .org 0x21c42 - 0x83e8
L_21c42:
    div1 r0,r1
    .org 0x21c44 - 0x83e8
L_21c44:
    div1 r0,r1
    .org 0x21c46 - 0x83e8
L_21c46:
    div1 r0,r1
    .org 0x21c48 - 0x83e8
L_21c48:
    div1 r0,r1
    .org 0x21c4a - 0x83e8
L_21c4a:
    div1 r0,r1
    .org 0x21c4c - 0x83e8
L_21c4c:
    div1 r0,r1
    .org 0x21c4e - 0x83e8
L_21c4e:
    div1 r0,r1
    .org 0x21c50 - 0x83e8
L_21c50:
    div1 r0,r1
    .org 0x21c52 - 0x83e8
L_21c52:
    div1 r0,r1
    .org 0x21c54 - 0x83e8
L_21c54:
    div1 r0,r1
    .org 0x21c56 - 0x83e8
L_21c56:
    div1 r0,r1
    .org 0x21c58 - 0x83e8
L_21c58:
    div1 r0,r1
    .org 0x21c5a - 0x83e8
L_21c5a:
    rotcl r1
    .org 0x21c5c - 0x83e8
L_21c5c:
    extu.w r1,r0
    .org 0x21c5e - 0x83e8
L_21c5e:
    add r2,r0
    .org 0x21c60 - 0x83e8
L_21c60:
    rotcr r3
    .org 0x21c62 - 0x83e8
L_21c62:
    bf L_21c68
    .org 0x21c64 - 0x83e8
L_21c64:
    not r0,r0
    .org 0x21c66 - 0x83e8
L_21c66:
    add #0x1,r0
    .org 0x21c68 - 0x83e8
L_21c68:
    mov.l @r15+,r4
    .org 0x21c6a - 0x83e8
L_21c6a:
    mov.l @r15+,r3
    .org 0x21c6c - 0x83e8
L_21c6c:
    rts
    .org 0x21c6e - 0x83e8
L_21c6e:
    mov.l @r15+,r2
    .org 0x21c70 - 0x83e8
L_21c70:
    mov.l P_21cd8,r1
    .org 0x21c72 - 0x83e8
L_21c72:
    mov.l P_21cdc,r2
    .org 0x21c74 - 0x83e8
L_21c74:
    mov.l r2,@r1
    .org 0x21c76 - 0x83e8
L_21c76:
    mov #0x0,r0
    .org 0x21c78 - 0x83e8
L_21c78:
    rts
    .org 0x21c7a - 0x83e8
L_21c7a:
    mov.l @r15+,r2
    .org 0x21c7c - 0x83e8
L_21c7c:
    div0u
    .org 0x21c7e - 0x83e8
L_21c7e:
    extu.w r1,r2
    .org 0x21c80 - 0x83e8
L_21c80:
    shll16 r2
    .org 0x21c82 - 0x83e8
L_21c82:
    shlr16 r1
    .org 0x21c84 - 0x83e8
L_21c84:
    rotcl r2
    .org 0x21c86 - 0x83e8
L_21c86:
    div1 r0,r1
    .org 0x21c88 - 0x83e8
L_21c88:
    rotcl r2
    .org 0x21c8a - 0x83e8
L_21c8a:
    div1 r0,r1
    .org 0x21c8c - 0x83e8
L_21c8c:
    rotcl r2
    .org 0x21c8e - 0x83e8
L_21c8e:
    div1 r0,r1
    .org 0x21c90 - 0x83e8
L_21c90:
    rotcl r2
    .org 0x21c92 - 0x83e8
L_21c92:
    div1 r0,r1
    .org 0x21c94 - 0x83e8
L_21c94:
    rotcl r2
    .org 0x21c96 - 0x83e8
L_21c96:
    div1 r0,r1
    .org 0x21c98 - 0x83e8
L_21c98:
    rotcl r2
    .org 0x21c9a - 0x83e8
L_21c9a:
    div1 r0,r1
    .org 0x21c9c - 0x83e8
L_21c9c:
    rotcl r2
    .org 0x21c9e - 0x83e8
L_21c9e:
    div1 r0,r1
    .org 0x21ca0 - 0x83e8
L_21ca0:
    rotcl r2
    .org 0x21ca2 - 0x83e8
L_21ca2:
    div1 r0,r1
    .org 0x21ca4 - 0x83e8
L_21ca4:
    rotcl r2
    .org 0x21ca6 - 0x83e8
L_21ca6:
    div1 r0,r1
    .org 0x21ca8 - 0x83e8
L_21ca8:
    rotcl r2
    .org 0x21caa - 0x83e8
L_21caa:
    div1 r0,r1
    .org 0x21cac - 0x83e8
L_21cac:
    rotcl r2
    .org 0x21cae - 0x83e8
L_21cae:
    div1 r0,r1
    .org 0x21cb0 - 0x83e8
L_21cb0:
    rotcl r2
    .org 0x21cb2 - 0x83e8
L_21cb2:
    div1 r0,r1
    .org 0x21cb4 - 0x83e8
L_21cb4:
    rotcl r2
    .org 0x21cb6 - 0x83e8
L_21cb6:
    div1 r0,r1
    .org 0x21cb8 - 0x83e8
L_21cb8:
    rotcl r2
    .org 0x21cba - 0x83e8
L_21cba:
    div1 r0,r1
    .org 0x21cbc - 0x83e8
L_21cbc:
    rotcl r2
    .org 0x21cbe - 0x83e8
L_21cbe:
    div1 r0,r1
    .org 0x21cc0 - 0x83e8
L_21cc0:
    rotcl r2
    .org 0x21cc2 - 0x83e8
L_21cc2:
    div1 r0,r1
    .org 0x21cc4 - 0x83e8
L_21cc4:
    rotcl r2
    .org 0x21cc6 - 0x83e8
L_21cc6:
    mov r2,r0
    .org 0x21cc8 - 0x83e8
L_21cc8:
    rotcr r3
    .org 0x21cca - 0x83e8
L_21cca:
    bf L_21cd0
    .org 0x21ccc - 0x83e8
L_21ccc:
    not r0,r0
    .org 0x21cce - 0x83e8
L_21cce:
    add #0x1,r0
    .org 0x21cd0 - 0x83e8
L_21cd0:
    mov.l @r15+,r3
    .org 0x21cd2 - 0x83e8
L_21cd2:
    rts
    .org 0x21cd4 - 0x83e8
L_21cd4:
    mov.l @r15+,r2
    .org 0x21cd8 - 0x83e8
P_21cd8: .long 0xffff9818
    .org 0x21cdc - 0x83e8
P_21cdc: .long 0x0000044e
    .org 0x21e14 - 0x83e8
L_21e14:
    mov.l r2,@-r15
    .org 0x21e16 - 0x83e8
L_21e16:
    tst r0,r0
    .org 0x21e18 - 0x83e8
L_21e18:
    bt L_21ed0
    .org 0x21e1a - 0x83e8
L_21e1a:
    mov.l r3,@-r15
    .org 0x21e1c - 0x83e8
L_21e1c:
    mov r1,r3
    .org 0x21e1e - 0x83e8
L_21e1e:
    rotcl r3
    .org 0x21e20 - 0x83e8
L_21e20:
    movt r3
    .org 0x21e22 - 0x83e8
L_21e22:
    cmp/pl r0
    .org 0x21e24 - 0x83e8
L_21e24:
    bt L_21e2a
    .org 0x21e26 - 0x83e8
L_21e26:
    add #-0x1,r0
    .org 0x21e28 - 0x83e8
L_21e28:
    not r0,r0
    .org 0x21e2a - 0x83e8
L_21e2a:
    cmp/pl r1
    .org 0x21e2c - 0x83e8
L_21e2c:
    bt L_21e32
    .org 0x21e2e - 0x83e8
L_21e2e:
    add #-0x1,r1
    .org 0x21e30 - 0x83e8
L_21e30:
    not r1,r1
    .org 0x21e32 - 0x83e8
L_21e32:
    extu.w r0,r2
    .org 0x21e34 - 0x83e8
L_21e34:
    cmp/eq r2,r0
    .org 0x21e36 - 0x83e8
L_21e36:
    bf L_21edc
    .org 0x21e38 - 0x83e8
L_21e38:
    div0u
    .org 0x21e3a - 0x83e8
L_21e3a:
    shll8 r0
    .org 0x21e3c - 0x83e8
L_21e3c:
    cmp/hi r1,r0
    .org 0x21e3e - 0x83e8
L_21e3e:
    bf L_21e68
    .org 0x21e40 - 0x83e8
L_21e40:
    div1 r0,r1
    .org 0x21e42 - 0x83e8
L_21e42:
    div1 r0,r1
    .org 0x21e44 - 0x83e8
L_21e44:
    div1 r0,r1
    .org 0x21e46 - 0x83e8
L_21e46:
    div1 r0,r1
    .org 0x21e48 - 0x83e8
L_21e48:
    div1 r0,r1
    .org 0x21e4a - 0x83e8
L_21e4a:
    div1 r0,r1
    .org 0x21e4c - 0x83e8
L_21e4c:
    div1 r0,r1
    .org 0x21e4e - 0x83e8
L_21e4e:
    div1 r0,r1
    .org 0x21e50 - 0x83e8
L_21e50:
    mov r1,r2
    .org 0x21e52 - 0x83e8
L_21e52:
    bt L_21e56
    .org 0x21e54 - 0x83e8
L_21e54:
    add r0,r2
    .org 0x21e56 - 0x83e8
L_21e56:
    shlr8 r2
    .org 0x21e58 - 0x83e8
L_21e58:
    mov r2,r0
    .org 0x21e5a - 0x83e8
L_21e5a:
    rotcr r3
    .org 0x21e5c - 0x83e8
L_21e5c:
    bf L_21e62
    .org 0x21e5e - 0x83e8
L_21e5e:
    not r0,r0
    .org 0x21e60 - 0x83e8
L_21e60:
    add #0x1,r0
    .org 0x21e62 - 0x83e8
L_21e62:
    mov.l @r15+,r3
    .org 0x21e64 - 0x83e8
L_21e64:
    rts
    .org 0x21e66 - 0x83e8
L_21e66:
    mov.l @r15+,r2
    .org 0x21e68 - 0x83e8
L_21e68:
    mov.l r4,@-r15
    .org 0x21e6a - 0x83e8
L_21e6a:
    extu.w r1,r4
    .org 0x21e6c - 0x83e8
L_21e6c:
    shll8 r0
    .org 0x21e6e - 0x83e8
L_21e6e:
    shlr16 r1
    .org 0x21e70 - 0x83e8
L_21e70:
    div1 r0,r1
    .org 0x21e72 - 0x83e8
L_21e72:
    div1 r0,r1
    .org 0x21e74 - 0x83e8
L_21e74:
    div1 r0,r1
    .org 0x21e76 - 0x83e8
L_21e76:
    div1 r0,r1
    .org 0x21e78 - 0x83e8
L_21e78:
    div1 r0,r1
    .org 0x21e7a - 0x83e8
L_21e7a:
    div1 r0,r1
    .org 0x21e7c - 0x83e8
L_21e7c:
    div1 r0,r1
    .org 0x21e7e - 0x83e8
L_21e7e:
    div1 r0,r1
    .org 0x21e80 - 0x83e8
L_21e80:
    div1 r0,r1
    .org 0x21e82 - 0x83e8
L_21e82:
    div1 r0,r1
    .org 0x21e84 - 0x83e8
L_21e84:
    div1 r0,r1
    .org 0x21e86 - 0x83e8
L_21e86:
    div1 r0,r1
    .org 0x21e88 - 0x83e8
L_21e88:
    div1 r0,r1
    .org 0x21e8a - 0x83e8
L_21e8a:
    div1 r0,r1
    .org 0x21e8c - 0x83e8
L_21e8c:
    div1 r0,r1
    .org 0x21e8e - 0x83e8
L_21e8e:
    div1 r0,r1
    .org 0x21e90 - 0x83e8
L_21e90:
    extu.w r1,r2
    .org 0x21e92 - 0x83e8
L_21e92:
    xor r2,r1
    .org 0x21e94 - 0x83e8
L_21e94:
    add r4,r1
    .org 0x21e96 - 0x83e8
L_21e96:
    div1 r0,r1
    .org 0x21e98 - 0x83e8
L_21e98:
    div1 r0,r1
    .org 0x21e9a - 0x83e8
L_21e9a:
    div1 r0,r1
    .org 0x21e9c - 0x83e8
L_21e9c:
    div1 r0,r1
    .org 0x21e9e - 0x83e8
L_21e9e:
    div1 r0,r1
    .org 0x21ea0 - 0x83e8
L_21ea0:
    div1 r0,r1
    .org 0x21ea2 - 0x83e8
L_21ea2:
    div1 r0,r1
    .org 0x21ea4 - 0x83e8
L_21ea4:
    div1 r0,r1
    .org 0x21ea6 - 0x83e8
L_21ea6:
    div1 r0,r1
    .org 0x21ea8 - 0x83e8
L_21ea8:
    div1 r0,r1
    .org 0x21eaa - 0x83e8
L_21eaa:
    div1 r0,r1
    .org 0x21eac - 0x83e8
L_21eac:
    div1 r0,r1
    .org 0x21eae - 0x83e8
L_21eae:
    div1 r0,r1
    .org 0x21eb0 - 0x83e8
L_21eb0:
    div1 r0,r1
    .org 0x21eb2 - 0x83e8
L_21eb2:
    div1 r0,r1
    .org 0x21eb4 - 0x83e8
L_21eb4:
    div1 r0,r1
    .org 0x21eb6 - 0x83e8
L_21eb6:
    mov r1,r2
    .org 0x21eb8 - 0x83e8
L_21eb8:
    bt L_21ebc
    .org 0x21eba - 0x83e8
L_21eba:
    add r0,r2
    .org 0x21ebc - 0x83e8
L_21ebc:
    mov r2,r0
    .org 0x21ebe - 0x83e8
L_21ebe:
    shlr16 r0
    .org 0x21ec0 - 0x83e8
L_21ec0:
    rotcr r3
    .org 0x21ec2 - 0x83e8
L_21ec2:
    bf L_21ec8
    .org 0x21ec4 - 0x83e8
L_21ec4:
    not r0,r0
    .org 0x21ec6 - 0x83e8
L_21ec6:
    add #0x1,r0
    .org 0x21ec8 - 0x83e8
L_21ec8:
    mov.l @r15+,r4
    .org 0x21eca - 0x83e8
L_21eca:
    mov.l @r15+,r3
    .org 0x21ecc - 0x83e8
L_21ecc:
    rts
    .org 0x21ece - 0x83e8
L_21ece:
    mov.l @r15+,r2
    .org 0x21ed0 - 0x83e8
L_21ed0:
    mov.l P_21f38,r1
    .org 0x21ed2 - 0x83e8
L_21ed2:
    mov.l P_21f3c,r2
    .org 0x21ed4 - 0x83e8
L_21ed4:
    mov.l r2,@r1
    .org 0x21ed6 - 0x83e8
L_21ed6:
    mov #0x0,r0
    .org 0x21ed8 - 0x83e8
L_21ed8:
    rts
    .org 0x21eda - 0x83e8
L_21eda:
    mov.l @r15+,r2
    .org 0x21edc - 0x83e8
L_21edc:
    div0u
    .org 0x21ede - 0x83e8
L_21ede:
    extu.w r1,r2
    .org 0x21ee0 - 0x83e8
L_21ee0:
    shll16 r2
    .org 0x21ee2 - 0x83e8
L_21ee2:
    shlr16 r1
    .org 0x21ee4 - 0x83e8
L_21ee4:
    rotcl r2
    .org 0x21ee6 - 0x83e8
L_21ee6:
    div1 r0,r1
    .org 0x21ee8 - 0x83e8
L_21ee8:
    rotcl r2
    .org 0x21eea - 0x83e8
L_21eea:
    div1 r0,r1
    .org 0x21eec - 0x83e8
L_21eec:
    rotcl r2
    .org 0x21eee - 0x83e8
L_21eee:
    div1 r0,r1
    .org 0x21ef0 - 0x83e8
L_21ef0:
    rotcl r2
    .org 0x21ef2 - 0x83e8
L_21ef2:
    div1 r0,r1
    .org 0x21ef4 - 0x83e8
L_21ef4:
    rotcl r2
    .org 0x21ef6 - 0x83e8
L_21ef6:
    div1 r0,r1
    .org 0x21ef8 - 0x83e8
L_21ef8:
    rotcl r2
    .org 0x21efa - 0x83e8
L_21efa:
    div1 r0,r1
    .org 0x21efc - 0x83e8
L_21efc:
    rotcl r2
    .org 0x21efe - 0x83e8
L_21efe:
    div1 r0,r1
    .org 0x21f00 - 0x83e8
L_21f00:
    rotcl r2
    .org 0x21f02 - 0x83e8
L_21f02:
    div1 r0,r1
    .org 0x21f04 - 0x83e8
L_21f04:
    rotcl r2
    .org 0x21f06 - 0x83e8
L_21f06:
    div1 r0,r1
    .org 0x21f08 - 0x83e8
L_21f08:
    rotcl r2
    .org 0x21f0a - 0x83e8
L_21f0a:
    div1 r0,r1
    .org 0x21f0c - 0x83e8
L_21f0c:
    rotcl r2
    .org 0x21f0e - 0x83e8
L_21f0e:
    div1 r0,r1
    .org 0x21f10 - 0x83e8
L_21f10:
    rotcl r2
    .org 0x21f12 - 0x83e8
L_21f12:
    div1 r0,r1
    .org 0x21f14 - 0x83e8
L_21f14:
    rotcl r2
    .org 0x21f16 - 0x83e8
L_21f16:
    div1 r0,r1
    .org 0x21f18 - 0x83e8
L_21f18:
    rotcl r2
    .org 0x21f1a - 0x83e8
L_21f1a:
    div1 r0,r1
    .org 0x21f1c - 0x83e8
L_21f1c:
    rotcl r2
    .org 0x21f1e - 0x83e8
L_21f1e:
    div1 r0,r1
    .org 0x21f20 - 0x83e8
L_21f20:
    rotcl r2
    .org 0x21f22 - 0x83e8
L_21f22:
    div1 r0,r1
    .org 0x21f24 - 0x83e8
L_21f24:
    bt L_21f28
    .org 0x21f26 - 0x83e8
L_21f26:
    add r0,r1
    .org 0x21f28 - 0x83e8
L_21f28:
    mov r1,r0
    .org 0x21f2a - 0x83e8
L_21f2a:
    rotcr r3
    .org 0x21f2c - 0x83e8
L_21f2c:
    bf L_21f32
    .org 0x21f2e - 0x83e8
L_21f2e:
    not r0,r0
    .org 0x21f30 - 0x83e8
L_21f30:
    add #0x1,r0
    .org 0x21f32 - 0x83e8
L_21f32:
    mov.l @r15+,r3
    .org 0x21f34 - 0x83e8
L_21f34:
    rts
    .org 0x21f36 - 0x83e8
L_21f36:
    mov.l @r15+,r2
    .org 0x21f38 - 0x83e8
P_21f38: .long 0xffff9818
    .org 0x21f3c - 0x83e8
P_21f3c: .long 0x0000044e
    .org 0x521a8 - 0x83e8
L_521a8:
    mov.l r14,@-r15
    .org 0x521aa - 0x83e8
L_521aa:
    sts.l pr,@-r15
    .org 0x521ac - 0x83e8
L_521ac:
    sts.l macl,@-r15
    .org 0x521ae - 0x83e8
L_521ae:
    stc.l gbr,@-r15
    .org 0x521b0 - 0x83e8
L_521b0:
    mov.l P_52298,r0
    .org 0x521b2 - 0x83e8
L_521b2:
    ldc r0,gbr
    .org 0x521b4 - 0x83e8
L_521b4:
    add #-0x8,r15
    .org 0x521b6 - 0x83e8
L_521b6:
    mov.l P_5229c,r6
    .org 0x521b8 - 0x83e8
L_521b8:
    mov.b @r6,r0
    .org 0x521ba - 0x83e8
L_521ba:
    tst #0x40,r0
    .org 0x521bc - 0x83e8
L_521bc:
    bt L_521c6
    .org 0x521be - 0x83e8
L_521be:
    mov.l P_522a0,r2
    .org 0x521c0 - 0x83e8
L_521c0:
    mov #0x36,r0
    .org 0x521c2 - 0x83e8
L_521c2:
    bra L_521cc
    .org 0x521c4 - 0x83e8
L_521c4:
    mov.w @(r0,r2),r6
    .org 0x521c6 - 0x83e8
L_521c6:
    mov.l P_522a4,r2
    .org 0x521c8 - 0x83e8
L_521c8:
    mov #0x20,r0
    .org 0x521ca - 0x83e8
L_521ca:
    mov.w @(r0,r2),r6
    .org 0x521cc - 0x83e8
L_521cc:
    extu.w r6,r6
    .org 0x521ce - 0x83e8
L_521ce:
    mov.l P_522a8,r2
    .org 0x521d0 - 0x83e8
L_521d0:
    shll2 r6
    .org 0x521d2 - 0x83e8
L_521d2:
    shll2 r6
    .org 0x521d4 - 0x83e8
L_521d4:
    mul.l r6,r2
    .org 0x521d6 - 0x83e8
L_521d6:
    stc gbr,r4
    .org 0x521d8 - 0x83e8
L_521d8:
    sts macl,r7
    .org 0x521da - 0x83e8
L_521da:
    add #0x18,r4
    .org 0x521dc - 0x83e8
L_521dc:
    mov #0x0,r14
    .org 0x521de - 0x83e8
L_521de:
    shlr16 r7
    .org 0x521e0 - 0x83e8
L_521e0:
    mov #0x6,r5
    .org 0x521e2 - 0x83e8
L_521e2:
    mov.w @r4,r2
    .org 0x521e4 - 0x83e8
L_521e4:
    extu.w r2,r2
    .org 0x521e6 - 0x83e8
L_521e6:
    cmp/ge r2,r14
    .org 0x521e8 - 0x83e8
L_521e8:
    bt L_521ec
    .org 0x521ea - 0x83e8
L_521ea:
    mov r2,r14
    .org 0x521ec - 0x83e8
L_521ec:
    dt r5
    .org 0x521ee - 0x83e8
L_521ee:
    bf/s L_521e2
    .org 0x521f0 - 0x83e8
L_521f0:
    add #0x2,r4
    .org 0x521f2 - 0x83e8
L_521f2:
    mov.w @(0x60,gbr),r0
    .org 0x521f4 - 0x83e8
L_521f4:
    extu.w r0,r6
    .org 0x521f6 - 0x83e8
L_521f6:
    cmp/ge r6,r14
    .org 0x521f8 - 0x83e8
L_521f8:
    bt L_521fc
    .org 0x521fa - 0x83e8
L_521fa:
    mov r6,r14
    .org 0x521fc - 0x83e8
L_521fc:
    mul.l r7,r14
    .org 0x521fe - 0x83e8
L_521fe:
    mov #-0x1,r4
    .org 0x52200 - 0x83e8
L_52200:
    extu.b r4,r4
    .org 0x52202 - 0x83e8
L_52202:
    sts macl,r2
    .org 0x52204 - 0x83e8
L_52204:
    shlr16 r2
    .org 0x52206 - 0x83e8
L_52206:
    cmp/hi r4,r2
    .org 0x52208 - 0x83e8
L_52208:
    bt L_5220c
    .org 0x5220a - 0x83e8
L_5220a:
    mov r2,r4
    .org 0x5220c - 0x83e8
L_5220c:
    mov.l P_522ac,r2
    .org 0x5220e - 0x83e8
L_5220e:
    extu.b r4,r4
    .org 0x52210 - 0x83e8
L_52210:
    mov.w P_52296,r0
    .org 0x52212 - 0x83e8
L_52212:
    mov.w @(r0,r2),r5
    .org 0x52214 - 0x83e8
L_52214:
    mov r4,r2
    .org 0x52216 - 0x83e8
L_52216:
    shll r2
    .org 0x52218 - 0x83e8
L_52218:
    extu.w r5,r5
    .org 0x5221a - 0x83e8
L_5221a:
    cmp/ge r2,r5
    .org 0x5221c - 0x83e8
L_5221c:
    bt L_52222
    .org 0x5221e - 0x83e8
L_5221e:
    bra L_52228
    .org 0x52220 - 0x83e8
L_52220:
    mov #0x0,r5
    .org 0x52222 - 0x83e8
L_52222:
    shll r5
    .org 0x52224 - 0x83e8
L_52224:
    shll2 r4
    .org 0x52226 - 0x83e8
L_52226:
    sub r4,r5
    .org 0x52228 - 0x83e8
L_52228:
    mov.l P_522b0,r6
    .org 0x5222a - 0x83e8
L_5222a:
    mov.l r5,@r15
    .org 0x5222c - 0x83e8
L_5222c:
    mov.b @(0x1,r6),r0
    .org 0x5222e - 0x83e8
L_5222e:
    tst #0x20,r0
    .org 0x52230 - 0x83e8
L_52230:
    bt L_52242
    .org 0x52232 - 0x83e8
L_52232:
    mov.l P_522b4,r6
    .org 0x52234 - 0x83e8
L_52234:
    mov.b @r6,r2
    .org 0x52236 - 0x83e8
L_52236:
    extu.b r2,r2
    .org 0x52238 - 0x83e8
L_52238:
    sub r2,r5
    .org 0x5223a - 0x83e8
L_5223a:
    cmp/pz r5
    .org 0x5223c - 0x83e8
L_5223c:
    bt L_52240
    .org 0x5223e - 0x83e8
L_5223e:
    mov #0x0,r5
    .org 0x52240 - 0x83e8
L_52240:
    mov.l r5,@r15
    .org 0x52242 - 0x83e8
L_52242:
    mov.l P_522b8,r2
    .org 0x52244 - 0x83e8
L_52244:
    mov #0x78,r0
    .org 0x52246 - 0x83e8
L_52246:
    jsr @r2
    .org 0x52248 - 0x83e8
L_52248:
    mov r5,r1
    .org 0x5224a - 0x83e8
L_5224a:
    mov.l P_522bc,r2
    .org 0x5224c - 0x83e8
L_5224c:
    mov.l @r15,r1
    .org 0x5224e - 0x83e8
L_5224e:
    mov.l r0,@(0x4,r15)
    .org 0x52250 - 0x83e8
L_52250:
    jsr @r2
    .org 0x52252 - 0x83e8
L_52252:
    mov #0x78,r0
    .org 0x52254 - 0x83e8
L_52254:
    mov #0x4,r2
    .org 0x52256 - 0x83e8
L_52256:
    cmp/ge r2,r0
    .org 0x52258 - 0x83e8
L_52258:
    bt/s L_5225e
    .org 0x5225a - 0x83e8
L_5225a:
    mov r0,r5
    .org 0x5225c - 0x83e8
L_5225c:
    mov #0x4,r5
    .org 0x5225e - 0x83e8
L_5225e:
    mov #0x74,r2
    .org 0x52260 - 0x83e8
L_52260:
    cmp/gt r2,r5
    .org 0x52262 - 0x83e8
L_52262:
    bf L_52266
    .org 0x52264 - 0x83e8
L_52264:
    mov #0x74,r5
    .org 0x52266 - 0x83e8
L_52266:
    cmp/pz r5
    .org 0x52268 - 0x83e8
L_52268:
    bt/s L_5226e
    .org 0x5226a - 0x83e8
L_5226a:
    mov r5,r2
    .org 0x5226c - 0x83e8
L_5226c:
    add #0x3,r2
    .org 0x5226e - 0x83e8
L_5226e:
    shar r2
    .org 0x52270 - 0x83e8
L_52270:
    mov.l P_522c0,r5
    .org 0x52272 - 0x83e8
L_52272:
    shar r2
    .org 0x52274 - 0x83e8
L_52274:
    mov r2,r0
    .org 0x52276 - 0x83e8
L_52276:
    mov.b r0,@(0x3,gbr)
    .org 0x52278 - 0x83e8
L_52278:
    mov.b @(0x5,r5),r0
    .org 0x5227a - 0x83e8
L_5227a:
    tst #0x1,r0
    .org 0x5227c - 0x83e8
L_5227c:
    bt L_52282
    .org 0x5227e - 0x83e8
L_5227e:
    mov #0x3,r6
    .org 0x52280 - 0x83e8
L_52280:
    mov.l r6,@(0x4,r15)
    .org 0x52282 - 0x83e8
L_52282:
    mov.l @(0x4,r15),r0
    .org 0x52284 - 0x83e8
L_52284:
    mov.b r0,@(0x34,gbr)
    .org 0x52286 - 0x83e8
L_52286:
    add #0x8,r15
    .org 0x52288 - 0x83e8
L_52288:
    ldc.l @r15+,gbr
    .org 0x5228a - 0x83e8
L_5228a:
    lds.l @r15+,macl
    .org 0x5228c - 0x83e8
L_5228c:
    lds.l @r15+,pr
    .org 0x5228e - 0x83e8
L_5228e:
    rts
    .org 0x52290 - 0x83e8
L_52290:
    mov.l @r15+,r14
    .org 0x52296 - 0x83e8
P_52296: .word 0x06a2
    .org 0x52298 - 0x83e8
P_52298: .long 0xffff23bc
    .org 0x5229c - 0x83e8
P_5229c: .long 0xffff4184
    .org 0x522a0 - 0x83e8
P_522a0: .long 0xffff1094
    .org 0x522a4 - 0x83e8
P_522a4: .long 0xffff119c
    .org 0x522a8 - 0x83e8
P_522a8: .long 0x0000c49b
    .org 0x522ac - 0x83e8
P_522ac: .long 0xffff128c
    .org 0x522b0 - 0x83e8
P_522b0: .long 0xffff24c8
    .org 0x522b4 - 0x83e8
P_522b4: .long 0x000083ea
    .org 0x522b8 - 0x83e8
P_522b8: .long 0x00021bbc
    .org 0x522bc - 0x83e8
P_522bc: .long 0x00021e14
    .org 0x522c0 - 0x83e8
P_522c0: .long 0xffff424c
