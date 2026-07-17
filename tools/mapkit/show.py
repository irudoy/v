#!/usr/bin/env python3
# Печать карты либо оси в физических единицах: граф (адрес, форма, элемент, оси, шкала)
# плюс образ (значения). Инструмент разбора, не генератор: в git ничего не пишет.
#
# Один адрес бывает и картой, и осью - в JK03A таких 18, и семь пар читаются в обе
# стороны (defs/JK03A.notes.md, "Обратный поиск"). Роль задаёт сайт, а не сам массив,
# поэтому печатается всё, чем адрес в графе является.
#
# Шкала показана рядом с сырым значением, а не вместо него: множитель половины карт стоит
# на уровне candidate, и подменять им байт значит выдавать догадку за показание.
#
# Запуск: uv run --no-project --with neo4j python tools/mapkit/show.py [<rom>] <addr>...
import os
import sys

from neo4j import GraphDatabase

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import rom as romkit          # noqa: E402 - пакет соседний, не установленный

BOLT = "bolt://localhost:7687"


def hexa(a):
    return "0x" + a.upper().lstrip("0").rjust(5, "0")


def phys(v, expr):
    """Значение по шкале графа. Словарь выражения проверен загрузчиком."""
    if not expr or expr.strip() == "x":
        return None
    return eval(expr, {"__builtins__": {}}, {"x": v})


def num(v):
    return f"{v:.4g}" if isinstance(v, float) else str(v)


def cell(raw, expr):
    v = phys(raw, expr)
    return num(raw) if v is None else num(v)


def labels(ax, n):
    """Подписи точек оси либо их номера, если оси нет."""
    if not ax:
        return [str(i) for i in range(n)]
    vals, expr = ax
    return [cell(v, expr) for v in vals]


def scale_note(units, expr, conf):
    if not expr or expr.strip() == "x":
        return "шкалы нет, значения сырые"
    return f"шкала {expr} -> {units}" + (f" [{conf}]" if conf else "")


def show_axis(x, img, head="ось"):
    vals = img.values(x["addr"], x["len"], x["storagetype"])
    print(f"  {head} {hexa(x['addr'])}: {x['len']} точек {x['storagetype']}"
          f", {x['kind'] or 'семантика не снята'} [{x['confidence']}]"
          f", {scale_note(x['units'], x['scale_expr'], x['scale_conf'])}")
    print("    сырые:", " ".join(num(v) for v in vals))
    if phys(vals[0], x["scale_expr"]) is not None:
        print(f"    {x['units']}:", " ".join(num(phys(v, x["scale_expr"])) for v in vals))
    if x["note"]:
        print(f"    {x['note']}")
    return vals


def grid(cells, expr, head, lbl):
    """Сетка значений с подписями. У 2D строка - точка оси r5, столбец - точка оси r6."""
    body = [[cell(v, expr) for v in r] for r in cells]
    w = max(len(s) for s in head + [c for r in body for c in r])
    pad = max((len(s) for s in lbl), default=0)
    print("  " + " " * pad + " | " + " ".join(s.rjust(w) for s in head))
    print("  " + "-" * (pad + 1) + "+" + "-" * (len(head) * (w + 1) + 1))
    for i, r in enumerate(body):
        print(f"  {(lbl[i] if lbl else '').rjust(pad)} | "
              + " ".join(c.rjust(w) for c in r))


def show_map(m, axes, img):
    shape = f"{m['width']}x{m['height']}" if m["dims"] == 2 else f"1D-{m['width']}"
    print(f"{hexa(m['addr'])}  {m['semantics'] or '(семантика не снята)'}  "
          f"[{m['confidence']}]")
    print(f"  {shape} {m['storagetype']}, {m['family']}, значения {m['vmin']}..{m['vmax']}"
          f"; {scale_note(m['units'], m['scale_expr'], m['scale_conf'])}")
    if m["note"]:
        print(f"  {m['note']}")
    rows_ax = cols_ax = None
    for edge, key in (("AXIS_X", "axis_x"), ("AXIS_Y", "axis_y")):
        for a in m[key]:
            x = axes[a]
            head = ("ось r5 (строки, Y Axis дефа)" if edge == "AXIS_X"
                    else "ось r6 (столбцы, X Axis дефа)") if m["dims"] == 2 else "ось"
            vals = show_axis(x, img, head)
            if edge == "AXIS_X" and rows_ax is None:
                rows_ax = (vals, x["scale_expr"])
            elif edge == "AXIS_Y" and cols_ax is None:
                cols_ax = (vals, x["scale_expr"])
    if len(m["axis_x"]) > 1 or len(m["axis_y"]) > 1:
        print("  ВНИМАНИЕ: осей на ребре больше одной - ось выбирает ветвление (Stage 6);"
              " сетка взята по первой")
    if m["dims"] == 1 and not m["axis_x"] and m["steps"]:
        print(f"  ось неявная: точки 0..{m['width'] - 1} с шагом {m['steps'][0]}")
        cols_ax = ([i * m["steps"][0] for i in range(m["width"])], "x")
    # height у одномерной карты нет вовсе: Memgraph null-свойств не хранит.
    cells = img.table(m["addr"], m["width"], m.get("height"), m["storagetype"])
    # У одномерной карты строка одна, и её ось подписывает столбцы; у двумерной ось r5
    # идёт по строкам, а r6 - по столбцам (геометрия finisher'а, см. rom.py).
    if m["dims"] == 1:
        grid(cells, m["scale_expr"], labels(cols_ax or rows_ax, m["width"]), [])
    else:
        grid(cells, m["scale_expr"], labels(cols_ax, m["height"]),
             labels(rows_ax, m["width"]))


def fetch(s, rom, addr):
    m = s.run("""
        MATCH (m:Map {rom:$rom, addr:$a})
        OPTIONAL MATCH (m)-[:AXIS_X]->(x:Axis) OPTIONAL MATCH (m)-[:AXIS_Y]->(y:Axis)
        OPTIONAL MATCH (m)-[:VIA]->(w:Interp)
        RETURN m AS m, collect(DISTINCT x.addr) AS axis_x,
               collect(DISTINCT y.addr) AS axis_y,
               [s IN collect(DISTINCT w.step) WHERE s IS NOT NULL] AS steps
        """, rom=rom, a=addr).single()
    x = s.run("MATCH (x:Axis {rom:$rom, addr:$a}) RETURN x", rom=rom, a=addr).single()
    return m, x


def main():
    args = sys.argv[1:]
    try:
        known = {r["rom"] for r in romkit.registry() if r["rom"]}
    except ValueError as e:
        sys.exit(str(e))
    # Метка ROM отличается от адреса реестром, а не формой: 0xB33A и JK03A обе -
    # шестнадцатеричные слова, и разбор по виду перепутал бы их молча.
    rom = args.pop(0) if args and args[0] in known else "JK03A"
    if not args:
        sys.exit(f"нужен адрес: show.py [<rom>] <addr>...; метки ROM: "
                 f"{', '.join(sorted(known))}")
    try:
        img = romkit.load(rom)
    except ValueError as e:
        sys.exit(str(e))
    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    with driver.session() as s:
        for a in args:
            addr = "%08x" % int(a, 16)
            m, x = fetch(s, rom, addr)
            if not m and not x:
                print(f"{hexa(addr)}: в графе {rom} такого адреса нет")
                continue
            if m:
                d = dict(m["m"], axis_x=m["axis_x"], axis_y=m["axis_y"], steps=m["steps"])
                axes = {a2: dict(s.run("MATCH (x:Axis {rom:$rom, addr:$a}) RETURN x",
                                       rom=rom, a=a2).single()["x"])
                        for a2 in d["axis_x"] + d["axis_y"]}
                show_map(d, axes, img)
            if x:
                # Тот же адрес бывает осью другой карты - роль задаёт сайт, а не массив.
                if m:
                    print(f"  он же ось других карт:")
                show_axis(dict(x["x"]), img)
            print()
    driver.close()


if __name__ == "__main__":
    main()
