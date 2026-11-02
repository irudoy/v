    ! Enter the GR11A spark vector through TRAPA #0x40 with r0..r7 = 1..8
    ! and the T bit of r5. Record r0..r7 after the exception return, then SR
    ! before the TRAPA and SR after the return.
    .text
    .balign 2
    .global _invoke_spark_probe
    .type _invoke_spark_probe,@function
_invoke_spark_probe:
    sts.l pr,@-r15
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov r4,r9

    mov r5,r0
    cmp/eq #1,r0
    stc sr,r8
    mov #1,r0
    mov #2,r1
    mov #3,r2
    mov #4,r3
    mov #5,r4
    mov #6,r5
    mov #7,r6
    mov #8,r7
    trapa #0x40
    stc sr,r10
    mov.l r0,@r9
    add #4,r9
    mov.l r1,@r9
    add #4,r9
    mov.l r2,@r9
    add #4,r9
    mov.l r3,@r9
    add #4,r9
    mov.l r4,@r9
    add #4,r9
    mov.l r5,@r9
    add #4,r9
    mov.l r6,@r9
    add #4,r9
    mov.l r7,@r9
    add #4,r9
    mov.l r8,@r9
    add #4,r9
    mov.l r10,@r9

    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    lds.l @r15+,pr
    rts
    nop

    .size _invoke_spark_probe,.-_invoke_spark_probe

    ! Control handler for the same TRAPA: it pushes the SR of exception
    ! entry below the SR cell, without the spark wrapper, and returns.
    .balign 4
    .global _spark_entry_sr_handler
    .type _spark_entry_sr_handler,@function
_spark_entry_sr_handler:
    mov.l r1,@-r15
    mov.l .Lspark_entry_sr_end,r1
    stc.l sr,@-r1
    mov.l @r15+,r1
    rte
    nop
    .balign 4
.Lspark_entry_sr_end:
    ! Simulator alias of the SR cell 0xFFFF6FE8, plus 4.
    .long 0x01006fec

    .size _spark_entry_sr_handler,.-_spark_entry_sr_handler
