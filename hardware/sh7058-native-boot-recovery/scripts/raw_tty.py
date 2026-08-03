#!/usr/bin/env python3
"""Small dependency-free raw serial helper for the recovery scripts."""

import os
import select
import termios
import time
from typing import List, Optional


class SerialError(RuntimeError):
    """Raised when a serial operation cannot complete."""


class RawSerial:
    """Open a POSIX TTY as 8N1 with no software or hardware flow control."""

    def __init__(self, path: str, baud: int) -> None:
        self.path = path
        self.baud = baud
        self.fd: Optional[int] = None
        self._original: Optional[List[object]] = None

    def __enter__(self) -> "RawSerial":
        speed = getattr(termios, "B{}".format(self.baud), None)
        if speed is None:
            raise SerialError("unsupported baud rate: {}".format(self.baud))

        try:
            fd = os.open(
                self.path,
                os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK,
            )
        except OSError as exc:
            raise SerialError("cannot open {}: {}".format(self.path, exc)) from exc

        try:
            original = termios.tcgetattr(fd)
            attrs = list(original)
            attrs[6] = list(original[6])

            attrs[0] = 0
            attrs[1] = 0

            clear_cflags = termios.CSIZE | termios.PARENB | termios.CSTOPB
            for name in ("PARODD", "CRTSCTS", "CNEW_RTSCTS"):
                clear_cflags |= getattr(termios, name, 0)
            attrs[2] = (
                (attrs[2] & ~clear_cflags)
                | termios.CS8
                | termios.CREAD
                | termios.CLOCAL
            )

            attrs[3] = 0
            attrs[4] = speed
            attrs[5] = speed
            attrs[6][termios.VMIN] = 0
            attrs[6][termios.VTIME] = 0

            termios.tcsetattr(fd, termios.TCSANOW, attrs)
            termios.tcflush(fd, termios.TCIOFLUSH)
        except Exception as exc:
            os.close(fd)
            raise SerialError(
                "cannot configure {} at {} baud: {}".format(
                    self.path, self.baud, exc
                )
            ) from exc

        self.fd = fd
        self._original = original
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.fd is None:
            return
        if self._original is not None:
            try:
                termios.tcsetattr(self.fd, termios.TCSANOW, self._original)
            except termios.error:
                pass
        os.close(self.fd)
        self.fd = None

    def write(self, data: bytes, timeout: float = 1.0) -> None:
        if self.fd is None:
            raise SerialError("serial port is not open")

        deadline = time.monotonic() + timeout
        offset = 0
        while offset < len(data):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise SerialError("serial write timed out")
            _, writable, _ = select.select([], [self.fd], [], remaining)
            if not writable:
                raise SerialError("serial write timed out")
            try:
                written = os.write(self.fd, data[offset:])
            except BlockingIOError:
                continue
            if written == 0:
                raise SerialError("serial write returned zero bytes")
            offset += written

        termios.tcdrain(self.fd)

    def read_exact(self, size: int, timeout: float) -> bytes:
        if self.fd is None:
            raise SerialError("serial port is not open")

        deadline = time.monotonic() + timeout
        data = bytearray()
        while len(data) < size:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            readable, _, _ = select.select([self.fd], [], [], remaining)
            if not readable:
                break
            try:
                chunk = os.read(self.fd, size - len(data))
            except BlockingIOError:
                continue
            if chunk:
                data.extend(chunk)
        return bytes(data)


def hex_bytes(data: bytes) -> str:
    return data.hex(" ") if data else "<none>"
