# Preregistration Amendment A5 — Primary E3 Runner Operationalization

**Date:** 2026-09-02  
**Status:** PROSPECTIVE — must be committed before any real S1–S6 schedule-performance outcome is generated.

## A5.1 Purpose

This amendment freezes implementation details needed to convert the public raw archives into the already-preregistered schedule and TOD-z analysis. It does not change the hypotheses, cohort, energy budget, detector family, alert budget, or primary endpoint.

No real schedule-performance outcome had been inspected when these rules were written.

## A5.2 Primary execution cell

The confirmatory execution cell is:

- modelled-energy scenario: CENTRAL;
- budget: E3 = 5% of modelled continuous S1 schedule-attributable energy;
- acquisition length: 10 minutes;
- burst count: N = 7 for S2, S3, S4, S5, S3r and S6.

The pre-outcome energy audit established that E3 is feasible within ±5% and resolves to N=7 in LOW, CENTRAL and HIGH parameterizations. Therefore the actual schedule masks are identical across those three E3 energy scenarios; energy-model robustness is assessed from the frozen feasibility audit plus the common N=7 outcome analysis.

## A5.3 Raw source normalization

The two public ZIP archives are read directly without full extraction.

For each final-cohort participant:

- all matching HR members are combined;
- HR timestamps are parsed using the existing frozen timestamp parser;
- HR records sharing the exact same timestamp are averaged deterministically;
- step records are mapped to minute bins;
- multiple recorded step values within one minute are summed;
- missing step minutes remain missing and are not classified as rest;
- schedules operate on local timestamp minute bins;
- all native HR observations whose minute is retained by a schedule are passed to TOD-z.

This preprocessing is deterministic and does not depend on infection-detection outcomes.

## A5.4 Calendar skeleton and missingness

For each participant, the analysis calendar runs from the earliest available HR/step day through the index onset day.

A scheduled day with zero delivered HR remains present as an expected day and is unevaluable; it is not silently removed.

Partially observed presymptomatic windows remain in the analysis with their unavailable days preserved.

If an arm has zero z-defined days across the entire onset−21 through onset−1 presymptomatic window, that participant-arm outcome is marked **unevaluable**, not forced to a non-detection.

## A5.5 Threshold calibration

For each participant and arm:

- use all historical negative z-defined days available through **onset−28 inclusive**;
- exclude the union of every [episode onset−21, episode onset+21] infection window;
- apply the frozen TOD-z threshold grid 1.0–6.0 in 0.1 increments, with +∞ fallback;
- select the smallest admissible threshold satisfying ≤2 alert-days/person-month;
- freeze the threshold for evaluation.

The pair-specific calibration floor remains:

`C_floor = 16 z-defined calibration days`

A primary pair is not formally compared for a participant unless both arms satisfy C_floor.

## A5.6 Presymptomatic outcome

Primary presymptomatic window:

`[onset−21, onset−1]`

A participant-arm is detected if at least one alert occurs on a z-defined day in that interval.

Warning time is the number of days from the **earliest** such alert to onset.

For a non-detection, warning time remains missing/NA and is never imputed as zero.

Onset day (day 0) is evaluated separately as a descriptive at-or-before-onset endpoint.

## A5.7 Paired hierarchical outcome

For an evaluable pair A versus B:

1. A wins if A detects presymptomatically and B does not.
2. B wins if B detects presymptomatically and A does not.
3. If both detect, the arm with longer warning wins.
4. If neither detects, or both warning times are equal, the pair is a tie.
5. If calibration or the entire presymptomatic outcome window is unevaluable for either arm, the pair is marked unavailable rather than forcing a win/loss/tie.

The previously preregistered sign-test / θ analysis is unchanged.

## A5.8 M1 availability and sample-count sensitivity

For S3r versus S6, daily M1 feasibility is retained explicitly.

For each presymptomatic participant-day the runner records:

- whether the matched M1 pair was available;
- scheduled minutes;
- delivered minutes.

The prespecified >40% M1-unavailability rule and the realized-sample-count sensitivity will be evaluated from these saved records. These diagnostics may not be used to tune schedule placement or detector thresholds.

## A5.9 Execution guard

The real-data runner must:

- be committed to Git before execution;
- require a clean working tree;
- verify that energy-freeze commit `4023717` is an ancestor;
- verify N=38 frozen cohort;
- verify E3 N=7 feasibility in all LOW/CENTRAL/HIGH scenarios;
- write results to a commit-versioned output directory;
- refuse to overwrite an existing real-run directory.

The generation command will print participant progress and file locations only, not scientific detection/warning summaries. Outcome values will be inspected deliberately after the one-shot run completes.
