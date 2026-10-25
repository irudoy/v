! Complete stock native index1 learned-trim adjustment updater and real fixed-argument helpers.
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
    .org 0x25e20-ORIGIN
L_00025e20:
    mov.l P_00025f10,r1
    .org 0x25e22-ORIGIN
L_00025e22:
    exts.w r4,r0
    .org 0x25e24-ORIGIN
L_00025e24:
    cmp/eq #-0x1,r0
    .org 0x25e26-ORIGIN
L_00025e26:
    bt L_00025e3e
    .org 0x25e28-ORIGIN
L_00025e28:
    mov r1,r6
    .org 0x25e2a-ORIGIN
L_00025e2a:
    mov r0,r2
    .org 0x25e2c-ORIGIN
L_00025e2c:
    shll r2
    .org 0x25e2e-ORIGIN
L_00025e2e:
    add r0,r2
    .org 0x25e30-ORIGIN
L_00025e30:
    add r2,r6
    .org 0x25e32-ORIGIN
L_00025e32:
    mov.b @(0x1,r6),r0
    .org 0x25e34-ORIGIN
L_00025e34:
    tst #0x80,r0
    .org 0x25e36-ORIGIN
L_00025e36:
    movt r0
    .org 0x25e38-ORIGIN
L_00025e38:
    xor #0x1,r0
    .org 0x25e3a-ORIGIN
L_00025e3a:
    bra L_00025e40
    .org 0x25e3c-ORIGIN
L_00025e3c:
    extu.b r0,r2
    .org 0x25e3e-ORIGIN
L_00025e3e:
    mov #0x0,r2
    .org 0x25e40-ORIGIN
L_00025e40:
    rts
    .org 0x25e42-ORIGIN
L_00025e42:
    mov r2,r0
    .org 0x25f10-ORIGIN
P_00025f10:
    .byte 0xff
    .org 0x25f11-ORIGIN
P_00025f11:
    .byte 0xff
    .org 0x25f12-ORIGIN
P_00025f12:
    .byte 0x57
    .org 0x25f13-ORIGIN
P_00025f13:
    .byte 0x18
    .org 0x58168-ORIGIN
L_00058168:
    mov.l r8,@-r15
    .org 0x5816a-ORIGIN
L_0005816a:
    mov.l r9,@-r15
    .org 0x5816c-ORIGIN
L_0005816c:
    mov.l r10,@-r15
    .org 0x5816e-ORIGIN
L_0005816e:
    mov.l r11,@-r15
    .org 0x58170-ORIGIN
L_00058170:
    mov.l r12,@-r15
    .org 0x58172-ORIGIN
L_00058172:
    mov.l r13,@-r15
    .org 0x58174-ORIGIN
L_00058174:
    mov.l r14,@-r15
    .org 0x58176-ORIGIN
L_00058176:
    sts.l pr,@-r15
    .org 0x58178-ORIGIN
L_00058178:
    sts.l macl,@-r15
    .org 0x5817a-ORIGIN
L_0005817a:
    add #-0x20,r15
    .org 0x5817c-ORIGIN
L_0005817c:
    extu.b r4,r14
    .org 0x5817e-ORIGIN
L_0005817e:
    mov.l P_00058354,r9
    .org 0x58180-ORIGIN
L_00058180:
    mov r14,r0
    .org 0x58182-ORIGIN
L_00058182:
    shll r0
    .org 0x58184-ORIGIN
L_00058184:
    mov r0,r10
    .org 0x58186-ORIGIN
L_00058186:
    mov.w @(r0,r9),r0
    .org 0x58188-ORIGIN
L_00058188:
    mov.l P_00058358,r4
    .org 0x5818a-ORIGIN
L_0005818a:
    mov r14,r11
    .org 0x5818c-ORIGIN
L_0005818c:
    mov.l P_0005835c,r2
    .org 0x5818e-ORIGIN
L_0005818e:
    add #0x1,r11
    .org 0x58190-ORIGIN
L_00058190:
    mov.w r0,@r15
    .org 0x58192-ORIGIN
L_00058192:
    mov #0x0,r12
    .org 0x58194-ORIGIN
L_00058194:
    mov.w r0,@(0x4,r15)
    .org 0x58196-ORIGIN
L_00058196:
    mov r10,r0
    .org 0x58198-ORIGIN
L_00058198:
    mov.b @r4,r6
    .org 0x5819a-ORIGIN
L_0005819a:
    mov r14,r13
    .org 0x5819c-ORIGIN
L_0005819c:
    mov.w @(r0,r2),r0
    .org 0x5819e-ORIGIN
L_0005819e:
    add #0x1,r13
    .org 0x581a0-ORIGIN
L_000581a0:
    extu.b r6,r7
    .org 0x581a2-ORIGIN
L_000581a2:
    mov.l P_00058360,r8
    .org 0x581a4-ORIGIN
L_000581a4:
    extu.w r0,r6
    .org 0x581a6-ORIGIN
L_000581a6:
    mov.w r0,@(0x8,r15)
    .org 0x581a8-ORIGIN
L_000581a8:
    mul.l r7,r6
    .org 0x581aa-ORIGIN
L_000581aa:
    mov #0x64,r0
    .org 0x581ac-ORIGIN
L_000581ac:
    shll8 r0
    .org 0x581ae-ORIGIN
L_000581ae:
    jsr @r8
    .org 0x581b0-ORIGIN
L_000581b0:
    sts macl,r1
    .org 0x581b2-ORIGIN
L_000581b2:
    mov.l P_00058364,r6
    .org 0x581b4-ORIGIN
L_000581b4:
    mov r0,r2
    .org 0x581b6-ORIGIN
L_000581b6:
    mov.b @(0x5,r6),r0
    .org 0x581b8-ORIGIN
L_000581b8:
    extu.b r0,r7
    .org 0x581ba-ORIGIN
L_000581ba:
    tst r11,r7
    .org 0x581bc-ORIGIN
L_000581bc:
    bf L_000581c2
    .org 0x581be-ORIGIN
L_000581be:
    bra L_000583e4
    .org 0x581c0-ORIGIN
L_000581c0:
    nop
    .org 0x581c2-ORIGIN
L_000581c2:
    mov.l P_00058368,r6
    .org 0x581c4-ORIGIN
L_000581c4:
    mov #0x16,r0
    .org 0x581c6-ORIGIN
L_000581c6:
    mov.b @(r0,r6),r7
    .org 0x581c8-ORIGIN
L_000581c8:
    extu.b r7,r7
    .org 0x581ca-ORIGIN
L_000581ca:
    tst r11,r7
    .org 0x581cc-ORIGIN
L_000581cc:
    bf L_000581d2
    .org 0x581ce-ORIGIN
L_000581ce:
    bra L_000583e4
    .org 0x581d0-ORIGIN
L_000581d0:
    nop
    .org 0x581d2-ORIGIN
L_000581d2:
    mov.l P_0005836c,r6
    .org 0x581d4-ORIGIN
L_000581d4:
    mov r14,r0
    .org 0x581d6-ORIGIN
L_000581d6:
    mov.b @(r0,r6),r7
    .org 0x581d8-ORIGIN
L_000581d8:
    tst r7,r7
    .org 0x581da-ORIGIN
L_000581da:
    bt L_000581e0
    .org 0x581dc-ORIGIN
L_000581dc:
    bra L_00058440
    .org 0x581de-ORIGIN
L_000581de:
    nop
    .org 0x581e0-ORIGIN
L_000581e0:
    mov.l P_0005836c,r5
    .org 0x581e2-ORIGIN
L_000581e2:
    mov #0x10,r6
    .org 0x581e4-ORIGIN
L_000581e4:
    mov r14,r0
    .org 0x581e6-ORIGIN
L_000581e6:
    mov.b r6,@(r0,r5)
    .org 0x581e8-ORIGIN
L_000581e8:
    mov.l P_00058370,r5
    .org 0x581ea-ORIGIN
L_000581ea:
    mov.w P_0005828a,r0
    .org 0x581ec-ORIGIN
L_000581ec:
    mov.b @(r0,r5),r7
    .org 0x581ee-ORIGIN
L_000581ee:
    extu.b r7,r7
    .org 0x581f0-ORIGIN
L_000581f0:
    tst r11,r7
    .org 0x581f2-ORIGIN
L_000581f2:
    bf L_000581f8
    .org 0x581f4-ORIGIN
L_000581f4:
    bra L_0005838c
    .org 0x581f6-ORIGIN
L_000581f6:
    nop
    .org 0x581f8-ORIGIN
L_000581f8:
    mov.l P_00058374,r7
    .org 0x581fa-ORIGIN
L_000581fa:
    mov r10,r0
    .org 0x581fc-ORIGIN
L_000581fc:
    mov #0x64,r6
    .org 0x581fe-ORIGIN
L_000581fe:
    mov.l P_00058358,r4
    .org 0x58200-ORIGIN
L_00058200:
    mov.w @(r0,r7),r0
    .org 0x58202-ORIGIN
L_00058202:
    shll8 r6
    .org 0x58204-ORIGIN
L_00058204:
    mov.l P_00058378,r7
    .org 0x58206-ORIGIN
L_00058206:
    mov.w r0,@(0xc,r15)
    .org 0x58208-ORIGIN
L_00058208:
    mov r10,r0
    .org 0x5820a-ORIGIN
L_0005820a:
    mov.w @(r0,r7),r2
    .org 0x5820c-ORIGIN
L_0005820c:
    mov.w @(0xc,r15),r0
    .org 0x5820e-ORIGIN
L_0005820e:
    add r2,r0
    .org 0x58210-ORIGIN
L_00058210:
    mov.w r0,@(0xc,r15)
    .org 0x58212-ORIGIN
L_00058212:
    exts.w r0,r0
    .org 0x58214-ORIGIN
L_00058214:
    sub r6,r0
    .org 0x58216-ORIGIN
L_00058216:
    mov.b @r4,r6
    .org 0x58218-ORIGIN
L_00058218:
    mov.w r0,@(0xc,r15)
    .org 0x5821a-ORIGIN
L_0005821a:
    mov.w @(0x8,r15),r0
    .org 0x5821c-ORIGIN
L_0005821c:
    extu.b r6,r7
    .org 0x5821e-ORIGIN
L_0005821e:
    extu.w r0,r6
    .org 0x58220-ORIGIN
L_00058220:
    mul.l r7,r6
    .org 0x58222-ORIGIN
L_00058222:
    mov #0x64,r0
    .org 0x58224-ORIGIN
L_00058224:
    shll8 r0
    .org 0x58226-ORIGIN
L_00058226:
    sts macl,r1
    .org 0x58228-ORIGIN
L_00058228:
    jsr @r8
    .org 0x5822a-ORIGIN
L_0005822a:
    mov.l r0,@(0x10,r15)
    .org 0x5822c-ORIGIN
L_0005822c:
    mov.w @r15,r2
    .org 0x5822e-ORIGIN
L_0005822e:
    mov.l P_00058358,r4
    .org 0x58230-ORIGIN
L_00058230:
    add r0,r2
    .org 0x58232-ORIGIN
L_00058232:
    mov r2,r0
    .org 0x58234-ORIGIN
L_00058234:
    mov.w r0,@(0x14,r15)
    .org 0x58236-ORIGIN
L_00058236:
    mov.b @r4,r2
    .org 0x58238-ORIGIN
L_00058238:
    mov.w @(0x8,r15),r0
    .org 0x5823a-ORIGIN
L_0005823a:
    extu.b r2,r2
    .org 0x5823c-ORIGIN
L_0005823c:
    extu.w r0,r6
    .org 0x5823e-ORIGIN
L_0005823e:
    mov.l @(0x10,r15),r0
    .org 0x58240-ORIGIN
L_00058240:
    mul.l r2,r6
    .org 0x58242-ORIGIN
L_00058242:
    jsr @r8
    .org 0x58244-ORIGIN
L_00058244:
    sts macl,r1
    .org 0x58246-ORIGIN
L_00058246:
    mov.w @r15,r5
    .org 0x58248-ORIGIN
L_00058248:
    extu.w r5,r5
    .org 0x5824a-ORIGIN
L_0005824a:
    mov r5,r6
    .org 0x5824c-ORIGIN
L_0005824c:
    sub r0,r6
    .org 0x5824e-ORIGIN
L_0005824e:
    mov r6,r0
    .org 0x58250-ORIGIN
L_00058250:
    mov.w r0,@(0x18,r15)
    .org 0x58252-ORIGIN
L_00058252:
    mov.w @(0xc,r15),r0
    .org 0x58254-ORIGIN
L_00058254:
    extu.w r0,r2
    .org 0x58256-ORIGIN
L_00058256:
    mov.l r2,@(0x1c,r15)
    .org 0x58258-ORIGIN
L_00058258:
    mov.l P_0005837c,r2
    .org 0x5825a-ORIGIN
L_0005825a:
    mov.b @r2,r7
    .org 0x5825c-ORIGIN
L_0005825c:
    extu.b r7,r7
    .org 0x5825e-ORIGIN
L_0005825e:
    mov r7,r6
    .org 0x58260-ORIGIN
L_00058260:
    shll8 r6
    .org 0x58262-ORIGIN
L_00058262:
    extu.w r6,r2
    .org 0x58264-ORIGIN
L_00058264:
    mov.l @(0x1c,r15),r6
    .org 0x58266-ORIGIN
L_00058266:
    cmp/ge r2,r6
    .org 0x58268-ORIGIN
L_00058268:
    bf L_00058296
    .org 0x5826a-ORIGIN
L_0005826a:
    mov.w @(0x14,r15),r0
    .org 0x5826c-ORIGIN
L_0005826c:
    extu.w r0,r2
    .org 0x5826e-ORIGIN
L_0005826e:
    mov.w r0,@(0x4,r15)
    .org 0x58270-ORIGIN
L_00058270:
    mov.l r2,@(0x1c,r15)
    .org 0x58272-ORIGIN
L_00058272:
    mov.l P_00058380,r2
    .org 0x58274-ORIGIN
L_00058274:
    mov.b @r2,r6
    .org 0x58276-ORIGIN
L_00058276:
    extu.b r6,r2
    .org 0x58278-ORIGIN
L_00058278:
    mov.l @(0x1c,r15),r6
    .org 0x5827a-ORIGIN
L_0005827a:
    shll8 r2
    .org 0x5827c-ORIGIN
L_0005827c:
    extu.w r2,r2
    .org 0x5827e-ORIGIN
L_0005827e:
    cmp/gt r2,r6
    .org 0x58280-ORIGIN
L_00058280:
    bf/s L_000582d0
    .org 0x58282-ORIGIN
L_00058282:
    mov #0x1,r12
    .org 0x58284-ORIGIN
L_00058284:
    mov.l P_00058380,r3
    .org 0x58286-ORIGIN
L_00058286:
    bra L_0005828c
    .org 0x58288-ORIGIN
L_00058288:
    nop
    .org 0x5828a-ORIGIN
P_0005828a:
    .byte 0x04
    .org 0x5828b-ORIGIN
P_0005828b:
    .byte 0x6c
    .org 0x5828c-ORIGIN
L_0005828c:
    mov.b @r3,r6
    .org 0x5828e-ORIGIN
L_0005828e:
    extu.b r6,r0
    .org 0x58290-ORIGIN
L_00058290:
    shll8 r0
    .org 0x58292-ORIGIN
L_00058292:
    bra L_000582d0
    .org 0x58294-ORIGIN
L_00058294:
    mov.w r0,@(0x4,r15)
    .org 0x58296-ORIGIN
L_00058296:
    mov.w @(0xc,r15),r0
    .org 0x58298-ORIGIN
L_00058298:
    mov.l P_00058384,r2
    .org 0x5829a-ORIGIN
L_0005829a:
    extu.w r0,r6
    .org 0x5829c-ORIGIN
L_0005829c:
    mov.l r6,@(0x1c,r15)
    .org 0x5829e-ORIGIN
L_0005829e:
    mov.b @r2,r6
    .org 0x582a0-ORIGIN
L_000582a0:
    extu.b r6,r2
    .org 0x582a2-ORIGIN
L_000582a2:
    mov.l @(0x1c,r15),r6
    .org 0x582a4-ORIGIN
L_000582a4:
    shll8 r2
    .org 0x582a6-ORIGIN
L_000582a6:
    extu.w r2,r2
    .org 0x582a8-ORIGIN
L_000582a8:
    cmp/gt r2,r6
    .org 0x582aa-ORIGIN
L_000582aa:
    bt L_000582d0
    .org 0x582ac-ORIGIN
L_000582ac:
    mov.w @(0x18,r15),r0
    .org 0x582ae-ORIGIN
L_000582ae:
    extu.w r0,r2
    .org 0x582b0-ORIGIN
L_000582b0:
    mov.w r0,@(0x4,r15)
    .org 0x582b2-ORIGIN
L_000582b2:
    mov.l r2,@(0x1c,r15)
    .org 0x582b4-ORIGIN
L_000582b4:
    mov.l P_00058388,r2
    .org 0x582b6-ORIGIN
L_000582b6:
    mov.b @r2,r6
    .org 0x582b8-ORIGIN
L_000582b8:
    extu.b r6,r2
    .org 0x582ba-ORIGIN
L_000582ba:
    mov.l @(0x1c,r15),r6
    .org 0x582bc-ORIGIN
L_000582bc:
    shll8 r2
    .org 0x582be-ORIGIN
L_000582be:
    extu.w r2,r2
    .org 0x582c0-ORIGIN
L_000582c0:
    cmp/ge r2,r6
    .org 0x582c2-ORIGIN
L_000582c2:
    bt/s L_000582d0
    .org 0x582c4-ORIGIN
L_000582c4:
    mov #0x1,r12
    .org 0x582c6-ORIGIN
L_000582c6:
    mov.l P_00058388,r3
    .org 0x582c8-ORIGIN
L_000582c8:
    mov.b @r3,r6
    .org 0x582ca-ORIGIN
L_000582ca:
    extu.b r6,r0
    .org 0x582cc-ORIGIN
L_000582cc:
    shll8 r0
    .org 0x582ce-ORIGIN
L_000582ce:
    mov.w r0,@(0x4,r15)
    .org 0x582d0-ORIGIN
L_000582d0:
    extu.w r12,r12
    .org 0x582d2-ORIGIN
L_000582d2:
    tst r12,r12
    .org 0x582d4-ORIGIN
L_000582d4:
    bt L_000582da
    .org 0x582d6-ORIGIN
L_000582d6:
    bra L_00058440
    .org 0x582d8-ORIGIN
L_000582d8:
    nop
    .org 0x582da-ORIGIN
L_000582da:
    mov.w @(0xc,r15),r0
    .org 0x582dc-ORIGIN
L_000582dc:
    shll8 r7
    .org 0x582de-ORIGIN
L_000582de:
    extu.w r7,r2
    .org 0x582e0-ORIGIN
L_000582e0:
    extu.w r0,r4
    .org 0x582e2-ORIGIN
L_000582e2:
    cmp/ge r2,r4
    .org 0x582e4-ORIGIN
L_000582e4:
    bt L_00058304
    .org 0x582e6-ORIGIN
L_000582e6:
    mov #0x64,r6
    .org 0x582e8-ORIGIN
L_000582e8:
    shll8 r6
    .org 0x582ea-ORIGIN
L_000582ea:
    cmp/ge r6,r5
    .org 0x582ec-ORIGIN
L_000582ec:
    bf L_00058304
    .org 0x582ee-ORIGIN
L_000582ee:
    mov.w @(0x18,r15),r0
    .org 0x582f0-ORIGIN
L_000582f0:
    mov #0x64,r6
    .org 0x582f2-ORIGIN
L_000582f2:
    shll8 r6
    .org 0x582f4-ORIGIN
L_000582f4:
    extu.w r0,r2
    .org 0x582f6-ORIGIN
L_000582f6:
    mov.w r0,@(0x4,r15)
    .org 0x582f8-ORIGIN
L_000582f8:
    cmp/gt r6,r2
    .org 0x582fa-ORIGIN
L_000582fa:
    bt/s L_00058304
    .org 0x582fc-ORIGIN
L_000582fc:
    mov #0x1,r12
    .org 0x582fe-ORIGIN
L_000582fe:
    mov #0x64,r0
    .org 0x58300-ORIGIN
L_00058300:
    shll8 r0
    .org 0x58302-ORIGIN
L_00058302:
    mov.w r0,@(0x4,r15)
    .org 0x58304-ORIGIN
L_00058304:
    extu.w r12,r12
    .org 0x58306-ORIGIN
L_00058306:
    tst r12,r12
    .org 0x58308-ORIGIN
L_00058308:
    bt L_0005830e
    .org 0x5830a-ORIGIN
L_0005830a:
    bra L_00058440
    .org 0x5830c-ORIGIN
L_0005830c:
    nop
    .org 0x5830e-ORIGIN
L_0005830e:
    mov.l P_00058384,r2
    .org 0x58310-ORIGIN
L_00058310:
    mov.w @(0xc,r15),r0
    .org 0x58312-ORIGIN
L_00058312:
    mov.b @r2,r6
    .org 0x58314-ORIGIN
L_00058314:
    extu.w r0,r7
    .org 0x58316-ORIGIN
L_00058316:
    extu.b r6,r2
    .org 0x58318-ORIGIN
L_00058318:
    shll8 r2
    .org 0x5831a-ORIGIN
L_0005831a:
    extu.w r2,r2
    .org 0x5831c-ORIGIN
L_0005831c:
    cmp/gt r2,r7
    .org 0x5831e-ORIGIN
L_0005831e:
    bt L_00058324
    .org 0x58320-ORIGIN
L_00058320:
    bra L_00058440
    .org 0x58322-ORIGIN
L_00058322:
    nop
    .org 0x58324-ORIGIN
L_00058324:
    mov #0x64,r2
    .org 0x58326-ORIGIN
L_00058326:
    shll8 r2
    .org 0x58328-ORIGIN
L_00058328:
    cmp/gt r2,r5
    .org 0x5832a-ORIGIN
L_0005832a:
    bf L_00058330
    .org 0x5832c-ORIGIN
L_0005832c:
    bra L_00058440
    .org 0x5832e-ORIGIN
L_0005832e:
    nop
    .org 0x58330-ORIGIN
L_00058330:
    mov.w @(0x14,r15),r0
    .org 0x58332-ORIGIN
L_00058332:
    mov #0x64,r6
    .org 0x58334-ORIGIN
L_00058334:
    shll8 r6
    .org 0x58336-ORIGIN
L_00058336:
    extu.w r0,r2
    .org 0x58338-ORIGIN
L_00058338:
    cmp/ge r6,r2
    .org 0x5833a-ORIGIN
L_0005833a:
    bt/s L_000583de
    .org 0x5833c-ORIGIN
L_0005833c:
    mov.w r0,@(0x4,r15)
    .org 0x5833e-ORIGIN
L_0005833e:
    bra L_00058440
    .org 0x58340-ORIGIN
L_00058340:
    nop
    .org 0x58354-ORIGIN
P_00058354:
    .byte 0xff
    .org 0x58355-ORIGIN
P_00058355:
    .byte 0xff
    .org 0x58356-ORIGIN
P_00058356:
    .byte 0x56
    .org 0x58357-ORIGIN
P_00058357:
    .byte 0x48
    .org 0x58358-ORIGIN
P_00058358:
    .byte 0x00
    .org 0x58359-ORIGIN
P_00058359:
    .byte 0x00
    .org 0x5835a-ORIGIN
P_0005835a:
    .byte 0x87
    .org 0x5835b-ORIGIN
P_0005835b:
    .byte 0x8b
    .org 0x5835c-ORIGIN
P_0005835c:
    .byte 0xff
    .org 0x5835d-ORIGIN
P_0005835d:
    .byte 0xff
    .org 0x5835e-ORIGIN
P_0005835e:
    .byte 0x23
    .org 0x5835f-ORIGIN
P_0005835f:
    .byte 0x02
    .org 0x58360-ORIGIN
P_00058360:
    .byte 0x00
    .org 0x58361-ORIGIN
P_00058361:
    .byte 0x02
    .org 0x58362-ORIGIN
P_00058362:
    .byte 0x1b
    .org 0x58363-ORIGIN
P_00058363:
    .byte 0xbc
    .org 0x58364-ORIGIN
P_00058364:
    .byte 0xff
    .org 0x58365-ORIGIN
P_00058365:
    .byte 0xff
    .org 0x58366-ORIGIN
P_00058366:
    .byte 0x22
    .org 0x58367-ORIGIN
P_00058367:
    .byte 0xdc
    .org 0x58368-ORIGIN
P_00058368:
    .byte 0xff
    .org 0x58369-ORIGIN
P_00058369:
    .byte 0xff
    .org 0x5836a-ORIGIN
P_0005836a:
    .byte 0x22
    .org 0x5836b-ORIGIN
P_0005836b:
    .byte 0xf8
    .org 0x5836c-ORIGIN
P_0005836c:
    .byte 0xff
    .org 0x5836d-ORIGIN
P_0005836d:
    .byte 0xff
    .org 0x5836e-ORIGIN
P_0005836e:
    .byte 0x44
    .org 0x5836f-ORIGIN
P_0005836f:
    .byte 0x97
    .org 0x58370-ORIGIN
P_00058370:
    .byte 0xff
    .org 0x58371-ORIGIN
P_00058371:
    .byte 0xff
    .org 0x58372-ORIGIN
P_00058372:
    .byte 0x39
    .org 0x58373-ORIGIN
P_00058373:
    .byte 0xc4
    .org 0x58374-ORIGIN
P_00058374:
    .byte 0xff
    .org 0x58375-ORIGIN
P_00058375:
    .byte 0xff
    .org 0x58376-ORIGIN
P_00058376:
    .byte 0x13
    .org 0x58377-ORIGIN
P_00058377:
    .byte 0x06
    .org 0x58378-ORIGIN
P_00058378:
    .byte 0xff
    .org 0x58379-ORIGIN
P_00058379:
    .byte 0xff
    .org 0x5837a-ORIGIN
P_0005837a:
    .byte 0x23
    .org 0x5837b-ORIGIN
P_0005837b:
    .byte 0x06
    .org 0x5837c-ORIGIN
P_0005837c:
    .byte 0x00
    .org 0x5837d-ORIGIN
P_0005837d:
    .byte 0x00
    .org 0x5837e-ORIGIN
P_0005837e:
    .byte 0x87
    .org 0x5837f-ORIGIN
P_0005837f:
    .byte 0x8f
    .org 0x58380-ORIGIN
P_00058380:
    .byte 0x00
    .org 0x58381-ORIGIN
P_00058381:
    .byte 0x00
    .org 0x58382-ORIGIN
P_00058382:
    .byte 0x86
    .org 0x58383-ORIGIN
P_00058383:
    .byte 0xbe
    .org 0x58384-ORIGIN
P_00058384:
    .byte 0x00
    .org 0x58385-ORIGIN
P_00058385:
    .byte 0x00
    .org 0x58386-ORIGIN
P_00058386:
    .byte 0x87
    .org 0x58387-ORIGIN
P_00058387:
    .byte 0x90
    .org 0x58388-ORIGIN
P_00058388:
    .byte 0x00
    .org 0x58389-ORIGIN
P_00058389:
    .byte 0x00
    .org 0x5838a-ORIGIN
P_0005838a:
    .byte 0x86
    .org 0x5838b-ORIGIN
P_0005838b:
    .byte 0xbf
    .org 0x5838c-ORIGIN
L_0005838c:
    mov.w P_000583d0,r0
    .org 0x5838e-ORIGIN
L_0005838e:
    mov.b @(r0,r5),r6
    .org 0x58390-ORIGIN
L_00058390:
    extu.b r6,r6
    .org 0x58392-ORIGIN
L_00058392:
    tst r11,r6
    .org 0x58394-ORIGIN
L_00058394:
    bt L_0005839e
    .org 0x58396-ORIGIN
L_00058396:
    mov.l P_000585b0,r7
    .org 0x58398-ORIGIN
L_00058398:
    mov.b @(0x1,r7),r0
    .org 0x5839a-ORIGIN
L_0005839a:
    tst #0x8,r0
    .org 0x5839c-ORIGIN
L_0005839c:
    bt L_00058440
    .org 0x5839e-ORIGIN
L_0005839e:
    mov.w @r15,r5
    .org 0x583a0-ORIGIN
L_000583a0:
    mov #0x64,r4
    .org 0x583a2-ORIGIN
L_000583a2:
    shll8 r4
    .org 0x583a4-ORIGIN
L_000583a4:
    extu.w r5,r5
    .org 0x583a6-ORIGIN
L_000583a6:
    cmp/gt r4,r5
    .org 0x583a8-ORIGIN
L_000583a8:
    bf L_000583c0
    .org 0x583aa-ORIGIN
L_000583aa:
    mov r5,r0
    .org 0x583ac-ORIGIN
L_000583ac:
    sub r2,r0
    .org 0x583ae-ORIGIN
L_000583ae:
    mov #0x64,r4
    .org 0x583b0-ORIGIN
L_000583b0:
    extu.w r0,r6
    .org 0x583b2-ORIGIN
L_000583b2:
    shll8 r4
    .org 0x583b4-ORIGIN
L_000583b4:
    cmp/gt r4,r6
    .org 0x583b6-ORIGIN
L_000583b6:
    bt/s L_000583c0
    .org 0x583b8-ORIGIN
L_000583b8:
    mov.w r0,@(0x4,r15)
    .org 0x583ba-ORIGIN
L_000583ba:
    mov #0x64,r0
    .org 0x583bc-ORIGIN
L_000583bc:
    shll8 r0
    .org 0x583be-ORIGIN
L_000583be:
    mov.w r0,@(0x4,r15)
    .org 0x583c0-ORIGIN
L_000583c0:
    mov #0x64,r4
    .org 0x583c2-ORIGIN
L_000583c2:
    shll8 r4
    .org 0x583c4-ORIGIN
L_000583c4:
    cmp/ge r4,r5
    .org 0x583c6-ORIGIN
L_000583c6:
    bt L_00058440
    .org 0x583c8-ORIGIN
L_000583c8:
    add r2,r5
    .org 0x583ca-ORIGIN
L_000583ca:
    mov #0x64,r2
    .org 0x583cc-ORIGIN
L_000583cc:
    bra L_000583d2
    .org 0x583ce-ORIGIN
L_000583ce:
    mov.w r5,@r15
    .org 0x583d0-ORIGIN
P_000583d0:
    .byte 0x04
    .org 0x583d1-ORIGIN
P_000583d1:
    .byte 0xe0
    .org 0x583d2-ORIGIN
L_000583d2:
    mov r5,r0
    .org 0x583d4-ORIGIN
L_000583d4:
    extu.w r5,r5
    .org 0x583d6-ORIGIN
L_000583d6:
    shll8 r2
    .org 0x583d8-ORIGIN
L_000583d8:
    cmp/ge r2,r5
    .org 0x583da-ORIGIN
L_000583da:
    bf/s L_00058440
    .org 0x583dc-ORIGIN
L_000583dc:
    mov.w r0,@(0x4,r15)
    .org 0x583de-ORIGIN
L_000583de:
    mov #0x64,r0
    .org 0x583e0-ORIGIN
L_000583e0:
    bra L_0005843e
    .org 0x583e2-ORIGIN
L_000583e2:
    shll8 r0
    .org 0x583e4-ORIGIN
L_000583e4:
    mov.l P_000585b4,r5
    .org 0x583e6-ORIGIN
L_000583e6:
    mov.w P_00058528,r0
    .org 0x583e8-ORIGIN
L_000583e8:
    mov.b @(r0,r5),r6
    .org 0x583ea-ORIGIN
L_000583ea:
    extu.b r6,r6
    .org 0x583ec-ORIGIN
L_000583ec:
    tst r11,r6
    .org 0x583ee-ORIGIN
L_000583ee:
    bt L_00058440
    .org 0x583f0-ORIGIN
L_000583f0:
    not r13,r2
    .org 0x583f2-ORIGIN
L_000583f2:
    and r2,r6
    .org 0x583f4-ORIGIN
L_000583f4:
    mov.b r6,@(r0,r5)
    .org 0x583f6-ORIGIN
L_000583f6:
    mov.l P_000585b8,r5
    .org 0x583f8-ORIGIN
L_000583f8:
    mov.w P_0005852a,r0
    .org 0x583fa-ORIGIN
L_000583fa:
    mov.b @(r0,r5),r2
    .org 0x583fc-ORIGIN
L_000583fc:
    extu.b r2,r6
    .org 0x583fe-ORIGIN
L_000583fe:
    tst r11,r6
    .org 0x58400-ORIGIN
L_00058400:
    bt L_00058440
    .org 0x58402-ORIGIN
L_00058402:
    mov.l P_000585bc,r2
    .org 0x58404-ORIGIN
L_00058404:
    mov r10,r0
    .org 0x58406-ORIGIN
L_00058406:
    mov.w @r2,r7
    .org 0x58408-ORIGIN
L_00058408:
    mov.l P_000585c0,r2
    .org 0x5840a-ORIGIN
L_0005840a:
    extu.w r7,r7
    .org 0x5840c-ORIGIN
L_0005840c:
    mov.w @(r0,r2),r6
    .org 0x5840e-ORIGIN
L_0005840e:
    extu.w r6,r6
    .org 0x58410-ORIGIN
L_00058410:
    cmp/gt r6,r7
    .org 0x58412-ORIGIN
L_00058412:
    bf L_00058424
    .org 0x58414-ORIGIN
L_00058414:
    mov.l P_000585c4,r2
    .org 0x58416-ORIGIN
L_00058416:
    mov.w @r15,r0
    .org 0x58418-ORIGIN
L_00058418:
    mov.b @r2,r6
    .org 0x5841a-ORIGIN
L_0005841a:
    extu.b r6,r6
    .org 0x5841c-ORIGIN
L_0005841c:
    shll2 r6
    .org 0x5841e-ORIGIN
L_0005841e:
    shll2 r6
    .org 0x58420-ORIGIN
L_00058420:
    bra L_0005843c
    .org 0x58422-ORIGIN
L_00058422:
    sub r6,r0
    .org 0x58424-ORIGIN
L_00058424:
    mov.l P_000585c8,r5
    .org 0x58426-ORIGIN
L_00058426:
    mov.w @r5,r2
    .org 0x58428-ORIGIN
L_00058428:
    extu.w r2,r2
    .org 0x5842a-ORIGIN
L_0005842a:
    cmp/ge r6,r2
    .org 0x5842c-ORIGIN
L_0005842c:
    bt L_00058440
    .org 0x5842e-ORIGIN
L_0005842e:
    mov.l P_000585c4,r2
    .org 0x58430-ORIGIN
L_00058430:
    mov.w @r15,r0
    .org 0x58432-ORIGIN
L_00058432:
    mov.b @r2,r6
    .org 0x58434-ORIGIN
L_00058434:
    extu.b r6,r2
    .org 0x58436-ORIGIN
L_00058436:
    shll2 r2
    .org 0x58438-ORIGIN
L_00058438:
    shll2 r2
    .org 0x5843a-ORIGIN
L_0005843a:
    add r2,r0
    .org 0x5843c-ORIGIN
L_0005843c:
    mov.w r0,@r15
    .org 0x5843e-ORIGIN
L_0005843e:
    mov.w r0,@(0x4,r15)
    .org 0x58440-ORIGIN
L_00058440:
    mov.l P_000585cc,r3
    .org 0x58442-ORIGIN
L_00058442:
    mov.w @(0x4,r15),r0
    .org 0x58444-ORIGIN
L_00058444:
    mov.b @r3,r5
    .org 0x58446-ORIGIN
L_00058446:
    extu.w r0,r4
    .org 0x58448-ORIGIN
L_00058448:
    extu.b r5,r5
    .org 0x5844a-ORIGIN
L_0005844a:
    mov r5,r2
    .org 0x5844c-ORIGIN
L_0005844c:
    shll8 r2
    .org 0x5844e-ORIGIN
L_0005844e:
    extu.w r2,r2
    .org 0x58450-ORIGIN
L_00058450:
    cmp/gt r2,r4
    .org 0x58452-ORIGIN
L_00058452:
    bf L_00058458
    .org 0x58454-ORIGIN
L_00058454:
    shll8 r5
    .org 0x58456-ORIGIN
L_00058456:
    mov r5,r4
    .org 0x58458-ORIGIN
L_00058458:
    mov.l P_000585d0,r3
    .org 0x5845a-ORIGIN
L_0005845a:
    extu.w r4,r4
    .org 0x5845c-ORIGIN
L_0005845c:
    mov.b @r3,r7
    .org 0x5845e-ORIGIN
L_0005845e:
    extu.b r7,r7
    .org 0x58460-ORIGIN
L_00058460:
    mov r7,r6
    .org 0x58462-ORIGIN
L_00058462:
    shll8 r6
    .org 0x58464-ORIGIN
L_00058464:
    extu.w r6,r2
    .org 0x58466-ORIGIN
L_00058466:
    cmp/ge r2,r4
    .org 0x58468-ORIGIN
L_00058468:
    bt L_00058470
    .org 0x5846a-ORIGIN
L_0005846a:
    shll8 r7
    .org 0x5846c-ORIGIN
L_0005846c:
    bra L_00058472
    .org 0x5846e-ORIGIN
L_0005846e:
    mov r7,r2
    .org 0x58470-ORIGIN
L_00058470:
    mov r4,r2
    .org 0x58472-ORIGIN
L_00058472:
    mov r2,r14
    .org 0x58474-ORIGIN
L_00058474:
    mov.l P_000585d4,r2
    .org 0x58476-ORIGIN
L_00058476:
    mov.w P_0005852c,r4
    .org 0x58478-ORIGIN
L_00058478:
    jsr @r2
    .org 0x5847a-ORIGIN
L_0005847a:
    nop
    .org 0x5847c-ORIGIN
L_0005847c:
    tst r0,r0
    .org 0x5847e-ORIGIN
L_0005847e:
    bf L_00058488
    .org 0x58480-ORIGIN
L_00058480:
    mov.l P_000585d8,r6
    .org 0x58482-ORIGIN
L_00058482:
    mov.b @(0xc,r6),r0
    .org 0x58484-ORIGIN
L_00058484:
    tst #0x1,r0
    .org 0x58486-ORIGIN
L_00058486:
    bt L_0005848c
    .org 0x58488-ORIGIN
L_00058488:
    mov #0x64,r14
    .org 0x5848a-ORIGIN
L_0005848a:
    shll8 r14
    .org 0x5848c-ORIGIN
L_0005848c:
    mov r10,r0
    .org 0x5848e-ORIGIN
L_0005848e:
    mov.w r14,@(r0,r9)
    .org 0x58490-ORIGIN
L_00058490:
    mov.l P_000585b8,r5
    .org 0x58492-ORIGIN
L_00058492:
    mov.w P_0005852a,r0
    .org 0x58494-ORIGIN
L_00058494:
    mov.b @(r0,r5),r2
    .org 0x58496-ORIGIN
L_00058496:
    extu.b r2,r6
    .org 0x58498-ORIGIN
L_00058498:
    tst r11,r6
    .org 0x5849a-ORIGIN
L_0005849a:
    bt L_000584a8
    .org 0x5849c-ORIGIN
L_0005849c:
    mov.l P_000585dc,r5
    .org 0x5849e-ORIGIN
L_0005849e:
    mov #0x72,r0
    .org 0x584a0-ORIGIN
L_000584a0:
    mov.b @(r0,r5),r2
    .org 0x584a2-ORIGIN
L_000584a2:
    or r13,r2
    .org 0x584a4-ORIGIN
L_000584a4:
    bra L_000584b4
    .org 0x584a6-ORIGIN
L_000584a6:
    mov.b r2,@(r0,r5)
    .org 0x584a8-ORIGIN
L_000584a8:
    mov.l P_000585dc,r5
    .org 0x584aa-ORIGIN
L_000584aa:
    mov #0x72,r0
    .org 0x584ac-ORIGIN
L_000584ac:
    not r13,r2
    .org 0x584ae-ORIGIN
L_000584ae:
    mov.b @(r0,r5),r6
    .org 0x584b0-ORIGIN
L_000584b0:
    and r2,r6
    .org 0x584b2-ORIGIN
L_000584b2:
    mov.b r6,@(r0,r5)
    .org 0x584b4-ORIGIN
L_000584b4:
    add #0x20,r15
    .org 0x584b6-ORIGIN
L_000584b6:
    lds.l @r15+,macl
    .org 0x584b8-ORIGIN
L_000584b8:
    lds.l @r15+,pr
    .org 0x584ba-ORIGIN
L_000584ba:
    mov.l @r15+,r14
    .org 0x584bc-ORIGIN
L_000584bc:
    mov.l @r15+,r13
    .org 0x584be-ORIGIN
L_000584be:
    mov.l @r15+,r12
    .org 0x584c0-ORIGIN
L_000584c0:
    mov.l @r15+,r11
    .org 0x584c2-ORIGIN
L_000584c2:
    mov.l @r15+,r10
    .org 0x584c4-ORIGIN
L_000584c4:
    mov.l @r15+,r9
    .org 0x584c6-ORIGIN
L_000584c6:
    rts
    .org 0x584c8-ORIGIN
L_000584c8:
    mov.l @r15+,r8
    .org 0x58528-ORIGIN
P_00058528:
    .byte 0x07
    .org 0x58529-ORIGIN
P_00058529:
    .byte 0x8a
    .org 0x5852a-ORIGIN
P_0005852a:
    .byte 0x04
    .org 0x5852b-ORIGIN
P_0005852b:
    .byte 0x6c
    .org 0x5852c-ORIGIN
P_0005852c:
    .byte 0x01
    .org 0x5852d-ORIGIN
P_0005852d:
    .byte 0x29
    .org 0x585b0-ORIGIN
P_000585b0:
    .byte 0xff
    .org 0x585b1-ORIGIN
P_000585b1:
    .byte 0xff
    .org 0x585b2-ORIGIN
P_000585b2:
    .byte 0x24
    .org 0x585b3-ORIGIN
P_000585b3:
    .byte 0x60
    .org 0x585b4-ORIGIN
P_000585b4:
    .byte 0xff
    .org 0x585b5-ORIGIN
P_000585b5:
    .byte 0xff
    .org 0x585b6-ORIGIN
P_000585b6:
    .byte 0x28
    .org 0x585b7-ORIGIN
P_000585b7:
    .byte 0xf8
    .org 0x585b8-ORIGIN
P_000585b8:
    .byte 0xff
    .org 0x585b9-ORIGIN
P_000585b9:
    .byte 0xff
    .org 0x585ba-ORIGIN
P_000585ba:
    .byte 0x39
    .org 0x585bb-ORIGIN
P_000585bb:
    .byte 0xc4
    .org 0x585bc-ORIGIN
P_000585bc:
    .byte 0x00
    .org 0x585bd-ORIGIN
P_000585bd:
    .byte 0x00
    .org 0x585be-ORIGIN
P_000585be:
    .byte 0x8f
    .org 0x585bf-ORIGIN
P_000585bf:
    .byte 0xa8
    .org 0x585c0-ORIGIN
P_000585c0:
    .byte 0xff
    .org 0x585c1-ORIGIN
P_000585c1:
    .byte 0xff
    .org 0x585c2-ORIGIN
P_000585c2:
    .byte 0x29
    .org 0x585c3-ORIGIN
P_000585c3:
    .byte 0xe2
    .org 0x585c4-ORIGIN
P_000585c4:
    .byte 0x00
    .org 0x585c5-ORIGIN
P_000585c5:
    .byte 0x00
    .org 0x585c6-ORIGIN
P_000585c6:
    .byte 0x87
    .org 0x585c7-ORIGIN
P_000585c7:
    .byte 0x8c
    .org 0x585c8-ORIGIN
P_000585c8:
    .byte 0x00
    .org 0x585c9-ORIGIN
P_000585c9:
    .byte 0x00
    .org 0x585ca-ORIGIN
P_000585ca:
    .byte 0x8f
    .org 0x585cb-ORIGIN
P_000585cb:
    .byte 0xa6
    .org 0x585cc-ORIGIN
P_000585cc:
    .byte 0x00
    .org 0x585cd-ORIGIN
P_000585cd:
    .byte 0x00
    .org 0x585ce-ORIGIN
P_000585ce:
    .byte 0x86
    .org 0x585cf-ORIGIN
P_000585cf:
    .byte 0xbe
    .org 0x585d0-ORIGIN
P_000585d0:
    .byte 0x00
    .org 0x585d1-ORIGIN
P_000585d1:
    .byte 0x00
    .org 0x585d2-ORIGIN
P_000585d2:
    .byte 0x86
    .org 0x585d3-ORIGIN
P_000585d3:
    .byte 0xbf
    .org 0x585d4-ORIGIN
P_000585d4:
    .byte 0x00
    .org 0x585d5-ORIGIN
P_000585d5:
    .byte 0x02
    .org 0x585d6-ORIGIN
P_000585d6:
    .byte 0x5e
    .org 0x585d7-ORIGIN
P_000585d7:
    .byte 0x20
    .org 0x585d8-ORIGIN
P_000585d8:
    .byte 0xff
    .org 0x585d9-ORIGIN
P_000585d9:
    .byte 0xff
    .org 0x585da-ORIGIN
P_000585da:
    .byte 0x41
    .org 0x585db-ORIGIN
P_000585db:
    .byte 0xa9
    .org 0x585dc-ORIGIN
P_000585dc:
    .byte 0xff
    .org 0x585dd-ORIGIN
P_000585dd:
    .byte 0xff
    .org 0x585de-ORIGIN
P_000585de:
    .byte 0x12
    .org 0x585df-ORIGIN
P_000585df:
    .byte 0x8c
