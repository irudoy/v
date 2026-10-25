! Independently assembled bounded word-state and byte-view instructions.
! Caller reachability, helper output ranges and distant GBR preservation are separate obligations.
    .text
    .balign 4
    .set ORIGIN,0x2c2cc
    .org 0x2c2cc-ORIGIN
L_0002c2cc:
    mov.w L_0002c3f4,r2
    .org 0x2c2ce-ORIGIN
L_0002c2ce:
    mov r2,r0
    .org 0x2c2d0-ORIGIN
L_0002c2d0:
    mov.w r0,@(0x10,gbr)
    .org 0x2c3f4-ORIGIN
L_0002c3f4:
    .word 0xda80
    .org 0x35ce8-ORIGIN
L_00035ce8:
    mov.l L_00035e40,r6
    .org 0x35cea-ORIGIN
L_00035cea:
    mov.w L_00035d5e,r0
    .org 0x35cec-ORIGIN
L_00035cec:
    mov.w @(r0,r6),r2
    .org 0x35cee-ORIGIN
L_00035cee:
    extu.w r2,r6
    .org 0x35cf0-ORIGIN
L_00035cf0:
    mov #0x76,r2
    .org 0x35cf2-ORIGIN
L_00035cf2:
    mul.l r6,r2
    .org 0x35cf4-ORIGIN
L_00035cf4:
    mov.l L_00035e44,r6
    .org 0x35cf6-ORIGIN
L_00035cf6:
    mov.l L_00035e3c,r2
    .org 0x35cf8-ORIGIN
L_00035cf8:
    sts macl,r4
    .org 0x35cfa-ORIGIN
L_00035cfa:
    add r6,r4
    .org 0x35d5e-ORIGIN
L_00035d5e:
    .word 0x0446
    .org 0x35e3c-ORIGIN
L_00035e3c:
    .long 0x00037acc
    .org 0x35e40-ORIGIN
L_00035e40:
    .long 0xffff128c
    .org 0x35e44-ORIGIN
L_00035e44:
    .long 0x00018000
    .org 0x3cb9c-ORIGIN
L_0003cb9c:
    mov.w @(0x8,r15),r0
    .org 0x3cb9e-ORIGIN
L_0003cb9e:
    mov.l L_0003cd28,r6
    .org 0x3cba0-ORIGIN
L_0003cba0:
    extu.w r0,r2
    .org 0x3cba2-ORIGIN
L_0003cba2:
    mov.w r0,@(0x168,gbr)
    .org 0x3cba4-ORIGIN
L_0003cba4:
    shll2 r2
    .org 0x3cba6-ORIGIN
L_0003cba6:
    extu.w r2,r2
    .org 0x3cba8-ORIGIN
L_0003cba8:
    shll2 r2
    .org 0x3cbaa-ORIGIN
L_0003cbaa:
    extu.w r2,r2
    .org 0x3cbac-ORIGIN
L_0003cbac:
    shll2 r2
    .org 0x3cbae-ORIGIN
L_0003cbae:
    mov #0x76,r0
    .org 0x3cbb0-ORIGIN
L_0003cbb0:
    mov.w r2,@(r0,r6)
    .org 0x3cc44-ORIGIN
L_0003cc44:
    mov.l L_0003cd28,r2
    .org 0x3cc46-ORIGIN
L_0003cc46:
    mov #0x76,r0
    .org 0x3cc48-ORIGIN
L_0003cc48:
    mov.l L_0003cd3c,r13
    .org 0x3cc4a-ORIGIN
L_0003cc4a:
    sub r4,r5
    .org 0x3cc4c-ORIGIN
L_0003cc4c:
    mov.w @(r0,r2),r7
    .org 0x3cc76-ORIGIN
L_0003cc76:
    mov.l L_0003cd28,r3
    .org 0x3cc78-ORIGIN
L_0003cc78:
    mov #0x76,r0
    .org 0x3cc7a-ORIGIN
L_0003cc7a:
    mov.w @(r0,r3),r4
    .org 0x3cc9e-ORIGIN
L_0003cc9e:
    mov.w @(0x10,gbr),r0
    .org 0x3cd28-ORIGIN
L_0003cd28:
    .long 0xffff1114
    .org 0x3cd3c-ORIGIN
L_0003cd3c:
    .long 0xffff55bc
    .org 0x3cd5a-ORIGIN
L_0003cd5a:
    mov #0x4a,r0
    .org 0x3cd5c-ORIGIN
L_0003cd5c:
    mov.w @(r0,r13),r5
    .org 0x3cd5e-ORIGIN
L_0003cd5e:
    mov r5,r0
    .org 0x3cd60-ORIGIN
L_0003cd60:
    mov.w r0,@(0x10,gbr)
    .org 0x3cda4-ORIGIN
L_0003cda4:
    mov.w @(0x10,gbr),r0
    .org 0x3cda6-ORIGIN
L_0003cda6:
    mov.l r0,@r15
    .org 0x3cda8-ORIGIN
L_0003cda8:
    mov r0,r2
    .org 0x3cdea-ORIGIN
L_0003cdea:
    mov.w @(0x10,gbr),r0
    .org 0x3cdec-ORIGIN
L_0003cdec:
    mov #-0x2,r6
    .org 0x3cdee-ORIGIN
L_0003cdee:
    extu.b r6,r6
    .org 0x3cdf0-ORIGIN
L_0003cdf0:
    extu.w r0,r2
    .org 0x3cdf2-ORIGIN
L_0003cdf2:
    shlr8 r2
    .org 0x3cdf4-ORIGIN
L_0003cdf4:
    extu.b r2,r5
    .org 0x3ce4e-ORIGIN
L_0003ce4e:
    mov.w @(0x76,gbr),r0
    .org 0x3ce8e-ORIGIN
L_0003ce8e:
    mov.w @(0x76,gbr),r0
    .org 0x3ceb8-ORIGIN
L_0003ceb8:
    mov.w @(0x76,gbr),r0
    .org 0x3ceba-ORIGIN
L_0003ceba:
    bra L_0003cecc
    .org 0x3cebc-ORIGIN
L_0003cebc:
    mov.l r0,@r15
    .org 0x3cebe-ORIGIN
L_0003cebe:
    cmp/eq #0x2,r0
    .org 0x3cec0-ORIGIN
L_0003cec0:
    bf L_0003cec8
    .org 0x3cec2-ORIGIN
L_0003cec2:
    mov.w @(0x76,gbr),r0
    .org 0x3cec4-ORIGIN
L_0003cec4:
    bra L_0003cecc
    .org 0x3cec6-ORIGIN
L_0003cec6:
    mov.l r0,@(0x4,r15)
    .org 0x3cec8-ORIGIN
L_0003cec8:
    mov.l L_0003cf20,r6
    .org 0x3ceca-ORIGIN
L_0003ceca:
    mov.w @(0x10,r6),r0
    .org 0x3cecc-ORIGIN
L_0003cecc:
    mov.w r0,@(0x5a,gbr)
    .org 0x3cf20-ORIGIN
L_0003cf20:
    .long 0xffff4534
    .org 0x4a030-ORIGIN
L_0004a030:
    mov.l L_0004a214,r5
    .org 0x4a032-ORIGIN
L_0004a032:
    shll r14
    .org 0x4a034-ORIGIN
L_0004a034:
    mov r0,r2
    .org 0x4a036-ORIGIN
L_0004a036:
    mov r14,r0
    .org 0x4a038-ORIGIN
L_0004a038:
    add #-0x2,r5
    .org 0x4a03a-ORIGIN
L_0004a03a:
    mov.w r2,@(r0,r5)
    .org 0x4a214-ORIGIN
L_0004a214:
    .long 0xffff2144
    .org 0x4a2fe-ORIGIN
L_0004a2fe:
    mov.l L_0004a4cc,r3
    .org 0x4a300-ORIGIN
L_0004a300:
    mov.b @(0xa,r3),r0
    .org 0x4a302-ORIGIN
L_0004a302:
    mov r0,r4
    .org 0x4a304-ORIGIN
L_0004a304:
    mov.l L_0004a4e4,r2
    .org 0x4a306-ORIGIN
L_0004a306:
    extu.b r4,r4
    .org 0x4a308-ORIGIN
L_0004a308:
    mov.l L_0004a4e8,r5
    .org 0x4a30a-ORIGIN
L_0004a30a:
    mov r4,r6
    .org 0x4a30c-ORIGIN
L_0004a30c:
    add #-0x4,r2
    .org 0x4a30e-ORIGIN
L_0004a30e:
    mov r4,r0
    .org 0x4a310-ORIGIN
L_0004a310:
    shll2 r0
    .org 0x4a312-ORIGIN
L_0004a312:
    add #-0x2,r5
    .org 0x4a314-ORIGIN
L_0004a314:
    mov.l @(r0,r2),r7
    .org 0x4a316-ORIGIN
L_0004a316:
    shll r6
    .org 0x4a318-ORIGIN
L_0004a318:
    mov r6,r0
    .org 0x4a31a-ORIGIN
L_0004a31a:
    mov.w @(r0,r5),r2
    .org 0x4a35c-ORIGIN
L_0004a35c:
    tst r0,r0
    .org 0x4a35e-ORIGIN
L_0004a35e:
    bt L_0004a386
    .org 0x4a360-ORIGIN
L_0004a360:
    mov #0x1,r0
    .org 0x4a362-ORIGIN
L_0004a362:
    mov.l L_0004a4d0,r3
    .org 0x4a364-ORIGIN
L_0004a364:
    shll8 r0
    .org 0x4a366-ORIGIN
L_0004a366:
    add #0x4e,r0
    .org 0x4a368-ORIGIN
L_0004a368:
    mov.b @(r0,r3),r6
    .org 0x4a36a-ORIGIN
L_0004a36a:
    mov #-0x1,r5
    .org 0x4a36c-ORIGIN
L_0004a36c:
    extu.b r5,r5
    .org 0x4a36e-ORIGIN
L_0004a36e:
    extu.b r6,r6
    .org 0x4a370-ORIGIN
L_0004a370:
    mov r6,r2
    .org 0x4a372-ORIGIN
L_0004a372:
    add #0x1,r2
    .org 0x4a374-ORIGIN
L_0004a374:
    cmp/gt r5,r2
    .org 0x4a376-ORIGIN
L_0004a376:
    bt L_0004a3fe
    .org 0x4a378-ORIGIN
L_0004a378:
    add #0x1,r6
    .org 0x4a37a-ORIGIN
L_0004a37a:
    mov r6,r2
    .org 0x4a37c-ORIGIN
L_0004a37c:
    mov #0x1,r0
    .org 0x4a37e-ORIGIN
L_0004a37e:
    mov.l L_0004a4d0,r3
    .org 0x4a380-ORIGIN
L_0004a380:
    shll8 r0
    .org 0x4a382-ORIGIN
L_0004a382:
    add #0x4e,r0
    .org 0x4a384-ORIGIN
L_0004a384:
    mov.b r2,@(r0,r3)
    .org 0x4a3fe-ORIGIN
L_0004a3fe:
    bra L_0004a37c
    .org 0x4a400-ORIGIN
L_0004a400:
    mov r5,r2
    .org 0x4a402-ORIGIN
L_0004a402:
    mov #0x1,r0
    .org 0x4a404-ORIGIN
L_0004a404:
    mov.l L_0004a4d0,r3
    .org 0x4a406-ORIGIN
L_0004a406:
    shll8 r0
    .org 0x4a408-ORIGIN
L_0004a408:
    add #0x4f,r0
    .org 0x4a40a-ORIGIN
L_0004a40a:
    mov.b @(r0,r3),r4
    .org 0x4a40c-ORIGIN
L_0004a40c:
    bra L_0004a304
    .org 0x4a40e-ORIGIN
L_0004a40e:
    nop
    .org 0x4a4cc-ORIGIN
L_0004a4cc:
    .long 0xffff11d4
    .org 0x4a4d0-ORIGIN
L_0004a4d0:
    .long 0xffff1ff4
    .org 0x4a4e4-ORIGIN
L_0004a4e4:
    .long 0xffff21d8
    .org 0x4a4e8-ORIGIN
L_0004a4e8:
    .long 0xffff2144
    .org 0x7e670-ORIGIN
L_0007e670:
    mov.l L_0007e838,r6
    .org 0x7e672-ORIGIN
L_0007e672:
    mov.w L_0007e6d0,r0
    .org 0x7e674-ORIGIN
L_0007e674:
    mov.w @(r0,r6),r2
    .org 0x7e676-ORIGIN
L_0007e676:
    mov #0x76,r6
    .org 0x7e678-ORIGIN
L_0007e678:
    extu.w r2,r2
    .org 0x7e67a-ORIGIN
L_0007e67a:
    shlr2 r2
    .org 0x7e67c-ORIGIN
L_0007e67c:
    mul.l r2,r6
    .org 0x7e67e-ORIGIN
L_0007e67e:
    sts macl,r5
    .org 0x7e6d0-ORIGIN
L_0007e6d0:
    .word 0x0446
    .org 0x7e7ba-ORIGIN
L_0007e7ba:
    mov.l L_0007e838,r6
    .org 0x7e7bc-ORIGIN
L_0007e7bc:
    mov.w L_0007e7fa,r0
    .org 0x7e7be-ORIGIN
L_0007e7be:
    mov.w @(r0,r6),r2
    .org 0x7e7c0-ORIGIN
L_0007e7c0:
    mov #0x76,r6
    .org 0x7e7c2-ORIGIN
L_0007e7c2:
    extu.w r2,r2
    .org 0x7e7c4-ORIGIN
L_0007e7c4:
    shlr2 r2
    .org 0x7e7c6-ORIGIN
L_0007e7c6:
    mul.l r2,r6
    .org 0x7e7c8-ORIGIN
L_0007e7c8:
    sts macl,r5
    .org 0x7e7fa-ORIGIN
L_0007e7fa:
    .word 0x0446
    .org 0x7e838-ORIGIN
L_0007e838:
    .long 0xffff128c
    .org 0xa81fa-ORIGIN
L_000a81fa:
    mov.l L_000a83d4,r6
    .org 0xa81fc-ORIGIN
L_000a81fc:
    mov.b r0,@(0x1,gbr)
    .org 0xa81fe-ORIGIN
L_000a81fe:
    mov.w @(0x10,r6),r0
    .org 0xa8200-ORIGIN
L_000a8200:
    extu.w r0,r0
    .org 0xa8202-ORIGIN
L_000a8202:
    shlr8 r0
    .org 0xa8204-ORIGIN
L_000a8204:
    mov.b r0,@(0x2,gbr)
    .org 0xa83d4-ORIGIN
L_000a83d4:
    .long 0xffff4534
