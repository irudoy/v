# JK08A paired request conditioning and constant calibrations

## Scope

This note records the exact code-level roles of the seven catalog maps that
previously had no semantic claim. The functions belong to paired raw-request
conditioning and boundary preparation around the first- and second-channel
raw outputs. Code does not establish physical torque, airflow, or throttle
units for these values, so the maps remain hidden from tuning editors.

## Paired zero-surface stages

`FUN 00070e4c` and `FUN 000720c4` have the same two-surface structure:

| Channel | Source | Endpoint A | Endpoint B | Endpoint scratch | Blend scratch | Processed word | Published word |
|---|---:|---:|---:|---:|---:|---:|---:|
| first | `ffff1210` | `0001050e` | `0001070e` | `ffff133a` / `ffff133c` | `ffff1212` | `ffff1330` | `ffff1332` |
| second | `ffff1248` | `00017cc8` | `00017ec8` | `ffff1cba` / `ffff1cbc` | `ffff124a` | `ffff1cb4` | `ffff1cb6` |

Both endpoint lookups use the channel source and `ffff10d2` as coordinates.
The first channel uses axes `000131e2` and `00015f20`; the second uses axes
`00018746` and `00019340`. Both channels use the Q16 weight `ffff190e`, which
`FUN 00070e4c` obtains from map `0001488a` and `FUN 000720c4` reuses.

For endpoint results `A` and `B` and weight `w`, both functions calculate:

```text
blend = floor((A * (65536 - w) + B * w) / 65536)
```

Every cell in all four endpoint surfaces is zero. The exact blend therefore
equals zero for every coordinate and weight. The reads still execute and the
intermediate RAM words are written.

Stock `ROM8[000089fb]` is `0x20`. Its clear bit 6 selects the direct blend for
the processed word. Its clear bit 3 makes both final selectors publish the
original channel source instead of the processed word:

```text
ffff1332 = ffff1210
ffff1cb6 = ffff1248
```

The blend scratch words have no external readers. The processed words are read
only by their own functions before the final selector. Consequently the four
surface results cannot affect a terminal consumer in unmodified JK08A even
though their lookups execute. Their catalog role is `dead` for this exact ROM.

`ffff1332` is consumed by `FUN 00073948`, `FUN 00073a44`, and monitor
`FUN 0008d10a`. `ffff1cb6` is consumed by the same monitor, which compares the
two published channels.

## Live normalization endpoint pair

`FUN 0007af78` interpolates lower endpoint `L` from `000154e0` and upper
endpoint `U` from `000154c0`. Both use axis `00014baa` and input `ffff113c`.
For each signed int16 input `I` in `ffff338c`, `ffff338e`, and `ffff3396`, it
calculates:

```text
base = max(0, 32768 + I - L)
span = max(0, U - L)

if span == 0:
    output = 800
else:
    output = min(800, floor(base * 800 / span))
```

The three outputs are `ffff3478`, `ffff347a`, and `ffff347c`. Both endpoint
curves contain only zero, so the stock span is zero and every output is exactly
800. These are live values rather than discarded scratch. `FUN 0007ae80` uses
them to bound `ffff2a7a` as follows, unless `ffff41f3.bit0` selects the
`ffff3026` override:

```text
bounded = min(ffff347c, max(ffff2a7a, ffff3478, ffff347a))
```

The function publishes the selected result to `ffff412a` and updates zero and
800-bound state bits in `ffff41fb`. The exact arithmetic establishes lower and
upper endpoint roles and a normalized `0..800` output domain, but it does not
identify the physical quantity represented by the endpoints.

## Stock-disabled centered correction surface

`FUN 0007b3f4` first tests `ROM8[000083c1].bit1`. The stock byte is `0x2c`, so
bit 1 is clear and the function directly copies `ffff1d26` to `ffff35d2`.
This bypasses the branch containing map `00016948`.

If the branch were enabled and its local mode bits admitted the map path, the
function would interpolate `00016948` by `ffff35ce` and `ffff11b6` on axes
`00018846` and `00018866`, then calculate:

```text
ffff35d0 = int16(interpolated_raw - 32768)
```

Every cell of `00016948` is `0x8000`, so the centered correction would be zero
at every coordinate. The branch then combines the correction with a bounded
term derived from `ffff35f0`, `ffff4138`, and denominator curve `00018dd6`
before publishing `ffff35d2`. In stock JK08A the lookup itself is unreachable,
and `ffff35d2` always enters its consumers from the direct `ffff1d26` path.
The map therefore has role `dead` in this exact ROM.

## Calibration safety boundary

The seven maps are structural evidence, not tuning controls:

- four surfaces execute but are excluded from terminal publication by a fixed
  stock selector;
- two live curves intentionally exercise their zero-span fallback;
- one centered correction surface is in a stock-disabled branch;
- the physical quantities and engineering units of all three components remain
  unresolved.

Editor visibility requires an independently established physical identity,
scale, and hardware validation plan. Constant stock values alone do not justify
exposing these maps for calibration changes.
