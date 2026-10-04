! Signed integration from separate natural arithmetic entries.
    .section .text
    .balign 4
    .org 0x8eaa - 0x8ea8
C_quiet: .word 13
    .org 0x8eae - 0x8ea8
C_event: .word 307

    .org 0x49544 - 0x8ea8
L_integration_quiet:
    mov.l P_49690,r10
    mov.l P_49694,r5
    mov.w @(12,r10),r0
    mov.w @r5,r2
    add r2,r0
    mov r0,r4
L_integration_clamp:
    mov #-128,r2
    shll8 r2
    not r2,r2
    cmp/gt r2,r4
    bf L_integration_lower
    mov r2,r4
L_integration_lower:
    mov #-128,r2
    shll8 r2
    cmp/ge r2,r4
    bf L_integration_publish
    bra L_integration_publish
    mov r4,r2

    .org 0x4956a - 0x8ea8
L_integration_publish:
    mov.l P_49678,r3
    mov #-12,r0
    extu.b r0,r0
    mov.w r2,@(r0,r3)
    mov #1,r0
    mov.l P_4968c,r6
    shll8 r0
    mov.l P_49668,r3
    mov #0,r13
    mov.l P_49698,r5
    add #0x4e,r0
    mov.b r13,@(r0,r6)
L_integration_boundary:

    .org 0x49668 - 0x8ea8
P_49668: .long 0xffff119c
    .org 0x49678 - 0x8ea8
P_49678: .long 0xffff128c
    .org 0x4968c - 0x8ea8
P_4968c: .long 0xffff1ff4
P_49690: .long 0xffff124c
P_49694: .long 0x00008eaa
P_49698: .long 0x00008292

    .org 0x49900 - 0x8ea8
L_integration_event:
    mov.l P_4995c,r6
    mov.l P_49938,r10
    mov.w @r6,r2
    mov.w @(12,r10),r0
    mul.l r4,r2
    sts macl,r2
    sub r2,r0
    bra L_integration_clamp
    mov r0,r4

    .org 0x49938 - 0x8ea8
P_49938: .long 0xffff124c
    .org 0x4995c - 0x8ea8
P_4995c: .long 0x00008eae
