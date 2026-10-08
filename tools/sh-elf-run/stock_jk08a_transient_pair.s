! Exact two-call windows with actual natural coefficient and additive entries.
    .text
    .balign 4
    .org 0x8b40 - 0x8b40
L_00008b40:
    .byte 0x00
    .org 0x12176 - 0x8b40
L_00012176:
    .byte 0x46,0x46,0x48,0x4a,0x4d,0x54,0x5d,0x66
    .org 0x26370 - 0x8b40
L_00026370:
    mov.w L_00026382,r0
    .org 0x26372 - 0x8b40
L_00026372:
    extu.b r5,r5
    .org 0x26374 - 0x8b40
L_00026374:
    cmp/hs r0,r5
    .org 0x26376 - 0x8b40
L_00026376:
    bt L_0002637e
    .org 0x26378 - 0x8b40
L_00026378:
    mov.l L_00026384,r6
    .org 0x2637a - 0x8b40
L_0002637a:
    jmp @r6
    .org 0x2637c - 0x8b40
L_0002637c:
    mov #0x0,r3
    .org 0x2637e - 0x8b40
L_0002637e:
    rts
    .org 0x26380 - 0x8b40
L_00026380:
    mov.b @(0x7,r4),r0
    .org 0x26382 - 0x8b40
L_00026382:
    .word 0x00e0
    .org 0x26384 - 0x8b40
L_00026384:
    .long 0x00026a80
    .org 0x26740 - 0x8b40
L_00026740:
    cmp/hs r0,r2
    .org 0x26742 - 0x8b40
L_00026742:
    bt L_0002675c
    .org 0x26744 - 0x8b40
L_00026744:
    mov.l r0,@-r15
    .org 0x26746 - 0x8b40
L_00026746:
    sub r2,r0
    .org 0x26748 - 0x8b40
L_00026748:
    sts macl,r1
    .org 0x2674a - 0x8b40
L_0002674a:
    mul.l r3,r0
    .org 0x2674c - 0x8b40
L_0002674c:
    sts macl,r0
    .org 0x2674e - 0x8b40
L_0002674e:
    lds r1,macl
    .org 0x26750 - 0x8b40
L_00026750:
    swap.w r0,r0
    .org 0x26752 - 0x8b40
L_00026752:
    mov.l @r15+,r2
    .org 0x26754 - 0x8b40
L_00026754:
    extu.w r0,r0
    .org 0x26756 - 0x8b40
L_00026756:
    sub r0,r2
    .org 0x26758 - 0x8b40
L_00026758:
    rts
    .org 0x2675a - 0x8b40
L_0002675a:
    mov r2,r0
    .org 0x2675c - 0x8b40
L_0002675c:
    sub r0,r2
    .org 0x2675e - 0x8b40
L_0002675e:
    sts macl,r1
    .org 0x26760 - 0x8b40
L_00026760:
    mul.l r3,r2
    .org 0x26762 - 0x8b40
L_00026762:
    sts macl,r2
    .org 0x26764 - 0x8b40
L_00026764:
    lds r1,macl
    .org 0x26766 - 0x8b40
L_00026766:
    swap.w r2,r2
    .org 0x26768 - 0x8b40
L_00026768:
    extu.w r2,r2
    .org 0x2676a - 0x8b40
L_0002676a:
    rts
    .org 0x2676c - 0x8b40
L_0002676c:
    add r2,r0
    .org 0x26a80 - 0x8b40
L_00026a80:
    shlr r5
    .org 0x26a82 - 0x8b40
L_00026a82:
    rotcr r3
    .org 0x26a84 - 0x8b40
L_00026a84:
    shlr r5
    .org 0x26a86 - 0x8b40
L_00026a86:
    rotcr r3
    .org 0x26a88 - 0x8b40
L_00026a88:
    shlr r5
    .org 0x26a8a - 0x8b40
L_00026a8a:
    rotcr r3
    .org 0x26a8c - 0x8b40
L_00026a8c:
    shlr r5
    .org 0x26a8e - 0x8b40
L_00026a8e:
    rotcr r3
    .org 0x26a90 - 0x8b40
L_00026a90:
    shlr r5
    .org 0x26a92 - 0x8b40
L_00026a92:
    rotcr r3
    .org 0x26a94 - 0x8b40
L_00026a94:
    swap.w r3,r3
    .org 0x26a96 - 0x8b40
L_00026a96:
    shlr8 r0
    .org 0x26a98 - 0x8b40
L_00026a98:
    tst r0,r0
    .org 0x26a9a - 0x8b40
L_00026a9a:
    bt L_00026aaa
    .org 0x26a9c - 0x8b40
L_00026a9c:
    shll r5
    .org 0x26a9e - 0x8b40
L_00026a9e:
    add r5,r4
    .org 0x26aa0 - 0x8b40
L_00026aa0:
    mov.w @r4,r1
    .org 0x26aa2 - 0x8b40
L_00026aa2:
    mov.w @(0x2,r4),r0
    .org 0x26aa4 - 0x8b40
L_00026aa4:
    extu.w r0,r2
    .org 0x26aa6 - 0x8b40
L_00026aa6:
    bra L_00026ab4
    .org 0x26aa8 - 0x8b40
L_00026aa8:
    extu.w r1,r0
    .org 0x26aaa - 0x8b40
L_00026aaa:
    add r5,r4
    .org 0x26aac - 0x8b40
L_00026aac:
    mov.b @r4,r1
    .org 0x26aae - 0x8b40
L_00026aae:
    mov.b @(0x1,r4),r0
    .org 0x26ab0 - 0x8b40
L_00026ab0:
    extu.b r0,r2
    .org 0x26ab2 - 0x8b40
L_00026ab2:
    extu.b r1,r0
    .org 0x26ab4 - 0x8b40
L_00026ab4:
    mov.l L_00026abc,r6
    .org 0x26ab6 - 0x8b40
L_00026ab6:
    jmp @r6
    .org 0x26ab8 - 0x8b40
L_00026ab8:
    nop
    .org 0x26abc - 0x8b40
L_00026abc:
    .long 0x00026740
    .org 0x5243c - 0x8b40
L_0005243c:
    bsr L_000528be
    .org 0x5243e - 0x8b40
L_0005243e:
    nop
    .org 0x52440 - 0x8b40
L_00052440:
    bsr L_00052902
    .org 0x52442 - 0x8b40
L_00052442:
    nop
    .org 0x5249e - 0x8b40
L_0005249e:
    bsr L_000528be
    .org 0x524a0 - 0x8b40
L_000524a0:
    nop
    .org 0x524a2 - 0x8b40
L_000524a2:
    bsr L_00052902
    .org 0x524a4 - 0x8b40
L_000524a4:
    nop
    .org 0x528be - 0x8b40
L_000528be:
    sts.l pr,@-r15
    .org 0x528c0 - 0x8b40
L_000528c0:
    mov.l L_00052980,r6
    .org 0x528c2 - 0x8b40
L_000528c2:
    mov.b @r6,r2
    .org 0x528c4 - 0x8b40
L_000528c4:
    mov #-0x80,r6
    .org 0x528c6 - 0x8b40
L_000528c6:
    extu.b r6,r6
    .org 0x528c8 - 0x8b40
L_000528c8:
    extu.b r2,r2
    .org 0x528ca - 0x8b40
L_000528ca:
    cmp/ge r6,r2
    .org 0x528cc - 0x8b40
L_000528cc:
    bf L_000528d2
    .org 0x528ce - 0x8b40
L_000528ce:
    bra L_000528d6
    .org 0x528d0 - 0x8b40
L_000528d0:
    mov #-0x1,r5
    .org 0x528d2 - 0x8b40
L_000528d2:
    shll r2
    .org 0x528d4 - 0x8b40
L_000528d4:
    mov r2,r5
    .org 0x528d6 - 0x8b40
L_000528d6:
    mov.l L_00052984,r4
    .org 0x528d8 - 0x8b40
L_000528d8:
    mov.l L_00052988,r2
    .org 0x528da - 0x8b40
L_000528da:
    jsr @r2
    .org 0x528dc - 0x8b40
L_000528dc:
    extu.b r5,r5
    .org 0x528de - 0x8b40
L_000528de:
    extu.b r0,r6
    .org 0x528e0 - 0x8b40
L_000528e0:
    mov.l L_00052964,r5
    .org 0x528e2 - 0x8b40
L_000528e2:
    mov.w L_000528fc,r0
    .org 0x528e4 - 0x8b40
L_000528e4:
    shar r6
    .org 0x528e6 - 0x8b40
L_000528e6:
    mov.w @(r0,r5),r2
    .org 0x528e8 - 0x8b40
L_000528e8:
    cmp/pz r2
    .org 0x528ea - 0x8b40
L_000528ea:
    bf L_000528ee
    .org 0x528ec - 0x8b40
L_000528ec:
    mov #0x40,r6
    .org 0x528ee - 0x8b40
L_000528ee:
    mov.w L_00052900,r0
    .org 0x528f0 - 0x8b40
L_000528f0:
    lds.l @r15+,pr
    .org 0x528f2 - 0x8b40
L_000528f2:
    rts
    .org 0x528f4 - 0x8b40
L_000528f4:
    mov.b r6,@(r0,r5)
    .org 0x528fc - 0x8b40
L_000528fc:
    .word 0x07da
    .org 0x52900 - 0x8b40
L_00052900:
    .word 0x027e
    .org 0x52902 - 0x8b40
L_00052902:
    sts.l macl,@-r15
    .org 0x52904 - 0x8b40
L_00052904:
    mov.l L_00052964,r5
    .org 0x52906 - 0x8b40
L_00052906:
    mov.w L_0005295e,r0
    .org 0x52908 - 0x8b40
L_00052908:
    mov.b @(r0,r5),r2
    .org 0x5290a - 0x8b40
L_0005290a:
    mov.w L_00052960,r0
    .org 0x5290c - 0x8b40
L_0005290c:
    extu.b r2,r2
    .org 0x5290e - 0x8b40
L_0005290e:
    mov.w @(r0,r5),r6
    .org 0x52910 - 0x8b40
L_00052910:
    mul.l r6,r2
    .org 0x52912 - 0x8b40
L_00052912:
    sts macl,r6
    .org 0x52914 - 0x8b40
L_00052914:
    cmp/pz r6
    .org 0x52916 - 0x8b40
L_00052916:
    bt L_0005291e
    .org 0x52918 - 0x8b40
L_00052918:
    mov #-0x1,r2
    .org 0x5291a - 0x8b40
L_0005291a:
    extu.b r2,r2
    .org 0x5291c - 0x8b40
L_0005291c:
    add r2,r6
    .org 0x5291e - 0x8b40
L_0005291e:
    mov r6,r2
    .org 0x52920 - 0x8b40
L_00052920:
    shlr8 r2
    .org 0x52922 - 0x8b40
L_00052922:
    swap.w r2,r6
    .org 0x52924 - 0x8b40
L_00052924:
    exts.b r6,r2
    .org 0x52926 - 0x8b40
L_00052926:
    xtrct r2,r6
    .org 0x52928 - 0x8b40
L_00052928:
    cmp/pz r6
    .org 0x5292a - 0x8b40
L_0005292a:
    bf L_00052938
    .org 0x5292c - 0x8b40
L_0005292c:
    mov.w L_00052962,r2
    .org 0x5292e - 0x8b40
L_0005292e:
    cmp/gt r2,r6
    .org 0x52930 - 0x8b40
L_00052930:
    bf L_00052934
    .org 0x52932 - 0x8b40
L_00052932:
    mov r2,r6
    .org 0x52934 - 0x8b40
L_00052934:
    bra L_00052942
    .org 0x52936 - 0x8b40
L_00052936:
    mov r6,r5
    .org 0x52938 - 0x8b40
L_00052938:
    mov #-0x80,r5
    .org 0x5293a - 0x8b40
L_0005293a:
    shll8 r5
    .org 0x5293c - 0x8b40
L_0005293c:
    cmp/ge r5,r6
    .org 0x5293e - 0x8b40
L_0005293e:
    bf L_00052942
    .org 0x52940 - 0x8b40
L_00052940:
    mov r6,r5
    .org 0x52942 - 0x8b40
L_00052942:
    mov.l L_0005297c,r6
    .org 0x52944 - 0x8b40
L_00052944:
    mov.b @(0x1,r6),r0
    .org 0x52946 - 0x8b40
L_00052946:
    tst #0x20,r0
    .org 0x52948 - 0x8b40
L_00052948:
    bt L_00052954
    .org 0x5294a - 0x8b40
L_0005294a:
    mov.l L_0005298c,r6
    .org 0x5294c - 0x8b40
L_0005294c:
    mov.b @r6,r0
    .org 0x5294e - 0x8b40
L_0005294e:
    tst #0x4,r0
    .org 0x52950 - 0x8b40
L_00052950:
    bt L_00052954
    .org 0x52952 - 0x8b40
L_00052952:
    mov #0x0,r5
    .org 0x52954 - 0x8b40
L_00052954:
    mov.l L_00052990,r6
    .org 0x52956 - 0x8b40
L_00052956:
    mov r5,r0
    .org 0x52958 - 0x8b40
L_00052958:
    mov.w r0,@(0x8,r6)
    .org 0x5295a - 0x8b40
L_0005295a:
    rts
    .org 0x5295c - 0x8b40
L_0005295c:
    lds.l @r15+,macl
    .org 0x5295e - 0x8b40
L_0005295e:
    .word 0x027e
    .org 0x52960 - 0x8b40
L_00052960:
    .word 0x07da
    .org 0x52962 - 0x8b40
L_00052962:
    .word 0x7fff
    .org 0x52964 - 0x8b40
L_00052964:
    .long 0xffff128c
    .org 0x5297c - 0x8b40
L_0005297c:
    .long 0xffff245c
    .org 0x52980 - 0x8b40
L_00052980:
    .long 0xffff102c
    .org 0x52984 - 0x8b40
L_00052984:
    .long 0x00012176
    .org 0x52988 - 0x8b40
L_00052988:
    .long 0x00026370
    .org 0x5298c - 0x8b40
L_0005298c:
    .long 0x00008b40
    .org 0x52990 - 0x8b40
L_00052990:
    .long 0xffff22f8
