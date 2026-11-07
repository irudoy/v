"""Correlate completed selector requests, verified map indices and bus feedback."""

from bisect import bisect_left, bisect_right
from dataclasses import asdict, replace

from patches.map_switching_layout import load_layout
from tools.can_dashboard.model import ASCD_BUTTON_ID, BASE_TICK_SECONDS, DASHBOARD_STATE_ID
from tools.can_dashboard.selected_map import (
    DISPLAY_STATE_OFF, DISPLAY_STATE_ON, FEEDBACK_START_SECONDS, MAP_COUNT,
    MapTracker, display_state,
)
from tools.logs.ignition_surface_audit import detect_map_commits


class MapSelectionAudit:
    def __init__(self, expected_identity, profile, tick_divisor):
        self.expected_identity = expected_identity
        self.events = []
        self.tracker = MapTracker(on_selection=self.events.append)
        self.indices = []
        self.displays = []
        context_count = 1 + max(context["tag"] for context in profile["contexts"])
        self.refresh_seconds = context_count * BASE_TICK_SECONDS * tick_divisor
        feedback = load_layout().feedback
        self.display_gap_limit = min(
            feedback.default_on_frames, feedback.default_off_frames
        ) * BASE_TICK_SECONDS

    def frame(self, frame):
        if frame.direction != "Rx" or frame.extended or frame.remote:
            return
        time = frame.offset_ms / 1000
        self.tracker.activity(time)
        if frame.can_id == ASCD_BUTTON_ID and len(frame.data) >= 4:
            self.tracker.button(time, frame.data[3])
        elif frame.can_id == DASHBOARD_STATE_ID and len(frame.data) >= 6:
            self.tracker.dashboard(time, frame.data[5])
            self.displays.append((time, display_state(frame.data[5])))

    def snapshot(self, snapshot, identity):
        self.tracker.tick(snapshot.timestamp, snapshot.tick16)
        if snapshot.schema_verified and identity == self.expected_identity:
            index = snapshot.fields.get("active_map_index")
            if index is not None:
                self.indices.append((snapshot.timestamp, snapshot.run, index))

    def result(self, trace, expected_maps=()):
        expected_maps = set(expected_maps)
        if any(type(number) is not int or not 1 <= number <= MAP_COUNT for number in expected_maps):
            raise ValueError("expected maps must be one-based map slots")
        requests = detect_map_commits(replace(
            trace, frames=tuple(frame for frame in trace.frames if frame.direction == "Rx")
        ))
        resolutions = {event.released: event for event in self.events if event.status != "requested"}
        admitted = {event.released for event in self.events if event.status == "requested"}
        index_times = [sample[0] for sample in self.indices]
        display_times = [sample[0] for sample in self.displays]
        last = trace.frames[-1].offset_ms / 1000
        rows = []
        for position, request in enumerate(requests):
            release, wanted = request.timestamp, request.map_number
            event = resolutions.get(release)
            next_release = requests[position + 1].timestamp if position + 1 < len(requests) else last
            feedback_end = event.observed_at if event is not None else last
            end = min(last, next_release, feedback_end + self.refresh_seconds)
            first_pulse = event.first_pulse if event is not None else None
            start = first_pulse + self.refresh_seconds if first_pulse is not None else (
                release + FEEDBACK_START_SECONDS
            )
            before_position = bisect_right(index_times, release) - 1
            before = self.indices[before_position] if before_position >= 0 else None
            if before is not None and release - before[0] > 2 * self.refresh_seconds:
                before = None
            after = self.indices[bisect_left(index_times, start):bisect_right(index_times, end)]
            observed = sorted({sample[2] for sample in after})
            display = self.displays[
                bisect_left(display_times, release):bisect_right(display_times, min(feedback_end, end))
            ]
            times = [release, *(time for time, _state in display), min(feedback_end, end)]
            gap = max((b - a for a, b in zip(times, times[1:])), default=0)
            foreign = sorted({state for time, state in display if first_pulse is not None
                              and time >= first_pulse and state not in (DISPLAY_STATE_ON, DISPLAY_STATE_OFF)})
            index_covered = bool(after) and end - after[-1][0] <= 2 * self.refresh_seconds
            index_covered = index_covered and (
                before is None or all(sample[1] == before[1] for sample in after)
            )
            feedback_covered = bool(display) and gap <= self.display_gap_limit + 0.00002
            invalid = [index for index in observed if not 0 <= index < MAP_COUNT]
            status, outcome = "INCOMPLETE", "NOT_CORRELATED"
            if invalid:
                status, outcome = "FAIL", "INVALID_INDEX"
            elif event is None:
                outcome = "INCOMPLETE_FEEDBACK" if release in admitted else "NOT_CORRELATED"
            elif event.status in ("interrupted", "uncountable"):
                outcome = "INCOMPLETE_FEEDBACK"
            elif not feedback_covered or foreign or not index_covered:
                outcome = "INSUFFICIENT_COVERAGE"
            elif event.status == "mismatched":
                status, outcome = "FAIL", "FEEDBACK_MISMATCH"
            elif event.status == "not_observed":
                status, outcome = "FAIL", (
                    "FEEDBACK_MISSING" if observed == [wanted - 1] else "NOT_ACCEPTED"
                )
            elif observed != [wanted - 1]:
                status, outcome = "FAIL", "INDEX_MISMATCH"
            else:
                status, outcome = "PASS", "CONFIRMED"
            rows.append({
                "released_elapsed": release, "requested_map": wanted,
                "status": status, "outcome": outcome,
                "tracked_request": release in admitted,
                "before_index": None if before is None else before[2],
                "after_indices": observed, "index_samples": len(after),
                "index_window": [start, end],
                "feedback": None if event is None else asdict(event),
                "feedback_samples": len(display), "maximum_0x551_gap_seconds": gap,
                "foreign_display_states": foreign,
            })
        changes = []
        for before, after in zip(self.indices, self.indices[1:]):
            if before[1] != after[1] or before[2] == after[2]:
                continue
            if not any(row["released_elapsed"] <= after[0] <= row["index_window"][1]
                       and row["requested_map"] - 1 == after[2] for row in rows):
                changes.append({"elapsed": after[0], "from_index": before[2], "to_index": after[2]})
        covered = sorted({row["requested_map"] for row in rows if row["status"] == "PASS"})
        missing = sorted(expected_maps - set(covered))
        statuses = {row["status"] for row in rows}
        status = "FAIL" if "FAIL" in statuses else (
            "PASS" if statuses == {"PASS"} and not missing and not changes else "INCOMPLETE"
        )
        return {
            "status": status, "gestures": rows,
            "expected_maps": sorted(expected_maps), "covered_maps": covered,
            "missing_expected_maps": missing, "unmatched_index_change_count": len(changes),
            "unmatched_index_changes": changes[:8],
            "fresh_index_samples": len(self.indices),
            "feedback_sampling_gap_limit_seconds": self.display_gap_limit,
            "boundary": "Only fresh verified active_map_index fields establish the map; lamp behavior needs operator evidence.",
        }
