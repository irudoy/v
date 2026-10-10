"""Exact, read-only projection checks for the vendor dictionaries."""

import contextlib
import importlib
import io
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from tools.vendor import build_catalog as catalog


class VendorCatalogTest(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.vendor = Path(self.scratch.name)
        for name in ('proecu-maps.csv', 'uprev-maps.csv'):
            shutil.copyfile(catalog.VENDOR / name, self.vendor / name)
        catalog.generate(self.vendor)

    def snapshot(self):
        return {path.name: path.read_bytes() for path in self.vendor.iterdir()}

    def test_current_projection_is_exact_and_check_writes_nothing(self):
        before = self.snapshot()
        self.assertEqual(before['catalog.csv'],
                         (catalog.VENDOR / 'catalog.csv').read_bytes())
        with mock.patch.object(Path, 'write_bytes', side_effect=AssertionError('write')):
            rows = catalog.generate(self.vendor, check=True)
        self.assertEqual(len(rows), 371)
        self.assertEqual(self.snapshot(), before)

    def test_changed_derived_column_is_rejected_and_preserved(self):
        path = self.vendor / 'catalog.csv'
        path.write_bytes(path.read_bytes().replace(b'factory', b'unknown', 1))
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'differs from its rendering'):
            catalog.generate(self.vendor, check=True)
        self.assertEqual(self.snapshot(), before)

    def test_missing_projection_is_rejected_without_creation(self):
        (self.vendor / 'catalog.csv').unlink()
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'missing'):
            catalog.generate(self.vendor, check=True)
        self.assertEqual(self.snapshot(), before)

    def test_newline_drift_is_rejected(self):
        path = self.vendor / 'catalog.csv'
        path.write_bytes(path.read_bytes().replace(b'\n', b'\r\n'))
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'differs from its rendering'):
            catalog.generate(self.vendor, check=True)
        self.assertEqual(self.snapshot(), before)

    def test_unmatched_annotation_is_rejected_and_preserves_files(self):
        path = self.vendor / 'uprev-maps.csv'
        text = path.read_text(encoding='utf-8')
        self.assertIn('Calculated Load', text)
        path.write_text(text.replace('Calculated Load', 'Calculated Load Updated'),
                        encoding='utf-8')
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'concept refers to names absent'):
            catalog.generate(self.vendor, check=True)
        self.assertEqual(self.snapshot(), before)

    def test_source_row_order_requires_regeneration_then_passes(self):
        path = self.vendor / 'uprev-maps.csv'
        lines = path.read_bytes().splitlines(keepends=True)
        lines[1], lines[2] = lines[2], lines[1]
        path.write_bytes(b''.join(lines))
        with self.assertRaisesRegex(ValueError, 'differs from its rendering'):
            catalog.generate(self.vendor, check=True)
        catalog.generate(self.vendor)
        regenerated = self.snapshot()
        catalog.generate(self.vendor, check=True)
        self.assertEqual(self.snapshot(), regenerated)

    def test_throttle_a_keeps_the_effective_dictionary_link(self):
        rows = catalog.build(self.vendor)
        links = [r['concept'] for r in rows
                 if r['vendor'] == 'uprev' and r['name'] == 'Throttle A']
        self.assertEqual(links, ['torque-demand'])

    def test_import_does_not_write(self):
        with mock.patch.object(Path, 'write_bytes') as write:
            importlib.reload(catalog)
        write.assert_not_called()

    def test_cli_failure_has_nonzero_status_and_preserves_files(self):
        (self.vendor / 'catalog.csv').write_bytes(b'stale\n')
        before = self.snapshot()
        generate = catalog.generate
        with mock.patch.object(catalog, 'generate',
                               side_effect=lambda **kw: generate(self.vendor, **kw)):
            with contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(catalog.main(['--check']), 1)
        self.assertIn('make vendor-catalog', errors.getvalue())
        self.assertEqual(self.snapshot(), before)


if __name__ == '__main__':
    unittest.main()
