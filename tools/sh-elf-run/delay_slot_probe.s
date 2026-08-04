    .section .incident_target,"ax"
    .balign 2
incident_target:
    mov #0,r0
    rts
    nop

    .section .hardware_literal,"a"
    .balign 4
    .long 0x042e432b

    .section .incident,"ax"
    .balign 2
    .global _incident
    .type _incident,@function
_incident:
    .word 0xafac
    .word SLOT_WORD
    .size _incident,.-_incident

    .section .static_literal,"a"
    .balign 4
    .long 0x00026388
