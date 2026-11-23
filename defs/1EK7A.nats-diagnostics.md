# 1EK7A stock NATS diagnostics

This review applies to the registered stock `11EK7A-20261122-stock.bin`.
The catalog and the paths below are qualified by the stock ROM code.

## Diagnostic state

The descriptor table assigns P1610 through P1615 to indices 42 through 47
in group `0x0D`. Each descriptor points to a stock attribute of `0x0000`.
The exact records and their attribute pointers come from the
[ROM diagnostic catalog](../refs/diagnostics/rom-dtc/rom_dtc_descriptors.csv).

The stock function table at `0x000C4BDC` references reader `0x00138022`.
It qualifies each latched result with the diagnostic monitor mask and
dispatches the selected index to the generic DTC writer at `0x000C7990`.
The stock diagnostic mask enables all six positions. A parallel routine at
`0x00137F88` contains the same tests and dispatch indices. Its task-table
reference remains unresolved.

| Code | Index | Dispatch site |
| --- | ---: | ---: |
| P1610 | 42 | `0x001380B2` |
| P1611 | 43 | `0x00138098` |
| P1612 | 44 | `0x00138080` |
| P1613 | 45 | `0x00138068` |
| P1614 | 46 | `0x00138050` |
| P1615 | 47 | `0x00138038` |

The P1613 report predicate and descriptor index are code facts. Its upstream
result assertion and factory display label remain unresolved.

The generic writer delegates at `0x000C79FC` to `0x000DEB60`, which sets
the internal record status at `0x000DEBA2`. The writer also updates the
selected record's diagnostic status byte in `0x000C7A42..0x000C7A44`.

## Readout

The Mode `0x03` and `0x07` OBD publishers at `0x00040384` and `0x0004142C`
require attribute bit 7 in addition to their runtime-state predicates. The
attribute tests at `0x000403BC`, `0x00040442`, and `0x000414B6` exclude these
stock records from those lists even when an internal condition reaches the
writer.

The vendor diagnostic response paths at `0x0003BF98` and `0x0003C57C`
select a marked internal record at `0x0003C3F8` and `0x0003C7B8`. They read
the selected packed code at `0x0003C418` and `0x0003C7D6` and place it in
the response buffer. In this branch the configured response source selects
the first record whose runtime status is marked.

## Stock fuel authorization

The startup RAM clear in `0x0002EAE4` initializes the working state to zero.
Application vector slot `0x000201E4` points to the periodic ATU-II handler at
`0x0002040C`. Its tenth-phase task loop at `0x00020B14` calls the entries in
the table beginning at `0x00022018`. Slot `0x0002210C` supplies the stock
authorization task at `0x00137B56`.

That task calls `0x00136E8C` and `0x00137508` to process the runtime outcomes.
The stock image selects the outcome branch. The task updates the working
fuel-inhibit state using the exchange outcome and a separate phase status
of the requested diagnostic ROM self-test. The initializer at `0x001542DC`
clears that status. Routine `0x00154458` sets it after the scan and before
the final comparison outcomes. See the
[ROM self-test description](../patches/rom-selftest-checksum.md).

The periodic snapshot at `0x00021274` copies the resulting inhibit state
before dispatching the engine task list. Slot `0x000221D8` of that list
calls the fuel-inhibit coordinator at `0x0007BE28`, which uses an asserted
inhibit to request a mask for all six cylinders. The injection scheduler at
`0x00083328` also checks this state before scheduling its normal events.

The separate routine at `0x00137A04` has a similar state update. The stock
periodic dispatch establishes the writer through `0x00137B56`. The
reachability of the separate routine remains unresolved.

An ignition-side consumer at `0x0010A5BC` reads the NATS state as part of
P0350 evaluation. The reviewed APC output paths use a separate hardware
readiness input. A direct dependency of spark or starter actuation on the
NATS state remains unestablished by these readers.

## Editor coverage

The exact-match DTC projection carries the P1610 diagnostic descriptor
control. Its scope is the diagnostic record and its publication. The
firmware's fuel-inhibit state belongs to the stock runtime authorization
path.
