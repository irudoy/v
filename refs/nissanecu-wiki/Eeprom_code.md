# Eeprom code

> Зеркало страницы NissanECU RE wiki. Источник: https://nissanecu.miraheze.org/wiki/Eeprom_code
> Retrieved: 2026-07-15. License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) ()

---

# EEPROM access functions analysis

On many ROMs, the SPI EEPROM is accessed through software functions that bit-bang the SPI protocol without using a dedicated SPI peripheral of the mcu. Other ROMs use SCI2 instead (EC87A ?) 

Without opening the ECU, it's usually possible to discover the "spi_readw" function by observing this pattern - 

  1. spi_readw() takes r4.b as the 8-bit address to be read, and r5 as the address to store the read u16 value.
  2. spi_readw() is called *very often*, and so far many ROMs seem to have this access pattern somewhere : (compare code from an HR16DE type D ECU, with a QG18DE type A ECU (different ICs, different PCBs) : (notice the 4 calls to "spi_readw"


    
    
    ********* HR16DE - EC82A (SH7055)
    ROM:000456AC sub_456AC:                              ; CODE XREF: ROM:0000DC8C�p
    ROM:000456AC                                         ; sub_12044+36�p
    ROM:000456AC                                         ; DATA XREF: ...
    ROM:000456AC                 sts.l   pr, @-r15
    ROM:000456AE                 stc.l   gbr, @-r15
    ROM:000456B0                 mov.w   @(h'60,pc), r0 ; [00045714] = h'FFFFD4D8
    ROM:000456B2                 ldc     r0, gbr
    ROM:000456B4                 mov.w   @(h'5E,pc), r2 ; [00045716] = h'5AB6
    ROM:000456B6                 jsr     @r2 ; sub_5AB6
    ROM:000456B8                 mov     #h'59, r4 ; 'Y'
    ROM:000456BA                 tst     r0, r0
    ROM:000456BC                 bf      loc_456F0
    ROM:000456BE                 mov.b   @(h'E6,gbr), r0
    ROM:000456C0                 tst     #h'80, r0
    ROM:000456C2                 bf      loc_456F0
    ROM:000456C4                 stc     gbr, r5
    ROM:000456C6                 mov.l   @(h'54,pc), r2 ; [0004571C] = spi_readw??
    ROM:000456C8                 add     #4, r5
    ROM:000456CA                 jsr     @r2 ; spi_readw??
    ROM:000456CC                 mov     #3, r4
    ROM:000456CE                 mov.l   @(h'4C,pc), r2 ; [0004571C] = spi_readw??
    ROM:000456D0                 mov     #h'7B, r4 ; '{'
    ROM:000456D2                 stc     gbr, r5
    ROM:000456D4                 jsr     @r2 ; spi_readw??
    ROM:000456D6                 add     #h'50, r5 ; 'P'
    ROM:000456D8                 mov.l   @(h'40,pc), r2 ; [0004571C] = spi_readw??
    ROM:000456DA                 mov     #4, r4
    ROM:000456DC                 stc     gbr, r5
    ROM:000456DE                 jsr     @r2 ; spi_readw??
    ROM:000456E0                 add     #6, r5
    ROM:000456E2                 mov.l   @(h'38,pc), r2 ; [0004571C] = spi_readw??
    ROM:000456E4                 mov     #h'7C, r4 ; '|'
    ROM:000456E6                 stc     gbr, r5
    ROM:000456E8                 jsr     @r2 ; spi_readw??
    ROM:000456EA                 add     #h'52, r5 ; 'R'
    
    ********* QG18DE - 6Z68A (SH7058)
    ROM:0004BA54 sub_4BA54:                              ; CODE XREF: ROM:0000C3D6�p
    ROM:0004BA54                                         ; sub_10ACC+46�p
    ROM:0004BA54                                         ; DATA XREF: ...
    ROM:0004BA54                 sts.l   pr, @-r15
    ROM:0004BA56                 stc.l   gbr, @-r15
    ROM:0004BA58                 mov.w   @(h'64,pc), r0 ; [0004BAC0] = h'FFFFB0E0
    ROM:0004BA5A                 ldc     r0, gbr
    ROM:0004BA5C                 mov.w   @(h'62,pc), r2 ; [0004BAC2] = h'5A02
    ROM:0004BA5E                 jsr     @r2 ; sub_5A02
    ROM:0004BA60                 mov     #h'66, r4 ; 'f'
    ROM:0004BA62                 tst     r0, r0
    ROM:0004BA64                 bf      loc_4BA9A
    ROM:0004BA66                 mov.w   @(h'5A,pc), r6 ; [0004BAC4] = h'FFFFB50E
    ROM:0004BA68                 mov.b   @(3,r6), r0
    ROM:0004BA6A                 tst     #h'80, r0
    ROM:0004BA6C                 bf      loc_4BA9A
    ROM:0004BA6E                 stc     gbr, r5
    ROM:0004BA70                 mov.l   @(h'58,pc), r2 ; [0004BACC] = spi_readw?
    ROM:0004BA72                 add     #4, r5
    ROM:0004BA74                 jsr     @r2 ; spi_readw?
    ROM:0004BA76                 mov     #3, r4
    ROM:0004BA78                 mov.l   @(h'50,pc), r2 ; [0004BACC] = spi_readw?
    ROM:0004BA7A                 mov     #h'7B, r4 ; '{'
    ROM:0004BA7C                 stc     gbr, r5
    ROM:0004BA7E                 jsr     @r2 ; spi_readw?
    ROM:0004BA80                 add     #h'50, r5 ; 'P'
    ROM:0004BA82                 mov.l   @(h'48,pc), r2 ; [0004BACC] = spi_readw?
    ROM:0004BA84                 mov     #4, r4
    ROM:0004BA86                 stc     gbr, r5
    ROM:0004BA88                 jsr     @r2 ; spi_readw?
    ROM:0004BA8A                 add     #6, r5
    ROM:0004BA8C                 mov.l   @(h'3C,pc), r2 ; [0004BACC] = spi_readw?
    ROM:0004BA8E                 mov     #h'7C, r4 ; '|'
    ROM:0004BA90                 stc     gbr, r5
    ROM:0004BA92                 jsr     @r2 ; spi_readw?
    ROM:0004BA94                 add     #h'52, r5 ; 'R'
    
    

My method for finding this code is to locate a line that does 
    
    
    mov     #h'7B, r4
    

then inspect all the occurences and find code similar to above (4 calls to spi_readw() in a row !). It would appear that the layout inside the EEPROM is very similar accross generations. I.e. the same value (unknown for now) is stored at address 0x7B, for any generation / hardware revision. 

Analysis of the spi_readw() function will reveal what port and what pins are used for the CS, DI, DO and CK signals.
