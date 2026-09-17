#!/usr/bin/env bash
# On-demand decompilation and function listings of a registered stock ROM
# through headless Ghidra. No CodeBrowser window or MCP bridge is involved.
#
# Usage:
#   tools/ghidra/decompile.sh [-r ROM] [-o OUTDIR] [-l] [-f] <addr> [<addr>...]
#
#   -r ROM     ROM key from the image registry (default JK08A). The Ghidra
#              program name is the file name of the registered stock image.
#   -o OUTDIR  output directory (default ~/tools/ghidra-projects/export-<ROM>)
#   -l         also write funclisting_<addr>.txt through DumpFuncListing.java
#   -f         rerun even when the outputs already exist
#
# Addresses are hexadecimal without 0x, as in funcs.csv. Existing
# decomp_<addr>.c and funclisting_<addr>.txt files are reused, so a repeated
# request costs nothing; a headless run with missing files takes a few
# seconds. Output paths are printed one per line.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_DIR="${GHIDRA_PROJECT_DIR:-$HOME/tools/ghidra-projects}"
PROJECT_NAME="${GHIDRA_PROJECT_NAME:-vq-hr}"
rom="JK08A"
outdir=""
listings=0
force=0

while getopts "r:o:lf" option; do
    case "$option" in
        r) rom="$OPTARG" ;;
        o) outdir="$OPTARG" ;;
        l) listings=1 ;;
        f) force=1 ;;
        *) echo "usage: $0 [-r ROM] [-o OUTDIR] [-l] [-f] <addr>..." >&2; exit 2 ;;
    esac
done
shift $((OPTIND - 1))
if [ "$#" -eq 0 ]; then
    echo "usage: $0 [-r ROM] [-o OUTDIR] [-l] [-f] <addr>..." >&2
    exit 2
fi
[ -n "$outdir" ] || outdir="$PROJECT_DIR/export-$rom"
mkdir -p "$outdir"

program="$(cd "$ROOT" && uv run --quiet python -c "
import os, sys
from tools.mapkit import rom
print(os.path.basename(rom.load(sys.argv[1]).path))
" "$rom")"

declare -a addresses=()
declare -a decompile=()
declare -a listing=()
for raw in "$@"; do
    addr="$(printf '%08x' "0x${raw#0x}")"
    addresses+=("$addr")
    if [ "$force" -eq 1 ] || [ ! -s "$outdir/decomp_$addr.c" ]; then
        decompile+=("$addr")
    fi
    if [ "$listings" -eq 1 ] && { [ "$force" -eq 1 ] || [ ! -s "$outdir/funclisting_$addr.txt" ]; }; then
        listing+=("$addr")
    fi
done

if [ "${#decompile[@]}" -gt 0 ] || [ "${#listing[@]}" -gt 0 ]; then
    declare -a scripts=()
    if [ "${#decompile[@]}" -gt 0 ]; then
        scripts+=(-postScript DecompileFuncs.java "$outdir" "${decompile[@]}")
    fi
    if [ "${#listing[@]}" -gt 0 ]; then
        scripts+=(-postScript DumpFuncListing.java "$outdir" "${listing[@]}")
    fi
    log="$(mktemp -t ghidra-decompile.XXXXXX)"
    if ! "$ROOT/tools/ghidra/headless-analyze.sh" "$PROJECT_DIR" "$PROJECT_NAME" \
        -process "$program" -noanalysis -readOnly \
        -scriptPath "$ROOT/tools/ghidra" "${scripts[@]}" > "$log" 2>&1; then
        echo "headless Ghidra failed; log: $log" >&2
        exit 1
    fi
    rm -f "$log"
fi

status=0
for addr in "${addresses[@]}"; do
    if [ -s "$outdir/decomp_$addr.c" ]; then
        echo "$outdir/decomp_$addr.c"
    else
        echo "no function at $addr in $program" >&2
        status=1
    fi
    if [ "$listings" -eq 1 ]; then
        if [ -s "$outdir/funclisting_$addr.txt" ]; then
            echo "$outdir/funclisting_$addr.txt"
        else
            status=1
        fi
    fi
done
exit "$status"
