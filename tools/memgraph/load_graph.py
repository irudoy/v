#!/usr/bin/env python3
# Load a call graph (funcs.csv + calls.csv of the L0 of the ROM's layout) into Memgraph and
# cluster subsystems with Louvain on this ROM's call-graph projection. Nodes are
# :Func {rom,addr,name,size,is_thunk,is_external}; relationships are
# (:Func)-[:CALLS]->(:Func). A function takes its curated name from
# tools/ghidra/symbols/<layout>.csv and FUN_<addr> otherwise. Repeated runs for the same ROM
# are idempotent because its nodes are recreated.
#
# Invocation: uv run python tools/memgraph/load_graph.py \
#           <l0_dir> <rom_label>
# Defaults: l0_dir = the L0 of the ROM's layout, rom = 1ND0A.
import csv
import os
from pathlib import Path
import sys
from neo4j import GraphDatabase

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rom_sources  # noqa: E402

BOLT = "bolt://localhost:7687"


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def main():
    rom = sys.argv[2] if len(sys.argv) > 2 else "1ND0A"
    outdir = sys.argv[1] if len(sys.argv) > 1 else str(rom_sources.l0_dir(rom))

    names = rom_sources.function_names(rom)
    funcs = [
        {**row, "name": rom_sources.function_name(names, row["addr"])}
        for row in read_csv(os.path.join(outdir, "funcs.csv"))
    ]
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

        # Louvain on this ROM's call-graph projection sees only :Func and CALLS.
        # Clustering the whole storage is invalid because :Reg connects any functions that
        # access the same address and collapses the graph into one megacluster. Functions
        # without calls are absent from the projection and remain without a community.
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
        print(f"Louvain: {nc} communities, {iso} functions without calls (outside projection)")
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
