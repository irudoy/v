! Bounded scheduler copy call with explicit entry registers.
! The GNU gate binds all caller, helper and dispatch bytes to the owned stock image.
    .text
    .balign 4
    .org 0x20bce - 0x20bcc
L_00020bce:
    mov.l L_00020e40,r2
    .org 0x20bd0 - 0x20bcc
L_00020bd0:
    jsr @r9
    .org 0x20bd2 - 0x20bcc
L_00020bd2:
    mov #0x18,r0
    .org 0x20e40 - 0x20bcc
L_00020e40:
    .long 0xffff1dec
    .org 0x220f8 - 0x20bcc
L_000220f8:
    mov.l r3,@-r15
    .org 0x220fa - 0x20bcc
L_000220fa:
    mov.l L_00022110,r3
    .org 0x220fc - 0x20bcc
L_000220fc:
    mov.l @(r0,r3),r3
    .org 0x220fe - 0x20bcc
L_000220fe:
    add #-0x4,r0
    .org 0x22100 - 0x20bcc
L_00022100:
    jmp @r3
    .org 0x22102 - 0x20bcc
L_00022102:
    mov.l @(r0,r2),r0
    .org 0x22110 - 0x20bcc
L_00022110:
    .long 0x00022158
    .org 0x2211e - 0x20bcc
L_0002211e:
    mov.l @(0x30,r2),r3
    .org 0x22120 - 0x20bcc
L_00022120:
    mov.l r0,@(0x34,r1)
    .org 0x22122 - 0x20bcc
L_00022122:
    mov.l @(0x2c,r2),r0
    .org 0x22124 - 0x20bcc
L_00022124:
    mov.l r3,@(0x30,r1)
    .org 0x22126 - 0x20bcc
L_00022126:
    mov.l @(0x28,r2),r3
    .org 0x22128 - 0x20bcc
L_00022128:
    mov.l r0,@(0x2c,r1)
    .org 0x2212a - 0x20bcc
L_0002212a:
    mov.l @(0x24,r2),r0
    .org 0x2212c - 0x20bcc
L_0002212c:
    mov.l r3,@(0x28,r1)
    .org 0x2212e - 0x20bcc
L_0002212e:
    mov.l @(0x20,r2),r3
    .org 0x22130 - 0x20bcc
L_00022130:
    mov.l r0,@(0x24,r1)
    .org 0x22132 - 0x20bcc
L_00022132:
    mov.l @(0x1c,r2),r0
    .org 0x22134 - 0x20bcc
L_00022134:
    mov.l r3,@(0x20,r1)
    .org 0x22136 - 0x20bcc
L_00022136:
    mov.l @(0x18,r2),r3
    .org 0x22138 - 0x20bcc
L_00022138:
    mov.l r0,@(0x1c,r1)
    .org 0x2213a - 0x20bcc
L_0002213a:
    mov.l @(0x14,r2),r0
    .org 0x2213c - 0x20bcc
L_0002213c:
    mov.l r3,@(0x18,r1)
    .org 0x2213e - 0x20bcc
L_0002213e:
    mov.l @(0x10,r2),r3
    .org 0x22140 - 0x20bcc
L_00022140:
    mov.l r0,@(0x14,r1)
    .org 0x22142 - 0x20bcc
L_00022142:
    mov.l @(0xc,r2),r0
    .org 0x22144 - 0x20bcc
L_00022144:
    mov.l r3,@(0x10,r1)
    .org 0x22146 - 0x20bcc
L_00022146:
    mov.l @(0x8,r2),r3
    .org 0x22148 - 0x20bcc
L_00022148:
    mov.l r0,@(0xc,r1)
    .org 0x2214a - 0x20bcc
L_0002214a:
    mov.l @(0x4,r2),r0
    .org 0x2214c - 0x20bcc
L_0002214c:
    mov.l r3,@(0x8,r1)
    .org 0x2214e - 0x20bcc
L_0002214e:
    mov.l @r2,r3
    .org 0x22150 - 0x20bcc
L_00022150:
    mov.l r0,@(0x4,r1)
    .org 0x22152 - 0x20bcc
L_00022152:
    mov.l r3,@r1
    .org 0x22154 - 0x20bcc
L_00022154:
    rts
    .org 0x22156 - 0x20bcc
L_00022156:
    mov.l @r15+,r3
    .org 0x22170 - 0x20bcc
L_00022170:
    .long L_0002213e
