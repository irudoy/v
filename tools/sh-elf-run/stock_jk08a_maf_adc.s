! JK08A MAF ADC sampling slice. The harness supplies the mapped R4 MMIO base.
! Its original MOV #-8/SHLL8 prologue stays byte-bound outside this slice.
    .text
    .balign 4
    .word 0
maf_adc_samples:
    mov.w @(8,r4),r0
    mov.l sample_window,r5
    extu.w r0,r2
    shlr2 r2
    shlr2 r2
    shlr2 r2
    mov #0x2e,r0
    mov.w r2,@(r0,r5)
    mov #0x26,r0
    mov.w @(r0,r4),r2
    mov #0x30,r0
    extu.w r2,r2
    shlr2 r2
    shlr2 r2
    shlr2 r2
    rts
    mov.w r2,@(r0,r5)
    .org 0x334
sample_window:
    .long 0xffff1d34
