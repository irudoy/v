! Complete indexed channel target leaf with its original instruction bytes and literals.
    .text
    .balign 4
    .set ORIGIN,0xcb1c8
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
