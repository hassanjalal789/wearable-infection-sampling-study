# Research timeline

*Publication-stage guide, written on 20 September 2026 for research I designed and conducted. It sets out the order in which I developed the design, fixed the energy assumptions, ran the analysis, corrected it, and operationalised the sensitivities. Dates come from the documents themselves and from the preserved project records; the underlying documents are published unchanged. The supporting values are collected in the [timeline fact file](../evidence/TIMELINE_FACTS.md).*

## How to read this

The protocol and amendment files are preserved local design documents. They were never deposited with an external registry and are not independently timestamped public preregistrations, so the dates below are the dates I recorded in my own records, not third-party attestations. Several documents remain marked draft, and those markers are retained rather than tidied away.

One distinction runs through the whole chronology and matters for how the results should be read: some documents were written **before** any schedule-performance outcome had been inspected, and one was written **after** the primary result was known. Each entry says which.

## Design and protocol development

| When | What | Outcome status |
|---|---|---|
| 31 August 2026 (revision date in its header) | [`prereg-v1.1.md`](prereg-v1.1.md), the baseline protocol, fixing the question, endpoint, hypotheses and fixed-sequence gate, cohort rules, detector, schedules and estimand. Header still reads "DRAFT, NOT FROZEN"; the `prereg-v1` tag its own §0.2 requires before analysis was never created. | Before outcomes |
| 31 August 2026 | Amendments [A1](prereg-v1.2-amendment.md), [A2](prereg-v1.2-amendment-A2.md) and [A3](prereg-v1.2-amendment-A3.md), issued together after a Phase-0 correction and an implementation audit. A1 narrows the presymptomatic window to [onset − 21, onset − 1] and replaces the calibration-minimum rule; A2 adds the paired calibration floor `C_floor = 16` and the two-phase cohort construction; A3 corrects the baseline definition and several implementation rules. | Before outcomes |
| 1 September 2026 | The baseline-rule correction recorded in A3.1, removing a nested burn-in in which two 28-day requirements had been stacked. | Before outcomes |

## Pre-outcome checkpoint

| When | What | Outcome status |
|---|---|---|
| 1 September 2026 | [Pre-outcome checkpoint](PRE_OUTCOME_CHECKPOINT.md), recording the state of the work before any schedule-performance result was inspected: full regression suite at 140 tests passing, a final primary base cohort of 38, `C_min = 28` selected by the prespecified availability-only fallback after the 0.80 retention floor was not met, Gate A complete with mixed reproduction, and Gate B reconstructing six published quantities. | Before outcomes |

## Energy assumptions

| When | What | Outcome status |
|---|---|---|
| Before 2 September 2026 | The bench [measurement protocol](../hardware/measurement_protocol.md) was written and frozen, then superseded. It was never executed; see the [note on the superseded hardware protocol](../hardware/README.md). | Before outcomes |
| 2 September 2026 | Amendment [A4](prereg-v1.2-amendment-A4-no-hardware.md) replaces planned bench measurement with a modelled, schedule-attributable rail-level energy design. | Before outcomes |
| 2 September 2026 | The modelled-energy parameters and budgets were frozen, with their sources recorded in the [parameter provenance record](modelled_energy_parameter_provenance.md). The feasibility audit established that the E3 budget resolves to seven ten-minute bursts in the LOW, CENTRAL and HIGH parameterizations alike, so the schedule masks are identical across all three. | Before outcomes |

## Execution, correction, and re-execution

| When | What | Outcome status |
|---|---|---|
| 2 September 2026 | Amendment [A5](prereg-v1.2-amendment-A5-runner-operationalization.md) freezes the runner: raw-archive normalization, the calendar skeleton and its missingness rules, threshold calibration through onset − 28, the presymptomatic outcome on [onset − 21, onset − 1], the paired hierarchical outcome, and an execution guard requiring a committed runner, a clean working tree and the energy-freeze commit as an ancestor. | Before outcomes |
| 2 September 2026 | The first frozen real-data execution completed and wrote its preserved audit-trail directory. | Generated, not inspected |
| 2 September 2026 | Amendment [A6](prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md) corrects the Phase-2 step semantics. A quality-control audit — run before any win/loss/tie count, detection rate, warning time, p-value or effect size was inspected — found implausible input-dependent behaviour, and an outcome-blind diagnostic traced it to the Phase-2 step stream carrying no explicit zero rows. A6 confines the fix to inferring `steps = 0` only for Phase-2 minutes that have an observed heart rate and no explicit step record. | Correction chosen before outcomes were inspected |
| 2 September 2026 | The corrected run executed into a new commit-versioned directory. The superseded run was retained unchanged and is not eligible for confirmatory inference; its outputs are not mixed into the corrected findings anywhere in this repository. | Corrected run; this is the authoritative one |

The two runs are the pivot of this chronology, so the sequence is worth stating plainly. The first execution ran to completion under a frozen runner. Its outputs were then audited for plausibility without looking at any scientific outcome, and that audit failed. The cause was a data-encoding difference between the two source releases, not a choice about schedules or thresholds. A6 records the correction, what it deliberately leaves untouched — cohort, budget, schedules, detector, calibration floor, endpoint, gatekeeping — and the regression tests required before re-execution. Only then was the corrected run performed and its outcomes read.

## Sensitivity operationalisation, after the primary result

| When | What | Outcome status |
|---|---|---|
| 4 September 2026 | Amendment [A7](prereg-v1.2-amendment-A7-sensitivity-operationalization.md) operationalises the sensitivity analyses. **The confirmatory result was already known when this was written.** H1 did not reject, so the fixed sequence had closed, and A7 states that it cannot alter, reopen or reinterpret that gate. | After the primary outcome |

A7 is the one document in the chain written after the result was seen, and it is labelled that way in its own header rather than presented as prospective. It records the conditioning algorithm for the realised-sample-count M1 analysis that A3.9 had required but left underspecified, and it lists the planned analyses that were **not** run, with reasons — including a discrete-time survival analysis whose link function, covariate parameterization and estimand the baseline protocol never specified, and which is therefore not invented after the fact. Sensitivity results are estimation-only: point estimates and 95% intervals, no sensitivity p-value used for inference.

## Evidence preparation and release

| When | What |
|---|---|
| By 4 September 2026 | The initial research and the primary E3 analysis were complete, as documented in the project records. |
| 19–25 September 2026 | Formal evidence preparation, documentation, reproducibility verification and public release. The [changelog](../CHANGELOG.md) records what was published on each date. |
| 25 September 2026 | The evidence package was completed and its final verification carried out, ahead of the 28 and 29 September targets. The [verification report](VERIFICATION_REPORT.md) records the checks and their limits. |

I prioritized SAT preparation before beginning the formal evidence-documentation phase on 19 September. That is personal context for the gap between the two blocks above, not a technical finding.

## What this timeline does not establish

- It does not show that the protocol was externally registered or independently timestamped. It was not.
- It does not show that every possible investigation ended on 4 September 2026. It shows when the primary analysis was completed; later work is dated and described where it exists.
- It does not convert any post-primary analysis into a confirmatory one. The fixed sequence closed at H1 and stays closed.
- It does not record the energy ladder as an executed programme. Outcome analysis was limited to the central E3 budget, and separate LOW and HIGH outcome analyses were never performed.
