"""What each dashboard metric means, shown on hover over its name.

A description states the quantity the ECU or the bus carries, the direction
of its scale where that matters, and the evidence boundary of the conversion
the display applies. The README states the conversions themselves.
"""

from __future__ import annotations


def _injection(channel):
    return (
        f"Calculated injection pulse of channel {channel}, which drives "
        f"cylinder {channel + 1} by the diagnostic Power Balance order: the "
        "compensated software command in ms at 10 us per count, not a "
        "measured injector-open time."
    )


def _knock_margin(channel):
    text = (
        f"Smallest knock margin of evaluator channel {channel} since the "
        "previous capture of its context: the knock threshold minus the knock "
        "metric, in evaluator counts without a physical unit. A positive "
        "value is headroom below the threshold, and a negative value is an "
        "evaluation that the ECU counts as knock. The channel number is the "
        "cylinder number of the event that opens the knock window."
    )
    if channel in (3, 5):
        text += (
            " The stock threshold row of this channel holds 0xFFFF, so it "
            "reads -- unless the metric exceeds 32768."
        )
    return text


DESCRIPTIONS = {
    "rpm": (
        "Engine speed that the ECU measures from crank events, as the "
        "12.5 RPM word its own tables read, sampled with the rest of the "
        "telemetry snapshot. Stock CAN RPM carries the same measurement at "
        "a finer resolution from another moment."
    ),
    "vehicle_speed_kmh": (
        "Vehicle speed from the ABS frame 0x280 at 0.01 km/h per count. "
        "It reads 0 below about 1.5 km/h."
    ),
    "calculated_load_percent": (
        "Calculated load value of J1979 PID 0x04: the current airflow "
        "divided by the peak airflow. It is not the normalized Base Fuel "
        "Schedule that indexes the ignition and CVTC maps; Engine load "
        "carries that coordinate."
    ),
    "normalized_load_percent": (
        "Engine load that indexes the ignition and CVTC target maps: the "
        "Base Fuel Schedule as a ratio to the reference constant of the ROM "
        "in steps of 1/128, as the ECU computes it for the snapshot. 100 "
        "percent is the reference schedule, and the value saturates at "
        "199.2 percent. The live value feed sends it as VQ Engine Load."
    ),
    "timing_command_deg": (
        "Final ignition timing coordinate in degrees before TDC. A software "
        "command, not a measured spark angle. During a Rolling Launch late "
        "override it is the upstream stock coordinate, and APC command "
        "carries the effective value."
    ),
    "maf_total_g_s": (
        "Total intake airflow of both banks in g/s from the ECU airflow "
        "model, the value J1979 PID 0x10 reports. A model output, not a "
        "direct sensor reading."
    ),
    "injection_average_ms": (
        "Mean of the six calculated injection pulses in ms: compensated "
        "software commands, not measured injector-open times."
    ),
    "coolant_deg_c": "Engine coolant temperature.",
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
        "1; the runtime reads an index outside Maps 1..5 as Map 1. A stream "
        "without the index, such as profile 5, infers the map from the stock "
        "bus: every controller start selects Map 1, and a SET + CANCEL "
        "gesture that the CRUISE and SET lamps answer with N pulses selects "
        "Map N."
    ),
    "rolling_launch_phase_name": (
        "Phase of the Rolling Launch runtime: IDLE while it evaluates the "
        "activation gates, ACTIVE while it owns the launch fuel cut and the "
        "optional ignition retard, and COOLDOWN after a run ends, until the "
        "buttons stay released for the rearm period."
    ),
    "rolling_launch_abort_name": (
        "Reason code of the Rolling Launch runtime. In IDLE it names the "
        "first activation gate that fails, such as MAP DISABLED on a map "
        "without Rolling Launch or BUTTON INVALID while CANCEL is not held. "
        "ACTIVE reads NONE, and COOLDOWN keeps the reason that ended the "
        "run, such as BUTTON RELEASED, TIMEOUT, or MAP REQUEST."
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
    "maf_b1_v": (
        "Mass airflow sensor signal of bank 1 in volts, the ten-bit ADC "
        "count after a unit-nominal trim. The ECU converts it to airflow "
        "through its sensor table."
    ),
    "maf_b2_v": (
        "Mass airflow sensor signal of bank 2 in volts, the ten-bit ADC "
        "count after a unit-nominal trim. The ECU converts it to airflow "
        "through its sensor table."
    ),
    "bfs_ms": (
        "Base Fuel Schedule: the base injection time in ms for the measured "
        "air charge, before the fuel trims, the target-mixture factor, and "
        "the injector opening time. Normalized to its reference constant, "
        "it is the load axis of the ignition and CVTC maps, which Engine "
        "load shows."
    ),
    "af_sensor_b1_v": (
        "Front A/F sensor signal of bank 1 in volts, the item the factory "
        "data monitor calls A/F SEN1: 2.20 V is the sensor reference, and "
        "lower is richer. It is not converted to AFR: the ECU curve from "
        "voltage to lambda is not identified, and under sustained enrichment "
        "the reading moves lean."
    ),
    "af_sensor_b2_v": (
        "Front A/F sensor signal of bank 2 in volts, the item the factory "
        "data monitor calls A/F SEN1: 2.20 V is the sensor reference, and "
        "lower is richer. It is not converted to AFR: the ECU curve from "
        "voltage to lambda is not identified, and under sustained enrichment "
        "the reading moves lean."
    ),
    "af_state_factor": (
        "Commanded fuel multiplier against the stoichiometric base schedule. "
        "1.0000 is the closed-loop stoichiometric target, and a larger value "
        "commands enrichment: the target map supplies 1.00..1.16. The "
        "commanded lambda is 1 / factor."
    ),
    "stft_b1_percent": (
        "Short-term fuel trim of bank 1: the fast closed-loop correction "
        "from the A/F sensor, in percent. A positive value adds fuel."
    ),
    "stft_b2_percent": (
        "Short-term fuel trim of bank 2: the fast closed-loop correction "
        "from the A/F sensor, in percent. A positive value adds fuel."
    ),
    "ltft_b1_percent": (
        "Long-term fuel trim of bank 1 as diagnostics report it: the learned "
        "cell of the operating region plus the running adjustment, in "
        "percent. A positive value adds fuel."
    ),
    "ltft_b2_percent": (
        "Long-term fuel trim of bank 2 as diagnostics report it: the learned "
        "cell of the operating region plus the running adjustment, in "
        "percent. A positive value adds fuel."
    ),
    "apc_command_deg": (
        "Effective ignition timing command in degrees before TDC, as J1979 "
        "PID 0x0E reports it: 110 minus the APC byte. It follows Rolling "
        "Launch and the stock modes that move the command away from the "
        "timing coordinate. A software command, not a measured spark angle."
    ),
    "ignition_timing_adjustment_deg": (
        "Ignition timing adjustment of 0 to -5 degrees that the CONSULT "
        "work-support item TARGET IGN TIM ADJ sets and the ECU stores. The "
        "ECU adds it to the final timing coordinate only while coolant is "
        "above about 60 degC, engine speed is about 1200..3000 RPM, and the "
        "normalized load is about 50..72 percent, so it has no effect at "
        "idle. 0 means no adjustment."
    ),
    "app1_v": (
        "Accelerator pedal position sensor 1 in volts; it rises with pedal "
        "travel. Factory bands: 0.5..1.0 V released and 4.2..4.8 V fully "
        "depressed."
    ),
    "app2_v": (
        "Accelerator pedal position sensor 2 in volts, the second track that "
        "the ECU checks against sensor 1; it rises with pedal travel."
    ),
    "tps_b1_v": (
        "Throttle position sensor 1 of the bank 1 electric throttle body in "
        "volts; it rises with opening. Factory criteria: above 0.36 V "
        "released and below 4.75 V fully depressed."
    ),
    "tps_b2_v": (
        "Throttle position sensor 1 of the bank 2 electric throttle body in "
        "volts; it rises with opening. Factory criteria: above 0.36 V "
        "released and below 4.75 V fully depressed."
    ),
    "absolute_throttle_percent": (
        "Absolute throttle position as J1979 PID 0x11 reports it, in percent "
        "of the byte range."
    ),
    "intake_cvtc_actual_b1_deg_ca": (
        "Measured intake camshaft advance of bank 1 in crank degrees, from "
        "the phase of the cam sensor edges; a larger value is more advance."
    ),
    "intake_cvtc_actual_b2_deg_ca": (
        "Measured intake camshaft advance of bank 2 in crank degrees, from "
        "the phase of the cam sensor edges; a larger value is more advance."
    ),
    "intake_cvtc_target_deg_ca": (
        "Intake camshaft advance target common to both banks, in crank "
        "degrees. The CVTC controller drives the measured positions toward "
        "it."
    ),
    "exhaust_cvtc_target_deg_ca": (
        "Exhaust camshaft target common to both banks, in crank degrees."
    ),
    "intake_cvtc_duty_b1_percent": (
        "Duty of the bank 1 intake valve timing solenoid, in percent of its "
        "PWM period; the output that moves the camshaft. A larger duty "
        "advances the camshaft."
    ),
    "intake_cvtc_duty_b2_percent": (
        "Duty of the bank 2 intake valve timing solenoid, in percent of its "
        "PWM period; the output that moves the camshaft. A larger duty "
        "advances the camshaft."
    ),
    **{
        f"injection_{channel}_ms": _injection(channel)
        for channel in range(6)
    },
    "fuel_inhibit_cylinders": (
        "Cylinders whose injection the ECU cuts at this moment: none, all "
        "for a complete fuel cut, or the list of cut cylinders."
    ),
    "knock_timing_state": (
        "Signed Q8 timing state of the knock and high-detonation "
        "coordinator; its whole-number part enters the engine-event timing "
        "correction. Its physical unit is not resolved."
    ),
    "knock_surface_mode": (
        "Hot ignition surface in use: HIGH OCTANE or HIGH DETONATION. The "
        "knock coordinator selects it through several gates, one of them a "
        "hysteresis on a knock state, and the same bit scales the target "
        "mixture."
    ),
    "knock_count_latched": (
        "Knock exceedances that the evaluator counted between two snapshots, "
        "saturating."
    ),
    "knock_channels_latched": (
        "Knock channels that had an exceedance between two snapshots."
    ),
    **{
        f"knock_margin_min_ch{channel}_raw": _knock_margin(channel)
        for channel in range(1, 7)
    },
    "iat_deg_c": "Intake air temperature.",
    "fuel_temperature_deg_c": (
        "Fuel temperature from the fuel tank temperature sensor."
    ),
    "oil_temperature_deg_c": "Engine oil temperature.",
    "stock_rpm": (
        "Engine speed in the stock frame 0x180: the same ECU measurement as "
        "Engine speed at 3.125 RPM per count, taken when the frame is "
        "serialized. It cross-checks the stock transmit path and is not an "
        "independent sensor."
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
    "engine_torque_state_nm": (
        "Signed engine torque state of the torque and throttle calibration "
        "path, candidate 0.1 Nm per count."
    ),
    "torque_request_nm": (
        "Bounded torque request that the electronic throttle serves: the "
        "pedal demand of table 0xE98E minus 0x8000, candidate 0.1 Nm per "
        "count. Transmission requests can bound it during gear changes."
    ),
    "throttle_area_request_cm2": (
        "Target opening area of both throttle bodies, candidate 0.0008 cm2 "
        "per count; the channel targets derive from it."
    ),
    "throttle_target_b1_v": (
        "Target of the bank 1 throttle position sensor above its learned "
        "closed position, in volts. In steady state it reads the TPS voltage "
        "minus the closed position."
    ),
    "throttle_target_b2_v": (
        "Target of the bank 2 throttle position sensor above its learned "
        "closed position, in volts. In steady state it reads the TPS voltage "
        "minus the closed position."
    ),
    "injection_end_angle_deg": (
        "End of injection in crank degrees after intake TDC of the injected "
        "cylinder. A firmware coordinate from the injection-end tables, not "
        "a measured injector event."
    ),
    "exhaust_cvtc_actual_b1_deg_ca": (
        "Measured exhaust camshaft position of bank 1 in crank degrees, from "
        "the phase of the cam sensor edges."
    ),
    "exhaust_cvtc_actual_b2_deg_ca": (
        "Measured exhaust camshaft position of bank 2 in crank degrees, from "
        "the phase of the cam sensor edges."
    ),
    "intake_cvtc_duty_command_b1_percent": (
        "Scheduler copy of the bank 1 intake valve timing solenoid duty, in "
        "percent. Every profile 5 recording holds it equal to the live duty."
    ),
    "intake_cvtc_duty_command_b2_percent": (
        "Scheduler copy of the bank 2 intake valve timing solenoid duty, in "
        "percent. Every profile 5 recording holds it equal to the live duty."
    ),
    "exhaust_cvtc_duty_b1_word_percent": (
        "Duty of the bank 1 exhaust valve timing solenoid, in percent."
    ),
    "exhaust_cvtc_duty_b2_word_percent": (
        "Duty of the bank 2 exhaust valve timing solenoid, in percent."
    ),
    "ltft_learned_b1_percent": (
        "Learned long-term trim cell of bank 1 for the current operating "
        "region, in percent. LTFT bank 1 is this cell plus the adjustment."
    ),
    "ltft_adjustment_b1_percent": (
        "Running adjustment of the bank 1 long-term trim, in percent."
    ),
    "af_adjustment_b1": (
        "A/F adjustment of bank 1: the signed correction that the ECU "
        "integrates from the difference between the target mixture and the "
        "A/F sensor 1 mixture, bounded to -500..500 counts. The candidate "
        "factor 0.002 maps the factory running range to -0.33..0.33. Every "
        "recording so far reads 0."
    ),
    "af_adjustment_b2": (
        "A/F adjustment of bank 2: the signed correction that the ECU "
        "integrates from the difference between the target mixture and the "
        "A/F sensor 1 mixture, bounded to -500..500 counts. The candidate "
        "factor 0.002 maps the factory running range to -0.33..0.33. Every "
        "recording so far reads 0."
    ),
    "battery_voltage_v": "Battery voltage at the ECU supply.",
    "secondary_tps_b1_v": (
        "Throttle position sensor 2 of the bank 1 throttle body in volts, "
        "the second track that the ECU checks against sensor 1; it rises "
        "with opening."
    ),
    "secondary_tps_b2_v": (
        "Throttle position sensor 2 of the bank 2 throttle body in volts, "
        "the second track that the ECU checks against sensor 1; it rises "
        "with opening."
    ),
    "protocol_version": (
        "Telemetry protocol version that the ECU reports in the health "
        "context. Values are converted only when it matches the bundled "
        "schema."
    ),
    "profile_crc16": (
        "CRC16 of the wire layout that the ECU reports in the health "
        "context. Values are converted only when it equals the CRC of the "
        "bundled profile, because another layout carries other quantities "
        "in the same slots."
    ),
}


def describe(key):
    """Return the description of a metric key, or an empty string."""
    return DESCRIPTIONS.get(key, "")
