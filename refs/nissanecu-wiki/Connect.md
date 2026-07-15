# Connect

> Зеркало страницы NissanECU RE wiki. Источник: https://nissanecu.miraheze.org/wiki/Connect
> Retrieved: 2026-07-15. License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) ()

---

# Connecting to Consult-II ECUs

Currently it seems the most straightforward way to connect to these ECUs is through the K line of the OBD2 connector. On more recent vehicles it is probably possible to accomplish the same thing through the OBD2 CAN lines. These are not populated on some vehicles. 

## K line

### OBD-2 (SAE J1979) comms over ISO-9141

Some ECUs support J1979-compliant OBD2 traffic on the K line with the ISO 9141 protocol. This allows only basic, generic stuff like reading / clearing DTCs, freeze frame data etc. This iso9141 connection is established with a standard 5bps "slow init" with 0x33 as the functional address. This is of limited interest for reflashing. 

### "Consult-II" over ISO-14230

On the same K line the ECUs support the "Consult-II" (C2) mode, which is implemented on an iso 14230 protocol. This means : 

  * Connection is established and maintained according to iso 14230
  * The mandatory SID 3E is supported (TesterPresent , used as a "keepalive")
  * Some standard SIDs are supported (1A ReadECUIdentification, 21 RDBLI, 22 RDBCI, 27 SecurityAccess, etc.)
  * Some mfg-specific SIDs are implemented (A0, A3, AC)



Some of the standard SIDs have mfg-specific extensions, such as SID 1A with IDOPT 0x81. This is OK, since iso 14230 says IDOPT 0x80-0xFF are ManufacturerSpecific. See the [C2 protocol page](<https://nissanecu.miraheze.org/wiki/C2_14230> "C2 14230") for more info. 

To connect to the ECU : speed is 10.4kbps, ISO14230 fast init with Tester addr = 0xFC, dest addr = 0x10, using physical addressing. Example StartCommunications request (sent after the fast init "wakeup pattern") : 
    
    
    host req: 0x81 0x10 0xFC 0x81 cks1
    ECU resp: 0x83 0xFC 0x10 0xC1 0xD5 0x8F cks1
    

Note : some ECUs may use slightly different parameters (one USDM Titan 04 required functional address 0x10). freediag / nisprog have a "fastprobe" command that can assist in finding the correct address. 

Usually (always ?) the ECU will support "addressless headers" according to the keywords returned during init. Refer to the 14230 docs for details. Example of an addressless keepalive (TesterPresent) request : 
    
    
    TX 0x01 0x3E cks1
    RX 0x01 0x7E cks1
    

There is a tool to assist with connection and speaking with ECUs - [nisprog](<https://nissanecu.miraheze.org/wiki/Tools#nisprog> "Tools") a.k.a. freediag. 

# Direct connection to SH705x-family uCs

This assumes direct physical access to the mcu, i.e. unsealing the ECU to get to the circuit itself. Applicable to SH7051, SH7055, SH7058, probably others. 

## SHBootmode

The so-called "SHBootmode" method actually consists in setting the mcu to run in "Boot Mode", which is described in the Renesas datasheets. Subaru tuners have been using this technique to unbrick ECUs for years. However the process is slightly different on Nissan ECUs, because of different hardware. See [SHBootmode](<https://nissanecu.miraheze.org/wiki/Bootmode> "Bootmode") page for more info. 

## AUD

AUD is the "Advanced User Debugger" hardware port on these mcus. Not available on SH7051. There are two modes of operation: 

  * Branch trace mode : the AUD port outputs the PC address for every branch / jump / function call.
  * RAM monitor mode : the AUD port accepts commands to read/write to the RAM. This mode has also been used succesfully to dump the entire ROM.



Further information can be found on the [AUD page](<https://nissanecu.miraheze.org/wiki/AUD> "AUD")
