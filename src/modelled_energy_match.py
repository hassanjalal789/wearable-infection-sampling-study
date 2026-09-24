from __future__ import annotations

import json
from pathlib import Path
from energy_model import RailEnergyParams, e_sched_joules

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "modelled_energy_scenarios.json"

CAPACITY = {
    "S2": 144,
    "S3": 42,
    "S5": 144,
    "S4": 33,
    "S3r": 42,
    "S6": 102,
}
ARMS = ["S2", "S3", "S5", "S4", "S3r", "S6"]

def load():
    return json.loads(CONFIG.read_text())

def params(d):
    return RailEnergyParams(**d)

def s1_reference_energy(p):
    return e_sched_joules("S1", 1, 1440, p)

def nearest_integer_bursts(arm, target_J, L_min, p, n_max=None):
    if n_max is None:
        n_max = CAPACITY[arm]
    rows = []
    for n in range(n_max + 1):
        e = e_sched_joules(arm, n, L_min, p)
        err = abs(e / target_J - 1.0) if target_J > 0 else 0.0
        rows.append((err, e, n))
    err, e, n = min(rows, key=lambda x: (x[0], x[1], x[2]))
    return {
        "N": int(n),
        "achieved_J": float(e),
        "target_J": float(target_J),
        "relative_error": float(e / target_J - 1.0),
        "abs_relative_error": float(err),
    }

def audit():
    cfg = load()
    tol = float(cfg["tolerance_fraction"])
    L = int(cfg["burst_minutes"])
    out = {
        "status": "PRE_OUTCOME_ENERGY_MATCH_AUDIT",
        "tolerance_fraction": tol,
        "burst_minutes": L,
        "scenarios": {},
    }
    for scenario, pdict in cfg["scenarios"].items():
        p = params(pdict)
        ref = s1_reference_energy(p)
        srec = {"S1_reference_J": ref, "budgets": {}}
        for budget, frac in cfg["budget_fractions"].items():
            target = frac * ref
            brec = {"fraction_of_S1": frac, "target_J": target, "arms": {}}
            for arm in ARMS:
                rec = nearest_integer_bursts(arm, target, L, p)
                rec["status"] = (
                    "FEASIBLE_WITHIN_5PCT"
                    if rec["abs_relative_error"] <= tol + 1e-12
                    else "DISCRETE_GRANULARITY_INFEASIBLE"
                )
                brec["arms"][arm] = rec
            srec["budgets"][budget] = brec
        out["scenarios"][scenario] = srec

    bad_e3 = []
    for scenario, srec in out["scenarios"].items():
        for arm, rec in srec["budgets"]["E3"]["arms"].items():
            if rec["status"] != "FEASIBLE_WITHIN_5PCT":
                bad_e3.append([scenario, arm, rec])
    out["primary_E3_all_scenarios_feasible"] = not bad_e3
    out["primary_E3_failures"] = bad_e3
    return out

def main():
    out = audit()
    path = ROOT / "results" / "modelled_energy_match_audit.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    for scenario, srec in out["scenarios"].items():
        print(f"\n=== {scenario} ===")
        print(f"S1 reference: {srec['S1_reference_J']:.6f} J")
        for budget, b in srec["budgets"].items():
            print(f"{budget} target={b['target_J']:.6f} J")
            for arm, r in b["arms"].items():
                print(
                    f"  {arm:3s} N={r['N']:2d} achieved={r['achieved_J']:.6f} J "
                    f"err={100*r['relative_error']:+.3f}% {r['status']}"
                )
    print("\nPRIMARY E3 ALL SCENARIOS FEASIBLE:", out["primary_E3_all_scenarios_feasible"])
    print("Wrote:", path)
    if not out["primary_E3_all_scenarios_feasible"]:
        raise SystemExit("STOP: primary E3 energy matching is not feasible in all scenarios.")

if __name__ == "__main__":
    main()
