from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import primary_e3_experiment as P


def _hr():
    return pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2025-01-01 00:00:05",
            "2025-01-01 00:00:45",
            "2025-01-01 00:01:10",
            "2025-01-01 00:02:20",
            "2025-01-01 00:03:30",
        ]),
        "hr": [60, 61, 62, 63, 64],
    })


def _steps():
    idx = pd.to_datetime([
        "2025-01-01 00:01:00",
        "2025-01-01 00:02:00",
        "2025-01-01 00:04:00",
    ])
    return pd.Series([7.0, np.nan, 3.0], index=idx, name="steps")


def test_phase2_infers_zero_only_when_hr_minute_has_no_step_record():
    out, meta = P.normalise_step_semantics("phase2", _hr(), _steps())
    assert out.loc[pd.Timestamp("2025-01-01 00:00:00")] == 0.0
    assert out.loc[pd.Timestamp("2025-01-01 00:03:00")] == 0.0
    assert meta["n_phase2_zero_step_minutes_inferred"] == 2


def test_phase2_preserves_explicit_active_and_explicit_nan_step_records():
    out, _ = P.normalise_step_semantics("phase2", _hr(), _steps())
    assert out.loc[pd.Timestamp("2025-01-01 00:01:00")] == 7.0
    assert pd.isna(out.loc[pd.Timestamp("2025-01-01 00:02:00")])


def test_phase2_does_not_infer_minutes_without_hr():
    out, _ = P.normalise_step_semantics("phase2", _hr(), _steps())
    assert out.loc[pd.Timestamp("2025-01-01 00:04:00")] == 3.0
    assert pd.Timestamp("2025-01-01 00:05:00") not in out.index


def test_phase1_is_unchanged():
    src = _steps()
    out, meta = P.normalise_step_semantics("phase1", _hr(), src)
    pd.testing.assert_series_equal(out, src.sort_index())
    assert meta["phase2_sparse_step_semantics_applied"] is False
    assert meta["n_phase2_zero_step_minutes_inferred"] == 0


def test_day_input_receives_inferred_zero_active_and_unknown_distinctly():
    hr = _hr()
    out, _ = P.normalise_step_semantics("phase2", hr, _steps())
    di = P._day_input("phase2", "PX", pd.Timestamp("2025-01-01"), hr, out)
    assert di.steps[0] == 0.0
    assert di.steps[1] == 7.0
    assert pd.isna(di.steps[2])
    assert di.steps[3] == 0.0
