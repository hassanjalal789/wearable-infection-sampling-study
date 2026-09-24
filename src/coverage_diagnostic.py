#!/usr/bin/env python3
"""
Night-vs-day source-coverage diagnostic.  PATCH 1 and PATCH 6.

Coverage uses UNIQUE OBSERVED MINUTE BINS against their own denominators
(420 night, 1020 day).  Reported for three populations, because the figure in
the paper must describe the population the primary study actually uses:

  A  all Fitbit participants
  B  pre-calibration eligible Fitbit participants
  C  final primary cohort (once C_min is chosen)

The bootstrap resamples PARTICIPANTS, never participant-days.
"""
from __future__ import annotations
import argparse, json
import numpy as np, pandas as pd

SEED = 20261010


def per_participant(inv: pd.DataFrame) -> pd.DataFrame:
    d = inv.copy()
    d["night_frac"] = d.night_observed_minutes / 420.0
    d["day_frac"] = d.day_observed_minutes / 1020.0
    return (d.groupby(["phase", "participant_id"])[["night_frac", "day_frac"]]
            .mean().reset_index())


def summarise(per: pd.DataFrame, label: str, rng) -> dict:
    if per.empty:
        return dict(population=label, n_participants=0, note="empty population")
    diff = (per.night_frac - per.day_frac).to_numpy()
    bs = rng.choice(diff, size=(10000, len(diff)), replace=True).mean(axis=1)
    return dict(population=label, n_participants=int(len(per)),
                mean_night_coverage=float(per.night_frac.mean()),
                mean_day_coverage=float(per.day_frac.mean()),
                mean_paired_difference=float(diff.mean()),
                ci95=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                bootstrap_unit="participant",
                interpretation="positive = night better covered than day")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", nargs="+", required=True)
    ap.add_argument("--device-map", required=True)
    ap.add_argument("--cohort", default=None, help="results/cohort.json, if built")
    a = ap.parse_args()

    inv = pd.concat([pd.read_parquet(p) for p in a.inventory], ignore_index=True)
    dm = pd.read_csv(a.device_map)
    fitbit = set(map(tuple, dm.loc[dm.device == "Fitbit", ["phase", "participant_id"]].values))
    per = per_participant(inv)
    per["key"] = list(zip(per.phase, per.participant_id))
    rng = np.random.default_rng(SEED)

    out = [summarise(per[per.key.isin(fitbit)], "A_provenance_resolved_fitbit", rng)]
    if a.cohort:
        c = json.load(open(a.cohort))
        pre = {tuple(x) for x in c["pre_calibration"]}
        fin = {tuple(x) for x in c["final"]}
        out.append(summarise(per[per.key.isin(pre)], "B_pre_calibration_eligible", rng))
        out.append(summarise(per[per.key.isin(fin)], "C_final_primary_cohort", rng))
    else:
        out.append(dict(population="B_pre_calibration_eligible", n_participants=0,
                        note="cohort.json not supplied"))
        out.append(dict(population="C_final_primary_cohort", n_participants=0,
                        note="cohort.json not supplied"))

    json.dump(out, open("results/coverage_diagnostic.json", "w"), indent=2)
    per.drop(columns="key").to_csv("results/coverage_per_participant.csv", index=False)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
