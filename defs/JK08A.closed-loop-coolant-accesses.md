# Exact JK08A coolant constant readers

`JK08A.closed-loop-coolant-accesses.toml` binds the complete natural
`0005525A` invocation and its existing byte-curve and absolute-value callees.
The owning function is `knowing-potoo/fn`.

## Native owners and physical operands

| Owner | Native address | Semantic type | Physical read |
|---|---|---|---|
| `fuel_coolant_coefficients/const` | `0000990A` | unsigned8 | Selected byte at `000553E6` |
| `fuel_coolant_coordinate_offset/const` | `0005533C` | signed16 | Word at `0005532A` |

The load and RPM loops choose `load_bin` and `rpm_bin`. Each starts at one,
tests the next three observed byte thresholds in order, and retains four
when no earlier comparison admits the input. The selected coefficient index
is `4*rpm_bin+load_bin-5`. The physical address is `0000990A + index`.
Admission binds the exact index, address, byte value and lookup contribution.
All selected indices are required under the explicit software inputs. The
symbol name or presence of a lookup helper supplies no access admission.

The signed offset participates in
`uint8(4*max(0,uint8(previous_coolant)+int16(offset)))`. The real word load,
the byte read at `FFFF106F`, the signed lower clamp, byte truncation and
`EXTU.B` call delay slot retain their exact order. The natural byte lookup
uses `00012422`; its result is published at `FFFF15DD`. The selected
coefficient is published at `FFFF15DC` and multiplies that lookup result.
Conditional signed-difference rate limiting against old `FFFF15DA` and the
mixture-dependent cap precede the final derived word at FFFF15DA.

## Existing stock closure and observer

The complete unit contains 322 stock instructions, 644 code bytes and
126 pool bytes, for 770 bound bytes. Its seven long pointer aliases retain
the existing translation into ordinary simulator RAM. The source has no
additional native workspace, observing return stub or storage allocator.
All tested executable bytes remain stock.


BSR/JSR state binds the real curve call at `00055392` to `00026370`,
including its byte-extension delay slot and natural return to `00055396`.
The conditional absolute-value call at `0005541A` to `00022590` retains the
full signed difference, the actual flag store in delay slot `0005541C`,
SP/PR/GBR and natural return to `0005541E`. The root returns naturally at
`000554AA`. Separate numerical equations retain complete RAM, nested-frame
stores and full terminal CPU state alongside independent instruction state.

## Input-only domain and positive alternatives

The input parser preserves 14261 legacy input rows. It parses only the first
17 scalar inputs and five calibration arrays. The following nine scalar
results and local-result, incoming-register and expected-register arrays
are not parsed or compiled into the raw driver. Context variants and entry
SR are reconstructed from explicit input fields.

The 42 controlled calibration bytes contain the threshold/hysteresis data,
the byte curve, both byte axes, coefficient bytes, rate, cap and signed
offset. Additional inputs cover all selected coefficient bins, byte
boundaries, signed offset/clamp/wrap boundaries and fixed-other contrasts.
These profiles grant no stock calibration reachability or engine claim.

Each original constant needs different actual derived output words with
every other complete input fixed. Coefficient positives select the exact
native base byte at index zero. Offset positives hold all coefficient bytes
fixed. The positive key excludes only the operand's own bytes from both
the complete calibration preimage and its duplicate in the complete bound
snapshot. Full other RAM, context, frame, ABI, SP/SR, continuation and all
other calibration/code/pool bytes remain fixed. Merely changing the copied
coefficient byte at `FFFF15DC` does not satisfy this requirement.

There are 25 two-sided conditional sites in the root and natural helpers.
Both feasible outcomes are required. The separate byte-entry guard at
`26A9A` requires taken: real entry `26370` passes R0=224 and `SHLR8` makes
it zero. The original must not enter the word-only `26A9C..26AAA` span
(end exclusive). This exact call premise grants no general absence,
hardware, interrupt, scheduling or event-cadence claim.
