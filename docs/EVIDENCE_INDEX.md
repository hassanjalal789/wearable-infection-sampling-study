# Evidence index

*Publication-stage guide, written on 19 September 2026 for research I designed and conducted. It maps the claims this repository makes to the files that support them, and says where the support stops. It is extended as further material is published.*

## How to read this index

A claim is **supported** when a published file in this repository contains the evidence for it. It is **supported privately** when the evidence exists in the preserved project records but the file is not yet published or is not eligible for publication. It is **outstanding** when the check has not been performed for this publication. Nothing below is an independent verification of the research by a third party.

## Study design and executed rules

| Claim | Supporting file | Limit |
|---|---|---|
| The baseline design, its endpoint, hypotheses, gatekeeping and cohort rules | [`prereg-v1.1.md`](prereg-v1.1.md) | A preserved project record, still marked "DRAFT, NOT FROZEN", with unfilled placeholders. Not an independently timestamped registration, and the Git tag its own §0.2 requires was never created. |
| The executed endpoint [onset − 21, onset − 1], the calibration rule, schedule placement, energy accounting and the power treatment | [`prereg-v1.2-amendment.md`](prereg-v1.2-amendment.md) (A1) | Replaces the corresponding v1.1 sections in full; also marked draft. |
| The calibration floor of 16 z-defined days, cohort construction and device provenance | [`prereg-v1.2-amendment-A2.md`](prereg-v1.2-amendment-A2.md) | Supplements A1 and takes precedence where both touch a section. |
| The corrected single-pass baseline, the 90-day lookback, exact M1 matching | [`prereg-v1.2-amendment-A3.md`](prereg-v1.2-amendment-A3.md) | Includes a correction dated 1 September 2026. Measured effects quoted there are on synthetic records, not participant data. |
| Which document set each final rule | [`METHODS_GUIDE.md`](METHODS_GUIDE.md), [`PROTOCOL_INDEX.md`](PROTOCOL_INDEX.md) | Publication-stage writing, checked against the amendments; not itself historical evidence. |
| The runner specification, including evaluability and the executed window | [`prereg-v1.2-amendment-A5-runner-operationalization.md`](prereg-v1.2-amendment-A5-runner-operationalization.md) | Prospective by its own header: written before any schedule-performance outcome was generated. Still marked a project record, not a registration. |
| The Phase-2 step-data correction and why the first run is superseded | [`prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md`](prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md) | The diagnostic counts it reports are input-encoding diagnostics, not results. The superseded run's outputs are not published and appear in no table here. |
| The post-primary sensitivity operationalisation, and which planned analyses were not run | [`prereg-v1.2-amendment-A7-sensitivity-operationalization.md`](prereg-v1.2-amendment-A7-sensitivity-operationalization.md) | **Written after the primary result was known**, and labelled so in its own header. Sensitivity-only; it cannot reopen the closed gate. The sensitivity outputs themselves are not yet published. |
| The state of the work before any outcome was inspected | [`PRE_OUTCOME_CHECKPOINT.md`](PRE_OUTCOME_CHECKPOINT.md) | A contemporaneous record. It asserts that no schedule-performance outcome had been inspected; nothing external corroborates that. |
| The order of design, energy freeze, execution, correction and sensitivity work | [`RESEARCH_TIMELINE.md`](RESEARCH_TIMELINE.md), [`../evidence/TIMELINE_FACTS.md`](../evidence/TIMELINE_FACTS.md) | Dates come from document headers and the preserved audit trail. The audit trail fixes order, not wall-clock time; facts that could not be established are listed as unestablished. |
| Run configuration, the frozen calibration rule, and participant-flow counts | [`../evidence/EXECUTION_EXCERPTS.md`](../evidence/EXECUTION_EXCERPTS.md) | Configuration, decision rules and counts only. No per-participant record, and no output of the superseded run. |

## Data and cohort

| Claim | Supporting file | Limit |
|---|---|---|
| The two archives analysed, identified by size and SHA-256 | [`DATA_AND_COHORT.md`](DATA_AND_COHORT.md#1-source-data) | Taken from the preserved inventory manifests. The archives are not redistributed, and the download addresses were not re-checked for this publication. |
| Every CSV member of both archives matched a known schema (280 and 4,246) | [`schema_phase1.json`](../results/schema_phase1.json), [`schema_phase2.json`](../results/schema_phase2.json) | Counts only. The per-file inventories name participants and are withheld. |
| Every infection candidate's device came from a recorded source; none was guessed | [`device_coverage_check.json`](../results/device_coverage_check.json), [`device_map_summary.json`](../results/device_map_summary.json), [`build_device_map.py`](../src/build_device_map.py) | The per-participant device map is withheld. The Phase 1 Fitbit assignment rests on a published statement about a defined set of participants. |
| Onset dates came from the papers' supplementary data, never from the physiological signal | [`DATA_AND_COHORT.md`](DATA_AND_COHORT.md#1-source-data), [`find_onset_labels.md`](../src/find_onset_labels.md) | The source count was taken from the withheld label file; the labels are not published. |
| 116 candidates, 49 pre-calibration eligible, 38 in the cohort after the 28-day fallback minimum | [`participant_flow.json`](../results/participant_flow.json), [`calibration_rule.json`](../results/calibration_rule.json), [`build_cohort.py`](../src/build_cohort.py) | Aggregate counts; cohort membership is withheld. The step from 38 to 30 is explained in [results and limitations](RESULTS_AND_LIMITATIONS.md). |
| The cohort selection cannot see any schedule-performance quantity | [`build_cohort.py`](../src/build_cohort.py) | Shown by the module's imports, not by a rerun. |
| Night and day source coverage in three populations | [`coverage_diagnostic.json`](../results/coverage_diagnostic.json), [`coverage_diagnostic.py`](../src/coverage_diagnostic.py) | Describes data availability, not schedule performance. |
| Overlap between the two releases is undeterminable | [`overlap_investigation.json`](../results/overlap_investigation.json), [`check_overlap.py`](../src/check_overlap.py) | Both archives carry dates outside the published study windows, so no series comparison was run. |

## Energy

| Claim | Supporting file | Limit |
|---|---|---|
| The study reports modelled schedule-attributable rail-level energy, not measured energy | [`prereg-v1.2-amendment-A4-no-hardware.md`](prereg-v1.2-amendment-A4-no-hardware.md) | The amendment is the decision record; it is not a measurement. |
| The parameter values, their sources, and the LOW/CENTRAL/HIGH scenarios | [`modelled_energy_parameter_provenance.md`](modelled_energy_parameter_provenance.md) | Datasheet values and declared engineering assumptions. The duration assumptions are explicitly unmeasured. |
| Those eleven parameters match the configuration the analysis actually read | [`modelled_energy_scenarios.json`](../configs/modelled_energy_scenarios.json); publication check, 19 September 2026: 33 comparisons across the three scenarios, all equal | The configuration is byte-identical to the version I preserved during the research, so the comparison can now be repeated from this repository. |
| The bench protocol was planned and never executed | [`../hardware/measurement_protocol.md`](../hardware/measurement_protocol.md) with its [note](../hardware/README.md) | Supported by A4.1, the protocol's own empty replication record, and the absence of any measurement output in the preserved hardware folder. |
| E3 resolves to seven ten-minute bursts in all three scenarios, so one central outcome analysis was run | [`modelled_energy_match_audit.json`](../results/modelled_energy_match_audit.json), [`modelled_energy_match.py`](../src/modelled_energy_match.py), [`ENERGY_AND_SCHEDULES.md`](ENERGY_AND_SCHEDULES.md#4-from-budget-to-bursts), [`ENERGY_SCOPE.md`](ENERGY_SCOPE.md) | Recomputed from the published code and configuration on 24 September 2026; the output was byte-for-byte identical to the archived audit. Matching is to whole bursts within ±5%. Separate LOW and HIGH outcome analyses were never performed. |
| Each energy term is an increment above platform idle, idle is charged once, and the accelerometer is not counted twice | [`energy_model.py`](../src/energy_model.py), [`ENERGY_AND_SCHEDULES.md`](ENERGY_AND_SCHEDULES.md#2-the-model) | Shown by the code and its stated boundary definitions. It is a model of a reference architecture, not a measurement; the battery-life functions in the module were never used. |

## Sampling schedules

| Claim | Supporting file | Limit |
|---|---|---|
| How each arm places its bursts, and that every mask is deterministic apart from the seeded S5 | [`schedules.py`](../src/schedules.py), [`ENERGY_AND_SCHEDULES.md`](ENERGY_AND_SCHEDULES.md#5-the-schedules), [`test_schedules.py`](../tests/test_schedules.py) | Exercised by the published tests on synthetic days; see the [verification log](../evidence/VERIFICATION_LOG.md). |
| S3 is a fixed clock window, and S2 places three of its seven bursts inside that window | [`schedules.py`](../src/schedules.py) | Follows directly from the fixed strides at N = 7; S3 is not each participant's sleep. |
| S3r and S6 are counterfactual constructs matched at the same burst count each day | [`schedules.py`](../src/schedules.py), [`METHODS_GUIDE.md`](METHODS_GUIDE.md#5-schedules-and-matched-controls) | They read a whole day's rest pattern in advance and could not run in real time. |

## Pipeline and tests

| Claim | Supporting file | Limit |
|---|---|---|
| The detector's baseline reads only data from before the day it scores, and a day with no heart-rate data is unevaluable rather than negative | [`tod_z.py`](../src/tod_z.py), [`test_causality.py`](../tests/test_causality.py), [`test_missing_days.py`](../tests/test_missing_days.py) | Shown by the code and by tests on synthetic data, not by re-running the source data. |
| Every calibrated threshold keeps the calibration alert rate within 2 alert-days per person-month, and a schedule below 16 calibration days is not calibrated | [`tod_z.py`](../src/tod_z.py), [`primary_e3_experiment.py`](../src/primary_e3_experiment.py), [`PIPELINE_AND_TESTS.md`](PIPELINE_AND_TESTS.md#1-from-source-minutes-to-a-paired-result) | The per-participant calibration outputs are withheld because they name participants. |
| θ, the exact sign test, the BCa interval and the fixed-sequence gate were computed as described | [`reveal_primary_e3_confirmatory_results_fixed.py`](../evidence/scripts/reveal_primary_e3_confirmatory_results_fixed.py), [`verify_test_equivalence.py`](../src/verify_test_equivalence.py) | The script expects the project in a home-folder path and reads withheld participant-level outputs, so it cannot be run from this repository. |
| The runner refuses a real run without the energy-freeze ancestry, a committed runner and a clean working tree | [`primary_e3_experiment.py`](../src/primary_e3_experiment.py), [`VERIFICATION_LOG.md`](../evidence/VERIFICATION_LOG.md) | The guard was exercised here and stopped as designed; the full raw-data run cannot be performed from this repository. |
| The published test suite passes | [`VERIFICATION_LOG.md`](../evidence/VERIFICATION_LOG.md), [`PIPELINE_AND_TESTS.md`](PIPELINE_AND_TESTS.md#4-the-test-suite) | 156 passed on 24 September 2026. Synthetic inputs and published aggregates only; 25 historical tests await their modules. |
| The suite stood at 131, 140 and 159 passing tests at points during the research | [`provenance.txt`](../environment/provenance.txt), [`PRE_OUTCOME_CHECKPOINT.md`](PRE_OUTCOME_CHECKPOINT.md), [`audit_pytest.txt`](../evidence/audit/audit_pytest.txt) | Historical reports, not re-executed at those points. |
| The published chronology cites readable records and is internally consistent | [`validate_chronology.py`](../src/validate_chronology.py), [`timeline_facts.json`](../evidence/timeline_facts.json), [`test_validate_chronology.py`](../tests/test_validate_chronology.py) | New code for this repository. It checks support and consistency, not whether a record is true. |

## Results

| Claim | Supporting file | Limit |
|---|---|---|
| H1: 8 wins, 12 losses, 10 ties among 30 pairs; θ ≈ 0.433; 95% BCa 0.300–0.583; exact two-sided p ≈ 0.5034 | [`RESULTS_AND_LIMITATIONS.md`](RESULTS_AND_LIMITATIONS.md), transcribed from the archived corrected run | The archived tables and digest are **not yet published**, so the figures cannot yet be checked against source files inside this repository. |
| M1, H2 and H3 values are descriptive because the testing sequence closed after H1 | [`RESULTS_AND_LIMITATIONS.md`](RESULTS_AND_LIMITATIONS.md), [`METHODS_GUIDE.md`](METHODS_GUIDE.md) | Unadjusted values, shown for description only. |
| Detection counts and warning-time medians | [`RESULTS_AND_LIMITATIONS.md`](RESULTS_AND_LIMITATIONS.md) | Warning-time statistics are computed among detected participants only, a different denominator from the paired comparison. |
| The authoritative outputs are the corrected run; an earlier run is superseded | [`METHODS_GUIDE.md`](METHODS_GUIDE.md) §8, [`prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md`](prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md), [`../evidence/EXECUTION_EXCERPTS.md`](../evidence/EXECUTION_EXCERPTS.md) | The two run manifests differ only in the Phase-2 step-semantics field. The superseded run's outputs are not mixed into any table here, and neither run's result files are published yet. |

## Contributions and provenance

| Claim | Supporting file | Limit |
|---|---|---|
| Roles, advice received, and AI assistance | [`CONTRIBUTIONS.md`](CONTRIBUTIONS.md) | The roles listed are as I confirmed them. The preserved records document what was run; they cannot establish who performed each step. |
| What is published, what is excluded, and how privacy is handled | [`PUBLICATION_NOTES.md`](PUBLICATION_NOTES.md), [`../evidence/PUBLICATION_MANIFEST.csv`](../evidence/PUBLICATION_MANIFEST.csv) | Detailed redaction mappings are kept privately with the research evidence. |
| Every archived document here is byte-identical to the version I preserved during the research | Publication check, 19 September 2026: seven documents compared byte for byte | The check establishes content identity with the version I preserved; it does not by itself date when I wrote that version. |

## Outstanding for this publication

- The published test suite passes (156 tests, 24 September 2026); 25 historical tests await the modules they exercise.
- No figure has been regenerated, and no aggregate table has been recomputed from raw data.
- The full raw-data analysis has not been re-run; the runner requires a project history and withheld inputs this repository does not have, as the [pipeline and tests guide](PIPELINE_AND_TESTS.md#3-what-cannot-be-re-run-from-this-repository) explains.
- Reproduction of upstream algorithms was mixed in the archived work, and no negative-control analysis exists.
- Overlap between participants in the two dataset releases could not be determined.
- The data and cohort stage has not been re-run for publication; its published outputs are the preserved ones.
