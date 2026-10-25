! Bounded coherent snapshot caller and natural helper path.
! Separate ELF per caller keeps every observation boundary outside tested bytes.
    .text
    .balign 4
    .org 0x2131c - 0x2131c
L_0002131c:
    mov.l L_000213a8,r6
    .org 0x2131e - 0x2131c
L_0002131e:
    mov.l L_000213ac,r1
    .org 0x21320 - 0x2131c
L_00021320:
    mov.w @r6,r2
    .org 0x21322 - 0x2131c
L_00021322:
    mov.l L_000213b0,r6
    .org 0x21324 - 0x2131c
L_00021324:
    mov.w r2,@r6
    .org 0x21326 - 0x2131c
L_00021326:
    mov.l L_000213b4,r6
    .org 0x21328 - 0x2131c
L_00021328:
    mov.w r2,@r6
    .org 0x2132a - 0x2131c
L_0002132a:
    mov.l L_000213b8,r2
    .org 0x2132c - 0x2131c
L_0002132c:
    jsr @r9
    .org 0x2132e - 0x2131c
L_0002132e:
    mov #0x58,r0
    .org 0x213a8 - 0x2131c
L_000213a8:
    .long 0xffff40c6
    .org 0x213ac - 0x2131c
L_000213ac:
    .long 0xffff40cc
    .org 0x213b0 - 0x2131c
L_000213b0:
    .long 0xffff40c4
    .org 0x213b4 - 0x2131c
L_000213b4:
    .long 0xffff40c8
    .org 0x213b8 - 0x2131c
L_000213b8:
    .long 0xffff4124
    .org 0x22038 - 0x2131c
L_00022038:
    mov.l r3,@-r15
    .org 0x2203a - 0x2131c
L_0002203a:
    mov #0x40,r3
    .org 0x2203c - 0x2131c
L_0002203c:
    cmp/hs r0,r3
    .org 0x2203e - 0x2131c
L_0002203e:
    bf L_000220d8
    .org 0x220d8 - 0x2131c
L_000220d8:
    mov.l r2,@-r15
    .org 0x220da - 0x2131c
L_000220da:
    mov r2,r3
    .org 0x220dc - 0x2131c
L_000220dc:
    add r0,r3
    .org 0x220de - 0x2131c
L_000220de:
    mov.l @r2+,r0
    .org 0x220e0 - 0x2131c
L_000220e0:
    cmp/hs r2,r3
    .org 0x220e2 - 0x2131c
L_000220e2:
    bf L_000220f2
    .org 0x220e4 - 0x2131c
L_000220e4:
    mov.l r0,@r1
    .org 0x220e6 - 0x2131c
L_000220e6:
    mov.l @r2+,r0
    .org 0x220e8 - 0x2131c
L_000220e8:
    cmp/hs r2,r3
    .org 0x220ea - 0x2131c
L_000220ea:
    bf L_000220f2
    .org 0x220ec - 0x2131c
L_000220ec:
    mov.l r0,@(0x4,r1)
    .org 0x220ee - 0x2131c
L_000220ee:
    bra L_000220de
    .org 0x220f0 - 0x2131c
L_000220f0:
    add #0x8,r1
    .org 0x220f2 - 0x2131c
L_000220f2:
    mov.l @r15+,r2
    .org 0x220f4 - 0x2131c
L_000220f4:
    rts
    .org 0x220f6 - 0x2131c
L_000220f6:
    mov.l @r15+,r3
