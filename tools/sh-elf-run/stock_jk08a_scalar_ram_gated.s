! Exact natural scalar flag, indexed RAM and bound-selection paths.
    .text
    .balign 4
    .set ORIGIN,0x83c0
    .org 0x83c1-ORIGIN
P_000083c1:
    .byte 0x2c
    .org 0x89c5-ORIGIN
P_000089c5:
    .byte 0x19
    .org 0x8cf1-ORIGIN
P_00008cf1:
    .byte 0x01
    .org 0x8cf2-ORIGIN
P_00008cf2:
    .byte 0x00
    .org 0x8e1a-ORIGIN
P_00008e1a:
    .byte 0x00
    .org 0x3d45c-ORIGIN
L_0003d45c:
    add #-0x4,r15
    .org 0x3d45e-ORIGIN
L_0003d45e:
    mov.l P_0003d524,r6
    .org 0x3d460-ORIGIN
L_0003d460:
    mov.b @(0x6,r6),r0
    .org 0x3d462-ORIGIN
L_0003d462:
    tst #0x40,r0
    .org 0x3d464-ORIGIN
L_0003d464:
    bf/s L_0003d4a4
    .org 0x3d466-ORIGIN
L_0003d466:
    extu.b r4,r4
    .org 0x3d468-ORIGIN
L_0003d468:
    mov.b @r6,r0
    .org 0x3d46a-ORIGIN
L_0003d46a:
    tst #0x20,r0
    .org 0x3d46c-ORIGIN
L_0003d46c:
    bf L_0003d4a4
    .org 0x3d46e-ORIGIN
L_0003d46e:
    mov.l P_0003d4f8,r2
    .org 0x3d470-ORIGIN
L_0003d470:
    mov.w P_0003d4f0,r0
    .org 0x3d472-ORIGIN
L_0003d472:
    mov.b @(r0,r2),r6
    .org 0x3d474-ORIGIN
L_0003d474:
    mov r4,r2
    .org 0x3d476-ORIGIN
L_0003d476:
    add #0x1,r2
    .org 0x3d478-ORIGIN
L_0003d478:
    extu.b r6,r6
    .org 0x3d47a-ORIGIN
L_0003d47a:
    tst r2,r6
    .org 0x3d47c-ORIGIN
L_0003d47c:
    bt L_0003d4a4
    .org 0x3d47e-ORIGIN
L_0003d47e:
    mov.l P_0003d500,r2
    .org 0x3d480-ORIGIN
L_0003d480:
    mov #-0x46,r6
    .org 0x3d482-ORIGIN
L_0003d482:
    extu.b r6,r6
    .org 0x3d484-ORIGIN
L_0003d484:
    mov.l P_0003d4f8,r7
    .org 0x3d486-ORIGIN
L_0003d486:
    add r6,r2
    .org 0x3d488-ORIGIN
L_0003d488:
    mov.w P_0003d4f2,r6
    .org 0x3d48a-ORIGIN
L_0003d48a:
    mov r4,r0
    .org 0x3d48c-ORIGIN
L_0003d48c:
    mov.b @(r0,r2),r5
    .org 0x3d48e-ORIGIN
L_0003d48e:
    mov r7,r2
    .org 0x3d490-ORIGIN
L_0003d490:
    add r6,r2
    .org 0x3d492-ORIGIN
L_0003d492:
    mov.b @(r0,r2),r6
    .org 0x3d494-ORIGIN
L_0003d494:
    extu.b r5,r5
    .org 0x3d496-ORIGIN
L_0003d496:
    extu.b r6,r6
    .org 0x3d498-ORIGIN
L_0003d498:
    cmp/ge r6,r5
    .org 0x3d49a-ORIGIN
L_0003d49a:
    bt/s L_0003d4a4
    .org 0x3d49c-ORIGIN
L_0003d49c:
    mov.l r5,@r15
    .org 0x3d49e-ORIGIN
L_0003d49e:
    mov.w P_0003d4f2,r2
    .org 0x3d4a0-ORIGIN
L_0003d4a0:
    add r2,r7
    .org 0x3d4a2-ORIGIN
L_0003d4a2:
    mov.b r5,@(r0,r7)
    .org 0x3d4a4-ORIGIN
L_0003d4a4:
    rts
    .org 0x3d4a6-ORIGIN
L_0003d4a6:
    add #0x4,r15
    .org 0x3d4f0-ORIGIN
P_0003d4f0:
    .byte 0x05
    .org 0x3d4f1-ORIGIN
P_0003d4f1:
    .byte 0x7a
    .org 0x3d4f2-ORIGIN
P_0003d4f2:
    .byte 0x05
    .org 0x3d4f3-ORIGIN
P_0003d4f3:
    .byte 0x88
    .org 0x3d4f8-ORIGIN
P_0003d4f8:
    .byte 0xff
    .org 0x3d4f9-ORIGIN
P_0003d4f9:
    .byte 0xff
    .org 0x3d4fa-ORIGIN
P_0003d4fa:
    .byte 0x39
    .org 0x3d4fb-ORIGIN
P_0003d4fb:
    .byte 0xc4
    .org 0x3d500-ORIGIN
P_0003d500:
    .byte 0xff
    .org 0x3d501-ORIGIN
P_0003d501:
    .byte 0xff
    .org 0x3d502-ORIGIN
P_0003d502:
    .byte 0x27
    .org 0x3d503-ORIGIN
P_0003d503:
    .byte 0x7e
    .org 0x3d524-ORIGIN
P_0003d524:
    .byte 0xff
    .org 0x3d525-ORIGIN
P_0003d525:
    .byte 0xff
    .org 0x3d526-ORIGIN
P_0003d526:
    .byte 0x41
    .org 0x3d527-ORIGIN
P_0003d527:
    .byte 0x7f
    .org 0x44448-ORIGIN
L_00044448:
    mov.l r10,@-r15
    .org 0x4444a-ORIGIN
L_0004444a:
    mov.l r11,@-r15
    .org 0x4444c-ORIGIN
L_0004444c:
    mov.l r13,@-r15
    .org 0x4444e-ORIGIN
L_0004444e:
    stc.l gbr,@-r15
    .org 0x44450-ORIGIN
L_00044450:
    mov.l P_000444c0,r0
    .org 0x44452-ORIGIN
L_00044452:
    ldc r0,gbr
    .org 0x44454-ORIGIN
L_00044454:
    mov.l P_000444c4,r10
    .org 0x44456-ORIGIN
L_00044456:
    mov.w P_000444ba,r0
    .org 0x44458-ORIGIN
L_00044458:
    mov.l P_000444c8,r1
    .org 0x4445a-ORIGIN
L_0004445a:
    mov.b @(r0,r10),r2
    .org 0x4445c-ORIGIN
L_0004445c:
    mov.b @(0x9,r1),r0
    .org 0x4445e-ORIGIN
L_0004445e:
    mov.l P_000444cc,r7
    .org 0x44460-ORIGIN
L_00044460:
    extu.b r2,r2
    .org 0x44462-ORIGIN
L_00044462:
    mov r0,r6
    .org 0x44464-ORIGIN
L_00044464:
    mov r2,r11
    .org 0x44466-ORIGIN
L_00044466:
    mov.b @(0x1,r7),r0
    .org 0x44468-ORIGIN
L_00044468:
    shll2 r11
    .org 0x4446a-ORIGIN
L_0004446a:
    add r2,r11
    .org 0x4446c-ORIGIN
L_0004446c:
    mov r0,r13
    .org 0x4446e-ORIGIN
L_0004446e:
    mov.b @(0x3,gbr),r0
    .org 0x44470-ORIGIN
L_00044470:
    shll r11
    .org 0x44472-ORIGIN
L_00044472:
    cmp/hs r13,r6
    .org 0x44474-ORIGIN
L_00044474:
    bf/s L_000444aa
    .org 0x44476-ORIGIN
L_00044476:
    mov r0,r4
    .org 0x44478-ORIGIN
L_00044478:
    mov.w P_000444bc,r0
    .org 0x4447a-ORIGIN
L_0004447a:
    mov.b @(r0,r10),r5
    .org 0x4447c-ORIGIN
L_0004447c:
    extu.b r5,r5
    .org 0x4447e-ORIGIN
L_0004447e:
    mov r5,r0
    .org 0x44480-ORIGIN
L_00044480:
    cmp/eq #0x1,r0
    .org 0x44482-ORIGIN
L_00044482:
    bt L_000444aa
    .org 0x44484-ORIGIN
L_00044484:
    mov.b @(0x9,r1),r0
    .org 0x44486-ORIGIN
L_00044486:
    mov.b @r7,r2
    .org 0x44488-ORIGIN
L_00044488:
    cmp/hs r2,r0
    .org 0x4448a-ORIGIN
L_0004448a:
    bf L_0004449e
    .org 0x4448c-ORIGIN
L_0004448c:
    tst r5,r5
    .org 0x4448e-ORIGIN
L_0004448e:
    bf L_0004449e
    .org 0x44490-ORIGIN
L_00044490:
    mov #0x58,r0
    .org 0x44492-ORIGIN
L_00044492:
    mov.l @(r0,r1),r2
    .org 0x44494-ORIGIN
L_00044494:
    cmp/hi r11,r2
    .org 0x44496-ORIGIN
L_00044496:
    bf L_0004449e
    .org 0x44498-ORIGIN
L_00044498:
    mov r4,r0
    .org 0x4449a-ORIGIN
L_0004449a:
    bra L_000444ae
    .org 0x4449c-ORIGIN
L_0004449c:
    or #0x18,r0
    .org 0x4449e-ORIGIN
L_0004449e:
    mov r4,r0
    .org 0x444a0-ORIGIN
L_000444a0:
    or #0x8,r0
    .org 0x444a2-ORIGIN
L_000444a2:
    mov.b r0,@(0x3,gbr)
    .org 0x444a4-ORIGIN
L_000444a4:
    mov #0x3,r0
    .org 0x444a6-ORIGIN
L_000444a6:
    bra L_000444b0
    .org 0x444a8-ORIGIN
L_000444a8:
    and.b #0xef,@(r0,gbr)
    .org 0x444aa-ORIGIN
L_000444aa:
    mov r4,r0
    .org 0x444ac-ORIGIN
L_000444ac:
    and #0xe7,r0
    .org 0x444ae-ORIGIN
L_000444ae:
    mov.b r0,@(0x3,gbr)
    .org 0x444b0-ORIGIN
L_000444b0:
    ldc.l @r15+,gbr
    .org 0x444b2-ORIGIN
L_000444b2:
    mov.l @r15+,r13
    .org 0x444b4-ORIGIN
L_000444b4:
    mov.l @r15+,r11
    .org 0x444b6-ORIGIN
L_000444b6:
    rts
    .org 0x444b8-ORIGIN
L_000444b8:
    mov.l @r15+,r10
    .org 0x444ba-ORIGIN
P_000444ba:
    .byte 0x06
    .org 0x444bb-ORIGIN
P_000444bb:
    .byte 0xcc
    .org 0x444bc-ORIGIN
P_000444bc:
    .byte 0x05
    .org 0x444bd-ORIGIN
P_000444bd:
    .byte 0xb0
    .org 0x444c0-ORIGIN
P_000444c0:
    .byte 0xff
    .org 0x444c1-ORIGIN
P_000444c1:
    .byte 0xff
    .org 0x444c2-ORIGIN
P_000444c2:
    .byte 0x24
    .org 0x444c3-ORIGIN
P_000444c3:
    .byte 0xce
    .org 0x444c4-ORIGIN
P_000444c4:
    .byte 0xff
    .org 0x444c5-ORIGIN
P_000444c5:
    .byte 0xff
    .org 0x444c6-ORIGIN
P_000444c6:
    .byte 0x12
    .org 0x444c7-ORIGIN
P_000444c7:
    .byte 0x8c
    .org 0x444c8-ORIGIN
P_000444c8:
    .byte 0xff
    .org 0x444c9-ORIGIN
P_000444c9:
    .byte 0xff
    .org 0x444ca-ORIGIN
P_000444ca:
    .byte 0x10
    .org 0x444cb-ORIGIN
P_000444cb:
    .byte 0x68
    .org 0x444cc-ORIGIN
P_000444cc:
    .byte 0x00
    .org 0x444cd-ORIGIN
P_000444cd:
    .byte 0x00
    .org 0x444ce-ORIGIN
P_000444ce:
    .byte 0x8c
    .org 0x444cf-ORIGIN
P_000444cf:
    .byte 0xf1
    .org 0x74c08-ORIGIN
L_00074c08:
    sts.l macl,@-r15
    .org 0x74c0a-ORIGIN
L_00074c0a:
    mov.l P_00074d38,r6
    .org 0x74c0c-ORIGIN
L_00074c0c:
    mov.b @r6,r0
    .org 0x74c0e-ORIGIN
L_00074c0e:
    tst #0x8,r0
    .org 0x74c10-ORIGIN
L_00074c10:
    bf L_00074c74
    .org 0x74c12-ORIGIN
L_00074c12:
    mov.l P_00074d48,r6
    .org 0x74c14-ORIGIN
L_00074c14:
    mov #0x2b,r0
    .org 0x74c16-ORIGIN
L_00074c16:
    mov.b @(r0,r6),r0
    .org 0x74c18-ORIGIN
L_00074c18:
    tst #0x1,r0
    .org 0x74c1a-ORIGIN
L_00074c1a:
    bf L_00074c74
    .org 0x74c1c-ORIGIN
L_00074c1c:
    mov.l P_00074d4c,r6
    .org 0x74c1e-ORIGIN
L_00074c1e:
    mov.b @(0x3,r6),r0
    .org 0x74c20-ORIGIN
L_00074c20:
    tst #0x80,r0
    .org 0x74c22-ORIGIN
L_00074c22:
    bf L_00074c74
    .org 0x74c24-ORIGIN
L_00074c24:
    mov.l P_00074d24,r2
    .org 0x74c26-ORIGIN
L_00074c26:
    mov #0x66,r0
    .org 0x74c28-ORIGIN
L_00074c28:
    mov.w @(r0,r2),r5
    .org 0x74c2a-ORIGIN
L_00074c2a:
    extu.w r5,r5
    .org 0x74c2c-ORIGIN
L_00074c2c:
    tst r5,r5
    .org 0x74c2e-ORIGIN
L_00074c2e:
    bf L_00074c38
    .org 0x74c30-ORIGIN
L_00074c30:
    mov.l P_00074d28,r4
    .org 0x74c32-ORIGIN
L_00074c32:
    mov.w P_00074c4e,r0
    .org 0x74c34-ORIGIN
L_00074c34:
    bra L_00074c7a
    .org 0x74c36-ORIGIN
L_00074c36:
    mov.w @(r0,r4),r2
    .org 0x74c38-ORIGIN
L_00074c38:
    mov #-0x1,r6
    .org 0x74c3a-ORIGIN
L_00074c3a:
    extu.w r6,r6
    .org 0x74c3c-ORIGIN
L_00074c3c:
    cmp/eq r6,r5
    .org 0x74c3e-ORIGIN
L_00074c3e:
    bf L_00074c54
    .org 0x74c40-ORIGIN
L_00074c40:
    mov.l P_00074d28,r4
    .org 0x74c42-ORIGIN
L_00074c42:
    mov.w P_00074c52,r0
    .org 0x74c44-ORIGIN
L_00074c44:
    bra L_00074c7a
    .org 0x74c46-ORIGIN
L_00074c46:
    mov.w @(r0,r4),r2
    .org 0x74c4e-ORIGIN
P_00074c4e:
    .byte 0x06
    .org 0x74c4f-ORIGIN
P_00074c4f:
    .byte 0x5c
    .org 0x74c52-ORIGIN
P_00074c52:
    .byte 0x06
    .org 0x74c53-ORIGIN
P_00074c53:
    .byte 0x5a
    .org 0x74c54-ORIGIN
L_00074c54:
    mov.l P_00074d28,r4
    .org 0x74c56-ORIGIN
L_00074c56:
    mov #0x1,r2
    .org 0x74c58-ORIGIN
L_00074c58:
    mov.w P_00074d1c,r0
    .org 0x74c5a-ORIGIN
L_00074c5a:
    shll16 r2
    .org 0x74c5c-ORIGIN
L_00074c5c:
    sub r5,r2
    .org 0x74c5e-ORIGIN
L_00074c5e:
    mov.w @(r0,r4),r6
    .org 0x74c60-ORIGIN
L_00074c60:
    mov.w P_00074d1e,r0
    .org 0x74c62-ORIGIN
L_00074c62:
    mul.l r6,r2
    .org 0x74c64-ORIGIN
L_00074c64:
    mov.w @(r0,r4),r2
    .org 0x74c66-ORIGIN
L_00074c66:
    sts macl,r6
    .org 0x74c68-ORIGIN
L_00074c68:
    mul.l r2,r5
    .org 0x74c6a-ORIGIN
L_00074c6a:
    sts macl,r2
    .org 0x74c6c-ORIGIN
L_00074c6c:
    add r2,r6
    .org 0x74c6e-ORIGIN
L_00074c6e:
    swap.w r6,r2
    .org 0x74c70-ORIGIN
L_00074c70:
    bra L_00074c7a
    .org 0x74c72-ORIGIN
L_00074c72:
    exts.w r2,r2
    .org 0x74c74-ORIGIN
L_00074c74:
    mov.l P_00074d28,r4
    .org 0x74c76-ORIGIN
L_00074c76:
    mov.w P_00074d1c,r0
    .org 0x74c78-ORIGIN
L_00074c78:
    mov.w @(r0,r4),r2
    .org 0x74c7a-ORIGIN
L_00074c7a:
    mov.w P_00074d20,r0
    .org 0x74c7c-ORIGIN
L_00074c7c:
    mov.w r2,@(r0,r4)
    .org 0x74c7e-ORIGIN
L_00074c7e:
    rts
    .org 0x74c80-ORIGIN
L_00074c80:
    lds.l @r15+,macl
    .org 0x74d1c-ORIGIN
P_00074d1c:
    .byte 0x06
    .org 0x74d1d-ORIGIN
P_00074d1d:
    .byte 0x5c
    .org 0x74d1e-ORIGIN
P_00074d1e:
    .byte 0x06
    .org 0x74d1f-ORIGIN
P_00074d1f:
    .byte 0x5a
    .org 0x74d20-ORIGIN
P_00074d20:
    .byte 0x06
    .org 0x74d21-ORIGIN
P_00074d21:
    .byte 0x68
    .org 0x74d24-ORIGIN
P_00074d24:
    .byte 0xff
    .org 0x74d25-ORIGIN
P_00074d25:
    .byte 0xff
    .org 0x74d26-ORIGIN
P_00074d26:
    .byte 0x23
    .org 0x74d27-ORIGIN
P_00074d27:
    .byte 0xbc
    .org 0x74d28-ORIGIN
P_00074d28:
    .byte 0xff
    .org 0x74d29-ORIGIN
P_00074d29:
    .byte 0xff
    .org 0x74d2a-ORIGIN
P_00074d2a:
    .byte 0x12
    .org 0x74d2b-ORIGIN
P_00074d2b:
    .byte 0x8c
    .org 0x74d38-ORIGIN
P_00074d38:
    .byte 0xff
    .org 0x74d39-ORIGIN
P_00074d39:
    .byte 0xff
    .org 0x74d3a-ORIGIN
P_00074d3a:
    .byte 0x41
    .org 0x74d3b-ORIGIN
P_00074d3b:
    .byte 0x7e
    .org 0x74d48-ORIGIN
P_00074d48:
    .byte 0xff
    .org 0x74d49-ORIGIN
P_00074d49:
    .byte 0xff
    .org 0x74d4a-ORIGIN
P_00074d4a:
    .byte 0x24
    .org 0x74d4b-ORIGIN
P_00074d4b:
    .byte 0x70
    .org 0x74d4c-ORIGIN
P_00074d4c:
    .byte 0xff
    .org 0x74d4d-ORIGIN
P_00074d4d:
    .byte 0xff
    .org 0x74d4e-ORIGIN
P_00074d4e:
    .byte 0x24
    .org 0x74d4f-ORIGIN
P_00074d4f:
    .byte 0x5c
    .org 0x777fa-ORIGIN
L_000777fa:
    mov.l r13,@-r15
    .org 0x777fc-ORIGIN
L_000777fc:
    mov.l r14,@-r15
    .org 0x777fe-ORIGIN
L_000777fe:
    mov.l P_00077910,r1
    .org 0x77800-ORIGIN
L_00077800:
    mov.w P_0007787c,r0
    .org 0x77802-ORIGIN
L_00077802:
    mov.l P_00077914,r2
    .org 0x77804-ORIGIN
L_00077804:
    mov.w @(r0,r1),r13
    .org 0x77806-ORIGIN
L_00077806:
    mov.w P_0007787e,r0
    .org 0x77808-ORIGIN
L_00077808:
    mov.w @(r0,r1),r7
    .org 0x7780a-ORIGIN
L_0007780a:
    mov.w P_00077880,r0
    .org 0x7780c-ORIGIN
L_0007780c:
    mov.w @(r0,r1),r5
    .org 0x7780e-ORIGIN
L_0007780e:
    mov.w P_00077882,r0
    .org 0x77810-ORIGIN
L_00077810:
    mov.w @(r0,r1),r14
    .org 0x77812-ORIGIN
L_00077812:
    mov.b @r2,r0
    .org 0x77814-ORIGIN
L_00077814:
    tst #0x1,r0
    .org 0x77816-ORIGIN
L_00077816:
    bf L_00077864
    .org 0x77818-ORIGIN
L_00077818:
    mov.l P_00077918,r2
    .org 0x7781a-ORIGIN
L_0007781a:
    mov.l P_0007791c,r4
    .org 0x7781c-ORIGIN
L_0007781c:
    mov.b @r2,r0
    .org 0x7781e-ORIGIN
L_0007781e:
    and #0x1,r0
    .org 0x77820-ORIGIN
L_00077820:
    mov r0,r6
    .org 0x77822-ORIGIN
L_00077822:
    mov.b @(0x1,r4),r0
    .org 0x77824-ORIGIN
L_00077824:
    tst #0x8,r0
    .org 0x77826-ORIGIN
L_00077826:
    bt L_00077850
    .org 0x77828-ORIGIN
L_00077828:
    tst r6,r6
    .org 0x7782a-ORIGIN
L_0007782a:
    bt L_00077834
    .org 0x7782c-ORIGIN
L_0007782c:
    mov.l P_00077920,r5
    .org 0x7782e-ORIGIN
L_0007782e:
    mov #0x3e,r0
    .org 0x77830-ORIGIN
L_00077830:
    bra L_00077838
    .org 0x77832-ORIGIN
L_00077832:
    mov.w @(r0,r5),r13
    .org 0x77834-ORIGIN
L_00077834:
    mov.w P_00077884,r0
    .org 0x77836-ORIGIN
L_00077836:
    mov.w @(r0,r1),r13
    .org 0x77838-ORIGIN
L_00077838:
    mov.w P_00077886,r0
    .org 0x7783a-ORIGIN
L_0007783a:
    mov.l P_00077920,r5
    .org 0x7783c-ORIGIN
L_0007783c:
    mov.w @(r0,r1),r7
    .org 0x7783e-ORIGIN
L_0007783e:
    mov #0x3e,r0
    .org 0x77840-ORIGIN
L_00077840:
    mov.w @(r0,r5),r6
    .org 0x77842-ORIGIN
L_00077842:
    cmp/gt r7,r6
    .org 0x77844-ORIGIN
L_00077844:
    bt L_00077848
    .org 0x77846-ORIGIN
L_00077846:
    mov r6,r7
    .org 0x77848-ORIGIN
L_00077848:
    mov.w P_00077888,r0
    .org 0x7784a-ORIGIN
L_0007784a:
    mov.w @(r0,r1),r5
    .org 0x7784c-ORIGIN
L_0007784c:
    bra L_00077864
    .org 0x7784e-ORIGIN
L_0007784e:
    mov r5,r14
    .org 0x77850-ORIGIN
L_00077850:
    tst r6,r6
    .org 0x77852-ORIGIN
L_00077852:
    bf L_00077858
    .org 0x77854-ORIGIN
L_00077854:
    mov.w P_00077884,r0
    .org 0x77856-ORIGIN
L_00077856:
    mov.w @(r0,r1),r13
    .org 0x77858-ORIGIN
L_00077858:
    mov.w P_00077886,r0
    .org 0x7785a-ORIGIN
L_0007785a:
    mov.w @(r0,r1),r2
    .org 0x7785c-ORIGIN
L_0007785c:
    cmp/gt r2,r7
    .org 0x7785e-ORIGIN
L_0007785e:
    bt L_00077862
    .org 0x77860-ORIGIN
L_00077860:
    mov r7,r2
    .org 0x77862-ORIGIN
L_00077862:
    mov r2,r7
    .org 0x77864-ORIGIN
L_00077864:
    mov.w P_0007788a,r0
    .org 0x77866-ORIGIN
L_00077866:
    mov.w r13,@(r0,r1)
    .org 0x77868-ORIGIN
L_00077868:
    mov.w P_0007788c,r0
    .org 0x7786a-ORIGIN
L_0007786a:
    mov.w r7,@(r0,r1)
    .org 0x7786c-ORIGIN
L_0007786c:
    mov.w P_0007788e,r0
    .org 0x7786e-ORIGIN
L_0007786e:
    mov.w r5,@(r0,r1)
    .org 0x77870-ORIGIN
L_00077870:
    mov.w P_00077890,r0
    .org 0x77872-ORIGIN
L_00077872:
    mov.w r14,@(r0,r1)
    .org 0x77874-ORIGIN
L_00077874:
    mov.l @r15+,r14
    .org 0x77876-ORIGIN
L_00077876:
    rts
    .org 0x77878-ORIGIN
L_00077878:
    mov.l @r15+,r13
    .org 0x7787c-ORIGIN
P_0007787c:
    .byte 0x0b
    .org 0x7787d-ORIGIN
P_0007787d:
    .byte 0x90
    .org 0x7787e-ORIGIN
P_0007787e:
    .byte 0x0b
    .org 0x7787f-ORIGIN
P_0007787f:
    .byte 0x94
    .org 0x77880-ORIGIN
P_00077880:
    .byte 0x0b
    .org 0x77881-ORIGIN
P_00077881:
    .byte 0x8e
    .org 0x77882-ORIGIN
P_00077882:
    .byte 0x0b
    .org 0x77883-ORIGIN
P_00077883:
    .byte 0x92
    .org 0x77884-ORIGIN
P_00077884:
    .byte 0x0b
    .org 0x77885-ORIGIN
P_00077885:
    .byte 0xa8
    .org 0x77886-ORIGIN
P_00077886:
    .byte 0x0b
    .org 0x77887-ORIGIN
P_00077887:
    .byte 0xd0
    .org 0x77888-ORIGIN
P_00077888:
    .byte 0x0b
    .org 0x77889-ORIGIN
P_00077889:
    .byte 0xa4
    .org 0x7788a-ORIGIN
P_0007788a:
    .byte 0x0b
    .org 0x7788b-ORIGIN
P_0007788b:
    .byte 0x88
    .org 0x7788c-ORIGIN
P_0007788c:
    .byte 0x0b
    .org 0x7788d-ORIGIN
P_0007788d:
    .byte 0x8c
    .org 0x7788e-ORIGIN
P_0007788e:
    .byte 0x0b
    .org 0x7788f-ORIGIN
P_0007788f:
    .byte 0x86
    .org 0x77890-ORIGIN
P_00077890:
    .byte 0x0b
    .org 0x77891-ORIGIN
P_00077891:
    .byte 0x8a
    .org 0x77910-ORIGIN
P_00077910:
    .byte 0xff
    .org 0x77911-ORIGIN
P_00077911:
    .byte 0xff
    .org 0x77912-ORIGIN
P_00077912:
    .byte 0x28
    .org 0x77913-ORIGIN
P_00077913:
    .byte 0xf8
    .org 0x77914-ORIGIN
P_00077914:
    .byte 0x00
    .org 0x77915-ORIGIN
P_00077915:
    .byte 0x00
    .org 0x77916-ORIGIN
P_00077916:
    .byte 0x83
    .org 0x77917-ORIGIN
P_00077917:
    .byte 0xc1
    .org 0x77918-ORIGIN
P_00077918:
    .byte 0x00
    .org 0x77919-ORIGIN
P_00077919:
    .byte 0x00
    .org 0x7791a-ORIGIN
P_0007791a:
    .byte 0x89
    .org 0x7791b-ORIGIN
P_0007791b:
    .byte 0xc5
    .org 0x7791c-ORIGIN
P_0007791c:
    .byte 0xff
    .org 0x7791d-ORIGIN
P_0007791d:
    .byte 0xff
    .org 0x7791e-ORIGIN
P_0007791e:
    .byte 0x41
    .org 0x7791f-ORIGIN
P_0007791f:
    .byte 0xa5
    .org 0x77920-ORIGIN
P_00077920:
    .byte 0xff
    .org 0x77921-ORIGIN
P_00077921:
    .byte 0xff
    .org 0x77922-ORIGIN
P_00077922:
    .byte 0x41
    .org 0x77923-ORIGIN
P_00077923:
    .byte 0x24
    .org 0x907e8-ORIGIN
L_000907e8:
    extu.b r4,r4
    .org 0x907ea-ORIGIN
L_000907ea:
    extu.b r5,r1
    .org 0x907ec-ORIGIN
L_000907ec:
    tst r4,r4
    .org 0x907ee-ORIGIN
L_000907ee:
    mov r1,r7
    .org 0x907f0-ORIGIN
L_000907f0:
    bt/s L_00090854
    .org 0x907f2-ORIGIN
L_000907f2:
    add #0x1,r7
    .org 0x907f4-ORIGIN
L_000907f4:
    mov.l P_00090a5c,r6
    .org 0x907f6-ORIGIN
L_000907f6:
    mov.b @(0x3,r6),r0
    .org 0x907f8-ORIGIN
L_000907f8:
    mov #-0x80,r6
    .org 0x907fa-ORIGIN
L_000907fa:
    extu.b r6,r6
    .org 0x907fc-ORIGIN
L_000907fc:
    extu.b r0,r2
    .org 0x907fe-ORIGIN
L_000907fe:
    cmp/eq r6,r2
    .org 0x90800-ORIGIN
L_00090800:
    bf L_00090854
    .org 0x90802-ORIGIN
L_00090802:
    mov.l P_00090a60,r4
    .org 0x90804-ORIGIN
L_00090804:
    mov r1,r0
    .org 0x90806-ORIGIN
L_00090806:
    mov.w P_0009092a,r2
    .org 0x90808-ORIGIN
L_00090808:
    shll r0
    .org 0x9080a-ORIGIN
L_0009080a:
    mov r4,r5
    .org 0x9080c-ORIGIN
L_0009080c:
    add r2,r5
    .org 0x9080e-ORIGIN
L_0009080e:
    mov.w @(r0,r5),r2
    .org 0x90810-ORIGIN
L_00090810:
    tst r2,r2
    .org 0x90812-ORIGIN
L_00090812:
    bf L_00090854
    .org 0x90814-ORIGIN
L_00090814:
    mov.l P_00090a64,r2
    .org 0x90816-ORIGIN
L_00090816:
    mov r1,r0
    .org 0x90818-ORIGIN
L_00090818:
    add #0x6f,r2
    .org 0x9081a-ORIGIN
L_0009081a:
    mov.b @(r0,r2),r6
    .org 0x9081c-ORIGIN
L_0009081c:
    tst r6,r6
    .org 0x9081e-ORIGIN
L_0009081e:
    bf L_0009083e
    .org 0x90820-ORIGIN
L_00090820:
    mov.l P_00090a60,r5
    .org 0x90822-ORIGIN
L_00090822:
    mov r1,r2
    .org 0x90824-ORIGIN
L_00090824:
    mov.w P_0009092c,r0
    .org 0x90826-ORIGIN
L_00090826:
    add #0x1,r2
    .org 0x90828-ORIGIN
L_00090828:
    mov.b @(r0,r5),r6
    .org 0x9082a-ORIGIN
L_0009082a:
    extu.b r6,r6
    .org 0x9082c-ORIGIN
L_0009082c:
    tst r2,r6
    .org 0x9082e-ORIGIN
L_0009082e:
    bt L_0009087a
    .org 0x90830-ORIGIN
L_00090830:
    mov.w P_0009092e,r2
    .org 0x90832-ORIGIN
L_00090832:
    mov r1,r0
    .org 0x90834-ORIGIN
L_00090834:
    add r2,r4
    .org 0x90836-ORIGIN
L_00090836:
    mov #0x0,r2
    .org 0x90838-ORIGIN
L_00090838:
    mov.b r2,@(r0,r4)
    .org 0x9083a-ORIGIN
L_0009083a:
    bra L_0009084a
    .org 0x9083c-ORIGIN
L_0009083c:
    not r7,r2
    .org 0x9083e-ORIGIN
L_0009083e:
    mov.w P_0009092e,r2
    .org 0x90840-ORIGIN
L_00090840:
    mov.l P_00090a60,r5
    .org 0x90842-ORIGIN
L_00090842:
    add r2,r4
    .org 0x90844-ORIGIN
L_00090844:
    mov #0x0,r2
    .org 0x90846-ORIGIN
L_00090846:
    mov.b r2,@(r0,r4)
    .org 0x90848-ORIGIN
L_00090848:
    not r7,r2
    .org 0x9084a-ORIGIN
L_0009084a:
    mov.w P_00090930,r0
    .org 0x9084c-ORIGIN
L_0009084c:
    mov.b @(r0,r5),r6
    .org 0x9084e-ORIGIN
L_0009084e:
    and r2,r6
    .org 0x90850-ORIGIN
L_00090850:
    rts
    .org 0x90852-ORIGIN
L_00090852:
    mov.b r6,@(r0,r5)
    .org 0x90854-ORIGIN
L_00090854:
    mov.l P_00090a60,r2
    .org 0x90856-ORIGIN
L_00090856:
    mov r1,r0
    .org 0x90858-ORIGIN
L_00090858:
    mov.w P_0009092e,r6
    .org 0x9085a-ORIGIN
L_0009085a:
    mov.l P_00090a60,r5
    .org 0x9085c-ORIGIN
L_0009085c:
    add r6,r2
    .org 0x9085e-ORIGIN
L_0009085e:
    mov #0x0,r6
    .org 0x90860-ORIGIN
L_00090860:
    mov.b r6,@(r0,r2)
    .org 0x90862-ORIGIN
L_00090862:
    not r7,r2
    .org 0x90864-ORIGIN
L_00090864:
    mov.w P_00090930,r0
    .org 0x90866-ORIGIN
L_00090866:
    mov.b @(r0,r5),r6
    .org 0x90868-ORIGIN
L_00090868:
    and r2,r6
    .org 0x9086a-ORIGIN
L_0009086a:
    mov.l P_00090a64,r2
    .org 0x9086c-ORIGIN
L_0009086c:
    mov.b r6,@(r0,r5)
    .org 0x9086e-ORIGIN
L_0009086e:
    mov r1,r0
    .org 0x90870-ORIGIN
L_00090870:
    mov.l P_00090a68,r5
    .org 0x90872-ORIGIN
L_00090872:
    add #0x6f,r2
    .org 0x90874-ORIGIN
L_00090874:
    mov.b @r5,r6
    .org 0x90876-ORIGIN
L_00090876:
    rts
    .org 0x90878-ORIGIN
L_00090878:
    mov.b r6,@(r0,r2)
    .org 0x9087a-ORIGIN
L_0009087a:
    mov.w P_00090930,r0
    .org 0x9087c-ORIGIN
L_0009087c:
    mov.b @(r0,r5),r2
    .org 0x9087e-ORIGIN
L_0009087e:
    or r7,r2
    .org 0x90880-ORIGIN
L_00090880:
    rts
    .org 0x90882-ORIGIN
L_00090882:
    mov.b r2,@(r0,r5)
    .org 0x9092a-ORIGIN
P_0009092a:
    .byte 0x08
    .org 0x9092b-ORIGIN
P_0009092b:
    .byte 0x20
    .org 0x9092c-ORIGIN
P_0009092c:
    .byte 0x02
    .org 0x9092d-ORIGIN
P_0009092d:
    .byte 0x2c
    .org 0x9092e-ORIGIN
P_0009092e:
    .byte 0x06
    .org 0x9092f-ORIGIN
P_0009092f:
    .byte 0xa4
    .org 0x90930-ORIGIN
P_00090930:
    .byte 0x02
    .org 0x90931-ORIGIN
P_00090931:
    .byte 0x64
    .org 0x90a5c-ORIGIN
P_00090a5c:
    .byte 0xff
    .org 0x90a5d-ORIGIN
P_00090a5d:
    .byte 0xff
    .org 0x90a5e-ORIGIN
P_00090a5e:
    .byte 0x23
    .org 0x90a5f-ORIGIN
P_00090a5f:
    .byte 0x24
    .org 0x90a60-ORIGIN
P_00090a60:
    .byte 0xff
    .org 0x90a61-ORIGIN
P_00090a61:
    .byte 0xff
    .org 0x90a62-ORIGIN
P_00090a62:
    .byte 0x12
    .org 0x90a63-ORIGIN
P_00090a63:
    .byte 0x8c
    .org 0x90a64-ORIGIN
P_00090a64:
    .byte 0xff
    .org 0x90a65-ORIGIN
P_00090a65:
    .byte 0xff
    .org 0x90a66-ORIGIN
P_00090a66:
    .byte 0x24
    .org 0x90a67-ORIGIN
P_00090a67:
    .byte 0xf9
    .org 0x90a68-ORIGIN
P_00090a68:
    .byte 0x00
    .org 0x90a69-ORIGIN
P_00090a69:
    .byte 0x00
    .org 0x90a6a-ORIGIN
P_00090a6a:
    .byte 0x8e
    .org 0x90a6b-ORIGIN
P_00090a6b:
    .byte 0x1a
