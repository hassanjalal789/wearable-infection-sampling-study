# Protocol index

*Publication-stage guide, written on 18 September 2026. The protocol it describes — [`prereg-v1.1.md`](prereg-v1.1.md) — is the baseline protocol I wrote during the research, published exactly as I preserved it, with its filename, wording, status marker, and unfilled placeholders unchanged.*

## What this document is, and what it is not

`prereg-v1.1.md` is the study's baseline protocol. I wrote it as a local Markdown file and kept it in a local Git repository. It was never deposited with an external registry, and the Git tag its own §0.2 requires before analysis (`prereg-v1`) was never created. Its header still reads **"DRAFT, NOT FROZEN"**, and fields such as `Frozen on`, `Commit at freeze`, `Author`, and the eligible sample size remain placeholders.

It is therefore a preserved local design document, not an independently timestamped public preregistration. Publishing it here records what was planned and when it was superseded; it does not turn it into a registration. See [publication notes](PUBLICATION_NOTES.md) for the publication-history disclosure.

## What the protocol fixed

- **Question.** Whether concentrating a fixed sensing budget in a nighttime window improves pre-symptomatic infection warning, and whether any such advantage survives matching on rest state (§1, §2.1).
- **Endpoint.** Pre-symptomatic warning at a fixed alert budget: warning = onset date − first alert date in whole days, counted only for alerts in the window from onset − 21 to onset. A participant with no qualifying alert is a non-detection, handled by the hierarchical comparison rather than by imputing zero (§9). **This onset-inclusive window is the historical v1.1 draft rule.** Amendment A1 replaced §9 with the narrower window **[onset − 21, onset − 1]**, so a pre-symptomatic warning is at least one day; an alert on the onset day itself is same-day detection, which does not count toward the primary endpoint and is tabulated separately, and the at-or-before window [onset − 21, onset] survives only as a labelled descriptive statistic for comparison with the source studies. The A5 runner specification implements [onset − 21, onset − 1] and evaluates onset day separately as a descriptive at-or-before endpoint; the archived run manifest records the same window. A1 and A5 are both published in this repository.
- **Hypotheses and gate.** H1 (S3 nocturnal vs S2 uniform), then M1 (S3ʳ vs S6), then H2 (S3 vs S5) and H3 (S3 vs S4) under Holm — a serial fixed-sequence procedure at α = 0.05 in which each stage is tested only if the previous stage rejected in the nocturnally-favouring direction. If a gate does not open, downstream comparisons are still estimated and reported, but labelled non-confirmatory (§2.1–2.3).
- **Cohort rules.** Stanford Phase 1 and Phase 2 public archives; Fitbit streams only; infection-positive under each source paper's rule; symptomatic with an onset date; at least 21 of the 28 days before onset analysable; a minimum number of calibration days with `z` defined. Sample size was left to be determined by applying these rules to the archives (§3).
- **Detector and operating point.** Time-of-day-normalised resting heart-rate z-score, thresholds calibrated per participant to at most 2 alert-days per person-month (§4, §5, §10).
- **Schedules.** Night window 00:00–06:59 (420 minutes), day window 07:00–23:59, 10-minute bursts for the burst-based comparison arms (S2, S3, S3ʳ, S4, S5 and S6), rest defined as a recorded step count of zero, non-overlapping bursts, and a per-day burst budget derived from the energy level (§7). S1 is the continuous reference arm: the protocol's own schedule table gives it all observed minutes and records it as "not energy-matched", so neither the burst length nor the energy budget applies to it.
- **Estimand and test.** Hierarchical paired win/loss/tie comparison summarised by θ, tested with an exact sign test, with bootstrap intervals and a mandatory reporting set for every comparison (§11).

## What later documents replaced

The amendments published so far are linked in the table below; the detailed crosswalk is in the [methods guide](METHODS_GUIDE.md).

| Rule in `prereg-v1.1.md` | Replaced or constrained by | Effect |
|---|---|---|
| §9 primary endpoint; §5.b minimum calibration data and the C_min rule; §7.1–7.5 schedule naming and placement; §8.1–8.4 energy accounting; §15 power, MDE and precision | Amendment A1 (`prereg-v1.2-amendment.md`), which replaces those sections in full | The pre-symptomatic window becomes [onset − 21, onset − 1], with onset-day alerts tabulated separately; the v1.1 minimum of 14 calibration days is described there as inadequate and is replaced by an availability-only C_min decision rule; and cross-schedule dependence in the power calculation is swept over a pre-specified sensitivity grid (correlations 0, 0.25, 0.50, 0.75) rather than estimated from the single S1 arm, which may inform only the marginal baseline detection probability, logged before any comparison is inspected |
| Calibration eligibility and the common-cohort principle; coverage-diagnostic populations; overlap investigation; energy boundaries; device assignment; two-phase cohort construction | Amendment A2 ([`prereg-v1.2-amendment-A2.md`](prereg-v1.2-amendment-A2.md)) | Introduces the calibration floor `C_floor = 16` z-defined days, required in both arms before a pair is compared. A2 supplements A1 and takes precedence where they touch the same section |
| Baseline definition, M1 matching, alert-budget handling, overlap check, power-simulation replicates, coverage population, reproduction-gate feasibility | Amendment A3 ([`prereg-v1.2-amendment-A3.md`](prereg-v1.2-amendment-A3.md)) | Corrects the baseline definition and several implementation rules before outcome analysis |
| §8.4 hardware measurement arrangements | Amendment A4 ([`prereg-v1.2-amendment-A4-no-hardware.md`](prereg-v1.2-amendment-A4-no-hardware.md)) | The study reports modelled schedule-attributable rail-level energy. The [hardware protocol](../hardware/measurement_protocol.md) is retained as a record of originally planned work and was not executed; see the [energy scope guide](ENERGY_SCOPE.md) and the [parameter provenance record](modelled_energy_parameter_provenance.md) |
| §8.5 energy ladder (E1–E4) as an analysis programme | Amendment [A5](prereg-v1.2-amendment-A5-runner-operationalization.md) | Outcome analysis is limited to the central E3 budget; energy robustness is represented by the frozen feasibility audit |
| §7.1 rest condition (step count zero) applied to Phase 2 | Amendment [A6](prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md) | Zero steps are inferred only for Phase-2 minutes with an observed heart rate and no explicit step record; this correction superseded the first run |
| §16 sensitivity analyses | Amendment [A7](prereg-v1.2-amendment-A7-sensitivity-operationalization.md) | Sensitivity analyses were operationalised after the primary result was seen, are sensitivity-only, and several planned analyses were not run, with reasons given |
| §3.2 sample size placeholder | The executed analysis | A source-defined cohort of 38 participants, of whom 30 had an evaluable pair in every primary comparison (see [results and limitations](RESULTS_AND_LIMITATIONS.md)) |
| §21 deviation register (`docs/deviations.md`) | Not created | No such file exists in the preserved archive. The amendment documents, this index, and the methods guide record the changes instead |

## Reading order

1. [`prereg-v1.1.md`](prereg-v1.1.md) — the baseline protocol published here.
2. Amendments [A1](prereg-v1.2-amendment.md) (v1.2), [A2](prereg-v1.2-amendment-A2.md) and [A3](prereg-v1.2-amendment-A3.md), with the [methods guide](METHODS_GUIDE.md) as their crosswalk.
3. [A4](prereg-v1.2-amendment-A4-no-hardware.md) and the [energy parameter provenance record](modelled_energy_parameter_provenance.md), read with the [energy scope guide](ENERGY_SCOPE.md) and the [note on the superseded hardware protocol](../hardware/README.md).
4. Amendments [A5](prereg-v1.2-amendment-A5-runner-operationalization.md), [A6](prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md) and [A7](prereg-v1.2-amendment-A7-sensitivity-operationalization.md), with the [pre-outcome checkpoint](PRE_OUTCOME_CHECKPOINT.md) that records the state of the work before any outcome was inspected. The [research timeline](RESEARCH_TIMELINE.md) places all of these in order.
5. [Results and limitations](RESULTS_AND_LIMITATIONS.md) for what the executed analysis found.
