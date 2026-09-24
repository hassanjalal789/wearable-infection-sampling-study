"""PATCH 1 and PATCH 2: minute-bin coverage and timestamp parsing precedence."""
import numpy as np, pandas as pd, pytest
import phase1_inventory as pi


def ts15(day="2020-08-12", hours=(0,), per_minute=4, minutes=1):
    """Synthetic 15-second HR: `per_minute` samples inside each minute."""
    out = []
    for h in hours:
        for m in range(minutes):
            for k in range(per_minute):
                out.append(pd.Timestamp(f"{day} {h:02d}:{m:02d}:{k*15:02d}"))
    return pd.Series(out)


def test_four_samples_in_one_minute_count_as_one_observed_minute():
    cov = pi.per_day_coverage(ts15(hours=(0,), per_minute=4, minutes=1))
    assert len(cov) == 1
    assert cov.raw_samples.iloc[0] == 4
    assert cov.night_observed_minutes.iloc[0] == 1
    assert cov.day_observed_minutes.iloc[0] == 0
    assert cov.observed_minutes.iloc[0] == 1


def test_night_and_day_bins_are_counted_independently():
    s = pd.concat([ts15(hours=(0, 3, 6), per_minute=4, minutes=5),
                   ts15(hours=(7, 12, 23), per_minute=4, minutes=5)])
    cov = pi.per_day_coverage(s)
    assert cov.night_observed_minutes.iloc[0] == 15      # 3 night hours x 5 min
    assert cov.day_observed_minutes.iloc[0] == 15        # 3 day hours x 5 min
    assert cov.raw_samples.iloc[0] == 120                # 30 minutes x 4 samples


def test_day_coverage_is_not_derived_by_subtracting_raw_samples():
    """The old bug: observed_minutes - night_samples. With 15 s data that is
    negative or nonsensical; the current code must be immune."""
    cov = pi.per_day_coverage(ts15(hours=(0,), per_minute=4, minutes=60))
    assert cov.night_observed_minutes.iloc[0] == 60
    assert cov.day_observed_minutes.iloc[0] == 0
    assert cov.raw_samples.iloc[0] == 240
    assert (cov.observed_minutes >= 0).all()


def test_invariants_hold_on_a_full_day():
    s = ts15(hours=tuple(range(24)), per_minute=4, minutes=60)
    cov = pi.per_day_coverage(s)
    r = cov.iloc[0]
    assert 0 <= r.night_observed_minutes <= 420
    assert 0 <= r.day_observed_minutes <= 1020
    assert r.observed_minutes == r.night_observed_minutes + r.day_observed_minutes
    assert r.observed_minutes <= 1440
    assert r.night_observed_minutes == 420 and r.day_observed_minutes == 1020


def test_hour_boundary_0659_is_night_and_0700_is_day():
    s = pd.Series([pd.Timestamp("2020-08-12 06:59:59"), pd.Timestamp("2020-08-12 07:00:00")])
    cov = pi.per_day_coverage(s)
    assert cov.night_observed_minutes.iloc[0] == 1
    assert cov.day_observed_minutes.iloc[0] == 1


def test_start_date_time_pair_beats_any_single_column():
    df = pd.DataFrame({"Device": ["HK Apple Watch"], "Start_Date": ["2021-05-04"],
                       "Start_Time": ["13:42:17"], "Heartrate": [70]})
    got = pi.parse_timestamps(df).iloc[0]
    assert got == pd.Timestamp("2021-05-04 13:42:17")
    assert got != pd.Timestamp("2021-05-04 00:00:00")


def test_pair_wins_even_when_a_generic_datetime_column_exists():
    df = pd.DataFrame({"Start_Date": ["2021-05-04"], "Start_Time": ["13:42:17"],
                       "datetime": ["1999-01-01 00:00:00"], "Heartrate": [70]})
    assert pi.parse_timestamps(df).iloc[0] == pd.Timestamp("2021-05-04 13:42:17")


def test_start_date_without_start_time_raises_instead_of_midnight():
    df = pd.DataFrame({"Start_Date": ["2021-05-04"], "Heartrate": [70]})
    with pytest.raises(RuntimeError, match="midnight"):
        pi.parse_timestamps(df)


def test_missing_timestamp_column_raises():
    with pytest.raises(RuntimeError, match="no timestamp column"):
        pi.parse_timestamps(pd.DataFrame({"a": [1], "b": [2]}))


def test_filename_without_device_token_is_unknown_not_fitbit():
    assert pi.classify("AHYIJDV_hr.csv")["device"] == "UNKNOWN"
    assert pi.classify("P682517-Fitbit-rhr.csv")["device"] == "Fitbit"
    assert pi.classify("P355472-AppleWatch-hr.csv")["device"] == "AppleWatch"
