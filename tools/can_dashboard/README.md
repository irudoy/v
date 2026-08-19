# VQ CAN telemetry dashboard

Current dashboard version: `1.1.3`.

This Tkinter application displays and records VQ custom CAN telemetry from a
PEAK PCAN-USB adapter on Windows or macOS. The current verified schema supports
the JK08A `core32` and `wide54` profiles. The default configuration matches
local candidate `v1.11`:

- PCAN channel `PCAN_USBBUS1`;
- classical CAN at `500000 bit/s`;
- standard ID `0x6F0`;
- `wide54`, divisor 1;
- listen-only PCAN state.

The application uses the tracked strict decoder and generated schema. It does
not transmit application CAN messages. Listen-only mode also suppresses CAN
ACK participation. Use the separate active/ACK launcher only on an isolated
bench where the ECU otherwise has no node to acknowledge its transmissions.

The version has one source in `tools/can_dashboard/__init__.py`. It is visible
in the window title, main heading, Windows portable-package directory,
`VERSION.txt`, and macOS `Info.plist`. Semantic-version major changes denote an
incompatible UI, CLI, or MLG contract; minor changes add compatible
functionality; patch changes preserve both contracts.

The Windows driver package installs the PCAN-Basic DLL in the system directory.
The dashboard accesses it through `python-can` 4.6.1. PEAK documents the
PCAN-Basic DLL as the supported interface between an application and the device
driver, and `python-can` documents `PCAN_USBBUS1`, passive state, and
`500000 bit/s` for this adapter. The portable package also installs `tzdata`
2026.3 so IANA timezones used by the TRC converter are available on Windows.

On macOS, `python-can` uses the third-party MacCAN `libPCBUSB` user-space
driver. Version 0.13 supports PCAN-USB on Intel and Apple silicon. The dashboard
follows the proven Cansult connection sequence and releases the PCAN-Basic
channel before opening it and after shutdown. This reset is enabled by default
on macOS and can be disabled with `--no-reset-channel` when another process
intentionally owns the channel. Close other PCAN clients before normal use.
The native application embeds Python, Tk, `python-can`, and its data files;
MacCAN remains a system driver and is not copied into the application.

Each source run has a generation identifier. Reconnect, replay replacement,
and source stop invalidate queued events from the retired worker before a new
model is created. Terminal source status is retained even when the frame queue
is full, and PCAN receive or shutdown failures remain visible as errors rather
than being replaced by a normal stopped state.

## Portable Windows package

Build the ignored transfer archive from the repository root:

```bash
python3 tools/can_dashboard/package_windows.py \
  --output tmp/vq-can-telemetry-v1.1.3-windows.zip
```

On the Windows laptop:

1. Install the current PEAK PCAN-USB driver and verify the adapter with
   PCAN-View at `500 kbit/s`.
2. Install 64-bit Python 3.11 from python.org with the `py` launcher.
3. Extract the complete ZIP to a writable directory.
4. Run `install.cmd` once. It creates `.venv` and installs `python-can`.
5. Run `run-demo.cmd` to verify the UI without CAN hardware.
6. Run `run-dashboard.cmd` for listen-only vehicle capture.
7. Use `run-dashboard-active.cmd` only when an isolated ECU needs this adapter
   to provide CAN ACK.

The package also includes `convert-trc-to-mlg.cmd`. Pass one or more PEAK TRC
1.1 paths to it after `install.cmd`; each result is written beside its source.

The default hardware filter accepts custom telemetry plus stock context IDs
`0x180`, `0x239`, `0x280`, `0x421`, and `0x551`. They provide an independent
RPM cross-check, vehicle speed, ASCD input, selector state, and dashboard
indication state.

## Native macOS application

Build the ignored arm64 application and transfer archive from the repository
root:

```bash
make dashboard-package-macos
```

The target writes:

- `tmp/VQ CAN Telemetry.app` for direct local use;
- `tmp/vq-can-telemetry-v1.1.3-macos-arm64.zip` for transfer.

The build uses pinned PyInstaller 6.21.0 in `onedir`, `windowed` mode. It embeds
the tested Python/Tk runtime and all Python dependencies, preserves bundle
symlinks in the ZIP, records version 1.1.3 in `Info.plist`, and applies an
ad-hoc signature. The build gate verifies the arm64 architecture, deep code
signature, complete bundle metadata, and a hidden deterministic UI/demo run.
The same gate loads the frozen `python-can` PCAN backend and the installed
MacCAN library without changing a channel's state. It extracts the completed
ZIP and revalidates the archived application before accepting the package.

On the target Mac, install MacCAN `libPCBUSB` 0.13, extract the ZIP, and open
`VQ CAN Telemetry.app`. No Python installation or shell launcher is needed.
The main source starts in listen-only mode; use the visible `Listen-only`
control to opt into active/ACK behavior only on an isolated bench. A downloaded
ad-hoc-signed build is not notarized, so the first launch may require Finder's
Open action after the archive source and SHA-256 are verified.

The `0x551` display uses neutral labels `ASCD STATE 6` and `ASCD STATE 7`.
Exact-target observation shows that custom state 6 illuminates SET together
with CRUISE, so it is not labeled CRUISE-only. The correct CRUISE-only state
remains pending a passive stock-state correlation.

## Direct repository run

Install the Windows dependency and start the module from the repository root:

```text
py -3.11 -m pip install -r tools\can_dashboard\requirements-windows.txt
py -3.11 -m tools.can_dashboard.app
```

Useful modes:

```text
py -3.11 -m tools.can_dashboard.app --demo
py -3.11 -m tools.can_dashboard.app --replay capture.log
py -3.11 -m tools.can_dashboard.app --active
py -3.11 -m tools.can_dashboard.app --channel PCAN_USBBUS2
py -3.11 -m tools.can_dashboard.app --record drive.mlg
```

On macOS with `libPCBUSB` already installed, the equivalent repository run is:

```bash
uv run --with-requirements tools/can_dashboard/requirements-macos.txt \
  python -m tools.can_dashboard.app \
  --channel PCAN_USBBUS1 --bitrate 500000 \
  --can-id 0x6F0 --profile wide54 --tick-divisor 1
```

The macOS default includes the channel reset. Pass `--no-reset-channel` only
when preserving another client's PCAN-Basic ownership is intentional.

Replay accepts PEAK PCAN-View TRC 1.1 files directly, including the `.trc`
captures used by the project. It also accepts compact candump lines such as
`(12.500000) can0 6F0#A001020304050607`.

## MLG recording

`Record MLG` selects a destination and starts an atomic MLVLG v2 recording.
Only complete strict telemetry snapshots produce records. `Stop MLG`, source
stop, source replacement, and window close finalize and validate the file.
No new output is left when no complete snapshot was received; an existing file
selected for replacement remains unchanged in that case. Existing files require
an explicit replacement confirmation in the UI and are rejected by `--record`.

Frames already queued when recording starts update the display but are not
written to the new file. The first MLG event therefore cannot predate the
recording start or be collapsed onto elapsed time zero.

The `wide54` MLG schema has 60 channels: time, schema state, every fixed and
rotating custom-telemetry field, stock CAN RPM, vehicle speed, selector code,
ASCD input, dashboard state, and `gps_lat`/`gps_lon`. Candidate transforms
retain `*` in their field names. Decoded telemetry and context values use F32,
so a rotating context that has not arrived yet can be represented as `NaN`
rather than a fabricated zero.

MLG has a wrapping 16-bit 10-us block timestamp. A hold-last bridge record is
inserted when complete snapshots are more than 0.3 seconds apart, which keeps
the wrap sequence unambiguous to the local UltraLog parser. Normal divisor-1
traffic needs no bridge records.

The dashboard declares `gps_lat` and `gps_lon` for Track Map compatibility,
but no geographic-coordinate signal is verified on the captured primary CAN
network. Both values therefore display `--` and are stored as `NaN`. A real
route requires a separately captured and decoded AV/navigation network or
another GPS source. The logger never invents coordinates from vehicle speed.

## Display semantics

The decoder retains the latest values from the four rotating page-7 contexts.
Schema-dependent conversions stay disabled until the in-band health context
matches protocol version, profile ID, and CRC16. Stale context values remain
visible while their update cadence is one quarter of the snapshot rate.

Fields marked with `*` use target-correlated transforms, candidate transforms,
or diagnostic semantic bindings. The current conversions are:

| Display | Source | Conversion | Evidence boundary |
| --- | --- | --- | --- |
| vehicle speed | `0x280` bytes 4..5 | big-endian `raw / 100 km/h` | target field and zero state confirmed; scale remains homologous |
| APP 1/2 | telemetry words | `raw / 200 V` | homologous formula and near-adjacent target agreement |
| TPS bank 1/2 | telemetry words | `raw / 200 V` | near-adjacent target agreement |
| fuel/oil temperature | telemetry bytes | `raw - 50 degC` | exact JK08A DID pointers plus homologous profile; oil agrees on target |
| short/long fuel trim | telemetry Q8.8 words | `raw / 256 - 100 percent` | exact neutral representation and target diagnostic agreement |
| timing coordinate | `final_timing_raw` signed byte | `raw deg` | upstream stock coordinate during a Rolling Launch late override; not a measured spark angle |
| APC command | `apc_command_raw` byte | raw | effective software command consumed by the APC scheduler; normal-path timing coordinate is `110 - raw` |

The CarScanner comparison follows the CAN recording rather than sharing a
clock with it. It corroborates transforms but cannot prove equality for values
that can change between captures. Injection values use the declared candidate
`raw / 100 ms` transform but are compensated software commands, not verified
electrical injector-open durations. Timing is also a software command, not a
measured spark angle. The current top-card label `Timing command` names
`final_timing_raw`; during a Rolling Launch late override it is the upstream
stock coordinate rather than the effective command. The detailed `APC command`
field carries the effective command.

Health indicators include complete snapshot and frame rates, tick-derived
loss, incomplete and malformed groups, schema mismatches, source queue drops,
telemetry status flags, and the rotating overrun and abort counters.

Convert an existing PEAK trace without replay timing:

```bash
python3 tools/logs/trc_to_mlg.py tmp/can-dump/new-log-full.trc
```

The converter and live recorder use the same MLVLG schema and validator.

## Target-vehicle result

The 2026-08-17 `wide54`, divisor-1 capture contains 35,811 complete snapshots
at 97.599 Hz. After synchronization to the first page 0, it has zero malformed
or incomplete groups, tick gaps, schema mismatches, nonzero telemetry status,
snapshot overruns, TX aborts, PCAN warnings, and PCAN errors. Whole-bus average
load is 57.185% to 69.437%, and the maximum rolling 100 ms estimate is 59.006%
to 71.650% at `500 kbit/s`.

Observed selector codes are `08=P`, `10=R`, `18=N`, `20=D`, `28=DS`,
`80=M1`, `88=M2`, `90=M3`, `98=M4`, and `A0=M5`. Codes `98` and `A0` are
operator-confirmed observations outside the saved trace. ASCD byte 3 code
`10` is RESUME/ACCEL and has the same evidence boundary.
