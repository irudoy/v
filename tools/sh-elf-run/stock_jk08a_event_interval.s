! JK08A event-interval producer at its original addresses. The first MOV.W
! loads the high-RAM previous-capture pointer. It is outside the executable
! slice, whose harness supplies the mapped pointer in R1 before 0x00028afa.
! The reconstruction preserves the original pointer word and stock returns.
    .text
    .balign 4
    mov.w previous_pointer,r1
event_interval:
    mov.l mode_base,r6
    mov.b @(1,r6),r0
    tst #0x20,r0
    bf inhibited
    mov.l holdoff_base,r6
    mov.b @(4,r6),r0
    tst r0,r0
    bt measure
    mov.l interval_base,r5
    mov #-1,r2
    bra refresh_previous
    mov.l r2,@(0x28,r5)
measure:
    mov.l capture_base,r6
    mov.w capture_offset,r0
    mov.l @(r0,r6),r4
    mov.l @r1,r0
    cmp/hs r0,r4
    bt/s convert
    sub r0,r4
    add #-1,r4
convert:
    mov.l marker_pointer,r6
    shlr2 r4
    shlr2 r4
    mov.l interval_base,r5
    mov.b @r6,r0
    shlr r4
    mov.l r4,@(0x28,r5)
    or #0x20,r0
    mov.b r0,@r6
refresh_previous:
    mov.l capture_base,r6
    mov.w capture_offset,r0
    mov.l @(r0,r6),r0
    rts
    mov.l r0,@r1
inhibited:
    rts
    nop
event_interval_end:
previous_pointer:
    .word 0x84cc
capture_offset:
    .word 0x05d0
    .org 0x50
mode_base:
    .long 0xffff24c8
holdoff_base:
    .long 0xffff25fb
interval_base:
    .long 0xffff11d4
capture_base:
    .long 0xffff128c
marker_pointer:
    .long 0xffff2465
