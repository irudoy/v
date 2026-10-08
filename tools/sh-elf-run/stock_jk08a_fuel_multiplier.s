! Exact complete multiplier publisher and original input pools.
    .text
    .balign 4
    .org 0x838e - 0x838c
L_0000838e:
    .byte 0x40
    .org 0x840d - 0x838c
L_0000840d:
    .byte 0x00,0x00,0x00,0x03,0x03,0x00
    .org 0x84e6 - 0x838c
L_000084e6:
    .byte 0xff,0xff
    .org 0x8b9d - 0x838c
L_00008b9d:
    .byte 0xfe
    .org 0x556ec - 0x838c
L_000556ec:
    mov.l r13,@-r15
    .org 0x556ee - 0x838c
L_000556ee:
    mov.l r14,@-r15
    .org 0x556f0 - 0x838c
L_000556f0:
    sts.l macl,@-r15
    .org 0x556f2 - 0x838c
L_000556f2:
    stc.l gbr,@-r15
    .org 0x556f4 - 0x838c
L_000556f4:
    mov.l L_00055858,r0
    .org 0x556f6 - 0x838c
L_000556f6:
    ldc r0,gbr
    .org 0x556f8 - 0x838c
L_000556f8:
    add #-0x10,r15
    .org 0x556fa - 0x838c
L_000556fa:
    mov.w @(0x3e,gbr),r0
    .org 0x556fc - 0x838c
L_000556fc:
    mov #-0x1,r14
    .org 0x556fe - 0x838c
L_000556fe:
    extu.w r14,r14
    .org 0x55700 - 0x838c
L_00055700:
    extu.w r0,r6
    .org 0x55702 - 0x838c
L_00055702:
    mov.w @(0x12e,gbr),r0
    .org 0x55704 - 0x838c
L_00055704:
    extu.w r0,r2
    .org 0x55706 - 0x838c
L_00055706:
    add r2,r6
    .org 0x55708 - 0x838c
L_00055708:
    cmp/hi r14,r6
    .org 0x5570a - 0x838c
L_0005570a:
    bf/s L_00055710
    .org 0x5570c - 0x838c
L_0005570c:
    mov r6,r2
    .org 0x5570e - 0x838c
L_0005570e:
    mov r14,r2
    .org 0x55710 - 0x838c
L_00055710:
    mov.w @(0xc,gbr),r0
    .org 0x55712 - 0x838c
L_00055712:
    mov.l L_00055880,r13
    .org 0x55714 - 0x838c
L_00055714:
    extu.w r0,r6
    .org 0x55716 - 0x838c
L_00055716:
    mul.l r6,r2
    .org 0x55718 - 0x838c
L_00055718:
    mov.b @r13,r0
    .org 0x5571a - 0x838c
L_0005571a:
    sts macl,r4
    .org 0x5571c - 0x838c
L_0005571c:
    and #0x40,r0
    .org 0x5571e - 0x838c
L_0005571e:
    tst r0,r0
    .org 0x55720 - 0x838c
L_00055720:
    shlr8 r4
    .org 0x55722 - 0x838c
L_00055722:
    shlr2 r4
    .org 0x55724 - 0x838c
L_00055724:
    shlr2 r4
    .org 0x55726 - 0x838c
L_00055726:
    shlr2 r4
    .org 0x55728 - 0x838c
L_00055728:
    bt/s L_0005574e
    .org 0x5572a - 0x838c
L_0005572a:
    mov r0,r6
    .org 0x5572c - 0x838c
L_0005572c:
    mov.l L_00055884,r2
    .org 0x5572e - 0x838c
L_0005572e:
    mov.b @r2,r5
    .org 0x55730 - 0x838c
L_00055730:
    extu.b r5,r2
    .org 0x55732 - 0x838c
L_00055732:
    mul.l r4,r2
    .org 0x55734 - 0x838c
L_00055734:
    sts macl,r2
    .org 0x55736 - 0x838c
L_00055736:
    shlr2 r2
    .org 0x55738 - 0x838c
L_00055738:
    mov r2,r5
    .org 0x5573a - 0x838c
L_0005573a:
    shlr2 r5
    .org 0x5573c - 0x838c
L_0005573c:
    shlr2 r5
    .org 0x5573e - 0x838c
L_0005573e:
    cmp/hi r14,r5
    .org 0x55740 - 0x838c
L_00055740:
    bt L_00055748
    .org 0x55742 - 0x838c
L_00055742:
    shlr2 r2
    .org 0x55744 - 0x838c
L_00055744:
    shlr2 r2
    .org 0x55746 - 0x838c
L_00055746:
    mov r2,r14
    .org 0x55748 - 0x838c
L_00055748:
    bra L_00055776
    .org 0x5574a - 0x838c
L_0005574a:
    mov r14,r4
    .org 0x5574e - 0x838c
L_0005574e:
    mov.l L_0005587c,r1
    .org 0x55750 - 0x838c
L_00055750:
    mov.w L_00055850,r0
    .org 0x55752 - 0x838c
L_00055752:
    mov.l L_00055888,r7
    .org 0x55754 - 0x838c
L_00055754:
    mov.w @(r0,r1),r2
    .org 0x55756 - 0x838c
L_00055756:
    mov.b @(0x4,r7),r0
    .org 0x55758 - 0x838c
L_00055758:
    extu.w r2,r5
    .org 0x5575a - 0x838c
L_0005575a:
    cmp/hs r5,r4
    .org 0x5575c - 0x838c
L_0005575c:
    bf/s L_0005576c
    .org 0x5575e - 0x838c
L_0005575e:
    mov r0,r2
    .org 0x55760 - 0x838c
L_00055760:
    cmp/hi r14,r4
    .org 0x55762 - 0x838c
L_00055762:
    bf L_00055766
    .org 0x55764 - 0x838c
L_00055764:
    mov r14,r4
    .org 0x55766 - 0x838c
L_00055766:
    mov r2,r0
    .org 0x55768 - 0x838c
L_00055768:
    bra L_00055774
    .org 0x5576a - 0x838c
L_0005576a:
    and #0xef,r0
    .org 0x5576c - 0x838c
L_0005576c:
    mov.w L_00055850,r0
    .org 0x5576e - 0x838c
L_0005576e:
    mov.w @(r0,r1),r4
    .org 0x55770 - 0x838c
L_00055770:
    mov r2,r0
    .org 0x55772 - 0x838c
L_00055772:
    or #0x10,r0
    .org 0x55774 - 0x838c
L_00055774:
    mov.b r0,@(0x4,r7)
    .org 0x55776 - 0x838c
L_00055776:
    mov.b @(0x12,gbr),r0
    .org 0x55778 - 0x838c
L_00055778:
    cmp/eq #0x3f,r0
    .org 0x5577a - 0x838c
L_0005577a:
    bf L_00055780
    .org 0x5577c - 0x838c
L_0005577c:
    bra L_0005592c
    .org 0x5577e - 0x838c
L_0005577e:
    nop
    .org 0x55780 - 0x838c
L_00055780:
    mov.b @(0x4,gbr),r0
    .org 0x55782 - 0x838c
L_00055782:
    cmp/eq #0x3f,r0
    .org 0x55784 - 0x838c
L_00055784:
    bf L_0005578a
    .org 0x55786 - 0x838c
L_00055786:
    bra L_0005592c
    .org 0x55788 - 0x838c
L_00055788:
    nop
    .org 0x5578a - 0x838c
L_0005578a:
    mov.b @(0x2,r13),r0
    .org 0x5578c - 0x838c
L_0005578c:
    tst #0x40,r0
    .org 0x5578e - 0x838c
L_0005578e:
    bt L_00055794
    .org 0x55790 - 0x838c
L_00055790:
    bra L_0005592c
    .org 0x55792 - 0x838c
L_00055792:
    nop
    .org 0x55794 - 0x838c
L_00055794:
    tst r6,r6
    .org 0x55796 - 0x838c
L_00055796:
    bt L_0005579c
    .org 0x55798 - 0x838c
L_00055798:
    bra L_0005592c
    .org 0x5579a - 0x838c
L_0005579a:
    nop
    .org 0x5579c - 0x838c
L_0005579c:
    mov.l L_00055888,r6
    .org 0x5579e - 0x838c
L_0005579e:
    mov.b @r6,r0
    .org 0x557a0 - 0x838c
L_000557a0:
    tst #0x8,r0
    .org 0x557a2 - 0x838c
L_000557a2:
    bt/s L_000557aa
    .org 0x557a4 - 0x838c
L_000557a4:
    mov.l r6,@(0x8,r15)
    .org 0x557a6 - 0x838c
L_000557a6:
    bra L_0005592c
    .org 0x557a8 - 0x838c
L_000557a8:
    nop
    .org 0x557aa - 0x838c
L_000557aa:
    mov.l L_0005587c,r1
    .org 0x557ac - 0x838c
L_000557ac:
    mov #0x62,r0
    .org 0x557ae - 0x838c
L_000557ae:
    shll2 r0
    .org 0x557b0 - 0x838c
L_000557b0:
    mov.l L_0005588c,r6
    .org 0x557b2 - 0x838c
L_000557b2:
    mov.w @(r0,r1),r2
    .org 0x557b4 - 0x838c
L_000557b4:
    extu.w r2,r2
    .org 0x557b6 - 0x838c
L_000557b6:
    cmp/eq r6,r2
    .org 0x557b8 - 0x838c
L_000557b8:
    bt L_000557be
    .org 0x557ba - 0x838c
L_000557ba:
    bra L_0005592c
    .org 0x557bc - 0x838c
L_000557bc:
    nop
    .org 0x557be - 0x838c
L_000557be:
    mov.l L_00055890,r6
    .org 0x557c0 - 0x838c
L_000557c0:
    mov #0x3a,r0
    .org 0x557c2 - 0x838c
L_000557c2:
    mov.l @(0x8,r15),r5
    .org 0x557c4 - 0x838c
L_000557c4:
    extu.w r4,r4
    .org 0x557c6 - 0x838c
L_000557c6:
    mov.b @r6,r2
    .org 0x557c8 - 0x838c
L_000557c8:
    mov.b @(r0,r5),r5
    .org 0x557ca - 0x838c
L_000557ca:
    extu.b r2,r6
    .org 0x557cc - 0x838c
L_000557cc:
    shll8 r6
    .org 0x557ce - 0x838c
L_000557ce:
    cmp/gt r6,r4
    .org 0x557d0 - 0x838c
L_000557d0:
    bf/s L_000557d6
    .org 0x557d2 - 0x838c
L_000557d2:
    mov.b r5,@r15
    .org 0x557d4 - 0x838c
L_000557d4:
    mov r6,r4
    .org 0x557d6 - 0x838c
L_000557d6:
    mov.l @(0x8,r15),r6
    .org 0x557d8 - 0x838c
L_000557d8:
    mov.b @(0x7,r6),r0
    .org 0x557da - 0x838c
L_000557da:
    tst #0x10,r0
    .org 0x557dc - 0x838c
L_000557dc:
    movt r0
    .org 0x557de - 0x838c
L_000557de:
    xor #0x1,r0
    .org 0x557e0 - 0x838c
L_000557e0:
    extu.b r0,r7
    .org 0x557e2 - 0x838c
L_000557e2:
    mov.b @(0x4,r6),r0
    .org 0x557e4 - 0x838c
L_000557e4:
    tst #0x10,r0
    .org 0x557e6 - 0x838c
L_000557e6:
    mov.b r0,@(0x4,r15)
    .org 0x557e8 - 0x838c
L_000557e8:
    movt r0
    .org 0x557ea - 0x838c
L_000557ea:
    xor #0x1,r0
    .org 0x557ec - 0x838c
L_000557ec:
    extu.b r0,r6
    .org 0x557ee - 0x838c
L_000557ee:
    cmp/eq r6,r7
    .org 0x557f0 - 0x838c
L_000557f0:
    bt L_00055800
    .org 0x557f2 - 0x838c
L_000557f2:
    mov #0x40,r0
    .org 0x557f4 - 0x838c
L_000557f4:
    mov.l @(0x8,r15),r2
    .org 0x557f6 - 0x838c
L_000557f6:
    or r0,r5
    .org 0x557f8 - 0x838c
L_000557f8:
    mov #0x3a,r0
    .org 0x557fa - 0x838c
L_000557fa:
    mov.b r5,@(r0,r2)
    .org 0x557fc - 0x838c
L_000557fc:
    exts.b r5,r2
    .org 0x557fe - 0x838c
L_000557fe:
    mov.b r2,@r15
    .org 0x55800 - 0x838c
L_00055800:
    mov.b @r15,r0
    .org 0x55802 - 0x838c
L_00055802:
    tst #0x40,r0
    .org 0x55804 - 0x838c
L_00055804:
    bt/s L_000558d2
    .org 0x55806 - 0x838c
L_00055806:
    mov.b r0,@(0xc,r15)
    .org 0x55808 - 0x838c
L_00055808:
    mov.w L_00055852,r6
    .org 0x5580a - 0x838c
L_0005580a:
    mov.b @r6,r0
    .org 0x5580c - 0x838c
L_0005580c:
    tst #0x80,r0
    .org 0x5580e - 0x838c
L_0005580e:
    bt L_000558cc
    .org 0x55810 - 0x838c
L_00055810:
    mov.b @(0x4,r15),r0
    .org 0x55812 - 0x838c
L_00055812:
    tst #0x10,r0
    .org 0x55814 - 0x838c
L_00055814:
    bt L_00055840
    .org 0x55816 - 0x838c
L_00055816:
    mov.l L_00055894,r5
    .org 0x55818 - 0x838c
L_00055818:
    extu.w r4,r4
    .org 0x5581a - 0x838c
L_0005581a:
    mov.b @(0x5,r5),r0
    .org 0x5581c - 0x838c
L_0005581c:
    extu.b r0,r6
    .org 0x5581e - 0x838c
L_0005581e:
    mov.w @(0x18,gbr),r0
    .org 0x55820 - 0x838c
L_00055820:
    shll2 r6
    .org 0x55822 - 0x838c
L_00055822:
    shll2 r6
    .org 0x55824 - 0x838c
L_00055824:
    extu.w r0,r7
    .org 0x55826 - 0x838c
L_00055826:
    mov r7,r2
    .org 0x55828 - 0x838c
L_00055828:
    add r6,r2
    .org 0x5582a - 0x838c
L_0005582a:
    cmp/ge r4,r2
    .org 0x5582c - 0x838c
L_0005582c:
    bt L_000558bc
    .org 0x5582e - 0x838c
L_0005582e:
    mov #-0x1,r5
    .org 0x55830 - 0x838c
L_00055830:
    mov r7,r2
    .org 0x55832 - 0x838c
L_00055832:
    add r6,r2
    .org 0x55834 - 0x838c
L_00055834:
    extu.w r5,r4
    .org 0x55836 - 0x838c
L_00055836:
    cmp/gt r4,r2
    .org 0x55838 - 0x838c
L_00055838:
    bt L_0005592c
    .org 0x5583a - 0x838c
L_0005583a:
    add r6,r7
    .org 0x5583c - 0x838c
L_0005583c:
    bra L_0005592c
    .org 0x5583e - 0x838c
L_0005583e:
    mov r7,r4
    .org 0x55840 - 0x838c
L_00055840:
    mov.l @(0x8,r15),r6
    .org 0x55842 - 0x838c
L_00055842:
    mov.l L_00055894,r5
    .org 0x55844 - 0x838c
L_00055844:
    mov.b @(0xb,r6),r0
    .org 0x55846 - 0x838c
L_00055846:
    tst #0x40,r0
    .org 0x55848 - 0x838c
L_00055848:
    bt L_00055898
    .org 0x5584a - 0x838c
L_0005584a:
    mov.b @(0x1,r5),r0
    .org 0x5584c - 0x838c
L_0005584c:
    bra L_0005589c
    .org 0x5584e - 0x838c
L_0005584e:
    extu.b r0,r5
    .org 0x55850 - 0x838c
L_00055850:
    .word 0x0340
    .org 0x55852 - 0x838c
L_00055852:
    .word 0x84c3
    .org 0x55858 - 0x838c
L_00055858:
    .long 0xffff22dc
    .org 0x5587c - 0x838c
L_0005587c:
    .long 0xffff128c
    .org 0x55880 - 0x838c
L_00055880:
    .long 0xffff4184
    .org 0x55884 - 0x838c
L_00055884:
    .long 0x0000838e
    .org 0x55888 - 0x838c
L_00055888:
    .long 0xffff2468
    .org 0x5588c - 0x838c
L_0005588c:
    .long 0x00008000
    .org 0x55890 - 0x838c
L_00055890:
    .long 0x00008b9d
    .org 0x55894 - 0x838c
L_00055894:
    .long 0x0000840d
    .org 0x55898 - 0x838c
L_00055898:
    mov.b @r5,r2
    .org 0x5589a - 0x838c
L_0005589a:
    extu.b r2,r5
    .org 0x5589c - 0x838c
L_0005589c:
    mov.w @(0x18,gbr),r0
    .org 0x5589e - 0x838c
L_0005589e:
    shll2 r5
    .org 0x558a0 - 0x838c
L_000558a0:
    shll2 r5
    .org 0x558a2 - 0x838c
L_000558a2:
    extu.w r0,r7
    .org 0x558a4 - 0x838c
L_000558a4:
    mov r7,r2
    .org 0x558a6 - 0x838c
L_000558a6:
    extu.w r4,r4
    .org 0x558a8 - 0x838c
L_000558a8:
    sub r5,r2
    .org 0x558aa - 0x838c
L_000558aa:
    cmp/gt r4,r2
    .org 0x558ac - 0x838c
L_000558ac:
    bf L_000558bc
    .org 0x558ae - 0x838c
L_000558ae:
    cmp/ge r5,r7
    .org 0x558b0 - 0x838c
L_000558b0:
    bt L_000558b6
    .org 0x558b2 - 0x838c
L_000558b2:
    bra L_0005592c
    .org 0x558b4 - 0x838c
L_000558b4:
    mov #0x0,r4
    .org 0x558b6 - 0x838c
L_000558b6:
    sub r5,r7
    .org 0x558b8 - 0x838c
L_000558b8:
    bra L_0005592c
    .org 0x558ba - 0x838c
L_000558ba:
    mov r7,r4
    .org 0x558bc - 0x838c
L_000558bc:
    mov.b @(0xc,r15),r0
    .org 0x558be - 0x838c
L_000558be:
    mov.l @(0x8,r15),r6
    .org 0x558c0 - 0x838c
L_000558c0:
    and #0xbf,r0
    .org 0x558c2 - 0x838c
L_000558c2:
    mov.b r0,@(0xc,r15)
    .org 0x558c4 - 0x838c
L_000558c4:
    exts.b r0,r2
    .org 0x558c6 - 0x838c
L_000558c6:
    mov #0x3a,r0
    .org 0x558c8 - 0x838c
L_000558c8:
    bra L_0005592c
    .org 0x558ca - 0x838c
L_000558ca:
    mov.b r2,@(r0,r6)
    .org 0x558cc - 0x838c
L_000558cc:
    mov.w @(0x18,gbr),r0
    .org 0x558ce - 0x838c
L_000558ce:
    bra L_0005592c
    .org 0x558d0 - 0x838c
L_000558d0:
    mov r0,r4
    .org 0x558d2 - 0x838c
L_000558d2:
    mov.w @(0x18,gbr),r0
    .org 0x558d4 - 0x838c
L_000558d4:
    extu.w r4,r4
    .org 0x558d6 - 0x838c
L_000558d6:
    mov r4,r6
    .org 0x558d8 - 0x838c
L_000558d8:
    extu.w r0,r5
    .org 0x558da - 0x838c
L_000558da:
    sub r5,r6
    .org 0x558dc - 0x838c
L_000558dc:
    cmp/pz r6
    .org 0x558de - 0x838c
L_000558de:
    bf/s L_00055908
    .org 0x558e0 - 0x838c
L_000558e0:
    mov r6,r5
    .org 0x558e2 - 0x838c
L_000558e2:
    mov.l L_00055adc,r6
    .org 0x558e4 - 0x838c
L_000558e4:
    mov.b @r6,r2
    .org 0x558e6 - 0x838c
L_000558e6:
    extu.b r2,r2
    .org 0x558e8 - 0x838c
L_000558e8:
    shll2 r2
    .org 0x558ea - 0x838c
L_000558ea:
    shll2 r2
    .org 0x558ec - 0x838c
L_000558ec:
    shll2 r2
    .org 0x558ee - 0x838c
L_000558ee:
    cmp/gt r2,r5
    .org 0x558f0 - 0x838c
L_000558f0:
    bf L_0005592c
    .org 0x558f2 - 0x838c
L_000558f2:
    mov.w @(0x18,gbr),r0
    .org 0x558f4 - 0x838c
L_000558f4:
    mov #-0x1,r5
    .org 0x558f6 - 0x838c
L_000558f6:
    extu.w r5,r4
    .org 0x558f8 - 0x838c
L_000558f8:
    extu.w r0,r6
    .org 0x558fa - 0x838c
L_000558fa:
    add r2,r6
    .org 0x558fc - 0x838c
L_000558fc:
    cmp/gt r4,r6
    .org 0x558fe - 0x838c
L_000558fe:
    bt L_0005592c
    .org 0x55900 - 0x838c
L_00055900:
    mov.w @(0x18,gbr),r0
    .org 0x55902 - 0x838c
L_00055902:
    add r2,r0
    .org 0x55904 - 0x838c
L_00055904:
    bra L_0005592c
    .org 0x55906 - 0x838c
L_00055906:
    mov r0,r4
    .org 0x55908 - 0x838c
L_00055908:
    mov.l L_00055ae0,r6
    .org 0x5590a - 0x838c
L_0005590a:
    mov.b @r6,r2
    .org 0x5590c - 0x838c
L_0005590c:
    extu.b r2,r7
    .org 0x5590e - 0x838c
L_0005590e:
    shll2 r7
    .org 0x55910 - 0x838c
L_00055910:
    shll2 r7
    .org 0x55912 - 0x838c
L_00055912:
    shll2 r7
    .org 0x55914 - 0x838c
L_00055914:
    neg r5,r2
    .org 0x55916 - 0x838c
L_00055916:
    cmp/gt r7,r2
    .org 0x55918 - 0x838c
L_00055918:
    bf L_0005592c
    .org 0x5591a - 0x838c
L_0005591a:
    mov.w @(0x18,gbr),r0
    .org 0x5591c - 0x838c
L_0005591c:
    extu.w r0,r6
    .org 0x5591e - 0x838c
L_0005591e:
    cmp/ge r7,r6
    .org 0x55920 - 0x838c
L_00055920:
    bt L_00055926
    .org 0x55922 - 0x838c
L_00055922:
    bra L_0005592c
    .org 0x55924 - 0x838c
L_00055924:
    mov #0x0,r4
    .org 0x55926 - 0x838c
L_00055926:
    mov.w @(0x18,gbr),r0
    .org 0x55928 - 0x838c
L_00055928:
    extu.w r0,r4
    .org 0x5592a - 0x838c
L_0005592a:
    sub r7,r4
    .org 0x5592c - 0x838c
L_0005592c:
    mov.l L_00055ae4,r1
    .org 0x5592e - 0x838c
L_0005592e:
    mov.w L_000559f2,r0
    .org 0x55930 - 0x838c
L_00055930:
    mov.w r4,@(r0,r1)
    .org 0x55932 - 0x838c
L_00055932:
    mov.b @(0x4,gbr),r0
    .org 0x55934 - 0x838c
L_00055934:
    cmp/eq #0x3f,r0
    .org 0x55936 - 0x838c
L_00055936:
    bf L_0005593a
    .org 0x55938 - 0x838c
L_00055938:
    mov #0x0,r4
    .org 0x5593a - 0x838c
L_0005593a:
    mov r4,r0
    .org 0x5593c - 0x838c
L_0005593c:
    mov.w r0,@(0xa,gbr)
    .org 0x5593e - 0x838c
L_0005593e:
    add #0x10,r15
    .org 0x55940 - 0x838c
L_00055940:
    ldc.l @r15+,gbr
    .org 0x55942 - 0x838c
L_00055942:
    lds.l @r15+,macl
    .org 0x55944 - 0x838c
L_00055944:
    mov.l @r15+,r14
    .org 0x55946 - 0x838c
L_00055946:
    rts
    .org 0x55948 - 0x838c
L_00055948:
    mov.l @r15+,r13
    .org 0x559f2 - 0x838c
L_000559f2:
    .word 0x0658
    .org 0x55adc - 0x838c
L_00055adc:
    .long 0x000084e6
    .org 0x55ae0 - 0x838c
L_00055ae0:
    .long 0x000084e7
    .org 0x55ae4 - 0x838c
L_00055ae4:
    .long 0xffff128c
