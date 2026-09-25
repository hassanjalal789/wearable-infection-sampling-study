#!/usr/bin/env python3
"""
Paired-design power / MDE simulation.  PREREGISTRATION ARTEFACT, v2.

Changes from v1 (post-review):
  P1  Cross-schedule dependence is NOT estimated from the S1 arm -- it cannot be
      identified from a single arm.  A preregistered SENSITIVITY GRID over
      within-participant dependence is swept instead, and MDE / precision are
      reported across the whole grid.  The S1 arm may inform only the MARGINAL
      baseline detection probability p_B, and that use is logged.
  P2  The simulated endpoint now matches the preregistered endpoint exactly:
      pre-symptomatic detection means a first qualifying alert in
      [onset-21, onset-1], so a detected participant always has warning >= 1 day.
      A 0-day (same-day) alert is NOT pre-symptomatic.
  P2b Precision for the paired warning-time difference is computed on the
      DETECTED-UNDER-BOTH subgroup, bootstrapped over that subgroup only.
      Non-detections are never zero-imputed into that estimate.

Primary test: exact binomial sign test on the hierarchical win/loss comparison,
identical to a within-participant sign-flip permutation test on theta
(proved numerically in verify_test_equivalence.py).
"""
from __future__ import annotations
import argparse, hashlib, json, sys
import numpy as np
from scipy.stats import binomtest, norm

SEED = 20261010
ALPHA = 0.05
N_MONTE_CARLO = 4000
W_MIN, W_MAX = 1, 21          # preregistered pre-symptomatic warning window, days

# ---- preregistered dependence sensitivity grid (P1) -------------------------
DEPENDENCE_GRID = {
    "independent": dict(rho_det=0.00, rho_lead=0.00),
    "low":         dict(rho_det=0.25, rho_lead=0.25),
    "moderate":    dict(rho_det=0.50, rho_lead=0.50),
    "high":        dict(rho_det=0.75, rho_lead=0.75),
}
AUDITED_N = None              # set from the eligibility audit before freezing
BASELINE_P_B = None           # may be set from the S1 reference arm; must be logged


def lam_from_rho(rho_det: float) -> float:
    """Frailty SD giving the requested latent (tetrachoric) detection correlation."""
    if not 0.0 <= rho_det < 1.0:
        raise ValueError("rho_det must be in [0, 1)")
    return float(np.sqrt(rho_det / (1.0 - rho_det)))


def tau_sigma_from_rho(rho_lead: float, total_sd: float = 2.0):
    """Split a fixed total warning-time SD into shared and idiosyncratic parts."""
    if not 0.0 <= rho_lead < 1.0:
        raise ValueError("rho_lead must be in [0, 1)")
    return float(total_sd * np.sqrt(rho_lead)), float(total_sd * np.sqrt(1.0 - rho_lead))


def warning_days(mu, v, noise):
    """Warning time in whole days, constrained to the preregistered window.

    P2: a pre-symptomatically detected participant has warning >= 1 by
    definition, because the endpoint window is [onset-21, onset-1].
    """
    return np.clip(np.round(mu + v + noise), W_MIN, W_MAX)


def simulate_cell(n, p_A, p_B, rho_det, rho_lead, mu_A, mu_B,
                  reps, rng, total_sd=2.0, alpha=ALPHA, ci_every=1):
    lam = lam_from_rho(rho_det)
    tau, sigma = tau_sigma_from_rho(rho_lead, total_sd)
    scale = np.sqrt(1.0 + lam ** 2)
    a_A, a_B = norm.ppf(p_A) * scale, norm.ppf(p_B) * scale

    rej = 0
    W_, L_, T_, th_ = [], [], [], []
    hw_theta, hw_days_both, hw_prop, n_both = [], [], [], []

    for _rep in range(reps):
        u = rng.normal(0.0, 1.0, n)
        dA = rng.normal(0.0, 1.0, n) + a_A + lam * u > 0.0
        dB = rng.normal(0.0, 1.0, n) + a_B + lam * u > 0.0

        v = rng.normal(0.0, tau, n)
        lA = warning_days(mu_A, v, rng.normal(0.0, sigma, n))
        lB = warning_days(mu_B, v, rng.normal(0.0, sigma, n))

        both = dA & dB
        win = (dA & ~dB) | (both & (lA > lB))
        loss = (~dA & dB) | (both & (lA < lB))
        tie = ~(win | loss)
        W, L, T = int(win.sum()), int(loss.sum()), int(tie.sum())
        W_.append(W); L_.append(L); T_.append(T); th_.append((W + 0.5 * T) / n)

        if W + L > 0 and binomtest(W, W + L, 0.5).pvalue < alpha:
            rej += 1

        nb = int(both.sum()); n_both.append(nb)
        if _rep % ci_every == 0:                       # CI widths on a subsample
            s = win.astype(float) + 0.5 * tie.astype(float)
            bs = rng.choice(s, size=(400, n), replace=True).mean(axis=1)
            hw_theta.append((np.percentile(bs, 97.5) - np.percentile(bs, 2.5)) / 2)

            # P2b: detected-under-both subgroup ONLY; no zero-imputation.
            if nb >= 2:
                d = (lA - lB)[both]
                bs = rng.choice(d, size=(400, nb), replace=True).mean(axis=1)
                hw_days_both.append((np.percentile(bs, 97.5) - np.percentile(bs, 2.5)) / 2)

            dp = dA.astype(int) - dB.astype(int)
            bs = rng.choice(dp, size=(400, n), replace=True).mean(axis=1)
            hw_prop.append((np.percentile(bs, 97.5) - np.percentile(bs, 2.5)) / 2)

    return dict(
        power=rej / reps, theta=float(np.mean(th_)),
        mean_W=float(np.mean(W_)), mean_L=float(np.mean(L_)), mean_T=float(np.mean(T_)),
        mean_discordant=float(np.mean(W_) + np.mean(L_)),
        mean_n_both=float(np.mean(n_both)),
        ci_hw_theta=float(np.mean(hw_theta)) if hw_theta else float("nan"),
        ci_hw_days_detected_both=(float(np.mean(hw_days_both)) if hw_days_both else float("nan")),
        ci_hw_detect_prop=float(np.mean(hw_prop)) if hw_prop else float("nan"),
    )


EFFECT_RAY = [(0.05, 0.5), (0.10, 1.0), (0.15, 1.5), (0.20, 2.0),
              (0.25, 2.5), (0.30, 3.0), (0.35, 3.5)]
"""The prespecified effect ray: detection gain and warning gain move TOGETHER in
a fixed 1 pp : 0.1 day proportion.  A result from this search is a MINIMUM
DETECTABLE JOINT EFFECT ALONG THIS RAY, not a one-dimensional MDE, and must
always be reported with the ray stated."""

DELTA_P_GRID = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25]
DELTA_DAYS_GRID = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]


def power_surface(n, p_B, mu_B, rho_det, rho_lead, reps, rng,
                  dp_grid=None, dd_grid=None, ci_every=10):
    """Two-dimensional power surface over delta-detection x delta-warning-days.

    PATCH 2(B).  Replaces the single-ray summary as the primary reporting object,
    because the ray conflates two effects that the design does not require to move
    together.  Each cell reports power, expected theta CI half-width, and expected
    CI half-width for the paired warning difference on the DETECTED-UNDER-BOTH
    subgroup.
    """
    dp_grid = DELTA_P_GRID if dp_grid is None else dp_grid
    dd_grid = DELTA_DAYS_GRID if dd_grid is None else dd_grid
    cells = []
    for dp in dp_grid:
        for dd in dd_grid:
            r = simulate_cell(n, min(p_B + dp, 0.98), p_B, rho_det, rho_lead,
                              mu_B + dd, mu_B, reps, rng, ci_every=ci_every)
            cells.append(dict(delta_p=dp, delta_days=dd, **r))
    return cells


def mde_search(n, p_B, mu_B, rho_det, rho_lead, reps, rng, target=0.80):
    """Smallest JOINT effect along EFFECT_RAY reaching `target` power.

    NOT a one-dimensional MDE.  Report as "minimum detectable joint effect along
    the prespecified effect ray (+1 pp detection : +0.1 day warning)".
    """
    for dp, dm in EFFECT_RAY:
        r = simulate_cell(n, min(p_B + dp, 0.98), p_B, rho_det, rho_lead,
                          mu_B + dm, mu_B, reps, rng)
        if r["power"] >= target:
            return dict(delta_p=dp, delta_mu_days=dm, **r)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audited", action="store_true")
    ap.add_argument("--reps", type=int, default=N_MONTE_CARLO)
    ap.add_argument("--p-b", type=float, default=None,
                    help="single marginal baseline detection probability; if taken "
                         "from the S1 arm it MUST be logged with --log-baseline")
    ap.add_argument("--sweep-p-b", type=str, default=None,
                    help="comma-separated baseline probabilities to sweep instead of "
                         "using a single value, e.g. 0.40,0.50,0.60 -- the cleanest "
                         "option, since it uses no result-derived input at all")
    ap.add_argument("--log-baseline", type=str, default=None)
    ap.add_argument("--surface", action="store_true",
                    help="produce the 2-D power surface (preferred reporting object)")
    ap.add_argument("--frozen", action="store_true",
                    help="mark this run as the frozen preregistration calculation; "
                         "requires --audited and reps >= 4000")
    ap.add_argument("--ci-every", type=int, default=10)
    ap.add_argument("--out", type=str, default=None)
    a = ap.parse_args()

    if a.audited and AUDITED_N is None:
        sys.exit("AUDITED_N is not set. Fill it from the eligibility audit first.")
    if a.frozen and not (a.audited and a.reps >= 4000):
        sys.exit("--frozen requires --audited and --reps >= 4000 (prereg A1/A3.7).")
    out_path = a.out or ("results/power_sim_FROZEN.json" if a.frozen
                         else "results/power_sim_PLANNING_do_not_cite.json")
    ns = [AUDITED_N] if a.audited else [25, 30, 40, 50]

    if a.sweep_p_b:
        p_bs = [float(x) for x in a.sweep_p_b.split(",")]
        p_b_source = "preregistered sweep; no result-derived input used"
    else:
        p_bs = [a.p_b if a.p_b is not None else (BASELINE_P_B or 0.50)]
        p_b_source = ("S1 reference arm marginal detection rate" if a.p_b is not None
                      else "default placeholder 0.50")
    if a.p_b is not None:
        rec = {"p_B": a.p_b, "source": "S1 reference arm marginal detection rate",
               "note": "This is the ONLY result-derived input to the power analysis. "
                       "Cross-schedule dependence is NOT identifiable from S1 and is "
                       "swept over the preregistered grid. No analysis rule is changed "
                       "on the basis of this value."}
        if a.log_baseline:
            open(a.log_baseline, "a").write(json.dumps(rec) + "\n")
        print("baseline provenance logged:", rec)

    rng = np.random.default_rng(SEED)
    rows = []
    print("PLANNING RUN — NOT BINDING\n" if not a.audited else "AUDITED RUN\n")
    hdr = (f"{'n':>4} {'dependence':>12} {'rho_d':>6} {'rho_L':>6} {'MDE dp':>7} "
           f"{'MDE dd':>7} {'power':>7} {'disc':>6} {'n_both':>7} {'CIhw_th':>8} {'CIhw_d*':>8}")
    print(hdr); print("-" * len(hdr))
    for n in ns:
      for p_B in p_bs:
        for name, g in DEPENDENCE_GRID.items():
            # PATCH 6: the documented replicate count IS the count used.
            m = mde_search(n, p_B, 3.0, g["rho_det"], g["rho_lead"], a.reps, rng)
            if m is None:
                print(f"{n:>4} {name:>12} {g['rho_det']:>6.2f} {g['rho_lead']:>6.2f} "
                      f"{'>0.35':>7} {'>3.5':>7} {'--':>7} {'--':>6} {'--':>7} {'--':>8} {'--':>8}")
                rows.append(dict(n=n, p_B=p_B, dependence=name, **g, mde=None)); continue
            print(f"{n:>4} {name:>12} {g['rho_det']:>6.2f} {g['rho_lead']:>6.2f} "
                  f"{m['delta_p']:>7.2f} {m['delta_mu_days']:>7.1f} {m['power']:>7.3f} "
                  f"{m['mean_discordant']:>6.1f} {m['mean_n_both']:>7.1f} "
                  f"{m['ci_hw_theta']:>8.3f} {m['ci_hw_days_detected_both']:>8.2f}")
            rows.append(dict(n=n, p_B=p_B, dependence=name, **g, mde=m))

    meta = dict(seed=SEED, reps_requested=a.reps,
                effective_reps_per_candidate_cell=a.reps,
                reps_note=("PATCH 6: mde_search now runs the FULL requested replicate "
                           "count for every candidate-effect cell. The previous "
                           "max(500, reps//4) reduction is removed, so the documented "
                           "and actual counts are identical."),
                frozen=bool(a.frozen),
                status=("FROZEN preregistration calculation" if a.frozen
                        else "PLANNING RUN — NOT BINDING, DO NOT CITE"),
                ci_every=a.ci_every,
                effect_ray=EFFECT_RAY,
                effect_ray_note=("mde_search moves detection gain and warning gain "
                                 "TOGETHER at +1 pp : +0.1 day. Its output is a MINIMUM "
                                 "DETECTABLE JOINT EFFECT ALONG THIS RAY, never a "
                                 "one-dimensional MDE, and must be reported with the "
                                 "ray stated. The 2-D surface is the preferred object."),
                alpha=ALPHA, p_B_values=p_bs, p_B_source=p_b_source,
                warning_window_days=[W_MIN, W_MAX],
                endpoint=("pre-symptomatic = first qualifying alert in [onset-21, onset-1]; "
                          "warning >= 1 day by construction; same-day alerts are NOT "
                          "pre-symptomatic"),
                precision_note=("paired warning-time CI is computed on the detected-under-"
                                "both subgroup with no zero-imputation"),
                dependence_note=("cross-schedule dependence is NOT identifiable from the S1 "
                                 "arm; it is swept over this preregistered grid"),
                test="exact binomial sign test on hierarchical win/loss",
                dependence_grid=DEPENDENCE_GRID, numpy=np.__version__,
                script_sha256=hashlib.sha256(open(__file__, "rb").read()).hexdigest())
    if a.surface:
        surf = []
        for n in ns:
            for p_B in p_bs:
                for name, g in DEPENDENCE_GRID.items():
                    for c in power_surface(n, p_B, 3.0, g["rho_det"], g["rho_lead"],
                                           a.reps, rng, ci_every=a.ci_every):
                        surf.append(dict(n=n, p_B=p_B, dependence=name, **g, **c))
        meta["surface_grid"] = dict(delta_p=DELTA_P_GRID, delta_days=DELTA_DAYS_GRID)
        json.dump(dict(meta=meta, ray_cells=rows, surface=surf),
                  open(out_path, "w"), indent=2, default=str)
    else:
        json.dump(dict(meta=meta, ray_cells=rows), open(out_path, "w"), indent=2, default=str)
    print("\nCIhw_d* = CI half-width for the paired warning difference, detected-under-both only.")
    print("wrote", out_path, " sha256(script) =", meta["script_sha256"][:16])


if __name__ == "__main__":
    main()
