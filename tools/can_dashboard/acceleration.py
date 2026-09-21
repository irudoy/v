"""Time 0-100 and 100-200 km/h runs from the stock vehicle speed.

The speed is the ABS value of frame 0x280, which reads 0 below about
1.5 km/h. A 0-100 run is armed at standstill and starts at the first sample
above zero; a 100-200 run is armed below 97 km/h and starts where the speed
crosses 100 km/h. Each run ends where the speed crosses its end speed, both
crossings interpolated linearly between the samples around them. A run that
returns to standstill, loses more than 2 km/h from its peak, gains no speed
for 2 s, exceeds its time limit, or meets a gap in the samples is discarded.
"""

from __future__ import annotations

from dataclasses import dataclass


DROP_KMH = 2.0
STALL_SECONDS = 2.0
MAX_SAMPLE_GAP_SECONDS = 0.5


@dataclass(frozen=True)
class RunResult:
    seconds: float
    finished_at: float


def _crossing(previous, current, speed):
    (time0, speed0), (time1, speed1) = previous, current
    if speed1 == speed0:
        return time1
    return time0 + (speed - speed0) * (time1 - time0) / (speed1 - speed0)


class SpeedRun:
    """Time one speed interval, keeping the last and the best result."""

    def __init__(self, name, start_kmh, end_kmh, arm_below_kmh, max_seconds):
        self.name = name
        self.start_kmh = start_kmh
        self.end_kmh = end_kmh
        self.arm_below_kmh = arm_below_kmh
        self.max_seconds = max_seconds
        self.state = "idle"
        self.started_at = None
        self.now = None
        self.last = None
        self.best = None
        self._sample = None
        self._peak = None
        self._peak_at = None

    def _armed_by(self, kmh):
        if self.start_kmh == 0:
            return kmh <= 0
        return kmh < self.arm_below_kmh

    def _idle(self, kmh):
        self.started_at = None
        self.state = "armed" if self._armed_by(kmh) else "idle"

    def _start(self, time, started_at, kmh):
        self.state = "running"
        self.started_at = started_at
        self._peak = kmh
        self._peak_at = time

    def elapsed(self):
        """Seconds of the running run up to its latest sample, else None."""
        if self.state != "running" or self.now is None:
            return None
        return max(0.0, self.now - self.started_at)

    def reset_results(self):
        self.last = None
        self.best = None

    def update(self, time, kmh):
        previous = self._sample
        current = (time, kmh)
        self._sample = current
        self.now = time
        if previous is not None and not (
            0.0 <= time - previous[0] <= MAX_SAMPLE_GAP_SECONDS
        ):
            previous = None
            self._idle(kmh)
            return
        if self.state == "running":
            if self.start_kmh == 0 and kmh <= 0:
                self._idle(kmh)
                return
            if kmh > self._peak:
                self._peak = kmh
                self._peak_at = time
            elif (
                self._peak - kmh > DROP_KMH
                or time - self._peak_at > STALL_SECONDS
            ):
                self._idle(kmh)
                return
            if time - self.started_at > self.max_seconds:
                self._idle(kmh)
                return
            if previous is not None and previous[1] < self.end_kmh <= kmh:
                finished = _crossing(previous, current, self.end_kmh)
                result = RunResult(finished - self.started_at, finished)
                self.last = result
                if self.best is None or result.seconds < self.best.seconds:
                    self.best = result
                self._idle(kmh)
            return
        if self.state == "idle":
            self._idle(kmh)
            return
        if self.start_kmh == 0:
            if kmh > 0:
                self._start(time, time, kmh)
        elif previous is not None and previous[1] < self.start_kmh <= kmh:
            self._start(time, _crossing(previous, current, self.start_kmh), kmh)


class AccelerationTimer:
    """Run the 0-100 and 100-200 km/h timers on one speed stream."""

    def __init__(self):
        self.runs = (
            SpeedRun("0-100", 0.0, 100.0, 0.0, 30.0),
            SpeedRun("100-200", 100.0, 200.0, 97.0, 60.0),
        )

    def speed(self, time, kmh):
        for run in self.runs:
            run.update(time, kmh)

    def reset_results(self):
        for run in self.runs:
            run.reset_results()

    def run(self, name):
        for run in self.runs:
            if run.name == name:
                return run
        raise KeyError(name)
