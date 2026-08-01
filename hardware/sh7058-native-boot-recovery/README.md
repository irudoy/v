# SH7058S native boot recovery harness

This KiCad project documents the bench wiring used to enter the native boot
loader of the SH7058S ECUs represented by JK00D and JK08A.

The schematic is a logical harness diagram. ECU PCB testpoint locations remain
unknown until they are verified by continuity to the MCU pins on the actual
board. Do not probe the MCU pins directly and do not copy physical testpoint
numbers from a legacy type A board.

## Project files

- `sh7058-native-boot-recovery.kicad_pro` - KiCad project.
- `sh7058-native-boot-recovery.kicad_sch` - source schematic.
- `sh7058-native-boot-recovery.kicad_pcb` - empty board placeholder created by
  KiCad; no recovery PCB is defined.
- `sh7058-native-boot-recovery.pdf` - printable schematic.
- `sh7058-native-boot-recovery.svg` - vector preview.
- `sh7058-native-boot-recovery.png` - raster preview.

## ECU recovery connector J1

| Pin | Signal | MCU reference | Harness connection |
| --- | --- | --- | --- |
| 1 | `SCI1_TX` | PC0 / TxD1, pin 165 | USB-UART RXD through R2 |
| 2 | `SCI1_RX` | PC1 / RxD1, pin 166 | USB-UART TXD through R1 |
| 3 | `MD1` | pin 55 | R3 and SW1 to GND |
| 4 | `WDT_IN` | supervisor path through the board resistor to PL5, pin 221 | R5 from the selected WDT source |
| 5 | `nRES` | pin 58 | R4 and momentary SW2 to GND |
| 6 | `GND` | board ground | common bench ground |

R1 through R4 are provisional service resistors and require board verification.
R1 and R2 are 22 ohm in the drawing; R3 and R4 are specified as <=22 ohm. R5
is the 10 ohm reference value from the archived recovery circuit.

## Interfaces

The USB-UART adapter uses 19200 8N1 and must have a 5 V compatible TX level.
Only TXD, RXD, and GND are connected. Adapter VCC remains disconnected. This is
TTL-level SCI, not RS-232.

The WDT source is selected by fitting exactly one jumper:

- JP1 selects Arduino D9 / OC1A at 250 Hz, 50% duty cycle, and 5 V.
- JP2 selects an STM32 timer output at 240-250 Hz and 50% duty cycle through a
  74AHCT1G125 powered from the regulated 5 V input on J5.

J6 represents the verified ECU bench harness for BATT, IGN, and GND. It is the
only ECU power entry shown. J5 powers only the 5 V logic buffer. J7 provides
oscilloscope access to `WDT_IN`, `nRES`, and GND.

The baseline circuit does not include a second SCI interlock. It can be added
only if a specific ECU or ROM is shown to require it.

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

- ERC: 0 errors. Two `same_local_global_label` warnings are expected because
  `WDT_IN` and `nRES` use local labels at J1 and global labels only at the
  remote monitoring endpoints.
- Off-grid connection geometry: 0 items.
- Orphaned wires: 0 items.

Electrical validation in KiCad does not validate the unknown ECU testpoint
locations, voltage levels on a specific PCB revision, or the WDT waveform
accepted by the target supervisor. Those remain bench measurements.
