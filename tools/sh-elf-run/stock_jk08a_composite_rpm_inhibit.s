! Exact stock instructions and pools at their natural addresses.
    .text
    .balign 4
    .org 0x507ce - 0x507cc
L_000507ce:
    mov.l r12,@-r15
    .org 0x507d0 - 0x507cc
L_000507d0:
    mov.l r13,@-r15
    .org 0x507d2 - 0x507cc
L_000507d2:
    mov.l r14,@-r15
    .org 0x507d4 - 0x507cc
L_000507d4:
    sts.l pr,@-r15
    .org 0x507d6 - 0x507cc
L_000507d6:
    stc.l gbr,@-r15
    .org 0x507d8 - 0x507cc
L_000507d8:
    mov.l L_000508fc,r0
    .org 0x507da - 0x507cc
L_000507da:
    ldc r0,gbr
    .org 0x507dc - 0x507cc
L_000507dc:
    add #-0x4,r15
    .org 0x507de - 0x507cc
L_000507de:
    mov.l L_00050900,r14
    .org 0x507e0 - 0x507cc
L_000507e0:
    mov #0x41,r0
    .org 0x507e2 - 0x507cc
L_000507e2:
    mov.b @(r0,r14),r0
    .org 0x507e4 - 0x507cc
L_000507e4:
    tst #0x80,r0
    .org 0x507e6 - 0x507cc
L_000507e6:
    movt r0
    .org 0x507e8 - 0x507cc
L_000507e8:
    mov.l L_00050904,r6
    .org 0x507ea - 0x507cc
L_000507ea:
    xor #0x1,r0
    .org 0x507ec - 0x507cc
L_000507ec:
    extu.b r0,r7
    .org 0x507ee - 0x507cc
L_000507ee:
    mov #-0x1,r4
    .org 0x507f0 - 0x507cc
L_000507f0:
    jsr @r6
    .org 0x507f2 - 0x507cc
L_000507f2:
    mov.l r7,@r15
    .org 0x507f4 - 0x507cc
L_000507f4:
    tst r0,r0
    .org 0x507f6 - 0x507cc
L_000507f6:
    bf L_00050802
    .org 0x507f8 - 0x507cc
L_000507f8:
    mov.l L_00050904,r6
    .org 0x507fa - 0x507cc
L_000507fa:
    jsr @r6
    .org 0x507fc - 0x507cc
L_000507fc:
    mov #-0x1,r4
    .org 0x507fe - 0x507cc
L_000507fe:
    tst r0,r0
    .org 0x50800 - 0x507cc
L_00050800:
    bt L_0005083e
    .org 0x50802 - 0x507cc
L_00050802:
    mov.l L_00050908,r6
    .org 0x50804 - 0x507cc
L_00050804:
    mov.w L_00050832,r4
    .org 0x50806 - 0x507cc
L_00050806:
    mov.w @(0xc,r6),r0
    .org 0x50808 - 0x507cc
L_00050808:
    extu.w r0,r2
    .org 0x5080a - 0x507cc
L_0005080a:
    mov #0x57,r0
    .org 0x5080c - 0x507cc
L_0005080c:
    cmp/ge r4,r2
    .org 0x5080e - 0x507cc
L_0005080e:
    bf/s L_0005081a
    .org 0x50810 - 0x507cc
L_00050810:
    mov.b @(r0,r14),r0
    .org 0x50812 - 0x507cc
L_00050812:
    mov #0x1,r7
    .org 0x50814 - 0x507cc
L_00050814:
    mov.l r7,@r15
    .org 0x50816 - 0x507cc
L_00050816:
    bra L_00050822
    .org 0x50818 - 0x507cc
L_00050818:
    or #0x10,r0
    .org 0x5081a - 0x507cc
L_0005081a:
    mov.w L_00050834,r5
    .org 0x5081c - 0x507cc
L_0005081c:
    cmp/gt r5,r2
    .org 0x5081e - 0x507cc
L_0005081e:
    bt L_00050836
    .org 0x50820 - 0x507cc
L_00050820:
    and #0xef,r0
    .org 0x50822 - 0x507cc
L_00050822:
    mov r0,r6
    .org 0x50824 - 0x507cc
L_00050824:
    mov #0x57,r0
    .org 0x50826 - 0x507cc
L_00050826:
    bra L_0005083e
    .org 0x50828 - 0x507cc
L_00050828:
    mov.b r6,@(r0,r14)
    .org 0x50832 - 0x507cc
L_00050832:
    .word 0x3852
    .org 0x50834 - 0x507cc
L_00050834:
    .word 0x30bc
    .org 0x50836 - 0x507cc
L_00050836:
    tst #0x10,r0
    .org 0x50838 - 0x507cc
L_00050838:
    bt L_0005083e
    .org 0x5083a - 0x507cc
L_0005083a:
    mov #0x1,r7
    .org 0x5083c - 0x507cc
L_0005083c:
    mov.l r7,@r15
    .org 0x5083e - 0x507cc
L_0005083e:
    mov.l L_0005090c,r12
    .org 0x50840 - 0x507cc
L_00050840:
    mov #0x17,r0
    .org 0x50842 - 0x507cc
L_00050842:
    mov.b @(r0,r12),r13
    .org 0x50844 - 0x507cc
L_00050844:
    mov.b @(0x31,gbr),r0
    .org 0x50846 - 0x507cc
L_00050846:
    tst #0x1,r0
    .org 0x50848 - 0x507cc
L_00050848:
    bt/s L_0005084e
    .org 0x5084a - 0x507cc
L_0005084a:
    extu.b r13,r13
    .org 0x5084c - 0x507cc
L_0005084c:
    add #0x8,r13
    .org 0x5084e - 0x507cc
L_0005084e:
    mov #0x48,r2
    .org 0x50850 - 0x507cc
L_00050850:
    cmp/hs r2,r13
    .org 0x50852 - 0x507cc
L_00050852:
    bt/s L_0005085a
    .org 0x50854 - 0x507cc
L_00050854:
    mov #0x31,r0
    .org 0x50856 - 0x507cc
L_00050856:
    bra L_0005085c
    .org 0x50858 - 0x507cc
L_00050858:
    and.b #0xfe,@(r0,gbr)
    .org 0x5085a - 0x507cc
L_0005085a:
    or.b #0x1,@(r0,gbr)
    .org 0x5085c - 0x507cc
L_0005085c:
    mov.b @(0x5,gbr),r0
    .org 0x5085e - 0x507cc
L_0005085e:
    tst #0x40,r0
    .org 0x50860 - 0x507cc
L_00050860:
    bt L_00050872
    .org 0x50862 - 0x507cc
L_00050862:
    mov.b @(0x0,gbr),r0
    .org 0x50864 - 0x507cc
L_00050864:
    tst #0x20,r0
    .org 0x50866 - 0x507cc
L_00050866:
    bt L_00050872
    .org 0x50868 - 0x507cc
L_00050868:
    mov.b @(0x31,gbr),r0
    .org 0x5086a - 0x507cc
L_0005086a:
    tst #0x1,r0
    .org 0x5086c - 0x507cc
L_0005086c:
    bt L_00050872
    .org 0x5086e - 0x507cc
L_0005086e:
    mov #0x1,r7
    .org 0x50870 - 0x507cc
L_00050870:
    mov.l r7,@r15
    .org 0x50872 - 0x507cc
L_00050872:
    mov.l L_000508ec,r2
    .org 0x50874 - 0x507cc
L_00050874:
    mov #0x7a,r0
    .org 0x50876 - 0x507cc
L_00050876:
    mov #0x3f,r5
    .org 0x50878 - 0x507cc
L_00050878:
    mov.b @(r0,r2),r6
    .org 0x5087a - 0x507cc
L_0005087a:
    extu.b r6,r6
    .org 0x5087c - 0x507cc
L_0005087c:
    cmp/gt r5,r6
    .org 0x5087e - 0x507cc
L_0005087e:
    bf L_00050882
    .org 0x50880 - 0x507cc
L_00050880:
    mov #0x3f,r6
    .org 0x50882 - 0x507cc
L_00050882:
    mov r6,r5
    .org 0x50884 - 0x507cc
L_00050884:
    shll2 r5
    .org 0x50886 - 0x507cc
L_00050886:
    mov.l L_00050910,r4
    .org 0x50888 - 0x507cc
L_00050888:
    mov.l L_00050914,r2
    .org 0x5088a - 0x507cc
L_0005088a:
    jsr @r2
    .org 0x5088c - 0x507cc
L_0005088c:
    extu.b r5,r5
    .org 0x5088e - 0x507cc
L_0005088e:
    extu.b r0,r6
    .org 0x50890 - 0x507cc
L_00050890:
    mov.l L_00050918,r5
    .org 0x50892 - 0x507cc
L_00050892:
    mov.w L_000508e6,r0
    .org 0x50894 - 0x507cc
L_00050894:
    shll r6
    .org 0x50896 - 0x507cc
L_00050896:
    mov.w r6,@(r0,r5)
    .org 0x50898 - 0x507cc
L_00050898:
    mov #0x20,r0
    .org 0x5089a - 0x507cc
L_0005089a:
    mov.w @(r0,r12),r13
    .org 0x5089c - 0x507cc
L_0005089c:
    mov.b @(0x47,gbr),r0
    .org 0x5089e - 0x507cc
L_0005089e:
    tst #0x4,r0
    .org 0x508a0 - 0x507cc
L_000508a0:
    bt/s L_000508ac
    .org 0x508a2 - 0x507cc
L_000508a2:
    extu.w r13,r13
    .org 0x508a4 - 0x507cc
L_000508a4:
    mov.l L_0005091c,r6
    .org 0x508a6 - 0x507cc
L_000508a6:
    mov.w @r6,r2
    .org 0x508a8 - 0x507cc
L_000508a8:
    extu.w r2,r2
    .org 0x508aa - 0x507cc
L_000508aa:
    add r2,r13
    .org 0x508ac - 0x507cc
L_000508ac:
    mov.l L_00050918,r5
    .org 0x508ae - 0x507cc
L_000508ae:
    mov.w L_000508e6,r0
    .org 0x508b0 - 0x507cc
L_000508b0:
    mov.w @(r0,r5),r6
    .org 0x508b2 - 0x507cc
L_000508b2:
    extu.w r6,r6
    .org 0x508b4 - 0x507cc
L_000508b4:
    cmp/hs r6,r13
    .org 0x508b6 - 0x507cc
L_000508b6:
    bt/s L_000508be
    .org 0x508b8 - 0x507cc
L_000508b8:
    mov #0x47,r0
    .org 0x508ba - 0x507cc
L_000508ba:
    bra L_000508c0
    .org 0x508bc - 0x507cc
L_000508bc:
    and.b #0xfb,@(r0,gbr)
    .org 0x508be - 0x507cc
L_000508be:
    or.b #0x4,@(r0,gbr)
    .org 0x508c0 - 0x507cc
L_000508c0:
    mov.b @(0x76,gbr),r0
    .org 0x508c2 - 0x507cc
L_000508c2:
    tst #0x4,r0
    .org 0x508c4 - 0x507cc
L_000508c4:
    bf L_000508cc
    .org 0x508c6 - 0x507cc
L_000508c6:
    mov.b @(0x7a,gbr),r0
    .org 0x508c8 - 0x507cc
L_000508c8:
    tst #0x1,r0
    .org 0x508ca - 0x507cc
L_000508ca:
    bt L_000508d6
    .org 0x508cc - 0x507cc
L_000508cc:
    mov.b @(0x47,gbr),r0
    .org 0x508ce - 0x507cc
L_000508ce:
    tst #0x4,r0
    .org 0x508d0 - 0x507cc
L_000508d0:
    bt L_000508d6
    .org 0x508d2 - 0x507cc
L_000508d2:
    mov #0x1,r7
    .org 0x508d4 - 0x507cc
L_000508d4:
    mov.l r7,@r15
    .org 0x508d6 - 0x507cc
L_000508d6:
    mov.l @r15,r0
    .org 0x508d8 - 0x507cc
L_000508d8:
    add #0x4,r15
    .org 0x508da - 0x507cc
L_000508da:
    ldc.l @r15+,gbr
    .org 0x508dc - 0x507cc
L_000508dc:
    lds.l @r15+,pr
    .org 0x508de - 0x507cc
L_000508de:
    mov.l @r15+,r14
    .org 0x508e0 - 0x507cc
L_000508e0:
    mov.l @r15+,r13
    .org 0x508e2 - 0x507cc
L_000508e2:
    rts
    .org 0x508e4 - 0x507cc
L_000508e4:
    mov.l @r15+,r12
    .org 0x508e6 - 0x507cc
L_000508e6:
    .word 0x53e
    .org 0x508ec - 0x507cc
L_000508ec:
    .long 0xffff1094
    .org 0x508fc - 0x507cc
L_000508fc:
    .long 0xffff2458
    .org 0x50900 - 0x507cc
L_00050900:
    .long 0xffff41a9
    .org 0x50904 - 0x507cc
L_00050904:
    .long 0x259e4
    .org 0x50908 - 0x507cc
L_00050908:
    .long 0xffff102c
    .org 0x5090c - 0x507cc
L_0005090c:
    .long 0xffff119c
    .org 0x50910 - 0x507cc
L_00050910:
    .long 0x12a32
    .org 0x50914 - 0x507cc
L_00050914:
    .long 0x26370
    .org 0x50918 - 0x507cc
L_00050918:
    .long 0xffff128c
    .org 0x5091c - 0x507cc
L_0005091c:
    .long 0x9462
