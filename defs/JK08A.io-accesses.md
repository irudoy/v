# Bounded JK08A I/O accesses

`JK08A.io-accesses.toml` binds independently assembled SH-2E instruction
windows to exact stock bytes. `JK08A.io-access-claims.toml` binds three
existing register claims to their complete original and proposed native
documents. Qualified admission requires the original complete shared GNU
execution, independently consumed full state, exact native transitions,
unchanged TEST origins and unchanged physical proof namespaces.

## Storage and observations

The simulator exposes flat storage at `FFFFD900` for 1024 bytes,
`FFFFF400` for 256 bytes and `FFFFF700` for 256 bytes. The harness observes
all 1536 native bytes before and after every invocation, separately from
all 65536 bytes of relocated RAM at `01000000`. Initial native bytes are
copied from their declared RAM shadows. Subsequent native writes do not
update those shadows. The consumer compares both snapshots independently.
The ELF storage gate excludes the four declared memory domains from
harness allocation; the state oracle also refuses a frame overlapping them.

Each observation includes the immutable 80-byte input context, actual exit
registers, full SR, stack pointer, continuation, caller ABI, 192-byte frame,
both memory domains and all 512 declared descriptor bytes. Numeric
equations complement the instruction-state oracle. Neither component
grants its own semantic admission.

## Captured word

The natural prologue at `00002040` saves R14 and PR and allocates 12 bytes.
`0000204E` reads four bytes at `FFFFF430`. The window retains the original
uint32 value in R0, takes its unsigned low word into R6, stores that word
in the local frame, and forms R2 as
`((incoming_R4 & 0xFFFF) << 16) | (native_word & 0xFFFF)`.
An independently assembled return at `0000205A` releases the frame and
restores the saved PR and R14 before returning to the observer.

The window ends before the call at `0000205A` to `000015CC`. It establishes
the positive physical read and bounded operand formation. It establishes
neither that helper's behavior nor the complete enclosing function.

The native transition removes only the exact original `reader/indexed_by`
relation from `ingenious-kagu/reg` to `capture_interval_update/fn` at
`0002B768`. It preserves the existing L0 evidence at `0000204E` as the
first evidence item and appends the qualified I/O item to that same
register symbol. It introduces no ledger, canonical function at
`00002040`, function name or architecture review. The transition makes
no universal claim about reads by `0002B768`.

## Monitor descriptor and word

The bounded prefix at `000A6DC8` establishes GBR `00023AC4`, computes
`selector * 56`, loads the selected pointer and takes the nonzero-pointer
branch with its real delay slot. An observing return at `000A6DE8`
releases its eight-byte local frame.

The following bounded entry at `000A6E9E` takes R4 and GBR from the actual
prefix exit. It reloads the selected pointer, reads the 16-bit native word
at `000A6EA4`, reads the descriptor's 16-bit mask and leaves the actual
T bit from `TST`. Its observing return begins at `000A6EB0`. Complete RAM,
native banks and descriptor bytes remain continuous between the entries.
The intervening parent control flow is an explicit premise.

Selectors 0 and 6 address `FFFFF754`, with masks `0x0800` and `0x0004`.
The matrix requires both masked and unmasked word outcomes for each
selector. `precise-kagu/reg` retains its existing reader relation to
`festive-gopher/fn`, its ledger and its complete diagnostic binding.
Entry 6 remains configured-disabled by stock byte `00018700 = 00`;
bounded invocation grants no natural caller reachability or P0447 behavior.

## Mailbox fields

The bounded entry at `000C2FE4` uses an explicit R11 slot, R7 mask
`1 << (slot + 1)` and prior R9. It reads the selected four-byte record at
`0000975A + slot * 4`. Types 1 and 2 select format 2; types 3 and 4 select
format 0; other values select format 7. Types 2 and 4 also OR R7 into R9.
The exact native base is `FFFFD920 + slot * 32`.

The identifier word is `(((record[2] << 8) | record[3]) >> 1) & 0x7FF0`;
the control word is `(format << 8) | record[1]`. Six 16-bit stores start
at `000C3058` and write offsets 0, 2, 4, 6, 16 and 18. The observing
return at `000C307A` precedes the parent readback and nested peripheral
operations. For slot 25, the native base is `FFFFDC40`, owned by
`solemn-heron/reg`; the stock record is `05 00 00 00` and selects inactive
format 7. The existing writer relation to `granite-chameleon/fn` and its
ledger remain intact, with one qualified owning evidence append.

## Publication boundary

`reconcile-io-access` accepts all three unique exact original claim
identities in one metadata publication batch. Preparation requires each
complete unchanged native document and exact retained unresolved review.
Publication permits only the two owning link-evidence appends and the
specified captured-word relation removal and symbol-evidence append.
Original evidence order, TEST attachments, diagnostic bindings, names,
geometry, units and other native facts remain fixed. Ordinary `link`
operations cannot attach these reserved proof items.

Owning I/O evidence supports identity only. It grants no reverse function
level, scale, physical units, peripheral side effects, natural scheduling
or hardware qualification. Qualified software evidence remains subject to
the repository's hardware validation requirements.
