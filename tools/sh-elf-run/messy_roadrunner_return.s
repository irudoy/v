! Observing return outside the admitted stock window.
    .text
    .balign 2
messy_roadrunner_return:
    mov.l @(24,r15),r7
    lds r7,pr
    rts
    nop
