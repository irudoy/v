# Diagnostic-record stored-fault clear

The complete natural `0008C348` entry clears bit7 of the second byte selected
by `u32(FFFF5718+3*R4+1)`. The full raw R4 value participates in the SH-2E
address arithmetic. The `R4=FFFFFFFF` sentinel returns `FFFFFFFF` without a RAM
operand; the native pointer literal is still loaded. The active path loads the
signed byte at `0008C35A`, applies `AND7F` to R0 and stores the resulting byte in
the real RTS delay slot at `0008C360`. Its actual returned R0 is the unsigned
low-seven-bit value. The sentinel uses its separate RTS and NOP delay slot.

`defs/JK08A.diagnostic-record-highbit-clear-paths.toml` binds the complete
15-instruction body and its single literal at `0008C45C`. One simulator-only
pointer relocation maps native `FFFF5718` into ordinary RAM `01005718`.
Every instruction remains exact. No stub, outside-code return, additional
observer, memory profile or runner is introduced.

The explicit observations include ordinary record indices, the sentinel and
full-width modular inputs. Raw `AAAAAAAB` selects native `FFFF571A`; raw
`55555555` selects native `FFFF5718`. These inputs preserve the actual 32-bit
arithmetic and distinguish it from a silent low16 truncation. The observed
input set supplies no API index limit, array-extent declaration, semantic
meaning for an arbitrary alias or natural caller reachability. The separate
unresolved RAM358B and RAM358C reader associations retain their original facts.

The selected original is the writer association from `hallowed-malkoha/ram`
to `tough-avocet/fn`, SHA256
`0e678170c81620a6a4cdf9506fc54f5b3c460ff14a59b9a157a01b6b8164205b`.
The existing `diagnostic-record-bit4-access` family requires one additional
identity-only owning attachment for this exact indexed write. Its complete
array owner and function, all other links, both ledger ends, semantic types,
native units, TEST origins and positions remain fixed. Physical byte evidence
adds no native geometry, scale, units, scheduler or hardware qualification.

Independent equations retain every register, complete SR, GBR, MACH, MACL,
natural SP/PR, both 192-byte frame images and the complete 64 KiB ordinary RAM.
They expose the signed load carrier, full triple/index/address carriers, exact
ordered physical operands and actual post-delay return. The separate instruction oracle must agree with the equations at every
instruction. Actual GNU observations must match the complete exit CPU/SR,
frame and RAM results. Both conditional outcomes and both RTS delay slots are
mandatory in the same complete primary original.

Every physical selected-byte preimage occurs for each active explicit raw R4.
The independent consumer checks the actual computed RAM byte and actual
returned R0. Fixed-other alternatives require different source bytes to change
both actual results while preserving every other complete input. Input echo,
a supplied scalar or a changed write-set alone supplies no admission. Index
alternatives also require changed actual common-byte values with all other
inputs fixed. Every sentinel observation preserves the entire RAM and has no
RAM read or write.

The standard `ordinary-80-572` adapter transports only declared inputs and raw
observations. Its reviewed declaration owns generated C transport and
structural refusals. Exact code/pool reconstruction, physical and numerical
checks, full native/TEST preservation and current same-primary source bindings
remain separate obligations. Source preparation establishes no accepted
execution, native publication or hardware eligibility.


## Registered shared source boundary

The diagnostic-record-bit4-access family contains four exact positive
originals: three writers and one indexed reader, with five complete unchanged
function snapshots and one joint owner postimage. All four original captures
belong to the same complete primary. The existing registry contains 42 families
and 87 captures. The standard ordinary adapter registry contains 40 descriptors
and 80 generated outputs. The high-bit clear adapter supplies two source outputs;
the 78 preceding generated outputs retain their exact bytes. The older paired
array originals keep their separate source obligations and receive no credit.
