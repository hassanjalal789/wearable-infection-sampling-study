#!/usr/bin/env python3
"""
Two-phase cohort construction.  PATCH 4 and PATCH 5.

PHASE A  pre-calibration eligible set -- device, infection status, symptomatic,
         onset available, baseline and source-coverage requirements.  NO C_min
         filter is applied here.
         Then C_p is computed from SOURCE AVAILABILITY ONLY and C_min is chosen
         by the frozen v1.2 rule.
PHASE B  final primary cohort -- Phase A plus C_p >= C_min.

The stale `c >= 14` rule from v1.1 is removed.  Device comes from
results/device_map.csv, never from a filename guess.  No outcome, alert or
schedule-performance quantity can reach this file: it imports nothing from
schedules.py or tod_z.py, by design.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

import calibration_resolution as cr

NIGHT_MIN, DAY_MIN = 120, 120                 # >= 2 h in each window (prereg 3.1)
BASELINE_WINDOW, BASELINE_DAYS_REQUIRED = 28, 21
EXCL_BEFORE, EXCL_AFTER = 21, 21              # [onset - 21, onset + 21]


def episode_anchors(rows: pd.DataFrame) -> list:
    """One anchor date per infection episode: onset where present, else diagnosis.

    An asymptomatic episode has no onset date but still contaminates the negative
    period, so it must contribute an exclusion window anchored on its diagnosis date.
    """
    out = []
    for _, r in rows.iterrows():
        a = r.get("onset_date")
        if pd.isna(a):
            a = r.get("diagnosis_date")
        if not pd.isna(a):
            out.append(pd.to_datetime(a))
    return sorted(set(out))


def exclusion_mask(dates: pd.Series, anchors: list) -> pd.Series:
    """PATCH 4: union of [anchor_i - 21, anchor_i + 21] over ALL episodes.

    Every episode contributes, not only the index one, and an episode that
    precedes the index event is removed from calibration availability even though
    a later episode is the index. Anchors come from episode_anchors(), so
    asymptomatic episodes (diagnosis date only) are included.
    """
    m = pd.Series(False, index=dates.index)
    for on in anchors:
        on = pd.to_datetime(on)
        m |= ((dates >= on - pd.Timedelta(days=EXCL_BEFORE))
              & (dates <= on + pd.Timedelta(days=EXCL_AFTER)))
    return m


def mark_analysable(inv: pd.DataFrame) -> pd.DataFrame:
    d = inv.copy()
    d["date"] = pd.to_datetime(d["date"])
    d["analysable"] = ((d.night_observed_minutes >= NIGHT_MIN)
                       & (d.day_observed_minutes >= DAY_MIN))
    return d


def phase_a(inv: pd.DataFrame, onsets: pd.DataFrame, device_map: pd.DataFrame,
            required_device: str = "Fitbit"):
    d = mark_analysable(inv)
    dm = device_map.set_index(["participant_id", "phase"])
    flow, eligible, cal_days = {}, [], {}

    for phase in sorted(inv.phase.unique()):
        p = d[d.phase == phase]
        o = onsets[onsets.phase == phase]
        step = {}

        pos = set(o.participant_id)
        dev_ok = {pid for pid in pos
                  if (pid, phase) in dm.index
                  and dm.loc[(pid, phase), "device"] == required_device}
        step["infection_positive"] = len(pos)
        step[f"device_{required_device}_with_provenance"] = len(dev_ok)
        step["device_unknown_or_conflict"] = len(
            {pid for pid in pos if (pid, phase) in dm.index
             and dm.loc[(pid, phase), "device"] in ("UNKNOWN", "CONFLICT")})

        symp = dev_ok & set(o.loc[o.symptomatic == True, "participant_id"])
        step["of_which_symptomatic"] = len(symp)
        withonset = symp & set(o.loc[o.onset_date.notna(), "participant_id"])
        step["with_onset_date"] = len(withonset)

        base = set()
        for pid in withonset:
            on = sorted(pd.to_datetime(
                o.loc[o.participant_id == pid, "onset_date"].dropna()))[0]
            w = p[(p.participant_id == pid) & (p.date < on)
                  & (p.date >= on - pd.Timedelta(days=BASELINE_WINDOW))]
            if int(w.analysable.sum()) >= BASELINE_DAYS_REQUIRED:
                base.add(pid)
        step["sufficient_baseline"] = len(base)
        step["pre_calibration_eligible"] = len(base)
        flow[phase] = step

        for pid in base:
            rows = o[o.participant_id == pid]
            index_onset = sorted(pd.to_datetime(rows.onset_date.dropna()))[0]  # 6.9
            anchors = episode_anchors(rows)                # 6.9 + 6.10
            pp = p[p.participant_id == pid]
            hist = pp[(pp.date < index_onset - pd.Timedelta(days=BASELINE_WINDOW))
                      & (~exclusion_mask(pp.date, anchors))]
            cal_days[(phase, pid)] = int(hist.analysable.sum())
            eligible.append((phase, pid))
    return flow, eligible, cal_days


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", nargs="+", required=True)
    ap.add_argument("--onsets", required=True)
    ap.add_argument("--device-map", required=True)
    ap.add_argument("--budget", type=float, default=2.0)
    a = ap.parse_args()

    inv = pd.concat([pd.read_parquet(p) for p in a.inventory], ignore_index=True)
    onsets = pd.read_csv(a.onsets, parse_dates=["onset_date"])
    dm = pd.read_csv(a.device_map)

    flow, eligible, cal = phase_a(inv, onsets, dm)
    pre_n = len(eligible)
    if pre_n == 0:
        raise SystemExit("FATAL: pre-calibration eligible set is empty. "
                         "Check device_map.csv provenance and onset labels before "
                         "interpreting this as a data property.")

    # ---- availability-only C_min selection (frozen v1.2 rule) ----------------
    rule = cr.choose_c_min(list(cal.values()))
    Path("results").mkdir(exist_ok=True)
    json.dump(rule, open("results/calibration_rule.json", "w"), indent=2)
    json.dump({f"{ph}:{pid}": c for (ph, pid), c in cal.items()},
              open("results/calibration_days.json", "w"), indent=2)

    c_min = rule["chosen_C_min"]
    final = [(ph, pid) for (ph, pid) in eligible if cal[(ph, pid)] >= c_min]

    report = {
        "per_phase": flow,
        "pre_calibration_eligible_total": pre_n,
        "calibration_days_distribution": {
            k: rule[k] for k in ("median", "iqr", "minimum", "maximum",
                                 "shares", "floor")},
        "chosen_C_min": c_min,
        "C_min_selection_rule": rule["note"],
        "excluded_for_C_p_below_C_min": pre_n - len(final),
        "FINAL_ELIGIBLE_N": len(final),
        "budget_used_for_resolution_reporting": a.budget,
        "one_alert_resolution_at_chosen_C_min": round(cr.resolution(c_min), 3),
    }
    json.dump(report, open("results/participant_flow.json", "w"), indent=2)
    json.dump({"pre_calibration": [list(x) for x in eligible],
               "final": [list(x) for x in final],
               "calibration_days": {f"{ph}:{pid}": c for (ph, pid), c in cal.items()}},
              open("results/cohort.json", "w"), indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
