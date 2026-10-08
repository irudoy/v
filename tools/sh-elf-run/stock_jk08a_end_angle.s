! Complete stock angle calculation with actual interpolation, predicate and division callees.
    .text
    .balign 4
    .org 0x86f9 - 0x86f8
L_000086f9:
    .byte 0xdc
    .org 0x870b - 0x86f8
L_0000870b:
    .byte 0x46
    .org 0x8729 - 0x86f8
L_00008729:
    .byte 0x9e
    .org 0x876e - 0x86f8
L_0000876e:
    .byte 0x00
    .org 0x876f - 0x86f8
L_0000876f:
    .byte 0x1e
    .org 0x8770 - 0x86f8
L_00008770:
    .byte 0x78
    .org 0x88bb - 0x86f8
L_000088bb:
    .byte 0x50
    .org 0x8b34 - 0x86f8
L_00008b34:
    .byte 0x81
    .org 0x8b42 - 0x86f8
L_00008b42:
    .byte 0xe0
    .org 0x8bdb - 0x86f8
L_00008bdb:
    .byte 0x00
    .org 0x8cec - 0x86f8
L_00008cec:
    .byte 0x37
    .org 0x8d2c - 0x86f8
L_00008d2c:
    .byte 0x06
    .org 0x8e03 - 0x86f8
L_00008e03:
    .byte 0x6a
    .org 0x8e06 - 0x86f8
L_00008e06:
    .byte 0x46
    .org 0x9036 - 0x86f8
L_00009036:
    .byte 0xff,0xfe
    .org 0x9038 - 0x86f8
L_00009038:
    .byte 0xff,0xfe
    .org 0x90fa - 0x86f8
L_000090fa:
    .byte 0x01,0x18
    .org 0x9504 - 0x86f8
L_00009504:
    .byte 0xff,0xff
    .org 0x11bb3 - 0x86f8
L_00011bb3:
    .byte 0x14,0x1e,0x28,0x32,0x3c,0x46,0x50,0x5a
    .org 0x12136 - 0x86f8
L_00012136:
    .byte 0x14,0x14,0x14,0x14,0x14,0x0a,0x00,0x00
    .org 0x12302 - 0x86f8
L_00012302:
    .byte 0x85,0x85,0x85,0x85,0x85,0x85,0x85,0x85
    .org 0x1230a - 0x86f8
L_0001230a:
    .byte 0xa0,0xa0,0xa0,0xa5,0xaa,0xb9,0xc8,0xc8
    .org 0x12c12 - 0x86f8
L_00012c12:
    .byte 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x15
    .org 0x21ce0 - 0x86f8
L_00021ce0:
    mov.l r2,@-r15
    .org 0x21ce2 - 0x86f8
L_00021ce2:
    tst r0,r0
    .org 0x21ce4 - 0x86f8
L_00021ce4:
    bt L_00021d6a
    .org 0x21ce6 - 0x86f8
L_00021ce6:
    extu.w r0,r2
    .org 0x21ce8 - 0x86f8
L_00021ce8:
    cmp/eq r2,r0
    .org 0x21cea - 0x86f8
L_00021cea:
    bf L_00021d76
    .org 0x21cec - 0x86f8
L_00021cec:
    div0u
    .org 0x21cee - 0x86f8
L_00021cee:
    shll8 r0
    .org 0x21cf0 - 0x86f8
L_00021cf0:
    cmp/hi r1,r0
    .org 0x21cf2 - 0x86f8
L_00021cf2:
    bf L_00021d0c
    .org 0x21cf4 - 0x86f8
L_00021cf4:
    div1 r0,r1
    .org 0x21cf6 - 0x86f8
L_00021cf6:
    div1 r0,r1
    .org 0x21cf8 - 0x86f8
L_00021cf8:
    div1 r0,r1
    .org 0x21cfa - 0x86f8
L_00021cfa:
    div1 r0,r1
    .org 0x21cfc - 0x86f8
L_00021cfc:
    div1 r0,r1
    .org 0x21cfe - 0x86f8
L_00021cfe:
    div1 r0,r1
    .org 0x21d00 - 0x86f8
L_00021d00:
    div1 r0,r1
    .org 0x21d02 - 0x86f8
L_00021d02:
    div1 r0,r1
    .org 0x21d04 - 0x86f8
L_00021d04:
    rotcl r1
    .org 0x21d06 - 0x86f8
L_00021d06:
    mov.l @r15+,r2
    .org 0x21d08 - 0x86f8
L_00021d08:
    rts
    .org 0x21d0a - 0x86f8
L_00021d0a:
    extu.b r1,r0
    .org 0x21d0c - 0x86f8
L_00021d0c:
    mov.l r3,@-r15
    .org 0x21d0e - 0x86f8
L_00021d0e:
    extu.w r1,r3
    .org 0x21d10 - 0x86f8
L_00021d10:
    shll8 r0
    .org 0x21d12 - 0x86f8
L_00021d12:
    shlr16 r1
    .org 0x21d14 - 0x86f8
L_00021d14:
    div1 r0,r1
    .org 0x21d16 - 0x86f8
L_00021d16:
    div1 r0,r1
    .org 0x21d18 - 0x86f8
L_00021d18:
    div1 r0,r1
    .org 0x21d1a - 0x86f8
L_00021d1a:
    div1 r0,r1
    .org 0x21d1c - 0x86f8
L_00021d1c:
    div1 r0,r1
    .org 0x21d1e - 0x86f8
L_00021d1e:
    div1 r0,r1
    .org 0x21d20 - 0x86f8
L_00021d20:
    div1 r0,r1
    .org 0x21d22 - 0x86f8
L_00021d22:
    div1 r0,r1
    .org 0x21d24 - 0x86f8
L_00021d24:
    div1 r0,r1
    .org 0x21d26 - 0x86f8
L_00021d26:
    div1 r0,r1
    .org 0x21d28 - 0x86f8
L_00021d28:
    div1 r0,r1
    .org 0x21d2a - 0x86f8
L_00021d2a:
    div1 r0,r1
    .org 0x21d2c - 0x86f8
L_00021d2c:
    div1 r0,r1
    .org 0x21d2e - 0x86f8
L_00021d2e:
    div1 r0,r1
    .org 0x21d30 - 0x86f8
L_00021d30:
    div1 r0,r1
    .org 0x21d32 - 0x86f8
L_00021d32:
    div1 r0,r1
    .org 0x21d34 - 0x86f8
L_00021d34:
    extu.w r1,r2
    .org 0x21d36 - 0x86f8
L_00021d36:
    xor r2,r1
    .org 0x21d38 - 0x86f8
L_00021d38:
    addc r2,r2
    .org 0x21d3a - 0x86f8
L_00021d3a:
    shll16 r2
    .org 0x21d3c - 0x86f8
L_00021d3c:
    add r3,r1
    .org 0x21d3e - 0x86f8
L_00021d3e:
    div1 r0,r1
    .org 0x21d40 - 0x86f8
L_00021d40:
    div1 r0,r1
    .org 0x21d42 - 0x86f8
L_00021d42:
    div1 r0,r1
    .org 0x21d44 - 0x86f8
L_00021d44:
    div1 r0,r1
    .org 0x21d46 - 0x86f8
L_00021d46:
    div1 r0,r1
    .org 0x21d48 - 0x86f8
L_00021d48:
    div1 r0,r1
    .org 0x21d4a - 0x86f8
L_00021d4a:
    div1 r0,r1
    .org 0x21d4c - 0x86f8
L_00021d4c:
    div1 r0,r1
    .org 0x21d4e - 0x86f8
L_00021d4e:
    div1 r0,r1
    .org 0x21d50 - 0x86f8
L_00021d50:
    div1 r0,r1
    .org 0x21d52 - 0x86f8
L_00021d52:
    div1 r0,r1
    .org 0x21d54 - 0x86f8
L_00021d54:
    div1 r0,r1
    .org 0x21d56 - 0x86f8
L_00021d56:
    div1 r0,r1
    .org 0x21d58 - 0x86f8
L_00021d58:
    div1 r0,r1
    .org 0x21d5a - 0x86f8
L_00021d5a:
    div1 r0,r1
    .org 0x21d5c - 0x86f8
L_00021d5c:
    div1 r0,r1
    .org 0x21d5e - 0x86f8
L_00021d5e:
    rotcl r1
    .org 0x21d60 - 0x86f8
L_00021d60:
    extu.w r1,r0
    .org 0x21d62 - 0x86f8
L_00021d62:
    add r2,r0
    .org 0x21d64 - 0x86f8
L_00021d64:
    mov.l @r15+,r3
    .org 0x21d66 - 0x86f8
L_00021d66:
    rts
    .org 0x21d68 - 0x86f8
L_00021d68:
    mov.l @r15+,r2
    .org 0x21d6a - 0x86f8
L_00021d6a:
    mov.l L_00021dc8,r1
    .org 0x21d6c - 0x86f8
L_00021d6c:
    mov.l L_00021dcc,r2
    .org 0x21d6e - 0x86f8
L_00021d6e:
    mov.l r2,@r1
    .org 0x21d70 - 0x86f8
L_00021d70:
    mov #0x0,r0
    .org 0x21d72 - 0x86f8
L_00021d72:
    rts
    .org 0x21d74 - 0x86f8
L_00021d74:
    mov.l @r15+,r2
    .org 0x21d76 - 0x86f8
L_00021d76:
    div0u
    .org 0x21d78 - 0x86f8
L_00021d78:
    extu.w r1,r2
    .org 0x21d7a - 0x86f8
L_00021d7a:
    shll16 r2
    .org 0x21d7c - 0x86f8
L_00021d7c:
    shlr16 r1
    .org 0x21d7e - 0x86f8
L_00021d7e:
    rotcl r2
    .org 0x21d80 - 0x86f8
L_00021d80:
    div1 r0,r1
    .org 0x21d82 - 0x86f8
L_00021d82:
    rotcl r2
    .org 0x21d84 - 0x86f8
L_00021d84:
    div1 r0,r1
    .org 0x21d86 - 0x86f8
L_00021d86:
    rotcl r2
    .org 0x21d88 - 0x86f8
L_00021d88:
    div1 r0,r1
    .org 0x21d8a - 0x86f8
L_00021d8a:
    rotcl r2
    .org 0x21d8c - 0x86f8
L_00021d8c:
    div1 r0,r1
    .org 0x21d8e - 0x86f8
L_00021d8e:
    rotcl r2
    .org 0x21d90 - 0x86f8
L_00021d90:
    div1 r0,r1
    .org 0x21d92 - 0x86f8
L_00021d92:
    rotcl r2
    .org 0x21d94 - 0x86f8
L_00021d94:
    div1 r0,r1
    .org 0x21d96 - 0x86f8
L_00021d96:
    rotcl r2
    .org 0x21d98 - 0x86f8
L_00021d98:
    div1 r0,r1
    .org 0x21d9a - 0x86f8
L_00021d9a:
    rotcl r2
    .org 0x21d9c - 0x86f8
L_00021d9c:
    div1 r0,r1
    .org 0x21d9e - 0x86f8
L_00021d9e:
    rotcl r2
    .org 0x21da0 - 0x86f8
L_00021da0:
    div1 r0,r1
    .org 0x21da2 - 0x86f8
L_00021da2:
    rotcl r2
    .org 0x21da4 - 0x86f8
L_00021da4:
    div1 r0,r1
    .org 0x21da6 - 0x86f8
L_00021da6:
    rotcl r2
    .org 0x21da8 - 0x86f8
L_00021da8:
    div1 r0,r1
    .org 0x21daa - 0x86f8
L_00021daa:
    rotcl r2
    .org 0x21dac - 0x86f8
L_00021dac:
    div1 r0,r1
    .org 0x21dae - 0x86f8
L_00021dae:
    rotcl r2
    .org 0x21db0 - 0x86f8
L_00021db0:
    div1 r0,r1
    .org 0x21db2 - 0x86f8
L_00021db2:
    rotcl r2
    .org 0x21db4 - 0x86f8
L_00021db4:
    div1 r0,r1
    .org 0x21db6 - 0x86f8
L_00021db6:
    rotcl r2
    .org 0x21db8 - 0x86f8
L_00021db8:
    div1 r0,r1
    .org 0x21dba - 0x86f8
L_00021dba:
    rotcl r2
    .org 0x21dbc - 0x86f8
L_00021dbc:
    div1 r0,r1
    .org 0x21dbe - 0x86f8
L_00021dbe:
    rotcl r2
    .org 0x21dc0 - 0x86f8
L_00021dc0:
    mov r2,r0
    .org 0x21dc2 - 0x86f8
L_00021dc2:
    rts
    .org 0x21dc4 - 0x86f8
L_00021dc4:
    mov.l @r15+,r2
    .org 0x21dc8 - 0x86f8
L_00021dc8:
    .long 0xffff9818
    .org 0x21dcc - 0x86f8
L_00021dcc:
    .long 0x0000044e
    .org 0x259e4 - 0x86f8
L_000259e4:
    mov.l L_00025b98,r1
    .org 0x259e6 - 0x86f8
L_000259e6:
    exts.w r4,r0
    .org 0x259e8 - 0x86f8
L_000259e8:
    cmp/eq #-0x1,r0
    .org 0x259ea - 0x86f8
L_000259ea:
    bt L_00025a0c
    .org 0x259ec - 0x86f8
L_000259ec:
    mov r0,r7
    .org 0x259ee - 0x86f8
L_000259ee:
    shll r7
    .org 0x259f0 - 0x86f8
L_000259f0:
    mov r1,r2
    .org 0x259f2 - 0x86f8
L_000259f2:
    add r0,r7
    .org 0x259f4 - 0x86f8
L_000259f4:
    add r7,r2
    .org 0x259f6 - 0x86f8
L_000259f6:
    mov.b @(0x2,r2),r0
    .org 0x259f8 - 0x86f8
L_000259f8:
    tst #0x40,r0
    .org 0x259fa - 0x86f8
L_000259fa:
    bf/s L_00025a0e
    .org 0x259fc - 0x86f8
L_000259fc:
    mov #0x1,r5
    .org 0x259fe - 0x86f8
L_000259fe:
    mov r1,r2
    .org 0x25a00 - 0x86f8
L_00025a00:
    add r7,r2
    .org 0x25a02 - 0x86f8
L_00025a02:
    mov.b @(0x2,r2),r0
    .org 0x25a04 - 0x86f8
L_00025a04:
    tst #0x20,r0
    .org 0x25a06 - 0x86f8
L_00025a06:
    bf L_00025a0e
    .org 0x25a08 - 0x86f8
L_00025a08:
    bra L_00025a0e
    .org 0x25a0a - 0x86f8
L_00025a0a:
    mov #0x0,r5
    .org 0x25a0c - 0x86f8
L_00025a0c:
    mov #0x0,r5
    .org 0x25a0e - 0x86f8
L_00025a0e:
    rts
    .org 0x25a10 - 0x86f8
L_00025a10:
    mov r5,r0
    .org 0x25b98 - 0x86f8
L_00025b98:
    .long 0xffff5718
    .org 0x26370 - 0x86f8
L_00026370:
    mov.w L_00026382,r0
    .org 0x26372 - 0x86f8
L_00026372:
    extu.b r5,r5
    .org 0x26374 - 0x86f8
L_00026374:
    cmp/hs r0,r5
    .org 0x26376 - 0x86f8
L_00026376:
    bt L_0002637e
    .org 0x26378 - 0x86f8
L_00026378:
    mov.l L_00026384,r6
    .org 0x2637a - 0x86f8
L_0002637a:
    jmp @r6
    .org 0x2637c - 0x86f8
L_0002637c:
    mov #0x0,r3
    .org 0x2637e - 0x86f8
L_0002637e:
    rts
    .org 0x26380 - 0x86f8
L_00026380:
    mov.b @(0x7,r4),r0
    .org 0x26382 - 0x86f8
L_00026382:
    .word 0x00e0
    .org 0x26384 - 0x86f8
L_00026384:
    .long 0x00026a80
    .org 0x26474 - 0x86f8
L_00026474:
    sts.l pr,@-r15
    .org 0x26476 - 0x86f8
L_00026476:
    mov.l r4,@-r15
    .org 0x26478 - 0x86f8
L_00026478:
    mov r5,r0
    .org 0x2647a - 0x86f8
L_0002647a:
    extu.b r6,r5
    .org 0x2647c - 0x86f8
L_0002647c:
    mov.l L_0002649c,r7
    .org 0x2647e - 0x86f8
L_0002647e:
    jsr @r7
    .org 0x26480 - 0x86f8
L_00026480:
    mov #0x7,r4
    .org 0x26482 - 0x86f8
L_00026482:
    mov.l @r15+,r6
    .org 0x26484 - 0x86f8
L_00026484:
    add r4,r6
    .org 0x26486 - 0x86f8
L_00026486:
    mov.b @(0x1,r6),r0
    .org 0x26488 - 0x86f8
L_00026488:
    extu.b r0,r2
    .org 0x2648a - 0x86f8
L_0002648a:
    mov r5,r3
    .org 0x2648c - 0x86f8
L_0002648c:
    mov.b @r6,r1
    .org 0x2648e - 0x86f8
L_0002648e:
    lds.l @r15+,pr
    .org 0x26490 - 0x86f8
L_00026490:
    mov.l L_00026498,r6
    .org 0x26492 - 0x86f8
L_00026492:
    jmp @r6
    .org 0x26494 - 0x86f8
L_00026494:
    extu.b r1,r0
    .org 0x26498 - 0x86f8
L_00026498:
    .long 0x00026740
    .org 0x2649c - 0x86f8
L_0002649c:
    .long 0x00026944
    .org 0x26740 - 0x86f8
L_00026740:
    cmp/hs r0,r2
    .org 0x26742 - 0x86f8
L_00026742:
    bt L_0002675c
    .org 0x26744 - 0x86f8
L_00026744:
    mov.l r0,@-r15
    .org 0x26746 - 0x86f8
L_00026746:
    sub r2,r0
    .org 0x26748 - 0x86f8
L_00026748:
    sts macl,r1
    .org 0x2674a - 0x86f8
L_0002674a:
    mul.l r3,r0
    .org 0x2674c - 0x86f8
L_0002674c:
    sts macl,r0
    .org 0x2674e - 0x86f8
L_0002674e:
    lds r1,macl
    .org 0x26750 - 0x86f8
L_00026750:
    swap.w r0,r0
    .org 0x26752 - 0x86f8
L_00026752:
    mov.l @r15+,r2
    .org 0x26754 - 0x86f8
L_00026754:
    extu.w r0,r0
    .org 0x26756 - 0x86f8
L_00026756:
    sub r0,r2
    .org 0x26758 - 0x86f8
L_00026758:
    rts
    .org 0x2675a - 0x86f8
L_0002675a:
    mov r2,r0
    .org 0x2675c - 0x86f8
L_0002675c:
    sub r0,r2
    .org 0x2675e - 0x86f8
L_0002675e:
    sts macl,r1
    .org 0x26760 - 0x86f8
L_00026760:
    mul.l r3,r2
    .org 0x26762 - 0x86f8
L_00026762:
    sts macl,r2
    .org 0x26764 - 0x86f8
L_00026764:
    lds r1,macl
    .org 0x26766 - 0x86f8
L_00026766:
    swap.w r2,r2
    .org 0x26768 - 0x86f8
L_00026768:
    extu.w r2,r2
    .org 0x2676a - 0x86f8
L_0002676a:
    rts
    .org 0x2676c - 0x86f8
L_0002676c:
    add r2,r0
    .org 0x26944 - 0x86f8
L_00026944:
    mov r4,r3
    .org 0x26946 - 0x86f8
L_00026946:
    mov.b @(r0,r4),r1
    .org 0x26948 - 0x86f8
L_00026948:
    extu.b r1,r1
    .org 0x2694a - 0x86f8
L_0002694a:
    cmp/eq r1,r5
    .org 0x2694c - 0x86f8
L_0002694c:
    bt L_0002697c
    .org 0x2694e - 0x86f8
L_0002694e:
    cmp/hi r1,r5
    .org 0x26950 - 0x86f8
L_00026950:
    bf L_00026974
    .org 0x26952 - 0x86f8
L_00026952:
    cmp/eq r4,r3
    .org 0x26954 - 0x86f8
L_00026954:
    bt L_0002697c
    .org 0x26956 - 0x86f8
L_00026956:
    sub r1,r5
    .org 0x26958 - 0x86f8
L_00026958:
    shll16 r5
    .org 0x2695a - 0x86f8
L_0002695a:
    add r4,r0
    .org 0x2695c - 0x86f8
L_0002695c:
    mov.b @r0,r1
    .org 0x2695e - 0x86f8
L_0002695e:
    mov.b @(0x1,r0),r0
    .org 0x26960 - 0x86f8
L_00026960:
    extu.b r1,r1
    .org 0x26962 - 0x86f8
L_00026962:
    extu.b r0,r0
    .org 0x26964 - 0x86f8
L_00026964:
    sts.l pr,@-r15
    .org 0x26966 - 0x86f8
L_00026966:
    mov.l L_00026980,r2
    .org 0x26968 - 0x86f8
L_00026968:
    sub r1,r0
    .org 0x2696a - 0x86f8
L_0002696a:
    jsr @r2
    .org 0x2696c - 0x86f8
L_0002696c:
    mov r5,r1
    .org 0x2696e - 0x86f8
L_0002696e:
    lds.l @r15+,pr
    .org 0x26970 - 0x86f8
L_00026970:
    rts
    .org 0x26972 - 0x86f8
L_00026972:
    mov r0,r5
    .org 0x26974 - 0x86f8
L_00026974:
    add #-0x1,r4
    .org 0x26976 - 0x86f8
L_00026976:
    cmp/pz r4
    .org 0x26978 - 0x86f8
L_00026978:
    bt L_00026946
    .org 0x2697a - 0x86f8
L_0002697a:
    mov #0x0,r4
    .org 0x2697c - 0x86f8
L_0002697c:
    rts
    .org 0x2697e - 0x86f8
L_0002697e:
    mov #0x0,r5
    .org 0x26980 - 0x86f8
L_00026980:
    .long 0x00026c78
    .org 0x26a80 - 0x86f8
L_00026a80:
    shlr r5
    .org 0x26a82 - 0x86f8
L_00026a82:
    rotcr r3
    .org 0x26a84 - 0x86f8
L_00026a84:
    shlr r5
    .org 0x26a86 - 0x86f8
L_00026a86:
    rotcr r3
    .org 0x26a88 - 0x86f8
L_00026a88:
    shlr r5
    .org 0x26a8a - 0x86f8
L_00026a8a:
    rotcr r3
    .org 0x26a8c - 0x86f8
L_00026a8c:
    shlr r5
    .org 0x26a8e - 0x86f8
L_00026a8e:
    rotcr r3
    .org 0x26a90 - 0x86f8
L_00026a90:
    shlr r5
    .org 0x26a92 - 0x86f8
L_00026a92:
    rotcr r3
    .org 0x26a94 - 0x86f8
L_00026a94:
    swap.w r3,r3
    .org 0x26a96 - 0x86f8
L_00026a96:
    shlr8 r0
    .org 0x26a98 - 0x86f8
L_00026a98:
    tst r0,r0
    .org 0x26a9a - 0x86f8
L_00026a9a:
    bt L_00026aaa
    .org 0x26a9c - 0x86f8
L_00026a9c:
    shll r5
    .org 0x26a9e - 0x86f8
L_00026a9e:
    add r5,r4
    .org 0x26aa0 - 0x86f8
L_00026aa0:
    mov.w @r4,r1
    .org 0x26aa2 - 0x86f8
L_00026aa2:
    mov.w @(0x2,r4),r0
    .org 0x26aa4 - 0x86f8
L_00026aa4:
    extu.w r0,r2
    .org 0x26aa6 - 0x86f8
L_00026aa6:
    bra L_00026ab4
    .org 0x26aa8 - 0x86f8
L_00026aa8:
    extu.w r1,r0
    .org 0x26aaa - 0x86f8
L_00026aaa:
    add r5,r4
    .org 0x26aac - 0x86f8
L_00026aac:
    mov.b @r4,r1
    .org 0x26aae - 0x86f8
L_00026aae:
    mov.b @(0x1,r4),r0
    .org 0x26ab0 - 0x86f8
L_00026ab0:
    extu.b r0,r2
    .org 0x26ab2 - 0x86f8
L_00026ab2:
    extu.b r1,r0
    .org 0x26ab4 - 0x86f8
L_00026ab4:
    mov.l L_00026abc,r6
    .org 0x26ab6 - 0x86f8
L_00026ab6:
    jmp @r6
    .org 0x26ab8 - 0x86f8
L_00026ab8:
    nop
    .org 0x26abc - 0x86f8
L_00026abc:
    .long 0x00026740
    .org 0x26c78 - 0x86f8
L_00026c78:
    tst r0,r0
    .org 0x26c7a - 0x86f8
L_00026c7a:
    bt L_00026d0a
    .org 0x26c7c - 0x86f8
L_00026c7c:
    mov.l r2,@-r15
    .org 0x26c7e - 0x86f8
L_00026c7e:
    mov #0x0,r2
    .org 0x26c80 - 0x86f8
L_00026c80:
    div0u
    .org 0x26c82 - 0x86f8
L_00026c82:
    rotcl r1
    .org 0x26c84 - 0x86f8
L_00026c84:
    div1 r0,r2
    .org 0x26c86 - 0x86f8
L_00026c86:
    rotcl r1
    .org 0x26c88 - 0x86f8
L_00026c88:
    div1 r0,r2
    .org 0x26c8a - 0x86f8
L_00026c8a:
    rotcl r1
    .org 0x26c8c - 0x86f8
L_00026c8c:
    div1 r0,r2
    .org 0x26c8e - 0x86f8
L_00026c8e:
    rotcl r1
    .org 0x26c90 - 0x86f8
L_00026c90:
    div1 r0,r2
    .org 0x26c92 - 0x86f8
L_00026c92:
    rotcl r1
    .org 0x26c94 - 0x86f8
L_00026c94:
    div1 r0,r2
    .org 0x26c96 - 0x86f8
L_00026c96:
    rotcl r1
    .org 0x26c98 - 0x86f8
L_00026c98:
    div1 r0,r2
    .org 0x26c9a - 0x86f8
L_00026c9a:
    rotcl r1
    .org 0x26c9c - 0x86f8
L_00026c9c:
    div1 r0,r2
    .org 0x26c9e - 0x86f8
L_00026c9e:
    rotcl r1
    .org 0x26ca0 - 0x86f8
L_00026ca0:
    div1 r0,r2
    .org 0x26ca2 - 0x86f8
L_00026ca2:
    rotcl r1
    .org 0x26ca4 - 0x86f8
L_00026ca4:
    div1 r0,r2
    .org 0x26ca6 - 0x86f8
L_00026ca6:
    rotcl r1
    .org 0x26ca8 - 0x86f8
L_00026ca8:
    div1 r0,r2
    .org 0x26caa - 0x86f8
L_00026caa:
    rotcl r1
    .org 0x26cac - 0x86f8
L_00026cac:
    div1 r0,r2
    .org 0x26cae - 0x86f8
L_00026cae:
    rotcl r1
    .org 0x26cb0 - 0x86f8
L_00026cb0:
    div1 r0,r2
    .org 0x26cb2 - 0x86f8
L_00026cb2:
    rotcl r1
    .org 0x26cb4 - 0x86f8
L_00026cb4:
    div1 r0,r2
    .org 0x26cb6 - 0x86f8
L_00026cb6:
    rotcl r1
    .org 0x26cb8 - 0x86f8
L_00026cb8:
    div1 r0,r2
    .org 0x26cba - 0x86f8
L_00026cba:
    rotcl r1
    .org 0x26cbc - 0x86f8
L_00026cbc:
    div1 r0,r2
    .org 0x26cbe - 0x86f8
L_00026cbe:
    rotcl r1
    .org 0x26cc0 - 0x86f8
L_00026cc0:
    div1 r0,r2
    .org 0x26cc2 - 0x86f8
L_00026cc2:
    rotcl r1
    .org 0x26cc4 - 0x86f8
L_00026cc4:
    div1 r0,r2
    .org 0x26cc6 - 0x86f8
L_00026cc6:
    rotcl r1
    .org 0x26cc8 - 0x86f8
L_00026cc8:
    div1 r0,r2
    .org 0x26cca - 0x86f8
L_00026cca:
    rotcl r1
    .org 0x26ccc - 0x86f8
L_00026ccc:
    div1 r0,r2
    .org 0x26cce - 0x86f8
L_00026cce:
    rotcl r1
    .org 0x26cd0 - 0x86f8
L_00026cd0:
    div1 r0,r2
    .org 0x26cd2 - 0x86f8
L_00026cd2:
    rotcl r1
    .org 0x26cd4 - 0x86f8
L_00026cd4:
    div1 r0,r2
    .org 0x26cd6 - 0x86f8
L_00026cd6:
    rotcl r1
    .org 0x26cd8 - 0x86f8
L_00026cd8:
    div1 r0,r2
    .org 0x26cda - 0x86f8
L_00026cda:
    rotcl r1
    .org 0x26cdc - 0x86f8
L_00026cdc:
    div1 r0,r2
    .org 0x26cde - 0x86f8
L_00026cde:
    rotcl r1
    .org 0x26ce0 - 0x86f8
L_00026ce0:
    div1 r0,r2
    .org 0x26ce2 - 0x86f8
L_00026ce2:
    rotcl r1
    .org 0x26ce4 - 0x86f8
L_00026ce4:
    div1 r0,r2
    .org 0x26ce6 - 0x86f8
L_00026ce6:
    rotcl r1
    .org 0x26ce8 - 0x86f8
L_00026ce8:
    div1 r0,r2
    .org 0x26cea - 0x86f8
L_00026cea:
    rotcl r1
    .org 0x26cec - 0x86f8
L_00026cec:
    div1 r0,r2
    .org 0x26cee - 0x86f8
L_00026cee:
    rotcl r1
    .org 0x26cf0 - 0x86f8
L_00026cf0:
    div1 r0,r2
    .org 0x26cf2 - 0x86f8
L_00026cf2:
    rotcl r1
    .org 0x26cf4 - 0x86f8
L_00026cf4:
    div1 r0,r2
    .org 0x26cf6 - 0x86f8
L_00026cf6:
    rotcl r1
    .org 0x26cf8 - 0x86f8
L_00026cf8:
    div1 r0,r2
    .org 0x26cfa - 0x86f8
L_00026cfa:
    rotcl r1
    .org 0x26cfc - 0x86f8
L_00026cfc:
    div1 r0,r2
    .org 0x26cfe - 0x86f8
L_00026cfe:
    rotcl r1
    .org 0x26d00 - 0x86f8
L_00026d00:
    div1 r0,r2
    .org 0x26d02 - 0x86f8
L_00026d02:
    rotcl r1
    .org 0x26d04 - 0x86f8
L_00026d04:
    mov.l @r15+,r2
    .org 0x26d06 - 0x86f8
L_00026d06:
    rts
    .org 0x26d08 - 0x86f8
L_00026d08:
    mov r1,r0
    .org 0x26d0a - 0x86f8
L_00026d0a:
    rts
    .org 0x26d0c - 0x86f8
L_00026d0c:
    mov #0x0,r0
    .org 0x56bd0 - 0x86f8
L_00056bd0:
    mov.l r11,@-r15
    .org 0x56bd2 - 0x86f8
L_00056bd2:
    mov.l r12,@-r15
    .org 0x56bd4 - 0x86f8
L_00056bd4:
    mov.l r13,@-r15
    .org 0x56bd6 - 0x86f8
L_00056bd6:
    mov.l r14,@-r15
    .org 0x56bd8 - 0x86f8
L_00056bd8:
    sts.l pr,@-r15
    .org 0x56bda - 0x86f8
L_00056bda:
    sts.l macl,@-r15
    .org 0x56bdc - 0x86f8
L_00056bdc:
    stc.l gbr,@-r15
    .org 0x56bde - 0x86f8
L_00056bde:
    mov.l L_00056dc0,r0
    .org 0x56be0 - 0x86f8
L_00056be0:
    ldc r0,gbr
    .org 0x56be2 - 0x86f8
L_00056be2:
    add #-0xc,r15
    .org 0x56be4 - 0x86f8
L_00056be4:
    bsr L_00056ea6
    .org 0x56be6 - 0x86f8
L_00056be6:
    nop
    .org 0x56be8 - 0x86f8
L_00056be8:
    mov.l L_00056dc4,r6
    .org 0x56bea - 0x86f8
L_00056bea:
    mov.b @r6,r0
    .org 0x56bec - 0x86f8
L_00056bec:
    tst #0x1,r0
    .org 0x56bee - 0x86f8
L_00056bee:
    bf L_00056c04
    .org 0x56bf0 - 0x86f8
L_00056bf0:
    tst #0x10,r0
    .org 0x56bf2 - 0x86f8
L_00056bf2:
    bt L_00056c04
    .org 0x56bf4 - 0x86f8
L_00056bf4:
    mov.l L_00056dc8,r2
    .org 0x56bf6 - 0x86f8
L_00056bf6:
    mov.b @r2,r0
    .org 0x56bf8 - 0x86f8
L_00056bf8:
    tst #0x41,r0
    .org 0x56bfa - 0x86f8
L_00056bfa:
    bt L_00056c04
    .org 0x56bfc - 0x86f8
L_00056bfc:
    bsr L_00056e70
    .org 0x56bfe - 0x86f8
L_00056bfe:
    nop
    .org 0x56c00 - 0x86f8
L_00056c00:
    bra L_00056e5e
    .org 0x56c02 - 0x86f8
L_00056c02:
    nop
    .org 0x56c04 - 0x86f8
L_00056c04:
    mov.l L_00056dcc,r6
    .org 0x56c06 - 0x86f8
L_00056c06:
    mov.b @r6,r0
    .org 0x56c08 - 0x86f8
L_00056c08:
    tst #0x1,r0
    .org 0x56c0a - 0x86f8
L_00056c0a:
    bt L_00056c10
    .org 0x56c0c - 0x86f8
L_00056c0c:
    bra L_00056e5e
    .org 0x56c0e - 0x86f8
L_00056c0e:
    nop
    .org 0x56c10 - 0x86f8
L_00056c10:
    mov.l L_00056dd0,r11
    .org 0x56c12 - 0x86f8
L_00056c12:
    mov.l L_00056dd4,r12
    .org 0x56c14 - 0x86f8
L_00056c14:
    mov.b @(0x7,r11),r0
    .org 0x56c16 - 0x86f8
L_00056c16:
    extu.b r0,r13
    .org 0x56c18 - 0x86f8
L_00056c18:
    mov.b @(0x38,gbr),r0
    .org 0x56c1a - 0x86f8
L_00056c1a:
    mov r0,r14
    .org 0x56c1c - 0x86f8
L_00056c1c:
    mov #0x27,r0
    .org 0x56c1e - 0x86f8
L_00056c1e:
    mov.b @(r0,r12),r6
    .org 0x56c20 - 0x86f8
L_00056c20:
    mov r6,r0
    .org 0x56c22 - 0x86f8
L_00056c22:
    tst #0x2,r0
    .org 0x56c24 - 0x86f8
L_00056c24:
    bt L_00056c28
    .org 0x56c26 - 0x86f8
L_00056c26:
    add #0x5,r13
    .org 0x56c28 - 0x86f8
L_00056c28:
    mov.l L_00056dd8,r5
    .org 0x56c2a - 0x86f8
L_00056c2a:
    mov r6,r0
    .org 0x56c2c - 0x86f8
L_00056c2c:
    mov.b @r5,r2
    .org 0x56c2e - 0x86f8
L_00056c2e:
    extu.b r2,r2
    .org 0x56c30 - 0x86f8
L_00056c30:
    cmp/hs r2,r13
    .org 0x56c32 - 0x86f8
L_00056c32:
    bt/s L_00056c38
    .org 0x56c34 - 0x86f8
L_00056c34:
    or #0x2,r0
    .org 0x56c36 - 0x86f8
L_00056c36:
    and #0xfd,r0
    .org 0x56c38 - 0x86f8
L_00056c38:
    mov r0,r2
    .org 0x56c3a - 0x86f8
L_00056c3a:
    mov #0x27,r0
    .org 0x56c3c - 0x86f8
L_00056c3c:
    mov.b r2,@(r0,r12)
    .org 0x56c3e - 0x86f8
L_00056c3e:
    mov.l L_00056ddc,r2
    .org 0x56c40 - 0x86f8
L_00056c40:
    mov.b @r2,r0
    .org 0x56c42 - 0x86f8
L_00056c42:
    and #0x40,r0
    .org 0x56c44 - 0x86f8
L_00056c44:
    tst r0,r0
    .org 0x56c46 - 0x86f8
L_00056c46:
    bf/s L_00056c50
    .org 0x56c48 - 0x86f8
L_00056c48:
    mov.b r0,@r15
    .org 0x56c4a - 0x86f8
L_00056c4a:
    mov.b @(0x3,gbr),r0
    .org 0x56c4c - 0x86f8
L_00056c4c:
    tst #0x20,r0
    .org 0x56c4e - 0x86f8
L_00056c4e:
    bf L_00056c56
    .org 0x56c50 - 0x86f8
L_00056c50:
    mov.l L_00056de0,r6
    .org 0x56c52 - 0x86f8
L_00056c52:
    mov.b @r6,r0
    .org 0x56c54 - 0x86f8
L_00056c54:
    mov.b r0,@(0x93,gbr)
    .org 0x56c56 - 0x86f8
L_00056c56:
    mov.b @(0x93,gbr),r0
    .org 0x56c58 - 0x86f8
L_00056c58:
    tst r0,r0
    .org 0x56c5a - 0x86f8
L_00056c5a:
    bf L_00056c68
    .org 0x56c5c - 0x86f8
L_00056c5c:
    mov.b @r15,r6
    .org 0x56c5e - 0x86f8
L_00056c5e:
    tst r6,r6
    .org 0x56c60 - 0x86f8
L_00056c60:
    bf L_00056c68
    .org 0x56c62 - 0x86f8
L_00056c62:
    mov r14,r0
    .org 0x56c64 - 0x86f8
L_00056c64:
    bra L_00056c6c
    .org 0x56c66 - 0x86f8
L_00056c66:
    or #0x10,r0
    .org 0x56c68 - 0x86f8
L_00056c68:
    mov r14,r0
    .org 0x56c6a - 0x86f8
L_00056c6a:
    and #0xef,r0
    .org 0x56c6c - 0x86f8
L_00056c6c:
    mov.b r0,@(0x38,gbr)
    .org 0x56c6e - 0x86f8
L_00056c6e:
    mov.b @(0x1c,gbr),r0
    .org 0x56c70 - 0x86f8
L_00056c70:
    tst #0x8,r0
    .org 0x56c72 - 0x86f8
L_00056c72:
    bt L_00056c84
    .org 0x56c74 - 0x86f8
L_00056c74:
    mov.l L_00056de4,r6
    .org 0x56c76 - 0x86f8
L_00056c76:
    mov #0x29,r0
    .org 0x56c78 - 0x86f8
L_00056c78:
    mov.b @(r0,r6),r2
    .org 0x56c7a - 0x86f8
L_00056c7a:
    tst r2,r2
    .org 0x56c7c - 0x86f8
L_00056c7c:
    bf L_00056c92
    .org 0x56c7e - 0x86f8
L_00056c7e:
    mov #0x38,r0
    .org 0x56c80 - 0x86f8
L_00056c80:
    bra L_00056c92
    .org 0x56c82 - 0x86f8
L_00056c82:
    or.b #0x20,@(r0,gbr)
    .org 0x56c84 - 0x86f8
L_00056c84:
    mov.l L_00056de8,r6
    .org 0x56c86 - 0x86f8
L_00056c86:
    mov #0x29,r0
    .org 0x56c88 - 0x86f8
L_00056c88:
    mov.b @r6,r2
    .org 0x56c8a - 0x86f8
L_00056c8a:
    mov.l L_00056de4,r6
    .org 0x56c8c - 0x86f8
L_00056c8c:
    mov.b r2,@(r0,r6)
    .org 0x56c8e - 0x86f8
L_00056c8e:
    mov #0x38,r0
    .org 0x56c90 - 0x86f8
L_00056c90:
    and.b #0xdf,@(r0,gbr)
    .org 0x56c92 - 0x86f8
L_00056c92:
    mov #0x27,r0
    .org 0x56c94 - 0x86f8
L_00056c94:
    mov.b @(r0,r12),r0
    .org 0x56c96 - 0x86f8
L_00056c96:
    tst #0x2,r0
    .org 0x56c98 - 0x86f8
L_00056c98:
    bt L_00056cba
    .org 0x56c9a - 0x86f8
L_00056c9a:
    mov.b @(0x38,gbr),r0
    .org 0x56c9c - 0x86f8
L_00056c9c:
    tst #0x10,r0
    .org 0x56c9e - 0x86f8
L_00056c9e:
    bt/s L_00056cba
    .org 0x56ca0 - 0x86f8
L_00056ca0:
    mov r0,r2
    .org 0x56ca2 - 0x86f8
L_00056ca2:
    mov r2,r0
    .org 0x56ca4 - 0x86f8
L_00056ca4:
    tst #0x20,r0
    .org 0x56ca6 - 0x86f8
L_00056ca6:
    bt L_00056cba
    .org 0x56ca8 - 0x86f8
L_00056ca8:
    mov.l L_00056dec,r5
    .org 0x56caa - 0x86f8
L_00056caa:
    mov #0x17,r0
    .org 0x56cac - 0x86f8
L_00056cac:
    mov.l L_00056df0,r4
    .org 0x56cae - 0x86f8
L_00056cae:
    mov.b @(r0,r5),r6
    .org 0x56cb0 - 0x86f8
L_00056cb0:
    mov.l L_00056df4,r2
    .org 0x56cb2 - 0x86f8
L_00056cb2:
    jsr @r2
    .org 0x56cb4 - 0x86f8
L_00056cb4:
    extu.b r6,r5
    .org 0x56cb6 - 0x86f8
L_00056cb6:
    bra L_00056e46
    .org 0x56cb8 - 0x86f8
L_00056cb8:
    extu.b r0,r2
    .org 0x56cba - 0x86f8
L_00056cba:
    mov.b @(0x84,gbr),r0
    .org 0x56cbc - 0x86f8
L_00056cbc:
    tst #0x2,r0
    .org 0x56cbe - 0x86f8
L_00056cbe:
    bt/s L_00056cd0
    .org 0x56cc0 - 0x86f8
L_00056cc0:
    mov r0,r2
    .org 0x56cc2 - 0x86f8
L_00056cc2:
    mov r2,r0
    .org 0x56cc4 - 0x86f8
L_00056cc4:
    tst #0x10,r0
    .org 0x56cc6 - 0x86f8
L_00056cc6:
    bf L_00056cd0
    .org 0x56cc8 - 0x86f8
L_00056cc8:
    mov.l L_00056df8,r6
    .org 0x56cca - 0x86f8
L_00056cca:
    mov.b @r6,r2
    .org 0x56ccc - 0x86f8
L_00056ccc:
    bra L_00056e46
    .org 0x56cce - 0x86f8
L_00056cce:
    extu.b r2,r2
    .org 0x56cd0 - 0x86f8
L_00056cd0:
    mov.b @(0x4,r11),r0
    .org 0x56cd2 - 0x86f8
L_00056cd2:
    mov.l L_00056dfc,r4
    .org 0x56cd4 - 0x86f8
L_00056cd4:
    mov.l L_00056e00,r5
    .org 0x56cd6 - 0x86f8
L_00056cd6:
    mov.l L_00056e04,r2
    .org 0x56cd8 - 0x86f8
L_00056cd8:
    jsr @r2
    .org 0x56cda - 0x86f8
L_00056cda:
    extu.b r0,r6
    .org 0x56cdc - 0x86f8
L_00056cdc:
    extu.b r0,r2
    .org 0x56cde - 0x86f8
L_00056cde:
    mov.l L_00056e08,r6
    .org 0x56ce0 - 0x86f8
L_00056ce0:
    mov.w L_00056d18,r0
    .org 0x56ce2 - 0x86f8
L_00056ce2:
    mov.b r2,@(r0,r6)
    .org 0x56ce4 - 0x86f8
L_00056ce4:
    mov.l L_00056e0c,r6
    .org 0x56ce6 - 0x86f8
L_00056ce6:
    mov.b @r6,r4
    .org 0x56ce8 - 0x86f8
L_00056ce8:
    mov.b @(0x3,r6),r0
    .org 0x56cea - 0x86f8
L_00056cea:
    extu.b r4,r4
    .org 0x56cec - 0x86f8
L_00056cec:
    extu.b r0,r5
    .org 0x56cee - 0x86f8
L_00056cee:
    cmp/gt r5,r4
    .org 0x56cf0 - 0x86f8
L_00056cf0:
    bt L_00056cf4
    .org 0x56cf2 - 0x86f8
L_00056cf2:
    mov r4,r5
    .org 0x56cf4 - 0x86f8
L_00056cf4:
    mov.l L_00056e10,r3
    .org 0x56cf6 - 0x86f8
L_00056cf6:
    extu.b r5,r5
    .org 0x56cf8 - 0x86f8
L_00056cf8:
    mov.b @(0x7,r11),r0
    .org 0x56cfa - 0x86f8
L_00056cfa:
    mov.b @r3,r6
    .org 0x56cfc - 0x86f8
L_00056cfc:
    extu.b r0,r7
    .org 0x56cfe - 0x86f8
L_00056cfe:
    extu.b r6,r6
    .org 0x56d00 - 0x86f8
L_00056d00:
    sub r6,r5
    .org 0x56d02 - 0x86f8
L_00056d02:
    cmp/ge r5,r7
    .org 0x56d04 - 0x86f8
L_00056d04:
    bt L_00056d14
    .org 0x56d06 - 0x86f8
L_00056d06:
    mov.b @(0x4,r11),r0
    .org 0x56d08 - 0x86f8
L_00056d08:
    mov r7,r6
    .org 0x56d0a - 0x86f8
L_00056d0a:
    extu.b r0,r7
    .org 0x56d0c - 0x86f8
L_00056d0c:
    sub r7,r6
    .org 0x56d0e - 0x86f8
L_00056d0e:
    cmp/ge r2,r6
    .org 0x56d10 - 0x86f8
L_00056d10:
    bf/s L_00056d24
    .org 0x56d12 - 0x86f8
L_00056d12:
    mov r2,r5
    .org 0x56d14 - 0x86f8
L_00056d14:
    bra L_00056d1a
    .org 0x56d16 - 0x86f8
L_00056d16:
    mov #0x5c,r0
    .org 0x56d18 - 0x86f8
L_00056d18:
    .word 0x0b13
    .org 0x56d1a - 0x86f8
L_00056d1a:
    mov.b @(r0,r12),r0
    .org 0x56d1c - 0x86f8
L_00056d1c:
    or #0x1,r0
    .org 0x56d1e - 0x86f8
L_00056d1e:
    mov r0,r6
    .org 0x56d20 - 0x86f8
L_00056d20:
    mov #0x5c,r0
    .org 0x56d22 - 0x86f8
L_00056d22:
    mov.b r6,@(r0,r12)
    .org 0x56d24 - 0x86f8
L_00056d24:
    tst r2,r2
    .org 0x56d26 - 0x86f8
L_00056d26:
    bf L_00056d2c
    .org 0x56d28 - 0x86f8
L_00056d28:
    bra L_00056e24
    .org 0x56d2a - 0x86f8
L_00056d2a:
    nop
    .org 0x56d2c - 0x86f8
L_00056d2c:
    mov.l L_00056e14,r2
    .org 0x56d2e - 0x86f8
L_00056d2e:
    mov.w L_00056dba,r4
    .org 0x56d30 - 0x86f8
L_00056d30:
    jsr @r2
    .org 0x56d32 - 0x86f8
L_00056d32:
    nop
    .org 0x56d34 - 0x86f8
L_00056d34:
    tst r0,r0
    .org 0x56d36 - 0x86f8
L_00056d36:
    bf L_00056e24
    .org 0x56d38 - 0x86f8
L_00056d38:
    mov.l L_00056e18,r6
    .org 0x56d3a - 0x86f8
L_00056d3a:
    mov.b @r6,r2
    .org 0x56d3c - 0x86f8
L_00056d3c:
    mov #0x64,r6
    .org 0x56d3e - 0x86f8
L_00056d3e:
    shll2 r6
    .org 0x56d40 - 0x86f8
L_00056d40:
    extu.b r2,r2
    .org 0x56d42 - 0x86f8
L_00056d42:
    mul.l r2,r6
    .org 0x56d44 - 0x86f8
L_00056d44:
    mov #-0x1,r6
    .org 0x56d46 - 0x86f8
L_00056d46:
    extu.w r6,r6
    .org 0x56d48 - 0x86f8
L_00056d48:
    sts macl,r5
    .org 0x56d4a - 0x86f8
L_00056d4a:
    cmp/hi r6,r5
    .org 0x56d4c - 0x86f8
L_00056d4c:
    bf/s L_00056d54
    .org 0x56d4e - 0x86f8
L_00056d4e:
    mov.l r5,@(0x8,r15)
    .org 0x56d50 - 0x86f8
L_00056d50:
    mov r6,r5
    .org 0x56d52 - 0x86f8
L_00056d52:
    mov.l r6,@(0x8,r15)
    .org 0x56d54 - 0x86f8
L_00056d54:
    mov #0x5c,r0
    .org 0x56d56 - 0x86f8
L_00056d56:
    mov.b @(r0,r12),r0
    .org 0x56d58 - 0x86f8
L_00056d58:
    tst #0x1,r0
    .org 0x56d5a - 0x86f8
L_00056d5a:
    bt L_00056d96
    .org 0x56d5c - 0x86f8
L_00056d5c:
    mov.l L_00056e1c,r2
    .org 0x56d5e - 0x86f8
L_00056d5e:
    mov.w @r2,r6
    .org 0x56d60 - 0x86f8
L_00056d60:
    extu.w r6,r0
    .org 0x56d62 - 0x86f8
L_00056d62:
    tst r0,r0
    .org 0x56d64 - 0x86f8
L_00056d64:
    bf L_00056d70
    .org 0x56d66 - 0x86f8
L_00056d66:
    mov.l L_00056e08,r3
    .org 0x56d68 - 0x86f8
L_00056d68:
    mov.w L_00056dbc,r0
    .org 0x56d6a - 0x86f8
L_00056d6a:
    mov.w r5,@(r0,r3)
    .org 0x56d6c - 0x86f8
L_00056d6c:
    bra L_00056d9e
    .org 0x56d6e - 0x86f8
L_00056d6e:
    mov r5,r6
    .org 0x56d70 - 0x86f8
L_00056d70:
    mov.l L_00056e20,r4
    .org 0x56d72 - 0x86f8
L_00056d72:
    mov r5,r1
    .org 0x56d74 - 0x86f8
L_00056d74:
    jsr @r4
    .org 0x56d76 - 0x86f8
L_00056d76:
    mov.l r4,@(0x4,r15)
    .org 0x56d78 - 0x86f8
L_00056d78:
    mov r0,r2
    .org 0x56d7a - 0x86f8
L_00056d7a:
    mov.l L_00056e08,r1
    .org 0x56d7c - 0x86f8
L_00056d7c:
    mov.w L_00056dbc,r0
    .org 0x56d7e - 0x86f8
L_00056d7e:
    mov.l @(0x8,r15),r5
    .org 0x56d80 - 0x86f8
L_00056d80:
    mov.w @(r0,r1),r6
    .org 0x56d82 - 0x86f8
L_00056d82:
    extu.w r6,r6
    .org 0x56d84 - 0x86f8
L_00056d84:
    add r2,r6
    .org 0x56d86 - 0x86f8
L_00056d86:
    cmp/hi r5,r6
    .org 0x56d88 - 0x86f8
L_00056d88:
    bf L_00056d8c
    .org 0x56d8a - 0x86f8
L_00056d8a:
    mov r5,r6
    .org 0x56d8c - 0x86f8
L_00056d8c:
    mov.l L_00056e08,r3
    .org 0x56d8e - 0x86f8
L_00056d8e:
    mov.w L_00056dbc,r0
    .org 0x56d90 - 0x86f8
L_00056d90:
    mov.w r6,@(r0,r3)
    .org 0x56d92 - 0x86f8
L_00056d92:
    bra L_00056da2
    .org 0x56d94 - 0x86f8
L_00056d94:
    nop
    .org 0x56d96 - 0x86f8
L_00056d96:
    mov.l L_00056e08,r3
    .org 0x56d98 - 0x86f8
L_00056d98:
    mov #0x0,r6
    .org 0x56d9a - 0x86f8
L_00056d9a:
    mov.w L_00056dbc,r0
    .org 0x56d9c - 0x86f8
L_00056d9c:
    mov.w r6,@(r0,r3)
    .org 0x56d9e - 0x86f8
L_00056d9e:
    mov.l L_00056e20,r4
    .org 0x56da0 - 0x86f8
L_00056da0:
    mov.l r4,@(0x4,r15)
    .org 0x56da2 - 0x86f8
L_00056da2:
    extu.w r6,r6
    .org 0x56da4 - 0x86f8
L_00056da4:
    mov.l @(0x4,r15),r4
    .org 0x56da6 - 0x86f8
L_00056da6:
    mov #0x64,r0
    .org 0x56da8 - 0x86f8
L_00056da8:
    sub r6,r5
    .org 0x56daa - 0x86f8
L_00056daa:
    shll2 r0
    .org 0x56dac - 0x86f8
L_00056dac:
    jsr @r4
    .org 0x56dae - 0x86f8
L_00056dae:
    mov r5,r1
    .org 0x56db0 - 0x86f8
L_00056db0:
    mov r0,r2
    .org 0x56db2 - 0x86f8
L_00056db2:
    mov.l L_00056e08,r1
    .org 0x56db4 - 0x86f8
L_00056db4:
    mov.w L_00056dbe,r0
    .org 0x56db6 - 0x86f8
L_00056db6:
    bra L_00056e2c
    .org 0x56db8 - 0x86f8
L_00056db8:
    mov.b r2,@(r0,r1)
    .org 0x56dba - 0x86f8
L_00056dba:
    .word 0x012a
    .org 0x56dbc - 0x86f8
L_00056dbc:
    .word 0x0b16
    .org 0x56dbe - 0x86f8
L_00056dbe:
    .word 0x0b14
    .org 0x56dc0 - 0x86f8
L_00056dc0:
    .long 0xffff244c
    .org 0x56dc4 - 0x86f8
L_00056dc4:
    .long 0x00008b34
    .org 0x56dc8 - 0x86f8
L_00056dc8:
    .long 0x00008b42
    .org 0x56dcc - 0x86f8
L_00056dcc:
    .long 0x0000870b
    .org 0x56dd0 - 0x86f8
L_00056dd0:
    .long 0xffff106a
    .org 0x56dd4 - 0x86f8
L_00056dd4:
    .long 0xffff41a9
    .org 0x56dd8 - 0x86f8
L_00056dd8:
    .long 0x00008770
    .org 0x56ddc - 0x86f8
L_00056ddc:
    .long 0xffff4184
    .org 0x56de0 - 0x86f8
L_00056de0:
    .long 0x0000876f
    .org 0x56de4 - 0x86f8
L_00056de4:
    .long 0xffff256a
    .org 0x56de8 - 0x86f8
L_00056de8:
    .long 0x0000876e
    .org 0x56dec - 0x86f8
L_00056dec:
    .long 0xffff119c
    .org 0x56df0 - 0x86f8
L_00056df0:
    .long 0x0001230a
    .org 0x56df4 - 0x86f8
L_00056df4:
    .long 0x00026370
    .org 0x56df8 - 0x86f8
L_00056df8:
    .long 0x00008729
    .org 0x56dfc - 0x86f8
L_00056dfc:
    .long 0x00012c12
    .org 0x56e00 - 0x86f8
L_00056e00:
    .long 0x00011bb3
    .org 0x56e04 - 0x86f8
L_00056e04:
    .long 0x00026474
    .org 0x56e08 - 0x86f8
L_00056e08:
    .long 0xffff28f8
    .org 0x56e0c - 0x86f8
L_00056e0c:
    .long 0x00008e03
    .org 0x56e10 - 0x86f8
L_00056e10:
    .long 0x00008d2c
    .org 0x56e14 - 0x86f8
L_00056e14:
    .long 0x000259e4
    .org 0x56e18 - 0x86f8
L_00056e18:
    .long 0x00008bdb
    .org 0x56e1c - 0x86f8
L_00056e1c:
    .long 0x00009504
    .org 0x56e20 - 0x86f8
L_00056e20:
    .long 0x00021ce0
    .org 0x56e24 - 0x86f8
L_00056e24:
    mov.l L_00056f74,r3
    .org 0x56e26 - 0x86f8
L_00056e26:
    mov #0x0,r2
    .org 0x56e28 - 0x86f8
L_00056e28:
    mov.w L_00056f6a,r0
    .org 0x56e2a - 0x86f8
L_00056e2a:
    mov.b r2,@(r0,r3)
    .org 0x56e2c - 0x86f8
L_00056e2c:
    mov.l L_00056f78,r5
    .org 0x56e2e - 0x86f8
L_00056e2e:
    mov #0x17,r0
    .org 0x56e30 - 0x86f8
L_00056e30:
    mov.l L_00056f7c,r4
    .org 0x56e32 - 0x86f8
L_00056e32:
    mov.b @(r0,r5),r6
    .org 0x56e34 - 0x86f8
L_00056e34:
    mov.l L_00056f80,r2
    .org 0x56e36 - 0x86f8
L_00056e36:
    jsr @r2
    .org 0x56e38 - 0x86f8
L_00056e38:
    extu.b r6,r5
    .org 0x56e3a - 0x86f8
L_00056e3a:
    extu.b r0,r2
    .org 0x56e3c - 0x86f8
L_00056e3c:
    mov.l L_00056f74,r3
    .org 0x56e3e - 0x86f8
L_00056e3e:
    mov.w L_00056f6a,r0
    .org 0x56e40 - 0x86f8
L_00056e40:
    mov.b @(r0,r3),r5
    .org 0x56e42 - 0x86f8
L_00056e42:
    extu.b r5,r6
    .org 0x56e44 - 0x86f8
L_00056e44:
    add r6,r2
    .org 0x56e46 - 0x86f8
L_00056e46:
    mov #-0x2e,r5
    .org 0x56e48 - 0x86f8
L_00056e48:
    extu.w r2,r2
    .org 0x56e4a - 0x86f8
L_00056e4a:
    extu.b r5,r5
    .org 0x56e4c - 0x86f8
L_00056e4c:
    cmp/ge r5,r2
    .org 0x56e4e - 0x86f8
L_00056e4e:
    bf L_00056e54
    .org 0x56e50 - 0x86f8
L_00056e50:
    mov #-0x2f,r6
    .org 0x56e52 - 0x86f8
L_00056e52:
    extu.b r6,r2
    .org 0x56e54 - 0x86f8
L_00056e54:
    extu.w r2,r6
    .org 0x56e56 - 0x86f8
L_00056e56:
    mov.l L_00056f84,r2
    .org 0x56e58 - 0x86f8
L_00056e58:
    mov.w L_00056f6c,r0
    .org 0x56e5a - 0x86f8
L_00056e5a:
    shll r6
    .org 0x56e5c - 0x86f8
L_00056e5c:
    mov.w r6,@(r0,r2)
    .org 0x56e5e - 0x86f8
L_00056e5e:
    add #0xc,r15
    .org 0x56e60 - 0x86f8
L_00056e60:
    ldc.l @r15+,gbr
    .org 0x56e62 - 0x86f8
L_00056e62:
    lds.l @r15+,macl
    .org 0x56e64 - 0x86f8
L_00056e64:
    lds.l @r15+,pr
    .org 0x56e66 - 0x86f8
L_00056e66:
    mov.l @r15+,r14
    .org 0x56e68 - 0x86f8
L_00056e68:
    mov.l @r15+,r13
    .org 0x56e6a - 0x86f8
L_00056e6a:
    mov.l @r15+,r12
    .org 0x56e6c - 0x86f8
L_00056e6c:
    rts
    .org 0x56e6e - 0x86f8
L_00056e6e:
    mov.l @r15+,r11
    .org 0x56e70 - 0x86f8
L_00056e70:
    mov.l L_00056f88,r6
    .org 0x56e72 - 0x86f8
L_00056e72:
    mov.b @r6,r0
    .org 0x56e74 - 0x86f8
L_00056e74:
    tst #0x1,r0
    .org 0x56e76 - 0x86f8
L_00056e76:
    bf L_00056e8a
    .org 0x56e78 - 0x86f8
L_00056e78:
    mov.l L_00056f8c,r6
    .org 0x56e7a - 0x86f8
L_00056e7a:
    mov.w @(0x2,r6),r0
    .org 0x56e7c - 0x86f8
L_00056e7c:
    extu.w r0,r2
    .org 0x56e7e - 0x86f8
L_00056e7e:
    cmp/pz r2
    .org 0x56e80 - 0x86f8
L_00056e80:
    bt L_00056e84
    .org 0x56e82 - 0x86f8
L_00056e82:
    add #0x3,r2
    .org 0x56e84 - 0x86f8
L_00056e84:
    shar r2
    .org 0x56e86 - 0x86f8
L_00056e86:
    bra L_00056e9e
    .org 0x56e88 - 0x86f8
L_00056e88:
    shar r2
    .org 0x56e8a - 0x86f8
L_00056e8a:
    mov.l L_00056f90,r2
    .org 0x56e8c - 0x86f8
L_00056e8c:
    mov.b @r2,r0
    .org 0x56e8e - 0x86f8
L_00056e8e:
    tst #0x2,r0
    .org 0x56e90 - 0x86f8
L_00056e90:
    bt L_00056e98
    .org 0x56e92 - 0x86f8
L_00056e92:
    mov.l L_00056f94,r6
    .org 0x56e94 - 0x86f8
L_00056e94:
    bra L_00056e9e
    .org 0x56e96 - 0x86f8
L_00056e96:
    mov.w @r6,r2
    .org 0x56e98 - 0x86f8
L_00056e98:
    mov.l L_00056f98,r6
    .org 0x56e9a - 0x86f8
L_00056e9a:
    mov.w L_00056f6e,r0
    .org 0x56e9c - 0x86f8
L_00056e9c:
    mov.w @(r0,r6),r2
    .org 0x56e9e - 0x86f8
L_00056e9e:
    mov.l L_00056f84,r5
    .org 0x56ea0 - 0x86f8
L_00056ea0:
    mov.w L_00056f6c,r0
    .org 0x56ea2 - 0x86f8
L_00056ea2:
    rts
    .org 0x56ea4 - 0x86f8
L_00056ea4:
    mov.w r2,@(r0,r5)
    .org 0x56ea6 - 0x86f8
L_00056ea6:
    mov.l r12,@-r15
    .org 0x56ea8 - 0x86f8
L_00056ea8:
    mov.l r13,@-r15
    .org 0x56eaa - 0x86f8
L_00056eaa:
    mov.l r14,@-r15
    .org 0x56eac - 0x86f8
L_00056eac:
    sts.l pr,@-r15
    .org 0x56eae - 0x86f8
L_00056eae:
    stc.l gbr,@-r15
    .org 0x56eb0 - 0x86f8
L_00056eb0:
    mov.l L_00056f9c,r0
    .org 0x56eb2 - 0x86f8
L_00056eb2:
    ldc r0,gbr
    .org 0x56eb4 - 0x86f8
L_00056eb4:
    mov.l L_00056fa0,r7
    .org 0x56eb6 - 0x86f8
L_00056eb6:
    mov.l L_00056fa4,r2
    .org 0x56eb8 - 0x86f8
L_00056eb8:
    mov.b @(0x4,r7),r0
    .org 0x56eba - 0x86f8
L_00056eba:
    mov.b @r2,r13
    .org 0x56ebc - 0x86f8
L_00056ebc:
    mov r0,r12
    .org 0x56ebe - 0x86f8
L_00056ebe:
    mov.b @(0x30,gbr),r0
    .org 0x56ec0 - 0x86f8
L_00056ec0:
    cmp/hi r13,r12
    .org 0x56ec2 - 0x86f8
L_00056ec2:
    bt/s L_00056eca
    .org 0x56ec4 - 0x86f8
L_00056ec4:
    mov r0,r14
    .org 0x56ec6 - 0x86f8
L_00056ec6:
    mov #0x60,r0
    .org 0x56ec8 - 0x86f8
L_00056ec8:
    or.b #0x2,@(r0,gbr)
    .org 0x56eca - 0x86f8
L_00056eca:
    mov.l L_00056f78,r2
    .org 0x56ecc - 0x86f8
L_00056ecc:
    mov #0x16,r0
    .org 0x56ece - 0x86f8
L_00056ece:
    mov.l L_00056fa8,r5
    .org 0x56ed0 - 0x86f8
L_00056ed0:
    mov.b @(r0,r2),r6
    .org 0x56ed2 - 0x86f8
L_00056ed2:
    mov.b @r5,r2
    .org 0x56ed4 - 0x86f8
L_00056ed4:
    cmp/hs r2,r6
    .org 0x56ed6 - 0x86f8
L_00056ed6:
    bf L_00056edc
    .org 0x56ed8 - 0x86f8
L_00056ed8:
    mov #0x60,r0
    .org 0x56eda - 0x86f8
L_00056eda:
    or.b #0x10,@(r0,gbr)
    .org 0x56edc - 0x86f8
L_00056edc:
    mov.l L_00056fac,r2
    .org 0x56ede - 0x86f8
L_00056ede:
    mov #0x24,r0
    .org 0x56ee0 - 0x86f8
L_00056ee0:
    mov.w @r2,r6
    .org 0x56ee2 - 0x86f8
L_00056ee2:
    mov.l L_00056fb0,r2
    .org 0x56ee4 - 0x86f8
L_00056ee4:
    extu.w r6,r6
    .org 0x56ee6 - 0x86f8
L_00056ee6:
    mov.w @(r0,r2),r5
    .org 0x56ee8 - 0x86f8
L_00056ee8:
    extu.w r5,r5
    .org 0x56eea - 0x86f8
L_00056eea:
    cmp/gt r5,r6
    .org 0x56eec - 0x86f8
L_00056eec:
    bt L_00056f06
    .org 0x56eee - 0x86f8
L_00056eee:
    mov.l L_00056fb4,r6
    .org 0x56ef0 - 0x86f8
L_00056ef0:
    mov.w @r6,r2
    .org 0x56ef2 - 0x86f8
L_00056ef2:
    extu.w r2,r2
    .org 0x56ef4 - 0x86f8
L_00056ef4:
    cmp/ge r2,r5
    .org 0x56ef6 - 0x86f8
L_00056ef6:
    bt L_00056f06
    .org 0x56ef8 - 0x86f8
L_00056ef8:
    mov.l L_00056fb8,r6
    .org 0x56efa - 0x86f8
L_00056efa:
    mov.b @r6,r0
    .org 0x56efc - 0x86f8
L_00056efc:
    tst #0x40,r0
    .org 0x56efe - 0x86f8
L_00056efe:
    bt L_00056f06
    .org 0x56f00 - 0x86f8
L_00056f00:
    mov r14,r0
    .org 0x56f02 - 0x86f8
L_00056f02:
    bra L_00056f0a
    .org 0x56f04 - 0x86f8
L_00056f04:
    or #0x40,r0
    .org 0x56f06 - 0x86f8
L_00056f06:
    mov r14,r0
    .org 0x56f08 - 0x86f8
L_00056f08:
    and #0xbf,r0
    .org 0x56f0a - 0x86f8
L_00056f0a:
    mov.b r0,@(0x30,gbr)
    .org 0x56f0c - 0x86f8
L_00056f0c:
    exts.b r0,r0
    .org 0x56f0e - 0x86f8
L_00056f0e:
    tst #0x40,r0
    .org 0x56f10 - 0x86f8
L_00056f10:
    bf L_00056f5e
    .org 0x56f12 - 0x86f8
L_00056f12:
    mov.b @(0x60,gbr),r0
    .org 0x56f14 - 0x86f8
L_00056f14:
    tst #0x4,r0
    .org 0x56f16 - 0x86f8
L_00056f16:
    bt L_00056f30
    .org 0x56f18 - 0x86f8
L_00056f18:
    mov.l L_00056f98,r5
    .org 0x56f1a - 0x86f8
L_00056f1a:
    mov #-0x1,r6
    .org 0x56f1c - 0x86f8
L_00056f1c:
    mov.w L_00056f70,r0
    .org 0x56f1e - 0x86f8
L_00056f1e:
    extu.b r6,r6
    .org 0x56f20 - 0x86f8
L_00056f20:
    mov.b @(r0,r5),r2
    .org 0x56f22 - 0x86f8
L_00056f22:
    extu.b r2,r2
    .org 0x56f24 - 0x86f8
L_00056f24:
    add #0x1,r2
    .org 0x56f26 - 0x86f8
L_00056f26:
    cmp/hi r6,r2
    .org 0x56f28 - 0x86f8
L_00056f28:
    bf L_00056f2c
    .org 0x56f2a - 0x86f8
L_00056f2a:
    mov r6,r2
    .org 0x56f2c - 0x86f8
L_00056f2c:
    mov.w L_00056f70,r0
    .org 0x56f2e - 0x86f8
L_00056f2e:
    mov.b r2,@(r0,r5)
    .org 0x56f30 - 0x86f8
L_00056f30:
    mov.l L_00056fa0,r7
    .org 0x56f32 - 0x86f8
L_00056f32:
    mov.l L_00056fbc,r4
    .org 0x56f34 - 0x86f8
L_00056f34:
    mov.b @(0x5,r7),r0
    .org 0x56f36 - 0x86f8
L_00056f36:
    mov.l L_00056f80,r2
    .org 0x56f38 - 0x86f8
L_00056f38:
    jsr @r2
    .org 0x56f3a - 0x86f8
L_00056f3a:
    extu.b r0,r5
    .org 0x56f3c - 0x86f8
L_00056f3c:
    mov r0,r2
    .org 0x56f3e - 0x86f8
L_00056f3e:
    mov.l L_00056f84,r6
    .org 0x56f40 - 0x86f8
L_00056f40:
    mov.w L_00056f72,r0
    .org 0x56f42 - 0x86f8
L_00056f42:
    mov.l L_00056f98,r5
    .org 0x56f44 - 0x86f8
L_00056f44:
    mov.b r2,@(r0,r6)
    .org 0x56f46 - 0x86f8
L_00056f46:
    extu.b r2,r2
    .org 0x56f48 - 0x86f8
L_00056f48:
    mov.w L_00056f70,r0
    .org 0x56f4a - 0x86f8
L_00056f4a:
    mov.b @(r0,r5),r6
    .org 0x56f4c - 0x86f8
L_00056f4c:
    extu.b r6,r5
    .org 0x56f4e - 0x86f8
L_00056f4e:
    cmp/ge r2,r5
    .org 0x56f50 - 0x86f8
L_00056f50:
    bf L_00056f5e
    .org 0x56f52 - 0x86f8
L_00056f52:
    mov.l L_00056fb8,r6
    .org 0x56f54 - 0x86f8
L_00056f54:
    mov.b @r6,r0
    .org 0x56f56 - 0x86f8
L_00056f56:
    tst #0x40,r0
    .org 0x56f58 - 0x86f8
L_00056f58:
    bt L_00056f5e
    .org 0x56f5a - 0x86f8
L_00056f5a:
    mov #0x60,r0
    .org 0x56f5c - 0x86f8
L_00056f5c:
    or.b #0x80,@(r0,gbr)
    .org 0x56f5e - 0x86f8
L_00056f5e:
    ldc.l @r15+,gbr
    .org 0x56f60 - 0x86f8
L_00056f60:
    lds.l @r15+,pr
    .org 0x56f62 - 0x86f8
L_00056f62:
    mov.l @r15+,r14
    .org 0x56f64 - 0x86f8
L_00056f64:
    mov.l @r15+,r13
    .org 0x56f66 - 0x86f8
L_00056f66:
    rts
    .org 0x56f68 - 0x86f8
L_00056f68:
    mov.l @r15+,r12
    .org 0x56f6a - 0x86f8
L_00056f6a:
    .word 0x0b14
    .org 0x56f6c - 0x86f8
L_00056f6c:
    .word 0x06a2
    .org 0x56f6e - 0x86f8
L_00056f6e:
    .word 0x102c
    .org 0x56f70 - 0x86f8
L_00056f70:
    .word 0x0f96
    .org 0x56f72 - 0x86f8
L_00056f72:
    .word 0x0253
    .org 0x56f74 - 0x86f8
L_00056f74:
    .long 0xffff28f8
    .org 0x56f78 - 0x86f8
L_00056f78:
    .long 0xffff119c
    .org 0x56f7c - 0x86f8
L_00056f7c:
    .long 0x00012302
    .org 0x56f80 - 0x86f8
L_00056f80:
    .long 0x00026370
    .org 0x56f84 - 0x86f8
L_00056f84:
    .long 0xffff128c
    .org 0x56f88 - 0x86f8
L_00056f88:
    .long 0x00008b42
    .org 0x56f8c - 0x86f8
L_00056f8c:
    .long 0xffff1000
    .org 0x56f90 - 0x86f8
L_00056f90:
    .long 0x000086f9
    .org 0x56f94 - 0x86f8
L_00056f94:
    .long 0x000090fa
    .org 0x56f98 - 0x86f8
L_00056f98:
    .long 0xffff4558
    .org 0x56f9c - 0x86f8
L_00056f9c:
    .long 0xffff2470
    .org 0x56fa0 - 0x86f8
L_00056fa0:
    .long 0xffff106a
    .org 0x56fa4 - 0x86f8
L_00056fa4:
    .long 0x00008cec
    .org 0x56fa8 - 0x86f8
L_00056fa8:
    .long 0x000088bb
    .org 0x56fac - 0x86f8
L_00056fac:
    .long 0x00009038
    .org 0x56fb0 - 0x86f8
L_00056fb0:
    .long 0xffff267a
    .org 0x56fb4 - 0x86f8
L_00056fb4:
    .long 0x00009036
    .org 0x56fb8 - 0x86f8
L_00056fb8:
    .long 0xffff4184
    .org 0x56fbc - 0x86f8
L_00056fbc:
    .long 0x00012136
