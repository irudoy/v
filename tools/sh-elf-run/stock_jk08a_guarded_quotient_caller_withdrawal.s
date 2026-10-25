! Exact full guarded quotient callers, literal holes, saved raw RAM carriers and complete real signed division.
    .text
    .balign 4
    .set ORIGIN,0x9090
    .org 0x9092-ORIGIN
P_00009092:
    .byte 0x01
    .org 0x9093-ORIGIN
P_00009093:
    .byte 0x48
    .org 0x914e-ORIGIN
P_0000914e:
    .byte 0x00
    .org 0x914f-ORIGIN
P_0000914f:
    .byte 0x1b
    .org 0x9150-ORIGIN
P_00009150:
    .byte 0x00
    .org 0x9151-ORIGIN
P_00009151:
    .byte 0x37
    .org 0x944e-ORIGIN
P_0000944e:
    .byte 0x35
    .org 0x944f-ORIGIN
P_0000944f:
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
    .org 0x532ae-ORIGIN
L_000532ae:
    mov.l r11,@-r15
    .org 0x532b0-ORIGIN
L_000532b0:
    mov.l r12,@-r15
    .org 0x532b2-ORIGIN
L_000532b2:
    mov.l r13,@-r15
    .org 0x532b4-ORIGIN
L_000532b4:
    mov.l r14,@-r15
    .org 0x532b6-ORIGIN
L_000532b6:
    sts.l pr,@-r15
    .org 0x532b8-ORIGIN
L_000532b8:
    sts.l macl,@-r15
    .org 0x532ba-ORIGIN
L_000532ba:
    stc.l gbr,@-r15
    .org 0x532bc-ORIGIN
L_000532bc:
    mov.l P_000533e0,r0
    .org 0x532be-ORIGIN
L_000532be:
    ldc r0,gbr
    .org 0x532c0-ORIGIN
L_000532c0:
    add #-0xc,r15
    .org 0x532c2-ORIGIN
L_000532c2:
    mov.l P_000533e4,r2
    .org 0x532c4-ORIGIN
L_000532c4:
    mov #0x16,r0
    .org 0x532c6-ORIGIN
L_000532c6:
    mov.l P_000533e8,r12
    .org 0x532c8-ORIGIN
L_000532c8:
    mov.b @(r0,r2),r5
    .org 0x532ca-ORIGIN
L_000532ca:
    mov #0x15,r0
    .org 0x532cc-ORIGIN
L_000532cc:
    mov.b @(r0,r12),r13
    .org 0x532ce-ORIGIN
L_000532ce:
    mov r13,r0
    .org 0x532d0-ORIGIN
L_000532d0:
    and #0x10,r0
    .org 0x532d2-ORIGIN
L_000532d2:
    mov r0,r2
    .org 0x532d4-ORIGIN
L_000532d4:
    mov r5,r0
    .org 0x532d6-ORIGIN
L_000532d6:
    tst #0x1,r0
    .org 0x532d8-ORIGIN
L_000532d8:
    bt L_000532de
    .org 0x532da-ORIGIN
L_000532da:
    bra L_000533fc
    .org 0x532dc-ORIGIN
L_000532dc:
    nop
    .org 0x532de-ORIGIN
L_000532de:
    tst r2,r2
    .org 0x532e0-ORIGIN
L_000532e0:
    bt L_000532e6
    .org 0x532e2-ORIGIN
L_000532e2:
    bra L_000533fc
    .org 0x532e4-ORIGIN
L_000532e4:
    nop
    .org 0x532e6-ORIGIN
L_000532e6:
    mov.l P_000533e0,r11
    .org 0x532e8-ORIGIN
L_000532e8:
    mov.w P_000533ba,r0
    .org 0x532ea-ORIGIN
L_000532ea:
    mov.b @(r0,r11),r4
    .org 0x532ec-ORIGIN
L_000532ec:
    mov r4,r0
    .org 0x532ee-ORIGIN
L_000532ee:
    tst #0x1,r0
    .org 0x532f0-ORIGIN
L_000532f0:
    bt L_00053304
    .org 0x532f2-ORIGIN
L_000532f2:
    mov.l P_000533ec,r7
    .org 0x532f4-ORIGIN
L_000532f4:
    mov.w @(0xc,r7),r0
    .org 0x532f6-ORIGIN
L_000532f6:
    mov #0x40,r7
    .org 0x532f8-ORIGIN
L_000532f8:
    shll8 r7
    .org 0x532fa-ORIGIN
L_000532fa:
    extu.w r0,r6
    .org 0x532fc-ORIGIN
L_000532fc:
    cmp/gt r7,r6
    .org 0x532fe-ORIGIN
L_000532fe:
    bf L_00053304
    .org 0x53300-ORIGIN
L_00053300:
    bra L_000533fc
    .org 0x53302-ORIGIN
L_00053302:
    nop
    .org 0x53304-ORIGIN
L_00053304:
    mov r5,r0
    .org 0x53306-ORIGIN
L_00053306:
    tst #0x2,r0
    .org 0x53308-ORIGIN
L_00053308:
    bf L_000533fc
    .org 0x5330a-ORIGIN
L_0005330a:
    mov r4,r0
    .org 0x5330c-ORIGIN
L_0005330c:
    tst #0x2,r0
    .org 0x5330e-ORIGIN
L_0005330e:
    bt L_0005331e
    .org 0x53310-ORIGIN
L_00053310:
    mov.l P_000533ec,r7
    .org 0x53312-ORIGIN
L_00053312:
    mov #0x40,r5
    .org 0x53314-ORIGIN
L_00053314:
    shll8 r5
    .org 0x53316-ORIGIN
L_00053316:
    mov.w @(0xc,r7),r0
    .org 0x53318-ORIGIN
L_00053318:
    extu.w r0,r6
    .org 0x5331a-ORIGIN
L_0005331a:
    cmp/gt r5,r6
    .org 0x5331c-ORIGIN
L_0005331c:
    bt L_000533fc
    .org 0x5331e-ORIGIN
L_0005331e:
    mov r4,r0
    .org 0x53320-ORIGIN
L_00053320:
    tst #0x1,r0
    .org 0x53322-ORIGIN
L_00053322:
    bt L_00053342
    .org 0x53324-ORIGIN
L_00053324:
    mov r4,r0
    .org 0x53326-ORIGIN
L_00053326:
    tst #0x2,r0
    .org 0x53328-ORIGIN
L_00053328:
    bt L_00053342
    .org 0x5332a-ORIGIN
L_0005332a:
    mov.l P_000533f0,r5
    .org 0x5332c-ORIGIN
L_0005332c:
    mov.w @(0x19a,gbr),r0
    .org 0x5332e-ORIGIN
L_0005332e:
    mov.w @r5,r2
    .org 0x53330-ORIGIN
L_00053330:
    extu.w r0,r6
    .org 0x53332-ORIGIN
L_00053332:
    extu.w r2,r2
    .org 0x53334-ORIGIN
L_00053334:
    sub r2,r6
    .org 0x53336-ORIGIN
L_00053336:
    cmp/pz r6
    .org 0x53338-ORIGIN
L_00053338:
    bt/s L_0005333e
    .org 0x5333a-ORIGIN
L_0005333a:
    mov r6,r2
    .org 0x5333c-ORIGIN
L_0005333c:
    mov #0x0,r2
    .org 0x5333e-ORIGIN
L_0005333e:
    mov r2,r0
    .org 0x53340-ORIGIN
L_00053340:
    mov.w r0,@(0x19a,gbr)
    .org 0x53342-ORIGIN
L_00053342:
    mov.w P_000533bc,r0
    .org 0x53344-ORIGIN
L_00053344:
    mov.l P_000533f4,r1
    .org 0x53346-ORIGIN
L_00053346:
    mov.w @(r0,r11),r6
    .org 0x53348-ORIGIN
L_00053348:
    mov.w @(0x19a,gbr),r0
    .org 0x5334a-ORIGIN
L_0005334a:
    extu.w r6,r2
    .org 0x5334c-ORIGIN
L_0005334c:
    extu.w r0,r4
    .org 0x5334e-ORIGIN
L_0005334e:
    mov.w P_000533be,r0
    .org 0x53350-ORIGIN
L_00053350:
    mov r4,r5
    .org 0x53352-ORIGIN
L_00053352:
    mov.w @(r0,r11),r6
    .org 0x53354-ORIGIN
L_00053354:
    mov r4,r0
    .org 0x53356-ORIGIN
L_00053356:
    add r2,r6
    .org 0x53358-ORIGIN
L_00053358:
    mov.l P_000533f8,r2
    .org 0x5335a-ORIGIN
L_0005335a:
    jsr @r2
    .org 0x5335c-ORIGIN
L_0005335c:
    mov.l r6,@r15
    .org 0x5335e-ORIGIN
L_0005335e:
    mov.l @r15,r6
    .org 0x53360-ORIGIN
L_00053360:
    cmp/gt r0,r6
    .org 0x53362-ORIGIN
L_00053362:
    bf L_00053390
    .org 0x53364-ORIGIN
L_00053364:
    mov.w @(0x19a,gbr),r0
    .org 0x53366-ORIGIN
L_00053366:
    extu.w r0,r4
    .org 0x53368-ORIGIN
L_00053368:
    tst r4,r4
    .org 0x5336a-ORIGIN
L_0005336a:
    bt L_00053390
    .org 0x5336c-ORIGIN
L_0005336c:
    mov.w P_000533bc,r0
    .org 0x5336e-ORIGIN
L_0005336e:
    mov.w @(r0,r11),r6
    .org 0x53370-ORIGIN
L_00053370:
    mov.w P_000533be,r0
    .org 0x53372-ORIGIN
L_00053372:
    extu.w r6,r2
    .org 0x53374-ORIGIN
L_00053374:
    mov.w @(r0,r11),r6
    .org 0x53376-ORIGIN
L_00053376:
    add r2,r6
    .org 0x53378-ORIGIN
L_00053378:
    cmp/pz r6
    .org 0x5337a-ORIGIN
L_0005337a:
    bt L_00053380
    .org 0x5337c-ORIGIN
L_0005337c:
    mov.w P_000533c0,r2
    .org 0x5337e-ORIGIN
L_0005337e:
    add r2,r6
    .org 0x53380-ORIGIN
L_00053380:
    shll r6
    .org 0x53382-ORIGIN
L_00053382:
    subc r2,r2
    .org 0x53384-ORIGIN
L_00053384:
    shll r6
    .org 0x53386-ORIGIN
L_00053386:
    rotcl r2
    .org 0x53388-ORIGIN
L_00053388:
    xtrct r2,r6
    .org 0x5338a-ORIGIN
L_0005338a:
    mul.l r6,r4
    .org 0x5338c-ORIGIN
L_0005338c:
    bra L_0005349a
    .org 0x5338e-ORIGIN
L_0005338e:
    sts macl,r2
    .org 0x53390-ORIGIN
L_00053390:
    mov.w @(0x19a,gbr),r0
    .org 0x53392-ORIGIN
L_00053392:
    extu.w r0,r4
    .org 0x53394-ORIGIN
L_00053394:
    mov.w P_000533bc,r0
    .org 0x53396-ORIGIN
L_00053396:
    mov.w @(r0,r11),r6
    .org 0x53398-ORIGIN
L_00053398:
    mov.w P_000533be,r0
    .org 0x5339a-ORIGIN
L_0005339a:
    extu.w r6,r6
    .org 0x5339c-ORIGIN
L_0005339c:
    mov.w @(r0,r11),r2
    .org 0x5339e-ORIGIN
L_0005339e:
    add r6,r2
    .org 0x533a0-ORIGIN
L_000533a0:
    mul.l r4,r2
    .org 0x533a2-ORIGIN
L_000533a2:
    sts macl,r6
    .org 0x533a4-ORIGIN
L_000533a4:
    cmp/pz r6
    .org 0x533a6-ORIGIN
L_000533a6:
    bt L_000533ac
    .org 0x533a8-ORIGIN
L_000533a8:
    mov.w P_000533c0,r2
    .org 0x533aa-ORIGIN
L_000533aa:
    add r2,r6
    .org 0x533ac-ORIGIN
L_000533ac:
    shll r6
    .org 0x533ae-ORIGIN
L_000533ae:
    subc r2,r2
    .org 0x533b0-ORIGIN
L_000533b0:
    shll r6
    .org 0x533b2-ORIGIN
L_000533b2:
    rotcl r2
    .org 0x533b4-ORIGIN
L_000533b4:
    xtrct r2,r6
    .org 0x533b6-ORIGIN
L_000533b6:
    bra L_0005349a
    .org 0x533b8-ORIGIN
L_000533b8:
    mov r6,r2
    .org 0x533ba-ORIGIN
P_000533ba:
    .byte 0x03
    .org 0x533bb-ORIGIN
P_000533bb:
    .byte 0x8e
    .org 0x533bc-ORIGIN
P_000533bc:
    .byte 0x03
    .org 0x533bd-ORIGIN
P_000533bd:
    .byte 0x42
    .org 0x533be-ORIGIN
P_000533be:
    .byte 0x03
    .org 0x533bf-ORIGIN
P_000533bf:
    .byte 0x72
    .org 0x533c0-ORIGIN
P_000533c0:
    .byte 0x3f
    .org 0x533c1-ORIGIN
P_000533c1:
    .byte 0xff
    .org 0x533e0-ORIGIN
P_000533e0:
    .byte 0xff
    .org 0x533e1-ORIGIN
P_000533e1:
    .byte 0xff
    .org 0x533e2-ORIGIN
P_000533e2:
    .byte 0x12
    .org 0x533e3-ORIGIN
P_000533e3:
    .byte 0x8c
    .org 0x533e4-ORIGIN
P_000533e4:
    .byte 0xff
    .org 0x533e5-ORIGIN
P_000533e5:
    .byte 0xff
    .org 0x533e6-ORIGIN
P_000533e6:
    .byte 0x22
    .org 0x533e7-ORIGIN
P_000533e7:
    .byte 0xf8
    .org 0x533e8-ORIGIN
P_000533e8:
    .byte 0xff
    .org 0x533e9-ORIGIN
P_000533e9:
    .byte 0xff
    .org 0x533ea-ORIGIN
P_000533ea:
    .byte 0x24
    .org 0x533eb-ORIGIN
P_000533eb:
    .byte 0x70
    .org 0x533ec-ORIGIN
P_000533ec:
    .byte 0xff
    .org 0x533ed-ORIGIN
P_000533ed:
    .byte 0xff
    .org 0x533ee-ORIGIN
P_000533ee:
    .byte 0x22
    .org 0x533ef-ORIGIN
P_000533ef:
    .byte 0xdc
    .org 0x533f0-ORIGIN
P_000533f0:
    .byte 0x00
    .org 0x533f1-ORIGIN
P_000533f1:
    .byte 0x00
    .org 0x533f2-ORIGIN
P_000533f2:
    .byte 0x90
    .org 0x533f3-ORIGIN
P_000533f3:
    .byte 0x92
    .org 0x533f4-ORIGIN
P_000533f4:
    .byte 0x7f
    .org 0x533f5-ORIGIN
P_000533f5:
    .byte 0xff
    .org 0x533f6-ORIGIN
P_000533f6:
    .byte 0xff
    .org 0x533f7-ORIGIN
P_000533f7:
    .byte 0xff
    .org 0x533f8-ORIGIN
P_000533f8:
    .byte 0x00
    .org 0x533f9-ORIGIN
P_000533f9:
    .byte 0x02
    .org 0x533fa-ORIGIN
P_000533fa:
    .byte 0x1b
    .org 0x533fb-ORIGIN
P_000533fb:
    .byte 0xbc
    .org 0x533fc-ORIGIN
L_000533fc:
    tst r2,r2
    .org 0x533fe-ORIGIN
L_000533fe:
    bf L_00053498
    .org 0x53400-ORIGIN
L_00053400:
    mov.l P_000534bc,r11
    .org 0x53402-ORIGIN
L_00053402:
    mov.w P_000534ae,r0
    .org 0x53404-ORIGIN
L_00053404:
    mov.b @(r0,r11),r5
    .org 0x53406-ORIGIN
L_00053406:
    mov.w P_000534b0,r0
    .org 0x53408-ORIGIN
L_00053408:
    extu.b r5,r5
    .org 0x5340a-ORIGIN
L_0005340a:
    mov.b @(r0,r11),r4
    .org 0x5340c-ORIGIN
L_0005340c:
    mov r5,r6
    .org 0x5340e-ORIGIN
L_0005340e:
    mov.w P_000534b2,r0
    .org 0x53410-ORIGIN
L_00053410:
    extu.b r4,r4
    .org 0x53412-ORIGIN
L_00053412:
    mov.b @(r0,r11),r2
    .org 0x53414-ORIGIN
L_00053414:
    mov.w P_000534b4,r0
    .org 0x53416-ORIGIN
L_00053416:
    shll r2
    .org 0x53418-ORIGIN
L_00053418:
    sub r2,r6
    .org 0x5341a-ORIGIN
L_0005341a:
    mul.l r6,r4
    .org 0x5341c-ORIGIN
L_0005341c:
    mov.b @(r0,r11),r4
    .org 0x5341e-ORIGIN
L_0005341e:
    mov.w P_000534b6,r0
    .org 0x53420-ORIGIN
L_00053420:
    extu.b r4,r4
    .org 0x53422-ORIGIN
L_00053422:
    mov.l P_000534c0,r6
    .org 0x53424-ORIGIN
L_00053424:
    mov.b @(r0,r11),r2
    .org 0x53426-ORIGIN
L_00053426:
    sts macl,r14
    .org 0x53428-ORIGIN
L_00053428:
    extu.b r2,r2
    .org 0x5342a-ORIGIN
L_0005342a:
    mov.w P_000534b8,r0
    .org 0x5342c-ORIGIN
L_0005342c:
    mul.l r4,r2
    .org 0x5342e-ORIGIN
L_0005342e:
    mov.w @(r0,r6),r7
    .org 0x53430-ORIGIN
L_00053430:
    mov r5,r6
    .org 0x53432-ORIGIN
L_00053432:
    shll8 r6
    .org 0x53434-ORIGIN
L_00053434:
    sts macl,r2
    .org 0x53436-ORIGIN
L_00053436:
    extu.w r7,r7
    .org 0x53438-ORIGIN
L_00053438:
    sub r14,r6
    .org 0x5343a-ORIGIN
L_0005343a:
    add r7,r2
    .org 0x5343c-ORIGIN
L_0005343c:
    shll r2
    .org 0x5343e-ORIGIN
L_0005343e:
    add r2,r6
    .org 0x53440-ORIGIN
L_00053440:
    cmp/pl r6
    .org 0x53442-ORIGIN
L_00053442:
    mov r6,r2
    .org 0x53444-ORIGIN
L_00053444:
    bt/s L_0005344c
    .org 0x53446-ORIGIN
L_00053446:
    mov.l r6,@(0x4,r15)
    .org 0x53448-ORIGIN
L_00053448:
    bra L_0005348c
    .org 0x5344a-ORIGIN
L_0005344a:
    mov #0x0,r2
    .org 0x5344c-ORIGIN
L_0005344c:
    mov.w @(0x19a,gbr),r0
    .org 0x5344e-ORIGIN
L_0005344e:
    mov.l P_000534c4,r6
    .org 0x53450-ORIGIN
L_00053450:
    extu.w r0,r5
    .org 0x53452-ORIGIN
L_00053452:
    mov r2,r0
    .org 0x53454-ORIGIN
L_00053454:
    mov.l r5,@(0x8,r15)
    .org 0x53456-ORIGIN
L_00053456:
    mov.l P_000534c8,r5
    .org 0x53458-ORIGIN
L_00053458:
    jsr @r6
    .org 0x5345a-ORIGIN
L_0005345a:
    mov r5,r1
    .org 0x5345c-ORIGIN
L_0005345c:
    mov.l @(0x8,r15),r2
    .org 0x5345e-ORIGIN
L_0005345e:
    cmp/gt r0,r2
    .org 0x53460-ORIGIN
L_00053460:
    bf L_00053466
    .org 0x53462-ORIGIN
L_00053462:
    bra L_0005348c
    .org 0x53464-ORIGIN
L_00053464:
    mov #-0x1,r2
    .org 0x53466-ORIGIN
L_00053466:
    mov.w @(0x19a,gbr),r0
    .org 0x53468-ORIGIN
L_00053468:
    mov.l @(0x4,r15),r2
    .org 0x5346a-ORIGIN
L_0005346a:
    extu.w r0,r5
    .org 0x5346c-ORIGIN
L_0005346c:
    mul.l r5,r2
    .org 0x5346e-ORIGIN
L_0005346e:
    sts macl,r6
    .org 0x53470-ORIGIN
L_00053470:
    cmp/pz r6
    .org 0x53472-ORIGIN
L_00053472:
    bt L_00053478
    .org 0x53474-ORIGIN
L_00053474:
    mov.l P_000534cc,r2
    .org 0x53476-ORIGIN
L_00053476:
    add r2,r6
    .org 0x53478-ORIGIN
L_00053478:
    swap.w r6,r2
    .org 0x5347a-ORIGIN
L_0005347a:
    exts.w r2,r2
    .org 0x5347c-ORIGIN
L_0005347c:
    shll2 r2
    .org 0x5347e-ORIGIN
L_0005347e:
    shlr8 r2
    .org 0x53480-ORIGIN
L_00053480:
    mov #-0x1,r5
    .org 0x53482-ORIGIN
L_00053482:
    exts.w r2,r6
    .org 0x53484-ORIGIN
L_00053484:
    extu.b r5,r2
    .org 0x53486-ORIGIN
L_00053486:
    cmp/gt r2,r6
    .org 0x53488-ORIGIN
L_00053488:
    bt L_0005348c
    .org 0x5348a-ORIGIN
L_0005348a:
    mov r6,r2
    .org 0x5348c-ORIGIN
L_0005348c:
    mov.w P_000534ba,r0
    .org 0x5348e-ORIGIN
L_0005348e:
    mov.b r2,@(r0,r11)
    .org 0x53490-ORIGIN
L_00053490:
    mov #0x10,r0
    .org 0x53492-ORIGIN
L_00053492:
    or r0,r13
    .org 0x53494-ORIGIN
L_00053494:
    mov #0x15,r0
    .org 0x53496-ORIGIN
L_00053496:
    mov.b r13,@(r0,r12)
    .org 0x53498-ORIGIN
L_00053498:
    mov #0x0,r2
    .org 0x5349a-ORIGIN
L_0005349a:
    mov r2,r0
    .org 0x5349c-ORIGIN
L_0005349c:
    add #0xc,r15
    .org 0x5349e-ORIGIN
L_0005349e:
    ldc.l @r15+,gbr
    .org 0x534a0-ORIGIN
L_000534a0:
    lds.l @r15+,macl
    .org 0x534a2-ORIGIN
L_000534a2:
    lds.l @r15+,pr
    .org 0x534a4-ORIGIN
L_000534a4:
    mov.l @r15+,r14
    .org 0x534a6-ORIGIN
L_000534a6:
    mov.l @r15+,r13
    .org 0x534a8-ORIGIN
L_000534a8:
    mov.l @r15+,r12
    .org 0x534aa-ORIGIN
L_000534aa:
    rts
    .org 0x534ac-ORIGIN
L_000534ac:
    mov.l @r15+,r11
    .org 0x534ae-ORIGIN
P_000534ae:
    .byte 0x03
    .org 0x534af-ORIGIN
P_000534af:
    .byte 0x75
    .org 0x534b0-ORIGIN
P_000534b0:
    .byte 0x03
    .org 0x534b1-ORIGIN
P_000534b1:
    .byte 0x53
    .org 0x534b2-ORIGIN
P_000534b2:
    .byte 0x03
    .org 0x534b3-ORIGIN
P_000534b3:
    .byte 0xd4
    .org 0x534b4-ORIGIN
P_000534b4:
    .byte 0x03
    .org 0x534b5-ORIGIN
P_000534b5:
    .byte 0xf4
    .org 0x534b6-ORIGIN
P_000534b6:
    .byte 0x06
    .org 0x534b7-ORIGIN
P_000534b7:
    .byte 0xb1
    .org 0x534b8-ORIGIN
P_000534b8:
    .byte 0x06
    .org 0x534b9-ORIGIN
P_000534b9:
    .byte 0xf8
    .org 0x534ba-ORIGIN
P_000534ba:
    .byte 0x03
    .org 0x534bb-ORIGIN
P_000534bb:
    .byte 0x74
    .org 0x534bc-ORIGIN
P_000534bc:
    .byte 0xff
    .org 0x534bd-ORIGIN
P_000534bd:
    .byte 0xff
    .org 0x534be-ORIGIN
P_000534be:
    .byte 0x12
    .org 0x534bf-ORIGIN
P_000534bf:
    .byte 0x8c
    .org 0x534c0-ORIGIN
P_000534c0:
    .byte 0xff
    .org 0x534c1-ORIGIN
P_000534c1:
    .byte 0xff
    .org 0x534c2-ORIGIN
P_000534c2:
    .byte 0x28
    .org 0x534c3-ORIGIN
P_000534c3:
    .byte 0xf8
    .org 0x534c4-ORIGIN
P_000534c4:
    .byte 0x00
    .org 0x534c5-ORIGIN
P_000534c5:
    .byte 0x02
    .org 0x534c6-ORIGIN
P_000534c6:
    .byte 0x1b
    .org 0x534c7-ORIGIN
P_000534c7:
    .byte 0xbc
    .org 0x534c8-ORIGIN
P_000534c8:
    .byte 0x3f
    .org 0x534c9-ORIGIN
P_000534c9:
    .byte 0xc0
    .org 0x534ca-ORIGIN
P_000534ca:
    .byte 0x00
    .org 0x534cb-ORIGIN
P_000534cb:
    .byte 0x00
    .org 0x534cc-ORIGIN
P_000534cc:
    .byte 0x00
    .org 0x534cd-ORIGIN
P_000534cd:
    .byte 0x3f
    .org 0x534ce-ORIGIN
P_000534ce:
    .byte 0xff
    .org 0x534cf-ORIGIN
P_000534cf:
    .byte 0xff
    .org 0x74b68-ORIGIN
L_00074b68:
    sts.l pr,@-r15
    .org 0x74b6a-ORIGIN
L_00074b6a:
    stc.l gbr,@-r15
    .org 0x74b6c-ORIGIN
L_00074b6c:
    mov.l P_00074d24,r0
    .org 0x74b6e-ORIGIN
L_00074b6e:
    ldc r0,gbr
    .org 0x74b70-ORIGIN
L_00074b70:
    add #-0x4,r15
    .org 0x74b72-ORIGIN
L_00074b72:
    mov.l P_00074d38,r6
    .org 0x74b74-ORIGIN
L_00074b74:
    mov.b @r6,r0
    .org 0x74b76-ORIGIN
L_00074b76:
    tst #0x8,r0
    .org 0x74b78-ORIGIN
L_00074b78:
    bf L_00074bfa
    .org 0x74b7a-ORIGIN
L_00074b7a:
    mov.b @(0xdf,gbr),r0
    .org 0x74b7c-ORIGIN
L_00074b7c:
    tst #0x1,r0
    .org 0x74b7e-ORIGIN
L_00074b7e:
    bf L_00074bfa
    .org 0x74b80-ORIGIN
L_00074b80:
    mov.b @(0xa3,gbr),r0
    .org 0x74b82-ORIGIN
L_00074b82:
    tst #0x80,r0
    .org 0x74b84-ORIGIN
L_00074b84:
    bf L_00074bfa
    .org 0x74b86-ORIGIN
L_00074b86:
    mov.l P_00074d3c,r6
    .org 0x74b88-ORIGIN
L_00074b88:
    mov.l P_00074d28,r5
    .org 0x74b8a-ORIGIN
L_00074b8a:
    mov.b @(0x4,r6),r0
    .org 0x74b8c-ORIGIN
L_00074b8c:
    tst #0x40,r0
    .org 0x74b8e-ORIGIN
L_00074b8e:
    mov.w @(0x66,gbr),r0
    .org 0x74b90-ORIGIN
L_00074b90:
    extu.w r0,r6
    .org 0x74b92-ORIGIN
L_00074b92:
    mov.w P_00074c50,r0
    .org 0x74b94-ORIGIN
L_00074b94:
    mov.w @(r0,r5),r2
    .org 0x74b96-ORIGIN
L_00074b96:
    bt/s L_00074bec
    .org 0x74b98-ORIGIN
L_00074b98:
    extu.w r2,r2
    .org 0x74b9a-ORIGIN
L_00074b9a:
    add r2,r6
    .org 0x74b9c-ORIGIN
L_00074b9c:
    mov.l P_00074d40,r2
    .org 0x74b9e-ORIGIN
L_00074b9e:
    mov.l r6,@r15
    .org 0x74ba0-ORIGIN
L_00074ba0:
    mov.w @(0x2,r2),r0
    .org 0x74ba2-ORIGIN
L_00074ba2:
    mov.l P_00074d44,r2
    .org 0x74ba4-ORIGIN
L_00074ba4:
    extu.w r0,r5
    .org 0x74ba6-ORIGIN
L_00074ba6:
    mov.w @r2,r7
    .org 0x74ba8-ORIGIN
L_00074ba8:
    extu.w r7,r7
    .org 0x74baa-ORIGIN
L_00074baa:
    cmp/gt r7,r5
    .org 0x74bac-ORIGIN
L_00074bac:
    bt L_00074bb2
    .org 0x74bae-ORIGIN
L_00074bae:
    bra L_00074bd4
    .org 0x74bb0-ORIGIN
L_00074bb0:
    mov #0x0,r2
    .org 0x74bb2-ORIGIN
L_00074bb2:
    mov.l P_00074d44,r3
    .org 0x74bb4-ORIGIN
L_00074bb4:
    mov.w @(0x2,r3),r0
    .org 0x74bb6-ORIGIN
L_00074bb6:
    extu.w r0,r4
    .org 0x74bb8-ORIGIN
L_00074bb8:
    cmp/ge r4,r5
    .org 0x74bba-ORIGIN
L_00074bba:
    bf L_00074bc2
    .org 0x74bbc-ORIGIN
L_00074bbc:
    mov #-0x1,r6
    .org 0x74bbe-ORIGIN
L_00074bbe:
    bra L_00074bd4
    .org 0x74bc0-ORIGIN
L_00074bc0:
    extu.w r6,r2
    .org 0x74bc2-ORIGIN
L_00074bc2:
    sub r7,r5
    .org 0x74bc4-ORIGIN
L_00074bc4:
    mov.l P_00074d34,r6
    .org 0x74bc6-ORIGIN
L_00074bc6:
    mov r5,r1
    .org 0x74bc8-ORIGIN
L_00074bc8:
    shll16 r1
    .org 0x74bca-ORIGIN
L_00074bca:
    sub r5,r1
    .org 0x74bcc-ORIGIN
L_00074bcc:
    sub r7,r4
    .org 0x74bce-ORIGIN
L_00074bce:
    jsr @r6
    .org 0x74bd0-ORIGIN
L_00074bd0:
    mov r4,r0
    .org 0x74bd2-ORIGIN
L_00074bd2:
    mov r0,r2
    .org 0x74bd4-ORIGIN
L_00074bd4:
    mov.l @r15,r6
    .org 0x74bd6-ORIGIN
L_00074bd6:
    cmp/hs r2,r6
    .org 0x74bd8-ORIGIN
L_00074bd8:
    bt L_00074bde
    .org 0x74bda-ORIGIN
L_00074bda:
    bra L_00074be0
    .org 0x74bdc-ORIGIN
L_00074bdc:
    mov r2,r6
    .org 0x74bde-ORIGIN
L_00074bde:
    mov.l @r15,r6
    .org 0x74be0-ORIGIN
L_00074be0:
    mov #-0x1,r2
    .org 0x74be2-ORIGIN
L_00074be2:
    extu.w r2,r2
    .org 0x74be4-ORIGIN
L_00074be4:
    cmp/gt r2,r6
    .org 0x74be6-ORIGIN
L_00074be6:
    bt L_00074bf6
    .org 0x74be8-ORIGIN
L_00074be8:
    bra L_00074bf6
    .org 0x74bea-ORIGIN
L_00074bea:
    mov r6,r2
    .org 0x74bec-ORIGIN
L_00074bec:
    sub r2,r6
    .org 0x74bee-ORIGIN
L_00074bee:
    cmp/pz r6
    .org 0x74bf0-ORIGIN
L_00074bf0:
    bt/s L_00074bf6
    .org 0x74bf2-ORIGIN
L_00074bf2:
    mov r6,r2
    .org 0x74bf4-ORIGIN
L_00074bf4:
    mov #0x0,r2
    .org 0x74bf6-ORIGIN
L_00074bf6:
    bra L_00074bfc
    .org 0x74bf8-ORIGIN
L_00074bf8:
    mov r2,r0
    .org 0x74bfa-ORIGIN
L_00074bfa:
    mov #0x0,r0
    .org 0x74bfc-ORIGIN
L_00074bfc:
    mov.w r0,@(0x66,gbr)
    .org 0x74bfe-ORIGIN
L_00074bfe:
    add #0x4,r15
    .org 0x74c00-ORIGIN
L_00074c00:
    ldc.l @r15+,gbr
    .org 0x74c02-ORIGIN
L_00074c02:
    lds.l @r15+,pr
    .org 0x74c04-ORIGIN
L_00074c04:
    rts
    .org 0x74c06-ORIGIN
L_00074c06:
    nop
    .org 0x74c50-ORIGIN
P_00074c50:
    .byte 0x05
    .org 0x74c51-ORIGIN
P_00074c51:
    .byte 0x6c
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
    .org 0x74d38-ORIGIN
P_00074d38:
    .byte 0xff
    .org 0x74d39-ORIGIN
P_00074d39:
    .byte 0xff
    .org 0x74d3a-ORIGIN
P_00074d3a:
    .byte 0x41
    .org 0x74d3b-ORIGIN
P_00074d3b:
    .byte 0x7e
    .org 0x74d3c-ORIGIN
P_00074d3c:
    .byte 0xff
    .org 0x74d3d-ORIGIN
P_00074d3d:
    .byte 0xff
    .org 0x74d3e-ORIGIN
P_00074d3e:
    .byte 0x24
    .org 0x74d3f-ORIGIN
P_00074d3f:
    .byte 0xce
    .org 0x74d40-ORIGIN
P_00074d40:
    .byte 0xff
    .org 0x74d41-ORIGIN
P_00074d41:
    .byte 0xff
    .org 0x74d42-ORIGIN
P_00074d42:
    .byte 0x12
    .org 0x74d43-ORIGIN
P_00074d43:
    .byte 0x0e
    .org 0x74d44-ORIGIN
P_00074d44:
    .byte 0x00
    .org 0x74d45-ORIGIN
P_00074d45:
    .byte 0x00
    .org 0x74d46-ORIGIN
P_00074d46:
    .byte 0x91
    .org 0x74d47-ORIGIN
P_00074d47:
    .byte 0x4e
    .org 0x75306-ORIGIN
L_00075306:
    sts.l pr,@-r15
    .org 0x75308-ORIGIN
L_00075308:
    sts.l macl,@-r15
    .org 0x7530a-ORIGIN
L_0007530a:
    mov.l P_00075444,r7
    .org 0x7530c-ORIGIN
L_0007530c:
    mov.w P_0007534a,r0
    .org 0x7530e-ORIGIN
L_0007530e:
    mov.w @(r0,r7),r6
    .org 0x75310-ORIGIN
L_00075310:
    extu.w r6,r6
    .org 0x75312-ORIGIN
L_00075312:
    tst r6,r6
    .org 0x75314-ORIGIN
L_00075314:
    bt L_0007538a
    .org 0x75316-ORIGIN
L_00075316:
    mov.l P_00075440,r2
    .org 0x75318-ORIGIN
L_00075318:
    mov #0x40,r0
    .org 0x7531a-ORIGIN
L_0007531a:
    mov.w @(r0,r2),r5
    .org 0x7531c-ORIGIN
L_0007531c:
    tst r5,r5
    .org 0x7531e-ORIGIN
L_0007531e:
    bt L_0007538a
    .org 0x75320-ORIGIN
L_00075320:
    mov.l P_00075448,r5
    .org 0x75322-ORIGIN
L_00075322:
    mov.w P_0007534c,r0
    .org 0x75324-ORIGIN
L_00075324:
    mov.w @r5,r2
    .org 0x75326-ORIGIN
L_00075326:
    mov.w @(r0,r7),r5
    .org 0x75328-ORIGIN
L_00075328:
    mov r6,r0
    .org 0x7532a-ORIGIN
L_0007532a:
    extu.w r2,r2
    .org 0x7532c-ORIGIN
L_0007532c:
    mov.l P_0007544c,r4
    .org 0x7532e-ORIGIN
L_0007532e:
    mul.l r5,r2
    .org 0x75330-ORIGIN
L_00075330:
    jsr @r4
    .org 0x75332-ORIGIN
L_00075332:
    sts macl,r1
    .org 0x75334-ORIGIN
L_00075334:
    cmp/pz r0
    .org 0x75336-ORIGIN
L_00075336:
    bf/s L_0007534e
    .org 0x75338-ORIGIN
L_00075338:
    mov r0,r6
    .org 0x7533a-ORIGIN
L_0007533a:
    mov.l P_00075450,r2
    .org 0x7533c-ORIGIN
L_0007533c:
    cmp/gt r2,r6
    .org 0x7533e-ORIGIN
L_0007533e:
    bf L_0007535c
    .org 0x75340-ORIGIN
L_00075340:
    bra L_0007535c
    .org 0x75342-ORIGIN
L_00075342:
    mov r2,r6
    .org 0x7534a-ORIGIN
P_0007534a:
    .byte 0x07
    .org 0x7534b-ORIGIN
P_0007534b:
    .byte 0x16
    .org 0x7534c-ORIGIN
P_0007534c:
    .byte 0x06
    .org 0x7534d-ORIGIN
P_0007534d:
    .byte 0x66
    .org 0x7534e-ORIGIN
L_0007534e:
    mov #-0x2,r2
    .org 0x75350-ORIGIN
L_00075350:
    shll8 r2
    .org 0x75352-ORIGIN
L_00075352:
    shll16 r2
    .org 0x75354-ORIGIN
L_00075354:
    cmp/ge r2,r6
    .org 0x75356-ORIGIN
L_00075356:
    bf L_0007535a
    .org 0x75358-ORIGIN
L_00075358:
    mov r6,r2
    .org 0x7535a-ORIGIN
L_0007535a:
    mov r2,r6
    .org 0x7535c-ORIGIN
L_0007535c:
    mov.l P_00075440,r3
    .org 0x7535e-ORIGIN
L_0007535e:
    mov #0x40,r0
    .org 0x75360-ORIGIN
L_00075360:
    mov r6,r1
    .org 0x75362-ORIGIN
L_00075362:
    shll2 r1
    .org 0x75364-ORIGIN
L_00075364:
    mov.w @(r0,r3),r5
    .org 0x75366-ORIGIN
L_00075366:
    shll2 r1
    .org 0x75368-ORIGIN
L_00075368:
    mov.l P_0007544c,r4
    .org 0x7536a-ORIGIN
L_0007536a:
    shll2 r1
    .org 0x7536c-ORIGIN
L_0007536c:
    jsr @r4
    .org 0x7536e-ORIGIN
L_0007536e:
    extu.w r5,r0
    .org 0x75370-ORIGIN
L_00075370:
    mov.w P_0007541e,r6
    .org 0x75372-ORIGIN
L_00075372:
    cmp/gt r6,r0
    .org 0x75374-ORIGIN
L_00075374:
    bt/s L_0007537a
    .org 0x75376-ORIGIN
L_00075376:
    mov r0,r2
    .org 0x75378-ORIGIN
L_00075378:
    mov r2,r6
    .org 0x7537a-ORIGIN
L_0007537a:
    mov #-0x80,r2
    .org 0x7537c-ORIGIN
L_0007537c:
    shll8 r2
    .org 0x7537e-ORIGIN
L_0007537e:
    cmp/ge r2,r6
    .org 0x75380-ORIGIN
L_00075380:
    bf L_00075384
    .org 0x75382-ORIGIN
L_00075382:
    mov r6,r2
    .org 0x75384-ORIGIN
L_00075384:
    mov.l P_00075444,r7
    .org 0x75386-ORIGIN
L_00075386:
    bra L_0007538c
    .org 0x75388-ORIGIN
L_00075388:
    nop
    .org 0x7538a-ORIGIN
L_0007538a:
    mov #0x0,r2
    .org 0x7538c-ORIGIN
L_0007538c:
    mov.w P_00075420,r0
    .org 0x7538e-ORIGIN
L_0007538e:
    lds.l @r15+,macl
    .org 0x75390-ORIGIN
L_00075390:
    lds.l @r15+,pr
    .org 0x75392-ORIGIN
L_00075392:
    rts
    .org 0x75394-ORIGIN
L_00075394:
    mov.w r2,@(r0,r7)
    .org 0x7541e-ORIGIN
P_0007541e:
    .byte 0x7f
    .org 0x7541f-ORIGIN
P_0007541f:
    .byte 0xff
    .org 0x75420-ORIGIN
P_00075420:
    .byte 0x07
    .org 0x75421-ORIGIN
P_00075421:
    .byte 0x48
    .org 0x75440-ORIGIN
P_00075440:
    .byte 0xff
    .org 0x75441-ORIGIN
P_00075441:
    .byte 0xff
    .org 0x75442-ORIGIN
P_00075442:
    .byte 0x23
    .org 0x75443-ORIGIN
P_00075443:
    .byte 0xbc
    .org 0x75444-ORIGIN
P_00075444:
    .byte 0xff
    .org 0x75445-ORIGIN
P_00075445:
    .byte 0xff
    .org 0x75446-ORIGIN
P_00075446:
    .byte 0x12
    .org 0x75447-ORIGIN
P_00075447:
    .byte 0x8c
    .org 0x75448-ORIGIN
P_00075448:
    .byte 0x00
    .org 0x75449-ORIGIN
P_00075449:
    .byte 0x00
    .org 0x7544a-ORIGIN
P_0007544a:
    .byte 0x94
    .org 0x7544b-ORIGIN
P_0007544b:
    .byte 0x4e
    .org 0x7544c-ORIGIN
P_0007544c:
    .byte 0x00
    .org 0x7544d-ORIGIN
P_0007544d:
    .byte 0x02
    .org 0x7544e-ORIGIN
P_0007544e:
    .byte 0x1b
    .org 0x7544f-ORIGIN
P_0007544f:
    .byte 0xbc
    .org 0x75450-ORIGIN
P_00075450:
    .byte 0x01
    .org 0x75451-ORIGIN
P_00075451:
    .byte 0xff
    .org 0x75452-ORIGIN
P_00075452:
    .byte 0xff
    .org 0x75453-ORIGIN
P_00075453:
    .byte 0xff
