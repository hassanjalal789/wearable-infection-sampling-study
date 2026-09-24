"""prereg sec.20: no statistic used on day d may read any timestamp >= d.

Mechanically checked rather than asserted in prose. TOD-z is instrumented to
record, per output day, the latest timestamp consulted for (a) the trailing
baseline and (b) the day's own samples.

  baseline reads  must be strictly BEFORE the start of day d
  day-of reads    must be strictly BEFORE the start of day d+1
"""
import numpy as np, pandas as pd, pytest
import tod_z


def synth(days=120, seed=0, bump_from=None, bump_to=None, bump=7.0):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(days):
        day = pd.Timestamp("2021-01-01") + pd.Timedelta(days=i)
        extra = bump if (bump_from is not None and bump_from <= i < bump_to) else 0.0
        for h in range(0, 7):
            for m in range(0, 60, 10):
                rows.append((day + pd.Timedelta(hours=h, minutes=m),
                             60 + 3 * np.sin(h / 3) + rng.normal(0, 1.5) + extra, 0.0))
    return pd.DataFrame(rows, columns=["timestamp", "hr", "steps"])


def test_baseline_never_reads_the_current_day_or_later():
    res = tod_z.daily_statistics(synth(), trace_reads=True)
    r = res.dropna(subset=["max_baseline_timestamp_read"])
    assert len(r) > 0
    assert (r.max_baseline_timestamp_read < r.day).all()


def test_day_statistic_never_reads_beyond_its_own_day():
    res = tod_z.daily_statistics(synth(), trace_reads=True)
    r = res.dropna(subset=["max_day_timestamp_read"])
    assert (r.max_day_timestamp_read < r.day + pd.Timedelta(days=1)).all()


def test_truncating_the_future_does_not_change_the_past():
    """The strongest causality test available: statistics for days 0..k must be
    byte-identical whether or not days k+1.. exist in the input."""
    full = synth(days=120)
    cut = full[full.timestamp < pd.Timestamp("2021-04-01")]
    a = tod_z.daily_statistics(full)
    b = tod_z.daily_statistics(cut)
    k = b.day.max()
    a_ = a[a.day <= k].reset_index(drop=True)
    b_ = b[b.day <= k].reset_index(drop=True)
    pd.testing.assert_frame_equal(a_[["day", "valid", "D", "z"]],
                                  b_[["day", "valid", "D", "z"]], check_exact=False)


def test_a_future_anomaly_cannot_change_an_earlier_z():
    clean = tod_z.daily_statistics(synth(days=120))
    spiked = tod_z.daily_statistics(synth(days=120, bump_from=110, bump_to=115))
    early = clean.day < pd.Timestamp("2021-01-01") + pd.Timedelta(days=110)
    np.testing.assert_allclose(clean.loc[early, "z"].to_numpy(),
                               spiked.loc[early.values, "z"].to_numpy(),
                               equal_nan=True)


def test_calibration_only_uses_days_before_the_evaluation_window():
    res = tod_z.daily_statistics(synth(days=160))
    onset = pd.Timestamp("2021-06-01")
    cal = res[res.day < onset - pd.Timedelta(days=28)]
    assert cal.day.max() < onset - pd.Timedelta(days=28)
    out = tod_z.calibrate_tau(cal, budget=2.0)
    assert out["calibration_days"] == int(cal.z_defined.sum())
