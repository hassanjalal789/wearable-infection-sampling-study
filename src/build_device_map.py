#!/usr/bin/env python3
"""
Build results/device_map.csv -- one authoritative device assignment per
participant, WITH PROVENANCE.  PATCH 3.

Rule: a device is never inferred because a downstream filter needs one.  Phase 1
filenames such as AHYIJDV_hr.csv carry no device token, and blanket-mapping them
to Fitbit would silently manufacture the very cohort the study depends on.

Provenance vocabulary, in descending strength:
  filename_token        the filename names the device (Phase 2 style)
  archive_metadata      a file inside the archive states it
  supplementary_table   a published supplementary table lists this participant
  paper_statement_scope a published statement covers a DEFINED SET this
                        participant is independently known to belong to
  author_correspondence a reply from the Snyder lab
  UNKNOWN               none of the above -- participant is excluded, not guessed

Mishra et al. state that the 32 analysed COVID-positive cases "had Fitbit data".
That is a statement about a set, not a per-participant label, so it may only be
used once membership of that set has been established from a source of its own,
and it is then recorded as paper_statement_scope with the membership source named.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

STRENGTH = ["filename_token", "archive_metadata", "supplementary_table",
            "paper_statement_scope", "author_correspondence", "UNKNOWN"]


def from_inventory(inv: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (phase, pid), g in inv.groupby(["phase", "participant_id"]):
        devs = sorted(set(g.device) - {"UNKNOWN"})
        if len(devs) == 1:
            rows.append(dict(participant_id=pid, phase=phase, device=devs[0],
                             provenance="filename_token",
                             detail=f"filename token in {g.source_file.iloc[0]}"))
        elif len(devs) > 1:
            rows.append(dict(participant_id=pid, phase=phase, device="CONFLICT",
                             provenance="UNKNOWN",
                             detail=f"multiple device tokens: {devs}"))
        else:
            rows.append(dict(participant_id=pid, phase=phase, device="UNKNOWN",
                             provenance="UNKNOWN",
                             detail="no device token in filename; resolve from "
                                    "archive metadata or supplementary tables"))
    return pd.DataFrame(rows)


def merge_external(base: pd.DataFrame, external_csv: str | None) -> pd.DataFrame:
    """Merge a curated file of externally sourced assignments.

    The external file must carry participant_id, phase, device, provenance, detail.
    A stronger provenance overrides a weaker one; equal strength with a different
    device raises rather than picking a winner.
    """
    if not external_csv:
        return base
    ext = pd.read_csv(external_csv)
    need = {"participant_id", "phase", "device", "provenance", "detail"}
    missing = need - set(ext.columns)
    if missing:
        raise RuntimeError(f"{external_csv} is missing columns: {sorted(missing)}")
    bad = set(ext.provenance) - set(STRENGTH)
    if bad:
        raise RuntimeError(f"unrecognised provenance values: {sorted(bad)}")
    out = base.set_index(["participant_id", "phase"])
    for _, r in ext.iterrows():
        k = (r.participant_id, r.phase)
        if k not in out.index:
            out.loc[k] = dict(device=r.device, provenance=r.provenance, detail=r.detail)
            continue
        cur = out.loc[k]
        si, sj = STRENGTH.index(cur.provenance), STRENGTH.index(r.provenance)
        if sj < si:
            out.loc[k] = dict(device=r.device, provenance=r.provenance, detail=r.detail)
        elif sj == si and cur.device != r.device:
            raise RuntimeError(
                f"conflicting device for {k} at equal provenance strength "
                f"'{r.provenance}': {cur.device} vs {r.device}. Resolve manually.")
    return out.reset_index()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", nargs="+", required=True)
    ap.add_argument("--external", default=None,
                    help="curated CSV of supplementary/correspondence assignments")
    ap.add_argument("--out", default="results/device_map.csv")
    a = ap.parse_args()
    inv = pd.concat([pd.read_parquet(p) for p in a.inventory], ignore_index=True)
    dm = merge_external(from_inventory(inv), a.external)
    dm = dm[["participant_id", "phase", "device", "provenance", "detail"]]
    Path("results").mkdir(exist_ok=True)
    dm.to_csv(a.out, index=False)
    summary = (dm.groupby(["phase", "device", "provenance"]).size()
               .rename("n").reset_index().to_dict("records"))
    json.dump(summary, open("results/device_map_summary.json", "w"), indent=2)
    print(dm.groupby(["phase", "device"]).size().to_string())
    n_unknown = int((dm.device.isin(["UNKNOWN", "CONFLICT"])).sum())
    if n_unknown:
        print(f"\n{n_unknown} participants have no defensible device assignment. "
              f"They are EXCLUDED from the cohort, not guessed. Resolve them by "
              f"supplying --external with supplementary-table or correspondence rows.")


if __name__ == "__main__":
    main()
