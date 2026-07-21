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

Запуск: uv run --no-project --with neo4j python tools/sweep/build_artifacts.py \
          <out_dir> [--rom JK03A] [--accessor <addr>] [--min-maps N] [--max-maps N] \
          [--export-dir <dir>]
"""
import argparse
import os
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
# :Map; kind, units, scale_expr, confidence, note у :Axis), - заявка агента.
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
       m.units AS units, m.scale_expr AS scale_expr, m.confidence AS confidence
"""

AXIS_ANSWERS = """
MATCH (a:Axis {rom:$rom}) WHERE a.addr IN $addrs
RETURN a.addr AS addr, a.kind AS kind, a.units AS units, a.scale_expr AS scale_expr,
       a.note AS note, a.confidence AS confidence
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

SITES = """
MATCH (f:Func {rom:$rom})-[x:ACCESSES]->(m:Map {rom:$rom})
WHERE f.addr IN $addrs
RETURN f.addr AS accessor, f.name AS name, f.size AS size, m.addr AS tbl,
       x.callsite AS callsite, x.r4 AS r4, x.r5 AS r5, x.r6 AS r6,
       x.kind AS kind, x.kind5 AS kind5, x.kind6 AS kind6, x.verdict AS verdict
ORDER BY accessor, callsite
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
CONSUMERS = """
MATCH (a:Func {rom:$rom})-[:USES {kind:'W'}]->(g:Reg {rom:$rom})
WHERE a.addr IN $addrs
OPTIONAL MATCH (c:Func {rom:$rom})-[:USES {kind:'R'}]->(g) WHERE NOT c.addr IN $addrs
WITH g, count(DISTINCT c) AS readers
WHERE readers >= 1 AND readers <= $maxr
MATCH (c2:Func {rom:$rom})-[:USES {kind:'R'}]->(g) WHERE NOT c2.addr IN $addrs
RETURN c2.addr AS consumer, c2.size AS size, collect(DISTINCT g.addr) AS regs
ORDER BY consumer
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


POOL_SYM = re.compile(r"\b((?:PTR_)?(?:DAT|FUN)_00([0-9a-f]{6}))\b")
POOL_ALIAS = re.compile(r"\b(\w+) = ((?:PTR_)?(?:DAT|FUN)_00[0-9a-f]{6})\s*;")
POOL_EXPR = re.compile(r"\(\s*(\w+)\s*\+\s*(\w+|0x[0-9a-fA-F]+)\s*\)")


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


def pool(image, text, regs):
    """Литералы пула псевдокода и привязка его выражений к регистрам.

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
    alias = {var: sym for var, sym in POOL_ALIAS.findall(text) if sym in syms}
    known = {int(r["addr"], 16): r["kind"] for r in regs}

    def base(term):
        sym = alias.get(term, term)
        return syms.get(sym, (None, {}))[1].get("mov.l"), sym

    def disp(term):
        if term.startswith("0x"):
            # декомпилятор эмитит C-суффиксы (0x1c00U, ...L); одиночный странный
            # литерал не должен ронять сборку - вызывающий пропускает None
            try:
                return int(term.rstrip("uUlL"), 16), term
            except ValueError:
                return None, term
        sym = alias.get(term, term)
        v = syms.get(sym, (None, {}))[1]
        return v.get("mov.w"), sym

    binds = {}
    for lhs, rhs in POOL_EXPR.findall(text):
        b, bsym = base(lhs)
        o, osym = disp(rhs)
        if b is None or o is None or not 0xFFFF0000 <= b <= 0xFFFFFFFF:
            continue
        target = (b + o) & 0xFFFFFFFF
        binds[(bsym, osym)] = (target, known.get(target))
    return syms, binds


def bind_state(target, kind, all_regs):
    """Сила привязки: ребро графа, узел графа, ничего."""
    if kind:
        return f"обращение известно ({kind})"
    if f"{target:08x}" in all_regs:
        return "адрес известен, обращение - нет"
    return "адрес не известен"


def render_pool(A, image, text, regs, addr, all_regs):
    """Раздел резолва под псевдокодом функции."""
    syms, binds = pool(image, text, regs)
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
    """Артефакт компоненты - markdown: единственный вход агента прогона."""
    L = []
    A = L.append
    A(f"# Компонента `{comp['key']}` ({rom})")
    A("")
    A(f"Карт: {len(comp['maps'])}. Аксессоров: {len(comp['accessors'])}.")
    A("")
    A("Компонента связного графа \"аксессор -> карта\": ни одна её карта не читается "
      "аксессором извне, и этим задан состав карт. Границей компоненты ограничен состав, "
      "а не свидетельство: физическую величину карты задают машинерия интерполяции "
      "(обёртка, ядро, finisher) и то, что делает с выходом потребитель RAM. Оба лежат "
      "за компонентой и оба в артефакте есть - разделы \"Машинерия интерполяции\" и "
      "\"Потребители выхода\". Трейс, остановленный на записи в RAM, до семантики не "
      "дошёл: `code` требует довести его до потребителя.")
    A("")
    A("Задача - раздел 6 контракта `tools/map-sweep.md`: вернуть заявку на каждую карту "
      "(`semantics`, `role`, `units`, `scale_expr`, `confidence`) и на каждую ось. "
      "Разметки в артефакте нет намеренно: она и есть то, что требуется вывести. "
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
        A(f"### Карта `{m['addr']}` – {shape(m['width'], m['height'])} {m['storagetype']}")
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
            A(f"| `{a['addr']}` | {a['len']} | {a['storagetype']} "
              f"| {'да' if a['monotonic'] else 'НЕТ'} "
              f"| {', '.join(str(v) for v in a['values'])} |")
        A("")
        A("Возрастание - требование ядра (бинарный поиск от старшей точки вниз до первой "
          "`<=` текущего значения), а не догадка о смысле: массив, который правилу не "
          "отвечает, осью не работает. Чем ось является и в чём измеряется - вывод о "
          "коде, и даёт его трейс RAM-входа.")
        A("")

    A("## Аксессоры")
    A("")
    for f_addr in comp["accessors"]:
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

        A(f"#### Листинги сайтов `{f_addr}`")
        A("")
        for s in sites:
            text, path = dumped(export_dir, s["callsite"], "listing")
            A(f"##### Сайт `{s['callsite']}` -> карта `{s['tbl']}`")
            A("")
            if text is None:
                A(f"Нет файла `{os.path.basename(path)}`: прогон подготовки этот сайт не "
                  f"покрыл.")
            else:
                A("```")
                A(text)
                A("```")
            A("")

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
                       for c in k["callees"] if c.get("addr"))
        A(f"| `{k['addr']}` | {k['role']} | "
          f"{k['size'] if k['size'] is not None else 'НЕ РАЗМЕЧЕН'} | {cs or '-'} |")
    A("")
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

    if data["consumers"]:
        A("## Потребители выхода")
        A("")
        A("Функции, читающие RAM, которую пишет аксессор компоненты. Смысл карты задаёт "
          "то, что происходит с её выходом дальше: запись в RAM - середина трейса, а не "
          "его конец. Отобраны потребители регистров, у которых читателей не больше "
          f"{data['maxr']}: регистр с одним читателем частный для этой компоненты, "
          "регистр с тремя десятками - разделяемая глобаль, и её потребитель о карте не "
          "говорит ничего.")
        A("")
        A("| Потребитель | Размер | Читает регистров | Регистры |")
        A("|---|---|---|---|")
        for c in data["consumers"]:
            A(f"| `{c['consumer']}` | {c['size']} | {len(c['regs'])} "
              f"| {', '.join('`%s`' % r for r in sorted(c['regs']))} |")
        A("")
        for c in data["consumers"]:
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
ANSWER_TEXT = ("semantics", "note", "scale_expr")


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
            if not value or not isinstance(value, str) or len(value.strip()) < 4:
                continue
            if value in allowed:
                continue
            if value in text:
                leaks.append(f"{row['addr']}.{field} = {value!r}")
    return leaks


def build(session, image, rom, comp, export_dir, catalog, maxr):
    maps = [r.data() for r in session.run(MAP_FACTS, rom=rom, addrs=comp["maps"])]
    for m in maps:
        m["values"] = read_values(image, m)
    axes = sorted({a for m in maps for a in m["axis_x"] + m["axis_y"]})
    kernels = [r.data() for r in session.run(KERNELS, rom=rom, maps=comp["maps"])]
    data = {
        "maps": maps,
        "axes": [r.data() for r in session.run(AXIS_FACTS, rom=rom, addrs=axes)],
        "sites": [r.data() for r in session.run(SITES, rom=rom, addrs=comp["accessors"])],
        "callers": [r.data() for r in session.run(CALLERS, rom=rom,
                                                  addrs=comp["accessors"])],
        "uses": [r.data() for r in session.run(USES, rom=rom, addrs=comp["accessors"])],
        "kernels": kernels,
        "consumers": [r.data() for r in session.run(CONSUMERS, rom=rom,
                                                    addrs=comp["accessors"], maxr=maxr)],
        "maxr": maxr,
        "a2l": {},
        "vendor": [],
        "concepts": [],
        "anchors": [],
    }
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
    decompiled = sorted(set(comp["accessors"]) | set(data["kernel_funcs"])
                        | {c["consumer"] for c in data["consumers"]})
    data["func_regs"] = {r["func"]: r["regs"] for r in
                         session.run(FUNC_REGS, rom=rom, addrs=decompiled)}
    data["all_regs"] = set(session.run(ALL_REGS, rom=rom).single()["addrs"])
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


def main():
    p = argparse.ArgumentParser(description="Артефакты компонент для sweep (map-sweep.md)")
    p.add_argument("out_dir")
    p.add_argument("--rom", default="JK03A")
    p.add_argument("--accessor", action="append", default=[],
                   help="ключ компоненты - адрес её аксессора (волна 0: 00082c8a)")
    p.add_argument("--min-maps", type=int, default=0)
    p.add_argument("--max-maps", type=int, default=10 ** 6)
    p.add_argument("--max-readers", type=int, default=8,
                   help="потолок читателей регистра, при котором его потребитель идёт "
                        "в артефакт: мера специфичности выхода (умеренные да, горячие нет)")
    p.add_argument("--export-dir", default=None,
                   help="прогон подготовки: decomp_<addr>.c и listing_<addr>.txt")
    args = p.parse_args()

    export_dir = args.export_dir or EXPORT.format(rom=args.rom)
    image = romkit.load(args.rom)
    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    os.makedirs(args.out_dir, exist_ok=True)

    with driver.session() as s:
        comps = components(s, args.rom)
        if not comps:
            sys.exit(f"в графе нет компонент rom={args.rom} - слой строит "
                     f"tools/memgraph/load_maps.py")
        if args.accessor:
            want = {a.lower() for a in args.accessor}
            picked = [c for c in comps if want & set(c["accessors"])]
            missed = want - {a for c in picked for a in c["accessors"]}
            if missed:
                sys.exit(f"аксессоров нет в графе: {', '.join(sorted(missed))}")
        else:
            picked = [c for c in comps
                      if args.min_maps <= len(c["maps"]) <= args.max_maps]
        catalog = load_catalog(s)
        print(f"компонент в графе: {len(comps)}, выбрано: {len(picked)}")

        leaked = 0
        for c in picked:
            text, leaks = build(s, image, args.rom, c, export_dir, catalog,
                                args.max_readers)
            path = os.path.join(args.out_dir, f"comp-{c['key']}.md")
            with open(path, "w") as f:
                f.write(text)
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


if __name__ == "__main__":
    main()
