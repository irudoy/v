! Exact natural RAM product, truncation, carry and saturation leaves.
    .text
    .balign 4
    .set ORIGIN,0x8b40
    .org 0x8b40-ORIGIN
P_00008b40:
    .byte 0x00
    .org 0x8bbe-ORIGIN
P_00008bbe:
    .byte 0x59
    .org 0x5279c-ORIGIN
L_0005279c:
    sts.l macl,@-r15
    .org 0x5279e-ORIGIN
L_0005279e:
    stc.l gbr,@-r15
    .org 0x527a0-ORIGIN
L_000527a0:
    mov.l P_00052964,r0
    .org 0x527a2-ORIGIN
L_000527a2:
    ldc r0,gbr
    .org 0x527a4-ORIGIN
L_000527a4:
    mov.l P_00052968,r5
    .org 0x527a6-ORIGIN
L_000527a6:
    mov.b @r5,r0
    .org 0x527a8-ORIGIN
L_000527a8:
    tst #0x40,r0
    .org 0x527aa-ORIGIN
L_000527aa:
    bf/s L_000527fc
    .org 0x527ac-ORIGIN
L_000527ac:
    mov #0x0,r6
    .org 0x527ae-ORIGIN
L_000527ae:
    mov.l P_00052964,r4
    .org 0x527b0-ORIGIN
L_000527b0:
    mov.w P_000528f6,r0
    .org 0x527b2-ORIGIN
L_000527b2:
    mov.w @(r0,r4),r6
    .org 0x527b4-ORIGIN
L_000527b4:
    mov.l @(0x3b4,gbr),r0
    .org 0x527b6-ORIGIN
L_000527b6:
    extu.w r6,r2
    .org 0x527b8-ORIGIN
L_000527b8:
    shll 8 r2
    .org 0x527ba-ORIGIN
L_000527ba:
    sub r0,r2
    .org 0x527bc-ORIGIN
L_000527bc:
    mov.w P_000528f8,r0
    .org 0x527be-ORIGIN
L_000527be:
    cmp/pz r2
    .org 0x527c0-ORIGIN
L_000527c0:
    mov.b @(r0,r4),r5
    .org 0x527c2-ORIGIN
L_000527c2:
    bt/s L_000527cc
    .org 0x527c4-ORIGIN
L_000527c4:
    extu.b r5,r5
    .org 0x527c6-ORIGIN
L_000527c6:
    mov #-0x1,r6
    .org 0x527c8-ORIGIN
L_000527c8:
    extu.b r6,r6
    .org 0x527ca-ORIGIN
L_000527ca:
    add r6,r2
    .org 0x527cc-ORIGIN
L_000527cc:
    mov r2,r6
    .org 0x527ce-ORIGIN
L_000527ce:
    shlr 8 r6
    .org 0x527d0-ORIGIN
L_000527d0:
    swap.w r6,r2
    .org 0x527d2-ORIGIN
L_000527d2:
    exts.b r2,r6
    .org 0x527d4-ORIGIN
L_000527d4:
    xtrct r6,r2
    .org 0x527d6-ORIGIN
L_000527d6:
    mul.l r2,r5
    .org 0x527d8-ORIGIN
L_000527d8:
    sts macl,r2
    .org 0x527da-ORIGIN
L_000527da:
    cmp/pz r2
    .org 0x527dc-ORIGIN
L_000527dc:
    bt L_000527e0
    .org 0x527de-ORIGIN
L_000527de:
    add #0x1f,r2
    .org 0x527e0-ORIGIN
L_000527e0:
    shar r2
    .org 0x527e2-ORIGIN
L_000527e2:
    mov.w P_000528fa,r6
    .org 0x527e4-ORIGIN
L_000527e4:
    shar r2
    .org 0x527e6-ORIGIN
L_000527e6:
    shar r2
    .org 0x527e8-ORIGIN
L_000527e8:
    shar r2
    .org 0x527ea-ORIGIN
L_000527ea:
    shar r2
    .org 0x527ec-ORIGIN
L_000527ec:
    cmp/gt r6,r2
    .org 0x527ee-ORIGIN
L_000527ee:
    bt L_000527f2
    .org 0x527f0-ORIGIN
L_000527f0:
    mov r2,r6
    .org 0x527f2-ORIGIN
L_000527f2:
    mov #-0x80,r2
    .org 0x527f4-ORIGIN
L_000527f4:
    shll 8 r2
    .org 0x527f6-ORIGIN
L_000527f6:
    cmp/ge r2,r6
    .org 0x527f8-ORIGIN
L_000527f8:
    bt L_000527fc
    .org 0x527fa-ORIGIN
L_000527fa:
    mov r2,r6
    .org 0x527fc-ORIGIN
L_000527fc:
    mov.l P_00052964,r4
    .org 0x527fe-ORIGIN
L_000527fe:
    mov.w P_000528fc,r0
    .org 0x52800-ORIGIN
L_00052800:
    mov.w r6,@(r0,r4)
    .org 0x52802-ORIGIN
L_00052802:
    ldc.l @r15+,gbr
    .org 0x52804-ORIGIN
L_00052804:
    rts
    .org 0x52806-ORIGIN
L_00052806:
    lds.l @r15+,macl
    .org 0x528f6-ORIGIN
P_000528f6:
    .byte 0x03
    .org 0x528f7-ORIGIN
P_000528f7:
    .byte 0xc4
    .org 0x528f8-ORIGIN
P_000528f8:
    .byte 0x03
    .org 0x528f9-ORIGIN
P_000528f9:
    .byte 0x52
    .org 0x528fa-ORIGIN
P_000528fa:
    .byte 0x7f
    .org 0x528fb-ORIGIN
P_000528fb:
    .byte 0xff
    .org 0x528fc-ORIGIN
P_000528fc:
    .byte 0x07
    .org 0x528fd-ORIGIN
P_000528fd:
    .byte 0xda
    .org 0x52902-ORIGIN
L_00052902:
    sts.l macl,@-r15
    .org 0x52904-ORIGIN
L_00052904:
    mov.l P_00052964,r5
    .org 0x52906-ORIGIN
L_00052906:
    mov.w P_0005295e,r0
    .org 0x52908-ORIGIN
L_00052908:
    mov.b @(r0,r5),r2
    .org 0x5290a-ORIGIN
L_0005290a:
    mov.w P_00052960,r0
    .org 0x5290c-ORIGIN
L_0005290c:
    extu.b r2,r2
    .org 0x5290e-ORIGIN
L_0005290e:
    mov.w @(r0,r5),r6
    .org 0x52910-ORIGIN
L_00052910:
    mul.l r6,r2
    .org 0x52912-ORIGIN
L_00052912:
    sts macl,r6
    .org 0x52914-ORIGIN
L_00052914:
    cmp/pz r6
    .org 0x52916-ORIGIN
L_00052916:
    bt L_0005291e
    .org 0x52918-ORIGIN
L_00052918:
    mov #-0x1,r2
    .org 0x5291a-ORIGIN
L_0005291a:
    extu.b r2,r2
    .org 0x5291c-ORIGIN
L_0005291c:
    add r2,r6
    .org 0x5291e-ORIGIN
L_0005291e:
    mov r6,r2
    .org 0x52920-ORIGIN
L_00052920:
    shlr 8 r2
    .org 0x52922-ORIGIN
L_00052922:
    swap.w r2,r6
    .org 0x52924-ORIGIN
L_00052924:
    exts.b r6,r2
    .org 0x52926-ORIGIN
L_00052926:
    xtrct r2,r6
    .org 0x52928-ORIGIN
L_00052928:
    cmp/pz r6
    .org 0x5292a-ORIGIN
L_0005292a:
    bf L_00052938
    .org 0x5292c-ORIGIN
L_0005292c:
    mov.w P_00052962,r2
    .org 0x5292e-ORIGIN
L_0005292e:
    cmp/gt r2,r6
    .org 0x52930-ORIGIN
L_00052930:
    bf L_00052934
    .org 0x52932-ORIGIN
L_00052932:
    mov r2,r6
    .org 0x52934-ORIGIN
L_00052934:
    bra L_00052942
    .org 0x52936-ORIGIN
L_00052936:
    mov r6,r5
    .org 0x52938-ORIGIN
L_00052938:
    mov #-0x80,r5
    .org 0x5293a-ORIGIN
L_0005293a:
    shll 8 r5
    .org 0x5293c-ORIGIN
L_0005293c:
    cmp/ge r5,r6
    .org 0x5293e-ORIGIN
L_0005293e:
    bf L_00052942
    .org 0x52940-ORIGIN
L_00052940:
    mov r6,r5
    .org 0x52942-ORIGIN
L_00052942:
    mov.l P_0005297c,r6
    .org 0x52944-ORIGIN
L_00052944:
    mov.b @(0x1,r6),r0
    .org 0x52946-ORIGIN
L_00052946:
    tst #0x20,r0
    .org 0x52948-ORIGIN
L_00052948:
    bt L_00052954
    .org 0x5294a-ORIGIN
L_0005294a:
    mov.l P_0005298c,r6
    .org 0x5294c-ORIGIN
L_0005294c:
    mov.b @r6,r0
    .org 0x5294e-ORIGIN
L_0005294e:
    tst #0x4,r0
    .org 0x52950-ORIGIN
L_00052950:
    bt L_00052954
    .org 0x52952-ORIGIN
L_00052952:
    mov #0x0,r5
    .org 0x52954-ORIGIN
L_00052954:
    mov.l P_00052990,r6
    .org 0x52956-ORIGIN
L_00052956:
    mov r5,r0
    .org 0x52958-ORIGIN
L_00052958:
    mov.w r0,@(0x8,r6)
    .org 0x5295a-ORIGIN
L_0005295a:
    rts
    .org 0x5295c-ORIGIN
L_0005295c:
    lds.l @r15+,macl
    .org 0x5295e-ORIGIN
P_0005295e:
    .byte 0x02
    .org 0x5295f-ORIGIN
P_0005295f:
    .byte 0x7e
    .org 0x52960-ORIGIN
P_00052960:
    .byte 0x07
    .org 0x52961-ORIGIN
P_00052961:
    .byte 0xda
    .org 0x52962-ORIGIN
P_00052962:
    .byte 0x7f
    .org 0x52963-ORIGIN
P_00052963:
    .byte 0xff
    .org 0x52964-ORIGIN
P_00052964:
    .byte 0xff
    .org 0x52965-ORIGIN
P_00052965:
    .byte 0xff
    .org 0x52966-ORIGIN
P_00052966:
    .byte 0x12
    .org 0x52967-ORIGIN
P_00052967:
    .byte 0x8c
    .org 0x52968-ORIGIN
P_00052968:
    .byte 0xff
    .org 0x52969-ORIGIN
P_00052969:
    .byte 0xff
    .org 0x5296a-ORIGIN
P_0005296a:
    .byte 0x41
    .org 0x5296b-ORIGIN
P_0005296b:
    .byte 0x84
    .org 0x5297c-ORIGIN
P_0005297c:
    .byte 0xff
    .org 0x5297d-ORIGIN
P_0005297d:
    .byte 0xff
    .org 0x5297e-ORIGIN
P_0005297e:
    .byte 0x24
    .org 0x5297f-ORIGIN
P_0005297f:
    .byte 0x5c
    .org 0x5298c-ORIGIN
P_0005298c:
    .byte 0x00
    .org 0x5298d-ORIGIN
P_0005298d:
    .byte 0x00
    .org 0x5298e-ORIGIN
P_0005298e:
    .byte 0x8b
    .org 0x5298f-ORIGIN
P_0005298f:
    .byte 0x40
    .org 0x52990-ORIGIN
P_00052990:
    .byte 0xff
    .org 0x52991-ORIGIN
P_00052991:
    .byte 0xff
    .org 0x52992-ORIGIN
P_00052992:
    .byte 0x22
    .org 0x52993-ORIGIN
P_00052993:
    .byte 0xf8
    .org 0x5444c-ORIGIN
L_0005444c:
    sts.l macl,@-r15
    .org 0x5444e-ORIGIN
L_0005444e:
    mov.l P_000545d4,r6
    .org 0x54450-ORIGIN
L_00054450:
    mov.l P_000545b0,r4
    .org 0x54452-ORIGIN
L_00054452:
    mov.w P_000544d2,r0
    .org 0x54454-ORIGIN
L_00054454:
    mov.b @r6,r2
    .org 0x54456-ORIGIN
L_00054456:
    mov.b @(r0,r4),r6
    .org 0x54458-ORIGIN
L_00054458:
    extu.b r2,r5
    .org 0x5445a-ORIGIN
L_0005445a:
    mov.w P_000544d4,r0
    .org 0x5445c-ORIGIN
L_0005445c:
    extu.b r6,r2
    .org 0x5445e-ORIGIN
L_0005445e:
    mul.l r5,r2
    .org 0x54460-ORIGIN
L_00054460:
    mov.b @(r0,r4),r6
    .org 0x54462-ORIGIN
L_00054462:
    sts macl,r2
    .org 0x54464-ORIGIN
L_00054464:
    extu.b r6,r5
    .org 0x54466-ORIGIN
L_00054466:
    mul.l r2,r5
    .org 0x54468-ORIGIN
L_00054468:
    mov #-0x1,r2
    .org 0x5446a-ORIGIN
L_0005446a:
    extu.b r2,r2
    .org 0x5446c-ORIGIN
L_0005446c:
    sts macl,r6
    .org 0x5446e-ORIGIN
L_0005446e:
    shlr 8 r6
    .org 0x54470-ORIGIN
L_00054470:
    shlr 2 r6
    .org 0x54472-ORIGIN
L_00054472:
    shlr 2 r6
    .org 0x54474-ORIGIN
L_00054474:
    shlr 2 r6
    .org 0x54476-ORIGIN
L_00054476:
    cmp/hi r2,r6
    .org 0x54478-ORIGIN
L_00054478:
    bt L_0005447c
    .org 0x5447a-ORIGIN
L_0005447a:
    mov r6,r2
    .org 0x5447c-ORIGIN
L_0005447c:
    mov.l P_000545cc,r5
    .org 0x5447e-ORIGIN
L_0005447e:
    mov.w P_000544d6,r0
    .org 0x54480-ORIGIN
L_00054480:
    mov.w @r5,r6
    .org 0x54482-ORIGIN
L_00054482:
    mov.b r2,@(r0,r4)
    .org 0x54484-ORIGIN
L_00054484:
    extu.b r2,r2
    .org 0x54486-ORIGIN
L_00054486:
    extu.w r6,r6
    .org 0x54488-ORIGIN
L_00054488:
    mul.l r6,r2
    .org 0x5448a-ORIGIN
L_0005448a:
    sts macl,r2
    .org 0x5448c-ORIGIN
L_0005448c:
    cmp/pz r2
    .org 0x5448e-ORIGIN
L_0005448e:
    bt L_00054492
    .org 0x54490-ORIGIN
L_00054490:
    add #0x1f,r2
    .org 0x54492-ORIGIN
L_00054492:
    shar r2
    .org 0x54494-ORIGIN
L_00054494:
    shar r2
    .org 0x54496-ORIGIN
L_00054496:
    shar r2
    .org 0x54498-ORIGIN
L_00054498:
    shar r2
    .org 0x5449a-ORIGIN
L_0005449a:
    mov #-0x1,r6
    .org 0x5449c-ORIGIN
L_0005449c:
    shar r2
    .org 0x5449e-ORIGIN
L_0005449e:
    extu.w r6,r6
    .org 0x544a0-ORIGIN
L_000544a0:
    cmp/hi r6,r2
    .org 0x544a2-ORIGIN
L_000544a2:
    bf L_000544a6
    .org 0x544a4-ORIGIN
L_000544a4:
    mov r6,r2
    .org 0x544a6-ORIGIN
L_000544a6:
    mov r2,r6
    .org 0x544a8-ORIGIN
L_000544a8:
    mov.l P_000545d8,r2
    .org 0x544aa-ORIGIN
L_000544aa:
    mov #0x36,r0
    .org 0x544ac-ORIGIN
L_000544ac:
    mov.w r6,@(r0,r2)
    .org 0x544ae-ORIGIN
L_000544ae:
    rts
    .org 0x544b0-ORIGIN
L_000544b0:
    lds.l @r15+,macl
    .org 0x544d2-ORIGIN
P_000544d2:
    .byte 0x06
    .org 0x544d3-ORIGIN
P_000544d3:
    .byte 0xc8
    .org 0x544d4-ORIGIN
P_000544d4:
    .byte 0x06
    .org 0x544d5-ORIGIN
P_000544d5:
    .byte 0xc9
    .org 0x544d6-ORIGIN
P_000544d6:
    .byte 0x0a
    .org 0x544d7-ORIGIN
P_000544d7:
    .byte 0xc6
    .org 0x545b0-ORIGIN
P_000545b0:
    .byte 0xff
    .org 0x545b1-ORIGIN
P_000545b1:
    .byte 0xff
    .org 0x545b2-ORIGIN
P_000545b2:
    .byte 0x28
    .org 0x545b3-ORIGIN
P_000545b3:
    .byte 0xf8
    .org 0x545cc-ORIGIN
P_000545cc:
    .byte 0xff
    .org 0x545cd-ORIGIN
P_000545cd:
    .byte 0xff
    .org 0x545ce-ORIGIN
P_000545ce:
    .byte 0x10
    .org 0x545cf-ORIGIN
P_000545cf:
    .byte 0x24
    .org 0x545d4-ORIGIN
P_000545d4:
    .byte 0x00
    .org 0x545d5-ORIGIN
P_000545d5:
    .byte 0x00
    .org 0x545d6-ORIGIN
P_000545d6:
    .byte 0x8b
    .org 0x545d7-ORIGIN
P_000545d7:
    .byte 0xbe
    .org 0x545d8-ORIGIN
P_000545d8:
    .byte 0xff
    .org 0x545d9-ORIGIN
P_000545d9:
    .byte 0xff
    .org 0x545da-ORIGIN
P_000545da:
    .byte 0x41
    .org 0x545db-ORIGIN
P_000545db:
    .byte 0x24
    .org 0xa5284-ORIGIN
L_000a5284:
    sts.l macl,@-r15
    .org 0xa5286-ORIGIN
L_000a5286:
    mov.l P_000a54d0,r6
    .org 0xa5288-ORIGIN
L_000a5288:
    mov r4,r7
    .org 0xa528a-ORIGIN
L_000a528a:
    mov.w P_000a5392,r0
    .org 0xa528c-ORIGIN
L_000a528c:
    extu.w r5,r5
    .org 0xa528e-ORIGIN
L_000a528e:
    mov.b @(r0,r6),r2
    .org 0xa5290-ORIGIN
L_000a5290:
    mov.w P_000a5394,r0
    .org 0xa5292-ORIGIN
L_000a5292:
    extu.b r2,r4
    .org 0xa5294-ORIGIN
L_000a5294:
    mov.b @(r0,r6),r2
    .org 0xa5296-ORIGIN
L_000a5296:
    extu.b r2,r6
    .org 0xa5298-ORIGIN
L_000a5298:
    mul.l r4,r6
    .org 0xa529a-ORIGIN
L_000a529a:
    mov #-0x80,r6
    .org 0xa529c-ORIGIN
L_000a529c:
    shll 8 r6
    .org 0xa529e-ORIGIN
L_000a529e:
    sts macl,r2
    .org 0xa52a0-ORIGIN
L_000a52a0:
    shll 16 r6
    .org 0xa52a2-ORIGIN
L_000a52a2:
    mul.l r2,r5
    .org 0xa52a4-ORIGIN
L_000a52a4:
    sts macl,r2
    .org 0xa52a6-ORIGIN
L_000a52a6:
    cmp/hs r6,r2
    .org 0xa52a8-ORIGIN
L_000a52a8:
    bf L_000a52ae
    .org 0xa52aa-ORIGIN
L_000a52aa:
    bra L_000a52b0
    .org 0xa52ac-ORIGIN
L_000a52ac:
    mov #-0x1,r2
    .org 0xa52ae-ORIGIN
L_000a52ae:
    shll r2
    .org 0xa52b0-ORIGIN
L_000a52b0:
    extu.w r2,r6
    .org 0xa52b2-ORIGIN
L_000a52b2:
    mov r2,r4
    .org 0xa52b4-ORIGIN
L_000a52b4:
    mov #0x1,r2
    .org 0xa52b6-ORIGIN
L_000a52b6:
    shll 16 r2
    .org 0xa52b8-ORIGIN
L_000a52b8:
    sub r5,r2
    .org 0xa52ba-ORIGIN
L_000a52ba:
    extu.w r7,r7
    .org 0xa52bc-ORIGIN
L_000a52bc:
    mul.l r7,r2
    .org 0xa52be-ORIGIN
L_000a52be:
    mov #0x1,r7
    .org 0xa52c0-ORIGIN
L_000a52c0:
    shll 16 r7
    .org 0xa52c2-ORIGIN
L_000a52c2:
    sts macl,r5
    .org 0xa52c4-ORIGIN
L_000a52c4:
    shlr 16 r4
    .org 0xa52c6-ORIGIN
L_000a52c6:
    extu.w r5,r2
    .org 0xa52c8-ORIGIN
L_000a52c8:
    add r2,r6
    .org 0xa52ca-ORIGIN
L_000a52ca:
    shlr 16 r5
    .org 0xa52cc-ORIGIN
L_000a52cc:
    cmp/hs r7,r6
    .org 0xa52ce-ORIGIN
L_000a52ce:
    movt r6
    .org 0xa52d0-ORIGIN
L_000a52d0:
    add r5,r4
    .org 0xa52d2-ORIGIN
L_000a52d2:
    add r6,r4
    .org 0xa52d4-ORIGIN
L_000a52d4:
    add #-0x1,r7
    .org 0xa52d6-ORIGIN
L_000a52d6:
    cmp/hi r7,r4
    .org 0xa52d8-ORIGIN
L_000a52d8:
    bf/s L_000a52de
    .org 0xa52da-ORIGIN
L_000a52da:
    mov r4,r2
    .org 0xa52dc-ORIGIN
L_000a52dc:
    mov #-0x1,r2
    .org 0xa52de-ORIGIN
L_000a52de:
    extu.w r2,r0
    .org 0xa52e0-ORIGIN
L_000a52e0:
    rts
    .org 0xa52e2-ORIGIN
L_000a52e2:
    lds.l @r15+,macl
    .org 0xa5392-ORIGIN
P_000a5392:
    .byte 0x0a
    .org 0xa5393-ORIGIN
P_000a5393:
    .byte 0x92
    .org 0xa5394-ORIGIN
P_000a5394:
    .byte 0x06
    .org 0xa5395-ORIGIN
P_000a5395:
    .byte 0xfa
    .org 0xa54d0-ORIGIN
P_000a54d0:
    .byte 0xff
    .org 0xa54d1-ORIGIN
P_000a54d1:
    .byte 0xff
    .org 0xa54d2-ORIGIN
P_000a54d2:
    .byte 0x28
    .org 0xa54d3-ORIGIN
P_000a54d3:
    .byte 0xf8
