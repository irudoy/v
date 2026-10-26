# JK08A cached publication inhibit and snapshot

Source bindings: `JK08A.publication-inhibit-path.toml`.


The normal lookup mode derives a saturated byte coordinate from the RPM word
at `FFFF114A`, reads the byte calibration at `0001202E`, and retains its result
at `FFFF1EE0` and `FFFF257A`. That invocation forces `FFFF1072` to zero. The
second invocation tests the retained Boolean value together with
`FFFF2451.bit7` before publishing the filtered word's high byte or zero.
The bounded scheduler instructions copy the resulting live bytes beginning at
`FFFF1072` to the snapshot beginning at `FFFF106A`.
