# Natural APC reset offset

`JK08A.apc-reset-offset.toml` declares the complete stock function `0004C1E4`
and its natural byte-lookup and division helpers. The GNU fixture preserves
instruction words, delay slots and returns. Only listed RAM pointer literals
relocate to simulator storage.

`FFFF4184` bit `0x40` selects which configuration byte scales the later
product. The selected source is clamped by the bytes at `0000851F` and stored
at `FFFF144C`. That byte is the coordinate of `0001208E`, `prophetic-jacamar`,
read through `00026370`. The companion curve `00012096` uses the byte stored
at `FFFF1450`. Each curve has eight bytes. A coordinate at or above 224
returns the last byte.

The signed call at `0004C34E` enters `00021BBC` and divides by the constant `00014000`. `0004C350`
completes the dividend from MACL. That dividend is the first lookup
multiplied by the configuration scale and then by the second lookup. The
quotient is saturated to 255 and combined with the earlier byte at
`FFFF23BC`.

Independent equations cover both gates, the post-delay operands and the byte
reads. Neither divisor in this entry is zero, so the callee fault store at
`FFFF9818` stays unchanged. The proof does not publish a native relation,
admit scale, establish scheduling, or qualify hardware.
