# JK08A register-operand division callees

`defs/analysis/arithmetic/JK08A.division-callees.toml` bounds the exact signed `00021BBC` and
unsigned `00021CE0` instructions, natural returns, literal pools and the
declared simulator alias of `FFFF9818`.

Both entry ABIs receive the divisor in R0 and dividend in R1. The signed
equation truncates toward zero and keeps the resulting register word modulo
32 bits, including the minimum signed value divided by minus one. A zero
divisor returns zero and writes the word `0000044E` to `FFFF9818`. Every other
RAM byte remains part of the independent full-state obligation.

The typed inputs cover explicit sign, divisor-size, quotient-size, arithmetic
boundary and initial Q/M/T/SR classes. The raw driver must retain complete
registers, special state, ABI, entry/exit frame, RAM and original terminal.
Separate quotient and fault-store equations do not replace instruction-state
equivalence or independent stock reconstruction.

Signed division initialization follows section7.2.16 of the
[SH-2E software manual](https://www.renesas.com/en/document/mah/sh-2e-software-manual),
REJ09B0316-0200. The independent state model derives Q/M/T from operand sign
bits while preserving the other SR bits.

Direct callee observations establish no caller argument lineage, ROM or RAM
datum identity, physical datum reader, units, scale, native relation replacement
or hardware qualification. Each retained caller attribution requires its own
positive argument path and exact claim admission. `automatic_resolution`,
`caller_argument_inference` and `datum_identity_inference` remain false.
