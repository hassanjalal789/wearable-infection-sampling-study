# Reproducibility guide

*Publication-stage guide, written on 25 September 2026 for research I designed and conducted. It sets out what can be reproduced from this repository, level by level, with the commands I ran for this publication and what they reported. It is new writing. Every command below was run in a fresh clone in the environment described in section 1; the [verification report](VERIFICATION_REPORT.md) records the runs, and nothing here is listed without having been run.*

Each level shows something different. Checking published files shows that they are the files released here; recomputing an aggregate shows that it follows from other published numbers; passing tests show that the code behaves as its tests expect on synthetic inputs; none of these re-runs the analysis on the source data.

| Level | What it can show | What it needs | Status |
|---|---|---|---|
| [1. Inspect archived outputs](#2-level-1-inspect-archived-outputs-and-check-file-integrity) | Every published file is the one released, byte for byte | This repository | Run; all files match |
| [2. Check published aggregates](#3-level-2-check-published-aggregates) | θ, exact p-values, BCa intervals, gate decisions and the energy audit follow from the published inputs | Section 1 environment | Run; no discrepancy |
| [3. Run the tests](#4-level-3-run-the-tests-and-the-chronology-validator) | The published code behaves as its tests expect; the chronology is consistent | Section 1 environment | Run; 174 passed, no chronology finding |
| [4. Regenerate tables and figures](#5-level-4-regenerate-the-result-tables-and-figures) | The published tables and figures follow from the two published summary files | Section 1 environment | Run; tables identical, figures visually identical |
| [5. Optional checks](#6-level-5-optional-checks-gate-b-and-the-power-calculation) | Published cohort numbers of the source papers (Gate B); the frozen power calculation | Two third-party workbooks (Gate B only) | Run; both matched |
| [6. Upstream reproduction (Gate A)](#7-level-6-upstream-reproduction-gate-a) | Whether upstream code reproduces its own outputs | Upstream repositories, R, container images | Not re-run |
| [7. Full raw-data analysis](#8-level-7-the-full-raw-data-analysis) | The study result from the source data | Project history, source archives, withheld participant-level inputs | Not possible from this repository |

## 1. Environment

The commands were run on Linux x86-64 with Python 3.13.13. From a terminal:

```bash
git clone https://github.com/hassanjalal789/wearable-infection-sampling-study.git
cd wearable-infection-sampling-study
python3.13 -m venv .venv
. .venv/bin/activate
python -m pip install -r environment/publication-requirements.txt
```

[`environment/publication-requirements.txt`](../environment/publication-requirements.txt) pins every package of the verification environment: NumPy 2.4.4, pandas 3.0.2, SciPy 1.17.1, Matplotlib 3.10.9, PyArrow 25.0.1, openpyxl 3.1.5 and pytest 9.1.1, with their dependencies. It is a publication file, not a historical record; the research environments are described in [`environment/README.md`](../environment/README.md). Do not add the optional `tabulate` package: the archived Markdown tables were written without it, and with it installed the table script formats them differently.

All later commands are run from the repository root with the environment active.

## 2. Level 1: inspect archived outputs and check file integrity

**What to inspect.** The [results note](../results/README.md) identifies the authoritative corrected run and lists every published output. The [evidence index](EVIDENCE_INDEX.md) maps each major claim to the file that supports it.

**Command.**

```bash
sha256sum -c evidence/SHA256SUMS.txt
```

**Expected output.** One line per listed file ending in `: OK`, and exit status 0. With `--quiet`, nothing is printed unless a file fails. [`SHA256SUMS.txt`](../evidence/SHA256SUMS.txt) lists every file tracked in the repository except itself. It shows that the files are the ones released here; the correspondence between the archived files and the versions I preserved during the research is recorded in the [verification log](../evidence/VERIFICATION_LOG.md) and the [publication manifest](../evidence/PUBLICATION_MANIFEST.csv).

## 3. Level 2: check published aggregates

**Command.**

```bash
python src/check_public_package.py links arithmetic intervals energy
```

[`src/check_public_package.py`](../src/check_public_package.py) is new code, written for this repository. Its docstring states each check. In short:

- **links:** every relative link in every Markdown file resolves, including `#anchor` links.
- **arithmetic:** in the published [confirmatory summary](../results/primary_e3_run_83cc8d1/confirmatory_analysis/confirmatory_comparison_summary.csv), counts sum to N, θ = (W + 0.5 × T) / N, the exact two-sided sign-test p-value follows from W and L, each estimate lies inside its interval, and detection rates equal detected over evaluable; the [gate decisions](../results/primary_e3_run_83cc8d1/confirmatory_analysis/gatekeeping_decisions.json) follow from the H1 row; the same count and θ checks hold for all 33 [sensitivity rows](../results/primary_e3_run_83cc8d1/sensitivity_analysis/sensitivity_summary.csv), none of which carries a p-value; and the README results table and the main summary documents quote the published values.
- **intervals:** every 95% BCa bootstrap interval, recomputed with the bootstrap function of the published script that produced it and that script's recorded seeds, equals the published limits. Both scripts bootstrap a vector built from the win, loss and tie counts alone, so the published counts suffice.
- **energy:** the [energy feasibility audit](../results/modelled_energy_match_audit.json), recomputed from the published model and configuration, is byte-for-byte identical to the archived file.

**Expected output.** A line `links: PASS (…)`, `arithmetic: PASS (…)`, `intervals: PASS (4 confirmatory and 33 sensitivity intervals)` and `energy: PASS (…)`, then `ALL CHECKS PASSED` and exit status 0. Any failure is listed under its check and the exit status is 1.

**Not covered.** Nothing at this level touches the source data. It shows that the published numbers are consistent with one another and with the published code, not that the underlying per-participant results are correct.

## 4. Level 3: run the tests and the chronology validator

**Commands.**

```bash
python -m pytest tests/ -q
python src/validate_chronology.py
```

**Expected output.** `174 passed`. The suite holds 152 historical tests and 22 tests for the chronology validator, which is new code. The seven Gate B tests in `tests/test_reproduction.py` need two third-party workbooks (level 5); when they are absent, the root [`conftest.py`](../conftest.py) leaves that module uncollected and names the missing files in the session header, which `-q` hides. The validator prints `SUPPORTED: … events and 0 additional analyses; no unresolved finding` and exits 0.

**What it shows.** The tests run on synthetic data built in [`tests/synth.py`](../tests/synth.py) and on published configuration and aggregate files; no test reads a source archive. The [pipeline and tests guide](PIPELINE_AND_TESTS.md#4-the-test-suite) describes what they check. The validator checks that the published chronology cites readable records and is internally consistent; it cannot show that a record is true.

## 5. Level 4: regenerate the result tables and figures

**Command.**

```bash
python src/check_public_package.py tables
```

This runs the unchanged [`src/make_final_tables_figures.py`](../src/make_final_tables_figures.py) in a temporary folder that contains only the two published summary files, then compares its output with the archived copies.

**Expected output.** `tables: PASS (7 table and digest files compared byte for byte; 6 figure files redrawn, not compared)`.

**To keep the regenerated files.** The table script reads from and writes to `rq1/results/primary_e3_run_83cc8d1/` inside the home folder, so point `HOME` at an empty folder that holds only the two summaries:

```bash
R=/tmp/regen/rq1/results/primary_e3_run_83cc8d1
mkdir -p $R/confirmatory_analysis $R/sensitivity_analysis
cp results/primary_e3_run_83cc8d1/confirmatory_analysis/confirmatory_comparison_summary.csv $R/confirmatory_analysis/
cp results/primary_e3_run_83cc8d1/sensitivity_analysis/sensitivity_summary.csv $R/sensitivity_analysis/
HOME=/tmp/regen MPLBACKEND=Agg python src/make_final_tables_figures.py
```

The output appears in `/tmp/regen/rq1/results/primary_e3_run_83cc8d1/final_tables_figures/`. The three CSV tables, three Markdown tables and the digest are byte-for-byte identical to the archived ones. The six figure files are not: the archived figures were drawn with Matplotlib 3.11.1, as the files record, and this environment has 3.10.9. Compared side by side, the regenerated figures show the same points, intervals, labels and reference lines; their pixel dimensions differ by a few pixels.

## 6. Level 5: optional checks, Gate B and the power calculation

**Gate B, the published cohort numbers of the source papers.** This needs two supplementary workbooks from the source studies, which are third-party files and are not in this repository. Save the Phase 1 supplementary workbook of Mishra et al. (2020) as `metadata/phase1_supplementary_data.xlsx` and the source-data workbook of Alavi et al. (2022) as `metadata/phase2_covid_metadata.xlsx`; the [data availability guide](DATA_AVAILABILITY.md) gives their SHA-256 values so that the files can be checked first. Then:

```bash
python -m pytest tests/ -q
python src/gate_b_compute.py
```

With both workbooks present the suite reports `181 passed`. `gate_b_compute.py` rewrites `results/gate_b_results.json` in your working copy; the regenerated file includes a list of participant identifiers that the published copy omits, and is otherwise identical to it. Do not commit the regenerated file.

**The frozen power calculation.**

```bash
python src/check_public_package.py power
```

This runs the unchanged [`src/power_sim.py`](../src/power_sim.py) for the 12 effect-ray cells of the frozen calculation at N = 38, with its recorded seed and 4,000 replicates per candidate cell, and compares every recorded field with [`results/power_sim_frozen_n38.json`](../results/power_sim_frozen_n38.json). It took about three minutes. Expected output: `power: PASS (12 effect-ray cells, 204 recorded fields compared)`. The 432-cell power surface is not re-run.

## 7. Level 6: upstream reproduction (Gate A)

Not re-run for this publication. Gate A ran unmodified upstream code on its own sample data. Repeating it needs the four upstream repositories at their pinned commits ([`docs/upstream_commits.json`](upstream_commits.json)), R with two packages, and the Python 3.6 container images described by the Dockerfiles in [`environment/`](../environment/). The archived records and their mixed outcome are explained in the [gates guide](REPRODUCTION_GATES_AND_POWER.md#2-gate-a-upstream-code-against-its-own-outputs). The historical `make gates` target clones the upstream repositories and rewrites `docs/upstream_commits.json`; it was not run.

## 8. Level 7: the full raw-data analysis

Not possible from this repository. Three things block it:

1. **The execution guard.** The primary runner refuses to run unless its energy-freeze commit is an ancestor of the current commit, the runner is committed and the working tree is clean. That history is not in this repository. On 25 September 2026, `python src/primary_e3_experiment.py --preflight` stopped with `RuntimeError: Energy freeze commit 4023717 is not an ancestor of HEAD.` I have not added a mode that bypasses the guard; the [pipeline and tests guide](PIPELINE_AND_TESTS.md#3-what-cannot-be-re-run-from-this-repository) explains why.
2. **The source archives.** About 5.9 GB in total, not redistributed here. The [data availability guide](DATA_AVAILABILITY.md) identifies them.
3. **Withheld participant-level inputs.** The onset labels, the external device map and the cohort files name participants and are withheld. They would have to be rebuilt from the source papers' supplementary material by the documented procedures before the acquisition, inventory and cohort stage could run.

The first stage can be checked without computing anything: `./run_phase1.sh --preflight` reported the Python dependencies and scripts present, both archives absent, the onset-label file absent and no external device map, then `preflight OK` and `preflight only; nothing computed.` It creates an empty `data_raw/` folder.

## 9. Automated checks

[`.github/workflows/public-checks.yml`](../.github/workflows/public-checks.yml) runs levels 1 to 4 on GitHub for every change to the main branch: it installs the environment of section 1, then runs `sha256sum -c evidence/SHA256SUMS.txt --quiet`, the chronology validator, `python src/check_public_package.py` and the test suite. It has read-only permissions and uses no data or secrets. It does not run the Gate B tests, the power calculation, Gate A or the raw-data analysis, and a passing run is not a clinical or scientific validation. Its results are recorded in the [verification report](VERIFICATION_REPORT.md).
