# Natural fine-gopher entry

`JK08A.fine-gopher.toml` declares the complete stock function `0006062C`
and its natural eight-word lookup and unsigned-division helpers. The GNU
fixture preserves instruction words, delay slots and returns. Only listed
RAM pointer literals relocate to simulator storage.

`0006062C` keeps its GBR at sign-extended `00008C54`, which is `FFFF8C54`,
and a later block at sign-extended `000099FC`, which is `FFFF99FC`. Those
windows are separate from the relocated 64 KiB image. The proof compares
each window to the instruction equation and does not treat the relocated
image as the destination of those stores.

`00014F42` is `rare-groundhog` and `00014F52` is `ochre-tuna`. Both use the
axis at `00013C58` and the unsigned word at `FFFF11F4`. `00015002` is
`steady-beetle`. It uses the axis at `00013BD8` and the byte at `FFFF1076`.
Each curve has eight semantic words. The wrapper `000264CC` also reads the
following physical word. For `00014F42` and `00015002` that word is the
first word of the next curve.

The two RAM words at `FFFF1026` and `FFFF22E6` are multiplied and divided by
the constant `00020202`. Each scaled product is then multiplied by one curve
and divided by the constant `000003FC`. `00060712` and `000607B8` complete
those dividends from MACL. `00015002` is read only when the long selected at
`00060898` is zero. Its lookup multiplied by 255 is the dividend. `000608C4`
places the unsigned word at `000093E8` in R0. A zero word skips `00021CE0`
and does not inherit the callee fault store at `FFFF9818`.

Independent equations cover the lookups, the post-delay unsigned arguments,
the zero-word bypass and the clamps. The proof does not publish a native
relation, admit scale, establish scheduling, or qualify hardware.
