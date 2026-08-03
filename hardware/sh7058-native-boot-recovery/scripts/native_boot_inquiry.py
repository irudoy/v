#!/usr/bin/env python3
"""Run the non-destructive SH7058 native boot handshake and device inquiry."""

import argparse
import sys
import time
from typing import List

from raw_tty import RawSerial, SerialError, hex_bytes


SYNC = b"\x00"
BIT_RATE_COMPLETE = b"\x55"
BOOT_OK = b"\xE6"
SUPPORTED_DEVICE_INQUIRY = b"\x20"
SUPPORTED_DEVICE_RESPONSE = 0x30


class ProtocolError(RuntimeError):
    """Raised when the boot loader returns an invalid or incomplete response."""


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Send only the non-destructive 00/55/20 SH7058 native boot sequence. "
            "This tool has no erase or programming command."
        )
    )
    parser.add_argument("port", help="serial device, for example /dev/cu.wchusbserial1220")
    parser.add_argument("--baud", type=int, default=19200)
    parser.add_argument("--sync-attempts", type=positive_int, default=30)
    parser.add_argument("--sync-timeout", type=positive_float, default=0.10)
    parser.add_argument("--response-timeout", type=positive_float, default=1.0)
    parser.add_argument("--inquiries", type=positive_int, default=3)
    parser.add_argument("--interval", type=positive_float, default=2.5)
    return parser.parse_args()


def read_inquiry_response(serial: RawSerial, timeout: float) -> bytes:
    header = serial.read_exact(2, timeout)
    if len(header) != 2:
        raise ProtocolError(
            "inquiry response header is incomplete: {}".format(hex_bytes(header))
        )
    if header[0] != SUPPORTED_DEVICE_RESPONSE:
        raise ProtocolError(
            "unexpected inquiry response command: {}".format(hex_bytes(header))
        )

    payload_length = header[1]
    remainder = serial.read_exact(payload_length + 1, timeout)
    if len(remainder) != payload_length + 1:
        raise ProtocolError(
            "inquiry response is incomplete: {}".format(hex_bytes(header + remainder))
        )

    frame = header + remainder
    if sum(frame) & 0xFF:
        raise ProtocolError(
            "inquiry response checksum is invalid: {}".format(hex_bytes(frame))
        )
    return frame


def printable_payload(frame: bytes) -> str:
    payload = frame[2:-1]
    return "".join(chr(value) if 0x20 <= value <= 0x7E else "." for value in payload)


def main() -> int:
    args = parse_args()
    responses: List[bytes] = []

    try:
        with RawSerial(args.port, args.baud) as serial:
            print("port={} mode={} 8N1".format(args.port, args.baud))
            print("TX is restricted to: 00, 55, 20")

            sync_reply = b""
            sync_attempt = 0
            unexpected = bytearray()
            for attempt in range(1, args.sync_attempts + 1):
                serial.write(SYNC)
                reply = serial.read_exact(1, args.sync_timeout)
                if reply == SYNC:
                    sync_reply = reply
                    sync_attempt = attempt
                    break
                unexpected.extend(reply)

            print("sync_attempt={}".format(sync_attempt or "none"))
            print("sync_rx={}".format(hex_bytes(sync_reply or bytes(unexpected))))
            if not sync_reply:
                raise ProtocolError("no 00 synchronization response")

            serial.write(BIT_RATE_COMPLETE)
            boot_reply = serial.read_exact(1, args.response_timeout)
            print("55_rx={}".format(hex_bytes(boot_reply)))
            if boot_reply == BIT_RATE_COMPLETE:
                raise ProtocolError("received 55 echo; check for TX/RX loopback")
            if boot_reply != BOOT_OK:
                raise ProtocolError("expected E6 boot response")

            for index in range(args.inquiries):
                if index:
                    time.sleep(args.interval)
                serial.write(SUPPORTED_DEVICE_INQUIRY)
                frame = read_inquiry_response(serial, args.response_timeout)
                responses.append(frame)
                print("inquiry_{}={}".format(index + 1, hex_bytes(frame)))
                print("payload_{}={}".format(index + 1, printable_payload(frame)))

    except (OSError, SerialError, ProtocolError) as exc:
        print("FAIL: {}".format(exc), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return 130

    identical = all(response == responses[0] for response in responses[1:])
    print("inquiries_identical={}".format(identical))
    if not identical:
        print("FAIL: inquiry responses differ", file=sys.stderr)
        return 1
    print("PASS: native boot inquiry completed without erase/program commands")
    return 0


if __name__ == "__main__":
    sys.exit(main())
