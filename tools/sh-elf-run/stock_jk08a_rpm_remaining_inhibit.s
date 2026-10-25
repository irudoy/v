! Exact stock callers, natural RPM consumers and byte16 interpolation closure.
    .text
    .balign 4
    .set ORIGIN,0x84d8
    .org 0x84da-ORIGIN
P_000084da:
    .byte 0x48,0x74,0x5c,0x3c,0x0c
    .org 0x85d9-ORIGIN
P_000085d9:
    .byte 0x24,0x1e
    .org 0x88ed-ORIGIN
P_000088ed:
    .byte 0x4c
    .org 0x8957-ORIGIN
P_00008957:
    .byte 0x08
    .org 0x89fc-ORIGIN
P_000089fc:
    .byte 0x06,0x24
    .org 0x8b3f-ORIGIN
P_00008b3f:
    .byte 0x18
    .org 0x8d0e-ORIGIN
P_00008d0e:
    .byte 0x00
    .org 0x8d15-ORIGIN
P_00008d15:
    .byte 0xbe
    .org 0x90e0-ORIGIN
P_000090e0:
    .byte 0x07,0xd0
    .org 0x911c-ORIGIN
P_0000911c:
    .byte 0x01,0x7d
    .org 0x124d2-ORIGIN
P_000124d2:
    .byte 0x80,0x81,0x81,0x81,0x82,0x82,0x82,0x82,0x84,0x85,0xa9,0xff,0xff,0xff,0xff,0xff
    .org 0x186c9-ORIGIN
P_000186c9:
    .byte 0x01
    .org 0x26388-ORIGIN
L_00026388:
    mov.w P_0002639a,r0
    .org 0x2638a-ORIGIN
L_0002638a:
    extu.b r5,r5
    .org 0x2638c-ORIGIN
L_0002638c:
    cmp/hs r0,r5
    .org 0x2638e-ORIGIN
L_0002638e:
    bt L_00026396
    .org 0x26390-ORIGIN
L_00026390:
    mov.l P_0002639c,r6
    .org 0x26392-ORIGIN
L_00026392:
    jmp @r6
    .org 0x26394-ORIGIN
L_00026394:
    mov #0x0,r3
    .org 0x26396-ORIGIN
L_00026396:
    rts
    .org 0x26398-ORIGIN
L_00026398:
    mov.b @(0xf,r4),r0
    .org 0x2639a-ORIGIN
P_0002639a:
    .byte 0x00,0xf0
    .org 0x2639c-ORIGIN
P_0002639c:
    .byte 0x00,0x02,0x6a,0x84
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
    .byte 0x00,0x02,0x67,0x40
    .org 0x4edc6-ORIGIN
L_0004edc6:
    bsr L_0004f324
    .org 0x4edc8-ORIGIN
L_0004edc8:
    or r0,r14
    .org 0x4edca-ORIGIN
L_0004edca:
    bsr L_0004f494
    .org 0x4edcc-ORIGIN
L_0004edcc:
    or r0,r14
    .org 0x4ede4-ORIGIN
L_0004ede4:
    bsr L_0004f958
    .org 0x4ede6-ORIGIN
L_0004ede6:
    nop
    .org 0x4ede8-ORIGIN
L_0004ede8:
    extu.b r0,r2
    .org 0x4ee00-ORIGIN
L_0004ee00:
    mov.l P_0004ef94,r3
    .org 0x4ee02-ORIGIN
L_0004ee02:
    jsr @r3
    .org 0x4ee04-ORIGIN
L_0004ee04:
    or r0,r14
    .org 0x4ef94-ORIGIN
P_0004ef94:
    .byte 0x00,0x05,0x0a,0x60
    .org 0x4f324-ORIGIN
L_0004f324:
    mov.l r13,@-r15
    .org 0x4f326-ORIGIN
L_0004f326:
    sts.l pr,@-r15
    .org 0x4f328-ORIGIN
L_0004f328:
    stc.l gbr,@-r15
    .org 0x4f32a-ORIGIN
L_0004f32a:
    mov.l P_0004f460,r0
    .org 0x4f32c-ORIGIN
L_0004f32c:
    ldc r0,gbr
    .org 0x4f32e-ORIGIN
L_0004f32e:
    add #-0x4,r15
    .org 0x4f330-ORIGIN
L_0004f330:
    mov.b @(0x33,gbr),r0
    .org 0x4f332-ORIGIN
L_0004f332:
    mov.l P_0004f454,r6
    .org 0x4f334-ORIGIN
L_0004f334:
    extu.b r0,r13
    .org 0x4f336-ORIGIN
L_0004f336:
    mov #0x7a,r0
    .org 0x4f338-ORIGIN
L_0004f338:
    mov.b @(r0,r6),r2
    .org 0x4f33a-ORIGIN
L_0004f33a:
    tst r2,r2
    .org 0x4f33c-ORIGIN
L_0004f33c:
    bf L_0004f42e
    .org 0x4f33e-ORIGIN
L_0004f33e:
    mov.b @(0x3,gbr),r0
    .org 0x4f340-ORIGIN
L_0004f340:
    tst #0x4,r0
    .org 0x4f342-ORIGIN
L_0004f342:
    bt L_0004f42e
    .org 0x4f344-ORIGIN
L_0004f344:
    mov.b @(0xc,gbr),r0
    .org 0x4f346-ORIGIN
L_0004f346:
    tst #0x20,r0
    .org 0x4f348-ORIGIN
L_0004f348:
    bf L_0004f42e
    .org 0x4f34a-ORIGIN
L_0004f34a:
    mov r13,r0
    .org 0x4f34c-ORIGIN
L_0004f34c:
    tst #0x8,r0
    .org 0x4f34e-ORIGIN
L_0004f34e:
    bf L_0004f362
    .org 0x4f350-ORIGIN
L_0004f350:
    mov.l P_0004f474,r7
    .org 0x4f352-ORIGIN
L_0004f352:
    mov #0x64,r2
    .org 0x4f354-ORIGIN
L_0004f354:
    mov #0x20,r0
    .org 0x4f356-ORIGIN
L_0004f356:
    mov.b r2,@(r0,r7)
    .org 0x4f358-ORIGIN
L_0004f358:
    mov r13,r0
    .org 0x4f35a-ORIGIN
L_0004f35a:
    or #0x8,r0
    .org 0x4f35c-ORIGIN
L_0004f35c:
    exts.b r0,r13
    .org 0x4f35e-ORIGIN
L_0004f35e:
    bra L_0004f3ce
    .org 0x4f360-ORIGIN
L_0004f360:
    mov.b r0,@(0x33,gbr)
    .org 0x4f362-ORIGIN
L_0004f362:
    mov.l P_0004f474,r7
    .org 0x4f364-ORIGIN
L_0004f364:
    mov #0x20,r0
    .org 0x4f366-ORIGIN
L_0004f366:
    mov.b @(r0,r7),r2
    .org 0x4f368-ORIGIN
L_0004f368:
    tst r2,r2
    .org 0x4f36a-ORIGIN
L_0004f36a:
    bf L_0004f3ce
    .org 0x4f36c-ORIGIN
L_0004f36c:
    mov.l P_0004f46c,r4
    .org 0x4f36e-ORIGIN
L_0004f36e:
    mov.w P_0004f378,r6
    .org 0x4f370-ORIGIN
L_0004f370:
    mov.w @(r0,r4),r2
    .org 0x4f372-ORIGIN
L_0004f372:
    extu.w r2,r2
    .org 0x4f374-ORIGIN
L_0004f374:
    bra L_0004f37a
    .org 0x4f376-ORIGIN
L_0004f376:
    add r6,r2
    .org 0x4f378-ORIGIN
P_0004f378:
    .byte 0xff,0x60
    .org 0x4f37a-ORIGIN
L_0004f37a:
    mov #0x0,r6
    .org 0x4f37c-ORIGIN
L_0004f37c:
    cmp/gt r2,r6
    .org 0x4f37e-ORIGIN
L_0004f37e:
    addc r6,r2
    .org 0x4f380-ORIGIN
L_0004f380:
    shar r2
    .org 0x4f382-ORIGIN
L_0004f382:
    cmp/pz r2
    .org 0x4f384-ORIGIN
L_0004f384:
    bt L_0004f388
    .org 0x4f386-ORIGIN
L_0004f386:
    mov #0x0,r2
    .org 0x4f388-ORIGIN
L_0004f388:
    mov #-0x1,r6
    .org 0x4f38a-ORIGIN
L_0004f38a:
    extu.b r6,r6
    .org 0x4f38c-ORIGIN
L_0004f38c:
    cmp/gt r6,r2
    .org 0x4f38e-ORIGIN
L_0004f38e:
    bf L_0004f392
    .org 0x4f390-ORIGIN
L_0004f390:
    mov r6,r2
    .org 0x4f392-ORIGIN
L_0004f392:
    mov r2,r5
    .org 0x4f394-ORIGIN
L_0004f394:
    mov.l P_0004f478,r4
    .org 0x4f396-ORIGIN
L_0004f396:
    mov.l P_0004f47c,r2
    .org 0x4f398-ORIGIN
L_0004f398:
    jsr @r2
    .org 0x4f39a-ORIGIN
L_0004f39a:
    extu.b r5,r5
    .org 0x4f39c-ORIGIN
L_0004f39c:
    extu.b r0,r2
    .org 0x4f39e-ORIGIN
L_0004f39e:
    mov.l P_0004f480,r5
    .org 0x4f3a0-ORIGIN
L_0004f3a0:
    mov.w P_0004f450,r0
    .org 0x4f3a2-ORIGIN
L_0004f3a2:
    add #-0x80,r2
    .org 0x4f3a4-ORIGIN
L_0004f3a4:
    mov.w @(r0,r5),r6
    .org 0x4f3a6-ORIGIN
L_0004f3a6:
    mov.b @(0x33,gbr),r0
    .org 0x4f3a8-ORIGIN
L_0004f3a8:
    extu.w r6,r6
    .org 0x4f3aa-ORIGIN
L_0004f3aa:
    add r2,r6
    .org 0x4f3ac-ORIGIN
L_0004f3ac:
    mov r0,r13
    .org 0x4f3ae-ORIGIN
L_0004f3ae:
    cmp/pz r6
    .org 0x4f3b0-ORIGIN
L_0004f3b0:
    bt/s L_0004f3b6
    .org 0x4f3b2-ORIGIN
L_0004f3b2:
    mov.l r6,@r15
    .org 0x4f3b4-ORIGIN
L_0004f3b4:
    mov #0x0,r6
    .org 0x4f3b6-ORIGIN
L_0004f3b6:
    mov #-0x1,r2
    .org 0x4f3b8-ORIGIN
L_0004f3b8:
    extu.w r2,r2
    .org 0x4f3ba-ORIGIN
L_0004f3ba:
    cmp/gt r2,r6
    .org 0x4f3bc-ORIGIN
L_0004f3bc:
    bf L_0004f3c0
    .org 0x4f3be-ORIGIN
L_0004f3be:
    mov r2,r6
    .org 0x4f3c0-ORIGIN
L_0004f3c0:
    mov.l P_0004f480,r5
    .org 0x4f3c2-ORIGIN
L_0004f3c2:
    mov #0x64,r2
    .org 0x4f3c4-ORIGIN
L_0004f3c4:
    mov.w P_0004f450,r0
    .org 0x4f3c6-ORIGIN
L_0004f3c6:
    mov.l P_0004f474,r7
    .org 0x4f3c8-ORIGIN
L_0004f3c8:
    mov.w r6,@(r0,r5)
    .org 0x4f3ca-ORIGIN
L_0004f3ca:
    mov #0x20,r0
    .org 0x4f3cc-ORIGIN
L_0004f3cc:
    mov.b r2,@(r0,r7)
    .org 0x4f3ce-ORIGIN
L_0004f3ce:
    mov.l P_0004f480,r5
    .org 0x4f3d0-ORIGIN
L_0004f3d0:
    mov.w P_0004f450,r0
    .org 0x4f3d2-ORIGIN
L_0004f3d2:
    mov.w @(r0,r5),r6
    .org 0x4f3d4-ORIGIN
L_0004f3d4:
    mov.l P_0004f484,r5
    .org 0x4f3d6-ORIGIN
L_0004f3d6:
    mov.w @r5,r2
    .org 0x4f3d8-ORIGIN
L_0004f3d8:
    cmp/hs r2,r6
    .org 0x4f3da-ORIGIN
L_0004f3da:
    bf L_0004f3f4
    .org 0x4f3dc-ORIGIN
L_0004f3dc:
    mov.l P_0004f488,r2
    .org 0x4f3de-ORIGIN
L_0004f3de:
    mov.l P_0004f48c,r5
    .org 0x4f3e0-ORIGIN
L_0004f3e0:
    mov.b @(0x9,r2),r0
    .org 0x4f3e2-ORIGIN
L_0004f3e2:
    mov.b @r5,r2
    .org 0x4f3e4-ORIGIN
L_0004f3e4:
    cmp/hs r2,r0
    .org 0x4f3e6-ORIGIN
L_0004f3e6:
    bt L_0004f3ee
    .org 0x4f3e8-ORIGIN
L_0004f3e8:
    mov.b @(0x11,gbr),r0
    .org 0x4f3ea-ORIGIN
L_0004f3ea:
    tst #0x40,r0
    .org 0x4f3ec-ORIGIN
L_0004f3ec:
    bt L_0004f3f4
    .org 0x4f3ee-ORIGIN
L_0004f3ee:
    mov r13,r0
    .org 0x4f3f0-ORIGIN
L_0004f3f0:
    bra L_0004f3f8
    .org 0x4f3f2-ORIGIN
L_0004f3f2:
    or #0x10,r0
    .org 0x4f3f4-ORIGIN
L_0004f3f4:
    mov r13,r0
    .org 0x4f3f6-ORIGIN
L_0004f3f6:
    and #0xef,r0
    .org 0x4f3f8-ORIGIN
L_0004f3f8:
    mov.b r0,@(0x33,gbr)
    .org 0x4f3fa-ORIGIN
L_0004f3fa:
    exts.b r0,r0
    .org 0x4f3fc-ORIGIN
L_0004f3fc:
    tst #0x20,r0
    .org 0x4f3fe-ORIGIN
L_0004f3fe:
    bt/s L_0004f414
    .org 0x4f400-ORIGIN
L_0004f400:
    mov r0,r5
    .org 0x4f402-ORIGIN
L_0004f402:
    mov.l P_0004f46c,r4
    .org 0x4f404-ORIGIN
L_0004f404:
    mov #0x12,r0
    .org 0x4f406-ORIGIN
L_0004f406:
    mov.b @(r0,r4),r6
    .org 0x4f408-ORIGIN
L_0004f408:
    mov.l P_0004f490,r4
    .org 0x4f40a-ORIGIN
L_0004f40a:
    mov.b @(0x1,r4),r0
    .org 0x4f40c-ORIGIN
L_0004f40c:
    cmp/hs r0,r6
    .org 0x4f40e-ORIGIN
L_0004f40e:
    bt L_0004f43c
    .org 0x4f410-ORIGIN
L_0004f410:
    bra L_0004f438
    .org 0x4f412-ORIGIN
L_0004f412:
    mov r5,r0
    .org 0x4f414-ORIGIN
L_0004f414:
    mov r5,r0
    .org 0x4f416-ORIGIN
L_0004f416:
    tst #0x10,r0
    .org 0x4f418-ORIGIN
L_0004f418:
    bt L_0004f43c
    .org 0x4f41a-ORIGIN
L_0004f41a:
    mov.l P_0004f46c,r4
    .org 0x4f41c-ORIGIN
L_0004f41c:
    mov #0x12,r0
    .org 0x4f41e-ORIGIN
L_0004f41e:
    mov.b @(r0,r4),r6
    .org 0x4f420-ORIGIN
L_0004f420:
    mov.l P_0004f490,r4
    .org 0x4f422-ORIGIN
L_0004f422:
    mov.b @r4,r2
    .org 0x4f424-ORIGIN
L_0004f424:
    cmp/hs r2,r6
    .org 0x4f426-ORIGIN
L_0004f426:
    bf L_0004f43c
    .org 0x4f428-ORIGIN
L_0004f428:
    mov r5,r0
    .org 0x4f42a-ORIGIN
L_0004f42a:
    bra L_0004f43a
    .org 0x4f42c-ORIGIN
L_0004f42c:
    or #0x20,r0
    .org 0x4f42e-ORIGIN
L_0004f42e:
    mov.l P_0004f480,r5
    .org 0x4f430-ORIGIN
L_0004f430:
    mov #0x0,r2
    .org 0x4f432-ORIGIN
L_0004f432:
    mov.w P_0004f450,r0
    .org 0x4f434-ORIGIN
L_0004f434:
    mov.w r2,@(r0,r5)
    .org 0x4f436-ORIGIN
L_0004f436:
    mov r13,r0
    .org 0x4f438-ORIGIN
L_0004f438:
    and #0xc7,r0
    .org 0x4f43a-ORIGIN
L_0004f43a:
    mov.b r0,@(0x33,gbr)
    .org 0x4f43c-ORIGIN
L_0004f43c:
    mov.b @(0x33,gbr),r0
    .org 0x4f43e-ORIGIN
L_0004f43e:
    tst #0x20,r0
    .org 0x4f440-ORIGIN
L_0004f440:
    movt r0
    .org 0x4f442-ORIGIN
L_0004f442:
    xor #0x1,r0
    .org 0x4f444-ORIGIN
L_0004f444:
    extu.b r0,r0
    .org 0x4f446-ORIGIN
L_0004f446:
    add #0x4,r15
    .org 0x4f448-ORIGIN
L_0004f448:
    ldc.l @r15+,gbr
    .org 0x4f44a-ORIGIN
L_0004f44a:
    lds.l @r15+,pr
    .org 0x4f44c-ORIGIN
L_0004f44c:
    rts
    .org 0x4f44e-ORIGIN
L_0004f44e:
    mov.l @r15+,r13
    .org 0x4f450-ORIGIN
P_0004f450:
    .byte 0x04,0x1a
    .org 0x4f454-ORIGIN
P_0004f454:
    .byte 0xff,0xff,0x10,0x94
    .org 0x4f460-ORIGIN
P_0004f460:
    .byte 0xff,0xff,0x24,0x4c
    .org 0x4f46c-ORIGIN
P_0004f46c:
    .byte 0xff,0xff,0x11,0x9c
    .org 0x4f474-ORIGIN
P_0004f474:
    .byte 0xff,0xff,0x25,0x6a
    .org 0x4f478-ORIGIN
P_0004f478:
    .byte 0x00,0x01,0x24,0xd2
    .org 0x4f47c-ORIGIN
P_0004f47c:
    .byte 0x00,0x02,0x63,0x88
    .org 0x4f480-ORIGIN
P_0004f480:
    .byte 0xff,0xff,0x12,0x8c
    .org 0x4f484-ORIGIN
P_0004f484:
    .byte 0x00,0x00,0x91,0x1c
    .org 0x4f488-ORIGIN
P_0004f488:
    .byte 0xff,0xff,0x10,0x68
    .org 0x4f48c-ORIGIN
P_0004f48c:
    .byte 0x00,0x00,0x8d,0x0e
    .org 0x4f490-ORIGIN
P_0004f490:
    .byte 0x00,0x00,0x85,0xd9
    .org 0x4f494-ORIGIN
L_0004f494:
    mov.l r9,@-r15
    .org 0x4f496-ORIGIN
L_0004f496:
    mov.l r10,@-r15
    .org 0x4f498-ORIGIN
L_0004f498:
    mov.l r11,@-r15
    .org 0x4f49a-ORIGIN
L_0004f49a:
    mov.l r12,@-r15
    .org 0x4f49c-ORIGIN
L_0004f49c:
    mov.l r13,@-r15
    .org 0x4f49e-ORIGIN
L_0004f49e:
    sts.l pr,@-r15
    .org 0x4f4a0-ORIGIN
L_0004f4a0:
    stc.l gbr,@-r15
    .org 0x4f4a2-ORIGIN
L_0004f4a2:
    mov.l P_0004f6bc,r0
    .org 0x4f4a4-ORIGIN
L_0004f4a4:
    ldc r0,gbr
    .org 0x4f4a6-ORIGIN
L_0004f4a6:
    add #-0x4,r15
    .org 0x4f4a8-ORIGIN
L_0004f4a8:
    mov.l P_0004f6c0,r2
    .org 0x4f4aa-ORIGIN
L_0004f4aa:
    mov.b @(0x1,r2),r0
    .org 0x4f4ac-ORIGIN
L_0004f4ac:
    tst #0x1,r0
    .org 0x4f4ae-ORIGIN
L_0004f4ae:
    bf/s L_0004f4b6
    .org 0x4f4b0-ORIGIN
L_0004f4b0:
    mov.b r0,@r15
    .org 0x4f4b2-ORIGIN
L_0004f4b2:
    bra L_0004f646
    .org 0x4f4b4-ORIGIN
L_0004f4b4:
    nop
    .org 0x4f4b6-ORIGIN
L_0004f4b6:
    mov.b @(0x0,gbr),r0
    .org 0x4f4b8-ORIGIN
L_0004f4b8:
    mov #0x0,r10
    .org 0x4f4ba-ORIGIN
L_0004f4ba:
    mov r10,r9
    .org 0x4f4bc-ORIGIN
L_0004f4bc:
    mov r0,r11
    .org 0x4f4be-ORIGIN
L_0004f4be:
    mov r0,r13
    .org 0x4f4c0-ORIGIN
L_0004f4c0:
    mov.b @(0x6e,gbr),r0
    .org 0x4f4c2-ORIGIN
L_0004f4c2:
    mov r0,r4
    .org 0x4f4c4-ORIGIN
L_0004f4c4:
    mov r11,r0
    .org 0x4f4c6-ORIGIN
L_0004f4c6:
    and #0x40,r0
    .org 0x4f4c8-ORIGIN
L_0004f4c8:
    tst r0,r0
    .org 0x4f4ca-ORIGIN
L_0004f4ca:
    bf/s L_0004f51a
    .org 0x4f4cc-ORIGIN
L_0004f4cc:
    mov r0,r11
    .org 0x4f4ce-ORIGIN
L_0004f4ce:
    mov.l P_0004f6c4,r2
    .org 0x4f4d0-ORIGIN
L_0004f4d0:
    mov #0x72,r0
    .org 0x4f4d2-ORIGIN
L_0004f4d2:
    mov #0x3,r6
    .org 0x4f4d4-ORIGIN
L_0004f4d4:
    mov.b @(r0,r2),r5
    .org 0x4f4d6-ORIGIN
L_0004f4d6:
    extu.b r5,r5
    .org 0x4f4d8-ORIGIN
L_0004f4d8:
    cmp/ge r6,r5
    .org 0x4f4da-ORIGIN
L_0004f4da:
    bf L_0004f4fe
    .org 0x4f4dc-ORIGIN
L_0004f4dc:
    mov #-0xe,r2
    .org 0x4f4de-ORIGIN
L_0004f4de:
    extu.b r2,r2
    .org 0x4f4e0-ORIGIN
L_0004f4e0:
    cmp/ge r2,r5
    .org 0x4f4e2-ORIGIN
L_0004f4e2:
    bt L_0004f4fe
    .org 0x4f4e4-ORIGIN
L_0004f4e4:
    mov.l P_0004f6c8,r7
    .org 0x4f4e6-ORIGIN
L_0004f4e6:
    mov #-0x3d,r0
    .org 0x4f4e8-ORIGIN
L_0004f4e8:
    mov #0x32,r2
    .org 0x4f4ea-ORIGIN
L_0004f4ea:
    extu.b r0,r0
    .org 0x4f4ec-ORIGIN
L_0004f4ec:
    mov.b r2,@(r0,r7)
    .org 0x4f4ee-ORIGIN
L_0004f4ee:
    mov #-0x3c,r0
    .org 0x4f4f0-ORIGIN
L_0004f4f0:
    extu.b r0,r0
    .org 0x4f4f2-ORIGIN
L_0004f4f2:
    mov.b @(r0,r7),r2
    .org 0x4f4f4-ORIGIN
L_0004f4f4:
    tst r2,r2
    .org 0x4f4f6-ORIGIN
L_0004f4f6:
    bf L_0004f52c
    .org 0x4f4f8-ORIGIN
L_0004f4f8:
    mov r4,r0
    .org 0x4f4fa-ORIGIN
L_0004f4fa:
    bra L_0004f516
    .org 0x4f4fc-ORIGIN
L_0004f4fc:
    and #0xfb,r0
    .org 0x4f4fe-ORIGIN
L_0004f4fe:
    mov.l P_0004f6c8,r7
    .org 0x4f500-ORIGIN
L_0004f500:
    mov #-0x3c,r0
    .org 0x4f502-ORIGIN
L_0004f502:
    mov #0xa,r2
    .org 0x4f504-ORIGIN
L_0004f504:
    extu.b r0,r0
    .org 0x4f506-ORIGIN
L_0004f506:
    mov.b r2,@(r0,r7)
    .org 0x4f508-ORIGIN
L_0004f508:
    mov #-0x3d,r0
    .org 0x4f50a-ORIGIN
L_0004f50a:
    extu.b r0,r0
    .org 0x4f50c-ORIGIN
L_0004f50c:
    mov.b @(r0,r7),r2
    .org 0x4f50e-ORIGIN
L_0004f50e:
    tst r2,r2
    .org 0x4f510-ORIGIN
L_0004f510:
    bf L_0004f52c
    .org 0x4f512-ORIGIN
L_0004f512:
    mov r4,r0
    .org 0x4f514-ORIGIN
L_0004f514:
    or #0x4,r0
    .org 0x4f516-ORIGIN
L_0004f516:
    bra L_0004f52c
    .org 0x4f518-ORIGIN
L_0004f518:
    mov.b r0,@(0x6e,gbr)
    .org 0x4f51a-ORIGIN
L_0004f51a:
    mov.l P_0004f6c8,r7
    .org 0x4f51c-ORIGIN
L_0004f51c:
    mov #-0x3c,r0
    .org 0x4f51e-ORIGIN
L_0004f51e:
    mov #0xa,r2
    .org 0x4f520-ORIGIN
L_0004f520:
    extu.b r0,r0
    .org 0x4f522-ORIGIN
L_0004f522:
    mov.b r2,@(r0,r7)
    .org 0x4f524-ORIGIN
L_0004f524:
    mov #-0x3d,r0
    .org 0x4f526-ORIGIN
L_0004f526:
    mov #0x32,r2
    .org 0x4f528-ORIGIN
L_0004f528:
    extu.b r0,r0
    .org 0x4f52a-ORIGIN
L_0004f52a:
    mov.b r2,@(r0,r7)
    .org 0x4f52c-ORIGIN
L_0004f52c:
    mov.b @(0x6e,gbr),r0
    .org 0x4f52e-ORIGIN
L_0004f52e:
    mov r0,r12
    .org 0x4f530-ORIGIN
L_0004f530:
    mov r13,r0
    .org 0x4f532-ORIGIN
L_0004f532:
    tst #0x80,r0
    .org 0x4f534-ORIGIN
L_0004f534:
    bt L_0004f544
    .org 0x4f536-ORIGIN
L_0004f536:
    mov r12,r0
    .org 0x4f538-ORIGIN
L_0004f538:
    tst #0x8,r0
    .org 0x4f53a-ORIGIN
L_0004f53a:
    bt L_0004f558
    .org 0x4f53c-ORIGIN
L_0004f53c:
    mov.l P_0004f6cc,r5
    .org 0x4f53e-ORIGIN
L_0004f53e:
    mov.b @(0x8,r5),r0
    .org 0x4f540-ORIGIN
L_0004f540:
    tst #0x10,r0
    .org 0x4f542-ORIGIN
L_0004f542:
    bf L_0004f558
    .org 0x4f544-ORIGIN
L_0004f544:
    mov r12,r0
    .org 0x4f546-ORIGIN
L_0004f546:
    and #0xf7,r0
    .org 0x4f548-ORIGIN
L_0004f548:
    mov.b r0,@(0x6e,gbr)
    .org 0x4f54a-ORIGIN
L_0004f54a:
    mov #-0x63,r0
    .org 0x4f54c-ORIGIN
L_0004f54c:
    mov.l P_0004f6c8,r7
    .org 0x4f54e-ORIGIN
L_0004f54e:
    mov #0xa,r2
    .org 0x4f550-ORIGIN
L_0004f550:
    extu.b r0,r0
    .org 0x4f552-ORIGIN
L_0004f552:
    mov.b r2,@(r0,r7)
    .org 0x4f554-ORIGIN
L_0004f554:
    mov.b @(0x6e,gbr),r0
    .org 0x4f556-ORIGIN
L_0004f556:
    mov r0,r12
    .org 0x4f558-ORIGIN
L_0004f558:
    mov.l P_0004f6d0,r2
    .org 0x4f55a-ORIGIN
L_0004f55a:
    mov.b @(0x9,r2),r0
    .org 0x4f55c-ORIGIN
L_0004f55c:
    extu.b r0,r13
    .org 0x4f55e-ORIGIN
L_0004f55e:
    mov.b @(0x85,gbr),r0
    .org 0x4f560-ORIGIN
L_0004f560:
    tst #0x1,r0
    .org 0x4f562-ORIGIN
L_0004f562:
    bt L_0004f566
    .org 0x4f564-ORIGIN
L_0004f564:
    add #0xa,r13
    .org 0x4f566-ORIGIN
L_0004f566:
    mov.l P_0004f6d4,r6
    .org 0x4f568-ORIGIN
L_0004f568:
    mov.b @r6,r2
    .org 0x4f56a-ORIGIN
L_0004f56a:
    extu.b r2,r2
    .org 0x4f56c-ORIGIN
L_0004f56c:
    cmp/hs r2,r13
    .org 0x4f56e-ORIGIN
L_0004f56e:
    mov #-0x7b,r2
    .org 0x4f570-ORIGIN
L_0004f570:
    bt/s L_0004f578
    .org 0x4f572-ORIGIN
L_0004f572:
    extu.b r2,r0
    .org 0x4f574-ORIGIN
L_0004f574:
    bra L_0004f57a
    .org 0x4f576-ORIGIN
L_0004f576:
    and.b #0xfe,@(r0,gbr)
    .org 0x4f578-ORIGIN
L_0004f578:
    or.b #0x1,@(r0,gbr)
    .org 0x4f57a-ORIGIN
L_0004f57a:
    tst r11,r11
    .org 0x4f57c-ORIGIN
L_0004f57c:
    bf L_0004f5aa
    .org 0x4f57e-ORIGIN
L_0004f57e:
    mov.l P_0004f6c4,r2
    .org 0x4f580-ORIGIN
L_0004f580:
    mov #0x72,r0
    .org 0x4f582-ORIGIN
L_0004f582:
    mov #0x3,r6
    .org 0x4f584-ORIGIN
L_0004f584:
    mov.b @(r0,r2),r5
    .org 0x4f586-ORIGIN
L_0004f586:
    extu.b r5,r5
    .org 0x4f588-ORIGIN
L_0004f588:
    cmp/ge r6,r5
    .org 0x4f58a-ORIGIN
L_0004f58a:
    bf L_0004f5aa
    .org 0x4f58c-ORIGIN
L_0004f58c:
    mov #-0xe,r6
    .org 0x4f58e-ORIGIN
L_0004f58e:
    extu.b r6,r6
    .org 0x4f590-ORIGIN
L_0004f590:
    cmp/ge r6,r5
    .org 0x4f592-ORIGIN
L_0004f592:
    bt L_0004f5aa
    .org 0x4f594-ORIGIN
L_0004f594:
    mov.b @(0x85,gbr),r0
    .org 0x4f596-ORIGIN
L_0004f596:
    tst #0x1,r0
    .org 0x4f598-ORIGIN
L_0004f598:
    bt L_0004f5aa
    .org 0x4f59a-ORIGIN
L_0004f59a:
    mov.l P_0004f6c8,r7
    .org 0x4f59c-ORIGIN
L_0004f59c:
    mov #-0x63,r0
    .org 0x4f59e-ORIGIN
L_0004f59e:
    extu.b r0,r0
    .org 0x4f5a0-ORIGIN
L_0004f5a0:
    mov.b @(r0,r7),r2
    .org 0x4f5a2-ORIGIN
L_0004f5a2:
    tst r2,r2
    .org 0x4f5a4-ORIGIN
L_0004f5a4:
    bf L_0004f5b4
    .org 0x4f5a6-ORIGIN
L_0004f5a6:
    bra L_0004f5b4
    .org 0x4f5a8-ORIGIN
L_0004f5a8:
    mov #0x1,r10
    .org 0x4f5aa-ORIGIN
L_0004f5aa:
    mov.l P_0004f6c8,r7
    .org 0x4f5ac-ORIGIN
L_0004f5ac:
    mov #-0x63,r0
    .org 0x4f5ae-ORIGIN
L_0004f5ae:
    mov #0xa,r2
    .org 0x4f5b0-ORIGIN
L_0004f5b0:
    extu.b r0,r0
    .org 0x4f5b2-ORIGIN
L_0004f5b2:
    mov.b r2,@(r0,r7)
    .org 0x4f5b4-ORIGIN
L_0004f5b4:
    mov.l P_0004f6cc,r4
    .org 0x4f5b6-ORIGIN
L_0004f5b6:
    mov.b @(0x8,r4),r0
    .org 0x4f5b8-ORIGIN
L_0004f5b8:
    tst #0x10,r0
    .org 0x4f5ba-ORIGIN
L_0004f5ba:
    bt L_0004f5ce
    .org 0x4f5bc-ORIGIN
L_0004f5bc:
    mov.b @(0x6,r4),r0
    .org 0x4f5be-ORIGIN
L_0004f5be:
    mov #0x28,r6
    .org 0x4f5c0-ORIGIN
L_0004f5c0:
    extu.b r0,r2
    .org 0x4f5c2-ORIGIN
L_0004f5c2:
    cmp/ge r6,r2
    .org 0x4f5c4-ORIGIN
L_0004f5c4:
    bt L_0004f5ce
    .org 0x4f5c6-ORIGIN
L_0004f5c6:
    mov r12,r0
    .org 0x4f5c8-ORIGIN
L_0004f5c8:
    tst #0x4,r0
    .org 0x4f5ca-ORIGIN
L_0004f5ca:
    bt L_0004f5ce
    .org 0x4f5cc-ORIGIN
L_0004f5cc:
    mov #0x1,r9
    .org 0x4f5ce-ORIGIN
L_0004f5ce:
    tst r10,r10
    .org 0x4f5d0-ORIGIN
L_0004f5d0:
    bf L_0004f5dc
    .org 0x4f5d2-ORIGIN
L_0004f5d2:
    tst r9,r9
    .org 0x4f5d4-ORIGIN
L_0004f5d4:
    bf L_0004f5dc
    .org 0x4f5d6-ORIGIN
L_0004f5d6:
    mov r12,r0
    .org 0x4f5d8-ORIGIN
L_0004f5d8:
    bra L_0004f5e0
    .org 0x4f5da-ORIGIN
L_0004f5da:
    and #0xef,r0
    .org 0x4f5dc-ORIGIN
L_0004f5dc:
    mov r12,r0
    .org 0x4f5de-ORIGIN
L_0004f5de:
    or #0x18,r0
    .org 0x4f5e0-ORIGIN
L_0004f5e0:
    mov.b @r15,r6
    .org 0x4f5e2-ORIGIN
L_0004f5e2:
    exts.b r0,r2
    .org 0x4f5e4-ORIGIN
L_0004f5e4:
    mov.b r0,@(0x6e,gbr)
    .org 0x4f5e6-ORIGIN
L_0004f5e6:
    extu.b r6,r6
    .org 0x4f5e8-ORIGIN
L_0004f5e8:
    mov r6,r0
    .org 0x4f5ea-ORIGIN
L_0004f5ea:
    tst #0x1,r0
    .org 0x4f5ec-ORIGIN
L_0004f5ec:
    bt L_0004f5fa
    .org 0x4f5ee-ORIGIN
L_0004f5ee:
    mov r2,r0
    .org 0x4f5f0-ORIGIN
L_0004f5f0:
    tst #0x10,r0
    .org 0x4f5f2-ORIGIN
L_0004f5f2:
    bt L_0004f5fa
    .org 0x4f5f4-ORIGIN
L_0004f5f4:
    mov.l P_0004f6d8,r2
    .org 0x4f5f6-ORIGIN
L_0004f5f6:
    jsr @r2
    .org 0x4f5f8-ORIGIN
L_0004f5f8:
    mov #0x2,r4
    .org 0x4f5fa-ORIGIN
L_0004f5fa:
    mov.l P_0004f6dc,r2
    .org 0x4f5fc-ORIGIN
L_0004f5fc:
    mov #0x17,r0
    .org 0x4f5fe-ORIGIN
L_0004f5fe:
    mov.b @(r0,r2),r13
    .org 0x4f600-ORIGIN
L_0004f600:
    mov.b @(0x6e,gbr),r0
    .org 0x4f602-ORIGIN
L_0004f602:
    mov r0,r12
    .org 0x4f604-ORIGIN
L_0004f604:
    mov.b @(0x6a,gbr),r0
    .org 0x4f606-ORIGIN
L_0004f606:
    tst #0x8,r0
    .org 0x4f608-ORIGIN
L_0004f608:
    bt/s L_0004f614
    .org 0x4f60a-ORIGIN
L_0004f60a:
    extu.b r13,r13
    .org 0x4f60c-ORIGIN
L_0004f60c:
    mov.l P_0004f6e0,r6
    .org 0x4f60e-ORIGIN
L_0004f60e:
    mov.b @r6,r2
    .org 0x4f610-ORIGIN
L_0004f610:
    extu.b r2,r2
    .org 0x4f612-ORIGIN
L_0004f612:
    add r2,r13
    .org 0x4f614-ORIGIN
L_0004f614:
    mov.l P_0004f6e4,r6
    .org 0x4f616-ORIGIN
L_0004f616:
    mov.b @r6,r2
    .org 0x4f618-ORIGIN
L_0004f618:
    extu.b r2,r2
    .org 0x4f61a-ORIGIN
L_0004f61a:
    cmp/hs r2,r13
    .org 0x4f61c-ORIGIN
L_0004f61c:
    bt/s L_0004f624
    .org 0x4f61e-ORIGIN
L_0004f61e:
    mov #0x6a,r0
    .org 0x4f620-ORIGIN
L_0004f620:
    bra L_0004f626
    .org 0x4f622-ORIGIN
L_0004f622:
    and.b #0xf7,@(r0,gbr)
    .org 0x4f624-ORIGIN
L_0004f624:
    or.b #0x8,@(r0,gbr)
    .org 0x4f626-ORIGIN
L_0004f626:
    mov r12,r0
    .org 0x4f628-ORIGIN
L_0004f628:
    tst #0x8,r0
    .org 0x4f62a-ORIGIN
L_0004f62a:
    bt L_0004f640
    .org 0x4f62c-ORIGIN
L_0004f62c:
    mov.l P_0004f6e8,r6
    .org 0x4f62e-ORIGIN
L_0004f62e:
    mov.b @r6,r0
    .org 0x4f630-ORIGIN
L_0004f630:
    tst #0x20,r0
    .org 0x4f632-ORIGIN
L_0004f632:
    bf L_0004f640
    .org 0x4f634-ORIGIN
L_0004f634:
    mov.b @(0x6a,gbr),r0
    .org 0x4f636-ORIGIN
L_0004f636:
    tst #0x8,r0
    .org 0x4f638-ORIGIN
L_0004f638:
    bt L_0004f640
    .org 0x4f63a-ORIGIN
L_0004f63a:
    mov r12,r0
    .org 0x4f63c-ORIGIN
L_0004f63c:
    bra L_0004f644
    .org 0x4f63e-ORIGIN
L_0004f63e:
    or #0x20,r0
    .org 0x4f640-ORIGIN
L_0004f640:
    mov r12,r0
    .org 0x4f642-ORIGIN
L_0004f642:
    and #0xdf,r0
    .org 0x4f644-ORIGIN
L_0004f644:
    mov.b r0,@(0x6e,gbr)
    .org 0x4f646-ORIGIN
L_0004f646:
    mov.b @(0x6e,gbr),r0
    .org 0x4f648-ORIGIN
L_0004f648:
    tst #0x20,r0
    .org 0x4f64a-ORIGIN
L_0004f64a:
    movt r0
    .org 0x4f64c-ORIGIN
L_0004f64c:
    xor #0x1,r0
    .org 0x4f64e-ORIGIN
L_0004f64e:
    extu.b r0,r0
    .org 0x4f650-ORIGIN
L_0004f650:
    add #0x4,r15
    .org 0x4f652-ORIGIN
L_0004f652:
    ldc.l @r15+,gbr
    .org 0x4f654-ORIGIN
L_0004f654:
    lds.l @r15+,pr
    .org 0x4f656-ORIGIN
L_0004f656:
    mov.l @r15+,r13
    .org 0x4f658-ORIGIN
L_0004f658:
    mov.l @r15+,r12
    .org 0x4f65a-ORIGIN
L_0004f65a:
    mov.l @r15+,r11
    .org 0x4f65c-ORIGIN
L_0004f65c:
    mov.l @r15+,r10
    .org 0x4f65e-ORIGIN
L_0004f65e:
    rts
    .org 0x4f660-ORIGIN
L_0004f660:
    mov.l @r15+,r9
    .org 0x4f6bc-ORIGIN
P_0004f6bc:
    .byte 0xff,0xff,0x41,0x84
    .org 0x4f6c0-ORIGIN
P_0004f6c0:
    .byte 0x00,0x01,0x86,0xc8
    .org 0x4f6c4-ORIGIN
P_0004f6c4:
    .byte 0xff,0xff,0x10,0x94
    .org 0x4f6c8-ORIGIN
P_0004f6c8:
    .byte 0xff,0xff,0x42,0xd3
    .org 0x4f6cc-ORIGIN
P_0004f6cc:
    .byte 0xff,0xff,0x57,0x18
    .org 0x4f6d0-ORIGIN
P_0004f6d0:
    .byte 0xff,0xff,0x10,0x68
    .org 0x4f6d4-ORIGIN
P_0004f6d4:
    .byte 0x00,0x00,0x8d,0x15
    .org 0x4f6d8-ORIGIN
P_0004f6d8:
    .byte 0x00,0x07,0xd8,0xb8
    .org 0x4f6dc-ORIGIN
P_0004f6dc:
    .byte 0xff,0xff,0x11,0x9c
    .org 0x4f6e0-ORIGIN
P_0004f6e0:
    .byte 0x00,0x00,0x89,0x57
    .org 0x4f6e4-ORIGIN
P_0004f6e4:
    .byte 0x00,0x00,0x88,0xed
    .org 0x4f6e8-ORIGIN
P_0004f6e8:
    .byte 0xff,0xff,0x24,0x58
    .org 0x4f958-ORIGIN
L_0004f958:
    sts.l macl,@-r15
    .org 0x4f95a-ORIGIN
L_0004f95a:
    stc.l gbr,@-r15
    .org 0x4f95c-ORIGIN
L_0004f95c:
    mov.l P_0004fb70,r0
    .org 0x4f95e-ORIGIN
L_0004f95e:
    ldc r0,gbr
    .org 0x4f960-ORIGIN
L_0004f960:
    mov.l P_0004fb74,r6
    .org 0x4f962-ORIGIN
L_0004f962:
    mov.b @r6,r0
    .org 0x4f964-ORIGIN
L_0004f964:
    tst #0x80,r0
    .org 0x4f966-ORIGIN
L_0004f966:
    bf L_0004f9b0
    .org 0x4f968-ORIGIN
L_0004f968:
    mov.l P_0004fb78,r2
    .org 0x4f96a-ORIGIN
L_0004f96a:
    mov #-0x1,r6
    .org 0x4f96c-ORIGIN
L_0004f96c:
    mov.l P_0004fb7c,r7
    .org 0x4f96e-ORIGIN
L_0004f96e:
    extu.w r6,r6
    .org 0x4f970-ORIGIN
L_0004f970:
    mov.w @r2,r4
    .org 0x4f972-ORIGIN
L_0004f972:
    mov.b @(0x4,r7),r0
    .org 0x4f974-ORIGIN
L_0004f974:
    extu.w r4,r4
    .org 0x4f976-ORIGIN
L_0004f976:
    extu.b r0,r5
    .org 0x4f978-ORIGIN
L_0004f978:
    mul.l r4,r5
    .org 0x4f97a-ORIGIN
L_0004f97a:
    sts macl,r2
    .org 0x4f97c-ORIGIN
L_0004f97c:
    cmp/gt r6,r2
    .org 0x4f97e-ORIGIN
L_0004f97e:
    bt L_0004f984
    .org 0x4f980-ORIGIN
L_0004f980:
    mul.l r4,r5
    .org 0x4f982-ORIGIN
L_0004f982:
    sts macl,r6
    .org 0x4f984-ORIGIN
L_0004f984:
    mov.l P_0004fb80,r5
    .org 0x4f986-ORIGIN
L_0004f986:
    mov.w P_0004fa9c,r0
    .org 0x4f988-ORIGIN
L_0004f988:
    extu.w r6,r2
    .org 0x4f98a-ORIGIN
L_0004f98a:
    mov.w @(r0,r5),r6
    .org 0x4f98c-ORIGIN
L_0004f98c:
    extu.w r6,r6
    .org 0x4f98e-ORIGIN
L_0004f98e:
    cmp/ge r2,r6
    .org 0x4f990-ORIGIN
L_0004f990:
    bf L_0004f9b0
    .org 0x4f992-ORIGIN
L_0004f992:
    mov.l P_0004fb84,r2
    .org 0x4f994-ORIGIN
L_0004f994:
    mov #0x17,r0
    .org 0x4f996-ORIGIN
L_0004f996:
    mov.b @(r0,r2),r5
    .org 0x4f998-ORIGIN
L_0004f998:
    mov.b @(0x3,r7),r0
    .org 0x4f99a-ORIGIN
L_0004f99a:
    extu.b r5,r5
    .org 0x4f99c-ORIGIN
L_0004f99c:
    extu.b r0,r2
    .org 0x4f99e-ORIGIN
L_0004f99e:
    cmp/ge r2,r5
    .org 0x4f9a0-ORIGIN
L_0004f9a0:
    bf L_0004f9b0
    .org 0x4f9a2-ORIGIN
L_0004f9a2:
    mov.b @r7,r2
    .org 0x4f9a4-ORIGIN
L_0004f9a4:
    extu.b r2,r2
    .org 0x4f9a6-ORIGIN
L_0004f9a6:
    cmp/ge r2,r5
    .org 0x4f9a8-ORIGIN
L_0004f9a8:
    bf L_0004f9b4
    .org 0x4f9aa-ORIGIN
L_0004f9aa:
    mov #0xc,r0
    .org 0x4f9ac-ORIGIN
L_0004f9ac:
    bra L_0004f9b4
    .org 0x4f9ae-ORIGIN
L_0004f9ae:
    or.b #0x80,@(r0,gbr)
    .org 0x4f9b0-ORIGIN
L_0004f9b0:
    mov #0xc,r0
    .org 0x4f9b2-ORIGIN
L_0004f9b2:
    and.b #0x7f,@(r0,gbr)
    .org 0x4f9b4-ORIGIN
L_0004f9b4:
    mov.b @(0xc,gbr),r0
    .org 0x4f9b6-ORIGIN
L_0004f9b6:
    tst #0x80,r0
    .org 0x4f9b8-ORIGIN
L_0004f9b8:
    movt r0
    .org 0x4f9ba-ORIGIN
L_0004f9ba:
    xor #0x1,r0
    .org 0x4f9bc-ORIGIN
L_0004f9bc:
    extu.b r0,r0
    .org 0x4f9be-ORIGIN
L_0004f9be:
    ldc.l @r15+,gbr
    .org 0x4f9c0-ORIGIN
L_0004f9c0:
    rts
    .org 0x4f9c2-ORIGIN
L_0004f9c2:
    lds.l @r15+,macl
    .org 0x4fa9c-ORIGIN
P_0004fa9c:
    .byte 0x06,0xa6
    .org 0x4fb70-ORIGIN
P_0004fb70:
    .byte 0xff,0xff,0x24,0x70
    .org 0x4fb74-ORIGIN
P_0004fb74:
    .byte 0x00,0x00,0x8b,0x3f
    .org 0x4fb78-ORIGIN
P_0004fb78:
    .byte 0x00,0x00,0x90,0xe0
    .org 0x4fb7c-ORIGIN
P_0004fb7c:
    .byte 0x00,0x00,0x84,0xda
    .org 0x4fb80-ORIGIN
P_0004fb80:
    .byte 0xff,0xff,0x12,0x8c
    .org 0x4fb84-ORIGIN
P_0004fb84:
    .byte 0xff,0xff,0x11,0x9c
    .org 0x50a60-ORIGIN
L_00050a60:
    stc.l gbr,@-r15
    .org 0x50a62-ORIGIN
L_00050a62:
    mov.l P_00050b24,r0
    .org 0x50a64-ORIGIN
L_00050a64:
    ldc r0,gbr
    .org 0x50a66-ORIGIN
L_00050a66:
    mov.b @(0x2c,gbr),r0
    .org 0x50a68-ORIGIN
L_00050a68:
    mov.l P_00050b28,r6
    .org 0x50a6a-ORIGIN
L_00050a6a:
    mov r0,r1
    .org 0x50a6c-ORIGIN
L_00050a6c:
    mov.b @r6,r0
    .org 0x50a6e-ORIGIN
L_00050a6e:
    tst #0x80,r0
    .org 0x50a70-ORIGIN
L_00050a70:
    bf L_00050af2
    .org 0x50a72-ORIGIN
L_00050a72:
    mov.l P_00050b2c,r7
    .org 0x50a74-ORIGIN
L_00050a74:
    mov #-0x66,r0
    .org 0x50a76-ORIGIN
L_00050a76:
    extu.b r0,r0
    .org 0x50a78-ORIGIN
L_00050a78:
    mov.b @(r0,r7),r4
    .org 0x50a7a-ORIGIN
L_00050a7a:
    mov #-0x1,r2
    .org 0x50a7c-ORIGIN
L_00050a7c:
    mov.b @(0x18,gbr),r0
    .org 0x50a7e-ORIGIN
L_00050a7e:
    extu.b r2,r2
    .org 0x50a80-ORIGIN
L_00050a80:
    extu.b r4,r4
    .org 0x50a82-ORIGIN
L_00050a82:
    cmp/eq r2,r4
    .org 0x50a84-ORIGIN
L_00050a84:
    bt/s L_00050abe
    .org 0x50a86-ORIGIN
L_00050a86:
    mov r0,r5
    .org 0x50a88-ORIGIN
L_00050a88:
    mov.l P_00050b30,r6
    .org 0x50a8a-ORIGIN
L_00050a8a:
    mov.b @(0x1,r6),r0
    .org 0x50a8c-ORIGIN
L_00050a8c:
    tst #0x2,r0
    .org 0x50a8e-ORIGIN
L_00050a8e:
    bf L_00050abe
    .org 0x50a90-ORIGIN
L_00050a90:
    mov.l P_00050b34,r6
    .org 0x50a92-ORIGIN
L_00050a92:
    mov.b @(0x4,r6),r0
    .org 0x50a94-ORIGIN
L_00050a94:
    tst #0x80,r0
    .org 0x50a96-ORIGIN
L_00050a96:
    bf L_00050abe
    .org 0x50a98-ORIGIN
L_00050a98:
    mov #-0x66,r0
    .org 0x50a9a-ORIGIN
L_00050a9a:
    extu.b r0,r0
    .org 0x50a9c-ORIGIN
L_00050a9c:
    mov.b @(r0,r7),r4
    .org 0x50a9e-ORIGIN
L_00050a9e:
    tst r4,r4
    .org 0x50aa0-ORIGIN
L_00050aa0:
    bt L_00050abe
    .org 0x50aa2-ORIGIN
L_00050aa2:
    mov r5,r0
    .org 0x50aa4-ORIGIN
L_00050aa4:
    or #0x20,r0
    .org 0x50aa6-ORIGIN
L_00050aa6:
    mov.b r0,@(0x18,gbr)
    .org 0x50aa8-ORIGIN
L_00050aa8:
    mov #-0x66,r0
    .org 0x50aaa-ORIGIN
L_00050aaa:
    extu.b r0,r0
    .org 0x50aac-ORIGIN
L_00050aac:
    mov.b @(r0,r7),r4
    .org 0x50aae-ORIGIN
L_00050aae:
    mov.l P_00050b38,r7
    .org 0x50ab0-ORIGIN
L_00050ab0:
    extu.b r4,r4
    .org 0x50ab2-ORIGIN
L_00050ab2:
    mov.b @(0x1,r7),r0
    .org 0x50ab4-ORIGIN
L_00050ab4:
    extu.b r0,r2
    .org 0x50ab6-ORIGIN
L_00050ab6:
    cmp/ge r2,r4
    .org 0x50ab8-ORIGIN
L_00050ab8:
    bf L_00050ac6
    .org 0x50aba-ORIGIN
L_00050aba:
    bra L_00050ac6
    .org 0x50abc-ORIGIN
L_00050abc:
    mov r4,r2
    .org 0x50abe-ORIGIN
L_00050abe:
    mov r5,r0
    .org 0x50ac0-ORIGIN
L_00050ac0:
    and #0xdf,r0
    .org 0x50ac2-ORIGIN
L_00050ac2:
    mov.b r0,@(0x18,gbr)
    .org 0x50ac4-ORIGIN
L_00050ac4:
    mov #-0x1,r2
    .org 0x50ac6-ORIGIN
L_00050ac6:
    mov.l P_00050b20,r6
    .org 0x50ac8-ORIGIN
L_00050ac8:
    mov.w P_00050b06,r0
    .org 0x50aca-ORIGIN
L_00050aca:
    mov.b r2,@(r0,r6)
    .org 0x50acc-ORIGIN
L_00050acc:
    mov #0x12,r0
    .org 0x50ace-ORIGIN
L_00050ace:
    mov.l P_00050b14,r6
    .org 0x50ad0-ORIGIN
L_00050ad0:
    mov.b @(r0,r6),r5
    .org 0x50ad2-ORIGIN
L_00050ad2:
    mov r1,r0
    .org 0x50ad4-ORIGIN
L_00050ad4:
    tst #0x80,r0
    .org 0x50ad6-ORIGIN
L_00050ad6:
    bt/s L_00050ae2
    .org 0x50ad8-ORIGIN
L_00050ad8:
    extu.b r5,r5
    .org 0x50ada-ORIGIN
L_00050ada:
    mov.l P_00050b38,r7
    .org 0x50adc-ORIGIN
L_00050adc:
    mov.b @r7,r6
    .org 0x50ade-ORIGIN
L_00050ade:
    extu.b r6,r6
    .org 0x50ae0-ORIGIN
L_00050ae0:
    add r6,r5
    .org 0x50ae2-ORIGIN
L_00050ae2:
    extu.b r2,r2
    .org 0x50ae4-ORIGIN
L_00050ae4:
    cmp/hi r2,r5
    .org 0x50ae6-ORIGIN
L_00050ae6:
    bt/s L_00050aee
    .org 0x50ae8-ORIGIN
L_00050ae8:
    mov #0x2c,r0
    .org 0x50aea-ORIGIN
L_00050aea:
    bra L_00050af8
    .org 0x50aec-ORIGIN
L_00050aec:
    and.b #0x7f,@(r0,gbr)
    .org 0x50aee-ORIGIN
L_00050aee:
    bra L_00050af8
    .org 0x50af0-ORIGIN
L_00050af0:
    or.b #0x80,@(r0,gbr)
    .org 0x50af2-ORIGIN
L_00050af2:
    mov r1,r0
    .org 0x50af4-ORIGIN
L_00050af4:
    and #0x7f,r0
    .org 0x50af6-ORIGIN
L_00050af6:
    mov.b r0,@(0x2c,gbr)
    .org 0x50af8-ORIGIN
L_00050af8:
    mov.b @(0x2c,gbr),r0
    .org 0x50afa-ORIGIN
L_00050afa:
    tst #0x80,r0
    .org 0x50afc-ORIGIN
L_00050afc:
    movt r0
    .org 0x50afe-ORIGIN
L_00050afe:
    xor #0x1,r0
    .org 0x50b00-ORIGIN
L_00050b00:
    extu.b r0,r0
    .org 0x50b02-ORIGIN
L_00050b02:
    rts
    .org 0x50b04-ORIGIN
L_00050b04:
    ldc.l @r15+,gbr
    .org 0x50b06-ORIGIN
P_00050b06:
    .byte 0x08,0xfe
    .org 0x50b14-ORIGIN
P_00050b14:
    .byte 0xff,0xff,0x11,0x9c
    .org 0x50b20-ORIGIN
P_00050b20:
    .byte 0xff,0xff,0x28,0xf8
    .org 0x50b24-ORIGIN
P_00050b24:
    .byte 0xff,0xff,0x24,0x70
    .org 0x50b28-ORIGIN
P_00050b28:
    .byte 0x00,0x00,0x8b,0x3f
    .org 0x50b2c-ORIGIN
P_00050b2c:
    .byte 0xff,0xff,0x26,0x7a
    .org 0x50b30-ORIGIN
P_00050b30:
    .byte 0xff,0xff,0x41,0x88
    .org 0x50b34-ORIGIN
P_00050b34:
    .byte 0xff,0xff,0x42,0x4c
    .org 0x50b38-ORIGIN
P_00050b38:
    .byte 0x00,0x00,0x89,0xfc
