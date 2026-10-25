# Conditional cached-publication snapshot dependency

`JK08A.snapshot-ROM-dependency.toml` binds the complete original
`0001202E` calibration claim to a conditional dependency of the byte at
`FFFF106A`. The live publication byte is `FFFF1072`. Their owners and
addresses are distinct and remain fixed.

The natural producer `0003E1DA` computes the calibration lookup and stores
its byte at `FFFF1EE0` and `FFFF257A` while `FFFF2459.bit5` is clear.
That mode forces the live byte to zero. An explicit sequence sets only
that mode bit and invokes the producer again. With `FFFF2451.bit7` clear,
the retained cached value selects zero or the filtered high byte for the
live publication. The second invocation retains the cache and does not
reload the calibration.

The bounded stock scheduler window `00020F1C..00020F3A` then calls the
natural `00022558` copier. It copies the eight live bytes
`FFFF1072..FFFF1079` into `FFFF106A..FFFF1071`. The observing return after
the window is separately assembled and lies outside its stock instruction
spans. The rest of the scheduler, natural scheduling and hardware effects
remain outside this conditional dependency.

The independent consumer requires the complete original publication
capture from the existing COPY primary. It validates exact instruction and
literal reconstruction, fixture transformations, private inputs, observer,
executable, full machine state, calibration and native-control snapshots,
process terminal and current source closure. The positive joint proof
requires complete RAM continuity through all three invocations, permits
only the specified mode-bit change, and requires distinct cached and
snapshot values when the calibration changes under equal original RAM.

The conditional calibration geometry is `uint8` with `4` values. Its
count is bound to the executed producer descriptor. A normal
`reconcile-snapshot-output` operation replaces the exact physical reader
with `depends` and role `snapshot-output`, retires only the matching
legacy ledger selector, and adds only absent matching per-layout geometry.
Every original TEST context, other fact and evidence position remains fixed.

COPY, injection-copy and coherent-copy hashes omit only the complete
registered original or replacement representation of this one claim.
Changed roles, properties, sources, layouts, evidence and unrelated facts
retain their namespace effect. The representation rule grants no positive
dependency proof; that requires the independently validated original
sequence. The transition preserves all existing physical proof namespaces
and publishes no additional receipt. It grants identity only, without
units, scale, universal absence of ROM reads or hardware qualification.
