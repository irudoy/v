! Exact JK08A bounded vehicle-speed state, two code spans and six pool words.
! The natural RTS delay slot restores GBR; all three stock bytes are bound.
    .text
    .org 0x8caf-0x8cac
reload_delay:
    .byte 0
    .org 0x8db7-0x8cac
activation:
    .byte 93
    .org 0x8dc3-0x8cac
release:
    .byte 91
    .org 0x4f19c-0x8cac
function:
    stc.l gbr,@-r15
    mov.l gbr_base,r0
    ldc r0,gbr
    mov.b @(0x36,gbr),r0
    mov r0,r4
    mov r0,r1
    mov.b @(0x37,gbr),r0
    mov r0,r7
    mov r4,r0
    tst #1,r0
    bt inactive
    mov r7,r0
    tst #0x20,r0
    bt active_speed
    mov r1,r0
    and #0xfe,r0
    mov.b r0,@(0x36,gbr)
active_speed:
    mov.l speed_base_active,r2
    mov #0x7a,r0
    mov.l activation_active,r5
    mov.b @(r0,r2),r6
    mov.b @(0xc,r5),r0
    cmp/hs r0,r6
    bt result
    mov r7,r0
    and #0x7f,r0
    mov.b r0,@(0x37,gbr)
    mov #0x36,r0
    bra result
    and.b #0xfe,@(r0,gbr)
active_end:
    .org 0x4f1fc-0x8cac
gbr_base:
    .long 0xffff2470
    .org 0x4f224-0x8cac
speed_base_active:
    .long 0xffff1094
    .org 0x4f23c-0x8cac
activation_active:
    .long 0x00008db7
    .org 0x4f240-0x8cac
inactive:
    mov.l speed_base_inactive,r2
    mov #0x7a,r0
    mov.l activation_inactive,r5
    mov.b @(r0,r2),r6
    mov.b @r5,r2
    cmp/hs r2,r6
    bf below_on
    mov r7,r0
    tst #0x80,r0
    bf armed
    mov.l delay_pointer,r6
    mov.b @r6,r0
    mov.b r0,@(0x86,gbr)
    mov r7,r0
    or #0x80,r0
    mov.b r0,@(0x37,gbr)
armed:
    mov.b @(0x86,gbr),r0
    tst r0,r0
    bf result
    mov.b @(0x37,gbr),r0
    tst #0x20,r0
    bf result
    mov r1,r0
    or #1,r0
    bra result
    mov.b r0,@(0x36,gbr)
below_on:
    mov r7,r0
    and #0x7f,r0
    mov.b r0,@(0x37,gbr)
result:
    mov.b @(0x36,gbr),r0
    and #1,r0
    rts
    ldc.l @r15+,gbr
function_end:
    .org 0x4f454-0x8cac
speed_base_inactive:
    .long 0xffff1094
activation_inactive:
    .long 0x00008db7
delay_pointer:
    .long 0x00008caf
