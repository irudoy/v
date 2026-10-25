! Bounded stock conditional counter arrays; exact word/byte loads and stores.
    .text
    .balign 4
    .org 0x205a6 - 0x205a4
L_000205a6:
    mov.l L_00020660,r5
L_000205a8:
    mov #-0x76,r4
L_000205aa:
    extu.b r4,r4
L_000205ac:
    mov r5,r2
L_000205ae:
    add r4,r2
L_000205b0:
    cmp/hs r2,r5
L_000205b2:
    bt/s L_000205ce
L_000205b4:
    mov r5,r6
L_000205b6:
    mov.b @r6,r2
L_000205b8:
    tst r2,r2
L_000205ba:
    bt L_000205c4
L_000205bc:
    mov.b @r6,r2
L_000205be:
    add #-0x1,r2
L_000205c0:
    extu.b r2,r2
L_000205c2:
    mov.b r2,@r6
L_000205c4:
    add #0x1,r6
L_000205c6:
    mov r5,r2
L_000205c8:
    add r4,r2
L_000205ca:
    cmp/hs r2,r6
L_000205cc:
    bf L_000205b6
L_000205ce:
    mov.l L_00020664,r5
L_000205d0:
    mov r5,r2
L_000205d2:
    add #0x14,r2
L_000205d4:
    cmp/hs r2,r5
L_000205d6:
    bt/s L_000205f2
L_000205d8:
    mov r5,r6
L_000205da:
    mov.w @r6,r2
L_000205dc:
    tst r2,r2
L_000205de:
    bt L_000205e8
L_000205e0:
    mov.w @r6,r2
L_000205e2:
    add #-0x1,r2
L_000205e4:
    extu.w r2,r2
L_000205e6:
    mov.w r2,@r6
L_000205e8:
    add #0x2,r6
L_000205ea:
    mov r5,r2
L_000205ec:
    add #0x14,r2
L_000205ee:
    cmp/hs r2,r6
L_000205f0:
    bf L_000205da
L_000205f2:
    mov.l L_00020668,r5
L_000205f4:
    mov #-0x3d,r4
L_000205f6:
    extu.b r4,r4
L_000205f8:
    mov r5,r2
L_000205fa:
    add r4,r2
L_000205fc:
    cmp/hs r2,r5
L_000205fe:
    bt/s L_0002061a
L_00020600:
    mov r5,r6
L_00020602:
    mov.b @r6,r2
L_00020604:
    tst r2,r2
L_00020606:
    bt L_00020610
L_00020608:
    mov.b @r6,r2
L_0002060a:
    add #-0x1,r2
L_0002060c:
    extu.b r2,r2
L_0002060e:
    mov.b r2,@r6
L_00020610:
    add #0x1,r6
L_00020612:
    mov r5,r2
L_00020614:
    add r4,r2
L_00020616:
    cmp/hs r2,r6
L_00020618:
    bf L_00020602
L_0002061a:
    .org 0x20660 - 0x205a4
L_00020660:
    .long 0xffff256a
    .org 0x20664 - 0x205a4
L_00020664:
    .long 0xffff2604
    .org 0x20668 - 0x205a4
L_00020668:
    .long 0xffff43c7
    .org 0x206a2 - 0x205a4
L_000206a2:
    mov.l L_000208e0,r5
L_000206a4:
    mov #-0xc,r4
L_000206a6:
    extu.b r4,r4
L_000206a8:
    mov r5,r2
L_000206aa:
    add r4,r2
L_000206ac:
    cmp/hs r2,r5
L_000206ae:
    bt/s L_000206ca
L_000206b0:
    mov r5,r6
L_000206b2:
    mov.b @r6,r2
L_000206b4:
    tst r2,r2
L_000206b6:
    bt L_000206c0
L_000206b8:
    mov.b @r6,r2
L_000206ba:
    add #-0x1,r2
L_000206bc:
    extu.b r2,r2
L_000206be:
    mov.b r2,@r6
L_000206c0:
    add #0x1,r6
L_000206c2:
    mov r5,r2
L_000206c4:
    add r4,r2
L_000206c6:
    cmp/hs r2,r6
L_000206c8:
    bf L_000206b2
L_000206ca:
    .org 0x208e0 - 0x205a4
L_000208e0:
    .long 0xffff42d3
    .org 0x2093e - 0x205a4
L_0002093e:
    mov.l L_00020b44,r5
    mov r5,r2
    add #7,r2
    cmp/hs r2,r5
    bt/s L_00020962
    mov r5,r6
L_0002094a:
    mov.b @r6,r2
    tst r2,r2
    bt L_00020958
    mov.b @r6,r2
    add #-1,r2
    extu.b r2,r2
    mov.b r2,@r6
L_00020958:
    add #1,r6
    mov r5,r2
    add #7,r2
    cmp/hs r2,r6
    bf L_0002094a
L_00020962:
    .org 0x20b44 - 0x205a4
L_00020b44:
    .long 0xffff25fb
