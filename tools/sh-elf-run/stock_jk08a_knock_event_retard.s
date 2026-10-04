! Complete narrow two-word retard publication from explicit RAM contexts.
    .section .text
    .balign 4
    .org 0x8710 - 0x8710
C_selector: .byte 0x7c

    .org 0x4d9ac - 0x8710
L_retard_entry:
    mov.l P_4dba4,r2
    mov.l P_4dba8,r7
    mov.b @r2,r0
    and #0x20,r0
    mov r0,r6
    mov.b @(5,r7),r0
    tst #0x20,r0
    bf L_retard_gated
    mov.b @(11,r7),r0
    tst #4,r0
    bf L_retard_gated
    mov.l P_4dbac,r14
    mov #0x25,r0
    tst r6,r6
    mov.b @(r0,r14),r5
    neg r5,r0
    bt/s L_retard_boundary
    mov.w r0,@(2,r14)
    mov #0x26,r0
    mov.b @(r0,r14),r6
    bra L_retard_companion_store
    neg r6,r0
L_retard_gated:
    tst r6,r6
    bf L_retard_enabled
    mov.l P_4dbac,r14
    mov #0x25,r0
    mov.l P_4dbb0,r4
    mov.b @(r0,r14),r2
    mov.b @(2,r4),r0
    neg r2,r6
    cmp/gt r6,r0
    bt/s L_retard_disabled_min
    mov r0,r2
    mov r2,r6
L_retard_disabled_min:
    mov r6,r0
    bra L_retard_boundary
    mov.w r0,@(2,r14)
L_retard_enabled:
    mov.l P_4dbb4,r6
    mov.l P_4dbb0,r4
    mov.w @(6,r6),r0
    mov.l P_4dbac,r14
    extu.w r0,r6
    mov.b @(2,r4),r0
    shlr8 r6
    mov r0,r5
    mov r0,r2
    mov #0x26,r0
    mov.b @(r0,r14),r4
    sub r6,r2
    exts.w r2,r2
    neg r4,r6
    cmp/gt r6,r2
    bf L_retard_enabled_first_min
    mov r6,r2
L_retard_enabled_first_min:
    cmp/gt r6,r5
    mov r2,r0
    bf/s L_retard_enabled_second_byte
    mov.w r0,@(2,r14)
    bra L_retard_enabled_second_store
    mov r6,r2
L_retard_enabled_second_byte:
    exts.b r5,r2
L_retard_enabled_second_store:
    mov r2,r0
L_retard_companion_store:
    mov.w r0,@(4,r14)
L_retard_boundary:

    .org 0x4dba4 - 0x8710
P_4dba4: .long 0x00008710
P_4dba8: .long 0xffff24c0
P_4dbac: .long 0xffff11d4
P_4dbb0: .long 0xffff22f8
P_4dbb4: .long 0xffff23bc
