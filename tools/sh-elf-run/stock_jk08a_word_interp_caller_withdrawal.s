! Exact constant-root word surface/curve callers with real helpers and one shared curve-word union.
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
    .org 0x26714-ORIGIN
L_00026714:
    sts.l pr,@-r15
    .org 0x26716-ORIGIN
L_00026716:
    mov.l r4,@-r15
    .org 0x26718-ORIGIN
L_00026718:
    mov r5,r0
    .org 0x2671a-ORIGIN
L_0002671a:
    extu.w r6,r5
    .org 0x2671c-ORIGIN
L_0002671c:
    mov.l P_0002673c,r7
    .org 0x2671e-ORIGIN
L_0002671e:
    jsr @r7
    .org 0x26720-ORIGIN
L_00026720:
    mov #0x3e,r4
    .org 0x26722-ORIGIN
L_00026722:
    mov.l @r15+,r6
    .org 0x26724-ORIGIN
L_00026724:
    add r4,r6
    .org 0x26726-ORIGIN
L_00026726:
    mov.w @(0x2,r6),r0
    .org 0x26728-ORIGIN
L_00026728:
    extu.w r0,r2
    .org 0x2672a-ORIGIN
L_0002672a:
    mov r5,r3
    .org 0x2672c-ORIGIN
L_0002672c:
    mov.w @r6,r1
    .org 0x2672e-ORIGIN
L_0002672e:
    lds.l @r15+,pr
    .org 0x26730-ORIGIN
L_00026730:
    mov.l P_00026738,r6
    .org 0x26732-ORIGIN
L_00026732:
    jmp @r6
    .org 0x26734-ORIGIN
L_00026734:
    extu.w r1,r0
    .org 0x26738-ORIGIN
P_00026738:
    .byte 0x00
    .org 0x26739-ORIGIN
P_00026739:
    .byte 0x02
    .org 0x2673a-ORIGIN
P_0002673a:
    .byte 0x6a
    .org 0x2673b-ORIGIN
P_0002673b:
    .byte 0xf8
    .org 0x2673c-ORIGIN
P_0002673c:
    .byte 0x00
    .org 0x2673d-ORIGIN
P_0002673d:
    .byte 0x02
    .org 0x2673e-ORIGIN
P_0002673e:
    .byte 0x6b
    .org 0x2673f-ORIGIN
P_0002673f:
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
    .org 0x72f1e-ORIGIN
L_00072f1e:
    sts.l pr,@-r15
    .org 0x72f20-ORIGIN
L_00072f20:
    mov.l P_00073020,r5
    .org 0x72f22-ORIGIN
L_00072f22:
    mov #0x3e,r0
    .org 0x72f24-ORIGIN
L_00072f24:
    mov.l P_00073014,r7
    .org 0x72f26-ORIGIN
L_00072f26:
    mov.w @(r0,r5),r2
    .org 0x72f28-ORIGIN
L_00072f28:
    mov.w P_00073002,r0
    .org 0x72f2a-ORIGIN
L_00072f2a:
    extu.w r2,r2
    .org 0x72f2c-ORIGIN
L_00072f2c:
    mov.l @(r0,r7),r6
    .org 0x72f2e-ORIGIN
L_00072f2e:
    cmp/hi r2,r6
    .org 0x72f30-ORIGIN
L_00072f30:
    bt L_00072f4e
    .org 0x72f32-ORIGIN
L_00072f32:
    mov #-0x1,r4
    .org 0x72f34-ORIGIN
L_00072f34:
    extu.w r4,r4
    .org 0x72f36-ORIGIN
L_00072f36:
    cmp/hi r4,r6
    .org 0x72f38-ORIGIN
L_00072f38:
    bf L_00072f3c
    .org 0x72f3a-ORIGIN
L_00072f3a:
    mov r4,r6
    .org 0x72f3c-ORIGIN
L_00072f3c:
    mov.l P_00073024,r4
    .org 0x72f3e-ORIGIN
L_00072f3e:
    mov.l P_00073028,r2
    .org 0x72f40-ORIGIN
L_00072f40:
    jsr @r2
    .org 0x72f42-ORIGIN
L_00072f42:
    extu.w r6,r6
    .org 0x72f44-ORIGIN
L_00072f44:
    mov r0,r2
    .org 0x72f46-ORIGIN
L_00072f46:
    mov.l P_00073014,r7
    .org 0x72f48-ORIGIN
L_00072f48:
    mov.w P_00073004,r0
    .org 0x72f4a-ORIGIN
L_00072f4a:
    bra L_00072f6e
    .org 0x72f4c-ORIGIN
L_00072f4c:
    mov.w r2,@(r0,r7)
    .org 0x72f4e-ORIGIN
L_00072f4e:
    shlr2 r6
    .org 0x72f50-ORIGIN
L_00072f50:
    mov #-0x1,r4
    .org 0x72f52-ORIGIN
L_00072f52:
    shlr2 r6
    .org 0x72f54-ORIGIN
L_00072f54:
    extu.w r4,r4
    .org 0x72f56-ORIGIN
L_00072f56:
    cmp/hi r4,r6
    .org 0x72f58-ORIGIN
L_00072f58:
    bf L_00072f5c
    .org 0x72f5a-ORIGIN
L_00072f5a:
    mov r4,r6
    .org 0x72f5c-ORIGIN
L_00072f5c:
    mov.l P_0007302c,r4
    .org 0x72f5e-ORIGIN
L_00072f5e:
    mov.l P_00073030,r5
    .org 0x72f60-ORIGIN
L_00072f60:
    mov.l P_00073028,r2
    .org 0x72f62-ORIGIN
L_00072f62:
    jsr @r2
    .org 0x72f64-ORIGIN
L_00072f64:
    extu.w r6,r6
    .org 0x72f66-ORIGIN
L_00072f66:
    mov r0,r6
    .org 0x72f68-ORIGIN
L_00072f68:
    mov.l P_00073014,r7
    .org 0x72f6a-ORIGIN
L_00072f6a:
    mov.w P_00073004,r0
    .org 0x72f6c-ORIGIN
L_00072f6c:
    mov.w r6,@(r0,r7)
    .org 0x72f6e-ORIGIN
L_00072f6e:
    lds.l @r15+,pr
    .org 0x72f70-ORIGIN
L_00072f70:
    rts
    .org 0x72f72-ORIGIN
L_00072f72:
    nop
    .org 0x73002-ORIGIN
P_00073002:
    .byte 0x0a
    .org 0x73003-ORIGIN
P_00073003:
    .byte 0x7c
    .org 0x73004-ORIGIN
P_00073004:
    .byte 0x0a
    .org 0x73005-ORIGIN
P_00073005:
    .byte 0x86
    .org 0x73014-ORIGIN
P_00073014:
    .byte 0xff
    .org 0x73015-ORIGIN
P_00073015:
    .byte 0xff
    .org 0x73016-ORIGIN
P_00073016:
    .byte 0x12
    .org 0x73017-ORIGIN
P_00073017:
    .byte 0x8c
    .org 0x73020-ORIGIN
P_00073020:
    .byte 0x00
    .org 0x73021-ORIGIN
P_00073021:
    .byte 0x01
    .org 0x73022-ORIGIN
P_00073022:
    .byte 0x8e
    .org 0x73023-ORIGIN
P_00073023:
    .byte 0x86
    .org 0x73024-ORIGIN
P_00073024:
    .byte 0x00
    .org 0x73025-ORIGIN
P_00073025:
    .byte 0x01
    .org 0x73026-ORIGIN
P_00073026:
    .byte 0x8f
    .org 0x73027-ORIGIN
P_00073027:
    .byte 0xd6
    .org 0x73028-ORIGIN
P_00073028:
    .byte 0x00
    .org 0x73029-ORIGIN
P_00073029:
    .byte 0x02
    .org 0x7302a-ORIGIN
P_0007302a:
    .byte 0x67
    .org 0x7302b-ORIGIN
P_0007302b:
    .byte 0x14
    .org 0x7302c-ORIGIN
P_0007302c:
    .byte 0x00
    .org 0x7302d-ORIGIN
P_0007302d:
    .byte 0x01
    .org 0x7302e-ORIGIN
P_0007302e:
    .byte 0x8f
    .org 0x7302f-ORIGIN
P_0007302f:
    .byte 0x96
    .org 0x73030-ORIGIN
P_00073030:
    .byte 0x00
    .org 0x73031-ORIGIN
P_00073031:
    .byte 0x01
    .org 0x73032-ORIGIN
P_00073032:
    .byte 0x8e
    .org 0x73033-ORIGIN
P_00073033:
    .byte 0x46
    .org 0xb7b98-ORIGIN
L_000b7b98:
    mov.l r13,@-r15
    .org 0xb7b9a-ORIGIN
L_000b7b9a:
    mov.l r14,@-r15
    .org 0xb7b9c-ORIGIN
L_000b7b9c:
    sts.l pr,@-r15
    .org 0xb7b9e-ORIGIN
L_000b7b9e:
    sts.l macl,@-r15
    .org 0xb7ba0-ORIGIN
L_000b7ba0:
    add #-0x4,r15
    .org 0xb7ba2-ORIGIN
L_000b7ba2:
    mov r5,r14
    .org 0xb7ba4-ORIGIN
L_000b7ba4:
    mov r6,r2
    .org 0xb7ba6-ORIGIN
L_000b7ba6:
    mov.l P_000b7c40,r5
    .org 0xb7ba8-ORIGIN
L_000b7ba8:
    mov r4,r0
    .org 0xb7baa-ORIGIN
L_000b7baa:
    mov.l P_000b7c44,r6
    .org 0xb7bac-ORIGIN
L_000b7bac:
    mov r7,r13
    .org 0xb7bae-ORIGIN
L_000b7bae:
    mov.l P_000b7c48,r4
    .org 0xb7bb0-ORIGIN
L_000b7bb0:
    extu.w r2,r7
    .org 0xb7bb2-ORIGIN
L_000b7bb2:
    mov.l P_000b7c4c,r3
    .org 0xb7bb4-ORIGIN
L_000b7bb4:
    extu.b r14,r14
    .org 0xb7bb6-ORIGIN
L_000b7bb6:
    jsr @r3
    .org 0xb7bb8-ORIGIN
L_000b7bb8:
    mov.w r0,@(0x2,r15)
    .org 0xb7bba-ORIGIN
L_000b7bba:
    tst r14,r14
    .org 0xb7bbc-ORIGIN
L_000b7bbc:
    bt/s L_000b7bc4
    .org 0xb7bbe-ORIGIN
L_000b7bbe:
    mov r0,r2
    .org 0xb7bc0-ORIGIN
L_000b7bc0:
    bra L_000b7bcc
    .org 0xb7bc2-ORIGIN
L_000b7bc2:
    mov #0x0,r2
    .org 0xb7bc4-ORIGIN
L_000b7bc4:
    extu.b r13,r13
    .org 0xb7bc6-ORIGIN
L_000b7bc6:
    extu.w r2,r2
    .org 0xb7bc8-ORIGIN
L_000b7bc8:
    mul.l r2,r13
    .org 0xb7bca-ORIGIN
L_000b7bca:
    sts macl,r2
    .org 0xb7bcc-ORIGIN
L_000b7bcc:
    mov.l P_000b7c18,r5
    .org 0xb7bce-ORIGIN
L_000b7bce:
    mov.w P_000b7bf6,r0
    .org 0xb7bd0-ORIGIN
L_000b7bd0:
    mov.l r2,@(r0,r5)
    .org 0xb7bd2-ORIGIN
L_000b7bd2:
    add #0x4,r15
    .org 0xb7bd4-ORIGIN
L_000b7bd4:
    lds.l @r15+,macl
    .org 0xb7bd6-ORIGIN
L_000b7bd6:
    lds.l @r15+,pr
    .org 0xb7bd8-ORIGIN
L_000b7bd8:
    mov.l @r15+,r14
    .org 0xb7bda-ORIGIN
L_000b7bda:
    rts
    .org 0xb7bdc-ORIGIN
L_000b7bdc:
    mov.l @r15+,r13
    .org 0xb7bf6-ORIGIN
P_000b7bf6:
    .byte 0x04
    .org 0xb7bf7-ORIGIN
P_000b7bf7:
    .byte 0x0c
    .org 0xb7c18-ORIGIN
P_000b7c18:
    .byte 0xff
    .org 0xb7c19-ORIGIN
P_000b7c19:
    .byte 0xff
    .org 0xb7c1a-ORIGIN
P_000b7c1a:
    .byte 0x28
    .org 0xb7c1b-ORIGIN
P_000b7c1b:
    .byte 0xf8
    .org 0xb7c40-ORIGIN
P_000b7c40:
    .byte 0x00
    .org 0xb7c41-ORIGIN
P_000b7c41:
    .byte 0x01
    .org 0xb7c42-ORIGIN
P_000b7c42:
    .byte 0x3d
    .org 0xb7c43-ORIGIN
P_000b7c43:
    .byte 0x74
    .org 0xb7c44-ORIGIN
P_000b7c44:
    .byte 0x00
    .org 0xb7c45-ORIGIN
P_000b7c45:
    .byte 0x01
    .org 0xb7c46-ORIGIN
P_000b7c46:
    .byte 0x3d
    .org 0xb7c47-ORIGIN
P_000b7c47:
    .byte 0xb4
    .org 0xb7c48-ORIGIN
P_000b7c48:
    .byte 0x00
    .org 0xb7c49-ORIGIN
P_000b7c49:
    .byte 0x00
    .org 0xb7c4a-ORIGIN
P_000b7c4a:
    .byte 0xd4
    .org 0xb7c4b-ORIGIN
P_000b7c4b:
    .byte 0x0e
    .org 0xb7c4c-ORIGIN
P_000b7c4c:
    .byte 0x00
    .org 0xb7c4d-ORIGIN
P_000b7c4d:
    .byte 0x02
    .org 0xb7c4e-ORIGIN
P_000b7c4e:
    .byte 0x62
    .org 0xb7c4f-ORIGIN
P_000b7c4f:
    .byte 0xa8
