#!/usr/bin/env python3
"""NON-PRODUCTION reference model: a wake signal is a hint, never an authority.

Run: python3 docs/research/agent-craft-20261117/test_wake_reference.py
No I/O, credentials, timers, remote work or task dispatch are performed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import unittest


@dataclass(frozen=True)
class Snapshot:
    work: str = "synthetic/work"
    generation: int = 1
    authorized: bool = True
    window_open: bool = True
    state: str = "completed"
    progress_fresh: bool = True
    question_pending: bool = False
    ready: tuple[str, ...] = ()
    free_slots: int = 0
    claimed: frozenset[str] = field(default_factory=frozenset)


def propose(snapshot: Snapshot, *, wake_hint: str = "timer") -> tuple[str, tuple[str, ...]]:
    """Only return candidates; it cannot claim, enqueue or wake an agent.

    wake_hint is deliberately not used as an authoritative state observation.
    A real implementation must get fresh state and atomically claim before effects.
    """
    if not snapshot.authorized:
        return "HOLD_AUTHORITY", ()
    if not snapshot.window_open:
        return "HOLD_WINDOW", ()
    if snapshot.state == "stopped_user":
        return "HOLD_HUMAN", ()
    if snapshot.state == "stopped_provider":
        return "HOLD_PROVIDER", ()
    if snapshot.state not in ("running", "completed"):
        return "INSPECT_UNKNOWN", ()
    if snapshot.question_pending:
        return "INSPECT_QUESTION", ()
    if snapshot.state == "running":
        return ("KEEP_RUNNING" if snapshot.progress_fresh else "INSPECT_STALLED"), ()
    if not snapshot.ready:
        return "PAUSE_CANDIDATE", ()
    if snapshot.free_slots <= 0:
        return "HOLD_CAPACITY", ()

    # Candidate intents are stable across duplicate notifications and timer ticks.
    # Claimed keys represent an authoritative owner ACK, not a model guess.
    keys: list[str] = []
    for item in dict.fromkeys(snapshot.ready):
        key = f"{snapshot.work}:{snapshot.generation}:{item}"
        if key not in snapshot.claimed:
            keys.append(key)
        if len(keys) >= snapshot.free_slots:
            break
    return ("PROPOSE_ONLY", tuple(keys)) if keys else ("ALREADY_CLAIMED", ())


class WakeReconcileReference(unittest.TestCase):
    def test_lost_notification_still_reconciles(self):
        s = Snapshot(ready=("next",), free_slots=1)
        self.assertEqual(propose(s, wake_hint="timer"), propose(s, wake_hint="notification"))

    def test_duplicate_wakes_share_intent_key(self):
        s = Snapshot(ready=("next",), free_slots=1)
        first = propose(s)[1]
        self.assertEqual(first, propose(s, wake_hint="manual")[1])
        self.assertEqual(propose(Snapshot(ready=("next",), free_slots=1,
                                          claimed=frozenset(first))), ("ALREADY_CLAIMED", ()))

    def test_no_new_authority_from_timer(self):
        self.assertEqual(propose(Snapshot(authorized=False, ready=("next",),
                                          free_slots=1)), ("HOLD_AUTHORITY", ()))

    def test_user_window_closed(self):
        self.assertEqual(propose(Snapshot(window_open=False, ready=("next",),
                                          free_slots=1)), ("HOLD_WINDOW", ()))

    def test_provider_stopped(self):
        self.assertEqual(propose(Snapshot(state="stopped_provider",
                                          ready=("next",), free_slots=1)), ("HOLD_PROVIDER", ()))

    def test_human_stopped(self):
        self.assertEqual(propose(Snapshot(state="stopped_user",
                                          ready=("next",), free_slots=1)), ("HOLD_HUMAN", ()))

    def test_running_rate_limited_but_fresh(self):
        self.assertEqual(propose(Snapshot(state="running", progress_fresh=True,
                                          ready=("next",), free_slots=1)), ("KEEP_RUNNING", ()))

    def test_stalled_is_inspected_not_killed(self):
        self.assertEqual(propose(Snapshot(state="running", progress_fresh=False)),
                         ("INSPECT_STALLED", ()))

    def test_question_is_not_auto_answered(self):
        self.assertEqual(propose(Snapshot(question_pending=True,
                                          ready=("next",), free_slots=1)), ("INSPECT_QUESTION", ()))

    def test_unknown_observation_not_treated_as_completed(self):
        self.assertEqual(propose(Snapshot(state="unknown",
                                          ready=("next",), free_slots=1)), ("INSPECT_UNKNOWN", ()))

    def test_no_ready_proposes_pause_not_actual_pause(self):
        self.assertEqual(propose(Snapshot()), ("PAUSE_CANDIDATE", ()))

    def test_bounded_unique_candidates(self):
        action, keys = propose(Snapshot(ready=("a", "a", "b", "c"), free_slots=2))
        self.assertEqual(action, "PROPOSE_ONLY")
        self.assertEqual(keys, ("synthetic/work:1:a", "synthetic/work:1:b"))

    def test_generation_changes_candidate_identity(self):
        old = propose(Snapshot(ready=("a",), free_slots=1))[1]
        new = propose(Snapshot(generation=2, ready=("a",), free_slots=1))[1]
        self.assertNotEqual(old, new)

    def test_zero_capacity_never_proposes(self):
        self.assertEqual(propose(Snapshot(ready=("next",), free_slots=0)),
                         ("HOLD_CAPACITY", ()))


if __name__ == "__main__":
    unittest.main()
