#!/usr/bin/env python3
"""
Device-coverage gate, scoped to the participants that actually matter.
PATCH (final) — audit item 1.

The previous gate aborted if ANY participant in device_map.csv was UNKNOWN or
CONFLICT.  Phase 1 filenames carry no device token, so that condition fires on
thousands of archive participants who are irrelevant to the infection-positive
cohort, and it would have blocked the pipeline for no scientific reason.

The fatal condition is now scoped to CANDIDATE PARTICIPANTS REQUIRED FOR COHORT
CONSTRUCTION: those appearing in onset_labels.csv as infection-positive.  A
negative or unrelated archive participant may remain UNKNOWN.  Devices are still
never guessed.

Exit 0  every candidate resolved
Exit 2  at least one candidate unresolved  (pipeline aborts)
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import pandas as pd

UNRESOLVED = ("UNKNOWN", "CONFLICT")


def candidates_from_onsets(onsets: pd.DataFrame) -> set:
    """Candidate = any participant listed as an infection case in onset_labels.csv.

    Scoped deliberately wider than 'finally eligible': a participant excluded
    later for missing onset or insufficient baseline should still have had a
    defensible device assignment attempted, so the flow table can say WHY they
    dropped rather than conflating it with an unresolved device.
    """
    return set(zip(onsets["phase"], onsets["participant_id"]))


def report(device_map: pd.DataFrame, onsets: pd.DataFrame) -> dict:
    dm = device_map.copy()
    key = list(zip(dm["phase"], dm["participant_id"]))
    dm["key"] = key
    cand = candidates_from_onsets(onsets)

    in_map = dm[dm.key.isin(cand)]
    missing_from_map = sorted(f"{p}:{i}" for (p, i) in cand - set(key))
    unresolved = in_map[in_map.device.isin(UNRESOLVED)]

    return dict(
        total_participants_in_map=int(len(dm)),
        total_unknown_or_conflict_all_participants=int(dm.device.isin(UNRESOLVED).sum()),
        note_on_total=("Reported for transparency only. Unresolved devices among "
                       "participants who are NOT infection candidates do not block "
                       "the pipeline."),
        n_candidates=len(cand),
        candidates_resolved=int(len(in_map) - len(unresolved)),
        candidates_unresolved=int(len(unresolved)),
        candidates_absent_from_device_map=missing_from_map[:100],
        n_candidates_absent_from_device_map=len(missing_from_map),
        unresolved_candidate_ids=sorted(
            f"{r.phase}:{r.participant_id}({r.device})" for _, r in unresolved.iterrows()
        )[:100],
        by_phase_device=(dm.groupby(["phase", "device"]).size().rename("n")
                         .reset_index().to_dict("records")),
        blocking=bool(len(unresolved) or missing_from_map),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device-map", required=True)
    ap.add_argument("--onsets", required=True)
    ap.add_argument("--out", default="results/device_coverage_check.json")
    a = ap.parse_args()

    dm = pd.read_csv(a.device_map)
    on = pd.read_csv(a.onsets)
    r = report(dm, on)
    Path("results").mkdir(exist_ok=True)
    json.dump(r, open(a.out, "w"), indent=2)
    print(json.dumps({k: v for k, v in r.items()
                      if k != "by_phase_device"}, indent=2))
    if r["blocking"]:
        print("\nFATAL: candidate infection-positive participants have no defensible "
              "device assignment. Supply results/device_map_external.csv with "
              "supplementary-table or author-correspondence rows for the IDs listed "
              "above. Devices are never guessed.", file=sys.stderr)
        sys.exit(2)
    print("\nAll candidate infection-positive participants have a device with provenance.")


if __name__ == "__main__":
    main()
