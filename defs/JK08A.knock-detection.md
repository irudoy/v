# JK08A knock-threshold detection

## Scope and result

This specification separates the active per-channel knock-threshold table at
`0x1108E` from the structurally similar but unreferenced calibration bank at
`0x10F8E`. Exact JK08A code reads only `0x1108E`. The neighboring bank does not
participate in the unmodified firmware and is hidden from tuning definitions.

The active table has six rows of sixteen big-endian `uint16` thresholds. Code
proves a one-based evaluator channel taken from the engine-event index, one
evaluation of every channel per engine cycle in a fixed crank-angle window,
and engine-speed interpolation. It selects no knock sensor per channel and
does not prove the catalog-derived knock strength scale.

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
thresholds after their first `0xFFFF` cell at 400 RPM. A `0xFFFF` threshold
admits an exceedance only for a metric above 65535 (see
[Evaluator outputs](#evaluator-outputs)), and
[Channel schedule](#channel-schedule) gives the crank-angle window that each
row serves.

## Channel schedule

Crank tooth handler `FUN_00029588` opens one knock window per 120 crank
degrees on tooth 7 and closes it on tooth 0, 50 degrees later:

```text
tooth 7: call 0x0004A5AC at 0x000297B0               open the window
         if 0xFFFF8501.bit7:                         crank synchronized
             uint8[0xFFFF11DE] = uint8[0xFFFF13C8]   store at 0x000297DE
tooth 0: call 0x0004A8D4 at 0x0002A1DE               close the window
             call 0x0004A238 through literal 0x0004A9C0
```

The window start runs before tooth 7 copies identified cylinder `0xFFFF13C8`
into event index `0xFFFF11DE`, so the evaluator on tooth 0 selects the index
of the tooth-7 event that opened the window. `FUN_0004A8D4` calls the
evaluator on every tooth 0 while `ROM8[0x8B3D]` bit 7 enables the window, and
the evaluator returns early only for index 0. Under crank synchronization the
index, which is the cylinder number, advances 1-2-3-4-5-6 in firing order
([`JK08A.fuel.md`](JK08A.fuel.md#reference-tooth-and-cylinder-order)), so
every channel is evaluated once per engine cycle. Channels 3 and 5 run the
same window, acquisition, metric, and comparison as the other channels; the
channels differ only in their threshold row, reference row, and result slots.

Tooth 7 is 110 degrees before compression TDC of its event cylinder in the
firmware coordinate of ignition command
`ROM8[0x83D5] - advance = 110 - advance`. The window of channel `c` therefore
spans 110..60 degrees before compression TDC of cylinder `c`, which is 10..60
degrees after compression TDC of cylinder `c - 1` (cylinder 6 for channel 1).
The windows of channels 3 and 5 span 10..60 degrees after compression TDC of
cylinders 2 and 4.

With stock `ROM8[0x8B3D] = 0x82`, the window start programs one acquisition
for every channel: DMAC channel 2 reads `ADDR24` (`SAR2 = 0xFFFFF840`), and
`ADCSR2 = 0x59` selects 4-channel scan mode over AN24 and AN25 with the A/D2
interrupt enabled. With bit 3 set, which the stock image does not select, the
window start stores the index before the tooth-7 copy, `c - 1`, as channel
`0xFFFF2143` and alternates the input by its parity: odd channels keep
`0xFFFFF840` and `0x59`, and even channels take `ADDR28` (`0xFFFFF848`) and
`ADCSR2 = 0x5D`, AN28 and AN29. On the stock path the channel number
therefore selects no A/D input. The code does not identify the sensors wired
to AN24, AN25, AN28, and AN29.

## Evaluator outputs

Function `0x0004A238` builds the metric of the selected channel `c`, calls
`0x00049FFC`, compares the metric with the threshold, and updates the
reference of the channel:

```text
c = uint8[0xFFFF11DE]                               return when c == 0
if uint8[0xFFFF2154] == 0:                          no DMAC block completed in the window
    v[i] = 0xFFFF                                   i = 0..7
else:
    v[i] = window value i through 0x00021CE0
d[i] = v[i] - reference[c][i]                       reference at 0xFFFF2178 + 16 * (c - 1)
s = sum of the ROM8[0x8870] = 3 largest d[i] outside mask ROM8[0x8618] = 0x00
metric = sign(s) * min(g * |s| >> 14, 0x7FFFFFFF)   g = ROM8[0x86AC] * ROM8[0x8694] * ROM8[0x86A7] >> 7
exceedance = metric > threshold                      threshold + 0x80000000 < metric + 0x80000000
reference[c][i] = (224 * v[i] + 31 * reference[c][i]) >> 8, plus 1 when below the old value
```

The stock bytes `ROM8[0x86AC] = ROM8[0x8694] = ROM8[0x86A7] = 0x80` give
`g = 16384`, a gain of exactly 1. The metric is therefore the sum of the three
largest rises of the window values over the reference of the channel and lies
in -196605..196605. The reference weight is `ROM8[0x884B] = 0xE0`. While
runtime diagnostic record `0x12D` or `0x13F` has byte-1 bit 7 set (predicate
`0x00025E20`), the update sets every reference to `ROM16[0x9282] = 0xFFFF`
instead. Threshold `0xFFFF` admits an exceedance only for a metric above
65535. A window without a completed DMAC block substitutes `0xFFFF` for every
value, and its metric is 196605 minus the sum of the three smallest references
of the channel.

The evaluator updates three outputs:

- `0xFFFF24C2.bit6` is the current selected-channel comparison result;
- bit `c - 1` of `0xFFFF2150` is the current comparison result of channel `c`;
- `0xFFFF2142` is the saturating interval event count consumed and cleared by
  knock timing-state coordinator `0x000493E8`.

An exceedance sets the selected bitmap bit and increments the event count up
to `0xFF`. A non-exceedance clears the selected bitmap bit. The coordinator
consumes the count, not the bitmap.

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
evaluation of the channel or a margin of 32767 or more. With one evaluation of
each channel per engine cycle, every 51.2 ms tag-4 interval holds an
evaluation of every channel from 2343.75 RPM, `0xFFFF11F4` 188, upward; below
that speed an interval can end without one. A row of `0xFFFF` thresholds
publishes a value below `32767` only for a metric above 32768, so on channels
3 and 5 the value `32767` does not distinguish an interval without an
evaluation from evaluated metrics of at most 32768. The profile carries no
evaluation count or metric per channel. `patches/can-telemetry.md` defines the
wire contract.

## Vehicle result of 2026-09-21

Registry entry `knock_margin.vehicle_2026_09_21` in
[`../patches/hardware-results.toml`](../patches/hardware-results.toml) holds
the knock margins of the eleven profile-5 captures of the 2026-09-21 road
session. The image carries the stock `0x1108E` rows and evaluator constants.
Channels 3 and 5 publish `32767` in all 18,893 tag-4 groups of the seven TRC
captures and carry no value in any of the 279,143 MLG records. Of those
groups, 1,158 have `0xFFFF11F4` 188 or more; there channels 1, 2, 4, and 6
carry an evaluated margin in every group and channels 3 and 5 in none. Every
evaluation of channels 3 and 5 in those intervals therefore has a metric of
at most 32768.

From `0xFFFF11F4` 64, the first axis point at which rows 1, 2, 4, and 6 hold
finite thresholds, one evaluation per engine cycle predicts 2,968 of 11,340
groups without an evaluation of a given channel; channels 1, 2, 4, and 6
publish `32767` in 2,936..2,944 of them. The idle values of the valued
channels follow the evaluation cadence.

| Channel | Idle TRC groups | Lowest margin | Largest metric |
| ---: | ---: | ---: | ---: |
| 1 | 8,731 | -1,957 | 15,190 |
| 2 | 8,739 | -1,680 | 14,240 |
| 3 | 18,893 | `32767` | at most 32768 |
| 4 | 8,730 | -3,018 | 20,627 |
| 5 | 18,893 | `32767` | at most 32768 |
| 6 | 8,732 | -3,939 | 13,226 |

The lowest margins cover all eleven captures, and none reaches `-32768`. The
metric of a group is the image threshold at the captured `0xFFFF11F4` minus the
published margin. From `0xFFFF11F4` 512 upward the threshold is the last row
cell, so the largest metrics, all at `0xFFFF11F4` 603..617 in the Map 3
full-pedal run of `6-map-1-3-4-limiter.mlg`, are exact. The largest, 20,627 on
channel 4 at 7537.5 RPM with margin -697 against threshold 19,930, falls
inside the main fuel-cut cycling of `main_fuel_cut.vehicle_2026_09_21`. The
latched bitmap is nonzero in 90 records, its union `0x2B` holds only the bits
of channels 1, 2, 4, and 6, and the latched count never exceeds 1.

The recordings bound the metric of channels 3 and 5 at 32768 without
observing it. The largest metric of the valued channels lies below that
bound, so evaluations with metrics like theirs publish `32767` on channels 3
and 5 as well.

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
- Rows 3 and 5 hold `0xFFFF` in stock and admit an exceedance only for a
  metric above 65535; the 2026-09-21 recordings bound their metric at 32768
  without observing it.
- The `x * 0.0015259` knock-strength conversion is catalog-derived and remains
  candidate evidence. Raw comparison behavior is code-proven.
- The combustion event that each channel window observes, the sensors behind
  AN24 and AN25, and the physical scale require controlled signal or vehicle
  validation before per-cylinder tuning decisions.
