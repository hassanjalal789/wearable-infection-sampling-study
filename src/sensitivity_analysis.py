#!/usr/bin/env python3
"""
Core sensitivity analysis for corrected primary E3 run.

This is sensitivity-only. It does not reopen fixed-sequence confirmatory testing.
No sensitivity p-values are produced.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import primary_e3_experiment as P

PRIMARY_RUN = ROOT / "results" / "primary_e3_run_83cc8d1"
OUTDIR = PRIMARY_RUN / "sensitivity_analysis"
ALERT_BUDGETS = (1.0, 4.0)
BOOT_N = 10_000
BOOT_SEED = 20260904
PRIMARY_PAIRS = (
    ("H1", "S3", "S2"),
    ("M1", "S3r", "S6"),
    ("H2", "S3", "S5"),
    ("H3", "S3", "S4"),
)
ALL_PRIMARY_ARMS = ("S2", "S3", "S5", "S4", "S3r", "S6")


def bca_ci(x, seed):
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 2:
        return (float("nan"), float("nan"))
    obs = float(x.mean())
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(BOOT_N, n))
    boot = x[idx].mean(axis=1)
    prop = ((boot < obs).sum() + 0.5 * (boot == obs).sum()) / BOOT_N
    eps = 0.5 / BOOT_N
    prop = min(max(prop, eps), 1 - eps)
    nd = NormalDist()
    z0 = nd.inv_cdf(prop)
    jack = np.array([np.delete(x, i).mean() for i in range(n)])
    jm = jack.mean()
    num = np.sum((jm - jack) ** 3)
    den = 6.0 * (np.sum((jm - jack) ** 2) ** 1.5)
    acc = 0.0 if den == 0 else float(num / den)

    def adj(q):
        z = nd.inv_cdf(q)
        d = 1.0 - acc * (z0 + z)
        return q if abs(d) < 1e-12 else nd.cdf(z0 + (z0 + z) / d)

    lo = min(max(adj(0.025), 0.0), 1.0)
    hi = min(max(adj(0.975), 0.0), 1.0)
    if lo > hi:
        lo, hi = hi, lo
    return float(np.quantile(boot, lo)), float(np.quantile(boot, hi))


def pair_rows_from_outcomes(outcomes: pd.DataFrame) -> pd.DataFrame:
    lookup = {
        (r.phase, r.participant_id, r.arm): r._asdict()
        for r in outcomes.itertuples(index=False)
    }
    rows = []
    ids = outcomes[["phase", "participant_id"]].drop_duplicates()
    for pidrow in ids.itertuples(index=False):
        phase, pid = pidrow.phase, pidrow.participant_id
        for label, aa, bb in PRIMARY_PAIRS:
            ka, kb = (phase, pid, aa), (phase, pid, bb)
            if ka not in lookup or kb not in lookup:
                continue
            h = P.hierarchical_pair(lookup[ka], lookup[kb])
            rows.append({
                "phase": phase,
                "participant_id": pid,
                "comparison": label,
                "A": aa,
                "B": bb,
                **h,
            })
    return pd.DataFrame(rows)


def summarize_pairs(pair_df: pd.DataFrame, scenario: str, seed_offset=0) -> pd.DataFrame:
    rows = []
    for j, (label, aa, bb) in enumerate(PRIMARY_PAIRS):
        d = pair_df[
            (pair_df["comparison"] == label)
            & pair_df["result"].isin(["A_WIN", "B_WIN", "TIE"])
        ]
        W = int((d["result"] == "A_WIN").sum())
        L = int((d["result"] == "B_WIN").sum())
        T = int((d["result"] == "TIE").sum())
        n = W + L + T
        theta = (W + 0.5*T) / n if n else np.nan
        if n:
            x = np.r_[np.ones(W), np.zeros(L), np.full(T, 0.5)]
            lo, hi = bca_ci(x, BOOT_SEED + seed_offset + j)
        else:
            lo = hi = np.nan
        rows.append({
            "scenario": scenario,
            "comparison": label,
            "A": aa,
            "B": bb,
            "N": n,
            "W": W,
            "L": L,
            "T": T,
            "theta": theta,
            "theta_bca95_lo": lo,
            "theta_bca95_hi": hi,
            "sensitivity_p_value": np.nan,
        })
    return pd.DataFrame(rows)


def fixed_budget_outcome(res, onset, episode_onsets, arm, phase, pid, budget, cfg):
    onset = pd.Timestamp(onset).normalize()
    cal = P.calibration_frame(res, onset, episode_onsets)
    out = {
        "phase": phase,
        "participant_id": pid,
        "arm": arm,
        "calibration_z_days": int(len(cal)),
        "calibration_floor_met": bool(len(cal) >= P.C_FLOOR),
        "presymptomatic_detected": pd.NA,
        "warning_days": np.nan,
        "day0_alert": pd.NA,
    }
    if len(cal) < P.C_FLOOR:
        return out

    crec = P.calibrate_tau(cal, budget, cfg)
    tau = float(crec["tau"])

    d = res.copy()
    d["day"] = pd.to_datetime(d["day"]).dt.normalize()
    d["alert"] = P.alert_days(d, tau, cfg).astype(bool).to_numpy()

    pre = d[d["day"].between(
        onset - pd.Timedelta(days=P.PRE_START),
        onset - pd.Timedelta(days=P.PRE_END),
    )]
    pe = pre[pre["z_defined"]]
    if len(pe):
        al = pe[pe["alert"]].sort_values("day")
        det = not al.empty
        out["presymptomatic_detected"] = bool(det)
        if det:
            out["warning_days"] = int(
                (onset - pd.Timestamp(al.iloc[0]["day"])).days
            )
    d0 = d[(d["day"] == onset) & d["z_defined"]]
    if len(d0):
        out["day0_alert"] = bool(d0["alert"].any())
    return out


def no_tod_daily_statistics(df, cfg, expected_days):
    all_rows = df.dropna(subset=["timestamp"]).copy()
    all_rows["timestamp"] = pd.to_datetime(all_rows["timestamp"])
    all_rows["day"] = all_rows["timestamp"].dt.normalize()
    skeleton = set(all_rows["day"].unique())
    skeleton |= set(pd.to_datetime(pd.Index(expected_days)).normalize())
    days = pd.DatetimeIndex(sorted(skeleton))

    d = all_rows.dropna(subset=["hr"]).copy()
    d["is_rest"] = d["steps"].fillna(1.0).to_numpy() == 0.0
    hr_counts = d.groupby("day").size().to_dict()
    rest = d[d["is_rest"]]
    by_day = {k: g for k, g in rest.groupby("day")}
    eligible = [
        k for k in days
        if len(by_day.get(k, rest.iloc[0:0])) >= cfg.min_rest_samples
    ]

    out = []
    for day in days:
        today = by_day.get(day, rest.iloc[0:0])
        cap_lo = day - pd.Timedelta(days=cfg.max_lookback_days)
        B = [k for k in eligible if cap_lo <= k < day][-cfg.baseline_days:]
        rec = {
            "day": day,
            "n_hr_samples": int(hr_counts.get(day, 0)),
            "n_rest_samples": int(len(today)),
            "valid": False,
            "reason": None,
            "D": np.nan,
            "z": np.nan,
            "n_baseline_valid_days": len(B),
            "n_baseline_D": 0,
        }
        if rec["n_hr_samples"] == 0:
            rec["reason"] = "source_missing_day"
            out.append(rec)
            continue
        if len(B) < cfg.baseline_days:
            rec["reason"] = "baseline_insufficient"
            out.append(rec)
            continue
        if len(today) < cfg.min_rest_samples:
            rec["reason"] = "invalid_too_few"
            out.append(rec)
            continue

        hist = pd.concat([by_day[k] for k in B], ignore_index=True)
        mu = float(hist["hr"].mean())
        Djs = []
        for k in B:
            g = by_day[k]
            if len(g) >= cfg.min_rest_samples:
                Djs.append(float(g["hr"].mean() - mu))
        rec["n_baseline_D"] = len(Djs)
        if len(Djs) < cfg.baseline_days:
            rec["reason"] = "baseline_insufficient"
            out.append(rec)
            continue

        rec["D"] = float(today["hr"].mean() - mu)
        arr = np.asarray(Djs, dtype=float)
        med = float(np.median(arr))
        mad = float(np.median(np.abs(arr - med)))
        rec["z"] = (
            rec["D"] - med
        ) / max(1.4826 * mad, cfg.scale_floor_bpm)
        rec["valid"] = True
        out.append(rec)

    res = pd.DataFrame(out)
    res["z_defined"] = res["z"].notna()
    return res


def _select_even_rank(mins: pd.DatetimeIndex, k: int) -> pd.DatetimeIndex:
    mins = pd.DatetimeIndex(sorted(pd.unique(mins)))
    n = len(mins)
    if k <= 0 or n == 0:
        return pd.DatetimeIndex([])
    if k >= n:
        return mins
    pos = np.floor((np.arange(k) + 0.5) * n / k).astype(int)
    pos = np.clip(pos, 0, n - 1)
    if len(np.unique(pos)) != k:
        raise RuntimeError("even-rank thinning produced duplicate positions")
    return mins[pos]


def equalize_m1_frames(frames, expected_days):
    out = {}
    qc = []
    for arm in ("S3r", "S6"):
        f = frames[arm].copy()
        f["timestamp"] = pd.to_datetime(f["timestamp"])
        f["minute"] = f["timestamp"].dt.floor("min")
        f["day"] = f["timestamp"].dt.normalize()
        out[arm] = f

    keep = {"S3r": [], "S6": []}
    for day in expected_days:
        per = {}
        for arm in ("S3r", "S6"):
            g = out[arm][out[arm]["day"] == day]
            per[arm] = pd.DatetimeIndex(sorted(g["minute"].unique()))
        k = min(len(per["S3r"]), len(per["S6"]))
        chosen = {
            arm: _select_even_rank(per[arm], k)
            for arm in ("S3r", "S6")
        }
        qc.append({
            "day": day,
            "S3r_original_minutes": len(per["S3r"]),
            "S6_original_minutes": len(per["S6"]),
            "matched_minutes": k,
        })
        for arm in ("S3r", "S6"):
            g = out[arm][out[arm]["day"] == day]
            if k:
                keep[arm].append(
                    g[g["minute"].isin(chosen[arm])][
                        ["timestamp", "hr", "steps"]
                    ].copy()
                )

    final = {}
    for arm in ("S3r", "S6"):
        final[arm] = (
            pd.concat(keep[arm], ignore_index=True).sort_values("timestamp")
            if keep[arm]
            else pd.DataFrame(columns=["timestamp", "hr", "steps"])
        )
    return final, pd.DataFrame(qc)


def dynamic_alert_days(res, onset, episode_onsets, budget, cfg):
    d = res.copy()
    d["day"] = pd.to_datetime(d["day"]).dt.normalize()
    d = d.sort_values("day").reset_index(drop=True)
    negmask = ~P.exclusion_mask(d["day"], episode_onsets)
    zdef = d["z_defined"].astype(bool)

    tau_by_day = {}
    for i, row in d.iterrows():
        if not bool(row["z_defined"]):
            continue
        hist = d.loc[(d.index < i) & zdef & negmask].copy()
        if len(hist) < P.C_FLOOR:
            continue
        tau_by_day[row["day"]] = float(
            P.calibrate_tau(hist, budget, cfg)["tau"]
        )

    flags = {}
    run = 0
    prev = None
    for _, row in d[d["z_defined"]].iterrows():
        day = row["day"]
        tau = tau_by_day.get(day, np.nan)
        if prev is not None and (day - prev).days > cfg.max_gap_days:
            run = 0
        if pd.isna(tau):
            run = 0
            flags[day] = False
        else:
            run = run + 1 if row["z"] >= tau else 0
            flags[day] = run >= cfg.persistence
        prev = day
    return d["day"].map(flags).fillna(False), tau_by_day


def rolling_outcome(res, onset, episode_onsets, arm, phase, pid, cfg):
    onset = pd.Timestamp(onset).normalize()
    initial = P.calibration_frame(res, onset, episode_onsets)
    out = {
        "phase": phase,
        "participant_id": pid,
        "arm": arm,
        "calibration_z_days": int(len(initial)),
        "calibration_floor_met": bool(len(initial) >= P.C_FLOOR),
        "presymptomatic_detected": pd.NA,
        "warning_days": np.nan,
    }
    if len(initial) < P.C_FLOOR:
        return out

    flags, _ = dynamic_alert_days(
        res, onset, episode_onsets, 2.0, cfg
    )
    d = res.copy()
    d["day"] = pd.to_datetime(d["day"]).dt.normalize()
    d["alert"] = flags.to_numpy()
    pe = d[
        d["day"].between(
            onset - pd.Timedelta(days=P.PRE_START),
            onset - pd.Timedelta(days=P.PRE_END),
        ) & d["z_defined"]
    ]
    if len(pe):
        al = pe[pe["alert"]].sort_values("day")
        det = not al.empty
        out["presymptomatic_detected"] = bool(det)
        if det:
            out["warning_days"] = int(
                (onset - pd.Timestamp(al.iloc[0]["day"])).days
            )
    return out


def filter_pair_df_by_ids(ph, ids):
    ids = ids[["phase", "participant_id"]].drop_duplicates()
    return ph.merge(ids, on=["phase", "participant_id"], how="inner")


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    cfg = P.TODZConfig()

    primary_o = pd.read_csv(PRIMARY_RUN / "arm_outcomes.csv")
    primary_ph = pd.read_csv(PRIMARY_RUN / "pair_hierarchy.csv")
    onsets = P.load_onsets()
    cohort = P.load_final_cohort_pairs()

    summaries = []

    # Derived sensitivity: Phase 2 only.
    summaries.append(
        summarize_pairs(
            primary_ph[primary_ph["phase"] == "phase2"],
            "phase2_only",
            100,
        )
    )

    # Derived sensitivity: common cohort across all primary arms.
    x = primary_o[primary_o["arm"].isin(ALL_PRIMARY_ARMS)].copy()
    x["floor"] = x["calibration_floor_met"].astype(bool)
    common = (
        x.groupby(["phase", "participant_id"])["floor"]
        .agg(["sum", "count"]).reset_index()
    )
    common = common[(common["sum"] == len(ALL_PRIMARY_ARMS)) &
                    (common["count"] == len(ALL_PRIMARY_ARMS))]
    summaries.append(
        summarize_pairs(
            filter_pair_df_by_ids(primary_ph, common),
            "common_cohort_all_primary_arms_Cfloor16",
            200,
        )
    )

    # Derived sensitivity: coarse calibration, pair-specific.
    coarse_parts = []
    for label, aa, bb in PRIMARY_PAIRS:
        a = primary_o[primary_o["arm"] == aa][
            ["phase", "participant_id", "calibration_z_days"]
        ].rename(columns={"calibration_z_days": "Ca"})
        b = primary_o[primary_o["arm"] == bb][
            ["phase", "participant_id", "calibration_z_days"]
        ].rename(columns={"calibration_z_days": "Cb"})
        ids = a.merge(b, on=["phase", "participant_id"])
        ids = ids[
            (30.44 / ids["Ca"] <= 1.0)
            & (30.44 / ids["Cb"] <= 1.0)
        ]
        q = primary_ph[primary_ph["comparison"] == label]
        q = filter_pair_df_by_ids(q, ids)
        tmp = summarize_pairs(q, "coarse_calibration_resolution_le_1pm", 300)
        coarse_parts.append(tmp[tmp["comparison"] == label])
    summaries.append(pd.concat(coarse_parts, ignore_index=True))

    # Derived sensitivity: exclude multi-episode participants.
    counts = (
        onsets[onsets["onset_date"].notna()]
        .groupby(["phase", "participant_id"])
        .size().rename("n_episode_rows").reset_index()
    )
    single = counts[counts["n_episode_rows"] <= 1][["phase", "participant_id"]]
    summaries.append(
        summarize_pairs(
            filter_pair_df_by_ids(primary_ph, single),
            "exclude_multiple_episode_rows",
            400,
        )
    )

    # Recomputed sensitivities.
    out_B1, out_B4, out_notod, out_roll, out_m1match = [], [], [], [], []
    m1match_qc = []

    for i, (phase, pid) in enumerate(cohort, 1):
        print(f"[{i:02d}/38] sensitivity preprocessing {phase}:{pid}", flush=True)
        info = P.participant_onset_info(onsets, phase, pid)
        onset = info["index_onset"]
        hr, steps, _ = P.load_participant_raw(phase, pid)
        frames, _, _, expected_days = P.schedule_participant(
            phase, pid, hr, steps, onset
        )

        stats = {}
        for arm in P.ALL_ARMS:
            stats[arm] = P.daily_statistics(
                frames[arm], cfg=cfg, expected_days=expected_days
            )
            out_B1.append(fixed_budget_outcome(
                stats[arm], onset, info["episode_onsets"],
                arm, phase, pid, 1.0, cfg
            ))
            out_B4.append(fixed_budget_outcome(
                stats[arm], onset, info["episode_onsets"],
                arm, phase, pid, 4.0, cfg
            ))
            out_roll.append(rolling_outcome(
                stats[arm], onset, info["episode_onsets"],
                arm, phase, pid, cfg
            ))

            nt = no_tod_daily_statistics(
                frames[arm], cfg, expected_days
            )
            out_notod.append(fixed_budget_outcome(
                nt, onset, info["episode_onsets"],
                arm, phase, pid, 2.0, cfg
            ))

        matched_frames, qcm = equalize_m1_frames(frames, expected_days)
        qcm.insert(0, "participant_id", pid)
        qcm.insert(0, "phase", phase)
        m1match_qc.append(qcm)
        for arm in ("S3r", "S6"):
            st = P.daily_statistics(
                matched_frames[arm], cfg=cfg, expected_days=expected_days
            )
            out_m1match.append(fixed_budget_outcome(
                st, onset, info["episode_onsets"],
                arm, phase, pid, 2.0, cfg
            ))

    scenarios = {
        "alert_budget_B1": pd.DataFrame(out_B1),
        "alert_budget_B4": pd.DataFrame(out_B4),
        "todz_without_time_of_day_normalisation": pd.DataFrame(out_notod),
        "rolling_tau_recalibration": pd.DataFrame(out_roll),
    }
    for k, odf in scenarios.items():
        odf.to_csv(OUTDIR / f"{k}_arm_outcomes.csv", index=False)
        pdf = pair_rows_from_outcomes(odf)
        pdf.to_csv(OUTDIR / f"{k}_pair_hierarchy.csv", index=False)
        summaries.append(summarize_pairs(pdf, k, 500 + len(summaries)*20))

    m1df = pd.DataFrame(out_m1match)
    m1df.to_csv(OUTDIR / "m1_realised_minute_matched_arm_outcomes.csv", index=False)
    m1pdf = pair_rows_from_outcomes(m1df)
    m1pdf = m1pdf[m1pdf["comparison"] == "M1"].copy()
    m1pdf.to_csv(OUTDIR / "m1_realised_minute_matched_pair_hierarchy.csv", index=False)
    ms = summarize_pairs(m1pdf, "m1_realised_minute_matched", 900)
    summaries.append(ms[ms["comparison"] == "M1"])
    pd.concat(m1match_qc, ignore_index=True).to_csv(
        OUTDIR / "m1_realised_minute_matching_qc.csv", index=False
    )

    final = pd.concat(summaries, ignore_index=True)
    final.to_csv(OUTDIR / "sensitivity_summary.csv", index=False)

    manifest = {
        "status": "SENSITIVITY_ONLY_POST_PRIMARY_OPERATIONALIZATION",
        "primary_run": str(PRIMARY_RUN.relative_to(ROOT)),
        "primary_commit": "83cc8d1",
        "bootstrap_resamples": BOOT_N,
        "bootstrap_seed_base": BOOT_SEED,
        "p_values_reported": False,
        "confirmatory_gate_reopened": False,
        "scenarios": sorted(final["scenario"].unique().tolist()),
        "notes": [
            "M1 realised-count conditioning equalizes delivered HR-observed minutes per participant-day.",
            "Discrete-time survival is not executed because the original preregistration under-specified its model/link/estimand.",
            "LOW/HIGH E3 physiological reruns are unnecessary because frozen E3 schedule masks are N=7,L=10 in all energy scenarios.",
        ],
    }
    (OUTDIR / "sensitivity_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )

    print("\n=== SENSITIVITY SUMMARY — ESTIMATION ONLY, NO P-VALUES ===")
    show = final[[
        "scenario", "comparison", "N", "W", "L", "T",
        "theta", "theta_bca95_lo", "theta_bca95_hi"
    ]].copy()
    print(show.to_string(index=False))
    print("\nSaved:", OUTDIR / "sensitivity_summary.csv")
    print("Confirmatory H1 result remains unchanged and gate remains closed.")


if __name__ == "__main__":
    main()
