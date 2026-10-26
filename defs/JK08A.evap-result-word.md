# JK08A bounded EVAP result-word writer

`JK08A.evap-result-word-paths.toml` binds 672 stock instructions in 11 actual entry paths and 13 spans,
44 literal pools, 6 four-byte RAM pointer aliases and 55 calibration spans.
The published identities and counts are checked against the executed descriptor.

The complete `B2096` entry retains every real interpolation, quotient and
remainder helper. The native caller `B29B8` supplies `R6=FFFF301C` at
`B2C88` with delay slot `B2C8A`. The bounded input maps only this initial
pointer to `0100301C` in the existing RAM mapping. Complete low16 R4/R5
domains retain arbitrary upper bits; the other complete CPU/SR inputs,
original observer frame and full RAM remain independently bound.
The full caller source and native document are retained as context.

The writer selects its baseline and both byte coefficients through the
actual ROM/state gates, transforms `2C92` through `152D6`, and compares the
result with low16 R5. A nonpositive difference produces zero. A positive
difference with a zero low16 R4 produces65535. Otherwise the normalized
word is `min(65535,floor(baseline*ROM8813*difference/(32*low16R4)))`.
The independent equation retains the full mathematical product. Physical
checks bind the stock48-bit split, early product bound, high quotient,
remainder, low dividend/quotient, caller-local stack words and saturation.
The actual result is
`min(65535,floor(normalized*coefficientA*coefficientB/16384))`.
`B22A6` writes its word through the live R12 pointer.

The actual `26388` tail enters `26A84`. Indexed byte and word curves retain
their unconditional neighbor reads, including guard cells at zero fraction.
The remainder call follows the high-quotient bound of31 and uses the short
division path. All helper instruction bytes remain bound, with complete
`timing_denominator`, `bfs_path` and `exhaust_cvtc` obligations required from
the identical primary.
