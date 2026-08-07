#!/usr/bin/env python3
# Add a peripheral-access layer (xrefs.csv from ExportXrefs.java) over the Memgraph call
# graph. Creates :Reg {addr,region,name} nodes and (:Func)-[:USES {kind}]->(:Reg)
# relationships; sets aggregates on :Func (n_can, n_sci, n_rxpr, n_ram). SH7058/59 register
# regions and names come from the Renesas datasheet. Finally, prints immo candidates
# (CAN/SCI communication functions and RXPR readers).
#
# Invocation: uv run python tools/memgraph/load_xrefs.py \
#           <export_dir> <rom_label>
import csv
import os
import sys
from neo4j import GraphDatabase

BOLT = "bolt://localhost:7687"

CAN_OFFS = {0x00: "MCR", 0x02: "GSR", 0x04: "BCR1", 0x06: "BCR0", 0x08: "IRR",
            0x0A: "IMR", 0x20: "TXPR", 0x28: "TXCR", 0x30: "TXACK", 0x38: "ABACK",
            0x40: "RXPR", 0x48: "RFPR", 0x50: "MBIMR", 0x58: "UMSR", 0x80: "TCNTR"}
SCI_OFFS = {0: "SMR", 1: "BRR", 2: "SCR", 3: "TDR", 4: "SSR", 5: "RDR", 6: "SDCR"}


def classify(addr):
    if 0xFFFFD000 <= addr <= 0xFFFFDFFF:
        base = 0xFFFFD000 if addr < 0xFFFFD800 else 0xFFFFD800
        ch = 0 if base == 0xFFFFD000 else 1
        off = addr - base
        if off >= 0x100:
            return "CAN", f"HCAN{ch}_MB{(off - 0x100) // 0x20}"
        return "CAN", f"HCAN{ch}_" + CAN_OFFS.get(off & 0xFE, f"{off:03x}")
    if 0xFFFFF000 <= addr <= 0xFFFFF027:
        ch = (addr - 0xFFFFF000) // 8
        off = (addr - 0xFFFFF000) % 8
        return "SCI", f"SCI{ch}_" + SCI_OFFS.get(off, f"{off}")
    if 0xFFFFF720 <= addr <= 0xFFFFF77F:
        return "PORT", f"PORT_{addr:08x}"
    if 0xFFFE8000 <= addr <= 0xFFFF3FFF:            # on-chip RAM SH7059 (48 KB)
        return "RAM", f"RAM_{addr:08x}"
    if 0xFFFFC000 <= addr <= 0xFFFFFFFF:
        return "REG", f"REG_{addr:08x}"
    return "OTHER", f"{addr:08x}"


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def main():
    default_dir = os.path.expanduser("~/tools/ghidra-projects/export-1ND0A")
    outdir = sys.argv[1] if len(sys.argv) > 1 else default_dir
    rom = sys.argv[2] if len(sys.argv) > 2 else "1ND0A"

    rows = read_csv(os.path.join(outdir, "xrefs.csv"))
    edges, regs = [], {}
    for r in rows:
        addr = int(r["periph_addr"], 16)
        region, name = classify(addr)
        regs[r["periph_addr"]] = {"addr": r["periph_addr"], "region": region, "name": name}
        edges.append({"func": r["func_addr"], "reg": r["periph_addr"], "kind": r["kind"]})
    print(f"xrefs: {len(edges)} edges, {len(regs)} distinct registers; rom={rom}")

    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    with driver.session() as s:
        s.run("MATCH (r:Reg {rom:$rom}) DETACH DELETE r", rom=rom)
        try:
            s.run("CREATE INDEX ON :Reg(addr)")
        except Exception:
            pass
        s.run(
            """
            UNWIND $regs AS r
            MERGE (x:Reg {rom:$rom, addr:r.addr})
            SET x.region = r.region, x.name = r.name
            """,
            regs=list(regs.values()),
            rom=rom,
        )
        s.run(
            """
            UNWIND $edges AS e
            MATCH (f:Func {rom:$rom, addr:e.func})
            MATCH (x:Reg  {rom:$rom, addr:e.reg})
            MERGE (f)-[u:USES {kind:e.kind}]->(x)
            """,
            edges=edges,
            rom=rom,
        )
        # Aggregates on functions.
        for prop, cond in (
            ("n_can", "r.region='CAN'"),
            ("n_sci", "r.region='SCI'"),
            ("n_rxpr", "r.name CONTAINS 'RXPR'"),
            ("n_ram", "r.region='RAM'"),
        ):
            s.run(
                f"MATCH (f:Func {{rom:$rom}})-[:USES]->(r:Reg {{rom:$rom}}) WHERE {cond} "
                f"WITH f, count(DISTINCT r) AS n SET f.{prop} = n",
                rom=rom,
            )

        nr = s.run("MATCH (r:Reg {rom:$rom}) RETURN count(r) AS n", rom=rom).single()["n"]
        nu = s.run(
            "MATCH (:Func {rom:$rom})-[u:USES]->(:Reg {rom:$rom}) RETURN count(u) AS n",
            rom=rom,
        ).single()["n"]
        print(f"Memgraph: {nr} :Reg nodes, {nu} :USES edges")

        print("\n=== CAN communication functions (immo candidates; RXPR readers marked) ===")
        rows = s.run(
            """
            MATCH (f:Func {rom:$rom})-[:USES]->(r:Reg {rom:$rom, region:'CAN'})
            WITH f, count(DISTINCT r) AS can_regs,
                 count(DISTINCT CASE WHEN r.name CONTAINS 'RXPR' THEN r END) AS rxpr,
                 collect(DISTINCT r.name)[0..8] AS regs
            RETURN f.addr AS addr, f.name AS name, can_regs, rxpr, regs
            ORDER BY rxpr DESC, can_regs DESC LIMIT 25
            """,
            rom=rom,
        )
        for r in rows:
            flag = " <-RX" if r["rxpr"] else ""
            print(f"  {r['addr']}  can={r['can_regs']:>2} rxpr={r['rxpr']}{flag}  "
                  f"{', '.join(r['regs'])}")

        print("\n=== functions using BOTH CAN and SCI (protocol bridges) ===")
        rows = s.run(
            """
            MATCH (f:Func {rom:$rom})-[:USES]->(c:Reg {rom:$rom, region:'CAN'})
            MATCH (f)-[:USES]->(sc:Reg {rom:$rom, region:'SCI'})
            RETURN f.addr AS addr, count(DISTINCT c) AS can, count(DISTINCT sc) AS sci
            ORDER BY can+sci DESC LIMIT 15
            """,
            rom=rom,
        )
        for r in rows:
            print(f"  {r['addr']}  can={r['can']} sci={r['sci']}")

    driver.close()


if __name__ == "__main__":
    main()
