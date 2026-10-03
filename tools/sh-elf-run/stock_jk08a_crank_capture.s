! JK08A word capture and first-sample period at original stock addresses.
! The earlier MOV.W of the MMIO base and its signed pool word stay bound
! outside the slice. The harness supplies the mapped MMIO base in R11.
! The return boundary follows the final period store, outside tested bytes.
    .text
    .balign 2
! Link origin is the four-byte boundary before the two-byte-aligned entry.
    .word 0
crank_capture:
    mov.w capture_offset,r0
    mov.l flags_base,r6
    mov.w @(r0,r8),r5
    mov.w @(0x16,r11),r0
    mov r0,r4
    mov.w capture_offset,r0
    mov.w r4,@(r0,r8)
    mov.w period_offset,r0
    mov.w @(r0,r9),r12
    mov.b @(1,r6),r0
    tst #0x40,r0
    bt/s first_capture
    mov r0,r6
    mov.w reference_offset,r0
    sub r5,r4
    mov r4,r13
    bra publish_period
    mov.w r4,@(r0,r9)
first_capture:
    mov.w reference_offset,r0
    mov #-1,r13
    mov.l flags_base,r2
    mov.w r13,@(r0,r9)
    mov r6,r0
    or #0x40,r0
    mov.b r0,@(1,r2)
publish_period:
    mov.w period_offset,r0
    mov.w next_flags_pointer,r6
    mov.w r13,@(r0,r9)
crank_capture_end:
    .org 0xf8
mmio_base:
    .word 0xf440
capture_offset:
    .word 0x02fe
period_offset:
    .word 0x02c6
reference_offset:
    .word 0x02a0
next_flags_pointer:
    .word 0x84e8
    .org 0x128
flags_base:
    .long 0xffff24c0
