# Rom an cf43d

> Зеркало страницы NissanECU RE wiki. Источник: https://nissanecu.miraheze.org/wiki/Rom_an_cf43d
> Retrieved: 2026-07-15. License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) ()

---

## general info

metadata and features automatically found by nisrom. Notes: 

  * "ofs" means "offset" => location in ROM
  * "&" prefix means "address of" (same thing !)
  * "cks" means "checksum"
  * checksum suffixes "_s" and "_x" are respectively the sum and xor totals. See <https://nissanecu.miraheze.org/wiki/Checksums>



  


size  | 1024k   
---|---  
LOADER ##  | 60  
LOADER ofs  | 0x1C1C   
LOADER CPU  | SH7058   
LOADER CPUcode  | 23  
&FID  | 0x4168   
FID  | 6GI5VN6   
FID CPU  | SH7058   
FID CPUcode  | 23  
RAMF_weird  | 0  
RAMjump entry  | 0xFFFF8438   
IVT2  | 0x2000   
IVT2 confidence  | 0.99  
std cks?  | 1  
&std_s  | 0x8C54   
&std_x  | 0x8C4C   
alt cks?  | 1  
&alt_s  | 0x240C   
&alt_x  | 0x2410   
alt_start  | 0x2414   
&alt_end  | 0x4166   
alt2 cks?  | 0  
&alt2_s  | N/A   
&alt2_x  | N/A   
alt2_start  | N/A   
RIPEMD160  | 0  
known keyset  | 1  
s27k  | 0x634D157A   
s36k  | 0x4B1D6294   
&EEPROM_read()  | 0x4EAF4   
EEPROM PORT  | 0xFFFFF766   
  
## similar ROMs

CM31C : 930 changed bytes; concentrated in the area from 0x7BAF to 0xDD8A (maps, probably) 

## Function list

### Notes

The main calltables are at 0x33B8 to 0x3770; 

### List
    
    
    Poweron_Reset	00000104
    alt_select_sidtree	00000484
    alt_SCI1_setup	00000696
    alt_iso14230_tree2	000006C6
    alt_iso14230_tree	00000966
    alt_SID3E	000012BE
    alt_SID27	000012D4
    alt_SID1A	00001644
    alt_SIDBF	000018BC
    alt_SID37	00001926
    alt_s27_prepkey	00001A7C
    alt_s36_decr	00001AC8
    alt_encr_mess1	00001B6E
    alt_encr_swapf	00001B90
    alt_encr_mess2	00001B9A
    alt_ramjump?	00001C04
    INT_ATU31_IMI3A	00002414
    cks_std	00003034
    std_cks_1step	000030FE
    std_cks_compare	00003186
    std_cks_checkresult	000031B8
    std_cks_DTC	000031F8
    altcks_1	00003278
    alt_cks_compare	00003316
    alt_Poweron_Reset	00003774
    div_1	00003788
    div_2	000038AC
    div_3	0000399C
    memcpy_1	00004124
    DTC_check_f2	00006808
    DTC_get_f2_1	00006A32
    DTC_get_f2_20	00006A52
    get_DTC_f2_10	00006AFE
    DTC_get_f2_02	00006B22
    DTC_get_f1_80	00006D0A
    RDtable_b_4bX4b	00006EC4
    RDtable_?_4bX4b	00006F3C
    RDtable_b_8bX8b	00006F74
    RDtable_b_8bX8b_0	00006FA8
    RDtable_b_16bX16b_0	00006FE0
    RDtable_b_16bX16b_1	00007014
    RDtable_b_16bX16b_2	0000704C
    RDtable_w_8wX8w	00007084
    RDtable_w_16wX16w_0	000070B8
    RDtable_w_16bX16w_0	000070EC
    RDtable_b_16bX16b	00007128
    RDtable_dw_16wx16w	000073E0
    RDtable_w_16bX16w	00007414
    RDtable_w_1x16w??	00007468
    RDtable_w_1x32w?	00007490
    interp8_76b0	000076B0
    interp16_76f0?	000076F0
    interp8_7730	00007730
    interp8_7774	00007774
    interp16_78e4	000078E4
    interp8_7924?	00007924
    div32_1	000079D0
    div32_2?	00007A68
    PL5_toggle	0000FAC2
    INT_WDT_ITI	0000FD2C
    alt_NMI	0000FF7C
    ADC_get12456	000100DC
    ADC_more1	0001013C
    TPS_getAN20	0001050E
    ADC_getfromtable	00010A54
    init_ports_2	00010C3C
    INT_ATU02_ICI0A	00010FB6
    INT_ATU12_IMI1AE	000123D0
    INT_ATU12_IMI1AF	000126B6
    INT_ATU11_IMI11A	00012C1C
    INT_ATU11_IMI11B	00013036
    INT_ATU51_IMI5A	00013488
    INT_ATU51_IMI5B	000135D8
    INT_ATU11_IMI1AB	00013E90
    INT_ATU11_IMI1AA	00013F24
    INT_ATU11_IMI1AC	00014080
    INT_ATU31_IMI3D	00015BD0
    DTC_clear_f2_02	000165C8
    SCI_worker?	00016624
    SCI1_tx	000166E0
    select_SIDtree	0001670A
    tx_stuff	0001699A
    INT_SCI1_RXI1	00016A8C
    INT_SCI1_TXI1	00016DCC
    INT_SCI1_TEI1	00016E20
    iso14230_alt1	00017530
    iso14230_normal	000175D0
    alt_sendFID?	00017F76
    SID14_ClearDiagInfo	00018330
    SIDA0_?	00018384
    SID30_ioctl_LID	00018644
    SID02_readff?	0001910C
    SID06_?	00019118
    SID09_rvi?	00019124
    SID22_ReadDataCID	00019D4C
    SID21_ReadDataLID	0001A290
    SID_A3_??	0001A63C
    SID1A_ECUID	0001A784
    SID12_ReadFF	0001AA0C
    SIDA4_readsingle	0001AB8C
    SID33_RoutResults	0001AE44
    SID27_secu	0001AF30
    SIDAC_readmulti	0001B1C0
    SID32_StopRout_LID	0001B80C
    SID31_StartRout_LID	0001B9B0
    tx_7F	0001BB44
    SID3B_WriteDataLID	0001BBC4
    SID34_ReqDownload	0001BE40
    SID36_TransferData	0001C01C
    SID37_ReqTransfExit	0001C0C4
    SIDBF_RAMjump	0001C184
    SID11_ECUreset	0001C20C
    sid34_dispatch	0001C520
    check_s36cks	0001C758
    die	0001C7F0
    sid27_prepkey	0001C820
    sid36_decrypt	0001C86E
    encr_mess1	0001C906
    encr_swap	0001C928
    encr_mess2	0001C932
    iso9141_stuff1	0001CC28
    iso9141_init	0001CCAC
    iso9141_stuff2	0001CD88
    iso9141_OBDtree1	0001CF10
    OBD_mode1	0001D124
    OBD_mode2	0001D834
    OBD_mode3	0001DA28
    OBD_mode6	0001DBAE
    OBD_mode7	0001E6D4
    OBD_mode8	0001E7D0
    OBD_mode9	0001E8BC
    OBD_queubuf?	0001F210
    OBD_queue_0s	0001F240
    OBD_queuebyte	0001F350
    throt_dcy	00026138
    INT_SCI3_RXI3	000265A0
    INT_DMAC2_DEI2	0002EE6A
    eeprom_ERAL	0004E930
    eeprom_write	0004E9FE
    eeprom_read16	0004EAF4
    eeprom_readw2	0004ED20
    eeprom_EWEN	0004FAAC
    INT_ATU31_IMI3B	000501C6
    APS_stuff2	00055960
    AN19_APS_stuff	0005596A
    APS_copyvals	00055A7C
    APS_ddt	00055AC4
    APS_ddt_parse	00055B3C
    APS1_moar	00055BA2
    APS1_averaging??	00055D40
    DTC_set	00062A0C
    test_every_instr?	00093E70
    INT_TRAPA32	000946E8
    INT_SCI0_RXI0	00095B2C
    INT_SCI2_TXI2	00097CFC
    INT_SCI2_TEI2	00097D4C
    INT_SCI2_RXI2	00097D88
    set_BFR7	0009923C
    INT_ATU41_IMI4C	0009D024
    INT_ATU41_IMI4D	0009D158
    INT_HCAN1_OVR1	0009D5F8
    ASCD_stuff1	000A7110
    
    

## Map list

TODO : format this into a table, with data size information etc 
    
    
    map	axis0	axis1
    
    8ded	b650	b640
    8eed	b650	b640
    8fed	b650	b640
    91cd	b2e1	b2e9
    920d	b2e1	b2e9
    928d	c3d8	c3f8
    92cd	c3d8	c3f8
    934d	b49a	b351
    948d	b4ca	b526
    971d	b4a2	b2f9
    987d	b7d0	b7d8
    98dd	b4da	b381
    98ed	c074	c07c
    992d	c074	c07c
    996d	bd82	bd8a
    99ed	cc2c	c2b4
    9a2d 	c318	c2f8
    9b2d	c328	c308
    9c2d	c2d4	c2bc
    9d0d	b385	b3a5
    9e0d	b385	b3a5
    9f0d	b385	b3a5
    a0a8	c79e	c7be
    a128	c79e	c7be
    a2a8	c7fe	c80e
    a3a8	c75e	c77e
    a5a8	c75e	c77e
    a7a8	b4e6	c81e
    aba8	cb7c	cb9c
    ac28	cb7c	cb9c
    ada8	c602	c5e2
    ae28	c612	c5d2
    aea8	cc8c	cc7c
    d762	ddf8	de18
    d962	ddf8	de18
    db62	dda8	de38
    
    

## Misc data stored in ROM

Note, some of these are not listed in the previous "maps" section. 
    
    
    IVECT2	00001000
    struct_LOADER	00001C1C
    IVT2	00002000
    ECUID_1	00002400
    ECUID_2	00002406
    alt_cks_sum	0000240C
    alt_cks_xor	00002410
    calltable_33B8	000033B8
    calltable_33CC	000033CC
    calltable_3404	00003404
    calltable_3538	00003538
    calltable_3554	00003554
    calltable_3750	00003750
    struct_FID	00004168
    struct_RAMF	000041B8
    ADCtable_4210	00004210
    CID1100_descr	00004330
    CID1120_descr	000043B0
    CID1140_descr	00004430
    CID1160_descr	000044B0
    CID1160_arr	000044B4
    CID12_00_descr	00004520
    CID12_20_descr	000045A0
    CID12_40_descr	00004620
    CID13_00_descr	0000463C
    CID1300_arr	00004640
    CID14_00_descr	000046E4
    CID14_20_descr	00004764
    CID15_00_descr	00004768
    CID16_00_descr	0000480C
    CID16_20_descr	0000488C
    SID21_LIDtable	0000490C
    std_cks_xor	00008C4C
    std_cks_sum	00008C54
    ut_8D1D	00008D1D
    ut_8D5D	00008D5D
    t_b_16x16_8DED	00008DED
    t_b_16x16_8EED	00008EED
    t_b_16x16_8FED	00008FED
    t_b_8x8_91CD	000091CD
    t_b_8x8_920D	0000920D
    ut_924D	0000924D
    t_b_8x8_928D	0000928D
    t_b_8x8_92CD	000092CD
    ut_930d	0000930D
    t_b_8x8_934D	0000934D
    ut_938D	0000938D
    t_b_16x16_948D	0000948D
    ut_958d	0000958D
    ut_969D	0000969D
    t_b_8x8_971D	0000971D
    ut_975d	0000975D
    t_b_4x4_98DD	000098DD
    t_b_8x8_98ED	000098ED
    t_b_8x8_992D	0000992D
    t_b_8x8_996D	0000996D
    ut_99ad	000099AD
    t_b_8x8_99ED	000099ED
    t_b_8x8_9A2D	00009A2D
    t_b_8x8_9B2D	00009B2D
    t_b_8x8_9c2d	00009C2D
    ut_9c6d	00009C6D
    t_b_16x16_9D0D	00009D0D
    t_b_16x16_9E0D	00009E0D
    t_b_16x16_9F0D	00009F0D
    ut_a00d	0000A00D
    t_w_8x8_A0A8	0000A0A8
    t_w_8x8_A128	0000A128
    t_w_8x8_A2A8	0000A2A8
    t_w_16x16_A3A8	0000A3A8
    t_w_16x16_A5A8	0000A5A8
    t_w_16x16_A7A8	0000A7A8
    t_w_8x8_ABA8	0000ABA8
    t_w_8x8_AC28	0000AC28
    ut8x8w_ACA8	0000ACA8
    ut8x8w_AD28	0000AD28
    t_w_8x8_ADA8	0000ADA8
    t_w_8x8_AEA8	0000AEA8
    OBD_1_00_mask	0000B2C9
    OBD_1_20_mask	0000B2CD
    OBD_2_00_mask	0000B2D1
    CID1100_supmask	0000B563
    CID1140_supmask	0000B567
    CID1160_supmask	0000B56B
    CID1120_supmask	0000B56F
    CID1400_supmask	0000B573
    CID1420_supmask	0000B577
    CID1200_supmask	0000B57B
    CID1220_supmask	0000B57F
    CID1240_supmask	0000B583
    CID1300_supmask	0000B587
    CID1500_supmask	0000B58B
    CID1600_supmask	0000B58F
    CID1620_supmask	0000B593
    LID30_00_supm	0000B597
    LID30_20_supm	0000B59B
    LID30_40_supm	0000B59F
    LID30_60_supm	0000B5A3
    t16?_1x8_CD6C	0000CD6C
    t16?_1x8_CD7C	0000CD7C
    t16?_1x8_CF98	0000CF98
    t16?_1x8_CFC2	0000CFC2
    t16u_1x32_D1C2	0000D1C2
    ax_8_?16_D412	0000D412
    ax_8_?16_D422	0000D422
    ax_8_?16_D432	0000D432
    ax_8_?16_D442	0000D442
    t16u_16x16_D762	0000D762
    t16u_16x16_D962	0000D962
    t16u_16x16_DB62	0000DB62
    ax_16_u8_DDA8	0000DDA8
    ax_32_u16_DDB8	0000DDB8
    ax_16_u16_DDF8	0000DDF8
    ax_16_u16_DE18	0000DE18
    ax_16_u8_DE38	0000DE38
    t16u_1x16_DE58	0000DE58
    t16u_1x16_DE78	0000DE78
    t16u_1x16_DE98	0000DE98
    t16u_1x16_DEB8	0000DEB8
    t16u_1x16_DED8	0000DED8
    ax_32_u16_DEF8	0000DEF8
    ax_32_u16_DF38	0000DF38
    t16u_1x32_DF78	0000DF78
    t16u_1x32_DFB8	0000DFB8
    t16u_1x32_E002	0000E002
    t16u_1x16_E042	0000E042
    t16u_1x16_E062	0000E062
    t16u_1x16_E082	0000E082
    t16u_1x16_E0A2	0000E0A2
    DTC_descriptors	0000E0C4
    DTC_options	0000ED78
    
    s36k2_halfkey1	0001C654
    s36k2_halfkey2	0001C656
    s27_halfkey1	0001C96E
    s27_halfkey2	0001C970
    s36k1_halfkey1	0001C974
    s36k1_halfkey2	0001C976
    
    ROMvalid_flag?	000FFF80
    ROMsignature_NHU	000FFF84
    
    

## Misc data stored in RAM
    
    
    ADCset1_r322c	FFFF322C	
    AN1_copy	FFFF3230	
    tmrblock_3BD4	FFFF3BD4	
    SCI1_rxbuf	FFFF8000	
    isomsg_data	FFFF8003	
    DTC_curstatus	FFFFB21C
