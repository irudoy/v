# SH7058S native boot recovery harness

This KiCad project documents the bench wiring used to enter the native boot
loader of the SH7058S ECUs represented by JK00D and JK08A.

J1 represents the measured 12-position ECU PCB testpoint group rather than a
fitted connector. The signal mapping and the shared ground and 12 V rails are
verified on the target board. Do not probe MCU pins directly.

## Project files

- `sh7058-native-boot-recovery.kicad_pro` - KiCad project.
- `sh7058-native-boot-recovery.kicad_sch` - source schematic.
- `sh7058-native-boot-recovery.kicad_pcb` - empty board placeholder created by
  KiCad; no recovery PCB is defined.
- `sh7058-native-boot-recovery.pdf` - printable schematic.
- `sh7058-native-boot-recovery.svg` - vector preview.
- `sh7058-native-boot-recovery.png` - raster preview.

## ECU PCB testpoint group J1

| Position | PCB signal | MCU reference | Harness use |
| ---: | --- | --- | --- |
| 1 | `nRES` | pin 58 | R4 and momentary SW2 to GND |
| 2 | `WDT_IN` | board resistor path to PL5, pin 221 | R5 from the selected WDT source |
| 3 | `SCI1_RX` | PC1 / RxD1, pin 166 | USB-UART TXD through R1 |
| 4 | `MD1` | pin 55 | R3 and SW1 to GND |
| 5 | `SCI1_TX` | PC0 / TxD1, pin 165 | USB-UART RXD through R2 |
| 6 | `PB14` | pin 162 | do not connect |
| 7 | unidentified | none established | do not connect |
| 8 | `TP84`, 5 V | board 5 V rail | monitor only |
| 9 | GND | board ground | common bench ground |
| 10 | GND | board ground | optional second ground |
| 11 | `TP83`, 12 V | ECU input power network | monitor only |
| 12 | `TP82`, 12 V | ECU input power network | monitor only |

Positions 9 and 10 are one ground net. Positions 11 and 12 are one 12 V net.
ECU power is applied through J6, not through J1 positions 8, 11, or 12.

R1 through R4 are provisional service resistors and require board verification.
R1 and R2 are 22 ohm in the drawing; R3 and R4 are specified as <=22 ohm. R5
is the 10 ohm reference value from the archived recovery circuit.

## Interfaces

The USB-UART adapter uses 19200 8N1 and must have a 5 V compatible TX level.
Only TXD, RXD, and GND are connected. Adapter VCC remains disconnected. This is
TTL-level SCI, not RS-232.

The WDT source is selected by fitting exactly one jumper:

- JP1 selects Arduino Uno/Nano D9 / OC1A or Mega 2560 D9 / OC2B at 250 Hz,
  50% duty cycle, and 5 V.
- JP2 selects an STM32 timer output at 240-250 Hz and 50% duty cycle through a
  74AHCT1G125 powered from the regulated 5 V input on J5.

For an Arduino Mega 2560, D9 is PH6 / OC2B. The project sketch at
`arduino-mega-wdt/arduino-mega-wdt.ino` configures Timer2 for exactly 250 Hz,
50% duty cycle, and 0-5 V output on D9. It does not use interrupts or software
delays. The waveform starts during `setup()` and continues until the board is
reset or loses power. A bench measurement at D9 confirms 2 ms HIGH, 2 ms LOW,
and 5 V amplitude, verifying 250 Hz, 50% duty cycle, and 0-5 V output.

J6 represents the verified ECU bench harness for BATT, IGN, and GND. It is the
only ECU power entry shown. J5 powers only the 5 V logic buffer. J7 provides
oscilloscope access to `WDT_IN`, `nRES`, and GND.

The baseline circuit does not include a second SCI interlock. It can be added
only if a specific ECU or ROM is shown to require it.

## Manual UART tools

The dependency-free scripts under `scripts/` use a POSIX serial device directly.
They configure 8N1 with no software or hardware flow control.

Test the USB-UART adapter only after disconnecting its TX and RX wires from the
ECU and shorting the adapter pins together:

```bash
./scripts/uart_loopback.py /dev/cu.wchusbserial1220 --loopback-connected
```

After reconnecting TXD to J1 position 3, RXD to J1 position 5, and GND, enter
native boot mode and run the inquiry immediately after releasing nRES:

```bash
./scripts/native_boot_inquiry.py /dev/cu.wchusbserial1220
```

The inquiry script transmits only `0x00`, `0x55`, and `0x20`. It stops unless
the expected `0x00` and `0xE6` responses are received, validates the inquiry
frame checksum, and compares three replies. It contains no erase or programming
command. A different initial rate can be selected explicitly after a fresh
reset, for example `--baud 9600`.

## Entry sequence

1. Close SW1 to hold MD1 low.
2. Hold SW2 to keep nRES low.
3. Start the selected WDT waveform.
4. Apply ECU power through J6.
5. Release SW2 so nRES returns to high impedance.
6. Perform the non-destructive SCI1 inquiry.

Do not force nRES high. Do not send command `0x40` during the inquiry.

## Validation

The source schematic was checked with KiCad 10.0.1:

- ERC: 0 errors and 5 expected warnings.
- Two `same_local_global_label` warnings identify the deliberate local/global
  label boundary for `WDT_IN` and `nRES`.
- Three `isolated_pin_label` warnings identify intentionally unconnected J1
  positions 6, 7, and 8: `PB14_NC`, `UNUSED_NC`, and `TP84_5V`.
- Unconnected wire endpoints: 0.
- Wires crossing symbols: 0.

Electrical validation in KiCad does not validate voltage levels under load or
the WDT waveform accepted by the target supervisor. Those remain bench
measurements.
