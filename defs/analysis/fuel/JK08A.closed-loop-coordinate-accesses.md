# Bounded JK08A coordinate input and publication accesses

`JK08A.closed-loop-coordinate.toml` binds the real parent call at
`0003EE7A` to the complete natural conditioner `0003EF74`. The parent
window is `0003EE5C`..`0003EE7E`, inside normalized function `0003EDB4`.
Five real helpers execute:
`000264A0`, `00026944`, `00026740`, `00026C78` and `00021BBC`.

## Explicit caller inputs

Incoming GBR=01008544 selects the declared caller workspace. The first
unsigned source word X0 is at01008554. Incoming full R0 supplies X1 through
the low-word store at0003EE60 to01008556. Upper-word R0 alternatives retain
this physical truncation. The source-selection and doubling instructions
before the window have no execution admission from this entry.

The caller reads speed word FFFF110A at0003EE6A and coefficient-input word
FFFF4524 at0003EE72. Their actual MOV.W sign extension and the call delay
slot determine R5 and R6. The natural helper explicitly zero-extends their
low words. R4=01008554 names the source pair, R7=01008558 names the output
pair, and the caller stores coefficient pointer0100855F at its actual SP
before the call. The helper loads this fifth argument from SP+0x34 after
its real prologue. Full frame and post-delay argument comparisons bind
these premises. A register parameter alone supplies no helper-specific
physical RAM reader claim.

## Separate coordinate equations

The high byte of the coefficient-input word selects byte table00012292
over the existing byte axis00011B47. The real axis search and unsigned
fractional divider retain exact point, endpoint and interior behavior.
Ascending and descending interpolation use directional truncation:
`left +/- floor(abs(right-left)*fraction/65536)`. The selected coefficient
C is published as a byte atFFFF2F8E and through the real fifth argument.

Let H be unsigned ROM16[00008F98]. For each source X:

```text
D = clamp(X-H, -32768, 32767)
Q = C > 0 ? clamp(trunc0(128*D/C), -32768, 32767)
          : (D < 0 ? -32768 : 32767)
A = H+Q
G = speed < 65280 && speed > ROM16[000095C6]
    && (sample > ROM16[00009384] || sample < ROM16[00009386]) && C > 0
Z = G ? uint16(max(0,A)) : X
```

The first signed clamp precedes multiplication and division. The final
word conversion retains modulo65536 behavior; it is not an upper clamp
at65535. The stored second word and terminal full R0 remain distinct:
admission retains max(0,A1) in the register, while bypass uses the natural
MOV.W sign extension of X1. Zero coefficient avoids both signed calls
and preserves the independently seeded divider fault wordFFFF9818.
The signed divider's zero-divisor and wide-divisor paths retain byte
identity without an execution claim from this caller domain.

## Native workspace and complete observations

The stock word at0003F002 remains8560. The natural helper executes its
original LDC and uses exactly20 bytes atFFFF8560..FFFF8574. The independent
state engine admits this storage only for the exact descriptor and pinned
native-storage declaration, with a separate frame-disjointness condition.
Other accesses retain their existing admission rules.

The existing native observation pattern captures all256 bytes atFFFF8500
before and after the invocation. Native neighbors outside the20-byte
workspace remain exact. The separate raw64KiB RAM observation retains
its unchanged mirror bytes at01008560..01008574. Only the declared20 native
bytes overlay that range for the independent logical-state comparison.
The explicit relocated caller workspace and native helper workspace are
separate observed storage. The observation does not infer an unexecuted
parent prologue or hardware memory timing.
