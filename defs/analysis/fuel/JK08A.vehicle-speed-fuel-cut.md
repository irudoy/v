# JK08A bounded vehicle-speed fuel-cut state

## Vehicle-speed fuel-cut state

The natural stock entry `0004f19c` returns bit 0 of `ffff24a6` and updates a
coarse vehicle-speed fuel-cut state. The function reads the raw speed byte at
`ffff110e`, the complete control byte at `ffff24a7`, and the delay counter at
`ffff24f6`. Its two code spans are `0004f19c..0004f1d8` and
`0004f240..0004f282`.

## Raw state transition

Bit 0 of the incoming state byte selects active and inactive paths. An
inactive state below the activation byte `ROM8[00008db7] = 93` clears control
bit 7 and leaves the state and counter unchanged. At speed >= 93, a clear
control bit 7 loads `ROM8[00008caf] = 0` into the counter and sets control bit
7. A zero counter and clear control bit 5 set state bit 0. An already armed
nonzero counter waits without decrementing it.

For an active state, control bit 5 clears state bit 0. Speed below the release
byte `ROM8[00008dc3] = 91` clears both state bit 0 and control bit 7. At speed
>= 91, the incoming control bit 7 is retained, including when the control
bit 5 gate clears the state. The counter is unchanged on every active path.
All unrelated state and control bits are retained.

The speed and threshold comparisons preserve the unsigned byte ordering.
The stock loads sign-extend speed into R6, but unsigned `CMP/HS` compares its
32-bit representation with positive thresholds 93 and 91. Raw speed bytes
128..255 therefore satisfy both thresholds. A physical speed conversion,
counter cadence and engine reachability require separate evidence.

## Arithmetic view

The chain input `from` is the raw speed byte and `prev` is the complete
incoming state byte. `J` is the complete outgoing control byte, `K` is the
outgoing counter, and `D` is the returned Boolean.

```text
F = uint8(prev); C = RAM8[ffff24a7]; A = F&1;
B = (C>>7)&1; G = (C>>5)&1; S = uint8(from);
L = ROM8[00008db7]; H = ROM8[00008dc3];
N = min(1,max(0,S-L+1)); V = min(1,max(0,S-H+1));
U = (1-A)*N*(1-B);
K = (1-U)*RAM8[ffff24f6]+U*ROM8[00008caf]; Z = 1-min(1,K);
E = A*V*B+(1-A)*N; J = uint8((C&127)|(128*E));
D = (1-G)*(A*V+(1-A)*N*Z); to = uint8((F&254)|D)
```
