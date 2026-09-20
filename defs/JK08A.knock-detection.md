# JK08A knock-threshold detection

## Scope and result

This specification separates the active per-channel knock-threshold table at
`0x1108E` from the structurally similar but unreferenced calibration bank at
`0x10F8E`. Exact JK08A code reads only `0x1108E`. The neighboring bank does not
participate in the unmodified firmware and is hidden from tuning definitions.

The active table has six rows of sixteen big-endian `uint16` thresholds. Code
proves a one-based evaluator-channel selector and engine-speed interpolation.
It does not prove the physical cylinder order or the catalog-derived knock
strength scale.

## Active lookup

Function `0x00049FFC` selects a one-based channel and interpolates one row:

```text
if ROM8[0x8B3D].bit3 == 0:
    channel = uint8[0xFFFF11DE]
else:
    channel = uint8[0xFFFF2143]

row = 0x1108E + 0x20 * (channel - 1)
threshold = interp_u16_1d(
    row,
    axis=0x15340,
    input=uint16[0xFFFF11F4]
)
uint16[0xFFFF2144 + 2 * (channel - 1)] = threshold
```

Stock `ROM8[0x8B3D]` is `0x82`, so bit 3 is clear and the exact image selects
`0xFFFF11DE`. A zero channel causes the evaluator to return before the lookup.
The speed input is the code-proven RPM/12.5 word. Static editor labels render
the sixteen positions as 400..6400 RPM, matching the exact axis contents.

Rows 3 and 5 contain only `0xFFFF`; rows 1, 2, 4, and 6 contain finite
thresholds after their first `0xFFFF` cell. This establishes which stored rows
are effectively disabled across the stock speed range. It does not establish
the physical cylinder or sensor associated with any row.

## Evaluator outputs

Function `0x0004A238` calls `0x00049FFC`, compares the selected calculated
metric with the stored threshold, and updates three outputs:

- `0xFFFF24C2.bit6` is the current selected-channel comparison result;
- `0xFFFF2150` is the six-position current-result bitmap;
- `0xFFFF2142` is the saturating interval event count consumed and cleared by
  knock timing-state coordinator `0x000493E8`.

An exceedance sets the selected bitmap bit and increments the event count up
to `0xFF`. A non-exceedance clears the selected bitmap bit. Threshold
`0xFFFF` is the `uint16` upper bound and effectively suppresses an exceedance
on the established metric path.

The event count influences the timing-state coordinator described in
`JK08A.ignition-state.md`. It is not itself a commanded retard value.

## Margin telemetry

The evaluator leaves both comparison operands in RAM: the offset-binary metric
of the evaluated channel at `int32[0xFFFF21D8 + 4 * (channel - 1)]` and its
threshold at `uint16[0xFFFF2144 + 2 * (channel - 1)]`. The stock comparison is
`threshold + 0x80000000 < metric` on unsigned 32-bit values. Every evaluation
overwrites the pair of its channel, so a pointer sampled at the snapshot rate
misses the evaluations between two snapshots.

The custom CAN telemetry wraps the evaluator behind its only reference, literal
`0x0004A9C0` in `FUN_0004A8D4`. The caller reads no register that the evaluator
leaves, so the wrapper calls the stock evaluator first and then repeats the
channel selection and the comparison on the stored operands. It keeps the
per-channel minimum of `threshold - metric` as a signed word at
`0xFFFF5E10 + 2 * (channel - 1)`. An exceedance yields a negative margin
limited at `-32768`. Context tag 4 of the `tuning` profile publishes the six
minimums and rearms them with `32767`, which stands for an interval without an
evaluation of the channel or a margin of 32767 or more. A row of `0xFFFF`
thresholds therefore reports `32767` until its metric exceeds 32768 evaluator
units. `patches/can-telemetry.md` defines the wire contract.

## Unreferenced bank at 0x10F8E

`0x10F8E..0x1104D` is another 192-byte, 6x16 `uint16` array. It resembles the
active table and has the same all-`0xFFFF` rows 3 and 5, but resemblance is not
execution evidence.

The exact-image reference audit establishes all of the following:

- the Ghidra direct and literal-pool reference census has zero hits anywhere
  in `0x10F8E..0x1104D`;
- the complete ROM contains no exact 32-bit value `0x00010F8E`;
- the recovered interpolation inventory assigns zero accessors to `0x10F8E`;
- active base `0x0001108E` occurs exactly once, at literal `0x0004A204`;
- instruction `0x0004A014` loads that literal and `0x0004A02C` calls the
  interpolation wrapper with the derived row address.

The unreferenced bank therefore has catalog role `dead` for exact JK08A code.
Changing it cannot alter the active threshold calculation unless executable
code is also changed to reference it.

## Calibration boundary

- Only `0x1108E` is an active threshold calibration in the exact image.
- Increasing an active raw threshold makes an exceedance less likely; lowering
  it makes an exceedance more likely.
- Rows 3 and 5 are disabled by `0xFFFF` stock contents, but their physical
  channel identities remain unverified.
- The `x * 0.0015259` knock-strength conversion is catalog-derived and remains
  candidate evidence. Raw comparison behavior is code-proven.
- Channel-to-cylinder mapping and physical scale require controlled signal or
  vehicle validation before per-cylinder tuning decisions.
