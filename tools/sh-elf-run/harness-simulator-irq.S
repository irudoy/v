/* The same linked instructions run with and without injection. */
    .text
    .align 2
    .global irq_probe
    .global _irq_probe
    .global irq_trigger
    .global irq_resume
    .type irq_probe,@function
_irq_probe:
irq_probe:
    mov.l .Lexpected_sp,r1
    mov r15,r0
    mov.l r0,@r1
#if PROBE_CASE == 1 || PROBE_CASE == 4 || PROBE_CASE == 28 || PROBE_CASE == 29 || PROBE_CASE == 30
    mov.l .Lmasked_sr,r0
#elif PROBE_CASE == 6
    mov.l .Lequal_sr,r0
#elif PROBE_CASE == 31
    mov.l .Llower_sr,r0
#else
    mov.l .Linitial_sr,r0
#endif
    ldc r0,sr
    nop
    sts pr,r7
    stc gbr,r6
    mov.l .Lvalue,r1
    mov.l .Lfirst,r0
#if PROBE_CASE == 7
#ifndef IRQ_INHIBIT
#error IRQ_INHIBIT is required for the register-inhibit matrix
#endif
    mov.l r0,@r1
    mov.l .Lsecond,r1
#if IRQ_VALUE_VECTOR
    mov.l .Lvectors,r0
#elif IRQ_VALUE_SR
    mov.l .Linitial_sr,r0
#else
    mov #0,r0
#endif
    mov.l r0,@r1
#if IRQ_PREDECREMENT
    add #4,r1
#endif
irq_trigger:
    IRQ_INHIBIT
    nop
#elif PROBE_CASE == 15 || PROBE_CASE == 16
    mov.l r0,@r1
irq_trigger:
#if PROBE_CASE == 15
    fldi0 fr0
#else
    ldc r0,gbr
    sts macl,r2
    fldi0 fr0
    stc sr,r2
#endif
    nop
#elif PROBE_CASE == 17
    mov.l r0,@r1
irq_trigger:
    bra .Lslot_target
    stc sr,r2
.Lslot_target:
    nop
#elif PROBE_CASE == 2
irq_trigger:
    bra irq_resume
    mov.l r0,@r1
#elif PROBE_CASE == 3
    bra irq_resume
irq_trigger:
    mov.l r0,@r1
#elif PROBE_CASE >= 18 && PROBE_CASE <= 21
#if PROBE_CASE == 18 || PROBE_CASE == 21
    cmp/eq r0,r0
#else
    cmp/eq r0,r1
#endif
irq_trigger:
#if PROBE_CASE == 18 || PROBE_CASE == 19
    bt/s irq_resume
#else
    bf/s irq_resume
#endif
    mov.l r0,@r1
#elif PROBE_CASE == 22
    mov.l .Labsolute_target,r2
irq_trigger:
    jmp @r2
    mov.l r0,@r1
#elif PROBE_CASE == 23
    mov.l .Labsolute_target,r2
irq_trigger:
    jsr @r2
    mov.l r0,@r1
    bra .Lfinish
    nop
#elif PROBE_CASE == 24 || PROBE_CASE == 25
    mov.l .Lrelative_target,r2
irq_trigger:
#if PROBE_CASE == 24
    braf r2
#else
    bsrf r2
#endif
    mov.l r0,@r1
#if PROBE_CASE == 25
    bra .Lfinish
    nop
#endif
#elif PROBE_CASE == 26
    mov.l .Labsolute_target,r2
    lds r2,pr
    nop
irq_trigger:
    rts
    mov.l r0,@r1
#elif PROBE_CASE == 27
irq_trigger:
    bsr irq_resume
    mov.l r0,@r1
    bra .Lfinish
    nop
#else
#if PROBE_CASE == 5
    mov #5,r3
.Lloop:
    mov.l .Literations,r2
    mov.l @r2,r4
    add #1,r4
    mov.l r4,@r2
#endif
#if PROBE_CASE == 33
    mov.l r0,@r1
    mov.l .Lrte_sp,r1
#endif
irq_trigger:
    mov.l r0,@r1
#if PROBE_CASE == 28
    bra irq_resume
    /* Original GNU delay-slot signal control: PC-relative MOV.L. */
    .word 0xD304
#endif
#if PROBE_CASE == 1 || PROBE_CASE == 6 || PROBE_CASE == 29 || PROBE_CASE == 30
    mov.l .Lsecond,r1
    mov.l .Lsecond_value,r0
    mov.l r0,@r1
#if PROBE_CASE == 29
    mov.l .Lvector_entry,r2
    mov.l .Lalternate_handler,r3
    mov.l r3,@r2
#elif PROBE_CASE == 30
    mov.l .Lalternate_vectors,r2
    ldc r2,vbr
    nop
#endif
    mov.l .Linitial_sr,r0
    ldc r0,sr
    nop
#endif
#endif
irq_resume:
    mov.l .Lafter_r0,r2
    mov.l r0,@r2
    mov.l .Lafter_r1,r2
    mov.l r1,@r2
    stc sr,r0
    mov.l .Lafter_sr,r2
    mov.l r0,@r2
#if PROBE_CASE == 5
    dt r3
    mov.l .Lfirst,r0
    bf .Lloop
#elif PROBE_CASE == 23 || PROBE_CASE == 25 || PROBE_CASE == 27
    rts
    nop
#endif
.Lfinish:
    ldc r6,gbr
    lds r7,pr
    rts
    nop
    .align 2
.Lexpected_sp: .long _irq_expected_sp
.Linitial_sr: .long 0x00000303
.Lmasked_sr: .long 0x000003F3
.Lequal_sr: .long 0x00000383
.Llower_sr: .long 0x00000333
.Lfirst: .long 0x12345678
.Lvalue: .long _irq_value
.Lsecond: .long _irq_second
.Lsecond_value: .long 0x89ABCDEF
.Lafter_r0: .long _irq_after_r0
.Lafter_r1: .long _irq_after_r1
.Lafter_sr: .long _irq_after_sr
.Labsolute_target: .long irq_resume
.Lrelative_target: .long irq_resume - (irq_trigger + 4)
.Lvector_entry: .long _irq_vectors + 80*4
.Lalternate_handler: .long irq_handler_alt
.Lalternate_vectors: .long _irq_vectors_alt
.Lvectors: .long _irq_vectors
.Lrte_sp: .long _irq_rte_sp
.Literations: .long _irq_iterations
    .size irq_probe,.-irq_probe

    .align 2
    .global irq_handler
    .global _irq_handler
    .global irq_handler_alt
    .global _irq_handler_alt
    .type irq_handler,@function
    .global irq_stack_bytes
    .set irq_stack_bytes,16
_irq_handler_alt:
irq_handler_alt:
    nop
_irq_handler:
irq_handler:
    mov.l r0,@-r15
    mov.l r1,@-r15
    mov.l @(8,r15),r0
    mov.l .Lsaved_pc,r1
    mov.l r0,@r1
    mov.l @(12,r15),r0
    mov.l .Lsaved_sr,r1
    mov.l r0,@r1
    stc sr,r0
    mov.l .Lhandler_sr,r1
    mov.l r0,@r1
    mov r15,r0
    add #8,r0
    mov.l .Lentry_sp,r1
    mov.l r0,@r1
    mov.l .Lread_value,r1
    mov.l @r1,r0
    mov.l .Lseen_value,r1
    mov.l r0,@r1
    mov.l .Lread_second,r1
    mov.l @r1,r0
    mov.l .Lseen_second,r1
    mov.l r0,@r1
    mov.l .Lread_iterations,r1
    mov.l @r1,r0
    mov.l .Lseen_iterations,r1
    mov.l r0,@r1
    mov.l .Lhits,r1
    mov.l @r1,r0
    add #1,r0
    mov.l r0,@r1
    mov.l @r15+,r1
    mov.l @r15+,r0
    rte
#if PROBE_CASE == 33
    mov.l r15,@r1
#else
    nop
#endif
    .align 2
.Lsaved_pc: .long _irq_saved_pc
.Lsaved_sr: .long _irq_saved_sr
.Lhandler_sr: .long _irq_handler_sr
.Lentry_sp: .long _irq_entry_sp
.Lread_value: .long _irq_value
.Lread_second: .long _irq_second
.Lseen_value: .long _irq_seen_value
.Lseen_second: .long _irq_seen_second
.Lread_iterations: .long _irq_iterations
.Lseen_iterations: .long _irq_seen_iterations
.Lhits: .long _irq_hits
    .size irq_handler,.-irq_handler
    .global irq_handler_end
irq_handler_end:
