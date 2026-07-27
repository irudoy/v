# Rom an al500

> Local mirror of a NissanECU RE wiki page. Source: https://nissanecu.miraheze.org/wiki/Rom_an_al500
> Retrieved: 2026-07-15. License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) ()

---

## general info

metadata and features automatically found by nisrom. Notes: 

  * "ofs" means "offset" => location in ROM
  * "&" prefix means "address of" (same thing !)
  * "cks" means "checksum"
  * checksum suffixes "_s" and "_x" are respectively the sum and xor totals. See <https://nissanecu.miraheze.org/wiki/Checksums>

size  | 512k   
---|---  
LOADER ##  | N/A   
LOADER ofs  | N/A   
LOADER CPU  | N/A   
LOADER CPUcode  | N/A   
&FID  | 0xB8CC   
FID  | M1ZVDABDQ   
FID CPU  | SH7055   
FID CPUcode  | 07  
RAMF_weird  | 0  
RAMjump entry  | 0xFFFF8424   
IVT2  | 0xFFFFFFFF   
IVT2 confidence  | 0  
std cks?  | 1  
&std_s  | 0x44ac   
&std_x  | 0x4498   
alt cks?  | 1  
&alt_s  | 0x400   
&alt_x  | 0x404   
alt_start  | 0x408   
&alt_end  | 0x2016   
alt2 cks?  | 0  
&alt2_s  | N/A   
&alt2_x  | N/A   
alt2_start  | N/A   
RIPEMD160  | 0  
known keyset  | 1  
s27k  | 0x3E29F056   
s36k  | 0x27F83D70   
&EEPROM_read()  | 0x3F300   
EEPROM PORT  | 0xFFFFF766   
  
## similar ROMs

## Function list

### Notes

Main calltable is from 0x1360 to 0x16E0 

### List
    
    
    INT_ATU31_IMI3A     0x00000408
    calltable_worker1   0x000008C6
    std_cks             0x00001008
    std_cks_1step       0x000010C6
    std_cks_verify      0x00001138
    std_cks_save        0x0000115C
    altcks_prep         0x00001194
    altcks_1            0x000011BA
    altcks_verify       0x00001280
    altcks_save         0x000012B2
    div_1864            0x00001864
    div1                0x00001918
    div_19C0            0x000019C0
    memcpy3b?           0x00001A88
    memcpy3?            0x00001A94
    memcpy2?            0x00001B2C
    memcpy1             0x00001BEC
    shift1              0x00001C44
    shift2              0x00001D04
    ADC_read1           0x00002070
    DTC_check_f2        0x000024DC
    RDtable_b_4bX4b_1   0x000029F0
    RDtable_b_4bX4b_0   0x00002A24
    RDtable_b_4bX4w     0x00002A68
    RDtable_b_4bX4b     0x00002AA4
    RDtable_b_8bX8b_1   0x00002ADC
    RDtable_b_8bX8b_0   0x00002B10
    RDtable_b_8bX8w     0x00002B44
    RDtable_b_8bX8b_2   0x00002B80
    RDtable_b_8bX8b     0x00002BB8
    RDtable_b_16bX16b_3 0x00002BF0
    RDtable_b_16bX16w   0x00002C24
    RDtable_b_16bX16b_2 0x00002C60
    RDtable_b_16bX16b   0x00002C98
    RDtable_w_8wX8w     0x00002CD0
    RDtable_w_16wX16w   0x00002D04
    RDtable_w_16bX16w   0x00002D38
    RDtable_w_16bX16w_2 0x00002D74
    RDax_16b?           0x00002DE0
    RDax_32b?           0x00002DF8
    RDax_8w             0x00002E28
    RDax_16w            0x00002E40
    RDax_32w?           0x00002F80
    interp_b_32d0       0x000032D0
    interp_w            0x00003310
    interp_b_3350       0x00003350
    interp_b            0x00003394
    div_35f0            0x000035F0
    PL5_toggle          0x0000CC1C
    INT_WDT_ITI         0x0000CE8C
    NMI                 0x0000D0D4
    Poweron_Reset       0x0000D120
    ADC_get_set1        0x0000D200
    ADC_get_set2        0x0000D268
    INT_ATU31_IMI3C     0x0000D73C
    INT_ATU02_ICI0A     0x0000E05C
    INT_ATU12_IMI1AE    0x0000F04E
    INT_ATU12_IMI1AF    0x0000F324
    INT_ATU11_IMI11A    0x0000F884
    INT_ATU11_IMI11B    0x0000FCF0
    INT_ATU11_IMI1AA    0x000107CC
    INT_ATU11_IMI1AC    0x00010958
    INT_ATU81_OSI8A     0x00011BA6
    INT_ATU81_OSI8B     0x00011C88
    INT_ATU81_OSI8C     0x00011D7A
    INT_ATU81_OSI8D     0x00011E68
    INT_ATU82_OSI8E     0x00011F34
    INT_ATU82_OSI8F     0x00012026
    INT_ATU83_OSI8I     0x000134D0
    INT_ATU83_OSI8J     0x0001355E
    INT_ATU83_OSI8K     0x0001360C
    INT_ATU12_IMI1AG    0x0001369A
    INT_ATU31_IMI3D     0x0001424C
    DTC_clr_f2_1        0x000149E2
    SCImach_worker?     0x00014A60
    iso14230_normal     0x00014B6C
    INT_SCI1_RXI1       0x00014FF0
    INT_SCI1_TXI1       0x0001538C
    INT_SCI1_TEI1       0x000153E4
    analyze_SCI1_RX?    0x00015708
    iso14230_alt?       0x00015BE8
    tx_7F_negresp       0x00019328
    sid27_prepkey       0x00019D80
    sid36_decrypt       0x00019DCC
    encr_mess1          0x00019E54
    encr_swapf          0x00019E74
    encr_mess2          0x00019EA8
    MAF_stuff1          0x0001CEB0
    set_BFR6A           0x0001EF90
    INT_DMAC2_DEI2      0x0002504A
    eeprom_ERAL         0x0003F124
    eeprom_write        0x0003F204
    eeprom_read         0x0003F300
    eeprom_read2        0x0003F524
    eeprom_EWEN         0x0003FCC8
    eeprom_EWDS         0x0003FDA0
    INT_HCAN1_OVR1      0x0004040C
    INT_ATU31_IMI3B     0x00043E54
    INT_ATU41_IMI4A     0x0004CC00
    INT_ATU41_IMI4B     0x0004CD30
    INT_ATU41_IMI4C     0x0004CE68
    INT_ATU41_IMI4D     0x0004CFA4
    APS_stuff_0         0x0004FEF4
    APS_copyvals        0x0004FF22
    APS_ddt             0x0004FF68
    DTC_set             0x0005A49C
    APS1_checkrange     0x00066AF0
    APS2_checkrange     0x00066B60
    APS_stuff           0x00066D32
    APS1_stuff          0x000695F4
    INT_SCI0_RXI0       0x0006B318
    INT_TRAPA32         0x0006C308
    INT_ATU12_IMI1AH    0x0006C91C
    INT_ATU02_ICI0B     0x00070498
    
    

## Map list

See other sections for size information for these 
    
    
    map	axis0	axis1
    
    474e	85bc	85ac
    484e	85bc	85ac
    488e	85a4	859c
    48ce	85bc	85ac
    49ce	8594	858c
    4a0e	887c	8884
    4a4e	887c	8884
    4a8e	8409	846d
    4ace	8409	846d
    4b0e	8409	846d
    4b4e	8409	846d
    4c8e	8ada	85d0
    4dde	8355	91fc
    4e22	82a8	82ac
    4e32	8311	830d
    4e42	8411	8475
    4e52	8411	8475
    4e62	8411	8475
    4e72	8411	8475
    4e82	883c	885c
    4f82	884c	886c
    5082	887c	8884
    50c2	8445	82bf
    5142	8445	82bf
    5242	8311	830d
    5252	8315	831d
    5292	8315	831d
    52d2	8315	831d
    5312	82fd	8305
    5352	82fd	8305
    5492	8f8c	a52e
    54d2	8f94	a53e
    55d2	8415	8479
    57d2	8425	8365
    5962	9028	902c
    5972	9028	902c
    5982	8704	870c
    59c2	9029	a51e
    59d2	9024	a526
    5b42	8f8c	a52e
    5b82	8f94	a53e
    5bc2	8425	8365
    5c12	8f8c	a52e
    5c52	8f94	a53e
    5c92	8fc8	a4de
    5d92	8fd8	a4fe
    5e92	8378	9262
    5ea2	837c	926a
    5ee2	8ba6	8bae
    62b6	8435	90a8
    64b6	a41e	a19e
    6536	a41e	a19e
    69b6	92ec	977a
    6a36	92ec	977a
    6ab6	92fc	97ca
    6b36	92fc	97ca
    6bb6	83e9	97aa
    71b6	92fc	97ca
    7236	928c	92ac
    7436	928c	92ac
    7636	8435	934c
    7a36	965a	967a
    7ab6	965a	967a
    7B36	966a	968a
    7bb6	966a	968a
    7C36	978A	979A
    a24e	a30e
    a28e	a34e
    A2CE	9068
    
    

## Misc data stored in ROM

Note, some of these are not listed in the previous "maps" section. 
    
    
    altcks_sum          00000400
    altcks_xor          00000404
    eep_retries         00003C50
    std_cks_xor         00004498
    std_cks_sum         000044AC
    
    t_b_16x16_474E      0000474E
    t_b_8x8_484E        0000484E
    t_b_8x8_488E        0000488E
    t_b_16x16_48CE      000048CE
    t_b_8x8_49CE        000049CE
    tb_8x8_4A0E         00004A0E
    tb_8x8_4A4E         00004A4E
    tb_8x8_4A8E         00004A8E
    tb_8x8_4ACE         00004ACE
    tb_8x8_4B0E         00004B0E
    tb_8x8_4B4E         00004B4E
    tb_8x8_4C8E         00004C8E
    tb_8x8_4DDE         00004DDE
    tb4x4_4E22          00004E22
    tb_4x4_4E32         00004E32
    tb_4x4_4E42         00004E42
    tb_4x4_4E52         00004E52
    tb_4x4_4E62         00004E62
    tb_4x4_4E72         00004E72
    tb_16x16_4E82       00004E82
    tb_16x16_4F82       00004F82
    tb_8x8_5082         00005082
    tb_8x8_50C2         000050C2
    tb_8x8_5142         00005142
    tb4x4_5242          00005242
    tb_8x8_5252         00005252
    tb_8x8_5292         00005292
    tb_8x8_52D2         000052D2
    tb_8x8_5312         00005312
    tb_8x8_5352         00005352
    tb_8x8_5492         00005492
    tb_8x8_54D2         000054D2
    t_b_16x16_55D2      000055D2
    zt_256b_56d2        000056D2
    tb_4x4_57D2         000057D2
    utb_8x8_57e2        000057E2
    utb_8x8_5822        00005822
    ut_256b_5862        00005862
    tb_4x4_5962         00005962
    tb_4x4_5972         00005972
    tb_8x8_5982         00005982
    tb_4x4_59C2         000059C2
    tb_4x4_59D2         000059D2
    tb_8x8_5B42         00005B42
    tb_8x8_5B82         00005B82
    tb_4x4_5BC2         00005BC2
    ut_64b_5bd2         00005BD2
    tb_8x8_5C12         00005C12
    tb_8x8_5C52         00005C52
    tb16x16_5C92        00005C92
    tb16x16_5D92        00005D92
    tb_4x4_5E92         00005E92
    tb_8x8_5EA2         00005EA2
    tb_8x8_5EE2         00005EE2
    utb_8x8_5f22        00005F22
    zt_256b_5f62        00005F62
    utb_8x8_6162        00006162
    tb_4x4_61A2         000061A2
    t_w_16x16_62B6      000062B6
    t_w_8x8_64B6        000064B6
    t_w_8x8_6536        00006536
    t_w_8x8_69B6        000069B6
    t_w_8x8_6A36        00006A36
    t_w_8x8_6AB6        00006AB6
    t_w_8x8_6B36        00006B36
    t_w_16x16_6BB6      00006BB6
    t_w_16x16_6DB6      00006DB6
    u_256w_6FB6         00006FB6
    t_w_8x8_71B6        000071B6
    t_w_16x16_7236      00007236
    t_w_16x16_7436      00007436
    t_w_16x16_7636      00007636
    u_256w_7836         00007836
    t_w_8x8_7A36        00007A36
    t_w_8x8_7AB6        00007AB6
    t_w_8x8_7B36        00007B36
    t_w_8x8_7BB6        00007BB6
    t_w_8x8_7C36        00007C36
    t_w_16x16_7CB6      00007CB6
    
    ax_16w_7EB6         00007EB6
    ax_16w_7ED6         00007ED6
    ax_16w_7EF6         00007EF6
    ax_16w_7F16         00007F16
    ax_16w_7F36         00007F36
    ax_16w_7F56         00007F56
    ax_8w_7FB6          00007FB6
    ax4b_82A8           000082A8
    ax4b_82AC           000082AC
    
    ECUID               000082B9
    
    ax8b_82BF           000082BF
    ax8b_82fd           000082FD
    ax8b_8305           00008305
    ax4b_830D           0000830D
    ax4b_8311           00008311
    ax8b_8315           00008315
    ax8b_831D           0000831D
    ax8b_8355           00008355
    ax4b_8365           00008365
    ax4b_8378           00008378
    ax8b_837C           0000837C
    ax_16b_83E9         000083E9
    ax8b_8409           00008409
    ax4b_8411           00008411
    ax_16b_8415         00008415
    ax4b_8425           00008425
    ax_16b_8435         00008435
    ax8b_8445           00008445
    ax8b_846D           0000846D
    ax4b_8475           00008475
    ax_16b_8479         00008479
    
    CID1100_supmask     000084AB
    CID1140_supmask     000084AF
    CID1160_supmask     000084B3
    CID1120_supmask     000084B7
    CID1400_supmask     000084BB
    CID1420_supmask     000084BF
    CID1200_supmask     000084C3
    CID1220_supmask     000084C7
    CID1300_supmask     000084CB
    CID1500_supmask     000084CF
    SID30_LIDmask       000084D3
    SID21_LIDmask       000084E3
    SID3B_supmask       000084EB
    
    ax_8b_858C          0000858C
    ax_8b_8594          00008594
    ax_8b_859C          0000859C
    ax_8b_85A4          000085A4
    ax_16b_85AC         000085AC
    ax_16b_85BC         000085BC
    ax8b_85D0           000085D0
    ax8b_8704           00008704
    ax8b_870C           0000870C
    ax16b_883C          0000883C
    ax16b_884C          0000884C
    ax16b_885C          0000885C
    ax16b_886c          0000886C
    ax8b_887C           0000887C
    ax8b_8884           00008884
    ax8b_8ADA           00008ADA
    ax8b_8BA6           00008BA6
    ax8b_8BAE           00008BAE
    ax8b_8F8C           00008F8C
    ax8b_8F94           00008F94
    ax16b_8fc8          00008FC8
    ax16b_8FD8          00008FD8
    ax4b_9020           00009020
    ax4b_9024           00009024
    ax4b_9028           00009028
    ax4b_902C           0000902C
    ax_32w_9068         00009068
    ax_16w_90A8         000090A8
    ax8w_91FC           000091FC
    ax4w_9262           00009262
    ax8w_926A           0000926A
    ax_16w_928C         0000928C
    ax_16w_92AC         000092AC
    ax_8w_92EC          000092EC
    ax_8w_92FC          000092FC
    ax_16w_934C         0000934C
    MAF_LUT?            0000936C
    ax_8w_965A          0000965A
    ax_8w_966A          0000966A
    ax_w_967A           0000967A
    ax_8w_968a          0000968A
    ax_8w_977A          0000977A
    ax_8w_978A          0000978A
    ax_8w_979A          0000979A
    ax_16w_97AA         000097AA
    ax_8w_97CA          000097CA
    ax_8w_a19e          0000A19E
    t_w_1x32_A24E       0000A24E
    t_w_1x32_A28E       0000A28E
    t_w_1x32_A2CE       0000A2CE
    ax_32w_A30E         0000A30E
    ax_32w_A34E         0000A34E
    ax_8w_a41e          0000A41E
    ax16w_A4DE          0000A4DE
    ax16w_A4FE          0000A4FE
    ax4w_A51E           0000A51E
    ax4w_a526           0000A526
    ax8w_A52E           0000A52E
    ax8w_A53E           0000A53E
    
    DTC_descriptors     0000B12C
    DTC_options         0000B6E4
    struct_FID          0000B8CC
    struct_RAMF         0000B91C
    
    CID1100_table       0000B9E8
    CID1120_table       0000BA68
    CID1140_table       0000BAE8
    CID1160_table       0000BB68
    CID1200_table       0000BBBC
    CID1220_table       0000BC3C
    CID1300_table       0000BC80
    CID1400_table       0000BD10
    CID1420_table       0000BD90
    CID1500_table       0000BD98
    SID21_LIDtable      0000BDF0
    SID30_LIDtable      0000BE08
    SID3B_table         0000BEEC
    
    tw_1x256_BEF8       0000BEF8
    ax_16_b             0000C5D4
    ax_12_w             0000C5E4
    ax_14_w             0000C5FC
    
    s36k2_halfkey1      00019B6C
    s36k2_halfkey2      00019BA0
    s27_halfkey1        00019E8C
    s36k1_halfkey1      00019E8E
    s36k1_halfkey2      00019E90
    s27_halfkey2        00019E98
    
    

## Misc data stored in RAM
    
    
    CID1204_MAF_V       FFFF844E
    CID1201_RPM         FFFF85DC
    CID120D_APS1        FFFF9B0C
    CID120E_APS2        FFFF9B10
    CID1209_MAF_gs      FFFFA0AC
    tmrblock_a5aa       FFFFA5AA
    tmrblock_a61e       FFFFA61E
    DTC_status          FFFFAEA6
