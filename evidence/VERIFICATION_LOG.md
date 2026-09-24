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
