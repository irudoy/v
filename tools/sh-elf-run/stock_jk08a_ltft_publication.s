! Complete two-bank LTFT publication with the real natural diagnostic predicate.
    .section .text
    .balign 4
    .org 0x8e5a - 0x8e58
P_8e5a: .byte 0x6e
    .org 0x8e5b - 0x8e58
P_8e5b: .byte 0x5a
    .org 0x25e20 - 0x8e58
L_25e20:
    mov.l P_25f10,r1
    .org 0x25e22 - 0x8e58
L_25e22:
    exts.w r4,r0
    .org 0x25e24 - 0x8e58
L_25e24:
    cmp/eq #-0x1,r0
    .org 0x25e26 - 0x8e58
L_25e26:
    bt L_25e3e
    .org 0x25e28 - 0x8e58
L_25e28:
    mov r1,r6
    .org 0x25e2a - 0x8e58
L_25e2a:
    mov r0,r2
    .org 0x25e2c - 0x8e58
L_25e2c:
    shll r2
    .org 0x25e2e - 0x8e58
L_25e2e:
    add r0,r2
    .org 0x25e30 - 0x8e58
L_25e30:
    add r2,r6
    .org 0x25e32 - 0x8e58
L_25e32:
    mov.b @(0x1,r6),r0
    .org 0x25e34 - 0x8e58
L_25e34:
    tst #0x80,r0
    .org 0x25e36 - 0x8e58
L_25e36:
    movt r0
    .org 0x25e38 - 0x8e58
L_25e38:
    xor #0x1,r0
    .org 0x25e3a - 0x8e58
L_25e3a:
    bra L_25e40
    .org 0x25e3c - 0x8e58
L_25e3c:
    extu.b r0,r2
    .org 0x25e3e - 0x8e58
L_25e3e:
    mov #0x0,r2
    .org 0x25e40 - 0x8e58
L_25e40:
    rts
    .org 0x25e42 - 0x8e58
L_25e42:
    mov r2,r0
    .org 0x25f10 - 0x8e58
P_25f10: .long 0xffff5718
    .org 0x57b26 - 0x8e58
L_57b26:
    mov.l r13,@-r15
    .org 0x57b28 - 0x8e58
L_57b28:
    mov.l r14,@-r15
    .org 0x57b2a - 0x8e58
L_57b2a:
    sts.l pr,@-r15
    .org 0x57b2c - 0x8e58
L_57b2c:
    extu.b r4,r4
    .org 0x57b2e - 0x8e58
L_57b2e:
    mov.l P_57bc0,r6
    .org 0x57b30 - 0x8e58
L_57b30:
    mov.l P_57bc4,r5
    .org 0x57b32 - 0x8e58
L_57b32:
    mov r4,r0
    .org 0x57b34 - 0x8e58
L_57b34:
    shll r0
    .org 0x57b36 - 0x8e58
L_57b36:
    mov.w @(r0,r6),r2
    .org 0x57b38 - 0x8e58
L_57b38:
    mov r0,r13
    .org 0x57b3a - 0x8e58
L_57b3a:
    mov.w @(r0,r5),r6
    .org 0x57b3c - 0x8e58
L_57b3c:
    mov #0x16,r0
    .org 0x57b3e - 0x8e58
L_57b3e:
    extu.w r2,r14
    .org 0x57b40 - 0x8e58
L_57b40:
    mov.l P_57bc8,r2
    .org 0x57b42 - 0x8e58
L_57b42:
    extu.w r6,r6
    .org 0x57b44 - 0x8e58
L_57b44:
    add r6,r14
    .org 0x57b46 - 0x8e58
L_57b46:
    mov #-0x64,r6
    .org 0x57b48 - 0x8e58
L_57b48:
    shll8 r6
    .org 0x57b4a - 0x8e58
L_57b4a:
    add r6,r14
    .org 0x57b4c - 0x8e58
L_57b4c:
    mov.b @(r0,r2),r6
    .org 0x57b4e - 0x8e58
L_57b4e:
    mov r4,r2
    .org 0x57b50 - 0x8e58
L_57b50:
    add #0x1,r2
    .org 0x57b52 - 0x8e58
L_57b52:
    extu.b r6,r6
    .org 0x57b54 - 0x8e58
L_57b54:
    tst r2,r6
    .org 0x57b56 - 0x8e58
L_57b56:
    bf L_57bea
    .org 0x57b58 - 0x8e58
L_57b58:
    mov.l P_57bcc,r5
    .org 0x57b5a - 0x8e58
L_57b5a:
    mov.w P_57b7a,r0
    .org 0x57b5c - 0x8e58
L_57b5c:
    mov.w @(r0,r5),r2
    .org 0x57b5e - 0x8e58
L_57b5e:
    mov.w P_57b7c,r0
    .org 0x57b60 - 0x8e58
L_57b60:
    extu.w r2,r2
    .org 0x57b62 - 0x8e58
L_57b62:
    mov.w @(r0,r5),r6
    .org 0x57b64 - 0x8e58
L_57b64:
    cmp/gt r6,r2
    .org 0x57b66 - 0x8e58
L_57b66:
    bf L_57bea
    .org 0x57b68 - 0x8e58
L_57b68:
    mov.l P_57bd0,r2
    .org 0x57b6a - 0x8e58
L_57b6a:
    mov.b @r2,r6
    .org 0x57b6c - 0x8e58
L_57b6c:
    extu.b r6,r5
    .org 0x57b6e - 0x8e58
L_57b6e:
    mov r5,r2
    .org 0x57b70 - 0x8e58
L_57b70:
    shll8 r2
    .org 0x57b72 - 0x8e58
L_57b72:
    cmp/hs r2,r14
    .org 0x57b74 - 0x8e58
L_57b74:
    bt L_57bd4
    .org 0x57b76 - 0x8e58
L_57b76:
    bra L_57bd6
    .org 0x57b78 - 0x8e58
L_57b78:
    shll8 r5
    .org 0x57b7a - 0x8e58
P_57b7a: .word 0x0370
    .org 0x57b7c - 0x8e58
P_57b7c: .word 0x0372
    .org 0x57bc0 - 0x8e58
P_57bc0: .long 0xffff2306
    .org 0x57bc4 - 0x8e58
P_57bc4: .long 0xffff5648
    .org 0x57bc8 - 0x8e58
P_57bc8: .long 0xffff22f8
    .org 0x57bcc - 0x8e58
P_57bcc: .long 0xffff128c
    .org 0x57bd0 - 0x8e58
P_57bd0: .long 0x00008e5b
    .org 0x57bd4 - 0x8e58
L_57bd4:
    mov r14,r5
    .org 0x57bd6 - 0x8e58
L_57bd6:
    mov.l P_57e34,r2
    .org 0x57bd8 - 0x8e58
L_57bd8:
    mov.b @r2,r6
    .org 0x57bda - 0x8e58
L_57bda:
    extu.b r6,r6
    .org 0x57bdc - 0x8e58
L_57bdc:
    mov r6,r2
    .org 0x57bde - 0x8e58
L_57bde:
    shll8 r2
    .org 0x57be0 - 0x8e58
L_57be0:
    cmp/hi r2,r5
    .org 0x57be2 - 0x8e58
L_57be2:
    bf L_57be8
    .org 0x57be4 - 0x8e58
L_57be4:
    shll8 r6
    .org 0x57be6 - 0x8e58
L_57be6:
    mov r6,r5
    .org 0x57be8 - 0x8e58
L_57be8:
    mov r5,r14
    .org 0x57bea - 0x8e58
L_57bea:
    mov.l P_57e38,r2
    .org 0x57bec - 0x8e58
L_57bec:
    mov.w P_57d1a,r4
    .org 0x57bee - 0x8e58
L_57bee:
    jsr @r2
    .org 0x57bf0 - 0x8e58
L_57bf0:
    nop
    .org 0x57bf2 - 0x8e58
L_57bf2:
    tst r0,r0
    .org 0x57bf4 - 0x8e58
L_57bf4:
    bf L_57c22
    .org 0x57bf6 - 0x8e58
L_57bf6:
    mov.l P_57e3c,r6
    .org 0x57bf8 - 0x8e58
L_57bf8:
    mov.b @(0xc,r6),r0
    .org 0x57bfa - 0x8e58
L_57bfa:
    tst #0x1,r0
    .org 0x57bfc - 0x8e58
L_57bfc:
    bf L_57c22
    .org 0x57bfe - 0x8e58
L_57bfe:
    mov #0x51,r0
    .org 0x57c00 - 0x8e58
L_57c00:
    mov.b @(r0,r6),r0
    .org 0x57c02 - 0x8e58
L_57c02:
    tst #0x1,r0
    .org 0x57c04 - 0x8e58
L_57c04:
    bt L_57c10
    .org 0x57c06 - 0x8e58
L_57c06:
    mov.l P_57e40,r6
    .org 0x57c08 - 0x8e58
L_57c08:
    mov #0x1b,r0
    .org 0x57c0a - 0x8e58
L_57c0a:
    mov.b @(r0,r6),r0
    .org 0x57c0c - 0x8e58
L_57c0c:
    tst #0x2,r0
    .org 0x57c0e - 0x8e58
L_57c0e:
    bf L_57c22
    .org 0x57c10 - 0x8e58
L_57c10:
    mov.l P_57e40,r6
    .org 0x57c12 - 0x8e58
L_57c12:
    mov #0x2c,r0
    .org 0x57c14 - 0x8e58
L_57c14:
    mov.b @(r0,r6),r0
    .org 0x57c16 - 0x8e58
L_57c16:
    tst #0x40,r0
    .org 0x57c18 - 0x8e58
L_57c18:
    bt L_57c26
    .org 0x57c1a - 0x8e58
L_57c1a:
    mov #0x1b,r0
    .org 0x57c1c - 0x8e58
L_57c1c:
    mov.b @(r0,r6),r0
    .org 0x57c1e - 0x8e58
L_57c1e:
    tst #0x1,r0
    .org 0x57c20 - 0x8e58
L_57c20:
    bt L_57c26
    .org 0x57c22 - 0x8e58
L_57c22:
    mov #0x64,r14
    .org 0x57c24 - 0x8e58
L_57c24:
    shll8 r14
    .org 0x57c26 - 0x8e58
L_57c26:
    mov.l P_57e44,r2
    .org 0x57c28 - 0x8e58
L_57c28:
    mov r13,r0
    .org 0x57c2a - 0x8e58
L_57c2a:
    mov.w r14,@(r0,r2)
    .org 0x57c2c - 0x8e58
L_57c2c:
    lds.l @r15+,pr
    .org 0x57c2e - 0x8e58
L_57c2e:
    mov.l @r15+,r14
    .org 0x57c30 - 0x8e58
L_57c30:
    rts
    .org 0x57c32 - 0x8e58
L_57c32:
    mov.l @r15+,r13
    .org 0x57d1a - 0x8e58
P_57d1a: .word 0x0129
    .org 0x57e34 - 0x8e58
P_57e34: .long 0x00008e5a
    .org 0x57e38 - 0x8e58
P_57e38: .long 0x00025e20
    .org 0x57e3c - 0x8e58
P_57e3c: .long 0xffff41a9
    .org 0x57e40 - 0x8e58
P_57e40: .long 0xffff2470
    .org 0x57e44 - 0x8e58
P_57e44: .long 0xffff2302
