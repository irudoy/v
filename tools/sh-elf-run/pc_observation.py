"""Strict GNU SH PC records and byte-bound invocation observations."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_trace(data: bytes, process_exit: int):
    """Accept only a complete successful version-1 ASCII/LF byte stream."""
    require(type(data) is bytes, "trace input must be raw bytes")
    require(type(process_exit) is int and process_exit == 0, "simulator process failed")
    try:
        text = data.decode("ascii", errors="strict")
    except UnicodeDecodeError as error:
        raise ValueError("trace is not ASCII") from error
    require(text.endswith("\n"), "trace lacks terminal LF")
    lines = text.split("\n")[:-1]
    require(len(lines) >= 3 and lines[0] == "VQ_SH_PC_TRACE version=1",
            "unsupported or empty trace header")
    footer = re.fullmatch(r"VQ_SH_PC_TRACE end=complete records=([1-9][0-9]*)", lines[-1])
    require(footer is not None and int(footer[1]) == len(lines) - 2,
            "missing or inconsistent complete trailer")
    records = []
    for line in lines[1:-1]:
        row = re.fullmatch(r"pc=([0-9a-f]{8}) opcode=([0-9a-f]{4}) delay=([01])", line)
        require(row is not None, "unsupported instruction record")
        record = tuple(int(value, 16) for value in row.groups())
        require(record[0] % 2 == 0, "instruction PC is not word-aligned")
        records.append(record)
    return records


def function_block(source: bytes, name: str):
    """Extract one complete independently named assembly function."""
    require(re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", name) is not None,
            "unsupported assembly function name")
    escaped = re.escape(name.encode("ascii"))
    start = re.compile(rb"^    \.global " + escaped + rb"\n", re.M)
    finish = re.compile(rb"^    \.size " + escaped + rb",\.-" + escaped + rb"\n", re.M)
    starts, ends = list(start.finditer(source)), list(finish.finditer(source))
    require(len(starts) == len(ends) == 1 and starts[0].end() < ends[0].start(),
            "assembly function is missing, duplicated or incomplete")
    block = source[starts[0].start():ends[0].end()]
    require(len(re.findall(rb"^" + escaped + rb":\n", block, re.M)) == 1,
            "assembly function lacks one entry label")
    return block


def symbols_from_nm(text, begin_name, return_name, forbidden_range=None):
    wanted = {begin_name, return_name}
    found = {}
    for line in text.splitlines():
        fields = line.split()
        if len(fields) not in (3, 4) or fields[-1] not in wanted:
            continue
        name = fields[-1]
        require(name not in found, f"duplicate ELF marker: {name}")
        try:
            found[name] = (int(fields[0], 16), int(fields[1], 16) if len(fields) == 4 else None)
        except ValueError as error:
            raise ValueError("invalid ELF marker address or size") from error
    require(set(found) == wanted, "ELF lacks invocation/return markers")
    begin, size = found[begin_name]
    returned, _ = found[return_name]
    require(size is not None and size > 0 and size % 2 == 0,
            "ELF invocation size is invalid")
    require(0 <= begin < returned < begin + size <= 0x100000000
            and begin % 2 == returned % 2 == 0, "ELF return marker is outside the invocation")
    if forbidden_range is not None:
        low, high = forbidden_range
        require(not (begin < high and low < begin + size), "ELF observation ranges overlap")
    return {"begin": begin, "return": returned, "size": size, "end": begin + size}


def wrapper_bytes_from_elf(elf, output, markers, command, objcopy="sh-elf-objcopy"):
    """Extract linked wrapper bytes without writing to the input ELF."""
    before = sha256(elf)
    sections = command(["sh-elf-objdump", "-h", elf]).stdout
    (output / "elf-sections.txt").write_text(sections, encoding="utf-8")
    rows = re.findall(r"^\s*\d+\s+\.text\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+",
                      sections, re.M)
    require(len(rows) == 1, "ELF lacks one .text byte section")
    size, address = (int(value, 16) for value in rows[0])
    text_path = output / "linked-text.bin"
    require(text_path.resolve() != Path(elf).resolve(), "ELF extraction output aliases its input")
    command([objcopy, "--only-section=.text", "-O", "binary", elf, text_path])
    text = text_path.read_bytes()
    require(sha256(elf) == before, "ELF byte extraction changed its input")
    require(len(text) == size, "ELF .text byte extraction length differs")
    require(address <= markers["begin"] < markers["end"] <= address + size,
            "ELF invocation lies outside the linked .text section")
    wrapper = text[markers["begin"] - address:markers["end"] - address]
    (output / "invocation-wrapper.bin").write_bytes(wrapper)
    return wrapper


def segment_invocations(records, markers, helper_start, helper_bytes, helper_delays,
                        expected_frames):
    """Bind every opcode and retain each complete helper count in its caller frame."""
    helper_end = helper_start + len(helper_bytes)
    require(len(helper_bytes) > 0 and len(helper_bytes) % 2 == 0,
            "helper has no complete instruction words")
    helper_pcs = tuple(range(helper_start, helper_end, 2))
    require(len(helper_delays) == len(helper_pcs) and all(d in (0, 1) for d in helper_delays),
            "helper delay contract differs")
    require(len(wrapper_bytes := markers["bytes"]) == markers["size"],
            "linked wrapper size differs")
    require(not (markers["begin"] < helper_end and helper_start < markers["end"]),
            "ELF observation ranges overlap")
    counts, active, helper_records = [], False, []
    for pc, opcode, delay in records:
        require(type(pc) is int and type(opcode) is int and delay in (0, 1),
                "unsupported decoded instruction")
        inside_wrapper = markers["begin"] <= pc < markers["end"]
        inside_helper = helper_start <= pc < helper_end
        require(inside_wrapper or inside_helper, "record escaped requested ELF/helper ranges")
        if inside_wrapper:
            offset = pc - markers["begin"]
            require(pc % 2 == 0 and offset + 2 <= len(wrapper_bytes)
                    and opcode == int.from_bytes(wrapper_bytes[offset:offset + 2], "big"),
                    "wrapper opcode/address differs from linked ELF bytes")
        if pc == markers["begin"]:
            require(delay == 0 and not active, "nested or delayed invocation marker")
            active, helper_records = True, []
        if inside_helper:
            require(active, "helper PC outside an invocation")
            offset = pc - helper_start
            require(pc % 2 == 0 and opcode == int.from_bytes(helper_bytes[offset:offset + 2], "big"),
                    "helper opcode/address differs from stock bytes")
            helper_records.append((pc, delay))
        if pc == markers["return"]:
            require(delay == 0 and active, "unpaired or delayed return marker")
            length = len(helper_pcs)
            require(len(helper_records) % length == 0, "partial helper instruction sequence")
            for first in range(0, len(helper_records), length):
                sequence = helper_records[first:first + length]
                require(tuple(pc for pc, _ in sequence) == helper_pcs,
                        "helper ordinary/return/delay PC sequence differs")
                require(tuple(delay for _, delay in sequence) == tuple(helper_delays),
                        "helper delay-slot classification differs")
            counts.append(len(helper_records) // length)
            active = False
    require(not active, "trace ends inside an invocation")
    require(len(counts) == expected_frames,
            f"observed {len(counts)} invocation frames, expected {expected_frames}")
    return counts
