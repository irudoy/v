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
JAVA_HOME="$(brew --prefix openjdk@21)/libexec/openjdk.jdk/Contents/Home"
export JAVA_HOME
exec "$(brew --prefix ghidra)/libexec/support/analyzeHeadless" "$@"
