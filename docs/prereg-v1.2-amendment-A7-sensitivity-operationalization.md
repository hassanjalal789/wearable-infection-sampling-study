# Analysis Amendment A7 — Sensitivity Operationalization After Primary Outcome Reveal

**Date:** 2026-09-04  
**Status:** POST-PRIMARY-OUTCOME OPERATIONALIZATION; sensitivity-only, never confirmatory.

## A7.1 Reason for this amendment

The confirmatory E3 analysis was completed and revealed before this amendment. H1 did not reject, so the preregistered fixed-sequence gate closed. This amendment therefore cannot alter, reopen, or reinterpret the confirmatory gate.

Several sensitivity analyses were prespecified, but some implementation details were not fully operationalized. In particular, A3.9 required a “realised-sample-count-conditioned” M1 analysis without specifying the exact deterministic conditioning algorithm. This amendment records that implementation transparently **after** the primary result was known.

Consistent with prereg-v1.1 §2.2, sensitivity analyses are estimation-only: point estimates and 95% confidence intervals are reported; **no sensitivity p-value is used for confirmatory inference**.

## A7.2 Sensitivities executed in the core runner

The core sensitivity runner executes:

1. **Phase-2-only cohort** on the corrected E3 primary outcomes.
2. **Common-cohort restriction**: participants meeting `C_floor=16` in S2, S3, S4, S5, S3r and S6.
3. **Coarse-calibration restriction**: for each pair, both arms must satisfy `30.44 / C_p <= B/2` at the primary `B=2`; equivalently integer `C_p >= 31`.
4. **Multiple-episode exclusion** using all available onset rows; if no final-cohort participant has >1 onset row, the sensitivity is reported as vacuous.
5. **Alert-budget sensitivities** at B=1 and B=4 alert-days/person-month, using the same schedules, TOD-z, calibration history, endpoint and `C_floor=16`.
6. **TOD-z without time-of-day normalization** as specified below.
7. **Rolling threshold recalibration** as specified below.
8. **M1 realised-sample-count-conditioned analysis** as specified below.

All sensitivity summaries use the same hierarchical paired effect:
`theta = (W + 0.5*T) / N`,
with a 95% BCa participant bootstrap (10,000 resamples). No sensitivity p-value is reported.

## A7.3 Realised-sample-count-conditioned M1 operationalization

The schedule engine's delivered-sample accounting is minute based. Therefore the conditioning variable is **delivered HR-observed minutes**, not native sub-minute HR row count.

For every participant-day, after the preregistered S3r and S6 masks have been applied:

1. Let `K3` and `K6` be the number of unique delivered HR minutes in S3r and S6.
2. Set `K = min(K3, K6)`.
3. If an arm has more than `K` delivered minutes, deterministically thin its ordered delivered-minute set to exactly `K` minutes using evenly spaced rank positions across that arm's own delivered minutes.
4. Retain all native HR rows falling inside the selected minutes.
5. Apply this rule symmetrically to both arms on **all days**, including calibration history and the event window.
6. If `K=0`, both arms deliver zero minutes that day.
7. Recompute TOD-z, calibration thresholds and outcomes from these count-matched streams.

The thinning rule does not move observations between times of day and does not choose minutes using HR values or outcomes. It only removes excess delivered minutes to equalize realised minute counts.

This is a post-primary operationalization of the previously required but underspecified sensitivity and must be labelled as such in the paper.

## A7.4 TOD-z without time-of-day normalization

The same causal single-pass 28-valid-day / 90-calendar-day baseline logic is retained, but the hour-specific mean `mu(p,h)` is removed.

For each prediction day d:

1. select the same most recent 28 baseline-eligible historical days within the 90-day cap;
2. estimate one participant-level resting-HR mean `mu(p)` from all retained rest samples on those days;
3. compute each historical `D_j` as that day's mean resting HR minus `mu(p)`;
4. compute current `D_d` analogously;
5. calculate z using the same median/MAD rule and 1 bpm scale floor.

All missingness, minimum-rest-sample and causal-history rules otherwise remain unchanged.

## A7.5 Rolling recalibration operationalization

The primary z series is unchanged. Instead of freezing tau after the initial calibration:

- for each z-defined day d, tau(d) is recalibrated from all z-defined negative days strictly before d and outside the union of all infection exclusion windows;
- the same tau grid and +infinity fallback are used;
- a participant-arm must still satisfy the original `C_floor=16` on the initial through-onset−28 calibration frame to enter the sensitivity;
- the persistence state machine compares each day to its own causal tau(d).

This sensitivity cannot add outcome-window days to the negative calibration history because those days lie inside the infection exclusion window.

## A7.6 Items not treated as core executable sensitivities

- **Detection-proportion-only endpoint:** not triggered because final N=38 >=15.
- **Budget-infeasible exclusion:** vacuous under the amended +infinity fallback; the corrected primary run had zero saturated arms.
- **Option-A / delivered-energy hardware accounting:** superseded as inferential hardware sensitivities by A4's no-hardware modelled-energy design. Delivered minutes remain descriptive.
- **LOW/HIGH E3 energy scenarios:** E3 resolves to the same N=7, L=10 schedule masks in all three scenarios, so physiological outcomes are identical; robustness is represented by the frozen energy-feasibility audit.
- **Sleep-record-defined nocturnal window** and **synthetic sensor-degradation ablation:** exploratory appendix analyses, not needed to adjudicate the primary null.
- **Discrete-time survival:** the original preregistration did not specify a reproducible link function, covariate parameterization or estimand. It is therefore not silently invented here after outcome reveal. If added later, it will be explicitly labelled post hoc/exploratory.

## A7.7 Interpretation rule

Sensitivity results may support statements such as “the primary null was robust/not robust to X.” They may not convert M1, H2 or H3 into confirmatory findings, and they may not override the failed H1 gate.
