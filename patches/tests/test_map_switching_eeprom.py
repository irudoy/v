"""Unit tests for the Map Switching two-copy ping-pong EEPROM persistence model."""

from __future__ import annotations

import unittest
import zlib

from patches import map_switching_eeprom as ee


class RecordAndRecoveryTest(unittest.TestCase):
    def test_mspe_config_codec_round_trip_and_rejection(self):
        cfg = ee.EepromPersistenceConfig()
        raw = cfg.to_bytes()
        self.assertEqual(len(raw), ee.EEPROM_CONFIG_SIZE)
        self.assertEqual(ee.EepromPersistenceConfig.from_bytes(raw), cfg)
        disabled = ee.EepromPersistenceConfig(
            flags=0, write_delay_ticks=75, wip_timeout_ticks=8, max_retries_per_slot=3
        )
        self.assertFalse(disabled.enabled)
        self.assertEqual(
            ee.EepromPersistenceConfig.from_bytes(disabled.to_bytes()), disabled
        )
        for bad in (
            b"XXXX" + raw[4:],
            raw[:4] + b"\x02" + raw[5:],
            raw[:5] + b"\x02" + raw[6:],
            raw[:10] + b"\x00\x01" + raw[12:],
            raw[:12] + b"\x00\x00\x00\x00",
        ):
            with self.assertRaises(ValueError):
                ee.EepromPersistenceConfig.from_bytes(bad)

    def test_crc32_matches_zlib(self):
        for payload in (b"", b"MS\x01\x01\x00\x00\x00\x00", b"MS\x01\x05\xff\xff\xff\xff"):
            self.assertEqual(ee.crc32_ieee(payload), zlib.crc32(payload) & 0xFFFFFFFF)

    def test_erased_pages_fall_back_to_map_1(self):
        dev = ee.M95320Device()
        res = ee.recover_eeprom(dev.memory)
        self.assertEqual(res.active_page, ee.PAGE_NONE)
        self.assertEqual(res.slot, 1)
        self.assertEqual(res.generation, 0)
        self.assertFalse(res.ambiguous)

    def test_generation_rollover_and_ambiguity(self):
        for gen_a, gen_b, expected_page, expected_slot, expected_ambig in (
            (0, 1, ee.PAGE_INDEX_B, 3, False),
            (1, 0, ee.PAGE_INDEX_A, 2, False),
            (0xFFFFFFFF, 0, ee.PAGE_INDEX_B, 3, False),
            (0, 0xFFFFFFFF, ee.PAGE_INDEX_A, 2, False),
            (17, 17, ee.PAGE_NONE, 1, True),
            (17, 17 + 0x80000000, ee.PAGE_NONE, 1, True),
        ):
            page_a = ee.PersistenceRecord(2, gen_a).page_bytes()
            page_b = ee.PersistenceRecord(3, gen_b).page_bytes()
            res = ee.recover_pages(page_a, page_b)
            self.assertEqual(res.active_page, expected_page)
            self.assertEqual(res.slot, expected_slot)
            self.assertEqual(res.ambiguous, expected_ambig)

    def test_single_bit_corruption_invalidates_record(self):
        rec = ee.PersistenceRecord(4, 99).record_bytes()
        for byte_index in range(ee.RECORD_SIZE):
            for bit in range(8):
                corrupted = bytearray(rec)
                corrupted[byte_index] ^= 1 << bit
                self.assertIsNone(ee.decode_record(bytes(corrupted)))

    def test_upper_page_bytes_16_to_31_preserved(self):
        dev = ee.M95320Device()
        dev.memory[ee.PAGE_A_ADDRESS + 16:ee.PAGE_A_ADDRESS + 32] = bytes(range(16, 32))
        dev.memory[ee.PAGE_B_ADDRESS + 16:ee.PAGE_B_ADDRESS + 32] = bytes(range(32, 48))
        state = ee.PersistenceState()
        self.assertEqual(ee.boot_restore(dev, state), 0)
        for _ in range(30):
            ee.step_persistence(dev, state, active_slot_index=2, write_delay_ticks=3)
        self.assertEqual(state.committed_slot, 3)
        self.assertEqual(
            bytes(dev.memory[ee.PAGE_A_ADDRESS + 16:ee.PAGE_A_ADDRESS + 32]),
            bytes(range(16, 32)),
        )
        self.assertEqual(
            bytes(dev.memory[ee.PAGE_B_ADDRESS + 16:ee.PAGE_B_ADDRESS + 32]),
            bytes(range(32, 48)),
        )


class SteppedWriterTest(unittest.TestCase):
    def _run_until_idle(self, dev, state, slot_index, *, max_ticks=60, **kwargs):
        for _ in range(max_ticks):
            ee.step_persistence(dev, state, active_slot_index=slot_index, **kwargs)
            if state.phase == ee.PHASE_IDLE and state.committed_slot == slot_index + 1:
                return
        self.fail(f"writer did not settle to slot {slot_index + 1}: {state}")

    def test_ping_pong_cycle_debounce_and_redundant_skip(self):
        dev = ee.M95320Device(wip_polls_per_write=2)
        state = ee.PersistenceState()
        self.assertEqual(ee.boot_restore(dev, state), 0)

        # Rapid cycling 2 -> 3 -> 4 resets debounce and performs a single write for slot 4.
        for slot_idx in (1, 2, 3):
            ee.step_persistence(dev, state, active_slot_index=slot_idx, write_delay_ticks=4)
            self.assertEqual(state.phase, ee.PHASE_IDLE)
        self._run_until_idle(dev, state, 3, write_delay_ticks=4)
        self.assertEqual(state.write_count, 1)
        self.assertEqual(state.active_page, ee.PAGE_INDEX_A)
        self.assertEqual(state.active_generation, 0)

        # Selecting the same slot again schedules no write.
        for _ in range(20):
            ee.step_persistence(dev, state, active_slot_index=3, write_delay_ticks=2)
        self.assertEqual(state.write_count, 1)

        # Switching to slot 2 writes to page B with generation 1.
        self._run_until_idle(dev, state, 1, write_delay_ticks=2)
        self.assertEqual(state.write_count, 2)
        self.assertEqual(state.active_page, ee.PAGE_INDEX_B)
        self.assertEqual(state.active_generation, 1)

        # Boot restore recovers slot 2 (index 1).
        reboot = ee.PersistenceState()
        self.assertEqual(ee.boot_restore(dev, reboot), 1)
        self.assertEqual(reboot.active_page, ee.PAGE_INDEX_B)
        self.assertEqual(reboot.committed_slot, 2)
        self.assertEqual(reboot.active_generation, 1)

    def test_power_loss_between_phases_preserves_previous_slot(self):
        dev = ee.M95320Device(wip_polls_per_write=0)
        state = ee.PersistenceState()
        ee.boot_restore(dev, state)
        self._run_until_idle(dev, state, 2, write_delay_ticks=1)
        self.assertEqual(ee.recover_eeprom(dev.memory).slot, 3)

        # Advance phase by phase towards slot 5 and reboot after each intermediate phase.
        base_mem = bytearray(dev.memory)
        for stop_phase in (ee.PHASE_WAIT_INVAL, ee.PHASE_WAIT_BODY):
            sim_dev = ee.M95320Device(memory=bytearray(base_mem), wip_polls_per_write=0)
            sim_state = ee.PersistenceState()
            ee.boot_restore(sim_dev, sim_state)
            for _ in range(10):
                ee.step_persistence(sim_dev, sim_state, active_slot_index=4, write_delay_ticks=1)
                if sim_state.phase == stop_phase:
                    break
            self.assertEqual(sim_state.phase, stop_phase)
            # Simulated power loss right here: previous committed page A must still win.
            reboot_state = ee.PersistenceState()
            self.assertEqual(ee.boot_restore(sim_dev, reboot_state), 2)
            self.assertEqual(reboot_state.active_page, ee.PAGE_INDEX_A)

    def test_inhibit_stock_busy_and_retry_bound(self):
        dev = ee.M95320Device(bp_bits=3, wip_polls_per_write=0)
        state = ee.PersistenceState()
        ee.boot_restore(dev, state)

        # Stock busy or inhibit blocks starting a write.
        for _ in range(10):
            ee.step_persistence(dev, state, active_slot_index=2, stock_busy=True, write_delay_ticks=1)
            ee.step_persistence(dev, state, active_slot_index=2, inhibited=True, write_delay_ticks=1)
        self.assertEqual(state.phase, ee.PHASE_IDLE)
        self.assertEqual(state.retry_count, 0)

        # Whole-array write protection fails verify and stops after max_retries_per_slot.
        for _ in range(40):
            ee.step_persistence(
                dev, state, active_slot_index=2, write_delay_ticks=1, max_retries_per_slot=2
            )
        self.assertEqual(state.phase, ee.PHASE_IDLE)
        self.assertEqual(state.last_error, ee.ERR_VERIFY_INVAL)
        self.assertEqual(state.retry_count, 2)
        self.assertEqual(state.write_count, 0)

    def test_wip_timeout_and_ambiguous_lockout(self):
        dev = ee.M95320Device(wip_polls_per_write=100)
        state = ee.PersistenceState()
        ee.boot_restore(dev, state)
        for _ in range(20):
            ee.step_persistence(
                dev, state, active_slot_index=1, write_delay_ticks=1, wip_timeout_ticks=3
            )
        self.assertEqual(state.last_error, ee.ERR_WIP_TIMEOUT)
        self.assertEqual(state.phase, ee.PHASE_QUARANTINE)
        # Clear WIP with WEL still latched: quarantine issues WRDI and requires
        # a subsequent fresh RDSR confirming WIP==0 && WEL==0 before IDLE.
        dev.wip_remaining = 0
        dev.wel = True
        ee.step_persistence(dev, state, active_slot_index=1, write_delay_ticks=1)
        self.assertFalse(dev.wel)
        self.assertEqual(state.phase, ee.PHASE_QUARANTINE)
        ee.step_persistence(dev, state, active_slot_index=1, write_delay_ticks=1)
        self.assertEqual(state.phase, ee.PHASE_IDLE)

        # Equal generation ambiguity falls back to Map 1 and inhibits all writes.
        ambig_dev = ee.M95320Device()
        ambig_dev.memory[ee.PAGE_A_ADDRESS:ee.PAGE_A_ADDRESS + 32] = ee.PersistenceRecord(2, 5).page_bytes()
        ambig_dev.memory[ee.PAGE_B_ADDRESS:ee.PAGE_B_ADDRESS + 32] = ee.PersistenceRecord(4, 5).page_bytes()
        ambig_state = ee.PersistenceState()
        self.assertEqual(ee.boot_restore(ambig_dev, ambig_state), 0)
        self.assertTrue(ambig_state.boot_ambiguous)
        before = bytes(ambig_dev.memory)
        for _ in range(20):
            ee.step_persistence(ambig_dev, ambig_state, active_slot_index=3, write_delay_ticks=1)
        self.assertEqual(bytes(ambig_dev.memory), before)

    def test_v1_backward_compat_and_v2_telemetry_autostart_round_trip(self):
        dev = ee.M95320Device(wip_polls_per_write=1)
        # Legacy v1 record boots with autostart disabled and saved=True.
        dev.memory[ee.PAGE_A_ADDRESS:ee.PAGE_A_ADDRESS + 32] = ee.PersistenceRecord(
            3, 7, version=1
        ).page_bytes()
        state = ee.PersistenceState()
        self.assertEqual(ee.boot_restore(dev, state), 2)
        self.assertFalse(state.committed_autostart)
        self.assertFalse(state.autostart_enabled)
        self.assertTrue(state.autostart_saved)

        # Toggling autostart on writes a v2 record on page B without changing map slot.
        for _ in range(30):
            ee.step_persistence(
                dev, state, active_slot_index=2, telemetry_autostart=True, write_delay_ticks=2
            )
            if state.phase == ee.PHASE_IDLE and state.committed_autostart:
                break
        self.assertTrue(state.committed_autostart)
        self.assertTrue(state.autostart_saved)
        self.assertEqual(state.active_page, ee.PAGE_INDEX_B)

        # Warm sync restores desired and saved bits after telemetry RAM clear.
        self.assertEqual(ee.warm_sync(state), (True, True))
        state.pending_slot = 3
        state.pending_autostart = False
        self.assertEqual(ee.warm_sync(state), (False, False))

        # Cold reboot recovers slot 3 and autostart=True from v2 record.
        reboot = ee.PersistenceState()
        self.assertEqual(ee.boot_restore(dev, reboot), 2)
        self.assertTrue(reboot.committed_autostart)
        self.assertTrue(reboot.autostart_enabled)
        self.assertTrue(reboot.autostart_saved)

        # Reserved v2 bits (0x70) and v1 autostart bit (0x80) are rejected.
        bad_v2 = bytearray(ee.PersistenceRecord(3, 9, telemetry_autostart=True).record_bytes())
        bad_v2[3] = 0x13
        bad_v2[8:12] = ee.crc32_ieee(bytes(bad_v2[:8])).to_bytes(4, "big")
        self.assertIsNone(ee.decode_record(bytes(bad_v2)))

        bad_v1 = bytearray(ee.PersistenceRecord(3, 9, version=1).record_bytes())
        bad_v1[3] = 0x83
        bad_v1[8:12] = ee.crc32_ieee(bytes(bad_v1[:8])).to_bytes(4, "big")
        self.assertIsNone(ee.decode_record(bytes(bad_v1)))


if __name__ == "__main__":
    unittest.main()
