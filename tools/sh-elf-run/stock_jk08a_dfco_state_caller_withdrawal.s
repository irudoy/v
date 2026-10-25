! Complete natural DFCO state caller and exact real six-channel mask rotation.
    .text
    .balign 4
    .set ORIGIN,0x85f4
    .org 0x85f6-ORIGIN
P_000085f6:
    .byte 0x14
    .org 0x8711-ORIGIN
P_00008711:
    .byte 0x00
    .org 0x8a40-ORIGIN
P_00008a40:
    .byte 0x04
    .org 0x8b3f-ORIGIN
P_00008b3f:
    .byte 0x18
    .org 0x8c1a-ORIGIN
P_00008c1a:
    .byte 0x05
    .org 0x8c1b-ORIGIN
P_00008c1b:
    .byte 0x04
    .org 0x8c1c-ORIGIN
P_00008c1c:
    .byte 0x00
    .org 0x8c1d-ORIGIN
P_00008c1d:
    .byte 0x00
    .org 0x8c1e-ORIGIN
P_00008c1e:
    .byte 0x70
    .org 0x503e0-ORIGIN
L_000503e0:
    mov.l r9,@-r15
    .org 0x503e2-ORIGIN
L_000503e2:
    mov.l r10,@-r15
    .org 0x503e4-ORIGIN
L_000503e4:
    mov.l r11,@-r15
    .org 0x503e6-ORIGIN
L_000503e6:
    mov.l r12,@-r15
    .org 0x503e8-ORIGIN
L_000503e8:
    mov.l r13,@-r15
    .org 0x503ea-ORIGIN
L_000503ea:
    mov.l r14,@-r15
    .org 0x503ec-ORIGIN
L_000503ec:
    sts.l pr,@-r15
    .org 0x503ee-ORIGIN
L_000503ee:
    sts.l macl,@-r15
    .org 0x503f0-ORIGIN
L_000503f0:
    add #-0x4,r15
    .org 0x503f2-ORIGIN
L_000503f2:
    mov r6,r0
    .org 0x503f4-ORIGIN
L_000503f4:
    mov.w r0,@(0x2,r15)
    .org 0x503f6-ORIGIN
L_000503f6:
    mov.l P_00050478,r9
    .org 0x503f8-ORIGIN
L_000503f8:
    mov.w P_00050400,r0
    .org 0x503fa-ORIGIN
L_000503fa:
    mov.l P_0005047c,r10
    .org 0x503fc-ORIGIN
L_000503fc:
    bra L_00050402
    .org 0x503fe-ORIGIN
L_000503fe:
    mov r5,r12
    .org 0x50400-ORIGIN
P_00050400:
    .byte 0x02
    .org 0x50401-ORIGIN
P_00050401:
    .byte 0x35
    .org 0x50402-ORIGIN
L_00050402:
    mov.b @(r0,r9),r2
    .org 0x50404-ORIGIN
L_00050404:
    mov.b @r10,r0
    .org 0x50406-ORIGIN
L_00050406:
    mov.l r6,@r15
    .org 0x50408-ORIGIN
L_00050408:
    mov #0x0,r6
    .org 0x5040a-ORIGIN
L_0005040a:
    tst #0x40,r0
    .org 0x5040c-ORIGIN
L_0005040c:
    extu.b r2,r11
    .org 0x5040e-ORIGIN
L_0005040e:
    mov r6,r13
    .org 0x50410-ORIGIN
L_00050410:
    bt/s L_00050418
    .org 0x50412-ORIGIN
L_00050412:
    mov r6,r14
    .org 0x50414-ORIGIN
L_00050414:
    bra L_000505f4
    .org 0x50416-ORIGIN
L_00050416:
    nop
    .org 0x50418-ORIGIN
L_00050418:
    mov r11,r0
    .org 0x5041a-ORIGIN
L_0005041a:
    cmp/eq #0x4,r0
    .org 0x5041c-ORIGIN
L_0005041c:
    bf L_00050436
    .org 0x5041e-ORIGIN
L_0005041e:
    mov.l P_00050468,r5
    .org 0x50420-ORIGIN
L_00050420:
    mov.b @r5,r0
    .org 0x50422-ORIGIN
L_00050422:
    tst #0x20,r0
    .org 0x50424-ORIGIN
L_00050424:
    bt L_00050436
    .org 0x50426-ORIGIN
L_00050426:
    mov.l P_00050480,r2
    .org 0x50428-ORIGIN
L_00050428:
    mov.l P_00050470,r3
    .org 0x5042a-ORIGIN
L_0005042a:
    mov.b @(0x2,r2),r0
    .org 0x5042c-ORIGIN
L_0005042c:
    mov.b @r3,r2
    .org 0x5042e-ORIGIN
L_0005042e:
    cmp/hs r2,r0
    .org 0x50430-ORIGIN
L_00050430:
    bf L_00050436
    .org 0x50432-ORIGIN
L_00050432:
    bra L_000505f4
    .org 0x50434-ORIGIN
L_00050434:
    nop
    .org 0x50436-ORIGIN
L_00050436:
    mov #0x2,r5
    .org 0x50438-ORIGIN
L_00050438:
    cmp/gt r5,r11
    .org 0x5043a-ORIGIN
L_0005043a:
    bt L_000504ca
    .org 0x5043c-ORIGIN
L_0005043c:
    tst r12,r12
    .org 0x5043e-ORIGIN
L_0005043e:
    bt L_00050484
    .org 0x50440-ORIGIN
L_00050440:
    bra L_00050498
    .org 0x50442-ORIGIN
L_00050442:
    mov #0x0,r11
    .org 0x50468-ORIGIN
P_00050468:
    .byte 0xff
    .org 0x50469-ORIGIN
P_00050469:
    .byte 0xff
    .org 0x5046a-ORIGIN
P_0005046a:
    .byte 0x24
    .org 0x5046b-ORIGIN
P_0005046b:
    .byte 0x58
    .org 0x50470-ORIGIN
P_00050470:
    .byte 0x00
    .org 0x50471-ORIGIN
P_00050471:
    .byte 0x00
    .org 0x50472-ORIGIN
P_00050472:
    .byte 0x8a
    .org 0x50473-ORIGIN
P_00050473:
    .byte 0x40
    .org 0x50478-ORIGIN
P_00050478:
    .byte 0xff
    .org 0x50479-ORIGIN
P_00050479:
    .byte 0xff
    .org 0x5047a-ORIGIN
P_0005047a:
    .byte 0x12
    .org 0x5047b-ORIGIN
P_0005047b:
    .byte 0x8c
    .org 0x5047c-ORIGIN
P_0005047c:
    .byte 0xff
    .org 0x5047d-ORIGIN
P_0005047d:
    .byte 0xff
    .org 0x5047e-ORIGIN
P_0005047e:
    .byte 0x24
    .org 0x5047f-ORIGIN
P_0005047f:
    .byte 0x68
    .org 0x50480-ORIGIN
P_00050480:
    .byte 0xff
    .org 0x50481-ORIGIN
P_00050481:
    .byte 0xff
    .org 0x50482-ORIGIN
P_00050482:
    .byte 0x10
    .org 0x50483-ORIGIN
P_00050483:
    .byte 0x68
    .org 0x50484-ORIGIN
L_00050484:
    tst r4,r4
    .org 0x50486-ORIGIN
L_00050486:
    bt L_00050498
    .org 0x50488-ORIGIN
L_00050488:
    tst r11,r11
    .org 0x5048a-ORIGIN
L_0005048a:
    bf L_00050498
    .org 0x5048c-ORIGIN
L_0005048c:
    mov r15,r5
    .org 0x5048e-ORIGIN
L_0005048e:
    add #0x2,r5
    .org 0x50490-ORIGIN
L_00050490:
    mov.b @r5,r0
    .org 0x50492-ORIGIN
L_00050492:
    mov #0x1,r11
    .org 0x50494-ORIGIN
L_00050494:
    mov.l P_000506b0,r4
    .org 0x50496-ORIGIN
L_00050496:
    mov.b r0,@(0x7,r4)
    .org 0x50498-ORIGIN
L_00050498:
    extu.b r11,r11
    .org 0x5049a-ORIGIN
L_0005049a:
    mov r11,r0
    .org 0x5049c-ORIGIN
L_0005049c:
    cmp/eq #0x1,r0
    .org 0x5049e-ORIGIN
L_0005049e:
    bf L_000504b2
    .org 0x504a0-ORIGIN
L_000504a0:
    mov.l P_000506b0,r4
    .org 0x504a2-ORIGIN
L_000504a2:
    mov.b @(0x7,r4),r0
    .org 0x504a4-ORIGIN
L_000504a4:
    tst r0,r0
    .org 0x504a6-ORIGIN
L_000504a6:
    bf L_000504b2
    .org 0x504a8-ORIGIN
L_000504a8:
    mov r15,r5
    .org 0x504aa-ORIGIN
L_000504aa:
    add #0x2,r5
    .org 0x504ac-ORIGIN
L_000504ac:
    mov.b @(0x1,r5),r0
    .org 0x504ae-ORIGIN
L_000504ae:
    mov #0x2,r11
    .org 0x504b0-ORIGIN
L_000504b0:
    mov.b r0,@(0x8,r4)
    .org 0x504b2-ORIGIN
L_000504b2:
    extu.b r11,r11
    .org 0x504b4-ORIGIN
L_000504b4:
    mov r11,r0
    .org 0x504b6-ORIGIN
L_000504b6:
    cmp/eq #0x2,r0
    .org 0x504b8-ORIGIN
L_000504b8:
    bt L_000504be
    .org 0x504ba-ORIGIN
L_000504ba:
    bra L_000505ae
    .org 0x504bc-ORIGIN
L_000504bc:
    nop
    .org 0x504be-ORIGIN
L_000504be:
    mov.l P_000506b0,r4
    .org 0x504c0-ORIGIN
L_000504c0:
    mov.b @(0x8,r4),r0
    .org 0x504c2-ORIGIN
L_000504c2:
    tst r0,r0
    .org 0x504c4-ORIGIN
L_000504c4:
    bf L_000505ae
    .org 0x504c6-ORIGIN
L_000504c6:
    bra L_000505ae
    .org 0x504c8-ORIGIN
L_000504c8:
    mov #0x3,r11
    .org 0x504ca-ORIGIN
L_000504ca:
    tst r4,r4
    .org 0x504cc-ORIGIN
L_000504cc:
    bt L_000504d6
    .org 0x504ce-ORIGIN
L_000504ce:
    tst r12,r12
    .org 0x504d0-ORIGIN
L_000504d0:
    bf L_000504d6
    .org 0x504d2-ORIGIN
L_000504d2:
    bra L_0005059e
    .org 0x504d4-ORIGIN
L_000504d4:
    mov #0x3,r11
    .org 0x504d6-ORIGIN
L_000504d6:
    tst r12,r12
    .org 0x504d8-ORIGIN
L_000504d8:
    bt L_000505ae
    .org 0x504da-ORIGIN
L_000504da:
    mov r11,r0
    .org 0x504dc-ORIGIN
L_000504dc:
    cmp/eq #0x3,r0
    .org 0x504de-ORIGIN
L_000504de:
    bf L_000505ae
    .org 0x504e0-ORIGIN
L_000504e0:
    mov.l P_000506b4,r5
    .org 0x504e2-ORIGIN
L_000504e2:
    mov.b @r5,r0
    .org 0x504e4-ORIGIN
L_000504e4:
    tst #0x20,r0
    .org 0x504e6-ORIGIN
L_000504e6:
    bf L_00050596
    .org 0x504e8-ORIGIN
L_000504e8:
    mov.l P_000506b8,r2
    .org 0x504ea-ORIGIN
L_000504ea:
    mov.b @r2,r0
    .org 0x504ec-ORIGIN
L_000504ec:
    tst #0x2,r0
    .org 0x504ee-ORIGIN
L_000504ee:
    bf L_00050500
    .org 0x504f0-ORIGIN
L_000504f0:
    mov.l P_000506bc,r5
    .org 0x504f2-ORIGIN
L_000504f2:
    mov.b @r5,r0
    .org 0x504f4-ORIGIN
L_000504f4:
    tst #0x80,r0
    .org 0x504f6-ORIGIN
L_000504f6:
    bf L_00050596
    .org 0x504f8-ORIGIN
L_000504f8:
    mov.l P_000506c0,r5
    .org 0x504fa-ORIGIN
L_000504fa:
    mov.b @(0x1,r5),r0
    .org 0x504fc-ORIGIN
L_000504fc:
    tst #0x10,r0
    .org 0x504fe-ORIGIN
L_000504fe:
    bt L_00050596
    .org 0x50500-ORIGIN
L_00050500:
    mov.l P_000506c4,r2
    .org 0x50502-ORIGIN
L_00050502:
    mov #0x17,r0
    .org 0x50504-ORIGIN
L_00050504:
    mov.l P_000506c8,r4
    .org 0x50506-ORIGIN
L_00050506:
    mov.b @(r0,r2),r5
    .org 0x50508-ORIGIN
L_00050508:
    mov.b @(0x4,r4),r0
    .org 0x5050a-ORIGIN
L_0005050a:
    cmp/hi r0,r5
    .org 0x5050c-ORIGIN
L_0005050c:
    bt/s L_0005058e
    .org 0x5050e-ORIGIN
L_0005050e:
    mov #0x0,r11
    .org 0x50510-ORIGIN
L_00050510:
    mov.l P_000506bc,r5
    .org 0x50512-ORIGIN
L_00050512:
    mov.b @r5,r0
    .org 0x50514-ORIGIN
L_00050514:
    tst #0x80,r0
    .org 0x50516-ORIGIN
L_00050516:
    bt L_0005054a
    .org 0x50518-ORIGIN
L_00050518:
    mov.l P_000506c4,r3
    .org 0x5051a-ORIGIN
L_0005051a:
    mov.l P_000506cc,r2
    .org 0x5051c-ORIGIN
L_0005051c:
    mov.w @(0x1a,r3),r0
    .org 0x5051e-ORIGIN
L_0005051e:
    mov.l P_000506c8,r1
    .org 0x50520-ORIGIN
L_00050520:
    extu.w r0,r4
    .org 0x50522-ORIGIN
L_00050522:
    mov #0x7a,r0
    .org 0x50524-ORIGIN
L_00050524:
    mov.b @(r0,r2),r7
    .org 0x50526-ORIGIN
L_00050526:
    mov.b @(0x3,r1),r0
    .org 0x50528-ORIGIN
L_00050528:
    extu.b r7,r7
    .org 0x5052a-ORIGIN
L_0005052a:
    extu.b r0,r2
    .org 0x5052c-ORIGIN
L_0005052c:
    mul.l r7,r2
    .org 0x5052e-ORIGIN
L_0005052e:
    sts macl,r2
    .org 0x50530-ORIGIN
L_00050530:
    cmp/gt r2,r4
    .org 0x50532-ORIGIN
L_00050532:
    bf L_0005056e
    .org 0x50534-ORIGIN
L_00050534:
    mov.l P_000506c4,r3
    .org 0x50536-ORIGIN
L_00050536:
    mov.w @(0x1a,r3),r0
    .org 0x50538-ORIGIN
L_00050538:
    extu.w r0,r4
    .org 0x5053a-ORIGIN
L_0005053a:
    mov.b @(0x2,r1),r0
    .org 0x5053c-ORIGIN
L_0005053c:
    extu.b r0,r2
    .org 0x5053e-ORIGIN
L_0005053e:
    mul.l r7,r2
    .org 0x50540-ORIGIN
L_00050540:
    sts macl,r2
    .org 0x50542-ORIGIN
L_00050542:
    cmp/gt r2,r4
    .org 0x50544-ORIGIN
L_00050544:
    bf L_0005056a
    .org 0x50546-ORIGIN
L_00050546:
    bra L_00050570
    .org 0x50548-ORIGIN
L_00050548:
    nop
    .org 0x5054a-ORIGIN
L_0005054a:
    mov.w P_00050552,r0
    .org 0x5054c-ORIGIN
L_0005054c:
    mov.l P_000506c8,r3
    .org 0x5054e-ORIGIN
L_0005054e:
    bra L_00050554
    .org 0x50550-ORIGIN
L_00050550:
    nop
    .org 0x50552-ORIGIN
P_00050552:
    .byte 0x02
    .org 0x50553-ORIGIN
P_00050553:
    .byte 0x8b
    .org 0x50554-ORIGIN
L_00050554:
    mov.b @(r0,r9),r4
    .org 0x50556-ORIGIN
L_00050556:
    mov.b @r3,r2
    .org 0x50558-ORIGIN
L_00050558:
    extu.b r4,r4
    .org 0x5055a-ORIGIN
L_0005055a:
    extu.b r2,r2
    .org 0x5055c-ORIGIN
L_0005055c:
    cmp/ge r2,r4
    .org 0x5055e-ORIGIN
L_0005055e:
    bt L_0005056e
    .org 0x50560-ORIGIN
L_00050560:
    mov.l P_000506c8,r3
    .org 0x50562-ORIGIN
L_00050562:
    mov.b @(0x1,r3),r0
    .org 0x50564-ORIGIN
L_00050564:
    extu.b r0,r2
    .org 0x50566-ORIGIN
L_00050566:
    cmp/ge r2,r4
    .org 0x50568-ORIGIN
L_00050568:
    bf L_00050570
    .org 0x5056a-ORIGIN
L_0005056a:
    bra L_00050570
    .org 0x5056c-ORIGIN
L_0005056c:
    mov #0x1,r6
    .org 0x5056e-ORIGIN
L_0005056e:
    mov #0x2,r6
    .org 0x50570-ORIGIN
L_00050570:
    mov.w P_0005068c,r0
    .org 0x50572-ORIGIN
L_00050572:
    mov.l P_000506d0,r5
    .org 0x50574-ORIGIN
L_00050574:
    mov.b r6,@(r0,r9)
    .org 0x50576-ORIGIN
L_00050576:
    extu.b r6,r6
    .org 0x50578-ORIGIN
L_00050578:
    mov r6,r0
    .org 0x5057a-ORIGIN
L_0005057a:
    mov.b @(r0,r5),r2
    .org 0x5057c-ORIGIN
L_0005057c:
    mov.w P_0005068e,r0
    .org 0x5057e-ORIGIN
L_0005057e:
    mov.l P_000506d4,r5
    .org 0x50580-ORIGIN
L_00050580:
    mov.b r2,@(r0,r9)
    .org 0x50582-ORIGIN
L_00050582:
    mov r6,r0
    .org 0x50584-ORIGIN
L_00050584:
    mov.b @(r0,r5),r2
    .org 0x50586-ORIGIN
L_00050586:
    mov #-0x1,r6
    .org 0x50588-ORIGIN
L_00050588:
    mov.w P_00050690,r0
    .org 0x5058a-ORIGIN
L_0005058a:
    bra L_000505ae
    .org 0x5058c-ORIGIN
L_0005058c:
    mov.b r2,@(r0,r9)
    .org 0x5058e-ORIGIN
L_0005058e:
    mov.w P_0005068c,r0
    .org 0x50590-ORIGIN
L_00050590:
    mov #0xa,r2
    .org 0x50592-ORIGIN
L_00050592:
    bra L_0005059e
    .org 0x50594-ORIGIN
L_00050594:
    mov.b r2,@(r0,r9)
    .org 0x50596-ORIGIN
L_00050596:
    mov.l P_000506b0,r4
    .org 0x50598-ORIGIN
L_00050598:
    mov r7,r0
    .org 0x5059a-ORIGIN
L_0005059a:
    mov #0x4,r11
    .org 0x5059c-ORIGIN
L_0005059c:
    mov.b r0,@(0x9,r4)
    .org 0x5059e-ORIGIN
L_0005059e:
    mov.w P_0005068e,r0
    .org 0x505a0-ORIGIN
L_000505a0:
    mov #-0x1,r2
    .org 0x505a2-ORIGIN
L_000505a2:
    mov.b r2,@(r0,r9)
    .org 0x505a4-ORIGIN
L_000505a4:
    mov #0x0,r2
    .org 0x505a6-ORIGIN
L_000505a6:
    mov.w P_00050690,r0
    .org 0x505a8-ORIGIN
L_000505a8:
    mov.b r2,@(r0,r9)
    .org 0x505aa-ORIGIN
L_000505aa:
    mov.w P_00050692,r0
    .org 0x505ac-ORIGIN
L_000505ac:
    mov.b r2,@(r0,r9)
    .org 0x505ae-ORIGIN
L_000505ae:
    extu.b r11,r11
    .org 0x505b0-ORIGIN
L_000505b0:
    mov r11,r0
    .org 0x505b2-ORIGIN
L_000505b2:
    cmp/eq #0x4,r0
    .org 0x505b4-ORIGIN
L_000505b4:
    bf L_000505c0
    .org 0x505b6-ORIGIN
L_000505b6:
    mov.l P_000506b0,r4
    .org 0x505b8-ORIGIN
L_000505b8:
    mov.b @(0x9,r4),r0
    .org 0x505ba-ORIGIN
L_000505ba:
    tst r0,r0
    .org 0x505bc-ORIGIN
L_000505bc:
    bf L_000505c0
    .org 0x505be-ORIGIN
L_000505be:
    mov #0x0,r11
    .org 0x505c0-ORIGIN
L_000505c0:
    mov.w P_0005068e,r0
    .org 0x505c2-ORIGIN
L_000505c2:
    mov #-0x1,r4
    .org 0x505c4-ORIGIN
L_000505c4:
    extu.b r4,r4
    .org 0x505c6-ORIGIN
L_000505c6:
    mov.b @(r0,r9),r5
    .org 0x505c8-ORIGIN
L_000505c8:
    extu.b r5,r5
    .org 0x505ca-ORIGIN
L_000505ca:
    cmp/eq r4,r5
    .org 0x505cc-ORIGIN
L_000505cc:
    bt L_000505f6
    .org 0x505ce-ORIGIN
L_000505ce:
    extu.b r6,r6
    .org 0x505d0-ORIGIN
L_000505d0:
    cmp/eq r4,r6
    .org 0x505d2-ORIGIN
L_000505d2:
    bt L_000505de
    .org 0x505d4-ORIGIN
L_000505d4:
    tst r5,r5
    .org 0x505d6-ORIGIN
L_000505d6:
    bt L_000505de
    .org 0x505d8-ORIGIN
L_000505d8:
    add #-0x1,r5
    .org 0x505da-ORIGIN
L_000505da:
    extu.b r5,r5
    .org 0x505dc-ORIGIN
L_000505dc:
    mov.b r5,@(r0,r9)
    .org 0x505de-ORIGIN
L_000505de:
    extu.b r5,r5
    .org 0x505e0-ORIGIN
L_000505e0:
    tst r5,r5
    .org 0x505e2-ORIGIN
L_000505e2:
    bf L_000505f6
    .org 0x505e4-ORIGIN
L_000505e4:
    mov.w P_0005068e,r0
    .org 0x505e6-ORIGIN
L_000505e6:
    mov #-0x1,r2
    .org 0x505e8-ORIGIN
L_000505e8:
    mov.b r2,@(r0,r9)
    .org 0x505ea-ORIGIN
L_000505ea:
    mov.w P_00050690,r0
    .org 0x505ec-ORIGIN
L_000505ec:
    mov.b @(r0,r9),r2
    .org 0x505ee-ORIGIN
L_000505ee:
    mov.w P_00050692,r0
    .org 0x505f0-ORIGIN
L_000505f0:
    bra L_000505f6
    .org 0x505f2-ORIGIN
L_000505f2:
    mov.b r2,@(r0,r9)
    .org 0x505f4-ORIGIN
L_000505f4:
    mov #0x0,r11
    .org 0x505f6-ORIGIN
L_000505f6:
    mov.l P_000506d8,r6
    .org 0x505f8-ORIGIN
L_000505f8:
    mov.b @(0x4,r6),r0
    .org 0x505fa-ORIGIN
L_000505fa:
    tst #0x80,r0
    .org 0x505fc-ORIGIN
L_000505fc:
    bt L_0005060e
    .org 0x505fe-ORIGIN
L_000505fe:
    mov.w P_0005068e,r0
    .org 0x50600-ORIGIN
L_00050600:
    mov #-0x1,r2
    .org 0x50602-ORIGIN
L_00050602:
    mov.b r2,@(r0,r9)
    .org 0x50604-ORIGIN
L_00050604:
    mov #0x0,r2
    .org 0x50606-ORIGIN
L_00050606:
    mov.w P_00050690,r0
    .org 0x50608-ORIGIN
L_00050608:
    mov.b r2,@(r0,r9)
    .org 0x5060a-ORIGIN
L_0005060a:
    mov.w P_00050692,r0
    .org 0x5060c-ORIGIN
L_0005060c:
    mov.b r2,@(r0,r9)
    .org 0x5060e-ORIGIN
L_0005060e:
    mov.l P_000506b0,r4
    .org 0x50610-ORIGIN
L_00050610:
    mov #0x32,r0
    .org 0x50612-ORIGIN
L_00050612:
    mov.b @(r0,r4),r2
    .org 0x50614-ORIGIN
L_00050614:
    tst r2,r2
    .org 0x50616-ORIGIN
L_00050616:
    bt L_00050628
    .org 0x50618-ORIGIN
L_00050618:
    mov.w P_0005068e,r0
    .org 0x5061a-ORIGIN
L_0005061a:
    mov #-0x1,r2
    .org 0x5061c-ORIGIN
L_0005061c:
    mov.b r2,@(r0,r9)
    .org 0x5061e-ORIGIN
L_0005061e:
    mov #0x0,r2
    .org 0x50620-ORIGIN
L_00050620:
    mov.w P_00050690,r0
    .org 0x50622-ORIGIN
L_00050622:
    mov.b r2,@(r0,r9)
    .org 0x50624-ORIGIN
L_00050624:
    mov.w P_00050692,r0
    .org 0x50626-ORIGIN
L_00050626:
    mov.b r2,@(r0,r9)
    .org 0x50628-ORIGIN
L_00050628:
    mov.w P_00050694,r0
    .org 0x5062a-ORIGIN
L_0005062a:
    mov #0x6,r12
    .org 0x5062c-ORIGIN
L_0005062c:
    mov.b r11,@(r0,r9)
    .org 0x5062e-ORIGIN
L_0005062e:
    mov.w P_00050696,r0
    .org 0x50630-ORIGIN
L_00050630:
    mov.b @(r0,r9),r4
    .org 0x50632-ORIGIN
L_00050632:
    mov.w P_00050692,r0
    .org 0x50634-ORIGIN
L_00050634:
    extu.b r13,r13
    .org 0x50636-ORIGIN
L_00050636:
    mov.b @(r0,r9),r2
    .org 0x50638-ORIGIN
L_00050638:
    extu.b r2,r5
    .org 0x5063a-ORIGIN
L_0005063a:
    cmp/ge r5,r13
    .org 0x5063c-ORIGIN
L_0005063c:
    bt L_0005064e
    .org 0x5063e-ORIGIN
L_0005063e:
    add #0x1,r13
    .org 0x50640-ORIGIN
L_00050640:
    extu.b r4,r4
    .org 0x50642-ORIGIN
L_00050642:
    bsr L_00050766
    .org 0x50644-ORIGIN
L_00050644:
    extu.b r13,r13
    .org 0x50646-ORIGIN
L_00050646:
    cmp/ge r12,r13
    .org 0x50648-ORIGIN
L_00050648:
    mov r0,r4
    .org 0x5064a-ORIGIN
L_0005064a:
    bf/s L_00050632
    .org 0x5064c-ORIGIN
L_0005064c:
    or r0,r14
    .org 0x5064e-ORIGIN
L_0005064e:
    mov.w P_00050694,r0
    .org 0x50650-ORIGIN
L_00050650:
    mov.l P_000506dc,r2
    .org 0x50652-ORIGIN
L_00050652:
    mov.b @(r0,r9),r6
    .org 0x50654-ORIGIN
L_00050654:
    mov.l P_000506e0,r13
    .org 0x50656-ORIGIN
L_00050656:
    extu.b r6,r0
    .org 0x50658-ORIGIN
L_00050658:
    mov.b @(r0,r2),r6
    .org 0x5065a-ORIGIN
L_0005065a:
    mov #0x2f,r0
    .org 0x5065c-ORIGIN
L_0005065c:
    mov.b @(r0,r13),r4
    .org 0x5065e-ORIGIN
L_0005065e:
    mov r6,r2
    .org 0x50660-ORIGIN
L_00050660:
    or r14,r2
    .org 0x50662-ORIGIN
L_00050662:
    extu.b r2,r5
    .org 0x50664-ORIGIN
L_00050664:
    tst r5,r5
    .org 0x50666-ORIGIN
L_00050666:
    bf/s L_000506fc
    .org 0x50668-ORIGIN
L_00050668:
    extu.b r4,r2
    .org 0x5066a-ORIGIN
L_0005066a:
    mov.b @r10,r0
    .org 0x5066c-ORIGIN
L_0005066c:
    tst #0x40,r0
    .org 0x5066e-ORIGIN
L_0005066e:
    bf L_000506a4
    .org 0x50670-ORIGIN
L_00050670:
    mov r2,r0
    .org 0x50672-ORIGIN
L_00050672:
    tst #0x20,r0
    .org 0x50674-ORIGIN
L_00050674:
    bt L_000506a4
    .org 0x50676-ORIGIN
L_00050676:
    mov.l P_000506b4,r7
    .org 0x50678-ORIGIN
L_00050678:
    mov.b @r7,r0
    .org 0x5067a-ORIGIN
L_0005067a:
    tst #0x20,r0
    .org 0x5067c-ORIGIN
L_0005067c:
    bt L_00050698
    .org 0x5067e-ORIGIN
L_0005067e:
    mov r2,r0
    .org 0x50680-ORIGIN
L_00050680:
    or #0x80,r0
    .org 0x50682-ORIGIN
L_00050682:
    mov r0,r2
    .org 0x50684-ORIGIN
L_00050684:
    mov #0x2f,r0
    .org 0x50686-ORIGIN
L_00050686:
    mov.b r2,@(r0,r13)
    .org 0x50688-ORIGIN
L_00050688:
    bra L_000506a4
    .org 0x5068a-ORIGIN
L_0005068a:
    exts.b r2,r4
    .org 0x5068c-ORIGIN
P_0005068c:
    .byte 0x06
    .org 0x5068d-ORIGIN
P_0005068d:
    .byte 0xad
    .org 0x5068e-ORIGIN
P_0005068e:
    .byte 0x06
    .org 0x5068f-ORIGIN
P_0005068f:
    .byte 0xae
    .org 0x50690-ORIGIN
P_00050690:
    .byte 0x06
    .org 0x50691-ORIGIN
P_00050691:
    .byte 0xac
    .org 0x50692-ORIGIN
P_00050692:
    .byte 0x06
    .org 0x50693-ORIGIN
P_00050693:
    .byte 0xab
    .org 0x50694-ORIGIN
P_00050694:
    .byte 0x02
    .org 0x50695-ORIGIN
P_00050695:
    .byte 0x35
    .org 0x50696-ORIGIN
P_00050696:
    .byte 0x06
    .org 0x50697-ORIGIN
P_00050697:
    .byte 0xaa
    .org 0x50698-ORIGIN
L_00050698:
    mov #0x1f,r0
    .org 0x5069a-ORIGIN
L_0005069a:
    mov.b @(r0,r13),r0
    .org 0x5069c-ORIGIN
L_0005069c:
    or #0x40,r0
    .org 0x5069e-ORIGIN
L_0005069e:
    mov r0,r2
    .org 0x506a0-ORIGIN
L_000506a0:
    mov #0x1f,r0
    .org 0x506a2-ORIGIN
L_000506a2:
    mov.b r2,@(r0,r13)
    .org 0x506a4-ORIGIN
L_000506a4:
    mov.w P_000506ae,r0
    .org 0x506a6-ORIGIN
L_000506a6:
    mov #0x0,r2
    .org 0x506a8-ORIGIN
L_000506a8:
    mov.l P_000506e4,r5
    .org 0x506aa-ORIGIN
L_000506aa:
    bra L_000506e8
    .org 0x506ac-ORIGIN
L_000506ac:
    mov.b r2,@(r0,r9)
    .org 0x506ae-ORIGIN
P_000506ae:
    .byte 0x02
    .org 0x506af-ORIGIN
P_000506af:
    .byte 0x38
    .org 0x506b0-ORIGIN
P_000506b0:
    .byte 0xff
    .org 0x506b1-ORIGIN
P_000506b1:
    .byte 0xff
    .org 0x506b2-ORIGIN
P_000506b2:
    .byte 0x25
    .org 0x506b3-ORIGIN
P_000506b3:
    .byte 0x6a
    .org 0x506b4-ORIGIN
P_000506b4:
    .byte 0xff
    .org 0x506b5-ORIGIN
P_000506b5:
    .byte 0xff
    .org 0x506b6-ORIGIN
P_000506b6:
    .byte 0x24
    .org 0x506b7-ORIGIN
P_000506b7:
    .byte 0x58
    .org 0x506b8-ORIGIN
P_000506b8:
    .byte 0x00
    .org 0x506b9-ORIGIN
P_000506b9:
    .byte 0x00
    .org 0x506ba-ORIGIN
P_000506ba:
    .byte 0x87
    .org 0x506bb-ORIGIN
P_000506bb:
    .byte 0x11
    .org 0x506bc-ORIGIN
P_000506bc:
    .byte 0x00
    .org 0x506bd-ORIGIN
P_000506bd:
    .byte 0x00
    .org 0x506be-ORIGIN
P_000506be:
    .byte 0x8b
    .org 0x506bf-ORIGIN
P_000506bf:
    .byte 0x3f
    .org 0x506c0-ORIGIN
P_000506c0:
    .byte 0xff
    .org 0x506c1-ORIGIN
P_000506c1:
    .byte 0xff
    .org 0x506c2-ORIGIN
P_000506c2:
    .byte 0x24
    .org 0x506c3-ORIGIN
P_000506c3:
    .byte 0xce
    .org 0x506c4-ORIGIN
P_000506c4:
    .byte 0xff
    .org 0x506c5-ORIGIN
P_000506c5:
    .byte 0xff
    .org 0x506c6-ORIGIN
P_000506c6:
    .byte 0x11
    .org 0x506c7-ORIGIN
P_000506c7:
    .byte 0x9c
    .org 0x506c8-ORIGIN
P_000506c8:
    .byte 0x00
    .org 0x506c9-ORIGIN
P_000506c9:
    .byte 0x00
    .org 0x506ca-ORIGIN
P_000506ca:
    .byte 0x8c
    .org 0x506cb-ORIGIN
P_000506cb:
    .byte 0x1a
    .org 0x506cc-ORIGIN
P_000506cc:
    .byte 0xff
    .org 0x506cd-ORIGIN
P_000506cd:
    .byte 0xff
    .org 0x506ce-ORIGIN
P_000506ce:
    .byte 0x10
    .org 0x506cf-ORIGIN
P_000506cf:
    .byte 0x94
    .org 0x506d0-ORIGIN
P_000506d0:
    .byte 0x00
    .org 0x506d1-ORIGIN
P_000506d1:
    .byte 0x01
    .org 0x506d2-ORIGIN
P_000506d2:
    .byte 0x26
    .org 0x506d3-ORIGIN
P_000506d3:
    .byte 0x9d
    .org 0x506d4-ORIGIN
P_000506d4:
    .byte 0x00
    .org 0x506d5-ORIGIN
P_000506d5:
    .byte 0x01
    .org 0x506d6-ORIGIN
P_000506d6:
    .byte 0x26
    .org 0x506d7-ORIGIN
P_000506d7:
    .byte 0x9a
    .org 0x506d8-ORIGIN
P_000506d8:
    .byte 0xff
    .org 0x506d9-ORIGIN
P_000506d9:
    .byte 0xff
    .org 0x506da-ORIGIN
P_000506da:
    .byte 0x42
    .org 0x506db-ORIGIN
P_000506db:
    .byte 0x4c
    .org 0x506dc-ORIGIN
P_000506dc:
    .byte 0x00
    .org 0x506dd-ORIGIN
P_000506dd:
    .byte 0x02
    .org 0x506de-ORIGIN
P_000506de:
    .byte 0x37
    .org 0x506df-ORIGIN
P_000506df:
    .byte 0x1c
    .org 0x506e0-ORIGIN
P_000506e0:
    .byte 0xff
    .org 0x506e1-ORIGIN
P_000506e1:
    .byte 0xff
    .org 0x506e2-ORIGIN
P_000506e2:
    .byte 0x24
    .org 0x506e3-ORIGIN
P_000506e3:
    .byte 0x70
    .org 0x506e4-ORIGIN
P_000506e4:
    .byte 0x00
    .org 0x506e5-ORIGIN
P_000506e5:
    .byte 0x00
    .org 0x506e6-ORIGIN
P_000506e6:
    .byte 0x85
    .org 0x506e7-ORIGIN
P_000506e7:
    .byte 0xf6
    .org 0x506e8-ORIGIN
L_000506e8:
    mov r4,r0
    .org 0x506ea-ORIGIN
L_000506ea:
    and #0xdf,r0
    .org 0x506ec-ORIGIN
L_000506ec:
    mov r0,r2
    .org 0x506ee-ORIGIN
L_000506ee:
    mov #0x2f,r0
    .org 0x506f0-ORIGIN
L_000506f0:
    mov.b r2,@(r0,r13)
    .org 0x506f2-ORIGIN
L_000506f2:
    mov #0x22,r0
    .org 0x506f4-ORIGIN
L_000506f4:
    mov.b @r5,r2
    .org 0x506f6-ORIGIN
L_000506f6:
    mov.l P_000508e8,r5
    .org 0x506f8-ORIGIN
L_000506f8:
    bra L_0005074e
    .org 0x506fa-ORIGIN
L_000506fa:
    mov.b r2,@(r0,r5)
    .org 0x506fc-ORIGIN
L_000506fc:
    mov r2,r0
    .org 0x506fe-ORIGIN
L_000506fe:
    tst #0x20,r0
    .org 0x50700-ORIGIN
L_00050700:
    bf L_00050730
    .org 0x50702-ORIGIN
L_00050702:
    mov.l P_000508ec,r3
    .org 0x50704-ORIGIN
L_00050704:
    mov #0x7a,r0
    .org 0x50706-ORIGIN
L_00050706:
    mov #-0x2,r1
    .org 0x50708-ORIGIN
L_00050708:
    mov.b @(r0,r3),r5
    .org 0x5070a-ORIGIN
L_0005070a:
    mov #-0x3,r3
    .org 0x5070c-ORIGIN
L_0005070c:
    mov.w P_0005082a,r0
    .org 0x5070e-ORIGIN
L_0005070e:
    mov.b r5,@(r0,r9)
    .org 0x50710-ORIGIN
L_00050710:
    mov.w P_0005082c,r0
    .org 0x50712-ORIGIN
L_00050712:
    mov.b @(r0,r9),r7
    .org 0x50714-ORIGIN
L_00050714:
    mov.w P_0005082e,r0
    .org 0x50716-ORIGIN
L_00050716:
    extu.b r7,r7
    .org 0x50718-ORIGIN
L_00050718:
    mov.b @(r0,r9),r4
    .org 0x5071a-ORIGIN
L_0005071a:
    and r1,r7
    .org 0x5071c-ORIGIN
L_0005071c:
    extu.b r7,r5
    .org 0x5071e-ORIGIN
L_0005071e:
    mov.w P_0005082c,r0
    .org 0x50720-ORIGIN
L_00050720:
    extu.b r4,r4
    .org 0x50722-ORIGIN
L_00050722:
    and r1,r4
    .org 0x50724-ORIGIN
L_00050724:
    and r3,r5
    .org 0x50726-ORIGIN
L_00050726:
    mov.b r5,@(r0,r9)
    .org 0x50728-ORIGIN
L_00050728:
    extu.b r4,r5
    .org 0x5072a-ORIGIN
L_0005072a:
    mov.w P_0005082e,r0
    .org 0x5072c-ORIGIN
L_0005072c:
    and r3,r5
    .org 0x5072e-ORIGIN
L_0005072e:
    mov.b r5,@(r0,r9)
    .org 0x50730-ORIGIN
L_00050730:
    mov #0x20,r0
    .org 0x50732-ORIGIN
L_00050732:
    or r0,r2
    .org 0x50734-ORIGIN
L_00050734:
    mov #0x2f,r0
    .org 0x50736-ORIGIN
L_00050736:
    mov.b r2,@(r0,r13)
    .org 0x50738-ORIGIN
L_00050738:
    exts.b r2,r0
    .org 0x5073a-ORIGIN
L_0005073a:
    and #0x7f,r0
    .org 0x5073c-ORIGIN
L_0005073c:
    mov r0,r2
    .org 0x5073e-ORIGIN
L_0005073e:
    mov #0x2f,r0
    .org 0x50740-ORIGIN
L_00050740:
    mov.b r2,@(r0,r13)
    .org 0x50742-ORIGIN
L_00050742:
    mov #0x1f,r0
    .org 0x50744-ORIGIN
L_00050744:
    mov.b @(r0,r13),r0
    .org 0x50746-ORIGIN
L_00050746:
    and #0xbf,r0
    .org 0x50748-ORIGIN
L_00050748:
    mov r0,r2
    .org 0x5074a-ORIGIN
L_0005074a:
    mov #0x1f,r0
    .org 0x5074c-ORIGIN
L_0005074c:
    mov.b r2,@(r0,r13)
    .org 0x5074e-ORIGIN
L_0005074e:
    or r14,r6
    .org 0x50750-ORIGIN
L_00050750:
    extu.b r6,r0
    .org 0x50752-ORIGIN
L_00050752:
    add #0x4,r15
    .org 0x50754-ORIGIN
L_00050754:
    lds.l @r15+,macl
    .org 0x50756-ORIGIN
L_00050756:
    lds.l @r15+,pr
    .org 0x50758-ORIGIN
L_00050758:
    mov.l @r15+,r14
    .org 0x5075a-ORIGIN
L_0005075a:
    mov.l @r15+,r13
    .org 0x5075c-ORIGIN
L_0005075c:
    mov.l @r15+,r12
    .org 0x5075e-ORIGIN
L_0005075e:
    mov.l @r15+,r11
    .org 0x50760-ORIGIN
L_00050760:
    mov.l @r15+,r10
    .org 0x50762-ORIGIN
L_00050762:
    rts
    .org 0x50764-ORIGIN
L_00050764:
    mov.l @r15+,r9
    .org 0x50766-ORIGIN
L_00050766:
    extu.b r4,r0
    .org 0x50768-ORIGIN
L_00050768:
    cmp/eq #0x1,r0
    .org 0x5076a-ORIGIN
L_0005076a:
    bt/s L_00050796
    .org 0x5076c-ORIGIN
L_0005076c:
    mov #0x0,r2
    .org 0x5076e-ORIGIN
L_0005076e:
    cmp/eq #0x2,r0
    .org 0x50770-ORIGIN
L_00050770:
    bt L_00050792
    .org 0x50772-ORIGIN
L_00050772:
    cmp/eq #0x4,r0
    .org 0x50774-ORIGIN
L_00050774:
    bt L_0005078e
    .org 0x50776-ORIGIN
L_00050776:
    cmp/eq #0x8,r0
    .org 0x50778-ORIGIN
L_00050778:
    bt L_0005078a
    .org 0x5077a-ORIGIN
L_0005077a:
    cmp/eq #0x10,r0
    .org 0x5077c-ORIGIN
L_0005077c:
    bt L_00050786
    .org 0x5077e-ORIGIN
L_0005077e:
    cmp/eq #0x20,r0
    .org 0x50780-ORIGIN
L_00050780:
    bf L_00050798
    .org 0x50782-ORIGIN
L_00050782:
    bra L_00050798
    .org 0x50784-ORIGIN
L_00050784:
    mov #0x1,r2
    .org 0x50786-ORIGIN
L_00050786:
    bra L_00050798
    .org 0x50788-ORIGIN
L_00050788:
    mov #0x20,r2
    .org 0x5078a-ORIGIN
L_0005078a:
    bra L_00050798
    .org 0x5078c-ORIGIN
L_0005078c:
    mov #0x10,r2
    .org 0x5078e-ORIGIN
L_0005078e:
    bra L_00050798
    .org 0x50790-ORIGIN
L_00050790:
    mov #0x8,r2
    .org 0x50792-ORIGIN
L_00050792:
    bra L_00050798
    .org 0x50794-ORIGIN
L_00050794:
    mov #0x4,r2
    .org 0x50796-ORIGIN
L_00050796:
    mov #0x2,r2
    .org 0x50798-ORIGIN
L_00050798:
    rts
    .org 0x5079a-ORIGIN
L_0005079a:
    extu.b r2,r0
    .org 0x5082a-ORIGIN
P_0005082a:
    .byte 0x02
    .org 0x5082b-ORIGIN
P_0005082b:
    .byte 0x38
    .org 0x5082c-ORIGIN
P_0005082c:
    .byte 0x02
    .org 0x5082d-ORIGIN
P_0005082d:
    .byte 0xb0
    .org 0x5082e-ORIGIN
P_0005082e:
    .byte 0x05
    .org 0x5082f-ORIGIN
P_0005082f:
    .byte 0x31
    .org 0x508e8-ORIGIN
P_000508e8:
    .byte 0xff
    .org 0x508e9-ORIGIN
P_000508e9:
    .byte 0xff
    .org 0x508ea-ORIGIN
P_000508ea:
    .byte 0x24
    .org 0x508eb-ORIGIN
P_000508eb:
    .byte 0xf9
    .org 0x508ec-ORIGIN
P_000508ec:
    .byte 0xff
    .org 0x508ed-ORIGIN
P_000508ed:
    .byte 0xff
    .org 0x508ee-ORIGIN
P_000508ee:
    .byte 0x10
    .org 0x508ef-ORIGIN
P_000508ef:
    .byte 0x94
