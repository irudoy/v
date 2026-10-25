! Bounded stock longword clear loops and their exact ROM range descriptors.
    .text
    .balign 4
L_00022604:
    .long 0xffff261c
    .long 0xffff4512
    .org 0x22614 - 0x22604
L_00022614:
    .long 0xffff1000
    .long 0xffff261a
    .org 0x22624 - 0x22604
L_00022624:
    .long 0xffff4514
    .org 0x22628 - 0x22604
L_00022628:
    .long 0xffff5cf2
    .org 0x26f30 - 0x22604
L_00026f30:
    mov.l L_00026f9c,r1
    mov.l @r1,r0
    mov r0,r2
    mov.l @(0x4,r1),r0
    cmp/hs r0,r2
    bt L_00026f48
    mov #0,r6
L_00026f3e:
    mov.l r6,@r2
    add #4,r2
    mov.l @(0x4,r1),r0
    cmp/hs r0,r2
    bf L_00026f3e
L_00026f48:
    rts
    nop
    .org 0x26f9c - 0x22604
L_00026f9c:
    .long 0x00022624
    .org 0x27ae4 - 0x22604
L_00027ae4:
    mov.l @(0x10,gbr),r0
    mov r0,r2
    mov.l @(0x14,gbr),r0
    cmp/hs r0,r2
    bt L_00027afa
    mov #0,r5
L_00027af0:
    mov.l r5,@r2
    add #4,r2
    mov.l @(0x14,gbr),r0
    cmp/hs r0,r2
    bf L_00027af0
L_00027afa:
    .org 0x27c6e - 0x22604
L_00027c6e:
    mov.l @(0x8,gbr),r0
    mov r0,r2
    mov.l @(0xc,gbr),r0
    cmp/hs r0,r2
    bt L_00027c84
    mov #0,r6
L_00027c7a:
    mov.l r6,@r2
    add #4,r2
    mov.l @(0xc,gbr),r0
    cmp/hs r0,r2
    bf L_00027c7a
L_00027c84:
    .org 0x2fc8a - 0x22604
L_0002fc8a:
    mov.l @(0x8,gbr),r0
    mov r0,r2
    mov.l r0,@r15
    mov.l @(0x1c,gbr),r0
    cmp/hs r0,r2
    bt L_0002fca4
    mov #0,r6
L_0002fc98:
    mov.l r6,@r2
    add #4,r2
    mov.l @(0x1c,gbr),r0
    cmp/hs r0,r2
    bf/s L_0002fc98
    mov.l r2,@r15
L_0002fca4:
    .org 0x34bf4 - 0x22604
L_00034bf4:
    mov.l L_00034da0,r14
    mov.l @(0x20,r14),r2
    mov.l @(0x34,r14),r6
    cmp/hs r6,r2
    bt/s L_00034c10
    mov.l r2,@(0xc,r15)
    mov #0,r11
L_00034c02:
    mov.l L_00034da0,r3
    mov.l r11,@r2
    add #4,r2
    mov.l @(0x34,r3),r6
    cmp/hs r6,r2
    bf/s L_00034c02
    mov.l r2,@(0xc,r15)
L_00034c10:
    .org 0x34da0 - 0x22604
L_00034da0:
    .long 0x000225f4
