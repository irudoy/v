#!/usr/bin/env python3
"""Ledger карт defs/<rom>.maps.csv - проекция каталога из графа.

Система учёта - граф: карты, их входы интерполяции, оси и аксессоров кладёт туда
load_maps.py из переписей резолвера (Stage 3) и ручного слоя. Ledger - читаемый срез
этого каталога: worklist разбора, который виден в диффе и проходит ревью. Правится он
не правкой файла: геометрия входов живёт в defs/<rom>.interp.csv, находки - в
defs/<rom>.findings.csv, а этот скрипт только печатает то, что уже в графе.

Открытая работа - строки с уровнем candidate и пустой semantics. Отдельной колонки
status здесь нет: она была бы рендером уровня, роли и семантики, то есть копией
соседних колонок, а копия факта и есть то, из-за чего источники расходятся.

Колонка vals - диапазон ячеек, измеренный по образу (Stage 4). Она и делит открытую
работу: таблица 0..0 либо сплошь 0xFF стоит разбора иначе, чем поверхность значений.

Запуск: uv run --no-project --with neo4j python tools/maps/build_tracker.py [<rom>]
"""
import csv
import os
import sys
from neo4j import GraphDatabase

BOLT = "bolt://localhost:7687"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FIELDS = ["table", "family", "via", "kernel", "dim", "storagetype", "vals", "scaling",
          "axis_x", "axis_y", "accessors", "sites", "confidence", "role", "semantics",
          "note"]

# Сверху - разобранное, снизу - открытое: сначала таблицы по уровню и наличию семантики,
# затем базы, тюнингу не подлежащие (порог компаратора, отключённая калибровкой ветка).
LEVEL_ORDER = {"silicon": 0, "code": 1, "candidate": 2, "pattern": 3}
ROLE_ORDER = {"table": 0, "threshold": 1, "dead": 2}

QUERY = """
MATCH (m:Map {rom:$rom})
OPTIONAL MATCH (m)-[:VIA]->(w:Interp {rom:$rom})
OPTIONAL MATCH (w)-[:KERNEL]->(k:Interp {rom:$rom})
OPTIONAL MATCH (m)-[:AXIS_X]->(ax:Axis {rom:$rom})
OPTIONAL MATCH (m)-[:AXIS_Y]->(ay:Axis {rom:$rom})
OPTIONAL MATCH (f:Func {rom:$rom})-[a:ACCESSES]->(m)
RETURN m.addr AS table, m.family AS family, m.width AS width, m.height AS height,
       m.storagetype AS storagetype, m.confidence AS confidence, m.role AS role,
       m.semantics AS semantics, m.note AS note, m.vmin AS vmin, m.vmax AS vmax,
       m.units AS units, m.scale_expr AS scale_expr, m.scale_conf AS scale_conf,
       collect(DISTINCT w.addr) AS via, collect(DISTINCT k.addr) AS kernel,
       collect(DISTINCT ax.addr) AS axis_x, collect(DISTINCT ay.addr) AS axis_y,
       collect(DISTINCT f.addr) AS accessors, count(DISTINCT a) AS sites
"""


def shape(width, height):
    """Форма таблицы: у 2D - сетка, у 1D - число точек оси."""
    if width is None:
        return ""
    return f"{width}x{height}" if height else f"1D-{width}"


def scaling(r):
    """Шкала одной строкой; уровень при ней - её собственный, не уровень карты."""
    if not r["scale_expr"] or r["scale_expr"].strip() == "x":
        return ""
    return (f"{r['scale_expr']} {r['units']}"
            + (f" [{r['scale_conf']}]" if r["scale_conf"] else ""))


def project(rows):
    out = [{
        "table": r["table"],
        "family": r["family"],
        "via": ";".join(sorted(r["via"])),
        "kernel": ";".join(sorted(r["kernel"])),
        "dim": shape(r["width"], r["height"]),
        "storagetype": r["storagetype"] or "",
        "vals": f"{r['vmin']}..{r['vmax']}",
        "scaling": scaling(r),
        "axis_x": ";".join(sorted(r["axis_x"])),
        "axis_y": ";".join(sorted(r["axis_y"])),
        "accessors": ";".join(sorted(r["accessors"])),
        "sites": str(r["sites"]),
        "confidence": r["confidence"],
        "role": r["role"],
        "semantics": r["semantics"],
        "note": r["note"],
    } for r in rows]
    out.sort(key=lambda r: (ROLE_ORDER.get(r["role"], 9),
                            LEVEL_ORDER.get(r["confidence"], 9),
                            r["semantics"] == "", r["family"], r["dim"], r["table"]))
    return out


def report(out, tracker):
    tally = {}
    for r in out:
        tally[r["confidence"]] = tally.get(r["confidence"], 0) + 1
    fam, role = {}, {}
    for r in out:
        fam[r["family"]] = fam.get(r["family"], 0) + 1
        role[r["role"]] = role.get(r["role"], 0) + 1
    print(f"{os.path.relpath(tracker)}: {len(out)} карт")
    print("  уровни: " + ", ".join(f"{k}={tally[k]}" for k in LEVEL_ORDER if k in tally))
    print("  роли: " + ", ".join(f"{k}={role[k]}" for k in ROLE_ORDER if k in role))
    print("  семейства: " + ", ".join(f"{k}={fam[k]}" for k in sorted(fam)))
    named = sum(1 for r in out if r["semantics"])
    empty = sum(1 for r in out if not r["via"] and not r["accessors"])
    print(f"  с семантикой: {named}/{len(out)}")
    print(f"  открыто (candidate без семантики): "
          f"{sum(1 for r in out if r['confidence'] == 'candidate' and not r['semantics'])}")
    if empty:
        print(f"ВНИМАНИЕ: {empty} карт без входа и аксессора - осиротевшие узлы графа")


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else "JK03A"
    tracker = os.path.join(ROOT, "defs", f"{rom}.maps.csv")

    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    with driver.session() as s:
        rows = [r.data() for r in s.run(QUERY, rom=rom)]
    driver.close()
    if not rows:
        sys.exit(f"в графе нет карт rom={rom} - слой строит tools/memgraph/load_maps.py")

    out = project(rows)
    with open(tracker, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)
    report(out, tracker)


if __name__ == "__main__":
    main()
