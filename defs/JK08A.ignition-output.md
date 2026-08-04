# JK08A ignition output and late-retard contract

## Scope and result

This document describes the exact stock JK08A software path from the final
signed timing coordinate to the SH7058 Advanced Pulse Controller (APC). It also
defines the static acceptance boundary for a late retard-only override used by
Rolling RPM Hold.

The normal-mode software contract supports a target command range of
`110..117`. In the normal diagnostic coordinate this range represents
`0..-7 deg BTDC`. A late override is retard-only when it selects
`max(stock_command, target_command)`. Support is conditional on preserving the
stock command while `0xFFFF24C9.bit6` is set, because that bit selects a
P0335-driven APC fallback scheduler whose physical angle behavior is not part
of the normal contract.

Static analysis proves command construction, ordering, byte ranges, both APC
compare paths, and diagnostic publication. It does not prove the physical spark
edge, external driver polarity, or actual crank angle. Those properties require
a timing light and a controlled bench or engine test.

## Final command and diagnostic coordinate

Engine-event dispatcher `0x0004E162` executes this fixed order:

```text
0x0004E112 -> 0x0004E0C2 -> 0x0004D99C -> 0x0004DBE8
             -> 0x0004DF82 -> 0x0004E080
```

`0x0004DBE8` performs the final stock timing arbitration and writes signed byte
`0xFFFF11D4`. Its normal map/state clamp uses stock ROM bounds
`ROM8[0x821E] = 50` and `ROM8[0x8221] = 0xF9`, where `0xF9` is `-7` as `int8`.
Additional diagnostic and fallback modes can use other boundaries, so this is
the normal-mode envelope rather than a universal final range.

On the normal path `0x0004DF82` computes:

```text
command = uint8(110 - uint8(final_signed_coordinate))
```

Stock `ROM8[0x83D5]` supplies `110`. The function writes the command to
`0xFFFF2022` and calls primary scheduler `0x0002A892`. Exact JK08A UDS table
entries for DIDs `0x1107`, `0x1108`, `0x1109`, and `0x110A` all return this same
byte.

The homologous P32M Nissan diagnostic profile defines DID `0x110A` as
`IGN TIMING4` with `deg = 110 - raw`. This exactly inverts the normal firmware
transform over the admitted range:

| Command | Normal diagnostic coordinate |
| ---: | ---: |
| `110` | `0 deg BTDC` |
| `115` | `-5 deg BTDC` |
| `117` | `-7 deg BTDC` |

The VQ35HR factory ESM identifies `IGN TIMING` as a value computed by the ECM.
Its active test directs CONSULT-III to retard ignition while a timing light is
connected. The diagnostic byte is therefore a commanded/computed value, not a
measurement of physical spark angle.

## Late override point

The call target literal at `0x0004E198` belongs to the final call in
`0x0004DF82`. Replacing only that consumer places an adapter after all stock
final-angle arbitration and before the primary APC scheduler. The required
adapter sequence is:

```text
stock command from r4
  -> validate runtime mode and configuration
  -> require 0xFFFF24C9.bit6 == 0
  -> validate target in 110..117
  -> effective = max(stock, target)
  -> write effective to 0xFFFF2022
  -> tail-call 0x0002A892 with effective in r4
```

Every invalid, inactive, or fallback-mode path must tail-call `0x0002A892`
with the unchanged stock command. Writing the effective command to
`0xFFFF2022` is necessary because the following `0x0004E080` call reads that
byte to construct the secondary command. It also makes DIDs `0x1107..0x110A`
report the effective command.

For normal-mode commands, selecting the larger byte cannot advance the
software timing coordinate because the diagnostic transform has slope `-1`.
Targets `110..117` stay inside the stock normal lower bound. Commands above
`117`, which would represent values below `-7 deg BTDC` under the same formula,
are outside this static acceptance boundary.

## Primary APC scheduler

Helper `0x00028E7C` splits an unsigned byte exactly into:

```text
quotient = floor(command / 10)
remainder = command - 10 * quotient
```

Normal-mode scheduler `0x0002A892` stores the decade and remainder at
`0xFFFF1558` and `0xFFFF155A`, carries complete decades through
`0x00028DC8` and continuation handler `0x0002AB24`, and calculates the current
fractional compare offset as:

```text
0xFFFF16C2 = min(65535, floor(0xFFFF22BC * remainder / 10))
```

It programs `GR11A` at `0xFFFFF5C2`, clears the applicable `TSR11` flag, and
enables the current-cylinder low-byte `POPCR` action. Target commands
`110..117` share one command decade and remain below the fallback-only clamp at
`199`.

`0xFFFF24C9.bit6` selects a different primary and secondary scheduling mode.
The bit is the periodic snapshot of `0xFFFF24CF.bit6`. Function `0x00099A48`
sets it from the active runtime status of the P0335 record pair when the P0340
and P0345 record pairs do not select their companion modes. Because the
alternate APC path is a position-sensor diagnostic fallback, the late override
must pass the stock command through whenever the snapshot bit is set.

## Secondary compare and overflow proof

The secondary command is produced after the primary call:

```text
secondary_command = effective_primary_command + reset_offset
```

The complete stock range proof is:

1. `0x0004C1E4` bounds byte `0xFFFF1874` by
   `ROM8[0x8B88] = 6` and `ROM8[0x8B87] = 114`.
2. It writes `0xFFFF2406 = min(0xFFFF1874, 0xFFFF1875)`, or forces `24` under
   the associated diagnostic state. Therefore `0xFFFF2406` is in `0..114`.
3. Periodic dispatcher `0x00020DFE` copies `0x8C` bytes from
   `0xFFFF23BC..0xFFFF2447` to `0xFFFF2330..0xFFFF23BB`. The matching offset
   proves `0xFFFF2406 -> 0xFFFF237A`.
4. `0x0004E080` starts from `120 - uint8(0xFFFF237A)`. Its optional subtraction
   uses stock `ROM8[0x8649] = 0`, so stock `reset_offset` is in `6..120` in
   either branch.
5. For an applied target of at most `117`, the largest newly constructed
   secondary command is `117 + 120 = 237`, below the byte boundary `256`.
   When the stock primary command is already above the target, the override
   leaves it unchanged and introduces no new arithmetic case.

`0x0004E080` stores the offset at `0xFFFF2230` and calls `0x0002ACBA` with the
sum. The secondary scheduler uses the same divide-by-ten representation and
programs `GR11B` at `0xFFFFF5C4`. The accepted override range therefore reaches
both stock compare schedulers without a newly introduced `uint8` wrap.

The SH7058 hardware manual proves that the selected low `POPCR` bit drives the
PULS output high on a `GR11A` compare and the selected high `POPCR` bit drives
it low on a `GR11B` compare. It does not identify the external ignition-driver
polarity or which physical transition is the spark event on JK08A.

## Acceptance boundary

Static support for Rolling RPM Hold retard requires all of these conditions:

- the adapter is placed at the final `0x0004E198` consumer;
- inactive and invalid paths preserve the stock command;
- `0xFFFF24C9.bit6 != 0` forces stock pass-through;
- each target is in `110..117`;
- the effective command is `max(stock, target)`;
- the effective command is written to `0xFFFF2022` before `0x0002A892`;
- commands above `117` remain rejected until separate hardware validation.

Hardware enablement remains blocked until CONSULT3P command observation and a
timing-light measurement establish command direction, actual crank angle, and
safe combustion behavior on the target engine.
