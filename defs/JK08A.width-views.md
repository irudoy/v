# JK08A diagnostic byte views and wider working-state accesses

Source bindings: `JK08A.width-views.toml`.

## Diagnostic views

DID `1116` reads one byte at `FFFF118A`; DID `112A` reads one byte at `FFFF16D2`;
DID `1129` reads one byte at `FFFF4544`.

Wider working-state operations have separate bounded observations. The
`118A` producer resumes after the preceding helper with an independently
staged word at `SP+8`. It stores the unscaled word at `FFFF1FC8` and the low
word of the six-bit left shift at `FFFF118A`. Its diagnostic high byte loses
information from that working state. The admitted stack word does not prove
which values the preceding helper produces.

The `16D2` windows read the full unsigned word. One multiplies it by 118 and
adds `00018000`; two shift the unsigned word right by two before multiplying
by 118. Equal diagnostic high bytes can therefore coexist with different
working-state results. The `4544` windows contain word stores and loads; the
publication window explicitly selects the high byte for `FFFF9BBA`.
The working-state access width, response width and declared semantic field
width remain distinct facts.

## Indexed base

The indexed word instructions normalize to base `FFFF2142`. The store window
uses its explicit incoming `R14`, doubles it and addresses
`FFFF2142 + 2 * R14_entry`. The read window loads and zero-extends the primary
selector byte or its alternate byte, then forms the corresponding word
address.

A zero selector addresses the base; a nonzero selector addresses a later word. This observation neither
proves nor refutes zero at every natural caller. The store resumes after the
preceding lookup call, so its explicit `R14` premise does not establish
callee preservation. The byte counter at the normalized base and the
conditional word-vector access require separate semantic ownership.
