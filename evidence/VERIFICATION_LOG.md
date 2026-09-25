# Verification log

*Publication-stage record of checks I executed for this repository, with their actual dates, commands, environments and outcomes. It is new writing. Historical results reported in the preserved research records are not repeated here as if they were new; they are cited in the guides with their sources.*

## 24 September 2026 — energy matching audit recomputed

- **Inputs:** [`src/energy_model.py`](../src/energy_model.py), [`src/modelled_energy_match.py`](../src/modelled_energy_match.py), [`configs/modelled_energy_scenarios.json`](../configs/modelled_energy_scenarios.json), as published.
- **Action:** called the module's `audit()` function in a fresh environment (Python 3.13.13) and serialised the result the way the module writes its output file, without overwriting the archived file.
- **Outcome:** byte-for-byte identical to the archived [`results/modelled_energy_match_audit.json`](../results/modelled_energy_match_audit.json). E3 resolves to seven ten-minute bursts for every arm in LOW, CENTRAL and HIGH.

## 24 September 2026 — published test suite

- **Command:** `python -m pytest tests/ -q` and `make test`, from the repository root.
- **Environment:** fresh virtual environment, Python 3.13.13, NumPy 2.4.4, pandas 3.0.2, SciPy 1.17.1, pytest 9.1.1, Matplotlib 3.10.9, PyArrow 25.0.1, openpyxl 3.1.5, tabulate 0.10.0; Linux x86-64.
- **Outcome:** 156 passed, 0 failed, 0 skipped: 134 historical tests from the 16 historical modules published so far, and 22 new tests for the chronology validator. No input file changed during the run.
- **Not covered:** 25 historical tests whose modules are not yet published (power simulation 13, upstream reproduction 7, sensitivity analysis 5). Tests use synthetic data and published aggregates; they do not re-run the analysis on the source data.

## 24 September 2026 — chronology validator

- **Command:** `python src/validate_chronology.py`, from the repository root.
- **Outcome:** 15 events and 0 additional analyses, no unresolved finding.
- **Limit:** the validator checks that claims cite readable published records and are mutually consistent. It does not establish that a record is true.

## 24 September 2026 — primary runner guard

- **Command:** `python src/primary_e3_experiment.py --preflight`, in a clean copy of this repository.
- **Outcome:** stopped as designed with `Energy freeze commit 4023717 is not an ancestor of HEAD`. The full raw-data run cannot be performed from this repository; see the [pipeline and tests guide](../docs/PIPELINE_AND_TESTS.md#3-what-cannot-be-re-run-from-this-repository).

## 24 September 2026 — corrected primary run: published results

- **Hashes:** every file published under [`results/primary_e3_run_83cc8d1/`](../results/primary_e3_run_83cc8d1/) hashed against the version I preserved during the research; all identical.
- **Arithmetic:** θ = (W + 0.5 × T) / N and the exact two-sided binomial p-value recomputed from the published counts for H1, M1, H2 and H3 (SciPy 1.17.1), and θ recomputed for all 33 sensitivity rows. No discrepancy. Win, loss and tie counts sum to N in every row, detection rates equal detected over evaluable, and every point estimate lies inside its interval. No sensitivity row carries a p-value.
- **Regeneration:** [`src/make_final_tables_figures.py`](../src/make_final_tables_figures.py), unchanged, run in a temporary home folder that contained only the two published summary files, in the environment above without the optional table library. The regenerated digest, three CSV tables and three plain-text tables were byte-for-byte identical to the archived copies. The regenerated figures matched the archived figures on visual comparison; they are not byte-identical, because the archived figures were drawn with a newer version of the plotting library (Matplotlib 3.11.1, recorded in the files) than the one used here (3.10.9).
- **Not done:** the BCa intervals were not recomputed, because they need participant-level results that are withheld. Nothing was recomputed from the source data.

## 24 September 2026 — published test suite, after the sensitivity module

- **Command and environment:** as above.
- **Outcome:** 161 passed, 0 failed, 0 skipped: 139 historical tests from 17 modules and 22 validator tests. The 20 historical tests for the power simulation and upstream reproduction checks await their modules.
- **Chronology validator:** re-run after the result files were added as sources; 15 events, no unresolved finding.

## 25 September 2026 — archived files added on this date

- **Action:** every archived file published on this date was hashed and compared with the SHA-256 list in my preserved research record: the Gate A and Gate B code, the power simulation and its outputs and logs, the two test modules, the superseded run's manifest, the Gate A records and logs, and the five script versions kept before fixes.
- **Outcome:** all matched, except the three files published as sanitized copies, whose changes are described in the [gates guide](../docs/REPRODUCTION_GATES_AND_POWER.md) and the [execution log guide](EXECUTION_LOG_GUIDE.md). The source workbooks and the terminal record were also checked against the values in that record before use.

## 25 September 2026 — frozen power calculation, effect-ray cells

- **Command:** the published `src/power_sim.py`, unchanged, called for the 12 effect-ray cells in the order the script uses (N = 38; baseline 0.40, 0.50, 0.60; four dependence levels), with seed 20261010 and 4,000 replicates per candidate cell.
- **Environment:** as below.
- **Outcome:** all 12 cells identical to the `ray_cells` of the archived [`power_sim_frozen_n38.json`](../results/power_sim_frozen_n38.json), in every one of 144 recorded fields. The archived file was produced with NumPy 2.5.2; this run used 2.4.4.
- **Not done:** the 432-cell power surface was not re-run.

## 25 September 2026 — Gate B

- **Inputs:** the two supplementary workbooks of the source studies, placed under `metadata/` in a temporary copy of this repository after their SHA-256 values were checked against my preserved research record. They are not committed.
- **Commands:** `python -m pytest tests/test_reproduction.py -q`, then `python src/gate_b_compute.py`.
- **Outcome:** 7 passed. The regenerated `results/gate_b_results.json` was byte-for-byte identical to the preserved version. The published copy differs from both only by the removal of the participant-identifier list.

## 25 September 2026 — published test suite

- **Command:** `python -m pytest tests/ -q`, from the repository root.
- **Environment:** fresh virtual environment, Python 3.13.13, NumPy 2.4.4, pandas 3.0.2, SciPy 1.17.1, pytest 9.1.1, Matplotlib 3.10.9, PyArrow 25.0.1, openpyxl 3.1.5, tabulate 0.10.0; Linux x86-64.
- **Outcome:** **174 passed**, 0 failed, 0 skipped: 152 historical tests from 18 modules and 22 validator tests. `tests/test_reproduction.py` was not collected, because the source workbooks are absent; without `-q`, the session header names the missing files. With the workbooks supplied, as above: **181 passed**.
- **Not covered:** the tests use synthetic data, published aggregates and published tables. They do not re-run the analysis on the source data.

## 25 September 2026 — historical execution log

- **Action:** 40 excerpts, 1,819 of the record's lines, selected and sanitized as the [guide](EXECUTION_LOG_GUIDE.md) describes. The resulting file was scanned for account names, host names, private paths, e-mail addresses and every participant identifier that occurs in the record.
- **Outcome:** no match. Every omission is marked in place.
- **Limit:** the log is a curated excerpt of a preserved record, not an independently timestamped log.

## 25 September 2026 — chronology validator and checksums

- **Command:** `python src/validate_chronology.py`, from the repository root.
- **Outcome:** 15 events and 0 additional analyses, no unresolved finding.
- **Checksums:** [`SHA256SUMS.txt`](SHA256SUMS.txt) lists every file tracked in this repository at this publication, except itself. Verify from the repository root with `sha256sum -c evidence/SHA256SUMS.txt`.

## 25 September 2026 — fresh environment and published-package checks

- **Environment:** a fresh clone and a new virtual environment built with `python -m pip install -r environment/publication-requirements.txt`: Python 3.13.13, NumPy 2.4.4, pandas 3.0.2, SciPy 1.17.1, Matplotlib 3.10.9, PyArrow 25.0.1, openpyxl 3.1.5, pytest 9.1.1, without `tabulate`; Linux x86-64.
- **Commands and outcomes:** `sha256sum -c evidence/SHA256SUMS.txt`, every file OK; `python -m pytest tests/ -q`, 174 passed; `python src/validate_chronology.py`, no unresolved finding; `python src/check_public_package.py`, every check passed (links, arithmetic, intervals, energy audit, tables); `python src/check_public_package.py power`, all 12 effect-ray cells identical in all 204 recorded fields, in about three minutes.
- **Gate B:** with the two workbooks supplied and their SHA-256 values checked against my preserved research record, 181 passed, and `python src/gate_b_compute.py` regenerated a file with the SHA-256 of the preserved research version.
- **Guards:** `python src/primary_e3_experiment.py --preflight` stopped with `Energy freeze commit 4023717 is not an ancestor of HEAD.`; `./run_phase1.sh --preflight` found the scripts and dependencies, reported the archives, onset labels and external device map absent, and computed nothing.
- **Checker controls:** before relying on `src/check_public_package.py`, I ran it on a scratch copy with deliberate faults: a broken file link, a broken anchor, a changed p-value in the README table, a changed interval limit, a relabelled sensitivity row, a byte appended to a table, a changed energy tolerance, and the `tabulate` package installed. Each was reported as a failure.
- **Figures:** the regenerated figures were compared with the archived ones side by side and show the same points, intervals and labels; they are not byte-identical, because the archived figures were drawn with Matplotlib 3.11.1.

## 25 September 2026 — correction: bootstrap intervals

- **Finding:** the entry of 24 September says the BCa intervals were not recomputed because they need withheld participant-level results. That reason was wrong. The confirmatory script and the sensitivity script both bootstrap a vector built only from the win, loss and tie counts, with seeds recorded in each script.
- **Action:** `python src/check_public_package.py intervals` loads the bootstrap function of each published script without running the script, and recomputes every interval from the published counts.
- **Outcome:** all 4 confirmatory and 33 sensitivity intervals equal the published limits. The entry of 24 September is left as it stood; the correction is recorded here and in the [publication notes](../docs/PUBLICATION_NOTES.md#material-corrections).
