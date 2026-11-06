# Exact-family runtime ownership and growth reserves

`jk08a-runtime-reservations.toml` is the canonical cross-runtime ownership
ledger for Map Switching, Rolling Launch, and custom CAN telemetry in the
exact JK00A/JK03A/JK03B/JK08A family. The corresponding validator is
`jk08a_runtime_reservations.py`; the unified ROM builder loads it before
composing an image.

Each runtime layout remains authoritative for its active code, hooks, tables,
configuration, and RAM records. The shared ledger adds two guarantees that an
individual layout cannot provide:

- active RAM records from different runtimes do not overlap;
- every runtime has an exclusive, erased ROM and RAM reserve for future schema
  revisions.

## Current allocation

| Runtime | Active RAM | Future RAM | Future ROM |
| --- | ---: | ---: | ---: |
| Map Switching | `0xFFFF5D00..0xFFFF5D3C` | `0xFFFF6000..0xFFFF6100` | `0x000D6800..0x000D7000` |
| Rolling Launch | `0xFFFF5D40..0xFFFF5D6C`, `0xFFFF6100..0xFFFF6120` | `0xFFFF6120..0xFFFF6160`, `0xFFFF6160..0xFFFF6200` | `0x000D67F0..0x000D6800` |
| CAN telemetry | `0xFFFF5E00..0xFFFF5F90` | `0xFFFF5F90..0xFFFF6000` | `0x000D5000..0x000D6000` |

A runtime may own several disjoint spans. The Rolling Launch state record and
its extension are active; the first Rolling Launch future RAM span is the
scratch budget of the spark-cut veto delivery and stays outside the active
write set. Unassigned gaps remain unowned and are not silently available to a
patch. `patches/jk08a_runtime_reservations.py` prints the active RAM, future
RAM, and future ROM totals.

CAN telemetry schema 2 uses the complete active RAM allocation. Its
two 88-byte frame banks end at `0xFFFF5ED0`; the remaining active bytes contain
state, event, and cleared reserve records and, from `0xFFFF5F00`, the dynamic
page configuration. The generated 492-byte pointer table
fits `0x000D4C00..0x000D4E00`, and the 16-byte configuration remains at
`0x000D4E00`. The adjacent future ROM and RAM ranges remain erased and are not
part of the schema 2 write set.

The original Map Switching `claimed_rom` interval is a compatibility envelope
used by its historical layout checks. It includes gaps and overlaps later
layer addresses, so it is not an exclusive ownership claim. Cross-runtime
validation uses the exact composition write sets instead. Every future ROM
reserve must be inside an audited free region, outside all exact write sets and
checksum fields, and erased in the complete current composition.

Changing a reserve requires updating the ledger and the owning runtime layout
when that layout exposes the same boundary. Consuming reserved bytes requires
a new schema version, a narrowed active write-set update, and the applicable
static and executable verification gates.
