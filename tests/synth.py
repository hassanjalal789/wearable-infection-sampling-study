"""Synthetic participant-days.  SYNTHETIC ONLY -- no real archive data is used
anywhere in Phase 1 schedule development."""
import numpy as np
from schedules import MINUTES, DayInput


def make_day(pid="P000001", date="2026-03-01", seed=0,
             night_rest=0.97, day_rest=0.35, coverage=0.92,
             day_rest_blocks=6, block_len=25):
    """Night is mostly rest; daytime rest occurs in a few discrete blocks."""
    rng = np.random.default_rng(seed)
    steps = np.zeros(MINUTES, dtype=float)
    # night 00:00-06:59
    steps[0:420] = np.where(rng.random(420) < night_rest, 0.0, rng.integers(1, 30, 420))
    # daytime: active by default
    steps[420:] = rng.integers(1, 90, MINUTES - 420).astype(float)
    # carve discrete daytime rest blocks (sitting, meetings, naps)
    for _ in range(day_rest_blocks):
        s = int(rng.integers(430, MINUTES - block_len))
        steps[s:s + block_len] = 0.0
    # scattered daytime zero-step minutes
    idx = rng.choice(np.arange(420, MINUTES), size=int((MINUTES - 420) * day_rest * 0.3),
                     replace=False)
    steps[idx] = 0.0
    observed = rng.random(MINUTES) < coverage
    return DayInput(participant_id=pid, date=date, observed=observed, steps=steps)


def sparse_day(pid="P000002", date="2026-03-02", seed=1):
    """A day with almost no daytime rest -- exercises the M1 unavailability path."""
    rng = np.random.default_rng(seed)
    steps = np.zeros(MINUTES, dtype=float)
    steps[0:420] = 0.0
    steps[420:] = rng.integers(5, 120, MINUTES - 420).astype(float)
    return DayInput(pid, date, np.ones(MINUTES, dtype=bool), steps)
