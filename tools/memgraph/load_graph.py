#!/usr/bin/env python3
# Загрузка call-графа Ghidra (funcs.csv + calls.csv из ExportGraph.java) в Memgraph
# и кластеризация подсистем (Louvain на проекции call-графа этого rom). Узлы
# :Func {rom,addr,name,size,is_thunk,is_external}, рёбра (:Func)-[:CALLS]->(:Func).
# Повторный прогон для того же rom идемпотентен (узлы этого rom пересоздаются).
#
# Запуск: uv run --no-project --with neo4j python tools/memgraph/load_graph.py \
#           <export_dir> <rom_label>
# По умолчанию export_dir = ~/tools/ghidra-projects/export-1ND0A, rom = 1ND0A.
import csv
import os
import sys
from neo4j import GraphDatabase

BOLT = "bolt://localhost:7687"


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def main():
    default_dir = os.path.expanduser("~/tools/ghidra-projects/export-1ND0A")
    outdir = sys.argv[1] if len(sys.argv) > 1 else default_dir
    rom = sys.argv[2] if len(sys.argv) > 2 else "1ND0A"

    funcs = read_csv(os.path.join(outdir, "funcs.csv"))
    calls = read_csv(os.path.join(outdir, "calls.csv"))
    print(f"CSV: {len(funcs)} funcs, {len(calls)} calls; rom={rom}")

    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    with driver.session() as s:
        s.run("MATCH (n:Func {rom:$rom}) DETACH DELETE n", rom=rom)
        for idx in ("CREATE INDEX ON :Func(addr)", "CREATE INDEX ON :Func(rom)"):
            try:
                s.run(idx)
            except Exception:
                pass

        s.run(
            """
            UNWIND $rows AS r
            MERGE (f:Func {rom:$rom, addr:r.addr})
            SET f.name = r.name,
                f.size = toInteger(r.size),
                f.is_thunk = (r.is_thunk = 'true'),
                f.is_external = (r.is_external = 'true')
            """,
            rows=funcs,
            rom=rom,
        )
        s.run(
            """
            UNWIND $rows AS r
            MATCH (a:Func {rom:$rom, addr:r.src})
            MATCH (b:Func {rom:$rom, addr:r.dst})
            MERGE (a)-[:CALLS]->(b)
            """,
            rows=calls,
            rom=rom,
        )

        nn = s.run("MATCH (f:Func {rom:$rom}) RETURN count(f) AS n", rom=rom).single()["n"]
        ne = s.run(
            "MATCH (:Func {rom:$rom})-[c:CALLS]->(:Func {rom:$rom}) RETURN count(c) AS n",
            rom=rom,
        ).single()["n"]
        print(f"Memgraph: {nn} nodes, {ne} CALLS edges")

        # Louvain на проекции call-графа этого rom: алгоритму видны только :Func и
        # CALLS. По всему storage кластеризация непригодна - :Reg связывает любые две
        # функции, обращающиеся к общему адресу, и граф схлопывается в один мегакластер.
        # Функции без вызовов в проекцию не входят и остаются без community.
        s.run("MATCH (f:Func {rom:$rom}) REMOVE f.community", rom=rom)
        s.run(
            """
            MATCH p=(:Func {rom:$rom})-[:CALLS]->(:Func {rom:$rom})
            WITH project(p) AS g
            CALL community_detection.get(g) YIELD node, community_id
            SET node.community = community_id
            """,
            rom=rom,
        )
        nc = s.run(
            "MATCH (f:Func {rom:$rom}) WHERE f.community IS NOT NULL "
            "RETURN count(DISTINCT f.community) AS c",
            rom=rom,
        ).single()["c"]
        iso = s.run(
            "MATCH (f:Func {rom:$rom}) WHERE f.community IS NULL RETURN count(f) AS n",
            rom=rom,
        ).single()["n"]
        print(f"Louvain: {nc} communities, {iso} функций без вызовов (вне проекции)")
        print("Top communities (size, sample funcs):")
        rows = s.run(
            """
            MATCH (f:Func {rom:$rom}) WHERE f.community IS NOT NULL
            WITH f.community AS c, count(*) AS n, collect(f.name)[0..6] AS sample
            RETURN c, n, sample ORDER BY n DESC LIMIT 15
            """,
            rom=rom,
        )
        for r in rows:
            print(f"  c={r['c']:>5}  n={r['n']:>4}  {', '.join(r['sample'])}")

    driver.close()


if __name__ == "__main__":
    main()
