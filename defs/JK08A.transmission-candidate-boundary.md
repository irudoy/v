# Transmission candidate and signed request boundary

The source binds 294 stock instructions in 2 actual entry paths and 3 spans,
38 literal pools, 9 four-byte RAM pointer aliases and 41 calibration spans.
The complete 000777FA completion has 64 instructions; the complete 00079030
boundary has 230 instructions. Both use the existing 80-byte context,
572-byte observer and 192-byte frame. Each phase has 20 independent context
fields. All published counts read the executed descriptor.

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

Original 9377739e0c6019c86f49d44e3ec1a8af161348c35772dcacacad54b6eea2416a
retains its reader type, structural identity claim, roles and evidence.
Its physical FFFF4162 loads belong to 000777FA. The reader relation to
00079030 states the conditional quantity association through FFFF3480 and
FFFF3484. One exact owning proof append preserves all other native links,
input/lookup dependencies, summaries, units, symbols, ledger/evidence/TEST
positions and both complete native functions. Semantic width and signedness
remain unset. The package grants no geometry, scaling, units, scheduling,
whole-ECU or hardware admission.

The separate 0000942C scalar association requires its own complete producer
and transitive scope. This package does not admit or remove that original.
