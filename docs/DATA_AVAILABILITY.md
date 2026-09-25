# Data availability

*Publication-stage document, written on 25 September 2026 for research I designed and conducted. It states which data the study used, where they come from, what a reader would need to repeat each stage, and what this repository does not contain. It is new writing.*

## 1. Source datasets

The study reanalysed two public Stanford COVID-19 wearables datasets. No participants were recruited for this study.

| Release | Reference | Archive analysed | Size (bytes) | SHA-256 |
|---|---|---|---|---|
| Phase 1 | Mishra, T. et al. Pre-symptomatic detection of COVID-19 from smartwatch data. *Nature Biomedical Engineering* 4, 1208–1220 (2020). https://doi.org/10.1038/s41551-020-00640-6 | `COVID-19-Wearables.zip` | 378,380,920 | `52ca976e6c08daa0cf34b6b82f4fc69b8894c1eef66e598efa40197df4e380f4` |
| Phase 2 | Alavi, A. et al. Real-time alerting system for COVID-19 and other stress events using wearable data. *Nature Medicine* 28, 175–184 (2022). https://doi.org/10.1038/s41591-021-01593-2 | `COVID-19-Phase2-Wearables.zip` | 5,537,624,129 | `c90b13146d3996b4d2159c4af31115b9ba2cb3c3fc2e15565b34c016ced9c994` |

The sizes and hashes are those recorded by the inventory step for the archives I analysed; a download can be checked against them. The archives were downloaded from the public storage addresses set at the top of [`run_phase1.sh`](../run_phase1.sh). I have not re-checked that those addresses still serve the same files. Each paper's data availability statement is the authoritative route to its data.

**Supplementary workbooks.** Symptom-onset dates and the Gate B reconstruction come from the papers' supplementary material. The two workbooks used by the Gate B tests are:

| Saved as | Source | SHA-256 of the file used |
|---|---|---|
| `metadata/phase1_supplementary_data.xlsx` | Phase 1 supplementary workbook of Mishra et al. (2020) | `cf89b4b7e6209905d48adce5c4a56d76ea661e4ebd7b439636df46adc5c198ec` |
| `metadata/phase2_covid_metadata.xlsx` | Source-data workbook of Alavi et al. (2022) | `166f8465e9e0259fc6e185a07630f1048b369f9e0c34872dc978f656cd08e3b3` |

The download commands used during the research appear in the [historical execution log](../evidence/historical_execution_log.md#31-supplementary-tables-and-onset-labels).

## 2. Terms and redistribution

The datasets and supplementary files belong to the study teams and remain subject to whatever terms they set. This repository redistributes none of them: not the archives, not the supplementary workbooks, and nothing derived from them at the level of an individual participant. Public availability is not treated as permission to republish. Using them here implies no affiliation with or endorsement by the study teams. The [third-party notices](THIRD_PARTY_NOTICES.md) credit the datasets and the upstream software.

## 3. What each stage needs

| Stage | Inputs | In this repository? |
|---|---|---|
| Acquisition, inventory and cohort ([`run_phase1.sh`](../run_phase1.sh)) | The two archives; the onset-label file; for Phase 1, the external device map | Archives: no, identified above. Onset labels and device map: no, withheld because they name participants; the procedures that built them are published ([`src/find_onset_labels.md`](../src/find_onset_labels.md), [data and cohort guide](DATA_AND_COHORT.md)) |
| Primary run ([`src/primary_e3_experiment.py`](../src/primary_e3_experiment.py)) | The archives, the cohort and onset files, the frozen configuration, and the project history its guard checks | Configuration: yes. Everything else: no; see the [reproducibility guide](REPRODUCIBILITY.md#8-level-7-the-full-raw-data-analysis) |
| Confirmatory statistics and sensitivity analyses | The run's participant-level outputs | No, withheld. The published summaries and the counts they contain are enough to recompute θ, the exact p-values and the BCa intervals |
| Result tables, figures and digest | The two published summary files | Yes |
| Energy feasibility audit | The energy model and frozen configuration | Yes |
| Power calculation | None; it is a simulation | Yes |
| Gate B | The two supplementary workbooks above | No, third-party files |
| Gate A | The upstream repositories at their pinned commits and their sample data | No, referenced by commit in [`upstream_commits.json`](upstream_commits.json) |

## 4. Withheld material

The [publication manifest](../evidence/PUBLICATION_MANIFEST.csv) lists every research artifact group with its status. The groups not published are participant-level: onset labels, device maps, cohort membership, per-participant calibration and coverage, per-file inventories, the primary run's arm outcomes, pair results, daily records and participant input summary, the input diagnostic, and the sensitivity analyses' per-participant outcomes and pair results. They name or describe individual participants of the source studies and stay withheld until a specific publication-rights and privacy review establishes a basis for release. The aggregate results derived from them are published under [`results/`](../results/README.md).
