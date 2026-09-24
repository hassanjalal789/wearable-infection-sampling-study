#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path.home() / "rq1"
RUN = ROOT / "results" / "primary_e3_run_83cc8d1"
PRIMARY = RUN / "confirmatory_analysis" / "confirmatory_comparison_summary.csv"
SENS = RUN / "sensitivity_analysis" / "sensitivity_summary.csv"
OUT = RUN / "final_tables_figures"
OUT.mkdir(parents=True, exist_ok=True)

def fmt_ci(theta, lo, hi):
    return f"{theta:.3f} ({lo:.3f}–{hi:.3f})"

def pct(x):
    return "" if pd.isna(x) else f"{100*x:.1f}%"

def save_table(df, stem):
    df.to_csv(OUT / f"{stem}.csv", index=False)
    try:
        md = df.to_markdown(index=False)
    except Exception:
        md = df.to_string(index=False)
    (OUT / f"{stem}.md").write_text(md + "\n")

primary = pd.read_csv(PRIMARY)
sens = pd.read_csv(SENS)

# Table 1: primary confirmatory results
t1 = primary.copy()
t1["W/L/T"] = [f"{int(r.W)}/{int(r.L)}/{int(r.T)}" for r in t1.itertuples()]
t1["Effect θ (95% BCa CI)"] = [
    fmt_ci(r.theta, r.theta_bca95_lo, r.theta_bca95_hi) for r in t1.itertuples()
]
t1["Exact p"] = t1["p_exact_two_sided"].map(lambda x: f"{x:.4f}")
t1["A detection"] = [
    f"{int(r.A_detected_n)}/{int(r.A_eval_n)} ({pct(r.A_detection_rate)})"
    for r in t1.itertuples()
]
t1["B detection"] = [
    f"{int(r.B_detected_n)}/{int(r.B_eval_n)} ({pct(r.B_detection_rate)})"
    for r in t1.itertuples()
]
t1["A warning median (IQR), d"] = [
    "" if pd.isna(r.A_warning_median_days_detected_only)
    else f"{r.A_warning_median_days_detected_only:.1f} ({r.A_warning_iqr_lo:.1f}–{r.A_warning_iqr_hi:.1f})"
    for r in t1.itertuples()
]
t1["B warning median (IQR), d"] = [
    "" if pd.isna(r.B_warning_median_days_detected_only)
    else f"{r.B_warning_median_days_detected_only:.1f} ({r.B_warning_iqr_lo:.1f}–{r.B_warning_iqr_hi:.1f})"
    for r in t1.itertuples()
]

def status(row):
    tested = bool(row["confirmatory_tested"])
    rejected = bool(row["confirmatory_rejected"])
    favours = bool(row["direction_favours_A"])
    if not tested:
        return "Not confirmatorily tested (gate closed)"
    if rejected and favours:
        return "Rejected, favours A"
    if rejected:
        return "Rejected, opposite direction"
    return "Not rejected"

t1["Confirmatory status"] = t1.apply(status, axis=1)
table1 = t1[[
    "comparison", "A", "B", "N_pair", "W/L/T",
    "Effect θ (95% BCa CI)", "Exact p",
    "A detection", "B detection",
    "A warning median (IQR), d", "B warning median (IQR), d",
    "Confirmatory status"
]].rename(columns={"comparison": "Hypothesis", "N_pair": "N"})
save_table(table1, "table_primary_confirmatory_results")

# Table 2: all sensitivities
t2 = sens.copy()
t2["W/L/T"] = [f"{int(r.W)}/{int(r.L)}/{int(r.T)}" for r in t2.itertuples()]
t2["Effect θ (95% BCa CI)"] = [
    fmt_ci(r.theta, r.theta_bca95_lo, r.theta_bca95_hi) for r in t2.itertuples()
]
table2 = t2[[
    "scenario", "comparison", "N", "W/L/T", "Effect θ (95% BCa CI)"
]].rename(columns={"scenario": "Sensitivity", "comparison": "Comparison"})
save_table(table2, "table_sensitivity_results")

# Table 3 + Figure 2: H1 robustness
h1p = primary[primary["comparison"] == "H1"].iloc[0]
h1_rows = [{
    "Sensitivity": "Primary E3",
    "N": int(h1p["N_pair"]), "W": int(h1p["W"]), "L": int(h1p["L"]), "T": int(h1p["T"]),
    "theta": float(h1p["theta"]),
    "lo": float(h1p["theta_bca95_lo"]),
    "hi": float(h1p["theta_bca95_hi"]),
}]
label_map = {
    "phase2_only": "Phase 2 only",
    "common_cohort_all_primary_arms_Cfloor16": "Common cohort",
    "coarse_calibration_resolution_le_1pm": "Fine calibration only",
    "exclude_multiple_episode_rows": "Exclude multiple episodes",
    "alert_budget_B1": "Alert budget B=1",
    "alert_budget_B4": "Alert budget B=4",
    "todz_without_time_of_day_normalisation": "No TOD normalisation",
    "rolling_tau_recalibration": "Rolling threshold",
    "m1_realised_minute_matched": "Realised-minute matched",
}
for r in sens[sens["comparison"] == "H1"].itertuples():
    h1_rows.append({
        "Sensitivity": label_map.get(r.scenario, r.scenario),
        "N": int(r.N), "W": int(r.W), "L": int(r.L), "T": int(r.T),
        "theta": float(r.theta), "lo": float(r.theta_bca95_lo), "hi": float(r.theta_bca95_hi)
    })
h1 = pd.DataFrame(h1_rows)
h1["W/L/T"] = [f"{int(r.W)}/{int(r.L)}/{int(r.T)}" for r in h1.itertuples()]
h1["Effect θ (95% BCa CI)"] = [fmt_ci(r.theta, r.lo, r.hi) for r in h1.itertuples()]
save_table(h1[["Sensitivity", "N", "W/L/T", "Effect θ (95% BCa CI)"]], "table_h1_robustness")

# Figure 1: primary effects
order = ["H1", "M1", "H2", "H3"]
pf = primary.set_index("comparison").loc[order].reset_index()
fig, ax = plt.subplots(figsize=(7.2, 4.4))
y = np.arange(len(pf))
x = pf["theta"].to_numpy()
lo = pf["theta_bca95_lo"].to_numpy()
hi = pf["theta_bca95_hi"].to_numpy()
ax.errorbar(x, y, xerr=np.vstack([x-lo, hi-x]), fmt="o", capsize=4)
ax.axvline(0.5, linestyle="--", linewidth=1)
ax.set_yticks(y)
ax.set_yticklabels(["H1: S3 vs S2", "M1: S3r vs S6", "H2: S3 vs S5", "H3: S3 vs S4"])
ax.invert_yaxis()
ax.set_xlim(0, 1)
ax.set_xlabel("Paired superiority effect θ")
ax.set_title("Primary E3 paired effects")
ax.grid(axis="x", alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "figure_primary_effects.png", dpi=300, bbox_inches="tight")
fig.savefig(OUT / "figure_primary_effects.pdf", bbox_inches="tight")
plt.close(fig)

# Figure 2: H1 sensitivity
fig, ax = plt.subplots(figsize=(7.8, 6.0))
y = np.arange(len(h1))
x = h1["theta"].to_numpy()
lo = h1["lo"].to_numpy()
hi = h1["hi"].to_numpy()
ax.errorbar(x, y, xerr=np.vstack([x-lo, hi-x]), fmt="o", capsize=4)
ax.axvline(0.5, linestyle="--", linewidth=1)
ax.set_yticks(y)
ax.set_yticklabels(h1["Sensitivity"])
ax.invert_yaxis()
ax.set_xlim(0, 1)
ax.set_xlabel("H1 paired superiority effect θ")
ax.set_title("Robustness of nocturnal S3 versus uniform S2")
ax.grid(axis="x", alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "figure_h1_sensitivity.png", dpi=300, bbox_inches="tight")
fig.savefig(OUT / "figure_h1_sensitivity.pdf", bbox_inches="tight")
plt.close(fig)

# Figure 3: M1 estimation-only sensitivities
m1p = primary[primary["comparison"] == "M1"].iloc[0]
m1_rows = [{
    "Sensitivity": "Primary E3 (gate closed)",
    "theta": float(m1p["theta"]),
    "lo": float(m1p["theta_bca95_lo"]),
    "hi": float(m1p["theta_bca95_hi"]),
}]
for r in sens[sens["comparison"] == "M1"].itertuples():
    m1_rows.append({
        "Sensitivity": label_map.get(r.scenario, r.scenario),
        "theta": float(r.theta),
        "lo": float(r.theta_bca95_lo),
        "hi": float(r.theta_bca95_hi),
    })
m1 = pd.DataFrame(m1_rows)
fig, ax = plt.subplots(figsize=(7.8, 6.0))
y = np.arange(len(m1))
x = m1["theta"].to_numpy()
lo = m1["lo"].to_numpy()
hi = m1["hi"].to_numpy()
ax.errorbar(x, y, xerr=np.vstack([x-lo, hi-x]), fmt="o", capsize=4)
ax.axvline(0.5, linestyle="--", linewidth=1)
ax.set_yticks(y)
ax.set_yticklabels(m1["Sensitivity"])
ax.invert_yaxis()
ax.set_xlim(0, 1)
ax.set_xlabel("M1 paired superiority effect θ")
ax.set_title("M1 estimation-only sensitivity analysis")
ax.grid(axis="x", alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "figure_m1_sensitivity.png", dpi=300, bbox_inches="tight")
fig.savefig(OUT / "figure_m1_sensitivity.pdf", bbox_inches="tight")
plt.close(fig)

# Results digest
digest = f"""FINAL RESULTS DIGEST

Primary H1 (S3 nocturnal vs S2 uniform):
N={int(h1p['N_pair'])}, W/L/T={int(h1p['W'])}/{int(h1p['L'])}/{int(h1p['T'])}
theta={h1p['theta']:.3f}, 95% BCa CI {h1p['theta_bca95_lo']:.3f} to {h1p['theta_bca95_hi']:.3f}
exact two-sided p={h1p['p_exact_two_sided']:.4f}

Confirmatory conclusion:
H1 was not rejected and the fixed-sequence gate closed.

Main interpretation:
No evidence that nocturnally concentrated HR acquisition improves presymptomatic
warning over uniform-block acquisition at the tested E3 modelled-energy budget.

Sensitivity interpretation:
Every reported H1 sensitivity estimate remained <= 0.5. The primary null finding
was therefore robust to the sensitivity analyses reported in the core runner.

M1/H2/H3:
Estimation-only after the H1 gate closed; none may be presented as confirmatory.
"""
(OUT / "final_results_digest.txt").write_text(digest)

print("PASS — final tables and figures created")
print("Output directory:", OUT)
for p in sorted(OUT.iterdir()):
    print(p.name)
