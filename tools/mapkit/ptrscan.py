#!/usr/bin/env python3
# Кто указывает на адрес: скан образа, без Ghidra и без проекта.
#
# Дополняет FindTableRefs.java, а не заменяет: тот перечисляет ссылки, разрешённые
# анализом, и потому знает, ссылка это или совпадение, но видит только размеченный код.
# Скан по образу не знает ничего, зато видит всё - включая пулы под кодом, который Ghidra
# функциями не разметила (JK03A: 38627 инструкций в 494 участках до Stage 0). Отсюда его
# место: первый вопрос о незнакомом массиве и проверка на дампе, для которого проекта нет.
#
# Ищет обе формы константы. mov.l берёт 32-битное слово по 4-байтовой границе - обычный
# указатель пула. mov.w берёт 16-битное по 2-байтовой, и адрес калибровки в него влезает
# (0xB33A, 0x8FDC): эталонный backtrack читал такую константу 32-битной и ошибался на пяти
# сайтах каталога.
#
# Совпадение отличается от указателя не формой, а тем, кто рядом: 16-битных слов со
# значением из диапазона в мегабайте образа тысячи. Поэтому выдача - кандидаты, а решает
# дизассемблер по месту (tools/ghidra/DumpListing.java).
#
# Запуск: uv run --no-project python tools/mapkit/ptrscan.py [<rom>] <addr> [<addr_hi>]
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import rom as romkit          # noqa: E402 - пакет соседний, не установленный


def main():
    args = sys.argv[1:]
    try:
        known = {r["rom"] for r in romkit.registry() if r["rom"]}
    except ValueError as e:
        sys.exit(str(e))
    rom = args.pop(0) if args and args[0] in known else "JK03A"
    if not args:
        sys.exit(f"нужен адрес: ptrscan.py [<rom>] <addr> [<addr_hi>]; метки ROM: "
                 f"{', '.join(sorted(known))}")
    lo = int(args[0], 16)
    hi = int(args[1], 16) if len(args) > 1 else lo
    if hi < lo:
        sys.exit(f"диапазон пуст: {lo:#x}..{hi:#x}")
    try:
        img = romkit.load(rom)
    except ValueError as e:
        sys.exit(str(e))

    hits = img.scan(lo, hi)
    span = "" if lo == hi else f"..{hi:#07x}"
    print(f"{rom} ({os.path.basename(img.path)}): {lo:#07x}{span} - "
          f"{len(hits)} кандидатов")
    by_kind = {}
    for h in hits:
        by_kind[h["kind"]] = by_kind.get(h["kind"], 0) + 1
    for kind in ("mov.l", "mov.w"):
        if kind in by_kind:
            print(f"  {kind}: {by_kind[kind]}")
    for h in hits:
        print(f"  {h['at']:#08x}  {h['kind']:<5} -> {h['value']:#07x}")
    if by_kind.get("mov.w"):
        print("16-битные попадания - кандидаты, а не ссылки: слов с таким значением в "
              "образе много. Решает листинг по месту (ghidra/DumpListing.java).")


if __name__ == "__main__":
    main()
