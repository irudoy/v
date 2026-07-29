from datetime import datetime
import math
from pathlib import Path
import struct
import tempfile
import unittest
from zoneinfo import ZoneInfo

from tools.logs import csv_to_mlg


HEADER = (
    '"SECONDS";"PID";"VALUE";"UNITS";'
    '"LATITUDE";"LONGTITUDE";\n'
)


def parse_mlg(path):
    data = path.read_bytes()
    header = struct.unpack(">6sHIIIHH", data[:24])
    field_count = header[-1]
    record_length = header[-2]
    fields = []
    offset = 24
    for _ in range(field_count):
        descriptor = data[offset : offset + 89]
        fields.append(
            {
                "type": descriptor[0],
                "name": descriptor[1:35].split(b"\x00", 1)[0].decode("ascii"),
                "units": descriptor[35:45]
                .split(b"\x00", 1)[0]
                .decode("ascii"),
                "style": descriptor[45],
                "digits": struct.unpack(">b", descriptor[54:55])[0],
                "category": descriptor[55:89]
                .split(b"\x00", 1)[0]
                .decode("ascii"),
            }
        )
        offset += 89

    records = []
    block_size = record_length + 5
    while offset < len(data):
        block = data[offset : offset + block_size]
        values = {}
        value_offset = 4
        for field in fields:
            if field["type"] == csv_to_mlg.MLG_U32:
                value = struct.unpack(
                    ">I", block[value_offset : value_offset + 4]
                )[0]
            else:
                value = struct.unpack(
                    ">f", block[value_offset : value_offset + 4]
                )[0]
            values[field["name"]] = value
            value_offset += 4
        records.append(
            {
                "counter": block[1],
                "timestamp": struct.unpack(">H", block[2:4])[0],
                "values": values,
                "crc": block[-1],
                "calculated_crc": sum(block[4:-1]) & 0xFF,
            }
        )
        offset += block_size
    return header, fields, records


class ConversionTest(unittest.TestCase):
    def write_csv(self, directory, name, rows):
        path = Path(directory) / name
        path.write_text(HEADER + "".join(rows), encoding="utf-8")
        return path

    def test_conversion_preserves_updates_and_bridges_long_gaps(self):
        rows = [
            '"3600.0000";"Altitude (GPS)";"12.5";"m";'
            '"43.1";"131.9";\n',
            '"3600.0000";"[NC] Engine RPM";"1000";"rpm";'
            '"43.1";"131.9";\n',
            '"3601.2000";"[NC] Engine RPM";"1100";"rpm";'
            '"43.2";"132.0";\n',
            '"3601.2000";"Late flag";"1";"";'
            '"43.2";"132.0";\n',
        ]
        with tempfile.TemporaryDirectory() as directory:
            source = self.write_csv(
                directory, "2026-07-30 01-00-00.csv", rows
            )
            output = Path(directory) / "result.mlg"
            summary = csv_to_mlg.convert_csv(source, output)
            validation = csv_to_mlg.validate_mlg(output)
            header, fields, records = parse_mlg(output)

        self.assertEqual(header[0], b"MLVLG\x00")
        self.assertEqual(header[1], 2)
        expected_start = int(
            datetime(
                2026,
                7,
                30,
                1,
                0,
                tzinfo=ZoneInfo("Asia/Vladivostok"),
            ).timestamp()
        )
        self.assertEqual(header[2], expected_start)
        self.assertEqual(header[3], 0)
        self.assertEqual(summary.event_records, 2)
        self.assertEqual(summary.bridge_records, 3)
        self.assertEqual(validation.records, 5)
        self.assertEqual(
            [record["counter"] for record in records], [0, 1, 2, 3, 4]
        )
        self.assertEqual(
            [record["timestamp"] for record in records],
            [0, 30000, 60000, 24464, 54464],
        )
        ultralog_times = []
        previous_raw = 0
        wraps = 0
        for record in records:
            raw = record["timestamp"]
            if raw < previous_raw and previous_raw - raw > 30000:
                wraps += 1
            previous_raw = raw
            ultralog_times.append((raw + wraps * 65536) * 1e-5)
        self.assertEqual(ultralog_times, sorted(ultralog_times))
        self.assertAlmostEqual(ultralog_times[-1], 1.2, places=5)
        self.assertTrue(
            all(
                record["crc"] == record["calculated_crc"]
                for record in records
            )
        )

        names = [field["name"] for field in fields]
        self.assertEqual(
            names,
            [
                "Date",
                "Elapsed",
                "gps_lat",
                "gps_lon",
                "Altitude (GPS)",
                "Engine RPM",
                "Late flag",
            ],
        )
        self.assertEqual(fields[-1]["style"], csv_to_mlg.MLG_ON_OFF)
        gps_lat = fields[names.index("gps_lat")]
        gps_lon = fields[names.index("gps_lon")]
        for gps_field in (gps_lat, gps_lon):
            self.assertEqual(gps_field["type"], csv_to_mlg.MLG_F32)
            self.assertEqual(gps_field["units"], "deg")
            self.assertEqual(gps_field["style"], csv_to_mlg.MLG_FLOAT)
            self.assertEqual(gps_field["digits"], 6)
            self.assertEqual(gps_field["category"], "GPS")
        self.assertAlmostEqual(records[0]["values"]["Engine RPM"], 1000.0)
        self.assertAlmostEqual(records[1]["values"]["Engine RPM"], 1000.0)
        self.assertTrue(math.isnan(records[0]["values"]["Late flag"]))
        self.assertAlmostEqual(records[-1]["values"]["Late flag"], 1.0)
        self.assertAlmostEqual(records[-1]["values"]["gps_lat"], 43.2, places=4)
        self.assertAlmostEqual(
            records[-1]["values"]["gps_lon"], 132.0, places=4
        )

    def test_long_unicode_names_are_ascii_bounded_and_unique(self):
        source_fields = (
            csv_to_mlg.SourceField(
                "[NC] Throttle position sensor 1 (volts)", "\u2103"
            ),
            csv_to_mlg.SourceField(
                "[NC] Throttle position sensor 2 (volts)", "\u2103"
            ),
        )
        scan = csv_to_mlg.ScanResult(
            row_count=2,
            unique_timestamps=1,
            duplicate_pid_updates=0,
            first_seconds=0.0,
            last_seconds=0.0,
            source_fields=source_fields,
            has_latitude=False,
            has_longitude=False,
        )
        fields = csv_to_mlg.build_field_specs(scan)
        names = [field.name for field in fields]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(all(len(name.encode("ascii")) <= 33 for name in names))
        self.assertEqual(fields[-1].units, "degC")
        self.assertIn("1 (volts)", fields[-2].name)
        self.assertIn("2 (volts)", fields[-1].name)

    def test_block_counter_uses_full_u8_range(self):
        rows = [
            f'"{index / 100:.2f}";"RPM";"{index}";"rpm";"";"";\n'
            for index in range(257)
        ]
        with tempfile.TemporaryDirectory() as directory:
            source = self.write_csv(
                directory, "2026-07-30 01-00-00.csv", rows
            )
            output = Path(directory) / "result.mlg"
            csv_to_mlg.convert_csv(source, output)
            _, _, records = parse_mlg(output)

        self.assertEqual(
            [record["counter"] for record in records[254:257]],
            [254, 255, 0],
        )

    def test_decreasing_timestamps_are_rejected(self):
        rows = [
            '"2";"RPM";"1000";"rpm";"";"";\n',
            '"1";"RPM";"900";"rpm";"";"";\n',
        ]
        with tempfile.TemporaryDirectory() as directory:
            source = self.write_csv(
                directory, "2026-07-30 01-00-00.csv", rows
            )
            with self.assertRaisesRegex(
                csv_to_mlg.ConversionError, "SECONDS decreased"
            ):
                csv_to_mlg.scan_csv(source)

    def test_existing_output_requires_force(self):
        rows = ['"1";"RPM";"900";"rpm";"";"";\n']
        with tempfile.TemporaryDirectory() as directory:
            source = self.write_csv(
                directory, "2026-07-30 01-00-00.csv", rows
            )
            output = Path(directory) / "result.mlg"
            output.write_bytes(b"existing")
            with self.assertRaisesRegex(
                csv_to_mlg.ConversionError, "already exists"
            ):
                csv_to_mlg.convert_csv(source, output)

    def test_invalid_coordinates_are_rejected(self):
        rows = ['"1";"RPM";"900";"rpm";"91";"131";\n']
        with tempfile.TemporaryDirectory() as directory:
            source = self.write_csv(
                directory, "2026-07-30 01-00-00.csv", rows
            )
            with self.assertRaisesRegex(
                csv_to_mlg.ConversionError, "LATITUDE is outside"
            ):
                csv_to_mlg.scan_csv(source)


if __name__ == "__main__":
    unittest.main()
