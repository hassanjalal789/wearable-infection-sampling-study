# Data sources and cohort methods

*Publication-stage guide, written on 21 September 2026 for research I designed and conducted. It describes where the data came from, how I built the cohort, and what is published or withheld. It is new explanatory writing. The scripts, records and aggregate outputs it points to are byte-identical to the versions I preserved during the research process; I have not retrospectively edited them for publication.*

## 1. Source data

The study used two public archives released by the Stanford study teams. Their contents belong to those teams, and their use here implies no affiliation with or endorsement by them.

| Release | Paper | Archive | Size (bytes) |
|---|---|---|---|
| Phase 1 | [Mishra et al., 2020](https://doi.org/10.1038/s41551-020-00640-6) | `COVID-19-Wearables.zip` | 378,380,920 |
| Phase 2 | [Alavi et al., 2022](https://doi.org/10.1038/s41591-021-01593-2) | `COVID-19-Phase2-Wearables.zip` | 5,537,624,129 |

SHA-256 of the two archives I analysed, as recorded by the inventory step, so that a download can be checked against them:

```text
Phase 1  52ca976e6c08daa0cf34b6b82f4fc69b8894c1eef66e598efa40197df4e380f4
Phase 2  c90b13146d3996b4d2159c4af31115b9ba2cb3c3fc2e15565b34c016ced9c994
```

The download addresses are set at the top of [`run_phase1.sh`](../run_phase1.sh). I have not re-checked them for this publication.

**Nothing from the archives is redistributed here** — not the archives, not the papers' supplementary workbooks, and nothing derived from them at the level of an individual participant. Their public availability is not treated as permission to republish them.

**Acquisition record.** [`DATA_ACQUISITION_BLOCKED.md`](DATA_ACQUISITION_BLOCKED.md), dated 31 August 2026 (UTC), is the project record of an automated download of both archives failing because each exceeded the retrieval tool's size limit. It notes that both addresses were serving at the time. It is published as it stood; the archives identified above are the ones the inventory scripts then read.

**Symptom-onset dates.** The cohort needs an onset date for each infection-positive participant. The label rows for all 116 candidates came from the papers' own supplementary data — 32 from Mishra et al. and 84 from Alavi et al. — under the procedure in [`src/find_onset_labels.md`](../src/find_onset_labels.md), which never infers an onset date from the physiological data. A candidate with no onset date in those sources fails the onset requirement and is excluded. The label file names participants and is withheld.

## 2. Inventory

[`src/zip_inventory.py`](../src/zip_inventory.py) reads each archive in place. It records the archive's SHA-256 and every member's CRC32, classifies the members, measures each heart-rate file's native sampling resolution, and sets aside heart-rate files it cannot read. [`src/phase1_inventory.py`](../src/phase1_inventory.py), which [`run_phase1.sh`](../run_phase1.sh) runs on both releases, discovers each file's schema and fails loudly on any it does not recognise. Two of its rules matter downstream:

- Coverage is counted in **unique observed minute bins** against fixed denominators — 420 minutes at night (00:00–06:59) and 1,020 by day (07:00–23:59) — never as raw sample counts, which would overstate coverage for devices that record every few seconds.
- A device is **never inferred from a filename** that does not name one; such files are marked unknown and resolved separately (section 3).

Aggregate results: every CSV member matched a known schema — 280 of 280 in Phase 1 and 4,246 of 4,246 in Phase 2 ([`results/schema_phase1.json`](../results/schema_phase1.json), [`results/schema_phase2.json`](../results/schema_phase2.json)). One Phase 2 heart-rate file was set aside by the quarantine rule. The per-file inventories, member manifests, native-resolution tables and the quarantine list all name participants and are withheld.

## 3. Device provenance

[`src/build_device_map.py`](../src/build_device_map.py) assigns one device per participant **with a recorded source**, and never guesses one because a later filter needs it. Its sources, strongest first: the filename names the device; a file inside the archive states it; a published supplementary table lists the participant; a published statement covers a defined set the participant is independently known to belong to; correspondence with the study team. A participant with none of these is marked unknown and excluded, not guessed.

Phase 1 filenames carry no device. Mishra et al. state that their 32 analysed COVID-positive cases had Fitbit data; that statement describes a set, so it is applied only to participants whose membership of that set is established from a source of its own.

| Release | Device | Source of the assignment | Participants |
|---|---|---|---|
| Phase 1 | Fitbit | published statement covering a defined set | 32 |
| Phase 1 | unknown | — | 86 |
| Phase 2 | Fitbit | filename | 1,027 |
| Phase 2 | Apple Watch | supplementary table | 35 |
| Phase 2 | unknown | — | 1,060 |

From [`results/device_map_summary.json`](../results/device_map_summary.json); 2,240 participants in all. Unknown devices among participants who were never infection candidates do not affect the cohort. The check that matters is scoped to the candidates: [`src/check_device_coverage.py`](../src/check_device_coverage.py) found all **116 infection-positive candidates** (32 in Phase 1, 84 in Phase 2) resolved, none unknown or conflicting ([`results/device_coverage_check.json`](../results/device_coverage_check.json)).

## 4. Cohort construction

[`src/build_cohort.py`](../src/build_cohort.py) builds the cohort in the two phases set by amendment [A2](prereg-v1.2-amendment-A2.md) and explained in the [methods guide](METHODS_GUIDE.md#2-source-defined-cohort). It imports nothing from the schedule or detector code, so no schedule-performance quantity can reach the selection.

- **Phase A** applies device, infection status, symptoms with an onset date, baseline and source-coverage requirements, with no calibration-days filter. **49** participants qualified.
- **Calibration availability.** For each of the 49, the number of calibration days available from the source data alone was counted. The median was 46 days (interquartile range 34–112; range 0–407). The frozen rule picks the largest minimum in {28, 42, 61, 91} that keeps at least 80% of participants; the shares kept were 77.6%, 63.3%, 34.7% and 30.6%, so none qualified and the prespecified fallback of **28 days** applied ([`results/calibration_rule.json`](../results/calibration_rule.json)).
- **Phase B** keeps participants with at least 28 such days: **38** participants, after excluding 11 ([`results/participant_flow.json`](../results/participant_flow.json)).

The full per-phase flow is tabulated in the [execution excerpts](../evidence/EXECUTION_EXCERPTS.md#participant-flow). Of the 38, **30** had an evaluable pair in every primary comparison; the step from 38 to 30 is explained in [results and limitations](RESULTS_AND_LIMITATIONS.md).

**Why the minimum matters.** [`src/calibration_resolution.py`](../src/calibration_resolution.py) sets out the arithmetic. With *C* calibration days, a single alert corresponds to 30.44 / *C* alert-days per person-month. At *C* = 28 that is about 1.087, below the alert budget of 2, so meeting the budget does not force every threshold to produce zero calibration-window alerts.

## 5. Source coverage, night versus day

[`src/coverage_diagnostic.py`](../src/coverage_diagnostic.py) measures the share of each window's minutes with any heart-rate record, for three populations, bootstrapping over participants ([`results/coverage_diagnostic.json`](../results/coverage_diagnostic.json)):

| Population | Participants | Night coverage | Day coverage | Night minus day (95% CI) |
|---|---|---|---|---|
| Fitbit participants with a recorded device source | 1,059 | 0.851 | 0.860 | −0.009 (−0.020 to 0.001) |
| Pre-calibration eligible | 49 | 0.945 | 0.924 | 0.020 (0.009 to 0.032) |
| Final cohort | 38 | 0.937 | 0.922 | 0.016 (0.001 to 0.029) |

This describes how much source data each window has. It is a data-quality diagnostic, not a schedule outcome.

## 6. Overlap between the two releases

Whether any participant appears in both releases **could not be determined**. [`src/check_overlap.py`](../src/check_overlap.py) found no shared identifiers, but identifiers alone cannot rule overlap out. Its next step, comparing heart-rate series across releases, is valid only if both carry true calendar dates, so it checks those first. Neither passed: Phase 1 dates run from 2022-01-18 to 2030-09-03 against a published study window of 2020-01-01 to 2021-03-31, and Phase 2 dates from 2021-01-31 to 2029-12-31 against 2020-11-27 to 2021-07-20. With no valid calendar alignment, no series comparison was run and the verdict is `UNDETERMINABLE` ([`results/overlap_investigation.json`](../results/overlap_investigation.json)). The script never reports "no evidence of overlap" as "no overlap". The record notes that the Phase-2-only sensitivity analysis runs regardless of this verdict.

## 7. What is published and what is withheld

| Material | Status |
|---|---|
| Acquisition, inventory, device-provenance, cohort, coverage, overlap and calibration code (`src/`, `run_phase1.sh`) and the onset-label procedure | Published, byte-identical to the versions I preserved |
| Acquisition record and upstream commit pins (`docs/`) | Published, byte-identical |
| Aggregate outputs: schema checks, device summary, candidate device check, participant flow, calibration rule, coverage diagnostic, overlap investigation (`results/`) | Published, byte-identical |
| Onset labels, device maps, cohort membership, per-participant calibration days and coverage, per-file inventories and manifests, native-resolution tables, quarantine list, a Phase 2 timestamp audit | Withheld: each names participants |
| The two archives and the papers' supplementary workbooks | Not redistributed; identified above |
| Upstream repositories used in reproduction checks | Not redistributed; see [third-party notices](THIRD_PARTY_NOTICES.md) |
| Earlier versions of some of these scripts, kept before fixes | Published, byte-identical, in [`evidence/historical_code/`](../evidence/historical_code/README.md) |

## 8. Re-running this stage

[`run_phase1.sh`](../run_phase1.sh) runs the stage from the repository root, and `./run_phase1.sh --preflight` checks inputs and commands without computing anything. A full run needs the two archives, the onset-label file and, for Phase 1, the external device map; the last two are withheld here and would have to be rebuilt from the papers' supplementary material by the procedures above. The scripts need Python with NumPy and pandas; the historical environment records are in [`environment/`](../environment/README.md). The [data availability guide](DATA_AVAILABILITY.md) lists what each stage needs.

I have not re-run this stage for publication. Every number in this guide is transcribed from the preserved outputs linked beside it.
