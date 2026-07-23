#!/usr/bin/env python3
# Образ ROM: реестр дампов, чтение калибровочных массивов и их измерение (Stage 4,
# раздел 7 tools/map-flag-pipeline.md). Библиотека, не скрипт: её зовут load_maps.py
# (характеризация слоя тем же прогоном, что создаёт узлы) и show.py/ptrscan.py.
#
# Граница инструмента: он МЕРИТ, но не ЗАКЛЮЧАЕТ. Диапазон, монотонность и содержимое -
# свойства байтов образа, и читаются они одинаково у карты любой семантики. Чем ось
# является, в чём измеряется и что означает карта - выводы о коде, и приходят они трейсом
# через ручной слой (defs/<rom>.findings.csv, <rom>.axes.csv). Вывод смысла из формы
# данных - ровно то, чем pattern-scan уже дважды ошибся (P6), и здесь его нет намеренно.
#
# Монотонность под это правило не подпадает: возрастающий массив - требование самого ядра
# (обратный линейный проход от старшей точки вниз до первой <= текущего значения), а не
# догадка о смысле. Массив, который ему не отвечает, осью не работает, чем бы он ни был назван.
import csv
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGES = os.path.join(HERE, "..", "..", "rom-images")
REGISTRY = os.path.join(IMAGES, "roms.csv")

# Элемент калибровки: размер в байтах. Беззнаковы оба - все пять 2D-finisher'ов читают
# EXTU.B либо EXTU.W на обоих операндах интерполяции, инструкции EXTS в области
# 0x26740..0x26BC4 нет ни одной (defs/JK03A.notes.md, "Кодировка элемента 2D-карт").
# Знаковый элемент объявляется здесь вместе с кодом, который так читает.
ELEM = {"uint8": 1, "uint16": 2}

# Стёртая флешь: незапрограммированная ячейка читается как все единицы.
ERASED = {"uint8": 0xFF, "uint16": 0xFFFF}


def addr_int(a):
    """Адрес графа (hex-строка без 0x) либо число."""
    return a if isinstance(a, int) else int(str(a), 16)


class Image:
    """Байты одного дампа. Файл-офсет равен адресу: образ грузится с базой 0x0."""

    def __init__(self, rom, path, data):
        self.rom, self.path, self.data = rom, path, data

    def __len__(self):
        return len(self.data)

    def values(self, addr, n, storagetype):
        """n элементов подряд, big-endian, беззнаковые."""
        if storagetype not in ELEM:
            raise ValueError(f"элемент {storagetype!r} не объявлен: {tuple(ELEM)}")
        size, addr = ELEM[storagetype], addr_int(addr)
        end = addr + n * size
        if addr < 0 or end > len(self.data):
            raise ValueError(f"{self.rom}: {addr:#x} + {n} x {size} B выходит за образ "
                             f"({len(self.data):#x} B)")
        return [int.from_bytes(self.data[i:i + size], "big")
                for i in range(addr, end, size)]

    def table(self, addr, width, height, storagetype):
        """Карта построчно: строка - точка оси r5 (:AXIS_X), столбец - точка оси r6.

        Геометрия - finisher'а: cell = table + idxY + width*idxX, где idxX - индекс по
        оси r5, а шаг строки передаёт ему сам вход (журнал: 0x10 у 16x16 uint8, 8 у 8x8
        через 0x26040). Шаг строки есть её длина, то есть число столбцов - длина оси r6.
        У всех 2D-входов JK03A оси равной длины (4x4, 8x8, 16x16), поэтому там это число
        совпадает и с числом строк; неквадратный вход прочтётся по формуле, а не по
        совпадению.
        """
        if not height:
            return [self.values(addr, width, storagetype)]
        flat = self.values(addr, width * height, storagetype)
        return [flat[i * height:(i + 1) * height] for i in range(width)]

    def scan(self, lo, hi):
        """Слова образа, попадающие значением в [lo, hi]: кто указывает на диапазон.

        Ищет обе формы константы. mov.l читает 32-битное слово по 4-байтовой границе -
        это указатель пула. mov.w читает 16-битное по 2-байтовой, и адрес калибровки в
        него влезает (0xB33A, 0x8FDC): такую константу линейный backtrack эталона читал
        32-битной и ошибался на пяти сайтах каталога, поэтому форма здесь отдельная.

        Младшая половина найденного 32-битного слова несёт то же значение, когда оно
        влезает в 16 бит, и отдельным попаданием не считается: это одна константа, а не
        две.
        """
        out, halves = [], set()
        for off in range(0, len(self.data) - 3, 4):
            v = int.from_bytes(self.data[off:off + 4], "big")
            if lo <= v <= hi:
                out.append({"at": off, "value": v, "kind": "mov.l"})
                if v <= 0xFFFF:
                    halves.add(off + 2)
        if lo <= 0xFFFF:
            for off in range(0, len(self.data) - 1, 2):
                v = int.from_bytes(self.data[off:off + 2], "big")
                if lo <= v <= min(hi, 0xFFFF) and off not in halves:
                    out.append({"at": off, "value": v, "kind": "mov.w"})
        return sorted(out, key=lambda r: r["at"])


def measure(values):
    """Диапазон и содержимое массива - то, что образ говорит о нём сам.

    Хеш нужен там, где самих значений в графе нет: карта до 256 ячеек, её содержимое
    остаётся в образе, и одинаковые карты ищутся по хешу. У оси значения лежат в узле
    целиком, и одинаковые оси сходятся сравнением списков - хеш там был бы вторым видом
    одного факта.
    """
    return {
        "vmin": min(values),
        "vmax": max(values),
        "values_hash": hashlib.sha256(",".join(map(str, values)).encode()).hexdigest()[:16],
    }


def erased(values, storagetype):
    """Массив из одних единичных битов: стёртая флешь, а не данные.

    Свойство носителя, а не вывод о смысле: стирание NOR-флеши идёт в единицы, и
    сплошной 0xFF в объявленном массиве означает, что массива там нет.
    """
    return all(v == ERASED[storagetype] for v in values)


def monotone(values):
    """Возрастает ли массив (нестрого).

    Ядро проходит линейно от старшей точки вниз до первого break-point <= текущего
    значения - это работает на возрастающем массиве и ни на каком другом. Массив, который
    правилу не отвечает, осью не работает, чем бы его ни назвал резолвер.
    """
    return all(a <= b for a, b in zip(values, values[1:]))


def registry(path=REGISTRY):
    """Реестр образов: строка = файл дампа, rom - его метка в графе (пусто - метки нет).

    Реестр машинный, идентификация дампа прозой - в rom-images/README.md (происхождение,
    part #, уверенность). Sha256 объявлен здесь: опознание дампа - условие прогона, а не
    справка для человека.
    """
    if not os.path.exists(path):
        raise ValueError(f"нет реестра образов {path}")
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    seen = {}
    for r in rows:
        r["path"] = os.path.join(IMAGES, r["path"])
        if not r["sha256"]:
            raise ValueError(f"{path}: {r['path']} без sha256 - дамп опознаётся по нему")
        if r["rom"]:
            if r["rom"] in seen:
                raise ValueError(f"{path}: метка {r['rom']} на двух образах")
            seen[r["rom"]] = r
    return rows


def load(rom, path=REGISTRY):
    """Образ по метке графа, сверенный по sha256.

    Сверка не формальность: перепись снята с проекта Ghidra по одному файлу, а измерения
    идут вторым обращением к диску. Подмена дала бы не отказ, а 227 осей правдоподобных
    чисел не из того дампа - брак, который в графе ничем не отличается от факта.
    """
    row = next((r for r in registry(path) if r["rom"] == rom), None)
    if row is None:
        raise ValueError(f"{path}: образа с меткой {rom} в реестре нет")
    if not os.path.exists(row["path"]):
        raise ValueError(f"{row['path']}: файла нет (реестр объявляет его образом {rom})")
    with open(row["path"], "rb") as f:
        data = f.read()
    got = hashlib.sha256(data).hexdigest()
    if got != row["sha256"]:
        raise ValueError(f"{row['path']}: sha256 {got}, реестр объявляет "
                         f"{row['sha256']} - это другой дамп")
    return Image(rom, row["path"], data)
