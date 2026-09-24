"""PATCH 1: adversarial proof that M1 matching is exact.

_max_packing reports the optimal number of non-overlapping eligible bursts.
_even_spread must realise exactly that many whenever asked, or the M1 claim
that S3r and S6 both receive N' bursts is false.  Thousands of random rest
patterns are exercised, including hostile ones built to strand a naive greedy.
"""
import numpy as np, pytest
import schedules as S

L = 10


def random_day(rng, night_rest=0.6, day_rest=0.25, clump=True):
    steps = np.zeros(S.MINUTES, dtype=float)
    if clump:
        steps[:] = 1.0
        for _ in range(rng.integers(2, 25)):
            a = int(rng.integers(0, S.MINUTES - 5))
            b = a + int(rng.integers(5, 90))
            steps[a:b] = 0.0
    else:
        steps[0:420] = np.where(rng.random(420) < night_rest, 0.0, 5.0)
        steps[420:] = np.where(rng.random(1020) < day_rest, 0.0, 5.0)
    return S.DayInput("P", "2026-03-01", np.ones(S.MINUTES, dtype=bool), steps)


@pytest.mark.parametrize("clump,min_checks", [(True, 3000), (False, 1000)])
def test_even_spread_realises_the_optimal_packing(clump, min_checks):
    """Exhaustive over 1500 random patterns x several feasible N each.

    The unclumped generator scatters single rest minutes, so a 10-minute all-rest
    run is rarer and fewer patterns yield a non-zero capacity -- hence the lower
    floor on that arm. Every pattern that does yield capacity is still checked.
    """
    rng = np.random.default_rng(7 if clump else 8)
    checked = 0
    for _ in range(1500):
        day = random_day(rng, clump=clump)
        for window in (S.NIGHT, S.DAY):
            el = S._eligible_rest_starts(day, window, L)
            cap = S._max_packing(el, L)
            if cap == 0:
                continue
            for n in {1, max(1, cap // 2), cap}:
                got = S._even_spread(el, n, window, L)
                assert len(got) == n, (window, cap, n, len(got))
                assert all(b - a >= L for a, b in zip(got, got[1:]))
                assert all(e in el for e in got)
                checked += 1
    assert checked > min_checks


def test_asking_for_more_than_feasible_returns_the_maximum_not_a_crash():
    rng = np.random.default_rng(11)
    for _ in range(300):
        day = random_day(rng)
        el = S._eligible_rest_starts(day, S.NIGHT, L)
        cap = S._max_packing(el, L)
        assert len(S._even_spread(el, cap + 5, S.NIGHT, L)) == cap


def test_hostile_pattern_that_strands_a_naive_greedy():
    """Two tight eligible clusters far apart.  A greedy that takes the start
    nearest the ideal target first can strand later bursts; the feasibility-aware
    version must realise the full optimum."""
    el = list(range(600, 611)) + list(range(1400, 1411))
    cap = S._max_packing(el, L)
    assert cap == 4                       # each 11-wide cluster hosts two bursts
    for n in range(1, cap + 1):
        got = S._even_spread(el, n, S.DAY, L)
        assert len(got) == n, (n, got)
        assert all(b - a >= L for a, b in zip(got, got[1:]))


def test_single_narrow_cluster_cannot_over_promise():
    """A 10-wide cluster hosts exactly one burst, whatever N is requested."""
    el = list(range(500, 510))
    assert S._max_packing(el, L) == 1
    assert len(S._even_spread(el, 5, S.DAY, L)) == 1


def test_capacity_table_agrees_with_greedy_optimum():
    rng = np.random.default_rng(13)
    for _ in range(800):
        el = sorted(rng.choice(np.arange(0, 1440), size=int(rng.integers(1, 120)),
                               replace=False).tolist())
        assert S._suffix_capacity(el, L)[0] == S._max_packing(el, L)


def test_m1_invariants_hold_over_many_synthetic_days():
    """The full contract asserted per the review, on 2000 random days."""
    rng = np.random.default_rng(21)
    available = 0
    for i in range(2000):
        day = random_day(rng)
        a, b, rec = S.m1_matched_pair(day, n_budget=int(rng.integers(1, 12)), L=L)
        if not rec["available"]:
            assert a is None and b is None
            continue
        available += 1
        n = rec["n_prime"]
        assert a.n_scheduled == b.n_scheduled == n              # identical matched N
        assert all(y - x >= L for x, y in zip(a.starts, a.starts[1:]))
        assert all(y - x >= L for x, y in zip(b.starts, b.starts[1:]))
        assert all(S.NIGHT[0] <= s and s + L <= S.NIGHT[1] for s in a.starts)
        assert all(S.DAY[0] <= s and s + L <= S.DAY[1] for s in b.starts)
        assert a.samples_scheduled == b.samples_scheduled == n * L   # identical length
        rest = day.rest()
        for st in a.starts + b.starts:
            assert rest[st:st + L].all()                        # rest-only, both arms
        if a.samples_delivered:
            assert S.rest_purity(a, day) == 1.0
        if b.samples_delivered:
            assert S.rest_purity(b, day) == 1.0
    assert available > 400, f"only {available} available days -- generator too hostile"
