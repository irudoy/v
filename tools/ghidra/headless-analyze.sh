#!/usr/bin/env bash
# Ghidra analyzeHeadless wrapper using JDK 21.
# System JAVA_HOME may point to JDK 17. Ghidra 12.x requires 21 and fails without
# a TTY instead of asking for a path. Homebrew's bin/ghidraRun wrapper selects
# JDK 21 itself, while support/analyzeHeadless is called directly and would
# inherit system JAVA_HOME.
#
# Usage:
#   tools/ghidra/headless-analyze.sh <project_dir> <project_name> -import <file> [options]
# Example: import a dump as a big-endian SH-2E core using the SH-2A FPU variant:
#   tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
#     -import rom-images/23710-1ND0A/11ND0A-20260715-stock.bin \
#     -processor "SuperH:BE:32:SH-2A" -loader BinaryLoader -loader-baseAddr 0x0
set -euo pipefail

# The tracked exports, symbol names, and decompiler output belong to one Ghidra
# release. An unnoticed upgrade changes them silently, so the installation is
# pinned here and `tools/README.md` carries the same version under a gate.
GHIDRA_VERSION=12.1.4

GHIDRA_HOME="$(brew --prefix ghidra)/libexec"
INSTALLED="$(sed -n 's/^application\.version=//p' \
  "$GHIDRA_HOME/Ghidra/application.properties")"
if [ "$INSTALLED" != "$GHIDRA_VERSION" ]; then
  echo "Ghidra $GHIDRA_VERSION is required, found ${INSTALLED:-none}." >&2
  echo "Reanalyze the project and update the pin before using the exports." >&2
  exit 1
fi

JAVA_HOME="$(brew --prefix openjdk@21)/libexec/openjdk.jdk/Contents/Home"
export JAVA_HOME
exec "$GHIDRA_HOME/support/analyzeHeadless" "$@"
