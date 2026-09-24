from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import sensitivity_analysis as S
import primary_e3_experiment as P


def test_even_rank_selection_exact_and_deterministic():
    mins = pd.date_range("2025-01-01", periods=10, freq="min")
    a = S._select_even_rank(mins, 4)
    b = S._select_even_rank(mins, 4)
    assert len(a) == 4
    assert a.equals(b)
    assert set(a).issubset(set(mins))


def test_equalize_m1_frames_matches_delivered_minutes_per_day():
    day = pd.Timestamp("2025-01-01")
    a_mins = pd.date_range(day, periods=10, freq="min")
    b_mins = pd.date_range(day, periods=6, freq="min")

    def frame(mins):
        return pd.DataFrame({
            "timestamp": mins + pd.Timedelta(seconds=5),
            "hr": np.arange(len(mins)) + 60.0,
            "steps": 0.0,
        })

    frames = {"S3r": frame(a_mins), "S6": frame(b_mins)}
    out, qc = S.equalize_m1_frames(frames, pd.DatetimeIndex([day]))

    assert out["S3r"]["timestamp"].dt.floor("min").nunique() == 6
    assert out["S6"]["timestamp"].dt.floor("min").nunique() == 6
    assert int(qc.iloc[0]["matched_minutes"]) == 6


def test_no_tod_first_z_requires_28_baseline_eligible_days():
    cfg = P.TODZConfig()
    days = pd.date_range("2025-01-01", periods=30, freq="D")
    rows = []
    for i, d in enumerate(days):
        for m in range(5):
            rows.append({
                "timestamp": d + pd.Timedelta(hours=1, minutes=m),
                "hr": 60.0 + i * 0.01,
                "steps": 0.0,
            })
    df = pd.DataFrame(rows)
    res = S.no_tod_daily_statistics(df, cfg, days)
    assert res.iloc[:28]["z_defined"].sum() == 0
    assert bool(res.iloc[28]["z_defined"])


def test_fixed_budget_nondetection_warning_is_missing():
    cfg = P.TODZConfig()
    days = pd.date_range("2025-01-01", periods=100, freq="D")
    onset = pd.Timestamp("2025-04-11")
    res = pd.DataFrame({
        "day": days,
        "z": np.zeros(len(days)),
        "z_defined": True,
        "valid": True,
    })
    out = S.fixed_budget_outcome(
        res, onset, [onset], "S3", "phaseX", "PX", 4.0, cfg
    )
    assert out["calibration_floor_met"]
    assert out["presymptomatic_detected"] is False
    assert np.isnan(out["warning_days"])


def test_sensitivity_summary_contains_no_p_values():
    ph = pd.DataFrame([
        {"phase":"p","participant_id":"1","comparison":"H1","A":"S3","B":"S2","result":"A_WIN"},
        {"phase":"p","participant_id":"2","comparison":"H1","A":"S3","B":"S2","result":"B_WIN"},
        {"phase":"p","participant_id":"3","comparison":"H1","A":"S3","B":"S2","result":"TIE"},
    ])
    out = S.summarize_pairs(ph, "unit", 1)
    row = out[out["comparison"] == "H1"].iloc[0]
    assert row["N"] == 3
    assert row["theta"] == 0.5
    assert pd.isna(row["sensitivity_p_value"])
