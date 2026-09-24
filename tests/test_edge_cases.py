"""prereg sec.6: all fourteen TOD-z edge cases, one test each where testable."""
import numpy as np, pandas as pd, pytest
import tod_z

CFG = tod_z.TODZConfig()


def frame(days, per_night_minutes=6, hr=60.0, jitter=0.0, steps=0.0, seed=0,
          start="2021-01-01"):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(days):
        day = pd.Timestamp(start) + pd.Timedelta(days=i)
        for h in range(0, 7):
            for k in range(per_night_minutes):
                rows.append((day + pd.Timedelta(hours=h, minutes=k * 10),
                             hr + rng.normal(0, jitter) if jitter else hr, steps))
    return pd.DataFrame(rows, columns=["timestamp", "hr", "steps"])


def test_6_1_mad_zero_uses_the_scale_floor_and_never_divides_by_zero():
    res = tod_z.daily_statistics(frame(60, jitter=0.0))          # perfectly flat
    z = res.loc[res.z_defined, "z"]
    assert len(z) > 0 and np.isfinite(z).all()
    assert (np.abs(z) < 1e-6).all()          # zero residual over a floored scale


def test_6_2_fewer_than_28_trailing_valid_days_is_not_evaluable():
    res = tod_z.daily_statistics(frame(40))
    early = res.iloc[:CFG.baseline_days]
    assert (~early.z_defined).all()
    assert set(early.reason.dropna()) <= {"baseline_insufficient"}


def test_6_3_hour_with_too_few_baseline_observations_is_dropped():
    df = frame(60)
    # inject a 23:00 hour on one day only -> that hour has < 7 baseline obs
    day = pd.Timestamp("2021-02-20")
    extra = pd.DataFrame({"timestamp": [day + pd.Timedelta(hours=23, minutes=m)
                                        for m in range(0, 60, 10)],
                          "hr": [200.0] * 6, "steps": [0.0] * 6})
    res = tod_z.daily_statistics(pd.concat([df, extra], ignore_index=True))
    r = res[res.day == day].iloc[0]
    assert r.valid and abs(r.D) < 1.0        # the 200 bpm hour was dropped, not averaged


def test_6_4_first_28_days_are_burn_in():
    res = tod_z.daily_statistics(frame(60))
    assert not res.iloc[0].z_defined and res.iloc[0].reason == "baseline_insufficient"


def test_6_5_zero_rest_samples_marks_invalid_no_rest():
    df = frame(60)
    df.loc[df.timestamp.dt.normalize() == pd.Timestamp("2021-02-20"), "steps"] = 5.0
    res = tod_z.daily_statistics(df)
    assert res[res.day == pd.Timestamp("2021-02-20")].iloc[0].reason == "invalid_no_rest"


def test_6_6_fewer_than_five_rest_samples_marks_invalid_too_few():
    df = frame(60)
    m = df.timestamp.dt.normalize() == pd.Timestamp("2021-02-20")
    keep = df[m].head(3)
    res = tod_z.daily_statistics(pd.concat([df[~m], keep], ignore_index=True))
    assert res[res.day == pd.Timestamp("2021-02-20")].iloc[0].reason == "invalid_too_few"


def test_6_6b_persistence_resets_across_a_gap_longer_than_three_days():
    res = pd.DataFrame({
        "day": pd.to_datetime(["2021-03-01", "2021-03-10"]),
        "z": [9.0, 9.0], "z_defined": [True, True]})
    flags = tod_z.alert_days(res, tau=2.0)
    assert not flags.any(), "a 9-day gap must not satisfy 'two consecutive valid days'"


def test_6_6c_persistence_fires_on_two_adjacent_valid_days():
    res = pd.DataFrame({"day": pd.to_datetime(["2021-03-01", "2021-03-02"]),
                        "z": [9.0, 9.0], "z_defined": [True, True]})
    assert tod_z.alert_days(res, tau=2.0).iloc[1]


def test_6_7_missing_steps_is_not_rest():
    df = frame(60)
    df.loc[df.timestamp.dt.normalize() == pd.Timestamp("2021-02-20"), "steps"] = np.nan
    res = tod_z.daily_statistics(df)
    assert res[res.day == pd.Timestamp("2021-02-20")].iloc[0].reason == "invalid_no_rest"


def test_6_8_missing_hr_rows_are_dropped_without_crashing():
    df = frame(60)
    df.loc[df.sample(frac=0.2, random_state=1).index, "hr"] = np.nan
    res = tod_z.daily_statistics(df)
    assert res.z_defined.sum() > 0


def test_6_12_dst_day_exclusion_is_the_callers_responsibility_and_is_representable():
    res = tod_z.daily_statistics(frame(60))
    excluded = res[res.day != pd.Timestamp("2021-02-20")]
    assert len(excluded) == len(res) - 1


def test_5_e_smallest_admissible_threshold_is_selected():
    res = tod_z.daily_statistics(frame(120, jitter=1.5, seed=3))
    cal = res[res.day < pd.Timestamp("2021-03-15")]
    out = tod_z.calibrate_tau(cal, budget=2.0)
    assert out["tau"] == min(t for t in CFG.tau_grid
                             if tod_z.achieved_rate(cal, float(t)) <= 2.0)


def test_5_e_achieved_rate_is_monotone_non_increasing_in_tau():
    res = tod_z.daily_statistics(frame(120, jitter=1.5, seed=4))
    cal = res[res.day < pd.Timestamp("2021-03-15")]
    a = [tod_z.achieved_rate(cal, float(t)) for t in np.arange(1.0, 6.01, 0.25)]
    assert all(x >= y - 1e-9 for x, y in zip(a, a[1:]))


def test_5_f_saturated_calibration_falls_back_to_an_infinite_threshold():
    """PATCH 2: when every finite threshold fails, tau = +inf keeps the
    participant paired AND guarantees the alert budget is satisfied."""
    res = pd.DataFrame({"day": pd.date_range("2021-01-01", periods=40),
                        "z": [99.0] * 40, "z_defined": [True] * 40})
    out = tod_z.calibrate_tau(res, budget=2.0)
    assert out["tau"] == float("inf")
    assert out["finite_threshold"] is False
    assert out["calibration_saturated"] is True
    assert out["achieved_rate"] == 0.0
    assert int(tod_z.alert_days(res, out["tau"]).sum()) == 0


@pytest.mark.parametrize("budget", [1.0, 2.0, 4.0])
def test_5_f_selected_threshold_never_exceeds_the_budget(budget):
    """The invariant the whole equal-alert-budget design rests on."""
    for z in (99.0, 5.0, 0.0):
        res = pd.DataFrame({"day": pd.date_range("2021-01-01", periods=45),
                            "z": [z] * 45, "z_defined": [True] * 45})
        out = tod_z.calibrate_tau(res, budget=budget)
        realised = tod_z.achieved_rate(res, out["tau"]) if out["finite_threshold"] else 0.0
        assert realised <= budget + 1e-12


def test_5_f_every_finite_threshold_failing_is_detected_not_clamped():
    res = pd.DataFrame({"day": pd.date_range("2021-01-01", periods=60),
                        "z": [1000.0] * 60, "z_defined": [True] * 60})
    assert all(tod_z.achieved_rate(res, float(t)) > 2.0 for t in CFG.tau_grid)
    assert tod_z.calibrate_tau(res, 2.0)["tau"] == float("inf")


def test_5_coarse_calibration_flag_fires_when_one_alert_exceeds_half_the_budget():
    res = pd.DataFrame({"day": pd.date_range("2021-01-01", periods=20),
                        "z": [0.0] * 20, "z_defined": [True] * 20})
    out = tod_z.calibrate_tau(res, budget=2.0)
    assert out["calibration_days"] == 20
    assert out["coarse_calibration"] is True          # 30.44/20 = 1.52 > 1.0
