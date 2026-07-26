#!/usr/bin/env python3
"""Единый источник аннотаций для exact-code ROM без копирования defs/<rom>.*."""

from dataclasses import dataclass
import csv
import hashlib
from pathlib import Path
import re
import tomllib


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "defs" / "rom-inheritance.toml"
IMAGE_REGISTRY = ROOT / "rom-images" / "roms.csv"
ROM_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
KINDS = frozenset({"exact-code"})
FIELDS = frozenset({
    "source", "kind", "target_sha256", "source_sha256", "ranges", "evidence",
})
PROSE_FIELDS = {
    "Func": frozenset({"semantics", "contract", "note"}),
    "Reg": frozenset({"semantics", "units", "note"}),
    "Map": frozenset({"semantics", "units", "note"}),
    "Axis": frozenset({"kind", "units", "note"}),
}


class SourceModelError(ValueError):
    pass


@dataclass(frozen=True)
class SourceModel:
    target: str
    source: str
    kind: str
    target_sha256: str = ""
    source_sha256: str = ""
    ranges: tuple = ()
    evidence: str = ""

    @property
    def inherited(self):
        return self.target != self.source


def _read_registry(path):
    path = Path(path)
    try:
        with path.open("rb") as fh:
            document = tomllib.load(fh)
    except OSError as error:
        raise SourceModelError(f"нет реестра наследования ROM {path}") from error
    unknown_top = sorted(set(document) - {"inherit"})
    if unknown_top:
        raise SourceModelError(
            f"{path}: неизвестные верхнеуровневые секции {unknown_top}"
        )
    entries = document.get("inherit", {})
    if not isinstance(entries, dict):
        raise SourceModelError(f"{path}: inherit должен быть TOML-таблицей")
    return path, entries


def read_registry(path=DEFAULT_REGISTRY):
    path, raw = _read_registry(path)
    entries = {}
    for target, row in raw.items():
        if not ROM_RE.fullmatch(target) or not isinstance(row, dict):
            raise SourceModelError(f"{path}: некорректная запись inherit.{target}")
        unknown = sorted(set(row) - FIELDS)
        if unknown:
            raise SourceModelError(
                f"{path}: inherit.{target} содержит неизвестные поля {unknown}"
            )
        missing = sorted(FIELDS - set(row))
        if missing:
            raise SourceModelError(
                f"{path}: inherit.{target} без полей {missing}"
            )
        source = row["source"]
        kind = row["kind"]
        if not isinstance(source, str) or not ROM_RE.fullmatch(source):
            raise SourceModelError(
                f"{path}: inherit.{target}.source не является меткой ROM"
            )
        if source == target:
            raise SourceModelError(
                f"{path}: inherit.{target} ссылается сам на себя"
            )
        if kind not in KINDS:
            raise SourceModelError(
                f"{path}: inherit.{target}.kind={kind!r} вне {sorted(KINDS)}"
            )
        for field in ("target_sha256", "source_sha256"):
            if not isinstance(row[field], str) or not SHA256_RE.fullmatch(row[field]):
                raise SourceModelError(
                    f"{path}: inherit.{target}.{field} не является SHA-256"
                )
        ranges = row["ranges"]
        if not isinstance(ranges, list) or not ranges:
            raise SourceModelError(
                f"{path}: inherit.{target}.ranges должен быть непустым массивом"
            )
        parsed_ranges = []
        for value in ranges:
            if not isinstance(value, str) or not re.fullmatch(
                r"0x[0-9a-fA-F]+:0x[0-9a-fA-F]+", value
            ):
                raise SourceModelError(
                    f"{path}: inherit.{target}.ranges содержит {value!r}"
                )
            start_text, end_text = value.split(":", 1)
            start, end = int(start_text, 16), int(end_text, 16)
            if start >= end:
                raise SourceModelError(
                    f"{path}: inherit.{target}.ranges содержит пустой диапазон {value}"
                )
            parsed_ranges.append((start, end, value))
        ordered = sorted(parsed_ranges)
        if parsed_ranges != ordered or any(
            left[1] > right[0] for left, right in zip(ordered, ordered[1:])
        ):
            raise SourceModelError(
                f"{path}: inherit.{target}.ranges не упорядочены или пересекаются"
            )
        if not isinstance(row["evidence"], str) or not row["evidence"].strip():
            raise SourceModelError(
                f"{path}: inherit.{target}.evidence пуст"
            )
        entries[target] = SourceModel(
            target=target,
            source=source,
            kind=kind,
            target_sha256=row["target_sha256"],
            source_sha256=row["source_sha256"],
            ranges=tuple(ranges),
            evidence=row["evidence"],
        )

    chained = sorted(
        target for target, model in entries.items() if model.source in entries
    )
    if chained:
        raise SourceModelError(
            f"{path}: цепочки наследования запрещены, цели {chained}"
        )
    return entries


def resolve(rom, path=DEFAULT_REGISTRY):
    if not isinstance(rom, str) or not ROM_RE.fullmatch(rom):
        raise SourceModelError(f"некорректная метка ROM {rom!r}")
    return read_registry(path).get(
        rom,
        SourceModel(target=rom, source=rom, kind="canonical"),
    )


def definition_paths(model):
    defs = ROOT / "defs"
    return {
        "Func": defs / f"{model.source}.funcs.csv",
        "Reg": defs / f"{model.source}.vars.csv",
        "Map": defs / f"{model.source}.findings.csv",
        "Axis": defs / f"{model.source}.axes.csv",
        "Interp": defs / f"{model.source}.interp.csv",
    }


def materialize_rows(model, label, rows):
    """Подставить целевую метку только в человекочитаемые поля общего источника."""
    if not model.inherited:
        return rows
    fields = PROSE_FIELDS.get(label, ())
    return [
        {
            key: (
                value.replace(model.source, model.target)
                if key in fields and isinstance(value, str)
                else value
            )
            for key, value in row.items()
        }
        for row in rows
    ]


def verify_image_binding(model, path=IMAGE_REGISTRY):
    """Привязать exact-code связь к конкретным образам, а не только к меткам."""
    if not model.inherited:
        return
    path = Path(path)
    try:
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    except OSError as error:
        raise SourceModelError(f"нет реестра образов {path}") from error
    by_rom = {}
    for row in rows:
        rom = row.get("rom", "")
        if not rom:
            continue
        if rom in by_rom:
            raise SourceModelError(f"{path}: ROM {rom} объявлен несколько раз")
        by_rom[rom] = row
    expected = {
        model.target: model.target_sha256,
        model.source: model.source_sha256,
    }
    bad = [
        f"{rom}: registry={by_rom.get(rom, {}).get('sha256')!r}, "
        f"inheritance={digest!r}"
        for rom, digest in expected.items()
        if by_rom.get(rom, {}).get("sha256") != digest
    ]
    if bad:
        raise SourceModelError(
            "exact-code наследование не совпадает с реестром образов: "
            + "; ".join(bad)
        )
    images = {}
    for rom, digest in expected.items():
        image_path = path.parent / by_rom[rom]["path"]
        try:
            data = image_path.read_bytes()
        except OSError as error:
            raise SourceModelError(f"нет образа exact-code ROM {image_path}") from error
        actual = hashlib.sha256(data).hexdigest()
        if actual != digest:
            raise SourceModelError(
                f"{image_path}: SHA-256 {actual}, ожидался {digest}"
            )
        images[rom] = data
    target_data = images[model.target]
    source_data = images[model.source]
    for value in model.ranges:
        start_text, end_text = value.split(":", 1)
        start, end = int(start_text, 16), int(end_text, 16)
        if end > len(target_data) or end > len(source_data):
            raise SourceModelError(
                f"exact-code диапазон {value} выходит за один из образов"
            )
        if target_data[start:end] != source_data[start:end]:
            raise SourceModelError(
                f"exact-code диапазон {value} различается у "
                f"{model.target}/{model.source}"
            )
