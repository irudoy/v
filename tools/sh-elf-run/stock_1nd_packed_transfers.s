! Independent reconstruction of bounded packed-field transfers.
! Both CVTC copies belong to the same straight-line instruction window.
! The mask window executes the exact natural callee after loading R10.
    .text
    .balign 4
    .set ORIGIN,0x21318
    mov.l L_21578,r11
    mov.l L_2157c,r2
    mov.w @r11,r0
    mov.l @r2,r14
    mov.l @(12,r2),r1
    mov.l @(28,r2),r7
    mov.l @(32,r2),r8
    mov.l @(44,r2),r9
    mov.w r0,@(4,r11)
    mov.w @(2,r11),r0
    mov.l @(4,r2),r13
    mov.l r14,@(8,r11)
    .org 0x21368-ORIGIN
    mov.l L_2158c,r10
    jsr @r7
    mov #60,r0
    mov.w @r10,r0
    mov #2,r5
    mov.w r0,@(12,r10)
    mov.w @(2,r10),r0
    shll8 r5
    mov.w r0,@(14,r10)
    mov.w @(4,r10),r0
    add #124,r5
    mov.w r0,@(16,r10)
    .org 0x21578-ORIGIN
L_21578: .long 0xfffe818c
L_2157c: .long 0xfffe81cc
    .org 0x2158c-ORIGIN
L_2158c: .long 0xfffe92e0
    .org 0x21722-ORIGIN
    mov.l L_21940,r1
    mov.w @(8,r1),r0
    mov #-100,r12
    mov.w r0,@(2,r1)
    mov.w @(10,r1),r0
    extu.b r12,r12
    mov.w r0,@(4,r1)
    mov.w @(12,r1),r0
    mov.l L_21944,r13
    mov.w r0,@(6,r1)
    mov.w @(8,r1),r0
    stc gbr,r2
    mov.w r0,@(14,r1)
    mov.w @(10,r1),r0
    mov.w r0,@(16,r1)
    .org 0x21940-ORIGIN
L_21940: .long 0xfffe931c
L_21944: .long 0x00022870
    .org 0x22870-ORIGIN
copy_callee:
    mov.l r2,@-r15
    mov.l r3,@-r15
    mov.l r4,@-r15
    cmp/eq #0,r0
    bt copy_return
    mov r2,r4
    add r0,r4
copy_loop:
    mov.b @r2+,r0
    mov.b r0,@r1
    cmp/hi r2,r4
    bf copy_return
    mov.b @r2+,r0
    mov.b r0,@(1,r1)
    cmp/hi r2,r4
    bf copy_return
    mov.b @r2+,r0
    mov.b r0,@(2,r1)
    cmp/hi r2,r4
    bf copy_return
    mov.b @r2+,r0
    mov.b r0,@(3,r1)
    cmp/hi r2,r4
    add #4,r1
    bt copy_loop
copy_return:
    mov.l @r15+,r4
    mov.l @r15+,r3
    rts
    mov.l @r15+,r2
