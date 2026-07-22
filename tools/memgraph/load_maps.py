#!/usr/bin/env python3
# Загрузка калибровочного слоя (Stage 3, разделы 5 и 7 tools/map-flag-pipeline.md) в
# Memgraph: узлы :Interp/:Map/:Axis и рёбра :ACCESSES/:VIA/:KERNEL/:AXIS_X/:AXIS_Y.
# Переносит в граф то, чего :CALLS не несёт, - операнды вызова: какая таблица и какие
# оси переданы аксессором в r4/r5/r6 (P2).
#
# Источников четыре, и каждый отвечает за своё:
#   defs/<rom>.interp.csv   - реестр входов интерполяции: строка = вход со своей
#                             геометрией, снятой с его кода (Stage 2);
#   accessors.<kernel>.csv  - переписи резолвера (ResolveAccessors.java): сайты и
#                             операнды, снятые data-flow декомпилятора (Stage 3);
#   defs/<rom>.findings.csv - ручной слой карт: что установлено человеком и чего перепись
#                             дать не может (семантика, единицы, уровень, роль);
#   defs/<rom>.axes.csv     - ручной слой осей: семантика оси и её единицы.
# Единицы - в ручном слое, а не в переписи: шкалу даёт трейс потребителя, а не операнд
# вызова. Резолвер видит указатель на массив, но не то, во что превращает его значение
# арифметика мотора.
#
# Пятый источник - сам образ ROM (реестр rom-images/roms.csv -> файл дампа, сверка по
# sha256). Перепись говорит, по какому адресу и какой формой читать; что там лежит,
# говорит образ, и это Stage 4: диапазон, содержимое, монотонность оси.
#
# Слой грузится целиком, всеми цензами сразу: узлы слоя пересоздаются на каждом прогоне,
# поэтому ценз на прогон означал бы, что загрузка второго ядра сносит карты первого. По
# той же причине ручной слой грузится здесь, а не отдельным прогоном: находка живёт на
# том же узле, что и факт переписи, и пересоздание узла унесло бы её с собой.
#
# Реестр (строка = вход):
#   family      - explicit-axis (ось - массив breakpoint'ов в ПЗУ, указатель в r5/r6)
#                 либо implicit-axis (массива нет: точки 0..N-1 с равномерным шагом по
#                 сырому входу);
#   kernel      - общий движок входа, он же имя файла переписи;
#   wrapper     - адрес самого входа;
#   width/height- число точек оси; height пуст - вход одномерный;
#   step        - шаг неявной оси (только implicit-axis);
#   storagetype - элемент. У 1D-входа его читает сам вход, у 2D - его finisher (вход
#                 держит указатель на него в своём пуле и уходит туда хвостовым
#                 переходом). У implicit-axis элемент задаёт лимит, и объявлять его там -
#                 значит заводить второй источник одного факта;
#   axistype_x/_y - элемент массива оси r5 и оси r6 (только explicit-axis). Своё у каждой
#                 оси: вход зовёт поиск по каждой отдельно и может звать разные - 0x262E0
#                 берёт байтовый 0x26A0C для r5 и словесный 0x26984 для r6, 0x26660 то же
#                 парой 0x26BC4/0x26B84. Элемент снят с клэмпа в delay slot вызова: он
#                 равен (точек - 1) * размер элемента, поэтому у 16 точек байтовая ось
#                 даёт 15, словесная - 30. Тот же клэмп подтверждает и число точек.
# Перепись, которой в реестре нет, - ценз с неизвестной моделью оси; вход с таблицами,
# которого в реестре нет, - обёртка с неизвестной геометрией. И то и другое
# останавливает загрузку, а не размечается наугад.
#
# Обе модели доступа устроены одинаково - слот с указателем на общий движок,
# специализированный вход, jsr от аксессора, - поэтому ценз у них общий, и примитив
# банка проходит по графу обёрткой. Отличается трактовка операндов: у explicit-axis
# r5/r6 суть указатели осей, у implicit-axis ось задана арифметикой и узла :Axis нет.
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
#   - база берётся только из df. Линейный backtrack (bt) остаётся эталоном ворот раздела 6
#     и фактов не даёт: на всех десяти базовых расхождениях каталога JK03A он неверен -
#     поднимает ось вместо базы (0x732a8: базу ставит delay slot `mov r7,r4`, а назад по
#     коду лежит указатель оси), теряет арифметику delay slot (`add 0x8,r4` - пять сайтов
#     банка) либо берёт произвольный элемент селекторного множества.
#   - геометрия карты - геометрия её входа: вход специализирован по форме таблицы, а не
#     параметризован ею. Соглашение осей: r5 -> :AXIS_X, r6 -> :AXIS_Y; регистр-источник
#     сохраняется на ребре (reg), поэтому ориентация уточняется в Stage 4 без потери
#     факта. Ось читается из r6 только у 2D-входов: у 1D-входов ROM-значение в r6 тоже
#     встречается (15 сайтов из 240), но аргументом r6 там не является - это значение
#     регистра, снятое резервом на адресе сайта. Отброшенные значения считаются в отчёте.
#   - kind операнда (pool | slice | const | sp | gbrrel | dyn) идёт на ребро :ACCESSES и в
#     resolver_kinds карты. kind=sp означает, что декомпилятор не свернул базу в одно значение и
#     её снял резерв: r4 там задан ветвлением, и снятая база - один элемент множества
#     (0x64344: шесть таблиц по r5; 0xbe39a: две по r13). Полный набор таких сайтов -
#     вход Stage 6, где ветвление становится :Flag {role:'selector'}.
#   - ось, которую называет только резерв (k5/k6=sp на всех её сайтах), стоит на уровне
#     pattern, а не candidate: резерв - линейная эвристика, и на осях она ошибается так же,
#     как на базах. Доказательство прямое: сайт 0x735ac объявляет осью 0x8000, где лежит
#     стёртая флешь (сплошь 0xFFFF). Свёрнутый сайт (любой kind, кроме sp) поднимает ось до
#     candidate. Полный набор осей-ветвлений разбирает Stage 6 вместе с базами.
# Уровень слоя переписи - candidate (раздел 5): резолвер дал операнды, семантика не
# прослежена. Выше его поднимает только трейс, и приходит он ручным слоем.
#
# Запуск: uv run --no-project --with neo4j python tools/memgraph/load_maps.py \
#           <export_dir> <rom_label> [<registry.csv>] [<findings.csv>] [<axes.csv>]
# По умолчанию export_dir = ~/tools/ghidra-projects/export-JK03A, rom = JK03A,
# реестр = defs/<rom>.interp.csv, ручные слои = defs/<rom>.findings.csv и axes.csv.
import csv
import glob
import os
import re
import sys
from neo4j import GraphDatabase

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import rom as romkit          # noqa: E402 - пакет соседний, не установленный

BOLT = "bolt://localhost:7687"

# Границы ROM: ниже ROM_LO лежат векторы прерываний, а снятые из r6/r7 малые значения -
# runtime-скаляры (индекс, маска), не базы. ROM_HI - размер образа.
ROM_LO = 0x1000
ROM_HI = 0x180000

FAMILIES = ("explicit", "implicit")           # модели доступа, разобранные цензом
ROLES = ("table", "threshold", "dead")        # роль базы в калибровке
LEVELS = ("pattern", "candidate", "code", "silicon")   # лестница уверенности раздела 5
AXIS_KINDS = ("rpm", "load", "temp", "raw")   # семантика оси, она же ключ матча Stage 5
FINDING_FIELDS = [
    "addr", "family", "width", "height", "storagetype", "accessor",
    "confidence", "evidence", "role", "semantics", "units", "scale_expr",
    "to_byte", "scale_conf", "scale_evidence", "note",
]
AXIS_FIELDS = [
    "addr", "kind", "units", "scale_expr", "to_byte", "scale_conf",
    "scale_evidence", "note",
]

# Словарь выражения шкалы: константы, x и арифметика. Шире не нужно - RomRaider читает
# то же выражение, а всё, что не сводится к нему, шкалой карты не является.
SCALE_CHARS = re.compile(r"^[0-9x+\-*/(). ]+$")

DEFS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "defs")


def scale_roundtrip(expr, to_byte):
    """Расхождение пары выражений либо None, если она сходится.

    Обратное выражение объявлено, а не выведено: символьной алгебры в загрузчике нет, а
    угадывать обратное к 1881.6/x он не должен. Зато пара проверяется численно -
    подстановка x -> scale_expr -> to_byte обязана вернуть x, и это ловит расхождение
    ровно там, где оно возникает: при правке одного выражения без второго.
    """
    for v in (1, 7, 64, 100, 255):
        try:
            y = eval(expr, {"__builtins__": {}}, {"x": v})
            back = eval(to_byte, {"__builtins__": {}}, {"x": y})
        except ZeroDivisionError:
            continue
        if abs(back - v) > 1e-6 * max(1.0, abs(v)):
            return f"x={v}: {expr} = {y}, обратно {to_byte} = {back}"
    return None


def check_scale(path, who, r, conf_col):
    """Ценз шкалы: единицы, прямое и обратное выражение, уровень утверждения.

    Тождество (x) единиц не утверждает - это отказ от утверждения, а не факт уровня
    candidate, поэтому уровня у него нет. Непустая шкала без уровня, наоборот, выдала бы
    множитель за данность.
    """
    units, expr, tb, conf = r["units"], r["scale_expr"], r["to_byte"], r[conf_col]
    if not expr:
        extra = [c for c in ("units", "to_byte", conf_col) if r[c]]
        if extra:
            sys.exit(f"{path}: {who} - {', '.join(extra)} без scale_expr")
        return
    if not (units and tb):
        sys.exit(f"{path}: {who} - шкала без единиц либо без обратного выражения")
    for e in (expr, tb):
        if not SCALE_CHARS.match(e):
            sys.exit(f"{path}: {who} - выражение {e!r} вне словаря шкалы")
    bad = scale_roundtrip(expr, tb)
    if bad:
        sys.exit(f"{path}: {who} - to_byte не обратно scale_expr ({bad})")
    if expr.strip() == "x":
        if conf:
            sys.exit(f"{path}: {who} - тождество x единиц не утверждает, уровню места нет")
    elif conf not in LEVELS:
        sys.exit(f"{path}: {who} - уровень шкалы {conf!r} вне лестницы раздела 5")


def read_registry(path):
    """Реестр входов интерполяции: строка = вход со своей геометрией."""
    if not os.path.exists(path):
        sys.exit(f"нет реестра входов интерполяции {path}")
    with open(path, newline="") as f:
        reg = list(csv.DictReader(f))
    seen = set()
    for e in reg:
        w = e["wrapper"] or "?"
        if e["family"] not in FAMILIES:
            sys.exit(f"{path}: вход {w} объявлен семейством {e['family']!r}")
        if not (e["kernel"] and e["wrapper"] and e["width"]):
            sys.exit(f"{path}: вход {w} без ядра, адреса или числа точек")
        if e["wrapper"] in seen:
            sys.exit(f"{path}: вход {w} объявлен дважды")
        seen.add(e["wrapper"])
        if e["family"] == "implicit":
            if not e["step"]:
                sys.exit(f"{path}: implicit-вход {w} без шага оси")
            if e["height"]:
                sys.exit(f"{path}: implicit-вход {w}: у примитива банка вход один")
            if e["storagetype"]:
                sys.exit(f"{path}: implicit-вход {w}: элемент там задаёт лимит")
            if e["axistype_x"] or e["axistype_y"]:
                sys.exit(f"{path}: implicit-вход {w}: массива оси нет, элемента у неё нет")
        else:
            if e["step"]:
                sys.exit(f"{path}: explicit-вход {w}: ось - массив, шага у неё нет")
            if not e["storagetype"]:
                sys.exit(f"{path}: explicit-вход {w} без элемента: у 1D его читает сам "
                         f"вход, у 2D - его finisher")
            if not e["axistype_x"]:
                sys.exit(f"{path}: explicit-вход {w} без элемента оси r5")
            # Ось r6 есть ровно у 2D-входа: у 1D второго поиска в коде нет.
            if bool(e["axistype_y"]) != bool(e["height"]):
                sys.exit(f"{path}: explicit-вход {w}: элемент оси r6 объявлен "
                         f"{'без' if e['axistype_y'] else 'не'} второй оси")
    return reg


def census_path(outdir, kernel):
    """Имя файла переписи: резолвер пишет ядро без ведущих нулей."""
    return os.path.join(outdir, "accessors.%x.csv" % int(kernel, 16))


def read_censuses(outdir, reg, registry):
    """Переписи объявленных ядер; строка несёт геометрию своего входа.

    Вход лежит в переписи каждого ядра, чей слот он держит: 0x26474 держит и kernel
    0x26944, и finisher 0x26740, поэтому одни и те же 47 его сайтов есть в обеих
    переписях. Строка берётся по паре (ядро, вход) из реестра - счёт по одному лишь
    адресу входа дал бы их дважды.
    """
    declared = {(e["kernel"], e["wrapper"]): e for e in reg}
    known = {e["wrapper"] for e in reg}
    rows, taken, seen, unknown = [], set(), set(), {}
    for kernel in dict.fromkeys(e["kernel"] for e in reg):
        p = census_path(outdir, kernel)
        if not os.path.exists(p):
            sys.exit(f"ядро {kernel} объявлено, переписи {os.path.basename(p)} нет")
        taken.add(os.path.realpath(p))
        with open(p, newline="") as f:
            for r in csv.DictReader(f):
                e = declared.get((kernel, r["wrapper"]))
                if e is None:
                    # Вход, не читающий таблиц, - внутренний узел интерполяции, а не
                    # обёртка: у ядра 0x26740 таких пять (2D-finisher 0x26770 и четыре
                    # внутренних входа). Вход с базой в ПЗУ - обёртка, и её геометрия
                    # обязана быть объявлена.
                    if r["wrapper"] not in known and rom_addr(r["df_r4"]):
                        unknown.setdefault(r["wrapper"], kernel)
                    continue
                for c in ("family", "width", "height", "step", "storagetype",
                          "axistype_x", "axistype_y"):
                    r[c] = e[c]
                rows.append(r)
                seen.add((kernel, r["wrapper"]))
    if unknown:
        sys.exit("перепись нашла таблицы через необъявленный вход: "
                 + ", ".join(f"{w} (ядро {k})" for w, k in sorted(unknown.items()))
                 + f" - геометрия неизвестна, объявить в {os.path.basename(registry)}")
    idle = sorted(set(declared) - seen)
    if idle:
        sys.exit("вход объявлен, а сайтов у него нет: "
                 + ", ".join(f"{w} (ядро {k})" for k, w in idle))
    extra = sorted(os.path.basename(p)
                   for p in glob.glob(os.path.join(outdir, "accessors.*.csv"))
                   if os.path.realpath(p) not in taken)
    if extra:
        sys.exit(f"переписи вне реестра: {', '.join(extra)} - модель оси неизвестна, "
                 f"объявить входы в {os.path.basename(registry)}")
    return rows, taken


def rom_addr(v):
    """Адрес в ROM (база карты или оси) либо None, если значение базой быть не может."""
    if not v:
        return None
    return v if ROM_LO <= int(v, 16) < ROM_HI else None


def geometry(e):
    """Геометрия входа из реестра.

    implicit-axis: ось арифметическая - точки 0..(width-1) с шагом step, лимит есть
    последняя точка. Элемент задаёт сам лимит: в точке слияния цепочки (0x26a94) стоит
    SHLR8 R0; TST R0,R0 по лимиту, и лимит >= 256 выбирает word-ветвь; обе ветви
    заканчиваются EXTU, то есть значения беззнаковые. Отдельного флага ширины в коде нет.

    explicit-axis: ось - массив breakpoint'ов, шага у неё нет; число точек снято с кода
    входа (клэмп в delay slot). Элемент у 1D-входа читает сам вход (MOV.B/MOV.W перед
    хвостовым переходом), у 2D - finisher из пула входа, и все пять 2D-finisher'ов читают
    его беззнаковым (EXTU.B либо EXTU.W на обоих операндах интерполяции).
    """
    w = int(e["width"])
    h = int(e["height"]) if e["height"] else None
    g = {"dims": 2 if h else 1, "width": w, "height": h, "step": None, "limit": None,
         "storagetype": e["storagetype"] or None}
    if e["family"] == "implicit":
        g["step"] = int(e["step"])
        g["limit"] = (w - 1) * g["step"]
        g["storagetype"] = "uint16" if g["limit"] >= 256 else "uint8"
    return g


def check_dims(rows, declared):
    """Размерность объявлена геометрией входа; независимый признак - ось в r6.

    Признак разделяет входы explicit-axis JK03A большинством, а не начисто: у 2D ось в
    r6 несут 86 сайтов из 87, у 1D - 15 из 240, и наибольшая доля у 1D-входа - 1 из 7
    (0x26550). Поэтому сверяется большинство: одиночное ROM-значение в r6 у 1D-входа
    аргументом не является.
    """
    total, with_y = {}, {}
    for r in rows:
        if r["family"] != "explicit":
            continue
        w = r["wrapper"]
        total[w] = total.get(w, 0) + 1
        if rom_addr(r["df_r6"]):
            with_y[w] = with_y.get(w, 0) + 1
    bad = [f"{w}: реестр {declared[w]}D, сайты {2 if with_y.get(w, 0) * 2 > n else 1}D "
           f"({with_y.get(w, 0)} из {n} с осью в r6)"
           for w, n in sorted(total.items())
           if (2 if with_y.get(w, 0) * 2 > n else 1) != declared[w]]
    if bad:
        sys.exit("размерность входа расходится с его сайтами: " + "; ".join(bad))


def build(rows):
    """Переписи резолвера -> узлы и рёбра калибровочного слоя."""
    maps, axes, interps, accesses = {}, {}, {}, []
    kernels = {}                                  # вход -> его ядро (ребро :KERNEL)
    dropped = 0                                   # r6-значения у 1D-входов: не оси

    for r in rows:
        kern, w, family = r["kernel"], r["wrapper"], r["family"]
        g = geometry(r)

        interps.setdefault(kern, {"addr": kern, "role": "kernel", "family": None,
                                  "slot": "", "dims": None, "width": None,
                                  "height": None, "step": None, "limit": None,
                                  "storagetype": None})
        interps.setdefault(w, dict(g, addr=w, role="wrapper", family=family,
                                   slot=r["slot"]))
        kernels[w] = kern

        # Ось - объект только у explicit-axis; у банка она арифметическая, и снятые там
        # r5/r6 суть остаточные значения регистров, а не аргументы вызова.
        explicit = family == "explicit"
        ax = rom_addr(r["df_r5"]) if explicit else None
        ay = rom_addr(r["df_r6"]) if explicit and g["dims"] == 2 else None
        if explicit and g["dims"] == 1 and rom_addr(r["df_r6"]):
            dropped += 1

        base = rom_addr(r["df_r4"])
        if not base:
            continue
        # Ось заводится только у карты: на сайте без базы (kind=dyn) снятый указатель -
        # ось неизвестно чего, и узел без ребра был бы осью ни одной таблицы. Значение
        # при этом не теряется - оно остаётся в переписи и вернётся с базой на Stage 6.
        # Длина и элемент оси - не её собственные факты: число точек задаёт клэмп входа,
        # элемент - код ядра. Расхождение между читателями одной оси останавливает
        # загрузку здесь, вместе с прочими расхождениями геометрии.
        for a, n, k, el in ((ax, g["width"], r["k5"], r["axistype_x"]),
                            (ay, g["height"], r["k6"], r["axistype_y"])):
            if a:
                x = axes.setdefault(a, {"addr": a, "confidence": "pattern", "kind": "",
                                        "units": "", "scale_expr": "", "to_byte": "",
                                        "scale_conf": "", "scale_evidence": "", "note": "",
                                        "len": n, "storagetype": el})
                if x["storagetype"] != el:
                    sys.exit(f"ось {a} читается входами с разным элементом: "
                             f"{x['storagetype']} и {el}")
                if x["len"] != n:
                    sys.exit(f"ось {a} читается входами разной длины: {x['len']} и {n}")
                if k != "sp":
                    x["confidence"] = "candidate"
        m = maps.setdefault(base, dict(g, addr=base, family=family,
                                       confidence="candidate", resolver_kinds=[],
                                       evidence="", scale_evidence="",
                                       role="table", semantics="", note="",
                                       units="", scale_expr="", to_byte="",
                                       scale_conf=""))
        # Таблица, читаемая обеими моделями оси либо входами разной формы, - находка, а
        # не разновидность нормы: геометрия у неё тогда задана двумя способами сразу.
        if m["family"] != family:
            sys.exit(f"таблица {base} адресуется семействами {m['family']} и {family}")
        if (m["width"], m["height"], m["storagetype"], m["step"]) != (
                g["width"], g["height"], g["storagetype"], g["step"]):
            sys.exit(f"таблица {base} читается входами разной геометрии: "
                     f"{m['width']}x{m['height']}/{m['storagetype']}/шаг {m['step']} и "
                     f"{g['width']}x{g['height']}/{g['storagetype']}/шаг {g['step']}")
        if r["k4"] not in m["resolver_kinds"]:
            m["resolver_kinds"].append(r["k4"])
        accesses.append({"accessor": r["accessor"], "callsite": r["callsite"],
                         "base": base, "wrapper": w, "kernel": kern, "family": family,
                         "kind": r["k4"], "kind5": r["k5"], "kind6": r["k6"],
                         "verdict": r["verdict"], "r4": r["df_r4"],
                         "r5": r["df_r5"], "r6": r["df_r6"],
                         "axis_x": ax or "", "axis_y": ay or ""})

    for m in maps.values():
        m["resolver_kinds"] = sorted(m["resolver_kinds"])
    return maps, axes, interps, kernels, accesses, dropped


def apply_findings(path, maps, accesses):
    """Ручной слой: что установлено человеком и чего перепись дать не может.

    Строка с непустым family объявляет карту вне моделей доступа: её не читает ни один
    объявленный вход, поэтому резолвер её и не находит (0x8fdc - прямой word-компаратор
    без lookup'а; 0x9eda и 0xa8ea - 2D через 0x26040, где неявны обе оси). Пустой
    family - находка о карте, которую нашёл резолвер.

    В файл идёт только то, чего граф сказать не может. Обёртка, геометрия, оси и
    аксессор карты из переписи - факты графа, и повторить их находкой значит завести
    второй источник одного факта. Уровень поднимает сюда трейс: перепись даёт весь свой
    слой candidate, и выше его двигает только разбор.

    Шкала (units/scale_expr/to_byte) идёт сюда по той же причине: операнд вызова говорит,
    где лежит таблица, но не во что мотор превращает её байт. У шкалы свой уровень: адрес
    и форма 0xB61A сняты кодом, а множитель x-64 взят из каталога A2L, и уровень карты за
    него не отвечает.
    """
    if not os.path.exists(path):
        sys.exit(f"нет ручного слоя {path}")
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FINDING_FIELDS:
            sys.exit(f"{path}: заголовок {reader.fieldnames}, ожидается {FINDING_FIELDS}")
        rows = list(reader)
    declared = 0
    for r in rows:
        a, fam = r["addr"], r["family"]
        if r["confidence"] not in LEVELS:
            sys.exit(f"{path}: {a} - уровень {r['confidence']!r} вне лестницы раздела 5")
        if r["role"] not in ROLES:
            sys.exit(f"{path}: {a} - роль {r['role']!r} вне словаря {ROLES}")
        check_scale(path, a, r, "scale_conf")
        if fam:
            if fam in FAMILIES:
                sys.exit(f"{path}: {a} объявлена семейством {fam!r} - это модель "
                         f"доступа, её карты даёт перепись, а не находка")
            if a in maps:
                sys.exit(f"{path}: {a} объявлена вручную, но её нашёл резолвер через "
                         f"{maps[a]['family']} - объявление устарело, строку убрать")
            if not (r["width"] and r["storagetype"]):
                sys.exit(f"{path}: {a} объявлена без числа точек либо элемента - по её "
                         f"строке карту в образе не прочитать")
            declared += 1
            maps[a] = {"addr": a, "family": fam, "resolver_kinds": ["manual"],
                       "dims": 2 if r["height"] else 1,
                       "width": int(r["width"]) if r["width"] else None,
                       "height": int(r["height"]) if r["height"] else None,
                       "storagetype": r["storagetype"] or None,
                       "step": None, "limit": None}
            maps[a].update(units="", scale_expr="", to_byte="", scale_conf="",
                           evidence="", scale_evidence="")
            if r["accessor"]:
                accesses.append({"accessor": r["accessor"], "callsite": "", "base": a,
                                 "wrapper": "", "kernel": "", "family": fam,
                                 "kind": "manual", "kind5": "manual", "kind6": "manual",
                                 "verdict": "", "r4": "", "r5": "", "r6": "",
                                 "axis_x": "", "axis_y": ""})
        elif a not in maps:
            sys.exit(f"{path}: находка о карте {a}, которой в графе нет - либо адрес "
                     f"неверен, либо строка пережила свою карту")
        else:
            dup = [c for c in ("width", "height", "storagetype", "accessor") if r[c]]
            if dup:
                sys.exit(f"{path}: {a} - {', '.join(dup)} даёт перепись, находке это "
                         f"поле не переопределять")
        maps[a].update(confidence=r["confidence"], evidence=r["evidence"],
                       role=r["role"], semantics=r["semantics"], note=r["note"],
                       units=r["units"], scale_expr=r["scale_expr"],
                       to_byte=r["to_byte"], scale_conf=r["scale_conf"],
                       scale_evidence=r["scale_evidence"])
    return len(rows), declared


def apply_axis_facts(path, axes):
    """Ручной слой осей: семантика оси и её единицы.

    Ось как объект даёт перепись (указатель в r5/r6), её элемент - ядро. Чем ось является
    и в чём измеряется, не говорит ни то ни другое: это трейс её потребителя. Отсюда
    отдельный файл, а не колонки в слое карт: ось общая у нескольких карт (0x11B6B несут
    все три карты зажигания), и объявление на карту размножило бы один факт по строкам.
    """
    if not os.path.exists(path):
        sys.exit(f"нет осевого слоя {path}")
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != AXIS_FIELDS:
            sys.exit(f"{path}: заголовок {reader.fieldnames}, ожидается {AXIS_FIELDS}")
        rows = list(reader)
    seen = set()
    for r in rows:
        a = r["addr"]
        if a in seen:
            sys.exit(f"{path}: ось {a} объявлена дважды")
        seen.add(a)
        if a not in axes:
            sys.exit(f"{path}: находка об оси {a}, которой в графе нет - либо адрес "
                     f"неверен, либо строка пережила свою ось")
        if r["kind"] not in AXIS_KINDS:
            sys.exit(f"{path}: ось {a} - kind {r['kind']!r} вне словаря {AXIS_KINDS}")
        check_scale(path, f"ось {a}", r, "scale_conf")
        axes[a].update(kind=r["kind"], units=r["units"], scale_expr=r["scale_expr"],
                       to_byte=r["to_byte"], scale_conf=r["scale_conf"],
                       scale_evidence=r["scale_evidence"], note=r["note"])
    return len(rows)


def characterize(img, maps, axes):
    """Stage 4: измерить то, что образ говорит о слое сам.

    Идёт тем же прогоном, что создаёт узлы, по той же причине, что и ручной слой:
    измерение живёт на том же узле, что и факт переписи, и пересоздание узла унесло бы
    его с собой. Второго источника факта здесь нет - источник и есть образ, а перепись
    говорит лишь, по какому адресу и какой формой его читать.

    Ось несёт свои точки целиком: она коротка, и она ими и является - общие оси сходятся
    сравнением списков, а лесенка оборотов видна в графе без обращения к образу. Карта
    несёт диапазон и хеш: 256 ячеек в узле - это содержимое образа, переписанное в граф,
    а одинаковые карты находит хеш.

    Промах чтения останавливает загрузку: карта, которой в образе нет, - не карта, а
    неверный адрес либо неверная форма, и измерять там нечего. Ценз переписи держит базы
    в 0x1000..0x180000 - границе самого крупного дампа семейства, а не этого; настоящую
    границу знает только образ.
    """
    for a, m in sorted(maps.items()):
        try:
            rows = img.table(a, m["width"], m["height"], m["storagetype"])
        except ValueError as e:
            sys.exit(f"карта {a} ({m['width']}x{m['height']} {m['storagetype']}): {e}")
        m.update(romkit.measure([v for r in rows for v in r]))
    for a, x in sorted(axes.items()):
        try:
            vals = img.values(a, x["len"], x["storagetype"])
        except ValueError as e:
            sys.exit(f"ось {a} ({x['len']} x {x['storagetype']}): {e}")
        x.update(values=vals, monotonic=romkit.monotone(vals))


def report(rows, maps, axes, interps, kernels, accesses, dropped, taken, findings, naxes):
    nfind, nmanual = findings
    d2 = sum(1 for i in interps.values() if i["dims"] == 2)
    callsites = {row["callsite"] for row in rows}
    projected = {
        (row["accessor"], row["callsite"], row["base"])
        for row in accesses
    }
    print(f"переписи: {', '.join(sorted(os.path.basename(p) for p in taken))}")
    print(f"CSV: {len(rows)} строк для {len(callsites)} callsite, "
          f"{len(set(kernels.values()))} ядер, {len(kernels)} входов")
    print(f"Слой: {len(maps)} карт, {len(axes)} осей, {len(interps)} узлов интерполяции "
          f"({d2} входов 2D), {len(accesses)} строк доступов / "
          f"{len(projected)} уникальных")
    if dropped:
        print(f"  r6 у 1D-входов осью не считан: {dropped} значений (не аргумент вызова)")

    # Непересечение цензов: общая таблица у двух семейств доступа - находка, а не
    # разновидность нормы. Счёт карт на вход даёт таблица в конце отчёта.
    per_table, per_family = {}, {}
    for a in accesses:
        if a["kernel"]:
            per_table.setdefault(a["base"], set()).add(a["kernel"])
    for m in maps.values():
        per_family.setdefault(m["family"], set()).add(m["addr"])
    for f in sorted(per_family):
        print(f"  семейство {f}: {len(per_family[f])} карт")
    shared = {b: ks for b, ks in per_table.items() if len(ks) > 1}
    for b, ks in sorted(shared.items()):
        print(f"  ВНИМАНИЕ: таблица {b} адресуется цензами {sorted(ks)}")
    if not shared:
        print(f"  цензы по таблицам не пересекаются ({len(per_table)} баз)")

    print(f"  ручной слой: {nfind} находок, из них {nmanual} объявляют карту вне "
          f"моделей доступа; {naxes} осей размечено")
    scaled = sum(1 for m in maps.values() if m["scale_expr"])
    named = sum(1 for m in maps.values() if m["semantics"])
    both = sum(1 for m in maps.values() if m["semantics"] and m["scale_expr"])
    print(f"  читаемо (семантика + шкала): {both} карт; семантика у {named}, "
          f"шкала у {scaled}")
    lvl = {}
    for m in maps.values():
        lvl[m["confidence"]] = lvl.get(m["confidence"], 0) + 1
    print("  уровни: " + ", ".join(f"{k}={lvl[k]}" for k in LEVELS if k in lvl))
    role = {}
    for m in maps.values():
        role[m["role"]] = role.get(m["role"], 0) + 1
    print("  роли: " + ", ".join(f"{k}={role[k]}" for k in ROLES if k in role))

    # Сайты, где операнд не свёрнут в одно значение: снят резервом по одному пути либо
    # не снят вовсе. Вход Stage 6 - там операнд выбирает ветвление.
    sel = [a for a in accesses if a["kind"] == "sp"]
    sel_projected = {
        (a["accessor"], a["callsite"], a["base"])
        for a in sel
    }
    print(f"  база не свёрнута декомпилятором (kind=sp): {len(sel)} строк / "
          f"{len(sel_projected)} уникальных доступов - вход Stage 6")
    axsel = [a for a in accesses if "sp" in (a["kind5"], a["kind6"])]
    axsel_sites = {a["callsite"] for a in axsel}
    weak = [x for x in axes.values() if x["confidence"] == "pattern"]
    print(f"  ось не свёрнута декомпилятором (kind5/kind6=sp): "
          f"{len(axsel)} доступов на {len(axsel_sites)} callsite; "
          f"{len(weak)} осей стоят только на резерве (уровень pattern) - туда же")

    # Stage 4 - что образ говорит о слое сам. Дедуп идёт по содержимому вместе с формой:
    # одинаковые байты разной формы - разные таблицы, а не одна.
    print(f"  измерено по образу: {len(maps)} карт, {len(axes)} осей")
    seen_ax = {tuple(x["values"]) for x in axes.values()}
    seen_m = {(m["values_hash"], m["width"], m["height"], m["storagetype"])
              for m in maps.values()}
    print(f"    различимы содержимым: {len(seen_ax)} осей из {len(axes)} "
          f"(общая ось у нескольких карт - норма), {len(seen_m)} карт из {len(maps)}")

    # Возрастание оси - не догадка о смысле, а условие ядра: бинарный поиск от старшей
    # точки вниз читает только возрастающий массив, и невозрастающая ось осью не работает.
    bad = sorted(x["addr"] for x in axes.values() if not x["monotonic"])
    if bad:
        print(f"    ВНИМАНИЕ: массив не возрастает, бинарным поиском ядра не читается: "
              f"{', '.join(bad)}")
    blank_ax = [x["addr"] for x in axes.values()
                if romkit.erased(x["values"], x["storagetype"])]
    blank_m = [m["addr"] for m in maps.values()
               if m["vmin"] == m["vmax"] == romkit.ERASED[m["storagetype"]]]
    if blank_ax or blank_m:
        print(f"    сплошь 0xFF (незапрограммированная флешь либо насыщенный предел, "
              f"различает трейс): осей {len(blank_ax)}, карт {len(blank_m)}")


def main():
    default_dir = os.path.expanduser("~/tools/ghidra-projects/export-JK03A")
    outdir = sys.argv[1] if len(sys.argv) > 1 else default_dir
    rom = sys.argv[2] if len(sys.argv) > 2 else "JK03A"
    registry = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
        DEFS, f"{rom}.interp.csv")
    findings = sys.argv[4] if len(sys.argv) > 4 else os.path.join(
        DEFS, f"{rom}.findings.csv")
    axfile = sys.argv[5] if len(sys.argv) > 5 else os.path.join(DEFS, f"{rom}.axes.csv")

    reg = read_registry(registry)
    rows, taken = read_censuses(outdir, reg, registry)
    check_dims(rows, {e["wrapper"]: 2 if e["height"] else 1 for e in reg})
    maps, axes, interps, kernels, accesses, dropped = build(rows)
    found = apply_findings(findings, maps, accesses)
    naxes = apply_axis_facts(axfile, axes)
    try:
        img = romkit.load(rom)
    except ValueError as e:
        sys.exit(str(e))
    characterize(img, maps, axes)
    print(f"rom={rom}; реестр: {os.path.relpath(registry)} ({len(reg)} входов); "
          f"ручной слой: {os.path.relpath(findings)}, {os.path.relpath(axfile)}")
    print(f"образ: {os.path.relpath(img.path)} ({len(img)} B, sha256 сверен)")
    report(rows, maps, axes, interps, kernels, accesses, dropped, taken, found, naxes)

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
            SET i.role = r.role, i.family = r.family, i.slot = r.slot, i.dims = r.dims,
                i.width = r.width, i.height = r.height, i.step = r.step,
                i.limit = r.limit, i.storagetype = r.storagetype
            """,
            rows=list(interps.values()),
            rom=rom,
        )
        s.run(
            """
            UNWIND $rows AS r
            MERGE (m:Map {rom:$rom, addr:r.addr})
            SET m.dims = toInteger(r.dims), m.family = r.family, m.width = r.width,
                m.height = r.height, m.storagetype = r.storagetype,
                m.confidence = r.confidence, m.resolver_kinds = r.resolver_kinds,
                m.evidence = r.evidence, m.scale_evidence = r.scale_evidence,
                m.role = r.role,
                m.semantics = r.semantics, m.note = r.note, m.units = r.units,
                m.scale_expr = r.scale_expr, m.to_byte = r.to_byte,
                m.scale_conf = r.scale_conf, m.vmin = r.vmin, m.vmax = r.vmax,
                m.values_hash = r.values_hash
            """,
            rows=list(maps.values()),
            rom=rom,
        )
        s.run(
            """
            UNWIND $rows AS r
            MERGE (x:Axis {rom:$rom, addr:r.addr})
            SET x.confidence = r.confidence, x.storagetype = r.storagetype,
                x.len = r.len, x.kind = r.kind, x.units = r.units,
                x.scale_expr = r.scale_expr, x.to_byte = r.to_byte,
                x.scale_conf = r.scale_conf, x.scale_evidence = r.scale_evidence,
                x.note = r.note, x.values = r.values,
                x.monotonic = r.monotonic
            """,
            rows=list(axes.values()),
            rom=rom,
        )
        s.run(
            """
            UNWIND $rows AS r
            MATCH (w:Interp {rom:$rom, addr:r.wrapper}), (k:Interp {rom:$rom, addr:r.kernel})
            MERGE (w)-[:KERNEL]->(k)
            """,
            rows=[{"wrapper": w, "kernel": k} for w, k in sorted(kernels.items())],
            rom=rom,
        )
        s.run(
            """
            UNWIND $rows AS r
            MERGE (a:Func {rom:$rom, addr:r.accessor})
            WITH a, r
            MATCH (m:Map {rom:$rom, addr:r.base})
            MERGE (a)-[x:ACCESSES {callsite:r.callsite, base:r.base}]->(m)
            SET x.r4 = r.r4, x.r5 = r.r5, x.r6 = r.r6, x.kind = r.kind,
                x.kind5 = r.kind5, x.kind6 = r.kind6, x.verdict = r.verdict
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
            rows=[r for r in accesses if r["wrapper"]],
            rom=rom,
        )
        for reg_name, edge, key in (("r5", "AXIS_X", "axis_x"), ("r6", "AXIS_Y", "axis_y")):
            s.run(
                f"""
                UNWIND $rows AS r
                MATCH (m:Map {{rom:$rom, addr:r.base}}), (x:Axis {{rom:$rom, addr:r.{key}}})
                MERGE (m)-[e:{edge}]->(x)
                SET e.reg = '{reg_name}'
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
        print(f"Memgraph: {counts['maps']} :Map, {counts['axes']} :Axis, "
              f"{counts['acc']} :ACCESSES, {counts['via']} :VIA")
        if orphan:
            print(f"ВНИМАНИЕ: {orphan} аксессоров нет в :Func - граф собран до разметки "
                  f"Stage 0; переэкспортировать (RecoverFuncs.java + ExportGraph.java)")

        print("Карты по входам интерполяции (каталог Stage 2):")
        rows_out = s.run(
            """
            MATCH (m:Map {rom:$rom})-[:VIA]->(w:Interp {rom:$rom})
            RETURN w.addr AS wrapper, w.family AS family, w.width AS width,
                   w.height AS height, count(DISTINCT m) AS maps
            ORDER BY family, maps DESC
            """,
            rom=rom,
        )
        for r in rows_out:
            shape = f"{r['width']}x{r['height']}" if r["height"] else f"1D-{r['width']}"
            print(f"  {r['family']:<8} вход {r['wrapper']}  {shape:<7}  "
                  f"карт {r['maps']:>3}")

    driver.close()


if __name__ == "__main__":
    main()
