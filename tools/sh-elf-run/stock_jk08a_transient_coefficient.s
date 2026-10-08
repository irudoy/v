! Complete natural entry and actual callees at their exact stock addresses.
    .text
    .balign 4
    .org 0x12176 - 0x12174
L_00012176:
    .byte 0x46,0x46,0x48,0x4a,0x4d,0x54,0x5d,0x66
    .org 0x26370 - 0x12174
L_00026370:
    mov.w L_00026382,r0
    .org 0x26372 - 0x12174
L_00026372:
    extu.b r5,r5
    .org 0x26374 - 0x12174
L_00026374:
    cmp/hs r0,r5
    .org 0x26376 - 0x12174
L_00026376:
    bt L_0002637e
    .org 0x26378 - 0x12174
L_00026378:
    mov.l L_00026384,r6
    .org 0x2637a - 0x12174
L_0002637a:
    jmp @r6
    .org 0x2637c - 0x12174
L_0002637c:
    mov #0x0,r3
    .org 0x2637e - 0x12174
L_0002637e:
    rts
    .org 0x26380 - 0x12174
L_00026380:
    mov.b @(0x7,r4),r0
    .org 0x26382 - 0x12174
L_00026382:
    .word 0x00e0
    .org 0x26384 - 0x12174
L_00026384:
    .long 0x00026a80
    .org 0x26740 - 0x12174
L_00026740:
    cmp/hs r0,r2
    .org 0x26742 - 0x12174
L_00026742:
    bt L_0002675c
    .org 0x26744 - 0x12174
L_00026744:
    mov.l r0,@-r15
    .org 0x26746 - 0x12174
L_00026746:
    sub r2,r0
    .org 0x26748 - 0x12174
L_00026748:
    sts macl,r1
    .org 0x2674a - 0x12174
L_0002674a:
    mul.l r3,r0
    .org 0x2674c - 0x12174
L_0002674c:
    sts macl,r0
    .org 0x2674e - 0x12174
L_0002674e:
    lds r1,macl
    .org 0x26750 - 0x12174
L_00026750:
    swap.w r0,r0
    .org 0x26752 - 0x12174
L_00026752:
    mov.l @r15+,r2
    .org 0x26754 - 0x12174
L_00026754:
    extu.w r0,r0
    .org 0x26756 - 0x12174
L_00026756:
    sub r0,r2
    .org 0x26758 - 0x12174
L_00026758:
    rts
    .org 0x2675a - 0x12174
L_0002675a:
    mov r2,r0
    .org 0x2675c - 0x12174
L_0002675c:
    sub r0,r2
    .org 0x2675e - 0x12174
L_0002675e:
    sts macl,r1
    .org 0x26760 - 0x12174
L_00026760:
    mul.l r3,r2
    .org 0x26762 - 0x12174
L_00026762:
    sts macl,r2
    .org 0x26764 - 0x12174
L_00026764:
    lds r1,macl
    .org 0x26766 - 0x12174
L_00026766:
    swap.w r2,r2
    .org 0x26768 - 0x12174
L_00026768:
    extu.w r2,r2
    .org 0x2676a - 0x12174
L_0002676a:
    rts
    .org 0x2676c - 0x12174
L_0002676c:
    add r2,r0
    .org 0x26a80 - 0x12174
L_00026a80:
    shlr r5
    .org 0x26a82 - 0x12174
L_00026a82:
    rotcr r3
    .org 0x26a84 - 0x12174
L_00026a84:
    shlr r5
    .org 0x26a86 - 0x12174
L_00026a86:
    rotcr r3
    .org 0x26a88 - 0x12174
L_00026a88:
    shlr r5
    .org 0x26a8a - 0x12174
L_00026a8a:
    rotcr r3
    .org 0x26a8c - 0x12174
L_00026a8c:
    shlr r5
    .org 0x26a8e - 0x12174
L_00026a8e:
    rotcr r3
    .org 0x26a90 - 0x12174
L_00026a90:
    shlr r5
    .org 0x26a92 - 0x12174
L_00026a92:
    rotcr r3
    .org 0x26a94 - 0x12174
L_00026a94:
    swap.w r3,r3
    .org 0x26a96 - 0x12174
L_00026a96:
    shlr8 r0
    .org 0x26a98 - 0x12174
L_00026a98:
    tst r0,r0
    .org 0x26a9a - 0x12174
L_00026a9a:
    bt L_00026aaa
    .org 0x26a9c - 0x12174
L_00026a9c:
    shll r5
    .org 0x26a9e - 0x12174
L_00026a9e:
    add r5,r4
    .org 0x26aa0 - 0x12174
L_00026aa0:
    mov.w @r4,r1
    .org 0x26aa2 - 0x12174
L_00026aa2:
    mov.w @(0x2,r4),r0
    .org 0x26aa4 - 0x12174
L_00026aa4:
    extu.w r0,r2
    .org 0x26aa6 - 0x12174
L_00026aa6:
    bra L_00026ab4
    .org 0x26aa8 - 0x12174
L_00026aa8:
    extu.w r1,r0
    .org 0x26aaa - 0x12174
L_00026aaa:
    add r5,r4
    .org 0x26aac - 0x12174
L_00026aac:
    mov.b @r4,r1
    .org 0x26aae - 0x12174
L_00026aae:
    mov.b @(0x1,r4),r0
    .org 0x26ab0 - 0x12174
L_00026ab0:
    extu.b r0,r2
    .org 0x26ab2 - 0x12174
L_00026ab2:
    extu.b r1,r0
    .org 0x26ab4 - 0x12174
L_00026ab4:
    mov.l L_00026abc,r6
    .org 0x26ab6 - 0x12174
L_00026ab6:
    jmp @r6
    .org 0x26ab8 - 0x12174
L_00026ab8:
    nop
    .org 0x26abc - 0x12174
L_00026abc:
    .long 0x00026740
    .org 0x528be - 0x12174
L_000528be:
    sts.l pr,@-r15
    .org 0x528c0 - 0x12174
L_000528c0:
    mov.l L_00052980,r6
    .org 0x528c2 - 0x12174
L_000528c2:
    mov.b @r6,r2
    .org 0x528c4 - 0x12174
L_000528c4:
    mov #-0x80,r6
    .org 0x528c6 - 0x12174
L_000528c6:
    extu.b r6,r6
    .org 0x528c8 - 0x12174
L_000528c8:
    extu.b r2,r2
    .org 0x528ca - 0x12174
L_000528ca:
    cmp/ge r6,r2
    .org 0x528cc - 0x12174
L_000528cc:
    bf L_000528d2
    .org 0x528ce - 0x12174
L_000528ce:
    bra L_000528d6
    .org 0x528d0 - 0x12174
L_000528d0:
    mov #-0x1,r5
    .org 0x528d2 - 0x12174
L_000528d2:
    shll r2
    .org 0x528d4 - 0x12174
L_000528d4:
    mov r2,r5
    .org 0x528d6 - 0x12174
L_000528d6:
    mov.l L_00052984,r4
    .org 0x528d8 - 0x12174
L_000528d8:
    mov.l L_00052988,r2
    .org 0x528da - 0x12174
L_000528da:
    jsr @r2
    .org 0x528dc - 0x12174
L_000528dc:
    extu.b r5,r5
    .org 0x528de - 0x12174
L_000528de:
    extu.b r0,r6
    .org 0x528e0 - 0x12174
L_000528e0:
    mov.l L_00052964,r5
    .org 0x528e2 - 0x12174
L_000528e2:
    mov.w L_000528fc,r0
    .org 0x528e4 - 0x12174
L_000528e4:
    shar r6
    .org 0x528e6 - 0x12174
L_000528e6:
    mov.w @(r0,r5),r2
    .org 0x528e8 - 0x12174
L_000528e8:
    cmp/pz r2
    .org 0x528ea - 0x12174
L_000528ea:
    bf L_000528ee
    .org 0x528ec - 0x12174
L_000528ec:
    mov #0x40,r6
    .org 0x528ee - 0x12174
L_000528ee:
    mov.w L_00052900,r0
    .org 0x528f0 - 0x12174
L_000528f0:
    lds.l @r15+,pr
    .org 0x528f2 - 0x12174
L_000528f2:
    rts
    .org 0x528f4 - 0x12174
L_000528f4:
    mov.b r6,@(r0,r5)
    .org 0x528fc - 0x12174
L_000528fc:
    .word 0x07da
    .org 0x52900 - 0x12174
L_00052900:
    .word 0x027e
    .org 0x52964 - 0x12174
L_00052964:
    .long 0xffff128c
    .org 0x52980 - 0x12174
L_00052980:
    .long 0xffff102c
    .org 0x52984 - 0x12174
L_00052984:
    .long 0x00012176
    .org 0x52988 - 0x12174
L_00052988:
    .long 0x00026370
