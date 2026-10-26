# JK08A torque correction and ratio consumers

`JK08A.torque-correction-ratio-paths.toml` binds 690 stock instructions in 9 actual entry paths and 10 spans,
46 literal pools, 12 four-byte RAM pointer aliases and 54 calibration spans.
The published identities and counts are checked against the executed descriptor.
The full normal listing of `26A60` is retained as source context. The actual
`263FE` tail enters `26A64`; its preceding four bytes are outside this caller's
instruction boundary.

The complete `658A4` producer interpolates the eight active words of `14C1A`
against the eight-word `14ABA` axis. `264CC` reads both neighboring coefficient
words even when the fraction is zero, including the ninth physical guard word.
The live result is retained after its `14E4` scratch copy. The producer selects
the direct `1071` byte or its weighted combination with `2772`, multiplies the
coefficient by the signed difference from `ROM8E51`, clamps a negative product
to zero, divides by256 and stores the correction at `14E2`.

The complete `64A1C` consumer obtains its lag weight from `14E52`, preserves
signed target and previous-state arithmetic, and applies the stuck-progress
increment. It initializes ten history words when required, reads the selected
delay before shifting, caps the delay at ten and publishes `19A0`. The selected
divisor and optional signed factor retain actual truncation and low-word wrap.
Both `64BD4` and `64C44` read the carried correction. The two ratio-byte paths
retain their independent sentinels, signed divisions, zero-divisor behavior
and lower/upper clamps before publishing `186C` and `1864`.


Independent integer equations, exact instruction-state reconstruction,
ordered physical reads/writes and full post-delay call/tail/return checks
consume the original raw stream. Every active coefficient word requires an
alternative with all other complete inputs fixed and changed actual producer
correction and both ratio bytes. The guard word has a distinct physical-read
obligation. Generic signed and unsigned division obligations remain required
through `timing_denominator` from the same complete primary.
