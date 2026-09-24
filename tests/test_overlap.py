"""PATCH 3: the overlap check must not apply a bpm threshold to minute counts,
must only call something an HR identity test when it compares real bpm, and must
refuse any series comparison when calendar alignment is invalid."""
import numpy as np, pandas as pd, pytest
import check_overlap as co


def inv_rows(phase, pid, start, days, night, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "phase": phase, "participant_id": pid,
        "date": pd.date_range(start, periods=days).astype(str),
        "night_observed_minutes": np.clip(night + rng.integers(-3, 4, days), 0, 420),
        "day_observed_minutes": 600, "observed_minutes": 600 + night,
        "raw_samples": 5000, "device": "Fitbit", "source_file": f"{pid}_hr.csv"})


def hr_rows(phase, pid, start, days, base_bpm, seed=0, jitter=2.0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "phase": phase, "participant_id": pid,
        "date": pd.date_range(start, periods=days).astype(str),
        "nightly_median_rhr_bpm": base_bpm + rng.normal(0, jitter, days)})


def test_shared_identifier_is_overlap_found():
    inv = pd.concat([inv_rows("phase1", "X1", "2020-06-01", 40, 300),
                     inv_rows("phase2", "X1", "2021-01-01", 40, 300)])
    assert co.investigate(inv)["verdict"] == "OVERLAP_FOUND"


def test_implausible_dates_block_every_series_comparison():
    inv = pd.concat([inv_rows("phase1", "A", "2020-06-01", 40, 300),
                     inv_rows("phase2", "P1", "2026-01-03", 40, 300)])
    out = co.investigate(inv)
    assert out["verdict"] == "UNDETERMINABLE"
    assert out["hr_series_check_performed"] is False
    assert out["supplementary_coverage_check_performed"] is False


def test_without_hr_series_the_verdict_is_undeterminable_not_no_evidence():
    """PATCH 3: coverage similarity alone must never decide the verdict."""
    inv = pd.concat([inv_rows("phase1", "A", "2021-01-01", 60, 300, seed=1),
                     inv_rows("phase2", "P8", "2021-01-01", 60, 90, seed=9)])
    out = co.investigate(inv, hr_path=None)
    assert out["verdict"] == "UNDETERMINABLE"
    assert out["hr_series_check_performed"] is False
    assert out["supplementary_coverage_check_performed"] is True
    assert "NOT an HR-series identity test" in out["basis"]


def test_coverage_comparison_reports_minutes_and_no_bpm_threshold(tmp_path):
    a = pd.Series([300.0] * 30, index=pd.date_range("2021-01-01", periods=30))
    b = pd.Series([301.0] * 30, index=pd.date_range("2021-01-01", periods=30))
    c = co.compare_coverage(a, b)
    assert c["units"] == "minutes"
    assert "mad_bpm" not in c and "coverage_corr" in c


def test_real_hr_series_flags_a_planted_duplicate(tmp_path):
    base = hr_rows("phase1", "A", "2021-01-01", 60, 58.0, seed=3)
    dup = base.copy(); dup["phase"] = "phase2"; dup["participant_id"] = "P9"
    other = hr_rows("phase2", "P8", "2021-01-01", 60, 72.0, seed=44)
    f = tmp_path / "hr.csv"
    pd.concat([base, dup, other]).to_csv(f, index=False)
    inv = pd.concat([inv_rows("phase1", "A", "2021-01-01", 60, 300),
                     inv_rows("phase2", "P9", "2021-01-01", 60, 300),
                     inv_rows("phase2", "P8", "2021-01-01", 60, 300)])
    out = co.investigate(inv, hr_path=str(f))
    assert out["hr_series_check_performed"] is True
    assert out["verdict"] == "OVERLAP_FOUND"
    assert any(p["phase1"] == "A" and p["phase2"] == "P9" for p in out["flagged_pairs"])
    assert all("mad_bpm" in p for p in out["flagged_pairs"])


def test_real_hr_series_unrelated_gives_no_evidence_never_disjointness(tmp_path):
    f = tmp_path / "hr.csv"
    pd.concat([hr_rows("phase1", "A", "2021-01-01", 60, 58.0, seed=3),
               hr_rows("phase2", "P8", "2021-01-01", 60, 74.0, seed=88)]).to_csv(f, index=False)
    inv = pd.concat([inv_rows("phase1", "A", "2021-01-01", 60, 300),
                     inv_rows("phase2", "P8", "2021-01-01", 60, 300)])
    out = co.investigate(inv, hr_path=str(f))
    assert out["verdict"] == "NO_EVIDENCE_OF_OVERLAP"
    assert "NOT a finding of disjointness" in out["basis"]


def test_hr_series_file_missing_columns_raises(tmp_path):
    f = tmp_path / "bad.csv"
    pd.DataFrame({"phase": ["phase1"], "participant_id": ["A"]}).to_csv(f, index=False)
    with pytest.raises(RuntimeError, match="missing columns"):
        co.hr_series(str(f))
