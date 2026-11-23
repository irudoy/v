# JK08A rest-position byte judgement at native index 1

`JK08A.rest-position-judgement-paths.toml` binds 273 stock instructions in 1 actual entry path and 3 spans,
26 literal pools, 7 four-byte RAM pointer aliases and 34 calibration spans.
Published identities and counts are checked against the executed descriptor.
The complete `90256` natural entry has no callees or stock-function stubs.

The exact incoming full R4 word is `1`. The native `16BB` owner explicitly
names this bank index. The other nineteen complete CPU-context fields are
independent raw inputs, including the complete zero/nonzero R5 enable word.
This boundary grants no other-bank, natural-caller or scheduling admission.

A zero incoming R5 or `2327 !=128` selects the complete reset path. The enabled
path retains two independent reset permits. The first requires clear `43C3`
and both `24AB` bits `0x40/0x10`. The second requires clear `43C2`, all `24AA`
bits `0x40/0x10/0x08` and `2458.bit5`. A failed permit reloads its actual
counter at `42F7` or `430B` and clears only mask `2` in aggregate byte `3599`.
Counter reloads use the complete raw bytes at `855D` and `871F`.

A nonzero counter reloads the corresponding two timers. A zero counter sets
mask `2` in `3599` and reads `16BA+1` at actual site `9030C` or `903AA`.
The first window uses upper bound `128+ROM8[8951]` and lower bound
`128-ROM8[8952]`; the second uses `8736/8737`. Bounds use signed integer
comparisons after unsigned byte promotion. Equality is inside the window.
An outside value ORs mask `2` into actual fault bytes `358B` and `3582` only
when each corresponding timer is zero. The four timers have independent
gates. An inside value reloads both window timers from `8E25/8E1C`.
This invocation does not decrement those timers or counters.

The reset path clears only mask `2` in `3599`, reloads both counters and all
four timers, and preserves the fault bytes. The complete initial values of
all bitfields retain their unrelated bits. Sign-extended byte loads and the
full 32-bit live OR/AND and timer-store registers remain distinct from the
low bytes eventually written.

Both window paths retain the local mask byte at root `SP-8`. GBR is saved,
set from its literal pool to the `FFFF42D3` window, used by indexed accesses
and restored in the natural RTS delay slot.

The raw input source declares all 256 values of each of sixteen RAM bytes
and eight ROM controls in separate bounded partitions, full other-context
boundaries and I/M/Q/T controls, both threshold equalities and all four timer
gates. Counter and timer ROM variations enter their actual read paths.
These sets do not constitute a full Cartesian product. No expected comparison
or output value is supplied by the driver.

Held-other alternatives change only the raw selected `16BB` byte. Both actual
fault publications at `358B` and `3582` must change while the complete other
RAM, CPU context, frame, ABI, calibration and code/pool bounds remain fixed.
Matching scalar flags, changed input echoes or a changed write set without
changed computed bytes do not establish this obligation.
