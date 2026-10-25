# Conditional CVTC byte-result publication

`JK08A.cvtc-gain-output.toml` contains one exact original relation:
`FFFF143A`, owned by `curious-perch/ram`, has a declared reader to
`00026474` (`brilliant-ibis/fn`). The replacement is an owning
`arithmetic-output` dependency through caller `000C1DEC`.

The existing natural bank2 component calls the real byte wrapper at
`000C1ED4`, with delay slot `000C1ED6`. The wrapper searches axis
`00012850`, interpolates curve `0001205A` through its real helpers and
returns R0 to `000C1ED8`. The caller extends that byte into R6 and
publishes it at `000C1EE2` to `FFFF143A`. The full instruction-state trace,
independent curve equation, exact physical byte store and actual observed
RAM byte must agree. The inactive mode has neither the return phase nor
the publication.

The distinct `exact_cvtc_gain_output` consumer flag requires changed actual
`143A` output for both coordinate-only and controlled-curve-only input
alternatives. Every other RAM byte, calibration, CPU register, SR, frame,
SP, continuation and external ABI remains fixed. The curve comparison
excludes only its exact nine controlled bytes from the calibration and bound
preimages. A retained input, unchanged output or changed caller context
cannot satisfy this condition.

The calculation registry contains 38 dispositions. Its original 37 identity
records retain their exact complete values and order. The existing
`reconcile-calculation-dependency` batch performs this replacement under the
same complete original primary, native fence, writer and shared receipt.
The CVTC11 physical access obligations remain mandatory. Fixture, matrix,
observer, producer, transport and generated driver remain unchanged.

The full original/proposed native documents retain all eight link positions,
both L0 evidence items, unset semantic width/signedness and all unrelated
facts. Only the exact old reader becomes the result dependency; only its
matching legacy consumer selector retires. Every other ledger selector,
field, note, identity index and source order remains fixed. Original TEST
contexts and COPY/injection/coherent/SID22 scopes remain exact.

The proof grants conditional output identity without helper physical RAM
reader inference, universal absence of reads, geometry, units, scale,
scheduler, sensor or hardware admission. Native publication and the common
B acceptance require the complete original execution and independent refusal
boundary.
