#!/usr/bin/env bash
# Ghidra analyzeHeadless wrapper with explicit installation paths.
# GHIDRA_HOME selects Ghidra; JAVA_HOME selects its JDK. Unset paths use the
# Homebrew installations of Ghidra and JDK 21.
#
# Usage:
#   tools/ghidra/headless-analyze.sh <project_dir> <project_name> -import <file> [options]
# Example: import a dump as a big-endian SH-2E core using the SH-2A FPU variant:
#   tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
#     -import rom-images/23710-1ND0A/11ND0A-20260715-stock.bin \
#     -processor "SuperH:BE:32:SH-2A" -loader BinaryLoader -loader-baseAddr 0x0
set -euo pipefail

# The tracked exports, symbol names, and decompiler output belong to one Ghidra
# release. The knowledge tools read this pin when validating exports.
GHIDRA_VERSION=12.1.4

homebrew_prefix() {
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is unavailable; set GHIDRA_HOME and JAVA_HOME explicitly." >&2
    return 1
  fi
  brew --prefix "$1"
}

if [ -z "${GHIDRA_HOME:-}" ]; then
  GHIDRA_HOME="$(homebrew_prefix ghidra)/libexec"
fi
if [ ! -r "$GHIDRA_HOME/Ghidra/application.properties" ] || \
   [ ! -x "$GHIDRA_HOME/support/analyzeHeadless" ]; then
  echo "GHIDRA_HOME does not name a usable Ghidra installation: $GHIDRA_HOME" >&2
  exit 1
fi
INSTALLED="$(sed -n 's/^application\.version=//p' \
  "$GHIDRA_HOME/Ghidra/application.properties")"
if [ "$INSTALLED" != "$GHIDRA_VERSION" ]; then
  echo "Ghidra $GHIDRA_VERSION is required, found ${INSTALLED:-none}." >&2
  echo "Reanalyze the project and update the pin before using the exports." >&2
  exit 1
fi

if [ -z "${JAVA_HOME:-}" ]; then
  JAVA_HOME="$(homebrew_prefix openjdk@21)/libexec/openjdk.jdk/Contents/Home"
fi
if [ ! -x "$JAVA_HOME/bin/java" ]; then
  echo "JAVA_HOME does not name a usable JDK installation: $JAVA_HOME" >&2
  exit 1
fi
export JAVA_HOME
exec "$GHIDRA_HOME/support/analyzeHeadless" "$@"
