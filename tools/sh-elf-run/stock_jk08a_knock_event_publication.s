! Base anchors are byte-bound context evidence, not executed paths.
    .section .text
    .balign 4
L_publication_gbr_anchor:
    mov.l P_4dba0,r0
    ldc r0,gbr
    .org 0x4d9c2 - 0x4d9a8
L_publication_r14_anchor:
    mov.l P_4dbac,r14
    .org 0x4da7c - 0x4d9a8
L_publication_r13_anchor:
    mov.l P_4dbbc,r13

    .org 0x4db48 - 0x4d9a8
L_publication_entry:
    mov.w @(2,r14),r0
    mov r0,r4
    mov #0x48,r0
    mov.b @(r0,r13),r2
    add r4,r2
    mov r2,r0
    mov.l r0,@(4,gbr)
    mov #0x26,r0
    mov.b @(r0,r13),r5
    add r5,r2
    sub r6,r2
    mov r2,r6
    mov #-128,r2
    cmp/ge r2,r6
    bt/s L_publication_upper
    mov r6,r2
    mov #-128,r2
L_publication_upper:
    mov #127,r6
    cmp/gt r6,r2
    bf L_publication_store
    bra L_publication_store
    mov #127,r2
    .org 0x4db86 - 0x4d9a8
L_publication_store:
    mov r2,r6
    mov.l P_4dbe4,r2
    mov #0x4a,r0
    mov.b r6,@(r0,r2)
L_publication_boundary:

    .org 0x4dba0 - 0x4d9a8
P_4dba0: .long 0xffff1ff4
    .org 0x4dbac - 0x4d9a8
P_4dbac: .long 0xffff11d4
    .org 0x4dbbc - 0x4d9a8
P_4dbbc: .long 0xffff2330
    .org 0x4dbe4 - 0x4d9a8
P_4dbe4: .long 0xffff128c
