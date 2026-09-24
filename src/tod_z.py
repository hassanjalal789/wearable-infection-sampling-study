#!/usr/bin/env python3
"""
TOD-z: causal time-of-day-normalised rest-heart-rate z-score.
PREREGISTRATION ARTEFACT.  Implements prereg-v1.1 sec.4 and sec.6 (all fourteen
edge cases) and sec.5 threshold calibration as amended by v1.2.

Every window is STRICTLY causal: a statistic for day d reads only timestamps
< start-of-day d.  `trace_reads=True` records the maximum timestamp consulted
for each output day so tests/test_causality.py can assert this mechanically
rather than by inspection.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
import pandas as pd

DAYS_PER_MONTH = 30.44


@dataclass
class TODZConfig:
    """PATCH 7 -- resolved baseline definition.

    The baseline is THE MOST RECENT 28 VALID DAYS, not "valid days falling inside
    the trailing 28 calendar days".  The previous implementation required all 28
    preceding calendar days to be valid, which is close to unachievable at low
    duty cycles and would have made the comparison partly a test of which
    schedule happens to produce contiguous valid days.  A lookback cap keeps the
    baseline physiologically current.
    """
    baseline_days: int = 28          # Mishra 2020: 28 valid days
    min_rest_samples: int = 5        # declared choice (prereg sec.4)
    min_hour_obs: int = 7            # edge case 6.3
    persistence: int = 2             # NightSignal FSM
    max_gap_days: int = 3            # edge case 6.6
    scale_floor_bpm: float = 1.0     # edge case 6.1
    max_lookback_days: int = 90      # PATCH 7: the 28 valid days must fall
                                     # within this many calendar days
    tau_grid: np.ndarray = field(
        default_factory=lambda: np.round(np.arange(1.0, 6.0001, 0.1), 4))


def _rest_mask(steps: pd.Series) -> np.ndarray:
    """Edge case 6.7: a minute with a missing step record is NOT rest."""
    return (steps.fillna(1.0).to_numpy() == 0.0)


def baseline_eligible(day_rest: pd.DataFrame, cfg) -> bool:
    """History-free eligibility: does this day carry enough retained rest samples?

    Deliberately independent of any baseline, so selecting the baseline set cannot
    depend on an earlier baseline.  That independence is what removes the nested
    burn-in.
    """
    return len(day_rest) >= cfg.min_rest_samples


def daily_statistics(df: pd.DataFrame, cfg: TODZConfig = TODZConfig(),
                     trace_reads: bool = False, expected_days=None) -> pd.DataFrame:
    """df columns: timestamp (datetime64), hr (float), steps (float, NaN allowed).

    SINGLE-PASS BASELINE (A3.1 as corrected).  For prediction day d:

      1. B := the most recent `baseline_days` baseline-eligible days strictly
         before d and no older than `max_lookback_days` calendar days.
      2. mu(p,h) is estimated from the retained rest samples on THOSE days.
      3. one historical D_j is computed for each day in B, using that same mu.
      4. the location and scale are the median and MAD of those D_j.
      5. D_d for the current day uses the same mu.
      6. z_d = (D_d - median(D_j)) / max(1.4826 * MAD(D_j), scale_floor_bpm)

    Consequences, each asserted by tests:
      * exactly ONE 28-valid-day baseline is required, so the first z-defined day
        follows 28 baseline-eligible historical days rather than ~56;
      * every sample contributing to z_d, directly or indirectly, lies inside
        [d - max_lookback_days, d);
      * the rule is identical for sparse and dense schedules;
      * no future timestamp is read.

    The superseded implementation nested two 28-day requirements -- D became valid
    only after 28 historical days, and z only after 28 historical D values -- which
    produced a ~56-day effective burn-in and let information reach z_d from before
    the declared 90-day cap, because those historical D values carried baselines of
    their own.
    """
    # PATCH: build the calendar skeleton BEFORE dropping missing HR, so a
    # participant-day with zero delivered samples appears as an UNEVALUABLE row
    # rather than vanishing from the output and from invalid-day accounting.
    all_rows = df.dropna(subset=["timestamp"]).copy()
    all_rows["timestamp"] = pd.to_datetime(all_rows["timestamp"])
    all_rows["day"] = all_rows["timestamp"].dt.normalize()

    skeleton = set(all_rows["day"].unique())
    if expected_days is not None:
        skeleton |= set(pd.to_datetime(pd.Index(expected_days)).normalize())
    days = pd.DatetimeIndex(sorted(skeleton))

    d = all_rows.dropna(subset=["hr"]).copy()
    d["hour"] = d["timestamp"].dt.hour
    d["is_rest"] = _rest_mask(d["steps"])
    hr_counts = d.groupby("day").size().to_dict()          # delivered HR per day

    rest = d[d.is_rest]
    by_day = {k: g for k, g in rest.groupby("day")}
    eligible_days = [k for k in days if baseline_eligible(by_day.get(k, rest.iloc[0:0]), cfg)]

    out = []
    for day in days:
        today = by_day.get(day, rest.iloc[0:0])
        cap_lo = day - pd.Timedelta(days=cfg.max_lookback_days)
        B = [k for k in eligible_days if cap_lo <= k < day][-cfg.baseline_days:]

        rec = dict(day=day, n_hr_samples=int(hr_counts.get(day, 0)),
                   n_rest_samples=int(len(today)), valid=False, reason=None,
                   D=np.nan, z=np.nan, n_baseline_valid_days=len(B), n_baseline_D=0,
                   baseline_oldest=(B[0] if B else pd.NaT))
        if trace_reads:
            hist_ts = pd.concat([by_day[k]["timestamp"] for k in B]) if B else pd.Series(dtype="datetime64[ns]")
            rec["max_baseline_timestamp_read"] = hist_ts.max() if len(hist_ts) else pd.NaT
            rec["min_baseline_timestamp_read"] = hist_ts.min() if len(hist_ts) else pd.NaT
            rec["max_day_timestamp_read"] = today["timestamp"].max() if len(today) else pd.NaT

        # zero delivered HR: unevaluable, NOT a non-detection. Checked before the
        # baseline gate so the reason names the actual cause.
        if rec["n_hr_samples"] == 0:                                # 6.8
            rec["reason"] = "source_missing_day"; out.append(rec); continue
        if len(B) < cfg.baseline_days:                              # 6.2 / 6.4
            rec["reason"] = "baseline_insufficient"; out.append(rec); continue
        if len(today) == 0:                                         # 6.5
            rec["reason"] = "invalid_no_rest"; out.append(rec); continue

        hist = pd.concat([by_day[k] for k in B])
        mu = hist.groupby("hour")["hr"].agg(["mean", "count"])      # step 2
        good = mu[mu["count"] >= cfg.min_hour_obs]["mean"]          # 6.3
        if good.empty:
            rec["reason"] = "no_hour_baseline"; out.append(rec); continue

        Djs = []                                                    # step 3
        for k in B:
            g = by_day[k]
            g = g[g.hour.isin(good.index)]
            if len(g) >= cfg.min_rest_samples:
                Djs.append(float((g["hr"].to_numpy() - good.loc[g.hour].to_numpy()).mean()))
        rec["n_baseline_D"] = len(Djs)
        if len(Djs) < cfg.baseline_days:
            rec["reason"] = "baseline_insufficient"; out.append(rec); continue

        keep = today[today.hour.isin(good.index)]                   # step 5
        if len(keep) < cfg.min_rest_samples:                        # 6.6
            rec["n_rest_samples"] = int(len(keep))
            rec["reason"] = "invalid_too_few" if len(keep) else "invalid_no_rest"
            out.append(rec); continue

        rec["n_rest_samples"] = int(len(keep))
        rec["D"] = float((keep["hr"].to_numpy() - good.loc[keep.hour].to_numpy()).mean())
        rec["valid"] = True

        arr = np.asarray(Djs, dtype=float)                          # steps 4 and 6
        med = float(np.median(arr))
        mad = float(np.median(np.abs(arr - med)))
        rec["z"] = (rec["D"] - med) / max(1.4826 * mad, cfg.scale_floor_bpm)
        out.append(rec)

    res = pd.DataFrame(out)
    res["z_defined"] = res.z.notna()
    return res


def alert_days(res: pd.DataFrame, tau: float, cfg: TODZConfig = TODZConfig()) -> pd.Series:
    """Alert when z >= tau on `persistence` consecutive VALID days no more than
    `max_gap_days` calendar days apart (edge case 6.6)."""
    v = res[res.z_defined].sort_values("day")
    flags, run, prev = {}, 0, None
    for _, r in v.iterrows():
        if prev is not None and (r.day - prev).days > cfg.max_gap_days:
            run = 0
        run = run + 1 if r.z >= tau else 0
        flags[r.day] = run >= cfg.persistence
        prev = r.day
    return res.day.map(flags).fillna(False)


def achieved_rate(res: pd.DataFrame, tau: float, cfg: TODZConfig = TODZConfig()) -> float:
    """A(tau) in alert-days per person-month over the calibration frame."""
    n = int(res.z_defined.sum())
    if n == 0:
        return float("nan")
    return float(alert_days(res, tau, cfg).sum()) / (n / DAYS_PER_MONTH)


def calibrate_tau(res_cal: pd.DataFrame, budget: float,
                  cfg: TODZConfig = TODZConfig()) -> dict:
    """prereg sec.5(c)-(f).  A(tau) is monotone non-increasing in tau, so
    {tau : A(tau) <= B} is an upper set and its minimum is well defined.

    PATCH 2 -- the grid is extended by a terminal tau = +inf, which produces zero
    alerts and is therefore ALWAYS admissible.  The previous behaviour (clamp to
    6.0, flag, retain) could leave a participant whose realised calibration alert
    rate exceeded the budget inside a primary comparison, violating the
    equal-alert-budget condition the whole design rests on.  Every participant
    now stays paired AND satisfies the budget.
    """
    rates = [(float(t), achieved_rate(res_cal, float(t), cfg)) for t in cfg.tau_grid]
    admissible = [t for t, a in rates if not np.isnan(a) and a <= budget]
    C = int(res_cal.z_defined.sum())
    if admissible:
        tau, finite, saturated = min(admissible), True, False
    else:
        tau, finite, saturated = float("inf"), False, True
    achieved = 0.0 if not finite else achieved_rate(res_cal, tau, cfg)
    assert np.isnan(achieved) or achieved <= budget + 1e-12, "budget violated"
    return dict(tau=tau, finite_threshold=finite, calibration_saturated=saturated,
                budget_infeasible=saturated,      # retained alias for v1.1 readers
                calibration_days=C,
                resolution_per_month=(DAYS_PER_MONTH / C if C else float("nan")),
                achieved_rate=achieved,
                coarse_calibration=bool(C and DAYS_PER_MONTH / C > budget / 2))
