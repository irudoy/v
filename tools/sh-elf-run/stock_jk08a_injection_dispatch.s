! Bounded argument preparation; observation precedes the callee JSR.
    .text
    .balign 4
dispatch_entry:
    mov.l ram_base,r3
    mov.w lead_offset,r0
    mov.l flag_base,r6
    mov.b r9,@(r0,r3)
    mov.b @(5,r6),r0
    tst #1,r0
    bt snapshot_argument
    mov.l callee,r2
    bra dispatch_boundary
    mov #52,r4
snapshot_argument:
    mov.l @(8,r15),r4
    mov.l callee,r2
dispatch_boundary:
    .org 0x54dce - 0x54d0c
lead_offset: .word 0x0229
    .org 0x54e8c - 0x54d0c
ram_base: .long 0xffff1ff4
    .org 0x54e9c - 0x54d0c
flag_base: .long 0xffff424c
callee: .long 0x0002b64a
