! Exact declared RPM view; boundaries do not execute omitted producer code.
    .text
    .balign 4
    .org 0x8743 - 0x8740
L_00008743:
    .byte 0xff
    .org 0x38506 - 0x8740
L_00038506:
    mov.l L_000385a8,r0
    .org 0x38508 - 0x8740
L_00038508:
    ldc r0,gbr
    .org 0x3850a - 0x8740
L_0003850a:
    mov.l L_000385b4,r6
    .org 0x3850c - 0x8740
L_0003850c:
    mov.w @r6,r2
    .org 0x3850e - 0x8740
L_0003850e:
    mov.l L_000385b8,r6
    .org 0x38510 - 0x8740
L_00038510:
    extu.w r2,r2
    .org 0x38512 - 0x8740
L_00038512:
    shlr2 r2
    .org 0x38514 - 0x8740
L_00038514:
    shlr r2
    .org 0x38516 - 0x8740
L_00038516:
    extu.w r2,r13
    .org 0x38518 - 0x8740
L_00038518:
    mov.b @r6,r2
    .org 0x3851a - 0x8740
L_0003851a:
    mov r13,r0
    .org 0x3851c - 0x8740
L_0003851c:
    mov.w r0,@(0x14,gbr)
    .org 0x385a8 - 0x8740
L_000385a8:
    .long 0xffff11d4
    .org 0x385b4 - 0x8740
L_000385b4:
    .long 0xffff1196
    .org 0x385b8 - 0x8740
L_000385b8:
    .long 0x00008743
