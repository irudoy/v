# Cruise Control Switch

## Purpose

The Cruise Control Switch of the editor definitions sets the cruise control
configuration byte of an image. The ECM decodes the steering switch buttons
from one analog input only while bit 0 of that byte is set, and the Map
Switching gestures and, on JK00A, JK03A, JK03B, and JK08A, the Rolling Launch
CANCEL hold read the decoded button code. Stock JK08A holds `0x2B`, the configuration of a vehicle with Intelligent
Cruise Control (ICC). JK00A, JK03A, JK03B, JK00C, JK00D, 1ND0A, 1ND3B, and 1EK7A hold
`0x00`: their decoder stores no button code, so the selector stays on Map 1
and, on JK00A, JK03A, and JK03B, Rolling Launch never arms. On these images the switch selects the JK08A
configuration for a vehicle fitted with the five-button ICC steering switch.

The switch is a definition-controlled data edit of one byte in the calibration
partition. The ROM builder preserves it as configuration outside its declared
ranges.

## States

| State | Byte | Decoder |
| --- | ---: | --- |
| Not Installed | `0x00` | returns before the decode and stores no code |
| ICC Switch (5 Buttons) | `0x2B` | decodes the ICC ladder into the JK08A button codes |

`0x2B` is the whole JK08A byte: bit 0 enables the decoder, bit 1 selects the
ICC ladder, and the other bits carry their JK08A values.

Each definition lists the stock state of its image first, so the TunerPro
patch keeps the stock byte as its base data: on JK08A the patch applies Not
Installed, and on the other images it applies ICC Switch (5 Buttons).

## Sites

| Image | Layout | Byte | Stock | Stock state |
| --- | --- | ---: | ---: | --- |
| JK08A | `7mfk` | `0x8B28` | `0x2B` | ICC Switch (5 Buttons) |
| JK00A | `7mfk` | `0x8B28` | `0x00` | Not Installed |
| JK03A | `7mfk` | `0x8B28` | `0x00` | Not Installed |
| JK03B | `7mfk` | `0x8B28` | `0x00` | Not Installed |
| JK00C | `jk00c` | `0x8B59` | `0x00` | Not Installed |
| JK00D | `jk00d` | `0x8B5A` | `0x00` | Not Installed |
| 1ND0A | `1nd` | `0x8A11` | `0x00` | Not Installed |
| 1ND3B | `1nd` | `0x8A11` | `0x00` | Not Installed |
| 1EK7A | `1ek7a` | `0x8AD9` | `0x00` | Not Installed |

JK78C and 1ME3B carry no switch: their stock configuration bytes, `0x49` at
`0x894F` and `0x3B` at `0x8A62`, set bit 0, and their decoders decode the
buttons.

## Decoder

| Layout | Decoder | Input word | Code | Accepted code |
| --- | ---: | ---: | ---: | ---: |
| `7mfk` | `0x000D185C` | `0xFFFF3630` | `0xFFFF36D9` | `0xFFFF36D8` |
| `jk00c` | `0x000DD6F4` | `0xFFFF3728` | `0xFFFF37E5` | `0xFFFF37E4` |
| `jk00d` | `0x000DDE30` | `0xFFFF373C` | `0xFFFF37F9` | `0xFFFF37F8` |
| `1nd` | `0x0012B270` | `0xFFFEAAC0` | `0xFFFEAB76` | `0xFFFEAB74` |
| `jk78c` | `0x000FE2B8` | `0xFFFF3854` | `0xFFFF3909` | `0xFFFF3908` |
| `1me3b` | `0x001386A4` | `0xFFFEAC00` | `0xFFFEACBC` | `0xFFFEACBA` |
| `1ek7a` | `0x00159F20` | `0xFFFEAF30` | `0xFFFEAFEE` | `0xFFFEAFEC` |

The decoder compares the input word with a ladder of windows and stores the
one-hot code of the window that holds it; a level outside every window gives
`0x80`. It accepts a code once two consecutive passes give it. The first pass
after reset, while a flag bit of the decoder is still clear, takes its own code
as the code of the previous pass and accepts it.

On JK08A the function `0x000D0F44` shifts the accepted code into a five-sample
window, the scheduler copies the window, and the ASCD task `FUN_000CF020` takes
the stable code `button_state/ram` once the five samples are equal. Map
Switching and Rolling Launch read the stable code, and the CAN serializer
places the accepted code in byte 3 of frame `0x239`
(`../defs/JK08A.can.md`).

The 1EK7A ASCD task `0x00155FC8` compares five samples at `0xFFFE97B5`
through `0xFFFE97B9` and writes the stable code at `0xFFFE9C25`. The Map
Switching selector reads that byte. Configuration `0x2B` enables the decoder
and selects bit 0 of the stable code as the MAIN source at `0x00157900`.
The task stores MAIN in bit 7 at `0xFFFEBD15`.

With bit 0 of the configuration byte clear, the decoder skips the decode.
The `1nd` and `1ek7a` decoders then read a second gate, at `0x8A23` and
`0x8AEC` respectively. Both stock gates have bit 0 clear, so the decoders
return. Setting this bit continues at `0x0012B424` on `1nd` and at
`0x0015A0D4` on `1ek7a`.

With bit 1 set, the decoder takes an ICC ladder. The 8MFK, `1nd`, `1me3b`, and `1ek7a`
decoders hold two ICC ladders and select the second one with bit 0 of a
selector byte: `0x8B64` on JK00C, `0x8B65` on JK00D, `0x8A1D` on 1ND,
`0x8A6E` on 1ME3B, and `0x8AE6` on 1EK7A. Every image with the switch holds
`0x00` there and takes the first ICC ladder, which equals the JK08A ladder at
`0x24C08`. The first and second 1EK7A ladders are at `0x26BD0` and
`0x26BEC`. 1ME3B holds `0x0F` and takes the second ladder.

The ICC windows, in input-word counts, and their codes:

| Button | Window | Code | Switch resistance |
| --- | --- | ---: | ---: |
| MAIN | 0..108 | `0x01` | 0 Ohm |
| CANCEL | 224..317 | `0x02` | 309 Ohm |
| DISTANCE | 416..489 | `0x04` | 741 Ohm |
| SET/COAST | 578..636 | `0x08` | 1406 Ohm |
| RESUME/ACCELERATE | 720..764 | `0x10` | 2586 Ohm |
| all released | 850..883 | `0x20` | 5456 Ohm |
| open input | 940..65535 | `0x40` | open |

The resistances are those of the ICC steering switch between its terminals 13
and 16 in the factory manual (2007 G35 Sedan, CCS-47). Each lies in its window
under the count `1023 * R / (R + 1000 Ohm)`, the reading of a 10-bit converter
across the switch with a 1 kOhm pull-up; the pull-up is inferred from this
agreement and is not traced on the board.

`tests/test_cruise_control_switch.py` executes each decoder of the table on
the stock images in the SH-2 interpreter of `tools/mapkit/sh2_interpreter.py`,
from cells that read zero until set. With the byte of Not Installed the decoder
stores nothing outside its stack frame. With the byte of ICC Switch (5
Buttons) both bounds of every window give its code, and the counts next to
them give `0x80`. Over consecutive passes the first pass accepts its code, and
a level that changes is accepted only on the pass that repeats it. The JK78C
and 1ME3B decoders decode with their stock bytes and store nothing with bit 0
cleared, and count 400, between the CANCEL and DISTANCE windows of the first
ICC ladder, gives CANCEL on the second ladder.

## ICC configuration without an ICC unit

In the ICC configuration the ECM sends the button code to the ICC unit: the
factory manual has the ECM transmit the ICC steering switch signal over CAN
(2007 G35 Sedan, CCS-26), and JK08A places the accepted code in frame `0x239`.
The switch changes only the configuration byte. JK08A configures transmit
mailbox `0x239` and receive mailboxes `0x2B0` and `0x1A5` in its mailbox table
at `0x975A`. The images with the switch configure none of them: the `7mfk`
records at `0x975A`, `0x975E`, and `0x979A` hold type 5, inactive, and the
mailbox tables of JK00C at `0x9822`, JK00D at `0x9832`, `1nd` at `0x975C`,
and 1EK7A at `0x9944` carry no record with these identifiers. Cruise control on these images
therefore needs an ICC unit and the ICC CAN mailboxes, which the switch does
not configure, while Map Switching and Rolling Launch read the button code
inside the ECM and need neither.

Byte `0x28` of the DTC group enable table holds `0x7F` on JK08A and `0x00` on
every image with the switch; the table is at `0x186C8` on `7mfk`, `0x1B638` on
JK00C, `0x1B658` on JK00D, `0x1AEDC` on `1nd`, and `0x1B9E0` on 1EK7A.
The P1564 steering switch monitor `0x000913D0` of `7mfk` and its 8MFK
homologs `0x0009608C` and
`0x00096078` read that byte once bit 0 of the configuration byte is set, and
the `1nd` function `0x000D1CBC` reads it once bit 0 of `ROM8[0x8A11]` is set.
On 1EK7A the equivalent monitor is `0x000E6828` and reads `ROM8[0x8AD9]`.
The switch leaves the group byte unchanged.

## Hardware status

No image with a changed configuration byte has a hardware result. Hardware
evidence covers the stock JK08A configuration: the vehicle capture
`map_switching.ascd_main_vehicle_2026_09_21` in `hardware-results.toml`
records its MAIN codes. An image with ICC Switch (5 Buttons) needs these checks
before it is driven:

1. Before flashing, the retrofitted switch shows the resistances of the
   window table between terminals 13 and 16 while each button is pressed and
   5456 Ohm with all buttons released.
2. After flashing, with the ignition on and the engine stopped, the steering
   switch items of the CONSULT-III Plus ECM data monitor follow the MAIN,
   CANCEL, SET/COAST, and RESUME/ACCELERATE buttons, and a DTC read shows no
   new code.
3. With the cruise MAIN state off, the Map Switching gestures select a map and,
   on JK00A, JK03A, and JK03B, the Rolling Launch CANCEL hold arms as on JK08A.
