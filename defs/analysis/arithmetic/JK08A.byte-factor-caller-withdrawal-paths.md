# JK08A byte factor caller withdrawal

Source bindings: `JK08A.byte-factor-caller-withdrawal-paths.toml`.


## Complete raw arithmetic and real calls

The caller occupies4BA48..4BA62 and4BA64..4BB6A around its literal hole.
The complete helpers are26370..26382,26A60..26ABA and26740..2676E.
The implicit-byte entry26A80 lies inside the complete normal26A60 parent.
The16 preceding instructions and seven word-cell sibling instructions are
excluded by the exact byte-mode literal224 after SHLR8.

RAM2478 bit2 selects an in-place override. The complete unsigned1657 byte
subtracts twice the raw byte atROM886D. The signed-word intermediate clamps
negative results to0 and publishes1657. The complete1657 input preimage and
arithmetic remain bound. This same-location read/write is not an outside-input
causal alternative. Raw overrides preserve the prior1658/1659 bytes and use
the natural common store4BB5E.

The other paths read15FC as an unsigned word and15FE as a sign-extended word.
The nonnegative difference ranges through98303. Neither an unsigned second
word nor an ideal narrowed difference replaces that exact promotion. RAM2458
bit32 selects the percentage path. The complete difference multiplies raw
ROM886B, keeps the low32 product, multiplies100 and keeps low32 again. The
logical shift14 result caps at255 before the real byte store4BABE in the BRA
delay slot. The other two publication bytes remain unchanged.

The curve path clips unsigned1024>>7 to255, then calls the real26370 helper
at4BADE with data126A8 in its delay-slot R4. It publishes the raw lookup byte
to1659. The complete unsigned11BC word subtracts32 with a lower0 and upper255
clamp, then calls the same real helper at4BB0C with independent data126A0.
The second raw byte publishes1658. Each table contains eight independent raw
bytes. Coordinates below224 interpolate adjacent bytes at a32-unit step.
Coordinates at or above224 retain the actual signed MOV.B endpoint return
before each caller's byte publication and explicit unsigned promotion.

The two unsigned lookup bytes multiply into a complete16-bit factor. The
difference multiplies100 into low32. The caller separately multiplies the
low16 part and high16 part of that scaled difference by the factor, keeping
their low32 products. It takes the upper16 bits of the low product, caps the
high product at65535, adds those two contributions and shifts logically by5.
The result caps at255 and publishes1657 at4BB5E. A widened ideal product does
not replace the actual distinct partial products or their high-term cap.

All paths return R0=0x3CB. The natural RTS at4BB66 includes the R13 restore
in its delay slot. R13, R14, MACL, PR and SP are restored; GBR and MACH retain
their incoming values.
