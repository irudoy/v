! Original injection programmer prologue through the entry RAM-byte store.
    .section .text
    .global _stock_code_region
    .word 0
_stock_code_region:
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    mov.l base_pointer,r0
    ldc r0,gbr
    mov.w control_pointer,r6
    mov.b @r6,r0
    or #0x80,r0
    mov.b r0,@r6
    .org 0x2b75c - 0x2b648
control_pointer:
    .word 0x84ec
    .org 0x2b864 - 0x2b648
base_pointer:
    .long 0xffff128c
