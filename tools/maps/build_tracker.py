#!/usr/bin/env python3
"""Сборка ledger'а карт JK03A.maps.csv из переписи MapInventory.

Перепись (defs/reference/JK03A.map_inventory.csv) снимается Ghidra-скриптом
MapInventory.java по kernel'у 0x26944 и содержит все ссылки на обёртки-
интерполяторы. Строки reftype=DATA - это pool-слоты с адресом обёртки, а не
места вызова; в ценз карт входят только is_call=true.

Скрипт merge-aware: механические колонки (обёртка, размерность, оси, аксессоры,
число сайтов) пересобираются из переписи, а разметка (status/name/note)
переносится из существующего ledger'а. Значит после повторного прогона
MapInventory прогресс не теряется.

Запуск: python3 tools/maps/build_tracker.py
"""
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CENSUS = os.path.join(ROOT, "defs", "reference", "JK03A.map_inventory.csv")
TRACKER = os.path.join(ROOT, "defs", "JK03A.maps.csv")

FIELDS = ["table", "wrapper", "dim", "axis_x", "axis_y", "accessors", "sites",
          "status", "name", "note"]

# Размерность по обёртке. Доказано трейсом (см. JK03A.notes.md, разделы
# "Интерполяторный кластер" и "Оси карт"): константа в обёртке = размер оси.
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
# status: in-def | identified | geometry | not-a-map | unopened | unresolved
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
}

# Карты вне kernel-переписи: читаются не через интерполятор, поэтому в
# MapInventory не попадают, но в дефе присутствуют.
EXTRA = [{
    "table": "00008fdc", "wrapper": "-", "dim": "2-cell", "axis_x": "", "axis_y": "",
    "accessors": "00047a56", "sites": "0", "status": "in-def",
    "name": "Rev Limit - Fuel Cut Speed",
    "note": "не через kernel: прямой word-компаратор vs 0xFFFF266E (rpm/12.5), "
            "пороги 0x8fdc=7625/0x8fde=6600 rpm, выбор 0xFFFF246D bit7",
}]


def join_uniq(values):
    seen = []
    for v in values:
        if v and v not in seen:
            seen.append(v)
    return ";".join(seen)


def main():
    with open(CENSUS, newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r["is_call"] == "true"]

    # Группировка: разрешённые таблицы по адресу, неразрешённые - по сайту вызова.
    groups = {}
    for r in rows:
        key = r["r4"] if r["r4"] else "@" + r["from"]
        groups.setdefault(key, []).append(r)

    out = []
    for key, grp in groups.items():
        resolved = not key.startswith("@")
        wrapper = join_uniq(g["wrapper"] for g in grp)
        dim = join_uniq(WRAPPER_DIM.get(g["wrapper"], "?") for g in grp)
        status, name, note = SEED.get(key, ("", "", ""))
        if not status:
            status = "unopened" if resolved else "unresolved"
        if not resolved:
            note = note or "backtrack не снял r4: таблица определяется вручную по аксессору"
        out.append({
            "table": key if resolved else "",
            "wrapper": wrapper,
            "dim": dim,
            "axis_x": join_uniq(g["r5"] for g in grp),
            "axis_y": join_uniq(g["r6"] for g in grp),
            "accessors": join_uniq(g["from_func"] for g in grp if g["from_func"] != "?")
                         or join_uniq("@" + g["from"] for g in grp),
            "sites": str(len(grp)),
            "status": status,
            "name": name,
            "note": note,
        })
    out.extend(EXTRA)

    # Перенос разметки из существующего ledger'а: правки status/name/note переживают
    # пересборку механических колонок.
    if os.path.exists(TRACKER):
        with open(TRACKER, newline="") as fh:
            prev = {r["table"] or "@" + r["accessors"]: r for r in csv.DictReader(fh)}
        for row in out:
            key = row["table"] or "@" + row["accessors"]
            old = prev.get(key)
            if old and old.get("status") not in ("", "unopened", "unresolved"):
                row["status"] = old["status"]
                row["name"] = old["name"]
                row["note"] = old["note"]

    order = {"in-def": 0, "identified": 1, "geometry": 2, "not-a-map": 3,
             "unopened": 4, "unresolved": 5}
    out.sort(key=lambda r: (order.get(r["status"], 9), r["dim"], r["table"]))

    with open(TRACKER, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)

    tally = {}
    for r in out:
        tally[r["status"]] = tally.get(r["status"], 0) + 1
    total = len(out)
    done = tally.get("in-def", 0)
    print(f"{TRACKER}: {total} записей")
    for k in sorted(tally, key=lambda s: order.get(s, 9)):
        print(f"  {k:11s} {tally[k]}")
    print(f"закрыто (in-def): {done}/{total}")


if __name__ == "__main__":
    main()
