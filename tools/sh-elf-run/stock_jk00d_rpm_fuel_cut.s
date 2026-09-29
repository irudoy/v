! JK00D 0x00050bf4..0x00050c95: the main RPM fuel-cut state machine, with the
! pool word at 0x00050d64 and the four pool words at 0x00050d84 that it loads,
! reconstructed from the stock image. The verifier links this source at
! 0x00050bf4 and requires byte identity with the image for the function and
! the pool words.
!
! The function points GBR at 0xffff24d8, keeps the arm in bit 5 and the active
! cut in bit 6 of 0xffff2527, loads the delay counter 0xffff2581 from
! ROM8[0x8c99], takes the threshold pair of the table at 0x000093f4 that bit 4
! of 0xffff24f4 selects while bit 7 of ROM8[0x8b6c] is clear, compares the
! engine speed word 0xffff11ca, and returns the active cut in r0 through its
! own RTS, whose delay slot restores GBR.
    .text
    .balign 2
function:
    stc.l   gbr,@-r15
    mov.l   gbr_base,r0
    ldc     r0,gbr
    mov.b   @(0x4f,gbr),r0
    mov.l   cut_config,r6
    mov     r0,r1
    mov.b   @r6,r0
    tst     #0x80,r0
    bf      conditioned_pair
    mov.b   @(0x1c,gbr),r0
    tst     #0x10,r0
    bf      second_pair
    bra     first_pair
    nop
conditioned_pair:
    mov.b   @(0x51,gbr),r0
    tst     #0x20,r0
    bt      selected_pair
    mov.b   @(0x4b,gbr),r0
    tst     #0x02,r0
    bt      selected_pair
    mov.b   @(0x3,gbr),r0
    tst     #0x04,r0
    bt      selected_pair
    mov.l   thresholds,r4
    mov.w   @(0x8,r4),r0
    extu.w  r0,r5
    bra     compare
    mov.w   @(0xa,r4),r0
selected_pair:
    mov.b   @(0x1c,gbr),r0
    tst     #0x10,r0
    bt      first_pair
second_pair:
    mov.l   thresholds,r4
    mov.w   @(0x2,r4),r0
    extu.w  r0,r5
    bra     compare
    mov.w   @(0x6,r4),r0
first_pair:
    mov.l   thresholds,r4
    mov.w   @r4,r2
    mov.w   @(0x4,r4),r0
    extu.w  r2,r5
compare:
    mov.l   engine_speed_base,r4
    extu.w  r0,r6
    mov     r1,r0
    tst     #0x40,r0
    mov     #34,r0
    bt/s    inactive
    mov.w   @(r0,r4),r2
    extu.w  r2,r2
    cmp/ge  r6,r2
    bt      result
    mov     r1,r0
    bra     store
    and     #0x9f,r0
inactive:
    extu.w  r2,r6
    cmp/ge  r5,r6
    bf      below_cut_on
    mov     r1,r0
    tst     #0x20,r0
    bf      armed
    mov.l   cut_delay,r6
    mov.b   @r6,r0
    mov.b   r0,@(0xa9,gbr)
    mov     r1,r0
    or      #0x20,r0
    mov.b   r0,@(0x4f,gbr)
armed:
    mov.b   @(0xa9,gbr),r0
    tst     r0,r0
    bf      result
    mov     #79,r0
    bra     result
    or.b    #0x40,@(r0,gbr)
below_cut_on:
    mov     r1,r0
    and     #0xdf,r0
store:
    mov.b   r0,@(0x4f,gbr)
result:
    mov.b   @(0x4f,gbr),r0
    tst     #0x40,r0
    movt    r0
    xor     #0x01,r0
    extu.b  r0,r0
    rts
    ldc.l   @r15+,gbr
function_end:

    .org    0x170
engine_speed_base:
    .long   0xffff11a8

    .org    0x190
gbr_base:
    .long   0xffff24d8
cut_config:
    .long   0x00008b6c
thresholds:
    .long   0x000093f4
cut_delay:
    .long   0x00008c99
