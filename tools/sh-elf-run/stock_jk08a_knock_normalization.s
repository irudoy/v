! Exact eight-word normalization and positive word-denominator divider.
    .section .text
    .balign 4
    .org 0x8b3d - 0x8b3c
P_8b3d:
    .byte 0x82
    .org 0x21ce0 - 0x8b3c
L_21ce0:
    mov.l r2,@-r15
    .org 0x21ce2 - 0x8b3c
L_21ce2:
    tst r0,r0
    .org 0x21ce4 - 0x8b3c
L_21ce4:
    bt L_21d6a
    .org 0x21ce6 - 0x8b3c
L_21ce6:
    extu.w r0,r2
    .org 0x21ce8 - 0x8b3c
L_21ce8:
    cmp/eq r2,r0
    .org 0x21cea - 0x8b3c
L_21cea:
    bf L_21d76
    .org 0x21cec - 0x8b3c
L_21cec:
    div0u
    .org 0x21cee - 0x8b3c
L_21cee:
    shll8 r0
    .org 0x21cf0 - 0x8b3c
L_21cf0:
    cmp/hi r1,r0
    .org 0x21cf2 - 0x8b3c
L_21cf2:
    bf L_21d0c
    .org 0x21cf4 - 0x8b3c
L_21cf4:
    div1 r0,r1
    .org 0x21cf6 - 0x8b3c
L_21cf6:
    div1 r0,r1
    .org 0x21cf8 - 0x8b3c
L_21cf8:
    div1 r0,r1
    .org 0x21cfa - 0x8b3c
L_21cfa:
    div1 r0,r1
    .org 0x21cfc - 0x8b3c
L_21cfc:
    div1 r0,r1
    .org 0x21cfe - 0x8b3c
L_21cfe:
    div1 r0,r1
    .org 0x21d00 - 0x8b3c
L_21d00:
    div1 r0,r1
    .org 0x21d02 - 0x8b3c
L_21d02:
    div1 r0,r1
    .org 0x21d04 - 0x8b3c
L_21d04:
    rotcl r1
    .org 0x21d06 - 0x8b3c
L_21d06:
    mov.l @r15+,r2
    .org 0x21d08 - 0x8b3c
L_21d08:
    rts
    .org 0x21d0a - 0x8b3c
L_21d0a:
    extu.b r1,r0
    .org 0x21d0c - 0x8b3c
L_21d0c:
    mov.l r3,@-r15
    .org 0x21d0e - 0x8b3c
L_21d0e:
    extu.w r1,r3
    .org 0x21d10 - 0x8b3c
L_21d10:
    shll8 r0
    .org 0x21d12 - 0x8b3c
L_21d12:
    shlr16 r1
    .org 0x21d14 - 0x8b3c
L_21d14:
    div1 r0,r1
    .org 0x21d16 - 0x8b3c
L_21d16:
    div1 r0,r1
    .org 0x21d18 - 0x8b3c
L_21d18:
    div1 r0,r1
    .org 0x21d1a - 0x8b3c
L_21d1a:
    div1 r0,r1
    .org 0x21d1c - 0x8b3c
L_21d1c:
    div1 r0,r1
    .org 0x21d1e - 0x8b3c
L_21d1e:
    div1 r0,r1
    .org 0x21d20 - 0x8b3c
L_21d20:
    div1 r0,r1
    .org 0x21d22 - 0x8b3c
L_21d22:
    div1 r0,r1
    .org 0x21d24 - 0x8b3c
L_21d24:
    div1 r0,r1
    .org 0x21d26 - 0x8b3c
L_21d26:
    div1 r0,r1
    .org 0x21d28 - 0x8b3c
L_21d28:
    div1 r0,r1
    .org 0x21d2a - 0x8b3c
L_21d2a:
    div1 r0,r1
    .org 0x21d2c - 0x8b3c
L_21d2c:
    div1 r0,r1
    .org 0x21d2e - 0x8b3c
L_21d2e:
    div1 r0,r1
    .org 0x21d30 - 0x8b3c
L_21d30:
    div1 r0,r1
    .org 0x21d32 - 0x8b3c
L_21d32:
    div1 r0,r1
    .org 0x21d34 - 0x8b3c
L_21d34:
    extu.w r1,r2
    .org 0x21d36 - 0x8b3c
L_21d36:
    xor r2,r1
    .org 0x21d38 - 0x8b3c
L_21d38:
    addc r2,r2
    .org 0x21d3a - 0x8b3c
L_21d3a:
    shll16 r2
    .org 0x21d3c - 0x8b3c
L_21d3c:
    add r3,r1
    .org 0x21d3e - 0x8b3c
L_21d3e:
    div1 r0,r1
    .org 0x21d40 - 0x8b3c
L_21d40:
    div1 r0,r1
    .org 0x21d42 - 0x8b3c
L_21d42:
    div1 r0,r1
    .org 0x21d44 - 0x8b3c
L_21d44:
    div1 r0,r1
    .org 0x21d46 - 0x8b3c
L_21d46:
    div1 r0,r1
    .org 0x21d48 - 0x8b3c
L_21d48:
    div1 r0,r1
    .org 0x21d4a - 0x8b3c
L_21d4a:
    div1 r0,r1
    .org 0x21d4c - 0x8b3c
L_21d4c:
    div1 r0,r1
    .org 0x21d4e - 0x8b3c
L_21d4e:
    div1 r0,r1
    .org 0x21d50 - 0x8b3c
L_21d50:
    div1 r0,r1
    .org 0x21d52 - 0x8b3c
L_21d52:
    div1 r0,r1
    .org 0x21d54 - 0x8b3c
L_21d54:
    div1 r0,r1
    .org 0x21d56 - 0x8b3c
L_21d56:
    div1 r0,r1
    .org 0x21d58 - 0x8b3c
L_21d58:
    div1 r0,r1
    .org 0x21d5a - 0x8b3c
L_21d5a:
    div1 r0,r1
    .org 0x21d5c - 0x8b3c
L_21d5c:
    div1 r0,r1
    .org 0x21d5e - 0x8b3c
L_21d5e:
    rotcl r1
    .org 0x21d60 - 0x8b3c
L_21d60:
    extu.w r1,r0
    .org 0x21d62 - 0x8b3c
L_21d62:
    add r2,r0
    .org 0x21d64 - 0x8b3c
L_21d64:
    mov.l @r15+,r3
    .org 0x21d66 - 0x8b3c
L_21d66:
    rts
    .org 0x21d68 - 0x8b3c
L_21d68:
    mov.l @r15+,r2
    .org 0x21d6a - 0x8b3c
L_21d6a:
    .org 0x21d76 - 0x8b3c
L_21d76:
    .org 0x4a24c - 0x8b3c
P_4a24c:
    .byte 0xd2,0x9e,0x60,0x20,0xc9,0x08,0x20,0x08,0x8d,0x02,0x6b,0x03
    .org 0x4a25c - 0x8b3c
P_4a25c:
    .byte 0xde,0x9b,0x84,0xea,0x65,0x0c,0x25,0x58,0x8b,0x01,0xa0,0x90,0x00,0x09
    .org 0x4a26a - 0x8b3c
L_4a26a:
    mov.l P_4a4d0,r14
    .org 0x4a26c - 0x8b3c
L_4a26c:
    mov #0x58,r0
    .org 0x4a26e - 0x8b3c
L_4a26e:
    shll2 r0
    .org 0x4a270 - 0x8b3c
L_4a270:
    mov.b @(r0,r14),r6
    .org 0x4a272 - 0x8b3c
L_4a272:
    extu.b r6,r6
    .org 0x4a274 - 0x8b3c
L_4a274:
    shll2 r6
    .org 0x4a276 - 0x8b3c
L_4a276:
    shll2 r6
    .org 0x4a278 - 0x8b3c
L_4a278:
    shll r6
    .org 0x4a27a - 0x8b3c
L_4a27a:
    extu.w r6,r9
    .org 0x4a27c - 0x8b3c
L_4a27c:
    tst r9,r9
    .org 0x4a27e - 0x8b3c
L_4a27e:
    bt L_4a284
    .org 0x4a280 - 0x8b3c
L_4a280:
    bra L_4a4fc
    .org 0x4a282 - 0x8b3c
L_4a282:
    nop
    .org 0x4a284 - 0x8b3c
L_4a284:
    mov r5,r14
    .org 0x4a286 - 0x8b3c
L_4a286:
    mov r5,r6
    .org 0x4a288 - 0x8b3c
L_4a288:
    shll2 r6
    .org 0x4a28a - 0x8b3c
L_4a28a:
    mov.l P_4a4d4,r5
    .org 0x4a28c - 0x8b3c
L_4a28c:
    shll2 r14
    .org 0x4a28e - 0x8b3c
L_4a28e:
    shll2 r6
    .org 0x4a290 - 0x8b3c
L_4a290:
    shll2 r14
    .org 0x4a292 - 0x8b3c
L_4a292:
    sub r6,r14
    .org 0x4a294 - 0x8b3c
L_4a294:
    add r6,r5
    .org 0x4a296 - 0x8b3c
L_4a296:
    mov.l P_4a4d8,r6
    .org 0x4a298 - 0x8b3c
L_4a298:
    add #0x2,r14
    .org 0x4a29a - 0x8b3c
L_4a29a:
    add #-0x10,r5
    .org 0x4a29c - 0x8b3c
L_4a29c:
    mov.l r6,@r15
    .org 0x4a29e - 0x8b3c
L_4a29e:
    mov #0x4,r7
    .org 0x4a2a0 - 0x8b3c
L_4a2a0:
    mov #-0x1,r2
    .org 0x4a2a2 - 0x8b3c
L_4a2a2:
    dt r7
    .org 0x4a2a4 - 0x8b3c
L_4a2a4:
    mov.w r2,@r6
    .org 0x4a2a6 - 0x8b3c
L_4a2a6:
    mov.w r2,@r5
    .org 0x4a2a8 - 0x8b3c
L_4a2a8:
    mov r2,r0
    .org 0x4a2aa - 0x8b3c
L_4a2aa:
    mov.w r0,@(0x2,r6)
    .org 0x4a2ac - 0x8b3c
L_4a2ac:
    mov r14,r0
    .org 0x4a2ae - 0x8b3c
L_4a2ae:
    mov.w r2,@(r0,r5)
    .org 0x4a2b0 - 0x8b3c
L_4a2b0:
    add #0x4,r6
    .org 0x4a2b2 - 0x8b3c
L_4a2b2:
    bf/s L_4a2a2
    .org 0x4a2b4 - 0x8b3c
L_4a2b4:
    add #0x4,r5
    .org 0x4a2b6 - 0x8b3c
L_4a2b6:
    .org 0x4a3a0 - 0x8b3c
P_4a3a0:
    .byte 0xe0,0x01,0xde,0x4b,0x40,0x18,0x70,0x4f,0x05,0xec,0x6e,0x5c,0x2e,0xe8,0x89,0xec
    .org 0x4a3b0 - 0x8b3c
L_4a3b0:
    mov.l P_4a4d0,r3
    .org 0x4a3b2 - 0x8b3c
L_4a3b2:
    mov #0x58,r0
    .org 0x4a3b4 - 0x8b3c
L_4a3b4:
    shll2 r0
    .org 0x4a3b6 - 0x8b3c
L_4a3b6:
    mov.b @(r0,r3),r6
    .org 0x4a3b8 - 0x8b3c
L_4a3b8:
    extu.b r6,r6
    .org 0x4a3ba - 0x8b3c
L_4a3ba:
    shll2 r6
    .org 0x4a3bc - 0x8b3c
L_4a3bc:
    shll2 r6
    .org 0x4a3be - 0x8b3c
L_4a3be:
    shll r6
    .org 0x4a3c0 - 0x8b3c
L_4a3c0:
    extu.w r6,r9
    .org 0x4a3c2 - 0x8b3c
L_4a3c2:
    tst r9,r9
    .org 0x4a3c4 - 0x8b3c
L_4a3c4:
    bt L_4a3ca
    .org 0x4a3c6 - 0x8b3c
L_4a3c6:
    bra L_4a4fc
    .org 0x4a3c8 - 0x8b3c
L_4a3c8:
    nop
    .org 0x4a3ca - 0x8b3c
L_4a3ca:
    mov r14,r6
    .org 0x4a3cc - 0x8b3c
L_4a3cc:
    shll2 r6
    .org 0x4a3ce - 0x8b3c
L_4a3ce:
    shll2 r14
    .org 0x4a3d0 - 0x8b3c
L_4a3d0:
    mov.l P_4a4d4,r5
    .org 0x4a3d2 - 0x8b3c
L_4a3d2:
    shll2 r6
    .org 0x4a3d4 - 0x8b3c
L_4a3d4:
    shll2 r14
    .org 0x4a3d6 - 0x8b3c
L_4a3d6:
    sub r6,r14
    .org 0x4a3d8 - 0x8b3c
L_4a3d8:
    add r6,r5
    .org 0x4a3da - 0x8b3c
L_4a3da:
    mov.l P_4a4d8,r6
    .org 0x4a3dc - 0x8b3c
L_4a3dc:
    add #0x2,r14
    .org 0x4a3de - 0x8b3c
L_4a3de:
    add #-0x10,r5
    .org 0x4a3e0 - 0x8b3c
L_4a3e0:
    mov.l r6,@r15
    .org 0x4a3e2 - 0x8b3c
L_4a3e2:
    mov #0x4,r7
    .org 0x4a3e4 - 0x8b3c
L_4a3e4:
    mov #-0x1,r2
    .org 0x4a3e6 - 0x8b3c
L_4a3e6:
    dt r7
    .org 0x4a3e8 - 0x8b3c
L_4a3e8:
    mov.w r2,@r6
    .org 0x4a3ea - 0x8b3c
L_4a3ea:
    mov.w r2,@r5
    .org 0x4a3ec - 0x8b3c
L_4a3ec:
    mov r2,r0
    .org 0x4a3ee - 0x8b3c
L_4a3ee:
    mov.w r0,@(0x2,r6)
    .org 0x4a3f0 - 0x8b3c
L_4a3f0:
    mov r14,r0
    .org 0x4a3f2 - 0x8b3c
L_4a3f2:
    mov.w r2,@(r0,r5)
    .org 0x4a3f4 - 0x8b3c
L_4a3f4:
    add #0x4,r6
    .org 0x4a3f6 - 0x8b3c
L_4a3f6:
    bf/s L_4a3e6
    .org 0x4a3f8 - 0x8b3c
L_4a3f8:
    add #0x4,r5
    .org 0x4a3fa - 0x8b3c
L_4a3fa:
    bra L_4a2b6
    .org 0x4a3fc - 0x8b3c
L_4a3fc:
    nop
    .org 0x4a438 - 0x8b3c
L_4a438:
    mov.l P_4a4cc,r3
    .org 0x4a43a - 0x8b3c
L_4a43a:
    mov.l @(0x4,r15),r7
    .org 0x4a43c - 0x8b3c
L_4a43c:
    mov.b @(0xa,r3),r0
    .org 0x4a43e - 0x8b3c
L_4a43e:
    extu.b r0,r0
    .org 0x4a440 - 0x8b3c
L_4a440:
    shll2 r0
    .org 0x4a442 - 0x8b3c
L_4a442:
    shll2 r0
    .org 0x4a444 - 0x8b3c
L_4a444:
    add r14,r0
    .org 0x4a446 - 0x8b3c
L_4a446:
    mov.w r2,@(r0,r7)
    .org 0x4a448 - 0x8b3c
L_4a448:
    dt r13
    .org 0x4a44a - 0x8b3c
L_4a44a:
    add #0x2,r14
    .org 0x4a44c - 0x8b3c
L_4a44c:
    bf/s L_4a454
    .org 0x4a44e - 0x8b3c
L_4a44e:
    add #0x2,r12
    .org 0x4a450 - 0x8b3c
L_4a450:
    bra L_4a2b6
    .org 0x4a452 - 0x8b3c
L_4a452:
    nop
    .org 0x4a454 - 0x8b3c
L_4a454:
    mov.l P_4a4f4,r6
    .org 0x4a456 - 0x8b3c
L_4a456:
    mov r14,r0
    .org 0x4a458 - 0x8b3c
L_4a458:
    extu.w r10,r10
    .org 0x4a45a - 0x8b3c
L_4a45a:
    mov.w @(r0,r6),r2
    .org 0x4a45c - 0x8b3c
L_4a45c:
    extu.w r9,r9
    .org 0x4a45e - 0x8b3c
L_4a45e:
    mov.l P_4a4f8,r6
    .org 0x4a460 - 0x8b3c
L_4a460:
    mov r9,r0
    .org 0x4a462 - 0x8b3c
L_4a462:
    extu.w r2,r2
    .org 0x4a464 - 0x8b3c
L_4a464:
    mul.l r2,r10
    .org 0x4a466 - 0x8b3c
L_4a466:
    jsr @r6
    .org 0x4a468 - 0x8b3c
L_4a468:
    sts macl,r1
    .org 0x4a46a - 0x8b3c
L_4a46a:
    shll2 r0
    .org 0x4a46c - 0x8b3c
L_4a46c:
    shll r0
    .org 0x4a46e - 0x8b3c
L_4a46e:
    cmp/hi r8,r0
    .org 0x4a470 - 0x8b3c
L_4a470:
    bf/s L_4a476
    .org 0x4a472 - 0x8b3c
L_4a472:
    mov r0,r2
    .org 0x4a474 - 0x8b3c
L_4a474:
    mov r8,r2
    .org 0x4a476 - 0x8b3c
L_4a476:
    extu.b r11,r11
    .org 0x4a478 - 0x8b3c
L_4a478:
    tst r11,r11
    .org 0x4a47a - 0x8b3c
L_4a47a:
    bt/s L_4a438
    .org 0x4a47c - 0x8b3c
L_4a47c:
    mov.w r2,@r12
    .org 0x4a47e - 0x8b3c
L_4a47e:
    mov #0x1,r0
    .org 0x4a480 - 0x8b3c
L_4a480:
    mov.l P_4a4d0,r3
    .org 0x4a482 - 0x8b3c
L_4a482:
    shll8 r0
    .org 0x4a484 - 0x8b3c
L_4a484:
    mov.l @(0x4,r15),r7
    .org 0x4a486 - 0x8b3c
L_4a486:
    add #0x4f,r0
    .org 0x4a488 - 0x8b3c
L_4a488:
    mov.b @(r0,r3),r6
    .org 0x4a48a - 0x8b3c
L_4a48a:
    extu.b r6,r0
    .org 0x4a48c - 0x8b3c
L_4a48c:
    shll2 r0
    .org 0x4a48e - 0x8b3c
L_4a48e:
    shll2 r0
    .org 0x4a490 - 0x8b3c
L_4a490:
    add r14,r0
    .org 0x4a492 - 0x8b3c
L_4a492:
    bra L_4a448
    .org 0x4a494 - 0x8b3c
L_4a494:
    mov.w r2,@(r0,r7)
    .org 0x4a4c8 - 0x8b3c
P_4a4c8:
    .long 0x00008b3d
    .org 0x4a4cc - 0x8b3c
P_4a4cc:
    .long 0xffff11d4
    .org 0x4a4d0 - 0x8b3c
P_4a4d0:
    .long 0xffff1ff4
    .org 0x4a4d4 - 0x8b3c
P_4a4d4:
    .long 0xffff20d2
    .org 0x4a4d8 - 0x8b3c
P_4a4d8:
    .long 0xffff20c2
    .org 0x4a4f4 - 0x8b3c
P_4a4f4:
    .long 0xffff2132
    .org 0x4a4f8 - 0x8b3c
P_4a4f8:
    .long 0x00021ce0
    .org 0x4a4fc - 0x8b3c
L_4a4fc:
    mov.l P_4a590,r6
    .org 0x4a4fe - 0x8b3c
L_4a4fe:
    mov.b @r6,r2
    .org 0x4a500 - 0x8b3c
L_4a500:
    tst r2,r2
    .org 0x4a502 - 0x8b3c
L_4a502:
    bt L_4a522
    .org 0x4a504 - 0x8b3c
L_4a504:
    mov #0x1,r0
    .org 0x4a506 - 0x8b3c
L_4a506:
    mov.l P_4a594,r7
    .org 0x4a508 - 0x8b3c
L_4a508:
    mov.l P_4a598,r3
    .org 0x4a50a - 0x8b3c
L_4a50a:
    shll8 r0
    .org 0x4a50c - 0x8b3c
L_4a50c:
    mov.l P_4a59c,r12
    .org 0x4a50e - 0x8b3c
L_4a50e:
    add #0x5e,r0
    .org 0x4a510 - 0x8b3c
L_4a510:
    add #-0x10,r7
    .org 0x4a512 - 0x8b3c
L_4a512:
    mov.w @(r0,r3),r10
    .org 0x4a514 - 0x8b3c
L_4a514:
    mov #-0x1,r8
    .org 0x4a516 - 0x8b3c
L_4a516:
    mov.l r12,@r15
    .org 0x4a518 - 0x8b3c
L_4a518:
    mov.l r7,@(0x4,r15)
    .org 0x4a51a - 0x8b3c
L_4a51a:
    extu.w r8,r8
    .org 0x4a51c - 0x8b3c
L_4a51c:
    mov #0x8,r13
    .org 0x4a51e - 0x8b3c
L_4a51e:
    bra L_4a454
    .org 0x4a520 - 0x8b3c
L_4a520:
    mov #0x0,r14
    .org 0x4a522 - 0x8b3c
L_4a522:
    mov #0x1,r0
    .org 0x4a524 - 0x8b3c
L_4a524:
    mov.l P_4a598,r8
    .org 0x4a526 - 0x8b3c
L_4a526:
    shll8 r0
    .org 0x4a528 - 0x8b3c
L_4a528:
    mov.l P_4a594,r7
    .org 0x4a52a - 0x8b3c
L_4a52a:
    add #0x4f,r0
    .org 0x4a52c - 0x8b3c
L_4a52c:
    mov.l P_4a59c,r13
    .org 0x4a52e - 0x8b3c
L_4a52e:
    mov.b @(r0,r8),r10
    .org 0x4a530 - 0x8b3c
L_4a530:
    mov #0x1,r0
    .org 0x4a532 - 0x8b3c
L_4a532:
    shll8 r0
    .org 0x4a534 - 0x8b3c
L_4a534:
    mov.l r13,@r15
    .org 0x4a536 - 0x8b3c
L_4a536:
    add #0x5e,r0
    .org 0x4a538 - 0x8b3c
L_4a538:
    add #-0x10,r7
    .org 0x4a53a - 0x8b3c
L_4a53a:
    mov.w @(r0,r8),r12
    .org 0x4a53c - 0x8b3c
L_4a53c:
    mov.l r7,@(0x8,r15)
    .org 0x4a53e - 0x8b3c
L_4a53e:
    mov #0x0,r14
    .org 0x4a540 - 0x8b3c
L_4a540:
    mov.l P_4a5a0,r6
    .org 0x4a542 - 0x8b3c
L_4a542:
    mov r14,r0
    .org 0x4a544 - 0x8b3c
L_4a544:
    extu.w r12,r12
    .org 0x4a546 - 0x8b3c
L_4a546:
    mov.w @(r0,r6),r2
    .org 0x4a548 - 0x8b3c
L_4a548:
    extu.w r9,r9
    .org 0x4a54a - 0x8b3c
L_4a54a:
    mov.l P_4a5a4,r6
    .org 0x4a54c - 0x8b3c
L_4a54c:
    extu.b r11,r11
    .org 0x4a54e - 0x8b3c
L_4a54e:
    extu.w r2,r2
    .org 0x4a550 - 0x8b3c
L_4a550:
    mov r9,r0
    .org 0x4a552 - 0x8b3c
L_4a552:
    mul.l r2,r12
    .org 0x4a554 - 0x8b3c
L_4a554:
    jsr @r6
    .org 0x4a556 - 0x8b3c
L_4a556:
    sts macl,r1
    .org 0x4a558 - 0x8b3c
L_4a558:
    tst r11,r11
    .org 0x4a55a - 0x8b3c
L_4a55a:
    mov r0,r2
    .org 0x4a55c - 0x8b3c
L_4a55c:
    bt/s L_4a57c
    .org 0x4a55e - 0x8b3c
L_4a55e:
    mov.w r0,@r13
    .org 0x4a560 - 0x8b3c
L_4a560:
    extu.b r10,r10
    .org 0x4a562 - 0x8b3c
L_4a562:
    mov.l @(0x8,r15),r7
    .org 0x4a564 - 0x8b3c
L_4a564:
    mov r10,r0
    .org 0x4a566 - 0x8b3c
L_4a566:
    shll2 r0
    .org 0x4a568 - 0x8b3c
L_4a568:
    shll2 r0
    .org 0x4a56a - 0x8b3c
L_4a56a:
    add r14,r0
    .org 0x4a56c - 0x8b3c
L_4a56c:
    mov.w r2,@(r0,r7)
    .org 0x4a56e - 0x8b3c
L_4a56e:
    add #0x2,r14
    .org 0x4a570 - 0x8b3c
L_4a570:
    mov #0x10,r2
    .org 0x4a572 - 0x8b3c
L_4a572:
    cmp/ge r2,r14
    .org 0x4a574 - 0x8b3c
L_4a574:
    bf/s L_4a540
    .org 0x4a576 - 0x8b3c
L_4a576:
    add #0x2,r13
    .org 0x4a578 - 0x8b3c
L_4a578:
    bra L_4a2b6
    .org 0x4a57a - 0x8b3c
L_4a57a:
    nop
    .org 0x4a57c - 0x8b3c
L_4a57c:
    mov.l P_4a5a8,r3
    .org 0x4a57e - 0x8b3c
L_4a57e:
    mov.l @(0x8,r15),r7
    .org 0x4a580 - 0x8b3c
L_4a580:
    mov.b @(0xa,r3),r0
    .org 0x4a582 - 0x8b3c
L_4a582:
    extu.b r0,r0
    .org 0x4a584 - 0x8b3c
L_4a584:
    shll2 r0
    .org 0x4a586 - 0x8b3c
L_4a586:
    shll2 r0
    .org 0x4a588 - 0x8b3c
L_4a588:
    add r14,r0
    .org 0x4a58a - 0x8b3c
L_4a58a:
    bra L_4a56e
    .org 0x4a58c - 0x8b3c
L_4a58c:
    mov.w r2,@(r0,r7)
    .org 0x4a590 - 0x8b3c
P_4a590:
    .long 0xffff87e1
    .org 0x4a594 - 0x8b3c
P_4a594:
    .long 0xffff20d2
    .org 0x4a598 - 0x8b3c
P_4a598:
    .long 0xffff1ff4
    .org 0x4a59c - 0x8b3c
P_4a59c:
    .long 0xffff20c2
    .org 0x4a5a0 - 0x8b3c
P_4a5a0:
    .long 0xffff2132
    .org 0x4a5a4 - 0x8b3c
P_4a5a4:
    .long 0x00021ce0
    .org 0x4a5a8 - 0x8b3c
P_4a5a8:
    .long 0xffff11d4
