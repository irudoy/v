! Complete natural647E8 caller and exact byte-surface and implicit-byte-curve helpers.
! The26A80 entry is bound inside its complete normal26A60 exported parent.
    .text
    .balign 4
    .set ORIGIN,0x8798
    .org 0x8799-ORIGIN
P_00008799:
    .byte 0x0f
    .org 0x8b3f-ORIGIN
P_00008b3f:
    .byte 0x18
    .org 0x26084-ORIGIN
L_00026084:
    sts.l pr,@-r15
    .org 0x26086-ORIGIN
L_00026086:
    mov.l r4,@-r15
    .org 0x26088-ORIGIN
L_00026088:
    extu.b r7,r7
    .org 0x2608a-ORIGIN
L_0002608a:
    mov r5,r0
    .org 0x2608c-ORIGIN
L_0002608c:
    mov r7,r5
    .org 0x2608e-ORIGIN
L_0002608e:
    mov.l P_000260b8,r7
    .org 0x26090-ORIGIN
L_00026090:
    jsr @r7
    .org 0x26092-ORIGIN
L_00026092:
    mov #0x3,r4
    .org 0x26094-ORIGIN
L_00026094:
    mov.l r4,@-r15
    .org 0x26096-ORIGIN
L_00026096:
    mov.l r5,@-r15
    .org 0x26098-ORIGIN
L_00026098:
    mov r6,r0
    .org 0x2609a-ORIGIN
L_0002609a:
    mov.l @(0x10,r15),r5
    .org 0x2609c-ORIGIN
L_0002609c:
    extu.b r5,r5
    .org 0x2609e-ORIGIN
L_0002609e:
    jsr @r7
    .org 0x260a0-ORIGIN
L_000260a0:
    mov #0x3,r4
    .org 0x260a2-ORIGIN
L_000260a2:
    mov.l @r15+,r1
    .org 0x260a4-ORIGIN
L_000260a4:
    mov.l @r15+,r0
    .org 0x260a6-ORIGIN
L_000260a6:
    mov r4,r2
    .org 0x260a8-ORIGIN
L_000260a8:
    mov r5,r3
    .org 0x260aa-ORIGIN
L_000260aa:
    mov.l @r15+,r4
    .org 0x260ac-ORIGIN
L_000260ac:
    lds.l @r15+,pr
    .org 0x260ae-ORIGIN
L_000260ae:
    mov.l P_000260b4,r7
    .org 0x260b0-ORIGIN
L_000260b0:
    jmp @r7
    .org 0x260b2-ORIGIN
L_000260b2:
    mov #0x4,r5
    .org 0x260b4-ORIGIN
P_000260b4:
    .byte 0x00
    .org 0x260b5-ORIGIN
P_000260b5:
    .byte 0x02
    .org 0x260b6-ORIGIN
P_000260b6:
    .byte 0x67
    .org 0x260b7-ORIGIN
P_000260b7:
    .byte 0x70
    .org 0x260b8-ORIGIN
P_000260b8:
    .byte 0x00
    .org 0x260b9-ORIGIN
P_000260b9:
    .byte 0x02
    .org 0x260ba-ORIGIN
P_000260ba:
    .byte 0x69
    .org 0x260bb-ORIGIN
P_000260bb:
    .byte 0x44
    .org 0x26370-ORIGIN
L_00026370:
    mov.w P_00026382,r0
    .org 0x26372-ORIGIN
L_00026372:
    extu.b r5,r5
    .org 0x26374-ORIGIN
L_00026374:
    cmp/hs r0,r5
    .org 0x26376-ORIGIN
L_00026376:
    bt L_0002637e
    .org 0x26378-ORIGIN
L_00026378:
    mov.l P_00026384,r6
    .org 0x2637a-ORIGIN
L_0002637a:
    jmp @r6
    .org 0x2637c-ORIGIN
L_0002637c:
    mov #0x0,r3
    .org 0x2637e-ORIGIN
L_0002637e:
    rts
    .org 0x26380-ORIGIN
L_00026380:
    mov.b @(0x7,r4),r0
    .org 0x26382-ORIGIN
P_00026382:
    .byte 0x00
    .org 0x26383-ORIGIN
P_00026383:
    .byte 0xe0
    .org 0x26384-ORIGIN
P_00026384:
    .byte 0x00
    .org 0x26385-ORIGIN
P_00026385:
    .byte 0x02
    .org 0x26386-ORIGIN
P_00026386:
    .byte 0x6a
    .org 0x26387-ORIGIN
P_00026387:
    .byte 0x80
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
    .org 0x26770-ORIGIN
L_00026770:
    mov.l r8,@-r15
    .org 0x26772-ORIGIN
L_00026772:
    sts.l pr,@-r15
    .org 0x26774-ORIGIN
L_00026774:
    sts macl,r7
    .org 0x26776-ORIGIN
L_00026776:
    mulu.w r5,r0
    .org 0x26778-ORIGIN
L_00026778:
    add r2,r4
    .org 0x2677a-ORIGIN
L_0002677a:
    sts macl,r0
    .org 0x2677c-ORIGIN
L_0002677c:
    lds r7,macl
    .org 0x2677e-ORIGIN
L_0002677e:
    add r0,r4
    .org 0x26780-ORIGIN
L_00026780:
    add r4,r5
    .org 0x26782-ORIGIN
L_00026782:
    mov r1,r8
    .org 0x26784-ORIGIN
L_00026784:
    mov.l P_000267c8,r7
    .org 0x26786-ORIGIN
L_00026786:
    tst r3,r3
    .org 0x26788-ORIGIN
L_00026788:
    bt L_000267b0
    .org 0x2678a-ORIGIN
L_0002678a:
    mov.b @r4,r1
    .org 0x2678c-ORIGIN
L_0002678c:
    mov.b @(0x1,r4),r0
    .org 0x2678e-ORIGIN
L_0002678e:
    extu.b r0,r2
    .org 0x26790-ORIGIN
L_00026790:
    jsr @r7
    .org 0x26792-ORIGIN
L_00026792:
    extu.b r1,r0
    .org 0x26794-ORIGIN
L_00026794:
    tst r8,r8
    .org 0x26796-ORIGIN
L_00026796:
    bt L_000267c0
    .org 0x26798-ORIGIN
L_00026798:
    mov.l r0,@-r15
    .org 0x2679a-ORIGIN
L_0002679a:
    mov.b @r5,r1
    .org 0x2679c-ORIGIN
L_0002679c:
    mov.b @(0x1,r5),r0
    .org 0x2679e-ORIGIN
L_0002679e:
    extu.b r0,r2
    .org 0x267a0-ORIGIN
L_000267a0:
    jsr @r7
    .org 0x267a2-ORIGIN
L_000267a2:
    extu.b r1,r0
    .org 0x267a4-ORIGIN
L_000267a4:
    mov r0,r2
    .org 0x267a6-ORIGIN
L_000267a6:
    mov.l @r15+,r0
    .org 0x267a8-ORIGIN
L_000267a8:
    jsr @r7
    .org 0x267aa-ORIGIN
L_000267aa:
    mov r8,r3
    .org 0x267ac-ORIGIN
L_000267ac:
    bra L_000267c0
    .org 0x267ae-ORIGIN
L_000267ae:
    nop
    .org 0x267b0-ORIGIN
L_000267b0:
    tst r8,r8
    .org 0x267b2-ORIGIN
L_000267b2:
    bt/s L_000267c0
    .org 0x267b4-ORIGIN
L_000267b4:
    mov.b @r4,r0
    .org 0x267b6-ORIGIN
L_000267b6:
    mov.b @r5,r2
    .org 0x267b8-ORIGIN
L_000267b8:
    extu.b r0,r0
    .org 0x267ba-ORIGIN
L_000267ba:
    extu.b r2,r2
    .org 0x267bc-ORIGIN
L_000267bc:
    jsr @r7
    .org 0x267be-ORIGIN
L_000267be:
    mov r8,r3
    .org 0x267c0-ORIGIN
L_000267c0:
    lds.l @r15+,pr
    .org 0x267c2-ORIGIN
L_000267c2:
    rts
    .org 0x267c4-ORIGIN
L_000267c4:
    mov.l @r15+,r8
    .org 0x267c8-ORIGIN
P_000267c8:
    .byte 0x00
    .org 0x267c9-ORIGIN
P_000267c9:
    .byte 0x02
    .org 0x267ca-ORIGIN
P_000267ca:
    .byte 0x67
    .org 0x267cb-ORIGIN
P_000267cb:
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
    .org 0x647e8-ORIGIN
L_000647e8:
    mov.l r13,@-r15
    .org 0x647ea-ORIGIN
L_000647ea:
    mov.l r14,@-r15
    .org 0x647ec-ORIGIN
L_000647ec:
    sts.l pr,@-r15
    .org 0x647ee-ORIGIN
L_000647ee:
    sts.l macl,@-r15
    .org 0x647f0-ORIGIN
L_000647f0:
    stc.l gbr,@-r15
    .org 0x647f2-ORIGIN
L_000647f2:
    mov.l P_000648d0,r0
    .org 0x647f4-ORIGIN
L_000647f4:
    ldc r0,gbr
    .org 0x647f6-ORIGIN
L_000647f6:
    add #-0x4,r15
    .org 0x647f8-ORIGIN
L_000647f8:
    mov.l P_00064894,r2
    .org 0x647fa-ORIGIN
L_000647fa:
    mov.b @r2,r0
    .org 0x647fc-ORIGIN
L_000647fc:
    and #0x10,r0
    .org 0x647fe-ORIGIN
L_000647fe:
    tst r0,r0
    .org 0x64800-ORIGIN
L_00064800:
    bt/s L_0006480e
    .org 0x64802-ORIGIN
L_00064802:
    mov r0,r5
    .org 0x64804-ORIGIN
L_00064804:
    mov.b @(0x1,gbr),r0
    .org 0x64806-ORIGIN
L_00064806:
    mov r0,r6
    .org 0x64808-ORIGIN
L_00064808:
    mov.b @(0x0,gbr),r0
    .org 0x6480a-ORIGIN
L_0006480a:
    cmp/hs r0,r6
    .org 0x6480c-ORIGIN
L_0006480c:
    bf L_0006481a
    .org 0x6480e-ORIGIN
L_0006480e:
    tst r5,r5
    .org 0x64810-ORIGIN
L_00064810:
    bf L_000648f0
    .org 0x64812-ORIGIN
L_00064812:
    mov.l P_000648d4,r6
    .org 0x64814-ORIGIN
L_00064814:
    mov.b @r6,r0
    .org 0x64816-ORIGIN
L_00064816:
    tst #0x40,r0
    .org 0x64818-ORIGIN
L_00064818:
    bt L_000648f0
    .org 0x6481a-ORIGIN
L_0006481a:
    mov.l P_000648d8,r13
    .org 0x6481c-ORIGIN
L_0006481c:
    mov #0x3,r5
    .org 0x6481e-ORIGIN
L_0006481e:
    mov.w P_00064886,r0
    .org 0x64820-ORIGIN
L_00064820:
    mov.l P_000648a4,r14
    .org 0x64822-ORIGIN
L_00064822:
    mov.b @(r0,r13),r2
    .org 0x64824-ORIGIN
L_00064824:
    mov.w P_00064888,r0
    .org 0x64826-ORIGIN
L_00064826:
    mov.b r2,@(r0,r14)
    .org 0x64828-ORIGIN
L_00064828:
    mov #-0x1,r2
    .org 0x6482a-ORIGIN
L_0006482a:
    mov.w P_0006488a,r0
    .org 0x6482c-ORIGIN
L_0006482c:
    mov.w r2,@(r0,r14)
    .org 0x6482e-ORIGIN
L_0006482e:
    mov.b @(0x1,gbr),r0
    .org 0x64830-ORIGIN
L_00064830:
    extu.b r0,r2
    .org 0x64832-ORIGIN
L_00064832:
    cmp/gt r5,r2
    .org 0x64834-ORIGIN
L_00064834:
    bf L_00064838
    .org 0x64836-ORIGIN
L_00064836:
    mov #0x3,r2
    .org 0x64838-ORIGIN
L_00064838:
    mov.b @(0x0,gbr),r0
    .org 0x6483a-ORIGIN
L_0006483a:
    mov r2,r4
    .org 0x6483c-ORIGIN
L_0006483c:
    mov #0x1,r5
    .org 0x6483e-ORIGIN
L_0006483e:
    extu.b r0,r2
    .org 0x64840-ORIGIN
L_00064840:
    cmp/ge r5,r2
    .org 0x64842-ORIGIN
L_00064842:
    bt L_00064846
    .org 0x64844-ORIGIN
L_00064844:
    mov #0x1,r2
    .org 0x64846-ORIGIN
L_00064846:
    extu.b r2,r2
    .org 0x64848-ORIGIN
L_00064848:
    mov #0x4,r5
    .org 0x6484a-ORIGIN
L_0006484a:
    cmp/gt r5,r2
    .org 0x6484c-ORIGIN
L_0006484c:
    bf L_00064850
    .org 0x6484e-ORIGIN
L_0006484e:
    mov #0x4,r2
    .org 0x64850-ORIGIN
L_00064850:
    extu.b r2,r0
    .org 0x64852-ORIGIN
L_00064852:
    mov.l P_000648dc,r5
    .org 0x64854-ORIGIN
L_00064854:
    shll2 r0
    .org 0x64856-ORIGIN
L_00064856:
    mov.l P_000648bc,r7
    .org 0x64858-ORIGIN
L_00064858:
    extu.b r4,r4
    .org 0x6485a-ORIGIN
L_0006485a:
    mov.l P_000648e0,r2
    .org 0x6485c-ORIGIN
L_0006485c:
    add #-0x4,r5
    .org 0x6485e-ORIGIN
L_0006485e:
    add r4,r0
    .org 0x64860-ORIGIN
L_00064860:
    mov.l P_000648e4,r4
    .org 0x64862-ORIGIN
L_00064862:
    mov.b @(r0,r5),r6
    .org 0x64864-ORIGIN
L_00064864:
    mov.w P_0006488c,r0
    .org 0x64866-ORIGIN
L_00064866:
    mov.l P_000648e8,r5
    .org 0x64868-ORIGIN
L_00064868:
    mov.b r6,@(r0,r14)
    .org 0x6486a-ORIGIN
L_0006486a:
    mov r6,r0
    .org 0x6486c-ORIGIN
L_0006486c:
    mov.b r0,@(0x3,r15)
    .org 0x6486e-ORIGIN
L_0006486e:
    mov #0x12,r0
    .org 0x64870-ORIGIN
L_00064870:
    mov.b @(r0,r7),r6
    .org 0x64872-ORIGIN
L_00064872:
    extu.b r6,r7
    .org 0x64874-ORIGIN
L_00064874:
    mov.l P_000648ec,r6
    .org 0x64876-ORIGIN
L_00064876:
    jsr @r2
    .org 0x64878-ORIGIN
L_00064878:
    nop
    .org 0x6487a-ORIGIN
L_0006487a:
    extu.b r0,r2
    .org 0x6487c-ORIGIN
L_0006487c:
    mov.w P_00064886,r0
    .org 0x6487e-ORIGIN
L_0006487e:
    mov.b @(r0,r13),r5
    .org 0x64880-ORIGIN
L_00064880:
    extu.b r5,r6
    .org 0x64882-ORIGIN
L_00064882:
    bra L_000649fe
    .org 0x64884-ORIGIN
L_00064884:
    mulu.w r2,r6
    .org 0x64886-ORIGIN
P_00064886:
    .byte 0x0a
    .org 0x64887-ORIGIN
P_00064887:
    .byte 0x7b
    .org 0x64888-ORIGIN
P_00064888:
    .byte 0x05
    .org 0x64889-ORIGIN
P_00064889:
    .byte 0xe7
    .org 0x6488a-ORIGIN
P_0006488a:
    .byte 0x01
    .org 0x6488b-ORIGIN
P_0006488b:
    .byte 0x52
    .org 0x6488c-ORIGIN
P_0006488c:
    .byte 0x05
    .org 0x6488d-ORIGIN
P_0006488d:
    .byte 0xd5
    .org 0x64894-ORIGIN
P_00064894:
    .byte 0x00
    .org 0x64895-ORIGIN
P_00064895:
    .byte 0x00
    .org 0x64896-ORIGIN
P_00064896:
    .byte 0x8b
    .org 0x64897-ORIGIN
P_00064897:
    .byte 0x3f
    .org 0x648a4-ORIGIN
P_000648a4:
    .byte 0xff
    .org 0x648a5-ORIGIN
P_000648a5:
    .byte 0xff
    .org 0x648a6-ORIGIN
P_000648a6:
    .byte 0x12
    .org 0x648a7-ORIGIN
P_000648a7:
    .byte 0x8c
    .org 0x648bc-ORIGIN
P_000648bc:
    .byte 0xff
    .org 0x648bd-ORIGIN
P_000648bd:
    .byte 0xff
    .org 0x648be-ORIGIN
P_000648be:
    .byte 0x11
    .org 0x648bf-ORIGIN
P_000648bf:
    .byte 0x9c
    .org 0x648d0-ORIGIN
P_000648d0:
    .byte 0xff
    .org 0x648d1-ORIGIN
P_000648d1:
    .byte 0xff
    .org 0x648d2-ORIGIN
P_000648d2:
    .byte 0x10
    .org 0x648d3-ORIGIN
P_000648d3:
    .byte 0x82
    .org 0x648d4-ORIGIN
P_000648d4:
    .byte 0xff
    .org 0x648d5-ORIGIN
P_000648d5:
    .byte 0xff
    .org 0x648d6-ORIGIN
P_000648d6:
    .byte 0x24
    .org 0x648d7-ORIGIN
P_000648d7:
    .byte 0x4f
    .org 0x648d8-ORIGIN
P_000648d8:
    .byte 0xff
    .org 0x648d9-ORIGIN
P_000648d9:
    .byte 0xff
    .org 0x648da-ORIGIN
P_000648da:
    .byte 0x28
    .org 0x648db-ORIGIN
P_000648db:
    .byte 0xf8
    .org 0x648dc-ORIGIN
P_000648dc:
    .byte 0x00
    .org 0x648dd-ORIGIN
P_000648dd:
    .byte 0x00
    .org 0x648de-ORIGIN
P_000648de:
    .byte 0xb6
    .org 0x648df-ORIGIN
P_000648df:
    .byte 0x0a
    .org 0x648e0-ORIGIN
P_000648e0:
    .byte 0x00
    .org 0x648e1-ORIGIN
P_000648e1:
    .byte 0x02
    .org 0x648e2-ORIGIN
P_000648e2:
    .byte 0x60
    .org 0x648e3-ORIGIN
P_000648e3:
    .byte 0x84
    .org 0x648e4-ORIGIN
P_000648e4:
    .byte 0x00
    .org 0x648e5-ORIGIN
P_000648e5:
    .byte 0x00
    .org 0x648e6-ORIGIN
P_000648e6:
    .byte 0xb5
    .org 0x648e7-ORIGIN
P_000648e7:
    .byte 0xfa
    .org 0x648e8-ORIGIN
P_000648e8:
    .byte 0x00
    .org 0x648e9-ORIGIN
P_000648e9:
    .byte 0x01
    .org 0x648ea-ORIGIN
P_000648ea:
    .byte 0x1f
    .org 0x648eb-ORIGIN
P_000648eb:
    .byte 0xe2
    .org 0x648ec-ORIGIN
P_000648ec:
    .byte 0x00
    .org 0x648ed-ORIGIN
P_000648ed:
    .byte 0x01
    .org 0x648ee-ORIGIN
P_000648ee:
    .byte 0x1f
    .org 0x648ef-ORIGIN
P_000648ef:
    .byte 0xde
    .org 0x648f0-ORIGIN
L_000648f0:
    tst r5,r5
    .org 0x648f2-ORIGIN
L_000648f2:
    bt L_000648fe
    .org 0x648f4-ORIGIN
L_000648f4:
    mov.b @(0x1,gbr),r0
    .org 0x648f6-ORIGIN
L_000648f6:
    mov r0,r6
    .org 0x648f8-ORIGIN
L_000648f8:
    mov.b @(0x0,gbr),r0
    .org 0x648fa-ORIGIN
L_000648fa:
    cmp/hi r0,r6
    .org 0x648fc-ORIGIN
L_000648fc:
    bt L_0006490a
    .org 0x648fe-ORIGIN
L_000648fe:
    tst r5,r5
    .org 0x64900-ORIGIN
L_00064900:
    bf L_00064980
    .org 0x64902-ORIGIN
L_00064902:
    mov.l P_00064b44,r6
    .org 0x64904-ORIGIN
L_00064904:
    mov.b @(0x1,r6),r0
    .org 0x64906-ORIGIN
L_00064906:
    tst #0x20,r0
    .org 0x64908-ORIGIN
L_00064908:
    bt L_00064980
    .org 0x6490a-ORIGIN
L_0006490a:
    mov.b @(0x1,gbr),r0
    .org 0x6490c-ORIGIN
L_0006490c:
    mov #0x1,r5
    .org 0x6490e-ORIGIN
L_0006490e:
    extu.b r0,r2
    .org 0x64910-ORIGIN
L_00064910:
    cmp/ge r5,r2
    .org 0x64912-ORIGIN
L_00064912:
    bt L_00064916
    .org 0x64914-ORIGIN
L_00064914:
    mov #0x1,r2
    .org 0x64916-ORIGIN
L_00064916:
    extu.b r2,r2
    .org 0x64918-ORIGIN
L_00064918:
    mov #0x4,r5
    .org 0x6491a-ORIGIN
L_0006491a:
    cmp/gt r5,r2
    .org 0x6491c-ORIGIN
L_0006491c:
    bf L_00064920
    .org 0x6491e-ORIGIN
L_0006491e:
    mov #0x4,r2
    .org 0x64920-ORIGIN
L_00064920:
    add #-0x1,r2
    .org 0x64922-ORIGIN
L_00064922:
    extu.b r2,r2
    .org 0x64924-ORIGIN
L_00064924:
    mov.l P_00064b48,r6
    .org 0x64926-ORIGIN
L_00064926:
    extu.b r2,r4
    .org 0x64928-ORIGIN
L_00064928:
    mov.l P_00064b4c,r13
    .org 0x6492a-ORIGIN
L_0006492a:
    mov r4,r0
    .org 0x6492c-ORIGIN
L_0006492c:
    mov.b @(r0,r6),r2
    .org 0x6492e-ORIGIN
L_0006492e:
    mov.w P_00064a14,r0
    .org 0x64930-ORIGIN
L_00064930:
    extu.b r2,r6
    .org 0x64932-ORIGIN
L_00064932:
    mov.b @(r0,r13),r7
    .org 0x64934-ORIGIN
L_00064934:
    extu.b r7,r7
    .org 0x64936-ORIGIN
L_00064936:
    mul.l r6,r7
    .org 0x64938-ORIGIN
L_00064938:
    sts macl,r2
    .org 0x6493a-ORIGIN
L_0006493a:
    cmp/pz r2
    .org 0x6493c-ORIGIN
L_0006493c:
    bt L_00064944
    .org 0x6493e-ORIGIN
L_0006493e:
    mov #-0x1,r6
    .org 0x64940-ORIGIN
L_00064940:
    extu.b r6,r6
    .org 0x64942-ORIGIN
L_00064942:
    add r6,r2
    .org 0x64944-ORIGIN
L_00064944:
    mov r2,r6
    .org 0x64946-ORIGIN
L_00064946:
    shlr8 r6
    .org 0x64948-ORIGIN
L_00064948:
    swap.w r6,r5
    .org 0x6494a-ORIGIN
L_0006494a:
    mov.l P_00064b50,r14
    .org 0x6494c-ORIGIN
L_0006494c:
    exts.b r5,r6
    .org 0x6494e-ORIGIN
L_0006494e:
    mov.w P_00064a16,r0
    .org 0x64950-ORIGIN
L_00064950:
    xtrct r6,r5
    .org 0x64952-ORIGIN
L_00064952:
    mov r7,r6
    .org 0x64954-ORIGIN
L_00064954:
    mov.b r5,@(r0,r14)
    .org 0x64956-ORIGIN
L_00064956:
    extu.b r5,r5
    .org 0x64958-ORIGIN
L_00064958:
    sub r5,r6
    .org 0x6495a-ORIGIN
L_0006495a:
    exts.w r6,r2
    .org 0x6495c-ORIGIN
L_0006495c:
    cmp/pz r2
    .org 0x6495e-ORIGIN
L_0006495e:
    bt L_00064962
    .org 0x64960-ORIGIN
L_00064960:
    mov #0x0,r2
    .org 0x64962-ORIGIN
L_00064962:
    mov r2,r6
    .org 0x64964-ORIGIN
L_00064964:
    mov.l P_00064b54,r2
    .org 0x64966-ORIGIN
L_00064966:
    mov r4,r0
    .org 0x64968-ORIGIN
L_00064968:
    add #0xc,r2
    .org 0x6496a-ORIGIN
L_0006496a:
    mov.b @(r0,r2),r5
    .org 0x6496c-ORIGIN
L_0006496c:
    mov.w P_00064a18,r0
    .org 0x6496e-ORIGIN
L_0006496e:
    extu.b r5,r5
    .org 0x64970-ORIGIN
L_00064970:
    mulu.w r5,r6
    .org 0x64972-ORIGIN
L_00064972:
    mov.l P_00064b58,r6
    .org 0x64974-ORIGIN
L_00064974:
    sts macl,r2
    .org 0x64976-ORIGIN
L_00064976:
    mov.w r2,@(r0,r14)
    .org 0x64978-ORIGIN
L_00064978:
    mov.b @r6,r2
    .org 0x6497a-ORIGIN
L_0006497a:
    extu.b r2,r6
    .org 0x6497c-ORIGIN
L_0006497c:
    bra L_000649fe
    .org 0x6497e-ORIGIN
L_0006497e:
    mulu.w r7,r6
    .org 0x64980-ORIGIN
L_00064980:
    tst r5,r5
    .org 0x64982-ORIGIN
L_00064982:
    bf L_00064a06
    .org 0x64984-ORIGIN
L_00064984:
    mov.l P_00064b44,r6
    .org 0x64986-ORIGIN
L_00064986:
    mov.b @r6,r0
    .org 0x64988-ORIGIN
L_00064988:
    tst #0x1,r0
    .org 0x6498a-ORIGIN
L_0006498a:
    bt L_00064a06
    .org 0x6498c-ORIGIN
L_0006498c:
    mov.l P_00064b50,r14
    .org 0x6498e-ORIGIN
L_0006498e:
    mov #0x0,r2
    .org 0x64990-ORIGIN
L_00064990:
    mov.w P_00064a16,r0
    .org 0x64992-ORIGIN
L_00064992:
    mov #0x1,r5
    .org 0x64994-ORIGIN
L_00064994:
    mov.b r2,@(r0,r14)
    .org 0x64996-ORIGIN
L_00064996:
    mov.b @(0x1,gbr),r0
    .org 0x64998-ORIGIN
L_00064998:
    extu.b r0,r2
    .org 0x6499a-ORIGIN
L_0006499a:
    cmp/ge r5,r2
    .org 0x6499c-ORIGIN
L_0006499c:
    bt L_000649a0
    .org 0x6499e-ORIGIN
L_0006499e:
    mov #0x1,r2
    .org 0x649a0-ORIGIN
L_000649a0:
    extu.b r2,r2
    .org 0x649a2-ORIGIN
L_000649a2:
    mov #0x4,r5
    .org 0x649a4-ORIGIN
L_000649a4:
    cmp/gt r5,r2
    .org 0x649a6-ORIGIN
L_000649a6:
    bf L_000649aa
    .org 0x649a8-ORIGIN
L_000649a8:
    mov #0x4,r2
    .org 0x649aa-ORIGIN
L_000649aa:
    mov.l P_00064b54,r4
    .org 0x649ac-ORIGIN
L_000649ac:
    extu.b r2,r0
    .org 0x649ae-ORIGIN
L_000649ae:
    mov.l P_00064b4c,r13
    .org 0x649b0-ORIGIN
L_000649b0:
    mov r4,r2
    .org 0x649b2-ORIGIN
L_000649b2:
    add #0x7,r2
    .org 0x649b4-ORIGIN
L_000649b4:
    mov.b @(r0,r2),r6
    .org 0x649b6-ORIGIN
L_000649b6:
    mov.w P_00064a14,r0
    .org 0x649b8-ORIGIN
L_000649b8:
    extu.b r6,r2
    .org 0x649ba-ORIGIN
L_000649ba:
    mov.b @(r0,r13),r6
    .org 0x649bc-ORIGIN
L_000649bc:
    mov.w P_00064a18,r0
    .org 0x649be-ORIGIN
L_000649be:
    extu.b r6,r5
    .org 0x649c0-ORIGIN
L_000649c0:
    mov.l P_00064b5c,r6
    .org 0x649c2-ORIGIN
L_000649c2:
    mulu.w r2,r5
    .org 0x649c4-ORIGIN
L_000649c4:
    sts macl,r2
    .org 0x649c6-ORIGIN
L_000649c6:
    mov.w r2,@(r0,r14)
    .org 0x649c8-ORIGIN
L_000649c8:
    mov.w @r6,r2
    .org 0x649ca-ORIGIN
L_000649ca:
    extu.w r2,r6
    .org 0x649cc-ORIGIN
L_000649cc:
    mov.w P_00064a1a,r2
    .org 0x649ce-ORIGIN
L_000649ce:
    mul.l r6,r2
    .org 0x649d0-ORIGIN
L_000649d0:
    sts macl,r5
    .org 0x649d2-ORIGIN
L_000649d2:
    shlr8 r5
    .org 0x649d4-ORIGIN
L_000649d4:
    shlr2 r5
    .org 0x649d6-ORIGIN
L_000649d6:
    shlr2 r5
    .org 0x649d8-ORIGIN
L_000649d8:
    shlr2 r5
    .org 0x649da-ORIGIN
L_000649da:
    shlr r5
    .org 0x649dc-ORIGIN
L_000649dc:
    add #-0x20,r5
    .org 0x649de-ORIGIN
L_000649de:
    cmp/pz r5
    .org 0x649e0-ORIGIN
L_000649e0:
    bt L_000649e4
    .org 0x649e2-ORIGIN
L_000649e2:
    mov #0x0,r5
    .org 0x649e4-ORIGIN
L_000649e4:
    mov #-0x1,r6
    .org 0x649e6-ORIGIN
L_000649e6:
    extu.b r6,r6
    .org 0x649e8-ORIGIN
L_000649e8:
    cmp/gt r6,r5
    .org 0x649ea-ORIGIN
L_000649ea:
    bf L_000649ee
    .org 0x649ec-ORIGIN
L_000649ec:
    mov r6,r5
    .org 0x649ee-ORIGIN
L_000649ee:
    mov.l P_00064b60,r2
    .org 0x649f0-ORIGIN
L_000649f0:
    jsr @r2
    .org 0x649f2-ORIGIN
L_000649f2:
    extu.b r5,r5
    .org 0x649f4-ORIGIN
L_000649f4:
    extu.b r0,r2
    .org 0x649f6-ORIGIN
L_000649f6:
    mov.w P_00064a14,r0
    .org 0x649f8-ORIGIN
L_000649f8:
    mov.b @(r0,r13),r6
    .org 0x649fa-ORIGIN
L_000649fa:
    extu.b r6,r5
    .org 0x649fc-ORIGIN
L_000649fc:
    mulu.w r2,r5
    .org 0x649fe-ORIGIN
L_000649fe:
    sts macl,r2
    .org 0x64a00-ORIGIN
L_00064a00:
    mov #0x54,r0
    .org 0x64a02-ORIGIN
L_00064a02:
    shll2 r0
    .org 0x64a04-ORIGIN
L_00064a04:
    mov.w r2,@(r0,r14)
    .org 0x64a06-ORIGIN
L_00064a06:
    add #0x4,r15
    .org 0x64a08-ORIGIN
L_00064a08:
    ldc.l @r15+,gbr
    .org 0x64a0a-ORIGIN
L_00064a0a:
    lds.l @r15+,macl
    .org 0x64a0c-ORIGIN
L_00064a0c:
    lds.l @r15+,pr
    .org 0x64a0e-ORIGIN
L_00064a0e:
    mov.l @r15+,r14
    .org 0x64a10-ORIGIN
L_00064a10:
    rts
    .org 0x64a12-ORIGIN
L_00064a12:
    mov.l @r15+,r13
    .org 0x64a14-ORIGIN
P_00064a14:
    .byte 0x0a
    .org 0x64a15-ORIGIN
P_00064a15:
    .byte 0x7b
    .org 0x64a16-ORIGIN
P_00064a16:
    .byte 0x05
    .org 0x64a17-ORIGIN
P_00064a17:
    .byte 0xe7
    .org 0x64a18-ORIGIN
P_00064a18:
    .byte 0x01
    .org 0x64a19-ORIGIN
P_00064a19:
    .byte 0x52
    .org 0x64a1a-ORIGIN
P_00064a1a:
    .byte 0x2d
    .org 0x64a1b-ORIGIN
P_00064a1b:
    .byte 0x0e
    .org 0x64b44-ORIGIN
P_00064b44:
    .byte 0xff
    .org 0x64b45-ORIGIN
P_00064b45:
    .byte 0xff
    .org 0x64b46-ORIGIN
P_00064b46:
    .byte 0x24
    .org 0x64b47-ORIGIN
P_00064b47:
    .byte 0x4f
    .org 0x64b48-ORIGIN
P_00064b48:
    .byte 0x00
    .org 0x64b49-ORIGIN
P_00064b49:
    .byte 0x01
    .org 0x64b4a-ORIGIN
P_00064b4a:
    .byte 0x2b
    .org 0x64b4b-ORIGIN
P_00064b4b:
    .byte 0x62
    .org 0x64b4c-ORIGIN
P_00064b4c:
    .byte 0xff
    .org 0x64b4d-ORIGIN
P_00064b4d:
    .byte 0xff
    .org 0x64b4e-ORIGIN
P_00064b4e:
    .byte 0x28
    .org 0x64b4f-ORIGIN
P_00064b4f:
    .byte 0xf8
    .org 0x64b50-ORIGIN
P_00064b50:
    .byte 0xff
    .org 0x64b51-ORIGIN
P_00064b51:
    .byte 0xff
    .org 0x64b52-ORIGIN
P_00064b52:
    .byte 0x12
    .org 0x64b53-ORIGIN
P_00064b53:
    .byte 0x8c
    .org 0x64b54-ORIGIN
P_00064b54:
    .byte 0x00
    .org 0x64b55-ORIGIN
P_00064b55:
    .byte 0x01
    .org 0x64b56-ORIGIN
P_00064b56:
    .byte 0x1f
    .org 0x64b57-ORIGIN
P_00064b57:
    .byte 0xe6
    .org 0x64b58-ORIGIN
P_00064b58:
    .byte 0x00
    .org 0x64b59-ORIGIN
P_00064b59:
    .byte 0x00
    .org 0x64b5a-ORIGIN
P_00064b5a:
    .byte 0x87
    .org 0x64b5b-ORIGIN
P_00064b5b:
    .byte 0x99
    .org 0x64b5c-ORIGIN
P_00064b5c:
    .byte 0xff
    .org 0x64b5d-ORIGIN
P_00064b5d:
    .byte 0xff
    .org 0x64b5e-ORIGIN
P_00064b5e:
    .byte 0x40
    .org 0x64b5f-ORIGIN
P_00064b5f:
    .byte 0xc6
    .org 0x64b60-ORIGIN
P_00064b60:
    .byte 0x00
    .org 0x64b61-ORIGIN
P_00064b61:
    .byte 0x02
    .org 0x64b62-ORIGIN
P_00064b62:
    .byte 0x63
    .org 0x64b63-ORIGIN
P_00064b63:
    .byte 0x70
