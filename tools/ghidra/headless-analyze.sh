#!/usr/bin/env bash
# Ghidra analyzeHeadless wrapper with explicit installation paths.
# GHIDRA_HOME selects Ghidra; GHIDRA_JAVA_HOME selects its JDK. Unset paths use
# the Homebrew installations of Ghidra and JDK 21. The inherited JAVA_HOME is
# ignored because it can select an older JDK used by unrelated applications.
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
GHIDRA_MIN_JAVA_VERSION=21

homebrew_prefix() {
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is unavailable; set GHIDRA_HOME and GHIDRA_JAVA_HOME explicitly." >&2
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

if [ -n "${GHIDRA_JAVA_HOME:-}" ]; then
  JAVA_HOME="$GHIDRA_JAVA_HOME"
else
  JAVA_HOME="$(homebrew_prefix openjdk@21)/libexec/openjdk.jdk/Contents/Home"
fi
if [ ! -x "$JAVA_HOME/bin/java" ]; then
  echo "The selected Ghidra JDK has no executable bin/java: $JAVA_HOME" >&2
  echo "Set GHIDRA_JAVA_HOME to a usable JDK installation." >&2
  exit 1
fi
if ! JAVA_DETAILS="$("$JAVA_HOME/bin/java" -XshowSettings:properties -version 2>&1)"; then
  echo "Cannot inspect the Ghidra JDK selected at $JAVA_HOME." >&2
  exit 1
fi
JAVA_SPECIFICATION="$(printf '%s\n' "$JAVA_DETAILS" | sed -n \
  's/^[[:space:]]*java\.specification\.version = \([^[:space:]]*\)[[:space:]]*$/\1/p')"
case "$JAVA_SPECIFICATION" in
  ''|*[!0-9]*) JAVA_MAJOR=0 ;;
  *) JAVA_MAJOR="$JAVA_SPECIFICATION" ;;
esac
if [ "$JAVA_MAJOR" -lt "$GHIDRA_MIN_JAVA_VERSION" ]; then
  echo "JDK $GHIDRA_MIN_JAVA_VERSION or newer is required for Ghidra; found ${JAVA_SPECIFICATION:-unknown} at $JAVA_HOME." >&2
  exit 1
fi
export JAVA_HOME
exec "$GHIDRA_HOME/support/analyzeHeadless" "$@"
