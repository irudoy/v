#!/usr/bin/env bash
# Export the L0 of one layout into l0/<layout>/ with its manifest.
#
# Usage:
#   tools/ghidra/export-l0.sh <layout> [--check] [--jobs N] [--stage DIR] [--from-stage DIR]
#                             [--batch FILE]
#                             [--family-draft FILE [--interp-draft FILE]]
#
#   --check           export into a temporary directory and compare the result
#                     byte for byte with the tracked files
#   --jobs N          run N headless sessions at once, each on a copy of the
#                     Ghidra project, because a project admits one process
#   --stage DIR       keep the raw headless export in DIR
#   --from-stage DIR  normalize a raw export from DIR instead of running Ghidra
#   --batch FILE      plan the census from the registry that the kb batch FILE
#                     renders, so the census of a kernel that the batch adds
#                     precedes `kb apply FILE`
#   --family-draft FILE  select the layout proposed by `kb family new --draft`
#   --interp-draft FILE  use the draft census registry of that proposed layout
#
# The layout's L0 image comes from the published or proposed family registry.
# The Ghidra project index supplies the program, verified by SHA-256. The
# census kernels come from the interpolation registry that tools/kb/config.toml
# names for the layout, or with --batch from the registry that the batch
# renders. tools/kb/SPEC.md section 8 defines the files, the normal form, and
# the manifest.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
exec uv run --quiet python -m kb.l0 "$@"
