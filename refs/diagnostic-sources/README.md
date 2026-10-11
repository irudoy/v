# Pinned public diagnostic sources

The submodules in this directory retain the original inputs of the 370Z CAN
Logger and ecudocs diagnostic projections. Their Git revisions are pinned by
the superproject gitlinks and checked by each importer against its `REVISION`.
The importers also reject locally modified selected source files.

`make setup` initializes these sources through the repository's standard
submodule workflow. `make check` compares every CSV/JSONL output through the
same production importers without executing source-project code:

```bash
uv run python tools/diagnostics/import_370z_logger.py --check
uv run python tools/diagnostics/import_ecudocs.py --check
```

Remove `--check` to regenerate a projection from the same pinned source. An
explicit source-directory argument selects another checkout with the same
required revision and unchanged input files. The source pack, fragments, and
applicability levels remain those of the original corpus.
