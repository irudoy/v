import unittest

from tools.can_dashboard.acceleration import AccelerationTimer


STEP = 0.02


def drive(timer, profile, start=0.0, stop=None):
    """Feed speed(time) every 20 ms from start to stop; return the end time."""
    time = start
    while stop is None or time <= stop + 1e-9:
        speed = profile(time)
        if speed is None:
            break
        timer.speed(time, speed)
        time = round(time + STEP, 6)
    return time


def ramp(start_time, start_kmh, rate, top=None):
    def profile(time):
        if time < start_time:
            return start_kmh if start_kmh > 0 else 0.0
        speed = start_kmh + rate * (time - start_time)
        return speed if top is None else min(speed, top)

    return profile


class AccelerationTimerTest(unittest.TestCase):
    def test_zero_to_100_starts_moving_and_ends_at_the_crossing(self):
        timer = AccelerationTimer()
        drive(timer, ramp(1.0, 0.0, 12.5), stop=10.0)
        run = timer.run("0-100")
        self.assertAlmostEqual(run.last.seconds, 9.0 - 1.02, places=6)
        self.assertAlmostEqual(run.last.finished_at, 9.0, places=6)
        self.assertEqual(run.best, run.last)
        self.assertIsNone(timer.run("100-200").last)

    def test_hundred_to_200_is_timed_between_the_crossings(self):
        timer = AccelerationTimer()
        drive(timer, ramp(0.0, 90.0, 5.0), stop=25.0)
        run = timer.run("100-200")
        self.assertAlmostEqual(run.last.seconds, 20.0, places=6)
        self.assertAlmostEqual(run.last.finished_at, 22.0, places=6)
        self.assertIsNone(timer.run("0-100").last)

    def test_the_running_time_is_reported_until_the_end(self):
        timer = AccelerationTimer()
        drive(timer, ramp(1.0, 0.0, 12.5), stop=5.0)
        run = timer.run("0-100")
        self.assertEqual(run.state, "running")
        self.assertAlmostEqual(run.elapsed(), 5.0 - 1.02, places=6)
        self.assertIsNone(run.last)

    def test_best_keeps_the_fastest_run_and_reset_clears_both(self):
        timer = AccelerationTimer()
        time = drive(timer, ramp(1.0, 0.0, 10.0), stop=12.0)

        def slow_down(now):
            speed = 110.0 - 1.5 * (now - time)
            return max(0.0, speed)

        time = drive(timer, slow_down, start=time, stop=time + 80.0)
        drive(timer, ramp(time + 1.0, 0.0, 12.5), start=time, stop=time + 10.0)
        run = timer.run("0-100")
        self.assertAlmostEqual(run.last.seconds, 8.0 - STEP, places=6)
        self.assertAlmostEqual(run.best.seconds, 8.0 - STEP, places=6)
        timer.reset_results()
        self.assertIsNone(run.last)
        self.assertIsNone(run.best)

    def test_a_drop_below_the_peak_discards_the_run(self):
        timer = AccelerationTimer()

        def lift(time):
            if time < 1.0:
                return 0.0
            if time < 5.0:
                return 12.5 * (time - 1.0)
            if time < 5.5:
                return 50.0 - 6.0 * (time - 5.0)
            return 47.0 + 12.5 * (time - 5.5)

        drive(timer, lift, stop=12.0)
        run = timer.run("0-100")
        self.assertIsNone(run.last)
        self.assertEqual(run.state, "idle")

    def test_a_stall_discards_the_run(self):
        timer = AccelerationTimer()
        drive(timer, ramp(1.0, 0.0, 12.5, top=40.0), stop=9.0)
        run = timer.run("0-100")
        self.assertEqual(run.state, "idle")
        self.assertIsNone(run.last)

    def test_a_gap_in_the_samples_discards_the_run(self):
        timer = AccelerationTimer()
        profile = ramp(1.0, 0.0, 12.5)
        drive(timer, profile, stop=3.0)
        drive(timer, profile, start=3.6, stop=10.0)
        run = timer.run("0-100")
        self.assertIsNone(run.last)

    def test_a_return_to_standstill_rearms_the_zero_to_100_run(self):
        timer = AccelerationTimer()

        def creep(time):
            if time < 1.0:
                return 0.0
            if time < 2.0:
                return 1.5
            if time < 3.0:
                return 0.0
            return 12.5 * (time - 3.0)

        drive(timer, creep, stop=12.0)
        run = timer.run("0-100")
        self.assertAlmostEqual(run.last.seconds, 11.0 - 3.02, places=6)


if __name__ == "__main__":
    unittest.main()
