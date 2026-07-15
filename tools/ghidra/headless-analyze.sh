#!/usr/bin/env bash
# Обёртка Ghidra analyzeHeadless с JDK 21.
# Системный JAVA_HOME может указывать на JDK 17 (Ghidra 12.x требует 21 и без TTY
# падает вместо запроса пути). brew-обёртка bin/ghidraRun ставит JDK 21 сама, а
# support/analyzeHeadless вызывается напрямую и системный JAVA_HOME перекрывает.
#
# Использование:
#   tools/ghidra/headless-analyze.sh <project_dir> <project_name> -import <file> [опции]
# Пример (импорт дампа как SH-2E ядро, вариант SH-2A с FPU, big-endian):
#   tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
#     -import rom-images/1ND0A_Stock.bin \
#     -processor "SuperH:BE:32:SH-2A" -loader BinaryLoader -loader-baseAddr 0x0
set -euo pipefail
JAVA_HOME="$(brew --prefix openjdk@21)/libexec/openjdk.jdk/Contents/Home"
export JAVA_HOME
exec "$(brew --prefix ghidra)/libexec/support/analyzeHeadless" "$@"
