#!/usr/bin/env python3
# Загрузка калибровочного слоя (Stage 3, разделы 5 и 7 tools/map-flag-pipeline.md) из
# accessors.csv (ResolveAccessors.java) в Memgraph: узлы :Interp/:Map/:Axis и рёбра
# :ACCESSES/:VIA/:KERNEL/:AXIS_X/:AXIS_Y. Переносит в граф то, чего :CALLS не несёт, -
# операнды вызова: какая таблица и какие оси переданы аксессором в r4/r5/r6 (P2).
#
# Идёт после load_graph.py: :Func этого rom - его слой, а тот при перезагрузке узлы rom
# пересоздаёт, снося вместе с ними рёбра :ACCESSES. Аксессор, которого нет в :Func,
# создаётся здесь (счётчик в отчёте) - ненулевой счётчик означает, что граф собран до
# разметки RecoverFuncs.java (Stage 0) и его надо переэкспортировать.
#
# Что переносится как факт, а что нет:
#   - база карты (r4) и оси (r5/r6) - только значения, указывающие в ROM. Runtime-вход
#     (текущее значение оси в RAM, индекс, маска) базой не является и осью не считается;
#     он остаётся на ребре :ACCESSES в r4/r5/r6 как снятое значение, но узла не создаёт.
#   - dims - свойство обёртки (обёртка специализирована по размерности), а не отдельного
#     сайта: у 2D-обёрток вторую ось несут все сайты, у 1D - ни один. Признак разделяет
#     обёртки JK03A начисто (10 обёрток - 100% сайтов с осью в r6, 0x264a0 - 0%), кроме
#     0x26474: 2 сайта из 47 дают в r6 ROM-адрес. Там r6 аргументом не является, и это
#     значение регистра, снятое резервом на адресе сайта, а не ось. Поэтому размерность
#     берётся большинством сайтов обёртки, а r6 читается осью только у 2D-обёрток;
#     отброшенные значения считаются в отчёте. Геометрия (width/height, storagetype,
#     scaling, монотонность и kind оси) - Stage 4, здесь не заполняется.
#   - соглашение осей: r5 -> :AXIS_X, r6 -> :AXIS_Y; регистр-источник сохраняется на ребре
#     (reg), поэтому ориентация уточняется в Stage 4 без потери факта.
#   - verdict=conflict: базы bt и df расходятся, обе валидны и обе идут в граф картами
#     (src на ребре :ACCESSES). Ветвление, выбирающее одну из них, - :Flag {role:'selector'}
#     в Stage 6; до него обе карты равноправны.
# Уровень всего слоя - candidate (раздел 5): резолвер дал операнды, семантика не прослежена.
#
# Запуск: uv run --no-project --with neo4j python tools/memgraph/load_maps.py \
#           <export_dir> <rom_label> [kernel_hex]
# По умолчанию export_dir = ~/tools/ghidra-projects/export-JK03A, rom = JK03A,
# kernel = 26944.
import csv
import os
import sys
from neo4j import GraphDatabase

BOLT = "bolt://localhost:7687"

# Границы ROM: ниже ROM_LO лежат векторы прерываний, а снятые из r6/r7 малые значения -
# runtime-скаляры (индекс, маска), не базы. ROM_HI - размер образа.
ROM_LO = 0x1000
ROM_HI = 0x180000


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def rom_addr(v):
    """Адрес в ROM (база карты или оси) либо None, если значение базой быть не может."""
    if not v:
        return None
    return v if ROM_LO <= int(v, 16) < ROM_HI else None


def wrapper_dims(rows):
    """Размерность обёрток по большинству их сайтов: 2D несёт вторую ось в r6."""
    total, with_y = {}, {}
    for r in rows:
        w = r["wrapper"]
        total[w] = total.get(w, 0) + 1
        if rom_addr(r["df_r6"]):
            with_y[w] = with_y.get(w, 0) + 1
    return {w: (2 if with_y.get(w, 0) * 2 > n else 1) for w, n in total.items()}


def build(rows, kernel):
    """CSV резолвера -> узлы и рёбра калибровочного слоя."""
    maps, axes, interps, accesses = {}, {}, {}, []
    interps[kernel] = {"addr": kernel, "role": "kernel", "slot": "", "dims": None}
    wdims = wrapper_dims(rows)
    dropped = 0                                   # r6-значения вне 2D-обёрток: не оси

    for r in rows:
        w = r["wrapper"]
        interps.setdefault(
            w, {"addr": w, "role": "wrapper", "slot": r["slot"], "dims": wdims[w]}
        )

        dims = wdims[w]
        ax = rom_addr(r["df_r5"])
        ay = rom_addr(r["df_r6"]) if dims == 2 else None
        if dims == 1 and rom_addr(r["df_r6"]):
            dropped += 1
        for a in (ax, ay):
            if a:
                axes.setdefault(a, {"addr": a, "confidence": "candidate"})

        # База df - основная; на conflict вторая (bt) валидна тоже: обе идут картами.
        bases = []
        d4, b4 = rom_addr(r["df_r4"]), rom_addr(r["bt_r4"])
        if d4:
            bases.append((d4, "df", r["k4"]))
        if r["verdict"] == "conflict" and b4 and b4 != d4:
            bases.append((b4, "bt", "nearest"))

        for base, src, kind in bases:
            m = maps.setdefault(
                base, {"addr": base, "dims": dims, "confidence": "candidate", "evidence": []}
            )
            m["dims"] = max(m["dims"], dims)          # 2D-доступ к карте важнее 1D
            tag = f"{src}:{kind}"
            if tag not in m["evidence"]:
                m["evidence"].append(tag)
            accesses.append(
                {
                    "accessor": r["accessor"],
                    "callsite": r["callsite"],
                    "base": base,
                    "wrapper": w,
                    "src": src,
                    "kind": kind,
                    "verdict": r["verdict"],
                    "r4": r["df_r4"],
                    "r5": r["df_r5"],
                    "r6": r["df_r6"],
                    "axis_x": ax or "",
                    "axis_y": ay or "",
                }
            )

    for m in maps.values():
        m["evidence"] = sorted(m["evidence"])
    return maps, axes, interps, accesses, dropped


def main():
    default_dir = os.path.expanduser("~/tools/ghidra-projects/export-JK03A")
    outdir = sys.argv[1] if len(sys.argv) > 1 else default_dir
    rom = sys.argv[2] if len(sys.argv) > 2 else "JK03A"
    kernel = (sys.argv[3] if len(sys.argv) > 3 else "26944").lower().rjust(8, "0")

    rows = read_csv(os.path.join(outdir, "accessors.csv"))
    maps, axes, interps, accesses, dropped = build(rows, kernel)
    d2 = sum(1 for i in interps.values() if i["dims"] == 2)
    print(f"CSV: {len(rows)} сайтов; rom={rom} kernel={kernel}")
    print(
        f"Слой: {len(maps)} карт, {len(axes)} осей, {len(interps)} узлов интерполяции "
        f"({d2} обёрток 2D), {len(accesses)} доступов"
    )
    if dropped:
        print(f"  r6 у 1D-обёрток осью не считан: {dropped} значений (не аргумент вызова)")

    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    with driver.session() as s:
        for lbl in ("Map", "Axis", "Interp"):
            s.run(f"MATCH (n:{lbl} {{rom:$rom}}) DETACH DELETE n", rom=rom)
            for prop in ("addr", "rom"):
                try:
                    s.run(f"CREATE INDEX ON :{lbl}({prop})")
                except Exception:
                    pass

        # Аксессор без узла :Func - признак графа, собранного до разметки Stage 0.
        orphan = s.run(
            """
            UNWIND $addrs AS a
            OPTIONAL MATCH (f:Func {rom:$rom, addr:a})
            WITH a, f WHERE f IS NULL
            RETURN count(DISTINCT a) AS n
            """,
            addrs=sorted({x["accessor"] for x in accesses}),
            rom=rom,
        ).single()["n"]

        s.run(
            """
            UNWIND $rows AS r
            MERGE (i:Interp {rom:$rom, addr:r.addr})
            SET i.role = r.role, i.slot = r.slot, i.dims = r.dims
            """,
            rows=list(interps.values()),
            rom=rom,
        )
        s.run(
            """
            UNWIND $rows AS r
            MERGE (m:Map {rom:$rom, addr:r.addr})
            SET m.dims = toInteger(r.dims), m.confidence = r.confidence,
                m.evidence = r.evidence
            """,
            rows=list(maps.values()),
            rom=rom,
        )
        s.run(
            """
            UNWIND $rows AS r
            MERGE (x:Axis {rom:$rom, addr:r.addr})
            SET x.confidence = r.confidence
            """,
            rows=list(axes.values()),
            rom=rom,
        )
        s.run(
            """
            MATCH (w:Interp {rom:$rom, role:'wrapper'}), (k:Interp {rom:$rom, addr:$kernel})
            MERGE (w)-[:KERNEL]->(k)
            """,
            rom=rom,
            kernel=kernel,
        )
        s.run(
            """
            UNWIND $rows AS r
            MERGE (a:Func {rom:$rom, addr:r.accessor})
            WITH a, r
            MATCH (m:Map {rom:$rom, addr:r.base})
            MERGE (a)-[x:ACCESSES {callsite:r.callsite, base:r.base}]->(m)
            SET x.r4 = r.r4, x.r5 = r.r5, x.r6 = r.r6,
                x.src = r.src, x.kind = r.kind, x.verdict = r.verdict
            """,
            rows=accesses,
            rom=rom,
        )
        s.run(
            """
            UNWIND $rows AS r
            MATCH (m:Map {rom:$rom, addr:r.base}), (w:Interp {rom:$rom, addr:r.wrapper})
            MERGE (m)-[:VIA]->(w)
            """,
            rows=accesses,
            rom=rom,
        )
        for reg, edge, key in (("r5", "AXIS_X", "axis_x"), ("r6", "AXIS_Y", "axis_y")):
            s.run(
                f"""
                UNWIND $rows AS r
                MATCH (m:Map {{rom:$rom, addr:r.base}}), (x:Axis {{rom:$rom, addr:r.{key}}})
                MERGE (m)-[e:{edge}]->(x)
                SET e.reg = '{reg}'
                """,
                rows=[r for r in accesses if r[key]],
                rom=rom,
            )

        counts = s.run(
            """
            MATCH (m:Map {rom:$rom}) WITH count(m) AS maps
            MATCH (x:Axis {rom:$rom}) WITH maps, count(x) AS axes
            MATCH (:Func {rom:$rom})-[a:ACCESSES]->(:Map {rom:$rom})
            WITH maps, axes, count(a) AS acc
            MATCH (:Map {rom:$rom})-[v:VIA]->(:Interp {rom:$rom})
            RETURN maps, axes, acc, count(v) AS via
            """,
            rom=rom,
        ).single()
        print(
            f"Memgraph: {counts['maps']} :Map, {counts['axes']} :Axis, "
            f"{counts['acc']} :ACCESSES, {counts['via']} :VIA"
        )
        if orphan:
            print(
                f"ВНИМАНИЕ: {orphan} аксессоров нет в :Func - граф собран до разметки "
                f"Stage 0; переэкспортировать (RecoverFuncs.java + ExportGraph.java)"
            )

        print("Карты по обёрткам (каталог Stage 2):")
        rows_out = s.run(
            """
            MATCH (m:Map {rom:$rom})-[:VIA]->(w:Interp {rom:$rom})
            RETURN w.addr AS wrapper, count(DISTINCT m) AS maps,
                   count(DISTINCT CASE WHEN m.dims = 2 THEN m END) AS d2
            ORDER BY maps DESC
            """,
            rom=rom,
        )
        for r in rows_out:
            print(f"  обёртка {r['wrapper']}  карт {r['maps']:>3}  из них 2D {r['d2']:>3}")

    driver.close()


if __name__ == "__main__":
    main()
