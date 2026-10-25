# JK08A conditional remaining RPM-inhibit readers

The `rpm_remaining_inhibit_paths` component binds five exact reader relations
owned by `fuel_output_inhibit_coordinator/fn` at `0004ED88`.
The owning batch in `JK08A.rpm-inhibit-access-claims.toml` contains fourteen
relations. Its nine `rpm_inhibit_paths` records retain their complete original
and proposed native documents, reference identities, evidence and positions.
The separate component appends one evidence item per existing reader relation.
Every other relation, native type, layout, ledger and TEST origin stays exact.

| Existing owner | Native address | Exact byte-read sites | Retained semantic type |
|---|---|---|---|
| `gifted-jackrabbit/tbl` | `000085D9` | `0004F422` | width and signedness unset |
| `ochre-jacamar/ram` | `FFFF247C` | `0004F9AE`, `0004F9B2`, `0004F9B4` | width and signedness unset |
| `blue-oyster/ram` | `FFFF247F` | `0004F330`, `0004F3A6`, `0004F43C` | width and signedness unset |
| `jovial-buzzard/ram` | `FFFF249C` | `00050A66`, `00050AEC`, `00050AF0`, `00050AF8` | width 8, signedness unset |
| `heavenly-whippet/ram` | `FFFF41F2` | `0004F4C0`, `0004F52C`, `0004F554`, `0004F600`, `0004F646` | width and signedness unset |

## Separate caller phases

`JK08A.rpm-remaining-inhibit.toml` declares three bounded caller entries:

| Entry | Stock call and delay | Natural return | Separate observing return |
|---|---|---|---|
| `0004EDC6` | BSR `0004F324`, OR R0,R14; BSR `0004F494`, OR R0,R14 | `0004F44C` to `0004EDCA`, `0004F65E` to `0004EDCE` | `0004EDCE` |
| `0004EDE4` | BSR `0004F958`, NOP; EXTU.B R0,R2 at `0004EDE8` | `0004F9C0` to `0004EDE8` | `0004EDEA` |
| `0004EE00` | MOV.L target `00050A60`; JSR R3, OR R0,R14 | `00050B02` to `0004EE06` | `0004EE06` |

The incoming R0 is zero and incoming R14 is `3E5F6A00`. Other complete register
and special-register inputs have explicit context variants. The incoming GBR
is `01009F34`. The first phase returns the thermal Boolean in R0 and merges
the stationary Boolean into R14 in the second call's real delay slot. The
second phase exposes the sustained Boolean in R0/R2. The third phase exposes
the CAN ceiling Boolean in R0; its call delay uses the incoming R0.
No result is retroactively inserted into an earlier delay slot.

`stock_jk08a_rpm_remaining_inhibit.s` independently reconstructs the exact
caller, leaf and byte16 helper spans and their data. The stationary helper is
the real `00026388` entry with natural tail jumps through `00026A84` and
`00026740`. The call at `0004F398` passes the actual table at `000124D2` and
the byte coordinate after its EXTU.B delay. The upper-byte RTS at `00026396`
or the linear-kernel RTS at `00026758`/`0002676A` returns to `0004F39C`.
Their delay slots supply the real returned R0.

The twenty-two long RAM pointer aliases change existing high-RAM literals
into the established `01000000..01010000` simulator RAM domain. Instructions
remain exact stock bytes. The SP+24/R7 observing return is independently
assembled at each separate boundary. It restores PR and returns outside
every tested instruction and data span. This fixture is separate from the
old RPM fixture: old observing returns overlap these stock caller entries.
Neither fixture's observing bytes replace instructions under test in that
fixture.

## Conditional diagnostic premise

The thermal consumer requires `FFFF4184 = C0` and unsigned `FFFF571E >= 40`.
The first condition fixes the status branches and holds R10 at zero. The
second condition, or a clear diagnostic flag at `FFFF5720.bit4`, holds R9 at
zero. The consumer clears `FFFF41F2.bit4`; the dispatch at `0004F5F6` to
`0007D8B8` is excluded under these exact premises. No stock function is
stubbed. This is conditional consumer evidence, with no diagnostic-producer
proof, universal no-call claim or complete coordinator admission.

When ROM `000186C9.bit0` is clear, the leaf returns the incoming
`FFFF41F2.bit5`. When enabled, the exact quiet status path reloads its local
diagnostic counters, handles `FFFF41F2.bit3` and `FFFF5720.bit4`, updates the
temperature and RPM hysteresis bits, and derives bit5. The physical consumer
binds every feasible read and store. Excluded diagnostic blocks cannot appear
in the instruction-state result or call list.

## Independent numerical and physical obligations

The stationary scalar equation checks the three entry gates, readiness timer,
byte16 coordinate `clamp(trunc((uint16 RPM - 160)/2),0,255)`, selected curve
bytes, interpolation fraction and unsigned accumulator saturation. Readiness
uses the unsigned threshold at `0000911C` and the qualifier or bypass bit.
The cut and restore cells at `000085D9` and `000085DA` have distinct latch
roles. Their byte access does not establish a missing semantic type or scale.

The sustained equation saturates the calibration product to 65535, compares
the complete exposure word and applies separate cut, hold and restore
branches. The CAN equation distinguishes disabled configuration, invalid
requests, status gates, request floor, strict RPM comparison and nonwrapping
hysteresis. Unrelated latch bits and every other RAM byte remain exact.

The input source supplies 35 controlled calibration bytes, including the
sixteen curve cells. A generated standard input driver uses the existing
80-byte context, 572-byte observer result and 192-byte before/after frames.
It records complete 64 KiB RAM, context, CPU, SP, continuation, ABI, frames,
SR and bound executable/data bytes. It contains no expected outputs.

Independent consumers require agreement between the instruction-state
equations, separate scalar equations and ordered physical ROM/RAM transfers.
Real calls include exact targets, post-delay registers, SP, PR and GBR;
natural leaf and helper returns include their delay-slot effects. All
42 conditional branch sites require both feasible outcomes. The nine
fixed-outcome sites retain their exact quiet-status or byte-entry premises.
Fixed-other alternatives must change the actual caller result for every
native root; copying the incoming flag into an observation is insufficient.

Complete producer, descriptor, independent consumer, generated driver,
refusal source and transitive source identities belong to the same complete
COPY primary. The ordinary writer admits only the exact joint owning batch
after that primary and all shared acceptance obligations pass. The component
provides no native geometry, units, scale, natural scheduling, whole
coordinator, diagnostic producer or hardware qualification.
