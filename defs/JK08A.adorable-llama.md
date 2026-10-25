# JK08A bounded paired normalization

The explicit `000413CC` window starts at `0004161C` with a uint8 coordinate q
in R5 and R10 pointing to the simulator view of `FFFF1FF4`. Its first span
ends at `000416A0`; the publication tail is `000416F0..000416F8`. Embedded
literals remain data between the spans. Complete parent reachability and the
earlier formation of q are outside the admitted scope.

Four natural `00026388` calls read A(q), B(q), A(128) and B(128) from the
sixteen-byte curves `00012798` and `000127D8`. Coordinates below 240 use
uniform spacing 16 and adjacent bytes; higher coordinates select the last
byte. The actual post-delay table/coordinate arguments and physical read
order are required observations.

If A(q) <= B(q), the output is zero. Otherwise the intermediate starts as
`(A(q) - B(q)) * 256`. When A(128) > B(128), call `0004168A` divides this
positive intermediate by `A(128) - B(128)`, which delay slot `0004168C`
finishes in R0. A nonpositive anchor difference bypasses division. The
intermediate is bounded to 255 and stored as a byte at `FFFF2236` in
`000416F6`. The mode bit read from `FFFF2459` remains observable in R14;
its later consumption is outside the window.

Independent changes only to B must alter B(q), B(128), the actual dividend,
the actual divisor and the final output with A, input context and all RAM
held fixed. Separate controlled curves exercise the nonpositive first
difference, equal and reversed anchor differences, unit divisor, saturated
and unsaturated outputs, interpolation directions and endpoint behavior.

The exact arithmetic-argument proposal replaces only the original attributed
physical reader on `00021BBC` and its ledger selector. It retains the other
readers, editor metadata, raw identity scale and all unrelated native facts.
It supplies no physical units or scale admission.

Stock instructions write SP+24. The existing `stock_normalization_invoke.s`
observer also preserves continuation at SP+28, which the separately assembled
`000416F8..00041700` return uses. Both continuation copies and the overwritten
SP+24 stock temporary are part of the complete frame comparison. The fixture
aliases only the RAM pointer at `000416B4`; the later pointer loaded from
`0004192C` stays stock and is not dereferenced. Later brake/mode processing,
scheduling and hardware behavior remain unadmitted.
