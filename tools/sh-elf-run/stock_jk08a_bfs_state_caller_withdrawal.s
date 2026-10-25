! Complete stock BFS-dependent state caller and real byte-curve/diagnostic helpers.
    .text
    .balign 4
    .set ORIGIN,0x25e20
    .org 0x25e20-ORIGIN
L_00025e20:
    mov.l P_00025f10,r1
    .org 0x25e22-ORIGIN
L_00025e22:
    exts.w r4,r0
    .org 0x25e24-ORIGIN
L_00025e24:
    cmp/eq #-0x1,r0
    .org 0x25e26-ORIGIN
L_00025e26:
    bt L_00025e3e
    .org 0x25e28-ORIGIN
L_00025e28:
    mov r1,r6
    .org 0x25e2a-ORIGIN
L_00025e2a:
    mov r0,r2
    .org 0x25e2c-ORIGIN
L_00025e2c:
    shll r2
    .org 0x25e2e-ORIGIN
L_00025e2e:
    add r0,r2
    .org 0x25e30-ORIGIN
L_00025e30:
    add r2,r6
    .org 0x25e32-ORIGIN
L_00025e32:
    mov.b @(0x1,r6),r0
    .org 0x25e34-ORIGIN
L_00025e34:
    tst #0x80,r0
    .org 0x25e36-ORIGIN
L_00025e36:
    movt r0
    .org 0x25e38-ORIGIN
L_00025e38:
    xor #0x1,r0
    .org 0x25e3a-ORIGIN
L_00025e3a:
    bra L_00025e40
    .org 0x25e3c-ORIGIN
L_00025e3c:
    extu.b r0,r2
    .org 0x25e3e-ORIGIN
L_00025e3e:
    mov #0x0,r2
    .org 0x25e40-ORIGIN
L_00025e40:
    rts
    .org 0x25e42-ORIGIN
L_00025e42:
    mov r2,r0
    .org 0x25f10-ORIGIN
P_00025f10:
    .byte 0xff
    .org 0x25f11-ORIGIN
P_00025f11:
    .byte 0xff
    .org 0x25f12-ORIGIN
P_00025f12:
    .byte 0x57
    .org 0x25f13-ORIGIN
P_00025f13:
    .byte 0x18
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
    .org 0x3a750-ORIGIN
L_0003a750:
    sts.l pr,@-r15
    .org 0x3a752-ORIGIN
L_0003a752:
    stc.l gbr,@-r15
    .org 0x3a754-ORIGIN
L_0003a754:
    mov.l P_0003a8d0,r0
    .org 0x3a756-ORIGIN
L_0003a756:
    ldc r0,gbr
    .org 0x3a758-ORIGIN
L_0003a758:
    add #-0x8,r15
    .org 0x3a75a-ORIGIN
L_0003a75a:
    mov.l @(0xc,gbr),r0
    .org 0x3a75c-ORIGIN
L_0003a75c:
    tst r0,r0
    .org 0x3a75e-ORIGIN
L_0003a75e:
    bf/s L_0003a788
    .org 0x3a760-ORIGIN
L_0003a760:
    mov r0,r4
    .org 0x3a762-ORIGIN
L_0003a762:
    mov.l P_0003a8d4,r6
    .org 0x3a764-ORIGIN
L_0003a764:
    mov.b @(0xa,r6),r0
    .org 0x3a766-ORIGIN
L_0003a766:
    tst #0x1,r0
    .org 0x3a768-ORIGIN
L_0003a768:
    bt L_0003a7b2
    .org 0x3a76a-ORIGIN
L_0003a76a:
    mov.l P_0003a8d8,r7
    .org 0x3a76c-ORIGIN
L_0003a76c:
    mov.l P_0003a8dc,r4
    .org 0x3a76e-ORIGIN
L_0003a76e:
    mov.b @(0x5,r7),r0
    .org 0x3a770-ORIGIN
L_0003a770:
    mov.l P_0003a8e0,r2
    .org 0x3a772-ORIGIN
L_0003a772:
    jsr @r2
    .org 0x3a774-ORIGIN
L_0003a774:
    extu.b r0,r5
    .org 0x3a776-ORIGIN
L_0003a776:
    mov r0,r2
    .org 0x3a778-ORIGIN
L_0003a778:
    mov.l P_0003a8e4,r6
    .org 0x3a77a-ORIGIN
L_0003a77a:
    mov #0x46,r0
    .org 0x3a77c-ORIGIN
L_0003a77c:
    mov.l P_0003a8e8,r5
    .org 0x3a77e-ORIGIN
L_0003a77e:
    shll2 r0
    .org 0x3a780-ORIGIN
L_0003a780:
    mov.b r2,@(r0,r6)
    .org 0x3a782-ORIGIN
L_0003a782:
    mov #0x49,r0
    .org 0x3a784-ORIGIN
L_0003a784:
    bra L_0003a7a0
    .org 0x3a786-ORIGIN
L_0003a786:
    mov.b r2,@(r0,r5)
    .org 0x3a788-ORIGIN
L_0003a788:
    mov r4,r0
    .org 0x3a78a-ORIGIN
L_0003a78a:
    cmp/eq #0x1,r0
    .org 0x3a78c-ORIGIN
L_0003a78c:
    bf L_0003a7a4
    .org 0x3a78e-ORIGIN
L_0003a78e:
    mov.l P_0003a8d4,r6
    .org 0x3a790-ORIGIN
L_0003a790:
    mov.b @(0xa,r6),r0
    .org 0x3a792-ORIGIN
L_0003a792:
    tst #0x1,r0
    .org 0x3a794-ORIGIN
L_0003a794:
    bt L_0003a7b2
    .org 0x3a796-ORIGIN
L_0003a796:
    mov.l P_0003a8e8,r5
    .org 0x3a798-ORIGIN
L_0003a798:
    mov #0x49,r0
    .org 0x3a79a-ORIGIN
L_0003a79a:
    mov.b @(r0,r5),r2
    .org 0x3a79c-ORIGIN
L_0003a79c:
    tst r2,r2
    .org 0x3a79e-ORIGIN
L_0003a79e:
    bt L_0003a7b6
    .org 0x3a7a0-ORIGIN
L_0003a7a0:
    bra L_0003a7b8
    .org 0x3a7a2-ORIGIN
L_0003a7a2:
    mov #0x1,r4
    .org 0x3a7a4-ORIGIN
L_0003a7a4:
    mov r4,r0
    .org 0x3a7a6-ORIGIN
L_0003a7a6:
    cmp/eq #0x2,r0
    .org 0x3a7a8-ORIGIN
L_0003a7a8:
    bf L_0003a7bc
    .org 0x3a7aa-ORIGIN
L_0003a7aa:
    mov.l P_0003a8d4,r6
    .org 0x3a7ac-ORIGIN
L_0003a7ac:
    mov.b @(0xa,r6),r0
    .org 0x3a7ae-ORIGIN
L_0003a7ae:
    tst #0x1,r0
    .org 0x3a7b0-ORIGIN
L_0003a7b0:
    bf L_0003a7b6
    .org 0x3a7b2-ORIGIN
L_0003a7b2:
    bra L_0003a7b8
    .org 0x3a7b4-ORIGIN
L_0003a7b4:
    mov #0x0,r4
    .org 0x3a7b6-ORIGIN
L_0003a7b6:
    mov #0x2,r4
    .org 0x3a7b8-ORIGIN
L_0003a7b8:
    mov r4,r0
    .org 0x3a7ba-ORIGIN
L_0003a7ba:
    mov.l r0,@(0xc,gbr)
    .org 0x3a7bc-ORIGIN
L_0003a7bc:
    mov.l P_0003a8d8,r7
    .org 0x3a7be-ORIGIN
L_0003a7be:
    mov.l P_0003a8ec,r6
    .org 0x3a7c0-ORIGIN
L_0003a7c0:
    mov.b @(0x7,r7),r0
    .org 0x3a7c2-ORIGIN
L_0003a7c2:
    extu.b r0,r5
    .org 0x3a7c4-ORIGIN
L_0003a7c4:
    mov.b @(0xa,r6),r0
    .org 0x3a7c6-ORIGIN
L_0003a7c6:
    tst #0x80,r0
    .org 0x3a7c8-ORIGIN
L_0003a7c8:
    bt L_0003a7cc
    .org 0x3a7ca-ORIGIN
L_0003a7ca:
    add #0x4,r5
    .org 0x3a7cc-ORIGIN
L_0003a7cc:
    mov.l P_0003a8f0,r6
    .org 0x3a7ce-ORIGIN
L_0003a7ce:
    mov.b @r6,r2
    .org 0x3a7d0-ORIGIN
L_0003a7d0:
    extu.b r2,r2
    .org 0x3a7d2-ORIGIN
L_0003a7d2:
    cmp/hs r2,r5
    .org 0x3a7d4-ORIGIN
L_0003a7d4:
    bt L_0003a7de
    .org 0x3a7d6-ORIGIN
L_0003a7d6:
    mov.l P_0003a8ec,r6
    .org 0x3a7d8-ORIGIN
L_0003a7d8:
    mov.b @(0xa,r6),r0
    .org 0x3a7da-ORIGIN
L_0003a7da:
    bra L_0003a7e4
    .org 0x3a7dc-ORIGIN
L_0003a7dc:
    and #0x7f,r0
    .org 0x3a7de-ORIGIN
L_0003a7de:
    mov.l P_0003a8ec,r6
    .org 0x3a7e0-ORIGIN
L_0003a7e0:
    mov.b @(0xa,r6),r0
    .org 0x3a7e2-ORIGIN
L_0003a7e2:
    or #0x80,r0
    .org 0x3a7e4-ORIGIN
L_0003a7e4:
    mov.b r0,@(0xa,r6)
    .org 0x3a7e6-ORIGIN
L_0003a7e6:
    mov.l @(0x10,gbr),r0
    .org 0x3a7e8-ORIGIN
L_0003a7e8:
    tst r0,r0
    .org 0x3a7ea-ORIGIN
L_0003a7ea:
    bf/s L_0003a892
    .org 0x3a7ec-ORIGIN
L_0003a7ec:
    mov r0,r2
    .org 0x3a7ee-ORIGIN
L_0003a7ee:
    mov.l P_0003a8d4,r6
    .org 0x3a7f0-ORIGIN
L_0003a7f0:
    mov.b @(0xd,r6),r0
    .org 0x3a7f2-ORIGIN
L_0003a7f2:
    tst #0x40,r0
    .org 0x3a7f4-ORIGIN
L_0003a7f4:
    bt L_0003a88c
    .org 0x3a7f6-ORIGIN
L_0003a7f6:
    mov r4,r0
    .org 0x3a7f8-ORIGIN
L_0003a7f8:
    cmp/eq #0x2,r0
    .org 0x3a7fa-ORIGIN
L_0003a7fa:
    bf L_0003a88c
    .org 0x3a7fc-ORIGIN
L_0003a7fc:
    mov.l P_0003a8ec,r6
    .org 0x3a7fe-ORIGIN
L_0003a7fe:
    mov.b @(0xa,r6),r0
    .org 0x3a800-ORIGIN
L_0003a800:
    tst #0x80,r0
    .org 0x3a802-ORIGIN
L_0003a802:
    bt L_0003a88c
    .org 0x3a804-ORIGIN
L_0003a804:
    mov.l P_0003a8d4,r6
    .org 0x3a806-ORIGIN
L_0003a806:
    mov.b @(0x1,r6),r0
    .org 0x3a808-ORIGIN
L_0003a808:
    tst #0x20,r0
    .org 0x3a80a-ORIGIN
L_0003a80a:
    bt L_0003a88c
    .org 0x3a80c-ORIGIN
L_0003a80c:
    mov.l P_0003a8f4,r2
    .org 0x3a80e-ORIGIN
L_0003a80e:
    mov.w P_0003a870,r4
    .org 0x3a810-ORIGIN
L_0003a810:
    jsr @r2
    .org 0x3a812-ORIGIN
L_0003a812:
    nop
    .org 0x3a814-ORIGIN
L_0003a814:
    tst r0,r0
    .org 0x3a816-ORIGIN
L_0003a816:
    bf L_0003a88c
    .org 0x3a818-ORIGIN
L_0003a818:
    mov.l P_0003a8f8,r2
    .org 0x3a81a-ORIGIN
L_0003a81a:
    mov.l P_0003a8ec,r6
    .org 0x3a81c-ORIGIN
L_0003a81c:
    mov.b @r2,r4
    .org 0x3a81e-ORIGIN
L_0003a81e:
    mov.b @(0x1,r6),r0
    .org 0x3a820-ORIGIN
L_0003a820:
    extu.b r4,r4
    .org 0x3a822-ORIGIN
L_0003a822:
    tst #0x10,r0
    .org 0x3a824-ORIGIN
L_0003a824:
    mov r4,r7
    .org 0x3a826-ORIGIN
L_0003a826:
    bf/s L_0003a872
    .org 0x3a828-ORIGIN
L_0003a828:
    shll8 r7
    .org 0x3a82a-ORIGIN
L_0003a82a:
    mov.l P_0003a8fc,r3
    .org 0x3a82c-ORIGIN
L_0003a82c:
    mov r4,r2
    .org 0x3a82e-ORIGIN
L_0003a82e:
    mov.l P_0003a900,r1
    .org 0x3a830-ORIGIN
L_0003a830:
    shll8 r2
    .org 0x3a832-ORIGIN
L_0003a832:
    mov.w @(0x2,r3),r0
    .org 0x3a834-ORIGIN
L_0003a834:
    extu.w r0,r5
    .org 0x3a836-ORIGIN
L_0003a836:
    mov.w @(0x1a,r1),r0
    .org 0x3a838-ORIGIN
L_0003a838:
    cmp/ge r2,r5
    .org 0x3a83a-ORIGIN
L_0003a83a:
    extu.w r0,r1
    .org 0x3a83c-ORIGIN
L_0003a83c:
    mov.w @(0x2,r3),r0
    .org 0x3a83e-ORIGIN
L_0003a83e:
    shll2 r1
    .org 0x3a840-ORIGIN
L_0003a840:
    mov.l r1,@r15
    .org 0x3a842-ORIGIN
L_0003a842:
    extu.w r0,r1
    .org 0x3a844-ORIGIN
L_0003a844:
    add r7,r1
    .org 0x3a846-ORIGIN
L_0003a846:
    mov.l @r15,r6
    .org 0x3a848-ORIGIN
L_0003a848:
    bf/s L_0003a86a
    .org 0x3a84a-ORIGIN
L_0003a84a:
    mov.l r1,@(0x4,r15)
    .org 0x3a84c-ORIGIN
L_0003a84c:
    cmp/hi r6,r1
    .org 0x3a84e-ORIGIN
L_0003a84e:
    bf L_0003a88c
    .org 0x3a850-ORIGIN
L_0003a850:
    mov.l P_0003a900,r3
    .org 0x3a852-ORIGIN
L_0003a852:
    shll8 r4
    .org 0x3a854-ORIGIN
L_0003a854:
    mov.l P_0003a8fc,r1
    .org 0x3a856-ORIGIN
L_0003a856:
    mov.w @(0x1a,r3),r0
    .org 0x3a858-ORIGIN
L_0003a858:
    extu.w r0,r5
    .org 0x3a85a-ORIGIN
L_0003a85a:
    mov.w @(0x2,r1),r0
    .org 0x3a85c-ORIGIN
L_0003a85c:
    shll2 r5
    .org 0x3a85e-ORIGIN
L_0003a85e:
    extu.w r0,r6
    .org 0x3a860-ORIGIN
L_0003a860:
    sub r4,r6
    .org 0x3a862-ORIGIN
L_0003a862:
    cmp/ge r6,r5
    .org 0x3a864-ORIGIN
L_0003a864:
    bf L_0003a88c
    .org 0x3a866-ORIGIN
L_0003a866:
    bra L_0003a88e
    .org 0x3a868-ORIGIN
L_0003a868:
    mov #0x1,r2
    .org 0x3a86a-ORIGIN
L_0003a86a:
    cmp/hi r6,r1
    .org 0x3a86c-ORIGIN
L_0003a86c:
    bra L_0003a88e
    .org 0x3a86e-ORIGIN
L_0003a86e:
    movt r2
    .org 0x3a870-ORIGIN
P_0003a870:
    .byte 0x01
    .org 0x3a871-ORIGIN
P_0003a871:
    .byte 0x29
    .org 0x3a872-ORIGIN
L_0003a872:
    mov.l P_0003a8fc,r3
    .org 0x3a874-ORIGIN
L_0003a874:
    mov.w @(0x2,r3),r0
    .org 0x3a876-ORIGIN
L_0003a876:
    extu.w r0,r5
    .org 0x3a878-ORIGIN
L_0003a878:
    cmp/hs r7,r5
    .org 0x3a87a-ORIGIN
L_0003a87a:
    bt L_0003a88c
    .org 0x3a87c-ORIGIN
L_0003a87c:
    mov.l P_0003a900,r3
    .org 0x3a87e-ORIGIN
L_0003a87e:
    shll8 r4
    .org 0x3a880-ORIGIN
L_0003a880:
    sub r5,r4
    .org 0x3a882-ORIGIN
L_0003a882:
    mov.w @(0x1a,r3),r0
    .org 0x3a884-ORIGIN
L_0003a884:
    extu.w r0,r6
    .org 0x3a886-ORIGIN
L_0003a886:
    shll2 r6
    .org 0x3a888-ORIGIN
L_0003a888:
    bra L_0003a89e
    .org 0x3a88a-ORIGIN
L_0003a88a:
    cmp/gt r4,r6
    .org 0x3a88c-ORIGIN
L_0003a88c:
    mov #0x0,r2
    .org 0x3a88e-ORIGIN
L_0003a88e:
    bra L_0003a8a4
    .org 0x3a890-ORIGIN
L_0003a890:
    mov r2,r0
    .org 0x3a892-ORIGIN
L_0003a892:
    mov r2,r0
    .org 0x3a894-ORIGIN
L_0003a894:
    cmp/eq #0x1,r0
    .org 0x3a896-ORIGIN
L_0003a896:
    bf L_0003a8a6
    .org 0x3a898-ORIGIN
L_0003a898:
    mov.l P_0003a8d4,r6
    .org 0x3a89a-ORIGIN
L_0003a89a:
    mov.b @(0x1,r6),r0
    .org 0x3a89c-ORIGIN
L_0003a89c:
    tst #0x20,r0
    .org 0x3a89e-ORIGIN
L_0003a89e:
    movt r0
    .org 0x3a8a0-ORIGIN
L_0003a8a0:
    xor #0x1,r0
    .org 0x3a8a2-ORIGIN
L_0003a8a2:
    mov r0,r2
    .org 0x3a8a4-ORIGIN
L_0003a8a4:
    mov.l r0,@(0x10,gbr)
    .org 0x3a8a6-ORIGIN
L_0003a8a6:
    tst r2,r2
    .org 0x3a8a8-ORIGIN
L_0003a8a8:
    bf L_0003a8b4
    .org 0x3a8aa-ORIGIN
L_0003a8aa:
    mov.l P_0003a8d4,r6
    .org 0x3a8ac-ORIGIN
L_0003a8ac:
    mov.l P_0003a8d4,r5
    .org 0x3a8ae-ORIGIN
L_0003a8ae:
    mov.b @(0x9,r6),r0
    .org 0x3a8b0-ORIGIN
L_0003a8b0:
    bra L_0003a8c2
    .org 0x3a8b2-ORIGIN
L_0003a8b2:
    and #0xdf,r0
    .org 0x3a8b4-ORIGIN
L_0003a8b4:
    mov r2,r0
    .org 0x3a8b6-ORIGIN
L_0003a8b6:
    cmp/eq #0x1,r0
    .org 0x3a8b8-ORIGIN
L_0003a8b8:
    bf L_0003a8c4
    .org 0x3a8ba-ORIGIN
L_0003a8ba:
    mov.l P_0003a8d4,r6
    .org 0x3a8bc-ORIGIN
L_0003a8bc:
    mov.l P_0003a8d4,r5
    .org 0x3a8be-ORIGIN
L_0003a8be:
    mov.b @(0x9,r6),r0
    .org 0x3a8c0-ORIGIN
L_0003a8c0:
    or #0x20,r0
    .org 0x3a8c2-ORIGIN
L_0003a8c2:
    mov.b r0,@(0x9,r5)
    .org 0x3a8c4-ORIGIN
L_0003a8c4:
    add #0x8,r15
    .org 0x3a8c6-ORIGIN
L_0003a8c6:
    ldc.l @r15+,gbr
    .org 0x3a8c8-ORIGIN
L_0003a8c8:
    lds.l @r15+,pr
    .org 0x3a8ca-ORIGIN
L_0003a8ca:
    rts
    .org 0x3a8cc-ORIGIN
L_0003a8cc:
    nop
    .org 0x3a8d0-ORIGIN
P_0003a8d0:
    .byte 0xff
    .org 0x3a8d1-ORIGIN
P_0003a8d1:
    .byte 0xff
    .org 0x3a8d2-ORIGIN
P_0003a8d2:
    .byte 0x39
    .org 0x3a8d3-ORIGIN
P_0003a8d3:
    .byte 0xc4
    .org 0x3a8d4-ORIGIN
P_0003a8d4:
    .byte 0xff
    .org 0x3a8d5-ORIGIN
P_0003a8d5:
    .byte 0xff
    .org 0x3a8d6-ORIGIN
P_0003a8d6:
    .byte 0x24
    .org 0x3a8d7-ORIGIN
P_0003a8d7:
    .byte 0x58
    .org 0x3a8d8-ORIGIN
P_0003a8d8:
    .byte 0xff
    .org 0x3a8d9-ORIGIN
P_0003a8d9:
    .byte 0xff
    .org 0x3a8da-ORIGIN
P_0003a8da:
    .byte 0x10
    .org 0x3a8db-ORIGIN
P_0003a8db:
    .byte 0x72
    .org 0x3a8dc-ORIGIN
P_0003a8dc:
    .byte 0x00
    .org 0x3a8dd-ORIGIN
P_0003a8dd:
    .byte 0x01
    .org 0x3a8de-ORIGIN
P_0003a8de:
    .byte 0x2a
    .org 0x3a8df-ORIGIN
P_0003a8df:
    .byte 0x3a
    .org 0x3a8e0-ORIGIN
P_0003a8e0:
    .byte 0x00
    .org 0x3a8e1-ORIGIN
P_0003a8e1:
    .byte 0x02
    .org 0x3a8e2-ORIGIN
P_0003a8e2:
    .byte 0x63
    .org 0x3a8e3-ORIGIN
P_0003a8e3:
    .byte 0x70
    .org 0x3a8e4-ORIGIN
P_0003a8e4:
    .byte 0xff
    .org 0x3a8e5-ORIGIN
P_0003a8e5:
    .byte 0xff
    .org 0x3a8e6-ORIGIN
P_0003a8e6:
    .byte 0x1e
    .org 0x3a8e7-ORIGIN
P_0003a8e7:
    .byte 0x60
    .org 0x3a8e8-ORIGIN
P_0003a8e8:
    .byte 0xff
    .org 0x3a8e9-ORIGIN
P_0003a8e9:
    .byte 0xff
    .org 0x3a8ea-ORIGIN
P_0003a8ea:
    .byte 0x24
    .org 0x3a8eb-ORIGIN
P_0003a8eb:
    .byte 0xf9
    .org 0x3a8ec-ORIGIN
P_0003a8ec:
    .byte 0xff
    .org 0x3a8ed-ORIGIN
P_0003a8ed:
    .byte 0xff
    .org 0x3a8ee-ORIGIN
P_0003a8ee:
    .byte 0x24
    .org 0x3a8ef-ORIGIN
P_0003a8ef:
    .byte 0xb0
    .org 0x3a8f0-ORIGIN
P_0003a8f0:
    .byte 0x00
    .org 0x3a8f1-ORIGIN
P_0003a8f1:
    .byte 0x00
    .org 0x3a8f2-ORIGIN
P_0003a8f2:
    .byte 0x87
    .org 0x3a8f3-ORIGIN
P_0003a8f3:
    .byte 0x5c
    .org 0x3a8f4-ORIGIN
P_0003a8f4:
    .byte 0x00
    .org 0x3a8f5-ORIGIN
P_0003a8f5:
    .byte 0x02
    .org 0x3a8f6-ORIGIN
P_0003a8f6:
    .byte 0x5e
    .org 0x3a8f7-ORIGIN
P_0003a8f7:
    .byte 0x20
    .org 0x3a8f8-ORIGIN
P_0003a8f8:
    .byte 0x00
    .org 0x3a8f9-ORIGIN
P_0003a8f9:
    .byte 0x00
    .org 0x3a8fa-ORIGIN
P_0003a8fa:
    .byte 0x8a
    .org 0x3a8fb-ORIGIN
P_0003a8fb:
    .byte 0xd9
    .org 0x3a8fc-ORIGIN
P_0003a8fc:
    .byte 0xff
    .org 0x3a8fd-ORIGIN
P_0003a8fd:
    .byte 0xff
    .org 0x3a8fe-ORIGIN
P_0003a8fe:
    .byte 0x10
    .org 0x3a8ff-ORIGIN
P_0003a8ff:
    .byte 0x24
    .org 0x3a900-ORIGIN
P_0003a900:
    .byte 0xff
    .org 0x3a901-ORIGIN
P_0003a901:
    .byte 0xff
    .org 0x3a902-ORIGIN
P_0003a902:
    .byte 0x10
    .org 0x3a903-ORIGIN
P_0003a903:
    .byte 0x48
