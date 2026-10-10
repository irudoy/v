"""Exact read-only comparisons through the diagnostic production writers."""

from pathlib import Path
import sys
import tempfile

from catalog import CatalogError, ROOT

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools import projection_check


def check(output, catalog, write):
    """Re-render CSV/JSONL outputs outside their destination and compare bytes."""
    with tempfile.TemporaryDirectory(prefix='vq-diagnostic-check-') as directory:
        rendered = Path(directory)
        write(rendered, catalog)
        expected = {path.name: path.read_bytes() for path in rendered.iterdir()}
        try:
            projection_check.compare(expected, output, ('*.csv', 'fragments.jsonl'),
                                     regenerate='rerun the same importer without --check')
        except ValueError as error:
            raise CatalogError(str(error)) from None
