# JK08A CAN telemetry dashboard

This Tkinter application displays the custom JK08A `core32` or `wide54`
telemetry stream from a PEAK PCAN-USB adapter. The default configuration
matches local candidate `v1.11`:

- PCAN channel `PCAN_USBBUS1`;
- classical CAN at `500000 bit/s`;
- standard ID `0x6F0`;
- `wide54`, divisor 1;
- listen-only PCAN state.

The application uses the tracked strict decoder and generated schema. It does
not transmit application CAN messages. Listen-only mode also suppresses CAN
ACK participation. Use the separate active/ACK launcher only on an isolated
bench where the ECU otherwise has no node to acknowledge its transmissions.

The Windows driver package installs the PCAN-Basic DLL in the system directory.
The dashboard accesses it through `python-can` 4.6.1. PEAK documents the
PCAN-Basic DLL as the supported interface between an application and the device
driver, and `python-can` documents `PCAN_USBBUS1`, passive state, and
`500000 bit/s` for this adapter.

## Portable Windows package

Build the ignored transfer archive from the repository root:

```bash
python3 tools/can_dashboard/package_windows.py \
  --output tmp/jk08a-can-dashboard-windows.zip
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

The default hardware filter accepts custom telemetry plus stock context IDs
`0x180`, `0x239`, `0x421`, and `0x551`. The latter provide an independent RPM
cross-check, ASCD input, PRND, and dashboard indication state.

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
```

Replay accepts PEAK PCAN-View TRC 1.1 files directly, including the `.trc`
captures used by the project. It also accepts compact candump lines such as
`(12.500000) can0 6F0#A001020304050607`.

## Display semantics

The decoder retains the latest values from the four rotating page-7 contexts.
Schema-dependent conversions stay disabled until the in-band health context
matches protocol version, profile ID, and CRC16. Stale context values remain
visible while their update cadence is one quarter of the snapshot rate.

Fields marked with `*` use candidate transforms or diagnostic semantic
bindings. `final_timing_raw` is a software command, not a measured spark angle.
Injection values use the declared candidate `/100 ms` transform but are not a
verified electrical injector-open duration. The dashboard preserves these
boundaries in its labels and footer.

Health indicators include complete snapshot and frame rates, tick-derived
loss, incomplete and malformed groups, schema mismatches, source queue drops,
telemetry status flags, and the rotating overrun and abort counters.
