! Complete stock third fuel-trim indexed word writer.
    .text
    .balign 4
    .set ORIGIN,0x5b534
    .org 0x5b534-ORIGIN
L_0005b534:
    mov.l r9,@-r15
    .org 0x5b536-ORIGIN
L_0005b536:
    mov.l r10,@-r15
    .org 0x5b538-ORIGIN
L_0005b538:
    mov.l r11,@-r15
    .org 0x5b53a-ORIGIN
L_0005b53a:
    mov.l r12,@-r15
    .org 0x5b53c-ORIGIN
L_0005b53c:
    mov.l r13,@-r15
    .org 0x5b53e-ORIGIN
L_0005b53e:
    mov.l r14,@-r15
    .org 0x5b540-ORIGIN
L_0005b540:
    mov.l P_0005b5e4,r6
    .org 0x5b542-ORIGIN
L_0005b542:
    extu.b r4,r5
    .org 0x5b544-ORIGIN
L_0005b544:
    mov r5,r10
    .org 0x5b546-ORIGIN
L_0005b546:
    shll r10
    .org 0x5b548-ORIGIN
L_0005b548:
    mov.b @r6,r0
    .org 0x5b54a-ORIGIN
L_0005b54a:
    mov r5,r4
    .org 0x5b54c-ORIGIN
L_0005b54c:
    add #0x1,r4
    .org 0x5b54e-ORIGIN
L_0005b54e:
    and #0x4,r0
    .org 0x5b550-ORIGIN
L_0005b550:
    tst r0,r0
    .org 0x5b552-ORIGIN
L_0005b552:
    bf/s L_0005b576
    .org 0x5b554-ORIGIN
L_0005b554:
    mov r0,r13
    .org 0x5b556-ORIGIN
L_0005b556:
    mov.l P_0005b5e0,r1
    .org 0x5b558-ORIGIN
L_0005b558:
    mov.w P_0005b5c2,r0
    .org 0x5b55a-ORIGIN
L_0005b55a:
    mov.b @(r0,r1),r2
    .org 0x5b55c-ORIGIN
L_0005b55c:
    extu.b r2,r2
    .org 0x5b55e-ORIGIN
L_0005b55e:
    tst r4,r2
    .org 0x5b560-ORIGIN
L_0005b560:
    bt L_0005b576
    .org 0x5b562-ORIGIN
L_0005b562:
    mov.w P_0005b5c4,r0
    .org 0x5b564-ORIGIN
L_0005b564:
    mov.b @(r0,r1),r2
    .org 0x5b566-ORIGIN
L_0005b566:
    extu.b r2,r2
    .org 0x5b568-ORIGIN
L_0005b568:
    tst r4,r2
    .org 0x5b56a-ORIGIN
L_0005b56a:
    bf L_0005b5a4
    .org 0x5b56c-ORIGIN
L_0005b56c:
    mov.w P_0005b5c6,r0
    .org 0x5b56e-ORIGIN
L_0005b56e:
    mov.b @(r0,r1),r2
    .org 0x5b570-ORIGIN
L_0005b570:
    extu.b r2,r2
    .org 0x5b572-ORIGIN
L_0005b572:
    tst r4,r2
    .org 0x5b574-ORIGIN
L_0005b574:
    bf L_0005b5a4
    .org 0x5b576-ORIGIN
L_0005b576:
    tst r13,r13
    .org 0x5b578-ORIGIN
L_0005b578:
    bf L_0005b57e
    .org 0x5b57a-ORIGIN
L_0005b57a:
    bra L_0005b66a
    .org 0x5b57c-ORIGIN
L_0005b57c:
    nop
    .org 0x5b57e-ORIGIN
L_0005b57e:
    mov.l P_0005b5e0,r1
    .org 0x5b580-ORIGIN
L_0005b580:
    mov.w P_0005b5c2,r0
    .org 0x5b582-ORIGIN
L_0005b582:
    mov.b @(r0,r1),r0
    .org 0x5b584-ORIGIN
L_0005b584:
    tst #0x1,r0
    .org 0x5b586-ORIGIN
L_0005b586:
    bt L_0005b66a
    .org 0x5b588-ORIGIN
L_0005b588:
    tst #0x2,r0
    .org 0x5b58a-ORIGIN
L_0005b58a:
    bt L_0005b66a
    .org 0x5b58c-ORIGIN
L_0005b58c:
    mov.w P_0005b5c4,r0
    .org 0x5b58e-ORIGIN
L_0005b58e:
    mov.b @(r0,r1),r0
    .org 0x5b590-ORIGIN
L_0005b590:
    tst #0x1,r0
    .org 0x5b592-ORIGIN
L_0005b592:
    bt L_0005b598
    .org 0x5b594-ORIGIN
L_0005b594:
    tst #0x2,r0
    .org 0x5b596-ORIGIN
L_0005b596:
    bf L_0005b5a4
    .org 0x5b598-ORIGIN
L_0005b598:
    mov.w P_0005b5c6,r0
    .org 0x5b59a-ORIGIN
L_0005b59a:
    mov.b @(r0,r1),r0
    .org 0x5b59c-ORIGIN
L_0005b59c:
    tst #0x1,r0
    .org 0x5b59e-ORIGIN
L_0005b59e:
    bt L_0005b66a
    .org 0x5b5a0-ORIGIN
L_0005b5a0:
    tst #0x2,r0
    .org 0x5b5a2-ORIGIN
L_0005b5a2:
    bt L_0005b66a
    .org 0x5b5a4-ORIGIN
L_0005b5a4:
    mov.l P_0005b5cc,r2
    .org 0x5b5a6-ORIGIN
L_0005b5a6:
    mov #0x1c,r0
    .org 0x5b5a8-ORIGIN
L_0005b5a8:
    mov.l P_0005b5f4,r11
    .org 0x5b5aa-ORIGIN
L_0005b5aa:
    mov.b @(r0,r2),r6
    .org 0x5b5ac-ORIGIN
L_0005b5ac:
    mov r10,r0
    .org 0x5b5ae-ORIGIN
L_0005b5ae:
    mov.w @(r0,r11),r2
    .org 0x5b5b0-ORIGIN
L_0005b5b0:
    mov #0x1c,r0
    .org 0x5b5b2-ORIGIN
L_0005b5b2:
    extu.b r6,r6
    .org 0x5b5b4-ORIGIN
L_0005b5b4:
    mov.l P_0005b5e8,r5
    .org 0x5b5b6-ORIGIN
L_0005b5b6:
    tst r4,r6
    .org 0x5b5b8-ORIGIN
L_0005b5b8:
    extu.w r2,r2
    .org 0x5b5ba-ORIGIN
L_0005b5ba:
    bt/s L_0005b61a
    .org 0x5b5bc-ORIGIN
L_0005b5bc:
    mov.b @(r0,r5),r6
    .org 0x5b5be-ORIGIN
L_0005b5be:
    bra L_0005b5f8
    .org 0x5b5c0-ORIGIN
L_0005b5c0:
    nop
    .org 0x5b5c2-ORIGIN
P_0005b5c2:
    .byte 0x09
    .org 0x5b5c3-ORIGIN
P_0005b5c3:
    .byte 0x92
    .org 0x5b5c4-ORIGIN
P_0005b5c4:
    .byte 0x09
    .org 0x5b5c5-ORIGIN
P_0005b5c5:
    .byte 0x93
    .org 0x5b5c6-ORIGIN
P_0005b5c6:
    .byte 0x09
    .org 0x5b5c7-ORIGIN
P_0005b5c7:
    .byte 0x96
    .org 0x5b5cc-ORIGIN
P_0005b5cc:
    .byte 0xff
    .org 0x5b5cd-ORIGIN
P_0005b5cd:
    .byte 0xff
    .org 0x5b5ce-ORIGIN
P_0005b5ce:
    .byte 0x28
    .org 0x5b5cf-ORIGIN
P_0005b5cf:
    .byte 0xc8
    .org 0x5b5e0-ORIGIN
P_0005b5e0:
    .byte 0xff
    .org 0x5b5e1-ORIGIN
P_0005b5e1:
    .byte 0xff
    .org 0x5b5e2-ORIGIN
P_0005b5e2:
    .byte 0x28
    .org 0x5b5e3-ORIGIN
P_0005b5e3:
    .byte 0xf8
    .org 0x5b5e4-ORIGIN
P_0005b5e4:
    .byte 0x00
    .org 0x5b5e5-ORIGIN
P_0005b5e5:
    .byte 0x00
    .org 0x5b5e6-ORIGIN
P_0005b5e6:
    .byte 0x8b
    .org 0x5b5e7-ORIGIN
P_0005b5e7:
    .byte 0x2a
    .org 0x5b5e8-ORIGIN
P_0005b5e8:
    .byte 0xff
    .org 0x5b5e9-ORIGIN
P_0005b5e9:
    .byte 0xff
    .org 0x5b5ea-ORIGIN
P_0005b5ea:
    .byte 0x28
    .org 0x5b5eb-ORIGIN
P_0005b5eb:
    .byte 0x98
    .org 0x5b5f4-ORIGIN
P_0005b5f4:
    .byte 0xff
    .org 0x5b5f5-ORIGIN
P_0005b5f5:
    .byte 0xff
    .org 0x5b5f6-ORIGIN
P_0005b5f6:
    .byte 0x2a
    .org 0x5b5f7-ORIGIN
P_0005b5f7:
    .byte 0x24
    .org 0x5b5f8-ORIGIN
L_0005b5f8:
    extu.b r6,r6
    .org 0x5b5fa-ORIGIN
L_0005b5fa:
    tst r4,r6
    .org 0x5b5fc-ORIGIN
L_0005b5fc:
    bf L_0005b60a
    .org 0x5b5fe-ORIGIN
L_0005b5fe:
    mov.l P_0005b7a8,r6
    .org 0x5b600-ORIGIN
L_0005b600:
    mov.b @r6,r5
    .org 0x5b602-ORIGIN
L_0005b602:
    extu.b r5,r5
    .org 0x5b604-ORIGIN
L_0005b604:
    shll2 r5
    .org 0x5b606-ORIGIN
L_0005b606:
    bra L_0005b63c
    .org 0x5b608-ORIGIN
L_0005b608:
    shll2 r5
    .org 0x5b60a-ORIGIN
L_0005b60a:
    mov.l P_0005b7ac,r6
    .org 0x5b60c-ORIGIN
L_0005b60c:
    mov.b @r6,r4
    .org 0x5b60e-ORIGIN
L_0005b60e:
    extu.b r4,r4
    .org 0x5b610-ORIGIN
L_0005b610:
    cmp/gt r4,r2
    .org 0x5b612-ORIGIN
L_0005b612:
    bf L_0005b632
    .org 0x5b614-ORIGIN
L_0005b614:
    sub r4,r2
    .org 0x5b616-ORIGIN
L_0005b616:
    bra L_0005b640
    .org 0x5b618-ORIGIN
L_0005b618:
    mov r2,r4
    .org 0x5b61a-ORIGIN
L_0005b61a:
    extu.b r6,r5
    .org 0x5b61c-ORIGIN
L_0005b61c:
    tst r4,r5
    .org 0x5b61e-ORIGIN
L_0005b61e:
    bt L_0005b636
    .org 0x5b620-ORIGIN
L_0005b620:
    mov.l P_0005b7b0,r5
    .org 0x5b622-ORIGIN
L_0005b622:
    mov.b @r5,r6
    .org 0x5b624-ORIGIN
L_0005b624:
    extu.b r6,r5
    .org 0x5b626-ORIGIN
L_0005b626:
    shll2 r5
    .org 0x5b628-ORIGIN
L_0005b628:
    shll2 r5
    .org 0x5b62a-ORIGIN
L_0005b62a:
    cmp/hi r5,r2
    .org 0x5b62c-ORIGIN
L_0005b62c:
    bf L_0005b632
    .org 0x5b62e-ORIGIN
L_0005b62e:
    bra L_0005b63e
    .org 0x5b630-ORIGIN
L_0005b630:
    sub r5,r2
    .org 0x5b632-ORIGIN
L_0005b632:
    bra L_0005b640
    .org 0x5b634-ORIGIN
L_0005b634:
    mov #0x0,r4
    .org 0x5b636-ORIGIN
L_0005b636:
    mov.l P_0005b7b4,r5
    .org 0x5b638-ORIGIN
L_0005b638:
    mov.b @r5,r6
    .org 0x5b63a-ORIGIN
L_0005b63a:
    extu.b r6,r5
    .org 0x5b63c-ORIGIN
L_0005b63c:
    add r5,r2
    .org 0x5b63e-ORIGIN
L_0005b63e:
    mov r2,r4
    .org 0x5b640-ORIGIN
L_0005b640:
    mov.l P_0005b7b8,r2
    .org 0x5b642-ORIGIN
L_0005b642:
    mov.b @r2,r6
    .org 0x5b644-ORIGIN
L_0005b644:
    extu.b r6,r6
    .org 0x5b646-ORIGIN
L_0005b646:
    mov r6,r2
    .org 0x5b648-ORIGIN
L_0005b648:
    shll8 r2
    .org 0x5b64a-ORIGIN
L_0005b64a:
    cmp/hi r2,r4
    .org 0x5b64c-ORIGIN
L_0005b64c:
    bf L_0005b652
    .org 0x5b64e-ORIGIN
L_0005b64e:
    bra L_0005b654
    .org 0x5b650-ORIGIN
L_0005b650:
    shll8 r6
    .org 0x5b652-ORIGIN
L_0005b652:
    mov r4,r6
    .org 0x5b654-ORIGIN
L_0005b654:
    mov.l P_0005b7bc,r2
    .org 0x5b656-ORIGIN
L_0005b656:
    mov.b @r2,r5
    .org 0x5b658-ORIGIN
L_0005b658:
    extu.b r5,r5
    .org 0x5b65a-ORIGIN
L_0005b65a:
    mov r5,r2
    .org 0x5b65c-ORIGIN
L_0005b65c:
    shll8 r2
    .org 0x5b65e-ORIGIN
L_0005b65e:
    cmp/hs r2,r6
    .org 0x5b660-ORIGIN
L_0005b660:
    bt L_0005b666
    .org 0x5b662-ORIGIN
L_0005b662:
    shll8 r5
    .org 0x5b664-ORIGIN
L_0005b664:
    mov r5,r6
    .org 0x5b666-ORIGIN
L_0005b666:
    bra L_0005b6ea
    .org 0x5b668-ORIGIN
L_0005b668:
    mov r6,r2
    .org 0x5b66a-ORIGIN
L_0005b66a:
    mov.l P_0005b7c0,r1
    .org 0x5b66c-ORIGIN
L_0005b66c:
    mov.w P_0005b704,r0
    .org 0x5b66e-ORIGIN
L_0005b66e:
    mov.l P_0005b7c4,r11
    .org 0x5b670-ORIGIN
L_0005b670:
    mov.b @(r0,r1),r2
    .org 0x5b672-ORIGIN
L_0005b672:
    extu.b r2,r6
    .org 0x5b674-ORIGIN
L_0005b674:
    tst r4,r6
    .org 0x5b676-ORIGIN
L_0005b676:
    bf L_0005b688
    .org 0x5b678-ORIGIN
L_0005b678:
    mov.w P_0005b706,r0
    .org 0x5b67a-ORIGIN
L_0005b67a:
    mov.b @(r0,r1),r2
    .org 0x5b67c-ORIGIN
L_0005b67c:
    extu.b r2,r2
    .org 0x5b67e-ORIGIN
L_0005b67e:
    tst r4,r2
    .org 0x5b680-ORIGIN
L_0005b680:
    bf L_0005b688
    .org 0x5b682-ORIGIN
L_0005b682:
    mov #0x64,r2
    .org 0x5b684-ORIGIN
L_0005b684:
    bra L_0005b6ea
    .org 0x5b686-ORIGIN
L_0005b686:
    shll8 r2
    .org 0x5b688-ORIGIN
L_0005b688:
    mov.l P_0005b7c8,r9
    .org 0x5b68a-ORIGIN
L_0005b68a:
    mov r5,r0
    .org 0x5b68c-ORIGIN
L_0005b68c:
    shll2 r0
    .org 0x5b68e-ORIGIN
L_0005b68e:
    mov.l P_0005b7cc,r2
    .org 0x5b690-ORIGIN
L_0005b690:
    mov.l @(r0,r9),r14
    .org 0x5b692-ORIGIN
L_0005b692:
    mov #0x64,r7
    .org 0x5b694-ORIGIN
L_0005b694:
    shll8 r7
    .org 0x5b696-ORIGIN
L_0005b696:
    mov.b @r2,r4
    .org 0x5b698-ORIGIN
L_0005b698:
    cmp/ge r7,r14
    .org 0x5b69a-ORIGIN
L_0005b69a:
    mov r0,r12
    .org 0x5b69c-ORIGIN
L_0005b69c:
    extu.b r4,r4
    .org 0x5b69e-ORIGIN
L_0005b69e:
    bt/s L_0005b6be
    .org 0x5b6a0-ORIGIN
L_0005b6a0:
    mov r14,r2
    .org 0x5b6a2-ORIGIN
L_0005b6a2:
    add r4,r2
    .org 0x5b6a4-ORIGIN
L_0005b6a4:
    cmp/gt r7,r2
    .org 0x5b6a6-ORIGIN
L_0005b6a6:
    bt L_0005b6ac
    .org 0x5b6a8-ORIGIN
L_0005b6a8:
    add r4,r14
    .org 0x5b6aa-ORIGIN
L_0005b6aa:
    mov r14,r7
    .org 0x5b6ac-ORIGIN
L_0005b6ac:
    mov #0x64,r6
    .org 0x5b6ae-ORIGIN
L_0005b6ae:
    mov r7,r2
    .org 0x5b6b0-ORIGIN
L_0005b6b0:
    shll8 r6
    .org 0x5b6b2-ORIGIN
L_0005b6b2:
    mov r12,r0
    .org 0x5b6b4-ORIGIN
L_0005b6b4:
    cmp/eq r6,r7
    .org 0x5b6b6-ORIGIN
L_0005b6b6:
    bt/s L_0005b6d6
    .org 0x5b6b8-ORIGIN
L_0005b6b8:
    mov.l r7,@(r0,r9)
    .org 0x5b6ba-ORIGIN
L_0005b6ba:
    bra L_0005b6ea
    .org 0x5b6bc-ORIGIN
L_0005b6bc:
    nop
    .org 0x5b6be-ORIGIN
L_0005b6be:
    sub r4,r2
    .org 0x5b6c0-ORIGIN
L_0005b6c0:
    cmp/ge r7,r2
    .org 0x5b6c2-ORIGIN
L_0005b6c2:
    bf L_0005b6c8
    .org 0x5b6c4-ORIGIN
L_0005b6c4:
    sub r4,r14
    .org 0x5b6c6-ORIGIN
L_0005b6c6:
    mov r14,r7
    .org 0x5b6c8-ORIGIN
L_0005b6c8:
    mov #0x64,r6
    .org 0x5b6ca-ORIGIN
L_0005b6ca:
    mov r7,r2
    .org 0x5b6cc-ORIGIN
L_0005b6cc:
    shll8 r6
    .org 0x5b6ce-ORIGIN
L_0005b6ce:
    mov r12,r0
    .org 0x5b6d0-ORIGIN
L_0005b6d0:
    cmp/eq r6,r7
    .org 0x5b6d2-ORIGIN
L_0005b6d2:
    bf/s L_0005b6ea
    .org 0x5b6d4-ORIGIN
L_0005b6d4:
    mov.l r7,@(r0,r9)
    .org 0x5b6d6-ORIGIN
L_0005b6d6:
    mov.w P_0005b704,r0
    .org 0x5b6d8-ORIGIN
L_0005b6d8:
    add #0x1,r5
    .org 0x5b6da-ORIGIN
L_0005b6da:
    not r5,r5
    .org 0x5b6dc-ORIGIN
L_0005b6dc:
    mov.b @(r0,r1),r6
    .org 0x5b6de-ORIGIN
L_0005b6de:
    and r5,r6
    .org 0x5b6e0-ORIGIN
L_0005b6e0:
    mov.b r6,@(r0,r1)
    .org 0x5b6e2-ORIGIN
L_0005b6e2:
    mov.w P_0005b706,r0
    .org 0x5b6e4-ORIGIN
L_0005b6e4:
    mov.b @(r0,r1),r6
    .org 0x5b6e6-ORIGIN
L_0005b6e6:
    and r5,r6
    .org 0x5b6e8-ORIGIN
L_0005b6e8:
    mov.b r6,@(r0,r1)
    .org 0x5b6ea-ORIGIN
L_0005b6ea:
    tst r13,r13
    .org 0x5b6ec-ORIGIN
L_0005b6ec:
    mov r10,r0
    .org 0x5b6ee-ORIGIN
L_0005b6ee:
    bt/s L_0005b6f6
    .org 0x5b6f0-ORIGIN
L_0005b6f0:
    mov.w r2,@(r0,r11)
    .org 0x5b6f2-ORIGIN
L_0005b6f2:
    mov r2,r0
    .org 0x5b6f4-ORIGIN
L_0005b6f4:
    mov.w r0,@(0x2,r11)
    .org 0x5b6f6-ORIGIN
L_0005b6f6:
    mov.l @r15+,r14
    .org 0x5b6f8-ORIGIN
L_0005b6f8:
    mov.l @r15+,r13
    .org 0x5b6fa-ORIGIN
L_0005b6fa:
    mov.l @r15+,r12
    .org 0x5b6fc-ORIGIN
L_0005b6fc:
    mov.l @r15+,r11
    .org 0x5b6fe-ORIGIN
L_0005b6fe:
    mov.l @r15+,r10
    .org 0x5b700-ORIGIN
L_0005b700:
    rts
    .org 0x5b702-ORIGIN
L_0005b702:
    mov.l @r15+,r9
    .org 0x5b704-ORIGIN
P_0005b704:
    .byte 0x09
    .org 0x5b705-ORIGIN
P_0005b705:
    .byte 0x94
    .org 0x5b706-ORIGIN
P_0005b706:
    .byte 0x09
    .org 0x5b707-ORIGIN
P_0005b707:
    .byte 0x90
    .org 0x5b7a8-ORIGIN
P_0005b7a8:
    .byte 0x00
    .org 0x5b7a9-ORIGIN
P_0005b7a9:
    .byte 0x00
    .org 0x5b7aa-ORIGIN
P_0005b7aa:
    .byte 0x89
    .org 0x5b7ab-ORIGIN
P_0005b7ab:
    .byte 0x98
    .org 0x5b7ac-ORIGIN
P_0005b7ac:
    .byte 0x00
    .org 0x5b7ad-ORIGIN
P_0005b7ad:
    .byte 0x00
    .org 0x5b7ae-ORIGIN
P_0005b7ae:
    .byte 0x86
    .org 0x5b7af-ORIGIN
P_0005b7af:
    .byte 0xf7
    .org 0x5b7b0-ORIGIN
P_0005b7b0:
    .byte 0x00
    .org 0x5b7b1-ORIGIN
P_0005b7b1:
    .byte 0x00
    .org 0x5b7b2-ORIGIN
P_0005b7b2:
    .byte 0x89
    .org 0x5b7b3-ORIGIN
P_0005b7b3:
    .byte 0x97
    .org 0x5b7b4-ORIGIN
P_0005b7b4:
    .byte 0x00
    .org 0x5b7b5-ORIGIN
P_0005b7b5:
    .byte 0x00
    .org 0x5b7b6-ORIGIN
P_0005b7b6:
    .byte 0x86
    .org 0x5b7b7-ORIGIN
P_0005b7b7:
    .byte 0xf6
    .org 0x5b7b8-ORIGIN
P_0005b7b8:
    .byte 0x00
    .org 0x5b7b9-ORIGIN
P_0005b7b9:
    .byte 0x00
    .org 0x5b7ba-ORIGIN
P_0005b7ba:
    .byte 0x82
    .org 0x5b7bb-ORIGIN
P_0005b7bb:
    .byte 0xe5
    .org 0x5b7bc-ORIGIN
P_0005b7bc:
    .byte 0x00
    .org 0x5b7bd-ORIGIN
P_0005b7bd:
    .byte 0x00
    .org 0x5b7be-ORIGIN
P_0005b7be:
    .byte 0x82
    .org 0x5b7bf-ORIGIN
P_0005b7bf:
    .byte 0xe4
    .org 0x5b7c0-ORIGIN
P_0005b7c0:
    .byte 0xff
    .org 0x5b7c1-ORIGIN
P_0005b7c1:
    .byte 0xff
    .org 0x5b7c2-ORIGIN
P_0005b7c2:
    .byte 0x28
    .org 0x5b7c3-ORIGIN
P_0005b7c3:
    .byte 0xf8
    .org 0x5b7c4-ORIGIN
P_0005b7c4:
    .byte 0xff
    .org 0x5b7c5-ORIGIN
P_0005b7c5:
    .byte 0xff
    .org 0x5b7c6-ORIGIN
P_0005b7c6:
    .byte 0x2a
    .org 0x5b7c7-ORIGIN
P_0005b7c7:
    .byte 0x24
    .org 0x5b7c8-ORIGIN
P_0005b7c8:
    .byte 0xff
    .org 0x5b7c9-ORIGIN
P_0005b7c9:
    .byte 0xff
    .org 0x5b7ca-ORIGIN
P_0005b7ca:
    .byte 0x33
    .org 0x5b7cb-ORIGIN
P_0005b7cb:
    .byte 0x10
    .org 0x5b7cc-ORIGIN
P_0005b7cc:
    .byte 0x00
    .org 0x5b7cd-ORIGIN
P_0005b7cd:
    .byte 0x00
    .org 0x5b7ce-ORIGIN
P_0005b7ce:
    .byte 0x86
    .org 0x5b7cf-ORIGIN
P_0005b7cf:
    .byte 0xf5
