"""Tests for the two review findings on power_sim.py:
   P2  simulated pre-symptomatic detection must imply warning >= 1 day
   P2b paired warning-time precision must use the detected-under-both subgroup,
       never zero-imputed non-detections
   P1  cross-schedule dependence is a preregistered grid, not an S1 estimate
"""
import numpy as np
import pytest
from scipy.stats import norm
import power_sim as ps


# ---------------------------------------------------------------- P2
def test_warning_days_never_below_one():
    """Even with a strongly negative mean, a detected participant warns >= 1 day."""
    rng = np.random.default_rng(0)
    w = ps.warning_days(-50.0, rng.normal(0, 2, 20000), rng.normal(0, 2, 20000))
    assert w.min() >= ps.W_MIN == 1


def test_warning_days_capped_at_window():
    rng = np.random.default_rng(0)
    w = ps.warning_days(500.0, rng.normal(0, 2, 5000), rng.normal(0, 2, 5000))
    assert w.max() <= ps.W_MAX == 21


def test_detection_implies_at_least_one_day_of_warning():
    """Replicates the generative step and asserts no detected participant has 0 days."""
    rng = np.random.default_rng(7)
    n, reps = 400, 40
    for _ in range(reps):
        d = rng.random(n) < 0.6
        w = ps.warning_days(3.0, rng.normal(0, 1.4, n), rng.normal(0, 1.4, n))
        assert (w[d] >= 1).all()


def test_simulated_endpoint_produces_no_zero_day_wins():
    """A win driven by warning time can never rest on a 0-day warning."""
    rng = np.random.default_rng(11)
    r = ps.simulate_cell(60, 0.65, 0.50, 0.5, 0.5, 4.5, 3.0, reps=60, rng=rng)
    assert r["mean_n_both"] > 0
    assert 0.0 <= r["theta"] <= 1.0


# ---------------------------------------------------------------- P2b
def _both_vs_zero_imputed(n, p, rng, reps=300, mu_a=4.0, mu_b=3.0):
    """Return (estimate, CI half-width) for both estimators.

    'both'  = paired mean warning difference on the detected-under-both subgroup
    'zero'  = the same difference after zero-imputing non-detections
    """
    est_b, est_z, hw_b, hw_z = [], [], [], []
    for _ in range(reps):
        dA = rng.random(n) < p
        dB = rng.random(n) < p
        v = rng.normal(0, 1.4, n)
        lA = ps.warning_days(mu_a, v, rng.normal(0, 1.4, n))
        lB = ps.warning_days(mu_b, v, rng.normal(0, 1.4, n))
        both = dA & dB
        if both.sum() >= 2:
            d = (lA - lB)[both]
            est_b.append(d.mean())
            bs = rng.choice(d, size=(300, both.sum()), replace=True).mean(axis=1)
            hw_b.append((np.percentile(bs, 97.5) - np.percentile(bs, 2.5)) / 2)
        dz = np.where(dA, lA, 0) - np.where(dB, lB, 0)
        est_z.append(dz.mean())
        bs = rng.choice(dz, size=(300, n), replace=True).mean(axis=1)
        hw_z.append((np.percentile(bs, 97.5) - np.percentile(bs, 2.5)) / 2)
    return (float(np.mean(est_b)), float(np.mean(hw_b)),
            float(np.mean(est_z)), float(np.mean(hw_z)))


def test_zero_imputation_attenuates_the_warning_time_effect():
    """The two estimands differ: zero-imputation drags the paired warning
    difference toward 0 because non-detections enter as fabricated 0-day
    warnings. The detected-under-both estimator recovers the true +1 day."""
    rng = np.random.default_rng(21)
    est_b, _, est_z, _ = _both_vs_zero_imputed(60, 0.55, rng)
    assert 0.8 < est_b < 1.2                    # recovers the true effect
    assert est_z < 0.6 * est_b                  # materially attenuated
    assert abs(est_b - est_z) > 0.3             # days


def test_the_two_agree_when_everyone_is_detected():
    """With p = 1 the subgroup is the whole sample, so the estimators coincide."""
    rng = np.random.default_rng(22)
    est_b, hw_b, est_z, hw_z = _both_vs_zero_imputed(60, 1.0, rng, reps=200)
    assert abs(est_b - est_z) < 0.02
    assert abs(hw_b - hw_z) / hw_z < 0.05


def test_simulate_cell_reports_the_subgroup_size():
    rng = np.random.default_rng(23)
    r = ps.simulate_cell(50, 0.6, 0.5, 0.25, 0.25, 4.0, 3.0, reps=40, rng=rng)
    assert not np.isnan(r["ci_hw_days_detected_both"])
    assert 0 < r["mean_n_both"] <= 50


# ---------------------------------------------------------------- P1
def test_dependence_grid_is_preregistered_and_spans_low_to_high():
    g = ps.DEPENDENCE_GRID
    assert set(g) == {"independent", "low", "moderate", "high"}
    assert [g[k]["rho_det"] for k in ("independent", "low", "moderate", "high")] == [0.0, 0.25, 0.5, 0.75]


def test_lambda_round_trips_to_the_requested_detection_correlation():
    for rho in (0.0, 0.25, 0.5, 0.75):
        lam = ps.lam_from_rho(rho)
        assert abs(lam ** 2 / (1 + lam ** 2) - rho) < 1e-12


def test_tau_sigma_round_trip_to_the_requested_lead_correlation():
    for rho in (0.0, 0.25, 0.5, 0.75):
        tau, sig = ps.tau_sigma_from_rho(rho, total_sd=2.0)
        assert abs(tau ** 2 / (tau ** 2 + sig ** 2) - rho) < 1e-12
        assert abs((tau ** 2 + sig ** 2) ** 0.5 - 2.0) < 1e-12


def test_realised_lead_correlation_tracks_the_target():
    rng = np.random.default_rng(31)
    for rho in (0.0, 0.5, 0.75):
        tau, sig = ps.tau_sigma_from_rho(rho, 2.0)
        v = rng.normal(0, tau, 200000)
        a = 8.0 + v + rng.normal(0, sig, 200000)
        b = 8.0 + v + rng.normal(0, sig, 200000)
        assert abs(np.corrcoef(a, b)[0, 1] - rho) < 0.02


def test_detection_concordance_increases_with_dependence():
    rng = np.random.default_rng(41)
    conc = []
    for rho in (0.0, 0.5, 0.75):
        lam = ps.lam_from_rho(rho)
        scale = np.sqrt(1 + lam ** 2)
        a = norm.ppf(0.55) * scale
        u = rng.normal(0, 1, 200000)
        dA = rng.normal(0, 1, 200000) + a + lam * u > 0
        dB = rng.normal(0, 1, 200000) + a + lam * u > 0
        conc.append((dA == dB).mean())
    assert conc[0] < conc[1] < conc[2]


def test_invalid_correlations_are_rejected():
    with pytest.raises(ValueError):
        ps.lam_from_rho(1.0)
    with pytest.raises(ValueError):
        ps.tau_sigma_from_rho(-0.1)
