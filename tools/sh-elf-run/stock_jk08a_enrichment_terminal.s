! Exact staged mixture terminal, its real auxiliary producer and implicit byte lookup.
    .text
    .balign 4
    .org 0x849b - 0x8498
L_0000849b:
    .byte 0x26,0x30
    .org 0x86ea - 0x8498
L_000086ea:
    .byte 0x00
    .org 0x86f3 - 0x8498
L_000086f3:
    .byte 0x00
    .org 0x87d6 - 0x8498
L_000087d6:
    .byte 0x02
    .org 0x87d9 - 0x8498
L_000087d9:
    .byte 0x00
    .org 0x8b9b - 0x8498
L_00008b9b:
    .byte 0x82,0x82
    .org 0x8b9f - 0x8498
L_00008b9f:
    .byte 0x81
    .org 0x8bef - 0x8498
L_00008bef:
    .byte 0xfe
    .org 0x8f86 - 0x8498
L_00008f86:
    .byte 0x40,0x00
    .org 0x929c - 0x8498
L_0000929c:
    .byte 0x40,0x00
    .org 0x94ec - 0x8498
L_000094ec:
    .byte 0xff,0xff
    .org 0x11ede - 0x8498
L_00011ede:
    .byte 0xfe,0xfe,0xfe,0xfe,0xfe,0xfe,0xfe,0xfe
    .org 0x26370 - 0x8498
L_00026370:
    mov.w L_00026382,r0
    .org 0x26372 - 0x8498
L_00026372:
    extu.b r5,r5
    .org 0x26374 - 0x8498
L_00026374:
    cmp/hs r0,r5
    .org 0x26376 - 0x8498
L_00026376:
    bt L_0002637e
    .org 0x26378 - 0x8498
L_00026378:
    mov.l L_00026384,r6
    .org 0x2637a - 0x8498
L_0002637a:
    jmp @r6
    .org 0x2637c - 0x8498
L_0002637c:
    mov #0x0,r3
    .org 0x2637e - 0x8498
L_0002637e:
    rts
    .org 0x26380 - 0x8498
L_00026380:
    mov.b @(0x7,r4),r0
    .org 0x26382 - 0x8498
L_00026382:
    .word 0x00e0
    .org 0x26384 - 0x8498
L_00026384:
    .long 0x00026a80
    .org 0x26740 - 0x8498
L_00026740:
    cmp/hs r0,r2
    .org 0x26742 - 0x8498
L_00026742:
    bt L_0002675c
    .org 0x26744 - 0x8498
L_00026744:
    mov.l r0,@-r15
    .org 0x26746 - 0x8498
L_00026746:
    sub r2,r0
    .org 0x26748 - 0x8498
L_00026748:
    sts macl,r1
    .org 0x2674a - 0x8498
L_0002674a:
    mul.l r3,r0
    .org 0x2674c - 0x8498
L_0002674c:
    sts macl,r0
    .org 0x2674e - 0x8498
L_0002674e:
    lds r1,macl
    .org 0x26750 - 0x8498
L_00026750:
    swap.w r0,r0
    .org 0x26752 - 0x8498
L_00026752:
    mov.l @r15+,r2
    .org 0x26754 - 0x8498
L_00026754:
    extu.w r0,r0
    .org 0x26756 - 0x8498
L_00026756:
    sub r0,r2
    .org 0x26758 - 0x8498
L_00026758:
    rts
    .org 0x2675a - 0x8498
L_0002675a:
    mov r2,r0
    .org 0x2675c - 0x8498
L_0002675c:
    sub r0,r2
    .org 0x2675e - 0x8498
L_0002675e:
    sts macl,r1
    .org 0x26760 - 0x8498
L_00026760:
    mul.l r3,r2
    .org 0x26762 - 0x8498
L_00026762:
    sts macl,r2
    .org 0x26764 - 0x8498
L_00026764:
    lds r1,macl
    .org 0x26766 - 0x8498
L_00026766:
    swap.w r2,r2
    .org 0x26768 - 0x8498
L_00026768:
    extu.w r2,r2
    .org 0x2676a - 0x8498
L_0002676a:
    rts
    .org 0x2676c - 0x8498
L_0002676c:
    add r2,r0
    .org 0x26a80 - 0x8498
L_00026a80:
    shlr r5
    .org 0x26a82 - 0x8498
L_00026a82:
    rotcr r3
    .org 0x26a84 - 0x8498
L_00026a84:
    shlr r5
    .org 0x26a86 - 0x8498
L_00026a86:
    rotcr r3
    .org 0x26a88 - 0x8498
L_00026a88:
    shlr r5
    .org 0x26a8a - 0x8498
L_00026a8a:
    rotcr r3
    .org 0x26a8c - 0x8498
L_00026a8c:
    shlr r5
    .org 0x26a8e - 0x8498
L_00026a8e:
    rotcr r3
    .org 0x26a90 - 0x8498
L_00026a90:
    shlr r5
    .org 0x26a92 - 0x8498
L_00026a92:
    rotcr r3
    .org 0x26a94 - 0x8498
L_00026a94:
    swap.w r3,r3
    .org 0x26a96 - 0x8498
L_00026a96:
    shlr8 r0
    .org 0x26a98 - 0x8498
L_00026a98:
    tst r0,r0
    .org 0x26a9a - 0x8498
L_00026a9a:
    bt L_00026aaa
    .org 0x26a9c - 0x8498
L_00026a9c:
    shll r5
    .org 0x26a9e - 0x8498
L_00026a9e:
    add r5,r4
    .org 0x26aa0 - 0x8498
L_00026aa0:
    mov.w @r4,r1
    .org 0x26aa2 - 0x8498
L_00026aa2:
    mov.w @(0x2,r4),r0
    .org 0x26aa4 - 0x8498
L_00026aa4:
    extu.w r0,r2
    .org 0x26aa6 - 0x8498
L_00026aa6:
    bra L_00026ab4
    .org 0x26aa8 - 0x8498
L_00026aa8:
    extu.w r1,r0
    .org 0x26aaa - 0x8498
L_00026aaa:
    add r5,r4
    .org 0x26aac - 0x8498
L_00026aac:
    mov.b @r4,r1
    .org 0x26aae - 0x8498
L_00026aae:
    mov.b @(0x1,r4),r0
    .org 0x26ab0 - 0x8498
L_00026ab0:
    extu.b r0,r2
    .org 0x26ab2 - 0x8498
L_00026ab2:
    extu.b r1,r0
    .org 0x26ab4 - 0x8498
L_00026ab4:
    mov.l L_00026abc,r6
    .org 0x26ab6 - 0x8498
L_00026ab6:
    jmp @r6
    .org 0x26ab8 - 0x8498
L_00026ab8:
    nop
    .org 0x26abc - 0x8498
L_00026abc:
    .long 0x00026740
    .org 0x562e2 - 0x8498
L_000562e2:
    mov.l L_000563e4,r6
    .org 0x562e4 - 0x8498
L_000562e4:
    mov #0x21,r0
    .org 0x562e6 - 0x8498
L_000562e6:
    mov.l L_000563f0,r2
    .org 0x562e8 - 0x8498
L_000562e8:
    mov.b @(r0,r6),r13
    .org 0x562ea - 0x8498
L_000562ea:
    mov.w L_00056316,r6
    .org 0x562ec - 0x8498
L_000562ec:
    mov.b @r6,r0
    .org 0x562ee - 0x8498
L_000562ee:
    tst #0x80,r0
    .org 0x562f0 - 0x8498
L_000562f0:
    mov #0x2c,r0
    .org 0x562f2 - 0x8498
L_000562f2:
    bt/s L_0005636a
    .org 0x562f4 - 0x8498
L_000562f4:
    mov.w @(r0,r2),r4
    .org 0x562f6 - 0x8498
L_000562f6:
    mov.l L_000563f4,r2
    .org 0x562f8 - 0x8498
L_000562f8:
    extu.w r4,r4
    .org 0x562fa - 0x8498
L_000562fa:
    mov #0x40,r12
    .org 0x562fc - 0x8498
L_000562fc:
    mov r4,r6
    .org 0x562fe - 0x8498
L_000562fe:
    mov.b @r2,r5
    .org 0x56300 - 0x8498
L_00056300:
    shll8 r12
    .org 0x56302 - 0x8498
L_00056302:
    extu.b r5,r5
    .org 0x56304 - 0x8498
L_00056304:
    mov r5,r2
    .org 0x56306 - 0x8498
L_00056306:
    shll2 r2
    .org 0x56308 - 0x8498
L_00056308:
    shll r2
    .org 0x5630a - 0x8498
L_0005630a:
    sub r2,r6
    .org 0x5630c - 0x8498
L_0005630c:
    cmp/ge r12,r6
    .org 0x5630e - 0x8498
L_0005630e:
    bt L_00056320
    .org 0x56310 - 0x8498
L_00056310:
    bra L_00056328
    .org 0x56312 - 0x8498
L_00056312:
    mov r12,r2
    .org 0x56316 - 0x8498
L_00056316:
    .word 0x84c3
    .org 0x56320 - 0x8498
L_00056320:
    shll2 r5
    .org 0x56322 - 0x8498
L_00056322:
    mov r4,r2
    .org 0x56324 - 0x8498
L_00056324:
    shll r5
    .org 0x56326 - 0x8498
L_00056326:
    sub r5,r2
    .org 0x56328 - 0x8498
L_00056328:
    mov.l L_000563e0,r11
    .org 0x5632a - 0x8498
L_0005632a:
    mov r2,r14
    .org 0x5632c - 0x8498
L_0005632c:
    mov.w L_000563dc,r0
    .org 0x5632e - 0x8498
L_0005632e:
    mov r4,r5
    .org 0x56330 - 0x8498
L_00056330:
    mov.l L_000563f8,r2
    .org 0x56332 - 0x8498
L_00056332:
    mov.b @(r0,r11),r7
    .org 0x56334 - 0x8498
L_00056334:
    mov.b @r2,r12
    .org 0x56336 - 0x8498
L_00056336:
    extu.b r7,r7
    .org 0x56338 - 0x8498
L_00056338:
    extu.b r12,r12
    .org 0x5633a - 0x8498
L_0005633a:
    mov r7,r6
    .org 0x5633c - 0x8498
L_0005633c:
    shll2 r6
    .org 0x5633e - 0x8498
L_0005633e:
    mov r12,r2
    .org 0x56340 - 0x8498
L_00056340:
    shll2 r2
    .org 0x56342 - 0x8498
L_00056342:
    shll2 r6
    .org 0x56344 - 0x8498
L_00056344:
    shll r2
    .org 0x56346 - 0x8498
L_00056346:
    shll2 r6
    .org 0x56348 - 0x8498
L_00056348:
    add r2,r5
    .org 0x5634a - 0x8498
L_0005634a:
    shll r6
    .org 0x5634c - 0x8498
L_0005634c:
    cmp/gt r6,r5
    .org 0x5634e - 0x8498
L_0005634e:
    bf L_0005635c
    .org 0x56350 - 0x8498
L_00056350:
    shll2 r7
    .org 0x56352 - 0x8498
L_00056352:
    shll2 r7
    .org 0x56354 - 0x8498
L_00056354:
    shll2 r7
    .org 0x56356 - 0x8498
L_00056356:
    shll r7
    .org 0x56358 - 0x8498
L_00056358:
    bra L_00056366
    .org 0x5635a - 0x8498
L_0005635a:
    mov r7,r6
    .org 0x5635c - 0x8498
L_0005635c:
    mov r12,r2
    .org 0x5635e - 0x8498
L_0005635e:
    shll2 r2
    .org 0x56360 - 0x8498
L_00056360:
    shll r2
    .org 0x56362 - 0x8498
L_00056362:
    mov r4,r6
    .org 0x56364 - 0x8498
L_00056364:
    add r2,r6
    .org 0x56366 - 0x8498
L_00056366:
    bra L_0005636e
    .org 0x56368 - 0x8498
L_00056368:
    mov r6,r7
    .org 0x5636a - 0x8498
L_0005636a:
    mov r4,r14
    .org 0x5636c - 0x8498
L_0005636c:
    mov r4,r7
    .org 0x5636e - 0x8498
L_0005636e:
    mov.l L_000563e0,r11
    .org 0x56370 - 0x8498
L_00056370:
    mov #0x61,r0
    .org 0x56372 - 0x8498
L_00056372:
    shll2 r0
    .org 0x56374 - 0x8498
L_00056374:
    mov.b @(r0,r11),r5
    .org 0x56376 - 0x8498
L_00056376:
    extu.b r5,r5
    .org 0x56378 - 0x8498
L_00056378:
    mov r5,r0
    .org 0x5637a - 0x8498
L_0005637a:
    cmp/eq #0x1,r0
    .org 0x5637c - 0x8498
L_0005637c:
    bt L_00056452
    .org 0x5637e - 0x8498
L_0005637e:
    cmp/eq #0x2,r0
    .org 0x56380 - 0x8498
L_00056380:
    bf L_000563a8
    .org 0x56382 - 0x8498
L_00056382:
    mov.l L_000563e4,r6
    .org 0x56384 - 0x8498
L_00056384:
    mov #0x2f,r0
    .org 0x56386 - 0x8498
L_00056386:
    mov.b @(r0,r6),r0
    .org 0x56388 - 0x8498
L_00056388:
    tst #0x10,r0
    .org 0x5638a - 0x8498
L_0005638a:
    bf L_000563a8
    .org 0x5638c - 0x8498
L_0005638c:
    tst #0x8,r0
    .org 0x5638e - 0x8498
L_0005638e:
    bt L_000563a8
    .org 0x56390 - 0x8498
L_00056390:
    mov.l L_000563fc,r6
    .org 0x56392 - 0x8498
L_00056392:
    extu.w r14,r0
    .org 0x56394 - 0x8498
L_00056394:
    mov.b @r6,r2
    .org 0x56396 - 0x8498
L_00056396:
    extu.b r2,r6
    .org 0x56398 - 0x8498
L_00056398:
    shll2 r6
    .org 0x5639a - 0x8498
L_0005639a:
    shll2 r6
    .org 0x5639c - 0x8498
L_0005639c:
    shll2 r6
    .org 0x5639e - 0x8498
L_0005639e:
    shll r6
    .org 0x563a0 - 0x8498
L_000563a0:
    cmp/ge r6,r0
    .org 0x563a2 - 0x8498
L_000563a2:
    bf L_00056452
    .org 0x563a4 - 0x8498
L_000563a4:
    bra L_00056456
    .org 0x563a6 - 0x8498
L_000563a6:
    nop
    .org 0x563a8 - 0x8498
L_000563a8:
    mov r5,r0
    .org 0x563aa - 0x8498
L_000563aa:
    cmp/eq #0x6,r0
    .org 0x563ac - 0x8498
L_000563ac:
    bf L_00056408
    .org 0x563ae - 0x8498
L_000563ae:
    mov.l L_000563e4,r6
    .org 0x563b0 - 0x8498
L_000563b0:
    mov #0x2f,r0
    .org 0x563b2 - 0x8498
L_000563b2:
    mov.b @(r0,r6),r0
    .org 0x563b4 - 0x8498
L_000563b4:
    tst #0x10,r0
    .org 0x563b6 - 0x8498
L_000563b6:
    bf L_00056408
    .org 0x563b8 - 0x8498
L_000563b8:
    tst #0x8,r0
    .org 0x563ba - 0x8498
L_000563ba:
    bt L_00056408
    .org 0x563bc - 0x8498
L_000563bc:
    mov #0x40,r12
    .org 0x563be - 0x8498
L_000563be:
    extu.w r4,r4
    .org 0x563c0 - 0x8498
L_000563c0:
    shll8 r12
    .org 0x563c2 - 0x8498
L_000563c2:
    cmp/eq r12,r4
    .org 0x563c4 - 0x8498
L_000563c4:
    bf L_000563cc
    .org 0x563c6 - 0x8498
L_000563c6:
    mov.l L_00056400,r6
    .org 0x563c8 - 0x8498
L_000563c8:
    bra L_00056446
    .org 0x563ca - 0x8498
L_000563ca:
    mov.b @r6,r2
    .org 0x563cc - 0x8498
L_000563cc:
    mov.l L_00056404,r6
    .org 0x563ce - 0x8498
L_000563ce:
    mov.w @r6,r2
    .org 0x563d0 - 0x8498
L_000563d0:
    extu.w r2,r2
    .org 0x563d2 - 0x8498
L_000563d2:
    cmp/gt r2,r4
    .org 0x563d4 - 0x8498
L_000563d4:
    bf/s L_0005643e
    .org 0x563d6 - 0x8498
L_000563d6:
    mov r14,r0
    .org 0x563d8 - 0x8498
L_000563d8:
    bra L_00056456
    .org 0x563da - 0x8498
L_000563da:
    nop
    .org 0x563dc - 0x8498
L_000563dc:
    .word 0x035f
    .org 0x563e0 - 0x8498
L_000563e0:
    .long 0xffff128c
    .org 0x563e4 - 0x8498
L_000563e4:
    .long 0xffff2464
    .org 0x563f0 - 0x8498
L_000563f0:
    .long 0xffff124c
    .org 0x563f4 - 0x8498
L_000563f4:
    .long 0x0000849b
    .org 0x563f8 - 0x8498
L_000563f8:
    .long 0x0000849c
    .org 0x563fc - 0x8498
L_000563fc:
    .long 0x00008b9f
    .org 0x56400 - 0x8498
L_00056400:
    .long 0x00008b9c
    .org 0x56404 - 0x8498
L_00056404:
    .long 0x0000929c
    .org 0x56408 - 0x8498
L_00056408:
    mov r5,r0
    .org 0x5640a - 0x8498
L_0005640a:
    cmp/eq #0x3,r0
    .org 0x5640c - 0x8498
L_0005640c:
    bt L_00056424
    .org 0x5640e - 0x8498
L_0005640e:
    cmp/eq #0x2,r0
    .org 0x56410 - 0x8498
L_00056410:
    bt L_00056424
    .org 0x56412 - 0x8498
L_00056412:
    cmp/eq #0x6,r0
    .org 0x56414 - 0x8498
L_00056414:
    bt L_00056424
    .org 0x56416 - 0x8498
L_00056416:
    cmp/eq #0x4,r0
    .org 0x56418 - 0x8498
L_00056418:
    bt L_00056442
    .org 0x5641a - 0x8498
L_0005641a:
    mov r5,r0
    .org 0x5641c - 0x8498
L_0005641c:
    cmp/eq #0x5,r0
    .org 0x5641e - 0x8498
L_0005641e:
    bt L_00056442
    .org 0x56420 - 0x8498
L_00056420:
    bra L_00056458
    .org 0x56422 - 0x8498
L_00056422:
    nop
    .org 0x56424 - 0x8498
L_00056424:
    mov r13,r0
    .org 0x56426 - 0x8498
L_00056426:
    tst #0x20,r0
    .org 0x56428 - 0x8498
L_00056428:
    bf L_00056442
    .org 0x5642a - 0x8498
L_0005642a:
    mov #0x40,r12
    .org 0x5642c - 0x8498
L_0005642c:
    extu.w r4,r4
    .org 0x5642e - 0x8498
L_0005642e:
    shll8 r12
    .org 0x56430 - 0x8498
L_00056430:
    cmp/eq r12,r4
    .org 0x56432 - 0x8498
L_00056432:
    bf L_0005643a
    .org 0x56434 - 0x8498
L_00056434:
    mov.l L_00056610,r6
    .org 0x56436 - 0x8498
L_00056436:
    bra L_00056446
    .org 0x56438 - 0x8498
L_00056438:
    mov.b @r6,r2
    .org 0x5643a - 0x8498
L_0005643a:
    cmp/gt r12,r4
    .org 0x5643c - 0x8498
L_0005643c:
    bf L_00056458
    .org 0x5643e - 0x8498
L_0005643e:
    bra L_00056456
    .org 0x56440 - 0x8498
L_00056440:
    mov r7,r0
    .org 0x56442 - 0x8498
L_00056442:
    mov.w L_0005651a,r0
    .org 0x56444 - 0x8498
L_00056444:
    mov.b @(r0,r11),r2
    .org 0x56446 - 0x8498
L_00056446:
    extu.b r2,r0
    .org 0x56448 - 0x8498
L_00056448:
    shll2 r0
    .org 0x5644a - 0x8498
L_0005644a:
    shll2 r0
    .org 0x5644c - 0x8498
L_0005644c:
    shll2 r0
    .org 0x5644e - 0x8498
L_0005644e:
    bra L_00056456
    .org 0x56450 - 0x8498
L_00056450:
    shll r0
    .org 0x56452 - 0x8498
L_00056452:
    mov #0x40,r0
    .org 0x56454 - 0x8498
L_00056454:
    shll8 r0
    .org 0x56456 - 0x8498
L_00056456:
    mov.w r0,@(0xc,r15)
    .org 0x56458 - 0x8498
L_00056458:
    mov.w @(0xc,r15),r0
    .org 0x5645a - 0x8498
L_0005645a:
    extu.w r0,r4
    .org 0x5645c - 0x8498
L_0005645c:
    mov.w L_0005651a,r0
    .org 0x5645e - 0x8498
L_0005645e:
    mov.b @(r0,r11),r7
    .org 0x56460 - 0x8498
L_00056460:
    extu.b r7,r7
    .org 0x56462 - 0x8498
L_00056462:
    mov r7,r6
    .org 0x56464 - 0x8498
L_00056464:
    shll2 r6
    .org 0x56466 - 0x8498
L_00056466:
    shll2 r6
    .org 0x56468 - 0x8498
L_00056468:
    shll2 r6
    .org 0x5646a - 0x8498
L_0005646a:
    shll r6
    .org 0x5646c - 0x8498
L_0005646c:
    cmp/gt r6,r4
    .org 0x5646e - 0x8498
L_0005646e:
    bf L_0005647c
    .org 0x56470 - 0x8498
L_00056470:
    mov r7,r6
    .org 0x56472 - 0x8498
L_00056472:
    shll2 r6
    .org 0x56474 - 0x8498
L_00056474:
    shll2 r6
    .org 0x56476 - 0x8498
L_00056476:
    shll2 r6
    .org 0x56478 - 0x8498
L_00056478:
    bra L_0005647e
    .org 0x5647a - 0x8498
L_0005647a:
    shll r6
    .org 0x5647c - 0x8498
L_0005647c:
    mov r4,r6
    .org 0x5647e - 0x8498
L_0005647e:
    extu.w r6,r4
    .org 0x56480 - 0x8498
L_00056480:
    mov r7,r6
    .org 0x56482 - 0x8498
L_00056482:
    shll2 r6
    .org 0x56484 - 0x8498
L_00056484:
    shll2 r6
    .org 0x56486 - 0x8498
L_00056486:
    shll2 r6
    .org 0x56488 - 0x8498
L_00056488:
    shll r6
    .org 0x5648a - 0x8498
L_0005648a:
    cmp/eq r6,r4
    .org 0x5648c - 0x8498
L_0005648c:
    bf L_00056496
    .org 0x5648e - 0x8498
L_0005648e:
    mov r13,r0
    .org 0x56490 - 0x8498
L_00056490:
    mov.l L_00056614,r2
    .org 0x56492 - 0x8498
L_00056492:
    bra L_0005649c
    .org 0x56494 - 0x8498
L_00056494:
    or #0x20,r0
    .org 0x56496 - 0x8498
L_00056496:
    mov r13,r0
    .org 0x56498 - 0x8498
L_00056498:
    and #0xdf,r0
    .org 0x5649a - 0x8498
L_0005649a:
    mov.l L_00056614,r2
    .org 0x5649c - 0x8498
L_0005649c:
    mov r0,r13
    .org 0x5649e - 0x8498
L_0005649e:
    mov #0x21,r0
    .org 0x564a0 - 0x8498
L_000564a0:
    mov.l L_00056618,r14
    .org 0x564a2 - 0x8498
L_000564a2:
    mov.b r13,@(r0,r2)
    .org 0x564a4 - 0x8498
L_000564a4:
    mov #0x2c,r0
    .org 0x564a6 - 0x8498
L_000564a6:
    bsr L_0005651c
    .org 0x564a8 - 0x8498
L_000564a8:
    mov.w r4,@(r0,r14)
    .org 0x564aa - 0x8498
L_000564aa:
    mov #0x2c,r0
    .org 0x564ac - 0x8498
L_000564ac:
    mov.w @(r0,r14),r4
    .org 0x564ae - 0x8498
L_000564ae:
    mov #0x2e,r0
    .org 0x564b0 - 0x8498
L_000564b0:
    mov.w @(r0,r14),r5
    .org 0x564b2 - 0x8498
L_000564b2:
    extu.w r4,r4
    .org 0x564b4 - 0x8498
L_000564b4:
    extu.w r5,r2
    .org 0x564b6 - 0x8498
L_000564b6:
    cmp/ge r2,r4
    .org 0x564b8 - 0x8498
L_000564b8:
    bf L_000564bc
    .org 0x564ba - 0x8498
L_000564ba:
    mov r4,r2
    .org 0x564bc - 0x8498
L_000564bc:
    mov r2,r5
    .org 0x564be - 0x8498
L_000564be:
    mov.l L_0005661c,r2
    .org 0x564c0 - 0x8498
L_000564c0:
    mov #-0x7a,r0
    .org 0x564c2 - 0x8498
L_000564c2:
    extu.b r0,r0
    .org 0x564c4 - 0x8498
L_000564c4:
    mov.b @(r0,r2),r6
    .org 0x564c6 - 0x8498
L_000564c6:
    mov #0x20,r4
    .org 0x564c8 - 0x8498
L_000564c8:
    extu.b r6,r6
    .org 0x564ca - 0x8498
L_000564ca:
    cmp/ge r4,r6
    .org 0x564cc - 0x8498
L_000564cc:
    bt L_000564da
    .org 0x564ce - 0x8498
L_000564ce:
    mov.l L_00056620,r14
    .org 0x564d0 - 0x8498
L_000564d0:
    mov.l L_00056624,r7
    .org 0x564d2 - 0x8498
L_000564d2:
    mov.b @(0xa,r14),r0
    .org 0x564d4 - 0x8498
L_000564d4:
    mov r0,r2
    .org 0x564d6 - 0x8498
L_000564d6:
    mov #0x38,r0
    .org 0x564d8 - 0x8498
L_000564d8:
    mov.b r2,@(r0,r7)
    .org 0x564da - 0x8498
L_000564da:
    cmp/ge r4,r6
    .org 0x564dc - 0x8498
L_000564dc:
    bf L_000564e8
    .org 0x564de - 0x8498
L_000564de:
    mov.l L_00056624,r7
    .org 0x564e0 - 0x8498
L_000564e0:
    mov #0x38,r0
    .org 0x564e2 - 0x8498
L_000564e2:
    mov.b @(r0,r7),r2
    .org 0x564e4 - 0x8498
L_000564e4:
    tst r2,r2
    .org 0x564e6 - 0x8498
L_000564e6:
    bt L_000564ec
    .org 0x564e8 - 0x8498
L_000564e8:
    mov #0x40,r5
    .org 0x564ea - 0x8498
L_000564ea:
    shll8 r5
    .org 0x564ec - 0x8498
L_000564ec:
    mov.l L_00056628,r6
    .org 0x564ee - 0x8498
L_000564ee:
    mov.b @(0x6,r6),r0
    .org 0x564f0 - 0x8498
L_000564f0:
    tst #0x2,r0
    .org 0x564f2 - 0x8498
L_000564f2:
    bt L_00056504
    .org 0x564f4 - 0x8498
L_000564f4:
    mov.l L_0005662c,r2
    .org 0x564f6 - 0x8498
L_000564f6:
    extu.w r5,r5
    .org 0x564f8 - 0x8498
L_000564f8:
    mov.w @r2,r4
    .org 0x564fa - 0x8498
L_000564fa:
    extu.w r4,r2
    .org 0x564fc - 0x8498
L_000564fc:
    cmp/gt r2,r5
    .org 0x564fe - 0x8498
L_000564fe:
    bt L_00056502
    .org 0x56500 - 0x8498
L_00056500:
    mov r5,r2
    .org 0x56502 - 0x8498
L_00056502:
    mov r2,r5
    .org 0x56504 - 0x8498
L_00056504:
    mov.l L_00056630,r6
    .org 0x56506 - 0x8498
L_00056506:
    mov r5,r0
    .org 0x56508 - 0x8498
L_00056508:
    mov.w r0,@(0xc,r6)
    .org 0x5651a - 0x8498
L_0005651a:
    .word 0x035f
    .org 0x5651c - 0x8498
L_0005651c:
    mov.l r11,@-r15
    .org 0x5651e - 0x8498
L_0005651e:
    mov.l r13,@-r15
    .org 0x56520 - 0x8498
L_00056520:
    sts.l pr,@-r15
    .org 0x56522 - 0x8498
L_00056522:
    stc.l gbr,@-r15
    .org 0x56524 - 0x8498
L_00056524:
    mov.l L_00056634,r0
    .org 0x56526 - 0x8498
L_00056526:
    ldc r0,gbr
    .org 0x56528 - 0x8498
L_00056528:
    add #-0x4,r15
    .org 0x5652a - 0x8498
L_0005652a:
    mov.l L_00056638,r5
    .org 0x5652c - 0x8498
L_0005652c:
    mov #0x17,r0
    .org 0x5652e - 0x8498
L_0005652e:
    mov.l L_0005663c,r4
    .org 0x56530 - 0x8498
L_00056530:
    mov.b @(r0,r5),r6
    .org 0x56532 - 0x8498
L_00056532:
    mov.l L_00056640,r2
    .org 0x56534 - 0x8498
L_00056534:
    jsr @r2
    .org 0x56536 - 0x8498
L_00056536:
    extu.b r6,r5
    .org 0x56538 - 0x8498
L_00056538:
    mov.l L_00056644,r5
    .org 0x5653a - 0x8498
L_0005653a:
    mov r0,r2
    .org 0x5653c - 0x8498
L_0005653c:
    mov #0x5b,r0
    .org 0x5653e - 0x8498
L_0005653e:
    mov.b r2,@(r0,r5)
    .org 0x56540 - 0x8498
L_00056540:
    mov.l L_00056648,r2
    .org 0x56542 - 0x8498
L_00056542:
    mov.b @(0x4,gbr),r0
    .org 0x56544 - 0x8498
L_00056544:
    mov.b @r2,r13
    .org 0x56546 - 0x8498
L_00056546:
    tst #0x80,r0
    .org 0x56548 - 0x8498
L_00056548:
    bt/s L_00056554
    .org 0x5654a - 0x8498
L_0005654a:
    extu.b r13,r13
    .org 0x5654c - 0x8498
L_0005654c:
    mov.l L_0005664c,r2
    .org 0x5654e - 0x8498
L_0005654e:
    mov.b @r2,r6
    .org 0x56550 - 0x8498
L_00056550:
    extu.b r6,r6
    .org 0x56552 - 0x8498
L_00056552:
    add r6,r13
    .org 0x56554 - 0x8498
L_00056554:
    mov.l L_00056644,r5
    .org 0x56556 - 0x8498
L_00056556:
    mov #0x5b,r0
    .org 0x56558 - 0x8498
L_00056558:
    mov.b @(r0,r5),r2
    .org 0x5655a - 0x8498
L_0005655a:
    extu.b r2,r2
    .org 0x5655c - 0x8498
L_0005655c:
    cmp/hs r2,r13
    .org 0x5655e - 0x8498
L_0005655e:
    bt/s L_00056566
    .org 0x56560 - 0x8498
L_00056560:
    mov #0x4,r0
    .org 0x56562 - 0x8498
L_00056562:
    bra L_00056568
    .org 0x56564 - 0x8498
L_00056564:
    and.b #0x7f,@(r0,gbr)
    .org 0x56566 - 0x8498
L_00056566:
    or.b #0x80,@(r0,gbr)
    .org 0x56568 - 0x8498
L_00056568:
    mov.l L_00056650,r2
    .org 0x5656a - 0x8498
L_0005656a:
    mov #0x7a,r0
    .org 0x5656c - 0x8498
L_0005656c:
    mov.b @(r0,r2),r13
    .org 0x5656e - 0x8498
L_0005656e:
    mov.b @(0x23,gbr),r0
    .org 0x56570 - 0x8498
L_00056570:
    tst #0x4,r0
    .org 0x56572 - 0x8498
L_00056572:
    bf/s L_0005657e
    .org 0x56574 - 0x8498
L_00056574:
    extu.b r13,r13
    .org 0x56576 - 0x8498
L_00056576:
    mov.l L_00056654,r6
    .org 0x56578 - 0x8498
L_00056578:
    mov.b @r6,r2
    .org 0x5657a - 0x8498
L_0005657a:
    extu.b r2,r2
    .org 0x5657c - 0x8498
L_0005657c:
    add r2,r13
    .org 0x5657e - 0x8498
L_0005657e:
    mov.l L_00056658,r6
    .org 0x56580 - 0x8498
L_00056580:
    mov.b @r6,r2
    .org 0x56582 - 0x8498
L_00056582:
    extu.b r2,r2
    .org 0x56584 - 0x8498
L_00056584:
    cmp/hi r2,r13
    .org 0x56586 - 0x8498
L_00056586:
    bt/s L_0005658e
    .org 0x56588 - 0x8498
L_00056588:
    mov #0x23,r0
    .org 0x5658a - 0x8498
L_0005658a:
    bra L_00056590
    .org 0x5658c - 0x8498
L_0005658c:
    or.b #0x4,@(r0,gbr)
    .org 0x5658e - 0x8498
L_0005658e:
    and.b #0xfb,@(r0,gbr)
    .org 0x56590 - 0x8498
L_00056590:
    mov.b @(0x4,gbr),r0
    .org 0x56592 - 0x8498
L_00056592:
    tst #0x80,r0
    .org 0x56594 - 0x8498
L_00056594:
    bt/s L_000565aa
    .org 0x56596 - 0x8498
L_00056596:
    mov r0,r13
    .org 0x56598 - 0x8498
L_00056598:
    mov.b @(0x23,gbr),r0
    .org 0x5659a - 0x8498
L_0005659a:
    tst #0x4,r0
    .org 0x5659c - 0x8498
L_0005659c:
    bt L_000565aa
    .org 0x5659e - 0x8498
L_0005659e:
    mov.b @(0x79,gbr),r0
    .org 0x565a0 - 0x8498
L_000565a0:
    tst r0,r0
    .org 0x565a2 - 0x8498
L_000565a2:
    bf L_000565b0
    .org 0x565a4 - 0x8498
L_000565a4:
    mov r13,r0
    .org 0x565a6 - 0x8498
L_000565a6:
    bra L_000565b4
    .org 0x565a8 - 0x8498
L_000565a8:
    or #0x40,r0
    .org 0x565aa - 0x8498
L_000565aa:
    mov.l L_0005665c,r6
    .org 0x565ac - 0x8498
L_000565ac:
    mov.b @r6,r0
    .org 0x565ae - 0x8498
L_000565ae:
    mov.b r0,@(0x79,gbr)
    .org 0x565b0 - 0x8498
L_000565b0:
    mov r13,r0
    .org 0x565b2 - 0x8498
L_000565b2:
    and #0xbf,r0
    .org 0x565b4 - 0x8498
L_000565b4:
    mov.w L_0005660e,r6
    .org 0x565b6 - 0x8498
L_000565b6:
    mov.b r0,@(0x4,gbr)
    .org 0x565b8 - 0x8498
L_000565b8:
    mov.b @r6,r0
    .org 0x565ba - 0x8498
L_000565ba:
    tst #0x80,r0
    .org 0x565bc - 0x8498
L_000565bc:
    bf L_000565c2
    .org 0x565be - 0x8498
L_000565be:
    bra L_000566f4
    .org 0x565c0 - 0x8498
L_000565c0:
    nop
    .org 0x565c2 - 0x8498
L_000565c2:
    mov.l L_00056660,r4
    .org 0x565c4 - 0x8498
L_000565c4:
    mov #0x2e,r0
    .org 0x565c6 - 0x8498
L_000565c6:
    mov.l L_00056664,r2
    .org 0x565c8 - 0x8498
L_000565c8:
    mov.b @r4,r5
    .org 0x565ca - 0x8498
L_000565ca:
    mov.w @(r0,r2),r13
    .org 0x565cc - 0x8498
L_000565cc:
    extu.b r5,r5
    .org 0x565ce - 0x8498
L_000565ce:
    mov r5,r2
    .org 0x565d0 - 0x8498
L_000565d0:
    shll2 r2
    .org 0x565d2 - 0x8498
L_000565d2:
    extu.w r13,r13
    .org 0x565d4 - 0x8498
L_000565d4:
    shll r2
    .org 0x565d6 - 0x8498
L_000565d6:
    mov r13,r6
    .org 0x565d8 - 0x8498
L_000565d8:
    sub r2,r6
    .org 0x565da - 0x8498
L_000565da:
    mov #0x40,r2
    .org 0x565dc - 0x8498
L_000565dc:
    shll8 r2
    .org 0x565de - 0x8498
L_000565de:
    cmp/ge r2,r6
    .org 0x565e0 - 0x8498
L_000565e0:
    bt L_000565e8
    .org 0x565e2 - 0x8498
L_000565e2:
    mov #0x40,r6
    .org 0x565e4 - 0x8498
L_000565e4:
    bra L_000565f0
    .org 0x565e6 - 0x8498
L_000565e6:
    shll8 r6
    .org 0x565e8 - 0x8498
L_000565e8:
    shll2 r5
    .org 0x565ea - 0x8498
L_000565ea:
    mov r13,r6
    .org 0x565ec - 0x8498
L_000565ec:
    shll r5
    .org 0x565ee - 0x8498
L_000565ee:
    sub r5,r6
    .org 0x565f0 - 0x8498
L_000565f0:
    mov.b @(0x1,r4),r0
    .org 0x565f2 - 0x8498
L_000565f2:
    mov r6,r11
    .org 0x565f4 - 0x8498
L_000565f4:
    mov.l L_00056668,r5
    .org 0x565f6 - 0x8498
L_000565f6:
    mov r13,r6
    .org 0x565f8 - 0x8498
L_000565f8:
    extu.b r0,r7
    .org 0x565fa - 0x8498
L_000565fa:
    mov r7,r2
    .org 0x565fc - 0x8498
L_000565fc:
    mov.w @r5,r4
    .org 0x565fe - 0x8498
L_000565fe:
    shll2 r2
    .org 0x56600 - 0x8498
L_00056600:
    shll r2
    .org 0x56602 - 0x8498
L_00056602:
    extu.w r4,r4
    .org 0x56604 - 0x8498
L_00056604:
    add r2,r6
    .org 0x56606 - 0x8498
L_00056606:
    cmp/gt r4,r6
    .org 0x56608 - 0x8498
L_00056608:
    bf L_0005666c
    .org 0x5660a - 0x8498
L_0005660a:
    bra L_00056674
    .org 0x5660c - 0x8498
L_0005660c:
    mov r4,r2
    .org 0x5660e - 0x8498
L_0005660e:
    .word 0x84c3
    .org 0x56610 - 0x8498
L_00056610:
    .long 0x00008b9b
    .org 0x56614 - 0x8498
L_00056614:
    .long 0xffff2464
    .org 0x56618 - 0x8498
L_00056618:
    .long 0xffff120e
    .org 0x5661c - 0x8498
L_0005661c:
    .long 0xffff267a
    .org 0x56620 - 0x8498
L_00056620:
    .long 0x000087cc
    .org 0x56624 - 0x8498
L_00056624:
    .long 0xffff24f9
    .org 0x56628 - 0x8498
L_00056628:
    .long 0xffff424c
    .org 0x5662c - 0x8498
L_0005662c:
    .long 0x000094ec
    .org 0x56630 - 0x8498
L_00056630:
    .long 0xffff22dc
    .org 0x56634 - 0x8498
L_00056634:
    .long 0xffff2470
    .org 0x56638 - 0x8498
L_00056638:
    .long 0xffff119c
    .org 0x5663c - 0x8498
L_0005663c:
    .long 0x00011ede
    .org 0x56640 - 0x8498
L_00056640:
    .long 0x00026370
    .org 0x56644 - 0x8498
L_00056644:
    .long 0xffff128c
    .org 0x56648 - 0x8498
L_00056648:
    .long 0xffff102c
    .org 0x5664c - 0x8498
L_0005664c:
    .long 0x000086ea
    .org 0x56650 - 0x8498
L_00056650:
    .long 0xffff1094
    .org 0x56654 - 0x8498
L_00056654:
    .long 0x000086f3
    .org 0x56658 - 0x8498
L_00056658:
    .long 0x000087d9
    .org 0x5665c - 0x8498
L_0005665c:
    .long 0x00008bef
    .org 0x56660 - 0x8498
L_00056660:
    .long 0x0000849b
    .org 0x56664 - 0x8498
L_00056664:
    .long 0xffff124c
    .org 0x56668 - 0x8498
L_00056668:
    .long 0x00008f86
    .org 0x5666c - 0x8498
L_0005666c:
    shll2 r7
    .org 0x5666e - 0x8498
L_0005666e:
    mov r13,r2
    .org 0x56670 - 0x8498
L_00056670:
    shll r7
    .org 0x56672 - 0x8498
L_00056672:
    add r7,r2
    .org 0x56674 - 0x8498
L_00056674:
    mov.b @(0x4,gbr),r0
    .org 0x56676 - 0x8498
L_00056676:
    tst #0x40,r0
    .org 0x56678 - 0x8498
L_00056678:
    bt L_000566b8
    .org 0x5667a - 0x8498
L_0005667a:
    mov #0x40,r6
    .org 0x5667c - 0x8498
L_0005667c:
    shll8 r6
    .org 0x5667e - 0x8498
L_0005667e:
    cmp/eq r6,r13
    .org 0x56680 - 0x8498
L_00056680:
    bf L_00056694
    .org 0x56682 - 0x8498
L_00056682:
    mov.l L_00056700,r6
    .org 0x56684 - 0x8498
L_00056684:
    mov.b @r6,r2
    .org 0x56686 - 0x8498
L_00056686:
    extu.b r2,r2
    .org 0x56688 - 0x8498
L_00056688:
    shll2 r2
    .org 0x5668a - 0x8498
L_0005668a:
    shll2 r2
    .org 0x5668c - 0x8498
L_0005668c:
    shll2 r2
    .org 0x5668e - 0x8498
L_0005668e:
    shll r2
    .org 0x56690 - 0x8498
L_00056690:
    bra L_000566ee
    .org 0x56692 - 0x8498
L_00056692:
    mov.w r2,@r15
    .org 0x56694 - 0x8498
L_00056694:
    mov #0x40,r6
    .org 0x56696 - 0x8498
L_00056696:
    shll8 r6
    .org 0x56698 - 0x8498
L_00056698:
    cmp/gt r6,r13
    .org 0x5669a - 0x8498
L_0005669a:
    bf L_000566a6
    .org 0x5669c - 0x8498
L_0005669c:
    mov.l L_00056704,r3
    .org 0x5669e - 0x8498
L_0005669e:
    mov.w @r3,r4
    .org 0x566a0 - 0x8498
L_000566a0:
    extu.w r4,r4
    .org 0x566a2 - 0x8498
L_000566a2:
    cmp/ge r4,r13
    .org 0x566a4 - 0x8498
L_000566a4:
    bf L_000566ee
    .org 0x566a6 - 0x8498
L_000566a6:
    mov.l L_00056704,r3
    .org 0x566a8 - 0x8498
L_000566a8:
    mov.w @r3,r4
    .org 0x566aa - 0x8498
L_000566aa:
    extu.w r4,r4
    .org 0x566ac - 0x8498
L_000566ac:
    cmp/ge r4,r13
    .org 0x566ae - 0x8498
L_000566ae:
    bf L_000566f4
    .org 0x566b0 - 0x8498
L_000566b0:
    mov.l L_00056708,r5
    .org 0x566b2 - 0x8498
L_000566b2:
    mov #0x2e,r0
    .org 0x566b4 - 0x8498
L_000566b4:
    bra L_000566f4
    .org 0x566b6 - 0x8498
L_000566b6:
    mov.w r4,@(r0,r5)
    .org 0x566b8 - 0x8498
L_000566b8:
    mov.l L_0005670c,r2
    .org 0x566ba - 0x8498
L_000566ba:
    mov.b @r2,r5
    .org 0x566bc - 0x8498
L_000566bc:
    extu.b r5,r5
    .org 0x566be - 0x8498
L_000566be:
    mov r5,r6
    .org 0x566c0 - 0x8498
L_000566c0:
    shll2 r6
    .org 0x566c2 - 0x8498
L_000566c2:
    shll2 r6
    .org 0x566c4 - 0x8498
L_000566c4:
    shll2 r6
    .org 0x566c6 - 0x8498
L_000566c6:
    shll r6
    .org 0x566c8 - 0x8498
L_000566c8:
    cmp/gt r6,r13
    .org 0x566ca - 0x8498
L_000566ca:
    bf L_000566de
    .org 0x566cc - 0x8498
L_000566cc:
    mov.l L_00056704,r3
    .org 0x566ce - 0x8498
L_000566ce:
    mov.w @r3,r4
    .org 0x566d0 - 0x8498
L_000566d0:
    extu.w r4,r4
    .org 0x566d2 - 0x8498
L_000566d2:
    cmp/gt r4,r13
    .org 0x566d4 - 0x8498
L_000566d4:
    bt L_000566de
    .org 0x566d6 - 0x8498
L_000566d6:
    mov.l L_00056708,r5
    .org 0x566d8 - 0x8498
L_000566d8:
    mov #0x2e,r0
    .org 0x566da - 0x8498
L_000566da:
    bra L_000566f4
    .org 0x566dc - 0x8498
L_000566dc:
    mov.w r11,@(r0,r5)
    .org 0x566de - 0x8498
L_000566de:
    shll2 r5
    .org 0x566e0 - 0x8498
L_000566e0:
    shll2 r5
    .org 0x566e2 - 0x8498
L_000566e2:
    shll2 r5
    .org 0x566e4 - 0x8498
L_000566e4:
    shll r5
    .org 0x566e6 - 0x8498
L_000566e6:
    cmp/gt r5,r13
    .org 0x566e8 - 0x8498
L_000566e8:
    bt L_000566f4
    .org 0x566ea - 0x8498
L_000566ea:
    mov #0x40,r2
    .org 0x566ec - 0x8498
L_000566ec:
    shll8 r2
    .org 0x566ee - 0x8498
L_000566ee:
    mov.l L_00056708,r5
    .org 0x566f0 - 0x8498
L_000566f0:
    mov #0x2e,r0
    .org 0x566f2 - 0x8498
L_000566f2:
    mov.w r2,@(r0,r5)
    .org 0x566f4 - 0x8498
L_000566f4:
    add #0x4,r15
    .org 0x566f6 - 0x8498
L_000566f6:
    ldc.l @r15+,gbr
    .org 0x566f8 - 0x8498
L_000566f8:
    lds.l @r15+,pr
    .org 0x566fa - 0x8498
L_000566fa:
    mov.l @r15+,r13
    .org 0x566fc - 0x8498
L_000566fc:
    rts
    .org 0x566fe - 0x8498
L_000566fe:
    mov.l @r15+,r11
    .org 0x56700 - 0x8498
L_00056700:
    .long 0x00008b9b
    .org 0x56704 - 0x8498
L_00056704:
    .long 0x00008f86
    .org 0x56708 - 0x8498
L_00056708:
    .long 0xffff120e
    .org 0x5670c - 0x8498
L_0005670c:
    .long 0x00008b9f
