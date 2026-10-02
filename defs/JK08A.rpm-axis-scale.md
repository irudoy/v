# JK08A candidate nominal RPM axis scale

## Scope and evidence level

The byte axes `00012858`, `000120ae`, `00011b6b`, and `0001264a` of
layout `7mfk` have the candidate scale `x*50 RPM`. Their scale owner is
`defs/JK08A.axes.csv`; the editor grid inverse is `x/50`. This inverse is
not an exact inverse of physical RPM after the firmware quantizes the value.

The placement and conversion fixture executes each of these independently
SHA-locked stock images. A common layout name is not the transfer proof.
The exact expected instruction, literal, and axis-byte spans are bound and
executed separately for every image by
`tools/mapkit/tests/test_rpm_axis_scale.py`.

| Image | SHA-256 |
| --- | --- |
| JK00A | `ed0941de8435d9c61ac093a293757b93ad81bd413270a348c44a8fb6b78b6118` |
| JK03A | `f78929547c08dc5ecde256fb3a6f6f3ef6daa9010e1531b3eac99fd9509225b4` |
| JK03B | `a9aa7a337375b7c9419b0970c32674e98f12ea4215c079898190c5c771a96f1a` |
| JK08A | `ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23` |

The physical association remains candidate. CONSULT-III Plus or bench data
must check the hardware correspondence. This proof does not establish the
measuring producer of `U`, a timing-clock frequency, a crank-event angle, or
an independently measured instantaneous engine speed.

## Independent physical decoding source

The source is the community table
[TihanPelser/370Z-CAN-Logger, candata/standard_pids.csv, line 14](https://github.com/TihanPelser/370Z-CAN-Logger/blob/2decbc957523ee46dd39b3e3a7594e23ad7eee97/candata/standard_pids.csv#L14),
pinned at revision `2decbc957523ee46dd39b3e3a7594e23ad7eee97`.

- Dataset: `370z-can-logger-2025-07-05`.
- Document: `370z-can-logger-2025-07-05:candata-standard-pids-csv`.
- Fragment: `370z-can-logger-2025-07-05:candata-standard-pids-csv:l0014-l0014:source-row-standard-pids`.
- Request: service `01`, PID `0C`; two response data bytes, `A` then `B`.
- Quantity and unit: Engine RPM, `rpm`.
- Formula: `((A*256)+B)/4`.
- Applicability: `homologous_community`; source tier: `community`.

The importer categorizes this row as `standard_definition`. That category is
not original SAE, factory-manual, or vendor evidence, and is not a hardware
verification status. The fixture checks the retained source fragment,
revision, request context, quantity, width, unit, and formula against literal
expectations; the current corpus cannot supply refreshed expected values.

## Bounded conversion chain

Let `U = u16(ffff1196)` and consider one common producer value.

1. `0003850a/0c` loads `U`. `00038510..16` zero-extends and shifts it by
   three; `0003851c` writes `E8 = U >> 3` to `ffff11e8`.
2. `00038562/64` shifts the preserved value by another three.
   The call delay slot `0003856c` writes `W = U >> 6` to `ffff11f4`.
3. `00038572..7e` reads `E8`, zero-extends it, and shifts it by five.
   `00038580..84` caps the byte result at 255; the call delay slot
   `0003858a` writes `Q = min(255, E8 >> 5) = U >> 8` to `ffff11e6`.
   Production `U16` implies `E8 <= 8191`, `W <= 1023`, and `Q <= 255`.
4. The scheduler segment `00020f5a..6e` loads source `ffff11d4`,
   destination `ffff119c`, and a byte count of `56` (`0x38`). The real
   `000220f8` dispatch selects the fixed ladder entry `0002211e` through
   `00022190`. Load `0002213e` reads the longword at `ffff11e4` and store
   `00022144` writes it at `ffff11ac`. Thus the contained `ffff11e6` byte
   reaches `ffff11ae` without a numeric conversion.
5. The PID branch predicate at `00035d04` is `R0 == 0x0c`.
   `00035d0c` reads the unsigned word at `ffff11f4`; `00035d10/12`
   multiplies it by 50. `00035d1a..20` caps the result at 65535.
   `00035d2a/2c` and `00035d32/34` call the real byte writer `00037acc`
   in high-byte-first order; its byte store is `00037ade`.

The independent PID decoder therefore gives `RPM_PID = 12.5*W` in this
producer domain. Since `Q = floor(W/4)`, the nominal byte coordinate is
`50*Q RPM`; its residual relative to this PID value is `0`, `12.5`, `25`,
or `37.5 RPM`. The residual comparison requires the same producer value:
independently sampled diagnostics and a scheduler snapshot can represent
different times. The expression `x/50` reconstructs only the nominal editor
grid, not discarded sub-byte information or arbitrary physical RPM.

The publisher tests also seed `W = 1310` and `W = 1311` independently to
exercise its saturation boundary: responses `ffdc` and `ffff`. These operands
are outside the production domain `W <= 1023` of `U16`. Independently seeded
`E8 > 8191` exercises the byte cap without claiming a reachable production
speed.

## Separate axis placements

| Axis | Stock axis literal | Byte source | Call | Wrapper |
| --- | --- | --- | --- | --- |
| `00012858` | `000bf174` | `000befd2`, `ffff11ae` | `000befd8/da` | `00026140` |
| `000120ae` | `000bf184` | `000beff2`, `ffff11ae` | `000beff4/f6` | `00026140` |
| `00011b6b` | `0008336c` | `000832b2`, `ffff11ae` | `000832b6/b8` | `00026320` |
| `0001264a` | `00083a44` | `0008397e`, `ffff11ae` | `00083988/8a` | `000264a0` |

Each placement executes its own literal and byte-input path, then the first
wrapper call into `00026944`. The kernel's byte read at `00026946` compares
axis counts and input counts in the same coordinate system. Calibration-byte
equality, axis geometry, and plausible RPM breakpoints do not supply the
physical multiplier.

## Executable boundary

The producer fixture executes three conversion segments. Its intervening
filter calculations and producer-helper calls/returns are outside the proof;
the conversion operands bridge the segments explicitly. The copier and byte
writer execute their real narrow call/return paths. Axis placement stops after
the first byte-axis sample read: interpolation-wrapper helper returns,
fractional interpolation, full ECU functions, protocol readiness and response
headers are outside this placement/conversion proof. No stock-function stubs
or simulator-only instruction relocations are used.

The negative fixtures reject changed source and axis literals, registers,
widths, call delay operands, shifts, copy count and placement, publication
factor, saturation, byte order, and source formula/context. Instruction mutants
exist only in memory and are not patch images. The compiled-owner gate checks
that the four typed test items support `scale`, retain `candidate`, and resolve
to the actual top-level test functions through the knowledge-base AST check.
