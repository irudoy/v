! Bounded coherent snapshot caller and natural helper path.
! Separate ELF per caller keeps every observation boundary outside tested bytes.
    .text
    .balign 4
    .org 0x20f04 - 0x20f04
L_00020f04:
    mov.l L_0002110c,r4
    .org 0x20f06 - 0x20f04
L_00020f06:
    mov.l L_00021110,r6
    .org 0x20f08 - 0x20f04
L_00020f08:
    mov.w @r4,r2
    .org 0x20f0a - 0x20f04
L_00020f0a:
    mov.l L_00021114,r1
    .org 0x20f0c - 0x20f04
L_00020f0c:
    mov.w r2,@r6
    .org 0x20f0e - 0x20f04
L_00020f0e:
    mov.l L_00021118,r6
    .org 0x20f10 - 0x20f04
L_00020f10:
    mov.w @r6,r2
    .org 0x20f12 - 0x20f04
L_00020f12:
    mov.l L_0002111c,r6
    .org 0x20f14 - 0x20f04
L_00020f14:
    mov.w r2,@r4
    .org 0x20f16 - 0x20f04
L_00020f16:
    mov.l L_00021120,r2
    .org 0x20f18 - 0x20f04
L_00020f18:
    jsr @r6
    .org 0x20f1a - 0x20f04
L_00020f1a:
    mov #0x1c,r0
    .org 0x2110c - 0x20f04
L_0002110c:
    .long 0xffff1024
    .org 0x21110 - 0x20f04
L_00021110:
    .long 0xffff1028
    .org 0x21114 - 0x20f04
L_00021114:
    .long 0xffff102c
    .org 0x21118 - 0x20f04
L_00021118:
    .long 0xffff1026
    .org 0x2111c - 0x20f04
L_0002111c:
    .long 0x00022104
    .org 0x21120 - 0x20f04
L_00021120:
    .long 0xffff1048
    .org 0x22104 - 0x20f04
L_00022104:
    mov.l r3,@-r15
    .org 0x22106 - 0x20f04
L_00022106:
    mov.l L_00022110,r3
    .org 0x22108 - 0x20f04
L_00022108:
    mov.l @(r0,r3),r3
    .org 0x2210a - 0x20f04
L_0002210a:
    add #-0x4,r0
    .org 0x2210c - 0x20f04
L_0002210c:
    jmp @r3
    .org 0x2210e - 0x20f04
L_0002210e:
    mov.l @(r0,r2),r3
    .org 0x22110 - 0x20f04
L_00022110:
    .long 0x00022158
    .org 0x2213a - 0x20f04
L_0002213a:
    mov.l @(20,r2),r0
    .org 0x2213c - 0x20f04
L_0002213c:
    mov.l r3,@(24,r1)
    .org 0x2213e - 0x20f04
L_0002213e:
    mov.l @(16,r2),r3
    .org 0x22140 - 0x20f04
L_00022140:
    mov.l r0,@(20,r1)
    .org 0x22142 - 0x20f04
L_00022142:
    mov.l @(12,r2),r0
    .org 0x22144 - 0x20f04
L_00022144:
    mov.l r3,@(16,r1)
    .org 0x22146 - 0x20f04
L_00022146:
    mov.l @(8,r2),r3
    .org 0x22148 - 0x20f04
L_00022148:
    mov.l r0,@(12,r1)
    .org 0x2214a - 0x20f04
L_0002214a:
    mov.l @(4,r2),r0
    .org 0x2214c - 0x20f04
L_0002214c:
    mov.l r3,@(8,r1)
    .org 0x2214e - 0x20f04
L_0002214e:
    mov.l @r2,r3
    .org 0x22150 - 0x20f04
L_00022150:
    mov.l r0,@(4,r1)
    .org 0x22152 - 0x20f04
L_00022152:
    mov.l r3,@r1
    .org 0x22154 - 0x20f04
L_00022154:
    rts
    .org 0x22156 - 0x20f04
L_00022156:
    mov.l @r15+,r3
    .org 0x22174 - 0x20f04
L_00022174:
    .long 0x0002213a
