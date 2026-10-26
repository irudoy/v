# Packed-field transfer boundary

`packed-field-transfers.toml` binds retained width questions to exact stock
transfer sites. It distinguishes a declared byte field, the physical width of
an instruction, and the width of a diagnostic or telemetry publication.
Neither a word nor a longword copy establishes a wider semantic field.

Each transfer names the exact source/destination bytes, load/store sites and
data register.

The fuel-mask windows include the literal load of R10, the actual JSR and its
length-setting delay slot, the natural copy helper and the subsequent wider
field access. Their explicit bounded entry supplies R1/R2/R7. A post-call R10
assumption cannot establish that callee's behavior.
