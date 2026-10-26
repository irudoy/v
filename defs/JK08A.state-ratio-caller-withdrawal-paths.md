# JK08A state-ratio and byte-transition caller withdrawals

Source bindings: `JK08A.state-ratio-caller-withdrawal-paths.toml`.


## Complete callers and physical input closure

Caller 64CB2 retains 64CB2..64DC4, 64E00..64ED4 and 64EE2..64FE2.
Caller BDC66 retains BDC66..BDCFA and BDD80..BDED8. The three intervening
literal holes remain data.

## Signed and unsigned state ratios

Configuration byte 870C and the independent RAM flag combinations choose the
primary or alternate ratio paths. The primary path updates flag 40 of 24A3 and
flag 01 of 246A. The divisor at 240E is a real sign-extended word. Zero bypasses
the division and publishes zero without a fault-helper entry. A nonzero divisor
and the sign-extended ROM word 8EA6 form a signed difference. The difference is
clamped to the signed 16 interval before the actual 32-bit left shift by 16.
The raw shifted word enters real 21BBC with the signed-word divisor.

Both divisor signs and both short/long quotient paths remain explicit. The real
DIV0S sign carrier is numerator-MSB XOR divisor-MSB, including zero numerator
with a negative divisor. Negative-divisor normalization and the exact sign
restoration instructions remain reachable. The signed quotient is interpreted
after its real 32-bit wrap, then independently floored at zero and capped at FFFF.
INT_MIN divided by minus one therefore retains its raw 80000000 result before
the caller's signed floor. A widened positive integer cannot replace that word.

The remaining primary path subtracts unsigned ROM word 906C with a zero floor.
The complete alternate body retains the 1082/108A threshold, the independent
246D/246A/2454/2450/2453/244F gates, and both configuration-selected byte inputs.
The 3373-based target is scaled by 256;the ramp retains its independent 13DE
addition, FFFF cap and target minimum. Exact 1770/176A/1774/1868 transfers and
every conditional publication remain distinct.

The variable unsigned-ratio path retains the minimum of 1774 and 1770 and the
complete sum of 1772 with unsigned ROM word 9456. Both actual comparisons must
establish a positive difference before real 21CE0 receives its divisor. The
divisor is bounded to 1..65535. The numerator is the real 32-bit product of the
positive difference and 1868. Exact short/long division, FFFF cap, 13DC decay,
the saved local flag byte and saved native pointer remain explicit. All known
returned registers and special registers are independent of the final stores.

## Byte transition, counter and saved candidate

The 8B34/8B42 special path retains its status gate and the unchanged RAM path
when 10E4 mask 08 is clear. EXTU.W bounds the 1000 word before its two arithmetic
right shifts and 255 cap. Both CMP/PZ branches are therefore fixed taken.
The alternate special path reads either signed ROM byte 851D or native byte 558A.

The main body retains every 246B/248B/41FA gate. ROM bytes 8D2D and 8D2E are
independent raw high and low thresholds. The sorted interior branch requires
low<coordinate<=high. The unsigned 1C5C/1C5E endpoint difference is a signed 32
carrier, its product enters real 21BBC, and the saved unsigned low endpoint is
added after truncation toward zero. This convex byte result is in 0..255, so the
upper-overflow branch at BDDDA is fixed fallthrough. Reversed or equal thresholds
retain their actual endpoint-selection path instead of a sorted-axis premise.

The complete candidate is saved at local SP and published separately to 1BEE.
The 24A7/previous 2326/1553/247B/1A1E gates and 25EE counter select a saved threshold,
the previous byte, or the previous byte plus one. With a zero counter, the
incremented candidate remains in the frame while the real curve call updates
1A1E and 25EE. Its return cannot replace the separate saved 2326 candidate.
The optional sign-extended 1704 byte is added to that candidate with independent
upper 255 and zero floors before the final byte 2326 publication.

## Exact fixed byte lookup and complete helper originals

The first physical byte curve is 12EFE..12F06 and the second is 12F06..12F0E.
Each has exactly eight independently controlled bytes. They are distinct,
contiguous and nonoverlapping. Configuration 8616 selects the first curve with
the actual unsigned 2772-byte times 32 divided by 20 and capped at 255, or the
second curve with unsigned 106F as coordinate.

The complete 26370 entry loads threshold 00E0 from 26382. Coordinates below 224
take the exact jump at 2637A and its real delay slot clearingR3, entering 26A80.
Only the actual byte-mode spans 26A80..26A9C and 26AAA..26ABA belong to this
closure. The fixed branch at 26A9A takes the byte path. The generic 26A60 entry
and its word mode are not admitted by this caller. The real 26740 interpolation
retains direction-dependent truncation, MACL preservation and its saved first
byte. Coordinates 224..255 return the sign-extended endpoint byte from the
real RTS delay slot 26380. Byte stores truncate that word;the helper return
and scratch state retain its complete sign extension.

The caller premises retain nonzero/signed-word or positive unsigned divisors,
the fixed byte mode, the two EXTU.W signs and the convex transition cap.
