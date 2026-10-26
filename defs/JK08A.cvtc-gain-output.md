# Conditional CVTC byte-result publication

Source bindings: `JK08A.cvtc-gain-output.toml`.

The existing natural bank2 component calls the real byte wrapper at
`000C1ED4`, with delay slot `000C1ED6`. The wrapper searches axis
`00012850`, interpolates curve `0001205A` through its real helpers and
returns R0 to `000C1ED8`. The caller extends that byte into R6 and
publishes it at `000C1EE2` to `FFFF143A`. The inactive mode has neither the return phase nor
the publication.
