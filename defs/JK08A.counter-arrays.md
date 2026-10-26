# Bounded JK08A conditional counter-array writes

Three bounded windows bind nine original writer relations. Two windows of
`0002040C` are `000205A6..0002061A` and `000206A2..000206CA`. The first window
updates 138 bytes at FFFF256A, ten words at FFFF2604 and 195 bytes at FFFF43C7.
The second updates 244 bytes at FFFF42D3. The intermediate word array remains
in the complete physical and state contract; it grants no additional review
completion. The five exact ROM pointers are captured before and after each
invocation and relocated without changing tested instruction bytes.

The third window, `0002093E..00020962` of parent `000208F8`, updates 7 bytes
at `FFFF25FB..FFFF2602`. The holdoff byte `FFFF25FF` is offset four in this
array. Its exact nonzero path rereads the byte at `00020950` and stores the
truncated decrement at `00020956`; its zero path reads once at `0002094A`
and skips the store. The original L0 and TEST evidence retains its positions,
including the existing source contract for producer calls and holdoff use.
This bounded window supplies no independent producer-call, ISR-entry or
cadence reachability claim.

Each element is read once. Zero takes the skip branch and performs no store.
A nonzero element is read again, decremented, truncated to its byte or word
width and stored. Independent element equations retain unsigned zero
saturation, high-bit values and the word carry from 0100 to 00FF. Separate
instruction-state equations bind the exact read/repeated-read/store sequence,
conditional branches, complete RAM, registers, SR, frame, SP, PR and ABI.
The common default finite instruction limit applies without extension.


The 34 explicit inputs retain the previous eighteen counter rows and word
patterns, add the same nine seed/context patterns for the third window, and
add seven isolated holdoff byte values. Those isolated inputs hold every
other RAM byte, complete context and ROM pointer fixed. The shared driver
applies an explicit byte-input table before the raw snapshot; the RAM-clear
input source has no such table. Observer and raw transport ABIs remain exact.
Independent positive checks require the actual holdoff output and its
saturating relation to all seven isolated byte inputs.
