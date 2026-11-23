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
