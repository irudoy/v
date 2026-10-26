# JK08A bounded main RPM fuel-cut state

## Main RPM fuel-cut state

Stock configuration 00008b38=63 has bit 7 clear. Raw selector byte ffff2468.bit4
chooses activation/release pairs (612,596) or (596,368). The third pair (0,0)
belongs to the guarded path.

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

Physical RPM scaling, periodic decrement production, upstream state/selector
reachability, interrupt delivery, full ECU scheduling, invocation cadence,
the global inhibit coordinator and actual fuel delivery require separate
evidence. This entry does not establish those mechanisms.
