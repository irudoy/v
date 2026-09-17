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
9 and 10 are transmitted at the same rate and rotate a shared four-value tag,
so each tagged field set refreshes at `24.4140625 Hz`.

The fixed pages provide:

- engine speed, both MAF sensor words, combined airflow, base fuel schedule,
  and calculated load;
- final ignition coordinate, APC command, ignition state, knock state, and
  latched knock interval count and channel mask;
- all six calculated injection words, injection timing state, and the final
  fuel-output inhibit mask;
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
- intake CVTC solenoid duty commands, the low-resolution intake duty
  monitor pair, and high-resolution exhaust duty;
- atmospheric pressure and battery voltage;
- higher-resolution front A/F sensor words and both adjustment integrators;
- secondary throttle feedback for both banks;
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

The exact source identity is stronger than the physical conversion. The
airflow, coolant, intake-air, timing, vehicle-speed, and absolute-throttle
units are the ECU's own J1979 Mode 01 declarations, recorded in the
diagnostics note; they describe the firmware model, not a hardware measurement.
Fields marked as candidates by the dashboard and MLG schema still require
synchronized target validation before their engineering units are treated as
measured fact.

## Remaining semantic gaps

Commanded mixture is the Q14 word `FFFF22E8`: stage `0x5594A` forms it from
target mixture map `0xA9AA`, and `0x4000` is the closed-loop stoichiometric
target. Commanded lambda is `16384 / raw`. The gasoline AFR scale
`1881.6 / (raw / 128)` of the public HR A2L remains a candidate until a
wideband correlation is recorded.

The reviewed code and diagnostic layers do not establish a fuel-pressure
source or confirm that this ECU has a pressure sensor represented in software.

The active knock evaluator uses a transient register-local metric. Existing
state and latches show intervention, but per-evaluation metric, threshold, or
margin requires a capture hook in the evaluator path.

The final ignition coordinate and APC command are software values. Neither is
independent feedback of spark delivery relative to the crankshaft. A physical
spark-angle claim requires external crank-referenced measurement.

The six injection words are compensated software calculations. Their equality
to electrical injector-open duration and their physical cylinder ordering are
not established by the current evidence.

## Transport boundary

Schema 2 uses protocol version 2, profile ID 3, generated CRC16 `0x01A3`, one
build-selected standard data CAN ID on physical mailbox 26, and the adjacent
control ID on polled receive mailbox 31. The data ID range is `0x001..0x7FE`;
the control ID is always `data_can_id + 1`.

Configuration byte `0x000D4E03` controls streaming at startup and is exposed in
the generated definitions as `CAN Telemetry at Startup`. The default is off.
Exact DLC-8 START and STOP commands on the control ID override that byte until
reset, and START activates telemetry even when the definition flag is off. The
dashboard can send these commands only through an active/ACK PCAN connection.

The dashboard, strict decoder, TRC converter, and MLVLG recorder implement only
this current schema. Historical schema 1 captures require the historical
decoder revision and are not accepted as schema 2 input.

The firmware and executable SH-2E gate are complete. Physical validation of
mailbox-31 START/STOP and the eleven-frame stream remains required before
schema 2 is used for a normal target-vehicle logging run.
