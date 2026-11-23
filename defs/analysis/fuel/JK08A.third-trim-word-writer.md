# Complete third-trim word writer

The described natural entry is `0005B534`.

All 256 raw channel values of the complete incoming R4 remain observed.
The function selects its low8 and uses channel+1 as the actual mask.
The exact retained writer identity binds bank1 channel0 at FFFF2A24.
Behavior of other raw channels does not assign additional semantic owners
or geometry. Inputs include 256 raw prior words and 256 raw32 accumulators.

The individual mode tests actual masks in FFFF328A, FFFF328B and FFFF328E.
ROM8[00008B2A].bit2 selects the shared mode with its actual combined
bit0/bit1 admission predicates. FFFF28E4 and FFFF28B4 select the real
correction direction. The indexed word at FFFF2A24+2*channel is read
unsigned by MOV.W/EXTU.W. ROM8[00008998] and ROM8[00008997] increments
are multiplied by 16; ROM8[000086F6] and ROM8[000086F7] retain their
other actual paths. Subtraction reaches zero at its real boundaries.
Raw ROM8[000082E5]<<8 and ROM8[000082E4]<<8 apply upper then lower
limits, including unordered endpoints.

The fallback tests FFFF328C and FFFF3288 with the same channel+1 mask.
Without a selected counter it writes neutral 00006400. Otherwise it
reads the full signed32 accumulator at FFFF3310+4*channel and moves it
toward neutral by raw ROM8[000086F5]. Exact signed comparisons, neutral
crossings, both accumulator stores and conditional clears of the two
raw masks remain in the complete path. The full produced R2 can contain
a negative signed32 value; its low16 is physically stored without an
additional producer-signedness claim.

Instruction 0005B6F0 writes the indexed word from complete R2. In shared
mode 0005B6F2 copies that complete R2 to R0 and 0005B6F4 also writes
FFFF2A26. Both writes remain separately observed when their addresses
coincide. Individual mode preserves the independently seeded sibling.
No helper, stock call, boundary return, observer or native profile is
substituted. The complete leaf returns naturally through the RTS delay
slot that restores full R9.

Separate wide equations bind every physical ROM/RAM operand and exact
write order. The complete independent instruction trace binds all CPU
registers, saved R9-R14, frame and SP/PR. GBR, MACH, MACL, M/Q and other
SR controls are preserved; final T comes from the actual shared-mode
test. All 65536 RAM bytes and immutable code, pools and controls remain
observed. Only declared four-byte RAM pointers are relocated for the
existing simulator. Every instruction byte remains stock.

Bank1 prior-word and full accumulator alternatives require changed
actual FFFF2A24 storage while every other complete input stays fixed.
Ordinary and shared sibling alternatives require their distinct
preservation/overwrite behavior without an unrelated prior-sibling
effect on full output CPU, frame and other RAM. Independent high24
bits of the incoming channel require identical complete output state.
A matching low16 store, truncated accumulator, shifted-bit mask or
supplied produced R2 cannot replace these complete requirements.
