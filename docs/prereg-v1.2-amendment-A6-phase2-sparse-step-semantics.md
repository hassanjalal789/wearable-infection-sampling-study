# Preregistration Amendment A6 — Phase-2 Sparse-Step Semantics Correction

**Date:** 2026-09-02  
**Status:** POST-GENERATION / PRE-SCIENTIFIC-OUTCOME-INSPECTION CORRECTION

## A6.1 Why this correction exists

The first frozen real-data execution at commit `d1d5265` completed and wrote the preserved audit-trail directory `results/primary_e3_run_d1d5265`.

Before any H1/M1/H2/H3 win/loss counts, detection rates, warning-time results, p-values, effect sizes, or hypothesis conclusions were inspected, a QC-only audit revealed implausible input-dependent behavior:

- only 5/38 participant-arms met the TOD-z calibration floor even for S1;
- 33/38 participants had zero z-defined presymptomatic days even for S1;
- S4, S3r and S6 had median zero scheduled event-window minutes;
- 28/38 participants exceeded the preregistered 40% M1-unavailability threshold.

An outcome-blind raw-input diagnostic showed that Phase 1 step data contained explicit zero-step minutes (median zero-step fraction 0.824), whereas the Phase 2 Fitbit step stream contained no explicit zero rows despite dense HR coverage.

The Stanford `AnomalyDetect` RHRAD implementation documents this source convention in `rhrad_online_24hr_alerts_v6.py`: the raw steps data “doesn't have zeroes” and zeroes need to be inferred from the HR datetime stamp. The script outer-merges HR and steps and fills missing values with zero before deriving rest.

Reference inspected 2026-09-02:
https://github.com/gireeshkbogu/AnomalyDetect/blob/master/scripts/rhrad_online_24hr_alerts_v6.py

This source is used here only to establish the public-data step encoding; the RHRAD detector itself is not substituted for TOD-z.

## A6.2 Corrected minute-level rule

The experiment's schedule/rest engine is minute-based. Therefore, for **Phase-2 Fitbit only**, `steps(minute)=0` is inferred only when:

1. at least one HR observation exists in that minute; and
2. there is no explicit Phase-2 step-file record for that minute.

Conservative precedence:

- any explicit recorded step value wins over zero inference;
- an explicit step row whose value is missing/NaN remains unknown;
- a minute containing neither HR nor a step record remains unknown;
- no zero is inferred outside HR-observed minutes;
- Phase 1 is unchanged because its source stream already records explicit zero-step minutes.

Inference occurs after minute binning. Thus a nonzero step record anywhere within a minute cannot be overwritten merely because HR timestamps occur at different seconds.

## A6.3 What remains frozen

This correction does **not** change the N=38 cohort, CENTRAL E3, N=7 × 10-minute bursts, schedule definitions, TOD-z, causal baseline, tau grid, +infinity fallback, alert budget, C_floor=16, presymptomatic endpoint, hierarchical paired outcome, fixed-sequence gatekeeping, or LOW/CENTRAL/HIGH energy scenarios.

No scientific outcome performance was used to select this correction.

## A6.4 Audit trail

`results/primary_e3_run_d1d5265` must remain unchanged. It is a superseded implementation-error run and is not eligible for confirmatory inference.

The corrected runner and regression tests must be committed before another real-data execution. The corrected run will use a new commit-versioned output directory and will not overwrite the superseded run.

## A6.5 Required regression tests

Before the corrected real run, tests must establish that:

- omitted Phase-2 step records at HR-observed minutes become zero;
- explicit positive/nonzero step records are preserved;
- explicit NaN step records remain unknown;
- minutes with neither HR nor steps remain unknown;
- Phase 1 semantics are unchanged;
- the existing full regression suite still passes.
