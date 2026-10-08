! Exact declared RPM view; boundaries do not execute omitted producer code.
    .text
    .balign 4
    .org 0x384cc - 0x384cc
L_000384cc:
    mov.l L_000385a8,r5
    .org 0x384ce - 0x384cc
L_000384ce:
    mov #-0x1,r2
    .org 0x384d0 - 0x384cc
L_000384d0:
    extu.b r2,r2
    .org 0x384d2 - 0x384cc
L_000384d2:
    mov.w @(0x14,r5),r0
    .org 0x384d4 - 0x384cc
L_000384d4:
    extu.w r0,r6
    .org 0x384d6 - 0x384cc
L_000384d6:
    shlr2 r6
    .org 0x384d8 - 0x384cc
L_000384d8:
    shlr2 r6
    .org 0x384da - 0x384cc
L_000384da:
    cmp/hi r2,r6
    .org 0x384dc - 0x384cc
L_000384dc:
    bf L_000384e0
    .org 0x384de - 0x384cc
L_000384de:
    mov r2,r6
    .org 0x384e0 - 0x384cc
L_000384e0:
    mov #0x17,r0
    .org 0x384e2 - 0x384cc
L_000384e2:
    rts
    .org 0x384e4 - 0x384cc
L_000384e4:
    mov.b r6,@(r0,r5)
    .org 0x385a8 - 0x384cc
L_000385a8:
    .long 0xffff11d4
