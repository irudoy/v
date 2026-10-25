! Bounded coherent snapshot caller and natural helper path.
! Separate ELF per caller keeps every observation boundary outside tested bytes.
    .text
    .balign 4
    .org 0x20fa4 - 0x20fa4
L_00020fa4:
    mov.l L_00021190,r4
    .org 0x20fa6 - 0x20fa4
L_00020fa6:
    mov.l L_00021194,r6
    .org 0x20fa8 - 0x20fa4
L_00020fa8:
    mov.b @r4,r2
    .org 0x20faa - 0x20fa4
L_00020faa:
    mov.b @(0x1,r4),r0
    .org 0x20fac - 0x20fa4
L_00020fac:
    mov.b r2,@r6
    .org 0x20fae - 0x20fa4
L_00020fae:
    mov.b r0,@(0x1,r6)
    .org 0x20fb0 - 0x20fa4
L_00020fb0:
    mov.l L_00021198,r6
    .org 0x20fb2 - 0x20fa4
L_00020fb2:
    mov.l L_0002119c,r1
    .org 0x20fb4 - 0x20fa4
L_00020fb4:
    mov.b @r6,r2
    .org 0x20fb6 - 0x20fa4
L_00020fb6:
    mov.b @(0x1,r6),r0
    .org 0x20fb8 - 0x20fa4
L_00020fb8:
    mov.l L_000211a0,r6
    .org 0x20fba - 0x20fa4
L_00020fba:
    mov.b r2,@r4
    .org 0x20fbc - 0x20fa4
L_00020fbc:
    mov.b r0,@(0x1,r4)
    .org 0x20fbe - 0x20fa4
L_00020fbe:
    mov.l L_000211a4,r4
    .org 0x20fc0 - 0x20fa4
L_00020fc0:
    mov.w @r6,r2
    .org 0x20fc2 - 0x20fa4
L_00020fc2:
    mov.w @(0x2,r6),r0
    .org 0x20fc4 - 0x20fa4
L_00020fc4:
    mov.w r2,@r4
    .org 0x20fc6 - 0x20fa4
L_00020fc6:
    mov.w r0,@(0x2,r4)
    .org 0x20fc8 - 0x20fa4
L_00020fc8:
    mov #0x41,r0
    .org 0x20fca - 0x20fa4
L_00020fca:
    mov.l L_000211a8,r2
    .org 0x20fcc - 0x20fa4
L_00020fcc:
    jsr @r11
    .org 0x20fce - 0x20fa4
L_00020fce:
    shll2 r0
    .org 0x21190 - 0x20fa4
L_00021190:
    .long 0xffff2668
    .org 0x21194 - 0x20fa4
L_00021194:
    .long 0xffff266c
    .org 0x21198 - 0x20fa4
L_00021198:
    .long 0xffff266a
    .org 0x2119c - 0x20fa4
L_0002119c:
    .long 0xffff267a
    .org 0x211a0 - 0x20fa4
L_000211a0:
    .long 0xffff2672
    .org 0x211a4 - 0x20fa4
L_000211a4:
    .long 0xffff266e
    .org 0x211a8 - 0x20fa4
L_000211a8:
    .long 0xffff277e
    .org 0x22558 - 0x20fa4
L_00022558:
    mov.l r2,@-r15
    .org 0x2255a - 0x20fa4
L_0002255a:
    mov.l r3,@-r15
    .org 0x2255c - 0x20fa4
L_0002255c:
    mov.l r4,@-r15
    .org 0x2255e - 0x20fa4
L_0002255e:
    cmp/eq #0,r0
    .org 0x22560 - 0x20fa4
L_00022560:
    bt L_00022588
    .org 0x22562 - 0x20fa4
L_00022562:
    mov r2,r4
    .org 0x22564 - 0x20fa4
L_00022564:
    add r0,r4
    .org 0x22566 - 0x20fa4
L_00022566:
    mov.b @r2+,r0
    .org 0x22568 - 0x20fa4
L_00022568:
    mov.b r0,@r1
    .org 0x2256a - 0x20fa4
L_0002256a:
    cmp/hi r2,r4
    .org 0x2256c - 0x20fa4
L_0002256c:
    bf L_00022588
    .org 0x2256e - 0x20fa4
L_0002256e:
    mov.b @r2+,r0
    .org 0x22570 - 0x20fa4
L_00022570:
    mov.b r0,@(1,r1)
    .org 0x22572 - 0x20fa4
L_00022572:
    cmp/hi r2,r4
    .org 0x22574 - 0x20fa4
L_00022574:
    bf L_00022588
    .org 0x22576 - 0x20fa4
L_00022576:
    mov.b @r2+,r0
    .org 0x22578 - 0x20fa4
L_00022578:
    mov.b r0,@(2,r1)
    .org 0x2257a - 0x20fa4
L_0002257a:
    cmp/hi r2,r4
    .org 0x2257c - 0x20fa4
L_0002257c:
    bf L_00022588
    .org 0x2257e - 0x20fa4
L_0002257e:
    mov.b @r2+,r0
    .org 0x22580 - 0x20fa4
L_00022580:
    mov.b r0,@(3,r1)
    .org 0x22582 - 0x20fa4
L_00022582:
    cmp/hi r2,r4
    .org 0x22584 - 0x20fa4
L_00022584:
    add #4,r1
    .org 0x22586 - 0x20fa4
L_00022586:
    bt L_00022566
    .org 0x22588 - 0x20fa4
L_00022588:
    mov.l @r15+,r4
    .org 0x2258a - 0x20fa4
L_0002258a:
    mov.l @r15+,r3
    .org 0x2258c - 0x20fa4
L_0002258c:
    rts
    .org 0x2258e - 0x20fa4
L_0002258e:
    mov.l @r15+,r2
