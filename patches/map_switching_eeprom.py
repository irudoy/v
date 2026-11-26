"""Reference protocol and stepped state machine for two-copy EEPROM persistence.

This module defines the canonical 16-byte record format, recovery rules,
three-phase ping-pong transaction planner, M95320 SPI EEPROM model, and
stepped periodic writer matching the SH-2E firmware persistence unit for
Map Switching (#194).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import struct
import zlib


EEPROM_SIZE = 4096
PAGE_SIZE = 32
PAGE_A_ADDRESS = 0x0680  # Page 0x34 (0x0680..0x069F)
PAGE_B_ADDRESS = 0x0700  # Page 0x38 (0x0700..0x071F)
PAGES = (PAGE_A_ADDRESS, PAGE_B_ADDRESS)

RECORD_MAGIC = b"MS"
RECORD_VERSION = 1
RECORD_HEADER = struct.Struct(">2sBBI")
RECORD_CRC = struct.Struct(">I")
BODY_SIZE = RECORD_HEADER.size + RECORD_CRC.size  # 12 bytes
MARKER_SIZE = 4
RECORD_SIZE = BODY_SIZE + MARKER_SIZE  # 16 bytes

VALID_MARKER = 0xA65DC39E
INVALID_MARKER = 0x00000000
VALID_MARKER_BYTES = struct.pack(">I", VALID_MARKER)
INVALID_MARKER_BYTES = struct.pack(">I", INVALID_MARKER)
ERASED_PAGE = bytes([0xFF]) * PAGE_SIZE
U32_MASK = 0xFFFFFFFF

MIN_SLOT = 1
MAX_SLOT = 5
SLOTS = range(MIN_SLOT, MAX_SLOT + 1)

PAGE_NONE = 0xFF
PAGE_INDEX_A = 0
PAGE_INDEX_B = 1

# Stepped writer phases matching the SH-2E runtime RAM state machine.
PHASE_IDLE = 0
PHASE_WAIT_PRE_WIP = 1
PHASE_WAIT_INVAL = 2
PHASE_WAIT_BODY = 3
PHASE_WAIT_COMMIT = 4
PHASE_QUARANTINE = 5

# Diagnostic error / abort codes recorded in runtime RAM.
ERR_NONE = 0
ERR_SPI_TIMEOUT = 1
ERR_WIP_TIMEOUT = 2
ERR_VERIFY_INVAL = 3
ERR_VERIFY_BODY = 4
ERR_VERIFY_COMMIT = 5
ERR_INHIBITED = 6
ERR_BOOT_AMBIGUOUS = 7
ERR_BOOT_READ_FAILED = 8

# Default timing and wear-bounding limits (periodic EEPROM task tick units).
DEFAULT_WRITE_DELAY_TICKS = 150
DEFAULT_WIP_TIMEOUT_TICKS = 10
DEFAULT_MAX_RETRIES_PER_SLOT = 2

# 16-byte ROM configuration block (MSPE v1) placed at 0x000D6D80..0x000D6D8F on JK08A:
#   +0x00: 4s  magic ("MSPE")
#   +0x04: B   version (1)
#   +0x05: B   flags (bit0=enabled)
#   +0x06: H   write_delay_ticks (1..65535)
#   +0x08: B   wip_timeout_ticks (1..255)
#   +0x09: B   max_retries_per_slot (1..255)
#   +0x0A: H   reserved (0)
#   +0x0C: I   sentinel (0x5AA5A55A)
EEPROM_CONFIG_MAGIC = b"MSPE"
EEPROM_CONFIG_VERSION = 1
EEPROM_CONFIG_SENTINEL = 0x5AA5A55A
EEPROM_CONFIG_SIZE = 16
EEPROM_CONFIG_FORMAT = struct.Struct(">4sBBHBBHI")
assert EEPROM_CONFIG_FORMAT.size == EEPROM_CONFIG_SIZE

EEPROM_FLAG_ENABLED = 0x01
VALID_EEPROM_FLAGS_MASK = EEPROM_FLAG_ENABLED


@dataclass(frozen=True)
class EepromPersistenceConfig:
    """16-byte ROM configuration for Map Switching EEPROM persistence (MSPE v1)."""

    flags: int = EEPROM_FLAG_ENABLED
    write_delay_ticks: int = DEFAULT_WRITE_DELAY_TICKS
    wip_timeout_ticks: int = DEFAULT_WIP_TIMEOUT_TICKS
    max_retries_per_slot: int = DEFAULT_MAX_RETRIES_PER_SLOT

    @property
    def enabled(self) -> bool:
        return bool(self.flags & EEPROM_FLAG_ENABLED)

    def validate(self) -> None:
        if self.flags & ~VALID_EEPROM_FLAGS_MASK:
            raise ValueError(f"unsupported eeprom persistence flags {self.flags:#x}")
        if not 1 <= self.write_delay_ticks <= 0xFFFF:
            raise ValueError("write_delay_ticks must lie in 1..65535")
        if not 1 <= self.wip_timeout_ticks <= 255:
            raise ValueError("wip_timeout_ticks must lie in 1..255")
        if not 1 <= self.max_retries_per_slot <= 255:
            raise ValueError("max_retries_per_slot must lie in 1..255")

    def is_valid(self) -> bool:
        try:
            self.validate()
        except ValueError:
            return False
        return True

    def to_bytes(self) -> bytes:
        self.validate()
        return EEPROM_CONFIG_FORMAT.pack(
            EEPROM_CONFIG_MAGIC,
            EEPROM_CONFIG_VERSION,
            self.flags,
            self.write_delay_ticks,
            self.wip_timeout_ticks,
            self.max_retries_per_slot,
            0,
            EEPROM_CONFIG_SENTINEL,
        )

    @classmethod
    def from_bytes(cls, raw: bytes) -> "EepromPersistenceConfig":
        if len(raw) != EEPROM_CONFIG_SIZE:
            raise ValueError(
                f"expected {EEPROM_CONFIG_SIZE} bytes for MSPE config, got {len(raw)}"
            )
        (
            magic,
            version,
            flags,
            write_delay_ticks,
            wip_timeout_ticks,
            max_retries_per_slot,
            reserved,
            sentinel,
        ) = EEPROM_CONFIG_FORMAT.unpack(raw)
        if magic != EEPROM_CONFIG_MAGIC:
            raise ValueError(f"invalid MSPE magic {magic!r}")
        if version != EEPROM_CONFIG_VERSION:
            raise ValueError(f"unsupported MSPE version {version}")
        if reserved != 0:
            raise ValueError(f"non-zero MSPE reserved field {reserved:#x}")
        if sentinel != EEPROM_CONFIG_SENTINEL:
            raise ValueError(f"invalid MSPE sentinel {sentinel:#010x}")
        config = cls(
            flags=flags,
            write_delay_ticks=write_delay_ticks,
            wip_timeout_ticks=wip_timeout_ticks,
            max_retries_per_slot=max_retries_per_slot,
        )
        config.validate()
        return config


@dataclass(frozen=True)
class PersistenceRecord:
    """Decoded two-copy Map Switching EEPROM record."""

    slot: int
    generation: int

    def __post_init__(self) -> None:
        if self.slot not in SLOTS:
            raise ValueError(f"slot must be in 1..5, got {self.slot}")
        if not (0 <= self.generation <= U32_MASK):
            raise ValueError(f"generation out of u32 range: {self.generation}")

    def body_bytes(self) -> bytes:
        header = RECORD_HEADER.pack(
            RECORD_MAGIC, RECORD_VERSION, self.slot, self.generation
        )
        crc = zlib.crc32(header) & U32_MASK
        return header + RECORD_CRC.pack(crc)

    def record_bytes(self, *, valid: bool = True) -> bytes:
        marker = VALID_MARKER_BYTES if valid else INVALID_MARKER_BYTES
        return self.body_bytes() + marker

    def page_bytes(self, *, valid: bool = True) -> bytes:
        return self.record_bytes(valid=valid).ljust(PAGE_SIZE, b"\xff")


@dataclass(frozen=True)
class RecoveryResult:
    """Boot-time selection outcome across both reserved EEPROM pages."""

    active_page: int  # PAGE_INDEX_A, PAGE_INDEX_B, or PAGE_NONE
    slot: int  # 1..5
    generation: int
    ambiguous: bool

    @property
    def slot_index(self) -> int:
        return self.slot - 1

    @property
    def active_address(self) -> int | None:
        if self.active_page == PAGE_INDEX_A:
            return PAGE_A_ADDRESS
        if self.active_page == PAGE_INDEX_B:
            return PAGE_B_ADDRESS
        return None


@dataclass(frozen=True)
class WriteOperation:
    """Single page-local M95320 WRITE command frame."""

    address: int
    data: bytes

    def __post_init__(self) -> None:
        if not (0 <= self.address < EEPROM_SIZE):
            raise ValueError(f"address out of 4 KiB range: {self.address:#x}")
        page_base = self.address & ~(PAGE_SIZE - 1)
        if page_base not in PAGES:
            raise ValueError(f"address outside reserved pages: {self.address:#x}")
        offset = self.address - page_base
        if not (1 <= len(self.data) <= PAGE_SIZE - offset):
            raise ValueError(
                f"write crosses 32-byte page boundary at {self.address:#x} "
                f"(len={len(self.data)})"
            )


def crc32_ieee(data: bytes) -> int:
    """Compute standard IEEE 802.3 CRC-32 matching the SH-2E bitwise routine."""
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xEDB88320
            else:
                crc >>= 1
    return crc ^ 0xFFFFFFFF


def decode_record(raw: bytes) -> PersistenceRecord | None:
    """Validate and decode a 16-byte record prefix, or return None if invalid."""
    if len(raw) < RECORD_SIZE:
        return None
    if raw[BODY_SIZE:RECORD_SIZE] != VALID_MARKER_BYTES:
        return None
    header = raw[:RECORD_HEADER.size]
    magic, version, slot, generation = RECORD_HEADER.unpack(header)
    if magic != RECORD_MAGIC or version != RECORD_VERSION or slot not in SLOTS:
        return None
    stored_crc = RECORD_CRC.unpack(raw[RECORD_HEADER.size:BODY_SIZE])[0]
    if stored_crc != crc32_ieee(header):
        return None
    return PersistenceRecord(slot=slot, generation=generation)


def recover_pages(page_a: bytes, page_b: bytes) -> RecoveryResult:
    """Select the newest valid record across pages 0x0680 and 0x0700."""
    rec_a = decode_record(page_a)
    rec_b = decode_record(page_b)
    if rec_a is None and rec_b is None:
        return RecoveryResult(
            active_page=PAGE_NONE,
            slot=1,
            generation=0,
            ambiguous=False,
        )
    if rec_a is None:
        assert rec_b is not None
        return RecoveryResult(
            active_page=PAGE_INDEX_B,
            slot=rec_b.slot,
            generation=rec_b.generation,
            ambiguous=False,
        )
    if rec_b is None:
        return RecoveryResult(
            active_page=PAGE_INDEX_A,
            slot=rec_a.slot,
            generation=rec_a.generation,
            ambiguous=False,
        )
    distance = (rec_b.generation - rec_a.generation) & U32_MASK
    if distance == 0 or distance == 0x80000000:
        return RecoveryResult(
            active_page=PAGE_NONE,
            slot=1,
            generation=0,
            ambiguous=True,
        )
    if distance < 0x80000000:
        return RecoveryResult(
            active_page=PAGE_INDEX_B,
            slot=rec_b.slot,
            generation=rec_b.generation,
            ambiguous=False,
        )
    return RecoveryResult(
        active_page=PAGE_INDEX_A,
        slot=rec_a.slot,
        generation=rec_a.generation,
        ambiguous=False,
    )


def recover_eeprom(eeprom: bytes | bytearray) -> RecoveryResult:
    """Recover the selected slot from a full 4 KiB EEPROM image."""
    if len(eeprom) != EEPROM_SIZE:
        raise ValueError(f"expected {EEPROM_SIZE} bytes, got {len(eeprom)}")
    page_a = bytes(eeprom[PAGE_A_ADDRESS:PAGE_A_ADDRESS + RECORD_SIZE])
    page_b = bytes(eeprom[PAGE_B_ADDRESS:PAGE_B_ADDRESS + RECORD_SIZE])
    return recover_pages(page_a, page_b)


def plan_write(eeprom: bytes | bytearray, slot: int) -> tuple[WriteOperation, ...]:
    """Build the three-phase write sequence on the inactive page, if needed."""
    if slot not in SLOTS:
        raise ValueError(f"slot must be in 1..5, got {slot}")
    recovery = recover_eeprom(eeprom)
    if recovery.ambiguous:
        return ()
    if recovery.active_page != PAGE_NONE and recovery.slot == slot:
        return ()
    destination = (
        PAGE_B_ADDRESS if recovery.active_page == PAGE_INDEX_A else PAGE_A_ADDRESS
    )
    generation = (
        0 if recovery.active_page == PAGE_NONE else (recovery.generation + 1) & U32_MASK
    )
    record = PersistenceRecord(slot=slot, generation=generation)
    return (
        WriteOperation(destination + BODY_SIZE, INVALID_MARKER_BYTES),
        WriteOperation(destination, record.body_bytes()),
        WriteOperation(destination + BODY_SIZE, VALID_MARKER_BYTES),
    )


@dataclass
class M95320Device:
    """Behavioral model of the 4 KiB ST M95320 SPI EEPROM for persistence tests."""

    memory: bytearray = field(default_factory=lambda: bytearray([0xFF] * EEPROM_SIZE))
    wel: bool = False
    wip_remaining: int = 0
    bp_bits: int = 0  # bits 3..2 of status register (0=none, 1=top1/4, 2=top1/2, 3=all)
    wip_polls_per_write: int = 1
    bus_fault_read: bool = False
    bus_fault_write: bool = False

    def is_protected(self, address: int) -> bool:
        if self.bp_bits == 0:
            return False
        if self.bp_bits == 1:
            return address >= 0x0C00
        if self.bp_bits == 2:
            return address >= 0x0800
        return True

    def rdsr(self) -> int:
        if self.bus_fault_read:
            return 0xFF
        wip = 1 if self.wip_remaining > 0 else 0
        status = ((self.bp_bits & 0x3) << 2) | ((1 if self.wel else 0) << 1) | wip
        if self.wip_remaining > 0:
            self.wip_remaining -= 1
        return status

    def wren(self) -> None:
        if self.wip_remaining == 0 and not self.bus_fault_write:
            self.wel = True

    def wrdi(self) -> None:
        self.wel = False

    def read(self, address: int, length: int) -> bytes:
        if self.bus_fault_read or self.wip_remaining > 0:
            return bytes([0xFF]) * length
        out = bytearray(length)
        for index in range(length):
            out[index] = self.memory[(address + index) % EEPROM_SIZE]
        return bytes(out)

    def write(self, address: int, data: bytes) -> None:
        if self.wip_remaining > 0 or not self.wel or not data or self.bus_fault_write:
            self.wel = False
            return
        self.wel = False
        if self.is_protected(address):
            return
        page_base = address & ~(PAGE_SIZE - 1)
        offset = address - page_base
        for index, byte in enumerate(data):
            self.memory[page_base + ((offset + index) % PAGE_SIZE)] = byte
        self.wip_remaining = self.wip_polls_per_write


@dataclass
class PersistenceState:
    """RAM state of the stepped Map Switching EEPROM persistence manager."""

    phase: int = PHASE_IDLE
    active_page: int = PAGE_NONE
    committed_slot: int = 0  # 0=none committed in EEPROM yet, else 1..5
    active_generation: int = 0
    boot_ok: bool = False
    boot_ambiguous: bool = False
    pending_slot: int = 0
    debounce_ticks: int = 0
    wip_ticks: int = 0
    dest_page: int = PAGE_INDEX_A
    staged_record: bytes = b""
    staged_generation: int = 0
    retry_slot: int = 0
    retry_count: int = 0
    last_error: int = ERR_NONE
    write_count: int = 0


def boot_restore(device: M95320Device, state: PersistenceState) -> int:
    """Restore slot 0..4 from EEPROM on boot and initialize runtime state."""
    state.phase = PHASE_IDLE
    state.active_page = PAGE_NONE
    state.committed_slot = 0
    state.active_generation = 0
    state.boot_ok = False
    state.boot_ambiguous = False
    state.pending_slot = 0
    state.debounce_ticks = 0
    state.wip_ticks = 0
    state.dest_page = PAGE_INDEX_A
    state.staged_record = b""
    state.staged_generation = 0
    state.retry_slot = 0
    state.retry_count = 0
    state.last_error = ERR_NONE
    state.write_count = 0
    status = device.rdsr()
    if device.bus_fault_read or (status & 0x01):
        state.last_error = ERR_BOOT_READ_FAILED
        return 0
    page_a = device.read(PAGE_A_ADDRESS, RECORD_SIZE)
    page_b = device.read(PAGE_B_ADDRESS, RECORD_SIZE)
    recovery = recover_pages(page_a, page_b)
    state.boot_ok = True
    state.boot_ambiguous = recovery.ambiguous
    state.active_page = recovery.active_page
    state.active_generation = recovery.generation
    state.committed_slot = (
        recovery.slot if recovery.active_page != PAGE_NONE else 0
    )
    if recovery.ambiguous:
        state.last_error = ERR_BOOT_AMBIGUOUS
    return recovery.slot_index


def _abort_write(state: PersistenceState, error: int) -> None:
    state.phase = PHASE_QUARANTINE
    state.debounce_ticks = 0
    state.wip_ticks = 0
    state.last_error = error
    if state.retry_slot != state.pending_slot:
        state.retry_slot = state.pending_slot
        state.retry_count = 1
    elif state.retry_count < 0xFF:
        state.retry_count += 1


def step_persistence(
    device: M95320Device,
    state: PersistenceState,
    *,
    active_slot_index: int,
    enabled: bool = True,
    stock_busy: bool = False,
    inhibited: bool = False,
    write_delay_ticks: int = DEFAULT_WRITE_DELAY_TICKS,
    wip_timeout_ticks: int = DEFAULT_WIP_TIMEOUT_TICKS,
    max_retries_per_slot: int = DEFAULT_MAX_RETRIES_PER_SLOT,
) -> None:
    """Advance the stepped background EEPROM writer by one periodic tick."""
    if state.phase == PHASE_IDLE:
        if not enabled or stock_busy or not state.boot_ok or state.boot_ambiguous:
            return
        if not (0 <= active_slot_index <= 4):
            return
        desired_slot = active_slot_index + 1
        if state.committed_slot == desired_slot:
            state.pending_slot = 0
            state.debounce_ticks = 0
            return
        if inhibited:
            state.debounce_ticks = 0
            return
        if state.retry_slot == desired_slot and state.retry_count >= max_retries_per_slot:
            return
        if state.pending_slot != desired_slot:
            state.pending_slot = desired_slot
            state.debounce_ticks = 1
            if state.retry_slot != desired_slot:
                state.retry_slot = desired_slot
                state.retry_count = 0
            if state.debounce_ticks < write_delay_ticks:
                return
        else:
            state.debounce_ticks += 1
            if state.debounce_ticks < write_delay_ticks:
                return
        state.dest_page = (
            PAGE_INDEX_B if state.active_page == PAGE_INDEX_A else PAGE_INDEX_A
        )
        state.staged_generation = (
            0
            if state.active_page == PAGE_NONE
            else (state.active_generation + 1) & U32_MASK
        )
        rec = PersistenceRecord(slot=desired_slot, generation=state.staged_generation)
        state.staged_record = rec.record_bytes(valid=True)
        state.wip_ticks = 0
        state.phase = PHASE_WAIT_PRE_WIP
        return

    dest_addr = PAGES[state.dest_page]
    status = device.rdsr()
    if status & 0x01:
        if state.phase == PHASE_QUARANTINE:
            return
        state.wip_ticks += 1
        if state.wip_ticks >= wip_timeout_ticks:
            _abort_write(state, ERR_WIP_TIMEOUT)
        return

    if state.phase == PHASE_QUARANTINE:
        if status & 0x02:
            device.wrdi()
            return
        state.phase = PHASE_IDLE
        return

    if state.phase == PHASE_WAIT_PRE_WIP:
        if inhibited:
            _abort_write(state, ERR_INHIBITED)
            return
        device.wren()
        device.write(dest_addr + BODY_SIZE, INVALID_MARKER_BYTES)
        device.wrdi()
        state.wip_ticks = 0
        state.phase = PHASE_WAIT_INVAL
        return

    if state.phase == PHASE_WAIT_INVAL:
        marker = device.read(dest_addr + BODY_SIZE, MARKER_SIZE)
        if marker != INVALID_MARKER_BYTES:
            _abort_write(state, ERR_VERIFY_INVAL)
            return
        if inhibited:
            _abort_write(state, ERR_INHIBITED)
            return
        device.wren()
        device.write(dest_addr, state.staged_record[:BODY_SIZE])
        device.wrdi()
        state.wip_ticks = 0
        state.phase = PHASE_WAIT_BODY
        return

    if state.phase == PHASE_WAIT_BODY:
        readback = device.read(dest_addr, RECORD_SIZE)
        if (
            readback[:BODY_SIZE] != state.staged_record[:BODY_SIZE]
            or readback[BODY_SIZE:RECORD_SIZE] != INVALID_MARKER_BYTES
        ):
            _abort_write(state, ERR_VERIFY_BODY)
            return
        if inhibited:
            _abort_write(state, ERR_INHIBITED)
            return
        device.wren()
        device.write(dest_addr + BODY_SIZE, VALID_MARKER_BYTES)
        device.wrdi()
        state.wip_ticks = 0
        state.phase = PHASE_WAIT_COMMIT
        return

    if state.phase == PHASE_WAIT_COMMIT:
        readback = device.read(dest_addr, RECORD_SIZE)
        if readback != state.staged_record:
            _abort_write(state, ERR_VERIFY_COMMIT)
            return
        state.active_page = state.dest_page
        state.committed_slot = state.pending_slot
        state.active_generation = state.staged_generation
        state.phase = PHASE_IDLE
        state.debounce_ticks = 0
        state.wip_ticks = 0
        state.retry_count = 0
        state.last_error = ERR_NONE
        state.write_count += 1
