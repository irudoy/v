! Exact natural word-rate and scaling paths with selected ROM-root absence.
    .text
    .balign 4
    .set ORIGIN,0x90a4
    .org 0x90a6-ORIGIN
P_000090a6:
    .byte 0x03
    .org 0x90a7-ORIGIN
P_000090a7:
    .byte 0xe8
    .org 0x90a8-ORIGIN
P_000090a8:
    .byte 0x03
    .org 0x90a9-ORIGIN
P_000090a9:
    .byte 0xe8
    .org 0x93c8-ORIGIN
P_000093c8:
    .byte 0x00
    .org 0x93c9-ORIGIN
P_000093c9:
    .byte 0x00
    .org 0x6e490-ORIGIN
L_0006e490:
    sts.l macl,@-r15
    .org 0x6e492-ORIGIN
L_0006e492:
    mov.l P_0006e5c4,r4
    .org 0x6e494-ORIGIN
L_0006e494:
    mov.w P_0006e4e2,r0
    .org 0x6e496-ORIGIN
L_0006e496:
    mov.b @(r0,r4),r2
    .org 0x6e498-ORIGIN
L_0006e498:
    extu.b r2,r5
    .org 0x6e49a-ORIGIN
L_0006e49a:
    mov.l P_0006e5ec,r2
    .org 0x6e49c-ORIGIN
L_0006e49c:
    mov.w @r2,r6
    .org 0x6e49e-ORIGIN
L_0006e49e:
    extu.w r6,r2
    .org 0x6e4a0-ORIGIN
L_0006e4a0:
    mov.l P_0006e5f0,r6
    .org 0x6e4a2-ORIGIN
L_0006e4a2:
    mul.l r5,r2
    .org 0x6e4a4-ORIGIN
L_0006e4a4:
    sts macl,r2
    .org 0x6e4a6-ORIGIN
L_0006e4a6:
    shll2 r2
    .org 0x6e4a8-ORIGIN
L_0006e4a8:
    cmp/hi r6,r2
    .org 0x6e4aa-ORIGIN
L_0006e4aa:
    bf L_0006e4ae
    .org 0x6e4ac-ORIGIN
L_0006e4ac:
    mov r6,r2
    .org 0x6e4ae-ORIGIN
L_0006e4ae:
    mov.w P_0006e4e8,r6
    .org 0x6e4b0-ORIGIN
L_0006e4b0:
    mul.l r2,r6
    .org 0x6e4b2-ORIGIN
L_0006e4b2:
    mov #-0x1,r6
    .org 0x6e4b4-ORIGIN
L_0006e4b4:
    extu.w r6,r6
    .org 0x6e4b6-ORIGIN
L_0006e4b6:
    sts macl,r2
    .org 0x6e4b8-ORIGIN
L_0006e4b8:
    shlr16 r2
    .org 0x6e4ba-ORIGIN
L_0006e4ba:
    cmp/hi r6,r2
    .org 0x6e4bc-ORIGIN
L_0006e4bc:
    bf L_0006e4c0
    .org 0x6e4be-ORIGIN
L_0006e4be:
    mov r6,r2
    .org 0x6e4c0-ORIGIN
L_0006e4c0:
    mov #0x74,r0
    .org 0x6e4c2-ORIGIN
L_0006e4c2:
    mov.w r2,@(r0,r4)
    .org 0x6e4c4-ORIGIN
L_0006e4c4:
    rts
    .org 0x6e4c6-ORIGIN
L_0006e4c6:
    lds.l @r15+,macl
    .org 0x6e4e2-ORIGIN
P_0006e4e2:
    .byte 0x04
    .org 0x6e4e3-ORIGIN
P_0006e4e3:
    .byte 0xda
    .org 0x6e4e8-ORIGIN
P_0006e4e8:
    .byte 0x04
    .org 0x6e4e9-ORIGIN
P_0006e4e9:
    .byte 0xe2
    .org 0x6e5c4-ORIGIN
P_0006e5c4:
    .byte 0xff
    .org 0x6e5c5-ORIGIN
P_0006e5c5:
    .byte 0xff
    .org 0x6e5c6-ORIGIN
P_0006e5c6:
    .byte 0x12
    .org 0x6e5c7-ORIGIN
P_0006e5c7:
    .byte 0x8c
    .org 0x6e5ec-ORIGIN
P_0006e5ec:
    .byte 0x00
    .org 0x6e5ed-ORIGIN
P_0006e5ed:
    .byte 0x00
    .org 0x6e5ee-ORIGIN
P_0006e5ee:
    .byte 0x93
    .org 0x6e5ef-ORIGIN
P_0006e5ef:
    .byte 0xc8
    .org 0x6e5f0-ORIGIN
P_0006e5f0:
    .byte 0x00
    .org 0x6e5f1-ORIGIN
P_0006e5f1:
    .byte 0x34
    .org 0x6e5f2-ORIGIN
P_0006e5f2:
    .byte 0x6d
    .org 0x6e5f3-ORIGIN
P_0006e5f3:
    .byte 0xc5
    .org 0x76380-ORIGIN
L_00076380:
    mov.l P_00076454,r7
    .org 0x76382-ORIGIN
L_00076382:
    mov.w P_00076448,r0
    .org 0x76384-ORIGIN
L_00076384:
    mov.l P_00076470,r2
    .org 0x76386-ORIGIN
L_00076386:
    mov.w @(r0,r7),r4
    .org 0x76388-ORIGIN
L_00076388:
    mov.w P_0007644a,r0
    .org 0x7638a-ORIGIN
L_0007638a:
    mov.l P_00076474,r5
    .org 0x7638c-ORIGIN
L_0007638c:
    mov.w @(r0,r2),r6
    .org 0x7638e-ORIGIN
L_0007638e:
    cmp/gt r4,r6
    .org 0x76390-ORIGIN
L_00076390:
    bf L_000763a2
    .org 0x76392-ORIGIN
L_00076392:
    mov.w @(0x2,r5),r0
    .org 0x76394-ORIGIN
L_00076394:
    extu.w r0,r2
    .org 0x76396-ORIGIN
L_00076396:
    add r2,r4
    .org 0x76398-ORIGIN
L_00076398:
    cmp/gt r6,r4
    .org 0x7639a-ORIGIN
L_0007639a:
    bf/s L_000763b0
    .org 0x7639c-ORIGIN
L_0007639c:
    mov r4,r5
    .org 0x7639e-ORIGIN
L_0007639e:
    bra L_000763b0
    .org 0x763a0-ORIGIN
L_000763a0:
    exts.w r6,r5
    .org 0x763a2-ORIGIN
L_000763a2:
    mov.w @r5,r2
    .org 0x763a4-ORIGIN
L_000763a4:
    extu.w r2,r2
    .org 0x763a6-ORIGIN
L_000763a6:
    sub r2,r4
    .org 0x763a8-ORIGIN
L_000763a8:
    cmp/ge r6,r4
    .org 0x763aa-ORIGIN
L_000763aa:
    bt/s L_000763b0
    .org 0x763ac-ORIGIN
L_000763ac:
    mov r4,r5
    .org 0x763ae-ORIGIN
L_000763ae:
    exts.w r6,r5
    .org 0x763b0-ORIGIN
L_000763b0:
    mov.w P_00076448,r0
    .org 0x763b2-ORIGIN
L_000763b2:
    rts
    .org 0x763b4-ORIGIN
L_000763b4:
    mov.w r5,@(r0,r7)
    .org 0x76448-ORIGIN
P_00076448:
    .byte 0x03
    .org 0x76449-ORIGIN
P_00076449:
    .byte 0xac
    .org 0x7644a-ORIGIN
P_0007644a:
    .byte 0x0c
    .org 0x7644b-ORIGIN
P_0007644b:
    .byte 0x26
    .org 0x76454-ORIGIN
P_00076454:
    .byte 0xff
    .org 0x76455-ORIGIN
P_00076455:
    .byte 0xff
    .org 0x76456-ORIGIN
P_00076456:
    .byte 0x39
    .org 0x76457-ORIGIN
P_00076457:
    .byte 0xc4
    .org 0x76470-ORIGIN
P_00076470:
    .byte 0xff
    .org 0x76471-ORIGIN
P_00076471:
    .byte 0xff
    .org 0x76472-ORIGIN
P_00076472:
    .byte 0x28
    .org 0x76473-ORIGIN
P_00076473:
    .byte 0xf8
    .org 0x76474-ORIGIN
P_00076474:
    .byte 0x00
    .org 0x76475-ORIGIN
P_00076475:
    .byte 0x00
    .org 0x76476-ORIGIN
P_00076476:
    .byte 0x90
    .org 0x76477-ORIGIN
P_00076477:
    .byte 0xa6
    .org 0xcb1ca-ORIGIN
L_000cb1ca:
    mov.l P_000cb220,r2
    .org 0xcb1cc-ORIGIN
L_000cb1cc:
    extu.b r4,r5
    .org 0xcb1ce-ORIGIN
L_000cb1ce:
    shll r5
    .org 0xcb1d0-ORIGIN
L_000cb1d0:
    add #0x24,r2
    .org 0xcb1d2-ORIGIN
L_000cb1d2:
    mov r5,r0
    .org 0xcb1d4-ORIGIN
L_000cb1d4:
    mov.w @(r0,r2),r6
    .org 0xcb1d6-ORIGIN
L_000cb1d6:
    mov #0x20,r3
    .org 0xcb1d8-ORIGIN
L_000cb1d8:
    shll8 r3
    .org 0xcb1da-ORIGIN
L_000cb1da:
    extu.w r6,r2
    .org 0xcb1dc-ORIGIN
L_000cb1dc:
    shll2 r2
    .org 0xcb1de-ORIGIN
L_000cb1de:
    shll2 r2
    .org 0xcb1e0-ORIGIN
L_000cb1e0:
    mov #-0x1,r6
    .org 0xcb1e2-ORIGIN
L_000cb1e2:
    add r3,r2
    .org 0xcb1e4-ORIGIN
L_000cb1e4:
    extu.w r6,r6
    .org 0xcb1e6-ORIGIN
L_000cb1e6:
    cmp/hi r6,r2
    .org 0xcb1e8-ORIGIN
L_000cb1e8:
    bt L_000cb1ec
    .org 0xcb1ea-ORIGIN
L_000cb1ea:
    mov r2,r6
    .org 0xcb1ec-ORIGIN
L_000cb1ec:
    mov.l P_000cb20c,r2
    .org 0xcb1ee-ORIGIN
L_000cb1ee:
    mov r5,r0
    .org 0xcb1f0-ORIGIN
L_000cb1f0:
    mov.w P_000cb1fa,r3
    .org 0xcb1f2-ORIGIN
L_000cb1f2:
    add r3,r2
    .org 0xcb1f4-ORIGIN
L_000cb1f4:
    rts
    .org 0xcb1f6-ORIGIN
L_000cb1f6:
    mov.w r6,@(r0,r2)
    .org 0xcb1fa-ORIGIN
P_000cb1fa:
    .byte 0x01
    .org 0xcb1fb-ORIGIN
P_000cb1fb:
    .byte 0xa2
    .org 0xcb20c-ORIGIN
P_000cb20c:
    .byte 0xff
    .org 0xcb20d-ORIGIN
P_000cb20d:
    .byte 0xff
    .org 0xcb20e-ORIGIN
P_000cb20e:
    .byte 0x36
    .org 0xcb20f-ORIGIN
P_000cb20f:
    .byte 0xd8
    .org 0xcb220-ORIGIN
P_000cb220:
    .byte 0xff
    .org 0xcb221-ORIGIN
P_000cb221:
    .byte 0xff
    .org 0xcb222-ORIGIN
P_000cb222:
    .byte 0x28
    .org 0xcb223-ORIGIN
P_000cb223:
    .byte 0x98
