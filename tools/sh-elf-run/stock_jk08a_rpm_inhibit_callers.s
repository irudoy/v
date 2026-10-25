! Bounded real contributor calls; leaf units retain their stock bytes.
    .text
    .balign 4
    .org 0x4edbe - 0x4edbc
L_0004edbe:
    bsr L_0004f19c
    mov r0,r14
    bsr L_0004f282
    or r0,r14
    .org 0x4edd2 - 0x4edbc
L_0004edd2:
    bsr L_0004f736
    or r0,r14
    .org 0x4edea - 0x4edbc
L_0004edea:
    mov.l L_0004ef8c,r3
    jsr @r3
    or r2,r14
    .org 0x4edf8 - 0x4edbc
L_0004edf8:
    bsr L_0004faa0
    or r2,r14
    .org 0x4ef8c - 0x4edbc
L_0004ef8c:
    .long 0x507ce
    .org 0x4f19c - 0x4edbc
L_0004f19c:
    .org 0x4f282 - 0x4edbc
L_0004f282:
    .org 0x4f736 - 0x4edbc
L_0004f736:
    .org 0x4faa0 - 0x4edbc
L_0004faa0:
