! Observing return retains SP+24 for the genuine stock temporary.
    .text
    .balign 2
adorable_llama_return:
    mov.l @(28,r15),r7
    lds r7,pr
    rts
    nop
