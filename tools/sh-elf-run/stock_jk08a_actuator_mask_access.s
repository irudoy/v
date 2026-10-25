! Complete natural5096C actuator mask caller and exact real predicate and staged-mask helpers.
    .text
    .balign 4
    .set ORIGIN,0x25e20
    .org 0x25e20-ORIGIN
L_00025e20:
    mov.l P_00025f10,r1
    .org 0x25e22-ORIGIN
L_00025e22:
    exts.w r4,r0
    .org 0x25e24-ORIGIN
L_00025e24:
    cmp/eq #-0x1,r0
    .org 0x25e26-ORIGIN
L_00025e26:
    bt L_00025e3e
    .org 0x25e28-ORIGIN
L_00025e28:
    mov r1,r6
    .org 0x25e2a-ORIGIN
L_00025e2a:
    mov r0,r2
    .org 0x25e2c-ORIGIN
L_00025e2c:
    shll r2
    .org 0x25e2e-ORIGIN
L_00025e2e:
    add r0,r2
    .org 0x25e30-ORIGIN
L_00025e30:
    add r2,r6
    .org 0x25e32-ORIGIN
L_00025e32:
    mov.b @(0x1,r6),r0
    .org 0x25e34-ORIGIN
L_00025e34:
    tst #0x80,r0
    .org 0x25e36-ORIGIN
L_00025e36:
    movt r0
    .org 0x25e38-ORIGIN
L_00025e38:
    xor #0x1,r0
    .org 0x25e3a-ORIGIN
L_00025e3a:
    bra L_00025e40
    .org 0x25e3c-ORIGIN
L_00025e3c:
    extu.b r0,r2
    .org 0x25e3e-ORIGIN
L_00025e3e:
    mov #0x0,r2
    .org 0x25e40-ORIGIN
L_00025e40:
    rts
    .org 0x25e42-ORIGIN
L_00025e42:
    mov r2,r0
    .org 0x25f10-ORIGIN
P_00025f10:
    .byte 0xff
    .org 0x25f11-ORIGIN
P_00025f11:
    .byte 0xff
    .org 0x25f12-ORIGIN
P_00025f12:
    .byte 0x57
    .org 0x25f13-ORIGIN
P_00025f13:
    .byte 0x18
    .org 0x5096c-ORIGIN
L_0005096c:
    sts.l pr,@-r15
    .org 0x5096e-ORIGIN
L_0005096e:
    add #-0x4,r15
    .org 0x50970-ORIGIN
L_00050970:
    mov.l P_00050b18,r6
    .org 0x50972-ORIGIN
L_00050972:
    jsr @r6
    .org 0x50974-ORIGIN
L_00050974:
    mov #0x71,r4
    .org 0x50976-ORIGIN
L_00050976:
    tst r0,r0
    .org 0x50978-ORIGIN
L_00050978:
    bf L_0005098a
    .org 0x5097a-ORIGIN
L_0005097a:
    mov.l P_00050b18,r6
    .org 0x5097c-ORIGIN
L_0005097c:
    mov.w P_00050a58,r4
    .org 0x5097e-ORIGIN
L_0005097e:
    jsr @r6
    .org 0x50980-ORIGIN
L_00050980:
    nop
    .org 0x50982-ORIGIN
L_00050982:
    tst r0,r0
    .org 0x50984-ORIGIN
L_00050984:
    bf L_0005098a
    .org 0x50986-ORIGIN
L_00050986:
    bra L_00050998
    .org 0x50988-ORIGIN
L_00050988:
    mov #0x0,r0
    .org 0x5098a-ORIGIN
L_0005098a:
    bsr L_000509a0
    .org 0x5098c-ORIGIN
L_0005098c:
    nop
    .org 0x5098e-ORIGIN
L_0005098e:
    bsr L_000509ea
    .org 0x50990-ORIGIN
L_00050990:
    mov.b r0,@r15
    .org 0x50992-ORIGIN
L_00050992:
    mov.b @r15,r2
    .org 0x50994-ORIGIN
L_00050994:
    or r0,r2
    .org 0x50996-ORIGIN
L_00050996:
    extu.b r2,r0
    .org 0x50998-ORIGIN
L_00050998:
    add #0x4,r15
    .org 0x5099a-ORIGIN
L_0005099a:
    lds.l @r15+,pr
    .org 0x5099c-ORIGIN
L_0005099c:
    rts
    .org 0x5099e-ORIGIN
L_0005099e:
    nop
    .org 0x509a0-ORIGIN
L_000509a0:
    mov.l P_00050b14,r6
    .org 0x509a2-ORIGIN
L_000509a2:
    mov #0x17,r0
    .org 0x509a4-ORIGIN
L_000509a4:
    mov.b @(r0,r6),r2
    .org 0x509a6-ORIGIN
L_000509a6:
    mov #0x2b,r6
    .org 0x509a8-ORIGIN
L_000509a8:
    extu.b r2,r2
    .org 0x509aa-ORIGIN
L_000509aa:
    cmp/ge r6,r2
    .org 0x509ac-ORIGIN
L_000509ac:
    bt L_000509b2
    .org 0x509ae-ORIGIN
L_000509ae:
    rts
    .org 0x509b0-ORIGIN
L_000509b0:
    mov #0x0,r0
    .org 0x509b2-ORIGIN
L_000509b2:
    mov #0x2c,r6
    .org 0x509b4-ORIGIN
L_000509b4:
    cmp/ge r6,r2
    .org 0x509b6-ORIGIN
L_000509b6:
    bt L_000509bc
    .org 0x509b8-ORIGIN
L_000509b8:
    rts
    .org 0x509ba-ORIGIN
L_000509ba:
    mov #0x1,r0
    .org 0x509bc-ORIGIN
L_000509bc:
    mov #0x2d,r6
    .org 0x509be-ORIGIN
L_000509be:
    cmp/ge r6,r2
    .org 0x509c0-ORIGIN
L_000509c0:
    bt L_000509c6
    .org 0x509c2-ORIGIN
L_000509c2:
    rts
    .org 0x509c4-ORIGIN
L_000509c4:
    mov #0x5,r0
    .org 0x509c6-ORIGIN
L_000509c6:
    mov #0x2e,r6
    .org 0x509c8-ORIGIN
L_000509c8:
    cmp/ge r6,r2
    .org 0x509ca-ORIGIN
L_000509ca:
    bt L_000509d0
    .org 0x509cc-ORIGIN
L_000509cc:
    rts
    .org 0x509ce-ORIGIN
L_000509ce:
    mov #0x7,r0
    .org 0x509d0-ORIGIN
L_000509d0:
    mov #0x2f,r6
    .org 0x509d2-ORIGIN
L_000509d2:
    cmp/ge r6,r2
    .org 0x509d4-ORIGIN
L_000509d4:
    bt L_000509da
    .org 0x509d6-ORIGIN
L_000509d6:
    rts
    .org 0x509d8-ORIGIN
L_000509d8:
    mov #0xf,r0
    .org 0x509da-ORIGIN
L_000509da:
    mov #0x30,r6
    .org 0x509dc-ORIGIN
L_000509dc:
    cmp/ge r6,r2
    .org 0x509de-ORIGIN
L_000509de:
    bt/s L_000509e6
    .org 0x509e0-ORIGIN
L_000509e0:
    mov #0x3f,r0
    .org 0x509e2-ORIGIN
L_000509e2:
    rts
    .org 0x509e4-ORIGIN
L_000509e4:
    mov #0x1f,r0
    .org 0x509e6-ORIGIN
L_000509e6:
    rts
    .org 0x509e8-ORIGIN
L_000509e8:
    nop
    .org 0x509ea-ORIGIN
L_000509ea:
    mov.l P_00050b1c,r5
    .org 0x509ec-ORIGIN
L_000509ec:
    mov #0x7a,r0
    .org 0x509ee-ORIGIN
L_000509ee:
    mov #0x2,r6
    .org 0x509f0-ORIGIN
L_000509f0:
    mov.b @(r0,r5),r2
    .org 0x509f2-ORIGIN
L_000509f2:
    cmp/hi r6,r2
    .org 0x509f4-ORIGIN
L_000509f4:
    bt L_000509fe
    .org 0x509f6-ORIGIN
L_000509f6:
    mov #0x50,r0
    .org 0x509f8-ORIGIN
L_000509f8:
    mov.b @(r0,r5),r0
    .org 0x509fa-ORIGIN
L_000509fa:
    tst #0x4,r0
    .org 0x509fc-ORIGIN
L_000509fc:
    bf L_00050a02
    .org 0x509fe-ORIGIN
L_000509fe:
    rts
    .org 0x50a00-ORIGIN
L_00050a00:
    mov #0x0,r0
    .org 0x50a02-ORIGIN
L_00050a02:
    rts
    .org 0x50a04-ORIGIN
L_00050a04:
    mov #0x3f,r0
    .org 0x50a58-ORIGIN
P_00050a58:
    .byte 0x01
    .org 0x50a59-ORIGIN
P_00050a59:
    .byte 0x23
    .org 0x50b14-ORIGIN
P_00050b14:
    .byte 0xff
    .org 0x50b15-ORIGIN
P_00050b15:
    .byte 0xff
    .org 0x50b16-ORIGIN
P_00050b16:
    .byte 0x11
    .org 0x50b17-ORIGIN
P_00050b17:
    .byte 0x9c
    .org 0x50b18-ORIGIN
P_00050b18:
    .byte 0x00
    .org 0x50b19-ORIGIN
P_00050b19:
    .byte 0x02
    .org 0x50b1a-ORIGIN
P_00050b1a:
    .byte 0x5e
    .org 0x50b1b-ORIGIN
P_00050b1b:
    .byte 0x20
    .org 0x50b1c-ORIGIN
P_00050b1c:
    .byte 0xff
    .org 0x50b1d-ORIGIN
P_00050b1d:
    .byte 0xff
    .org 0x50b1e-ORIGIN
P_00050b1e:
    .byte 0x10
    .org 0x50b1f-ORIGIN
P_00050b1f:
    .byte 0x94
