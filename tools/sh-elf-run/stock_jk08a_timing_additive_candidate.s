! Complete stock timing additive candidate builder and all real arithmetic helpers.
    .text
    .balign 4
    .set ORIGIN,0x21ce0
    .org 0x21ce0-ORIGIN
L_00021ce0:
    mov.l r2,@-r15
    .org 0x21ce2-ORIGIN
L_00021ce2:
    tst r0,r0
    .org 0x21ce4-ORIGIN
L_00021ce4:
    bt L_00021d6a
    .org 0x21ce6-ORIGIN
L_00021ce6:
    extu.w r0,r2
    .org 0x21ce8-ORIGIN
L_00021ce8:
    cmp/eq r2,r0
    .org 0x21cea-ORIGIN
L_00021cea:
    bf L_00021d76
    .org 0x21cec-ORIGIN
L_00021cec:
    div0u
    .org 0x21cee-ORIGIN
L_00021cee:
    shll8 r0
    .org 0x21cf0-ORIGIN
L_00021cf0:
    cmp/hi r1,r0
    .org 0x21cf2-ORIGIN
L_00021cf2:
    bf L_00021d0c
    .org 0x21cf4-ORIGIN
L_00021cf4:
    div1 r0,r1
    .org 0x21cf6-ORIGIN
L_00021cf6:
    div1 r0,r1
    .org 0x21cf8-ORIGIN
L_00021cf8:
    div1 r0,r1
    .org 0x21cfa-ORIGIN
L_00021cfa:
    div1 r0,r1
    .org 0x21cfc-ORIGIN
L_00021cfc:
    div1 r0,r1
    .org 0x21cfe-ORIGIN
L_00021cfe:
    div1 r0,r1
    .org 0x21d00-ORIGIN
L_00021d00:
    div1 r0,r1
    .org 0x21d02-ORIGIN
L_00021d02:
    div1 r0,r1
    .org 0x21d04-ORIGIN
L_00021d04:
    rotcl r1
    .org 0x21d06-ORIGIN
L_00021d06:
    mov.l @r15+,r2
    .org 0x21d08-ORIGIN
L_00021d08:
    rts
    .org 0x21d0a-ORIGIN
L_00021d0a:
    extu.b r1,r0
    .org 0x21d0c-ORIGIN
L_00021d0c:
    mov.l r3,@-r15
    .org 0x21d0e-ORIGIN
L_00021d0e:
    extu.w r1,r3
    .org 0x21d10-ORIGIN
L_00021d10:
    shll8 r0
    .org 0x21d12-ORIGIN
L_00021d12:
    shlr16 r1
    .org 0x21d14-ORIGIN
L_00021d14:
    div1 r0,r1
    .org 0x21d16-ORIGIN
L_00021d16:
    div1 r0,r1
    .org 0x21d18-ORIGIN
L_00021d18:
    div1 r0,r1
    .org 0x21d1a-ORIGIN
L_00021d1a:
    div1 r0,r1
    .org 0x21d1c-ORIGIN
L_00021d1c:
    div1 r0,r1
    .org 0x21d1e-ORIGIN
L_00021d1e:
    div1 r0,r1
    .org 0x21d20-ORIGIN
L_00021d20:
    div1 r0,r1
    .org 0x21d22-ORIGIN
L_00021d22:
    div1 r0,r1
    .org 0x21d24-ORIGIN
L_00021d24:
    div1 r0,r1
    .org 0x21d26-ORIGIN
L_00021d26:
    div1 r0,r1
    .org 0x21d28-ORIGIN
L_00021d28:
    div1 r0,r1
    .org 0x21d2a-ORIGIN
L_00021d2a:
    div1 r0,r1
    .org 0x21d2c-ORIGIN
L_00021d2c:
    div1 r0,r1
    .org 0x21d2e-ORIGIN
L_00021d2e:
    div1 r0,r1
    .org 0x21d30-ORIGIN
L_00021d30:
    div1 r0,r1
    .org 0x21d32-ORIGIN
L_00021d32:
    div1 r0,r1
    .org 0x21d34-ORIGIN
L_00021d34:
    extu.w r1,r2
    .org 0x21d36-ORIGIN
L_00021d36:
    xor r2,r1
    .org 0x21d38-ORIGIN
L_00021d38:
    addc r2,r2
    .org 0x21d3a-ORIGIN
L_00021d3a:
    shll16 r2
    .org 0x21d3c-ORIGIN
L_00021d3c:
    add r3,r1
    .org 0x21d3e-ORIGIN
L_00021d3e:
    div1 r0,r1
    .org 0x21d40-ORIGIN
L_00021d40:
    div1 r0,r1
    .org 0x21d42-ORIGIN
L_00021d42:
    div1 r0,r1
    .org 0x21d44-ORIGIN
L_00021d44:
    div1 r0,r1
    .org 0x21d46-ORIGIN
L_00021d46:
    div1 r0,r1
    .org 0x21d48-ORIGIN
L_00021d48:
    div1 r0,r1
    .org 0x21d4a-ORIGIN
L_00021d4a:
    div1 r0,r1
    .org 0x21d4c-ORIGIN
L_00021d4c:
    div1 r0,r1
    .org 0x21d4e-ORIGIN
L_00021d4e:
    div1 r0,r1
    .org 0x21d50-ORIGIN
L_00021d50:
    div1 r0,r1
    .org 0x21d52-ORIGIN
L_00021d52:
    div1 r0,r1
    .org 0x21d54-ORIGIN
L_00021d54:
    div1 r0,r1
    .org 0x21d56-ORIGIN
L_00021d56:
    div1 r0,r1
    .org 0x21d58-ORIGIN
L_00021d58:
    div1 r0,r1
    .org 0x21d5a-ORIGIN
L_00021d5a:
    div1 r0,r1
    .org 0x21d5c-ORIGIN
L_00021d5c:
    div1 r0,r1
    .org 0x21d5e-ORIGIN
L_00021d5e:
    rotcl r1
    .org 0x21d60-ORIGIN
L_00021d60:
    extu.w r1,r0
    .org 0x21d62-ORIGIN
L_00021d62:
    add r2,r0
    .org 0x21d64-ORIGIN
L_00021d64:
    mov.l @r15+,r3
    .org 0x21d66-ORIGIN
L_00021d66:
    rts
    .org 0x21d68-ORIGIN
L_00021d68:
    mov.l @r15+,r2
    .org 0x21d6a-ORIGIN
L_00021d6a:
    mov.l P_00021dc8,r1
    .org 0x21d6c-ORIGIN
L_00021d6c:
    mov.l P_00021dcc,r2
    .org 0x21d6e-ORIGIN
L_00021d6e:
    mov.l r2,@r1
    .org 0x21d70-ORIGIN
L_00021d70:
    mov #0x0,r0
    .org 0x21d72-ORIGIN
L_00021d72:
    rts
    .org 0x21d74-ORIGIN
L_00021d74:
    mov.l @r15+,r2
    .org 0x21d76-ORIGIN
L_00021d76:
    div0u
    .org 0x21d78-ORIGIN
L_00021d78:
    extu.w r1,r2
    .org 0x21d7a-ORIGIN
L_00021d7a:
    shll16 r2
    .org 0x21d7c-ORIGIN
L_00021d7c:
    shlr16 r1
    .org 0x21d7e-ORIGIN
L_00021d7e:
    rotcl r2
    .org 0x21d80-ORIGIN
L_00021d80:
    div1 r0,r1
    .org 0x21d82-ORIGIN
L_00021d82:
    rotcl r2
    .org 0x21d84-ORIGIN
L_00021d84:
    div1 r0,r1
    .org 0x21d86-ORIGIN
L_00021d86:
    rotcl r2
    .org 0x21d88-ORIGIN
L_00021d88:
    div1 r0,r1
    .org 0x21d8a-ORIGIN
L_00021d8a:
    rotcl r2
    .org 0x21d8c-ORIGIN
L_00021d8c:
    div1 r0,r1
    .org 0x21d8e-ORIGIN
L_00021d8e:
    rotcl r2
    .org 0x21d90-ORIGIN
L_00021d90:
    div1 r0,r1
    .org 0x21d92-ORIGIN
L_00021d92:
    rotcl r2
    .org 0x21d94-ORIGIN
L_00021d94:
    div1 r0,r1
    .org 0x21d96-ORIGIN
L_00021d96:
    rotcl r2
    .org 0x21d98-ORIGIN
L_00021d98:
    div1 r0,r1
    .org 0x21d9a-ORIGIN
L_00021d9a:
    rotcl r2
    .org 0x21d9c-ORIGIN
L_00021d9c:
    div1 r0,r1
    .org 0x21d9e-ORIGIN
L_00021d9e:
    rotcl r2
    .org 0x21da0-ORIGIN
L_00021da0:
    div1 r0,r1
    .org 0x21da2-ORIGIN
L_00021da2:
    rotcl r2
    .org 0x21da4-ORIGIN
L_00021da4:
    div1 r0,r1
    .org 0x21da6-ORIGIN
L_00021da6:
    rotcl r2
    .org 0x21da8-ORIGIN
L_00021da8:
    div1 r0,r1
    .org 0x21daa-ORIGIN
L_00021daa:
    rotcl r2
    .org 0x21dac-ORIGIN
L_00021dac:
    div1 r0,r1
    .org 0x21dae-ORIGIN
L_00021dae:
    rotcl r2
    .org 0x21db0-ORIGIN
L_00021db0:
    div1 r0,r1
    .org 0x21db2-ORIGIN
L_00021db2:
    rotcl r2
    .org 0x21db4-ORIGIN
L_00021db4:
    div1 r0,r1
    .org 0x21db6-ORIGIN
L_00021db6:
    rotcl r2
    .org 0x21db8-ORIGIN
L_00021db8:
    div1 r0,r1
    .org 0x21dba-ORIGIN
L_00021dba:
    rotcl r2
    .org 0x21dbc-ORIGIN
L_00021dbc:
    div1 r0,r1
    .org 0x21dbe-ORIGIN
L_00021dbe:
    rotcl r2
    .org 0x21dc0-ORIGIN
L_00021dc0:
    mov r2,r0
    .org 0x21dc2-ORIGIN
L_00021dc2:
    rts
    .org 0x21dc4-ORIGIN
L_00021dc4:
    mov.l @r15+,r2
    .org 0x21dc8-ORIGIN
P_00021dc8:
    .byte 0xff
    .org 0x21dc9-ORIGIN
P_00021dc9:
    .byte 0xff
    .org 0x21dca-ORIGIN
P_00021dca:
    .byte 0x98
    .org 0x21dcb-ORIGIN
P_00021dcb:
    .byte 0x18
    .org 0x21dcc-ORIGIN
P_00021dcc:
    .byte 0x00
    .org 0x21dcd-ORIGIN
P_00021dcd:
    .byte 0x00
    .org 0x21dce-ORIGIN
P_00021dce:
    .byte 0x04
    .org 0x21dcf-ORIGIN
P_00021dcf:
    .byte 0x4e
    .org 0x26270-ORIGIN
L_00026270:
    sts.l pr,@-r15
    .org 0x26272-ORIGIN
L_00026272:
    mov.l r4,@-r15
    .org 0x26274-ORIGIN
L_00026274:
    extu.w r7,r7
    .org 0x26276-ORIGIN
L_00026276:
    mov r5,r0
    .org 0x26278-ORIGIN
L_00026278:
    mov r7,r5
    .org 0x2627a-ORIGIN
L_0002627a:
    mov.l P_000262a4,r7
    .org 0x2627c-ORIGIN
L_0002627c:
    jsr @r7
    .org 0x2627e-ORIGIN
L_0002627e:
    mov #0xe,r4
    .org 0x26280-ORIGIN
L_00026280:
    mov.l r4,@-r15
    .org 0x26282-ORIGIN
L_00026282:
    mov.l r5,@-r15
    .org 0x26284-ORIGIN
L_00026284:
    mov r6,r0
    .org 0x26286-ORIGIN
L_00026286:
    mov.l @(0x10,r15),r5
    .org 0x26288-ORIGIN
L_00026288:
    extu.w r5,r5
    .org 0x2628a-ORIGIN
L_0002628a:
    jsr @r7
    .org 0x2628c-ORIGIN
L_0002628c:
    mov #0xe,r4
    .org 0x2628e-ORIGIN
L_0002628e:
    mov.l @r15+,r1
    .org 0x26290-ORIGIN
L_00026290:
    mov.l @r15+,r0
    .org 0x26292-ORIGIN
L_00026292:
    mov r4,r2
    .org 0x26294-ORIGIN
L_00026294:
    mov r5,r3
    .org 0x26296-ORIGIN
L_00026296:
    mov.l @r15+,r4
    .org 0x26298-ORIGIN
L_00026298:
    lds.l @r15+,pr
    .org 0x2629a-ORIGIN
L_0002629a:
    mov.l P_000262a0,r7
    .org 0x2629c-ORIGIN
L_0002629c:
    jmp @r7
    .org 0x2629e-ORIGIN
L_0002629e:
    mov #0x8,r5
    .org 0x262a0-ORIGIN
P_000262a0:
    .byte 0x00
    .org 0x262a1-ORIGIN
P_000262a1:
    .byte 0x02
    .org 0x262a2-ORIGIN
P_000262a2:
    .byte 0x68
    .org 0x262a3-ORIGIN
P_000262a3:
    .byte 0x48
    .org 0x262a4-ORIGIN
P_000262a4:
    .byte 0x00
    .org 0x262a5-ORIGIN
P_000262a5:
    .byte 0x02
    .org 0x262a6-ORIGIN
P_000262a6:
    .byte 0x69
    .org 0x262a7-ORIGIN
P_000262a7:
    .byte 0x84
    .org 0x26474-ORIGIN
L_00026474:
    sts.l pr,@-r15
    .org 0x26476-ORIGIN
L_00026476:
    mov.l r4,@-r15
    .org 0x26478-ORIGIN
L_00026478:
    mov r5,r0
    .org 0x2647a-ORIGIN
L_0002647a:
    extu.b r6,r5
    .org 0x2647c-ORIGIN
L_0002647c:
    mov.l P_0002649c,r7
    .org 0x2647e-ORIGIN
L_0002647e:
    jsr @r7
    .org 0x26480-ORIGIN
L_00026480:
    mov #0x7,r4
    .org 0x26482-ORIGIN
L_00026482:
    mov.l @r15+,r6
    .org 0x26484-ORIGIN
L_00026484:
    add r4,r6
    .org 0x26486-ORIGIN
L_00026486:
    mov.b @(0x1,r6),r0
    .org 0x26488-ORIGIN
L_00026488:
    extu.b r0,r2
    .org 0x2648a-ORIGIN
L_0002648a:
    mov r5,r3
    .org 0x2648c-ORIGIN
L_0002648c:
    mov.b @r6,r1
    .org 0x2648e-ORIGIN
L_0002648e:
    lds.l @r15+,pr
    .org 0x26490-ORIGIN
L_00026490:
    mov.l P_00026498,r6
    .org 0x26492-ORIGIN
L_00026492:
    jmp @r6
    .org 0x26494-ORIGIN
L_00026494:
    extu.b r1,r0
    .org 0x26498-ORIGIN
P_00026498:
    .byte 0x00
    .org 0x26499-ORIGIN
P_00026499:
    .byte 0x02
    .org 0x2649a-ORIGIN
P_0002649a:
    .byte 0x67
    .org 0x2649b-ORIGIN
P_0002649b:
    .byte 0x40
    .org 0x2649c-ORIGIN
P_0002649c:
    .byte 0x00
    .org 0x2649d-ORIGIN
P_0002649d:
    .byte 0x02
    .org 0x2649e-ORIGIN
P_0002649e:
    .byte 0x69
    .org 0x2649f-ORIGIN
P_0002649f:
    .byte 0x44
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
    .org 0x26848-ORIGIN
L_00026848:
    mov.l r8,@-r15
    .org 0x2684a-ORIGIN
L_0002684a:
    sts.l pr,@-r15
    .org 0x2684c-ORIGIN
L_0002684c:
    sts macl,r7
    .org 0x2684e-ORIGIN
L_0002684e:
    mulu.w r5,r0
    .org 0x26850-ORIGIN
L_00026850:
    add r2,r4
    .org 0x26852-ORIGIN
L_00026852:
    sts macl,r0
    .org 0x26854-ORIGIN
L_00026854:
    lds r7,macl
    .org 0x26856-ORIGIN
L_00026856:
    shll r5
    .org 0x26858-ORIGIN
L_00026858:
    add r0,r4
    .org 0x2685a-ORIGIN
L_0002685a:
    add r4,r5
    .org 0x2685c-ORIGIN
L_0002685c:
    mov r1,r8
    .org 0x2685e-ORIGIN
L_0002685e:
    mov.l P_000268a0,r7
    .org 0x26860-ORIGIN
L_00026860:
    tst r3,r3
    .org 0x26862-ORIGIN
L_00026862:
    bt L_0002688a
    .org 0x26864-ORIGIN
L_00026864:
    mov.w @r4,r1
    .org 0x26866-ORIGIN
L_00026866:
    mov.w @(0x2,r4),r0
    .org 0x26868-ORIGIN
L_00026868:
    extu.w r0,r2
    .org 0x2686a-ORIGIN
L_0002686a:
    jsr @r7
    .org 0x2686c-ORIGIN
L_0002686c:
    extu.w r1,r0
    .org 0x2686e-ORIGIN
L_0002686e:
    tst r8,r8
    .org 0x26870-ORIGIN
L_00026870:
    bt L_0002689a
    .org 0x26872-ORIGIN
L_00026872:
    mov.l r0,@-r15
    .org 0x26874-ORIGIN
L_00026874:
    mov.w @r5,r1
    .org 0x26876-ORIGIN
L_00026876:
    mov.w @(0x2,r5),r0
    .org 0x26878-ORIGIN
L_00026878:
    extu.w r0,r2
    .org 0x2687a-ORIGIN
L_0002687a:
    jsr @r7
    .org 0x2687c-ORIGIN
L_0002687c:
    extu.w r1,r0
    .org 0x2687e-ORIGIN
L_0002687e:
    mov r0,r2
    .org 0x26880-ORIGIN
L_00026880:
    mov.l @r15+,r0
    .org 0x26882-ORIGIN
L_00026882:
    jsr @r7
    .org 0x26884-ORIGIN
L_00026884:
    mov r8,r3
    .org 0x26886-ORIGIN
L_00026886:
    bra L_0002689a
    .org 0x26888-ORIGIN
L_00026888:
    nop
    .org 0x2688a-ORIGIN
L_0002688a:
    tst r8,r8
    .org 0x2688c-ORIGIN
L_0002688c:
    bt/s L_0002689a
    .org 0x2688e-ORIGIN
L_0002688e:
    mov.w @r4,r0
    .org 0x26890-ORIGIN
L_00026890:
    mov.w @r5,r2
    .org 0x26892-ORIGIN
L_00026892:
    extu.w r0,r0
    .org 0x26894-ORIGIN
L_00026894:
    extu.w r2,r2
    .org 0x26896-ORIGIN
L_00026896:
    jsr @r7
    .org 0x26898-ORIGIN
L_00026898:
    mov r8,r3
    .org 0x2689a-ORIGIN
L_0002689a:
    lds.l @r15+,pr
    .org 0x2689c-ORIGIN
L_0002689c:
    rts
    .org 0x2689e-ORIGIN
L_0002689e:
    mov.l @r15+,r8
    .org 0x268a0-ORIGIN
P_000268a0:
    .byte 0x00
    .org 0x268a1-ORIGIN
P_000268a1:
    .byte 0x02
    .org 0x268a2-ORIGIN
P_000268a2:
    .byte 0x67
    .org 0x268a3-ORIGIN
P_000268a3:
    .byte 0x40
    .org 0x26944-ORIGIN
L_00026944:
    mov r4,r3
    .org 0x26946-ORIGIN
L_00026946:
    mov.b @(r0,r4),r1
    .org 0x26948-ORIGIN
L_00026948:
    extu.b r1,r1
    .org 0x2694a-ORIGIN
L_0002694a:
    cmp/eq r1,r5
    .org 0x2694c-ORIGIN
L_0002694c:
    bt L_0002697c
    .org 0x2694e-ORIGIN
L_0002694e:
    cmp/hi r1,r5
    .org 0x26950-ORIGIN
L_00026950:
    bf L_00026974
    .org 0x26952-ORIGIN
L_00026952:
    cmp/eq r4,r3
    .org 0x26954-ORIGIN
L_00026954:
    bt L_0002697c
    .org 0x26956-ORIGIN
L_00026956:
    sub r1,r5
    .org 0x26958-ORIGIN
L_00026958:
    shll16 r5
    .org 0x2695a-ORIGIN
L_0002695a:
    add r4,r0
    .org 0x2695c-ORIGIN
L_0002695c:
    mov.b @r0,r1
    .org 0x2695e-ORIGIN
L_0002695e:
    mov.b @(0x1,r0),r0
    .org 0x26960-ORIGIN
L_00026960:
    extu.b r1,r1
    .org 0x26962-ORIGIN
L_00026962:
    extu.b r0,r0
    .org 0x26964-ORIGIN
L_00026964:
    sts.l pr,@-r15
    .org 0x26966-ORIGIN
L_00026966:
    mov.l P_00026980,r2
    .org 0x26968-ORIGIN
L_00026968:
    sub r1,r0
    .org 0x2696a-ORIGIN
L_0002696a:
    jsr @r2
    .org 0x2696c-ORIGIN
L_0002696c:
    mov r5,r1
    .org 0x2696e-ORIGIN
L_0002696e:
    lds.l @r15+,pr
    .org 0x26970-ORIGIN
L_00026970:
    rts
    .org 0x26972-ORIGIN
L_00026972:
    mov r0,r5
    .org 0x26974-ORIGIN
L_00026974:
    add #-0x1,r4
    .org 0x26976-ORIGIN
L_00026976:
    cmp/pz r4
    .org 0x26978-ORIGIN
L_00026978:
    bt L_00026946
    .org 0x2697a-ORIGIN
L_0002697a:
    mov #0x0,r4
    .org 0x2697c-ORIGIN
L_0002697c:
    rts
    .org 0x2697e-ORIGIN
L_0002697e:
    mov #0x0,r5
    .org 0x26980-ORIGIN
P_00026980:
    .byte 0x00
    .org 0x26981-ORIGIN
P_00026981:
    .byte 0x02
    .org 0x26982-ORIGIN
P_00026982:
    .byte 0x6c
    .org 0x26983-ORIGIN
P_00026983:
    .byte 0x78
    .org 0x26984-ORIGIN
L_00026984:
    mov r4,r3
    .org 0x26986-ORIGIN
L_00026986:
    mov.w @(r0,r4),r1
    .org 0x26988-ORIGIN
L_00026988:
    extu.w r1,r1
    .org 0x2698a-ORIGIN
L_0002698a:
    cmp/eq r1,r5
    .org 0x2698c-ORIGIN
L_0002698c:
    bt L_000269bc
    .org 0x2698e-ORIGIN
L_0002698e:
    cmp/hi r1,r5
    .org 0x26990-ORIGIN
L_00026990:
    bf L_000269b4
    .org 0x26992-ORIGIN
L_00026992:
    cmp/eq r4,r3
    .org 0x26994-ORIGIN
L_00026994:
    bt L_000269bc
    .org 0x26996-ORIGIN
L_00026996:
    sub r1,r5
    .org 0x26998-ORIGIN
L_00026998:
    shll16 r5
    .org 0x2699a-ORIGIN
L_0002699a:
    add r4,r0
    .org 0x2699c-ORIGIN
L_0002699c:
    mov.w @r0,r1
    .org 0x2699e-ORIGIN
L_0002699e:
    mov.w @(0x2,r0),r0
    .org 0x269a0-ORIGIN
L_000269a0:
    extu.w r1,r1
    .org 0x269a2-ORIGIN
L_000269a2:
    extu.w r0,r0
    .org 0x269a4-ORIGIN
L_000269a4:
    sts.l pr,@-r15
    .org 0x269a6-ORIGIN
L_000269a6:
    mov.l P_000269c0,r2
    .org 0x269a8-ORIGIN
L_000269a8:
    sub r1,r0
    .org 0x269aa-ORIGIN
L_000269aa:
    jsr @r2
    .org 0x269ac-ORIGIN
L_000269ac:
    mov r5,r1
    .org 0x269ae-ORIGIN
L_000269ae:
    lds.l @r15+,pr
    .org 0x269b0-ORIGIN
L_000269b0:
    rts
    .org 0x269b2-ORIGIN
L_000269b2:
    mov r0,r5
    .org 0x269b4-ORIGIN
L_000269b4:
    add #-0x2,r4
    .org 0x269b6-ORIGIN
L_000269b6:
    cmp/pz r4
    .org 0x269b8-ORIGIN
L_000269b8:
    bt L_00026986
    .org 0x269ba-ORIGIN
L_000269ba:
    mov #0x0,r4
    .org 0x269bc-ORIGIN
L_000269bc:
    rts
    .org 0x269be-ORIGIN
L_000269be:
    mov #0x0,r5
    .org 0x269c0-ORIGIN
P_000269c0:
    .byte 0x00
    .org 0x269c1-ORIGIN
P_000269c1:
    .byte 0x02
    .org 0x269c2-ORIGIN
P_000269c2:
    .byte 0x6c
    .org 0x269c3-ORIGIN
P_000269c3:
    .byte 0x78
    .org 0x26c78-ORIGIN
L_00026c78:
    tst r0,r0
    .org 0x26c7a-ORIGIN
L_00026c7a:
    bt L_00026d0a
    .org 0x26c7c-ORIGIN
L_00026c7c:
    mov.l r2,@-r15
    .org 0x26c7e-ORIGIN
L_00026c7e:
    mov #0x0,r2
    .org 0x26c80-ORIGIN
L_00026c80:
    div0u
    .org 0x26c82-ORIGIN
L_00026c82:
    rotcl r1
    .org 0x26c84-ORIGIN
L_00026c84:
    div1 r0,r2
    .org 0x26c86-ORIGIN
L_00026c86:
    rotcl r1
    .org 0x26c88-ORIGIN
L_00026c88:
    div1 r0,r2
    .org 0x26c8a-ORIGIN
L_00026c8a:
    rotcl r1
    .org 0x26c8c-ORIGIN
L_00026c8c:
    div1 r0,r2
    .org 0x26c8e-ORIGIN
L_00026c8e:
    rotcl r1
    .org 0x26c90-ORIGIN
L_00026c90:
    div1 r0,r2
    .org 0x26c92-ORIGIN
L_00026c92:
    rotcl r1
    .org 0x26c94-ORIGIN
L_00026c94:
    div1 r0,r2
    .org 0x26c96-ORIGIN
L_00026c96:
    rotcl r1
    .org 0x26c98-ORIGIN
L_00026c98:
    div1 r0,r2
    .org 0x26c9a-ORIGIN
L_00026c9a:
    rotcl r1
    .org 0x26c9c-ORIGIN
L_00026c9c:
    div1 r0,r2
    .org 0x26c9e-ORIGIN
L_00026c9e:
    rotcl r1
    .org 0x26ca0-ORIGIN
L_00026ca0:
    div1 r0,r2
    .org 0x26ca2-ORIGIN
L_00026ca2:
    rotcl r1
    .org 0x26ca4-ORIGIN
L_00026ca4:
    div1 r0,r2
    .org 0x26ca6-ORIGIN
L_00026ca6:
    rotcl r1
    .org 0x26ca8-ORIGIN
L_00026ca8:
    div1 r0,r2
    .org 0x26caa-ORIGIN
L_00026caa:
    rotcl r1
    .org 0x26cac-ORIGIN
L_00026cac:
    div1 r0,r2
    .org 0x26cae-ORIGIN
L_00026cae:
    rotcl r1
    .org 0x26cb0-ORIGIN
L_00026cb0:
    div1 r0,r2
    .org 0x26cb2-ORIGIN
L_00026cb2:
    rotcl r1
    .org 0x26cb4-ORIGIN
L_00026cb4:
    div1 r0,r2
    .org 0x26cb6-ORIGIN
L_00026cb6:
    rotcl r1
    .org 0x26cb8-ORIGIN
L_00026cb8:
    div1 r0,r2
    .org 0x26cba-ORIGIN
L_00026cba:
    rotcl r1
    .org 0x26cbc-ORIGIN
L_00026cbc:
    div1 r0,r2
    .org 0x26cbe-ORIGIN
L_00026cbe:
    rotcl r1
    .org 0x26cc0-ORIGIN
L_00026cc0:
    div1 r0,r2
    .org 0x26cc2-ORIGIN
L_00026cc2:
    rotcl r1
    .org 0x26cc4-ORIGIN
L_00026cc4:
    div1 r0,r2
    .org 0x26cc6-ORIGIN
L_00026cc6:
    rotcl r1
    .org 0x26cc8-ORIGIN
L_00026cc8:
    div1 r0,r2
    .org 0x26cca-ORIGIN
L_00026cca:
    rotcl r1
    .org 0x26ccc-ORIGIN
L_00026ccc:
    div1 r0,r2
    .org 0x26cce-ORIGIN
L_00026cce:
    rotcl r1
    .org 0x26cd0-ORIGIN
L_00026cd0:
    div1 r0,r2
    .org 0x26cd2-ORIGIN
L_00026cd2:
    rotcl r1
    .org 0x26cd4-ORIGIN
L_00026cd4:
    div1 r0,r2
    .org 0x26cd6-ORIGIN
L_00026cd6:
    rotcl r1
    .org 0x26cd8-ORIGIN
L_00026cd8:
    div1 r0,r2
    .org 0x26cda-ORIGIN
L_00026cda:
    rotcl r1
    .org 0x26cdc-ORIGIN
L_00026cdc:
    div1 r0,r2
    .org 0x26cde-ORIGIN
L_00026cde:
    rotcl r1
    .org 0x26ce0-ORIGIN
L_00026ce0:
    div1 r0,r2
    .org 0x26ce2-ORIGIN
L_00026ce2:
    rotcl r1
    .org 0x26ce4-ORIGIN
L_00026ce4:
    div1 r0,r2
    .org 0x26ce6-ORIGIN
L_00026ce6:
    rotcl r1
    .org 0x26ce8-ORIGIN
L_00026ce8:
    div1 r0,r2
    .org 0x26cea-ORIGIN
L_00026cea:
    rotcl r1
    .org 0x26cec-ORIGIN
L_00026cec:
    div1 r0,r2
    .org 0x26cee-ORIGIN
L_00026cee:
    rotcl r1
    .org 0x26cf0-ORIGIN
L_00026cf0:
    div1 r0,r2
    .org 0x26cf2-ORIGIN
L_00026cf2:
    rotcl r1
    .org 0x26cf4-ORIGIN
L_00026cf4:
    div1 r0,r2
    .org 0x26cf6-ORIGIN
L_00026cf6:
    rotcl r1
    .org 0x26cf8-ORIGIN
L_00026cf8:
    div1 r0,r2
    .org 0x26cfa-ORIGIN
L_00026cfa:
    rotcl r1
    .org 0x26cfc-ORIGIN
L_00026cfc:
    div1 r0,r2
    .org 0x26cfe-ORIGIN
L_00026cfe:
    rotcl r1
    .org 0x26d00-ORIGIN
L_00026d00:
    div1 r0,r2
    .org 0x26d02-ORIGIN
L_00026d02:
    rotcl r1
    .org 0x26d04-ORIGIN
L_00026d04:
    mov.l @r15+,r2
    .org 0x26d06-ORIGIN
L_00026d06:
    rts
    .org 0x26d08-ORIGIN
L_00026d08:
    mov r1,r0
    .org 0x26d0a-ORIGIN
L_00026d0a:
    rts
    .org 0x26d0c-ORIGIN
L_00026d0c:
    mov #0x0,r0
    .org 0x4bdc2-ORIGIN
L_0004bdc2:
    mov.l r13,@-r15
    .org 0x4bdc4-ORIGIN
L_0004bdc4:
    mov.l r14,@-r15
    .org 0x4bdc6-ORIGIN
L_0004bdc6:
    sts.l pr,@-r15
    .org 0x4bdc8-ORIGIN
L_0004bdc8:
    sts.l macl,@-r15
    .org 0x4bdca-ORIGIN
L_0004bdca:
    stc.l gbr,@-r15
    .org 0x4bdcc-ORIGIN
L_0004bdcc:
    mov.l P_0004bf08,r0
    .org 0x4bdce-ORIGIN
L_0004bdce:
    ldc r0,gbr
    .org 0x4bdd0-ORIGIN
L_0004bdd0:
    add #-0x4,r15
    .org 0x4bdd2-ORIGIN
L_0004bdd2:
    mov.l P_0004bf24,r6
    .org 0x4bdd4-ORIGIN
L_0004bdd4:
    mov.l P_0004bf28,r7
    .org 0x4bdd6-ORIGIN
L_0004bdd6:
    mov.b @r6,r0
    .org 0x4bdd8-ORIGIN
L_0004bdd8:
    tst #0x20,r0
    .org 0x4bdda-ORIGIN
L_0004bdda:
    bf L_0004beaa
    .org 0x4bddc-ORIGIN
L_0004bddc:
    mov.b @(0x1,r7),r0
    .org 0x4bdde-ORIGIN
L_0004bdde:
    mov.l P_0004bf08,r13
    .org 0x4bde0-ORIGIN
L_0004bde0:
    extu.b r0,r6
    .org 0x4bde2-ORIGIN
L_0004bde2:
    mov.b @(0x9,r7),r0
    .org 0x4bde4-ORIGIN
L_0004bde4:
    extu.b r0,r5
    .org 0x4bde6-ORIGIN
L_0004bde6:
    mov #0x35,r0
    .org 0x4bde8-ORIGIN
L_0004bde8:
    mov.b @(r0,r7),r2
    .org 0x4bdea-ORIGIN
L_0004bdea:
    mov.b @(0x50,gbr),r0
    .org 0x4bdec-ORIGIN
L_0004bdec:
    add r6,r2
    .org 0x4bdee-ORIGIN
L_0004bdee:
    extu.b r0,r4
    .org 0x4bdf0-ORIGIN
L_0004bdf0:
    mov.w P_0004bef2,r0
    .org 0x4bdf2-ORIGIN
L_0004bdf2:
    sub r5,r2
    .org 0x4bdf4-ORIGIN
L_0004bdf4:
    mov.b @(r0,r13),r5
    .org 0x4bdf6-ORIGIN
L_0004bdf6:
    add #-0x40,r2
    .org 0x4bdf8-ORIGIN
L_0004bdf8:
    mov.w P_0004bef4,r0
    .org 0x4bdfa-ORIGIN
L_0004bdfa:
    sub r4,r2
    .org 0x4bdfc-ORIGIN
L_0004bdfc:
    extu.b r5,r5
    .org 0x4bdfe-ORIGIN
L_0004bdfe:
    mov.b @(r0,r13),r6
    .org 0x4be00-ORIGIN
L_0004be00:
    sub r5,r2
    .org 0x4be02-ORIGIN
L_0004be02:
    mov.l P_0004bf2c,r5
    .org 0x4be04-ORIGIN
L_0004be04:
    mov #0x20,r0
    .org 0x4be06-ORIGIN
L_0004be06:
    extu.b r6,r14
    .org 0x4be08-ORIGIN
L_0004be08:
    mov.w @(r0,r5),r6
    .org 0x4be0a-ORIGIN
L_0004be0a:
    mov #0x22,r0
    .org 0x4be0c-ORIGIN
L_0004be0c:
    add r2,r14
    .org 0x4be0e-ORIGIN
L_0004be0e:
    mov.w @(r0,r5),r2
    .org 0x4be10-ORIGIN
L_0004be10:
    extu.w r6,r6
    .org 0x4be12-ORIGIN
L_0004be12:
    extu.w r2,r2
    .org 0x4be14-ORIGIN
L_0004be14:
    cmp/gt r2,r6
    .org 0x4be16-ORIGIN
L_0004be16:
    bf/s L_0004be1c
    .org 0x4be18-ORIGIN
L_0004be18:
    add #-0x40,r14
    .org 0x4be1a-ORIGIN
L_0004be1a:
    mov r2,r6
    .org 0x4be1c-ORIGIN
L_0004be1c:
    mov r6,r5
    .org 0x4be1e-ORIGIN
L_0004be1e:
    mov.l P_0004bf30,r6
    .org 0x4be20-ORIGIN
L_0004be20:
    mov.b @(0x2,r6),r0
    .org 0x4be22-ORIGIN
L_0004be22:
    tst #0x40,r0
    .org 0x4be24-ORIGIN
L_0004be24:
    bt L_0004be98
    .org 0x4be26-ORIGIN
L_0004be26:
    mov.l P_0004bf34,r6
    .org 0x4be28-ORIGIN
L_0004be28:
    extu.w r5,r5
    .org 0x4be2a-ORIGIN
L_0004be2a:
    mov.w @r6,r2
    .org 0x4be2c-ORIGIN
L_0004be2c:
    extu.w r2,r2
    .org 0x4be2e-ORIGIN
L_0004be2e:
    cmp/ge r2,r5
    .org 0x4be30-ORIGIN
L_0004be30:
    bf L_0004be98
    .org 0x4be32-ORIGIN
L_0004be32:
    mov.l P_0004bf38,r6
    .org 0x4be34-ORIGIN
L_0004be34:
    mov.l P_0004bf3c,r4
    .org 0x4be36-ORIGIN
L_0004be36:
    mov.b @(0x7,r6),r0
    .org 0x4be38-ORIGIN
L_0004be38:
    mov.l P_0004bf40,r5
    .org 0x4be3a-ORIGIN
L_0004be3a:
    mov.l P_0004bf44,r2
    .org 0x4be3c-ORIGIN
L_0004be3c:
    jsr @r2
    .org 0x4be3e-ORIGIN
L_0004be3e:
    extu.b r0,r6
    .org 0x4be40-ORIGIN
L_0004be40:
    mov.l P_0004bf48,r7
    .org 0x4be42-ORIGIN
L_0004be42:
    mov.b r0,@(0xc0,gbr)
    .org 0x4be44-ORIGIN
L_0004be44:
    mov.w @r7,r0
    .org 0x4be46-ORIGIN
L_0004be46:
    mov.l P_0004bf4c,r7
    .org 0x4be48-ORIGIN
L_0004be48:
    mov.w r0,@(0x2,r15)
    .org 0x4be4a-ORIGIN
L_0004be4a:
    mov #0x36,r0
    .org 0x4be4c-ORIGIN
L_0004be4c:
    mov.w @(r0,r7),r3
    .org 0x4be4e-ORIGIN
L_0004be4e:
    mov.l P_0004bf50,r4
    .org 0x4be50-ORIGIN
L_0004be50:
    mov.l P_0004bf54,r5
    .org 0x4be52-ORIGIN
L_0004be52:
    mov.l P_0004bf58,r6
    .org 0x4be54-ORIGIN
L_0004be54:
    mov.l P_0004bf5c,r2
    .org 0x4be56-ORIGIN
L_0004be56:
    jsr @r2
    .org 0x4be58-ORIGIN
L_0004be58:
    extu.w r3,r7
    .org 0x4be5a-ORIGIN
L_0004be5a:
    mov #-0x1,r5
    .org 0x4be5c-ORIGIN
L_0004be5c:
    extu.w r0,r6
    .org 0x4be5e-ORIGIN
L_0004be5e:
    extu.b r5,r5
    .org 0x4be60-ORIGIN
L_0004be60:
    cmp/gt r5,r6
    .org 0x4be62-ORIGIN
L_0004be62:
    bt L_0004be66
    .org 0x4be64-ORIGIN
L_0004be64:
    mov r6,r5
    .org 0x4be66-ORIGIN
L_0004be66:
    mov r5,r0
    .org 0x4be68-ORIGIN
L_0004be68:
    mov.b r0,@(0xbc,gbr)
    .org 0x4be6a-ORIGIN
L_0004be6a:
    mov.w P_0004bef6,r0
    .org 0x4be6c-ORIGIN
L_0004be6c:
    extu.b r5,r6
    .org 0x4be6e-ORIGIN
L_0004be6e:
    mov.w @(r0,r13),r2
    .org 0x4be70-ORIGIN
L_0004be70:
    mov.b @(0xc0,gbr),r0
    .org 0x4be72-ORIGIN
L_0004be72:
    extu.w r2,r3
    .org 0x4be74-ORIGIN
L_0004be74:
    extu.b r0,r2
    .org 0x4be76-ORIGIN
L_0004be76:
    mov.l P_0004bf60,r0
    .org 0x4be78-ORIGIN
L_0004be78:
    mul.l r3,r2
    .org 0x4be7a-ORIGIN
L_0004be7a:
    sts macl,r2
    .org 0x4be7c-ORIGIN
L_0004be7c:
    mul.l r2,r6
    .org 0x4be7e-ORIGIN
L_0004be7e:
    mov.l P_0004bf64,r6
    .org 0x4be80-ORIGIN
L_0004be80:
    jsr @r6
    .org 0x4be82-ORIGIN
L_0004be82:
    sts macl,r1
    .org 0x4be84-ORIGIN
L_0004be84:
    mov #-0x1,r2
    .org 0x4be86-ORIGIN
L_0004be86:
    extu.b r2,r2
    .org 0x4be88-ORIGIN
L_0004be88:
    cmp/hi r2,r0
    .org 0x4be8a-ORIGIN
L_0004be8a:
    bf/s L_0004be90
    .org 0x4be8c-ORIGIN
L_0004be8c:
    mov r0,r6
    .org 0x4be8e-ORIGIN
L_0004be8e:
    mov r2,r6
    .org 0x4be90-ORIGIN
L_0004be90:
    mov r6,r0
    .org 0x4be92-ORIGIN
L_0004be92:
    mov.b r0,@(0xbe,gbr)
    .org 0x4be94-ORIGIN
L_0004be94:
    bra L_0004be9c
    .org 0x4be96-ORIGIN
L_0004be96:
    mov r6,r2
    .org 0x4be98-ORIGIN
L_0004be98:
    mov #0x0,r2
    .org 0x4be9a-ORIGIN
L_0004be9a:
    mov r2,r0
    .org 0x4be9c-ORIGIN
L_0004be9c:
    mov.l P_0004bf68,r6
    .org 0x4be9e-ORIGIN
L_0004be9e:
    extu.b r2,r2
    .org 0x4bea0-ORIGIN
L_0004bea0:
    mov.b r0,@(0x48,gbr)
    .org 0x4bea2-ORIGIN
L_0004bea2:
    add r2,r14
    .org 0x4bea4-ORIGIN
L_0004bea4:
    mov.b @(0x3,r6),r0
    .org 0x4bea6-ORIGIN
L_0004bea6:
    bra L_0004bec6
    .org 0x4bea8-ORIGIN
L_0004bea8:
    and #0xdf,r0
    .org 0x4beaa-ORIGIN
L_0004beaa:
    mov.b @(0x9,r7),r0
    .org 0x4beac-ORIGIN
L_0004beac:
    mov.l P_0004bf08,r13
    .org 0x4beae-ORIGIN
L_0004beae:
    extu.b r0,r5
    .org 0x4beb0-ORIGIN
L_0004beb0:
    mov.w P_0004bef4,r0
    .org 0x4beb2-ORIGIN
L_0004beb2:
    mov.l P_0004bf68,r6
    .org 0x4beb4-ORIGIN
L_0004beb4:
    mov.b @(r0,r13),r2
    .org 0x4beb6-ORIGIN
L_0004beb6:
    mov #0x32,r0
    .org 0x4beb8-ORIGIN
L_0004beb8:
    mov.b @(r0,r7),r4
    .org 0x4beba-ORIGIN
L_0004beba:
    extu.b r2,r14
    .org 0x4bebc-ORIGIN
L_0004bebc:
    mov.b @(0x3,r6),r0
    .org 0x4bebe-ORIGIN
L_0004bebe:
    sub r5,r4
    .org 0x4bec0-ORIGIN
L_0004bec0:
    add r4,r14
    .org 0x4bec2-ORIGIN
L_0004bec2:
    add #-0x40,r14
    .org 0x4bec4-ORIGIN
L_0004bec4:
    or #0x20,r0
    .org 0x4bec6-ORIGIN
L_0004bec6:
    exts.w r14,r14
    .org 0x4bec8-ORIGIN
L_0004bec8:
    mov #-0x80,r2
    .org 0x4beca-ORIGIN
L_0004beca:
    cmp/ge r2,r14
    .org 0x4becc-ORIGIN
L_0004becc:
    bt/s L_0004bed4
    .org 0x4bece-ORIGIN
L_0004bece:
    mov.b r0,@(0x3,r6)
    .org 0x4bed0-ORIGIN
L_0004bed0:
    bra L_0004bed6
    .org 0x4bed2-ORIGIN
L_0004bed2:
    mov #-0x80,r6
    .org 0x4bed4-ORIGIN
L_0004bed4:
    exts.w r14,r6
    .org 0x4bed6-ORIGIN
L_0004bed6:
    exts.w r6,r2
    .org 0x4bed8-ORIGIN
L_0004bed8:
    mov #0x7f,r6
    .org 0x4beda-ORIGIN
L_0004beda:
    cmp/gt r6,r2
    .org 0x4bedc-ORIGIN
L_0004bedc:
    bf L_0004bee0
    .org 0x4bede-ORIGIN
L_0004bede:
    mov #0x7f,r2
    .org 0x4bee0-ORIGIN
L_0004bee0:
    mov.w P_0004bef8,r0
    .org 0x4bee2-ORIGIN
L_0004bee2:
    mov.b r2,@(r0,r13)
    .org 0x4bee4-ORIGIN
L_0004bee4:
    add #0x4,r15
    .org 0x4bee6-ORIGIN
L_0004bee6:
    ldc.l @r15+,gbr
    .org 0x4bee8-ORIGIN
L_0004bee8:
    lds.l @r15+,macl
    .org 0x4beea-ORIGIN
L_0004beea:
    lds.l @r15+,pr
    .org 0x4beec-ORIGIN
L_0004beec:
    mov.l @r15+,r14
    .org 0x4beee-ORIGIN
L_0004beee:
    rts
    .org 0x4bef0-ORIGIN
L_0004bef0:
    mov.l @r15+,r13
    .org 0x4bef2-ORIGIN
P_0004bef2:
    .byte 0x03
    .org 0x4bef3-ORIGIN
P_0004bef3:
    .byte 0x5e
    .org 0x4bef4-ORIGIN
P_0004bef4:
    .byte 0x07
    .org 0x4bef5-ORIGIN
P_0004bef5:
    .byte 0xf1
    .org 0x4bef6-ORIGIN
P_0004bef6:
    .byte 0x06
    .org 0x4bef7-ORIGIN
P_0004bef7:
    .byte 0x74
    .org 0x4bef8-ORIGIN
P_0004bef8:
    .byte 0x05
    .org 0x4bef9-ORIGIN
P_0004bef9:
    .byte 0xa4
    .org 0x4bf08-ORIGIN
P_0004bf08:
    .byte 0xff
    .org 0x4bf09-ORIGIN
P_0004bf09:
    .byte 0xff
    .org 0x4bf0a-ORIGIN
P_0004bf0a:
    .byte 0x12
    .org 0x4bf0b-ORIGIN
P_0004bf0b:
    .byte 0x8c
    .org 0x4bf24-ORIGIN
P_0004bf24:
    .byte 0xff
    .org 0x4bf25-ORIGIN
P_0004bf25:
    .byte 0xff
    .org 0x4bf26-ORIGIN
P_0004bf26:
    .byte 0x24
    .org 0x4bf27-ORIGIN
P_0004bf27:
    .byte 0x58
    .org 0x4bf28-ORIGIN
P_0004bf28:
    .byte 0xff
    .org 0x4bf29-ORIGIN
P_0004bf29:
    .byte 0xff
    .org 0x4bf2a-ORIGIN
P_0004bf2a:
    .byte 0x23
    .org 0x4bf2b-ORIGIN
P_0004bf2b:
    .byte 0xbc
    .org 0x4bf2c-ORIGIN
P_0004bf2c:
    .byte 0xff
    .org 0x4bf2d-ORIGIN
P_0004bf2d:
    .byte 0xff
    .org 0x4bf2e-ORIGIN
P_0004bf2e:
    .byte 0x28
    .org 0x4bf2f-ORIGIN
P_0004bf2f:
    .byte 0x98
    .org 0x4bf30-ORIGIN
P_0004bf30:
    .byte 0xff
    .org 0x4bf31-ORIGIN
P_0004bf31:
    .byte 0xff
    .org 0x4bf32-ORIGIN
P_0004bf32:
    .byte 0x41
    .org 0x4bf33-ORIGIN
P_0004bf33:
    .byte 0xa9
    .org 0x4bf34-ORIGIN
P_0004bf34:
    .byte 0x00
    .org 0x4bf35-ORIGIN
P_0004bf35:
    .byte 0x00
    .org 0x4bf36-ORIGIN
P_0004bf36:
    .byte 0x90
    .org 0x4bf37-ORIGIN
P_0004bf37:
    .byte 0x12
    .org 0x4bf38-ORIGIN
P_0004bf38:
    .byte 0xff
    .org 0x4bf39-ORIGIN
P_0004bf39:
    .byte 0xff
    .org 0x4bf3a-ORIGIN
P_0004bf3a:
    .byte 0x10
    .org 0x4bf3b-ORIGIN
P_0004bf3b:
    .byte 0x68
    .org 0x4bf3c-ORIGIN
P_0004bf3c:
    .byte 0x00
    .org 0x4bf3d-ORIGIN
P_0004bf3d:
    .byte 0x01
    .org 0x4bf3e-ORIGIN
P_0004bf3e:
    .byte 0x1f
    .org 0x4bf3f-ORIGIN
P_0004bf3f:
    .byte 0x02
    .org 0x4bf40-ORIGIN
P_0004bf40:
    .byte 0x00
    .org 0x4bf41-ORIGIN
P_0004bf41:
    .byte 0x01
    .org 0x4bf42-ORIGIN
P_0004bf42:
    .byte 0x1e
    .org 0x4bf43-ORIGIN
P_0004bf43:
    .byte 0xea
    .org 0x4bf44-ORIGIN
P_0004bf44:
    .byte 0x00
    .org 0x4bf45-ORIGIN
P_0004bf45:
    .byte 0x02
    .org 0x4bf46-ORIGIN
P_0004bf46:
    .byte 0x64
    .org 0x4bf47-ORIGIN
P_0004bf47:
    .byte 0x74
    .org 0x4bf48-ORIGIN
P_0004bf48:
    .byte 0xff
    .org 0x4bf49-ORIGIN
P_0004bf49:
    .byte 0xff
    .org 0x4bf4a-ORIGIN
P_0004bf4a:
    .byte 0x10
    .org 0x4bf4b-ORIGIN
P_0004bf4b:
    .byte 0x24
    .org 0x4bf4c-ORIGIN
P_0004bf4c:
    .byte 0xff
    .org 0x4bf4d-ORIGIN
P_0004bf4d:
    .byte 0xff
    .org 0x4bf4e-ORIGIN
P_0004bf4e:
    .byte 0x10
    .org 0x4bf4f-ORIGIN
P_0004bf4f:
    .byte 0x94
    .org 0x4bf50-ORIGIN
P_0004bf50:
    .byte 0x00
    .org 0x4bf51-ORIGIN
P_0004bf51:
    .byte 0x00
    .org 0x4bf52-ORIGIN
P_0004bf52:
    .byte 0xc5
    .org 0x4bf53-ORIGIN
P_0004bf53:
    .byte 0x0e
    .org 0x4bf54-ORIGIN
P_0004bf54:
    .byte 0x00
    .org 0x4bf55-ORIGIN
P_0004bf55:
    .byte 0x01
    .org 0x4bf56-ORIGIN
P_0004bf56:
    .byte 0x46
    .org 0x4bf57-ORIGIN
P_0004bf57:
    .byte 0x1a
    .org 0x4bf58-ORIGIN
P_0004bf58:
    .byte 0x00
    .org 0x4bf59-ORIGIN
P_0004bf59:
    .byte 0x01
    .org 0x4bf5a-ORIGIN
P_0004bf5a:
    .byte 0x46
    .org 0x4bf5b-ORIGIN
P_0004bf5b:
    .byte 0x4a
    .org 0x4bf5c-ORIGIN
P_0004bf5c:
    .byte 0x00
    .org 0x4bf5d-ORIGIN
P_0004bf5d:
    .byte 0x02
    .org 0x4bf5e-ORIGIN
P_0004bf5e:
    .byte 0x62
    .org 0x4bf5f-ORIGIN
P_0004bf5f:
    .byte 0x70
    .org 0x4bf60-ORIGIN
P_0004bf60:
    .byte 0x00
    .org 0x4bf61-ORIGIN
P_0004bf61:
    .byte 0x07
    .org 0x4bf62-ORIGIN
P_0004bf62:
    .byte 0xa1
    .org 0x4bf63-ORIGIN
P_0004bf63:
    .byte 0x20
    .org 0x4bf64-ORIGIN
P_0004bf64:
    .byte 0x00
    .org 0x4bf65-ORIGIN
P_0004bf65:
    .byte 0x02
    .org 0x4bf66-ORIGIN
P_0004bf66:
    .byte 0x1c
    .org 0x4bf67-ORIGIN
P_0004bf67:
    .byte 0xe0
    .org 0x4bf68-ORIGIN
P_0004bf68:
    .byte 0xff
    .org 0x4bf69-ORIGIN
P_0004bf69:
    .byte 0xff
    .org 0x4bf6a-ORIGIN
P_0004bf6a:
    .byte 0x24
    .org 0x4bf6b-ORIGIN
P_0004bf6b:
    .byte 0xce
