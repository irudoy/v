#!/usr/bin/env python3
# Загрузка вендорских словарей (Stage 5, разделы 5 и 7 tools/map-flag-pipeline.md) в Memgraph:
# узлы :VendorEntry (каталог имён) и :VendorFact (якорные факты) - rom-независимый слой
# семейства HR рядом с :A2LEntry (P7).
#
# Источник - refs/vendor/catalog.csv и refs/vendor/facts.csv, сведённые словари ProECU
# (EcuTek) и UpRev; метод и правила разметки - refs/vendor/README.md. Адресов в них нет, как
# и в A2L: словари задают классы, а не размещение.
#
# Зачем второй каталог рядом с A2L. A2L знает форму таблицы (геометрия, storagetype, scaling),
# но не смысл: имена там есть, а механики за ними нет. Вендорские доки несут ровно
# недостающее - смысл калибровки, оси в терминах ROM и документированные дефолты. Прецедент
# ценности - K-Factor: его дефолт 26806 назван прозой, найден в дампе поиском значения и дал
# гомолог-джойн на пять ROM раньше любого трейса.
#
# Ключ узла каталога - (vendor, family, name). Имя одно на вендора: имена вербатим, и два
# словаря называют одно разными словами (`BFS Multiplier (K-Factor)` против
# `K - Fuel Multiplier`), поэтому глобальный ключ по имени слил бы разные записи и разорвал бы
# одинаковые.
#
# Соединяет словари колонка concept, а не имя. Она проставлена только там, где связка
# обоснована (170 записей из 371, 27 concept'ов покрыты обоими словарями); пустая означает
# "связка не установлена". Рёбер concept загрузчик не строит: join по свойству - одна строка
# Cypher, а материализованное ребро было бы копией свойства, то есть вторым источником правды
# ровно того сорта, против которого стоит P5.
#
# Рёбра :MATCHES здесь не строятся - как и в load_a2l.py. Ключи матча по разделу 7 -
# (dims, scale-family, axis semantics). У ProECU нет ни одного из трёх: скриншоты дерева несут
# только имена. У UpRev есть семантика осей, но она прозаическая (`Base Fuel Schedule`,
# `coolant temp`), и сведение её с семантикой :Axis - работа Stage 5 после Stage 4, а не
# загрузчика. Матч по имени вслепую - ровно тот отказ, против которого стоит P6.
#
# Фильтр origin=factory обязателен для разметки стокового ROM: 128 записей из 371 заводскими не
# являются - 126 описывают патчи самих вендоров (RaceROM у EcuTek, ARC у UpRev), то есть чужой
# код, которого в стоке нет, а 2 не разрешены. Матч стоковой карты к patch-записи был бы не
# слабой подсказкой, а неверной.
#
# Запуск: uv run --no-project --with neo4j python tools/memgraph/load_vendor.py [family]
# По умолчанию family = HR.
import csv
import os
import sys

from neo4j import GraphDatabase

BOLT = "bolt://localhost:7687"

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CATALOG = os.path.join(ROOT, "refs", "vendor", "catalog.csv")
FACTS = os.path.join(ROOT, "refs", "vendor", "facts.csv")

ORIGINS = {"factory", "patch", "unknown"}
KINDS = {"const", "unit", "axis", "geometry", "mechanics", "hardware", "gap", "hypothesis"}


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(s):
    """dims - число осей, как у :A2LEntry и :Map. Пустое - не объявлено словарём."""
    return int(s) if s and s.isdigit() else None


def build_entries(family):
    rows = []
    for r in read(CATALOG):
        rows.append(
            {
                "vendor": r["vendor"],
                "family": family,
                "name": r["name"],
                "doc": r["doc"],
                "section": r["section"],
                "group": r["group"],
                "dims": num(r["dims"]),
                "axis_x": r["axis_x"],
                "axis_y": r["axis_y"],
                "output": r["output"],
                "origin": r["origin"],
                "level": r["level"],
                "concept": r["concept"],
                "source": r["source"],
                "note": r["note"],
            }
        )
    return rows


def build_facts(family):
    rows = []
    for r in read(FACTS):
        rows.append(
            {
                "vendor": r["vendor"],
                "family": family,
                "subject": r["subject"],
                "doc": r["doc"],
                "kind": r["kind"],
                "concept": r["concept"],
                "statement": r["statement"],
                "value": r["value"],
                "units": r["units"],
                "applies_to": r["applies_to"],
                "anchor": r["anchor"],
                "note": r["note"],
            }
        )
    return rows


def check(entries, facts):
    """Отказы, которые в графе неотличимы от факта, ловятся до загрузки."""
    bad = sorted({e["origin"] for e in entries} - ORIGINS)
    if bad:
        sys.exit(f"catalog.csv: неизвестный origin: {bad}")
    bad = sorted({f["kind"] for f in facts} - KINDS)
    if bad:
        sys.exit(f"facts.csv: неизвестный kind: {bad}")

    # Ключ узла - (vendor, name): коллизия молча слила бы две записи каталога в одну.
    seen = {}
    for e in entries:
        seen.setdefault((e["vendor"], e["name"]), 0)
        seen[(e["vendor"], e["name"])] += 1
    dup = sorted(k for k, n in seen.items() if n > 1)
    if dup:
        sys.exit(f"catalog.csv: неуникальные (vendor, name), {len(dup)}: {dup[:5]}")

    seen = {}
    for f in facts:
        seen.setdefault((f["vendor"], f["subject"]), 0)
        seen[(f["vendor"], f["subject"])] += 1
    dup = sorted(k for k, n in seen.items() if n > 1)
    if dup:
        sys.exit(f"facts.csv: неуникальные (vendor, subject), {len(dup)}: {dup[:5]}")


def main():
    family = sys.argv[1] if len(sys.argv) > 1 else "HR"
    entries, facts = build_entries(family), build_facts(family)
    check(entries, facts)

    vendors = sorted({e["vendor"] for e in entries})
    factory = sum(1 for e in entries if e["origin"] == "factory")
    print(f"Вендорские словари: {len(entries)} записей каталога, {len(facts)} фактов; "
          f"family={family}")
    print(f"Словари: {', '.join(vendors)}")
    print(f"origin=factory (пригодны для стокового ROM): {factory} из {len(entries)}")

    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    with driver.session() as s:
        s.run("MATCH (n:VendorEntry {family:$f}) DETACH DELETE n", f=family)
        s.run("MATCH (n:VendorFact {family:$f}) DETACH DELETE n", f=family)
        for label, props in (
            ("VendorEntry", ("family", "vendor", "name", "concept", "origin")),
            ("VendorFact", ("family", "vendor", "subject", "concept", "kind")),
        ):
            for prop in props:
                try:
                    s.run(f"CREATE INDEX ON :{label}({prop})")
                except Exception:
                    pass

        s.run(
            """
            UNWIND $rows AS r
            MERGE (e:VendorEntry {vendor:r.vendor, family:r.family, name:r.name})
            SET e.doc = r.doc, e.section = r.section, e.group = r.group,
                e.dims = r.dims, e.axis_x = r.axis_x, e.axis_y = r.axis_y,
                e.output = r.output, e.origin = r.origin, e.level = r.level,
                e.concept = r.concept, e.source = r.source, e.note = r.note
            """,
            rows=entries,
        )
        s.run(
            """
            UNWIND $rows AS r
            MERGE (f:VendorFact {vendor:r.vendor, family:r.family, subject:r.subject})
            SET f.doc = r.doc, f.kind = r.kind, f.concept = r.concept,
                f.statement = r.statement, f.value = r.value, f.units = r.units,
                f.applies_to = r.applies_to, f.anchor = r.anchor, f.note = r.note
            """,
            rows=facts,
        )
        n = s.run(
            "MATCH (e:VendorEntry {family:$f}) RETURN count(e) AS n", f=family
        ).single()["n"]
        m = s.run(
            "MATCH (f:VendorFact {family:$f}) RETURN count(f) AS n", f=family
        ).single()["n"]
        print(f"Memgraph: {n} :VendorEntry, {m} :VendorFact")

        print("Заводские имена по словарям (вход матча Stage 5):")
        for r in s.run(
            """
            MATCH (e:VendorEntry {family:$f, origin:'factory'})
            RETURN e.vendor AS vendor, count(*) AS n ORDER BY n DESC
            """,
            f=family,
        ):
            print(f"  {r['vendor']:<8} {r['n']:>3}")

        print("Схождение словарей (concept, покрытые обоими):")
        rows = list(
            s.run(
                """
                MATCH (e:VendorEntry {family:$f}) WHERE e.concept <> ''
                WITH e.concept AS c, collect(DISTINCT e.vendor) AS vs, count(*) AS n
                WHERE size(vs) > 1
                RETURN c, n ORDER BY c
                """,
                f=family,
            )
        )
        for r in rows:
            print(f"  {r['c']:<24} записей {r['n']:>2}")
        print(f"  всего: {len(rows)}")

        print("Документированные дефолты (искомые в дампе якоря):")
        for r in s.run(
            """
            MATCH (f:VendorFact {family:$f, kind:'const'}) WHERE f.value <> ''
            RETURN f.value AS value, f.units AS units, f.subject AS subject,
                   f.applies_to AS scope ORDER BY f.concept, f.subject
            """,
            f=family,
        ):
            print(f"  {r['value']:>10} {r['units']:<22} {r['scope']:<9} {r['subject']}")

        print("Открытая работа (пробелы вендоров и гипотезы сведения):")
        for r in s.run(
            """
            MATCH (f:VendorFact {family:$f}) WHERE f.kind IN ['gap','hypothesis']
            RETURN f.kind AS kind, f.vendor AS vendor, f.subject AS subject
            ORDER BY f.kind, f.vendor, f.subject
            """,
            f=family,
        ):
            print(f"  {r['kind']:<11} {r['vendor']:<8} {r['subject']}")

    driver.close()


if __name__ == "__main__":
    main()
