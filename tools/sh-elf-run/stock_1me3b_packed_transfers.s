! Independent reconstruction of bounded packed-field transfers.
! The mask window executes its R10 literal load, natural copy callee and
! subsequent wide accesses with explicit incoming R1/R2/R7.
    .text
    .balign 4
    .set ORIGIN,0x2133c
    .org 0x2133e-ORIGIN
    mov.l L_21560,r4
    mov.l L_21564,r2
    mov.w @r4,r0
    mov.l @r2,r9
    mov.l @(12,r2),r10
    mov.l @(20,r2),r11
    mov.l @(28,r2),r13
    mov.l @(36,r2),r14
    mov.l @(44,r2),r1
    mov.w r0,@(4,r4)
    mov.w @(2,r4),r0
    mov.l @(4,r2),r8
    mov.l r9,@(8,r4)
    .org 0x2138e-ORIGIN
    mov.l L_21574,r10
    jsr @r7
    mov #56,r0
    mov.w @r10,r0
    mov #3,r13
    mov.w r0,@(12,r10)
    mov.w @(2,r10),r0
    shll8 r13
    mov.w r0,@(14,r10)
    mov.w @(4,r10),r0
    add #-124,r13
    mov.w r0,@(16,r10)
    .org 0x21560-ORIGIN
L_21560: .long 0xfffe8174
L_21564: .long 0xfffe81b4
    .org 0x21574-ORIGIN
L_21574: .long 0xfffe92ac
    .org 0x21776-ORIGIN
    mov.l L_219a8,r1
    mov #-100,r12
    mov.w @(8,r1),r0
    extu.b r12,r12
    mov r0,r13
    mov.w r0,@r1
    mov.w @(10,r1),r0
    mov.l L_219ac,r6
    mov r0,r7
    mov.w r0,@(2,r1)
    mov.w @(12,r1),r0
    mov r0,r2
    mov.w r0,@(4,r1)
    .org 0x219a8-ORIGIN
L_219a8: .long 0xfffe92e8
L_219ac: .long 0x000228ec
    .org 0x228ec-ORIGIN
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
