# JK08A tuning-observation coverage

## Scope

This specification defines the runtime observation set used to interpret JK08A
calibration behavior. The machine-readable authority is
`JK08A.tuning-signals.toml`; `tools/diagnostics/tuning_signal_coverage.py`
validates it against the exact service-0x22 publisher and custom CAN schema 2.

The catalog distinguishes:

1. exact runtime-source evidence;
2. service-0x22 availability;
3. fixed-rate or rotating custom-CAN coverage;
4. equivalent stock-CAN context;
5. quantities that still require firmware instrumentation or external
   measurement.

Service 0x22 is an address and semantic cross-check. Its request-response
transport is not the high-rate logging path.

## Custom CAN profile

The single `tuning` profile sends eleven DLC-8 frames per snapshot. Pages 0
through 8 refresh at the `97.65625 Hz` scheduler cadence with divisor 1. Pages
9 and 10 are transmitted at the same rate and rotate a shared five-value tag,
so each tagged field set refreshes at `19.53125 Hz`.

The fixed pages provide:

- engine speed, both MAF sensor words, combined airflow, base fuel schedule,
  and calculated load;
- final ignition coordinate, APC command, ignition state, knock state, and
  latched knock interval count and channel mask;
- all six calculated injection words, the end-of-injection angle word, and the
  final fuel-output inhibit mask;
- both front heated-oxygen-sensor bytes;
- both accelerator channels, primary throttle feedback, absolute throttle,
  bounded request, shared target, and both final channel targets;
- engine torque state;
- intake and exhaust CVTC targets plus both-bank actual intake and exhaust
  positions.

The rotating contexts provide:

- coolant, intake-air, fuel, and oil temperature sources;
- the upstream Q14 fuel multiplier, STFT, and LTFT;
- the bank 1 long-term trim learned and adjustment summands;
- intake CVTC solenoid duty commands and the live intake duty pair they
  latch under one tag, so both pairs come from the same scheduler pass, and
  high-resolution exhaust duty;
- atmospheric pressure and battery voltage;
- higher-resolution front A/F sensor words and both adjustment integrators;
- secondary throttle feedback for both banks;
- the minimum knock threshold margin of each of the six evaluator channels
  since the previous capture of its tag;
- two timing state bytes and the in-band transport identity and counters.

Stock CAN independently provides RPM, vehicle speed, selector position, ASCD
input, and dashboard state. The dashboard and MLVLG recorder retain those
values without consuming custom payload capacity.

## Closed control-loop coverage

Schema 2 carries the command and feedback sides needed for offline tuning
analysis:

| Control family | Command or target | Feedback or state |
| --- | --- | --- |
| electronic throttle | `FFFF19C6`, `FFFF19B2`, `FFFF28BC`, `FFFF28BE` | APP `FFFF269E/26A2`, primary TPS `FFFF2756/285C`, secondary TPS `FFFF275E/2864` |
| intake CVTC | common target `FFFF2326`, low- and high-resolution duty | actual B1/B2 `FFFF2442/2443` |
| exhaust CVTC | common target `FFFF2327`, high-resolution duty B1/B2 | actual B1/B2 `FFFF2324/2325` |
| fuel correction | Q14 factor, STFT, LTFT, adjustment B1/B2 | oxygen-sensor bytes and front A/F words |
| torque | bounded throttle request and target path | signed torque state `FFFF18CC` |

The airflow, coolant, intake-air, timing, vehicle-speed, and absolute-throttle
units are the ECU's own J1979 Mode 01 declarations, recorded in the
diagnostics note; they describe the firmware model, not a hardware measurement.
Code and ROM constants fix the remaining closed scales: MAF, pedal, and
throttle sensor voltage at `raw / 200 V`, Base Fuel Schedule at
`raw / 2048 ms`, the injection words at `raw / 100 ms`, CVTC targets and
positions at `raw * 0.5 - 64 degCA`, the intake duty command at
`raw * 39 / 100 percent`, exhaust duty at `raw * 100 / 1024 percent`, fuel and
oil temperature at `raw - 50 degC`, battery voltage at `raw * 0.08 V`, and the
end-of-injection angle at `raw * 2 - 590` degrees after intake TDC of the
injected cylinder. The
command pair `FFFF23B4/23B5` is the scheduler block-copy latch of live duty
pair `FFFF2440/2441`, so the command conversion applies to both pairs. Engine
torque state, atmospheric pressure, the front A/F words, and both adjustment states
keep candidate or unresolved conversions; the dashboard and MLG schema mark
the torque conversion as a candidate, and it requires synchronized target
validation before its engineering unit is treated as measured fact.

## Remaining semantic gaps

Commanded mixture is the Q14 word `FFFF22E8`: stage `0x5594A` forms it from
target mixture map `0xA9AA`, and `0x4000` is the closed-loop stoichiometric
target. Commanded lambda is `16384 / raw`. The gasoline AFR scale
`1881.6 / (raw / 128)` of the public HR A2L remains a candidate until a
wideband correlation is recorded.

The reviewed code and diagnostic layers do not establish a fuel-pressure
source or confirm that this ECU has a pressure sensor represented in software.

Knock margin fields `knock_margin_min_ch1_raw` through
`knock_margin_min_ch6_raw` publish the per-channel minimum of
`threshold - metric` as a signed word in evaluator units, latched by the
mechanism in
[`../patches/can-telemetry.md`](../patches/can-telemetry.md#knock-margin-latches).
A negative value is an evaluation that the stock comparison counts as a knock
event, limited at `-32768`. Context tag 4 publishes the six minimums and
rearms them with `32767`, which stands for an interval without an evaluation
of the channel or a margin of 32767 or more. Stock threshold rows 3 and 5 hold
`0xFFFF`, so their channels report `32767` until the metric exceeds 32768
units. The metric is a summed and gain-scaled sensor difference without a
physical conversion, and the channel-to-cylinder assignment is not
established. A tag-4 group that the queue replaces, preempts, or discards
before transmission takes its minimums with it.

The final ignition coordinate and APC command are software values. Neither is
independent feedback of spark delivery relative to the crankshaft. A physical
spark-angle claim requires external crank-referenced measurement.

The six injection words are compensated software calculations, and word `i`
belongs to cylinder `i + 1` by code. Their equality to electrical
injector-open duration is not measured at the injector terminals.

The end-of-injection angle word `FFFF192E` is a firmware coordinate:
`FUN_00056BD0` stores `2 * min(y, 209)` from tables `0x12302` and `0x1230A`,
and `raw * 2` is the delay in crank degrees after the reference tooth of the
scheduled cylinder. The intake-TDC anchor of `-590` degrees rests on the
reference-tooth and cylinder-order analysis in [`JK08A.fuel.md`](JK08A.fuel.md);
the mechanical offset between the crank sensor and the signal plate is a
hardware boundary. JK00C, JK00D, JK78C, 1ND, and 1ME3B bind the word their
homologous stage writes and carry the same chain from the tooth-7 reference
with ignition constant `110` to the slot masks, so the anchor holds for them.
For 1ND and 1ME3B the identity of event index and cylinder number rests on the
misfire attribution map, which 1ME3B builds in RAM, because their misfire
metric is not decompiled. Diagnostic word `FFFF162E`
behind DIDs `0x1131`, `0x1132`, `0x1133`, and `0x113D` has no runtime producer
in JK08A, reads zero, and is not streamed.

## Transport boundary

Schema 2 uses protocol version 2, profile ID 5, generated CRC16 `0xE144`, one
build-selected standard data CAN ID on physical mailbox 26, and the adjacent
control ID on polled receive mailbox 31. The CRC covers the wire layout alone:
protocol version, profile ID, page count, and the placement, width, and
signedness of every slot. Field names and scale strings are outside it, and a
slot that carries a different quantity takes a new profile ID. The data ID range is `0x001..0x7FE`;
the control ID is always `data_can_id + 1`.

Configuration byte `0x000D4E03` controls streaming at startup and is exposed in
the generated definitions as `CAN Telemetry at Startup`. The default is off.
Exact DLC-8 START and STOP commands on the control ID override that byte until
reset, and START activates telemetry even when the definition flag is off. The
dashboard can send these commands only through an active/ACK PCAN connection.

The dashboard, strict decoder, TRC converter, and MLVLG recorder implement only
this current schema. Historical schema 1 captures require the historical
decoder revision and are not accepted as schema 2 input.

The firmware and executable SH-2E gate are complete. Three road drives on
2026-08-26 with profile 1 and a road session on 2026-09-21 with the current
profile 5 carried the eleven-frame stream with the overrun and abort counters
at zero; [`../patches/hardware-results.toml`](../patches/hardware-results.toml)
records the captures. Physical validation of mailbox-31 START/STOP remains
required.
