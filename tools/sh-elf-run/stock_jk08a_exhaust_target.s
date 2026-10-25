! JK08A exhaust-target conditional paths and natural hysteresis helper.
! The complete function listing is reconstructed; only declared positive modes are admitted.
! Other calls are not stubbed and cannot be reached by admitted observations.
    .text
    .balign 4
    .set ORIGIN,0x259d0
    .org 0x259d0-ORIGIN
L_000259d0:
    extu.b r7,r7
    .org 0x259d2-ORIGIN
L_000259d2:
    tst r7,r7
    .org 0x259d4-ORIGIN
L_000259d4:
    bt/s L_000259da
    .org 0x259d6-ORIGIN
L_000259d6:
    mov r4,r2
    .org 0x259d8-ORIGIN
L_000259d8:
    sub r6,r2
    .org 0x259da-ORIGIN
L_000259da:
    cmp/gt r5,r2
    .org 0x259dc-ORIGIN
L_000259dc:
    movt r0
    .org 0x259de-ORIGIN
L_000259de:
    xor #0x1,r0
    .org 0x259e0-ORIGIN
L_000259e0:
    rts
    .org 0x259e2-ORIGIN
L_000259e2:
    extu.b r0,r0
    .org 0xbfe88-ORIGIN
L_000bfe88:
    mov.l r8,@-r15
    .org 0xbfe8a-ORIGIN
L_000bfe8a:
    mov.l r9,@-r15
    .org 0xbfe8c-ORIGIN
L_000bfe8c:
    mov.l r10,@-r15
    .org 0xbfe8e-ORIGIN
L_000bfe8e:
    mov.l r11,@-r15
    .org 0xbfe90-ORIGIN
L_000bfe90:
    mov.l r12,@-r15
    .org 0xbfe92-ORIGIN
L_000bfe92:
    mov.l r13,@-r15
    .org 0xbfe94-ORIGIN
L_000bfe94:
    mov.l r14,@-r15
    .org 0xbfe96-ORIGIN
L_000bfe96:
    sts.l pr,@-r15
    .org 0xbfe98-ORIGIN
L_000bfe98:
    sts.l macl,@-r15
    .org 0xbfe9a-ORIGIN
L_000bfe9a:
    stc.l gbr,@-r15
    .org 0xbfe9c-ORIGIN
L_000bfe9c:
    mov.l L_000bfff8,r0
    .org 0xbfe9e-ORIGIN
L_000bfe9e:
    ldc r0,gbr
    .org 0xbfea0-ORIGIN
L_000bfea0:
    add #-0x38,r15
    .org 0xbfea2-ORIGIN
L_000bfea2:
    mov.l L_000bfffc,r6
    .org 0xbfea4-ORIGIN
L_000bfea4:
    mov.l L_000c002c,r13
    .org 0xbfea6-ORIGIN
L_000bfea6:
    mov.b @(0x3,r6),r0
    .org 0xbfea8-ORIGIN
L_000bfea8:
    extu.b r0,r2
    .org 0xbfeaa-ORIGIN
L_000bfeaa:
    mov.b @(0xf3,gbr),r0
    .org 0xbfeac-ORIGIN
L_000bfeac:
    mov.l r2,@r15
    .org 0xbfeae-ORIGIN
L_000bfeae:
    mov.l L_000c0010,r2
    .org 0xbfeb0-ORIGIN
L_000bfeb0:
    mov r0,r12
    .org 0xbfeb2-ORIGIN
L_000bfeb2:
    mov #0x12,r0
    .org 0xbfeb4-ORIGIN
L_000bfeb4:
    mov.b @(r0,r2),r4
    .org 0xbfeb6-ORIGIN
L_000bfeb6:
    mov #0x43,r0
    .org 0xbfeb8-ORIGIN
L_000bfeb8:
    mov.b @(r0,r13),r5
    .org 0xbfeba-ORIGIN
L_000bfeba:
    extu.b r4,r4
    .org 0xbfebc-ORIGIN
L_000bfebc:
    mov r5,r0
    .org 0xbfebe-ORIGIN
L_000bfebe:
    tst #0x1,r0
    .org 0xbfec0-ORIGIN
L_000bfec0:
    bt/s L_000bfecc
    .org 0xbfec2-ORIGIN
L_000bfec2:
    mov r4,r6
    .org 0xbfec4-ORIGIN
L_000bfec4:
    mov.l L_000c0030,r7
    .org 0xbfec6-ORIGIN
L_000bfec6:
    mov.b @r7,r2
    .org 0xbfec8-ORIGIN
L_000bfec8:
    extu.b r2,r2
    .org 0xbfeca-ORIGIN
L_000bfeca:
    add r2,r6
    .org 0xbfecc-ORIGIN
L_000bfecc:
    mov.l L_000c0034,r14
    .org 0xbfece-ORIGIN
L_000bfece:
    mov.b @(0x5,r14),r0
    .org 0xbfed0-ORIGIN
L_000bfed0:
    extu.b r0,r2
    .org 0xbfed2-ORIGIN
L_000bfed2:
    mov r5,r0
    .org 0xbfed4-ORIGIN
L_000bfed4:
    cmp/hs r2,r6
    .org 0xbfed6-ORIGIN
L_000bfed6:
    bt/s L_000bfedc
    .org 0xbfed8-ORIGIN
L_000bfed8:
    or #0x1,r0
    .org 0xbfeda-ORIGIN
L_000bfeda:
    and #0xfe,r0
    .org 0xbfedc-ORIGIN
L_000bfedc:
    mov.l L_000c0034,r3
    .org 0xbfede-ORIGIN
L_000bfede:
    mov r0,r2
    .org 0xbfee0-ORIGIN
L_000bfee0:
    mov #0x43,r0
    .org 0xbfee2-ORIGIN
L_000bfee2:
    mov.l L_000c0030,r7
    .org 0xbfee4-ORIGIN
L_000bfee4:
    mov.b r2,@(r0,r13)
    .org 0xbfee6-ORIGIN
L_000bfee6:
    mov.b @(0x4,r3),r0
    .org 0xbfee8-ORIGIN
L_000bfee8:
    mov.b @r7,r6
    .org 0xbfeea-ORIGIN
L_000bfeea:
    extu.b r0,r5
    .org 0xbfeec-ORIGIN
L_000bfeec:
    mov #0x43,r0
    .org 0xbfeee-ORIGIN
L_000bfeee:
    mov.b @(r0,r13),r0
    .org 0xbfef0-ORIGIN
L_000bfef0:
    extu.b r6,r6
    .org 0xbfef2-ORIGIN
L_000bfef2:
    tst #0x2,r0
    .org 0xbfef4-ORIGIN
L_000bfef4:
    movt r0
    .org 0xbfef6-ORIGIN
L_000bfef6:
    mov.l L_000c0038,r14
    .org 0xbfef8-ORIGIN
L_000bfef8:
    xor #0x1,r0
    .org 0xbfefa-ORIGIN
L_000bfefa:
    jsr @r14
    .org 0xbfefc-ORIGIN
L_000bfefc:
    extu.b r0,r7
    .org 0xbfefe-ORIGIN
L_000bfefe:
    mov r0,r2
    .org 0xbff00-ORIGIN
L_000bff00:
    mov #0x43,r0
    .org 0xbff02-ORIGIN
L_000bff02:
    mov.b @(r0,r13),r6
    .org 0xbff04-ORIGIN
L_000bff04:
    mov r2,r0
    .org 0xbff06-ORIGIN
L_000bff06:
    tst #0x1,r0
    .org 0xbff08-ORIGIN
L_000bff08:
    mov r6,r0
    .org 0xbff0a-ORIGIN
L_000bff0a:
    bf/s L_000bff10
    .org 0xbff0c-ORIGIN
L_000bff0c:
    or #0x2,r0
    .org 0xbff0e-ORIGIN
L_000bff0e:
    and #0xfd,r0
    .org 0xbff10-ORIGIN
L_000bff10:
    mov r0,r6
    .org 0xbff12-ORIGIN
L_000bff12:
    mov #0x43,r0
    .org 0xbff14-ORIGIN
L_000bff14:
    mov.b r6,@(r0,r13)
    .org 0xbff16-ORIGIN
L_000bff16:
    mov #0x7a,r0
    .org 0xbff18-ORIGIN
L_000bff18:
    mov.l L_000c003c,r6
    .org 0xbff1a-ORIGIN
L_000bff1a:
    mov.l L_000c0034,r3
    .org 0xbff1c-ORIGIN
L_000bff1c:
    mov.b @(r0,r6),r2
    .org 0xbff1e-ORIGIN
L_000bff1e:
    mov.b @(0x6,r3),r0
    .org 0xbff20-ORIGIN
L_000bff20:
    extu.b r2,r4
    .org 0xbff22-ORIGIN
L_000bff22:
    mov.l L_000c0040,r2
    .org 0xbff24-ORIGIN
L_000bff24:
    extu.b r0,r5
    .org 0xbff26-ORIGIN
L_000bff26:
    mov #0x44,r0
    .org 0xbff28-ORIGIN
L_000bff28:
    mov.b @r2,r6
    .org 0xbff2a-ORIGIN
L_000bff2a:
    mov.b @(r0,r13),r0
    .org 0xbff2c-ORIGIN
L_000bff2c:
    extu.b r6,r6
    .org 0xbff2e-ORIGIN
L_000bff2e:
    tst #0x80,r0
    .org 0xbff30-ORIGIN
L_000bff30:
    movt r0
    .org 0xbff32-ORIGIN
L_000bff32:
    xor #0x1,r0
    .org 0xbff34-ORIGIN
L_000bff34:
    jsr @r14
    .org 0xbff36-ORIGIN
L_000bff36:
    extu.b r0,r7
    .org 0xbff38-ORIGIN
L_000bff38:
    mov r0,r2
    .org 0xbff3a-ORIGIN
L_000bff3a:
    mov #0x44,r0
    .org 0xbff3c-ORIGIN
L_000bff3c:
    mov.b @(r0,r13),r6
    .org 0xbff3e-ORIGIN
L_000bff3e:
    mov r2,r0
    .org 0xbff40-ORIGIN
L_000bff40:
    tst #0x1,r0
    .org 0xbff42-ORIGIN
L_000bff42:
    mov r6,r0
    .org 0xbff44-ORIGIN
L_000bff44:
    bf/s L_000bff4a
    .org 0xbff46-ORIGIN
L_000bff46:
    or #0x80,r0
    .org 0xbff48-ORIGIN
L_000bff48:
    and #0x7f,r0
    .org 0xbff4a-ORIGIN
L_000bff4a:
    mov r0,r6
    .org 0xbff4c-ORIGIN
L_000bff4c:
    mov #0x44,r0
    .org 0xbff4e-ORIGIN
L_000bff4e:
    mov.b r6,@(r0,r13)
    .org 0xbff50-ORIGIN
L_000bff50:
    mov #-0x8,r0
    .org 0xbff52-ORIGIN
L_000bff52:
    mov.l L_000c0044,r6
    .org 0xbff54-ORIGIN
L_000bff54:
    extu.b r0,r0
    .org 0xbff56-ORIGIN
L_000bff56:
    mov.b @r6,r2
    .org 0xbff58-ORIGIN
L_000bff58:
    mov.l L_000c0048,r6
    .org 0xbff5a-ORIGIN
L_000bff5a:
    extu.b r2,r2
    .org 0xbff5c-ORIGIN
L_000bff5c:
    mov.b @(r0,r6),r5
    .org 0xbff5e-ORIGIN
L_000bff5e:
    mov #0x40,r0
    .org 0xbff60-ORIGIN
L_000bff60:
    mov.b @(r0,r13),r4
    .org 0xbff62-ORIGIN
L_000bff62:
    add #0x32,r2
    .org 0xbff64-ORIGIN
L_000bff64:
    mov r4,r0
    .org 0xbff66-ORIGIN
L_000bff66:
    tst #0x2,r0
    .org 0xbff68-ORIGIN
L_000bff68:
    bt/s L_000bff74
    .org 0xbff6a-ORIGIN
L_000bff6a:
    extu.b r5,r5
    .org 0xbff6c-ORIGIN
L_000bff6c:
    mov.l L_000c004c,r7
    .org 0xbff6e-ORIGIN
L_000bff6e:
    mov.b @r7,r6
    .org 0xbff70-ORIGIN
L_000bff70:
    extu.b r6,r6
    .org 0xbff72-ORIGIN
L_000bff72:
    add r6,r5
    .org 0xbff74-ORIGIN
L_000bff74:
    extu.w r2,r2
    .org 0xbff76-ORIGIN
L_000bff76:
    mov r4,r0
    .org 0xbff78-ORIGIN
L_000bff78:
    cmp/hs r2,r5
    .org 0xbff7a-ORIGIN
L_000bff7a:
    bt/s L_000bff80
    .org 0xbff7c-ORIGIN
L_000bff7c:
    or #0x2,r0
    .org 0xbff7e-ORIGIN
L_000bff7e:
    and #0xfd,r0
    .org 0xbff80-ORIGIN
L_000bff80:
    mov r0,r2
    .org 0xbff82-ORIGIN
L_000bff82:
    mov #0x40,r0
    .org 0xbff84-ORIGIN
L_000bff84:
    mov.l L_000c0050,r6
    .org 0xbff86-ORIGIN
L_000bff86:
    mov.b r2,@(r0,r13)
    .org 0xbff88-ORIGIN
L_000bff88:
    mov #0x32,r0
    .org 0xbff8a-ORIGIN
L_000bff8a:
    mov.b @(r0,r6),r2
    .org 0xbff8c-ORIGIN
L_000bff8c:
    mov #0x33,r0
    .org 0xbff8e-ORIGIN
L_000bff8e:
    extu.b r2,r5
    .org 0xbff90-ORIGIN
L_000bff90:
    mov.b @(r0,r6),r2
    .org 0xbff92-ORIGIN
L_000bff92:
    add #-0x80,r5
    .org 0xbff94-ORIGIN
L_000bff94:
    extu.b r2,r7
    .org 0xbff96-ORIGIN
L_000bff96:
    mov.l L_000c0054,r2
    .org 0xbff98-ORIGIN
L_000bff98:
    mov.b @r2,r4
    .org 0xbff9a-ORIGIN
L_000bff9a:
    extu.b r4,r4
    .org 0xbff9c-ORIGIN
L_000bff9c:
    neg r4,r6
    .org 0xbff9e-ORIGIN
L_000bff9e:
    cmp/gt r5,r6
    .org 0xbffa0-ORIGIN
L_000bffa0:
    bt/s L_000bffb2
    .org 0xbffa2-ORIGIN
L_000bffa2:
    add #-0x80,r7
    .org 0xbffa4-ORIGIN
L_000bffa4:
    neg r4,r6
    .org 0xbffa6-ORIGIN
L_000bffa6:
    cmp/gt r7,r6
    .org 0xbffa8-ORIGIN
L_000bffa8:
    bt L_000bffb2
    .org 0xbffaa-ORIGIN
L_000bffaa:
    cmp/gt r4,r5
    .org 0xbffac-ORIGIN
L_000bffac:
    bt L_000bffb2
    .org 0xbffae-ORIGIN
L_000bffae:
    cmp/gt r4,r7
    .org 0xbffb0-ORIGIN
L_000bffb0:
    bf L_000bffbe
    .org 0xbffb2-ORIGIN
L_000bffb2:
    mov.l L_000c0058,r6
    .org 0xbffb4-ORIGIN
L_000bffb4:
    mov.b @(0x3,r6),r0
    .org 0xbffb6-ORIGIN
L_000bffb6:
    mov.l L_000c005c,r6
    .org 0xbffb8-ORIGIN
L_000bffb8:
    mov r0,r2
    .org 0xbffba-ORIGIN
L_000bffba:
    mov #0x7d,r0
    .org 0xbffbc-ORIGIN
L_000bffbc:
    mov.b r2,@(r0,r6)
    .org 0xbffbe-ORIGIN
L_000bffbe:
    mov #0x23,r0
    .org 0xbffc0-ORIGIN
L_000bffc0:
    mov.b @(r0,r13),r11
    .org 0xbffc2-ORIGIN
L_000bffc2:
    mov r11,r0
    .org 0xbffc4-ORIGIN
L_000bffc4:
    tst #0x1,r0
    .org 0xbffc6-ORIGIN
L_000bffc6:
    bf L_000bffcc
    .org 0xbffc8-ORIGIN
L_000bffc8:
    bra L_000c0ce0
    .org 0xbffca-ORIGIN
L_000bffca:
    nop
    .org 0xbffcc-ORIGIN
L_000bffcc:
    mov.b @(0x4,r13),r0
    .org 0xbffce-ORIGIN
L_000bffce:
    mov.l L_000c0060,r2
    .org 0xbffd0-ORIGIN
L_000bffd0:
    mov r0,r14
    .org 0xbffd2-ORIGIN
L_000bffd2:
    mov #0x41,r0
    .org 0xbffd4-ORIGIN
L_000bffd4:
    mov.b @(r0,r13),r10
    .org 0xbffd6-ORIGIN
L_000bffd6:
    mov.b @r2,r5
    .org 0xbffd8-ORIGIN
L_000bffd8:
    mov r10,r0
    .org 0xbffda-ORIGIN
L_000bffda:
    mov.b r0,@(0x4,r15)
    .org 0xbffdc-ORIGIN
L_000bffdc:
    mov #0x1a,r0
    .org 0xbffde-ORIGIN
L_000bffde:
    mov.b @(r0,r13),r9
    .org 0xbffe0-ORIGIN
L_000bffe0:
    mov #0x22,r0
    .org 0xbffe2-ORIGIN
L_000bffe2:
    mov.b @(r0,r13),r8
    .org 0xbffe4-ORIGIN
L_000bffe4:
    mov r5,r0
    .org 0xbffe6-ORIGIN
L_000bffe6:
    tst #0x4,r0
    .org 0xbffe8-ORIGIN
L_000bffe8:
    bt L_000c0094
    .org 0xbffea-ORIGIN
L_000bffea:
    mov.l L_000c0064,r6
    .org 0xbffec-ORIGIN
L_000bffec:
    mov.b @r6,r0
    .org 0xbffee-ORIGIN
L_000bffee:
    tst #0x10,r0
    .org 0xbfff0-ORIGIN
L_000bfff0:
    bt L_000c0094
    .org 0xbfff2-ORIGIN
L_000bfff2:
    bra L_000c0068
    .org 0xbfff4-ORIGIN
L_000bfff4:
    nop
    .org 0xbfff8-ORIGIN
L_000bfff8:
    .long 0xffff128c
    .org 0xbfffc-ORIGIN
L_000bfffc:
    .long 0xffff2324
    .org 0xc0010-ORIGIN
L_000c0010:
    .long 0xffff119c
    .org 0xc002c-ORIGIN
L_000c002c:
    .long 0xffff2468
    .org 0xc0030-ORIGIN
L_000c0030:
    .long 0x000086e1
    .org 0xc0034-ORIGIN
L_000c0034:
    .long 0x00008e36
    .org 0xc0038-ORIGIN
L_000c0038:
    .long 0x000259d0
    .org 0xc003c-ORIGIN
L_000c003c:
    .long 0xffff1094
    .org 0xc0040-ORIGIN
L_000c0040:
    .long 0x000086e8
    .org 0xc0044-ORIGIN
L_000c0044:
    .long 0x00008dee
    .org 0xc0048-ORIGIN
L_000c0048:
    .long 0xffff267a
    .org 0xc004c-ORIGIN
L_000c004c:
    .long 0x00008e28
    .org 0xc0050-ORIGIN
L_000c0050:
    .long 0xffff120e
    .org 0xc0054-ORIGIN
L_000c0054:
    .long 0x00008e16
    .org 0xc0058-ORIGIN
L_000c0058:
    .long 0x00008cbc
    .org 0xc005c-ORIGIN
L_000c005c:
    .long 0xffff256a
    .org 0xc0060-ORIGIN
L_000c0060:
    .long 0x00008615
    .org 0xc0064-ORIGIN
L_000c0064:
    .long 0x00008b34
    .org 0xc0068-ORIGIN
L_000c0068:
    mov.l L_000c0268,r2
    .org 0xc006a-ORIGIN
L_000c006a:
    mov.b @r2,r0
    .org 0xc006c-ORIGIN
L_000c006c:
    tst #0x1,r0
    .org 0xc006e-ORIGIN
L_000c006e:
    bf L_000c008e
    .org 0xc0070-ORIGIN
L_000c0070:
    mov.l L_000c026c,r3
    .org 0xc0072-ORIGIN
L_000c0072:
    mov #0x50,r0
    .org 0xc0074-ORIGIN
L_000c0074:
    mov.b @(r0,r3),r0
    .org 0xc0076-ORIGIN
L_000c0076:
    tst #0x8,r0
    .org 0xc0078-ORIGIN
L_000c0078:
    bt L_000c0146
    .org 0xc007a-ORIGIN
L_000c007a:
    mov.l L_000c0270,r2
    .org 0xc007c-ORIGIN
L_000c007c:
    mov.w @(0x4,r2),r0
    .org 0xc007e-ORIGIN
L_000c007e:
    mov #-0x1,r2
    .org 0xc0080-ORIGIN
L_000c0080:
    extu.b r2,r2
    .org 0xc0082-ORIGIN
L_000c0082:
    extu.w r0,r6
    .org 0xc0084-ORIGIN
L_000c0084:
    shlr2 r6
    .org 0xc0086-ORIGIN
L_000c0086:
    cmp/gt r2,r6
    .org 0xc0088-ORIGIN
L_000c0088:
    bf L_000c0126
    .org 0xc008a-ORIGIN
L_000c008a:
    bra L_000c0126
    .org 0xc008c-ORIGIN
L_000c008c:
    mov #-0x1,r6
    .org 0xc008e-ORIGIN
L_000c008e:
    mov.l L_000c0274,r2
    .org 0xc0090-ORIGIN
L_000c0090:
    bra L_000c0146
    .org 0xc0092-ORIGIN
L_000c0092:
    mov.b @r2,r12
    .org 0xc0094-ORIGIN
L_000c0094:
    mov.b @r13,r0
    .org 0xc0096-ORIGIN
L_000c0096:
    tst #0x8,r0
    .org 0xc0098-ORIGIN
L_000c0098:
    bt L_000c00a0
    .org 0xc009a-ORIGIN
L_000c009a:
    mov r5,r0
    .org 0xc009c-ORIGIN
L_000c009c:
    tst #0x1,r0
    .org 0xc009e-ORIGIN
L_000c009e:
    bt L_000c00a0
    .org 0xc00a0-ORIGIN
L_000c00a0:
    mov.l L_000c0278,r2
    .org 0xc00a2-ORIGIN
L_000c00a2:
    mov.b @r2,r7
    .org 0xc00a4-ORIGIN
L_000c00a4:
    mov.l L_000c027c,r2
    .org 0xc00a6-ORIGIN
L_000c00a6:
    extu.b r7,r7
    .org 0xc00a8-ORIGIN
L_000c00a8:
    mov.b @r2,r4
    .org 0xc00aa-ORIGIN
L_000c00aa:
    extu.b r4,r4
    .org 0xc00ac-ORIGIN
L_000c00ac:
    cmp/ge r4,r7
    .org 0xc00ae-ORIGIN
L_000c00ae:
    bt L_000c012a
    .org 0xc00b0-ORIGIN
L_000c00b0:
    mov.l L_000c0280,r6
    .org 0xc00b2-ORIGIN
L_000c00b2:
    mov.b @(0x7,r6),r0
    .org 0xc00b4-ORIGIN
L_000c00b4:
    extu.b r0,r5
    .org 0xc00b6-ORIGIN
L_000c00b6:
    cmp/gt r4,r5
    .org 0xc00b8-ORIGIN
L_000c00b8:
    bt L_000c0140
    .org 0xc00ba-ORIGIN
L_000c00ba:
    mov.l L_000c0280,r3
    .org 0xc00bc-ORIGIN
L_000c00bc:
    mov.b @(0x7,r3),r0
    .org 0xc00be-ORIGIN
L_000c00be:
    extu.b r0,r2
    .org 0xc00c0-ORIGIN
L_000c00c0:
    cmp/gt r7,r2
    .org 0xc00c2-ORIGIN
L_000c00c2:
    bt L_000c00d2
    .org 0xc00c4-ORIGIN
L_000c00c4:
    mov.l L_000c0284,r2
    .org 0xc00c6-ORIGIN
L_000c00c6:
    mov.w L_000c00cc,r0
    .org 0xc00c8-ORIGIN
L_000c00c8:
    bra L_000c00ce
    .org 0xc00ca-ORIGIN
L_000c00ca:
    mov.b @(r0,r2),r12
    .org 0xc00cc-ORIGIN
L_000c00cc:
    .word 0x09d3
    .org 0xc00ce-ORIGIN
L_000c00ce:
    bra L_000c0146
    .org 0xc00d0-ORIGIN
L_000c00d0:
    nop
    .org 0xc00d2-ORIGIN
L_000c00d2:
    mov.l L_000c0284,r3
    .org 0xc00d4-ORIGIN
L_000c00d4:
    mov.w L_000c01e6,r0
    .org 0xc00d6-ORIGIN
L_000c00d6:
    mov.l L_000c0280,r1
    .org 0xc00d8-ORIGIN
L_000c00d8:
    mov.b @(r0,r3),r6
    .org 0xc00da-ORIGIN
L_000c00da:
    mov.w L_000c01e8,r0
    .org 0xc00dc-ORIGIN
L_000c00dc:
    extu.b r6,r2
    .org 0xc00de-ORIGIN
L_000c00de:
    mov.l r7,@(0xc,r15)
    .org 0xc00e0-ORIGIN
L_000c00e0:
    mov.b @(r0,r3),r6
    .org 0xc00e2-ORIGIN
L_000c00e2:
    mov.b @(0x7,r1),r0
    .org 0xc00e4-ORIGIN
L_000c00e4:
    mov.l r2,@(0x14,r15)
    .org 0xc00e6-ORIGIN
L_000c00e6:
    extu.b r6,r2
    .org 0xc00e8-ORIGIN
L_000c00e8:
    extu.b r0,r5
    .org 0xc00ea-ORIGIN
L_000c00ea:
    mov.w L_000c01e8,r0
    .org 0xc00ec-ORIGIN
L_000c00ec:
    mov.l r2,@(0x8,r15)
    .org 0xc00ee-ORIGIN
L_000c00ee:
    mov r4,r6
    .org 0xc00f0-ORIGIN
L_000c00f0:
    mov.b @(r0,r3),r2
    .org 0xc00f2-ORIGIN
L_000c00f2:
    sub r7,r5
    .org 0xc00f4-ORIGIN
L_000c00f4:
    sub r7,r6
    .org 0xc00f6-ORIGIN
L_000c00f6:
    extu.b r2,r4
    .org 0xc00f8-ORIGIN
L_000c00f8:
    mov.l @(0x14,r15),r2
    .org 0xc00fa-ORIGIN
L_000c00fa:
    mov.l r4,@(0x10,r15)
    .org 0xc00fc-ORIGIN
L_000c00fc:
    mov r6,r0
    .org 0xc00fe-ORIGIN
L_000c00fe:
    mov.l @(0x8,r15),r4
    .org 0xc0100-ORIGIN
L_000c0100:
    sub r4,r2
    .org 0xc0102-ORIGIN
L_000c0102:
    mov.l L_000c0288,r4
    .org 0xc0104-ORIGIN
L_000c0104:
    mov.l r2,@(0x14,r15)
    .org 0xc0106-ORIGIN
L_000c0106:
    mul.l r2,r5
    .org 0xc0108-ORIGIN
L_000c0108:
    sts macl,r5
    .org 0xc010a-ORIGIN
L_000c010a:
    jsr @r4
    .org 0xc010c-ORIGIN
L_000c010c:
    mov r5,r1
    .org 0xc010e-ORIGIN
L_000c010e:
    mov.l @(0x10,r15),r2
    .org 0xc0110-ORIGIN
L_000c0110:
    add r2,r0
    .org 0xc0112-ORIGIN
L_000c0112:
    cmp/pz r0
    .org 0xc0114-ORIGIN
L_000c0114:
    bt/s L_000c011a
    .org 0xc0116-ORIGIN
L_000c0116:
    mov r0,r5
    .org 0xc0118-ORIGIN
L_000c0118:
    mov #0x0,r5
    .org 0xc011a-ORIGIN
L_000c011a:
    mov #-0x1,r2
    .org 0xc011c-ORIGIN
L_000c011c:
    extu.b r2,r2
    .org 0xc011e-ORIGIN
L_000c011e:
    cmp/gt r2,r5
    .org 0xc0120-ORIGIN
L_000c0120:
    bf/s L_000c0126
    .org 0xc0122-ORIGIN
L_000c0122:
    mov r5,r6
    .org 0xc0124-ORIGIN
L_000c0124:
    mov #-0x1,r6
    .org 0xc0126-ORIGIN
L_000c0126:
    bra L_000c0146
    .org 0xc0128-ORIGIN
L_000c0128:
    mov r6,r12
    .org 0xc012a-ORIGIN
L_000c012a:
    mov.l L_000c0280,r3
    .org 0xc012c-ORIGIN
L_000c012c:
    mov.b @(0x7,r3),r0
    .org 0xc012e-ORIGIN
L_000c012e:
    extu.b r0,r5
    .org 0xc0130-ORIGIN
L_000c0130:
    cmp/gt r4,r5
    .org 0xc0132-ORIGIN
L_000c0132:
    bt L_000c0140
    .org 0xc0134-ORIGIN
L_000c0134:
    cmp/gt r7,r5
    .org 0xc0136-ORIGIN
L_000c0136:
    bt L_000c0146
    .org 0xc0138-ORIGIN
L_000c0138:
    mov.l L_000c0284,r6
    .org 0xc013a-ORIGIN
L_000c013a:
    mov.w L_000c01e8,r0
    .org 0xc013c-ORIGIN
L_000c013c:
    bra L_000c0146
    .org 0xc013e-ORIGIN
L_000c013e:
    mov.b @(r0,r6),r12
    .org 0xc0140-ORIGIN
L_000c0140:
    mov.l L_000c0284,r2
    .org 0xc0142-ORIGIN
L_000c0142:
    mov.w L_000c01e6,r0
    .org 0xc0144-ORIGIN
L_000c0144:
    mov.b @(r0,r2),r12
    .org 0xc0146-ORIGIN
L_000c0146:
    mov r12,r0
    .org 0xc0148-ORIGIN
L_000c0148:
    mov.b r0,@(0xee,gbr)
    .org 0xc014a-ORIGIN
L_000c014a:
    mov r11,r0
    .org 0xc014c-ORIGIN
L_000c014c:
    and #0x4,r0
    .org 0xc014e-ORIGIN
L_000c014e:
    tst r0,r0
    .org 0xc0150-ORIGIN
L_000c0150:
    bt/s L_000c0176
    .org 0xc0152-ORIGIN
L_000c0152:
    mov r0,r11
    .org 0xc0154-ORIGIN
L_000c0154:
    mov #0x43,r0
    .org 0xc0156-ORIGIN
L_000c0156:
    mov.b @(r0,r13),r0
    .org 0xc0158-ORIGIN
L_000c0158:
    tst #0x1,r0
    .org 0xc015a-ORIGIN
L_000c015a:
    bt L_000c0176
    .org 0xc015c-ORIGIN
L_000c015c:
    tst #0x2,r0
    .org 0xc015e-ORIGIN
L_000c015e:
    bt L_000c0176
    .org 0xc0160-ORIGIN
L_000c0160:
    mov #0x44,r0
    .org 0xc0162-ORIGIN
L_000c0162:
    mov.b @(r0,r13),r0
    .org 0xc0164-ORIGIN
L_000c0164:
    tst #0x80,r0
    .org 0xc0166-ORIGIN
L_000c0166:
    bt L_000c0176
    .org 0xc0168-ORIGIN
L_000c0168:
    mov.l L_000c028c,r5
    .org 0xc016a-ORIGIN
L_000c016a:
    mov.b @r5,r0
    .org 0xc016c-ORIGIN
L_000c016c:
    tst #0x4,r0
    .org 0xc016e-ORIGIN
L_000c016e:
    bt L_000c0176
    .org 0xc0170-ORIGIN
L_000c0170:
    mov r14,r0
    .org 0xc0172-ORIGIN
L_000c0172:
    bra L_000c017a
    .org 0xc0174-ORIGIN
L_000c0174:
    or #0x2,r0
    .org 0xc0176-ORIGIN
L_000c0176:
    mov r14,r0
    .org 0xc0178-ORIGIN
L_000c0178:
    and #0xfd,r0
    .org 0xc017a-ORIGIN
L_000c017a:
    tst r11,r11
    .org 0xc017c-ORIGIN
L_000c017c:
    bf/s L_000c018e
    .org 0xc017e-ORIGIN
L_000c017e:
    mov.b r0,@(0x4,r13)
    .org 0xc0180-ORIGIN
L_000c0180:
    mov #0x10,r0
    .org 0xc0182-ORIGIN
L_000c0182:
    mov.b @(r0,r13),r0
    .org 0xc0184-ORIGIN
L_000c0184:
    and #0xef,r0
    .org 0xc0186-ORIGIN
L_000c0186:
    mov r0,r6
    .org 0xc0188-ORIGIN
L_000c0188:
    mov #0x10,r0
    .org 0xc018a-ORIGIN
L_000c018a:
    bra L_000c01ea
    .org 0xc018c-ORIGIN
L_000c018c:
    mov.b r6,@(r0,r13)
    .org 0xc018e-ORIGIN
L_000c018e:
    mov.b @(0x4,r13),r0
    .org 0xc0190-ORIGIN
L_000c0190:
    tst #0x2,r0
    .org 0xc0192-ORIGIN
L_000c0192:
    bt L_000c01ce
    .org 0xc0194-ORIGIN
L_000c0194:
    mov #0x10,r0
    .org 0xc0196-ORIGIN
L_000c0196:
    mov.b @(r0,r13),r7
    .org 0xc0198-ORIGIN
L_000c0198:
    mov r7,r0
    .org 0xc019a-ORIGIN
L_000c019a:
    tst #0x10,r0
    .org 0xc019c-ORIGIN
L_000c019c:
    bf L_000c01ce
    .org 0xc019e-ORIGIN
L_000c019e:
    mov.l L_000c0290,r3
    .org 0xc01a0-ORIGIN
L_000c01a0:
    mov #-0x80,r2
    .org 0xc01a2-ORIGIN
L_000c01a2:
    extu.b r2,r2
    .org 0xc01a4-ORIGIN
L_000c01a4:
    mov.b @r3,r4
    .org 0xc01a6-ORIGIN
L_000c01a6:
    extu.b r4,r6
    .org 0xc01a8-ORIGIN
L_000c01a8:
    mov r6,r5
    .org 0xc01aa-ORIGIN
L_000c01aa:
    add r2,r5
    .org 0xc01ac-ORIGIN
L_000c01ac:
    add #0x7f,r2
    .org 0xc01ae-ORIGIN
L_000c01ae:
    cmp/gt r2,r5
    .org 0xc01b0-ORIGIN
L_000c01b0:
    bf L_000c01b6
    .org 0xc01b2-ORIGIN
L_000c01b2:
    bra L_000c01ba
    .org 0xc01b4-ORIGIN
L_000c01b4:
    mov #-0x1,r6
    .org 0xc01b6-ORIGIN
L_000c01b6:
    mov #-0x80,r2
    .org 0xc01b8-ORIGIN
L_000c01b8:
    add r2,r6
    .org 0xc01ba-ORIGIN
L_000c01ba:
    mov.l L_000c0294,r4
    .org 0xc01bc-ORIGIN
L_000c01bc:
    mov.b @(0x5,r4),r0
    .org 0xc01be-ORIGIN
L_000c01be:
    tst #0x10,r0
    .org 0xc01c0-ORIGIN
L_000c01c0:
    bt L_000c01ec
    .org 0xc01c2-ORIGIN
L_000c01c2:
    mov #0x10,r0
    .org 0xc01c4-ORIGIN
L_000c01c4:
    or r0,r7
    .org 0xc01c6-ORIGIN
L_000c01c6:
    mov #0x10,r0
    .org 0xc01c8-ORIGIN
L_000c01c8:
    mov.b r7,@(r0,r13)
    .org 0xc01ca-ORIGIN
L_000c01ca:
    bra L_000c01ec
    .org 0xc01cc-ORIGIN
L_000c01cc:
    mov #-0x80,r6
    .org 0xc01ce-ORIGIN
L_000c01ce:
    mov.b @(0x7,r13),r0
    .org 0xc01d0-ORIGIN
L_000c01d0:
    tst #0x2,r0
    .org 0xc01d2-ORIGIN
L_000c01d2:
    bt L_000c01d8
    .org 0xc01d4-ORIGIN
L_000c01d4:
    bra L_000c01ec
    .org 0xc01d6-ORIGIN
L_000c01d6:
    mov #-0x80,r6
    .org 0xc01d8-ORIGIN
L_000c01d8:
    mov #0x10,r0
    .org 0xc01da-ORIGIN
L_000c01da:
    mov.b @(r0,r13),r0
    .org 0xc01dc-ORIGIN
L_000c01dc:
    tst #0x10,r0
    .org 0xc01de-ORIGIN
L_000c01de:
    bt L_000c01ea
    .org 0xc01e0-ORIGIN
L_000c01e0:
    mov.b @(0xf2,gbr),r0
    .org 0xc01e2-ORIGIN
L_000c01e2:
    bra L_000c01ec
    .org 0xc01e4-ORIGIN
L_000c01e4:
    mov r0,r6
    .org 0xc01e6-ORIGIN
L_000c01e6:
    .word 0x09d1
    .org 0xc01e8-ORIGIN
L_000c01e8:
    .word 0x09d3
    .org 0xc01ea-ORIGIN
L_000c01ea:
    mov r12,r6
    .org 0xc01ec-ORIGIN
L_000c01ec:
    extu.b r6,r4
    .org 0xc01ee-ORIGIN
L_000c01ee:
    tst r11,r11
    .org 0xc01f0-ORIGIN
L_000c01f0:
    mov r4,r0
    .org 0xc01f2-ORIGIN
L_000c01f2:
    bt/s L_000c0234
    .org 0xc01f4-ORIGIN
L_000c01f4:
    mov.b r0,@(0xf2,gbr)
    .org 0xc01f6-ORIGIN
L_000c01f6:
    mov.l L_000c0298,r2
    .org 0xc01f8-ORIGIN
L_000c01f8:
    mov.b @r2,r7
    .org 0xc01fa-ORIGIN
L_000c01fa:
    extu.b r7,r7
    .org 0xc01fc-ORIGIN
L_000c01fc:
    cmp/ge r7,r4
    .org 0xc01fe-ORIGIN
L_000c01fe:
    bf L_000c0234
    .org 0xc0200-ORIGIN
L_000c0200:
    mov.l L_000c0284,r2
    .org 0xc0202-ORIGIN
L_000c0202:
    mov.w L_000c0266,r0
    .org 0xc0204-ORIGIN
L_000c0204:
    mov.b @(r0,r2),r5
    .org 0xc0206-ORIGIN
L_000c0206:
    mov #-0x1,r2
    .org 0xc0208-ORIGIN
L_000c0208:
    extu.b r2,r2
    .org 0xc020a-ORIGIN
L_000c020a:
    extu.b r5,r5
    .org 0xc020c-ORIGIN
L_000c020c:
    mov r5,r6
    .org 0xc020e-ORIGIN
L_000c020e:
    add #0x1,r6
    .org 0xc0210-ORIGIN
L_000c0210:
    cmp/gt r2,r6
    .org 0xc0212-ORIGIN
L_000c0212:
    bf L_000c0218
    .org 0xc0214-ORIGIN
L_000c0214:
    bra L_000c021c
    .org 0xc0216-ORIGIN
L_000c0216:
    mov #-0x1,r6
    .org 0xc0218-ORIGIN
L_000c0218:
    add #0x1,r5
    .org 0xc021a-ORIGIN
L_000c021a:
    mov r5,r6
    .org 0xc021c-ORIGIN
L_000c021c:
    mov.l L_000c0284,r3
    .org 0xc021e-ORIGIN
L_000c021e:
    extu.b r6,r5
    .org 0xc0220-ORIGIN
L_000c0220:
    mov.w L_000c0266,r0
    .org 0xc0222-ORIGIN
L_000c0222:
    mov.l L_000c029c,r2
    .org 0xc0224-ORIGIN
L_000c0224:
    mov.b r6,@(r0,r3)
    .org 0xc0226-ORIGIN
L_000c0226:
    mov.b @r2,r6
    .org 0xc0228-ORIGIN
L_000c0228:
    extu.b r6,r6
    .org 0xc022a-ORIGIN
L_000c022a:
    cmp/gt r6,r5
    .org 0xc022c-ORIGIN
L_000c022c:
    bt/s L_000c023e
    .org 0xc022e-ORIGIN
L_000c022e:
    mov r4,r5
    .org 0xc0230-ORIGIN
L_000c0230:
    bra L_000c023e
    .org 0xc0232-ORIGIN
L_000c0232:
    mov r7,r5
    .org 0xc0234-ORIGIN
L_000c0234:
    mov.l L_000c0284,r6
    .org 0xc0236-ORIGIN
L_000c0236:
    mov #0x0,r2
    .org 0xc0238-ORIGIN
L_000c0238:
    mov.w L_000c0266,r0
    .org 0xc023a-ORIGIN
L_000c023a:
    mov r4,r5
    .org 0xc023c-ORIGIN
L_000c023c:
    mov.b r2,@(r0,r6)
    .org 0xc023e-ORIGIN
L_000c023e:
    extu.b r5,r4
    .org 0xc0240-ORIGIN
L_000c0240:
    mov.l L_000c026c,r3
    .org 0xc0242-ORIGIN
L_000c0242:
    mov.l L_000c02a0,r2
    .org 0xc0244-ORIGIN
L_000c0244:
    mov r4,r0
    .org 0xc0246-ORIGIN
L_000c0246:
    mov.b r0,@(0xf3,gbr)
    .org 0xc0248-ORIGIN
L_000c0248:
    mov #0x7a,r0
    .org 0xc024a-ORIGIN
L_000c024a:
    mov.b @(r0,r3),r5
    .org 0xc024c-ORIGIN
L_000c024c:
    mov.b @r2,r6
    .org 0xc024e-ORIGIN
L_000c024e:
    cmp/hi r6,r5
    .org 0xc0250-ORIGIN
L_000c0250:
    bt L_000c025a
    .org 0xc0252-ORIGIN
L_000c0252:
    mov #0x40,r0
    .org 0xc0254-ORIGIN
L_000c0254:
    mov.b @(r0,r13),r0
    .org 0xc0256-ORIGIN
L_000c0256:
    tst #0x2,r0
    .org 0xc0258-ORIGIN
L_000c0258:
    bt L_000c0260
    .org 0xc025a-ORIGIN
L_000c025a:
    mov.b @r13,r0
    .org 0xc025c-ORIGIN
L_000c025c:
    tst #0x8,r0
    .org 0xc025e-ORIGIN
L_000c025e:
    bt L_000c02a4
    .org 0xc0260-ORIGIN
L_000c0260:
    mov.b @(0x4,r15),r0
    .org 0xc0262-ORIGIN
L_000c0262:
    bra L_000c02b0
    .org 0xc0264-ORIGIN
L_000c0264:
    and #0x7f,r0
    .org 0xc0266-ORIGIN
L_000c0266:
    .word 0x06c8
    .org 0xc0268-ORIGIN
L_000c0268:
    .long 0x00008b42
    .org 0xc026c-ORIGIN
L_000c026c:
    .long 0xffff1094
    .org 0xc0270-ORIGIN
L_000c0270:
    .long 0xffff1000
    .org 0xc0274-ORIGIN
L_000c0274:
    .long 0x0000851e
    .org 0xc0278-ORIGIN
L_000c0278:
    .long 0x00008d2e
    .org 0xc027c-ORIGIN
L_000c027c:
    .long 0x00008d2d
    .org 0xc0280-ORIGIN
L_000c0280:
    .long 0xffff106a
    .org 0xc0284-ORIGIN
L_000c0284:
    .long 0xffff128c
    .org 0xc0288-ORIGIN
L_000c0288:
    .long 0x00021bbc
    .org 0xc028c-ORIGIN
L_000c028c:
    .long 0xffff244f
    .org 0xc0290-ORIGIN
L_000c0290:
    .long 0x00008e36
    .org 0xc0294-ORIGIN
L_000c0294:
    .long 0xffff24ce
    .org 0xc0298-ORIGIN
L_000c0298:
    .long 0x00008de4
    .org 0xc029c-ORIGIN
L_000c029c:
    .long 0x00008e1e
    .org 0xc02a0-ORIGIN
L_000c02a0:
    .long 0x00008e29
    .org 0xc02a4-ORIGIN
L_000c02a4:
    mov #0x40,r0
    .org 0xc02a6-ORIGIN
L_000c02a6:
    mov.b @(r0,r13),r0
    .org 0xc02a8-ORIGIN
L_000c02a8:
    tst #0x2,r0
    .org 0xc02aa-ORIGIN
L_000c02aa:
    bt L_000c02ba
    .org 0xc02ac-ORIGIN
L_000c02ac:
    mov.b @(0x4,r15),r0
    .org 0xc02ae-ORIGIN
L_000c02ae:
    or #0x80,r0
    .org 0xc02b0-ORIGIN
L_000c02b0:
    mov r0,r2
    .org 0xc02b2-ORIGIN
L_000c02b2:
    mov.b r0,@(0x4,r15)
    .org 0xc02b4-ORIGIN
L_000c02b4:
    mov #0x41,r0
    .org 0xc02b6-ORIGIN
L_000c02b6:
    mov.b r2,@(r0,r13)
    .org 0xc02b8-ORIGIN
L_000c02b8:
    exts.b r2,r10
    .org 0xc02ba-ORIGIN
L_000c02ba:
    mov r10,r0
    .org 0xc02bc-ORIGIN
L_000c02bc:
    tst #0x80,r0
    .org 0xc02be-ORIGIN
L_000c02be:
    bf L_000c02d4
    .org 0xc02c0-ORIGIN
L_000c02c0:
    mov.l L_000c04f0,r2
    .org 0xc02c2-ORIGIN
L_000c02c2:
    mov r4,r0
    .org 0xc02c4-ORIGIN
L_000c02c4:
    mov.l L_000c04f4,r6
    .org 0xc02c6-ORIGIN
L_000c02c6:
    mov.b r0,@(0xe,r2)
    .org 0xc02c8-ORIGIN
L_000c02c8:
    mov.b @(0x2,r6),r0
    .org 0xc02ca-ORIGIN
L_000c02ca:
    mov.l L_000c04f8,r6
    .org 0xc02cc-ORIGIN
L_000c02cc:
    mov r0,r2
    .org 0xc02ce-ORIGIN
L_000c02ce:
    mov #0x6b,r0
    .org 0xc02d0-ORIGIN
L_000c02d0:
    bra L_000c032a
    .org 0xc02d2-ORIGIN
L_000c02d2:
    mov.b r2,@(r0,r6)
    .org 0xc02d4-ORIGIN
L_000c02d4:
    mov.l L_000c04f8,r6
    .org 0xc02d6-ORIGIN
L_000c02d6:
    mov #0x6b,r0
    .org 0xc02d8-ORIGIN
L_000c02d8:
    mov.b @(r0,r6),r2
    .org 0xc02da-ORIGIN
L_000c02da:
    tst r2,r2
    .org 0xc02dc-ORIGIN
L_000c02dc:
    mov.l L_000c04f0,r2
    .org 0xc02de-ORIGIN
L_000c02de:
    mov.b @(0xe,r2),r0
    .org 0xc02e0-ORIGIN
L_000c02e0:
    bt/s L_000c02ee
    .org 0xc02e2-ORIGIN
L_000c02e2:
    extu.b r0,r7
    .org 0xc02e4-ORIGIN
L_000c02e4:
    cmp/gt r7,r4
    .org 0xc02e6-ORIGIN
L_000c02e6:
    bf/s L_000c0312
    .org 0xc02e8-ORIGIN
L_000c02e8:
    mov r4,r6
    .org 0xc02ea-ORIGIN
L_000c02ea:
    bra L_000c0312
    .org 0xc02ec-ORIGIN
L_000c02ec:
    mov r7,r6
    .org 0xc02ee-ORIGIN
L_000c02ee:
    mov r7,r2
    .org 0xc02f0-ORIGIN
L_000c02f0:
    add #-0x1,r2
    .org 0xc02f2-ORIGIN
L_000c02f2:
    cmp/pz r2
    .org 0xc02f4-ORIGIN
L_000c02f4:
    bt L_000c02fa
    .org 0xc02f6-ORIGIN
L_000c02f6:
    bra L_000c02fe
    .org 0xc02f8-ORIGIN
L_000c02f8:
    mov #0x0,r2
    .org 0xc02fa-ORIGIN
L_000c02fa:
    mov r7,r2
    .org 0xc02fc-ORIGIN
L_000c02fc:
    add #-0x1,r2
    .org 0xc02fe-ORIGIN
L_000c02fe:
    extu.b r2,r6
    .org 0xc0300-ORIGIN
L_000c0300:
    cmp/gt r6,r4
    .org 0xc0302-ORIGIN
L_000c0302:
    bt L_000c0306
    .org 0xc0304-ORIGIN
L_000c0304:
    mov r4,r6
    .org 0xc0306-ORIGIN
L_000c0306:
    mov #-0x80,r5
    .org 0xc0308-ORIGIN
L_000c0308:
    extu.b r6,r6
    .org 0xc030a-ORIGIN
L_000c030a:
    extu.b r5,r5
    .org 0xc030c-ORIGIN
L_000c030c:
    cmp/ge r5,r6
    .org 0xc030e-ORIGIN
L_000c030e:
    bt L_000c0312
    .org 0xc0310-ORIGIN
L_000c0310:
    mov #-0x80,r6
    .org 0xc0312-ORIGIN
L_000c0312:
    extu.b r6,r4
    .org 0xc0314-ORIGIN
L_000c0314:
    cmp/eq r7,r4
    .org 0xc0316-ORIGIN
L_000c0316:
    bt L_000c0324
    .org 0xc0318-ORIGIN
L_000c0318:
    mov.l L_000c04f4,r6
    .org 0xc031a-ORIGIN
L_000c031a:
    mov.l L_000c04f8,r3
    .org 0xc031c-ORIGIN
L_000c031c:
    mov.b @(0x2,r6),r0
    .org 0xc031e-ORIGIN
L_000c031e:
    mov r0,r2
    .org 0xc0320-ORIGIN
L_000c0320:
    mov #0x6b,r0
    .org 0xc0322-ORIGIN
L_000c0322:
    mov.b r2,@(r0,r3)
    .org 0xc0324-ORIGIN
L_000c0324:
    mov.l L_000c04f0,r3
    .org 0xc0326-ORIGIN
L_000c0326:
    mov r4,r0
    .org 0xc0328-ORIGIN
L_000c0328:
    mov.b r0,@(0xe,r3)
    .org 0xc032a-ORIGIN
L_000c032a:
    mov.l L_000c04fc,r2
    .org 0xc032c-ORIGIN
L_000c032c:
    extu.b r4,r4
    .org 0xc032e-ORIGIN
L_000c032e:
    mov.b @(0xe,r2),r0
    .org 0xc0330-ORIGIN
L_000c0330:
    extu.b r0,r7
    .org 0xc0332-ORIGIN
L_000c0332:
    mov r9,r0
    .org 0xc0334-ORIGIN
L_000c0334:
    cmp/ge r7,r4
    .org 0xc0336-ORIGIN
L_000c0336:
    bf/s L_000c033c
    .org 0xc0338-ORIGIN
L_000c0338:
    and #0xfd,r0
    .org 0xc033a-ORIGIN
L_000c033a:
    or #0x2,r0
    .org 0xc033c-ORIGIN
L_000c033c:
    mov.l L_000c0500,r6
    .org 0xc033e-ORIGIN
L_000c033e:
    mov r4,r14
    .org 0xc0340-ORIGIN
L_000c0340:
    mov r0,r9
    .org 0xc0342-ORIGIN
L_000c0342:
    mov #0x1a,r0
    .org 0xc0344-ORIGIN
L_000c0344:
    mov.b @r6,r2
    .org 0xc0346-ORIGIN
L_000c0346:
    mov.b r9,@(r0,r13)
    .org 0xc0348-ORIGIN
L_000c0348:
    extu.b r2,r2
    .org 0xc034a-ORIGIN
L_000c034a:
    sub r2,r14
    .org 0xc034c-ORIGIN
L_000c034c:
    mov.l L_000c0504,r2
    .org 0xc034e-ORIGIN
L_000c034e:
    mov.b @r2,r5
    .org 0xc0350-ORIGIN
L_000c0350:
    extu.b r5,r5
    .org 0xc0352-ORIGIN
L_000c0352:
    neg r5,r6
    .org 0xc0354-ORIGIN
L_000c0354:
    cmp/gt r6,r14
    .org 0xc0356-ORIGIN
L_000c0356:
    bf L_000c0374
    .org 0xc0358-ORIGIN
L_000c0358:
    cmp/gt r14,r5
    .org 0xc035a-ORIGIN
L_000c035a:
    bf L_000c0374
    .org 0xc035c-ORIGIN
L_000c035c:
    mov.l L_000c0508,r3
    .org 0xc035e-ORIGIN
L_000c035e:
    mov #0x66,r0
    .org 0xc0360-ORIGIN
L_000c0360:
    shll2 r0
    .org 0xc0362-ORIGIN
L_000c0362:
    mov.b @(r0,r3),r12
    .org 0xc0364-ORIGIN
L_000c0364:
    mov #-0x2,r6
    .org 0xc0366-ORIGIN
L_000c0366:
    mov #0x66,r0
    .org 0xc0368-ORIGIN
L_000c0368:
    extu.b r12,r12
    .org 0xc036a-ORIGIN
L_000c036a:
    and r6,r12
    .org 0xc036c-ORIGIN
L_000c036c:
    shll2 r0
    .org 0xc036e-ORIGIN
L_000c036e:
    mov.b r12,@(r0,r3)
    .org 0xc0370-ORIGIN
L_000c0370:
    bra L_000c03ca
    .org 0xc0372-ORIGIN
L_000c0372:
    nop
    .org 0xc0374-ORIGIN
L_000c0374:
    mov.l L_000c0508,r3
    .org 0xc0376-ORIGIN
L_000c0376:
    mov #0x66,r0
    .org 0xc0378-ORIGIN
L_000c0378:
    shll2 r0
    .org 0xc037a-ORIGIN
L_000c037a:
    mov.b @(r0,r3),r12
    .org 0xc037c-ORIGIN
L_000c037c:
    extu.b r12,r12
    .org 0xc037e-ORIGIN
L_000c037e:
    mov r12,r0
    .org 0xc0380-ORIGIN
L_000c0380:
    tst #0x1,r0
    .org 0xc0382-ORIGIN
L_000c0382:
    bf L_000c03ca
    .org 0xc0384-ORIGIN
L_000c0384:
    mov.l L_000c050c,r2
    .org 0xc0386-ORIGIN
L_000c0386:
    mov r4,r14
    .org 0xc0388-ORIGIN
L_000c0388:
    sub r7,r14
    .org 0xc038a-ORIGIN
L_000c038a:
    mov.b @r2,r6
    .org 0xc038c-ORIGIN
L_000c038c:
    extu.b r6,r6
    .org 0xc038e-ORIGIN
L_000c038e:
    cmp/ge r6,r14
    .org 0xc0390-ORIGIN
L_000c0390:
    bf L_000c03ac
    .org 0xc0392-ORIGIN
L_000c0392:
    mov.l L_000c0508,r6
    .org 0xc0394-ORIGIN
L_000c0394:
    mov.w L_000c03f0,r0
    .org 0xc0396-ORIGIN
L_000c0396:
    mov.b @(r0,r6),r0
    .org 0xc0398-ORIGIN
L_000c0398:
    or #0x1,r0
    .org 0xc039a-ORIGIN
L_000c039a:
    mov r0,r2
    .org 0xc039c-ORIGIN
L_000c039c:
    mov.w L_000c03f0,r0
    .org 0xc039e-ORIGIN
L_000c039e:
    mov.b r2,@(r0,r6)
    .org 0xc03a0-ORIGIN
L_000c03a0:
    mov #0x1,r0
    .org 0xc03a2-ORIGIN
L_000c03a2:
    or r0,r12
    .org 0xc03a4-ORIGIN
L_000c03a4:
    mov #0x66,r0
    .org 0xc03a6-ORIGIN
L_000c03a6:
    shll2 r0
    .org 0xc03a8-ORIGIN
L_000c03a8:
    bra L_000c03ca
    .org 0xc03aa-ORIGIN
L_000c03aa:
    mov.b r12,@(r0,r6)
    .org 0xc03ac-ORIGIN
L_000c03ac:
    neg r6,r2
    .org 0xc03ae-ORIGIN
L_000c03ae:
    cmp/ge r2,r14
    .org 0xc03b0-ORIGIN
L_000c03b0:
    bt L_000c03ca
    .org 0xc03b2-ORIGIN
L_000c03b2:
    mov.l L_000c0508,r1
    .org 0xc03b4-ORIGIN
L_000c03b4:
    mov #-0x2,r3
    .org 0xc03b6-ORIGIN
L_000c03b6:
    mov.w L_000c03f0,r0
    .org 0xc03b8-ORIGIN
L_000c03b8:
    mov.b @(r0,r1),r2
    .org 0xc03ba-ORIGIN
L_000c03ba:
    extu.b r2,r2
    .org 0xc03bc-ORIGIN
L_000c03bc:
    and r3,r2
    .org 0xc03be-ORIGIN
L_000c03be:
    mov.b r2,@(r0,r1)
    .org 0xc03c0-ORIGIN
L_000c03c0:
    mov #0x1,r0
    .org 0xc03c2-ORIGIN
L_000c03c2:
    or r0,r12
    .org 0xc03c4-ORIGIN
L_000c03c4:
    mov #0x66,r0
    .org 0xc03c6-ORIGIN
L_000c03c6:
    shll2 r0
    .org 0xc03c8-ORIGIN
L_000c03c8:
    mov.b r12,@(r0,r1)
    .org 0xc03ca-ORIGIN
L_000c03ca:
    mov.l L_000c0500,r6
    .org 0xc03cc-ORIGIN
L_000c03cc:
    mov r4,r14
    .org 0xc03ce-ORIGIN
L_000c03ce:
    mov.b @(0x1,r6),r0
    .org 0xc03d0-ORIGIN
L_000c03d0:
    neg r5,r6
    .org 0xc03d2-ORIGIN
L_000c03d2:
    extu.b r0,r2
    .org 0xc03d4-ORIGIN
L_000c03d4:
    sub r2,r14
    .org 0xc03d6-ORIGIN
L_000c03d6:
    cmp/gt r6,r14
    .org 0xc03d8-ORIGIN
L_000c03d8:
    bf L_000c03f2
    .org 0xc03da-ORIGIN
L_000c03da:
    cmp/gt r14,r5
    .org 0xc03dc-ORIGIN
L_000c03dc:
    bf L_000c03f2
    .org 0xc03de-ORIGIN
L_000c03de:
    extu.b r12,r2
    .org 0xc03e0-ORIGIN
L_000c03e0:
    mov.l L_000c0508,r3
    .org 0xc03e2-ORIGIN
L_000c03e2:
    mov #-0x3,r6
    .org 0xc03e4-ORIGIN
L_000c03e4:
    mov #0x66,r0
    .org 0xc03e6-ORIGIN
L_000c03e6:
    and r6,r2
    .org 0xc03e8-ORIGIN
L_000c03e8:
    shll2 r0
    .org 0xc03ea-ORIGIN
L_000c03ea:
    mov.b r2,@(r0,r3)
    .org 0xc03ec-ORIGIN
L_000c03ec:
    bra L_000c043e
    .org 0xc03ee-ORIGIN
L_000c03ee:
    nop
    .org 0xc03f0-ORIGIN
L_000c03f0:
    .word 0x023c
    .org 0xc03f2-ORIGIN
L_000c03f2:
    mov r12,r0
    .org 0xc03f4-ORIGIN
L_000c03f4:
    tst #0x2,r0
    .org 0xc03f6-ORIGIN
L_000c03f6:
    bf L_000c043e
    .org 0xc03f8-ORIGIN
L_000c03f8:
    mov.l L_000c050c,r2
    .org 0xc03fa-ORIGIN
L_000c03fa:
    mov r4,r5
    .org 0xc03fc-ORIGIN
L_000c03fc:
    sub r7,r5
    .org 0xc03fe-ORIGIN
L_000c03fe:
    mov.b @r2,r6
    .org 0xc0400-ORIGIN
L_000c0400:
    extu.b r6,r6
    .org 0xc0402-ORIGIN
L_000c0402:
    cmp/ge r6,r5
    .org 0xc0404-ORIGIN
L_000c0404:
    bf L_000c0420
    .org 0xc0406-ORIGIN
L_000c0406:
    mov.l L_000c0508,r6
    .org 0xc0408-ORIGIN
L_000c0408:
    mov.w L_000c04e8,r0
    .org 0xc040a-ORIGIN
L_000c040a:
    mov.b @(r0,r6),r0
    .org 0xc040c-ORIGIN
L_000c040c:
    or #0x2,r0
    .org 0xc040e-ORIGIN
L_000c040e:
    mov r0,r2
    .org 0xc0410-ORIGIN
L_000c0410:
    mov.w L_000c04e8,r0
    .org 0xc0412-ORIGIN
L_000c0412:
    mov.b r2,@(r0,r6)
    .org 0xc0414-ORIGIN
L_000c0414:
    mov #0x2,r0
    .org 0xc0416-ORIGIN
L_000c0416:
    or r0,r12
    .org 0xc0418-ORIGIN
L_000c0418:
    mov #0x66,r0
    .org 0xc041a-ORIGIN
L_000c041a:
    shll2 r0
    .org 0xc041c-ORIGIN
L_000c041c:
    bra L_000c043e
    .org 0xc041e-ORIGIN
L_000c041e:
    mov.b r12,@(r0,r6)
    .org 0xc0420-ORIGIN
L_000c0420:
    neg r6,r6
    .org 0xc0422-ORIGIN
L_000c0422:
    cmp/ge r6,r5
    .org 0xc0424-ORIGIN
L_000c0424:
    bt L_000c043e
    .org 0xc0426-ORIGIN
L_000c0426:
    mov.l L_000c0508,r7
    .org 0xc0428-ORIGIN
L_000c0428:
    mov #-0x3,r5
    .org 0xc042a-ORIGIN
L_000c042a:
    mov.w L_000c04e8,r0
    .org 0xc042c-ORIGIN
L_000c042c:
    mov.b @(r0,r7),r2
    .org 0xc042e-ORIGIN
L_000c042e:
    extu.b r2,r2
    .org 0xc0430-ORIGIN
L_000c0430:
    and r5,r2
    .org 0xc0432-ORIGIN
L_000c0432:
    mov.b r2,@(r0,r7)
    .org 0xc0434-ORIGIN
L_000c0434:
    mov #0x2,r0
    .org 0xc0436-ORIGIN
L_000c0436:
    or r0,r12
    .org 0xc0438-ORIGIN
L_000c0438:
    mov #0x66,r0
    .org 0xc043a-ORIGIN
L_000c043a:
    shll2 r0
    .org 0xc043c-ORIGIN
L_000c043c:
    mov.b r12,@(r0,r7)
    .org 0xc043e-ORIGIN
L_000c043e:
    mov #-0x80,r6
    .org 0xc0440-ORIGIN
L_000c0440:
    extu.b r6,r6
    .org 0xc0442-ORIGIN
L_000c0442:
    cmp/eq r6,r4
    .org 0xc0444-ORIGIN
L_000c0444:
    bf/s L_000c0452
    .org 0xc0446-ORIGIN
L_000c0446:
    mov r8,r0
    .org 0xc0448-ORIGIN
L_000c0448:
    and #0xfd,r0
    .org 0xc044a-ORIGIN
L_000c044a:
    mov r0,r8
    .org 0xc044c-ORIGIN
L_000c044c:
    mov #0x22,r0
    .org 0xc044e-ORIGIN
L_000c044e:
    bra L_000c04c4
    .org 0xc0450-ORIGIN
L_000c0450:
    mov.b r8,@(r0,r13)
    .org 0xc0452-ORIGIN
L_000c0452:
    or #0x2,r0
    .org 0xc0454-ORIGIN
L_000c0454:
    mov r0,r8
    .org 0xc0456-ORIGIN
L_000c0456:
    mov #0x22,r0
    .org 0xc0458-ORIGIN
L_000c0458:
    mov.b r8,@(r0,r13)
    .org 0xc045a-ORIGIN
L_000c045a:
    mov #0x1a,r0
    .org 0xc045c-ORIGIN
L_000c045c:
    mov.b @(r0,r13),r0
    .org 0xc045e-ORIGIN
L_000c045e:
    tst #0x2,r0
    .org 0xc0460-ORIGIN
L_000c0460:
    bt L_000c0474
    .org 0xc0462-ORIGIN
L_000c0462:
    mov.l L_000c0510,r2
    .org 0xc0464-ORIGIN
L_000c0464:
    mov #0x24,r0
    .org 0xc0466-ORIGIN
L_000c0466:
    mov.l L_000c0514,r3
    .org 0xc0468-ORIGIN
L_000c0468:
    mov.b @r2,r6
    .org 0xc046a-ORIGIN
L_000c046a:
    mov.b @(r0,r3),r2
    .org 0xc046c-ORIGIN
L_000c046c:
    extu.b r6,r6
    .org 0xc046e-ORIGIN
L_000c046e:
    extu.b r2,r2
    .org 0xc0470-ORIGIN
L_000c0470:
    bra L_000c0484
    .org 0xc0472-ORIGIN
L_000c0472:
    mul.l r6,r2
    .org 0xc0474-ORIGIN
L_000c0474:
    mov.l L_000c0518,r2
    .org 0xc0476-ORIGIN
L_000c0476:
    mov #0x24,r0
    .org 0xc0478-ORIGIN
L_000c0478:
    mov.l L_000c0514,r3
    .org 0xc047a-ORIGIN
L_000c047a:
    mov.b @r2,r6
    .org 0xc047c-ORIGIN
L_000c047c:
    mov.b @(r0,r3),r2
    .org 0xc047e-ORIGIN
L_000c047e:
    extu.b r6,r6
    .org 0xc0480-ORIGIN
L_000c0480:
    extu.b r2,r5
    .org 0xc0482-ORIGIN
L_000c0482:
    mul.l r6,r5
    .org 0xc0484-ORIGIN
L_000c0484:
    sts macl,r6
    .org 0xc0486-ORIGIN
L_000c0486:
    mov #-0x1,r2
    .org 0xc0488-ORIGIN
L_000c0488:
    extu.b r2,r2
    .org 0xc048a-ORIGIN
L_000c048a:
    cmp/gt r2,r6
    .org 0xc048c-ORIGIN
L_000c048c:
    bf L_000c0490
    .org 0xc048e-ORIGIN
L_000c048e:
    mov #-0x1,r6
    .org 0xc0490-ORIGIN
L_000c0490:
    mov.l L_000c0508,r3
    .org 0xc0492-ORIGIN
L_000c0492:
    mov r6,r7
    .org 0xc0494-ORIGIN
L_000c0494:
    mov.w L_000c04ea,r0
    .org 0xc0496-ORIGIN
L_000c0496:
    mov r4,r2
    .org 0xc0498-ORIGIN
L_000c0498:
    mov.b r6,@(r0,r3)
    .org 0xc049a-ORIGIN
L_000c049a:
    extu.b r6,r6
    .org 0xc049c-ORIGIN
L_000c049c:
    mov.w L_000c04ec,r0
    .org 0xc049e-ORIGIN
L_000c049e:
    mov.b @(r0,r3),r5
    .org 0xc04a0-ORIGIN
L_000c04a0:
    extu.b r5,r3
    .org 0xc04a2-ORIGIN
L_000c04a2:
    sub r3,r2
    .org 0xc04a4-ORIGIN
L_000c04a4:
    cmp/ge r2,r6
    .org 0xc04a6-ORIGIN
L_000c04a6:
    bt L_000c04c4
    .org 0xc04a8-ORIGIN
L_000c04a8:
    mov.l L_000c0508,r3
    .org 0xc04aa-ORIGIN
L_000c04aa:
    extu.b r7,r7
    .org 0xc04ac-ORIGIN
L_000c04ac:
    mov #-0x1,r6
    .org 0xc04ae-ORIGIN
L_000c04ae:
    mov.b @(r0,r3),r2
    .org 0xc04b0-ORIGIN
L_000c04b0:
    extu.b r6,r6
    .org 0xc04b2-ORIGIN
L_000c04b2:
    extu.b r2,r2
    .org 0xc04b4-ORIGIN
L_000c04b4:
    add r7,r2
    .org 0xc04b6-ORIGIN
L_000c04b6:
    cmp/gt r6,r2
    .org 0xc04b8-ORIGIN
L_000c04b8:
    bf L_000c04be
    .org 0xc04ba-ORIGIN
L_000c04ba:
    mov #-0x1,r6
    .org 0xc04bc-ORIGIN
L_000c04bc:
    extu.b r6,r2
    .org 0xc04be-ORIGIN
L_000c04be:
    mov r2,r7
    .org 0xc04c0-ORIGIN
L_000c04c0:
    bra L_000c04c8
    .org 0xc04c2-ORIGIN
L_000c04c2:
    mov.l r2,@r15
    .org 0xc04c4-ORIGIN
L_000c04c4:
    mov r4,r7
    .org 0xc04c6-ORIGIN
L_000c04c6:
    mov.l r4,@r15
    .org 0xc04c8-ORIGIN
L_000c04c8:
    mov #0x34,r0
    .org 0xc04ca-ORIGIN
L_000c04ca:
    mov.b @(r0,r13),r0
    .org 0xc04cc-ORIGIN
L_000c04cc:
    tst #0x40,r0
    .org 0xc04ce-ORIGIN
L_000c04ce:
    bt L_000c0528
    .org 0xc04d0-ORIGIN
L_000c04d0:
    mov.l L_000c0508,r3
    .org 0xc04d2-ORIGIN
L_000c04d2:
    mov #-0x1,r6
    .org 0xc04d4-ORIGIN
L_000c04d4:
    mov.w L_000c04ee,r0
    .org 0xc04d6-ORIGIN
L_000c04d6:
    mov r7,r2
    .org 0xc04d8-ORIGIN
L_000c04d8:
    extu.b r6,r6
    .org 0xc04da-ORIGIN
L_000c04da:
    mov.b @(r0,r3),r5
    .org 0xc04dc-ORIGIN
L_000c04dc:
    add r5,r2
    .org 0xc04de-ORIGIN
L_000c04de:
    cmp/gt r6,r2
    .org 0xc04e0-ORIGIN
L_000c04e0:
    bf L_000c051c
    .org 0xc04e2-ORIGIN
L_000c04e2:
    mov #-0x1,r2
    .org 0xc04e4-ORIGIN
L_000c04e4:
    bra L_000c0520
    .org 0xc04e6-ORIGIN
L_000c04e6:
    extu.b r2,r6
    .org 0xc04e8-ORIGIN
L_000c04e8:
    .word 0x023c
    .org 0xc04ea-ORIGIN
L_000c04ea:
    .word 0x0709
    .org 0xc04ec-ORIGIN
L_000c04ec:
    .word 0x0a04
    .org 0xc04ee-ORIGIN
L_000c04ee:
    .word 0x047a
    .org 0xc04f0-ORIGIN
L_000c04f0:
    .long 0xffff120e
    .org 0xc04f4-ORIGIN
L_000c04f4:
    .long 0x00008cbc
    .org 0xc04f8-ORIGIN
L_000c04f8:
    .long 0xffff24f9
    .org 0xc04fc-ORIGIN
L_000c04fc:
    .long 0xffff124c
    .org 0xc0500-ORIGIN
L_000c0500:
    .long 0xffff2324
    .org 0xc0504-ORIGIN
L_000c0504:
    .long 0x000084d1
    .org 0xc0508-ORIGIN
L_000c0508:
    .long 0xffff128c
    .org 0xc050c-ORIGIN
L_000c050c:
    .long 0x000084c7
    .org 0xc0510-ORIGIN
L_000c0510:
    .long 0x0000830a
    .org 0xc0514-ORIGIN
L_000c0514:
    .long 0xffff119c
    .org 0xc0518-ORIGIN
L_000c0518:
    .long 0x000084f3
    .org 0xc051c-ORIGIN
L_000c051c:
    add r5,r7
    .org 0xc051e-ORIGIN
L_000c051e:
    mov r7,r6
    .org 0xc0520-ORIGIN
L_000c0520:
    cmp/pz r6
    .org 0xc0522-ORIGIN
L_000c0522:
    bt L_000c0526
    .org 0xc0524-ORIGIN
L_000c0524:
    mov #0x0,r6
    .org 0xc0526-ORIGIN
L_000c0526:
    mov.l r6,@r15
    .org 0xc0528-ORIGIN
L_000c0528:
    tst r11,r11
    .org 0xc052a-ORIGIN
L_000c052a:
    bf L_000c054e
    .org 0xc052c-ORIGIN
L_000c052c:
    mov.l L_000c0764,r3
    .org 0xc052e-ORIGIN
L_000c052e:
    mov #-0x80,r4
    .org 0xc0530-ORIGIN
L_000c0530:
    extu.b r4,r4
    .org 0xc0532-ORIGIN
L_000c0532:
    mov.b @(0x2,r3),r0
    .org 0xc0534-ORIGIN
L_000c0534:
    extu.b r0,r5
    .org 0xc0536-ORIGIN
L_000c0536:
    mov r5,r6
    .org 0xc0538-ORIGIN
L_000c0538:
    add r4,r6
    .org 0xc053a-ORIGIN
L_000c053a:
    add #0x7f,r4
    .org 0xc053c-ORIGIN
L_000c053c:
    cmp/gt r4,r6
    .org 0xc053e-ORIGIN
L_000c053e:
    bf L_000c0546
    .org 0xc0540-ORIGIN
L_000c0540:
    mov #-0x1,r2
    .org 0xc0542-ORIGIN
L_000c0542:
    bra L_000c054c
    .org 0xc0544-ORIGIN
L_000c0544:
    extu.b r2,r5
    .org 0xc0546-ORIGIN
L_000c0546:
    mov #-0x80,r2
    .org 0xc0548-ORIGIN
L_000c0548:
    extu.b r2,r2
    .org 0xc054a-ORIGIN
L_000c054a:
    add r2,r5
    .org 0xc054c-ORIGIN
L_000c054c:
    mov.l r5,@r15
    .org 0xc054e-ORIGIN
L_000c054e:
    mov.l @r15,r2
    .org 0xc0550-ORIGIN
L_000c0550:
    mov.l L_000c0768,r6
    .org 0xc0552-ORIGIN
L_000c0552:
    extu.b r2,r12
    .org 0xc0554-ORIGIN
L_000c0554:
    mov.l L_000c076c,r14
    .org 0xc0556-ORIGIN
L_000c0556:
    mov.w L_000c066e,r0
    .org 0xc0558-ORIGIN
L_000c0558:
    mov.b @r6,r2
    .org 0xc055a-ORIGIN
L_000c055a:
    mov.l L_000c0770,r6
    .org 0xc055c-ORIGIN
L_000c055c:
    mov.b r12,@(r0,r14)
    .org 0xc055e-ORIGIN
L_000c055e:
    extu.b r2,r7
    .org 0xc0560-ORIGIN
L_000c0560:
    mov.b @(0x1,r6),r0
    .org 0xc0562-ORIGIN
L_000c0562:
    mov.l L_000c0774,r14
    .org 0xc0564-ORIGIN
L_000c0564:
    extu.b r0,r2
    .org 0xc0566-ORIGIN
L_000c0566:
    mov.l L_000c0778,r10
    .org 0xc0568-ORIGIN
L_000c0568:
    mov #0x38,r0
    .org 0xc056a-ORIGIN
L_000c056a:
    mov.b @r6,r4
    .org 0xc056c-ORIGIN
L_000c056c:
    mov.b @(r0,r14),r0
    .org 0xc056e-ORIGIN
L_000c056e:
    mov.l L_000c077c,r14
    .org 0xc0570-ORIGIN
L_000c0570:
    extu.b r4,r4
    .org 0xc0572-ORIGIN
L_000c0572:
    and #0x1,r0
    .org 0xc0574-ORIGIN
L_000c0574:
    mov r0,r11
    .org 0xc0576-ORIGIN
L_000c0576:
    mov #0x16,r0
    .org 0xc0578-ORIGIN
L_000c0578:
    mov.b @(r0,r10),r6
    .org 0xc057a-ORIGIN
L_000c057a:
    mov #0x18,r0
    .org 0xc057c-ORIGIN
L_000c057c:
    mov.b r6,@(r0,r15)
    .org 0xc057e-ORIGIN
L_000c057e:
    extu.b r6,r5
    .org 0xc0580-ORIGIN
L_000c0580:
    mov.b @(0x5,r14),r0
    .org 0xc0582-ORIGIN
L_000c0582:
    mov #-0x80,r14
    .org 0xc0584-ORIGIN
L_000c0584:
    extu.b r14,r14
    .org 0xc0586-ORIGIN
L_000c0586:
    add r14,r7
    .org 0xc0588-ORIGIN
L_000c0588:
    mov r0,r9
    .org 0xc058a-ORIGIN
L_000c058a:
    add #0x7f,r14
    .org 0xc058c-ORIGIN
L_000c058c:
    mov #0x43,r0
    .org 0xc058e-ORIGIN
L_000c058e:
    cmp/gt r14,r7
    .org 0xc0590-ORIGIN
L_000c0590:
    bf/s L_000c059a
    .org 0xc0592-ORIGIN
L_000c0592:
    mov.b @(r0,r10),r8
    .org 0xc0594-ORIGIN
L_000c0594:
    mov #-0x1,r7
    .org 0xc0596-ORIGIN
L_000c0596:
    bra L_000c05a6
    .org 0xc0598-ORIGIN
L_000c0598:
    extu.b r7,r13
    .org 0xc059a-ORIGIN
L_000c059a:
    mov.l L_000c0768,r3
    .org 0xc059c-ORIGIN
L_000c059c:
    mov #-0x80,r7
    .org 0xc059e-ORIGIN
L_000c059e:
    extu.b r7,r7
    .org 0xc05a0-ORIGIN
L_000c05a0:
    mov.b @r3,r6
    .org 0xc05a2-ORIGIN
L_000c05a2:
    extu.b r6,r13
    .org 0xc05a4-ORIGIN
L_000c05a4:
    add r7,r13
    .org 0xc05a6-ORIGIN
L_000c05a6:
    mov #0x3f,r0
    .org 0xc05a8-ORIGIN
L_000c05a8:
    mov.b @(r0,r10),r14
    .org 0xc05aa-ORIGIN
L_000c05aa:
    mov r14,r0
    .org 0xc05ac-ORIGIN
L_000c05ac:
    tst #0x8,r0
    .org 0xc05ae-ORIGIN
L_000c05ae:
    bt/s L_000c05ba
    .org 0xc05b0-ORIGIN
L_000c05b0:
    mov r12,r7
    .org 0xc05b2-ORIGIN
L_000c05b2:
    mov.l L_000c0780,r3
    .org 0xc05b4-ORIGIN
L_000c05b4:
    mov.b @r3,r6
    .org 0xc05b6-ORIGIN
L_000c05b6:
    extu.b r6,r6
    .org 0xc05b8-ORIGIN
L_000c05b8:
    add r6,r7
    .org 0xc05ba-ORIGIN
L_000c05ba:
    cmp/hs r13,r7
    .org 0xc05bc-ORIGIN
L_000c05bc:
    mov r14,r0
    .org 0xc05be-ORIGIN
L_000c05be:
    bt/s L_000c05c4
    .org 0xc05c0-ORIGIN
L_000c05c0:
    or #0x8,r0
    .org 0xc05c2-ORIGIN
L_000c05c2:
    and #0xf7,r0
    .org 0xc05c4-ORIGIN
L_000c05c4:
    mov r0,r6
    .org 0xc05c6-ORIGIN
L_000c05c6:
    mov #0x3f,r0
    .org 0xc05c8-ORIGIN
L_000c05c8:
    mov.b r6,@(r0,r10)
    .org 0xc05ca-ORIGIN
L_000c05ca:
    mov #-0x80,r13
    .org 0xc05cc-ORIGIN
L_000c05cc:
    mov.l L_000c0784,r6
    .org 0xc05ce-ORIGIN
L_000c05ce:
    extu.b r13,r13
    .org 0xc05d0-ORIGIN
L_000c05d0:
    mov.b @r6,r14
    .org 0xc05d2-ORIGIN
L_000c05d2:
    extu.b r14,r14
    .org 0xc05d4-ORIGIN
L_000c05d4:
    mov r14,r7
    .org 0xc05d6-ORIGIN
L_000c05d6:
    add r13,r7
    .org 0xc05d8-ORIGIN
L_000c05d8:
    add #0x7f,r13
    .org 0xc05da-ORIGIN
L_000c05da:
    cmp/gt r13,r7
    .org 0xc05dc-ORIGIN
L_000c05dc:
    bf L_000c05e4
    .org 0xc05de-ORIGIN
L_000c05de:
    mov #-0x1,r7
    .org 0xc05e0-ORIGIN
L_000c05e0:
    bra L_000c05ea
    .org 0xc05e2-ORIGIN
L_000c05e2:
    extu.b r7,r14
    .org 0xc05e4-ORIGIN
L_000c05e4:
    mov #-0x80,r7
    .org 0xc05e6-ORIGIN
L_000c05e6:
    extu.b r7,r7
    .org 0xc05e8-ORIGIN
L_000c05e8:
    add r7,r14
    .org 0xc05ea-ORIGIN
L_000c05ea:
    mov #0x3f,r0
    .org 0xc05ec-ORIGIN
L_000c05ec:
    mov.b @(r0,r10),r0
    .org 0xc05ee-ORIGIN
L_000c05ee:
    tst #0x8,r0
    .org 0xc05f0-ORIGIN
L_000c05f0:
    bt L_000c06d8
    .org 0xc05f2-ORIGIN
L_000c05f2:
    mov.l L_000c0788,r6
    .org 0xc05f4-ORIGIN
L_000c05f4:
    mov #0x38,r0
    .org 0xc05f6-ORIGIN
L_000c05f6:
    mov.l r12,@r15
    .org 0xc05f8-ORIGIN
L_000c05f8:
    mov #-0x2,r13
    .org 0xc05fa-ORIGIN
L_000c05fa:
    mov.b @(r0,r6),r0
    .org 0xc05fc-ORIGIN
L_000c05fc:
    mov.l L_000c076c,r3
    .org 0xc05fe-ORIGIN
L_000c05fe:
    or #0x3,r0
    .org 0xc0600-ORIGIN
L_000c0600:
    mov r0,r12
    .org 0xc0602-ORIGIN
L_000c0602:
    mov #0x38,r0
    .org 0xc0604-ORIGIN
L_000c0604:
    mov.b r12,@(r0,r6)
    .org 0xc0606-ORIGIN
L_000c0606:
    mov.w L_000c0670,r0
    .org 0xc0608-ORIGIN
L_000c0608:
    mov.b @(r0,r3),r6
    .org 0xc060a-ORIGIN
L_000c060a:
    extu.b r6,r7
    .org 0xc060c-ORIGIN
L_000c060c:
    and r13,r7
    .org 0xc060e-ORIGIN
L_000c060e:
    extu.b r7,r7
    .org 0xc0610-ORIGIN
L_000c0610:
    mov #-0x3,r13
    .org 0xc0612-ORIGIN
L_000c0612:
    and r13,r7
    .org 0xc0614-ORIGIN
L_000c0614:
    mov.b r7,@(r0,r3)
    .org 0xc0616-ORIGIN
L_000c0616:
    mov.w L_000c0672,r0
    .org 0xc0618-ORIGIN
L_000c0618:
    mov.b @(r0,r3),r13
    .org 0xc061a-ORIGIN
L_000c061a:
    mov r13,r0
    .org 0xc061c-ORIGIN
L_000c061c:
    tst #0x1,r0
    .org 0xc061e-ORIGIN
L_000c061e:
    bt L_000c064a
    .org 0xc0620-ORIGIN
L_000c0620:
    mov.l L_000c076c,r3
    .org 0xc0622-ORIGIN
L_000c0622:
    mov.w L_000c0674,r0
    .org 0xc0624-ORIGIN
L_000c0624:
    mov.b @(r0,r3),r6
    .org 0xc0626-ORIGIN
L_000c0626:
    tst r6,r6
    .org 0xc0628-ORIGIN
L_000c0628:
    bt L_000c064a
    .org 0xc062a-ORIGIN
L_000c062a:
    mov.l L_000c076c,r3
    .org 0xc062c-ORIGIN
L_000c062c:
    mov #-0x1,r7
    .org 0xc062e-ORIGIN
L_000c062e:
    extu.b r7,r7
    .org 0xc0630-ORIGIN
L_000c0630:
    mov.b @(r0,r3),r6
    .org 0xc0632-ORIGIN
L_000c0632:
    extu.b r6,r6
    .org 0xc0634-ORIGIN
L_000c0634:
    add #0x1,r6
    .org 0xc0636-ORIGIN
L_000c0636:
    cmp/gt r7,r6
    .org 0xc0638-ORIGIN
L_000c0638:
    bf L_000c063e
    .org 0xc063a-ORIGIN
L_000c063a:
    bra L_000c0644
    .org 0xc063c-ORIGIN
L_000c063c:
    mov r7,r6
    .org 0xc063e-ORIGIN
L_000c063e:
    mov.l L_000c076c,r3
    .org 0xc0640-ORIGIN
L_000c0640:
    mov.b @(r0,r3),r6
    .org 0xc0642-ORIGIN
L_000c0642:
    add #0x1,r6
    .org 0xc0644-ORIGIN
L_000c0644:
    mov.l L_000c076c,r3
    .org 0xc0646-ORIGIN
L_000c0646:
    mov.w L_000c0674,r0
    .org 0xc0648-ORIGIN
L_000c0648:
    mov.b r6,@(r0,r3)
    .org 0xc064a-ORIGIN
L_000c064a:
    mov r13,r0
    .org 0xc064c-ORIGIN
L_000c064c:
    tst #0x2,r0
    .org 0xc064e-ORIGIN
L_000c064e:
    bt L_000c0684
    .org 0xc0650-ORIGIN
L_000c0650:
    mov.l L_000c076c,r3
    .org 0xc0652-ORIGIN
L_000c0652:
    mov.w L_000c0676,r0
    .org 0xc0654-ORIGIN
L_000c0654:
    mov.b @(r0,r3),r6
    .org 0xc0656-ORIGIN
L_000c0656:
    tst r6,r6
    .org 0xc0658-ORIGIN
L_000c0658:
    bt L_000c0684
    .org 0xc065a-ORIGIN
L_000c065a:
    mov.l L_000c076c,r3
    .org 0xc065c-ORIGIN
L_000c065c:
    mov #-0x1,r7
    .org 0xc065e-ORIGIN
L_000c065e:
    extu.b r7,r7
    .org 0xc0660-ORIGIN
L_000c0660:
    mov.b @(r0,r3),r6
    .org 0xc0662-ORIGIN
L_000c0662:
    extu.b r6,r6
    .org 0xc0664-ORIGIN
L_000c0664:
    add #0x1,r6
    .org 0xc0666-ORIGIN
L_000c0666:
    cmp/gt r7,r6
    .org 0xc0668-ORIGIN
L_000c0668:
    bf L_000c0678
    .org 0xc066a-ORIGIN
L_000c066a:
    bra L_000c067e
    .org 0xc066c-ORIGIN
L_000c066c:
    mov r7,r6
    .org 0xc066e-ORIGIN
L_000c066e:
    .word 0x0a04
    .org 0xc0670-ORIGIN
L_000c0670:
    .word 0x09f2
    .org 0xc0672-ORIGIN
L_000c0672:
    .word 0x084d
    .org 0xc0674-ORIGIN
L_000c0674:
    .word 0x06c5
    .org 0xc0676-ORIGIN
L_000c0676:
    .word 0x06c6
    .org 0xc0678-ORIGIN
L_000c0678:
    mov.l L_000c076c,r3
    .org 0xc067a-ORIGIN
L_000c067a:
    mov.b @(r0,r3),r6
    .org 0xc067c-ORIGIN
L_000c067c:
    add #0x1,r6
    .org 0xc067e-ORIGIN
L_000c067e:
    mov.l L_000c076c,r3
    .org 0xc0680-ORIGIN
L_000c0680:
    mov.w L_000c075a,r0
    .org 0xc0682-ORIGIN
L_000c0682:
    mov.b r6,@(r0,r3)
    .org 0xc0684-ORIGIN
L_000c0684:
    mov.l L_000c076c,r3
    .org 0xc0686-ORIGIN
L_000c0686:
    mov #-0x1,r7
    .org 0xc0688-ORIGIN
L_000c0688:
    mov.w L_000c075c,r0
    .org 0xc068a-ORIGIN
L_000c068a:
    extu.b r7,r7
    .org 0xc068c-ORIGIN
L_000c068c:
    mov.b @(r0,r3),r6
    .org 0xc068e-ORIGIN
L_000c068e:
    extu.b r6,r6
    .org 0xc0690-ORIGIN
L_000c0690:
    add #0x1,r6
    .org 0xc0692-ORIGIN
L_000c0692:
    cmp/gt r7,r6
    .org 0xc0694-ORIGIN
L_000c0694:
    bf L_000c069a
    .org 0xc0696-ORIGIN
L_000c0696:
    bra L_000c06a0
    .org 0xc0698-ORIGIN
L_000c0698:
    mov r7,r6
    .org 0xc069a-ORIGIN
L_000c069a:
    mov.l L_000c076c,r3
    .org 0xc069c-ORIGIN
L_000c069c:
    mov.b @(r0,r3),r6
    .org 0xc069e-ORIGIN
L_000c069e:
    add #0x1,r6
    .org 0xc06a0-ORIGIN
L_000c06a0:
    mov.l L_000c076c,r3
    .org 0xc06a2-ORIGIN
L_000c06a2:
    cmp/ge r14,r4
    .org 0xc06a4-ORIGIN
L_000c06a4:
    mov.w L_000c075c,r0
    .org 0xc06a6-ORIGIN
L_000c06a6:
    mov.b r6,@(r0,r3)
    .org 0xc06a8-ORIGIN
L_000c06a8:
    bf L_000c06bc
    .org 0xc06aa-ORIGIN
L_000c06aa:
    mov.l L_000c076c,r3
    .org 0xc06ac-ORIGIN
L_000c06ac:
    mov #0x0,r6
    .org 0xc06ae-ORIGIN
L_000c06ae:
    mov.w L_000c075e,r0
    .org 0xc06b0-ORIGIN
L_000c06b0:
    mov #-0x2,r4
    .org 0xc06b2-ORIGIN
L_000c06b2:
    extu.b r13,r13
    .org 0xc06b4-ORIGIN
L_000c06b4:
    mov.b r6,@(r0,r3)
    .org 0xc06b6-ORIGIN
L_000c06b6:
    and r4,r13
    .org 0xc06b8-ORIGIN
L_000c06b8:
    mov.w L_000c0760,r0
    .org 0xc06ba-ORIGIN
L_000c06ba:
    mov.b r13,@(r0,r3)
    .org 0xc06bc-ORIGIN
L_000c06bc:
    cmp/ge r14,r2
    .org 0xc06be-ORIGIN
L_000c06be:
    bt L_000c06c4
    .org 0xc06c0-ORIGIN
L_000c06c0:
    bra L_000c0944
    .org 0xc06c2-ORIGIN
L_000c06c2:
    nop
    .org 0xc06c4-ORIGIN
L_000c06c4:
    mov.l L_000c076c,r14
    .org 0xc06c6-ORIGIN
L_000c06c6:
    mov #0x0,r2
    .org 0xc06c8-ORIGIN
L_000c06c8:
    mov.w L_000c075a,r0
    .org 0xc06ca-ORIGIN
L_000c06ca:
    mov #-0x3,r6
    .org 0xc06cc-ORIGIN
L_000c06cc:
    mov.b r2,@(r0,r14)
    .org 0xc06ce-ORIGIN
L_000c06ce:
    extu.b r13,r2
    .org 0xc06d0-ORIGIN
L_000c06d0:
    mov.w L_000c0760,r0
    .org 0xc06d2-ORIGIN
L_000c06d2:
    and r6,r2
    .org 0xc06d4-ORIGIN
L_000c06d4:
    bra L_000c0944
    .org 0xc06d6-ORIGIN
L_000c06d6:
    mov.b r2,@(r0,r14)
    .org 0xc06d8-ORIGIN
L_000c06d8:
    mov.l L_000c0770,r7
    .org 0xc06da-ORIGIN
L_000c06da:
    cmp/ge r14,r4
    .org 0xc06dc-ORIGIN
L_000c06dc:
    mov.b @(0x3,r7),r0
    .org 0xc06de-ORIGIN
L_000c06de:
    extu.b r0,r6
    .org 0xc06e0-ORIGIN
L_000c06e0:
    bt/s L_000c06f2
    .org 0xc06e2-ORIGIN
L_000c06e2:
    mov.l r6,@r15
    .org 0xc06e4-ORIGIN
L_000c06e4:
    mov.l L_000c076c,r3
    .org 0xc06e6-ORIGIN
L_000c06e6:
    mov.w L_000c0760,r0
    .org 0xc06e8-ORIGIN
L_000c06e8:
    mov.b @(r0,r3),r0
    .org 0xc06ea-ORIGIN
L_000c06ea:
    or #0x1,r0
    .org 0xc06ec-ORIGIN
L_000c06ec:
    mov r0,r6
    .org 0xc06ee-ORIGIN
L_000c06ee:
    mov.w L_000c0760,r0
    .org 0xc06f0-ORIGIN
L_000c06f0:
    mov.b r6,@(r0,r3)
    .org 0xc06f2-ORIGIN
L_000c06f2:
    cmp/ge r14,r2
    .org 0xc06f4-ORIGIN
L_000c06f4:
    bt L_000c0704
    .org 0xc06f6-ORIGIN
L_000c06f6:
    mov.l L_000c076c,r3
    .org 0xc06f8-ORIGIN
L_000c06f8:
    mov.w L_000c0760,r0
    .org 0xc06fa-ORIGIN
L_000c06fa:
    mov.b @(r0,r3),r0
    .org 0xc06fc-ORIGIN
L_000c06fc:
    or #0x2,r0
    .org 0xc06fe-ORIGIN
L_000c06fe:
    mov r0,r2
    .org 0xc0700-ORIGIN
L_000c0700:
    mov.w L_000c0760,r0
    .org 0xc0702-ORIGIN
L_000c0702:
    mov.b r2,@(r0,r3)
    .org 0xc0704-ORIGIN
L_000c0704:
    mov.l L_000c0788,r2
    .org 0xc0706-ORIGIN
L_000c0706:
    mov #0x38,r0
    .org 0xc0708-ORIGIN
L_000c0708:
    mov.b @(r0,r2),r12
    .org 0xc070a-ORIGIN
L_000c070a:
    mov r12,r0
    .org 0xc070c-ORIGIN
L_000c070c:
    and #0x3,r0
    .org 0xc070e-ORIGIN
L_000c070e:
    tst r0,r0
    .org 0xc0710-ORIGIN
L_000c0710:
    bt/s L_000c0736
    .org 0xc0712-ORIGIN
L_000c0712:
    mov r0,r14
    .org 0xc0714-ORIGIN
L_000c0714:
    mov.l L_000c076c,r3
    .org 0xc0716-ORIGIN
L_000c0716:
    mov #-0x1,r7
    .org 0xc0718-ORIGIN
L_000c0718:
    mov.w L_000c075c,r0
    .org 0xc071a-ORIGIN
L_000c071a:
    extu.b r7,r7
    .org 0xc071c-ORIGIN
L_000c071c:
    mov.b @(r0,r3),r6
    .org 0xc071e-ORIGIN
L_000c071e:
    extu.b r6,r6
    .org 0xc0720-ORIGIN
L_000c0720:
    mov r6,r2
    .org 0xc0722-ORIGIN
L_000c0722:
    add #0x1,r2
    .org 0xc0724-ORIGIN
L_000c0724:
    cmp/gt r7,r2
    .org 0xc0726-ORIGIN
L_000c0726:
    bf L_000c072c
    .org 0xc0728-ORIGIN
L_000c0728:
    bra L_000c0730
    .org 0xc072a-ORIGIN
L_000c072a:
    mov r7,r2
    .org 0xc072c-ORIGIN
L_000c072c:
    add #0x1,r6
    .org 0xc072e-ORIGIN
L_000c072e:
    mov r6,r2
    .org 0xc0730-ORIGIN
L_000c0730:
    mov.l L_000c076c,r3
    .org 0xc0732-ORIGIN
L_000c0732:
    mov.w L_000c075c,r0
    .org 0xc0734-ORIGIN
L_000c0734:
    mov.b r2,@(r0,r3)
    .org 0xc0736-ORIGIN
L_000c0736:
    mov.l L_000c076c,r3
    .org 0xc0738-ORIGIN
L_000c0738:
    mov.w L_000c0760,r0
    .org 0xc073a-ORIGIN
L_000c073a:
    mov.b @(r0,r3),r6
    .org 0xc073c-ORIGIN
L_000c073c:
    mov r6,r0
    .org 0xc073e-ORIGIN
L_000c073e:
    tst #0x1,r0
    .org 0xc0740-ORIGIN
L_000c0740:
    bt L_000c0796
    .org 0xc0742-ORIGIN
L_000c0742:
    mov.l L_000c076c,r3
    .org 0xc0744-ORIGIN
L_000c0744:
    mov #-0x1,r7
    .org 0xc0746-ORIGIN
L_000c0746:
    mov.w L_000c075e,r0
    .org 0xc0748-ORIGIN
L_000c0748:
    extu.b r7,r7
    .org 0xc074a-ORIGIN
L_000c074a:
    mov.b @(r0,r3),r4
    .org 0xc074c-ORIGIN
L_000c074c:
    extu.b r4,r4
    .org 0xc074e-ORIGIN
L_000c074e:
    mov r4,r2
    .org 0xc0750-ORIGIN
L_000c0750:
    add #0x1,r2
    .org 0xc0752-ORIGIN
L_000c0752:
    cmp/gt r7,r2
    .org 0xc0754-ORIGIN
L_000c0754:
    bf L_000c078c
    .org 0xc0756-ORIGIN
L_000c0756:
    bra L_000c0790
    .org 0xc0758-ORIGIN
L_000c0758:
    mov r7,r2
    .org 0xc075a-ORIGIN
L_000c075a:
    .word 0x06c6
    .org 0xc075c-ORIGIN
L_000c075c:
    .word 0x06c7
    .org 0xc075e-ORIGIN
L_000c075e:
    .word 0x06c5
    .org 0xc0760-ORIGIN
L_000c0760:
    .word 0x084d
    .org 0xc0764-ORIGIN
L_000c0764:
    .long 0x00008e36
    .org 0xc0768-ORIGIN
L_000c0768:
    .long 0x00008dcb
    .org 0xc076c-ORIGIN
L_000c076c:
    .long 0xffff128c
    .org 0xc0770-ORIGIN
L_000c0770:
    .long 0xffff2324
    .org 0xc0774-ORIGIN
L_000c0774:
    .long 0xffff124c
    .org 0xc0778-ORIGIN
L_000c0778:
    .long 0xffff2468
    .org 0xc077c-ORIGIN
L_000c077c:
    .long 0xffff24ce
    .org 0xc0780-ORIGIN
L_000c0780:
    .long 0x000086f4
    .org 0xc0784-ORIGIN
L_000c0784:
    .long 0x00008de6
    .org 0xc0788-ORIGIN
L_000c0788:
    .long 0xffff120e
    .org 0xc078c-ORIGIN
L_000c078c:
    add #0x1,r4
    .org 0xc078e-ORIGIN
L_000c078e:
    mov r4,r2
    .org 0xc0790-ORIGIN
L_000c0790:
    mov.l L_000c09d0,r3
    .org 0xc0792-ORIGIN
L_000c0792:
    mov.w L_000c0886,r0
    .org 0xc0794-ORIGIN
L_000c0794:
    mov.b r2,@(r0,r3)
    .org 0xc0796-ORIGIN
L_000c0796:
    mov r6,r0
    .org 0xc0798-ORIGIN
L_000c0798:
    tst #0x2,r0
    .org 0xc079a-ORIGIN
L_000c079a:
    bt L_000c07ba
    .org 0xc079c-ORIGIN
L_000c079c:
    mov.l L_000c09d0,r3
    .org 0xc079e-ORIGIN
L_000c079e:
    mov #-0x1,r7
    .org 0xc07a0-ORIGIN
L_000c07a0:
    mov.w L_000c0888,r0
    .org 0xc07a2-ORIGIN
L_000c07a2:
    extu.b r7,r7
    .org 0xc07a4-ORIGIN
L_000c07a4:
    mov.b @(r0,r3),r6
    .org 0xc07a6-ORIGIN
L_000c07a6:
    extu.b r6,r6
    .org 0xc07a8-ORIGIN
L_000c07a8:
    mov r6,r2
    .org 0xc07aa-ORIGIN
L_000c07aa:
    add #0x1,r2
    .org 0xc07ac-ORIGIN
L_000c07ac:
    cmp/gt r7,r2
    .org 0xc07ae-ORIGIN
L_000c07ae:
    bt L_000c07b4
    .org 0xc07b0-ORIGIN
L_000c07b0:
    add #0x1,r6
    .org 0xc07b2-ORIGIN
L_000c07b2:
    mov r6,r7
    .org 0xc07b4-ORIGIN
L_000c07b4:
    mov.l L_000c09d0,r3
    .org 0xc07b6-ORIGIN
L_000c07b6:
    mov.w L_000c0888,r0
    .org 0xc07b8-ORIGIN
L_000c07b8:
    mov.b r7,@(r0,r3)
    .org 0xc07ba-ORIGIN
L_000c07ba:
    mov.l L_000c09d0,r3
    .org 0xc07bc-ORIGIN
L_000c07bc:
    mov.w L_000c0886,r0
    .org 0xc07be-ORIGIN
L_000c07be:
    mov.l L_000c09d4,r2
    .org 0xc07c0-ORIGIN
L_000c07c0:
    mov.b @(r0,r3),r4
    .org 0xc07c2-ORIGIN
L_000c07c2:
    mov.b @r2,r13
    .org 0xc07c4-ORIGIN
L_000c07c4:
    extu.b r4,r4
    .org 0xc07c6-ORIGIN
L_000c07c6:
    extu.b r13,r13
    .org 0xc07c8-ORIGIN
L_000c07c8:
    cmp/ge r13,r4
    .org 0xc07ca-ORIGIN
L_000c07ca:
    bf L_000c07e6
    .org 0xc07cc-ORIGIN
L_000c07cc:
    mov.l L_000c09d0,r3
    .org 0xc07ce-ORIGIN
L_000c07ce:
    mov.w L_000c0888,r0
    .org 0xc07d0-ORIGIN
L_000c07d0:
    mov.b @(r0,r3),r6
    .org 0xc07d2-ORIGIN
L_000c07d2:
    extu.b r6,r6
    .org 0xc07d4-ORIGIN
L_000c07d4:
    cmp/ge r13,r6
    .org 0xc07d6-ORIGIN
L_000c07d6:
    bf L_000c07e6
    .org 0xc07d8-ORIGIN
L_000c07d8:
    mov.l L_000c09d0,r3
    .org 0xc07da-ORIGIN
L_000c07da:
    mov.w L_000c088a,r0
    .org 0xc07dc-ORIGIN
L_000c07dc:
    mov.l L_000c09d4,r1
    .org 0xc07de-ORIGIN
L_000c07de:
    mov.b @(r0,r3),r6
    .org 0xc07e0-ORIGIN
L_000c07e0:
    mov.b @(0x5,r1),r0
    .org 0xc07e2-ORIGIN
L_000c07e2:
    cmp/hi r0,r6
    .org 0xc07e4-ORIGIN
L_000c07e4:
    bt L_000c0842
    .org 0xc07e6-ORIGIN
L_000c07e6:
    tst r14,r14
    .org 0xc07e8-ORIGIN
L_000c07e8:
    bt L_000c0820
    .org 0xc07ea-ORIGIN
L_000c07ea:
    mov.l L_000c09d8,r3
    .org 0xc07ec-ORIGIN
L_000c07ec:
    mov #-0x80,r6
    .org 0xc07ee-ORIGIN
L_000c07ee:
    mov.l L_000c09dc,r1
    .org 0xc07f0-ORIGIN
L_000c07f0:
    extu.b r6,r6
    .org 0xc07f2-ORIGIN
L_000c07f2:
    mov.b @r3,r2
    .org 0xc07f4-ORIGIN
L_000c07f4:
    mov.b @r1,r7
    .org 0xc07f6-ORIGIN
L_000c07f6:
    extu.b r2,r2
    .org 0xc07f8-ORIGIN
L_000c07f8:
    extu.b r7,r7
    .org 0xc07fa-ORIGIN
L_000c07fa:
    sub r7,r2
    .org 0xc07fc-ORIGIN
L_000c07fc:
    add r6,r2
    .org 0xc07fe-ORIGIN
L_000c07fe:
    cmp/pz r2
    .org 0xc0800-ORIGIN
L_000c0800:
    bt L_000c0806
    .org 0xc0802-ORIGIN
L_000c0802:
    bra L_000c0814
    .org 0xc0804-ORIGIN
L_000c0804:
    mov #0x0,r2
    .org 0xc0806-ORIGIN
L_000c0806:
    mov.l L_000c09d8,r3
    .org 0xc0808-ORIGIN
L_000c0808:
    mov #-0x80,r6
    .org 0xc080a-ORIGIN
L_000c080a:
    extu.b r6,r6
    .org 0xc080c-ORIGIN
L_000c080c:
    mov.b @r3,r2
    .org 0xc080e-ORIGIN
L_000c080e:
    extu.b r2,r2
    .org 0xc0810-ORIGIN
L_000c0810:
    sub r7,r2
    .org 0xc0812-ORIGIN
L_000c0812:
    add r6,r2
    .org 0xc0814-ORIGIN
L_000c0814:
    mov #-0x1,r7
    .org 0xc0816-ORIGIN
L_000c0816:
    extu.b r7,r7
    .org 0xc0818-ORIGIN
L_000c0818:
    cmp/gt r7,r2
    .org 0xc081a-ORIGIN
L_000c081a:
    bt L_000c0840
    .org 0xc081c-ORIGIN
L_000c081c:
    bra L_000c0840
    .org 0xc081e-ORIGIN
L_000c081e:
    mov r2,r7
    .org 0xc0820-ORIGIN
L_000c0820:
    mov.l L_000c09e0,r2
    .org 0xc0822-ORIGIN
L_000c0822:
    mov #-0x80,r14
    .org 0xc0824-ORIGIN
L_000c0824:
    extu.b r14,r14
    .org 0xc0826-ORIGIN
L_000c0826:
    mov.b @(0x2,r2),r0
    .org 0xc0828-ORIGIN
L_000c0828:
    extu.b r0,r7
    .org 0xc082a-ORIGIN
L_000c082a:
    mov r7,r6
    .org 0xc082c-ORIGIN
L_000c082c:
    add r14,r6
    .org 0xc082e-ORIGIN
L_000c082e:
    add #0x7f,r14
    .org 0xc0830-ORIGIN
L_000c0830:
    cmp/gt r14,r6
    .org 0xc0832-ORIGIN
L_000c0832:
    bf L_000c083a
    .org 0xc0834-ORIGIN
L_000c0834:
    mov #-0x1,r7
    .org 0xc0836-ORIGIN
L_000c0836:
    bra L_000c0840
    .org 0xc0838-ORIGIN
L_000c0838:
    extu.b r7,r7
    .org 0xc083a-ORIGIN
L_000c083a:
    mov #-0x80,r2
    .org 0xc083c-ORIGIN
L_000c083c:
    extu.b r2,r2
    .org 0xc083e-ORIGIN
L_000c083e:
    add r2,r7
    .org 0xc0840-ORIGIN
L_000c0840:
    mov.l r7,@r15
    .org 0xc0842-ORIGIN
L_000c0842:
    mov.l L_000c09d0,r3
    .org 0xc0844-ORIGIN
L_000c0844:
    mov.w L_000c088a,r0
    .org 0xc0846-ORIGIN
L_000c0846:
    mov.l L_000c09d4,r1
    .org 0xc0848-ORIGIN
L_000c0848:
    mov.b @(r0,r3),r6
    .org 0xc084a-ORIGIN
L_000c084a:
    mov.b @(0x5,r1),r0
    .org 0xc084c-ORIGIN
L_000c084c:
    cmp/hi r0,r6
    .org 0xc084e-ORIGIN
L_000c084e:
    bf L_000c0944
    .org 0xc0850-ORIGIN
L_000c0850:
    cmp/ge r13,r4
    .org 0xc0852-ORIGIN
L_000c0852:
    bf L_000c08a8
    .org 0xc0854-ORIGIN
L_000c0854:
    tst r11,r11
    .org 0xc0856-ORIGIN
L_000c0856:
    bt L_000c089c
    .org 0xc0858-ORIGIN
L_000c0858:
    mov.l L_000c09e4,r2
    .org 0xc085a-ORIGIN
L_000c085a:
    mov #0x12,r0
    .org 0xc085c-ORIGIN
L_000c085c:
    mov.b @r2,r6
    .org 0xc085e-ORIGIN
L_000c085e:
    mov.l L_000c09e8,r2
    .org 0xc0860-ORIGIN
L_000c0860:
    extu.b r6,r6
    .org 0xc0862-ORIGIN
L_000c0862:
    mov.b @(r0,r2),r7
    .org 0xc0864-ORIGIN
L_000c0864:
    extu.b r7,r7
    .org 0xc0866-ORIGIN
L_000c0866:
    cmp/gt r7,r6
    .org 0xc0868-ORIGIN
L_000c0868:
    bt L_000c088e
    .org 0xc086a-ORIGIN
L_000c086a:
    mov.l L_000c09ec,r6
    .org 0xc086c-ORIGIN
L_000c086c:
    mov.b @r6,r2
    .org 0xc086e-ORIGIN
L_000c086e:
    extu.b r2,r2
    .org 0xc0870-ORIGIN
L_000c0870:
    cmp/gt r2,r7
    .org 0xc0872-ORIGIN
L_000c0872:
    bt L_000c088e
    .org 0xc0874-ORIGIN
L_000c0874:
    mov.l L_000c09d0,r3
    .org 0xc0876-ORIGIN
L_000c0876:
    mov.w L_000c088c,r0
    .org 0xc0878-ORIGIN
L_000c0878:
    mov.b @(r0,r3),r0
    .org 0xc087a-ORIGIN
L_000c087a:
    or #0x1,r0
    .org 0xc087c-ORIGIN
L_000c087c:
    mov r0,r2
    .org 0xc087e-ORIGIN
L_000c087e:
    mov.w L_000c088c,r0
    .org 0xc0880-ORIGIN
L_000c0880:
    mov.b r2,@(r0,r3)
    .org 0xc0882-ORIGIN
L_000c0882:
    bra L_000c089c
    .org 0xc0884-ORIGIN
L_000c0884:
    nop
    .org 0xc0886-ORIGIN
L_000c0886:
    .word 0x06c5
    .org 0xc0888-ORIGIN
L_000c0888:
    .word 0x06c6
    .org 0xc088a-ORIGIN
L_000c088a:
    .word 0x06c7
    .org 0xc088c-ORIGIN
L_000c088c:
    .word 0x09f2
    .org 0xc088e-ORIGIN
L_000c088e:
    mov.l L_000c09d0,r14
    .org 0xc0890-ORIGIN
L_000c0890:
    mov #-0x2,r7
    .org 0xc0892-ORIGIN
L_000c0892:
    mov.w L_000c09c6,r0
    .org 0xc0894-ORIGIN
L_000c0894:
    mov.b @(r0,r14),r2
    .org 0xc0896-ORIGIN
L_000c0896:
    extu.b r2,r2
    .org 0xc0898-ORIGIN
L_000c0898:
    and r7,r2
    .org 0xc089a-ORIGIN
L_000c089a:
    mov.b r2,@(r0,r14)
    .org 0xc089c-ORIGIN
L_000c089c:
    extu.b r12,r12
    .org 0xc089e-ORIGIN
L_000c089e:
    mov.l L_000c09f0,r3
    .org 0xc08a0-ORIGIN
L_000c08a0:
    mov #-0x2,r6
    .org 0xc08a2-ORIGIN
L_000c08a2:
    and r6,r12
    .org 0xc08a4-ORIGIN
L_000c08a4:
    mov #0x38,r0
    .org 0xc08a6-ORIGIN
L_000c08a6:
    mov.b r12,@(r0,r3)
    .org 0xc08a8-ORIGIN
L_000c08a8:
    mov.l L_000c09d0,r3
    .org 0xc08aa-ORIGIN
L_000c08aa:
    mov.w L_000c09c8,r0
    .org 0xc08ac-ORIGIN
L_000c08ac:
    mov.b @(r0,r3),r6
    .org 0xc08ae-ORIGIN
L_000c08ae:
    extu.b r6,r6
    .org 0xc08b0-ORIGIN
L_000c08b0:
    cmp/ge r13,r6
    .org 0xc08b2-ORIGIN
L_000c08b2:
    bf L_000c0908
    .org 0xc08b4-ORIGIN
L_000c08b4:
    mov.l L_000c09f4,r3
    .org 0xc08b6-ORIGIN
L_000c08b6:
    mov #0x38,r0
    .org 0xc08b8-ORIGIN
L_000c08b8:
    mov.b @(r0,r3),r0
    .org 0xc08ba-ORIGIN
L_000c08ba:
    tst #0x2,r0
    .org 0xc08bc-ORIGIN
L_000c08bc:
    bt L_000c08fc
    .org 0xc08be-ORIGIN
L_000c08be:
    mov.l L_000c09e4,r2
    .org 0xc08c0-ORIGIN
L_000c08c0:
    mov #0x12,r0
    .org 0xc08c2-ORIGIN
L_000c08c2:
    mov.b @r2,r6
    .org 0xc08c4-ORIGIN
L_000c08c4:
    mov.l L_000c09e8,r2
    .org 0xc08c6-ORIGIN
L_000c08c6:
    extu.b r6,r6
    .org 0xc08c8-ORIGIN
L_000c08c8:
    mov.b @(r0,r2),r7
    .org 0xc08ca-ORIGIN
L_000c08ca:
    extu.b r7,r7
    .org 0xc08cc-ORIGIN
L_000c08cc:
    cmp/gt r7,r6
    .org 0xc08ce-ORIGIN
L_000c08ce:
    bt L_000c08ee
    .org 0xc08d0-ORIGIN
L_000c08d0:
    mov.l L_000c09ec,r3
    .org 0xc08d2-ORIGIN
L_000c08d2:
    mov r7,r6
    .org 0xc08d4-ORIGIN
L_000c08d4:
    mov.b @r3,r2
    .org 0xc08d6-ORIGIN
L_000c08d6:
    extu.b r2,r7
    .org 0xc08d8-ORIGIN
L_000c08d8:
    cmp/gt r7,r6
    .org 0xc08da-ORIGIN
L_000c08da:
    bt L_000c08ee
    .org 0xc08dc-ORIGIN
L_000c08dc:
    mov.l L_000c09d0,r3
    .org 0xc08de-ORIGIN
L_000c08de:
    mov.w L_000c09c6,r0
    .org 0xc08e0-ORIGIN
L_000c08e0:
    mov.b @(r0,r3),r0
    .org 0xc08e2-ORIGIN
L_000c08e2:
    or #0x2,r0
    .org 0xc08e4-ORIGIN
L_000c08e4:
    mov r0,r2
    .org 0xc08e6-ORIGIN
L_000c08e6:
    mov.w L_000c09c6,r0
    .org 0xc08e8-ORIGIN
L_000c08e8:
    mov.b r2,@(r0,r3)
    .org 0xc08ea-ORIGIN
L_000c08ea:
    bra L_000c08fc
    .org 0xc08ec-ORIGIN
L_000c08ec:
    nop
    .org 0xc08ee-ORIGIN
L_000c08ee:
    mov.l L_000c09d0,r14
    .org 0xc08f0-ORIGIN
L_000c08f0:
    mov #-0x3,r7
    .org 0xc08f2-ORIGIN
L_000c08f2:
    mov.w L_000c09c6,r0
    .org 0xc08f4-ORIGIN
L_000c08f4:
    mov.b @(r0,r14),r2
    .org 0xc08f6-ORIGIN
L_000c08f6:
    extu.b r2,r2
    .org 0xc08f8-ORIGIN
L_000c08f8:
    and r7,r2
    .org 0xc08fa-ORIGIN
L_000c08fa:
    mov.b r2,@(r0,r14)
    .org 0xc08fc-ORIGIN
L_000c08fc:
    extu.b r12,r12
    .org 0xc08fe-ORIGIN
L_000c08fe:
    mov.l L_000c09f0,r3
    .org 0xc0900-ORIGIN
L_000c0900:
    mov #-0x3,r6
    .org 0xc0902-ORIGIN
L_000c0902:
    and r6,r12
    .org 0xc0904-ORIGIN
L_000c0904:
    mov #0x38,r0
    .org 0xc0906-ORIGIN
L_000c0906:
    mov.b r12,@(r0,r3)
    .org 0xc0908-ORIGIN
L_000c0908:
    cmp/ge r13,r4
    .org 0xc090a-ORIGIN
L_000c090a:
    bf L_000c0944
    .org 0xc090c-ORIGIN
L_000c090c:
    mov.l L_000c09d0,r3
    .org 0xc090e-ORIGIN
L_000c090e:
    mov.w L_000c09c8,r0
    .org 0xc0910-ORIGIN
L_000c0910:
    mov.b @(r0,r3),r2
    .org 0xc0912-ORIGIN
L_000c0912:
    extu.b r2,r4
    .org 0xc0914-ORIGIN
L_000c0914:
    cmp/ge r13,r4
    .org 0xc0916-ORIGIN
L_000c0916:
    bf L_000c0944
    .org 0xc0918-ORIGIN
L_000c0918:
    mov.l L_000c09d0,r3
    .org 0xc091a-ORIGIN
L_000c091a:
    mov #0x0,r2
    .org 0xc091c-ORIGIN
L_000c091c:
    mov.w L_000c09ca,r0
    .org 0xc091e-ORIGIN
L_000c091e:
    mov #-0x80,r7
    .org 0xc0920-ORIGIN
L_000c0920:
    mov.b r2,@(r0,r3)
    .org 0xc0922-ORIGIN
L_000c0922:
    mov.l L_000c09e0,r2
    .org 0xc0924-ORIGIN
L_000c0924:
    mov.b @(0x2,r2),r0
    .org 0xc0926-ORIGIN
L_000c0926:
    extu.b r7,r2
    .org 0xc0928-ORIGIN
L_000c0928:
    extu.b r0,r4
    .org 0xc092a-ORIGIN
L_000c092a:
    mov r4,r6
    .org 0xc092c-ORIGIN
L_000c092c:
    add r2,r6
    .org 0xc092e-ORIGIN
L_000c092e:
    add #0x7f,r2
    .org 0xc0930-ORIGIN
L_000c0930:
    cmp/gt r2,r6
    .org 0xc0932-ORIGIN
L_000c0932:
    bf L_000c093a
    .org 0xc0934-ORIGIN
L_000c0934:
    mov #-0x1,r7
    .org 0xc0936-ORIGIN
L_000c0936:
    bra L_000c0942
    .org 0xc0938-ORIGIN
L_000c0938:
    extu.b r7,r2
    .org 0xc093a-ORIGIN
L_000c093a:
    mov #-0x80,r6
    .org 0xc093c-ORIGIN
L_000c093c:
    mov r4,r2
    .org 0xc093e-ORIGIN
L_000c093e:
    extu.b r6,r6
    .org 0xc0940-ORIGIN
L_000c0940:
    add r6,r2
    .org 0xc0942-ORIGIN
L_000c0942:
    mov.l r2,@r15
    .org 0xc0944-ORIGIN
L_000c0944:
    mov r12,r0
    .org 0xc0946-ORIGIN
L_000c0946:
    and #0x1,r0
    .org 0xc0948-ORIGIN
L_000c0948:
    tst r11,r11
    .org 0xc094a-ORIGIN
L_000c094a:
    bf/s L_000c0958
    .org 0xc094c-ORIGIN
L_000c094c:
    mov r0,r14
    .org 0xc094e-ORIGIN
L_000c094e:
    mov.l L_000c09f4,r3
    .org 0xc0950-ORIGIN
L_000c0950:
    mov #0x38,r0
    .org 0xc0952-ORIGIN
L_000c0952:
    mov.b @(r0,r3),r0
    .org 0xc0954-ORIGIN
L_000c0954:
    tst #0x2,r0
    .org 0xc0956-ORIGIN
L_000c0956:
    bt L_000c097a
    .org 0xc0958-ORIGIN
L_000c0958:
    mov.l L_000c09f8,r7
    .org 0xc095a-ORIGIN
L_000c095a:
    mov.l L_000c09fc,r4
    .org 0xc095c-ORIGIN
L_000c095c:
    mov.b @(0x3,r7),r0
    .org 0xc095e-ORIGIN
L_000c095e:
    mov r0,r6
    .org 0xc0960-ORIGIN
L_000c0960:
    mov.b @(0x3,r4),r0
    .org 0xc0962-ORIGIN
L_000c0962:
    cmp/hi r0,r6
    .org 0xc0964-ORIGIN
L_000c0964:
    bf L_000c0980
    .org 0xc0966-ORIGIN
L_000c0966:
    mov.l L_000c0a00,r6
    .org 0xc0968-ORIGIN
L_000c0968:
    mov #0x7d,r0
    .org 0xc096a-ORIGIN
L_000c096a:
    mov.b @(r0,r6),r2
    .org 0xc096c-ORIGIN
L_000c096c:
    tst r2,r2
    .org 0xc096e-ORIGIN
L_000c096e:
    bt L_000c0980
    .org 0xc0970-ORIGIN
L_000c0970:
    tst r14,r14
    .org 0xc0972-ORIGIN
L_000c0972:
    bt L_000c0980
    .org 0xc0974-ORIGIN
L_000c0974:
    mov r12,r0
    .org 0xc0976-ORIGIN
L_000c0976:
    tst #0x2,r0
    .org 0xc0978-ORIGIN
L_000c0978:
    bt L_000c0980
    .org 0xc097a-ORIGIN
L_000c097a:
    mov r5,r0
    .org 0xc097c-ORIGIN
L_000c097c:
    bra L_000c098e
    .org 0xc097e-ORIGIN
L_000c097e:
    and #0xfe,r0
    .org 0xc0980-ORIGIN
L_000c0980:
    mov.l L_000c0a00,r6
    .org 0xc0982-ORIGIN
L_000c0982:
    mov #0x7d,r0
    .org 0xc0984-ORIGIN
L_000c0984:
    mov.b @(r0,r6),r2
    .org 0xc0986-ORIGIN
L_000c0986:
    tst r2,r2
    .org 0xc0988-ORIGIN
L_000c0988:
    bf L_000c099a
    .org 0xc098a-ORIGIN
L_000c098a:
    mov r5,r0
    .org 0xc098c-ORIGIN
L_000c098c:
    or #0x1,r0
    .org 0xc098e-ORIGIN
L_000c098e:
    mov r0,r5
    .org 0xc0990-ORIGIN
L_000c0990:
    mov #0x16,r0
    .org 0xc0992-ORIGIN
L_000c0992:
    mov.b r5,@(r0,r10)
    .org 0xc0994-ORIGIN
L_000c0994:
    exts.b r5,r2
    .org 0xc0996-ORIGIN
L_000c0996:
    mov #0x18,r0
    .org 0xc0998-ORIGIN
L_000c0998:
    mov.b r2,@(r0,r15)
    .org 0xc099a-ORIGIN
L_000c099a:
    mov #0x18,r0
    .org 0xc099c-ORIGIN
L_000c099c:
    mov.b @(r0,r15),r0
    .org 0xc099e-ORIGIN
L_000c099e:
    tst #0x1,r0
    .org 0xc09a0-ORIGIN
L_000c09a0:
    bt L_000c0a04
    .org 0xc09a2-ORIGIN
L_000c09a2:
    mov.l L_000c09f8,r7
    .org 0xc09a4-ORIGIN
L_000c09a4:
    mov.l L_000c09e0,r3
    .org 0xc09a6-ORIGIN
L_000c09a6:
    mov.b @(0x3,r7),r0
    .org 0xc09a8-ORIGIN
L_000c09a8:
    extu.b r0,r2
    .org 0xc09aa-ORIGIN
L_000c09aa:
    mov.b @(0x2,r3),r0
    .org 0xc09ac-ORIGIN
L_000c09ac:
    add #-0x80,r2
    .org 0xc09ae-ORIGIN
L_000c09ae:
    extu.b r0,r5
    .org 0xc09b0-ORIGIN
L_000c09b0:
    cmp/gt r5,r2
    .org 0xc09b2-ORIGIN
L_000c09b2:
    bt L_000c09c0
    .org 0xc09b4-ORIGIN
L_000c09b4:
    mov.l L_000c09d0,r3
    .org 0xc09b6-ORIGIN
L_000c09b6:
    mov #0x2,r6
    .org 0xc09b8-ORIGIN
L_000c09b8:
    mov.w L_000c09cc,r0
    .org 0xc09ba-ORIGIN
L_000c09ba:
    mov.b @(r0,r3),r2
    .org 0xc09bc-ORIGIN
L_000c09bc:
    cmp/hi r6,r2
    .org 0xc09be-ORIGIN
L_000c09be:
    bt L_000c0a04
    .org 0xc09c0-ORIGIN
L_000c09c0:
    mov r9,r0
    .org 0xc09c2-ORIGIN
L_000c09c2:
    bra L_000c0a08
    .org 0xc09c4-ORIGIN
L_000c09c4:
    or #0x10,r0
    .org 0xc09c6-ORIGIN
L_000c09c6:
    .word 0x09f2
    .org 0xc09c8-ORIGIN
L_000c09c8:
    .word 0x06c6
    .org 0xc09ca-ORIGIN
L_000c09ca:
    .word 0x06c7
    .org 0xc09cc-ORIGIN
L_000c09cc:
    .word 0x09e8
    .org 0xc09d0-ORIGIN
L_000c09d0:
    .long 0xffff128c
    .org 0xc09d4-ORIGIN
L_000c09d4:
    .long 0x00008cbc
    .org 0xc09d8-ORIGIN
L_000c09d8:
    .long 0x00008dcb
    .org 0xc09dc-ORIGIN
L_000c09dc:
    .long 0x000086f4
    .org 0xc09e0-ORIGIN
L_000c09e0:
    .long 0x00008e36
    .org 0xc09e4-ORIGIN
L_000c09e4:
    .long 0x00008e15
    .org 0xc09e8-ORIGIN
L_000c09e8:
    .long 0xffff119c
    .org 0xc09ec-ORIGIN
L_000c09ec:
    .long 0x00008e14
    .org 0xc09f0-ORIGIN
L_000c09f0:
    .long 0xffff120e
    .org 0xc09f4-ORIGIN
L_000c09f4:
    .long 0xffff124c
    .org 0xc09f8-ORIGIN
L_000c09f8:
    .long 0xffff2324
    .org 0xc09fc-ORIGIN
L_000c09fc:
    .long 0xffff232a
    .org 0xc0a00-ORIGIN
L_000c0a00:
    .long 0xffff256a
    .org 0xc0a04-ORIGIN
L_000c0a04:
    mov r9,r0
    .org 0xc0a06-ORIGIN
L_000c0a06:
    and #0xef,r0
    .org 0xc0a08-ORIGIN
L_000c0a08:
    mov.l L_000c0cb4,r2
    .org 0xc0a0a-ORIGIN
L_000c0a0a:
    mov.b r0,@(0x5,r2)
    .org 0xc0a0c-ORIGIN
L_000c0a0c:
    mov.b @(0x5,r2),r0
    .org 0xc0a0e-ORIGIN
L_000c0a0e:
    and #0x10,r0
    .org 0xc0a10-ORIGIN
L_000c0a10:
    tst r0,r0
    .org 0xc0a12-ORIGIN
L_000c0a12:
    bt/s L_000c0a24
    .org 0xc0a14-ORIGIN
L_000c0a14:
    mov r0,r6
    .org 0xc0a16-ORIGIN
L_000c0a16:
    mov.l L_000c0cb8,r5
    .org 0xc0a18-ORIGIN
L_000c0a18:
    mov.b @r5,r0
    .org 0xc0a1a-ORIGIN
L_000c0a1a:
    tst #0x8,r0
    .org 0xc0a1c-ORIGIN
L_000c0a1c:
    bt L_000c0a24
    .org 0xc0a1e-ORIGIN
L_000c0a1e:
    mov r8,r0
    .org 0xc0a20-ORIGIN
L_000c0a20:
    bra L_000c0a28
    .org 0xc0a22-ORIGIN
L_000c0a22:
    or #0x4,r0
    .org 0xc0a24-ORIGIN
L_000c0a24:
    mov r8,r0
    .org 0xc0a26-ORIGIN
L_000c0a26:
    and #0xfb,r0
    .org 0xc0a28-ORIGIN
L_000c0a28:
    mov r0,r8
    .org 0xc0a2a-ORIGIN
L_000c0a2a:
    mov #0x43,r0
    .org 0xc0a2c-ORIGIN
L_000c0a2c:
    mov.b r8,@(r0,r10)
    .org 0xc0a2e-ORIGIN
L_000c0a2e:
    mov #0x42,r0
    .org 0xc0a30-ORIGIN
L_000c0a30:
    tst r6,r6
    .org 0xc0a32-ORIGIN
L_000c0a32:
    bt/s L_000c0a44
    .org 0xc0a34-ORIGIN
L_000c0a34:
    mov.b @(r0,r10),r5
    .org 0xc0a36-ORIGIN
L_000c0a36:
    mov #0x43,r0
    .org 0xc0a38-ORIGIN
L_000c0a38:
    mov.b @(r0,r10),r0
    .org 0xc0a3a-ORIGIN
L_000c0a3a:
    tst #0x4,r0
    .org 0xc0a3c-ORIGIN
L_000c0a3c:
    bf L_000c0a44
    .org 0xc0a3e-ORIGIN
L_000c0a3e:
    mov r5,r0
    .org 0xc0a40-ORIGIN
L_000c0a40:
    bra L_000c0a48
    .org 0xc0a42-ORIGIN
L_000c0a42:
    or #0x4,r0
    .org 0xc0a44-ORIGIN
L_000c0a44:
    mov r5,r0
    .org 0xc0a46-ORIGIN
L_000c0a46:
    and #0xfb,r0
    .org 0xc0a48-ORIGIN
L_000c0a48:
    mov r0,r5
    .org 0xc0a4a-ORIGIN
L_000c0a4a:
    mov #0x42,r0
    .org 0xc0a4c-ORIGIN
L_000c0a4c:
    tst r14,r14
    .org 0xc0a4e-ORIGIN
L_000c0a4e:
    bt/s L_000c0a58
    .org 0xc0a50-ORIGIN
L_000c0a50:
    mov.b r5,@(r0,r10)
    .org 0xc0a52-ORIGIN
L_000c0a52:
    mov r12,r0
    .org 0xc0a54-ORIGIN
L_000c0a54:
    tst #0x2,r0
    .org 0xc0a56-ORIGIN
L_000c0a56:
    bf L_000c0a7a
    .org 0xc0a58-ORIGIN
L_000c0a58:
    mov.l L_000c0cbc,r3
    .org 0xc0a5a-ORIGIN
L_000c0a5a:
    mov.w L_000c0aba,r0
    .org 0xc0a5c-ORIGIN
L_000c0a5c:
    mov.b @(r0,r3),r0
    .org 0xc0a5e-ORIGIN
L_000c0a5e:
    tst #0x1,r0
    .org 0xc0a60-ORIGIN
L_000c0a60:
    bt L_000c0a7a
    .org 0xc0a62-ORIGIN
L_000c0a62:
    tst r11,r11
    .org 0xc0a64-ORIGIN
L_000c0a64:
    bt L_000c0a88
    .org 0xc0a66-ORIGIN
L_000c0a66:
    mov.l @(0x1f0,gbr),r0
    .org 0xc0a68-ORIGIN
L_000c0a68:
    mov.l L_000c0cbc,r13
    .org 0xc0a6a-ORIGIN
L_000c0a6a:
    mov.l r0,@(0x1f8,gbr)
    .org 0xc0a6c-ORIGIN
L_000c0a6c:
    mov.w L_000c0abc,r0
    .org 0xc0a6e-ORIGIN
L_000c0a6e:
    mov.b @(r0,r13),r0
    .org 0xc0a70-ORIGIN
L_000c0a70:
    or #0x1,r0
    .org 0xc0a72-ORIGIN
L_000c0a72:
    mov r0,r2
    .org 0xc0a74-ORIGIN
L_000c0a74:
    mov.w L_000c0abc,r0
    .org 0xc0a76-ORIGIN
L_000c0a76:
    bra L_000c0a86
    .org 0xc0a78-ORIGIN
L_000c0a78:
    nop
    .org 0xc0a7a-ORIGIN
L_000c0a7a:
    mov.l L_000c0cbc,r13
    .org 0xc0a7c-ORIGIN
L_000c0a7c:
    mov #-0x2,r5
    .org 0xc0a7e-ORIGIN
L_000c0a7e:
    mov.w L_000c0abc,r0
    .org 0xc0a80-ORIGIN
L_000c0a80:
    mov.b @(r0,r13),r2
    .org 0xc0a82-ORIGIN
L_000c0a82:
    extu.b r2,r2
    .org 0xc0a84-ORIGIN
L_000c0a84:
    and r5,r2
    .org 0xc0a86-ORIGIN
L_000c0a86:
    mov.b r2,@(r0,r13)
    .org 0xc0a88-ORIGIN
L_000c0a88:
    tst r14,r14
    .org 0xc0a8a-ORIGIN
L_000c0a8a:
    bt L_000c0a92
    .org 0xc0a8c-ORIGIN
L_000c0a8c:
    mov r12,r0
    .org 0xc0a8e-ORIGIN
L_000c0a8e:
    tst #0x2,r0
    .org 0xc0a90-ORIGIN
L_000c0a90:
    bf L_000c0abe
    .org 0xc0a92-ORIGIN
L_000c0a92:
    mov.l L_000c0cbc,r3
    .org 0xc0a94-ORIGIN
L_000c0a94:
    mov.w L_000c0aba,r0
    .org 0xc0a96-ORIGIN
L_000c0a96:
    mov.b @(r0,r3),r0
    .org 0xc0a98-ORIGIN
L_000c0a98:
    tst #0x2,r0
    .org 0xc0a9a-ORIGIN
L_000c0a9a:
    bt L_000c0abe
    .org 0xc0a9c-ORIGIN
L_000c0a9c:
    mov.l L_000c0cc0,r3
    .org 0xc0a9e-ORIGIN
L_000c0a9e:
    mov #0x38,r0
    .org 0xc0aa0-ORIGIN
L_000c0aa0:
    mov.b @(r0,r3),r0
    .org 0xc0aa2-ORIGIN
L_000c0aa2:
    tst #0x2,r0
    .org 0xc0aa4-ORIGIN
L_000c0aa4:
    bt L_000c0acc
    .org 0xc0aa6-ORIGIN
L_000c0aa6:
    mov.l @(0x1f4,gbr),r0
    .org 0xc0aa8-ORIGIN
L_000c0aa8:
    mov.l L_000c0cbc,r14
    .org 0xc0aaa-ORIGIN
L_000c0aaa:
    mov.l r0,@(0x1fc,gbr)
    .org 0xc0aac-ORIGIN
L_000c0aac:
    mov.w L_000c0abc,r0
    .org 0xc0aae-ORIGIN
L_000c0aae:
    mov.b @(r0,r14),r0
    .org 0xc0ab0-ORIGIN
L_000c0ab0:
    or #0x2,r0
    .org 0xc0ab2-ORIGIN
L_000c0ab2:
    mov r0,r2
    .org 0xc0ab4-ORIGIN
L_000c0ab4:
    mov.w L_000c0abc,r0
    .org 0xc0ab6-ORIGIN
L_000c0ab6:
    bra L_000c0aca
    .org 0xc0ab8-ORIGIN
L_000c0ab8:
    nop
    .org 0xc0aba-ORIGIN
L_000c0aba:
    .word 0x09f2
    .org 0xc0abc-ORIGIN
L_000c0abc:
    .word 0x01ee
    .org 0xc0abe-ORIGIN
L_000c0abe:
    mov.l L_000c0cbc,r14
    .org 0xc0ac0-ORIGIN
L_000c0ac0:
    mov #-0x3,r5
    .org 0xc0ac2-ORIGIN
L_000c0ac2:
    mov.w L_000c0c50,r0
    .org 0xc0ac4-ORIGIN
L_000c0ac4:
    mov.b @(r0,r14),r2
    .org 0xc0ac6-ORIGIN
L_000c0ac6:
    extu.b r2,r2
    .org 0xc0ac8-ORIGIN
L_000c0ac8:
    and r5,r2
    .org 0xc0aca-ORIGIN
L_000c0aca:
    mov.b r2,@(r0,r14)
    .org 0xc0acc-ORIGIN
L_000c0acc:
    mov #0x42,r0
    .org 0xc0ace-ORIGIN
L_000c0ace:
    mov.b @(r0,r10),r6
    .org 0xc0ad0-ORIGIN
L_000c0ad0:
    mov r6,r0
    .org 0xc0ad2-ORIGIN
L_000c0ad2:
    tst #0x4,r0
    .org 0xc0ad4-ORIGIN
L_000c0ad4:
    bf L_000c0ada
    .org 0xc0ad6-ORIGIN
L_000c0ad6:
    bra L_000c0c0e
    .org 0xc0ad8-ORIGIN
L_000c0ad8:
    nop
    .org 0xc0ada-ORIGIN
L_000c0ada:
    mov.l L_000c0cbc,r3
    .org 0xc0adc-ORIGIN
L_000c0adc:
    mov.w L_000c0c52,r0
    .org 0xc0ade-ORIGIN
L_000c0ade:
    mov.b @(r0,r3),r0
    .org 0xc0ae0-ORIGIN
L_000c0ae0:
    tst #0x1,r0
    .org 0xc0ae2-ORIGIN
L_000c0ae2:
    bf L_000c0ae8
    .org 0xc0ae4-ORIGIN
L_000c0ae4:
    bra L_000c0c0e
    .org 0xc0ae6-ORIGIN
L_000c0ae6:
    nop
    .org 0xc0ae8-ORIGIN
L_000c0ae8:
    tst #0x2,r0
    .org 0xc0aea-ORIGIN
L_000c0aea:
    bf L_000c0af0
    .org 0xc0aec-ORIGIN
L_000c0aec:
    bra L_000c0c0e
    .org 0xc0aee-ORIGIN
L_000c0aee:
    nop
    .org 0xc0af0-ORIGIN
L_000c0af0:
    mov.l L_000c0cc0,r3
    .org 0xc0af2-ORIGIN
L_000c0af2:
    mov #0x38,r0
    .org 0xc0af4-ORIGIN
L_000c0af4:
    mov.b @(r0,r3),r0
    .org 0xc0af6-ORIGIN
L_000c0af6:
    tst #0x3,r0
    .org 0xc0af8-ORIGIN
L_000c0af8:
    bf L_000c0afe
    .org 0xc0afa-ORIGIN
L_000c0afa:
    bra L_000c0c0e
    .org 0xc0afc-ORIGIN
L_000c0afc:
    nop
    .org 0xc0afe-ORIGIN
L_000c0afe:
    mov.l L_000c0cbc,r3
    .org 0xc0b00-ORIGIN
L_000c0b00:
    mov.w L_000c0c50,r0
    .org 0xc0b02-ORIGIN
L_000c0b02:
    mov.b @(r0,r3),r0
    .org 0xc0b04-ORIGIN
L_000c0b04:
    tst #0x1,r0
    .org 0xc0b06-ORIGIN
L_000c0b06:
    bt L_000c0b72
    .org 0xc0b08-ORIGIN
L_000c0b08:
    mov.l L_000c0cc4,r3
    .org 0xc0b0a-ORIGIN
L_000c0b0a:
    mov #0x1,r5
    .org 0xc0b0c-ORIGIN
L_000c0b0c:
    mov.l L_000c0cc8,r2
    .org 0xc0b0e-ORIGIN
L_000c0b0e:
    shll8 r5
    .org 0xc0b10-ORIGIN
L_000c0b10:
    mov.w L_000c0c54,r0
    .org 0xc0b12-ORIGIN
L_000c0b12:
    mov.b @r3,r6
    .org 0xc0b14-ORIGIN
L_000c0b14:
    mov.l r2,@(0x1c,r15)
    .org 0xc0b16-ORIGIN
L_000c0b16:
    mov.l @(r0,r2),r4
    .org 0xc0b18-ORIGIN
L_000c0b18:
    mov #-0x80,r2
    .org 0xc0b1a-ORIGIN
L_000c0b1a:
    extu.b r6,r6
    .org 0xc0b1c-ORIGIN
L_000c0b1c:
    mov.l L_000c0ccc,r7
    .org 0xc0b1e-ORIGIN
L_000c0b1e:
    shll8 r2
    .org 0xc0b20-ORIGIN
L_000c0b20:
    sub r6,r5
    .org 0xc0b22-ORIGIN
L_000c0b22:
    mov.l r7,@(0x24,r15)
    .org 0xc0b24-ORIGIN
L_000c0b24:
    shll16 r2
    .org 0xc0b26-ORIGIN
L_000c0b26:
    shll8 r5
    .org 0xc0b28-ORIGIN
L_000c0b28:
    mov.l r2,@(0x20,r15)
    .org 0xc0b2a-ORIGIN
L_000c0b2a:
    sub r2,r4
    .org 0xc0b2c-ORIGIN
L_000c0b2c:
    extu.w r5,r5
    .org 0xc0b2e-ORIGIN
L_000c0b2e:
    jsr @r7
    .org 0xc0b30-ORIGIN
L_000c0b30:
    mov #0x0,r6
    .org 0xc0b32-ORIGIN
L_000c0b32:
    mov.l r0,@(0x28,r15)
    .org 0xc0b34-ORIGIN
L_000c0b34:
    mov #0x0,r6
    .org 0xc0b36-ORIGIN
L_000c0b36:
    mov.l @(0x1f8,gbr),r0
    .org 0xc0b38-ORIGIN
L_000c0b38:
    mov.l @(0x20,r15),r2
    .org 0xc0b3a-ORIGIN
L_000c0b3a:
    mov.l L_000c0cc4,r1
    .org 0xc0b3c-ORIGIN
L_000c0b3c:
    mov r0,r4
    .org 0xc0b3e-ORIGIN
L_000c0b3e:
    sub r2,r4
    .org 0xc0b40-ORIGIN
L_000c0b40:
    mov.l @(0x24,r15),r7
    .org 0xc0b42-ORIGIN
L_000c0b42:
    mov.b @r1,r2
    .org 0xc0b44-ORIGIN
L_000c0b44:
    mov.l r0,@(0x2c,r15)
    .org 0xc0b46-ORIGIN
L_000c0b46:
    extu.b r2,r5
    .org 0xc0b48-ORIGIN
L_000c0b48:
    shll8 r5
    .org 0xc0b4a-ORIGIN
L_000c0b4a:
    jsr @r7
    .org 0xc0b4c-ORIGIN
L_000c0b4c:
    extu.w r5,r5
    .org 0xc0b4e-ORIGIN
L_000c0b4e:
    mov.l L_000c0cd0,r2
    .org 0xc0b50-ORIGIN
L_000c0b50:
    mov r0,r5
    .org 0xc0b52-ORIGIN
L_000c0b52:
    jsr @r2
    .org 0xc0b54-ORIGIN
L_000c0b54:
    mov.l @(0x28,r15),r4
    .org 0xc0b56-ORIGIN
L_000c0b56:
    mov #-0x80,r6
    .org 0xc0b58-ORIGIN
L_000c0b58:
    mov r0,r2
    .org 0xc0b5a-ORIGIN
L_000c0b5a:
    shll8 r6
    .org 0xc0b5c-ORIGIN
L_000c0b5c:
    mov.w L_000c0c56,r0
    .org 0xc0b5e-ORIGIN
L_000c0b5e:
    shll16 r6
    .org 0xc0b60-ORIGIN
L_000c0b60:
    add r6,r2
    .org 0xc0b62-ORIGIN
L_000c0b62:
    mov.l @(0x1c,r15),r6
    .org 0xc0b64-ORIGIN
L_000c0b64:
    mov.l r2,@(r0,r6)
    .org 0xc0b66-ORIGIN
L_000c0b66:
    mov #0x16,r0
    .org 0xc0b68-ORIGIN
L_000c0b68:
    mov.b @(r0,r10),r0
    .org 0xc0b6a-ORIGIN
L_000c0b6a:
    or #0x8,r0
    .org 0xc0b6c-ORIGIN
L_000c0b6c:
    mov r0,r2
    .org 0xc0b6e-ORIGIN
L_000c0b6e:
    mov #0x16,r0
    .org 0xc0b70-ORIGIN
L_000c0b70:
    mov.b r2,@(r0,r10)
    .org 0xc0b72-ORIGIN
L_000c0b72:
    mov.l L_000c0cbc,r3
    .org 0xc0b74-ORIGIN
L_000c0b74:
    mov.w L_000c0c50,r0
    .org 0xc0b76-ORIGIN
L_000c0b76:
    mov.b @(r0,r3),r0
    .org 0xc0b78-ORIGIN
L_000c0b78:
    tst #0x2,r0
    .org 0xc0b7a-ORIGIN
L_000c0b7a:
    bt L_000c0be6
    .org 0xc0b7c-ORIGIN
L_000c0b7c:
    mov.l L_000c0cc4,r3
    .org 0xc0b7e-ORIGIN
L_000c0b7e:
    mov #0x1,r5
    .org 0xc0b80-ORIGIN
L_000c0b80:
    mov.l L_000c0cc8,r2
    .org 0xc0b82-ORIGIN
L_000c0b82:
    shll8 r5
    .org 0xc0b84-ORIGIN
L_000c0b84:
    mov.w L_000c0c58,r0
    .org 0xc0b86-ORIGIN
L_000c0b86:
    mov.b @r3,r6
    .org 0xc0b88-ORIGIN
L_000c0b88:
    mov.l r2,@(0x1c,r15)
    .org 0xc0b8a-ORIGIN
L_000c0b8a:
    mov.l @(r0,r2),r4
    .org 0xc0b8c-ORIGIN
L_000c0b8c:
    mov #-0x80,r2
    .org 0xc0b8e-ORIGIN
L_000c0b8e:
    extu.b r6,r6
    .org 0xc0b90-ORIGIN
L_000c0b90:
    mov.l L_000c0ccc,r7
    .org 0xc0b92-ORIGIN
L_000c0b92:
    shll8 r2
    .org 0xc0b94-ORIGIN
L_000c0b94:
    sub r6,r5
    .org 0xc0b96-ORIGIN
L_000c0b96:
    mov.l r7,@(0x24,r15)
    .org 0xc0b98-ORIGIN
L_000c0b98:
    shll16 r2
    .org 0xc0b9a-ORIGIN
L_000c0b9a:
    shll8 r5
    .org 0xc0b9c-ORIGIN
L_000c0b9c:
    mov.l r2,@(0x30,r15)
    .org 0xc0b9e-ORIGIN
L_000c0b9e:
    sub r2,r4
    .org 0xc0ba0-ORIGIN
L_000c0ba0:
    mov #0x0,r6
    .org 0xc0ba2-ORIGIN
L_000c0ba2:
    jsr @r7
    .org 0xc0ba4-ORIGIN
L_000c0ba4:
    extu.w r5,r5
    .org 0xc0ba6-ORIGIN
L_000c0ba6:
    mov.l r0,@(0x28,r15)
    .org 0xc0ba8-ORIGIN
L_000c0ba8:
    mov #0x0,r6
    .org 0xc0baa-ORIGIN
L_000c0baa:
    mov.l @(0x1fc,gbr),r0
    .org 0xc0bac-ORIGIN
L_000c0bac:
    mov.l @(0x30,r15),r2
    .org 0xc0bae-ORIGIN
L_000c0bae:
    mov.l L_000c0cc4,r1
    .org 0xc0bb0-ORIGIN
L_000c0bb0:
    mov r0,r4
    .org 0xc0bb2-ORIGIN
L_000c0bb2:
    sub r2,r4
    .org 0xc0bb4-ORIGIN
L_000c0bb4:
    mov.l @(0x24,r15),r7
    .org 0xc0bb6-ORIGIN
L_000c0bb6:
    mov.b @r1,r2
    .org 0xc0bb8-ORIGIN
L_000c0bb8:
    mov.l r0,@(0x34,r15)
    .org 0xc0bba-ORIGIN
L_000c0bba:
    extu.b r2,r5
    .org 0xc0bbc-ORIGIN
L_000c0bbc:
    shll8 r5
    .org 0xc0bbe-ORIGIN
L_000c0bbe:
    jsr @r7
    .org 0xc0bc0-ORIGIN
L_000c0bc0:
    extu.w r5,r5
    .org 0xc0bc2-ORIGIN
L_000c0bc2:
    mov.l L_000c0cd0,r2
    .org 0xc0bc4-ORIGIN
L_000c0bc4:
    mov r0,r5
    .org 0xc0bc6-ORIGIN
L_000c0bc6:
    jsr @r2
    .org 0xc0bc8-ORIGIN
L_000c0bc8:
    mov.l @(0x28,r15),r4
    .org 0xc0bca-ORIGIN
L_000c0bca:
    mov #-0x80,r6
    .org 0xc0bcc-ORIGIN
L_000c0bcc:
    mov r0,r2
    .org 0xc0bce-ORIGIN
L_000c0bce:
    shll8 r6
    .org 0xc0bd0-ORIGIN
L_000c0bd0:
    mov.w L_000c0c5a,r0
    .org 0xc0bd2-ORIGIN
L_000c0bd2:
    shll16 r6
    .org 0xc0bd4-ORIGIN
L_000c0bd4:
    add r6,r2
    .org 0xc0bd6-ORIGIN
L_000c0bd6:
    mov.l @(0x1c,r15),r6
    .org 0xc0bd8-ORIGIN
L_000c0bd8:
    mov.l r2,@(r0,r6)
    .org 0xc0bda-ORIGIN
L_000c0bda:
    mov #0x16,r0
    .org 0xc0bdc-ORIGIN
L_000c0bdc:
    mov.b @(r0,r10),r0
    .org 0xc0bde-ORIGIN
L_000c0bde:
    or #0x10,r0
    .org 0xc0be0-ORIGIN
L_000c0be0:
    mov r0,r2
    .org 0xc0be2-ORIGIN
L_000c0be2:
    mov #0x16,r0
    .org 0xc0be4-ORIGIN
L_000c0be4:
    mov.b r2,@(r0,r10)
    .org 0xc0be6-ORIGIN
L_000c0be6:
    mov #0x16,r0
    .org 0xc0be8-ORIGIN
L_000c0be8:
    mov.b @(r0,r10),r5
    .org 0xc0bea-ORIGIN
L_000c0bea:
    mov #0x42,r0
    .org 0xc0bec-ORIGIN
L_000c0bec:
    mov.b @(r0,r10),r6
    .org 0xc0bee-ORIGIN
L_000c0bee:
    mov r5,r0
    .org 0xc0bf0-ORIGIN
L_000c0bf0:
    and #0x18,r0
    .org 0xc0bf2-ORIGIN
L_000c0bf2:
    cmp/eq #0x18,r0
    .org 0xc0bf4-ORIGIN
L_000c0bf4:
    bf L_000c0c0e
    .org 0xc0bf6-ORIGIN
L_000c0bf6:
    mov.l L_000c0cbc,r14
    .org 0xc0bf8-ORIGIN
L_000c0bf8:
    mov.w L_000c0c5c,r0
    .org 0xc0bfa-ORIGIN
L_000c0bfa:
    mov.b @(r0,r14),r0
    .org 0xc0bfc-ORIGIN
L_000c0bfc:
    or #0x3,r0
    .org 0xc0bfe-ORIGIN
L_000c0bfe:
    mov r0,r2
    .org 0xc0c00-ORIGIN
L_000c0c00:
    mov.w L_000c0c5c,r0
    .org 0xc0c02-ORIGIN
L_000c0c02:
    mov.b r2,@(r0,r14)
    .org 0xc0c04-ORIGIN
L_000c0c04:
    mov r5,r0
    .org 0xc0c06-ORIGIN
L_000c0c06:
    and #0xe7,r0
    .org 0xc0c08-ORIGIN
L_000c0c08:
    mov r0,r4
    .org 0xc0c0a-ORIGIN
L_000c0c0a:
    mov #0x16,r0
    .org 0xc0c0c-ORIGIN
L_000c0c0c:
    mov.b r4,@(r0,r10)
    .org 0xc0c0e-ORIGIN
L_000c0c0e:
    mov r6,r0
    .org 0xc0c10-ORIGIN
L_000c0c10:
    and #0xfb,r0
    .org 0xc0c12-ORIGIN
L_000c0c12:
    mov r0,r6
    .org 0xc0c14-ORIGIN
L_000c0c14:
    mov #0x42,r0
    .org 0xc0c16-ORIGIN
L_000c0c16:
    mov.b r6,@(r0,r10)
    .org 0xc0c18-ORIGIN
L_000c0c18:
    mov #0x43,r0
    .org 0xc0c1a-ORIGIN
L_000c0c1a:
    mov.b @(r0,r10),r6
    .org 0xc0c1c-ORIGIN
L_000c0c1c:
    mov r6,r0
    .org 0xc0c1e-ORIGIN
L_000c0c1e:
    tst #0x4,r0
    .org 0xc0c20-ORIGIN
L_000c0c20:
    bt L_000c0cd6
    .org 0xc0c22-ORIGIN
L_000c0c22:
    mov.l L_000c0cbc,r3
    .org 0xc0c24-ORIGIN
L_000c0c24:
    mov.w L_000c0c52,r0
    .org 0xc0c26-ORIGIN
L_000c0c26:
    mov.b @(r0,r3),r0
    .org 0xc0c28-ORIGIN
L_000c0c28:
    tst #0x1,r0
    .org 0xc0c2a-ORIGIN
L_000c0c2a:
    bt L_000c0cd6
    .org 0xc0c2c-ORIGIN
L_000c0c2c:
    tst #0x2,r0
    .org 0xc0c2e-ORIGIN
L_000c0c2e:
    bt L_000c0cd6
    .org 0xc0c30-ORIGIN
L_000c0c30:
    mov.l L_000c0cc0,r3
    .org 0xc0c32-ORIGIN
L_000c0c32:
    mov #0x38,r0
    .org 0xc0c34-ORIGIN
L_000c0c34:
    mov.b @(r0,r3),r0
    .org 0xc0c36-ORIGIN
L_000c0c36:
    tst #0x3,r0
    .org 0xc0c38-ORIGIN
L_000c0c38:
    bt L_000c0cd6
    .org 0xc0c3a-ORIGIN
L_000c0c3a:
    mov #0x16,r0
    .org 0xc0c3c-ORIGIN
L_000c0c3c:
    mov.l L_000c0cbc,r3
    .org 0xc0c3e-ORIGIN
L_000c0c3e:
    mov.b @(r0,r10),r2
    .org 0xc0c40-ORIGIN
L_000c0c40:
    mov.w L_000c0c50,r0
    .org 0xc0c42-ORIGIN
L_000c0c42:
    mov.b @(r0,r3),r4
    .org 0xc0c44-ORIGIN
L_000c0c44:
    mov r4,r0
    .org 0xc0c46-ORIGIN
L_000c0c46:
    tst #0x1,r0
    .org 0xc0c48-ORIGIN
L_000c0c48:
    bt/s L_000c0c78
    .org 0xc0c4a-ORIGIN
L_000c0c4a:
    extu.b r2,r5
    .org 0xc0c4c-ORIGIN
L_000c0c4c:
    bra L_000c0c5e
    .org 0xc0c4e-ORIGIN
L_000c0c4e:
    nop
    .org 0xc0c50-ORIGIN
L_000c0c50:
    .word 0x01ee
    .org 0xc0c52-ORIGIN
L_000c0c52:
    .word 0x09f2
    .org 0xc0c54-ORIGIN
L_000c0c54:
    .word 0x02e8
    .org 0xc0c56-ORIGIN
L_000c0c56:
    .word 0x02e0
    .org 0xc0c58-ORIGIN
L_000c0c58:
    .word 0x02ec
    .org 0xc0c5a-ORIGIN
L_000c0c5a:
    .word 0x02e4
    .org 0xc0c5c-ORIGIN
L_000c0c5c:
    .word 0x09f3
    .org 0xc0c5e-ORIGIN
L_000c0c5e:
    mov.l L_000c0cbc,r14
    .org 0xc0c60-ORIGIN
L_000c0c60:
    mov.w L_000c0cb0,r0
    .org 0xc0c62-ORIGIN
L_000c0c62:
    mov.b @(r0,r14),r0
    .org 0xc0c64-ORIGIN
L_000c0c64:
    or #0x1,r0
    .org 0xc0c66-ORIGIN
L_000c0c66:
    mov r0,r2
    .org 0xc0c68-ORIGIN
L_000c0c68:
    mov.w L_000c0cb0,r0
    .org 0xc0c6a-ORIGIN
L_000c0c6a:
    mov.b r2,@(r0,r14)
    .org 0xc0c6c-ORIGIN
L_000c0c6c:
    mov #0x2,r0
    .org 0xc0c6e-ORIGIN
L_000c0c6e:
    or r0,r5
    .org 0xc0c70-ORIGIN
L_000c0c70:
    mov #0x16,r0
    .org 0xc0c72-ORIGIN
L_000c0c72:
    exts.b r5,r2
    .org 0xc0c74-ORIGIN
L_000c0c74:
    mov.b r5,@(r0,r10)
    .org 0xc0c76-ORIGIN
L_000c0c76:
    extu.b r2,r5
    .org 0xc0c78-ORIGIN
L_000c0c78:
    mov r4,r0
    .org 0xc0c7a-ORIGIN
L_000c0c7a:
    tst #0x2,r0
    .org 0xc0c7c-ORIGIN
L_000c0c7c:
    bt L_000c0c96
    .org 0xc0c7e-ORIGIN
L_000c0c7e:
    mov.l L_000c0cbc,r14
    .org 0xc0c80-ORIGIN
L_000c0c80:
    mov.w L_000c0cb0,r0
    .org 0xc0c82-ORIGIN
L_000c0c82:
    mov.b @(r0,r14),r0
    .org 0xc0c84-ORIGIN
L_000c0c84:
    or #0x2,r0
    .org 0xc0c86-ORIGIN
L_000c0c86:
    mov r0,r2
    .org 0xc0c88-ORIGIN
L_000c0c88:
    mov.w L_000c0cb0,r0
    .org 0xc0c8a-ORIGIN
L_000c0c8a:
    mov.b r2,@(r0,r14)
    .org 0xc0c8c-ORIGIN
L_000c0c8c:
    mov #0x4,r0
    .org 0xc0c8e-ORIGIN
L_000c0c8e:
    or r0,r5
    .org 0xc0c90-ORIGIN
L_000c0c90:
    mov #0x16,r0
    .org 0xc0c92-ORIGIN
L_000c0c92:
    mov.b r5,@(r0,r10)
    .org 0xc0c94-ORIGIN
L_000c0c94:
    exts.b r5,r5
    .org 0xc0c96-ORIGIN
L_000c0c96:
    mov r5,r0
    .org 0xc0c98-ORIGIN
L_000c0c98:
    and #0x6,r0
    .org 0xc0c9a-ORIGIN
L_000c0c9a:
    cmp/eq #0x6,r0
    .org 0xc0c9c-ORIGIN
L_000c0c9c:
    bf L_000c0cd6
    .org 0xc0c9e-ORIGIN
L_000c0c9e:
    mov.l L_000c0cb8,r4
    .org 0xc0ca0-ORIGIN
L_000c0ca0:
    mov.b @r4,r0
    .org 0xc0ca2-ORIGIN
L_000c0ca2:
    and #0xf7,r0
    .org 0xc0ca4-ORIGIN
L_000c0ca4:
    mov.b r0,@r4
    .org 0xc0ca6-ORIGIN
L_000c0ca6:
    mov r5,r0
    .org 0xc0ca8-ORIGIN
L_000c0ca8:
    and #0xf9,r0
    .org 0xc0caa-ORIGIN
L_000c0caa:
    mov r0,r5
    .org 0xc0cac-ORIGIN
L_000c0cac:
    bra L_000c0cd4
    .org 0xc0cae-ORIGIN
L_000c0cae:
    mov #0x16,r0
    .org 0xc0cb0-ORIGIN
L_000c0cb0:
    .word 0x0a02
    .org 0xc0cb4-ORIGIN
L_000c0cb4:
    .long 0xffff24ce
    .org 0xc0cb8-ORIGIN
L_000c0cb8:
    .long 0xffff5b33
    .org 0xc0cbc-ORIGIN
L_000c0cbc:
    .long 0xffff128c
    .org 0xc0cc0-ORIGIN
L_000c0cc0:
    .long 0xffff124c
    .org 0xc0cc4-ORIGIN
L_000c0cc4:
    .long 0x00008e52
    .org 0xc0cc8-ORIGIN
L_000c0cc8:
    .long 0xffff4558
    .org 0xc0ccc-ORIGIN
L_000c0ccc:
    .long 0x0002657c
    .org 0xc0cd0-ORIGIN
L_000c0cd0:
    .long 0x000265c4
    .org 0xc0cd4-ORIGIN
L_000c0cd4:
    mov.b r5,@(r0,r10)
    .org 0xc0cd6-ORIGIN
L_000c0cd6:
    mov r6,r0
    .org 0xc0cd8-ORIGIN
L_000c0cd8:
    and #0xfb,r0
    .org 0xc0cda-ORIGIN
L_000c0cda:
    mov r0,r6
    .org 0xc0cdc-ORIGIN
L_000c0cdc:
    mov #0x43,r0
    .org 0xc0cde-ORIGIN
L_000c0cde:
    mov.b r6,@(r0,r10)
    .org 0xc0ce0-ORIGIN
L_000c0ce0:
    mov.l @r15,r0
    .org 0xc0ce2-ORIGIN
L_000c0ce2:
    mov #-0x80,r6
    .org 0xc0ce4-ORIGIN
L_000c0ce4:
    mov.l L_000c0ebc,r7
    .org 0xc0ce6-ORIGIN
L_000c0ce6:
    extu.b r6,r6
    .org 0xc0ce8-ORIGIN
L_000c0ce8:
    extu.b r0,r2
    .org 0xc0cea-ORIGIN
L_000c0cea:
    cmp/eq r6,r2
    .org 0xc0cec-ORIGIN
L_000c0cec:
    bf/s L_000c0cfc
    .org 0xc0cee-ORIGIN
L_000c0cee:
    mov.b r0,@(0x3,r7)
    .org 0xc0cf0-ORIGIN
L_000c0cf0:
    mov.l L_000c0ec0,r3
    .org 0xc0cf2-ORIGIN
L_000c0cf2:
    mov #0x0,r2
    .org 0xc0cf4-ORIGIN
L_000c0cf4:
    mov.w L_000c0e42,r0
    .org 0xc0cf6-ORIGIN
L_000c0cf6:
    mov.b r2,@(r0,r3)
    .org 0xc0cf8-ORIGIN
L_000c0cf8:
    bra L_000c0d1a
    .org 0xc0cfa-ORIGIN
L_000c0cfa:
    nop
    .org 0xc0cfc-ORIGIN
L_000c0cfc:
    mov.l L_000c0ec0,r14
    .org 0xc0cfe-ORIGIN
L_000c0cfe:
    mov #-0x1,r7
    .org 0xc0d00-ORIGIN
L_000c0d00:
    mov.w L_000c0e42,r0
    .org 0xc0d02-ORIGIN
L_000c0d02:
    extu.b r7,r7
    .org 0xc0d04-ORIGIN
L_000c0d04:
    mov.b @(r0,r14),r6
    .org 0xc0d06-ORIGIN
L_000c0d06:
    extu.b r6,r6
    .org 0xc0d08-ORIGIN
L_000c0d08:
    mov r6,r2
    .org 0xc0d0a-ORIGIN
L_000c0d0a:
    add #0x1,r2
    .org 0xc0d0c-ORIGIN
L_000c0d0c:
    cmp/gt r7,r2
    .org 0xc0d0e-ORIGIN
L_000c0d0e:
    bt L_000c0d14
    .org 0xc0d10-ORIGIN
L_000c0d10:
    mov r6,r7
    .org 0xc0d12-ORIGIN
L_000c0d12:
    add #0x1,r7
    .org 0xc0d14-ORIGIN
L_000c0d14:
    mov.l L_000c0ec0,r3
    .org 0xc0d16-ORIGIN
L_000c0d16:
    mov.w L_000c0e42,r0
    .org 0xc0d18-ORIGIN
L_000c0d18:
    mov.b r7,@(r0,r3)
    .org 0xc0d1a-ORIGIN
L_000c0d1a:
    add #0x38,r15
    .org 0xc0d1c-ORIGIN
L_000c0d1c:
    ldc.l @r15+,gbr
    .org 0xc0d1e-ORIGIN
L_000c0d1e:
    lds.l @r15+,macl
    .org 0xc0d20-ORIGIN
L_000c0d20:
    lds.l @r15+,pr
    .org 0xc0d22-ORIGIN
L_000c0d22:
    mov.l @r15+,r14
    .org 0xc0d24-ORIGIN
L_000c0d24:
    mov.l @r15+,r13
    .org 0xc0d26-ORIGIN
L_000c0d26:
    mov.l @r15+,r12
    .org 0xc0d28-ORIGIN
L_000c0d28:
    mov.l @r15+,r11
    .org 0xc0d2a-ORIGIN
L_000c0d2a:
    mov.l @r15+,r10
    .org 0xc0d2c-ORIGIN
L_000c0d2c:
    mov.l @r15+,r9
    .org 0xc0d2e-ORIGIN
L_000c0d2e:
    rts
    .org 0xc0d30-ORIGIN
L_000c0d30:
    mov.l @r15+,r8
    .org 0xc0e42-ORIGIN
L_000c0e42:
    .word 0x09e8
    .org 0xc0ebc-ORIGIN
L_000c0ebc:
    .long 0xffff2324
    .org 0xc0ec0-ORIGIN
L_000c0ec0:
    .long 0xffff128c
