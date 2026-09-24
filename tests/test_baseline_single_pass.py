"""A3.1 as corrected: ONE 28-valid-day baseline, no nested burn-in, and every
sample reaching z_d -- directly or indirectly -- inside the 90-day lookback."""
import numpy as np, pandas as pd, pytest
import tod_z

CFG = tod_z.TODZConfig()
D0 = pd.Timestamp("2021-01-01")


def record(days=150, per_hour=6, hours=range(7), seed=5, hr=60.0, jitter=1.5,
           start=D0, skip=()):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(days):
        if i in skip:
            continue
        day = start + pd.Timedelta(days=i)
        for h in hours:
            for k in range(per_hour):
                rows.append((day + pd.Timedelta(hours=h, minutes=k * (60 // per_hour)),
                             hr + rng.normal(0, jitter), 0.0))
    return pd.DataFrame(rows, columns=["timestamp", "hr", "steps"])


def day_index(ts):
    return (ts - D0).days + 1


def test_first_z_defined_day_follows_exactly_28_historical_days():
    """The reported defect: first z-defined day was 57, i.e. a ~56-day nested
    burn-in. It must be 29 -- 28 baseline-eligible historical days, then the
    first prediction."""
    res = tod_z.daily_statistics(record())
    assert day_index(res[res.valid].day.min()) == 29
    assert day_index(res[res.z_defined].day.min()) == 29


def test_no_nested_burn_in_between_D_and_z():
    """D-validity and z-definition must begin on the SAME day; a gap between them
    is the signature of the two-stage nesting."""
    res = tod_z.daily_statistics(record())
    assert res[res.valid].day.min() == res[res.z_defined].day.min()


def test_z_defined_count_matches_a_single_28_day_burn_in():
    res = tod_z.daily_statistics(record(days=150))
    assert int(res.z_defined.sum()) == 150 - 28


def test_baseline_never_reaches_past_the_90_day_lookback():
    res = tod_z.daily_statistics(record(days=200), trace_reads=True)
    r = res.dropna(subset=["min_baseline_timestamp_read"])
    assert len(r) > 0
    assert (r.min_baseline_timestamp_read
            >= r.day - pd.Timedelta(days=CFG.max_lookback_days)).all()
    assert (r.baseline_oldest >= r.day - pd.Timedelta(days=CFG.max_lookback_days)).all()


def test_data_older_than_the_lookback_cannot_change_z_even_indirectly():
    """Behavioural proof. Corrupting everything before d-90 must leave z_d
    untouched; under the old nested design those days fed historical D values
    that fed z_d."""
    clean = record(days=200)
    dirty = clean.copy()
    cutoff = D0 + pd.Timedelta(days=200 - 90)
    dirty.loc[dirty.timestamp < cutoff, "hr"] += 40.0
    a = tod_z.daily_statistics(clean)
    b = tod_z.daily_statistics(dirty)
    last = a.day.max()
    za = a.loc[a.day == last, "z"].iloc[0]
    zb = b.loc[b.day == last, "z"].iloc[0]
    assert np.isfinite(za) and abs(za - zb) < 1e-9


def test_sparse_and_dense_schedules_apply_the_identical_history_rule():
    dense = tod_z.daily_statistics(record(per_hour=6, seed=11))
    sparse = tod_z.daily_statistics(record(per_hour=1, seed=11))
    assert dense[dense.z_defined].day.min() == sparse[sparse.z_defined].day.min()
    assert int(dense.z_defined.sum()) == int(sparse.z_defined.sum())
    assert (dense.n_baseline_valid_days.to_numpy()
            == sparse.n_baseline_valid_days.to_numpy()).all()


def test_gaps_delay_the_first_prediction_by_the_number_of_missing_days():
    """Baseline days are counted as VALID days, not calendar days, so five missing
    days push the first prediction five days later -- and no further."""
    res = tod_z.daily_statistics(record(days=60, skip={3, 4, 5, 6, 7}))
    assert day_index(res[res.z_defined].day.min()) == 34


def test_no_future_timestamp_is_read():
    res = tod_z.daily_statistics(record(days=120), trace_reads=True)
    r = res.dropna(subset=["max_baseline_timestamp_read"])
    assert (r.max_baseline_timestamp_read < r.day).all()
    d = res.dropna(subset=["max_day_timestamp_read"])
    assert (d.max_day_timestamp_read < d.day + pd.Timedelta(days=1)).all()


def test_truncating_the_future_leaves_earlier_z_unchanged():
    full = record(days=200)
    cut = full[full.timestamp < D0 + pd.Timedelta(days=120)]
    a = tod_z.daily_statistics(full)
    b = tod_z.daily_statistics(cut)
    k = b.day.max()
    pd.testing.assert_frame_equal(
        a[a.day <= k][["day", "valid", "D", "z"]].reset_index(drop=True),
        b[b.day <= k][["day", "valid", "D", "z"]].reset_index(drop=True),
        check_exact=False)


def test_baseline_D_count_is_reported_and_equals_the_baseline_size():
    res = tod_z.daily_statistics(record())
    r = res[res.z_defined]
    assert (r.n_baseline_valid_days == CFG.baseline_days).all()
    assert (r.n_baseline_D >= CFG.baseline_days).all()


def test_one_mu_serves_both_the_history_and_the_current_day():
    """If mu were re-estimated per historical day, a constant record would still
    produce non-zero D_j scatter. With a single mu the scatter is exactly zero and
    the scale floor takes over, giving z = 0."""
    res = tod_z.daily_statistics(record(jitter=0.0))
    z = res.loc[res.z_defined, "z"]
    assert len(z) > 0 and np.allclose(z, 0.0, atol=1e-9)
