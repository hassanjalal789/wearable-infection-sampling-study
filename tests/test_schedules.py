import hashlib
import numpy as np
import pytest
import schedules as S
from synth import make_day, sparse_day

L = 10


def starts_are_disjoint(mask):
    s = sorted(mask.starts)
    return all(b - a >= L for a, b in zip(s, s[1:]))


def all_arms(day, N=7):
    return {"S1": S.s1_continuous(day), "S2": S.s2_uniform_block(day, N, L),
            "S3": S.s3_nocturnal(day, N, L), "S3r": S.s3r_nocturnal_rest(day, N, L),
            "S4": S.s4_rest_triggered(day, N, L), "S5": S.s5_random_block(day, N, L),
            "S6": S.s6_daytime_rest(day, N, L)}


def test_retained_never_exceeds_source():
    """No arm may retain a minute the archive never observed."""
    day = make_day(seed=3)
    for name, m in all_arms(day).items():
        assert not (m.retained & ~day.observed).any(), name


def test_s3_confined_to_night_window():
    m = S.s3_nocturnal(make_day(seed=4), 7, L)
    assert not m.retained[S.NIGHT[1]:].any()


def test_s6_confined_to_day_window():
    m = S.s6_daytime_rest(make_day(seed=5), 7, L)
    assert not m.retained[:S.DAY[0]].any()


def test_s6_retains_only_rest_minutes_no_topup():
    """The active-minute top-up rule is deleted; S6 purity must be exactly 1.0."""
    day = make_day(seed=6)
    m = S.s6_daytime_rest(day, 7, L)
    scheduled = np.zeros(S.MINUTES, dtype=bool)
    for s in m.starts:
        scheduled[s:s + L] = True
    assert (scheduled & ~day.rest()).sum() == 0


def test_s3r_retains_only_rest_minutes():
    day = make_day(seed=7)
    m = S.s3r_nocturnal_rest(day, 7, L)
    scheduled = np.zeros(S.MINUTES, dtype=bool)
    for s in m.starts:
        scheduled[s:s + L] = True
    assert (scheduled & ~day.rest()).sum() == 0


def test_bursts_never_overlap():
    day = make_day(seed=8)
    for name, m in all_arms(day, N=12).items():
        if name == "S1":
            continue
        assert starts_are_disjoint(m), name


def test_burst_length_is_exact():
    day = make_day(seed=9, coverage=1.0)
    for name, m in all_arms(day, N=6).items():
        if name == "S1":
            continue
        assert m.samples_scheduled == len(m.starts) * L, name


def test_deterministic_bit_for_bit():
    """Two independent runs must produce byte-identical masks for every arm."""
    d1, d2 = make_day(seed=10), make_day(seed=10)
    a, b = all_arms(d1, 9), all_arms(d2, 9)
    for k in a:
        assert a[k].digest() == b[k].digest(), k


def test_s5_seed_is_participant_day_specific():
    same = S.s5_random_block(make_day(pid="PX", date="2026-03-01", seed=11), 9, L)
    again = S.s5_random_block(make_day(pid="PX", date="2026-03-01", seed=11), 9, L)
    other = S.s5_random_block(make_day(pid="PX", date="2026-03-02", seed=11), 9, L)
    assert same.starts == again.starts
    assert same.starts != other.starts


def test_clock_driven_arms_share_burst_count():
    """At equal energy S2, S3 and S5 must receive the identical N."""
    day = make_day(seed=12)
    N = 9
    assert (S.s2_uniform_block(day, N, L).n_scheduled
            == S.s3_nocturnal(day, N, L).n_scheduled
            == S.s5_random_block(day, N, L).n_scheduled == N)


def test_s3_saturates_at_night_capacity():
    day = make_day(seed=13)
    m = S.s3_nocturnal(day, 60, L)          # 60 > 420/10
    assert m.n_scheduled == 42 and m.shortfall == 18


def test_m1_matches_both_arms_to_the_same_count():
    day = make_day(seed=14)
    a, b, rec = S.m1_matched_pair(day, n_budget=7, L=L)
    assert rec["available"]
    assert a.n_scheduled == b.n_scheduled == rec["n_prime"]
    assert rec["s3r_purity"] == 1.0 and rec["s6_purity"] == 1.0


def test_m1_unavailable_when_daytime_rest_is_scarce():
    a, b, rec = S.m1_matched_pair(sparse_day(), n_budget=7, L=L)
    assert a is None and b is None
    assert rec["available"] is False and rec["reason"] == "n6<n_min"


def test_even_spread_is_reproducible_and_ordered():
    el = list(range(430, 900, 3))
    x = S._even_spread(el, 6, S.DAY, L)
    y = S._even_spread(el, 6, S.DAY, L)
    assert x == y == sorted(x)
    assert all(b - a >= L for a, b in zip(x, x[1:]))
