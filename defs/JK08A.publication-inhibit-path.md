# JK08A cached publication inhibit and snapshot

`defs/JK08A.publication-inhibit-path.toml` bounds the stock producer `0003E1DA`,
its natural predicate and lookup helpers, and the snapshot window starting at
`00020F1C`. The stock instruction bytes and literal inventory require exact
independent GNU reconstruction. Pointer aliases and the native `FFFF84C3`
control view have separate explicit boundaries.

The input sequence invokes the complete producer with the configured initial
mode, sets only `FFFF2459.bit5` before the second producer invocation, and then
enters the bounded snapshot window with explicit R11=`00022558`. All other RAM
retains the previous actual output. This mode change is an explicit external
input; the sequence establishes no natural caller or scheduler reachability.

The normal lookup mode derives a saturated byte coordinate from the RPM word
at `FFFF114A`, reads the byte calibration at `0001202E`, and retains its result
at `FFFF1EE0` and `FFFF257A`. That invocation forces `FFFF1072` to zero. The
second invocation tests the retained Boolean value together with
`FFFF2451.bit7` before publishing the filtered word's high byte or zero.
The bounded scheduler instructions copy the resulting live bytes beginning at
`FFFF1072` to the snapshot beginning at `FFFF106A`.

The return after the bounded snapshot instructions is simulator-only. Its
separate assembly restores PR from the observing entry frame and returns
through R7. It changes no tested stock instruction and admits no remaining
scheduler body, live cadence, hardware atomicity or peripheral behavior.

This descriptor and its input/equation sources grant no ROM-reader replacement,
native geometry, evidence level, review retirement, receipt or hardware
qualification. A complete original raw producer, independent full-state and
numeric consumer, joint native relation admission and exact ledger-selector
transition are required separately.
