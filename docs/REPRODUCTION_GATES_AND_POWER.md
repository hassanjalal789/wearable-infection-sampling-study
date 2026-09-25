# Reproduction gates and power calculation

*Publication-stage guide, written on 25 September 2026 for research I designed and conducted. It explains the two reproduction gates I ran before the outcome analysis, what each found, and the power calculation I froze at the audited cohort size. It is new explanatory writing. The code, result records and logs it points to are the versions I preserved during the research process. Two are published as sanitized copies and are marked as such in the [manifest](../evidence/PUBLICATION_MANIFEST.csv): the Gate B result, with its list of participant identifiers removed, and one Gate A log, with its private paths and a participant identifier replaced. I have not retrospectively edited any other file for publication.*

## 1. Why the gates existed

The baseline protocol set out the reproduction checks in [§18.1](prereg-v1.1.md#181-reproduction):

- **Gate A (required):** upstream code, run unmodified on the sample participants shipped in its own repository, reproduces that repository's committed output files exactly.
- **Gate B (target):** published cohort numbers from the two source studies are reproduced within stated tolerances.
- **Gate C (fallback):** if a gate fails, the discrepancy is reported as a finding, the upstream code is not modified to close it, and every schedule comparison is anchored to the study's own continuous reference arm, S1.

The gates check the context of the study, not its result. The primary comparison uses my own detector and the S1 reference arm. It does not depend on any upstream detector reproducing.

Inspection of the four pinned repositories showed that the Gate A wording could not be evaluated for all of them, because two ship no complete machine-readable reference output. Amendment A3 records the change in [§A3.10](prereg-v1.2-amendment-A3.md#a310--reproduction-gate-a-feasibility-clarification), before any schedule-performance analysis. Gate A was split into **A1**, exact reproduction where a repository ships a sample input and reference output, and **A2**, an execution test where it does not. Upstream files could not be edited to obtain a pass. Any environment workaround had to be recorded and had to leave the upstream file's checksum unchanged.

## 2. Gate A: upstream code against its own outputs

The repositories were pinned at the commits in [`upstream_commits.json`](upstream_commits.json); their licences are in the [third-party notices](THIRD_PARTY_NOTICES.md). No upstream code is redistributed here.

| Detector | Repository | Check | Ran | Reproduced its committed output |
|---|---|---|---|---|
| RHR-Diff | WearableDetection | A1 | yes | **yes**, byte for byte (5 rows) |
| CuSum | WearableDetection | A1 | yes | **yes**, byte for byte (3 rows) |
| HROS-AD | AnomalyDetect | A1 | yes, in the pinned Python 3.6 environment | **no**: 22 rows generated against 456 in the reference; none of the 22 appears in the reference |
| RHRAD | AnomalyDetect | A1 | yes, in the pinned Python 3.6 environment | **no**: 22 rows generated against 617 in the reference; 20 of the 22 appear in it |
| NightSignal (Fitbit sample) | wearable-infection | A2 | yes: 197 nights classified | no complete reference exists |
| Alarm online CuSum | Alarm | A2 | its functions load with the expected interfaces | no sample data or reference exists |

Source: [`results/gate_a/gate_a_results.json`](../results/gate_a/gate_a_results.json), the authoritative record, and the summary [`results/gate_a_summary.json`](../results/gate_a_summary.json). The NightSignal night counts by class are in [`nightsignal_fitbit_summary.json`](../results/gate_a/nightsignal_fitbit_summary.json) (170 green, 6 yellow, 21 red), with the Apple Watch sample in [`nightsignal_applewatch_summary.json`](../results/gate_a/nightsignal_applewatch_summary.json).

**The outcome was mixed, and it is reported as mixed.** WearableDetection reproduced exactly. AnomalyDetect ran to completion in a container built to its pinned versions (Python 3.6.8, NumPy 1.18.5, pandas 1.0.4, statsmodels 0.11.0), but neither of its two detectors regenerated its committed output. A history check in the execution record shows that the sample input files and the HROS-AD script at the pinned commit are the same Git blobs as at the commit that added the reference output. The cause of the mismatch was not established, and the upstream code was not changed to remove it.

**Failures on the way.** In a current Python environment, HROS-AD failed three times: a missing plotting dependency, a pandas change that no longer drops non-numeric columns from rolling means, and a pandas change to frequency aliases. The upstream script's SHA-256 was unchanged before and after every attempt. These attempts are shown in the [execution log](../evidence/historical_execution_log.md#74-hros-ad-attempts-in-the-current-environment). An earlier, superseded record is published as [`gate_a_results_PRELIMINARY_DO_NOT_USE.json`](../results/gate_a/gate_a_results_PRELIMINARY_DO_NOT_USE.json). Its own label says not to use it; it is published because the authoritative record names it, and because it records the blocked and failed runs from the first attempt, including the R dependency blocker and the Isolation Forest run.

**Environment workarounds.** Two small wrappers ran upstream scripts without editing them:

- [`src/gate_a_shim.py`](../src/gate_a_shim.py) maps matplotlib style names that newer versions renamed.
- [`src/gate_a_anomalydetect_compat.py`](../src/gate_a_anomalydetect_compat.py) also restores two older pandas and statsmodels calling conventions.

Each wrapper prints the upstream file's SHA-256 before and after execution. The runs that count for AnomalyDetect used neither wrapper; they ran in the pinned container.

## 3. Gate B: published cohort numbers

[`src/gate_b_compute.py`](../src/gate_b_compute.py) reads the source studies' supplementary tables and recomputes the counts each paper reports. It checks that the published numbers can be reconstructed from the published tables. It does not re-run either study's detection algorithm on raw data.

| Quantity | Published | Reconstructed | Tolerance | Status |
|---|---|---|---|---|
| Mishra et al.: analysed COVID-19 cases | 32 | 32 | exact | pass |
| Mishra et al.: detected cases | 26 | 26 | ± 2 | pass |
| Mishra et al.: median days before symptom onset | 4 | 4.0 | ± 1 | pass |
| Mishra et al.: detected at or before onset, of 25 with symptom information | 22 | 22 | ± 2 | pass |
| Alavi et al.: confirmed positives | 84 | 84 | exact | pass |
| Alavi et al.: sensitivity per person | 80% | 79.8% (67 of 84) | ± 5 pp | pass |
| Alavi et al.: specificity per alert-day | 87.7% | not reconstructible | ± 2 pp | not tested |

Source: [`results/gate_b_results.json`](../results/gate_b_results.json).

The published specificity rests on 87,124 true-negative and 12,186 false-positive alert-days. The public tables cover the COVID-positive participants and their alert timing, but not the non-COVID participant-days needed to count those, so the figure is kept as a paper-reported benchmark and is labelled neither pass nor fail. A search of the supplementary workbooks for the underlying counts is shown in the [execution log](../evidence/historical_execution_log.md#81-source-search-and-an-interrupted-cell-search); it was stopped by hand, and its partial output is not published.

The two Alavi figures have different denominators, one per person and one per alert-day, and are never presented as a matched sensitivity and specificity pair.

**What is withheld.** The Gate B audit files that print rows of the supplementary tables, and the three table extracts, contain participant-level rows from third-party files and are not published. The published result file omits the list of 32 participant identifiers that the preserved version carries; nothing else in it differs.

## 4. The frozen power calculation

The power design is set out in amendment A1's [replacement §15](prereg-v1.2-amendment.md#replaces-15--power-mde-and-precision), with the replicate-count correction in [§A3.7](prereg-v1.2-amendment-A3.md#a37--power-simulation-replicate-count-audit-item-6). [`src/power_sim.py`](../src/power_sim.py) simulates the paired design and the exact sign test:

- the audited cohort size, N = 38;
- 4,000 Monte Carlo replicates per candidate cell, with seed 20261010;
- baseline detection probabilities of 0.40, 0.50 and 0.60, swept rather than taken from any result;
- within-participant dependence swept over a grid from 0 to 0.75, because it cannot be estimated from one arm;
- two-sided α = 0.05.

The effect is searched along a fixed ray: detection and warning time improve together, one percentage point for each 0.1 day. The result is therefore a minimum detectable *joint* effect along that ray, not a one-dimensional minimum detectable effect.

| Baseline detection | Dependence (ρ) | Smallest joint effect with ≥ 80% power | Power | Expected discordant pairs | Expected θ half-width |
|---|---|---|---|---|---|
| 0.40 | independent (0.00) | +25 pp, +2.5 d | 0.812 | 29.1 | 0.119 |
| 0.40 | low (0.25) | +25 pp, +2.5 d | 0.904 | 27.5 | 0.111 |
| 0.40 | moderate (0.50) | +20 pp, +2.0 d | 0.884 | 24.3 | 0.106 |
| 0.40 | high (0.75) | +15 pp, +1.5 d | 0.891 | 20.4 | 0.097 |
| 0.50 | independent (0.00) | +25 pp, +2.5 d | 0.889 | 31.8 | 0.119 |
| 0.50 | low (0.25) | +20 pp, +2.0 d | 0.827 | 29.2 | 0.118 |
| 0.50 | moderate (0.50) | +20 pp, +2.0 d | 0.949 | 27.4 | 0.108 |
| 0.50 | high (0.75) | +15 pp, +1.5 d | 0.949 | 23.3 | 0.100 |
| 0.60 | independent (0.00) | +20 pp, +2.0 d | 0.817 | 32.9 | 0.126 |
| 0.60 | low (0.25) | +20 pp, +2.0 d | 0.922 | 31.5 | 0.118 |
| 0.60 | moderate (0.50) | +15 pp, +1.5 d | 0.832 | 28.2 | 0.116 |
| 0.60 | high (0.75) | +15 pp, +1.5 d | 0.983 | 26.0 | 0.100 |

Source: the `ray_cells` of [`results/power_sim_frozen_n38.json`](../results/power_sim_frozen_n38.json), which also holds the two-dimensional power surface (432 cells) that the script's own documentation names as the preferred reporting object. The file records the SHA-256 of the script that produced it, and that value matches the published `src/power_sim.py`.

**How to read it.** Before any outcome was seen, the design could expect 80% power only for large joint effects: roughly 15 to 25 percentage points more presymptomatic detections together with 1.5 to 2.5 more days of warning. The primary comparison then had 30 evaluable pairs, not 38, so its power against those effects would be expected to be lower than the table shows. I have not recomputed power at N = 30 or at the observed effect; power computed after the result would add nothing to the interval already reported. The negative H1 result should therefore be read with its interval, 0.300 to 0.583, not as evidence that nighttime sampling makes no difference.

**Earlier planning runs.** Four further files record non-binding planning runs:

- [`power_sim_output.json`](../results/power_sim_output.json)
- [`power_surface_PLANNING_demo.json`](../results/power_surface_PLANNING_demo.json)
- the logs [`power_planning.log`](../results/power_planning.log) and [`power_sim_run.log`](../results/power_sim_run.log)

They used cohort sizes of 25 to 50, smaller replicate counts and earlier versions of the script. They do not all correspond to one another: the output file records a different script hash from the one the run log prints, and its values match neither log. None was used for the frozen calculation. They are published as historical records. The two logs and the demonstration surface label themselves as planning runs; the output file carries no status label.

## 5. What was re-run for this publication

On 25 September 2026, in the environment recorded in the [verification log](../evidence/VERIFICATION_LOG.md):

- **Power.** The published `src/power_sim.py`, unchanged, was re-run for the 12 effect-ray cells of the frozen calculation with its recorded seed and replicate count. Every cell's result matched the archived file. The two-dimensional surface was not re-run.
- **Power tests.** `tests/test_power_sim.py` passes as part of the published suite.
- **Gate B.** With the two supplementary workbooks placed under `metadata/`, `tests/test_reproduction.py` passed, and `src/gate_b_compute.py` regenerated a result file byte-for-byte identical to the preserved one. The workbooks were first checked against the checksums in my preserved research record. They are third-party files and are not in this repository. Without them the test module is not collected, and pytest names the missing files in its session header, which `-q` hides; see [`conftest.py`](../conftest.py).
- **Gate A** was not re-run. It needs the four upstream repositories, R with two packages, and a Python 3.6 container image; its published records are archived outputs.

## 6. Running these checks yourself

- `python -m pytest tests/ -q` runs the published suite, including the power-simulation tests. It needs no data.
- The Gate B tests need the Phase 1 supplementary workbook of [Mishra et al. (2020)](https://doi.org/10.1038/s41551-020-00640-6), saved as `metadata/phase1_supplementary_data.xlsx`, and the source-data workbook of [Alavi et al. (2022)](https://doi.org/10.1038/s41591-021-01593-2), saved as `metadata/phase2_covid_metadata.xlsx`. The download commands used during the research are shown in the [execution log](../evidence/historical_execution_log.md#31-supplementary-tables-and-onset-labels). `metadata/` is ignored by Git in this repository.
- `make gates` clones the upstream repositories and rewrites `docs/upstream_commits.json`. It is a historical target and was not run for this publication.
