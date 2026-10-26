# JK08A bounded fuel-cut consumer

## Fuel-cut consumer and event history


The one-shot takes the whole mask from independent R4 and six duration words
from independent R5. The accepted domains include both ffff224e and ffff1568
arrays. Channels are i in 0..5. Formula arguments x=[R4,i,duration[i]] bind
the selected raw duration explicitly; they do not infer a producer or require
a single duration-array base. The prior counter word is prev. Step23 uses
from=inhibit byte ffff22e0; step25 uses from=entry history byte ffff1935.

With ffff4184.bit7 clear, all counter words, DSTR and history are preserved.
With the bit set, any intersection of the whole mask with the inhibit or
entry-history byte selects unsigned16 opening word ffff23aa for every
selected channel. The consumer ORs the whole low-byte mask into history.
An individual channel-bit test does not express this selection condition.
No selected bit in 0..5 means no counter, DSTR or one-shot history store,
including a mask whose only set bits are 6/7.

An already set DSTR bit i subtracts opening with floor 0. The increment is
min(65535,floor(800*d/256)), or 1000 under ffff4251.bit0. The raw counter
addition uses uint16 wrap, and DSTR ORs the selected bits. Other control
bits do not change these conditions. Counter wrap and aggregate selection
prevent a universal positive or negative influence; both step signs are none.

For step24, from is the incoming rotating count ffff1937 and prev is incoming
history ffff1935. RAM8[ffff1936] is read after the event handler copies pending
byte ffff2228 into it, before its history operations. The handler always
clears every bit of this current mask from history. If both the count and
the entire inhibit byte are nonzero, it decrements the count once and ORs
the entire mask into history, even when one-shot output is disabled or the
mask does not intersect inhibition. Auxiliary R in the formula is the
stored remaining count.

The real one-shot call can OR that mask into history again. The final history
formula includes its enable bit, the existence of a selected channel0..5,
and the whole-mask intersection with inhibition or the history immediately
before that call. It includes this call and the handler's
earlier history store. Its sign is none.

Mandatory arithmetic gates compare both counter formulas with 48072 raw
counter observations each and the history/count formula with all 7254 complete
event cases. Eight semantic mutations reject individual-bit intersection,
counter saturation in place of wrap, omitted opening subtraction, altered
diagnostic increment, omitted history clearing, inhibit bit0 in place of
nonzero-byte admission, omitted called-consumer publication and ignored
output enable. Explicit witnesses distinguish a multibit mask from an
individual channel test, disabled-output count/history updates and a
high-only mask without a selected channel.

| Owned operand | Role in the bounded consumer |
| --- | --- |
| 0002c13c | Complete one-shot function |
| 0002be40 | Complete event handler |
| 00054d3e | Real event duration selector |
| ffff22e0 | Entire aggregate inhibit byte |
| ffff1935 | Incoming, intermediate and final history byte |
| ffff1936 | Current mask copied before history operations |
| ffff1937 | Incoming and decremented release count |
| ffff23aa | Unsigned opening word |
| ffff4184 | Output-enable bit7 |
| ffff4251 | Diagnostic-increment bit0 |
| ffff224e | Scheduled duration-array base |
| ffff1568 | Alternate duration-array base |
| ffff2228 | Pending mask copied by the event handler |
| fffff640 | First counter word; six selected words at base+2*i |
| fffff666 | Start-register bits0..5 |

The event observer retains the accepted explicit return transport and complete
SH-2E exception stack. SPC/SSR peripheral exception behavior is outside this
software invocation. Synthetic register storage does not establish timer
evolution, physical units, channel-to-cylinder wiring, injector timing or fuel
delivery. Upstream inhibit/count/one-hot producers, physical reachability,
operating cadence and engine hardware validation retain separate evidence.
