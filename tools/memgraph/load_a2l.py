#!/usr/bin/env python3
# Загрузка каталога A2L (Stage 5, разделы 5 и 7 tools/map-flag-pipeline.md) в Memgraph:
# узлы :A2LEntry - rom-независимый эталон семейства HR (P7).
#
# Источник - defs/reference/Pytrex-NissanDefinitions/Nissan Definitions/A2L.xml, базовый деф
# RomRaider: имена, категории, геометрия, scaling, описания. Адресов в нём нет вовсе - их
# дают ROM-дефы, наследующие этот base. Требование "адреса не переносятся" (layout JDM 2.5L
# != USDM 3.5L) поэтому структурное: переносить нечего, каталог задаёт классы, не размещение.
#
# Ловушка нотации RomRaider: type="2D" - таблица с ОДНОЙ осью, "3D" - с двумя, "1D" - скаляр
# без осей. В графе dims - число осей (:Map, load_maps.py), поэтому нотация нормализуется:
# 2D -> dims=1, 3D -> dims=2, 1D -> dims=0. Без нормализации join по dims сошёлся бы на
# "2D"=2 и молча смэтчил каждую запись не с тем классом карт.
#
# shape пишется словарём журнала разметки (defs/JK03A.maps.csv, колонка dim): 3D 16x16 ->
# "16x16", 2D sizex=8 -> "1D-8". Обёртка задаёт геометрию карты однозначно (у всех 36
# обёрток журнала dim однороден), поэтому общий словарь делает будущий матч прямым join'ом
# строк, а не сверкой двух нотаций.
#
# Рёбра :MATCHES здесь не строятся. Ключи матча по разделу 7 - (dims, scale-family, axis
# semantics); на стороне :Map из них есть только dims, а scale_expr и семантика осей
# появляются в Stage 4 (геометрия и чтение осей). Матч по одному dims свёл бы 37 записей "3D"
# с каждой картой dims=2 - это шум, а не подсказка, и ровно тот отказ, против которого стоит
# P6 ("pattern != семантика"). Загрузчик ставит эталон в граф; ребро строит Stage 5 после
# Stage 4.
#
# Биты switch'ей лежат списком на узле записи: единица идентичности каталога - переключатель
# (байт/dword по одному адресу), бит - поле внутри него. Гранулярность :Flag {addr,bit} - за
# Stage 6; расщеплять каталог по битам до его модели матча преждевременно.
#
# Запуск: uv run --no-project --with neo4j python tools/memgraph/load_a2l.py [a2l_xml] [family]
# По умолчанию xml = defs/reference/.../A2L.xml, family = HR.
import os
import re
import sys
import xml.etree.ElementTree as ET

from neo4j import GraphDatabase

BOLT = "bolt://localhost:7687"

DEFAULT_XML = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "defs",
    "reference",
    "Pytrex-NissanDefinitions",
    "Nissan Definitions",
    "A2L.xml",
)

# type RomRaider -> (kind, dims). dims - число осей, не имя нотации.
KIND = {
    "3D": ("map", 2),
    "2D": ("map", 1),
    "1D": ("scalar", 0),
    "BitwiseSwitch": ("switch", 0),
}

# "Axis RPM (x*50)" -> ("RPM", "x*50"); "- (x)" -> ("-", "x").
SCALE_RE = re.compile(r"^\s*(.*?)\s*\(([^)]*)\)\s*$")


def parse_scaling(el):
    """Единица (scale-family матча) и точное выражение из scaling base."""
    if el is None:
        return "", ""
    sc = el.find("scaling")
    if sc is None:
        return "", ""
    base = (sc.get("base") or "").strip()
    m = SCALE_RE.match(base)
    if not m:
        return base, ""
    unit, expr = m.group(1).strip(), m.group(2).strip()
    if unit.startswith("Axis "):
        unit = unit[5:]           # "Axis RPM" и "RPM" - одна семья: ось и значение
    return unit, expr


def shape_of(kind, dims, sx, sy):
    """Геометрия словарём журнала разметки: 16x16, 8x8, 1D-8, 1D-16."""
    if kind != "map":
        return ""
    if dims == 2:
        return f"{sx}x{sy}" if sx and sy else ""
    return f"1D-{sx}" if sx else ""


def axis_of(t, want):
    """Ось таблицы: 'X Axis' и 'Static X Axis' - одна роль, статика лишь держит точки в дефе."""
    for a in t.findall("table"):
        typ = (a.get("type") or "").replace("Static ", "")
        if typ == want:
            return a
    return None


def build(path, family):
    root = ET.parse(path).getroot()
    entries, skipped = [], []
    for t in root.findall("table"):
        typ = t.get("type")
        if typ not in KIND:
            skipped.append(typ)
            continue
        kind, dims = KIND[typ]
        sx, sy = t.get("sizex"), t.get("sizey")
        unit, expr = parse_scaling(t)
        ax, ay = axis_of(t, "X Axis"), axis_of(t, "Y Axis")
        ax_unit, ax_expr = parse_scaling(ax)
        ay_unit, ay_expr = parse_scaling(ay)
        desc = t.find("description")
        bits = t.findall("bit")
        entries.append(
            {
                "family": family,
                "name": t.get("name") or "",
                "category": t.get("category") or "",
                "kind": kind,
                "dims": dims,
                "shape": shape_of(kind, dims, sx, sy),
                "width": int(sx) if sx and sx.isdigit() else None,
                "height": int(sy) if sy and sy.isdigit() else None,
                "storagetype": t.get("storagetype") or "",
                "unit": unit,
                "scale_expr": expr,
                "axis_x_sem": (ax.get("name") or "") if ax is not None else "",
                "axis_y_sem": (ay.get("name") or "") if ay is not None else "",
                "axis_x_scale": ax_expr,
                "axis_y_scale": ay_expr,
                "axis_x_unit": ax_unit,
                "axis_y_unit": ay_unit,
                "userlevel": int(t.get("userlevel")) if t.get("userlevel") else None,
                "bits": [f"{b.get('position')}={b.get('name')}" for b in bits],
                "description": "".join(desc.itertext()).strip() if desc is not None else "",
            }
        )
    return entries, skipped


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_XML
    family = sys.argv[2] if len(sys.argv) > 2 else "HR"

    entries, skipped = build(path, family)
    kinds = {}
    for e in entries:
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    print(f"A2L: {len(entries)} записей из {os.path.basename(path)}; family={family}")
    print(
        f"Каталог: {kinds.get('map', 0)} карт ("
        f"{sum(1 for e in entries if e['dims'] == 2)} с двумя осями, "
        f"{sum(1 for e in entries if e['dims'] == 1)} с одной), "
        f"{kinds.get('scalar', 0)} скаляров, {kinds.get('switch', 0)} switch'ей"
    )
    if skipped:
        print(f"  не разобрано типов: {sorted(set(skipped))}")

    # Имя - ключ узла: коллизия молча слила бы две записи каталога в одну.
    names = [e["name"] for e in entries]
    dup = sorted({n for n in names if names.count(n) > 1})
    if dup:
        print(f"ВНИМАНИЕ: неуникальные имена ({len(dup)}): {dup[:5]}")

    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    with driver.session() as s:
        s.run("MATCH (n:A2LEntry {family:$f}) DETACH DELETE n", f=family)
        for prop in ("family", "name"):
            try:
                s.run(f"CREATE INDEX ON :A2LEntry({prop})")
            except Exception:
                pass

        s.run(
            """
            UNWIND $rows AS r
            MERGE (e:A2LEntry {family:r.family, name:r.name})
            SET e.category = r.category, e.kind = r.kind, e.dims = r.dims,
                e.shape = r.shape, e.width = r.width, e.height = r.height,
                e.storagetype = r.storagetype, e.unit = r.unit,
                e.scale_expr = r.scale_expr,
                e.axis_x_sem = r.axis_x_sem, e.axis_y_sem = r.axis_y_sem,
                e.axis_x_scale = r.axis_x_scale, e.axis_y_scale = r.axis_y_scale,
                e.axis_x_unit = r.axis_x_unit, e.axis_y_unit = r.axis_y_unit,
                e.userlevel = r.userlevel, e.bits = r.bits, e.description = r.description
            """,
            rows=entries,
            family=family,
        )
        n = s.run(
            "MATCH (e:A2LEntry {family:$f}) RETURN count(e) AS n", f=family
        ).single()["n"]
        print(f"Memgraph: {n} :A2LEntry")

        print("Геометрия карт каталога (словарь журнала разметки):")
        for r in s.run(
            """
            MATCH (e:A2LEntry {family:$f, kind:'map'})
            RETURN e.shape AS shape, count(*) AS n ORDER BY n DESC, shape
            """,
            f=family,
        ):
            print(f"  {r['shape']:<8} {r['n']:>3}")

        print("Флаги каталога (вход Stage 6):")
        for r in s.run(
            """
            MATCH (e:A2LEntry {family:$f, kind:'switch'})
            RETURN split(e.category,'//')[1] AS grp, count(*) AS n,
                   sum(size(e.bits)) AS bits ORDER BY n DESC
            """,
            f=family,
        ):
            print(f"  {r['grp']:<10} записей {r['n']:>3}, битов {r['bits']:>4}")

    driver.close()


if __name__ == "__main__":
    main()
