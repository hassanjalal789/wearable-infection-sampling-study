#!/usr/bin/env python3
"""
Sensing-schedule engine.  PREREGISTRATION ARTEFACT.

Seven arms.  Every arm returns a boolean mask over the 1440 minutes of a
participant-day plus a metadata record.  Masks are deterministic and
reproducible bit-for-bit: the only stochastic arm is S5, whose randomness is
seeded by SHA256(global_seed || participant_id || ISO-date).

Naming (post-review patch 5): S2 is UNIFORM-BLOCK duty cycling -- equally spaced
10-minute bursts.  It is NOT the 1-in-n single-minute baseline; that variant is
not implemented and must never be described as the primary baseline.

Placement families
------------------
  clock-driven      S2, S3   fixed stride from the window start; no lookahead
  reactive trigger  S4       earliest-first causal scan; a real device cannot
                             see the future, so S4 is deliberately greedy
  counterfactual    S3r, S6  even-spread nearest-eligible over rest-only starts.
                             These use an ORACLE over the day's rest pattern and
                             are matched constructs for the M1 mechanism test,
                             NOT deployable schedules.  Stated as an M1 limitation.
  seeded random     S5       non-overlapping starts, rejection sampled
"""
from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
import numpy as np

MINUTES = 1440
NIGHT = (0, 420)      # 00:00-06:59  -> 420 minutes
DAY = (420, 1440)     # 07:00-23:59  -> 1020 minutes
GLOBAL_SEED = 20261010


@dataclass
class DayInput:
    """One participant-day of source data."""
    participant_id: str
    date: str                      # ISO yyyy-mm-dd
    observed: np.ndarray           # bool[1440]  minute contains >=1 source HR sample
    steps: np.ndarray              # float[1440] step count; NaN = missing

    def rest(self) -> np.ndarray:
        """Rest minute := recorded steps == 0.  Missing steps are NOT rest."""
        return np.nan_to_num(self.steps, nan=1.0) == 0.0


@dataclass
class Mask:
    arm: str
    retained: np.ndarray           # bool[1440]
    starts: list = field(default_factory=list)
    n_scheduled: int = 0
    n_requested: int = 0
    shortfall: int = 0
    samples_scheduled: int = 0
    samples_delivered: int = 0

    def digest(self) -> str:
        return hashlib.sha256(self.retained.tobytes()).hexdigest()[:16]


def day_seed(participant_id: str, date: str) -> int:
    h = hashlib.sha256(f"{GLOBAL_SEED}‖{participant_id}‖{date}".encode())
    return int.from_bytes(h.digest()[:8], "big")


def _finalise(arm, starts, day, L) -> Mask:
    starts = sorted(starts)
    m = np.zeros(MINUTES, dtype=bool)
    for s in starts:
        m[s:s + L] = True
    delivered = m & day.observed
    return Mask(arm=arm, retained=delivered, starts=starts, n_scheduled=len(starts),
                samples_scheduled=int(m.sum()), samples_delivered=int(delivered.sum()))


def _eligible_rest_starts(day: DayInput, window, L) -> list[int]:
    """Start minutes m where [m, m+L-1] lies inside the window and is all rest."""
    lo, hi = window
    rest = day.rest()
    csum = np.concatenate([[0], np.cumsum(rest.astype(int))])
    return [m for m in range(lo, hi - L + 1) if csum[m + L] - csum[m] == L]


def _max_packing(starts: list[int], L: int) -> int:
    """Optimal count of non-overlapping bursts: greedy earliest-first."""
    n, last = 0, -10 ** 9
    for s in starts:
        if s >= last + L:
            n += 1; last = s
    return n


def _suffix_capacity(starts: list[int], L: int) -> list[int]:
    """cap[i] = maximum non-overlapping bursts selectable from starts[i:].

    Right-to-left dynamic programme.  cap[0] equals the optimal packing, so it
    agrees with _max_packing by construction rather than by coincidence.
    """
    import bisect
    n = len(starts)
    cap = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        j = bisect.bisect_left(starts, starts[i] + L)
        cap[i] = max(cap[i + 1], 1 + cap[j])
    return cap


def _even_spread(starts: list[int], N: int, window, L: int) -> list[int]:
    """Feasibility-aware deterministic even-spread placement.

    PATCH 1.  The previous greedy could pick a start that looked closest to the
    target but stranded the remaining budget, so it returned fewer than N even
    when N was feasible -- which broke the M1 claim that S3r and S6 both receive
    exactly N' bursts.

    This version is exact.  A candidate is admissible only if selecting it still
    leaves enough capacity for every remaining burst, tested against a suffix
    capacity table.  Among admissible candidates it takes the one nearest the
    ideal evenly-spaced target, ties to the smaller minute.

    GUARANTEE: returns exactly N starts whenever N <= _max_packing(starts, L),
    and the maximum feasible count otherwise.  Deterministic, no seed.
    """
    import bisect
    if N <= 0 or not starts:
        return []
    starts = sorted(starts)
    cap = _suffix_capacity(starts, L)
    N = min(N, cap[0])                       # never promise more than is feasible
    lo, hi = window
    span = hi - lo
    chosen: list[int] = []
    idx = 0                                   # first index not overlapping the last pick
    for k in range(N):
        remaining = N - k
        target = lo + (k + 0.5) * span / N
        best, best_key = None, None
        for j in range(idx, len(starts)):
            if cap[j] < remaining:            # nothing from here on can finish the job
                break
            nxt = bisect.bisect_left(starts, starts[j] + L)
            if 1 + cap[nxt] < remaining:      # picking j would strand the remainder
                continue
            key = (abs(starts[j] - target), starts[j])
            if best_key is None or key < best_key:
                best, best_key = j, key
        if best is None:                      # unreachable given cap[0] clamp
            break
        chosen.append(starts[best])
        idx = bisect.bisect_left(starts, starts[best] + L)
    return chosen


# ----------------------------------------------------------------------------- arms
def s1_continuous(day: DayInput, **_) -> Mask:
    m = day.observed.copy()
    return Mask(arm="S1", retained=m, starts=[], n_scheduled=0,
                samples_scheduled=MINUTES, samples_delivered=int(m.sum()))


def s2_uniform_block(day: DayInput, N: int, L: int = 10) -> Mask:
    """Uniform-block duty cycling: N equally spaced L-minute bursts over 24 h."""
    stride = MINUTES // max(N, 1)
    starts = [i * stride for i in range(N) if i * stride + L <= MINUTES]
    mask = _finalise("S2", starts, day, L)
    mask.n_requested = N; mask.shortfall = N - len(starts)
    return mask


def s3_nocturnal(day: DayInput, N: int, L: int = 10) -> Mask:
    lo, hi = NIGHT
    cap = (hi - lo) // L                                   # 42 at L=10
    n = min(N, cap)
    stride = (hi - lo) // max(n, 1)
    starts = [lo + i * stride for i in range(n) if lo + i * stride + L <= hi]
    mask = _finalise("S3", starts, day, L)
    mask.n_requested = N; mask.shortfall = N - len(starts)
    return mask


def s5_random_block(day: DayInput, N: int, L: int = 10) -> Mask:
    rng = np.random.default_rng(day_seed(day.participant_id, day.date))
    starts: list[int] = []
    rejects = 0
    while len(starts) < N and rejects < 1000:
        c = int(rng.integers(0, MINUTES - L + 1))
        if all(abs(c - s) >= L for s in starts):
            starts.append(c)
        else:
            rejects += 1
    if len(starts) < N:                                    # documented fallback
        for c in range(0, MINUTES - L + 1):
            if len(starts) >= N:
                break
            if all(abs(c - s) >= L for s in starts):
                starts.append(c)
    mask = _finalise("S5", starts, day, L)
    mask.n_requested = N; mask.shortfall = N - len(starts)
    return mask


def s4_rest_triggered(day: DayInput, N: int, L: int = 10,
                      hold: int = 5, skip: int = 30) -> Mask:
    """Causal earliest-first trigger: fire when rest has held `hold` minutes."""
    rest = day.rest()
    starts, m, run = [], 0, 0
    while m < MINUTES - L + 1 and len(starts) < N:
        run = run + 1 if rest[m] else 0
        if run >= hold:
            starts.append(m)
            m += L + skip
            run = 0
        else:
            m += 1
    mask = _finalise("S4", starts, day, L)
    mask.n_requested = N; mask.shortfall = N - len(starts)
    return mask


def s3r_nocturnal_rest(day: DayInput, N: int, L: int = 10) -> Mask:
    el = _eligible_rest_starts(day, NIGHT, L)
    starts = _even_spread(el, N, NIGHT, L)
    mask = _finalise("S3r", starts, day, L)
    mask.n_requested = N; mask.shortfall = N - len(starts)
    return mask


def s6_daytime_rest(day: DayInput, N: int, L: int = 10) -> Mask:
    """Strict rest-only daytime control.  NO active-minute top-up, ever."""
    el = _eligible_rest_starts(day, DAY, L)
    starts = _even_spread(el, N, DAY, L)
    mask = _finalise("S6", starts, day, L)
    mask.n_requested = N; mask.shortfall = N - len(starts)
    return mask


def m1_matched_pair(day: DayInput, n_budget: int, L: int = 10, n_min: int = 2):
    """M1 matching: run S3r and S6 at the SAME feasible burst count N'.

    N' = min(max packing of night rest starts, max packing of day rest starts,
             budget).  Returns (mask_s3r, mask_s6, record) or (None, None, record)
    when the participant-day is unavailable for M1.
    """
    night = _eligible_rest_starts(day, NIGHT, L)
    dayw = _eligible_rest_starts(day, DAY, L)
    n3, n6 = _max_packing(night, L), _max_packing(dayw, L)
    n_prime = min(n3, n6, n_budget)
    rec = dict(participant_id=day.participant_id, date=day.date,
               max_night=n3, max_day=n6, n_budget=n_budget, n_prime=n_prime)
    if n_prime < n_min:
        rec.update(available=False,
                   reason="n3<n_min" if n3 < n_min else ("n6<n_min" if n6 < n_min
                          else "budget<n_min"))
        return None, None, rec
    a, b = s3r_nocturnal_rest(day, n_prime, L), s6_daytime_rest(day, n_prime, L)
    rec.update(available=True, reason=None,
               s3r_delivered=a.samples_delivered, s6_delivered=b.samples_delivered,
               s3r_purity=rest_purity(a, day), s6_purity=rest_purity(b, day))
    return a, b, rec


def rest_purity(mask: Mask, day: DayInput) -> float:
    r = mask.retained
    return float((r & day.rest()).sum() / r.sum()) if r.sum() else float("nan")


ARMS = {"S1": s1_continuous, "S2": s2_uniform_block, "S3": s3_nocturnal,
        "S3r": s3r_nocturnal_rest, "S4": s4_rest_triggered,
        "S5": s5_random_block, "S6": s6_daytime_rest}
