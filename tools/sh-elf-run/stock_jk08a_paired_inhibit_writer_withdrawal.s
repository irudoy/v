! Complete natural paired flag callers and exact real nibble-mask helper.
    .text
    .balign 4
    .set ORIGIN,0x885c
    .org 0x885d-ORIGIN
P_0000885d:
    .byte 0x04
    .org 0x7c8fa-ORIGIN
L_0007c8fa:
    sts.l pr,@-r15
    .org 0x7c8fc-ORIGIN
L_0007c8fc:
    stc.l gbr,@-r15
    .org 0x7c8fe-ORIGIN
L_0007c8fe:
    mov.l P_0007cae0,r0
    .org 0x7c900-ORIGIN
L_0007c900:
    ldc r0,gbr
    .org 0x7c902-ORIGIN
L_0007c902:
    mov.l P_0007cae4,r6
    .org 0x7c904-ORIGIN
L_0007c904:
    mov #0x1c,r0
    .org 0x7c906-ORIGIN
L_0007c906:
    mov.b @(r0,r6),r0
    .org 0x7c908-ORIGIN
L_0007c908:
    tst #0x20,r0
    .org 0x7c90a-ORIGIN
L_0007c90a:
    bt L_0007c9a0
    .org 0x7c90c-ORIGIN
L_0007c90c:
    mov #0x26,r0
    .org 0x7c90e-ORIGIN
L_0007c90e:
    mov.b @(r0,r6),r0
    .org 0x7c910-ORIGIN
L_0007c910:
    tst #0x20,r0
    .org 0x7c912-ORIGIN
L_0007c912:
    bf L_0007c9a0
    .org 0x7c914-ORIGIN
L_0007c914:
    mov #0x31,r0
    .org 0x7c916-ORIGIN
L_0007c916:
    mov.l P_0007cae8,r5
    .org 0x7c918-ORIGIN
L_0007c918:
    or.b #0x4,@(r0,gbr)
    .org 0x7c91a-ORIGIN
L_0007c91a:
    mov #0x2e,r0
    .org 0x7c91c-ORIGIN
L_0007c91c:
    or.b #0x4,@(r0,gbr)
    .org 0x7c91e-ORIGIN
L_0007c91e:
    mov #0x2b,r0
    .org 0x7c920-ORIGIN
L_0007c920:
    or.b #0x4,@(r0,gbr)
    .org 0x7c922-ORIGIN
L_0007c922:
    mov #0x28,r0
    .org 0x7c924-ORIGIN
L_0007c924:
    or.b #0x4,@(r0,gbr)
    .org 0x7c926-ORIGIN
L_0007c926:
    mov #0x25,r0
    .org 0x7c928-ORIGIN
L_0007c928:
    or.b #0x4,@(r0,gbr)
    .org 0x7c92a-ORIGIN
L_0007c92a:
    mov #0x22,r0
    .org 0x7c92c-ORIGIN
L_0007c92c:
    or.b #0x4,@(r0,gbr)
    .org 0x7c92e-ORIGIN
L_0007c92e:
    mov #0x1f,r0
    .org 0x7c930-ORIGIN
L_0007c930:
    or.b #0x4,@(r0,gbr)
    .org 0x7c932-ORIGIN
L_0007c932:
    mov.b @(0x2,r5),r0
    .org 0x7c934-ORIGIN
L_0007c934:
    tst #0x8,r0
    .org 0x7c936-ORIGIN
L_0007c936:
    bf L_0007c9a0
    .org 0x7c938-ORIGIN
L_0007c938:
    mov #0x2b,r0
    .org 0x7c93a-ORIGIN
L_0007c93a:
    mov.l P_0007cadc,r4
    .org 0x7c93c-ORIGIN
L_0007c93c:
    mov.b @(r0,r6),r0
    .org 0x7c93e-ORIGIN
L_0007c93e:
    and #0xdf,r0
    .org 0x7c940-ORIGIN
L_0007c940:
    mov r0,r2
    .org 0x7c942-ORIGIN
L_0007c942:
    mov #0x2b,r0
    .org 0x7c944-ORIGIN
L_0007c944:
    mov.b r2,@(r0,r6)
    .org 0x7c946-ORIGIN
L_0007c946:
    mov #0x0,r2
    .org 0x7c948-ORIGIN
L_0007c948:
    mov.b @(0x1,r5),r0
    .org 0x7c94a-ORIGIN
L_0007c94a:
    and #0xbf,r0
    .org 0x7c94c-ORIGIN
L_0007c94c:
    mov.b r0,@(0x1,r5)
    .org 0x7c94e-ORIGIN
L_0007c94e:
    mov #0x32,r0
    .org 0x7c950-ORIGIN
L_0007c950:
    and.b #0xbf,@(r0,gbr)
    .org 0x7c952-ORIGIN
L_0007c952:
    mov #0x2f,r0
    .org 0x7c954-ORIGIN
L_0007c954:
    and.b #0xbf,@(r0,gbr)
    .org 0x7c956-ORIGIN
L_0007c956:
    mov #0x2c,r0
    .org 0x7c958-ORIGIN
L_0007c958:
    and.b #0xbf,@(r0,gbr)
    .org 0x7c95a-ORIGIN
L_0007c95a:
    mov #0x29,r0
    .org 0x7c95c-ORIGIN
L_0007c95c:
    and.b #0xbf,@(r0,gbr)
    .org 0x7c95e-ORIGIN
L_0007c95e:
    mov #0x26,r0
    .org 0x7c960-ORIGIN
L_0007c960:
    and.b #0xbf,@(r0,gbr)
    .org 0x7c962-ORIGIN
L_0007c962:
    mov #0x23,r0
    .org 0x7c964-ORIGIN
L_0007c964:
    and.b #0xbf,@(r0,gbr)
    .org 0x7c966-ORIGIN
L_0007c966:
    mov #0x20,r0
    .org 0x7c968-ORIGIN
L_0007c968:
    and.b #0xbf,@(r0,gbr)
    .org 0x7c96a-ORIGIN
L_0007c96a:
    mov.w P_0007ca58,r0
    .org 0x7c96c-ORIGIN
L_0007c96c:
    mov.b r2,@(r0,r4)
    .org 0x7c96e-ORIGIN
L_0007c96e:
    mov.w P_0007ca5a,r0
    .org 0x7c970-ORIGIN
L_0007c970:
    mov.b r2,@(r0,r4)
    .org 0x7c972-ORIGIN
L_0007c972:
    mov.w P_0007ca5c,r0
    .org 0x7c974-ORIGIN
L_0007c974:
    mov.w r2,@(r0,r4)
    .org 0x7c976-ORIGIN
L_0007c976:
    mov.b @r5,r0
    .org 0x7c978-ORIGIN
L_0007c978:
    and #0xfb,r0
    .org 0x7c97a-ORIGIN
L_0007c97a:
    mov.b r0,@r5
    .org 0x7c97c-ORIGIN
L_0007c97c:
    mov #0x18,r0
    .org 0x7c97e-ORIGIN
L_0007c97e:
    mov.b @(r0,r6),r0
    .org 0x7c980-ORIGIN
L_0007c980:
    and #0xfd,r0
    .org 0x7c982-ORIGIN
L_0007c982:
    mov r0,r2
    .org 0x7c984-ORIGIN
L_0007c984:
    mov #0x18,r0
    .org 0x7c986-ORIGIN
L_0007c986:
    mov.b r2,@(r0,r6)
    .org 0x7c988-ORIGIN
L_0007c988:
    mov #0x0,r2
    .org 0x7c98a-ORIGIN
L_0007c98a:
    mov.w P_0007ca5e,r0
    .org 0x7c98c-ORIGIN
L_0007c98c:
    mov.b r2,@(r0,r4)
    .org 0x7c98e-ORIGIN
L_0007c98e:
    mov.b @(0x9,r5),r0
    .org 0x7c990-ORIGIN
L_0007c990:
    tst #0x80,r0
    .org 0x7c992-ORIGIN
L_0007c992:
    bf/s L_0007c9a0
    .org 0x7c994-ORIGIN
L_0007c994:
    mov r0,r2
    .org 0x7c996-ORIGIN
L_0007c996:
    mov r2,r0
    .org 0x7c998-ORIGIN
L_0007c998:
    tst #0x20,r0
    .org 0x7c99a-ORIGIN
L_0007c99a:
    bt L_0007c9a0
    .org 0x7c99c-ORIGIN
L_0007c99c:
    bsr L_0007d84c
    .org 0x7c99e-ORIGIN
L_0007c99e:
    nop
    .org 0x7c9a0-ORIGIN
L_0007c9a0:
    ldc.l @r15+,gbr
    .org 0x7c9a2-ORIGIN
L_0007c9a2:
    lds.l @r15+,pr
    .org 0x7c9a4-ORIGIN
L_0007c9a4:
    rts
    .org 0x7c9a6-ORIGIN
L_0007c9a6:
    nop
    .org 0x7c9a8-ORIGIN
L_0007c9a8:
    sts.l pr,@-r15
    .org 0x7c9aa-ORIGIN
L_0007c9aa:
    stc.l gbr,@-r15
    .org 0x7c9ac-ORIGIN
L_0007c9ac:
    mov.l P_0007cae0,r0
    .org 0x7c9ae-ORIGIN
L_0007c9ae:
    ldc r0,gbr
    .org 0x7c9b0-ORIGIN
L_0007c9b0:
    mov.l P_0007cae4,r5
    .org 0x7c9b2-ORIGIN
L_0007c9b2:
    mov #0x2f,r0
    .org 0x7c9b4-ORIGIN
L_0007c9b4:
    mov.b @(r0,r5),r0
    .org 0x7c9b6-ORIGIN
L_0007c9b6:
    tst #0x20,r0
    .org 0x7c9b8-ORIGIN
L_0007c9b8:
    bt L_0007ca50
    .org 0x7c9ba-ORIGIN
L_0007c9ba:
    mov #0x12,r0
    .org 0x7c9bc-ORIGIN
L_0007c9bc:
    mov.b @(r0,r5),r0
    .org 0x7c9be-ORIGIN
L_0007c9be:
    tst #0x40,r0
    .org 0x7c9c0-ORIGIN
L_0007c9c0:
    bf L_0007ca50
    .org 0x7c9c2-ORIGIN
L_0007c9c2:
    mov.l P_0007caec,r2
    .org 0x7c9c4-ORIGIN
L_0007c9c4:
    mov.w P_0007ca60,r0
    .org 0x7c9c6-ORIGIN
L_0007c9c6:
    mov.l P_0007caf0,r5
    .org 0x7c9c8-ORIGIN
L_0007c9c8:
    mov.b @(r0,r2),r6
    .org 0x7c9ca-ORIGIN
L_0007c9ca:
    mov.b @r5,r2
    .org 0x7c9cc-ORIGIN
L_0007c9cc:
    cmp/hs r2,r6
    .org 0x7c9ce-ORIGIN
L_0007c9ce:
    bt L_0007ca50
    .org 0x7c9d0-ORIGIN
L_0007c9d0:
    mov #0x31,r0
    .org 0x7c9d2-ORIGIN
L_0007c9d2:
    mov.l P_0007cae8,r6
    .org 0x7c9d4-ORIGIN
L_0007c9d4:
    or.b #0x4,@(r0,gbr)
    .org 0x7c9d6-ORIGIN
L_0007c9d6:
    mov #0x2e,r0
    .org 0x7c9d8-ORIGIN
L_0007c9d8:
    or.b #0x4,@(r0,gbr)
    .org 0x7c9da-ORIGIN
L_0007c9da:
    mov #0x2b,r0
    .org 0x7c9dc-ORIGIN
L_0007c9dc:
    or.b #0x4,@(r0,gbr)
    .org 0x7c9de-ORIGIN
L_0007c9de:
    mov #0x28,r0
    .org 0x7c9e0-ORIGIN
L_0007c9e0:
    or.b #0x4,@(r0,gbr)
    .org 0x7c9e2-ORIGIN
L_0007c9e2:
    mov #0x25,r0
    .org 0x7c9e4-ORIGIN
L_0007c9e4:
    or.b #0x4,@(r0,gbr)
    .org 0x7c9e6-ORIGIN
L_0007c9e6:
    mov #0x22,r0
    .org 0x7c9e8-ORIGIN
L_0007c9e8:
    or.b #0x4,@(r0,gbr)
    .org 0x7c9ea-ORIGIN
L_0007c9ea:
    mov #0x1f,r0
    .org 0x7c9ec-ORIGIN
L_0007c9ec:
    or.b #0x4,@(r0,gbr)
    .org 0x7c9ee-ORIGIN
L_0007c9ee:
    mov.b @(0x2,r6),r0
    .org 0x7c9f0-ORIGIN
L_0007c9f0:
    tst #0x8,r0
    .org 0x7c9f2-ORIGIN
L_0007c9f2:
    bf L_0007ca50
    .org 0x7c9f4-ORIGIN
L_0007c9f4:
    mov.l P_0007cae4,r5
    .org 0x7c9f6-ORIGIN
L_0007c9f6:
    mov #0x2b,r0
    .org 0x7c9f8-ORIGIN
L_0007c9f8:
    mov.b @(r0,r5),r0
    .org 0x7c9fa-ORIGIN
L_0007c9fa:
    and #0xf7,r0
    .org 0x7c9fc-ORIGIN
L_0007c9fc:
    mov r0,r2
    .org 0x7c9fe-ORIGIN
L_0007c9fe:
    mov #0x2b,r0
    .org 0x7ca00-ORIGIN
L_0007ca00:
    mov.b r2,@(r0,r5)
    .org 0x7ca02-ORIGIN
L_0007ca02:
    mov #0x0,r2
    .org 0x7ca04-ORIGIN
L_0007ca04:
    mov.b @(0x1,r6),r0
    .org 0x7ca06-ORIGIN
L_0007ca06:
    mov.l P_0007cadc,r5
    .org 0x7ca08-ORIGIN
L_0007ca08:
    and #0xef,r0
    .org 0x7ca0a-ORIGIN
L_0007ca0a:
    mov.b r0,@(0x1,r6)
    .org 0x7ca0c-ORIGIN
L_0007ca0c:
    mov #0x32,r0
    .org 0x7ca0e-ORIGIN
L_0007ca0e:
    and.b #0xbf,@(r0,gbr)
    .org 0x7ca10-ORIGIN
L_0007ca10:
    mov #0x2f,r0
    .org 0x7ca12-ORIGIN
L_0007ca12:
    and.b #0xbf,@(r0,gbr)
    .org 0x7ca14-ORIGIN
L_0007ca14:
    mov #0x2c,r0
    .org 0x7ca16-ORIGIN
L_0007ca16:
    and.b #0xbf,@(r0,gbr)
    .org 0x7ca18-ORIGIN
L_0007ca18:
    mov #0x29,r0
    .org 0x7ca1a-ORIGIN
L_0007ca1a:
    and.b #0xbf,@(r0,gbr)
    .org 0x7ca1c-ORIGIN
L_0007ca1c:
    mov #0x26,r0
    .org 0x7ca1e-ORIGIN
L_0007ca1e:
    and.b #0xbf,@(r0,gbr)
    .org 0x7ca20-ORIGIN
L_0007ca20:
    mov #0x23,r0
    .org 0x7ca22-ORIGIN
L_0007ca22:
    and.b #0xbf,@(r0,gbr)
    .org 0x7ca24-ORIGIN
L_0007ca24:
    mov #0x20,r0
    .org 0x7ca26-ORIGIN
L_0007ca26:
    and.b #0xbf,@(r0,gbr)
    .org 0x7ca28-ORIGIN
L_0007ca28:
    mov.w P_0007ca62,r0
    .org 0x7ca2a-ORIGIN
L_0007ca2a:
    mov.b r2,@(r0,r5)
    .org 0x7ca2c-ORIGIN
L_0007ca2c:
    mov.w P_0007ca64,r0
    .org 0x7ca2e-ORIGIN
L_0007ca2e:
    mov.b r2,@(r0,r5)
    .org 0x7ca30-ORIGIN
L_0007ca30:
    mov.w P_0007ca66,r0
    .org 0x7ca32-ORIGIN
L_0007ca32:
    mov.w r2,@(r0,r5)
    .org 0x7ca34-ORIGIN
L_0007ca34:
    mov.b @(0x1,r6),r0
    .org 0x7ca36-ORIGIN
L_0007ca36:
    and #0x7f,r0
    .org 0x7ca38-ORIGIN
L_0007ca38:
    mov.b r0,@(0x1,r6)
    .org 0x7ca3a-ORIGIN
L_0007ca3a:
    mov.w P_0007ca68,r0
    .org 0x7ca3c-ORIGIN
L_0007ca3c:
    mov.b r2,@(r0,r5)
    .org 0x7ca3e-ORIGIN
L_0007ca3e:
    mov.b @(0x9,r6),r0
    .org 0x7ca40-ORIGIN
L_0007ca40:
    tst #0x80,r0
    .org 0x7ca42-ORIGIN
L_0007ca42:
    bf/s L_0007ca50
    .org 0x7ca44-ORIGIN
L_0007ca44:
    mov r0,r2
    .org 0x7ca46-ORIGIN
L_0007ca46:
    mov r2,r0
    .org 0x7ca48-ORIGIN
L_0007ca48:
    tst #0x20,r0
    .org 0x7ca4a-ORIGIN
L_0007ca4a:
    bt L_0007ca50
    .org 0x7ca4c-ORIGIN
L_0007ca4c:
    bsr L_0007d84c
    .org 0x7ca4e-ORIGIN
L_0007ca4e:
    nop
    .org 0x7ca50-ORIGIN
L_0007ca50:
    ldc.l @r15+,gbr
    .org 0x7ca52-ORIGIN
L_0007ca52:
    lds.l @r15+,pr
    .org 0x7ca54-ORIGIN
L_0007ca54:
    rts
    .org 0x7ca56-ORIGIN
L_0007ca56:
    nop
    .org 0x7ca58-ORIGIN
P_0007ca58:
    .byte 0x05
    .org 0x7ca59-ORIGIN
P_0007ca59:
    .byte 0x6e
    .org 0x7ca5a-ORIGIN
P_0007ca5a:
    .byte 0x04
    .org 0x7ca5b-ORIGIN
P_0007ca5b:
    .byte 0xed
    .org 0x7ca5c-ORIGIN
P_0007ca5c:
    .byte 0x05
    .org 0x7ca5d-ORIGIN
P_0007ca5d:
    .byte 0x18
    .org 0x7ca5e-ORIGIN
P_0007ca5e:
    .byte 0x03
    .org 0x7ca5f-ORIGIN
P_0007ca5f:
    .byte 0x6a
    .org 0x7ca60-ORIGIN
P_0007ca60:
    .byte 0x08
    .org 0x7ca61-ORIGIN
P_0007ca61:
    .byte 0x20
    .org 0x7ca62-ORIGIN
P_0007ca62:
    .byte 0x05
    .org 0x7ca63-ORIGIN
P_0007ca63:
    .byte 0x70
    .org 0x7ca64-ORIGIN
P_0007ca64:
    .byte 0x04
    .org 0x7ca65-ORIGIN
P_0007ca65:
    .byte 0xef
    .org 0x7ca66-ORIGIN
P_0007ca66:
    .byte 0x05
    .org 0x7ca67-ORIGIN
P_0007ca67:
    .byte 0x1c
    .org 0x7ca68-ORIGIN
P_0007ca68:
    .byte 0x03
    .org 0x7ca69-ORIGIN
P_0007ca69:
    .byte 0x6c
    .org 0x7cadc-ORIGIN
P_0007cadc:
    .byte 0xff
    .org 0x7cadd-ORIGIN
P_0007cadd:
    .byte 0xff
    .org 0x7cade-ORIGIN
P_0007cade:
    .byte 0x45
    .org 0x7cadf-ORIGIN
P_0007cadf:
    .byte 0x58
    .org 0x7cae0-ORIGIN
P_0007cae0:
    .byte 0xff
    .org 0x7cae1-ORIGIN
P_0007cae1:
    .byte 0xff
    .org 0x7cae2-ORIGIN
P_0007cae2:
    .byte 0x57
    .org 0x7cae3-ORIGIN
P_0007cae3:
    .byte 0x18
    .org 0x7cae4-ORIGIN
P_0007cae4:
    .byte 0xff
    .org 0x7cae5-ORIGIN
P_0007cae5:
    .byte 0xff
    .org 0x7cae6-ORIGIN
P_0007cae6:
    .byte 0x41
    .org 0x7cae7-ORIGIN
P_0007cae7:
    .byte 0xa9
    .org 0x7cae8-ORIGIN
P_0007cae8:
    .byte 0xff
    .org 0x7cae9-ORIGIN
P_0007cae9:
    .byte 0xff
    .org 0x7caea-ORIGIN
P_0007caea:
    .byte 0x5b
    .org 0x7caeb-ORIGIN
P_0007caeb:
    .byte 0x2a
    .org 0x7caec-ORIGIN
P_0007caec:
    .byte 0xff
    .org 0x7caed-ORIGIN
P_0007caed:
    .byte 0xff
    .org 0x7caee-ORIGIN
P_0007caee:
    .byte 0x28
    .org 0x7caef-ORIGIN
P_0007caef:
    .byte 0xf8
    .org 0x7caf0-ORIGIN
P_0007caf0:
    .byte 0x00
    .org 0x7caf1-ORIGIN
P_0007caf1:
    .byte 0x00
    .org 0x7caf2-ORIGIN
P_0007caf2:
    .byte 0x88
    .org 0x7caf3-ORIGIN
P_0007caf3:
    .byte 0x5d
    .org 0x7d84c-ORIGIN
L_0007d84c:
    mov.l P_0007d8a0,r6
    .org 0x7d84e-ORIGIN
L_0007d84e:
    mov.b @r6,r0
    .org 0x7d850-ORIGIN
L_0007d850:
    and #0xf,r0
    .org 0x7d852-ORIGIN
L_0007d852:
    rts
    .org 0x7d854-ORIGIN
L_0007d854:
    mov.b r0,@r6
    .org 0x7d8a0-ORIGIN
P_0007d8a0:
    .byte 0xff
    .org 0x7d8a1-ORIGIN
P_0007d8a1:
    .byte 0xff
    .org 0x7d8a2-ORIGIN
P_0007d8a2:
    .byte 0x5b
    .org 0x7d8a3-ORIGIN
P_0007d8a3:
    .byte 0x33
