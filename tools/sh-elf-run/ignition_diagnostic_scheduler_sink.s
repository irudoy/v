! Simulator observation boundary after the stock diagnostic command-byte stores.
! The APC scheduler's MMIO, timing and hardware effects are outside this fixture.
! The sink preserves all inputs except its explicitly synthetic R0 return value.
! Its instructions replace no byte in the declared stock instruction spans.
    .text
    .balign 2
    .global _ignition_diagnostic_scheduler_sink
_ignition_diagnostic_scheduler_sink:
    mov #0,r0
    rts
    nop
