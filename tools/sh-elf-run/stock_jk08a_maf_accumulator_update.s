! Complete stock native index1 MAF accumulator updater and real unsigned division/byte curves.
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
    .org 0x3aa12-ORIGIN
L_0003aa12:
    mov.l r9,@-r15
    .org 0x3aa14-ORIGIN
L_0003aa14:
    mov.l r10,@-r15
    .org 0x3aa16-ORIGIN
L_0003aa16:
    mov.l r12,@-r15
    .org 0x3aa18-ORIGIN
L_0003aa18:
    mov.l r13,@-r15
    .org 0x3aa1a-ORIGIN
L_0003aa1a:
    mov.l r14,@-r15
    .org 0x3aa1c-ORIGIN
L_0003aa1c:
    sts.l pr,@-r15
    .org 0x3aa1e-ORIGIN
L_0003aa1e:
    sts.l macl,@-r15
    .org 0x3aa20-ORIGIN
L_0003aa20:
    stc.l gbr,@-r15
    .org 0x3aa22-ORIGIN
L_0003aa22:
    mov.l P_0003ab7c,r0
    .org 0x3aa24-ORIGIN
L_0003aa24:
    ldc r0,gbr
    .org 0x3aa26-ORIGIN
L_0003aa26:
    add #-0x18,r15
    .org 0x3aa28-ORIGIN
L_0003aa28:
    mov #-0x4a,r2
    .org 0x3aa2a-ORIGIN
L_0003aa2a:
    mov.l P_0003ab80,r9
    .org 0x3aa2c-ORIGIN
L_0003aa2c:
    stc gbr,r6
    .org 0x3aa2e-ORIGIN
L_0003aa2e:
    extu.b r2,r2
    .org 0x3aa30-ORIGIN
L_0003aa30:
    mov.l P_0003ab84,r14
    .org 0x3aa32-ORIGIN
L_0003aa32:
    extu.b r4,r7
    .org 0x3aa34-ORIGIN
L_0003aa34:
    add r2,r6
    .org 0x3aa36-ORIGIN
L_0003aa36:
    mov r7,r0
    .org 0x3aa38-ORIGIN
L_0003aa38:
    mov.b r0,@(0x3,r15)
    .org 0x3aa3a-ORIGIN
L_0003aa3a:
    mov r7,r12
    .org 0x3aa3c-ORIGIN
L_0003aa3c:
    mov.b @(r0,r6),r2
    .org 0x3aa3e-ORIGIN
L_0003aa3e:
    shll2 r12
    .org 0x3aa40-ORIGIN
L_0003aa40:
    mov.b @(0x1,r9),r0
    .org 0x3aa42-ORIGIN
L_0003aa42:
    cmp/hs r0,r2
    .org 0x3aa44-ORIGIN
L_0003aa44:
    bt/s L_0003aa9e
    .org 0x3aa46-ORIGIN
L_0003aa46:
    mov.b @r14,r4
    .org 0x3aa48-ORIGIN
L_0003aa48:
    mov.l P_0003ab88,r2
    .org 0x3aa4a-ORIGIN
L_0003aa4a:
    mov.b @(0x3,r2),r0
    .org 0x3aa4c-ORIGIN
L_0003aa4c:
    mov r0,r6
    .org 0x3aa4e-ORIGIN
L_0003aa4e:
    mov.b @(0x2,r9),r0
    .org 0x3aa50-ORIGIN
L_0003aa50:
    cmp/hs r0,r6
    .org 0x3aa52-ORIGIN
L_0003aa52:
    bt L_0003aa9e
    .org 0x3aa54-ORIGIN
L_0003aa54:
    mov.l P_0003ab8c,r5
    .org 0x3aa56-ORIGIN
L_0003aa56:
    mov r7,r0
    .org 0x3aa58-ORIGIN
L_0003aa58:
    shll r0
    .org 0x3aa5a-ORIGIN
L_0003aa5a:
    add #0x4,r5
    .org 0x3aa5c-ORIGIN
L_0003aa5c:
    mov.w @(r0,r5),r6
    .org 0x3aa5e-ORIGIN
L_0003aa5e:
    mov.l P_0003ab90,r5
    .org 0x3aa60-ORIGIN
L_0003aa60:
    mov.w @r5,r2
    .org 0x3aa62-ORIGIN
L_0003aa62:
    cmp/hs r2,r6
    .org 0x3aa64-ORIGIN
L_0003aa64:
    bf L_0003aa9e
    .org 0x3aa66-ORIGIN
L_0003aa66:
    stc gbr,r6
    .org 0x3aa68-ORIGIN
L_0003aa68:
    mov r4,r0
    .org 0x3aa6a-ORIGIN
L_0003aa6a:
    or #0x80,r0
    .org 0x3aa6c-ORIGIN
L_0003aa6c:
    mov.b r0,@r14
    .org 0x3aa6e-ORIGIN
L_0003aa6e:
    mov r7,r0
    .org 0x3aa70-ORIGIN
L_0003aa70:
    mov.b @(r0,r6),r2
    .org 0x3aa72-ORIGIN
L_0003aa72:
    mov.b @r9,r6
    .org 0x3aa74-ORIGIN
L_0003aa74:
    extu.b r2,r2
    .org 0x3aa76-ORIGIN
L_0003aa76:
    extu.b r6,r6
    .org 0x3aa78-ORIGIN
L_0003aa78:
    cmp/ge r6,r2
    .org 0x3aa7a-ORIGIN
L_0003aa7a:
    bf L_0003aa88
    .org 0x3aa7c-ORIGIN
L_0003aa7c:
    mov.b @(0xf,gbr),r0
    .org 0x3aa7e-ORIGIN
L_0003aa7e:
    mov r7,r6
    .org 0x3aa80-ORIGIN
L_0003aa80:
    add #0x1,r6
    .org 0x3aa82-ORIGIN
L_0003aa82:
    mov.l r0,@(0x8,r15)
    .org 0x3aa84-ORIGIN
L_0003aa84:
    or r6,r0
    .org 0x3aa86-ORIGIN
L_0003aa86:
    mov.b r0,@(0xf,gbr)
    .org 0x3aa88-ORIGIN
L_0003aa88:
    add #0x1,r2
    .org 0x3aa8a-ORIGIN
L_0003aa8a:
    mov #-0x1,r4
    .org 0x3aa8c-ORIGIN
L_0003aa8c:
    extu.w r2,r6
    .org 0x3aa8e-ORIGIN
L_0003aa8e:
    extu.b r4,r4
    .org 0x3aa90-ORIGIN
L_0003aa90:
    cmp/gt r4,r6
    .org 0x3aa92-ORIGIN
L_0003aa92:
    bt L_0003aa96
    .org 0x3aa94-ORIGIN
L_0003aa94:
    mov r6,r4
    .org 0x3aa96-ORIGIN
L_0003aa96:
    stc gbr,r2
    .org 0x3aa98-ORIGIN
L_0003aa98:
    mov r7,r0
    .org 0x3aa9a-ORIGIN
L_0003aa9a:
    bra L_0003aaac
    .org 0x3aa9c-ORIGIN
L_0003aa9c:
    mov.b r4,@(r0,r2)
    .org 0x3aa9e-ORIGIN
L_0003aa9e:
    stc gbr,r2
    .org 0x3aaa0-ORIGIN
L_0003aaa0:
    mov r4,r0
    .org 0x3aaa2-ORIGIN
L_0003aaa2:
    and #0x7f,r0
    .org 0x3aaa4-ORIGIN
L_0003aaa4:
    mov #0x0,r6
    .org 0x3aaa6-ORIGIN
L_0003aaa6:
    mov.b r0,@r14
    .org 0x3aaa8-ORIGIN
L_0003aaa8:
    mov r7,r0
    .org 0x3aaaa-ORIGIN
L_0003aaaa:
    mov.b r6,@(r0,r2)
    .org 0x3aaac-ORIGIN
L_0003aaac:
    mov.b @(0xf,gbr),r0
    .org 0x3aaae-ORIGIN
L_0003aaae:
    mov r7,r13
    .org 0x3aab0-ORIGIN
L_0003aab0:
    add #0x1,r13
    .org 0x3aab2-ORIGIN
L_0003aab2:
    extu.b r0,r6
    .org 0x3aab4-ORIGIN
L_0003aab4:
    tst r13,r6
    .org 0x3aab6-ORIGIN
L_0003aab6:
    bt/s L_0003ab10
    .org 0x3aab8-ORIGIN
L_0003aab8:
    mov.b @r14,r4
    .org 0x3aaba-ORIGIN
L_0003aaba:
    mov.l P_0003ab8c,r5
    .org 0x3aabc-ORIGIN
L_0003aabc:
    mov r7,r0
    .org 0x3aabe-ORIGIN
L_0003aabe:
    shll r0
    .org 0x3aac0-ORIGIN
L_0003aac0:
    add #0x4,r5
    .org 0x3aac2-ORIGIN
L_0003aac2:
    mov.w @(r0,r5),r6
    .org 0x3aac4-ORIGIN
L_0003aac4:
    mov.l P_0003ab94,r5
    .org 0x3aac6-ORIGIN
L_0003aac6:
    mov.w @r5,r2
    .org 0x3aac8-ORIGIN
L_0003aac8:
    cmp/hs r2,r6
    .org 0x3aaca-ORIGIN
L_0003aaca:
    bt L_0003ab10
    .org 0x3aacc-ORIGIN
L_0003aacc:
    mov.l P_0003ab98,r5
    .org 0x3aace-ORIGIN
L_0003aace:
    mov #0x74,r0
    .org 0x3aad0-ORIGIN
L_0003aad0:
    mov.b @(r0,r5),r6
    .org 0x3aad2-ORIGIN
L_0003aad2:
    mov.b @(0x3,r9),r0
    .org 0x3aad4-ORIGIN
L_0003aad4:
    cmp/hs r0,r6
    .org 0x3aad6-ORIGIN
L_0003aad6:
    bf L_0003ab10
    .org 0x3aad8-ORIGIN
L_0003aad8:
    stc gbr,r2
    .org 0x3aada-ORIGIN
L_0003aada:
    mov r4,r0
    .org 0x3aadc-ORIGIN
L_0003aadc:
    or #0x40,r0
    .org 0x3aade-ORIGIN
L_0003aade:
    add #0x2,r2
    .org 0x3aae0-ORIGIN
L_0003aae0:
    mov.b r0,@r14
    .org 0x3aae2-ORIGIN
L_0003aae2:
    mov r7,r0
    .org 0x3aae4-ORIGIN
L_0003aae4:
    mov.b @(r0,r2),r6
    .org 0x3aae6-ORIGIN
L_0003aae6:
    mov.b @r9,r2
    .org 0x3aae8-ORIGIN
L_0003aae8:
    extu.b r6,r6
    .org 0x3aaea-ORIGIN
L_0003aaea:
    extu.b r2,r4
    .org 0x3aaec-ORIGIN
L_0003aaec:
    cmp/ge r4,r6
    .org 0x3aaee-ORIGIN
L_0003aaee:
    bf L_0003aafc
    .org 0x3aaf0-ORIGIN
L_0003aaf0:
    mov.b @(0x10,gbr),r0
    .org 0x3aaf2-ORIGIN
L_0003aaf2:
    mov r7,r2
    .org 0x3aaf4-ORIGIN
L_0003aaf4:
    add #0x1,r2
    .org 0x3aaf6-ORIGIN
L_0003aaf6:
    mov.l r0,@(0xc,r15)
    .org 0x3aaf8-ORIGIN
L_0003aaf8:
    or r2,r0
    .org 0x3aafa-ORIGIN
L_0003aafa:
    mov.b r0,@(0x10,gbr)
    .org 0x3aafc-ORIGIN
L_0003aafc:
    add #0x1,r6
    .org 0x3aafe-ORIGIN
L_0003aafe:
    mov #-0x1,r4
    .org 0x3ab00-ORIGIN
L_0003ab00:
    extu.w r6,r5
    .org 0x3ab02-ORIGIN
L_0003ab02:
    extu.b r4,r6
    .org 0x3ab04-ORIGIN
L_0003ab04:
    cmp/gt r6,r5
    .org 0x3ab06-ORIGIN
L_0003ab06:
    bt L_0003ab0a
    .org 0x3ab08-ORIGIN
L_0003ab08:
    mov r5,r6
    .org 0x3ab0a-ORIGIN
L_0003ab0a:
    stc gbr,r2
    .org 0x3ab0c-ORIGIN
L_0003ab0c:
    bra L_0003ab1c
    .org 0x3ab0e-ORIGIN
L_0003ab0e:
    add #0x2,r2
    .org 0x3ab10-ORIGIN
L_0003ab10:
    stc gbr,r2
    .org 0x3ab12-ORIGIN
L_0003ab12:
    mov r4,r0
    .org 0x3ab14-ORIGIN
L_0003ab14:
    and #0xbf,r0
    .org 0x3ab16-ORIGIN
L_0003ab16:
    mov.b r0,@r14
    .org 0x3ab18-ORIGIN
L_0003ab18:
    add #0x2,r2
    .org 0x3ab1a-ORIGIN
L_0003ab1a:
    mov #0x0,r6
    .org 0x3ab1c-ORIGIN
L_0003ab1c:
    mov r7,r0
    .org 0x3ab1e-ORIGIN
L_0003ab1e:
    mov.b r6,@(r0,r2)
    .org 0x3ab20-ORIGIN
L_0003ab20:
    mov.b @(0x10,gbr),r0
    .org 0x3ab22-ORIGIN
L_0003ab22:
    extu.b r0,r6
    .org 0x3ab24-ORIGIN
L_0003ab24:
    tst r13,r6
    .org 0x3ab26-ORIGIN
L_0003ab26:
    bt L_0003ab9c
    .org 0x3ab28-ORIGIN
L_0003ab28:
    mov.b @(0x24,gbr),r0
    .org 0x3ab2a-ORIGIN
L_0003ab2a:
    extu.b r0,r4
    .org 0x3ab2c-ORIGIN
L_0003ab2c:
    tst r13,r4
    .org 0x3ab2e-ORIGIN
L_0003ab2e:
    bf L_0003abbc
    .org 0x3ab30-ORIGIN
L_0003ab30:
    stc gbr,r6
    .org 0x3ab32-ORIGIN
L_0003ab32:
    add #0x22,r6
    .org 0x3ab34-ORIGIN
L_0003ab34:
    mov r7,r0
    .org 0x3ab36-ORIGIN
L_0003ab36:
    mov.b @(r0,r6),r2
    .org 0x3ab38-ORIGIN
L_0003ab38:
    mov.b @r9,r6
    .org 0x3ab3a-ORIGIN
L_0003ab3a:
    extu.b r2,r2
    .org 0x3ab3c-ORIGIN
L_0003ab3c:
    extu.b r6,r5
    .org 0x3ab3e-ORIGIN
L_0003ab3e:
    sub r5,r2
    .org 0x3ab40-ORIGIN
L_0003ab40:
    mov r7,r5
    .org 0x3ab42-ORIGIN
L_0003ab42:
    extu.w r2,r6
    .org 0x3ab44-ORIGIN
L_0003ab44:
    cmp/pz r6
    .org 0x3ab46-ORIGIN
L_0003ab46:
    bt/s L_0003ab4c
    .org 0x3ab48-ORIGIN
L_0003ab48:
    add #0x1,r5
    .org 0x3ab4a-ORIGIN
L_0003ab4a:
    mov #0x0,r6
    .org 0x3ab4c-ORIGIN
L_0003ab4c:
    stc gbr,r2
    .org 0x3ab4e-ORIGIN
L_0003ab4e:
    add #0x20,r2
    .org 0x3ab50-ORIGIN
L_0003ab50:
    mov r7,r0
    .org 0x3ab52-ORIGIN
L_0003ab52:
    or r5,r4
    .org 0x3ab54-ORIGIN
L_0003ab54:
    mov.b r6,@(r0,r2)
    .org 0x3ab56-ORIGIN
L_0003ab56:
    mov r4,r0
    .org 0x3ab58-ORIGIN
L_0003ab58:
    bra L_0003abbc
    .org 0x3ab5a-ORIGIN
L_0003ab5a:
    mov.b r0,@(0x24,gbr)
    .org 0x3ab7c-ORIGIN
P_0003ab7c:
    .byte 0xff
    .org 0x3ab7d-ORIGIN
P_0003ab7d:
    .byte 0xff
    .org 0x3ab7e-ORIGIN
P_0003ab7e:
    .byte 0x39
    .org 0x3ab7f-ORIGIN
P_0003ab7f:
    .byte 0x68
    .org 0x3ab80-ORIGIN
P_0003ab80:
    .byte 0x00
    .org 0x3ab81-ORIGIN
P_0003ab81:
    .byte 0x00
    .org 0x3ab82-ORIGIN
P_0003ab82:
    .byte 0x82
    .org 0x3ab83-ORIGIN
P_0003ab83:
    .byte 0x9e
    .org 0x3ab84-ORIGIN
P_0003ab84:
    .byte 0xff
    .org 0x3ab85-ORIGIN
P_0003ab85:
    .byte 0xff
    .org 0x3ab86-ORIGIN
P_0003ab86:
    .byte 0x42
    .org 0x3ab87-ORIGIN
P_0003ab87:
    .byte 0x1a
    .org 0x3ab88-ORIGIN
P_0003ab88:
    .byte 0xff
    .org 0x3ab89-ORIGIN
P_0003ab89:
    .byte 0xff
    .org 0x3ab8a-ORIGIN
P_0003ab8a:
    .byte 0x10
    .org 0x3ab8b-ORIGIN
P_0003ab8b:
    .byte 0x72
    .org 0x3ab8c-ORIGIN
P_0003ab8c:
    .byte 0xff
    .org 0x3ab8d-ORIGIN
P_0003ab8d:
    .byte 0xff
    .org 0x3ab8e-ORIGIN
P_0003ab8e:
    .byte 0x10
    .org 0x3ab8f-ORIGIN
P_0003ab8f:
    .byte 0x18
    .org 0x3ab90-ORIGIN
P_0003ab90:
    .byte 0x00
    .org 0x3ab91-ORIGIN
P_0003ab91:
    .byte 0x00
    .org 0x3ab92-ORIGIN
P_0003ab92:
    .byte 0x8f
    .org 0x3ab93-ORIGIN
P_0003ab93:
    .byte 0x8a
    .org 0x3ab94-ORIGIN
P_0003ab94:
    .byte 0x00
    .org 0x3ab95-ORIGIN
P_0003ab95:
    .byte 0x00
    .org 0x3ab96-ORIGIN
P_0003ab96:
    .byte 0x8f
    .org 0x3ab97-ORIGIN
P_0003ab97:
    .byte 0x8c
    .org 0x3ab98-ORIGIN
P_0003ab98:
    .byte 0xff
    .org 0x3ab99-ORIGIN
P_0003ab99:
    .byte 0xff
    .org 0x3ab9a-ORIGIN
P_0003ab9a:
    .byte 0x11
    .org 0x3ab9b-ORIGIN
P_0003ab9b:
    .byte 0x14
    .org 0x3ab9c-ORIGIN
L_0003ab9c:
    stc gbr,r6
    .org 0x3ab9e-ORIGIN
L_0003ab9e:
    add #0x22,r6
    .org 0x3aba0-ORIGIN
L_0003aba0:
    mov r7,r0
    .org 0x3aba2-ORIGIN
L_0003aba2:
    mov.b @(r0,r6),r2
    .org 0x3aba4-ORIGIN
L_0003aba4:
    mov #-0x1,r4
    .org 0x3aba6-ORIGIN
L_0003aba6:
    extu.b r4,r4
    .org 0x3aba8-ORIGIN
L_0003aba8:
    extu.b r2,r6
    .org 0x3abaa-ORIGIN
L_0003abaa:
    add #0x1,r6
    .org 0x3abac-ORIGIN
L_0003abac:
    extu.w r6,r6
    .org 0x3abae-ORIGIN
L_0003abae:
    cmp/gt r4,r6
    .org 0x3abb0-ORIGIN
L_0003abb0:
    bf L_0003abb4
    .org 0x3abb2-ORIGIN
L_0003abb2:
    mov r4,r6
    .org 0x3abb4-ORIGIN
L_0003abb4:
    stc gbr,r2
    .org 0x3abb6-ORIGIN
L_0003abb6:
    add #0x22,r2
    .org 0x3abb8-ORIGIN
L_0003abb8:
    mov r7,r0
    .org 0x3abba-ORIGIN
L_0003abba:
    mov.b r6,@(r0,r2)
    .org 0x3abbc-ORIGIN
L_0003abbc:
    mov.b @(0x2f,gbr),r0
    .org 0x3abbe-ORIGIN
L_0003abbe:
    extu.b r0,r5
    .org 0x3abc0-ORIGIN
L_0003abc0:
    tst r13,r5
    .org 0x3abc2-ORIGIN
L_0003abc2:
    bf L_0003abfc
    .org 0x3abc4-ORIGIN
L_0003abc4:
    mov.l P_0003ae28,r10
    .org 0x3abc6-ORIGIN
L_0003abc6:
    mov.l P_0003ae2c,r6
    .org 0x3abc8-ORIGIN
L_0003abc8:
    mov.b @(0x2,r10),r0
    .org 0x3abca-ORIGIN
L_0003abca:
    mov.b @r6,r2
    .org 0x3abcc-ORIGIN
L_0003abcc:
    extu.b r0,r4
    .org 0x3abce-ORIGIN
L_0003abce:
    mov r12,r0
    .org 0x3abd0-ORIGIN
L_0003abd0:
    extu.b r2,r6
    .org 0x3abd2-ORIGIN
L_0003abd2:
    mov r4,r2
    .org 0x3abd4-ORIGIN
L_0003abd4:
    sub r6,r2
    .org 0x3abd6-ORIGIN
L_0003abd6:
    mov.b @r10,r6
    .org 0x3abd8-ORIGIN
L_0003abd8:
    mulu.w r2,r2
    .org 0x3abda-ORIGIN
L_0003abda:
    extu.b r6,r4
    .org 0x3abdc-ORIGIN
L_0003abdc:
    sts macl,r2
    .org 0x3abde-ORIGIN
L_0003abde:
    extu.w r2,r2
    .org 0x3abe0-ORIGIN
L_0003abe0:
    mul.l r2,r4
    .org 0x3abe2-ORIGIN
L_0003abe2:
    sts macl,r6
    .org 0x3abe4-ORIGIN
L_0003abe4:
    mov r6,r2
    .org 0x3abe6-ORIGIN
L_0003abe6:
    shll2 r2
    .org 0x3abe8-ORIGIN
L_0003abe8:
    add r6,r2
    .org 0x3abea-ORIGIN
L_0003abea:
    stc gbr,r6
    .org 0x3abec-ORIGIN
L_0003abec:
    add #0x14,r6
    .org 0x3abee-ORIGIN
L_0003abee:
    mov.l r2,@(r0,r6)
    .org 0x3abf0-ORIGIN
L_0003abf0:
    mov r7,r2
    .org 0x3abf2-ORIGIN
L_0003abf2:
    add #0x1,r2
    .org 0x3abf4-ORIGIN
L_0003abf4:
    or r2,r5
    .org 0x3abf6-ORIGIN
L_0003abf6:
    mov r5,r0
    .org 0x3abf8-ORIGIN
L_0003abf8:
    bra L_0003ac5a
    .org 0x3abfa-ORIGIN
L_0003abfa:
    mov.b r0,@(0x2f,gbr)
    .org 0x3abfc-ORIGIN
L_0003abfc:
    mov.b @r14,r2
    .org 0x3abfe-ORIGIN
L_0003abfe:
    mov r2,r0
    .org 0x3ac00-ORIGIN
L_0003ac00:
    tst #0x80,r0
    .org 0x3ac02-ORIGIN
L_0003ac02:
    bf L_0003ac0c
    .org 0x3ac04-ORIGIN
L_0003ac04:
    mov.b @(0xf,gbr),r0
    .org 0x3ac06-ORIGIN
L_0003ac06:
    extu.b r0,r5
    .org 0x3ac08-ORIGIN
L_0003ac08:
    tst r13,r5
    .org 0x3ac0a-ORIGIN
L_0003ac0a:
    bt L_0003ac5a
    .org 0x3ac0c-ORIGIN
L_0003ac0c:
    mov r2,r0
    .org 0x3ac0e-ORIGIN
L_0003ac0e:
    tst #0x40,r0
    .org 0x3ac10-ORIGIN
L_0003ac10:
    bf L_0003ac5a
    .org 0x3ac12-ORIGIN
L_0003ac12:
    mov.b @(0x10,gbr),r0
    .org 0x3ac14-ORIGIN
L_0003ac14:
    extu.b r0,r6
    .org 0x3ac16-ORIGIN
L_0003ac16:
    tst r13,r6
    .org 0x3ac18-ORIGIN
L_0003ac18:
    bf L_0003ac5a
    .org 0x3ac1a-ORIGIN
L_0003ac1a:
    mov.l P_0003ae30,r5
    .org 0x3ac1c-ORIGIN
L_0003ac1c:
    mov #0x74,r0
    .org 0x3ac1e-ORIGIN
L_0003ac1e:
    mov.l P_0003ae2c,r3
    .org 0x3ac20-ORIGIN
L_0003ac20:
    mov.b @(r0,r5),r2
    .org 0x3ac22-ORIGIN
L_0003ac22:
    mov r12,r0
    .org 0x3ac24-ORIGIN
L_0003ac24:
    mov.b @r3,r6
    .org 0x3ac26-ORIGIN
L_0003ac26:
    extu.b r2,r2
    .org 0x3ac28-ORIGIN
L_0003ac28:
    extu.b r6,r6
    .org 0x3ac2a-ORIGIN
L_0003ac2a:
    mov r2,r5
    .org 0x3ac2c-ORIGIN
L_0003ac2c:
    sub r6,r5
    .org 0x3ac2e-ORIGIN
L_0003ac2e:
    sub r6,r2
    .org 0x3ac30-ORIGIN
L_0003ac30:
    mul.l r5,r2
    .org 0x3ac32-ORIGIN
L_0003ac32:
    sts macl,r2
    .org 0x3ac34-ORIGIN
L_0003ac34:
    mov r2,r5
    .org 0x3ac36-ORIGIN
L_0003ac36:
    shll2 r5
    .org 0x3ac38-ORIGIN
L_0003ac38:
    add r2,r5
    .org 0x3ac3a-ORIGIN
L_0003ac3a:
    stc gbr,r2
    .org 0x3ac3c-ORIGIN
L_0003ac3c:
    add #0x14,r2
    .org 0x3ac3e-ORIGIN
L_0003ac3e:
    mov.l @(r0,r2),r6
    .org 0x3ac40-ORIGIN
L_0003ac40:
    mov #-0x1,r2
    .org 0x3ac42-ORIGIN
L_0003ac42:
    sub r5,r2
    .org 0x3ac44-ORIGIN
L_0003ac44:
    cmp/hs r2,r6
    .org 0x3ac46-ORIGIN
L_0003ac46:
    bt L_0003ac50
    .org 0x3ac48-ORIGIN
L_0003ac48:
    stc gbr,r2
    .org 0x3ac4a-ORIGIN
L_0003ac4a:
    add #0x14,r2
    .org 0x3ac4c-ORIGIN
L_0003ac4c:
    bra L_0003ac56
    .org 0x3ac4e-ORIGIN
L_0003ac4e:
    add r5,r6
    .org 0x3ac50-ORIGIN
L_0003ac50:
    stc gbr,r2
    .org 0x3ac52-ORIGIN
L_0003ac52:
    add #0x14,r2
    .org 0x3ac54-ORIGIN
L_0003ac54:
    mov #-0x1,r6
    .org 0x3ac56-ORIGIN
L_0003ac56:
    mov r12,r0
    .org 0x3ac58-ORIGIN
L_0003ac58:
    mov.l r6,@(r0,r2)
    .org 0x3ac5a-ORIGIN
L_0003ac5a:
    stc gbr,r6
    .org 0x3ac5c-ORIGIN
L_0003ac5c:
    mov.l P_0003ae28,r10
    .org 0x3ac5e-ORIGIN
L_0003ac5e:
    add #0x20,r6
    .org 0x3ac60-ORIGIN
L_0003ac60:
    mov r7,r0
    .org 0x3ac62-ORIGIN
L_0003ac62:
    mov.b @(r0,r6),r2
    .org 0x3ac64-ORIGIN
L_0003ac64:
    mov.b @r10,r6
    .org 0x3ac66-ORIGIN
L_0003ac66:
    extu.b r2,r2
    .org 0x3ac68-ORIGIN
L_0003ac68:
    extu.b r6,r4
    .org 0x3ac6a-ORIGIN
L_0003ac6a:
    mov r4,r5
    .org 0x3ac6c-ORIGIN
L_0003ac6c:
    add r2,r5
    .org 0x3ac6e-ORIGIN
L_0003ac6e:
    extu.w r5,r5
    .org 0x3ac70-ORIGIN
L_0003ac70:
    tst r5,r5
    .org 0x3ac72-ORIGIN
L_0003ac72:
    bf L_0003ac7c
    .org 0x3ac74-ORIGIN
L_0003ac74:
    stc gbr,r2
    .org 0x3ac76-ORIGIN
L_0003ac76:
    add #0x11,r2
    .org 0x3ac78-ORIGIN
L_0003ac78:
    bra L_0003acae
    .org 0x3ac7a-ORIGIN
L_0003ac7a:
    mov #-0x1,r6
    .org 0x3ac7c-ORIGIN
L_0003ac7c:
    stc gbr,r6
    .org 0x3ac7e-ORIGIN
L_0003ac7e:
    add #0x14,r6
    .org 0x3ac80-ORIGIN
L_0003ac80:
    mov r12,r0
    .org 0x3ac82-ORIGIN
L_0003ac82:
    mov.l @(r0,r6),r1
    .org 0x3ac84-ORIGIN
L_0003ac84:
    mov.l P_0003ae34,r6
    .org 0x3ac86-ORIGIN
L_0003ac86:
    jsr @r6
    .org 0x3ac88-ORIGIN
L_0003ac88:
    mov r5,r0
    .org 0x3ac8a-ORIGIN
L_0003ac8a:
    mov.l P_0003ae34,r6
    .org 0x3ac8c-ORIGIN
L_0003ac8c:
    mov r0,r1
    .org 0x3ac8e-ORIGIN
L_0003ac8e:
    mov.w P_0003ac98,r0
    .org 0x3ac90-ORIGIN
L_0003ac90:
    jsr @r6
    .org 0x3ac92-ORIGIN
L_0003ac92:
    nop
    .org 0x3ac94-ORIGIN
L_0003ac94:
    bra L_0003ac9a
    .org 0x3ac96-ORIGIN
L_0003ac96:
    nop
    .org 0x3ac98-ORIGIN
P_0003ac98:
    .byte 0x03
    .org 0x3ac99-ORIGIN
P_0003ac99:
    .byte 0xe8
    .org 0x3ac9a-ORIGIN
L_0003ac9a:
    mov #-0x1,r2
    .org 0x3ac9c-ORIGIN
L_0003ac9c:
    extu.b r2,r2
    .org 0x3ac9e-ORIGIN
L_0003ac9e:
    cmp/hi r2,r0
    .org 0x3aca0-ORIGIN
L_0003aca0:
    bf/s L_0003aca6
    .org 0x3aca2-ORIGIN
L_0003aca2:
    mov r0,r6
    .org 0x3aca4-ORIGIN
L_0003aca4:
    mov r2,r6
    .org 0x3aca6-ORIGIN
L_0003aca6:
    stc gbr,r2
    .org 0x3aca8-ORIGIN
L_0003aca8:
    mov.b @(0x3,r15),r0
    .org 0x3acaa-ORIGIN
L_0003acaa:
    add #0x11,r2
    .org 0x3acac-ORIGIN
L_0003acac:
    extu.b r0,r7
    .org 0x3acae-ORIGIN
L_0003acae:
    mov r7,r0
    .org 0x3acb0-ORIGIN
L_0003acb0:
    mov.b r6,@(r0,r2)
    .org 0x3acb2-ORIGIN
L_0003acb2:
    stc gbr,r2
    .org 0x3acb4-ORIGIN
L_0003acb4:
    add #0x11,r2
    .org 0x3acb6-ORIGIN
L_0003acb6:
    mov r7,r0
    .org 0x3acb8-ORIGIN
L_0003acb8:
    mov.b @(r0,r2),r6
    .org 0x3acba-ORIGIN
L_0003acba:
    mov.l P_0003ae38,r4
    .org 0x3acbc-ORIGIN
L_0003acbc:
    mov.l P_0003ae3c,r5
    .org 0x3acbe-ORIGIN
L_0003acbe:
    mov.l P_0003ae40,r14
    .org 0x3acc0-ORIGIN
L_0003acc0:
    jsr @r14
    .org 0x3acc2-ORIGIN
L_0003acc2:
    extu.b r6,r6
    .org 0x3acc4-ORIGIN
L_0003acc4:
    mov r0,r2
    .org 0x3acc6-ORIGIN
L_0003acc6:
    mov.b @(0x3,r15),r0
    .org 0x3acc8-ORIGIN
L_0003acc8:
    stc gbr,r6
    .org 0x3acca-ORIGIN
L_0003acca:
    add #0x2d,r6
    .org 0x3accc-ORIGIN
L_0003accc:
    extu.b r0,r7
    .org 0x3acce-ORIGIN
L_0003acce:
    mov r7,r0
    .org 0x3acd0-ORIGIN
L_0003acd0:
    mov.b r2,@(r0,r6)
    .org 0x3acd2-ORIGIN
L_0003acd2:
    mov.b @(0x2a,gbr),r0
    .org 0x3acd4-ORIGIN
L_0003acd4:
    extu.b r0,r5
    .org 0x3acd6-ORIGIN
L_0003acd6:
    tst r13,r5
    .org 0x3acd8-ORIGIN
L_0003acd8:
    bf L_0003ad44
    .org 0x3acda-ORIGIN
L_0003acda:
    mov.b @(0x10,gbr),r0
    .org 0x3acdc-ORIGIN
L_0003acdc:
    extu.b r0,r6
    .org 0x3acde-ORIGIN
L_0003acde:
    tst r13,r6
    .org 0x3ace0-ORIGIN
L_0003ace0:
    bt L_0003ad16
    .org 0x3ace2-ORIGIN
L_0003ace2:
    stc gbr,r5
    .org 0x3ace4-ORIGIN
L_0003ace4:
    add #0x20,r5
    .org 0x3ace6-ORIGIN
L_0003ace6:
    mov r7,r0
    .org 0x3ace8-ORIGIN
L_0003ace8:
    mov.b @(r0,r5),r6
    .org 0x3acea-ORIGIN
L_0003acea:
    extu.b r2,r2
    .org 0x3acec-ORIGIN
L_0003acec:
    mov.b @r10,r5
    .org 0x3acee-ORIGIN
L_0003acee:
    extu.b r6,r6
    .org 0x3acf0-ORIGIN
L_0003acf0:
    extu.b r5,r4
    .org 0x3acf2-ORIGIN
L_0003acf2:
    mov r7,r5
    .org 0x3acf4-ORIGIN
L_0003acf4:
    add r4,r6
    .org 0x3acf6-ORIGIN
L_0003acf6:
    mul.l r6,r2
    .org 0x3acf8-ORIGIN
L_0003acf8:
    mov #-0x1,r4
    .org 0x3acfa-ORIGIN
L_0003acfa:
    extu.w r4,r4
    .org 0x3acfc-ORIGIN
L_0003acfc:
    sts macl,r2
    .org 0x3acfe-ORIGIN
L_0003acfe:
    cmp/hi r4,r2
    .org 0x3ad00-ORIGIN
L_0003ad00:
    bt/s L_0003ad06
    .org 0x3ad02-ORIGIN
L_0003ad02:
    add #0x1,r5
    .org 0x3ad04-ORIGIN
L_0003ad04:
    mov r2,r4
    .org 0x3ad06-ORIGIN
L_0003ad06:
    stc gbr,r6
    .org 0x3ad08-ORIGIN
L_0003ad08:
    add #0x26,r6
    .org 0x3ad0a-ORIGIN
L_0003ad0a:
    mov r7,r0
    .org 0x3ad0c-ORIGIN
L_0003ad0c:
    shll r0
    .org 0x3ad0e-ORIGIN
L_0003ad0e:
    mov.w r4,@(r0,r6)
    .org 0x3ad10-ORIGIN
L_0003ad10:
    mov.b @(0x2a,gbr),r0
    .org 0x3ad12-ORIGIN
L_0003ad12:
    bra L_0003ad42
    .org 0x3ad14-ORIGIN
L_0003ad14:
    or r5,r0
    .org 0x3ad16-ORIGIN
L_0003ad16:
    stc gbr,r6
    .org 0x3ad18-ORIGIN
L_0003ad18:
    add #0x22,r6
    .org 0x3ad1a-ORIGIN
L_0003ad1a:
    mov r7,r0
    .org 0x3ad1c-ORIGIN
L_0003ad1c:
    mov.b @(r0,r6),r0
    .org 0x3ad1e-ORIGIN
L_0003ad1e:
    cmp/eq #0x7d,r0
    .org 0x3ad20-ORIGIN
L_0003ad20:
    bf L_0003ad44
    .org 0x3ad22-ORIGIN
L_0003ad22:
    mov.b @(0xf,gbr),r0
    .org 0x3ad24-ORIGIN
L_0003ad24:
    extu.b r0,r6
    .org 0x3ad26-ORIGIN
L_0003ad26:
    tst r13,r6
    .org 0x3ad28-ORIGIN
L_0003ad28:
    bt L_0003ad44
    .org 0x3ad2a-ORIGIN
L_0003ad2a:
    stc gbr,r6
    .org 0x3ad2c-ORIGIN
L_0003ad2c:
    mov #0x64,r5
    .org 0x3ad2e-ORIGIN
L_0003ad2e:
    mov r7,r0
    .org 0x3ad30-ORIGIN
L_0003ad30:
    add #0x26,r6
    .org 0x3ad32-ORIGIN
L_0003ad32:
    mov r7,r2
    .org 0x3ad34-ORIGIN
L_0003ad34:
    shll r0
    .org 0x3ad36-ORIGIN
L_0003ad36:
    shll8 r5
    .org 0x3ad38-ORIGIN
L_0003ad38:
    mov.w r5,@(r0,r6)
    .org 0x3ad3a-ORIGIN
L_0003ad3a:
    add #0x1,r2
    .org 0x3ad3c-ORIGIN
L_0003ad3c:
    mov.b @(0x2a,gbr),r0
    .org 0x3ad3e-ORIGIN
L_0003ad3e:
    mov.l r0,@(0x10,r15)
    .org 0x3ad40-ORIGIN
L_0003ad40:
    or r2,r0
    .org 0x3ad42-ORIGIN
L_0003ad42:
    mov.b r0,@(0x2a,gbr)
    .org 0x3ad44-ORIGIN
L_0003ad44:
    mov.b @(0xf,gbr),r0
    .org 0x3ad46-ORIGIN
L_0003ad46:
    extu.b r0,r2
    .org 0x3ad48-ORIGIN
L_0003ad48:
    tst r13,r2
    .org 0x3ad4a-ORIGIN
L_0003ad4a:
    bt L_0003ad70
    .org 0x3ad4c-ORIGIN
L_0003ad4c:
    stc gbr,r5
    .org 0x3ad4e-ORIGIN
L_0003ad4e:
    add #0x26,r5
    .org 0x3ad50-ORIGIN
L_0003ad50:
    mov r7,r0
    .org 0x3ad52-ORIGIN
L_0003ad52:
    shll r0
    .org 0x3ad54-ORIGIN
L_0003ad54:
    mov.l P_0003ae44,r4
    .org 0x3ad56-ORIGIN
L_0003ad56:
    mov.w @(r0,r5),r6
    .org 0x3ad58-ORIGIN
L_0003ad58:
    mov.l P_0003ae48,r5
    .org 0x3ad5a-ORIGIN
L_0003ad5a:
    extu.w r6,r6
    .org 0x3ad5c-ORIGIN
L_0003ad5c:
    shlr8 r6
    .org 0x3ad5e-ORIGIN
L_0003ad5e:
    jsr @r14
    .org 0x3ad60-ORIGIN
L_0003ad60:
    extu.b r6,r6
    .org 0x3ad62-ORIGIN
L_0003ad62:
    mov r0,r2
    .org 0x3ad64-ORIGIN
L_0003ad64:
    mov.b @(0x3,r15),r0
    .org 0x3ad66-ORIGIN
L_0003ad66:
    stc gbr,r6
    .org 0x3ad68-ORIGIN
L_0003ad68:
    add #0x2b,r6
    .org 0x3ad6a-ORIGIN
L_0003ad6a:
    extu.b r0,r7
    .org 0x3ad6c-ORIGIN
L_0003ad6c:
    mov r7,r0
    .org 0x3ad6e-ORIGIN
L_0003ad6e:
    mov.b r2,@(r0,r6)
    .org 0x3ad70-ORIGIN
L_0003ad70:
    mov.b @(0x38,gbr),r0
    .org 0x3ad72-ORIGIN
L_0003ad72:
    extu.b r0,r5
    .org 0x3ad74-ORIGIN
L_0003ad74:
    tst r13,r5
    .org 0x3ad76-ORIGIN
L_0003ad76:
    bf L_0003ad92
    .org 0x3ad78-ORIGIN
L_0003ad78:
    mov.l P_0003ae4c,r6
    .org 0x3ad7a-ORIGIN
L_0003ad7a:
    add #0x1,r7
    .org 0x3ad7c-ORIGIN
L_0003ad7c:
    or r7,r5
    .org 0x3ad7e-ORIGIN
L_0003ad7e:
    mov r12,r0
    .org 0x3ad80-ORIGIN
L_0003ad80:
    mov.w @r6,r2
    .org 0x3ad82-ORIGIN
L_0003ad82:
    extu.w r2,r6
    .org 0x3ad84-ORIGIN
L_0003ad84:
    stc gbr,r2
    .org 0x3ad86-ORIGIN
L_0003ad86:
    shll16 r6
    .org 0x3ad88-ORIGIN
L_0003ad88:
    add #0x30,r2
    .org 0x3ad8a-ORIGIN
L_0003ad8a:
    mov.l r6,@(r0,r2)
    .org 0x3ad8c-ORIGIN
L_0003ad8c:
    mov r5,r0
    .org 0x3ad8e-ORIGIN
L_0003ad8e:
    bra L_0003ae76
    .org 0x3ad90-ORIGIN
L_0003ad90:
    mov.b r0,@(0x38,gbr)
    .org 0x3ad92-ORIGIN
L_0003ad92:
    mov.b @(0xf,gbr),r0
    .org 0x3ad94-ORIGIN
L_0003ad94:
    extu.b r0,r6
    .org 0x3ad96-ORIGIN
L_0003ad96:
    tst r13,r6
    .org 0x3ad98-ORIGIN
L_0003ad98:
    bf L_0003adac
    .org 0x3ad9a-ORIGIN
L_0003ad9a:
    mov #-0x4a,r6
    .org 0x3ad9c-ORIGIN
L_0003ad9c:
    mov r7,r0
    .org 0x3ad9e-ORIGIN
L_0003ad9e:
    stc gbr,r2
    .org 0x3ada0-ORIGIN
L_0003ada0:
    extu.b r6,r6
    .org 0x3ada2-ORIGIN
L_0003ada2:
    add r6,r2
    .org 0x3ada4-ORIGIN
L_0003ada4:
    mov.b @(r0,r2),r6
    .org 0x3ada6-ORIGIN
L_0003ada6:
    mov.b @(0x1,r9),r0
    .org 0x3ada8-ORIGIN
L_0003ada8:
    cmp/hs r0,r6
    .org 0x3adaa-ORIGIN
L_0003adaa:
    bt L_0003adbc
    .org 0x3adac-ORIGIN
L_0003adac:
    mov.l P_0003ae50,r2
    .org 0x3adae-ORIGIN
L_0003adae:
    mov #-0x39,r6
    .org 0x3adb0-ORIGIN
L_0003adb0:
    extu.b r6,r6
    .org 0x3adb2-ORIGIN
L_0003adb2:
    mov r7,r0
    .org 0x3adb4-ORIGIN
L_0003adb4:
    add r6,r2
    .org 0x3adb6-ORIGIN
L_0003adb6:
    mov.b @(r0,r2),r6
    .org 0x3adb8-ORIGIN
L_0003adb8:
    tst r6,r6
    .org 0x3adba-ORIGIN
L_0003adba:
    bf L_0003adc4
    .org 0x3adbc-ORIGIN
L_0003adbc:
    stc gbr,r2
    .org 0x3adbe-ORIGIN
L_0003adbe:
    add #0x30,r2
    .org 0x3adc0-ORIGIN
L_0003adc0:
    bra L_0003ae72
    .org 0x3adc2-ORIGIN
L_0003adc2:
    mov #0x0,r6
    .org 0x3adc4-ORIGIN
L_0003adc4:
    stc gbr,r2
    .org 0x3adc6-ORIGIN
L_0003adc6:
    mov.b @(0x2a,gbr),r0
    .org 0x3adc8-ORIGIN
L_0003adc8:
    add #0x30,r2
    .org 0x3adca-ORIGIN
L_0003adca:
    extu.b r0,r6
    .org 0x3adcc-ORIGIN
L_0003adcc:
    mov r12,r0
    .org 0x3adce-ORIGIN
L_0003adce:
    mov.l @(r0,r2),r4
    .org 0x3add0-ORIGIN
L_0003add0:
    tst r13,r6
    .org 0x3add2-ORIGIN
L_0003add2:
    mov.l r4,@(0x4,r15)
    .org 0x3add4-ORIGIN
L_0003add4:
    shlr16 r4
    .org 0x3add6-ORIGIN
L_0003add6:
    bt L_0003ae58
    .org 0x3add8-ORIGIN
L_0003add8:
    mov.b @(0x39,gbr),r0
    .org 0x3adda-ORIGIN
L_0003adda:
    extu.b r0,r6
    .org 0x3addc-ORIGIN
L_0003addc:
    tst r13,r6
    .org 0x3adde-ORIGIN
L_0003adde:
    bf L_0003ae58
    .org 0x3ade0-ORIGIN
L_0003ade0:
    mov.l P_0003ae54,r2
    .org 0x3ade2-ORIGIN
L_0003ade2:
    mov r7,r0
    .org 0x3ade4-ORIGIN
L_0003ade4:
    add #0x1,r7
    .org 0x3ade6-ORIGIN
L_0003ade6:
    mov.w @r2,r6
    .org 0x3ade8-ORIGIN
L_0003ade8:
    extu.w r6,r6
    .org 0x3adea-ORIGIN
L_0003adea:
    mul.l r4,r6
    .org 0x3adec-ORIGIN
L_0003adec:
    mov.l @(0x4,r15),r4
    .org 0x3adee-ORIGIN
L_0003adee:
    extu.w r4,r2
    .org 0x3adf0-ORIGIN
L_0003adf0:
    sts macl,r5
    .org 0x3adf2-ORIGIN
L_0003adf2:
    mul.l r2,r6
    .org 0x3adf4-ORIGIN
L_0003adf4:
    sts macl,r2
    .org 0x3adf6-ORIGIN
L_0003adf6:
    shlr16 r2
    .org 0x3adf8-ORIGIN
L_0003adf8:
    add r2,r5
    .org 0x3adfa-ORIGIN
L_0003adfa:
    stc gbr,r2
    .org 0x3adfc-ORIGIN
L_0003adfc:
    add #0x2b,r2
    .org 0x3adfe-ORIGIN
L_0003adfe:
    mov.b @(r0,r2),r6
    .org 0x3ae00-ORIGIN
L_0003ae00:
    mov r5,r2
    .org 0x3ae02-ORIGIN
L_0003ae02:
    shlr8 r2
    .org 0x3ae04-ORIGIN
L_0003ae04:
    mov r12,r0
    .org 0x3ae06-ORIGIN
L_0003ae06:
    extu.b r6,r6
    .org 0x3ae08-ORIGIN
L_0003ae08:
    mul.l r2,r6
    .org 0x3ae0a-ORIGIN
L_0003ae0a:
    extu.b r5,r5
    .org 0x3ae0c-ORIGIN
L_0003ae0c:
    sts macl,r4
    .org 0x3ae0e-ORIGIN
L_0003ae0e:
    mul.l r5,r6
    .org 0x3ae10-ORIGIN
L_0003ae10:
    sts macl,r2
    .org 0x3ae12-ORIGIN
L_0003ae12:
    shlr8 r2
    .org 0x3ae14-ORIGIN
L_0003ae14:
    add r2,r4
    .org 0x3ae16-ORIGIN
L_0003ae16:
    stc gbr,r2
    .org 0x3ae18-ORIGIN
L_0003ae18:
    add #0x30,r2
    .org 0x3ae1a-ORIGIN
L_0003ae1a:
    mov.l r4,@(r0,r2)
    .org 0x3ae1c-ORIGIN
L_0003ae1c:
    mov.b @(0x39,gbr),r0
    .org 0x3ae1e-ORIGIN
L_0003ae1e:
    mov.l r0,@(0x14,r15)
    .org 0x3ae20-ORIGIN
L_0003ae20:
    or r7,r0
    .org 0x3ae22-ORIGIN
L_0003ae22:
    bra L_0003ae76
    .org 0x3ae24-ORIGIN
L_0003ae24:
    mov.b r0,@(0x39,gbr)
    .org 0x3ae28-ORIGIN
P_0003ae28:
    .byte 0x00
    .org 0x3ae29-ORIGIN
P_0003ae29:
    .byte 0x00
    .org 0x3ae2a-ORIGIN
P_0003ae2a:
    .byte 0x8a
    .org 0x3ae2b-ORIGIN
P_0003ae2b:
    .byte 0x4c
    .org 0x3ae2c-ORIGIN
P_0003ae2c:
    .byte 0x00
    .org 0x3ae2d-ORIGIN
P_0003ae2d:
    .byte 0x00
    .org 0x3ae2e-ORIGIN
P_0003ae2e:
    .byte 0x8d
    .org 0x3ae2f-ORIGIN
P_0003ae2f:
    .byte 0x75
    .org 0x3ae30-ORIGIN
P_0003ae30:
    .byte 0xff
    .org 0x3ae31-ORIGIN
P_0003ae31:
    .byte 0xff
    .org 0x3ae32-ORIGIN
P_0003ae32:
    .byte 0x11
    .org 0x3ae33-ORIGIN
P_0003ae33:
    .byte 0x14
    .org 0x3ae34-ORIGIN
P_0003ae34:
    .byte 0x00
    .org 0x3ae35-ORIGIN
P_0003ae35:
    .byte 0x02
    .org 0x3ae36-ORIGIN
P_0003ae36:
    .byte 0x1c
    .org 0x3ae37-ORIGIN
P_0003ae37:
    .byte 0xe0
    .org 0x3ae38-ORIGIN
P_0003ae38:
    .byte 0x00
    .org 0x3ae39-ORIGIN
P_0003ae39:
    .byte 0x01
    .org 0x3ae3a-ORIGIN
P_0003ae3a:
    .byte 0x2d
    .org 0x3ae3b-ORIGIN
P_0003ae3b:
    .byte 0x82
    .org 0x3ae3c-ORIGIN
P_0003ae3c:
    .byte 0x00
    .org 0x3ae3d-ORIGIN
P_0003ae3d:
    .byte 0x01
    .org 0x3ae3e-ORIGIN
P_0003ae3e:
    .byte 0x1b
    .org 0x3ae3f-ORIGIN
P_0003ae3f:
    .byte 0xc3
    .org 0x3ae40-ORIGIN
P_0003ae40:
    .byte 0x00
    .org 0x3ae41-ORIGIN
P_0003ae41:
    .byte 0x02
    .org 0x3ae42-ORIGIN
P_0003ae42:
    .byte 0x64
    .org 0x3ae43-ORIGIN
P_0003ae43:
    .byte 0x74
    .org 0x3ae44-ORIGIN
P_0003ae44:
    .byte 0x00
    .org 0x3ae45-ORIGIN
P_0003ae45:
    .byte 0x01
    .org 0x3ae46-ORIGIN
P_0003ae46:
    .byte 0x2c
    .org 0x3ae47-ORIGIN
P_0003ae47:
    .byte 0x4a
    .org 0x3ae48-ORIGIN
P_0003ae48:
    .byte 0x00
    .org 0x3ae49-ORIGIN
P_0003ae49:
    .byte 0x01
    .org 0x3ae4a-ORIGIN
P_0003ae4a:
    .byte 0x1b
    .org 0x3ae4b-ORIGIN
P_0003ae4b:
    .byte 0xbb
    .org 0x3ae4c-ORIGIN
P_0003ae4c:
    .byte 0x00
    .org 0x3ae4d-ORIGIN
P_0003ae4d:
    .byte 0x00
    .org 0x3ae4e-ORIGIN
P_0003ae4e:
    .byte 0x95
    .org 0x3ae4f-ORIGIN
P_0003ae4f:
    .byte 0xb6
    .org 0x3ae50-ORIGIN
P_0003ae50:
    .byte 0xff
    .org 0x3ae51-ORIGIN
P_0003ae51:
    .byte 0xff
    .org 0x3ae52-ORIGIN
P_0003ae52:
    .byte 0x42
    .org 0x3ae53-ORIGIN
P_0003ae53:
    .byte 0xd3
    .org 0x3ae54-ORIGIN
P_0003ae54:
    .byte 0x00
    .org 0x3ae55-ORIGIN
P_0003ae55:
    .byte 0x00
    .org 0x3ae56-ORIGIN
P_0003ae56:
    .byte 0x94
    .org 0x3ae57-ORIGIN
P_0003ae57:
    .byte 0x10
    .org 0x3ae58-ORIGIN
L_0003ae58:
    mov.l P_0003b0f4,r2
    .org 0x3ae5a-ORIGIN
L_0003ae5a:
    mov.w @r2,r5
    .org 0x3ae5c-ORIGIN
L_0003ae5c:
    extu.w r5,r5
    .org 0x3ae5e-ORIGIN
L_0003ae5e:
    mul.l r4,r5
    .org 0x3ae60-ORIGIN
L_0003ae60:
    mov.l @(0x4,r15),r4
    .org 0x3ae62-ORIGIN
L_0003ae62:
    extu.w r4,r2
    .org 0x3ae64-ORIGIN
L_0003ae64:
    sts macl,r6
    .org 0x3ae66-ORIGIN
L_0003ae66:
    mul.l r2,r5
    .org 0x3ae68-ORIGIN
L_0003ae68:
    sts macl,r2
    .org 0x3ae6a-ORIGIN
L_0003ae6a:
    shlr16 r2
    .org 0x3ae6c-ORIGIN
L_0003ae6c:
    add r2,r6
    .org 0x3ae6e-ORIGIN
L_0003ae6e:
    stc gbr,r2
    .org 0x3ae70-ORIGIN
L_0003ae70:
    add #0x30,r2
    .org 0x3ae72-ORIGIN
L_0003ae72:
    mov r12,r0
    .org 0x3ae74-ORIGIN
L_0003ae74:
    mov.l r6,@(r0,r2)
    .org 0x3ae76-ORIGIN
L_0003ae76:
    add #0x18,r15
    .org 0x3ae78-ORIGIN
L_0003ae78:
    ldc.l @r15+,gbr
    .org 0x3ae7a-ORIGIN
L_0003ae7a:
    lds.l @r15+,macl
    .org 0x3ae7c-ORIGIN
L_0003ae7c:
    lds.l @r15+,pr
    .org 0x3ae7e-ORIGIN
L_0003ae7e:
    mov.l @r15+,r14
    .org 0x3ae80-ORIGIN
L_0003ae80:
    mov.l @r15+,r13
    .org 0x3ae82-ORIGIN
L_0003ae82:
    mov.l @r15+,r12
    .org 0x3ae84-ORIGIN
L_0003ae84:
    mov.l @r15+,r10
    .org 0x3ae86-ORIGIN
L_0003ae86:
    rts
    .org 0x3ae88-ORIGIN
L_0003ae88:
    mov.l @r15+,r9
    .org 0x3b0f4-ORIGIN
P_0003b0f4:
    .byte 0x00
    .org 0x3b0f5-ORIGIN
P_0003b0f5:
    .byte 0x00
    .org 0x3b0f6-ORIGIN
P_0003b0f6:
    .byte 0x94
    .org 0x3b0f7-ORIGIN
P_0003b0f7:
    .byte 0x10
