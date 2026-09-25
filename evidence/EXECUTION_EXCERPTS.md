# Execution excerpts

*Publication-stage record, written on 20 September 2026. It reproduces the parts of the preserved execution records that can be published as they stand: run configuration, the frozen selection rules, and aggregate participant counts. The records are quoted exactly; the surrounding explanation is new writing. Result tables, figures and per-participant files are not included here — they are listed in the [publication manifest](PUBLICATION_MANIFEST.csv) with their current status.*

## What is eligible, and why

Every excerpt below is either a configuration value, a frozen decision rule, or a count over participants. None of it is a schedule-performance outcome, and none identifies a participant. Per-participant records exist in the research materials and are not reproduced here.

The superseded run's configuration **is** published, because the whole point of publishing it is to let a reader see that the correction changed the step-encoding rule and nothing else. Its outputs are not published and are not mixed into any result in this repository.

## Run manifests

Both executions wrote a manifest recording the configuration under which they ran.

### Superseded run

```json
{
  "status": "REAL_PRIMARY_E3_OUTCOMES_GENERATED",
  "scenario": "CENTRAL",
  "budget": "E3",
  "N_budget": 7,
  "burst_minutes": 10,
  "alert_budget_per_person_month": 2.0,
  "C_floor": 16,
  "calibration_stop": "through onset-28 inclusive",
  "presymptomatic_window": "onset-21 through onset-1 inclusive",
  "n_frozen_cohort": 38,
  "terminal_policy": "No detection/warning summary printed during generation."
}
```

This run is superseded. Amendment [A6](../docs/prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md) §A6.4 requires its directory to remain unchanged and states that it is not eligible for confirmatory inference.

### Corrected run

```json
{
  "status": "REAL_PRIMARY_E3_OUTCOMES_GENERATED",
  "scenario": "CENTRAL",
  "budget": "E3",
  "N_budget": 7,
  "burst_minutes": 10,
  "alert_budget_per_person_month": 2.0,
  "C_floor": 16,
  "phase2_step_semantics": "At minute resolution, infer steps=0 only for Phase-2 Fitbit HR-observed minutes with no explicit step-file record; explicit step records win; minutes with neither HR nor steps remain unknown.",
  "calibration_stop": "through onset-28 inclusive",
  "presymptomatic_window": "onset-21 through onset-1 inclusive",
  "n_frozen_cohort": 38,
  "terminal_policy": "No detection/warning summary printed during generation."
}
```

This is the authoritative run. The only field that differs between the two manifests is `phase2_step_semantics`, which the corrected run records explicitly and the superseded run does not carry at all.

Both manifests also record the same frozen energy commit as the ancestor the execution guard required, and both record the same two input archives by relative path and byte size. The guard conditions themselves are set out in [A5](../docs/prereg-v1.2-amendment-A5-runner-operationalization.md) §A5.9: the runner had to be committed before execution, the working tree clean, the energy-freeze commit an ancestor, the frozen cohort verified at 38, E3 feasibility verified at N = 7 across all three energy scenarios, output written to a commit-versioned directory, and any existing real-run directory left untouched rather than overwritten.

## Frozen calibration-minimum rule

The `C_min` decision was frozen before any outcome inspection and recorded in full:

```json
{
  "n_participants": 49,
  "chosen_C_min": 28,
  "retention_at_choice": 0.7755102040816326,
  "shares": { "28": 0.7755102040816326, "42": 0.6326530612244898,
              "61": 0.3469387755102041, "91": 0.30612244897959184 },
  "floor": 0.8,
  "median": 46.0,
  "iqr": [34.0, 112.0],
  "minimum": 0.0,
  "maximum": 407.0,
  "note": "availability-only rule; frozen before any outcome inspection; no candidate minimum met the 0.80 retention floor, so the prespecified fallback C_min=28 was invoked",
  "fallback_invoked": true,
  "retention_floor_met": false
}
```

The record states plainly that the retention floor was not met and that the fallback was invoked. That is a designed-for outcome of the rule rather than a deviation from it: the rule names 28 as the default when no candidate qualifies. It is reported here because a reader should not have to infer from a single retained number that the preferred condition failed.

## Participant flow

Counts only, by phase:

| Stage | Phase 1 | Phase 2 |
|---|---|---|
| Infection-positive | 32 | 84 |
| Fitbit with recorded device provenance | 32 | 49 |
| Device unknown or conflicting | 0 | 0 |
| Of which symptomatic | 30 | 37 |
| With an onset date | 30 | 37 |
| Sufficient baseline | 18 | 31 |
| Pre-calibration eligible | 18 | 31 |

Pre-calibration eligible across both phases: **49**. Applying `C_p^src ≥ C_min = 28` gives the source-defined cohort of **38**. Of those, **30** had an evaluable pair in every primary comparison; the step from 38 to 30 is explained in [results and limitations](../docs/RESULTS_AND_LIMITATIONS.md).

No participant was dropped for an unknown or conflicting device, because the device map resolved every participant in both phases. The cohort builder imports nothing from the schedule or detector code, so no schedule-performance quantity could reach the selection.

## Quality-control audit that triggered the correction

Amendment A6 §A6.1 records what the outcome-blind audit found before any scientific outcome was inspected:

- only 5 of 38 participant-arms met the time-of-day-z calibration floor even for the continuous reference arm;
- 33 of 38 participants had zero z-defined presymptomatic days even for that arm;
- three of the burst arms had a median of zero scheduled event-window minutes;
- 28 of 38 participants exceeded the preregistered 40% unavailability threshold for the matched comparison.

An outcome-blind diagnostic of the raw inputs then showed that the Phase 1 step stream contained explicit zero-step minutes, with a median zero-step fraction of 0.824, while the Phase 2 stream contained no explicit zero rows despite dense heart-rate coverage. A6 cites the upstream Stanford implementation as documenting that source convention, and uses it only to establish the step encoding — the upstream detector is not substituted for the study's own.

These are diagnostic counts, not results. They describe how the input data was encoded, and they were what justified the correction.

## What is not included here

- Win/loss/tie counts, detection rates, warning times, effect sizes, intervals and p-values — these belong to [results and limitations](../docs/RESULTS_AND_LIMITATIONS.md), which reports the corrected run only.
- Any output of the superseded run.
- Per-participant records of any kind.
- Result tables, digests and figures, which are published separately under [`results/`](../results/README.md).
