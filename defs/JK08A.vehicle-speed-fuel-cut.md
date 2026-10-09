# JK08A bounded vehicle-speed fuel-cut state

## Vehicle-speed fuel-cut state

The bounded entry 0004f19c binds 63 stock instructions and 153 bytes.
The literal matrix has 12544 independent contexts. Hardware readiness is NO.

The invocation does not decrement the counter. The observer checks full SR/MQT.

The natural stock entry `0004f19c` returns bit 0 of `ffff24a6` and updates a
coarse vehicle-speed fuel-cut state. The function reads the raw speed byte at
`ffff110e`, the complete control byte at `ffff24a7`, and the delay counter at
`ffff24f6`. Its two code spans are `0004f19c..0004f1d8` and
`0004f240..0004f282`. All 63 instructions retain the stock ROM bytes.

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

## Bounded executable observations

The declared matrix has 12,544 contexts and ten natural path classes. It
covers all 256 state bytes, all 256 control bytes, all 256 counter bytes,
speed boundaries 0, 90, 91, 92, 93, 94, 127, 128 and 255, and all 128
combinations of T, IMASK, Q and M controls. These sets occur in separate
bounded partitions; the matrix is not their full Cartesian product.

Independent literals describe all fifteen GPRs, the complete controlled SR
and final T. The observer independently captures actual status bits outside
the declared controls and retains them through entry and return. It checks
natural PR/SP, MACH/MACL/GBR, the C caller ABI, an 80-byte frame, all 64 KiB of
working RAM, and all 27 bound pool and calibration bytes. The only stock
frame write is the four-byte saved GBR at offsets 44..47. R7 receives the
sign-extended incoming control byte and is an outgoing clobber.

Six stock long pools supply the working base, speed base and calibration
addresses. Three RAM long values have declared simulator translations;
instruction bytes, calibration bytes and stock call/return behavior retain
their original values. The function uses no helper stubs. Software execution
does not establish the global inhibit coordinator, interrupt delivery,
physical units, complete ECU scheduling or hardware readiness.
