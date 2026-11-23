# JK08A dual-bank MAF range-performance monitor

## Scope and result

This specification records the exact JK08A path that computes the
shared RPM-dependent calibration at `0x1236A` and dispatches dual-bank MAF
range-performance diagnostics. The table is not a fuel-enrichment or ignition
calibration. It belongs exclusively to the paired P0101/P010B monitor.

The stock selector bypasses the comparison that consumes the table-derived
threshold. In the unmodified image, the table changes only a captured
diagnostic-event field. It does not alter fuel, air, throttle, ignition, or DTC
decision logic.

## Exact diagnostic dispatch

Periodic diagnostic dispatcher `FUN_0007BFC4` reaches coordinator
`FUN_00080E20`. The coordinator calls the two long-form bank monitors and
passes their Boolean returns to `FUN_00080F82`:

| Monitor | Aggregator argument | Runtime record | Descriptor | DTC |
|---|---:|---:|---:|---|
| `FUN_0008152A` | 4 | `0xBA` | `0x00019C18` | P0101 |
| `FUN_00081D74` | 7 | `0x07` | `0x000193B4` | P010B |

`FUN_00080F82` calls the exact diagnostic reporter at `0x0007D8B8` with
record `0xBA` when argument 4 is nonzero and with record `0x07` when argument
7 is nonzero. The ROM descriptors encode P0101 and P010B respectively. The
homologous VQ35HR factory manual defines both as MAF circuit range/performance
diagnostics, with separate high-signal/light-load and low-signal/heavy-load
conditions.

## Shared RPM factor

Both monitors perform the same lookup:

```text
rpm50 = uint8[0xFFFF11AE]
M = interp_u8_1d(
    table = 0x1236A,
    axis  = 0x1238A,
    input = rpm50
)
uint8[0xFFFF15BE] = M
```

The writer of `0xFFFF11AE` establishes an exact RPM/50 representation. Axis
`0x1238A` contains `8, 16, ..., 128`, so its points are exactly 400 through
6400 RPM. The table contains sixteen raw bytes:

```text
74, 99, 99, 97, 115, 116, 110, 111,
110, 113, 117, 123, 125, 123, 125, 124
```

The raw table scale is not independently established. The lookup result is a
dimensionless factor inside a multi-stage integer composition, not a direct
airflow or voltage value.

## Composite threshold path

Let:

```text
M = lookup(0x1236A, 0x1238A, uint8[0xFFFF11AE])
A = lookup_u8_1d8(0x12AC2, uint8[0xFFFF10F5])
B = lookup_u8_1d8(0x12868, high8(uint16[0xFFFF517C]))
C = min(255, floor(M*A*B / 16384))
G = floor(uint8[0xFFFF1733] * C / 256)
W0 = uint16[0xFFFF2A8C]
W1 = uint16[0xFFFF2A8E]
```

The first bank path selects `W0`; the second selects `W1`:

```text
if W0 == 0 and W1 == 0:
    R0 = R1 = 255
else:
    R0 = min(255, floor(W0*G / (W0+W1)))
    R1 = min(255, floor(W1*G / (W0+W1)))

Q0 = floor(128*R0 / 256)
Q1 = floor(128*R1 / 256)
```

The stock byte at `0x82BA` is 128. The two monitors write `Q0` and `Q1` to
`0xFFFF12EB` and `0xFFFF12EC`. Bank-indexed model builder `FUN_00082604`
independently writes comparison bytes to `0xFFFF15BC` and `0xFFFF15BD`.

When `ROM8[0x8D92].bit5` is clear, each monitor can use the comparison
`model_byte < Qn` as one of its fault candidates. Increasing `0x1236A` can
therefore increase `Qn` and make that candidate easier to satisfy, subject to
the other factors, saturation, and monitor gates.

## Stock selector and terminal effect

Stock `ROM8[0x8D92]` is `0x7A`, so bit 5 is set. Both monitors take an
independent direct-condition branch and never execute the `model_byte < Qn`
comparison. The complete RAM census found no other decision consumer:

- `0xFFFF12EB` is read only by the bypassed comparison at `0x00081942` and by
  event-snapshot copy `0x00081C62`;
- `0xFFFF12EC` is read only by the mirrored comparison at `0x0008216A` and by
  event-snapshot copy `0x000824B4`;
- `0xFFFF15BE` and the composition scratch bytes are local to the two monitor
  functions;
- the event snapshot stores model bytes at `0xFFFF4564/0xFFFF4565` and the
  table-derived values at `0xFFFF4566/0xFFFF4567`.

Consequently, editing `0x1236A`, `0x12AC2`, or `0x12868` in an otherwise stock
JK08A image can change captured monitor context but cannot change P0101/P010B
fault decisions. Clearing `0x8D92.bit5` or modifying executable control flow
would activate a different semantic regime and requires separate validation.

## Definition boundary

`0x1236A` remains in the canonical ledger with code confidence and a raw
diagnostic-factor role. It is hidden from RomRaider and TunerPro because:

- it has no fuel or tuning-output consumer;
- its active comparison is bypassed in stock JK08A;
- its stock terminal effect is limited to a diagnostic-event snapshot;
- exposing it as a tunable enrichment map would imply a false engine-control
  effect.

Hardware validation can observe `0xFFFF15BC/0xFFFF15BD`,
`0xFFFF12EB/0xFFFF12EC`, and the event snapshot around a controlled P0101 or
P010B confirmation procedure. It is not required to establish the stock
control-flow result above.
