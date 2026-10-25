! Complete stock ROM-gated signed endpoint evaluators, real weight update and blend caller.
    .text
    .balign 4
    .set ORIGIN,0x262a8
    .org 0x262a8-ORIGIN
L_000262a8:
    sts.l pr,@-r15
    .org 0x262aa-ORIGIN
L_000262aa:
    mov.l r4,@-r15
    .org 0x262ac-ORIGIN
L_000262ac:
    extu.w r7,r7
    .org 0x262ae-ORIGIN
L_000262ae:
    mov r5,r0
    .org 0x262b0-ORIGIN
L_000262b0:
    mov r7,r5
    .org 0x262b2-ORIGIN
L_000262b2:
    mov.l P_000262dc,r7
    .org 0x262b4-ORIGIN
L_000262b4:
    jsr @r7
    .org 0x262b6-ORIGIN
L_000262b6:
    mov #0x1e,r4
    .org 0x262b8-ORIGIN
L_000262b8:
    mov.l r5,@-r15
    .org 0x262ba-ORIGIN
L_000262ba:
    mov.l r4,@-r15
    .org 0x262bc-ORIGIN
L_000262bc:
    mov r6,r0
    .org 0x262be-ORIGIN
L_000262be:
    mov.l @(0x10,r15),r5
    .org 0x262c0-ORIGIN
L_000262c0:
    extu.w r5,r5
    .org 0x262c2-ORIGIN
L_000262c2:
    jsr @r7
    .org 0x262c4-ORIGIN
L_000262c4:
    mov #0x1e,r4
    .org 0x262c6-ORIGIN
L_000262c6:
    mov.l @r15+,r0
    .org 0x262c8-ORIGIN
L_000262c8:
    mov.l @r15+,r1
    .org 0x262ca-ORIGIN
L_000262ca:
    mov r4,r2
    .org 0x262cc-ORIGIN
L_000262cc:
    mov r5,r3
    .org 0x262ce-ORIGIN
L_000262ce:
    mov.l @r15+,r4
    .org 0x262d0-ORIGIN
L_000262d0:
    lds.l @r15+,pr
    .org 0x262d2-ORIGIN
L_000262d2:
    mov.l P_000262d8,r7
    .org 0x262d4-ORIGIN
L_000262d4:
    jmp @r7
    .org 0x262d6-ORIGIN
L_000262d6:
    mov #0x10,r5
    .org 0x262d8-ORIGIN
P_000262d8:
    .byte 0x00
    .org 0x262d9-ORIGIN
P_000262d9:
    .byte 0x02
    .org 0x262da-ORIGIN
P_000262da:
    .byte 0x68
    .org 0x262db-ORIGIN
P_000262db:
    .byte 0x48
    .org 0x262dc-ORIGIN
P_000262dc:
    .byte 0x00
    .org 0x262dd-ORIGIN
P_000262dd:
    .byte 0x02
    .org 0x262de-ORIGIN
P_000262de:
    .byte 0x69
    .org 0x262df-ORIGIN
P_000262df:
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
    .org 0x7604c-ORIGIN
L_0007604c:
    mov.l r9,@-r15
    .org 0x7604e-ORIGIN
L_0007604e:
    mov.l r10,@-r15
    .org 0x76050-ORIGIN
L_00076050:
    mov.l r11,@-r15
    .org 0x76052-ORIGIN
L_00076052:
    mov.l r12,@-r15
    .org 0x76054-ORIGIN
L_00076054:
    mov.l r13,@-r15
    .org 0x76056-ORIGIN
L_00076056:
    mov.l r14,@-r15
    .org 0x76058-ORIGIN
L_00076058:
    sts.l pr,@-r15
    .org 0x7605a-ORIGIN
L_0007605a:
    stc.l gbr,@-r15
    .org 0x7605c-ORIGIN
L_0007605c:
    mov.l P_00076178,r0
    .org 0x7605e-ORIGIN
L_0007605e:
    ldc r0,gbr
    .org 0x76060-ORIGIN
L_00076060:
    add #-0x4,r15
    .org 0x76062-ORIGIN
L_00076062:
    mov.l P_0007617c,r6
    .org 0x76064-ORIGIN
L_00076064:
    mov.b @(0x9,r6),r0
    .org 0x76066-ORIGIN
L_00076066:
    tst #0x80,r0
    .org 0x76068-ORIGIN
L_00076068:
    bt/s L_0007607c
    .org 0x7606a-ORIGIN
L_0007606a:
    mov.w @(0x3e,gbr),r0
    .org 0x7606c-ORIGIN
L_0007606c:
    extu.w r0,r4
    .org 0x7606e-ORIGIN
L_0007606e:
    mov.w @(0x4e,gbr),r0
    .org 0x76070-ORIGIN
L_00076070:
    extu.w r0,r2
    .org 0x76072-ORIGIN
L_00076072:
    cmp/ge r2,r4
    .org 0x76074-ORIGIN
L_00076074:
    bf L_00076078
    .org 0x76076-ORIGIN
L_00076076:
    mov r4,r2
    .org 0x76078-ORIGIN
L_00076078:
    bra L_0007607e
    .org 0x7607a-ORIGIN
L_0007607a:
    mov r2,r13
    .org 0x7607c-ORIGIN
L_0007607c:
    mov r0,r13
    .org 0x7607e-ORIGIN
L_0007607e:
    mov r13,r0
    .org 0x76080-ORIGIN
L_00076080:
    mov.w r0,@(0x2,r15)
    .org 0x76082-ORIGIN
L_00076082:
    mov.w @(0x17c,gbr),r0
    .org 0x76084-ORIGIN
L_00076084:
    mov #-0x80,r14
    .org 0x76086-ORIGIN
L_00076086:
    mov.l P_00076180,r4
    .org 0x76088-ORIGIN
L_00076088:
    shll8 r14
    .org 0x7608a-ORIGIN
L_0007608a:
    mov.l P_00076184,r10
    .org 0x7608c-ORIGIN
L_0007608c:
    extu.w r0,r7
    .org 0x7608e-ORIGIN
L_0007608e:
    mov.l P_00076188,r11
    .org 0x76090-ORIGIN
L_00076090:
    mov.l P_0007618c,r12
    .org 0x76092-ORIGIN
L_00076092:
    mov r10,r5
    .org 0x76094-ORIGIN
L_00076094:
    mov.l P_00076190,r9
    .org 0x76096-ORIGIN
L_00076096:
    jsr @r12
    .org 0x76098-ORIGIN
L_00076098:
    mov r11,r6
    .org 0x7609a-ORIGIN
L_0007609a:
    extu.w r0,r2
    .org 0x7609c-ORIGIN
L_0007609c:
    mov.w P_00076172,r0
    .org 0x7609e-ORIGIN
L_0007609e:
    exts.w r2,r2
    .org 0x760a0-ORIGIN
L_000760a0:
    mov.l P_00076194,r4
    .org 0x760a2-ORIGIN
L_000760a2:
    add r14,r2
    .org 0x760a4-ORIGIN
L_000760a4:
    mov r10,r5
    .org 0x760a6-ORIGIN
L_000760a6:
    mov.w r2,@(r0,r9)
    .org 0x760a8-ORIGIN
L_000760a8:
    mov r13,r0
    .org 0x760aa-ORIGIN
L_000760aa:
    mov.w r0,@(0x2,r15)
    .org 0x760ac-ORIGIN
L_000760ac:
    mov r11,r6
    .org 0x760ae-ORIGIN
L_000760ae:
    mov.w @(0x17c,gbr),r0
    .org 0x760b0-ORIGIN
L_000760b0:
    jsr @r12
    .org 0x760b2-ORIGIN
L_000760b2:
    extu.w r0,r7
    .org 0x760b4-ORIGIN
L_000760b4:
    extu.w r0,r2
    .org 0x760b6-ORIGIN
L_000760b6:
    mov.w P_00076174,r0
    .org 0x760b8-ORIGIN
L_000760b8:
    exts.w r2,r2
    .org 0x760ba-ORIGIN
L_000760ba:
    add r14,r2
    .org 0x760bc-ORIGIN
L_000760bc:
    mov.w r2,@(r0,r9)
    .org 0x760be-ORIGIN
L_000760be:
    add #0x4,r15
    .org 0x760c0-ORIGIN
L_000760c0:
    ldc.l @r15+,gbr
    .org 0x760c2-ORIGIN
L_000760c2:
    lds.l @r15+,pr
    .org 0x760c4-ORIGIN
L_000760c4:
    mov.l @r15+,r14
    .org 0x760c6-ORIGIN
L_000760c6:
    mov.l @r15+,r13
    .org 0x760c8-ORIGIN
L_000760c8:
    mov.l @r15+,r12
    .org 0x760ca-ORIGIN
L_000760ca:
    mov.l @r15+,r11
    .org 0x760cc-ORIGIN
L_000760cc:
    mov.l @r15+,r10
    .org 0x760ce-ORIGIN
L_000760ce:
    rts
    .org 0x760d0-ORIGIN
L_000760d0:
    mov.l @r15+,r9
    .org 0x760d2-ORIGIN
L_000760d2:
    stc.l gbr,@-r15
    .org 0x760d4-ORIGIN
L_000760d4:
    mov.l P_00076198,r0
    .org 0x760d6-ORIGIN
L_000760d6:
    ldc r0,gbr
    .org 0x760d8-ORIGIN
L_000760d8:
    mov.b @(0xa0,gbr),r0
    .org 0x760da-ORIGIN
L_000760da:
    mov.l P_0007619c,r5
    .org 0x760dc-ORIGIN
L_000760dc:
    tst #0x4,r0
    .org 0x760de-ORIGIN
L_000760de:
    mov.w @(0x64,gbr),r0
    .org 0x760e0-ORIGIN
L_000760e0:
    mov.w @r5,r6
    .org 0x760e2-ORIGIN
L_000760e2:
    bt/s L_000760f6
    .org 0x760e4-ORIGIN
L_000760e4:
    extu.w r0,r2
    .org 0x760e6-ORIGIN
L_000760e6:
    extu.w r6,r6
    .org 0x760e8-ORIGIN
L_000760e8:
    add r6,r2
    .org 0x760ea-ORIGIN
L_000760ea:
    mov #-0x1,r6
    .org 0x760ec-ORIGIN
L_000760ec:
    extu.w r6,r6
    .org 0x760ee-ORIGIN
L_000760ee:
    cmp/gt r6,r2
    .org 0x760f0-ORIGIN
L_000760f0:
    bf L_00076100
    .org 0x760f2-ORIGIN
L_000760f2:
    bra L_00076100
    .org 0x760f4-ORIGIN
L_000760f4:
    mov r6,r2
    .org 0x760f6-ORIGIN
L_000760f6:
    extu.w r6,r5
    .org 0x760f8-ORIGIN
L_000760f8:
    sub r5,r2
    .org 0x760fa-ORIGIN
L_000760fa:
    cmp/pz r2
    .org 0x760fc-ORIGIN
L_000760fc:
    bt L_00076100
    .org 0x760fe-ORIGIN
L_000760fe:
    mov #0x0,r2
    .org 0x76100-ORIGIN
L_00076100:
    mov r2,r0
    .org 0x76102-ORIGIN
L_00076102:
    mov.w r0,@(0x64,gbr)
    .org 0x76104-ORIGIN
L_00076104:
    rts
    .org 0x76106-ORIGIN
L_00076106:
    ldc.l @r15+,gbr
    .org 0x76108-ORIGIN
L_00076108:
    sts.l pr,@-r15
    .org 0x7610a-ORIGIN
L_0007610a:
    sts.l macl,@-r15
    .org 0x7610c-ORIGIN
L_0007610c:
    mov.l P_000761a0,r6
    .org 0x7610e-ORIGIN
L_0007610e:
    mov.b @r6,r0
    .org 0x76110-ORIGIN
L_00076110:
    tst #0x80,r0
    .org 0x76112-ORIGIN
L_00076112:
    bf L_0007616a
    .org 0x76114-ORIGIN
L_00076114:
    mov.l P_000761a4,r6
    .org 0x76116-ORIGIN
L_00076116:
    mov.b @r6,r0
    .org 0x76118-ORIGIN
L_00076118:
    tst #0x20,r0
    .org 0x7611a-ORIGIN
L_0007611a:
    bt L_0007616a
    .org 0x7611c-ORIGIN
L_0007611c:
    bsr L_0007604c
    .org 0x7611e-ORIGIN
L_0007611e:
    nop
    .org 0x76120-ORIGIN
L_00076120:
    bsr L_000760d2
    .org 0x76122-ORIGIN
L_00076122:
    nop
    .org 0x76124-ORIGIN
L_00076124:
    mov.l P_00076198,r2
    .org 0x76126-ORIGIN
L_00076126:
    mov #0x64,r0
    .org 0x76128-ORIGIN
L_00076128:
    mov.w @(r0,r2),r5
    .org 0x7612a-ORIGIN
L_0007612a:
    extu.w r5,r5
    .org 0x7612c-ORIGIN
L_0007612c:
    tst r5,r5
    .org 0x7612e-ORIGIN
L_0007612e:
    bf L_00076138
    .org 0x76130-ORIGIN
L_00076130:
    mov.l P_00076190,r4
    .org 0x76132-ORIGIN
L_00076132:
    mov.w P_00076172,r0
    .org 0x76134-ORIGIN
L_00076134:
    bra L_00076166
    .org 0x76136-ORIGIN
L_00076136:
    mov.w @(r0,r4),r2
    .org 0x76138-ORIGIN
L_00076138:
    mov #-0x1,r6
    .org 0x7613a-ORIGIN
L_0007613a:
    extu.w r6,r6
    .org 0x7613c-ORIGIN
L_0007613c:
    cmp/eq r6,r5
    .org 0x7613e-ORIGIN
L_0007613e:
    bf L_00076148
    .org 0x76140-ORIGIN
L_00076140:
    mov.l P_00076190,r4
    .org 0x76142-ORIGIN
L_00076142:
    mov.w P_00076174,r0
    .org 0x76144-ORIGIN
L_00076144:
    bra L_00076166
    .org 0x76146-ORIGIN
L_00076146:
    mov.w @(r0,r4),r2
    .org 0x76148-ORIGIN
L_00076148:
    mov.l P_00076190,r4
    .org 0x7614a-ORIGIN
L_0007614a:
    mov #0x1,r2
    .org 0x7614c-ORIGIN
L_0007614c:
    mov.w P_00076172,r0
    .org 0x7614e-ORIGIN
L_0007614e:
    shll16 r2
    .org 0x76150-ORIGIN
L_00076150:
    sub r5,r2
    .org 0x76152-ORIGIN
L_00076152:
    mov.w @(r0,r4),r6
    .org 0x76154-ORIGIN
L_00076154:
    mov.w P_00076174,r0
    .org 0x76156-ORIGIN
L_00076156:
    mul.l r6,r2
    .org 0x76158-ORIGIN
L_00076158:
    mov.w @(r0,r4),r2
    .org 0x7615a-ORIGIN
L_0007615a:
    sts macl,r6
    .org 0x7615c-ORIGIN
L_0007615c:
    mul.l r2,r5
    .org 0x7615e-ORIGIN
L_0007615e:
    sts macl,r2
    .org 0x76160-ORIGIN
L_00076160:
    add r2,r6
    .org 0x76162-ORIGIN
L_00076162:
    swap.w r6,r2
    .org 0x76164-ORIGIN
L_00076164:
    exts.w r2,r2
    .org 0x76166-ORIGIN
L_00076166:
    mov.w P_00076176,r0
    .org 0x76168-ORIGIN
L_00076168:
    mov.w r2,@(r0,r4)
    .org 0x7616a-ORIGIN
L_0007616a:
    lds.l @r15+,macl
    .org 0x7616c-ORIGIN
L_0007616c:
    lds.l @r15+,pr
    .org 0x7616e-ORIGIN
L_0007616e:
    rts
    .org 0x76170-ORIGIN
L_00076170:
    nop
    .org 0x76172-ORIGIN
P_00076172:
    .byte 0x06
    .org 0x76173-ORIGIN
P_00076173:
    .byte 0x60
    .org 0x76174-ORIGIN
P_00076174:
    .byte 0x06
    .org 0x76175-ORIGIN
P_00076175:
    .byte 0x62
    .org 0x76176-ORIGIN
P_00076176:
    .byte 0x06
    .org 0x76177-ORIGIN
P_00076177:
    .byte 0x5a
    .org 0x76178-ORIGIN
P_00076178:
    .byte 0xff
    .org 0x76179-ORIGIN
P_00076179:
    .byte 0xff
    .org 0x7617a-ORIGIN
P_0007617a:
    .byte 0x10
    .org 0x7617b-ORIGIN
P_0007617b:
    .byte 0x94
    .org 0x7617c-ORIGIN
P_0007617c:
    .byte 0xff
    .org 0x7617d-ORIGIN
P_0007617d:
    .byte 0xff
    .org 0x7617e-ORIGIN
P_0007617e:
    .byte 0x42
    .org 0x7617f-ORIGIN
P_0007617f:
    .byte 0x4c
    .org 0x76180-ORIGIN
P_00076180:
    .byte 0x00
    .org 0x76181-ORIGIN
P_00076181:
    .byte 0x00
    .org 0x76182-ORIGIN
P_00076182:
    .byte 0xde
    .org 0x76183-ORIGIN
P_00076183:
    .byte 0x8e
    .org 0x76184-ORIGIN
P_00076184:
    .byte 0x00
    .org 0x76185-ORIGIN
P_00076185:
    .byte 0x01
    .org 0x76186-ORIGIN
P_00076186:
    .byte 0x3d
    .org 0x76187-ORIGIN
P_00076187:
    .byte 0x14
    .org 0x76188-ORIGIN
P_00076188:
    .byte 0x00
    .org 0x76189-ORIGIN
P_00076189:
    .byte 0x01
    .org 0x7618a-ORIGIN
P_0007618a:
    .byte 0x3d
    .org 0x7618b-ORIGIN
P_0007618b:
    .byte 0x34
    .org 0x7618c-ORIGIN
P_0007618c:
    .byte 0x00
    .org 0x7618d-ORIGIN
P_0007618d:
    .byte 0x02
    .org 0x7618e-ORIGIN
P_0007618e:
    .byte 0x62
    .org 0x7618f-ORIGIN
P_0007618f:
    .byte 0xa8
    .org 0x76190-ORIGIN
P_00076190:
    .byte 0xff
    .org 0x76191-ORIGIN
P_00076191:
    .byte 0xff
    .org 0x76192-ORIGIN
P_00076192:
    .byte 0x12
    .org 0x76193-ORIGIN
P_00076193:
    .byte 0x8c
    .org 0x76194-ORIGIN
P_00076194:
    .byte 0x00
    .org 0x76195-ORIGIN
P_00076195:
    .byte 0x00
    .org 0x76196-ORIGIN
P_00076196:
    .byte 0xe0
    .org 0x76197-ORIGIN
P_00076197:
    .byte 0x8e
    .org 0x76198-ORIGIN
P_00076198:
    .byte 0xff
    .org 0x76199-ORIGIN
P_00076199:
    .byte 0xff
    .org 0x7619a-ORIGIN
P_0007619a:
    .byte 0x23
    .org 0x7619b-ORIGIN
P_0007619b:
    .byte 0xbc
    .org 0x7619c-ORIGIN
P_0007619c:
    .byte 0x00
    .org 0x7619d-ORIGIN
P_0007619d:
    .byte 0x00
    .org 0x7619e-ORIGIN
P_0007619e:
    .byte 0x90
    .org 0x7619f-ORIGIN
P_0007619f:
    .byte 0xa0
    .org 0x761a0-ORIGIN
P_000761a0:
    .byte 0x00
    .org 0x761a1-ORIGIN
P_000761a1:
    .byte 0x00
    .org 0x761a2-ORIGIN
P_000761a2:
    .byte 0x8b
    .org 0x761a3-ORIGIN
P_000761a3:
    .byte 0x3f
    .org 0x761a4-ORIGIN
P_000761a4:
    .byte 0x00
    .org 0x761a5-ORIGIN
P_000761a5:
    .byte 0x00
    .org 0x761a6-ORIGIN
P_000761a6:
    .byte 0x89
    .org 0x761a7-ORIGIN
P_000761a7:
    .byte 0xfa
