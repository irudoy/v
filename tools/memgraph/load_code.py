#!/usr/bin/env python3
# Слой понимания кода (tools/code-provenance-proposal.md, раздел 4, шаг 1 раздела 7):
# проекция установленных фактов о функциях и RAM-переменных на существующие
# :Func/:Reg. Источник - defs/<rom>.funcs.csv и defs/<rom>.vars.csv; граф - проекция
# (И1): свойства пересоздаются каждым прогоном, руками в графе не правятся.
#
# Ставит на :Func свойства role/semantics/confidence/evidence, на :Reg -
# semantics/units/confidence/evidence. Уровень - лестница pattern->candidate->code->
# silicon (P3/P6): code только по трейсу со свидетельством, не по имени и не по форме.
#
# Порядок в цепочке: ПОСЛЕ load_graph.py (владелец :Func) и load_xrefs.py (владелец
# :Reg) - оба пересоздают свои узлы per-rom, стирая свойства этого слоя; load_code.py
# переспроецирует их следом.
#   :Func - MATCH: функция обязана существовать (Ghidra Stage 0). Несуществующий адрес -
#           не факт, а промах; загрузка останавливается (аудит §8: свидетельство резолвимо).
#   :Reg  - MERGE: RAM-переменная из notes.md часто адресуется как base+offset и прямого
#           xref не имеет, поэтому :Reg для неё load_xrefs не создал; регион/имя ставятся
#           через ту же classify(), что у load_xrefs.
#
# Поле evidence несёт разобранные ссылки (indexed_by:/writes:/trace:/consumer:/...).
# Оно кладётся свойством и проецируется в рёбра :RESTS_ON (шаг 2 раздела 7): токен
# класса-ребра адресует узел, из которого строится (вывод)-[:RESTS_ON {role}]->(свидетельство).
# Направление читается по метке субъекта: на :Func writes:X - субъект пишет X, на :Reg
# writes:X - X пишет субъект; consumer:X - X потребляет выход субъекта.
#
# Запуск: uv run --no-project --with neo4j python tools/memgraph/load_code.py [rom]
# По умолчанию rom = JK03A.
import csv
import os
import re
import sys
from collections import Counter

from neo4j import GraphDatabase

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_xrefs import classify  # noqa: E402

BOLT = "bolt://localhost:7687"

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFS = os.path.join(ROOT, "defs")

# Лестница уверенности спеки; пусто = не ранжировано.
LEVELS = {"", "pattern", "candidate", "code", "silicon"}
# Роль функции (proposal раздел 4, расширяемо); пусто допустимо.
FUNC_ROLES = {
    "", "accessor", "consumer", "monitor", "driver", "init", "kernel",
    "wrapper", "finisher", "service", "dispatch", "handler", "selector",
}
ADDR_RE = re.compile(r"^[0-9a-f]{8}$")

# Словарь evidence (proposal раздел 4). Классы различаются не смыслом, а тем, адресует
# ли значение узел графа: только адресуемое несёт провенанс и распространяет уверенность.
#
# Класс-ребро: значение - адрес узла, из токена строится :RESTS_ON {role}. Порядок меток -
# приоритет разрешения адреса, первая присутствующая выигрывает (адрес бывает и :Func,
# и :Map одновременно).
EDGE_ROLES = {
    "consumer": ("Func", "Reg"),
    "writes": ("Reg", "Func"),
    "indexed_by": ("Reg", "Axis", "Func", "Map"),
    "selector": ("Reg", "Func"),
    "threshold": ("Reg", "Map"),
    "from_map": ("Map", "Axis"),
    "homolog": ("Func",),
    "trace": ("Func",),
    "base": ("Reg",),
    "match": ("Map", "Axis"),
}
# Роли, чья цель лежит в каталоге карт - слое, полнота которого своя (спека, раздел 11:
# карты вне графа называет только backtrack). Нерезолвимая ссылка здесь - объявленный
# пробел каталога, а не промах: она перечисляется и считается, загрузку не останавливает.
CATALOG_ROLES = {"from_map", "match"}
# Класс-терминал: свидетельство читается прямо из образа (rom_const), из инструкций самого
# субъекта (spec, registry) или с конкретного сайта (site). Узла не имеет, уверенность не
# кэпирует - проверяется чтением, а не обходом графа.
TERMINAL = {"rom_const", "spec", "registry", "site"}
# Метаданные процесса. Свидетельством не являются: "найдено в волне 3b" не обосновывает факт.
PROCESS = {"wave", "arg"}

VOCAB = set(EDGE_ROLES) | TERMINAL | PROCESS


def read(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_addrs_uniq(rows, path):
    seen = {}
    for r in rows:
        a = r["addr"]
        if not ADDR_RE.match(a):
            sys.exit(f"{path}: addr не 8 hex-цифр нижнего регистра: {a!r}")
        seen[a] = seen.get(a, 0) + 1
    dup = sorted(a for a, n in seen.items() if n > 1)
    if dup:
        sys.exit(f"{path}: неуникальные addr, {len(dup)}: {dup[:5]}")


def parse_evidence(rows, path):
    """evidence -> список (role, value); словарь заморожен, чужой токен - отказ."""
    for r in rows:
        toks = []
        for t in r["evidence"].split(";"):
            t = t.strip()
            if not t:
                continue
            if ":" not in t:
                sys.exit(f"{path}:{r['addr']}: токен без класса: {t!r}")
            role, value = t.split(":", 1)
            if role not in VOCAB:
                sys.exit(f"{path}:{r['addr']}: класс {role!r} вне словаря "
                         f"{sorted(VOCAB)}; расширять - вместе с proposal разделом 4")
            toks.append((role, value))
        r["_toks"] = toks


def check(funcs, vars_, fpath, vpath):
    """Отказы, в графе неотличимые от факта, ловятся до загрузки (как в load_vendor)."""
    check_addrs_uniq(funcs, fpath)
    check_addrs_uniq(vars_, vpath)
    parse_evidence(funcs, fpath)
    parse_evidence(vars_, vpath)

    # Ворота уровня (раздел 5.1): вывод code обязан опираться на свидетельство - ребро
    # либо терминал. Строка с одними метаданными процесса держит уровень на ходе работы,
    # а не на факте, и до code не поднимается.
    bare = [
        (path, r["addr"]) for rows, path in ((funcs, fpath), (vars_, vpath))
        for r in rows
        if r["confidence"] == "code"
        and not [1 for role, _ in r["_toks"] if role not in PROCESS]
    ]
    if bare:
        sys.exit(f"ворота уровня: {len(bare)} выводов code без свидетельства "
                 f"(только метаданные процесса): {bare}")

    bad = sorted({r["role"] for r in funcs} - FUNC_ROLES)
    if bad:
        sys.exit(f"{fpath}: неизвестный role {bad}; добавить в FUNC_ROLES, если легитимен")
    bad = sorted({r["confidence"] for r in funcs + vars_} - LEVELS)
    if bad:
        sys.exit(f"funcs/vars: confidence вне лестницы {sorted(LEVELS)}: {bad}")


def build_rests_on(s, rom, funcs, vars_):
    """Проекция evidence в (вывод)-[:RESTS_ON {role}]->(свидетельство).

    Рёбра пересоздаются целиком: источник правды - git, граф - проекция (И1).
    """
    subjects = [("Func", r) for r in funcs] + [("Reg", r) for r in vars_]
    wanted = sorted({
        v for _, r in subjects for role, v in r["_toks"]
        if role in EDGE_ROLES and ADDR_RE.match(v)
    })
    labels = sorted({lb for pref in EDGE_ROLES.values() for lb in pref})
    at = {
        lb: {
            x["a"] for x in s.run(
                f"MATCH (n:{lb} {{rom:$rom}}) WHERE n.addr IN $a RETURN n.addr AS a",
                rom=rom, a=wanted,
            )
        }
        for lb in labels
    }

    edges, gaps, dangling = [], [], []
    for src_label, r in subjects:
        for role, value in r["_toks"]:
            if role not in EDGE_ROLES or not ADDR_RE.match(value):
                continue  # арифметика базы и свободный текст - терминал, не ссылка
            dst = next((lb for lb in EDGE_ROLES[role] if value in at[lb]), None)
            if dst is None:
                (gaps if role in CATALOG_ROLES else dangling).append(
                    (src_label, r["addr"], f"{role}:{value}"))
                continue
            edges.append({"sl": src_label, "sa": r["addr"], "dl": dst,
                          "da": value, "role": role})
    if dangling:
        sys.exit(f"свидетельство не резолвимо: {len(dangling)} ссылок мимо узла "
                 f"(промах, не пробел каталога): {dangling}")

    s.run("MATCH (:Func {rom:$rom})-[e:RESTS_ON]->() DELETE e", rom=rom)
    s.run("MATCH (:Reg {rom:$rom})-[e:RESTS_ON]->() DELETE e", rom=rom)
    for sl in ("Func", "Reg"):
        for dl in labels:
            part = [e for e in edges if e["sl"] == sl and e["dl"] == dl]
            if part:
                s.run(
                    f"UNWIND $rows AS r "
                    f"MATCH (a:{sl} {{rom:$rom, addr:r.sa}}), (b:{dl} {{rom:$rom, addr:r.da}}) "
                    f"MERGE (a)-[:RESTS_ON {{role:r.role}}]->(b)",
                    rows=part, rom=rom,
                )
    return edges, gaps


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else "JK03A"
    fpath = os.path.join(DEFS, f"{rom}.funcs.csv")
    vpath = os.path.join(DEFS, f"{rom}.vars.csv")

    funcs, vars_ = read(fpath), read(vpath)
    check(funcs, vars_, fpath, vpath)
    for v in vars_:
        region, name = classify(int(v["addr"], 16))
        v["region"], v["name"] = region, name
    print(f"Слой кода {rom}: {len(funcs)} функций, {len(vars_)} переменных из git-источника")

    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    with driver.session() as s:
        # :Func обязаны существовать - иначе разметка висит на промахе (§8).
        addrs = [r["addr"] for r in funcs]
        present = {
            r["a"] for r in s.run(
                "MATCH (f:Func {rom:$rom}) WHERE f.addr IN $a RETURN f.addr AS a",
                rom=rom, a=addrs,
            )
        }
        missing = sorted(set(addrs) - present)
        if missing:
            sys.exit(f"{fpath}: {len(missing)} адресов не резолвятся в :Func {rom}: {missing}")

        reg_before = s.run(
            "MATCH (r:Reg {rom:$rom}) RETURN count(r) AS n", rom=rom
        ).single()["n"]

        s.run(
            """
            UNWIND $rows AS r
            MATCH (f:Func {rom:$rom, addr:r.addr})
            SET f.role = r.role, f.semantics = r.semantics,
                f.confidence = r.confidence, f.evidence = r.evidence
            """,
            rows=funcs, rom=rom,
        )
        s.run(
            """
            UNWIND $rows AS r
            MERGE (x:Reg {rom:$rom, addr:r.addr})
            ON CREATE SET x.region = r.region, x.name = r.name
            SET x.semantics = r.semantics, x.units = r.units,
                x.confidence = r.confidence, x.evidence = r.evidence
            """,
            rows=vars_, rom=rom,
        )

        reg_after = s.run(
            "MATCH (r:Reg {rom:$rom}) RETURN count(r) AS n", rom=rom
        ).single()["n"]
        created = reg_after - reg_before

        def by(label, prop):
            return list(s.run(
                f"MATCH (x:{label} {{rom:$rom}}) WHERE x.{prop} <> '' "
                f"RETURN x.{prop} AS v, count(*) AS n ORDER BY n DESC",
                rom=rom,
            ))

        fr = s.run(
            "MATCH (f:Func {rom:$rom}) WHERE f.confidence <> '' RETURN count(f) AS n", rom=rom
        ).single()["n"]
        vr = s.run(
            "MATCH (x:Reg {rom:$rom}) WHERE x.confidence <> '' RETURN count(x) AS n", rom=rom
        ).single()["n"]
        print(f"Memgraph: :Func размечено {fr}, :Reg размечено {vr} "
              f"(:Reg создано base+offset: {created})")
        print("  :Func по role:   " + ", ".join(f"{r['v']}={r['n']}" for r in by("Func", "role")))
        print("  :Func по уровню: " + ", ".join(
            f"{r['v']}={r['n']}" for r in by("Func", "confidence")))
        print("  :Reg по уровню:  " + ", ".join(
            f"{r['v']}={r['n']}" for r in by("Reg", "confidence")))

        edges, gaps = build_rests_on(s, rom, funcs, vars_)
        roles = Counter(e["role"] for e in edges)
        tgt = Counter(e["dl"] for e in edges)
        print(f"  :RESTS_ON рёбер: {len(edges)} "
              f"(цели: {', '.join(f'{k}={n}' for k, n in tgt.most_common())})")
        print("  по роли: " + ", ".join(f"{k}={n}" for k, n in roles.most_common()))

        # Ворота раздела 8: свидетельство резолвимо, ворота уровня замкнуты.
        code = [r for r in funcs + vars_ if r["confidence"] == "code"]
        with_edge = sum(
            1 for r in code
            if [1 for role, v in r["_toks"] if role in EDGE_ROLES and ADDR_RE.match(v)]
        )
        print(f"  выводы code: {len(code)}; с ребром {with_edge}, "
              f"только терминал {len(code) - with_edge}")
        if gaps:
            uniq = sorted({g[2] for g in gaps})
            print(f"  пробелы каталога (ссылка на карту вне графа): {len(gaps)} "
                  f"в {len(uniq)} адресах - {', '.join(uniq)}")

    driver.close()


if __name__ == "__main__":
    main()
