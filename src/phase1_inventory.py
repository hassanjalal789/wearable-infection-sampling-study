#!/usr/bin/env python3
"""
Phase 1 archive inventory.  SCHEMA-DISCOVERING AND FAIL-LOUD BY DESIGN.

PATCH 1 (critical): night and day coverage are counted as UNIQUE OBSERVED
MINUTE BINS, never as raw timestamp counts.  Phase 1 Fitbit heart rate arrives
every ~5-15 s, so a raw-sample count overstates night coverage by an order of
magnitude against a 420-minute denominator.  Day coverage is computed directly
from its own minute bins, never by subtracting a sample count from a minute count.

PATCH 2: timestamp parsing tests the (Start_Date, Start_Time) PAIR first, before
any generic single-column candidate, so an Apple Watch file cannot be parsed to
midnight by selecting Start_Date alone.

PATCH 3: device is NOT inferred from the filename when the filename carries no
device token.  Such rows are emitted as device="UNKNOWN" and must be resolved by
src/build_device_map.py with recorded provenance.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path
import numpy as np
import pandas as pd

NIGHT_HOURS = set(range(0, 7))        # 00:00-06:59  -> 420 minutes
DAY_HOURS = set(range(7, 24))         # 07:00-23:59  -> 1020 minutes
NIGHT_MINUTES, DAY_MINUTES = 420, 1020

FNAME_PAT = re.compile(
    r"^(?P<pid>[A-Za-z0-9]+)[-_](?:(?P<dev>Fitbit|AppleWatch|Apple_Watch|Garmin)[-_])?"
    r"(?P<kind>hr|rhr|st|steps|step|sleep)\.csv$", re.I)
DEVICE_CANON = {"fitbit": "Fitbit", "applewatch": "AppleWatch",
                "apple_watch": "AppleWatch", "garmin": "Garmin"}


def sha256(p: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def classify(name: str):
    m = FNAME_PAT.match(name)
    if not m:
        return None
    d = m.groupdict()
    dev = d["dev"]
    return {"pid": d["pid"], "kind": d["kind"].lower(),
            "device": DEVICE_CANON.get(dev.lower(), dev) if dev else "UNKNOWN"}


def parse_timestamps(df: pd.DataFrame) -> pd.Series:
    """PATCH 2: the (Start_Date, Start_Time) pair wins over any single column.

    Column matching is case-insensitive.  A file carrying Start_Date without
    Start_Time raises rather than silently parsing every row to midnight.
    """
    lower = {c.lower(): c for c in df.columns}
    if "start_date" in lower and "start_time" in lower:
        return pd.to_datetime(df[lower["start_date"]].astype(str).str.strip() + " "
                              + df[lower["start_time"]].astype(str).str.strip(),
                              errors="coerce")
    if "start_date" in lower and "start_time" not in lower:
        raise RuntimeError(
            "Start_Date present without Start_Time. Parsing it alone would set every "
            "timestamp to midnight and destroy the night/day split. Columns: "
            f"{list(df.columns)}")
    for cand in ("datetime", "timestamp", "time", "date"):
        if cand in lower:
            return pd.to_datetime(df[lower[cand]], errors="coerce")
    raise RuntimeError(f"no timestamp column found; columns were {list(df.columns)}")


def per_day_coverage(ts: pd.Series) -> pd.DataFrame:
    """PATCH 1: unique observed minute bins, split by the local hour of the bin."""
    ts = pd.Series(pd.to_datetime(ts)).dropna()
    if ts.empty:
        return pd.DataFrame(columns=["date", "night_observed_minutes",
                                     "day_observed_minutes", "observed_minutes",
                                     "raw_samples"])
    minute = ts.dt.floor("min")
    frame = pd.DataFrame({"minute": minute, "date": minute.dt.date,
                          "hour": minute.dt.hour})
    uniq = frame.drop_duplicates("minute")
    night = (uniq[uniq.hour.isin(NIGHT_HOURS)].groupby("date").size()
             .rename("night_observed_minutes"))
    day = (uniq[uniq.hour.isin(DAY_HOURS)].groupby("date").size()
           .rename("day_observed_minutes"))
    raw = frame.groupby("date").size().rename("raw_samples")
    out = pd.concat([night, day, raw], axis=1).fillna(0).astype(int).reset_index()
    out["observed_minutes"] = out.night_observed_minutes + out.day_observed_minutes
    assert (out.night_observed_minutes.between(0, NIGHT_MINUTES)).all()
    assert (out.day_observed_minutes.between(0, DAY_MINUTES)).all()
    assert (out.observed_minutes <= 1440).all()
    return out[["date", "night_observed_minutes", "day_observed_minutes",
                "observed_minutes", "raw_samples"]]


def native_interval_seconds(ts: pd.Series) -> dict:
    d = pd.Series(pd.to_datetime(ts)).dropna().sort_values().diff().dt.total_seconds().dropna()
    d = d[(d > 0) & (d < 3600)]
    if d.empty:
        return {}
    return {"median_s": float(d.median()), "p05_s": float(d.quantile(.05)),
            "p95_s": float(d.quantile(.95)), "frac_gt_120s": float((d > 120).mean()),
            "regular_1min": bool(abs(d.median() - 60) < 1 and d.quantile(.95) <= 61)}


def discover_schema(files, n_sample=12):
    schema = {}
    for f in files[:n_sample]:
        cols = tuple(pd.read_csv(f, nrows=5).columns)
        e = schema.setdefault(str(cols), {"columns": list(cols),
                                          "example_file": f.name, "count": 0})
        e["count"] += 1
    return schema


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--phase", required=True, choices=["phase1", "phase2"])
    a = ap.parse_args()
    root = Path(a.root)
    if not root.is_dir():
        sys.exit(f"FATAL: {root} is not a directory. Nothing was inventoried.")

    Path("results").mkdir(exist_ok=True)
    files = [f for f in sorted(root.rglob("*")) if f.is_file()]
    manifest = [{"path": str(f.relative_to(root)), "bytes": f.stat().st_size,
                 "sha256": sha256(f)} for f in files]
    json.dump(manifest, open(f"results/manifest_{a.phase}.json", "w"), indent=2)

    csvs = [f for f in files if f.suffix.lower() == ".csv"]
    unmatched = [f.name for f in csvs if classify(f.name) is None]
    json.dump({"schemas": discover_schema(csvs), "n_csv": len(csvs),
               "unmatched_filenames": unmatched[:200], "n_unmatched": len(unmatched)},
              open(f"results/schema_{a.phase}.json", "w"), indent=2)
    if len(unmatched) > 0.25 * max(len(csvs), 1):
        sys.exit(f"FATAL: {len(unmatched)}/{len(csvs)} filenames matched no known pattern. "
                 f"The archive layout differs from what the code repositories suggested. "
                 f"Inspect results/schema_{a.phase}.json and update the pattern "
                 f"DELIBERATELY -- do not let this pass silently.")

    rows, native = [], []
    for f in csvs:
        c = classify(f.name)
        if c is None or c["kind"] not in ("hr", "rhr"):
            continue
        ts = parse_timestamps(pd.read_csv(f)).dropna()
        if ts.empty:
            continue
        cov = per_day_coverage(ts)
        cov.insert(0, "phase", a.phase)
        cov.insert(1, "participant_id", c["pid"])
        cov.insert(2, "device", c["device"])
        cov.insert(3, "source_file", f.name)
        rows.append(cov)
        native.append(dict(phase=a.phase, participant_id=c["pid"], device=c["device"],
                           source_file=f.name, **native_interval_seconds(ts)))

    inv = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    inv.to_parquet(f"results/inventory_{a.phase}.parquet")
    pd.DataFrame(native).to_csv(f"results/native_resolution_{a.phase}.csv", index=False)
    n_unknown = int((inv.device == "UNKNOWN").sum()) if len(inv) else 0
    print(f"{a.phase}: {len(manifest)} files, "
          f"{inv.participant_id.nunique() if len(inv) else 0} participants, "
          f"devices={sorted(inv.device.unique()) if len(inv) else []}, "
          f"participant-days with device=UNKNOWN: {n_unknown}")
    if n_unknown:
        print("  -> resolve with: python3 src/build_device_map.py --phase", a.phase)


if __name__ == "__main__":
    main()
