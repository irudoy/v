# Natural AN1 source dispatcher

`defs/JK08A.an1-source-dispatch-access-paths.toml` binds 22 complete function
bodies and 63 literal pools. Natural entry `0003d832` makes 22 ordered direct
calls and returns through its stock RTS and delay slot. The body owning the
interpolation core is `00026a60`; the selected byte wrapper enters its existing
interior at `00026a88`. Every instruction remains at its original ROM address.

The dispatcher processes two raw AN1 lanes. `0003d258` alternates their phase
bits and initializes or updates the unsigned-word filter with
`floor((3*previous+sample)/4)`. A rising sample whose rounded result equals the
previous word advances the filter by one. `0003d2dc` uses a configuration-selected
constant 75 or looks up the filtered source in the byte curve at `00012dea`.
`0003d344` converts the resulting code to a capped percentage-like byte through
the actual signed helper `00021bbc`, with positive divisor 150 and numerator
`240*(code-10)` on the admitted middle branch.

The complete sequence also updates raw transfer bytes, freshness bits,
conditional running minima, the history and absolute-difference byte, timer
gates, a saturating byte counter and its latches. The publication paths preserve
their actual order. `0003d4a8` looks up each unfiltered source through the same
curve, subtracts 10 with a floor at zero and writes `ffff3f42/ffff3f43`. The
dispatcher copies lane zero to `ffff3f41` in the delay slot at `0003d8c6`.
The physical input terminal and scheduler cadence are outside this proof.

The existing `cautious-iguana/tbl` reader association with this dispatcher is a
nested natural-reader association. It is retained with one identity-only
owning append. The selected lookup calls are `0003d32e` and `0003d4c0`, reached
from the two respective parent entries for both lane indices. They pass the
exact table pointer and `uint8(uint16(source)>>2)` after their real call delay
slots. The 32-byte wrapper caps coordinates 248..255 at byte 31. Other inputs
interpolate adjacent bytes with `fraction=(coordinate%8)*8192`. Every physical
table byte and every fixed-other changed-cell alternative reaches an actual
changed PID publication in the required original.

The descriptor's physical 32-byte interval follows these actual operands. It
adds no declared native element width, table geometry, unit or scale. The full
native owner, all layouts, other readers, ledger fields and selectors, scale
facts and evidence remain exact. The complete native dispatcher remains exact.
The original claim digest is
`0e2c8b6427f1e91ecf78415869bfaaf68236306e76800f375bf7d81863706087`.

Independent equations compose every ordinary-RAM store of the entire sequence
with its physical site, width, register and bytes. The existing independent
SH-2E instruction oracle binds complete CPU/SR/frame state to actual GNU
observations. Fixed per-site physical operand declarations separately require
all load/store address carriers, original data bytes, complete ordered accesses
and resulting RAM/frame bytes. Real caller entries, post-delay arguments,
natural tail jumps and complete callee returns remain mandatory.

The bounded signed division receives only numerator 0..38160 and divisor 150.
It uses the short magnitude path, including zero dividend, with no zero-divisor,
wide-divisor, long quotient or sign-correction path. The byte lookup enters
`00026a88` with byte mode; the earlier core shifts and word-mode branch are
outside this natural root. These caller premises explain the exact excluded
instruction sites. The complete existing helper bodies remain reconstructed.

The transport uses the existing ordinary 80-byte context, 572-byte observation,
both 192-byte frame images, complete 64 KiB ordinary RAM and the existing
native `ffff8400..ffff84ff` observation premise. Native `ffff84c3` must match its
ordinary mirror before and after every invocation. Only declared full pointer
pools relocate into ordinary simulator RAM. Native word literals, code, pools,
natural returns and real helper bodies remain bound. No stock-function stub,
synthetic return, instruction substitution, observer or runner is introduced.

The producer emits raw observations and carries no expected output. The
independent consumer requires the complete actual original, current sources,
physical reconstruction, CPU/frame/RAM, every feasible instruction and branch,
both selected-call paths and changed actual publication for each source byte
with all other complete inputs fixed. Source preparation establishes no
accepted execution, native publication, scale, scheduler or hardware fact.


## Complete owning source boundary

The owner has four exact supported phases: the original, the single positive
append, the complete scalar withdrawals, and their joint postimage. The finite
compatibility bridge recognizes only this complete table owner and this exact
identity append. Every other native fact, link, ledger selector and TEST
position remains mandatory. The positive consumer retains its own complete
primary; a withdrawn owner additionally requires the scalar family's complete
independent admission from that identical primary. Neither result replaces
the other family's obligations.

The existing registry contains 42 families and 88 captures. The ordinary adapter
registry contains 41 descriptors and 82 generated outputs. This native-window
component uses its existing manual raw driver; its registration adds no ordinary
adapter output. Complete native owner and retained-function refusals cover all
four phases. A complete result preserves every explicit false boundary for
native identity, geometry, scale, units, natural caller reachability, scheduling
and hardware admission. Source preparation grants no successful execution or
native publication.
