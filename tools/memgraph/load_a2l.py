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
# Колонка concept - курируемая разметка идентичности, ключ джойна с вендорским каталогом
# (:VendorEntry, refs/vendor/catalog.csv): записи с одним значением описывают одну сущность.
# Все три словаря зовут её по-разному (`K-Value` против `BFS Multiplier (K-Factor)` против
# `K - Fuel Multiplier`), поэтому джойн по имени не сошёлся бы вовсе, а джойн по похожести имён
# сводил бы разное. Пустой concept означает "связка не установлена", а не "связки нет".
#
# Основание связки - description и геометрия записи против прозы вендоров, не близость имён.
# Прецедент отказа: A2L 'MAF Voltage Lower Limit' по имени садится на 'MAF Voltage Min Allowed'
# EcuTek, но описания противоречат (у A2L порог поднимает P0102, EcuTek пишет "DTC не
# выставляется"), поэтому связка не проставлена - разбор в refs/vendor/facts.csv.
#
# Словарь concept'ов задаёт вендорский каталог. Значение, которого там нет, джойнится в пустоту,
# и разметка молча осталась бы мёртвой - поэтому и словарь, и имена проверяются до загрузки.
#
# Разметка ставится только на карты и скаляры. Флаги (Options//Flags, DTC, Supmask) размечает
# Stage 6 по своей модели: у вендоров они не карты, а биты внутри переключателя.
#
# Запуск: uv run --no-project --with neo4j python tools/memgraph/load_a2l.py [a2l_xml] [family]
# По умолчанию xml = defs/reference/.../A2L.xml, family = HR.
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET

from neo4j import GraphDatabase

BOLT = "bolt://localhost:7687"

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEFAULT_XML = os.path.join(
    ROOT,
    "defs",
    "reference",
    "Pytrex-NissanDefinitions",
    "Nissan Definitions",
    "A2L.xml",
)

CATALOG = os.path.join(ROOT, "refs", "vendor", "catalog.csv")

# type RomRaider -> (kind, dims). dims - число осей, не имя нотации.
KIND = {
    "3D": ("map", 2),
    "2D": ("map", 1),
    "1D": ("scalar", 0),
    "BitwiseSwitch": ("switch", 0),
}

# "Axis RPM (x*50)" -> ("RPM", "x*50"); "- (x)" -> ("-", "x").
SCALE_RE = re.compile(r"^\s*(.*?)\s*\(([^)]*)\)\s*$")

# --- concept: точное имя A2L -> сущность вендорского каталога ---
# Гранулярность concept'а задана каталогом: это семейство калибровки, а не одна таблица. У
# `vvel-duration` семь записей ProECU (Cold, Main, Overrun, WOT...), у `idle-ignition` девять,
# поэтому варианты одной функции (Cold/High Detonation/High Octane, Trustful) делят concept.
A2L_CONCEPT = {
    # Тракт MAF -> BFS -> нагрузка. Описания A2L называют связку прямо: 'MAF Factor' - "what
    # Nissan uses to scale MAF from factory", 'Load Base Fuel Schedule Table' - "The 100% BFS
    # value... used to calculate Calculated Load", 'Cylinder Filling Up Efficiency Scaler' -
    # "BFS at which maximum airflow occurs".
    'MAF Table': 'maf-curve',
    'MAF Factor': 'maf-gps-scalar',
    'K-Value': 'bfs-multiplier',
    'Load Base Fuel Schedule Table': 'load-100pct',
    'Cylinder Filling Up Efficiency Scaler': 'load-point-scaler',
    # Цель AFR. EcuTek держит заводскую карту 8x8, и обе геометрии A2L лежат рядом.
    'Target AFR Map (16x16)': 'fuel-target',
    'Target AFR Map (8x8)': 'fuel-target',
    'Target AFR Table (High Detonation)': 'fuel-target',
    # Топливные поправки. У 'Fuel Compensation Map' оси QH0 Flow Quantity x Engine Speed - те же,
    # что UpRev называет Volumetric Flow Ratio x RPM у 'Fuel Compensation Main'; обе правят BFS.
    # Пара KHOT - высокотемпературное обогащение, оно же 'Fuel Enrichment - Hot' у EcuTek.
    'Fuel Compensation Map (16x16)': 'fuel-comp',
    'High Coolant Temperature Increase Compensation Table': 'fuel-comp',
    'High Temperature Fuel Compensation Map': 'fuel-comp',
    'Individual Cylinder Fuel Trims': 'cylinder-trim',
    # Форсунки. Пара latency - это прямая UpRev y = m * X + B: 'at 14V' даёт B, 'Adder' - наклон.
    'Fuel Injector Latency at 14V': 'injector-latency',
    'Fuel Injector Latency Adder': 'injector-latency',
    'Minimum Injector Pulse Width': 'injector-minimum',
    # Пуск: ось - температура охлаждающей жидкости, значение - ширина импульса (BFS в мс), как у
    # 'Cranking Enrichment Initial Value' UpRev.
    'Cranking Base Fuel Schedule Table': 'cranking-initial',
    # Отсечка на сбросе, а не ограничитель оборотов: "fuel cut will occur (on decel) until the
    # RPM's hit the recover speed". Комплекта два по линейкам ЭБУ (Bosch, JECS/Hitachi), и это
    # ровно четыре карты EcuTek: Overrun Fuel Cut #1, #1 Restore, #2, #2 Restore.
    'Bosch Fuel Cut Table': 'overrun-fuel-cut',
    'Bosch Fuel Restore Table': 'overrun-fuel-cut',
    'JECS Fuel Cut Table': 'overrun-fuel-cut',
    'JECS Fuel Restore Table': 'overrun-fuel-cut',
    # Ограничители оборотов и скорости. Одна карта 2x2 A2L несёт и отсечку, и восстановление
    # (ось Fuel = Cut/Restore), тогда как EcuTek показывает их двумя картами; concept ставится по
    # имени записи, разбор осей - в facts.csv.
    'Rev Limit (Fuel Cut - 3D)': 'rev-limit-fuel',
    'Throttle Rev Limiter': 'rev-limit-throttle',
    'Speed Limiter': 'speed-limit',
    'Speed Limiter (Fuel Cut)': 'speed-limit',
    'Speed Limiter (Fuel Restore)': 'speed-limit',
    # Зажигание: три карты поправки к расчётному MBT ("this trimming map value is added/
    # subtracted from that value") - ровно три таблицы UpRev (Main, High Det, Cold). Базовой
    # таблицы угла в ЭБУ нет: MBT считается формулой.
    'Cold Ignition Timing Map (16x16)': 'ignition-trim',
    'High Detonation Ignition Timing Map (16x16)': 'ignition-trim',
    'High Octane Ignition Timing Map (16x16)': 'ignition-trim',
    # Окна детонации парны картам поправки один к одному - так же, как у EcuTek 'Knock Control
    # Enable A1' пять карт по числу вариантов 'Mode A1 Adj'.
    'Cold Ignition Timing Map Knock Window': 'knock-enable',
    'High Detonation Ignition Timing Map Knock Window': 'knock-enable',
    'High Octane Ignition Timing Map Knock Window': 'knock-enable',
    # Пороги детонации: 16x6, ось Y - номер цилиндра. EcuTek описывает ту же карту, отмечая
    # завышенные пороги средних цилиндров 3 и 4.
    'Knock Slice Map': 'knock-threshold',
    # Холостой ход: угол на холостом и сбросе мимо расчётного MBT (GOV-таблицы).
    'Idle Ignition Timing Table': 'idle-ignition',
    'Cold Idle Ignition Timing Table': 'idle-ignition',
    'Lean Burn Idle Ignition Timing Table': 'idle-ignition',
    # VTC - угол впускного распредвала. Карта High Detonation ("only used when knock is
    # detected") независимо подтверждает разбор суффикса ETD в дереве ProECU. Exhaust Cam Timing
    # не размечен: у вендоров ответной сущности нет.
    'Intake Cam Timing Map (16x16)': 'vtc-advance',
    'Cold Intake Cam Timing Map (8x8)': 'vtc-advance',
    'High Detonation Intake Cam Timing Map (4x4)': 'vtc-advance',
    # Педаль -> запрос расхода -> запрошенный момент -> открытие дросселя. Пара Lo/Hi плюс пара
    # контрольных копий - те же четыре записи, что 'Accel to Throttle Hi/Lo' (+Trustful) EcuTek.
    'Throttle Flow Potential Table': 'accel-throttle',
    'Throttle Flow Potential Table (High Flow-Quantity)': 'accel-throttle',
    'Throttle Flow Potential Table Trustful': 'accel-throttle',
    'Throttle Flow Potential Table (High Flow-Quantity) Trustful': 'accel-throttle',
    'QH0/ Torque Conversion Map': 'torque-demand',
    'QH0/ Torque Conversion Map Trustful': 'torque-demand',
    # Момент для TCM (давление в линии), он же 'Estimated Torque Delivered' UpRev: та же шкала
    # момента, что у карты запроса, ось нагрузки - наполнение цилиндра вместо BFS.
    'Engine Torque Map': 'torque-actual',
}


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
                "concept": A2L_CONCEPT.get(t.get("name") or "", ""),
            }
        )
    return entries, skipped


def vocabulary():
    """Словарь concept'ов задаёт вендорский каталог: A2L джойнится только к нему."""
    with open(CATALOG, newline="", encoding="utf-8") as f:
        return {r["concept"] for r in csv.DictReader(f) if r["concept"]}


def check(entries):
    """Мёртвая разметка в графе неотличима от непроставленной, поэтому ловится до загрузки."""
    stale = sorted(set(A2L_CONCEPT) - {e["name"] for e in entries})
    if stale:
        sys.exit(f"concept ссылается на имена, которых нет в A2L: {stale}")
    unknown = sorted(set(A2L_CONCEPT.values()) - vocabulary())
    if unknown:
        sys.exit(f"concept'ов нет в вендорском каталоге, джойн уйдёт в пустоту: {unknown}")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_XML
    family = sys.argv[2] if len(sys.argv) > 2 else "HR"

    entries, skipped = build(path, family)
    check(entries)
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
        for prop in ("family", "name", "concept"):
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
                e.userlevel = r.userlevel, e.bits = r.bits, e.description = r.description,
                e.concept = r.concept
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

        # Джойн трёх словарей: A2L даёт форму и место в тракте, вендоры - смысл и дефолты.
        print("Схождение трёх словарей (concept: A2L + ProECU + UpRev):")
        rows = list(
            s.run(
                """
                MATCH (a:A2LEntry {family:$f}) WHERE a.concept <> ''
                WITH a.concept AS c, count(a) AS a2l
                MATCH (v:VendorEntry {family:$f, origin:'factory', concept:c})
                WITH c, a2l, collect(DISTINCT v.vendor) AS vs, count(v) AS vend
                RETURN c, a2l, vend, vs ORDER BY c
                """,
                f=family,
            )
        )
        for r in rows:
            print(f"  {r['c']:<20} A2L {r['a2l']:>2} <-> вендоры {r['vend']:>2} "
                  f"({', '.join(sorted(r['vs']))})")
        both = sum(1 for r in rows if len(r["vs"]) > 1)
        marked = sum(1 for e in entries if e["concept"])
        print(f"  всего concept'ов: {len(rows)}, из них покрыты обоими словарями: {both}")
        print(f"  размечено записей A2L: {marked} из {len(entries)}")

    driver.close()


if __name__ == "__main__":
    main()
