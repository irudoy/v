"""Conformance of the MLVLG encoder to the version 2 format specification.

Every expectation here restates "Binary MLG Logging (MLVLG) file format
specification" Rev. 0.94 by Philip Tobin: byte offsets, field widths, the
10 us block timestamp, and the record checksum.
"""

import struct
import unittest

from tools.logs import mlvlg


HEADER_FIELDS = (
    mlvlg.FieldSpec(
        "Date", "s", "Time", mlvlg.MLG_U32, mlvlg.MLG_DATE, 1.0, 0.0, 0
    ),
    mlvlg.FieldSpec("Engine speed", "RPM", "Engine", mlvlg.MLG_U16, digits=0),
    mlvlg.FieldSpec(
        "Coolant",
        "degC",
        "Engine",
        mlvlg.MLG_U08,
        mlvlg.MLG_FLOAT,
        1.0,
        -50.0,
        1,
    ),
)


class HeaderLayoutTest(unittest.TestCase):
    def test_header_holds_the_specified_offsets(self):
        header = mlvlg.encode_header(HEADER_FIELDS, 1787740137)

        self.assertEqual(len(header), 24)
        self.assertEqual(header[0:6], b"MLVLG\x00")
        self.assertEqual(struct.unpack(">H", header[6:8])[0], 2)
        self.assertEqual(struct.unpack(">I", header[8:12])[0], 1787740137)
        self.assertEqual(struct.unpack(">I", header[12:16])[0], 0)
        self.assertEqual(
            struct.unpack(">I", header[16:20])[0],
            24 + 89 * len(HEADER_FIELDS),
        )
        self.assertEqual(struct.unpack(">H", header[20:22])[0], 4 + 2 + 1)
        self.assertEqual(
            struct.unpack(">H", header[22:24])[0], len(HEADER_FIELDS)
        )

    def test_absent_start_time_is_stored_as_zero(self):
        header = mlvlg.encode_header(HEADER_FIELDS, 0)

        self.assertEqual(header[8:12], bytes(4))

    def test_field_data_sizes_follow_the_type_table(self):
        expected = {
            mlvlg.MLG_U08: 1,
            mlvlg.MLG_S08: 1,
            mlvlg.MLG_U16: 2,
            mlvlg.MLG_S16: 2,
            mlvlg.MLG_U32: 4,
            mlvlg.MLG_S32: 4,
            mlvlg.MLG_S64: 8,
            mlvlg.MLG_F32: 4,
        }
        for field_type, size in expected.items():
            with self.subTest(field_type=field_type):
                field = mlvlg.FieldSpec("Probe", field_type=field_type)
                self.assertEqual(field.data_size, size)


class LoggerFieldLayoutTest(unittest.TestCase):
    def test_scalar_descriptor_holds_the_specified_offsets(self):
        field = mlvlg.FieldSpec(
            "Intake CVTC actual B1",
            "degCA*",
            "CVTC",
            mlvlg.MLG_U08,
            mlvlg.MLG_FLOAT,
            0.5,
            -128.0,
            1,
        )

        encoded = mlvlg.encode_field(field)

        self.assertEqual(len(encoded), 89)
        self.assertEqual(encoded[0], mlvlg.MLG_U08)
        self.assertEqual(
            encoded[1:35].rstrip(b"\x00"), b"Intake CVTC actual B1"
        )
        self.assertEqual(encoded[34], 0)
        self.assertEqual(encoded[35:45].rstrip(b"\x00"), b"degCA*")
        self.assertEqual(encoded[44], 0)
        self.assertEqual(encoded[45], mlvlg.MLG_FLOAT)
        self.assertEqual(struct.unpack(">f", encoded[46:50])[0], 0.5)
        self.assertEqual(struct.unpack(">f", encoded[50:54])[0], -128.0)
        self.assertEqual(struct.unpack(">b", encoded[54:55])[0], 1)
        self.assertEqual(encoded[55:89].rstrip(b"\x00"), b"CVTC")
        self.assertEqual(encoded[88], 0)

    def test_text_stays_ascii_and_null_terminated(self):
        field = mlvlg.FieldSpec("Timing 30°", "℃", "Engine")

        encoded = mlvlg.encode_field(field)

        self.assertEqual(encoded[1:35].rstrip(b"\x00"), b"Timing 30deg")
        self.assertEqual(encoded[35:45].rstrip(b"\x00"), b"degC")
        for start, end in ((1, 35), (35, 45), (55, 89)):
            encoded[start:end].decode("ascii")

    def test_text_that_leaves_no_terminator_is_rejected(self):
        with self.assertRaises(mlvlg.MlvlgError):
            mlvlg.encode_field(mlvlg.FieldSpec("N" * 34))
        with self.assertRaises(mlvlg.MlvlgError):
            mlvlg.encode_field(mlvlg.FieldSpec("Probe", "u" * 10))
        with self.assertRaises(mlvlg.MlvlgError):
            mlvlg.encode_field(mlvlg.FieldSpec("Probe", "u", "c" * 34))

    def test_digits_are_a_signed_byte(self):
        encoded = mlvlg.encode_field(mlvlg.FieldSpec("Probe", digits=-2))

        self.assertEqual(struct.unpack(">b", encoded[54:55])[0], -2)
        with self.assertRaises(mlvlg.MlvlgError):
            mlvlg.encode_field(mlvlg.FieldSpec("Probe", digits=128))


class DataBlockLayoutTest(unittest.TestCase):
    def test_data_block_holds_the_specified_offsets(self):
        payload = bytes((0x12, 0x34, 0xFE))

        block = mlvlg.encode_payload_block(payload, 7, 0.01)

        self.assertEqual(len(block), 4 + len(payload) + 1)
        self.assertEqual(block[0], 0x00)
        self.assertEqual(block[1], 7)
        self.assertEqual(struct.unpack(">H", block[2:4])[0], 1000)
        self.assertEqual(block[4:4 + len(payload)], payload)
        self.assertEqual(block[-1], (0x12 + 0x34 + 0xFE) & 0xFF)

    def test_checksum_covers_the_record_only(self):
        payload = bytes((0xFF, 0x02))

        block = mlvlg.encode_payload_block(payload, 200, 0.5)

        self.assertEqual(block[-1], 0x01)

    def test_timestamp_resolves_ten_microseconds(self):
        cases = {
            0.0: 0,
            0.00001: 1,
            0.000216: 22,
            0.015: 1500,
            0.65535: 65535,
            0.65536: 0,
            1.0: 34464,
        }
        for elapsed, ticks in cases.items():
            with self.subTest(elapsed=elapsed):
                block = mlvlg.encode_payload_block(b"\x00", 0, elapsed)
                self.assertEqual(struct.unpack(">H", block[2:4])[0], ticks)

    def test_counter_rolls_over_one_byte(self):
        """The type-0 table writes ``Counter % 255``.

        A rolling one-byte counter carries the record number modulo 256, which
        is what the rusEFI reference writer stores and MegaLogViewer reads.
        """

        for counter, stored in ((0, 0), (255, 255), (256, 0), (257, 1)):
            with self.subTest(counter=counter):
                block = mlvlg.encode_payload_block(b"\x00", counter, 0.0)
                self.assertEqual(block[1], stored)

    def test_record_values_are_big_endian(self):
        fields = (
            mlvlg.FieldSpec("Speed", field_type=mlvlg.MLG_U16),
            mlvlg.FieldSpec("Value", field_type=mlvlg.MLG_F32),
        )

        data = mlvlg.encode_record_data(fields, (0x1234, 1.0))

        self.assertEqual(data, b"\x12\x34" + struct.pack(">f", 1.0))


if __name__ == "__main__":
    unittest.main()
