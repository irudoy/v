# Exact bank2 CVTC state and duty accesses

`JK08A.exhaust-cvtc-accesses.toml` binds natural functions `000C1DEC` and
`000C2040` to the owned JK08A image. The bank index is the low byte of R4
and equals one. Upper R4 bits, registers, GBR, MACH, MACL, SR, frame,
external ABI and complete 64 KiB RAM are explicit inputs. Battery byte
`FFFF1108` is nonzero. These premises grant no scheduler or sensor reachability.

The independent assembly retains every tested stock instruction and address.
Only declared RAM pointer pools relocate to simulator RAM. Arithmetic literal
`FFFF0000` at `000C203C` retains its value. Both roots use their natural
stack prologues and RTS delay slots, with no observing return patch or stub.

The real helper closure contains byte wrapper `00026474`, axis search
`00026944`, fractional division `00026C78`, interpolation `00026740`,
unsigned quotient `00021CE0` and unsigned remainder `00021F40`. Each helper
instruction executes. The wrapper reads both selected curve bytes even at
the upper clamp, so the source binds nine curve bytes at `0001205A` and
eight strictly increasing axis bytes at `00012850`. Controlled curves retain
ascending, descending, constant and endpoint cases. Saved decompiler output
and function membership supply structural inputs, without access admission.

## Independent domain obligations

The scalar consumer models ordered mode transitions, including a mode-2
clear followed by a possible reenable. Nonzero modes retain their actual
code behavior without receiving additional physical meaning. The configured
product path splits the low32 word product into high and low parts, retains
actual quotient/remainder calls with divisor 625, combines their results and
caps the longword. The alternate path retains low32 wrap, signed-positive
selection, byte gain and the `0x04000000` cap.

The duty consumer independently calculates both battery divisions, rounded
fraction, preliminary cap, conditional current-to-lag copy, mode selection,
unsigned lag-product decrement, zero floor and final 1024 cap. It compares
complete resulting RAM, including untouched neighbors. Ordered byte/word/long
operands, selected axis/curve bytes, arguments after actual delay slots,
helper/root continuations, stack phases and terminal comparisons remain
separate obligations of the domain consumer.

Both outcomes of every declared feasible branch are required across complete
inputs. Exact bank2 and nonzero/word-divisor premises exclude separate
zero/wide-divisor paths. The final state-path upper clamp retains its exact
fallthrough consequence after the earlier cap. No universal behavior outside
these premises is admitted.

## Exact native publication

`JK08A.exhaust-cvtc-access-claims.toml` pins eleven complete original
relations and their grouped owning evidence appends:

| Native address | Root | Direction | Exact physical sites |
|---|---|---|---|
| FFFF1AA8 | 000C1DEC | writer | 000C1FF4 |
| FFFF1AA8 | 000C2040 | reader | 000C205E |
| FFFF1AAE | 000C1DEC | reader | 000C1E78 |
| FFFF1AAE | 000C2040 | writer | 000C213E |
| FFFF1AB6 | 000C2040 | reader | 000C2114 |
| FFFF1AB6 | 000C2040 | writer | 000C20DA |
| FFFF1B1A | 000C1DEC | reader | 000C1F0C |
| FFFF1B1D | 000C1DEC | reader | 000C1E06,000C1EBC |
| FFFF1B1D | 000C1DEC | writer | 000C1E32,000C1E66,000C1E92,000C1EB4 |
| FFFF1B1D | 000C2040 | reader | 000C20E4 |
| FFFF1C72 | 000C2040 | writer | 000C20AE |

Every reader requires a changed actual dependent output when only its exact
incoming physical datum changes. Every writer requires a changed actual
publication when one explicit causal operand changes. All other RAM,
calibration, CPU, SR, frame, SP, continuation and external ABI remain fixed.
A retained input or an expected scalar result without actual raw output
cannot satisfy this condition.

The ordinary `exhaust-cvtc-access` family routes
`exhaust_cvtc_transition_paths` through the existing complete COPY primary,
80/572 observer, standard input-only adapter and shared receipt. Independent
domain consumers remain mandatory. One authoritative registration supplies
capture order, source closure, read/rank/level guards and normal grouped
`link` publication without a family-specific common dispatcher.

Every other native fact, layout, declared type, symbol evidence, ledger and
TEST origin retains its complete value and position. Unset width and
signedness remain unset. The three retained TEST selectors cover placement
slices; the owning raw proof grants no TEST execution or broader semantics.
Exact unique owning appends preserve COPY/injection/coherent/SID22 scopes.
Scale, units, reverse identity, geometry, scheduler, sensor and hardware
admission are excluded. Evidence requires the complete successful original
primary and common B acceptance.

The same component supplies the separate conditional result disposition
`JK08A.cvtc-gain-output.toml`. Its distinct actual143A return/store and
fixed-other coordinate/curve guard is mandatory in addition to every
CVTC access obligation. The existing fixture, matrix, observer, producer,
transport and generated driver retain their exact source bytes.
