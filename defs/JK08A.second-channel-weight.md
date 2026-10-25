# Second-channel weight publication and live consumption

`JK08A.second-channel-weight-paths.toml` binds 524 stock instructions in 1 actual entry path and 9 spans,
42 literal pools, 8 four-byte RAM pointer aliases and 49 calibration spans.
The complete 7A804 entry has 196 instructions. Its 8 stock entry paths include
the real 266E8/265F0 wrappers, 26B84 axis search, 26AF8 interpolation,
26B28 surface kernel, 26D10 fraction divider and 21CE0 unsigned divider.
The 80-byte context, 572-byte observer and 192-byte frame preserve
20 independent context fields. All 65536 RAM bytes remain observable.
There are 2 raw ROM controls containing 3 bytes.

## Exact retained fact

The retained original claim is
`f9e43aae9a95c058dcbb91b05308323e4b6e28177c2d7bb74b2a63840c26dc13`:
the 35F4 quantity has a reader association with the complete 7A804 function.
The native writer, unit `Q15 fraction`, unset semantic width and signedness,
other links, ledger, evidence and TEST positions remain exact. The owning
operation appends one identity proof to this reader. The complete function
document remains unchanged. It grants no scale, units, geometry, scheduling
or hardware admission.

## Complete source and physical boundary

RAM249F.bit1 selects the ordinary 18CF6/18D16 endpoint pair or the alternate
19090/190B0 pair. The common curve starts at 18D36. Each curve uses the
16-word unsigned axis at 18F76 and reads a seventeenth physical endpoint word.
The ordinary curves occupy one 49-word physical span; the alternate curves
occupy one 33-word physical span. Shared neighboring words have one input
preimage. The last common and alternate guard words are physically read with
zero arithmetic weight at their last knots.

ROM83C1.bit7 selects the raw ROM16[1630C] substitute or the 8x8 uint16 surface
at 16F48. The surface has 64 physical words. The contiguous inner/outer axes
at 18A86/18A96 occupy 16 physical words. The inner coordinate is the unsigned
RAM2C71 byte shifted left by eight; the outer coordinate is RAM10BC.
The backward word search chooses the rightmost qualifying knot without
assuming monotonic or distinct axes. An actual interpolation bracket supplies
a positive divisor to the complete 26D10 body.

7A878 writes the low word at SP+2 in the real four-byte local. 26606 reads the
full 32-bit argument before its unsigned-word extension. The high word comes
from the incoming frame. The root allocates 40 stack bytes, preserves R8-R14,
PR and MACL, and restores R8 in the natural 7A994 RTS delay slot at 7A996.
GBR and MACH remain preserved. The real divider determines the M/Q/T effects.

## Weight and output calculation

7A88C stores the full returned or sign-extended R5 low word at 35F4.
7A88E extends that same R5 to unsigned16. Its complement and both wrapped32
products continue through 7A890/7A892/7A898. The unsigned/signed overflow
guard chooses a wrapped sum or zero. The shifted result is capped to 65535
and stored at 35CA. The common curve is published at 35FC.

RAM245E.bit6 selects an additional common-curve product. Its shifted result
can exceed 65535 and remains full32 in R14. The actual first 21CE0 call divides
FFFFFFFF by RAM31E2; a zero divisor executes the error store at 9818 and
returns zero. The quotient guard and the later unsigned product bound the
scaled value to 800. RAM2698 can replace that value, RAM3024 caps it, and
RAM4214.bit6 can select RAM35EA. The actual R5 output is stored at 35CC.
The final real division uses multiplier 727 and divisor 800; R2 is stored
at 1248. MUL.L changes MACL and retains the R6 used to construct divisor 800.

There is no physical read of prior35F4. The retained reader describes the
published quantity continuing in R5. Independent prior35F4 alternatives must
preserve the complete final RAM, CPU and frame on both weight paths.

## Required executable and independent consumers

Every one of 64 surface words and the raw substitute word require held-other
alternatives that change actual35F4, 35CA, 35CC and1248 publications. Input
echoes and altered write sets do not establish the quantity association.
The input matrix retains complete raw word domains, unsigned/sign-extension
boundaries, duplicate and nonmonotonic knots, all surface fraction paths,
wrapped products, wide R14, zero division, mode bits and output boundaries.

The existing observer and GNU lifecycle transport complete original inputs
and outputs. Separate numerical and instruction-state consumers require
ordered physical operands, full pre/post-extension R5, complete local carrier,
real nested calls, return paths, delay slots, ABI and exact source identities.
The complete word-interpolation caller and division originals remain mandatory
from the identical primary execution. Source files and local commits supply
no successful executable acceptance or native publication.
