! Exact natural enrichment prefix, explicit axes and actual surface/correction kernels.
    .text
    .balign 4
    .org 0x8b9b - 0x8b98
L_00008b9b:
    .byte 0x82
    .org 0x8b9f - 0x8b98
L_00008b9f:
    .byte 0x81
    .org 0xa9aa - 0x8b98
L_0000a9aa:
    .byte 0x80,0x80,0x80,0x80,0x80,0x80,0x80,0x8e,0x80,0x80,0x80,0x80,0x80,0x80,0x80,0x92,0x80,0x80,0x80,0x80,0x80,0x80,0x80,0x92,0x80,0x80,0x80,0x80,0x8a,0x92,0x92,0x95,0x80,0x80,0x80,0x8a,0x8a,0x92,0x92,0x95,0x80,0x80,0x80,0x8a,0x8e,0x95,0x95,0x95,0x80,0x80,0x8e,0x8e,0x90,0x95,0x95,0x95,0x80,0x8c,0x90,0x92,0x93,0x95,0x95,0x95
    .org 0x11ac7 - 0x8b98
L_00011ac7:
    .byte 0x50,0x58,0x68,0x70,0x78,0x80,0x87,0x95
    .org 0x11cc0 - 0x8b98
L_00011cc0:
    .byte 0x30,0x38,0x40,0x50,0x68,0x70,0x78,0x88
    .org 0x11cd8 - 0x8b98
L_00011cd8:
    .byte 0x00,0x10,0x20,0x30,0x40,0x50,0x60,0x70
    .org 0x1214e - 0x8b98
L_0001214e:
    .byte 0xc8,0xc8,0xc8,0xc8,0xc8,0xc8,0xc8,0xc8,0xc8,0xc8,0xc8,0xc8,0xc8,0xc8,0xc8,0xc8
    .org 0x12552 - 0x8b98
L_00012552:
    .byte 0x80,0x80,0x80,0x80,0x80,0x80,0x9a,0x9a,0x28
    .org 0x224f8 - 0x8b98
L_000224f8:
    shar r0
    .org 0x224fa - 0x8b98
L_000224fa:
    shar r0
    .org 0x224fc - 0x8b98
L_000224fc:
    shar r0
    .org 0x224fe - 0x8b98
L_000224fe:
    shar r0
    .org 0x22500 - 0x8b98
L_00022500:
    shar r0
    .org 0x22502 - 0x8b98
L_00022502:
    shar r0
    .org 0x22504 - 0x8b98
L_00022504:
    rts
    .org 0x22506 - 0x8b98
L_00022506:
    shar r0
    .org 0x26178 - 0x8b98
L_00026178:
    sts.l pr,@-r15
    .org 0x2617a - 0x8b98
L_0002617a:
    mov.l r4,@-r15
    .org 0x2617c - 0x8b98
L_0002617c:
    extu.w r7,r7
    .org 0x2617e - 0x8b98
L_0002617e:
    mov r5,r0
    .org 0x26180 - 0x8b98
L_00026180:
    mov r7,r5
    .org 0x26182 - 0x8b98
L_00026182:
    mov.l L_000261b4,r7
    .org 0x26184 - 0x8b98
L_00026184:
    jsr @r7
    .org 0x26186 - 0x8b98
L_00026186:
    mov #0x7,r4
    .org 0x26188 - 0x8b98
L_00026188:
    mov.l r5,@-r15
    .org 0x2618a - 0x8b98
L_0002618a:
    mov.l r4,@-r15
    .org 0x2618c - 0x8b98
L_0002618c:
    mov r6,r0
    .org 0x2618e - 0x8b98
L_0002618e:
    mov.l @(0x10,r15),r5
    .org 0x26190 - 0x8b98
L_00026190:
    extu.b r5,r5
    .org 0x26192 - 0x8b98
L_00026192:
    mov.l L_000261b0,r7
    .org 0x26194 - 0x8b98
L_00026194:
    jsr @r7
    .org 0x26196 - 0x8b98
L_00026196:
    mov #0x7,r4
    .org 0x26198 - 0x8b98
L_00026198:
    mov.l @r15+,r0
    .org 0x2619a - 0x8b98
L_0002619a:
    mov.l @r15+,r1
    .org 0x2619c - 0x8b98
L_0002619c:
    mov r4,r2
    .org 0x2619e - 0x8b98
L_0002619e:
    mov r5,r3
    .org 0x261a0 - 0x8b98
L_000261a0:
    mov.l @r15+,r4
    .org 0x261a2 - 0x8b98
L_000261a2:
    lds.l @r15+,pr
    .org 0x261a4 - 0x8b98
L_000261a4:
    mov.l L_000261ac,r7
    .org 0x261a6 - 0x8b98
L_000261a6:
    jmp @r7
    .org 0x261a8 - 0x8b98
L_000261a8:
    mov #0x8,r5
    .org 0x261ac - 0x8b98
L_000261ac:
    .long 0x00026770
    .org 0x261b0 - 0x8b98
L_000261b0:
    .long 0x00026944
    .org 0x261b4 - 0x8b98
L_000261b4:
    .long 0x000269c4
    .org 0x26388 - 0x8b98
L_00026388:
    mov.w L_0002639a,r0
    .org 0x2638a - 0x8b98
L_0002638a:
    extu.b r5,r5
    .org 0x2638c - 0x8b98
L_0002638c:
    cmp/hs r0,r5
    .org 0x2638e - 0x8b98
L_0002638e:
    bt L_00026396
    .org 0x26390 - 0x8b98
L_00026390:
    mov.l L_0002639c,r6
    .org 0x26392 - 0x8b98
L_00026392:
    jmp @r6
    .org 0x26394 - 0x8b98
L_00026394:
    mov #0x0,r3
    .org 0x26396 - 0x8b98
L_00026396:
    rts
    .org 0x26398 - 0x8b98
L_00026398:
    mov.b @(0xf,r4),r0
    .org 0x2639a - 0x8b98
L_0002639a:
    .word 0x00f0
    .org 0x2639c - 0x8b98
L_0002639c:
    .long 0x00026a84
    .org 0x26474 - 0x8b98
L_00026474:
    sts.l pr,@-r15
    .org 0x26476 - 0x8b98
L_00026476:
    mov.l r4,@-r15
    .org 0x26478 - 0x8b98
L_00026478:
    mov r5,r0
    .org 0x2647a - 0x8b98
L_0002647a:
    extu.b r6,r5
    .org 0x2647c - 0x8b98
L_0002647c:
    mov.l L_0002649c,r7
    .org 0x2647e - 0x8b98
L_0002647e:
    jsr @r7
    .org 0x26480 - 0x8b98
L_00026480:
    mov #0x7,r4
    .org 0x26482 - 0x8b98
L_00026482:
    mov.l @r15+,r6
    .org 0x26484 - 0x8b98
L_00026484:
    add r4,r6
    .org 0x26486 - 0x8b98
L_00026486:
    mov.b @(0x1,r6),r0
    .org 0x26488 - 0x8b98
L_00026488:
    extu.b r0,r2
    .org 0x2648a - 0x8b98
L_0002648a:
    mov r5,r3
    .org 0x2648c - 0x8b98
L_0002648c:
    mov.b @r6,r1
    .org 0x2648e - 0x8b98
L_0002648e:
    lds.l @r15+,pr
    .org 0x26490 - 0x8b98
L_00026490:
    mov.l L_00026498,r6
    .org 0x26492 - 0x8b98
L_00026492:
    jmp @r6
    .org 0x26494 - 0x8b98
L_00026494:
    extu.b r1,r0
    .org 0x26498 - 0x8b98
L_00026498:
    .long 0x00026740
    .org 0x2649c - 0x8b98
L_0002649c:
    .long 0x00026944
    .org 0x26740 - 0x8b98
L_00026740:
    cmp/hs r0,r2
    .org 0x26742 - 0x8b98
L_00026742:
    bt L_0002675c
    .org 0x26744 - 0x8b98
L_00026744:
    mov.l r0,@-r15
    .org 0x26746 - 0x8b98
L_00026746:
    sub r2,r0
    .org 0x26748 - 0x8b98
L_00026748:
    sts macl,r1
    .org 0x2674a - 0x8b98
L_0002674a:
    mul.l r3,r0
    .org 0x2674c - 0x8b98
L_0002674c:
    sts macl,r0
    .org 0x2674e - 0x8b98
L_0002674e:
    lds r1,macl
    .org 0x26750 - 0x8b98
L_00026750:
    swap.w r0,r0
    .org 0x26752 - 0x8b98
L_00026752:
    mov.l @r15+,r2
    .org 0x26754 - 0x8b98
L_00026754:
    extu.w r0,r0
    .org 0x26756 - 0x8b98
L_00026756:
    sub r0,r2
    .org 0x26758 - 0x8b98
L_00026758:
    rts
    .org 0x2675a - 0x8b98
L_0002675a:
    mov r2,r0
    .org 0x2675c - 0x8b98
L_0002675c:
    sub r0,r2
    .org 0x2675e - 0x8b98
L_0002675e:
    sts macl,r1
    .org 0x26760 - 0x8b98
L_00026760:
    mul.l r3,r2
    .org 0x26762 - 0x8b98
L_00026762:
    sts macl,r2
    .org 0x26764 - 0x8b98
L_00026764:
    lds r1,macl
    .org 0x26766 - 0x8b98
L_00026766:
    swap.w r2,r2
    .org 0x26768 - 0x8b98
L_00026768:
    extu.w r2,r2
    .org 0x2676a - 0x8b98
L_0002676a:
    rts
    .org 0x2676c - 0x8b98
L_0002676c:
    add r2,r0
    .org 0x26770 - 0x8b98
L_00026770:
    mov.l r8,@-r15
    .org 0x26772 - 0x8b98
L_00026772:
    sts.l pr,@-r15
    .org 0x26774 - 0x8b98
L_00026774:
    sts macl,r7
    .org 0x26776 - 0x8b98
L_00026776:
    mulu.w r5,r0
    .org 0x26778 - 0x8b98
L_00026778:
    add r2,r4
    .org 0x2677a - 0x8b98
L_0002677a:
    sts macl,r0
    .org 0x2677c - 0x8b98
L_0002677c:
    lds r7,macl
    .org 0x2677e - 0x8b98
L_0002677e:
    add r0,r4
    .org 0x26780 - 0x8b98
L_00026780:
    add r4,r5
    .org 0x26782 - 0x8b98
L_00026782:
    mov r1,r8
    .org 0x26784 - 0x8b98
L_00026784:
    mov.l L_000267c8,r7
    .org 0x26786 - 0x8b98
L_00026786:
    tst r3,r3
    .org 0x26788 - 0x8b98
L_00026788:
    bt L_000267b0
    .org 0x2678a - 0x8b98
L_0002678a:
    mov.b @r4,r1
    .org 0x2678c - 0x8b98
L_0002678c:
    mov.b @(0x1,r4),r0
    .org 0x2678e - 0x8b98
L_0002678e:
    extu.b r0,r2
    .org 0x26790 - 0x8b98
L_00026790:
    jsr @r7
    .org 0x26792 - 0x8b98
L_00026792:
    extu.b r1,r0
    .org 0x26794 - 0x8b98
L_00026794:
    tst r8,r8
    .org 0x26796 - 0x8b98
L_00026796:
    bt L_000267c0
    .org 0x26798 - 0x8b98
L_00026798:
    mov.l r0,@-r15
    .org 0x2679a - 0x8b98
L_0002679a:
    mov.b @r5,r1
    .org 0x2679c - 0x8b98
L_0002679c:
    mov.b @(0x1,r5),r0
    .org 0x2679e - 0x8b98
L_0002679e:
    extu.b r0,r2
    .org 0x267a0 - 0x8b98
L_000267a0:
    jsr @r7
    .org 0x267a2 - 0x8b98
L_000267a2:
    extu.b r1,r0
    .org 0x267a4 - 0x8b98
L_000267a4:
    mov r0,r2
    .org 0x267a6 - 0x8b98
L_000267a6:
    mov.l @r15+,r0
    .org 0x267a8 - 0x8b98
L_000267a8:
    jsr @r7
    .org 0x267aa - 0x8b98
L_000267aa:
    mov r8,r3
    .org 0x267ac - 0x8b98
L_000267ac:
    bra L_000267c0
    .org 0x267ae - 0x8b98
L_000267ae:
    nop
    .org 0x267b0 - 0x8b98
L_000267b0:
    tst r8,r8
    .org 0x267b2 - 0x8b98
L_000267b2:
    bt/s L_000267c0
    .org 0x267b4 - 0x8b98
L_000267b4:
    mov.b @r4,r0
    .org 0x267b6 - 0x8b98
L_000267b6:
    mov.b @r5,r2
    .org 0x267b8 - 0x8b98
L_000267b8:
    extu.b r0,r0
    .org 0x267ba - 0x8b98
L_000267ba:
    extu.b r2,r2
    .org 0x267bc - 0x8b98
L_000267bc:
    jsr @r7
    .org 0x267be - 0x8b98
L_000267be:
    mov r8,r3
    .org 0x267c0 - 0x8b98
L_000267c0:
    lds.l @r15+,pr
    .org 0x267c2 - 0x8b98
L_000267c2:
    rts
    .org 0x267c4 - 0x8b98
L_000267c4:
    mov.l @r15+,r8
    .org 0x267c8 - 0x8b98
L_000267c8:
    .long 0x00026740
    .org 0x26944 - 0x8b98
L_00026944:
    mov r4,r3
    .org 0x26946 - 0x8b98
L_00026946:
    mov.b @(r0,r4),r1
    .org 0x26948 - 0x8b98
L_00026948:
    extu.b r1,r1
    .org 0x2694a - 0x8b98
L_0002694a:
    cmp/eq r1,r5
    .org 0x2694c - 0x8b98
L_0002694c:
    bt L_0002697c
    .org 0x2694e - 0x8b98
L_0002694e:
    cmp/hi r1,r5
    .org 0x26950 - 0x8b98
L_00026950:
    bf L_00026974
    .org 0x26952 - 0x8b98
L_00026952:
    cmp/eq r4,r3
    .org 0x26954 - 0x8b98
L_00026954:
    bt L_0002697c
    .org 0x26956 - 0x8b98
L_00026956:
    sub r1,r5
    .org 0x26958 - 0x8b98
L_00026958:
    shll16 r5
    .org 0x2695a - 0x8b98
L_0002695a:
    add r4,r0
    .org 0x2695c - 0x8b98
L_0002695c:
    mov.b @r0,r1
    .org 0x2695e - 0x8b98
L_0002695e:
    mov.b @(0x1,r0),r0
    .org 0x26960 - 0x8b98
L_00026960:
    extu.b r1,r1
    .org 0x26962 - 0x8b98
L_00026962:
    extu.b r0,r0
    .org 0x26964 - 0x8b98
L_00026964:
    sts.l pr,@-r15
    .org 0x26966 - 0x8b98
L_00026966:
    mov.l L_00026980,r2
    .org 0x26968 - 0x8b98
L_00026968:
    sub r1,r0
    .org 0x2696a - 0x8b98
L_0002696a:
    jsr @r2
    .org 0x2696c - 0x8b98
L_0002696c:
    mov r5,r1
    .org 0x2696e - 0x8b98
L_0002696e:
    lds.l @r15+,pr
    .org 0x26970 - 0x8b98
L_00026970:
    rts
    .org 0x26972 - 0x8b98
L_00026972:
    mov r0,r5
    .org 0x26974 - 0x8b98
L_00026974:
    add #-0x1,r4
    .org 0x26976 - 0x8b98
L_00026976:
    cmp/pz r4
    .org 0x26978 - 0x8b98
L_00026978:
    bt L_00026946
    .org 0x2697a - 0x8b98
L_0002697a:
    mov #0x0,r4
    .org 0x2697c - 0x8b98
L_0002697c:
    rts
    .org 0x2697e - 0x8b98
L_0002697e:
    mov #0x0,r5
    .org 0x26980 - 0x8b98
L_00026980:
    .long 0x00026c78
    .org 0x269c4 - 0x8b98
L_000269c4:
    mov r4,r3
    .org 0x269c6 - 0x8b98
L_000269c6:
    mov.b @(r0,r4),r1
    .org 0x269c8 - 0x8b98
L_000269c8:
    extu.b r1,r1
    .org 0x269ca - 0x8b98
L_000269ca:
    shll2 r1
    .org 0x269cc - 0x8b98
L_000269cc:
    cmp/eq r5,r1
    .org 0x269ce - 0x8b98
L_000269ce:
    bt L_00026a02
    .org 0x269d0 - 0x8b98
L_000269d0:
    cmp/hi r5,r1
    .org 0x269d2 - 0x8b98
L_000269d2:
    bt L_000269fa
    .org 0x269d4 - 0x8b98
L_000269d4:
    cmp/eq r4,r3
    .org 0x269d6 - 0x8b98
L_000269d6:
    bt L_00026a02
    .org 0x269d8 - 0x8b98
L_000269d8:
    sub r1,r5
    .org 0x269da - 0x8b98
L_000269da:
    shll16 r5
    .org 0x269dc - 0x8b98
L_000269dc:
    mov r4,r3
    .org 0x269de - 0x8b98
L_000269de:
    add r0,r3
    .org 0x269e0 - 0x8b98
L_000269e0:
    mov.b @r3,r1
    .org 0x269e2 - 0x8b98
L_000269e2:
    mov.b @(0x1,r3),r0
    .org 0x269e4 - 0x8b98
L_000269e4:
    extu.b r1,r1
    .org 0x269e6 - 0x8b98
L_000269e6:
    extu.b r0,r0
    .org 0x269e8 - 0x8b98
L_000269e8:
    sts.l pr,@-r15
    .org 0x269ea - 0x8b98
L_000269ea:
    mov.l L_00026a08,r2
    .org 0x269ec - 0x8b98
L_000269ec:
    sub r1,r0
    .org 0x269ee - 0x8b98
L_000269ee:
    shll2 r0
    .org 0x269f0 - 0x8b98
L_000269f0:
    jsr @r2
    .org 0x269f2 - 0x8b98
L_000269f2:
    mov r5,r1
    .org 0x269f4 - 0x8b98
L_000269f4:
    lds.l @r15+,pr
    .org 0x269f6 - 0x8b98
L_000269f6:
    rts
    .org 0x269f8 - 0x8b98
L_000269f8:
    mov r0,r5
    .org 0x269fa - 0x8b98
L_000269fa:
    add #-0x1,r4
    .org 0x269fc - 0x8b98
L_000269fc:
    cmp/pz r4
    .org 0x269fe - 0x8b98
L_000269fe:
    bt L_000269c6
    .org 0x26a00 - 0x8b98
L_00026a00:
    mov #0x0,r4
    .org 0x26a02 - 0x8b98
L_00026a02:
    rts
    .org 0x26a04 - 0x8b98
L_00026a04:
    mov #0x0,r5
    .org 0x26a08 - 0x8b98
L_00026a08:
    .long 0x00026c78
    .org 0x26a84 - 0x8b98
L_00026a84:
    shlr r5
    .org 0x26a86 - 0x8b98
L_00026a86:
    rotcr r3
    .org 0x26a88 - 0x8b98
L_00026a88:
    shlr r5
    .org 0x26a8a - 0x8b98
L_00026a8a:
    rotcr r3
    .org 0x26a8c - 0x8b98
L_00026a8c:
    shlr r5
    .org 0x26a8e - 0x8b98
L_00026a8e:
    rotcr r3
    .org 0x26a90 - 0x8b98
L_00026a90:
    shlr r5
    .org 0x26a92 - 0x8b98
L_00026a92:
    rotcr r3
    .org 0x26a94 - 0x8b98
L_00026a94:
    swap.w r3,r3
    .org 0x26a96 - 0x8b98
L_00026a96:
    shlr8 r0
    .org 0x26a98 - 0x8b98
L_00026a98:
    tst r0,r0
    .org 0x26a9a - 0x8b98
L_00026a9a:
    bt L_00026aaa
    .org 0x26a9c - 0x8b98
L_00026a9c:
    shll r5
    .org 0x26a9e - 0x8b98
L_00026a9e:
    add r5,r4
    .org 0x26aa0 - 0x8b98
L_00026aa0:
    mov.w @r4,r1
    .org 0x26aa2 - 0x8b98
L_00026aa2:
    mov.w @(0x2,r4),r0
    .org 0x26aa4 - 0x8b98
L_00026aa4:
    extu.w r0,r2
    .org 0x26aa6 - 0x8b98
L_00026aa6:
    bra L_00026ab4
    .org 0x26aa8 - 0x8b98
L_00026aa8:
    extu.w r1,r0
    .org 0x26aaa - 0x8b98
L_00026aaa:
    add r5,r4
    .org 0x26aac - 0x8b98
L_00026aac:
    mov.b @r4,r1
    .org 0x26aae - 0x8b98
L_00026aae:
    mov.b @(0x1,r4),r0
    .org 0x26ab0 - 0x8b98
L_00026ab0:
    extu.b r0,r2
    .org 0x26ab2 - 0x8b98
L_00026ab2:
    extu.b r1,r0
    .org 0x26ab4 - 0x8b98
L_00026ab4:
    mov.l L_00026abc,r6
    .org 0x26ab6 - 0x8b98
L_00026ab6:
    jmp @r6
    .org 0x26ab8 - 0x8b98
L_00026ab8:
    nop
    .org 0x26abc - 0x8b98
L_00026abc:
    .long 0x00026740
    .org 0x26c78 - 0x8b98
L_00026c78:
    tst r0,r0
    .org 0x26c7a - 0x8b98
L_00026c7a:
    bt L_00026d0a
    .org 0x26c7c - 0x8b98
L_00026c7c:
    mov.l r2,@-r15
    .org 0x26c7e - 0x8b98
L_00026c7e:
    mov #0x0,r2
    .org 0x26c80 - 0x8b98
L_00026c80:
    div0u
    .org 0x26c82 - 0x8b98
L_00026c82:
    rotcl r1
    .org 0x26c84 - 0x8b98
L_00026c84:
    div1 r0,r2
    .org 0x26c86 - 0x8b98
L_00026c86:
    rotcl r1
    .org 0x26c88 - 0x8b98
L_00026c88:
    div1 r0,r2
    .org 0x26c8a - 0x8b98
L_00026c8a:
    rotcl r1
    .org 0x26c8c - 0x8b98
L_00026c8c:
    div1 r0,r2
    .org 0x26c8e - 0x8b98
L_00026c8e:
    rotcl r1
    .org 0x26c90 - 0x8b98
L_00026c90:
    div1 r0,r2
    .org 0x26c92 - 0x8b98
L_00026c92:
    rotcl r1
    .org 0x26c94 - 0x8b98
L_00026c94:
    div1 r0,r2
    .org 0x26c96 - 0x8b98
L_00026c96:
    rotcl r1
    .org 0x26c98 - 0x8b98
L_00026c98:
    div1 r0,r2
    .org 0x26c9a - 0x8b98
L_00026c9a:
    rotcl r1
    .org 0x26c9c - 0x8b98
L_00026c9c:
    div1 r0,r2
    .org 0x26c9e - 0x8b98
L_00026c9e:
    rotcl r1
    .org 0x26ca0 - 0x8b98
L_00026ca0:
    div1 r0,r2
    .org 0x26ca2 - 0x8b98
L_00026ca2:
    rotcl r1
    .org 0x26ca4 - 0x8b98
L_00026ca4:
    div1 r0,r2
    .org 0x26ca6 - 0x8b98
L_00026ca6:
    rotcl r1
    .org 0x26ca8 - 0x8b98
L_00026ca8:
    div1 r0,r2
    .org 0x26caa - 0x8b98
L_00026caa:
    rotcl r1
    .org 0x26cac - 0x8b98
L_00026cac:
    div1 r0,r2
    .org 0x26cae - 0x8b98
L_00026cae:
    rotcl r1
    .org 0x26cb0 - 0x8b98
L_00026cb0:
    div1 r0,r2
    .org 0x26cb2 - 0x8b98
L_00026cb2:
    rotcl r1
    .org 0x26cb4 - 0x8b98
L_00026cb4:
    div1 r0,r2
    .org 0x26cb6 - 0x8b98
L_00026cb6:
    rotcl r1
    .org 0x26cb8 - 0x8b98
L_00026cb8:
    div1 r0,r2
    .org 0x26cba - 0x8b98
L_00026cba:
    rotcl r1
    .org 0x26cbc - 0x8b98
L_00026cbc:
    div1 r0,r2
    .org 0x26cbe - 0x8b98
L_00026cbe:
    rotcl r1
    .org 0x26cc0 - 0x8b98
L_00026cc0:
    div1 r0,r2
    .org 0x26cc2 - 0x8b98
L_00026cc2:
    rotcl r1
    .org 0x26cc4 - 0x8b98
L_00026cc4:
    div1 r0,r2
    .org 0x26cc6 - 0x8b98
L_00026cc6:
    rotcl r1
    .org 0x26cc8 - 0x8b98
L_00026cc8:
    div1 r0,r2
    .org 0x26cca - 0x8b98
L_00026cca:
    rotcl r1
    .org 0x26ccc - 0x8b98
L_00026ccc:
    div1 r0,r2
    .org 0x26cce - 0x8b98
L_00026cce:
    rotcl r1
    .org 0x26cd0 - 0x8b98
L_00026cd0:
    div1 r0,r2
    .org 0x26cd2 - 0x8b98
L_00026cd2:
    rotcl r1
    .org 0x26cd4 - 0x8b98
L_00026cd4:
    div1 r0,r2
    .org 0x26cd6 - 0x8b98
L_00026cd6:
    rotcl r1
    .org 0x26cd8 - 0x8b98
L_00026cd8:
    div1 r0,r2
    .org 0x26cda - 0x8b98
L_00026cda:
    rotcl r1
    .org 0x26cdc - 0x8b98
L_00026cdc:
    div1 r0,r2
    .org 0x26cde - 0x8b98
L_00026cde:
    rotcl r1
    .org 0x26ce0 - 0x8b98
L_00026ce0:
    div1 r0,r2
    .org 0x26ce2 - 0x8b98
L_00026ce2:
    rotcl r1
    .org 0x26ce4 - 0x8b98
L_00026ce4:
    div1 r0,r2
    .org 0x26ce6 - 0x8b98
L_00026ce6:
    rotcl r1
    .org 0x26ce8 - 0x8b98
L_00026ce8:
    div1 r0,r2
    .org 0x26cea - 0x8b98
L_00026cea:
    rotcl r1
    .org 0x26cec - 0x8b98
L_00026cec:
    div1 r0,r2
    .org 0x26cee - 0x8b98
L_00026cee:
    rotcl r1
    .org 0x26cf0 - 0x8b98
L_00026cf0:
    div1 r0,r2
    .org 0x26cf2 - 0x8b98
L_00026cf2:
    rotcl r1
    .org 0x26cf4 - 0x8b98
L_00026cf4:
    div1 r0,r2
    .org 0x26cf6 - 0x8b98
L_00026cf6:
    rotcl r1
    .org 0x26cf8 - 0x8b98
L_00026cf8:
    div1 r0,r2
    .org 0x26cfa - 0x8b98
L_00026cfa:
    rotcl r1
    .org 0x26cfc - 0x8b98
L_00026cfc:
    div1 r0,r2
    .org 0x26cfe - 0x8b98
L_00026cfe:
    rotcl r1
    .org 0x26d00 - 0x8b98
L_00026d00:
    div1 r0,r2
    .org 0x26d02 - 0x8b98
L_00026d02:
    rotcl r1
    .org 0x26d04 - 0x8b98
L_00026d04:
    mov.l @r15+,r2
    .org 0x26d06 - 0x8b98
L_00026d06:
    rts
    .org 0x26d08 - 0x8b98
L_00026d08:
    mov r1,r0
    .org 0x26d0a - 0x8b98
L_00026d0a:
    rts
    .org 0x26d0c - 0x8b98
L_00026d0c:
    mov #0x0,r0
    .org 0x5594a - 0x8b98
L_0005594a:
    mov.l r11,@-r15
    .org 0x5594c - 0x8b98
L_0005594c:
    mov.l r12,@-r15
    .org 0x5594e - 0x8b98
L_0005594e:
    mov.l r13,@-r15
    .org 0x55950 - 0x8b98
L_00055950:
    mov.l r14,@-r15
    .org 0x55952 - 0x8b98
L_00055952:
    sts.l pr,@-r15
    .org 0x55954 - 0x8b98
L_00055954:
    sts.l macl,@-r15
    .org 0x55956 - 0x8b98
L_00055956:
    add #-0x10,r15
    .org 0x55958 - 0x8b98
L_00055958:
    mov.l L_00055ae8,r13
    .org 0x5595a - 0x8b98
L_0005595a:
    mov #0x17,r0
    .org 0x5595c - 0x8b98
L_0005595c:
    mov.l L_00055aec,r4
    .org 0x5595e - 0x8b98
L_0005595e:
    mov.b @(r0,r13),r6
    .org 0x55960 - 0x8b98
L_00055960:
    mov.l L_00055af0,r2
    .org 0x55962 - 0x8b98
L_00055962:
    mov.l L_00055ae4,r12
    .org 0x55964 - 0x8b98
L_00055964:
    jsr @r2
    .org 0x55966 - 0x8b98
L_00055966:
    extu.b r6,r5
    .org 0x55968 - 0x8b98
L_00055968:
    mov r0,r6
    .org 0x5596a - 0x8b98
L_0005596a:
    mov.w L_000559f4,r0
    .org 0x5596c - 0x8b98
L_0005596c:
    mov.l L_00055af4,r2
    .org 0x5596e - 0x8b98
L_0005596e:
    mov.b r6,@(r0,r12)
    .org 0x55970 - 0x8b98
L_00055970:
    mov.w L_000559f6,r0
    .org 0x55972 - 0x8b98
L_00055972:
    mov.l L_00055af8,r5
    .org 0x55974 - 0x8b98
L_00055974:
    mov.b @(r0,r2),r4
    .org 0x55976 - 0x8b98
L_00055976:
    mov.b @(0x4,r5),r0
    .org 0x55978 - 0x8b98
L_00055978:
    tst #0x8,r0
    .org 0x5597a - 0x8b98
L_0005597a:
    bt/s L_00055980
    .org 0x5597c - 0x8b98
L_0005597c:
    extu.b r4,r4
    .org 0x5597e - 0x8b98
L_0005597e:
    add #0x8,r4
    .org 0x55980 - 0x8b98
L_00055980:
    extu.b r6,r6
    .org 0x55982 - 0x8b98
L_00055982:
    cmp/hs r6,r4
    .org 0x55984 - 0x8b98
L_00055984:
    bt L_0005598e
    .org 0x55986 - 0x8b98
L_00055986:
    mov.l L_00055af8,r6
    .org 0x55988 - 0x8b98
L_00055988:
    mov.b @(0x4,r6),r0
    .org 0x5598a - 0x8b98
L_0005598a:
    bra L_00055994
    .org 0x5598c - 0x8b98
L_0005598c:
    and #0xf7,r0
    .org 0x5598e - 0x8b98
L_0005598e:
    mov.l L_00055af8,r6
    .org 0x55990 - 0x8b98
L_00055990:
    mov.b @(0x4,r6),r0
    .org 0x55992 - 0x8b98
L_00055992:
    or #0x8,r0
    .org 0x55994 - 0x8b98
L_00055994:
    mov.b r0,@(0x4,r6)
    .org 0x55996 - 0x8b98
L_00055996:
    mov.l L_00055af8,r6
    .org 0x55998 - 0x8b98
L_00055998:
    mov.b @(0x4,r6),r0
    .org 0x5599a - 0x8b98
L_0005599a:
    tst #0x8,r0
    .org 0x5599c - 0x8b98
L_0005599c:
    bt L_000559a2
    .org 0x5599e - 0x8b98
L_0005599e:
    bra L_000559a6
    .org 0x559a0 - 0x8b98
L_000559a0:
    mov #-0x1,r2
    .org 0x559a2 - 0x8b98
L_000559a2:
    mov.l L_00055afc,r2
    .org 0x559a4 - 0x8b98
L_000559a4:
    mov.b @r2,r2
    .org 0x559a6 - 0x8b98
L_000559a6:
    mov r2,r0
    .org 0x559a8 - 0x8b98
L_000559a8:
    mov.b r0,@(0x3,r15)
    .org 0x559aa - 0x8b98
L_000559aa:
    mov #0x20,r0
    .org 0x559ac - 0x8b98
L_000559ac:
    mov.l L_00055b00,r4
    .org 0x559ae - 0x8b98
L_000559ae:
    mov.w @(r0,r13),r14
    .org 0x559b0 - 0x8b98
L_000559b0:
    mov.l L_00055b04,r5
    .org 0x559b2 - 0x8b98
L_000559b2:
    mov.l L_00055b08,r6
    .org 0x559b4 - 0x8b98
L_000559b4:
    mov.l L_00055b0c,r2
    .org 0x559b6 - 0x8b98
L_000559b6:
    jsr @r2
    .org 0x559b8 - 0x8b98
L_000559b8:
    extu.w r14,r7
    .org 0x559ba - 0x8b98
L_000559ba:
    mov.l L_00055af8,r6
    .org 0x559bc - 0x8b98
L_000559bc:
    extu.b r0,r7
    .org 0x559be - 0x8b98
L_000559be:
    mov.l r7,@(0x4,r15)
    .org 0x559c0 - 0x8b98
L_000559c0:
    mov.b @(0x2,r6),r0
    .org 0x559c2 - 0x8b98
L_000559c2:
    tst #0x40,r0
    .org 0x559c4 - 0x8b98
L_000559c4:
    bt L_00055a02
    .org 0x559c6 - 0x8b98
L_000559c6:
    mov #0x12,r0
    .org 0x559c8 - 0x8b98
L_000559c8:
    mov.l L_00055b10,r4
    .org 0x559ca - 0x8b98
L_000559ca:
    mov.b @(r0,r13),r7
    .org 0x559cc - 0x8b98
L_000559cc:
    mov.l L_00055b14,r5
    .org 0x559ce - 0x8b98
L_000559ce:
    mov.l L_00055b18,r2
    .org 0x559d0 - 0x8b98
L_000559d0:
    jsr @r2
    .org 0x559d2 - 0x8b98
L_000559d2:
    extu.b r7,r6
    .org 0x559d4 - 0x8b98
L_000559d4:
    mov.l @(0x4,r15),r7
    .org 0x559d6 - 0x8b98
L_000559d6:
    extu.b r0,r2
    .org 0x559d8 - 0x8b98
L_000559d8:
    mov.l L_00055b1c,r6
    .org 0x559da - 0x8b98
L_000559da:
    add #-0x80,r7
    .org 0x559dc - 0x8b98
L_000559dc:
    mul.l r7,r2
    .org 0x559de - 0x8b98
L_000559de:
    jsr @r6
    .org 0x559e0 - 0x8b98
L_000559e0:
    sts macl,r0
    .org 0x559e2 - 0x8b98
L_000559e2:
    mov #-0x80,r6
    .org 0x559e4 - 0x8b98
L_000559e4:
    extu.b r6,r6
    .org 0x559e6 - 0x8b98
L_000559e6:
    add r6,r0
    .org 0x559e8 - 0x8b98
L_000559e8:
    cmp/pz r0
    .org 0x559ea - 0x8b98
L_000559ea:
    bt/s L_000559f8
    .org 0x559ec - 0x8b98
L_000559ec:
    mov r0,r2
    .org 0x559ee - 0x8b98
L_000559ee:
    bra L_00055a02
    .org 0x559f0 - 0x8b98
L_000559f0:
    mov #0x0,r7
    .org 0x559f4 - 0x8b98
L_000559f4:
    .word 0x0263
    .org 0x559f6 - 0x8b98
L_000559f6:
    .word 0x0c30
    .org 0x559f8 - 0x8b98
L_000559f8:
    mov #-0x1,r7
    .org 0x559fa - 0x8b98
L_000559fa:
    extu.b r7,r7
    .org 0x559fc - 0x8b98
L_000559fc:
    cmp/gt r7,r2
    .org 0x559fe - 0x8b98
L_000559fe:
    bt L_00055a02
    .org 0x55a00 - 0x8b98
L_00055a00:
    mov r2,r7
    .org 0x55a02 - 0x8b98
L_00055a02:
    mov.l L_00055af8,r6
    .org 0x55a04 - 0x8b98
L_00055a04:
    mov #0x3e,r0
    .org 0x55a06 - 0x8b98
L_00055a06:
    mov.b @(r0,r6),r0
    .org 0x55a08 - 0x8b98
L_00055a08:
    tst #0x80,r0
    .org 0x55a0a - 0x8b98
L_00055a0a:
    bt/s L_00055a20
    .org 0x55a0c - 0x8b98
L_00055a0c:
    mov r7,r5
    .org 0x55a0e - 0x8b98
L_00055a0e:
    mov.l L_00055b20,r4
    .org 0x55a10 - 0x8b98
L_00055a10:
    mov.b @r4,r6
    .org 0x55a12 - 0x8b98
L_00055a12:
    mov.l L_00055b24,r4
    .org 0x55a14 - 0x8b98
L_00055a14:
    extu.b r6,r6
    .org 0x55a16 - 0x8b98
L_00055a16:
    mov.b @r4,r2
    .org 0x55a18 - 0x8b98
L_00055a18:
    mov.l r6,@(0x8,r15)
    .org 0x55a1a - 0x8b98
L_00055a1a:
    extu.b r2,r2
    .org 0x55a1c - 0x8b98
L_00055a1c:
    sub r2,r6
    .org 0x55a1e - 0x8b98
L_00055a1e:
    add r6,r5
    .org 0x55a20 - 0x8b98
L_00055a20:
    mov.l L_00055b20,r4
    .org 0x55a22 - 0x8b98
L_00055a22:
    mov.b @r4,r2
    .org 0x55a24 - 0x8b98
L_00055a24:
    extu.b r2,r6
    .org 0x55a26 - 0x8b98
L_00055a26:
    cmp/hs r6,r5
    .org 0x55a28 - 0x8b98
L_00055a28:
    bt L_00055a34
    .org 0x55a2a - 0x8b98
L_00055a2a:
    mov.l L_00055af8,r6
    .org 0x55a2c - 0x8b98
L_00055a2c:
    mov #0x3e,r0
    .org 0x55a2e - 0x8b98
L_00055a2e:
    mov.b @(r0,r6),r0
    .org 0x55a30 - 0x8b98
L_00055a30:
    bra L_00055a3c
    .org 0x55a32 - 0x8b98
L_00055a32:
    and #0x7f,r0
    .org 0x55a34 - 0x8b98
L_00055a34:
    mov.l L_00055af8,r6
    .org 0x55a36 - 0x8b98
L_00055a36:
    mov #0x3e,r0
    .org 0x55a38 - 0x8b98
L_00055a38:
    mov.b @(r0,r6),r0
    .org 0x55a3a - 0x8b98
L_00055a3a:
    or #0x80,r0
    .org 0x55a3c - 0x8b98
L_00055a3c:
    mov r0,r2
    .org 0x55a3e - 0x8b98
L_00055a3e:
    mov #0x3e,r0
    .org 0x55a40 - 0x8b98
L_00055a40:
    mov.b r2,@(r0,r6)
    .org 0x55a42 - 0x8b98
L_00055a42:
    mov.l L_00055af8,r6
    .org 0x55a44 - 0x8b98
L_00055a44:
    mov.b @(r0,r6),r0
    .org 0x55a46 - 0x8b98
L_00055a46:
    tst #0x80,r0
    .org 0x55a48 - 0x8b98
L_00055a48:
    bf L_00055a4c
    .org 0x55a4a - 0x8b98
L_00055a4a:
    mov #-0x80,r7
    .org 0x55a4c - 0x8b98
L_00055a4c:
    mov.w L_00055ad8,r0
    .org 0x55a4e - 0x8b98
L_00055a4e:
    mov.l L_00055b28,r2
    .org 0x55a50 - 0x8b98
L_00055a50:
    mov.b r7,@(r0,r12)
    .org 0x55ad8 - 0x8b98
L_00055ad8:
    .word 0x035f
    .org 0x55ae4 - 0x8b98
L_00055ae4:
    .long 0xffff128c
    .org 0x55ae8 - 0x8b98
L_00055ae8:
    .long 0xffff119c
    .org 0x55aec - 0x8b98
L_00055aec:
    .long 0x0001214e
    .org 0x55af0 - 0x8b98
L_00055af0:
    .long 0x00026388
    .org 0x55af4 - 0x8b98
L_00055af4:
    .long 0xffff28f8
    .org 0x55af8 - 0x8b98
L_00055af8:
    .long 0xffff2464
    .org 0x55afc - 0x8b98
L_00055afc:
    .long 0xffff102c
    .org 0x55b00 - 0x8b98
L_00055b00:
    .long 0x0000a9aa
    .org 0x55b04 - 0x8b98
L_00055b04:
    .long 0x00011cc0
    .org 0x55b08 - 0x8b98
L_00055b08:
    .long 0x00011ac7
    .org 0x55b0c - 0x8b98
L_00055b0c:
    .long 0x00026178
    .org 0x55b10 - 0x8b98
L_00055b10:
    .long 0x00012552
    .org 0x55b14 - 0x8b98
L_00055b14:
    .long 0x00011cd8
    .org 0x55b18 - 0x8b98
L_00055b18:
    .long 0x00026474
    .org 0x55b1c - 0x8b98
L_00055b1c:
    .long 0x000224f8
    .org 0x55b20 - 0x8b98
L_00055b20:
    .long 0x00008b9b
    .org 0x55b24 - 0x8b98
L_00055b24:
    .long 0x00008b9f
    .org 0x55b28 - 0x8b98
L_00055b28:
    .long 0xffff106a
