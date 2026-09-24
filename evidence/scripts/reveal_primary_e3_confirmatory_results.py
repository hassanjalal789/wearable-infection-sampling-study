#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

ROOT = Path.home() / "rq1"
RUN = ROOT / "results" / "primary_e3_run_83cc8d1"
OUT = RUN / "confirmatory_analysis"
OUT.mkdir(exist_ok=True)

ALPHA = 0.05
BOOT_N = 10_000
BOOT_SEED = 20260902

COMPARISONS = [
    ("H1", "S3", "S2"),
    ("M1", "S3r", "S6"),
    ("H2", "S3", "S5"),
    ("H3", "S3", "S4"),
]


def exact_binom_two_sided(w: int, l: int) -> float:
    n = w + l
    if n == 0:
        return float("nan")
    probs = [math.comb(n, k) * (0.5 ** n) for k in range(n + 1)]
    p_obs = probs[w]
    return min(1.0, sum(p for p in probs if p <= p_obs + 1e-15))


def bca_ci(x: np.ndarray, n_boot: int = BOOT_N, seed: int = BOOT_SEED,
           alpha: float = 0.05) -> tuple[float, float]:
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 2:
        return (float("nan"), float("nan"))

    obs = float(x.mean())
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    boot = x[idx].mean(axis=1)

    # Bias correction with half-weight for exact bootstrap ties.
    prop = ((boot < obs).sum() + 0.5 * (boot == obs).sum()) / n_boot
    eps = 0.5 / n_boot
    prop = min(max(prop, eps), 1 - eps)
    nd = NormalDist()
    z0 = nd.inv_cdf(prop)

    jack = np.array([np.delete(x, i).mean() for i in range(n)], dtype=float)
    jm = jack.mean()
    num = np.sum((jm - jack) ** 3)
    den = 6.0 * (np.sum((jm - jack) ** 2) ** 1.5)
    acc = 0.0 if den == 0 else float(num / den)

    def adj(q: float) -> float:
        z = nd.inv_cdf(q)
        denom = 1.0 - acc * (z0 + z)
        if abs(denom) < 1e-12:
            return q
        return nd.cdf(z0 + (z0 + z) / denom)

    qlo = min(max(adj(alpha / 2), 0.0), 1.0)
    qhi = min(max(adj(1 - alpha / 2), 0.0), 1.0)
    if qlo > qhi:
        qlo, qhi = qhi, qlo
    return float(np.quantile(boot, qlo)), float(np.quantile(boot, qhi))


def fmt_p(p):
    if pd.isna(p):
        return "NA"
    if p < 0.0001:
        return "<0.0001"
    return f"{p:.4f}"


def boolish(s):
    if s.dtype == bool:
        return s
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


o = pd.read_csv(RUN / "arm_outcomes.csv")
ph = pd.read_csv(RUN / "pair_hierarchy.csv")
pm = pd.read_csv(RUN / "participant_input_and_m1_summary.csv")
manifest = json.loads((RUN / "run_manifest.json").read_text())

if not str(manifest.get("git_commit", "")).startswith("83cc8d1"):
    raise SystemExit("Wrong run commit.")
if len(o) != 266 or len(ph) != 152:
    raise SystemExit("Unexpected corrected-run table dimensions.")

# The QC showed M1's >40% unavailability stop is not triggered.
m1_frac = pd.to_numeric(pm["m1_unavailable_event_fraction"], errors="coerce")
m1_inconclusive_by_construction = bool((m1_frac > 0.40).any())
if m1_inconclusive_by_construction:
    raise SystemExit(
        "M1 construction stop unexpectedly triggered: at least one participant >40% unavailable."
    )

records = []
for j, (label, A, B) in enumerate(COMPARISONS):
    pp = ph[ph["comparison"] == label].copy()
    pp["evaluable"] = pp["result"].isin(["A_WIN", "B_WIN", "TIE"])
    pe = pp[pp["evaluable"]].copy()

    W = int((pe["result"] == "A_WIN").sum())
    L = int((pe["result"] == "B_WIN").sum())
    T = int((pe["result"] == "TIE").sum())
    n = int(len(pe))
    if W + L + T != n:
        raise RuntimeError(f"{label}: W/L/T do not sum to N.")

    theta = (W + 0.5 * T) / n if n else float("nan")
    x = np.r_[
        np.ones(W, dtype=float),
        np.zeros(L, dtype=float),
        np.full(T, 0.5, dtype=float),
    ]
    ci_lo, ci_hi = bca_ci(x, seed=BOOT_SEED + j) if n else (np.nan, np.nan)
    p = exact_binom_two_sided(W, L)
    wr = (W / L) if L else (float("inf") if W else float("nan"))

    ids = pe[["phase", "participant_id"]].drop_duplicates()
    oa = o[o["arm"] == A].merge(ids, on=["phase", "participant_id"], how="inner")
    ob = o[o["arm"] == B].merge(ids, on=["phase", "participant_id"], how="inner")

    def arm_desc(d):
        det = d["presymptomatic_detected"].astype("boolean")
        evaluable = det.notna()
        detected = det.fillna(False).astype(bool)
        wd = pd.to_numeric(d.loc[detected, "warning_days"], errors="coerce").dropna()
        return {
            "eval_n": int(evaluable.sum()),
            "detected_n": int((det[evaluable] == True).sum()),
            "detected_rate": (
                float((det[evaluable] == True).mean()) if evaluable.sum() else np.nan
            ),
            "warning_median": float(wd.median()) if len(wd) else np.nan,
            "warning_iqr_lo": float(wd.quantile(.25)) if len(wd) else np.nan,
            "warning_iqr_hi": float(wd.quantile(.75)) if len(wd) else np.nan,
        }

    ad = arm_desc(oa)
    bd = arm_desc(ob)

    records.append({
        "comparison": label,
        "A": A,
        "B": B,
        "N_pair": n,
        "W": W,
        "L": L,
        "T": T,
        "theta": theta,
        "theta_bca95_lo": ci_lo,
        "theta_bca95_hi": ci_hi,
        "win_ratio_W_over_L": wr,
        "discordant_W_plus_L": W + L,
        "p_exact_two_sided": p,
        "A_eval_n": ad["eval_n"],
        "A_detected_n": ad["detected_n"],
        "A_detection_rate": ad["detected_rate"],
        "A_warning_median_days_detected_only": ad["warning_median"],
        "A_warning_iqr_lo": ad["warning_iqr_lo"],
        "A_warning_iqr_hi": ad["warning_iqr_hi"],
        "B_eval_n": bd["eval_n"],
        "B_detected_n": bd["detected_n"],
        "B_detection_rate": bd["detected_rate"],
        "B_warning_median_days_detected_only": bd["warning_median"],
        "B_warning_iqr_lo": bd["warning_iqr_lo"],
        "B_warning_iqr_hi": bd["warning_iqr_hi"],
    })

r = pd.DataFrame(records).set_index("comparison")

# Fixed-sequence confirmatory logic.
h1_reject = bool(r.loc["H1", "p_exact_two_sided"] < ALPHA)
h1_positive = bool(r.loc["H1", "theta"] > 0.5)
gate2 = h1_reject and h1_positive

m1_reject = False
m1_positive = bool(r.loc["M1", "theta"] > 0.5)
gate3 = False
if gate2:
    m1_reject = bool(r.loc["M1", "p_exact_two_sided"] < ALPHA)
    gate3 = m1_reject and m1_positive

# Holm-Bonferroni at stage 3 only if gate 3 opens.
holm = {"H2": {"reject": False, "adj_p": np.nan},
        "H3": {"reject": False, "adj_p": np.nan}}
if gate3:
    raw = [(h, float(r.loc[h, "p_exact_two_sided"])) for h in ("H2", "H3")]
    raw_sorted = sorted(raw, key=lambda z: z[1])

    # Holm adjusted p-values, m=2.
    p1 = min(1.0, 2 * raw_sorted[0][1])
    p2 = min(1.0, max(p1, raw_sorted[1][1]))
    holm[raw_sorted[0][0]]["adj_p"] = p1
    holm[raw_sorted[1][0]]["adj_p"] = p2

    # Sequential rejective Holm.
    first_h, first_p = raw_sorted[0]
    if first_p <= ALPHA / 2:
        holm[first_h]["reject"] = True
        second_h, second_p = raw_sorted[1]
        if second_p <= ALPHA:
            holm[second_h]["reject"] = True

r["confirmatory_tested"] = False
r["confirmatory_rejected"] = False
r["direction_favours_A"] = r["theta"] > 0.5
r["holm_adjusted_p"] = np.nan

r.loc["H1", "confirmatory_tested"] = True
r.loc["H1", "confirmatory_rejected"] = h1_reject
if gate2:
    r.loc["M1", "confirmatory_tested"] = True
    r.loc["M1", "confirmatory_rejected"] = m1_reject
if gate3:
    for h in ("H2", "H3"):
        r.loc[h, "confirmatory_tested"] = True
        r.loc[h, "confirmatory_rejected"] = holm[h]["reject"]
        r.loc[h, "holm_adjusted_p"] = holm[h]["adj_p"]

r = r.reset_index()
r.to_csv(OUT / "confirmatory_comparison_summary.csv", index=False)

gate = {
    "alpha": ALPHA,
    "H1_rejected_two_sided": h1_reject,
    "H1_theta_gt_0_5": h1_positive,
    "stage2_gate_open": gate2,
    "M1_tested_confirmatorily": gate2,
    "M1_rejected_two_sided_if_tested": m1_reject if gate2 else None,
    "M1_theta_gt_0_5": m1_positive,
    "stage3_gate_open": gate3,
    "H2_H3_Holm_applied": gate3,
    "bootstrap": {
        "type": "BCa over participants",
        "resamples": BOOT_N,
        "seed_base": BOOT_SEED,
        "note": "seed is computational only; gate decisions use exact binomial p-values",
    },
}
(OUT / "gatekeeping_decisions.json").write_text(json.dumps(gate, indent=2) + "\n")

print("=== PREREGISTERED CONFIRMATORY ANALYSIS ===")
print("Corrected run commit:", manifest["git_commit"])
print("Primary test: exact binomial sign test on W vs L, two-sided alpha=0.05")
print("Effect: theta=(W+0.5*T)/N; 95% BCa bootstrap, 10,000 participant resamples")
print()

for _, row in r.iterrows():
    label = row["comparison"]
    A, B = row["A"], row["B"]
    print(f"--- {label}: {A} vs {B} ---")
    print(
        f"N={int(row.N_pair)} | W/L/T={int(row.W)}/{int(row.L)}/{int(row.T)} "
        f"| discordant={int(row.discordant_W_plus_L)}"
    )
    wr = row.win_ratio_W_over_L
    wr_txt = "∞" if np.isinf(wr) else ("NA" if pd.isna(wr) else f"{wr:.3f}")
    print(
        f"theta={row.theta:.3f} "
        f"(95% BCa {row.theta_bca95_lo:.3f} to {row.theta_bca95_hi:.3f}) "
        f"| W/L ratio={wr_txt}"
    )
    print(f"exact two-sided p={fmt_p(row.p_exact_two_sided)}")
    if not pd.isna(row.holm_adjusted_p):
        print(f"Holm-adjusted p={fmt_p(row.holm_adjusted_p)}")

    print(
        f"{A}: detection {int(row.A_detected_n)}/{int(row.A_eval_n)} "
        f"({100*row.A_detection_rate:.1f}%)"
    )
    if not pd.isna(row.A_warning_median_days_detected_only):
        print(
            f"{A}: warning among detected median "
            f"{row.A_warning_median_days_detected_only:.1f} d "
            f"(IQR {row.A_warning_iqr_lo:.1f}–{row.A_warning_iqr_hi:.1f})"
        )
    else:
        print(f"{A}: warning among detected: NA")

    print(
        f"{B}: detection {int(row.B_detected_n)}/{int(row.B_eval_n)} "
        f"({100*row.B_detection_rate:.1f}%)"
    )
    if not pd.isna(row.B_warning_median_days_detected_only):
        print(
            f"{B}: warning among detected median "
            f"{row.B_warning_median_days_detected_only:.1f} d "
            f"(IQR {row.B_warning_iqr_lo:.1f}–{row.B_warning_iqr_hi:.1f})"
        )
    else:
        print(f"{B}: warning among detected: NA")

    tested = bool(row.confirmatory_tested)
    rejected = bool(row.confirmatory_rejected)
    favours = bool(row.direction_favours_A)

    if not tested:
        print("CONFIRMATORY STATUS: NOT TESTED — preceding fixed-sequence gate closed.")
        print("The numerical estimate/p-value above is descriptive/estimation-only.")
    elif label in ("H1", "M1"):
        if rejected and favours:
            print("CONFIRMATORY STATUS: REJECTED in the preregistered A-favouring direction.")
        elif rejected and not favours:
            print("CONFIRMATORY STATUS: statistically different, but in the opposite direction.")
        else:
            print("CONFIRMATORY STATUS: NOT REJECTED.")
    else:
        if rejected and favours:
            print("CONFIRMATORY STATUS: HOLM-REJECTED in the preregistered A-favouring direction.")
        elif rejected and not favours:
            print("CONFIRMATORY STATUS: HOLM-REJECTED, but in the opposite direction.")
        else:
            print("CONFIRMATORY STATUS: NOT REJECTED after Holm.")
    print()

print("=== FIXED-SEQUENCE GATEKEEPING ===")
print("H1 rejected:", h1_reject)
print("H1 theta > 0.5:", h1_positive)
print("Stage-2 gate open:", gate2)
print("M1 confirmatorily tested:", gate2)
if gate2:
    print("M1 rejected:", m1_reject)
    print("M1 theta > 0.5:", m1_positive)
print("Stage-3 gate open:", gate3)
print("H2/H3 Holm applied:", gate3)

print("\nSaved:")
print(OUT / "confirmatory_comparison_summary.csv")
print(OUT / "gatekeeping_decisions.json")
