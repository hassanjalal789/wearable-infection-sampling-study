#!/usr/bin/env python3
"""
Alert-rate resolution implied by the historical calibration period.
PREREGISTRATION ARTEFACT (post-review patch 3).

With C valid calibration days, the achieved alert rate A(tau) can only take the
values k * 30.44 / C for integer k.  A single alert therefore corresponds to
30.44/C alert-days per person-month, and the budget constraint A(tau) <= B is
satisfiable at k = 0 only whenever 30.44/C > B.  A short calibration interval
does not merely add noise -- it collapses the constraint onto "zero alerts in
the calibration window", which is a materially stricter and participant-varying
operating point than the one preregistered.

Part 1 (analytic) runs now.  Part 2 needs the eligible cohort and reports the
observed distribution of C_p; the final C_min is then chosen by the frozen
decision rule below, using AVAILABILITY ONLY, before any schedule outcome is seen.
"""
from __future__ import annotations
import json, sys
import numpy as np

DAYS_PER_MONTH = 30.44
BUDGETS = (1.0, 2.0, 4.0)
CANDIDATE_MINIMA = (28, 42, 61, 91)
RETENTION_FLOOR = 0.80          # frozen: keep >=80% of the eligible cohort


def resolution(C: int) -> float:
    """Alert-days per person-month contributed by ONE alert over C days."""
    return DAYS_PER_MONTH / C


def admissible_levels(C: int, B: float) -> int:
    """How many integer alert counts satisfy A <= B (k = 0, 1, 2, ...)."""
    return int(np.floor(B * C / DAYS_PER_MONTH)) + 1


def min_C_for_levels(B: float, levels: int) -> int:
    """Smallest C admitting at least `levels` distinct alert counts under budget B."""
    C = 1
    while admissible_levels(C, B) < levels:
        C += 1
    return C


def analytic_table():
    rows = []
    for C in (14, 21, 28, 35, 42, 56, 61, 70, 91, 120, 180):
        r = dict(C=C, resolution_per_month=round(resolution(C), 3))
        for B in BUDGETS:
            r[f"levels_B{int(B)}"] = admissible_levels(C, B)
        r["one_alert_as_pct_of_B2"] = round(100 * resolution(C) / 2.0, 1)
        rows.append(r)
    return rows


def choose_c_min(calibration_days: list[int]) -> dict:
    """FROZEN DECISION RULE, availability-only.

    C_min := max{ c in CANDIDATE_MINIMA : share of eligible participants with
                  C_p >= c is at least RETENTION_FLOOR }, defaulting to 28.
    Uses only the distribution of available calibration days.  It cannot see any
    schedule outcome, any alert, or any comparison.
    """
    a = np.asarray(calibration_days, dtype=float)
    shares = {c: float((a >= c).mean()) for c in CANDIDATE_MINIMA}
    ok = [c for c in CANDIDATE_MINIMA if shares[c] >= RETENTION_FLOOR]
    fallback_invoked = not ok
    chosen = max(ok) if ok else 28
    retention_at_choice = shares.get(chosen, float((a >= chosen).mean()))
    retention_floor_met = retention_at_choice >= RETENTION_FLOOR
    return dict(
        n_participants=int(a.size), chosen_C_min=chosen,
        retention_at_choice=retention_at_choice,
        shares=shares, floor=RETENTION_FLOOR,
        fallback_invoked=bool(fallback_invoked),
        fallback_value=28,
        retention_floor_met=bool(retention_floor_met),
        median=float(np.median(a)),
        iqr=[float(np.percentile(a, 25)), float(np.percentile(a, 75))],
        minimum=float(a.min()), maximum=float(a.max()),
        implied_one_alert_resolution_at_median=round(resolution(int(np.median(a))), 3),
        note=(
            "availability-only rule; frozen before any outcome inspection; "
            + (
                "no candidate minimum met the 0.80 retention floor, so the "
                "prespecified fallback C_min=28 was invoked"
                if fallback_invoked
                else
                "retention floor met; highest admissible candidate selected"
            )
        ))


def main():
    print("PART 1 — ANALYTIC RESOLUTION (runs without data)\n")
    hdr = f"{'C days':>7} {'1 alert = /month':>17} {'levels B=1':>11} {'levels B=2':>11} {'levels B=4':>11} {'1 alert as % of B=2':>21}"
    print(hdr); print("-" * len(hdr))
    for r in analytic_table():
        print(f"{r['C']:>7} {r['resolution_per_month']:>17.3f} {r['levels_B1']:>11} "
              f"{r['levels_B2']:>11} {r['levels_B4']:>11} {r['one_alert_as_pct_of_B2']:>20.1f}%")
    print("\nMinimum C for at least 2 admissible alert counts (i.e. 1 alert is allowed):")
    for B in BUDGETS:
        print(f"   B = {B:.0f} alert-days/person-month  ->  C >= {min_C_for_levels(B, 2):>3} days")
    print("Minimum C for at least 3 admissible alert counts:")
    for B in BUDGETS:
        print(f"   B = {B:.0f}  ->  C >= {min_C_for_levels(B, 3):>3} days")

    print("\nPART 2 — OBSERVED DISTRIBUTION OF C_p")
    if len(sys.argv) > 1:
        days = json.load(open(sys.argv[1]))
        out = choose_c_min(days)
        print(json.dumps(out, indent=2))
        json.dump(out, open("results/calibration_rule.json", "w"), indent=2)
    else:
        print("   BLOCKED — requires the eligible cohort.")
        print("   Run:  python3 src/calibration_resolution.py results/calibration_days.json")


if __name__ == "__main__":
    main()
