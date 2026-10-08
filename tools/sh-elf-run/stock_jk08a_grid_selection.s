! Complete bank selector with real grid fill, auxiliary reset and diagnostic predicate.
    .section .text
    .org 0x839c-0x839c
P_839c: .byte 0x6e,0x5a
    .org 0x881a-0x839c
P_881a: .byte 0x04,0x04
    .org 0x88f5-0x839c
P_88f5: .byte 0x00
    .org 0x8a9e-0x839c
P_8a9e: .byte 0x5a,0x6e
    .org 0x12592-0x839c
P_12592: .byte 0x00,0x15,0x1d,0x28,0x40,0x58,0x70,0x80
    .org 0x126dc-0x839c
P_126dc: .byte 0x00,0x14,0x1e,0x2c,0x44,0x58,0x6c,0x80
    .org 0x25e20 - 0x839c
L_25e20:
    mov.l P_25f10,r1
    .org 0x25e22 - 0x839c
L_25e22:
    exts.w r4,r0
    .org 0x25e24 - 0x839c
L_25e24:
    cmp/eq #-0x1,r0
    .org 0x25e26 - 0x839c
L_25e26:
    bt L_25e3e
    .org 0x25e28 - 0x839c
L_25e28:
    mov r1,r6
    .org 0x25e2a - 0x839c
L_25e2a:
    mov r0,r2
    .org 0x25e2c - 0x839c
L_25e2c:
    shll r2
    .org 0x25e2e - 0x839c
L_25e2e:
    add r0,r2
    .org 0x25e30 - 0x839c
L_25e30:
    add r2,r6
    .org 0x25e32 - 0x839c
L_25e32:
    mov.b @(0x1,r6),r0
    .org 0x25e34 - 0x839c
L_25e34:
    tst #0x80,r0
    .org 0x25e36 - 0x839c
L_25e36:
    movt r0
    .org 0x25e38 - 0x839c
L_25e38:
    xor #0x1,r0
    .org 0x25e3a - 0x839c
L_25e3a:
    bra L_25e40
    .org 0x25e3c - 0x839c
L_25e3c:
    extu.b r0,r2
    .org 0x25e3e - 0x839c
L_25e3e:
    mov #0x0,r2
    .org 0x25e40 - 0x839c
L_25e40:
    rts
    .org 0x25e42 - 0x839c
L_25e42:
    mov r2,r0
    .org 0x25f10 - 0x839c
P_25f10: .long 0xffff5718
    .org 0x5796c-0x839c
L_5796c:
    mov.l r8,@-r15
    .org 0x5796e-0x839c
L_5796e:
    mov.l r9,@-r15
    .org 0x57970-0x839c
L_57970:
    mov.l r10,@-r15
    .org 0x57972-0x839c
L_57972:
    mov.l r11,@-r15
    .org 0x57974-0x839c
L_57974:
    mov.l r12,@-r15
    .org 0x57976-0x839c
L_57976:
    mov.l r13,@-r15
    .org 0x57978-0x839c
L_57978:
    mov.l r14,@-r15
    .org 0x5797a-0x839c
L_5797a:
    sts.l pr,@-r15
    .org 0x5797c-0x839c
L_5797c:
    add #-0x4,r15
    .org 0x5797e-0x839c
L_5797e:
    mov.l P_57b80,r2
    .org 0x57980-0x839c
L_57980:
    extu.b r4,r9
    .org 0x57982-0x839c
L_57982:
    mov.l P_57b84,r14
    .org 0x57984-0x839c
L_57984:
    mov #0x0,r12
    .org 0x57986-0x839c
L_57986:
    mov.w @r2,r7
    .org 0x57988-0x839c
L_57988:
    mov #0x7,r8
    .org 0x5798a-0x839c
L_5798a:
    mov r14,r5
    .org 0x5798c-0x839c
L_5798c:
    add #0x1,r5
    .org 0x5798e-0x839c
L_5798e:
    extu.w r7,r7
    .org 0x57990-0x839c
L_57990:
    extu.b r12,r12
    .org 0x57992-0x839c
L_57992:
    mov r9,r10
    .org 0x57994-0x839c
L_57994:
    mov r12,r0
    .org 0x57996-0x839c
L_57996:
    mov.b @(r0,r5),r2
    .org 0x57998-0x839c
L_57998:
    shll r10
    .org 0x5799a-0x839c
L_5799a:
    extu.b r2,r6
    .org 0x5799c-0x839c
L_5799c:
    shll8 r6
    .org 0x5799e-0x839c
L_5799e:
    cmp/ge r6,r7
    .org 0x579a0-0x839c
L_579a0:
    bf L_579aa
    .org 0x579a2-0x839c
L_579a2:
    add #0x1,r12
    .org 0x579a4-0x839c
L_579a4:
    extu.b r12,r12
    .org 0x579a6-0x839c
L_579a6:
    cmp/ge r8,r12
    .org 0x579a8-0x839c
L_579a8:
    bf L_57990
    .org 0x579aa-0x839c
L_579aa:
    mov.l P_57b88,r2
    .org 0x579ac-0x839c
L_579ac:
    mov r9,r0
    .org 0x579ae-0x839c
L_579ae:
    extu.b r12,r12
    .org 0x579b0-0x839c
L_579b0:
    mov.b @(r0,r2),r5
    .org 0x579b2-0x839c
L_579b2:
    mov r5,r0
    .org 0x579b4-0x839c
L_579b4:
    and #0x7,r0
    .org 0x579b6-0x839c
L_579b6:
    cmp/eq r0,r12
    .org 0x579b8-0x839c
L_579b8:
    bt/s L_579f2
    .org 0x579ba-0x839c
L_579ba:
    mov r0,r4
    .org 0x579bc-0x839c
L_579bc:
    cmp/gt r4,r12
    .org 0x579be-0x839c
L_579be:
    bf L_579dc
    .org 0x579c0-0x839c
L_579c0:
    mov r4,r0
    .org 0x579c2-0x839c
L_579c2:
    mov.l P_57b8c,r4
    .org 0x579c4-0x839c
L_579c4:
    add #0x1,r14
    .org 0x579c6-0x839c
L_579c6:
    mov.b @(r0,r14),r6
    .org 0x579c8-0x839c
L_579c8:
    mov.b @r4,r2
    .org 0x579ca-0x839c
L_579ca:
    extu.b r6,r6
    .org 0x579cc-0x839c
L_579cc:
    extu.b r2,r2
    .org 0x579ce-0x839c
L_579ce:
    add r2,r6
    .org 0x579d0-0x839c
L_579d0:
    shll8 r6
    .org 0x579d2-0x839c
L_579d2:
    cmp/ge r6,r7
    .org 0x579d4-0x839c
L_579d4:
    bt L_579f2
    .org 0x579d6-0x839c
L_579d6:
    add #-0x1,r12
    .org 0x579d8-0x839c
L_579d8:
    bra L_579f2
    .org 0x579da-0x839c
L_579da:
    extu.b r12,r12
    .org 0x579dc-0x839c
L_579dc:
    mov r4,r0
    .org 0x579de-0x839c
L_579de:
    mov.l P_57b8c,r4
    .org 0x579e0-0x839c
L_579e0:
    mov.b @(r0,r14),r2
    .org 0x579e2-0x839c
L_579e2:
    mov.b @r4,r6
    .org 0x579e4-0x839c
L_579e4:
    extu.b r2,r2
    .org 0x579e6-0x839c
L_579e6:
    extu.b r6,r4
    .org 0x579e8-0x839c
L_579e8:
    sub r4,r2
    .org 0x579ea-0x839c
L_579ea:
    shll8 r2
    .org 0x579ec-0x839c
L_579ec:
    cmp/gt r2,r7
    .org 0x579ee-0x839c
L_579ee:
    bf L_579f2
    .org 0x579f0-0x839c
L_579f0:
    add #0x1,r12
    .org 0x579f2-0x839c
L_579f2:
    mov.l P_57b90,r6
    .org 0x579f4-0x839c
L_579f4:
    mov #0x12,r0
    .org 0x579f6-0x839c
L_579f6:
    mov.l P_57b94,r11
    .org 0x579f8-0x839c
L_579f8:
    mov #0x0,r14
    .org 0x579fa-0x839c
L_579fa:
    mov.b @(r0,r6),r2
    .org 0x579fc-0x839c
L_579fc:
    mov r11,r4
    .org 0x579fe-0x839c
L_579fe:
    add #0x1,r4
    .org 0x57a00-0x839c
L_57a00:
    extu.b r2,r6
    .org 0x57a02-0x839c
L_57a02:
    extu.b r14,r14
    .org 0x57a04-0x839c
L_57a04:
    mov r14,r0
    .org 0x57a06-0x839c
L_57a06:
    mov.b @(r0,r4),r2
    .org 0x57a08-0x839c
L_57a08:
    extu.b r12,r12
    .org 0x57a0a-0x839c
L_57a0a:
    extu.b r2,r2
    .org 0x57a0c-0x839c
L_57a0c:
    mov r12,r7
    .org 0x57a0e-0x839c
L_57a0e:
    shll r7
    .org 0x57a10-0x839c
L_57a10:
    cmp/ge r2,r6
    .org 0x57a12-0x839c
L_57a12:
    bf L_57a1c
    .org 0x57a14-0x839c
L_57a14:
    add #0x1,r14
    .org 0x57a16-0x839c
L_57a16:
    extu.b r14,r14
    .org 0x57a18-0x839c
L_57a18:
    cmp/ge r8,r14
    .org 0x57a1a-0x839c
L_57a1a:
    bf L_57a02
    .org 0x57a1c-0x839c
L_57a1c:
    extu.b r5,r0
    .org 0x57a1e-0x839c
L_57a1e:
    shlr2 r0
    .org 0x57a20-0x839c
L_57a20:
    shlr r0
    .org 0x57a22-0x839c
L_57a22:
    and #0x7,r0
    .org 0x57a24-0x839c
L_57a24:
    extu.b r14,r14
    .org 0x57a26-0x839c
L_57a26:
    cmp/eq r0,r14
    .org 0x57a28-0x839c
L_57a28:
    bt/s L_57a76
    .org 0x57a2a-0x839c
L_57a2a:
    mov r0,r5
    .org 0x57a2c-0x839c
L_57a2c:
    cmp/gt r5,r14
    .org 0x57a2e-0x839c
L_57a2e:
    bf L_57a56
    .org 0x57a30-0x839c
L_57a30:
    mov.l P_57b90,r3
    .org 0x57a32-0x839c
L_57a32:
    mov #0x12,r0
    .org 0x57a34-0x839c
L_57a34:
    add #0x1,r11
    .org 0x57a36-0x839c
L_57a36:
    mov.b @(r0,r3),r6
    .org 0x57a38-0x839c
L_57a38:
    mov r5,r0
    .org 0x57a3a-0x839c
L_57a3a:
    mov.b @(r0,r11),r2
    .org 0x57a3c-0x839c
L_57a3c:
    mov.l P_57b98,r5
    .org 0x57a3e-0x839c
L_57a3e:
    extu.b r6,r4
    .org 0x57a40-0x839c
L_57a40:
    extu.b r2,r6
    .org 0x57a42-0x839c
L_57a42:
    mov.b @r5,r2
    .org 0x57a44-0x839c
L_57a44:
    extu.b r2,r2
    .org 0x57a46-0x839c
L_57a46:
    shar r2
    .org 0x57a48-0x839c
L_57a48:
    shar r2
    .org 0x57a4a-0x839c
L_57a4a:
    add r2,r6
    .org 0x57a4c-0x839c
L_57a4c:
    cmp/ge r6,r4
    .org 0x57a4e-0x839c
L_57a4e:
    bt L_57a76
    .org 0x57a50-0x839c
L_57a50:
    add #-0x1,r14
    .org 0x57a52-0x839c
L_57a52:
    bra L_57a76
    .org 0x57a54-0x839c
L_57a54:
    extu.b r14,r14
    .org 0x57a56-0x839c
L_57a56:
    mov.l P_57b90,r3
    .org 0x57a58-0x839c
L_57a58:
    mov #0x12,r0
    .org 0x57a5a-0x839c
L_57a5a:
    mov.b @(r0,r3),r6
    .org 0x57a5c-0x839c
L_57a5c:
    mov r5,r0
    .org 0x57a5e-0x839c
L_57a5e:
    mov.b @(r0,r11),r2
    .org 0x57a60-0x839c
L_57a60:
    mov.l P_57b98,r5
    .org 0x57a62-0x839c
L_57a62:
    extu.b r6,r4
    .org 0x57a64-0x839c
L_57a64:
    extu.b r2,r6
    .org 0x57a66-0x839c
L_57a66:
    mov.b @r5,r2
    .org 0x57a68-0x839c
L_57a68:
    extu.b r2,r5
    .org 0x57a6a-0x839c
L_57a6a:
    shar r5
    .org 0x57a6c-0x839c
L_57a6c:
    shar r5
    .org 0x57a6e-0x839c
L_57a6e:
    sub r5,r6
    .org 0x57a70-0x839c
L_57a70:
    cmp/gt r6,r4
    .org 0x57a72-0x839c
L_57a72:
    bf L_57a76
    .org 0x57a74-0x839c
L_57a74:
    add #0x1,r14
    .org 0x57a76-0x839c
L_57a76:
    extu.b r14,r14
    .org 0x57a78-0x839c
L_57a78:
    mov r9,r0
    .org 0x57a7a-0x839c
L_57a7a:
    mov r14,r2
    .org 0x57a7c-0x839c
L_57a7c:
    shll2 r2
    .org 0x57a7e-0x839c
L_57a7e:
    shll2 r2
    .org 0x57a80-0x839c
L_57a80:
    cmp/eq #0x1,r0
    .org 0x57a82-0x839c
L_57a82:
    bf/s L_57a8e
    .org 0x57a84-0x839c
L_57a84:
    add r7,r2
    .org 0x57a86-0x839c
L_57a86:
    mov.l P_57b9c,r6
    .org 0x57a88-0x839c
L_57a88:
    mov r2,r0
    .org 0x57a8a-0x839c
L_57a8a:
    bra L_57a94
    .org 0x57a8c-0x839c
L_57a8c:
    mov.w @(r0,r6),r7
    .org 0x57a8e-0x839c
L_57a8e:
    mov.l P_57ba0,r6
    .org 0x57a90-0x839c
L_57a90:
    mov r2,r0
    .org 0x57a92-0x839c
L_57a92:
    mov.w @(r0,r6),r7
    .org 0x57a94-0x839c
L_57a94:
    mov.l P_57ba4,r2
    .org 0x57a96-0x839c
L_57a96:
    mov.w r7,@r15
    .org 0x57a98-0x839c
L_57a98:
    extu.w r7,r7
    .org 0x57a9a-0x839c
L_57a9a:
    mov.b @r2,r6
    .org 0x57a9c-0x839c
L_57a9c:
    extu.b r6,r6
    .org 0x57a9e-0x839c
L_57a9e:
    shll8 r6
    .org 0x57aa0-0x839c
L_57aa0:
    cmp/ge r6,r7
    .org 0x57aa2-0x839c
L_57aa2:
    bf L_57ac4
    .org 0x57aa4-0x839c
L_57aa4:
    mov.l P_57ba8,r5
    .org 0x57aa6-0x839c
L_57aa6:
    mov.b @r5,r2
    .org 0x57aa8-0x839c
L_57aa8:
    extu.b r2,r2
    .org 0x57aaa-0x839c
L_57aaa:
    shll8 r2
    .org 0x57aac-0x839c
L_57aac:
    cmp/gt r2,r7
    .org 0x57aae-0x839c
L_57aae:
    bt L_57ac4
    .org 0x57ab0-0x839c
L_57ab0:
    mov.l P_57bac,r6
    .org 0x57ab2-0x839c
L_57ab2:
    mov.b @(0xc,r6),r0
    .org 0x57ab4-0x839c
L_57ab4:
    tst #0x1,r0
    .org 0x57ab6-0x839c
L_57ab6:
    bf L_57ac4
    .org 0x57ab8-0x839c
L_57ab8:
    mov.l P_57bb0,r2
    .org 0x57aba-0x839c
L_57aba:
    mov.w P_57ace,r4
    .org 0x57abc-0x839c
L_57abc:
    jsr @r2
    .org 0x57abe-0x839c
L_57abe:
    nop
    .org 0x57ac0-0x839c
L_57ac0:
    tst r0,r0
    .org 0x57ac2-0x839c
L_57ac2:
    bt L_57afe
    .org 0x57ac4-0x839c
L_57ac4:
    mov.l P_57bb4,r2
    .org 0x57ac6-0x839c
L_57ac6:
    mov #0x0,r6
    .org 0x57ac8-0x839c
L_57ac8:
    mov #0x64,r5
    .org 0x57aca-0x839c
L_57aca:
    bra L_57ad0
    .org 0x57acc-0x839c
L_57acc:
    mov r10,r0
    .org 0x57ace-0x839c
P_57ace: .word 0x0129
    .org 0x57ad0-0x839c
L_57ad0:
    mov.w r6,@(r0,r2)
    .org 0x57ad2-0x839c
L_57ad2:
    shll8 r5
    .org 0x57ad4-0x839c
L_57ad4:
    mov r9,r0
    .org 0x57ad6-0x839c
L_57ad6:
    cmp/eq #0x1,r0
    .org 0x57ad8-0x839c
L_57ad8:
    bf/s L_57aec
    .org 0x57ada-0x839c
L_57ada:
    mov.w r5,@r15
    .org 0x57adc-0x839c
L_57adc:
    mov.l P_57b9c,r4
    .org 0x57ade-0x839c
L_57ade:
    mov #-0x1,r13
    .org 0x57ae0-0x839c
L_57ae0:
    extu.b r13,r13
    .org 0x57ae2-0x839c
L_57ae2:
    bsr L_58092
    .org 0x57ae4-0x839c
L_57ae4:
    mov r13,r6
    .org 0x57ae6-0x839c
L_57ae6:
    mov.l P_57bb8,r4
    .org 0x57ae8-0x839c
L_57ae8:
    bra L_57afa
    .org 0x57aea-0x839c
L_57aea:
    mov r9,r6
    .org 0x57aec-0x839c
L_57aec:
    mov.l P_57ba0,r4
    .org 0x57aee-0x839c
L_57aee:
    mov #-0x1,r13
    .org 0x57af0-0x839c
L_57af0:
    extu.b r13,r13
    .org 0x57af2-0x839c
L_57af2:
    bsr L_58092
    .org 0x57af4-0x839c
L_57af4:
    mov r13,r6
    .org 0x57af6-0x839c
L_57af6:
    mov r9,r6
    .org 0x57af8-0x839c
L_57af8:
    mov.l P_57bbc,r4
    .org 0x57afa-0x839c
L_57afa:
    bsr L_580e8
    .org 0x57afc-0x839c
L_57afc:
    mov r13,r5
    .org 0x57afe-0x839c
L_57afe:
    shll2 r14
    .org 0x57b00-0x839c
L_57b00:
    mov.l P_57bc0,r2
    .org 0x57b02-0x839c
L_57b02:
    mov.w @r15,r7
    .org 0x57b04-0x839c
L_57b04:
    shll r14
    .org 0x57b06-0x839c
L_57b06:
    mov.l P_57b88,r6
    .org 0x57b08-0x839c
L_57b08:
    add r12,r14
    .org 0x57b0a-0x839c
L_57b0a:
    mov r10,r0
    .org 0x57b0c-0x839c
L_57b0c:
    mov.w r7,@(r0,r2)
    .org 0x57b0e-0x839c
L_57b0e:
    mov r9,r0
    .org 0x57b10-0x839c
L_57b10:
    mov.b r14,@(r0,r6)
    .org 0x57b12-0x839c
L_57b12:
    add #0x4,r15
    .org 0x57b14-0x839c
L_57b14:
    lds.l @r15+,pr
    .org 0x57b16-0x839c
L_57b16:
    mov.l @r15+,r14
    .org 0x57b18-0x839c
L_57b18:
    mov.l @r15+,r13
    .org 0x57b1a-0x839c
L_57b1a:
    mov.l @r15+,r12
    .org 0x57b1c-0x839c
L_57b1c:
    mov.l @r15+,r11
    .org 0x57b1e-0x839c
L_57b1e:
    mov.l @r15+,r10
    .org 0x57b20-0x839c
L_57b20:
    mov.l @r15+,r9
    .org 0x57b22-0x839c
L_57b22:
    rts
    .org 0x57b24-0x839c
L_57b24:
    mov.l @r15+,r8
    .org 0x57b80-0x839c
P_57b80: .long 0xffff1024
    .org 0x57b84-0x839c
P_57b84: .long 0x00012592
    .org 0x57b88-0x839c
P_57b88: .long 0xffff130a
    .org 0x57b8c-0x839c
P_57b8c: .long 0x0000881b
    .org 0x57b90-0x839c
P_57b90: .long 0xffff119c
    .org 0x57b94-0x839c
P_57b94: .long 0x000126dc
    .org 0x57b98-0x839c
P_57b98: .long 0x0000881a
    .org 0x57b9c-0x839c
P_57b9c: .long 0xffff4b10
    .org 0x57ba0-0x839c
P_57ba0: .long 0xffff4b90
    .org 0x57ba4-0x839c
P_57ba4: .long 0x00008a9e
    .org 0x57ba8-0x839c
P_57ba8: .long 0x00008a9f
    .org 0x57bac-0x839c
P_57bac: .long 0xffff41a9
    .org 0x57bb0-0x839c
P_57bb0: .long 0x00025e20
    .org 0x57bb4-0x839c
P_57bb4: .long 0xffff45a0
    .org 0x57bb8-0x839c
P_57bb8: .long 0xffff49b0
    .org 0x57bbc-0x839c
P_57bbc: .long 0xffff49f0
    .org 0x57bc0-0x839c
P_57bc0: .long 0xffff2306
    .org 0x58092-0x839c
L_58092:
    mov #-0x1,r3
    .org 0x58094-0x839c
L_58094:
    extu.b r6,r6
    .org 0x58096-0x839c
L_58096:
    extu.b r3,r3
    .org 0x58098-0x839c
L_58098:
    cmp/eq r3,r6
    .org 0x5809a-0x839c
L_5809a:
    bf/s L_580a4
    .org 0x5809c-0x839c
L_5809c:
    mov r5,r7
    .org 0x5809e-0x839c
L_5809e:
    mov #0x3f,r5
    .org 0x580a0-0x839c
L_580a0:
    bra L_580a6
    .org 0x580a2-0x839c
L_580a2:
    mov #0x0,r6
    .org 0x580a4-0x839c
L_580a4:
    mov r6,r5
    .org 0x580a6-0x839c
L_580a6:
    extu.b r5,r5
    .org 0x580a8-0x839c
L_580a8:
    extu.b r6,r6
    .org 0x580aa-0x839c
L_580aa:
    cmp/gt r5,r6
    .org 0x580ac-0x839c
L_580ac:
    bt L_580be
    .org 0x580ae-0x839c
L_580ae:
    extu.b r6,r6
    .org 0x580b0-0x839c
L_580b0:
    mov r6,r0
    .org 0x580b2-0x839c
L_580b2:
    add #0x1,r6
    .org 0x580b4-0x839c
L_580b4:
    extu.b r6,r6
    .org 0x580b6-0x839c
L_580b6:
    shll r0
    .org 0x580b8-0x839c
L_580b8:
    cmp/gt r5,r6
    .org 0x580ba-0x839c
L_580ba:
    bf/s L_580ae
    .org 0x580bc-0x839c
L_580bc:
    mov.w r7,@(r0,r4)
    .org 0x580be-0x839c
L_580be:
    rts
    .org 0x580c0-0x839c
L_580c0:
    nop
    .org 0x580e8-0x839c
L_580e8:
    mov.l r14,@-r15
    .org 0x580ea-0x839c
L_580ea:
    mov r6,r2
    .org 0x580ec-0x839c
L_580ec:
    mov #-0x1,r6
    .org 0x580ee-0x839c
L_580ee:
    extu.b r5,r1
    .org 0x580f0-0x839c
L_580f0:
    extu.b r6,r6
    .org 0x580f2-0x839c
L_580f2:
    cmp/eq r6,r1
    .org 0x580f4-0x839c
L_580f4:
    bf/s L_5810e
    .org 0x580f6-0x839c
L_580f6:
    mov r4,r14
    .org 0x580f8-0x839c
L_580f8:
    mov #0x0,r2
    .org 0x580fa-0x839c
L_580fa:
    mov r2,r5
    .org 0x580fc-0x839c
L_580fc:
    mov #0x40,r6
    .org 0x580fe-0x839c
L_580fe:
    extu.b r2,r0
    .org 0x58100-0x839c
L_58100:
    mov.b r5,@(r0,r14)
    .org 0x58102-0x839c
L_58102:
    add #0x1,r0
    .org 0x58104-0x839c
L_58104:
    extu.b r0,r2
    .org 0x58106-0x839c
L_58106:
    cmp/ge r6,r2
    .org 0x58108-0x839c
L_58108:
    bf L_580fe
    .org 0x5810a-0x839c
L_5810a:
    bra L_58164
    .org 0x5810c-0x839c
L_5810c:
    nop
    .org 0x5810e-0x839c
L_5810e:
    mov r1,r0
    .org 0x58110-0x839c
L_58110:
    mov.b @(r0,r14),r4
    .org 0x58112-0x839c
L_58112:
    mov.l P_58344,r5
    .org 0x58114-0x839c
L_58114:
    add #0x1,r4
    .org 0x58116-0x839c
L_58116:
    extu.b r4,r4
    .org 0x58118-0x839c
L_58118:
    mov.b r4,@(r0,r14)
    .org 0x5811a-0x839c
L_5811a:
    mov r4,r6
    .org 0x5811c-0x839c
L_5811c:
    mov.b @r5,r7
    .org 0x5811e-0x839c
L_5811e:
    mov #-0x1,r5
    .org 0x58120-0x839c
L_58120:
    extu.b r5,r5
    .org 0x58122-0x839c
L_58122:
    extu.b r7,r7
    .org 0x58124-0x839c
L_58124:
    add r7,r6
    .org 0x58126-0x839c
L_58126:
    cmp/gt r5,r6
    .org 0x58128-0x839c
L_58128:
    bf L_5813a
    .org 0x5812a-0x839c
L_5812a:
    cmp/ge r7,r4
    .org 0x5812c-0x839c
L_5812c:
    bt L_58132
    .org 0x5812e-0x839c
L_5812e:
    bra L_58136
    .org 0x58130-0x839c
L_58130:
    mov #0x0,r6
    .org 0x58132-0x839c
L_58132:
    sub r7,r4
    .org 0x58134-0x839c
L_58134:
    mov r4,r6
    .org 0x58136-0x839c
L_58136:
    mov r1,r0
    .org 0x58138-0x839c
L_58138:
    mov.b r6,@(r0,r14)
    .org 0x5813a-0x839c
L_5813a:
    mov.l P_58348,r5
    .org 0x5813c-0x839c
L_5813c:
    extu.b r2,r0
    .org 0x5813e-0x839c
L_5813e:
    shll r0
    .org 0x58140-0x839c
L_58140:
    mov.w @(r0,r5),r2
    .org 0x58142-0x839c
L_58142:
    mov.l P_5834c,r5
    .org 0x58144-0x839c
L_58144:
    extu.w r2,r2
    .org 0x58146-0x839c
L_58146:
    mov.b @r5,r6
    .org 0x58148-0x839c
L_58148:
    extu.b r6,r6
    .org 0x5814a-0x839c
L_5814a:
    shll8 r6
    .org 0x5814c-0x839c
L_5814c:
    cmp/ge r6,r2
    .org 0x5814e-0x839c
L_5814e:
    bt L_5815e
    .org 0x58150-0x839c
L_58150:
    mov.l P_58350,r5
    .org 0x58152-0x839c
L_58152:
    mov r2,r6
    .org 0x58154-0x839c
L_58154:
    mov.b @r5,r2
    .org 0x58156-0x839c
L_58156:
    extu.b r2,r5
    .org 0x58158-0x839c
L_58158:
    shll8 r5
    .org 0x5815a-0x839c
L_5815a:
    cmp/ge r5,r6
    .org 0x5815c-0x839c
L_5815c:
    bt L_58164
    .org 0x5815e-0x839c
L_5815e:
    mov #0x0,r5
    .org 0x58160-0x839c
L_58160:
    mov r1,r0
    .org 0x58162-0x839c
L_58162:
    mov.b r5,@(r0,r14)
    .org 0x58164-0x839c
L_58164:
    rts
    .org 0x58166-0x839c
L_58166:
    mov.l @r15+,r14
    .org 0x58344-0x839c
P_58344: .long 0x000088f5
    .org 0x58348-0x839c
P_58348: .long 0xffff134e
    .org 0x5834c-0x839c
P_5834c: .long 0x0000839c
    .org 0x58350-0x839c
P_58350: .long 0x0000839d
