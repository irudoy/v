#!/usr/bin/env python3
"""Сборка ledger'а карт JK03A.maps.csv из переписей обоих семейств доступа.

Карты в JK03A читаются двумя независимыми механизмами; переписи снимаются
разными Ghidra-скриптами и не пересекаются ни таблицами, ни сайтами вызова:

- interp (defs/reference/JK03A.map_inventory.csv, MapInventory.java по kernel'у
  0x26944): обёртка по размерности + явные указатели осей в r5/r6. Строки
  reftype=DATA - это pool-слоты с адресом обёртки, а не места вызова; в ценз
  входят только is_call=true.
- direct (defs/reference/JK03A.direct_lookup_inventory.csv,
  DirectLookupInventory.java по примитиву 0x26370): обёрток нет, аксессор зовёт
  примитив напрямую, указателя оси нет. Ось неявная: 8 точек с шагом 32 по сырому
  байту 0..224, значения - беззнаковые байты. См. JK03A.notes.md, раздел
  "Прямой lookup 0x26370".

Скрипт merge-aware: механические колонки (семейство, вход, размерность, оси,
значения, аксессоры, число сайтов) пересобираются из переписей, а разметка
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

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CENSUS_INTERP = os.path.join(ROOT, "defs", "reference", "JK03A.map_inventory.csv")
CENSUS_DIRECT = os.path.join(ROOT, "defs", "reference", "JK03A.direct_lookup_inventory.csv")
TRACKER = os.path.join(ROOT, "defs", "JK03A.maps.csv")

FIELDS = ["table", "family", "via", "dim", "axis_x", "axis_y", "vals",
          "accessors", "sites", "status", "name", "note"]

# Размерность по обёртке interp-семейства. Доказано трейсом (см. JK03A.notes.md,
# разделы "Интерполяторный кластер" и "Оси карт"): константа в обёртке = размер оси.
# Обёртки без записи - размерность ещё не снята.
WRAPPER_DIM = {
    "00026084": "4x4",
    "00026140": "8x8",
    "000261b8": "16x16",
    "000261f0": "16x16",
    "00026320": "16x16",
    "00026474": "8-wide",
    "000264a0": "1D-16",
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

# Карты вне обеих переписей: читаются не через таблицу-lookup, поэтому ни один
# ценз их не видит, но в дефе присутствуют.
EXTRA = [{
    "table": "00008fdc", "family": "compare", "via": "-", "dim": "2-cell",
    "axis_x": "", "axis_y": "", "vals": "7625 6600",
    "accessors": "00047a56", "sites": "0", "status": "in-def",
    "name": "Rev Limit - Fuel Cut Maximum",
    "note": "не через lookup: прямой word-компаратор vs 0xFFFF266E (rpm/12.5), пороги "
            "0x8fdc=7625 (отсечка)/0x8fde=6600 (восстановление), селектор 0xFFFF246D "
            "bit7; имя пары по ProECU [CANDIDATE]",
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
    with open(CENSUS_INTERP, newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r["is_call"] == "true"]
    out = []
    for key, grp in group(rows, lambda r: r["r4"] or "@" + r["from"]).items():
        out.append({
            "table": key,
            "family": "interp",
            "via": join_uniq(g["wrapper"] for g in grp),
            "dim": join_uniq(WRAPPER_DIM.get(g["wrapper"], "?") for g in grp),
            "axis_x": join_uniq(g["r5"] for g in grp),
            "axis_y": join_uniq(g["r6"] for g in grp),
            "vals": "",
            "accessors": join_uniq(g["from_func"] for g in grp if g["from_func"] != "?")
                         or join_uniq("@" + g["from"] for g in grp),
            "sites": str(len(grp)),
        })
    return out


def load_direct():
    with open(CENSUS_DIRECT, newline="") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for key, grp in group(rows, lambda r: r["table"] or "@" + r["from"]).items():
        out.append({
            "table": key,
            "family": "direct",
            "via": "00026370",
            "dim": "1D-8",
            "axis_x": "implicit-32",   # 8 точек, шаг 32 по сырому байту 0..224
            "axis_y": "",
            "vals": join_uniq(g["vals"] for g in grp),
            "accessors": join_uniq(g["from_func"] for g in grp if g["from_func"] != "?")
                         or join_uniq("@" + g["from"] for g in grp),
            "sites": str(len(grp)),
        })
    return out


def main():
    out = load_interp() + load_direct()
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
