! Bounded coherent snapshot caller and natural helper path.
! Separate ELF per caller keeps every observation boundary outside tested bytes.
    .text
    .balign 4
    .org 0x2104e - 0x2104c
L_0002104e:
    mov.l L_00021218,r6
    .org 0x21050 - 0x2104c
L_00021050:
    mov.l L_0002121c,r1
    .org 0x21052 - 0x2104c
L_00021052:
    mov.b @r6,r2
    .org 0x21054 - 0x2104c
L_00021054:
    mov.l L_00021220,r6
    .org 0x21056 - 0x2104c
L_00021056:
    mov.b r2,@r6
    .org 0x21058 - 0x2104c
L_00021058:
    mov.l L_00021224,r2
    .org 0x2105a - 0x2104c
L_0002105a:
    jsr @r11
    .org 0x2105c - 0x2104c
L_0002105c:
    mov #0x3,r0
    .org 0x21218 - 0x2104c
L_00021218:
    .long 0xffff2465
    .org 0x2121c - 0x2104c
L_0002121c:
    .long 0xffff246d
    .org 0x21220 - 0x2104c
L_00021220:
    .long 0xffff2464
    .org 0x21224 - 0x2104c
L_00021224:
    .long 0xffff246a
    .org 0x22558 - 0x2104c
L_00022558:
    mov.l r2,@-r15
    .org 0x2255a - 0x2104c
L_0002255a:
    mov.l r3,@-r15
    .org 0x2255c - 0x2104c
L_0002255c:
    mov.l r4,@-r15
    .org 0x2255e - 0x2104c
L_0002255e:
    cmp/eq #0,r0
    .org 0x22560 - 0x2104c
L_00022560:
    bt L_00022588
    .org 0x22562 - 0x2104c
L_00022562:
    mov r2,r4
    .org 0x22564 - 0x2104c
L_00022564:
    add r0,r4
    .org 0x22566 - 0x2104c
L_00022566:
    mov.b @r2+,r0
    .org 0x22568 - 0x2104c
L_00022568:
    mov.b r0,@r1
    .org 0x2256a - 0x2104c
L_0002256a:
    cmp/hi r2,r4
    .org 0x2256c - 0x2104c
L_0002256c:
    bf L_00022588
    .org 0x2256e - 0x2104c
L_0002256e:
    mov.b @r2+,r0
    .org 0x22570 - 0x2104c
L_00022570:
    mov.b r0,@(1,r1)
    .org 0x22572 - 0x2104c
L_00022572:
    cmp/hi r2,r4
    .org 0x22574 - 0x2104c
L_00022574:
    bf L_00022588
    .org 0x22576 - 0x2104c
L_00022576:
    mov.b @r2+,r0
    .org 0x22578 - 0x2104c
L_00022578:
    mov.b r0,@(2,r1)
    .org 0x2257a - 0x2104c
L_0002257a:
    cmp/hi r2,r4
    .org 0x2257c - 0x2104c
L_0002257c:
    bf L_00022588
    .org 0x2257e - 0x2104c
L_0002257e:
    mov.b @r2+,r0
    .org 0x22580 - 0x2104c
L_00022580:
    mov.b r0,@(3,r1)
    .org 0x22582 - 0x2104c
L_00022582:
    cmp/hi r2,r4
    .org 0x22584 - 0x2104c
L_00022584:
    add #4,r1
    .org 0x22586 - 0x2104c
L_00022586:
    bt L_00022566
    .org 0x22588 - 0x2104c
L_00022588:
    mov.l @r15+,r4
    .org 0x2258a - 0x2104c
L_0002258a:
    mov.l @r15+,r3
    .org 0x2258c - 0x2104c
L_0002258c:
    rts
    .org 0x2258e - 0x2104c
L_0002258e:
    mov.l @r15+,r2
