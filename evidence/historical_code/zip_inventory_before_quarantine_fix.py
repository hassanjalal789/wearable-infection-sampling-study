#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

import numpy as np
import pandas as pd

from phase1_inventory import parse_timestamps

NIGHT_HOURS = set(range(0, 7))
DAY_HOURS = set(range(7, 24))

P1_RE = re.compile(
    r"^(?P<pid>[A-Za-z0-9]+)(?:_\d+)?_"
    r"(?P<kind>hr|steps|sleep)(?:_longterm)?\.csv$",
    re.I
)


def archive_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 << 20), b""):
            h.update(block)
    return h.hexdigest()


def classify(name: str, phase: str):
    p = PurePosixPath(name)
    base = p.name

    if phase == "phase1":
        m = P1_RE.match(base)
        if not m:
            return None

        d = m.groupdict()
        return {
            "pid": d["pid"],
            "kind": d["kind"].lower(),
            "device": "UNKNOWN",
        }

    # Phase 2 layout:
    # .../P123456/Orig_Fitbit_HR.csv
    # .../P123456/Orig_NonFitbit_HR.csv
    if len(p.parts) < 2:
        return None

    pid = p.parts[-2]
    b = base.lower()

    if b == "orig_fitbit_hr.csv":
        return {"pid": pid, "kind": "hr", "device": "Fitbit"}

    if b == "orig_fitbit_st.csv":
        return {"pid": pid, "kind": "steps", "device": "Fitbit"}

    if b == "orig_nonfitbit_hr.csv":
        # Filename proves only NOT Fitbit.
        # Exact candidate device comes from supplementary metadata.
        return {"pid": pid, "kind": "hr", "device": "UNKNOWN"}

    if b == "orig_nonfitbit_st.csv":
        return {"pid": pid, "kind": "steps", "device": "UNKNOWN"}

    return None


def native_from_hist(hist):
    n = int(hist.sum())
    if n == 0:
        return {}

    cum = np.cumsum(hist)

    def q(x):
        target = max(1, int(np.ceil(x * n)))
        return float(np.searchsorted(cum, target))

    med = q(.50)
    p05 = q(.05)
    p95 = q(.95)

    return {
        "median_s": med,
        "p05_s": p05,
        "p95_s": p95,
        "frac_gt_120s": float(hist[121:].sum() / n),
        "regular_1min": bool(abs(med - 60) < 1 and p95 <= 61),
    }


def read_hr_member(z, info):
    minutes = set()
    raw_by_date = Counter()
    hist = np.zeros(3600, dtype=np.int64)

    previous_second = None
    boundary_order_ok = True

    with z.open(info) as fh:
        for chunk in pd.read_csv(fh, chunksize=250000):
            ts = parse_timestamps(chunk).dropna()

            if ts.empty:
                continue

            ts = pd.Series(pd.to_datetime(ts)).dropna()

            # Raw samples/day — diagnostic only.
            counts = ts.dt.date.value_counts()
            for day, n in counts.items():
                raw_by_date[day] += int(n)

            # Coverage: UNIQUE minute bins.
            mins = (
                ts.dt.floor("min")
                .to_numpy(dtype="datetime64[ns]")
                .astype("int64")
            )
            minutes.update(int(x) for x in np.unique(mins))

            # Native interval diagnostic.
            secs = np.sort(
                ts.to_numpy(dtype="datetime64[ns]").astype("int64")
                // 1_000_000_000
            )

            if len(secs) == 0:
                continue

            if previous_second is not None:
                if secs[0] < previous_second:
                    boundary_order_ok = False

                first_diff = secs[0] - previous_second
                if 0 < first_diff < 3600:
                    hist[int(first_diff)] += 1

            if len(secs) > 1:
                d = np.diff(secs)
                d = d[(d > 0) & (d < 3600)]
                if len(d):
                    np.add.at(hist, d.astype(int), 1)

            previous_second = int(secs[-1])

    native = native_from_hist(hist)
    native["chunk_boundary_order_ok"] = bool(boundary_order_ok)

    return minutes, raw_by_date, native


def coverage_from_minutes(minutes, raw_by_date):
    if not minutes:
        return pd.DataFrame(columns=[
            "date", "night_observed_minutes",
            "day_observed_minutes", "observed_minutes",
            "raw_samples"
        ])

    arr = np.fromiter(minutes, dtype=np.int64)
    dt = pd.Series(pd.to_datetime(arr, unit="ns"))

    frame = pd.DataFrame({
        "minute": dt,
        "date": dt.dt.date,
        "hour": dt.dt.hour,
    })

    night = (
        frame[frame.hour.isin(NIGHT_HOURS)]
        .groupby("date").size()
        .rename("night_observed_minutes")
    )

    day = (
        frame[frame.hour.isin(DAY_HOURS)]
        .groupby("date").size()
        .rename("day_observed_minutes")
    )

    raw = pd.Series(raw_by_date, name="raw_samples")

    out = (
        pd.concat([night, day, raw], axis=1)
        .fillna(0)
        .astype(int)
        .reset_index()
        .rename(columns={"index": "date"})
    )

    out["observed_minutes"] = (
        out.night_observed_minutes +
        out.day_observed_minutes
    )

    assert out.night_observed_minutes.between(0, 420).all()
    assert out.day_observed_minutes.between(0, 1020).all()
    assert (out.observed_minutes <= 1440).all()

    return out[[
        "date",
        "night_observed_minutes",
        "day_observed_minutes",
        "observed_minutes",
        "raw_samples",
    ]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--phase", required=True,
                    choices=["phase1", "phase2"])
    a = ap.parse_args()

    zp = Path(a.zip)

    if not zp.is_file():
        raise SystemExit(f"FATAL: ZIP not found: {zp}")

    Path("results").mkdir(exist_ok=True)

    print(f"{a.phase}: opening {zp}")

    with zipfile.ZipFile(zp) as z:
        members = [
            x for x in z.infolist()
            if not x.is_dir()
            and not x.filename.startswith("__MACOSX/")
        ]

        csvs = [
            x for x in members
            if x.filename.lower().endswith(".csv")
        ]

        # Archive/member provenance without extracting 36 GB.
        manifest = {
            "archive": str(zp),
            "archive_bytes": zp.stat().st_size,
            "archive_sha256": archive_sha256(zp),
            "integrity_basis":
                "archive SHA-256 plus ZIP member CRC32",
            "members": [
                {
                    "path": x.filename,
                    "bytes": x.file_size,
                    "compressed_bytes": x.compress_size,
                    "crc32": f"{x.CRC:08x}",
                }
                for x in members
            ],
        }

        with open(f"results/manifest_{a.phase}.json", "w") as f:
            json.dump(manifest, f, indent=2)

        classified = {}
        unmatched = []

        for info in csvs:
            c = classify(info.filename, a.phase)
            if c is None:
                unmatched.append(info.filename)
            else:
                classified[info.filename] = c

        with open(f"results/schema_{a.phase}.json", "w") as f:
            json.dump({
                "n_csv": len(csvs),
                "n_matched": len(classified),
                "n_unmatched": len(unmatched),
                "unmatched_filenames": unmatched[:200],
            }, f, indent=2)

        if len(unmatched) > .25 * max(len(csvs), 1):
            raise SystemExit(
                f"FATAL: {len(unmatched)}/{len(csvs)} CSV filenames "
                "matched no known pattern."
            )

        groups = defaultdict(list)

        for info in csvs:
            c = classified.get(info.filename)
            if c and c["kind"] == "hr":
                groups[c["pid"]].append((info, c))

        rows = []
        native_rows = []

        total = len(groups)

        for idx, pid in enumerate(sorted(groups), 1):
            all_minutes = set()
            all_raw = Counter()
            known_devices = set()
            sources = []

            for info, c in groups[pid]:
                sources.append(PurePosixPath(info.filename).name)

                if c["device"] != "UNKNOWN":
                    known_devices.add(c["device"])

                mins, raw, native = read_hr_member(z, info)

                # Critical: union across regular/long-term/split files.
                all_minutes.update(mins)
                all_raw.update(raw)

                native_rows.append({
                    "phase": a.phase,
                    "participant_id": pid,
                    "device": c["device"],
                    "source_file":
                        PurePosixPath(info.filename).name,
                    **native,
                })

            if len(known_devices) == 1:
                device = next(iter(known_devices))
            elif len(known_devices) > 1:
                device = "CONFLICT"
            else:
                device = "UNKNOWN"

            cov = coverage_from_minutes(all_minutes, all_raw)

            if not cov.empty:
                cov.insert(0, "phase", a.phase)
                cov.insert(1, "participant_id", pid)
                cov.insert(2, "device", device)
                cov.insert(
                    3,
                    "source_file",
                    ";".join(sorted(sources))
                )
                rows.append(cov)

            if idx % 50 == 0 or idx == total:
                print(f"  {idx}/{total} HR participants")

    inv = (
        pd.concat(rows, ignore_index=True)
        if rows else pd.DataFrame()
    )

    inv.to_parquet(
        f"results/inventory_{a.phase}.parquet",
        index=False
    )

    pd.DataFrame(native_rows).to_csv(
        f"results/native_resolution_{a.phase}.csv",
        index=False
    )

    print("\n=== SUMMARY ===")
    print("phase:", a.phase)
    print("CSV files:", len(csvs))
    print("unmatched:", len(unmatched))
    print("HR participants:", inv.participant_id.nunique())
    print("participant-days:", len(inv))

    if len(inv):
        print("\ndevices:")
        print(
            inv.groupby("device")
            .participant_id.nunique()
            .to_string()
        )

        dup = inv.duplicated(
            ["phase", "participant_id", "date"]
        ).sum()

        print("\nduplicate participant-days:", int(dup))
        assert dup == 0

    print("\nDONE:", a.phase)


if __name__ == "__main__":
    main()
