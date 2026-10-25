# Natural sexy-tamarin

`JK08A.sexy-tamarin.toml` declares the complete stock function `000C0D90`
and its natural byte-lookup and division helpers. The GNU fixture preserves
instruction words, delay slots and returns. Only listed RAM pointer literals
relocate to simulator storage.

R4 is an index. The byte at `FFFF1240` plus that index, reduced by 128, is one
factor. `00026474` reads an eight-byte curve on the axis at `0001302E`.
Index zero selects `0001252A`, `sturdy-worm`. Any other index selects
`00012532`, `foamy-cuckoo`. `000C0DF6` enters `00021BBC`. `000C0DF8` completes
the product of that lookup and the biased byte, shifted left by eight, in R1.
R0 is the constant 100.

The same index then selects the second curve on the axis at `00011BEB`.
Index zero reads `000123F2`, `strange-salmon`. Any other index reads
`000123FA`, `greedy-chamois`. `000C0F28` enters `00021BBC`. `000C0F2A`
completes the product of that lookup and the difference of the two biased
bytes in R1. R0 is again the constant 100.

Independent equations cover both indexes, the post-delay operands and the byte
reads. Changing only the selected curve changes its dividend. The other curve
of the pair is not read. These divisors are never zero, so the callee fault
store at `FFFF9818` stays unchanged. The proof does not publish a native
relation, admit scale, establish scheduling, or qualify hardware.
