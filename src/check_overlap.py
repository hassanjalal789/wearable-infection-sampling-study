#!/usr/bin/env python3
"""
Phase-1 / Phase-2 participant-overlap investigation.  PATCH 7.

The prereg claims overlap is investigated using identifiers, date ranges AND
heart-rate series.  This file now actually performs the third check, and states
its precondition rather than assuming it.

PRECONDITION.  An HR-series comparison across releases is only meaningful if
both releases carry TRUE calendar dates.  The sample files shipped in
StanfordBioinformatics/wearable-infection carry dates in 2025-2026 for a study
that ended in July 2021, so date shifting in this data family is a demonstrated
possibility, not a hypothetical.  The script therefore checks each archive's
dates against the published study windows first.  If either fails, calendar
alignment is invalid, the series check is skipped, and the verdict is
UNDETERMINABLE -- never NO_EVIDENCE_OF_OVERLAP.

Verdicts: OVERLAP_FOUND | NO_EVIDENCE_OF_OVERLAP | UNDETERMINABLE
'No evidence' is never reported as 'no overlap'.
"""
from __future__ import annotations
import argparse, json
import numpy as np, pandas as pd

STUDY_WINDOWS = {                       # published enrolment / collection windows
    "phase1": ("2020-01-01", "2021-03-31"),
    "phase2": ("2020-11-27", "2021-07-20"),
}
MIN_COMMON_DAYS = 14
CORR_THRESHOLD = 0.95
MAD_THRESHOLD_BPM = 1.5          # applies ONLY to real bpm series (--hr-series)
COVERAGE_CORR_SUPPLEMENTARY = 0.98   # unitless; supplementary evidence only


def dates_plausible(inv: pd.DataFrame, phase: str) -> dict:
    lo, hi = (pd.Timestamp(x) for x in STUDY_WINDOWS[phase])
    d = pd.to_datetime(inv.loc[inv.phase == phase, "date"])
    if d.empty:
        return dict(phase=phase, plausible=False, reason="no dates")
    frac = float(((d >= lo) & (d <= hi)).mean())
    return dict(phase=phase, plausible=frac >= 0.90, frac_in_window=frac,
                observed_range=[str(d.min().date()), str(d.max().date())],
                published_window=[str(lo.date()), str(hi.date())])


def hr_series(path: str) -> dict:
    """Per-participant daily nighttime median resting HR, in BPM.

    Expected columns: phase, participant_id, date, nightly_median_rhr_bpm.
    This is the ONLY series the bpm thresholds may be applied to.
    """
    df = pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)
    need = {"phase", "participant_id", "date", "nightly_median_rhr_bpm"}
    missing = need - set(df.columns)
    if missing:
        raise RuntimeError(f"{path} is missing columns: {sorted(missing)}")
    out = {}
    for (ph, pid), g in df.groupby(["phase", "participant_id"]):
        s = g.set_index(pd.to_datetime(g.date))["nightly_median_rhr_bpm"].astype(float)
        out[(ph, pid)] = s[~s.index.duplicated()].sort_index()
    return out


def coverage_series(inv: pd.DataFrame) -> dict:
    """Per-participant daily NIGHT OBSERVED MINUTES.  Units are MINUTES.

    PATCH 3: this is a coverage series, not a heart-rate series.  It is used only
    as SUPPLEMENTARY evidence, with a unitless correlation threshold, and is never
    described as an HR-series identity test.  The previous code compared these
    minute counts against a 1.5-BPM threshold, which was dimensionally invalid.
    """
    out = {}
    for (ph, pid), g in inv.groupby(["phase", "participant_id"]):
        s = g.set_index(pd.to_datetime(g.date))["night_observed_minutes"].astype(float)
        out[(ph, pid)] = s[~s.index.duplicated()].sort_index()
    return out


def compare_hr(a: pd.Series, b: pd.Series) -> dict | None:
    """Real bpm comparison.  MAD threshold is in BPM and applies here only."""
    common = a.index.intersection(b.index)
    if len(common) < MIN_COMMON_DAYS:
        return None
    x, y = a.loc[common].to_numpy(), b.loc[common].to_numpy()
    corr = float("nan") if x.std() == 0 or y.std() == 0 else float(np.corrcoef(x, y)[0, 1])
    mad_bpm = float(np.mean(np.abs(x - y)))
    exact = float(np.mean(np.isclose(x, y)))
    return dict(n_common_days=int(len(common)), corr=corr, mad_bpm=mad_bpm,
                exact_match_frac=exact,
                flag=bool((not np.isnan(corr) and corr >= CORR_THRESHOLD
                           and mad_bpm <= MAD_THRESHOLD_BPM) or exact >= 0.98))


def compare_coverage(a: pd.Series, b: pd.Series) -> dict | None:
    """Supplementary only.  Unitless correlation; no bpm threshold is applied."""
    common = a.index.intersection(b.index)
    if len(common) < MIN_COMMON_DAYS:
        return None
    x, y = a.loc[common].to_numpy(), b.loc[common].to_numpy()
    corr = float("nan") if x.std() == 0 or y.std() == 0 else float(np.corrcoef(x, y)[0, 1])
    exact = float(np.mean(x == y))
    return dict(n_common_days=int(len(common)), coverage_corr=corr,
                coverage_exact_frac=exact, units="minutes",
                supplementary_flag=bool((not np.isnan(corr)
                                         and corr >= COVERAGE_CORR_SUPPLEMENTARY)
                                        or exact >= 0.98))


def investigate(inv: pd.DataFrame, hr_path: str | None = None) -> dict:
    plaus = {p: dates_plausible(inv, p) for p in ("phase1", "phase2")}
    i1 = set(inv.loc[inv.phase == "phase1", "participant_id"])
    i2 = set(inv.loc[inv.phase == "phase2", "participant_id"])
    shared = sorted(i1 & i2)

    result = dict(shared_identifiers=shared[:50], n_shared=len(shared),
                  date_plausibility=plaus, hr_series_check_performed=False,
                  supplementary_coverage_check_performed=False,
                  flagged_pairs=[], supplementary_flagged_pairs=[],
                  n_pairs_compared=0)

    if shared:
        result.update(verdict="OVERLAP_FOUND", basis="shared participant identifiers")
        return result

    if not (plaus["phase1"]["plausible"] and plaus["phase2"]["plausible"]):
        result.update(verdict="UNDETERMINABLE", basis=(
            "calendar dates in at least one archive fall outside the published study "
            "window, so cross-release date alignment is invalid. No series comparison "
            "of any kind was performed. See date_plausibility."))
        return result

    if hr_path is None:
        # PATCH 3: no pseudo-HR comparison. Coverage similarity is reported as
        # supplementary evidence only and cannot decide the verdict.
        cov = coverage_series(inv)
        c1 = {k: v for k, v in cov.items() if k[0] == "phase1"}
        c2 = {k: v for k, v in cov.items() if k[0] == "phase2"}
        sup, n = [], 0
        for k1, s1 in c1.items():
            for k2, s2 in c2.items():
                c = compare_coverage(s1, s2)
                if c is None:
                    continue
                n += 1
                if c["supplementary_flag"]:
                    sup.append(dict(phase1=k1[1], phase2=k2[1], **c))
        result.update(supplementary_coverage_check_performed=True, n_pairs_compared=n,
                      supplementary_flagged_pairs=sup[:50], n_supplementary_flagged=len(sup),
                      verdict="UNDETERMINABLE", basis=(
                          "no HR series was supplied (--hr-series), so no heart-rate "
                          "identity test was performed. Coverage similarity is reported "
                          "as supplementary evidence in minutes and is NOT an HR-series "
                          "identity test; it cannot establish or exclude overlap."))
        return result

    series = hr_series(hr_path)
    p1 = {k: v for k, v in series.items() if k[0] == "phase1"}
    p2 = {k: v for k, v in series.items() if k[0] == "phase2"}
    flagged, n = [], 0
    for k1, s1 in p1.items():
        for k2, s2 in p2.items():
            c = compare_hr(s1, s2)
            if c is None:
                continue
            n += 1
            if c["flag"]:
                flagged.append(dict(phase1=k1[1], phase2=k2[1], **c))
    result.update(hr_series_check_performed=True, n_pairs_compared=n,
                  flagged_pairs=flagged[:50], n_flagged=len(flagged),
                  hr_series_source=hr_path)
    if flagged:
        result.update(verdict="OVERLAP_FOUND", basis=(
            f"{len(flagged)} participant pairs matched on nightly median resting HR "
            f"(corr >= {CORR_THRESHOLD} and mean absolute difference <= "
            f"{MAD_THRESHOLD_BPM} bpm, or >= 98% exact daily agreement) over >= "
            f"{MIN_COMMON_DAYS} common days"))
    else:
        result.update(verdict="NO_EVIDENCE_OF_OVERLAP", basis=(
            "identifiers disjoint and no participant pair matched on nightly median "
            "resting HR. This is NOT a finding of disjointness: de-identified releases "
            "may re-randomise identifiers, and a re-enrolled participant contributing "
            "different calendar periods would not match."))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inventories", nargs="+")
    ap.add_argument("--hr-series", default=None,
                    help="parquet/csv of phase, participant_id, date, "
                         "nightly_median_rhr_bpm. Required for a real HR identity test.")
    a = ap.parse_args()
    inv = pd.concat([pd.read_parquet(p) for p in a.inventories], ignore_index=True)
    out = investigate(inv, a.hr_series)
    out["note"] = ("The Phase-2-only sensitivity analysis runs regardless of this "
                   "verdict. The verdict changes what Methods says, not what is computed.")
    json.dump(out, open("results/overlap_investigation.json", "w"), indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
