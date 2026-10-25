# JK08A delegated request publication

`00079DD8` calls `000797D0`, returns to `00079DDE`, and jumps to
`00079030`. The jump's `00079DE2` delay slot restores the original PR.
`000797D0` calls complete `00079358` and `000793D2`, then branches to
complete `00079538` while restoring its caller PR in `000797DC`.
The descriptor binds 1132 stock instructions, 2264 instruction bytes,
17 contiguous spans, and 14 complete source bodies.

The first stages clamp `FFFF186B` between the byte sample `FFFF1864` and
its saturating sample+10 limit, calculate an optional integer correction,
and perform four real `000259D0` hysteresis calls. The complete `00079538`
state machine preserves disable, reset, latch, lower-knot table selection,
counter saturation, threshold comparison, division, and flag publication.
The two four-by-four byte grids are physical input spans. This binding
does not publish native table geometry or engineering units.

The final stage uses signed word arithmetic without declaring the datum's
native signedness. It derives an upper candidate from the duplicated
`FFFF19C2` selection and a lower candidate from `FFFF2438`, with optional
nonpositive offset `FFFF34CA`. `R7` retains the independent `FFFF34BA`
cap. The selected lower candidate also includes `FFFF34B4`. Transmission
bounds `FFFF3484` and `FFFF3480`, followed by lower `FFFF413A` and upper
`FFFF4138`, produce `R13`. The actual word publication is:

```text
ROM8[000083C1].bit0 set:   FFFF19C6 = low16(R13)
ROM8[000083C1].bit0 clear: FFFF19C6 = low16(min(FFFF34BA, max(R13, FFFF349A)))
```

`000791A8` stores R13 and `000791B2` stores R7. The selected store has an
independent live-register and ordered physical operand obligation. The
`FFFF415E` and `FFFF4160` publications apply the upper bound before the
lower bound; reversed limits retain that explicit instruction order.

The source descriptor binds 81 literal pools, 21 four-byte RAM pointer
aliases, and 94 calibration spans. Only declared pointer data changes for
the simulator's `01000000` RAM window. Instruction bytes and signed
16-bit literals remain stock. The actual `00026A84` byte-curve entry is
contained in complete `00026A60`; its preceding shift instructions receive
no reachability credit. The word interpolation arm, impossible signed
division branches, and unsigned word negative-adjustment arms remain
explicitly excluded under their exact caller premises.

The input-only matrix carries complete 80-byte CPU/SR contexts, full
64 KiB RAM, raw calibration bytes, and prior publications. The unchanged
572-byte ordinary observer records complete 192-byte natural frames,
external ABI, CPU, RAM, calibration, and instruction/literal snapshots.
One invocation executes the complete dispatcher and all actual helpers.
Separate complete stage equations predict every RAM publication. Physical
site/address/width/register checks and real post-delay call/return states
remain independent obligations. Eleven held-other alternatives require
an actual changed computed `FFFF19C6` word while every other complete
input remains fixed. An echoed input, matching final number, or write set
alone supplies no owning support.

The complete existing division, byte-curve, counter-threshold, and
register-helper originals remain required from the same primary process.
Their independent source, numerical, physical, causal, native, and TEST
obligations are retained. Source preparation supplies no execution receipt.

The owning declaration retains the exact writer relation from
`throttle_request_bounded/ram` to `request_boundary_dispatch/fn` and appends
one identity witness. Native width16, absent signedness, all owner facts,
the three complete natural function documents, and every ledger/evidence/
TEST position remain fixed. The separate `000730FC` reader remains outside
this append. Physical scale, scheduler cadence, natural scheduling,
actuator behavior, bank identity, and hardware eligibility are separate.
