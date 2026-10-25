! Complete stock pedal high-state comparator and real curve/diagnostic helper closure.
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
    .org 0x263d8-ORIGIN
L_000263d8:
    mov.l P_000263f0,r0
    .org 0x263da-ORIGIN
L_000263da:
    extu.w r5,r5
    .org 0x263dc-ORIGIN
L_000263dc:
    cmp/hs r0,r5
    .org 0x263de-ORIGIN
L_000263de:
    bt L_000263e6
    .org 0x263e0-ORIGIN
L_000263e0:
    mov.l P_000263ec,r6
    .org 0x263e2-ORIGIN
L_000263e2:
    jmp @r6
    .org 0x263e4-ORIGIN
L_000263e4:
    mov #0x0,r3
    .org 0x263e6-ORIGIN
L_000263e6:
    rts
    .org 0x263e8-ORIGIN
L_000263e8:
    mov.w @(0xe,r4),r0
    .org 0x263ec-ORIGIN
P_000263ec:
    .byte 0x00
    .org 0x263ed-ORIGIN
P_000263ed:
    .byte 0x02
    .org 0x263ee-ORIGIN
P_000263ee:
    .byte 0x6a
    .org 0x263ef-ORIGIN
P_000263ef:
    .byte 0x60
    .org 0x263f0-ORIGIN
P_000263f0:
    .byte 0x00
    .org 0x263f1-ORIGIN
P_000263f1:
    .byte 0x00
    .org 0x263f2-ORIGIN
P_000263f2:
    .byte 0xe0
    .org 0x263f3-ORIGIN
P_000263f3:
    .byte 0x00
    .org 0x26740-ORIGIN
L_00026740:
    cmp/hs r0,r2
    .org 0x26742-ORIGIN
L_00026742:
    bt L_0002675c
    .org 0x26744-ORIGIN
L_00026744:
    mov.l r0,@-r15
    .org 0x26746-ORIGIN
L_00026746:
    sub r2,r0
    .org 0x26748-ORIGIN
L_00026748:
    sts macl,r1
    .org 0x2674a-ORIGIN
L_0002674a:
    mul.l r3,r0
    .org 0x2674c-ORIGIN
L_0002674c:
    sts macl,r0
    .org 0x2674e-ORIGIN
L_0002674e:
    lds r1,macl
    .org 0x26750-ORIGIN
L_00026750:
    swap.w r0,r0
    .org 0x26752-ORIGIN
L_00026752:
    mov.l @r15+,r2
    .org 0x26754-ORIGIN
L_00026754:
    extu.w r0,r0
    .org 0x26756-ORIGIN
L_00026756:
    sub r0,r2
    .org 0x26758-ORIGIN
L_00026758:
    rts
    .org 0x2675a-ORIGIN
L_0002675a:
    mov r2,r0
    .org 0x2675c-ORIGIN
L_0002675c:
    sub r0,r2
    .org 0x2675e-ORIGIN
L_0002675e:
    sts macl,r1
    .org 0x26760-ORIGIN
L_00026760:
    mul.l r3,r2
    .org 0x26762-ORIGIN
L_00026762:
    sts macl,r2
    .org 0x26764-ORIGIN
L_00026764:
    lds r1,macl
    .org 0x26766-ORIGIN
L_00026766:
    swap.w r2,r2
    .org 0x26768-ORIGIN
L_00026768:
    extu.w r2,r2
    .org 0x2676a-ORIGIN
L_0002676a:
    rts
    .org 0x2676c-ORIGIN
L_0002676c:
    add r2,r0
    .org 0x26a60-ORIGIN
L_00026a60:
    shlr r5
    .org 0x26a62-ORIGIN
L_00026a62:
    rotcr r3
    .org 0x26a64-ORIGIN
L_00026a64:
    shlr r5
    .org 0x26a66-ORIGIN
L_00026a66:
    rotcr r3
    .org 0x26a68-ORIGIN
L_00026a68:
    shlr r5
    .org 0x26a6a-ORIGIN
L_00026a6a:
    rotcr r3
    .org 0x26a6c-ORIGIN
L_00026a6c:
    shlr r5
    .org 0x26a6e-ORIGIN
L_00026a6e:
    rotcr r3
    .org 0x26a70-ORIGIN
L_00026a70:
    shlr r5
    .org 0x26a72-ORIGIN
L_00026a72:
    rotcr r3
    .org 0x26a74-ORIGIN
L_00026a74:
    shlr r5
    .org 0x26a76-ORIGIN
L_00026a76:
    rotcr r3
    .org 0x26a78-ORIGIN
L_00026a78:
    shlr r5
    .org 0x26a7a-ORIGIN
L_00026a7a:
    rotcr r3
    .org 0x26a7c-ORIGIN
L_00026a7c:
    shlr r5
    .org 0x26a7e-ORIGIN
L_00026a7e:
    rotcr r3
    .org 0x26a80-ORIGIN
L_00026a80:
    shlr r5
    .org 0x26a82-ORIGIN
L_00026a82:
    rotcr r3
    .org 0x26a84-ORIGIN
L_00026a84:
    shlr r5
    .org 0x26a86-ORIGIN
L_00026a86:
    rotcr r3
    .org 0x26a88-ORIGIN
L_00026a88:
    shlr r5
    .org 0x26a8a-ORIGIN
L_00026a8a:
    rotcr r3
    .org 0x26a8c-ORIGIN
L_00026a8c:
    shlr r5
    .org 0x26a8e-ORIGIN
L_00026a8e:
    rotcr r3
    .org 0x26a90-ORIGIN
L_00026a90:
    shlr r5
    .org 0x26a92-ORIGIN
L_00026a92:
    rotcr r3
    .org 0x26a94-ORIGIN
L_00026a94:
    swap.w r3,r3
    .org 0x26a96-ORIGIN
L_00026a96:
    shlr8 r0
    .org 0x26a98-ORIGIN
L_00026a98:
    tst r0,r0
    .org 0x26a9a-ORIGIN
L_00026a9a:
    bt L_00026aaa
    .org 0x26a9c-ORIGIN
L_00026a9c:
    shll r5
    .org 0x26a9e-ORIGIN
L_00026a9e:
    add r5,r4
    .org 0x26aa0-ORIGIN
L_00026aa0:
    mov.w @r4,r1
    .org 0x26aa2-ORIGIN
L_00026aa2:
    mov.w @(0x2,r4),r0
    .org 0x26aa4-ORIGIN
L_00026aa4:
    extu.w r0,r2
    .org 0x26aa6-ORIGIN
L_00026aa6:
    bra L_00026ab4
    .org 0x26aa8-ORIGIN
L_00026aa8:
    extu.w r1,r0
    .org 0x26aaa-ORIGIN
L_00026aaa:
    add r5,r4
    .org 0x26aac-ORIGIN
L_00026aac:
    mov.b @r4,r1
    .org 0x26aae-ORIGIN
L_00026aae:
    mov.b @(0x1,r4),r0
    .org 0x26ab0-ORIGIN
L_00026ab0:
    extu.b r0,r2
    .org 0x26ab2-ORIGIN
L_00026ab2:
    extu.b r1,r0
    .org 0x26ab4-ORIGIN
L_00026ab4:
    mov.l P_00026abc,r6
    .org 0x26ab6-ORIGIN
L_00026ab6:
    jmp @r6
    .org 0x26ab8-ORIGIN
L_00026ab8:
    nop
    .org 0x26abc-ORIGIN
P_00026abc:
    .byte 0x00
    .org 0x26abd-ORIGIN
P_00026abd:
    .byte 0x02
    .org 0x26abe-ORIGIN
P_00026abe:
    .byte 0x67
    .org 0x26abf-ORIGIN
P_00026abf:
    .byte 0x40
    .org 0x47a56-ORIGIN
L_00047a56:
    mov.l r11,@-r15
    .org 0x47a58-ORIGIN
L_00047a58:
    mov.l r12,@-r15
    .org 0x47a5a-ORIGIN
L_00047a5a:
    mov.l r13,@-r15
    .org 0x47a5c-ORIGIN
L_00047a5c:
    mov.l r14,@-r15
    .org 0x47a5e-ORIGIN
L_00047a5e:
    sts.l pr,@-r15
    .org 0x47a60-ORIGIN
L_00047a60:
    stc.l gbr,@-r15
    .org 0x47a62-ORIGIN
L_00047a62:
    mov.l P_00047b64,r0
    .org 0x47a64-ORIGIN
L_00047a64:
    ldc r0,gbr
    .org 0x47a66-ORIGIN
L_00047a66:
    add #-0x4,r15
    .org 0x47a68-ORIGIN
L_00047a68:
    mov.l P_00047b68,r12
    .org 0x47a6a-ORIGIN
L_00047a6a:
    mov.b @r12,r0
    .org 0x47a6c-ORIGIN
L_00047a6c:
    tst #0x80,r0
    .org 0x47a6e-ORIGIN
L_00047a6e:
    bf L_00047a74
    .org 0x47a70-ORIGIN
L_00047a70:
    bra L_00047b88
    .org 0x47a72-ORIGIN
L_00047a72:
    nop
    .org 0x47a74-ORIGIN
L_00047a74:
    mov.l P_00047b58,r7
    .org 0x47a76-ORIGIN
L_00047a76:
    mov #0x7a,r0
    .org 0x47a78-ORIGIN
L_00047a78:
    mov #-0x1,r5
    .org 0x47a7a-ORIGIN
L_00047a7a:
    mov.b @(r0,r7),r2
    .org 0x47a7c-ORIGIN
L_00047a7c:
    extu.w r5,r5
    .org 0x47a7e-ORIGIN
L_00047a7e:
    extu.b r2,r6
    .org 0x47a80-ORIGIN
L_00047a80:
    shll8 r6
    .org 0x47a82-ORIGIN
L_00047a82:
    shll2 r6
    .org 0x47a84-ORIGIN
L_00047a84:
    shll r6
    .org 0x47a86-ORIGIN
L_00047a86:
    cmp/hi r5,r6
    .org 0x47a88-ORIGIN
L_00047a88:
    bt L_00047a8c
    .org 0x47a8a-ORIGIN
L_00047a8a:
    mov r6,r5
    .org 0x47a8c-ORIGIN
L_00047a8c:
    mov.l P_00047b6c,r4
    .org 0x47a8e-ORIGIN
L_00047a8e:
    mov.l P_00047b70,r2
    .org 0x47a90-ORIGIN
L_00047a90:
    jsr @r2
    .org 0x47a92-ORIGIN
L_00047a92:
    extu.w r5,r5
    .org 0x47a94-ORIGIN
L_00047a94:
    mov r0,r6
    .org 0x47a96-ORIGIN
L_00047a96:
    mov.l P_00047b34,r5
    .org 0x47a98-ORIGIN
L_00047a98:
    mov.w P_00047b32,r0
    .org 0x47a9a-ORIGIN
L_00047a9a:
    mov.w r6,@(r0,r5)
    .org 0x47a9c-ORIGIN
L_00047a9c:
    mov.b @(0x5a,gbr),r0
    .org 0x47a9e-ORIGIN
L_00047a9e:
    mov r0,r13
    .org 0x47aa0-ORIGIN
L_00047aa0:
    mov.b @(0x2,gbr),r0
    .org 0x47aa2-ORIGIN
L_00047aa2:
    tst #0x40,r0
    .org 0x47aa4-ORIGIN
L_00047aa4:
    bf L_00047ac8
    .org 0x47aa6-ORIGIN
L_00047aa6:
    mov.l P_00047b74,r2
    .org 0x47aa8-ORIGIN
L_00047aa8:
    mov.b @(0x58,gbr),r0
    .org 0x47aaa-ORIGIN
L_00047aaa:
    mov.w @r2,r14
    .org 0x47aac-ORIGIN
L_00047aac:
    tst #0x40,r0
    .org 0x47aae-ORIGIN
L_00047aae:
    bt/s L_00047ab4
    .org 0x47ab0-ORIGIN
L_00047ab0:
    extu.w r14,r14
    .org 0x47ab2-ORIGIN
L_00047ab2:
    add #0x33,r14
    .org 0x47ab4-ORIGIN
L_00047ab4:
    mov.l P_00047b34,r5
    .org 0x47ab6-ORIGIN
L_00047ab6:
    mov.w P_00047b32,r0
    .org 0x47ab8-ORIGIN
L_00047ab8:
    mov.w @(r0,r5),r6
    .org 0x47aba-ORIGIN
L_00047aba:
    extu.w r6,r6
    .org 0x47abc-ORIGIN
L_00047abc:
    cmp/hs r6,r14
    .org 0x47abe-ORIGIN
L_00047abe:
    bt/s L_00047ac6
    .org 0x47ac0-ORIGIN
L_00047ac0:
    mov #0x58,r0
    .org 0x47ac2-ORIGIN
L_00047ac2:
    bra L_00047ac8
    .org 0x47ac4-ORIGIN
L_00047ac4:
    and.b #0xbf,@(r0,gbr)
    .org 0x47ac6-ORIGIN
L_00047ac6:
    or.b #0x40,@(r0,gbr)
    .org 0x47ac8-ORIGIN
L_00047ac8:
    mov.b @(0x58,gbr),r0
    .org 0x47aca-ORIGIN
L_00047aca:
    tst #0x40,r0
    .org 0x47acc-ORIGIN
L_00047acc:
    bt L_00047ada
    .org 0x47ace-ORIGIN
L_00047ace:
    mov.b @(0x8c,gbr),r0
    .org 0x47ad0-ORIGIN
L_00047ad0:
    tst r0,r0
    .org 0x47ad2-ORIGIN
L_00047ad2:
    bt L_00047ae0
    .org 0x47ad4-ORIGIN
L_00047ad4:
    mov r13,r0
    .org 0x47ad6-ORIGIN
L_00047ad6:
    bra L_00047ae4
    .org 0x47ad8-ORIGIN
L_00047ad8:
    or #0x2,r0
    .org 0x47ada-ORIGIN
L_00047ada:
    mov.l P_00047b78,r6
    .org 0x47adc-ORIGIN
L_00047adc:
    mov.b @r6,r0
    .org 0x47ade-ORIGIN
L_00047ade:
    mov.b r0,@(0x8c,gbr)
    .org 0x47ae0-ORIGIN
L_00047ae0:
    mov r13,r0
    .org 0x47ae2-ORIGIN
L_00047ae2:
    and #0xfd,r0
    .org 0x47ae4-ORIGIN
L_00047ae4:
    mov.b r0,@(0x5a,gbr)
    .org 0x47ae6-ORIGIN
L_00047ae6:
    mov.b @(0x7b,gbr),r0
    .org 0x47ae8-ORIGIN
L_00047ae8:
    tst r0,r0
    .org 0x47aea-ORIGIN
L_00047aea:
    bt L_00047af2
    .org 0x47aec-ORIGIN
L_00047aec:
    mov.b @(0x14,gbr),r0
    .org 0x47aee-ORIGIN
L_00047aee:
    tst #0x4,r0
    .org 0x47af0-ORIGIN
L_00047af0:
    bt L_00047b2e
    .org 0x47af2-ORIGIN
L_00047af2:
    mov.l P_00047b7c,r6
    .org 0x47af4-ORIGIN
L_00047af4:
    mov.b @(0x3,r6),r0
    .org 0x47af6-ORIGIN
L_00047af6:
    tst #0x8,r0
    .org 0x47af8-ORIGIN
L_00047af8:
    bf L_00047b2e
    .org 0x47afa-ORIGIN
L_00047afa:
    mov.l P_00047b80,r2
    .org 0x47afc-ORIGIN
L_00047afc:
    jsr @r2
    .org 0x47afe-ORIGIN
L_00047afe:
    mov #0x0,r4
    .org 0x47b00-ORIGIN
L_00047b00:
    tst r0,r0
    .org 0x47b02-ORIGIN
L_00047b02:
    bt L_00047b0c
    .org 0x47b04-ORIGIN
L_00047b04:
    mov.l P_00047b84,r6
    .org 0x47b06-ORIGIN
L_00047b06:
    mov.b @r6,r0
    .org 0x47b08-ORIGIN
L_00047b08:
    tst #0x80,r0
    .org 0x47b0a-ORIGIN
L_00047b0a:
    bt L_00047b2e
    .org 0x47b0c-ORIGIN
L_00047b0c:
    mov.b @(0x14,gbr),r0
    .org 0x47b0e-ORIGIN
L_00047b0e:
    mov.l P_00047b84,r6
    .org 0x47b10-ORIGIN
L_00047b10:
    mov.b r0,@r15
    .org 0x47b12-ORIGIN
L_00047b12:
    mov.b @r6,r0
    .org 0x47b14-ORIGIN
L_00047b14:
    tst #0x80,r0
    .org 0x47b16-ORIGIN
L_00047b16:
    bf L_00047b2e
    .org 0x47b18-ORIGIN
L_00047b18:
    mov.b @r12,r0
    .org 0x47b1a-ORIGIN
L_00047b1a:
    tst #0x80,r0
    .org 0x47b1c-ORIGIN
L_00047b1c:
    bt L_00047b2e
    .org 0x47b1e-ORIGIN
L_00047b1e:
    mov.b @(0x2,gbr),r0
    .org 0x47b20-ORIGIN
L_00047b20:
    tst #0x40,r0
    .org 0x47b22-ORIGIN
L_00047b22:
    bf L_00047b2e
    .org 0x47b24-ORIGIN
L_00047b24:
    mov.b @(0x5a,gbr),r0
    .org 0x47b26-ORIGIN
L_00047b26:
    tst #0x2,r0
    .org 0x47b28-ORIGIN
L_00047b28:
    bf L_00047c18
    .org 0x47b2a-ORIGIN
L_00047b2a:
    bra L_00047c24
    .org 0x47b2c-ORIGIN
L_00047b2c:
    nop
    .org 0x47b2e-ORIGIN
L_00047b2e:
    bra L_00047c2e
    .org 0x47b30-ORIGIN
L_00047b30:
    nop
    .org 0x47b32-ORIGIN
P_00047b32:
    .byte 0x07
    .org 0x47b33-ORIGIN
P_00047b33:
    .byte 0xb6
    .org 0x47b34-ORIGIN
P_00047b34:
    .byte 0xff
    .org 0x47b35-ORIGIN
P_00047b35:
    .byte 0xff
    .org 0x47b36-ORIGIN
P_00047b36:
    .byte 0x12
    .org 0x47b37-ORIGIN
P_00047b37:
    .byte 0x8c
    .org 0x47b58-ORIGIN
P_00047b58:
    .byte 0xff
    .org 0x47b59-ORIGIN
P_00047b59:
    .byte 0xff
    .org 0x47b5a-ORIGIN
P_00047b5a:
    .byte 0x10
    .org 0x47b5b-ORIGIN
P_00047b5b:
    .byte 0x94
    .org 0x47b64-ORIGIN
P_00047b64:
    .byte 0xff
    .org 0x47b65-ORIGIN
P_00047b65:
    .byte 0xff
    .org 0x47b66-ORIGIN
P_00047b66:
    .byte 0x24
    .org 0x47b67-ORIGIN
P_00047b67:
    .byte 0x5c
    .org 0x47b68-ORIGIN
P_00047b68:
    .byte 0x00
    .org 0x47b69-ORIGIN
P_00047b69:
    .byte 0x00
    .org 0x47b6a-ORIGIN
P_00047b6a:
    .byte 0x87
    .org 0x47b6b-ORIGIN
P_00047b6b:
    .byte 0x0c
    .org 0x47b6c-ORIGIN
P_00047b6c:
    .byte 0x00
    .org 0x47b6d-ORIGIN
P_00047b6d:
    .byte 0x01
    .org 0x47b6e-ORIGIN
P_00047b6e:
    .byte 0x47
    .org 0x47b6f-ORIGIN
P_00047b6f:
    .byte 0x3a
    .org 0x47b70-ORIGIN
P_00047b70:
    .byte 0x00
    .org 0x47b71-ORIGIN
P_00047b71:
    .byte 0x02
    .org 0x47b72-ORIGIN
P_00047b72:
    .byte 0x63
    .org 0x47b73-ORIGIN
P_00047b73:
    .byte 0xd8
    .org 0x47b74-ORIGIN
P_00047b74:
    .byte 0xff
    .org 0x47b75-ORIGIN
P_00047b75:
    .byte 0xff
    .org 0x47b76-ORIGIN
P_00047b76:
    .byte 0x26
    .org 0x47b77-ORIGIN
P_00047b77:
    .byte 0x6e
    .org 0x47b78-ORIGIN
P_00047b78:
    .byte 0x00
    .org 0x47b79-ORIGIN
P_00047b79:
    .byte 0x00
    .org 0x47b7a-ORIGIN
P_00047b7a:
    .byte 0x8b
    .org 0x47b7b-ORIGIN
P_00047b7b:
    .byte 0xeb
    .org 0x47b7c-ORIGIN
P_00047b7c:
    .byte 0xff
    .org 0x47b7d-ORIGIN
P_00047b7d:
    .byte 0xff
    .org 0x47b7e-ORIGIN
P_00047b7e:
    .byte 0x42
    .org 0x47b7f-ORIGIN
P_00047b7f:
    .byte 0x4c
    .org 0x47b80-ORIGIN
P_00047b80:
    .byte 0x00
    .org 0x47b81-ORIGIN
P_00047b81:
    .byte 0x02
    .org 0x47b82-ORIGIN
P_00047b82:
    .byte 0x5e
    .org 0x47b83-ORIGIN
P_00047b83:
    .byte 0x20
    .org 0x47b84-ORIGIN
P_00047b84:
    .byte 0x00
    .org 0x47b85-ORIGIN
P_00047b85:
    .byte 0x00
    .org 0x47b86-ORIGIN
P_00047b86:
    .byte 0x8b
    .org 0x47b87-ORIGIN
P_00047b87:
    .byte 0x3f
    .org 0x47b88-ORIGIN
L_00047b88:
    mov.b @(0x5a,gbr),r0
    .org 0x47b8a-ORIGIN
L_00047b8a:
    mov.l P_00047d40,r2
    .org 0x47b8c-ORIGIN
L_00047b8c:
    mov r0,r13
    .org 0x47b8e-ORIGIN
L_00047b8e:
    mov.b @(0x11,gbr),r0
    .org 0x47b90-ORIGIN
L_00047b90:
    tst #0x80,r0
    .org 0x47b92-ORIGIN
L_00047b92:
    bt/s L_00047ba2
    .org 0x47b94-ORIGIN
L_00047b94:
    mov.w @r2,r6
    .org 0x47b96-ORIGIN
L_00047b96:
    mov.l P_00047d44,r5
    .org 0x47b98-ORIGIN
L_00047b98:
    mov.w @r5,r2
    .org 0x47b9a-ORIGIN
L_00047b9a:
    cmp/hs r2,r6
    .org 0x47b9c-ORIGIN
L_00047b9c:
    bf L_00047baa
    .org 0x47b9e-ORIGIN
L_00047b9e:
    bra L_00047bb0
    .org 0x47ba0-ORIGIN
L_00047ba0:
    nop
    .org 0x47ba2-ORIGIN
L_00047ba2:
    mov.l P_00047d48,r5
    .org 0x47ba4-ORIGIN
L_00047ba4:
    mov.w @r5,r2
    .org 0x47ba6-ORIGIN
L_00047ba6:
    cmp/hs r2,r6
    .org 0x47ba8-ORIGIN
L_00047ba8:
    bt L_00047bb0
    .org 0x47baa-ORIGIN
L_00047baa:
    mov #0xe,r0
    .org 0x47bac-ORIGIN
L_00047bac:
    bra L_00047bb4
    .org 0x47bae-ORIGIN
L_00047bae:
    and.b #0x7f,@(r0,gbr)
    .org 0x47bb0-ORIGIN
L_00047bb0:
    mov #0xe,r0
    .org 0x47bb2-ORIGIN
L_00047bb2:
    or.b #0x80,@(r0,gbr)
    .org 0x47bb4-ORIGIN
L_00047bb4:
    mov.b @(0xe,gbr),r0
    .org 0x47bb6-ORIGIN
L_00047bb6:
    tst #0x80,r0
    .org 0x47bb8-ORIGIN
L_00047bb8:
    bt L_00047be4
    .org 0x47bba-ORIGIN
L_00047bba:
    mov.l P_00047d4c,r7
    .org 0x47bbc-ORIGIN
L_00047bbc:
    mov #0x7a,r0
    .org 0x47bbe-ORIGIN
L_00047bbe:
    mov.l P_00047d50,r5
    .org 0x47bc0-ORIGIN
L_00047bc0:
    mov.b @(r0,r7),r6
    .org 0x47bc2-ORIGIN
L_00047bc2:
    mov.b @r5,r2
    .org 0x47bc4-ORIGIN
L_00047bc4:
    mov.b @(0x8c,gbr),r0
    .org 0x47bc6-ORIGIN
L_00047bc6:
    cmp/hs r2,r6
    .org 0x47bc8-ORIGIN
L_00047bc8:
    bt/s L_00047bd4
    .org 0x47bca-ORIGIN
L_00047bca:
    mov r0,r2
    .org 0x47bcc-ORIGIN
L_00047bcc:
    tst r2,r2
    .org 0x47bce-ORIGIN
L_00047bce:
    bf L_00047bde
    .org 0x47bd0-ORIGIN
L_00047bd0:
    bra L_00047bea
    .org 0x47bd2-ORIGIN
L_00047bd2:
    nop
    .org 0x47bd4-ORIGIN
L_00047bd4:
    tst r2,r2
    .org 0x47bd6-ORIGIN
L_00047bd6:
    bt L_00047be4
    .org 0x47bd8-ORIGIN
L_00047bd8:
    mov r13,r0
    .org 0x47bda-ORIGIN
L_00047bda:
    tst #0x2,r0
    .org 0x47bdc-ORIGIN
L_00047bdc:
    bt L_00047be4
    .org 0x47bde-ORIGIN
L_00047bde:
    mov r13,r0
    .org 0x47be0-ORIGIN
L_00047be0:
    bra L_00047bee
    .org 0x47be2-ORIGIN
L_00047be2:
    or #0x2,r0
    .org 0x47be4-ORIGIN
L_00047be4:
    mov.l P_00047d54,r6
    .org 0x47be6-ORIGIN
L_00047be6:
    mov.b @r6,r0
    .org 0x47be8-ORIGIN
L_00047be8:
    mov.b r0,@(0x8c,gbr)
    .org 0x47bea-ORIGIN
L_00047bea:
    mov r13,r0
    .org 0x47bec-ORIGIN
L_00047bec:
    and #0xfd,r0
    .org 0x47bee-ORIGIN
L_00047bee:
    mov.b r0,@(0x5a,gbr)
    .org 0x47bf0-ORIGIN
L_00047bf0:
    mov.b @(0x7b,gbr),r0
    .org 0x47bf2-ORIGIN
L_00047bf2:
    tst r0,r0
    .org 0x47bf4-ORIGIN
L_00047bf4:
    bt L_00047bfc
    .org 0x47bf6-ORIGIN
L_00047bf6:
    mov.b @(0x14,gbr),r0
    .org 0x47bf8-ORIGIN
L_00047bf8:
    tst #0x4,r0
    .org 0x47bfa-ORIGIN
L_00047bfa:
    bt L_00047c2e
    .org 0x47bfc-ORIGIN
L_00047bfc:
    mov.l P_00047d58,r6
    .org 0x47bfe-ORIGIN
L_00047bfe:
    mov.b @(0x3,r6),r0
    .org 0x47c00-ORIGIN
L_00047c00:
    tst #0x8,r0
    .org 0x47c02-ORIGIN
L_00047c02:
    bf L_00047c2e
    .org 0x47c04-ORIGIN
L_00047c04:
    mov.l P_00047d5c,r2
    .org 0x47c06-ORIGIN
L_00047c06:
    jsr @r2
    .org 0x47c08-ORIGIN
L_00047c08:
    mov #0x0,r4
    .org 0x47c0a-ORIGIN
L_00047c0a:
    tst r0,r0
    .org 0x47c0c-ORIGIN
L_00047c0c:
    bf L_00047c2e
    .org 0x47c0e-ORIGIN
L_00047c0e:
    mov.b @(0x14,gbr),r0
    .org 0x47c10-ORIGIN
L_00047c10:
    mov.b r0,@r15
    .org 0x47c12-ORIGIN
L_00047c12:
    mov.b @(0x5a,gbr),r0
    .org 0x47c14-ORIGIN
L_00047c14:
    tst #0x2,r0
    .org 0x47c16-ORIGIN
L_00047c16:
    bt L_00047c24
    .org 0x47c18-ORIGIN
L_00047c18:
    mov.l P_00047d60,r6
    .org 0x47c1a-ORIGIN
L_00047c1a:
    mov.b @r6,r0
    .org 0x47c1c-ORIGIN
L_00047c1c:
    mov.b r0,@(0x7b,gbr)
    .org 0x47c1e-ORIGIN
L_00047c1e:
    mov.b @r15,r0
    .org 0x47c20-ORIGIN
L_00047c20:
    bra L_00047c28
    .org 0x47c22-ORIGIN
L_00047c22:
    or #0x4,r0
    .org 0x47c24-ORIGIN
L_00047c24:
    mov.b @r15,r0
    .org 0x47c26-ORIGIN
L_00047c26:
    and #0xfb,r0
    .org 0x47c28-ORIGIN
L_00047c28:
    mov.b r0,@r15
    .org 0x47c2a-ORIGIN
L_00047c2a:
    bra L_00047c32
    .org 0x47c2c-ORIGIN
L_00047c2c:
    mov.b r0,@(0x14,gbr)
    .org 0x47c2e-ORIGIN
L_00047c2e:
    mov #0x14,r0
    .org 0x47c30-ORIGIN
L_00047c30:
    and.b #0xfb,@(r0,gbr)
    .org 0x47c32-ORIGIN
L_00047c32:
    mov.b @(0x15,gbr),r0
    .org 0x47c34-ORIGIN
L_00047c34:
    mov.l P_00047d64,r2
    .org 0x47c36-ORIGIN
L_00047c36:
    mov r0,r14
    .org 0x47c38-ORIGIN
L_00047c38:
    mov.l P_00047d68,r12
    .org 0x47c3a-ORIGIN
L_00047c3a:
    mov.b @r2,r0
    .org 0x47c3c-ORIGIN
L_00047c3c:
    tst #0x4,r0
    .org 0x47c3e-ORIGIN
L_00047c3e:
    mov #0x12,r0
    .org 0x47c40-ORIGIN
L_00047c40:
    mov.b @(r0,r12),r4
    .org 0x47c42-ORIGIN
L_00047c42:
    bf/s L_00047c5c
    .org 0x47c44-ORIGIN
L_00047c44:
    extu.b r4,r4
    .org 0x47c46-ORIGIN
L_00047c46:
    mov.l P_00047d6c,r11
    .org 0x47c48-ORIGIN
L_00047c48:
    mov.b @(0x2,r11),r0
    .org 0x47c4a-ORIGIN
L_00047c4a:
    extu.b r0,r2
    .org 0x47c4c-ORIGIN
L_00047c4c:
    cmp/ge r2,r4
    .org 0x47c4e-ORIGIN
L_00047c4e:
    bf L_00047cee
    .org 0x47c50-ORIGIN
L_00047c50:
    mov.b @(0x1,r11),r0
    .org 0x47c52-ORIGIN
L_00047c52:
    extu.b r0,r2
    .org 0x47c54-ORIGIN
L_00047c54:
    cmp/ge r2,r4
    .org 0x47c56-ORIGIN
L_00047c56:
    bt L_00047cf4
    .org 0x47c58-ORIGIN
L_00047c58:
    bra L_00047cf8
    .org 0x47c5a-ORIGIN
L_00047c5a:
    nop
    .org 0x47c5c-ORIGIN
L_00047c5c:
    mov.l P_00047d70,r5
    .org 0x47c5e-ORIGIN
L_00047c5e:
    mov.b @r5,r2
    .org 0x47c60-ORIGIN
L_00047c60:
    extu.b r2,r2
    .org 0x47c62-ORIGIN
L_00047c62:
    cmp/ge r2,r4
    .org 0x47c64-ORIGIN
L_00047c64:
    bt L_00047cf4
    .org 0x47c66-ORIGIN
L_00047c66:
    mov.l P_00047d4c,r7
    .org 0x47c68-ORIGIN
L_00047c68:
    mov #0x58,r0
    .org 0x47c6a-ORIGIN
L_00047c6a:
    mov.b @(r0,r7),r5
    .org 0x47c6c-ORIGIN
L_00047c6c:
    mov.l P_00047d74,r7
    .org 0x47c6e-ORIGIN
L_00047c6e:
    extu.b r5,r5
    .org 0x47c70-ORIGIN
L_00047c70:
    mov.b @r7,r2
    .org 0x47c72-ORIGIN
L_00047c72:
    extu.b r2,r2
    .org 0x47c74-ORIGIN
L_00047c74:
    cmp/ge r2,r5
    .org 0x47c76-ORIGIN
L_00047c76:
    bt L_00047cf4
    .org 0x47c78-ORIGIN
L_00047c78:
    mov.l P_00047d78,r7
    .org 0x47c7a-ORIGIN
L_00047c7a:
    mov.b @r7,r2
    .org 0x47c7c-ORIGIN
L_00047c7c:
    extu.b r2,r2
    .org 0x47c7e-ORIGIN
L_00047c7e:
    cmp/gt r2,r5
    .org 0x47c80-ORIGIN
L_00047c80:
    bf L_00047cf4
    .org 0x47c82-ORIGIN
L_00047c82:
    mov.l P_00047d7c,r7
    .org 0x47c84-ORIGIN
L_00047c84:
    mov.b @r7,r2
    .org 0x47c86-ORIGIN
L_00047c86:
    extu.b r2,r2
    .org 0x47c88-ORIGIN
L_00047c88:
    cmp/ge r2,r4
    .org 0x47c8a-ORIGIN
L_00047c8a:
    bf L_00047c96
    .org 0x47c8c-ORIGIN
L_00047c8c:
    mov.l P_00047d80,r7
    .org 0x47c8e-ORIGIN
L_00047c8e:
    mov.b @r7,r2
    .org 0x47c90-ORIGIN
L_00047c90:
    extu.b r2,r2
    .org 0x47c92-ORIGIN
L_00047c92:
    cmp/ge r2,r5
    .org 0x47c94-ORIGIN
L_00047c94:
    bt L_00047cf4
    .org 0x47c96-ORIGIN
L_00047c96:
    mov.l P_00047d6c,r11
    .org 0x47c98-ORIGIN
L_00047c98:
    mov.b @(0x1,r11),r0
    .org 0x47c9a-ORIGIN
L_00047c9a:
    extu.b r0,r7
    .org 0x47c9c-ORIGIN
L_00047c9c:
    cmp/ge r7,r4
    .org 0x47c9e-ORIGIN
L_00047c9e:
    bf L_00047caa
    .org 0x47ca0-ORIGIN
L_00047ca0:
    mov.l P_00047d84,r7
    .org 0x47ca2-ORIGIN
L_00047ca2:
    mov.b @r7,r2
    .org 0x47ca4-ORIGIN
L_00047ca4:
    extu.b r2,r2
    .org 0x47ca6-ORIGIN
L_00047ca6:
    cmp/ge r2,r5
    .org 0x47ca8-ORIGIN
L_00047ca8:
    bt L_00047cf4
    .org 0x47caa-ORIGIN
L_00047caa:
    mov.b @(0x2,r11),r0
    .org 0x47cac-ORIGIN
L_00047cac:
    extu.b r0,r7
    .org 0x47cae-ORIGIN
L_00047cae:
    cmp/ge r7,r4
    .org 0x47cb0-ORIGIN
L_00047cb0:
    bt L_00047ccc
    .org 0x47cb2-ORIGIN
L_00047cb2:
    cmp/pl r4
    .org 0x47cb4-ORIGIN
L_00047cb4:
    bf L_00047ccc
    .org 0x47cb6-ORIGIN
L_00047cb6:
    mov.l P_00047d88,r7
    .org 0x47cb8-ORIGIN
L_00047cb8:
    extu.b r5,r5
    .org 0x47cba-ORIGIN
L_00047cba:
    mov.b @r7,r2
    .org 0x47cbc-ORIGIN
L_00047cbc:
    extu.b r2,r2
    .org 0x47cbe-ORIGIN
L_00047cbe:
    cmp/ge r2,r5
    .org 0x47cc0-ORIGIN
L_00047cc0:
    bt L_00047ccc
    .org 0x47cc2-ORIGIN
L_00047cc2:
    mov.l P_00047d8c,r7
    .org 0x47cc4-ORIGIN
L_00047cc4:
    mov.b @r7,r2
    .org 0x47cc6-ORIGIN
L_00047cc6:
    extu.b r2,r2
    .org 0x47cc8-ORIGIN
L_00047cc8:
    cmp/gt r2,r5
    .org 0x47cca-ORIGIN
L_00047cca:
    bt L_00047cee
    .org 0x47ccc-ORIGIN
L_00047ccc:
    mov.b @(0x3,r11),r0
    .org 0x47cce-ORIGIN
L_00047cce:
    extu.b r0,r2
    .org 0x47cd0-ORIGIN
L_00047cd0:
    cmp/ge r2,r4
    .org 0x47cd2-ORIGIN
L_00047cd2:
    bt L_00047cf8
    .org 0x47cd4-ORIGIN
L_00047cd4:
    cmp/pl r4
    .org 0x47cd6-ORIGIN
L_00047cd6:
    bf L_00047cf8
    .org 0x47cd8-ORIGIN
L_00047cd8:
    mov.l P_00047d90,r4
    .org 0x47cda-ORIGIN
L_00047cda:
    extu.b r5,r5
    .org 0x47cdc-ORIGIN
L_00047cdc:
    mov.b @r4,r2
    .org 0x47cde-ORIGIN
L_00047cde:
    extu.b r2,r2
    .org 0x47ce0-ORIGIN
L_00047ce0:
    cmp/ge r2,r5
    .org 0x47ce2-ORIGIN
L_00047ce2:
    bt L_00047cf8
    .org 0x47ce4-ORIGIN
L_00047ce4:
    mov.l P_00047d88,r7
    .org 0x47ce6-ORIGIN
L_00047ce6:
    mov.b @r7,r2
    .org 0x47ce8-ORIGIN
L_00047ce8:
    extu.b r2,r6
    .org 0x47cea-ORIGIN
L_00047cea:
    cmp/ge r6,r5
    .org 0x47cec-ORIGIN
L_00047cec:
    bf L_00047cf8
    .org 0x47cee-ORIGIN
L_00047cee:
    mov #0xe,r0
    .org 0x47cf0-ORIGIN
L_00047cf0:
    bra L_00047cf8
    .org 0x47cf2-ORIGIN
L_00047cf2:
    and.b #0xbf,@(r0,gbr)
    .org 0x47cf4-ORIGIN
L_00047cf4:
    mov #0xe,r0
    .org 0x47cf6-ORIGIN
L_00047cf6:
    or.b #0x40,@(r0,gbr)
    .org 0x47cf8-ORIGIN
L_00047cf8:
    mov.l P_00047d94,r6
    .org 0x47cfa-ORIGIN
L_00047cfa:
    mov.b @r6,r0
    .org 0x47cfc-ORIGIN
L_00047cfc:
    and #0x40,r0
    .org 0x47cfe-ORIGIN
L_00047cfe:
    tst r0,r0
    .org 0x47d00-ORIGIN
L_00047d00:
    bt/s L_00047d0a
    .org 0x47d02-ORIGIN
L_00047d02:
    mov r0,r2
    .org 0x47d04-ORIGIN
L_00047d04:
    mov.l P_00047d98,r5
    .org 0x47d06-ORIGIN
L_00047d06:
    mov.b @r5,r0
    .org 0x47d08-ORIGIN
L_00047d08:
    mov.b r0,@(0xfd,gbr)
    .org 0x47d0a-ORIGIN
L_00047d0a:
    tst r2,r2
    .org 0x47d0c-ORIGIN
L_00047d0c:
    bf L_00047d1a
    .org 0x47d0e-ORIGIN
L_00047d0e:
    mov.b @(0xfd,gbr),r0
    .org 0x47d10-ORIGIN
L_00047d10:
    tst r0,r0
    .org 0x47d12-ORIGIN
L_00047d12:
    bf L_00047d1a
    .org 0x47d14-ORIGIN
L_00047d14:
    mov r14,r0
    .org 0x47d16-ORIGIN
L_00047d16:
    bra L_00047d1e
    .org 0x47d18-ORIGIN
L_00047d18:
    and #0x7f,r0
    .org 0x47d1a-ORIGIN
L_00047d1a:
    mov r14,r0
    .org 0x47d1c-ORIGIN
L_00047d1c:
    or #0x80,r0
    .org 0x47d1e-ORIGIN
L_00047d1e:
    mov.b r0,@(0x15,gbr)
    .org 0x47d20-ORIGIN
L_00047d20:
    exts.b r0,r0
    .org 0x47d22-ORIGIN
L_00047d22:
    extu.b r0,r13
    .org 0x47d24-ORIGIN
L_00047d24:
    mov r13,r0
    .org 0x47d26-ORIGIN
L_00047d26:
    and #0x40,r0
    .org 0x47d28-ORIGIN
L_00047d28:
    tst r0,r0
    .org 0x47d2a-ORIGIN
L_00047d2a:
    bt/s L_00047da0
    .org 0x47d2c-ORIGIN
L_00047d2c:
    mov r0,r6
    .org 0x47d2e-ORIGIN
L_00047d2e:
    mov.l P_00047d9c,r4
    .org 0x47d30-ORIGIN
L_00047d30:
    mov #0x12,r0
    .org 0x47d32-ORIGIN
L_00047d32:
    mov.b @(r0,r12),r5
    .org 0x47d34-ORIGIN
L_00047d34:
    mov.b @r4,r2
    .org 0x47d36-ORIGIN
L_00047d36:
    cmp/hs r2,r5
    .org 0x47d38-ORIGIN
L_00047d38:
    bf L_00047da0
    .org 0x47d3a-ORIGIN
L_00047d3a:
    mov r13,r0
    .org 0x47d3c-ORIGIN
L_00047d3c:
    bra L_00047db4
    .org 0x47d3e-ORIGIN
L_00047d3e:
    and #0xbf,r0
    .org 0x47d40-ORIGIN
P_00047d40:
    .byte 0xff
    .org 0x47d41-ORIGIN
P_00047d41:
    .byte 0xff
    .org 0x47d42-ORIGIN
P_00047d42:
    .byte 0x26
    .org 0x47d43-ORIGIN
P_00047d43:
    .byte 0x6e
    .org 0x47d44-ORIGIN
P_00047d44:
    .byte 0x00
    .org 0x47d45-ORIGIN
P_00047d45:
    .byte 0x00
    .org 0x47d46-ORIGIN
P_00047d46:
    .byte 0x8f
    .org 0x47d47-ORIGIN
P_00047d47:
    .byte 0xde
    .org 0x47d48-ORIGIN
P_00047d48:
    .byte 0x00
    .org 0x47d49-ORIGIN
P_00047d49:
    .byte 0x00
    .org 0x47d4a-ORIGIN
P_00047d4a:
    .byte 0x8f
    .org 0x47d4b-ORIGIN
P_00047d4b:
    .byte 0xdc
    .org 0x47d4c-ORIGIN
P_00047d4c:
    .byte 0xff
    .org 0x47d4d-ORIGIN
P_00047d4d:
    .byte 0xff
    .org 0x47d4e-ORIGIN
P_00047d4e:
    .byte 0x10
    .org 0x47d4f-ORIGIN
P_00047d4f:
    .byte 0x94
    .org 0x47d50-ORIGIN
P_00047d50:
    .byte 0x00
    .org 0x47d51-ORIGIN
P_00047d51:
    .byte 0x00
    .org 0x47d52-ORIGIN
P_00047d52:
    .byte 0x8d
    .org 0x47d53-ORIGIN
P_00047d53:
    .byte 0xb5
    .org 0x47d54-ORIGIN
P_00047d54:
    .byte 0x00
    .org 0x47d55-ORIGIN
P_00047d55:
    .byte 0x00
    .org 0x47d56-ORIGIN
P_00047d56:
    .byte 0x8b
    .org 0x47d57-ORIGIN
P_00047d57:
    .byte 0xeb
    .org 0x47d58-ORIGIN
P_00047d58:
    .byte 0xff
    .org 0x47d59-ORIGIN
P_00047d59:
    .byte 0xff
    .org 0x47d5a-ORIGIN
P_00047d5a:
    .byte 0x42
    .org 0x47d5b-ORIGIN
P_00047d5b:
    .byte 0x4c
    .org 0x47d5c-ORIGIN
P_00047d5c:
    .byte 0x00
    .org 0x47d5d-ORIGIN
P_00047d5d:
    .byte 0x02
    .org 0x47d5e-ORIGIN
P_00047d5e:
    .byte 0x5e
    .org 0x47d5f-ORIGIN
P_00047d5f:
    .byte 0x20
    .org 0x47d60-ORIGIN
P_00047d60:
    .byte 0x00
    .org 0x47d61-ORIGIN
P_00047d61:
    .byte 0x00
    .org 0x47d62-ORIGIN
P_00047d62:
    .byte 0x83
    .org 0x47d63-ORIGIN
P_00047d63:
    .byte 0xf2
    .org 0x47d64-ORIGIN
P_00047d64:
    .byte 0x00
    .org 0x47d65-ORIGIN
P_00047d65:
    .byte 0x00
    .org 0x47d66-ORIGIN
P_00047d66:
    .byte 0x87
    .org 0x47d67-ORIGIN
P_00047d67:
    .byte 0x0d
    .org 0x47d68-ORIGIN
P_00047d68:
    .byte 0xff
    .org 0x47d69-ORIGIN
P_00047d69:
    .byte 0xff
    .org 0x47d6a-ORIGIN
P_00047d6a:
    .byte 0x11
    .org 0x47d6b-ORIGIN
P_00047d6b:
    .byte 0x9c
    .org 0x47d6c-ORIGIN
P_00047d6c:
    .byte 0x00
    .org 0x47d6d-ORIGIN
P_00047d6d:
    .byte 0x00
    .org 0x47d6e-ORIGIN
P_00047d6e:
    .byte 0x88
    .org 0x47d6f-ORIGIN
P_00047d6f:
    .byte 0x91
    .org 0x47d70-ORIGIN
P_00047d70:
    .byte 0x00
    .org 0x47d71-ORIGIN
P_00047d71:
    .byte 0x00
    .org 0x47d72-ORIGIN
P_00047d72:
    .byte 0x88
    .org 0x47d73-ORIGIN
P_00047d73:
    .byte 0xb0
    .org 0x47d74-ORIGIN
P_00047d74:
    .byte 0x00
    .org 0x47d75-ORIGIN
P_00047d75:
    .byte 0x00
    .org 0x47d76-ORIGIN
P_00047d76:
    .byte 0x89
    .org 0x47d77-ORIGIN
P_00047d77:
    .byte 0xa4
    .org 0x47d78-ORIGIN
P_00047d78:
    .byte 0x00
    .org 0x47d79-ORIGIN
P_00047d79:
    .byte 0x00
    .org 0x47d7a-ORIGIN
P_00047d7a:
    .byte 0x8d
    .org 0x47d7b-ORIGIN
P_00047d7b:
    .byte 0x98
    .org 0x47d7c-ORIGIN
P_00047d7c:
    .byte 0x00
    .org 0x47d7d-ORIGIN
P_00047d7d:
    .byte 0x00
    .org 0x47d7e-ORIGIN
P_00047d7e:
    .byte 0x88
    .org 0x47d7f-ORIGIN
P_00047d7f:
    .byte 0xb2
    .org 0x47d80-ORIGIN
P_00047d80:
    .byte 0x00
    .org 0x47d81-ORIGIN
P_00047d81:
    .byte 0x00
    .org 0x47d82-ORIGIN
P_00047d82:
    .byte 0x8d
    .org 0x47d83-ORIGIN
P_00047d83:
    .byte 0x97
    .org 0x47d84-ORIGIN
P_00047d84:
    .byte 0x00
    .org 0x47d85-ORIGIN
P_00047d85:
    .byte 0x00
    .org 0x47d86-ORIGIN
P_00047d86:
    .byte 0x89
    .org 0x47d87-ORIGIN
P_00047d87:
    .byte 0xa5
    .org 0x47d88-ORIGIN
P_00047d88:
    .byte 0x00
    .org 0x47d89-ORIGIN
P_00047d89:
    .byte 0x00
    .org 0x47d8a-ORIGIN
P_00047d8a:
    .byte 0x8d
    .org 0x47d8b-ORIGIN
P_00047d8b:
    .byte 0x99
    .org 0x47d8c-ORIGIN
P_00047d8c:
    .byte 0x00
    .org 0x47d8d-ORIGIN
P_00047d8d:
    .byte 0x00
    .org 0x47d8e-ORIGIN
P_00047d8e:
    .byte 0x8d
    .org 0x47d8f-ORIGIN
P_00047d8f:
    .byte 0x9b
    .org 0x47d90-ORIGIN
P_00047d90:
    .byte 0x00
    .org 0x47d91-ORIGIN
P_00047d91:
    .byte 0x00
    .org 0x47d92-ORIGIN
P_00047d92:
    .byte 0x8d
    .org 0x47d93-ORIGIN
P_00047d93:
    .byte 0x9a
    .org 0x47d94-ORIGIN
P_00047d94:
    .byte 0xff
    .org 0x47d95-ORIGIN
P_00047d95:
    .byte 0xff
    .org 0x47d96-ORIGIN
P_00047d96:
    .byte 0x41
    .org 0x47d97-ORIGIN
P_00047d97:
    .byte 0x84
    .org 0x47d98-ORIGIN
P_00047d98:
    .byte 0x00
    .org 0x47d99-ORIGIN
P_00047d99:
    .byte 0x00
    .org 0x47d9a-ORIGIN
P_00047d9a:
    .byte 0x8b
    .org 0x47d9b-ORIGIN
P_00047d9b:
    .byte 0xed
    .org 0x47d9c-ORIGIN
P_00047d9c:
    .byte 0x00
    .org 0x47d9d-ORIGIN
P_00047d9d:
    .byte 0x00
    .org 0x47d9e-ORIGIN
P_00047d9e:
    .byte 0x88
    .org 0x47d9f-ORIGIN
P_00047d9f:
    .byte 0xb4
    .org 0x47da0-ORIGIN
L_00047da0:
    tst r6,r6
    .org 0x47da2-ORIGIN
L_00047da2:
    bf L_00047db8
    .org 0x47da4-ORIGIN
L_00047da4:
    mov.l P_00047f84,r5
    .org 0x47da6-ORIGIN
L_00047da6:
    mov #0x12,r0
    .org 0x47da8-ORIGIN
L_00047da8:
    mov.b @(r0,r12),r4
    .org 0x47daa-ORIGIN
L_00047daa:
    mov.b @r5,r2
    .org 0x47dac-ORIGIN
L_00047dac:
    cmp/hs r2,r4
    .org 0x47dae-ORIGIN
L_00047dae:
    bt L_00047db8
    .org 0x47db0-ORIGIN
L_00047db0:
    mov r13,r0
    .org 0x47db2-ORIGIN
L_00047db2:
    or #0x40,r0
    .org 0x47db4-ORIGIN
L_00047db4:
    mov.b r0,@(0x15,gbr)
    .org 0x47db6-ORIGIN
L_00047db6:
    exts.b r0,r13
    .org 0x47db8-ORIGIN
L_00047db8:
    mov.b @(0x14,gbr),r0
    .org 0x47dba-ORIGIN
L_00047dba:
    mov r0,r2
    .org 0x47dbc-ORIGIN
L_00047dbc:
    mov r13,r0
    .org 0x47dbe-ORIGIN
L_00047dbe:
    tst #0xc0,r0
    .org 0x47dc0-ORIGIN
L_00047dc0:
    mov r2,r0
    .org 0x47dc2-ORIGIN
L_00047dc2:
    bt/s L_00047dc8
    .org 0x47dc4-ORIGIN
L_00047dc4:
    and #0xfe,r0
    .org 0x47dc6-ORIGIN
L_00047dc6:
    or #0x1,r0
    .org 0x47dc8-ORIGIN
L_00047dc8:
    mov.b r0,@(0x14,gbr)
    .org 0x47dca-ORIGIN
L_00047dca:
    mov.b @(0x15,gbr),r0
    .org 0x47dcc-ORIGIN
L_00047dcc:
    tst #0x20,r0
    .org 0x47dce-ORIGIN
L_00047dce:
    bt L_00047de0
    .org 0x47dd0-ORIGIN
L_00047dd0:
    mov.l P_00047f88,r4
    .org 0x47dd2-ORIGIN
L_00047dd2:
    mov.l P_00047f8c,r5
    .org 0x47dd4-ORIGIN
L_00047dd4:
    mov.b @(0x9,r4),r0
    .org 0x47dd6-ORIGIN
L_00047dd6:
    mov.b @r5,r2
    .org 0x47dd8-ORIGIN
L_00047dd8:
    cmp/hs r2,r0
    .org 0x47dda-ORIGIN
L_00047dda:
    bf L_00047dec
    .org 0x47ddc-ORIGIN
L_00047ddc:
    bra L_00047df2
    .org 0x47dde-ORIGIN
L_00047dde:
    nop
    .org 0x47de0-ORIGIN
L_00047de0:
    mov.l P_00047f88,r4
    .org 0x47de2-ORIGIN
L_00047de2:
    mov.l P_00047f90,r5
    .org 0x47de4-ORIGIN
L_00047de4:
    mov.b @(0x9,r4),r0
    .org 0x47de6-ORIGIN
L_00047de6:
    mov.b @r5,r2
    .org 0x47de8-ORIGIN
L_00047de8:
    cmp/hs r2,r0
    .org 0x47dea-ORIGIN
L_00047dea:
    bt L_00047df2
    .org 0x47dec-ORIGIN
L_00047dec:
    mov #0x15,r0
    .org 0x47dee-ORIGIN
L_00047dee:
    bra L_00047df6
    .org 0x47df0-ORIGIN
L_00047df0:
    and.b #0xdf,@(r0,gbr)
    .org 0x47df2-ORIGIN
L_00047df2:
    mov #0x15,r0
    .org 0x47df4-ORIGIN
L_00047df4:
    or.b #0x20,@(r0,gbr)
    .org 0x47df6-ORIGIN
L_00047df6:
    mov.b @(0x14,gbr),r0
    .org 0x47df8-ORIGIN
L_00047df8:
    mov.l P_00047f88,r4
    .org 0x47dfa-ORIGIN
L_00047dfa:
    extu.b r0,r13
    .org 0x47dfc-ORIGIN
L_00047dfc:
    mov r13,r0
    .org 0x47dfe-ORIGIN
L_00047dfe:
    tst #0x2,r0
    .org 0x47e00-ORIGIN
L_00047e00:
    mov.b @(0x9,r4),r0
    .org 0x47e02-ORIGIN
L_00047e02:
    bf/s L_00047e3c
    .org 0x47e04-ORIGIN
L_00047e04:
    extu.b r0,r5
    .org 0x47e06-ORIGIN
L_00047e06:
    mov.l P_00047f94,r6
    .org 0x47e08-ORIGIN
L_00047e08:
    mov.b @r6,r2
    .org 0x47e0a-ORIGIN
L_00047e0a:
    extu.b r2,r2
    .org 0x47e0c-ORIGIN
L_00047e0c:
    cmp/ge r2,r5
    .org 0x47e0e-ORIGIN
L_00047e0e:
    bf L_00047e66
    .org 0x47e10-ORIGIN
L_00047e10:
    mov.l P_00047f98,r5
    .org 0x47e12-ORIGIN
L_00047e12:
    mov.w @r5,r6
    .org 0x47e14-ORIGIN
L_00047e14:
    mov.l P_00047f9c,r5
    .org 0x47e16-ORIGIN
L_00047e16:
    mov.w @r5,r2
    .org 0x47e18-ORIGIN
L_00047e18:
    cmp/hs r2,r6
    .org 0x47e1a-ORIGIN
L_00047e1a:
    bt L_00047e28
    .org 0x47e1c-ORIGIN
L_00047e1c:
    mov.l P_00047fa0,r11
    .org 0x47e1e-ORIGIN
L_00047e1e:
    mov #0x12,r0
    .org 0x47e20-ORIGIN
L_00047e20:
    mov.b @(r0,r12),r4
    .org 0x47e22-ORIGIN
L_00047e22:
    mov.b @r11,r2
    .org 0x47e24-ORIGIN
L_00047e24:
    cmp/hs r2,r4
    .org 0x47e26-ORIGIN
L_00047e26:
    bf L_00047e66
    .org 0x47e28-ORIGIN
L_00047e28:
    mov.l P_00047fa4,r6
    .org 0x47e2a-ORIGIN
L_00047e2a:
    mov #0x5c,r0
    .org 0x47e2c-ORIGIN
L_00047e2c:
    mov.b @(r0,r6),r2
    .org 0x47e2e-ORIGIN
L_00047e2e:
    tst r2,r2
    .org 0x47e30-ORIGIN
L_00047e30:
    bf L_00047e70
    .org 0x47e32-ORIGIN
L_00047e32:
    mov r13,r0
    .org 0x47e34-ORIGIN
L_00047e34:
    or #0x2,r0
    .org 0x47e36-ORIGIN
L_00047e36:
    exts.b r0,r13
    .org 0x47e38-ORIGIN
L_00047e38:
    bra L_00047e70
    .org 0x47e3a-ORIGIN
L_00047e3a:
    mov.b r0,@(0x14,gbr)
    .org 0x47e3c-ORIGIN
L_00047e3c:
    mov.l P_00047fa8,r6
    .org 0x47e3e-ORIGIN
L_00047e3e:
    mov.b @r6,r2
    .org 0x47e40-ORIGIN
L_00047e40:
    extu.b r2,r2
    .org 0x47e42-ORIGIN
L_00047e42:
    cmp/ge r2,r5
    .org 0x47e44-ORIGIN
L_00047e44:
    bf L_00047e5e
    .org 0x47e46-ORIGIN
L_00047e46:
    mov.l P_00047f98,r5
    .org 0x47e48-ORIGIN
L_00047e48:
    mov.w @r5,r6
    .org 0x47e4a-ORIGIN
L_00047e4a:
    mov.l P_00047f9c,r5
    .org 0x47e4c-ORIGIN
L_00047e4c:
    mov.w @r5,r2
    .org 0x47e4e-ORIGIN
L_00047e4e:
    cmp/hs r2,r6
    .org 0x47e50-ORIGIN
L_00047e50:
    bt L_00047e66
    .org 0x47e52-ORIGIN
L_00047e52:
    mov.l P_00047fa0,r11
    .org 0x47e54-ORIGIN
L_00047e54:
    mov #0x12,r0
    .org 0x47e56-ORIGIN
L_00047e56:
    mov.b @(r0,r12),r4
    .org 0x47e58-ORIGIN
L_00047e58:
    mov.b @r11,r2
    .org 0x47e5a-ORIGIN
L_00047e5a:
    cmp/hs r2,r4
    .org 0x47e5c-ORIGIN
L_00047e5c:
    bt L_00047e66
    .org 0x47e5e-ORIGIN
L_00047e5e:
    mov r13,r0
    .org 0x47e60-ORIGIN
L_00047e60:
    and #0xfd,r0
    .org 0x47e62-ORIGIN
L_00047e62:
    exts.b r0,r13
    .org 0x47e64-ORIGIN
L_00047e64:
    mov.b r0,@(0x14,gbr)
    .org 0x47e66-ORIGIN
L_00047e66:
    mov.l P_00047fac,r6
    .org 0x47e68-ORIGIN
L_00047e68:
    mov #0x5c,r0
    .org 0x47e6a-ORIGIN
L_00047e6a:
    mov.b @r6,r2
    .org 0x47e6c-ORIGIN
L_00047e6c:
    mov.l P_00047fa4,r6
    .org 0x47e6e-ORIGIN
L_00047e6e:
    mov.b r2,@(r0,r6)
    .org 0x47e70-ORIGIN
L_00047e70:
    mov r13,r0
    .org 0x47e72-ORIGIN
L_00047e72:
    tst #0x4,r0
    .org 0x47e74-ORIGIN
L_00047e74:
    bf L_00047ea0
    .org 0x47e76-ORIGIN
L_00047e76:
    mov.b @(0xe,gbr),r0
    .org 0x47e78-ORIGIN
L_00047e78:
    tst #0x40,r0
    .org 0x47e7a-ORIGIN
L_00047e7a:
    bf L_00047ea0
    .org 0x47e7c-ORIGIN
L_00047e7c:
    mov r13,r0
    .org 0x47e7e-ORIGIN
L_00047e7e:
    tst #0x1,r0
    .org 0x47e80-ORIGIN
L_00047e80:
    bf L_00047ea0
    .org 0x47e82-ORIGIN
L_00047e82:
    mov.b @(0x15,gbr),r0
    .org 0x47e84-ORIGIN
L_00047e84:
    tst #0x20,r0
    .org 0x47e86-ORIGIN
L_00047e86:
    bf/s L_00047ea0
    .org 0x47e88-ORIGIN
L_00047e88:
    mov r0,r2
    .org 0x47e8a-ORIGIN
L_00047e8a:
    mov r2,r0
    .org 0x47e8c-ORIGIN
L_00047e8c:
    tst #0x10,r0
    .org 0x47e8e-ORIGIN
L_00047e8e:
    bf L_00047ea0
    .org 0x47e90-ORIGIN
L_00047e90:
    tst #0x8,r0
    .org 0x47e92-ORIGIN
L_00047e92:
    bf L_00047ea0
    .org 0x47e94-ORIGIN
L_00047e94:
    mov r13,r0
    .org 0x47e96-ORIGIN
L_00047e96:
    tst #0x2,r0
    .org 0x47e98-ORIGIN
L_00047e98:
    bf L_00047ea0
    .org 0x47e9a-ORIGIN
L_00047e9a:
    mov #0x6a,r0
    .org 0x47e9c-ORIGIN
L_00047e9c:
    bra L_00047ea4
    .org 0x47e9e-ORIGIN
L_00047e9e:
    and.b #0x7f,@(r0,gbr)
    .org 0x47ea0-ORIGIN
L_00047ea0:
    mov #0x6a,r0
    .org 0x47ea2-ORIGIN
L_00047ea2:
    or.b #0x80,@(r0,gbr)
    .org 0x47ea4-ORIGIN
L_00047ea4:
    add #0x4,r15
    .org 0x47ea6-ORIGIN
L_00047ea6:
    ldc.l @r15+,gbr
    .org 0x47ea8-ORIGIN
L_00047ea8:
    lds.l @r15+,pr
    .org 0x47eaa-ORIGIN
L_00047eaa:
    mov.l @r15+,r14
    .org 0x47eac-ORIGIN
L_00047eac:
    mov.l @r15+,r13
    .org 0x47eae-ORIGIN
L_00047eae:
    mov.l @r15+,r12
    .org 0x47eb0-ORIGIN
L_00047eb0:
    rts
    .org 0x47eb2-ORIGIN
L_00047eb2:
    mov.l @r15+,r11
    .org 0x47f84-ORIGIN
P_00047f84:
    .byte 0x00
    .org 0x47f85-ORIGIN
P_00047f85:
    .byte 0x00
    .org 0x47f86-ORIGIN
P_00047f86:
    .byte 0x88
    .org 0x47f87-ORIGIN
P_00047f87:
    .byte 0xb1
    .org 0x47f88-ORIGIN
P_00047f88:
    .byte 0xff
    .org 0x47f89-ORIGIN
P_00047f89:
    .byte 0xff
    .org 0x47f8a-ORIGIN
P_00047f8a:
    .byte 0x10
    .org 0x47f8b-ORIGIN
P_00047f8b:
    .byte 0x68
    .org 0x47f8c-ORIGIN
P_00047f8c:
    .byte 0x00
    .org 0x47f8d-ORIGIN
P_00047f8d:
    .byte 0x00
    .org 0x47f8e-ORIGIN
P_00047f8e:
    .byte 0x8c
    .org 0x47f8f-ORIGIN
P_00047f8f:
    .byte 0xc6
    .org 0x47f90-ORIGIN
P_00047f90:
    .byte 0x00
    .org 0x47f91-ORIGIN
P_00047f91:
    .byte 0x00
    .org 0x47f92-ORIGIN
P_00047f92:
    .byte 0x8c
    .org 0x47f93-ORIGIN
P_00047f93:
    .byte 0xc5
    .org 0x47f94-ORIGIN
P_00047f94:
    .byte 0x00
    .org 0x47f95-ORIGIN
P_00047f95:
    .byte 0x00
    .org 0x47f96-ORIGIN
P_00047f96:
    .byte 0x8c
    .org 0x47f97-ORIGIN
P_00047f97:
    .byte 0x74
    .org 0x47f98-ORIGIN
P_00047f98:
    .byte 0xff
    .org 0x47f99-ORIGIN
P_00047f99:
    .byte 0xff
    .org 0x47f9a-ORIGIN
P_00047f9a:
    .byte 0x10
    .org 0x47f9b-ORIGIN
P_00047f9b:
    .byte 0x24
    .org 0x47f9c-ORIGIN
P_00047f9c:
    .byte 0x00
    .org 0x47f9d-ORIGIN
P_00047f9d:
    .byte 0x00
    .org 0x47f9e-ORIGIN
P_00047f9e:
    .byte 0x95
    .org 0x47f9f-ORIGIN
P_00047f9f:
    .byte 0x36
    .org 0x47fa0-ORIGIN
P_00047fa0:
    .byte 0x00
    .org 0x47fa1-ORIGIN
P_00047fa1:
    .byte 0x00
    .org 0x47fa2-ORIGIN
P_00047fa2:
    .byte 0x88
    .org 0x47fa3-ORIGIN
P_00047fa3:
    .byte 0x91
    .org 0x47fa4-ORIGIN
P_00047fa4:
    .byte 0xff
    .org 0x47fa5-ORIGIN
P_00047fa5:
    .byte 0xff
    .org 0x47fa6-ORIGIN
P_00047fa6:
    .byte 0x42
    .org 0x47fa7-ORIGIN
P_00047fa7:
    .byte 0x58
    .org 0x47fa8-ORIGIN
P_00047fa8:
    .byte 0x00
    .org 0x47fa9-ORIGIN
P_00047fa9:
    .byte 0x00
    .org 0x47faa-ORIGIN
P_00047faa:
    .byte 0x8c
    .org 0x47fab-ORIGIN
P_00047fab:
    .byte 0x75
    .org 0x47fac-ORIGIN
P_00047fac:
    .byte 0x00
    .org 0x47fad-ORIGIN
P_00047fad:
    .byte 0x00
    .org 0x47fae-ORIGIN
P_00047fae:
    .byte 0x8b
    .org 0x47faf-ORIGIN
P_00047faf:
    .byte 0xea
