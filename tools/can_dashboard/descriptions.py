"""What each code metric of the dashboard means, shown on hover over its name.

The code metrics are the quantities of the stock frames, the drive runs, and
the GPS source. A description states the quantity the ECU or the bus carries
and the direction of its scale where that matters. A telemetry field carries
its description in its presentation in the schema.
"""

from __future__ import annotations


DESCRIPTIONS = {
    "rpm": (
        "Engine speed that the ECU measures from crank events, from the "
        "stock frame 0x180 at 3.125 RPM per count."
    ),
    "vehicle_speed_kmh": (
        "Vehicle speed from the ABS frame 0x280 at 0.01 km/h per count. "
        "It reads 0 below about 1.5 km/h."
    ),
    "injection_average_ms": (
        "Mean of the six calculated injection pulses in ms: compensated "
        "software commands, not measured injector-open times."
    ),
    "gear": (
        "Selector lever position from frame 0x421: P, R, N, D, DS, or the "
        "manual gears M1..M5. TRANSITION while the lever moves between "
        "positions."
    ),
    "tcm_gear": (
        "Current gear that the transmission control module reports in the "
        "low nibble of frame 0x174 byte 3, in D and DS as well as in manual "
        "mode. The high nibble holds the target gear of a shift. P, R, and N "
        "carry no forward gear and read --."
    ),
    "selected_map": (
        "Map selected through the ASCD switch. The telemetry stream carries "
        "the zero-based index of the map-switching runtime, shown as index + "
        "1; the runtime reads an index outside Maps 1..5 as Map 1. Until a "
        "verified stream publishes the index, the map follows the stock "
        "bus: every controller start selects Map 1, and a SET + CANCEL "
        "gesture that the CRUISE and SET lamps answer with N pulses selects "
        "Map N."
    ),
    "zero_to_100_s": (
        "Last 0-100 km/h time from the ABS speed. A run arms at standstill "
        "and starts at the first speed above zero. The 0-100 button shows "
        "the timer bar with the best times."
    ),
    "hundred_to_200_s": (
        "Last 100-200 km/h time from the ABS speed, timed between the "
        "crossings of 100 and 200 km/h. The 0-100 button shows the timer bar "
        "with the best times."
    ),
    "stock_rpm": (
        "Engine speed in the stock frame 0x180 at 3.125 RPM per count, taken "
        "when the frame is serialized. Engine speed shows the same frame, so "
        "the row is not an independent sensor."
    ),
    "ascd_button": (
        "Cruise control (ASCD) switch input from frame 0x239: RELEASE, SET, "
        "RES, or CANCEL. The map selection gesture uses this input."
    ),
    "dashboard_state": (
        "ASCD lamp state that the ECU sends to the combination meter in "
        "frame 0x551 byte 5. The runtime pulses state 4 to confirm a map "
        "selection and holds it while Rolling Launch is active."
    ),
    "gps_lat": (
        "No latitude signal is decoded on the primary CAN network, so the "
        "row reads --."
    ),
    "gps_lon": (
        "No longitude signal is decoded on the primary CAN network, so the "
        "row reads --."
    ),
    "gps_status": "Source of the coordinates, when one is decoded.",
}


def describe(key):
    """Return the description of a code metric key, or an empty string."""
    return DESCRIPTIONS.get(key, "")
