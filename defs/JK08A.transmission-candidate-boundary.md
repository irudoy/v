# Transmission candidate and signed request boundary

The completion entry is `000777FA` and the boundary entry is `00079030`.

The completion reads the signed candidate at FFFF4162 when ROM8[000083C1].bit0
is clear and FFFF41A6.bit3 is set. Raw ROM8[000089C5].bit0 selects either that
candidate or FFFF34A0 as the upper word FFFF3480. The lower word FFFF3484 is
min(signed FFFF34C8, signed FFFF4162). In that path FFFF349C supplies both
FFFF347E and FFFF3482. Separate bypass paths preserve the full preselected
signed-word and mode behavior. All 4 actual completion publications and
their full-width live signed source registers remain mandatory.

The boundary consumes the actual FFFF3480 and FFFF3484 words with its other
independent signed candidates. It retains every lower/upper clamp, the
duplicated FFFF2438/FFFF19C2 selection, ROM8[00008B38] modes, the shared
ROM8[000083C1] mode, and all actual flag/word publications. The actual final
word is FFFF19C6. Both source-load sites, both carried-word consumer sites,
and both final publication sites remain exact.

Each input case invokes the complete completion and boundary entries.
The C driver captures the complete 65536-byte RAM after completion and
before the boundary without reseeding between the calls. The consumer
requires exact equality of that RAM, every calibration span and all bound
code/pool bytes. Both independent phase contexts, frames, SP/PR, saved full
register words, natural RTS-delay restores, SR and preserved special
registers remain bound. No semantic stub or inserted return replaces stock
instructions.

Separate wide signed equations compute all RAM publications and their
ordered physical operands. Held-other alternatives require changed actual
carried words and changed actual FFFF19C6 when only the initial FFFF4162
word changes. Both phase contexts, complete initial RAM outside that word,
all ROM modes and every other physical input stay fixed. A supplied
intermediate scalar or matching output bytes do not establish the path.
The complete existing request-boundary publication original remains
mandatory from the same primary.

The separate 0000942C scalar association requires its own complete producer
and transitive scope. This package does not admit or remove that original.
