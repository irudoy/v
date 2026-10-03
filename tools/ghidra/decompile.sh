#!/usr/bin/env bash
# On-demand code of registered stock ROMs through the primary read-only runner.
# Usage: decompile.sh [-r ROM] [-p PROGRAM] [-o OUTDIR] [-l] [-f] <addr>...
# Verified outputs and their input key replace the cache together. Preparation
# failures leave accepted outputs untouched and retain the primary process log.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
exec uv run --quiet python -m tools.ghidra.decompile "$@"
