! Exact complete scaling/division callers with real arithmetic-shift and signed-divider helpers.
    .text
    .balign 4
    .set ORIGIN,0x944c
    .org 0x944e-ORIGIN
P_0000944e:
    .byte 0x35
    .org 0x944f-ORIGIN
P_0000944f:
    .byte 0x1e
    .org 0x16316-ORIGIN
P_00016316:
    .byte 0x35
    .org 0x16317-ORIGIN
P_00016317:
    .byte 0x1e
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
    .org 0x4e59c-ORIGIN
L_0004e59c:
    sts.l pr,@-r15
    .org 0x4e59e-ORIGIN
L_0004e59e:
    sts.l macl,@-r15
    .org 0x4e5a0-ORIGIN
L_0004e5a0:
    stc.l gbr,@-r15
    .org 0x4e5a2-ORIGIN
L_0004e5a2:
    mov.l P_0004e60c,r0
    .org 0x4e5a4-ORIGIN
L_0004e5a4:
    ldc r0,gbr
    .org 0x4e5a6-ORIGIN
L_0004e5a6:
    mov.l P_0004e60c,r4
    .org 0x4e5a8-ORIGIN
L_0004e5a8:
    mov #-0x1,r5
    .org 0x4e5aa-ORIGIN
L_0004e5aa:
    mov.w P_0004e604,r0
    .org 0x4e5ac-ORIGIN
L_0004e5ac:
    extu.w r5,r5
    .org 0x4e5ae-ORIGIN
L_0004e5ae:
    mov.w @(r0,r4),r6
    .org 0x4e5b0-ORIGIN
L_0004e5b0:
    mov.w P_0004e606,r0
    .org 0x4e5b2-ORIGIN
L_0004e5b2:
    extu.w r6,r6
    .org 0x4e5b4-ORIGIN
L_0004e5b4:
    mov.b @(r0,r4),r2
    .org 0x4e5b6-ORIGIN
L_0004e5b6:
    extu.b r2,r2
    .org 0x4e5b8-ORIGIN
L_0004e5b8:
    mul.l r6,r2
    .org 0x4e5ba-ORIGIN
L_0004e5ba:
    sts macl,r6
    .org 0x4e5bc-ORIGIN
L_0004e5bc:
    mov r6,r2
    .org 0x4e5be-ORIGIN
L_0004e5be:
    shll r2
    .org 0x4e5c0-ORIGIN
L_0004e5c0:
    add r6,r2
    .org 0x4e5c2-ORIGIN
L_0004e5c2:
    shll r2
    .org 0x4e5c4-ORIGIN
L_0004e5c4:
    shlr8 r2
    .org 0x4e5c6-ORIGIN
L_0004e5c6:
    shlr2 r2
    .org 0x4e5c8-ORIGIN
L_0004e5c8:
    shlr2 r2
    .org 0x4e5ca-ORIGIN
L_0004e5ca:
    shlr2 r2
    .org 0x4e5cc-ORIGIN
L_0004e5cc:
    shlr r2
    .org 0x4e5ce-ORIGIN
L_0004e5ce:
    cmp/hi r5,r2
    .org 0x4e5d0-ORIGIN
L_0004e5d0:
    bf L_0004e5d4
    .org 0x4e5d2-ORIGIN
L_0004e5d2:
    mov r5,r2
    .org 0x4e5d4-ORIGIN
L_0004e5d4:
    mov.l P_0004e610,r6
    .org 0x4e5d6-ORIGIN
L_0004e5d6:
    mov #0x1,r1
    .org 0x4e5d8-ORIGIN
L_0004e5d8:
    mov r2,r0
    .org 0x4e5da-ORIGIN
L_0004e5da:
    mov.w r0,@(0x36,gbr)
    .org 0x4e5dc-ORIGIN
L_0004e5dc:
    extu.w r2,r0
    .org 0x4e5de-ORIGIN
L_0004e5de:
    jsr @r6
    .org 0x4e5e0-ORIGIN
L_0004e5e0:
    shll16 r1
    .org 0x4e5e2-ORIGIN
L_0004e5e2:
    mov #0x1,r6
    .org 0x4e5e4-ORIGIN
L_0004e5e4:
    shll8 r6
    .org 0x4e5e6-ORIGIN
L_0004e5e6:
    mov #-0x1,r5
    .org 0x4e5e8-ORIGIN
L_0004e5e8:
    add r6,r0
    .org 0x4e5ea-ORIGIN
L_0004e5ea:
    extu.w r5,r5
    .org 0x4e5ec-ORIGIN
L_0004e5ec:
    cmp/hi r5,r0
    .org 0x4e5ee-ORIGIN
L_0004e5ee:
    bf/s L_0004e5f4
    .org 0x4e5f0-ORIGIN
L_0004e5f0:
    mov r0,r2
    .org 0x4e5f2-ORIGIN
L_0004e5f2:
    mov r5,r2
    .org 0x4e5f4-ORIGIN
L_0004e5f4:
    mov.l P_0004e60c,r4
    .org 0x4e5f6-ORIGIN
L_0004e5f6:
    mov.w P_0004e608,r0
    .org 0x4e5f8-ORIGIN
L_0004e5f8:
    mov.w r2,@(r0,r4)
    .org 0x4e5fa-ORIGIN
L_0004e5fa:
    ldc.l @r15+,gbr
    .org 0x4e5fc-ORIGIN
L_0004e5fc:
    lds.l @r15+,macl
    .org 0x4e5fe-ORIGIN
L_0004e5fe:
    lds.l @r15+,pr
    .org 0x4e600-ORIGIN
L_0004e600:
    rts
    .org 0x4e602-ORIGIN
L_0004e602:
    nop
    .org 0x4e604-ORIGIN
P_0004e604:
    .byte 0x03
    .org 0x4e605-ORIGIN
P_0004e605:
    .byte 0xc6
    .org 0x4e606-ORIGIN
P_0004e606:
    .byte 0x03
    .org 0x4e607-ORIGIN
P_0004e607:
    .byte 0x52
    .org 0x4e608-ORIGIN
P_0004e608:
    .byte 0x04
    .org 0x4e609-ORIGIN
P_0004e609:
    .byte 0x34
    .org 0x4e60c-ORIGIN
P_0004e60c:
    .byte 0xff
    .org 0x4e60d-ORIGIN
P_0004e60d:
    .byte 0xff
    .org 0x4e60e-ORIGIN
P_0004e60e:
    .byte 0x12
    .org 0x4e60f-ORIGIN
P_0004e60f:
    .byte 0x8c
    .org 0x4e610-ORIGIN
P_0004e610:
    .byte 0x00
    .org 0x4e611-ORIGIN
P_0004e611:
    .byte 0x02
    .org 0x4e612-ORIGIN
P_0004e612:
    .byte 0x1b
    .org 0x4e613-ORIGIN
P_0004e613:
    .byte 0xbc
    .org 0x74478-ORIGIN
L_00074478:
    mov.l r14,@-r15
    .org 0x7447a-ORIGIN
L_0007447a:
    sts.l pr,@-r15
    .org 0x7447c-ORIGIN
L_0007447c:
    sts.l macl,@-r15
    .org 0x7447e-ORIGIN
L_0007447e:
    mov.l P_0007453c,r14
    .org 0x74480-ORIGIN
L_00074480:
    mov.w P_0007452c,r0
    .org 0x74482-ORIGIN
L_00074482:
    mov.w @(r0,r14),r6
    .org 0x74484-ORIGIN
L_00074484:
    mov.w P_0007452e,r0
    .org 0x74486-ORIGIN
L_00074486:
    extu.w r6,r6
    .org 0x74488-ORIGIN
L_00074488:
    mov.w @(r0,r14),r2
    .org 0x7448a-ORIGIN
L_0007448a:
    extu.w r2,r2
    .org 0x7448c-ORIGIN
L_0007448c:
    mul.l r6,r2
    .org 0x7448e-ORIGIN
L_0007448e:
    mov.l P_00074540,r6
    .org 0x74490-ORIGIN
L_00074490:
    jsr @r6
    .org 0x74492-ORIGIN
L_00074492:
    sts macl,r0
    .org 0x74494-ORIGIN
L_00074494:
    mov r0,r2
    .org 0x74496-ORIGIN
L_00074496:
    mov.w P_00074530,r0
    .org 0x74498-ORIGIN
L_00074498:
    mov.l P_00074544,r5
    .org 0x7449a-ORIGIN
L_0007449a:
    mov.w @(r0,r14),r6
    .org 0x7449c-ORIGIN
L_0007449c:
    mul.l r2,r6
    .org 0x7449e-ORIGIN
L_0007449e:
    mov.w @r5,r6
    .org 0x744a0-ORIGIN
L_000744a0:
    mov.l P_00074548,r5
    .org 0x744a2-ORIGIN
L_000744a2:
    sts macl,r1
    .org 0x744a4-ORIGIN
L_000744a4:
    jsr @r5
    .org 0x744a6-ORIGIN
L_000744a6:
    extu.w r6,r0
    .org 0x744a8-ORIGIN
L_000744a8:
    mov.w P_00074532,r6
    .org 0x744aa-ORIGIN
L_000744aa:
    cmp/gt r6,r0
    .org 0x744ac-ORIGIN
L_000744ac:
    bf/s L_000744b2
    .org 0x744ae-ORIGIN
L_000744ae:
    mov r0,r2
    .org 0x744b0-ORIGIN
L_000744b0:
    mov r6,r2
    .org 0x744b2-ORIGIN
L_000744b2:
    mov #-0x80,r6
    .org 0x744b4-ORIGIN
L_000744b4:
    shll8 r6
    .org 0x744b6-ORIGIN
L_000744b6:
    cmp/ge r6,r2
    .org 0x744b8-ORIGIN
L_000744b8:
    bt L_000744bc
    .org 0x744ba-ORIGIN
L_000744ba:
    mov r6,r2
    .org 0x744bc-ORIGIN
L_000744bc:
    mov.w P_00074534,r0
    .org 0x744be-ORIGIN
L_000744be:
    exts.w r2,r4
    .org 0x744c0-ORIGIN
L_000744c0:
    mov.l P_0007454c,r6
    .org 0x744c2-ORIGIN
L_000744c2:
    mov.w r4,@(r0,r14)
    .org 0x744c4-ORIGIN
L_000744c4:
    mov.b @(0x3,r6),r0
    .org 0x744c6-ORIGIN
L_000744c6:
    tst #0x80,r0
    .org 0x744c8-ORIGIN
L_000744c8:
    movt r0
    .org 0x744ca-ORIGIN
L_000744ca:
    mov.l P_00074550,r6
    .org 0x744cc-ORIGIN
L_000744cc:
    xor #0x1,r0
    .org 0x744ce-ORIGIN
L_000744ce:
    mov r0,r5
    .org 0x744d0-ORIGIN
L_000744d0:
    mov.b @r6,r0
    .org 0x744d2-ORIGIN
L_000744d2:
    tst #0x8,r0
    .org 0x744d4-ORIGIN
L_000744d4:
    movt r0
    .org 0x744d6-ORIGIN
L_000744d6:
    mov.l P_00074554,r2
    .org 0x744d8-ORIGIN
L_000744d8:
    xor #0x1,r0
    .org 0x744da-ORIGIN
L_000744da:
    or r0,r5
    .org 0x744dc-ORIGIN
L_000744dc:
    mov #0x2b,r0
    .org 0x744de-ORIGIN
L_000744de:
    mov.b @(r0,r2),r0
    .org 0x744e0-ORIGIN
L_000744e0:
    and #0x1,r0
    .org 0x744e2-ORIGIN
L_000744e2:
    or r0,r5
    .org 0x744e4-ORIGIN
L_000744e4:
    extu.b r5,r5
    .org 0x744e6-ORIGIN
L_000744e6:
    tst r5,r5
    .org 0x744e8-ORIGIN
L_000744e8:
    bt L_000744f0
    .org 0x744ea-ORIGIN
L_000744ea:
    mov.w P_00074536,r0
    .org 0x744ec-ORIGIN
L_000744ec:
    bra L_00074524
    .org 0x744ee-ORIGIN
L_000744ee:
    mov.w r4,@(r0,r14)
    .org 0x744f0-ORIGIN
L_000744f0:
    mov.l P_00074558,r2
    .org 0x744f2-ORIGIN
L_000744f2:
    mov #0x66,r0
    .org 0x744f4-ORIGIN
L_000744f4:
    mov.w @(r0,r2),r5
    .org 0x744f6-ORIGIN
L_000744f6:
    extu.w r5,r5
    .org 0x744f8-ORIGIN
L_000744f8:
    tst r5,r5
    .org 0x744fa-ORIGIN
L_000744fa:
    bt L_00074520
    .org 0x744fc-ORIGIN
L_000744fc:
    mov #-0x1,r6
    .org 0x744fe-ORIGIN
L_000744fe:
    extu.w r6,r6
    .org 0x74500-ORIGIN
L_00074500:
    cmp/eq r6,r5
    .org 0x74502-ORIGIN
L_00074502:
    bf L_0007450a
    .org 0x74504-ORIGIN
L_00074504:
    mov.w P_00074538,r0
    .org 0x74506-ORIGIN
L_00074506:
    bra L_00074520
    .org 0x74508-ORIGIN
L_00074508:
    mov.w @(r0,r14),r4
    .org 0x7450a-ORIGIN
L_0007450a:
    mov #0x1,r2
    .org 0x7450c-ORIGIN
L_0007450c:
    mov.w P_00074538,r0
    .org 0x7450e-ORIGIN
L_0007450e:
    shll16 r2
    .org 0x74510-ORIGIN
L_00074510:
    sub r5,r2
    .org 0x74512-ORIGIN
L_00074512:
    mul.l r4,r2
    .org 0x74514-ORIGIN
L_00074514:
    mov.w @(r0,r14),r2
    .org 0x74516-ORIGIN
L_00074516:
    sts macl,r6
    .org 0x74518-ORIGIN
L_00074518:
    mul.l r2,r5
    .org 0x7451a-ORIGIN
L_0007451a:
    sts macl,r2
    .org 0x7451c-ORIGIN
L_0007451c:
    add r2,r6
    .org 0x7451e-ORIGIN
L_0007451e:
    swap.w r6,r4
    .org 0x74520-ORIGIN
L_00074520:
    mov.w P_00074536,r0
    .org 0x74522-ORIGIN
L_00074522:
    mov.w r4,@(r0,r14)
    .org 0x74524-ORIGIN
L_00074524:
    lds.l @r15+,macl
    .org 0x74526-ORIGIN
L_00074526:
    lds.l @r15+,pr
    .org 0x74528-ORIGIN
L_00074528:
    rts
    .org 0x7452a-ORIGIN
L_0007452a:
    mov.l @r15+,r14
    .org 0x7452c-ORIGIN
P_0007452c:
    .byte 0x0a
    .org 0x7452d-ORIGIN
P_0007452d:
    .byte 0x42
    .org 0x7452e-ORIGIN
P_0007452e:
    .byte 0x0a
    .org 0x7452f-ORIGIN
P_0007452f:
    .byte 0x8a
    .org 0x74530-ORIGIN
P_00074530:
    .byte 0x0a
    .org 0x74531-ORIGIN
P_00074531:
    .byte 0x8e
    .org 0x74532-ORIGIN
P_00074532:
    .byte 0x7f
    .org 0x74533-ORIGIN
P_00074533:
    .byte 0xff
    .org 0x74534-ORIGIN
P_00074534:
    .byte 0x0a
    .org 0x74535-ORIGIN
P_00074535:
    .byte 0x6c
    .org 0x74536-ORIGIN
P_00074536:
    .byte 0x0a
    .org 0x74537-ORIGIN
P_00074537:
    .byte 0x74
    .org 0x74538-ORIGIN
P_00074538:
    .byte 0x0a
    .org 0x74539-ORIGIN
P_00074539:
    .byte 0x6a
    .org 0x7453c-ORIGIN
P_0007453c:
    .byte 0xff
    .org 0x7453d-ORIGIN
P_0007453d:
    .byte 0xff
    .org 0x7453e-ORIGIN
P_0007453e:
    .byte 0x12
    .org 0x7453f-ORIGIN
P_0007453f:
    .byte 0x8c
    .org 0x74540-ORIGIN
P_00074540:
    .byte 0x00
    .org 0x74541-ORIGIN
P_00074541:
    .byte 0x02
    .org 0x74542-ORIGIN
P_00074542:
    .byte 0x24
    .org 0x74543-ORIGIN
P_00074543:
    .byte 0xfa
    .org 0x74544-ORIGIN
P_00074544:
    .byte 0x00
    .org 0x74545-ORIGIN
P_00074545:
    .byte 0x01
    .org 0x74546-ORIGIN
P_00074546:
    .byte 0x63
    .org 0x74547-ORIGIN
P_00074547:
    .byte 0x16
    .org 0x74548-ORIGIN
P_00074548:
    .byte 0x00
    .org 0x74549-ORIGIN
P_00074549:
    .byte 0x02
    .org 0x7454a-ORIGIN
P_0007454a:
    .byte 0x1b
    .org 0x7454b-ORIGIN
P_0007454b:
    .byte 0xbc
    .org 0x7454c-ORIGIN
P_0007454c:
    .byte 0xff
    .org 0x7454d-ORIGIN
P_0007454d:
    .byte 0xff
    .org 0x7454e-ORIGIN
P_0007454e:
    .byte 0x24
    .org 0x7454f-ORIGIN
P_0007454f:
    .byte 0x5c
    .org 0x74550-ORIGIN
P_00074550:
    .byte 0xff
    .org 0x74551-ORIGIN
P_00074551:
    .byte 0xff
    .org 0x74552-ORIGIN
P_00074552:
    .byte 0x41
    .org 0x74553-ORIGIN
P_00074553:
    .byte 0x7e
    .org 0x74554-ORIGIN
P_00074554:
    .byte 0xff
    .org 0x74555-ORIGIN
P_00074555:
    .byte 0xff
    .org 0x74556-ORIGIN
P_00074556:
    .byte 0x24
    .org 0x74557-ORIGIN
P_00074557:
    .byte 0x70
    .org 0x74558-ORIGIN
P_00074558:
    .byte 0xff
    .org 0x74559-ORIGIN
P_00074559:
    .byte 0xff
    .org 0x7455a-ORIGIN
P_0007455a:
    .byte 0x23
    .org 0x7455b-ORIGIN
P_0007455b:
    .byte 0xbc
    .org 0x74b04-ORIGIN
L_00074b04:
    mov.l r13,@-r15
    .org 0x74b06-ORIGIN
L_00074b06:
    mov.l r14,@-r15
    .org 0x74b08-ORIGIN
L_00074b08:
    sts.l pr,@-r15
    .org 0x74b0a-ORIGIN
L_00074b0a:
    sts.l macl,@-r15
    .org 0x74b0c-ORIGIN
L_00074b0c:
    add #-0x4,r15
    .org 0x74b0e-ORIGIN
L_00074b0e:
    mov.l P_00074d24,r2
    .org 0x74b10-ORIGIN
L_00074b10:
    mov #0x40,r0
    .org 0x74b12-ORIGIN
L_00074b12:
    mov.l P_00074d28,r14
    .org 0x74b14-ORIGIN
L_00074b14:
    mov.w @(r0,r2),r6
    .org 0x74b16-ORIGIN
L_00074b16:
    mov.w P_00074c48,r0
    .org 0x74b18-ORIGIN
L_00074b18:
    extu.w r6,r6
    .org 0x74b1a-ORIGIN
L_00074b1a:
    mov.l P_00074d2c,r13
    .org 0x74b1c-ORIGIN
L_00074b1c:
    mov.w @(r0,r14),r2
    .org 0x74b1e-ORIGIN
L_00074b1e:
    extu.w r2,r2
    .org 0x74b20-ORIGIN
L_00074b20:
    mul.l r6,r2
    .org 0x74b22-ORIGIN
L_00074b22:
    mov.l P_00074d30,r6
    .org 0x74b24-ORIGIN
L_00074b24:
    jsr @r6
    .org 0x74b26-ORIGIN
L_00074b26:
    sts macl,r0
    .org 0x74b28-ORIGIN
L_00074b28:
    mov r0,r2
    .org 0x74b2a-ORIGIN
L_00074b2a:
    mov.w P_00074c4a,r0
    .org 0x74b2c-ORIGIN
L_00074b2c:
    mov.w @r13,r5
    .org 0x74b2e-ORIGIN
L_00074b2e:
    mov.w @(r0,r14),r6
    .org 0x74b30-ORIGIN
L_00074b30:
    mov.l P_00074d34,r7
    .org 0x74b32-ORIGIN
L_00074b32:
    extu.w r5,r0
    .org 0x74b34-ORIGIN
L_00074b34:
    mul.l r2,r6
    .org 0x74b36-ORIGIN
L_00074b36:
    sts macl,r1
    .org 0x74b38-ORIGIN
L_00074b38:
    jsr @r7
    .org 0x74b3a-ORIGIN
L_00074b3a:
    mov.l r1,@r15
    .org 0x74b3c-ORIGIN
L_00074b3c:
    mov.w P_00074c4c,r4
    .org 0x74b3e-ORIGIN
L_00074b3e:
    cmp/gt r4,r0
    .org 0x74b40-ORIGIN
L_00074b40:
    bt L_00074b4e
    .org 0x74b42-ORIGIN
L_00074b42:
    mov.w @r13,r5
    .org 0x74b44-ORIGIN
L_00074b44:
    mov.l @r15,r1
    .org 0x74b46-ORIGIN
L_00074b46:
    mov.l P_00074d34,r7
    .org 0x74b48-ORIGIN
L_00074b48:
    jsr @r7
    .org 0x74b4a-ORIGIN
L_00074b4a:
    extu.w r5,r0
    .org 0x74b4c-ORIGIN
L_00074b4c:
    mov r0,r4
    .org 0x74b4e-ORIGIN
L_00074b4e:
    mov #-0x80,r2
    .org 0x74b50-ORIGIN
L_00074b50:
    shll8 r2
    .org 0x74b52-ORIGIN
L_00074b52:
    cmp/ge r2,r4
    .org 0x74b54-ORIGIN
L_00074b54:
    bf L_00074b58
    .org 0x74b56-ORIGIN
L_00074b56:
    mov r4,r2
    .org 0x74b58-ORIGIN
L_00074b58:
    mov.w P_00074c4e,r0
    .org 0x74b5a-ORIGIN
L_00074b5a:
    mov.w r2,@(r0,r14)
    .org 0x74b5c-ORIGIN
L_00074b5c:
    add #0x4,r15
    .org 0x74b5e-ORIGIN
L_00074b5e:
    lds.l @r15+,macl
    .org 0x74b60-ORIGIN
L_00074b60:
    lds.l @r15+,pr
    .org 0x74b62-ORIGIN
L_00074b62:
    mov.l @r15+,r14
    .org 0x74b64-ORIGIN
L_00074b64:
    rts
    .org 0x74b66-ORIGIN
L_00074b66:
    mov.l @r15+,r13
    .org 0x74c48-ORIGIN
P_00074c48:
    .byte 0x07
    .org 0x74c49-ORIGIN
P_00074c49:
    .byte 0x16
    .org 0x74c4a-ORIGIN
P_00074c4a:
    .byte 0x07
    .org 0x74c4b-ORIGIN
P_00074c4b:
    .byte 0x2e
    .org 0x74c4c-ORIGIN
P_00074c4c:
    .byte 0x7f
    .org 0x74c4d-ORIGIN
P_00074c4d:
    .byte 0xff
    .org 0x74c4e-ORIGIN
P_00074c4e:
    .byte 0x06
    .org 0x74c4f-ORIGIN
P_00074c4f:
    .byte 0x5c
    .org 0x74d24-ORIGIN
P_00074d24:
    .byte 0xff
    .org 0x74d25-ORIGIN
P_00074d25:
    .byte 0xff
    .org 0x74d26-ORIGIN
P_00074d26:
    .byte 0x23
    .org 0x74d27-ORIGIN
P_00074d27:
    .byte 0xbc
    .org 0x74d28-ORIGIN
P_00074d28:
    .byte 0xff
    .org 0x74d29-ORIGIN
P_00074d29:
    .byte 0xff
    .org 0x74d2a-ORIGIN
P_00074d2a:
    .byte 0x12
    .org 0x74d2b-ORIGIN
P_00074d2b:
    .byte 0x8c
    .org 0x74d2c-ORIGIN
P_00074d2c:
    .byte 0x00
    .org 0x74d2d-ORIGIN
P_00074d2d:
    .byte 0x00
    .org 0x74d2e-ORIGIN
P_00074d2e:
    .byte 0x94
    .org 0x74d2f-ORIGIN
P_00074d2f:
    .byte 0x4e
    .org 0x74d30-ORIGIN
P_00074d30:
    .byte 0x00
    .org 0x74d31-ORIGIN
P_00074d31:
    .byte 0x02
    .org 0x74d32-ORIGIN
P_00074d32:
    .byte 0x24
    .org 0x74d33-ORIGIN
P_00074d33:
    .byte 0xfa
    .org 0x74d34-ORIGIN
P_00074d34:
    .byte 0x00
    .org 0x74d35-ORIGIN
P_00074d35:
    .byte 0x02
    .org 0x74d36-ORIGIN
P_00074d36:
    .byte 0x1b
    .org 0x74d37-ORIGIN
P_00074d37:
    .byte 0xbc
