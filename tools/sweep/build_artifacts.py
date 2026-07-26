#!/usr/bin/env python3
"""Артефакт компоненты графа "аксессор -> карта": шаг подготовки массового прохода.

Контракт прогона - tools/map-sweep.md, здесь его раздел 2. Единица работы - связная
компонента двудольного графа "аксессор -> карта": компоненты независимы по построению
(две не делят ни карту, ни аксессор), и все свидетельства о карте лежат внутри одной.

Артефакт - единственный вход агента прогона: доступа к Memgraph у агента нет. Отсюда
ослепление структурно, а не обещанием: что агент видит, задаёт этот скрипт. Ослепить
агента, который сам ходит в граф, нельзя - разметочный слой лежит там же, где форма, и
один запрос вернёт ответ вместе с вопросом.

Ослепление сделано БЕЛЫМ списком (MAP_FACTS/AXIS_FACTS - это RETURN запросов), а не
чёрным. Разметка и измерение лежат на одном узле, и свойство, добавленное в него позже,
по умолчанию обязано быть невидимым, а не видимым: чёрный список пропустил бы его молча.
Заявка агента - semantics/role/units/scale_expr/confidence, и вывести их он обязан сам.
Проверка ослепления идёт на каждом прогоне (verify_blind): текст артефакта сверяется с
теми самыми строками разметки, которые он не должен нести.

Значения карт берёт образ, а не граф: в узле лежит только vmin/vmax/values_hash - 256
ячеек в графе были бы содержимым образа, переписанным туда (Stage 4).

Список компонент не хранится: он выводится запросом на каждом прогоне (P5). Ключ
компоненты - младший адрес её аксессора; component_id от MAGE между прогонами не
стабилен и именем файла служить не может.

Артефакт строится на компоненту (заявка на каждую её карту), карту (`--focus-map`) или
ось (`--focus-axis`). Фокус карты сужает свидетельство до аксессоров целевой карты; фокус
оси агрегирует все карты с этой осью и все аксессоры этих карт. В обоих случаях заявка
требуется только по цели, а соседние карты и оси остаются контекстом.

Запуск: uv run --no-project --with neo4j python tools/sweep/build_artifacts.py \
          <out_dir> [--rom JK03A] [--accessor <addr>] [--min-maps N] [--max-maps N] \
          [--focus-map <addr> | --focus-maps-file <path> | \
           --focus-axis <addr> | --focus-axes-file <path>] [--export-dir <dir>]
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from neo4j import GraphDatabase

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import rom as romkit          # noqa: E402 - пакет соседний, не установленный

BOLT = "bolt://localhost:7687"
EXPORT = os.path.expanduser("~/tools/ghidra-projects/export-{rom}")

# --- Граница ослепления -------------------------------------------------------------
# Ниже - RETURN запросов о картах и осях компоненты. Он и есть белый список: разметка не
# покидает базу, а не отфильтровывается после выборки. Свойства, которых здесь нет
# (semantics, role, units, scale_expr, to_byte, scale_conf, confidence, evidence, note у
# :Map; kind, units, scale_expr, to_byte, confidence, note у :Axis), - заявка агента.
MAP_FACTS = """
MATCH (m:Map {rom:$rom}) WHERE m.addr IN $addrs
OPTIONAL MATCH (m)-[:VIA]->(w:Interp {rom:$rom})
OPTIONAL MATCH (w)-[:KERNEL]->(k:Interp {rom:$rom})
OPTIONAL MATCH (m)-[:AXIS_X]->(ax:Axis {rom:$rom})
OPTIONAL MATCH (m)-[:AXIS_Y]->(ay:Axis {rom:$rom})
RETURN m.addr AS addr, m.family AS family, m.dims AS dims, m.width AS width,
       m.height AS height, m.storagetype AS storagetype, m.vmin AS vmin, m.vmax AS vmax,
       m.values_hash AS values_hash,
       collect(DISTINCT w.addr) AS via, collect(DISTINCT k.addr) AS kernel,
       collect(DISTINCT ax.addr) AS axis_x, collect(DISTINCT ay.addr) AS axis_y
ORDER BY addr
"""

AXIS_FACTS = """
MATCH (a:Axis {rom:$rom}) WHERE a.addr IN $addrs
RETURN a.addr AS addr, a.len AS len, a.storagetype AS storagetype,
       a.values AS values, a.monotonic AS monotonic
ORDER BY addr
"""

# Разметка компоненты - её же ответ. Достаётся отдельным запросом и в артефакт не идёт:
# ею verify_blind проверяет, что артефакт её не несёт.
MAP_ANSWERS = """
MATCH (m:Map {rom:$rom}) WHERE m.addr IN $addrs
RETURN m.addr AS addr, m.semantics AS semantics, m.note AS note, m.role AS role,
       m.units AS units, m.scale_expr AS scale_expr, m.to_byte AS to_byte,
       m.confidence AS confidence, m.evidence AS evidence,
       m.scale_evidence AS scale_evidence
"""

AXIS_ANSWERS = """
MATCH (a:Axis {rom:$rom}) WHERE a.addr IN $addrs
RETURN a.addr AS addr, a.kind AS kind, a.units AS units, a.scale_expr AS scale_expr,
       a.to_byte AS to_byte, a.note AS note, a.confidence AS confidence,
       a.scale_evidence AS scale_evidence
"""

# Разметка функций - тоже ответ: в semantics слоя кода копится знание проекта со ссылками
# на конкретные карты ("домножение такой-то карты на такую-то константу"). В артефакт из
# слоя идёт только contract, от карт не зависящий; проверяется это здесь, а не доверием к
# RETURN запроса CONTRACTS. Берётся весь ПЗУ, а не показанные функции: утечь может и
# разметка соседа, попавшая в текст через чужое поле.
FUNC_ANSWERS = """
MATCH (f:Func {rom:$rom})
WHERE f.semantics <> '' OR f.note <> '' OR f.evidence <> '' OR f.contract_evidence <> ''
RETURN f.addr AS addr, f.semantics AS semantics, f.note AS note,
       f.evidence AS evidence, f.contract_evidence AS contract_evidence
"""

# --- Перечисление компонент ---------------------------------------------------------
COMPONENTS = """
MATCH p=(:Func {rom:$rom})-[:ACCESSES]->(:Map {rom:$rom})
WITH project(p) AS g
CALL weakly_connected_components.get(g) YIELD node, component_id
WITH component_id, collect(node) AS nodes
RETURN component_id,
       [n IN nodes WHERE 'Map'  IN labels(n) | n.addr] AS maps,
       [n IN nodes WHERE 'Func' IN labels(n) | n.addr] AS accessors
"""

# Фокус оси не выбирает одну произвольную карту-представителя: общая ось может связывать
# несколько карт и компонент. Контекстом служат ВСЕ карты с прямым ребром к оси и ВСЕ
# аксессоры этих карт.
# OPTIONAL MATCH сохраняет ось и карту без аксессора, чтобы неполнота графа не скрывала цель.
AXIS_CONTEXTS = """
MATCH (a:Axis {rom:$rom}) WHERE a.addr IN $addrs
OPTIONAL MATCH (m:Map {rom:$rom})-[:AXIS_X|AXIS_Y]->(a)
OPTIONAL MATCH (f:Func {rom:$rom})-[:ACCESSES]->(m)
RETURN a.addr AS axis, m.addr AS map, f.addr AS accessor
ORDER BY axis, map, accessor
"""

# Фокус: аксессоры, читающие одну заданную карту. Компонента задаёт СОСТАВ карт, но
# свидетельство о карте лежит в её собственной окрестности - аксессорах, которые её читают,
# и в том, что делают с их выходом. Аксессор компоненты, целевой карты не касающийся,
# отстоит от неё на два и более шага и в трейс не входит; в артефакт он вносит объём.
# Цена объёма не линейна: списание идёт как "ходов x контекст", а большой артефакт растит
# оба множителя сразу (он читается кусками, и контекст пухнет от хода к ходу).
FOCUS_ACC = """
MATCH (f:Func {rom:$rom})-[:ACCESSES]->(m:Map {rom:$rom, addr:$map})
RETURN collect(DISTINCT f.addr) AS accessors
"""

SITES = """
MATCH (f:Func {rom:$rom})-[x:ACCESSES]->(m:Map {rom:$rom})
WHERE f.addr IN $addrs
RETURN f.addr AS accessor, f.name AS name, f.size AS size, m.addr AS tbl,
       x.callsite AS callsite, x.r4 AS r4, x.r5 AS r5, x.r6 AS r6,
       x.kind AS kind, x.kind5 AS kind5, x.kind6 AS kind6, x.verdict AS verdict
ORDER BY accessor, callsite, tbl
"""

CALLERS = """
MATCH (c:Func {rom:$rom})-[:CALLS]->(f:Func {rom:$rom})
WHERE f.addr IN $addrs
RETURN f.addr AS accessor, c.addr AS caller, c.name AS name, c.size AS size
ORDER BY accessor, caller
"""

USES = """
MATCH (f:Func {rom:$rom})-[u:USES]->(r:Reg {rom:$rom})
WHERE f.addr IN $addrs
RETURN f.addr AS accessor, r.addr AS reg, r.region AS region, r.name AS name,
       collect(DISTINCT u.kind) AS kinds
ORDER BY accessor, region, reg
"""

# Машинерия интерполяции: карта идёт VIA на обёртку, обёртка KERNEL на ядро. Обёртка
# уходит в ядро через jmp, а не jsr, поэтому ребра CALLS туда нет и size ядра пуст -
# Ghidra его функцией не размечает (лечит RecoverFuncs.java, раздел 7
# map-flag-pipeline.md). Пустой size - факт артефакта: трейс через это ядро не ведётся.
# Здесь же лежит finisher: он вызывается ядром и держит насыщение и элемент карты.
KERNELS = """
MATCH (m:Map {rom:$rom})-[:VIA]->(w:Interp {rom:$rom})
WHERE m.addr IN $maps
OPTIONAL MATCH (w)-[:KERNEL]->(k:Interp {rom:$rom})
WITH collect(DISTINCT {a:w.addr, r:w.role}) + collect(DISTINCT {a:k.addr, r:k.role}) AS xs
UNWIND xs AS x
WITH DISTINCT x WHERE x.a IS NOT NULL
OPTIONAL MATCH (f:Func {rom:$rom, addr:x.a})
OPTIONAL MATCH (f)-[:CALLS]->(c:Func {rom:$rom})
RETURN x.a AS addr, x.r AS role, f.size AS size,
       collect(DISTINCT {addr:c.addr, size:c.size}) AS callees
ORDER BY addr
"""

# Контракты вызываемых функций из слоя понимания кода. RETURN здесь тоже белый список, и
# `semantics` в него не входит намеренно: в semantics копится знание проекта со ссылками на
# конкретные карты ("домножение 0x145ca на константу 0x1495a = 50000"), то есть готовый
# ответ. Контракт - операция, соглашение о регистрах, побочные эффекты - от карт не зависит
# и остаётся свидетельством, а не подсказкой.
CONTRACTS = """
MATCH (f:Func {rom:$rom}) WHERE f.addr IN $addrs AND f.contract <> ''
RETURN f.addr AS addr, f.role AS role, f.size AS size, f.contract AS contract,
       f.contract_conf AS contract_conf
ORDER BY addr
"""

# Кого показанный код вызывает. Считать по тексту псевдокода нельзя: библиотека
# вызывается через регистр, загруженный из литерального пула, и Ghidra печатает такой вызов
# как `(*pcVar26)()` - адреса в тексте нет вовсе. Ребро CALLS его знает, потому что цель
# разрешена на этапе анализа, а не при печати.
CALLED = """
MATCH (f:Func {rom:$rom})-[:CALLS]->(g:Func {rom:$rom})
WHERE f.addr IN $addrs AND g.contract <> ''
RETURN DISTINCT g.addr AS addr
"""

# Потребители выхода: функции, читающие RAM, которую пишет аксессор компоненты. Смысл
# карты задаёт то, что происходит с её выходом дальше, а выход - это запись в RAM.
# Отсечка по числу читателей - мера специфичности: регистр с единицами читателей частный
# для компоненты, а читаемый многими - разделяемая шина, потребитель которой о карте не
# говорит. Порог 8 держит умеренно-разделяемые выходы (2-8 потребителей - основная масса
# случаев, где трейс доходит до смысла) и отсекает горячие стоки/шины (9+ читателей): их
# полный набор потребителей дорог и даёт агенту стог, а не иглу. Цена в ТЕКСТЕ, не в
# машинном коде: декомпилят потребителя в ~5-7 раз длиннее его size. У самого широкого
# аксессора ROM'а (000b29b8, 65 write-регистров) артефакт при 8 уже ~800 КБ, при 32 - многие
# мегабайты; выше порог растит цену прогона, не разметку.
#
# Отсечка по разделяемости - не единственный источник объёма и не главный. Широкий аксессор
# держит сотню приватных регистров (по одному читателю на каждый), и они проходят любой
# порог: у карты 0001218e из 305 потребителей 56 приходят через 119 регистров с ровно одним
# читателем. Поэтому декомпиляция потребителей идёт под своим бюджетом (--max-consumer-decomp),
# а таблица потребителей печатается ПОЛНОЙ: состав выхода агент видит весь, код получает
# наиболее специфичная часть. Порядок отбора - min(readers) по связывающим регистрам, затем
# размер: приватный регистр ближе к выходу карты, чем умеренно-разделяемый.
CONSUMERS = """
MATCH (a:Func {rom:$rom})-[:USES {kind:'W'}]->(g:Reg {rom:$rom})
WHERE a.addr IN $addrs
OPTIONAL MATCH (c:Func {rom:$rom})-[:USES {kind:'R'}]->(g) WHERE NOT c.addr IN $addrs
WITH g, count(DISTINCT c) AS readers
WHERE readers >= 1 AND readers <= $maxr
MATCH (c2:Func {rom:$rom})-[:USES {kind:'R'}]->(g) WHERE NOT c2.addr IN $addrs
RETURN c2.addr AS consumer, c2.size AS size, collect(DISTINCT g.addr) AS regs,
       min(readers) AS spec
ORDER BY spec, size, consumer
"""

# Потребители привязанного выхода. Отличие от CONSUMERS - в источнике набора регистров:
# там он выводится из всех записей аксессора и потому несёт чужие величины, здесь задан
# привязкой и несёт только величину целевой карты. Отсечка по разделяемости тут не нужна:
# набор уже специфичен, а разделяемость привязанного регистра - факт о карте, и скрывать
# его отсечкой значит терять свидетельство.
CONSUMERS_OF = """
UNWIND $regs AS reg
MATCH (c:Func {rom:$rom})-[:USES {kind:'R'}]->(g:Reg {rom:$rom, addr:reg})
WHERE NOT c.addr IN $addrs
RETURN c.addr AS consumer, c.size AS size, collect(DISTINCT g.addr) AS regs, 1 AS spec
ORDER BY size, consumer
"""

# Разбор пустого раздела потребителей. Пусто выходит по трём разным причинам, и они
# значат для агента разное: аксессор вообще ничего не пишет в RAM (трейс кончается в
# аксессоре), написанное никто снаружи не читает (выход мёртв либо читается тем же
# аксессором), написанное читают все подряд (регистр - разделяемая шина, и отсечка по
# специфичности его сняла). Молча опущенный раздел все три случая делает неразличимыми.
WRITE_REGS = """
MATCH (a:Func {rom:$rom})-[:USES {kind:'W'}]->(g:Reg {rom:$rom})
WHERE a.addr IN $addrs
OPTIONAL MATCH (c:Func {rom:$rom})-[:USES {kind:'R'}]->(g) WHERE NOT c.addr IN $addrs
RETURN g.addr AS reg, g.name AS name, count(DISTINCT c) AS readers
ORDER BY readers DESC, reg
"""

# Регистры декомпилированных функций - сверщик резолва пула. Декомпилятор печатает литерал
# именем `DAT_<адрес>`, и обращение `*(byte *)(DAT_0008625c + DAT_0008608e)` адреса не
# называет, хотя граф его знает. Резолв по образу даёт адрес-кандидат, а этот запрос -
# множество, на котором кандидат проверяется: совпадение и есть подтверждение трактовки.
FUNC_REGS = """
MATCH (f:Func {rom:$rom})-[u:USES]->(g:Reg {rom:$rom})
WHERE f.addr IN $addrs
RETURN f.addr AS func, collect(DISTINCT {addr:g.addr, kind:u.kind}) AS regs
"""

# Все известные адреса RAM и периферии ROM'а - второй, более слабый сверщик резолва.
# Обращение по адресу, сложенному в регистре, Ghidra не резолвит, и ребра USES у него нет,
# хотя адрес существует и узел о нём есть. Отсюда три состояния привязки, а не два.
ALL_REGS = """
MATCH (g:Reg {rom:$rom}) RETURN collect(g.addr) AS addrs
"""

# Каталог-эталон. Ключ - геометрия: из трёх ключей матча (dims, scale-family, семантика
# осей) на ослеплённой стороне есть только он. Семантика осей пришла бы из разметки,
# которой в артефакте нет; scale-family - оттуда же. Матч слаб, и артефакт говорит это
# прямо: 16 записей каталога имеют форму 16x16 (раздел 5 спеки - подсказка candidate, не
# идентификация).
A2L_BY_SHAPE = """
MATCH (e:A2LEntry {family:'HR'}) WHERE e.dims = $dims AND e.shape = $shape
RETURN e.name AS name, e.kind AS kind, e.unit AS unit, e.scale_expr AS scale_expr,
       e.storagetype AS storagetype, e.axis_x_sem AS axis_x_sem,
       e.axis_y_sem AS axis_y_sem, e.category AS category, e.concept AS concept
ORDER BY name
"""

# Вендорский словарь матчится не сам по себе, а через A2L по concept: у ProECU нет ни одного
# из трёх ключей матча - скриншоты дерева несут только имена, - а матч по имени вслепую есть
# ровно тот отказ, против которого стоит P6. Отсюда цепочка: геометрия карты -> запись A2L ->
# её concept -> записи вендоров с тем же concept.
#
# origin=factory обязателен: 128 записей из 371 заводскими не являются (патчи RaceROM и ARC -
# чужой код, которого в стоке нет). Матч стоковой карты к patch-записи был бы не слабой
# подсказкой, а неверной.
VENDOR_BY_CONCEPT = """
MATCH (e:VendorEntry {family:'HR', origin:'factory'}) WHERE e.concept IN $concepts
RETURN e.vendor AS vendor, e.name AS name, e.group AS grp, e.axis_x AS axis_x,
       e.axis_y AS axis_y, e.output AS output, e.concept AS concept
ORDER BY concept, vendor, name
"""

# Якорь по содержимому: документированный дефолт ищется прямо в значениях компоненты.
# applies_to печатается: EcuTek документирует VQ37VHR, а JK03A - VQ25HR без VVEL, и
# граница применимости - предмет решения агента, а не фильтра здесь.
VENDOR_CONSTS = """
MATCH (f:VendorFact {family:'HR', kind:'const'})
RETURN f.vendor AS vendor, f.subject AS subject, f.value AS value, f.units AS units,
       f.statement AS statement, f.applies_to AS applies_to, f.concept AS concept
ORDER BY subject
"""


def shape(width, height):
    """Форма таблицы словарём журнала разметки, общим с каталогом A2L."""
    if width is None:
        return ""
    return f"{width}x{height}" if height else f"1D-{width}"


def group(rows, key):
    out = {}
    for r in rows:
        out.setdefault(r[key], []).append(r)
    return out


def components(session, rom):
    """Компоненты графа, ключ - младший адрес аксессора.

    Список нигде не хранится: граф меняется разметкой, и записанный список стал бы
    вторым источником правды (P5, раздел 1 контракта).
    """
    out = []
    for r in session.run(COMPONENTS, rom=rom):
        if not r["accessors"]:
            continue
        out.append({"key": min(r["accessors"]),
                    "maps": sorted(r["maps"]),
                    "accessors": sorted(r["accessors"])})
    out.sort(key=lambda c: (-len(c["maps"]), c["key"]))
    return out


def read_values(image, m):
    """Значения карты - из образа: в графе их нет, там vmin/vmax/values_hash."""
    try:
        return image.table(m["addr"], m["width"], m["height"], m["storagetype"])
    except ValueError as e:
        return [[f"ЧТЕНИЕ НЕ УДАЛОСЬ: {e}"]]


def grid(rows):
    """Карта построчно: строка - точка оси r5 (:AXIS_X), столбец - точка оси r6."""
    if not rows or isinstance(rows[0][0], str):
        return "    " + str(rows[0][0] if rows else "")
    w = max(len(str(v)) for row in rows for v in row)
    return "\n".join("    " + " ".join(str(v).rjust(w) for v in row) for row in rows)


def dumped(export_dir, addr, kind):
    """Выход прогона подготовки. Отсутствие файла - факт артефакта, а не пропуск.

    Листинг берётся на адрес сайта, а не функции: операнды резолвятся там, и окно
    DumpListing (+-24 инструкции) вокруг входа функции до сайта не достаёт.
    """
    path = os.path.join(export_dir, f"{kind}_{addr}.{'c' if kind == 'decomp' else 'txt'}")
    if not os.path.exists(path):
        return None, path
    with open(path) as f:
        return f.read().rstrip(), path


def render_site_listing(A, export_dir, site):
    """Листинг есть только у карты, пришедшей из переписи с callsite."""
    callsite = site["callsite"]
    A(f"##### Сайт `{callsite}` -> карта `{site['tbl']}`")
    A("")
    if not callsite:
        A("Сайт вызова отсутствует: карта добавлена ручным слоем вне переписи "
          "резолвера, поэтому листинга сайта для неё не существует.")
    else:
        text, path = dumped(export_dir, callsite, "listing")
        if text is None:
            A(f"Нет файла `{os.path.basename(path)}`: прогон подготовки этот сайт не "
              f"покрыл.")
        else:
            A("```")
            A(text)
            A("```")
    A("")


# Вызов, у которого адрес виден прямо в тексте: `FUN_00021bbc` псевдокода и `jsr`-цель
# листинга (`-> 00021bbc`). Основной канал - ребро :CALLS (запрос CALLED), потому что вызов
# через регистр адреса в тексте не оставляет; здесь добирается то, чего нет в графе.
CALLED_ADDR = re.compile(r"(?:\bFUN_|-> )(00[0-9a-f]{6})\b")
POOL_SYM = re.compile(r"\b((?:PTR_)?(?:DAT|FUN)_00([0-9a-f]{6}))\b")
POOL_ALIAS = re.compile(
    r"(?<![!<>=])\b(\w+)\s*=(?!=)\s*((?:PTR_)?(?:DAT|FUN)_00[0-9a-f]{6})\s*$"
)
POOL_EXPR = re.compile(r"\(\s*(\w+)\s*\+\s*(\w+|0x[0-9a-fA-F]+)\s*\)")
ASSIGN = re.compile(r"(?<![!<>=])\b(\w+)\s*=(?!=)\s*(.+)$")
NUMERIC = re.compile(r"0x[0-9a-fA-F]+[uUlL]*|\d+[uUlL]*")


def literal(image, addr):
    """Трактовки литерала пула по адресу.

    Ширина из псевдокода не видна: `mov.l @(disp,pc)` кладёт 32 бита с выравниванием 4,
    `mov.w @(disp,pc)` - 16 со знаковым расширением. Обе и возвращаются: выбор между ними
    - предмет проверки, а не догадки сборщика.
    """
    d, out = image.data, {}
    if addr % 4 == 0 and addr + 4 <= len(d):
        out["mov.l"] = int.from_bytes(d[addr:addr + 4], "big")
    if addr % 2 == 0 and addr + 2 <= len(d):
        v = int.from_bytes(d[addr:addr + 2], "big")
        out["mov.w"] = v | 0xFFFF0000 if v & 0x8000 else v
    return out


def stable_addrs(values):
    """Канонический порядок множества адресов."""
    return sorted(set(values))


def stable_map_facts(rows):
    """Канонический порядок карт и их множественных связей."""
    out = []
    for row in rows:
        fact = dict(row)
        for field in ("via", "kernel", "axis_x", "axis_y"):
            fact[field] = stable_addrs(fact.get(field) or [])
        out.append(fact)
    return sorted(out, key=lambda row: row["addr"])


def axis_contexts(session, rom, addrs):
    """Полный детерминированный контекст каждой целевой оси.

    Карты выбираются прямыми рёбрами AXIS_X/AXIS_Y, аксессоры - прямыми ACCESSES к
    выбранным картам. Множества агрегируются по оси, поэтому общая ось не сводится к
    контексту одной произвольно выбранной карты.
    """
    wanted = stable_addrs(addrs)
    grouped = {}
    for row in session.run(AXIS_CONTEXTS, rom=rom, addrs=wanted):
        axis = row["axis"]
        context = grouped.setdefault(axis, {"maps": set(), "accessors": set()})
        if row["map"]:
            context["maps"].add(row["map"])
        if row["accessor"]:
            context["accessors"].add(row["accessor"])
    return {
        axis: {
            "key": axis,
            "maps": stable_addrs(context["maps"]),
            "accessors": stable_addrs(context["accessors"]),
        }
        for axis, context in sorted(grouped.items())
    }


def axis_focus_jobs(session, rom, addrs):
    """Задания axis-<addr>.md с полным контекстом либо точная ошибка состава."""
    wanted = stable_addrs(addrs)
    contexts = axis_contexts(session, rom, wanted)
    missing = sorted(set(wanted) - set(contexts))
    if missing:
        raise SystemExit(f"осей нет в графе: {', '.join(missing)}")
    unlinked = [axis for axis in wanted if not contexts[axis]["maps"]]
    if unlinked:
        raise SystemExit(f"оси не связаны с картами: {', '.join(unlinked)}")
    return [(contexts[axis], None, axis, f"axis-{axis}.md") for axis in wanted]


def kinds_by_addr(rows):
    """Свести все виды обращений к адресу без зависимости от порядка рёбер."""
    kinds = {}
    for row in rows:
        kinds.setdefault(int(row["addr"], 16), set()).add(row["kind"])
    return {addr: "".join(sorted(values)) for addr, values in kinds.items()}


def stable_sites(rows):
    """Канонический порядок обращений при совпадающих accessor и callsite."""
    return sorted(rows, key=lambda row: (row["accessor"], row["callsite"], row["tbl"]))


def stable_callees(rows):
    """Канонический порядок множества вызываемых функций."""
    return sorted(rows, key=lambda row: (row.get("addr") or "", row.get("size") or -1))


def alias_snapshots(stmts, syms):
    """Значение локального alias перед каждым оператором псевдокода.

    Ghidra повторно использует одно локальное имя для разных баз RAM. Глобальный словарь
    alias в таком случае приписывает ранней записи последнее значение имени и связывает
    результат карты с чужим регистром. Здесь действует ближайшее предшествующее
    присваивание; любое присваивание не из пула снимает прежний alias.
    """
    aliases, snapshots = {}, []
    for stmt in stmts:
        snapshots.append(dict(aliases))
        assigned = ASSIGN.search(stmt)
        if not assigned:
            continue
        direct = POOL_ALIAS.search(stmt)
        name = assigned.group(1)
        if direct and direct.group(1) == name and direct.group(2) in syms:
            aliases[name] = direct.group(2)
        else:
            aliases.pop(name, None)
    return snapshots


def pool(image, text, regs):
    """Литералы пула псевдокода и позиционные привязки выражений к регистрам.

    Декомпилятор печатает литерал именем `DAT_<адрес>`, значения не подставляя: в
    обращении `*(byte *)(DAT_0008625c + DAT_0008608e)` символы и база, и смещение, так что
    регистр из псевдокода не читается - хотя таблица USES того же артефакта его знает.
    Без этого трейс потребителя обрывается на имени функции, не доходя до того, что она с
    величиной делает, и заявка о карте не может подняться выше `candidate`.

    Трактовку ширины выбирает не сборщик, а арифметика под проверкой графа: адрес
    `база + смещение` сверяется сперва с регистрами этой функции, затем со всеми
    известными адресами ROM'а. Состояния разные по силе и не сводятся к "верно/неверно":
    обращение по адресу, сложенному в регистре, Ghidra не резолвит, ребра USES у него нет,
    и подтвердить его первым сверщиком нельзя, хотя адрес настоящий.
    """
    syms = {}
    for full, hexa in POOL_SYM.findall(text):
        addr = int(hexa, 16)
        if addr < len(image.data):
            syms[full] = (addr, literal(image, addr))
    known = kinds_by_addr(regs)
    stmts = split_stmts(text)
    aliases = alias_snapshots(stmts, syms)

    def base(term, current=None):
        sym = (current or {}).get(term, term)
        return syms.get(sym, (None, {}))[1].get("mov.l"), sym

    def disp(term, current=None):
        if NUMERIC.fullmatch(term):
            # декомпилятор эмитит C-суффиксы (0x1c00U, ...L) и печатает малые смещения
            # десятичными (`iVar3 + 100`); одиночный странный литерал не должен ронять
            # сборку - вызывающий пропускает None
            try:
                return int(term.rstrip("uUlL"), 0), term
            except ValueError:
                return None, term
        sym = (current or {}).get(term, term)
        v = syms.get(sym, (None, {}))[1]
        return v.get("mov.w"), sym

    binds, raw = {}, {}
    for index, (stmt, current) in enumerate(zip(stmts, aliases)):
        for match in POOL_EXPR.finditer(stmt):
            lhs, rhs = match.groups()
            b, bsym = base(lhs, current)
            o, osym = disp(rhs, current)
            if b is None or o is None or not 0xFFFF0000 <= b <= 0xFFFFFFFF:
                continue
            target = (b + o) & 0xFFFFFFFF
            binds[(bsym, osym)] = (target, known.get(target))
            # Один и тот же текст выражения может означать разные адреса после
            # переприсваивания локальной базы, поэтому индекс оператора входит в ключ.
            key = re.sub(r"\s+", " ", match.group(0))
            raw[(index, key)] = target
    return syms, binds, raw, base, aliases, stmts


CALL = re.compile(r"(?:\(\*\(code \*\)\s*(?:\w+)\s*\)|\bFUN_[0-9a-f]{8})\s*\(")
VAR = re.compile(r"\b([a-zA-Z_]\w*)\b")
# `*(тип *)(A + B) = rhs` либо `*(тип *)A = rhs`; звёздочка обязательна - без неё
# присваивание идёт в локальную переменную, а не в память
STORE = re.compile(r"\*\s*\(\s*(\w+)\s*\*\s*\)\s*(\([^;]*?\)|\w+)\s*=\s*([^;=][^;]*)$")
# ширина записи задаёт, по каким адресам величину читают: 16-битная запись занимает два
# байта, и читатель старшей половины обращается к A, младшей - к A+1
STORE_WIDTH = {"char": 1, "uchar": 1, "byte": 1, "undefined1": 1,
               "short": 2, "ushort": 2, "undefined2": 2,
               "int": 4, "uint": 4, "undefined4": 4, "float": 4}
# Граница ставится по числу переприсваиваний, а не по расстоянию в тексте: между вызовом
# и записью стоят несвязанные операторы, и величина к моменту записи - та же переменная,
# нетронутая. Расползается пометка с глубиной, не с расстоянием.
#
# На JK03A граница не работает: 2, 3, 4 и 6 дают один и тот же результат - 254 привязки на
# 586 рёбер. Величина этого ПЗУ либо доходит до памяти за пару присваиваний, либо не
# доходит вовсе, и 135 обрывов трейса - свойство кода, а не следствие отсечки. Параметр
# остаётся защитой от кода другой формы, а не настройкой под ответ.
TAINT_DEPTH = 2


def attribute(image, text, regs, bases):
    """Регистры RAM, принимающие величину карты, по сайтам вызова обёртки.

    Аксессор широкий: у самого широкого в ПЗУ 274 записываемых регистра, и раздел
    потребителей, собранный по всем сразу, величину карты растворяет. Граф связи не даёт -
    ребро ACCESSES знает сайт и базу, ребро USES знает записанные регистры, общего между
    ними нет. Псевдокод даёт: обёртка вызывается с базой карты первым аргументом, её
    результат связывается именем, и запись этого имени в память видна текстом.

    Обрыв трейса - факт, а не пробел: величина, которая до памяти не доходит, либо
    возвращается вызывающему, либо потребляется на месте, и регистра выхода у карты нет.
    """
    _syms, _binds, raw, resolve, aliases, stmts = pool(image, text, regs)
    known = {int(r["addr"], 16) for r in regs}
    out = []
    for i, st in enumerate(stmts):
        m = CALL.search(st)
        if not m:
            continue
        args = call_args(st, st.index("(", m.end() - 1))
        if not args:
            continue
        target, _sym = resolve(args[0], aliases[i])
        if target is None or f"{target:08x}" not in bases:
            continue
        rec = {"base": f"{target:08x}", "sink": None, "kind": None, "width": 0,
               "stmt": st}
        name = re.fullmatch(r"\w+", st[:m.start()].strip().rstrip("=").strip())
        if not name:
            # результат не связывается именем: либо возвращается наружу, либо тут же
            # потребляется выражением, в которое вложен вызов
            rec["kind"] = "return" if st.startswith("return") else "inline"
            out.append(rec)
            continue
        rec.update(trace_sink(stmts, i, name.group(0), raw, resolve, aliases, known))
        out.append(rec)
    return out


def trace_sink(stmts, call, name, raw, resolve, aliases, known):
    """Первая запись в память, достижимая от результата вызова.

    Величина от вызова до записи проходит через промежуточные имена, поэтому трейс идёт
    вперёд по присваиваниям, а не по одному оператору.
    """
    live = {name: 0}
    for j in range(call + 1, len(stmts)):
        st = stmts[j]
        used = set(VAR.findall(st)) & set(live)
        if not used:
            continue
        sm = STORE.match(st) or STORE.search(st)
        if sm and set(VAR.findall(sm.group(3))) & set(live):
            key = re.sub(r"\s+", " ", sm.group(2))
            addr = raw.get((j, key))
            if addr is None and re.fullmatch(r"\w+", key):
                # запись без смещения: база сама и есть адрес регистра
                v, _sym = resolve(key, aliases[j])
                addr = v if v is not None and 0xFFFF0000 <= v <= 0xFFFFFFFF else None
            if addr is None:
                return {"sink": key, "kind": "unresolved", "width": 0}
            return {"sink": f"{addr:08x}",
                    "kind": "reg" if addr in known else "ram",
                    "width": STORE_WIDTH.get(sm.group(1), 1)}
        asg = re.fullmatch(r"(\w+) = (.*)", st)
        if asg:
            src = set(VAR.findall(asg.group(2))) & set(live)
            if src:
                d = min(live[v] for v in src) + 1
                if d <= TAINT_DEPTH:
                    live[asg.group(1)] = min(live.get(asg.group(1), d), d)
            elif asg.group(1) in live:
                # имя переприсвоено чужой величиной - пометку с него снять, иначе она
                # переезжает на постороннее значение и запись найдётся не та
                del live[asg.group(1)]
    return {"sink": None, "kind": "lost", "width": 0}


def split_stmts(text):
    """Тело функции, разбитое на операторы. Длинные Ghidra переносит - склеиваются."""
    body = text[text.index("{", text.index(")")) + 1:]
    out, cur = [], []
    for ch in body:
        if ch in "{};":
            if "".join(cur).strip():
                out.append("".join(cur).strip())
            cur = []
            continue
        cur.append(" " if ch == "\n" else ch)
    return [re.sub(r"\s+", " ", s) for s in out]


def call_args(text, open_paren):
    """Аргументы вызова: срез до парной скобки, разрезанный по запятым верхнего уровня."""
    depth, start, out = 0, open_paren + 1, []
    for i in range(open_paren, len(text)):
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                out.append(text[start:i].strip())
                return [a for a in out if a]
        elif c == "," and depth == 1:
            out.append(text[start:i].strip())
            start = i + 1
    return []


ATTRIB_MISS = {
    "return": "результат вызова не связывается именем - возвращается наружу. Регистра "
              "выхода у карты в этом аксессоре нет, величину получает вызывающий.",
    "inline": "результат вызова не связывается именем - потребляется выражением, в "
              "которое вложен вызов. Что с ним происходит, читается по самому оператору.",
    "unresolved": "запись найдена, но её адрес сложен в регистре, и арифметика литералов "
                  "пула его не берёт. Адрес настоящий, привязка не выведена.",
    "lost": "записи в память в пределах прослеживания не встретилось. Величина остаётся "
            "в регистрах процессора: её либо сравнивают на месте, либо передают дальше "
            "вызовом.",
}


def render_library(A, data, export_dir):
    """Контракты вызываемых функций плюс их листинг целиком.

    Листинг, а не псевдокод: у этих функций тело - развёрнутый цикл, и декомпилятор даёт
    31 КБ на 282 байта кода. Ассемблер тех же 282 байт читается прямо и стоит 4 КБ.
    """
    if not data["library"]:
        return
    A("## Вызываемые функции с разобранным контрактом")
    A("")
    A("Функции, вызываемые из показанного выше кода и разобранные отдельно. Аргументы они "
      "принимают РЕГИСТРАМИ, а не по ABI, поэтому Ghidra соглашения не восстанавливает: в "
      "псевдокоде их вызовы стоят без аргументов, а входы видны как необъявленные `in_r0`, "
      "`in_r1`. Величина карты уходит в такую функцию именно так, и без контракта трейс на "
      "ней обрывается.")
    A("")
    A("Контракт - операция, регистры аргументов и результата, побочные эффекты - о карте "
      "не говорит ничего: это свойство функции, общей для всего ПЗУ. Что через неё "
      "проходит величина ИМЕННО этой карты, остаётся предметом трейса.")
    A("")
    A("| Адрес | Роль | Размер | Уровень | Контракт |")
    A("|---|---|---|---|---|")
    for f in data["library"]:
        size = f["size"] if f["size"] is not None else "-"
        A(f"| `{f['addr']}` | {f['role'] or '-'} | {size} | {f['contract_conf']} | "
          f"{f['contract']} |")
    A("")
    for f in data["library"]:
        text, path = dumped(export_dir, f["addr"], "funclisting")
        A(f"### Листинг `{f['addr']}`")
        A("")
        if text is None:
            A(f"Нет файла `{os.path.basename(path)}`: прогон подготовки на эту функцию "
              f"не сделан.")
        else:
            A("```")
            A(text)
            A("```")
        A("")


def render_attrib(A, data):
    """Раздел привязки выхода целевой карты."""
    A("## Привязка выхода")
    A("")
    A("Регистр RAM, в который уходит величина именно этой карты. Аксессор пишет много "
      "регистров сразу, и потребители всего набора о карте не говорят: там её величина "
      "растворена среди чужих. Привязка снимается с псевдокода - обёртка вызывается с "
      "базой карты первым аргументом, а её результат виден по имени до записи в память.")
    A("")
    if not data["attrib"]:
        A("Сайтов вызова обёртки с базой этой карты в псевдокоде аксессоров не нашлось. "
          "Обычная причина - база выбирается ветвлением либо считается, и первым "
          "аргументом стоит не литерал. Набор потребителей ниже выведен из всех записей "
          "аксессора и специфичным для карты не является.")
        A("")
        return
    A("| Аксессор | Приёмник | Ширина | Состояние |")
    A("|---|---|---|---|")
    for r in data["attrib"]:
        if r["kind"] in ("reg", "ram"):
            state = ("подтверждён ребром графа" if r["kind"] == "reg"
                     else "адрес разобран, ребра USES под ним нет")
            A(f"| `{r['acc']}` | `{r['sink']}` | {r['width']} | {state} |")
        else:
            A(f"| `{r['acc']}` | нет | – | {ATTRIB_MISS[r['kind']]} |")
    A("")
    # Оператор вызова - самое короткое свидетельство из возможных: там стоит и база карты,
    # и то, во что её величина уходит. Без приёмника он единственное, что о выходе есть.
    miss = [r for r in data["attrib"] if r["kind"] not in ("reg", "ram")]
    if miss:
        A("Оператор вызова у сайтов без приёмника:")
        A("")
        A("```c")
        for r in miss:
            A(f"// {r['acc']}")
            A(r["stmt"][:400] + ";")
        A("```")
        A("")
    A(f"Величина прослеживается через {TAINT_DEPTH} переприсваивания, расстояние в тексте "
      "не ограничено: между вызовом и записью стоят несвязанные операторы, а расползается "
      "пометка с глубиной, не с расстоянием. Отсутствие приёмника - факт о карте, а не "
      "пробел артефакта: величина, которая до памяти не доходит, потребляется на месте.")
    A("")


def bind_state(target, kind, all_regs):
    """Сила привязки: ребро графа, узел графа, ничего."""
    if kind:
        return f"обращение известно ({kind})"
    if f"{target:08x}" in all_regs:
        return "адрес известен, обращение - нет"
    return "адрес не известен"


def render_pool(A, image, text, regs, addr, all_regs):
    """Раздел резолва под псевдокодом функции."""
    syms, binds, _raw, _res, _aliases, _stmts = pool(image, text, regs)
    if not syms:
        return
    A(f"#### Символы пула `{addr}`")
    A("")
    A("Значение литерала декомпилятор не подставляет - печатает имя `DAT_<адрес>`. Ширина "
      "литерала из псевдокода не видна (`mov.l` - 32 бита, `mov.w` - 16 со знаковым "
      "расширением), поэтому даны обе трактовки. Выбирает между ними арифметика: у "
      "выражения `база + смещение` верна та пара, чей адрес граф подтверждает регистром "
      "этой функции. Регистр, названный через пул, - тот же регистр: адрес из этой "
      "таблицы равноправен адресу из листинга.")
    A("")
    A("| Символ | `mov.l` (32) | `mov.w` (16, знак) |")
    A("|---|---|---|")
    for sym, (a, lit) in sorted(syms.items(), key=lambda kv: kv[1][0]):
        l32 = f"`{lit['mov.l']:08x}`" if "mov.l" in lit else "-"
        l16 = f"`0x{lit['mov.w']:04x}`" if "mov.w" in lit else "-"
        A(f"| `{sym}` | {l32} | {l16} |")
    A("")
    if binds:
        A("| Выражение | Адрес | Граф |")
        A("|---|---|---|")
        for (b, o), (t, kind) in sorted(binds.items(), key=lambda kv: kv[1][0]):
            A(f"| `{b} + {o}` | `{t:08x}` | {bind_state(t, kind, all_regs)} |")
        A("")
        A("Адрес в этой таблице сложен сборщиком из значений образа. Столбец `Граф` "
          "говорит только о том, есть ли у сборщика независимый свидетель, и различает "
          "три состояния. Подтверждение усиливает; отсутствие подтверждения не "
          "опровергает - ни одно состояние не означает \"неверно\":")
        A("")
        A("- `обращение известно (R/W/L/D)` - граф знает это обращение именно у этой "
          "функции. Образ и граф сошлись на одном адресе независимо.")
        A("- `адрес известен, обращение - нет` - адрес встречается резолвнутой ссылкой "
          "где-то в ROM'е, но ребра к этой функции нет.")
        A("- `адрес не известен` - адрес не встречается резолвнутой ссылкой нигде. Так "
          "выглядит и неверная трактовка ширины литерала, и поле структуры, к которому "
          "обращаются только смещением от базы в регистре: такое обращение Ghidra не "
          "резолвит, ссылки не пишет, и узла об адресе не заводит. В JK03A под второе "
          "подпадает вся структура `ffff119c` целиком, включая RAM-вход оси `ffff11ae`.")
        A("")
        A("Различает эти два случая код, а не таблица: у верной пары база - это база, "
          "которую функция откуда-то получила, а смещения соседних полей идут подряд.")
        A("")


def render(comp, rom, data, export_dir):
    """Артефакт компоненты либо целевого фокуса - единственный вход агента прогона."""
    L = []
    A = L.append
    focus = data.get("focus")
    focus_axis = data.get("focus_axis")
    if focus_axis:
        A(f"# Ось `{focus_axis}` ({rom})")
    elif focus:
        A(f"# Карта `{focus}` компоненты `{comp['key']}` ({rom})")
    else:
        A(f"# Компонента `{comp['key']}` ({rom})")
    A("")
    if focus_axis:
        A(f"Карт, непосредственно связанных с осью: {len(comp['maps'])}. "
          f"Аксессоров этих карт: {len(comp['accessors'])}.")
        A("")
        A(f"Контекст целевой оси `{focus_axis}` агрегирован по прямым рёбрам "
          f"`AXIS_X`/`AXIS_Y`: включены ВСЕ связанные карты "
          f"({', '.join(f'`{m}`' for m in comp['maps'])}) и ВСЕ их аксессоры "
          f"({', '.join(f'`{a}`' for a in comp['accessors']) or 'нет'}). Общая ось может "
          f"обслуживать карты разных компонент, поэтому одна карта-представитель границу "
          f"контекста не задаёт.")
        A("")
        A("Карты и аксессоры служат контекстом трейса входа оси. Машинерия интерполяции "
          "показывает, как точки оси индексируют ячейку, а RAM и код аксессоров - откуда "
          "приходит текущее значение и в каких единицах оно представлено.")
    else:
        A(f"Карт в компоненте: {len(comp['maps'])}. Аксессоров: {len(comp['accessors'])}.")
        A("")
        A("Компонента связного графа \"аксессор -> карта\": ни одна её карта не читается "
          "аксессором извне, и этим задан состав карт. Границей компоненты ограничен состав, "
          "а не свидетельство: физическую величину карты задают машинерия интерполяции "
          "(обёртка, ядро, finisher) и то, что делает с выходом потребитель RAM. Оба лежат "
          "за компонентой и оба в артефакте есть - разделы \"Машинерия интерполяции\" и "
          "\"Потребители выхода\". Трейс, остановленный на записи в RAM, до семантики не "
          "дошёл: `code` требует довести его до потребителя.")
    A("")
    if focus:
        A(f"Целевая карта - `{focus}`, и свидетельство сужено до её окрестности: разделы "
          f"\"Аксессоры\", \"Машинерия интерполяции\" и \"Потребители выхода\" построены "
          f"по {len(data['acc'])} аксессорам, читающим именно её "
          f"({', '.join(f'`{a}`' for a in data['acc'])}), а не по всем "
          f"{len(comp['accessors'])} аксессорам компоненты. Свидетельства о целевой карте "
          f"это не убавляет: аксессор, её не читающий, о ней и не говорит. Убавляет оно "
          f"свидетельство о СОСЕДНИХ картах - они остаются в разделе \"Карты\" значениями "
          f"и геометрией, без своего кода.")
        A("")
        A("Задача - раздел 6 контракта `tools/map-sweep.md`: вернуть заявку "
          f"(`semantics`, `role`, `units`, `scale_expr`, `confidence`) РОВНО по карте "
          f"`{focus}` и по её осям. Соседние карты - контекст: они показывают, что ещё "
          f"читает общий аксессор, и требуют различать, чей трейс перед тобой.")
    elif focus_axis:
        A("Задача - раздел 6 контракта `tools/map-sweep.md`: вернуть заявку "
          f"(`kind`, `units`, `scale_expr`, `to_byte`, `scale_conf`, `scale_evidence`, "
          f"`note`) РОВНО по оси `{focus_axis}`. Связанные карты, их прочие оси и "
          f"аксессоры - контекст, а не дополнительные цели заявки.")
    else:
        A("Задача - раздел 6 контракта `tools/map-sweep.md`: вернуть заявку на каждую карту "
          "(`semantics`, `role`, `units`, `scale_expr`, `confidence`) и на каждую ось.")
    A("")
    A("Разметки в артефакте нет намеренно: она и есть то, что требуется вывести. "
      "Заявка без трейса - `candidate`, а не `code`, каким бы убедительным ни было "
      "совпадение; сплошь `0xFF` по форме не заключается.")
    A("")

    A("## Карты")
    A("")
    A("| Карта | Форма | Элемент | Семейство | Вход | Ядро | Ось X | Ось Y | Значения |")
    A("|---|---|---|---|---|---|---|---|---|")
    for m in data["maps"]:
        A(f"| `{m['addr']}` | {shape(m['width'], m['height'])} | {m['storagetype']} "
          f"| {m['family']} | {';'.join(m['via']) or '-'} | {';'.join(m['kernel']) or '-'} "
          f"| {';'.join(m['axis_x']) or '-'} | {';'.join(m['axis_y']) or '-'} "
          f"| {m['vmin']}..{m['vmax']} |")
    A("")
    A("Геометрия - свойство входа интерполяции, а не карты: вход специализирован по форме "
      "таблицы. Элемент 2D-карты снят с её finisher'а, все читают беззнаковым.")
    A("")

    for m in data["maps"]:
        tag = " – ЦЕЛЕВАЯ" if m["addr"] == focus else ""
        A(f"### Карта `{m['addr']}` – {shape(m['width'], m['height'])} "
          f"{m['storagetype']}{tag}")
        A("")
        A(f"Диапазон {m['vmin']}..{m['vmax']}, хеш содержимого `{m['values_hash']}`.")
        A("")
        A("```")
        A(grid(m["values"]))
        A("```")
        A("")

    if data["axes"]:
        A("## Оси")
        A("")
        A("| Ось | Точек | Элемент | Возрастает | Значения |")
        A("|---|---|---|---|---|")
        for a in data["axes"]:
            tag = " – ЦЕЛЕВАЯ" if a["addr"] == focus_axis else ""
            A(f"| `{a['addr']}`{tag} | {a['len']} | {a['storagetype']} "
              f"| {'да' if a['monotonic'] else 'НЕТ'} "
              f"| {', '.join(str(v) for v in a['values'])} |")
        A("")
        A("Возрастание - требование ядра (обратный линейный проход от старшей точки вниз "
          "до первой `<=` текущего значения), а не догадка о смысле: массив, который правилу не "
          "отвечает, осью не работает. Чем ось является и в чём измеряется - вывод о "
          "коде, и даёт его трейс RAM-входа.")
        A("")

    A("## Аксессоры")
    A("")
    if focus:
        A(f"Аксессоры целевой карты `{focus}`. Сайты вызова у каждого показаны все, "
          f"включая ведущие в соседние карты: по ним и различается, чей трейс.")
        A("")
    elif focus_axis:
        A(f"Все аксессоры карт, непосредственно связанных с целевой осью `{focus_axis}`. "
          f"Сайты каждого аксессора показаны полностью: в колонках `r5`/`r6` видно, "
          f"какой вызов использует целевую ось, а какой относится к соседнему контексту.")
        A("")
    for f_addr in data["acc"]:
        sites = [s for s in data["sites"] if s["accessor"] == f_addr]
        name = sites[0]["name"] if sites else f_addr
        A(f"### `{f_addr}` ({name})")
        A("")
        A("Сайты вызова и операнды переписи резолвера:")
        A("")
        A("| Сайт | Карта | r4 | kind | r5 | kind5 | r6 | kind6 | verdict |")
        A("|---|---|---|---|---|---|---|---|---|")
        for s in sites:
            A(f"| `{s['callsite']}` | `{s['tbl']}` | `{s['r4']}` | {s['kind']} "
              f"| `{s['r5']}` | {s['kind5']} | `{s['r6']}` | {s['kind6']} "
              f"| {s['verdict']} |")
        A("")
        A("`kind=sp` означает, что декомпилятор операнд не свернул и значение снял линейный "
          "резерв: операнд задан ветвлением, и снятое - один элемент множества, а не факт. "
          "`pool` - указатель из пула, `slice` - вычислен, `const` - непосредственный.")
        A("")

        callers = [c for c in data["callers"] if c["accessor"] == f_addr]
        A(f"Вызыватели ({len(callers)}): "
          + (", ".join(f"`{c['caller']}`" for c in callers) or "нет – корень"))
        A("")
        if callers:
            A("Вызыватель – производитель входа аксессора: аргумент, пришедший регистром или "
              "стеком, внутри аксессора писателя не имеет, и его величину задаёт код "
              "вызывателя. Единица оси, взятой из аргумента, устанавливается там.")
            A("")

        uses = [u for u in data["uses"] if u["accessor"] == f_addr]
        if uses:
            A(f"Обращения к RAM и периферии ({len(uses)}):")
            A("")
            A("| Адрес | Область | Имя | Доступ |")
            A("|---|---|---|---|")
            for u in uses:
                A(f"| `{u['reg']}` | {u['region']} | {u['name'] or '-'} "
                  f"| {''.join(sorted(u['kinds']))} |")
            A("")
            A("Доступ: `R` - чтение, `W` - запись, `L` - загрузка адреса, `D` - данные. "
              "RAM-вход оси даёт её единицу, RAM-выход интерполяции - смысл карты.")
            A("")

        text, path = dumped(export_dir, f_addr, "decomp")
        A(f"#### C-псевдокод `{f_addr}`")
        A("")
        if text is None:
            A(f"Нет файла `{os.path.basename(path)}`: прогон подготовки на эту функцию не "
              f"сделан. Это пропуск шага подготовки, а не свойство компоненты, и трейс "
              f"без него не ведётся.")
        else:
            A("```c")
            A(text)
            A("```")
            A("")
            render_pool(A, data["image"], text, data["func_regs"].get(f_addr, []), f_addr,
                        data["all_regs"])
        A("")

        for c in callers:
            text, path = dumped(export_dir, c["caller"], "decomp")
            A(f"#### C-псевдокод вызывателя `{c['caller']}`")
            A("")
            if text is None:
                A(f"Нет файла `{os.path.basename(path)}`: прогон подготовки на эту функцию "
                  f"не сделан. Это пропуск шага подготовки, а не свойство компоненты.")
            else:
                A("```c")
                A(text)
                A("```")
                A("")
                render_pool(A, data["image"], text,
                            data["func_regs"].get(c["caller"], []), c["caller"],
                            data["all_regs"])
            A("")

        A(f"#### Листинги сайтов `{f_addr}`")
        A("")
        for s in sites:
            render_site_listing(A, export_dir, s)

    A("## Машинерия интерполяции")
    A("")
    A("Ячейку карты читает не аксессор, а обёртка, специализированная по форме таблицы, "
      "и её ядро; finisher вызывается ядром и держит насыщение и элемент. Это код между "
      "картой и записью выхода в RAM: чем ячейка становится к моменту записи, видно "
      "здесь, а не на сайте вызова.")
    A("")
    A("| Адрес | Роль | Размер | Вызывает |")
    A("|---|---|---|---|")
    for k in data["kernels"]:
        cs = ", ".join(f"`{c['addr']}` ({c['size']} б)"
                       for c in stable_callees(k["callees"]) if c.get("addr"))
        A(f"| `{k['addr']}` | {k['role']} | "
          f"{k['size'] if k['size'] is not None else 'НЕ РАЗМЕЧЕН'} | {cs or '-'} |")
    A("")
    if data["kernel_listings"]:
        A("`НЕ РАЗМЕЧЕН`: обёртка уходит в это ядро через `jmp`, а не `jsr`, и в функцию "
          "участок не выделен. C-псевдокода у такого ядра нет; листинг есть и идёт ниже - "
          "разметка функции нужна декомпилятору, а не дизассемблеру. Трейс через такое ядро "
          "ведётся по листингу, и уровень заявки оно само по себе не ограничивает.")
        A("")
    for f_addr in data["kernel_funcs"]:
        text, path = dumped(export_dir, f_addr, "decomp")
        A(f"### C-псевдокод `{f_addr}`")
        A("")
        if text is None:
            A(f"Нет файла `{os.path.basename(path)}`: прогон подготовки на эту функцию "
              f"не сделан.")
        else:
            A("```c")
            A(text)
            A("```")
            A("")
            render_pool(A, data["image"], text, data["func_regs"].get(f_addr, []), f_addr,
                        data["all_regs"])
        A("")

    for k_addr in data["kernel_listings"]:
        text, path = dumped(export_dir, k_addr, "listing")
        A(f"### Листинг `{k_addr}` – ядро без разметки функции")
        A("")
        if text is None:
            A(f"Нет файла `{os.path.basename(path)}`: прогон подготовки на этот адрес не "
              f"сделан.")
        else:
            A("```")
            A(text)
            A("```")
        A("")

    render_library(A, data, export_dir)

    if data["focus"]:
        render_attrib(A, data)

    A("## Потребители выхода")
    A("")
    if not data["consumers"]:
        regs = data["write_regs"]
        A("Потребителей нет: раздел пуст не по недосмотру сборки, а по состоянию графа, и "
          "это факт о данном наборе аксессоров, а не пробел артефакта.")
        A("")
        if data["sinks"]:
            named = ", ".join("`%s`" % s for s in data["sinks"])
            A(f"Набор задан привязкой: читателей у выхода {named} снаружи аксессора нет. "
              "Величина карты либо потребляется внутри аксессора, либо не потребляется "
              "вовсе - и то и другое читается по коду аксессора, а не по коду соседей. "
              "Прочие регистры аксессора несут чужие величины, и разбирать их состав "
              "здесь незачем: о целевой карте они не говорят.")
        elif not regs:
            A("Аксессор компоненты не пишет ни одного регистра RAM. Трейс кончается внутри "
              "аксессора: выход карты дальше него не уходит - либо возвращается вызывателю "
              "значением, либо сравнивается на месте. Смысл, если он устанавливается, "
              "устанавливается по коду аксессора и его сайтов вызова.")
        else:
            hot = [r for r in regs if r["readers"] > data["maxr"]]
            cold = [r for r in regs if r["readers"] == 0]
            A(f"Аксессор пишет {len(regs)} регистров RAM, но ни один не прошёл отбор: "
              f"{len(cold)} без единого читателя снаружи компоненты, {len(hot)} с числом "
              f"читателей выше отсечки {data['maxr']}.")
            A("")
            A("| Регистр | Читателей снаружи |")
            A("|---|---|")
            for r in regs[:24]:
                A(f"| `{r['reg']}` | {r['readers']} |")
            if len(regs) > 24:
                A(f"| ... ещё {len(regs) - 24} | |")
            A("")
            A("Регистр без внешних читателей - выход, который никто не потребляет: либо "
              "ветвь мертва, либо читает его сам аксессор. Регистр выше отсечки - "
              "разделяемая шина, и её потребитель о карте не говорит ничего. Ни то ни "
              "другое семантику карты не закрывает: заявка идёт `candidate`.")
        A("")
    else:
        A("Функции, читающие RAM, которую пишет аксессор. Смысл карты задаёт то, что "
          "происходит с её выходом дальше: запись в RAM - середина трейса, а не его конец.")
        A("")
        if data["sinks"]:
            named = ", ".join("`%s`" % s for s in data["sinks"])
            A(f"Набор задан привязкой: это читатели выхода {named}, и только его. Прочие "
              "регистры аксессора несут чужие величины и в отбор не входят - отсечка по "
              "разделяемости тут не нужна, набор специфичен по построению. Разделяемость "
              "самого привязанного регистра при этом не скрыта: если его читают десятки "
              "функций, они здесь все, и это факт о карте.")
        else:
            A("Привязки выхода нет, поэтому набор выведен из всех записей аксессора и "
              "несёт чужие величины вперемешку с величиной карты. Отобраны потребители "
              f"регистров, у которых читателей не больше {data['maxr']}: регистр с одним "
              "читателем частный для этого аксессора, регистр с тремя десятками - "
              "разделяемая глобаль, и её потребитель о карте не говорит ничего. Связь "
              "потребителя именно с этой картой отсюда не следует - она предмет проверки "
              "по коду, а не вывод из состава таблицы.")
        A("")
        A("Таблица полна: в ней все отобранные потребители. C-псевдокод идёт не у всех - "
          "он под отдельным бюджетом, и колонка \"Код\" говорит, у кого он ниже есть. "
          "Порядок - по специфичности связи (наименьшее число читателей у связывающего "
          "регистра), затем по размеру: приватный регистр ближе к выходу карты, чем "
          "умеренно-разделяемый.")
        A("")
        A("| Потребитель | Размер | Читателей у регистра | Читает регистров | Код "
          "| Регистры |")
        A("|---|---|---|---|---|---|")
        shown = {c["consumer"] for c in data["consumers_decomp"]}
        for c in data["consumers"]:
            A(f"| `{c['consumer']}` | {c['size']} | {c['spec']} | {len(c['regs'])} "
              f"| {'да' if c['consumer'] in shown else 'нет'} "
              f"| {', '.join('`%s`' % r for r in sorted(c['regs']))} |")
        A("")
        if data["consumers_cut"]:
            A(f"Псевдокода нет у {data['consumers_cut']} потребителей из "
              f"{len(data['consumers'])}: бюджет на декомпиляцию - "
              f"{len(data['consumers_decomp'])} наиболее специфичных. Это граница "
              f"артефакта, а не факт о карте: если трейс упирается в потребителя без "
              f"кода, заявка идёт `candidate` с указанием его адреса в `note`, а не "
              f"домысливается по имени регистра.")
            A("")
        for c in data["consumers_decomp"]:
            text, path = dumped(export_dir, c["consumer"], "decomp")
            A(f"### C-псевдокод `{c['consumer']}`")
            A("")
            if text is None:
                A(f"Нет файла `{os.path.basename(path)}`: прогон подготовки на эту "
                  f"функцию не сделан.")
            else:
                A("```c")
                A(text)
                A("```")
                A("")
                render_pool(A, data["image"], text,
                            data["func_regs"].get(c["consumer"], []), c["consumer"],
                            data["all_regs"])
            A("")

    A("## Каталоги-эталоны")
    A("")
    A("Каталоги адресов не несут: они задают классы, а не размещение. Имя из каталога даёт "
      "`candidate`-идентичность, не семантику. Единицы и множитель шкалы - тоже разметка "
      "каталога: взятые из совпадения формы, они дают `candidate`, а не `code` (P6).")
    A("")
    by_shape = {}
    for m in data["maps"]:
        by_shape.setdefault((m["dims"], shape(m["width"], m["height"])),
                            []).append(m["addr"])
    for (dims, sh), addrs in sorted(by_shape.items(), key=lambda kv: kv[0]):
        cands = data["a2l"].get((dims, sh), [])
        A(f"### Форма {sh}: карты {', '.join('`%s`' % a for a in addrs)}")
        A("")
        if not cands:
            A("Каталог этой формы не знает.")
            A("")
            continue
        A(f"Записей каталога с такой формой: {len(cands)}.")
        A("")
        A("| Имя | Единица | Шкала | Элемент | Ось X | Ось Y | Категория |")
        A("|---|---|---|---|---|---|---|")
        for c in cands:
            A(f"| {c['name']} | {c['unit'] or '-'} | {c['scale_expr'] or '-'} "
              f"| {c['storagetype'] or '-'} | {c['axis_x_sem'] or '-'} "
              f"| {c['axis_y_sem'] or '-'} | {c['category'] or '-'} |")
        A("")
    A("Ключ здесь - одна геометрия: из трёх ключей матча (`dims`, scale-family, семантика "
      "осей) два последних сами суть разметка, которой в артефакте нет. Форму 16x16 несут "
      "16 записей каталога – это подсказка, а не идентификация, и различает их трейс "
      "RAM-входов осей.")
    A("")

    A("### Вендорские словари через A2L по `concept` (только `origin=factory`)")
    A("")
    if not data["concepts"]:
        A("Записи каталога, совпавшие формой, `concept` не несут: связка с вендорским "
          "словарём не установлена. Матч по имени вслепую запрещён (P6).")
        A("")
    elif not data["vendor"]:
        A(f"Концепты записей A2L этой формы ({', '.join('`%s`' % c for c in data['concepts'])}) "
          f"заводских вендорских записей не имеют.")
        A("")
    else:
        A(f"Цепочка: геометрия карты -> запись A2L -> её `concept` -> записи вендоров. "
          f"Концепты: {', '.join('`%s`' % c for c in data['concepts'])}.")
        A("")
        A("| Вендор | Имя | Группа | Ось X | Ось Y | Выход | concept |")
        A("|---|---|---|---|---|---|---|")
        for v in data["vendor"]:
            A(f"| {v['vendor']} | {v['name']} | {v['grp'] or '-'} | {v['axis_x'] or '-'} "
              f"| {v['axis_y'] or '-'} | {v['output'] or '-'} | {v['concept'] or '-'} |")
        A("")
        A("Гранулярность `concept` - семейство калибровки, а не одна таблица: варианты одной "
          "функции значение делят, поэтому записей на концепт бывает несколько.")
        A("")

    A("### Якоря по содержимому: документированные дефолты против плоских карт")
    A("")
    if not data["anchors"]:
        A("Совпадений нет: ни одна константа плоской карты компоненты не равна "
          "документированному дефолту словарей.")
        A("")
    else:
        A("| Значение | Вендор | Предмет | Единица | Применимость | Карты |")
        A("|---|---|---|---|---|---|")
        for a in data["anchors"]:
            A(f"| {a['value']} | {a['vendor']} | {a['subject']} | {a['units'] or '-'} "
              f"| {a['applies_to']} | {', '.join('`%s`' % x for x in a['in_maps'])} |")
        A("")
        A("Совпадение значения само по себе даёт `pattern`, а не `candidate`: чем короче "
          "число, тем чаще оно встретится случайно. До `candidate` находку поднимает "
          "подтверждение – гомологичная сигнатура блока либо трейс потребителя. "
          "Применимость проверяется: EcuTek документирует VQ37VHR с VVEL, а JK03A – "
          "VQ25HR без него.")
        A("")
    A("Дефолт сверяется только с плоскими картами (`vmin == vmax`): в поверхности из 256 "
      "ячеек встречается почти любой байт, и совпадение там не значило бы ничего.")
    A("")

    return "\n".join(L) + "\n"


# Поля разметки, чьё значение - свободный текст: совпадение такого значения в артефакте
# есть утечка. role, confidence, units и kind оси из сверки исключены намеренно: их
# словарь замкнут и короток ('table', 'code', 'deg', 'rpm'), подстрока совпала бы
# случайно, и сверка давала бы шум в обе стороны. Их не пускает белый список RETURN, а не
# эта проверка - у двух механизмов разные роли.
ANSWER_TEXT = ("semantics", "note", "scale_expr", "to_byte", "evidence",
               "contract_evidence", "scale_evidence")


def answer_occurs(text, value, field):
    """Совпадение ответа в тексте без ложных подстрок у короткого to_byte."""
    if field == "to_byte" and len(value.strip()) < 4:
        # `x`, `x/2`, `x/4` - реальные обратные шкалы. Обычный поиск подстроки нашёл бы
        # `x` в `scale_expr` и `x/2` в `x/20`; границы выражения сохраняют аудит и убирают
        # эти заведомые ложные совпадения.
        pattern = rf"(?<![\w.+*/%-]){re.escape(value)}(?![\w.+*/%-])"
        return re.search(pattern, text) is not None
    return value in text


def catalog_strings(data):
    """Строки, которые артефакт несёт из каталога законно.

    Каталог в артефакте нужен по контракту (раздел 2), и разметка часто взята из него же:
    шкалу 'x-64' у карт зажигания 16x16 A2L объявляет сам, а в графе она стоит с пометкой
    [cand] - множитель из каталога, кодом не закреплённый. Совпав с каталогом дословно,
    разметка из сверки выпадает: её появление в артефакте объяснено независимым
    источником, и агент читает каталог, а не ответ.
    """
    out = set()
    for rows in list(data["a2l"].values()) + [data["vendor"], data["anchors"]]:
        for r in rows:
            out |= {v for v in r.values() if isinstance(v, str)}
    return out


def verify_blind(text, answers, allowed):
    """Ослепление - проверяемое свойство прогона, а не намерение автора запросов.

    Сверяет текст артефакта с той самой разметкой, которую он нести не должен. Ловит и
    ошибку в RETURN, и разметку, просочившуюся через чужое поле: имя функции из
    symbols.csv, C-псевдокод с осмысленным именем, строку переписи. Утечка - разметка, у
    которой в артефакте нет независимого источника (allowed); находка - остановка
    прогона: артефакт с ответом превращает калибровку в репетицию и обесценивает
    единственный прогон, где харнесс можно проверить.
    """
    leaks = []
    for row in answers:
        for field in ANSWER_TEXT:
            value = row.get(field)
            if not value or not isinstance(value, str):
                continue
            if len(value.strip()) < 4 and field != "to_byte":
                continue
            if not answer_occurs(text, value, field):
                continue
            # Оправдание засчитывается тем же видом совпадения, что и сама утечка: шкала
            # `x-128` стоит в каталожной строке `Degrees (x-128)*0.5`, и её появление
            # объяснено тем же независимым источником, что и совпадение дословное. Сверять
            # утечку подстрокой, а источник - полным равенством значит останавливать прогон
            # на коротких общих значениях, которых у offset-binary шкал большинство.
            if any(answer_occurs(a, value, field) for a in allowed):
                continue
            leaks.append(f"{row['addr']}.{field} = {value!r}")
    return leaks


def build(session, image, rom, comp, export_dir, catalog, maxr, focus=None,
          maxdec=24, focus_axis=None):
    # Состав карт задаёт компонента либо полный контекст оси, состав свидетельства - фокус:
    # без фокуса окрестностью служит вся компонента, с фокусом карты - её аксессоры. У оси
    # comp уже содержит точное объединение всех непосредственно связанных карт и аксессоров.
    if focus and focus_axis:
        raise ValueError("фокус карты и оси взаимоисключающие")
    if focus:
        acc = stable_addrs(session.run(FOCUS_ACC, rom=rom, map=focus).single()["accessors"])
        if not acc:
            raise SystemExit(f"карту {focus} не читает ни один аксессор")
    else:
        acc = stable_addrs(comp["accessors"])
    maps = stable_map_facts(
        r.data() for r in session.run(MAP_FACTS, rom=rom, addrs=stable_addrs(comp["maps"]))
    )
    for m in maps:
        m["values"] = read_values(image, m)
    axes = sorted({a for m in maps for a in m["axis_x"] + m["axis_y"]})
    if focus_axis and focus_axis not in axes:
        raise SystemExit(f"ось {focus_axis} не связана с картами контекста")
    kernels = sorted(
        (r.data() for r in session.run(KERNELS, rom=rom,
                                       maps=[focus] if focus else stable_addrs(comp["maps"]))),
        key=lambda row: row["addr"],
    )
    data = {
        "maps": maps,
        "focus": focus,
        "focus_axis": focus_axis,
        "acc": acc,
        "axes": sorted(
            (r.data() for r in session.run(AXIS_FACTS, rom=rom, addrs=axes)),
            key=lambda row: row["addr"],
        ),
        "sites": stable_sites([r.data() for r in session.run(SITES, rom=rom, addrs=acc)]),
        "callers": [r.data() for r in session.run(CALLERS, rom=rom, addrs=acc)],
        "uses": [r.data() for r in session.run(USES, rom=rom, addrs=acc)],
        "kernels": kernels,
        "write_regs": [r.data() for r in session.run(WRITE_REGS, rom=rom, addrs=acc)],
        "maxr": maxr,
        "a2l": {},
        "vendor": [],
        "concepts": [],
        "anchors": [],
    }
    # Привязка выхода идёт до потребителей и задаёт их набор. Без фокуса привязывать не к
    # чему: компонента несёт много карт, и их выходы в один набор не сводятся.
    data["all_regs"] = set(session.run(ALL_REGS, rom=rom).single()["addrs"])
    acc_regs = {r["func"]: r["regs"] for r in session.run(FUNC_REGS, rom=rom, addrs=acc)}
    data["attrib"] = []
    if focus:
        bases = {m["addr"] for m in maps}
        for a in acc:
            text, _p = dumped(export_dir, a, "decomp")
            if text is None:
                continue
            for rec in attribute(image, text, acc_regs.get(a, []), bases):
                if rec["base"] == focus:
                    data["attrib"].append({"acc": a, **rec})
    sinks = sorted({r["sink"] for r in data["attrib"] if r["kind"] in ("reg", "ram")})
    # Величина шире байта занимает несколько адресов, и читатель берёт любой из них:
    # окно задаётся шириной записи, а не догадкой о соседстве.
    span = sorted({f"{int(r['sink'], 16) + k:08x}"
                   for r in data["attrib"] if r["kind"] in ("reg", "ram")
                   for k in range(max(r["width"], 1))})
    data["sinks"] = sinks
    if sinks:
        data["consumers"] = [r.data() for r in
                             session.run(CONSUMERS_OF, rom=rom, addrs=acc, regs=span)]
    else:
        data["consumers"] = [r.data() for r in
                             session.run(CONSUMERS, rom=rom, addrs=acc, maxr=maxr)]
    # Таблица потребителей идёт полной, код - под бюджетом: запрос отдал их уже в порядке
    # специфичности, так что голова списка и есть наиболее близкое к выходу карты.
    data["consumers_decomp"] = data["consumers"][:maxdec]
    data["consumers_cut"] = len(data["consumers"]) - len(data["consumers_decomp"])
    # Декомпилируется то, что размечено функцией: у ядра за jmp размера нет и файла тоже.
    data["kernel_funcs"] = sorted(
        {k["addr"] for k in kernels if k["size"] is not None}
        | {c["addr"] for k in kernels for c in k["callees"] if c.get("addr")}
    )
    # Ядро за jmp идёт листингом: разметка функции нужна декомпилятору, а дизассемблеру
    # нет, и код ядра читается там же. Без этого агент видел адрес ядра и не видел ядра.
    data["kernel_listings"] = sorted({k["addr"] for k in kernels if k["size"] is None})
    # Резолв пула: образ даёт значение литерала, граф - множество для его проверки.
    data["image"] = image
    decompiled = sorted(set(acc) | set(data["kernel_funcs"])
                        | {c["consumer"] for c in data["consumers_decomp"]}
                        | {c["caller"] for c in data["callers"]})
    data["func_regs"] = {r["func"]: r["regs"] for r in
                         session.run(FUNC_REGS, rom=rom, addrs=decompiled)}
    # Функции, вызываемые из показанного кода и разобранные слоем кода. Библиотека
    # арифметики (0x21000..0x23000) передаёт аргументы регистрами, Ghidra соглашения не
    # восстанавливает, и в псевдокоде её вызовы стоят без аргументов - величина карты
    # входит в такую функцию, и трейс на ней обрывается. Контракт обрыв снимает.
    shown = sorted(set(decompiled) | set(data["kernel_listings"]))
    called = {r["addr"] for r in session.run(CALLED, rom=rom, addrs=shown)}
    # Листинги показывают цель jsr прямо (`-> 00021bbc`), и там, где Ghidra ребро не
    # построила, текст остаётся единственным источником. Два канала складываются.
    for a in shown:
        text, _p = dumped(export_dir, a, "decomp")
        if text is None:
            text, _p = dumped(export_dir, a, "listing")
        if text:
            called |= {m.group(1) for m in CALLED_ADDR.finditer(text)}
    called -= set(decompiled)
    data["library"] = [r.data() for r in
                       session.run(CONTRACTS, rom=rom, addrs=sorted(called))]
    for m in maps:
        key = (m["dims"], shape(m["width"], m["height"]))
        if key not in data["a2l"]:
            data["a2l"][key] = catalog["a2l"].get(key, [])
    concepts = sorted({c["concept"] for rows in data["a2l"].values() for c in rows
                       if c.get("concept")})
    data["concepts"] = concepts
    data["vendor"] = [v for v in catalog["vendor"] if v["concept"] in set(concepts)]

    # Якорь ищется только в плоских картах (vmin == vmax). В поверхности из 256 ячеек
    # встречается почти любой байт, и совпадение с документированным дефолтом там не
    # значит ничего - это вывод из формы данных, которым pattern-scan уже дважды ошибся
    # (P6). У плоской карты константа и есть карта, и совпадение с дефолтом - сигнал.
    flat = {m["addr"]: m["vmin"] for m in maps if m["vmin"] == m["vmax"]}
    for c in catalog["consts"]:
        hits = sorted(a for a, v in flat.items() if v == c["number"])
        if hits:
            data["anchors"].append(dict(c, in_maps=hits))

    text = render(comp, rom, data, export_dir)
    answers = [r.data() for r in session.run(MAP_ANSWERS, rom=rom, addrs=comp["maps"])]
    answers += [r.data() for r in session.run(AXIS_ANSWERS, rom=rom, addrs=axes)]
    answers += [r.data() for r in session.run(FUNC_ANSWERS, rom=rom)]
    return text, verify_blind(text, answers, catalog_strings(data))


def load_catalog(session):
    """Каталоги грузятся раз на прогон: они rom-независимы и от компоненты не зависят."""
    pairs = [(r["dims"], r["shape"]) for r in
             session.run("MATCH (e:A2LEntry {family:'HR'}) RETURN DISTINCT "
                         "e.dims AS dims, e.shape AS shape")]
    a2l = {}
    for dims, sh in pairs:
        a2l[(dims, sh)] = [x.data() for x in session.run(A2L_BY_SHAPE, dims=dims,
                                                         shape=sh)]
    concepts = [r["c"] for r in session.run(
        "MATCH (e:A2LEntry {family:'HR'}) WHERE e.concept <> '' RETURN DISTINCT e.concept AS c")]
    vendor = [x.data() for x in session.run(VENDOR_BY_CONCEPT, concepts=concepts)]
    consts = []
    for r in session.run(VENDOR_CONSTS):
        c = r.data()
        num = re.match(r"^-?\d+(\.\d+)?$", str(c["value"]).strip())
        if not num:
            continue
        v = float(c["value"])
        if v != int(v) or not 0 <= v <= 0xFFFF:
            continue          # ячейка карты - целое в диапазоне элемента
        consts.append(dict(c, number=int(v)))
    return {"a2l": a2l, "vendor": vendor, "consts": consts}


def nonnegative_int(value):
    """Целое >= 0 для бюджетов артефакта."""
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("значение должно быть >= 0")
    return parsed


def focus_addrs(values, path=None):
    """Адреса из повторяемого флага и файла: нижний регистр, без дублей, стабильно."""
    out = [value.strip().lower() for value in values if value.strip()]
    if path:
        with open(path, encoding="utf-8") as source:
            out.extend(line.strip().lower() for line in source if line.strip())
    return stable_addrs(out)


def main():
    p = argparse.ArgumentParser(description="Артефакты компонент для sweep (map-sweep.md)")
    p.add_argument("out_dir")
    p.add_argument("--rom", default="JK03A")
    p.add_argument("--accessor", action="append", default=[],
                   help="ключ компоненты - адрес её аксессора (волна 0: 00082c8a)")
    p.add_argument("--focus-map", action="append", default=[],
                   help="артефакт на карту, а не на компоненту: свидетельство сужается до "
                        "аксессоров этой карты, файл идёт как map-<addr>.md")
    p.add_argument("--focus-maps-file", default=None,
                   help="то же списком: по адресу карты на строку")
    p.add_argument("--focus-axis", action="append", default=[],
                   help="артефакт на ось: полный контекст всех связанных карт и их "
                        "аксессоров, файл идёт как axis-<addr>.md")
    p.add_argument("--focus-axes-file", default=None,
                   help="то же списком: по адресу оси на строку")
    p.add_argument("--min-maps", type=int, default=0)
    p.add_argument("--max-maps", type=int, default=10 ** 6)
    p.add_argument("--max-readers", type=nonnegative_int, default=8,
                   help="потолок читателей регистра, при котором его потребитель идёт "
                        "в артефакт: мера специфичности выхода (умеренные да, горячие нет)")
    p.add_argument("--max-consumer-decomp", type=nonnegative_int, default=24,
                   help="бюджет на C-псевдокод потребителей: таблица печатается полной, "
                        "код - у стольких наиболее специфичных")
    p.add_argument("--export-dir", default=None,
                   help="прогон подготовки: decomp_<addr>.c и listing_<addr>.txt")
    p.add_argument("--audit-output", default=None,
                   help="JSON-отчёт успешного blind gate и SHA-256 артефактов")
    args = p.parse_args()
    focus_maps = focus_addrs(args.focus_map, args.focus_maps_file)
    focus_axes = focus_addrs(args.focus_axis, args.focus_axes_file)
    if focus_maps and focus_axes:
        p.error("фокус карты и фокус оси взаимоисключающие")

    export_dir = args.export_dir or EXPORT.format(rom=args.rom)
    image = romkit.load(args.rom)
    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    os.makedirs(args.out_dir, exist_ok=True)

    with driver.session() as s:
        comps = components(s, args.rom)
        if not comps:
            sys.exit(f"в графе нет компонент rom={args.rom} - слой строит "
                     f"tools/memgraph/load_maps.py")
        if focus_axes:
            jobs = axis_focus_jobs(s, args.rom, focus_axes)
        elif focus_maps:
            by_map = {m: c for c in comps for m in c["maps"]}
            missed = [m for m in focus_maps if m not in by_map]
            if missed:
                sys.exit(f"карт нет в графе: {', '.join(sorted(missed))}")
            jobs = [(by_map[m], m, None, f"map-{m}.md") for m in focus_maps]
        else:
            if args.accessor:
                want = {a.lower() for a in args.accessor}
                picked = [c for c in comps if want & set(c["accessors"])]
                missed = want - {a for c in picked for a in c["accessors"]}
                if missed:
                    sys.exit(f"аксессоров нет в графе: {', '.join(sorted(missed))}")
            else:
                picked = [c for c in comps
                          if args.min_maps <= len(c["maps"]) <= args.max_maps]
            jobs = [(c, None, None, f"comp-{c['key']}.md") for c in picked]
        catalog = load_catalog(s)
        print(f"компонент в графе: {len(comps)}, артефактов к сборке: {len(jobs)}")

        leaked = 0
        audit_artifacts = []
        for c, focus, focus_axis, fname in jobs:
            text, leaks = build(
                s, image, args.rom, c, export_dir, catalog, args.max_readers,
                focus=focus, maxdec=args.max_consumer_decomp, focus_axis=focus_axis,
            )
            path = os.path.join(args.out_dir, fname)
            with open(path, "w") as f:
                f.write(text)
            with open(path, "rb") as artifact_stream:
                artifact_sha256 = hashlib.sha256(artifact_stream.read()).hexdigest()
            audit_artifacts.append({
                "target_address": focus or focus_axis or c["key"],
                "path": str(Path(path).resolve()),
                "sha256": artifact_sha256,
                "blind_verified": not leaks,
            })
            if focus_axis:
                note = (f"ось {focus_axis}, {len(c['maps'])} карт, "
                        f"{len(c['accessors'])} аксессоров")
            elif focus:
                note = f"компонента {c['key']}, {len(c['maps'])} карт"
            else:
                note = f"{len(c['maps'])} карт, {len(c['accessors'])} аксессоров"
            if leaks:
                leaked += 1
                print(f"  {os.path.basename(path)}: {note} - ОСЛЕПЛЕНИЕ НАРУШЕНО")
                for x in leaks:
                    print(f"      просочилось: {x}")
            else:
                print(f"  {os.path.basename(path)}: {note}")
    driver.close()

    if leaked:
        sys.exit(f"артефактов с разметкой: {leaked} - прогон не годен: агент, читающий "
                 f"ответ, харнесс не проверяет")

    if args.audit_output:
        builder_path = str(Path(__file__).resolve())
        with open(builder_path, "rb") as builder_stream:
            builder_sha256 = hashlib.sha256(builder_stream.read()).hexdigest()
        audit = {
            "schema": "vq.blind-artifact-audit/v1",
            "rom": args.rom,
            "mode": "focus-maps" if focus_maps else "focus-axes" if focus_axes else "components",
            "targets": focus_maps or focus_axes or [item["target_address"] for item in audit_artifacts],
            "builder_path": builder_path,
            "builder_sha256": builder_sha256,
            "export_dir": str(Path(export_dir).resolve()),
            "max_readers": args.max_readers,
            "max_consumer_decomp": args.max_consumer_decomp,
            "artifacts": audit_artifacts,
        }
        audit_path = str(Path(args.audit_output).resolve())
        os.makedirs(os.path.dirname(audit_path), exist_ok=True)
        data = (json.dumps(audit, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
        if os.path.exists(audit_path):
            with open(audit_path, "rb") as existing:
                if existing.read() != data:
                    sys.exit(f"blind audit уже существует с другим содержимым: {audit_path}")
        with open(audit_path, "wb") as audit_stream:
            audit_stream.write(data)


if __name__ == "__main__":
    main()
