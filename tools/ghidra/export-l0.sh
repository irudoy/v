#!/usr/bin/env bash
# Export the L0 of one layout into l0/<layout>/ with its manifest.
#
# Usage:
#   tools/ghidra/export-l0.sh <layout> [--check] [--jobs N] [--stage DIR] [--from-stage DIR]
#
#   --check           export into a temporary directory and compare the result
#                     byte for byte with the tracked files
#   --jobs N          run N headless sessions at once, each on a copy of the
#                     Ghidra project, because a project admits one process
#   --stage DIR       keep the raw headless export in DIR
#   --from-stage DIR  normalize a raw export from DIR instead of running Ghidra
#
# The layout's L0 image comes from rom-images/homology.toml and its program
# from the Ghidra project index, verified by SHA-256 as decompile.sh does. The
# census kernels come from the interpolation registry that tools/kb/config.toml
# names for the layout. tools/kb/SPEC.md section 8 defines the files, the normal
# form, and the manifest.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
exec uv run --quiet python -m kb.l0 "$@"
