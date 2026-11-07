"""Follow the active map of the map-switching runtime from the stock bus.

The runtime keeps a zero-based active index that its startup wrapper resets to
Map 1 at every controller start. A committed selection queues one state-4
pulse per map number on the ASCD display state of frame 0x551, and selector
input stays blocked until the queue is empty. The telemetry profile carries
the index, and the dashboard model takes the map from it. Until a verified
stream publishes the index, the tracker establishes the map from two
observations:

- a controller start: a telemetry run that opens after a silent bus, or a
  tick16 reset inside an observed stream;
- a selector gesture on frame 0x239 that the runtime confirms with exactly as
  many pulses as the gesture counted.

Everything else leaves the map it knew. A selection whose pulses do not match
the gesture, or that the tracker cannot count, makes the map unknown.
"""

from __future__ import annotations

from dataclasses import dataclass

from tools.logs.can_telemetry import (
    PRODUCER_RUN_TICK_MAX, TickStep, receive_gap, tick_step,
)


MAP_COUNT = 5
BUTTON_RELEASED = 0x20
BUTTON_SET = 0x08
BUTTON_CANCEL = 0x02
DISPLAY_STATE_ON = 4
DISPLAY_STATE_OFF = 0
# Recorded commits show the first ON phase 70 to 110 ms after SET is released.
# Each phase lasts 20 serializer invocations, about 205 ms, which frame 0x551
# carries in two transmissions 102.4 ms apart.
FEEDBACK_START_SECONDS = 0.6
FEEDBACK_PHASE_MAX_SECONDS = 0.45
FEEDBACK_END_SECONDS = 0.45
# A bus without any frame for this long has lost the controller; the next
# telemetry run that opens in its first tick16 window follows a start.
BUS_SILENCE_SECONDS = 1.0
UNKNOWN_REASON = "no controller start or confirmed selection observed"


def display_state(code):
    """Return the three-bit ASCD display state of 0x551 byte 5."""
    return (code >> 4) & 0x07


@dataclass(frozen=True)
class SelectionObservation:
    requested_map: int
    released: float
    observed_at: float
    status: str
    pulses: int
    first_pulse: float | None


class MapTracker:
    """Infer the one-based active map, or None while it is unknown."""

    def __init__(self, on_selection=None):
        self.on_selection = on_selection
        self.number = None
        self.reason = UNKNOWN_REASON
        self.since = None
        self._last_activity = 0.0
        self._awaiting_tick = False
        self._tick = None
        self._tick_time = None
        self._button = None
        self._gesture = None
        self._cancel_held = False
        self._commit = None
        self._pulses = 0
        self._phase_on = False
        self._phase_since = None
        self._first_pulse = None

    def _report(self, status, time):
        if self.on_selection is not None and self._commit is not None:
            count, released = self._commit
            self.on_selection(SelectionObservation(
                count, released, time, status, self._pulses, self._first_pulse
            ))

    def _select(self, number, reason, time):
        self.number = number
        self.reason = reason
        self.since = time

    def _clear_selector(self):
        self._gesture = None
        self._cancel_held = False
        self._commit = None
        self._pulses = 0
        self._phase_on = False
        self._phase_since = None
        self._first_pulse = None

    def activity(self, time):
        """Record one frame or record of any kind at its source time."""
        if time - self._last_activity >= BUS_SILENCE_SECONDS:
            self._awaiting_tick = True
        self._last_activity = time

    def tick(self, time, tick16):
        """Consume the tick16 of one telemetry group."""
        previous, previous_time = self._tick, self._tick_time
        opening = self._awaiting_tick and tick16 <= PRODUCER_RUN_TICK_MAX
        self._awaiting_tick = False
        step = None if previous is None else tick_step(
            previous, tick16, receive_gap(previous_time, time)
        )
        if step is TickStep.STALE and not opening:
            # The decoder rejects a repeated or reordered group and steps the
            # next one from the last accepted group.
            return
        self._tick, self._tick_time = tick16, time
        if opening or step is TickStep.RESTART:
            self._report("interrupted", time)
            self._clear_selector()
            self._select(1, "controller start observed", time)

    def button(self, time, code):
        """Consume the ASCD input code of 0x239 byte 3."""
        previous = self._button
        self._button = code
        if previous is None or code == previous:
            return
        if self._commit is not None:
            # The runtime ignores selector input until the pulses end.
            self._gesture = None
            return
        if self._gesture is None:
            if previous == BUTTON_RELEASED and code == BUTTON_SET:
                self._gesture = 0
                self._cancel_held = False
            return
        if self._cancel_held:
            if code == BUTTON_SET:
                self._gesture += 1
                self._cancel_held = False
                if self._gesture > MAP_COUNT:
                    self._gesture = None
            else:
                self._gesture = None
            return
        if code == BUTTON_CANCEL:
            self._cancel_held = True
            return
        if code == BUTTON_RELEASED and self._gesture >= 1:
            self._commit = (self._gesture, time)
            self._pulses = 0
            self._phase_on = False
            self._phase_since = None
            self._first_pulse = None
            self._report("requested", time)
        self._gesture = None

    def dashboard(self, time, code):
        """Consume the ASCD display code of 0x551 byte 5."""
        if self._commit is None:
            return
        count, released = self._commit
        state = display_state(code)
        on = state == DISPLAY_STATE_ON
        if self._pulses == 0:
            if on:
                self._pulses = 1
                self._phase_on = True
                self._phase_since = time
                self._first_pulse = time
            elif time - released > FEEDBACK_START_SECONDS:
                # The runtime did not commit the gesture.
                self._report("not_observed", time)
                self._clear_selector()
            return
        if self._phase_on:
            if on:
                if time - self._phase_since > FEEDBACK_PHASE_MAX_SECONDS:
                    self._unconfirmed(count, time)
            elif state == DISPLAY_STATE_OFF:
                self._phase_on = False
                self._phase_since = time
            else:
                self._unconfirmed(count, time)
            return
        if on:
            self._pulses += 1
            if self._pulses > MAP_COUNT:
                self._unconfirmed(count, time)
                return
            self._phase_on = True
            self._phase_since = time
        elif (
            state != DISPLAY_STATE_OFF
            or time - self._phase_since >= FEEDBACK_END_SECONDS
        ):
            self._finish(count, time)

    def _finish(self, count, time):
        pulses = self._pulses
        self._report("confirmed" if pulses == count else "mismatched", time)
        self._clear_selector()
        if pulses == count:
            noun = "pulse" if pulses == 1 else "pulses"
            self._select(
                count,
                f"selection confirmed by {pulses} feedback {noun}",
                time,
            )
        else:
            self._select(
                None,
                f"selection of Map {count} answered by {pulses} pulses",
                time,
            )

    def _unconfirmed(self, count, time):
        self._report("uncountable", time)
        self._clear_selector()
        self._select(
            None,
            f"selection of Map {count} without countable pulses",
            time,
        )
