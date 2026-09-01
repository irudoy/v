from pathlib import Path
import struct
import tempfile
import unittest

from tools.logs import mlg_retime, mlvlg


START_EPOCH = 1_787_740_137
PERIOD = 0.0102429

SPECS = (
    mlvlg.FieldSpec("Date", "s", "Time", mlvlg.MLG_U32, mlvlg.MLG_DATE, digits=0),
    mlvlg.FieldSpec("Elapsed", "s", "Time", mlvlg.MLG_F32, digits=3),
    mlvlg.FieldSpec("Telemetry tick", "", "Time", mlvlg.MLG_F32, digits=0),
    mlvlg.FieldSpec("Engine speed", "RPM", "Engine", mlvlg.MLG_F32, digits=0),
)


def collapsed_log(path, records=8, first_tick=65530):
    """Write a log whose host clock collapses every second record onto one tick."""

    times = []
    with path.open("wb") as stream:
        writer = mlvlg.StreamWriter(stream, SPECS, START_EPOCH)
        for index in range(records):
            elapsed = 0.02 + (index // 2) * 0.015
            times.append(elapsed)
            tick = (first_tick + index) % 0x10000
            writer.write(
                (
                    START_EPOCH + int(elapsed),
                    elapsed,
                    float(tick),
                    1000.0 + index,
                ),
                elapsed,
            )
    mlvlg.validate_mlg(path)
    return times


def channels(path):
    specs = mlvlg.read_fields(path)
    data = Path(path).read_bytes()
    header = struct.unpack(">6sHIIIHH", data[: mlvlg.MLG_HEADER_SIZE])
    data_begin, record_length = header[4], header[5]
    formats = [mlvlg.FIELD_STRUCTS[spec.field_type] for spec in specs]
    names = [spec.name.strip() for spec in specs]
    rows = []
    stamps = []
    offset = data_begin
    while offset + record_length + 5 <= len(data):
        stamps.append(struct.unpack(">H", data[offset + 2 : offset + 4])[0])
        base = offset + 4
        row = {}
        for name, fmt in zip(names, formats):
            size = struct.calcsize(fmt)
            row[name] = struct.unpack(fmt, data[base : base + size])[0]
            base += size
        rows.append(row)
        offset += record_length + 5
    return rows, stamps


class MlgRetimeTest(unittest.TestCase):
    def test_retime_restores_the_tick_spacing(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "collapsed.mlg"
            output = Path(directory) / "retimed.mlg"
            collapsed_log(source)
            before, before_stamps = channels(source)

            summary = mlg_retime.retime(
                source, output, period_seconds=PERIOD
            )

            self.assertTrue(summary.written)
            self.assertEqual(summary.records, len(before))
            self.assertEqual(summary.collapsed_before, 4)
            self.assertEqual(summary.collapsed_after, 0)
            self.assertLess(len(set(before_stamps)), len(before_stamps))

            after, stamps = channels(output)
            self.assertEqual(len(set(stamps)), len(stamps))
            steps = [
                round((b["Elapsed"] - a["Elapsed"]) * 1e6)
                for a, b in zip(after, after[1:])
            ]
            self.assertEqual(set(steps), {round(PERIOD * 1e6)})
            for index, (a, b) in enumerate(zip(before, after)):
                with self.subTest(record=index):
                    self.assertEqual(a["Telemetry tick"], b["Telemetry tick"])
                    self.assertEqual(a["Engine speed"], b["Engine speed"])

    def test_retime_keeps_the_recording_start_and_updates_dates(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "collapsed.mlg"
            output = Path(directory) / "retimed.mlg"
            collapsed_log(source, records=200)

            mlg_retime.retime(source, output, period_seconds=PERIOD)

            after, stamps = channels(output)
            self.assertAlmostEqual(after[0]["Elapsed"], 0.02, places=5)
            self.assertEqual(stamps[0], round(0.02 * 100_000))
            for index, row in enumerate(after):
                with self.subTest(record=index):
                    self.assertEqual(
                        row["Date"], int(START_EPOCH + row["Elapsed"])
                    )
                    stored = round(row["Elapsed"] * 100_000) & 0xFFFF
                    self.assertLessEqual(
                        min(
                            abs(stamps[index] - stored),
                            0x10000 - abs(stamps[index] - stored),
                        ),
                        1,
                    )

    def test_measured_period_matches_the_recorded_span(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "collapsed.mlg"
            output = Path(directory) / "retimed.mlg"
            times = collapsed_log(source, records=64)

            summary = mlg_retime.retime(source, output)

            self.assertAlmostEqual(
                summary.period_seconds,
                (times[-1] - times[0]) / 63,
                places=9,
            )
            self.assertAlmostEqual(
                summary.span_seconds, times[-1] - times[0], places=6
            )

    def test_repeated_ticks_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bridged.mlg"
            output = Path(directory) / "retimed.mlg"
            with source.open("wb") as stream:
                writer = mlvlg.StreamWriter(stream, SPECS, START_EPOCH)
                for index, tick in enumerate((1.0, 2.0, 2.0, 3.0)):
                    writer.write(
                        (START_EPOCH, index * 0.01, tick, 900.0), index * 0.01
                    )
            mlvlg.validate_mlg(source)

            with self.assertRaises(mlvlg.MlvlgError) as error:
                mlg_retime.retime(source, output)

            self.assertIn("repeat a telemetry tick", str(error.exception))
            self.assertFalse(output.exists())

    def test_dry_run_reports_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "collapsed.mlg"
            output = Path(directory) / "retimed.mlg"
            collapsed_log(source)

            summary = mlg_retime.retime(source, output, dry_run=True)

            self.assertFalse(summary.written)
            self.assertEqual(summary.collapsed_after, 0)
            self.assertFalse(output.exists())

    def test_cli_writes_a_derived_file_and_keeps_the_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "collapsed.mlg"
            collapsed_log(source)
            original = source.read_bytes()

            status = mlg_retime.main([str(source)])

            self.assertEqual(status, 0)
            self.assertEqual(source.read_bytes(), original)
            derived = mlg_retime.default_output(source)
            self.assertTrue(derived.exists())
            mlvlg.validate_mlg(derived)

    def test_output_must_be_a_new_file(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "collapsed.mlg"
            collapsed_log(source)

            with self.assertRaises(ValueError):
                mlg_retime.retime(source, source)


if __name__ == "__main__":
    unittest.main()
