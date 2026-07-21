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
# На этом шаге оно кладётся свойством; рёбра :RESTS_ON и ворота уровня строит шаг 2
# раздела 7 отдельно (структурный факт без провенанса при автоматике усиливает ошибку).
#
# Запуск: uv run --no-project --with neo4j python tools/memgraph/load_code.py [rom]
# По умолчанию rom = JK03A.
import csv
import os
import re
import sys

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


def check(funcs, vars_, fpath, vpath):
    """Отказы, в графе неотличимые от факта, ловятся до загрузки (как в load_vendor)."""
    check_addrs_uniq(funcs, fpath)
    check_addrs_uniq(vars_, vpath)

    bad = sorted({r["role"] for r in funcs} - FUNC_ROLES)
    if bad:
        sys.exit(f"{fpath}: неизвестный role {bad}; добавить в FUNC_ROLES, если легитимен")
    bad = sorted({r["confidence"] for r in funcs + vars_} - LEVELS)
    if bad:
        sys.exit(f"funcs/vars: confidence вне лестницы {sorted(LEVELS)}: {bad}")


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

        # Ворота шага 2 (раздел 7) ещё не действуют: :RESTS_ON строится отдельно.
        ro = s.run("MATCH ()-[e:RESTS_ON]->() RETURN count(e) AS n").single()["n"]
        print(f"  :RESTS_ON рёбер: {ro} (ворота уровня - шаг 2 раздела 7, отдельный инкремент)")

    driver.close()


if __name__ == "__main__":
    main()
