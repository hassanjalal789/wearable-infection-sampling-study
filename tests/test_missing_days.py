"""Zero-delivery calendar days must appear as UNEVALUABLE rows, not vanish."""
import numpy as np, pandas as pd, pytest
import tod_z

CFG = tod_z.TODZConfig()
D0 = pd.Timestamp("2021-01-01")


def rec(days=60, per_hour=6, seed=5, missing=(), nan_hr=(), scheduled_only=()):
    """`missing` days emit no rows at all; `nan_hr` days emit scheduled rows whose
    hr is NaN; `scheduled_only` days appear only via expected_days."""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(days):
        if i in missing or i in scheduled_only:
            continue
        day = D0 + pd.Timedelta(days=i)
        for h in range(7):
            for k in range(per_hour):
                ts = day + pd.Timedelta(hours=h, minutes=k * (60 // per_hour))
                hr = np.nan if i in nan_hr else 60 + rng.normal(0, 1.5)
                rows.append((ts, hr, 0.0))
    return pd.DataFrame(rows, columns=["timestamp", "hr", "steps"])


def cal(days=60):
    return pd.date_range(D0, periods=days)


def test_a_day_with_scheduled_rows_but_no_hr_is_present_and_unevaluable():
    res = tod_z.daily_statistics(rec(nan_hr={31}))
    r = res[res.day == D0 + pd.Timedelta(days=31)]
    assert len(r) == 1
    r = r.iloc[0]
    assert r.reason == "source_missing_day"
    assert r.valid is np.False_ or r.valid == False
    assert not r.z_defined and np.isnan(r.D) and np.isnan(r.z)
    assert r.n_rest_samples == 0 and r.n_hr_samples == 0


def test_a_completely_absent_day_is_recovered_from_the_expected_calendar():
    res = tod_z.daily_statistics(rec(missing={31}), expected_days=cal())
    r = res[res.day == D0 + pd.Timedelta(days=31)]
    assert len(r) == 1 and r.iloc[0].reason == "source_missing_day"
    assert len(res) == 60                      # every scheduled day represented once


def test_every_scheduled_day_appears_exactly_once():
    res = tod_z.daily_statistics(rec(missing={10, 11, 12}, nan_hr={40}),
                                 expected_days=cal())
    assert len(res) == 60
    assert res.day.is_unique
    assert set(res.day) == set(cal())


def test_several_consecutive_missing_days():
    res = tod_z.daily_statistics(rec(missing={20, 21, 22, 23, 24}), expected_days=cal())
    gap = res[res.day.isin(D0 + pd.to_timedelta(range(20, 25), unit="D"))]
    assert len(gap) == 5
    assert (gap.reason == "source_missing_day").all()
    assert (gap.n_hr_samples == 0).all()


def test_missing_days_are_counted_in_invalid_day_diagnostics():
    res = tod_z.daily_statistics(rec(missing={5, 6}, nan_hr={7}), expected_days=cal())
    counts = res.reason.value_counts()
    assert counts.get("source_missing_day", 0) == 3
    assert int((~res.z_defined).sum()) >= 3


def test_missing_days_do_not_count_toward_the_28_baseline_eligible_days():
    """Five missing days push the first prediction five days later, exactly."""
    clean = tod_z.daily_statistics(rec(days=60), expected_days=cal())
    holed = tod_z.daily_statistics(rec(days=60, missing={3, 4, 5, 6, 7}),
                                   expected_days=cal())
    first_clean = (clean[clean.z_defined].day.min() - D0).days
    first_holed = (holed[holed.z_defined].day.min() - D0).days
    assert first_clean == 28
    assert first_holed == 33


def test_a_missing_day_is_not_scored_as_a_non_detection():
    res = tod_z.daily_statistics(rec(missing={40}), expected_days=cal())
    r = res[res.day == D0 + pd.Timedelta(days=40)].iloc[0]
    assert not r.z_defined and np.isnan(r.z)
    assert r.reason == "source_missing_day"
    assert r.reason not in ("invalid_no_rest", "invalid_too_few")


def test_persistence_gap_rule_still_holds_across_a_missing_stretch():
    """Alert persistence counts consecutive VALID days no more than 3 calendar
    days apart; a missing stretch must break the run."""
    res = pd.DataFrame({"day": pd.to_datetime(["2021-03-01", "2021-03-09"]),
                        "z": [9.0, 9.0], "z_defined": [True, True]})
    assert not tod_z.alert_days(res, tau=2.0).any()


def test_missing_days_introduce_no_future_information():
    res = tod_z.daily_statistics(rec(days=120, missing={50, 51}),
                                 expected_days=cal(120), trace_reads=True)
    r = res.dropna(subset=["max_baseline_timestamp_read"])
    assert (r.max_baseline_timestamp_read < r.day).all()
    assert (r.min_baseline_timestamp_read
            >= r.day - pd.Timedelta(days=CFG.max_lookback_days)).all()


def test_expected_days_never_removes_an_observed_day():
    res = tod_z.daily_statistics(rec(days=60), expected_days=cal(30))
    assert len(res) == 60                      # union, not intersection


def test_z_values_are_unchanged_by_the_skeleton_patch():
    """Adding unevaluable rows must not perturb any surviving statistic."""
    df = rec(days=90)
    a = tod_z.daily_statistics(df)
    b = tod_z.daily_statistics(df, expected_days=cal(90))
    common = a.merge(b, on="day", suffixes=("_a", "_b"))
    np.testing.assert_allclose(common.z_a.to_numpy(), common.z_b.to_numpy(),
                               equal_nan=True)
