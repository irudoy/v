! Bounded coherent snapshot caller and natural helper path.
! Separate ELF per caller keeps every observation boundary outside tested bytes.
    .text
    .balign 4
    .org 0x20f1c - 0x20f1c
L_00020f1c:
    mov.l L_00021124,r4
    .org 0x20f1e - 0x20f1c
L_00020f1e:
    mov.l L_00021128,r6
    .org 0x20f20 - 0x20f1c
L_00020f20:
    mov.b @r4,r2
    .org 0x20f22 - 0x20f1c
L_00020f22:
    mov.b @(0x1,r4),r0
    .org 0x20f24 - 0x20f1c
L_00020f24:
    mov.b r2,@r6
    .org 0x20f26 - 0x20f1c
L_00020f26:
    mov.b r0,@(0x1,r6)
    .org 0x20f28 - 0x20f1c
L_00020f28:
    mov.l L_0002112c,r6
    .org 0x20f2a - 0x20f1c
L_00020f2a:
    mov.l L_00021130,r1
    .org 0x20f2c - 0x20f1c
L_00020f2c:
    mov.b @r6,r2
    .org 0x20f2e - 0x20f1c
L_00020f2e:
    mov.b @(0x1,r6),r0
    .org 0x20f30 - 0x20f1c
L_00020f30:
    mov.b r2,@r4
    .org 0x20f32 - 0x20f1c
L_00020f32:
    mov.l L_00021134,r2
    .org 0x20f34 - 0x20f1c
L_00020f34:
    mov.b r0,@(0x1,r4)
    .org 0x20f36 - 0x20f1c
L_00020f36:
    jsr @r11
    .org 0x20f38 - 0x20f1c
L_00020f38:
    mov #0x8,r0
    .org 0x21124 - 0x20f1c
L_00021124:
    .long 0xffff1064
    .org 0x21128 - 0x20f1c
L_00021128:
    .long 0xffff1068
    .org 0x2112c - 0x20f1c
L_0002112c:
    .long 0xffff1066
    .org 0x21130 - 0x20f1c
L_00021130:
    .long 0xffff106a
    .org 0x21134 - 0x20f1c
L_00021134:
    .long 0xffff1072
    .org 0x22558 - 0x20f1c
L_00022558:
    mov.l r2,@-r15
    .org 0x2255a - 0x20f1c
L_0002255a:
    mov.l r3,@-r15
    .org 0x2255c - 0x20f1c
L_0002255c:
    mov.l r4,@-r15
    .org 0x2255e - 0x20f1c
L_0002255e:
    cmp/eq #0,r0
    .org 0x22560 - 0x20f1c
L_00022560:
    bt L_00022588
    .org 0x22562 - 0x20f1c
L_00022562:
    mov r2,r4
    .org 0x22564 - 0x20f1c
L_00022564:
    add r0,r4
    .org 0x22566 - 0x20f1c
L_00022566:
    mov.b @r2+,r0
    .org 0x22568 - 0x20f1c
L_00022568:
    mov.b r0,@r1
    .org 0x2256a - 0x20f1c
L_0002256a:
    cmp/hi r2,r4
    .org 0x2256c - 0x20f1c
L_0002256c:
    bf L_00022588
    .org 0x2256e - 0x20f1c
L_0002256e:
    mov.b @r2+,r0
    .org 0x22570 - 0x20f1c
L_00022570:
    mov.b r0,@(1,r1)
    .org 0x22572 - 0x20f1c
L_00022572:
    cmp/hi r2,r4
    .org 0x22574 - 0x20f1c
L_00022574:
    bf L_00022588
    .org 0x22576 - 0x20f1c
L_00022576:
    mov.b @r2+,r0
    .org 0x22578 - 0x20f1c
L_00022578:
    mov.b r0,@(2,r1)
    .org 0x2257a - 0x20f1c
L_0002257a:
    cmp/hi r2,r4
    .org 0x2257c - 0x20f1c
L_0002257c:
    bf L_00022588
    .org 0x2257e - 0x20f1c
L_0002257e:
    mov.b @r2+,r0
    .org 0x22580 - 0x20f1c
L_00022580:
    mov.b r0,@(3,r1)
    .org 0x22582 - 0x20f1c
L_00022582:
    cmp/hi r2,r4
    .org 0x22584 - 0x20f1c
L_00022584:
    add #4,r1
    .org 0x22586 - 0x20f1c
L_00022586:
    bt L_00022566
    .org 0x22588 - 0x20f1c
L_00022588:
    mov.l @r15+,r4
    .org 0x2258a - 0x20f1c
L_0002258a:
    mov.l @r15+,r3
    .org 0x2258c - 0x20f1c
L_0002258c:
    rts
    .org 0x2258e - 0x20f1c
L_0002258e:
    mov.l @r15+,r2
