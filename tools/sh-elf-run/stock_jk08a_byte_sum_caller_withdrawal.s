! Complete natural464DE byte-sum caller and exact implicit-byte-curve helpers.
! The26A80 entry is bound inside its complete normal26A60 exported parent.
    .text
    .balign 4
    .set ORIGIN,0x26370
    .org 0x26370-ORIGIN
L_00026370:
    mov.w P_00026382,r0
    .org 0x26372-ORIGIN
L_00026372:
    extu.b r5,r5
    .org 0x26374-ORIGIN
L_00026374:
    cmp/hs r0,r5
    .org 0x26376-ORIGIN
L_00026376:
    bt L_0002637e
    .org 0x26378-ORIGIN
L_00026378:
    mov.l P_00026384,r6
    .org 0x2637a-ORIGIN
L_0002637a:
    jmp @r6
    .org 0x2637c-ORIGIN
L_0002637c:
    mov #0x0,r3
    .org 0x2637e-ORIGIN
L_0002637e:
    rts
    .org 0x26380-ORIGIN
L_00026380:
    mov.b @(0x7,r4),r0
    .org 0x26382-ORIGIN
P_00026382:
    .byte 0x00
    .org 0x26383-ORIGIN
P_00026383:
    .byte 0xe0
    .org 0x26384-ORIGIN
P_00026384:
    .byte 0x00
    .org 0x26385-ORIGIN
P_00026385:
    .byte 0x02
    .org 0x26386-ORIGIN
P_00026386:
    .byte 0x6a
    .org 0x26387-ORIGIN
P_00026387:
    .byte 0x80
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
    .org 0x26a60-ORIGIN
L_00026a60:
    shlr r5
    .org 0x26a62-ORIGIN
L_00026a62:
    rotcr r3
    .org 0x26a64-ORIGIN
L_00026a64:
    shlr r5
    .org 0x26a66-ORIGIN
L_00026a66:
    rotcr r3
    .org 0x26a68-ORIGIN
L_00026a68:
    shlr r5
    .org 0x26a6a-ORIGIN
L_00026a6a:
    rotcr r3
    .org 0x26a6c-ORIGIN
L_00026a6c:
    shlr r5
    .org 0x26a6e-ORIGIN
L_00026a6e:
    rotcr r3
    .org 0x26a70-ORIGIN
L_00026a70:
    shlr r5
    .org 0x26a72-ORIGIN
L_00026a72:
    rotcr r3
    .org 0x26a74-ORIGIN
L_00026a74:
    shlr r5
    .org 0x26a76-ORIGIN
L_00026a76:
    rotcr r3
    .org 0x26a78-ORIGIN
L_00026a78:
    shlr r5
    .org 0x26a7a-ORIGIN
L_00026a7a:
    rotcr r3
    .org 0x26a7c-ORIGIN
L_00026a7c:
    shlr r5
    .org 0x26a7e-ORIGIN
L_00026a7e:
    rotcr r3
    .org 0x26a80-ORIGIN
L_00026a80:
    shlr r5
    .org 0x26a82-ORIGIN
L_00026a82:
    rotcr r3
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
    .byte 0x00
    .org 0x26abd-ORIGIN
P_00026abd:
    .byte 0x02
    .org 0x26abe-ORIGIN
P_00026abe:
    .byte 0x67
    .org 0x26abf-ORIGIN
P_00026abf:
    .byte 0x40
    .org 0x464de-ORIGIN
L_000464de:
    mov.l r14,@-r15
    .org 0x464e0-ORIGIN
L_000464e0:
    sts.l pr,@-r15
    .org 0x464e2-ORIGIN
L_000464e2:
    mov.l P_00046514,r2
    .org 0x464e4-ORIGIN
L_000464e4:
    mov #0x28,r5
    .org 0x464e6-ORIGIN
L_000464e6:
    mov.b @(0x8,r2),r0
    .org 0x464e8-ORIGIN
L_000464e8:
    extu.b r0,r6
    .org 0x464ea-ORIGIN
L_000464ea:
    cmp/ge r5,r6
    .org 0x464ec-ORIGIN
L_000464ec:
    bt L_000464f2
    .org 0x464ee-ORIGIN
L_000464ee:
    bra L_00046544
    .org 0x464f0-ORIGIN
L_000464f0:
    mov #0x0,r5
    .org 0x464f2-ORIGIN
L_000464f2:
    mov r6,r2
    .org 0x464f4-ORIGIN
L_000464f4:
    add #-0x28,r2
    .org 0x464f6-ORIGIN
L_000464f6:
    mov #-0x1,r5
    .org 0x464f8-ORIGIN
L_000464f8:
    shll2 r2
    .org 0x464fa-ORIGIN
L_000464fa:
    extu.b r5,r5
    .org 0x464fc-ORIGIN
L_000464fc:
    cmp/gt r5,r2
    .org 0x464fe-ORIGIN
L_000464fe:
    bf L_0004653c
    .org 0x46500-ORIGIN
L_00046500:
    bra L_00046542
    .org 0x46502-ORIGIN
L_00046502:
    mov r5,r2
    .org 0x46514-ORIGIN
P_00046514:
    .byte 0xff
    .org 0x46515-ORIGIN
P_00046515:
    .byte 0xff
    .org 0x46516-ORIGIN
P_00046516:
    .byte 0x22
    .org 0x46517-ORIGIN
P_00046517:
    .byte 0xdc
    .org 0x4653c-ORIGIN
L_0004653c:
    add #-0x28,r6
    .org 0x4653e-ORIGIN
L_0004653e:
    shll2 r6
    .org 0x46540-ORIGIN
L_00046540:
    mov r6,r2
    .org 0x46542-ORIGIN
L_00046542:
    mov r2,r5
    .org 0x46544-ORIGIN
L_00046544:
    mov.l P_000466d8,r4
    .org 0x46546-ORIGIN
L_00046546:
    mov.l P_000466dc,r2
    .org 0x46548-ORIGIN
L_00046548:
    mov.l P_000466e0,r14
    .org 0x4654a-ORIGIN
L_0004654a:
    jsr @r2
    .org 0x4654c-ORIGIN
L_0004654c:
    extu.b r5,r5
    .org 0x4654e-ORIGIN
L_0004654e:
    extu.b r0,r6
    .org 0x46550-ORIGIN
L_00046550:
    mov.w P_0004668a,r0
    .org 0x46552-ORIGIN
L_00046552:
    mov.b r6,@(r0,r14)
    .org 0x46554-ORIGIN
L_00046554:
    mov.w P_0004668c,r0
    .org 0x46556-ORIGIN
L_00046556:
    mov.b @(r0,r14),r7
    .org 0x46558-ORIGIN
L_00046558:
    mov.w P_0004668e,r0
    .org 0x4655a-ORIGIN
L_0004655a:
    extu.b r7,r7
    .org 0x4655c-ORIGIN
L_0004655c:
    mov.b @(r0,r14),r2
    .org 0x4655e-ORIGIN
L_0004655e:
    mov.w P_00046690,r0
    .org 0x46560-ORIGIN
L_00046560:
    extu.b r2,r5
    .org 0x46562-ORIGIN
L_00046562:
    mov r7,r2
    .org 0x46564-ORIGIN
L_00046564:
    mov.b @(r0,r14),r4
    .org 0x46566-ORIGIN
L_00046566:
    add r5,r2
    .org 0x46568-ORIGIN
L_00046568:
    mov.w P_00046692,r0
    .org 0x4656a-ORIGIN
L_0004656a:
    extu.b r4,r4
    .org 0x4656c-ORIGIN
L_0004656c:
    add r4,r2
    .org 0x4656e-ORIGIN
L_0004656e:
    cmp/gt r6,r4
    .org 0x46570-ORIGIN
L_00046570:
    mov.w r2,@(r0,r14)
    .org 0x46572-ORIGIN
L_00046572:
    bf/s L_00046578
    .org 0x46574-ORIGIN
L_00046574:
    mov r4,r2
    .org 0x46576-ORIGIN
L_00046576:
    mov r6,r2
    .org 0x46578-ORIGIN
L_00046578:
    mov.w P_00046694,r0
    .org 0x4657a-ORIGIN
L_0004657a:
    extu.w r2,r2
    .org 0x4657c-ORIGIN
L_0004657c:
    add r2,r7
    .org 0x4657e-ORIGIN
L_0004657e:
    mov.w @(r0,r14),r2
    .org 0x46580-ORIGIN
L_00046580:
    mov #-0x1,r5
    .org 0x46582-ORIGIN
L_00046582:
    extu.w r5,r5
    .org 0x46584-ORIGIN
L_00046584:
    extu.w r2,r2
    .org 0x46586-ORIGIN
L_00046586:
    add r7,r2
    .org 0x46588-ORIGIN
L_00046588:
    cmp/hi r5,r2
    .org 0x4658a-ORIGIN
L_0004658a:
    bf L_0004658e
    .org 0x4658c-ORIGIN
L_0004658c:
    mov r5,r2
    .org 0x4658e-ORIGIN
L_0004658e:
    mov.w P_00046696,r0
    .org 0x46590-ORIGIN
L_00046590:
    mov.w r2,@(r0,r14)
    .org 0x46592-ORIGIN
L_00046592:
    extu.w r2,r2
    .org 0x46594-ORIGIN
L_00046594:
    mov.w P_00046698,r0
    .org 0x46596-ORIGIN
L_00046596:
    mov.b @(r0,r14),r6
    .org 0x46598-ORIGIN
L_00046598:
    extu.b r6,r4
    .org 0x4659a-ORIGIN
L_0004659a:
    add r4,r2
    .org 0x4659c-ORIGIN
L_0004659c:
    cmp/hi r5,r2
    .org 0x4659e-ORIGIN
L_0004659e:
    bf/s L_000465a4
    .org 0x465a0-ORIGIN
L_000465a0:
    mov r2,r6
    .org 0x465a2-ORIGIN
L_000465a2:
    mov r5,r6
    .org 0x465a4-ORIGIN
L_000465a4:
    mov.w P_0004669a,r0
    .org 0x465a6-ORIGIN
L_000465a6:
    mov.w r6,@(r0,r14)
    .org 0x465a8-ORIGIN
L_000465a8:
    lds.l @r15+,pr
    .org 0x465aa-ORIGIN
L_000465aa:
    rts
    .org 0x465ac-ORIGIN
L_000465ac:
    mov.l @r15+,r14
    .org 0x4668a-ORIGIN
P_0004668a:
    .byte 0x04
    .org 0x4668b-ORIGIN
P_0004668b:
    .byte 0x8a
    .org 0x4668c-ORIGIN
P_0004668c:
    .byte 0x04
    .org 0x4668d-ORIGIN
P_0004668d:
    .byte 0xb5
    .org 0x4668e-ORIGIN
P_0004668e:
    .byte 0x04
    .org 0x4668f-ORIGIN
P_0004668f:
    .byte 0xc3
    .org 0x46690-ORIGIN
P_00046690:
    .byte 0x04
    .org 0x46691-ORIGIN
P_00046691:
    .byte 0xb6
    .org 0x46692-ORIGIN
P_00046692:
    .byte 0x04
    .org 0x46693-ORIGIN
P_00046693:
    .byte 0xb0
    .org 0x46694-ORIGIN
P_00046694:
    .byte 0x04
    .org 0x46695-ORIGIN
P_00046695:
    .byte 0xc0
    .org 0x46696-ORIGIN
P_00046696:
    .byte 0x04
    .org 0x46697-ORIGIN
P_00046697:
    .byte 0xb2
    .org 0x46698-ORIGIN
P_00046698:
    .byte 0x04
    .org 0x46699-ORIGIN
P_00046699:
    .byte 0xb4
    .org 0x4669a-ORIGIN
P_0004669a:
    .byte 0x04
    .org 0x4669b-ORIGIN
P_0004669b:
    .byte 0xbc
    .org 0x466d8-ORIGIN
P_000466d8:
    .byte 0x00
    .org 0x466d9-ORIGIN
P_000466d9:
    .byte 0x01
    .org 0x466da-ORIGIN
P_000466da:
    .byte 0x28
    .org 0x466db-ORIGIN
P_000466db:
    .byte 0xd8
    .org 0x466dc-ORIGIN
P_000466dc:
    .byte 0x00
    .org 0x466dd-ORIGIN
P_000466dd:
    .byte 0x02
    .org 0x466de-ORIGIN
P_000466de:
    .byte 0x63
    .org 0x466df-ORIGIN
P_000466df:
    .byte 0x70
    .org 0x466e0-ORIGIN
P_000466e0:
    .byte 0xff
    .org 0x466e1-ORIGIN
P_000466e1:
    .byte 0xff
    .org 0x466e2-ORIGIN
P_000466e2:
    .byte 0x12
    .org 0x466e3-ORIGIN
P_000466e3:
    .byte 0x8c
