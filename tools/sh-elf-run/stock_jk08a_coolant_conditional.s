! Complete natural entry and actual callees at their exact stock addresses.
    .text
    .balign 4
    .org 0x86eb - 0x86e8
L_000086eb:
    .byte 0x03
    .org 0x87a5 - 0x86e8
L_000087a5:
    .byte 0x90,0x96,0x96
    .org 0x9090 - 0x86e8
L_00009090:
    .byte 0x00,0x05
    .org 0x929a - 0x86e8
L_0000929a:
    .byte 0x1e,0x77
    .org 0x990a - 0x86e8
L_0000990a:
    .byte 0x00,0x00,0x00,0x80,0x00,0x00,0x00,0x80,0x00,0x00,0x80,0x80,0x00,0x80,0x80,0x80
    .org 0x11b17 - 0x86e8
L_00011b17:
    .byte 0x18,0x48,0x50,0x68
    .org 0x11b1b - 0x86e8
L_00011b1b:
    .byte 0x40,0x46,0x52,0x66
    .org 0x12422 - 0x86e8
L_00012422:
    .byte 0x00,0x00,0x00,0x04,0x07,0x0a,0x0d,0x10
    .org 0x22590 - 0x86e8
L_00022590:
    cmp/pl r4
    .org 0x22592 - 0x86e8
L_00022592:
    bt L_00022596
    .org 0x22594 - 0x86e8
L_00022594:
    neg r4,r4
    .org 0x22596 - 0x86e8
L_00022596:
    rts
    .org 0x22598 - 0x86e8
L_00022598:
    mov r4,r0
    .org 0x26370 - 0x86e8
L_00026370:
    mov.w L_00026382,r0
    .org 0x26372 - 0x86e8
L_00026372:
    extu.b r5,r5
    .org 0x26374 - 0x86e8
L_00026374:
    cmp/hs r0,r5
    .org 0x26376 - 0x86e8
L_00026376:
    bt L_0002637e
    .org 0x26378 - 0x86e8
L_00026378:
    mov.l L_00026384,r6
    .org 0x2637a - 0x86e8
L_0002637a:
    jmp @r6
    .org 0x2637c - 0x86e8
L_0002637c:
    mov #0x0,r3
    .org 0x2637e - 0x86e8
L_0002637e:
    rts
    .org 0x26380 - 0x86e8
L_00026380:
    mov.b @(0x7,r4),r0
    .org 0x26382 - 0x86e8
L_00026382:
    .word 0x00e0
    .org 0x26384 - 0x86e8
L_00026384:
    .long 0x00026a80
    .org 0x26740 - 0x86e8
L_00026740:
    cmp/hs r0,r2
    .org 0x26742 - 0x86e8
L_00026742:
    bt L_0002675c
    .org 0x26744 - 0x86e8
L_00026744:
    mov.l r0,@-r15
    .org 0x26746 - 0x86e8
L_00026746:
    sub r2,r0
    .org 0x26748 - 0x86e8
L_00026748:
    sts macl,r1
    .org 0x2674a - 0x86e8
L_0002674a:
    mul.l r3,r0
    .org 0x2674c - 0x86e8
L_0002674c:
    sts macl,r0
    .org 0x2674e - 0x86e8
L_0002674e:
    lds r1,macl
    .org 0x26750 - 0x86e8
L_00026750:
    swap.w r0,r0
    .org 0x26752 - 0x86e8
L_00026752:
    mov.l @r15+,r2
    .org 0x26754 - 0x86e8
L_00026754:
    extu.w r0,r0
    .org 0x26756 - 0x86e8
L_00026756:
    sub r0,r2
    .org 0x26758 - 0x86e8
L_00026758:
    rts
    .org 0x2675a - 0x86e8
L_0002675a:
    mov r2,r0
    .org 0x2675c - 0x86e8
L_0002675c:
    sub r0,r2
    .org 0x2675e - 0x86e8
L_0002675e:
    sts macl,r1
    .org 0x26760 - 0x86e8
L_00026760:
    mul.l r3,r2
    .org 0x26762 - 0x86e8
L_00026762:
    sts macl,r2
    .org 0x26764 - 0x86e8
L_00026764:
    lds r1,macl
    .org 0x26766 - 0x86e8
L_00026766:
    swap.w r2,r2
    .org 0x26768 - 0x86e8
L_00026768:
    extu.w r2,r2
    .org 0x2676a - 0x86e8
L_0002676a:
    rts
    .org 0x2676c - 0x86e8
L_0002676c:
    add r2,r0
    .org 0x26a80 - 0x86e8
L_00026a80:
    shlr r5
    .org 0x26a82 - 0x86e8
L_00026a82:
    rotcr r3
    .org 0x26a84 - 0x86e8
L_00026a84:
    shlr r5
    .org 0x26a86 - 0x86e8
L_00026a86:
    rotcr r3
    .org 0x26a88 - 0x86e8
L_00026a88:
    shlr r5
    .org 0x26a8a - 0x86e8
L_00026a8a:
    rotcr r3
    .org 0x26a8c - 0x86e8
L_00026a8c:
    shlr r5
    .org 0x26a8e - 0x86e8
L_00026a8e:
    rotcr r3
    .org 0x26a90 - 0x86e8
L_00026a90:
    shlr r5
    .org 0x26a92 - 0x86e8
L_00026a92:
    rotcr r3
    .org 0x26a94 - 0x86e8
L_00026a94:
    swap.w r3,r3
    .org 0x26a96 - 0x86e8
L_00026a96:
    shlr8 r0
    .org 0x26a98 - 0x86e8
L_00026a98:
    tst r0,r0
    .org 0x26a9a - 0x86e8
L_00026a9a:
    bt L_00026aaa
    .org 0x26a9c - 0x86e8
L_00026a9c:
    shll r5
    .org 0x26a9e - 0x86e8
L_00026a9e:
    add r5,r4
    .org 0x26aa0 - 0x86e8
L_00026aa0:
    mov.w @r4,r1
    .org 0x26aa2 - 0x86e8
L_00026aa2:
    mov.w @(0x2,r4),r0
    .org 0x26aa4 - 0x86e8
L_00026aa4:
    extu.w r0,r2
    .org 0x26aa6 - 0x86e8
L_00026aa6:
    bra L_00026ab4
    .org 0x26aa8 - 0x86e8
L_00026aa8:
    extu.w r1,r0
    .org 0x26aaa - 0x86e8
L_00026aaa:
    add r5,r4
    .org 0x26aac - 0x86e8
L_00026aac:
    mov.b @r4,r1
    .org 0x26aae - 0x86e8
L_00026aae:
    mov.b @(0x1,r4),r0
    .org 0x26ab0 - 0x86e8
L_00026ab0:
    extu.b r0,r2
    .org 0x26ab2 - 0x86e8
L_00026ab2:
    extu.b r1,r0
    .org 0x26ab4 - 0x86e8
L_00026ab4:
    mov.l L_00026abc,r6
    .org 0x26ab6 - 0x86e8
L_00026ab6:
    jmp @r6
    .org 0x26ab8 - 0x86e8
L_00026ab8:
    nop
    .org 0x26abc - 0x86e8
L_00026abc:
    .long 0x00026740
    .org 0x5525a - 0x86e8
L_0005525a:
    mov.l r10,@-r15
    .org 0x5525c - 0x86e8
L_0005525c:
    mov.l r11,@-r15
    .org 0x5525e - 0x86e8
L_0005525e:
    mov.l r12,@-r15
    .org 0x55260 - 0x86e8
L_00055260:
    mov.l r13,@-r15
    .org 0x55262 - 0x86e8
L_00055262:
    mov.l r14,@-r15
    .org 0x55264 - 0x86e8
L_00055264:
    sts.l pr,@-r15
    .org 0x55266 - 0x86e8
L_00055266:
    sts.l macl,@-r15
    .org 0x55268 - 0x86e8
L_00055268:
    stc.l gbr,@-r15
    .org 0x5526a - 0x86e8
L_0005526a:
    mov.l L_00055370,r0
    .org 0x5526c - 0x86e8
L_0005526c:
    ldc r0,gbr
    .org 0x5526e - 0x86e8
L_0005526e:
    add #-0x14,r15
    .org 0x55270 - 0x86e8
L_00055270:
    mov.l L_00055350,r10
    .org 0x55272 - 0x86e8
L_00055272:
    mov #0x17,r0
    .org 0x55274 - 0x86e8
L_00055274:
    mov.b @(r0,r10),r13
    .org 0x55276 - 0x86e8
L_00055276:
    mov.b @(0x3a,gbr),r0
    .org 0x55278 - 0x86e8
L_00055278:
    tst #0x8,r0
    .org 0x5527a - 0x86e8
L_0005527a:
    bt/s L_00055280
    .org 0x5527c - 0x86e8
L_0005527c:
    extu.b r13,r13
    .org 0x5527e - 0x86e8
L_0005527e:
    add #0x2,r13
    .org 0x55280 - 0x86e8
L_00055280:
    mov.l L_00055374,r11
    .org 0x55282 - 0x86e8
L_00055282:
    mov.b @r11,r2
    .org 0x55284 - 0x86e8
L_00055284:
    extu.b r2,r2
    .org 0x55286 - 0x86e8
L_00055286:
    cmp/hs r2,r13
    .org 0x55288 - 0x86e8
L_00055288:
    bt/s L_00055290
    .org 0x5528a - 0x86e8
L_0005528a:
    mov #0x3a,r0
    .org 0x5528c - 0x86e8
L_0005528c:
    bra L_00055292
    .org 0x5528e - 0x86e8
L_0005528e:
    and.b #0xf7,@(r0,gbr)
    .org 0x55290 - 0x86e8
L_00055290:
    or.b #0x8,@(r0,gbr)
    .org 0x55292 - 0x86e8
L_00055292:
    mov.l L_00055378,r4
    .org 0x55294 - 0x86e8
L_00055294:
    mov #0x73,r0
    .org 0x55296 - 0x86e8
L_00055296:
    mov.b @(r0,r4),r6
    .org 0x55298 - 0x86e8
L_00055298:
    mov.b @(0x3a,gbr),r0
    .org 0x5529a - 0x86e8
L_0005529a:
    mov r0,r12
    .org 0x5529c - 0x86e8
L_0005529c:
    mov.b @(0x3b,gbr),r0
    .org 0x5529e - 0x86e8
L_0005529e:
    tst #0x80,r0
    .org 0x552a0 - 0x86e8
L_000552a0:
    bt/s L_000552ac
    .org 0x552a2 - 0x86e8
L_000552a2:
    extu.b r6,r13
    .org 0x552a4 - 0x86e8
L_000552a4:
    mov.l L_0005537c,r5
    .org 0x552a6 - 0x86e8
L_000552a6:
    mov.b @r5,r2
    .org 0x552a8 - 0x86e8
L_000552a8:
    extu.b r2,r2
    .org 0x552aa - 0x86e8
L_000552aa:
    add r2,r13
    .org 0x552ac - 0x86e8
L_000552ac:
    mov.b @(0x2,r11),r0
    .org 0x552ae - 0x86e8
L_000552ae:
    extu.b r0,r2
    .org 0x552b0 - 0x86e8
L_000552b0:
    cmp/hi r2,r13
    .org 0x552b2 - 0x86e8
L_000552b2:
    bt/s L_000552ba
    .org 0x552b4 - 0x86e8
L_000552b4:
    mov #0x3b,r0
    .org 0x552b6 - 0x86e8
L_000552b6:
    bra L_000552bc
    .org 0x552b8 - 0x86e8
L_000552b8:
    and.b #0x7f,@(r0,gbr)
    .org 0x552ba - 0x86e8
L_000552ba:
    or.b #0x80,@(r0,gbr)
    .org 0x552bc - 0x86e8
L_000552bc:
    mov.l L_00055378,r4
    .org 0x552be - 0x86e8
L_000552be:
    mov #0x73,r0
    .org 0x552c0 - 0x86e8
L_000552c0:
    mov.b @(r0,r4),r6
    .org 0x552c2 - 0x86e8
L_000552c2:
    mov r12,r0
    .org 0x552c4 - 0x86e8
L_000552c4:
    tst #0x2,r0
    .org 0x552c6 - 0x86e8
L_000552c6:
    bt/s L_000552d2
    .org 0x552c8 - 0x86e8
L_000552c8:
    extu.b r6,r6
    .org 0x552ca - 0x86e8
L_000552ca:
    mov.l L_0005537c,r5
    .org 0x552cc - 0x86e8
L_000552cc:
    mov.b @r5,r2
    .org 0x552ce - 0x86e8
L_000552ce:
    extu.b r2,r5
    .org 0x552d0 - 0x86e8
L_000552d0:
    add r5,r6
    .org 0x552d2 - 0x86e8
L_000552d2:
    mov.b @(0x1,r11),r0
    .org 0x552d4 - 0x86e8
L_000552d4:
    extu.b r0,r2
    .org 0x552d6 - 0x86e8
L_000552d6:
    cmp/hs r2,r6
    .org 0x552d8 - 0x86e8
L_000552d8:
    bt/s L_000552e0
    .org 0x552da - 0x86e8
L_000552da:
    mov #0x3a,r0
    .org 0x552dc - 0x86e8
L_000552dc:
    bra L_000552e2
    .org 0x552de - 0x86e8
L_000552de:
    and.b #0xfd,@(r0,gbr)
    .org 0x552e0 - 0x86e8
L_000552e0:
    or.b #0x2,@(r0,gbr)
    .org 0x552e2 - 0x86e8
L_000552e2:
    mov.b @(0x3a,gbr),r0
    .org 0x552e4 - 0x86e8
L_000552e4:
    tst #0x8,r0
    .org 0x552e6 - 0x86e8
L_000552e6:
    bt/s L_00055300
    .org 0x552e8 - 0x86e8
L_000552e8:
    mov r0,r13
    .org 0x552ea - 0x86e8
L_000552ea:
    mov r13,r0
    .org 0x552ec - 0x86e8
L_000552ec:
    tst #0x2,r0
    .org 0x552ee - 0x86e8
L_000552ee:
    bf L_00055306
    .org 0x552f0 - 0x86e8
L_000552f0:
    bra L_0005530c
    .org 0x552f2 - 0x86e8
L_000552f2:
    nop
    .org 0x55300 - 0x86e8
L_00055300:
    mov.b @(0x3b,gbr),r0
    .org 0x55302 - 0x86e8
L_00055302:
    tst #0x80,r0
    .org 0x55304 - 0x86e8
L_00055304:
    bt L_0005530c
    .org 0x55306 - 0x86e8
L_00055306:
    mov r13,r0
    .org 0x55308 - 0x86e8
L_00055308:
    bra L_00055310
    .org 0x5530a - 0x86e8
L_0005530a:
    or #0x4,r0
    .org 0x5530c - 0x86e8
L_0005530c:
    mov r13,r0
    .org 0x5530e - 0x86e8
L_0005530e:
    and #0xfb,r0
    .org 0x55310 - 0x86e8
L_00055310:
    mov.b r0,@(0x3a,gbr)
    .org 0x55312 - 0x86e8
L_00055312:
    exts.b r0,r13
    .org 0x55314 - 0x86e8
L_00055314:
    mov.b @(0x0,gbr),r0
    .org 0x55316 - 0x86e8
L_00055316:
    tst #0x20,r0
    .org 0x55318 - 0x86e8
L_00055318:
    bt L_0005531e
    .org 0x5531a - 0x86e8
L_0005531a:
    bra L_00055488
    .org 0x5531c - 0x86e8
L_0005531c:
    nop
    .org 0x5531e - 0x86e8
L_0005531e:
    mov r13,r0
    .org 0x55320 - 0x86e8
L_00055320:
    tst #0x4,r0
    .org 0x55322 - 0x86e8
L_00055322:
    bf L_00055328
    .org 0x55324 - 0x86e8
L_00055324:
    bra L_00055488
    .org 0x55326 - 0x86e8
L_00055326:
    nop
    .org 0x55328 - 0x86e8
L_00055328:
    mov.l L_00055380,r2
    .org 0x5532a - 0x86e8
L_0005532a:
    mov.w L_0005533c,r5
    .org 0x5532c - 0x86e8
L_0005532c:
    mov.b @(0x7,r2),r0
    .org 0x5532e - 0x86e8
L_0005532e:
    extu.b r0,r6
    .org 0x55330 - 0x86e8
L_00055330:
    mov r6,r2
    .org 0x55332 - 0x86e8
L_00055332:
    add r5,r2
    .org 0x55334 - 0x86e8
L_00055334:
    cmp/pz r2
    .org 0x55336 - 0x86e8
L_00055336:
    bt L_00055384
    .org 0x55338 - 0x86e8
L_00055338:
    bra L_00055388
    .org 0x5533a - 0x86e8
L_0005533a:
    mov #0x0,r2
    .org 0x5533c - 0x86e8
L_0005533c:
    .word 0xff40
    .org 0x55350 - 0x86e8
L_00055350:
    .long 0xffff119c
    .org 0x55370 - 0x86e8
L_00055370:
    .long 0xffff2458
    .org 0x55374 - 0x86e8
L_00055374:
    .long 0x000087a5
    .org 0x55378 - 0x86e8
L_00055378:
    .long 0xffff1094
    .org 0x5537c - 0x86e8
L_0005537c:
    .long 0x000086eb
    .org 0x55380 - 0x86e8
L_00055380:
    .long 0xffff1068
    .org 0x55384 - 0x86e8
L_00055384:
    add r5,r6
    .org 0x55386 - 0x86e8
L_00055386:
    mov r6,r2
    .org 0x55388 - 0x86e8
L_00055388:
    extu.b r2,r5
    .org 0x5538a - 0x86e8
L_0005538a:
    mov.l L_000555c0,r4
    .org 0x5538c - 0x86e8
L_0005538c:
    shll2 r5
    .org 0x5538e - 0x86e8
L_0005538e:
    mov.l L_000555c4,r2
    .org 0x55390 - 0x86e8
L_00055390:
    mov.l L_000555c8,r12
    .org 0x55392 - 0x86e8
L_00055392:
    jsr @r2
    .org 0x55394 - 0x86e8
L_00055394:
    extu.b r5,r5
    .org 0x55396 - 0x86e8
L_00055396:
    mov r0,r6
    .org 0x55398 - 0x86e8
L_00055398:
    mov.w L_000554f0,r0
    .org 0x5539a - 0x86e8
L_0005539a:
    mov.l L_000555cc,r2
    .org 0x5539c - 0x86e8
L_0005539c:
    mov #0x1,r4
    .org 0x5539e - 0x86e8
L_0005539e:
    mov.b r6,@(r0,r12)
    .org 0x553a0 - 0x86e8
L_000553a0:
    mov #0x3,r13
    .org 0x553a2 - 0x86e8
L_000553a2:
    mov.b @r2,r7
    .org 0x553a4 - 0x86e8
L_000553a4:
    mov.l L_000555d0,r5
    .org 0x553a6 - 0x86e8
L_000553a6:
    extu.b r7,r7
    .org 0x553a8 - 0x86e8
L_000553a8:
    extu.b r4,r4
    .org 0x553aa - 0x86e8
L_000553aa:
    mov r4,r0
    .org 0x553ac - 0x86e8
L_000553ac:
    mov.b @(r0,r5),r2
    .org 0x553ae - 0x86e8
L_000553ae:
    extu.b r2,r2
    .org 0x553b0 - 0x86e8
L_000553b0:
    cmp/gt r2,r7
    .org 0x553b2 - 0x86e8
L_000553b2:
    bf L_000553bc
    .org 0x553b4 - 0x86e8
L_000553b4:
    add #0x1,r4
    .org 0x553b6 - 0x86e8
L_000553b6:
    extu.b r4,r4
    .org 0x553b8 - 0x86e8
L_000553b8:
    cmp/gt r13,r4
    .org 0x553ba - 0x86e8
L_000553ba:
    bf L_000553a8
    .org 0x553bc - 0x86e8
L_000553bc:
    mov #0x12,r0
    .org 0x553be - 0x86e8
L_000553be:
    mov.l L_000555d4,r7
    .org 0x553c0 - 0x86e8
L_000553c0:
    mov.b @(r0,r10),r2
    .org 0x553c2 - 0x86e8
L_000553c2:
    mov #0x1,r5
    .org 0x553c4 - 0x86e8
L_000553c4:
    extu.b r2,r14
    .org 0x553c6 - 0x86e8
L_000553c6:
    extu.b r5,r5
    .org 0x553c8 - 0x86e8
L_000553c8:
    mov r5,r0
    .org 0x553ca - 0x86e8
L_000553ca:
    mov.b @(r0,r7),r2
    .org 0x553cc - 0x86e8
L_000553cc:
    extu.b r2,r2
    .org 0x553ce - 0x86e8
L_000553ce:
    cmp/gt r2,r14
    .org 0x553d0 - 0x86e8
L_000553d0:
    bf L_000553da
    .org 0x553d2 - 0x86e8
L_000553d2:
    add #0x1,r5
    .org 0x553d4 - 0x86e8
L_000553d4:
    extu.b r5,r5
    .org 0x553d6 - 0x86e8
L_000553d6:
    cmp/gt r13,r5
    .org 0x553d8 - 0x86e8
L_000553d8:
    bf L_000553c6
    .org 0x553da - 0x86e8
L_000553da:
    extu.b r5,r0
    .org 0x553dc - 0x86e8
L_000553dc:
    extu.b r4,r5
    .org 0x553de - 0x86e8
L_000553de:
    mov.l L_000555d8,r4
    .org 0x553e0 - 0x86e8
L_000553e0:
    shll2 r0
    .org 0x553e2 - 0x86e8
L_000553e2:
    add #-0x5,r4
    .org 0x553e4 - 0x86e8
L_000553e4:
    add r5,r0
    .org 0x553e6 - 0x86e8
L_000553e6:
    mov.b @(r0,r4),r5
    .org 0x553e8 - 0x86e8
L_000553e8:
    extu.b r6,r6
    .org 0x553ea - 0x86e8
L_000553ea:
    mov.w L_000554f2,r0
    .org 0x553ec - 0x86e8
L_000553ec:
    mov.b r5,@(r0,r12)
    .org 0x553ee - 0x86e8
L_000553ee:
    extu.b r5,r5
    .org 0x553f0 - 0x86e8
L_000553f0:
    mul.l r5,r6
    .org 0x553f2 - 0x86e8
L_000553f2:
    mov.b @(0x3a,gbr),r0
    .org 0x553f4 - 0x86e8
L_000553f4:
    sts macl,r5
    .org 0x553f6 - 0x86e8
L_000553f6:
    tst #0x1,r0
    .org 0x553f8 - 0x86e8
L_000553f8:
    mov r0,r14
    .org 0x553fa - 0x86e8
L_000553fa:
    bt/s L_00055458
    .org 0x553fc - 0x86e8
L_000553fc:
    mov.l r5,@r15
    .org 0x553fe - 0x86e8
L_000553fe:
    mov.w L_000554f4,r0
    .org 0x55400 - 0x86e8
L_00055400:
    mov.l @r15,r6
    .org 0x55402 - 0x86e8
L_00055402:
    mov.w @(r0,r12),r5
    .org 0x55404 - 0x86e8
L_00055404:
    mov.b @(0x2d,gbr),r0
    .org 0x55406 - 0x86e8
L_00055406:
    extu.w r5,r2
    .org 0x55408 - 0x86e8
L_00055408:
    sub r2,r6
    .org 0x5540a - 0x86e8
L_0005540a:
    cmp/pz r6
    .org 0x5540c - 0x86e8
L_0005540c:
    mov.l r6,@(0x4,r15)
    .org 0x5540e - 0x86e8
L_0005540e:
    mov.l r6,@(0xc,r15)
    .org 0x55410 - 0x86e8
L_00055410:
    bf/s L_00055416
    .org 0x55412 - 0x86e8
L_00055412:
    and #0x7f,r0
    .org 0x55414 - 0x86e8
L_00055414:
    or #0x80,r0
    .org 0x55416 - 0x86e8
L_00055416:
    mov.l L_000555dc,r2
    .org 0x55418 - 0x86e8
L_00055418:
    mov.l @(0xc,r15),r4
    .org 0x5541a - 0x86e8
L_0005541a:
    jsr @r2
    .org 0x5541c - 0x86e8
L_0005541c:
    mov.b r0,@(0x2d,gbr)
    .org 0x5541e - 0x86e8
L_0005541e:
    mov.l L_000555e0,r4
    .org 0x55420 - 0x86e8
L_00055420:
    mov.l r0,@(0x8,r15)
    .org 0x55422 - 0x86e8
L_00055422:
    mov.w @r4,r6
    .org 0x55424 - 0x86e8
L_00055424:
    mov.b @(0x3a,gbr),r0
    .org 0x55426 - 0x86e8
L_00055426:
    extu.w r6,r6
    .org 0x55428 - 0x86e8
L_00055428:
    mov.l r6,@(0x10,r15)
    .org 0x5542a - 0x86e8
L_0005542a:
    mov.l @(0x8,r15),r6
    .org 0x5542c - 0x86e8
L_0005542c:
    mov.l @(0x10,r15),r2
    .org 0x5542e - 0x86e8
L_0005542e:
    cmp/gt r2,r6
    .org 0x55430 - 0x86e8
L_00055430:
    bf/s L_00055458
    .org 0x55432 - 0x86e8
L_00055432:
    mov r0,r14
    .org 0x55434 - 0x86e8
L_00055434:
    mov.b @(0x2d,gbr),r0
    .org 0x55436 - 0x86e8
L_00055436:
    tst #0x80,r0
    .org 0x55438 - 0x86e8
L_00055438:
    mov.w L_000554f4,r0
    .org 0x5543a - 0x86e8
L_0005543a:
    bt L_0005544c
    .org 0x5543c - 0x86e8
L_0005543c:
    mov.w @(r0,r12),r6
    .org 0x5543e - 0x86e8
L_0005543e:
    mov.l L_000555e0,r4
    .org 0x55440 - 0x86e8
L_00055440:
    extu.w r6,r2
    .org 0x55442 - 0x86e8
L_00055442:
    mov.w @r4,r6
    .org 0x55444 - 0x86e8
L_00055444:
    extu.w r6,r6
    .org 0x55446 - 0x86e8
L_00055446:
    add r6,r2
    .org 0x55448 - 0x86e8
L_00055448:
    bra L_00055458
    .org 0x5544a - 0x86e8
L_0005544a:
    mov.l r2,@r15
    .org 0x5544c - 0x86e8
L_0005544c:
    mov.w @(r0,r12),r2
    .org 0x5544e - 0x86e8
L_0005544e:
    mov.w @r4,r6
    .org 0x55450 - 0x86e8
L_00055450:
    extu.w r2,r5
    .org 0x55452 - 0x86e8
L_00055452:
    extu.w r6,r6
    .org 0x55454 - 0x86e8
L_00055454:
    sub r6,r5
    .org 0x55456 - 0x86e8
L_00055456:
    mov.l r5,@r15
    .org 0x55458 - 0x86e8
L_00055458:
    mov.l L_000555e4,r2
    .org 0x5545a - 0x86e8
L_0005545a:
    mov.l L_000555e8,r6
    .org 0x5545c - 0x86e8
L_0005545c:
    mov.w @r2,r4
    .org 0x5545e - 0x86e8
L_0005545e:
    mov.w @(0xc,r6),r0
    .org 0x55460 - 0x86e8
L_00055460:
    mov #0x40,r6
    .org 0x55462 - 0x86e8
L_00055462:
    extu.w r4,r4
    .org 0x55464 - 0x86e8
L_00055464:
    extu.w r0,r7
    .org 0x55466 - 0x86e8
L_00055466:
    mov r4,r2
    .org 0x55468 - 0x86e8
L_00055468:
    sub r7,r2
    .org 0x5546a - 0x86e8
L_0005546a:
    shll8 r6
    .org 0x5546c - 0x86e8
L_0005546c:
    add r6,r2
    .org 0x5546e - 0x86e8
L_0005546e:
    cmp/pz r2
    .org 0x55470 - 0x86e8
L_00055470:
    bt L_00055476
    .org 0x55472 - 0x86e8
L_00055472:
    bra L_0005547a
    .org 0x55474 - 0x86e8
L_00055474:
    mov #0x0,r4
    .org 0x55476 - 0x86e8
L_00055476:
    sub r7,r4
    .org 0x55478 - 0x86e8
L_00055478:
    add r6,r4
    .org 0x5547a - 0x86e8
L_0005547a:
    mov.l @r15,r5
    .org 0x5547c - 0x86e8
L_0005547c:
    cmp/hi r4,r5
    .org 0x5547e - 0x86e8
L_0005547e:
    bf L_00055482
    .org 0x55480 - 0x86e8
L_00055480:
    mov.l r4,@r15
    .org 0x55482 - 0x86e8
L_00055482:
    mov r14,r0
    .org 0x55484 - 0x86e8
L_00055484:
    bra L_00055490
    .org 0x55486 - 0x86e8
L_00055486:
    or #0x1,r0
    .org 0x55488 - 0x86e8
L_00055488:
    mov #0x0,r5
    .org 0x5548a - 0x86e8
L_0005548a:
    mov r13,r0
    .org 0x5548c - 0x86e8
L_0005548c:
    mov.l r5,@r15
    .org 0x5548e - 0x86e8
L_0005548e:
    and #0xfe,r0
    .org 0x55490 - 0x86e8
L_00055490:
    mov.b r0,@(0x3a,gbr)
    .org 0x55492 - 0x86e8
L_00055492:
    mov.l @r15,r5
    .org 0x55494 - 0x86e8
L_00055494:
    mov.l L_000555c8,r12
    .org 0x55496 - 0x86e8
L_00055496:
    mov.w L_000554f4,r0
    .org 0x55498 - 0x86e8
L_00055498:
    mov.w r5,@(r0,r12)
    .org 0x5549a - 0x86e8
L_0005549a:
    add #0x14,r15
    .org 0x5549c - 0x86e8
L_0005549c:
    ldc.l @r15+,gbr
    .org 0x5549e - 0x86e8
L_0005549e:
    lds.l @r15+,macl
    .org 0x554a0 - 0x86e8
L_000554a0:
    lds.l @r15+,pr
    .org 0x554a2 - 0x86e8
L_000554a2:
    mov.l @r15+,r14
    .org 0x554a4 - 0x86e8
L_000554a4:
    mov.l @r15+,r13
    .org 0x554a6 - 0x86e8
L_000554a6:
    mov.l @r15+,r12
    .org 0x554a8 - 0x86e8
L_000554a8:
    mov.l @r15+,r11
    .org 0x554aa - 0x86e8
L_000554aa:
    rts
    .org 0x554ac - 0x86e8
L_000554ac:
    mov.l @r15+,r10
    .org 0x554f0 - 0x86e8
L_000554f0:
    .word 0x0351
    .org 0x554f2 - 0x86e8
L_000554f2:
    .word 0x0350
    .org 0x554f4 - 0x86e8
L_000554f4:
    .word 0x034e
    .org 0x555c0 - 0x86e8
L_000555c0:
    .long 0x00012422
    .org 0x555c4 - 0x86e8
L_000555c4:
    .long 0x00026370
    .org 0x555c8 - 0x86e8
L_000555c8:
    .long 0xffff128c
    .org 0x555cc - 0x86e8
L_000555cc:
    .long 0xffff102c
    .org 0x555d0 - 0x86e8
L_000555d0:
    .long 0x00011b1b
    .org 0x555d4 - 0x86e8
L_000555d4:
    .long 0x00011b17
    .org 0x555d8 - 0x86e8
L_000555d8:
    .long 0x0000990a
    .org 0x555dc - 0x86e8
L_000555dc:
    .long 0x00022590
    .org 0x555e0 - 0x86e8
L_000555e0:
    .long 0x00009090
    .org 0x555e4 - 0x86e8
L_000555e4:
    .long 0x0000929a
    .org 0x555e8 - 0x86e8
L_000555e8:
    .long 0xffff22dc
