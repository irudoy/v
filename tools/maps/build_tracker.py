#!/usr/bin/env python3
"""Сборка ledger'а карт JK03A.maps.csv из переписей всех семейств доступа.

Карты в JK03A читаются библиотекой примитивов, занимающей 0x26000..0x26E00. У неё
39 точек входа (чётные значения, на которые ссылается код вне региона); 35 из них -
доступ к таблицам, 4 - арифметика и работа с RAM. Внутри региона живут ядра, finisher'ы
и цепочки сдвигов, которые прикладной код не зовёт. См. JK03A.notes.md, раздел
"Библиотека доступа к таблицам".

Семейства и их переписи (пересечений по таблицам между ними нет, это проверяется
на сборке):

- interp (MapInventory.java, по одному прогону на ядро): обёртка задаёт геометрию,
  оси передаются указателями в r5/r6, ядро ищет точку по массиву оси. Три ядра:
  0x26944 (ось - байты), 0x26984 и 0x26b84 (ось - слова). Строки reftype=DATA - это
  pool-слоты с адресом обёртки, а не места вызова; в ценз входят только is_call=true.
- direct (DirectLookupInventory.java, один прогон на весь банк): обёрток нет, аксессор
  зовёт примитив напрямую, массива оси нет. Ось неявная и равномерная: N точек с шагом
  step по сырому входу. Значения беззнаковые.
- прочее (EXTRA ниже): доступ вне обеих моделей, вносится вручную.

Скрипт merge-aware: механические колонки (семейство, вход, ядро, размерность, элемент,
оси, значения, аксессоры, число сайтов) пересобираются из переписей, а разметка
(status/name/note) сохраняется. Значит после повторного прогона переписей прогресс
не теряется.

Приоритет разметки: SEED этого файла -> существующий ledger -> статус по умолчанию.
SEED старше ledger'а намеренно: он живёт в коде, виден в диффах и проходит ревью,
поэтому исправление разметки в SEED обязано доходить до файла. Разметка, введённая
правкой самого ledger'а, сохраняется для всех ключей, которых нет в SEED.

Ключ строки - адрес таблицы; для сайтов, где backtrack не снял r4, ключ "@<сайт>"
(адрес сайта уникален, в отличие от функции-аксессора).

Запуск: python3 tools/maps/build_tracker.py
"""
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF = os.path.join(ROOT, "defs", "reference")
TRACKER = os.path.join(ROOT, "defs", "JK03A.maps.csv")

CENSUS_INTERP = {
    "00026944": "JK03A.map_inventory.26944.csv",
    "00026984": "JK03A.map_inventory.26984.csv",
    "00026b84": "JK03A.map_inventory.26b84.csv",
}
CENSUS_DIRECT = "JK03A.direct_lookup_inventory.csv"

FIELDS = ["table", "family", "via", "kernel", "dim", "elem", "axis_x", "axis_y",
          "vals", "accessors", "sites", "status", "name", "note"]

# Геометрия обёрток explicit-axis, снятая с кода каждой обёртки: клэмп в delay slot
# (MOV #imm,R4) задаёт число точек оси, шаг строки (MOV #imm,R5 либо константа пула) -
# ширину ряда. Правило воспроизводит все пять обёрток, размерность которых установлена
# независимым трейсом раньше: 0x26084=4x4, 0x26140=8x8, 0x261b8/0x261f0/0x26320=16x16.
# При word-оси клэмп задан в байтах, поэтому 14 = 2*7 - это 8 точек, а 30 = 2*15 - 16.
#
# elem - ширина и знак элемента. Для 1D-обёрток снимается прямо с их кода (MOV.B+EXTU.B
# либо MOV.W+EXTU.W). Для 2D-обёрток элемент читает общий 2D-finisher (0x26770, 0x26b28,
# 0x267cc): там путь точного попадания знаковый, а путь интерполяции маскирует значение
# 0x7f, и какой из них выбирается - не снято. Поэтому elem у 2D пуст: ширина и знак
# элемента 2D-карт остаются открытым вопросом.
WRAPPERS = {
    "00026084": ("4x4",   ""),
    "000260bc": ("4x4",   "s8"),   # без интерполяции: RTS + MOV.B @R4,R0 в delay slot
    "00026100": ("4x4",   ""),
    "00026140": ("8x8",   ""),
    "00026178": ("8x8",   ""),
    "000261b8": ("16x16", ""),
    "000261f0": ("16x16", ""),
    "00026230": ("16x16", ""),
    "00026270": ("8x8",   ""),
    "000262a8": ("16x16", ""),
    "000262e0": ("16x16", ""),     # оси разной ширины: клэмпы 15 (байт) и 30 (слово)
    "00026320": ("16x16", ""),
    "00026474": ("1D-8",  "u8"),
    "000264a0": ("1D-16", "u8"),
    "000264cc": ("1D-8",  "u16"),
    "000264f8": ("1D-16", "u16"),
    "00026524": ("1D-32", "u16"),
    "00026550": ("1D-16", "u8"),   # word-ось, байтовый элемент: SHLR R4 после ядра
    "000265f0": ("8x8",   ""),
    "00026628": ("16x16", ""),
    "00026660": ("16x16", ""),     # оси разной ширины: клэмпы 15 (байт) и 30 (слово)
    "000266bc": ("1D-8",  "u16"),
    "000266e8": ("1D-16", "u16"),
    "00026714": ("1D-32", "u16"),
}

# Разметка-затравка. Пополняется правкой самого ledger'а, не этого файла.
# status: in-def | identified | geometry | not-a-map | inactive | unopened | unresolved
#   inactive - таблица сослана кодом, но её ветка отключена калибровочным байтом
#   в ROM, поэтому в этой прошивке не читается: правка значений ни на что не влияет.
SEED = {
    "0000b81a": ("in-def", "Ignition Adj Map [always]",
                 "CONFIRMED: аксессор 0x82c8a, оси RPM 0x11b6b x нагрузка 0x11b8b"),
    "0000b61a": ("in-def", "Ignition Adj Map [flag=set]",
                 "CONFIRMED: выбор по gbr+0x93 bit0"),
    "0000b71a": ("in-def", "Ignition Adj Map [flag=clr]",
                 "CONFIRMED: выбор по gbr+0x93 bit0"),
    "0000b33a": ("in-def", "Target AFR - Power",
                 "CONFIRMED: 16x16, scaling 1881.6/x, плато 14.7 + обогащение 11.2"),
    "0000a29a": ("in-def", "Lambda Target - flat",
                 "CONFIRMED: 16x16, плоский 14.0..14.8"),
    "0000b23a": ("in-def", "Transient Fuel Corr - weight",
                 "CONFIRMED геометрия/оси; [CANDIDATE] единицы значений"),
    "0000ab0a": ("in-def", "Transient Fuel Corr - magnitude",
                 "CONFIRMED геометрия/оси; [CANDIDATE] единицы значений"),
    "0000a49a": ("geometry", "",
                 "4x4 через 0x26084, оси 0x11d00/0x11b67; семантика TBD"),
    "0000ab6a": ("geometry", "",
                 "4x4 через 0x26084, оси 0x11d00/0x11b67; семантика TBD"),
    "000129d2": ("geometry", "",
                 "1D-16 через 0x264a0, ось 0x11b7b; семантика TBD"),
    "0000abba": ("geometry", "",
                 "условный выбор карт через аксессор 0xa52e4; семантика TBD"),
    "0000abfa": ("geometry", "",
                 "условный выбор карт через аксессор 0xa52e4; семантика TBD"),
    "0001236a": ("identified", "Fuel enrichment vs MBT-like axis",
                 "CONFIRMED: ось 0x1238a (0..128 шаг 8), вход byte[0xFFFF11AE]; "
                 "питает топливо, не угол - разбор K2Y"),
    "0001261a": ("not-a-map", "RPM-window comparator (lo)",
                 "CONFIRMED: порог по оси RPM 0x1264a, ставит флаг; не карта угла"),
    "0001263a": ("not-a-map", "RPM-window comparator (hi)",
                 "CONFIRMED: порог по оси RPM 0x1264a, ставит флаг; не карта угла"),
    "00012cbe": ("not-a-map", "RPM-window comparator",
                 "CONFIRMED: то же семейство, что 0x1261a/0x1263a"),
    "000121fe": ("identified", "Over Run Fuel Cut threshold [CANDIDATE]",
                 "CONFIRMED: безусловный вызов из 0x5185c, вход byte[0xFFFF106F]; "
                 "[CANDIDATE] смысл - порог по ProECU-словарю, множитель не снят"),
    "00012206": ("inactive", "",
                 "CONFIRMED: вызов из 0x51700, вход byte[0xFFFF106F]; ветка выбрана "
                 "калибровкой byte[0x8d92] bit3=1 в пользу 0x121e6/0x121ae/0x121ce, "
                 "поэтому таблица не читается"),
}

# Карты вне обеих моделей ценза, вносятся вручную.
EXTRA = [{
    "table": "00008fdc", "family": "compare", "via": "-", "kernel": "-", "dim": "2-cell",
    "elem": "u16", "axis_x": "", "axis_y": "", "vals": "7625 6600",
    "accessors": "00047a56", "sites": "0", "status": "in-def",
    "name": "Rev Limit - Fuel Cut Maximum",
    "note": "не через lookup: прямой word-компаратор vs 0xFFFF266E (rpm/12.5), пороги "
            "0x8fdc=7625 (отсечка)/0x8fde=6600 (восстановление), селектор 0xFFFF246D "
            "bit7; имя пары по ProECU [CANDIDATE]",
}, {
    "table": "0000a8ea", "family": "direct-2d", "via": "00026040", "kernel": "-",
    "dim": "8x8", "elem": "", "axis_x": "implicit", "axis_y": "implicit", "vals": "",
    "accessors": "00052576", "sites": "1", "status": "geometry", "name": "",
    "note": "CONFIRMED: 2D с неявными осями - 0x26040 зовёт 0x26ae0 на каждую ось и "
            "0x26770 с шагом строки 8; входы byte[0xFFFF106F] и byte[0xFFFF10F0]; "
            "[OPEN] кодировка элемента (см. elem)",
}, {
    "table": "00009eda", "family": "direct-2d", "via": "00026040", "kernel": "-",
    "dim": "8x8", "elem": "", "axis_x": "implicit", "axis_y": "implicit", "vals": "",
    "accessors": "000526a0", "sites": "1", "status": "geometry", "name": "",
    "note": "CONFIRMED: тот же вход 0x26040, что и 0xa8ea, те же оси; "
            "[OPEN] кодировка элемента (см. elem)",
}]


def join_uniq(values):
    seen = []
    for v in values:
        if v and v not in seen:
            seen.append(v)
    return ";".join(seen)


def group(rows, key_of):
    out = {}
    for r in rows:
        out.setdefault(key_of(r), []).append(r)
    return out


def load_interp():
    out = []
    for kernel, fname in CENSUS_INTERP.items():
        with open(os.path.join(REF, fname), newline="") as fh:
            rows = [r for r in csv.DictReader(fh) if r["is_call"] == "true"]
        for key, grp in group(rows, lambda r: r["r4"] or "@" + r["from"]).items():
            geom = [WRAPPERS.get(g["wrapper"], ("?", "")) for g in grp]
            out.append({
                "table": key,
                "family": "interp",
                "via": join_uniq(g["wrapper"] for g in grp),
                "kernel": kernel,
                "dim": join_uniq(d for d, _ in geom),
                "elem": join_uniq(e for _, e in geom),
                "axis_x": join_uniq(g["r5"] for g in grp),
                "axis_y": join_uniq(g["r6"] for g in grp),
                "vals": "",
                "accessors": join_uniq(g["from_func"] for g in grp if g["from_func"] != "?")
                             or join_uniq("@" + g["from"] for g in grp),
                "sites": str(len(grp)),
            })
    return out


def load_direct():
    with open(os.path.join(REF, CENSUS_DIRECT), newline="") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for key, grp in group(rows, lambda r: r["table"] or "@" + r["from"]).items():
        out.append({
            "table": key,
            "family": "direct",
            "via": join_uniq(g["prim"] for g in grp),
            "kernel": "-",
            "dim": join_uniq("1D-" + g["points"] for g in grp),
            "elem": join_uniq("u%d" % (int(g["width"]) * 8) for g in grp),
            "axis_x": join_uniq("implicit-" + g["step"] for g in grp),
            "axis_y": "",
            "vals": join_uniq(g["vals"] for g in grp),
            "accessors": join_uniq(g["from_func"] for g in grp if g["from_func"] != "?")
                         or join_uniq("@" + g["from"] for g in grp),
            "sites": str(len(grp)),
        })
    return out


def main():
    out = load_interp() + load_direct()

    # Семейства не должны делить таблицу: у таблицы одна геометрия, и чтение её двумя
    # разными примитивами означало бы ошибку ценза, а не находку. Проверка держит это
    # утверждение фактом, а не допущением.
    seen = {}
    for row in out:
        if row["table"] in seen:
            other = seen[row["table"]]
            sys.exit("таблица %s в двух семействах: %s/%s и %s/%s" % (
                row["table"], other["family"], other["via"], row["family"], row["via"]))
        seen[row["table"]] = row

    for row in out:
        resolved = not row["table"].startswith("@")
        status, name, note = SEED.get(row["table"], ("", "", ""))
        row["status"] = status or ("unopened" if resolved else "unresolved")
        row["name"] = name
        row["note"] = note or ("" if resolved else
                               "backtrack не снял r4: таблица определяется вручную "
                               "по аксессору")
    out.extend(EXTRA)

    # Перенос разметки из существующего ledger'а: правки status/name/note переживают
    # пересборку механических колонок. Ключи из SEED не трогаются - там источник код.
    if os.path.exists(TRACKER):
        with open(TRACKER, newline="") as fh:
            prev = {r["table"]: r for r in csv.DictReader(fh)}
        for row in out:
            if row["table"] in SEED:
                continue
            old = prev.get(row["table"])
            if old and old.get("status") not in ("", "unopened", "unresolved"):
                row["status"] = old["status"]
                row["name"] = old["name"]
                row["note"] = old["note"]

    order = {"in-def": 0, "identified": 1, "geometry": 2, "not-a-map": 3,
             "inactive": 4, "unopened": 5, "unresolved": 6}
    out.sort(key=lambda r: (order.get(r["status"], 9), r["family"], r["dim"], r["table"]))

    with open(TRACKER, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)

    tally, fam = {}, {}
    for r in out:
        tally[r["status"]] = tally.get(r["status"], 0) + 1
        fam[r["family"]] = fam.get(r["family"], 0) + 1
    print(f"{TRACKER}: {len(out)} записей")
    for k in sorted(tally, key=lambda s: order.get(s, 9)):
        print(f"  {k:11s} {tally[k]}")
    print("  " + " ".join(f"{k}={v}" for k, v in sorted(fam.items())))
    print(f"закрыто (in-def): {tally.get('in-def', 0)}/{len(out)}")


if __name__ == "__main__":
    main()
