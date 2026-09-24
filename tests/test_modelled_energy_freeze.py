from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import modelled_energy_match as mem

def test_primary_E3_feasible_in_every_frozen_scenario_and_arm():
    a = mem.audit()
    assert a["primary_E3_all_scenarios_feasible"] is True
    assert a["primary_E3_failures"] == []

def test_e1_e2_are_feasible_in_every_scenario_and_arm():
    a = mem.audit()
    for scenario, srec in a["scenarios"].items():
        for budget in ("E1", "E2"):
            for arm, rec in srec["budgets"][budget]["arms"].items():
                assert rec["status"] == "FEASIBLE_WITHIN_5PCT", (scenario, budget, arm, rec)

def test_e4_infeasibility_is_reported_not_hidden():
    a = mem.audit()
    statuses = [
        rec["status"]
        for srec in a["scenarios"].values()
        for rec in srec["budgets"]["E4"]["arms"].values()
    ]
    assert "DISCRETE_GRANULARITY_INFEASIBLE" in statuses
