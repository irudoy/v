#!/usr/bin/env python3
# Генератор дефа RomRaider (Stage 8, раздел 9 tools/map-flag-pipeline.md): граф Memgraph
# (факты) + defs/<rom>.overrides.toml (презентация) -> defs/<rom>.xml.
#
# Разделение источников - причина существования этого шага (P5). Факт объявлен один раз:
# адрес, форма, элемент, оси, шкала и уровень живут в графе, куда их кладут перепись
# резолвера и ручной слой; имя, категория, порядок и шаги редактора - в оверрайдах. Деф
# не источник ни того ни другого, и правка деф-файла не переживает следующего прогона.
#
# Ворота эмиссии (раздел 9): таблица выпускается, если её можно прочитать, то есть у неё
# есть роль table, семантика и шкала. Без семантики карта - адрес и форма, без шкалы -
# сетка сырых байтов; и то и другое уже есть в ledger'е, который для того и существует.
# Отброшенное перечисляется в отчёте: молчаливый пропуск читался бы как отсутствие карты.
#
# Разметка уровня идёт туда, где живёт само утверждение:
#   карта ниже code  -> категория с суффиксом " (candidate)": опознана, но не трейсом;
#   шкала ниже code  -> единицы с суффиксом " [cand]": множитель не закреплён кодом.
# Уровни обоих утверждений плюс доказательства выписываются в комментарий над таблицей.
#
# Перевод осей обёртки в оси RomRaider (снят с finisher'ов, см. defs/<rom>.notes.md):
# finisher адресует ячейку как cell = table + idxY + width*idxX, где idxX - позиция по
# оси из r5. Значит ось r5 (граф :AXIS_X) - строки, ось r6 (:AXIS_Y) - столбцы, а
# RomRaider называет столбцы X Axis, строки - Y Axis. Отсюда перекрёст: :AXIS_X -> Y Axis,
# :AXIS_Y -> X Axis. У одномерной карты ось одна, и RomRaider зовёт её X Axis.
#
# Запуск: uv run --no-project --with neo4j python tools/mapkit/emit_def.py [<rom>] [<out>]
import html
import os
import sys
import textwrap
import tomllib
from neo4j import GraphDatabase

BOLT = "bolt://localhost:7687"
DEFS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "defs")
LEVELS = ("pattern", "candidate", "code", "silicon")   # лестница раздела 5

ROMID_FIELDS = ("xmlid", "internalidaddress", "internalidstring", "ecuid", "caseid",
                "make", "model", "submodel", "market", "transmission", "memmodel",
                "endian", "flashmethod", "filesize", "author", "version")
CHECKSUM_FIELDS = (
    "type", "path", "expectedsize",
    "l1loc", "l1stock", "l1patched",
    "l2loc", "l2stock", "l2patched",
    "start", "end", "skiploc", "sumloc", "xorloc",
)
SWITCH_FIELDS = (
    "name", "category", "storageaddress", "storagetype", "sizex", "endian",
    "userlevel",
)
# Имя оси по её семантике. Ось общая у нескольких карт, поэтому имя задаётся один раз
# здесь, а не на карту; частный случай перекрывается [axis.<addr>] в оверрайдах.
AXIS_NAMES = {"rpm": "Engine Speed [RPM]", "load": "Engine Load",
              "temp": "Temperature", "raw": "Axis (raw)"}


def att(v):
    return html.escape(str(v), quote=True)


def hexa(a):
    """Адрес графа (8 hex-цифр) -> форма RomRaider."""
    return "0x" + a.upper().lstrip("0").rjust(5, "0")


def comment(lines, indent=4):
    """Комментарий XML: '--' внутри него недопустимо, поэтому сводится к '-'."""
    pad = " " * indent
    body = []
    for l in lines:
        l = l.replace("--", "-").rstrip()
        body += textwrap.wrap(l, 96 - indent - 5) or [""]
    while body and not body[-1]:
        body.pop()
    out = [(f"{pad}<!-- " + body[0]).rstrip()]
    out += [(pad + "     " + l).rstrip() for l in body[1:]]
    return "\n".join(out) + " -->"


def wrap(pad, head, attrs, tail):
    """Тег с переносом атрибутов по ширине строки; продолжение под первым атрибутом."""
    lines, cur = [], pad + head
    for a in attrs:
        if len(cur) + 1 + len(a) > 96:
            lines.append(cur)
            cur = pad + " " * len(head)
        cur += " " + a
    lines.append(cur + tail)
    return lines


def scaling(units, expr, to_byte, conf, fmt, fine, coarse, indent):
    """Блок <scaling>. Единицы несут суффикс, когда множитель кодом не закреплён."""
    if conf and conf != "code":
        units += " [cand]"
    a = [f'units="{att(units)}"', f'expression="{att(expr)}"',
         f'to_byte="{att(to_byte)}"', f'format="{att(fmt)}"']
    if fine is not None:
        a.append(f'fineincrement="{att(fine)}"')
    if coarse is not None:
        a.append(f'coarseincrement="{att(coarse)}"')
    return "\n".join(wrap(" " * indent, "<scaling", a, "/>"))


def fetch(rom):
    """Факты калибровочного слоя: карты-кандидаты на эмиссию, их оси и окружение."""
    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    with driver.session() as s:
        maps = {r["a"]: dict(r["m"]) for r in s.run(
            "MATCH (m:Map {rom:$rom}) RETURN m.addr AS a, m AS m", rom=rom)}
        for r in s.run(
                """
                MATCH (m:Map {rom:$rom})-[:VIA]->(w:Interp {rom:$rom})
                OPTIONAL MATCH (w)-[:KERNEL]->(k:Interp {rom:$rom})
                RETURN m.addr AS a, collect(DISTINCT w.addr) AS wrappers,
                       collect(DISTINCT w.step) AS steps,
                       collect(DISTINCT k.addr) AS kernels
                """, rom=rom):
            maps[r["a"]].update(wrappers=r["wrappers"], steps=[x for x in r["steps"] if x],
                                kernels=r["kernels"])
        for r in s.run(
                """
                MATCH (f:Func)-[e:ACCESSES]->(m:Map {rom:$rom})
                RETURN m.addr AS a, collect(DISTINCT f.addr) AS accessors
                """, rom=rom):
            maps[r["a"]]["accessors"] = r["accessors"]
        axes = {r["a"]: dict(r["x"]) for r in s.run(
            "MATCH (x:Axis {rom:$rom}) RETURN x.addr AS a, x AS x", rom=rom)}
        # Осей на ребре может быть больше одной: ось выбирает ветвление, и резолвер видит
        # на каждом сайте свою. Это не ошибка загрузки, а неоднозначность геометрии, и
        # разбирает её Stage 6; здесь она просто закрывает карте ворота эмиссии.
        for edge in ("AXIS_X", "AXIS_Y"):
            for r in s.run(
                    f"""
                    MATCH (m:Map {{rom:$rom}})-[:{edge}]->(x:Axis {{rom:$rom}})
                    RETURN m.addr AS a, collect(DISTINCT x.addr) AS ax
                    """, rom=rom):
                maps[r["a"]][edge.lower()] = r["ax"]
    driver.close()
    for m in maps.values():
        for k in ("wrappers", "kernels", "steps", "accessors", "axis_x", "axis_y"):
            m.setdefault(k, [])
    return maps, axes


def axis_xml(kind, x, ovr, size_attr, indent=6):
    """Ось-массив в ПЗУ: адрес, элемент и длина - факты графа, имя - презентация."""
    o = ovr.get("axis", {}).get(x["addr"], {})
    name = o.get("name") or AXIS_NAMES[x["kind"]]
    pad = " " * indent
    out = wrap(pad, "<table", [f'type="{kind}"', f'name="{att(name)}"',
                               f'storagetype="{att(x["storagetype"])}"',
                               f'storageaddress="{hexa(x["addr"])}"',
                               f'{size_attr}="{x["len"]}"', 'endian="big"'], ">")
    out.append(scaling(x["units"], x["scale_expr"], x["to_byte"], x["scale_conf"],
                       o.get("format", "0"), o.get("fine"), o.get("coarse"), indent + 2))
    out.append(f"{pad}</table>")
    return out


def static_axis_xml(values, name="Index", indent=6):
    pad = " " * indent
    out = [f'{pad}<table type="Static X Axis" name="{att(name)}" sizex="{len(values)}">']
    for i in range(0, len(values), 4):
        out.append(pad + "  " + "".join(f"<data>{att(v)}</data>"
                                        for v in values[i:i + 4]))
    out.append(f"{pad}</table>")
    return out


def switch_xml(entry, index):
    """Пользовательский TableSwitch из overrides: адрес и именованные состояния."""
    if not isinstance(entry, dict):
        sys.exit(f"switch #{index} должен быть таблицей TOML")
    unknown = sorted(set(entry) - set(SWITCH_FIELDS) - {"description", "state"})
    if unknown:
        sys.exit(f"switch #{index} содержит неизвестные поля {', '.join(unknown)}")
    missing = [k for k in SWITCH_FIELDS if k not in entry]
    if missing:
        sys.exit(f"switch #{index} без полей {', '.join(missing)}")
    states = entry.get("state", [])
    if not isinstance(states, list) or len(states) < 2:
        sys.exit(f"switch #{index}: нужен массив state минимум из двух состояний")

    attrs = ['type="Switch"'] + [
        f'{k}="{att(entry[k])}"' for k in SWITCH_FIELDS
    ]
    out = wrap("    ", "<table", attrs, ">")
    if entry.get("description"):
        out.append(f"      <description>{att(entry['description'])}</description>")
    for state_index, state in enumerate(states, 1):
        if not isinstance(state, dict):
            sys.exit(f"switch #{index}, state #{state_index} должен быть таблицей TOML")
        unknown_state = sorted(set(state) - {"name", "data"})
        if unknown_state:
            sys.exit(f"switch #{index}, state #{state_index} содержит неизвестные поля "
                     + ", ".join(unknown_state))
        missing_state = [k for k in ("name", "data") if k not in state]
        if missing_state:
            sys.exit(f"switch #{index}, state #{state_index} без полей "
                     + ", ".join(missing_state))
        out += wrap("      ", "<state",
                    [f'name="{att(state["name"])}"', f'data="{att(state["data"])}"'],
                    "/>")
    out.append("    </table>")
    return out


def evidence_lines(m, axes, rom):
    """Блок доказательств: что известно о карте и на каком уровне."""
    shape = (f'{m["width"]}x{m["height"]}' if m["dims"] == 2 else f'{m["width"]}')
    via = ""
    if m["wrappers"]:
        via = (f'; вход {", ".join(hexa(w) for w in sorted(m["wrappers"]))} '
               f'({m["family"]}, ядро {", ".join(hexa(k) for k in sorted(m["kernels"]))})')
    lines = [f'{hexa(m["addr"])}  {shape} {m["storagetype"]}  '
             f'карта [{m["confidence"]}]{via}']
    if m["accessors"]:
        lines.append("аксессор " + ", ".join(hexa(a) for a in sorted(m["accessors"]))
                     + "; операнд r4: " + ", ".join(sorted(m["resolver_kinds"])))
    scale = f'шкала {m["scale_expr"]} {m["units"]}'
    if m["scale_conf"]:
        scale += f' [{m["scale_conf"]}]'
    for role, key in (("Y", "axis_x"), ("X", "axis_y")):
        for x in (axes[a] for a in m[key]):
            lbl = "ось" if m["dims"] == 1 else f"{role} Axis"
            scale += (f'; {lbl} {hexa(x["addr"])} {x["kind"]}'
                      + (f' [{x["scale_conf"]}]' if x["scale_conf"] else ""))
    lines.append(scale)
    if m["note"]:
        lines.append(m["note"])
    lines.append(f"Разбор и метод - defs/{rom}.notes.md")
    return lines


def table_xml(m, ovr, axes, rom):
    o = ovr["table"][m["addr"]]
    cat = o["category"] + ("" if m["confidence"] == "code" else " (candidate)")
    dims = "3D" if m["dims"] == 2 else "2D"
    # Форма RomRaider: sizex - столбцы (ось r6), sizey - строки (ось r5). У одномерной
    # карты ось одна, её длина и есть sizex.
    size = ([f'sizex="{m["height"]}"', f'sizey="{m["width"]}"'] if m["dims"] == 2
            else [f'sizex="{m["width"]}"'])
    out = [comment(evidence_lines(m, axes, rom))]
    out += wrap("    ", "<table", [f'type="{dims}"', f'name="{att(o["name"])}"',
                                   f'category="{att(cat)}"',
                                   f'storagetype="{att(m["storagetype"])}"',
                                   f'storageaddress="{hexa(m["addr"])}"']
                + size + ['endian="big"'], ">")
    out.append(scaling(m["units"], m["scale_expr"], m["to_byte"], m["scale_conf"],
                       o.get("format", "0"), o.get("fine"), o.get("coarse"), 6))

    # Ось у карты одна на ребро - это ворота эмиссии, и до сюда доходит только такая.
    if m["dims"] == 2:
        out += axis_xml("X Axis", axes[m["axis_y"][0]], ovr, "sizex")
        out += axis_xml("Y Axis", axes[m["axis_x"][0]], ovr, "sizey")
    elif m["axis_x"]:
        out += axis_xml("X Axis", axes[m["axis_x"][0]], ovr, "sizex")
    elif m["steps"]:
        # implicit-axis: массива нет, ось - точки 0..(n-1) с шагом входа.
        step = m["steps"][0]
        out += static_axis_xml([i * step for i in range(m["width"])],
                               f"Raw input (step {step})")
    else:
        # compare: lookup'а нет, ячейки выбирает ветвление; подписи ветвей - оверрайд.
        out += static_axis_xml(o["static_axis"], "Selector")
    out.append("    </table>")
    return out


def emittable(m, axes):
    """Ворота раздела 9 либо причина, по которой карта дефом не выпускается."""
    if m["role"] != "table":
        return f'роль {m["role"]}'
    if not m["semantics"]:
        return "семантики нет"
    if not m["scale_expr"]:
        return "шкалы нет"
    if LEVELS.index(m["confidence"]) < LEVELS.index("candidate"):
        return f'уровень {m["confidence"]}'
    for key in ("axis_x", "axis_y"):
        if len(m[key]) > 1:
            return (f'ось выбирает ветвление: {", ".join(hexa(a) for a in m[key])} '
                    f'- вход Stage 6')
        for a in m[key]:
            if LEVELS.index(axes[a]["confidence"]) < LEVELS.index("candidate"):
                return f'ось {hexa(a)} стоит только на резерве'
            if not axes[a]["kind"]:
                return f'ось {hexa(a)} не размечена'
    if m["dims"] == 2 and not (m["axis_x"] and m["axis_y"]):
        return "у 2D-карты снята не всякая ось"
    # Ось одномерной карты задана массивом (explicit), шагом входа (implicit) либо не
    # задана вовсе: у семейства compare lookup'а нет, ячейки выбирает ветвление.
    if m["dims"] == 1 and not (m["axis_x"] or m["steps"] or m["family"] == "compare"):
        return "ось не задана ни массивом, ни шагом"
    return None


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else "JK08A"
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(DEFS, f"{rom}.xml")
    ovr_path = os.path.join(DEFS, f"{rom}.overrides.toml")
    if not os.path.exists(ovr_path):
        sys.exit(f"нет презентационного слоя {ovr_path}")
    with open(ovr_path, "rb") as f:
        ovr = tomllib.load(f)

    maps, axes = fetch(rom)
    emit, skipped = [], []
    for a, m in sorted(maps.items()):
        why = emittable(m, axes)
        if why:
            if m["semantics"] and m["role"] == "table":
                skipped.append((a, m["semantics"], why))
            continue
        o = ovr.get("table", {}).get(a)
        if o is None or not o.get("name") or not o.get("category"):
            sys.exit(f"карта {hexa(a)} ({m['semantics']}) проходит ворота эмиссии, но "
                     f"имени и категории у неё нет - объявить [table.{a}] в "
                     f"{os.path.basename(ovr_path)}")
        # У карты без оси подписи ячеек взять неоткуда, кроме оверрайда: ветвление
        # именует их, а не граф.
        if not (m["axis_x"] or m["steps"]):
            if len(o.get("static_axis", [])) != m["width"]:
                sys.exit(f"[table.{a}]: у карты оси нет, ячейки выбирает ветвление - "
                         f"нужен static_axis из {m['width']} подписей")
        elif "static_axis" in o:
            sys.exit(f"[table.{a}]: static_axis поверх оси {hexa((m['axis_x'] or ['-'])[0])} "
                     f"- ось даёт граф, оверрайду её не подменять")
        emit.append(m)
    unknown = sorted(set(ovr.get("table", {})) - {m["addr"] for m in emit})
    if unknown:
        sys.exit("оверрайд на карту, которая дефом не выпускается: "
                 + ", ".join(f"[table.{a}]" for a in unknown)
                 + " - либо адрес неверен, либо карта не проходит ворота")
    for a in sorted(ovr.get("axisview", {})):
        if a not in axes:
            sys.exit(f"оверрайд [axisview.{a}] на ось, которой в графе нет")
        if not axes[a]["kind"]:
            sys.exit(f"[axisview.{a}]: ось не размечена в {rom}.axes.csv, "
                     f"выпускать её нечем")

    switches = ovr.get("switch", [])
    if isinstance(switches, dict):
        switches = [switches]
    if not isinstance(switches, list):
        sys.exit(f"{os.path.basename(ovr_path)}: switch должен быть таблицей "
                 "или массивом таблиц")

    body = []
    for index, entry in enumerate(switches, 1):
        body += switch_xml(entry, index) + [""]
    for m in sorted(emit, key=lambda m: (ovr["table"][m["addr"]].get("order", 1 << 20),
                                         m["addr"])):
        body += table_xml(m, ovr, axes, rom) + [""]
    for a in sorted(ovr.get("axisview", {}),
                    key=lambda a: (ovr["axisview"][a].get("order", 1 << 20), a)):
        o, x = ovr["axisview"][a], axes[a]
        body += [comment([f'{hexa(a)}  ось {x["len"]} точек {x["storagetype"]}, '
                          f'{x["kind"]}' + (f' [{x["scale_conf"]}]'
                                            if x["scale_conf"] else ""),
                          x["note"] or "", f"Разбор и метод - defs/{rom}.notes.md"])]
        body += wrap("    ", "<table", ['type="2D"', f'name="{att(o["name"])}"',
                                        f'category="{att(o["category"])}"',
                                        f'storagetype="{att(x["storagetype"])}"',
                                        f'storageaddress="{hexa(a)}"',
                                        f'sizex="{x["len"]}"', 'endian="big"'], ">")
        body.append(scaling(x["units"], x["scale_expr"], x["to_byte"], x["scale_conf"],
                            o.get("format", "0"), o.get("fine"), o.get("coarse"), 6))
        body += static_axis_xml(list(range(x["len"])))
        body += ["    </table>", ""]

    romid = ovr["rom"]
    missing = [f for f in ROMID_FIELDS if f not in romid]
    if missing:
        sys.exit(f"{os.path.basename(ovr_path)}: [rom] без полей {', '.join(missing)}")
    head = [comment([f"RomRaider-деф {rom}. Файл сгенерирован tools/mapkit/emit_def.py из "
                     f"графа Memgraph (факты)", f"и defs/{rom}.overrides.toml "
                     f"(презентация). Правка этого файла следующего прогона не переживает:",
                     "править источники - defs/<rom>.findings.csv, <rom>.axes.csv, "
                     "<rom>.interp.csv, <rom>.overrides.toml.", ""]
                    + romid.get("comment", {}).get("text", "").split("\n"), indent=0),
            "<roms>", "  <rom>", "    <romid>"]
    head += [f"      <{f}>{att(romid[f])}</{f}>" for f in ROMID_FIELDS]
    head += ["    </romid>", ""]
    checksums = ovr.get("checksum", [])
    if isinstance(checksums, dict):
        checksums = [checksums]
    if not isinstance(checksums, list):
        sys.exit(f"{os.path.basename(ovr_path)}: checksum должен быть таблицей "
                 "или массивом таблиц")
    for i, c in enumerate(checksums, 1):
        unknown = sorted(set(c) - set(CHECKSUM_FIELDS) - {"comment"})
        if unknown:
            sys.exit(f"{os.path.basename(ovr_path)}: checksum #{i} содержит "
                     f"неизвестные поля {', '.join(unknown)}")
        required = (
            ("type", "path", "expectedsize",
             "l1loc", "l1stock", "l1patched",
             "l2loc", "l2stock", "l2patched")
            if "path" in c else
            ("type", "start", "end", "sumloc", "xorloc")
        )
        missing = [k for k in required if k not in c]
        if missing:
            sys.exit(f"{os.path.basename(ovr_path)}: checksum #{i} без полей "
                     f"{', '.join(missing)}")
        if "comment" in c:
            head.append(comment(c["comment"].split("\n")))
        head += wrap("    ", "<checksum",
                     [f'{k}="{att(c[k])}"' for k in CHECKSUM_FIELDS if k in c],
                     "/>") + [""]

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(head + body).rstrip()
           + "\n  </rom>\n</roms>\n")
    with open(out_path, "w") as f:
        f.write(xml)

    print(f"{os.path.relpath(out_path)}: {len(emit)} таблиц, "
          f"{len(ovr.get('axisview', {}))} осей-опор, {len(switches)} переключателей")
    lvl = {}
    for m in emit:
        lvl[m["confidence"]] = lvl.get(m["confidence"], 0) + 1
    print("  уровни: " + ", ".join(f"{k}={lvl[k]}" for k in LEVELS if k in lvl))
    cand = [m for m in emit if m["scale_conf"] and m["scale_conf"] != "code"]
    print(f"  шкала кодом не закреплена: {len(cand)} "
          f"({', '.join(hexa(m['addr']) for m in cand)})")
    print(f"  каталог: {len(maps)} карт; не выпускается {len(maps) - len(emit)}")
    for a, sem, why in skipped:
        print(f"    {hexa(a)} {sem}: {why}")
    nosem = sum(1 for m in maps.values() if not m["semantics"] and m["role"] == "table")
    print(f"    ещё {nosem} карт роли table без семантики - открытая работа ledger'а")


if __name__ == "__main__":
    main()
