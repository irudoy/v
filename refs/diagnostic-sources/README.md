# Retained public diagnostic sources

These tracked snapshots retain the original inputs of the 370Z CAN Logger and
ecudocs diagnostic projections. Each `source.toml` records the upstream URL,
Git revision, license and SHA-256 of every retained file. The importers check
the exact source identity, file inventory and bytes before building a catalog.

`370z-can-logger/` retains the consumed `candata/` CSV files, decoder source
and MIT license. `ecudocs/` retains
`public/ecus/N_P32M_ECM_TR25_20080313.json` and the GPL-3.0 license. Original
paths and file bytes preserve document and fragment provenance. Decoder source
is parsed as text; source-project code is not executed.

`make check` compares every CSV/JSONL output through the production importers:

```bash
uv run python tools/diagnostics/import_370z_logger.py --check
uv run python tools/diagnostics/import_ecudocs.py --check
```

Remove `--check` to regenerate a projection from the same retained source. An
explicit source-directory argument selects an external Git checkout with the
required revision and unchanged selected input files. A manifest in an
external directory does not replace that Git check. Source packs, fragments
and applicability levels retain the original corpus scope.

Snapshots are ordinary repository files. Restore a missing or damaged file
from the repository; `make setup` initializes only the definition submodules.
