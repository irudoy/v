! Bounded coherent snapshot caller and natural helper path.
! Separate ELF per caller keeps every observation boundary outside tested bytes.
    .text
    .balign 4
    .org 0x20f5a - 0x20f58
L_00020f5a:
    mov.l L_0002114c,r4
    .org 0x20f5c - 0x20f58
L_00020f5c:
    mov.l L_00021150,r6
    .org 0x20f5e - 0x20f58
L_00020f5e:
    mov.w @r4,r2
    .org 0x20f60 - 0x20f58
L_00020f60:
    mov.l L_00021154,r1
    .org 0x20f62 - 0x20f58
L_00020f62:
    mov.w r2,@r6
    .org 0x20f64 - 0x20f58
L_00020f64:
    mov.l L_00021158,r6
    .org 0x20f66 - 0x20f58
L_00020f66:
    mov.w @r6,r2
    .org 0x20f68 - 0x20f58
L_00020f68:
    mov.w r2,@r4
    .org 0x20f6a - 0x20f58
L_00020f6a:
    mov.l L_0002115c,r2
    .org 0x20f6c - 0x20f58
L_00020f6c:
    jsr @r14
    .org 0x20f6e - 0x20f58
L_00020f6e:
    mov #0x38,r0
    .org 0x2114c - 0x20f58
L_0002114c:
    .long 0xffff1194
    .org 0x21150 - 0x20f58
L_00021150:
    .long 0xffff1198
    .org 0x21154 - 0x20f58
L_00021154:
    .long 0xffff119c
    .org 0x21158 - 0x20f58
L_00021158:
    .long 0xffff1196
    .org 0x2115c - 0x20f58
L_0002115c:
    .long 0xffff11d4
    .org 0x220f8 - 0x20f58
L_000220f8:
    mov.l r3,@-r15
    .org 0x220fa - 0x20f58
L_000220fa:
    mov.l L_00022110,r3
    .org 0x220fc - 0x20f58
L_000220fc:
    mov.l @(r0,r3),r3
    .org 0x220fe - 0x20f58
L_000220fe:
    add #-0x4,r0
    .org 0x22100 - 0x20f58
L_00022100:
    jmp @r3
    .org 0x22102 - 0x20f58
L_00022102:
    mov.l @(r0,r2),r0
    .org 0x22110 - 0x20f58
L_00022110:
    .long 0x00022158
    .org 0x2211e - 0x20f58
L_0002211e:
    mov.l @(48,r2),r3
    .org 0x22120 - 0x20f58
L_00022120:
    mov.l r0,@(52,r1)
    .org 0x22122 - 0x20f58
L_00022122:
    mov.l @(44,r2),r0
    .org 0x22124 - 0x20f58
L_00022124:
    mov.l r3,@(48,r1)
    .org 0x22126 - 0x20f58
L_00022126:
    mov.l @(40,r2),r3
    .org 0x22128 - 0x20f58
L_00022128:
    mov.l r0,@(44,r1)
    .org 0x2212a - 0x20f58
L_0002212a:
    mov.l @(36,r2),r0
    .org 0x2212c - 0x20f58
L_0002212c:
    mov.l r3,@(40,r1)
    .org 0x2212e - 0x20f58
L_0002212e:
    mov.l @(32,r2),r3
    .org 0x22130 - 0x20f58
L_00022130:
    mov.l r0,@(36,r1)
    .org 0x22132 - 0x20f58
L_00022132:
    mov.l @(28,r2),r0
    .org 0x22134 - 0x20f58
L_00022134:
    mov.l r3,@(32,r1)
    .org 0x22136 - 0x20f58
L_00022136:
    mov.l @(24,r2),r3
    .org 0x22138 - 0x20f58
L_00022138:
    mov.l r0,@(28,r1)
    .org 0x2213a - 0x20f58
L_0002213a:
    mov.l @(20,r2),r0
    .org 0x2213c - 0x20f58
L_0002213c:
    mov.l r3,@(24,r1)
    .org 0x2213e - 0x20f58
L_0002213e:
    mov.l @(16,r2),r3
    .org 0x22140 - 0x20f58
L_00022140:
    mov.l r0,@(20,r1)
    .org 0x22142 - 0x20f58
L_00022142:
    mov.l @(12,r2),r0
    .org 0x22144 - 0x20f58
L_00022144:
    mov.l r3,@(16,r1)
    .org 0x22146 - 0x20f58
L_00022146:
    mov.l @(8,r2),r3
    .org 0x22148 - 0x20f58
L_00022148:
    mov.l r0,@(12,r1)
    .org 0x2214a - 0x20f58
L_0002214a:
    mov.l @(4,r2),r0
    .org 0x2214c - 0x20f58
L_0002214c:
    mov.l r3,@(8,r1)
    .org 0x2214e - 0x20f58
L_0002214e:
    mov.l @r2,r3
    .org 0x22150 - 0x20f58
L_00022150:
    mov.l r0,@(4,r1)
    .org 0x22152 - 0x20f58
L_00022152:
    mov.l r3,@r1
    .org 0x22154 - 0x20f58
L_00022154:
    rts
    .org 0x22156 - 0x20f58
L_00022156:
    mov.l @r15+,r3
    .org 0x22190 - 0x20f58
L_00022190:
    .long 0x0002211e
