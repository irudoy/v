#!/usr/bin/env bash
# On-demand decompilation and function listings of a registered stock ROM
# through headless Ghidra. No CodeBrowser window or MCP bridge is involved.
#
# Usage:
#   tools/ghidra/decompile.sh [-r ROM] [-p PROGRAM] [-o OUTDIR] [-l] [-f] <addr> [<addr>...]
#
#   -r ROM     ROM key from the image registry (default JK08A). The Ghidra
#              program is the one named after the registered stock image, or
#              else the only program of the project whose name contains the
#              ROM key.
#   -p PROGRAM Ghidra program name, overriding the lookup in the project index
#   -o OUTDIR  output directory (default ~/tools/ghidra-projects/export-<ROM>)
#   -l         also write funclisting_<addr>.txt through DumpFuncListing.java
#   -f         rerun even when the outputs already exist
#
# Addresses are hexadecimal without 0x, as in funcs.csv. Existing
# decomp_<addr>.c and funclisting_<addr>.txt files are reused, so a repeated
# request costs nothing; a headless run with missing files takes a few
# seconds. Output paths are printed one per line.
#
# Every headless run reads the executable SHA-256 that Ghidra recorded at
# import. Output reaches OUTDIR only when it equals the SHA-256 of the
# registered stock image, so a program under another name cannot stand in for
# a different dump.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_DIR="${GHIDRA_PROJECT_DIR:-$HOME/tools/ghidra-projects}"
PROJECT_NAME="${GHIDRA_PROJECT_NAME:-vq-hr}"
rom="JK08A"
program_override=""
outdir=""
listings=0
force=0

usage="usage: $0 [-r ROM] [-p PROGRAM] [-o OUTDIR] [-l] [-f] <addr>..."
while getopts "r:p:o:lf" option; do
    case "$option" in
        r) rom="$OPTARG" ;;
        p) program_override="$OPTARG" ;;
        o) outdir="$OPTARG" ;;
        l) listings=1 ;;
        f) force=1 ;;
        *) echo "$usage" >&2; exit 2 ;;
    esac
done
shift $((OPTIND - 1))
if [ "$#" -eq 0 ]; then
    echo "$usage" >&2
    exit 2
fi
[ -n "$outdir" ] || outdir="$PROJECT_DIR/export-$rom"
mkdir -p "$outdir"

resolved="$(cd "$ROOT" && uv run --quiet python -m tools.ghidra.program_name "$rom" \
    --project-dir "$PROJECT_DIR" --project-name "$PROJECT_NAME" \
    --program "$program_override")"
program="${resolved%%$'\t'*}"
image_sha256="${resolved##*$'\t'}"

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
    stage="$(mktemp -d -t ghidra-decompile-stage.XXXXXX)"
    trap 'rm -rf "$stage"' EXIT
    declare -a scripts=(-postScript ProgramSha256.java "$stage/program.sha256")
    if [ "${#decompile[@]}" -gt 0 ]; then
        scripts+=(-postScript DecompileFuncs.java "$stage" "${decompile[@]}")
    fi
    if [ "${#listing[@]}" -gt 0 ]; then
        scripts+=(-postScript DumpFuncListing.java "$stage" "${listing[@]}")
    fi
    log="$(mktemp -t ghidra-decompile.XXXXXX)"
    if ! "$ROOT/tools/ghidra/headless-analyze.sh" "$PROJECT_DIR" "$PROJECT_NAME" \
        -process "$program" -noanalysis -readOnly \
        -scriptPath "$ROOT/tools/ghidra" "${scripts[@]}" > "$log" 2>&1; then
        echo "headless Ghidra failed; log: $log" >&2
        exit 1
    fi
    program_sha256="$(tr -d '[:space:]' < "$stage/program.sha256" 2>/dev/null || true)"
    if [ -z "$program_sha256" ]; then
        echo "program $program is absent from the project or has no recorded SHA-256; log: $log" >&2
        exit 1
    fi
    if [ "$program_sha256" != "$image_sha256" ]; then
        echo "program $program holds $program_sha256, the registered $rom image is $image_sha256" >&2
        exit 1
    fi
    for addr in "${addresses[@]}"; do
        for staged in "$stage/decomp_$addr.c" "$stage/funclisting_$addr.txt"; do
            if [ -s "$staged" ]; then
                mv -f "$staged" "$outdir/"
            fi
        done
    done
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
