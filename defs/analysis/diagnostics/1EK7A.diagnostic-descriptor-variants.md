# 1EK7A diagnostic descriptor variants

The DTC decoder finds JK08A editor records whose packed DTC exists in
1EK7A without a unique byte-identical descriptor. The `dtc_projection.py`
check enumerates the reviewed source indices and all target indices with the
same packed code. The target record and attribute addresses come from the
stock descriptor and attribute-pointer tables.

```bash
uv run python tools/mapkit/dtc_projection.py 1EK7A --check
```

For each source record, one target candidate matches the group, sub-index,
monitor class, and packed code. Only descriptor byte 8 differs in that
candidate. The 1EK7A monitors pass every matching index to the
stock diagnostic dispatcher at `0x000C7990`. A repeated packed code can also
identify a different record. Each target index in the matrix has its own
attribute cell with stock value `0x00A0`.

| DTC | JK08A index | 1EK7A matching index | Other 1EK7A indices | Byte 8, JK08A to 1EK7A | Call to `0x000C7990` |
| --- | ---: | ---: | --- | --- | --- |
| P0420 | 17 | 17 | | `10` to `14` | `0x00107EF6`, `0x001091BC` |
| P0430 | 18 | 18 | | `10` to `14` | `0x00107FBE`, `0x0010910C` |
| P0443 | 46 | 48 | 24 | `00` to `10` | `0x00114602` |
| P0455 | 48 | 50 | | `10` to `14` | `0x0011D402` |
| P0139 | 167 | 162 | 319 | `10` to `14` | `0x000DA2D2` |
| P0159 | 168 | 163 | 320 | `10` to `14` | `0x000DA2E2` |
| P0138 | 169 | 164 | 168 | `10` to `14` | `0x000DA5F6` |
| P0158 | 170 | 165 | 169 | `10` to `14` | `0x000DA60C` |
| P0137 | 171 | 166 | | `10` to `14` | `0x000DA446` |
| P0157 | 172 | 167 | | `10` to `14` | `0x000DA4B6` |
| P0441 | 214 | 203 | | `00` to `04` | `0x00114738` |
| P0456 | 216 | 205 | 218 | `10` to `14` | `0x0011D862` |
| P0442 | 218 | 207 | | `10` to `14` | `0x0011D166` |

The alternate P0443 monitor passes index 24 at `0x00116382`. The rear O2
secondary path reports index 168 at `0x000DA920` for bank 1. The coordinator
inlines the bank-2 path and reports index 169 at `0x000D8640`. The matching
rear O2 records use a separate dispatcher at `0x000DA182`.

The group-87 monitor at `0x000DBBDA` passes indices 319 and 320 at
`0x000DC366` and `0x000DC354`. The stock group byte `0x00` leaves both bank
enables clear. The [rear oxygen specification](SH7059.rear-o2.md) traces the
per-bank gates. The queue insertion routine `0x00104AF8` compares packed
codes when it checks for a duplicate, so the existing queue index matters
when two records share the same code.

The alternate P0456 monitor passes index 218 at `0x00120646`. The first
delegation from `0x000C7990` to `0x000DEB60` retains index 218 on the stock
image because bit 6 of `ROM8[0x88F6]` is clear (`0x34`). With that configuration
bit set, the dispatcher can instead delegate index 50, 205, or 207 according
to the current runtime record flags.

## Effects of the existing editor operation

The existing DTC control clears the entire twelve-byte descriptor and its
attribute word. The following effects follow directly from the 1EK7A code
when the corresponding reader reaches a changed record:

- `0x00104C46` reads descriptor byte 8 and `0x00104C48` tests bit 2. Clearing
  a stock `0x04` or `0x14` lets the record pass this gate in `0x00104B9E`.
  Subject to the other runtime gates, that routine sets queue flags `0x08`
  and `0x04`. A later pass calls `0x00104978` for entries with both flags.
  That routine removes the indexed queue entry and shifts the following
  entries down.
- `0x000C72BA` tests descriptor byte 8 with mask `0xD0` while walking the
  first 51 runtime records, including both P0443 indices. Clearing bit 4
  selects a different runtime-state update branch. Other record walks in
  `0x000C723C` and `0x000C6AC6` also consume that mask.
- `0x00040384` and `0x0004142C` gate packed-code publication on attribute
  bit 7 and the corresponding runtime state. Clearing the attribute removes
  permission to publish via those paths. The delegated routine at
  `0x000DEB60` sets runtime record byte 1 bit 7 before reading the attribute.
- `0x000DECE2` tests attribute bit 5 during a scan of the complete pointer
  table. The scan clears runtime record byte 1 bit 7 only for attributes
  with that bit set. Changing `0x00A0` to `0x0000` skips this clearing path.

The existing operation changes stock reader behavior for every matching
index in the matrix. The 1EK7A editor leaves these matching indices and
their attributes at stock. It admits only unique exact descriptors.
