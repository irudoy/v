# Stock misfire registration on 1ND, JK78C, JK00C and JK00D

The stock reporters select local indices 10 through 16. The exact 12-byte
descriptors encode P0306 through P0300 in that order. Descriptor byte 8 is
`0x40` in all seven records. The separate attribute halfword comes from the
pointer at `attribute_table + 4 * index`.

## Exact descriptors and attributes

| Stock ROM | Descriptor base | Attribute pointer base | P0300 / P0301 / P0302 / P0303 / P0304 / P0305 / P0306 attribute addresses | All seven attributes |
| --- | --- | --- | --- | --- |
| 1ND0A | `0001be00` | `0001cd84` | `00017a70 / 00017a64 / 00017a66 / 00017a68 / 00017a6a / 00017a6c / 00017a6e` | `00b0` |
| 1ND3B | `0001be00` | `0001cd84` | `00017a70 / 00017a64 / 00017a66 / 00017a68 / 00017a6a / 00017a6c / 00017a6e` | `00b0` |
| JK78C | `0001b7ac` | `0001c5ec` | `00017436 / 0001742a / 0001742c / 0001742e / 00017430 / 00017432 / 00017434` | `00b0` |
| JK00C | `0001c4e0` | `0001d2b4` | `000185c4 / 000185b8 / 000185ba / 000185bc / 000185be / 000185c0 / 000185c2` | `0030` |
| JK00D | `0001c500` | `0001d2d4` | `000185e4 / 000185d8 / 000185da / 000185dc / 000185de / 000185e0 / 000185e2` | `0030` |

| DTC and index | Exact bytes | 1ND0A | 1ND3B | JK78C | JK00C | JK00D |
| --- | --- | --- | --- | --- | --- | --- |
| P0300, 16 | `06070d000000030040000000` | `0001bec0` | `0001bec0` | `0001b86c` | `0001c5a0` | `0001c5c0` |
| P0301, 15 | `05000d000000030140000000` | `0001beb4` | `0001beb4` | `0001b860` | `0001c594` | `0001c5b4` |
| P0302, 14 | `05010d000000030240000000` | `0001bea8` | `0001bea8` | `0001b854` | `0001c588` | `0001c5a8` |
| P0303, 13 | `05020d000000030340000000` | `0001be9c` | `0001be9c` | `0001b848` | `0001c57c` | `0001c59c` |
| P0304, 12 | `05030d000000030440000000` | `0001be90` | `0001be90` | `0001b83c` | `0001c570` | `0001c590` |
| P0305, 11 | `05040d000000030540000000` | `0001be84` | `0001be84` | `0001b830` | `0001c564` | `0001c584` |
| P0306, 10 | `05050d000000030640000000` | `0001be78` | `0001be78` | `0001b824` | `0001c558` | `0001c578` |

The two 1ND stock ROMs contain identical bytes from `0001bdfc` to the end
of the images. This includes the report code, its literals, the scheduler
slot and the two tables. The seven attribute halfwords and the relevant
group-enable and lane-floor bytes also agree when read separately from each
stock ROM, within the earlier region where the images differ.

## Periodic decisions and cylinder selection

Both layouts test bit `0x80` of a group-enable byte with stock value `0xe0`.
The 1ND schedule word at `00022250` selects `000b6384`. Its indirect call at
`000b63be` reaches `000c1c2c` through `ROM32[000b6610]`. The JK78C diagnostic
task loads `ROM32[0009c4f4] = 000a48fc` at `0009c2ba` and calls it at
`0009c2bc`.

| Stage | 1ND0A and 1ND3B | JK78C |
| --- | --- | --- |
| Group enable and comparison | `ROM8[0001aee2] = e0`, `000c1c4a..000c1c4e` | `ROM8[0001a892] = e0`, `000a4918..000a491c` |
| Decision routine | `000c1c2c` | `000a48fc` |
| Selector entry and decision call sites | `000c41f8` from `000c3074`, `000c33f8`, `000c3658`, `000c3932`, `000c3ba6` | `000a6bf8` from `000a5afc`, `000a6168`, `000a63d8`, `000a65e6` |
| Example six-lane count base | `fffeacba` at `000c343a`, through `fffeacc4` | `ffff3a4a`, passed at `000a5f90` to `000a69cc` |
| Inclusive per-lane floor | `ROM8[000087a7] = 06`, read at `000c3438` | `ROM8[00008738] = 06`, read in the call delay slot at `000a5f92` |
| Result rebuild and two-lane aggregate test | Clears low seven bits at `000c3436`, sets lane masks at `000c3448..000c348e`, sets aggregate at `000c349a` | Clears the reviewed masks at `000a69d8` and `000a69dc`, sets lane masks at `000a69ec..000a6a30`, sets aggregate at `000a6a3c` |

For the reviewed window branch, each of six successive unsigned count words
corresponds to cylinder 1 through 6 in ascending address order. A word at
or above the floor sets its local cylinder bit. Two or more qualifying
lanes set the aggregate bit. Other admitted window and retention paths can
also set the aggregate bit.

The selectors first consider the local aggregate bit and the prior
aggregate runtime status. Either causes P0300 selection. If there is a prior
cylinder result under runtime record byte 2 mask `0x04` and none of the
prior cylinder results matches the current bitmap, they select P0300.
Otherwise, the first present local bit in cylinder order 6, 5, 4, 3, 2, 1
selects the cylinder-specific record. The argument splits into group
`argument >> 1` and selector parity `argument & 1` for retained snapshots.
The argument itself is independent of the cylinder number.

| DTC | 1ND local mask at `fffeb888` and transfer | JK78C local mask and index load |
| --- | --- | --- |
| P0300 | `0x01`, call `000c4412` | `ffff4566 & 0x40`, calls `000a6f10` and `000a6f20` |
| P0301 | `0x40`, tail jump `000c440c` | `ffff4565 & 0x10`, index load `000a6f04` |
| P0302 | `0x20`, tail jump `000c43fc` | `ffff4565 & 0x08`, index load `000a6efc` |
| P0303 | `0x10`, tail jump `000c43ec` | `ffff4565 & 0x04`, index load `000a6ef2` |
| P0304 | `0x08`, tail jump `000c43dc` | `ffff4565 & 0x02`, index load `000a6ee8` |
| P0305 | `0x04`, tail jump `000c43cc` | `ffff4565 & 0x01`, index load `000a6ede` |
| P0306 | `0x02`, tail jump `000c43bc` | `ffff4566 & 0x80`, index load `000a6ed0` |

The six JK78C cylinder branches join at `000a6f06`. The 1ND target resolves
via `ROM32[000c4450] = 000ba0b8`. The JK78C target resolves via
`ROM32[000a6f8c] = 0009dfa8`.

## Common registration

The 1ND dispatcher invokes the marker `000ce048` at `000ba126`. The marker
sets bit 7 of byte 1 at `fffed298 + 3 * index`, writes the activity byte
`fffebf4a` at `000ce0c6`, and reads the attribute pointer at `000ce0ca`.
The dispatcher calculates `12 * index`, checks descriptor byte 8 at
`000ba144..000ba148`, and takes the bit-6 path for every P030x record. The
store at `000ba166` sets low bits `0x03` of runtime record byte 2.

JK78C calculates the same descriptor stride and tests byte 8 at
`0009e036..0009e042`. Its bit-6 path calls `0009e5ae` at `0009e044` with the
original local index. This helper sets low bits `0x03` of byte 2 at
`ffff5e94 + 3 * index` through stores `0009e5d0` and `0009e5da`. The
dispatcher also uses the attribute pointer table at `0009e0e6` on its other
record path.

## JK00C and JK00D comparison

Both stock ROMs contain the selector at `000893f6` with identical selector
instructions across `[000895c8, 00089716)`. The local result byte is
`ffff43a2` on JK00C and `ffff43b6` on JK00D. The bit assignments are
`0x01` for the aggregate and `0x02` through `0x40` in cylinder order 6
through 1. Both use the shared cylinder call `000896f8` and aggregate calls
`00089702` and `00089712`. The target `ROM32[00089774] = 000808e0` is the DTC
dispatcher. Its descriptor base literal at `00080b2c` distinguishes the two
catalogs. The bit-6 class branch calls `00080c5a` at `00080922` in both
images. These sites establish registration correspondence for P030x.

## Open evidence

The physical cylinder attribution of the upstream crank events, the full
set of admission and reset paths, and vehicle monitor completion retain
separate evidence requirements. JK00C and JK00D window producers and
readiness conditions remain open.
