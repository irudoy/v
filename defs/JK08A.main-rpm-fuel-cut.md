# JK08A bounded main RPM fuel-cut state

## Main RPM fuel-cut state

The bounded entry 0004f282 binds 81 stock instructions and 196 bytes:
162 instruction bytes, five long pool words, configuration byte 00008b38,
delay byte 00008c69 and six threshold words at 0000934e..00009358.
The two declared long RAM translations bind ffff244c and ffff119c to the
positive simulator RAM window. The natural RTS delay slot restores GBR.
Hardware readiness is NO.

Stock configuration 00008b38=63 has bit 7 clear. Raw selector byte ffff2468.bit4
chooses activation/release pairs (612,596) or (596,368). The third pair (0,0)
and its guarded path have identity-only evidence in this stock domain;
their execution is outside the contract. No calibration byte changes during
the bounded invocation. Other configuration-byte consumers retain their own
evidence.

The raw state byte is ffff2497. Bit1 is the arm and bit2 is active. While active,
RPM word ffff11bc at the release threshold or above preserves the state;
only a value below release clears both bits. While inactive, a value below
activation clears the arm. At activation or above, a clear arm loads the
stock delay into ffff24f1 and sets the arm. An existing arm retains its
incoming counter. Counter zero sets active; nonzero preserves the inactive
state. The function does not decrement the counter in this invocation.
All other state bits retain their incoming values.

Step 11 takes from as the four row-major words of the owned 2x2 table,
x=raw RPM and prev=incoming flags; bit 4 selects indices P and 2+P.
Step 12 takes from=raw RPM and prev=incoming flags;
its numerical expression reads the actual table pair through selector bit 4.
Auxiliary K is the stored delay byte. Both output the complete raw flag byte
and have sign none. Equality at activation admits the state transition;
equality at release retains active state. A stock zero reload applies to
a newly armed transition; an already armed nonzero counter still waits.

The literal matrix has 6400 independent contexts. It covers all 256 incoming
flag bytes, selector bytes and counter bytes; both table pairs; the raw RPM
boundaries 0, release-1, release, activation-1, activation, activation+1,
32768 and 65535; and all 128 supported incoming SR/MQT combinations.
The first six contexts contain all six branch outcomes. These axes do not
form the full Cartesian product and do not establish physical reachability.

The observer compares all fifteen natural exit GPRs, full SR/MQT,
MACH/MACL/GBR, PR/SP, a distinct C caller ABI, all 64 KiB RAM and all 34
pool/configuration/threshold bytes. Its independent 80-byte SP-48..SP+31
frame permits only the four-byte saved GBR at offsets 44..47. R7 is the
declared driver call target; the stock entry preserves it. Full incoming
GBR/MACH/MACL words include zero, all ones and both sign boundaries. The observer changes only
T, IMASK, Q and M in the actual incoming SR, retains every other status bit,
and independently compares the context pointer and R3 before and after
status preparation. The complete exit SR uses the independently observed
original status and the literal expected controls.

The numerical contract compares both complete flag/counter views with the
6400 literal contexts. Eight semantic mutations cover strict cut/release
equality, ignored arm counter, wrong selector bit, lost other flag bits,
signed RPM comparison, omitted delay loading and an in-call decrement.
Executable acceptance requires the exact-stock fixture and the mandatory
complete standard gate with EARLY_ONLY=0.

Physical RPM scaling, periodic decrement production, upstream state/selector
reachability, interrupt delivery, full ECU scheduling, invocation cadence,
the global inhibit coordinator and actual fuel delivery require separate
evidence. This entry does not establish those mechanisms.
