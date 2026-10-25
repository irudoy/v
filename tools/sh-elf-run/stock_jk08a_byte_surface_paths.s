! Natural JK08A byte-surface caller and complete interpolation helper closure.
! Tested instructions retain their stock bytes, entries and branch delay slots.
! Pool 000c0008 is a wrapping GBR-relative ROM offset, not a RAM pointer.
    .text
    .balign 4
    .set ORIGIN,0x26084
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
    mov.l L_000260b8,r7
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
    mov.l L_000260b4,r7
    .org 0x260b0-ORIGIN
L_000260b0:
    jmp @r7
    .org 0x260b2-ORIGIN
L_000260b2:
    mov #0x4,r5
    .org 0x260b4-ORIGIN
L_000260b4:
    .long 0x00026770
    .org 0x260b8-ORIGIN
L_000260b8:
    .long 0x00026944
    .org 0x26140-ORIGIN
L_00026140:
    sts.l pr,@-r15
    .org 0x26142-ORIGIN
L_00026142:
    mov.l r4,@-r15
    .org 0x26144-ORIGIN
L_00026144:
    extu.b r7,r7
    .org 0x26146-ORIGIN
L_00026146:
    mov r5,r0
    .org 0x26148-ORIGIN
L_00026148:
    mov r7,r5
    .org 0x2614a-ORIGIN
L_0002614a:
    mov.l L_00026174,r7
    .org 0x2614c-ORIGIN
L_0002614c:
    jsr @r7
    .org 0x2614e-ORIGIN
L_0002614e:
    mov #0x7,r4
    .org 0x26150-ORIGIN
L_00026150:
    mov.l r4,@-r15
    .org 0x26152-ORIGIN
L_00026152:
    mov.l r5,@-r15
    .org 0x26154-ORIGIN
L_00026154:
    mov r6,r0
    .org 0x26156-ORIGIN
L_00026156:
    mov.l @(0x10,r15),r5
    .org 0x26158-ORIGIN
L_00026158:
    extu.b r5,r5
    .org 0x2615a-ORIGIN
L_0002615a:
    jsr @r7
    .org 0x2615c-ORIGIN
L_0002615c:
    mov #0x7,r4
    .org 0x2615e-ORIGIN
L_0002615e:
    mov.l @r15+,r1
    .org 0x26160-ORIGIN
L_00026160:
    mov.l @r15+,r0
    .org 0x26162-ORIGIN
L_00026162:
    mov r4,r2
    .org 0x26164-ORIGIN
L_00026164:
    mov r5,r3
    .org 0x26166-ORIGIN
L_00026166:
    mov.l @r15+,r4
    .org 0x26168-ORIGIN
L_00026168:
    lds.l @r15+,pr
    .org 0x2616a-ORIGIN
L_0002616a:
    mov.l L_00026170,r7
    .org 0x2616c-ORIGIN
L_0002616c:
    jmp @r7
    .org 0x2616e-ORIGIN
L_0002616e:
    mov #0x8,r5
    .org 0x26170-ORIGIN
L_00026170:
    .long 0x00026770
    .org 0x26174-ORIGIN
L_00026174:
    .long 0x00026944
    .org 0x261b8-ORIGIN
L_000261b8:
    sts.l pr,@-r15
    .org 0x261ba-ORIGIN
L_000261ba:
    mov.l r4,@-r15
    .org 0x261bc-ORIGIN
L_000261bc:
    extu.b r7,r7
    .org 0x261be-ORIGIN
L_000261be:
    mov r5,r0
    .org 0x261c0-ORIGIN
L_000261c0:
    mov r7,r5
    .org 0x261c2-ORIGIN
L_000261c2:
    mov.l L_000261ec,r7
    .org 0x261c4-ORIGIN
L_000261c4:
    jsr @r7
    .org 0x261c6-ORIGIN
L_000261c6:
    mov #0xf,r4
    .org 0x261c8-ORIGIN
L_000261c8:
    mov.l r4,@-r15
    .org 0x261ca-ORIGIN
L_000261ca:
    mov.l r5,@-r15
    .org 0x261cc-ORIGIN
L_000261cc:
    mov r6,r0
    .org 0x261ce-ORIGIN
L_000261ce:
    mov.l @(0x10,r15),r5
    .org 0x261d0-ORIGIN
L_000261d0:
    extu.b r5,r5
    .org 0x261d2-ORIGIN
L_000261d2:
    jsr @r7
    .org 0x261d4-ORIGIN
L_000261d4:
    mov #0xf,r4
    .org 0x261d6-ORIGIN
L_000261d6:
    mov.l @r15+,r1
    .org 0x261d8-ORIGIN
L_000261d8:
    mov.l @r15+,r0
    .org 0x261da-ORIGIN
L_000261da:
    mov r4,r2
    .org 0x261dc-ORIGIN
L_000261dc:
    mov r5,r3
    .org 0x261de-ORIGIN
L_000261de:
    mov.l @r15+,r4
    .org 0x261e0-ORIGIN
L_000261e0:
    lds.l @r15+,pr
    .org 0x261e2-ORIGIN
L_000261e2:
    mov.l L_000261e8,r7
    .org 0x261e4-ORIGIN
L_000261e4:
    jmp @r7
    .org 0x261e6-ORIGIN
L_000261e6:
    mov #0x10,r5
    .org 0x261e8-ORIGIN
L_000261e8:
    .long 0x00026770
    .org 0x261ec-ORIGIN
L_000261ec:
    .long 0x00026944
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
    mov.l L_000267c8,r7
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
L_000267c8:
    .long 0x00026740
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
    mov.l L_00026980,r2
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
L_00026980:
    .long 0x00026c78
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
    .org 0xbfdc0-ORIGIN
L_000bfdc0:
    mov.l r10,@-r15
    .org 0xbfdc2-ORIGIN
L_000bfdc2:
    mov.l r11,@-r15
    .org 0xbfdc4-ORIGIN
L_000bfdc4:
    mov.l r12,@-r15
    .org 0xbfdc6-ORIGIN
L_000bfdc6:
    mov.l r13,@-r15
    .org 0xbfdc8-ORIGIN
L_000bfdc8:
    mov.l r14,@-r15
    .org 0xbfdca-ORIGIN
L_000bfdca:
    sts.l pr,@-r15
    .org 0xbfdcc-ORIGIN
L_000bfdcc:
    stc.l gbr,@-r15
    .org 0xbfdce-ORIGIN
L_000bfdce:
    mov.l L_000c0000,r0
    .org 0xbfdd0-ORIGIN
L_000bfdd0:
    ldc r0,gbr
    .org 0xbfdd2-ORIGIN
L_000bfdd2:
    add #-0x4,r15
    .org 0xbfdd4-ORIGIN
L_000bfdd4:
    mov.l L_000c0004,r6
    .org 0xbfdd6-ORIGIN
L_000bfdd6:
    mov.b @(0x4,r6),r0
    .org 0xbfdd8-ORIGIN
L_000bfdd8:
    tst #0x8,r0
    .org 0xbfdda-ORIGIN
L_000bfdda:
    bt L_000bfde6
    .org 0xbfddc-ORIGIN
L_000bfddc:
    mov.l L_000c0008,r0
    .org 0xbfdde-ORIGIN
L_000bfdde:
    tst.b #0x1,@(r0,gbr)
    .org 0xbfde0-ORIGIN
L_000bfde0:
    bt L_000bfde6
    .org 0xbfde2-ORIGIN
L_000bfde2:
    bra L_000bfdea
    .org 0xbfde4-ORIGIN
L_000bfde4:
    mov #-0x1,r14
    .org 0xbfde6-ORIGIN
L_000bfde6:
    mov.l L_000c000c,r6
    .org 0xbfde8-ORIGIN
L_000bfde8:
    mov.b @r6,r14
    .org 0xbfdea-ORIGIN
L_000bfdea:
    mov.l L_000c0010,r11
    .org 0xbfdec-ORIGIN
L_000bfdec:
    mov r14,r0
    .org 0xbfdee-ORIGIN
L_000bfdee:
    mov.b r0,@(0x3,r15)
    .org 0xbfdf0-ORIGIN
L_000bfdf0:
    mov #0x12,r0
    .org 0xbfdf2-ORIGIN
L_000bfdf2:
    stc gbr,r5
    .org 0xbfdf4-ORIGIN
L_000bfdf4:
    mov.b @(r0,r11),r13
    .org 0xbfdf6-ORIGIN
L_000bfdf6:
    add #0x20,r5
    .org 0xbfdf8-ORIGIN
L_000bfdf8:
    mov.l L_000c0014,r4
    .org 0xbfdfa-ORIGIN
L_000bfdfa:
    stc gbr,r6
    .org 0xbfdfc-ORIGIN
L_000bfdfc:
    mov.l L_000c0018,r2
    .org 0xbfdfe-ORIGIN
L_000bfdfe:
    mov.l L_000bfff8,r10
    .org 0xbfe00-ORIGIN
L_000bfe00:
    jsr @r2
    .org 0xbfe02-ORIGIN
L_000bfe02:
    extu.b r13,r7
    .org 0xbfe04-ORIGIN
L_000bfe04:
    mov r0,r2
    .org 0xbfe06-ORIGIN
L_000bfe06:
    mov.w L_000bfe84,r0
    .org 0xbfe08-ORIGIN
L_000bfe08:
    mov #-0x74,r6
    .org 0xbfe0a-ORIGIN
L_000bfe0a:
    mov.l L_000c001c,r4
    .org 0xbfe0c-ORIGIN
L_000bfe0c:
    stc gbr,r5
    .org 0xbfe0e-ORIGIN
L_000bfe0e:
    mov.b r2,@(r0,r10)
    .org 0xbfe10-ORIGIN
L_000bfe10:
    extu.b r6,r6
    .org 0xbfe12-ORIGIN
L_000bfe12:
    mov r14,r0
    .org 0xbfe14-ORIGIN
L_000bfe14:
    mov.b r0,@(0x3,r15)
    .org 0xbfe16-ORIGIN
L_000bfe16:
    mov #0x12,r0
    .org 0xbfe18-ORIGIN
L_000bfe18:
    mov.l L_000c0020,r2
    .org 0xbfe1a-ORIGIN
L_000bfe1a:
    add r6,r5
    .org 0xbfe1c-ORIGIN
L_000bfe1c:
    mov.b @(r0,r11),r13
    .org 0xbfe1e-ORIGIN
L_000bfe1e:
    stc gbr,r6
    .org 0xbfe20-ORIGIN
L_000bfe20:
    add #0x6c,r6
    .org 0xbfe22-ORIGIN
L_000bfe22:
    jsr @r2
    .org 0xbfe24-ORIGIN
L_000bfe24:
    extu.b r13,r7
    .org 0xbfe26-ORIGIN
L_000bfe26:
    mov.l L_000c0004,r5
    .org 0xbfe28-ORIGIN
L_000bfe28:
    extu.b r0,r13
    .org 0xbfe2a-ORIGIN
L_000bfe2a:
    mov.b @(0x2,r5),r0
    .org 0xbfe2c-ORIGIN
L_000bfe2c:
    tst #0x40,r0
    .org 0xbfe2e-ORIGIN
L_000bfe2e:
    bt/s L_000bfe6a
    .org 0xbfe30-ORIGIN
L_000bfe30:
    mov r13,r6
    .org 0xbfe32-ORIGIN
L_000bfe32:
    mov r14,r0
    .org 0xbfe34-ORIGIN
L_000bfe34:
    mov #-0xc,r2
    .org 0xbfe36-ORIGIN
L_000bfe36:
    stc gbr,r5
    .org 0xbfe38-ORIGIN
L_000bfe38:
    mov.b r0,@(0x3,r15)
    .org 0xbfe3a-ORIGIN
L_000bfe3a:
    mov #0x12,r0
    .org 0xbfe3c-ORIGIN
L_000bfe3c:
    extu.b r2,r12
    .org 0xbfe3e-ORIGIN
L_000bfe3e:
    mov.b @(r0,r11),r14
    .org 0xbfe40-ORIGIN
L_000bfe40:
    stc gbr,r6
    .org 0xbfe42-ORIGIN
L_000bfe42:
    mov.l L_000c0024,r4
    .org 0xbfe44-ORIGIN
L_000bfe44:
    add r12,r5
    .org 0xbfe46-ORIGIN
L_000bfe46:
    add #-0x8,r12
    .org 0xbfe48-ORIGIN
L_000bfe48:
    mov.l L_000c0028,r2
    .org 0xbfe4a-ORIGIN
L_000bfe4a:
    add r12,r6
    .org 0xbfe4c-ORIGIN
L_000bfe4c:
    jsr @r2
    .org 0xbfe4e-ORIGIN
L_000bfe4e:
    extu.b r14,r7
    .org 0xbfe50-ORIGIN
L_000bfe50:
    extu.b r0,r2
    .org 0xbfe52-ORIGIN
L_000bfe52:
    sub r2,r13
    .org 0xbfe54-ORIGIN
L_000bfe54:
    add #-0x6c,r12
    .org 0xbfe56-ORIGIN
L_000bfe56:
    add r12,r13
    .org 0xbfe58-ORIGIN
L_000bfe58:
    cmp/pz r13
    .org 0xbfe5a-ORIGIN
L_000bfe5a:
    bt/s L_000bfe60
    .org 0xbfe5c-ORIGIN
L_000bfe5c:
    mov r13,r6
    .org 0xbfe5e-ORIGIN
L_000bfe5e:
    mov #0x0,r6
    .org 0xbfe60-ORIGIN
L_000bfe60:
    mov #-0x1,r14
    .org 0xbfe62-ORIGIN
L_000bfe62:
    extu.b r14,r14
    .org 0xbfe64-ORIGIN
L_000bfe64:
    cmp/gt r14,r6
    .org 0xbfe66-ORIGIN
L_000bfe66:
    bf L_000bfe6a
    .org 0xbfe68-ORIGIN
L_000bfe68:
    mov r14,r6
    .org 0xbfe6a-ORIGIN
L_000bfe6a:
    mov.w L_000bfe86,r0
    .org 0xbfe6c-ORIGIN
L_000bfe6c:
    mov.b r6,@(r0,r10)
    .org 0xbfe6e-ORIGIN
L_000bfe6e:
    add #0x4,r15
    .org 0xbfe70-ORIGIN
L_000bfe70:
    ldc.l @r15+,gbr
    .org 0xbfe72-ORIGIN
L_000bfe72:
    lds.l @r15+,pr
    .org 0xbfe74-ORIGIN
L_000bfe74:
    mov.l @r15+,r14
    .org 0xbfe76-ORIGIN
L_000bfe76:
    mov.l @r15+,r13
    .org 0xbfe78-ORIGIN
L_000bfe78:
    mov.l @r15+,r12
    .org 0xbfe7a-ORIGIN
L_000bfe7a:
    mov.l @r15+,r11
    .org 0xbfe7c-ORIGIN
L_000bfe7c:
    rts
    .org 0xbfe7e-ORIGIN
L_000bfe7e:
    mov.l @r15+,r10
    .org 0xbfe84-ORIGIN
L_000bfe84:
    .word 0x09d3
    .org 0xbfe86-ORIGIN
L_000bfe86:
    .word 0x09d1
    .org 0xbfff8-ORIGIN
L_000bfff8:
    .long 0xffff128c
    .org 0xc0000-ORIGIN
L_000c0000:
    .long 0x00012ea2
    .org 0xc0004-ORIGIN
L_000c0004:
    .long 0xffff2464
    .org 0xc0008-ORIGIN
L_000c0008:
    .long 0xffff5773
    .org 0xc000c-ORIGIN
L_000c000c:
    .long 0xffff102c
    .org 0xc0010-ORIGIN
L_000c0010:
    .long 0xffff119c
    .org 0xc0014-ORIGIN
L_000c0014:
    .long 0x0000b2fa
    .org 0xc0018-ORIGIN
L_000c0018:
    .long 0x00026140
    .org 0xc001c-ORIGIN
L_000c001c:
    .long 0x0000b33a
    .org 0xc0020-ORIGIN
L_000c0020:
    .long 0x000261b8
    .org 0xc0024-ORIGIN
L_000c0024:
    .long 0x0000ab4a
    .org 0xc0028-ORIGIN
L_000c0028:
    .long 0x00026084
