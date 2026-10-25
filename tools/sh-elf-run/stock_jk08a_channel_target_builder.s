! Complete stock code-channel1 target builder, inverse curves and real fixed-record predicates.
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
    .org 0x26524-ORIGIN
L_00026524:
    sts.l pr,@-r15
    .org 0x26526-ORIGIN
L_00026526:
    mov.l r4,@-r15
    .org 0x26528-ORIGIN
L_00026528:
    mov r5,r0
    .org 0x2652a-ORIGIN
L_0002652a:
    extu.w r6,r5
    .org 0x2652c-ORIGIN
L_0002652c:
    mov.l P_0002654c,r7
    .org 0x2652e-ORIGIN
L_0002652e:
    jsr @r7
    .org 0x26530-ORIGIN
L_00026530:
    mov #0x3e,r4
    .org 0x26532-ORIGIN
L_00026532:
    mov.l @r15+,r6
    .org 0x26534-ORIGIN
L_00026534:
    add r4,r6
    .org 0x26536-ORIGIN
L_00026536:
    mov.w @(0x2,r6),r0
    .org 0x26538-ORIGIN
L_00026538:
    extu.w r0,r2
    .org 0x2653a-ORIGIN
L_0002653a:
    mov r5,r3
    .org 0x2653c-ORIGIN
L_0002653c:
    mov.w @r6,r1
    .org 0x2653e-ORIGIN
L_0002653e:
    lds.l @r15+,pr
    .org 0x26540-ORIGIN
L_00026540:
    mov.l P_00026548,r6
    .org 0x26542-ORIGIN
L_00026542:
    jmp @r6
    .org 0x26544-ORIGIN
L_00026544:
    extu.w r1,r0
    .org 0x26548-ORIGIN
P_00026548:
    .byte 0x00
    .org 0x26549-ORIGIN
P_00026549:
    .byte 0x02
    .org 0x2654a-ORIGIN
P_0002654a:
    .byte 0x67
    .org 0x2654b-ORIGIN
P_0002654b:
    .byte 0x40
    .org 0x2654c-ORIGIN
P_0002654c:
    .byte 0x00
    .org 0x2654d-ORIGIN
P_0002654d:
    .byte 0x02
    .org 0x2654e-ORIGIN
P_0002654e:
    .byte 0x69
    .org 0x2654f-ORIGIN
P_0002654f:
    .byte 0x84
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
    .org 0x6f48c-ORIGIN
L_0006f48c:
    mov.l r10,@-r15
    .org 0x6f48e-ORIGIN
L_0006f48e:
    mov.l r11,@-r15
    .org 0x6f490-ORIGIN
L_0006f490:
    mov.l r12,@-r15
    .org 0x6f492-ORIGIN
L_0006f492:
    mov.l r13,@-r15
    .org 0x6f494-ORIGIN
L_0006f494:
    mov.l r14,@-r15
    .org 0x6f496-ORIGIN
L_0006f496:
    sts.l pr,@-r15
    .org 0x6f498-ORIGIN
L_0006f498:
    sts.l macl,@-r15
    .org 0x6f49a-ORIGIN
L_0006f49a:
    stc.l gbr,@-r15
    .org 0x6f49c-ORIGIN
L_0006f49c:
    mov.l P_0006f698,r0
    .org 0x6f49e-ORIGIN
L_0006f49e:
    ldc r0,gbr
    .org 0x6f4a0-ORIGIN
L_0006f4a0:
    add #-0x8,r15
    .org 0x6f4a2-ORIGIN
L_0006f4a2:
    mov r4,r0
    .org 0x6f4a4-ORIGIN
L_0006f4a4:
    mov.b r0,@(0x3,r15)
    .org 0x6f4a6-ORIGIN
L_0006f4a6:
    mov.l P_0006f684,r14
    .org 0x6f4a8-ORIGIN
L_0006f4a8:
    mov #-0x4c,r0
    .org 0x6f4aa-ORIGIN
L_0006f4aa:
    extu.b r0,r0
    .org 0x6f4ac-ORIGIN
L_0006f4ac:
    mov.l P_0006f688,r11
    .org 0x6f4ae-ORIGIN
L_0006f4ae:
    mov.w @(r0,r14),r6
    .org 0x6f4b0-ORIGIN
L_0006f4b0:
    mov #0x0,r5
    .org 0x6f4b2-ORIGIN
L_0006f4b2:
    mov.l P_0006f68c,r13
    .org 0x6f4b4-ORIGIN
L_0006f4b4:
    mov r11,r4
    .org 0x6f4b6-ORIGIN
L_0006f4b6:
    extu.w r6,r6
    .org 0x6f4b8-ORIGIN
L_0006f4b8:
    mov.l P_0006f690,r7
    .org 0x6f4ba-ORIGIN
L_0006f4ba:
    cmp/gt r6,r5
    .org 0x6f4bc-ORIGIN
L_0006f4bc:
    mov.l P_0006f694,r10
    .org 0x6f4be-ORIGIN
L_0006f4be:
    addc r5,r6
    .org 0x6f4c0-ORIGIN
L_0006f4c0:
    mov r13,r5
    .org 0x6f4c2-ORIGIN
L_0006f4c2:
    shar r6
    .org 0x6f4c4-ORIGIN
L_0006f4c4:
    jsr @r7
    .org 0x6f4c6-ORIGIN
L_0006f4c6:
    extu.w r6,r6
    .org 0x6f4c8-ORIGIN
L_0006f4c8:
    extu.w r0,r5
    .org 0x6f4ca-ORIGIN
L_0006f4ca:
    mov.b @(0x3,r15),r0
    .org 0x6f4cc-ORIGIN
L_0006f4cc:
    mov.l P_0006f69c,r6
    .org 0x6f4ce-ORIGIN
L_0006f4ce:
    shlr2 r5
    .org 0x6f4d0-ORIGIN
L_0006f4d0:
    extu.b r0,r12
    .org 0x6f4d2-ORIGIN
L_0006f4d2:
    mov.w r5,@r10
    .org 0x6f4d4-ORIGIN
L_0006f4d4:
    mov.b @r6,r0
    .org 0x6f4d6-ORIGIN
L_0006f4d6:
    shll r12
    .org 0x6f4d8-ORIGIN
L_0006f4d8:
    tst #0x4,r0
    .org 0x6f4da-ORIGIN
L_0006f4da:
    bf L_0006f578
    .org 0x6f4dc-ORIGIN
L_0006f4dc:
    mov.b @(0x4,r6),r0
    .org 0x6f4de-ORIGIN
L_0006f4de:
    tst #0x1,r0
    .org 0x6f4e0-ORIGIN
L_0006f4e0:
    bf L_0006f578
    .org 0x6f4e2-ORIGIN
L_0006f4e2:
    mov.l P_0006f6a0,r6
    .org 0x6f4e4-ORIGIN
L_0006f4e4:
    mov.b @r6,r0
    .org 0x6f4e6-ORIGIN
L_0006f4e6:
    tst #0x4,r0
    .org 0x6f4e8-ORIGIN
L_0006f4e8:
    bt L_0006f55e
    .org 0x6f4ea-ORIGIN
L_0006f4ea:
    mov.l P_0006f6a4,r6
    .org 0x6f4ec-ORIGIN
L_0006f4ec:
    mov.b @r6,r0
    .org 0x6f4ee-ORIGIN
L_0006f4ee:
    tst #0x20,r0
    .org 0x6f4f0-ORIGIN
L_0006f4f0:
    bt L_0006f538
    .org 0x6f4f2-ORIGIN
L_0006f4f2:
    mov.w P_0006f5a0,r0
    .org 0x6f4f4-ORIGIN
L_0006f4f4:
    mov.l P_0006f6a8,r2
    .org 0x6f4f6-ORIGIN
L_0006f4f6:
    mov.w @(r0,r14),r5
    .org 0x6f4f8-ORIGIN
L_0006f4f8:
    mov r12,r0
    .org 0x6f4fa-ORIGIN
L_0006f4fa:
    add #0x56,r2
    .org 0x6f4fc-ORIGIN
L_0006f4fc:
    extu.w r5,r5
    .org 0x6f4fe-ORIGIN
L_0006f4fe:
    mov.w @(r0,r2),r4
    .org 0x6f500-ORIGIN
L_0006f500:
    mov #0x0,r2
    .org 0x6f502-ORIGIN
L_0006f502:
    mov r5,r6
    .org 0x6f504-ORIGIN
L_0006f504:
    cmp/gt r5,r2
    .org 0x6f506-ORIGIN
L_0006f506:
    addc r2,r6
    .org 0x6f508-ORIGIN
L_0006f508:
    shar r6
    .org 0x6f50a-ORIGIN
L_0006f50a:
    add r4,r6
    .org 0x6f50c-ORIGIN
L_0006f50c:
    cmp/pz r6
    .org 0x6f50e-ORIGIN
L_0006f50e:
    bt L_0006f514
    .org 0x6f510-ORIGIN
L_0006f510:
    bra L_0006f51e
    .org 0x6f512-ORIGIN
L_0006f512:
    mov #0x0,r6
    .org 0x6f514-ORIGIN
L_0006f514:
    cmp/gt r5,r2
    .org 0x6f516-ORIGIN
L_0006f516:
    mov r5,r6
    .org 0x6f518-ORIGIN
L_0006f518:
    addc r2,r6
    .org 0x6f51a-ORIGIN
L_0006f51a:
    shar r6
    .org 0x6f51c-ORIGIN
L_0006f51c:
    add r4,r6
    .org 0x6f51e-ORIGIN
L_0006f51e:
    mov #-0x1,r14
    .org 0x6f520-ORIGIN
L_0006f520:
    extu.w r14,r14
    .org 0x6f522-ORIGIN
L_0006f522:
    cmp/gt r14,r6
    .org 0x6f524-ORIGIN
L_0006f524:
    bf L_0006f528
    .org 0x6f526-ORIGIN
L_0006f526:
    mov r14,r6
    .org 0x6f528-ORIGIN
L_0006f528:
    mov.l P_0006f690,r7
    .org 0x6f52a-ORIGIN
L_0006f52a:
    extu.w r6,r6
    .org 0x6f52c-ORIGIN
L_0006f52c:
    mov r11,r4
    .org 0x6f52e-ORIGIN
L_0006f52e:
    jsr @r7
    .org 0x6f530-ORIGIN
L_0006f530:
    mov r13,r5
    .org 0x6f532-ORIGIN
L_0006f532:
    extu.w r0,r2
    .org 0x6f534-ORIGIN
L_0006f534:
    bra L_0006f590
    .org 0x6f536-ORIGIN
L_0006f536:
    mov.l r2,@(0x4,r15)
    .org 0x6f538-ORIGIN
L_0006f538:
    mov.l P_0006f6ac,r6
    .org 0x6f53a-ORIGIN
L_0006f53a:
    mov #-0x1,r14
    .org 0x6f53c-ORIGIN
L_0006f53c:
    mov.l P_0006f6b0,r7
    .org 0x6f53e-ORIGIN
L_0006f53e:
    extu.w r14,r14
    .org 0x6f540-ORIGIN
L_0006f540:
    mov.w @(0x1c,r6),r0
    .org 0x6f542-ORIGIN
L_0006f542:
    extu.w r0,r4
    .org 0x6f544-ORIGIN
L_0006f544:
    mov.b @(0x1,r7),r0
    .org 0x6f546-ORIGIN
L_0006f546:
    mov r4,r2
    .org 0x6f548-ORIGIN
L_0006f548:
    extu.b r0,r5
    .org 0x6f54a-ORIGIN
L_0006f54a:
    add r5,r2
    .org 0x6f54c-ORIGIN
L_0006f54c:
    shll2 r2
    .org 0x6f54e-ORIGIN
L_0006f54e:
    cmp/gt r14,r2
    .org 0x6f550-ORIGIN
L_0006f550:
    bf L_0006f556
    .org 0x6f552-ORIGIN
L_0006f552:
    bra L_0006f58e
    .org 0x6f554-ORIGIN
L_0006f554:
    mov r14,r7
    .org 0x6f556-ORIGIN
L_0006f556:
    mov r4,r7
    .org 0x6f558-ORIGIN
L_0006f558:
    add r5,r7
    .org 0x6f55a-ORIGIN
L_0006f55a:
    bra L_0006f58e
    .org 0x6f55c-ORIGIN
L_0006f55c:
    shll2 r7
    .org 0x6f55e-ORIGIN
L_0006f55e:
    mov.l P_0006f6b0,r7
    .org 0x6f560-ORIGIN
L_0006f560:
    mov #-0x1,r14
    .org 0x6f562-ORIGIN
L_0006f562:
    extu.w r14,r14
    .org 0x6f564-ORIGIN
L_0006f564:
    mov.b @r7,r6
    .org 0x6f566-ORIGIN
L_0006f566:
    extu.b r6,r7
    .org 0x6f568-ORIGIN
L_0006f568:
    mov r7,r2
    .org 0x6f56a-ORIGIN
L_0006f56a:
    shll2 r2
    .org 0x6f56c-ORIGIN
L_0006f56c:
    cmp/gt r14,r2
    .org 0x6f56e-ORIGIN
L_0006f56e:
    bf L_0006f574
    .org 0x6f570-ORIGIN
L_0006f570:
    bra L_0006f58e
    .org 0x6f572-ORIGIN
L_0006f572:
    mov r14,r7
    .org 0x6f574-ORIGIN
L_0006f574:
    bra L_0006f58e
    .org 0x6f576-ORIGIN
L_0006f576:
    shll2 r7
    .org 0x6f578-ORIGIN
L_0006f578:
    mov.l P_0006f6ac,r6
    .org 0x6f57a-ORIGIN
L_0006f57a:
    extu.w r5,r5
    .org 0x6f57c-ORIGIN
L_0006f57c:
    mov #-0x1,r14
    .org 0x6f57e-ORIGIN
L_0006f57e:
    mov.w @(0x1c,r6),r0
    .org 0x6f580-ORIGIN
L_0006f580:
    extu.w r14,r14
    .org 0x6f582-ORIGIN
L_0006f582:
    extu.w r0,r7
    .org 0x6f584-ORIGIN
L_0006f584:
    add r5,r7
    .org 0x6f586-ORIGIN
L_0006f586:
    shll2 r7
    .org 0x6f588-ORIGIN
L_0006f588:
    cmp/gt r14,r7
    .org 0x6f58a-ORIGIN
L_0006f58a:
    bf L_0006f58e
    .org 0x6f58c-ORIGIN
L_0006f58c:
    mov r14,r7
    .org 0x6f58e-ORIGIN
L_0006f58e:
    mov.l r7,@(0x4,r15)
    .org 0x6f590-ORIGIN
L_0006f590:
    mov.l P_0006f6b4,r6
    .org 0x6f592-ORIGIN
L_0006f592:
    mov.b @r6,r0
    .org 0x6f594-ORIGIN
L_0006f594:
    tst #0x20,r0
    .org 0x6f596-ORIGIN
L_0006f596:
    bt L_0006f5a4
    .org 0x6f598-ORIGIN
L_0006f598:
    mov.w @(0x4,gbr),r0
    .org 0x6f59a-ORIGIN
L_0006f59a:
    extu.w r0,r6
    .org 0x6f59c-ORIGIN
L_0006f59c:
    bra L_0006f5e2
    .org 0x6f59e-ORIGIN
L_0006f59e:
    shll2 r6
    .org 0x6f5a0-ORIGIN
P_0006f5a0:
    .byte 0x07
    .org 0x6f5a1-ORIGIN
P_0006f5a1:
    .byte 0x26
    .org 0x6f5a4-ORIGIN
L_0006f5a4:
    mov.l P_0006f6b8,r6
    .org 0x6f5a6-ORIGIN
L_0006f5a6:
    mov #0x17,r0
    .org 0x6f5a8-ORIGIN
L_0006f5a8:
    mov.l P_0006f6bc,r4
    .org 0x6f5aa-ORIGIN
L_0006f5aa:
    mov.b @(r0,r6),r7
    .org 0x6f5ac-ORIGIN
L_0006f5ac:
    mov.l P_0006f6c0,r5
    .org 0x6f5ae-ORIGIN
L_0006f5ae:
    mov.l P_0006f6c4,r2
    .org 0x6f5b0-ORIGIN
L_0006f5b0:
    jsr @r2
    .org 0x6f5b2-ORIGIN
L_0006f5b2:
    extu.b r7,r6
    .org 0x6f5b4-ORIGIN
L_0006f5b4:
    extu.b r0,r2
    .org 0x6f5b6-ORIGIN
L_0006f5b6:
    mov.w @(0x4,gbr),r0
    .org 0x6f5b8-ORIGIN
L_0006f5b8:
    mov #0xd,r6
    .org 0x6f5ba-ORIGIN
L_0006f5ba:
    mulu.w r2,r6
    .org 0x6f5bc-ORIGIN
L_0006f5bc:
    extu.w r0,r4
    .org 0x6f5be-ORIGIN
L_0006f5be:
    mov r4,r2
    .org 0x6f5c0-ORIGIN
L_0006f5c0:
    shll2 r2
    .org 0x6f5c2-ORIGIN
L_0006f5c2:
    sts macl,r6
    .org 0x6f5c4-ORIGIN
L_0006f5c4:
    extu.w r6,r6
    .org 0x6f5c6-ORIGIN
L_0006f5c6:
    cmp/gt r2,r6
    .org 0x6f5c8-ORIGIN
L_0006f5c8:
    bf L_0006f5ce
    .org 0x6f5ca-ORIGIN
L_0006f5ca:
    mov r4,r6
    .org 0x6f5cc-ORIGIN
L_0006f5cc:
    shll2 r6
    .org 0x6f5ce-ORIGIN
L_0006f5ce:
    mov.w @(0x2,gbr),r0
    .org 0x6f5d0-ORIGIN
L_0006f5d0:
    extu.w r6,r5
    .org 0x6f5d2-ORIGIN
L_0006f5d2:
    extu.w r0,r6
    .org 0x6f5d4-ORIGIN
L_0006f5d4:
    mov r6,r2
    .org 0x6f5d6-ORIGIN
L_0006f5d6:
    shll2 r2
    .org 0x6f5d8-ORIGIN
L_0006f5d8:
    cmp/ge r2,r5
    .org 0x6f5da-ORIGIN
L_0006f5da:
    bt L_0006f5e0
    .org 0x6f5dc-ORIGIN
L_0006f5dc:
    bra L_0006f5e2
    .org 0x6f5de-ORIGIN
L_0006f5de:
    shll2 r6
    .org 0x6f5e0-ORIGIN
L_0006f5e0:
    mov r5,r6
    .org 0x6f5e2-ORIGIN
L_0006f5e2:
    mov.w P_0006f67e,r0
    .org 0x6f5e4-ORIGIN
L_0006f5e4:
    mov.l @(0x4,r15),r7
    .org 0x6f5e6-ORIGIN
L_0006f5e6:
    mov.w r6,@(r0,r10)
    .org 0x6f5e8-ORIGIN
L_0006f5e8:
    extu.w r6,r6
    .org 0x6f5ea-ORIGIN
L_0006f5ea:
    cmp/gt r6,r7
    .org 0x6f5ec-ORIGIN
L_0006f5ec:
    bt L_0006f5f6
    .org 0x6f5ee-ORIGIN
L_0006f5ee:
    mov.w @(0x0,gbr),r0
    .org 0x6f5f0-ORIGIN
L_0006f5f0:
    extu.w r0,r6
    .org 0x6f5f2-ORIGIN
L_0006f5f2:
    cmp/gt r7,r6
    .org 0x6f5f4-ORIGIN
L_0006f5f4:
    bf L_0006f5f8
    .org 0x6f5f6-ORIGIN
L_0006f5f6:
    mov.l r6,@(0x4,r15)
    .org 0x6f5f8-ORIGIN
L_0006f5f8:
    mov.l P_0006f6b0,r7
    .org 0x6f5fa-ORIGIN
L_0006f5fa:
    mov.b @r7,r6
    .org 0x6f5fc-ORIGIN
L_0006f5fc:
    extu.b r6,r6
    .org 0x6f5fe-ORIGIN
L_0006f5fe:
    mov r6,r2
    .org 0x6f600-ORIGIN
L_0006f600:
    shll2 r2
    .org 0x6f602-ORIGIN
L_0006f602:
    cmp/gt r14,r2
    .org 0x6f604-ORIGIN
L_0006f604:
    bf L_0006f60a
    .org 0x6f606-ORIGIN
L_0006f606:
    bra L_0006f60e
    .org 0x6f608-ORIGIN
L_0006f608:
    mov r14,r2
    .org 0x6f60a-ORIGIN
L_0006f60a:
    shll2 r6
    .org 0x6f60c-ORIGIN
L_0006f60c:
    mov r6,r2
    .org 0x6f60e-ORIGIN
L_0006f60e:
    extu.w r2,r6
    .org 0x6f610-ORIGIN
L_0006f610:
    mov r6,r2
    .org 0x6f612-ORIGIN
L_0006f612:
    add #-0x14,r2
    .org 0x6f614-ORIGIN
L_0006f614:
    cmp/pz r2
    .org 0x6f616-ORIGIN
L_0006f616:
    bt L_0006f61c
    .org 0x6f618-ORIGIN
L_0006f618:
    bra L_0006f620
    .org 0x6f61a-ORIGIN
L_0006f61a:
    mov #0x0,r2
    .org 0x6f61c-ORIGIN
L_0006f61c:
    mov r6,r2
    .org 0x6f61e-ORIGIN
L_0006f61e:
    add #-0x14,r2
    .org 0x6f620-ORIGIN
L_0006f620:
    mov.l P_0006f6c8,r13
    .org 0x6f622-ORIGIN
L_0006f622:
    mov #0x6f,r4
    .org 0x6f624-ORIGIN
L_0006f624:
    jsr @r13
    .org 0x6f626-ORIGIN
L_0006f626:
    mov r2,r14
    .org 0x6f628-ORIGIN
L_0006f628:
    tst r0,r0
    .org 0x6f62a-ORIGIN
L_0006f62a:
    bf L_0006f636
    .org 0x6f62c-ORIGIN
L_0006f62c:
    mov.w P_0006f680,r4
    .org 0x6f62e-ORIGIN
L_0006f62e:
    jsr @r13
    .org 0x6f630-ORIGIN
L_0006f630:
    nop
    .org 0x6f632-ORIGIN
L_0006f632:
    tst r0,r0
    .org 0x6f634-ORIGIN
L_0006f634:
    bt L_0006f640
    .org 0x6f636-ORIGIN
L_0006f636:
    mov.l @(0x4,r15),r7
    .org 0x6f638-ORIGIN
L_0006f638:
    extu.w r14,r14
    .org 0x6f63a-ORIGIN
L_0006f63a:
    cmp/gt r14,r7
    .org 0x6f63c-ORIGIN
L_0006f63c:
    bf L_0006f640
    .org 0x6f63e-ORIGIN
L_0006f63e:
    mov.l r14,@(0x4,r15)
    .org 0x6f640-ORIGIN
L_0006f640:
    jsr @r13
    .org 0x6f642-ORIGIN
L_0006f642:
    mov #0x70,r4
    .org 0x6f644-ORIGIN
L_0006f644:
    tst r0,r0
    .org 0x6f646-ORIGIN
L_0006f646:
    bf L_0006f652
    .org 0x6f648-ORIGIN
L_0006f648:
    mov.w P_0006f682,r4
    .org 0x6f64a-ORIGIN
L_0006f64a:
    jsr @r13
    .org 0x6f64c-ORIGIN
L_0006f64c:
    nop
    .org 0x6f64e-ORIGIN
L_0006f64e:
    tst r0,r0
    .org 0x6f650-ORIGIN
L_0006f650:
    bt L_0006f660
    .org 0x6f652-ORIGIN
L_0006f652:
    mov.l P_0006f6cc,r2
    .org 0x6f654-ORIGIN
L_0006f654:
    mov.l @(0x4,r15),r7
    .org 0x6f656-ORIGIN
L_0006f656:
    mov.w @r2,r6
    .org 0x6f658-ORIGIN
L_0006f658:
    extu.w r6,r6
    .org 0x6f65a-ORIGIN
L_0006f65a:
    cmp/gt r6,r7
    .org 0x6f65c-ORIGIN
L_0006f65c:
    bf L_0006f660
    .org 0x6f65e-ORIGIN
L_0006f65e:
    mov.l r6,@(0x4,r15)
    .org 0x6f660-ORIGIN
L_0006f660:
    mov.l P_0006f6d0,r2
    .org 0x6f662-ORIGIN
L_0006f662:
    mov r12,r0
    .org 0x6f664-ORIGIN
L_0006f664:
    mov.l @(0x4,r15),r7
    .org 0x6f666-ORIGIN
L_0006f666:
    add #0x24,r2
    .org 0x6f668-ORIGIN
L_0006f668:
    mov.w r7,@(r0,r2)
    .org 0x6f66a-ORIGIN
L_0006f66a:
    add #0x8,r15
    .org 0x6f66c-ORIGIN
L_0006f66c:
    ldc.l @r15+,gbr
    .org 0x6f66e-ORIGIN
L_0006f66e:
    lds.l @r15+,macl
    .org 0x6f670-ORIGIN
L_0006f670:
    lds.l @r15+,pr
    .org 0x6f672-ORIGIN
L_0006f672:
    mov.l @r15+,r14
    .org 0x6f674-ORIGIN
L_0006f674:
    mov.l @r15+,r13
    .org 0x6f676-ORIGIN
L_0006f676:
    mov.l @r15+,r12
    .org 0x6f678-ORIGIN
L_0006f678:
    mov.l @r15+,r11
    .org 0x6f67a-ORIGIN
L_0006f67a:
    rts
    .org 0x6f67c-ORIGIN
L_0006f67c:
    mov.l @r15+,r10
    .org 0x6f67e-ORIGIN
P_0006f67e:
    .byte 0x0c
    .org 0x6f67f-ORIGIN
P_0006f67f:
    .byte 0x10
    .org 0x6f680-ORIGIN
P_0006f680:
    .byte 0x01
    .org 0x6f681-ORIGIN
P_0006f681:
    .byte 0x21
    .org 0x6f682-ORIGIN
P_0006f682:
    .byte 0x01
    .org 0x6f683-ORIGIN
P_0006f683:
    .byte 0x22
    .org 0x6f684-ORIGIN
P_0006f684:
    .byte 0xff
    .org 0x6f685-ORIGIN
P_0006f685:
    .byte 0xff
    .org 0x6f686-ORIGIN
P_0006f686:
    .byte 0x12
    .org 0x6f687-ORIGIN
P_0006f687:
    .byte 0x8c
    .org 0x6f688-ORIGIN
P_0006f688:
    .byte 0x00
    .org 0x6f689-ORIGIN
P_0006f689:
    .byte 0x01
    .org 0x6f68a-ORIGIN
P_0006f68a:
    .byte 0x55
    .org 0x6f68b-ORIGIN
P_0006f68b:
    .byte 0xa0
    .org 0x6f68c-ORIGIN
P_0006f68c:
    .byte 0x00
    .org 0x6f68d-ORIGIN
P_0006f68d:
    .byte 0x01
    .org 0x6f68e-ORIGIN
P_0006f68e:
    .byte 0x32
    .org 0x6f68f-ORIGIN
P_0006f68f:
    .byte 0x02
    .org 0x6f690-ORIGIN
P_0006f690:
    .byte 0x00
    .org 0x6f691-ORIGIN
P_0006f691:
    .byte 0x02
    .org 0x6f692-ORIGIN
P_0006f692:
    .byte 0x65
    .org 0x6f693-ORIGIN
P_0006f693:
    .byte 0x24
    .org 0x6f694-ORIGIN
P_0006f694:
    .byte 0xff
    .org 0x6f695-ORIGIN
P_0006f695:
    .byte 0xff
    .org 0x6f696-ORIGIN
P_0006f696:
    .byte 0x28
    .org 0x6f697-ORIGIN
P_0006f697:
    .byte 0xf8
    .org 0x6f698-ORIGIN
P_0006f698:
    .byte 0x00
    .org 0x6f699-ORIGIN
P_0006f699:
    .byte 0x00
    .org 0x6f69a-ORIGIN
P_0006f69a:
    .byte 0x95
    .org 0x6f69b-ORIGIN
P_0006f69b:
    .byte 0x74
    .org 0x6f69c-ORIGIN
P_0006f69c:
    .byte 0xff
    .org 0x6f69d-ORIGIN
P_0006f69d:
    .byte 0xff
    .org 0x6f69e-ORIGIN
P_0006f69e:
    .byte 0x24
    .org 0x6f69f-ORIGIN
P_0006f69f:
    .byte 0xce
    .org 0x6f6a0-ORIGIN
P_0006f6a0:
    .byte 0xff
    .org 0x6f6a1-ORIGIN
P_0006f6a1:
    .byte 0xff
    .org 0x6f6a2-ORIGIN
P_0006f6a2:
    .byte 0x41
    .org 0x6f6a3-ORIGIN
P_0006f6a3:
    .byte 0xa5
    .org 0x6f6a4-ORIGIN
P_0006f6a4:
    .byte 0xff
    .org 0x6f6a5-ORIGIN
P_0006f6a5:
    .byte 0xff
    .org 0x6f6a6-ORIGIN
P_0006f6a6:
    .byte 0x24
    .org 0x6f6a7-ORIGIN
P_0006f6a7:
    .byte 0x4f
    .org 0x6f6a8-ORIGIN
P_0006f6a8:
    .byte 0xff
    .org 0x6f6a9-ORIGIN
P_0006f6a9:
    .byte 0xff
    .org 0x6f6aa-ORIGIN
P_0006f6aa:
    .byte 0x56
    .org 0x6f6ab-ORIGIN
P_0006f6ab:
    .byte 0xb2
    .org 0x6f6ac-ORIGIN
P_0006f6ac:
    .byte 0xff
    .org 0x6f6ad-ORIGIN
P_0006f6ad:
    .byte 0xff
    .org 0x6f6ae-ORIGIN
P_0006f6ae:
    .byte 0x26
    .org 0x6f6af-ORIGIN
P_0006f6af:
    .byte 0x7a
    .org 0x6f6b0-ORIGIN
P_0006f6b0:
    .byte 0x00
    .org 0x6f6b1-ORIGIN
P_0006f6b1:
    .byte 0x00
    .org 0x6f6b2-ORIGIN
P_0006f6b2:
    .byte 0x8c
    .org 0x6f6b3-ORIGIN
P_0006f6b3:
    .byte 0xb6
    .org 0x6f6b4-ORIGIN
P_0006f6b4:
    .byte 0xff
    .org 0x6f6b5-ORIGIN
P_0006f6b5:
    .byte 0xff
    .org 0x6f6b6-ORIGIN
P_0006f6b6:
    .byte 0x41
    .org 0x6f6b7-ORIGIN
P_0006f6b7:
    .byte 0x7e
    .org 0x6f6b8-ORIGIN
P_0006f6b8:
    .byte 0xff
    .org 0x6f6b9-ORIGIN
P_0006f6b9:
    .byte 0xff
    .org 0x6f6ba-ORIGIN
P_0006f6ba:
    .byte 0x11
    .org 0x6f6bb-ORIGIN
P_0006f6bb:
    .byte 0x9c
    .org 0x6f6bc-ORIGIN
P_0006f6bc:
    .byte 0x00
    .org 0x6f6bd-ORIGIN
P_0006f6bd:
    .byte 0x01
    .org 0x6f6be-ORIGIN
P_0006f6be:
    .byte 0x2d
    .org 0x6f6bf-ORIGIN
P_0006f6bf:
    .byte 0xaa
    .org 0x6f6c0-ORIGIN
P_0006f6c0:
    .byte 0x00
    .org 0x6f6c1-ORIGIN
P_0006f6c1:
    .byte 0x01
    .org 0x6f6c2-ORIGIN
P_0006f6c2:
    .byte 0x2d
    .org 0x6f6c3-ORIGIN
P_0006f6c3:
    .byte 0x9a
    .org 0x6f6c4-ORIGIN
P_0006f6c4:
    .byte 0x00
    .org 0x6f6c5-ORIGIN
P_0006f6c5:
    .byte 0x02
    .org 0x6f6c6-ORIGIN
P_0006f6c6:
    .byte 0x64
    .org 0x6f6c7-ORIGIN
P_0006f6c7:
    .byte 0x74
    .org 0x6f6c8-ORIGIN
P_0006f6c8:
    .byte 0x00
    .org 0x6f6c9-ORIGIN
P_0006f6c9:
    .byte 0x02
    .org 0x6f6ca-ORIGIN
P_0006f6ca:
    .byte 0x5e
    .org 0x6f6cb-ORIGIN
P_0006f6cb:
    .byte 0x20
    .org 0x6f6cc-ORIGIN
P_0006f6cc:
    .byte 0x00
    .org 0x6f6cd-ORIGIN
P_0006f6cd:
    .byte 0x00
    .org 0x6f6ce-ORIGIN
P_0006f6ce:
    .byte 0x92
    .org 0x6f6cf-ORIGIN
P_0006f6cf:
    .byte 0xf2
    .org 0x6f6d0-ORIGIN
P_0006f6d0:
    .byte 0xff
    .org 0x6f6d1-ORIGIN
P_0006f6d1:
    .byte 0xff
    .org 0x6f6d2-ORIGIN
P_0006f6d2:
    .byte 0x28
    .org 0x6f6d3-ORIGIN
P_0006f6d3:
    .byte 0x98
