import hashlib
from pathlib import Path
import struct
import tempfile
import unittest

from tools.can_dashboard import recording
from tools.logs import ltft_publication_audit as audit
from tools.logs import mlvlg
from tools.mapkit import rom as romkit


NEUTRAL = audit.NEUTRAL
FIRST_TICK = 100
LAST_TICK = 159
ELAPSED_ORIGIN = FIRST_TICK - 1
WARM_TICK = 121
BRIDGE_TICK = 130
PUBLISHED_RESIDUE = 3
STFT = 26880
CELL_BFS = 0x3000
CELL_RPM_RAW = 180
FORCED_NEUTRAL_TICK = 128
HIGH_RPM_TICK = 150
HIGH_RPM_RAW = 200
HIGH_RPM_INHIBIT_TICK = 155
OTHER_TICK = 148
OTHER_WORD = 26000


def learned_at(tick):
    if tick < 120:
        return NEUTRAL
    if tick < 140:
        return NEUTRAL + 100
    return NEUTRAL + 1100


def last_refresh(tick, residue):
    return tick - (tick - residue) % audit.TAG_COUNT


def synthetic_row(tick):
    """Return retained MLG values of one snapshot of the modeled producer."""
    learned_tick = last_refresh(tick, (PUBLISHED_RESIDUE - 2) % audit.TAG_COUNT)
    published_tick = last_refresh(tick, PUBLISHED_RESIDUE)
    published = learned_at(published_tick)
    if published_tick == FORCED_NEUTRAL_TICK:
        published = NEUTRAL
    elif published_tick == OTHER_TICK:
        published = OTHER_WORD
    rpm = HIGH_RPM_RAW if tick >= HIGH_RPM_TICK else CELL_RPM_RAW
    return {
        "tick16": tick,
        "schema_verified": 1,
        "front_af_sensor_b1_word_raw": published_tick,
        "ltft_learned_b1_raw": learned_at(learned_tick),
        "ltft_adjustment_b1_raw": NEUTRAL,
        "ltft_b1_raw": published,
        "ltft_b2_raw": NEUTRAL,
        "coolant_raw": 125 if learned_tick >= 120 else 110,
        "stft_b1_raw": STFT,
        "stft_b2_raw": NEUTRAL,
        "bfs_raw": CELL_BFS,
        "rpm_raw": rpm,
        # The stock engine-speed frame of the snapshot's pass.
        "stock_rpm": rpm * 12.5,
        "gear_raw": audit.GEAR_D if tick < 140 else audit.GEAR_P,
        "vehicle_speed_kmh": 90.0 if tick < 140 else 0.0,
        "fuel_inhibit_mask": (
            audit.FULL_FUEL_INHIBIT_MASK
            if 110 <= tick <= 112 or tick == HIGH_RPM_INHIBIT_TICK
            else 0
        ),
    }


def write_log(path, pause_tick=None, pause_seconds=0.0):
    """Write the synthetic MLG; a pause holds the tick for pause_seconds."""
    bindings = recording.build_bindings("tuning")
    specs = [binding.spec for binding in bindings]
    rows = [dict(synthetic_row(FIRST_TICK - 1), schema_verified=0)]
    for tick in range(FIRST_TICK, LAST_TICK + 1):
        rows.append(synthetic_row(tick))
        if tick == BRIDGE_TICK:
            rows.append(synthetic_row(tick))
    with Path(path).open("wb") as stream:
        writer = mlvlg.StreamWriter(stream, specs, 1_789_600_000)
        for values in rows:
            elapsed = (values["tick16"] - ELAPSED_ORIGIN) * audit.TICK_SECONDS
            if pause_tick is not None and values["tick16"] >= pause_tick:
                elapsed += pause_seconds
            row = []
            for binding in bindings:
                if binding.source == "date":
                    row.append(1_789_600_000)
                elif binding.source == "elapsed":
                    row.append(elapsed)
                else:
                    row.append(values.get(binding.source, 0))
            writer.write(row, elapsed)
    return len(rows)


def snapshots_from(rows):
    columns = {name: [row.get(name) for row in rows] for name in audit.COLUMNS}
    columns["rpm_raw"] = [row.get("rpm_raw") for row in rows]
    columns["elapsed"] = [
        (row["tick16"] - FIRST_TICK) * audit.TICK_SECONDS for row in rows
    ]
    columns["date"] = [0.0 for _row in rows]
    return audit.Snapshots(
        Path("synthetic.mlg"),
        "0" * 64,
        len(rows),
        0,
        0,
        tuple(row["tick16"] for row in rows),
        columns,
    )


class LtftPublicationAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calibration = audit.load_calibration()
        cls.rows = [synthetic_row(tick) for tick in range(FIRST_TICK, LAST_TICK + 1)]

    def test_constants_are_read_from_the_registered_image(self):
        calibration = self.calibration
        image = romkit.load("JK08A")
        self.assertEqual(calibration.image_sha256, hashlib.sha256(image.data).hexdigest())
        self.assertEqual(
            (calibration.publication_low, calibration.publication_high),
            (90 << 8, 110 << 8),
        )
        self.assertEqual((calibration.cell_low, calibration.cell_high), (90 << 8, 110 << 8))
        self.assertEqual(calibration.coolant_threshold_raw, 120)
        self.assertEqual(calibration.gains, (26, 26, 16))
        self.assertEqual(calibration.first_visit_gain, 26)
        self.assertEqual(
            calibration.bfs_axis, (0x00, 0x15, 0x1D, 0x28, 0x40, 0x58, 0x70, 0x80)
        )
        self.assertEqual(calibration.rpm_axis, (0, 20, 30, 44, 68, 88, 108, 128))
        self.assertEqual((calibration.bfs_hysteresis, calibration.rpm_hysteresis), (4, 1))

    def test_maf_summary_gate_matches_the_rom(self):
        data = romkit.load("JK08A").data

        def word(address):
            return struct.unpack_from(">H", data, address)[0]

        def literal(address):
            return struct.unpack_from(">I", data, (address & ~3) + 4 + 4 * (word(address) & 0xFF))[0]

        # FUN 0004F736: 0xFFFF2448.bit7 set and uint8[0xFFFF119C + 22] >= 0xC0.
        self.assertEqual(literal(0x4F736), 0xFFFF2448)
        self.assertEqual(word(0x4F73A), 0xC880)
        self.assertEqual(literal(0x4F73E), 0xFFFF119C)
        self.assertEqual(word(0x4F740), 0xE016)
        self.assertEqual(word(0x4F744), 0xE600 | ((audit.MAF_SUMMARY_RPM_RAW - 256) & 0xFF))
        self.assertEqual(word(0x4F746), 0x666C)
        self.assertEqual(word(0x4F74A), 0x3263)

    def test_selector_follows_axes_and_hysteresis(self):
        select = audit.select_cell
        calibration = self.calibration
        self.assertEqual(select(calibration, CELL_BFS, CELL_RPM_RAW >> 2, None), 27)
        # Row 0 column boundary 0x15 << 8 with a band of 4 << 8 on each side.
        self.assertEqual(select(calibration, 5000, 12, None), 0)
        self.assertEqual(select(calibration, 5000, 12, 1), 1)
        self.assertEqual(select(calibration, 4352, 12, 1), 0)
        self.assertEqual(select(calibration, 6399, 12, 0), 0)
        self.assertEqual(select(calibration, 6400, 12, 0), 1)
        # Rising into row 3 needs one count above the 44 boundary.
        self.assertEqual(select(calibration, CELL_BFS, 44, 19), 19)
        self.assertEqual(select(calibration, CELL_BFS, 45, 19), 27)
        self.assertEqual(select(calibration, CELL_BFS, 43, 27), 19)

    def test_refresh_phase_requires_one_residue(self):
        snapshots = snapshots_from(self.rows)
        phase = audit.refresh_phase(snapshots)
        self.assertEqual(phase[audit.PUBLISHED_TAG], PUBLISHED_RESIDUE)
        self.assertEqual(phase[audit.LEARNED_TAG], PUBLISHED_RESIDUE - 2)
        rows = [dict(row) for row in self.rows]
        rows[10]["front_af_sensor_b1_word_raw"] = -1
        with self.assertRaises(ValueError):
            audit.refresh_phase(snapshots_from(rows))

    def test_publication_relation_separates_brackets(self):
        snapshots = snapshots_from(self.rows)
        phase = audit.refresh_phase(snapshots)
        relation = audit.publication_relation(snapshots, phase, self.calibration)
        self.assertEqual(relation["bracketed"], 9)
        self.assertEqual(relation["exact"], 7)
        self.assertEqual(relation["nonneutral_exact"], 4)
        self.assertEqual(relation["forced_neutral"], 1)
        self.assertEqual(relation["other"], 1)
        self.assertEqual(relation["transition"], 2)
        self.assertEqual(relation["transition_bracket"], 2)
        self.assertEqual(relation["unbracketed"], 1)
        self.assertEqual(
            audit.published_value(self.calibration, 28000, 26000), 110 << 8
        )

    def test_learning_changes_respect_the_update_bound(self):
        snapshots = snapshots_from(self.rows)
        phase = audit.refresh_phase(snapshots)
        changes = audit.learning_changes(snapshots, phase, self.calibration)
        self.assertEqual(changes["update_bound"], ((STFT - NEUTRAL) * 26) >> 8)
        self.assertEqual(changes["learned_pair_count"], 11)
        self.assertEqual(changes["learned_change_count"], 2)
        self.assertEqual(changes["gear_p_learned_pair_count"], 3)
        self.assertEqual(changes["gear_p_learned_change_count"], 0)
        self.assertEqual(changes["in_visit_change_count"], 2)
        self.assertEqual(changes["in_visit_update_count"], 1)
        self.assertEqual(changes["in_visit_over_bound_count"], 1)
        self.assertEqual(changes["row_0_update_count"], 0)
        self.assertEqual(changes["update_stft_sign_agreement_count"], 1)

    def test_audit_reads_a_synthetic_mlg(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.mlg"
            records = write_log(path)
            result = audit.audit(path, self.calibration)
        self.assertEqual(result["record_count"], records)
        self.assertEqual(result["unverified_record_count"], 1)
        self.assertEqual(result["bridge_record_count"], 1)
        self.assertEqual(result["snapshot_count"], LAST_TICK - FIRST_TICK + 1)
        self.assertEqual(result["learned_tag_residue"], PUBLISHED_RESIDUE - 2)
        self.assertEqual(result["adjustment_b1_neutral_count"], 12)
        self.assertEqual(result["relation_exact_count"], 7)
        self.assertEqual(
            result["relation_bracketed_count"] + result["relation_transition_count"],
            result["learned_pair_count"],
        )
        self.assertEqual(
            result["warm_elapsed_seconds"],
            round((WARM_TICK - ELAPSED_ORIGIN) * audit.TICK_SECONDS, 3),
        )
        self.assertEqual(
            result["warm_capture_seconds"],
            round((LAST_TICK - WARM_TICK + 1) * audit.TICK_SECONDS, 3),
        )
        self.assertEqual(
            result["warm_fueled_above_maf_gate_count"], LAST_TICK - HIGH_RPM_TICK
        )
        self.assertEqual(result["longest_gear_d_seconds"], round(40 * audit.TICK_SECONDS, 3))
        self.assertEqual(result["speed_band_seconds"], round(40 * audit.TICK_SECONDS, 3))
        self.assertEqual(result["speed_band_interval_count"], 1)
        self.assertEqual(result["final_gear_p_seconds"], round(20 * audit.TICK_SECONDS, 3))
        self.assertEqual(result["final_gear_p_stft_b1_median_raw"], STFT)
        self.assertEqual(result["warm_gear_p_seconds"], round(20 * audit.TICK_SECONDS, 3))
        self.assertEqual(result["gear_d_full_fuel_inhibit_interval_count"], 1)

    def test_a_stream_pause_keeps_its_time_and_splits_intervals(self):
        pause_tick = 125
        pause = 5.0
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.mlg"
            write_log(path)
            running = audit.audit(path, self.calibration)
            write_log(path, pause_tick, pause)
            paused = audit.audit(path, self.calibration)
            snapshots = audit.read_snapshots(path)
        index = snapshots.ticks.index(pause_tick)
        self.assertFalse(snapshots.contiguous(index))
        self.assertTrue(snapshots.contiguous(index + 1))
        self.assertEqual(
            paused["warm_capture_seconds"],
            round((LAST_TICK - WARM_TICK + 1) * audit.TICK_SECONDS + pause, 3),
        )
        self.assertEqual(
            paused["longest_gear_d_seconds"],
            round((pause_tick - FIRST_TICK) * audit.TICK_SECONDS, 3),
        )
        self.assertEqual(paused["speed_band_interval_count"], 2)
        self.assertEqual(paused["speed_band_seconds"], running["speed_band_seconds"])
        # The tag-0 pair across the pause compares values that are not five
        # snapshots apart in time.
        self.assertEqual(
            paused["learned_pair_count"], running["learned_pair_count"] - 1
        )


if __name__ == "__main__":
    unittest.main()
