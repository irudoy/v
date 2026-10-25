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

The input-only C driver uses the existing80-byte context,572-byte ordinary
observer and192-byte frame. Each phase retains a separate complete CPU context.
All65536 RAM bytes, calibration bytes and bound code/pool bytes pass from the
producer to the consumer unchanged by the driver. Equal complete raw
calibration inputs share storage; every phase observes the complete input.
The existing separate-storage gate remains mandatory.

Independent integer equations, exact instruction-state reconstruction,
ordered physical reads/writes and full post-delay call/tail/return checks
consume the original raw stream. Every active coefficient word requires an
alternative with all other complete inputs fixed and changed actual producer
correction and both ratio bytes. The guard word has a distinct physical-read
obligation. Generic signed and unsigned division obligations remain required
through `timing_denominator` from the same complete primary.

`JK08A.torque-correction-ratio-claims.toml` describes one exact owning identity
append for the retained `14C1A -> 64A1C` relation. The full owner and both
function documents, all other links, ledger entries, TEST evidence, layouts
and reverse properties remain fixed. The native width and signedness remain
unset. The catalog `x*0.1 Nm` conversion retains its candidate status.
The execution boundary establishes the exact table-derived quantity
association; physical scaling, scheduling and hardware validation retain
their separate evidence requirements.
