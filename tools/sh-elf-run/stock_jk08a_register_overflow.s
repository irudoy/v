! Exact natural register overflow helper, including the NEG minimum-word boundary.
    .text
    .balign 4
    .set ORIGIN,0x265c4
    .org 0x265c4-ORIGIN
L_000265c4:
    cmp/pz r5
    .org 0x265c6-ORIGIN
L_000265c6:
    bt L_000265d2
    .org 0x265c8-ORIGIN
L_000265c8:
    neg r5,r5
    .org 0x265ca-ORIGIN
L_000265ca:
    subv r5,r4
    .org 0x265cc-ORIGIN
L_000265cc:
    bt L_000265da
    .org 0x265ce-ORIGIN
L_000265ce:
    rts
    .org 0x265d0-ORIGIN
L_000265d0:
    mov r4,r0
    .org 0x265d2-ORIGIN
L_000265d2:
    addv r4,r5
    .org 0x265d4-ORIGIN
L_000265d4:
    bt L_000265e0
    .org 0x265d6-ORIGIN
L_000265d6:
    rts
    .org 0x265d8-ORIGIN
L_000265d8:
    mov r5,r0
    .org 0x265da-ORIGIN
L_000265da:
    mov.l P_000265e8,r0
    .org 0x265dc-ORIGIN
L_000265dc:
    rts
    .org 0x265de-ORIGIN
L_000265de:
    nop
    .org 0x265e0-ORIGIN
L_000265e0:
    mov.l P_000265ec,r0
    .org 0x265e2-ORIGIN
L_000265e2:
    rts
    .org 0x265e4-ORIGIN
L_000265e4:
    nop
    .org 0x265e8-ORIGIN
P_000265e8:
    .byte 0x80
    .org 0x265e9-ORIGIN
P_000265e9:
    .byte 0x00
    .org 0x265ea-ORIGIN
P_000265ea:
    .byte 0x00
    .org 0x265eb-ORIGIN
P_000265eb:
    .byte 0x00
    .org 0x265ec-ORIGIN
P_000265ec:
    .byte 0x7f
    .org 0x265ed-ORIGIN
P_000265ed:
    .byte 0xff
    .org 0x265ee-ORIGIN
P_000265ee:
    .byte 0xff
    .org 0x265ef-ORIGIN
P_000265ef:
    .byte 0xff
