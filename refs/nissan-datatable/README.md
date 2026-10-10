# Generic Nissan ECU register table

`NissanDatatable.pdf` is the immutable source of the
`generic-nissan-datatable-2003-v1` diagnostic dataset. `source.toml` binds its
filename, download URL, digest, and page count. The importer checks this pin
before extraction; the source and generated diagnostic rows retain the
`generic_legacy` applicability level.

Validate the source and every CSV/JSONL projection without replacing outputs:

```bash
uv run python tools/diagnostics/import_nissan_datatable.py --check
```

Regenerate with the same command without `--check`. Restore a missing source
from the declared URL and require its exact digest before extraction.
