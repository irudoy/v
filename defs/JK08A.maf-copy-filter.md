# Natural JK08A MAF copy and filter accesses

`JK08A.maf-copy-filter.toml` binds two complete natural entries to the
existing `stock_jk08a_maf_filter.s` fixture. The existing conventional
harness and its scenarios remain part of the common GNU gate. The raw
source reuses `stock_ignition_consumer_invoke.s` and the established
80-byte input and 572-byte observation ABI. Those sizes describe byte
layouts, not scenario counts or a separate acceptance requirement.

The independent consumer binds actual stock reconstruction, private
sources, aliases, fixture/ELF/object identities, simulator command and
terminal streams. It compares the complete context, GPR/SR/frame/ABI,
all relocated RAM bytes and the coefficient byte against independent
instruction and numeric equations. A PASS marker alone grants no claim.

## Exact natural sites

The low byte of incoming R4 selects the bank. The declared domain contains
banks 0 and 1, with separate upper-byte argument controls. Natural entry
`0003A982` reads the unsigned word at `FFFF1054 + 2 * bank` at
`0003A98E`. Its RTS delay slot at `0003A9A8` writes that word to
`FFFF1058 + 2 * bank`. At bank 1 these are `FFFF1056` and `FFFF105A`.
The signed clamps follow an unsigned word extension; their typed natural
entry outcomes are retained separately from arbitrary interior entry.

Natural entry `0003A9AA` reads its working word at `0003A9BE`. Mode byte
`FFFF2461` selects an unweighted copy or a weighted update. At bank 1,
the source is `FFFF105A` and destination is `FFFF1DF2`. The weighted
path reads the previous destination word and coefficient byte `0000870A`.
Its word store at `0003AA08` is the real BRA delay slot. The unweighted
path stores at `0003AA0A` without reading the previous word.

For unsigned input `x`, previous value `p` and byte coefficient `c`, the
weighted result is `floor((c*x + (256-c)*p)/256)`. When that result equals
`p` but differs from `x`, one unsigned word step moves toward `x`.
The declared inputs retain stock coefficient 26 and a controlled zero
coefficient for both anti-stall outcomes, word boundaries, both banks,
mode alternatives and positive input/output changes with every other
input fixed. Full sibling and neighbor bytes remain observed.

## Native publication

`JK08A.maf-access-claims.toml` pins the four complete original claims
within the joint 33-access MAF batch. Both `dancing-hippo` relations
share one original document and one proposed document. The spiked-dalmatian
document contains both its filter writer and the contribution reader
described in `JK08A.maf-extended.md`. The existing normal `link` writer
appends every reserved proof item as one exact joint batch, together with
the two exact curve-reader attribution unlinks. The four copy/filter
relations retain their type, ledger, semantic property, symbol width/signedness, original evidence
position or TEST origin. Complete native publication comparison and exact
COPY/injection/coherent/SID22 scope equality remain required gates.
The transition adds no physical scope normalization or separate receipt.

The qualified evidence supports only its owning word-transfer identity.
It supplies no reverse function level, engineering units, scale, natural
caller scheduling or hardware qualification. Source preparation and a
structural association with an older region do not qualify a pending claim.
