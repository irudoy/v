# JK08A bounded closed-loop input conversion

The complete stock entry at `0003edb4` calls the natural coordinate conditioner
at `0003ef74` and nine real lookup or division helpers. One mandatory Region
binds 823 instructions, 2233 bound bytes and 4338 literal cases. The contract
describes independent software inputs and both conversion channels. Hardware
readiness is NO. Source producers, physical units, permission cadence and the
joint feedback cycle require separate evidence and hardware observation.

## Coordinate conditioning

Let `b` be the channel in 0..1. Bit 3 of `ROM8[00008978]` selects the unsigned
word at `ffff2882+2*b` when set. When clear, the source is
`uint16(2*RAM16[ffff267c+2*b])`; the word wrap precedes every signed operation.
Let this selected source be `X`, and let `H = ROM16[00008f98]`.
The first difference is `D = sat_s16(X-H)`.

The real byte-curve wrapper at `000264a0` reads the coefficient table at
`00012292` over the byte axis at `00011b47`, using the high byte of the unsigned
word at `ffff4524`. With positive coefficient `C`, the real signed division
helper at `00021bbc` computes `trunc0(128*D/C)` and the second signed16 clamp
produces `Q`. The zero-coefficient branch performs no division and forms the
signed boundary from the sign of `D`.

Admission requires `ROM16[000095c6] < RAM16[ffff110a] < 65280`,
`RAM16[ffff4524] > ROM16[00009384]` or
`RAM16[ffff4524] < ROM16[00009386]`, and `C > 0`.
Admission publishes `uint16(max(0,H+Q))` as the coordinate. Bypass retains `X`.
The coefficient is copied to `ffff2f8e`; the two coordinates are copied to
`ffff322c` and `ffff322e` by the natural caller.

The stock midpoint is 880. With admitted raw source 65534 and coefficient 136,
the first clamp produces 32767, signed division produces 30839 and the
published coordinate is 31719. Omitting the first clamp yields 33647.
The literal matrix executes this witness without asserting engine reachability.

## Exact lookup and output arithmetic

The real axis searches scan downward, choose the last axis point no greater
than the input, and clamp below the first and at or above the last point.
Exact points and clamped endpoints have fraction zero. An interior fraction is
`floor(65536*(X-axis[i])/(axis[i+1]-axis[i]))`.
For an ascending segment the real linear helper returns
`left+floor((right-left)*fraction/65536)`; for a descending segment it returns
`left-floor((left-right)*fraction/65536)`.
This integer rounding applies to both byte and word curves.

The word wrapper at `000264f8` looks up the common conversion curve at
`000148fa` over its 16-word axis at `00015d20` using each published coordinate.
`lookup(0x000148fa,Z)` in a chain equation denotes this exact bounded lookup.
The paired word surfaces at `0000c10e` and `0000c18e` use the shared eight-word
axes at `00013d54` and `00013d94`. The complete `00026270` wrapper interpolates
the column before the row with the same directional integer rounding.
Zero fractions avoid the corresponding neighboring surface reads.

For each channel let `Y` be the conversion-curve result, `A` the unsigned
surface result, and `O = int16(RAM16[ffff45a0+2*b])`.
Bit `b` of the independent byte at `ffff2b4d` selects
`P = int16(ROM16[00008ea4])` or zero. The caller publishes `P` to
`ffff2b54+2*b`, then writes
`min(65535,max(0,Y+A+O+P-32768))` to `ffff29e2+2*b`.
The surface results are retained as unsigned words at `ffff8544+14-2*b`.
Their positive output influence and the signed-state influence refer to these
declared software values. The stock optional offset is zero.

## Execution boundary and observations

The simulator relocates nine declared 32-bit RAM pools and two exact 16-bit
RAM pointers: `0003ef10=8544` names a 28-byte workspace and `0003f002=8560`
names a 20-byte workspace. Both aliases preserve the addressed bytes and use
the original instruction bytes. All call targets are real stock functions.
The division fault and wide-divisor arms have byte identity only because they
are unreachable within the declared caller domains and the bound stock axes.

The observer checks R0..R14, full SR including M/Q/T, MACH, MACL, GBR, natural
PR/SP, the outer ABI, every byte of the 64 KiB RAM image, both workspace aliases
and neighbors, all bound code and data bytes, and the complete 160-byte nested
frame. The complete entry, branch outcomes, delay slots and real call/return
paths execute. Independent stock and synthetic calibration contexts exercise
all mode bytes, all permit bytes, every coefficient byte, signed clamps,
admission neighbors, all 64 surface cells, ascending and descending curves,
word-wrap inputs and output saturation boundaries. The matrix contains 4022
admitted calls and 46 zero-coefficient calls; it does not exhaust every joint
input combination or establish physical reachability or scheduler cadence.
