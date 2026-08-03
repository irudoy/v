#!/usr/bin/env python3
"""Verify a physically looped-back USB-UART adapter."""

import argparse
import sys

from raw_tty import RawSerial, SerialError, hex_bytes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify exact TX/RX loopback on a disconnected USB-UART adapter."
    )
    parser.add_argument("port", help="serial device, for example /dev/cu.wchusbserial1220")
    parser.add_argument("--baud", type=int, default=19200)
    parser.add_argument("--repeats", type=int, default=4)
    parser.add_argument(
        "--loopback-connected",
        action="store_true",
        help="confirm that adapter TX/RX are disconnected from the ECU and shorted together",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.loopback_connected:
        print(
            "Refusing to transmit: disconnect TX/RX from the ECU, short them "
            "together, and pass --loopback-connected.",
            file=sys.stderr,
        )
        return 2
    if args.repeats < 1:
        print("--repeats must be at least 1", file=sys.stderr)
        return 2

    payload = bytes(range(256)) * args.repeats
    timeout = max(2.0, len(payload) * 10.0 / args.baud * 3.0 + 0.5)

    try:
        with RawSerial(args.port, args.baud) as serial:
            serial.write(payload, timeout=timeout)
            received = serial.read_exact(len(payload), timeout=timeout)
    except (OSError, SerialError) as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 1

    exact = received == payload
    print("port={}".format(args.port))
    print("mode={} 8N1".format(args.baud))
    print("tx={} rx={}".format(len(payload), len(received)))
    print("exact_match={}".format(exact))
    print("rx_head={}".format(hex_bytes(received[:16])))
    return 0 if exact else 1


if __name__ == "__main__":
    sys.exit(main())
