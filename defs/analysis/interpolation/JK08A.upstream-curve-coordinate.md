# Indirect source-curve consumption through the complete coordinate caller


## Exact retained association

The original claim is
`37856daa195a7441c7da5fbe779866ada65f2da4b1782dc7a3cc626e4ebe12db`:
ROM14E42 has a reader association with primitive 264F8. The association denotes
indirect consumption of a derived coordinate. The complete caller interpolates
ROM14E42 through 264CC, retains its full R0 return in R2 and forms the real R6
input of 264F8 through arithmetic, comparison and conditional division.
264F8 physically reads its supplied ROM151F2 curve, not ROM14E42.

One ordinary owning operation appends one identity proof to this reader.
The complete native table owner and all three function documents remain fixed.
The unit BFS, candidate scale x*0.000488, inverse x/0.000488, unset semantic
width and signedness, other associations, ledgers, evidence and TEST positions
remain exact. The proof grants no scale, units, geometry, natural caller
reachability, scheduling or hardware admission.

## Actual return, arithmetic and delay-slot coordinate

The full fifth argument is read from the original SP into R6. Its low byte is
stored at original SP+3 without changing the high24 carrier. The local byte
comes from entry R7 and is stored at SP-29. The initial signed entry R6 is
divided by 20000 with truncation toward zero. Subtracting 50 times the unsigned
local byte forms the adjusted value. Values above 30267 select 32767; values
below -35268 select -32768; other values add 2500. The result is narrowed as
a signed word and clamped nonnegative before entering R14.

The source coordinate is the low byte of the fifth argument shifted left by 8.
Call B7AAC reaches 264CC with ROM14E42 and axis13BB8. The source curve has
8 active words and one physical guard word; its axis has 8 words.
At B7AB0 the full R0 return is copied to R2. EXTU.W at B7ACA transfers that
return to R6. The independent B term is the initial R14 multiplied by
ROM8A30: products above 0x1FFFE select full R12=0xFFFFFFFF, while other
products are shifted right by one. B is the low word of this full result.

H is the low word of entry R4. The source value is negated and multiplied by
the unsigned ROM8832 byte. The complete product reaches R6 in the B7ADC
delay slot. With H nonzero, signed division receives the product multiplied
by 20. Quotients at least -65535 are decremented; smaller quotients select
zero. With H zero, a negative product selects zero and a zero product selects
-1. The actual EXTU.W R6,R6 at B7B16 is the delay slot of call B7B14 to264F8.
The consumer curve is ROM151F2 with axis13BF8, 16 active words and one physical
guard word; its axis has 16 words.

Both complete explicit wrappers search the axis from its final knot backward,
read the selected word and its physical next word, and tail naturally to26740.
A positive bracket uses the full 26C78 fraction division. The integer result
is first +/- floor(abs(second-first)*fraction/65536). A zero fraction removes
the guard's arithmetic weight without removing its physical word read.

The consumer return supplies weight 255-min(return_u16,255). The low entry R5
byte plus one is capped at four. Its first state selects coefficient10; the
other states read ROM8A35, ROM8A36 or ROM8A34 as full signed bytes before the
real unsigned byte extension. The two actual 21CE0 calls compute
q1=floor(B*weight/255) and q2=floor(low16(q1)*H/2500). The full low32 product
q2*coefficient is stored from R2 to RAM3228 at B7B84. Prior3228 is not read.
