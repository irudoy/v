! Complete standalone raw32 signed-magnitude helper with its natural RTS delay.
    .text
    .balign 4
    .set ORIGIN,0x22590
    .org 0x22590-ORIGIN
L_00022590:
    cmp/pl r4
    .org 0x22592-ORIGIN
L_00022592:
    bt L_00022596
    .org 0x22594-ORIGIN
L_00022594:
    neg r4,r4
    .org 0x22596-ORIGIN
L_00022596:
    rts
    .org 0x22598-ORIGIN
L_00022598:
    mov r4,r0
