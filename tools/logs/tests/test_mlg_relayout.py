import math
from pathlib import Path
import struct
import tempfile
import unittest

from tools.can_dashboard import recording
from tools.logs import mlg_relayout, mlvlg


START_EPOCH = 1_789_935_345
BINDINGS = recording.build_bindings("tuning")
SPEC_BY_SOURCE = {binding.source: binding.spec for binding in BINDINGS}
MARKER = b"key off".ljust(mlvlg.MLG_MARKER_MESSAGE_SIZE, b"\x00")

# An earlier recorder put the candidate marker in the name, stored a signed
# slot unsigned, and recorded a channel the current profile does not bind.
SOURCE_SPECS = (
    SPEC_BY_SOURCE["date"],
    SPEC_BY_SOURCE["elapsed"],
    SPEC_BY_SOURCE["tick16"],
    mlvlg.FieldSpec(SPEC_BY_SOURCE["af_adjustment_b1_raw"].name + "*", "", "Fuel"),
    mlvlg.FieldSpec("Stock CAN RPM", "rpm", "Context"),
    mlvlg.FieldSpec("Retired slot", "raw", "Telemetry"),
)
# The second record repeats the tick of the first: a bridge record.
ROWS = (
    (START_EPOCH, 0.0, 100.0, 65535.0, 812.5, 7.0),
    (START_EPOCH, 0.3, 100.0, 65535.0, 812.5, 7.0),
    (START_EPOCH + 1, 0.3125, 101.0, 12.0, 825.0, 8.0),
)


def write_source(path, specs=SOURCE_SPECS, rows=ROWS):
    """Write a recording with a marker block between its first two records."""

    blocks = []
    counter = 0
    for index, row in enumerate(rows):
        blocks.append(mlvlg.encode_data_block(specs, row, counter, row[1]))
        counter += 1
        if index == 0:
            blocks.append(b"\x01" + bytes((counter,)) + b"\x00\x00" + MARKER)
            counter += 1
    header = mlvlg.encode_header(specs, START_EPOCH)
    path.write_bytes(
        header + b"".join(mlvlg.encode_field(spec) for spec in specs) + b"".join(blocks)
    )
    mlvlg.validate_mlg(path)


def read_blocks(path):
    specs = mlvlg.read_fields(path)
    data = Path(path).read_bytes()
    header = struct.unpack(">6sHIIIHH", data[: mlvlg.MLG_HEADER_SIZE])
    record = struct.Struct(
        ">" + "".join(mlvlg.FIELD_STRUCTS[spec.field_type][1:] for spec in specs)
    )
    blocks = []
    offset = header[4]
    while offset < len(data):
        prefix = data[offset : offset + 4]
        if prefix[0]:
            blocks.append((prefix, data[offset + 4 : offset + 4 + mlvlg.MLG_MARKER_MESSAGE_SIZE]))
            offset += 4 + mlvlg.MLG_MARKER_MESSAGE_SIZE
            continue
        values = record.unpack_from(data, offset + 4)
        blocks.append((prefix, dict(zip((spec.name for spec in specs), values))))
        offset += 4 + header[5] + 1
    return header, specs, blocks


class MlgRelayoutTest(unittest.TestCase):
    def test_output_takes_the_current_layout_and_keeps_every_block(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.mlg"
            output = Path(directory) / "current" / "source.mlg"
            write_source(source)

            summary = mlg_relayout.relayout(source, output)

            source_header, _specs, source_blocks = read_blocks(source)
            header, specs, blocks = read_blocks(output)
            self.assertEqual(
                specs,
                tuple(
                    mlvlg.decode_field(mlvlg.encode_field(binding.spec))
                    for binding in BINDINGS
                ),
            )
            self.assertEqual(header[2], source_header[2])
            self.assertEqual((summary.data_records, summary.marker_records), (3, 1))
            self.assertEqual(summary.dropped, ("Retired slot",))
            carried = {"Date", "Elapsed", "Telemetry tick", "Stock CAN RPM"}
            carried.add(SPEC_BY_SOURCE["af_adjustment_b1_raw"].name)
            self.assertEqual(
                set(summary.missing), {spec.name for spec in specs} - carried
            )
            self.assertEqual(
                [prefix for prefix, _values in blocks],
                [prefix for prefix, _values in source_blocks],
            )
            self.assertEqual(blocks[1][1], MARKER)

            adjustment = SPEC_BY_SOURCE["af_adjustment_b1_raw"].name
            data_blocks = [values for _prefix, values in blocks if isinstance(values, dict)]
            for row, values in zip(ROWS, data_blocks):
                self.assertEqual(values["Date"], row[0])
                self.assertEqual(values["Elapsed"], struct.unpack(">f", struct.pack(">f", row[1]))[0])
                self.assertEqual(values["Telemetry tick"], row[2])
                self.assertEqual(values["Stock CAN RPM"], row[4])
                self.assertTrue(math.isnan(values["Engine load"]))
            self.assertEqual(
                [values[adjustment] for values in data_blocks], [-1.0, -1.0, 12.0]
            )

    def test_output_never_replaces_the_source_or_an_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.mlg"
            output = Path(directory) / "output.mlg"
            write_source(source)
            with self.assertRaises(ValueError):
                mlg_relayout.relayout(source, source)
            output.write_bytes(b"kept")
            with self.assertRaises(FileExistsError):
                mlg_relayout.relayout(source, output)
            self.assertEqual(output.read_bytes(), b"kept")
            mlg_relayout.relayout(source, output, force=True)
            mlvlg.validate_mlg(output)

    def test_a_recording_without_the_producer_tick_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.mlg"
            specs = SOURCE_SPECS[:2] + SOURCE_SPECS[3:]
            write_source(source, specs, tuple(row[:2] + row[3:] for row in ROWS))
            with self.assertRaisesRegex(mlvlg.MlvlgError, "Telemetry tick"):
                mlg_relayout.relayout(source, Path(directory) / "output.mlg")

    def test_two_channels_of_one_identity_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.mlg"
            specs = SOURCE_SPECS + (mlvlg.FieldSpec("Stock CAN RPM*", "rpm", "Context"),)
            write_source(source, specs, tuple(row + (0.0,) for row in ROWS))
            with self.assertRaisesRegex(mlvlg.MlvlgError, "name one channel"):
                mlg_relayout.relayout(source, Path(directory) / "output.mlg")


if __name__ == "__main__":
    unittest.main()
