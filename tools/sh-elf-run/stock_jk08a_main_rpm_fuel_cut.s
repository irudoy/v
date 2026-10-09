! JK08A main RPM fuel-cut entry, five pool words and all14 calibration bytes.
! The independent reconstruction follows the primary function listing.
! The natural RTS delay slot restores GBR; instruction bytes stay unchanged.
    .text
    .org 0x8b38-0x8b38
configuration:
    .byte 0x63
    .org 0x8c69-0x8b38
reload_delay:
    .byte 0
    .org 0x934e-0x8b38
threshold_words:
    .short 612,596,596,368,0,0
    .org 0x4f282-0x8b38
function:
    stc.l gbr,@-r15
    mov.l gbr_base,r0
    ldc r0,gbr
    mov.b @(0x4b,gbr),r0
    mov.l cut_config,r6
    mov r0,r1
    mov.b @r6,r0
    tst #0x80,r0
    bf conditioned_pair
    mov.b @(0x1c,gbr),r0
    tst #0x10,r0
    bf second_pair
    bra first_pair
    nop
conditioned_pair:
    mov.b @(0x4d,gbr),r0
    tst #0x2,r0
    bt selected_pair
    mov.b @(0x48,gbr),r0
    tst #0x20,r0
    bt selected_pair
    mov.b @(0x3,gbr),r0
    tst #0x4,r0
    bt selected_pair
    mov.l thresholds,r4
    mov.w @(0x8,r4),r0
    extu.w r0,r5
    bra compare
    mov.w @(0xa,r4),r0
selected_pair:
    mov.b @(0x1c,gbr),r0
    tst #0x10,r0
    bt first_pair
second_pair:
    mov.l thresholds,r4
    mov.w @(0x2,r4),r0
    extu.w r0,r5
    bra compare
    mov.w @(0x6,r4),r0
first_pair:
    mov.l thresholds,r4
    mov.w @r4,r2
    mov.w @(0x4,r4),r0
    extu.w r2,r5
compare:
    mov.l engine_speed_base,r4
    extu.w r0,r6
    mov r1,r0
    tst #0x4,r0
    mov #0x20,r0
    bt/s inactive
    mov.w @(r0,r4),r2
    extu.w r2,r2
    cmp/ge r6,r2
    bt result
    mov r1,r0
    bra store
    and #0xf9,r0
inactive:
    extu.w r2,r6
    cmp/ge r5,r6
    bf below_cut_on
    mov r1,r0
    tst #0x2,r0
    bf armed
    mov.l cut_delay,r6
    mov.b @r6,r0
    mov.b r0,@(0xa5,gbr)
    mov r1,r0
    or #0x2,r0
    mov.b r0,@(0x4b,gbr)
armed:
    mov.b @(0xa5,gbr),r0
    tst r0,r0
    bf result
    mov #0x4b,r0
    bra result
    or.b #0x4,@(r0,gbr)
below_cut_on:
    mov r1,r0
    and #0xfd,r0
store:
    mov.b r0,@(0x4b,gbr)
result:
    mov.b @(0x4b,gbr),r0
    tst #0x4,r0
    movt r0
    xor #0x1,r0
    extu.b r0,r0
    rts
    ldc.l @r15+,gbr
function_end:
    .org 0x4f460-0x8b38
gbr_base:
    .long 0xffff244c
cut_config:
    .long 0x00008b38
thresholds:
    .long 0x0000934e
engine_speed_base:
    .long 0xffff119c
cut_delay:
    .long 0x00008c69
