"""Stock-bus recording fields from the CAN specification and shift audit.

See defs/analysis/can/JK08A.can.md and tools/logs/tcm_shift_audit.py. These host-only
fields do not change the ECU telemetry wire contract or its generated schema.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StockField:
    key: str
    label: str
    unit: str
    digits: int = 0


FIELDS = (
    StockField("tcm_target_gear", "TCM target gear", "gear"),
    StockField("tcm_output_speed", "TCM output speed", "cnt"),
    StockField("tcm_turbine_speed", "TCM turbine speed", "cnt"),
    StockField("tcm_speed_ratio", "TCM output / turbine ratio", "ratio", 4),
    StockField("vehicle_speed_284_kmh", "Vehicle speed 0x284", "km/h", 2),
    StockField("tcm_word_a", "TCM word A", "cnt"),
    StockField("tcm_word_b", "TCM word B", "cnt"),
    StockField("tcm_status", "TCM status", "code"),
    StockField("tcm_gear_phase", "TCM gear phase", "index"),
    StockField("tcm_reduction", "TCM reduction byte", "cnt"),
    StockField("tcm_shift_code", "TCM shift code", "index"),
    StockField("can_actual_torque", "CAN actual torque word", "cnt"),
    StockField("can_request", "CAN pre-limiter request word", "cnt"),
    StockField("can_limited_request", "CAN limited request word", "cnt"),
    StockField("can_parallel_torque", "CAN parallel torque word", "cnt"),
)
IDS = (0x160, 0x176, 0x177, 0x284)


def _word_pair(data):
    return data[0] << 4 | data[1] >> 4, (data[1] & 15) << 8 | data[2]


def decode(can_id, data):
    if can_id == 0x174 and len(data) >= 4:
        a, b = _word_pair(data)
        target = data[3] >> 4
        return dict(tcm_target_gear=target if 1 <= target <= 7 else None,
                    tcm_word_a=a, tcm_word_b=b,
                    tcm_status=data[4] >> 5 if len(data) >= 5 else None)
    if can_id == 0x176 and len(data) >= 4:
        output = int.from_bytes(data[:2], "big")
        turbine = int.from_bytes(data[2:4], "big")
        return dict(tcm_output_speed=output, tcm_turbine_speed=turbine,
                    tcm_speed_ratio=output / turbine if turbine else None)
    if can_id == 0x177 and len(data) >= 6:
        return dict(tcm_gear_phase=data[2] & 7, tcm_reduction=data[4],
                    tcm_shift_code=15 if data[5] & 128 else (data[5] >> 3) & 15)
    if can_id == 0x284 and len(data) >= 6:
        raw = int.from_bytes(data[4:6], "big")
        return dict(vehicle_speed_284_kmh=None if raw == 0xFFFF else raw / 100)
    if can_id == 0x180 and len(data) >= 5:
        a, b = _word_pair(data[2:5])
        return dict(can_actual_torque=None if a == 4095 else a,
                    can_request=None if b == 4095 else b)
    if can_id == 0x160 and len(data) >= 3:
        a, b = _word_pair(data[:3])
        return dict(can_limited_request=None if a == 4095 else a,
                    can_parallel_torque=None if b == 4095 else b)
    return {}
