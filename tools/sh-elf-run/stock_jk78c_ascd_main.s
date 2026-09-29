! JK78C 0x000fcbb0..0x000fcbed: the coolant flag and the MAIN switch block of
! the ASCD task 0x000fb9c0, with the four pool words at 0x000fcd60 that the
! region loads, reconstructed from the stock image. The verifier links this
! source at 0x000fcbb0 and requires byte identity with the image for the
! region and the pool words.
!
! Entry state: r12 holds the stock pool literal 0xffff4506 that 0x000fc9ca
! loads, r0 holds the value the region stores at @(0xd,r12), and GBR is 0.
    .text
    .balign 2
region:
    mov.l   coolant,r2
    mov.b   r0,@(0xd,r12)
    mov.b   @r2,r5
    mov.l   coolant_threshold,r2
    mov.b   @(0x5,r12),r0
    mov.b   @r2,r6
    mov     r0,r13
    mov.b   @(0x6,r12),r0
    cmp/hs  r6,r5
    bf/s    coolant_store
    and     #0xdf,r0
    or      #0x20,r0
coolant_store:
    mov.b   r0,@(0x6,r12)
    mov.l   main_config,r0
    tst.b   #0x80,@(r0,gbr)
    bf      alternative_source
    mov.l   button_state,r0
    tst.b   #0x01,@(r0,gbr)
    bf      main_set
    bra     main_clear
    nop
alternative_source:
    mov     #89,r0
    mov.b   @(r0,r12),r0
    tst     #0x80,r0
    bt      main_clear
main_set:
    mov     r13,r0
    bra     main_store
    or      #0x10,r0
main_clear:
    mov     r13,r0
    and     #0xef,r0
main_store:
    mov.b   r0,@(0x5,r12)
region_end:

    .org    0x1b0
coolant:
    .long   0xffff1079
coolant_threshold:
    .long   0x000087de
main_config:
    .long   0x0000894f
button_state:
    .long   0xffff29a1
