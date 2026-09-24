#!/usr/bin/env python3
"""
Primary E3 experiment runner — PRE-OUTCOME ARTEFACT.

Commit this file before using --run-real.

Frozen primary design
---------------------
- CENTRAL modelled-energy E3.
- E3 must resolve to N=7, L=10 min in LOW/CENTRAL/HIGH energy scenarios.
- Arms: S1 reference; S2, S3, S5, S4 primary schedules; S3r/S6 M1 pair.
- TOD-z primary detector.
- <=2 alert-days/person-month threshold calibration.
- Calibration: all historical negative z-defined days through onset-28 inclusive,
  outside every [episode onset-21, episode onset+21] exclusion window.
- Pair-specific calibration floor C_floor=16.
- Presymptomatic endpoint: onset-21 through onset-1 inclusive.
- Day 0 is descriptive and separate.
- Warning for non-detection is missing, never imputed to zero.
- M1 daily feasibility and delivered-minute counts are retained.

The real-data path refuses to run unless this file is tracked by Git and the
working tree is clean. It writes once to a commit-versioned results directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import schedules as S
from phase1_inventory import parse_timestamps
from tod_z import TODZConfig, alert_days, calibrate_tau, daily_statistics

ENERGY_FREEZE_COMMIT = "4023717"
N_BUDGET = 7
BURST_MINUTES = 10
ALERT_BUDGET_PER_MONTH = 2.0
C_FLOOR = 16
CAL_STOP = 28
PRE_START = 21
PRE_END = 1

ZIP_PATHS = {
    "phase1": ROOT / "data_raw" / "COVID-19-Wearables.zip",
    "phase2": ROOT / "data_raw" / "COVID-19-Phase2-Wearables.zip",
}

PRIMARY_ARMS = ("S2", "S3", "S5", "S4")
M1_ARMS = ("S3r", "S6")
ALL_ARMS = ("S1",) + PRIMARY_ARMS + M1_ARMS


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT
    ).strip()


def git_ancestor(older: str, newer: str = "HEAD") -> bool:
    p = subprocess.run(
        ["git", "merge-base", "--is-ancestor", older, newer],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return p.returncode == 0


def sha256_file(path: Path, chunk: int = 8 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def load_energy_audit() -> dict:
    p = ROOT / "results" / "modelled_energy_match_audit.json"
    x = json.loads(p.read_text())
    assert x["primary_E3_all_scenarios_feasible"] is True
    for scenario, rec in x["scenarios"].items():
        arms = rec["budgets"]["E3"]["arms"]
        for arm in ("S2", "S3", "S5", "S4", "S3r", "S6"):
            assert arms[arm]["status"] == "FEASIBLE_WITHIN_5PCT", (scenario, arm)
            assert int(arms[arm]["N"]) == N_BUDGET, (scenario, arm)
    return x


def load_final_cohort_pairs(path: Path | None = None) -> list[tuple[str, str]]:
    path = path or ROOT / "results" / "cohort.json"
    x = json.loads(path.read_text())

    preferred = (
        "final_cohort", "final", "eligible_final", "final_participants",
        "cohort_final", "included"
    )
    if isinstance(x, dict):
        for k in preferred:
            v = x.get(k)
            if isinstance(v, list) and len(v) == 38 and all(
                isinstance(z, (list, tuple)) and len(z) == 2 for z in v
            ):
                return [(str(a), str(b)) for a, b in v]

        candidates = []
        for k, v in x.items():
            if (
                isinstance(v, list)
                and len(v) == 38
                and all(isinstance(z, (list, tuple)) and len(z) == 2 for z in v)
            ):
                candidates.append((k, [(str(a), str(b)) for a, b in v]))
        if len(candidates) == 1:
            return candidates[0][1]

    raise RuntimeError(
        "Could not uniquely identify the frozen N=38 final cohort in cohort.json."
    )


def load_onsets(path: Path | None = None) -> pd.DataFrame:
    path = path or ROOT / "results" / "onset_labels.csv"
    d = pd.read_csv(path)
    d["onset_date"] = pd.to_datetime(d["onset_date"], errors="coerce").dt.normalize()
    if "diagnosis_date" in d:
        d["diagnosis_date"] = pd.to_datetime(
            d["diagnosis_date"], errors="coerce"
        ).dt.normalize()
    return d


def participant_onset_info(onsets: pd.DataFrame, phase: str, pid: str) -> dict:
    q = onsets[
        (onsets["phase"] == phase) & (onsets["participant_id"] == pid)
    ].copy()
    q = q[q["onset_date"].notna()].sort_values("onset_date")
    if q.empty:
        raise RuntimeError(f"No onset date for {phase}:{pid}")
    anchors = [pd.Timestamp(x).normalize() for x in q["onset_date"].tolist()]
    return {"index_onset": anchors[0], "episode_onsets": anchors}


def exclusion_mask(days: pd.Series, anchors: list[pd.Timestamp]) -> pd.Series:
    d = pd.to_datetime(days).dt.normalize()
    mask = pd.Series(False, index=d.index)
    for a in anchors:
        mask |= d.between(a - pd.Timedelta(days=21), a + pd.Timedelta(days=21))
    return mask


def calibration_frame(
    res: pd.DataFrame,
    onset: pd.Timestamp,
    episode_onsets: list[pd.Timestamp],
) -> pd.DataFrame:
    """All negative z-defined days through onset-28 inclusive."""
    d = res.copy()
    d["day"] = pd.to_datetime(d["day"]).dt.normalize()
    stop = pd.Timestamp(onset).normalize() - pd.Timedelta(days=CAL_STOP)
    neg = ~exclusion_mask(d["day"], episode_onsets)
    return d[d["z_defined"] & neg & (d["day"] <= stop)].sort_values("day").copy()


def outcome_from_stats(
    res: pd.DataFrame,
    onset: pd.Timestamp,
    episode_onsets: list[pd.Timestamp],
    arm: str,
    phase: str = "synthetic",
    pid: str = "synthetic",
    cfg: TODZConfig | None = None,
) -> dict:
    cfg = cfg or TODZConfig()
    onset = pd.Timestamp(onset).normalize()
    cal = calibration_frame(res, onset, episode_onsets)

    out = {
        "phase": phase,
        "participant_id": pid,
        "arm": arm,
        "calibration_z_days": int(len(cal)),
        "calibration_floor_met": bool(len(cal) >= C_FLOOR),
        "tau": np.nan,
        "finite_threshold": False,
        "calibration_saturated": False,
        "achieved_calibration_alert_rate": np.nan,
        "presymptomatic_evaluable_days": 0,
        "presymptomatic_detected": pd.NA,
        "warning_days": np.nan,
        "day0_evaluable": False,
        "day0_alert": pd.NA,
        "at_or_before_onset": pd.NA,
    }

    if len(cal) < C_FLOOR:
        return out

    crec = calibrate_tau(cal, ALERT_BUDGET_PER_MONTH, cfg)
    tau = float(crec["tau"])

    d = res.copy()
    d["day"] = pd.to_datetime(d["day"]).dt.normalize()
    d["alert"] = alert_days(d, tau, cfg).astype(bool).to_numpy()

    pre = d[
        d["day"].between(
            onset - pd.Timedelta(days=PRE_START),
            onset - pd.Timedelta(days=PRE_END),
        )
    ]
    pre_eval = pre[pre["z_defined"]].copy()
    day0_eval = d[(d["day"] == onset) & d["z_defined"]].copy()

    out.update({
        "tau": tau,
        "finite_threshold": bool(crec["finite_threshold"]),
        "calibration_saturated": bool(crec["calibration_saturated"]),
        "achieved_calibration_alert_rate": float(crec["achieved_rate"]),
        "presymptomatic_evaluable_days": int(len(pre_eval)),
        "day0_evaluable": bool(len(day0_eval)),
    })

    if len(pre_eval):
        alerted = pre_eval[pre_eval["alert"]].sort_values("day")
        detected = not alerted.empty
        out["presymptomatic_detected"] = bool(detected)
        if detected:
            out["warning_days"] = int(
                (onset - pd.Timestamp(alerted.iloc[0]["day"])).days
            )

    if len(day0_eval):
        out["day0_alert"] = bool(day0_eval["alert"].any())

    pre_det = out["presymptomatic_detected"]
    d0 = out["day0_alert"]
    if not (pd.isna(pre_det) and pd.isna(d0)):
        out["at_or_before_onset"] = bool(
            (False if pd.isna(pre_det) else pre_det)
            or (False if pd.isna(d0) else d0)
        )
    return out


def hierarchical_pair(a: dict, b: dict) -> dict:
    if not (a["calibration_floor_met"] and b["calibration_floor_met"]):
        return {"pair_evaluable": False, "result": "NA_CALIBRATION"}

    ad = a["presymptomatic_detected"]
    bd = b["presymptomatic_detected"]
    if pd.isna(ad) or pd.isna(bd):
        return {"pair_evaluable": False, "result": "NA_OUTCOME"}

    ad, bd = bool(ad), bool(bd)
    if ad and not bd:
        return {"pair_evaluable": True, "result": "A_WIN"}
    if bd and not ad:
        return {"pair_evaluable": True, "result": "B_WIN"}
    if not ad and not bd:
        return {"pair_evaluable": True, "result": "TIE"}

    aw, bw = float(a["warning_days"]), float(b["warning_days"])
    if aw > bw:
        return {"pair_evaluable": True, "result": "A_WIN"}
    if bw > aw:
        return {"pair_evaluable": True, "result": "B_WIN"}
    return {"pair_evaluable": True, "result": "TIE"}


def _value_column(df: pd.DataFrame, wanted: str) -> str:
    lower = {str(c).lower(): c for c in df.columns}
    if wanted not in lower:
        raise RuntimeError(f"Missing {wanted!r}; got columns {list(df.columns)}")
    return lower[wanted]


def _members_for(
    z: zipfile.ZipFile, phase: str, pid: str, kind: str
) -> list[str]:
    from zip_inventory import classify

    out = []
    for name in z.namelist():
        c = classify(name, phase)
        if c is None or c["pid"] != pid or c["kind"] != kind:
            continue
        if phase == "phase2" and c["device"] != "Fitbit":
            continue
        out.append(name)
    return sorted(out)


def _read_hr(z: zipfile.ZipFile, members: list[str]) -> pd.DataFrame:
    pieces = []
    for name in members:
        with z.open(name) as fh:
            for chunk in pd.read_csv(fh, chunksize=250_000):
                ts = parse_timestamps(chunk)
                hc = _value_column(chunk, "heartrate")
                x = pd.DataFrame({
                    "timestamp": pd.to_datetime(ts, errors="coerce"),
                    "hr": pd.to_numeric(chunk[hc], errors="coerce"),
                }).dropna(subset=["timestamp", "hr"])
                if len(x):
                    pieces.append(x)
    if not pieces:
        return pd.DataFrame(columns=["timestamp", "hr"])
    d = pd.concat(pieces, ignore_index=True)
    # Prospective deterministic source normalisation.
    return (
        d.groupby("timestamp", as_index=False)["hr"]
        .mean()
        .sort_values("timestamp")
        .reset_index(drop=True)
    )


def _read_steps(z: zipfile.ZipFile, members: list[str]) -> pd.Series:
    pieces = []
    for name in members:
        with z.open(name) as fh:
            for chunk in pd.read_csv(fh, chunksize=250_000):
                ts = parse_timestamps(chunk)
                sc = _value_column(chunk, "steps")
                x = pd.DataFrame({
                    "timestamp": pd.to_datetime(ts, errors="coerce"),
                    "steps": pd.to_numeric(chunk[sc], errors="coerce"),
                }).dropna(subset=["timestamp"])
                if len(x):
                    x["minute"] = x["timestamp"].dt.floor("min")
                    pieces.append(x[["minute", "steps"]])
    if not pieces:
        return pd.Series(dtype=float, name="steps")
    d = pd.concat(pieces, ignore_index=True)
    return d.groupby("minute")["steps"].sum(min_count=1).sort_index()


def normalise_step_semantics(
    phase: str,
    hr: pd.DataFrame,
    steps: pd.Series,
) -> tuple[pd.Series, dict]:
    # A6: Phase-2 Fitbit step files omit zero-step timestamps.  At the
    # minute-based schedule/rest layer, infer zero only for HR-observed minutes
    # with no explicit step-file record.  Explicit values (including NaN) win;
    # minutes with neither HR nor a step record remain unknown.  Phase 1 is
    # returned unchanged.
    out = steps.copy().sort_index()
    out.name = "steps"

    meta = {
        "phase2_sparse_step_semantics_applied": False,
        "n_step_minutes_original": int(len(out)),
        "n_phase2_zero_step_minutes_inferred": 0,
    }
    if phase != "phase2":
        meta["n_step_minutes_after_semantics"] = int(len(out))
        return out, meta

    hr_minutes = pd.DatetimeIndex(
        pd.to_datetime(hr["timestamp"], errors="coerce")
        .dropna()
        .dt.floor("min")
        .unique()
    ).sort_values()

    recorded_minutes = pd.DatetimeIndex(out.index)
    infer_minutes = hr_minutes.difference(recorded_minutes)

    out = out.reindex(recorded_minutes.union(hr_minutes)).sort_index()
    if len(infer_minutes):
        out.loc[infer_minutes] = 0.0

    meta.update({
        "phase2_sparse_step_semantics_applied": True,
        "n_phase2_zero_step_minutes_inferred": int(len(infer_minutes)),
        "n_step_minutes_after_semantics": int(len(out)),
    })
    return out, meta


def load_participant_raw(
    phase: str, pid: str
) -> tuple[pd.DataFrame, pd.Series, dict]:
    zp = ZIP_PATHS[phase]
    with zipfile.ZipFile(zp) as z:
        hm = _members_for(z, phase, pid, "hr")
        sm = _members_for(z, phase, pid, "steps")
        if not hm or not sm:
            raise RuntimeError(
                f"{phase}:{pid} missing HR/steps member; HR={hm}, steps={sm}"
            )
        hr = _read_hr(z, hm)
        steps = _read_steps(z, sm)

    if hr.empty:
        raise RuntimeError(f"{phase}:{pid}: no parseable HR rows")

    steps, step_meta = normalise_step_semantics(phase, hr, steps)

    return hr, steps, {
        "hr_members": hm,
        "step_members": sm,
        "n_hr_rows_after_timestamp_dedup": int(len(hr)),
        "n_step_minutes": int(len(steps)),
        **step_meta,
    }


def _day_input(
    phase: str,
    pid: str,
    day: pd.Timestamp,
    hr_day: pd.DataFrame,
    steps: pd.Series,
) -> S.DayInput:
    obs = np.zeros(S.MINUTES, dtype=bool)
    if len(hr_day):
        idx = (
            hr_day["timestamp"].dt.hour.to_numpy() * 60
            + hr_day["timestamp"].dt.minute.to_numpy()
        ).astype(int)
        obs[np.unique(idx)] = True

    st = np.full(S.MINUTES, np.nan, dtype=float)
    sd = steps[
        (steps.index >= day) & (steps.index < day + pd.Timedelta(days=1))
    ]
    if len(sd):
        idx = (
            sd.index.hour.to_numpy() * 60 + sd.index.minute.to_numpy()
        ).astype(int)
        st[idx] = sd.to_numpy(dtype=float)

    return S.DayInput(
        participant_id=f"{phase}:{pid}",
        date=day.date().isoformat(),
        observed=obs,
        steps=st,
    )


def _retain_hr(
    hr_day: pd.DataFrame, mask: S.Mask, steps: pd.Series
) -> pd.DataFrame:
    if hr_day.empty:
        return pd.DataFrame(columns=["timestamp", "hr", "steps"])
    idx = (
        hr_day["timestamp"].dt.hour.to_numpy() * 60
        + hr_day["timestamp"].dt.minute.to_numpy()
    ).astype(int)
    x = hr_day.loc[mask.retained[idx], ["timestamp", "hr"]].copy()
    if x.empty:
        return pd.DataFrame(columns=["timestamp", "hr", "steps"])
    x["steps"] = x["timestamp"].dt.floor("min").map(steps)
    return x


def schedule_participant(
    phase: str,
    pid: str,
    hr: pd.DataFrame,
    steps: pd.Series,
    onset: pd.Timestamp,
):
    hr = hr.copy()
    hr["timestamp"] = pd.to_datetime(hr["timestamp"])
    hr["day"] = hr["timestamp"].dt.normalize()
    onset = pd.Timestamp(onset).normalize()

    starts = [hr["day"].min()]
    if len(steps):
        starts.append(pd.Timestamp(steps.index.min()).normalize())
    expected_days = pd.date_range(min(starts), onset, freq="D")

    by_day = {k: g.copy() for k, g in hr.groupby("day")}
    empty = hr.iloc[0:0].copy()
    retained = {arm: [] for arm in ALL_ARMS}
    qc_rows, m1_rows = [], []

    for day in expected_days:
        hd = by_day.get(day, empty)
        di = _day_input(phase, pid, day, hd, steps)

        masks = {
            "S1": S.s1_continuous(di),
            "S2": S.s2_uniform_block(di, N_BUDGET, BURST_MINUTES),
            "S3": S.s3_nocturnal(di, N_BUDGET, BURST_MINUTES),
            "S5": S.s5_random_block(di, N_BUDGET, BURST_MINUTES),
            "S4": S.s4_rest_triggered(di, N_BUDGET, BURST_MINUTES),
        }

        s3r, s6, mrec = S.m1_matched_pair(
            di, n_budget=N_BUDGET, L=BURST_MINUTES
        )
        m1_rows.append({
            "phase": phase,
            "participant_id": pid,
            "day": day,
            **mrec,
        })
        if mrec["available"]:
            masks["S3r"] = s3r
            masks["S6"] = s6

        for arm in ALL_ARMS:
            mask = masks.get(arm)
            if mask is None:
                qc_rows.append({
                    "phase": phase,
                    "participant_id": pid,
                    "day": day,
                    "arm": arm,
                    "n_requested": N_BUDGET,
                    "n_scheduled": 0,
                    "shortfall": N_BUDGET,
                    "scheduled_minutes": 0,
                    "delivered_minutes": 0,
                    "m1_available": False,
                })
                continue

            x = _retain_hr(hd, mask, steps)
            if len(x):
                retained[arm].append(x)

            qc_rows.append({
                "phase": phase,
                "participant_id": pid,
                "day": day,
                "arm": arm,
                "n_requested": int(mask.n_requested),
                "n_scheduled": int(mask.n_scheduled),
                "shortfall": int(mask.shortfall),
                "scheduled_minutes": int(mask.samples_scheduled),
                "delivered_minutes": int(mask.samples_delivered),
                "m1_available": (
                    bool(mrec["available"]) if arm in M1_ARMS else pd.NA
                ),
            })

    frames = {}
    for arm, pieces in retained.items():
        frames[arm] = (
            pd.concat(pieces, ignore_index=True).sort_values("timestamp")
            if pieces
            else pd.DataFrame(columns=["timestamp", "hr", "steps"])
        )

    return (
        frames,
        pd.DataFrame(qc_rows),
        pd.DataFrame(m1_rows),
        expected_days,
    )


def run_participant(
    phase: str,
    pid: str,
    onsets: pd.DataFrame,
    cfg: TODZConfig | None = None,
):
    cfg = cfg or TODZConfig()
    info = participant_onset_info(onsets, phase, pid)
    onset = info["index_onset"]

    hr, steps, meta = load_participant_raw(phase, pid)
    frames, qc, m1, expected_days = schedule_participant(
        phase, pid, hr, steps, onset
    )

    rows = []
    for arm in ALL_ARMS:
        stats = daily_statistics(
            frames[arm], cfg=cfg, expected_days=expected_days
        )
        rec = outcome_from_stats(
            stats, onset, info["episode_onsets"], arm,
            phase=phase, pid=pid, cfg=cfg
        )

        lo = onset - pd.Timedelta(days=PRE_START)
        hi = onset - pd.Timedelta(days=PRE_END)
        q = qc[(qc["arm"] == arm) & qc["day"].between(lo, hi)]
        rec["event_scheduled_minutes"] = int(q["scheduled_minutes"].sum())
        rec["event_delivered_minutes"] = int(q["delivered_minutes"].sum())
        rec["event_days_with_delivery"] = int(
            (q["delivered_minutes"] > 0).sum()
        )
        rows.append(rec)

    lo = onset - pd.Timedelta(days=PRE_START)
    hi = onset - pd.Timedelta(days=PRE_END)
    mp = m1[m1["day"].between(lo, hi)]
    meta["m1_event_days"] = int(len(mp))
    meta["m1_unavailable_event_days"] = (
        int((~mp["available"].astype(bool)).sum()) if len(mp) else 0
    )
    meta["m1_unavailable_event_fraction"] = (
        float((~mp["available"].astype(bool)).mean()) if len(mp) else np.nan
    )
    return rows, qc, m1, meta


def preflight() -> None:
    if not git_ancestor(ENERGY_FREEZE_COMMIT):
        raise RuntimeError(
            f"Energy freeze commit {ENERGY_FREEZE_COMMIT} is not an ancestor of HEAD."
        )

    load_energy_audit()
    cohort = load_final_cohort_pairs()
    assert len(cohort) == 38 and len(set(cohort)) == 38

    onsets = load_onsets()
    for phase, pid in cohort:
        if phase not in ZIP_PATHS:
            raise RuntimeError(f"Unexpected phase {phase}:{pid}")
        if not ZIP_PATHS[phase].exists():
            raise FileNotFoundError(ZIP_PATHS[phase])
        participant_onset_info(onsets, phase, pid)

    print("PRE-FLIGHT PASS")
    print("  frozen cohort: N=38")
    print("  E3 LOW/CENTRAL/HIGH: all arms feasible at N=7")
    print("  burst length: 10 minutes")
    print("  alert budget: <=2 alert-days/person-month")
    print("  pair calibration floor: 16 z-defined days")
    print("  raw ZIPs present")


def require_real_run_freeze() -> str:
    preflight()
    try:
        git("ls-files", "--error-unmatch", "src/primary_e3_experiment.py")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            "Refusing real run: primary_e3_experiment.py is not committed."
        ) from e

    dirty = git("status", "--porcelain")
    if dirty:
        raise RuntimeError(
            "Refusing real run: Git working tree is not clean.\n" + dirty
        )
    return git("rev-parse", "HEAD")


def run_real(hash_inputs: bool = False) -> Path:
    commit = require_real_run_freeze()
    outdir = ROOT / "results" / f"primary_e3_run_{commit[:7]}"
    if outdir.exists():
        raise RuntimeError(f"Refusing to overwrite {outdir}")
    outdir.mkdir(parents=True)

    cohort = load_final_cohort_pairs()
    onsets = load_onsets()
    cfg = TODZConfig()

    outcome_rows, qc_parts, m1_parts, meta_rows = [], [], [], []

    for i, (phase, pid) in enumerate(cohort, 1):
        print(f"[{i:02d}/38] processing {phase}:{pid}", flush=True)
        rows, qc, m1, meta = run_participant(phase, pid, onsets, cfg)
        outcome_rows.extend(rows)
        qc_parts.append(qc)
        m1_parts.append(m1)
        meta_rows.append({"phase": phase, "participant_id": pid, **meta})

    outcomes = pd.DataFrame(outcome_rows)
    qc = pd.concat(qc_parts, ignore_index=True)
    m1 = pd.concat(m1_parts, ignore_index=True)

    outcomes.to_csv(outdir / "arm_outcomes.csv", index=False)
    qc.to_csv(outdir / "schedule_qc_daily.csv", index=False)
    m1.to_csv(outdir / "m1_daily_feasibility.csv", index=False)
    pd.DataFrame(meta_rows).to_csv(
        outdir / "participant_input_and_m1_summary.csv", index=False
    )

    lookup = {
        (r["phase"], r["participant_id"], r["arm"]): r
        for r in outcome_rows
    }
    comparisons = [
        ("H1", "S3", "S2"),
        ("M1", "S3r", "S6"),
        ("H2", "S3", "S5"),
        ("H3", "S3", "S4"),
    ]
    pair_rows = []
    for phase, pid in cohort:
        for label, aa, bb in comparisons:
            h = hierarchical_pair(
                lookup[(phase, pid, aa)],
                lookup[(phase, pid, bb)],
            )
            pair_rows.append({
                "phase": phase,
                "participant_id": pid,
                "comparison": label,
                "A": aa,
                "B": bb,
                **h,
            })
    pd.DataFrame(pair_rows).to_csv(
        outdir / "pair_hierarchy.csv", index=False
    )

    manifest = {
        "status": "REAL_PRIMARY_E3_OUTCOMES_GENERATED",
        "git_commit": commit,
        "energy_freeze_commit": ENERGY_FREEZE_COMMIT,
        "scenario": "CENTRAL",
        "budget": "E3",
        "N_budget": N_BUDGET,
        "burst_minutes": BURST_MINUTES,
        "alert_budget_per_person_month": ALERT_BUDGET_PER_MONTH,
        "C_floor": C_FLOOR,
        "phase2_step_semantics": (
            "At minute resolution, infer steps=0 only for Phase-2 Fitbit "
            "HR-observed minutes with no explicit step-file record; explicit "
            "step records win; minutes with neither HR nor steps remain unknown."
        ),
        "calibration_stop": "through onset-28 inclusive",
        "presymptomatic_window": "onset-21 through onset-1 inclusive",
        "n_frozen_cohort": 38,
        "input_archives": {
            phase: {
                "path": str(path.relative_to(ROOT)),
                "bytes": path.stat().st_size,
                **({"sha256": sha256_file(path)} if hash_inputs else {}),
            }
            for phase, path in ZIP_PATHS.items()
        },
        "terminal_policy": (
            "No detection/warning summary printed during generation."
        ),
    }
    (outdir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )

    print("REAL RUN COMPLETE")
    print("Outcome files:", outdir)
    print("No scientific outcome values were printed.")
    return outdir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preflight", action="store_true")
    ap.add_argument("--run-real", action="store_true")
    ap.add_argument("--hash-inputs", action="store_true")
    a = ap.parse_args()

    if a.run_real:
        run_real(hash_inputs=a.hash_inputs)
    else:
        preflight()


if __name__ == "__main__":
    main()
