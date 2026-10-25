! Complete stock signed endpoint evaluators, real weight update and blend caller.
    .text
    .balign 4
    .set ORIGIN,0x26628
    .org 0x26628-ORIGIN
L_00026628:
    sts.l pr,@-r15
    .org 0x2662a-ORIGIN
L_0002662a:
    mov.l r4,@-r15
    .org 0x2662c-ORIGIN
L_0002662c:
    extu.w r7,r7
    .org 0x2662e-ORIGIN
L_0002662e:
    mov r5,r0
    .org 0x26630-ORIGIN
L_00026630:
    mov r7,r5
    .org 0x26632-ORIGIN
L_00026632:
    mov.l P_0002665c,r7
    .org 0x26634-ORIGIN
L_00026634:
    jsr @r7
    .org 0x26636-ORIGIN
L_00026636:
    mov #0x1e,r4
    .org 0x26638-ORIGIN
L_00026638:
    mov.l r5,@-r15
    .org 0x2663a-ORIGIN
L_0002663a:
    mov.l r4,@-r15
    .org 0x2663c-ORIGIN
L_0002663c:
    mov r6,r0
    .org 0x2663e-ORIGIN
L_0002663e:
    mov.l @(0x10,r15),r5
    .org 0x26640-ORIGIN
L_00026640:
    extu.w r5,r5
    .org 0x26642-ORIGIN
L_00026642:
    jsr @r7
    .org 0x26644-ORIGIN
L_00026644:
    mov #0x1e,r4
    .org 0x26646-ORIGIN
L_00026646:
    mov.l @r15+,r0
    .org 0x26648-ORIGIN
L_00026648:
    mov.l @r15+,r1
    .org 0x2664a-ORIGIN
L_0002664a:
    mov r4,r2
    .org 0x2664c-ORIGIN
L_0002664c:
    mov r5,r3
    .org 0x2664e-ORIGIN
L_0002664e:
    mov.l @r15+,r4
    .org 0x26650-ORIGIN
L_00026650:
    lds.l @r15+,pr
    .org 0x26652-ORIGIN
L_00026652:
    mov.l P_00026658,r7
    .org 0x26654-ORIGIN
L_00026654:
    jmp @r7
    .org 0x26656-ORIGIN
L_00026656:
    mov #0x10,r5
    .org 0x26658-ORIGIN
P_00026658:
    .byte 0x00
    .org 0x26659-ORIGIN
P_00026659:
    .byte 0x02
    .org 0x2665a-ORIGIN
P_0002665a:
    .byte 0x6b
    .org 0x2665b-ORIGIN
P_0002665b:
    .byte 0x28
    .org 0x2665c-ORIGIN
P_0002665c:
    .byte 0x00
    .org 0x2665d-ORIGIN
P_0002665d:
    .byte 0x02
    .org 0x2665e-ORIGIN
P_0002665e:
    .byte 0x6b
    .org 0x2665f-ORIGIN
P_0002665f:
    .byte 0x84
    .org 0x26af8-ORIGIN
L_00026af8:
    cmp/hs r0,r2
    .org 0x26afa-ORIGIN
L_00026afa:
    bt L_00026b14
    .org 0x26afc-ORIGIN
L_00026afc:
    mov.l r0,@-r15
    .org 0x26afe-ORIGIN
L_00026afe:
    sub r2,r0
    .org 0x26b00-ORIGIN
L_00026b00:
    sts macl,r1
    .org 0x26b02-ORIGIN
L_00026b02:
    mul.l r3,r0
    .org 0x26b04-ORIGIN
L_00026b04:
    sts macl,r0
    .org 0x26b06-ORIGIN
L_00026b06:
    lds r1,macl
    .org 0x26b08-ORIGIN
L_00026b08:
    swap.w r0,r0
    .org 0x26b0a-ORIGIN
L_00026b0a:
    mov.l @r15+,r2
    .org 0x26b0c-ORIGIN
L_00026b0c:
    extu.w r0,r0
    .org 0x26b0e-ORIGIN
L_00026b0e:
    sub r0,r2
    .org 0x26b10-ORIGIN
L_00026b10:
    rts
    .org 0x26b12-ORIGIN
L_00026b12:
    mov r2,r0
    .org 0x26b14-ORIGIN
L_00026b14:
    sub r0,r2
    .org 0x26b16-ORIGIN
L_00026b16:
    sts macl,r1
    .org 0x26b18-ORIGIN
L_00026b18:
    mul.l r3,r2
    .org 0x26b1a-ORIGIN
L_00026b1a:
    sts macl,r2
    .org 0x26b1c-ORIGIN
L_00026b1c:
    lds r1,macl
    .org 0x26b1e-ORIGIN
L_00026b1e:
    swap.w r2,r2
    .org 0x26b20-ORIGIN
L_00026b20:
    extu.w r2,r2
    .org 0x26b22-ORIGIN
L_00026b22:
    rts
    .org 0x26b24-ORIGIN
L_00026b24:
    add r2,r0
    .org 0x26b28-ORIGIN
L_00026b28:
    mov.l r8,@-r15
    .org 0x26b2a-ORIGIN
L_00026b2a:
    sts.l pr,@-r15
    .org 0x26b2c-ORIGIN
L_00026b2c:
    sts macl,r7
    .org 0x26b2e-ORIGIN
L_00026b2e:
    mulu.w r5,r0
    .org 0x26b30-ORIGIN
L_00026b30:
    add r2,r4
    .org 0x26b32-ORIGIN
L_00026b32:
    sts macl,r0
    .org 0x26b34-ORIGIN
L_00026b34:
    lds r7,macl
    .org 0x26b36-ORIGIN
L_00026b36:
    shll r5
    .org 0x26b38-ORIGIN
L_00026b38:
    add r0,r4
    .org 0x26b3a-ORIGIN
L_00026b3a:
    add r4,r5
    .org 0x26b3c-ORIGIN
L_00026b3c:
    mov r1,r8
    .org 0x26b3e-ORIGIN
L_00026b3e:
    mov.l P_00026b80,r7
    .org 0x26b40-ORIGIN
L_00026b40:
    tst r3,r3
    .org 0x26b42-ORIGIN
L_00026b42:
    bt L_00026b6a
    .org 0x26b44-ORIGIN
L_00026b44:
    mov.w @r4,r1
    .org 0x26b46-ORIGIN
L_00026b46:
    mov.w @(0x2,r4),r0
    .org 0x26b48-ORIGIN
L_00026b48:
    extu.w r0,r2
    .org 0x26b4a-ORIGIN
L_00026b4a:
    jsr @r7
    .org 0x26b4c-ORIGIN
L_00026b4c:
    extu.w r1,r0
    .org 0x26b4e-ORIGIN
L_00026b4e:
    tst r8,r8
    .org 0x26b50-ORIGIN
L_00026b50:
    bt L_00026b7a
    .org 0x26b52-ORIGIN
L_00026b52:
    mov.l r0,@-r15
    .org 0x26b54-ORIGIN
L_00026b54:
    mov.w @r5,r1
    .org 0x26b56-ORIGIN
L_00026b56:
    mov.w @(0x2,r5),r0
    .org 0x26b58-ORIGIN
L_00026b58:
    extu.w r0,r2
    .org 0x26b5a-ORIGIN
L_00026b5a:
    jsr @r7
    .org 0x26b5c-ORIGIN
L_00026b5c:
    extu.w r1,r0
    .org 0x26b5e-ORIGIN
L_00026b5e:
    mov r0,r2
    .org 0x26b60-ORIGIN
L_00026b60:
    mov.l @r15+,r0
    .org 0x26b62-ORIGIN
L_00026b62:
    jsr @r7
    .org 0x26b64-ORIGIN
L_00026b64:
    mov r8,r3
    .org 0x26b66-ORIGIN
L_00026b66:
    bra L_00026b7a
    .org 0x26b68-ORIGIN
L_00026b68:
    nop
    .org 0x26b6a-ORIGIN
L_00026b6a:
    tst r8,r8
    .org 0x26b6c-ORIGIN
L_00026b6c:
    bt/s L_00026b7a
    .org 0x26b6e-ORIGIN
L_00026b6e:
    mov.w @r4,r0
    .org 0x26b70-ORIGIN
L_00026b70:
    mov.w @r5,r2
    .org 0x26b72-ORIGIN
L_00026b72:
    extu.w r0,r0
    .org 0x26b74-ORIGIN
L_00026b74:
    extu.w r2,r2
    .org 0x26b76-ORIGIN
L_00026b76:
    jsr @r7
    .org 0x26b78-ORIGIN
L_00026b78:
    mov r8,r3
    .org 0x26b7a-ORIGIN
L_00026b7a:
    lds.l @r15+,pr
    .org 0x26b7c-ORIGIN
L_00026b7c:
    rts
    .org 0x26b7e-ORIGIN
L_00026b7e:
    mov.l @r15+,r8
    .org 0x26b80-ORIGIN
P_00026b80:
    .byte 0x00
    .org 0x26b81-ORIGIN
P_00026b81:
    .byte 0x02
    .org 0x26b82-ORIGIN
P_00026b82:
    .byte 0x6a
    .org 0x26b83-ORIGIN
P_00026b83:
    .byte 0xf8
    .org 0x26b84-ORIGIN
L_00026b84:
    mov r4,r3
    .org 0x26b86-ORIGIN
L_00026b86:
    mov.w @(r0,r4),r1
    .org 0x26b88-ORIGIN
L_00026b88:
    extu.w r1,r1
    .org 0x26b8a-ORIGIN
L_00026b8a:
    cmp/eq r1,r5
    .org 0x26b8c-ORIGIN
L_00026b8c:
    bt L_00026bbc
    .org 0x26b8e-ORIGIN
L_00026b8e:
    cmp/hi r1,r5
    .org 0x26b90-ORIGIN
L_00026b90:
    bf L_00026bb4
    .org 0x26b92-ORIGIN
L_00026b92:
    cmp/eq r4,r3
    .org 0x26b94-ORIGIN
L_00026b94:
    bt L_00026bbc
    .org 0x26b96-ORIGIN
L_00026b96:
    sub r1,r5
    .org 0x26b98-ORIGIN
L_00026b98:
    shll16 r5
    .org 0x26b9a-ORIGIN
L_00026b9a:
    add r4,r0
    .org 0x26b9c-ORIGIN
L_00026b9c:
    mov.w @r0,r1
    .org 0x26b9e-ORIGIN
L_00026b9e:
    mov.w @(0x2,r0),r0
    .org 0x26ba0-ORIGIN
L_00026ba0:
    extu.w r1,r1
    .org 0x26ba2-ORIGIN
L_00026ba2:
    extu.w r0,r0
    .org 0x26ba4-ORIGIN
L_00026ba4:
    sts.l pr,@-r15
    .org 0x26ba6-ORIGIN
L_00026ba6:
    mov.l P_00026bc0,r2
    .org 0x26ba8-ORIGIN
L_00026ba8:
    sub r1,r0
    .org 0x26baa-ORIGIN
L_00026baa:
    jsr @r2
    .org 0x26bac-ORIGIN
L_00026bac:
    mov r5,r1
    .org 0x26bae-ORIGIN
L_00026bae:
    lds.l @r15+,pr
    .org 0x26bb0-ORIGIN
L_00026bb0:
    rts
    .org 0x26bb2-ORIGIN
L_00026bb2:
    mov r0,r5
    .org 0x26bb4-ORIGIN
L_00026bb4:
    add #-0x2,r4
    .org 0x26bb6-ORIGIN
L_00026bb6:
    cmp/pz r4
    .org 0x26bb8-ORIGIN
L_00026bb8:
    bt L_00026b86
    .org 0x26bba-ORIGIN
L_00026bba:
    mov #0x0,r4
    .org 0x26bbc-ORIGIN
L_00026bbc:
    rts
    .org 0x26bbe-ORIGIN
L_00026bbe:
    mov #0x0,r5
    .org 0x26bc0-ORIGIN
P_00026bc0:
    .byte 0x00
    .org 0x26bc1-ORIGIN
P_00026bc1:
    .byte 0x02
    .org 0x26bc2-ORIGIN
P_00026bc2:
    .byte 0x6d
    .org 0x26bc3-ORIGIN
P_00026bc3:
    .byte 0x10
    .org 0x26d10-ORIGIN
L_00026d10:
    tst r0,r0
    .org 0x26d12-ORIGIN
L_00026d12:
    bt L_00026da2
    .org 0x26d14-ORIGIN
L_00026d14:
    mov.l r2,@-r15
    .org 0x26d16-ORIGIN
L_00026d16:
    mov #0x0,r2
    .org 0x26d18-ORIGIN
L_00026d18:
    div0u
    .org 0x26d1a-ORIGIN
L_00026d1a:
    rotcl r1
    .org 0x26d1c-ORIGIN
L_00026d1c:
    div1 r0,r2
    .org 0x26d1e-ORIGIN
L_00026d1e:
    rotcl r1
    .org 0x26d20-ORIGIN
L_00026d20:
    div1 r0,r2
    .org 0x26d22-ORIGIN
L_00026d22:
    rotcl r1
    .org 0x26d24-ORIGIN
L_00026d24:
    div1 r0,r2
    .org 0x26d26-ORIGIN
L_00026d26:
    rotcl r1
    .org 0x26d28-ORIGIN
L_00026d28:
    div1 r0,r2
    .org 0x26d2a-ORIGIN
L_00026d2a:
    rotcl r1
    .org 0x26d2c-ORIGIN
L_00026d2c:
    div1 r0,r2
    .org 0x26d2e-ORIGIN
L_00026d2e:
    rotcl r1
    .org 0x26d30-ORIGIN
L_00026d30:
    div1 r0,r2
    .org 0x26d32-ORIGIN
L_00026d32:
    rotcl r1
    .org 0x26d34-ORIGIN
L_00026d34:
    div1 r0,r2
    .org 0x26d36-ORIGIN
L_00026d36:
    rotcl r1
    .org 0x26d38-ORIGIN
L_00026d38:
    div1 r0,r2
    .org 0x26d3a-ORIGIN
L_00026d3a:
    rotcl r1
    .org 0x26d3c-ORIGIN
L_00026d3c:
    div1 r0,r2
    .org 0x26d3e-ORIGIN
L_00026d3e:
    rotcl r1
    .org 0x26d40-ORIGIN
L_00026d40:
    div1 r0,r2
    .org 0x26d42-ORIGIN
L_00026d42:
    rotcl r1
    .org 0x26d44-ORIGIN
L_00026d44:
    div1 r0,r2
    .org 0x26d46-ORIGIN
L_00026d46:
    rotcl r1
    .org 0x26d48-ORIGIN
L_00026d48:
    div1 r0,r2
    .org 0x26d4a-ORIGIN
L_00026d4a:
    rotcl r1
    .org 0x26d4c-ORIGIN
L_00026d4c:
    div1 r0,r2
    .org 0x26d4e-ORIGIN
L_00026d4e:
    rotcl r1
    .org 0x26d50-ORIGIN
L_00026d50:
    div1 r0,r2
    .org 0x26d52-ORIGIN
L_00026d52:
    rotcl r1
    .org 0x26d54-ORIGIN
L_00026d54:
    div1 r0,r2
    .org 0x26d56-ORIGIN
L_00026d56:
    rotcl r1
    .org 0x26d58-ORIGIN
L_00026d58:
    div1 r0,r2
    .org 0x26d5a-ORIGIN
L_00026d5a:
    rotcl r1
    .org 0x26d5c-ORIGIN
L_00026d5c:
    div1 r0,r2
    .org 0x26d5e-ORIGIN
L_00026d5e:
    rotcl r1
    .org 0x26d60-ORIGIN
L_00026d60:
    div1 r0,r2
    .org 0x26d62-ORIGIN
L_00026d62:
    rotcl r1
    .org 0x26d64-ORIGIN
L_00026d64:
    div1 r0,r2
    .org 0x26d66-ORIGIN
L_00026d66:
    rotcl r1
    .org 0x26d68-ORIGIN
L_00026d68:
    div1 r0,r2
    .org 0x26d6a-ORIGIN
L_00026d6a:
    rotcl r1
    .org 0x26d6c-ORIGIN
L_00026d6c:
    div1 r0,r2
    .org 0x26d6e-ORIGIN
L_00026d6e:
    rotcl r1
    .org 0x26d70-ORIGIN
L_00026d70:
    div1 r0,r2
    .org 0x26d72-ORIGIN
L_00026d72:
    rotcl r1
    .org 0x26d74-ORIGIN
L_00026d74:
    div1 r0,r2
    .org 0x26d76-ORIGIN
L_00026d76:
    rotcl r1
    .org 0x26d78-ORIGIN
L_00026d78:
    div1 r0,r2
    .org 0x26d7a-ORIGIN
L_00026d7a:
    rotcl r1
    .org 0x26d7c-ORIGIN
L_00026d7c:
    div1 r0,r2
    .org 0x26d7e-ORIGIN
L_00026d7e:
    rotcl r1
    .org 0x26d80-ORIGIN
L_00026d80:
    div1 r0,r2
    .org 0x26d82-ORIGIN
L_00026d82:
    rotcl r1
    .org 0x26d84-ORIGIN
L_00026d84:
    div1 r0,r2
    .org 0x26d86-ORIGIN
L_00026d86:
    rotcl r1
    .org 0x26d88-ORIGIN
L_00026d88:
    div1 r0,r2
    .org 0x26d8a-ORIGIN
L_00026d8a:
    rotcl r1
    .org 0x26d8c-ORIGIN
L_00026d8c:
    div1 r0,r2
    .org 0x26d8e-ORIGIN
L_00026d8e:
    rotcl r1
    .org 0x26d90-ORIGIN
L_00026d90:
    div1 r0,r2
    .org 0x26d92-ORIGIN
L_00026d92:
    rotcl r1
    .org 0x26d94-ORIGIN
L_00026d94:
    div1 r0,r2
    .org 0x26d96-ORIGIN
L_00026d96:
    rotcl r1
    .org 0x26d98-ORIGIN
L_00026d98:
    div1 r0,r2
    .org 0x26d9a-ORIGIN
L_00026d9a:
    rotcl r1
    .org 0x26d9c-ORIGIN
L_00026d9c:
    mov.l @r15+,r2
    .org 0x26d9e-ORIGIN
L_00026d9e:
    rts
    .org 0x26da0-ORIGIN
L_00026da0:
    mov r1,r0
    .org 0x26da2-ORIGIN
L_00026da2:
    rts
    .org 0x26da4-ORIGIN
L_00026da4:
    mov #0x0,r0
    .org 0x74028-ORIGIN
L_00074028:
    mov.l r9,@-r15
    .org 0x7402a-ORIGIN
L_0007402a:
    mov.l r10,@-r15
    .org 0x7402c-ORIGIN
L_0007402c:
    mov.l r11,@-r15
    .org 0x7402e-ORIGIN
L_0007402e:
    mov.l r12,@-r15
    .org 0x74030-ORIGIN
L_00074030:
    mov.l r13,@-r15
    .org 0x74032-ORIGIN
L_00074032:
    mov.l r14,@-r15
    .org 0x74034-ORIGIN
L_00074034:
    sts.l pr,@-r15
    .org 0x74036-ORIGIN
L_00074036:
    stc.l gbr,@-r15
    .org 0x74038-ORIGIN
L_00074038:
    mov.l P_00074140,r0
    .org 0x7403a-ORIGIN
L_0007403a:
    ldc r0,gbr
    .org 0x7403c-ORIGIN
L_0007403c:
    add #-0x4,r15
    .org 0x7403e-ORIGIN
L_0007403e:
    mov.l P_00074144,r6
    .org 0x74040-ORIGIN
L_00074040:
    mov.b @(0x9,r6),r0
    .org 0x74042-ORIGIN
L_00074042:
    tst #0x80,r0
    .org 0x74044-ORIGIN
L_00074044:
    bt/s L_00074058
    .org 0x74046-ORIGIN
L_00074046:
    mov.w @(0x3e,gbr),r0
    .org 0x74048-ORIGIN
L_00074048:
    extu.w r0,r4
    .org 0x7404a-ORIGIN
L_0007404a:
    mov.w @(0x4e,gbr),r0
    .org 0x7404c-ORIGIN
L_0007404c:
    extu.w r0,r2
    .org 0x7404e-ORIGIN
L_0007404e:
    cmp/ge r2,r4
    .org 0x74050-ORIGIN
L_00074050:
    bf L_00074054
    .org 0x74052-ORIGIN
L_00074052:
    mov r4,r2
    .org 0x74054-ORIGIN
L_00074054:
    bra L_0007405a
    .org 0x74056-ORIGIN
L_00074056:
    mov r2,r13
    .org 0x74058-ORIGIN
L_00074058:
    mov r0,r13
    .org 0x7405a-ORIGIN
L_0007405a:
    mov r13,r0
    .org 0x7405c-ORIGIN
L_0007405c:
    mov.w r0,@(0x2,r15)
    .org 0x7405e-ORIGIN
L_0007405e:
    mov.w @(0x17c,gbr),r0
    .org 0x74060-ORIGIN
L_00074060:
    mov #-0x80,r14
    .org 0x74062-ORIGIN
L_00074062:
    mov.l P_00074148,r4
    .org 0x74064-ORIGIN
L_00074064:
    shll8 r14
    .org 0x74066-ORIGIN
L_00074066:
    mov.l P_0007414c,r10
    .org 0x74068-ORIGIN
L_00074068:
    extu.w r0,r7
    .org 0x7406a-ORIGIN
L_0007406a:
    mov.l P_00074150,r11
    .org 0x7406c-ORIGIN
L_0007406c:
    mov.l P_00074154,r12
    .org 0x7406e-ORIGIN
L_0007406e:
    mov r10,r5
    .org 0x74070-ORIGIN
L_00074070:
    mov.l P_00074158,r9
    .org 0x74072-ORIGIN
L_00074072:
    jsr @r12
    .org 0x74074-ORIGIN
L_00074074:
    mov r11,r6
    .org 0x74076-ORIGIN
L_00074076:
    extu.w r0,r2
    .org 0x74078-ORIGIN
L_00074078:
    mov.w P_00074138,r0
    .org 0x7407a-ORIGIN
L_0007407a:
    exts.w r2,r2
    .org 0x7407c-ORIGIN
L_0007407c:
    mov.l P_0007415c,r4
    .org 0x7407e-ORIGIN
L_0007407e:
    add r14,r2
    .org 0x74080-ORIGIN
L_00074080:
    mov r10,r5
    .org 0x74082-ORIGIN
L_00074082:
    mov.w r2,@(r0,r9)
    .org 0x74084-ORIGIN
L_00074084:
    mov r13,r0
    .org 0x74086-ORIGIN
L_00074086:
    mov.w r0,@(0x2,r15)
    .org 0x74088-ORIGIN
L_00074088:
    mov r11,r6
    .org 0x7408a-ORIGIN
L_0007408a:
    mov.w @(0x17c,gbr),r0
    .org 0x7408c-ORIGIN
L_0007408c:
    jsr @r12
    .org 0x7408e-ORIGIN
L_0007408e:
    extu.w r0,r7
    .org 0x74090-ORIGIN
L_00074090:
    extu.w r0,r2
    .org 0x74092-ORIGIN
L_00074092:
    mov.w P_0007413a,r0
    .org 0x74094-ORIGIN
L_00074094:
    exts.w r2,r2
    .org 0x74096-ORIGIN
L_00074096:
    add r14,r2
    .org 0x74098-ORIGIN
L_00074098:
    mov.w r2,@(r0,r9)
    .org 0x7409a-ORIGIN
L_0007409a:
    add #0x4,r15
    .org 0x7409c-ORIGIN
L_0007409c:
    ldc.l @r15+,gbr
    .org 0x7409e-ORIGIN
L_0007409e:
    lds.l @r15+,pr
    .org 0x740a0-ORIGIN
L_000740a0:
    mov.l @r15+,r14
    .org 0x740a2-ORIGIN
L_000740a2:
    mov.l @r15+,r13
    .org 0x740a4-ORIGIN
L_000740a4:
    mov.l @r15+,r12
    .org 0x740a6-ORIGIN
L_000740a6:
    mov.l @r15+,r11
    .org 0x740a8-ORIGIN
L_000740a8:
    mov.l @r15+,r10
    .org 0x740aa-ORIGIN
L_000740aa:
    rts
    .org 0x740ac-ORIGIN
L_000740ac:
    mov.l @r15+,r9
    .org 0x740ae-ORIGIN
L_000740ae:
    mov.l P_00074160,r6
    .org 0x740b0-ORIGIN
L_000740b0:
    mov.l P_00074158,r4
    .org 0x740b2-ORIGIN
L_000740b2:
    mov.b @r6,r0
    .org 0x740b4-ORIGIN
L_000740b4:
    mov.l P_00074164,r5
    .org 0x740b6-ORIGIN
L_000740b6:
    tst #0x4,r0
    .org 0x740b8-ORIGIN
L_000740b8:
    mov.w P_0007413c,r0
    .org 0x740ba-ORIGIN
L_000740ba:
    mov.w @r5,r6
    .org 0x740bc-ORIGIN
L_000740bc:
    mov.w @(r0,r4),r2
    .org 0x740be-ORIGIN
L_000740be:
    bt/s L_000740d2
    .org 0x740c0-ORIGIN
L_000740c0:
    extu.w r2,r2
    .org 0x740c2-ORIGIN
L_000740c2:
    extu.w r6,r6
    .org 0x740c4-ORIGIN
L_000740c4:
    add r6,r2
    .org 0x740c6-ORIGIN
L_000740c6:
    mov #-0x1,r6
    .org 0x740c8-ORIGIN
L_000740c8:
    extu.w r6,r6
    .org 0x740ca-ORIGIN
L_000740ca:
    cmp/gt r6,r2
    .org 0x740cc-ORIGIN
L_000740cc:
    bf L_000740dc
    .org 0x740ce-ORIGIN
L_000740ce:
    bra L_000740dc
    .org 0x740d0-ORIGIN
L_000740d0:
    mov r6,r2
    .org 0x740d2-ORIGIN
L_000740d2:
    extu.w r6,r5
    .org 0x740d4-ORIGIN
L_000740d4:
    sub r5,r2
    .org 0x740d6-ORIGIN
L_000740d6:
    cmp/pz r2
    .org 0x740d8-ORIGIN
L_000740d8:
    bt L_000740dc
    .org 0x740da-ORIGIN
L_000740da:
    mov #0x0,r2
    .org 0x740dc-ORIGIN
L_000740dc:
    mov.w P_0007413c,r0
    .org 0x740de-ORIGIN
L_000740de:
    rts
    .org 0x740e0-ORIGIN
L_000740e0:
    mov.w r2,@(r0,r4)
    .org 0x740e2-ORIGIN
L_000740e2:
    sts.l pr,@-r15
    .org 0x740e4-ORIGIN
L_000740e4:
    sts.l macl,@-r15
    .org 0x740e6-ORIGIN
L_000740e6:
    bsr L_00074028
    .org 0x740e8-ORIGIN
L_000740e8:
    nop
    .org 0x740ea-ORIGIN
L_000740ea:
    bsr L_000740ae
    .org 0x740ec-ORIGIN
L_000740ec:
    nop
    .org 0x740ee-ORIGIN
L_000740ee:
    mov.l P_00074158,r7
    .org 0x740f0-ORIGIN
L_000740f0:
    mov.w P_0007413c,r0
    .org 0x740f2-ORIGIN
L_000740f2:
    mov.w @(r0,r7),r5
    .org 0x740f4-ORIGIN
L_000740f4:
    extu.w r5,r4
    .org 0x740f6-ORIGIN
L_000740f6:
    tst r4,r4
    .org 0x740f8-ORIGIN
L_000740f8:
    bf L_00074100
    .org 0x740fa-ORIGIN
L_000740fa:
    mov.w P_00074138,r0
    .org 0x740fc-ORIGIN
L_000740fc:
    bra L_0007412c
    .org 0x740fe-ORIGIN
L_000740fe:
    mov.w @(r0,r7),r2
    .org 0x74100-ORIGIN
L_00074100:
    mov #-0x1,r6
    .org 0x74102-ORIGIN
L_00074102:
    extu.w r6,r6
    .org 0x74104-ORIGIN
L_00074104:
    cmp/eq r6,r4
    .org 0x74106-ORIGIN
L_00074106:
    bf L_0007410e
    .org 0x74108-ORIGIN
L_00074108:
    mov.w P_0007413a,r0
    .org 0x7410a-ORIGIN
L_0007410a:
    bra L_0007412a
    .org 0x7410c-ORIGIN
L_0007410c:
    mov.w @(r0,r7),r6
    .org 0x7410e-ORIGIN
L_0007410e:
    mov.w P_00074138,r0
    .org 0x74110-ORIGIN
L_00074110:
    mov #0x1,r2
    .org 0x74112-ORIGIN
L_00074112:
    shll16 r2
    .org 0x74114-ORIGIN
L_00074114:
    mov.w @(r0,r7),r6
    .org 0x74116-ORIGIN
L_00074116:
    sub r4,r2
    .org 0x74118-ORIGIN
L_00074118:
    mov.w P_0007413a,r0
    .org 0x7411a-ORIGIN
L_0007411a:
    mul.l r6,r2
    .org 0x7411c-ORIGIN
L_0007411c:
    mov.w @(r0,r7),r2
    .org 0x7411e-ORIGIN
L_0007411e:
    sts macl,r5
    .org 0x74120-ORIGIN
L_00074120:
    mul.l r2,r4
    .org 0x74122-ORIGIN
L_00074122:
    sts macl,r2
    .org 0x74124-ORIGIN
L_00074124:
    add r2,r5
    .org 0x74126-ORIGIN
L_00074126:
    swap.w r5,r6
    .org 0x74128-ORIGIN
L_00074128:
    exts.w r6,r6
    .org 0x7412a-ORIGIN
L_0007412a:
    mov r6,r2
    .org 0x7412c-ORIGIN
L_0007412c:
    mov.w P_0007413e,r0
    .org 0x7412e-ORIGIN
L_0007412e:
    mov.w r2,@(r0,r7)
    .org 0x74130-ORIGIN
L_00074130:
    lds.l @r15+,macl
    .org 0x74132-ORIGIN
L_00074132:
    lds.l @r15+,pr
    .org 0x74134-ORIGIN
L_00074134:
    rts
    .org 0x74136-ORIGIN
L_00074136:
    nop
    .org 0x74138-ORIGIN
P_00074138:
    .byte 0x0a
    .org 0x74139-ORIGIN
P_00074139:
    .byte 0x70
    .org 0x7413a-ORIGIN
P_0007413a:
    .byte 0x0a
    .org 0x7413b-ORIGIN
P_0007413b:
    .byte 0x72
    .org 0x7413c-ORIGIN
P_0007413c:
    .byte 0x0a
    .org 0x7413d-ORIGIN
P_0007413d:
    .byte 0x80
    .org 0x7413e-ORIGIN
P_0007413e:
    .byte 0x0a
    .org 0x7413f-ORIGIN
P_0007413f:
    .byte 0x6a
    .org 0x74140-ORIGIN
P_00074140:
    .byte 0xff
    .org 0x74141-ORIGIN
P_00074141:
    .byte 0xff
    .org 0x74142-ORIGIN
P_00074142:
    .byte 0x10
    .org 0x74143-ORIGIN
P_00074143:
    .byte 0x94
    .org 0x74144-ORIGIN
P_00074144:
    .byte 0xff
    .org 0x74145-ORIGIN
P_00074145:
    .byte 0xff
    .org 0x74146-ORIGIN
P_00074146:
    .byte 0x42
    .org 0x74147-ORIGIN
P_00074147:
    .byte 0x4c
    .org 0x74148-ORIGIN
P_00074148:
    .byte 0x00
    .org 0x74149-ORIGIN
P_00074149:
    .byte 0x01
    .org 0x7414a-ORIGIN
P_0007414a:
    .byte 0x71
    .org 0x7414b-ORIGIN
P_0007414b:
    .byte 0xc8
    .org 0x7414c-ORIGIN
P_0007414c:
    .byte 0x00
    .org 0x7414d-ORIGIN
P_0007414d:
    .byte 0x01
    .org 0x7414e-ORIGIN
P_0007414e:
    .byte 0x89
    .org 0x7414f-ORIGIN
P_0007414f:
    .byte 0x16
    .org 0x74150-ORIGIN
P_00074150:
    .byte 0x00
    .org 0x74151-ORIGIN
P_00074151:
    .byte 0x01
    .org 0x74152-ORIGIN
P_00074152:
    .byte 0x89
    .org 0x74153-ORIGIN
P_00074153:
    .byte 0x36
    .org 0x74154-ORIGIN
P_00074154:
    .byte 0x00
    .org 0x74155-ORIGIN
P_00074155:
    .byte 0x02
    .org 0x74156-ORIGIN
P_00074156:
    .byte 0x66
    .org 0x74157-ORIGIN
P_00074157:
    .byte 0x28
    .org 0x74158-ORIGIN
P_00074158:
    .byte 0xff
    .org 0x74159-ORIGIN
P_00074159:
    .byte 0xff
    .org 0x7415a-ORIGIN
P_0007415a:
    .byte 0x12
    .org 0x7415b-ORIGIN
P_0007415b:
    .byte 0x8c
    .org 0x7415c-ORIGIN
P_0007415c:
    .byte 0x00
    .org 0x7415d-ORIGIN
P_0007415d:
    .byte 0x01
    .org 0x7415e-ORIGIN
P_0007415e:
    .byte 0x6f
    .org 0x7415f-ORIGIN
P_0007415f:
    .byte 0xc8
    .org 0x74160-ORIGIN
P_00074160:
    .byte 0xff
    .org 0x74161-ORIGIN
P_00074161:
    .byte 0xff
    .org 0x74162-ORIGIN
P_00074162:
    .byte 0x24
    .org 0x74163-ORIGIN
P_00074163:
    .byte 0x5c
    .org 0x74164-ORIGIN
P_00074164:
    .byte 0x00
    .org 0x74165-ORIGIN
P_00074165:
    .byte 0x01
    .org 0x74166-ORIGIN
P_00074166:
    .byte 0x62
    .org 0x74167-ORIGIN
P_00074167:
    .byte 0xdc
