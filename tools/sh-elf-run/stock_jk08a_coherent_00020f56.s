! Bounded coherent snapshot caller and natural helper path.
! Separate ELF per caller keeps every observation boundary outside tested bytes.
    .text
    .balign 4
    .org 0x20f3a - 0x20f38
L_00020f3a:
    mov.l L_00021138,r4
    .org 0x20f3c - 0x20f38
L_00020f3c:
    mov.l L_0002113c,r6
    .org 0x20f3e - 0x20f38
L_00020f3e:
    mov.w @r4,r2
    .org 0x20f40 - 0x20f38
L_00020f40:
    mov.w @(0x2,r4),r0
    .org 0x20f42 - 0x20f38
L_00020f42:
    mov.w r2,@r6
    .org 0x20f44 - 0x20f38
L_00020f44:
    mov.w r0,@(0x2,r6)
    .org 0x20f46 - 0x20f38
L_00020f46:
    mov.l L_00021140,r6
    .org 0x20f48 - 0x20f38
L_00020f48:
    mov.l L_00021144,r1
    .org 0x20f4a - 0x20f38
L_00020f4a:
    mov.w @r6,r2
    .org 0x20f4c - 0x20f38
L_00020f4c:
    mov.w @(0x2,r6),r0
    .org 0x20f4e - 0x20f38
L_00020f4e:
    mov.w r2,@r4
    .org 0x20f50 - 0x20f38
L_00020f50:
    mov.l L_00021148,r2
    .org 0x20f52 - 0x20f38
L_00020f52:
    mov.w r0,@(0x2,r4)
    .org 0x20f54 - 0x20f38
L_00020f54:
    mov r12,r0
    .org 0x20f56 - 0x20f38
L_00020f56:
    jsr @r9
    .org 0x20f58 - 0x20f38
L_00020f58:
    add #-0x70,r0
    .org 0x21138 - 0x20f38
L_00021138:
    .long 0xffff1082
    .org 0x2113c - 0x20f38
L_0002113c:
    .long 0xffff108a
    .org 0x21140 - 0x20f38
L_00021140:
    .long 0xffff1086
    .org 0x21144 - 0x20f38
L_00021144:
    .long 0xffff1094
    .org 0x21148 - 0x20f38
L_00021148:
    .long 0xffff1114
    .org 0x22038 - 0x20f38
L_00022038:
    mov.l r3,@-r15
    .org 0x2203a - 0x20f38
L_0002203a:
    mov #0x40,r3
    .org 0x2203c - 0x20f38
L_0002203c:
    cmp/hs r0,r3
    .org 0x2203e - 0x20f38
L_0002203e:
    bf L_000220d8
    .org 0x220d8 - 0x20f38
L_000220d8:
    mov.l r2,@-r15
    .org 0x220da - 0x20f38
L_000220da:
    mov r2,r3
    .org 0x220dc - 0x20f38
L_000220dc:
    add r0,r3
    .org 0x220de - 0x20f38
L_000220de:
    mov.l @r2+,r0
    .org 0x220e0 - 0x20f38
L_000220e0:
    cmp/hs r2,r3
    .org 0x220e2 - 0x20f38
L_000220e2:
    bf L_000220f2
    .org 0x220e4 - 0x20f38
L_000220e4:
    mov.l r0,@r1
    .org 0x220e6 - 0x20f38
L_000220e6:
    mov.l @r2+,r0
    .org 0x220e8 - 0x20f38
L_000220e8:
    cmp/hs r2,r3
    .org 0x220ea - 0x20f38
L_000220ea:
    bf L_000220f2
    .org 0x220ec - 0x20f38
L_000220ec:
    mov.l r0,@(0x4,r1)
    .org 0x220ee - 0x20f38
L_000220ee:
    bra L_000220de
    .org 0x220f0 - 0x20f38
L_000220f0:
    add #0x8,r1
    .org 0x220f2 - 0x20f38
L_000220f2:
    mov.l @r15+,r2
    .org 0x220f4 - 0x20f38
L_000220f4:
    rts
    .org 0x220f6 - 0x20f38
L_000220f6:
    mov.l @r15+,r3
