#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path.home() / "rq1"
RUN = ROOT / "results" / "primary_e3_run_83cc8d1"

def fail(msg):
    raise SystemExit("FAIL: " + msg)

required = [
    "arm_outcomes.csv",
    "schedule_qc_daily.csv",
    "m1_daily_feasibility.csv",
    "participant_input_and_m1_summary.csv",
    "pair_hierarchy.csv",
    "run_manifest.json",
]
for name in required:
    if not (RUN / name).exists():
        fail(f"missing {name}")

o = pd.read_csv(RUN / "arm_outcomes.csv")
q = pd.read_csv(RUN / "schedule_qc_daily.csv")
m = pd.read_csv(RUN / "m1_daily_feasibility.csv")
pm = pd.read_csv(RUN / "participant_input_and_m1_summary.csv")
ph = pd.read_csv(RUN / "pair_hierarchy.csv")
man = json.loads((RUN / "run_manifest.json").read_text())

arms = ["S1", "S2", "S3", "S5", "S4", "S3r", "S6"]

print("=== MANIFEST ===")
for k in [
    "git_commit", "energy_freeze_commit", "scenario", "budget",
    "N_budget", "burst_minutes", "n_frozen_cohort"
]:
    print(f"{k}: {man.get(k)}")
print("phase2_step_semantics:", man.get("phase2_step_semantics"))

if not str(man.get("git_commit", "")).startswith("83cc8d1"):
    fail("manifest commit is not 83cc8d1")
if man.get("energy_freeze_commit") != "4023717":
    fail("wrong energy freeze commit")
if man.get("scenario") != "CENTRAL" or man.get("budget") != "E3":
    fail("wrong scenario/budget")
if int(man.get("N_budget")) != 7 or int(man.get("burst_minutes")) != 10:
    fail("wrong E3 allocation")
if int(man.get("n_frozen_cohort")) != 38:
    fail("wrong frozen cohort count")
if not man.get("phase2_step_semantics"):
    fail("A6 step-semantics field missing from manifest")

print("\n=== TABLE STRUCTURE ===")
print("arm_outcomes rows:", len(o), "expected 266")
print("unique participants:", o[["phase","participant_id"]].drop_duplicates().shape[0])
print("rows per arm:")
print(o.groupby("arm").size().reindex(arms).to_string())

if len(o) != 266:
    fail("arm_outcomes row count != 266")
if o[["phase","participant_id","arm"]].duplicated().any():
    fail("duplicate participant-arm row")
if set(o["arm"]) != set(arms):
    fail("arm set mismatch")

print("\n=== A6 INPUT-SEMANTICS QC ===")
p2 = pm[pm["phase"] == "phase2"]
p1 = pm[pm["phase"] == "phase1"]

print("phase2 participants:", len(p2))
print("phase1 participants:", len(p1))
print("phase2 semantics applied:",
      int(pd.to_numeric(p2["phase2_sparse_step_semantics_applied"], errors="coerce").fillna(0).astype(bool).sum()),
      "/", len(p2))
print("phase1 semantics applied:",
      int(pd.to_numeric(p1["phase2_sparse_step_semantics_applied"], errors="coerce").fillna(0).astype(bool).sum()),
      "/", len(p1))
print("phase2 inferred-zero minutes median:",
      float(pd.to_numeric(p2["n_phase2_zero_step_minutes_inferred"], errors="coerce").median()))
print("phase1 inferred-zero minutes total:",
      int(pd.to_numeric(p1["n_phase2_zero_step_minutes_inferred"], errors="coerce").fillna(0).sum()))

if len(p2) != 28 or len(p1) != 10:
    fail("unexpected phase split")
if not pd.to_numeric(p2["phase2_sparse_step_semantics_applied"], errors="coerce").fillna(0).astype(bool).all():
    fail("A6 semantics not applied to every Phase 2 participant")
if pd.to_numeric(p1["phase2_sparse_step_semantics_applied"], errors="coerce").fillna(0).astype(bool).any():
    fail("A6 semantics incorrectly applied to Phase 1")
if (pd.to_numeric(p2["n_phase2_zero_step_minutes_inferred"], errors="coerce") <= 0).any():
    fail("one or more Phase 2 participants have no inferred zero-step minutes")
if pd.to_numeric(p1["n_phase2_zero_step_minutes_inferred"], errors="coerce").fillna(0).sum() != 0:
    fail("Phase 1 has inferred zero-step minutes")

print("\n=== CALIBRATION QC — NO DETECTION RESULTS ===")
cal = o.groupby("arm").agg(
    n=("participant_id","size"),
    floor_met=("calibration_floor_met","sum"),
    cal_days_min=("calibration_z_days","min"),
    cal_days_median=("calibration_z_days","median"),
    cal_days_max=("calibration_z_days","max"),
    saturated=("calibration_saturated","sum"),
)
print(cal.reindex(arms).to_string())

viol = o[
    o["calibration_floor_met"].astype(bool)
    & o["achieved_calibration_alert_rate"].notna()
    & (o["achieved_calibration_alert_rate"] > 2.0 + 1e-12)
]
print("alert-budget violations:", len(viol))
if len(viol):
    fail("calibration alert budget violated")

print("\n=== PRESYMPTOMATIC EVALUABILITY QC — NO DETECTION RESULTS ===")
ev = o.groupby("arm").agg(
    participants=("participant_id","size"),
    zero_evaluable_days=("presymptomatic_evaluable_days", lambda s: int((s == 0).sum())),
    eval_days_min=("presymptomatic_evaluable_days","min"),
    eval_days_median=("presymptomatic_evaluable_days","median"),
    eval_days_max=("presymptomatic_evaluable_days","max"),
)
print(ev.reindex(arms).to_string())

print("\n=== SCHEDULE DELIVERY QC ===")
non_s1 = q[q["arm"] != "S1"]
print("rows with n_scheduled > n_requested:",
      int((non_s1["n_scheduled"] > non_s1["n_requested"]).sum()))
print("rows with delivered_minutes > scheduled_minutes:",
      int((q["delivered_minutes"] > q["scheduled_minutes"]).sum()))

if (non_s1["n_scheduled"] > non_s1["n_requested"]).any():
    fail("scheduled bursts exceed requested")
if (q["delivered_minutes"] > q["scheduled_minutes"]).any():
    fail("delivered minutes exceed scheduled minutes")

event = o.groupby("arm").agg(
    event_sched_min_median=("event_scheduled_minutes","median"),
    event_deliv_min_median=("event_delivered_minutes","median"),
    event_deliv_min_min=("event_delivered_minutes","min"),
    event_days_with_delivery_median=("event_days_with_delivery","median"),
)
print(event.reindex(arms).to_string())

print("\n=== M1 FEASIBILITY QC ===")
frac = pd.to_numeric(pm["m1_unavailable_event_fraction"], errors="coerce")
print("participants with >40% unavailable M1 event-days:", int((frac > 0.40).sum()))
print("M1 unavailable fraction median:", float(frac.median()))
print("M1 unavailable fraction max:", float(frac.max()))

print("\n=== PAIR FILE STRUCTURE ONLY ===")
print("rows:", len(ph), "expected 152")
print("comparisons:", sorted(ph["comparison"].unique().tolist()))
print("rows per comparison:")
print(ph.groupby("comparison").size().to_string())

if len(ph) != 152:
    fail("pair_hierarchy row count != 152")
if ph[["phase","participant_id","comparison"]].duplicated().any():
    fail("duplicate pair rows")
if set(ph["comparison"]) != {"H1","M1","H2","H3"}:
    fail("comparison set mismatch")

print("\n=== CORRECTED-RUN QC RESULT ===")
print("PASS — corrected-run structural/input/QC audit completed.")
print("No H1/M1/H2/H3 win-loss counts, detection rates, warning times, p-values, or effect sizes were printed.")
