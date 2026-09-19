# Wearable Infection Detection: Sampling Schedules Under Modelled Energy Budgets

A retrospective study of wearable heart-rate sampling schedules under modelled energy budgets. The primary comparison did not demonstrate an advantage for fixed-clock nighttime sampling over evenly spaced sampling.

The initial research and primary E3 analysis were completed by 4 September 2026, as documented in the project records. Formal evidence preparation, documentation, reproducibility verification, and public release began on 19 September 2026. The target is to complete the evidence package by 28 September, with final verification and handoff by 29 September. Any further analysis is documented with its actual dates, methods, and results. Completion will be reported after verification.

## Research question

Resting heart rate often rises before the symptoms of an infection appear, which is why consumer wearables have been studied as early-warning tools ([Mishra et al., 2020](https://doi.org/10.1038/s41551-020-00640-6); [Alavi et al., 2022](https://doi.org/10.1038/s41591-021-01593-2)). Measuring heart rate continuously costs energy, so a low-power device would sample in short bursts. If only a small share of the day can be sampled, does it matter *when* the samples are taken?

The study compared schedules held to the same modelled energy budget: about 5% of the energy of continuous sampling, which the model converts into seven ten-minute bursts a day. The primary question was whether placing those bursts in a fixed nighttime window (00:00–06:59 local clock time) gives better retrospective warning before symptom onset than spacing them evenly across the day. Nighttime was a candidate because measurements at night may be less disturbed by activity, meals, and posture; the design did not test why timing might matter.

## What this repository is

- **Retrospective analysis** of two public wearable datasets. No participants were recruited for this study, and no clinical monitoring system was deployed.
- **Modelled energy.** Budgets come from a parameterised energy model, not from hardware measurements. No battery saving was measured.
- **Negative primary finding.** The primary hypothesis (H1) was not rejected, so the fixed testing sequence closed and the remaining contrasts are estimation-only.
- **Records, not registration.** The protocol files labelled "preregistration" are preserved project records; several are still marked draft. They are not independently timestamped public preregistrations.
- **Verification status.** The values below were checked against the archived result files during preparation. The test suite has not been rerun and no figure has been regenerated for this publication; those checks are listed in the evidence index as outstanding.

## Start here

1. [Research summary](docs/RESEARCH_SUMMARY.md) — the study in plain language.
2. [Contribution statement](docs/CONTRIBUTIONS.md) — confirmed roles, advice received, and AI assistance.
3. [Methods guide](docs/METHODS_GUIDE.md) — the rules the executed study followed, each traced to the document that set it.
4. [Results and limitations](docs/RESULTS_AND_LIMITATIONS.md) — the main result and what constrains it.
5. [Evidence index](docs/EVIDENCE_INDEX.md) — which file supports which claim, and where the evidence stops.

Reproduction instructions are not yet published. No command is listed here until it has been run successfully for this publication in a documented environment.

## Main result

Each comparison pairs two schedules within the same participants. Schedule A *wins* for a participant if it produced a presymptomatic alert and B did not, or if both did and A's warning came strictly earlier; a *loss* is the reverse; everything else is a tie. θ = (wins + 0.5 × ties) / paired N. θ = 0.5 means no difference, and values below 0.5 favour schedule B. θ is a paired comparison statistic, not a detection accuracy.

| Comparison | A vs B | Paired N | Wins/losses/ties (A) | θ | 95% BCa interval | Exact two-sided p | Status |
|---|---|---|---|---|---|---|---|
| H1 | S3 nighttime vs S2 evenly spaced | 30 | 8/12/10 | 0.433 | 0.300–0.583 | 0.5034 | Confirmatory: not rejected |
| M1 | S3r vs S6 (rest-matched counterfactuals) | 30 | 13/11/6 | 0.533 | 0.367–0.683 | 0.8388* | Estimation-only (gate closed) |
| H2 | S3 nighttime vs S5 seeded random | 30 | 10/10/10 | 0.500 | 0.350–0.650 | 1.0000* | Estimation-only (gate closed) |
| H3 | S3 nighttime vs S4 rest-triggered | 30 | 2/9/19 | 0.383 | 0.283–0.483 | 0.0654* | Estimation-only (gate closed) |

\* Unadjusted values from the archived results table, shown for description only. They are not confirmatory tests, because the testing sequence closed after H1.

Under H1, nighttime sampling produced a presymptomatic alert for 19 of 30 participants and evenly spaced sampling for 20 of 30. Among participants with an alert, the median warning was 13 and 14 days. The aggregate result files and figures are not yet published, so no figure is shown here.

## Contents

Published so far:

```text
README.md                        this overview
CHANGELOG.md                     publication changes by date
docs/
  prereg-v1.1.md                 original baseline protocol (draft marker retained)
  prereg-v1.2-amendment.md       amendment A1: endpoint, calibration, schedules, energy, power
  prereg-v1.2-amendment-A2.md    amendment A2: cohort, calibration availability, device provenance
  prereg-v1.2-amendment-A3.md    amendment A3: implementation patches, corrected baseline rule
  prereg-v1.2-amendment-A4-no-hardware.md
                                 amendment A4: modelled energy replaces bench measurement
  modelled_energy_parameter_provenance.md
                                 frozen energy parameters with their sources
  PROTOCOL_INDEX.md              what the original protocol fixed, and what replaced each rule
  METHODS_GUIDE.md               final rules traced to the amendment that set them
  ENERGY_SCOPE.md                what the modelled energy budget does and does not establish
  RESEARCH_SUMMARY.md            plain-language summary
  RESULTS_AND_LIMITATIONS.md     main result and known limitations
  EVIDENCE_INDEX.md              claims mapped to supporting files and evidence limits
  CONTRIBUTIONS.md               confirmed contributions and assistance
  PUBLICATION_NOTES.md           how this archive is being published
hardware/
  measurement_protocol.md        historical bench protocol, superseded and never executed
  README.md                      why it is published and what it does not show
evidence/
  PUBLICATION_MANIFEST.csv       disposition of each research artifact group
```

Not yet published: amendments A5–A7 and the pre-outcome checkpoint, the research timeline, data-availability guidance and third-party notices, analysis code (`src/`) and configuration (`configs/`), tests (`tests/`) and historical environment records (`environment/`), aggregate results and figures (`results/`), and the reproducibility and validation records (`evidence/`). The [manifest](evidence/PUBLICATION_MANIFEST.csv) lists each group and its status.

**Source data.** The study used the public Stanford COVID-19 wearables datasets described by [Mishra et al. (2020)](https://doi.org/10.1038/s41551-020-00640-6) (Phase 1) and [Alavi et al. (2022)](https://doi.org/10.1038/s41591-021-01593-2) (Phase 2). Raw heart-rate and step records are not redistributed here. Access routes and archive details will be documented in a data-availability guide, which is not yet published.

## Limitations

- **Small retrospective sample.** 30 of the 38 source-defined participants had an evaluable pair for every comparison, and the H1 interval (0.300–0.583) is wide.
- **Modelled, not measured, energy.** The budget does not demonstrate battery savings on any real device; see the [energy scope guide](docs/ENERGY_SCOPE.md).
- **Schedule definitions.** S3 is a fixed clock window, not each person's sleep. The evenly spaced schedule S2 starts at midnight, so 3 of its 7 bursts also fall inside 00:00–06:59; H1 therefore compares 7 nighttime bursts with 3 nighttime plus 4 daytime bursts. S3r and S6 use a whole day's step data and could not run in real time.
- **Unresolved signal question.** Continuous sampling produced alerts for 19 of the same 30 participants, no more than the sparse schedules, and no negative-control analysis was run. How far the alerts reflect infection rather than chance under the alert budget is unresolved.
- **Timing of the analysis plan.** Several protocol files remain marked draft, and the sensitivity-analysis details were operationalised after the primary result was seen.
- **Other uncertainty.** Reproduction of upstream algorithms was mixed, and overlap between participants in the two dataset releases could not be determined.

Details and sources: [results and limitations](docs/RESULTS_AND_LIMITATIONS.md).

## Citation

Citation metadata (`CITATION.cff`) will be added once release information exists. Until then, please cite:

> Hassan Jalal. *Wearable Infection Detection: Sampling Schedules Under Modelled Energy Budgets* (research evidence archive). GitHub, 2026. https://github.com/hassanjalal789/wearable-infection-sampling-study

Please also cite the dataset papers:

- Mishra, T. et al. Pre-symptomatic detection of COVID-19 from smartwatch data. *Nature Biomedical Engineering* 4, 1208–1220 (2020). https://doi.org/10.1038/s41551-020-00640-6
- Alavi, A. et al. Real-time alerting system for COVID-19 and other stress events using wearable data. *Nature Medicine* 28, 175–184 (2022). https://doi.org/10.1038/s41591-021-01593-2

## Credits

- **Research and publication:** Hassan Jalal. See the [contribution statement](docs/CONTRIBUTIONS.md), which also records informal advice and AI assistance.
- **Data:** the Stanford study teams behind the Phase 1 and Phase 2 datasets cited above. Their use here does not imply affiliation with or endorsement by those teams.
- **Upstream software:** code used for reproduction checks keeps its original authors and licences; notices will be published with the data-availability guide.
- **Licence:** no licence has been selected for this project's own files yet. See [licensing status](docs/PUBLICATION_NOTES.md#licensing-status).
