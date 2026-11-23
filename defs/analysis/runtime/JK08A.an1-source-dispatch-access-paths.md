# Natural AN1 source dispatcher

Source bindings: `JK08A.an1-source-dispatch-access-paths.toml`.

Natural entry `0003d832` makes 22 ordered direct
calls and returns through its stock RTS and delay slot. The body owning the
interpolation core is `00026a60`; the selected byte wrapper enters its existing
interior at `00026a88`.

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
The physical input terminal and scheduler cadence require separate evidence.

The selected lookup calls are `0003d32e` and `0003d4c0`, reached
from the two respective parent entries for both lane indices. They pass the
exact table pointer and `uint8(uint16(source)>>2)` after their real call delay
slots. The 32-byte wrapper caps coordinates 248..255 at byte 31. Other inputs
interpolate adjacent bytes with `fraction=(coordinate%8)*8192`.

The bounded signed division receives only numerator 0..38160 and divisor 150.
It uses the short magnitude path, including zero dividend, with no zero-divisor,
wide-divisor, long quotient or sign-correction path. The byte lookup enters
`00026a88` with byte mode; the earlier core shifts and word-mode branch are
outside this natural root.
