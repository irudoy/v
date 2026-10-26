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


The conditional calibration geometry is `uint8` with `4` values.

COPY, injection-copy and coherent-copy hashes omit only the complete
registered original or replacement representation of this one claim.
Changed roles, properties, sources, layouts, evidence and unrelated facts
retain their namespace effect. The representation rule grants no positive
dependency proof; that requires the independently validated original
sequence. The transition preserves all existing physical proof namespaces
and publishes no additional receipt. It grants identity only, without
units, scale, universal absence of ROM reads or hardware qualification.
