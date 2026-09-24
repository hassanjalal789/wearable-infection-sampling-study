from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import primary_e3_experiment as P


def fake_stats(start="2025-01-01", n=100, onset="2025-04-11"):
    days = pd.date_range(start, periods=n, freq="D")
    d = pd.DataFrame({
        "day": days,
        "z": np.zeros(n, dtype=float),
        "z_defined": True,
        "valid": True,
        "n_hr_samples": 10,
        "n_rest_samples": 10,
    })
    return d, pd.Timestamp(onset)


def test_calibration_uses_all_negative_days_through_onset_minus_28():
    res, onset = fake_stats()
    cal = P.calibration_frame(res, onset, [onset])
    assert len(cal) == 73
    assert cal["day"].max() == onset - pd.Timedelta(days=28)


def test_calibration_excludes_other_episode_window():
    res, onset = fake_stats()
    other = pd.Timestamp("2025-02-15")
    cal = P.calibration_frame(res, onset, [other, onset])
    assert not cal["day"].between(
        other - pd.Timedelta(days=21),
        other + pd.Timedelta(days=21),
    ).any()


def test_warning_uses_first_alert_and_nondetection_warning_stays_missing():
    res, onset = fake_stats()
    res.loc[
        res["day"].isin([
            onset - pd.Timedelta(days=10),
            onset - pd.Timedelta(days=9),
        ]),
        "z",
    ] = 10.0

    out = P.outcome_from_stats(res, onset, [onset], "S3")
    assert out["calibration_floor_met"] is True
    assert out["presymptomatic_detected"] is True
    assert out["warning_days"] == 9

    res["z"] = 0.0
    out2 = P.outcome_from_stats(res, onset, [onset], "S3")
    assert out2["presymptomatic_detected"] is False
    assert np.isnan(out2["warning_days"])


def test_fully_unevaluable_presymptomatic_window_is_not_nondetection():
    res, onset = fake_stats()
    m = res["day"].between(
        onset - pd.Timedelta(days=21),
        onset - pd.Timedelta(days=1),
    )
    res.loc[m, "z_defined"] = False
    res.loc[m, "z"] = np.nan
    out = P.outcome_from_stats(res, onset, [onset], "S3")
    assert pd.isna(out["presymptomatic_detected"])
    assert np.isnan(out["warning_days"])


def test_hierarchical_pair_rules():
    base = {
        "calibration_floor_met": True,
        "presymptomatic_detected": True,
        "warning_days": 5,
    }
    a = dict(base)
    b = dict(base, warning_days=3)
    assert P.hierarchical_pair(a, b)["result"] == "A_WIN"

    b = dict(base, presymptomatic_detected=False, warning_days=np.nan)
    assert P.hierarchical_pair(a, b)["result"] == "A_WIN"

    a2 = dict(base, presymptomatic_detected=False, warning_days=np.nan)
    assert P.hierarchical_pair(a2, b)["result"] == "TIE"

    b2 = dict(base, presymptomatic_detected=pd.NA, warning_days=np.nan)
    assert P.hierarchical_pair(a, b2)["result"] == "NA_OUTCOME"


def test_ambiguous_38_row_cohort_lists_fail_loudly(tmp_path):
    x = {
        "a": [["phase1", f"A{i}"] for i in range(38)],
        "b": [["phase2", f"P{i}"] for i in range(38)],
    }
    p = tmp_path / "cohort.json"
    p.write_text(json.dumps(x))
    try:
        P.load_final_cohort_pairs(p)
    except RuntimeError as e:
        assert "uniquely identify" in str(e)
    else:
        raise AssertionError("ambiguous cohort file must fail loudly")
